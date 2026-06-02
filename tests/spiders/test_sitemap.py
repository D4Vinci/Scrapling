"""Tests for `SitemapSpider`."""

import gzip
import pickle

import pytest

from scrapling.engines.toolbelt.custom import Response
from scrapling.spiders.links import LinkExtractor
from scrapling.spiders.request import Request
from scrapling.spiders.templates.sitemap import SitemapSpider
from scrapling.spiders.templates import CrawlRule
from scrapling.core._types import AsyncGenerator


URLSET_XML = b"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>https://example.com/posts/1</loc>
    <lastmod>2026-01-15</lastmod>
    <changefreq>daily</changefreq>
    <priority>0.8</priority>
  </url>
  <url>
    <loc>https://example.com/posts/2</loc>
    <lastmod>2026-02-20</lastmod>
  </url>
  <url>
    <loc>https://example.com/about</loc>
  </url>
</urlset>
"""

URLSET_WITH_ALTERNATES = b"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
        xmlns:xhtml="http://www.w3.org/1999/xhtml">
  <url>
    <loc>https://example.com/en/page</loc>
    <xhtml:link rel="alternate" hreflang="fr" href="https://example.com/fr/page"/>
    <xhtml:link rel="alternate" hreflang="de" href="https://example.com/de/page"/>
  </url>
</urlset>
"""

INDEX_XML = b"""<?xml version="1.0" encoding="UTF-8"?>
<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <sitemap><loc>https://example.com/posts-sitemap.xml</loc></sitemap>
  <sitemap><loc>https://example.com/products-sitemap.xml</loc></sitemap>
  <sitemap><loc>https://example.com/skip-sitemap.xml</loc></sitemap>
</sitemapindex>
"""

def _make_response(body: bytes, url: str = "https://example.com/sitemap.xml", headers: dict | None = None) -> Response:
    resp = Response(
        url=url,
        content=body,
        status=200,
        reason="OK",
        cookies={},
        headers=headers or {},
        request_headers={},
    )
    resp.request = Request(url, sid="default")
    return resp


async def _collect(agen: AsyncGenerator) -> list:
    return [item async for item in agen]


class TestSitemapSpiderFlow:
    @pytest.mark.asyncio
    async def test_urlset_dispatched_through_rules(self):
        class S(SitemapSpider):
            name = "s"
            sitemap_urls = ["https://example.com/sitemap.xml"]

            def rules(self):
                return [CrawlRule(LinkExtractor(allow=r"/posts/"), callback=self.parse_post)]

            async def parse_post(self, response):
                yield {"post": response.url}

        spider = S()
        out = await _collect(spider._parse_sitemap(_make_response(URLSET_XML)))
        post_reqs = [r for r in out if "/posts/" in r.url]
        about_reqs = [r for r in out if "/about" in r.url]
        # Two posts dispatched to parse_post; /about is dropped (matches no rule, non-empty rules)
        assert len(post_reqs) == 2
        assert all(r.callback == spider.parse_post for r in post_reqs)
        assert about_reqs == []

    @pytest.mark.asyncio
    async def test_no_rules_means_all_urls_fall_through(self):
        class S(SitemapSpider):
            name = "s"
            sitemap_urls = ["https://example.com/sitemap.xml"]

        spider = S()
        out = await _collect(spider._parse_sitemap(_make_response(URLSET_XML)))
        assert len(out) == 3
        assert all(r.callback is None for r in out)

    @pytest.mark.asyncio
    async def test_sitemapindex_descends_into_children(self):
        class S(SitemapSpider):
            name = "s"
            sitemap_urls = ["https://example.com/sitemap.xml"]

        spider = S()
        out = await _collect(spider._parse_sitemap(_make_response(INDEX_XML)))
        # No urls in this index, just three child sitemap fetches
        assert len(out) == 3
        assert all(r.callback == spider._parse_sitemap for r in out)
        assert {r.url for r in out} == {
            "https://example.com/posts-sitemap.xml",
            "https://example.com/products-sitemap.xml",
            "https://example.com/skip-sitemap.xml",
        }

    @pytest.mark.asyncio
    async def test_sitemap_follow_filters_child_sitemaps(self):
        class S(SitemapSpider):
            name = "s"
            sitemap_urls = ["https://example.com/sitemap.xml"]
            sitemap_follow = LinkExtractor(allow=r"posts-sitemap")

        spider = S()
        out = await _collect(spider._parse_sitemap(_make_response(INDEX_XML)))
        assert {r.url for r in out} == {"https://example.com/posts-sitemap.xml"}

    @pytest.mark.asyncio
    async def test_alternate_links_dispatched_when_enabled(self):
        class S(SitemapSpider):
            name = "s"
            sitemap_urls = ["https://example.com/sitemap.xml"]
            sitemap_alternate_links = True

        spider = S()
        out = await _collect(spider._parse_sitemap(_make_response(URLSET_WITH_ALTERNATES)))
        urls = {r.url for r in out}
        assert urls == {
            "https://example.com/en/page",
            "https://example.com/fr/page",
            "https://example.com/de/page",
        }

    @pytest.mark.asyncio
    async def test_gzipped_sitemap_handled_via_magic_bytes(self):
        class S(SitemapSpider):
            name = "s"
            sitemap_urls = ["https://example.com/sitemap.xml.gz"]

        spider = S()
        body = gzip.compress(URLSET_XML)
        out = await _collect(spider._parse_sitemap(_make_response(body, url="https://example.com/sitemap.xml.gz")))
        assert len(out) == 3


class TestSitemapSpiderStartRequests:
    @pytest.mark.asyncio
    async def test_start_requests_uses_sitemap_urls(self):
        class S(SitemapSpider):
            name = "s"
            sitemap_urls = ["https://a.com/s.xml", "https://b.com/s.xml"]

        spider = S()
        out = [req async for req in spider.start_requests()]
        assert {r.url for r in out} == {"https://a.com/s.xml", "https://b.com/s.xml"}
        assert all(r.callback == spider._parse_sitemap for r in out)

    @pytest.mark.asyncio
    async def test_start_requests_raises_when_nothing_configured(self):
        class S(SitemapSpider):
            name = "s"

        spider = S()
        with pytest.raises(RuntimeError, match="needs `sitemap_urls`"):
            [req async for req in spider.start_requests()]


class TestRobotsTxt:
    @pytest.mark.asyncio
    async def test_parse_sitemap_yields_requests_from_robots_directives(self):
        class S(SitemapSpider):
            name = "s"
            sitemap_urls = ["https://example.com/robots.txt"]

        spider = S()
        body = b"User-agent: *\nSitemap: https://example.com/sitemap.xml\n"
        resp = _make_response(body, url="https://example.com/robots.txt")
        out = await _collect(spider._parse_sitemap(resp))
        assert len(out) == 1
        assert out[0].url == "https://example.com/sitemap.xml"
        assert out[0].callback == spider._parse_sitemap

    @pytest.mark.asyncio
    async def test_parse_sitemap_robots_with_no_directives_warns(self):
        # Spider's logger has propagate=False, so we attach our own handler to it.
        import logging

        class S(SitemapSpider):
            name = "s"
            sitemap_urls = ["https://example.com/robots.txt"]

        spider = S()
        records: list[logging.LogRecord] = []

        class _Capture(logging.Handler):
            def emit(self, record: logging.LogRecord) -> None:
                records.append(record)

        spider.logger.addHandler(_Capture())

        body = b"User-agent: *\nDisallow: /\n"
        resp = _make_response(body, url="https://example.com/robots.txt")
        out = await _collect(spider._parse_sitemap(resp))
        assert out == []
        assert any("No Sitemaps" in r.getMessage() for r in records if r.levelno == logging.WARNING)


class TestSitemapSpiderPickle:
    @pytest.mark.asyncio
    async def test_pickle_request_with_bound_method_callback_via_rules(self):
        class S(SitemapSpider):
            name = "s"
            sitemap_urls = ["https://example.com/sitemap.xml"]

            def rules(self):
                return [CrawlRule(LinkExtractor(allow=r"/posts/"), callback=self.parse_post)]

            async def parse_post(self, response):
                yield {"post": response.url}

        spider = S()
        out = await _collect(spider._parse_sitemap(_make_response(URLSET_XML)))
        post_req = next(r for r in out if "/posts/" in r.url)
        state = post_req.__getstate__()
        assert state["_callback_name"] == "parse_post"
        # Round-trip
        pickled = pickle.dumps(post_req)
        restored = pickle.loads(pickled)
        fresh = S()
        restored._restore_callback(fresh)
        assert restored.callback == fresh.parse_post


def test_sitemap_safe_xml_parser_blocks_external_entities():
    class DemoSitemap(SitemapSpider):
        name = "demo_sitemap_safe"
        sitemap_urls = ["https://example.com/sitemap.xml"]

        async def parse(self, response):
            yield None

    body = b'''<?xml version="1.0"?>
    <!DOCTYPE foo [ <!ENTITY xxe SYSTEM "file:///etc/passwd"> ]>
    <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
      <url><loc>&xxe;</loc></url>
    </urlset>'''
    spider = object.__new__(DemoSitemap)
    spider.logger = __import__("logging").getLogger("test_sitemap_safe")
    spider.sitemap_alternate_links = False

    result = spider._sm_body(body)
    assert result.urls in ([], [""])
