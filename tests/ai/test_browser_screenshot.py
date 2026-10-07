import asyncio
from base64 import b64decode
from contextlib import suppress
from os import getenv
from re import search
from struct import unpack
from time import monotonic
from unittest.mock import AsyncMock, Mock, call

import pytest
from anyio import CancelScope
from mcp.client import Client
from mcp.types import ImageContent, TextContent
from patchright.async_api import Error as PatchrightError
from pydantic import ValidationError

from scrapling.core.ai import ScraplingMCPServer, SessionType
from scrapling.core.ai.server import _SessionEntry
from scrapling.core._types import Any
from scrapling.engines._browsers._base import AsyncSession


def _server(session_type: SessionType = "stealthy") -> tuple[ScraplingMCPServer, AsyncSession, Mock]:
    server = ScraplingMCPServer()
    session = AsyncSession()
    session._is_alive = True
    page = Mock()
    page.is_closed.return_value = False
    page.url = "https://screenshot.test/current"
    page.screenshot = AsyncMock(return_value=b"captured pixels")
    page.locator.return_value.element_handle = AsyncMock()
    page.locator.return_value.element_handle.return_value.screenshot = AsyncMock(return_value=b"captured pixels")
    page.locator.return_value.element_handle.return_value.dispose = AsyncMock()
    session.page_pool.add_page(page).mark_ready()
    server._sessions["browser"] = _SessionEntry(session, session_type)
    return server, session, page


@pytest.mark.asyncio
async def test_browser_screenshot_schema() -> None:
    async with Client(ScraplingMCPServer()._build_server("127.0.0.1", 8000)) as client:
        tool = next(tool for tool in (await client.list_tools()).tools if tool.name == "browser_screenshot")
    schema = tool.input_schema
    assert schema["required"] == ["session_id"]
    properties = schema["properties"]
    assert set(properties) == {"session_id", "image_type", "full_page", "quality", "timeout", "selector", "ref"}
    for target in ("selector", "ref"):
        assert properties[target]["default"] is None
        assert {"type": "null"} in properties[target]["anyOf"]
        assert {"type": "string", "minLength": 1} in properties[target]["anyOf"]
    assert properties["image_type"]["default"] == "png"
    assert properties["image_type"]["enum"] == ["png", "jpeg"]
    assert properties["full_page"]["default"] is False
    assert properties["quality"]["default"] is None
    assert {"type": "integer", "minimum": 0, "maximum": 100} in properties["quality"]["anyOf"]
    assert {"type": "null"} in properties["quality"]["anyOf"]
    assert properties["timeout"]["default"] == 30000
    assert properties["timeout"]["minimum"] == 0
    assert tool.output_schema is None
    assert tool.annotations is not None
    assert tool.annotations.read_only_hint is True
    assert tool.annotations.open_world_hint is True


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "options",
    [
        {},
        {"image_type": "jpeg"},
        {"image_type": "jpeg", "quality": 0, "full_page": True, "timeout": 0},
        {"image_type": "jpeg", "quality": 100, "timeout": 12.5},
    ],
)
async def test_browser_screenshot_returns_native_image_without_navigation(options: dict[str, Any]) -> None:
    server, session, page = _server()

    async def capture(**kwargs: Any) -> bytes:
        assert session.page_pool.pages[0].state == "busy"
        return b"captured pixels"

    page.screenshot.side_effect = capture
    async with Client(server._build_server("127.0.0.1", 8000)) as client:
        result = await client.call_tool("browser_screenshot", {"session_id": "browser", **options})
    assert not result.is_error and result.structured_content is None
    assert len(result.content) == 2
    image, url = result.content
    assert isinstance(image, ImageContent)
    assert b64decode(image.data) == b"captured pixels"
    assert image.mime_type == f"image/{options.get('image_type', 'png')}"
    assert url == TextContent(type="text", text=page.url)
    assert page.mock_calls == [
        call.is_closed(),
        call.screenshot(
            type=options.get("image_type", "png"),
            full_page=options.get("full_page", False),
            quality=options.get("quality"),
            timeout=options.get("timeout", 30000),
        ),
        call.is_closed(),
    ]
    assert session.page_pool.pages[0].state == "ready"


@pytest.mark.asyncio
@pytest.mark.parametrize("target", [{"selector": "#card", "ref": None}, {"selector": None, "ref": "e2"}])
@pytest.mark.parametrize("options", [{}, {"image_type": "jpeg", "quality": 70, "timeout": 250}])
async def test_browser_screenshot_forwards_element_target_without_full_page(
    target: dict[str, Any], options: dict[str, Any], monkeypatch: pytest.MonkeyPatch
) -> None:
    server, session, page = _server()
    monkeypatch.setattr("scrapling.core.ai.server.monotonic", lambda: 10)

    async def capture(**kwargs: Any) -> bytes:
        assert session.page_pool.pages[0].state == "busy"
        return b"captured pixels"

    page.locator.return_value.element_handle.return_value.screenshot.side_effect = capture
    async with Client(server._build_server("127.0.0.1", 8000)) as client:
        result = await client.call_tool("browser_screenshot", {"session_id": "browser", **target, **options})
    assert not result.is_error and result.structured_content is None
    assert len(result.content) == 2 and isinstance(result.content[0], ImageContent)
    assert b64decode(result.content[0].data) == b"captured pixels"
    assert result.content[0].mime_type == f"image/{options.get('image_type', 'png')}"
    assert result.content[1] == TextContent(type="text", text=page.url)
    assert page.mock_calls == [
        call.is_closed(),
        call.locator(target.get("selector") or "aria-ref=e2"),
        call.locator().element_handle(timeout=options.get("timeout", 30000)),
        call.locator()
        .element_handle()
        .screenshot(
            type=options.get("image_type", "png"), quality=options.get("quality"), timeout=options.get("timeout", 30000)
        ),
        call.locator().element_handle().dispose(),
        call.is_closed(),
    ]
    page.screenshot.assert_not_awaited()
    assert session.page_pool.pages[0].state == "ready"


@pytest.mark.asyncio
@pytest.mark.parametrize("timeout, elapsed, remaining", [(1000, 0.25, 750), (100, 0.1, 1), (100, 0.2, 1), (0, 100, 0)])
async def test_browser_screenshot_element_resolution_uses_capture_budget(
    timeout: float, elapsed: float, remaining: float, monkeypatch: pytest.MonkeyPatch
) -> None:
    server, session, page = _server()
    monkeypatch.setattr("scrapling.core.ai.server.monotonic", Mock(side_effect=[10, 10 + elapsed]))
    await server.browser_screenshot("browser", selector="#card", timeout=timeout)
    locator = page.locator.return_value
    locator.element_handle.assert_awaited_once_with(timeout=timeout)
    locator.element_handle.return_value.screenshot.assert_awaited_once_with(type="png", quality=None, timeout=remaining)
    locator.element_handle.return_value.dispose.assert_awaited_once()
    page.screenshot.assert_not_awaited()
    page.set_default_timeout.assert_not_called()
    assert session.page_pool.pages[0].state == "ready"


@pytest.mark.asyncio
async def test_browser_screenshot_element_resolution_failure_does_not_capture_or_retry() -> None:
    server, session, page = _server()
    native_error = PatchrightError("element resolution failed")
    locator = page.locator.return_value
    locator.element_handle.side_effect = native_error
    with pytest.raises(PatchrightError) as error:
        await server.browser_screenshot("browser", ref="e2", timeout=100)
    assert error.value is native_error
    locator.element_handle.assert_awaited_once_with(timeout=100)
    locator.element_handle.return_value.screenshot.assert_not_awaited()
    locator.element_handle.return_value.dispose.assert_not_awaited()
    page.screenshot.assert_not_awaited()
    assert session.page_pool.pages[0].state == "ready"


@pytest.mark.asyncio
@pytest.mark.parametrize("outcome", ["success", "error", "cancel"])
async def test_browser_screenshot_disposal_failure_preserves_capture_error_or_cancellation(outcome: str) -> None:
    server, session, page = _server()
    element = page.locator.return_value.element_handle.return_value
    native_error = PatchrightError("capture failed")
    cleanup_error = PatchrightError("dispose failed")
    entered = asyncio.Event()
    release = asyncio.Event()

    async def capture(**kwargs: Any) -> bytes:
        entered.set()
        await release.wait()
        if outcome == "error":
            raise native_error
        return b"captured pixels"

    async def screenshot() -> None:
        with pytest.raises(asyncio.CancelledError if outcome == "cancel" else PatchrightError) as error:
            await server.browser_screenshot("browser", selector="#card")
        if outcome == "success":
            assert error.value is cleanup_error
        else:
            if outcome == "error":
                assert error.value is native_error
            assert error.value.__cause__ is cleanup_error
        raise error.value

    element.screenshot.side_effect = capture
    element.dispose.side_effect = cleanup_error
    task = asyncio.create_task(screenshot())
    try:
        await asyncio.wait_for(entered.wait(), 5)
        task.cancel() if outcome == "cancel" else release.set()
        with pytest.raises(asyncio.CancelledError if outcome == "cancel" else PatchrightError):
            await task
    finally:
        if not task.done():
            task.cancel()
        with suppress(Exception, asyncio.CancelledError):
            await task
    page.locator.return_value.element_handle.assert_awaited_once()
    element.screenshot.assert_awaited_once()
    element.dispose.assert_awaited_once()
    assert session.page_pool.pages[0].state == "ready"


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "options",
    [{"selector": "#card", "ref": "e2"}, {"selector": "#card", "full_page": True}, {"ref": "e2", "full_page": True}],
)
async def test_browser_screenshot_conflicting_targets_do_not_reserve_page(options: dict[str, Any]) -> None:
    server, session, page = _server()
    with pytest.raises(ValueError):
        await server.browser_screenshot("browser", **options)
    async with Client(server._build_server("127.0.0.1", 8000)) as client:
        result = await client.call_tool("browser_screenshot", {"session_id": "browser", **options})
    assert result.is_error
    page.is_closed.assert_not_called()
    page.locator.assert_not_called()
    page.screenshot.assert_not_awaited()
    assert session.page_pool.pages[0].state == "ready"


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "options",
    [
        {"image_type": "gif"},
        {"quality": -1},
        {"quality": 101},
        {"quality": 1.5},
        {"quality": "invalid"},
        {"timeout": -1},
        {"timeout": "NaN"},
        {"timeout": "Infinity"},
        {"selector": ""},
        {"ref": ""},
    ],
)
async def test_browser_screenshot_invalid_input_does_not_reserve_page(options: dict[str, Any]) -> None:
    server, session, page = _server()
    async with Client(server._build_server("127.0.0.1", 8000)) as client:
        result = await client.call_tool(
            "browser_screenshot", {"session_id": "browser", "image_type": "jpeg", **options}
        )
    assert result.is_error
    page.is_closed.assert_not_called()
    page.screenshot.assert_not_awaited()
    assert session.page_pool.pages[0].state == "ready"


@pytest.mark.parametrize("value", [float("nan"), float("inf"), float("-inf")])
def test_browser_screenshot_schema_rejects_nonfinite_timeout(value: float) -> None:
    tool = ScraplingMCPServer()._build_server("127.0.0.1", 8000)._tool_manager.get_tool("browser_screenshot")
    assert tool is not None
    with pytest.raises(ValidationError):
        tool.fn_metadata.arg_model.model_validate({"session_id": "browser", "timeout": value})


@pytest.mark.asyncio
@pytest.mark.parametrize("quality", [0, 90])
async def test_browser_screenshot_png_quality_does_not_reserve_page(quality: int) -> None:
    server, session, page = _server()
    with pytest.raises(ValueError, match="quality"):
        await server.browser_screenshot("browser", quality=quality)
    async with Client(server._build_server("127.0.0.1", 8000)) as client:
        result = await client.call_tool("browser_screenshot", {"session_id": "browser", "quality": quality})
    assert result.is_error
    page.is_closed.assert_not_called()
    page.screenshot.assert_not_awaited()
    assert session.page_pool.pages[0].state == "ready"


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "state, message",
    [
        ("missing", "not found"),
        ("dead", "no longer alive"),
        ("static", "'stealthy'"),
        ("empty", "browser_fetch"),
        ("busy", "busy"),
        ("closed", "closed page"),
    ],
)
async def test_browser_screenshot_session_errors(state: str, message: str) -> None:
    server, session, page = _server("static" if state == "static" else "stealthy")
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
        result = await client.call_tool("browser_screenshot", {"session_id": "browser"})
    assert result.is_error and isinstance(result.content[0], TextContent)
    assert message in result.content[0].text
    page.screenshot.assert_not_awaited()
    if state == "closed":
        assert session.page_pool.pages_count == 0
    elif state == "busy":
        assert session.page_pool.pages[0].state == "busy"


@pytest.mark.asyncio
@pytest.mark.parametrize("closed", [False, True])
@pytest.mark.parametrize("through_mcp", [False, True])
@pytest.mark.parametrize("target", [{}, {"selector": "#card"}, {"ref": "e2"}])
async def test_browser_screenshot_native_error_releases_page_without_retry(
    closed: bool, through_mcp: bool, target: dict[str, str]
) -> None:
    server, session, page = _server()
    native_error = PatchrightError("capture failed")

    async def fail(**kwargs: Any) -> bytes:
        page.is_closed.return_value = closed
        raise native_error

    capture = page.locator.return_value.element_handle.return_value.screenshot if target else page.screenshot
    capture.side_effect = fail
    if through_mcp:
        async with Client(server._build_server("127.0.0.1", 8000)) as client:
            result = await client.call_tool("browser_screenshot", {"session_id": "browser", **target})
        assert result.is_error and isinstance(result.content[0], TextContent)
        assert "capture failed" in result.content[0].text
    else:
        with pytest.raises(PatchrightError) as error:
            await server.browser_screenshot("browser", **target)
        assert error.value is native_error
    capture.assert_awaited_once()
    if target:
        page.locator.return_value.element_handle.assert_awaited_once()
        page.locator.return_value.element_handle.return_value.dispose.assert_awaited_once()
        page.screenshot.assert_not_awaited()
    page.close.assert_not_called()
    if closed:
        assert session.page_pool.pages_count == 0
    else:
        assert session.page_pool.pages[0].state == "ready"


@pytest.mark.asyncio
@pytest.mark.parametrize("cancel_mode", ["task", "scope"])
@pytest.mark.parametrize("closed", [False, True])
@pytest.mark.parametrize("target", [{}, {"selector": "#card"}, {"ref": "e2"}])
async def test_browser_screenshot_reserves_page_until_cancelled(
    cancel_mode: str, closed: bool, target: dict[str, str]
) -> None:
    server, session, page = _server()
    entered = asyncio.Event()
    disposing = asyncio.Event()
    released = asyncio.Event()
    scope = CancelScope()

    async def pending(**kwargs: Any) -> bytes:
        entered.set()
        await asyncio.Event().wait()
        return b""

    async def dispose() -> None:
        disposing.set()
        await released.wait()

    async def capture() -> None:
        with scope:
            await server.browser_screenshot("browser", **target)

    screenshot = page.locator.return_value.element_handle.return_value.screenshot if target else page.screenshot
    screenshot.side_effect = pending
    page.locator.return_value.element_handle.return_value.dispose.side_effect = dispose
    task = asyncio.create_task(capture())
    try:
        await asyncio.wait_for(entered.wait(), 5)
        assert session.page_pool.pages[0].state == "busy"
        with pytest.raises(RuntimeError, match="busy"):
            await server.browser_screenshot("browser", **target)
        with pytest.raises(RuntimeError, match="busy"):
            await server.browser_actions("browser", [{"type": "press_key", "key": "Enter"}])
        page.is_closed.return_value = closed
        scope.cancel() if cancel_mode == "scope" else task.cancel()
        if target:
            await asyncio.wait_for(disposing.wait(), 5)
            assert session.page_pool.pages[0].state == "busy"
            assert not task.done()
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
    screenshot.assert_awaited_once()
    if target:
        page.locator.return_value.element_handle.assert_awaited_once()
        page.locator.return_value.element_handle.return_value.dispose.assert_awaited_once()
        page.screenshot.assert_not_awaited()
    page.close.assert_not_called()
    if closed:
        assert session.page_pool.pages_count == 0
    else:
        assert session.page_pool.pages[0].state == "ready"


@pytest.mark.asyncio
async def test_browser_screenshot_live_preserves_actions_and_current_page() -> None:
    server = ScraplingMCPServer(executable_path=getenv("SCRAPLING_EXECUTABLE_PATH"))
    requests: list[str] = []
    html = """<!DOCTYPE html><html><head><style>
        body { margin: 0; height: 4000px; background: linear-gradient(white, #abc); }
        #controls { position: fixed; top: 20px; left: 20px; background: white; }
        #toggle { width: 120px; height: 40px; box-sizing: border-box; }
        #below { position: absolute; top: 3000px; left: 20px; width: 100px; height: 50px; box-sizing: border-box; }
        </style></head><body><div id=controls>
        <input id=name><input id=agree type=checkbox><button id=toggle>Open menu</button>
        <div id=menu hidden>Saved choices</div></div><button id=below>Below</button><script>
        document.querySelector('#toggle').onclick = () => {
            document.querySelector('#menu').hidden = false;
            history.pushState({}, '', '/edited');
        };
        </script></body></html>"""

    async def serve(route: Any) -> None:
        requests.append(route.request.url)
        await route.fulfill(content_type="text/html", body=html)

    async with Client(server._build_server("127.0.0.1", 8000)) as client:
        opened = await client.call_tool("browser_open", {"session_id": "browser"})
        assert not opened.is_error
        try:
            session = server._sessions["browser"].session
            await session.context.route("**/*", serve)
            fetched = await client.call_tool(
                "browser_fetch",
                {"session_id": "browser", "url": "https://screenshot.test/start", "google_search": False},
            )
            assert not fetched.is_error
            page_info = session.page_pool.pages[0]
            page = page_info.page
            actions = await client.call_tool(
                "browser_actions",
                {
                    "session_id": "browser",
                    "actions": [
                        {"type": "textbox", "target": "#name", "value": "Scrapling"},
                        {"type": "checkbox", "target": "#agree", "value": True},
                        {"type": "click", "target": "#toggle"},
                        {"type": "click", "target": "#name"},
                        {"type": "move", "x": 400, "y": 300},
                        {"type": "wheel", "delta_y": 600},
                    ],
                },
            )
            assert not actions.is_error
            await page.wait_for_function("scrollY === 600")
            read_state = """() => ({url: location.href, name: document.querySelector('#name').value,
                checked: document.querySelector('#agree').checked, menu: !document.querySelector('#menu').hidden,
                focus: document.activeElement.id, x: scrollX, y: scrollY})"""
            before = await page.evaluate(read_state)
            assert before == {
                "url": "https://screenshot.test/edited",
                "name": "Scrapling",
                "checked": True,
                "menu": True,
                "focus": "name",
                "x": 0,
                "y": 600,
            }
            initial_requests = requests.copy()
            assert initial_requests == ["https://screenshot.test/start"]
            pixel_ratio = await page.evaluate("devicePixelRatio")
            dimensions = []
            for full_page in (False, True):
                result = await client.call_tool("browser_screenshot", {"session_id": "browser", "full_page": full_page})
                assert not result.is_error and result.structured_content is None
                assert len(result.content) == 2 and isinstance(result.content[0], ImageContent)
                assert result.content[0].mime_type == "image/png"
                assert result.content[1] == TextContent(type="text", text=before["url"])
                png = b64decode(result.content[0].data)
                assert png.startswith(b"\x89PNG\r\n\x1a\n")
                dimensions.append(unpack(">II", png[16:24]))
                assert await page.evaluate(read_state) == before
                assert requests == initial_requests
                assert session.page_pool.pages == [page_info] and page_info.state == "ready"
            assert dimensions[1][1] > dimensions[0][1]
            snapshot = await server.browser_extract("browser")
            ref = search(r'button "Open menu".*?\[ref=([^\]]+)\]', snapshot)
            assert ref is not None
            for target in ({"selector": "#toggle"}, {"ref": ref[1]}):
                result = await client.call_tool("browser_screenshot", {"session_id": "browser", **target})
                assert not result.is_error and result.structured_content is None
                assert isinstance(result.content[0], ImageContent)
                assert result.content[1] == TextContent(type="text", text=before["url"])
                size = unpack(">II", b64decode(result.content[0].data)[16:24])
                assert size == (round(120 * pixel_ratio), round(40 * pixel_ratio))
                box = await page.locator("#toggle").bounding_box()
                assert box is not None and size == (
                    round(box["width"] * pixel_ratio),
                    round(box["height"] * pixel_ratio),
                )
                assert size[0] < dimensions[0][0] and size[1] < dimensions[0][1]
                assert await page.evaluate(read_state) == before
                assert requests == initial_requests
            result = await client.call_tool("browser_screenshot", {"session_id": "browser", "selector": "#below"})
            assert not result.is_error and isinstance(result.content[0], ImageContent)
            assert unpack(">II", b64decode(result.content[0].data)[16:24]) == (
                round(100 * pixel_ratio),
                round(50 * pixel_ratio),
            )
            scrolled = await page.evaluate(read_state)
            assert scrolled["y"] > before["y"]
            assert {**scrolled, "y": before["y"]} == before
            assert requests == initial_requests
            await page.locator("#toggle").evaluate("element => element.remove()")
            for target, message in (
                ({"selector": "input"}, "strict mode violation"),
                ({"selector": "#missing"}, "Timeout"),
                ({"ref": ref[1]}, "Timeout"),
            ):
                started = monotonic()
                result = await client.call_tool(
                    "browser_screenshot", {"session_id": "browser", "timeout": 100, **target}
                )
                assert monotonic() - started < 2
                assert result.is_error and isinstance(result.content[0], TextContent)
                assert message in result.content[0].text
                assert await page.evaluate(read_state) == scrolled
                assert requests == initial_requests
                assert session.page_pool.pages == [page_info] and page_info.state == "ready"
        finally:
            assert not (await client.call_tool("close_session", {"session_id": "browser"})).is_error
