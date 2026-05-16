import os

import pytest


@pytest.fixture(autouse=True)
def _allow_local_mcp_targets(monkeypatch):
    """The existing MCP test suite uses pytest_httpbin which serves on
    localhost. The MCP URL guard otherwise blocks loopback targets, so we
    set the documented dev-only escape hatch for these tests.
    """
    monkeypatch.setenv("SCRAPLING_MCP_ALLOW_LOCAL", "1")
    monkeypatch.delenv("SCRAPLING_MCP_ALLOWLIST", raising=False)
    yield
