import logging
from pathlib import Path
from abc import ABC

import anyio

from scrapling.spiders.request import Request
from scrapling.spiders.result import CrawlResult
from scrapling.spiders.engine import CrawlerEngine
from scrapling.spiders.session import SessionManager
from scrapling.core.utils import set_logger, reset_logger
from scrapling.core._types import Set, Any, Dict, Optional, TYPE_CHECKING, AsyncGenerator

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

    # Logging settings
    logging_level: int = logging.DEBUG
    log_file: Optional[str] = None

    def __init__(self):
        if self.name is None:
            raise ValueError(f"{self.__class__.__name__} must have a name.")

        self.logger = logging.getLogger(f"scrapling.spiders.{self.name}")
        self.logger.setLevel(self.logging_level)
        self.logger.handlers.clear()
        self.logger.propagate = False  # Don't propagate to parent 'scrapling' logger

        formatter = logging.Formatter(
            fmt=f"[%(asctime)s]:({self.name}) %(levelname)s: %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
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

    async def parse(self, response: "Response") -> AsyncGenerator[Dict[str, Any] | Request | None, None]:
        """Default callback for processing responses"""
        raise NotImplementedError(f"{self.__class__.__name__} must implement parse() method")
        yield  # Make this a generator

    async def on_start(self) -> None:
        """Called before crawling starts. Override for setup logic."""
        self.logger.debug("Starting spider")

    async def on_close(self) -> None:
        """Called after crawling finishes. Override for cleanup logic."""
        self.logger.debug("Spider closed")

    async def on_error(self, request: Request, error: Exception) -> None:
        """
        Handle request errors for all spider requests.

        Override for custom error handling.
        """
        self.logger.error(error, exc_info=error)

    @staticmethod
    async def is_blocked(response: "Response") -> bool:
        """Check if the response is blocked."""
        # TODO
        if response.status in BLOCKED_CODES:
            return True
        return False

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

    async def __run(self) -> CrawlResult:
        token = set_logger(self.logger)
        try:
            engine = CrawlerEngine(self, session_manager=self._session_manager)
            stats = await engine.crawl()
            return CrawlResult(stats=stats, items=engine.items)
        finally:
            reset_logger(token)
            # Close any file handlers to release file resources.
            if self.log_file:
                for handler in self.logger.handlers:
                    if isinstance(handler, logging.FileHandler):
                        handler.close()

    def start(self, backend_options: Dict[str, Any] | None = None) -> CrawlResult:
        """Run the spider and return results.

        This is the main entry point for running a spider.
        Handles async execution internally via anyio.

        :param backend_options: Asyncio backend options to be used with `anyio.run`
        """
        backend_options = backend_options or {}
        # By default use the faster uvloop/winloop event loop implementation, if available
        backend_options.update({"use_uvloop": True})
        return anyio.run(self.__run, backend="asyncio", backend_options=backend_options)
