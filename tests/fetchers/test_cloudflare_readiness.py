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
PAGE = """<!DOCTYPE html><html><head><link rel="icon" href="data:,"></head><body>
<script>addEventListener('message', event => {
    if (event.data === 'solved') {
        document.body.dataset.clicks = Number(document.body.dataset.clicks || 0) + 1;
    }
});</script></body></html>"""
CHECKBOX = """<input type="checkbox" style="width:24px;height:24px;margin:16px"
onclick="this.dataset.clicks = Number(this.dataset.clicks || 0) + 1; parent.postMessage('solved', '*')">"""
WIDGET = f'<!DOCTYPE html><html><body style="margin:0">{CHECKBOX}</body></html>'
DELAYED_WIDGET = f"""<!DOCTYPE html><html><body style="margin:0"><script>
setTimeout(() => document.body.insertAdjacentHTML('beforeend', `{CHECKBOX}`), 700);
</script></body></html>"""
ADD_SCRIPT = f"""const script = document.createElement('script');
script.onload = () => document.body.dataset.scriptLoaded = 'true';
script.src = '{SCRIPT_URL}'; document.head.appendChild(script);"""
ADD_FRAME = f"""const frame = document.createElement('iframe');
frame.style = 'border:0;width:300px;height:150px'; frame.src = '{FRAME_URL}'; document.body.appendChild(frame);"""
SCRIPT = f'<script src="{SCRIPT_URL}"></script>'
FRAME = f'<iframe style="border:0;width:300px;height:150px" src="{FRAME_URL}"></iframe>'
BUSY = """<script>setInterval(() => fetch('/noise?' + Math.random()).then(response => response.text()).then(() => {
    document.body.dataset.background = Number(document.body.dataset.background || 0) + 1;
}), 100);</script>"""


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
    if url.startswith(FRAME_URL):
        return "text/html", DELAYED_WIDGET if url.endswith("?delayed") else WIDGET
    if url.startswith(URL + "noise?"):
        return "text/plain", "ok"
    content = {
        "delayed_script": f"<script>setTimeout(() => {{{ADD_SCRIPT}}}, 700); setTimeout(() => {{{ADD_FRAME}}}, 1300);</script>",
        "delayed_frame": SCRIPT + f"<script>setTimeout(() => {{{ADD_FRAME}}}, 900);</script>",
        "initial_checkbox": SCRIPT + FRAME.replace(FRAME_URL, FRAME_URL + "?delayed"),
        "busy": SCRIPT + FRAME + BUSY,
    }.get(url.removeprefix(URL), "")
    return "text/html", PAGE.replace("</body>", content + "</body>")


def setup_page(page: Page) -> None:
    def fulfill(route: Route) -> None:
        content_type, body = route_payload(route.request.url)
        route.fulfill(content_type=content_type, body=body)

    page.route("**/*", fulfill)


async def setup_async_page(page: AsyncPage) -> None:
    async def fulfill(route: AsyncRoute) -> None:
        content_type, body = route_payload(route.request.url)
        await route.fulfill(content_type=content_type, body=body)

    await page.route("**/*", fulfill)


def wait_for_solve(page: Page) -> None:
    page.frame_locator("iframe").locator('input[data-clicks="1"]:checked').wait_for(state="attached")
    page.wait_for_function("document.body.dataset.clicks === '1'")
    if page.url.endswith("/busy"):
        page.wait_for_function("Number(document.body.dataset.background) >= 2")


async def wait_for_async_solve(page: AsyncPage) -> None:
    await page.frame_locator("iframe").locator('input[data-clicks="1"]:checked').wait_for(state="attached")
    await page.wait_for_function("document.body.dataset.clicks === '1'")
    if page.url.endswith("/busy"):
        await page.wait_for_function("Number(document.body.dataset.background) >= 2")


@pytest.mark.browser
@pytest.mark.parametrize("case", ["delayed_script", "delayed_frame", "initial_checkbox", "busy"])
def test_sync_widget_readiness(case: str) -> None:
    with StealthySession(**options()) as session:
        response = session.fetch(URL + case, page_setup=setup_page, page_action=wait_for_solve)
        page = session.page_pool.pages[0].page
        checkbox = page.frame_locator("iframe").locator('input[type="checkbox"]')
        assert checkbox.is_checked(), checkbox.get_attribute("data-clicks")
        assert checkbox.get_attribute("data-clicks") == "1"
        assert response.css('body[data-clicks="1"]'), response.css("body")[0].attrib
        if case == "busy":
            assert int(response.css("body")[0].attrib.get("data-background", "0")) >= 2
        elif case == "delayed_script":
            assert response.css('body[data-script-loaded="true"]')

    assert page.is_closed()


@pytest.mark.browser
@pytest.mark.asyncio
@pytest.mark.parametrize("case", ["delayed_script", "delayed_frame", "initial_checkbox", "busy"])
async def test_async_widget_readiness(case: str) -> None:
    async with AsyncStealthySession(**options()) as session:
        response = await session.fetch(URL + case, page_setup=setup_async_page, page_action=wait_for_async_solve)
        page = cast(AsyncPage, session.page_pool.pages[0].page)
        checkbox = page.frame_locator("iframe").locator('input[type="checkbox"]')
        assert await checkbox.is_checked(), await checkbox.get_attribute("data-clicks")
        assert await checkbox.get_attribute("data-clicks") == "1"
        assert response.css('body[data-clicks="1"]'), response.css("body")[0].attrib
        if case == "busy":
            assert int(response.css("body")[0].attrib.get("data-background", "0")) >= 2
        elif case == "delayed_script":
            assert response.css('body[data-script-loaded="true"]')

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
