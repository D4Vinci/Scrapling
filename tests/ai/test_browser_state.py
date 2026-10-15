from contextlib import asynccontextmanager
from errno import EISDIR, ENOENT
from json import loads
from os import getenv, strerror
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest
from mcp.client import Client
from mcp.types import CallToolResult, TextContent

from scrapling.core._types import Any, AsyncGenerator
from scrapling.core.ai import ScraplingMCPServer
from scrapling.core.ai.server import _SessionEntry
from tests.fetchers.test_session_state import HTML, READ_STATE, SAVED_STATE, URL, WRITE_STATE, _check_json


def _status(result: CallToolResult, text: str) -> None:
    assert not result.is_error and result.structured_content is None
    assert result.content == [TextContent(type="text", text=text)]


@asynccontextmanager
async def _browser() -> AsyncGenerator[tuple[Client, Any], None]:
    server = ScraplingMCPServer(executable_path=getenv("SCRAPLING_EXECUTABLE_PATH"))
    async with Client(server._build_server("127.0.0.1", 8000)) as client:
        opened = await client.call_tool("browser_open", {"session_id": "browser"})
        assert not opened.is_error
        try:
            session = server._sessions["browser"].session
            await session.context.route("**/*", lambda route: route.fulfill(body=HTML, content_type="text/html"))
            yield client, session
        finally:
            assert not (await client.call_tool("close_session", {"session_id": "browser"})).is_error


@pytest.mark.asyncio
@pytest.mark.parametrize("operation", ["save", "load"])
async def test_browser_state_schema_and_empty_path(operation: str) -> None:
    server = ScraplingMCPServer()
    session = SimpleNamespace(_is_alive=True, save_state=AsyncMock(), load_state=AsyncMock())
    server._sessions["browser"] = _SessionEntry(session, "stealthy")
    name = f"browser_{operation}_state"
    async with Client(server._build_server("127.0.0.1", 8000)) as client:
        tool = next(tool for tool in (await client.list_tools()).tools if tool.name == name)
        assert tool.title == f"{operation.title()} browser state"
        assert tool.input_schema["required"] == ["session_id", "path"]
        properties = tool.input_schema["properties"]
        assert set(properties) == {"session_id", "path"}
        assert properties["path"]["type"] == "string" and properties["path"]["minLength"] == 1
        assert tool.output_schema is None
        assert tool.annotations is not None
        assert tool.annotations.read_only_hint is False
        assert tool.annotations.destructive_hint is True
        assert tool.annotations.idempotent_hint is False
        assert tool.annotations.open_world_hint is True
        result = await client.call_tool(name, {"session_id": "browser", "path": ""})
    assert result.is_error and result.structured_content is None
    assert isinstance(result.content[0], TextContent) and "path" in result.content[0].text
    session.save_state.assert_not_awaited()
    session.load_state.assert_not_awaited()


@pytest.mark.asyncio
@pytest.mark.parametrize("operation", ["save", "load"])
@pytest.mark.parametrize(
    "kind, message",
    [("unknown", "not found"), ("dead", "no longer alive"), ("static", "requires a 'stealthy' session")],
)
async def test_browser_state_requires_live_browser(operation: str, kind: str, message: str, tmp_path: Path) -> None:
    server = ScraplingMCPServer()
    session = SimpleNamespace(_is_alive=kind != "dead", save_state=AsyncMock(), load_state=AsyncMock())
    if kind != "unknown":
        server._sessions["browser"] = _SessionEntry(session, "static" if kind == "static" else "stealthy")
    path = tmp_path / "state.json"
    async with Client(server._build_server("127.0.0.1", 8000)) as client:
        result = await client.call_tool(f"browser_{operation}_state", {"session_id": "browser", "path": str(path)})
    assert result.is_error and result.structured_content is None
    assert isinstance(result.content[0], TextContent) and message in result.content[0].text
    assert not path.exists()
    session.save_state.assert_not_awaited()
    session.load_state.assert_not_awaited()


@pytest.mark.browser
@pytest.mark.asyncio
async def test_browser_state_live_round_trip(tmp_path: Path) -> None:
    path, native_path = tmp_path / "state.json", tmp_path / "native.json"
    arguments = {"session_id": "browser", "path": str(path)}
    fetch = {"session_id": "browser", "url": URL, "google_search": False}
    async with _browser() as (client, source):
        assert source.page_pool.pages_count == 0
        _status(await client.call_tool("browser_save_state", arguments), "State saved.")
        assert loads(path.read_text())["cookies"] == loads(path.read_text())["origins"] == []
        assert source.page_pool.pages_count == 0
        assert not (await client.call_tool("browser_fetch", fetch)).is_error
        await source.page_pool.pages[0].page.evaluate(WRITE_STATE, "saved")
        _status(await client.call_tool("browser_save_state", arguments), "State saved.")
        _check_json(path, await source.context.storage_state(path=native_path, indexed_db=True))
    async with _browser() as (client, restored):
        assert restored.page_pool.pages_count == 0
        _status(await client.call_tool("browser_load_state", arguments), "State loaded.")
        assert restored.page_pool.pages_count == 0
        assert not (await client.call_tool("browser_fetch", fetch)).is_error
        page_info = restored.page_pool.pages[0]
        page = page_info.page
        assert await page.evaluate(READ_STATE) == SAVED_STATE
        assert await page.evaluate("sessionStorage.length") == 0
        await page.evaluate(WRITE_STATE, "changed")
        changed = await page.evaluate(READ_STATE)
        assert changed["indexedDB"]["value"] == "changed" and changed["databases"] == ["auth", "stale"]
        _status(await client.call_tool("browser_load_state", {**arguments, "path": str(native_path)}), "State loaded.")
        assert restored.page_pool.pages == [page_info] and page_info.state == "ready"
        assert page.url == URL and not page.is_closed()
        assert await page.evaluate("sessionStorage.getItem('temporary')") == "changed"
        assert not (await client.call_tool("browser_fetch", fetch)).is_error
        assert restored.page_pool.pages[0].page is page
        assert await page.evaluate(READ_STATE) == SAVED_STATE


@pytest.mark.browser
@pytest.mark.asyncio
async def test_browser_state_live_file_errors(tmp_path: Path) -> None:
    invalid = tmp_path / "invalid.json"
    invalid.write_text("{")
    cases = [
        ("load", tmp_path / "missing.json", strerror(ENOENT)),
        ("load", invalid, "Expecting property name enclosed in double quotes"),
        ("save", tmp_path / "missing" / "state.json", strerror(ENOENT)),
        ("save", tmp_path, strerror(EISDIR)),
    ]
    async with _browser() as (client, session):
        await session.context.add_cookies([{"name": "kept", "value": "private-token", "url": URL}])
        for operation, path, message in cases:
            result = await client.call_tool(f"browser_{operation}_state", {"session_id": "browser", "path": str(path)})
            assert result.is_error and result.structured_content is None
            assert len(result.content) == 1 and isinstance(result.content[0], TextContent)
            assert message in result.content[0].text and "private-token" not in result.content[0].text
        assert session.page_pool.pages_count == 0
        assert [(cookie["name"], cookie["value"]) for cookie in await session.context.cookies()] == [
            ("kept", "private-token")
        ]
