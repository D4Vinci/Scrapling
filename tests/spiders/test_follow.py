import logging
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread
from urllib.parse import urlsplit

import pytest

from scrapling.core._types import Any, AsyncGenerator, Iterator
from scrapling.fetchers import FetcherSession
from scrapling.spiders import Request, Response, SessionManager, Spider


@pytest.fixture
def follow_server() -> Iterator[tuple[str, dict[str, dict[str, Any]]]]:
    received: dict[str, dict[str, Any]] = {}

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:
            path = urlsplit(self.path).path
            received[path] = {
                "method": self.command,
                "body": self.rfile.read(int(self.headers.get("Content-Length", "0"))),
                "headers": {key.lower(): value for key, value in self.headers.items()},
            }
            body = b"<html><body>Page</body></html>"
            self.send_response(200)
            if path == "/start":
                self.send_header("Set-Cookie", "site_cookie=kept; Path=/")
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        do_POST = do_GET

        def log_message(self, format: str, *args: Any) -> None:
            pass

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_port}", received
    finally:
        server.shutdown()
        server.server_close()
        thread.join()


@pytest.mark.asyncio
async def test_follow_crawl_inherits_routing_with_fresh_options_and_explicit_overrides(
    follow_server: tuple[str, dict[str, dict[str, Any]]],
) -> None:
    origin, received = follow_server

    class FollowSpider(Spider):
        name = "fresh_follow"
        logging_level = logging.CRITICAL

        def configure_sessions(self, manager: SessionManager) -> None:
            manager.add("public", FetcherSession(stealthy_headers=False, headers={"X-Session": "public"}))
            manager.add("private", FetcherSession(stealthy_headers=False, headers={"X-Session": "private"}))

        async def start_requests(self) -> AsyncGenerator[Request, None]:
            yield Request(
                origin + "/start?token=dummy",
                sid="private",
                callback=self.parse_pages,
                priority=99,
                meta={"seed": "secret"},
                method="POST",
                data="secret body",
                headers={"Authorization": "Bearer seed", "Cookie": "raw=secret", "X-Api-Key": "secret"},
            )

        async def parse_pages(self, response: Response) -> AsyncGenerator[Request | dict[str, Any], None]:
            if urlsplit(response.url).path != "/start":
                assert response.request is not None
                assert response.request.sid == "private"
                assert response.request.priority == 99
                assert response.request.meta == {}
                assert "seed" not in response.meta
                yield {"path": urlsplit(response.url).path, "callback": "inherited"}
                return

            yield response.follow("/default")
            yield response.follow(origin.replace("127.0.0.1", "localhost") + "/cross")
            yield response.follow("/no-referer", referer_flow=False)
            yield response.follow(
                "/explicit",
                sid="public",
                callback=self.parse_explicit,
                priority=0,
                meta={"child": 1},
                headers={"Authorization": "Bearer destination"},
            )

        async def parse(self, response: Response) -> AsyncGenerator[dict[str, Any], None]:
            yield {"path": urlsplit(response.url).path, "callback": "parse"}

        async def parse_explicit(self, response: Response) -> AsyncGenerator[dict[str, Any], None]:
            assert response.request is not None
            assert response.request.sid == "public"
            assert response.request.priority == 0
            assert response.request.meta == {"child": 1}
            assert "seed" not in response.meta
            yield {"path": urlsplit(response.url).path, "callback": "explicit"}

    items = {item["path"]: item["callback"] async for item in FollowSpider().stream()}

    assert items == {
        "/default": "inherited",
        "/cross": "inherited",
        "/no-referer": "inherited",
        "/explicit": "explicit",
    }
    assert received["/start"]["method"] == "POST"
    assert received["/start"]["headers"]["authorization"] == "Bearer seed"
    for path in items:
        request = received[path]
        assert request["method"] == "GET"
        assert request["body"] == b""
        assert "x-api-key" not in request["headers"]
        assert request["headers"].get("referer") == (None if path == "/no-referer" else origin + "/start?token=dummy")
        if path != "/explicit":
            assert request["headers"]["x-session"] == "private"
            assert "authorization" not in request["headers"]
            assert request["headers"].get("cookie") == (None if path == "/cross" else "site_cookie=kept")
    assert received["/explicit"]["headers"]["authorization"] == "Bearer destination"
    assert received["/explicit"]["headers"]["x-session"] == "public"
    assert "cookie" not in received["/explicit"]["headers"]
