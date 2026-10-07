import base64
import inspect
from json import loads
import struct
from typing import Any
from contextlib import contextmanager
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread
from unittest.mock import AsyncMock, Mock, patch

import pytest
import pytest_httpbin
from mcp.client import Client
from mcp.server import MCPServer
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
    SessionType,
)
from scrapling.core.ai.server import (
    _SessionEntry,
    _normalize_credentials,
    _session_settings,
    _StaticTokenVerifier,
    _STEALTH_FETCH_KEYS,
    _translate_response,
)
from scrapling.engines._browsers._validators import StealthConfig, models_default_values, validate
from scrapling.fetchers import AsyncStealthySession, FetcherSession


MCP_TOOLS = {
    "make_request",
    "browser_fetch_once",
    "open_request_session",
    "session_make_request",
    "browser_open",
    "browser_fetch",
    "browser_actions",
    "browser_evaluate",
    "browser_extract",
    "browser_screenshot",
    "browser_network_requests",
    "browser_network_request",
    "close_session",
    "list_sessions",
}


def test_translate_response_strips_control_characters():
    """Pages with control chars like U+0008 must not crash the request/fetch path (issue #366)"""
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


class _FakePage:
    """The page object a fake session hands to a `page_action`."""

    url = "https://example.com/captured"

    async def screenshot(self, **kwargs: Any) -> bytes:
        return b"fake-png-bytes"


class _FakeStealthySession:
    instances: list["_FakeStealthySession"] = []

    def __init__(self, **kwargs: Any) -> None:
        self.kwargs = kwargs
        self.fetch_calls: list[dict[str, Any]] = []
        self._is_alive = False
        # `executable_path` is validated against the filesystem; drop it so the fake accepts test paths.
        self._config = validate(
            {name: value for name, value in kwargs.items() if name != "executable_path"}, StealthConfig
        )
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
        self.fetch_calls.append(kwargs)
        if kwargs.get("page_action") is not None:
            await kwargs["page_action"](_FakePage())
        return Response(
            url=url,
            content="<html><body>ok</body></html>",
            status=200,
            reason="OK",
            cookies={},
            headers={},
            request_headers={},
        )


class TestOneShotTools:
    @pytest.mark.asyncio
    async def test_make_request_get_and_post_through_mcp(self, monkeypatch, httpbin):
        sessions: list[FetcherSession] = []

        def create_session():
            session = FetcherSession()
            sessions.append(session)
            return session

        monkeypatch.setattr("scrapling.core.ai.server.FetcherSession", create_session)
        server = ScraplingMCPServer()
        async with Client(server._build_server("127.0.0.1", 8000)) as client:
            fetched = await client.call_tool("make_request", {"url": f"{httpbin.url}/html", "css_selector": "h1"})
            assert not fetched.is_error and fetched.structured_content is not None
            assert fetched.structured_content["status"] == 200
            assert fetched.structured_content["url"] == f"{httpbin.url}/html"
            assert "Herman Melville - Moby-Dick" in "".join(fetched.structured_content["content"])
            posted = await client.call_tool(
                "make_request",
                {
                    "url": f"{httpbin.url}/post",
                    "method": "POST",
                    "json": {"key": "value"},
                    "extraction_type": "text",
                },
            )
            assert not posted.is_error and posted.structured_content is not None
            assert posted.structured_content["status"] == 200
            assert loads("".join(posted.structured_content["content"]))["json"] == {"key": "value"}
            cookies = await client.call_tool(
                "make_request",
                {"url": f"{httpbin.url}/cookies/set/test/value", "follow_redirects": True, "extraction_type": "text"},
            )
            assert not cookies.is_error and cookies.structured_content is not None
            assert loads("".join(cookies.structured_content["content"]))["cookies"] == {"test": "value"}
            fresh = await client.call_tool("make_request", {"url": f"{httpbin.url}/cookies", "extraction_type": "text"})
            assert not fresh.is_error and fresh.structured_content is not None
            assert loads("".join(fresh.structured_content["content"]))["cookies"] == {}
        assert len(sessions) == 4 and all(not session._is_alive for session in sessions)
        assert not server._sessions

    @pytest.mark.asyncio
    async def test_browser_fetch_once_renders_and_closes_through_mcp(self, monkeypatch):
        sessions: list[AsyncStealthySession] = []

        def create_session(**kwargs: Any):
            session = AsyncStealthySession(**kwargs)
            sessions.append(session)
            return session

        monkeypatch.setattr("scrapling.core.ai.server.AsyncStealthySession", create_session)
        server = ScraplingMCPServer()
        html = b"""<html><body><p id="answer">Initial</p><p>Outside</p><script>
setTimeout(() => { const p = document.querySelector('#answer'); p.textContent = 'Rendered'; p.id = 'ready'; }, 50);
</script></body></html>"""
        with _serve_html(html) as url:
            async with Client(server._build_server("127.0.0.1", 8000)) as client:
                result = await client.call_tool(
                    "browser_fetch_once",
                    {"url": url, "google_search": False, "wait_selector": "#ready", "css_selector": "#ready"},
                )
        assert not result.is_error and result.structured_content is not None
        assert result.structured_content["status"] == 200
        assert result.structured_content["url"] == url
        content = "".join(result.structured_content["content"])
        assert "Rendered" in content and "Initial" not in content and "Outside" not in content
        assert len(sessions) == 1 and not sessions[0]._is_alive
        assert sessions[0].page_pool.pages_count == 0
        assert not server._sessions

    @pytest.mark.asyncio
    @pytest.mark.parametrize("method", ["GET", "POST", "PUT", "DELETE"])
    async def test_make_request_forwards_options_and_closes(self, monkeypatch, method):
        response = Response(
            url="https://example.com/final",
            content="<main>ok</main>",
            status=201,
            reason="Created",
            cookies={},
            headers={},
            request_headers={},
        )
        request = AsyncMock(return_value=response)
        session = Mock(**{method.lower(): request})
        context = AsyncMock()
        context.__aenter__.return_value = session
        factory = Mock(return_value=context)
        monkeypatch.setattr("scrapling.core.ai.server.FetcherSession", factory)
        server = ScraplingMCPServer()
        existing = _SessionEntry(Mock(_is_alive=True), "static")
        server._sessions["existing"] = existing
        options = {
            "impersonate": "firefox",
            "params": {"q": "query"},
            "data": "body",
            "json": {"key": "value"},
            "headers": {"X-Test": "value"},
            "cookies": {"theme": "dark"},
            "timeout": 12.5,
            "follow_redirects": False,
            "max_redirects": 5,
            "retries": 2,
            "retry_delay": 0,
            "proxy": "http://127.0.0.1:8080",
            "proxy_auth": {"username": "proxy-user", "password": "proxy-pass"},
            "auth": {"username": "user", "password": "pass"},
            "verify": False,
            "http3": True,
            "stealthy_headers": False,
        }
        async with Client(server._build_server("127.0.0.1", 8000)) as client:
            result = await client.call_tool("make_request", {"url": "https://example.com", "method": method, **options})
        assert not result.is_error and result.structured_content is not None
        assert result.structured_content["status"] == 201
        assert result.structured_content["url"] == response.url
        expected = {**options, "auth": ("user", "pass"), "proxy_auth": ("proxy-user", "proxy-pass")}
        if method == "GET":
            expected.pop("data")
            expected.pop("json")
        request.assert_awaited_once_with("https://example.com", **expected)
        factory.assert_called_once_with()
        context.__aexit__.assert_awaited_once_with(None, None, None)
        assert server._sessions == {"existing": existing}
        assert existing.session.mock_calls == []

    @pytest.mark.asyncio
    @pytest.mark.parametrize("tool", ["make_request", "browser_fetch_once"])
    async def test_failed_one_shot_closes_without_touching_registered_sessions(self, monkeypatch, tool):
        context = AsyncMock()
        context.__aenter__.return_value = context
        request = context.get if tool == "make_request" else context.fetch
        request.side_effect = RuntimeError("fetch failed")
        factory = Mock(return_value=context)
        monkeypatch.setattr(
            "scrapling.core.ai.server.FetcherSession"
            if tool == "make_request"
            else "scrapling.core.ai.server.AsyncStealthySession",
            factory,
        )
        server = ScraplingMCPServer()
        existing = _SessionEntry(Mock(_is_alive=True), "stealthy")
        server._sessions["existing"] = existing
        async with Client(server._build_server("127.0.0.1", 8000)) as client:
            result = await client.call_tool(tool, {"url": "https://example.com"})
        assert result.is_error
        assert result.content and isinstance(result.content[0], TextContent)
        assert "fetch failed" in result.content[0].text
        request.assert_awaited_once()
        context.__aexit__.assert_awaited_once()
        assert context.__aexit__.call_args.args[0] is RuntimeError
        assert server._sessions == {"existing": existing}
        assert existing.session.mock_calls == []


class TestRequestProfiles:
    @pytest.mark.asyncio
    @pytest.mark.parametrize("tool", ["make_request", "open_request_session"])
    @pytest.mark.parametrize("impersonate", ["chrome", ["chrome", "firefox"], None])
    async def test_profiles_fetch_through_mcp(self, httpbin, tool, impersonate):
        server = ScraplingMCPServer()
        async with Client(server._build_server("127.0.0.1", 8000)) as client:
            args = {"url": f"{httpbin.url}/html", "css_selector": "h1"}
            try:
                if tool == "open_request_session":
                    opened = await client.call_tool(tool, {"session_id": "profiles", "impersonate": impersonate})
                    assert not opened.is_error and opened.structured_content is not None
                    assert server._sessions["profiles"].session._default_impersonate == impersonate
                    args["session_id"] = "profiles"
                else:
                    args["impersonate"] = impersonate
                result = await client.call_tool(
                    "session_make_request" if tool == "open_request_session" else tool, args
                )
                assert not result.is_error and result.structured_content is not None
                assert result.structured_content["status"] == 200
                assert "Herman Melville - Moby-Dick" in "".join(result.structured_content["content"])
            finally:
                if "profiles" in server._sessions:
                    closed = await client.call_tool("close_session", {"session_id": "profiles"})
                    assert not closed.is_error
        assert not server._sessions

    @pytest.mark.asyncio
    @pytest.mark.parametrize("tool", ["make_request", "open_request_session"])
    @pytest.mark.parametrize("impersonate", ["unknown-browser", ["chrome", "unknown-browser"]])
    async def test_invalid_profiles_fail_before_opening_sessions(self, monkeypatch, tool, impersonate):
        factory = Mock()
        monkeypatch.setattr("scrapling.core.ai.server.FetcherSession", factory)
        server = ScraplingMCPServer()
        args = {"url": "https://example.com"} if tool == "make_request" else {"session_id": "profiles"}
        args["impersonate"] = impersonate
        async with Client(server._build_server("127.0.0.1", 8000)) as client:
            result = await client.call_tool(tool, args)
        assert result.is_error
        assert result.content and isinstance(result.content[0], TextContent)
        assert "impersonate" in result.content[0].text
        factory.assert_not_called()
        assert not server._sessions

    @pytest.mark.asyncio
    async def test_profile_schemas_share_the_enum_and_keep_titles(self):
        async with Client(ScraplingMCPServer()._build_server("127.0.0.1", 8000)) as client:
            tools = {tool.name: tool for tool in (await client.list_tools()).tools}
        for name in ("make_request", "open_request_session"):
            schema = tools[name].input_schema
            profile = schema["properties"]["impersonate"]
            assert profile["title"] == "Impersonate" and profile["default"] == "chrome"
            choices = profile["anyOf"]
            scalar = next(choice for choice in choices if "$ref" in choice)
            array = next(choice for choice in choices if choice.get("type") == "array")
            assert array["items"] == scalar
            assert {"type": "null"} in choices
            definition = schema["$defs"][scalar["$ref"].removeprefix("#/$defs/")]
            assert definition["type"] == "string"
            assert {"chrome", "firefox"} <= set(definition["enum"])


class TestSessionTypeChecks:
    @pytest.mark.parametrize(
        "session_type, allowed, error",
        [
            ("stealthy", ["stealthy"], None),
            ("static", ["static"], None),
            ("static", ["stealthy"], "requires a 'stealthy' session"),
            ("stealthy", ["static"], "requires a 'static' session"),
        ],
    )
    def test_get_session_checks_allowed_types(
        self, session_type: SessionType, allowed: list[SessionType], error: str | None
    ) -> None:
        server = ScraplingMCPServer()
        session = Mock(_is_alive=True)
        entry = _SessionEntry(session, session_type)
        server._sessions["test"] = entry
        if error:
            with pytest.raises(ValueError, match=error):
                server._get_session("test", allowed)
        else:
            assert server._get_session("test", allowed) is entry
        assert session.mock_calls == []

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "tool, session_type, required",
        [
            ("browser_fetch", "static", "'stealthy'"),
            ("browser_screenshot", "static", "'stealthy'"),
            ("browser_extract", "static", "'stealthy'"),
            ("session_make_request", "stealthy", "'static'"),
        ],
    )
    async def test_tool_rejects_wrong_session_before_any_action(
        self, tool: str, session_type: SessionType, required: str
    ) -> None:
        server = ScraplingMCPServer()
        session = Mock(_is_alive=True)
        server._sessions["test"] = _SessionEntry(session, session_type)
        args = {"session_id": "test"}
        if tool not in ("browser_extract", "browser_screenshot"):
            args["url"] = "https://example.com"
        async with Client(server._build_server("127.0.0.1", 8000)) as client:
            result = await client.call_tool(tool, args)
        assert result.is_error
        assert result.content and isinstance(result.content[0], TextContent)
        assert f"requires a {required} session" in result.content[0].text
        assert session.mock_calls == []
        assert server._sessions["test"].session is session


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
        """Test opening and closing a stealthy session"""
        result = await server.browser_open(headless=True)
        assert isinstance(result, SessionCreatedModel)
        assert result.session_type == "stealthy"
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
        result = await server.browser_open(headless=True)
        session_id = result.session_id

        # List should show it
        sessions = await server.list_sessions()
        assert len(sessions) == 1
        assert isinstance(sessions[0], SessionInfo)
        assert sessions[0].session_id == session_id
        assert sessions[0].session_type == "stealthy"
        assert sessions[0].is_alive is True

        # Cleanup
        await server.close_session(session_id)

    @pytest.mark.asyncio
    async def test_browser_fetch_reuses_the_session(self, server, test_url):
        """Test fetching a page twice through a persistent stealthy session"""
        result = await server.browser_open(headless=True)
        session_id = result.session_id

        response = await server.browser_fetch(url=test_url, session_id=session_id)
        assert isinstance(response, ResponseModel)
        assert response.status == 200

        # Fetch again with the same session (reuse)
        response2 = await server.browser_fetch(url=test_url, session_id=session_id)
        assert isinstance(response2, ResponseModel)
        assert response2.status == 200

        await server.close_session(session_id)

    @pytest.mark.asyncio
    async def test_browser_fetch_accepts_per_request_overrides(self, server, test_url):
        """A per-request override is honored on a session fetch"""
        result = await server.browser_open(headless=True)
        session_id = result.session_id

        response = await server.browser_fetch(url=test_url, session_id=session_id, network_idle=True, timeout=45000)
        assert isinstance(response, ResponseModel)
        assert response.status == 200

        await server.close_session(session_id)

    @pytest.mark.asyncio
    async def test_close_nonexistent_session(self, server):
        """Test closing a session that doesn't exist"""
        with pytest.raises(ValueError, match="not found"):
            await server.close_session("nonexistent")

    @pytest.mark.asyncio
    async def test_browser_fetch_with_nonexistent_session(self, server, test_url):
        """Test fetching with a session ID that doesn't exist"""
        with pytest.raises(ValueError, match="not found"):
            await server.browser_fetch(url=test_url, session_id="nonexistent")

    @pytest.mark.asyncio
    async def test_browser_fetch_with_closed_session(self, server, test_url):
        """Test fetching with a session that has been closed"""
        result = await server.browser_open(headless=True)
        session_id = result.session_id
        await server.close_session(session_id)

        with pytest.raises(ValueError, match="not found"):
            await server.browser_fetch(url=test_url, session_id=session_id)

    @pytest.mark.asyncio
    async def test_browser_open_with_custom_id(self, server):
        """Test opening a session with a custom session_id"""
        result = await server.browser_open(session_id="my-session", headless=True)
        assert isinstance(result, SessionCreatedModel)
        assert result.session_id == "my-session"

        await server.close_session("my-session")

    @pytest.mark.asyncio
    async def test_browser_open_duplicate_id_raises(self, server):
        """Test that opening a session with a duplicate session_id raises an error"""
        await server.browser_open(session_id="dupe", headless=True)

        with pytest.raises(ValueError, match="already exists"):
            await server.browser_open(session_id="dupe", headless=True)

        await server.close_session("dupe")


class TestStaticSessionManagement:
    """Test persistent requests (HTTP) session management"""

    @pytest.fixture
    def server(self):
        return ScraplingMCPServer()

    @pytest.mark.asyncio
    async def test_static_session_workflow_through_mcp(self, server, httpbin):
        async with Client(server._build_server("127.0.0.1", 8000)) as client:
            opened = await client.call_tool("open_request_session", {"session_id": "http"})
            assert not opened.is_error
            session = server._sessions["http"].session
            try:
                response = await client.call_tool(
                    "session_make_request",
                    {"url": f"{httpbin.url}/html", "session_id": "http", "css_selector": "h1"},
                )
                assert not response.is_error
                assert response.structured_content is not None
                assert response.structured_content["status"] == 200
                assert response.structured_content["url"] == f"{httpbin.url}/html"
                assert "Herman Melville - Moby-Dick" in "".join(response.structured_content["content"])
                posted = await client.call_tool(
                    "session_make_request",
                    {
                        "url": f"{httpbin.url}/post",
                        "session_id": "http",
                        "method": "POST",
                        "json": {"key": "value"},
                        "extraction_type": "text",
                    },
                )
                assert not posted.is_error
                assert posted.structured_content is not None
                assert posted.structured_content["status"] == 200
                assert loads("".join(posted.structured_content["content"]))["json"] == {"key": "value"}
            finally:
                closed = await client.call_tool("close_session", {"session_id": "http"})
                assert not closed.is_error
        assert not session._is_alive
        assert not server._sessions

    @pytest.mark.asyncio
    async def test_static_session_lifecycle(self, server, httpbin):
        """Open a requests session, make GET and POST requests through it, then close it"""
        created = await server.open_request_session(session_id="st")
        assert isinstance(created, SessionCreatedModel)
        assert created.session_type == "static"
        assert created.is_alive is True
        assert created.settings["impersonate"] == "chrome"

        response = await server.session_make_request(url=f"{httpbin.url}/html", session_id="st")
        assert isinstance(response, ResponseModel)
        assert response.status == 200

        posted = await server.session_make_request(
            url=f"{httpbin.url}/post", session_id="st", method="POST", json={"key": "value"}, extraction_type="text"
        )
        assert posted.status == 200

        listed = await server.list_sessions()
        assert listed[0].session_type == "static"
        assert listed[0].settings == created.settings

        session = server._sessions["st"].session
        closed = await server.close_session("st")
        assert closed.session_id == "st"
        assert session._is_alive is False

    @pytest.mark.asyncio
    async def test_static_session_keeps_cookies(self, server, httpbin):
        """Cookies set by one request are sent with the next request of the same session"""
        await server.open_request_session(session_id="jar")
        await server.session_make_request(
            url=f"{httpbin.url}/cookies/set/test/value",
            session_id="jar",
            follow_redirects=True,
            extraction_type="text",
        )
        response = await server.session_make_request(
            url=f"{httpbin.url}/cookies", session_id="jar", extraction_type="text"
        )
        assert "test" in "".join(response.content)
        await server.close_session("jar")

    @pytest.mark.asyncio
    async def test_session_ids_are_shared_across_both_open_tools(self, server, monkeypatch):
        """A requests session and a browser session can't share the same ID"""
        monkeypatch.setattr("scrapling.core.ai.server.AsyncStealthySession", _FakeStealthySession)
        await server.open_request_session(session_id="shared")
        with pytest.raises(ValueError, match="already exists"):
            await server.browser_open(session_id="shared")
        await server.close_session("shared")

    @pytest.mark.asyncio
    async def test_session_make_request_requires_a_static_session(self, server, monkeypatch):
        """session_make_request rejects browser sessions"""
        monkeypatch.setattr("scrapling.core.ai.server.AsyncStealthySession", _FakeStealthySession)
        await server.browser_open(session_id="browser")
        with pytest.raises(ValueError, match="requires a 'static' session"):
            await server.session_make_request(url="https://example.com", session_id="browser")
        await server.close_session("browser")

    @pytest.mark.asyncio
    async def test_browser_fetch_and_screenshot_reject_static_sessions(self, server):
        """The browser session tools refuse a static session with a clear error"""
        await server.open_request_session(session_id="st2")
        with pytest.raises(ValueError, match="requires a 'stealthy' session"):
            await server.browser_fetch(url="https://example.com", session_id="st2")
        with pytest.raises(ValueError, match="requires a 'stealthy' session"):
            await server.browser_screenshot(session_id="st2")
        await server.close_session("st2")


class TestExecutablePath:
    """Test custom browser executable path plumbing in the MCP browser tools"""

    @pytest.fixture(autouse=True)
    def reset_fakes(self):
        _FakeStealthySession.instances = []

    @pytest.mark.asyncio
    async def test_browser_open_passes_executable_path(self, monkeypatch):
        """browser_open forwards per-session executable_path to the stealthy session"""
        monkeypatch.setattr("scrapling.core.ai.server.AsyncStealthySession", _FakeStealthySession)
        server = ScraplingMCPServer()

        created = await server.browser_open(executable_path="/tmp/chrome")

        assert _FakeStealthySession.instances[0].kwargs["executable_path"] == "/tmp/chrome"
        await server.close_session(created.session_id)

    @pytest.mark.asyncio
    async def test_browser_open_uses_environment_default(self, monkeypatch):
        """browser_open uses SCRAPLING_EXECUTABLE_PATH when no per-call value is provided"""
        monkeypatch.setenv("SCRAPLING_EXECUTABLE_PATH", "/opt/custom-chromium")
        monkeypatch.setattr("scrapling.core.ai.server.AsyncStealthySession", _FakeStealthySession)
        server = ScraplingMCPServer()

        created = await server.browser_open()

        assert _FakeStealthySession.instances[0].kwargs["executable_path"] == "/opt/custom-chromium"
        await server.close_session(created.session_id)

    @pytest.mark.asyncio
    async def test_browser_open_overrides_global_executable_path(self, monkeypatch):
        """browser_open prefers the supplied executable path to the server default."""
        monkeypatch.setattr("scrapling.core.ai.server.AsyncStealthySession", _FakeStealthySession)
        server = ScraplingMCPServer(executable_path="/opt/default-chromium")

        created = await server.browser_open(executable_path="/opt/request-chromium")

        assert _FakeStealthySession.instances[0].kwargs["executable_path"] == "/opt/request-chromium"
        await server.close_session(created.session_id)

    @pytest.mark.asyncio
    async def test_browser_open_uses_global_executable_path(self, monkeypatch):
        """browser_open forwards the server executable path default."""
        monkeypatch.setattr("scrapling.core.ai.server.AsyncStealthySession", _FakeStealthySession)
        server = ScraplingMCPServer(executable_path="/opt/default-chromium")

        created = await server.browser_open()

        assert _FakeStealthySession.instances[0].kwargs["executable_path"] == "/opt/default-chromium"
        await server.close_session(created.session_id)

    @pytest.mark.asyncio
    async def test_browser_fetch_once_overrides_global_executable_path(self, monkeypatch):
        """browser_fetch_once forwards a per-call executable_path instead of the server default"""
        monkeypatch.setattr("scrapling.core.ai.server.AsyncStealthySession", _FakeStealthySession)
        server = ScraplingMCPServer(executable_path="/opt/default-chromium")

        result = await server.browser_fetch_once(url="https://example.com", executable_path="/opt/request-chromium")

        assert isinstance(result, ResponseModel)
        assert _FakeStealthySession.instances[0].kwargs["executable_path"] == "/opt/request-chromium"

    @pytest.mark.asyncio
    async def test_browser_fetch_once_uses_global_executable_path(self, monkeypatch):
        """browser_fetch_once forwards the server executable_path default"""
        monkeypatch.setattr("scrapling.core.ai.server.AsyncStealthySession", _FakeStealthySession)
        server = ScraplingMCPServer(executable_path="/opt/default-chromium")

        result = await server.browser_fetch_once(url="https://example.com")

        assert isinstance(result, ResponseModel)
        assert _FakeStealthySession.instances[0].kwargs["executable_path"] == "/opt/default-chromium"

    @pytest.mark.asyncio
    async def test_browser_fetch_once_uses_environment_default(self, monkeypatch):
        monkeypatch.setenv("SCRAPLING_EXECUTABLE_PATH", "/opt/environment-chromium")
        monkeypatch.setattr("scrapling.core.ai.server.AsyncStealthySession", _FakeStealthySession)
        await ScraplingMCPServer().browser_fetch_once(url="https://example.com")
        assert _FakeStealthySession.instances[0].kwargs["executable_path"] == "/opt/environment-chromium"
        assert not _FakeStealthySession.instances[0]._is_alive


class TestOneShotBrowserForwarding:
    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "options",
        [
            {},
            {
                "headless": False,
                "google_search": False,
                "real_chrome": True,
                "wait": 250,
                "proxy": {"server": "http://host:8080", "username": "user", "password": "pass"},
                "timezone_id": "Europe/London",
                "locale": "en-GB",
                "extra_headers": {"X-Test": "value"},
                "useragent": "test-agent",
                "hide_canvas": True,
                "cdp_url": "ws://127.0.0.1:9222/devtools/browser/test",
                "executable_path": "/tmp/chromium",
                "timeout": 45000,
                "disable_resources": True,
                "wait_selector": "#main",
                "cookies": [{"name": "theme", "value": "dark", "url": "https://example.com"}],
                "network_idle": True,
                "wait_selector_state": "visible",
                "block_webrtc": True,
                "allow_webgl": False,
                "solve_cloudflare": True,
                "additional_args": {"viewport": {"width": 1024, "height": 768}},
                "pierce_shadow": True,
            },
        ],
        ids=["defaults", "overrides"],
    )
    async def test_each_call_uses_a_closed_stealth_session_with_all_options(self, monkeypatch, options):
        monkeypatch.delenv("SCRAPLING_EXECUTABLE_PATH", raising=False)
        monkeypatch.setattr("scrapling.core.ai.server.AsyncStealthySession", _FakeStealthySession)
        _FakeStealthySession.instances = []
        server = ScraplingMCPServer()
        existing = _SessionEntry(Mock(_is_alive=True), "stealthy")
        server._sessions["existing"] = existing
        expected = {
            "headless": True,
            "google_search": True,
            "real_chrome": False,
            "wait": 0,
            "proxy": None,
            "timezone_id": None,
            "locale": None,
            "extra_headers": None,
            "useragent": None,
            "hide_canvas": False,
            "cdp_url": None,
            "executable_path": None,
            "timeout": 30000,
            "disable_resources": False,
            "wait_selector": None,
            "cookies": None,
            "network_idle": False,
            "wait_selector_state": "attached",
            "block_webrtc": False,
            "allow_webgl": True,
            "solve_cloudflare": False,
            "additional_args": None,
            "pierce_shadow": False,
            **options,
            "block_ads": True,
            "max_pages": 1,
        }
        async with Client(server._build_server("127.0.0.1", 8000)) as client:
            for _ in range(2):
                result = await client.call_tool("browser_fetch_once", {"url": "https://example.com/1", **options})
                assert not result.is_error
                assert server._sessions == {"existing": existing}
                assert existing.session.mock_calls == []
        assert len(_FakeStealthySession.instances) == 2
        for session in _FakeStealthySession.instances:
            assert session.kwargs == expected
            assert session.fetch_calls == [{}]
            assert not session._is_alive


class TestBrowserFetchForwarding:
    """`browser_fetch` forwards its per-request params by name to the session's fetch()."""

    @pytest.fixture(autouse=True)
    def reset_fakes(self):
        _FakeStealthySession.instances = []

    @staticmethod
    def _fetch_call(fake: type[_FakeStealthySession]) -> dict[str, Any]:
        return fake.instances[0].fetch_calls[0]

    @pytest.mark.asyncio
    async def test_stealthy_browser_fetch_forwards_the_per_request_params(self, monkeypatch):
        """A stealthy session receives every stealthy per-request param, including explicit None values"""
        monkeypatch.setattr("scrapling.core.ai.server.AsyncStealthySession", _FakeStealthySession)
        server = ScraplingMCPServer()
        opened = await server.browser_open()

        await server.browser_fetch(url="https://example.com/1", session_id=opened.session_id)

        forwarded = self._fetch_call(_FakeStealthySession)
        assert forwarded == {
            "wait": 0,
            "timeout": 30000,
            "google_search": True,
            "network_idle": False,
            "load_dom": True,
            "pierce_shadow": False,
            "disable_resources": False,
            "wait_selector": None,
            "wait_selector_state": "attached",
            "extra_headers": None,
            "blocked_domains": None,
            "solve_cloudflare": False,
        }, forwarded
        assert "proxy" not in forwarded, "proxy is session-level (browser_open), never forwarded per request"

    @pytest.mark.asyncio
    async def test_stealthy_browser_fetch_forwards_solve_cloudflare(self, monkeypatch):
        """A stealthy session additionally receives solve_cloudflare"""
        monkeypatch.setattr("scrapling.core.ai.server.AsyncStealthySession", _FakeStealthySession)
        server = ScraplingMCPServer()
        opened = await server.browser_open()

        await server.browser_fetch(url="https://example.com/1", session_id=opened.session_id, solve_cloudflare=True)

        forwarded = self._fetch_call(_FakeStealthySession)
        assert forwarded.get("solve_cloudflare") is True, forwarded

    @pytest.mark.asyncio
    async def test_supplied_values_are_forwarded(self, monkeypatch):
        """Per-request overrides reach the session as given"""
        monkeypatch.setattr("scrapling.core.ai.server.AsyncStealthySession", _FakeStealthySession)
        server = ScraplingMCPServer()
        options = {
            "wait": 250,
            "timeout": 45000,
            "google_search": False,
            "network_idle": True,
            "load_dom": False,
            "pierce_shadow": True,
            "disable_resources": True,
            "wait_selector": "#main",
            "wait_selector_state": "visible",
            "extra_headers": {"X-Test": "value"},
            "blocked_domains": ["ads.example.com"],
            "solve_cloudflare": True,
        }
        async with Client(server._build_server("127.0.0.1", 8000)) as client:
            opened = await client.call_tool("browser_open", {"session_id": "browser"})
            assert not opened.is_error
            try:
                fetched = await client.call_tool(
                    "browser_fetch", {"url": "https://example.com/1", "session_id": "browser", **options}
                )
                assert not fetched.is_error
                assert self._fetch_call(_FakeStealthySession) == {**options, "blocked_domains": {"ads.example.com"}}
                assert _FakeStealthySession.instances[0]._config.max_pages == 1
            finally:
                closed = await client.call_tool("close_session", {"session_id": "browser"})
                assert not closed.is_error
        assert not _FakeStealthySession.instances[0]._is_alive

    @pytest.mark.asyncio
    async def test_unknown_session_raises(self):
        server = ScraplingMCPServer()
        with pytest.raises(ValueError, match="not found"):
            await server.browser_fetch(url="https://example.com/1", session_id="nope")


class TestModeSplitContract:
    """Session setup and per-request options must stay in sync with the library."""

    def test_browser_fetch_signature_matches_the_derived_fetch_keys(self):
        """browser_fetch exposes exactly the stealth per-request keys (plus url/session_id/extraction trio)"""
        params = set(inspect.signature(ScraplingMCPServer.browser_fetch).parameters) - {
            "self",
            "url",
            "session_id",
            "extraction_type",
            "css_selector",
            "main_content_only",
        }
        assert params == set(_STEALTH_FETCH_KEYS), (
            f"browser_fetch params drifted from _STEALTH_FETCH_KEYS: {params ^ set(_STEALTH_FETCH_KEYS)}"
        )

    def test_browser_fetch_defaults_match_the_library(self):
        """Each per-request default equals the library config default so the AI sees the real value"""
        defaults = {
            name: p.default
            for name, p in inspect.signature(ScraplingMCPServer.browser_fetch).parameters.items()
            if name in _STEALTH_FETCH_KEYS
        }
        library = models_default_values["StealthConfig"]
        for name, value in defaults.items():
            assert value == library[name], f"browser_fetch {name} default {value!r} != library {library[name]!r}"

    def test_browser_open_holds_no_per_request_params(self):
        """browser_open keeps browser-level params only, none of the per-request fetch keys"""
        params = set(inspect.signature(ScraplingMCPServer.browser_open).parameters)
        assert "session_type" not in params
        assert params.isdisjoint(_STEALTH_FETCH_KEYS), (
            f"browser_open still carries per-request params: {params & set(_STEALTH_FETCH_KEYS)}"
        )

    def test_proxy_is_session_level_not_per_request(self):
        """A session runs one tab, so proxy is set once on browser_open, never per request"""
        assert "proxy" in inspect.signature(ScraplingMCPServer.browser_open).parameters
        assert "proxy" not in inspect.signature(ScraplingMCPServer.browser_fetch).parameters
        assert "proxy" not in _STEALTH_FETCH_KEYS

    @pytest.mark.asyncio
    async def test_browser_open_forwards_proxy_to_the_session(self, monkeypatch):
        """The session-level proxy reaches the underlying session so it applies to every fetch"""
        monkeypatch.setattr("scrapling.core.ai.server.AsyncStealthySession", _FakeStealthySession)
        _FakeStealthySession.instances = []
        server = ScraplingMCPServer()

        await server.browser_open(proxy="http://user:pass@host:8080")

        assert _FakeStealthySession.instances[0].kwargs["proxy"] == "http://user:pass@host:8080"

    @pytest.mark.asyncio
    async def test_browser_open_preserves_stealth_session_options(self, monkeypatch):
        monkeypatch.setattr("scrapling.core.ai.server.AsyncStealthySession", _FakeStealthySession)
        server = ScraplingMCPServer()
        options = {
            "headless": False,
            "real_chrome": True,
            "timezone_id": "Europe/London",
            "locale": "en-GB",
            "useragent": "test-agent",
            "proxy": {"server": "http://host:8080", "username": "user", "password": "pass"},
            "cdp_url": "ws://127.0.0.1:9222/devtools/browser/test",
            "executable_path": "/tmp/chromium",
            "cookies": [{"name": "theme", "value": "dark", "url": "https://example.com"}],
            "hide_canvas": True,
            "block_webrtc": True,
            "allow_webgl": False,
            "additional_args": {"viewport": {"width": 1024, "height": 768}},
        }
        async with Client(server._build_server("127.0.0.1", 8000)) as client:
            tool = next(tool for tool in (await client.list_tools()).tools if tool.name == "browser_open")
            assert set(tool.input_schema["properties"]) == {"session_id", *options}
            assert not tool.input_schema.get("required")
            result = await client.call_tool("browser_open", {"session_id": "browser", **options})
            assert not result.is_error
            assert result.structured_content is not None
            assert result.structured_content["session_type"] == "stealthy"
            session = _FakeStealthySession.instances[-1]
            assert session.kwargs == {**options, "block_ads": True, "record_requests": True}
            assert server._sessions["browser"].session is session
            closed = await client.call_tool("close_session", {"session_id": "browser"})
            assert not closed.is_error
        assert not session._is_alive

    def test_session_metadata_lists_only_supported_types(self):
        for model in (SessionInfo, SessionCreatedModel):
            assert set(model.model_json_schema()["properties"]["session_type"]["enum"]) == {"stealthy", "static"}


class TestSessionSettingsReceipt:
    """browser_open and list_sessions return the session's effective settings."""

    def test_session_settings_extracts_json_safe_fields(self):
        """The helper keeps JSON primitives and drops the rest (callables, structs, sequences)"""
        settings = _session_settings(AsyncStealthySession(headless=True))
        assert settings["headless"] is True
        assert settings["timeout"] == 30000
        assert "cookies" not in settings, "non-primitive fields (list) must be dropped"
        assert all(isinstance(v, (str, int, float, bool)) or v is None for v in settings.values()), settings

    def test_cdp_session_reports_empty_settings(self):
        """A CDP session drives a remote browser, so the local config is not reported as its settings"""
        assert _session_settings(AsyncStealthySession(cdp_url="ws://127.0.0.1:9222/devtools/browser/x")) == {}

    def test_static_session_settings_extracts_json_safe_fields(self):
        """A static session reports its HTTP defaults (impersonate, proxy, timeout, ...)"""
        settings = _session_settings(FetcherSession(impersonate="chrome", proxy=None))
        assert settings["impersonate"] == "chrome"
        assert settings["proxy"] is None
        assert settings["timeout"] == 30
        assert settings["stealthy_headers"] is True
        assert "headers" not in settings, "non-primitive fields (dict) must be dropped"
        assert all(isinstance(v, (str, int, float, bool)) or v is None for v in settings.values()), settings

    @pytest.mark.asyncio
    async def test_browser_open_and_list_report_the_receipt(self, monkeypatch):
        """browser_open returns the receipt and list_sessions reports the same one"""
        monkeypatch.setattr("scrapling.core.ai.server.AsyncStealthySession", _FakeStealthySession)
        server = ScraplingMCPServer()

        created = await server.browser_open()

        assert created.settings["headless"] is True
        listed = await server.list_sessions()
        assert listed[0].settings == created.settings


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
    async def test_screenshot_png_with_stealthy_session(self, server, test_url):
        """PNG screenshot via a stealthy session returns image and url content blocks"""
        opened = await server.browser_open(headless=True)
        try:
            await server.browser_fetch(url=test_url, session_id=opened.session_id)
            result = await server.browser_screenshot(session_id=opened.session_id)
            assert isinstance(result, list) and len(result) == 2
            assert isinstance(result[0], ImageContent)
            assert result[0].mime_type == "image/png"
            assert base64.b64decode(result[0].data).startswith(b"\x89PNG\r\n\x1a\n")
            assert isinstance(result[1], TextContent)
            assert result[1].text == test_url
        finally:
            await server.close_session(opened.session_id)

    @pytest.mark.asyncio
    async def test_screenshot_jpeg_with_quality(self, server, test_url):
        """JPEG screenshot with quality parameter via a stealthy session"""
        opened = await server.browser_open(headless=True)
        try:
            await server.browser_fetch(url=test_url, session_id=opened.session_id)
            result = await server.browser_screenshot(session_id=opened.session_id, image_type="jpeg", quality=80)
            assert isinstance(result[0], ImageContent)
            assert result[0].mime_type == "image/jpeg"
            jpeg = base64.b64decode(result[0].data)
            assert jpeg.startswith(b"\xff\xd8") and jpeg.endswith(b"\xff\xd9")
        finally:
            await server.close_session(opened.session_id)

    @pytest.mark.asyncio
    async def test_screenshot_full_page_taller_than_viewport(self, server):
        """full_page=True produces an image taller than the viewport-only capture"""
        tall_html = b"<html><body><div style='height:5000px;background:#abc'></div></body></html>"
        with _serve_html(tall_html) as tall_url:
            opened = await server.browser_open(headless=True)
            try:
                await server.browser_fetch(url=tall_url, session_id=opened.session_id)
                viewport_result = await server.browser_screenshot(session_id=opened.session_id, full_page=False)
                full_result = await server.browser_screenshot(session_id=opened.session_id, full_page=True)

                viewport_png = base64.b64decode(viewport_result[0].data)
                full_png = base64.b64decode(full_result[0].data)

                assert _png_height(full_png) > _png_height(viewport_png)
            finally:
                await server.close_session(opened.session_id)

    @pytest.mark.asyncio
    async def test_screenshot_invalid_session_id_raises(self, server, test_url):
        """Unknown session_id raises ValueError"""
        with pytest.raises(ValueError, match="not found"):
            await server.browser_screenshot(session_id="does-not-exist")

    @pytest.mark.asyncio
    async def test_screenshot_quality_with_png_raises(self, server, test_url):
        """quality is rejected when image_type is png"""
        opened = await server.browser_open(headless=True)
        try:
            with pytest.raises(ValueError, match="quality"):
                await server.browser_screenshot(session_id=opened.session_id, image_type="png", quality=90)
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

        assert {tool.name for tool in built._tool_manager.list_tools()} == MCP_TOOLS

    def test_http_without_a_token_refuses_to_serve(self, monkeypatch):
        """The streamable-http transport requires authentication unless the caller explicitly opts out"""
        monkeypatch.delenv(MCP_AUTH_TOKEN_ENV, raising=False)
        server = ScraplingMCPServer()

        with pytest.raises(ValueError, match="without authentication"):
            server.serve(True, "0.0.0.0", 8000)

    def test_stdio_without_a_token_still_serves(self, monkeypatch):
        """stdio is only reachable by the program that started it, so it stays unauthenticated"""
        monkeypatch.delenv(MCP_AUTH_TOKEN_ENV, raising=False)
        server = ScraplingMCPServer()

        with patch.object(MCPServer, "run") as mocked_run:
            server.serve(False, "0.0.0.0", 8000)

        mocked_run.assert_called_once_with()

    def test_http_serves_unauthenticated_when_explicitly_allowed(self, monkeypatch):
        """`--no-auth` is the opt-out, and the server still warns that it's unprotected"""
        monkeypatch.delenv(MCP_AUTH_TOKEN_ENV, raising=False)
        server = ScraplingMCPServer()

        with patch.object(MCPServer, "run") as mocked_run:
            server.serve(True, "0.0.0.0", 8000, allow_unauthenticated=True)

        assert mocked_run.call_args.kwargs["transport"] == "streamable-http"
        assert server._build_server("0.0.0.0", 8000).settings.auth is None

    def test_token_wins_over_the_opt_out(self, monkeypatch):
        """Passing both keeps authentication on instead of silently dropping the token"""
        monkeypatch.delenv(MCP_AUTH_TOKEN_ENV, raising=False)
        server = ScraplingMCPServer(auth_token=SHARED_KEY)

        with patch.object(MCPServer, "run") as mocked_run:
            server.serve(True, "0.0.0.0", 8000, allow_unauthenticated=True)

        assert mocked_run.call_args.kwargs["transport"] == "streamable-http"
        assert server._build_server("0.0.0.0", 8000).settings.auth is not None

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
        """Single-page and session tools retain their output schemas."""
        server = ScraplingMCPServer()._build_server("127.0.0.1", 8000)
        async with Client(server) as client:
            assert client.instructions
            assert "dynamic" not in client.instructions.lower()
            tools = {tool.name: tool for tool in (await client.list_tools()).tools}
            for name in (
                "bulk_get",
                "browser_fetch_many_once",
                "browser_type",
                "browser_fill_form",
                "browser_fill_fields",
                "browser_mouse",
                "browser_wait",
                "browser_press_key",
                "open_session",
                "session_fetch",
                "screenshot",
                "browser_mouse_move",
                "browser_mouse_wheel",
                "browser_click",
                "browser_mouse_move_xy",
                "fetch",
                "bulk_fetch",
                "stealthy_fetch",
                "bulk_stealthy_fetch",
                "browser_stealth_fetch_once",
                "browser_stealth_fetch_many_once",
            ):
                result = await client.call_tool(name, {})
                assert result.is_error

        assert set(tools) == MCP_TOOLS
        assert {"bulk_get", "browser_fetch_many_once"}.isdisjoint(tools)
        assert tools["browser_screenshot"].output_schema is None
        assert tools["browser_extract"].output_schema is None
        assert tools["browser_actions"].output_schema is None
        assert tools["browser_evaluate"].output_schema is None
        assert {
            "browser_type",
            "browser_fill_form",
            "browser_fill_fields",
            "browser_mouse",
            "browser_wait",
            "browser_press_key",
            "session_snapshot",
            "open_session",
            "session_fetch",
            "screenshot",
            "browser_mouse_move",
            "browser_mouse_wheel",
            "browser_click",
            "browser_mouse_move_xy",
            "fetch",
            "bulk_fetch",
            "stealthy_fetch",
            "bulk_stealthy_fetch",
            "browser_stealth_fetch_once",
            "browser_stealth_fetch_many_once",
        }.isdisjoint(tools)
        assert all(
            tool.output_schema is not None
            for name, tool in tools.items()
            if name
            not in (
                "browser_screenshot",
                "browser_extract",
                "browser_actions",
                "browser_evaluate",
            )
        )

    @pytest.mark.asyncio
    async def test_fetch_tools_keep_single_url_session_schemas(self):
        """Session tools keep one required URL and their current defaults."""
        server = ScraplingMCPServer()._build_server("127.0.0.1", 8000)
        async with Client(server) as client:
            tools = {tool.name: tool for tool in (await client.list_tools()).tools}

        for name in ("session_make_request", "browser_fetch"):
            props = tools[name].input_schema["properties"]
            assert props["url"]["type"] == "string"
            assert "urls" not in props
            assert set(tools[name].input_schema["required"]) >= {"url", "session_id"}

        static_props = tools["session_make_request"].input_schema["properties"]
        assert static_props["method"]["default"] == "GET"
        assert "data" in static_props and "json" in static_props
        assert "proxy" not in static_props and "impersonate" not in static_props, "session-level params leaked"
        assert set(tools["open_request_session"].input_schema["properties"]) == {"session_id", "impersonate", "proxy"}

        session_props = tools["browser_fetch"].input_schema["properties"]
        assert session_props["timeout"]["default"] == 30000
        assert session_props["google_search"]["default"] is True
        assert session_props["pierce_shadow"]["type"] == "boolean"
        assert session_props["pierce_shadow"]["default"] is False
        assert session_props["solve_cloudflare"]["type"] == "boolean"
        assert session_props["solve_cloudflare"]["default"] is False
        assert session_props["extraction_type"]["default"] == "markdown"
        assert set(session_props["extraction_type"]["enum"]) == {"markdown", "html", "text", "snapshot"}
        assert {"depth", "boxes"}.isdisjoint(session_props)

        open_props = tools["browser_open"].input_schema["properties"]
        for option in ("hide_canvas", "block_webrtc"):
            assert open_props[option]["type"] == "boolean"
            assert open_props[option]["default"] is False
        assert open_props["allow_webgl"]["default"] is True
        assert open_props["additional_args"]["default"] is None
        open_props = set(open_props)
        assert open_props.isdisjoint(_STEALTH_FETCH_KEYS), (
            f"browser_open still exposes per-request params: {open_props & set(_STEALTH_FETCH_KEYS)}"
        )

    @pytest.mark.asyncio
    async def test_one_shot_schemas_keep_original_options_and_defaults(self):
        async with Client(ScraplingMCPServer()._build_server("127.0.0.1", 8000)) as client:
            tools = {tool.name: tool for tool in (await client.list_tools()).tools}
        for name in ("make_request", "browser_fetch_once"):
            props = tools[name].input_schema["properties"]
            assert props["url"]["type"] == "string"
            assert {"urls", "session_id"}.isdisjoint(props)
            assert tools[name].input_schema["required"] == ["url"]
            assert props["extraction_type"]["default"] == "markdown"
            assert set(props["extraction_type"]["enum"]) == {"markdown", "html", "text"}
            assert tools[name].output_schema == tools["session_make_request"].output_schema
        request_props = tools["make_request"].input_schema["properties"]
        assert request_props["method"]["default"] == "GET"
        assert {"data", "json", "proxy", "impersonate"} <= request_props.keys()
        assert request_props["timeout"]["default"] == 30
        assert request_props["follow_redirects"]["default"] == "safe"
        props = tools["browser_fetch_once"].input_schema["properties"]
        assert props["timeout"]["default"] == 30000
        assert props["google_search"]["default"] is True
        for option in ("pierce_shadow", "hide_canvas", "block_webrtc", "solve_cloudflare"):
            assert props[option]["type"] == "boolean"
            assert props[option]["default"] is False
        assert props["allow_webgl"]["default"] is True
        assert props["additional_args"]["default"] is None
        assert not hasattr(ScraplingMCPServer, "bulk_get")
        assert not hasattr(ScraplingMCPServer, "browser_fetch_many_once")

    @pytest.mark.asyncio
    @pytest.mark.parametrize("tool", ["make_request", "browser_fetch_once"])
    @pytest.mark.parametrize("args", [{"url": ["https://example.com"]}, {"urls": ["https://example.com"]}])
    async def test_one_shot_tools_reject_batches_before_opening_sessions(self, monkeypatch, tool, args):
        static = Mock()
        browser = Mock()
        monkeypatch.setattr("scrapling.core.ai.server.FetcherSession", static)
        monkeypatch.setattr("scrapling.core.ai.server.AsyncStealthySession", browser)
        async with Client(ScraplingMCPServer()._build_server("127.0.0.1", 8000)) as client:
            result = await client.call_tool(tool, args)
        assert result.is_error
        assert result.content and isinstance(result.content[0], TextContent)
        assert "url" in result.content[0].text
        static.assert_not_called()
        browser.assert_not_called()

    @pytest.mark.asyncio
    @pytest.mark.parametrize("tool, session_type", [("browser_fetch", "stealthy"), ("session_make_request", "static")])
    @pytest.mark.parametrize(
        "args, field",
        [
            ({"url": ["https://example.com/1", "https://example.com/2"], "session_id": "test"}, "url"),
            ({"urls": ["https://example.com/1", "https://example.com/2"], "session_id": "test"}, "url"),
            ({"url": "https://example.com/1"}, "session_id"),
        ],
    )
    async def test_session_fetch_validation_prevents_batches_and_missing_sessions(
        self, tool, session_type, args, field
    ):
        server = ScraplingMCPServer()
        session = Mock(_is_alive=True)
        server._sessions["test"] = _SessionEntry(session, session_type)
        async with Client(server._build_server("127.0.0.1", 8000)) as client:
            result = await client.call_tool(tool, args)
        assert result.is_error
        assert result.content and isinstance(result.content[0], TextContent)
        assert field in result.content[0].text
        assert session.mock_calls == []

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
        assert set(annotations) == MCP_TOOLS
        for name in (
            "make_request",
            "browser_fetch_once",
            "browser_fetch",
            "session_make_request",
            "browser_extract",
            "browser_screenshot",
        ):
            assert annotations[name].read_only_hint is True
            assert annotations[name].open_world_hint is True
        for name in ("browser_open", "open_request_session", "close_session"):
            assert annotations[name].read_only_hint is False
            assert annotations[name].destructive_hint is False
            assert annotations[name].open_world_hint is True
        assert annotations["list_sessions"].read_only_hint is True
        assert annotations["list_sessions"].open_world_hint is False
        for name in ("browser_actions", "browser_evaluate"):
            assert annotations[name].read_only_hint is False
            assert annotations[name].destructive_hint is True
            assert annotations[name].idempotent_hint is False
            assert annotations[name].open_world_hint is True


@pytest.mark.asyncio
async def test_shadow_option_changes_per_session_request(monkeypatch):
    monkeypatch.setattr("scrapling.core.ai.server.AsyncStealthySession", _FakeStealthySession)
    server = ScraplingMCPServer()._build_server("127.0.0.1", 8000)
    async with Client(server) as client:
        opened = await client.call_tool("browser_open", {"session_id": "shadow-test"})
        assert not opened.is_error
        try:
            for args, expected in [({"pierce_shadow": True}, True), ({"pierce_shadow": False}, False), ({}, False)]:
                result = await client.call_tool(
                    "browser_fetch", {"url": "https://example.com", "session_id": "shadow-test", **args}
                )
                assert not result.is_error
                assert _FakeStealthySession.instances[-1].fetch_calls[-1]["pierce_shadow"] is expected
        finally:
            await client.call_tool("close_session", {"session_id": "shadow-test"})
    assert not _FakeStealthySession.instances[-1]._is_alive


@pytest.mark.asyncio
@pytest.mark.parametrize("enabled", [False, True])
async def test_shadow_option_reaches_browser_session(monkeypatch, enabled):
    monkeypatch.setattr("scrapling.core.ai.server.AsyncStealthySession", _FakeStealthySession)
    server = ScraplingMCPServer()._build_server("127.0.0.1", 8000)
    async with Client(server) as client:
        result = await client.call_tool("browser_fetch_once", {"url": "https://example.com", "pierce_shadow": enabled})
    assert not result.is_error
    assert _FakeStealthySession.instances[-1].kwargs["pierce_shadow"] is enabled
    assert not _FakeStealthySession.instances[-1]._is_alive
