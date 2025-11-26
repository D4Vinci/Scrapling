import pytest
import pytest_httpbin

from scrapling import DynamicFetcher

DynamicFetcher.adaptive = True


@pytest_httpbin.use_class_based_httpbin
class TestDynamicFetcher:
    @pytest.fixture(scope="class")
    def fetcher(self):
        """Fixture to create a StealthyFetcher instance for the entire test class"""
        return DynamicFetcher

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
            {"disable_webgl": True, "hide_canvas": False},
            {"disable_webgl": False, "hide_canvas": True, "disable_resources": True},
            {"stealth": True},  # causes issues with GitHub Actions
            {"stealth": True, "real_chrome": True},  # causes issues with GitHub Actions
            {"wait_selector": "h1", "wait_selector_state": "attached"},
            {"wait_selector": "h1", "wait_selector_state": "visible"},
            {
                "google_search": True,
                "real_chrome": True,
                "wait": 10,
                "locale": "en-US",
                "extra_headers": {"ayo": ""},
                "useragent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:131.0) Gecko/20100101 Firefox/131.0",
                "cookies": [{"name": "test", "value": "123", "domain": "example.com", "path": "/"}],
                "network_idle": True,
                "selector_config": {"keep_comments": False, "keep_cdata": False},
            },
        ],
    )
    def test_properties(self, fetcher, kwargs):
        """Test if different arguments break the code or not"""
        response = fetcher.fetch(self.html_url, **kwargs)
        assert response.status == 200

    def test_cdp_url_invalid(self, fetcher):
        """Test if invalid CDP URLs raise appropriate exceptions"""
        with pytest.raises(TypeError):
            fetcher.fetch(self.html_url, cdp_url="blahblah")

        with pytest.raises(TypeError):
            fetcher.fetch(self.html_url, cdp_url="blahblah")

        with pytest.raises(Exception):
            fetcher.fetch(self.html_url, cdp_url="ws://blahblah")
