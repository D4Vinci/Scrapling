import pytest
import pytest_httpbin

from scrapling.fetchers import AsyncFetcher

AsyncFetcher.adaptive = True


@pytest.fixture
def _reset_async_fetcher_config():
    """Snapshot and restore the mutable class-level parser config around a test."""
    snapshot = {k: getattr(AsyncFetcher, k) for k in AsyncFetcher.parser_keywords}
    try:
        yield
    finally:
        for k, v in snapshot.items():
            setattr(AsyncFetcher, k, v)


@pytest_httpbin.use_class_based_httpbin
@pytest.mark.asyncio
class TestAsyncFetcher:
    @pytest.fixture(scope="class")
    def fetcher(self):
        return AsyncFetcher

    @pytest.fixture(scope="class")
    def urls(self, httpbin):
        return {
            "status_200": f"{httpbin.url}/status/200",
            "status_404": f"{httpbin.url}/status/404",
            "status_501": f"{httpbin.url}/status/501",
            "basic_url": f"{httpbin.url}/get",
            "post_url": f"{httpbin.url}/post",
            "put_url": f"{httpbin.url}/put",
            "delete_url": f"{httpbin.url}/delete",
            "html_url": f"{httpbin.url}/html",
        }

    async def test_basic_get(self, fetcher, urls):
        """Test doing basic get request with multiple statuses"""
        assert (await fetcher.get(urls["status_200"])).status == 200
        assert (await fetcher.get(urls["status_404"])).status == 404
        assert (await fetcher.get(urls["status_501"])).status == 501

    async def test_get_properties(self, fetcher, urls):
        """Test if different arguments with the GET request break the code or not"""
        assert (
            await fetcher.get(urls["status_200"], stealthy_headers=True)
        ).status == 200
        assert (
            await fetcher.get(urls["status_200"], follow_redirects=True)
        ).status == 200
        assert (await fetcher.get(urls["status_200"], timeout=None)).status == 200
        assert (
            await fetcher.get(
                urls["status_200"],
                stealthy_headers=True,
                follow_redirects=True,
                timeout=None,
            )
        ).status == 200

    async def test_post_properties(self, fetcher, urls):
        """Test if different arguments with the POST request break the code or not"""
        assert (
            await fetcher.post(urls["post_url"], data={"key": "value"})
        ).status == 200
        assert (
            await fetcher.post(
                urls["post_url"], data={"key": "value"}, stealthy_headers=True
            )
        ).status == 200
        assert (
            await fetcher.post(
                urls["post_url"], data={"key": "value"}, follow_redirects=True
            )
        ).status == 200
        assert (
            await fetcher.post(urls["post_url"], data={"key": "value"}, timeout=None)
        ).status == 200
        assert (
            await fetcher.post(
                urls["post_url"],
                data={"key": "value"},
                stealthy_headers=True,
                follow_redirects=True,
                timeout=None,
            )
        ).status == 200

    async def test_put_properties(self, fetcher, urls):
        """Test if different arguments with a PUT request break the code or not"""
        assert (await fetcher.put(urls["put_url"], data={"key": "value"})).status in [
            200,
            405,
        ]
        assert (
            await fetcher.put(
                urls["put_url"], data={"key": "value"}, stealthy_headers=True
            )
        ).status in [200, 405]
        assert (
            await fetcher.put(
                urls["put_url"], data={"key": "value"}, follow_redirects=True
            )
        ).status in [200, 405]
        assert (
            await fetcher.put(urls["put_url"], data={"key": "value"}, timeout=None)
        ).status in [200, 405]
        assert (
            await fetcher.put(
                urls["put_url"],
                data={"key": "value"},
                stealthy_headers=True,
                follow_redirects=True,
                timeout=None,
            )
        ).status in [200, 405]

    async def test_delete_properties(self, fetcher, urls):
        """Test if different arguments with the DELETE request break the code or not"""
        assert (
            await fetcher.delete(urls["delete_url"], stealthy_headers=True)
        ).status == 200
        assert (
            await fetcher.delete(urls["delete_url"], follow_redirects=True)
        ).status == 200
        assert (await fetcher.delete(urls["delete_url"], timeout=None)).status == 200
        assert (
            await fetcher.delete(
                urls["delete_url"],
                stealthy_headers=True,
                follow_redirects=True,
                timeout=None,
            )
        ).status == 200

    async def test_configure_propagates_to_response(
        self, fetcher, urls, _reset_async_fetcher_config
    ):
        """`AsyncFetcher.configure()` must reach the Response's Selector on the HTTP path."""
        AsyncFetcher.configure(adaptive=False, adaptive_domain="")
        baseline = await fetcher.get(urls["html_url"])
        assert baseline._storage is None

        AsyncFetcher.configure(adaptive=True, adaptive_domain="configured.test")
        configured = await fetcher.get(urls["html_url"])
        assert configured._storage is not None
        assert configured.url == "configured.test"

    async def test_selector_config_overrides_configure(
        self, fetcher, urls, _reset_async_fetcher_config
    ):
        """A per-request ``selector_config`` overrides the class-level configure()."""
        AsyncFetcher.configure(adaptive=True, adaptive_domain="from-configure.test")
        response = await fetcher.get(
            urls["html_url"],
            selector_config={"adaptive_domain": "from-request.test"},
        )
        assert response._storage is not None
        assert response.url == "from-request.test"

    async def test_retries_below_one_still_performs_the_request(self, fetcher, urls):
        """``retries`` below 1 means "send the request once", not "send nothing"."""
        assert (await fetcher.get(urls["status_200"], retries=0)).status == 200
        assert (await fetcher.get(urls["status_200"], retries=-1)).status == 200
