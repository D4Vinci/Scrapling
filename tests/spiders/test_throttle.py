"""Tests for the AutoThrottle algorithm and its integration with the crawling engine."""

import anyio
import pytest

from scrapling.spiders.engine import CrawlerEngine
from scrapling.spiders.request import Request
from scrapling.spiders.session import SessionManager
from scrapling.spiders.throttle import AutoThrottle, parse_retry_after
from scrapling.engines.toolbelt.custom import Response
from scrapling.core._types import Any, Dict, Set, AsyncGenerator


def _make_response(url: str = "https://example.com", status: int = 200, retry_after: str = "") -> Response:
    headers = {"content-type": "text/html"}
    if retry_after:
        headers["Retry-After"] = retry_after

    return Response(
        url=url,
        content=b"<html>hello</html>",
        status=status,
        reason="OK",
        encoding="utf-8",
        cookies={},
        headers=headers,
        request_headers={"user-agent": "test"},
        method="GET",
    )


class TestAutoThrottleValidation:
    """Test the constructor guards"""

    def test_invalid_target_concurrency(self):
        for value in (0, -1.0):
            with pytest.raises(ValueError, match="target_concurrency"):
                AutoThrottle(target_concurrency=value)

    def test_max_delay_lower_than_start_delay(self):
        with pytest.raises(ValueError, match="max_delay"):
            AutoThrottle(start_delay=10.0, max_delay=5.0)


class TestAutoThrottleMath:
    """Test the delay calculation itself"""

    def test_starts_at_start_delay(self):
        throttle = AutoThrottle(start_delay=5.0)

        assert throttle.delay_for("example.com") == 5.0

    def test_floor_raises_the_starting_delay(self):
        throttle = AutoThrottle(start_delay=1.0)

        assert throttle.delay_for("example.com", floor=3.0) == 3.0

    def test_start_delay_is_capped_by_max_delay(self):
        throttle = AutoThrottle(start_delay=5.0, max_delay=20.0)

        assert throttle.delay_for("example.com", floor=100.0) == 20.0

    def test_converges_toward_latency_over_target_concurrency(self):
        throttle = AutoThrottle(start_delay=5.0)

        for _ in range(20):
            delay = throttle.record("example.com", latency=2.0, ok=True)

        assert delay == pytest.approx(2.0, abs=0.01)

    def test_target_concurrency_divides_the_latency(self):
        throttle = AutoThrottle(start_delay=5.0, target_concurrency=4.0)

        for _ in range(20):
            delay = throttle.record("example.com", latency=2.0, ok=True)

        assert delay == pytest.approx(0.5, abs=0.01)

    def test_latency_spike_jumps_straight_to_target(self):
        """A slow response must not be averaged down, it takes effect immediately"""
        throttle = AutoThrottle(start_delay=1.0)

        assert throttle.record("example.com", latency=10.0, ok=True) == 10.0

    def test_non_ok_response_never_decreases_the_delay(self):
        throttle = AutoThrottle(start_delay=5.0, block_backoff=False)

        assert throttle.record("example.com", latency=0.1, ok=False) == 5.0

    def test_non_ok_response_can_still_increase_the_delay(self):
        throttle = AutoThrottle(start_delay=1.0, block_backoff=False)

        assert throttle.record("example.com", latency=8.0, ok=False) == 8.0

    def test_delay_is_clamped_between_floor_and_max(self):
        throttle = AutoThrottle(start_delay=1.0, max_delay=3.0)

        assert throttle.record("example.com", latency=100.0, ok=True) == 3.0
        assert throttle.record("other.com", latency=0.001, ok=True, floor=2.0) == 2.0

    def test_domains_are_throttled_independently(self):
        throttle = AutoThrottle(start_delay=1.0)

        throttle.record("slow.com", latency=9.0, ok=True)
        throttle.record("fast.com", latency=0.5, ok=True)

        assert throttle.delays["slow.com"] == 9.0
        assert throttle.delays["fast.com"] < 1.0

    def test_reset_clears_every_domain(self):
        throttle = AutoThrottle(start_delay=1.0)
        throttle.record("example.com", latency=9.0, ok=True)

        throttle.reset()

        assert throttle.delays == {}
        assert throttle.delay_for("example.com") == 1.0


class TestBlockBackoff:
    """Test the doubling that kicks in when a website blocks us"""

    def test_each_block_doubles_the_delay(self):
        """Blocks are often served fast, so latency alone would never slow the spider down"""
        throttle = AutoThrottle(start_delay=1.0, max_delay=60.0)

        assert [throttle.record("example.com", latency=0.05, ok=False) for _ in range(5)] == [2.0, 4.0, 8.0, 16.0, 32.0]

    def test_backoff_stops_at_max_delay(self):
        throttle = AutoThrottle(start_delay=1.0, max_delay=5.0)

        for _ in range(10):
            delay = throttle.record("example.com", latency=0.05, ok=False)

        assert delay == 5.0

    def test_healthy_responses_bring_the_delay_back_down(self):
        """Once the website stops blocking, the normal averaging has to recover"""
        throttle = AutoThrottle(start_delay=1.0, max_delay=60.0)
        for _ in range(4):
            throttle.record("example.com", latency=0.05, ok=False)
        assert throttle.delays["example.com"] == 16.0

        for _ in range(20):
            delay = throttle.record("example.com", latency=0.5, ok=True)

        assert delay == pytest.approx(0.5, abs=0.01)

    def test_disabled_backoff_only_freezes_the_delay(self):
        throttle = AutoThrottle(start_delay=1.0, block_backoff=False)

        assert [throttle.record("example.com", latency=0.05, ok=False) for _ in range(3)] == [1.0, 1.0, 1.0]

    def test_retry_after_wins_over_the_doubling(self):
        throttle = AutoThrottle(start_delay=1.0, max_delay=60.0)

        assert throttle.record("example.com", latency=0.05, ok=False, retry_after=30.0) == 30.0

    def test_retry_after_is_capped_by_max_delay(self):
        throttle = AutoThrottle(start_delay=1.0, max_delay=60.0)

        assert throttle.record("example.com", latency=0.05, ok=False, retry_after=3600.0) == 60.0

    def test_retry_after_never_speeds_the_spider_up(self):
        """A tiny or zero Retry-After on a block must not undo the backoff"""
        throttle = AutoThrottle(start_delay=10.0, max_delay=60.0)

        assert throttle.record("example.com", latency=0.05, ok=False, retry_after=0.0) == 10.0

    def test_retry_after_is_ignored_when_backoff_is_disabled(self):
        throttle = AutoThrottle(start_delay=1.0, block_backoff=False)

        assert throttle.record("example.com", latency=0.05, ok=False, retry_after=30.0) == 1.0


class TestParseRetryAfter:
    """Test reading the `Retry-After` header"""

    def test_missing_header(self):
        assert parse_retry_after({}) is None
        assert parse_retry_after({"Content-Type": "text/html"}) is None

    def test_seconds(self):
        assert parse_retry_after({"Retry-After": "120"}) == 120.0

    def test_header_name_is_case_insensitive(self):
        """Engines don't agree on the casing of header names"""
        assert parse_retry_after({"retry-after": "120"}) == 120.0
        assert parse_retry_after({"RETRY-AFTER": " 120 "}) == 120.0

    def test_http_date(self):
        from email.utils import format_datetime
        from datetime import datetime, timedelta, timezone

        future = datetime.now(timezone.utc) + timedelta(seconds=90)

        assert parse_retry_after({"Retry-After": format_datetime(future)}) == pytest.approx(90.0, abs=5.0)

    def test_past_http_date_is_zero(self):
        assert parse_retry_after({"Retry-After": "Wed, 21 Oct 2015 07:28:00 GMT"}) == 0.0

    def test_negative_seconds_are_clamped(self):
        assert parse_retry_after({"Retry-After": "-5"}) == 0.0

    def test_garbage_is_ignored(self):
        for value in ("soon", "", "   ", "12 seconds"):
            assert parse_retry_after({"Retry-After": value}) is None


# ---------------------------------------------------------------------------
# Engine integration
# ---------------------------------------------------------------------------


class MockSession:
    def __init__(self, latency: float = 0.05, status: int = 200, retry_after: str = ""):
        self._is_alive = False
        self.latency = latency
        self.status = status
        self.retry_after = retry_after
        self.fetch_count = 0

    async def __aenter__(self):
        self._is_alive = True
        return self

    async def __aexit__(self, *args):
        self._is_alive = False

    async def fetch(self, url: str, **kwargs):
        self.fetch_count += 1
        await anyio.sleep(self.latency)
        return _make_response(url=url, status=self.status, retry_after=self.retry_after)


class _LogCounterStub:
    def get_counts(self) -> Dict[str, int]:
        return {"debug": 0, "info": 0, "warning": 0, "error": 0, "critical": 0}


class MockSpider:
    def __init__(self, enabled: bool = True, start_delay: float = 0.2, blocked: bool = False, urls: int = 6):
        self.concurrent_requests = 4
        self.concurrent_requests_per_domain = 1
        self.download_delay = 0.0
        self.max_blocked_retries = 0
        self.autothrottle_enabled = enabled
        self.autothrottle_start_delay = start_delay
        self.autothrottle_max_delay = 1.0
        self.autothrottle_target_concurrency = None
        self.autothrottle_block_backoff = True
        self.allowed_domains: Set[str] = set()
        self.fp_include_kwargs = False
        self.fp_include_headers = False
        self.fp_keep_fragments = False
        self.robots_txt_obey = False
        self.development_mode = False
        self.development_cache_dir = None
        self.start_urls: list[str] = []
        self.name = "test_throttle_spider"
        self._log_counter = _LogCounterStub()
        self._blocked = blocked
        self._urls = urls

    async def parse(self, response) -> AsyncGenerator[Dict[str, Any] | Request | None, None]:
        yield {"url": str(response)}

    async def on_start(self, resuming: bool = False) -> None:
        pass

    async def on_close(self) -> None:
        pass

    async def on_error(self, request: Request, error: Exception) -> None:
        pass

    async def on_scraped_item(self, item: Dict[str, Any]) -> Dict[str, Any] | None:
        return item

    async def is_blocked(self, response) -> bool:
        return self._blocked

    async def retry_blocked_request(self, request: Request, response) -> Request:
        return request

    async def start_requests(self) -> AsyncGenerator[Request, None]:
        for index in range(self._urls):
            yield Request(f"https://example.com/page{index}", sid="default")


async def _crawl(spider: MockSpider, session: MockSession):
    manager = SessionManager()
    manager.add("default", session)
    engine = CrawlerEngine(spider, manager)
    return engine, await engine.crawl()


class TestAutoThrottleIntegration:
    """Test how the engine drives the throttle"""

    @pytest.mark.anyio
    async def test_explicit_target_concurrency_wins(self):
        """The order is autothrottle_target_concurrency, then concurrent_requests_per_domain, then 1"""
        spider = MockSpider()
        spider.autothrottle_target_concurrency = 2.5
        spider.concurrent_requests_per_domain = 4
        engine, _ = await _crawl(spider, MockSession(latency=0.01))

        assert engine._autothrottle.target_concurrency == 2.5

    @pytest.mark.anyio
    async def test_target_concurrency_falls_back_to_the_per_domain_limit(self):
        spider = MockSpider()
        spider.autothrottle_target_concurrency = None
        spider.concurrent_requests_per_domain = 4
        engine, _ = await _crawl(spider, MockSession(latency=0.01))

        assert engine._autothrottle.target_concurrency == 4

    @pytest.mark.anyio
    async def test_target_concurrency_falls_back_to_one(self):
        spider = MockSpider()
        spider.autothrottle_target_concurrency = None
        spider.concurrent_requests_per_domain = 0
        engine, _ = await _crawl(spider, MockSession(latency=0.01))

        assert engine._autothrottle.target_concurrency == 1.0

    @pytest.mark.anyio
    async def test_disabled_by_default_leaves_no_state(self):
        engine, stats = await _crawl(MockSpider(enabled=False), MockSession())

        assert engine._autothrottle is None
        assert stats.autothrottle_enabled is False
        assert stats.autothrottle_delays == {}

    @pytest.mark.anyio
    async def test_fast_responses_speed_the_crawl_up(self):
        """A server answering in ~0.05s must pull the delay down from the 0.2s start"""
        spider = MockSpider(start_delay=0.2)
        engine, stats = await _crawl(spider, MockSession(latency=0.05))

        assert stats.autothrottle_enabled is True
        assert list(stats.autothrottle_delays) == ["example.com"]
        assert stats.autothrottle_delays["example.com"] < 0.2
        assert stats.autothrottle_delays["example.com"] >= 0.05
        assert stats.autothrottle_delays == engine._autothrottle.delays

    @pytest.mark.anyio
    async def test_blocked_responses_slow_the_crawl_down(self):
        """Content-based blocks come back as fast 200s, so only the backoff can react to them"""
        spider = MockSpider(start_delay=0.05, blocked=True, urls=4)
        spider.autothrottle_max_delay = 0.4
        engine, stats = await _crawl(spider, MockSession(latency=0.01))

        assert stats.blocked_requests_count > 0
        assert stats.autothrottle_delays["example.com"] > 0.05

    @pytest.mark.anyio
    async def test_error_responses_slow_the_crawl_down(self):
        spider = MockSpider(start_delay=0.05, urls=4)
        spider.autothrottle_max_delay = 0.4
        engine, stats = await _crawl(spider, MockSession(latency=0.01, status=503))

        assert stats.autothrottle_delays["example.com"] > 0.05

    @pytest.mark.anyio
    async def test_backoff_can_be_turned_off(self):
        spider = MockSpider(start_delay=0.05, blocked=True, urls=4)
        spider.autothrottle_block_backoff = False
        engine, stats = await _crawl(spider, MockSession(latency=0.01))

        assert stats.autothrottle_delays["example.com"] == 0.05

    @pytest.mark.anyio
    async def test_retry_after_header_is_honored(self):
        """A rate-limited response carrying `Retry-After` sets the delay directly"""
        spider = MockSpider(start_delay=0.05, urls=2)
        spider.autothrottle_max_delay = 5.0
        engine, stats = await _crawl(spider, MockSession(latency=0.01, status=429, retry_after="3"))

        assert stats.autothrottle_delays["example.com"] == 3.0

    @pytest.mark.anyio
    async def test_delays_are_included_in_the_stats_dump(self):
        _, stats = await _crawl(MockSpider(start_delay=0.2), MockSession(latency=0.05))
        dumped = stats.to_dict()

        assert dumped["autothrottle_enabled"] is True
        assert dumped["autothrottle_delays"]["example.com"] == pytest.approx(
            stats.autothrottle_delays["example.com"], abs=0.01
        )
