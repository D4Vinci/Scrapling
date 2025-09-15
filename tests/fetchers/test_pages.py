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

        page_info.mark_finished()
        assert page_info.state == "finished"
        assert page_info.url == ""

        page_info.mark_error()
        assert page_info.state == "error"

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
        assert page_info.state == "ready"
        assert pool.pages_count == 1

    def test_add_page_limit_exceeded(self):
        """Test adding page when limit exceeded"""
        pool = PagePool(max_pages=1)

        # Add first page
        pool.add_page(Mock())

        # Try to add a second page
        with pytest.raises(RuntimeError):
            pool.add_page(Mock())

    def test_get_ready_page(self):
        """Test getting ready page"""
        pool = PagePool(max_pages=3)

        # Add pages
        page1 = pool.add_page(Mock())
        page2 = pool.add_page(Mock())

        # Mark them as finished
        page1.mark_finished()
        page2.mark_finished()

        # test
        pool.close_all_finished_pages()
        assert pool.pages_count == 0

    def test_cleanup_error_pages(self):
        """Test cleaning up error pages"""
        pool = PagePool(max_pages=3)

        # Add pages
        page1 = pool.add_page(Mock())
        _ = pool.add_page(Mock())
        page3 = pool.add_page(Mock())

        # Mark some as error
        page1.mark_error()
        page3.mark_error()

        assert pool.pages_count == 3

        pool.cleanup_error_pages()

        assert pool.pages_count == 1  # Only 2 should remain
