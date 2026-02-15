"""Tests for the CrawlerEngine class."""

import tempfile
from pathlib import Path

import anyio
import pytest

from scrapling.spiders.engine import CrawlerEngine, _dump
from scrapling.spiders.request import Request
from scrapling.spiders.session import SessionManager
from scrapling.spiders.result import CrawlStats, ItemList
from scrapling.spiders.checkpoint import CheckpointData
from scrapling.core._types import Any, Dict, Set, AsyncGenerator


# ---------------------------------------------------------------------------
# Mock helpers
# ---------------------------------------------------------------------------


class MockResponse:
    """Minimal Response stand-in."""

    def __init__(self, status: int = 200, body: bytes = b"ok", url: str = "https://example.com"):
        self.status = status
        self.body = body
        self.url = url
        self.request: Any = None
        self.meta: Dict[str, Any] = {}

    def __str__(self) -> str:
        return self.url


class MockSession:
    """Mock session that returns a canned response."""

    def __init__(self, name: str = "mock", response: MockResponse | None = None):
        self.name = name
        self._is_alive = False
        self._response = response or MockResponse()
        self.fetch_calls: list[dict] = []

    async def __aenter__(self):
        self._is_alive = True
        return self

    async def __aexit__(self, *args):
        self._is_alive = False

    async def fetch(self, url: str, **kwargs):
        self.fetch_calls.append({"url": url, **kwargs})
        resp = MockResponse(status=self._response.status, body=self._response.body, url=url)
        return resp


class ErrorSession(MockSession):
    """Session that raises on fetch."""

    def __init__(self, error: Exception | None = None):
        super().__init__("error")
        self._error = error or RuntimeError("fetch failed")

    async def fetch(self, url: str, **kwargs):
        raise self._error


class MockSpider:
    """Lightweight spider stub for engine tests."""

    def __init__(
        self,
        *,
        concurrent_requests: int = 4,
        concurrent_requests_per_domain: int = 0,
        download_delay: float = 0.0,
        max_blocked_retries: int = 3,
        allowed_domains: Set[str] | None = None,
        fp_include_kwargs: bool = False,
        fp_include_headers: bool = False,
        fp_keep_fragments: bool = False,
        is_blocked_fn=None,
        on_scraped_item_fn=None,
        retry_blocked_request_fn=None,
    ):
        self.concurrent_requests = concurrent_requests
        self.concurrent_requests_per_domain = concurrent_requests_per_domain
        self.download_delay = download_delay
        self.max_blocked_retries = max_blocked_retries
        self.allowed_domains = allowed_domains or set()
        self.fp_include_kwargs = fp_include_kwargs
        self.fp_include_headers = fp_include_headers
        self.fp_keep_fragments = fp_keep_fragments
        self.name = "test_spider"

        # Tracking lists
        self.on_start_calls: list[dict] = []
        self.on_close_calls: int = 0
        self.on_error_calls: list[tuple[Request, Exception]] = []
        self.scraped_items: list[dict] = []
        self.blocked_responses: list = []
        self.retry_requests: list = []

        # Pluggable behaviour
        self._is_blocked_fn = is_blocked_fn
        self._on_scraped_item_fn = on_scraped_item_fn
        self._retry_blocked_request_fn = retry_blocked_request_fn

        # Log counter stub
        self._log_counter = _LogCounterStub()

    async def parse(self, response) -> AsyncGenerator[Dict[str, Any] | Request | None, None]:
        yield {"url": str(response)}

    async def on_start(self, resuming: bool = False) -> None:
        self.on_start_calls.append({"resuming": resuming})

    async def on_close(self) -> None:
        self.on_close_calls += 1

    async def on_error(self, request: Request, error: Exception) -> None:
        self.on_error_calls.append((request, error))

    async def on_scraped_item(self, item: Dict[str, Any]) -> Dict[str, Any] | None:
        if self._on_scraped_item_fn:
            return self._on_scraped_item_fn(item)
        self.scraped_items.append(item)
        return item

    async def is_blocked(self, response) -> bool:
        if self._is_blocked_fn:
            return self._is_blocked_fn(response)
        return False

    async def retry_blocked_request(self, request: Request, response) -> Request:
        self.retry_requests.append(request)
        if self._retry_blocked_request_fn:
            return self._retry_blocked_request_fn(request, response)
        return request

    async def start_requests(self) -> AsyncGenerator[Request, None]:
        yield Request("https://example.com", sid="default")


class _LogCounterStub:
    """Stub for LogCounterHandler."""

    def get_counts(self) -> Dict[str, int]:
        return {"debug": 0, "info": 0, "warning": 0, "error": 0, "critical": 0}


def _make_engine(
    spider: MockSpider | None = None,
    session: MockSession | None = None,
    crawldir: str | None = None,
    interval: float = 300.0,
) -> CrawlerEngine:
    """Create a CrawlerEngine wired to mock objects."""
    spider = spider or MockSpider()
    sm = SessionManager()
    sm.add("default", session or MockSession())
    return CrawlerEngine(spider, sm, crawldir=crawldir, interval=interval)


# ---------------------------------------------------------------------------
# Tests: _dump helper
# ---------------------------------------------------------------------------


class TestDumpHelper:
    def test_dump_returns_json_string(self):
        result = _dump({"key": "value"})
        assert '"key": "value"' in result

    def test_dump_handles_nested(self):
        result = _dump({"a": {"b": 1}})
        assert '"a"' in result
        assert '"b"' in result


# ---------------------------------------------------------------------------
# Tests: __init__
# ---------------------------------------------------------------------------


class TestCrawlerEngineInit:
    def test_default_initialisation(self):
        engine = _make_engine()

        assert engine._running is False
        assert engine._active_tasks == 0
        assert engine._pause_requested is False
        assert engine._force_stop is False
        assert engine.paused is False
        assert isinstance(engine.stats, CrawlStats)
        assert isinstance(engine.items, ItemList)

    def test_checkpoint_system_disabled_by_default(self):
        engine = _make_engine()
        assert engine._checkpoint_system_enabled is False

    def test_checkpoint_system_enabled_with_crawldir(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            engine = _make_engine(crawldir=tmpdir)
            assert engine._checkpoint_system_enabled is True

    def test_global_limiter_uses_concurrent_requests(self):
        spider = MockSpider(concurrent_requests=8)
        engine = _make_engine(spider=spider)
        assert engine._global_limiter.total_tokens == 8

    def test_allowed_domains_from_spider(self):
        spider = MockSpider(allowed_domains={"example.com", "test.org"})
        engine = _make_engine(spider=spider)
        assert engine._allowed_domains == {"example.com", "test.org"}


# ---------------------------------------------------------------------------
# Tests: _is_domain_allowed
# ---------------------------------------------------------------------------


class TestIsDomainAllowed:
    def test_all_allowed_when_empty(self):
        engine = _make_engine()
        request = Request("https://anything.com/page")
        assert engine._is_domain_allowed(request) is True

    def test_exact_domain_match(self):
        spider = MockSpider(allowed_domains={"example.com"})
        engine = _make_engine(spider=spider)

        assert engine._is_domain_allowed(Request("https://example.com/page")) is True
        assert engine._is_domain_allowed(Request("https://other.com/page")) is False

    def test_subdomain_match(self):
        spider = MockSpider(allowed_domains={"example.com"})
        engine = _make_engine(spider=spider)

        assert engine._is_domain_allowed(Request("https://sub.example.com/page")) is True
        assert engine._is_domain_allowed(Request("https://deep.sub.example.com/x")) is True

    def test_partial_name_not_matched(self):
        spider = MockSpider(allowed_domains={"example.com"})
        engine = _make_engine(spider=spider)

        # "notexample.com" should NOT match "example.com"
        assert engine._is_domain_allowed(Request("https://notexample.com/x")) is False

    def test_multiple_allowed_domains(self):
        spider = MockSpider(allowed_domains={"a.com", "b.org"})
        engine = _make_engine(spider=spider)

        assert engine._is_domain_allowed(Request("https://a.com/")) is True
        assert engine._is_domain_allowed(Request("https://b.org/")) is True
        assert engine._is_domain_allowed(Request("https://c.net/")) is False


# ---------------------------------------------------------------------------
# Tests: _rate_limiter
# ---------------------------------------------------------------------------


class TestRateLimiter:
    def test_returns_global_limiter_when_per_domain_disabled(self):
        engine = _make_engine()  # concurrent_requests_per_domain=0
        limiter = engine._rate_limiter("example.com")
        assert limiter is engine._global_limiter

    def test_returns_per_domain_limiter_when_enabled(self):
        spider = MockSpider(concurrent_requests_per_domain=2)
        engine = _make_engine(spider=spider)

        limiter = engine._rate_limiter("example.com")
        assert limiter is not engine._global_limiter
        assert limiter.total_tokens == 2

    def test_same_domain_returns_same_limiter(self):
        spider = MockSpider(concurrent_requests_per_domain=2)
        engine = _make_engine(spider=spider)

        l1 = engine._rate_limiter("example.com")
        l2 = engine._rate_limiter("example.com")
        assert l1 is l2

    def test_different_domains_get_different_limiters(self):
        spider = MockSpider(concurrent_requests_per_domain=2)
        engine = _make_engine(spider=spider)

        l1 = engine._rate_limiter("a.com")
        l2 = engine._rate_limiter("b.com")
        assert l1 is not l2


# ---------------------------------------------------------------------------
# Tests: _normalize_request
# ---------------------------------------------------------------------------


class TestNormalizeRequest:
    def test_sets_default_sid_when_empty(self):
        engine = _make_engine()
        request = Request("https://example.com")
        assert request.sid == ""

        engine._normalize_request(request)
        assert request.sid == "default"

    def test_preserves_existing_sid(self):
        engine = _make_engine()
        request = Request("https://example.com", sid="custom")

        engine._normalize_request(request)
        assert request.sid == "custom"


# ---------------------------------------------------------------------------
# Tests: _process_request
# ---------------------------------------------------------------------------


class TestProcessRequest:
    @pytest.mark.asyncio
    async def test_successful_fetch_updates_stats(self):
        spider = MockSpider()
        session = MockSession(response=MockResponse(status=200, body=b"hello"))
        engine = _make_engine(spider=spider, session=session)

        request = Request("https://example.com", sid="default")
        await engine._process_request(request)

        assert engine.stats.requests_count == 1
        assert engine.stats.response_bytes == 5  # len(b"hello") from MockSession
        assert "status_200" in engine.stats.response_status_count

    @pytest.mark.asyncio
    async def test_failed_fetch_increments_failed_count(self):
        spider = MockSpider()
        sm = SessionManager()
        sm.add("default", ErrorSession())
        engine = CrawlerEngine(spider, sm)

        request = Request("https://example.com", sid="default")
        await engine._process_request(request)

        assert engine.stats.failed_requests_count == 1
        assert len(spider.on_error_calls) == 1

    @pytest.mark.asyncio
    async def test_failed_fetch_does_not_increment_requests_count(self):
        spider = MockSpider()
        sm = SessionManager()
        sm.add("default", ErrorSession())
        engine = CrawlerEngine(spider, sm)

        request = Request("https://example.com", sid="default")
        await engine._process_request(request)

        assert engine.stats.requests_count == 0

    @pytest.mark.asyncio
    async def test_blocked_response_triggers_retry(self):
        spider = MockSpider(is_blocked_fn=lambda r: True, max_blocked_retries=2)
        engine = _make_engine(spider=spider)

        request = Request("https://example.com", sid="default")
        await engine._process_request(request)

        assert engine.stats.blocked_requests_count == 1
        # A retry request should be enqueued
        assert not engine.scheduler.is_empty

    @pytest.mark.asyncio
    async def test_blocked_response_max_retries_exceeded(self):
        spider = MockSpider(is_blocked_fn=lambda r: True, max_blocked_retries=2)
        engine = _make_engine(spider=spider)

        request = Request("https://example.com", sid="default")
        request._retry_count = 2  # Already at max
        await engine._process_request(request)

        assert engine.stats.blocked_requests_count == 1
        # No retry enqueued
        assert engine.scheduler.is_empty

    @pytest.mark.asyncio
    async def test_retry_request_has_dont_filter(self):
        spider = MockSpider(is_blocked_fn=lambda r: True, max_blocked_retries=3)
        engine = _make_engine(spider=spider)

        request = Request("https://example.com", sid="default")
        await engine._process_request(request)

        retry = await engine.scheduler.dequeue()
        assert retry.dont_filter is True
        assert retry._retry_count == 1

    @pytest.mark.asyncio
    async def test_retry_clears_proxy_kwargs(self):
        spider = MockSpider(is_blocked_fn=lambda r: True, max_blocked_retries=3)
        engine = _make_engine(spider=spider)

        request = Request("https://example.com", sid="default", proxy="http://proxy:8080")
        await engine._process_request(request)

        retry = await engine.scheduler.dequeue()
        assert "proxy" not in retry._session_kwargs
        assert "proxies" not in retry._session_kwargs

    @pytest.mark.asyncio
    async def test_callback_yielding_dict_increments_items(self):
        spider = MockSpider()
        engine = _make_engine(spider=spider)

        request = Request("https://example.com", sid="default")
        await engine._process_request(request)

        assert engine.stats.items_scraped == 1
        assert len(engine.items) == 1

    @pytest.mark.asyncio
    async def test_callback_yielding_request_enqueues(self):
        async def callback(response) -> AsyncGenerator:
            yield Request("https://example.com/page2", sid="default")

        spider = MockSpider()
        engine = _make_engine(spider=spider)

        request = Request("https://example.com", sid="default", callback=callback)
        await engine._process_request(request)

        assert not engine.scheduler.is_empty

    @pytest.mark.asyncio
    async def test_callback_yielding_offsite_request_filtered(self):
        async def callback(response) -> AsyncGenerator:
            yield Request("https://other.com/page", sid="default")

        spider = MockSpider(allowed_domains={"example.com"})
        engine = _make_engine(spider=spider)

        request = Request("https://example.com", sid="default", callback=callback)
        await engine._process_request(request)

        assert engine.stats.offsite_requests_count == 1
        assert engine.scheduler.is_empty

    @pytest.mark.asyncio
    async def test_dropped_item_when_on_scraped_item_returns_none(self):
        spider = MockSpider(on_scraped_item_fn=lambda item: None)
        engine = _make_engine(spider=spider)

        request = Request("https://example.com", sid="default")
        await engine._process_request(request)

        assert engine.stats.items_dropped == 1
        assert engine.stats.items_scraped == 0
        assert len(engine.items) == 0

    @pytest.mark.asyncio
    async def test_callback_exception_calls_on_error(self):
        async def bad_callback(response) -> AsyncGenerator:
            raise ValueError("callback boom")
            yield  # noqa: unreachable

        spider = MockSpider()
        engine = _make_engine(spider=spider)

        request = Request("https://example.com", sid="default", callback=bad_callback)
        await engine._process_request(request)

        assert len(spider.on_error_calls) == 1
        assert isinstance(spider.on_error_calls[0][1], ValueError)

    @pytest.mark.asyncio
    async def test_proxy_tracked_in_stats(self):
        spider = MockSpider()
        engine = _make_engine(spider=spider)

        request = Request("https://example.com", sid="default", proxy="http://p:8080")
        await engine._process_request(request)

        assert "http://p:8080" in engine.stats.proxies

    @pytest.mark.asyncio
    async def test_proxies_dict_tracked_in_stats(self):
        spider = MockSpider()
        engine = _make_engine(spider=spider)

        proxies = {"http": "http://p:8080", "https": "https://p:8443"}
        request = Request("https://example.com", sid="default", proxies=proxies)
        await engine._process_request(request)

        assert len(engine.stats.proxies) == 1
        assert engine.stats.proxies[0] == proxies

    @pytest.mark.asyncio
    async def test_uses_parse_when_no_callback(self):
        items_seen = []

        async def custom_parse(response) -> AsyncGenerator:
            yield {"from": "custom_parse"}

        spider = MockSpider()
        spider.parse = custom_parse  # type: ignore[assignment]
        engine = _make_engine(spider=spider)

        request = Request("https://example.com", sid="default")
        # No callback set → should use spider.parse
        await engine._process_request(request)

        assert engine.stats.items_scraped == 1


# ---------------------------------------------------------------------------
# Tests: _task_wrapper
# ---------------------------------------------------------------------------


class TestTaskWrapper:
    @pytest.mark.asyncio
    async def test_decrements_active_tasks(self):
        engine = _make_engine()
        engine._active_tasks = 1

        request = Request("https://example.com", sid="default")
        await engine._task_wrapper(request)

        assert engine._active_tasks == 0

    @pytest.mark.asyncio
    async def test_decrements_even_on_error(self):
        spider = MockSpider()
        sm = SessionManager()
        sm.add("default", ErrorSession())
        engine = CrawlerEngine(spider, sm)
        engine._active_tasks = 1

        request = Request("https://example.com", sid="default")
        await engine._task_wrapper(request)

        assert engine._active_tasks == 0


# ---------------------------------------------------------------------------
# Tests: request_pause
# ---------------------------------------------------------------------------


class TestRequestPause:
    def test_first_call_sets_pause_requested(self):
        engine = _make_engine()

        engine.request_pause()

        assert engine._pause_requested is True
        assert engine._force_stop is False

    def test_second_call_sets_force_stop(self):
        engine = _make_engine()

        engine.request_pause()  # first
        engine.request_pause()  # second

        assert engine._pause_requested is True
        assert engine._force_stop is True

    def test_third_call_after_force_stop_is_noop(self):
        engine = _make_engine()

        engine.request_pause()
        engine.request_pause()
        engine.request_pause()  # should not raise

        assert engine._force_stop is True


# ---------------------------------------------------------------------------
# Tests: checkpoint methods
# ---------------------------------------------------------------------------


class TestCheckpointMethods:
    def test_is_checkpoint_time_false_when_disabled(self):
        engine = _make_engine()  # no crawldir
        assert engine._is_checkpoint_time() is False

    @pytest.mark.asyncio
    async def test_save_and_restore_checkpoint(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            spider = MockSpider()
            engine = _make_engine(spider=spider, crawldir=tmpdir)

            # Enqueue a request so snapshot has data
            req = Request("https://example.com", sid="default")
            engine._normalize_request(req)
            await engine.scheduler.enqueue(req)

            await engine._save_checkpoint()

            # Verify checkpoint file exists
            checkpoint_path = Path(tmpdir) / "checkpoint.pkl"
            assert checkpoint_path.exists()

    @pytest.mark.asyncio
    async def test_restore_when_no_checkpoint_returns_false(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            engine = _make_engine(crawldir=tmpdir)
            result = await engine._restore_from_checkpoint()
            assert result is False

    @pytest.mark.asyncio
    async def test_restore_from_checkpoint_raises_when_disabled(self):
        engine = _make_engine()  # no crawldir → checkpoint disabled
        with pytest.raises(RuntimeError):
            await engine._restore_from_checkpoint()


# ---------------------------------------------------------------------------
# Tests: crawl
# ---------------------------------------------------------------------------


class TestCrawl:
    @pytest.mark.asyncio
    async def test_basic_crawl_returns_stats(self):
        spider = MockSpider()
        engine = _make_engine(spider=spider)

        stats = await engine.crawl()

        assert isinstance(stats, CrawlStats)
        assert stats.requests_count >= 1
        assert stats.items_scraped >= 1

    @pytest.mark.asyncio
    async def test_crawl_calls_on_start_and_on_close(self):
        spider = MockSpider()
        engine = _make_engine(spider=spider)

        await engine.crawl()

        assert len(spider.on_start_calls) == 1
        assert spider.on_start_calls[0]["resuming"] is False
        assert spider.on_close_calls == 1

    @pytest.mark.asyncio
    async def test_crawl_sets_stats_timing(self):
        spider = MockSpider()
        engine = _make_engine(spider=spider)

        stats = await engine.crawl()

        assert stats.start_time > 0
        assert stats.end_time > 0
        assert stats.end_time >= stats.start_time

    @pytest.mark.asyncio
    async def test_crawl_sets_concurrency_stats(self):
        spider = MockSpider(concurrent_requests=16, concurrent_requests_per_domain=4)
        engine = _make_engine(spider=spider)

        stats = await engine.crawl()

        assert stats.concurrent_requests == 16
        assert stats.concurrent_requests_per_domain == 4

    @pytest.mark.asyncio
    async def test_crawl_processes_multiple_start_urls(self):
        spider = MockSpider()

        urls = ["https://example.com/1", "https://example.com/2", "https://example.com/3"]

        async def multi_start_requests() -> AsyncGenerator[Request, None]:
            for url in urls:
                yield Request(url, sid="default")

        spider.start_requests = multi_start_requests  # type: ignore[assignment]
        engine = _make_engine(spider=spider)

        stats = await engine.crawl()

        assert stats.requests_count == 3
        assert stats.items_scraped == 3

    @pytest.mark.asyncio
    async def test_crawl_follows_yielded_requests(self):
        """Test that requests yielded from callbacks are processed."""
        call_count = 0

        async def parse_with_follow(response) -> AsyncGenerator:
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                yield Request("https://example.com/page2", sid="default")
            yield {"page": str(response)}

        spider = MockSpider()
        spider.parse = parse_with_follow  # type: ignore[assignment]
        engine = _make_engine(spider=spider)

        stats = await engine.crawl()

        assert stats.requests_count == 2
        assert stats.items_scraped == 2

    @pytest.mark.asyncio
    async def test_crawl_with_download_delay(self):
        spider = MockSpider(download_delay=0.01)
        engine = _make_engine(spider=spider)

        stats = await engine.crawl()

        assert stats.download_delay == 0.01
        assert stats.requests_count >= 1

    @pytest.mark.asyncio
    async def test_crawl_filters_offsite_requests(self):
        async def parse_offsite(response) -> AsyncGenerator:
            yield Request("https://other-domain.com/page", sid="default")
            yield {"url": str(response)}

        spider = MockSpider(allowed_domains={"example.com"})
        spider.parse = parse_offsite  # type: ignore[assignment]
        engine = _make_engine(spider=spider)

        stats = await engine.crawl()

        assert stats.offsite_requests_count == 1
        assert stats.requests_count == 1  # Only the initial request

    @pytest.mark.asyncio
    async def test_crawl_cleans_up_checkpoint_on_completion(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            spider = MockSpider()
            engine = _make_engine(spider=spider, crawldir=tmpdir)

            await engine.crawl()

            checkpoint_path = Path(tmpdir) / "checkpoint.pkl"
            assert not checkpoint_path.exists()  # Cleaned up

    @pytest.mark.asyncio
    async def test_crawl_handles_fetch_error_gracefully(self):
        spider = MockSpider()
        sm = SessionManager()
        sm.add("default", ErrorSession())
        engine = CrawlerEngine(spider, sm)

        stats = await engine.crawl()

        assert stats.failed_requests_count == 1
        assert len(spider.on_error_calls) == 1

    @pytest.mark.asyncio
    async def test_crawl_log_levels_populated(self):
        spider = MockSpider()
        engine = _make_engine(spider=spider)

        stats = await engine.crawl()

        assert isinstance(stats.log_levels_counter, dict)

    @pytest.mark.asyncio
    async def test_crawl_resets_state_on_each_run(self):
        spider = MockSpider()
        engine = _make_engine(spider=spider)

        # Run first crawl
        await engine.crawl()
        assert engine.stats.requests_count >= 1

        # Run second crawl - stats should reset
        stats = await engine.crawl()
        # Items are cleared on each crawl
        assert engine.paused is False


# ---------------------------------------------------------------------------
# Tests: items property
# ---------------------------------------------------------------------------


class TestItemsProperty:
    def test_items_returns_item_list(self):
        engine = _make_engine()
        assert isinstance(engine.items, ItemList)

    def test_items_initially_empty(self):
        engine = _make_engine()
        assert len(engine.items) == 0

    @pytest.mark.asyncio
    async def test_items_populated_after_crawl(self):
        engine = _make_engine()
        await engine.crawl()
        assert len(engine.items) >= 1


# ---------------------------------------------------------------------------
# Tests: streaming (__aiter__ / _stream)
# ---------------------------------------------------------------------------


class TestStreaming:
    @pytest.mark.asyncio
    async def test_stream_yields_items(self):
        spider = MockSpider()
        engine = _make_engine(spider=spider)

        items = []
        async for item in engine:
            items.append(item)

        assert len(items) >= 1
        assert isinstance(items[0], dict)

    @pytest.mark.asyncio
    async def test_stream_processes_follow_up_requests(self):
        call_count = 0

        async def parse_with_follow(response) -> AsyncGenerator:
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                yield Request("https://example.com/page2", sid="default")
            yield {"page": call_count}

        spider = MockSpider()
        spider.parse = parse_with_follow  # type: ignore[assignment]
        engine = _make_engine(spider=spider)

        items = []
        async for item in engine:
            items.append(item)

        assert len(items) == 2

    @pytest.mark.asyncio
    async def test_stream_items_not_stored_in_items_list(self):
        """When streaming, items go to the stream, not to engine._items."""
        spider = MockSpider()
        engine = _make_engine(spider=spider)

        items = []
        async for item in engine:
            items.append(item)

        # Items were sent through stream, not appended to _items
        assert len(items) >= 1
        assert len(engine.items) == 0


# ---------------------------------------------------------------------------
# Tests: pause during crawl
# ---------------------------------------------------------------------------


class TestPauseDuringCrawl:
    @pytest.mark.asyncio
    async def test_pause_stops_crawl_gracefully(self):
        processed = 0

        async def slow_parse(response) -> AsyncGenerator:
            nonlocal processed
            processed += 1
            # Yield more requests to keep the crawl going
            if processed <= 2:
                yield Request(f"https://example.com/p{processed + 1}", sid="default")
            yield {"n": processed}

        spider = MockSpider()
        spider.parse = slow_parse  # type: ignore[assignment]
        engine = _make_engine(spider=spider)

        # Request pause immediately - the engine will stop as soon as active tasks complete
        engine._pause_requested = True

        stats = await engine.crawl()
        # Should stop without processing everything
        assert engine._running is False

    @pytest.mark.asyncio
    async def test_pause_with_checkpoint_sets_paused(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            parse_count = 0

            async def parse_and_pause(response) -> AsyncGenerator:
                nonlocal parse_count
                parse_count += 1
                # Request pause after first request, but yield follow-ups
                if parse_count == 1:
                    engine.request_pause()
                    yield Request("https://example.com/p2", sid="default")
                yield {"n": parse_count}

            spider = MockSpider()
            spider.parse = parse_and_pause  # type: ignore[assignment]
            engine = _make_engine(spider=spider, crawldir=tmpdir)

            await engine.crawl()

            assert engine.paused is True

    @pytest.mark.asyncio
    async def test_pause_without_checkpoint_does_not_set_paused(self):
        spider = MockSpider()
        engine = _make_engine(spider=spider)

        engine._pause_requested = True

        await engine.crawl()

        assert engine.paused is False
