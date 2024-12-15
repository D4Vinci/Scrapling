import pytest
import pytest_httpbin

from scrapling import StealthyFetcher


@pytest_httpbin.use_class_based_httpbin
@pytest.mark.asyncio
class TestStealthyFetcher:
    @pytest.fixture(scope="class")
    def fetcher(self):
        return StealthyFetcher(auto_match=False)

    @pytest.fixture(scope="class")
    def urls(self, httpbin):
        url = httpbin.url
        return {
            'status_200': f'{url}/status/200',
            'status_404': f'{url}/status/404',
            'status_501': f'{url}/status/501',
            'basic_url': f'{url}/get',
            'html_url': f'{url}/html',
            'delayed_url': f'{url}/delay/10',  # 10 Seconds delay response
            'cookies_url': f"{url}/cookies/set/test/value"
        }

    async def test_basic_fetch(self, fetcher, urls):
        """Test doing basic fetch request with multiple statuses"""
        assert (await fetcher.async_fetch(urls['status_200'])).status == 200
        assert (await fetcher.async_fetch(urls['status_404'])).status == 404
        assert (await fetcher.async_fetch(urls['status_501'])).status == 501

    async def test_networkidle(self, fetcher, urls):
        """Test if waiting for `networkidle` make page does not finish loading or not"""
        assert (await fetcher.async_fetch(urls['basic_url'], network_idle=True)).status == 200

    async def test_blocking_resources(self, fetcher, urls):
        """Test if blocking resources make page does not finish loading or not"""
        assert (await fetcher.async_fetch(urls['basic_url'], block_images=True)).status == 200
        assert (await fetcher.async_fetch(urls['basic_url'], disable_resources=True)).status == 200

    async def test_waiting_selector(self, fetcher, urls):
        """Test if waiting for a selector make page does not finish loading or not"""
        assert (await fetcher.async_fetch(urls['html_url'], wait_selector='h1')).status == 200
        assert (await fetcher.async_fetch(
            urls['html_url'],
            wait_selector='h1',
            wait_selector_state='visible'
        )).status == 200

    async def test_cookies_loading(self, fetcher, urls):
        """Test if cookies are set after the request"""
        response = await fetcher.async_fetch(urls['cookies_url'])
        assert response.cookies == {'test': 'value'}

    async def test_automation(self, fetcher, urls):
        """Test if automation break the code or not"""

        async def scroll_page(page):
            await page.mouse.wheel(10, 0)
            await page.mouse.move(100, 400)
            await page.mouse.up()
            return page

        assert (await fetcher.async_fetch(urls['html_url'], page_action=scroll_page)).status == 200

    async def test_properties(self, fetcher, urls):
        """Test if different arguments breaks the code or not"""
        assert (await fetcher.async_fetch(
            urls['html_url'],
            block_webrtc=True,
            allow_webgl=True
        )).status == 200

        assert (await fetcher.async_fetch(
            urls['html_url'],
            block_webrtc=False,
            allow_webgl=True
        )).status == 200

        assert (await fetcher.async_fetch(
            urls['html_url'],
            block_webrtc=True,
            allow_webgl=False
        )).status == 200

        assert (await fetcher.async_fetch(
            urls['html_url'],
            extra_headers={'ayo': ''},
            os_randomize=True
        )).status == 200

    async def test_infinite_timeout(self, fetcher, urls):
        """Test if infinite timeout breaks the code or not"""
        assert (await fetcher.async_fetch(urls['delayed_url'], timeout=None)).status == 200
