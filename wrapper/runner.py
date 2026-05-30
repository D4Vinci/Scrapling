"""
Pagination loop for the Scrapling wrapper.

Ties together the fetcher and the extractor: fetches the starting URL,
extracts data, follows "next page" links (if configured), and accumulates
results until the link is gone or max_pages is reached.

Public API:
    scrape(cfg, fetcher) -> ScrapeResult
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from wrapper.config import ScrapeConfig
from wrapper.extractor import extract_items, extract_top_level

if TYPE_CHECKING:
    from wrapper.fetcher import FetcherWrapper

log = logging.getLogger(__name__)


@dataclass
class ScrapeResult:
    items: list[dict] = field(default_factory=list)
    top_level: dict | None = None
    pages_scraped: int = 0


def scrape(cfg: ScrapeConfig, fetcher: "FetcherWrapper") -> ScrapeResult:
    """
    Fetch one or more pages according to *cfg* and return all extracted data.

    - cfg.items      → rows accumulated across every page into result.items
    - cfg.top_level  → extracted from the first page only into result.top_level
    - cfg.pagination → followed until the next-selector yields nothing or
                       max_pages is reached; absent means single-page only
    """
    result = ScrapeResult()
    url: str = cfg.url
    max_pages: int | None = cfg.pagination.max_pages if cfg.pagination else None

    while url:
        log.info("Fetching page %d: %s", result.pages_scraped + 1, url)
        page = fetcher.fetch(url)
        result.pages_scraped += 1

        if cfg.items:
            new_rows = extract_items(page, cfg.items)
            log.debug("  extracted %d item(s)", len(new_rows))
            result.items.extend(new_rows)

        if cfg.top_level and result.pages_scraped == 1:
            result.top_level = extract_top_level(page, cfg.top_level)

        url = _next_url(page, cfg, result.pages_scraped, max_pages)

    log.info(
        "Done. %d page(s) scraped, %d item(s) collected.",
        result.pages_scraped,
        len(result.items),
    )
    return result


# ---------------------------------------------------------------------------
# Internal
# ---------------------------------------------------------------------------

def _next_url(page, cfg: ScrapeConfig, pages_done: int, max_pages: int | None) -> str | None:
    """Return the absolute URL of the next page, or None to stop."""
    if cfg.pagination is None:
        return None

    if max_pages is not None and pages_done >= max_pages:
        log.debug("  max_pages=%d reached, stopping", max_pages)
        return None

    href = page.css(f"{cfg.pagination.next_selector}::attr(href)").get()
    if not href:
        log.debug("  next selector yielded nothing, stopping")
        return None

    return page.urljoin(str(href))
