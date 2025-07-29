from threading import RLock
from dataclasses import dataclass

from playwright.sync_api import Page as SyncPage
from playwright.async_api import Page as AsyncPage

from scrapling.core._types import Optional, List, Literal

PageState = Literal["ready", "busy", "error"]  # States that a page can be in


@dataclass
class PageInfo:
    """Information about the page and its current state"""

    __slots__ = ("page", "state", "url")
    page: SyncPage | AsyncPage
    state: PageState
    url: Optional[str]

    def mark_busy(self, url: str = ""):
        """Mark the page as busy"""
        self.state = "busy"
        self.url = url

    def mark_ready(self):
        """Mark the page as ready for new requests"""
        self.state = "ready"
        self.url = ""

    def mark_error(self):
        """Mark the page as having an error"""
        self.state = "error"

    def __repr__(self):
        return f'Page(URL="{self.url!r}", state={self.state!r})'

    def __eq__(self, other_page):
        """Comparing this page to another page object."""
        if other_page.__class__ is not self.__class__:
            return NotImplemented
        return self.page == other_page.page


class PagePool:
    """Manages a pool of browser pages/tabs with state tracking"""

    __slots__ = ("max_pages", "pages", "_lock")

    def __init__(self, max_pages: int = 5):
        self.max_pages = max_pages
        self.pages: List[PageInfo] = []
        self._lock = RLock()

    def add_page(self, page: SyncPage | AsyncPage) -> PageInfo:
        """Add a new page to the pool"""
        with self._lock:
            if len(self.pages) >= self.max_pages:
                raise RuntimeError(f"Maximum page limit ({self.max_pages}) reached")

            page_info = PageInfo(page, "ready", "")
            self.pages.append(page_info)
            return page_info

    def get_ready_page(self) -> Optional[PageInfo]:
        """Get a page that's ready for use"""
        with self._lock:
            for page_info in self.pages:
                if page_info.state == "ready":
                    return page_info
            return None

    @property
    def pages_count(self) -> int:
        """Get the total number of pages"""
        return len(self.pages)

    @property
    def ready_count(self) -> int:
        """Get the number of ready pages"""
        with self._lock:
            return sum(1 for p in self.pages if p.state == "ready")

    @property
    def busy_count(self) -> int:
        """Get the number of busy pages"""
        with self._lock:
            return sum(1 for p in self.pages if p.state == "busy")

    def cleanup_error_pages(self):
        """Remove pages in error state"""
        with self._lock:
            self.pages = [p for p in self.pages if p.state != "error"]
