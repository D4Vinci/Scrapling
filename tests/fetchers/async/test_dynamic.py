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
    async def test_networkidle(self, fetcher, urls):
        """Test if waiting for `networkidle` make page does not finish loading or not"""
        response = await fetcher.async_fetch(urls["basic_url"], network_idle=True)
        assert response.status == 200

    @pytest.mark.asyncio
    async def test_blocking_resources(self, fetcher, urls):
        """Test if blocking resources make the page does not finish loading or not"""
        response = await fetcher.async_fetch(urls["basic_url"], disable_resources=True)
        assert response.status == 200

    @pytest.mark.asyncio
    async def test_waiting_selector(self, fetcher, urls):
        """Test if waiting for a selector make page does not finish loading or not"""
        response1 = await fetcher.async_fetch(urls["html_url"], wait_selector="h1")
        assert response1.status == 200

        response2 = await fetcher.async_fetch(
            urls["html_url"], wait_selector="h1", wait_selector_state="visible"
        )
        assert response2.status == 200

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
            {"disable_webgl": False, "hide_canvas": True},
            {"stealth": True},  # causes issues with GitHub Actions
            {
                "useragent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:131.0) Gecko/20100101 Firefox/131.0"
            },
            {"extra_headers": {"ayo": ""}},
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
                urls["html_url"], cdp_url="blahblah", nstbrowser_mode=True
            )

        with pytest.raises(Exception):
            await fetcher.async_fetch(urls["html_url"], cdp_url="ws://blahblah")

    @pytest.mark.asyncio
    async def test_infinite_timeout(self, fetcher, urls):
        """Test if infinite timeout breaks the code or not"""
        response = await fetcher.async_fetch(urls["delayed_url"], timeout=0)
        assert response.status == 200
