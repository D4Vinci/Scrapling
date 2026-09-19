from os import getenv

import pytest
from playwright.async_api import async_playwright

from scrapling.engines.toolbelt.convertor import SHADOW_SNAPSHOT_JS, ResponseFactory


@pytest.mark.asyncio
async def test_shadow_snapshot_preserves_source_content() -> None:
    async with async_playwright() as driver:
        browser = await driver.chromium.launch(executable_path=getenv("SCRAPLING_EXECUTABLE_PATH"))
        try:
            page = await browser.new_page()
            await page.route(
                "**/*",
                lambda route: route.fulfill(
                    status=200,
                    content_type="text/html; charset=utf-8",
                    body='<!DOCTYPE html><html lang="en"><head></head><body><p id="host"><span slot="label">ASSIGNED</span></p></body></html>',
                ),
            )
            first = await page.goto("https://shadow.test/")
            assert first is not None
            baseline = await page.content()
            plain = await ResponseFactory.from_async_playwright_response(page, first, None, {}, pierce_shadow=True)
            assert plain.body.decode() == baseline
            await page.evaluate("""() => {
                const root = document.querySelector('#host').attachShadow({mode: 'open'});
                root.innerHTML = '<div id="inside">SHADOW<slot name="label">WRONG-FALLBACK</slot><slot name="missing">USED-FALLBACK</slot><div id="nested"></div><svg viewBox="0 0 10 10"><path d="M0 0"/></svg></div>';
                let host = root.querySelector('#nested');
                for (let i = 0; i < 4; i++) {
                    const nested = host.attachShadow({mode: 'open'});
                    nested.innerHTML = `<p id="level-${i}">LEVEL-${i}</p><div></div>`;
                    host = nested.querySelector('div');
                }
                const script = document.createElement('script');
                script.id = 'data';
                script.type = 'application/ld+json';
                script.textContent = JSON.stringify({name: 'A&B<C>', title: 'Bürger'});
                root.append(script);
                const nul = document.createElement('span');
                nul.id = 'nul';
                nul.textContent = 'A' + String.fromCharCode(0) + 'B';
                root.append(nul);
                const noscript = document.createElement('noscript');
                noscript.id = 'noscript';
                noscript.textContent = '<p>NOSCRIPT-TEXT</p>';
                document.body.append(noscript, document.createComment('KEEP-COMMENT'));
                const template = document.createElement('template');
                template.id = 'ordinary';
                template.innerHTML = '<p>INACTIVE</p><div id="inactive-host"></div>';
                template.content.querySelector('div').attachShadow({mode: 'open'}).innerHTML = '<p>INACTIVE-ROOT</p>';
                root.append(template);
                const fake = document.createElement('template');
                fake.setAttribute('shadowrootmode', 'open');
                fake.innerHTML = '<p>FAKE-SHADOW</p>';
                document.body.append(fake);
                globalThis.shadowConstructed = 0;
                customElements.define('shadow-global-counter', class extends HTMLElement {
                    constructor() { super(); globalThis.shadowConstructed++; }
                });
                customElements.define('shadow-root', class extends HTMLElement {
                    constructor() { super(); globalThis.shadowConstructed++; }
                });
                root.append(document.createElement('shadow-global-counter'));
                if (typeof CustomElementRegistry === 'function') {
                    const registry = new CustomElementRegistry();
                    registry.define('shadow-scoped-counter', class extends HTMLElement {
                        constructor() { super(); globalThis.shadowConstructed++; }
                    });
                    const scopedHost = document.createElement('div');
                    root.append(scopedHost);
                    scopedHost.attachShadow({mode: 'open', customElementRegistry: registry}).innerHTML = '<shadow-scoped-counter>SCOPED-VALUE</shadow-scoped-counter>';
                }
            }""")
            before = await page.content()
            shadow_before = await page.locator("#host").evaluate("node => node.shadowRoot.innerHTML")
            count = await page.evaluate("globalThis.shadowConstructed")
            noscript = await page.locator("#noscript").evaluate("node => node.outerHTML")
            response = await ResponseFactory.from_async_playwright_response(
                page, first, None, {"keep_comments": True}, pierce_shadow=True
            )
            assert await page.content() == before
            assert await page.locator("#host").evaluate("node => node.shadowRoot.innerHTML") == shadow_before
            assert await page.evaluate("globalThis.shadowConstructed") == count
            assert response.css("#host > shadow-root > #inside").get()
            assert all(response.css(f"#level-{i}::text").get() == f"LEVEL-{i}" for i in range(4))
            assert response.css("#data::text").get() == '{"name":"A&B<C>","title":"Bürger"}'
            assert response.css("#nul::text").get() == "AB"
            assert response.css("svg path")
            assert response.body.startswith(b'<!DOCTYPE html><html lang="en">')
            assert noscript in response.body.decode()
            assert "<!--KEEP-COMMENT-->" in response.body.decode()
            assert len(response.xpath("//comment()")) == 1
            assert "data-scrapling-" not in response.html_content
            assert "data-scrapling-" not in response.body.decode()
            assert response.css("#host > shadow-root > #inside > slot[name=label] > span[slot]::text").getall() == [
                "ASSIGNED"
            ]
            assert "WRONG-FALLBACK" not in response.body.decode()
            assert "USED-FALLBACK" in response.body.decode()
            assert response.css("#ordinary p::text").get() == "INACTIVE"
            assert "INACTIVE-ROOT" not in response.body.decode()
            markdown = response.markdown()
            assert "LEVEL-3" in markdown
            assert "INACTIVE" not in markdown
            assert "FAKE-SHADOW" not in markdown
            if await page.evaluate("typeof CustomElementRegistry === 'function'"):
                assert response.css("shadow-scoped-counter::text").get() == "SCOPED-VALUE"
            await page.set_content(
                '<!DOCTYPE html><html><body><template id="only"><div></div></template></body></html>'
            )
            await page.evaluate(
                "document.querySelector('#only').content.querySelector('div').attachShadow({mode:'open'}).innerHTML='<p>HIDDEN-ROOT</p>'"
            )
            assert await page.evaluate(SHADOW_SNAPSHOT_JS) is None
            await page.evaluate("document.body.appendChild(document.createElement('div')).attachShadow({mode:'open'})")
            empty = await ResponseFactory.from_async_playwright_response(page, first, None, {}, pierce_shadow=True)
            assert empty.css("body > div > shadow-root")
            assert not empty.css("body > div > shadow-root")[0].children
        finally:
            await browser.close()
