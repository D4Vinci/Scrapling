from functools import partial
from os import getenv
from unittest.mock import patch

import pytest
from patchright.async_api import Page as AsyncPage, Route as AsyncRoute
from patchright.sync_api import Page, Route

from scrapling.core._types import Any, cast
from scrapling.fetchers import AsyncStealthySession, StealthySession


URL = "https://cloudflare-readiness.test/"
FRAME_URL = "https://challenges.cloudflare.com/cdn-cgi/challenge-platform/test/widget"
SCRIPT_URL = "https://challenges.cloudflare.com/turnstile/v0/api.js"
CLEAN = '<!DOCTYPE html><html><head><link rel="icon" href="data:,"></head><body></body></html>'
BUSY = f"""<!DOCTYPE html><html><head><link rel="icon" href="data:,"><script src="{SCRIPT_URL}"></script></head>
<body data-background="pending"><script>
fetch('/pending').then(() => document.body.dataset.background = 'done');
addEventListener('message', event => {{
    if (event.data === 'solved') document.body.dataset.clicks = Number(document.body.dataset.clicks || 0) + 1;
}});
</script><iframe style="border:0;width:300px;height:150px" src="{FRAME_URL}"></iframe></body></html>"""
WIDGET = """<!DOCTYPE html><html><body style="margin:0"><input type="checkbox" style="width:24px;height:24px;margin:16px"
onclick="this.dataset.clicks = Number(this.dataset.clicks || 0) + 1; parent.postMessage('solved', '*')"></body></html>"""
CLICKED = 'body[data-clicks="1"]'


def options() -> dict[str, Any]:
    return {
        "executable_path": getenv("SCRAPLING_EXECUTABLE_PATH"),
        "google_search": False,
        "solve_cloudflare": True,
        "retries": 1,
    }


def route_payload(url: str) -> tuple[str, str]:
    if url == SCRIPT_URL:
        return "application/javascript", ""
    if url == FRAME_URL:
        return "text/html", WIDGET
    return "text/html", BUSY if url == URL + "busy" else CLEAN


def setup_page(page: Page, pending: list[Route] | None = None) -> None:
    def fulfill(route: Route) -> None:
        if pending is not None and route.request.url == URL + "pending":
            pending.append(route)
            return
        content_type, body = route_payload(route.request.url)
        route.fulfill(content_type=content_type, body=body)

    page.route("**/*", fulfill)


async def setup_async_page(page: AsyncPage, pending: list[AsyncRoute] | None = None) -> None:
    async def fulfill(route: AsyncRoute) -> None:
        if pending is not None and route.request.url == URL + "pending":
            pending.append(route)
            return
        content_type, body = route_payload(route.request.url)
        await route.fulfill(content_type=content_type, body=body)

    await page.route("**/*", fulfill)


@pytest.mark.browser
def test_sync_widget_with_pending_request() -> None:
    pending: list[Route] = []
    with StealthySession(**options()) as session:
        response = session.fetch(URL + "busy", page_setup=partial(setup_page, pending=pending), wait_selector=CLICKED)
        page = session.page_pool.pages[0].page
        checkbox = page.frame_locator("iframe").locator('input[type="checkbox"]')
        assert checkbox.is_checked(), checkbox.get_attribute("data-clicks")
        assert checkbox.get_attribute("data-clicks") == "1"
        assert response.css(CLICKED + '[data-background="pending"]'), response.css("body")[0].attrib
        (request,) = pending
        request.fulfill(body="ok")
        page.locator('body[data-background="done"]').wait_for()

    assert page.is_closed()


@pytest.mark.browser
@pytest.mark.asyncio
async def test_async_widget_with_pending_request() -> None:
    pending: list[AsyncRoute] = []
    async with AsyncStealthySession(**options()) as session:
        response = await session.fetch(
            URL + "busy", page_setup=partial(setup_async_page, pending=pending), wait_selector=CLICKED
        )
        page = cast(AsyncPage, session.page_pool.pages[0].page)
        checkbox = page.frame_locator("iframe").locator('input[type="checkbox"]')
        assert await checkbox.is_checked(), await checkbox.get_attribute("data-clicks")
        assert await checkbox.get_attribute("data-clicks") == "1"
        assert response.css(CLICKED + '[data-background="pending"]'), response.css("body")[0].attrib
        (request,) = pending
        await request.fulfill(body="ok")
        await page.locator('body[data-background="done"]').wait_for()

    assert page.is_closed()


@pytest.mark.browser
@pytest.mark.parametrize("enabled", [False, True])
def test_sync_clean_page_grace_period(enabled: bool) -> None:
    with StealthySession(**options()) as session:
        with patch.object(session, "_cloudflare_solver", wraps=session._cloudflare_solver) as solve:
            response = session.fetch(URL + "clean", solve_cloudflare=enabled, page_setup=setup_page)
        assert solve.call_count == int(enabled)
        assert response.status == 200 and not response.css("iframe")
        page = session.page_pool.pages[0].page

    assert page.is_closed()


@pytest.mark.browser
@pytest.mark.asyncio
@pytest.mark.parametrize("enabled", [False, True])
async def test_async_clean_page_grace_period(enabled: bool) -> None:
    async with AsyncStealthySession(**options()) as session:
        with patch.object(session, "_cloudflare_solver", wraps=session._cloudflare_solver) as solve:
            response = await session.fetch(URL + "clean", solve_cloudflare=enabled, page_setup=setup_async_page)
        assert solve.await_count == int(enabled)
        assert response.status == 200 and not response.css("iframe")
        page = session.page_pool.pages[0].page

    assert page.is_closed()
