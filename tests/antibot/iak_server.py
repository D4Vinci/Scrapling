"""A local stand-in for Imperva, AWS WAF and Kasada pages, for the in-browser solver tests.

Served from ``127.0.0.1``; nothing touches the network. Each flow keeps the part of the vendor's behaviour the
solvers depend on, with the vendor's own page shapes (taken from the public descriptions in Hyper Solutions' docs
and AWS's WAF documentation) but none of their scripts:

* ``/imperva``: the reese84 interstitial ("Pardon Our Interruption", interstitial hooks); its script posts to a
  sensor path (``?d=<host>``), stores the returned ``reese84`` token and reloads. ``?stall=1`` stores the cookie
  but never reloads.
* ``/aws/challenge``: HTTP 202 + ``x-amzn-waf-action: challenge`` with ``gokuProps``; the script stores
  ``aws-waf-token`` and reloads (``?stall=1``: no reload).
* ``/aws/captcha``: HTTP 405 + ``x-amzn-waf-action: captcha`` with an ``<awswaf-captcha>`` element (open shadow
  root): "Begin" fetches ``/problem`` (nine images and a target), the canvas takes cell clicks, "Confirm" posts them
  to ``/verify``; a right answer stores the token and reloads.
* ``/kasada``: HTTP 429 with the KPSDK bootstrap and ``/<uuid>/<uuid>/ips.js``; the script posts to ``/tl``, which
  answers ``x-kpsdk-ct``/``x-kpsdk-st`` and sets ``KP_UIDz``, then reloads.
"""

from __future__ import annotations

import base64
import json
import threading
from http.cookies import SimpleCookie
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlsplit

from .iak_fakes import PARAGRAPHS

KASADA = "/149e9513-01fa-4fb0-aad4-566afd725d1b/2d206a39-8ed7-437e-a3be-862e0f06eea3"
REESE_PATH = "/Onalbaine-legeance-what-come/14167535692918208311"
AWS_ANSWER = [0, 4, 8]
LOADER = '<script src="/_Incapsula_Resource?SWJIYLWA=719d34d31c8e3a6e6fffd425f7e032f3"></script>'
CONTENT = (
    "<!doctype html><html><head><title>Catalogue</title>%s</head><body><h1>Catalogue</h1>" + PARAGRAPHS + "</body></html>"
)
GOKU = '{"key":"AQIDAHjcYu/GjX+QlghicBgQ/7bFaQZ+m5FKCMDnO+vTbNg96AE","iv":"CgAHbCe2GgAAAAAA","context":"Q2tJ+ctx=="}'

IMPERVA_INTERSTITIAL = (
    f"<!DOCTYPE html><html><head><title>Pardon Our Interruption</title>{LOADER}"
    "<script>window.reeseSkipExpirationCheck = true;</script></head><body>"
    '<div id="interstitial-inprogress"><h1>Pardon Our Interruption</h1><p>As you were browsing something about your '
    "browser made us think you were a bot.</p></div><script>"
    "setTimeout(async () => {"
    f" const r = await fetch('{REESE_PATH}?d=' + location.hostname, {{method: 'POST', body: 'sensor'}});"
    " const t = await r.json();"
    " document.cookie = 'reese84=' + t.token + '; path=/';"
    " if (!location.search.includes('stall')) location.reload();"
    "}, 600);</script></body></html>"
)
AWS_CHALLENGE = (
    f"<!DOCTYPE html><html><head><script>window.awsWafCookieDomainList = [];window.gokuProps = {GOKU};</script>"
    '<script src="/aws/challenge.js"></script></head><body><div id="challenge-container"></div><script>'
    "setTimeout(() => { document.cookie = 'aws-waf-token=valid; path=/';"
    " if (!location.search.includes('stall')) location.reload(); }, 700);</script></body></html>"
)
AWS_CAPTCHA = (
    f"<!DOCTYPE html><html><head><title>Human Verification</title><script>window.gokuProps = {GOKU};</script></head>"
    '<body><div id="captcha-container"><awswaf-captcha></awswaf-captcha></div><script>'
    "customElements.define('awswaf-captcha', class extends HTMLElement { connectedCallback() {"
    " const root = this.attachShadow({mode: 'open'}); const picked = new Set();"
    " root.innerHTML = '<div id=\"root\"><p class=\"amzn-captcha-modal-title\">Let\\'s confirm you are human</p>"
    '<button id="amzn-captcha-verify-button" type="button">Begin</button></div>\';'
    " root.querySelector('button').addEventListener('click', async () => {"
    "  const p = await (await fetch('/aws/problem?kind=visual')).json();"
    "  root.innerHTML = '<p>Choose all the ' + JSON.parse(p.assets.target) + '</p>"
    '<canvas width="320" height="320" style="width:320px;height:320px;background:#ccc"></canvas>'
    '<button id="amzn-btn-verify-internal" type="button">Confirm</button>\';'
    "  const canvas = root.querySelector('canvas');"
    "  canvas.addEventListener('click', e => { const r = canvas.getBoundingClientRect();"
    "   const col = Math.floor((e.clientX - r.left) / (r.width / 3)), row = Math.floor((e.clientY - r.top) / (r.height / 3));"
    "   picked.add(row * 3 + col); });"
    "  root.querySelector('button').addEventListener('click', async () => {"
    "   const v = await (await fetch('/aws/verify', {method: 'POST', body: JSON.stringify({client_solution: [...picked]})})).json();"
    "   if (v.success) { document.cookie = 'aws-waf-token=captcha-ok; path=/'; location.reload(); } });"
    " }); } });"
    "</script></body></html>"
)
KASADA_BLOCK = (
    "<!DOCTYPE html><html><head></head><body><script>window.KPSDK={};KPSDK.now=typeof performance!=='undefined'"
    "&&performance.now?performance.now.bind(performance):Date.now.bind(Date);KPSDK.start=KPSDK.now();</script>"
    f'<script src="{KASADA}/ips.js?tkrm_alpekz_s1.3=0Zhprgz&amp;x-kpsdk-im=AAIHh6y"></script></body></html>'
)
KASADA_IPS = (
    "setTimeout(async () => {"
    f" const r = await fetch('{KASADA}/tl', {{method: 'POST', headers: {{'Content-Type': 'application/octet-stream'}},"
    " body: new Uint8Array([1, 2, 3])}); const j = await r.json(); if (j.reload) location.reload(); }, 500);"
)


class State:
    def __init__(self) -> None:
        self.paths: list = []
        self.verify: list = []
        self.sensor_posts = 0
        self.tl_posts = 0


class _Handler(BaseHTTPRequestHandler):
    server: "_Server"

    def log_message(self, *_: object) -> None:  # quiet
        pass

    def cookies(self) -> dict:
        jar = SimpleCookie()
        jar.load(self.headers.get("Cookie", ""))
        return {k: v.value for k, v in jar.items()}

    def send(self, status: int, text: str, ctype: str = "text/html; charset=utf-8", headers=None, cookies=()) -> None:
        data = text.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        for name, value in (headers or {}).items():
            self.send_header(name, value)
        for cookie in cookies:
            self.send_header("Set-Cookie", cookie + "; Path=/")
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self) -> None:  # noqa: N802
        url = urlsplit(self.path)
        path = url.path
        cookies = self.cookies()
        state = self.server.state
        state.paths.append(("GET", path))
        imperva = {"X-Iinfo": "8-12345-0 0NNN RT(1 0) q(0 -1 -1 -1) r(0 -1)", "X-CDN": "Imperva"}
        if path == "/imperva":
            if cookies.get("reese84"):
                return self.send(200, CONTENT % LOADER, headers=imperva)
            return self.send(200, IMPERVA_INTERSTITIAL, headers=imperva, cookies=["incap_ses_1_2=s", "visid_incap_2=v"])
        if path == "/aws/challenge":
            if cookies.get("aws-waf-token") == "valid":
                return self.send(200, CONTENT % "")
            return self.send(202, AWS_CHALLENGE, headers={"x-amzn-waf-action": "challenge"})
        if path == "/aws/captcha":
            if cookies.get("aws-waf-token") == "captcha-ok":
                return self.send(200, CONTENT % "")
            return self.send(405, AWS_CAPTCHA, headers={"x-amzn-waf-action": "captcha"})
        if path == "/aws/challenge.js":
            return self.send(200, "window.AwsWafIntegration = {};", "application/javascript")
        if path == "/aws/problem":
            tile = base64.b64encode(b"\x89PNG\r\n\x1a\n tile").decode()
            problem = {
                "problem_type": "HumanCaptchaGridProblem",
                "assets": {"images": json.dumps([tile] * 9), "target": json.dumps("bed")},
                "localized_assets": {"target0": "beds"},
            }
            return self.send(200, json.dumps(problem), "application/json", headers={"Access-Control-Allow-Origin": "*"})
        if path == "/kasada":
            if cookies.get("KP_UIDz"):
                return self.send(200, CONTENT % "", headers={"x-kpsdk-ct": "03refreshed"})
            return self.send(429, KASADA_BLOCK, headers={"x-kpsdk-ct": "0init", "x-kpsdk-r": "1-B"})
        if path == f"{KASADA}/ips.js":
            return self.send(200, KASADA_IPS, "application/javascript")
        return self.send(404, "<html><body>not found</body></html>")

    def do_POST(self) -> None:  # noqa: N802
        url = urlsplit(self.path)
        path, query = url.path, parse_qs(url.query)
        length = int(self.headers.get("Content-Length") or 0)
        body = self.rfile.read(length) if length else b""
        state = self.server.state
        state.paths.append(("POST", path))
        if path == REESE_PATH and "d" in query:
            state.sensor_posts += 1
            token = {"token": "3:reese-token", "renewInSec": 896, "cookieDomain": query["d"][0]}
            return self.send(200, json.dumps(token), "application/json")
        if path == "/aws/verify":
            solution = json.loads(body or b"{}").get("client_solution", [])
            state.verify.append(sorted(solution))
            ok = sorted(solution) == AWS_ANSWER
            return self.send(200, json.dumps({"success": ok, "captcha_voucher": "v" if ok else ""}), "application/json")
        if path == f"{KASADA}/tl":
            state.tl_posts += 1
            return self.send(
                200,
                json.dumps({"reload": True}),
                "application/json",
                headers={"x-kpsdk-ct": "02tlvalue", "x-kpsdk-st": "1759149934586"},
                cookies=["KP_UIDz=02tlvalue", "KP_UIDz-ssn=02tlvalue"],
            )
        return self.send(404, "{}", "application/json")


class _Server(ThreadingHTTPServer):
    daemon_threads = True
    state: State


class IakServer:
    """Runs the stand-in site on ``127.0.0.1`` in a background thread."""

    def __init__(self) -> None:
        self.httpd = _Server(("127.0.0.1", 0), _Handler)
        self.httpd.state = State()
        self.thread = threading.Thread(target=self.httpd.serve_forever, daemon=True)
        self.thread.start()

    @property
    def state(self) -> State:
        return self.httpd.state

    def reset(self) -> State:
        self.httpd.state = State()
        return self.httpd.state

    def url(self, path: str) -> str:
        return f"http://127.0.0.1:{self.httpd.server_address[1]}{path}"

    def close(self) -> None:
        self.httpd.shutdown()
        self.httpd.server_close()
