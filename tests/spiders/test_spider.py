"""Tests for the Spider class and related components."""

import logging
import tempfile
from pathlib import Path

import pytest

from scrapling.spiders.spider import Spider, SessionConfigurationError, LogCounterHandler, BLOCKED_CODES
from scrapling.spiders.request import Request
from scrapling.spiders.session import SessionManager
from scrapling.spiders.result import CrawlStats
from scrapling.core._types import Any, Dict, AsyncGenerator


class TestLogCounterHandler:
    """Test LogCounterHandler for tracking log counts."""

    def test_initial_counts_are_zero(self):
        """Test that handler starts with zero counts."""
        handler = LogCounterHandler()
        counts = handler.get_counts()

        assert counts["debug"] == 0
        assert counts["info"] == 0
        assert counts["warning"] == 0
        assert counts["error"] == 0
        assert counts["critical"] == 0

    def test_counts_debug_messages(self):
        """Test counting debug level messages."""
        handler = LogCounterHandler()
        record = logging.LogRecord(
            name="test",
            level=logging.DEBUG,
            pathname="",
            lineno=0,
            msg="test",
            args=(),
            exc_info=None,
        )

        handler.emit(record)
        handler.emit(record)

        assert handler.get_counts()["debug"] == 2

    def test_counts_info_messages(self):
        """Test counting info level messages."""
        handler = LogCounterHandler()
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="test",
            args=(),
            exc_info=None,
        )

        handler.emit(record)

        assert handler.get_counts()["info"] == 1

    def test_counts_warning_messages(self):
        """Test counting warning level messages."""
        handler = LogCounterHandler()
        record = logging.LogRecord(
            name="test",
            level=logging.WARNING,
            pathname="",
            lineno=0,
            msg="test",
            args=(),
            exc_info=None,
        )

        handler.emit(record)

        assert handler.get_counts()["warning"] == 1

    def test_counts_error_messages(self):
        """Test counting error level messages."""
        handler = LogCounterHandler()
        record = logging.LogRecord(
            name="test",
            level=logging.ERROR,
            pathname="",
            lineno=0,
            msg="test",
            args=(),
            exc_info=None,
        )

        handler.emit(record)

        assert handler.get_counts()["error"] == 1

    def test_counts_critical_messages(self):
        """Test counting critical level messages."""
        handler = LogCounterHandler()
        record = logging.LogRecord(
            name="test",
            level=logging.CRITICAL,
            pathname="",
            lineno=0,
            msg="test",
            args=(),
            exc_info=None,
        )

        handler.emit(record)

        assert handler.get_counts()["critical"] == 1

    def test_counts_multiple_levels(self):
        """Test counting messages at different levels."""
        handler = LogCounterHandler()

        levels = [
            logging.DEBUG,
            logging.DEBUG,
            logging.INFO,
            logging.WARNING,
            logging.ERROR,
            logging.ERROR,
            logging.ERROR,
            logging.CRITICAL,
        ]

        for level in levels:
            record = logging.LogRecord(
                name="test",
                level=level,
                pathname="",
                lineno=0,
                msg="test",
                args=(),
                exc_info=None,
            )
            handler.emit(record)

        counts = handler.get_counts()
        assert counts["debug"] == 2
        assert counts["info"] == 1
        assert counts["warning"] == 1
        assert counts["error"] == 3
        assert counts["critical"] == 1


class TestBlockedCodes:
    """Test BLOCKED_CODES constant."""

    def test_blocked_codes_contains_expected_values(self):
        """Test that BLOCKED_CODES contains expected HTTP status codes."""
        assert 401 in BLOCKED_CODES  # Unauthorized
        assert 403 in BLOCKED_CODES  # Forbidden
        assert 407 in BLOCKED_CODES  # Proxy Authentication Required
        assert 429 in BLOCKED_CODES  # Too Many Requests
        assert 444 in BLOCKED_CODES  # Connection Closed Without Response (nginx)
        assert 500 in BLOCKED_CODES  # Internal Server Error
        assert 502 in BLOCKED_CODES  # Bad Gateway
        assert 503 in BLOCKED_CODES  # Service Unavailable
        assert 504 in BLOCKED_CODES  # Gateway Timeout

    def test_blocked_codes_does_not_contain_success(self):
        """Test that success codes are not blocked."""
        assert 200 not in BLOCKED_CODES
        assert 201 not in BLOCKED_CODES
        assert 204 not in BLOCKED_CODES
        assert 301 not in BLOCKED_CODES
        assert 302 not in BLOCKED_CODES


class ConcreteSpider(Spider):
    """Concrete spider implementation for testing."""

    name = "test_spider"
    start_urls = ["https://example.com"]

    async def parse(self, response) -> AsyncGenerator[Dict[str, Any] | Request | None, None]:
        yield {"url": str(response)}


class TestSpiderInit:
    """Test Spider initialization."""

    def test_spider_requires_name(self):
        """Test that spider without name raises ValueError."""

        class NoNameSpider(Spider):
            async def parse(self, response) -> AsyncGenerator[Dict[str, Any] | Request | None, None]:
                yield None

        with pytest.raises(ValueError, match="must have a name"):
            NoNameSpider()

    def test_spider_initializes_logger(self):
        """Test that spider creates a logger."""
        spider = ConcreteSpider()

        assert spider.logger is not None
        assert spider.logger.name == "scrapling.spiders.test_spider"

    def test_spider_logger_has_log_counter(self):
        """Test that spider logger has log counter handler."""
        spider = ConcreteSpider()

        assert spider._log_counter is not None
        assert isinstance(spider._log_counter, LogCounterHandler)

    def test_spider_with_crawldir(self):
        """Test spider initialization with crawldir."""
        with tempfile.TemporaryDirectory() as tmpdir:
            spider = ConcreteSpider(crawldir=tmpdir)

            assert spider.crawldir == Path(tmpdir)

    def test_spider_without_crawldir(self):
        """Test spider initialization without crawldir."""
        spider = ConcreteSpider()

        assert spider.crawldir is None

    def test_spider_custom_interval(self):
        """Test spider with custom checkpoint interval."""
        spider = ConcreteSpider(interval=60.0)

        assert spider._interval == 60.0

    def test_spider_default_interval(self):
        """Test spider has default checkpoint interval."""
        spider = ConcreteSpider()

        assert spider._interval == 300.0

    def test_spider_repr(self):
        """Test spider string representation."""
        spider = ConcreteSpider()

        repr_str = repr(spider)

        assert "ConcreteSpider" in repr_str
        assert "test_spider" in repr_str


class TestSpiderClassAttributes:
    """Test Spider class attribute defaults."""

    def test_default_concurrent_requests(self):
        """Test default concurrent_requests is 16."""
        assert ConcreteSpider.concurrent_requests == 16

    def test_default_concurrent_requests_per_domain(self):
        """Test default concurrent_requests_per_domain is 0 (disabled)."""
        assert ConcreteSpider.concurrent_requests_per_domain == 0

    def test_default_download_delay(self):
        """Test default download_delay is 0."""
        assert ConcreteSpider.download_delay == 0.0

    def test_default_max_blocked_retries(self):
        """Test default max_blocked_retries is 3."""
        assert ConcreteSpider.max_blocked_retries == 3

    def test_default_logging_level(self):
        """Test default logging level is DEBUG."""
        assert ConcreteSpider.logging_level == logging.DEBUG

    def test_default_allowed_domains_empty(self):
        """Test default allowed_domains is empty set."""
        assert ConcreteSpider.allowed_domains == set()


class TestSpiderSessionConfiguration:
    """Test Spider session configuration."""

    def test_default_configure_sessions(self):
        """Test that default configure_sessions adds a session."""
        spider = ConcreteSpider()

        assert len(spider._session_manager) > 0

    def test_configure_sessions_error_raises_custom_exception(self):
        """Test that errors in configure_sessions raise SessionConfigurationError."""

        class BadSessionSpider(Spider):
            name = "bad_spider"

            def configure_sessions(self, manager: SessionManager) -> None:
                raise RuntimeError("Configuration failed!")

            async def parse(self, response) -> AsyncGenerator[Dict[str, Any] | Request | None, None]:
                yield None

        with pytest.raises(SessionConfigurationError, match="Configuration failed"):
            BadSessionSpider()

    def test_configure_sessions_no_sessions_raises(self):
        """Test that not adding any sessions raises SessionConfigurationError."""

        class NoSessionSpider(Spider):
            name = "no_session_spider"

            def configure_sessions(self, manager: SessionManager) -> None:
                pass  # Don't add any sessions

            async def parse(self, response) -> AsyncGenerator[Dict[str, Any] | Request | None, None]:
                yield None

        with pytest.raises(SessionConfigurationError, match="did not add any sessions"):
            NoSessionSpider()


class TestSpiderStartRequests:
    """Test Spider start_requests method."""

    @pytest.mark.asyncio
    async def test_start_requests_yields_from_start_urls(self):
        """Test that start_requests yields requests for start_urls."""

        class MultiUrlSpider(Spider):
            name = "multi_url"
            start_urls = [
                "https://example.com/1",
                "https://example.com/2",
                "https://example.com/3",
            ]

            async def parse(self, response) -> AsyncGenerator[Dict[str, Any] | Request | None, None]:
                yield None

        spider = MultiUrlSpider()
        requests = [r async for r in spider.start_requests()]

        assert len(requests) == 3
        assert requests[0].url == "https://example.com/1"
        assert requests[1].url == "https://example.com/2"
        assert requests[2].url == "https://example.com/3"

    @pytest.mark.asyncio
    async def test_start_requests_no_urls_raises(self):
        """Test that start_requests raises when no start_urls."""

        class NoUrlSpider(Spider):
            name = "no_url"
            start_urls = []

            async def parse(self, response) -> AsyncGenerator[Dict[str, Any] | Request | None, None]:
                yield None

        spider = NoUrlSpider()

        with pytest.raises(RuntimeError, match="no starting point"):
            async for _ in spider.start_requests():
                pass

    @pytest.mark.asyncio
    async def test_start_requests_uses_default_session(self):
        """Test that start_requests uses default session ID."""
        spider = ConcreteSpider()
        requests = [r async for r in spider.start_requests()]

        # Should use the default session from session manager
        default_sid = spider._session_manager.default_session_id
        assert requests[0].sid == default_sid


class TestSpiderHooks:
    """Test Spider lifecycle hooks."""

    @pytest.mark.asyncio
    async def test_on_start_default(self):
        """Test default on_start doesn't raise."""
        spider = ConcreteSpider()

        # Should not raise
        await spider.on_start(resuming=False)
        await spider.on_start(resuming=True)

    @pytest.mark.asyncio
    async def test_on_close_default(self):
        """Test default on_close doesn't raise."""
        spider = ConcreteSpider()

        # Should not raise
        await spider.on_close()

    @pytest.mark.asyncio
    async def test_on_error_default(self):
        """Test default on_error logs the error."""
        spider = ConcreteSpider()
        request = Request("https://example.com")
        error = ValueError("test error")

        # Should not raise
        await spider.on_error(request, error)

    @pytest.mark.asyncio
    async def test_on_scraped_item_default_returns_item(self):
        """Test default on_scraped_item returns the item unchanged."""
        spider = ConcreteSpider()
        item = {"key": "value", "nested": {"a": 1}}

        result = await spider.on_scraped_item(item)

        assert result == item

    @pytest.mark.asyncio
    async def test_is_blocked_default_checks_status_codes(self):
        """Test default is_blocked checks blocked status codes."""

        class MockResponse:
            def __init__(self, status: int):
                self.status = status

        spider = ConcreteSpider()

        # Test blocked codes
        assert await spider.is_blocked(MockResponse(403)) is True
        assert await spider.is_blocked(MockResponse(429)) is True
        assert await spider.is_blocked(MockResponse(503)) is True

        # Test non-blocked codes
        assert await spider.is_blocked(MockResponse(200)) is False
        assert await spider.is_blocked(MockResponse(404)) is False

    @pytest.mark.asyncio
    async def test_retry_blocked_request_default_returns_request(self):
        """Test default retry_blocked_request returns the request unchanged."""

        class MockResponse:
            status = 429

        spider = ConcreteSpider()
        request = Request("https://example.com", priority=5)

        result = await spider.retry_blocked_request(request, MockResponse())

        assert result is request


class TestSpiderPause:
    """Test Spider pause functionality."""

    def test_pause_without_crawldir_raises(self):
        """Test that pause without crawldir raises RuntimeError."""
        spider = ConcreteSpider()

        with pytest.raises(RuntimeError, match="Cannot pause without crawldir"):
            spider.pause()

    def test_pause_without_engine_raises(self):
        """Test that pause without active engine raises RuntimeError."""
        with tempfile.TemporaryDirectory() as tmpdir:
            spider = ConcreteSpider(crawldir=tmpdir)

            with pytest.raises(RuntimeError, match="no crawl engine started"):
                spider.pause()


class TestSpiderStats:
    """Test Spider stats property."""

    def test_stats_without_engine_raises(self):
        """Test that accessing stats without active crawl raises."""
        spider = ConcreteSpider()

        with pytest.raises(RuntimeError, match="No active crawl"):
            _ = spider.stats


class TestSpiderCustomization:
    """Test Spider customization patterns."""

    def test_custom_concurrent_requests(self):
        """Test spider with custom concurrent_requests."""

        class CustomSpider(Spider):
            name = "custom"
            concurrent_requests = 32
            start_urls = ["https://example.com"]

            async def parse(self, response) -> AsyncGenerator[Dict[str, Any] | Request | None, None]:
                yield None

        spider = CustomSpider()
        assert spider.concurrent_requests == 32

    def test_custom_allowed_domains(self):
        """Test spider with allowed_domains."""

        class DomainSpider(Spider):
            name = "domain_spider"
            start_urls = ["https://example.com"]
            allowed_domains = {"example.com", "api.example.com"}

            async def parse(self, response) -> AsyncGenerator[Dict[str, Any] | Request | None, None]:
                yield None

        spider = DomainSpider()
        assert "example.com" in spider.allowed_domains
        assert "api.example.com" in spider.allowed_domains

    def test_custom_download_delay(self):
        """Test spider with download delay."""

        class SlowSpider(Spider):
            name = "slow"
            download_delay = 1.5
            start_urls = ["https://example.com"]

            async def parse(self, response) -> AsyncGenerator[Dict[str, Any] | Request | None, None]:
                yield None

        spider = SlowSpider()
        assert spider.download_delay == 1.5


class TestSpiderLogging:
    """Test Spider logging configuration."""

    def test_custom_logging_level(self):
        """Test spider with custom logging level."""

        class QuietSpider(Spider):
            name = "quiet"
            logging_level = logging.WARNING
            start_urls = ["https://example.com"]

            async def parse(self, response) -> AsyncGenerator[Dict[str, Any] | Request | None, None]:
                yield None

        spider = QuietSpider()
        assert spider.logger.level == logging.WARNING

    def test_log_file_creates_handler(self):
        """Test spider with log file creates file handler."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_path = Path(tmpdir) / "spider.log"

            class FileLogSpider(Spider):
                name = "file_log"
                log_file = str(log_path)
                start_urls = ["https://example.com"]

                async def parse(self, response) -> AsyncGenerator[Dict[str, Any] | Request | None, None]:
                    yield None

            spider = FileLogSpider()

            # Should have a file handler
            file_handlers = [
                h for h in spider.logger.handlers if isinstance(h, logging.FileHandler)
            ]
            assert len(file_handlers) == 1

            # Clean up
            for h in file_handlers:
                h.close()

    def test_logger_does_not_propagate(self):
        """Test that spider logger does not propagate to parent."""
        spider = ConcreteSpider()

        assert spider.logger.propagate is False


class TestSessionConfigurationError:
    """Test SessionConfigurationError exception."""

    def test_exception_message(self):
        """Test that exception preserves message."""
        error = SessionConfigurationError("Custom error message")

        assert str(error) == "Custom error message"

    def test_exception_is_exception(self):
        """Test that it's a proper exception."""
        error = SessionConfigurationError("test")

        assert isinstance(error, Exception)
