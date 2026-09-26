import asyncio
from contextlib import asynccontextmanager
from json import loads
from os import getenv
from unittest.mock import AsyncMock, Mock

import pytest
from anyio import CancelScope
from mcp.client import Client
from mcp.types import TextContent
from pydantic import ValidationError

from scrapling.core.ai import ScraplingMCPServer, SessionType, _SessionEntry
from scrapling.core._types import Any, AsyncGenerator
from scrapling.engines._browsers._base import AsyncSession


HTML = """<!DOCTYPE html><html><head><style>
html { scroll-behavior: auto; }
body { margin: 0; }
#surface { width: 3000px; height: 3000px; }
#panel { position: fixed; left: 40px; top: 40px; width: 240px; height: 180px;
    overflow: auto; overscroll-behavior: contain; scroll-behavior: auto; }
#content { width: 2000px; height: 2000px; }
</style></head><body><main id="surface">Page</main><div id="panel"><div id="content">Panel</div></div>
<textarea id="events" hidden>[]</textarea><script>
document.addEventListener('wheel', event => {
    const events = document.querySelector('#events');
    events.value = JSON.stringify([...JSON.parse(events.value), {dx: event.deltaX, dy: event.deltaY,
        x: event.clientX, y: event.clientY, mode: event.deltaMode, trusted: event.isTrusted,
        target: event.target.closest('#panel') ? 'panel' : 'page'}]);
}, {passive: true});
</script></body></html>"""


def _server(session_type: SessionType = "dynamic") -> tuple[ScraplingMCPServer, AsyncSession, Mock]:
    server = ScraplingMCPServer()
    session = AsyncSession()
    session._is_alive = True
    page = Mock()
    page.is_closed.return_value = False
    page.mouse.wheel = AsyncMock()
    session.page_pool.add_page(page).mark_ready()
    server._sessions["browser"] = _SessionEntry(session, session_type)
    return server, session, page


@pytest.mark.asyncio
async def test_browser_wheel_schema() -> None:
    async with Client(ScraplingMCPServer()._build_server("127.0.0.1", 8000)) as client:
        tool = next(tool for tool in (await client.list_tools()).tools if tool.name == "browser_mouse_wheel")
    assert set(tool.input_schema["properties"]) == {"session_id", "delta_x", "delta_y"}
    assert tool.input_schema["required"] == ["session_id"]
    for field in ("delta_x", "delta_y"):
        assert tool.input_schema["properties"][field]["type"] == "number"
        assert tool.input_schema["properties"][field]["default"] == 0


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "values", [{}, {"delta_y": 120}, {"delta_x": -12.5, "delta_y": 23.5}, {"delta_x": 10.5, "delta_y": -20.5}]
)
async def test_browser_wheel_forwards_deltas_without_moving_or_capturing(values: dict[str, float]) -> None:
    server, session, page = _server()
    async with Client(server._build_server("127.0.0.1", 8000)) as client:
        result = await client.call_tool("browser_mouse_wheel", {"session_id": "browser", **values})
    assert not result.is_error
    assert result.structured_content is None
    assert result.content == [TextContent(type="text", text="Wheel event sent.")]
    page.mouse.wheel.assert_awaited_once_with(values.get("delta_x", 0), values.get("delta_y", 0))
    page.mouse.move.assert_not_called()
    page.locator.assert_not_called()
    page.aria_snapshot.assert_not_called()
    page.screenshot.assert_not_called()
    assert session.page_pool.pages[0].state == "ready"


@pytest.mark.asyncio
@pytest.mark.parametrize("field", ["delta_x", "delta_y"])
@pytest.mark.parametrize("value", ["invalid", "NaN", "Infinity", None])
async def test_browser_wheel_invalid_input_does_not_reserve_page(field: str, value: Any) -> None:
    server, session, page = _server()
    async with Client(server._build_server("127.0.0.1", 8000)) as client:
        result = await client.call_tool("browser_mouse_wheel", {"session_id": "browser", field: value})
    assert result.is_error
    page.is_closed.assert_not_called()
    page.mouse.wheel.assert_not_awaited()
    assert session.page_pool.pages[0].state == "ready"


@pytest.mark.parametrize("value", [float("nan"), float("inf"), float("-inf")])
def test_browser_wheel_schema_rejects_nonfinite_deltas(value: float) -> None:
    tool = ScraplingMCPServer()._build_server("127.0.0.1", 8000)._tool_manager.get_tool("browser_mouse_wheel")
    assert tool is not None
    for field in ("delta_x", "delta_y"):
        with pytest.raises(ValidationError):
            tool.fn_metadata.arg_model.model_validate({"session_id": "browser", field: value})


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
async def test_browser_wheel_session_errors_reach_mcp(state: str, message: str) -> None:
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
        result = await client.call_tool("browser_mouse_wheel", {"session_id": "browser", "delta_y": 120})
    assert result.is_error
    assert result.content and isinstance(result.content[0], TextContent)
    assert message in result.content[0].text
    page.mouse.wheel.assert_not_awaited()


@pytest.mark.asyncio
async def test_browser_wheel_error_is_not_retried_and_releases_page() -> None:
    server, session, page = _server()
    page.mouse.wheel.side_effect = RuntimeError("wheel failed")
    async with Client(server._build_server("127.0.0.1", 8000)) as client:
        result = await client.call_tool("browser_mouse_wheel", {"session_id": "browser", "delta_y": 120})
    assert result.is_error
    assert result.content and isinstance(result.content[0], TextContent)
    assert "wheel failed" in result.content[0].text
    page.mouse.wheel.assert_awaited_once()
    assert session.page_pool.pages[0].state == "ready"
    page.mouse.wheel.side_effect = None
    assert await server.browser_mouse_wheel("browser", delta_y=-120) == "Wheel event sent."


@pytest.mark.asyncio
@pytest.mark.parametrize("cancel_mode", ["task", "scope"])
async def test_browser_wheel_reserves_page_until_cancelled(cancel_mode: str) -> None:
    server, session, page = _server()
    entered = asyncio.Event()
    scope = CancelScope()

    async def pending(*args: Any, **kwargs: Any) -> None:
        entered.set()
        await asyncio.Event().wait()

    async def wheel() -> None:
        with scope:
            await server.browser_mouse_wheel("browser", delta_y=120)

    page.mouse.wheel.side_effect = pending
    task = asyncio.create_task(wheel())
    try:
        await asyncio.wait_for(entered.wait(), 5)
        assert session.page_pool.pages[0].state == "busy"
        with pytest.raises(RuntimeError, match="busy"):
            await server.browser_mouse_wheel("browser", delta_y=120)
    finally:
        scope.cancel() if cancel_mode == "scope" else task.cancel()
        if cancel_mode == "scope":
            await asyncio.wait_for(task, 5)
            assert scope.cancelled_caught
        else:
            with pytest.raises(asyncio.CancelledError):
                await task
    page.mouse.wheel.assert_awaited_once()
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
                "browser_fetch", {"session_id": "browser", "url": "https://wheel.test/", "google_search": False}
            )
            assert not fetched.is_error
            yield client, session, session.page_pool.pages[0].page
        finally:
            closed = await client.call_tool("close_session", {"session_id": "browser"})
            assert not closed.is_error


@pytest.mark.asyncio
@pytest.mark.parametrize("session_type", ["dynamic", "stealthy"])
async def test_browser_wheel_live_scrolls_under_current_pointer(session_type: SessionType) -> None:
    async with _browser(session_type) as (client, session, page):
        expected = {"page": [0, 0], "panel": [0, 0]}
        events_count = 0
        for target, x, y in (("page", 400, 300), ("panel", 100, 100)):
            moved = await client.call_tool("browser_mouse_move", {"session_id": "browser", "x": x, "y": y})
            assert not moved.is_error
            for dx, dy in ((0, 120), (80, 0), (0, -60), (-40, 0)):
                result = await client.call_tool(
                    "browser_mouse_wheel", {"session_id": "browser", "delta_x": dx, "delta_y": dy}
                )
                assert not result.is_error
                expected[target][0] += dx
                expected[target][1] += dy
                await page.wait_for_function(
                    """([target, x, y]) => {
                        const element = target === 'page' ? document.scrollingElement : document.querySelector('#panel');
                        return Math.abs(element.scrollLeft - x) < 1 && Math.abs(element.scrollTop - y) < 1;
                    }""",
                    arg=[target, *expected[target]],
                    timeout=5000,
                )
                assert (
                    await page.evaluate("""() => ({page: [scrollX, scrollY], panel:
                    [document.querySelector('#panel').scrollLeft, document.querySelector('#panel').scrollTop]})""")
                    == expected
                )
                events = loads(await page.locator("#events").input_value())
                events_count += 1
                assert len(events) == events_count
                event = events[-1]
                for axis, delta in (("dx", dx), ("dy", dy)):
                    assert event[axis] == 0 if delta == 0 else event[axis] * delta > 0
                assert event.items() >= {"x": x, "y": y, "mode": 0, "trusted": True, "target": target}.items()
                assert session.page_pool.pages[0].state == "ready"
