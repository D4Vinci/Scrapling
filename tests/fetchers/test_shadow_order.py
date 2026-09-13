from os import getenv
from pathlib import Path

import pytest
from playwright.async_api import async_playwright

from scrapling.engines.toolbelt.convertor import ResponseFactory
from scrapling.engines.toolbelt.custom import Response
from scrapling.parser import Selector
from scrapling.spiders.cache import ResponseCacheManager


async def extract(html: str, setup: str) -> Response:
    async with async_playwright() as driver:
        browser = await driver.chromium.launch(executable_path=getenv("SCRAPLING_EXECUTABLE_PATH"))
        try:
            page = await browser.new_page()
            await page.route(
                "**/*", lambda route: route.fulfill(status=200, content_type="text/html; charset=utf-8", body=html)
            )
            first = await page.goto("https://shadow.test/")
            assert first is not None
            await page.evaluate(setup)
            state = """() => {
                const roots = [];
                function collect(node) {
                    if (node.shadowRoot) {
                        roots.push([node.id, node.shadowRoot.innerHTML]);
                        collect(node.shadowRoot);
                    }
                    for (const child of node.children) collect(child);
                }
                collect(document.documentElement);
                return [document.documentElement.outerHTML, roots];
            }"""
            before = await page.evaluate(state)
            response = await ResponseFactory.from_async_playwright_response(page, first, None, {}, pierce_shadow=True)
            assert await page.evaluate(state) == before
            assert "data-scrapling-" not in response.body.decode()
            return response
        finally:
            await browser.close()


@pytest.mark.asyncio
async def test_shadow_slots_follow_composed_order(tmp_path: Path) -> None:
    response = await extract(
        '<html><body><main><p id="host">LIGHT-TEXT<span id="second" slot="second">SECOND</span><span id="first" slot="first">FIRST</span><b id="unused" slot="unused">UNUSED</b><i id="default">DEFAULT</i></p><slot id="ordinary"><b>ORDINARY-SLOT</b></slot></main></body></html>',
        """() => {
            document.querySelector('#host').attachShadow({mode: 'open'}).innerHTML = '<section id="rendered"><slot name="first">WRONG-FIRST</slot><em id="between">BETWEEN</em><slot name="second">WRONG-SECOND</slot><slot>WRONG-DEFAULT</slot><slot name="missing"><strong id="fallback">FALLBACK</strong></slot></section>';
        }""",
    )
    assert response.css("#host > shadow-root > #rendered")
    assert (
        response.css("#rendered")[0].get_all_text(separator="|", strip=True)
        == "FIRST|BETWEEN|SECOND|LIGHT-TEXT|DEFAULT|FALLBACK"
    )
    ordered = "#rendered > slot > *::attr(id), #rendered > em::attr(id)"
    assert response.css(ordered).getall() == ["first", "between", "second", "default", "fallback"]
    assert response.css("#rendered > slot:not([name])::text").get() == "LIGHT-TEXT"
    assert [node.tag for node in response.css("#rendered > *")] == ["slot", "em", "slot", "slot", "slot"]
    assert response.css("#host slot::attr(name)").getall() == ["first", "second", "missing"]
    assert not response.css("#unused")
    assert len(response.css("#first")) == len(response.css("#second")) == len(response.css("#default")) == 1
    assert response.css("main > slot#ordinary > b::text").get() == "ORDINARY-SLOT"
    assert (
        Selector(response.body).css("#rendered")[0].get_all_text(separator="|", strip=True)
        == "FIRST|BETWEEN|SECOND|LIGHT-TEXT|DEFAULT|FALLBACK"
    )
    cache = ResponseCacheManager(tmp_path)
    await cache.put(b"composed-order", response)
    restored = await cache.get(b"composed-order")
    assert restored is not None
    assert restored.body == response.body
    assert (
        restored.css("#host > shadow-root > #rendered")[0].get_all_text(separator="|", strip=True)
        == "FIRST|BETWEEN|SECOND|LIGHT-TEXT|DEFAULT|FALLBACK"
    )
    assert restored.css(ordered).getall() == ["first", "between", "second", "default", "fallback"]
    assert len(restored.css("#host slot")) == 4
    assert not restored.css("#unused")


@pytest.mark.asyncio
@pytest.mark.parametrize("assigned", [False, True])
async def test_shadow_forwarded_slots_and_nested_hosts(assigned: bool) -> None:
    value = (
        '<div id="value" slot="outer"><span id="leaf" slot="leaf">VALUE</span><p id="unused-nested" slot="unused">UNUSED-NESTED</p></div>'
        if assigned
        else ""
    )
    response = await extract(
        f'<html><body><div id="outer">{value}<small id="unused" slot="unused">UNUSED</small></div></body></html>',
        """() => {
            const value = document.querySelector('#value');
            if (value) value.attachShadow({mode: 'open'}).innerHTML = '<aside id="value-order"><slot name="leaf">WRONG-LEAF</slot></aside>';
            const root = document.querySelector('#outer').attachShadow({mode: 'open'});
            root.innerHTML = '<article id="outer-order"><b>OUTER-BEGIN</b><div id="inner"><slot name="outer" slot="inner">FORWARD-FALLBACK</slot></div><b>OUTER-END</b></article>';
            root.querySelector('#inner').attachShadow({mode: 'open'}).innerHTML = '<section id="inner-order"><i>INNER-BEGIN</i><slot name="inner">WRONG-INNER</slot><i>INNER-END</i></section>';
        }""",
    )
    expected = "VALUE" if assigned else "FORWARD-FALLBACK"
    assert (
        response.css("#outer > shadow-root > #outer-order")[0].get_all_text(separator="|", strip=True)
        == f"OUTER-BEGIN|INNER-BEGIN|{expected}|INNER-END|OUTER-END"
    )
    assert response.css("#outer-order > #inner > shadow-root > #inner-order")
    assert response.css("#inner-order > slot[name=inner] > slot[name=outer][slot=inner]")
    assert not response.css("#unused, #unused-nested")
    if assigned:
        assert (
            response.css(
                "#inner-order > slot > slot > #value > shadow-root > #value-order > slot[name=leaf] > #leaf::text"
            ).get()
            == "VALUE"
        )
        assert len(response.css("#value")) == len(response.css("#leaf")) == 1
    else:
        assert not response.css("#value")
