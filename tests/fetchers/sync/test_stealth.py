import pytest
import pytest_httpbin

from scrapling import StealthyFetcher
StealthyFetcher.adaptive = True


@pytest_httpbin.use_class_based_httpbin
class TestStealthyFetcher:
    @pytest.fixture(scope="class")
    def fetcher(self):
        """Fixture to create a StealthyFetcher instance for the entire test class"""
        return StealthyFetcher

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

    def test_basic_fetch(self, fetcher):
        """Test doing a basic fetch request with multiple statuses"""
        assert fetcher.fetch(self.status_200).status == 200
        # There's a bug with playwright makes it crashes if a URL returns status code 4xx/5xx without body, let's disable this till they reply to my issue report
        # assert fetcher.fetch(self.status_404).status == 404
        # assert fetcher.fetch(self.status_501).status == 501

    def test_cookies_loading(self, fetcher):
        """Test if cookies are set after the request"""
        response = fetcher.fetch(self.cookies_url)
        cookies = {response.cookies[0]['name']: response.cookies[0]['value']}
        assert cookies == {"test": "value"}

    def test_automation(self, fetcher):
        """Test if automation breaks the code or not"""

        def scroll_page(page):
            page.mouse.wheel(10, 0)
            page.mouse.move(100, 400)
            page.mouse.up()
            return page

        assert fetcher.fetch(self.html_url, page_action=scroll_page).status == 200

    @pytest.mark.parametrize(
        "kwargs",
        [
            {"block_webrtc": True, "allow_webgl": True, "disable_ads": False},
            {"block_webrtc": False, "allow_webgl": True, "block_images": True},
            {"block_webrtc": True, "allow_webgl": False, "disable_resources": True},
            {"block_images": True, "disable_resources": True, },
            {"wait_selector": "h1", "wait_selector_state": "attached"},
            {"wait_selector": "h1", "wait_selector_state": "visible"},
            {
                "network_idle": True,
                "wait": 10,
                "timeout": 30_000,
                "cookies": [{"name": "test", "value": "123", "domain": "example.com", "path": "/"}],
                "google_search": True,
                "extra_headers": {"ayo": ""},
                "os_randomize": True,
                "disable_ads": True,
                # "geoip": True,
                "selector_config": {"keep_comments": False, "keep_cdata": False},
                "additional_args": {},
            },
        ],
    )
    def test_properties(self, fetcher, kwargs):
        """Test if different arguments break the code or not"""
        response = fetcher.fetch(
            self.html_url,
            **kwargs
        )
        assert response.status == 200
