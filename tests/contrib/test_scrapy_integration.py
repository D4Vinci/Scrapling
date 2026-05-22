"""Tests for optional Scrapy bridge (``scrapling[scrapy]``)."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

pytest.importorskip("scrapy")

from scrapy import Request  # noqa: E402
from scrapy.http import HtmlResponse  # noqa: E402
from scrapy.settings import Settings  # noqa: E402

from scrapling.contrib.scrapy.adapter import scrapling_response_from_scrapy  # noqa: E402
from scrapling.contrib.scrapy.middleware import (  # noqa: E402
    SCRAPLING_ENABLED,
    SCRAPLING_META_KEY,
    SCRAPLING_SELECTOR_KWARGS,
    ScraplingMiddleware,
)


class _BareSpider:
    name = "test_spider"


HTML = b"""<!doctype html>
<html><head><title>TS</title></head>
<body><p id="item" class="x">Hello</p></body></html>"""


def test_scrapling_response_from_scrapy_css_and_xpath():
    req = Request(
        url="https://example.com/page",
        method="GET",
        headers={b"X-Req": [b"1"]},
    )
    scrapy_resp = HtmlResponse(
        url="https://example.com/page",
        status=200,
        headers={b"Content-Type": [b"text/html; charset=utf-8"], b"X-Res": [b"2"]},
        body=HTML,
        encoding="utf-8",
        request=req,
    )
    sl = scrapling_response_from_scrapy(scrapy_resp)

    assert sl.url == "https://example.com/page"
    assert sl.status == 200
    assert sl.encoding == "utf-8"
    assert "OK" in sl.reason or sl.reason == "OK"
    assert sl.headers.get("Content-Type", "").startswith("text/html")
    assert sl.headers.get("X-Res") == "2"
    assert sl.request_headers.get("X-Req") == "1"

    assert sl.css("p#item.x::text").get().strip() == "Hello"
    assert sl.xpath('//p[@id="item"]/text()').get().strip() == "Hello"

    # Shallow meta copy: mutating Scrapling copy must not mutate scrapy meta
    scrapy_resp.meta["outer"] = 1
    sl.meta["inner"] = 2
    assert "inner" not in scrapy_resp.meta
    assert scrapy_resp.meta["outer"] == 1


def test_scrapling_response_from_scrapy_adaptive_storage(tmp_path):
    req = Request(url="https://adapt.example/a")
    scrapy_resp = HtmlResponse(
        url="https://adapt.example/a",
        body=HTML,
        encoding="utf-8",
        request=req,
    )
    db = tmp_path / "scrape.sqlite"
    sl = scrapling_response_from_scrapy(
        scrapy_resp,
        adaptive=True,
        storage_args={"storage_file": str(db), "url": scrapy_resp.url},
    )
    assert sl.css("p#item::text").get().strip() == "Hello"
    assert db.exists()


def test_scrapling_middleware_sets_meta():
    mw = ScraplingMiddleware(enabled=True, selector_kwargs={}, meta_key="scrapling")
    req = Request("https://mw.example/")
    resp = HtmlResponse(
        url="https://mw.example/",
        body=HTML,
        encoding="utf-8",
        request=req,
    )
    out = mw.process_response(req, resp, _BareSpider())
    assert out is resp
    assert "scrapling" in resp.meta
    assert resp.meta["scrapling"].css("title::text").get().strip() == "TS"


def test_middleware_from_crawler():
    crawler = MagicMock()
    crawler.settings = Settings()
    crawler.settings.set(SCRAPLING_ENABLED, False)
    crawler.settings.set(SCRAPLING_META_KEY, "z")
    crawler.settings.set(SCRAPLING_SELECTOR_KWARGS, {"adaptive": False})
    mw = ScraplingMiddleware.from_crawler(crawler)
    assert mw.enabled is False
    assert mw.meta_key == "z"
    assert mw.selector_kwargs == {"adaptive": False}
