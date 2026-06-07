import pytest
from unittest.mock import patch, MagicMock
from curl_cffi.curl import CurlError

from scrapling.engines.static import _SyncSessionLogic as FetcherSession, FetcherClient
from scrapling.engines.toolbelt import ProxyRotator


class TestFetcherSession:
    """Test FetcherSession functionality"""

    def test_fetcher_session_creation(self):
        """Test FetcherSession creation"""
        session = FetcherSession(timeout=30, retries=3, stealthy_headers=True)

        assert session._default_timeout == 30
        assert session._default_retries == 3

    def test_fetcher_session_context_manager(self):
        """Test FetcherSession as a context manager"""
        session = FetcherSession()

        with session as s:
            assert s == session
            assert session._curl_session is not None

        # Session should be cleaned up

    def test_fetcher_session_double_enter(self):
        """Test error on double entering"""
        session = FetcherSession()

        with session:
            with pytest.raises(RuntimeError):
                session.__enter__()

    def test_fetcher_client_creation(self):
        """Test FetcherClient creation"""
        client = FetcherClient()

        # Should not have context manager methods
        assert client.__enter__ is None
        assert client.__exit__ is None

    def test_session_level_proxy_is_applied(self):
        """Session-level proxy must reach the request, not be silently dropped (#295)"""
        proxy = "http://10.255.255.1:9999"

        with FetcherSession(proxy=proxy) as session:
            with (
                patch.object(session._curl_session, "request") as mocked_request,
                patch("scrapling.engines.static.ResponseFactory.from_http_request", return_value=MagicMock()),
            ):
                session.get("http://example.com")

            assert mocked_request.call_args.kwargs["proxy"] == proxy

    def test_per_request_proxy_overrides_session_proxy(self):
        """A per-request proxy must take precedence over the session-level proxy"""
        request_proxy = "http://10.255.255.2:9999"

        with FetcherSession(proxy="http://10.255.255.1:9999") as session:
            with (
                patch.object(session._curl_session, "request") as mocked_request,
                patch("scrapling.engines.static.ResponseFactory.from_http_request", return_value=MagicMock()),
            ):
                session.get("http://example.com", proxy=request_proxy)

            assert mocked_request.call_args.kwargs["proxy"] == request_proxy

    def test_proxy_rotates_per_retry_attempt(self):
        """With a rotator, every retry attempt must pull a fresh proxy"""
        rotator = ProxyRotator(["http://p1:8080", "http://p2:8080"])

        with FetcherSession(proxy_rotator=rotator, retries=2, retry_delay=0) as session:
            with (
                patch.object(session._curl_session, "request") as mocked_request,
                patch("scrapling.engines.static.ResponseFactory.from_http_request", return_value=MagicMock()),
            ):
                mocked_request.side_effect = [CurlError("transient"), MagicMock()]
                session.get("http://example.com")

            proxies_used = [call.kwargs["proxy"] for call in mocked_request.call_args_list]
            assert proxies_used == ["http://p1:8080", "http://p2:8080"]
