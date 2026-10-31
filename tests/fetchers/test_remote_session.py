from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from inspect import isawaitable
from os import getenv
from pathlib import Path
from subprocess import DEVNULL, Popen, TimeoutExpired
from threading import Thread
from time import monotonic, sleep
from unittest.mock import AsyncMock, Mock

import pytest
from patchright.async_api import async_playwright
from patchright.sync_api import sync_playwright

import scrapling.fetchers as fetchers
from scrapling.core._types import Any, Generator
from scrapling.engines._browsers import _stealth
from scrapling.engines._browsers._types import RemoteSessionParams, StealthSession
from scrapling.engines.toolbelt.proxy_rotation import ProxyRotator
from scrapling.fetchers import AsyncRemoteSession, AsyncStealthySession, RemoteSession, StealthySession


ENDPOINT = "http://127.0.0.1:9222"
HTML = b'<!doctype html><html><head><link rel="icon" href="data:,"></head><body><h1>Remote page</h1></body></html>'
SETTINGS = "({agent: navigator.userAgent, locale: navigator.language, timezone: Intl.DateTimeFormat().resolvedOptions().timeZone, width: innerWidth})"
REMOTE_OPTIONS: dict[str, Any] = {
    "useragent": "ScraplingRemoteTest/1",
    "locale": "fr-FR",
    "timezone_id": "Europe/Paris",
    "additional_args": {"viewport": {"width": 555, "height": 444}},
    "google_search": False,
    "retries": 1,
    "record_requests": True,
}
REMOTE_SETTINGS = {"agent": "ScraplingRemoteTest/1", "locale": "fr-FR", "timezone": "Europe/Paris", "width": 555}


async def _resolve(result: Any) -> Any:
    return await result if isawaitable(result) else result


def _browser(monkeypatch: pytest.MonkeyPatch, asynchronous: bool) -> tuple[Any, ...]:
    method = AsyncMock if asynchronous else Mock
    original, page = Mock(), Mock()
    for tab in (original, page):
        tab.is_closed.return_value = False
        for name in (
            "close",
            "set_extra_http_headers",
            "unroute_all",
            "route",
            "goto",
            "wait_for_load_state",
            "wait_for_timeout",
        ):
            setattr(tab, name, method())
    existing, created = Mock(pages=[original]), Mock(pages=[])
    for context in (existing, created):
        context.new_page = method(return_value=page)
        for name in ("close", "add_init_script", "add_cookies"):
            setattr(context, name, method())
    browser = Mock(contexts=[existing])
    browser.new_context, browser.close = method(return_value=created), method()
    driver = Mock()
    driver.chromium.connect_over_cdp, driver.stop = method(return_value=browser), method()
    factory = Mock()
    factory.return_value.start = method(return_value=driver)
    monkeypatch.setattr(_stealth, "async_playwright" if asynchronous else "sync_playwright", factory)
    return driver, browser, existing, created, original, page


def test_remote_exports() -> None:
    assert issubclass(RemoteSession, StealthySession)
    assert issubclass(AsyncRemoteSession, AsyncStealthySession)
    assert {"RemoteSession", "AsyncRemoteSession"} <= set(fetchers.__all__)
    assert not hasattr(fetchers, "RemoteFetcher")


def test_remote_option_types_exclude_real_chrome() -> None:
    assert RemoteSessionParams.__optional_keys__ == StealthSession.__optional_keys__ - {"real_chrome"}


@pytest.mark.parametrize("session_type", [RemoteSession, AsyncRemoteSession])
@pytest.mark.parametrize("new_context", [False, True])
@pytest.mark.parametrize("real_chrome", [False, True])
def test_remote_rejects_real_chrome(session_type: Any, new_context: bool, real_chrome: bool) -> None:
    with pytest.raises(TypeError, match="do not accept real_chrome"):
        session_type(ENDPOINT, new_context=new_context, real_chrome=real_chrome)


@pytest.mark.parametrize("session_type", [StealthySession, AsyncStealthySession])
@pytest.mark.parametrize("real_chrome", [False, True])
def test_local_sessions_keep_real_chrome(session_type: Any, real_chrome: bool) -> None:
    assert session_type(real_chrome=real_chrome)._config.real_chrome is real_chrome


@pytest.mark.parametrize("session_type", [RemoteSession, AsyncRemoteSession])
def test_remote_requires_endpoint_and_keyword_context_option(session_type: Any) -> None:
    with pytest.raises(TypeError, match="cdp_url"):
        session_type()
    with pytest.raises(TypeError):
        session_type(ENDPOINT, False)
    assert session_type(ENDPOINT)._config.new_context is True


@pytest.mark.parametrize("session_type", [RemoteSession, AsyncRemoteSession])
@pytest.mark.parametrize("endpoint", [None, "", "invalid", "ftp://localhost:9222", "http://"])
def test_remote_rejects_invalid_endpoint(session_type: Any, endpoint: Any) -> None:
    with pytest.raises(TypeError):
        session_type(endpoint)


@pytest.mark.parametrize("session_type", [RemoteSession, AsyncRemoteSession])
@pytest.mark.parametrize("scheme", ["http", "https", "ws", "wss"])
def test_remote_accepts_endpoint_schemes(session_type: Any, scheme: str) -> None:
    endpoint = f"{scheme}://localhost:9222"
    assert session_type(endpoint)._config.cdp_url == endpoint


@pytest.mark.parametrize("session_type", [StealthySession, AsyncStealthySession])
@pytest.mark.parametrize("endpoint", [None, ENDPOINT])
def test_local_sessions_reject_cdp_with_migration_hint(session_type: Any, endpoint: Any) -> None:
    with pytest.raises(TypeError, match="RemoteSession"):
        session_type(cdp_url=endpoint)


@pytest.mark.parametrize("session_type", [RemoteSession, AsyncRemoteSession])
def test_borrowed_context_ignores_context_settings(session_type: Any) -> None:
    session = session_type(
        ENDPOINT,
        new_context=False,
        useragent="Ignored agent",
        locale="fr-FR",
        timezone_id="Europe/Paris",
        proxy="http://localhost:1",
        proxy_rotator=ProxyRotator(["http://localhost:2"]),
        additional_args={"viewport": {"width": 1, "height": 1}},
        timeout=1500,
        extra_headers={"X-Test": "kept"},
    )
    for name in ("useragent", "locale", "timezone_id", "proxy", "proxy_rotator", "additional_args"):
        assert not getattr(session._config, name)
    assert session._config.timeout == 1500
    assert session._config.extra_headers == {"X-Test": "kept"}


@pytest.mark.asyncio
@pytest.mark.parametrize("asynchronous", [False, True])
@pytest.mark.parametrize("new_context", [False, True])
async def test_remote_context_ownership_and_page_cleanup(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, asynchronous: bool, new_context: bool
) -> None:
    driver, browser, existing, created, original, page = _browser(monkeypatch, asynchronous)
    script = tmp_path / "init.js"
    script.write_text("window.remoteSession = true;")
    cookies = [{"name": "session", "value": "kept", "url": "https://example.test"}]
    session_type: Any = AsyncRemoteSession if asynchronous else RemoteSession
    session = session_type(
        ENDPOINT,
        new_context=new_context,
        locale="fr-FR",
        cookies=cookies,
        init_script=str(script),
        record_requests=True,
    )
    await _resolve(session.start())
    context = created if new_context else existing
    assert session.context is context
    driver.chromium.connect_over_cdp.assert_called_once_with(endpoint_url=ENDPOINT, no_defaults=True)
    driver.chromium.launch.assert_not_called()
    driver.chromium.launch_persistent_context.assert_not_called()
    if new_context:
        assert browser.new_context.call_args.kwargs["locale"] == "fr-FR"
    else:
        browser.new_context.assert_not_called()
    context.add_cookies.assert_called_once_with(cookies)
    context.add_init_script.assert_called_once_with(path=str(script))
    await _resolve(session._get_page(1234, {"X-Test": "kept"}, True))
    page.set_default_timeout.assert_called_once_with(1234)
    page.set_extra_http_headers.assert_called_once_with({"X-Test": "kept"})
    page.route.assert_called_once()
    await _resolve(session.close())
    await _resolve(session.close())
    page.close.assert_called_once_with()
    original.close.assert_not_called()
    existing.close.assert_not_called()
    assert created.close.call_count == int(new_context)
    browser.close.assert_called_once_with()
    driver.stop.assert_called_once_with()
    assert session.context is session.browser is session.playwright is None
    assert not session._is_alive and not session.network._contexts
    assert {call.args[0] for call in context.remove_listener.call_args_list} == {"requestfinished", "close"}


@pytest.mark.asyncio
@pytest.mark.parametrize("asynchronous", [False, True])
async def test_borrowed_context_requires_an_existing_context(
    monkeypatch: pytest.MonkeyPatch, asynchronous: bool
) -> None:
    driver, browser, existing, created, original, page = _browser(monkeypatch, asynchronous)
    browser.contexts = []
    session_type: Any = AsyncRemoteSession if asynchronous else RemoteSession
    session = session_type(ENDPOINT, new_context=False)
    with pytest.raises(RuntimeError, match="context"):
        await _resolve(session.start())
    browser.new_context.assert_not_called()
    driver.stop.assert_called_once_with()
    assert not session._is_alive and session.playwright is None


@pytest.mark.asyncio
@pytest.mark.parametrize("asynchronous", [False, True])
@pytest.mark.parametrize("new_context", [False, True])
async def test_failed_context_setup_cleans_up_only_owned_resources(
    monkeypatch: pytest.MonkeyPatch, asynchronous: bool, new_context: bool
) -> None:
    driver, browser, existing, created, original, page = _browser(monkeypatch, asynchronous)
    context = created if new_context else existing
    context.add_cookies.side_effect = RuntimeError("Cookie setup failed")
    session_type: Any = AsyncRemoteSession if asynchronous else RemoteSession
    session = session_type(
        ENDPOINT, new_context=new_context, cookies=[{"name": "test", "value": "value", "url": "https://example.test"}]
    )
    with pytest.raises(RuntimeError, match="Cookie setup failed"):
        await _resolve(session.start())
    existing.close.assert_not_called()
    original.close.assert_not_called()
    assert created.close.call_count == int(new_context)
    driver.stop.assert_called_once_with()
    assert not session._is_alive and session.playwright is None


@pytest.mark.asyncio
@pytest.mark.parametrize("asynchronous", [False, True])
async def test_borrowed_fetch_ignores_proxy_overrides(monkeypatch: pytest.MonkeyPatch, asynchronous: bool) -> None:
    driver, browser, existing, created, original, page = _browser(monkeypatch, asynchronous)
    rotator = ProxyRotator(["http://localhost:1"])
    get_proxy = Mock(wraps=rotator.get_proxy)
    monkeypatch.setattr(ProxyRotator, "get_proxy", get_proxy)
    factory = AsyncMock() if asynchronous else Mock()
    monkeypatch.setattr(
        _stealth.ResponseFactory,
        "from_async_playwright_response" if asynchronous else "from_playwright_response",
        factory,
    )
    session_type: Any = AsyncRemoteSession if asynchronous else RemoteSession
    session = session_type(ENDPOINT, new_context=False, proxy_rotator=rotator, retries=1)
    await _resolve(session.start())
    try:
        await _resolve(session.fetch("https://example.test", proxy="http://localhost:2"))
        await _resolve(session.fetch("https://example.test"))
        assert existing.new_page.call_count == 1
        browser.new_context.assert_not_called()
        get_proxy.assert_not_called()
        assert all(call.kwargs["meta"]["proxy"] is None for call in factory.call_args_list)
    finally:
        await _resolve(session.close())


@pytest.mark.asyncio
@pytest.mark.parametrize("asynchronous", [False, True])
async def test_owned_remote_fetch_keeps_proxy_rotation(monkeypatch: pytest.MonkeyPatch, asynchronous: bool) -> None:
    driver, browser, existing, created, original, page = _browser(monkeypatch, asynchronous)
    factory = AsyncMock() if asynchronous else Mock()
    monkeypatch.setattr(
        _stealth.ResponseFactory,
        "from_async_playwright_response" if asynchronous else "from_playwright_response",
        factory,
    )
    session_type: Any = AsyncRemoteSession if asynchronous else RemoteSession
    session = session_type(ENDPOINT, proxy_rotator=ProxyRotator(["http://localhost:1"]), retries=1)
    await _resolve(session.start())
    try:
        browser.new_context.assert_not_called()
        await _resolve(session.fetch("https://example.test"))
        await _resolve(session.fetch("https://example.test", proxy="http://localhost:2"))
        assert [call.kwargs["proxy"]["server"] for call in browser.new_context.call_args_list] == [
            "http://localhost:1",
            "http://localhost:2",
        ]
        assert created.close.call_count == 2
        assert session.page_pool.pages_count == 0
        existing.close.assert_not_called()
    finally:
        await _resolve(session.close())


@pytest.mark.asyncio
@pytest.mark.parametrize("asynchronous", [False, True])
async def test_remote_disconnects_when_owned_context_close_fails(
    monkeypatch: pytest.MonkeyPatch, asynchronous: bool
) -> None:
    driver, browser, existing, created, original, page = _browser(monkeypatch, asynchronous)
    session_type: Any = AsyncRemoteSession if asynchronous else RemoteSession
    session = session_type(ENDPOINT)
    await _resolve(session.start())
    created.close.side_effect = RuntimeError("Context close failed")
    with pytest.raises(RuntimeError, match="Context close failed"):
        await _resolve(session.close())
    browser.close.assert_called_once_with()
    driver.stop.assert_called_once_with()
    existing.close.assert_not_called()
    assert not session._is_alive


class _Handler(BaseHTTPRequestHandler):
    def log_message(self, format: str, *args: Any) -> None:
        pass

    def do_GET(self) -> None:
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(HTML)))
        self.end_headers()
        self.wfile.write(HTML)


@pytest.fixture
def remote_browser(tmp_path: Path) -> Generator[tuple[str, str], None, None]:
    with ThreadingHTTPServer(("127.0.0.1", 0), _Handler) as server:
        thread = Thread(target=server.serve_forever, daemon=True)
        thread.start()
        process = None
        try:
            with sync_playwright() as playwright:
                process = Popen(
                    [
                        getenv("SCRAPLING_EXECUTABLE_PATH") or playwright.chromium.executable_path,
                        "--headless=new",
                        "--no-sandbox",
                        "--no-first-run",
                        "--no-default-browser-check",
                        "--use-mock-keychain",
                        "--password-store=basic",
                        "--remote-debugging-port=0",
                        f"--user-data-dir={tmp_path / 'profile'}",
                        "about:blank",
                    ],
                    stdout=DEVNULL,
                    stderr=DEVNULL,
                )
                port_file = tmp_path / "profile" / "DevToolsActivePort"
                deadline = monotonic() + 20
                while not port_file.exists():
                    if process.poll() is not None or monotonic() >= deadline:
                        pytest.fail("Disposable CDP browser did not start")
                    sleep(0.05)
                endpoint = f"http://127.0.0.1:{port_file.read_text().splitlines()[0]}"
                playwright.chromium.connect_over_cdp(endpoint, no_defaults=True, timeout=10000).close()
            yield endpoint, f"http://127.0.0.1:{server.server_port}"
        finally:
            if process is not None:
                process.terminate()
                try:
                    process.wait(timeout=5)
                except TimeoutExpired:
                    process.kill()
                    process.wait(timeout=5)
            server.shutdown()
            thread.join(timeout=5)


@pytest.mark.browser
@pytest.mark.parametrize("new_context", [False, True])
def test_sync_remote_browser_preserves_external_context(remote_browser: tuple[str, str], new_context: bool) -> None:
    endpoint, url = remote_browser
    with sync_playwright() as playwright:
        browser = playwright.chromium.connect_over_cdp(endpoint, no_defaults=True)
        original = browser.contexts[0].pages[0]
        original.goto(f"{url}/original")
        original.evaluate("localStorage.setItem('login', 'saved')")
        settings = original.evaluate(SETTINGS)
        browser.close()
    with RemoteSession(endpoint, new_context=new_context, **REMOTE_OPTIONS) as session:
        response = session.fetch(f"{url}/fetch", **({"proxy": "http://127.0.0.1:1"} if not new_context else {}))
        assert response.status == 200 and response.css("h1::text").get() == "Remote page"
        owned_page = session.context.pages[-1]
        assert owned_page.evaluate("localStorage.getItem('login')") == (None if new_context else "saved")
        assert owned_page.evaluate(SETTINGS) == (REMOTE_SETTINGS if new_context else settings)
        original = next(
            page for context in session.browser.contexts for page in context.pages if page.url == f"{url}/original"
        )
        assert original.evaluate(SETTINGS) == settings
        cdp = session.browser.new_browser_cdp_session()
        assert len(cdp.send("Target.getBrowserContexts")["browserContextIds"]) == int(new_context)
        cdp.detach()
    with sync_playwright() as playwright:
        browser = playwright.chromium.connect_over_cdp(endpoint, no_defaults=True)
        assert len(browser.contexts) == 1 and len(browser.contexts[0].pages) == 1
        original = browser.contexts[0].pages[0]
        assert original.url == f"{url}/original"
        assert original.evaluate("localStorage.getItem('login')") == "saved"
        assert original.evaluate(SETTINGS) == settings
        browser.close()


@pytest.mark.browser
@pytest.mark.asyncio
@pytest.mark.parametrize("new_context", [False, True])
async def test_async_remote_browser_preserves_external_context(
    remote_browser: tuple[str, str], new_context: bool
) -> None:
    endpoint, url = remote_browser
    async with async_playwright() as playwright:
        browser = await playwright.chromium.connect_over_cdp(endpoint, no_defaults=True)
        original = browser.contexts[0].pages[0]
        await original.goto(f"{url}/original")
        await original.evaluate("localStorage.setItem('login', 'saved')")
        settings = await original.evaluate(SETTINGS)
        await browser.close()
    async with AsyncRemoteSession(endpoint, new_context=new_context, **REMOTE_OPTIONS) as session:
        response = await session.fetch(f"{url}/fetch", **({"proxy": "http://127.0.0.1:1"} if not new_context else {}))
        assert response.status == 200 and response.css("h1::text").get() == "Remote page"
        owned_page = session.context.pages[-1]
        assert await owned_page.evaluate("localStorage.getItem('login')") == (None if new_context else "saved")
        assert await owned_page.evaluate(SETTINGS) == (REMOTE_SETTINGS if new_context else settings)
        original = next(
            page for context in session.browser.contexts for page in context.pages if page.url == f"{url}/original"
        )
        assert await original.evaluate(SETTINGS) == settings
        cdp = await session.browser.new_browser_cdp_session()
        assert len((await cdp.send("Target.getBrowserContexts"))["browserContextIds"]) == int(new_context)
        await cdp.detach()
    async with async_playwright() as playwright:
        browser = await playwright.chromium.connect_over_cdp(endpoint, no_defaults=True)
        assert len(browser.contexts) == 1 and len(browser.contexts[0].pages) == 1
        original = browser.contexts[0].pages[0]
        assert original.url == f"{url}/original"
        assert await original.evaluate("localStorage.getItem('login')") == "saved"
        assert await original.evaluate(SETTINGS) == settings
        await browser.close()
