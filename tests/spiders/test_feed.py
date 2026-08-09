"""Tests for `XMLFeedSpider` and `CSVFeedSpider`."""

import gzip
import logging

import pytest

from scrapling.engines.toolbelt.custom import Response
from scrapling.spiders.request import Request
from scrapling.spiders.templates.feed import CSVFeedSpider, XMLFeedSpider
from scrapling.core._types import AsyncGenerator


RSS_XML = b"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:media="http://search.yahoo.com/mrss/">
  <channel>
    <title>Feed Title</title>
    <item>
      <title>First Post</title>
      <link>https://example.com/posts/1</link>
      <pubDate>Mon, 01 Jan 2026 00:00:00 GMT</pubDate>
      <media:thumbnail url="https://example.com/thumb1.jpg"/>
    </item>
    <item>
      <title>Second Post</title>
      <link>https://example.com/posts/2</link>
    </item>
  </channel>
</rss>
"""

ATOM_XML = b"""<?xml version="1.0" encoding="utf-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <title>Atom Feed</title>
  <entry>
    <title>Atom Post</title>
    <link href="https://example.com/atom/1"/>
  </entry>
</feed>
"""

CSV_BODY = b"""title,price,url
First,10.5,https://example.com/products/1
Second,20,https://example.com/products/2
"""

CSV_NO_HEADER = b"""First,10.5
Second,20
"""

CSV_SEMICOLON = b"""title;price
'First;Post';10.5
"""


def _make_response(body: bytes, url: str = "https://example.com/feed.xml", headers: dict | None = None) -> Response:
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


class _RSSSpider(XMLFeedSpider):
    name = "rss"
    start_urls = ["https://example.com/feed.xml"]

    async def parse_node(self, response, node):
        yield {
            "title": node.findtext("title"),
            "link": node.findtext("link"),
            "date": node.findtext("pubDate"),
        }


class TestXMLFeedSpider:
    @pytest.mark.asyncio
    async def test_iterates_default_itertag(self):
        items = await _collect(_RSSSpider().parse(_make_response(RSS_XML)))

        assert len(items) == 2
        assert items[0] == {
            "title": "First Post",
            "link": "https://example.com/posts/1",
            "date": "Mon, 01 Jan 2026 00:00:00 GMT",
        }
        assert items[1]["title"] == "Second Post" and items[1]["date"] is None

    @pytest.mark.asyncio
    async def test_nodes_are_namespace_stripped(self):
        class S(XMLFeedSpider):
            name = "s"

            async def parse_node(self, response, node):
                thumbnail = node.find("thumbnail")
                yield {"thumb": thumbnail.get("url") if thumbnail is not None else None}

        items = await _collect(S().parse(_make_response(RSS_XML)))
        assert items[0]["thumb"] == "https://example.com/thumb1.jpg"

    @pytest.mark.asyncio
    async def test_plain_itertag_matches_namespaced_nodes(self):
        class S(XMLFeedSpider):
            name = "s"
            itertag = "entry"

            async def parse_node(self, response, node):
                link = node.find("link")
                yield {"title": node.findtext("title"), "href": link.get("href") if link is not None else None}

        items = await _collect(S().parse(_make_response(ATOM_XML)))
        assert items == [{"title": "Atom Post", "href": "https://example.com/atom/1"}]

    @pytest.mark.asyncio
    async def test_prefixed_itertag_matches_by_namespace(self):
        class S(XMLFeedSpider):
            name = "s"
            itertag = "media:thumbnail"
            namespaces = (("media", "http://search.yahoo.com/mrss/"),)

            async def parse_node(self, response, node):
                yield {"url": node.get("url")}

        items = await _collect(S().parse(_make_response(RSS_XML)))
        assert items == [{"url": "https://example.com/thumb1.jpg"}]

    @pytest.mark.asyncio
    async def test_unknown_itertag_prefix_raises(self):
        class S(XMLFeedSpider):
            name = "s"
            itertag = "media:thumbnail"

        with pytest.raises(ValueError, match="namespaces"):
            await _collect(S().parse(_make_response(RSS_XML)))

    @pytest.mark.asyncio
    async def test_gzipped_feed_is_decompressed(self):
        items = await _collect(_RSSSpider().parse(_make_response(gzip.compress(RSS_XML))))
        assert len(items) == 2

    @pytest.mark.asyncio
    async def test_malformed_xml_logs_warning_and_yields_nothing(self):
        spider = _RSSSpider()
        records = []

        class Capture(logging.Handler):
            def emit(self, record):
                records.append(record.getMessage())

        spider.logger.addHandler(Capture())
        items = await _collect(spider.parse(_make_response(b"this is <<< not xml")))

        assert items == []
        assert any("Failed to parse XML feed" in message for message in records)

    @pytest.mark.asyncio
    async def test_requests_yielded_from_parse_node_flow_through(self):
        class S(XMLFeedSpider):
            name = "s"

            async def parse_node(self, response, node):
                yield response.follow(node.findtext("link"), callback=self.parse_post)

            async def parse_post(self, response):
                yield {"url": response.url}

        results = await _collect(S().parse(_make_response(RSS_XML)))
        assert len(results) == 2
        assert all(isinstance(r, Request) for r in results)
        assert results[0].url == "https://example.com/posts/1"

    @pytest.mark.asyncio
    async def test_parse_node_not_overridden_raises(self):
        class S(XMLFeedSpider):
            name = "s"

        with pytest.raises(NotImplementedError, match="parse_node"):
            await _collect(S().parse(_make_response(RSS_XML)))

    @pytest.mark.asyncio
    async def test_start_requests_uses_start_urls(self):
        requests = await _collect(_RSSSpider().start_requests())
        assert len(requests) == 1 and requests[0].url == "https://example.com/feed.xml"


class _PriceSpider(CSVFeedSpider):
    name = "prices"
    start_urls = ["https://example.com/feed.csv"]

    async def parse_row(self, response, row):
        yield row


class TestCSVFeedSpider:
    @pytest.mark.asyncio
    async def test_first_row_is_the_header(self):
        rows = await _collect(_PriceSpider().parse(_make_response(CSV_BODY)))

        assert len(rows) == 2
        assert rows[0] == {"title": "First", "price": "10.5", "url": "https://example.com/products/1"}

    @pytest.mark.asyncio
    async def test_explicit_headers(self):
        class S(_PriceSpider):
            headers = ["name", "cost"]

        rows = await _collect(S().parse(_make_response(CSV_NO_HEADER)))
        assert rows == [{"name": "First", "cost": "10.5"}, {"name": "Second", "cost": "20"}]

    @pytest.mark.asyncio
    async def test_custom_delimiter_and_quotechar(self):
        class S(_PriceSpider):
            delimiter = ";"
            quotechar = "'"

        rows = await _collect(S().parse(_make_response(CSV_SEMICOLON)))
        assert rows == [{"title": "First;Post", "price": "10.5"}]

    @pytest.mark.asyncio
    async def test_gzipped_feed_is_decompressed(self):
        rows = await _collect(_PriceSpider().parse(_make_response(gzip.compress(CSV_BODY))))
        assert len(rows) == 2

    @pytest.mark.asyncio
    async def test_empty_body_yields_nothing(self):
        assert await _collect(_PriceSpider().parse(_make_response(b""))) == []

    @pytest.mark.asyncio
    async def test_non_utf8_bytes_do_not_crash(self):
        body = "title,price\nCafé,10\n".encode("latin-1")
        rows = await _collect(_PriceSpider().parse(_make_response(body)))
        assert len(rows) == 1 and rows[0]["price"] == "10"

    @pytest.mark.asyncio
    async def test_parse_row_not_overridden_raises(self):
        class S(CSVFeedSpider):
            name = "s"

        with pytest.raises(NotImplementedError, match="parse_row"):
            await _collect(S().parse(_make_response(CSV_BODY)))

    @pytest.mark.asyncio
    async def test_requests_yielded_from_parse_row_flow_through(self):
        class S(CSVFeedSpider):
            name = "s"

            async def parse_row(self, response, row):
                yield response.follow(row["url"], callback=self.parse_product)

            async def parse_product(self, response):
                yield {"url": response.url}

        results = await _collect(S().parse(_make_response(CSV_BODY, url="https://example.com/feed.csv")))
        assert len(results) == 2
        assert all(isinstance(r, Request) for r in results)
        assert results[0].url == "https://example.com/products/1"
