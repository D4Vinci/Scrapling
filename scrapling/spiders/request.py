import hashlib
from io import BytesIO
from functools import cached_property
from urllib.parse import urlparse, urlencode

import orjson
from w3lib.url import canonicalize_url

from scrapling.engines.toolbelt.custom import Response
from scrapling.core._types import Any, AsyncGenerator, Callable, Dict, Optional, Union, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from scrapling.spiders.spider import Spider

_SECURITY_CONTEXT_HEADERS = frozenset({"authorization", "cookie"})
_SECURITY_CONTEXT_KWARGS = frozenset({"auth", "cookies"})


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


def _process_headers(headers: Dict[str, Any], header_names: frozenset[str] | None = None) -> Tuple[Tuple[str, str], ...]:
    processed_headers = {}
    for key, value in headers.items():
        normalized_key = key.lower()
        if header_names is not None and normalized_key not in header_names:
            continue
        processed_headers[_convert_to_bytes(normalized_key).hex()] = _convert_to_bytes(value).hex()
    return tuple(sorted(processed_headers.items()))


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
        self.url: str = url
        self.sid: str = sid
        self.callback = callback
        self.priority: int = priority
        self.dont_filter: bool = dont_filter
        self.meta: dict[str, Any] = meta if meta else {}
        self._retry_count: int = _retry_count
        self._session_kwargs = kwargs if kwargs else {}
        self._fp: Optional[bytes] = None

    def copy(self) -> "Request":
        """Create a copy of this request."""
        return Request(
            url=self.url,
            sid=self.sid,
            callback=self.callback,
            priority=self.priority,
            dont_filter=self.dont_filter,
            meta=self.meta.copy(),
            _retry_count=self._retry_count,
            **self._session_kwargs,
        )

    @cached_property
    def domain(self) -> str:
        return urlparse(self.url).netloc

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

        data: Dict[str, Any] = {
            "sid": self.sid,
            "body": body.hex(),
            "method": self._session_kwargs.get("method", "GET"),
            "url": canonicalize_url(self.url, keep_fragments=keep_fragments),
        }

        security_context_kwargs = {
            key.lower(): _stable_value_repr(value)
            for key, value in self._session_kwargs.items()
            if key.lower() in _SECURITY_CONTEXT_KWARGS
        }
        if security_context_kwargs:
            data["security_context_kwargs"] = tuple(sorted(security_context_kwargs.items()))

        security_context_headers = []
        for headers_key in ("headers", "extra_headers"):
            headers = self._session_kwargs.get(headers_key) or {}
            processed_headers = _process_headers(headers, _SECURITY_CONTEXT_HEADERS)
            if processed_headers:
                security_context_headers.append((headers_key, processed_headers))
        if security_context_headers:
            data["security_context_headers"] = tuple(security_context_headers)

        if include_kwargs:
            filtered_kwargs = {
                key.lower(): _stable_value_repr(value)
                for key, value in self._session_kwargs.items()
                if key.lower() not in ("data", "json")
            }
            data["kwargs"] = tuple(sorted(filtered_kwargs.items()))

        if include_headers:
            headers = self._session_kwargs.get("headers") or self._session_kwargs.get("extra_headers") or {}
            data["headers"] = _process_headers(headers)

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
        if self._fp is None or other._fp is None:
            raise RuntimeError("Cannot compare requests before generating their fingerprints!")
        return self._fp == other._fp

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
