"""Stealth TLS verification against an untrusted local HTTPS server."""

import ssl
import subprocess
from collections.abc import Iterator
from copy import deepcopy
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread

import pytest
from patchright.sync_api import Error as BrowserError

from scrapling.core._types import Any
from scrapling.fetchers import AsyncStealthySession, StealthyFetcher, StealthySession


TLS_CONTENT = "scrapling-local-self-signed-content"


@pytest.fixture
def untrusted_https(tmp_path: Path) -> Iterator[tuple[str, list[str]]]:
    """Serve known content with an untrusted certificate and record HTTP requests."""
    certificate = tmp_path / "certificate.pem"
    private_key = tmp_path / "private_key.pem"
    subprocess.run(
        [
            "openssl",
            "req",
            "-x509",
            "-newkey",
            "rsa:2048",
            "-nodes",
            "-keyout",
            str(private_key),
            "-out",
            str(certificate),
            "-days",
            "1",
            "-subj",
            "/CN=localhost",
            "-addext",
            "subjectAltName=DNS:localhost,IP:127.0.0.1",
        ],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
    )
    private_key.chmod(0o600)
    requests: list[str] = []

    class Handler(BaseHTTPRequestHandler):
        """Return the fixture body only after a successful TLS handshake."""

        def do_GET(self) -> None:
            """Record each HTTP request and return exact identifiable content."""
            requests.append(self.path)
            content = f'<html><body><p id="tls-content">{TLS_CONTENT}</p></body></html>'.encode()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(content)))
            self.end_headers()
            self.wfile.write(content)

        def log_message(self, format: str, *args: Any) -> None:
            """Keep the fixture's access log out of pytest output."""

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(certificate, private_key)
    server.socket = context.wrap_socket(server.socket, server_side=True)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"https://127.0.0.1:{server.server_port}/tls", requests
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)
        assert not thread.is_alive()


@pytest.fixture
def browser_options() -> dict[str, Any]:
    """Use one short browser attempt so certificate errors remain explicit."""
    return {"headless": True, "google_search": False, "timeout": 10000, "retries": 1}


@pytest.mark.browser
@pytest.mark.parametrize("use_session", [False, True], ids=["one_shot", "session"])
@pytest.mark.parametrize("ignore_https_errors", [None, False, True], ids=["default", "verify", "opt_out"])
def test_sync_stealth_tls(
    untrusted_https: tuple[str, list[str]],
    browser_options: dict[str, Any],
    use_session: bool,
    ignore_https_errors: bool | None,
) -> None:
    """Reject untrusted certificates unless the sync caller explicitly opts out."""
    url, requests = untrusted_https
    if ignore_https_errors is not None:
        browser_options["additional_args"] = {"ignore_https_errors": ignore_https_errors}

    def fetch() -> Any:
        """Exercise the public sync one-shot or reusable session API."""
        if use_session:
            with StealthySession(**browser_options) as session:
                return session.fetch(url)
        return StealthyFetcher.fetch(url, **browser_options)

    if ignore_https_errors is True:
        response = fetch()
        assert response.status == 200
        assert response.css("#tls-content::text").get() == TLS_CONTENT
        assert "/tls" in requests
    else:
        with pytest.raises(BrowserError, match="ERR_CERT_AUTHORITY_INVALID") as error:
            fetch()
        assert TLS_CONTENT not in str(error.value)
        assert requests == []


@pytest.mark.browser
@pytest.mark.asyncio
@pytest.mark.parametrize("use_session", [False, True], ids=["one_shot", "session"])
@pytest.mark.parametrize("ignore_https_errors", [None, False, True], ids=["default", "verify", "opt_out"])
async def test_async_stealth_tls(
    untrusted_https: tuple[str, list[str]],
    browser_options: dict[str, Any],
    use_session: bool,
    ignore_https_errors: bool | None,
) -> None:
    """Reject untrusted certificates unless the async caller explicitly opts out."""
    url, requests = untrusted_https
    if ignore_https_errors is not None:
        browser_options["additional_args"] = {"ignore_https_errors": ignore_https_errors}

    async def fetch() -> Any:
        """Exercise the public async one-shot or reusable session API."""
        if use_session:
            async with AsyncStealthySession(**browser_options) as session:
                return await session.fetch(url)
        return await StealthyFetcher.async_fetch(url, **browser_options)

    if ignore_https_errors is True:
        response = await fetch()
        assert response.status == 200
        assert response.css("#tls-content::text").get() == TLS_CONTENT
        assert "/tls" in requests
    else:
        with pytest.raises(BrowserError, match="ERR_CERT_AUTHORITY_INVALID") as error:
            await fetch()
        assert TLS_CONTENT not in str(error.value)
        assert requests == []


@pytest.mark.parametrize("session_type", [StealthySession, AsyncStealthySession])
@pytest.mark.parametrize("ignore_https_errors", [None, False, True], ids=["default", "verify", "opt_out"])
def test_context_options_preserve_explicit_overrides(session_type: Any, ignore_https_errors: bool | None) -> None:
    """Keep context overrides and the caller's dictionary intact."""
    additional_args: dict[str, Any] = {"color_scheme": "dark", "viewport": {"width": 800, "height": 600}}
    if ignore_https_errors is not None:
        additional_args["ignore_https_errors"] = ignore_https_errors
    original = deepcopy(additional_args)
    session = session_type(additional_args=additional_args)

    assert session._context_options["ignore_https_errors"] is (ignore_https_errors is True)
    assert session._context_options["color_scheme"] == "dark"
    assert session._context_options["viewport"] == {"width": 800, "height": 600}
    assert session._context_options["service_workers"] == "allow"
    assert additional_args == original
