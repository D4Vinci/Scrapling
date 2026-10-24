"""Tests for conditional requests (`ETag` / `Last-Modified` validators saved between runs)."""

from pathlib import Path

import pytest

from scrapling.spiders.conditional import ConditionalRequestManager
from scrapling.spiders.engine import CrawlerEngine
from scrapling.spiders.request import Request
from scrapling.spiders.session import SessionManager
from scrapling.spiders.spider import Spider
from scrapling.engines.toolbelt.custom import Response
from scrapling.core._types import Any, Dict, List, Optional, AsyncGenerator


def _make_response(
    url: str = "https://example.com/feed",
    status: int = 200,
    body: bytes = b"<rss/>",
    headers: Optional[Dict[str, str]] = None,
) -> Response:
    return Response(
        url=url,
        content=body,
        status=status,
        reason="",
        cookies={},
        headers=headers or {},
        request_headers={},
        _log=False,
    )


class FakeSite:
    """A website that answers conditional requests like a real server would.

    `pages` maps each URL to its `(body, etag, last_modified)`; either validator can be `None`.
    """

    def __init__(self, pages: Dict[str, tuple]):
        self.pages = dict(pages)
        self.sent_headers: List[Dict[str, str]] = []

    def respond(self, url: str, headers: Dict[str, str]) -> Response:
        self.sent_headers.append(dict(headers))
        body, etag, last_modified = self.pages[url]
        sent = {key.lower(): value for key, value in headers.items()}
        response_headers = {}
        if etag:
            response_headers["ETag"] = etag
        if last_modified:
            response_headers["Last-Modified"] = last_modified

        # If-None-Match wins over If-Modified-Since when both are sent (RFC 9110, section 13.2.2)
        if "if-none-match" in sent:
            unchanged = sent["if-none-match"] == etag
        else:
            unchanged = "if-modified-since" in sent and sent["if-modified-since"] == last_modified

        if unchanged:
            return _make_response(url, status=304, body=b"", headers=response_headers)
        return _make_response(url, body=body, headers=response_headers)


class FakeSession:
    def __init__(self, site: FakeSite):
        self.site = site
        self._is_alive = False

    async def __aenter__(self):
        self._is_alive = True
        return self

    async def __aexit__(self, *args):
        self._is_alive = False

    async def fetch(self, url: str, **kwargs: Any) -> Response:
        return self.site.respond(url, kwargs.get("headers") or {})


class MonitorSpider(Spider):
    name = "monitor"
    start_urls = ["https://example.com/feed"]
    conditional_requests = True

    def __init__(self, site: FakeSite, validators_dir: Path, **kwargs: Any):
        self.site = site
        self.conditional_requests_dir = str(validators_dir)
        self.not_modified: List[str] = []
        self.parsed: List[str] = []
        super().__init__(**kwargs)

    def configure_sessions(self, manager: SessionManager) -> None:
        manager.add("default", FakeSession(self.site))

    async def parse(self, response: Response) -> AsyncGenerator[Dict[str, Any] | Request | None, None]:
        self.parsed.append(response.url)
        yield {"url": response.url, "body": response.body}

    async def on_not_modified(self, request: Request, response: Response) -> None:
        self.not_modified.append(request.url)


FEED = {"https://example.com/feed": (b"<rss>v1</rss>", '"v1"', "Sat, 24 Oct 2026 10:00:00 GMT")}


class TestConditionalRequestManager:
    @pytest.mark.asyncio
    async def test_saved_validators_become_conditional_headers(self, tmp_path: Path):
        manager = ConditionalRequestManager(tmp_path)
        fp = b"\x01" * 20
        response = _make_response(headers={"ETag": 'W/"abc"', "Last-Modified": "Sat, 24 Oct 2026 10:00:00 GMT"})

        await manager.put(fp, response)
        assert await manager.get_headers(fp) == {
            "If-None-Match": 'W/"abc"',
            "If-Modified-Since": "Sat, 24 Oct 2026 10:00:00 GMT",
        }

    @pytest.mark.asyncio
    async def test_header_names_are_matched_in_any_case(self, tmp_path: Path):
        manager = ConditionalRequestManager(tmp_path)
        fp = b"\x02" * 20

        await manager.put(fp, _make_response(headers={"etag": '"lower"'}))
        assert await manager.get_headers(fp) == {"If-None-Match": '"lower"'}

    @pytest.mark.asyncio
    async def test_only_last_modified(self, tmp_path: Path):
        manager = ConditionalRequestManager(tmp_path)
        fp = b"\x03" * 20

        await manager.put(fp, _make_response(headers={"last-modified": "Sat, 24 Oct 2026 10:00:00 GMT"}))
        assert await manager.get_headers(fp) == {"If-Modified-Since": "Sat, 24 Oct 2026 10:00:00 GMT"}

    @pytest.mark.asyncio
    async def test_response_without_validators_drops_the_saved_ones(self, tmp_path: Path):
        manager = ConditionalRequestManager(tmp_path)
        fp = b"\x04" * 20

        await manager.put(fp, _make_response(headers={"ETag": '"old"'}))
        await manager.put(fp, _make_response(headers={}))
        assert await manager.get_headers(fp) == {}
        assert not list(tmp_path.glob("*.json"))

    @pytest.mark.asyncio
    async def test_response_without_validators_writes_nothing(self, tmp_path: Path):
        validators_dir = tmp_path / "validators"
        manager = ConditionalRequestManager(validators_dir)

        await manager.put(b"\x05" * 20, _make_response(headers={"content-type": "text/html"}))
        assert not validators_dir.exists()

    @pytest.mark.asyncio
    async def test_put_overwrites(self, tmp_path: Path):
        manager = ConditionalRequestManager(tmp_path)
        fp = b"\x06" * 20

        await manager.put(fp, _make_response(headers={"ETag": '"first"'}))
        await manager.put(fp, _make_response(headers={"ETag": '"second"'}))
        assert await manager.get_headers(fp) == {"If-None-Match": '"second"'}

    @pytest.mark.asyncio
    async def test_missing_and_corrupt_entries_give_no_headers(self, tmp_path: Path):
        manager = ConditionalRequestManager(tmp_path)
        assert await manager.get_headers(b"\x07" * 20) == {}

        fp = b"\x08" * 20
        (tmp_path / f"{fp.hex()}.json").write_text("not json{{")
        assert await manager.get_headers(fp) == {}

    @pytest.mark.asyncio
    async def test_clear(self, tmp_path: Path):
        manager = ConditionalRequestManager(tmp_path)
        fp = b"\x09" * 20

        await manager.put(fp, _make_response(headers={"ETag": '"x"'}))
        await manager.clear()
        assert await manager.get_headers(fp) == {}


class TestConditionalCrawl:
    def test_second_run_skips_the_unchanged_page(self, tmp_path: Path):
        site = FakeSite(FEED)

        first = MonitorSpider(site, tmp_path)
        result = first.start()
        assert site.sent_headers == [{}]
        assert first.parsed == ["https://example.com/feed"]
        assert result.stats.not_modified_count == 0

        second = MonitorSpider(site, tmp_path)
        result = second.start()
        assert site.sent_headers[1] == {
            "If-None-Match": '"v1"',
            "If-Modified-Since": "Sat, 24 Oct 2026 10:00:00 GMT",
        }
        assert second.parsed == []
        assert second.not_modified == ["https://example.com/feed"]
        assert result.stats.not_modified_count == 1
        assert result.stats.response_status_count == {"status_304": 1}
        assert len(result.items) == 0

    def test_changed_page_is_processed_and_its_new_validators_saved(self, tmp_path: Path):
        site = FakeSite(FEED)
        MonitorSpider(site, tmp_path).start()

        site.pages["https://example.com/feed"] = (b"<rss>v2</rss>", '"v2"', None)
        changed = MonitorSpider(site, tmp_path)
        result = changed.start()
        assert [item["body"] for item in result.items] == [b"<rss>v2</rss>"]
        assert changed.not_modified == []

        MonitorSpider(site, tmp_path).start()
        assert site.sent_headers[-1] == {"If-None-Match": '"v2"'}

    def test_last_modified_alone_is_enough(self, tmp_path: Path):
        site = FakeSite({"https://example.com/feed": (b"<rss/>", None, "Sat, 24 Oct 2026 10:00:00 GMT")})
        MonitorSpider(site, tmp_path).start()

        second = MonitorSpider(site, tmp_path)
        second.start()
        assert site.sent_headers[-1] == {"If-Modified-Since": "Sat, 24 Oct 2026 10:00:00 GMT"}
        assert second.not_modified == ["https://example.com/feed"]

    def test_failed_callback_keeps_the_page_unconditional(self, tmp_path: Path):
        class FailingSpider(MonitorSpider):
            async def parse(self, response: Response) -> AsyncGenerator[Dict[str, Any] | Request | None, None]:
                raise RuntimeError("parser broke")
                yield

        site = FakeSite(FEED)
        FailingSpider(site, tmp_path).start()

        retry = MonitorSpider(site, tmp_path)
        retry.start()
        assert site.sent_headers == [{}, {}]
        assert retry.parsed == ["https://example.com/feed"]

    def test_blocked_response_is_not_remembered(self, tmp_path: Path):
        class BlockedSpider(MonitorSpider):
            max_blocked_retries = 0

            async def is_blocked(self, response: Response) -> bool:
                return True

        site = FakeSite(FEED)
        BlockedSpider(site, tmp_path).start()
        MonitorSpider(site, tmp_path).start()
        assert site.sent_headers == [{}, {}]

    def test_followed_requests_dont_inherit_the_validators(self, tmp_path: Path):
        pages = {
            **FEED,
            "https://example.com/article": (b"<html>article</html>", None, None),
        }

        class FollowingSpider(MonitorSpider):
            async def parse(self, response: Response) -> AsyncGenerator[Dict[str, Any] | Request | None, None]:
                self.parsed.append(response.url)
                if response.url.endswith("/feed"):
                    yield response.follow("/article", dont_filter=True)

        site = FakeSite(pages)
        FollowingSpider(site, tmp_path).start()

        # The feed changed, so the second run fetches the article from it again
        site.pages["https://example.com/feed"] = (b"<rss>v2</rss>", '"v2"', None)
        FollowingSpider(site, tmp_path).start()
        article_headers = site.sent_headers[-1]
        assert {key.lower() for key in article_headers} == {"referer"}

    def test_request_kwargs_are_left_untouched(self, tmp_path: Path):
        shared_headers = {"X-Token": "abc"}

        class HeadersSpider(MonitorSpider):
            async def start_requests(self) -> AsyncGenerator[Request, None]:
                yield Request("https://example.com/feed", sid="default", headers=shared_headers)

        site = FakeSite(FEED)
        HeadersSpider(site, tmp_path).start()
        HeadersSpider(site, tmp_path).start()
        assert site.sent_headers[-1] == {
            "X-Token": "abc",
            "If-None-Match": '"v1"',
            "If-Modified-Since": "Sat, 24 Oct 2026 10:00:00 GMT",
        }
        assert shared_headers == {"X-Token": "abc"}

    def test_requests_with_their_own_validators_are_left_alone(self, tmp_path: Path):
        class OwnValidatorsSpider(MonitorSpider):
            async def start_requests(self) -> AsyncGenerator[Request, None]:
                yield Request("https://example.com/feed", sid="default", headers={"If-None-Match": '"mine"'})

        site = FakeSite(FEED)
        spider = OwnValidatorsSpider(site, tmp_path)
        spider.start()
        assert site.sent_headers == [{"If-None-Match": '"mine"'}]
        assert spider.parsed == ["https://example.com/feed"]
        assert not list(tmp_path.glob("*.json"))

    def test_post_requests_are_never_conditional(self, tmp_path: Path):
        class PostSpider(MonitorSpider):
            async def start_requests(self) -> AsyncGenerator[Request, None]:
                yield Request("https://example.com/feed", sid="default", method="POST", data={"q": "x"})

        site = FakeSite(FEED)
        PostSpider(site, tmp_path).start()
        PostSpider(site, tmp_path).start()
        assert site.sent_headers == [{}, {}]

    def test_disabled_by_default(self, tmp_path: Path):
        class PlainSpider(MonitorSpider):
            conditional_requests = False

        site = FakeSite(FEED)
        PlainSpider(site, tmp_path / "validators").start()
        PlainSpider(site, tmp_path / "validators").start()
        assert site.sent_headers == [{}, {}]
        assert not (tmp_path / "validators").exists()

    def test_not_modified_counts_as_healthy_for_autothrottle(self, tmp_path: Path):
        class ThrottledSpider(MonitorSpider):
            autothrottle_enabled = True
            autothrottle_start_delay = 0.01
            autothrottle_max_delay = 1.0

        site = FakeSite(FEED)
        ThrottledSpider(site, tmp_path).start()
        result = ThrottledSpider(site, tmp_path).start()
        assert result.stats.not_modified_count == 1
        # A failed response would have doubled the delay instead of easing it
        assert result.stats.autothrottle_delays["example.com"] <= 0.01


class TestWithHttpSession:
    """The same flow through the default `FetcherSession` against a real server."""

    def test_not_modified_from_a_real_server(self, httpbin, tmp_path: Path):
        url = f"{httpbin.url}/etag/v1"

        class HttpSpider(Spider):
            name = "http_monitor"
            start_urls = [url]
            conditional_requests = True
            conditional_requests_dir = str(tmp_path)

            def __init__(self, **kwargs: Any):
                self.not_modified: List[str] = []
                super().__init__(**kwargs)

            async def parse(self, response: Response) -> AsyncGenerator[Dict[str, Any] | Request | None, None]:
                yield {"status": response.status}

            async def on_not_modified(self, request: Request, response: Response) -> None:
                self.not_modified.append(request.url)

        first = HttpSpider().start()
        assert [item["status"] for item in first.items] == [200]

        spider = HttpSpider()
        second = spider.start()
        assert second.stats.not_modified_count == 1
        assert second.stats.response_status_count == {"status_304": 1}
        assert spider.not_modified == [url]
        assert len(second.items) == 0


class TestDevelopmentModeInteraction:
    def test_disabled_while_development_mode_is_on(self, tmp_path: Path):
        site = FakeSite(FEED)

        class DevSpider(MonitorSpider):
            development_mode = True

            def __init__(self, *args: Any, **kwargs: Any):
                self.development_cache_dir = str(tmp_path / "cache")
                super().__init__(*args, **kwargs)

        spider = DevSpider(site, tmp_path / "validators")
        engine = CrawlerEngine(spider, spider._session_manager)
        assert engine._cache_manager is not None
        assert engine._conditional_manager is None

        first = DevSpider(site, tmp_path / "validators").start()
        second = DevSpider(site, tmp_path / "validators").start()
        # Only the first run touched the website; the second one was replayed from the response cache
        assert site.sent_headers == [{}]
        assert second.stats.cache_hits == 1
        assert [item["body"] for item in first.items] == [item["body"] for item in second.items] == [b"<rss>v1</rss>"]
        assert not (tmp_path / "validators").exists()


class TestSessionManagerHeaders:
    @pytest.mark.asyncio
    async def test_fetch_headers_are_merged_without_touching_the_request(self):
        site = FakeSite(FEED)
        manager = SessionManager()
        manager.add("default", FakeSession(site))
        request = Request("https://example.com/feed", sid="default", headers={"X-Token": "abc"})

        async with manager:
            response = await manager.fetch(request, headers={"If-None-Match": '"v1"'})

        assert site.sent_headers == [{"X-Token": "abc", "If-None-Match": '"v1"'}]
        assert request._session_kwargs == {"headers": {"X-Token": "abc"}}
        assert response.request is request
        assert response.status == 304
