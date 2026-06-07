import pytest
from unittest.mock import patch, MagicMock, AsyncMock
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
