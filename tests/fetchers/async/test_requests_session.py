import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from curl_cffi import CurlECode
from curl_cffi.curl import CurlError

from scrapling.engines.static import _ASyncSessionLogic as AsyncFetcherSession, AsyncFetcherClient
from scrapling.engines.toolbelt import ProxyRotator


class TestFetcherSession:
    """Test FetcherSession functionality"""

    def test_async_fetcher_client_creation(self):
        """Test AsyncFetcherClient creation"""
        client = AsyncFetcherClient()

        # Should not have context manager methods
        assert client.__aenter__ is None
        assert client.__aexit__ is None

    @pytest.mark.asyncio
    async def test_session_level_proxy_is_applied(self):
        """Session-level proxy must reach the request, not be silently dropped (#295)"""
        proxy = "http://10.255.255.1:9999"

        async with AsyncFetcherSession(proxy=proxy) as session:
            with (
                patch.object(session._async_curl_session, "request", new=AsyncMock()) as mocked_request,
                patch("scrapling.engines.static.ResponseFactory.from_http_request", return_value=MagicMock()),
            ):
                await session.get("http://example.com")

            assert mocked_request.call_args.kwargs["proxy"] == proxy

    @pytest.mark.asyncio
    async def test_per_request_proxy_overrides_session_proxy(self):
        """A per-request proxy must take precedence over the session-level proxy"""
        request_proxy = "http://10.255.255.2:9999"

        async with AsyncFetcherSession(proxy="http://10.255.255.1:9999") as session:
            with (
                patch.object(session._async_curl_session, "request", new=AsyncMock()) as mocked_request,
                patch("scrapling.engines.static.ResponseFactory.from_http_request", return_value=MagicMock()),
            ):
                await session.get("http://example.com", proxy=request_proxy)

            assert mocked_request.call_args.kwargs["proxy"] == request_proxy

    @pytest.mark.asyncio
    async def test_proxy_rotates_per_retry_attempt(self):
        """With a rotator, every retry attempt must pull a fresh proxy"""
        rotator = ProxyRotator(["http://p1:8080", "http://p2:8080"])

        async with AsyncFetcherSession(proxy_rotator=rotator, retries=2, retry_delay=0) as session:
            with (
                patch.object(session._async_curl_session, "request", new=AsyncMock()) as mocked_request,
                patch("scrapling.engines.static.ResponseFactory.from_http_request", return_value=MagicMock()),
            ):
                mocked_request.side_effect = [CurlError("transient"), MagicMock()]
                await session.get("http://example.com")

            proxies_used = [call.kwargs["proxy"] for call in mocked_request.call_args_list]
            assert proxies_used == ["http://p1:8080", "http://p2:8080"]

    @pytest.mark.asyncio
    @pytest.mark.parametrize("retries", [0, -1, None])
    async def test_retries_below_one_still_sends_the_request(self, retries):
        """A session-level retries below 1 must still send the request once instead of skipping it"""
        async with AsyncFetcherSession(retries=retries, retry_delay=0) as session:
            with (
                patch.object(session._async_curl_session, "request", new=AsyncMock()) as mocked_request,
                patch("scrapling.engines.static.ResponseFactory.from_http_request", return_value=MagicMock()),
            ):
                await session.get("http://example.com")

            assert mocked_request.call_count == 1

    @pytest.mark.asyncio
    async def test_per_request_retries_below_one_still_sends_the_request(self):
        """A per-request retries of 0 must override the session default without skipping the request"""
        async with AsyncFetcherSession(retries=3, retry_delay=0) as session:
            with (
                patch.object(session._async_curl_session, "request", new=AsyncMock()) as mocked_request,
                patch("scrapling.engines.static.ResponseFactory.from_http_request", return_value=MagicMock()),
            ):
                await session.get("http://example.com", retries=0)

            assert mocked_request.call_count == 1

    @pytest.mark.asyncio
    async def test_certificate_failure_is_not_retried(self):
        """Repeating the identical request cannot change the certificate verification result (#426)"""
        async with AsyncFetcherSession(retries=3, retry_delay=0) as session:
            with (
                patch.object(session._async_curl_session, "request", new=AsyncMock()) as mocked_request,
                patch("scrapling.engines.static.ResponseFactory.from_http_request", return_value=MagicMock()),
            ):
                mocked_request.side_effect = CurlError(
                    "SSL peer certificate was not OK", CurlECode.PEER_FAILED_VERIFICATION
                )
                with pytest.raises(CurlError):
                    await session.get("https://expired.badssl.com/")

            assert mocked_request.call_count == 1

    @pytest.mark.asyncio
    async def test_certificate_failure_is_retried_while_rotating(self):
        """A rotator makes the next attempt a different exit, so a route-caused certificate failure is worth retrying"""
        rotator = ProxyRotator(["http://p1:8080", "http://p2:8080"])

        async with AsyncFetcherSession(proxy_rotator=rotator, retries=2, retry_delay=0) as session:
            with (
                patch.object(session._async_curl_session, "request", new=AsyncMock()) as mocked_request,
                patch("scrapling.engines.static.ResponseFactory.from_http_request", return_value=MagicMock()),
            ):
                mocked_request.side_effect = [
                    CurlError("SSL peer certificate was not OK", CurlECode.PEER_FAILED_VERIFICATION),
                    MagicMock(),
                ]
                await session.get("https://example.com")

            assert mocked_request.call_count == 2

    @pytest.mark.asyncio
    async def test_client_side_error_is_not_retried_even_while_rotating(self):
        """A malformed URL holds on every exit, so rotation does not make it worth repeating"""
        rotator = ProxyRotator(["http://p1:8080", "http://p2:8080"])

        async with AsyncFetcherSession(proxy_rotator=rotator, retries=3, retry_delay=0) as session:
            with (
                patch.object(session._async_curl_session, "request", new=AsyncMock()) as mocked_request,
                patch("scrapling.engines.static.ResponseFactory.from_http_request", return_value=MagicMock()),
            ):
                mocked_request.side_effect = CurlError("URL using bad/illegal format", CurlECode.URL_MALFORMAT)
                with pytest.raises(CurlError):
                    await session.get("http://example.com")

            assert mocked_request.call_count == 1

    @pytest.mark.asyncio
    async def test_transient_error_is_still_retried(self):
        """Errors that are not classified as deterministic must keep their existing retry behaviour"""
        async with AsyncFetcherSession(retries=3, retry_delay=0) as session:
            with (
                patch.object(session._async_curl_session, "request", new=AsyncMock()) as mocked_request,
                patch("scrapling.engines.static.ResponseFactory.from_http_request", return_value=MagicMock()),
            ):
                mocked_request.side_effect = [
                    CurlError("Connection timed out", CurlECode.OPERATION_TIMEDOUT),
                    MagicMock(),
                ]
                await session.get("http://example.com")

            assert mocked_request.call_count == 2
