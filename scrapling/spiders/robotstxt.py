from urllib.parse import urlparse

from anyio import create_task_group
from protego import Protego

from scrapling.core._types import Dict, Optional, Callable, Awaitable
from scrapling.core.utils import log


class RobotsTxtManager:
    """Manages fetching, parsing, and caching of robots.txt files."""

    def __init__(self, fetch_fn: Callable[[str, str], Awaitable]):
        self._fetch_fn = fetch_fn
        self._cache: Dict[str, Protego] = {}

    async def _get_parser(self, url: str, sid: str) -> Protego:
        parsed = urlparse(url)
        domain = parsed.netloc

        if domain in self._cache:
            return self._cache[domain]

        scheme = parsed.scheme or "https"
        robots_url = f"{scheme}://{domain}/robots.txt"
        content = ""
        try:
            response = await self._fetch_fn(robots_url, sid)
            if response.status == 200:
                content = response.body.decode(response.encoding, errors="replace")
        except Exception as e:
            log.warning(f"Failed to fetch robots.txt for {domain}: {e}")

        try:
            # Left in place, a BOM hides the first line (usually `User-agent: *`) from protego
            parser = Protego.parse(content.removeprefix("\N{BYTE ORDER MARK}"))
        except Exception as e:
            log.warning(f"Failed to parse robots.txt for {domain}: {e}")
            parser = Protego.parse("")

        self._cache[domain] = parser
        return parser

    async def can_fetch(self, url: str, sid: str) -> bool:
        """Check if a URL can be fetched according to the domain's robots.txt.

        :param url: The full URL to check
        :param sid: Session ID for fetching robots.txt if not yet cached
        """
        parser = await self._get_parser(url, sid)
        return parser.can_fetch(url, "*")

    async def get_delay_directives(self, url: str, sid: str) -> tuple[Optional[float], Optional[tuple[int, int]]]:
        """Return both crawl-delay and request-rate in a single parser lookup.

        :param url: Any URL on the domain to check
        :param sid: Session ID for fetching robots.txt if not yet cached
        """
        parser = await self._get_parser(url, sid)
        c_delay = parser.crawl_delay("*")
        rate = parser.request_rate("*")
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
