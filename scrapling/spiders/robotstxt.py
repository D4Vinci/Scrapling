from time import time
from urllib.parse import urlparse

from anyio import create_task_group
from protego import Protego

from scrapling.core._types import Dict, Optional, Callable, Awaitable
from scrapling.core.utils import log


class RobotsTxtManager:
    """Manages fetching, parsing, and caching of robots.txt files."""

    def __init__(
        self,
        fetch_fn: Callable[[str, str], Awaitable],
        user_agent: str = "*",
        fail_closed: bool = False,
        max_cache_entries: int = 256,
        ttl_seconds: Optional[float] = None,
    ):
        self._fetch_fn = fetch_fn
        self._user_agent = user_agent or "*"
        self._fail_closed = fail_closed
        self._max_cache_entries = max_cache_entries
        self._ttl_seconds = ttl_seconds
        self._cache: Dict[str, tuple[float, Protego]] = {}

    async def _get_parser(self, url: str, sid: str) -> Protego:
        parsed = urlparse(url)
        hostname = (parsed.hostname or parsed.netloc).lower()
        authority = hostname
        if parsed.port is not None:
            authority = f"{hostname}:{parsed.port}"
        domain = authority

        cached = self._cache.get(domain)
        if cached is not None:
            cached_at, parser = cached
            if self._ttl_seconds is None or time() - cached_at <= self._ttl_seconds:
                return parser
            self._cache.pop(domain, None)

        scheme = parsed.scheme or "https"
        robots_url = f"{scheme}://{authority}/robots.txt"
        content = ""
        try:
            response = await self._fetch_fn(robots_url, sid)
            if response.status == 200:
                content = response.body.decode(response.encoding, errors="replace")
        except Exception as e:
            log.warning(f"Failed to fetch robots.txt for {domain}: {e}")
            if self._fail_closed:
                content = "User-agent: *\nDisallow: /\n"

        try:
            parser = Protego.parse(content)
        except Exception as e:
            log.warning(f"Failed to parse robots.txt for {domain}: {e}")
            parser = Protego.parse("User-agent: *\nDisallow: /\n" if self._fail_closed else "")

        if len(self._cache) >= self._max_cache_entries:
            self._cache.pop(next(iter(self._cache)))
        self._cache[domain] = (time(), parser)
        return parser

    async def can_fetch(self, url: str, sid: str) -> bool:
        """Check if a URL can be fetched according to the domain's robots.txt.

        :param url: The full URL to check
        :param sid: Session ID for fetching robots.txt if not yet cached
        """
        parser = await self._get_parser(url, sid)
        return parser.can_fetch(url, self._user_agent)

    async def get_delay_directives(self, url: str, sid: str) -> tuple[Optional[float], Optional[tuple[int, int]]]:
        """Return both crawl-delay and request-rate in a single parser lookup.

        :param url: Any URL on the domain to check
        :param sid: Session ID for fetching robots.txt if not yet cached
        """
        parser = await self._get_parser(url, sid)
        c_delay = parser.crawl_delay(self._user_agent)
        rate = parser.request_rate(self._user_agent)
        return (
            float(c_delay) if c_delay is not None else None,
            (rate.requests, rate.seconds) if rate is not None else None,
        )

    async def prefetch(self, urls: list[str], sid: str) -> None:
        """Pre-warm the robots.txt cache for a list of seed URLs concurrently.

        :param urls: Seed URLs whose domains should be pre-fetched (one per domain).
        :param sid: Session ID to use for the robots.txt fetch requests.
        """
        if not urls:
            return
        log.debug(f"Pre-fetching robots.txt for {len(urls)} domain(s)")
        async with create_task_group() as tg:
            for url in urls:
                tg.start_soon(self._get_parser, url, sid)
