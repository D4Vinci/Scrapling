import asyncio
from contextlib import asynccontextmanager
from json import loads
from os import getenv
from re import search
from unittest.mock import AsyncMock, Mock, call

import pytest
from anyio import CancelScope
from mcp.client import Client
from mcp.types import TextContent
from patchright.async_api import TimeoutError as PatchrightTimeoutError
from playwright.async_api import TimeoutError as PlaywrightTimeoutError
from pydantic import ValidationError

from scrapling.core.ai import ScraplingMCPServer, SessionType, _SessionEntry
from scrapling.core._types import Any, AsyncGenerator
from scrapling.engines._browsers._base import AsyncSession


HTML = """<!DOCTYPE html><html><body>
<form><label>Name<input id="name" name="name" value="initial"></label><button>Save</button></form>
<textarea id="notes">initial notes</textarea><div id="editor" contenteditable="true">initial editor</div>
<output id="submitted" data-count="0"></output><textarea id="events" hidden>[]</textarea><script>
document.querySelector('form').addEventListener('submit', event => {
    event.preventDefault();
    const output = document.querySelector('#submitted');
    output.textContent = new FormData(event.target).get('name');
    output.dataset.count = Number(output.dataset.count) + 1;
});
for (const type of ['keydown', 'keyup', 'input']) {
    document.addEventListener(type, event => {
        const events = document.querySelector('#events');
        events.value = JSON.stringify([...JSON.parse(events.value),
            {type, key: event.key, trusted: event.isTrusted, target: event.target.id}]);
    });
}
</script></body></html>"""


def _server(session_type: SessionType = "dynamic") -> tuple[ScraplingMCPServer, AsyncSession, Mock]:
    server = ScraplingMCPServer()
    session = AsyncSession()
    session._is_alive = True
    page = Mock()
    page.is_closed.return_value = False
    for method in ("fill", "press_sequentially", "press"):
        setattr(page.locator.return_value, method, AsyncMock())
    session.page_pool.add_page(page).mark_ready()
    server._sessions["browser"] = _SessionEntry(session, session_type)
    return server, session, page


@pytest.mark.asyncio
async def test_browser_type_schema() -> None:
    async with Client(ScraplingMCPServer()._build_server("127.0.0.1", 8000)) as client:
        tool = next(tool for tool in (await client.list_tools()).tools if tool.name == "browser_type")
    assert set(tool.input_schema["properties"]) == {
        "session_id",
        "text",
        "selector",
        "ref",
        "slowly",
        "submit",
        "timeout",
    }
    assert tool.input_schema["required"] == ["session_id", "text"]
    props = tool.input_schema["properties"]
    assert props["text"]["type"] == "string"
    assert props["slowly"]["default"] is props["submit"]["default"] is False
    assert props["timeout"]["default"] == 30000
    assert props["timeout"]["minimum"] == 0


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "target, options, method, timeout",
    [
        ({"selector": "#name"}, {}, "fill", 30000),
        ({"ref": "e4"}, {"submit": True, "timeout": 0}, "fill", 0),
        ({"selector": "#name"}, {"slowly": True, "timeout": 400}, "press_sequentially", 400),
        ({"ref": "e4"}, {"slowly": True, "submit": True}, "press_sequentially", 30000),
    ],
)
async def test_browser_type_forwards_options_and_submits_after_typing(
    target: dict[str, Any], options: dict[str, Any], method: str, timeout: int
) -> None:
    server, session, page = _server()
    async with Client(server._build_server("127.0.0.1", 8000)) as client:
        result = await client.call_tool(
            "browser_type", {"session_id": "browser", "text": "private text", **target, **options}
        )
    assert not result.is_error
    assert result.structured_content is None
    assert result.content == [TextContent(type="text", text="Text entered.")]
    page.locator.assert_called_once_with("#name" if "selector" in target else "aria-ref=e4")
    expected = [getattr(call, method)("private text", timeout=timeout)]
    if options.get("submit"):
        expected.append(call.press("Enter", timeout=timeout))
    assert page.locator.return_value.mock_calls == expected
    assert session.page_pool.pages[0].state == "ready"
    page.goto.assert_not_called()
    page.aria_snapshot.assert_not_called()
    page.set_default_timeout.assert_not_called()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "values",
    [
        {"selector": None},
        {"selector": ""},
        {"selector": None, "ref": ""},
        {"ref": "e1"},
        {"text": None},
        {"text": ["invalid"]},
        {"slowly": "invalid"},
        {"submit": "invalid"},
        {"timeout": -1},
    ],
)
async def test_browser_type_invalid_input_does_not_reserve_page(values: dict[str, Any]) -> None:
    server, session, page = _server()
    async with Client(server._build_server("127.0.0.1", 8000)) as client:
        result = await client.call_tool(
            "browser_type", {"session_id": "browser", "text": "value", "selector": "#name", **values}
        )
    assert result.is_error
    page.is_closed.assert_not_called()
    page.locator.assert_not_called()
    assert session.page_pool.pages[0].state == "ready"


@pytest.mark.parametrize("timeout", [float("nan"), float("inf"), float("-inf")])
def test_browser_type_rejects_nonfinite_timeout(timeout: float) -> None:
    tool = ScraplingMCPServer()._build_server("127.0.0.1", 8000)._tool_manager.get_tool("browser_type")
    assert tool is not None
    with pytest.raises(ValidationError):
        tool.fn_metadata.arg_model.model_validate(
            {"session_id": "browser", "selector": "#name", "text": "value", "timeout": timeout}
        )


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "state, message",
    [
        ("missing", "not found"),
        ("dead", "no longer alive"),
        ("static", "'static'"),
        ("empty", "browser_fetch"),
        ("busy", "busy"),
        ("closed", "closed"),
    ],
)
async def test_browser_type_session_errors_reach_mcp(state: str, message: str) -> None:
    server, session, page = _server("static" if state == "static" else "dynamic")
    if state == "missing":
        server._sessions.clear()
    elif state == "dead":
        session._is_alive = False
    elif state == "empty":
        session.page_pool.clear()
    elif state == "busy":
        session.page_pool.pages[0].mark_busy()
    elif state == "closed":
        page.is_closed.return_value = True
    async with Client(server._build_server("127.0.0.1", 8000)) as client:
        result = await client.call_tool("browser_type", {"session_id": "browser", "selector": "#name", "text": "value"})
    assert result.is_error
    assert result.content and isinstance(result.content[0], TextContent)
    assert message in result.content[0].text
    page.locator.assert_not_called()
    if state == "closed":
        assert session.page_pool.pages_count == 0
    elif state == "busy":
        assert session.page_pool.pages[0].state == "busy"


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "session_type, error", [("dynamic", PlaywrightTimeoutError), ("stealthy", PatchrightTimeoutError)]
)
@pytest.mark.parametrize("method", ["fill", "press_sequentially", "press"])
async def test_browser_type_timeout_does_not_retry_or_submit_failed_input(
    session_type: SessionType, error: type[Exception], method: str
) -> None:
    server, session, page = _server(session_type)
    action = getattr(page.locator.return_value, method)
    action.side_effect = error("typing timed out")
    async with Client(server._build_server("127.0.0.1", 8000)) as client:
        result = await client.call_tool(
            "browser_type",
            {
                "session_id": "browser",
                "selector": "#name",
                "text": "value",
                "slowly": method == "press_sequentially",
                "submit": True,
            },
        )
    assert result.is_error
    assert result.content and isinstance(result.content[0], TextContent)
    assert "typing timed out" in result.content[0].text
    action.assert_awaited_once()
    if method != "press":
        page.locator.return_value.press.assert_not_awaited()
    else:
        page.locator.return_value.fill.assert_awaited_once()
    assert session.page_pool.pages[0].state == "ready"
    action.side_effect = None
    assert await server.browser_type("browser", "next", selector="#name") == "Text entered."


@pytest.mark.asyncio
@pytest.mark.parametrize("method", ["fill", "press_sequentially", "press"])
@pytest.mark.parametrize("cancel_mode", ["task", "scope"])
async def test_browser_type_reserves_page_until_cancelled(method: str, cancel_mode: str) -> None:
    server, session, page = _server()
    entered = asyncio.Event()
    scope = CancelScope()

    async def pending(*args: Any, **kwargs: Any) -> None:
        entered.set()
        await asyncio.Event().wait()

    async def type_text() -> None:
        with scope:
            await server.browser_type(
                "browser", "value", selector="#name", slowly=method == "press_sequentially", submit=True
            )

    getattr(page.locator.return_value, method).side_effect = pending
    task = asyncio.create_task(type_text())
    try:
        await asyncio.wait_for(entered.wait(), 5)
        assert session.page_pool.pages[0].state == "busy"
        with pytest.raises(RuntimeError, match="busy"):
            await server.browser_type("browser", "other", selector="#name")
    finally:
        scope.cancel() if cancel_mode == "scope" else task.cancel()
        if cancel_mode == "scope":
            await asyncio.wait_for(task, 5)
            assert scope.cancelled_caught
        else:
            with pytest.raises(asyncio.CancelledError):
                await task
    assert session.page_pool.pages[0].state == "ready"
    if method != "press":
        page.locator.return_value.press.assert_not_awaited()


@asynccontextmanager
async def _browser(session_type: SessionType) -> AsyncGenerator[tuple[ScraplingMCPServer, Client, Any, Any], None]:
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
                "browser_fetch", {"session_id": "browser", "url": "https://type.test/", "google_search": False}
            )
            assert not fetched.is_error
            yield server, client, session, session.page_pool.pages[0].page
        finally:
            closed = await client.call_tool("close_session", {"session_id": "browser"})
            assert not closed.is_error


@pytest.mark.asyncio
@pytest.mark.parametrize("session_type", ["dynamic", "stealthy"])
async def test_browser_type_live_fill_selectors_refs_and_editable_fields(session_type: SessionType) -> None:
    async with _browser(session_type) as browser:
        server, client, session, page = browser
        snapshot = await server.browser_snapshot("browser")
        match = search(r'textbox "Name".*?\[ref=([^\]]+)\]', snapshot)
        assert match is not None
        for target, text, element in (
            ({"selector": "#name"}, "new α value", "#name"),
            ({"ref": match[1]}, "", "#name"),
            ({"selector": 'xpath=//textarea[@id="notes"]'}, "line one\nline two", "#notes"),
            ({"selector": "#editor"}, "edited content", "#editor"),
        ):
            result = await client.call_tool("browser_type", {"session_id": "browser", "text": text, **target})
            assert not result.is_error
            value = (
                await page.locator(element).inner_text()
                if element == "#editor"
                else await page.locator(element).input_value()
            )
            assert value == text
            assert session.page_pool.pages[0].state == "ready"
        events = loads(await page.locator("#events").input_value())
        assert {event["target"] for event in events if event["type"] == "input"} == {"name", "notes", "editor"}
        assert all(event["trusted"] for event in events)
        assert await page.locator("#submitted").get_attribute("data-count") == "0"


@pytest.mark.asyncio
@pytest.mark.parametrize("session_type", ["dynamic", "stealthy"])
async def test_browser_type_live_sequential_keys_and_submit(session_type: SessionType) -> None:
    async with _browser(session_type) as browser:
        _, client, session, page = browser
        for text, slowly, expected, count in (("prefix", False, "prefix", 1), ("abc", True, "prefixabc", 2)):
            await page.locator("#events").evaluate("element => element.value = '[]'")
            result = await client.call_tool(
                "browser_type",
                {"session_id": "browser", "selector": "#name", "text": text, "slowly": slowly, "submit": True},
            )
            assert not result.is_error
            assert await page.locator("#name").input_value() == expected
            assert await page.locator("#submitted").inner_text() == expected
            assert await page.locator("#submitted").get_attribute("data-count") == str(count)
            events = loads(await page.locator("#events").input_value())
            assert all(event["trusted"] and event["target"] == "name" for event in events)
            assert [event["key"] for event in events if event["type"] == "keydown"] == (
                ["a", "b", "c", "Enter"] if slowly else ["Enter"]
            )
            assert [event["key"] for event in events if event["type"] == "keyup"] == (
                ["a", "b", "c", "Enter"] if slowly else ["Enter"]
            )
            assert next(index for index, event in enumerate(events) if event.get("key") == "Enter") > max(
                index for index, event in enumerate(events) if event["type"] == "input"
            )
            assert session.page_pool.pages[0].state == "ready"


@pytest.mark.asyncio
@pytest.mark.parametrize("session_type", ["dynamic", "stealthy"])
async def test_browser_type_live_bad_targets_do_not_submit(session_type: SessionType) -> None:
    async with _browser(session_type) as browser:
        server, client, session, page = browser
        match = search(r'textbox "Name".*?\[ref=([^\]]+)\]', await server.browser_snapshot("browser"))
        assert match is not None
        await page.locator("#name").evaluate("element => element.remove()")
        for target in ({"selector": "textarea"}, {"selector": "#missing"}, {"ref": match[1]}):
            result = await client.call_tool(
                "browser_type", {"session_id": "browser", "text": "value", "submit": True, "timeout": 100, **target}
            )
            assert result.is_error
            assert result.content and isinstance(result.content[0], TextContent)
            assert ("strict mode violation" if target.get("selector") == "textarea" else "Timeout") in result.content[
                0
            ].text
            assert loads(await page.locator("#events").input_value()) == []
            assert await page.locator("#submitted").get_attribute("data-count") == "0"
            assert session.page_pool.pages[0].state == "ready"
