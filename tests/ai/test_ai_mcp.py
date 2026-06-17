import inspect
import base64
import struct
from contextlib import contextmanager
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread

import pytest
import pytest_httpbin
from mcp.types import ImageContent, TextContent

from scrapling.core import ai as ai_module
from scrapling.core.ai import (
    ScraplingMCPServer,
    ResponseModel,
    SessionInfo,
    SessionCreatedModel,
    SessionClosedModel,
    _SessionEntry,
    _normalize_credentials,
)


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
            assert result[0].mimeType == "image/png"
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
            assert result[0].mimeType == "image/jpeg"
        finally:
            await server.close_session(opened.session_id)

    @pytest.mark.asyncio
    async def test_screenshot_with_stealthy_session(self, server, test_url):
        """PNG screenshot via a stealthy session"""
        opened = await server.open_session(session_type="stealthy", headless=True)
        try:
            result = await server.screenshot(url=test_url, session_id=opened.session_id)
            assert isinstance(result[0], ImageContent)
            assert result[0].mimeType == "image/png"
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


class _FakeBrowserSession:
    def __init__(self, **kwargs):
        self.kwargs = kwargs
        self.fetch_calls = []
        self._is_alive = True

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False

    async def start(self):
        return None

    async def close(self):
        self._is_alive = False

    async def fetch(self, url, **kwargs):
        self.fetch_calls.append((url, kwargs))
        return object()


class TestMCPWaitUntil:
    """Test wait_until exposure and forwarding in MCP browser tools."""

    def test_browser_tools_expose_wait_until(self):
        for tool_name in (
            "open_session",
            "screenshot",
            "fetch",
            "bulk_fetch",
            "stealthy_fetch",
            "bulk_stealthy_fetch",
        ):
            signature = inspect.signature(getattr(ScraplingMCPServer, tool_name))
            assert "wait_until" in signature.parameters

    @pytest.mark.asyncio
    async def test_bulk_fetch_forwards_wait_until_to_dynamic_session(self, monkeypatch):
        created_sessions = []

        def fake_dynamic_session(**kwargs):
            session = _FakeBrowserSession(**kwargs)
            created_sessions.append(session)
            return session

        monkeypatch.setattr(ai_module, "AsyncDynamicSession", fake_dynamic_session)
        monkeypatch.setattr(
            ai_module,
            "_translate_response",
            lambda page, extraction_type, css_selector, main_content_only: ResponseModel(
                status=200,
                content=[],
                url="https://example.com",
            ),
        )

        server = ScraplingMCPServer()
        await server.bulk_fetch(urls=["https://example.com"], wait_until="domcontentloaded")

        assert created_sessions[0].kwargs["wait_until"] == "domcontentloaded"

    @pytest.mark.asyncio
    async def test_open_session_forwards_wait_until_to_dynamic_session(self, monkeypatch):
        created_sessions = []

        def fake_dynamic_session(**kwargs):
            session = _FakeBrowserSession(**kwargs)
            created_sessions.append(session)
            return session

        monkeypatch.setattr(ai_module, "AsyncDynamicSession", fake_dynamic_session)

        server = ScraplingMCPServer()
        opened = await server.open_session(session_type="dynamic", wait_until="domcontentloaded")

        assert created_sessions[0].kwargs["wait_until"] == "domcontentloaded"
        await server.close_session(opened.session_id)

    @pytest.mark.asyncio
    async def test_bulk_fetch_forwards_wait_until_to_existing_dynamic_session(self, monkeypatch):
        fake_session = _FakeBrowserSession()
        server = ScraplingMCPServer()
        server._sessions["session-id"] = _SessionEntry(session=fake_session, session_type="dynamic")
        monkeypatch.setattr(
            ai_module,
            "_translate_response",
            lambda page, extraction_type, css_selector, main_content_only: ResponseModel(
                status=200,
                content=[],
                url="https://example.com",
            ),
        )

        await server.bulk_fetch(
            urls=["https://example.com"],
            session_id="session-id",
            wait_until="domcontentloaded",
        )

        assert fake_session.fetch_calls[0][1]["wait_until"] == "domcontentloaded"

    @pytest.mark.asyncio
    async def test_bulk_stealthy_fetch_forwards_wait_until_to_stealthy_session(self, monkeypatch):
        created_sessions = []

        def fake_stealthy_session(**kwargs):
            session = _FakeBrowserSession(**kwargs)
            created_sessions.append(session)
            return session

        monkeypatch.setattr(ai_module, "AsyncStealthySession", fake_stealthy_session)
        monkeypatch.setattr(
            ai_module,
            "_translate_response",
            lambda page, extraction_type, css_selector, main_content_only: ResponseModel(
                status=200,
                content=[],
                url="https://example.com",
            ),
        )

        server = ScraplingMCPServer()
        await server.bulk_stealthy_fetch(urls=["https://example.com"], wait_until="domcontentloaded")

        assert created_sessions[0].kwargs["wait_until"] == "domcontentloaded"

    @pytest.mark.asyncio
    async def test_open_session_forwards_wait_until_to_stealthy_session(self, monkeypatch):
        created_sessions = []

        def fake_stealthy_session(**kwargs):
            session = _FakeBrowserSession(**kwargs)
            created_sessions.append(session)
            return session

        monkeypatch.setattr(ai_module, "AsyncStealthySession", fake_stealthy_session)

        server = ScraplingMCPServer()
        opened = await server.open_session(session_type="stealthy", wait_until="domcontentloaded")

        assert created_sessions[0].kwargs["wait_until"] == "domcontentloaded"
        await server.close_session(opened.session_id)

    @pytest.mark.asyncio
    async def test_bulk_stealthy_fetch_forwards_wait_until_to_existing_stealthy_session(self, monkeypatch):
        fake_session = _FakeBrowserSession()
        server = ScraplingMCPServer()
        server._sessions["session-id"] = _SessionEntry(session=fake_session, session_type="stealthy")
        monkeypatch.setattr(
            ai_module,
            "_translate_response",
            lambda page, extraction_type, css_selector, main_content_only: ResponseModel(
                status=200,
                content=[],
                url="https://example.com",
            ),
        )

        await server.bulk_stealthy_fetch(
            urls=["https://example.com"],
            session_id="session-id",
            wait_until="domcontentloaded",
        )

        assert fake_session.fetch_calls[0][1]["wait_until"] == "domcontentloaded"

    @pytest.mark.asyncio
    async def test_screenshot_forwards_wait_until_to_existing_session(self):
        fake_session = _FakeBrowserSession()
        server = ScraplingMCPServer()
        server._sessions["session-id"] = _SessionEntry(session=fake_session, session_type="dynamic")

        class FakePage:
            url = "https://example.com"

            async def screenshot(self, **kwargs):
                return b"image"

        async def fake_fetch(url, **kwargs):
            fake_session.fetch_calls.append((url, kwargs))
            await kwargs["page_action"](FakePage())
            return object()

        fake_session.fetch = fake_fetch

        await server.screenshot(
            url="https://example.com",
            session_id="session-id",
            wait_until="domcontentloaded",
        )

        assert fake_session.fetch_calls[0][1]["wait_until"] == "domcontentloaded"
