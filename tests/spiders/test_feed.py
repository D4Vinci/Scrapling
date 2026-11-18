"""Tests for `XMLFeedSpider` and `CSVFeedSpider`."""

import gzip
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread
import logging

import pytest

from scrapling.engines.toolbelt.custom import Response
from scrapling.spiders.request import Request
from scrapling.spiders.templates.feed import CSVFeedSpider, XMLFeedSpider
from scrapling.spiders import JSONFeedSpider
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
    @pytest.mark.parametrize("damage", ["truncated", "deflate"])
    async def test_invalid_gzip_yields_nothing(self, damage: str) -> None:
        """Malformed gzip must follow the feed's existing error handling."""
        body = gzip.compress(RSS_XML)
        body = body[:-4] if damage == "truncated" else body[:10] + b"\x07" + body[11:]

        assert await _collect(_RSSSpider().parse(_make_response(body))) == []

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
    @pytest.mark.parametrize("newline", ["\n", "\r\n", "\r"])
    @pytest.mark.parametrize("explicit_headers", [False, True])
    @pytest.mark.parametrize("compressed", [False, True])
    async def test_record_newlines_preserve_quoted_line_breaks(
        self, newline: str, explicit_headers: bool, compressed: bool
    ) -> None:
        """记录分隔符应兼容 CR，同时保留引号字段里的原始换行。"""
        spider = _PriceSpider()
        records = ['"First\rPost",10', '"Second\r\nPost",20']
        if explicit_headers:
            spider.headers = ["title", "price"]
        else:
            records.insert(0, "title,price")
        body = (newline.join(records) + newline).encode()
        if compressed:
            body = gzip.compress(body)

        rows = await _collect(spider.parse(_make_response(body)))

        assert rows == [{"title": "First\rPost", "price": "10"}, {"title": "Second\r\nPost", "price": "20"}]

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
    @pytest.mark.parametrize("damage", ["truncated", "deflate"])
    async def test_invalid_gzip_yields_nothing(self, damage: str) -> None:
        """Malformed gzip must follow the feed's existing error handling."""
        body = gzip.compress(CSV_BODY)
        body = body[:-4] if damage == "truncated" else body[:10] + b"\x07" + body[11:]

        assert await _collect(_PriceSpider().parse(_make_response(body))) == []

    @pytest.mark.asyncio
    async def test_leading_byte_order_mark_stays_out_of_the_first_column(self):
        rows = await _collect(_PriceSpider().parse(_make_response(b"\xef\xbb\xbf" + CSV_BODY)))
        assert rows[0] == {"title": "First", "price": "10.5", "url": "https://example.com/products/1"}

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


class _JSONSpider(JSONFeedSpider):
    name = "json-feed"
    start_urls = ["https://example.com/feed.json"]

    async def parse_item(self, response, item):
        yield item


class TestJSONFeedSpider:
    @pytest.mark.asyncio
    @pytest.mark.parametrize("compressed", [False, True])
    async def test_preserves_items_and_follows_next_page(self, compressed):
        items = [
            {"id": "a", "content_html": "<p>News</p>", "_custom": {"score": 1}},
            {"id": "b", "content_text": "Update"},
        ]
        body = json.dumps(
            {"version": "https://jsonfeed.org/version/1.1", "items": items, "next_url": "?page=2"}
        ).encode()
        if compressed:
            body = gzip.compress(body)
        spider = _JSONSpider()
        results = await _collect(spider.parse(_make_response(body, "https://example.com/feed.json")))
        assert results[:2] == items
        request = results[2]
        assert isinstance(request, Request)
        assert request.url == "https://example.com/feed.json?page=2"
        assert request.callback == spider.parse
        assert request.sid == "default"

    @pytest.mark.asyncio
    async def test_next_page_can_be_disabled(self):
        spider = _JSONSpider()
        spider.follow_next = False
        body = json.dumps({"items": [{"id": "a"}], "next_url": "https://example.com/next.json"}).encode()
        assert await _collect(spider.parse(_make_response(body))) == [{"id": "a"}]

    @pytest.mark.asyncio
    @pytest.mark.parametrize("body", [b"{", b"[]", b'{"items":{}}', b"\x1f\x8bbroken"])
    async def test_bad_feed_is_reported(self, body, caplog, monkeypatch):
        spider = _JSONSpider()
        monkeypatch.setattr(spider.logger, "propagate", True)
        with caplog.at_level(logging.WARNING):
            assert await _collect(spider.parse(_make_response(body))) == []
        assert caplog.records

    @pytest.mark.asyncio
    async def test_bad_item_does_not_drop_remaining_items(self, caplog, monkeypatch):
        spider = _JSONSpider()
        monkeypatch.setattr(spider.logger, "propagate", True)
        body = json.dumps({"items": [None, {"id": "a"}], "next_url": 42}).encode()
        with caplog.at_level(logging.WARNING):
            assert await _collect(spider.parse(_make_response(body))) == [{"id": "a"}]
        assert "not an object" in caplog.text
        assert "next_url" in caplog.text

    @pytest.mark.asyncio
    async def test_callback_can_follow_article(self):
        class ArticleSpider(_JSONSpider):
            async def parse_item(self, response, item):
                yield response.follow(item["url"])

        body = json.dumps({"items": [{"id": "a", "url": "/article"}]}).encode()
        results = await _collect(ArticleSpider().parse(_make_response(body)))
        assert results[0].url == "https://example.com/article"

    @pytest.mark.asyncio
    async def test_real_crawl_follows_pages_and_stops_at_repeated_url(self):
        visited = []

        class Handler(BaseHTTPRequestHandler):
            def do_GET(self):
                visited.append(self.path)
                data = {
                    "version": "https://jsonfeed.org/version/1.1",
                    "items": [{"id": self.path}],
                    "next_url": "/second.json",
                }
                body = json.dumps(data).encode()
                self.send_response(200)
                self.send_header("Content-Type", "application/feed+json")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)

            def log_message(self, *args):
                pass

        server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        thread = Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:

            class NewsSpider(_JSONSpider):
                start_urls = [f"http://127.0.0.1:{server.server_port}/first.json"]

            items = [item async for item in NewsSpider().stream()]
            assert [item["id"] for item in items] == ["/first.json", "/second.json"]
            assert visited == ["/first.json", "/second.json"]
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=5)
