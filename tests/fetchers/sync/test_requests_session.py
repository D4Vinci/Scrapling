import pytest


from scrapling.engines.static import _SyncSessionLogic as FetcherSession, FetcherClient


class TestFetcherSession:
    """Test FetcherSession functionality"""

    def test_fetcher_session_creation(self):
        """Test FetcherSession creation"""
        session = FetcherSession(
            timeout=30,
            retries=3,
            stealthy_headers=True
        )

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
