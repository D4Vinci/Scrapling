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


TEXT_FIELD = {"type": "textbox", "selector": "#name", "value": "private value"}
HTML = """<!DOCTYPE html><html><body><form>
<label>Name<input id="name" value="initial"></label><label>Notes<textarea id="notes">initial notes</textarea></label>
<div id="editor" contenteditable="true">initial editor</div>
<label>Agree<input id="agree" type="checkbox"></label><label>Updates<input id="updates" type="checkbox" checked></label>
<label>Basic<input id="basic" type="radio" name="plan" checked></label><label>Pro<input id="pro" type="radio" name="plan"></label>
<button>Submit</button></form>
<label>Country<select id="country"><option value="us">United States</option><option value="gb">United Kingdom</option></select></label>
<label>Colors<select id="colors" multiple><option value="r">Red</option><option value="g">Green</option><option value="b">Blue</option></select></label>
<output id="submitted">0</output><textarea id="events" hidden>[]</textarea><script>
document.querySelector('form').addEventListener('submit', event => {
    event.preventDefault();
    const output = document.querySelector('#submitted');
    output.textContent = Number(output.textContent) + 1;
});
for (const type of ['input', 'change', 'keydown', 'keyup']) {
    document.addEventListener(type, event => {
        const events = document.querySelector('#events');
        events.value = JSON.stringify([...JSON.parse(events.value), {type, target: event.target.id, key: event.key, time: performance.now()}]);
    });
}
</script></body></html>"""


def _server(session_type: SessionType = "dynamic") -> tuple[ScraplingMCPServer, AsyncSession, Mock]:
    server = ScraplingMCPServer()
    session = AsyncSession()
    session._is_alive = True
    page = Mock()
    page.is_closed.return_value = False
    for method in ("fill", "press_sequentially", "set_checked", "select_option"):
        setattr(page.locator.return_value, method, AsyncMock())
    session.page_pool.add_page(page).mark_ready()
    server._sessions["browser"] = _SessionEntry(session, session_type)
    return server, session, page


@pytest.mark.asyncio
async def test_browser_fill_fields_schema() -> None:
    async with Client(ScraplingMCPServer()._build_server("127.0.0.1", 8000)) as client:
        tool = next(tool for tool in (await client.list_tools()).tools if tool.name == "browser_fill_fields")
    assert tool.title == "Fill fields"
    schema = tool.input_schema
    assert set(schema["properties"]) == {"session_id", "fields", "timeout", "slowly"}
    assert schema["required"] == ["session_id", "fields"]
    assert schema["properties"]["slowly"]["type"] == "boolean"
    assert schema["properties"]["slowly"]["default"] is False
    assert schema["properties"]["timeout"]["default"] == 30000
    assert schema["properties"]["timeout"]["minimum"] == 0
    fields = schema["properties"]["fields"]
    assert fields["type"] == "array" and fields["minItems"] == 1
    items = fields["items"]
    assert items["discriminator"]["propertyName"] == "type"
    variants = {kind: schema["$defs"][ref.rsplit("/", 1)[1]] for kind, ref in items["discriminator"]["mapping"].items()}
    assert set(variants) == {"textbox", "checkbox", "radio", "combobox"}
    assert len(items["oneOf"]) == 4
    for kind, variant in variants.items():
        assert set(variant["required"]) == {"type", "value"}
        assert set(variant["properties"]) == {"type", "value", "selector", "ref"} | (
            {"clear"} if kind == "textbox" else set()
        )
        assert variant["properties"]["type"]["const"] == kind
        for target in ("selector", "ref"):
            assert {"type": "null"} in variant["properties"][target]["anyOf"]
            assert any(option.get("minLength") == 1 for option in variant["properties"][target]["anyOf"])
    assert variants["textbox"]["properties"]["value"]["type"] == "string"
    assert variants["textbox"]["properties"]["clear"]["type"] == "boolean"
    assert variants["textbox"]["properties"]["clear"]["default"] is True
    assert variants["checkbox"]["properties"]["value"]["type"] == "boolean"
    assert variants["radio"]["properties"]["value"]["const"] is True
    assert {option["type"] for option in variants["combobox"]["properties"]["value"]["anyOf"]} == {"string", "array"}


@pytest.mark.asyncio
@pytest.mark.parametrize("options, timeout", [({}, 30000), ({"timeout": 0}, 0), ({"timeout": 123.5}, 123.5)])
async def test_browser_fill_fields_forwards_native_actions_in_order(
    options: dict[str, Any], timeout: float, monkeypatch: pytest.MonkeyPatch
) -> None:
    server, session, page = _server()
    pause = AsyncMock()
    monkeypatch.setattr("scrapling.core.ai.sleep", pause)
    fields = [
        {**TEXT_FIELD, "ref": None},
        {"type": "textbox", "selector": None, "ref": "e2", "value": "", "clear": True},
        {"type": "checkbox", "selector": "#agree", "value": True},
        {"type": "checkbox", "selector": "#agree", "value": False},
        {"type": "checkbox", "selector": "#agree", "value": "false"},
        {"type": "radio", "selector": "#pro", "value": True},
        {"type": "combobox", "selector": "#country", "value": "United Kingdom"},
        {"type": "combobox", "selector": "#colors", "value": ["Red", "Blue"]},
        {"type": "combobox", "selector": "#colors", "value": []},
    ]
    async with Client(server._build_server("127.0.0.1", 8000)) as client:
        result = await client.call_tool("browser_fill_fields", {"session_id": "browser", "fields": fields, **options})
    assert not result.is_error
    assert result.structured_content is None
    assert result.content == [TextContent(type="text", text="Fields filled.")]
    assert page.locator.mock_calls == [
        call("#name"),
        call().fill("private value", timeout=timeout),
        call("aria-ref=e2"),
        call().fill("", timeout=timeout),
        call("#agree"),
        call().set_checked(True, timeout=timeout),
        call("#agree"),
        call().set_checked(False, timeout=timeout),
        call("#agree"),
        call().set_checked(False, timeout=timeout),
        call("#pro"),
        call().set_checked(True, timeout=timeout),
        call("#country"),
        call().select_option(label="United Kingdom", timeout=timeout),
        call("#colors"),
        call().select_option(label=["Red", "Blue"], timeout=timeout),
        call("#colors"),
        call().select_option(label=[], timeout=timeout),
    ]
    page.keyboard.press.assert_not_called()
    page.locator.return_value.press.assert_not_called()
    page.aria_snapshot.assert_not_called()
    page.screenshot.assert_not_called()
    pause.assert_not_awaited()
    assert session.page_pool.pages[0].state == "ready"


@pytest.mark.asyncio
@pytest.mark.parametrize("slowly", [False, True])
@pytest.mark.parametrize("value", ["xy", ""])
async def test_browser_fill_fields_types_without_clearing(
    slowly: bool, value: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    server, session, page = _server()
    monkeypatch.setattr("scrapling.core.ai.uniform", Mock(side_effect=[60, 140]))
    async with Client(server._build_server("127.0.0.1", 8000)) as client:
        result = await client.call_tool(
            "browser_fill_fields",
            {"session_id": "browser", "fields": [{**TEXT_FIELD, "value": value, "clear": False}], "slowly": slowly},
        )
    assert not result.is_error
    assert result.content == [TextContent(type="text", text="Fields filled.")]
    page.locator.return_value.fill.assert_not_awaited()
    assert page.locator.return_value.press_sequentially.await_args_list == (
        [call("x", delay=60, timeout=30000), call("y", delay=140, timeout=30000)]
        if slowly and value
        else [call(value, timeout=30000)]
    )
    assert session.page_pool.pages[0].state == "ready"


@pytest.mark.asyncio
async def test_browser_fill_fields_slow_pacing_and_empty_text(monkeypatch: pytest.MonkeyPatch) -> None:
    server, session, page = _server()
    actions = Mock()
    actions.attach_mock(page.locator, "locator")
    actions.pause = AsyncMock()
    monkeypatch.setattr("scrapling.core.ai.sleep", actions.pause)
    intervals = Mock(side_effect=[60, 140, 0.12, 0.27, 0.18, 0.22])
    monkeypatch.setattr("scrapling.core.ai.uniform", intervals)
    fields = [
        {**TEXT_FIELD, "value": "ab"},
        {"type": "textbox", "ref": "e2", "value": ""},
        {"type": "checkbox", "selector": "#agree", "value": True},
        {"type": "radio", "selector": "#pro", "value": True},
        {"type": "combobox", "selector": "#country", "value": "United Kingdom"},
    ]
    async with Client(server._build_server("127.0.0.1", 8000)) as client:
        result = await client.call_tool(
            "browser_fill_fields", {"session_id": "browser", "fields": fields, "slowly": True, "timeout": 0}
        )
    assert not result.is_error
    assert result.content == [TextContent(type="text", text="Fields filled.")]
    assert actions.mock_calls == [
        call.locator("#name"),
        call.locator().fill("", timeout=0),
        call.locator().press_sequentially("a", delay=60, timeout=0),
        call.locator().press_sequentially("b", delay=140, timeout=0),
        call.pause(0.12),
        call.locator("aria-ref=e2"),
        call.locator().fill("", timeout=0),
        call.pause(0.27),
        call.locator("#agree"),
        call.locator().set_checked(True, timeout=0),
        call.pause(0.18),
        call.locator("#pro"),
        call.locator().set_checked(True, timeout=0),
        call.pause(0.22),
        call.locator("#country"),
        call.locator().select_option(label="United Kingdom", timeout=0),
    ]
    assert intervals.call_args_list == [call(50, 150), call(50, 150), *[call(0.1, 0.3)] * 4]
    assert session.page_pool.pages[0].state == "ready"


@pytest.mark.asyncio
@pytest.mark.parametrize("method", ["fill", "press_sequentially"])
async def test_browser_fill_fields_slow_failure_stops_before_next_pause(
    method: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    server, session, page = _server()
    getattr(page.locator.return_value, method).side_effect = (
        [None, RuntimeError("text failed")] if method == "press_sequentially" else RuntimeError("text failed")
    )
    pause = AsyncMock()
    monkeypatch.setattr("scrapling.core.ai.sleep", pause)
    async with Client(server._build_server("127.0.0.1", 8000)) as client:
        result = await client.call_tool(
            "browser_fill_fields", {"session_id": "browser", "fields": [TEXT_FIELD, TEXT_FIELD], "slowly": True}
        )
    assert result.is_error
    page.locator.assert_called_once_with("#name")
    pause.assert_not_awaited()
    if method == "fill":
        page.locator.return_value.press_sequentially.assert_not_awaited()
    else:
        assert [args.args[0] for args in page.locator.return_value.press_sequentially.await_args_list] == ["p", "r"]
    assert session.page_pool.pages[0].state == "ready"


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "invalid",
    [
        {"selector": None},
        {"ref": "e1"},
        {"selector": ""},
        {"selector": None, "ref": ""},
        {"type": "unknown"},
        {"type": None},
        {"value": None},
        {"value": False},
        {"clear": None},
        {"clear": "invalid"},
        {"type": "checkbox", "value": "invalid"},
        {"type": "radio", "value": False},
        {"type": "combobox", "value": True},
        {"type": "combobox", "value": ["Red", None]},
    ],
)
async def test_browser_fill_fields_invalid_later_field_prevents_all_actions(invalid: dict[str, Any]) -> None:
    server, session, page = _server()
    async with Client(server._build_server("127.0.0.1", 8000)) as client:
        result = await client.call_tool(
            "browser_fill_fields", {"session_id": "browser", "fields": [TEXT_FIELD, {**TEXT_FIELD, **invalid}]}
        )
    assert result.is_error
    page.is_closed.assert_not_called()
    page.locator.assert_not_called()
    assert session.page_pool.pages[0].state == "ready"


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "values",
    [
        {},
        {"fields": []},
        {"fields": None},
        {"fields": TEXT_FIELD},
        {"fields": [{"type": "textbox", "selector": "#name"}]},
        {"fields": [{"selector": "#name", "value": "value"}]},
        {"fields": [TEXT_FIELD], "timeout": -1},
        {"fields": [TEXT_FIELD], "slowly": "invalid"},
    ],
)
async def test_browser_fill_fields_invalid_arguments_do_not_reserve_page(values: dict[str, Any]) -> None:
    server, _, page = _server()
    async with Client(server._build_server("127.0.0.1", 8000)) as client:
        result = await client.call_tool("browser_fill_fields", {"session_id": "browser", **values})
    assert result.is_error
    page.is_closed.assert_not_called()
    page.locator.assert_not_called()


@pytest.mark.parametrize("timeout", [float("nan"), float("inf"), float("-inf")])
def test_browser_fill_fields_rejects_nonfinite_timeout(timeout: float) -> None:
    tool = ScraplingMCPServer()._build_server("127.0.0.1", 8000)._tool_manager.get_tool("browser_fill_fields")
    assert tool is not None
    with pytest.raises(ValidationError):
        tool.fn_metadata.arg_model.model_validate({"session_id": "browser", "fields": [TEXT_FIELD], "timeout": timeout})


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
async def test_browser_fill_fields_session_errors_reach_mcp(state: str, message: str) -> None:
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
        result = await client.call_tool("browser_fill_fields", {"session_id": "browser", "fields": [TEXT_FIELD]})
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
@pytest.mark.parametrize("clear, slowly", [(True, False), (False, False), (False, True)])
async def test_browser_fill_fields_timeout_stops_and_releases_page(
    session_type: SessionType, error: type[Exception], clear: bool, slowly: bool
) -> None:
    server, session, page = _server(session_type)
    action = page.locator.return_value.fill if clear else page.locator.return_value.press_sequentially
    action.side_effect = error("typing timed out")
    async with Client(server._build_server("127.0.0.1", 8000)) as client:
        result = await client.call_tool(
            "browser_fill_fields",
            {"session_id": "browser", "fields": [{**TEXT_FIELD, "clear": clear}, TEXT_FIELD], "slowly": slowly},
        )
    assert result.is_error
    assert result.content and isinstance(result.content[0], TextContent)
    assert "typing timed out" in result.content[0].text
    action.assert_awaited_once()
    page.locator.assert_called_once_with("#name")
    page.locator.return_value.press.assert_not_called()
    assert session.page_pool.pages[0].state == "ready"
    action.side_effect = None
    assert await server.browser_fill_fields("browser", [TEXT_FIELD]) == "Fields filled."


@pytest.mark.asyncio
async def test_browser_fill_fields_error_stops_remaining_fields_and_releases_page() -> None:
    server, session, page = _server()
    page.locator.return_value.fill.side_effect = [None, RuntimeError("field failed")]
    fields = [{**TEXT_FIELD, "value": value} for value in ("first", "second", "third")]
    async with Client(server._build_server("127.0.0.1", 8000)) as client:
        result = await client.call_tool("browser_fill_fields", {"session_id": "browser", "fields": fields})
    assert result.is_error
    assert result.content and isinstance(result.content[0], TextContent)
    assert "field failed" in result.content[0].text
    assert page.locator.return_value.fill.await_args_list == [
        call("first", timeout=30000),
        call("second", timeout=30000),
    ]
    assert session.page_pool.pages[0].state == "ready"


@pytest.mark.asyncio
@pytest.mark.parametrize("cancel_mode", ["task", "scope"])
@pytest.mark.parametrize("clear", [False, True])
async def test_browser_fill_fields_cancellation_stops_remaining_fields(cancel_mode: str, clear: bool) -> None:
    server, session, page = _server()
    entered = asyncio.Event()
    scope = CancelScope()
    fields = [{**TEXT_FIELD, "value": value, "clear": clear} for value in ("first", "second", "third")]

    async def pending(value: str, **kwargs: Any) -> None:
        if value == "second":
            entered.set()
            await asyncio.Event().wait()

    async def fill() -> None:
        with scope:
            await server.browser_fill_fields("browser", fields)

    action = page.locator.return_value.fill if clear else page.locator.return_value.press_sequentially
    action.side_effect = pending
    task = asyncio.create_task(fill())
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
    assert action.await_args_list == [
        call("first", timeout=30000),
        call("second", timeout=30000),
    ]
    assert session.page_pool.pages[0].state == "ready"


@pytest.mark.asyncio
@pytest.mark.parametrize("stage", ["typing", "pause"])
@pytest.mark.parametrize("cancel_mode", ["task", "scope"])
async def test_browser_fill_fields_slow_cancellation_releases_page(
    stage: str, cancel_mode: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    server, session, page = _server()
    entered = asyncio.Event()
    scope = CancelScope()

    async def pending(*args: Any, **kwargs: Any) -> None:
        entered.set()
        await asyncio.Event().wait()

    async def fill() -> None:
        with scope:
            await server.browser_fill_fields("browser", [TEXT_FIELD, TEXT_FIELD], slowly=True)

    if stage == "typing":
        page.locator.return_value.press_sequentially.side_effect = pending
    else:
        monkeypatch.setattr("scrapling.core.ai.sleep", pending)
    task = asyncio.create_task(fill())
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
    page.locator.assert_called_once_with("#name")
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
                "browser_fetch", {"session_id": "browser", "url": "https://form.test/", "google_search": False}
            )
            assert not fetched.is_error
            yield client, session, session.page_pool.pages[0].page
        finally:
            closed = await client.call_tool("close_session", {"session_id": "browser"})
            assert not closed.is_error


@pytest.mark.asyncio
@pytest.mark.parametrize("session_type", ["dynamic", "stealthy"])
async def test_browser_fill_fields_live_mixed_fields_and_clearing(session_type: SessionType) -> None:
    async with _browser(session_type) as (client, session, page):
        snapshot = await client.call_tool("browser_snapshot", {"session_id": "browser"})
        assert not snapshot.is_error
        assert snapshot.content and isinstance(snapshot.content[0], TextContent)
        name = search(r'textbox "Name".*?\[ref=([^\]]+)\]', snapshot.content[0].text)
        agree = search(r'checkbox "Agree".*?\[ref=([^\]]+)\]', snapshot.content[0].text)
        assert name is not None and agree is not None
        fields = [
            {"type": "textbox", "ref": name[1], "value": "new α name"},
            {"type": "textbox", "selector": 'xpath=//textarea[@id="notes"]', "value": "line one\nline two"},
            {"type": "textbox", "selector": "#editor", "value": "edited content"},
            {"type": "checkbox", "ref": agree[1], "value": True},
            {"type": "checkbox", "selector": "#updates", "value": False},
            {"type": "radio", "selector": "#pro", "value": True},
            {"type": "combobox", "selector": "#country", "value": "United Kingdom"},
            {"type": "combobox", "selector": "#colors", "value": ["Red", "Blue"]},
        ]
        filled = await client.call_tool("browser_fill_fields", {"session_id": "browser", "fields": fields})
        assert not filled.is_error
        assert await page.locator("#name").input_value() == "new α name"
        assert await page.locator("#notes").input_value() == "line one\nline two"
        assert await page.locator("#editor").inner_text() == "edited content"
        for selector, expected in (("#agree", True), ("#updates", False), ("#pro", True), ("#basic", False)):
            assert await page.locator(selector).is_checked() is expected
        assert await page.locator("#country").input_value() == "gb"
        assert await page.locator("#colors").evaluate(
            "element => [...element.selectedOptions].map(option => option.value)"
        ) == ["r", "b"]
        events = loads(await page.locator("#events").input_value())
        assert list(dict.fromkeys(event["target"] for event in events)) == [
            "name",
            "notes",
            "editor",
            "agree",
            "updates",
            "pro",
            "country",
            "colors",
        ]
        assert {event["target"] for event in events if event["type"] == "change"} >= {
            "agree",
            "updates",
            "pro",
            "country",
            "colors",
        }
        cleared = await client.call_tool(
            "browser_fill_fields",
            {
                "session_id": "browser",
                "fields": [
                    {"type": "textbox", "selector": "#name", "value": ""},
                    {"type": "checkbox", "selector": "#agree", "value": False},
                    {"type": "checkbox", "selector": "#updates", "value": True},
                    {"type": "radio", "selector": "#basic", "value": True},
                    {"type": "combobox", "selector": "#colors", "value": []},
                ],
            },
        )
        assert not cleared.is_error
        assert await page.locator("#name").input_value() == ""
        for selector, expected in (("#agree", False), ("#updates", True), ("#basic", True), ("#pro", False)):
            assert await page.locator(selector).is_checked() is expected
        assert await page.locator("#colors").evaluate("element => element.selectedOptions.length") == 0
        assert await page.locator("#submitted").inner_text() == "0"
        assert session.page_pool.pages[0].state == "ready"


@pytest.mark.asyncio
@pytest.mark.parametrize("session_type", ["dynamic", "stealthy"])
async def test_browser_fill_fields_live_slow_typing_and_field_delays(session_type: SessionType) -> None:
    async with _browser(session_type) as (client, session, page):
        snapshot = await client.call_tool("browser_snapshot", {"session_id": "browser"})
        assert not snapshot.is_error
        assert snapshot.content and isinstance(snapshot.content[0], TextContent)
        name = search(r'textbox "Name".*?\[ref=([^\]]+)\]', snapshot.content[0].text)
        assert name is not None
        fields = [
            {"type": "textbox", "ref": name[1], "value": "abc"},
            {"type": "textbox", "selector": "#notes", "value": "x\ny"},
            {"type": "textbox", "selector": "#editor", "value": "xyα🙂"},
            {"type": "checkbox", "selector": "#agree", "value": True},
            {"type": "radio", "selector": "#pro", "value": True},
            {"type": "combobox", "selector": "#country", "value": "United Kingdom"},
        ]
        result = await client.call_tool(
            "browser_fill_fields", {"session_id": "browser", "fields": fields, "slowly": True}
        )
        assert not result.is_error
        assert await page.locator("#name").input_value() == "abc"
        assert await page.locator("#notes").input_value() == "x\ny"
        assert await page.locator("#editor").inner_text() == "xyα🙂"
        assert await page.locator("#agree").is_checked()
        assert await page.locator("#pro").is_checked()
        assert await page.locator("#country").input_value() == "gb"
        events = loads(await page.locator("#events").input_value())
        keys = [
            event
            for event in events
            if event["target"] == "name" and event["type"] == "keydown" and event["key"] in "abc"
        ]
        assert [event["key"] for event in keys] == ["a", "b", "c"]
        assert all(second["time"] - first["time"] >= 40 for first, second in zip(keys, keys[1:]))
        for previous, following in zip(
            ("name", "notes", "editor", "agree", "pro"), ("notes", "editor", "agree", "pro", "country")
        ):
            previous_time = max(
                event["time"] for event in events if event["target"] == previous and event["type"] == "input"
            )
            next_time = min(
                event["time"] for event in events if event["target"] == following and event["type"] == "input"
            )
            assert next_time - previous_time >= 80
        cleared = await client.call_tool(
            "browser_fill_fields",
            {"session_id": "browser", "fields": [{**TEXT_FIELD, "value": ""}], "slowly": True},
        )
        assert not cleared.is_error
        assert await page.locator("#name").input_value() == ""
        assert await page.locator("#submitted").inner_text() == "0"
        assert session.page_pool.pages[0].state == "ready"


@pytest.mark.asyncio
@pytest.mark.parametrize("session_type", ["dynamic", "stealthy"])
@pytest.mark.parametrize("slowly", [False, True])
async def test_browser_fill_fields_live_caret_selection_and_submit(session_type: SessionType, slowly: bool) -> None:
    async with _browser(session_type) as (client, session, page):
        snapshot = await client.call_tool("browser_snapshot", {"session_id": "browser"})
        assert not snapshot.is_error
        assert snapshot.content and isinstance(snapshot.content[0], TextContent)
        name = search(r'textbox "Name".*?\[ref=([^\]]+)\]', snapshot.content[0].text)
        assert name is not None

        async def fill(fields: list[dict[str, Any]]) -> None:
            result = await client.call_tool(
                "browser_fill_fields", {"session_id": "browser", "fields": fields, "slowly": slowly}
            )
            assert not result.is_error
            assert session.page_pool.pages[0].state == "ready"

        async def press(keys: list[str]) -> None:
            result = await client.call_tool("browser_press_key", {"session_id": "browser", "keys": keys})
            assert not result.is_error

        await fill([{**TEXT_FIELD, "value": "abcd"}])
        await press(["ArrowLeft"])
        await fill([{"type": "textbox", "ref": name[1], "value": "XY", "clear": False}])
        assert await page.locator("#name").input_value() == "abcXYd"
        await press(["Shift+ArrowLeft", "Shift+ArrowLeft"])
        await fill([{**TEXT_FIELD, "value": "z", "clear": False}])
        assert await page.locator("#name").input_value() == "abczd"
        await fill([{**TEXT_FIELD, "value": "", "clear": False}])
        assert await page.locator("#name").input_value() == "abczd"
        await fill(
            [
                {**TEXT_FIELD, "value": "!", "clear": False},
                {"type": "textbox", "selector": "#notes", "value": "new notes"},
            ]
        )
        assert await page.locator("#name").input_value() == "abcz!d"
        assert await page.locator("#notes").input_value() == "new notes"
        assert await page.locator("#submitted").inner_text() == "0"
        focused = await client.call_tool(
            "browser_mouse", {"session_id": "browser", "actions": [{"type": "click", "ref": name[1]}]}
        )
        assert not focused.is_error
        await press(["Enter"])
        assert await page.locator("#submitted").inner_text() == "1"
        events = loads(await page.locator("#events").input_value())
        assert [
            event["key"] for event in events if event["type"] == "keydown" and event["key"] in ["X", "Y", "z", "!"]
        ] == ["X", "Y", "z", "!"]


@pytest.mark.asyncio
@pytest.mark.parametrize("session_type", ["dynamic", "stealthy"])
async def test_browser_fill_fields_live_failed_field_preserves_prior_changes(session_type: SessionType) -> None:
    async with _browser(session_type) as (client, session, page):
        for selector in ("#missing", "input"):
            await page.locator("#name").fill("initial")
            result = await client.call_tool(
                "browser_fill_fields",
                {
                    "session_id": "browser",
                    "timeout": 100,
                    "fields": [
                        {**TEXT_FIELD, "value": "changed first"},
                        {**TEXT_FIELD, "selector": selector, "value": "fails"},
                        {**TEXT_FIELD, "selector": "#notes", "value": "must not run"},
                    ],
                },
            )
            assert result.is_error
            assert result.content and isinstance(result.content[0], TextContent)
            assert ("Timeout" if selector == "#missing" else "strict mode violation") in result.content[0].text
            assert await page.locator("#name").input_value() == "changed first"
            assert await page.locator("#notes").input_value() == "initial notes"
            assert await page.locator("#submitted").inner_text() == "0"
            assert session.page_pool.pages[0].state == "ready"
