import pytest
import pytest_httpbin

from scrapling import DynamicFetcher

DynamicFetcher.adaptive = True


@pytest_httpbin.use_class_based_httpbin
class TestDynamicFetcherAsync:
    @pytest.fixture
    def fetcher(self):
        return DynamicFetcher

    @pytest.fixture
    def urls(self, httpbin):
        return {
            "status_200": f"{httpbin.url}/status/200",
            "status_404": f"{httpbin.url}/status/404",
            "status_501": f"{httpbin.url}/status/501",
            "basic_url": f"{httpbin.url}/get",
            "html_url": f"{httpbin.url}/html",
            "delayed_url": f"{httpbin.url}/delay/10",
            "cookies_url": f"{httpbin.url}/cookies/set/test/value",
        }

    @pytest.mark.asyncio
    async def test_basic_fetch(self, fetcher, urls):
        """Test doing a basic fetch request with multiple statuses"""
        response = await fetcher.async_fetch(urls["status_200"])
        assert response.status == 200

    @pytest.mark.asyncio
    async def test_cookies_loading(self, fetcher, urls):
        """Test if cookies are set after the request"""
        response = await fetcher.async_fetch(urls["cookies_url"])
        cookies = {response.cookies[0]['name']: response.cookies[0]['value']}
        assert cookies == {"test": "value"}

    @pytest.mark.asyncio
    async def test_automation(self, fetcher, urls):
        """Test if automation breaks the code or not"""

        async def scroll_page(page):
            await page.mouse.wheel(10, 0)
            await page.mouse.move(100, 400)
            await page.mouse.up()
            return page

        response = await fetcher.async_fetch(urls["html_url"], page_action=scroll_page)
        assert response.status == 200

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
                "custom_config": {"keep_comments": False, "keep_cdata": False},
            },
        ],
    )
    @pytest.mark.asyncio
    async def test_properties(self, fetcher, urls, kwargs):
        """Test if different arguments break the code or not"""
        response = await fetcher.async_fetch(urls["html_url"], **kwargs)
        assert response.status == 200

    @pytest.mark.asyncio
    async def test_cdp_url_invalid(self, fetcher, urls):
        """Test if invalid CDP URLs raise appropriate exceptions"""
        with pytest.raises(TypeError):
            await fetcher.async_fetch(urls["html_url"], cdp_url="blahblah")

        with pytest.raises(TypeError):
            await fetcher.async_fetch(
                urls["html_url"], cdp_url="blahblah"
            )

        with pytest.raises(Exception):
            await fetcher.async_fetch(urls["html_url"], cdp_url="ws://blahblah")
