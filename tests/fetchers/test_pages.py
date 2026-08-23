import pytest
from unittest.mock import Mock
from scrapling.engines._browsers._page import PageInfo, PagePool


class TestPageInfo:
    """Test PageInfo functionality"""

    def test_page_info_creation(self):
        """Test PageInfo creation"""
        mock_page = Mock()
        page_info = PageInfo(mock_page, "ready", "https://example.com")

        assert page_info.page == mock_page
        assert page_info.state == "ready"
        assert page_info.url == "https://example.com"

    def test_page_info_marking(self):
        """Test marking page"""
        mock_page = Mock()
        page_info = PageInfo(mock_page, "ready", None)

        page_info.mark_busy("https://example.com")
        assert page_info.state == "busy"
        assert page_info.url == "https://example.com"

        page_info.mark_error()
        assert page_info.state == "error"

        page_info.mark_ready()
        assert page_info.state == "ready"
        assert page_info.url == ""

    def test_page_info_equality(self):
        """Test PageInfo equality comparison"""
        mock_page1 = Mock()
        mock_page2 = Mock()

        page_info1 = PageInfo(mock_page1, "ready", None)
        page_info2 = PageInfo(mock_page1, "busy", None)  # Same page, different state
        page_info3 = PageInfo(mock_page2, "ready", None)  # Different page

        assert page_info1 == page_info2  # Same page
        assert page_info1 != page_info3  # Different page
        assert page_info1 != "not a page info"  # Different type

    def test_page_info_repr(self):
        """Test PageInfo string representation"""
        mock_page = Mock()
        page_info = PageInfo(mock_page, "ready", "https://example.com")

        repr_str = repr(page_info)
        assert "ready" in repr_str
        assert "https://example.com" in repr_str


class TestPagePool:
    """Test PagePool functionality"""

    def test_page_pool_creation(self):
        """Test PagePool creation"""
        pool = PagePool(max_pages=5)

        assert pool.max_pages == 5
        assert pool.pages_count == 0
        assert pool.busy_count == 0

    def test_add_page(self):
        """Test adding page to pool"""
        pool = PagePool(max_pages=2)
        mock_page = Mock()

        page_info = pool.add_page(mock_page)

        assert isinstance(page_info, PageInfo)
        assert page_info.page == mock_page
        assert page_info.state == "busy", "a new page is busy for the request that opened it"
        assert pool.pages_count == 1
        assert pool.busy_count == 1

    def test_add_page_limit_exceeded(self):
        """Test adding page when limit exceeded"""
        pool = PagePool(max_pages=1)

        # Add first page
        pool.add_page(Mock())

        # Try to add a second page
        with pytest.raises(RuntimeError):
            pool.add_page(Mock())

    def test_proxy_rotation_pool_leak(self):
        pool = PagePool(max_pages=1)
        page_info = pool.add_page(Mock())
        assert pool.pages_count == 1
        pool.remove_page(page_info)
        assert pool.pages_count == 0
        pool.add_page(Mock())
        assert pool.pages_count == 1

    def test_get_ready_page_skips_busy_and_error_pages(self):
        pool = PagePool(max_pages=3)
        busy = pool.add_page(Mock())
        errored = pool.add_page(Mock())
        errored.mark_error()
        assert pool.get_ready_page() is None

        busy.mark_ready()
        taken = pool.get_ready_page()
        assert taken is busy
        assert taken.state == "busy", "the returned page is reserved for the caller"
        assert pool.get_ready_page() is None

    def test_remove_page_ignores_unknown_pages(self):
        pool = PagePool(max_pages=2)
        page_info = pool.add_page(Mock())
        pool.remove_page(page_info)
        pool.remove_page(page_info)
        assert pool.pages_count == 0

    def test_clear_returns_every_page_and_empties_the_pool(self):
        pool = PagePool(max_pages=3)
        pages = [pool.add_page(Mock()) for _ in range(3)]
        pages[1].mark_ready()

        cleared = pool.clear()

        assert cleared == pages
        assert pool.pages_count == 0
        pool.add_page(Mock())
        assert pool.pages_count == 1
