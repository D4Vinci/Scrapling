import pytest
import pytest_httpbin

from scrapling import PlayWrightFetcher


@pytest_httpbin.use_class_based_httpbin
class TestPlayWrightFetcher:

    @pytest.fixture(scope="class")
    def fetcher(self):
        """Fixture to create a StealthyFetcher instance for the entire test class"""
        return PlayWrightFetcher(auto_match=False)

    @pytest.fixture(autouse=True)
    def setup_urls(self, httpbin):
        """Fixture to set up URLs for testing"""
        self.status_200 = f'{httpbin.url}/status/200'
        self.status_404 = f'{httpbin.url}/status/404'
        self.status_501 = f'{httpbin.url}/status/501'
        self.basic_url = f'{httpbin.url}/get'
        self.html_url = f'{httpbin.url}/html'
        self.delayed_url = f'{httpbin.url}/delay/10'  # 10 Seconds delay response
        self.cookies_url = f"{httpbin.url}/cookies/set/test/value"

    def test_basic_fetch(self, fetcher):
        """Test doing basic fetch request with multiple statuses"""
        assert fetcher.fetch(self.status_200).status == 200
        # There's a bug with playwright makes it crashes if a URL returns status code 4xx/5xx without body, let's disable this till they reply to my issue report
        # assert fetcher.fetch(self.status_404).status == 404
        # assert fetcher.fetch(self.status_501).status == 501

    def test_networkidle(self, fetcher):
        """Test if waiting for `networkidle` make page does not finish loading or not"""
        assert fetcher.fetch(self.basic_url, network_idle=True).status == 200

    def test_blocking_resources(self, fetcher):
        """Test if blocking resources make page does not finish loading or not"""
        assert fetcher.fetch(self.basic_url, disable_resources=True).status == 200

    def test_waiting_selector(self, fetcher):
        """Test if waiting for a selector make page does not finish loading or not"""
        assert fetcher.fetch(self.html_url, wait_selector='h1').status == 200
        assert fetcher.fetch(self.html_url, wait_selector='h1', wait_selector_state='visible').status == 200

    def test_cookies_loading(self, fetcher):
        """Test if cookies are set after the request"""
        assert fetcher.fetch(self.cookies_url).cookies == {'test': 'value'}

    def test_automation(self, fetcher):
        """Test if automation break the code or not"""

        def scroll_page(page):
            page.mouse.wheel(10, 0)
            page.mouse.move(100, 400)
            page.mouse.up()
            return page

        assert fetcher.fetch(self.html_url, page_action=scroll_page).status == 200

    @pytest.mark.parametrize("kwargs", [
        {"disable_webgl": True, "hide_canvas": False},
        {"disable_webgl": False, "hide_canvas": True},
        # {"stealth": True}, # causes issues with Github Actions
        {"useragent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:131.0) Gecko/20100101 Firefox/131.0'},
        {"extra_headers": {'ayo': ''}}
    ])
    def test_properties(self, fetcher, kwargs):
        """Test if different arguments breaks the code or not"""
        response = fetcher.fetch(self.html_url, **kwargs)
        assert response.status == 200

    def test_cdp_url_invalid(self, fetcher):
        """Test if invalid CDP URLs raise appropriate exceptions"""
        with pytest.raises(ValueError):
            fetcher.fetch(self.html_url, cdp_url='blahblah')

        with pytest.raises(ValueError):
            fetcher.fetch(self.html_url, cdp_url='blahblah', nstbrowser_mode=True)

        with pytest.raises(Exception):
            fetcher.fetch(self.html_url, cdp_url='ws://blahblah')

    def test_infinite_timeout(self, fetcher, ):
        """Test if infinite timeout breaks the code or not"""
        response = fetcher.fetch(self.delayed_url, timeout=None)
        assert response.status == 200
