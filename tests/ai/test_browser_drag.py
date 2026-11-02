import asyncio
from contextlib import suppress
from json import loads
from re import findall
from unittest.mock import AsyncMock, Mock, call

import pytest
from anyio import CancelScope
from mcp.client import Client
from mcp.types import TextContent
from patchright.async_api import TimeoutError as PatchrightTimeoutError
from pydantic import TypeAdapter, ValidationError

from scrapling.core._types import Any
from scrapling.core.ai import ScraplingMCPServer
from scrapling.core.ai._browser_actions import BrowserAction, _MouseDrag
from scrapling.core.ai.server import _SessionEntry
from tests.ai.test_browser_mouse import _server
from tests.ai.test_browser_wait import _browser


ELEMENT: _MouseDrag = {"type": "drag", "source": "#source", "target": "#target"}
PATH: _MouseDrag = {"type": "drag", "path": [{"x": 100, "y": 100}, {"x": 200, "y": 150}, {"x": 350, "y": 100}]}
HTML = """<!DOCTYPE html><style>
#source, #target { position: absolute; top: 80px; width: 80px; height: 80px; }
#source { left: 80px; background: blue; }
#target { left: 320px; background: green; }
</style><div id="source" role="button" aria-label="Source" draggable="true">Source</div>
<div id="target" role="button" aria-label="Target">Target</div><textarea id="events" hidden>[]</textarea>
<script>
const events = document.querySelector('#events');
for (const type of ['mousedown', 'mousemove', 'mouseup', 'dragstart', 'dragover', 'drop', 'dragend']) {
    document.addEventListener(type, event => {
        events.value = JSON.stringify([...JSON.parse(events.value), {
            type, x: event.clientX, y: event.clientY, buttons: event.buttons,
            trusted: event.isTrusted, target: event.target.id
        }]);
        if (type === 'dragstart') event.dataTransfer.setData('text/plain', 'moved');
        if (type === 'dragover') event.preventDefault();
        if (type === 'drop') event.target.dataset.dropped = event.dataTransfer.getData('text/plain');
    });
}
</script>"""


@pytest.mark.asyncio
async def test_drag_schema() -> None:
    server, _, _ = _server()
    async with Client(server._build_server("127.0.0.1", 8000)) as client:
        tool = next(tool for tool in (await client.list_tools()).tools if tool.name == "browser_actions")
    schema = tool.input_schema
    ref = schema["properties"]["actions"]["items"]["discriminator"]["mapping"]["drag"]
    drag = schema["$defs"][ref.rsplit("/", 1)[1]]
    assert drag["required"] == ["type"]
    assert set(drag["properties"]) == {"type", "source", "target", "path", "steps", "timeout"}
    assert drag["properties"]["path"]["minItems"] == 2
    assert drag["properties"]["steps"]["default"] == 1
    assert drag["properties"]["timeout"]["default"] == 30000


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "values",
    [
        {},
        {"source": "#source"},
        {"target": "#target"},
        {"source": "", "target": "#target"},
        {"source": "#source", "target": None},
        {"source": "#source", "target": "#target", "path": PATH["path"]},
        {"source": "#source", "path": PATH["path"]},
        {"target": "#target", "path": PATH["path"]},
        {"path": []},
        {"path": [{"x": 1, "y": 2}]},
        {"path": [{"x": 1}, {"x": 2, "y": 3}]},
        {"path": [{"x": "bad", "y": 1}, {"x": 2, "y": 3}]},
        {"path": PATH["path"], "steps": 0},
        {"path": PATH["path"], "steps": 1.5},
        {"source": "#source", "target": "#target", "timeout": -1},
    ],
)
async def test_invalid_drag_prevents_all_actions(values: dict[str, Any]) -> None:
    server, session, page = _server()
    async with Client(server._build_server("127.0.0.1", 8000)) as client:
        result = await client.call_tool(
            "browser_actions",
            {"session_id": "browser", "actions": [{"type": "wheel", "delta_y": 1}, {"type": "drag", **values}]},
        )
    assert result.is_error
    page.is_closed.assert_not_called()
    page.mouse.wheel.assert_not_awaited()
    page.locator.assert_not_called()
    assert session.page_pool.pages[0].state == "ready"


@pytest.mark.parametrize("value", [float("inf"), float("-inf"), float("nan")])
def test_drag_rejects_nonfinite_numbers(value: float) -> None:
    for action in (
        {**ELEMENT, "timeout": value},
        {"type": "drag", "path": [{"x": value, "y": 0}, {"x": 1, "y": 2}]},
        {"type": "drag", "path": [{"x": 0, "y": value}, {"x": 1, "y": 2}]},
    ):
        with pytest.raises(ValidationError):
            TypeAdapter(BrowserAction).validate_python(action)


@pytest.mark.asyncio
@pytest.mark.parametrize("slowly", [False, True])
async def test_drag_modes_keep_order_and_page_reserved(slowly: bool, monkeypatch: pytest.MonkeyPatch) -> None:
    server, session, page = _server()
    page.mouse.down = AsyncMock()
    source, target = Mock(), Mock()
    source.drag_to = AsyncMock()
    page.locator.side_effect = {"aria-ref=e1": source, "aria-ref=e2": target}.__getitem__
    pause = AsyncMock()
    monkeypatch.setattr("scrapling.core.ai._browser_actions.sleep", pause)
    events = Mock()

    async def reserved(*args: Any, **kwargs: Any) -> None:
        assert session.page_pool.pages[0].state == "busy"

    for name, method in (
        ("drag", source.drag_to),
        ("move", page.mouse.move),
        ("down", page.mouse.down),
        ("up", page.mouse.up),
        ("wheel", page.mouse.wheel),
    ):
        method.side_effect = reserved
        events.attach_mock(method, name)
    async with Client(server._build_server("127.0.0.1", 8000)) as client:
        result = await client.call_tool(
            "browser_actions",
            {
                "session_id": "browser",
                "slowly": slowly,
                "actions": [
                    {"type": "drag", "source": "aria-ref=e1", "target": "aria-ref=e2", "steps": 4, "timeout": 19},
                    {**PATH, "steps": 3},
                    {"type": "wheel", "delta_y": 1},
                ],
            },
        )
    assert not result.is_error and result.structured_content is None
    assert result.content == [TextContent(type="text", text="Actions completed.")]
    assert events.mock_calls == [
        call.drag(target, steps=4, timeout=19),
        call.move(x=100, y=100),
        call.down(),
        call.move(x=200, y=150, steps=3),
        call.move(x=350, y=100, steps=3),
        call.move(x=350, y=100),
        call.up(),
        call.wheel(0, 1),
    ]
    assert pause.await_count == (2 if slowly else 0)
    assert session.page_pool.pages[0].state == "ready"


@pytest.mark.asyncio
@pytest.mark.parametrize("stage", ["element", "timeout", "down", "move"])
async def test_drag_failure_releases_button_and_stops_chain(stage: str) -> None:
    server, session, page = _server()
    error = (PatchrightTimeoutError if stage == "timeout" else RuntimeError)("drag failed")
    page.locator.return_value.drag_to = AsyncMock(side_effect=error)
    page.mouse.down = AsyncMock(side_effect=error if stage == "down" else None)
    if stage == "move":
        page.mouse.move.side_effect = [None, error]
    action = ELEMENT if stage in ("element", "timeout") else PATH
    with pytest.raises(RuntimeError, match=r"Action 1 \(drag\) failed: drag failed") as caught:
        await server.browser_actions("browser", [action, {"type": "wheel", "delta_y": 1}])
    assert caught.value.__cause__ is error
    page.mouse.up.assert_awaited_once_with()
    page.mouse.wheel.assert_not_awaited()
    assert session.page_pool.pages[0].state == "ready"


@pytest.mark.asyncio
@pytest.mark.parametrize("closed", [False, True])
async def test_drag_cleanup_preserves_original_error(closed: bool) -> None:
    server, session, page = _server()
    original, cleanup = RuntimeError("drag failed"), RuntimeError("release failed")

    async def fail(*args: Any, **kwargs: Any) -> None:
        page.is_closed.return_value = closed
        raise original

    page.locator.return_value.drag_to = AsyncMock(side_effect=fail)
    page.mouse.up.side_effect = cleanup
    with pytest.raises(RuntimeError, match=r"Action 1 \(drag\) failed: drag failed") as caught:
        await server.browser_actions("browser", [ELEMENT])
    assert caught.value.__cause__ is original
    assert original.__cause__ is (None if closed else cleanup)
    assert page.mouse.up.await_count == (0 if closed else 1)
    assert len(session.page_pool.pages) == (0 if closed else 1)


@pytest.mark.asyncio
@pytest.mark.parametrize("cancel_mode", ["task", "scope"])
@pytest.mark.parametrize("coordinates", [False, True])
async def test_drag_cancellation_keeps_page_busy_until_release(cancel_mode: str, coordinates: bool) -> None:
    server, session, page = _server()
    entered, releasing, release = asyncio.Event(), asyncio.Event(), asyncio.Event()
    scope = CancelScope()

    async def pending(*args: Any, **kwargs: Any) -> None:
        entered.set()
        await asyncio.Event().wait()

    async def unpress() -> None:
        releasing.set()
        await release.wait()

    page.locator.return_value.drag_to = AsyncMock(side_effect=pending)
    page.mouse.down = AsyncMock(side_effect=pending)
    page.mouse.up.side_effect = unpress

    async def run() -> None:
        with scope:
            await server.browser_actions("browser", [PATH if coordinates else ELEMENT, {"type": "wheel", "delta_y": 1}])

    task = asyncio.create_task(run())
    try:
        await asyncio.wait_for(entered.wait(), 5)
        scope.cancel() if cancel_mode == "scope" else task.cancel()
        await asyncio.wait_for(releasing.wait(), 5)
        assert session.page_pool.pages[0].state == "busy"
        with pytest.raises(RuntimeError, match="busy"):
            await server.browser_actions("browser", [{"type": "wheel", "delta_y": 1}])
        release.set()
        if cancel_mode == "scope":
            await asyncio.wait_for(task, 5)
            assert scope.cancelled_caught
        else:
            with pytest.raises(asyncio.CancelledError):
                await asyncio.wait_for(task, 5)
    finally:
        release.set()
        if not task.done():
            task.cancel()
        with suppress(asyncio.CancelledError):
            await task
    page.mouse.up.assert_awaited_once_with()
    page.mouse.wheel.assert_not_awaited()
    assert session.page_pool.pages[0].state == "ready"


@pytest.mark.browser
@pytest.mark.asyncio
@pytest.mark.parametrize("mode", ["selector", "ref", "path"])
async def test_drag_live_html_drop(mode: str) -> None:
    async with _browser() as (client, _, page):
        await page.set_content(HTML)
        action: dict[str, Any] = dict(ELEMENT)
        if mode == "ref":
            snapshot = await page.locator("body").aria_snapshot(mode="ai")
            refs = dict(findall(r'button "(Source|Target)" \[ref=(e\d+)\]', snapshot))
            assert set(refs) == {"Source", "Target"}, snapshot
            action.update(source=f"aria-ref={refs['Source']}", target=f"aria-ref={refs['Target']}")
        elif mode == "path":
            action = dict(PATH)
        result = await client.call_tool("browser_actions", {"session_id": "browser", "actions": [action]})
        assert not result.is_error, result
        assert await page.locator("#target").get_attribute("data-dropped") == "moved"
        events = loads(await page.locator("#events").input_value())
        assert any(event["type"] == "dragstart" for event in events)
        assert any(event["type"] == "drop" and event["target"] == "target" for event in events)
        assert all(event["trusted"] for event in events)
        await page.mouse.move(20, 20)
        assert loads(await page.locator("#events").input_value())[-1]["buttons"] == 0


@pytest.mark.browser
@pytest.mark.asyncio
async def test_drag_live_pointer_path() -> None:
    async with _browser() as (client, _, page):
        await page.set_content(HTML)
        await page.locator("#source").evaluate("el => el.draggable = false")
        result = await client.call_tool("browser_actions", {"session_id": "browser", "actions": [{**PATH, "steps": 3}]})
        assert not result.is_error, result
        events = loads(await page.locator("#events").input_value())
        down = next(i for i, event in enumerate(events) if event["type"] == "mousedown")
        held = events[down + 1 : -1]
        assert len(held) == 7 and all(event["type"] == "mousemove" and event["buttons"] == 1 for event in held)
        assert any((event["x"], event["y"]) == (200, 150) for event in held)
        assert events[-1]["type"] == "mouseup" and events[-1]["buttons"] == 0
        assert (events[-1]["x"], events[-1]["y"]) == (350, 100)


@pytest.mark.browser
@pytest.mark.asyncio
async def test_drag_live_slider_value() -> None:
    async with _browser() as (client, _, page):
        await page.set_content('<input type="range" min="0" max="100" value="0" style="width:300px">')
        slider = page.locator("input")
        box = await slider.bounding_box()
        assert box is not None
        path = [{"x": x, "y": box["y"] + box["height"] / 2} for x in (box["x"] + 8, box["x"] + box["width"] - 8)]
        result = await client.call_tool(
            "browser_actions",
            {
                "session_id": "browser",
                "actions": [{"type": "drag", "path": path, "steps": 5}],
            },
        )
        assert not result.is_error, result
        assert int(await slider.input_value()) >= 95


@pytest.mark.browser
@pytest.mark.asyncio
async def test_drag_live_timeout_releases_button() -> None:
    async with _browser() as (client, _, page):
        await page.set_content(HTML)
        await page.locator("#source").evaluate("el => el.draggable = false")
        result = await client.call_tool(
            "browser_actions",
            {
                "session_id": "browser",
                "actions": [{**ELEMENT, "target": "#missing", "timeout": 300}],
            },
        )
        assert result.is_error
        events = loads(await page.locator("#events").input_value())
        assert any(event["type"] == "mousedown" for event in events)
        await page.mouse.move(20, 20)
        assert loads(await page.locator("#events").input_value())[-1]["buttons"] == 0


@pytest.mark.browser
@pytest.mark.asyncio
@pytest.mark.parametrize("cancel_mode", ["task", "scope"])
@pytest.mark.parametrize("hidden", ["source", "target"])
async def test_drag_live_cancel_aborts_pending_press(cancel_mode: str, hidden: str) -> None:
    async with _browser() as (_, session, page):
        server = ScraplingMCPServer()
        server._sessions["browser"] = _SessionEntry(session, "stealthy")
        await page.set_content(HTML)
        await page.locator("#source").evaluate("el => el.draggable = false")
        await page.locator(f"#{hidden}").evaluate("el => el.hidden = true")
        scope = CancelScope()

        async def run() -> None:
            with scope:
                await server.browser_actions("browser", [{**ELEMENT, "timeout": 0}])

        task = asyncio.create_task(run())
        try:
            if hidden == "target":
                await page.wait_for_function(
                    "JSON.parse(document.querySelector('#events').value).some(e => e.type === 'mousedown')"
                )
            else:
                await page.wait_for_timeout(100)
            scope.cancel() if cancel_mode == "scope" else task.cancel()
            if cancel_mode == "scope":
                await asyncio.wait_for(task, 5)
                assert scope.cancelled_caught
            else:
                with pytest.raises(asyncio.CancelledError):
                    await asyncio.wait_for(task, 5)
            stopped = loads(await page.locator("#events").input_value())
            await page.locator(f"#{hidden}").evaluate("el => el.hidden = false")
            await page.wait_for_timeout(600)
            assert loads(await page.locator("#events").input_value()) == stopped
            await page.mouse.move(20, 20)
            events = loads(await page.locator("#events").input_value())
            assert sum(event["type"] == "mousedown" for event in events) == (1 if hidden == "target" else 0)
            assert events[-1]["buttons"] == 0
            assert session.page_pool.pages[0].state == "ready"
        finally:
            if not task.done():
                task.cancel()
            with suppress(asyncio.CancelledError):
                await task
