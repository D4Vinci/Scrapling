"""Test cookie handling in browser sessions.

This module tests the improved cookie handling functionality that ensures
cookies are properly validated and added to browser contexts for authenticated
sessions.
"""

import pytest
import pytest_httpbin

from scrapling.engines._browsers._stealth import StealthySession
from scrapling.fetchers.stealth_chrome import StealthyFetcher


class TestCookieHandling:
    """Test cookie validation and injection into browser contexts."""

    @pytest.fixture(autouse=True)
    def setup_urls(self, httpbin):
        """Fixture to set up URLs for testing."""
        self.status_200 = f"{httpbin.url}/status/200"
        self.cookies_url = f"{httpbin.url}/cookies"
        self.set_cookies_url = f"{httpbin.url}/cookies/set/test/value"

    def test_basic_cookie_creation(self):
        """Test that session accepts and validates basic cookie format."""
        cookies = [
            {
                "name": "test_cookie",
                "value": "test_value",
                "domain": "httpbin.org",
                "path": "/",
                "secure": True,
                "httpOnly": True,
                "sameSite": "Lax"
            }
        ]

        with StealthySession(
            headless=True,
            disable_resources=True,
            cookies=cookies,
        ) as session:
            assert session.context is not None
            # Session should have been created without errors
            assert session._is_alive is True

    def test_multiple_cookies(self):
        """Test that session handles multiple cookies correctly."""
        cookies = [
            {"name": "cookie1", "value": "value1", "domain": "httpbin.org", "path": "/"},
            {"name": "cookie2", "value": "value2", "domain": "httpbin.org", "path": "/"},
            {"name": "cookie3", "value": "value3", "domain": "httpbin.org", "path": "/"},
        ]

        with StealthySession(
            headless=True,
            disable_resources=True,
            cookies=cookies,
        ) as session:
            assert session.context is not None
            assert session._is_alive is True

    def test_cookie_without_optional_fields(self):
        """Test that cookies work with only required fields."""
        cookies = [
            {"name": "minimal_cookie", "value": "minimal_value"}
        ]

        with StealthySession(
            headless=True,
            disable_resources=True,
            cookies=cookies,
        ) as session:
            assert session.context is not None
            assert session._is_alive is True

    def test_invalid_cookie_format_raises_error(self):
        """Test that invalid cookie format raises ValueError."""
        # Cookie without 'name' field
        invalid_cookies = [
            {"value": "only_value"}
        ]

        with pytest.raises(ValueError, match="must have 'name' and 'value' fields"):
            with StealthySession(
                headless=True,
                disable_resources=True,
                cookies=invalid_cookies,
            ) as session:
                pass

    def test_non_dict_cookie_raises_error(self):
        """Test that non-dictionary cookie raises ValueError."""
        invalid_cookies = ["not_a_dict"]

        with pytest.raises(ValueError, match="Cookie must be a dictionary"):
            with StealthySession(
                headless=True,
                disable_resources=True,
                cookies=invalid_cookies,
            ) as session:
                pass

    def test_empty_cookies_list(self):
        """Test that empty cookies list doesn't cause errors."""
        with StealthySession(
            headless=True,
            disable_resources=True,
            cookies=[],
        ) as session:
            assert session.context is not None
            assert session._is_alive is True

    def test_none_cookies(self):
        """Test that None cookies doesn't cause errors."""
        with StealthySession(
            headless=True,
            disable_resources=True,
            cookies=None,
        ) as session:
            assert session.context is not None
            assert session._is_alive is True

    def test_cookie_with_special_characters(self):
        """Test that cookies with special characters are handled correctly."""
        cookies = [
            {
                "name": "special_cookie",
                "value": "value=with&special?chars#here",
                "domain": "httpbin.org",
                "path": "/",
            }
        ]

        with StealthySession(
            headless=True,
            disable_resources=True,
            cookies=cookies,
        ) as session:
            assert session.context is not None
            assert session._is_alive is True

    def test_cookie_persistence_across_requests(self):
        """Test that cookies persist across multiple requests in the same session."""
        cookies = [
            {"name": "persistent_cookie", "value": "persistent_value", "domain": "httpbin.org", "path": "/"}
        ]

        with StealthySession(
            headless=True,
            disable_resources=True,
            cookies=cookies,
        ) as session:
            # Make first request
            response1 = session.fetch(self.status_200)
            assert response1.status == 200

            # Make second request in same session
            response2 = session.fetch(self.status_200)
            assert response2.status == 200

            # Session should still be alive
            assert session._is_alive is True

    def test_fetcher_with_cookies(self):
        """Test that StealthyFetcher accepts cookies properly."""
        cookies = [
            {"name": "fetcher_cookie", "value": "fetcher_value", "domain": "httpbin.org", "path": "/"}
        ]

        response = StealthyFetcher.fetch(
            self.status_200,
            headless=True,
            disable_resources=True,
            cookies=cookies,
        )

        assert response.status == 200

    def test_cookie_with_url_attribute(self):
        """Test cookie with URL attribute instead of domain."""
        cookies = [
            {"name": "url_cookie", "value": "url_value", "url": "http://httpbin.org/"}
        ]

        with StealthySession(
            headless=True,
            disable_resources=True,
            cookies=cookies,
        ) as session:
            assert session.context is not None
            assert session._is_alive is True

    def test_cookie_with_expires_attribute(self):
        """Test cookie with expires timestamp."""
        import time
        cookies = [
            {
                "name": "expires_cookie",
                "value": "expires_value",
                "domain": "httpbin.org",
                "path": "/",
                "expires": time.time() + 3600  # Expires in 1 hour
            }
        ]

        with StealthySession(
            headless=True,
            disable_resources=True,
            cookies=cookies,
        ) as session:
            assert session.context is not None
            assert session._is_alive is True

    def test_mixed_valid_and_invalid_cookies(self):
        """Test that session handles mixed valid/invalid cookies appropriately."""
        # First cookie is valid, second is invalid (missing 'value')
        mixed_cookies = [
            {"name": "valid_cookie", "value": "valid_value", "domain": "httpbin.org", "path": "/"},
            {"name": "invalid_cookie", "domain": "httpbin.org", "path": "/"},  # Missing 'value'
        ]

        # Should raise ValueError for the invalid cookie
        with pytest.raises(ValueError, match="must have 'name' and 'value' fields"):
            with StealthySession(
                headless=True,
                disable_resources=True,
                cookies=mixed_cookies,
            ) as session:
                pass

    def test_samesite_values(self):
        """Test different SameSite attribute values."""
        for samesite_value in ["Lax", "None", "Strict"]:
            cookies = [
                {
                    "name": f"cookie_{samesite_value}",
                    "value": f"value_{samesite_value}",
                    "domain": "httpbin.org",
                    "path": "/",
                    "sameSite": samesite_value
                }
            ]

            with StealthySession(
                headless=True,
                disable_resources=True,
                cookies=cookies,
            ) as session:
                assert session.context is not None
                assert session._is_alive is True
