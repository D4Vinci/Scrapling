import unittest
import pytest_httpbin

from scrapling import StealthyFetcher


@pytest_httpbin.use_class_based_httpbin
# @pytest_httpbin.use_class_based_httpbin_secure
class TestStealthyFetcher(unittest.TestCase):
    def setUp(self):
        self.fetcher = StealthyFetcher(auto_match=False)
        url = self.httpbin.url
        self.status_200 = f'{url}/status/200'
        self.status_404 = f'{url}/status/404'
        self.status_501 = f'{url}/status/501'
        self.basic_url = f'{url}/get'
        self.html_url = f'{url}/html'
        self.delayed_url = f'{url}/delay/10'  # 10 Seconds delay response
        self.cookies_url = f"{url}/cookies/set/test/value"

    def test_basic_fetch(self):
        """Test doing basic fetch request with multiple statuses"""
        self.assertEqual(self.fetcher.fetch(self.status_200).status, 200)
        self.assertEqual(self.fetcher.fetch(self.status_404).status, 404)
        self.assertEqual(self.fetcher.fetch(self.status_501).status, 501)

    def test_networkidle(self):
        """Test if waiting for `networkidle` make page does not finish loading or not"""
        self.assertEqual(self.fetcher.fetch(self.basic_url, network_idle=True).status, 200)

    def test_blocking_resources(self):
        """Test if blocking resources make page does not finish loading or not"""
        self.assertEqual(self.fetcher.fetch(self.basic_url, block_images=True).status, 200)
        self.assertEqual(self.fetcher.fetch(self.basic_url, disable_resources=True).status, 200)

    def test_waiting_selector(self):
        """Test if waiting for a selector make page does not finish loading or not"""
        self.assertEqual(self.fetcher.fetch(self.html_url, wait_selector='h1').status, 200)
        self.assertEqual(self.fetcher.fetch(self.html_url, wait_selector='h1', wait_selector_state='visible').status, 200)

    def test_cookies_loading(self):
        """Test if cookies are set after the request"""
        self.assertEqual(self.fetcher.fetch(self.cookies_url).cookies, {'test': 'value'})

    def test_automation(self):
        """Test if automation break the code or not"""
        def scroll_page(page):
            page.mouse.wheel(10, 0)
            page.mouse.move(100, 400)
            page.mouse.up()
            return page

        self.assertEqual(self.fetcher.fetch(self.html_url, page_action=scroll_page).status, 200)

    def test_properties(self):
        """Test if different arguments breaks the code or not"""
        self.assertEqual(self.fetcher.fetch(self.html_url, block_webrtc=True, allow_webgl=True).status, 200)
        self.assertEqual(self.fetcher.fetch(self.html_url, block_webrtc=False, allow_webgl=True).status, 200)
        self.assertEqual(self.fetcher.fetch(self.html_url, block_webrtc=True, allow_webgl=False).status, 200)
        self.assertEqual(self.fetcher.fetch(self.html_url, extra_headers={'ayo': ''}, os_randomize=True).status, 200)

    def test_infinite_timeout(self):
        """Test if infinite timeout breaks the code or not"""
        self.assertEqual(self.fetcher.fetch(self.delayed_url, timeout=None).status, 200)
