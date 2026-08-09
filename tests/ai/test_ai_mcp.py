import base64
import struct
from typing import Any
from contextlib import contextmanager
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread

import pytest
import pytest_httpbin
from mcp.client import Client
from mcp.types import ImageContent, TextContent

from scrapling import __version__ as scrapling_version
from scrapling.engines.toolbelt.custom import Response
from scrapling.core.ai import (
    MCP_AUTH_TOKEN_ENV,
    ScraplingMCPServer,
    ResponseModel,
    SessionInfo,
    SessionCreatedModel,
    SessionClosedModel,
    _normalize_credentials,
    _page_pool_size,
    _StaticTokenVerifier,
    _translate_response,
)
from scrapling.fetchers import AsyncDynamicSession


def test_translate_response_strips_control_characters():
    """Pages with control chars like U+0008 must not crash the get/fetch path (issue #366)"""
    html = "<html><body><p>Hello\x08World</p>\t\n<div>Foo\x0cbar</div></body></html>"
    page = Response(
        url="https://jfinal.com/doc/1-5",
        content=html,
        status=200,
        reason="OK",
        cookies={},
        headers={},
        request_headers={},
    )

    result = _translate_response(page, "markdown", None, main_content_only=True)

    joined = "".join(result.content)
    assert "HelloWorld" in joined and "Foobar" in joined
    assert not any(ord(c) < 0x20 and c not in "\t\n\r" for c in joined)


class _FakeAsyncBrowserSession:
    instances: list["_FakeAsyncBrowserSession"] = []

    def __init__(self, **kwargs: Any) -> None:
        self.kwargs = kwargs
        self._is_alive = False
        type(self).instances.append(self)

    async def __aenter__(self):
        self._is_alive = True
        return self

    async def __aexit__(self, exc_type: Any, exc: Any, tb: Any) -> None:
        self._is_alive = False

    async def start(self) -> None:
        self._is_alive = True

    async def close(self) -> None:
        self._is_alive = False

    async def fetch(self, url: str, **kwargs: Any) -> Response:
        return Response(
            url=url,
            content="<html><body>ok</body></html>",
            status=200,
            reason="OK",
            cookies={},
            headers={},
            request_headers={},
        )


class _FakeDynamicSession(_FakeAsyncBrowserSession):
    instances = []


class _FakeStealthySession(_FakeAsyncBrowserSession):
    instances = []


@pytest_httpbin.use_class_based_httpbin
class TestMCPServer:
    """Test MCP server functionality"""

    @pytest.fixture(scope="class")
    def test_url(self, httpbin):
        return f"{httpbin.url}/html"

    @pytest.fixture
    def server(self):
        return ScraplingMCPServer()

    @pytest.mark.asyncio
    async def test_get_tool(self, server, test_url):
        """Test the get tool method"""
        result = await server.get(url=test_url, extraction_type="markdown")
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


@pytest_httpbin.use_class_based_httpbin
class TestSessionManagement:
    """Test persistent browser session management"""

    @pytest.fixture(scope="class")
    def test_url(self, httpbin):
        return f"{httpbin.url}/html"

    @pytest.fixture
    def server(self):
        return ScraplingMCPServer()

    @pytest.mark.asyncio
    async def test_open_and_close_session(self, server):
        """Test opening and closing a dynamic session"""
        result = await server.open_session(session_type="dynamic", headless=True)
        assert isinstance(result, SessionCreatedModel)
        assert result.session_type == "dynamic"
        assert result.is_alive is True
        session_id = result.session_id

        # Close the session
        closed = await server.close_session(session_id)
        assert isinstance(closed, SessionClosedModel)
        assert closed.session_id == session_id

    @pytest.mark.asyncio
    async def test_list_sessions(self, server):
        """Test listing sessions"""
        # Initially empty
        sessions = await server.list_sessions()
        assert sessions == []

        # Open a session
        result = await server.open_session(session_type="dynamic", headless=True)
        session_id = result.session_id

        # List should show it
        sessions = await server.list_sessions()
        assert len(sessions) == 1
        assert isinstance(sessions[0], SessionInfo)
        assert sessions[0].session_id == session_id
        assert sessions[0].session_type == "dynamic"
        assert sessions[0].is_alive is True

        # Cleanup
        await server.close_session(session_id)

    @pytest.mark.asyncio
    async def test_fetch_with_session(self, server, test_url):
        """Test fetching with a persistent dynamic session"""
        result = await server.open_session(session_type="dynamic", headless=True)
        session_id = result.session_id

        # Fetch using the session
        response = await server.fetch(url=test_url, session_id=session_id)
        assert isinstance(response, ResponseModel)
        assert response.status == 200

        # Fetch again with the same session (reuse)
        response2 = await server.fetch(url=test_url, session_id=session_id)
        assert isinstance(response2, ResponseModel)
        assert response2.status == 200

        await server.close_session(session_id)

    @pytest.mark.asyncio
    async def test_bulk_fetch_with_session(self, server, test_url):
        """Test bulk fetching with a persistent dynamic session"""
        result = await server.open_session(session_type="dynamic", headless=True, max_pages=5)
        session_id = result.session_id

        responses = await server.bulk_fetch(urls=[test_url, test_url], session_id=session_id)
        assert len(responses) == 2
        assert all(isinstance(r, ResponseModel) for r in responses)

        await server.close_session(session_id)

    @pytest.mark.asyncio
    async def test_session_type_mismatch(self, server, test_url):
        """Test that using a dynamic session with stealthy_fetch raises an error"""
        result = await server.open_session(session_type="dynamic", headless=True)
        session_id = result.session_id

        with pytest.raises(ValueError, match="'dynamic' session"):
            await server.stealthy_fetch(url=test_url, session_id=session_id)

        await server.close_session(session_id)

    @pytest.mark.asyncio
    async def test_close_nonexistent_session(self, server):
        """Test closing a session that doesn't exist"""
        with pytest.raises(ValueError, match="not found"):
            await server.close_session("nonexistent")

    @pytest.mark.asyncio
    async def test_fetch_with_nonexistent_session(self, server, test_url):
        """Test fetching with a session ID that doesn't exist"""
        with pytest.raises(ValueError, match="not found"):
            await server.fetch(url=test_url, session_id="nonexistent")

    @pytest.mark.asyncio
    async def test_fetch_with_closed_session(self, server, test_url):
        """Test fetching with a session that has been closed"""
        result = await server.open_session(session_type="dynamic", headless=True)
        session_id = result.session_id
        await server.close_session(session_id)

        with pytest.raises(ValueError, match="not found"):
            await server.fetch(url=test_url, session_id=session_id)

    @pytest.mark.asyncio
    async def test_open_session_with_custom_id(self, server):
        """Test opening a session with a custom session_id"""
        result = await server.open_session(session_type="dynamic", session_id="my-session", headless=True)
        assert isinstance(result, SessionCreatedModel)
        assert result.session_id == "my-session"

        await server.close_session("my-session")

    @pytest.mark.asyncio
    async def test_open_session_duplicate_id_raises(self, server):
        """Test that opening a session with a duplicate session_id raises an error"""
        await server.open_session(session_type="dynamic", session_id="dupe", headless=True)

        with pytest.raises(ValueError, match="already exists"):
            await server.open_session(session_type="dynamic", session_id="dupe", headless=True)

        await server.close_session("dupe")


class TestExecutablePath:
    """Test custom browser executable path plumbing in the MCP browser tools"""

    @pytest.fixture(autouse=True)
    def reset_fakes(self):
        _FakeDynamicSession.instances = []
        _FakeStealthySession.instances = []

    @pytest.mark.asyncio
    async def test_open_session_passes_executable_path(self, monkeypatch):
        """open_session forwards per-session executable_path to the dynamic session"""
        monkeypatch.setattr("scrapling.core.ai.AsyncDynamicSession", _FakeDynamicSession)
        server = ScraplingMCPServer()

        created = await server.open_session(session_type="dynamic", executable_path="/tmp/chrome")

        assert _FakeDynamicSession.instances[0].kwargs["executable_path"] == "/tmp/chrome"
        await server.close_session(created.session_id)

    @pytest.mark.asyncio
    async def test_open_session_uses_environment_default(self, monkeypatch):
        """open_session uses SCRAPLING_EXECUTABLE_PATH when no per-call value is provided"""
        monkeypatch.setenv("SCRAPLING_EXECUTABLE_PATH", "/opt/custom-chromium")
        monkeypatch.setattr("scrapling.core.ai.AsyncStealthySession", _FakeStealthySession)
        server = ScraplingMCPServer()

        created = await server.open_session(session_type="stealthy")

        assert _FakeStealthySession.instances[0].kwargs["executable_path"] == "/opt/custom-chromium"
        await server.close_session(created.session_id)

    @pytest.mark.asyncio
    async def test_fetch_overrides_global_executable_path(self, monkeypatch):
        """fetch forwards a per-call executable_path instead of the server default"""
        monkeypatch.setattr("scrapling.core.ai.AsyncDynamicSession", _FakeDynamicSession)
        server = ScraplingMCPServer(executable_path="/opt/default-chromium")

        result = await server.fetch(url="https://example.com", executable_path="/opt/request-chromium")

        assert isinstance(result, ResponseModel)
        assert _FakeDynamicSession.instances[0].kwargs["executable_path"] == "/opt/request-chromium"

    @pytest.mark.asyncio
    async def test_stealthy_fetch_uses_global_executable_path(self, monkeypatch):
        """stealthy_fetch forwards the server executable_path default"""
        monkeypatch.setattr("scrapling.core.ai.AsyncStealthySession", _FakeStealthySession)
        server = ScraplingMCPServer(executable_path="/opt/default-chromium")

        result = await server.stealthy_fetch(url="https://example.com")

        assert isinstance(result, ResponseModel)
        assert _FakeStealthySession.instances[0].kwargs["executable_path"] == "/opt/default-chromium"


class TestBulkPagePool:
    """Test the page pool sizing of the bulk browser tools"""

    @pytest.fixture(autouse=True)
    def reset_fakes(self):
        _FakeDynamicSession.instances = []
        _FakeStealthySession.instances = []

    @pytest.mark.asyncio
    @pytest.mark.parametrize("url_count,expected_pages", [(3, 3), (60, 50), (0, 1)])
    async def test_bulk_fetch_sizes_pool_within_validator_bounds(self, monkeypatch, url_count, expected_pages):
        """bulk_fetch opens a pool that covers the batch but stays inside the 1..50 `PagesCount` range"""
        monkeypatch.setattr("scrapling.core.ai.AsyncDynamicSession", _FakeDynamicSession)
        server = ScraplingMCPServer()
        urls = [f"https://example.com/{index}" for index in range(url_count)]

        results = await server.bulk_fetch(urls=urls)

        max_pages = _FakeDynamicSession.instances[0].kwargs["max_pages"]
        assert max_pages == expected_pages, f"Expected max_pages {expected_pages} for {url_count} URLs, got {max_pages}"
        assert len(results) == url_count, f"Expected {url_count} responses, got {len(results)}"

    @pytest.mark.asyncio
    @pytest.mark.parametrize("url_count,expected_pages", [(4, 4), (60, 50), (0, 1)])
    async def test_bulk_stealthy_fetch_sizes_pool_within_validator_bounds(self, monkeypatch, url_count, expected_pages):
        """bulk_stealthy_fetch sizes its pool to the batch instead of leaving it at the default of 1"""
        monkeypatch.setattr("scrapling.core.ai.AsyncStealthySession", _FakeStealthySession)
        server = ScraplingMCPServer()
        urls = [f"https://example.com/{index}" for index in range(url_count)]

        results = await server.bulk_stealthy_fetch(urls=urls)

        max_pages = _FakeStealthySession.instances[0].kwargs["max_pages"]
        assert max_pages == expected_pages, f"Expected max_pages {expected_pages} for {url_count} URLs, got {max_pages}"
        assert len(results) == url_count, f"Expected {url_count} responses, got {len(results)}"

    @pytest.mark.parametrize("url_count", [0, 1, 50, 60, 500])
    def test_page_pool_size_is_accepted_by_session_validation(self, url_count):
        """The computed pool size always passes the real session validation without launching a browser"""
        urls = [f"https://example.com/{index}" for index in range(url_count)]

        session = AsyncDynamicSession(max_pages=_page_pool_size(urls))

        assert session.max_pages == _page_pool_size(urls), (
            f"Expected the session to keep max_pages {_page_pool_size(urls)}, got {session.max_pages}"
        )


def _png_height(data: bytes) -> int:
    """Read the height field from a PNG IHDR chunk."""
    return struct.unpack(">I", data[20:24])[0]


@contextmanager
def _serve_html(body: bytes):
    """Serve a fixed HTML body on localhost, yielding its URL."""

    class _Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, *args, **kwargs):
            pass

    server = ThreadingHTTPServer(("127.0.0.1", 0), _Handler)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_address[1]}/"
    finally:
        server.shutdown()
        server.server_close()


@pytest_httpbin.use_class_based_httpbin
class TestScreenshot:
    """Test the screenshot tool"""

    @pytest.fixture(scope="class")
    def test_url(self, httpbin):
        return f"{httpbin.url}/html"

    @pytest.fixture
    def server(self):
        return ScraplingMCPServer()

    @pytest.mark.asyncio
    async def test_screenshot_png_with_dynamic_session(self, server, test_url):
        """PNG screenshot via a dynamic session returns image and url content blocks"""
        opened = await server.open_session(session_type="dynamic", headless=True)
        try:
            result = await server.screenshot(url=test_url, session_id=opened.session_id)
            assert isinstance(result, list) and len(result) == 2
            assert isinstance(result[0], ImageContent)
            assert result[0].mime_type == "image/png"
            assert isinstance(result[1], TextContent)
            assert result[1].text == test_url
        finally:
            await server.close_session(opened.session_id)

    @pytest.mark.asyncio
    async def test_screenshot_jpeg_with_quality(self, server, test_url):
        """JPEG screenshot with quality parameter via a dynamic session"""
        opened = await server.open_session(session_type="dynamic", headless=True)
        try:
            result = await server.screenshot(url=test_url, session_id=opened.session_id, image_type="jpeg", quality=80)
            assert isinstance(result[0], ImageContent)
            assert result[0].mime_type == "image/jpeg"
        finally:
            await server.close_session(opened.session_id)

    @pytest.mark.asyncio
    async def test_screenshot_with_stealthy_session(self, server, test_url):
        """PNG screenshot via a stealthy session"""
        opened = await server.open_session(session_type="stealthy", headless=True)
        try:
            result = await server.screenshot(url=test_url, session_id=opened.session_id)
            assert isinstance(result[0], ImageContent)
            assert result[0].mime_type == "image/png"
        finally:
            await server.close_session(opened.session_id)

    @pytest.mark.asyncio
    async def test_screenshot_full_page_taller_than_viewport(self, server):
        """full_page=True produces an image taller than the viewport-only capture"""
        tall_html = b"<html><body><div style='height:5000px;background:#abc'></div></body></html>"
        with _serve_html(tall_html) as tall_url:
            opened = await server.open_session(session_type="dynamic", headless=True)
            try:
                viewport_result = await server.screenshot(url=tall_url, session_id=opened.session_id, full_page=False)
                full_result = await server.screenshot(url=tall_url, session_id=opened.session_id, full_page=True)

                viewport_png = base64.b64decode(viewport_result[0].data)
                full_png = base64.b64decode(full_result[0].data)

                assert _png_height(full_png) > _png_height(viewport_png)
            finally:
                await server.close_session(opened.session_id)

    @pytest.mark.asyncio
    async def test_screenshot_invalid_session_id_raises(self, server, test_url):
        """Unknown session_id raises ValueError"""
        with pytest.raises(ValueError, match="not found"):
            await server.screenshot(url=test_url, session_id="does-not-exist")

    @pytest.mark.asyncio
    async def test_screenshot_quality_with_png_raises(self, server, test_url):
        """quality is rejected when image_type is png"""
        opened = await server.open_session(session_type="dynamic", headless=True)
        try:
            with pytest.raises(ValueError, match="quality"):
                await server.screenshot(url=test_url, session_id=opened.session_id, image_type="png", quality=90)
        finally:
            await server.close_session(opened.session_id)


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


SHARED_KEY = "s3cret"
UNICODE_KEY = "ünïcode-tökén"


class TestStaticTokenVerifier:
    """Test the shared bearer token verifier"""

    @pytest.mark.asyncio
    async def test_correct_token_is_accepted(self):
        result = await _StaticTokenVerifier(SHARED_KEY).verify_token(SHARED_KEY)

        assert result is not None
        assert result.token == SHARED_KEY
        assert result.scopes == []
        assert result.expires_at is None

    @pytest.mark.asyncio
    async def test_wrong_tokens_are_rejected(self):
        verifier = _StaticTokenVerifier(SHARED_KEY)

        for token in ("", "wrong", "s3cre", "s3cret ", "S3CRET"):
            assert await verifier.verify_token(token) is None

    @pytest.mark.asyncio
    async def test_non_ascii_token(self):
        """Tokens are compared as bytes, so non-ASCII characters must not raise"""
        verifier = _StaticTokenVerifier(UNICODE_KEY)

        assert await verifier.verify_token(UNICODE_KEY) is not None
        assert await verifier.verify_token("unicode-token") is None


class TestMCPServerAuthentication:
    """Test how the authentication token and transport security reach the MCP server"""

    def test_no_token_leaves_auth_disabled(self, monkeypatch):
        monkeypatch.delenv(MCP_AUTH_TOKEN_ENV, raising=False)
        server = ScraplingMCPServer()

        assert server._auth_token is None
        assert server._build_server("127.0.0.1", 8000).settings.auth is None

    def test_token_enables_auth(self, monkeypatch):
        monkeypatch.delenv(MCP_AUTH_TOKEN_ENV, raising=False)
        built = ScraplingMCPServer(auth_token=SHARED_KEY)._build_server("127.0.0.1", 8000)

        assert built.settings.auth is not None
        assert str(built.settings.auth.issuer_url) == "http://127.0.0.1:8000/"
        assert str(built.settings.auth.resource_server_url) == "http://127.0.0.1:8000/"

    def test_token_read_from_environment(self, monkeypatch):
        env_key, explicit_key = "from-env", "explicit"
        monkeypatch.setenv(MCP_AUTH_TOKEN_ENV, env_key)

        assert ScraplingMCPServer()._auth_token == env_key
        assert ScraplingMCPServer(auth_token=explicit_key)._auth_token == explicit_key

    def test_all_tools_are_registered_with_auth_enabled(self, monkeypatch):
        """MCPServer raises when `auth` and `token_verifier` are mismatched, so building must stay valid"""
        monkeypatch.delenv(MCP_AUTH_TOKEN_ENV, raising=False)
        built = ScraplingMCPServer(auth_token=SHARED_KEY)._build_server("0.0.0.0", 8000)

        assert len(built._tool_manager.list_tools()) == 10

    def test_allowed_hosts_enable_dns_rebinding_protection(self):
        assert ScraplingMCPServer._transport_security(()) is None

        security = ScraplingMCPServer._transport_security(("mcp.example.com:8000",))
        assert security is not None
        assert security.enable_dns_rebinding_protection is True
        assert security.allowed_hosts == ["mcp.example.com:8000"]
        assert security.allowed_origins == ["http://mcp.example.com:8000", "https://mcp.example.com:8000"]


class TestServerToolRegistration:
    """Test the built server end-to-end through an in-memory MCP client"""

    @pytest.mark.asyncio
    async def test_tools_are_listed_with_expected_schemas(self):
        """All 10 tools are advertised, and only the screenshot tool skips the structured output schema"""
        server = ScraplingMCPServer()._build_server("127.0.0.1", 8000)
        async with Client(server) as client:
            assert client.instructions
            tools = {tool.name: tool for tool in (await client.list_tools()).tools}

        assert len(tools) == 10
        assert tools["screenshot"].output_schema is None
        assert all(tool.output_schema is not None for name, tool in tools.items() if name != "screenshot")

    @pytest.mark.asyncio
    async def test_server_metadata_and_tool_annotations(self):
        """Server card metadata, cache hints, and tool annotations are advertised to clients"""
        server = ScraplingMCPServer()._build_server("127.0.0.1", 8000)
        async with Client(server) as client:
            info = client.server_info
            result = await client.list_tools()

        assert info is not None
        assert info.title == "Scrapling"
        assert info.version == scrapling_version
        assert info.website_url and info.icons
        assert result.ttl_ms == 3_600_000 and result.cache_scope == "public"

        annotations = {tool.name: tool.annotations for tool in result.tools if tool.annotations is not None}
        assert len(annotations) == 10
        for name in ("get", "bulk_get", "fetch", "bulk_fetch", "stealthy_fetch", "bulk_stealthy_fetch", "screenshot"):
            assert annotations[name].read_only_hint is True
            assert annotations[name].open_world_hint is True
        for name in ("open_session", "close_session"):
            assert annotations[name].read_only_hint is False
            assert annotations[name].destructive_hint is False
            assert annotations[name].open_world_hint is True
        assert annotations["list_sessions"].read_only_hint is True
        assert annotations["list_sessions"].open_world_hint is False
