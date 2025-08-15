import pytest
from click.testing import CliRunner
from unittest.mock import patch, MagicMock
import pytest_httpbin

from scrapling.cli import (
    shell, mcp, get, post, put, delete, fetch, stealthy_fetch
)


@pytest_httpbin.use_class_based_httpbin
class TestCLI:
    """Test CLI functionality"""

    @pytest.fixture
    def html_url(self, httpbin):
        return f"{httpbin.url}/html"

    @pytest.fixture
    def runner(self):
        return CliRunner()

    def test_shell_command(self, runner):
        """Test shell command"""
        with patch('scrapling.core.shell.CustomShell') as mock_shell:
            mock_instance = MagicMock()
            mock_shell.return_value = mock_instance

            result = runner.invoke(shell)
            assert result.exit_code == 0
            mock_instance.start.assert_called_once()

    def test_mcp_command(self, runner):
        """Test MCP command"""
        with patch('scrapling.core.ai.ScraplingMCPServer') as mock_server:
            mock_instance = MagicMock()
            mock_server.return_value = mock_instance

            result = runner.invoke(mcp)
            assert result.exit_code == 0
            mock_instance.serve.assert_called_once()

    def test_extract_get_command(self, runner, tmp_path, html_url):
        """Test extract `get` command"""
        output_file = tmp_path / "output.md"

        with patch('scrapling.fetchers.Fetcher.get') as mock_get:
            mock_response = MagicMock()
            mock_response.status = 200
            mock_get.return_value = mock_response

            with patch('scrapling.cli.Convertor.write_content_to_file'):
                result = runner.invoke(
                    get,
                    [html_url, str(output_file)]
                )
                assert result.exit_code == 0

        # Test with various options
        with patch('scrapling.fetchers.Fetcher.get') as mock_get:
            mock_get.return_value = mock_response

            with patch('scrapling.cli.Convertor.write_content_to_file'):
                result = runner.invoke(
                    get,
                    [
                        html_url,
                        str(output_file),
                        '-H', 'User-Agent: Test',
                        '--cookies', 'session=abc123',
                        '--timeout', '60',
                        '--proxy', 'http://proxy:8080',
                        '-s', '.content',
                        '-p', 'page=1'
                    ]
                )
                assert result.exit_code == 0

    def test_extract_post_command(self, runner, tmp_path, html_url):
        """Test extract `post` command"""
        output_file = tmp_path / "output.html"

        with patch('scrapling.fetchers.Fetcher.post') as mock_post:
            mock_response = MagicMock()
            mock_post.return_value = mock_response

            with patch('scrapling.cli.Convertor.write_content_to_file'):
                result = runner.invoke(
                    post,
                    [
                        html_url,
                        str(output_file),
                        '-d', 'key=value',
                        '-j', '{"data": "test"}'
                    ]
                )
                assert result.exit_code == 0

    def test_extract_put_command(self, runner, tmp_path, html_url):
        """Test extract `put` command"""
        output_file = tmp_path / "output.html"

        with patch('scrapling.fetchers.Fetcher.put') as mock_put:
            mock_response = MagicMock()
            mock_put.return_value = mock_response

            with patch('scrapling.cli.Convertor.write_content_to_file'):
                result = runner.invoke(
                    put,
                    [
                        html_url,
                        str(output_file),
                        '-d', 'key=value',
                        '-j', '{"data": "test"}'
                    ]
                )
                assert result.exit_code == 0

    def test_extract_delete_command(self, runner, tmp_path, html_url):
        """Test extract `delete` command"""
        output_file = tmp_path / "output.html"

        with patch('scrapling.fetchers.Fetcher.delete') as mock_delete:
            mock_response = MagicMock()
            mock_delete.return_value = mock_response

            with patch('scrapling.cli.Convertor.write_content_to_file'):
                result = runner.invoke(
                    delete,
                    [
                        html_url,
                        str(output_file)
                    ]
                )
                assert result.exit_code == 0

    def test_extract_fetch_command(self, runner, tmp_path, html_url):
        """Test extract fetch command"""
        output_file = tmp_path / "output.txt"

        with patch('scrapling.fetchers.DynamicFetcher.fetch') as mock_fetch:
            mock_response = MagicMock()
            mock_fetch.return_value = mock_response

            with patch('scrapling.cli.Convertor.write_content_to_file'):
                result = runner.invoke(
                    fetch,
                    [
                        html_url,
                        str(output_file),
                        '--headless',
                        '--stealth',
                        '--timeout', '60000'
                    ]
                )
                assert result.exit_code == 0

    def test_extract_stealthy_fetch_command(self, runner, tmp_path, html_url):
        """Test extract fetch command"""
        output_file = tmp_path / "output.md"

        with patch('scrapling.fetchers.StealthyFetcher.fetch') as mock_fetch:
            mock_response = MagicMock()
            mock_fetch.return_value = mock_response

            with patch('scrapling.cli.Convertor.write_content_to_file'):
                result = runner.invoke(
                    stealthy_fetch,
                    [
                        html_url,
                        str(output_file),
                        '--headless',
                        '--css-selector', 'body',
                        '--timeout', '60000'
                    ]
                )
                assert result.exit_code == 0

    def test_invalid_arguments(self, runner, html_url):
        """Test invalid arguments handling"""
        # Missing required arguments
        result = runner.invoke(get)
        assert result.exit_code != 0

        # Invalid output file extension
        with patch('scrapling.cli.Convertor.write_content_to_file') as mock_write:
            mock_write.side_effect = ValueError("Unknown file type")

            _ = runner.invoke(
                get,
                [html_url, 'output.invalid']
            )
            # Should handle the error gracefully
