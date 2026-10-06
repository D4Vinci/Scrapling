import asyncio
import re
from os import getenv
from re import search
from unittest.mock import AsyncMock, Mock

import pytest
from mcp.client import Client
from mcp.types import TextContent
from patchright.async_api import Page, TimeoutError as PatchrightTimeoutError

from scrapling.core.ai import ScraplingMCPServer, SessionType
from scrapling.core.ai.server import _SessionEntry
from scrapling.core.ai._snapshot_search import _search_snapshot
from scrapling.core._types import Any, cast
from scrapling.engines._browsers._base import AsyncSession
from scrapling.engines._browsers._stealth import AsyncStealthySession
from scrapling.engines.toolbelt.custom import Response


SNAPSHOT = '- button "Save" [ref=e2]'
HTML = """<!DOCTYPE html><html><body><main><label>Name<input value="initial"></label>
<button onclick="document.querySelector('output').textContent = document.querySelector('input').value">Save</button>
<output></output></main><button>Outside scope</button><script>
setTimeout(() => { document.querySelector('output').textContent = 'Ready'; document.querySelector('output').id = 'ready'; }, 50);
setTimeout(() => { document.querySelector('input').value = 'after wait'; }, 150);
</script></body></html>"""


def _server(session_type: SessionType = "stealthy") -> tuple[ScraplingMCPServer, AsyncSession, Mock]:
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
@pytest.mark.parametrize("boxes", [None, False, True])
async def test_browser_snapshot_returns_plain_mcp_text(boxes: bool | None) -> None:
    server, session, page = _server()
    async with Client(server._build_server("127.0.0.1", 8000)) as client:
        tools = {tool.name: tool for tool in (await client.list_tools()).tools}
        assert "session_snapshot" not in tools
        tool = tools["browser_snapshot"]
        assert tool.output_schema is None
        assert set(tool.input_schema["properties"]) == {"session_id", "depth", "boxes", "search", "regex"}
        assert tool.input_schema["properties"]["boxes"]["default"] is True
        assert tool.input_schema["properties"]["regex"]["default"] is False
        assert tool.input_schema["properties"]["search"]["default"] is None
        assert {"type": "string", "minLength": 1} in tool.input_schema["properties"]["search"]["anyOf"]
        assert tool.input_schema["required"] == ["session_id"]
        fetch_props = tools["browser_fetch"].input_schema["properties"]
        assert set(fetch_props["extraction_type"]["enum"]) == {"markdown", "html", "text", "snapshot"}
        assert "depth" not in fetch_props and "boxes" not in fetch_props
        assert "snapshot" not in tools["browser_fetch_once"].input_schema["properties"]["extraction_type"]["enum"]
        args: dict[str, Any] = {"session_id": "browser", "depth": 3}
        if boxes is not None:
            args["boxes"] = boxes
        result = await client.call_tool("browser_snapshot", args)
    assert not result.is_error
    assert result.structured_content is None
    assert result.content == [TextContent(type="text", text=SNAPSHOT)]
    page.aria_snapshot.assert_awaited_once_with(mode="ai", depth=3, boxes=True if boxes is None else boxes)
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
        ("static", "'stealthy'"),
        ("empty", "browser_fetch"),
        ("busy", "busy"),
        ("closed", "closed"),
    ],
)
async def test_browser_snapshot_errors_reach_the_mcp_client(state: str, message: str) -> None:
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
    page.aria_snapshot.side_effect = PatchrightTimeoutError("snapshot timeout")
    with pytest.raises(PatchrightTimeoutError, match="snapshot timeout"):
        await server.browser_snapshot("browser")
    assert session.page_pool.pages[0].state == "ready"
    page.close.assert_not_called()
    page.aria_snapshot.side_effect = None
    assert await server.browser_snapshot("browser") == SNAPSHOT


@pytest.mark.asyncio
@pytest.mark.parametrize("css_selector", [None, "main"])
async def test_browser_snapshot_live_mcp_round_trip(css_selector: str | None) -> None:
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
        opened = await client.call_tool("browser_open", {"session_id": "browser"})
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
            assert "[box=" in fetched_snapshot
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
            result = await client.call_tool("browser_snapshot", {"session_id": "browser"})
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
            without_boxes = await client.call_tool("browser_snapshot", {"session_id": "browser", "boxes": False})
            assert not without_boxes.is_error
            assert len(without_boxes.content) == 1 and isinstance(without_boxes.content[0], TextContent)
            assert "[box=" not in without_boxes.content[0].text
            assert "[ref=" in without_boxes.content[0].text
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
    page.aria_snapshot.assert_awaited_once_with(mode="ai", depth=None, boxes=True)
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
    page.locator.return_value.aria_snapshot = AsyncMock(side_effect=PatchrightTimeoutError("snapshot timeout"))
    with pytest.raises(PatchrightTimeoutError, match="snapshot timeout"):
        await server.browser_fetch("https://snapshot.test/", "browser", extraction_type="snapshot", css_selector="main")
    fetch.assert_awaited_once()
    assert {"extraction_type", "css_selector", "depth", "boxes"}.isdisjoint(fetch.call_args.kwargs)
    page.aria_snapshot.assert_not_awaited()
    assert session.page_pool.pages[0].state == "ready"
    page.close.assert_not_called()


@pytest.mark.parametrize(
    "snapshot, expression, expected",
    [
        ("", ".*", ""),
        (SNAPSHOT, "missing", ""),
        (SNAPSHOT, "save", ""),
        (SNAPSHOT, "(?i)save", SNAPSHOT),
        ("- text: Save Save", "Save", "- text: Save Save"),
        ("- text: A\n- text: B", ".*", "- text: A\n- text: B"),
        ("- text: Straße\n- text: Αθήνα", "(?i)αθήνα", "- text: Straße\n- text: Αθήνα"),
        ("- text: First\n- text: Second", "First.*Second", ""),
        ("- text: First\n- text: Second", "(?m)^- text: Second$", "- text: First\n- text: Second"),
        ("- text: A\u2028B", "B", "- text: A\u2028B"),
    ],
)
def test_snapshot_search_matches_lines(snapshot: str, expression: str, expected: str) -> None:
    assert _search_snapshot(snapshot, re.compile(expression)) == expected


@pytest.mark.parametrize(
    "expression, expected",
    [
        ("line 0$", "- text: line 0\n- text: line 1\n- text: line 2\n- text: line 3\n..."),
        ("line 10$", "...\n- text: line 7\n- text: line 8\n- text: line 9\n- text: line 10"),
        (
            "line [45]$",
            "...\n- text: line 1\n- text: line 2\n- text: line 3\n- text: line 4\n- text: line 5\n- text: line 6\n- text: line 7\n- text: line 8\n...",
        ),
        (
            "line (0|10)$",
            "- text: line 0\n- text: line 1\n- text: line 2\n- text: line 3\n...\n- text: line 7\n- text: line 8\n- text: line 9\n- text: line 10",
        ),
        (
            "line (3|7)$",
            "\n".join(f"- text: line {index}" for index in range(11)),
        ),
    ],
)
def test_snapshot_search_keeps_neighbors_and_merges_overlap(expression: str, expected: str) -> None:
    snapshot = "\n".join(f"- text: line {index}" for index in range(11))
    assert _search_snapshot(snapshot, re.compile(expression)) == expected


def test_snapshot_search_preserves_ancestors_for_matches_and_neighbors() -> None:
    snapshot = """- main [ref=e1]:
  - region "Before" [ref=e2]:
    - heading "Unrelated"
    - text: old 1
    - text: old 2
    - link "Previous" [ref=e6]:
      - /url: /previous
  - region "Matched" [ref=e8]:
    - list [ref=e9]:
      - listitem "Needle" [ref=e10] [box=10,20,30,40]
      - listitem "Next" [ref=e11]
  - region "After" [ref=e12]:
    - text: context
    - text: omitted 1
    - text: omitted 2"""
    expected = """- main [ref=e1]:
  - region "Before" [ref=e2]:
...
    - link "Previous" [ref=e6]:
      - /url: /previous
  - region "Matched" [ref=e8]:
    - list [ref=e9]:
      - listitem "Needle" [ref=e10] [box=10,20,30,40]
      - listitem "Next" [ref=e11]
  - region "After" [ref=e12]:
    - text: context
..."""
    assert _search_snapshot(snapshot, re.compile("Needle")) == expected


def test_snapshot_search_keeps_all_matches_without_a_result_limit() -> None:
    snapshot = "\n".join(f'- link "Result {index}" [ref=e{index}]' for index in range(150))
    assert _search_snapshot(snapshot, re.compile("Result")) == snapshot


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "snapshot, query, regex, expected",
    [
        (SNAPSHOT, "save", False, SNAPSHOT),
        (SNAPSHOT, "save", True, ""),
        (SNAPSHOT, "(?i)save", True, SNAPSHOT),
        (SNAPSHOT, '^.*button "S.ve"', True, SNAPSHOT),
        (SNAPSHOT, "/Save/", True, ""),
        (
            "- text: Price [USD]\n- text: Price USD",
            "[USD]",
            False,
            "- text: Price [USD]\n- text: Price USD",
        ),
        ("- text: C++", "C++", False, "- text: C++"),
        ("- text: Αθήνα", "ΑΘΉΝΑ", False, "- text: Αθήνα"),
        (SNAPSHOT, None, False, SNAPSHOT),
        ('- main:\n  - button "Save"\n', None, False, '- main:\n  - button "Save"\n'),
    ],
)
async def test_browser_snapshot_search_mcp(snapshot: str, query: str | None, regex: bool, expected: str) -> None:
    server, session, page = _server()
    page.aria_snapshot.return_value = snapshot
    async with Client(server._build_server("127.0.0.1", 8000)) as client:
        result = await client.call_tool(
            "browser_snapshot",
            {"session_id": "browser", "search": query, "regex": regex, "depth": 2, "boxes": False},
        )
    assert not result.is_error
    assert result.structured_content is None
    assert result.content == [TextContent(type="text", text=expected)]
    page.aria_snapshot.assert_awaited_once_with(mode="ai", depth=2, boxes=False)
    assert session.page_pool.pages[0].state == "ready"
    page.goto.assert_not_called()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "args", [{"regex": True}, {"regex": True, "search": None}, {"regex": True, "search": "["}, {"search": ""}]
)
async def test_browser_snapshot_search_rejects_invalid_input_before_page_capture(
    args: dict[str, Any], monkeypatch: pytest.MonkeyPatch
) -> None:
    server, session, page = _server()
    reserve = Mock(wraps=session.page_pool.get_ready_page)
    monkeypatch.setattr(type(session.page_pool), "get_ready_page", reserve)
    async with Client(server._build_server("127.0.0.1", 8000)) as client:
        result = await client.call_tool("browser_snapshot", {"session_id": "browser", **args})
    assert result.is_error
    assert result.content and isinstance(result.content[0], TextContent)
    assert "search" in result.content[0].text.lower() or "regular expression" in result.content[0].text.lower()
    reserve.assert_not_called()
    page.aria_snapshot.assert_not_awaited()
    assert session.page_pool.pages[0].state == "ready"


@pytest.mark.asyncio
@pytest.mark.parametrize("kwargs", [{"regex": True}, {"search": "[", "regex": True}])
async def test_browser_snapshot_search_errors_are_value_errors(kwargs: dict[str, Any]) -> None:
    server, session, page = _server()
    with pytest.raises(ValueError):
        await server.browser_snapshot("browser", **kwargs)
    page.aria_snapshot.assert_not_awaited()
    assert session.page_pool.pages[0].state == "ready"


@pytest.mark.asyncio
async def test_browser_snapshot_search_live_refs_and_state() -> None:
    server = ScraplingMCPServer(executable_path=getenv("SCRAPLING_EXECUTABLE_PATH"))
    requests: list[str] = []
    html = (
        '<main aria-label="Results"><section aria-label="Catalog">'
        + "".join(f"<p>Before result {index}</p>" for index in range(12))
        + "<button onclick=\"document.querySelector('output').textContent='Saved'\">Save result</button>"
        + "".join(f"<p>After result {index}</p>" for index in range(12))
        + "</section><output>Waiting</output></main>"
    )

    async def serve(route: Any) -> None:
        if route.request.is_navigation_request():
            requests.append(route.request.url)
        await route.fulfill(content_type="text/html", body=html)

    async with Client(server._build_server("127.0.0.1", 8000)) as client:
        opened = await client.call_tool("browser_open", {"session_id": "browser"})
        assert not opened.is_error
        try:
            session = cast(AsyncStealthySession, server._sessions["browser"].session)
            await session.context.route("**/*", serve)
            fetched = await client.call_tool(
                "browser_fetch",
                {
                    "session_id": "browser",
                    "url": "https://snapshot-search.test/",
                    "google_search": False,
                    "extraction_type": "snapshot",
                },
            )
            assert not fetched.is_error and fetched.structured_content is not None
            full_snapshot = fetched.structured_content["content"][0]
            page_info = session.page_pool.pages[0]
            page = cast(Page, page_info.page)
            navigations: list[str] = []
            page.on("framenavigated", lambda frame: navigations.append(frame.url))
            await page.evaluate("window.snapshotSearchState = 'retained'")
            result = await client.call_tool("browser_snapshot", {"session_id": "browser", "search": "save RESULT"})
            assert not result.is_error and isinstance(result.content[0], TextContent)
            snapshot = result.content[0].text
            assert snapshot.startswith('- main "Results"')
            assert len(snapshot) < len(full_snapshot)
            assert "[box=" in snapshot
            assert 'main "Results"' in snapshot and 'region "Catalog"' in snapshot
            assert "Before result 0" not in snapshot and "After result 11" not in snapshot
            assert "\n...\n" in snapshot and snapshot.endswith("...")
            matched = search(r'button "Save result".*?\[ref=([^\]]+)\]', snapshot)
            assert matched is not None
            clicked = await client.call_tool(
                "browser_actions",
                {"session_id": "browser", "actions": [{"type": "click", "target": f"aria-ref={matched[1]}"}]},
            )
            assert not clicked.is_error
            assert await page.locator("output").inner_text() == "Saved"
            without_boxes = await client.call_tool(
                "browser_snapshot",
                {"session_id": "browser", "search": '^ +-[ ]button "Save result"', "regex": True, "boxes": False},
            )
            assert not without_boxes.is_error and isinstance(without_boxes.content[0], TextContent)
            assert without_boxes.content[0].text.startswith('- main "Results"')
            assert "[box=" not in without_boxes.content[0].text
            assert "[ref=" in without_boxes.content[0].text
            shallow = await client.call_tool(
                "browser_snapshot", {"session_id": "browser", "search": "Save result", "depth": 1}
            )
            assert not shallow.is_error
            assert shallow.content == [TextContent(type="text", text="")]
            assert await page.evaluate("window.snapshotSearchState") == "retained"
            assert requests == ["https://snapshot-search.test/"] and not navigations
            assert session.page_pool.pages == [page_info] and page_info.state == "ready"
        finally:
            closed = await client.call_tool("close_session", {"session_id": "browser"})
            assert not closed.is_error
