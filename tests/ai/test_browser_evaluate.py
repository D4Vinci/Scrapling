import asyncio
from contextlib import suppress
from json import loads
from os import getenv
from unittest.mock import AsyncMock, Mock, call

import pytest
from anyio import CancelScope
from mcp.client import Client
from mcp.types import TextContent
from patchright.async_api import Error as PatchrightError

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
    page.evaluate = AsyncMock()
    session.page_pool.add_page(page).mark_ready()
    server._sessions["browser"] = _SessionEntry(session, session_type)
    return server, session, page


@pytest.mark.asyncio
async def test_browser_evaluate_schema_and_annotations() -> None:
    async with Client(ScraplingMCPServer()._build_server("127.0.0.1", 8000)) as client:
        tool = next(tool for tool in (await client.list_tools()).tools if tool.name == "browser_evaluate")
    assert tool.title == "Run JavaScript"
    assert tool.input_schema["required"] == ["session_id", "expression"]
    properties = tool.input_schema["properties"]
    assert set(properties) == {"session_id", "expression", "arg", "isolated_context"}
    assert properties["expression"]["type"] == "string"
    assert properties["expression"]["minLength"] == 1
    assert properties["arg"]["default"] is None
    assert {option["type"] for option in properties["arg"]["anyOf"]} == {"object", "null"}
    assert properties["isolated_context"]["type"] == "boolean"
    assert properties["isolated_context"]["default"] is True
    assert tool.output_schema is None
    assert tool.annotations is not None
    assert tool.annotations.read_only_hint is False
    assert tool.annotations.destructive_hint is True
    assert tool.annotations.idempotent_hint is False
    assert tool.annotations.open_world_hint is True


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "value, expected",
    [
        (None, "null"),
        (True, "true"),
        (False, "false"),
        (42, "42"),
        (1.25, "1.25"),
        ("مرحبا\n", '"مرحبا\\n"'),
        (["a", None], '["a",null]'),
        ({"x": "☃", "nested": [1, False]}, '{"x":"☃","nested":[1,false]}'),
    ],
)
async def test_browser_evaluate_returns_one_compact_json_text_block(value: Any, expected: str) -> None:
    server, session, page = _server()

    async def evaluate(*args: Any, **kwargs: Any) -> Any:
        assert session.page_pool.pages[0].state == "busy"
        return value

    page.evaluate.side_effect = evaluate
    async with Client(server._build_server("127.0.0.1", 8000)) as client:
        result = await client.call_tool("browser_evaluate", {"session_id": "browser", "expression": "document.title"})
    assert not result.is_error and result.structured_content is None
    assert result.content == [TextContent(type="text", text=expected)]
    assert page.mock_calls == [
        call.is_closed(),
        call.evaluate("document.title", arg=None, isolated_context=True),
        call.is_closed(),
    ]
    assert session.page_pool.pages[0].state == "ready"


@pytest.mark.asyncio
@pytest.mark.parametrize("options", [{}, {"isolated_context": False}])
async def test_browser_evaluate_forwards_argument_and_context(options: dict[str, Any]) -> None:
    server, session, page = _server()
    expression = "({items}) => items.length"
    arg = {"items": ["a", "b"], "enabled": True, "empty": None, "strings": ["null", "[1]", '{"x":1}']}
    page.evaluate.return_value = 2
    async with Client(server._build_server("127.0.0.1", 8000)) as client:
        result = await client.call_tool(
            "browser_evaluate", {"session_id": "browser", "expression": expression, "arg": arg, **options}
        )
    assert not result.is_error
    expected = {"isolated_context": options.get("isolated_context", True)}
    page.evaluate.assert_awaited_once_with(expression, arg=arg, **expected)
    assert result.content == [TextContent(type="text", text="2")]
    assert session.page_pool.pages[0].state == "ready"


@pytest.mark.asyncio
@pytest.mark.parametrize("arg", [[1, 2], 42])
async def test_browser_evaluate_rejects_non_object_arguments(arg: Any) -> None:
    server, session, page = _server()
    async with Client(server._build_server("127.0.0.1", 8000)) as client:
        result = await client.call_tool(
            "browser_evaluate", {"session_id": "browser", "expression": "value => value", "arg": arg}
        )
    assert result.is_error
    page.is_closed.assert_not_called()
    page.evaluate.assert_not_awaited()
    assert session.page_pool.pages[0].state == "ready"


@pytest.mark.asyncio
@pytest.mark.parametrize("expression", ["", None, [], 123])
async def test_browser_evaluate_invalid_expression_does_not_reserve_page(expression: Any) -> None:
    server, session, page = _server()
    async with Client(server._build_server("127.0.0.1", 8000)) as client:
        result = await client.call_tool("browser_evaluate", {"session_id": "browser", "expression": expression})
    assert result.is_error
    page.is_closed.assert_not_called()
    page.evaluate.assert_not_awaited()
    assert session.page_pool.pages[0].state == "ready"


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "case, error_type",
    [("nan", ValueError), ("infinite", ValueError), ("unsupported", TypeError), ("circular", ValueError)],
)
async def test_browser_evaluate_serialization_error_releases_page(case: str, error_type: type[Exception]) -> None:
    server, session, page = _server()
    value: Any = (
        [] if case == "circular" else {"nan": float("nan"), "infinite": float("inf"), "unsupported": object()}[case]
    )
    if case == "circular":
        value.append(value)
    page.evaluate.return_value = value
    with pytest.raises(error_type):
        await server.browser_evaluate("browser", "value")
    assert session.page_pool.pages[0].state == "ready"
    async with Client(server._build_server("127.0.0.1", 8000)) as client:
        result = await client.call_tool("browser_evaluate", {"session_id": "browser", "expression": "value"})
    assert result.is_error
    assert page.evaluate.await_count == 2
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
async def test_browser_evaluate_session_errors(state: str, message: str) -> None:
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
        result = await client.call_tool("browser_evaluate", {"session_id": "browser", "expression": "1"})
    assert result.is_error and isinstance(result.content[0], TextContent)
    assert message in result.content[0].text
    page.evaluate.assert_not_awaited()
    if state == "closed":
        assert session.page_pool.pages_count == 0
    elif state == "busy":
        assert session.page_pool.pages[0].state == "busy"


@pytest.mark.asyncio
@pytest.mark.parametrize("closed", [False, True])
async def test_browser_evaluate_native_error_releases_page_without_retry(closed: bool) -> None:
    server, session, page = _server()
    native_error = PatchrightError("script failed")

    async def fail(*args: Any, **kwargs: Any) -> None:
        page.is_closed.return_value = closed
        raise native_error

    page.evaluate.side_effect = fail
    with pytest.raises(PatchrightError) as error:
        await server.browser_evaluate("browser", "badScript()")
    assert error.value is native_error
    page.evaluate.assert_awaited_once()
    page.close.assert_not_called()
    if closed:
        assert session.page_pool.pages_count == 0
    else:
        assert session.page_pool.pages[0].state == "ready"


@pytest.mark.asyncio
@pytest.mark.parametrize("cancel_mode", ["task", "scope"])
async def test_browser_evaluate_reserves_page_until_cancelled(cancel_mode: str) -> None:
    server, session, page = _server()
    entered = asyncio.Event()
    scope = CancelScope()

    async def pending(*args: Any, **kwargs: Any) -> None:
        entered.set()
        await asyncio.Event().wait()

    async def evaluate() -> None:
        with scope:
            await server.browser_evaluate("browser", "new Promise(() => {})")

    page.evaluate.side_effect = pending
    task = asyncio.create_task(evaluate())
    try:
        await asyncio.wait_for(entered.wait(), 5)
        assert session.page_pool.pages[0].state == "busy"
        with pytest.raises(RuntimeError, match="busy"):
            await server.browser_evaluate("browser", "1")
        with pytest.raises(RuntimeError, match="busy"):
            await server.browser_extract("browser")
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
    page.evaluate.assert_awaited_once()
    assert session.page_pool.pages[0].state == "ready"
    page.close.assert_not_called()


@pytest.mark.asyncio
async def test_browser_evaluate_live_expressions_promises_context_and_page_state() -> None:
    server = ScraplingMCPServer(executable_path=getenv("SCRAPLING_EXECUTABLE_PATH"))
    requests: list[str] = []
    html = """<!DOCTYPE html><html><head><title>Evaluate test</title></head><body>
        <input id=name><input id=agree type=checkbox><button id=toggle>Menu</button><div id=menu hidden>Choices</div>
        <output id=status>pending</output><script>
        window.pageState = {label: 'page world'};
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
                "browser_fetch", {"session_id": "browser", "url": "https://evaluate.test/start", "google_search": False}
            )
            assert not fetched.is_error
            page_info = session.page_pool.pages[0]
            page = page_info.page
            actions = await client.call_tool(
                "browser_actions",
                {
                    "session_id": "browser",
                    "actions": [
                        {"type": "textbox", "target": "#name", "value": "before"},
                        {"type": "checkbox", "target": "#agree", "value": True},
                        {"type": "click", "target": "#toggle"},
                        {"type": "click", "target": "#name"},
                    ],
                },
            )
            assert not actions.is_error
            read_state = """() => ({url: location.href, name: document.querySelector('#name').value,
                checked: document.querySelector('#agree').checked, menu: !document.querySelector('#menu').hidden,
                focus: document.activeElement.id, status: document.querySelector('#status').textContent})"""
            before = await page.evaluate(read_state)
            assert before == {
                "url": "https://evaluate.test/edited",
                "name": "before",
                "checked": True,
                "menu": True,
                "focus": "name",
                "status": "pending",
            }
            assert requests == ["https://evaluate.test/start"]
            for expression, arg, expected in (
                ("document.title", None, "Evaluate test"),
                ("undefined", None, None),
                ("({items}) => items.map(item => item * 2)", {"items": [1, 2]}, [2, 4]),
                (
                    "({value}) => value",
                    {"value": {"strings": ["null", "[1]", '{"x":1}'], "count": 3, "flag": False}},
                    {"strings": ["null", "[1]", '{"x":1}'], "count": 3, "flag": False},
                ),
                (
                    "async ({value}) => { await new Promise(resolve => setTimeout(resolve, 20)); return {value, inputs: document.querySelectorAll('input').length}; }",
                    {"value": "مرحبا"},
                    {"value": "مرحبا", "inputs": 2},
                ),
                ("typeof window.pageState", None, "undefined"),
            ):
                result = await client.call_tool(
                    "browser_evaluate", {"session_id": "browser", "expression": expression, "arg": arg}
                )
                assert not result.is_error and result.structured_content is None
                assert len(result.content) == 1 and isinstance(result.content[0], TextContent)
                assert loads(result.content[0].text) == expected
                assert await page.evaluate(read_state) == before
            main_world = await client.call_tool(
                "browser_evaluate",
                {"session_id": "browser", "expression": "window.pageState.label", "isolated_context": False},
            )
            assert not main_world.is_error and isinstance(main_world.content[0], TextContent)
            assert loads(main_world.content[0].text) == "page world"
            changed = await client.call_tool(
                "browser_evaluate",
                {
                    "session_id": "browser",
                    "expression": "({value}) => { document.querySelector('#name').value = value; document.querySelector('#status').textContent = 'saved'; return document.querySelector('#name').value; }",
                    "arg": {"value": "after"},
                },
            )
            assert not changed.is_error and isinstance(changed.content[0], TextContent)
            assert loads(changed.content[0].text) == "after"
            expected_state = {**before, "name": "after", "status": "saved"}
            for expression, message in (
                ("() => { throw new Error('script failed'); }", "script failed"),
                ("Promise.reject(new Error('promise failed'))", "promise failed"),
                ("NaN", "JSON"),
            ):
                failed = await client.call_tool("browser_evaluate", {"session_id": "browser", "expression": expression})
                assert failed.is_error and isinstance(failed.content[0], TextContent)
                assert message in failed.content[0].text
                assert await page.evaluate(read_state) == expected_state
                assert requests == ["https://evaluate.test/start"]
                assert session.page_pool.pages == [page_info] and page_info.state == "ready"
        finally:
            assert not (await client.call_tool("close_session", {"session_id": "browser"})).is_error
