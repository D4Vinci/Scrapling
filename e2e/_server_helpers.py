from contextlib import contextmanager
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread
from typing import Any


@contextmanager
def _serve_mock(html: bytes, host: str = "0.0.0.0"):
    class _Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(html)))
            self.end_headers()
            self.wfile.write(html)

        def log_message(self, *args: Any, **kwargs: Any) -> None:
            pass

    server = ThreadingHTTPServer((host, 0), _Handler)
    Thread(target=server.serve_forever, daemon=True).start()
    port = server.server_address[1]
    try:
        yield f"http://127.0.0.1:{port}/", f"http://host.docker.internal:{port}/"
    finally:
        server.shutdown()
        server.server_close()
