from json import loads
from re import search
from unittest.mock import AsyncMock, Mock, call

import pytest
from mcp.client import Client
from mcp.types import TextContent

from scrapling.core.ai import ScraplingMCPServer
from scrapling.core.ai.server import _SessionEntry
from scrapling.core._types import Any
from scrapling.engines._browsers._base import AsyncSession
from tests.ai.test_browser_wait import _browser


def _server() -> tuple[ScraplingMCPServer, AsyncSession, Mock]:
    server = ScraplingMCPServer()
    session = AsyncSession()
    session._is_alive = True
    page = Mock()
    page.is_closed.return_value = False
    page.wait_for_timeout = AsyncMock()
    page.wait_for_load_state = AsyncMock()
    page.keyboard.press = AsyncMock()
    page.mouse.wheel = AsyncMock()
    for name in ("fill", "press_sequentially", "wait_for"):
        setattr(page.locator.return_value, name, AsyncMock())
    session.page_pool.add_page(page).mark_ready()
    server._sessions["browser"] = _SessionEntry(session, "stealthy")
    return server, session, page


@pytest.mark.asyncio
@pytest.mark.parametrize("slowly", [False, True])
async def test_mixed_actions_keep_order_and_sample_each_delay(slowly: bool, monkeypatch: pytest.MonkeyPatch) -> None:
    server, session, page = _server()
    events = Mock()
    pause = AsyncMock()
    random = Mock(side_effect=[55, 145, 0.11, 0.12, 0.13, 0.14, 0.15])
    monkeypatch.setattr("scrapling.core.ai._browser_actions.uniform", random)
    monkeypatch.setattr("scrapling.core.ai._browser_actions.sleep", pause)

    async def reserved(*args: Any, **kwargs: Any) -> None:
        assert session.page_pool.pages[0].state == "busy"

    for name, method in (
        ("fill", page.locator.return_value.fill),
        ("type", page.locator.return_value.press_sequentially),
        ("key", page.keyboard.press),
        ("time", page.wait_for_timeout),
        ("wheel", page.mouse.wheel),
        ("element", page.locator.return_value.wait_for),
        ("load", page.wait_for_load_state),
        ("pause", pause),
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
                    {"type": "textbox", "target": "#name", "value": "ab", "timeout": 17},
                    {"type": "press_key", "key": "Tab"},
                    {"type": "wait_time", "milliseconds": 12},
                    {"type": "wheel", "delta_y": 4},
                    {"type": "wait_element", "target": "#ready", "timeout": 23},
                    {"type": "wait_load", "state": "load", "timeout": 31},
                ],
            },
        )
    assert not result.is_error and result.structured_content is None
    assert result.content == [TextContent(type="text", text="Actions completed.")]
    expected = [call.fill("" if slowly else "ab", timeout=17)]
    if slowly:
        expected += [call.type("a", delay=55, timeout=17), call.type("b", delay=145, timeout=17)]
    for delay, action in zip(
        (0.11, 0.12, 0.13, 0.14, 0.15),
        (
            call.key("Tab"),
            call.time(12),
            call.wheel(0, 4),
            call.element(state="visible", timeout=23),
            call.load("load", timeout=31),
        ),
    ):
        if slowly:
            expected.append(call.pause(delay))
        expected.append(action)
    assert events.mock_calls == expected
    assert random.call_args_list == ([call(50, 150)] * 2 + [call(0.1, 0.3)] * 5 if slowly else [])
    assert page.is_closed.call_count == 2
    assert session.page_pool.pages[0].state == "ready"


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "invalid",
    [
        {"type": "textbox", "target": None, "value": "bad"},
        {"type": "click", "x": 10},
        {"type": "combobox", "target": "#kind", "value": {}},
        {"type": "press_key", "key": ""},
        {"type": "wait_element", "target": "#ready", "timeout": -1},
    ],
)
async def test_invalid_later_action_prevents_other_action_kinds(invalid: dict[str, Any]) -> None:
    server, session, page = _server()
    async with Client(server._build_server("127.0.0.1", 8000)) as client:
        result = await client.call_tool(
            "browser_actions",
            {
                "session_id": "browser",
                "actions": [
                    {"type": "wait_time", "milliseconds": 0},
                    {"type": "textbox", "target": "#name", "value": "unchanged"},
                    invalid,
                    {"type": "press_key", "key": "Enter"},
                ],
            },
        )
    assert result.is_error
    page.is_closed.assert_not_called()
    page.wait_for_timeout.assert_not_awaited()
    page.locator.assert_not_called()
    page.keyboard.press.assert_not_awaited()
    assert session.page_pool.pages[0].state == "ready"


@pytest.mark.asyncio
@pytest.mark.parametrize("slowly", [False, True])
async def test_live_mixed_chain_resolves_targets_created_by_earlier_actions(slowly: bool) -> None:
    async with _browser() as (client, session, page):
        await page.set_content("""<form><label>Query<input id=query></label><button>Search</button></form>
            <div id=loading hidden>Loading</div><div id=results></div><div id=details></div><textarea id=events hidden>[]</textarea>
            <script>
            const record = value => {
                const output = document.querySelector('#events');
                output.value = JSON.stringify([...JSON.parse(output.value), value]);
            };
            document.querySelector('form').onsubmit = event => {
                event.preventDefault();
                record('submit:' + document.querySelector('#query').value);
                document.querySelector('#loading').hidden = false;
                setTimeout(() => {
                    document.querySelector('#results').innerHTML = '<button id=result>Result</button><button id=choose hidden>Choose</button>';
                    document.querySelector('#loading').hidden = true;
                    document.querySelector('#result').onmouseenter = () => {
                        record('hover');
                        document.querySelector('#choose').hidden = false;
                    };
                    document.querySelector('#choose').onclick = () => {
                        record('choose');
                        document.querySelector('#details').innerHTML = '<input id=note><input id=agree type=checkbox><select id=kind><option value=a>A</option><option value=b>B</option></select>';
                    };
                }, 80);
            };
            </script>""")
        snapshot = await client.call_tool("browser_extract", {"session_id": "browser"})
        assert not snapshot.is_error and isinstance(snapshot.content[0], TextContent)
        ref = search(r'textbox "Query".*?\[ref=([^\]]+)\]', snapshot.content[0].text)
        assert ref is not None
        result = await client.call_tool(
            "browser_actions",
            {
                "session_id": "browser",
                "slowly": slowly,
                "actions": [
                    {"type": "textbox", "target": f"aria-ref={ref[1]}", "value": "Scrapling"},
                    {"type": "press_key", "key": "Enter"},
                    {"type": "wait_element", "target": "#result", "timeout": 5000},
                    {"type": "wait_element", "target": "#loading", "state": "hidden", "timeout": 5000},
                    {"type": "move", "target": "#result", "timeout": 5000},
                    {"type": "click", "target": "#choose", "timeout": 5000},
                    {"type": "textbox", "target": "#note", "value": "Done", "timeout": 5000},
                    {"type": "checkbox", "target": "#agree", "value": True, "timeout": 5000},
                    {"type": "combobox", "target": "#kind", "value": "B", "timeout": 5000},
                ],
            },
        )
        assert not result.is_error and result.content == [TextContent(type="text", text="Actions completed.")]
        assert loads(await page.locator("#events").input_value()) == ["submit:Scrapling", "hover", "choose"]
        assert await page.locator("#note").input_value() == "Done"
        assert await page.locator("#agree").is_checked()
        assert await page.locator("#kind").input_value() == "b"
        assert session.page_pool.pages[0].state == "ready"


@pytest.mark.asyncio
@pytest.mark.parametrize("kind", ["textbox", "move", "click", "wait_element"])
async def test_live_stale_ref_stops_mixed_chain_without_retargeting(kind: str) -> None:
    async with _browser() as (client, session, page):
        await page.set_content("""<label>Old<input id=field value=old></label><button id=replace>Replace</button>
            <script>
            document.querySelector('#replace').onclick = () => {
                document.querySelector('#field').outerHTML = '<input id=field value=new>';
            };
            </script>""")
        snapshot = await client.call_tool("browser_extract", {"session_id": "browser"})
        assert not snapshot.is_error and isinstance(snapshot.content[0], TextContent)
        ref = search(r'textbox "Old".*?\[ref=([^\]]+)\]', snapshot.content[0].text)
        assert ref is not None
        result = await client.call_tool(
            "browser_actions",
            {
                "session_id": "browser",
                "actions": [
                    {"type": "click", "target": "#replace"},
                    {
                        "type": kind,
                        "target": f"aria-ref={ref[1]}",
                        "timeout": 100,
                        **({"value": "wrong"} if kind == "textbox" else {}),
                    },
                    {"type": "textbox", "target": "#field", "value": "skipped"},
                ],
            },
        )
        assert result.is_error and isinstance(result.content[0], TextContent)
        assert f"Action 2 ({kind}) failed:" in result.content[0].text
        assert await page.locator("#field").input_value() == "new"
        assert session.page_pool.pages[0].state == "ready"


@pytest.mark.asyncio
@pytest.mark.parametrize("use_ref", [False, True])
async def test_live_targets_keep_explicit_refs_and_ref_shaped_selectors_distinct(use_ref: bool) -> None:
    async with _browser() as (client, session, page):
        await page.set_content("""<e12 role=textbox aria-label=Literal contenteditable=true
            style="display:block;width:200px;height:50px"
            onmouseenter="this.dataset.hovered='yes'" onclick="this.dataset.clicked='yes'">initial</e12>""")
        snapshot = await client.call_tool("browser_extract", {"session_id": "browser"})
        assert not snapshot.is_error and isinstance(snapshot.content[0], TextContent)
        ref = search(r'textbox "Literal".*?\[ref=([^\]]+)\]', snapshot.content[0].text)
        assert ref is not None
        target = f"aria-ref={ref[1]}" if use_ref else "e12"
        result = await client.call_tool(
            "browser_actions",
            {
                "session_id": "browser",
                "actions": [
                    {"type": "wait_element", "target": target, "timeout": 1000},
                    {"type": "move", "target": target, "timeout": 1000},
                    {"type": "textbox", "target": target, "value": "changed", "timeout": 1000},
                    {"type": "click", "target": target, "timeout": 1000},
                ],
            },
        )
        assert not result.is_error
        element = page.locator("e12")
        assert await element.text_content() == "changed"
        assert await element.get_attribute("data-hovered") == "yes"
        assert await element.get_attribute("data-clicked") == "yes"
        assert session.page_pool.pages[0].state == "ready"
