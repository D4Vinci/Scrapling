from urllib.parse import urlparse

from scrapling.engines.toolbelt.custom import Response
from scrapling.core._types import Any, AsyncGenerator, Callable, Dict, Union, TYPE_CHECKING

if TYPE_CHECKING:
    from scrapling.spiders.spider import Spider


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
