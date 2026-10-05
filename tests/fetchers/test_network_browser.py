import asyncio
from base64 import b64decode
from contextlib import suppress
from dataclasses import dataclass, field
from gzip import compress
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from json import loads
from os import getenv
from socket import SHUT_RDWR
from threading import Event, Thread
from time import monotonic
from unittest.mock import Mock
from urllib.parse import urlsplit

import pytest
from patchright.async_api import Response as AsyncPatchrightResponse
from patchright.sync_api import Response as PatchrightResponse
from playwright.async_api import Response as AsyncPlaywrightResponse
from playwright.sync_api import Response as PlaywrightResponse

from scrapling.core._types import Any, Generator
from scrapling.core._network_formatting import _request_details
from scrapling.fetchers import AsyncDynamicSession, AsyncStealthySession, DynamicSession, StealthySession
from scrapling.engines.toolbelt.custom import Response
from scrapling.engines.toolbelt.proxy_rotation import ProxyRotator


HTML = b"""<!DOCTYPE html><html><head><link rel="icon" href="data:,"><link rel="stylesheet" href="/style.css"></head>
<body><img src="/image.png"><script src="/script.js"></script></body></html>"""
SCRIPT = b"""Promise.all([
fetch('/api/initial').then(response => response.json()),
new Promise(resolve => { const xhr = new XMLHttpRequest(); xhr.open('GET', '/api/xhr');
xhr.onload = () => resolve(JSON.parse(xhr.responseText)); xhr.send(); })
]).then(() => document.body.dataset.initial = 'ready');"""
LATER = """async () => {
    await fetch('/api/post', {method: 'POST', headers: {'Content-Type': 'application/json', 'X-Sent': 'request'}, body: '{"sent":true}'}).then(response => response.json());
    await fetch('/api/repeated').then(response => response.text());
    await fetch('/api/repeated').then(response => response.text());
    await fetch('/api/status').then(response => response.text());
    await fetch('/redirect').then(response => response.text());
    await fetch('/api/fail').catch(() => null);
    await fetch('/api/large').then(response => response.text());
}"""
PENDING = """() => {
    fetch('/api/pending').then(response => response.text()).then(() => document.body.dataset.pending = 'done');
}"""
BLANK = b'<!DOCTYPE html><html><head><link rel="icon" href="data:,"></head><body>ready</body></html>'
LARGE = b"x" * (1024 * 1024 + 1)
BINARY = bytes(range(256))
PNG = b64decode("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+aZ1cAAAAASUVORK5CYII=")
TEXT_RESPONSES = {
    "/mime/json": ("application/json", b'{"saved":true}'),
    "/mime/xml": ("application/xml", b"<saved>true</saved>"),
    "/mime/vendor-json": ("application/vnd.scrapling+json", b'{"saved":true}'),
    "/mime/vendor-xml": ("application/vnd.scrapling+xml", b"<saved>true</saved>"),
    "/mime/javascript": ("application/javascript", b"window.saved = true;"),
    "/mime/graphql": ("application/graphql", b"{ saved }"),
    "/mime/form": ("application/x-www-form-urlencoded", b"saved=true"),
}
MIME_RESPONSES = {
    **TEXT_RESPONSES,
    "/mime/image": ("image/png", PNG),
    "/mime/pdf": ("application/pdf", b"%PDF-1.7\n%%EOF"),
    "/mime/file": ("application/octet-stream", BINARY),
    "/mime/media": ("audio/wav", b"RIFF\x04\x00\x00\x00WAVE"),
    "/mime/font": ("font/woff2", b"wOF2\x00\x01\x00\x00"),
    "/mime/missing": (None, b'{"saved":false}'),
    "/mime/unknown": ("application/x-scrapling-unknown", b'{"saved":false}'),
}
MIME_FETCH = """async paths => {
    const bodies = {};
    for (const path of paths) {
        const response = await fetch(path);
        bodies[path] = Array.from(new Uint8Array(await response.arrayBuffer()));
    }
    return bodies;
}"""
SEARCH_FETCH = """async () => {
    await Promise.all(Array.from({length: 150}, (_, index) => fetch(`/api/search/${index}`, index % 10 ? {
        method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({index})
    } : {}).then(response => response.json())));
    return true;
}"""
CHARSET_BODY = "caf\u00e9 \u20ac".encode("iso-8859-15")
CHARSET_PATHS = ("/wire/charset", "/wire/charset-spaced", "/wire/raw-charset")
WIRE_PATHS = ["/wire/chunked", "/wire/gzip", "/wire/binary", *CHARSET_PATHS, "/wire/head", "/wire/empty"]
WIRE_FETCH = """async paths => {
    const bodies = {};
    for (const path of paths) {
        const response = await fetch(path, {method: path.endsWith('/head') ? 'HEAD' : 'GET'});
        const body = await response.arrayBuffer();
        if (path.includes('charset') || path.endsWith('/binary')) bodies[path] = Array.from(new Uint8Array(body));
    }
    return bodies;
}"""


@dataclass
class _Gate:
    started: Event = field(default_factory=Event)
    release: Event = field(default_factory=Event)
    finished: Event = field(default_factory=Event)


class _Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def log_message(self, format: str, *args: Any) -> None:
        pass

    def do_GET(self) -> None:
        path = urlsplit(self.path).path
        if path == "/api/fail":
            self.connection.shutdown(SHUT_RDWR)
            self.connection.close()
            return
        if path == "/api/pending":
            if not getattr(self.server, "release_pending").wait(10):
                getattr(self.server, "errors").append("Timed out waiting to release /api/pending")
                return
        status, body = 200, b'{"ok":true}'
        content_type: str | None = "application/json"
        if path in ("/", "/second", "/fresh", "/other"):
            content_type, body = "text/html", HTML
        elif path == "/blank":
            content_type, body = "text/html", BLANK
        elif path == "/style.css":
            content_type, body = "text/css", b"body { color: black; }"
        elif path == "/script.js":
            content_type, body = "application/javascript", SCRIPT
        elif path == "/image.png":
            content_type, body = "image/png", PNG
        elif path == "/api/status":
            status, content_type, body = 503, "text/plain", b"Try later"
        elif path == "/api/large":
            content_type, body = "text/plain", LARGE
        elif path == "/redirect":
            status, body = 302, b""
        elif path in {"/wire/chunked", "/wire/gzip"}:
            content_type, body = "text/plain", compress(LARGE) if path.endswith("gzip") else LARGE
        elif path == "/wire/binary":
            content_type, body = "application/octet-stream", BINARY
        elif path == "/wire/charset":
            content_type, body = "text/plain; charset=iso-8859-15", CHARSET_BODY
        elif path == "/wire/charset-spaced":
            content_type, body = 'text/plain; CHARSET = "iso-8859-15"', CHARSET_BODY
        elif path == "/wire/raw-charset":
            content_type, body = 'application/octet-stream; CHARSET = "iso-8859-15"', CHARSET_BODY
        elif path == "/wire/head":
            content_type = "application/octet-stream"
        elif path == "/wire/empty":
            status, content_type, body = 204, "application/octet-stream", b""
        elif path in MIME_RESPONSES:
            content_type, body = MIME_RESPONSES[path]
        self.send_response(status)
        if content_type is not None:
            self.send_header("Content-Type", content_type)
        self.send_header("Transfer-Encoding", "chunked") if path == "/wire/chunked" else self.send_header(
            "Content-Length", str(len(body))
        )
        self.send_header("X-Recorded", "response")
        if path == "/redirect":
            self.send_header("Location", "/redirected")
        if path == "/wire/gzip":
            self.send_header("Content-Encoding", "gzip")
        self.end_headers()
        gate = getattr(self.server, "gates").get(path)
        try:
            if gate is not None:
                self.wfile.write(body[:1])
                self.wfile.flush()
                gate.started.set()
                if not gate.release.wait(10):
                    getattr(self.server, "errors").append(f"Timed out waiting to release {path}")
                    return
                body = body[1:]
            if path == "/wire/chunked":
                for start in range(0, len(body), 65536):
                    chunk = body[start : start + 65536]
                    self.wfile.write(f"{len(chunk):x}\r\n".encode() + chunk + b"\r\n")
                self.wfile.write(b"0\r\n\r\n")
            elif self.command != "HEAD":
                self.wfile.write(body)
        except (BrokenPipeError, ConnectionResetError):
            pass
        finally:
            if gate is not None:
                gate.finished.set()

    def do_HEAD(self) -> None:
        self.do_GET()

    def do_POST(self) -> None:
        body = self.rfile.read(int(self.headers.get("Content-Length", 0)))
        self.send_response(201)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("X-Recorded", "response")
        self.end_headers()
        self.wfile.write(body)


@pytest.fixture(scope="module")
def release_pending() -> Event:
    return Event()


@pytest.fixture(scope="module")
def network_gates() -> dict[str, _Gate]:
    return {}


@pytest.fixture(scope="module")
def network_url(release_pending: Event, network_gates: dict[str, _Gate]) -> Generator[str, None, None]:
    server = ThreadingHTTPServer(("127.0.0.1", 0), _Handler)
    setattr(server, "release_pending", release_pending)
    setattr(server, "gates", network_gates)
    errors: list[str] = []
    setattr(server, "errors", errors)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_port}"
    finally:
        release_pending.set()
        for gate in network_gates.values():
            gate.release.set()
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)
        assert not thread.is_alive()
        assert not errors


def _options(**kwargs: Any) -> dict[str, Any]:
    return {
        "executable_path": getenv("SCRAPLING_EXECUTABLE_PATH"),
        "google_search": False,
        "record_requests": True,
        "retries": 1,
        **kwargs,
    }


@pytest.mark.parametrize("session_type", [DynamicSession, StealthySession])
def test_sync_network_disabled_by_default(session_type: Any) -> None:
    session = session_type()
    context = Mock()
    session._initialize_context(session._config, context)
    assert not session.network.enabled
    context.on.assert_not_called()
    assert session.network.search() == [] and session.network.last_id == 0
    assert not session.network._contexts
    session.close()


@pytest.mark.asyncio
@pytest.mark.parametrize("session_type", [AsyncDynamicSession, AsyncStealthySession])
async def test_async_network_disabled_by_default(session_type: Any) -> None:
    session = session_type()
    context = Mock()
    await session._initialize_context(session._config, context)
    assert not session.network.enabled
    context.on.assert_not_called()
    assert session.network.search() == [] and session.network.last_id == 0
    assert not session.network._contexts
    await session.close()


def _wait_saved(page: Any, network: Any, pattern: str, count: int = 1, after_id: int = 0) -> list[Any]:
    for _ in range(250):
        records = network.search(url_pattern=pattern, after_id=after_id, limit=None)
        if len(records) >= count:
            return records
        page.wait_for_timeout(20)
    raise AssertionError(f"Expected {count} saved responses for {pattern!r}, got {len(records)}")


async def _wait_saved_async(page: Any, network: Any, pattern: str, count: int = 1, after_id: int = 0) -> list[Any]:
    for _ in range(250):
        records = network.search(url_pattern=pattern, after_id=after_id, limit=None)
        if len(records) >= count:
            return records
        await asyncio.sleep(0.02)
    raise AssertionError(f"Expected {count} saved responses for {pattern!r}, got {len(records)}")


def _check_initial(network: Any) -> Any:
    records = network.search()
    assert network.enabled
    assert {record.meta["resource_type"] for record in records} >= {
        "document",
        "script",
        "stylesheet",
        "image",
        "fetch",
        "xhr",
    }
    assert len({record.meta["network_id"] for record in records}) == len(records)
    initial = network.search(url_pattern=r"/api/initial$", resource_type="fetch")
    assert len(initial) == 1
    assert initial[0].status == 200
    assert initial[0].meta["request_body"] is None
    assert initial[0].json() == {"ok": True}
    assert isinstance(initial[0], Response) and initial[0].request is None
    assert "body_note" not in initial[0].meta and not hasattr(initial[0], "response")
    assert network.get(initial[0].meta["network_id"]) is initial[0]
    captured = network.search(url_pattern=r"/api/(initial|xhr)$")
    assert {urlsplit(item.url).path for item in captured} == {"/api/initial", "/api/xhr"}
    assert all(item.json() == {"ok": True} for item in captured)
    image = network.search(url_pattern=r"/image\.png$")[0]
    assert image.body == b"" and image.meta.get("body_note") == "Non-text body; not saved."
    for path, body in ((r"/script\.js$", SCRIPT), (r"/style\.css$", b"body { color: black; }")):
        asset = network.search(url_pattern=path)[0]
        assert asset.body == body and "body_note" not in asset.meta
    filtered = network.search(include_static=False)
    assert filtered and all(record.meta["resource_type"] in ("document", "xhr", "fetch") for record in filtered)
    return initial[0]


def _check_later(network: Any, after_id: int) -> tuple[Any, Any, Any]:
    records = network.search(after_id=after_id)
    assert records and all(record.meta["network_id"] > after_id for record in records)
    post = network.search(method="POST", status=201)
    assert len(post) == 1
    assert loads(post[0].meta["request_body"]) == {"sent": True}
    duplicate = network.search(url_pattern=r"/api/repeated$")
    assert len(duplicate) == 2 and duplicate[0].meta["network_id"] != duplicate[1].meta["network_id"]
    assert len(network.search(url_pattern=r"/api/repeated$", limit=1)) == 1
    status = network.search(status=503)
    assert len(status) == 1
    assert not network.search(url_pattern=r"/api/fail$")
    redirect = network.search(url_pattern=r"/redirect$")
    assert len(redirect) == 1 and redirect[0].status == 302
    redirected = network.search(url_pattern=r"/redirected$", status=200)
    assert len(redirected) == 1 and redirected[0].meta["network_id"] != redirect[0].meta["network_id"]
    assert redirect[0].headers["location"] == "/redirected"
    return post[0], status[0], network.search(url_pattern=r"/api/large$")[0]


@pytest.mark.parametrize("session_type", [DynamicSession, StealthySession])
def test_sync_network_browser_history(session_type: Any, network_url: str, release_pending: Event) -> None:
    with session_type(
        **_options(
            page_action=lambda page: page.locator("body[data-initial=ready]").wait_for(state="attached"),
        )
    ) as session:
        session.fetch(network_url + "/")
        page = session.page_pool.pages[0].page
        _wait_saved(page, session.network, r"/(?:api/(?:initial|xhr)|script\.js|style\.css|image\.png)?$", 6)
        initial = _check_initial(session.network)
        assert initial.json() == {"ok": True}
        page = session.page_pool.pages[0].page
        after_id = session.network.last_id
        with page.expect_request_finished(lambda request: request.url.endswith("/api/large")):
            page.evaluate(LATER)
        _wait_saved(page, session.network, r"/(?:api/(?:post|repeated|status|large)|redirect|redirected)$", 7)
        post, status, large = _check_later(session.network, after_id)
        assert post.request_headers["x-sent"] == "request"
        assert post.headers["x-recorded"] == "response"
        assert post.json() == {"sent": True}
        assert status.body == b"Try later"
        assert large.meta.get("body_note") == "too large; not saved." and large.body == b""
        release_pending.clear()
        try:
            with page.expect_request_finished(lambda request: request.url.endswith("/api/pending")):
                with page.expect_request("**/api/pending"):
                    page.evaluate(PENDING)
                assert not session.network.search(url_pattern=r"/api/pending$")
                release_pending.set()
            pending = _wait_saved(page, session.network, r"/api/pending$")[0]
            assert pending.status == 200 and pending.json() == {"ok": True}
        finally:
            release_pending.set()
        other = session.context.new_page()
        try:
            other.goto(network_url + "/other")
            other.locator("body[data-initial=ready]").wait_for(state="attached")
            _wait_saved(other, session.network, r"/other$")
        finally:
            other.close()
        assert session.network.search(url_pattern=r"/other$", resource_type="document")
        session.fetch(network_url + "/second")
        assert session.page_pool.pages[0].page is page
        session.close_pages()
        assert page.is_closed() and session.network.get(post.meta["network_id"]).url == post.url
        fresh_id = session.network.last_id
        session.fetch(network_url + "/fresh")
        _wait_saved(session.page_pool.pages[0].page, session.network, r"/(?:fresh|api/initial)$", 2, fresh_id)
        assert session.page_pool.pages[0].page is not page
        assert session.network.search(url_pattern=r"/fresh$", resource_type="document")
        unread = session.network.search(url_pattern=r"/api/initial$")[-1]
        page = session.page_pool.pages[0].page
        with page.expect_request_finished(lambda request: request.url.endswith("/api/closing")):
            page.evaluate("fetch('/api/closing', {method: 'POST', body: 'closing'}).then(response => response.text())")
        _wait_saved(page, session.network, r"/api/closing$")
        last_id = session.network.last_id
    assert session.network.last_id == last_id
    assert session.network.get(post.meta["network_id"]).status == 201
    assert session.network.get(post.meta["network_id"]).method == "POST"
    closing = session.network.search(url_pattern=r"/api/closing$")[0]
    assert closing.body == b"closing" and "body_note" not in closing.meta
    assert unread.json() == {"ok": True}
    assert initial.json() == {"ok": True}
    assert post.json() == {"sent": True}
    assert post.request_headers["x-sent"] == "request"
    assert post.headers["x-recorded"] == "response"


@pytest.mark.asyncio
@pytest.mark.parametrize("session_type", [AsyncDynamicSession, AsyncStealthySession])
async def test_async_network_browser_history(session_type: Any, network_url: str, release_pending: Event) -> None:
    async def initial_page(page: Any) -> None:
        await page.locator("body[data-initial=ready]").wait_for(state="attached")

    async with session_type(**_options(page_action=initial_page)) as session:
        await session.fetch(network_url + "/")
        page = session.page_pool.pages[0].page
        await _wait_saved_async(
            page, session.network, r"/(?:api/(?:initial|xhr)|script\.js|style\.css|image\.png)?$", 6
        )
        initial = _check_initial(session.network)
        assert initial.json() == {"ok": True}
        page = session.page_pool.pages[0].page
        after_id = session.network.last_id
        async with page.expect_request_finished(lambda request: request.url.endswith("/api/large")):
            await page.evaluate(LATER)
        await _wait_saved_async(
            page, session.network, r"/(?:api/(?:post|repeated|status|large)|redirect|redirected)$", 7
        )
        post, status, large = _check_later(session.network, after_id)
        assert post.request_headers["x-sent"] == "request"
        assert post.headers["x-recorded"] == "response"
        assert post.json() == {"sent": True}
        assert status.body == b"Try later"
        assert large.meta.get("body_note") == "too large; not saved." and large.body == b""
        release_pending.clear()
        try:
            async with page.expect_request("**/api/pending"):
                await page.evaluate(PENDING)
            assert not session.network.search(url_pattern=r"/api/pending$")
            release_pending.set()
            pending = (await _wait_saved_async(page, session.network, r"/api/pending$"))[0]
            assert pending.status == 200 and pending.json() == {"ok": True}
        finally:
            release_pending.set()
        other = await session.context.new_page()
        try:
            await other.goto(network_url + "/other")
            await other.locator("body[data-initial=ready]").wait_for(state="attached")
            await _wait_saved_async(other, session.network, r"/other$")
        finally:
            await other.close()
        assert session.network.search(url_pattern=r"/other$", resource_type="document")
        await session.fetch(network_url + "/second")
        assert session.page_pool.pages[0].page is page
        await session.close_pages()
        assert page.is_closed() and session.network.get(post.meta["network_id"]).url == post.url
        fresh_id = session.network.last_id
        await session.fetch(network_url + "/fresh")
        await _wait_saved_async(
            session.page_pool.pages[0].page, session.network, r"/(?:fresh|api/initial)$", 2, fresh_id
        )
        assert session.page_pool.pages[0].page is not page
        assert session.network.search(url_pattern=r"/fresh$", resource_type="document")
        unread = session.network.search(url_pattern=r"/api/initial$")[-1]
        page = session.page_pool.pages[0].page
        async with page.expect_request_finished(lambda request: request.url.endswith("/api/closing")):
            await page.evaluate(
                "fetch('/api/closing', {method: 'POST', body: 'closing'}).then(response => response.text())"
            )
        await _wait_saved_async(page, session.network, r"/api/closing$")
        last_id = session.network.last_id
    assert session.network.last_id == last_id
    assert session.network.get(post.meta["network_id"]).status == 201
    assert session.network.get(post.meta["network_id"]).method == "POST"
    closing = session.network.search(url_pattern=r"/api/closing$")[0]
    assert closing.body == b"closing" and "body_note" not in closing.meta
    assert unread.json() == {"ok": True}
    assert initial.json() == {"ok": True}
    assert post.json() == {"sent": True}
    assert post.request_headers["x-sent"] == "request"
    assert post.headers["x-recorded"] == "response"


def _check_eviction(network: Any) -> int:
    records = network.search()
    assert len(records) == 2 and network.dropped_count > 0
    assert network.get(1) is None
    last_id = network.last_id
    network.clear()
    assert network.search() == [] and network.last_id == last_id
    return last_id


@pytest.mark.parametrize("session_type", [DynamicSession, StealthySession])
def test_sync_network_browser_eviction_and_clear(session_type: Any, network_url: str) -> None:
    with session_type(**_options(max_recorded_requests=2)) as session:
        session.fetch(network_url + "/")
        page = session.page_pool.pages[0].page
        page.locator("body[data-initial=ready]").wait_for(state="attached")
        for _ in range(250):
            if session.network.last_id >= 6:
                break
            page.wait_for_timeout(20)
        assert session.network.last_id >= 6
        last_id = _check_eviction(session.network)
        with page.expect_request_finished(lambda request: request.url.endswith("/api/post")):
            page.evaluate("fetch('/api/post', {method: 'POST', body: 'fresh'}).then(response => response.text())")
        _wait_saved(page, session.network, r"/api/post$")
        records = session.network.search()
        assert len(records) == 1 and records[0].meta["network_id"] > last_id
        assert records[0].meta["request_body"] == records[0].body == b"fresh"


@pytest.mark.asyncio
@pytest.mark.parametrize("session_type", [AsyncDynamicSession, AsyncStealthySession])
async def test_async_network_browser_eviction_and_clear(session_type: Any, network_url: str) -> None:
    async with session_type(**_options(max_recorded_requests=2)) as session:
        await session.fetch(network_url + "/")
        page = session.page_pool.pages[0].page
        await page.locator("body[data-initial=ready]").wait_for(state="attached")
        for _ in range(250):
            if session.network.last_id >= 6:
                break
            await asyncio.sleep(0.02)
        assert session.network.last_id >= 6
        last_id = _check_eviction(session.network)
        async with page.expect_request_finished(lambda request: request.url.endswith("/api/post")):
            await page.evaluate("fetch('/api/post', {method: 'POST', body: 'fresh'}).then(response => response.text())")
        await _wait_saved_async(page, session.network, r"/api/post$")
        records = session.network.search()
        assert len(records) == 1 and records[0].meta["network_id"] > last_id
        assert records[0].meta["request_body"] == records[0].body == b"fresh"


PROXY_HTML = '<html><body><script>fetch("/api").then(response => response.json()).then(value => document.body.dataset.api = JSON.stringify(value));</script></body></html>'


@pytest.mark.parametrize("session_type", [DynamicSession, StealthySession])
def test_sync_network_browser_temporary_proxy_context(session_type: Any) -> None:
    def setup(page: Any) -> None:
        page.route(
            "**/*",
            lambda route: route.fulfill(
                content_type="application/json" if route.request.url.endswith("/api") else "text/html",
                body='{"temporary":true}' if route.request.url.endswith("/api") else PROXY_HTML,
            ),
        )

    def initial(page: Any) -> None:
        page.locator("body[data-api]").wait_for(state="attached")
        _wait_saved(page, session.network, r"/api$")

    with session_type(
        **_options(proxy_rotator=ProxyRotator(["http://127.0.0.1:1"]), page_setup=setup, page_action=initial)
    ) as session:
        session.fetch("https://network.test/")
        assert not session.page_pool.pages
        record = session.network.search(url_pattern=r"/api$")[0]
        assert record.status == 200 and record.meta["resource_type"] == "fetch"
        assert record.json() == {"temporary": True}
    assert session.network.get(record.meta["network_id"]).url == "https://network.test/api"
    assert record.json() == {"temporary": True}


@pytest.mark.asyncio
@pytest.mark.parametrize("session_type", [AsyncDynamicSession, AsyncStealthySession])
async def test_async_network_browser_temporary_proxy_context(session_type: Any) -> None:
    async def setup(page: Any) -> None:
        await page.route(
            "**/*",
            lambda route: route.fulfill(
                content_type="application/json" if route.request.url.endswith("/api") else "text/html",
                body='{"temporary":true}' if route.request.url.endswith("/api") else PROXY_HTML,
            ),
        )

    async def initial(page: Any) -> None:
        await page.locator("body[data-api]").wait_for(state="attached")
        await _wait_saved_async(page, session.network, r"/api$")

    async with session_type(
        **_options(proxy_rotator=ProxyRotator(["http://127.0.0.1:1"]), page_setup=setup, page_action=initial)
    ) as session:
        await session.fetch("https://network.test/")
        assert not session.page_pool.pages
        record = session.network.search(url_pattern=r"/api$")[0]
        assert record.status == 200 and record.meta["resource_type"] == "fetch"
        assert record.json() == {"temporary": True}
    assert session.network.get(record.meta["network_id"]).url == "https://network.test/api"
    assert record.json() == {"temporary": True}


def _check_saved_override(network: Any, network_url: str) -> None:
    records = network.search(url_pattern=r"/api/overridden$", method="POST", status=201)
    assert len(records) == 1
    record = records[0]
    assert record.url == network_url + "/api/overridden"
    assert record.meta["request_body"] == record.body == b"overridden"
    assert record.request_headers["x-overridden"] == "yes"
    assert not network.search(url_pattern=r"/api/original$")


@pytest.mark.parametrize("session_type", [DynamicSession, StealthySession])
def test_sync_network_browser_keeps_route_overrides_after_close(
    session_type: Any, network_url: str, monkeypatch: Any
) -> None:
    logger = Mock()
    monkeypatch.setattr("scrapling.engines.toolbelt.custom.log", logger)
    with session_type(**_options()) as session:
        session.fetch(network_url + "/")
        page = session.page_pool.pages[0].page
        page.route(
            "**/api/original",
            lambda route: route.continue_(
                url=network_url + "/api/overridden",
                method="POST",
                post_data="overridden",
                headers={**route.request.headers, "x-overridden": "yes"},
            ),
        )
        with page.expect_request_finished(lambda request: request.url.endswith("/api/overridden")):
            page.evaluate("fetch('/api/original').then(response => response.text())")
        _wait_saved(page, session.network, r"/api/overridden$")
    _check_saved_override(session.network, network_url)
    logger.info.assert_called_once()
    assert f"<GET {network_url}/>" in logger.info.call_args.args[0]


@pytest.mark.asyncio
@pytest.mark.parametrize("session_type", [AsyncDynamicSession, AsyncStealthySession])
async def test_async_network_browser_keeps_route_overrides_after_close(
    session_type: Any, network_url: str, monkeypatch: Any
) -> None:
    logger = Mock()
    monkeypatch.setattr("scrapling.engines.toolbelt.custom.log", logger)
    async with session_type(**_options()) as session:
        await session.fetch(network_url + "/")
        page = session.page_pool.pages[0].page
        await page.route(
            "**/api/original",
            lambda route: route.continue_(
                url=network_url + "/api/overridden",
                method="POST",
                post_data="overridden",
                headers={**route.request.headers, "x-overridden": "yes"},
            ),
        )
        async with page.expect_request_finished(lambda request: request.url.endswith("/api/overridden")):
            await page.evaluate("fetch('/api/original').then(response => response.text())")
        await _wait_saved_async(page, session.network, r"/api/overridden$")
    _check_saved_override(session.network, network_url)
    logger.info.assert_called_once()
    assert f"<GET {network_url}/>" in logger.info.call_args.args[0]


@pytest.mark.parametrize("session_type", [DynamicSession, StealthySession])
@pytest.mark.parametrize("target", ["page", "context", "session"])
def test_sync_network_close_during_unfinished_response(
    session_type: Any, target: str, network_url: str, network_gates: dict[str, _Gate]
) -> None:
    path = f"/api/held/{session_type.__name__}/{target}"
    gate = network_gates[path] = _Gate()
    with session_type(**_options()) as session:
        session.fetch(network_url + "/blank")
        page = session.page_pool.pages[0].page
        saved = _wait_saved(page, session.network, r"/blank$")[0]
        try:
            page.evaluate("fetch('/api/fail').catch(() => null)")
            with page.expect_response(network_url + path):
                page.evaluate("path => { fetch(path).then(response => response.text()).catch(() => null); }", path)
            assert gate.started.wait(5), "The server did not start the held response"
            assert not gate.release.is_set() and not gate.finished.is_set()
            assert not session.network.search(url_pattern=r"/api/(?:held|fail)")
            started = monotonic()
            {"page": session.close_pages, "context": session.context.close, "session": session.close}[target]()
            assert monotonic() - started < 5
            assert not gate.release.is_set() and not gate.finished.is_set()
            assert page.is_closed()
            assert session.network.get(saved.meta["network_id"]).body == BLANK
            assert not session.network.search(url_pattern=r"/api/(?:held|fail)")
            assert bool(session.network._contexts) == (target == "page")
        finally:
            gate.release.set()
            assert gate.finished.wait(5), "The server did not finish the released response"
    assert not session.network._contexts
    assert session.network.search() == [saved]
    assert saved.body == BLANK


@pytest.mark.asyncio
@pytest.mark.parametrize("session_type", [AsyncDynamicSession, AsyncStealthySession])
@pytest.mark.parametrize("target", ["page", "context", "session"])
async def test_async_network_close_during_unfinished_response(
    session_type: Any, target: str, network_url: str, network_gates: dict[str, _Gate]
) -> None:
    path = f"/api/held/{session_type.__name__}/{target}"
    gate = network_gates[path] = _Gate()
    async with session_type(**_options()) as session:
        await session.fetch(network_url + "/blank")
        page = session.page_pool.pages[0].page
        saved = (await _wait_saved_async(page, session.network, r"/blank$"))[0]
        try:
            await page.evaluate("fetch('/api/fail').catch(() => null)")
            async with page.expect_response(network_url + path):
                await page.evaluate(
                    "path => { fetch(path).then(response => response.text()).catch(() => null); }", path
                )
            assert await asyncio.to_thread(gate.started.wait, 5), "The server did not start the held response"
            assert not gate.release.is_set() and not gate.finished.is_set()
            assert not session.network.search(url_pattern=r"/api/(?:held|fail)")
            close = {"page": session.close_pages, "context": session.context.close, "session": session.close}[target]
            await asyncio.wait_for(close(), timeout=5)
            assert not gate.release.is_set() and not gate.finished.is_set()
            assert page.is_closed()
            assert session.network.get(saved.meta["network_id"]).body == BLANK
            assert not session.network.search(url_pattern=r"/api/(?:held|fail)")
            assert bool(session.network._contexts) == (target == "page")
        finally:
            gate.release.set()
            assert await asyncio.to_thread(gate.finished.wait, 5), "The server did not finish the released response"
    assert not session.network._contexts
    assert session.network.search() == [saved]
    assert saved.body == BLANK


def _check_burst(network: Any, cursor: int, path: str, expected_paths: list[str]) -> int:
    newer = network.search(after_id=cursor, limit=1)
    assert len(newer) == 1 and urlsplit(newer[0].url).path == path
    assert newer[0].meta["network_id"] == cursor + 1
    records = network.search(limit=2)
    records += network.search(after_id=records[-1].meta["network_id"], limit=2)
    assert [urlsplit(record.url).path for record in records] == expected_paths[-3:]
    assert all(record.json() == {"ok": True} for record in records)
    assert network.dropped_count == max(0, len(expected_paths) - 3)
    return newer[0].meta["network_id"]


@pytest.mark.parametrize("session_type", [DynamicSession, StealthySession])
def test_sync_network_burst_completion_order_and_pagination(
    session_type: Any, network_url: str, network_gates: dict[str, _Gate]
) -> None:
    paths = [f"/api/burst/{session_type.__name__}/{index}" for index in range(6)]
    gates = {path: _Gate() for path in paths}
    network_gates.update(gates)
    with session_type(**_options(max_recorded_requests=3)) as session:
        session.fetch(network_url + "/blank")
        page = session.page_pool.pages[0].page
        _wait_saved(page, session.network, r"/blank$")
        session.network.clear()
        cursor = session.network.last_id
        completed: list[str] = []
        try:
            page.evaluate(
                "paths => { for (const path of paths) fetch(path).then(response => response.text()).catch(() => null); }",
                paths,
            )
            assert all(gate.started.wait(5) for gate in gates.values()), "The request burst did not reach the server"
            assert session.network.search() == []
            for index in (5, 2, 4, 1, 3, 0):
                path = paths[index]
                gates[path].release.set()
                _wait_saved(page, session.network, path + "$", after_id=cursor)
                completed.append(path)
                cursor = _check_burst(session.network, cursor, path, completed)
            assert session.network.get(cursor - 3) is None
        finally:
            for gate in gates.values():
                gate.release.set()
            assert all(gate.finished.wait(5) for gate in gates.values())
    assert not session.network._contexts
    records = session.network.search()
    assert [urlsplit(record.url).path for record in records] == completed[-3:]
    assert all(record.json() == {"ok": True} for record in records)


@pytest.mark.asyncio
@pytest.mark.parametrize("session_type", [AsyncDynamicSession, AsyncStealthySession])
async def test_async_network_burst_completion_order_and_pagination(
    session_type: Any, network_url: str, network_gates: dict[str, _Gate]
) -> None:
    paths = [f"/api/burst/{session_type.__name__}/{index}" for index in range(6)]
    gates = {path: _Gate() for path in paths}
    network_gates.update(gates)
    async with session_type(**_options(max_recorded_requests=3)) as session:
        await session.fetch(network_url + "/blank")
        page = session.page_pool.pages[0].page
        await _wait_saved_async(page, session.network, r"/blank$")
        session.network.clear()
        cursor = session.network.last_id
        completed: list[str] = []
        try:
            await page.evaluate(
                "paths => { for (const path of paths) fetch(path).then(response => response.text()).catch(() => null); }",
                paths,
            )
            for gate in gates.values():
                assert await asyncio.to_thread(gate.started.wait, 5), "The request burst did not reach the server"
            assert session.network.search() == []
            for index in (5, 2, 4, 1, 3, 0):
                path = paths[index]
                gates[path].release.set()
                await _wait_saved_async(page, session.network, path + "$", after_id=cursor)
                completed.append(path)
                cursor = _check_burst(session.network, cursor, path, completed)
            assert session.network.get(cursor - 3) is None
        finally:
            for gate in gates.values():
                gate.release.set()
            for gate in gates.values():
                assert await asyncio.to_thread(gate.finished.wait, 5)
    assert not session.network._contexts
    records = session.network.search()
    assert [urlsplit(record.url).path for record in records] == completed[-3:]
    assert all(record.json() == {"ok": True} for record in records)


def _check_wire_bodies(
    network: Any, wire: dict[str, list[int]], native_bodies: dict[str, bytes], native_texts: dict[str, str]
) -> None:
    records = {urlsplit(record.url).path: record for record in network.search(url_pattern=r"/wire/")}
    assert set(records) == set(WIRE_PATHS)
    for path in ("/wire/chunked", "/wire/gzip"):
        assert records[path].meta.get("body_note") == "too large; not saved."
        assert records[path].body == b""
    assert "content-length" not in records["/wire/chunked"].headers
    assert records["/wire/chunked"].headers["transfer-encoding"] == "chunked"
    assert int(records["/wire/gzip"].headers["content-length"]) < 1024 * 1024
    assert records["/wire/gzip"].headers["content-encoding"] == "gzip"
    assert bytes(wire["/wire/binary"]) == native_bodies["/wire/binary"] == BINARY
    for path in ("/wire/binary", "/wire/raw-charset"):
        assert records[path].body == b""
        assert records[path].meta.get("body_note") == "Non-text body; not saved."
        details = _request_details(records[path], "response_body")
        assert details.data is None and details.note == "Non-text body; not saved."
    for path in CHARSET_PATHS:
        assert bytes(wire[path]) == CHARSET_BODY
        assert records[path].headers["content-type"].lower().endswith(("iso-8859-15", '"iso-8859-15"'))
    for path, text in native_texts.items():
        assert records[path].body == native_bodies[path]
        assert "body_note" not in records[path].meta
        assert records[path].encoding == "utf-8"
        assert native_bodies[path].decode("utf-8") == text
        assert records[path].get_all_text().strip() == text
        details = _request_details(records[path], "response_body")
        assert details.data == text and details.request_id == records[path].meta["network_id"]
        assert details.part == "response_body" and details.note is None
    assert native_texts["/wire/charset"] == "caf\u00e9 \u20ac"
    assert native_bodies["/wire/charset"] == "caf\u00e9 \u20ac".encode("utf-8")
    assert native_bodies["/wire/raw-charset"] == CHARSET_BODY
    assert records["/wire/head"].method == "HEAD" and records["/wire/head"].status == 200
    assert records["/wire/empty"].status == 204
    for path in ("/wire/head", "/wire/empty"):
        assert records[path].body == b"" and "body_note" not in records[path].meta


@pytest.mark.parametrize("session_type", [DynamicSession, StealthySession])
def test_sync_network_wire_bodies_remain_readable_after_close(session_type: Any, network_url: str) -> None:
    with session_type(**_options()) as session:
        session.fetch(network_url + "/blank")
        page = session.page_pool.pages[0].page
        native: dict[str, Any] = {}
        page.on("response", lambda response: native.update({urlsplit(response.url).path: response}))
        wire = page.evaluate(WIRE_FETCH, WIRE_PATHS)
        _wait_saved(page, session.network, r"/wire/", len(WIRE_PATHS))
        native_bodies = {path: native[path].body() for path in wire}
        native_texts = {path: native[path].text() for path in CHARSET_PATHS[:2]}
        with pytest.raises(UnicodeDecodeError):
            native["/wire/raw-charset"].text()
        _check_wire_bodies(session.network, wire, native_bodies, native_texts)
    assert not session.network._contexts
    _check_wire_bodies(session.network, wire, native_bodies, native_texts)


@pytest.mark.asyncio
@pytest.mark.parametrize("session_type", [AsyncDynamicSession, AsyncStealthySession])
async def test_async_network_wire_bodies_remain_readable_after_close(session_type: Any, network_url: str) -> None:
    async with session_type(**_options()) as session:
        await session.fetch(network_url + "/blank")
        page = session.page_pool.pages[0].page
        native: dict[str, Any] = {}
        page.on("response", lambda response: native.update({urlsplit(response.url).path: response}))
        wire = await page.evaluate(WIRE_FETCH, WIRE_PATHS)
        await _wait_saved_async(page, session.network, r"/wire/", len(WIRE_PATHS))
        native_bodies = {path: await native[path].body() for path in wire}
        native_texts = {path: await native[path].text() for path in CHARSET_PATHS[:2]}
        with pytest.raises(UnicodeDecodeError):
            await native["/wire/raw-charset"].text()
        _check_wire_bodies(session.network, wire, native_bodies, native_texts)
    assert not session.network._contexts
    _check_wire_bodies(session.network, wire, native_bodies, native_texts)


def _check_mime_bodies(network: Any, wire: dict[str, list[int]], reads: list[str]) -> None:
    records = {urlsplit(record.url).path: record for record in network.search(url_pattern=r"/mime/")}
    assert set(records) == set(wire) == set(MIME_RESPONSES)
    assert sorted(reads) == sorted(TEXT_RESPONSES)
    for path, (content_type, body) in MIME_RESPONSES.items():
        record = records[path]
        assert bytes(wire[path]) == body
        assert record.status == 200 and record.method == "GET" and record.meta["resource_type"] == "fetch"
        assert record.headers.get("content-type") == content_type
        assert record.headers["x-recorded"] == "response"
        assert int(record.headers["content-length"]) == len(body)
        if path in TEXT_RESPONSES:
            assert record.body == body and "body_note" not in record.meta
        else:
            assert record.body == b""
            assert record.meta.get("body_note") == "Non-text body; not saved."
    for path in ("/mime/json", "/mime/vendor-json"):
        assert records[path].json() == {"saved": True}


@pytest.mark.parametrize(
    ("session_type", "response_type"), [(DynamicSession, PlaywrightResponse), (StealthySession, PatchrightResponse)]
)
def test_sync_network_reads_only_text_bodies(
    session_type: Any, response_type: Any, network_url: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    reads: list[str] = []
    native_body = response_type.body

    def read_body(response: Any) -> bytes:
        path = urlsplit(response.url).path
        if path in MIME_RESPONSES:
            reads.append(path)
        return native_body(response)

    monkeypatch.setattr(response_type, "body", read_body)
    with session_type(**_options()) as session:
        session.fetch(network_url + "/blank")
        page = session.page_pool.pages[0].page
        wire = page.evaluate(MIME_FETCH, list(MIME_RESPONSES))
        _wait_saved(page, session.network, r"/mime/", len(MIME_RESPONSES))
        _check_mime_bodies(session.network, wire, reads)
    assert not session.network._contexts
    _check_mime_bodies(session.network, wire, reads)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("session_type", "response_type"),
    [(AsyncDynamicSession, AsyncPlaywrightResponse), (AsyncStealthySession, AsyncPatchrightResponse)],
)
async def test_async_network_reads_only_text_bodies(
    session_type: Any, response_type: Any, network_url: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    reads: list[str] = []
    native_body = response_type.body

    async def read_body(response: Any) -> bytes:
        path = urlsplit(response.url).path
        if path in MIME_RESPONSES:
            reads.append(path)
        return await native_body(response)

    monkeypatch.setattr(response_type, "body", read_body)
    async with session_type(**_options()) as session:
        await session.fetch(network_url + "/blank")
        page = session.page_pool.pages[0].page
        wire = await page.evaluate(MIME_FETCH, list(MIME_RESPONSES))
        await _wait_saved_async(page, session.network, r"/mime/", len(MIME_RESPONSES))
        _check_mime_bodies(session.network, wire, reads)
    assert not session.network._contexts
    _check_mime_bodies(session.network, wire, reads)


def _check_unlimited_search(network: Any, after_id: int) -> None:
    records = network.search(limit=None)
    assert len(records) == 125 and network.dropped_count == 25 and network.last_id == after_id + 150
    assert [record.meta["network_id"] for record in records] == list(range(after_id + 26, after_id + 151))
    assert network.get(after_id + 25) is None
    assert network.search() == records[:100]
    for record in records:
        index = int(urlsplit(record.url).path.rsplit("/", 1)[-1])
        assert isinstance(record, Response) and network.get(record.meta["network_id"]) is record
        assert record.request is None and record.meta["resource_type"] == "fetch"
        assert record.method == ("POST" if index % 10 else "GET")
        assert record.status == (201 if index % 10 else 200)
        assert record.json() == ({"index": index} if index % 10 else {"ok": True})
    filtered = network.search(
        url_pattern=r"/api/search/\d+$",
        method="post",
        status=201,
        resource_type="fetch",
        include_static=False,
        limit=None,
    )
    assert len(filtered) > 100 and filtered == [record for record in records if record.method == "POST"]
    records.clear()
    filtered.clear()
    assert len(network.search(limit=None)) == 125 and len(network.search()) == 100


@pytest.mark.parametrize("session_type", [DynamicSession, StealthySession])
def test_sync_network_unlimited_search_respects_retention(session_type: Any, network_url: str) -> None:
    with session_type(**_options(max_recorded_requests=125)) as session:
        session.fetch(network_url + "/blank")
        page = session.page_pool.pages[0].page
        _wait_saved(page, session.network, r"/blank$")
        after_id = session.network.last_id
        session.network.clear()
        assert page.evaluate(SEARCH_FETCH) is True
        _wait_saved(page, session.network, r"/api/search/", after_id=after_id + 149)
        _check_unlimited_search(session.network, after_id)
    assert not session.network._contexts
    _check_unlimited_search(session.network, after_id)


@pytest.mark.asyncio
@pytest.mark.parametrize("session_type", [AsyncDynamicSession, AsyncStealthySession])
async def test_async_network_unlimited_search_respects_retention(session_type: Any, network_url: str) -> None:
    async with session_type(**_options(max_recorded_requests=125)) as session:
        await session.fetch(network_url + "/blank")
        page = session.page_pool.pages[0].page
        await _wait_saved_async(page, session.network, r"/blank$")
        after_id = session.network.last_id
        session.network.clear()
        assert await page.evaluate(SEARCH_FETCH) is True
        await _wait_saved_async(page, session.network, r"/api/search/", after_id=after_id + 149)
        _check_unlimited_search(session.network, after_id)
    assert not session.network._contexts
    _check_unlimited_search(session.network, after_id)
