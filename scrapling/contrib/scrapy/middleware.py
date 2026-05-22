"""Downloader middleware that attaches a Scrapling response to Scrapy ``response.meta``."""

from __future__ import annotations

from typing import Any, Union

from scrapling.core._types import Dict

try:
    from scrapy.spiders import Spider
    from scrapy.http import Request, Response as ScrapyHttpResponse
    from scrapy.settings import BaseSettings
except ImportError as exc:  # pragma: no cover - optional dependency
    raise ImportError('Scrapy is required for this module. Install with: pip install "scrapling[scrapy]"') from exc

from scrapling.contrib.scrapy.adapter import scrapling_response_from_scrapy

# Settings keys (also documented on readthedocs).
SCRAPLING_ENABLED: str = "SCRAPLING_ENABLED"
SCRAPLING_SELECTOR_KWARGS: str = "SCRAPLING_SELECTOR_KWARGS"
SCRAPLING_META_KEY: str = "SCRAPLING_META_KEY"


class ScraplingMiddleware:
    """Attach a Scrapling :class:`~scrapling.engines.toolbelt.custom.Response` to ``response.meta``.

    The attribute name defaults to ``"scrapling"`` and is configured with the Scrapy setting
    ``SCRAPLING_META_KEY`` (the setting value is the meta key string, e.g. ``"scrapling"``).

    Enable in ``settings.py``::

        DOWNLOADER_MIDDLEWARES = {
            # Place after HttpCompressionMiddleware if responses must be decoded first.
            "scrapling.contrib.scrapy.middleware.ScraplingMiddleware": 585,
        }
        SCRAPLING_ENABLED = True
        SCRAPLING_META_KEY = "scrapling"
        SCRAPLING_SELECTOR_KWARGS = {"adaptive": False}

    Then in spider callbacks use ``response.meta["scrapling"]`` (or your custom key).
    """

    def __init__(
        self, enabled: bool = True, selector_kwargs: Dict[str, Any] | None = None, meta_key: str = "scrapling"
    ):
        self.enabled = enabled
        self.selector_kwargs = selector_kwargs or {}
        self.meta_key = meta_key

    @classmethod
    def from_crawler(cls, crawler: Any) -> ScraplingMiddleware:
        settings: BaseSettings = crawler.settings
        return cls(
            enabled=settings.getbool(SCRAPLING_ENABLED, True),
            selector_kwargs=dict(settings.getdict(SCRAPLING_SELECTOR_KWARGS, {})),
            meta_key=str(settings.get(SCRAPLING_META_KEY, "scrapling")),
        )

    def process_response(
        self,
        request: Request,
        response: ScrapyHttpResponse,
        spider: Spider,
    ) -> Union[Request, ScrapyHttpResponse]:
        if not self.enabled:
            return response
        sl_response = scrapling_response_from_scrapy(response, **self.selector_kwargs)
        response.meta[self.meta_key] = sl_response
        return response
