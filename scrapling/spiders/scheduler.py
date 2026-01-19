import asyncio
from itertools import count

from scrapling.core.utils import log
from scrapling.spiders.request import Request
from scrapling.core._types import List, Set, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from scrapling.spiders.checkpoint import CheckpointData


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
        # Mirror dict for snapshot without draining queue
        self._pending: dict[int, tuple[int, int, Request]] = {}

    async def enqueue(self, request: Request) -> bool:
        """Add a request to the queue."""
        fingerprint = request._fp

        if not request.dont_filter and fingerprint in self._seen:
            log.debug("Dropped duplicate request: %s", request)
            return False

        self._seen.add(fingerprint)

        # Negative priority so higher priority = dequeued first
        counter = next(self._counter)
        item = (-request.priority, counter, request)
        self._pending[counter] = item
        await self._queue.put(item)
        return True

    async def dequeue(self) -> Request:
        """Get the next request to process."""
        _, counter, request = await self._queue.get()
        self._pending.pop(counter, None)
        return request

    def __len__(self) -> int:
        return self._queue.qsize()

    @property
    def is_empty(self) -> bool:
        return self._queue.empty()

    def snapshot(self) -> Tuple[List[Request], Set[str]]:
        """Create a snapshot of the current state for checkpoints."""
        sorted_items = sorted(self._pending.values(), key=lambda x: (x[0], x[1]))  # Maintain queue order
        requests = [item[2] for item in sorted_items]
        return requests, self._seen.copy()

    def restore(self, data: "CheckpointData") -> None:
        """Restore scheduler state from checkpoint data.

        :param data: CheckpointData containing requests and seen set
        """
        self._seen = data.seen.copy()

        # Restore pending requests in order (they're already sorted by priority)
        for request in data.requests:
            counter = next(self._counter)
            item = (-request.priority, counter, request)
            self._pending[counter] = item
            self._queue.put_nowait(item)

        log.info(f"Scheduler restored: {len(data.requests)} requests, {len(data.seen)} seen")
