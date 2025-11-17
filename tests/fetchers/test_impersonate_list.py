"""Test suite for list-based impersonate parameter functionality."""
import pytest
import pytest_httpbin
from unittest.mock import patch, MagicMock

from scrapling import Fetcher
from scrapling.fetchers import FetcherSession
from scrapling.engines.static import _select_random_browser


class TestRandomBrowserSelection:
    """Test the random browser selection helper function."""

    def test_select_random_browser_with_single_string(self):
        """Test that single browser string is returned as-is."""
        result = _select_random_browser("chrome")
        assert result == "chrome"

    def test_select_random_browser_with_none(self):
        """Test that None is returned as-is."""
        result = _select_random_browser(None)
        assert result is None

    def test_select_random_browser_with_list(self):
        """Test that a browser is randomly selected from a list."""
        browsers = ["chrome", "firefox", "safari"]
        result = _select_random_browser(browsers)
        assert result in browsers

    def test_select_random_browser_with_empty_list(self):
        """Test that empty list returns None."""
        result = _select_random_browser([])
        assert result is None

    def test_select_random_browser_with_single_item_list(self):
        """Test that single-item list returns that item."""
        result = _select_random_browser(["chrome"])
        assert result == "chrome"


@pytest_httpbin.use_class_based_httpbin
class TestFetcherWithImpersonateList:
    """Test Fetcher with list-based impersonate parameter."""

    @pytest.fixture(autouse=True)
    def setup_urls(self, httpbin):
        """Fixture to set up URLs for testing."""
        self.basic_url = f"{httpbin.url}/get"

    def test_get_with_impersonate_list(self):
        """Test that GET request works with impersonate as a list."""
        browsers = ["chrome", "firefox"]
        response = Fetcher.get(self.basic_url, impersonate=browsers)
        assert response.status == 200

    def test_get_with_single_impersonate(self):
        """Test that GET request still works with single browser string."""
        response = Fetcher.get(self.basic_url, impersonate="chrome")
        assert response.status == 200

    def test_post_with_impersonate_list(self):
        """Test that POST request works with impersonate as a list."""
        browsers = ["chrome", "firefox"]
        post_url = self.basic_url.replace("/get", "/post")
        response = Fetcher.post(post_url, data={"key": "value"}, impersonate=browsers)
        assert response.status == 200

    def test_put_with_impersonate_list(self):
        """Test that PUT request works with impersonate as a list."""
        browsers = ["chrome", "safari"]
        put_url = self.basic_url.replace("/get", "/put")
        response = Fetcher.put(put_url, data={"key": "value"}, impersonate=browsers)
        assert response.status == 200

    def test_delete_with_impersonate_list(self):
        """Test that DELETE request works with impersonate as a list."""
        browsers = ["chrome", "edge"]
        delete_url = self.basic_url.replace("/get", "/delete")
        response = Fetcher.delete(delete_url, impersonate=browsers)
        assert response.status == 200


@pytest_httpbin.use_class_based_httpbin
class TestFetcherSessionWithImpersonateList:
    """Test FetcherSession with list-based impersonate parameter."""

    @pytest.fixture(autouse=True)
    def setup_urls(self, httpbin):
        """Fixture to set up URLs for testing."""
        self.basic_url = f"{httpbin.url}/get"

    def test_session_init_with_impersonate_list(self):
        """Test that FetcherSession can be initialized with impersonate as a list."""
        browsers = ["chrome", "firefox", "safari"]
        session = FetcherSession(impersonate=browsers)
        assert session._default_impersonate == browsers

    def test_session_request_with_impersonate_list(self):
        """Test that session request works with impersonate as a list."""
        browsers = ["chrome", "firefox"]
        with FetcherSession(impersonate=browsers) as session:
            response = session.get(self.basic_url)
            assert response.status == 200

    def test_session_multiple_requests_with_impersonate_list(self):
        """Test that multiple requests in a session work with impersonate list."""
        browsers = ["chrome110", "chrome120", "chrome131"]
        with FetcherSession(impersonate=browsers) as session:
            response1 = session.get(self.basic_url)
            response2 = session.get(self.basic_url)
            assert response1.status == 200
            assert response2.status == 200

    def test_session_request_level_impersonate_override(self):
        """Test that request-level impersonate overrides session-level."""
        session_browsers = ["chrome", "firefox"]
        request_browser = "safari"

        with FetcherSession(impersonate=session_browsers) as session:
            response = session.get(self.basic_url, impersonate=request_browser)
            assert response.status == 200

    def test_session_request_level_impersonate_list_override(self):
        """Test that request-level impersonate list overrides session-level."""
        session_browsers = ["chrome", "firefox"]
        request_browsers = ["safari", "edge"]

        with FetcherSession(impersonate=session_browsers) as session:
            response = session.get(self.basic_url, impersonate=request_browsers)
            assert response.status == 200


class TestImpersonateTypeValidation:
    """Test type validation for impersonate parameter."""

    def test_impersonate_accepts_string(self):
        """Test that impersonate accepts string type."""
        # This should not raise any type errors
        session = FetcherSession(impersonate="chrome")
        assert session._default_impersonate == "chrome"

    def test_impersonate_accepts_list(self):
        """Test that impersonate accepts list type."""
        # This should not raise any type errors
        browsers = ["chrome", "firefox"]
        session = FetcherSession(impersonate=browsers)
        assert session._default_impersonate == browsers

    def test_impersonate_accepts_none(self):
        """Test that impersonate accepts None."""
        # This should not raise any type errors
        session = FetcherSession(impersonate=None)
        assert session._default_impersonate is None
