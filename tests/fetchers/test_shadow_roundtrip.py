from os import getenv

import pytest
from playwright.async_api import async_playwright

from scrapling.core._types import extraction_types
from scrapling.core.shell import Convertor
from scrapling.engines.toolbelt.convertor import ResponseFactory
from scrapling.engines.toolbelt.custom import Response
from scrapling.parser import Selector


def check_roundtrip(content: bytes) -> None:
    response = Response("https://shadow.test/", content, 200, "OK", {}, {}, {})
    kinds: tuple[extraction_types, ...] = ("html", "text", "markdown")
    for parsed in (Selector(content), response, Selector(response.html_content)):
        assert parsed.css("#host > shadow-root > #rendered")
        assert parsed.css("#nested > shadow-root > #leaf::text").get() == "LEAF"
        assert parsed.css("#host")[0].get_all_text(separator="|", strip=True) == "FIRST|LEAF|LAST"
        assert parsed.css("#rendered > *::attr(id)").getall() == ["first", "nested", "last"]
        for kind in kinds:
            output = "".join(Convertor._extract_content(parsed, kind, main_content_only=True))
            assert output.index("FIRST") < output.index("LEAF") < output.index("LAST")
    markdown = response.markdown(css_selector="#host")
    assert markdown.index("FIRST") < markdown.index("LEAF") < markdown.index("LAST")
    assert response.body == content


@pytest.mark.asyncio
async def test_shadow_wrappers_roundtrip_across_host_tags() -> None:
    async with async_playwright() as driver:
        browser = await driver.chromium.launch(executable_path=getenv("SCRAPLING_EXECUTABLE_PATH"))
        try:
            page = await browser.new_page()
            content = ""
            await page.route(
                "**/*",
                lambda route: route.fulfill(status=200, content_type="text/html; charset=utf-8", body=content),
            )
            for tag in ("p", "h1", "h2", "h3", "h4", "h5", "h6", "div", "body", "shadow-card"):
                host = f'<{tag} id="host"><span>UNUSED-LIGHT</span></{tag}>'
                content = f"<html><head></head>{host if tag == 'body' else f'<body>{host}</body>'}</html>"
                first = await page.goto("https://shadow.test/")
                assert first is not None
                await page.evaluate("""() => {
                    const root = document.querySelector('#host').attachShadow({mode: 'open'});
                    root.innerHTML = '<section id="rendered"><span id="first">FIRST</span><p id="nested"></p><span id="last">LAST</span></section>';
                    root.querySelector('#nested').attachShadow({mode: 'open'}).innerHTML = '<div id="leaf">LEAF</div>';
                }""")
                before = await page.content()
                response = await ResponseFactory.from_async_playwright_response(
                    page, first, None, {}, pierce_shadow=True
                )
                assert await page.content() == before
                assert response.css(f"{tag}#host > shadow-root > #rendered")
                assert "UNUSED-LIGHT" not in response.body.decode()
                check_roundtrip(response.body)
        finally:
            await browser.close()
