import pytest
import pytest_httpbin

from scrapling import Fetcher


@pytest_httpbin.use_class_based_httpbin
class TestFetcher:
    @pytest.fixture(scope="class")
    def fetcher(self):
        """Fixture to create a Fetcher instance for the entire test class"""
        return Fetcher(auto_match=False)

    @pytest.fixture(autouse=True)
    def setup_urls(self, httpbin):
        """Fixture to set up URLs for testing"""
        self.status_200 = f'{httpbin.url}/status/200'
        self.status_404 = f'{httpbin.url}/status/404'
        self.status_501 = f'{httpbin.url}/status/501'
        self.basic_url = f'{httpbin.url}/get'
        self.post_url = f'{httpbin.url}/post'
        self.put_url = f'{httpbin.url}/put'
        self.delete_url = f'{httpbin.url}/delete'
        self.html_url = f'{httpbin.url}/html'

    def test_basic_get(self, fetcher):
        """Test doing basic get request with multiple statuses"""
        assert fetcher.get(self.status_200).status == 200
        assert fetcher.get(self.status_404).status == 404
        assert fetcher.get(self.status_501).status == 501

    def test_get_properties(self, fetcher):
        """Test if different arguments with GET request breaks the code or not"""
        assert fetcher.get(self.status_200, stealthy_headers=True).status == 200
        assert fetcher.get(self.status_200, follow_redirects=True).status == 200
        assert fetcher.get(self.status_200, timeout=None).status == 200
        assert fetcher.get(
            self.status_200,
            stealthy_headers=True,
            follow_redirects=True,
            timeout=None
        ).status == 200

    def test_post_properties(self, fetcher):
        """Test if different arguments with POST request breaks the code or not"""
        assert fetcher.post(self.post_url, data={'key': 'value'}).status == 200
        assert fetcher.post(self.post_url, data={'key': 'value'}, stealthy_headers=True).status == 200
        assert fetcher.post(self.post_url, data={'key': 'value'}, follow_redirects=True).status == 200
        assert fetcher.post(self.post_url, data={'key': 'value'}, timeout=None).status == 200
        assert fetcher.post(
            self.post_url,
            data={'key': 'value'},
            stealthy_headers=True,
            follow_redirects=True,
            timeout=None
        ).status == 200

    def test_put_properties(self, fetcher):
        """Test if different arguments with PUT request breaks the code or not"""
        assert fetcher.put(self.put_url, data={'key': 'value'}).status == 200
        assert fetcher.put(self.put_url, data={'key': 'value'}, stealthy_headers=True).status == 200
        assert fetcher.put(self.put_url, data={'key': 'value'}, follow_redirects=True).status == 200
        assert fetcher.put(self.put_url, data={'key': 'value'}, timeout=None).status == 200
        assert fetcher.put(
            self.put_url,
            data={'key': 'value'},
            stealthy_headers=True,
            follow_redirects=True,
            timeout=None
        ).status == 200

    def test_delete_properties(self, fetcher):
        """Test if different arguments with DELETE request breaks the code or not"""
        assert fetcher.delete(self.delete_url, stealthy_headers=True).status == 200
        assert fetcher.delete(self.delete_url, follow_redirects=True).status == 200
        assert fetcher.delete(self.delete_url, timeout=None).status == 200
        assert fetcher.delete(
            self.delete_url,
            stealthy_headers=True,
            follow_redirects=True,
            timeout=None
        ).status == 200
