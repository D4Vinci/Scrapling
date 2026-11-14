"""Crawler deduplication must agree with the POST bodies actually sent."""

from collections.abc import AsyncGenerator, Iterator
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from io import BytesIO
from threading import Thread
from urllib.parse import urlencode

import pytest

from scrapling.core._types import Any
from scrapling.engines.toolbelt.custom import Response
from scrapling.fetchers import FetcherSession
from scrapling.spiders import Request, Spider
from scrapling.spiders.session import SessionManager


@pytest.fixture
def body_echo_server() -> Iterator[tuple[str, list[tuple[bytes, str]]]]:
    """Record POST bodies and request identities on a loopback-only server."""
    bodies: list[tuple[bytes, str]] = []

    class Handler(BaseHTTPRequestHandler):
        def do_POST(self) -> None:
            body = self.rfile.read(int(self.headers.get("Content-Length", "0")))
            bodies.append((body, self.headers.get("X-Body-Variant", "")))
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", "2")
            self.end_headers()
            self.wfile.write(b"{}")

        def log_message(self, format: str, *args: Any) -> None:
            pass

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = Thread(target=server.serve_forever, kwargs={"poll_interval": 0.01}, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_port}/echo", bodies
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "overrides, body",
    [
        ({"json": {"id": 2}}, b'{"id":2}'),
        ({"json": {}}, b"{}"),
        ({"json": []}, b"[]"),
        ({"json": False}, b"false"),
        ({"json": 0}, b"0"),
        ({"json": ""}, b'""'),
        pytest.param({"json": {"label": "café"}}, b'{"label":"caf\\u00e9"}', id="escaped_json"),
        ({"content": b"second"}, b"second"),
        ({"content": "second"}, b"second"),
        ({"content": b""}, b""),
        ({"content": ""}, b""),
        ({"content": bytearray(b"second")}, b"second"),
        ({"content": bytearray()}, b""),
        ({"content": b"ignored", "json": {}}, b"{}"),
        ({"content": b"second", "json": None}, b"second"),
        ({"data": [("tag", ["a", "b"])]}, b"tag=%5B%27a%27%2C+%27b%27%5D"),
        ({"data": (("tag", ["a", "b"]),)}, b"tag=%5B%27a%27%2C+%27b%27%5D"),
    ],
)
async def test_crawl_sends_selected_bodies(
    body_echo_server: tuple[str, list[tuple[bytes, str]]], overrides: dict[str, Any], body: bytes
) -> None:
    """Send both original requests and filter their equivalent form/raw duplicates."""
    url, received = body_echo_server

    class BodySpider(Spider):
        name = "body_fingerprint"
        concurrent_requests = 1

        def configure_sessions(self, manager: SessionManager) -> None:
            manager.add("default", FetcherSession(stealthy_headers=False, retries=1, timeout=5))

        async def start_requests(self) -> AsyncGenerator[Request, None]:
            yield Request(url, method="POST", headers={"X-Body-Variant": "form"}, data={"tag": ["a", "b"]})
            yield Request(
                url, method="POST", headers={"X-Body-Variant": "selected"}, **{"data": "tag=a&tag=b", **overrides}
            )
            yield Request(url, method="POST", headers={"X-Body-Variant": "duplicate-form"}, data="tag=a&tag=b")
            yield Request(url, method="POST", headers={"X-Body-Variant": "duplicate-selected"}, data=body)

        async def parse(self, response: Response) -> AsyncGenerator[dict[str, Any] | Request | None, None]:
            yield {"url": response.url}

    items = [item async for item in BodySpider().stream()]

    assert received == [(b"tag=a&tag=b", "form"), (body, "selected")]
    assert len(items) == 2


@pytest.mark.asyncio
@pytest.mark.parametrize("form", [{}, {"tag": []}, {"tag": ()}, {"tag": ["a", "b"]}])
@pytest.mark.parametrize("stream_kind", ["buffer", "positioned", "iterator", "with_json"])
async def test_crawl_sends_form_and_content_streams(
    body_echo_server: tuple[str, list[tuple[bytes, str]]], form: dict[str, Any], stream_kind: str
) -> None:
    """Send empty forms and distinct uploads while retaining ordinary deduplication."""
    url, received = body_echo_server
    form_body = urlencode(form, doseq=True).encode()

    class StreamSpider(Spider):
        name = "stream_fingerprint"
        concurrent_requests = 1

        def configure_sessions(self, manager: SessionManager) -> None:
            """Use the real HTTP transport with bounded loopback requests."""
            manager.add("default", FetcherSession(stealthy_headers=False, retries=1, timeout=5))

        async def start_requests(self) -> AsyncGenerator[Request, None]:
            """Queue the maintainer's pair, another upload, and ordinary duplicates."""
            yield Request(url, method="POST", headers={"X-Body-Variant": "form"}, data=form)
            for label, body in (("stream", b"second"), ("mixed-stream", b"third")):
                headers = {"X-Body-Variant": label}
                if stream_kind == "iterator":
                    content = iter([body[:2], body[2:]])
                    headers["Content-Length"] = str(len(body))
                else:
                    content = BytesIO(body if stream_kind != "positioned" else b"prefix-" + body)
                    if stream_kind == "positioned":
                        content.seek(7)
                kwargs: dict[str, Any] = {"content": content}
                if label == "mixed-stream":
                    kwargs["data"] = form
                if stream_kind == "with_json":
                    kwargs["json"] = {}
                yield Request(url, method="POST", headers=headers, **kwargs)
            yield Request(url, method="POST", headers={"X-Body-Variant": "duplicate-form"}, data=form)
            yield Request(url, method="POST", headers={"X-Body-Variant": "duplicate-raw"}, data=form_body)

        async def parse(self, response: Response) -> AsyncGenerator[dict[str, Any] | Request | None, None]:
            """Count successful responses from the real HTTP server."""
            yield {"url": response.url}

    items = [item async for item in StreamSpider().stream()]

    assert received == [(form_body, "form"), (b"second", "stream"), (b"third", "mixed-stream")]
    assert len(items) == 3
