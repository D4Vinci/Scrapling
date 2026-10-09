import pytest
import pytest_httpbin

from scrapling import Fetcher
from scrapling.fetchers import FetcherSession

Fetcher.adaptive = True


@pytest.fixture
def _reset_fetcher_config():
    """Snapshot and restore the mutable class-level parser config around a test."""
    snapshot = {k: getattr(Fetcher, k) for k in Fetcher.parser_keywords}
    try:
        yield
    finally:
        for k, v in snapshot.items():
            setattr(Fetcher, k, v)


@pytest_httpbin.use_class_based_httpbin
class TestFetcher:
    @pytest.fixture(scope="class")
    def fetcher(self):
        """Fixture to create a Fetcher instance for the entire test class"""
        return Fetcher

    @pytest.fixture(autouse=True)
    def setup_urls(self, httpbin):
        """Fixture to set up URLs for testing"""
        self.status_200 = f"{httpbin.url}/status/200"
        self.status_404 = f"{httpbin.url}/status/404"
        self.status_501 = f"{httpbin.url}/status/501"
        self.basic_url = f"{httpbin.url}/get"
        self.post_url = f"{httpbin.url}/post"
        self.put_url = f"{httpbin.url}/put"
        self.delete_url = f"{httpbin.url}/delete"
        self.html_url = f"{httpbin.url}/html"

    def test_basic_get(self, fetcher):
        """Test doing basic get request with multiple statuses"""
        assert fetcher.get(self.status_200).status == 200
        assert fetcher.get(self.status_404).status == 404
        assert fetcher.get(self.status_501).status == 501

    def test_get_properties(self, fetcher):
        """Test if different arguments with the GET request break the code or not"""
        assert fetcher.get(self.status_200, stealthy_headers=True).status == 200
        assert fetcher.get(self.status_200, follow_redirects=True).status == 200
        assert fetcher.get(self.status_200, timeout=None).status == 200
        assert (
            fetcher.get(
                self.status_200,
                stealthy_headers=True,
                follow_redirects=True,
                timeout=None,
            ).status
            == 200
        )

    def test_post_properties(self, fetcher):
        """Test if different arguments with the POST request break the code or not"""
        assert fetcher.post(self.post_url, data={"key": "value"}).status == 200
        assert (
            fetcher.post(
                self.post_url, data={"key": "value"}, stealthy_headers=True
            ).status
            == 200
        )
        assert (
            fetcher.post(
                self.post_url, data={"key": "value"}, follow_redirects=True
            ).status
            == 200
        )
        assert (
            fetcher.post(self.post_url, data={"key": "value"}, timeout=None).status
            == 200
        )
        assert (
            fetcher.post(
                self.post_url,
                data={"key": "value"},
                stealthy_headers=True,
                follow_redirects=True,
                timeout=None,
            ).status
            == 200
        )

    def test_put_properties(self, fetcher):
        """Test if different arguments with a PUT request break the code or not"""
        assert fetcher.put(self.put_url, data={"key": "value"}).status == 200
        assert (
            fetcher.put(
                self.put_url, data={"key": "value"}, stealthy_headers=True
            ).status
            == 200
        )
        assert (
            fetcher.put(
                self.put_url, data={"key": "value"}, follow_redirects=True
            ).status
            == 200
        )
        assert (
            fetcher.put(self.put_url, data={"key": "value"}, timeout=None).status == 200
        )
        assert (
            fetcher.put(
                self.put_url,
                data={"key": "value"},
                stealthy_headers=True,
                follow_redirects=True,
                timeout=None,
            ).status
            == 200
        )

    def test_delete_properties(self, fetcher):
        """Test if different arguments with the DELETE request break the code or not"""
        assert fetcher.delete(self.delete_url, stealthy_headers=True).status == 200
        assert fetcher.delete(self.delete_url, follow_redirects=True).status == 200
        assert fetcher.delete(self.delete_url, timeout=None).status == 200
        assert (
            fetcher.delete(
                self.delete_url,
                stealthy_headers=True,
                follow_redirects=True,
                timeout=None,
            ).status
            == 200
        )

    def test_configure_propagates_to_response(self, fetcher, _reset_fetcher_config):
        """`Fetcher.configure()` must reach the Response's Selector on the HTTP path."""
        Fetcher.configure(adaptive=False, adaptive_domain="")
        baseline = fetcher.get(self.html_url)
        assert baseline._storage is None

        Fetcher.configure(adaptive=True, adaptive_domain="configured.test")
        configured = fetcher.get(self.html_url)
        assert configured._storage is not None
        assert configured.url == "configured.test"

    def test_selector_config_overrides_configure(self, fetcher, _reset_fetcher_config):
        """A per-request ``selector_config`` overrides the class-level configure()."""
        Fetcher.configure(adaptive=True, adaptive_domain="from-configure.test")
        response = fetcher.get(
            self.html_url,
            selector_config={"adaptive_domain": "from-request.test"},
        )
        assert response._storage is not None
        assert response.url == "from-request.test"

    def test_retries_below_one_still_performs_the_request(self, fetcher):
        """``retries`` below 1 means "send the request once", not "send nothing"."""
        assert fetcher.get(self.status_200, retries=0).status == 200
        assert fetcher.get(self.status_200, retries=-1).status == 200

    def test_post_dict_data_list_values_are_repeated_keys(self, fetcher):
        """List values in a dict ``data`` are sent as repeated keys, not as their repr."""
        body = fetcher.post(self.post_url, data={"tags": ["a", "b"], "ids": [1, 2]}).json()
        assert body["form"] == {"tags": ["a", "b"], "ids": ["1", "2"]}

    def test_post_dict_data_none_values_are_dropped(self, fetcher):
        """A ``None`` value in a dict ``data`` leaves the key out of the body."""
        body = fetcher.post(self.post_url, data={"opt": None, "q": "x"}).json()
        assert body["form"] == {"q": "x"}

    def test_post_dict_data_scalars_and_form_content_type(self, fetcher):
        body = fetcher.post(self.post_url, data={"a": "x y", "b": 2}).json()
        assert body["form"] == {"a": "x y", "b": "2"}
        assert body["headers"]["Content-Type"] == "application/x-www-form-urlencoded"

    def test_post_string_data_is_untouched(self, fetcher):
        body = fetcher.post(self.post_url, data="a=1&a=2").json()
        assert body["data"] == "a=1&a=2"

    def test_get_params_none_values_are_dropped(self, fetcher):
        """A ``None`` value in ``params`` leaves the key out of the query string."""
        body = fetcher.get(self.basic_url, params={"page": None, "q": "x"}).json()
        assert body["args"] == {"q": "x"}

    def test_get_params_list_values_are_repeated_keys(self, fetcher):
        body = fetcher.get(self.basic_url, params={"tag": ["a", "b"]}).json()
        assert body["args"] == {"tag": ["a", "b"]}

    def test_session_post_dict_data_matches_fetcher(self):
        with FetcherSession() as session:
            body = session.post(self.post_url, data={"ids": [1, 2], "opt": None}).json()
        assert body["form"] == {"ids": ["1", "2"]}
