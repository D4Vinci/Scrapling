import asyncio
from itertools import count

from scrapling.core.utils import log
from scrapling.spiders.request import Request


class Scheduler:
    """
    Priority queue with URL deduplication. (heapq)

    Higher priority requests are processed first.
    Duplicate URLs are filtered unless dont_filter=True.
    """

    def __init__(self):
        self._queue: asyncio.PriorityQueue[tuple[int, int, Request]] = asyncio.PriorityQueue()
        self._seen: set[str] = set()
        self._counter = count()

    async def enqueue(self, request: Request) -> bool:
        """Add a request to the queue."""
        fingerprint = request._fp

        if not request.dont_filter and fingerprint in self._seen:
            log.debug("Dropped duplicate request: %s", request)
            return False

        self._seen.add(fingerprint)

        # Negative priority so higher priority = dequeued first
        await self._queue.put((-request.priority, next(self._counter), request))
        return True

    async def dequeue(self) -> Request:
        """Get the next request to process."""
        _, _, request = await self._queue.get()
        return request

    def __len__(self) -> int:
        return self._queue.qsize()

    @property
    def is_empty(self) -> bool:
        return self._queue.empty()
