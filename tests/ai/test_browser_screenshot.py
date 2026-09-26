import asyncio
from base64 import b64decode
from contextlib import suppress
from os import getenv
from struct import unpack
from unittest.mock import AsyncMock, Mock, call

import pytest
from anyio import CancelScope
from mcp.client import Client
from mcp.types import ImageContent, TextContent
from patchright.async_api import Error as PatchrightError
from playwright.async_api import Error as PlaywrightError
from pydantic import ValidationError

from scrapling.core.ai import ScraplingMCPServer, SessionType, _SessionEntry
from scrapling.core._types import Any
from scrapling.engines._browsers._base import AsyncSession


def _server(session_type: SessionType = "dynamic") -> tuple[ScraplingMCPServer, AsyncSession, Mock]:
    server = ScraplingMCPServer()
    session = AsyncSession()
    session._is_alive = True
    page = Mock()
    page.is_closed.return_value = False
    page.url = "https://screenshot.test/current"
    page.screenshot = AsyncMock(return_value=b"captured pixels")
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
    assert set(properties) == {"session_id", "image_type", "full_page", "quality", "timeout"}
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
@pytest.mark.parametrize("session_type", ["dynamic", "stealthy"])
@pytest.mark.parametrize(
    "options",
    [
        {},
        {"image_type": "jpeg"},
        {"image_type": "jpeg", "quality": 0, "full_page": True, "timeout": 0},
        {"image_type": "jpeg", "quality": 100, "timeout": 12.5},
    ],
)
async def test_browser_screenshot_returns_native_image_without_navigation(
    session_type: SessionType, options: dict[str, Any]
) -> None:
    server, session, page = _server(session_type)

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
        ("static", "'dynamic' or 'stealthy'"),
        ("empty", "browser_fetch"),
        ("busy", "busy"),
        ("closed", "closed page"),
    ],
)
async def test_browser_screenshot_session_errors(state: str, message: str) -> None:
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
        result = await client.call_tool("browser_screenshot", {"session_id": "browser"})
    assert result.is_error and isinstance(result.content[0], TextContent)
    assert message in result.content[0].text
    page.screenshot.assert_not_awaited()
    if state == "closed":
        assert session.page_pool.pages_count == 0
    elif state == "busy":
        assert session.page_pool.pages[0].state == "busy"


@pytest.mark.asyncio
@pytest.mark.parametrize("session_type, error_type", [("dynamic", PlaywrightError), ("stealthy", PatchrightError)])
@pytest.mark.parametrize("closed", [False, True])
@pytest.mark.parametrize("through_mcp", [False, True])
async def test_browser_screenshot_native_error_releases_page_without_retry(
    session_type: SessionType, error_type: type[Exception], closed: bool, through_mcp: bool
) -> None:
    server, session, page = _server(session_type)
    native_error = error_type("capture failed")

    async def fail(**kwargs: Any) -> bytes:
        page.is_closed.return_value = closed
        raise native_error

    page.screenshot.side_effect = fail
    if through_mcp:
        async with Client(server._build_server("127.0.0.1", 8000)) as client:
            result = await client.call_tool("browser_screenshot", {"session_id": "browser"})
        assert result.is_error and isinstance(result.content[0], TextContent)
        assert "capture failed" in result.content[0].text
    else:
        with pytest.raises(error_type) as error:
            await server.browser_screenshot("browser")
        assert error.value is native_error
    page.screenshot.assert_awaited_once()
    page.close.assert_not_called()
    if closed:
        assert session.page_pool.pages_count == 0
    else:
        assert session.page_pool.pages[0].state == "ready"


@pytest.mark.asyncio
@pytest.mark.parametrize("cancel_mode", ["task", "scope"])
@pytest.mark.parametrize("closed", [False, True])
async def test_browser_screenshot_reserves_page_until_cancelled(cancel_mode: str, closed: bool) -> None:
    server, session, page = _server()
    entered = asyncio.Event()
    scope = CancelScope()

    async def pending(**kwargs: Any) -> bytes:
        entered.set()
        await asyncio.Event().wait()
        return b""

    async def capture() -> None:
        with scope:
            await server.browser_screenshot("browser")

    page.screenshot.side_effect = pending
    task = asyncio.create_task(capture())
    try:
        await asyncio.wait_for(entered.wait(), 5)
        assert session.page_pool.pages[0].state == "busy"
        with pytest.raises(RuntimeError, match="busy"):
            await server.browser_screenshot("browser")
        with pytest.raises(RuntimeError, match="busy"):
            await server.browser_actions("browser", [{"type": "press_key", "key": "Enter"}])
        page.is_closed.return_value = closed
        scope.cancel() if cancel_mode == "scope" else task.cancel()
        if cancel_mode == "scope":
            await asyncio.wait_for(task, 5)
            assert scope.cancelled_caught
        else:
            with pytest.raises(asyncio.CancelledError):
                await task
    finally:
        if not task.done():
            task.cancel()
        with suppress(asyncio.CancelledError):
            await task
    page.screenshot.assert_awaited_once()
    page.close.assert_not_called()
    if closed:
        assert session.page_pool.pages_count == 0
    else:
        assert session.page_pool.pages[0].state == "ready"


@pytest.mark.asyncio
@pytest.mark.parametrize("session_type", ["dynamic", "stealthy"])
async def test_browser_screenshot_live_preserves_actions_and_current_page(session_type: SessionType) -> None:
    server = ScraplingMCPServer(executable_path=getenv("SCRAPLING_EXECUTABLE_PATH"))
    requests: list[str] = []
    html = """<!DOCTYPE html><html><head><style>
        body { margin: 0; height: 4000px; background: linear-gradient(white, #abc); }
        #controls { position: fixed; top: 20px; left: 20px; background: white; }
        </style></head><body><div id=controls>
        <input id=name><input id=agree type=checkbox><button id=toggle>Open menu</button>
        <div id=menu hidden>Saved choices</div></div><script>
        document.querySelector('#toggle').onclick = () => {
            document.querySelector('#menu').hidden = false;
            history.pushState({}, '', '/edited');
        };
        </script></body></html>"""

    async def serve(route: Any) -> None:
        requests.append(route.request.url)
        await route.fulfill(content_type="text/html", body=html)

    async with Client(server._build_server("127.0.0.1", 8000)) as client:
        opened = await client.call_tool("browser_open", {"session_id": "browser", "session_type": session_type})
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
                        {"type": "textbox", "selector": "#name", "value": "Scrapling"},
                        {"type": "checkbox", "selector": "#agree", "value": True},
                        {"type": "click", "selector": "#toggle"},
                        {"type": "click", "selector": "#name"},
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
            heights = []
            for full_page in (False, True):
                result = await client.call_tool("browser_screenshot", {"session_id": "browser", "full_page": full_page})
                assert not result.is_error and result.structured_content is None
                assert len(result.content) == 2 and isinstance(result.content[0], ImageContent)
                assert result.content[0].mime_type == "image/png"
                assert result.content[1] == TextContent(type="text", text=before["url"])
                png = b64decode(result.content[0].data)
                assert png.startswith(b"\x89PNG\r\n\x1a\n")
                heights.append(unpack(">II", png[16:24])[1])
                assert await page.evaluate(read_state) == before
                assert requests == initial_requests
                assert session.page_pool.pages == [page_info] and page_info.state == "ready"
            assert heights[1] > heights[0]
        finally:
            assert not (await client.call_tool("close_session", {"session_id": "browser"})).is_error
