from os import getenv

import pytest
from playwright.async_api import async_playwright

from scrapling.engines.toolbelt.convertor import ResponseFactory


async def extract(html: str, setup: str = "", wait_frame: str = ""):
    async with async_playwright() as driver:
        browser = await driver.chromium.launch(executable_path=getenv("SCRAPLING_EXECUTABLE_PATH"))
        try:
            page = await browser.new_page()
            await page.route(
                "**/*", lambda route: route.fulfill(status=200, content_type="text/html; charset=utf-8", body=html)
            )
            first = await page.goto("https://shadow.test/")
            assert first is not None
            if setup:
                await page.evaluate(setup)
            if wait_frame:  # srcdoc frames load asynchronously; wait for their content
                await page.wait_for_function(wait_frame)
            before = await page.content()
            response = await ResponseFactory.from_async_playwright_response(page, first, None, {}, pierce_shadow=True)
            assert await page.content() == before  # live DOM untouched
            return response
        finally:
            await browser.close()


@pytest.mark.asyncio
async def test_same_origin_iframe_content_is_preserved() -> None:
    """srcdoc iframes keep their document in the snapshot, after the iframe element.

    Note: nested <head>/<body> tags are structural to HTML parsers and get dissolved
    on re-parse, so frame content is queried with descendant selectors.
    """
    response = await extract(
        "<html><body>"
        "<div id='app'></div>"
        "<iframe id='editor' srcdoc='<html><body><p id=\"inside\">FRAME-TEXT</p></body></html>'></iframe>"
        "</body></html>",
        "() => { document.querySelector('#app').attachShadow({mode: 'open'}).innerHTML = '<span id=\"s\">S</span>'; }",
        "() => { const d = document.querySelector('#editor').contentDocument; return d && !!d.querySelector('#inside'); }",
    )
    assert response.css("#editor + iframe-document #inside::text").get() == "FRAME-TEXT"


@pytest.mark.asyncio
async def test_shadow_inside_iframe_is_pierced() -> None:
    """Open shadow roots inside a same-origin frame are pierced like any other."""
    response = await extract(
        "<html><body>"
        "<div id='app'></div>"
        "<iframe id='fr' srcdoc='<html><body><captcha-widget></captcha-widget></body></html>'></iframe>"
        "</body></html>",
        """() => {
            document.querySelector('#app').attachShadow({mode: 'open'}).innerHTML = '<span id=\"s\">S</span>';
            const w = document.querySelector('#fr').contentDocument.querySelector('captcha-widget');
            w.attachShadow({mode: 'open'}).innerHTML = '<b id=\"token\">TOKEN-9F3K2</b>';
        }""",
        "() => { const d = document.querySelector('#fr').contentDocument; "
        "return d && d.querySelector('captcha-widget') && !!d.querySelector('captcha-widget').shadowRoot; }",
    )
    assert response.css("#fr + iframe-document captcha-widget > shadow-root > #token::text").get() == "TOKEN-9F3K2"


@pytest.mark.asyncio
async def test_nested_iframe_recursion() -> None:
    """Frames inside frames are traversed recursively (srcdoc set via JS to avoid attribute escaping)."""
    async with async_playwright() as driver:
        browser = await driver.chromium.launch(executable_path=getenv("SCRAPLING_EXECUTABLE_PATH"))
        try:
            page = await browser.new_page()
            await page.route(
                "**/*",
                lambda route: route.fulfill(
                    status=200,
                    content_type="text/html; charset=utf-8",
                    body="<html><body><div id='app'></div><iframe id='l1'></iframe></body></html>",
                ),
            )
            first = await page.goto("https://shadow.test/")
            assert first is not None
            await page.evaluate(
                """() => {
                    document.querySelector('#app').attachShadow({mode: 'open'}).innerHTML = '<span id=\"s\">S</span>';
                    document.querySelector('#l1').srcdoc = \"<html><body><iframe id='l2'></iframe></body></html>\";
                }"""
            )
            await page.wait_for_function(
                "() => { const d = document.querySelector('#l1').contentDocument; return d && !!d.querySelector('#l2'); }"
            )
            await page.evaluate(
                """() => {
                    document.querySelector('#l1').contentDocument.querySelector('#l2').srcdoc =
                        \"<html><body><i id='deep'>DEEP-VALUE</i></body></html>\";
                }"""
            )
            await page.wait_for_function(
                """() => {
                    const d1 = document.querySelector('#l1').contentDocument;
                    const d2 = d1.querySelector('#l2').contentDocument;
                    return d2 && !!d2.querySelector('#deep');
                }"""
            )
            before = await page.content()
            response = await ResponseFactory.from_async_playwright_response(page, first, None, {}, pierce_shadow=True)
            assert await page.content() == before
            hits = response.css("iframe-document iframe-document #deep::text").getall()
            assert "DEEP-VALUE" in hits
        finally:
            await browser.close()


@pytest.mark.asyncio
async def test_cross_origin_iframe_is_skipped_without_error() -> None:
    """Cross-origin frames stay a documented boundary: no crash, no fake content."""
    response = await extract(
        "<html><body>"
        "<div id='app'></div>"
        "<iframe id='ext' src='https://example.invalid/'></iframe>"
        "</body></html>",
        "() => { document.querySelector('#app').attachShadow({mode: 'open'}).innerHTML = '<span id=\"s\">S</span>'; }",
    )
    assert response.css("#app > shadow-root > #s::text").get() == "S"
    assert not response.css("#ext + iframe-document")
