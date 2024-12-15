import pytest
import pytest_httpbin

from scrapling.fetchers import AsyncFetcher


@pytest_httpbin.use_class_based_httpbin
@pytest.mark.asyncio
class TestAsyncFetcher:
    @pytest.fixture(scope="class")
    def fetcher(self):
        return AsyncFetcher(auto_match=True)

    @pytest.fixture(scope="class")
    def urls(self, httpbin):
        return {
            'status_200': f'{httpbin.url}/status/200',
            'status_404': f'{httpbin.url}/status/404',
            'status_501': f'{httpbin.url}/status/501',
            'basic_url': f'{httpbin.url}/get',
            'post_url': f'{httpbin.url}/post',
            'put_url': f'{httpbin.url}/put',
            'delete_url': f'{httpbin.url}/delete',
            'html_url': f'{httpbin.url}/html'
        }

    async def test_basic_get(self, fetcher, urls):
        """Test doing basic get request with multiple statuses"""
        assert (await fetcher.get(urls['status_200'])).status == 200
        assert (await fetcher.get(urls['status_404'])).status == 404
        assert (await fetcher.get(urls['status_501'])).status == 501

    async def test_get_properties(self, fetcher, urls):
        """Test if different arguments with GET request breaks the code or not"""
        assert (await fetcher.get(urls['status_200'], stealthy_headers=True)).status == 200
        assert (await fetcher.get(urls['status_200'], follow_redirects=True)).status == 200
        assert (await fetcher.get(urls['status_200'], timeout=None)).status == 200
        assert (await fetcher.get(
            urls['status_200'],
            stealthy_headers=True,
            follow_redirects=True,
            timeout=None
        )).status == 200

    async def test_post_properties(self, fetcher, urls):
        """Test if different arguments with POST request breaks the code or not"""
        assert (await fetcher.post(urls['post_url'], data={'key': 'value'})).status == 200
        assert (await fetcher.post(urls['post_url'], data={'key': 'value'}, stealthy_headers=True)).status == 200
        assert (await fetcher.post(urls['post_url'], data={'key': 'value'}, follow_redirects=True)).status == 200
        assert (await fetcher.post(urls['post_url'], data={'key': 'value'}, timeout=None)).status == 200
        assert (await fetcher.post(
            urls['post_url'],
            data={'key': 'value'},
            stealthy_headers=True,
            follow_redirects=True,
            timeout=None
        )).status == 200

    async def test_put_properties(self, fetcher, urls):
        """Test if different arguments with PUT request breaks the code or not"""
        assert (await fetcher.put(urls['put_url'], data={'key': 'value'})).status in [200, 405]
        assert (await fetcher.put(urls['put_url'], data={'key': 'value'}, stealthy_headers=True)).status in [200, 405]
        assert (await fetcher.put(urls['put_url'], data={'key': 'value'}, follow_redirects=True)).status in [200, 405]
        assert (await fetcher.put(urls['put_url'], data={'key': 'value'}, timeout=None)).status in [200, 405]
        assert (await fetcher.put(
            urls['put_url'],
            data={'key': 'value'},
            stealthy_headers=True,
            follow_redirects=True,
            timeout=None
        )).status in [200, 405]

    async def test_delete_properties(self, fetcher, urls):
        """Test if different arguments with DELETE request breaks the code or not"""
        assert (await fetcher.delete(urls['delete_url'], stealthy_headers=True)).status == 200
        assert (await fetcher.delete(urls['delete_url'], follow_redirects=True)).status == 200
        assert (await fetcher.delete(urls['delete_url'], timeout=None)).status == 200
        assert (await fetcher.delete(
            urls['delete_url'],
            stealthy_headers=True,
            follow_redirects=True,
            timeout=None
        )).status == 200
