from threading import RLock
from dataclasses import dataclass

from playwright.sync_api._generated import Page as SyncPage
from playwright.async_api._generated import Page as AsyncPage

from scrapling.core._types import Optional, List, Literal, overload, TypeVar, Generic, cast

PageState = Literal["ready", "busy", "error"]  # States that a page can be in
PageType = TypeVar("PageType", SyncPage, AsyncPage)


@dataclass
class PageInfo(Generic[PageType]):
    """Information about the page and its current state"""

    __slots__ = ("page", "state", "url")
    page: PageType
    state: PageState
    url: Optional[str]

    def mark_busy(self, url: str = ""):
        """Mark the page as busy"""
        self.state = "busy"
        self.url = url

    def mark_ready(self):
        """Mark the page as ready to be reused by the next request"""
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
        self.pages: List[PageInfo[SyncPage] | PageInfo[AsyncPage]] = []
        self._lock = RLock()

    @overload
    def add_page(self, page: SyncPage) -> PageInfo[SyncPage]: ...

    @overload
    def add_page(self, page: AsyncPage) -> PageInfo[AsyncPage]: ...

    def add_page(self, page: SyncPage | AsyncPage) -> PageInfo[SyncPage] | PageInfo[AsyncPage]:
        """Add a new page to the pool, marked busy for the request that created it"""
        with self._lock:
            if len(self.pages) >= self.max_pages:
                raise RuntimeError(f"Maximum page limit ({self.max_pages}) reached")

            if isinstance(page, AsyncPage):
                page_info: PageInfo[SyncPage] | PageInfo[AsyncPage] = cast(
                    PageInfo[AsyncPage], PageInfo(page, "busy", "")
                )
            else:
                page_info = cast(PageInfo[SyncPage], PageInfo(page, "busy", ""))

            self.pages.append(page_info)
            return page_info

    def get_ready_page(self) -> Optional[PageInfo[SyncPage] | PageInfo[AsyncPage]]:
        """Take the first ready page out of the pool's free pages, marking it busy, or return None"""
        with self._lock:
            for page_info in self.pages:
                if page_info.state == "ready":
                    page_info.mark_busy()
                    return page_info
            return None

    def remove_page(self, page_info: PageInfo[SyncPage] | PageInfo[AsyncPage]):
        """Forget a page, whether it's still in the pool or not"""
        with self._lock:
            if page_info in self.pages:
                self.pages.remove(page_info)

    def clear(self) -> List[PageInfo[SyncPage] | PageInfo[AsyncPage]]:
        """Forget every page and return them so the caller can close them"""
        with self._lock:
            pages, self.pages = self.pages, []
            return pages

    @property
    def pages_count(self) -> int:
        """Get the total number of pages"""
        return len(self.pages)

    @property
    def busy_count(self) -> int:
        """Get the number of busy pages"""
        with self._lock:
            return sum(1 for p in self.pages if p.state == "busy")
