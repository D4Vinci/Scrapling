"""
Fetcher builder for the Scrapling wrapper.

Maps the 'fetcher' key from a ScrapeConfig to the appropriate Scrapling
session class and exposes a uniform context-manager interface with a single
.fetch(url) method.

Usage:
    with build_fetcher(cfg) as fetcher:
        page = fetcher.fetch(cfg.url)
        page2 = fetcher.fetch(next_url)   # reuses the HTTP session if fetcher=http
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from wrapper.config import ScrapeConfig

if TYPE_CHECKING:
    from scrapling.engines.toolbelt.custom import Response


class FetcherWrapper:
    """
    Unified context manager around any Scrapling fetcher type.

    - http    → FetcherSession (persistent curl_cffi session, efficient for pagination)
    - stealth → StealthyFetcher (one browser launch per .fetch() call)
    - dynamic → DynamicFetcher  (one browser launch per .fetch() call)
    """

    def __init__(self, cfg: ScrapeConfig) -> None:
        self._cfg = cfg
        self._session_factory = None   # FetcherSession instance (http only)
        self._session = None           # _SyncSessionLogic yielded by __enter__ (http only)

    # ------------------------------------------------------------------
    # Context manager
    # ------------------------------------------------------------------

    def __enter__(self) -> "FetcherWrapper":
        if self._cfg.fetcher == "http":
            from scrapling.engines.static import FetcherSession

            fo = self._cfg.fetcher_options
            ro = self._cfg.request_options

            merged_headers = {**fo.extra_headers, **ro.headers}
            self._session_factory = FetcherSession(
                impersonate=fo.impersonate,
                http3=fo.http3,
                proxy=fo.proxy,
                headers=merged_headers or None,
                timeout=ro.timeout or 30,
            )
            self._session = self._session_factory.__enter__()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        if self._session_factory is not None:
            self._session_factory.__exit__(exc_type, exc_val, exc_tb)
            self._session_factory = None
            self._session = None

    # ------------------------------------------------------------------
    # Fetch
    # ------------------------------------------------------------------

    def fetch(self, url: str) -> "Response":
        """Fetch *url* and return a Scrapling Response (which extends Selector)."""
        cfg = self._cfg
        fo = cfg.fetcher_options
        ro = cfg.request_options

        if cfg.fetcher == "http":
            if self._session is None:
                raise RuntimeError("FetcherWrapper must be used as a context manager")
            kwargs: dict = {}
            if ro.cookies:
                kwargs["cookies"] = ro.cookies
            return self._session.get(url, **kwargs)

        if cfg.fetcher == "stealth":
            from scrapling.fetchers.stealth_chrome import StealthyFetcher

            return StealthyFetcher.fetch(url, **_browser_kwargs(fo, ro))

        if cfg.fetcher == "dynamic":
            from scrapling.fetchers.chrome import DynamicFetcher

            return DynamicFetcher.fetch(url, **_browser_kwargs(fo, ro))

        raise ValueError(f"Unknown fetcher type: {cfg.fetcher!r}")


# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------

def _browser_kwargs(fo, ro) -> dict:
    """Build the kwargs dict for StealthyFetcher / DynamicFetcher.fetch()."""
    kwargs: dict = {}

    merged_headers = {**fo.extra_headers, **ro.headers}
    if merged_headers:
        kwargs["extra_headers"] = merged_headers

    if fo.proxy:
        kwargs["proxy"] = fo.proxy

    # Browser fetchers expect timeout in milliseconds; our config stores seconds.
    if ro.timeout:
        kwargs["timeout"] = ro.timeout * 1000

    return kwargs


# ------------------------------------------------------------------
# Public factory
# ------------------------------------------------------------------

def build_fetcher(cfg: ScrapeConfig) -> FetcherWrapper:
    """Return a FetcherWrapper ready to be used as a context manager."""
    return FetcherWrapper(cfg)
