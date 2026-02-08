import signal
import logging
from pathlib import Path
from abc import ABC, abstractmethod

import anyio
from anyio import Path as AsyncPath

from scrapling.spiders.request import Request
from scrapling.spiders.engine import CrawlerEngine
from scrapling.spiders.session import SessionManager
from scrapling.core.utils import set_logger, reset_logger
from scrapling.spiders.result import CrawlResult, CrawlStats
from scrapling.core._types import Set, Any, Dict, Optional, Union, TYPE_CHECKING, AsyncGenerator

BLOCKED_CODES = {401, 403, 407, 429, 444, 500, 502, 503, 504}
if TYPE_CHECKING:
    from scrapling.engines.toolbelt.custom import Response


class LogCounterHandler(logging.Handler):
    """A logging handler that counts log messages by level."""

    def __init__(self):
        super().__init__()
        self.counts = {
            logging.DEBUG: 0,
            logging.INFO: 0,
            logging.WARNING: 0,
            logging.ERROR: 0,
            logging.CRITICAL: 0,
        }

    def emit(self, record: logging.LogRecord) -> None:
        level = record.levelno
        # Map to the closest standard level
        if level >= logging.CRITICAL:
            self.counts[logging.CRITICAL] += 1
        elif level >= logging.ERROR:
            self.counts[logging.ERROR] += 1
        elif level >= logging.WARNING:
            self.counts[logging.WARNING] += 1
        elif level >= logging.INFO:
            self.counts[logging.INFO] += 1
        else:
            self.counts[logging.DEBUG] += 1

    def get_counts(self) -> Dict[str, int]:
        """Return counts as a dictionary with string keys."""
        return {
            "debug": self.counts[logging.DEBUG],
            "info": self.counts[logging.INFO],
            "warning": self.counts[logging.WARNING],
            "error": self.counts[logging.ERROR],
            "critical": self.counts[logging.CRITICAL],
        }


class SessionConfigurationError(Exception):
    """Raised when session configuration fails."""

    pass


class Spider(ABC):
    """An abstract base class for creating web spiders.

    Check the documentation website for more information.
    """

    name: Optional[str] = None
    start_urls: list[str] = []
    allowed_domains: Set[str] = set()

    # Concurrency settings
    concurrent_requests: int = 16
    concurrent_requests_per_domain: int = 0
    download_delay: float = 0.0
    max_blocked_retries: int = 3

    # Fingerprint adjustments
    fp_include_kwargs = False
    fp_keep_fragments = False
    fp_include_headers = False

    # Logging settings
    logging_level: int = logging.DEBUG
    logging_format: str = "[%(asctime)s]:({spider_name}) %(levelname)s: %(message)s"
    logging_date_format: str = "%Y-%m-%d %H:%M:%S"
    log_file: Optional[str] = None

    def __init__(self, crawldir: Optional[Union[str, Path, AsyncPath]] = None, interval: float = 300.0):
        """Initialize the spider.

        :param crawldir: Directory for checkpoint files. If provided, enables pause/resume.
        :param interval: Seconds between periodic checkpoint saves (default 5 minutes).
        """
        if self.name is None:
            raise ValueError(f"{self.__class__.__name__} must have a name.")

        self.logger = logging.getLogger(f"scrapling.spiders.{self.name}")
        self.logger.setLevel(self.logging_level)
        self.logger.handlers.clear()
        self.logger.propagate = False  # Don't propagate to parent 'scrapling' logger

        formatter = logging.Formatter(
            fmt=self.logging_format.format(spider_name=self.name), datefmt=self.logging_date_format
        )

        # Add a log counter handler to track log counts by level
        self._log_counter = LogCounterHandler()
        self.logger.addHandler(self._log_counter)

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)

        if self.log_file:
            Path(self.log_file).parent.mkdir(parents=True, exist_ok=True)
            file_handler = logging.FileHandler(self.log_file)
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)

        self.crawldir: Optional[Path] = Path(crawldir) if crawldir else None
        self._interval = interval
        self._engine: Optional[CrawlerEngine] = None
        self._original_sigint_handler: Any = None

        self._session_manager = SessionManager()

        try:
            self.configure_sessions(self._session_manager)
        except Exception as e:
            raise SessionConfigurationError(f"Error in {self.__class__.__name__}.configure_sessions(): {e}") from e

        if len(self._session_manager) == 0:
            raise SessionConfigurationError(f"{self.__class__.__name__}.configure_sessions() did not add any sessions")

        self.logger.info("Spider initialized")

    async def start_requests(self) -> AsyncGenerator[Request, None]:
        """Generate initial requests to start the crawl.

        By default, this generates Request objects for each URL in `start_urls`
        using the session manager's default session and `parse()` as callback.

        Override this method for more control over initial requests
        (e.g., to add custom headers, use different callbacks, etc.)
        """
        if not self.start_urls:
            raise RuntimeError(
                "Spider has no starting point, either set `start_urls` or override `start_requests` function."
            )

        for url in self.start_urls:
            yield Request(url, sid=self._session_manager.default_session_id)

    @abstractmethod
    async def parse(self, response: "Response") -> AsyncGenerator[Dict[str, Any] | Request | None, None]:
        """Default callback for processing responses"""
        raise NotImplementedError(f"{self.__class__.__name__} must implement parse() method")
        yield  # Make this a generator for type checkers

    async def on_start(self, resuming: bool = False) -> None:
        """Called before crawling starts. Override for setup logic.

        :param resuming: It's enabled if the spider is resuming from a checkpoint, left for the user to use.
        """
        if resuming:
            self.logger.debug("Resuming spider from checkpoint")
        else:
            self.logger.debug("Starting spider")

    async def on_close(self) -> None:
        """Called after crawling finishes. Override for cleanup logic."""
        self.logger.debug("Spider closed")

    async def on_error(self, request: Request, error: Exception) -> None:
        """
        Handle request errors for all spider requests.

        Override for custom error handling.
        """
        pass

    async def on_scraped_item(self, item: Dict[str, Any]) -> Dict[str, Any] | None:
        """A hook to be overridden by users to do some processing on scraped items, return `None` to drop the item silently."""
        return item

    async def is_blocked(self, response: "Response") -> bool:
        """Check if the response is blocked. Users should override this for custom detection logic."""
        if response.status in BLOCKED_CODES:
            return True
        return False

    async def retry_blocked_request(self, request: Request, response: "Response") -> Request:
        """Users should override this to prepare the blocked request before retrying, if needed."""
        return request

    def __repr__(self) -> str:
        """String representation of the spider."""
        return f"<{self.__class__.__name__} '{self.name}'>"

    def configure_sessions(self, manager: SessionManager) -> None:
        """Configure sessions for this spider.

        Override this method to add custom sessions.
        The default implementation creates a FetcherSession session.

        The first session added becomes the default for `start_requests()` unless specified otherwise.

        :param manager: SessionManager to configure
        """
        from scrapling.fetchers import FetcherSession

        manager.add("default", FetcherSession())

    def pause(self):
        """Request graceful shutdown of the crawling process."""
        if self._engine:
            self._engine.request_pause()
        else:
            raise RuntimeError("No active crawl to stop")

    def _setup_signal_handler(self) -> None:
        """Set up SIGINT handler for graceful pause."""

        def handler(_signum: int, _frame: Any) -> None:
            if self._engine:
                self._engine.request_pause()
            else:
                # No engine yet, just raise KeyboardInterrupt
                raise KeyboardInterrupt

        try:
            self._original_sigint_handler = signal.signal(signal.SIGINT, handler)
        except ValueError:
            self._original_sigint_handler = None

    def _restore_signal_handler(self) -> None:
        """Restore original SIGINT handler."""
        if self._original_sigint_handler is not None:
            try:
                signal.signal(signal.SIGINT, self._original_sigint_handler)
            except ValueError:
                pass

    async def __run(self) -> CrawlResult:
        token = set_logger(self.logger)
        try:
            self._engine = CrawlerEngine(self, self._session_manager, self.crawldir, self._interval)
            stats = await self._engine.crawl()
            paused = self._engine.paused
            return CrawlResult(stats=stats, items=self._engine.items, paused=paused)
        finally:
            self._engine = None
            reset_logger(token)
            # Close any file handlers to release file resources.
            if self.log_file:
                for handler in self.logger.handlers:
                    if isinstance(handler, logging.FileHandler):
                        handler.close()

    def start(self, use_uvloop: bool = False, **backend_options: Any) -> CrawlResult:
        """Run the spider and return results.

        This is the main entry point for running a spider.
        Handles async execution internally via anyio.

        Pressing Ctrl+C will initiate graceful shutdown (waits for active tasks to complete).
        Pressing Ctrl+C a second time will force immediate stop.

        If crawldir is set, a checkpoint will also be saved on graceful shutdown,
        allowing you to resume the crawl later by running the spider again.

        :param use_uvloop: Whether to use the faster uvloop/winloop event loop implementation, if available.
        :param backend_options: Asyncio backend options to be used with `anyio.run`
        """
        backend_options = backend_options or {}
        if use_uvloop:
            backend_options.update({"use_uvloop": True})

        # Set up SIGINT handler for graceful shutdown
        self._setup_signal_handler()
        try:
            return anyio.run(self.__run, backend="asyncio", backend_options=backend_options)
        finally:
            self._restore_signal_handler()

    async def stream(self) -> AsyncGenerator[Dict[str, Any], None]:
        """Stream items as they're scraped. Ideal for long-running spiders or building applications on top of the spiders.

        Must be called from an async context. Yields items one by one as they are scraped.
        Access `spider.stats` during iteration for real-time statistics.

        Note: SIGINT handling for pause/resume is not available in stream mode.
        """
        token = set_logger(self.logger)
        try:
            self._engine = CrawlerEngine(self, self._session_manager, self.crawldir, self._interval)
            async for item in self._engine:
                yield item
        finally:
            self._engine = None
            reset_logger(token)
            if self.log_file:
                for handler in self.logger.handlers:
                    if isinstance(handler, logging.FileHandler):
                        handler.close()

    @property
    def stats(self) -> CrawlStats:
        """Access current crawl stats (works during streaming)."""
        if self._engine:
            return self._engine.stats
        raise RuntimeError("No active crawl. Use this property inside `async for item in spider.stream():`")
