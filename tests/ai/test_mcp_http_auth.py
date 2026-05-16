"""Tests for the request-level Bearer auth on the HTTP MCP transport."""
from __future__ import annotations

import pytest

from scrapling.core._mcp_auth import StaticBearerTokenVerifier, build_http_auth


@pytest.fixture(autouse=True)
def _clean_env(monkeypatch):
    for var in ("SCRAPLING_MCP_TOKEN", "SCRAPLING_MCP_ALLOWLIST", "SCRAPLING_MCP_ALLOW_LOCAL"):
        monkeypatch.delenv(var, raising=False)
    yield


class TestStaticBearerTokenVerifier:
    def test_construction_rejects_empty_token(self):
        with pytest.raises(ValueError):
            StaticBearerTokenVerifier("")

    def test_construction_rejects_whitespace_token(self):
        with pytest.raises(ValueError):
            StaticBearerTokenVerifier("   ")

    @pytest.mark.asyncio
    async def test_correct_token_returns_access_token(self):
        verifier = StaticBearerTokenVerifier("s3cret")
        result = await verifier.verify_token("s3cret")
        assert result is not None
        assert result.token == "s3cret"
        assert result.scopes == []
        assert result.client_id == "scrapling-mcp"

    @pytest.mark.asyncio
    async def test_wrong_token_returns_none(self):
        verifier = StaticBearerTokenVerifier("s3cret")
        assert await verifier.verify_token("not-the-token") is None

    @pytest.mark.asyncio
    async def test_empty_token_returns_none(self):
        verifier = StaticBearerTokenVerifier("s3cret")
        assert await verifier.verify_token("") is None

    @pytest.mark.asyncio
    async def test_non_string_token_returns_none(self):
        verifier = StaticBearerTokenVerifier("s3cret")
        # The MCP protocol always passes str, but verify defensive handling.
        assert await verifier.verify_token(None) is None  # type: ignore[arg-type]
        assert await verifier.verify_token(12345) is None  # type: ignore[arg-type]

    @pytest.mark.asyncio
    async def test_prefix_match_is_rejected(self):
        # Constant-time compare is not a prefix match; it must be exact.
        verifier = StaticBearerTokenVerifier("s3cret")
        assert await verifier.verify_token("s3cre") is None
        assert await verifier.verify_token("s3cret-extra") is None


class TestBuildHttpAuth:
    def test_returns_settings_and_verifier(self):
        settings, verifier = build_http_auth("token-abc", port=8123)
        # Settings carry the synthetic identifier URLs FastMCP requires.
        assert str(settings.issuer_url).startswith("http://127.0.0.1:8123")
        assert str(settings.resource_server_url).startswith("http://127.0.0.1:8123")
        assert settings.required_scopes == []
        assert isinstance(verifier, StaticBearerTokenVerifier)


class TestStreamableHttpAuthIntegration:
    """Drive the actual FastMCP streamable_http app and confirm Bearer auth.

    The auth check sits at the route level via ``RequireAuthMiddleware``,
    so a missing or wrong token must produce HTTP 401 *before* the body
    is parsed by the MCP layer. A valid token must NOT produce 401 (the
    transport may still reject the request body for other reasons; we
    only assert that auth no longer rejects it).
    """

    @pytest.fixture
    def token(self):
        return "shared-secret-xyz"

    @pytest.fixture
    def app(self, token):
        from mcp.server.fastmcp import FastMCP

        auth_settings, verifier = build_http_auth(token, port=8000)
        # host="0.0.0.0" so FastMCP does not auto-enable DNS rebinding
        # protection (which would otherwise reject TestClient's
        # "testserver" Host header).
        server = FastMCP(
            name="auth-test",
            host="0.0.0.0",
            port=8000,
            auth=auth_settings,
            token_verifier=verifier,
        )
        return server.streamable_http_app()

    @pytest.fixture
    def client(self, app):
        from starlette.testclient import TestClient

        return TestClient(app)

    def test_missing_authorization_header_yields_401(self, client):
        response = client.post("/mcp", json={"jsonrpc": "2.0", "method": "ping", "id": 1})
        assert response.status_code == 401

    def test_non_bearer_authorization_header_yields_401(self, client):
        response = client.post(
            "/mcp",
            json={"jsonrpc": "2.0", "method": "ping", "id": 1},
            headers={"Authorization": "Basic dXNlcjpwYXNz"},
        )
        assert response.status_code == 401

    def test_wrong_bearer_token_yields_401(self, client):
        response = client.post(
            "/mcp",
            json={"jsonrpc": "2.0", "method": "ping", "id": 1},
            headers={"Authorization": "Bearer not-the-real-token"},
        )
        assert response.status_code == 401

    def test_empty_bearer_token_yields_401(self, client):
        response = client.post(
            "/mcp",
            json={"jsonrpc": "2.0", "method": "ping", "id": 1},
            headers={"Authorization": "Bearer "},
        )
        assert response.status_code == 401

    def test_correct_bearer_token_passes_auth(self, app, token):
        # The streamable HTTP session manager needs the Starlette lifespan
        # to be active (it owns a task group spun up at startup), so we
        # drive the app via TestClient as a context manager.
        from starlette.testclient import TestClient

        with TestClient(app) as client:
            response = client.post(
                "/mcp",
                json={"jsonrpc": "2.0", "method": "ping", "id": 1},
                headers={
                    "Authorization": f"Bearer {token}",
                    "Accept": "application/json, text/event-stream",
                    "Content-Type": "application/json",
                },
            )
        # The MCP layer may still reject the body shape (e.g., 400/406),
        # but auth is what this test is about.
        assert response.status_code != 401


class TestServeWiresAuthForHttp:
    """The high-level ``ScraplingMCPServer.serve`` path must hand FastMCP
    both ``auth`` settings and a token verifier when ``http=True``, and
    must NOT do so for stdio.
    """

    def test_http_serve_constructs_fastmcp_with_auth(self, monkeypatch):
        from unittest.mock import MagicMock, patch

        from scrapling.core.ai import ScraplingMCPServer
        from scrapling.core._mcp_auth import StaticBearerTokenVerifier

        monkeypatch.setenv("SCRAPLING_MCP_TOKEN", "abc")
        with patch("scrapling.core.ai.FastMCP") as fastmcp_cls:
            instance = MagicMock()
            fastmcp_cls.return_value = instance
            ScraplingMCPServer().serve(http=True, host="127.0.0.1", port=8000)

        fastmcp_cls.assert_called_once()
        kwargs = fastmcp_cls.call_args.kwargs
        assert kwargs.get("auth") is not None
        assert isinstance(kwargs.get("token_verifier"), StaticBearerTokenVerifier)

    def test_stdio_serve_does_not_pass_auth(self, monkeypatch):
        from unittest.mock import MagicMock, patch

        from scrapling.core.ai import ScraplingMCPServer

        # No SCRAPLING_MCP_TOKEN set; stdio must not require it.
        with patch("scrapling.core.ai.FastMCP") as fastmcp_cls:
            instance = MagicMock()
            fastmcp_cls.return_value = instance
            ScraplingMCPServer().serve(http=False, host="127.0.0.1", port=8000)

        fastmcp_cls.assert_called_once()
        kwargs = fastmcp_cls.call_args.kwargs
        assert "auth" not in kwargs or kwargs.get("auth") is None
        assert "token_verifier" not in kwargs or kwargs.get("token_verifier") is None
