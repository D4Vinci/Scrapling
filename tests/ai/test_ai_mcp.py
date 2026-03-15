import pytest
import pytest_httpbin

from scrapling.core.ai import ScraplingMCPServer, ResponseModel, _normalize_credentials


@pytest_httpbin.use_class_based_httpbin
class TestMCPServer:
    """Test MCP server functionality"""

    @pytest.fixture(scope="class")
    def test_url(self, httpbin):
        return f"{httpbin.url}/html"

    @pytest.fixture
    def server(self):
        return ScraplingMCPServer()

    def test_get_tool(self, server, test_url):
        """Test the get tool method"""
        result = server.get(url=test_url, extraction_type="markdown")
        assert isinstance(result, ResponseModel)
        assert result.status == 200
        assert result.url == test_url

    @pytest.mark.asyncio
    async def test_bulk_get_tool(self, server, test_url):
        """Test the bulk_get tool method"""
        results = await server.bulk_get(urls=(test_url, test_url), extraction_type="html")

        assert len(results) == 2
        assert all(isinstance(r, ResponseModel) for r in results)

    @pytest.mark.asyncio
    async def test_fetch_tool(self, server, test_url):
        """Test the fetch tool method"""
        result = await server.fetch(url=test_url, headless=True)
        assert isinstance(result, ResponseModel)
        assert result.status == 200

    @pytest.mark.asyncio
    async def test_bulk_fetch_tool(self, server, test_url):
        """Test the bulk_fetch tool method"""
        result = await server.bulk_fetch(urls=(test_url, test_url), headless=True)
        assert all(isinstance(r, ResponseModel) for r in result)

    @pytest.mark.asyncio
    async def test_stealthy_fetch_tool(self, server, test_url):
        """Test the stealthy_fetch tool method"""
        result = await server.stealthy_fetch(url=test_url, headless=True)
        assert isinstance(result, ResponseModel)
        assert result.status == 200

    @pytest.mark.asyncio
    async def test_bulk_stealthy_fetch_tool(self, server, test_url):
        """Test the bulk_stealthy_fetch tool method"""
        result = await server.bulk_stealthy_fetch(urls=(test_url, test_url), headless=True)
        assert all(isinstance(r, ResponseModel) for r in result)


class TestNormalizeCredentials:
    """Test the _normalize_credentials helper"""

    def test_none_returns_none(self):
        assert _normalize_credentials(None) is None

    def test_empty_dict_returns_none(self):
        assert _normalize_credentials({}) is None

    def test_valid_credentials_returns_tuple(self):
        result = _normalize_credentials({"username": "user", "password": "pass"})
        assert result == ("user", "pass")

    def test_missing_password_raises(self):
        with pytest.raises(ValueError, match="password"):
            _normalize_credentials({"username": "user"})

    def test_missing_username_raises(self):
        with pytest.raises(ValueError, match="username"):
            _normalize_credentials({"password": "pass"})
