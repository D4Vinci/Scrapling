import asyncio
from json import loads

import pytest
from mcp.types import TextContent

from scrapling.core._types import Any
from tests.ai.test_browser_wait import _browser


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "expression, reply, expected",
    [
        ("alert('Notice')", {"accept": True}, None),
        ("alert('Notice')", {"accept": False}, None),
        ("confirm('Continue?')", {"accept": True}, True),
        ("confirm('Continue?')", {"accept": False}, False),
        ("prompt('Name?', 'Original')", {"accept": True}, ""),
        ("prompt('Name?', 'Original')", {"accept": True, "prompt_text": ""}, ""),
        ("prompt('Name?', 'Original')", {"accept": True, "prompt_text": "مرحبا 🌍"}, "مرحبا 🌍"),
        ("prompt('Name?', 'Original')", {"accept": False}, None),
        ("prompt('Name?', 'Original')", {"accept": False, "prompt_text": "Ignored"}, None),
    ],
)
async def test_dialog_live_native_results(expression: str, reply: dict[str, Any], expected: Any) -> None:
    async with _browser() as (client, session, page):
        await page.set_content("<button id=trigger>Open</button>")
        await page.evaluate(f"""() => {{
            document.querySelector('#trigger').onclick = () => {{
                document.body.dataset.result = JSON.stringify({expression}) ?? 'null';
                document.body.dataset.done = 'yes';
            }};
        }}""")
        if expression.startswith("prompt") and reply == {"accept": True}:
            page.once("dialog", lambda dialog: dialog.accept())
            await page.locator("#trigger").click(timeout=5000)
            assert loads(await page.get_attribute("body", "data-result")) == expected
        result = await client.call_tool(
            "browser_actions",
            {
                "session_id": "browser",
                "actions": [{"type": "dialog", **reply}, {"type": "click", "target": "#trigger", "timeout": 5000}],
            },
        )
        assert not result.is_error and result.structured_content is None
        assert result.content == [TextContent(type="text", text="Actions completed.")]
        assert await page.evaluate("document.body.dataset.done") == "yes"
        assert loads(await page.get_attribute("body", "data-result")) == expected
        assert session.page_pool.pages[0].state == "ready"


@pytest.mark.asyncio
@pytest.mark.parametrize("trigger", ["selector", "coordinates", "keyboard"])
async def test_dialog_live_queued_replies_and_unexpected_dialog(trigger: str) -> None:
    async with _browser() as (client, session, page):
        await page.set_content("""<button id=trigger>Open</button><script>
            document.querySelector('#trigger').onclick = () => {
                document.body.dataset.results = JSON.stringify([confirm('Continue?'), prompt('Name?', 'Original'), confirm('Unexpected?')]);
            };
        </script>""")
        click: dict[str, Any] = {"type": "click", "target": "#trigger", "timeout": 5000}
        if trigger == "coordinates":
            box = await page.locator("#trigger").bounding_box()
            assert box is not None
            click = {"type": "click", "x": box["x"] + box["width"] / 2, "y": box["y"] + box["height"] / 2}
        elif trigger == "keyboard":
            await page.locator("#trigger").focus()
            click = {"type": "press_key", "key": "Enter"}
        result = await client.call_tool(
            "browser_actions",
            {
                "session_id": "browser",
                "actions": [
                    {"type": "dialog", "accept": True},
                    {"type": "dialog", "accept": True, "prompt_text": "Scrapling"},
                    click,
                ],
            },
        )
        assert not result.is_error
        assert loads(await page.get_attribute("body", "data-results")) == [True, "Scrapling", False]
        assert session.page_pool.pages[0].state == "ready"


@pytest.mark.asyncio
@pytest.mark.parametrize("slowly", [False, True])
async def test_dialog_live_new_reply_after_previous_trigger(slowly: bool) -> None:
    async with _browser() as (client, session, page):
        await page.set_content("""<button id=trigger>Open</button><script>
            window.results = [];
            document.querySelector('#trigger').onclick = () => {
                window.results.push(confirm('Continue?'));
                document.body.dataset.results = JSON.stringify(window.results);
            };
        </script>""")
        result = await client.call_tool(
            "browser_actions",
            {
                "session_id": "browser",
                "slowly": slowly,
                "actions": [
                    {"type": "dialog", "accept": True},
                    {"type": "click", "target": "#trigger", "timeout": 5000},
                    {"type": "dialog", "accept": False},
                    {"type": "click", "target": "#trigger", "timeout": 5000},
                ],
            },
        )
        assert not result.is_error
        assert loads(await page.get_attribute("body", "data-results")) == [True, False]
        assert session.page_pool.pages[0].state == "ready"


@pytest.mark.asyncio
async def test_dialog_live_keyboard_trigger() -> None:
    async with _browser() as (client, session, page):
        await page.set_content("""<input id=name><script>
            document.querySelector('#name').onkeydown = event => {
                if (event.key === 'Enter') document.body.dataset.result = JSON.stringify(prompt('Name?', 'Original'));
            };
        </script>""")
        result = await client.call_tool(
            "browser_actions",
            {
                "session_id": "browser",
                "actions": [
                    {"type": "textbox", "target": "#name", "value": "Query", "timeout": 5000},
                    {"type": "dialog", "accept": True, "prompt_text": "Answer"},
                    {"type": "press_key", "key": "Enter"},
                ],
            },
        )
        assert not result.is_error
        assert loads(await page.get_attribute("body", "data-result")) == "Answer"
        assert session.page_pool.pages[0].state == "ready"


@pytest.mark.asyncio
async def test_dialog_live_delayed_trigger_during_wait() -> None:
    async with _browser() as (client, session, page):
        await page.set_content("""<button id=trigger>Open</button><p id=done hidden>Done</p><script>
            document.querySelector('#trigger').onclick = () => setTimeout(() => {
                document.body.dataset.result = JSON.stringify(confirm('Continue?'));
                document.querySelector('#done').hidden = false;
            }, 100);
        </script>""")
        result = await client.call_tool(
            "browser_actions",
            {
                "session_id": "browser",
                "actions": [
                    {"type": "dialog", "accept": True},
                    {"type": "click", "target": "#trigger", "timeout": 5000},
                    {"type": "wait_element", "target": "#done", "timeout": 5000},
                ],
            },
        )
        assert not result.is_error
        assert loads(await page.get_attribute("body", "data-result")) is True
        assert await page.locator("#done").is_visible()
        assert session.page_pool.pages[0].state == "ready"


@pytest.mark.asyncio
@pytest.mark.parametrize("accept", [False, True])
async def test_dialog_live_beforeunload_navigation(accept: bool) -> None:
    async with _browser() as (client, session, page):
        await page.set_content("""<button id=activate>Start</button><a id=next href=/next>Next</a><script>
            addEventListener('beforeunload', event => {
                event.preventDefault();
                event.returnValue = '';
            });
        </script>""")
        seen: list[str] = []

        def record(dialog: Any) -> None:
            seen.append(dialog.type)

        page.on("dialog", record)
        try:
            result = await client.call_tool(
                "browser_actions",
                {
                    "session_id": "browser",
                    "actions": [
                        {"type": "click", "target": "#activate", "timeout": 5000},
                        {"type": "dialog", "accept": accept},
                        {"type": "click", "target": "#next", "timeout": 5000},
                    ],
                },
            )
        finally:
            page.remove_listener("dialog", record)
        assert not result.is_error
        assert seen == ["beforeunload"]
        assert page.url == ("https://wait.test/next" if accept else "https://wait.test/")
        assert await page.locator("#activate").count() == (0 if accept else 1)
        assert session.page_pool.pages[0].state == "ready"


@pytest.mark.asyncio
@pytest.mark.parametrize("fail", [False, True])
async def test_dialog_live_unused_replies_do_not_reach_later_calls(fail: bool) -> None:
    async with _browser() as (client, session, page):
        await page.set_content("""<button id=trigger>Open</button><script>
            document.querySelector('#trigger').onclick = () => { document.body.dataset.result = JSON.stringify(confirm('Continue?')); };
        </script>""")
        actions: list[dict[str, Any]] = [{"type": "dialog", "accept": True}]
        if fail:
            actions.append({"type": "wait_element", "target": "#missing", "timeout": 50})
        result = await client.call_tool("browser_actions", {"session_id": "browser", "actions": actions})
        assert bool(result.is_error) == fail
        if fail:
            assert isinstance(result.content[0], TextContent)
            assert "Action 2 (wait_element) failed:" in result.content[0].text
        assert session.page_pool.pages[0].state == "ready"
        result = await client.call_tool(
            "browser_actions",
            {"session_id": "browser", "actions": [{"type": "click", "target": "#trigger", "timeout": 5000}]},
        )
        assert not result.is_error
        assert loads(await page.get_attribute("body", "data-result")) is False


@pytest.mark.asyncio
async def test_dialog_live_cancel_removes_unused_reply() -> None:
    async with _browser() as (client, session, page):
        await page.set_content("""<button id=start>Start</button><button id=trigger>Open</button><script>
            document.querySelector('#start').onclick = () => { document.body.dataset.started = 'yes'; };
            document.querySelector('#trigger').onclick = () => { document.body.dataset.result = JSON.stringify(confirm('Continue?')); };
        </script>""")
        task = asyncio.create_task(
            client.call_tool(
                "browser_actions",
                {
                    "session_id": "browser",
                    "actions": [
                        {"type": "dialog", "accept": True},
                        {"type": "click", "target": "#start", "timeout": 5000},
                        {"type": "wait_element", "target": "#missing", "timeout": 0},
                    ],
                },
            )
        )
        try:
            await page.wait_for_function("document.body.dataset.started === 'yes'", timeout=5000)
            assert session.page_pool.pages[0].state == "busy"
        finally:
            task.cancel()
            with pytest.raises(asyncio.CancelledError):
                await task

        async def released() -> None:
            while session.page_pool.pages[0].state != "ready":
                await asyncio.sleep(0.01)

        await asyncio.wait_for(released(), 5)
        result = await client.call_tool(
            "browser_actions",
            {"session_id": "browser", "actions": [{"type": "click", "target": "#trigger", "timeout": 5000}]},
        )
        assert not result.is_error
        assert loads(await page.get_attribute("body", "data-result")) is False
