import pytest


from scrapling.engines.static import AsyncFetcherClient


class TestFetcherSession:
    """Test FetcherSession functionality"""

    def test_async_fetcher_client_creation(self):
        """Test AsyncFetcherClient creation"""
        client = AsyncFetcherClient()

        # Should not have context manager methods
        assert client.__aenter__ is None
        assert client.__aexit__ is None
        assert client._async_curl_session is True  # Special marker
