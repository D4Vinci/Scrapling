import base64
import inspect
import struct
from typing import Any
from contextlib import contextmanager
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread
from unittest.mock import patch

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
    _normalize_credentials,
    _page_pool_size,
    _session_settings,
    _StaticTokenVerifier,
    _STEALTH_FETCH_KEYS,
    _translate_response,
)
from scrapling.engines._browsers._validators import PlaywrightConfig, StealthConfig, models_default_values, validate
from scrapling.fetchers import AsyncDynamicSession, AsyncStealthySession, FetcherSession


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


class _FakeAsyncBrowserSession:
    instances: list["_FakeAsyncBrowserSession"] = []
    _config_model: Any = PlaywrightConfig

    def __init__(self, **kwargs: Any) -> None:
        self.kwargs = kwargs
        self.fetch_calls: list[dict[str, Any]] = []
        self._is_alive = False
        # `executable_path` is validated against the filesystem; drop it so the fake accepts test paths.
        self._config = validate(
            {name: value for name, value in kwargs.items() if name != "executable_path"}, self._config_model
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


class _FakeDynamicSession(_FakeAsyncBrowserSession):
    instances = []


class _FakeStealthySession(_FakeAsyncBrowserSession):
    instances = []
    _config_model = StealthConfig


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
    async def test_make_request_tool(self, server, test_url):
        """Test the make_request tool method with a default GET"""
        result = await server.make_request(url=test_url, extraction_type="markdown")
        assert isinstance(result, ResponseModel)
        assert result.status == 200
        assert result.url == test_url

    @pytest.mark.asyncio
    async def test_make_request_post_tool(self, server, httpbin):
        """Test the make_request tool method with a POST body"""
        result = await server.make_request(
            url=f"{httpbin.url}/post", method="POST", json={"key": "value"}, extraction_type="text"
        )
        assert isinstance(result, ResponseModel)
        assert result.status == 200

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
    async def test_session_fetch_reuses_the_session(self, server, test_url):
        """Test fetching a page twice through a persistent dynamic session"""
        result = await server.open_session(session_type="dynamic", headless=True)
        session_id = result.session_id

        response = await server.session_fetch(url=test_url, session_id=session_id)
        assert isinstance(response, ResponseModel)
        assert response.status == 200

        # Fetch again with the same session (reuse)
        response2 = await server.session_fetch(url=test_url, session_id=session_id)
        assert isinstance(response2, ResponseModel)
        assert response2.status == 200

        await server.close_session(session_id)

    @pytest.mark.asyncio
    async def test_session_fetch_accepts_per_request_overrides(self, server, test_url):
        """A per-request override is honored on a session fetch"""
        result = await server.open_session(session_type="dynamic", headless=True)
        session_id = result.session_id

        response = await server.session_fetch(url=test_url, session_id=session_id, network_idle=True, timeout=45000)
        assert isinstance(response, ResponseModel)
        assert response.status == 200

        await server.close_session(session_id)

    @pytest.mark.asyncio
    async def test_close_nonexistent_session(self, server):
        """Test closing a session that doesn't exist"""
        with pytest.raises(ValueError, match="not found"):
            await server.close_session("nonexistent")

    @pytest.mark.asyncio
    async def test_session_fetch_with_nonexistent_session(self, server, test_url):
        """Test fetching with a session ID that doesn't exist"""
        with pytest.raises(ValueError, match="not found"):
            await server.session_fetch(url=test_url, session_id="nonexistent")

    @pytest.mark.asyncio
    async def test_session_fetch_with_closed_session(self, server, test_url):
        """Test fetching with a session that has been closed"""
        result = await server.open_session(session_type="dynamic", headless=True)
        session_id = result.session_id
        await server.close_session(session_id)

        with pytest.raises(ValueError, match="not found"):
            await server.session_fetch(url=test_url, session_id=session_id)

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


class TestStaticSessionManagement:
    """Test persistent requests (HTTP) session management"""

    @pytest.fixture
    def server(self):
        return ScraplingMCPServer()

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
        monkeypatch.setattr("scrapling.core.ai.AsyncDynamicSession", _FakeDynamicSession)
        await server.open_request_session(session_id="shared")
        with pytest.raises(ValueError, match="already exists"):
            await server.open_session(session_type="dynamic", session_id="shared")
        await server.close_session("shared")

    @pytest.mark.asyncio
    async def test_session_make_request_requires_a_static_session(self, server, monkeypatch):
        """session_make_request rejects browser sessions"""
        monkeypatch.setattr("scrapling.core.ai.AsyncDynamicSession", _FakeDynamicSession)
        await server.open_session(session_type="dynamic", session_id="browser")
        with pytest.raises(ValueError, match="requires a 'static' session"):
            await server.session_make_request(url="https://example.com", session_id="browser")
        await server.close_session("browser")

    @pytest.mark.asyncio
    async def test_session_fetch_and_screenshot_reject_static_sessions(self, server):
        """The browser session tools refuse a static session with a clear error"""
        await server.open_request_session(session_id="st2")
        with pytest.raises(ValueError, match="session_make_request"):
            await server.session_fetch(url="https://example.com", session_id="st2")
        with pytest.raises(ValueError, match="can't take screenshots"):
            await server.screenshot(url="https://example.com", session_id="st2")
        await server.close_session("st2")


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


class TestSessionFetchForwarding:
    """`session_fetch` forwards its per-request params by name to the session's fetch()."""

    @pytest.fixture(autouse=True)
    def reset_fakes(self):
        _FakeDynamicSession.instances = []
        _FakeStealthySession.instances = []

    @staticmethod
    def _fetch_call(fake: type[_FakeAsyncBrowserSession]) -> dict[str, Any]:
        return fake.instances[0].fetch_calls[0]

    @pytest.mark.asyncio
    async def test_dynamic_session_fetch_forwards_the_per_request_params(self, monkeypatch):
        """A dynamic session receives every dynamic per-request param, including explicit None values"""
        monkeypatch.setattr("scrapling.core.ai.AsyncDynamicSession", _FakeDynamicSession)
        server = ScraplingMCPServer()
        opened = await server.open_session(session_type="dynamic")

        await server.session_fetch(url="https://example.com/1", session_id=opened.session_id)

        forwarded = self._fetch_call(_FakeDynamicSession)
        assert forwarded == {
            "wait": 0,
            "timeout": 30000,
            "google_search": True,
            "network_idle": False,
            "load_dom": True,
            "disable_resources": False,
            "wait_selector": None,
            "wait_selector_state": "attached",
            "extra_headers": None,
            "blocked_domains": None,
        }, forwarded
        assert "solve_cloudflare" not in forwarded, "solve_cloudflare must not reach a dynamic session"
        assert "proxy" not in forwarded, "proxy is session-level (open_session), never forwarded per request"

    @pytest.mark.asyncio
    async def test_stealthy_session_fetch_forwards_solve_cloudflare(self, monkeypatch):
        """A stealthy session additionally receives solve_cloudflare"""
        monkeypatch.setattr("scrapling.core.ai.AsyncStealthySession", _FakeStealthySession)
        server = ScraplingMCPServer()
        opened = await server.open_session(session_type="stealthy")

        await server.session_fetch(url="https://example.com/1", session_id=opened.session_id, solve_cloudflare=True)

        forwarded = self._fetch_call(_FakeStealthySession)
        assert forwarded.get("solve_cloudflare") is True, forwarded

    @pytest.mark.asyncio
    async def test_supplied_values_are_forwarded(self, monkeypatch):
        """Per-request overrides reach the session as given"""
        monkeypatch.setattr("scrapling.core.ai.AsyncDynamicSession", _FakeDynamicSession)
        server = ScraplingMCPServer()
        opened = await server.open_session(session_type="dynamic")

        await server.session_fetch(
            url="https://example.com/1", session_id=opened.session_id, timeout=45000, wait_selector="#main"
        )

        forwarded = self._fetch_call(_FakeDynamicSession)
        assert forwarded["timeout"] == 45000
        assert forwarded["wait_selector"] == "#main"

    @pytest.mark.asyncio
    async def test_solve_cloudflare_on_dynamic_session_raises(self, monkeypatch):
        """Asking a dynamic session to solve Cloudflare is a clear error, not a silent no-op"""
        monkeypatch.setattr("scrapling.core.ai.AsyncDynamicSession", _FakeDynamicSession)
        server = ScraplingMCPServer()
        opened = await server.open_session(session_type="dynamic")

        with pytest.raises(ValueError, match="can't solve Cloudflare"):
            await server.session_fetch(url="https://example.com/1", session_id=opened.session_id, solve_cloudflare=True)

    @pytest.mark.asyncio
    async def test_unknown_session_raises(self):
        server = ScraplingMCPServer()
        with pytest.raises(ValueError, match="not found"):
            await server.session_fetch(url="https://example.com/1", session_id="nope")


class TestModeSplitContract:
    """The one-shot vs session split is derived from the library TypedDicts and must stay in sync."""

    def test_session_fetch_signature_matches_the_derived_fetch_keys(self):
        """session_fetch exposes exactly the stealth per-request keys (plus url/session_id/extraction trio)"""
        params = set(inspect.signature(ScraplingMCPServer.session_fetch).parameters) - {
            "self",
            "url",
            "session_id",
            "extraction_type",
            "css_selector",
            "main_content_only",
        }
        assert params == set(_STEALTH_FETCH_KEYS), (
            f"session_fetch params drifted from _STEALTH_FETCH_KEYS: {params ^ set(_STEALTH_FETCH_KEYS)}"
        )

    def test_session_fetch_defaults_match_the_library(self):
        """Each per-request default equals the library config default so the AI sees the real value"""
        defaults = {
            name: p.default
            for name, p in inspect.signature(ScraplingMCPServer.session_fetch).parameters.items()
            if name in _STEALTH_FETCH_KEYS
        }
        library = models_default_values["StealthConfig"]
        for name, value in defaults.items():
            assert value == library[name], f"session_fetch {name} default {value!r} != library {library[name]!r}"

    def test_one_shot_fetch_tools_have_no_session_id(self):
        """The one-shot tools no longer accept session_id"""
        for tool in (
            ScraplingMCPServer.fetch,
            ScraplingMCPServer.bulk_fetch,
            ScraplingMCPServer.stealthy_fetch,
            ScraplingMCPServer.bulk_stealthy_fetch,
        ):
            assert "session_id" not in inspect.signature(tool).parameters, f"{tool.__name__} still takes session_id"

    def test_open_session_holds_no_per_request_params(self):
        """open_session keeps browser-level params only, none of the per-request fetch keys"""
        params = set(inspect.signature(ScraplingMCPServer.open_session).parameters)
        assert params.isdisjoint(_STEALTH_FETCH_KEYS), (
            f"open_session still carries per-request params: {params & set(_STEALTH_FETCH_KEYS)}"
        )

    def test_proxy_is_session_level_not_per_request(self):
        """A session runs one tab, so proxy is set once on open_session, never per request"""
        assert "proxy" in inspect.signature(ScraplingMCPServer.open_session).parameters
        assert "proxy" not in inspect.signature(ScraplingMCPServer.session_fetch).parameters
        assert "proxy" not in _STEALTH_FETCH_KEYS

    @pytest.mark.asyncio
    async def test_open_session_forwards_proxy_to_the_session(self, monkeypatch):
        """The session-level proxy reaches the underlying session so it applies to every fetch"""
        monkeypatch.setattr("scrapling.core.ai.AsyncDynamicSession", _FakeDynamicSession)
        _FakeDynamicSession.instances = []
        server = ScraplingMCPServer()

        await server.open_session(session_type="dynamic", proxy="http://user:pass@host:8080")

        assert _FakeDynamicSession.instances[0].kwargs["proxy"] == "http://user:pass@host:8080"


class TestSessionSettingsReceipt:
    """open_session and list_sessions return the session's effective settings."""

    def test_session_settings_extracts_json_safe_fields(self):
        """The helper keeps JSON primitives and drops the rest (callables, structs, sequences)"""
        settings = _session_settings(AsyncStealthySession(headless=True))
        assert settings["headless"] is True
        assert settings["timeout"] == 30000
        assert "cookies" not in settings, "non-primitive fields (list) must be dropped"
        assert all(isinstance(v, (str, int, float, bool)) or v is None for v in settings.values()), settings

    def test_cdp_session_reports_empty_settings(self):
        """A CDP session drives a remote browser, so the local config is not reported as its settings"""
        assert _session_settings(AsyncDynamicSession(cdp_url="ws://127.0.0.1:9222/devtools/browser/x")) == {}

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
    async def test_open_session_and_list_report_the_receipt(self, monkeypatch):
        """open_session returns the receipt and list_sessions reports the same one"""
        monkeypatch.setattr("scrapling.core.ai.AsyncDynamicSession", _FakeDynamicSession)
        server = ScraplingMCPServer()

        created = await server.open_session(session_type="dynamic")

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

        assert len(built._tool_manager.list_tools()) == 13

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
        """All 13 tools are advertised, and only the screenshot tool skips the structured output schema"""
        server = ScraplingMCPServer()._build_server("127.0.0.1", 8000)
        async with Client(server) as client:
            assert client.instructions
            tools = {tool.name: tool for tool in (await client.list_tools()).tools}

        assert len(tools) == 13
        assert tools["screenshot"].output_schema is None
        assert all(tool.output_schema is not None for name, tool in tools.items() if name != "screenshot")

    @pytest.mark.asyncio
    async def test_fetch_tools_expose_real_defaults_and_no_session_id(self):
        """The one-shot tools show real defaults in their schema and no longer take session_id"""
        server = ScraplingMCPServer()._build_server("127.0.0.1", 8000)
        async with Client(server) as client:
            tools = {tool.name: tool for tool in (await client.list_tools()).tools}

        for name in ("fetch", "bulk_fetch", "stealthy_fetch", "bulk_stealthy_fetch"):
            props = tools[name].input_schema["properties"]
            assert "session_id" not in props, f"{name} still exposes session_id"
            assert props["timeout"]["default"] == 30000, f"{name} hides the real timeout default"
            assert props["google_search"]["default"] is True

        request_props = tools["make_request"].input_schema["properties"]
        assert request_props["method"]["default"] == "GET"
        assert "data" in request_props and "json" in request_props
        assert "method" not in tools["bulk_get"].input_schema["properties"]

        static_props = tools["session_make_request"].input_schema["properties"]
        assert static_props["method"]["default"] == "GET"
        assert "proxy" not in static_props and "impersonate" not in static_props, "session-level params leaked"
        assert set(tools["session_make_request"].input_schema["required"]) >= {"url", "session_id"}
        assert set(tools["open_request_session"].input_schema["properties"]) == {"session_id", "impersonate", "proxy"}

        session_props = tools["session_fetch"].input_schema["properties"]
        assert session_props["timeout"]["default"] == 30000
        assert "solve_cloudflare" in session_props
        assert set(tools["session_fetch"].input_schema["required"]) >= {"url", "session_id"}

        open_props = set(tools["open_session"].input_schema["properties"])
        assert open_props.isdisjoint(_STEALTH_FETCH_KEYS), (
            f"open_session still exposes per-request params: {open_props & set(_STEALTH_FETCH_KEYS)}"
        )

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
        assert len(annotations) == 13
        for name in (
            "make_request",
            "bulk_get",
            "fetch",
            "bulk_fetch",
            "stealthy_fetch",
            "bulk_stealthy_fetch",
            "session_fetch",
            "session_make_request",
            "screenshot",
        ):
            assert annotations[name].read_only_hint is True
            assert annotations[name].open_world_hint is True
        for name in ("open_session", "open_request_session", "close_session"):
            assert annotations[name].read_only_hint is False
            assert annotations[name].destructive_hint is False
            assert annotations[name].open_world_hint is True
        assert annotations["list_sessions"].read_only_hint is True
        assert annotations["list_sessions"].open_world_hint is False
