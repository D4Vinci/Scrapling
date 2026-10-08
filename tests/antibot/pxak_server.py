"""A local stand-in for HUMAN (PerimeterX) and Akamai pages, for the solver tests.

It serves the fixtures in ``fixtures/pxak`` from ``127.0.0.1`` and keeps just enough server-side state to behave
like the vendors: HUMAN's press-and-hold page that only accepts a long enough hold with pointer movement, Akamai's
SEC-CPT interstitial and 428 JSON (with a real proof-of-work check and the mandatory wait), the SBSD challenge page
that reloads itself, and an edge block that clears once ``_abck`` is valid. Nothing here touches the network.
"""

from __future__ import annotations

import base64
import hashlib
import json
import os
import threading
import time
from contextlib import asynccontextmanager
from http.cookies import SimpleCookie
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlsplit

import pytest

FIXTURES = os.path.join(os.path.dirname(__file__), "fixtures", "pxak")
PARAGRAPHS = "\n".join(
    f"<p>Paragraph {i}: a cordless drill drives screws and bores holes; this listing compares torque, battery "
    f"capacity, chuck size and weight across the models we carry, with prices and delivery times.</p>"
    for i in range(30)
)
SBSD_PATH = "/Gq7p/Rf/k2/sbsd"
SENSOR_PATH = "/x5Kq/Ab1/cd2/EfG3/sensor"


def fixture(name: str, **values: object) -> str:
    """A fixture file with its ``%NAME%`` placeholders filled."""
    with open(os.path.join(FIXTURES, name), encoding="utf-8") as handle:
        text = handle.read()
    values.setdefault("PARAGRAPHS", PARAGRAPHS)
    for key, value in values.items():
        text = text.replace(f"%{key}%", str(value))
    return text


def hyper_pow_ok(sec: str, challenge: dict, answers: list) -> bool:
    """Akamai's SEC-CPT check, written the way Hyper's SDK loops over the digest bytes (independent of the port)."""
    difficulty = challenge["difficulty"]
    for answer in answers:
        output = 0
        for byte in hashlib.sha256(
            f"{sec}{challenge['timestamp']}{challenge['nonce']}{difficulty}{answer}".encode()
        ).digest():
            output = ((output << 8) | byte) % difficulty
        if output != 0:
            return False
        difficulty += 1
    return len(answers) == challenge["count"]


class State:
    """Server-side knobs and counters; tests change the knobs with :meth:`FixtureServer.reset`."""

    def __init__(self, **overrides: object) -> None:
        # HUMAN
        self.px_need_ms = 3000
        self.px_fill_ms = 3000
        self.px_always_fail = False
        self.px_holds: list = []
        self.px_block_after_hold = False
        # Akamai SEC-CPT
        self.sec_provider = "crypto"
        self.sec_duration = 1
        self.sec_self_solve = False
        self.sec_difficulty = 1500
        self.sec_count = 2
        self.sec_challenges: dict = {}
        self.sec_verify_posts: list = []
        # Akamai SBSD
        self.sbsd_delay_ms = 600
        self.sbsd_posts = 0
        # Akamai edge block / sensor
        self.root_blocked = False
        self.sensor_posts_needed = 2
        self.sensor_posts = 0
        self.paths: list = []
        for key, value in overrides.items():
            if not hasattr(self, key):
                raise AttributeError(key)
            setattr(self, key, value)


class _Handler(BaseHTTPRequestHandler):
    server: "_Server"

    def log_message(self, *_: object) -> None:  # quiet
        pass

    # plumbing ----------------------------------------------------------------------------------------------

    @property
    def state(self) -> State:
        return self.server.state

    def cookies(self) -> dict:
        jar = SimpleCookie()
        jar.load(self.headers.get("Cookie", ""))
        return {k: v.value for k, v in jar.items()}

    def body(self) -> bytes:
        length = int(self.headers.get("Content-Length") or 0)
        return self.rfile.read(length) if length else b""

    def send(self, status: int, text: str, ctype: str = "text/html; charset=utf-8", cookies=(), akamai=False) -> None:
        data = text.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        if akamai:
            self.send_header("Server", "AkamaiGHost")
        for cookie in cookies:
            self.send_header("Set-Cookie", cookie + "; Path=/")
        self.end_headers()
        self.wfile.write(data)

    # routes -----------------------------------------------------------------------------------------------------

    def do_GET(self) -> None:  # noqa: N802
        url = urlsplit(self.path)
        path, query = url.path, parse_qs(url.query)
        cookies = self.cookies()
        self.state.paths.append(("GET", path))
        s = self.state

        if path == "/px/protected":
            if s.px_block_after_hold and s.px_holds:
                block = (
                    "<html><head><title>Access to this page has been denied</title></head><body>Blocked.</body></html>"
                )
                return self.send(403, block)
            if cookies.get("_px3") == "good":
                return self.send(200, fixture("content.html"))
            return self.send(403, fixture("px_block.html"), cookies=["_pxhd=hd-test", "_pxvid=vid-test"])
        if path == "/px/widget":
            return self.send(
                200,
                fixture(
                    "px_widget.html",
                    NEED_MS=s.px_need_ms,
                    FILL_MS=s.px_fill_ms,
                    ALWAYS_FAIL=str(s.px_always_fail).lower(),
                ),
            )

        if path == "/":
            if s.root_blocked:
                return self.send(403, fixture("akamai_access_denied.html", HOST=self.headers.get("Host")), akamai=True)
            new = [] if "_abck" in cookies else ["_abck=A1B2C3D4E5~-1~YAAQtest~-1~-1~-1", "bm_sz=SZtest~1"]
            return self.send(200, fixture("akamai_root.html"), cookies=new, akamai=True)
        if path == SENSOR_PATH:
            return self.send(200, fixture("akamai_sensor.js"), ctype="application/javascript", akamai=True)
        if path == "/strict/search":
            if "~0~" in cookies.get("_abck", ""):
                return self.send(200, fixture("content.html"), akamai=True)
            return self.send(
                403,
                fixture("akamai_access_denied.html", HOST=self.headers.get("Host")),
                cookies=["ak_bmsc=bmsc-test"],
                akamai=True,
            )

        if path == "/sec/page":
            if "~3~" in cookies.get("sec_cpt", ""):
                return self.send(200, fixture("content.html"), akamai=True)
            sec, challenge = self.new_sec_challenge()
            encoded = base64.b64encode(json.dumps(challenge).encode()).decode()
            html = fixture(
                "akamai_sec_cpt.html",
                PROVIDER=s.sec_provider,
                CHALLENGE=encoded,
                DURATION=s.sec_duration,
                SELF="?self=1" if s.sec_self_solve else "",
            )
            return self.send(200, html, cookies=[f"sec_cpt={sec}~1~{challenge['token'][:8]}~-1"], akamai=True)
        if path == "/sec/loop":
            html = fixture("akamai_sec_cpt.html", PROVIDER="behavioral", CHALLENGE="", DURATION=1, SELF="?loop=1")
            return self.send(200, html, akamai=True)
        if path == "/_sec/cp_challenge/ak-challenge-4-3.htm":
            return self.send(200, fixture("akamai_sec_cpt_iframe.html"), akamai=True)
        if path == "/_sec/cp_challenge/verify":
            sec = cookies.get("sec_cpt", "").split("~")[0]
            entry = s.sec_challenges.get(sec)
            if entry and entry.get("verified"):
                return self.send(
                    200, '{"success":"true"}', "application/json", cookies=[f"sec_cpt={sec}~3~done~-1"], akamai=True
                )
            return self.send(200, '{"success":"false"}', "application/json", akamai=True)
        if path == "/sec/api":
            if "~3~" in cookies.get("sec_cpt", ""):
                return self.send(200, '{"items":[1,2,3]}', "application/json", akamai=True)
            sec, challenge = self.new_sec_challenge()
            payload = dict(challenge)
            payload.update(
                {
                    "sec-cp-challenge": "true",
                    "provider": "crypto",
                    "chlg_duration": s.sec_duration,
                    "branding_url_content": "/_sec/cp_challenge/crypto_message-4-3.htm",
                    "timeout": 1000,
                }
            )
            return self.send(
                428, json.dumps(payload), "application/json", cookies=[f"sec_cpt={sec}~1~json~-1"], akamai=True
            )

        if path == "/sbsd/page":
            if cookies.get("sbsd") == "ok":
                return self.send(200, fixture("content.html"), akamai=True)
            return self.send(200, fixture("akamai_sbsd.html"), cookies=["bm_so=so-test"], akamai=True)
        if path == "/sbsd/passive":
            if cookies.get("sbsd") == "ok":
                return self.send(200, fixture("content.html"), akamai=True)
            return self.send(403, fixture("akamai_sbsd_passive.html"), cookies=["bm_so=so-test"], akamai=True)
        if path == SBSD_PATH and query.get("v") == ["4c3b2a19-0e8d-4f7a-9b6c-5d4e3f2a1b0c"]:
            return self.send(200, fixture("akamai_sbsd_passive.js"), ctype="application/javascript", akamai=True)
        if path == SBSD_PATH and "v" in query:
            return self.send(
                200, fixture("akamai_sbsd.js", DELAY_MS=s.sbsd_delay_ms), ctype="application/javascript", akamai=True
            )

        self.send(404, "<html><body>not found</body></html>")

    def do_POST(self) -> None:  # noqa: N802
        url = urlsplit(self.path)
        path, query = url.path, parse_qs(url.query)
        cookies, body = self.cookies(), self.body()
        self.state.paths.append(("POST", path))
        s = self.state

        if path == "/px/collect":
            s.px_holds.append(("ok", json.loads(body or b"{}")))
            return self.send(200, "{}", "application/json", cookies=["_px3=good", "pxcts=cts-test"])
        if path == "/px/fail":
            s.px_holds.append(("fail", json.loads(body or b"{}")))
            return self.send(200, "{}", "application/json")

        if path == SENSOR_PATH:
            if not body.startswith(b'{"sensor_data"'):
                return self.send(400, "{}", "application/json", akamai=True)
            s.sensor_posts += 1
            mark = "0" if s.sensor_posts >= s.sensor_posts_needed else "-1"
            return self.send(
                200,
                '{"success": true}',
                "application/json",
                cookies=[f"_abck=A1B2C3D4E5~{mark}~YAAQtest{s.sensor_posts}~-1~-1~-1"],
                akamai=True,
            )

        if path == "/_sec/verify":
            sec = cookies.get("sec_cpt", "").split("~")[0]
            entry = s.sec_challenges.get(sec)
            data = json.loads(body or b"{}")
            s.sec_verify_posts.append(
                {"provider": query.get("provider", [""])[0], "answers": len(data.get("answers", []))}
            )
            early = entry is not None and time.monotonic() - entry["issued"] < entry["challenge"]["duration"]
            if (
                entry
                and not early
                and data.get("token") == entry["challenge"]["token"]
                and hyper_pow_ok(sec, entry["challenge"], data.get("answers", []))
            ):
                entry["verified"] = True
                return self.send(200, '{"success":"true"}', "application/json", akamai=True)
            return self.send(
                400, '{"success":"false","early":%s}' % str(early).lower(), "application/json", akamai=True
            )
        if path == "/_sec/cp_challenge/self-solve":
            sec = cookies.get("sec_cpt", "").split("~")[0]
            return self.send(200, "{}", "application/json", cookies=[f"sec_cpt={sec}~3~self~-1"], akamai=True)

        if path == SBSD_PATH and "t" not in query and body.startswith(b'{"body"'):
            s.sbsd_posts += 1
            done = ["sbsd=ok", "sbsd_o=o-test"] if s.sbsd_posts >= 2 else ["sbsd_o=o-test"]
            return self.send(200, "{}", "application/json", cookies=done, akamai=True)
        if path == SBSD_PATH and query.get("t") == ["183446611"]:
            if body.startswith(b'{"body"'):
                s.sbsd_posts += 1
                return self.send(200, "{}", "application/json", cookies=["sbsd=ok", "sbsd_o=o-test"], akamai=True)
            return self.send(400, "{}", "application/json", akamai=True)

        self.send(404, "{}", "application/json")

    def new_sec_challenge(self):
        s = self.state
        sec = hashlib.sha1(os.urandom(8)).hexdigest()[:20].upper()
        challenge = {
            "token": "tok-" + os.urandom(6).hex(),
            "timestamp": int(time.time()),
            "nonce": os.urandom(10).hex(),
            "difficulty": s.sec_difficulty,
            "count": s.sec_count,
            "duration": s.sec_duration,
        }
        s.sec_challenges[sec] = {"challenge": challenge, "issued": time.monotonic(), "verified": False}
        return sec, challenge


class _Server(ThreadingHTTPServer):
    daemon_threads = True
    state: State


class FixtureServer:
    """Runs the fixture site on ``127.0.0.1`` in a background thread."""

    def __init__(self) -> None:
        self.httpd = _Server(("127.0.0.1", 0), _Handler)
        self.httpd.state = State()
        self.thread = threading.Thread(target=self.httpd.serve_forever, daemon=True)
        self.thread.start()

    @property
    def state(self) -> State:
        return self.httpd.state

    def reset(self, **overrides: object) -> State:
        """Fresh state with ``overrides`` applied (knobs named as in :class:`State`)."""
        self.httpd.state = State(**overrides)
        return self.httpd.state

    def url(self, path: str) -> str:
        return f"http://127.0.0.1:{self.httpd.server_address[1]}{path}"

    def close(self) -> None:
        self.httpd.shutdown()
        self.httpd.server_close()


@asynccontextmanager
async def browser_page():
    """A fresh headless Chromium page (Patchright when installed, else Playwright), sandbox on.

    ``SCRAPLING_TEST_CHROME`` may point at a Chromium-compatible executable; otherwise the driver's own browser is
    used. The test is skipped when no browser can be launched.
    """
    try:
        from patchright.async_api import async_playwright
    except ImportError:  # pragma: no cover
        from playwright.async_api import async_playwright
    executable = os.environ.get("SCRAPLING_TEST_CHROME") or None
    async with async_playwright() as driver:
        try:
            browser = await driver.chromium.launch(headless=True, executable_path=executable, chromium_sandbox=True)
        except Exception as error:  # pragma: no cover - no browser installed
            pytest.skip(f"no browser: {type(error).__name__}")
        try:
            context = await browser.new_context(viewport={"width": 1280, "height": 800})
            page = await context.new_page()
            yield page
        finally:
            await browser.close()
