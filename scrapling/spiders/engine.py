import json
import pprint
from pathlib import Path

import anyio
from anyio import Path as AsyncPath
from anyio import create_task_group, CapacityLimiter, create_memory_object_stream, EndOfStream

from scrapling.core.utils import log
from scrapling.spiders.request import Request
from scrapling.spiders.scheduler import Scheduler
from scrapling.spiders.session import SessionManager
from scrapling.spiders.result import CrawlStats, ItemList
from scrapling.spiders.checkpoint import CheckpointManager, CheckpointData
from scrapling.core._types import Dict, Union, Optional, TYPE_CHECKING, Any, AsyncGenerator

if TYPE_CHECKING:
    from scrapling.spiders.spider import Spider


def _dump(obj: Dict) -> str:
    return json.dumps(obj, indent=4)


class CrawlerEngine:
    """Orchestrates the crawling process."""

    def __init__(
        self,
        spider: "Spider",
        session_manager: SessionManager,
        crawldir: Optional[Union[str, Path, AsyncPath]] = None,
        interval: float = 300.0,
    ):
        self.spider = spider
        self.session_manager = session_manager
        self.scheduler = Scheduler()
        self.stats = CrawlStats()

        self._global_limiter = CapacityLimiter(spider.concurrent_requests)
        self._domain_limiters: dict[str, CapacityLimiter] = {}
        self._allowed_domains: set[str] = spider.allowed_domains or set()

        self._active_tasks: int = 0
        self._running: bool = False
        self._items: ItemList = ItemList()
        self._item_stream: Any = None

        self._checkpoint_system_enabled = bool(crawldir)
        self._checkpoint_manager = CheckpointManager(crawldir or "", interval)
        self._last_checkpoint_time: float = 0.0
        self._pause_requested: bool = False
        self._force_stop: bool = False
        self.paused: bool = False

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

        if await self.spider.is_blocked(response):
            self.stats.blocked_requests_count += 1
            if request._retry_count < self.spider.max_blocked_retries:
                retry_request = request.copy()
                retry_request._retry_count += 1
                retry_request.priority -= 1  # Don't retry immediately
                retry_request.dont_filter = True
                new_request = await self.spider.retry_blocked_request(retry_request, response)
                await self.scheduler.enqueue(new_request)
                log.info(
                    f"Scheduled blocked request for retry ({retry_request._retry_count}/{self.spider.max_blocked_retries}): {request.url}"
                )
            else:
                log.warning(f"Max retries exceeded for blocked request: {request.url}")
            return

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
                    processed_result = await self.spider.on_scraped_item(result)
                    if processed_result:
                        self.stats.items_scraped += 1
                        log.debug(f"Scraped from {str(response)}\n{pprint.pformat(processed_result)}")
                        if self._item_stream:
                            await self._item_stream.send(processed_result)
                        else:
                            self._items.append(processed_result)
                    else:
                        self.stats.items_dropped += 1
                        log.warning(f"Dropped from {str(response)}\n{processed_result}")
                elif result is not None:
                    log.error(f"Spider must return Request, dict or None, got '{type(result)}' in {request}")
        except Exception as e:
            msg = f"Spider error processing {request}:\n {e}"
            log.error(msg, exc_info=e)
            await self.spider.on_error(request, e)

    async def _task_wrapper(self, request: Request) -> None:
        """Wrapper to track active task count."""
        try:
            await self._process_request(request)
        finally:
            self._active_tasks -= 1

    def request_pause(self) -> None:
        """Request a graceful pause of the crawl.

        First call: requests graceful pause (waits for active tasks).
        Second call: forces immediate stop.
        """
        if self._force_stop:
            return  # Already forcing stop

        if self._pause_requested:
            # Second Ctrl+C - force stop
            self._force_stop = True
            log.warning("Force stop requested, cancelling immediately...")
        else:
            self._pause_requested = True
            log.info(
                "Pause requested, waiting for in-flight requests to complete (press Ctrl+C again to force stop)..."
            )

    async def _save_checkpoint(self) -> None:
        """Save current state to checkpoint files."""
        requests, seen = self.scheduler.snapshot()
        data = CheckpointData(requests=requests, seen=seen)
        await self._checkpoint_manager.save(data)
        self._last_checkpoint_time = anyio.current_time()

    def _is_checkpoint_time(self) -> bool:
        """Check if it's time for the periodic checkpoint."""
        if not self._checkpoint_system_enabled:
            return False

        if self._checkpoint_manager.interval == 0:
            return False

        current_time = anyio.current_time()
        return (current_time - self._last_checkpoint_time) >= self._checkpoint_manager.interval

    async def _restore_from_checkpoint(self) -> bool:
        """Attempt to restore state from checkpoint.

        Returns True if successfully restored, False otherwise.
        """
        if not self._checkpoint_system_enabled:
            raise

        data = await self._checkpoint_manager.load()
        if data is None:
            return False

        self.scheduler.restore(data)

        # Restore callbacks from spider after scheduler restore
        for request in data.requests:
            request._restore_callback(self.spider)

        return True

    async def crawl(self) -> CrawlStats:
        """Run the spider and return CrawlStats."""
        self._running = True
        self._items.clear()
        self.paused = False
        self._pause_requested = False
        self.stats = CrawlStats(start_time=anyio.current_time())

        # Check for existing checkpoint
        resuming = (await self._restore_from_checkpoint()) if self._checkpoint_system_enabled else False
        self._last_checkpoint_time = anyio.current_time()

        async with self.session_manager:
            self.stats.concurrent_requests = self.spider.concurrent_requests
            self.stats.concurrent_requests_per_domain = self.spider.concurrent_requests_per_domain
            self.stats.download_delay = self.spider.download_delay
            await self.spider.on_start(resuming=resuming)

            try:
                if not resuming:
                    async for request in self.spider.start_requests():
                        await self.scheduler.enqueue(request)
                else:
                    log.info("Resuming from checkpoint, skipping start_requests()")

                # Process queue
                async with create_task_group() as tg:
                    while self._running:
                        # Check for pause/stop request
                        if self._checkpoint_system_enabled:
                            if self._pause_requested:
                                # Wait for active tasks to complete
                                if self._active_tasks == 0 or self._force_stop:
                                    if self._force_stop:
                                        log.warning(f"Force stopping with {self._active_tasks} active tasks")

                                    await self._save_checkpoint()
                                    self.paused = True
                                    self._running = False

                                    if not self._force_stop:
                                        log.info("Spider paused, checkpoint saved")
                                    else:
                                        tg.cancel_scope.cancel()
                                    break
                                # Wait briefly and check again
                                await anyio.sleep(0.05)
                                continue

                            if self._is_checkpoint_time():
                                await self._save_checkpoint()

                        if self.scheduler.is_empty:
                            # Empty queue + no active tasks = done
                            if self._active_tasks == 0:
                                self._running = False
                                log.debug("Spider idle")
                                break

                            # Brief wait for callbacks to enqueue new requests
                            await anyio.sleep(0.05)
                            continue

                        # Only spawn tasks up to concurrent_requests limit
                        # This prevents spawning thousands of waiting tasks
                        if self._active_tasks >= self.spider.concurrent_requests:
                            await anyio.sleep(0.01)
                            continue

                        request = await self.scheduler.dequeue()
                        self._active_tasks += 1
                        tg.start_soon(self._task_wrapper, request)

            finally:
                await self.spider.on_close()
                # Clean up checkpoint files on successful completion (not paused)
                if not self.paused and self._checkpoint_system_enabled:
                    await self._checkpoint_manager.cleanup()

        self.stats.log_levels_counter = self.spider._log_counter.get_counts()
        self.stats.end_time = anyio.current_time()
        log.info(_dump(self.stats.to_dict()))
        return self.stats

    @property
    def items(self) -> ItemList:
        """Access scraped items."""
        return self._items

    def __aiter__(self) -> AsyncGenerator[dict, None]:
        return self._stream()

    async def _stream(self) -> AsyncGenerator[dict, None]:
        """Async generator that runs crawl and yields items."""
        send, recv = create_memory_object_stream[dict](100)
        self._item_stream = send

        async def run():
            try:
                await self.crawl()
            finally:
                await send.aclose()

        async with create_task_group() as tg:
            tg.start_soon(run)
            try:
                async for item in recv:
                    yield item
            except EndOfStream:
                pass
