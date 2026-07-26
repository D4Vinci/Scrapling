from email.utils import parsedate_to_datetime
from datetime import datetime, timezone

from scrapling.core.utils import log
from scrapling.core._types import Dict, Mapping, Optional

BLOCK_BACKOFF_FACTOR = 2.0


def parse_retry_after(headers: Mapping[str, str]) -> Optional[float]:
    """Return how many seconds a `Retry-After` header asks us to wait, or `None` when it's missing or unreadable.

    :param headers: The response headers to look the value up in.
    """
    value = next((headers[key] for key in headers if key.lower() == "retry-after"), "").strip()
    if not value:
        return None

    try:
        return max(float(value), 0.0)
    except ValueError:
        pass

    try:  # The header can be an HTTP date instead of a number of seconds
        return max((parsedate_to_datetime(value) - datetime.now(timezone.utc)).total_seconds(), 0.0)
    except (TypeError, ValueError):
        log.debug(f"Ignoring an unreadable `Retry-After` header: {value!r}")
        return None


class AutoThrottle:
    """Adjusts the per-domain delay from the observed response latency, so the spider speeds up on fast
    servers and backs off on slow or hostile ones."""

    def __init__(
        self,
        start_delay: float = 5.0,
        max_delay: float = 60.0,
        target_concurrency: float = 1.0,
        block_backoff: bool = True,
    ):
        """
        :param start_delay: The delay used for the first request to a domain.
        :param max_delay: The highest delay the throttle is allowed to reach.
        :param target_concurrency: How many requests the spider aims to have in flight per domain. The engine
            passes the spider's `concurrent_requests_per_domain` here, or 1 when it's unlimited.
        :param block_backoff: Double the delay of a domain whenever it blocks us, or wait what its `Retry-After`
            header asks for.
        """
        if target_concurrency <= 0:
            raise ValueError("`target_concurrency` must be higher than 0")
        if max_delay < start_delay:
            raise ValueError("`autothrottle_max_delay` can't be lower than `autothrottle_start_delay`")

        self.start_delay = start_delay
        self.max_delay = max_delay
        self.target_concurrency = target_concurrency
        self.block_backoff = block_backoff
        self.delays: Dict[str, float] = {}

    def delay_for(self, domain: str, floor: float = 0.0) -> float:
        """Return the current delay for a domain, starting it at `start_delay` the first time.

        :param domain: The domain the request belongs to.
        :param floor: The lowest delay allowed, which is the spider's own delay for this domain.
        """
        if domain not in self.delays:
            self.delays[domain] = min(max(floor, self.start_delay), self.max_delay)
        return self.delays[domain]

    def record(
        self, domain: str, latency: float, ok: bool, floor: float = 0.0, retry_after: Optional[float] = None
    ) -> float:
        """Feed a finished request back into the throttle and return the domain's new delay.

        :param domain: The domain the request belongs to.
        :param latency: How long the request took in seconds.
        :param ok: Whether the response was a healthy one, so a non-blocked 2xx.
        :param floor: The lowest delay allowed, which is the spider's own delay for this domain.
        :param retry_after: How long the website asked us to wait, when it did.
        """
        current_delay = self.delay_for(domain, floor)
        target_delay = latency / self.target_concurrency
        new_delay = max((current_delay + target_delay) / 2, target_delay)

        if not ok:
            penalty = current_delay
            if self.block_backoff:
                penalty = retry_after if retry_after is not None else current_delay * BLOCK_BACKOFF_FACTOR
            new_delay = max(new_delay, penalty, current_delay)  # A block can never speed the spider up

        new_delay = min(max(new_delay, floor), self.max_delay)
        self.delays[domain] = new_delay
        log.debug(
            f"AutoThrottle ({domain}): latency={latency:.2f}s, ok={ok}, delay {current_delay:.2f}s -> {new_delay:.2f}s"
        )
        return new_delay

    def reset(self) -> None:
        """Drop every learned delay."""
        self.delays.clear()
