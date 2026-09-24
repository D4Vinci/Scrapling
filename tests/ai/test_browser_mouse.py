import asyncio
from contextlib import suppress
from json import loads
from os import getenv
from re import search
from unittest.mock import AsyncMock, Mock

import pytest
from anyio import CancelScope
from mcp.client import Client
from mcp.types import TextContent
from patchright.async_api import Error as PatchrightError
from patchright.async_api import TimeoutError as PatchrightTimeoutError
from playwright.async_api import Error as PlaywrightError
from playwright.async_api import TimeoutError as PlaywrightTimeoutError
from pydantic import ValidationError

from scrapling.core.ai import ScraplingMCPServer, SessionType, _SessionEntry
from scrapling.core._types import Any
from scrapling.engines._browsers._base import AsyncSession


HTML = """<!DOCTYPE html><html><head><style>
#target { position: absolute; left: 80px; top: 80px; width: 120px; height: 60px; }
#target:hover { background: rgb(0, 128, 0); }
#next { position: absolute; left: 80px; top: 180px; width: 120px; height: 40px; }
#below { position: absolute; left: 80px; top: 4000px; width: 120px; height: 60px; }
</style></head><body><button id="target">Target</button><a id="next" href="/next">Next page</a>
<button id="below">Below</button>
<textarea id="events" hidden>[]</textarea><script>
const events = document.querySelector('#events');
for (const type of ['mousemove', 'mousedown', 'mouseup', 'click', 'dblclick', 'contextmenu', 'auxclick']) {
    document.addEventListener(type, event => {
        events.value = JSON.stringify([...JSON.parse(events.value), {type, x: event.clientX, y: event.clientY,
            button: event.button, buttons: event.buttons, detail: event.detail, trusted: event.isTrusted,
            target: event.target.id}]);
        if (type === 'contextmenu') event.preventDefault();
    });
}
</script></body></html>"""


def _server(session_type: SessionType = "dynamic") -> tuple[ScraplingMCPServer, AsyncSession, Mock]:
    server = ScraplingMCPServer()
    session = AsyncSession()
    session._is_alive = True
    page = Mock()
    page.is_closed.return_value = False
    page.mouse.move = AsyncMock()
    page.mouse.click = AsyncMock()
    page.mouse.up = AsyncMock()
    page.locator.return_value.click = AsyncMock()
    page.locator.return_value.hover = AsyncMock()
    session.page_pool.add_page(page).mark_ready()
    server._sessions["browser"] = _SessionEntry(session, session_type)
    return server, session, page


@pytest.mark.asyncio
async def test_browser_mouse_schema_and_annotations() -> None:
    server = ScraplingMCPServer()
    async with Client(server._build_server("127.0.0.1", 8000)) as client:
        tools = {tool.name: tool for tool in (await client.list_tools()).tools}
        removed = await client.call_tool("browser_mouse", {"session_id": "browser", "action": "move", "x": 1, "y": 2})
    assert "browser_mouse" not in tools and removed.is_error
    move, click = tools["browser_mouse_move"], tools["browser_click"]
    assert set(move.input_schema["properties"]) == {"session_id", "x", "y", "steps", "selector", "ref", "timeout"}
    assert move.input_schema["required"] == ["session_id"]
    assert move.input_schema["properties"]["steps"]["exclusiveMinimum"] == 0
    assert move.input_schema["properties"]["steps"]["default"] == 1
    assert move.input_schema["properties"]["timeout"]["minimum"] == 0
    assert move.input_schema["properties"]["timeout"]["default"] == 30000
    properties = click.input_schema["properties"]
    assert set(properties) == {"session_id", "selector", "ref", "x", "y", "button", "click_count", "delay", "timeout"}
    assert click.input_schema["required"] == ["session_id"]
    assert set(properties["button"]["enum"]) == {"left", "right", "middle"}
    assert properties["click_count"]["exclusiveMinimum"] == 0
    assert properties["delay"]["minimum"] == properties["timeout"]["minimum"] == 0
    assert {name: properties[name]["default"] for name in ("button", "click_count", "delay", "timeout")} == {
        "button": "left",
        "click_count": 1,
        "delay": 0,
        "timeout": 30000,
    }
    for tool in (move, click):
        assert tool.output_schema is None
        assert tool.annotations is not None
        assert tool.annotations.read_only_hint is False
        assert tool.annotations.destructive_hint is True
        assert tool.annotations.idempotent_hint is False
        assert tool.annotations.open_world_hint is True


@pytest.mark.asyncio
@pytest.mark.parametrize("session_type", ["dynamic", "stealthy"])
@pytest.mark.parametrize(
    "tool, target, options, expected",
    [
        ("browser_mouse_move", {"x": -12.5, "y": 23.5}, {}, {"steps": 1}),
        ("browser_mouse_move", {"x": -12.5, "y": 23.5}, {"steps": 5, "timeout": 400}, {"steps": 5}),
        ("browser_mouse_move", {"selector": "button"}, {}, {"timeout": 30000}),
        ("browser_mouse_move", {"ref": "e4"}, {"steps": 5, "timeout": 500}, {"timeout": 500}),
        ("browser_mouse_move", {"selector": "button"}, {"timeout": 0}, {"timeout": 0}),
        ("browser_click", {"x": -12.5, "y": 23.5}, {}, {"button": "left", "click_count": 1, "delay": 0}),
        (
            "browser_click",
            {"x": -12.5, "y": 23.5},
            {"button": "middle", "timeout": 400},
            {"button": "middle", "click_count": 1, "delay": 0},
        ),
        (
            "browser_click",
            {"selector": "button"},
            {},
            {"button": "left", "click_count": 1, "delay": 0, "timeout": 30000},
        ),
        (
            "browser_click",
            {"ref": "e4"},
            {"button": "right", "click_count": 2, "delay": 30, "timeout": 500},
            {"button": "right", "click_count": 2, "delay": 30, "timeout": 500},
        ),
    ],
)
async def test_browser_mouse_forwards_native_actions(
    session_type: SessionType, tool: str, target: dict[str, Any], options: dict[str, Any], expected: dict[str, Any]
) -> None:
    server, session, page = _server(session_type)
    async with Client(server._build_server("127.0.0.1", 8000)) as client:
        result = await client.call_tool(tool, {"session_id": "browser", **target, **options})
    assert not result.is_error
    assert result.structured_content is None
    message = "Click sent."
    if tool == "browser_mouse_move":
        message = "Mouse moved to (-12.5, 23.5)." if "x" in target else "Mouse hovered over element."
    assert result.content == [TextContent(type="text", text=message)]
    if tool == "browser_mouse_move" and "x" in target:
        page.mouse.move.assert_awaited_once_with(-12.5, 23.5, **expected)
        page.mouse.click.assert_not_awaited()
        page.locator.assert_not_called()
    elif "x" in target:
        page.mouse.click.assert_awaited_once_with(-12.5, 23.5, **expected)
        page.mouse.move.assert_not_awaited()
        page.locator.assert_not_called()
    else:
        page.locator.assert_called_once_with(target["selector"] if "selector" in target else "aria-ref=e4")
        action = "hover" if tool == "browser_mouse_move" else "click"
        getattr(page.locator.return_value, action).assert_awaited_once_with(**expected)
        getattr(page.locator.return_value, "click" if action == "hover" else "hover").assert_not_awaited()
        page.mouse.move.assert_not_awaited()
        page.mouse.click.assert_not_awaited()
    assert session.page_pool.pages_count == 1
    assert session.page_pool.pages[0].state == "ready"
    for name in (
        "goto",
        "evaluate",
        "add_init_script",
        "set_extra_http_headers",
        "unroute_all",
        "set_default_timeout",
        "set_default_navigation_timeout",
        "wait_for_load_state",
    ):
        getattr(page, name).assert_not_called()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "tool, values",
    [
        ("browser_mouse_move", {"x": "invalid"}),
        ("browser_mouse_move", {"y": None}),
        ("browser_mouse_move", {"steps": 1.5}),
        ("browser_mouse_move", {"steps": 0}),
        ("browser_mouse_move", {"steps": -1}),
        ("browser_mouse_move", {"selector": ""}),
        ("browser_mouse_move", {"ref": ""}),
        ("browser_mouse_move", {"timeout": -1}),
        ("browser_click", {"button": "back"}),
        ("browser_click", {"click_count": 1.5}),
        ("browser_click", {"click_count": 0}),
        ("browser_click", {"click_count": -1}),
        ("browser_click", {"delay": -1}),
        ("browser_click", {"delay": "invalid"}),
        ("browser_click", {"timeout": -1}),
        ("browser_click", {"selector": ""}),
        ("browser_click", {"ref": ""}),
    ],
)
async def test_browser_mouse_invalid_input_does_not_reserve_or_use_page(tool: str, values: dict[str, Any]) -> None:
    server, session, page = _server()
    async with Client(server._build_server("127.0.0.1", 8000)) as client:
        result = await client.call_tool(tool, {"session_id": "browser", "x": 10, "y": 20, **values})
    assert result.is_error
    assert result.content and isinstance(result.content[0], TextContent)
    page.mouse.move.assert_not_awaited()
    page.mouse.click.assert_not_awaited()
    page.is_closed.assert_not_called()
    assert session.page_pool.pages[0].state == "ready"


@pytest.mark.parametrize(
    "tool, fields", [("browser_mouse_move", ("x", "y", "timeout")), ("browser_click", ("x", "y", "delay", "timeout"))]
)
@pytest.mark.parametrize("value", [float("nan"), float("inf"), float("-inf")])
def test_browser_mouse_schema_rejects_nonfinite_values(tool: str, fields: tuple[str, ...], value: float) -> None:
    server, session, page = _server()
    registered = server._build_server("127.0.0.1", 8000)._tool_manager.get_tool(tool)
    assert registered is not None
    for field in fields:
        with pytest.raises(ValidationError):
            registered.fn_metadata.arg_model.model_validate({"session_id": "browser", "x": 10, "y": 20, field: value})
    page.mouse.move.assert_not_awaited()
    page.mouse.click.assert_not_awaited()
    page.is_closed.assert_not_called()
    assert session.page_pool.pages[0].state == "ready"


@pytest.mark.asyncio
@pytest.mark.parametrize("tool", ["browser_mouse_move", "browser_click"])
@pytest.mark.parametrize(
    "target",
    [
        {},
        {"x": 1},
        {"y": 2},
        {"selector": "button", "ref": "e2"},
        {"selector": "button", "x": 1},
        {"ref": "e2", "y": 2},
        {"selector": "button", "x": 1, "y": 2},
        {"ref": "e2", "x": 1, "y": 2},
    ],
)
async def test_browser_mouse_requires_exactly_one_complete_target(tool: str, target: dict[str, Any]) -> None:
    server, session, page = _server()
    async with Client(server._build_server("127.0.0.1", 8000)) as client:
        result = await client.call_tool(tool, {"session_id": "browser", **target})
    assert result.is_error
    page.is_closed.assert_not_called()
    page.mouse.move.assert_not_awaited()
    page.mouse.click.assert_not_awaited()
    page.locator.assert_not_called()
    assert session.page_pool.pages[0].state == "ready"


@pytest.mark.asyncio
@pytest.mark.parametrize("tool", ["browser_mouse_move", "browser_click"])
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
async def test_browser_mouse_session_errors_reach_mcp(tool: str, state: str, message: str) -> None:
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
        result = await client.call_tool(tool, {"session_id": "browser", "x": 10, "y": 20})
    assert result.is_error
    assert result.content and isinstance(result.content[0], TextContent)
    assert message in result.content[0].text
    page.mouse.move.assert_not_awaited()
    page.mouse.click.assert_not_awaited()
    if state == "closed":
        assert session.page_pool.pages_count == 0
    elif state == "busy":
        assert session.page_pool.pages[0].state == "busy"


@pytest.mark.asyncio
@pytest.mark.parametrize("tool", ["browser_mouse_move", "browser_click"])
@pytest.mark.parametrize("closed", [False, True])
@pytest.mark.parametrize("target", [{"x": 10, "y": 20}, {"selector": "button"}, {"ref": "e1"}])
async def test_browser_mouse_failure_is_not_retried_and_releases_page(
    tool: str, closed: bool, target: dict[str, Any]
) -> None:
    server, session, page = _server()

    async def fail(*args: Any, **kwargs: Any) -> None:
        page.is_closed.return_value = closed
        raise RuntimeError("mouse failed")

    if tool == "browser_mouse_move":
        action = page.mouse.move if "x" in target else page.locator.return_value.hover
    else:
        action = page.mouse.click if "x" in target else page.locator.return_value.click
    action.side_effect = fail
    async with Client(server._build_server("127.0.0.1", 8000)) as client:
        result = await client.call_tool(tool, {"session_id": "browser", **target})
    assert result.is_error
    assert result.content and isinstance(result.content[0], TextContent)
    assert "mouse failed" in result.content[0].text
    action.assert_awaited_once()
    if closed:
        assert session.page_pool.pages_count == 0
    else:
        assert session.page_pool.pages[0].state == "ready"
        action.side_effect = None
        await getattr(server, tool)("browser", **target)
    page.close.assert_not_called()
    page.mouse.up.assert_not_awaited()


@pytest.mark.asyncio
@pytest.mark.parametrize("target", [{"x": 10, "y": 20}, {"selector": "button"}, {"ref": "e1"}])
async def test_browser_mouse_reserves_page_until_cancelled(target: dict[str, Any]) -> None:
    server, session, page = _server()
    entered = asyncio.Event()
    release = asyncio.Event()

    async def move(*args: Any, **kwargs: Any) -> None:
        entered.set()
        await release.wait()

    action = page.mouse.move if "x" in target else page.locator.return_value.hover
    action.side_effect = move
    task = asyncio.create_task(
        server.browser_mouse_move("browser", 10, 20, 3)
        if "x" in target
        else server.browser_mouse_move("browser", **target)
    )
    try:
        await asyncio.wait_for(entered.wait(), 5)
        assert session.page_pool.pages[0].state == "busy"
        assert session.page_pool.get_ready_page() is None
        with pytest.raises(RuntimeError, match="busy"):
            await server.browser_click("browser", x=10, y=20)
        with pytest.raises(RuntimeError, match="busy"):
            await server.browser_snapshot("browser")
    finally:
        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await task
    assert session.page_pool.pages[0].state == "ready"
    page.close.assert_not_called()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "session_type, error_type", [("dynamic", PlaywrightTimeoutError), ("stealthy", PatchrightTimeoutError)]
)
async def test_browser_click_timeout_holds_page_until_button_is_released(
    session_type: SessionType, error_type: type[Exception]
) -> None:
    server, session, page = _server(session_type)
    releasing = asyncio.Event()
    release = asyncio.Event()

    async def unpress(*args: Any, **kwargs: Any) -> None:
        releasing.set()
        await release.wait()

    page.locator.return_value.click.side_effect = error_type("click timed out")
    page.mouse.up.side_effect = unpress
    task = asyncio.create_task(server.browser_click("browser", selector="button", button="right"))
    try:
        await asyncio.wait_for(releasing.wait(), 5)
        assert session.page_pool.pages[0].state == "busy"
        assert session.page_pool.get_ready_page() is None
        with pytest.raises(RuntimeError, match="busy"):
            await server.browser_mouse_move("browser", 30, 40)
        release.set()
        with pytest.raises(error_type, match="click timed out"):
            await task
    finally:
        release.set()
        with suppress(error_type):
            await task
    page.mouse.up.assert_awaited_once_with(button="right")
    page.locator.return_value.click.assert_awaited_once()
    assert session.page_pool.pages[0].state == "ready"
    page.close.assert_not_called()


@pytest.mark.asyncio
@pytest.mark.parametrize("cancel_mode", ["task", "scope"])
@pytest.mark.parametrize("target", [{"x": 10, "y": 20}, {"selector": "button"}, {"ref": "e1"}])
async def test_browser_mouse_cancelled_click_holds_page_until_button_is_released(
    cancel_mode: str, target: dict[str, Any]
) -> None:
    server, session, page = _server()
    entered = asyncio.Event()
    releasing = asyncio.Event()
    release = asyncio.Event()
    scope = CancelScope()

    async def press(*args: Any, **kwargs: Any) -> None:
        entered.set()
        await asyncio.Event().wait()

    async def unpress(*args: Any, **kwargs: Any) -> None:
        releasing.set()
        await release.wait()

    async def click() -> None:
        with scope:
            await server.browser_click("browser", **target, button="right", delay=60000)

    action = page.mouse.click if "x" in target else page.locator.return_value.click
    action.side_effect = press
    page.mouse.up.side_effect = unpress
    task = asyncio.create_task(click())
    try:
        await asyncio.wait_for(entered.wait(), 5)
        scope.cancel() if cancel_mode == "scope" else task.cancel()
        await asyncio.wait_for(releasing.wait(), 5)
        assert session.page_pool.pages[0].state == "busy"
        assert session.page_pool.get_ready_page() is None
        with pytest.raises(RuntimeError, match="busy"):
            await server.browser_mouse_move("browser", 30, 40)
        release.set()
        if cancel_mode == "scope":
            await asyncio.wait_for(task, 5)
            assert scope.cancelled_caught
        else:
            with pytest.raises(asyncio.CancelledError):
                await task
    finally:
        release.set()
        if not task.done():
            task.cancel()
        with suppress(asyncio.CancelledError):
            await task
    page.mouse.up.assert_awaited_once_with(button="right")
    action.assert_awaited_once()
    assert session.page_pool.pages[0].state == "ready"
    page.close.assert_not_called()


@pytest.mark.asyncio
@pytest.mark.parametrize("session_type", ["dynamic", "stealthy"])
async def test_browser_mouse_live_native_events_and_navigation(session_type: SessionType) -> None:
    server = ScraplingMCPServer(executable_path=getenv("SCRAPLING_EXECUTABLE_PATH"))
    requests: list[str] = []

    async def serve(route: Any) -> None:
        if route.request.is_navigation_request():
            requests.append(route.request.url)
        await route.fulfill(
            status=200,
            content_type="text/html",
            body="<html><body><h1>Arrived</h1></body></html>" if route.request.url.endswith("/next") else HTML,
        )

    async with Client(server._build_server("127.0.0.1", 8000)) as client:
        opened = await client.call_tool("browser_open", {"session_type": session_type, "session_id": "browser"})
        assert not opened.is_error
        try:
            session = server._sessions["browser"].session
            await session.context.route("**/*", serve)
            fetched = await client.call_tool(
                "browser_fetch", {"session_id": "browser", "url": "https://mouse.test/", "google_search": False}
            )
            assert not fetched.is_error
            page_info = session.page_pool.pages[0]
            page = page_info.page
            initial_dom = await page.content()
            moved = await client.call_tool(
                "browser_mouse_move", {"session_id": "browser", "x": 140, "y": 110, "steps": 4}
            )
            assert not moved.is_error
            assert (
                await page.locator("#target").evaluate("element => getComputedStyle(element).backgroundColor")
                == "rgb(0, 128, 0)"
            )
            events = loads(await page.locator("#events").input_value())
            assert events and events[-1]["type"] == "mousemove"
            assert (events[-1]["x"], events[-1]["y"]) == (140, 110)
            for options, event_type, button, detail in (
                ({}, "click", 0, 1),
                ({"click_count": 2, "delay": 10}, "dblclick", 0, 2),
                ({"button": "right"}, "contextmenu", 2, 0),
                ({"button": "middle"}, "auxclick", 1, 1),
            ):
                await page.locator("#events").evaluate("element => element.value = '[]'")
                result = await client.call_tool(
                    "browser_click", {"session_id": "browser", "x": 140, "y": 110, **options}
                )
                assert not result.is_error
                events = loads(await page.locator("#events").input_value())
                assert all(event["trusted"] for event in events)
                assert {"mousedown", "mouseup", event_type} <= {event["type"] for event in events}
                match = next(event for event in events if event["type"] == event_type)
                assert (match["button"], match["detail"]) == (button, detail)
                assert session.page_pool.pages == [page_info] and page_info.state == "ready"
            assert await page.content() == initial_dom
            assert requests == ["https://mouse.test/"]
            clicked = await client.call_tool("browser_click", {"session_id": "browser", "x": 140, "y": 200})
            assert not clicked.is_error
            await page.wait_for_url("https://mouse.test/next", timeout=5000)
            snapshot = await client.call_tool("browser_snapshot", {"session_id": "browser"})
            assert not snapshot.is_error
            assert snapshot.content and isinstance(snapshot.content[0], TextContent)
            assert "Arrived" in snapshot.content[0].text
            assert requests == ["https://mouse.test/", "https://mouse.test/next"]
            assert session.page_pool.pages == [page_info] and page_info.state == "ready"
        finally:
            closed = await client.call_tool("close_session", {"session_id": "browser"})
            assert not closed.is_error


@pytest.mark.asyncio
@pytest.mark.parametrize("session_type", ["dynamic", "stealthy"])
@pytest.mark.parametrize("cancel_mode", ["task", "scope"])
@pytest.mark.parametrize("target_type", ["xy", "ref"])
async def test_browser_mouse_live_cancelled_click_releases_native_button(
    session_type: SessionType, cancel_mode: str, target_type: str
) -> None:
    server = ScraplingMCPServer(executable_path=getenv("SCRAPLING_EXECUTABLE_PATH"))
    scope = CancelScope()
    target: dict[str, Any] = {"x": 140, "y": 110}

    async def serve(route: Any) -> None:
        await route.fulfill(status=200, content_type="text/html", body=HTML)

    async def click() -> None:
        with scope:
            await server.browser_click("browser", **target, delay=60000, timeout=0)

    async with Client(server._build_server("127.0.0.1", 8000)) as client:
        opened = await client.call_tool("browser_open", {"session_type": session_type, "session_id": "browser"})
        assert not opened.is_error
        task = None
        try:
            session = server._sessions["browser"].session
            await session.context.route("**/*", serve)
            fetched = await client.call_tool(
                "browser_fetch", {"session_id": "browser", "url": "https://mouse.test/", "google_search": False}
            )
            assert not fetched.is_error
            page_info = session.page_pool.pages[0]
            page = page_info.page
            if target_type == "ref":
                match = search(r'button "Target".*?\[ref=([^\]]+)\]', await server.browser_snapshot("browser"))
                assert match is not None
                target = {"ref": match[1]}
            task = asyncio.create_task(click())
            await page.wait_for_function(
                "JSON.parse(document.querySelector('#events').value).some(event => event.type === 'mousedown')",
                timeout=5000,
            )
            assert page_info.state == "busy"
            scope.cancel() if cancel_mode == "scope" else task.cancel()
            if cancel_mode == "scope":
                await asyncio.wait_for(task, 5)
                assert scope.cancelled_caught
            else:
                with pytest.raises(asyncio.CancelledError):
                    await asyncio.wait_for(task, 5)
            assert page_info.state == "ready"
            moved = await client.call_tool("browser_mouse_move", {"session_id": "browser", "x": 150, "y": 120})
            assert not moved.is_error
            events = loads(await page.locator("#events").input_value())
            assert all(event["trusted"] for event in events)
            assert len([event for event in events if event["type"] == "mousedown"]) == 1
            assert next(event for event in events if event["type"] == "mousedown")["buttons"] == 1
            assert next(event for event in events if event["type"] == "mouseup")["buttons"] == 0
            assert (events[-1]["type"], events[-1]["buttons"]) == ("mousemove", 0)
            assert session.page_pool.pages == [page_info] and page_info.state == "ready"
        finally:
            if task is not None and not task.done():
                task.cancel()
                with suppress(asyncio.CancelledError):
                    await task
            closed = await client.call_tool("close_session", {"session_id": "browser"})
            assert not closed.is_error


@pytest.mark.asyncio
@pytest.mark.parametrize("session_type", ["dynamic", "stealthy"])
@pytest.mark.parametrize("tool", ["browser_mouse_move", "browser_click"])
async def test_browser_mouse_live_selectors_refs_and_scroll(session_type: SessionType, tool: str) -> None:
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
                "browser_fetch", {"session_id": "browser", "url": "https://mouse.test/", "google_search": False}
            )
            assert not fetched.is_error
            page_info = session.page_pool.pages[0]
            page = page_info.page
            match = search(r'button "Target".*?\[ref=([^\]]+)\]', await server.browser_snapshot("browser"))
            assert match is not None
            ref = match[1]
            initial_dom = await page.content()
            for target in (
                {"selector": "#target"},
                {"selector": 'xpath=//button[@id="target"]'},
                {"ref": ref},
                {"selector": "#below"},
            ):
                await page.mouse.move(0, 0)
                await page.locator("#events").evaluate("element => element.value = '[]'")
                result = await client.call_tool(tool, {"session_id": "browser", **target})
                assert not result.is_error
                events = loads(await page.locator("#events").input_value())
                expected_id = "below" if target.get("selector") == "#below" else "target"
                if tool == "browser_mouse_move":
                    assert events and all(event["type"] == "mousemove" and event["trusted"] for event in events)
                    assert events[-1]["target"] == expected_id
                    assert await page.locator(f"#{expected_id}").evaluate("element => element.matches(':hover')")
                else:
                    clicks = [event for event in events if event["type"] == "click"]
                    assert len(clicks) == 1 and clicks[0]["trusted"]
                    assert clicks[0]["target"] == expected_id
            assert await page.evaluate("window.scrollY") > 0
            assert await page.content() == initial_dom
            await page.locator("#target").evaluate("element => element.remove()")
            for target in ({"selector": "button, a"}, {"selector": "#missing"}, {"ref": ref}):
                await page.locator("#events").evaluate("element => element.value = '[]'")
                with pytest.raises((PlaywrightError, PatchrightError)) as error:
                    await getattr(server, tool)(
                        "browser", selector=target.get("selector"), ref=target.get("ref"), timeout=100
                    )
                events = loads(await page.locator("#events").input_value())
                if target.get("selector") != "button, a":
                    assert isinstance(
                        error.value, PlaywrightTimeoutError if session_type == "dynamic" else PatchrightTimeoutError
                    )
                    assert not any(event["type"] in ("mousedown", "click") for event in events)
                    released = [event for event in events if event["type"] == "mouseup"]
                    if tool == "browser_click":
                        assert len(released) == 1 and released[0]["buttons"] == 0
                    else:
                        assert not released
                else:
                    assert "strict mode violation" in str(error.value)
                    assert not any(event["type"] in ("mousedown", "mouseup", "click") for event in events)
                assert session.page_pool.pages == [page_info] and page_info.state == "ready"
        finally:
            closed = await client.call_tool("close_session", {"session_id": "browser"})
            assert not closed.is_error


@pytest.mark.asyncio
@pytest.mark.parametrize("session_type", ["dynamic", "stealthy"])
async def test_browser_click_live_timeout_releases_native_button(session_type: SessionType) -> None:
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
                "browser_fetch", {"session_id": "browser", "url": "https://mouse.test/", "google_search": False}
            )
            assert not fetched.is_error
            page_info = session.page_pool.pages[0]
            page = page_info.page
            failed = await client.call_tool(
                "browser_click", {"session_id": "browser", "selector": "#target", "delay": 1000, "timeout": 300}
            )
            assert failed.is_error
            events = loads(await page.locator("#events").input_value())
            assert next(event for event in events if event["type"] == "mousedown")["buttons"] == 1
            moved = await client.call_tool("browser_mouse_move", {"session_id": "browser", "x": 150, "y": 120})
            assert not moved.is_error
            events = loads(await page.locator("#events").input_value())
            assert (events[-1]["type"], events[-1]["buttons"]) == ("mousemove", 0)
            assert next(event for event in events if event["type"] == "mouseup")["buttons"] == 0
            assert all(event["trusted"] for event in events)
            assert session.page_pool.pages == [page_info] and page_info.state == "ready"
        finally:
            closed = await client.call_tool("close_session", {"session_id": "browser"})
            assert not closed.is_error
