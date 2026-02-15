from typing import TYPE_CHECKING, Any
from scrapling.engines.toolbelt import ProxyRotator

if TYPE_CHECKING:
    from scrapling.fetchers.requests import Fetcher, AsyncFetcher, FetcherSession
    from scrapling.fetchers.chrome import DynamicFetcher, DynamicSession, AsyncDynamicSession
    from scrapling.fetchers.stealth_chrome import StealthyFetcher, StealthySession, AsyncStealthySession


# Lazy import mapping
_LAZY_IMPORTS = {
    "Fetcher": ("scrapling.fetchers.requests", "Fetcher"),
    "AsyncFetcher": ("scrapling.fetchers.requests", "AsyncFetcher"),
    "FetcherSession": ("scrapling.fetchers.requests", "FetcherSession"),
    "DynamicFetcher": ("scrapling.fetchers.chrome", "DynamicFetcher"),
    "DynamicSession": ("scrapling.fetchers.chrome", "DynamicSession"),
    "AsyncDynamicSession": ("scrapling.fetchers.chrome", "AsyncDynamicSession"),
    "StealthyFetcher": ("scrapling.fetchers.stealth_chrome", "StealthyFetcher"),
    "StealthySession": ("scrapling.fetchers.stealth_chrome", "StealthySession"),
    "AsyncStealthySession": ("scrapling.fetchers.stealth_chrome", "AsyncStealthySession"),
}

__all__ = [
    "Fetcher",
    "AsyncFetcher",
    "ProxyRotator",
    "FetcherSession",
    "DynamicFetcher",
    "DynamicSession",
    "AsyncDynamicSession",
    "StealthyFetcher",
    "StealthySession",
    "AsyncStealthySession",
]


def __getattr__(name: str) -> Any:
    if name in _LAZY_IMPORTS:
        module_path, class_name = _LAZY_IMPORTS[name]
        module = __import__(module_path, fromlist=[class_name])
        return getattr(module, class_name)
    else:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__() -> list[str]:
    """Support for dir() and autocomplete."""
    return sorted(list(_LAZY_IMPORTS.keys()))
