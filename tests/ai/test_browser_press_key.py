import asyncio
from contextlib import asynccontextmanager
from json import loads
from os import getenv
from unittest.mock import AsyncMock, Mock, call

import pytest
from anyio import CancelScope
from mcp.client import Client
from mcp.types import TextContent

from scrapling.core.ai import ScraplingMCPServer, SessionType, _SessionEntry
from scrapling.core._types import Any, AsyncGenerator
from scrapling.engines._browsers._base import AsyncSession


HTML = """<!DOCTYPE html><html><body><form>
<label>First<input id="first" name="value"></label><label>Second<input id="second"></label>
<button>Save</button></form><output id="submitted" data-count="0"></output><output id="escaped"></output>
<textarea id="events" hidden>[]</textarea><script>
document.querySelector('form').addEventListener('submit', event => {
    event.preventDefault();
    const output = document.querySelector('#submitted');
    output.textContent = new FormData(event.target).get('value');
    output.dataset.count = Number(output.dataset.count) + 1;
});
for (const type of ['keydown', 'keyup']) {
    document.addEventListener(type, event => {
        const events = document.querySelector('#events');
        events.value = JSON.stringify([...JSON.parse(events.value), {type, key: event.key, trusted: event.isTrusted,
            target: event.target.id, ctrl: event.ctrlKey, meta: event.metaKey, shift: event.shiftKey, alt: event.altKey}]);
        if (type === 'keydown' && event.key === 'Escape') document.querySelector('#escaped').textContent = 'closed';
    });
}
</script></body></html>"""


def _server(session_type: SessionType = "dynamic") -> tuple[ScraplingMCPServer, AsyncSession, Mock]:
    server = ScraplingMCPServer()
    session = AsyncSession()
    session._is_alive = True
    page = Mock()
    page.is_closed.return_value = False
    page.keyboard.press = AsyncMock()
    session.page_pool.add_page(page).mark_ready()
    server._sessions["browser"] = _SessionEntry(session, session_type)
    return server, session, page


@pytest.mark.asyncio
async def test_browser_press_key_schema() -> None:
    async with Client(ScraplingMCPServer()._build_server("127.0.0.1", 8000)) as client:
        tool = next(tool for tool in (await client.list_tools()).tools if tool.name == "browser_press_key")
    assert tool.title == "Press keys"
    assert set(tool.input_schema["properties"]) == {"session_id", "keys"}
    assert tool.input_schema["required"] == ["session_id", "keys"]
    keys = tool.input_schema["properties"]["keys"]
    assert keys["type"] == "array" and keys["minItems"] == 1
    assert keys["items"]["type"] == "string" and keys["items"]["minLength"] == 1


@pytest.mark.asyncio
@pytest.mark.parametrize("keys", [["Enter"], ["Escape", "Shift+Tab", "ControlOrMeta+A", "+", " ", "Enter", "Enter"]])
async def test_browser_press_key_forwards_native_keys_in_order(keys: list[str]) -> None:
    server, session, page = _server()
    async with Client(server._build_server("127.0.0.1", 8000)) as client:
        result = await client.call_tool("browser_press_key", {"session_id": "browser", "keys": keys})
    assert not result.is_error
    assert result.structured_content is None
    assert result.content == [TextContent(type="text", text="Keys pressed.")]
    assert page.keyboard.press.await_args_list == [call(key) for key in keys]
    page.locator.assert_not_called()
    page.aria_snapshot.assert_not_called()
    page.screenshot.assert_not_called()
    assert session.page_pool.pages[0].state == "ready"


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "values",
    [
        {},
        {"key": "Enter"},
        {"keys": []},
        {"keys": "Enter"},
        {"keys": None},
        {"keys": ["Enter", ""]},
        {"keys": ["Enter", None]},
        {"keys": ["Enter", 42]},
        {"keys": ["Enter", ["Escape"]]},
    ],
)
async def test_browser_press_key_invalid_input_does_not_reserve_page(values: dict[str, Any]) -> None:
    server, session, page = _server()
    async with Client(server._build_server("127.0.0.1", 8000)) as client:
        result = await client.call_tool("browser_press_key", {"session_id": "browser", **values})
    assert result.is_error
    page.is_closed.assert_not_called()
    page.keyboard.press.assert_not_awaited()
    assert session.page_pool.pages[0].state == "ready"


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "state, message", [("missing", "not found"), ("static", "'static'"), ("empty", "browser_fetch")]
)
async def test_browser_press_key_session_errors_reach_mcp(state: str, message: str) -> None:
    server, session, page = _server("static" if state == "static" else "dynamic")
    if state == "missing":
        server._sessions.clear()
    elif state == "empty":
        session.page_pool.clear()
    async with Client(server._build_server("127.0.0.1", 8000)) as client:
        result = await client.call_tool("browser_press_key", {"session_id": "browser", "keys": ["Enter"]})
    assert result.is_error
    assert result.content and isinstance(result.content[0], TextContent)
    assert message in result.content[0].text
    page.keyboard.press.assert_not_awaited()


@pytest.mark.asyncio
async def test_browser_press_key_error_stops_remaining_keys_and_releases_page() -> None:
    server, session, page = _server()
    page.keyboard.press.side_effect = [None, RuntimeError("key failed")]
    async with Client(server._build_server("127.0.0.1", 8000)) as client:
        result = await client.call_tool("browser_press_key", {"session_id": "browser", "keys": ["a", "Bad", "Enter"]})
    assert result.is_error
    assert result.content and isinstance(result.content[0], TextContent)
    assert "key failed" in result.content[0].text
    assert page.keyboard.press.await_args_list == [call("a"), call("Bad")]
    assert session.page_pool.pages[0].state == "ready"
    page.keyboard.press.side_effect = None
    assert await server.browser_press_key("browser", ["Escape"]) == "Keys pressed."


@pytest.mark.asyncio
@pytest.mark.parametrize("cancel_mode", ["task", "scope"])
async def test_browser_press_key_reserves_page_until_cancelled(cancel_mode: str) -> None:
    server, session, page = _server()
    entered = asyncio.Event()
    scope = CancelScope()

    async def pending(key: str) -> None:
        if key == "Enter":
            entered.set()
            await asyncio.Event().wait()

    async def press() -> None:
        with scope:
            await server.browser_press_key("browser", ["a", "Enter", "Escape"])

    page.keyboard.press.side_effect = pending
    task = asyncio.create_task(press())
    try:
        await asyncio.wait_for(entered.wait(), 5)
        assert session.page_pool.pages[0].state == "busy"
        with pytest.raises(RuntimeError, match="busy"):
            await server.browser_press_key("browser", ["Enter"])
    finally:
        scope.cancel() if cancel_mode == "scope" else task.cancel()
        if cancel_mode == "scope":
            await asyncio.wait_for(task, 5)
            assert scope.cancelled_caught
        else:
            with pytest.raises(asyncio.CancelledError):
                await task
    assert page.keyboard.press.await_args_list == [call("a"), call("Enter")]
    assert session.page_pool.pages[0].state == "ready"


@asynccontextmanager
async def _browser(session_type: SessionType) -> AsyncGenerator[tuple[Client, Any, Any], None]:
    server = ScraplingMCPServer(executable_path=getenv("SCRAPLING_EXECUTABLE_PATH"))

    async def serve(route: Any) -> None:
        await route.fulfill(status=200, content_type="text/html", body=HTML)

    async with Client(server._build_server("127.0.0.1", 8000)) as client:
        opened = await client.call_tool("browser_open", {"session_type": session_type, "session_id": "browser"})
        assert not opened.is_error
        try:
            session = server._sessions["browser"].session
            await session.context.route("**/*", serve)
            fetched = await client.call_tool(
                "browser_fetch", {"session_id": "browser", "url": "https://keys.test/", "google_search": False}
            )
            assert not fetched.is_error
            yield client, session, session.page_pool.pages[0].page
        finally:
            closed = await client.call_tool("close_session", {"session_id": "browser"})
            assert not closed.is_error


@pytest.mark.asyncio
@pytest.mark.parametrize("session_type", ["dynamic", "stealthy"])
async def test_browser_press_key_live_focus_editing_and_shortcuts(session_type: SessionType) -> None:
    async with _browser(session_type) as (client, session, page):

        async def press(keys: list[str]) -> None:
            result = await client.call_tool("browser_press_key", {"session_id": "browser", "keys": keys})
            assert not result.is_error
            assert session.page_pool.pages[0].state == "ready"

        typed = await client.call_tool(
            "browser_type", {"session_id": "browser", "selector": "#first", "text": "initial"}
        )
        assert not typed.is_error
        await page.locator("#events").evaluate("element => element.value = '[]'")
        await press(["Tab", "z", "Shift+Tab"])
        await page.wait_for_function("document.activeElement.id === 'first'", timeout=5000)
        assert await page.locator("#second").input_value() == "z"
        assert await page.locator("#first").input_value() == "initial"
        await press(["ControlOrMeta+A", "Backspace"])
        assert await page.locator("#first").input_value() == ""
        await press(["a", " ", "+", "ArrowLeft", "b"])
        assert await page.locator("#first").input_value() == "a b+"
        await press(["Escape", "Enter"])
        await page.wait_for_function("document.querySelector('#escaped').textContent === 'closed'", timeout=5000)
        await page.wait_for_function("document.querySelector('#submitted').dataset.count === '1'", timeout=5000)
        assert await page.locator("#submitted").inner_text() == "a b+"
        invalid = await client.call_tool(
            "browser_press_key", {"session_id": "browser", "keys": ["c", "ScraplingInvalidKey", "x"]}
        )
        assert invalid.is_error
        assert invalid.content and isinstance(invalid.content[0], TextContent)
        assert "Unknown key" in invalid.content[0].text
        assert session.page_pool.pages[0].state == "ready"
        assert await page.locator("#first").input_value() == "a bc+"
        await press(["d"])
        assert await page.locator("#first").input_value() == "a bcd+"
        events = loads(await page.locator("#events").input_value())
        assert events and all(event["trusted"] for event in events)
        assert [event["shift"] for event in events if event["type"] == "keydown" and event["key"] == "Tab"] == [
            False,
            True,
        ]
        assert any(event["type"] == "keydown" and (event["ctrl"] or event["meta"]) for event in events)
        assert not any(event["key"] in ("ScraplingInvalidKey", "x") for event in events)
        for key in ("Backspace", "b", "c", "d", "Escape", "Enter"):
            keyed = [event for event in events if event["key"] == key]
            assert [event["type"] for event in keyed] == ["keydown", "keyup"]
            assert all(not any(event[modifier] for modifier in ("ctrl", "meta", "shift", "alt")) for event in keyed)
