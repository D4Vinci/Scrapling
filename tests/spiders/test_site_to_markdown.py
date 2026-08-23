"""Tests for `SiteToMarkdownSpider`."""

import pytest

from scrapling.engines.toolbelt.custom import Response
from scrapling.spiders.links import LinkExtractor
from scrapling.spiders.request import Request
from scrapling.spiders.templates import CrawlRule, SiteToMarkdownSpider
from scrapling.core._types import AsyncGenerator

HTML = """
<html>
  <head><title> Example Site </title></head>
  <body>
    <h1>Welcome</h1>
    <div class="content"><p>Main content.</p></div>
    <a href="/docs/page-1">page 1</a>
    <a href="/blog/post-1">post 1</a>
  </body>
</html>
"""


def _make_response(url: str = "https://example.com/") -> Response:
    resp = Response(
        url=url,
        content=HTML,
        status=200,
        reason="OK",
        cookies={},
        headers={},
        request_headers={},
    )
    resp.request = Request(url)
    return resp


async def _collect(agen: AsyncGenerator) -> list:
    return [item async for item in agen]


def _spider(**attrs) -> SiteToMarkdownSpider:
    class S(SiteToMarkdownSpider):
        name = "s"
        start_urls = ["https://example.com/"]
        allowed_domains = {"example.com"}

    for name, value in attrs.items():
        setattr(S, name, value)
    return S()


class TestSiteToMarkdownSpider:
    def test_requires_allowed_domains(self):
        class S(SiteToMarkdownSpider):
            name = "s"
            start_urls = ["https://example.com/"]

        with pytest.raises(ValueError, match="allowed_domains"):
            S()

    @pytest.mark.asyncio
    async def test_parse_yields_item_and_follow_requests(self):
        out = await _collect(_spider().parse(_make_response()))
        items = [o for o in out if isinstance(o, dict)]
        requests = [o for o in out if isinstance(o, Request)]

        assert len(items) == 1
        item = items[0]
        assert item["url"] == "https://example.com/"
        assert item["title"] == "Example Site"
        assert type(item["title"]) is str
        assert type(item["markdown"]) is str
        assert "Welcome\n=======" in item["markdown"]
        assert "Example Site" not in item["markdown"], "main_content_only must exclude the <head>"
        assert [r.url for r in requests] == ["https://example.com/docs/page-1", "https://example.com/blog/post-1"]

    @pytest.mark.asyncio
    async def test_max_pages_caps_converted_pages(self):
        spider = _spider(max_pages=1)
        out = await _collect(spider.parse(_make_response()))
        assert len([o for o in out if isinstance(o, dict)]) == 1
        assert not [o for o in out if isinstance(o, Request)]

        beyond_cap = await _collect(spider.parse(_make_response("https://example.com/docs/page-1")))
        assert beyond_cap == []

    @pytest.mark.asyncio
    async def test_rules_override_narrows_the_crawl(self):
        spider = _spider()
        spider.rules = lambda: [CrawlRule(LinkExtractor(allow=r"/blog/"))]  # type: ignore[method-assign]
        out = await _collect(spider.parse(_make_response()))
        assert [r.url for r in out if isinstance(r, Request)] == ["https://example.com/blog/post-1"]

    @pytest.mark.asyncio
    async def test_rules_override_drops_url_patterns(self):
        spider = _spider()
        spider.rules = lambda: [CrawlRule(LinkExtractor(deny=r"/blog/"))]  # type: ignore[method-assign]
        out = await _collect(spider.parse(_make_response()))
        assert [r.url for r in out if isinstance(r, Request)] == ["https://example.com/docs/page-1"]

    @pytest.mark.asyncio
    async def test_css_selector_narrows_the_markdown(self):
        out = await _collect(_spider(css_selector=".content").parse(_make_response()))
        markdown = [o for o in out if isinstance(o, dict)][0]["markdown"]
        assert "Main content." in markdown
        assert "Welcome" not in markdown


class TestSiteToMarkdownOutputDir:
    @pytest.mark.asyncio
    async def test_writes_one_file_per_page(self, tmp_path):
        spider = _spider(output_dir=str(tmp_path))
        item = (await _collect(spider.parse(_make_response())))[0]

        returned = await spider.on_scraped_item(item)
        assert returned is item
        file = tmp_path / "example.com.md"
        assert file.exists()
        assert "Welcome" in file.read_text(encoding="utf-8")

    @pytest.mark.asyncio
    async def test_collisions_get_a_hash_suffix(self, tmp_path):
        spider = _spider(output_dir=str(tmp_path))
        item = (await _collect(spider.parse(_make_response())))[0]

        await spider.on_scraped_item(item)
        await spider.on_scraped_item(item)
        names = {f.name for f in tmp_path.iterdir()}
        assert len(names) == 2
        assert "example.com.md" in names
        suffixed = (names - {"example.com.md"}).pop()
        assert suffixed.startswith("example.com-") and suffixed.endswith(".md")

    def test_filenames_are_slugified_from_the_url(self):
        spider = _spider()
        assert spider._filename_for("https://example.com/") == "example.com"
        assert spider._filename_for("https://example.com/docs/page-1") == "example.com-docs-page-1"

    @pytest.mark.asyncio
    async def test_no_output_dir_writes_nothing(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        spider = _spider()
        item = (await _collect(spider.parse(_make_response())))[0]
        assert await spider.on_scraped_item(item) is item
        assert not list(tmp_path.iterdir())
