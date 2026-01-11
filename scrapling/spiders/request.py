from urllib.parse import urlparse

from scrapling.engines.toolbelt.custom import Response
from scrapling.core._types import Any, AsyncGenerator, Callable, Dict, Union


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

    @property
    def domain(self) -> str:
        return urlparse(self.url).netloc

    @property
    def _fp(self) -> str:
        """Generate a unique fingerprint for deduplication."""
        # TODO: Improve fingerprint
        return f"{self.sid}:{self.url}"

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
        return self._fp == other._fp
