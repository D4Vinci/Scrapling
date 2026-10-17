import asyncio
from contextlib import suppress
from unittest.mock import AsyncMock, Mock

import pytest
from anyio import CancelScope
from mcp.client import Client
from mcp.types import TextContent

from scrapling.core.ai import ScraplingMCPServer
from scrapling.core._types import Any
from tests.ai.test_browser_actions import _server


@pytest.mark.asyncio
async def test_dialog_schema() -> None:
    async with Client(ScraplingMCPServer()._build_server("127.0.0.1", 8000)) as client:
        tool = next(tool for tool in (await client.list_tools()).tools if tool.name == "browser_actions")
    mapping = tool.input_schema["properties"]["actions"]["items"]["discriminator"]["mapping"]
    schema = tool.input_schema["$defs"][mapping["dialog"].rsplit("/", 1)[1]]
    assert schema["required"] == ["type", "accept"]
    assert set(schema["properties"]) == {"type", "accept", "prompt_text"}
    assert schema["properties"]["accept"]["type"] == "boolean"
    assert schema["properties"]["prompt_text"]["type"] == "string"
    assert tool.output_schema is None


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "values",
    [{}, {"accept": None}, {"accept": []}, {"accept": True, "prompt_text": None}, {"accept": True, "prompt_text": 2}],
)
async def test_invalid_dialog_prevents_entire_chain(values: dict[str, Any]) -> None:
    server, session, page = _server()
    async with Client(server._build_server("127.0.0.1", 8000)) as client:
        result = await client.call_tool(
            "browser_actions",
            {"session_id": "browser", "actions": [{"type": "press_key", "key": "Enter"}, {"type": "dialog", **values}]},
        )
    assert result.is_error
    page.on.assert_not_called()
    page.is_closed.assert_not_called()
    page.keyboard.press.assert_not_awaited()
    assert session.page_pool.pages[0].state == "ready"


@pytest.mark.asyncio
async def test_unused_dialog_is_removed_without_waiting() -> None:
    server, session, page = _server()
    async with Client(server._build_server("127.0.0.1", 8000)) as client:
        result = await client.call_tool(
            "browser_actions", {"session_id": "browser", "actions": [{"type": "dialog", "accept": True}]}
        )
    assert not result.is_error
    assert result.content == [TextContent(type="text", text="Actions completed.")]
    page.on.assert_called_once()
    page.remove_listener.assert_called_once_with(*page.on.call_args.args)
    assert session.page_pool.pages[0].state == "ready"


@pytest.mark.asyncio
@pytest.mark.parametrize("accept", [True, False])
@pytest.mark.parametrize("trigger", ["click", "press_key"])
@pytest.mark.parametrize("blocked", [False, True])
async def test_dialog_failure_stops_blocked_action_and_reaches_mcp(accept: bool, trigger: str, blocked: bool) -> None:
    server, session, page = _server()
    dialog = Mock(accept=AsyncMock(), dismiss=AsyncMock())
    method = dialog.accept if accept else dialog.dismiss
    method.side_effect = RuntimeError("reply failed")
    page.mouse.up = AsyncMock()

    async def open_dialog(*args: Any, **kwargs: Any) -> None:
        page.on.call_args.args[1](dialog)
        if blocked:
            await asyncio.Event().wait()

    native = page.keyboard.press if trigger == "press_key" else page.locator.return_value.click
    if trigger == "click":
        page.locator.return_value.click = native = AsyncMock()
    native.side_effect = open_dialog
    action = {"type": "press_key", "key": "Enter"} if trigger == "press_key" else {"type": "click", "target": "button"}
    async with Client(server._build_server("127.0.0.1", 8000)) as client:
        result = await asyncio.wait_for(
            client.call_tool(
                "browser_actions",
                {
                    "session_id": "browser",
                    "actions": [{"type": "dialog", "accept": accept}, action, {"type": "wheel", "delta_y": 1}],
                },
            ),
            5,
        )
    assert result.is_error
    assert "Action 1 (dialog) failed: reply failed" in str(result.content)
    method.assert_awaited_once()
    page.remove_listener.assert_called_once_with(*page.on.call_args.args)
    page.mouse.wheel.assert_not_awaited()
    assert page.mouse.up.await_count == (1 if trigger == "click" and blocked else 0)
    assert session.page_pool.pages[0].state == "ready"


@pytest.mark.asyncio
@pytest.mark.parametrize("cancel_mode", ["task", "scope"])
@pytest.mark.parametrize("blocked", [False, True])
async def test_cancellation_waits_for_active_reply_before_releasing_page(cancel_mode: str, blocked: bool) -> None:
    server, session, page = _server()
    entered, release, cancelled = asyncio.Event(), asyncio.Event(), asyncio.Event()
    scope = CancelScope()
    dialog = Mock(accept=AsyncMock(), dismiss=AsyncMock())

    async def accept(**kwargs: Any) -> None:
        entered.set()
        await release.wait()

    async def open_dialog(key: str) -> None:
        page.on.call_args.args[1](dialog)
        try:
            if blocked:
                await asyncio.Event().wait()
        finally:
            cancelled.set()

    async def run() -> None:
        with scope:
            await server.browser_actions(
                "browser",
                [
                    {"type": "dialog", "accept": True},
                    {"type": "press_key", "key": "Enter"},
                    {"type": "wheel", "delta_y": 1},
                ],
            )

    dialog.accept.side_effect = accept
    page.keyboard.press.side_effect = open_dialog
    task = asyncio.create_task(run())
    try:
        await asyncio.wait_for(entered.wait(), 5)
        scope.cancel() if cancel_mode == "scope" else task.cancel()
        await asyncio.wait_for(cancelled.wait(), 5)
        assert session.page_pool.pages[0].state == "busy"
        assert not task.done()
        release.set()
        if cancel_mode == "task":
            with pytest.raises(asyncio.CancelledError):
                await asyncio.wait_for(task, 5)
        else:
            await asyncio.wait_for(task, 5)
            assert scope.cancelled_caught
    finally:
        release.set()
        if not task.done():
            task.cancel()
        with suppress(asyncio.CancelledError):
            await task
    dialog.accept.assert_awaited_once_with(prompt_text=None)
    page.remove_listener.assert_called_once_with(*page.on.call_args.args)
    page.mouse.wheel.assert_not_awaited()
    assert session.page_pool.pages[0].state == "ready"
