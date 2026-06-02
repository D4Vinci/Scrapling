"""Sitemap template spider."""

from dataclasses import dataclass, field
from gzip import GzipFile
from io import BytesIO
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

if TYPE_CHECKING:
    from scrapling.engines.toolbelt.custom import Response


__all__ = ["SitemapSpider"]


_GZIP_MAGIC = b"\x1f\x8b"
_GUNZIP_MAX_SIZE = 64 * 1024 * 1024  # 64 MiB cap, defends against gzip bombs
_SAFE_XML_PARSER = etree.XMLParser(
    resolve_entities=False,
    no_network=True,
    dtd_validation=False,
    load_dtd=False,
    huge_tree=False,
    recover=True,
)


@dataclass
class SitemapResult:
    """Parsed sitemap body.

    `urls` holds the entries from a `<urlset>`; `sitemaps` holds child sitemap
    URLs from a `<sitemapindex>` (each of which is fetched recursively).
    """

    urls: List[str] = field(default_factory=list)
    sitemaps: List[str] = field(default_factory=list)


class SitemapSpider(Spider):
    """A Spider that seeds a crawl from sitemap(s), and follows the rules.

    Override `rules()` to return a list of `CrawlRule`s.

    If there are no rules provided, all non-sitemap urls will be redirected to `parse()`, which must be overridden or it will raise `NotImplementedError`.

    :cvar sitemap_urls: Explicit list of sitemap (or robots.txt) URLs to fetch.
    :cvar sitemap_follow: `LinkExtractor` filtering which child sitemaps inside a
        `<sitemapindex>` to descend into. ``None`` means descend into all.
    :cvar sitemap_alternate_links: When enabled, alternate-language URLs are also
        routed through `rules()`.
    """

    sitemap_urls: List[str] = []
    sitemap_follow: Optional[LinkExtractor] = None
    sitemap_alternate_links: bool = False

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
            parser = Protego.parse(text)
        except Exception as e:
            self.logger.warning(f"Failed to parse robots.txt: {e}")
            return []
        return list(parser.sitemaps)

    @staticmethod
    def _decompress(body: bytes, content_type: Optional[str]) -> bytes:
        if (content_type and ("gzip" in content_type.lower())) or (body[:2] == _GZIP_MAGIC):
            out = bytearray()
            with GzipFile(fileobj=BytesIO(body)) as f:
                while chunk := f.read1(8192):
                    out.extend(chunk)
                    if len(out) > _GUNZIP_MAX_SIZE:
                        raise OSError(f"gzip output exceeds {_GUNZIP_MAX_SIZE} bytes")
            return bytes(out)
        return body

    def _extract_urls(self, root: Any) -> List[str]:
        urls: List[str] = []
        for url_el in root:
            if self._get_type(url_el) != "url":
                continue

            for child in url_el:
                name = self._get_type(child)
                if name == "loc" and child.text:
                    urls.append(child.text.strip())
                elif self.sitemap_alternate_links and name == "link":
                    href = child.get("href")
                    if href:
                        urls.append(href.strip())
        return urls

    @staticmethod
    def _get_type(el: Any) -> str:
        return etree.QName(el.tag).localname

    def _sm_body(self, body: bytes, content_type: Optional[str] = None) -> SitemapResult:
        """Parse a sitemap body and return its URLs and any child sitemaps."""
        try:
            body = self._decompress(body, content_type)
        except OSError as e:
            self.logger.warning(f"Failed to decompress sitemap: {e}")
            return SitemapResult()

        try:
            root = etree.fromstring(body, parser=_SAFE_XML_PARSER)
        except etree.XMLSyntaxError as e:
            self.logger.warning(f"Failed to parse sitemap XML: {e}")
            return SitemapResult()

        root_name = self._get_type(root)
        if root_name == "sitemapindex":
            locs = []
            for sm_el in root:
                if self._get_type(sm_el) == "sitemap":
                    for child in sm_el:
                        if self._get_type(child) == "loc" and child.text:
                            locs.append(child.text.strip())
                            break
            return SitemapResult(sitemaps=locs)
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

        # Descend into child sitemaps (apply sitemap_follow filter if present)
        for child_url in result.sitemaps:
            if self.sitemap_follow is not None and not self.sitemap_follow.matches(child_url):
                continue
            yield response.follow(child_url, callback=self._parse_sitemap)

        # Dispatch each URL through rules() (first match wins; unmatched drop unless rules empty)
        rules = self.rules()
        for url in result.urls:
            req = self._dispatch(response, url, rules)
            if req is not None:
                yield req

    @staticmethod
    def _dispatch(response: "Response", url: str, rules: List[CrawlRule]) -> Optional[Request]:
        if not rules:
            return response.follow(url)
        for rule in rules:
            if rule.link_extractor.matches(url):
                req = response.follow(url, callback=rule.callback)
                if rule.priority is not None:
                    req.priority = rule.priority
                if rule.process_request is not None:
                    req = rule.process_request(req, response)
                return req
        return None
