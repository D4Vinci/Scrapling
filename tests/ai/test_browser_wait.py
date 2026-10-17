import asyncio
from contextlib import asynccontextmanager
from os import getenv
from time import monotonic
from unittest.mock import AsyncMock, Mock, call

import pytest
from anyio import CancelScope
from mcp.client import Client
from mcp.types import TextContent
from patchright.async_api import TimeoutError as PatchrightTimeoutError

from scrapling.core.ai import ScraplingMCPServer, SessionType
from scrapling.core.ai.server import _SessionEntry
from scrapling.core._types import Any, AsyncGenerator
from scrapling.engines._browsers._base import AsyncSession


def _server(session_type: SessionType = "stealthy") -> tuple[ScraplingMCPServer, AsyncSession, Mock]:
    server = ScraplingMCPServer()
    session = AsyncSession()
    session._is_alive = True
    page = Mock()
    page.is_closed.return_value = False
    page.wait_for_timeout = AsyncMock()
    page.wait_for_load_state = AsyncMock()
    page.locator.return_value.wait_for = AsyncMock()
    session.page_pool.add_page(page).mark_ready()
    server._sessions["browser"] = _SessionEntry(session, session_type)
    return server, session, page


@pytest.mark.asyncio
async def test_browser_wait_schema_and_annotations() -> None:
    async with Client(ScraplingMCPServer()._build_server("127.0.0.1", 8000)) as client:
        tool = next(tool for tool in (await client.list_tools()).tools if tool.name == "browser_actions")
    assert tool.title == "Browser actions"
    assert tool.input_schema["required"] == ["session_id", "actions"]
    properties = tool.input_schema["properties"]
    assert set(properties) == {"session_id", "actions", "slowly"}
    actions = properties["actions"]
    assert actions["type"] == "array" and actions["minItems"] == 1
    items = actions["items"]
    assert items["discriminator"]["propertyName"] == "type"
    variants = {
        kind: tool.input_schema["$defs"][ref.rsplit("/", 1)[1]]
        for kind, ref in items["discriminator"]["mapping"].items()
    }
    assert set(variants) == {
        "move",
        "click",
        "wheel",
        "wait_time",
        "wait_element",
        "wait_load",
        "textbox",
        "checkbox",
        "radio",
        "combobox",
        "press_key",
        "dialog",
    }
    assert len(items["oneOf"]) == 12
    assert variants["wait_time"]["required"] == ["type", "milliseconds"]
    assert variants["wait_time"]["properties"]["milliseconds"]["minimum"] == 0
    assert variants["wait_element"]["required"] == ["type", "target"]
    assert variants["wait_element"]["properties"]["target"]["minLength"] == 1
    assert set(variants["wait_element"]["properties"]["state"]["enum"]) == {"attached", "detached", "visible", "hidden"}
    assert variants["wait_element"]["properties"]["state"]["default"] == "visible"
    assert variants["wait_load"]["required"] == ["type", "state"]
    assert set(variants["wait_load"]["properties"]["state"]["enum"]) == {"domcontentloaded", "load", "networkidle"}
    for kind in ("wait_element", "wait_load"):
        assert variants[kind]["properties"]["timeout"]["minimum"] == 0
        assert variants[kind]["properties"]["timeout"]["default"] == 30000
    assert tool.output_schema is None
    assert tool.annotations is not None
    assert tool.annotations.read_only_hint is False
    assert tool.annotations.destructive_hint is True
    assert tool.annotations.idempotent_hint is False
    assert tool.annotations.open_world_hint is True


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "values, method, args, kwargs",
    [
        ({"type": "wait_time", "milliseconds": 0}, "wait_for_timeout", (0,), {}),
        ({"type": "wait_time", "milliseconds": 12.5}, "wait_for_timeout", (12.5,), {}),
        ({"type": "wait_element", "target": "#ready"}, "locator", (), {"state": "visible", "timeout": 30000}),
        *[
            (
                {"type": "wait_element", "target": "#ready", "state": state, "timeout": 0},
                "locator",
                (),
                {"state": state, "timeout": 0},
            )
            for state in ("attached", "detached", "visible", "hidden")
        ],
        *[
            ({"type": "wait_load", "state": state, "timeout": 12.5}, "wait_for_load_state", (state,), {"timeout": 12.5})
            for state in ("domcontentloaded", "load", "networkidle")
        ],
    ],
)
async def test_browser_wait_forwards_only_requested_wait(
    values: dict[str, Any], method: str, args: tuple, kwargs: dict[str, Any]
) -> None:
    server, session, page = _server()
    async with Client(server._build_server("127.0.0.1", 8000)) as client:
        result = await client.call_tool("browser_actions", {"session_id": "browser", "actions": [values]})
    assert not result.is_error and result.structured_content is None
    assert result.content == [TextContent(type="text", text="Actions completed.")]
    for name in ("wait_for_timeout", "wait_for_load_state", "locator"):
        action = page.locator.return_value.wait_for if name == "locator" else getattr(page, name)
        if name == method:
            action.assert_awaited_once_with(*args, **kwargs)
        else:
            action.assert_not_awaited()
    if method == "locator":
        page.locator.assert_called_once_with("#ready")
        page.locator.return_value.first.wait_for.assert_not_called()
    else:
        page.locator.assert_not_called()
    for name in ("goto", "reload", "evaluate", "aria_snapshot", "screenshot", "set_default_timeout"):
        getattr(page, name).assert_not_called()
    assert session.page_pool.pages[0].state == "ready"


@pytest.mark.asyncio
async def test_browser_wait_mixed_chain_keeps_order_and_page_reservation() -> None:
    server, session, page = _server()
    waited = Mock()
    for name, method in (
        ("time", page.wait_for_timeout),
        ("element", page.locator.return_value.wait_for),
        ("load", page.wait_for_load_state),
    ):
        waited.attach_mock(method, name)

        async def assert_reserved(*args: Any, **kwargs: Any) -> None:
            assert session.page_pool.pages[0].state == "busy"

        method.side_effect = assert_reserved
    async with Client(server._build_server("127.0.0.1", 8000)) as client:
        result = await client.call_tool(
            "browser_actions",
            {
                "session_id": "browser",
                "actions": [
                    {"type": "wait_load", "state": "domcontentloaded"},
                    {"type": "wait_element", "target": "#ready", "timeout": 15},
                    {"type": "wait_time", "milliseconds": 2.5},
                    {"type": "wait_element", "target": "#ready", "state": "hidden", "timeout": 0},
                ],
            },
        )
    assert not result.is_error
    assert waited.mock_calls == [
        call.load("domcontentloaded", timeout=30000),
        call.element(state="visible", timeout=15),
        call.time(2.5),
        call.element(state="hidden", timeout=0),
    ]
    assert page.is_closed.call_count == 2
    assert session.page_pool.pages[0].state == "ready"


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "actions",
    [
        None,
        [],
        {},
        "load",
        [None],
        [{}],
        [{"type": "unknown"}],
        *[
            [{"type": "wait_time", "milliseconds": 0}, invalid]
            for invalid in (
                {"type": "wait_time"},
                {"type": "wait_time", "milliseconds": -1},
                {"type": "wait_time", "milliseconds": "NaN"},
                {"type": "wait_time", "milliseconds": "Infinity"},
                {"type": "wait_element"},
                {"type": "wait_element", "target": ""},
                {"type": "wait_element", "target": None},
                {"type": "wait_element", "target": 123},
                {"type": "wait_element", "selector": "#ready"},
                {"type": "wait_element", "ref": "e2"},
                {"type": "wait_element", "target": "#ready", "state": "missing"},
                {"type": "wait_load"},
                {"type": "wait_load", "state": "commit"},
                {"type": "wait_load", "state": "load", "timeout": -1},
                {"type": "wait_load", "state": "load", "timeout": "NaN"},
                {"type": "wait_element", "target": "#ready", "timeout": "Infinity"},
            )
        ],
    ],
)
async def test_browser_wait_invalid_batch_does_not_start_or_reserve_page(actions: Any) -> None:
    server, session, page = _server()
    async with Client(server._build_server("127.0.0.1", 8000)) as client:
        result = await client.call_tool("browser_actions", {"session_id": "browser", "actions": actions})
    assert result.is_error
    page.is_closed.assert_not_called()
    page.wait_for_timeout.assert_not_awaited()
    page.wait_for_load_state.assert_not_awaited()
    page.locator.assert_not_called()
    assert session.page_pool.pages[0].state == "ready"


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "values", [{"type": "wait_element", "target": "#missing"}, {"type": "wait_load", "state": "networkidle"}]
)
async def test_browser_wait_native_timeout_reaches_mcp_and_releases_page(values: dict[str, Any]) -> None:
    server, session, page = _server()
    action = page.locator.return_value.wait_for if values["type"] == "wait_element" else page.wait_for_load_state
    action.side_effect = PatchrightTimeoutError("wait timed out")
    async with Client(server._build_server("127.0.0.1", 8000)) as client:
        result = await client.call_tool(
            "browser_actions",
            {
                "session_id": "browser",
                "actions": [{"type": "wait_time", "milliseconds": 1}, values, {"type": "wait_time", "milliseconds": 2}],
            },
        )
        assert result.is_error and isinstance(result.content[0], TextContent)
        assert f"Action 2 ({values['type']}) failed: wait timed out" in result.content[0].text
        assert page.wait_for_timeout.await_args_list == [call(1)]
        assert session.page_pool.pages[0].state == "ready"
        assert not (
            await client.call_tool(
                "browser_actions", {"session_id": "browser", "actions": [{"type": "wait_time", "milliseconds": 0}]}
            )
        ).is_error
    assert action.await_count == 1
    with pytest.raises(RuntimeError, match=r"Action 1 .* failed: wait timed out") as failed:
        await server.browser_actions("browser", [values])
    assert isinstance(failed.value.__cause__, PatchrightTimeoutError)
    assert session.page_pool.pages[0].state == "ready"


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "state, message",
    [
        ("missing", "not found"),
        ("static", "'stealthy'"),
        ("dead", "no longer alive"),
        ("empty", "browser_fetch"),
        ("closed", "closed page"),
    ],
)
async def test_browser_wait_session_errors(state: str, message: str) -> None:
    server, session, page = _server("static" if state == "static" else "stealthy")
    if state == "missing":
        server._sessions.clear()
    elif state == "dead":
        session._is_alive = False
    elif state == "empty":
        session.page_pool.clear()
    elif state == "closed":
        page.is_closed.return_value = True
    async with Client(server._build_server("127.0.0.1", 8000)) as client:
        result = await client.call_tool(
            "browser_actions", {"session_id": "browser", "actions": [{"type": "wait_time", "milliseconds": 0}]}
        )
    assert result.is_error and isinstance(result.content[0], TextContent)
    assert message in result.content[0].text
    page.wait_for_timeout.assert_not_awaited()
    if state == "closed":
        assert not session.page_pool.pages


@pytest.mark.asyncio
@pytest.mark.parametrize("cancel_mode", ["task", "scope"])
async def test_browser_wait_reserves_page_until_cancelled(cancel_mode: str) -> None:
    server, session, page = _server()
    entered = asyncio.Event()
    scope = CancelScope()

    async def pending(*args: Any, **kwargs: Any) -> None:
        entered.set()
        await asyncio.Event().wait()

    async def wait() -> None:
        with scope:
            await server.browser_actions(
                "browser",
                [
                    {"type": "wait_time", "milliseconds": 1},
                    {"type": "wait_load", "state": "networkidle", "timeout": 0},
                    {"type": "wait_time", "milliseconds": 2},
                ],
            )

    page.wait_for_load_state.side_effect = pending
    task = asyncio.create_task(wait())
    try:
        await asyncio.wait_for(entered.wait(), 5)
        assert session.page_pool.pages[0].state == "busy"
        with pytest.raises(RuntimeError, match="busy"):
            await server.browser_actions("browser", [{"type": "wait_time", "milliseconds": 0}])
        with pytest.raises(RuntimeError, match="busy"):
            await server.browser_actions("browser", [{"type": "press_key", "key": "Enter"}])
    finally:
        scope.cancel() if cancel_mode == "scope" else task.cancel()
        if cancel_mode == "scope":
            await asyncio.wait_for(task, 5)
            assert scope.cancelled_caught
        else:
            with pytest.raises(asyncio.CancelledError):
                await task
    assert session.page_pool.pages[0].state == "ready"
    assert page.wait_for_timeout.await_args_list == [call(1)]
    assert await server.browser_actions("browser", [{"type": "wait_time", "milliseconds": 0}]) == "Actions completed."


@asynccontextmanager
async def _browser() -> AsyncGenerator[tuple[Client, Any, Any], None]:
    server = ScraplingMCPServer(executable_path=getenv("SCRAPLING_EXECUTABLE_PATH"))
    async with Client(server._build_server("127.0.0.1", 8000)) as client:
        opened = await client.call_tool("browser_open", {"session_id": "browser"})
        assert not opened.is_error
        try:
            session = server._sessions["browser"].session
            await session.context.route(
                "**/*", lambda route: route.fulfill(content_type="text/html", body="<html><body></body></html>")
            )
            fetched = await client.call_tool(
                "browser_fetch", {"session_id": "browser", "url": "https://wait.test/", "google_search": False}
            )
            assert not fetched.is_error
            yield client, session, session.page_pool.pages[0].page
        finally:
            assert not (await client.call_tool("close_session", {"session_id": "browser"})).is_error


@pytest.mark.browser
@pytest.mark.asyncio
async def test_browser_wait_live_pause_and_element_states() -> None:
    async with _browser() as (client, session, page):
        started = monotonic()
        assert not (
            await client.call_tool(
                "browser_actions", {"session_id": "browser", "actions": [{"type": "wait_time", "milliseconds": 80}]}
            )
        ).is_error
        assert monotonic() - started >= 0.07
        for state, setup, change in (
            (
                "attached",
                "document.body.innerHTML = ''",
                "document.body.innerHTML = '<div id=target hidden>Ready</div>'",
            ),
            ("visible", "", "document.querySelector('#target').hidden = false"),
            ("hidden", "", "document.querySelector('#target').hidden = true"),
            ("detached", "", "document.querySelector('#target').remove()"),
        ):
            await page.evaluate(f"() => {{ {setup}; setTimeout(() => {{ {change} }}, 80); }}")
            result = await client.call_tool(
                "browser_actions",
                {
                    "session_id": "browser",
                    "actions": [{"type": "wait_element", "target": "#target", "state": state, "timeout": 5000}],
                },
            )
            assert not result.is_error
            assert session.page_pool.pages[0].state == "ready"
            if state in ("attached", "detached"):
                assert await page.locator("#target").count() == (1 if state == "attached" else 0)
            else:
                assert await page.locator("#target").is_visible() == (state == "visible")
        for state in ("hidden", "detached"):
            assert not (
                await client.call_tool(
                    "browser_actions",
                    {
                        "session_id": "browser",
                        "actions": [{"type": "wait_element", "target": "#absent", "state": state, "timeout": 100}],
                    },
                )
            ).is_error
        await page.evaluate("document.body.innerHTML = '<div class=duplicate></div><div class=duplicate></div>'")
        result = await client.call_tool(
            "browser_actions",
            {
                "session_id": "browser",
                "actions": [{"type": "wait_element", "target": ".duplicate", "state": "attached", "timeout": 100}],
            },
        )
        assert result.is_error and isinstance(result.content[0], TextContent)
        assert "strict mode violation" in result.content[0].text
        assert session.page_pool.pages[0].state == "ready"


@pytest.mark.browser
@pytest.mark.asyncio
async def test_browser_wait_live_current_document_load_states() -> None:
    async with _browser() as (client, session, page):
        requested, release = asyncio.Event(), asyncio.Event()

        async def blocked(route: Any) -> None:
            requested.set()
            await release.wait()
            await route.fulfill(body="done")

        async def wait(values: dict[str, Any]) -> Any:
            return await client.call_tool(
                "browser_actions", {"session_id": "browser", "actions": [{"type": "wait_load", **values}]}
            )

        await page.route("**/pending", blocked)
        await page.route(
            "**/document",
            lambda route: route.fulfill(
                content_type="text/html", body='<html><body><img src="/pending"></body></html>'
            ),
        )
        task = None
        try:
            await page.goto("https://wait.test/document", wait_until="commit")
            await asyncio.wait_for(requested.wait(), 5)
            assert not (await wait({"state": "domcontentloaded", "timeout": 5000})).is_error
            assert await page.evaluate("document.readyState") == "interactive"
            task = asyncio.create_task(wait({"state": "load", "timeout": 5000}))
            await asyncio.sleep(0.05)
            assert not task.done()
            release.set()
            assert not (await asyncio.wait_for(task, 5)).is_error
            assert await page.evaluate("document.readyState") == "complete"
            requested.clear()
            release.clear()
            await page.evaluate("() => { window.pending = fetch('/pending').then(response => response.text()); }")
            await asyncio.wait_for(requested.wait(), 5)
            result = await wait({"state": "networkidle", "timeout": 100})
            assert result.is_error and isinstance(result.content[0], TextContent)
            assert "Timeout" in result.content[0].text
            assert session.page_pool.pages[0].state == "ready"
            task = asyncio.create_task(wait({"state": "networkidle", "timeout": 5000}))
            await asyncio.sleep(0.05)
            assert not task.done()
            release.set()
            assert not (await asyncio.wait_for(task, 5)).is_error
            assert await page.evaluate("window.pending") == "done"
            assert session.page_pool.pages[0].state == "ready"
        finally:
            release.set()
            if task is not None and not task.done():
                task.cancel()
                await asyncio.gather(task, return_exceptions=True)


@pytest.mark.browser
@pytest.mark.asyncio
async def test_browser_wait_live_load_visible_hidden_chain() -> None:
    async with _browser() as (client, session, page):
        await page.evaluate("""() => {
            document.body.innerHTML = '<div id=target hidden>Ready</div>';
            setTimeout(() => {
                document.querySelector('#target').hidden = false;
                setTimeout(() => document.querySelector('#target').hidden = true, 300);
            }, 100);
        }""")
        result = await client.call_tool(
            "browser_actions",
            {
                "session_id": "browser",
                "actions": [
                    {"type": "wait_load", "state": "load", "timeout": 5000},
                    {"type": "wait_element", "target": "#target", "state": "visible", "timeout": 5000},
                    {"type": "wait_element", "target": "#target", "state": "hidden", "timeout": 5000},
                ],
            },
        )
        assert not result.is_error
        assert result.content == [TextContent(type="text", text="Actions completed.")]
        assert await page.locator("#target").is_hidden()
        assert session.page_pool.pages[0].state == "ready"
