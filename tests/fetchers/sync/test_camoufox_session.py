import re
import pytest
import pytest_httpbin

from scrapling.engines._browsers._camoufox import StealthySession, __CF_PATTERN__


class TestCamoufoxConstants:
    """Test Camoufox constants and patterns"""

    def test_cf_pattern_regex(self):
        """Test __CF_PATTERN__ regex compilation"""

        assert isinstance(__CF_PATTERN__, re.Pattern)

        # Test matching URLs
        test_urls = [
            "https://challenges.cloudflare.com/cdn-cgi/challenge-platform/h/123456",
            "https://challenges.cloudflare.com/cdn-cgi/challenge-platform/orchestrate/jsch/v1",
            "http://challenges.cloudflare.com/cdn-cgi/challenge-platform/scripts/abc"
        ]

        for url in test_urls:
            assert __CF_PATTERN__.search(url) is not None

        # Test non-matching URLs
        non_matching_urls = [
            "https://example.com/challenge",
            "https://cloudflare.com/something",
            "https://challenges.cloudflare.com/other-path"
        ]

        for url in non_matching_urls:
            assert __CF_PATTERN__.search(url) is None


@pytest_httpbin.use_class_based_httpbin
class TestStealthySession:

    """All the code is tested in the async version tests, so no need to repeat it here. The async class inherits from this one."""
    @pytest.fixture(autouse=True)
    def setup_urls(self, httpbin):
        """Fixture to set up URLs for testing"""
        self.status_200 = f"{httpbin.url}/status/200"
        self.status_404 = f"{httpbin.url}/status/404"
        self.status_501 = f"{httpbin.url}/status/501"
        self.basic_url = f"{httpbin.url}/get"
        self.html_url = f"{httpbin.url}/html"
        self.delayed_url = f"{httpbin.url}/delay/10"  # 10 Seconds delay response
        self.cookies_url = f"{httpbin.url}/cookies/set/test/value"

    def test_session_creation(self):
        """Test if the session is created correctly"""

        with StealthySession(
            headless=True,
            block_images=True,
            disable_resources=True,
            solve_cloudflare=True,
            wait=1000,
            timeout=60000,
            cookies=[{"name": "test", "value": "123", "domain": "example.com", "path": "/"}],
        ) as session:

            assert session.max_pages == 1
            assert session.headless is True
            assert session.block_images is True
            assert session.disable_resources is True
            assert session.solve_cloudflare is True
            assert session.wait == 1000
            assert session.timeout == 60000
            assert session.context is not None

            # Test Cloudflare detection
            for cloudflare_type in ('managed', 'interactive', 'non-interactive'):
                page_content = f"""
                <html>
                    <script>
                        cType: '{cloudflare_type}'
                    </script>
                </html>
                """
                result = session._detect_cloudflare(page_content)
                assert result == cloudflare_type

            page_content = """
            <html>
                <body>
                    <p>Regular page content</p>
                </body>
            </html>
            """

            result = StealthySession._detect_cloudflare(page_content)
            assert result is None
            assert session.fetch(self.status_200).status == 200
