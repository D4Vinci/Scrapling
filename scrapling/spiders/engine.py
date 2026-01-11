import json

import anyio
from anyio import create_task_group, CapacityLimiter

from scrapling.core.utils import log
from scrapling.spiders.request import Request
from scrapling.spiders.result import CrawlStats
from scrapling.spiders.scheduler import Scheduler
from scrapling.spiders.session import SessionManager
from scrapling.core._types import Dict, TYPE_CHECKING, Any

if TYPE_CHECKING:
    from scrapling.spiders.spider import Spider


def _dump(obj: Dict) -> str:
    return json.dumps(obj, indent=4)


class CrawlerEngine:
    """Orchestrates the crawling process."""

    def __init__(self, spider: "Spider", session_manager: SessionManager, scheduler: Scheduler | None = None):
        self.spider = spider
        self.session_manager = session_manager
        self.scheduler = scheduler or Scheduler()
        self.stats = CrawlStats()

        self._global_limiter = CapacityLimiter(spider.concurrent_requests)
        self._domain_limiters: dict[str, CapacityLimiter] = {}
        self._allowed_domains: set[str] = spider.allowed_domains or set()

        self._active_tasks: int = 0
        self._running: bool = False
        self._items: list[dict[str, Any]] = []

    def _is_domain_allowed(self, request: Request) -> bool:
        """Check if the request's domain is in allowed_domains."""
        if not self._allowed_domains:
            return True

        domain = request.domain
        for allowed in self._allowed_domains:
            if domain == allowed or domain.endswith("." + allowed):
                return True
        return False

    def _rate_limiter(self, domain: str) -> CapacityLimiter:
        """Get or create a per-domain concurrency limiter if enabled, otherwise use the global limiter."""
        if self.spider.concurrent_requests_per_domain:
            if domain not in self._domain_limiters:
                self._domain_limiters[domain] = CapacityLimiter(self.spider.concurrent_requests_per_domain)
            return self._domain_limiters[domain]
        return self._global_limiter

    async def _process_request(self, request: Request) -> None:
        """Download and process a single request."""
        async with self._rate_limiter(request.domain):
            if self.spider.download_delay:
                await anyio.sleep(self.spider.download_delay)

            if request._session_kwargs.get("proxy"):
                self.stats.proxies.append(request._session_kwargs["proxy"])
            if request._session_kwargs.get("proxies"):
                self.stats.proxies.append(dict(request._session_kwargs["proxies"]))
            try:
                response = await self.session_manager.fetch(request)
                self.stats.increment_requests_count(request.sid)
                self.stats.increment_response_bytes(request.domain, len(response.body))
                self.stats.increment_status(response.status)

            except Exception as e:
                self.stats.failed_requests_count += 1
                await self.spider.on_error(request, e)
                return

        # Process response through callback
        callback = request.callback if request.callback else self.spider.parse
        try:
            async for result in callback(response):
                if isinstance(result, Request):
                    if self._is_domain_allowed(result):
                        await self.scheduler.enqueue(result)
                    else:
                        self.stats.offsite_requests_count += 1
                        log.debug(f"Filtered offsite request to: {result.url}")
                elif isinstance(result, dict):
                    await self._handle_item(result)
                    log.debug(f"Scraped from {str(response)}\n{result}")
        except Exception as e:
            await self.spider.on_error(request, e)

    async def _handle_item(self, item: dict[str, Any]) -> None:
        """Handle a scraped item. Override or extend for item pipelines."""
        self.stats.items_scraped += 1
        self._items.append(item)

    async def _task_wrapper(self, request: Request) -> None:
        """Wrapper to track active task count."""
        try:
            await self._process_request(request)
        finally:
            self._active_tasks -= 1

    async def crawl(self) -> CrawlStats:
        """Run the spider and return CrawlStats."""
        self._running = True
        self._items.clear()
        self.stats = CrawlStats(start_time=anyio.current_time())

        async with self.session_manager:
            self.stats.concurrent_requests = self.spider.concurrent_requests
            self.stats.concurrent_requests_per_domain = self.spider.concurrent_requests_per_domain
            self.stats.download_delay = self.spider.download_delay
            await self.spider.on_start()

            try:
                async for request in self.spider.start_requests():
                    await self.scheduler.enqueue(request)

                # Process queue
                async with create_task_group() as tg:
                    while self._running:
                        if self.scheduler.is_empty:
                            # Empty queue + no active tasks = done
                            if self._active_tasks == 0:
                                self._running = False
                                log.debug("Spider idle")
                                break

                            # Brief wait for callbacks to enqueue new requests
                            await anyio.sleep(0.05)
                            continue

                        request = await self.scheduler.dequeue()
                        self._active_tasks += 1
                        tg.start_soon(self._task_wrapper, request)

            finally:
                await self.spider.on_close()

        self.stats.log_levels_counter = self.spider._log_counter.get_counts()
        self.stats.end_time = anyio.current_time()
        log.info(_dump(self.stats.to_dict()))
        return self.stats

    @property
    def items(self) -> list[dict[str, Any]]:
        """Access scraped items."""
        return self._items
