import asyncio
from contextlib import suppress
from re import search
from unittest.mock import AsyncMock, Mock

import pytest
from anyio import CancelScope
from mcp.client import Client
from mcp.types import TextContent
from patchright.async_api import Error as PatchrightError

from scrapling.core.ai import ScraplingMCPServer, SessionType
from scrapling.core.ai.server import _SessionEntry
from scrapling.core._types import Any, Literal
from scrapling.engines._browsers._base import AsyncSession
from tests.ai.test_browser_wait import _browser


HTML = """<!DOCTYPE html><html><head><title>Head title</title></head><body>
<main><h1>Café مرحبا</h1><p>A &amp; B <a href="/more">More</a></p>
<p style="display:none">Hidden text</p><script>window.secret = 'Script text';</script></main>
<p>Outside text</p></body></html>"""


def _server(session_type: SessionType = "stealthy") -> tuple[ScraplingMCPServer, AsyncSession, Mock]:
    server = ScraplingMCPServer()
    session = AsyncSession()
    session._is_alive = True
    page = Mock()
    page.url = "https://extract.test/"
    page.is_closed.return_value = False
    page.content = AsyncMock(return_value=HTML)
    page.wait_for_timeout = AsyncMock()
    page.locator.return_value.evaluate = AsyncMock(return_value='<h1 id="title">Café مرحبا</h1>')
    session.page_pool.add_page(page).mark_ready()
    server._sessions["browser"] = _SessionEntry(session, session_type)
    return server, session, page


async def _extract(client: Client, **options: Any) -> str:
    result = await client.call_tool("browser_extract", {"session_id": "browser", **options})
    assert not result.is_error, result.content
    assert result.structured_content is None
    assert len(result.content) == 1 and isinstance(result.content[0], TextContent)
    return result.content[0].text


@pytest.mark.asyncio
@pytest.mark.parametrize("kind", ["html", "markdown", "text"])
@pytest.mark.parametrize("main_content_only", [False, True])
async def test_browser_extract_content_formats_and_cleaning(
    kind: Literal["html", "markdown", "text"], main_content_only: bool
) -> None:
    server, session, page = _server()
    async with Client(server._build_server("127.0.0.1", 8000)) as client:
        text = await _extract(client, extraction_type=kind, main_content_only=main_content_only, depth=1, boxes=False)
    assert "Café مرحبا" in text and "Outside text" in text
    assert ("Hidden text" in text) is not main_content_only
    assert ("Head title" in text) is not main_content_only
    if kind == "html":
        assert "<h1>Café مرحبا</h1>" in text and '<a href="/more">More</a>' in text
        assert "A &amp; B" in text
        assert ("<script>" in text) is not main_content_only
    elif kind == "markdown":
        assert "[More](/more)" in text and "A & B" in text and "<h1>" not in text
    else:
        assert "A & B" in text and "More" in text and "<" not in text and "Script text" not in text
    page.content.assert_awaited_once_with()
    for method in ("locator", "goto", "reload", "evaluate", "aria_snapshot", "set_default_timeout"):
        getattr(page, method).assert_not_called()
    assert session.page_pool.pages[0].state == "ready"


@pytest.mark.asyncio
@pytest.mark.parametrize("kind", ["html", "markdown", "text"])
@pytest.mark.parametrize("target", ["#title", "xpath=//h1", "aria-ref=e2"])
async def test_browser_extract_content_target_is_native_and_strict(kind: str, target: str) -> None:
    server, session, page = _server()
    async with Client(server._build_server("127.0.0.1", 8000)) as client:
        text = await _extract(client, extraction_type=kind, target=target)
    assert "Café مرحبا" in text and "Outside text" not in text
    page.locator.assert_called_once_with(target)
    page.locator.return_value.evaluate.assert_awaited_once_with("(element) => element.outerHTML")
    page.locator.return_value.first.evaluate.assert_not_called()
    page.content.assert_not_awaited()
    page.goto.assert_not_called()
    assert session.page_pool.pages[0].state == "ready"


@pytest.mark.asyncio
@pytest.mark.parametrize("kind", ["html", "markdown", "text"])
@pytest.mark.parametrize("main_content_only", [False, True])
async def test_browser_extract_content_strips_control_characters(kind: str, main_content_only: bool) -> None:
    server, _, page = _server()
    page.content.return_value = "<html><body><p>Café\x01مرحبا\x08世界\x1f</p></body></html>"
    async with Client(server._build_server("127.0.0.1", 8000)) as client:
        text = await _extract(client, extraction_type=kind, main_content_only=main_content_only)
    assert "Caféمرحبا世界" in text
    assert all(character not in text for character in ("\x01", "\x08", "\x1f"))


@pytest.mark.asyncio
@pytest.mark.parametrize("kind", ["markdown", "text"])
@pytest.mark.parametrize("target", [None, "#empty"])
async def test_browser_extract_content_empty_result_is_empty_text(kind: str, target: str | None) -> None:
    server, _, page = _server()
    page.content.return_value = '<html><body><p id="empty"></p></body></html>'
    page.locator.return_value.evaluate.return_value = '<p id="empty"></p>'
    async with Client(server._build_server("127.0.0.1", 8000)) as client:
        assert await _extract(client, extraction_type=kind, target=target) == ""


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "options",
    [
        {"extraction_type": "json"},
        {"target": ""},
        {"target": 123},
        *[{"extraction_type": kind, "search": ".*"} for kind in ("html", "markdown", "text")],
    ],
)
async def test_browser_extract_content_invalid_options_do_not_reserve_page(options: dict[str, Any]) -> None:
    server, session, page = _server()
    async with Client(server._build_server("127.0.0.1", 8000)) as client:
        result = await client.call_tool("browser_extract", {"session_id": "browser", **options})
    assert result.is_error
    page.is_closed.assert_not_called()
    page.content.assert_not_awaited()
    page.locator.assert_not_called()
    assert session.page_pool.pages[0].state == "ready"


@pytest.mark.asyncio
async def test_browser_extract_content_uses_existing_page_content_retry() -> None:
    server, session, page = _server()
    page.content.side_effect = [PatchrightError("Document is changing"), HTML]
    async with Client(server._build_server("127.0.0.1", 8000)) as client:
        assert "Café مرحبا" in await _extract(client, extraction_type="text")
    assert page.content.await_count == 2
    page.wait_for_timeout.assert_awaited_once_with(500)
    assert session.page_pool.pages[0].state == "ready"


@pytest.mark.asyncio
@pytest.mark.parametrize("closed", [False, True])
async def test_browser_extract_content_target_failure_releases_page(closed: bool) -> None:
    server, session, page = _server()

    async def fail(*args: Any, **kwargs: Any) -> None:
        page.is_closed.return_value = closed
        raise PatchrightError("Target detached")

    page.locator.return_value.evaluate.side_effect = fail
    async with Client(server._build_server("127.0.0.1", 8000)) as client:
        result = await client.call_tool(
            "browser_extract", {"session_id": "browser", "extraction_type": "html", "target": "#title"}
        )
    assert result.is_error and isinstance(result.content[0], TextContent)
    assert "Target detached" in result.content[0].text
    page.locator.return_value.evaluate.assert_awaited_once()
    page.content.assert_not_awaited()
    page.close.assert_not_called()
    assert session.page_pool.pages_count == (0 if closed else 1)
    if not closed:
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
        ("closed", "closed"),
    ],
)
async def test_browser_extract_content_session_errors(state: str, message: str) -> None:
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
        result = await client.call_tool("browser_extract", {"session_id": "browser", "extraction_type": "html"})
    assert result.is_error and isinstance(result.content[0], TextContent)
    assert message in result.content[0].text
    page.content.assert_not_awaited()
    page.locator.assert_not_called()
    if state == "closed":
        assert session.page_pool.pages_count == 0
    elif state == "busy":
        assert session.page_pool.pages[0].state == "busy"


@pytest.mark.asyncio
@pytest.mark.parametrize("target", [None, "#title"])
@pytest.mark.parametrize("cancel_mode", ["task", "scope"])
async def test_browser_extract_content_cancellation_releases_page(target: str | None, cancel_mode: str) -> None:
    server, session, page = _server()
    entered = asyncio.Event()
    scope = CancelScope()

    async def pending(*args: Any, **kwargs: Any) -> str:
        entered.set()
        await asyncio.Event().wait()
        return ""

    async def extract() -> None:
        with scope:
            await server.browser_extract("browser", extraction_type="html", target=target)

    capture = page.locator.return_value.evaluate if target else page.content
    capture.side_effect = pending
    task = asyncio.create_task(extract())
    try:
        await asyncio.wait_for(entered.wait(), 5)
        assert session.page_pool.pages[0].state == "busy"
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
    capture.assert_awaited_once()
    assert session.page_pool.pages[0].state == "ready"
    page.close.assert_not_called()


@pytest.mark.asyncio
async def test_browser_extract_content_live_formats_preserve_current_page() -> None:
    async with _browser() as (client, session, page):
        await page.set_content("""<!DOCTYPE html><html><head><title>Head title</title></head><body>
            <main><h1>Café مرحبا</h1><input id=name value=initial><input id=agree type=checkbox>
            <button id=save onclick="document.querySelector('output').textContent = document.querySelector('#name').value">Save</button>
            <output>Before click</output><p><a href="/more">More</a></p>
            <p style="display:none">Hidden text</p><script>window.secret = 'Script text';</script></main>
            <p>Outside text</p><div style="height: 3000px"></div></body></html>""")
        result = await client.call_tool(
            "browser_actions",
            {
                "session_id": "browser",
                "actions": [
                    {"type": "textbox", "target": "#name", "value": "نتائج جديدة 🌍"},
                    {"type": "checkbox", "target": "#agree", "value": True},
                    {"type": "click", "target": "#save"},
                ],
            },
        )
        assert not result.is_error
        await page.locator("#name").focus()
        await page.evaluate("window.scrollTo(0, 500)")
        state_expression = """() => ({
            html: document.documentElement.outerHTML,
            value: document.querySelector('#name').value,
            checked: document.querySelector('#agree').checked,
            focus: document.activeElement.id,
            scroll: window.scrollY,
            url: location.href
        })"""
        before = await page.evaluate(state_expression)
        page_info = session.page_pool.pages[0]
        navigations: list[str] = []
        requests: list[str] = []
        page.on("framenavigated", lambda frame: navigations.append(frame.url))
        page.on("request", lambda request: requests.append(request.url))
        for kind in ("html", "markdown", "text"):
            for clean in (False, True):
                text = await _extract(client, extraction_type=kind, main_content_only=clean)
                assert "نتائج جديدة 🌍" in text and "Café مرحبا" in text and "Outside text" in text
                assert ("Hidden text" in text) is not clean
                assert ("Head title" in text) is not clean
                if kind == "html":
                    assert "<output>نتائج جديدة 🌍</output>" in text
                    assert ("<script>" in text) is not clean
                elif kind == "markdown":
                    assert "[More](/more)" in text and "<output>" not in text
                else:
                    assert "<output>" not in text and "Script text" not in text
                assert await page.evaluate(state_expression) == before
                assert session.page_pool.pages == [page_info] and page_info.state == "ready"
        assert before["value"] == "نتائج جديدة 🌍" and before["checked"] and before["focus"] == "name"
        assert before["scroll"] == 500 and not navigations and not requests


@pytest.mark.asyncio
async def test_browser_extract_content_live_selectors_refs_and_snapshot_scope() -> None:
    async with _browser() as (client, session, page):
        await page.set_content("""<html><body>
            <main aria-label="Products"><h1>Café مرحبا</h1><button>Buy now</button>
            <p style="display:none">Hidden text</p></main><h2>Outside heading</h2><button>Outside button</button>
            </body></html>""")
        snapshot = await _extract(client, target="main", search="(?i)buy", boxes=False)
        assert 'button "Buy now"' in snapshot and "Outside" not in snapshot
        assert "[box=" not in snapshot
        ref = search(r'button "Buy now".*?\[ref=([^\]]+)\]', snapshot)
        assert ref is not None
        for target in ("main", "xpath=//main", 'role=main[name="Products"]'):
            for kind in ("html", "markdown", "text"):
                text = await _extract(client, extraction_type=kind, target=target)
                assert "Café مرحبا" in text and "Buy now" in text
                assert "Outside" not in text and "Hidden text" not in text
        for kind in ("html", "markdown", "text"):
            text = await _extract(client, extraction_type=kind, target=f"aria-ref={ref[1]}")
            assert "Buy now" in text and "Café" not in text and "Outside" not in text
        button_snapshot = await _extract(client, target=f"aria-ref={ref[1]}")
        assert 'button "Buy now"' in button_snapshot and "[box=" in button_snapshot
        assert "Café" not in button_snapshot and "Outside" not in button_snapshot
        assert await _extract(client, target="main", search="(?i)absent") == ""
        assert session.page_pool.pages[0].state == "ready"


@pytest.mark.asyncio
async def test_browser_extract_content_live_target_errors_allow_next_call() -> None:
    async with _browser() as (client, session, page):
        await page.set_content("<main><button id=old>Old button</button><button>Keep button</button></main>")
        page.set_default_timeout(100)
        snapshot = await _extract(client)
        ref = search(r'button "Old button".*?\[ref=([^\]]+)\]', snapshot)
        assert ref is not None
        await page.locator("#old").evaluate("element => element.remove()")
        for target, error in (
            ("#missing", "Timeout"),
            ("main, button", "strict mode violation"),
            ("[", "selector"),
            (f"aria-ref={ref[1]}", "ref"),
        ):
            for kind in ("snapshot", "html", "markdown", "text"):
                result = await client.call_tool(
                    "browser_extract", {"session_id": "browser", "extraction_type": kind, "target": target}
                )
                assert result.is_error and isinstance(result.content[0], TextContent)
                expected = "does not match any element" if kind == "snapshot" and target == "#missing" else error
                assert expected.lower() in result.content[0].text.lower(), result.content
                assert session.page_pool.pages[0].state == "ready"
        assert await _extract(client, extraction_type="text", target="button") == "Keep button"
