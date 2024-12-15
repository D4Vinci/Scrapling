import asyncio
import unittest

import pytest_httpbin

from scrapling.fetchers import AsyncFetcher


@pytest_httpbin.use_class_based_httpbin
class TestAsyncFetcher(unittest.TestCase):
    def setUp(self):
        self.fetcher = AsyncFetcher(auto_match=True)
        url = self.httpbin.url
        self.status_200 = f'{url}/status/200'
        self.status_404 = f'{url}/status/404'
        self.status_501 = f'{url}/status/501'
        self.basic_url = f'{url}/get'
        self.post_url = f'{url}/post'
        self.put_url = f'{url}/put'
        self.delete_url = f'{url}/delete'
        self.html_url = f'{url}/html'

    async def async_test(self, coro):
        return await coro

    def test_basic_get(self):
        """Test doing basic get request with multiple statuses"""

        async def run_tests():
            self.assertEqual((await self.fetcher.get(self.status_200)).status, 200)
            self.assertEqual((await self.fetcher.get(self.status_404)).status, 404)
            self.assertEqual((await self.fetcher.get(self.status_501)).status, 501)

        asyncio.run(run_tests())

    def test_get_properties(self):
        """Test if different arguments with GET request breaks the code or not"""

        async def run_tests():
            self.assertEqual((await self.fetcher.get(self.status_200, stealthy_headers=True)).status, 200)
            self.assertEqual((await self.fetcher.get(self.status_200, follow_redirects=True)).status, 200)
            self.assertEqual((await self.fetcher.get(self.status_200, timeout=None)).status, 200)
            self.assertEqual(
                (await self.fetcher.get(self.status_200, stealthy_headers=True, follow_redirects=True, timeout=None)).status,
                200
            )

        asyncio.run(run_tests())

    def test_post_properties(self):
        """Test if different arguments with POST request breaks the code or not"""

        async def run_tests():
            self.assertEqual((await self.fetcher.post(self.post_url, data={'key': 'value'})).status, 200)
            self.assertEqual((await self.fetcher.post(self.post_url, data={'key': 'value'}, stealthy_headers=True)).status, 200)
            self.assertEqual((await self.fetcher.post(self.post_url, data={'key': 'value'}, follow_redirects=True)).status, 200)
            self.assertEqual((await self.fetcher.post(self.post_url, data={'key': 'value'}, timeout=None)).status, 200)
            self.assertEqual(
                (await self.fetcher.post(self.post_url, data={'key': 'value'}, stealthy_headers=True, follow_redirects=True, timeout=None)).status,
                200
            )

        asyncio.run(run_tests())

    def test_put_properties(self):
        """Test if different arguments with PUT request breaks the code or not"""

        async def run_tests():
            self.assertIn((await self.fetcher.put(self.put_url, data={'key': 'value'})).status, [200, 405])
            self.assertIn((await self.fetcher.put(self.put_url, data={'key': 'value'}, stealthy_headers=True)).status, [200, 405])
            self.assertIn((await self.fetcher.put(self.put_url, data={'key': 'value'}, follow_redirects=True)).status, [200, 405])
            self.assertIn((await self.fetcher.put(self.put_url, data={'key': 'value'}, timeout=None)).status, [200, 405])
            self.assertIn(
                (await self.fetcher.put(self.put_url, data={'key': 'value'}, stealthy_headers=True, follow_redirects=True, timeout=None)).status,
                [200, 405]
            )

        asyncio.run(run_tests())

    def test_delete_properties(self):
        """Test if different arguments with DELETE request breaks the code or not"""

        async def run_tests():
            self.assertEqual((await self.fetcher.delete(self.delete_url, stealthy_headers=True)).status, 200)
            self.assertEqual((await self.fetcher.delete(self.delete_url, follow_redirects=True)).status, 200)
            self.assertEqual((await self.fetcher.delete(self.delete_url, timeout=None)).status, 200)
            self.assertEqual(
                (await self.fetcher.delete(self.delete_url, stealthy_headers=True, follow_redirects=True, timeout=None)).status,
                200
            )

        asyncio.run(run_tests())
