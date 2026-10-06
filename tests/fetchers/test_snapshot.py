from os import getenv
from re import search
from unittest.mock import AsyncMock, Mock

import pytest

from scrapling.core._types import Any
from scrapling.fetchers import AsyncDynamicSession, AsyncStealthySession, DynamicSession, StealthySession


HTML = """<!DOCTYPE html><html><body>
<main><label>Name<input value="initial"></label>
<button onclick="document.querySelector('output').textContent = document.querySelector('input').value">Save</button>
<output></output></main><p>Outside scope</p><script>document.body.dataset.snapshotState = 'kept';</script>
</body></html>"""


@pytest.mark.parametrize("session_type", [DynamicSession, StealthySession])
@pytest.mark.parametrize("css_selector", [None, "main"])
def test_sync_snapshot_forwards_options_and_errors(session_type: Any, css_selector: str | None) -> None:
    page = Mock()
    target = page.locator.return_value if css_selector else page
    target.aria_snapshot.return_value = "snapshot"
    assert session_type._snapshot(page, depth=3, boxes=True, css_selector=css_selector) == "snapshot"
    target.aria_snapshot.assert_called_once_with(mode="ai", depth=3, boxes=True)
    if css_selector:
        page.locator.assert_called_once_with(css_selector)
        page.aria_snapshot.assert_not_called()
    else:
        page.locator.assert_not_called()
    target.aria_snapshot.side_effect = TimeoutError("snapshot timeout")
    with pytest.raises(TimeoutError, match="snapshot timeout"):
        session_type._snapshot(page, css_selector=css_selector)


@pytest.mark.asyncio
@pytest.mark.parametrize("session_type", [AsyncDynamicSession, AsyncStealthySession])
@pytest.mark.parametrize("css_selector", [None, "main"])
async def test_async_snapshot_forwards_options_and_errors(session_type: Any, css_selector: str | None) -> None:
    page = Mock()
    target = page.locator.return_value if css_selector else page
    target.aria_snapshot = AsyncMock(return_value="snapshot")
    assert await session_type._snapshot(page, depth=3, boxes=True, css_selector=css_selector) == "snapshot"
    target.aria_snapshot.assert_awaited_once_with(mode="ai", depth=3, boxes=True)
    if css_selector:
        page.locator.assert_called_once_with(css_selector)
        page.aria_snapshot.assert_not_called()
    else:
        page.locator.assert_not_called()
    target.aria_snapshot.side_effect = TimeoutError("snapshot timeout")
    with pytest.raises(TimeoutError, match="snapshot timeout"):
        await session_type._snapshot(page, css_selector=css_selector)


def _button_ref(snapshot: str) -> str:
    assert "live value" in snapshot
    assert "initial" not in snapshot
    assert "[box=" in snapshot
    match = search(r'button "Save".*?\[ref=([^\]]+)\]', snapshot)
    assert match is not None
    return match[1]


@pytest.mark.parametrize("session_type", [DynamicSession, StealthySession])
def test_sync_snapshot_live_state_and_refs(session_type: Any) -> None:
    def setup(page: Any) -> None:
        page.route("**/*", lambda route: route.fulfill(status=200, content_type="text/html", body=HTML))

    with session_type(executable_path=getenv("SCRAPLING_EXECUTABLE_PATH"), google_search=False) as session:
        response = session.fetch("https://snapshot.test/", page_setup=setup)
        assert response.status == 200
        page = session.page_pool.pages[0].page
        page.get_by_label("Name").fill("live value")
        assert "Outside scope" in session_type._snapshot(page)
        snapshot = session_type._snapshot(page, depth=5, boxes=True)
        page.locator(f"aria-ref={_button_ref(snapshot)}").click()
        snapshot = session_type._snapshot(page, css_selector="main", boxes=True)
        assert "Outside scope" not in snapshot
        page.locator(f"aria-ref={_button_ref(snapshot)}").click()
        assert page.locator("output").inner_text() == "live value"
        assert page.locator("body").get_attribute("data-snapshot-state") == "kept"
        assert page.url == "https://snapshot.test/"
        assert session.page_pool.pages_count == 1


@pytest.mark.asyncio
@pytest.mark.parametrize("session_type", [AsyncDynamicSession, AsyncStealthySession])
async def test_async_snapshot_live_state_and_refs(session_type: Any) -> None:
    async def setup(page: Any) -> None:
        await page.route("**/*", lambda route: route.fulfill(status=200, content_type="text/html", body=HTML))

    async with session_type(executable_path=getenv("SCRAPLING_EXECUTABLE_PATH"), google_search=False) as session:
        response = await session.fetch("https://snapshot.test/", page_setup=setup)
        assert response.status == 200
        page = session.page_pool.pages[0].page
        await page.get_by_label("Name").fill("live value")
        assert "Outside scope" in await session_type._snapshot(page)
        snapshot = await session_type._snapshot(page, depth=5, boxes=True)
        await page.locator(f"aria-ref={_button_ref(snapshot)}").click()
        snapshot = await session_type._snapshot(page, css_selector="main", boxes=True)
        assert "Outside scope" not in snapshot
        await page.locator(f"aria-ref={_button_ref(snapshot)}").click()
        assert await page.locator("output").inner_text() == "live value"
        assert await page.locator("body").get_attribute("data-snapshot-state") == "kept"
        assert page.url == "https://snapshot.test/"
        assert session.page_pool.pages_count == 1
