from playwright._impl._errors import TimeoutError
import pytest
import pytest_httpbin

from scrapling import StealthyFetcher

StealthyFetcher.adaptive = True


@pytest_httpbin.use_class_based_httpbin
@pytest.mark.asyncio
class TestStealthyFetcher:
    @pytest.fixture(scope="class")
    def fetcher(self):
        return StealthyFetcher

    @pytest.fixture(scope="class")
    def urls(self, httpbin):
        url = httpbin.url
        return {
            "status_200": f"{url}/status/200",
            "status_404": f"{url}/status/404",
            "status_501": f"{url}/status/501",
            "basic_url": f"{url}/get",
            "html_url": f"{url}/html",
            "delayed_url": f"{url}/delay/10",  # 10 Seconds delay response
            "cookies_url": f"{url}/cookies/set/test/value"
        }

    async def test_basic_fetch(self, fetcher, urls):
        """Test doing a basic fetch request with multiple statuses"""
        assert (await fetcher.async_fetch(urls["status_200"])).status == 200
        # assert (await fetcher.async_fetch(urls["status_404"])).status == 404
        # assert (await fetcher.async_fetch(urls["status_501"])).status == 501

    async def test_cookies_loading(self, fetcher, urls):
        """Test if cookies are set after the request"""
        response = await fetcher.async_fetch(urls["cookies_url"])
        cookies = {response.cookies[0]['name']: response.cookies[0]['value']}
        assert cookies == {"test": "value"}

    async def test_automation(self, fetcher, urls):
        """Test if automation breaks the code or not"""

        async def scroll_page(page):
            await page.mouse.wheel(10, 0)
            await page.mouse.move(100, 400)
            await page.mouse.up()
            return page

        assert (
            await fetcher.async_fetch(urls["html_url"], page_action=scroll_page, humanize=True)
        ).status == 200

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
    async def test_properties(self, fetcher, urls, kwargs):
        """Test if different arguments break the code or not"""
        response = await fetcher.async_fetch(
            urls["html_url"],
            **kwargs
        )
        assert response.status == 200
