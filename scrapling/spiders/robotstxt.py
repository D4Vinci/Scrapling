import asyncio
from urllib.parse import urlparse

from protego import Protego

from scrapling.core._types import Dict, List, Optional, Callable, Awaitable
from scrapling.core.utils import log


class RobotsTxtManager:
    """Manages fetching, parsing, and caching of robots.txt files.

    Accepts a fetch callable ``(url: str, sid: str) -> Awaitable[Response]``
    so it stays decoupled from any specific session or transport layer.

    All public methods accept only ``(url, sid)`` — domain and scheme are
    derived internally from the URL so callers don't pass redundant data.

    Handles all standard robots.txt directives including:
    - User-agent specific rules
    - Allow/Disallow directives (including wildcards and $ anchors)
    - Crawl-delay directives
    - Sitemap declarations
    """

    def __init__(self, fetch_fn: Callable[[str, str], Awaitable]):
        self._fetch_fn = fetch_fn
        self._cache: Dict[tuple[str, str], Protego] = {}
        self._locks: Dict[tuple[str, str], asyncio.Lock] = {}

    async def _get_parser(self, url: str, sid: str) -> Protego:
        parsed = urlparse(url)
        domain = parsed.netloc
        scheme = parsed.scheme or "https"
        cache_key = (domain, sid)

        if cache_key not in self._cache:
            lock = self._locks.setdefault(cache_key, asyncio.Lock())
            async with lock:
                # Double-check if another task has already populated the cache
                if cache_key in self._cache:
                    return self._cache[cache_key]

                robots_url = f"{scheme}://{domain}/robots.txt"
                content = ""
                try:
                    response = await self._fetch_fn(robots_url, sid)
                    if response.status == 200:
                        body = response.body
                        content = body.decode(response.encoding, errors="replace") if isinstance(body, bytes) else body
                except Exception as e:
                    log.warning(f"Failed to fetch robots.txt for {domain}: {e}")

                parser = Protego.parse(content)
                self._cache[cache_key] = parser
                if cache_key in self._locks:
                    del self._locks[cache_key]

        return self._cache[cache_key]

    async def can_fetch(self, url: str, sid: str) -> bool:
        """Check if a URL can be fetched according to the domain's robots.txt.

        Handles:
        - User-agent specific rules (e.g., User-agent: SpinarakBot)
        - Wildcard user-agent rules (User-agent: *)
        - Allow/Disallow directives with wildcards (e.g., /*.pdf$)
        - Allow directives that override Disallow (e.g., Allow: /admin/public-docs/)

        Uses the wildcard user-agent (*) which matches standard robots.txt directives
        that apply to all bots. This is the conservative approach — if a URL is
        disallowed for all bots, we respect that.

        Args:
            url: The full URL to check
            sid: Session ID for fetching robots.txt

        Returns:
            True if the URL can be fetched, False otherwise
        """
        parser = await self._get_parser(url, sid)
        return parser.can_fetch(url, "*")

    async def get_crawl_delay(self, url: str, sid: str) -> Optional[float]:
        """Get the crawl delay for this crawler.

        Uses the wildcard user-agent (*) to get the general crawl delay
        that applies to all bots.

        Args:
            url: Any URL on the domain to check
            sid: Session ID for fetching robots.txt

        Returns:
            The crawl delay in seconds, or None if not specified
        """
        parser = await self._get_parser(url, sid)
        delay = parser.crawl_delay("*")
        return float(delay) if delay is not None else None

    async def get_sitemaps(self, url: str, sid: str) -> List[str]:
        """Get all sitemap URLs declared in robots.txt.

        Args:
            url: Any URL on the domain to check
            sid: Session ID for fetching robots.txt

        Returns:
            List of sitemap URLs declared in the robots.txt
        """
        parser = await self._get_parser(url, sid)
        return list(parser.sitemaps)

    async def get_request_rate(self, url: str, sid: str) -> Optional[tuple[int, int]]:
        """Get the request rate for this crawler.

        Uses the wildcard user-agent (*) to get the general request rate
        that applies to all bots.

        Args:
            url: Any URL on the domain to check
            sid: Session ID for fetching robots.txt

        Returns:
            A tuple of (requests, seconds) if specified, or None if not specified
        """
        parser = await self._get_parser(url, sid)
        rate = parser.request_rate("*")
        if rate is not None:
            return (rate.requests, rate.seconds)
        return None

    def clear_cache(self, domain: Optional[str] = None, sid: Optional[str] = None) -> None:
        """Clear the robots.txt cache.

        Args:
            domain: If specified, only clear cache for this domain
            sid: If specified, only clear cache for this session ID
                 If both are None, clears the entire cache
        """
        if domain is None and sid is None:
            self._cache.clear()
            self._locks.clear()
        else:
            keys_to_remove = [
                key for key in self._cache if (domain is None or key[0] == domain) and (sid is None or key[1] == sid)
            ]
            for key in keys_to_remove:
                self._cache.pop(key, None)
                self._locks.pop(key, None)
