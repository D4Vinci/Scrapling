"""Scrapy integration: build Scrapling :class:`~scrapling.engines.toolbelt.custom.Response` from Scrapy responses.

Install with ``pip install "scrapling[scrapy]"``.
"""

from scrapling.contrib.scrapy.adapter import scrapling_response_from_scrapy
from scrapling.contrib.scrapy.middleware import ScraplingMiddleware

__all__ = [
    "ScraplingMiddleware",
    "scrapling_response_from_scrapy",
]
