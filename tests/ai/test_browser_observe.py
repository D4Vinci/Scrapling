import asyncio
from base64 import b64decode
from contextlib import suppress
from json import loads
from os import getenv
from time import time
from unittest.mock import AsyncMock, Mock

import pytest
from anyio import CancelScope
from mcp.client import Client
from mcp.types import ImageContent, TextContent
from patchright.async_api import Error as PatchrightError

from scrapling.core._types import Any
from scrapling.core.ai import ScraplingMCPServer, SessionType
from scrapling.core.ai.server import _SessionEntry
from scrapling.engines._browsers._base import AsyncSession


def _server(session_type: SessionType = "stealthy") -> tuple[ScraplingMCPServer, AsyncSession, Mock]:
    server = ScraplingMCPServer()
    session = AsyncSession()
    session._is_alive = True
    page = Mock()
    page.is_closed.return_value = False
    page.url = "https://observe.test/current"
    page.screencast.start = AsyncMock()
    page.screencast.stop = AsyncMock()
    session.page_pool.add_page(page).mark_ready()
    server._sessions["browser"] = _SessionEntry(session, session_type)
    return server, session, page


def _frame(index: int) -> dict[str, Any]:
    return {
        "data": str(index).encode(),
        "timestamp": 1800000000000.0 + index * 20,
        "viewportWidth": 1200 + index,
        "viewportHeight": 800 + index,
    }


@pytest.mark.asyncio
async def test_browser_observe_schema() -> None:
    async with Client(ScraplingMCPServer()._build_server("127.0.0.1", 8000)) as client:
        tool = next(tool for tool in (await client.list_tools()).tools if tool.name == "browser_observe")
    assert tool.input_schema["required"] == ["session_id"]
    properties = tool.input_schema["properties"]
    assert set(properties) == {"session_id", "duration_ms", "max_frames"}
    for name, default, minimum, maximum in (("duration_ms", 1500, 100, 5000), ("max_frames", 12, 2, 20)):
        assert properties[name]["type"] == "integer"
        assert properties[name]["default"] == default
        assert properties[name]["minimum"] == minimum
        assert properties[name]["maximum"] == maximum
    assert tool.output_schema is None
    assert tool.annotations is not None
    assert tool.annotations.read_only_hint is True
    assert tool.annotations.open_world_hint is True


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "options",
    [
        {"duration_ms": 99},
        {"duration_ms": 5001},
        {"duration_ms": 100.5},
        {"duration_ms": "NaN"},
        {"max_frames": 1},
        {"max_frames": 21},
        {"max_frames": 2.5},
    ],
)
async def test_browser_observe_invalid_input_leaves_page_available(options: dict[str, Any]) -> None:
    server, session, page = _server()
    async with Client(server._build_server("127.0.0.1", 8000)) as client:
        result = await client.call_tool("browser_observe", {"session_id": "browser", **options})
    assert result.is_error
    page.is_closed.assert_not_called()
    page.screencast.start.assert_not_awaited()
    assert session.page_pool.pages[0].state == "ready"


@pytest.mark.asyncio
async def test_browser_observe_returns_paired_frame_data_without_url() -> None:
    server, session, page = _server()

    async def start(**kwargs: Any) -> None:
        assert session.page_pool.pages[0].state == "busy"
        kwargs["on_frame"](_frame(0))
        page.url = "https://observe.test/updated"

    page.screencast.start.side_effect = start
    async with Client(server._build_server("127.0.0.1", 8000)) as client:
        result = await client.call_tool("browser_observe", {"session_id": "browser", "duration_ms": 100})
    assert not result.is_error and result.structured_content is None
    assert len(result.content) == 2
    metadata, image = result.content
    assert isinstance(metadata, TextContent)
    assert loads(metadata.text) == {
        "timestamp_ms": 1800000000000.0,
        "viewport_width": 1200,
        "viewport_height": 800,
    }
    assert isinstance(image, ImageContent)
    assert image.mime_type == "image/jpeg" and b64decode(image.data) == b"0"
    page.screencast.stop.assert_awaited_once()
    page.goto.assert_not_called()
    page.close.assert_not_called()
    assert session.page_pool.pages[0].state == "ready"


@pytest.mark.asyncio
async def test_browser_observe_samples_across_window_and_limits_output() -> None:
    server, session, page = _server()
    emitter: asyncio.Task[None] | None = None

    async def start(**kwargs: Any) -> None:
        nonlocal emitter

        async def emit() -> None:
            for index in range(12):
                kwargs["on_frame"](_frame(index))
                await asyncio.sleep(0.02)

        emitter = asyncio.create_task(emit())

    async def stop() -> None:
        assert session.page_pool.pages[0].state == "busy"
        assert emitter is not None
        emitter.cancel()
        with suppress(asyncio.CancelledError):
            await emitter

    page.screencast.start.side_effect = start
    page.screencast.stop.side_effect = stop
    result = await server.browser_observe("browser", duration_ms=200, max_frames=3)
    assert len(result) % 2 == 0 and 2 <= len(result) // 2 <= 3
    timestamps = []
    for metadata, image in zip(result[::2], result[1::2]):
        assert isinstance(metadata, TextContent)
        assert isinstance(image, ImageContent) and image.mime_type == "image/jpeg"
        expected = _frame(int(b64decode(image.data)))
        frame = loads(metadata.text)
        assert frame == {
            "timestamp_ms": expected["timestamp"],
            "viewport_width": expected["viewportWidth"],
            "viewport_height": expected["viewportHeight"],
        }
        assert b64decode(image.data) == expected["data"]
        timestamps.append(frame["timestamp_ms"])
    assert timestamps == sorted(timestamps) and timestamps[-1] - timestamps[0] >= 80
    assert session.page_pool.pages[0].state == "ready"


@pytest.mark.asyncio
async def test_browser_observe_reports_no_frames_and_stops_capture() -> None:
    server, session, page = _server()
    async with Client(server._build_server("127.0.0.1", 8000)) as client:
        result = await client.call_tool("browser_observe", {"session_id": "browser", "duration_ms": 100})
    assert result.is_error and isinstance(result.content[0], TextContent)
    assert "frame" in result.content[0].text.lower()
    page.screencast.stop.assert_awaited_once()
    assert session.page_pool.pages[0].state == "ready"


@pytest.mark.asyncio
@pytest.mark.parametrize("operation", ["start", "stop"])
async def test_browser_observe_reports_browser_errors_and_releases_page(operation: str) -> None:
    server, session, page = _server()
    getattr(page.screencast, operation).side_effect = PatchrightError("capture failed")
    async with Client(server._build_server("127.0.0.1", 8000)) as client:
        result = await client.call_tool("browser_observe", {"session_id": "browser", "duration_ms": 100})
    assert result.is_error and isinstance(result.content[0], TextContent)
    assert "capture failed" in result.content[0].text
    page.screencast.stop.assert_awaited_once()
    page.close.assert_not_called()
    assert session.page_pool.pages[0].state == "ready"


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "state, message",
    [
        ("missing", "not found"),
        ("static", "'stealthy'"),
        ("empty", "browser_fetch"),
        ("busy", "busy"),
        ("closed", "closed page"),
    ],
)
async def test_browser_observe_rejects_unavailable_sessions(state: str, message: str) -> None:
    server, session, page = _server("static" if state == "static" else "stealthy")
    if state == "missing":
        server._sessions.clear()
    elif state == "empty":
        session.page_pool.clear()
    elif state == "busy":
        session.page_pool.pages[0].mark_busy()
    elif state == "closed":
        page.is_closed.return_value = True
    async with Client(server._build_server("127.0.0.1", 8000)) as client:
        result = await client.call_tool("browser_observe", {"session_id": "browser"})
    assert result.is_error and isinstance(result.content[0], TextContent)
    assert message in result.content[0].text
    page.screencast.start.assert_not_awaited()
    if state == "closed":
        assert session.page_pool.pages_count == 0
    elif state == "busy":
        assert session.page_pool.pages[0].state == "busy"


@pytest.mark.asyncio
@pytest.mark.parametrize("cancel_mode", ["task", "scope"])
@pytest.mark.parametrize("during_start", [False, True])
async def test_browser_observe_cancellation_stops_before_releasing_page(cancel_mode: str, during_start: bool) -> None:
    server, session, page = _server()
    entered = asyncio.Event()
    stopping = asyncio.Event()
    released = asyncio.Event()
    scope = CancelScope()

    async def start(**kwargs: Any) -> None:
        entered.set()
        if during_start:
            await asyncio.Event().wait()

    async def stop() -> None:
        stopping.set()
        await released.wait()

    async def observe() -> None:
        with scope:
            await server.browser_observe("browser", duration_ms=5000)

    page.screencast.start.side_effect = start
    page.screencast.stop.side_effect = stop
    task = asyncio.create_task(observe())
    try:
        await asyncio.wait_for(entered.wait(), 5)
        assert session.page_pool.pages[0].state == "busy"
        scope.cancel() if cancel_mode == "scope" else task.cancel()
        await asyncio.wait_for(stopping.wait(), 5)
        assert session.page_pool.pages[0].state == "busy" and not task.done()
        with pytest.raises(RuntimeError, match="busy"):
            await server.browser_actions("browser", [{"type": "press_key", "key": "Enter"}])
        released.set()
        if cancel_mode == "scope":
            await asyncio.wait_for(task, 5)
            assert scope.cancelled_caught
        else:
            with pytest.raises(asyncio.CancelledError):
                await task
    finally:
        released.set()
        if not task.done():
            task.cancel()
        with suppress(asyncio.CancelledError):
            await task
    page.screencast.stop.assert_awaited_once()
    assert session.page_pool.pages[0].state == "ready"


@pytest.mark.asyncio
@pytest.mark.parametrize("cancellations", [1, 2])
async def test_browser_observe_waits_for_stop_when_task_cancelled_during_cleanup(cancellations: int) -> None:
    server, session, page = _server()
    stopping = asyncio.Event()
    released = asyncio.Event()

    async def start(**kwargs: Any) -> None:
        kwargs["on_frame"](_frame(0))

    async def stop() -> None:
        stopping.set()
        await released.wait()

    page.screencast.start.side_effect = start
    page.screencast.stop.side_effect = stop
    task = asyncio.create_task(server.browser_observe("browser", duration_ms=100))
    try:
        await asyncio.wait_for(stopping.wait(), 5)
        for _ in range(cancellations):
            task.cancel()
            await asyncio.sleep(0)
            assert not task.done() and session.page_pool.pages[0].state == "busy"
        released.set()
        with pytest.raises(asyncio.CancelledError):
            await task
    finally:
        released.set()
        if not task.done():
            task.cancel()
        with suppress(asyncio.CancelledError):
            await task
    page.screencast.stop.assert_awaited_once()
    assert session.page_pool.pages[0].state == "ready"


@pytest.mark.asyncio
async def test_browser_observe_keeps_start_error_when_cleanup_also_fails() -> None:
    server, session, page = _server()
    start_error = PatchrightError("start failed")
    stop_error = PatchrightError("stop failed")
    page.screencast.start.side_effect = start_error
    page.screencast.stop.side_effect = stop_error
    with pytest.raises(PatchrightError) as error:
        await server.browser_observe("browser", duration_ms=100)
    assert error.value is start_error and error.value.__cause__ is stop_error
    assert session.page_pool.pages[0].state == "ready"


@pytest.mark.browser
@pytest.mark.asyncio
async def test_browser_observe_live_motion_and_page_reuse() -> None:
    server = ScraplingMCPServer(executable_path=getenv("SCRAPLING_EXECUTABLE_PATH"))
    requests: list[str] = []
    html = """<!doctype html><html><head><style>
        body { margin: 0; height: 3000px; }
        #controls { position: fixed; top: 20px; left: 20px; }
        #moving { position: fixed; top: 120px; width: 80px; height: 80px; background: red;
            animation: move 1s linear infinite alternate; }
        @keyframes move { from { left: 0; } to { left: 500px; } }
        </style></head><body><div id=controls><input id=name><button id=done>Finish</button></div>
        <div id=moving></div><script>
        document.querySelector('#done').onclick = () => document.body.dataset.done = 'yes';
        </script></body></html>"""

    async def serve(route: Any) -> None:
        requests.append(route.request.url)
        await route.fulfill(content_type="text/html", body=html)

    async with Client(server._build_server("127.0.0.1", 8000)) as client:
        opened = await client.call_tool("browser_open", {"session_id": "browser"})
        assert not opened.is_error, opened.content
        try:
            session = server._sessions["browser"].session
            await session.context.route("**/*", serve)
            assert not (
                await client.call_tool(
                    "browser_fetch",
                    {"session_id": "browser", "url": "https://observe.test/start", "google_search": False},
                )
            ).is_error
            page_info = session.page_pool.pages[0]
            page = page_info.page
            await page.locator("#name").fill("Scrapling")
            await page.evaluate("scrollTo(0, 600)")
            await page.wait_for_function("scrollY === 600")
            state = "() => ({url: location.href, name: document.querySelector('#name').value, focus: document.activeElement.id, scroll: scrollY, width: innerWidth, height: innerHeight})"
            before = await page.evaluate(state)
            initial_requests = requests.copy()
            started = time() * 1000
            result = await client.call_tool(
                "browser_observe", {"session_id": "browser", "duration_ms": 600, "max_frames": 6}
            )
            ended = time() * 1000
            assert not result.is_error, result.content
            assert result.structured_content is None
            assert len(result.content) % 2 == 0 and 2 <= len(result.content) // 2 <= 6
            timestamps = []
            pixels = []
            for metadata, image in zip(result.content[::2], result.content[1::2]):
                assert isinstance(metadata, TextContent)
                frame = loads(metadata.text)
                assert set(frame) == {"timestamp_ms", "viewport_width", "viewport_height"}
                assert frame["viewport_width"] == before["width"] and frame["viewport_height"] == before["height"]
                assert isinstance(image, ImageContent) and image.mime_type == "image/jpeg"
                data = b64decode(image.data)
                assert data.startswith(b"\xff\xd8") and data.endswith(b"\xff\xd9")
                timestamps.append(frame["timestamp_ms"])
                pixels.append(data)
            assert timestamps == sorted(timestamps) and timestamps[-1] - timestamps[0] >= 200
            assert all(started - 1000 <= timestamp <= ended + 1000 for timestamp in timestamps)
            assert len(set(pixels)) > 1
            assert await page.evaluate(state) == before and requests == initial_requests
            assert session.page_pool.pages == [page_info] and page_info.state == "ready"
            actions = await client.call_tool(
                "browser_actions", {"session_id": "browser", "actions": [{"type": "click", "target": "#done"}]}
            )
            assert not actions.is_error and await page.get_attribute("body", "data-done") == "yes"
            repeated = await client.call_tool("browser_observe", {"session_id": "browser", "max_frames": 2})
            assert not repeated.is_error, repeated.content
            assert session.page_pool.pages[0] is page_info
        finally:
            assert not (await client.call_tool("close_session", {"session_id": "browser"})).is_error
