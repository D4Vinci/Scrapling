"""Site-to-Markdown template spider for building RAG/LLM ingestion pipelines."""

from re import sub as re_sub
from hashlib import sha1
from urllib.parse import urlparse

from anyio import Path as AsyncPath

from scrapling.spiders.links import LinkExtractor
from scrapling.spiders.request import Request
from scrapling.spiders.templates.crawler import CrawlRule, CrawlSpider
from scrapling.core._types import (
    TYPE_CHECKING,
    Any,
    AsyncGenerator,
    Dict,
    List,
    Optional,
    Set,
    Union,
)

if TYPE_CHECKING:
    from scrapling.engines.toolbelt.custom import Response


__all__ = ["SiteToMarkdownSpider"]


class SiteToMarkdownSpider(CrawlSpider):
    """A spider that crawls a website and converts every page to clean, LLM-ready Markdown.

    Yields one item per page with `url`, `title`, and `markdown` keys, and when `output_dir` is set, it also
    writes each page to a Markdown file named after its URL. Every page link inside `allowed_domains` is followed
    by default; override `rules()` with your own `LinkExtractor` to narrow the crawl or drop URL patterns.

    `allowed_domains` is required so the crawl stays bound to the target website(s).

    :cvar css_selector: CSS selector to convert only the matching elements of each page.
    :cvar main_content_only: Convert only the content inside each page's `<body>` tag. Enabled by default.
    :cvar output_dir: When set, each page is also written to this directory as a Markdown file.
    :cvar max_pages: Maximum number of pages to convert. Requests already queued when the cap hits may still
        be fetched, but they aren't converted or followed. `0` disables the cap.
    """

    css_selector: Optional[str] = None
    main_content_only: bool = True
    output_dir: Optional[str] = None
    max_pages: int = 0

    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        if not self.allowed_domains:
            raise ValueError(
                f"{self.__class__.__name__} must set `allowed_domains` to bound the crawl to the target website(s)"
            )
        self._page_count = 0
        self._used_names: Set[str] = set()

    def rules(self) -> List[CrawlRule]:
        """Follow every page link. Override to narrow the crawl or drop URL patterns."""
        return [CrawlRule(LinkExtractor())]

    async def parse(self, response: "Response") -> AsyncGenerator[Union[Dict[str, Any], Request, None], None]:
        """Yield the page as a Markdown item, then follow its links through the crawl rules."""
        if self.max_pages and self._page_count >= self.max_pages:
            return
        self._page_count += 1
        yield {
            "url": response.url,
            "title": str(response.css("title::text").get() or "").strip(),
            "markdown": response.markdown(self.css_selector, self.main_content_only),
        }
        if not self.max_pages or self._page_count < self.max_pages:
            async for request in super().parse(response):
                yield request

    async def on_scraped_item(self, item: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Write the item to a Markdown file inside `output_dir` when it's set."""
        if self.output_dir:
            file = AsyncPath(self.output_dir) / f"{self._filename_for(item['url'])}.md"
            await file.parent.mkdir(parents=True, exist_ok=True)
            await file.write_text(item["markdown"], encoding="utf-8")
        return item

    def _filename_for(self, url: str) -> str:
        """Build a unique filesystem-safe name from the URL, suffixing a hash on collisions."""
        parsed = urlparse(url)
        name = re_sub(r"[^A-Za-z0-9._-]+", "-", f"{parsed.netloc}{parsed.path}".strip("/")).strip("-")[:150] or "index"
        if name in self._used_names:
            name = f"{name}-{sha1(url.encode(), usedforsecurity=False).hexdigest()[:8]}"
        self._used_names.add(name)
        return name
