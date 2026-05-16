from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner

# The mcp command imports scrapling.core.ai lazily inside the callback;
# import it here so that ``patch('scrapling.core.ai.ScraplingMCPServer')``
# can resolve the attribute path at patch-time.
import scrapling.core.ai  # noqa: F401
from scrapling.cli import mcp


@pytest.fixture(autouse=True)
def _clean_env(monkeypatch):
    for var in ("SCRAPLING_MCP_TOKEN", "SCRAPLING_MCP_ALLOWLIST", "SCRAPLING_MCP_ALLOW_LOCAL"):
        monkeypatch.delenv(var, raising=False)
    yield


@pytest.fixture
def runner():
    return CliRunner()


def _patched_server():
    """Patch ScraplingMCPServer at the import site so we never start a real server."""
    return patch("scrapling.core.ai.ScraplingMCPServer")


class TestStdioMode:
    def test_stdio_default_runs_without_token(self, runner):
        with _patched_server() as mock_cls:
            mock_instance = MagicMock()
            mock_cls.return_value = mock_instance
            result = runner.invoke(mcp, [])
            assert result.exit_code == 0, result.output
            mock_instance.serve.assert_called_once()
            args, kwargs = mock_instance.serve.call_args
            http_arg = args[0] if args else kwargs["http"]
            assert http_arg is False

    def test_stdio_does_not_warn_about_bind_all(self, runner):
        with _patched_server() as mock_cls:
            mock_cls.return_value = MagicMock()
            result = runner.invoke(mcp, [])
            assert "0.0.0.0" not in (result.output or "")


class TestHttpDefaultHost:
    def test_default_host_is_loopback_when_http(self, runner, monkeypatch):
        monkeypatch.setenv("SCRAPLING_MCP_TOKEN", "secret")
        with _patched_server() as mock_cls:
            mock_instance = MagicMock()
            mock_cls.return_value = mock_instance
            result = runner.invoke(mcp, ["--http"])
            assert result.exit_code == 0, result.output
            args, kwargs = mock_instance.serve.call_args
            host = args[1] if len(args) >= 2 else kwargs["host"]
            assert host == "127.0.0.1"

    def test_explicit_host_is_passed_through(self, runner, monkeypatch):
        monkeypatch.setenv("SCRAPLING_MCP_TOKEN", "secret")
        with _patched_server() as mock_cls:
            mock_instance = MagicMock()
            mock_cls.return_value = mock_instance
            result = runner.invoke(mcp, ["--http", "--host", "127.0.0.5"])
            assert result.exit_code == 0, result.output
            args, kwargs = mock_instance.serve.call_args
            host = args[1] if len(args) >= 2 else kwargs["host"]
            assert host == "127.0.0.5"


class TestBindAllGate:
    def test_zero_zero_without_bind_all_is_rejected(self, runner, monkeypatch):
        monkeypatch.setenv("SCRAPLING_MCP_TOKEN", "secret")
        with _patched_server() as mock_cls:
            mock_cls.return_value = MagicMock()
            result = runner.invoke(mcp, ["--http", "--host", "0.0.0.0"])
            assert result.exit_code != 0
            assert "bind-all" in (result.output or "").lower()

    def test_double_colon_without_bind_all_is_rejected(self, runner, monkeypatch):
        monkeypatch.setenv("SCRAPLING_MCP_TOKEN", "secret")
        with _patched_server() as mock_cls:
            mock_cls.return_value = MagicMock()
            result = runner.invoke(mcp, ["--http", "--host", "::"])
            assert result.exit_code != 0

    def test_bind_all_yields_zero_zero(self, runner, monkeypatch):
        monkeypatch.setenv("SCRAPLING_MCP_TOKEN", "secret")
        with _patched_server() as mock_cls:
            mock_instance = MagicMock()
            mock_cls.return_value = mock_instance
            result = runner.invoke(mcp, ["--http", "--bind-all"])
            assert result.exit_code == 0, result.output
            args, kwargs = mock_instance.serve.call_args
            host = args[1] if len(args) >= 2 else kwargs["host"]
            assert host == "0.0.0.0"

    def test_bind_all_emits_warning(self, runner, monkeypatch):
        monkeypatch.setenv("SCRAPLING_MCP_TOKEN", "secret")
        with _patched_server() as mock_cls:
            mock_cls.return_value = MagicMock()
            result = runner.invoke(mcp, ["--http", "--bind-all"])
            assert result.exit_code == 0, result.output
            combined = (result.output or "") + (result.stderr_bytes or b"").decode(errors="ignore")
            assert "WARNING" in combined or "warning" in combined.lower()


class TestTokenGate:
    def test_http_without_token_exits(self, runner):
        with _patched_server() as mock_cls:
            mock_cls.return_value = MagicMock()
            result = runner.invoke(mcp, ["--http"])
            assert result.exit_code != 0
            assert "SCRAPLING_MCP_TOKEN" in (result.output or "")

    def test_http_with_blank_token_exits(self, runner, monkeypatch):
        monkeypatch.setenv("SCRAPLING_MCP_TOKEN", "   ")
        with _patched_server() as mock_cls:
            mock_cls.return_value = MagicMock()
            result = runner.invoke(mcp, ["--http"])
            assert result.exit_code != 0
            assert "SCRAPLING_MCP_TOKEN" in (result.output or "")

    def test_stdio_does_not_require_token(self, runner):
        with _patched_server() as mock_cls:
            mock_instance = MagicMock()
            mock_cls.return_value = mock_instance
            result = runner.invoke(mcp, [])
            assert result.exit_code == 0, result.output
            mock_instance.serve.assert_called_once()
