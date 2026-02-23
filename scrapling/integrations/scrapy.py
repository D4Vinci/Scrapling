from functools import wraps

from scrapling.core._types import Any, Callable, Optional
from scrapling.parser import Selector


class ScraplingScrapyResponse:
    """Wrap a Scrapy-like response and expose Scrapling selectors."""

    __slots__ = ("_response", "_selector")

    def __init__(self, response: Any):
        self._response = response
        self._selector: Optional[Selector] = None

    @property
    def scrapling(self) -> Selector:
        if self._selector is None:
            self._selector = Selector(
                getattr(self._response, "text", "") or "",
                url=getattr(self._response, "url", "") or "",
            )
        return self._selector

    @property
    def selector(self) -> Selector:
        return self.scrapling

    def css(self, selector: str):
        return self.scrapling.css(selector)

    def xpath(self, selector: str, **kwargs: Any):
        return self.scrapling.xpath(selector, **kwargs)

    def __getattr__(self, name: str) -> Any:
        return getattr(self._response, name)


def use_scrapling(callback: Optional[Callable[..., Any]] = None) -> Callable[..., Any]:
    """Decorator for Scrapy callbacks to transparently use Scrapling selectors."""

    def _decorate(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        def _wrapped(self, response: Any, *args: Any, **kwargs: Any) -> Any:
            return func(self, ScraplingScrapyResponse(response), *args, **kwargs)

        return _wrapped

    if callback is not None:
        return _decorate(callback)
    return _decorate
