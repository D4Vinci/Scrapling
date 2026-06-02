import hashlib
from io import BytesIO
from base64 import b64encode, b64decode
from urllib.parse import urlparse, urlencode

import orjson
from w3lib.url import canonicalize_url

from scrapling.engines.toolbelt.custom import Response
from scrapling.core.utils.redaction import redact_headers, redact_mapping, redact_proxy, is_sensitive_key
from scrapling.core._types import Any, AsyncGenerator, Callable, Dict, Optional, Union, Tuple, Mapping, TYPE_CHECKING

if TYPE_CHECKING:
    from scrapling.spiders.spider import Spider


def _convert_to_bytes(value: str | bytes) -> bytes:
    if isinstance(value, bytes):
        return value
    if not isinstance(value, str):
        raise TypeError(f"Can't convert {type(value).__name__} to bytes")

    return value.encode(encoding="utf-8", errors="ignore")


def _stable_value_repr(value: Any) -> str:
    try:
        return orjson.dumps(value, option=orjson.OPT_SORT_KEYS, default=repr).decode()
    except TypeError:
        return repr(value)


def _json_safe(value: Any, *, store_secrets: bool = False, key: str = "") -> Any:
    """Normalize checkpoint payloads into deterministic JSON-safe values."""
    if callable(value):
        return None
    if value is None or isinstance(value, (str, int, float, bool)):
        if not store_secrets and isinstance(value, str):
            if key.lower() in {"proxy", "proxies"}:
                return redact_proxy(value)
            if is_sensitive_key(key):
                return "***"
        return value
    if isinstance(value, bytes):
        return {"__type__": "bytes", "base64": b64encode(value).decode("ascii")}
    if isinstance(value, BytesIO):
        return {"__type__": "bytes", "base64": b64encode(value.getvalue()).decode("ascii")}
    if isinstance(value, (set, tuple, list)):
        return [_json_safe(item, store_secrets=store_secrets) for item in value]
    if isinstance(value, dict) or hasattr(value, "items"):
        mapping = dict(value)
        if not store_secrets:
            lowered = key.lower()
            if lowered in {"headers", "extra_headers", "request_headers"}:
                mapping = redact_headers(mapping)
            elif lowered in {"proxy", "proxies"}:
                mapping = redact_proxy(mapping)
            else:
                mapping = redact_mapping(mapping)
        return {str(k): _json_safe(v, store_secrets=store_secrets, key=str(k)) for k, v in mapping.items() if not callable(v)}
    return repr(value)


def _json_restore(value: Any) -> Any:
    if isinstance(value, dict) and value.get("__type__") == "bytes" and isinstance(value.get("base64"), str):
        try:
            return b64decode(value["base64"].encode("ascii"))
        except Exception:
            return b""
    if isinstance(value, dict):
        return {k: _json_restore(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_json_restore(v) for v in value]
    return value


class Request:
    def __init__(
        self,
        url: str,
        sid: str = "",
        callback: Callable[[Response], AsyncGenerator[Union[Dict[str, Any], "Request", None], None]] | None = None,
        priority: int = 0,
        dont_filter: bool = False,
        meta: dict[str, Any] | None = None,
        _retry_count: int = 0,
        **kwargs: Any,
    ) -> None:
        self._fp: Optional[bytes] = None
        self.url = url
        self.sid: str = sid
        self.callback = callback
        self.priority: int = priority
        self.dont_filter: bool = dont_filter
        self.meta: dict[str, Any] = meta if meta else {}
        self._retry_count: int = _retry_count
        self._session_kwargs = kwargs if kwargs else {}

    def copy(self) -> "Request":
        """Create a copy of this request."""
        request = Request(
            url=self.url,
            sid=self.sid,
            callback=self.callback,
            priority=self.priority,
            dont_filter=self.dont_filter,
            meta=self.meta.copy(),
            _retry_count=self._retry_count,
            **self._session_kwargs,
        )
        request._fp = self._fp
        return request

    @property
    def url(self) -> str:
        return self._url

    @url.setter
    def url(self, value: str) -> None:
        self._url = str(value)
        # URL participates in the default fingerprint; reset stale cached value on mutation.
        if hasattr(self, "_fp"):
            self._fp = None

    @property
    def domain(self) -> str:
        return (urlparse(self.url).hostname or "").lower()

    def update_fingerprint(
        self,
        include_kwargs: bool = False,
        include_headers: bool = False,
        keep_fragments: bool = False,
    ) -> bytes:
        """Generate a unique fingerprint for deduplication.

        Caches the result in self._fp after first computation.
        """
        if self._fp is not None:
            return self._fp

        post_data = self._session_kwargs.get("data", {})
        body = b""
        if post_data:
            if isinstance(post_data, dict | list | tuple):
                body = urlencode(post_data).encode()
            elif isinstance(post_data, str):
                body = post_data.encode()
            elif isinstance(post_data, BytesIO):
                body = post_data.getvalue()
            elif isinstance(post_data, bytes):
                body = post_data
        else:
            post_data = self._session_kwargs.get("json", {})
            body = orjson.dumps(post_data) if post_data else b""

        data: Dict[str, str | Tuple] = {
            "sid": self.sid,
            "body": body.hex(),
            "method": self._session_kwargs.get("method", "GET"),
            "url": canonicalize_url(self.url, keep_fragments=keep_fragments),
        }

        if include_kwargs:
            filtered_kwargs = {
                key.lower(): _stable_value_repr(value)
                for key, value in self._session_kwargs.items()
                if key.lower() not in ("data", "json")
            }
            data["kwargs"] = tuple(sorted(filtered_kwargs.items()))

        if include_headers:
            headers = self._session_kwargs.get("headers") or self._session_kwargs.get("extra_headers") or {}
            processed_headers = {}
            # Some header normalization
            for key, value in headers.items():
                processed_headers[_convert_to_bytes(key.lower()).hex()] = _convert_to_bytes(value).hex()
            data["headers"] = tuple(processed_headers.items())

        fp = hashlib.sha1(orjson.dumps(data, option=orjson.OPT_SORT_KEYS), usedforsecurity=False).digest()
        self._fp = fp
        return fp

    def __repr__(self) -> str:
        callback_name = getattr(self.callback, "__name__", None) or "None"
        return f"<Request({self.url}) priority={self.priority} callback={callback_name}>"

    def __str__(self) -> str:
        return self.url

    def __lt__(self, other: object) -> bool:
        """Compare requests by priority"""
        if not isinstance(other, Request):
            return NotImplemented
        return self.priority < other.priority

    def __gt__(self, other: object) -> bool:
        """Compare requests by priority"""
        if not isinstance(other, Request):
            return NotImplemented
        return self.priority > other.priority

    def __eq__(self, other: object) -> bool:
        """Requests are equal if they have the same fingerprint."""
        if not isinstance(other, Request):
            return NotImplemented
        return self.update_fingerprint() == other.update_fingerprint()

    def __hash__(self) -> int:
        """Make Request usable in sets/maps with the same key as equality."""
        return hash(self.update_fingerprint())

    def to_state(self, *, store_secrets: bool = False) -> dict[str, Any]:
        """Serialize this request to a versioned, pickle-free checkpoint state.

        Secrets are redacted by default so checkpoints are safe to keep on disk.
        Pass ``store_secrets=True`` only when exact proxy/auth replay is required
        and the checkpoint directory is trusted.
        """
        return {
            "version": 1,
            "url": self.url,
            "sid": self.sid,
            "priority": self.priority,
            "dont_filter": self.dont_filter,
            "meta": _json_safe(self.meta, store_secrets=store_secrets, key="meta"),
            "_retry_count": self._retry_count,
            "_session_kwargs": _json_safe(self._session_kwargs, store_secrets=store_secrets, key="_session_kwargs"),
            "_fp": self._fp.hex() if self._fp else None,
            "callback": getattr(self.callback, "__name__", None),
        }

    @classmethod
    def from_state(cls, state: Mapping[str, Any], callback_registry: Mapping[str, Any]) -> "Request":
        """Restore a request from pickle-free checkpoint state."""
        session_kwargs = dict(_json_restore(state.get("_session_kwargs") or {}))
        req = cls(
            url=str(state["url"]),
            sid=str(state.get("sid") or ""),
            callback=callback_registry.get(state.get("callback")),
            priority=int(state.get("priority", 0)),
            dont_filter=bool(state.get("dont_filter", False)),
            meta=dict(_json_restore(state.get("meta") or {})),
            _retry_count=int(state.get("_retry_count", 0)),
            **session_kwargs,
        )
        fp = state.get("_fp")
        req._fp = bytes.fromhex(fp) if isinstance(fp, str) and fp else None
        return req

    def __getstate__(self) -> dict[str, Any]:
        """Prepare state for pickling - store callback as name string for pickle compatibility."""
        state = self.__dict__.copy()
        state["_callback_name"] = getattr(self.callback, "__name__", None) if self.callback is not None else None
        state["callback"] = None  # Don't pickle the actual callable
        return state

    def __setstate__(self, state: dict[str, Any]) -> None:
        """Restore state from pickle - callback restored later via _restore_callback()."""
        self._callback_name: str | None = state.pop("_callback_name", None)
        self.__dict__.update(state)

    def _restore_callback(self, spider: "Spider") -> None:
        """Restore callback from spider after unpickling.

        :param spider: Spider instance to look up callback method on
        """
        if hasattr(self, "_callback_name") and self._callback_name:
            self.callback = getattr(spider, self._callback_name, None) or spider.parse
            del self._callback_name
        elif hasattr(self, "_callback_name"):
            del self._callback_name
