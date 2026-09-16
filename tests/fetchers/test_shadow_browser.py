from os import getenv

import pytest

from scrapling.core._types import Any
from scrapling.engines.toolbelt.custom import Response
from scrapling.fetchers import AsyncDynamicSession, AsyncStealthySession, DynamicSession, StealthySession


HTML = """<!DOCTYPE html><html><head><title>Shadow test</title></head><body>
<p id="host"><span slot="label">Assigned label</span></p><div id="closed"></div>
<template><p>Inactive template</p></template>
<script>
const host = document.querySelector('#host');
const root = host.attachShadow({mode: 'open'});
root.innerHTML = '<section id="shadow"><h2>Shadow title</h2><slot name="label">Wrong fallback</slot><slot name="empty">Fallback label</slot><div id="nested"></div><p aria-hidden="true">Hidden instructions</p><template>Inactive shadow template</template></section>';
root.querySelector('#nested').attachShadow({mode: 'open'}).innerHTML = '<a href="/nested">Nested link</a>';
document.querySelector('#closed').attachShadow({mode: 'closed'}).innerHTML = '<p>Closed secret</p>';
</script></body></html>"""


def check_response(response: Response) -> None:
    assert response.css("#host #shadow h2::text").get() == "Shadow title"
    assert response.xpath('//*[@id="host"]//*[@id="nested"]/shadow-root/a/text()').get() == "Nested link"
    assert len(response.css("#host span")) == 1
    assert "Assigned label" in response.markdown()
    assert "Fallback label" in response.markdown()
    assert "Wrong fallback" not in response.css("#host").get("")
    assert not response.css("#closed p")
    markdown = response.markdown(css_selector="#host #shadow")
    assert "Shadow title" in markdown
    assert "Nested link" in markdown
    assert markdown.index("Shadow title") < markdown.index("Assigned label") < markdown.index("Fallback label")
    assert response.css("#host slot::attr(name)").getall() == ["label", "empty"]
    assert "Hidden instructions" not in markdown
    assert "Inactive shadow template" not in markdown
    assert response.status == 200
    assert response.encoding == "utf-8"
    assert response.url == "https://shadow.test/"
    assert isinstance(response.body, bytes) and response.body


def setup_page(page: Any) -> None:
    page.route("**/*", lambda route: route.fulfill(status=200, content_type="text/html", body=HTML))


async def setup_async_page(page: Any) -> None:
    await page.route("**/*", lambda route: route.fulfill(status=200, content_type="text/html", body=HTML))


@pytest.mark.parametrize("session_type", [DynamicSession, StealthySession])
def test_sync_shadow_browser(session_type: Any) -> None:
    with session_type(
        executable_path=getenv("SCRAPLING_EXECUTABLE_PATH"),
        google_search=False,
        pierce_shadow=True,
        page_setup=setup_page,
    ) as session:
        check_response(session.fetch("https://shadow.test/"))
        assert not session.fetch("https://shadow.test/", pierce_shadow=False).css("#shadow")


@pytest.mark.asyncio
@pytest.mark.parametrize("session_type", [AsyncDynamicSession, AsyncStealthySession])
async def test_async_shadow_browser(session_type: Any) -> None:
    async with session_type(
        executable_path=getenv("SCRAPLING_EXECUTABLE_PATH"),
        google_search=False,
        pierce_shadow=True,
        page_setup=setup_async_page,
    ) as session:
        check_response(await session.fetch("https://shadow.test/"))
        assert not (await session.fetch("https://shadow.test/", pierce_shadow=False)).css("#shadow")
