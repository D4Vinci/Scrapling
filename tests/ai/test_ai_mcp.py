import pytest
from unittest.mock import Mock, patch

from scrapling.core.ai import ScraplingMCPServer, ResponseModel


class TestMCPServer:
    """Test MCP server functionality"""

    @pytest.fixture
    def server(self):
        return ScraplingMCPServer()

    def test_server_creation(self, server):
        """Test server instance creation"""
        assert server._server is not None
        assert server._server.name == "Scrapling"

    def test_get_tool(self):
        """Test the get tool method"""
        with patch('scrapling.fetchers.Fetcher.get') as mock_get:
            mock_response = Mock()
            mock_response.status = 200
            mock_response.url = "https://example.com"
            mock_get.return_value = mock_response

            with patch('scrapling.core.ai.Convertor._extract_content') as mock_extract:
                mock_extract.return_value = iter(["Content"])

                result = ScraplingMCPServer.get(
                    url="https://example.com",
                    extraction_type="markdown"
                )

                assert isinstance(result, ResponseModel)
                assert result.status == 200
                assert result.url == "https://example.com"

    @pytest.mark.asyncio
    async def test_bulk_get_tool(self):
        """Test the bulk_get tool method"""
        with patch('scrapling.engines.FetcherSession') as mock_session:
            mock_instance = Mock()
            mock_session.return_value.__aenter__.return_value = mock_instance

            # Mock async get method
            async def mock_async_get(*args, **kwargs):
                mock_resp = Mock()
                mock_resp.status = 200
                mock_resp.url = args[0]
                return mock_resp

            mock_instance.get = mock_async_get

            with patch('scrapling.core.ai.Convertor._extract_content') as mock_extract:
                mock_extract.return_value = iter(["Content"])

                results = await ScraplingMCPServer.bulk_get(
                    urls=("https://example1.com", "https://example2.com"),
                    extraction_type="html"
                )

                assert len(results) == 2
                assert all(isinstance(r, ResponseModel) for r in results)

    @pytest.mark.asyncio
    async def test_fetch_tool(self):
        """Test the fetch tool method"""
        with patch('scrapling.fetchers.DynamicFetcher.async_fetch') as mock_fetch:
            mock_response = Mock()
            mock_response.status = 200
            mock_response.url = "https://example.com"
            mock_fetch.return_value = mock_response

            with patch('scrapling.core.ai.Convertor._extract_content') as mock_extract:
                mock_extract.return_value = iter(["Content"])

                result = await ScraplingMCPServer.fetch(
                    url="https://example.com",
                    headless=True
                )

                assert isinstance(result, ResponseModel)

    def test_serve_method(self, server):
        """Test the serve method"""
        with patch.object(server._server, 'run') as mock_run:
            server.serve()
            mock_run.assert_called_once_with(transport="stdio")
