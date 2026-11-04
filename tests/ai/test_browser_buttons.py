import asyncio
from contextlib import suppress
from json import loads
from re import findall
from unittest.mock import AsyncMock, Mock, call

import pytest
from anyio import CancelScope
from mcp.client import Client
from mcp.types import ImageContent, TextContent

from scrapling.core._types import Any
from scrapling.core.ai._browser_actions import BrowserAction
from tests.ai.test_browser_mouse import _server
from tests.ai.test_browser_wait import _browser


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
async def test_mouse_button_schema() -> None:
    server, _, _ = _server()
    async with Client(server._build_server("127.0.0.1", 8000)) as client:
        tool = next(tool for tool in (await client.list_tools()).tools if tool.name == "browser_actions")
    schema = tool.input_schema
    mapping = schema["properties"]["actions"]["items"]["discriminator"]["mapping"]
    assert "drag" not in mapping
    for kind in ("mouse_down", "mouse_up"):
        button = schema["$defs"][mapping[kind].rsplit("/", 1)[1]]
        assert button["required"] == ["type"]
        assert set(button["properties"]) == {"type", "button"}
        assert button["properties"]["button"]["default"] == "left"
        assert set(button["properties"]["button"]["enum"]) == {"left", "right", "middle"}


@pytest.mark.asyncio
@pytest.mark.parametrize("kind", ["mouse_down", "mouse_up"])
@pytest.mark.parametrize("button", [None, "left", "right", "middle"])
async def test_mouse_buttons_use_current_pointer(kind: str, button: str | None) -> None:
    server, session, page = _server()
    async with Client(server._build_server("127.0.0.1", 8000)) as client:
        result = await client.call_tool(
            "browser_actions",
            {"session_id": "browser", "actions": [{"type": kind, **({"button": button} if button else {})}]},
        )
    assert not result.is_error and result.structured_content is None
    assert result.content == [TextContent(type="text", text="Actions completed.")]
    getattr(page.mouse, kind.removeprefix("mouse_")).assert_awaited_once_with(button=button or "left")
    getattr(page.mouse, "up" if kind == "mouse_down" else "down").assert_not_awaited()
    page.mouse.move.assert_not_awaited()
    page.locator.assert_not_called()
    assert session.page_pool.pages[0].state == "ready"


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "invalid",
    [
        {"type": "mouse_down", "button": "back"},
        {"type": "mouse_up", "button": None},
        {"type": "mouse_up", "button": 1},
        {"type": "drag", "source": "#source", "target": "#target"},
        {"type": "drag", "path": [{"x": 100, "y": 100}, {"x": 350, "y": 100}]},
    ],
)
async def test_invalid_button_or_removed_drag_prevents_all_actions(invalid: dict[str, Any]) -> None:
    server, session, page = _server()
    async with Client(server._build_server("127.0.0.1", 8000)) as client:
        result = await client.call_tool(
            "browser_actions",
            {"session_id": "browser", "actions": [{"type": "mouse_down"}, invalid, {"type": "mouse_up"}]},
        )
    assert result.is_error
    page.is_closed.assert_not_called()
    page.mouse.down.assert_not_awaited()
    page.mouse.up.assert_not_awaited()
    assert session.page_pool.pages[0].state == "ready"


@pytest.mark.asyncio
@pytest.mark.parametrize("slowly", [False, True])
async def test_button_chain_keeps_order_and_page_reserved(slowly: bool, monkeypatch: pytest.MonkeyPatch) -> None:
    server, session, page = _server()
    pause = AsyncMock()
    monkeypatch.setattr("scrapling.core.ai._browser_actions.sleep", pause)
    events = Mock()

    async def reserved(*args: Any, **kwargs: Any) -> None:
        assert session.page_pool.pages[0].state == "busy"

    for name, method in (
        ("hover", page.locator.return_value.hover),
        ("move", page.mouse.move),
        ("down", page.mouse.down),
        ("up", page.mouse.up),
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
                    {"type": "move", "target": "aria-ref=e1", "timeout": 19},
                    {"type": "mouse_down", "button": "right"},
                    {"type": "move", "x": 350, "y": 100, "steps": 3},
                    {"type": "mouse_up", "button": "right"},
                ],
            },
        )
    assert not result.is_error
    assert events.mock_calls == [
        call.hover(timeout=19),
        call.down(button="right"),
        call.move(350, 100, steps=3),
        call.up(button="right"),
    ]
    assert pause.await_count == (3 if slowly else 0)
    assert session.page_pool.pages[0].state == "ready"


@pytest.mark.asyncio
@pytest.mark.parametrize("kind", ["mouse_down", "move", "mouse_up"])
async def test_button_chain_error_stops_without_implicit_release(kind: str) -> None:
    server, session, page = _server()
    error = RuntimeError("input failed")
    method = getattr(page.mouse, kind.removeprefix("mouse_"))
    method.side_effect = error
    action: BrowserAction = {"type": "move", "x": 350, "y": 100}
    if kind == "mouse_down":
        action = {"type": "mouse_down"}
    elif kind == "mouse_up":
        action = {"type": "mouse_up"}
    with pytest.raises(RuntimeError, match=rf"Action 1 \({kind}\) failed: input failed") as caught:
        await server.browser_actions("browser", [action, {"type": "wheel", "delta_y": 1}])
    assert caught.value.__cause__ is error
    assert page.mouse.up.await_count == (1 if kind == "mouse_up" else 0)
    page.mouse.wheel.assert_not_awaited()
    assert session.page_pool.pages[0].state == "ready"
    method.side_effect = None
    assert await server.browser_actions("browser", [{"type": "mouse_up"}]) == "Actions completed."


@pytest.mark.asyncio
@pytest.mark.parametrize("cancel_mode", ["task", "scope"])
async def test_cancelled_move_allows_explicit_release(cancel_mode: str) -> None:
    server, session, page = _server()
    entered = asyncio.Event()
    scope = CancelScope()

    async def pending(*args: Any, **kwargs: Any) -> None:
        entered.set()
        await asyncio.Event().wait()

    page.mouse.move.side_effect = pending

    async def run() -> None:
        with scope:
            await server.browser_actions(
                "browser", [{"type": "mouse_down"}, {"type": "move", "x": 350, "y": 100}, {"type": "mouse_up"}]
            )

    task = asyncio.create_task(run())
    try:
        await asyncio.wait_for(entered.wait(), 5)
        assert session.page_pool.pages[0].state == "busy"
        with pytest.raises(RuntimeError, match="busy"):
            await server.browser_actions("browser", [{"type": "mouse_up"}])
        scope.cancel() if cancel_mode == "scope" else task.cancel()
        if cancel_mode == "scope":
            await asyncio.wait_for(task, 5)
            assert scope.cancelled_caught
        else:
            with pytest.raises(asyncio.CancelledError):
                await asyncio.wait_for(task, 5)
    finally:
        if not task.done():
            task.cancel()
        with suppress(asyncio.CancelledError):
            await task
    page.mouse.down.assert_awaited_once_with(button="left")
    page.mouse.up.assert_not_awaited()
    assert session.page_pool.pages[0].state == "ready"
    await server.browser_actions("browser", [{"type": "mouse_up"}])
    page.mouse.up.assert_awaited_once_with(button="left")


@pytest.mark.browser
@pytest.mark.asyncio
@pytest.mark.parametrize("mode", ["selector", "ref", "coordinates"])
async def test_button_chain_live_html_drop(mode: str) -> None:
    async with _browser() as (client, _, page):
        await page.set_content(HTML)
        source, target = {"target": "#source"}, {"target": "#target"}
        if mode == "ref":
            snapshot = await page.locator("body").aria_snapshot(mode="ai")
            refs = dict(findall(r'button "(Source|Target)" \[ref=(e\d+)\]', snapshot))
            assert set(refs) == {"Source", "Target"}, snapshot
            source, target = {"target": f"aria-ref={refs['Source']}"}, {"target": f"aria-ref={refs['Target']}"}
        moves = (
            [{"type": "move", "x": 100, "y": 100}, {"type": "move", "x": 350, "y": 100, "steps": 3}]
            if mode == "coordinates"
            else [{"type": "move", **source}, {"type": "move", **target}]
        )
        result = await client.call_tool(
            "browser_actions",
            {
                "session_id": "browser",
                "actions": [moves[0], {"type": "mouse_down"}, moves[1], moves[1], {"type": "mouse_up"}],
            },
        )
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
@pytest.mark.parametrize("observe", ["browser_extract", "browser_screenshot", "browser_observe"])
async def test_live_slider_stays_held_across_observation_calls(observe: str) -> None:
    async with _browser() as (client, session, page):
        await page.set_content("""<input type="range" min="0" max="100" value="0" style="width:300px">
            <textarea id="events" hidden>[]</textarea><script>
            for (const type of ['mousedown', 'mousemove', 'mouseup']) document.addEventListener(type, event => {
                const events = document.querySelector('#events');
                events.value = JSON.stringify([...JSON.parse(events.value), {
                    type, buttons: event.buttons, trusted: event.isTrusted
                }]);
            });
            </script>""")
        slider = page.locator("input")
        box = await slider.bounding_box()
        assert box is not None
        y = box["y"] + box["height"] / 2
        assert not (
            await client.call_tool(
                "browser_actions",
                {
                    "session_id": "browser",
                    "actions": [{"type": "move", "x": box["x"] + 8, "y": y}, {"type": "mouse_down"}],
                },
            )
        ).is_error
        for fraction in (0.35, 0.7, 1):
            assert not (
                await client.call_tool(
                    "browser_actions",
                    {
                        "session_id": "browser",
                        "actions": [{"type": "move", "x": box["x"] + 8 + (box["width"] - 16) * fraction, "y": y}],
                    },
                )
            ).is_error
            observed = await client.call_tool(
                observe,
                {
                    "session_id": "browser",
                    **({"max_frames": 2} if observe == "browser_observe" else {}),
                },
            )
            assert not observed.is_error, observed
            if observe != "browser_extract":
                assert any(isinstance(block, ImageContent) for block in observed.content)
            value = await client.call_tool(
                "browser_evaluate",
                {"session_id": "browser", "expression": "Number(document.querySelector('input').value)"},
            )
            assert not value.is_error and isinstance(value.content[0], TextContent)
            assert abs(loads(value.content[0].text) - fraction * 100) <= 2
            events = loads(await page.locator("#events").input_value())
            assert sum(event["type"] == "mousedown" for event in events) == 1
            assert not any(event["type"] == "mouseup" for event in events)
            assert events[-1]["buttons"] == 1 and all(event["trusted"] for event in events)
            assert session.page_pool.pages[0].state == "ready"
        assert not (
            await client.call_tool("browser_actions", {"session_id": "browser", "actions": [{"type": "mouse_up"}]})
        ).is_error
        events = loads(await page.locator("#events").input_value())
        assert events[-1]["type"] == "mouseup" and events[-1]["buttons"] == 0
        assert not (
            await client.call_tool(
                "browser_actions", {"session_id": "browser", "actions": [{"type": "move", "x": box["x"] + 8, "y": y}]}
            )
        ).is_error
        assert int(await slider.input_value()) >= 98


@pytest.mark.browser
@pytest.mark.asyncio
async def test_live_failed_move_keeps_button_held_until_release() -> None:
    async with _browser() as (client, _, page):
        await page.set_content(HTML)
        await page.locator("#source").evaluate("el => el.draggable = false")
        result = await client.call_tool(
            "browser_actions",
            {
                "session_id": "browser",
                "actions": [
                    {"type": "move", "target": "#source"},
                    {"type": "mouse_down"},
                    {"type": "move", "target": "#missing", "timeout": 100},
                    {"type": "mouse_up"},
                ],
            },
        )
        assert result.is_error
        assert not (
            await client.call_tool(
                "browser_actions", {"session_id": "browser", "actions": [{"type": "move", "x": 20, "y": 20}]}
            )
        ).is_error
        events = loads(await page.locator("#events").input_value())
        assert not any(event["type"] == "mouseup" for event in events)
        assert events[-1]["buttons"] == 1
        assert not (
            await client.call_tool("browser_actions", {"session_id": "browser", "actions": [{"type": "mouse_up"}]})
        ).is_error
        events = loads(await page.locator("#events").input_value())
        assert events[-1]["type"] == "mouseup" and events[-1]["buttons"] == 0
