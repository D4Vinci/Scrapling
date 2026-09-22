import asyncio
from os import getenv
from re import search
from unittest.mock import AsyncMock, Mock

import pytest
from mcp.client import Client
from mcp.types import TextContent

from scrapling.core.ai import ScraplingMCPServer, SessionType, _SessionEntry
from scrapling.core._types import Any
from scrapling.engines._browsers._base import AsyncSession
from scrapling.engines.toolbelt.custom import Response


SNAPSHOT = '- button "Save" [ref=e2]'
HTML = """<!DOCTYPE html><html><body><main><label>Name<input value="initial"></label>
<button onclick="document.querySelector('output').textContent = document.querySelector('input').value">Save</button>
<output></output></main><button>Outside scope</button><script>
setTimeout(() => { document.querySelector('output').textContent = 'Ready'; document.querySelector('output').id = 'ready'; }, 50);
setTimeout(() => { document.querySelector('input').value = 'after wait'; }, 150);
</script></body></html>"""


def _server(session_type: SessionType = "dynamic") -> tuple[ScraplingMCPServer, AsyncSession, Mock]:
    server = ScraplingMCPServer()
    session = AsyncSession()
    session._is_alive = True
    page = Mock()
    page.is_closed.return_value = False
    page.aria_snapshot = AsyncMock(return_value=SNAPSHOT)
    session.page_pool.add_page(page).mark_ready()
    server._sessions["browser"] = _SessionEntry(session, session_type)
    return server, session, page


@pytest.mark.asyncio
@pytest.mark.parametrize("session_type", ["dynamic", "stealthy"])
async def test_browser_snapshot_returns_plain_mcp_text(session_type: SessionType) -> None:
    server, session, page = _server(session_type)
    async with Client(server._build_server("127.0.0.1", 8000)) as client:
        tools = {tool.name: tool for tool in (await client.list_tools()).tools}
        assert "session_snapshot" not in tools
        tool = tools["browser_snapshot"]
        assert tool.output_schema is None
        assert set(tool.input_schema["properties"]) == {"session_id", "depth", "boxes"}
        assert tool.input_schema["required"] == ["session_id"]
        fetch_props = tools["browser_fetch"].input_schema["properties"]
        assert set(fetch_props["extraction_type"]["enum"]) == {"markdown", "html", "text", "snapshot"}
        assert "depth" not in fetch_props and "boxes" not in fetch_props
        assert "snapshot" not in tools["fetch"].input_schema["properties"]["extraction_type"]["enum"]
        result = await client.call_tool("browser_snapshot", {"session_id": "browser", "depth": 3, "boxes": True})
    assert not result.is_error
    assert result.structured_content is None
    assert result.content == [TextContent(type="text", text=SNAPSHOT)]
    page.aria_snapshot.assert_awaited_once_with(mode="ai", depth=3, boxes=True)
    assert session.page_pool.pages_count == 1
    assert session.page_pool.pages[0].state == "ready"
    page.goto.assert_not_called()
    page.set_extra_http_headers.assert_not_called()
    page.unroute_all.assert_not_called()
    page.set_default_timeout.assert_not_called()
    page.set_default_navigation_timeout.assert_not_called()


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
async def test_browser_snapshot_errors_reach_the_mcp_client(state: str, message: str) -> None:
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
        result = await client.call_tool("browser_snapshot", {"session_id": "browser"})
    assert result.is_error
    assert result.content and isinstance(result.content[0], TextContent)
    assert message in result.content[0].text
    page.aria_snapshot.assert_not_awaited()
    if state == "closed":
        assert session.page_pool.pages_count == 0
    elif state == "busy":
        assert session.page_pool.pages[0].state == "busy"


@pytest.mark.asyncio
async def test_browser_snapshot_releases_the_page_after_failure() -> None:
    server, session, page = _server()
    page.aria_snapshot.side_effect = TimeoutError("snapshot timeout")
    with pytest.raises(TimeoutError, match="snapshot timeout"):
        await server.browser_snapshot("browser")
    assert session.page_pool.pages[0].state == "ready"
    page.close.assert_not_called()
    page.aria_snapshot.side_effect = None
    assert await server.browser_snapshot("browser") == SNAPSHOT


@pytest.mark.asyncio
@pytest.mark.parametrize("session_type", ["dynamic", "stealthy"])
@pytest.mark.parametrize("css_selector", [None, "main"])
async def test_browser_snapshot_live_mcp_round_trip(session_type: SessionType, css_selector: str | None) -> None:
    server = ScraplingMCPServer(executable_path=getenv("SCRAPLING_EXECUTABLE_PATH"))
    requests: list[str] = []

    async def serve(route: Any) -> None:
        if route.request.is_navigation_request():
            requests.append(route.request.url)
        await route.fulfill(
            status=201,
            content_type="text/html",
            body=HTML,
        )

    async with Client(server._build_server("127.0.0.1", 8000)) as client:
        opened = await client.call_tool("browser_open", {"session_type": session_type, "session_id": "browser"})
        assert not opened.is_error
        try:
            session = server._sessions["browser"].session
            await session.context.route("**/*", serve)
            fetched = await client.call_tool(
                "browser_fetch",
                {
                    "session_id": "browser",
                    "url": "https://snapshot.test/",
                    "google_search": False,
                    "extraction_type": "snapshot",
                    "css_selector": css_selector,
                    "wait_selector": "#ready",
                    "wait": 250,
                },
            )
            assert not fetched.is_error
            assert fetched.structured_content is not None
            assert fetched.structured_content["status"] == 201
            assert fetched.structured_content["url"] == "https://snapshot.test/"
            fetched_snapshot = fetched.structured_content["content"][0]
            assert "after wait" in fetched_snapshot and "initial" not in fetched_snapshot
            assert ("Outside scope" in fetched_snapshot) is (css_selector is None)
            assert requests == ["https://snapshot.test/"]
            page_info = session.page_pool.pages[0]
            page = page_info.page
            match = search(r'button "Save".*?\[ref=([^\]]+)\]', fetched_snapshot)
            assert match is not None
            await page.locator(f"aria-ref={match[1]}").click()
            assert await page.locator("output").inner_text() == "after wait"
            await page.get_by_label("Name").fill("live value")
            navigations: list[str] = []
            page.on("framenavigated", lambda frame: navigations.append(frame.url))
            previous_requests = requests.copy()
            result = await client.call_tool("browser_snapshot", {"session_id": "browser", "boxes": True})
            assert not result.is_error
            assert result.structured_content is None
            assert len(result.content) == 1 and isinstance(result.content[0], TextContent)
            snapshot = result.content[0].text
            assert "live value" in snapshot and "initial" not in snapshot
            assert "Outside scope" in snapshot
            assert "[box=" in snapshot
            assert requests == previous_requests and not navigations
            assert session.page_pool.pages == [page_info] and page_info.state == "ready"
            match = search(r'button "Save".*?\[ref=([^\]]+)\]', snapshot)
            assert match is not None
            await page.locator(f"aria-ref={match[1]}").click()
            assert await page.locator("output").inner_text() == "live value"
            for selector in ("#missing", "button", "["):
                previous_count = len(requests)
                failed = await client.call_tool(
                    "browser_fetch",
                    {
                        "session_id": "browser",
                        "url": "https://snapshot.test/",
                        "google_search": False,
                        "extraction_type": "snapshot",
                        "css_selector": selector,
                    },
                )
                assert failed.is_error
                assert len(requests) == previous_count + 1
                assert session.page_pool.pages == [page_info] and page_info.state == "ready"
        finally:
            closed = await client.call_tool("close_session", {"session_id": "browser"})
            assert not closed.is_error


@pytest.mark.asyncio
async def test_browser_snapshot_reserves_and_releases_the_page_on_cancel() -> None:
    server, session, page = _server()
    entered = asyncio.Event()
    release = asyncio.Event()

    async def capture(**kwargs: object) -> str:
        entered.set()
        await release.wait()
        return SNAPSHOT

    page.aria_snapshot.side_effect = capture
    task = asyncio.create_task(server.browser_snapshot("browser"))
    try:
        await asyncio.wait_for(entered.wait(), 5)
        assert session.page_pool.pages[0].state == "busy"
        assert session.page_pool.get_ready_page() is None
        with pytest.raises(RuntimeError):
            await server.browser_snapshot("browser")
    finally:
        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await task
    assert session.page_pool.pages[0].state == "ready"
    page.close.assert_not_called()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "extraction_type, expected", [("markdown", ["Hello", ""]), ("html", ["<p>Hello</p>", ""]), ("text", ["Hello", ""])]
)
async def test_browser_fetch_keeps_existing_formats(extraction_type: Any, expected: list[str]) -> None:
    server, session, page = _server()
    response = Response(
        url="https://snapshot.test/final",
        content="<main><p>Hello</p></main>",
        status=201,
        reason="Created",
        cookies={},
        headers={},
        request_headers={},
    )
    fetch = AsyncMock(return_value=response)
    setattr(session, "fetch", fetch)
    result = await server.browser_fetch("https://snapshot.test/", "browser", extraction_type, "p")
    assert result.content == expected
    assert result.status == 201
    assert result.url == "https://snapshot.test/final"
    fetch.assert_awaited_once()
    page.aria_snapshot.assert_not_awaited()


@pytest.mark.asyncio
async def test_browser_fetch_snapshot_keeps_raw_content_and_response_metadata() -> None:
    server, session, page = _server()
    snapshot = '\n- button "Save" [ref=e2]\n'
    page.aria_snapshot.return_value = snapshot
    response = Response(
        url="https://snapshot.test/redirected",
        content="<p>Hello</p>",
        status=202,
        reason="Accepted",
        cookies={},
        headers={},
        request_headers={},
    )
    fetch = AsyncMock(return_value=response)
    setattr(session, "fetch", fetch)
    result = await server.browser_fetch("https://snapshot.test/start", "browser", extraction_type="snapshot")
    assert result.content == [snapshot]
    assert result.status == 202
    assert result.url == "https://snapshot.test/redirected"
    fetch.assert_awaited_once()
    assert {"extraction_type", "css_selector", "depth", "boxes"}.isdisjoint(fetch.call_args.kwargs)


@pytest.mark.asyncio
async def test_browser_fetch_snapshot_error_does_not_refetch() -> None:
    server, session, page = _server()
    response = Response(
        url="https://snapshot.test/final",
        content="<p>Hello</p>",
        status=201,
        reason="Created",
        cookies={},
        headers={},
        request_headers={},
    )
    fetch = AsyncMock(return_value=response)
    setattr(session, "fetch", fetch)
    page.locator.return_value.aria_snapshot = AsyncMock(side_effect=TimeoutError("snapshot timeout"))
    with pytest.raises(TimeoutError, match="snapshot timeout"):
        await server.browser_fetch("https://snapshot.test/", "browser", extraction_type="snapshot", css_selector="main")
    fetch.assert_awaited_once()
    assert {"extraction_type", "css_selector", "depth", "boxes"}.isdisjoint(fetch.call_args.kwargs)
    page.aria_snapshot.assert_not_awaited()
    assert session.page_pool.pages[0].state == "ready"
    page.close.assert_not_called()
