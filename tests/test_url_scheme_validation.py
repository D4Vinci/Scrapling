import pytest
from scrapling.core.utils import validate_url_scheme
from scrapling.fetchers import Fetcher
from scrapling.engines._browsers._stealth import StealthySession, AsyncStealthySession

class TestUrlSchemeValidation:
    def test_valid_schemes(self):
        validate_url_scheme("http://example.com")
        validate_url_scheme("https://example.com")

    def test_invalid_schemes(self):
        with pytest.raises(ValueError, match="Unsupported URL scheme"):
            validate_url_scheme("file:///etc/passwd")
        with pytest.raises(ValueError, match="Unsupported URL scheme"):
            validate_url_scheme("ftp://example.com")

    def test_http_fetcher_blocks_file(self):
        with pytest.raises(ValueError, match="Unsupported URL scheme"):
            Fetcher.get("file:///etc/passwd")

    def test_stealth_fetcher_blocks_file(self):
        session = StealthySession(headless=True)
        with pytest.raises(ValueError, match="Unsupported URL scheme"):
            session.fetch("file:///etc/passwd")

    @pytest.mark.asyncio
    async def test_async_stealth_fetcher_blocks_file(self):
        session = AsyncStealthySession(headless=True)
        with pytest.raises(ValueError, match="Unsupported URL scheme"):
            await session.fetch("file:///etc/passwd")