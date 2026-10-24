"""Sitemap template spider."""

import re
from dataclasses import dataclass, field, replace
from datetime import datetime, timedelta, timezone
from urllib.parse import urlsplit

from lxml import etree
from protego import Protego

from scrapling.core._types import (
    TYPE_CHECKING,
    Any,
    AsyncGenerator,
    Dict,
    List,
    Optional,
    Union,
)
from scrapling.spiders.links import LinkExtractor
from scrapling.spiders.request import Request
from scrapling.spiders.spider import Spider
from scrapling.spiders.templates.crawler import CrawlRule
from scrapling.spiders.templates._utils import _decompress

if TYPE_CHECKING:
    from scrapling.engines.toolbelt.custom import Response


__all__ = ["SitemapSpider"]

# W3C Datetime (https://www.w3.org/TR/NOTE-datetime), used by `<lastmod>` and `<news:publication_date>`
_W3C_DATETIME = re.compile(
    r"(\d{4})(?:-(\d{2})(?:-(\d{2})(?:[Tt ](\d{2}):(\d{2})(?::(\d{2})(?:[.,](\d+))?)?\s*([Zz]|[+-]\d{2}:?\d{2})?)?)?)?"
)


def _parse_w3c_datetime(value: Optional[str]) -> Optional[datetime]:
    """Parse a sitemap date like `2026-01-15` or `2026-01-15T10:30:00+02:00` into an aware datetime.

    Dates without an offset are taken as UTC, and unreadable ones return `None` instead of raising.
    """
    match = _W3C_DATETIME.fullmatch(value.strip()) if value else None
    if not match:
        return None

    year, month, day, hour, minute, second, fraction, offset = match.groups()
    try:
        tz = timezone.utc
        if offset and offset.upper() != "Z":
            digits = offset[1:].replace(":", "")
            delta = timedelta(hours=int(digits[:2]), minutes=int(digits[2:]))
            tz = timezone(-delta if offset[0] == "-" else delta)
        return datetime(
            int(year),
            int(month or 1),
            int(day or 1),
            int(hour or 0),
            int(minute or 0),
            int(second or 0),
            int((fraction or "0")[:6].ljust(6, "0")),
            tzinfo=tz,
        )
    except ValueError:
        return None


@dataclass
class SitemapEntry:
    """A URL listed in a sitemap, with the dates and title the sitemap gives for it."""

    url: str
    lastmod: Optional[datetime] = None
    news_publication_date: Optional[datetime] = None
    news_title: Optional[str] = None

    @property
    def meta(self) -> Dict[str, Any]:
        """The metadata handed to the URL's request. Every key is set, so none is inherited from the sitemap's request."""
        return {
            "sitemap_lastmod": self.lastmod,
            "sitemap_news_publication_date": self.news_publication_date,
            "sitemap_news_title": self.news_title,
        }

    def is_older_than(self, cutoff: datetime) -> bool:
        """Whether every date the sitemap gives for this URL is before `cutoff`. URLs without dates never are."""
        dates = [date for date in (self.lastmod, self.news_publication_date) if date is not None]
        return bool(dates) and max(dates) < cutoff


@dataclass
class SitemapResult:
    """Parsed sitemap body.

    `urls` holds the entries from a `<urlset>`; `sitemaps` holds child sitemap
    entries from a `<sitemapindex>` (each of which is fetched recursively).
    """

    urls: List[SitemapEntry] = field(default_factory=list)
    sitemaps: List[SitemapEntry] = field(default_factory=list)


class SitemapSpider(Spider):
    """A Spider that seeds a crawl from sitemap(s), and follows the rules.

    Override `rules()` to return a list of `CrawlRule`s.

    If there are no rules provided, all non-sitemap urls will be redirected to `parse()`, which must be overridden or it will raise `NotImplementedError`.

    Each URL's request carries what the sitemap says about it in `meta`: `sitemap_lastmod` and, for Google News
    sitemaps, `sitemap_news_publication_date` and `sitemap_news_title`. Dates are timezone-aware datetimes (UTC when
    the sitemap gives no offset), and any value the sitemap doesn't give is `None`.

    :cvar sitemap_urls: Explicit list of sitemap (or robots.txt) URLs to fetch.
    :cvar sitemap_follow: `LinkExtractor` filtering which child sitemaps inside a
        `<sitemapindex>` to descend into. ``None`` means descend into all.
    :cvar sitemap_alternate_links: When enabled, alternate-language URLs are also
        routed through `rules()`.
    :cvar sitemap_since: Skip URLs, and child sitemaps, whose sitemap dates are all older than this. Either a
        `datetime` (naive ones are taken as UTC) or a `timedelta` counted back from the moment each sitemap is
        parsed. URLs without any date are always kept. ``None`` keeps everything.
    """

    sitemap_urls: List[str] = []
    sitemap_follow: Optional[LinkExtractor] = None
    sitemap_alternate_links: bool = False
    sitemap_since: Optional[Union[datetime, timedelta]] = None

    def rules(self) -> List[CrawlRule]:
        """Override to define dispatch rules for sitemap URLs."""
        return []

    async def start_requests(self) -> AsyncGenerator[Request, None]:
        if self.sitemap_urls:
            for url in self.sitemap_urls:
                yield Request(url, callback=self._parse_sitemap)
            return

        raise RuntimeError("`SitemapSpider` needs `sitemap_urls` to be set.")

    async def parse(self, response: "Response") -> AsyncGenerator[Union[Dict[str, Any], Request, None], None]:
        """Default callback for processing responses"""
        raise NotImplementedError(f"{self.__class__.__name__} must implement parse() method")
        yield  # Make this a generator for type checkers

    def _robots_body(self, response: "Response") -> List[str]:
        """Extract `Sitemap` directives from a robots.txt body via protego."""
        try:
            text = response.body.decode(response.encoding, errors="replace")
            # Left in place, a BOM hides the first directive from protego
            parser = Protego.parse(text.removeprefix("\N{BYTE ORDER MARK}"))
        except Exception as e:
            self.logger.warning(f"Failed to parse robots.txt: {e}")
            return []
        return list(parser.sitemaps)

    def _extract_urls(self, root: Any, tag: str = "url") -> List[SitemapEntry]:
        """Read every `tag` element under `root` (`<url>` in a urlset, `<sitemap>` in an index) into entries."""
        entries: List[SitemapEntry] = []
        for url_el in root:
            if self._get_type(url_el) != tag:
                continue

            entry = SitemapEntry(url="")
            alternates: List[str] = []
            for child in url_el:
                name = self._get_type(child)
                if name == "loc" and child.text:
                    entry.url = child.text.strip()
                elif name == "lastmod":
                    entry.lastmod = _parse_w3c_datetime(child.text)
                elif name == "news":
                    for news_el in child:
                        news_name = self._get_type(news_el)
                        if news_name == "publication_date":
                            entry.news_publication_date = _parse_w3c_datetime(news_el.text)
                        elif news_name == "title" and news_el.text:
                            entry.news_title = news_el.text.strip()
                elif self.sitemap_alternate_links and name == "link":
                    href = child.get("href")
                    if href:
                        alternates.append(href.strip())

            if entry.url:
                entries.append(entry)
            # Alternate-language versions of a page share its dates and title
            entries.extend(replace(entry, url=href) for href in alternates)
        return entries

    def _sitemap_cutoff(self) -> Optional[datetime]:
        """Resolve `sitemap_since` into an aware datetime, or `None` when it's not set."""
        since = self.sitemap_since
        if since is None:
            return None
        if isinstance(since, timedelta):
            return datetime.now(timezone.utc) - since
        return since if since.tzinfo else since.replace(tzinfo=timezone.utc)

    @staticmethod
    def _get_type(el: Any) -> str:
        if not isinstance(el.tag, str):
            return ""
        return etree.QName(el.tag).localname

    def _sm_body(self, body: bytes, content_type: Optional[str] = None) -> SitemapResult:
        """Parse a sitemap body and return its URLs and any child sitemaps."""
        try:
            body = _decompress(body, content_type)
        except OSError as e:
            self.logger.warning(f"Failed to decompress sitemap: {e}")
            return SitemapResult()

        try:
            root = etree.fromstring(body)
        except etree.XMLSyntaxError as e:
            self.logger.warning(f"Failed to parse sitemap XML: {e}")
            return SitemapResult()

        root_name = self._get_type(root)
        if root_name == "sitemapindex":
            return SitemapResult(sitemaps=self._extract_urls(root, tag="sitemap"))
        if root_name == "urlset":
            return SitemapResult(urls=self._extract_urls(root))

        self.logger.warning(f"Unknown sitemap root element: {root_name!r}")
        return SitemapResult()

    async def _parse_sitemap(self, response: "Response") -> AsyncGenerator[Union[Dict[str, Any], Request, None], None]:
        if urlsplit(response.url).path.endswith("/robots.txt"):
            sitemaps = self._robots_body(response)
            if not sitemaps:
                self.logger.warning(f"No Sitemaps found in {response.url}")

            for sitemap_url in sitemaps:
                yield response.follow(sitemap_url, callback=self._parse_sitemap)
            return

        content_type = response.headers.get("content-type") if response.headers else None
        result = self._sm_body(response.body, content_type=content_type)

        cutoff = self._sitemap_cutoff()
        skipped = 0

        # Descend into child sitemaps (apply sitemap_follow filter if present)
        for child in result.sitemaps:
            if self.sitemap_follow is not None and not self.sitemap_follow.matches(child.url):
                continue
            if cutoff is not None and child.is_older_than(cutoff):
                skipped += 1
                continue
            yield response.follow(child.url, callback=self._parse_sitemap)

        # Dispatch each URL through rules() (first match wins; unmatched drop unless rules empty)
        rules = self.rules()
        for entry in result.urls:
            if cutoff is not None and entry.is_older_than(cutoff):
                skipped += 1
                continue
            req = self._dispatch(response, entry.url, rules, meta=entry.meta)
            if req is not None:
                yield req

        if skipped:
            self.logger.debug(f"Skipped {skipped} sitemap entries older than {cutoff} in {response.url}")

    def _dispatch(
        self, response: "Response", url: str, rules: List[CrawlRule], meta: Optional[Dict[str, Any]] = None
    ) -> Optional[Request]:
        # The callback is always set explicitly, otherwise `follow()` would inherit `_parse_sitemap` from the sitemap request
        if not rules:
            return response.follow(url, callback=self.parse, meta=meta)
        for rule in rules:
            if rule.link_extractor.matches(url):
                req = response.follow(url, callback=rule.callback or self.parse, meta=meta)
                if rule.priority is not None:
                    req.priority = rule.priority
                if rule.process_request is not None:
                    req = rule.process_request(req, response)
                return req
        return None
