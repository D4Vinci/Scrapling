"""A local stand-in for a DataDome-protected site, for the DataDome solver tests.

The protected page is served from ``http://127.0.0.1:<port>`` and the challenge frames from
``http://localhost:<port>``: a different site, so Chrome runs them in an out-of-process iframe exactly like
``geo.captcha-delivery.com``. The flow copies DataDome's shape, not its code:

* ``/dd/<scenario>`` answers 403 with ``x-dd-b``, a ``datadome`` cookie and an inline ``var dd={...}`` verdict, then
  inserts the challenge iframe. When the frame posts ``pass``, the page stores a new ``datadome`` cookie and
  reloads; a request carrying the cleared cookie gets the 200 content page.
* ``/interstitial/`` is the device check. Scenarios: ``pass`` (clears after a moment), ``confirm`` (a trusted click on
  the confirm button clears it), ``check`` (clears only when the frame's screen, window and client hints agree
  with the top page's, else escalates to the slider), ``restricted`` (a restricted-device notice that never moves)
  and ``hang`` (never resolves).
* ``/captcha/`` is an ArgoZhang-style jigsaw slider laid out like DataDome's live one (2026-10-08): a background
  ``canvas`` with a gap and a full-width ``canvas.block`` layer with the piece inside it, both 0 px high until the
  images "load", and the ``.slider`` handle in ``.sliderContainer`` beside ``.sliderTarget``. Trusted drags that
  leave the piece within 5 px of the gap with a non-flat vertical trail clear it. ``scenario=simple`` is the
  slide-to-target variant DataDome served live (``#captcha__frame.simple``, canvases never drawn): the handle must end
  on ``.sliderTarget``. ``t=bv`` in its URL serves the hard-block page instead.
"""

from __future__ import annotations

import json
import os
import random
import threading
from contextlib import asynccontextmanager
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlsplit

CONTENT = "<html><head><title>Example store</title></head><body><main><h1>Products</h1>%s</main></body></html>" % (
    "<p>" + "Lorem ipsum dolor sit amet, consectetur adipiscing elit. " * 60 + "</p>"
)

BLOCK_PAGE = """<html lang="en"><head><title>example.test</title><style>body{margin:0}</style></head><body>
<script data-cfasync="false">var dd={'rt':'%(rt)s','cid':'AHrlqAAAAAMA-test','hsh':'TESTHASH','t':'%(t)s','s':43337,'e':'x','qp':'','host':'geo.captcha-delivery.com','cookie':'initial'}</script>
<script>
(function () {
  var origin = %(frame_origin)s;
  var frame = document.createElement('iframe');
  frame.src = origin + %(frame_path)s;
  frame.width = '100%%'; frame.height = '640'; frame.setAttribute('frameborder', '0');
  frame.style.border = '0'; frame.style.display = 'block';
  document.body.appendChild(frame);
  function me() {
    var ua = navigator.userAgentData;
    return {sw: screen.width, sh: screen.height, at: screen.availTop, cd: screen.colorDepth, dpr: devicePixelRatio,
            ow: outerWidth, oh: outerHeight, ih: innerHeight,
            brands: ua ? ua.brands.map(function (b) { return b.brand; }) : [], ua: navigator.userAgent};
  }
  window.addEventListener('message', function (e) {
    if (e.origin !== origin) return;
    var d = e.data || {};
    if (d.type === 'top?') frame.contentWindow.postMessage({type: 'top', top: me()}, origin);
    if (d.type === 'reject') document.cookie = 'datadome=' + d.cookie + '; path=/';
    if (d.type === 'pass') { document.cookie = 'datadome=' + d.cookie + '; path=/'; location.reload(); }
  });
})();
</script></body></html>"""

INTERSTITIAL = """<html><head><title>DataDome Device Check</title></head><body>
<p data-dd-captcha-human-title>%(title)s</p>
%(button)s
<script>
var scenario = %(scenario)s, parentOrigin = %(parent_origin)s;
function post(m) { parent.postMessage(m, parentOrigin); }
function me() {
  var ua = navigator.userAgentData;
  return {sw: screen.width, sh: screen.height, at: screen.availTop, cd: screen.colorDepth, dpr: devicePixelRatio,
          ow: outerWidth, oh: outerHeight, brands: ua ? ua.brands.map(function (b) { return b.brand; }) : [],
          ua: navigator.userAgent, ih: innerHeight};
}
function escalate() { location.href = '/captcha/?scenario=slider&initialCid=AHrlqAAAAAMA-test&cid=x'; }
if (scenario === 'pass') setTimeout(function () { post({type: 'pass', cookie: 'cleared-pass'}); }, 1200);
if (scenario === 'check') {
  window.addEventListener('message', function (e) {
    if (e.origin !== parentOrigin || (e.data || {}).type !== 'top') return;
    var t = e.data.top, m = me(), why = [];
    ['sw', 'sh', 'at', 'cd', 'dpr', 'ow', 'oh'].forEach(function (k) { if (t[k] !== m[k]) why.push(k); });
    if (t.oh - t.ih <= 1) why.push('outer');
    if (m.sw === 800 && m.sh === 600) why.push('headless-screen');
    if (m.brands.indexOf('Google Chrome') < 0) why.push('brand');
    if (m.ua.indexOf('HeadlessChrome') >= 0 || t.ua.indexOf('HeadlessChrome') >= 0) why.push('ua');
    fetch('/report', {method: 'POST', body: JSON.stringify({why: why, frame: m, top: t})}).finally(function () {
      if (why.length) { post({type: 'reject', cookie: 'rejected-check'}); setTimeout(escalate, 300); }
      else setTimeout(function () { post({type: 'pass', cookie: 'cleared-check'}); }, 800);
    });
  });
  setTimeout(function () { post({type: 'top?'}); }, 300);
}
var button = document.querySelector('button.captcha_display_button_submit');
if (button) button.addEventListener('click', function (e) {
  if (e.isTrusted) post({type: 'pass', cookie: 'cleared-confirm'});
});
</script></body></html>"""

SLIDER = """<html><head><title>DataDome CAPTCHA</title><style>
body { margin: 0; font-family: sans-serif; }
#captcha__puzzle { position: relative; width: 280px; height: 155px; margin: 40px; }
#captcha__puzzle canvas { position: absolute; top: 0; left: 0; width: 280px; height: 155px; }
.sliderContainer { position: relative; width: 280px; height: 40px; margin: 15px 40px; background: #e8e8e8; }
.slider { position: absolute; top: 0; left: 0; width: 40px; height: 40px; background: #1991fa; cursor: pointer; }
.sliderTarget { position: absolute; top: 0; right: 0; width: 40px; height: 40px; }
</style></head><body class="%(body_class)s">
<div id="captcha-container" class="captcha"><div class="captcha__human"><p class="captcha__human__title">%(title)s</p></div>
<div id="ddv1-captcha-container" class="captcha__ddv1"><div id="captcha__frame" class="%(frame_class)s"><div id="captcha__element">
<div id="captcha__puzzle" class="toggled"><canvas width="560" height="0"></canvas><canvas class="block" width="560" height="0"></canvas></div>
<div id="captcha__frame__bottom" class="toggled"><div class="sliderText"><p>Slide right to complete the puzzle</p></div>
<div class="sliderContainer"><div class="sliderbg"></div><div class="sliderMask"></div><div class="sliderTarget"></div><div class="slider"></div></div></div>
</div></div></div></div>
<script>
var parentOrigin = %(parent_origin)s, gap = %(gap)d, pieceX = 12, gapY = 120, W = 280, simple = %(simple)s;
var canvases = document.querySelectorAll('#captcha__puzzle canvas'), bg = canvases[0], block = canvases[1];
var slider = document.querySelector('.slider');
// DataDome draws the puzzle once its images load; the canvases are 0 px high until then.
if (!simple) setTimeout(function draw() {
  bg.height = 310; block.height = 310;
  var c = bg.getContext('2d');
  var g = c.createLinearGradient(0, 0, 560, 310); g.addColorStop(0, '#5a7'); g.addColorStop(1, '#258');
  c.fillStyle = g; c.fillRect(0, 0, 560, 310);
  c.fillStyle = 'rgba(0,0,0,0.55)'; c.fillRect(gap, gapY, 80, 80);
  var b = block.getContext('2d'); b.fillStyle = '#ddd'; b.fillRect(pieceX, gapY, 80, 80);
}, 700);
var down = false, originX = 0, originY = 0, trail = [], trusted = true;
slider.addEventListener('mousedown', function (e) {
  down = true; originX = e.clientX; originY = e.clientY; trail = []; trusted = e.isTrusted;
});
document.addEventListener('mousemove', function (e) {
  if (!down) return;
  trusted = trusted && e.isTrusted;
  var moveX = Math.max(0, Math.min(W - 40, e.clientX - originX));
  slider.style.left = moveX + 'px';
  block.style.left = ((W - 60) / (W - 40) * moveX) + 'px';
  trail.push(e.clientY - originY);
});
document.addEventListener('mouseup', function (e) {
  if (!down) return;
  down = false;
  var left = (parseFloat(block.style.left) || 0) + pieceX / 2;
  var mean = trail.reduce(function (a, b) { return a + b; }, 0) / Math.max(1, trail.length);
  var sd = Math.sqrt(trail.reduce(function (a, b) { return a + (b - mean) * (b - mean); }, 0) / Math.max(1, trail.length));
  var handleCenter = (parseFloat(slider.style.left) || 0) + 20;
  var placed = simple ? Math.abs(handleCenter - (W - 20)) < 10 : Math.abs(left - gap / 2) < 5;
  var ok = trusted && e.isTrusted && placed && sd !== 0;
  fetch('/report', {method: 'POST', body: JSON.stringify({slider: {left: left, gapCss: gap / 2, sd: sd, trusted: trusted, ok: ok}})})
    .finally(function () {
      if (ok) parent.postMessage({type: 'pass', cookie: simple ? 'cleared-simple' : 'cleared-slider'}, parentOrigin);
      else { slider.style.left = '0px'; block.style.left = '0px'; }
    });
});
</script></body></html>"""

#: Scenario -> (rt, t, frame path, x-dd-b)
SCENARIOS = {
    "pass": ("i", "fe", "/interstitial/?scenario=pass", "259"),
    "confirm": ("i", "fe", "/interstitial/?scenario=confirm", "3"),
    "check": ("i", "fe", "/interstitial/?scenario=check", "259"),
    "restricted": ("i", "fe", "/interstitial/?scenario=restricted", "3"),
    "hang": ("i", "fe", "/interstitial/?scenario=hang", "3"),
    "slider": ("c", "fe", "/captcha/?scenario=slider", "1"),
    "simple": ("c", "fe", "/captcha/?scenario=simple", "1"),
    "ban": ("c", "bv", "/captcha/?scenario=slider&t=bv", "1"),
}


class _State:
    def __init__(self) -> None:
        self.lock = threading.Lock()
        self.reports: list = []
        self.requests: list = []
        self.gap = 300


class DataDomeFixture:
    """The fixture server. ``url(path)`` is on the protected site; ``frame_origin`` is the challenge frames' site."""

    def __init__(self) -> None:
        state = self.state = _State()

        class Handler(BaseHTTPRequestHandler):
            def log_message(self, *args):  # silence
                pass

            def _send(self, status: int, body: str, headers: dict | None = None) -> None:
                data = body.encode()
                self.send_response(status)
                self.send_header("content-type", "text/html; charset=utf-8")
                self.send_header("cache-control", "no-store")
                for key, value in (headers or {}).items():
                    self.send_header(key, value)
                self.send_header("content-length", str(len(data)))
                self.end_headers()
                self.wfile.write(data)

            def do_POST(self):
                size = int(self.headers.get("content-length", 0) or 0)
                try:
                    payload = json.loads(self.rfile.read(size) or b"{}")
                except ValueError:
                    payload = {}
                with state.lock:
                    state.reports.append(payload)
                self.send_response(204)
                self.end_headers()

            def do_GET(self):
                parts = urlsplit(self.path)
                query = parse_qs(parts.query)
                port = self.server.server_address[1]
                with state.lock:
                    state.requests.append(
                        {
                            "path": self.path,
                            "host": self.headers.get("host", ""),
                            "ua": self.headers.get("user-agent", ""),
                            "sec-ch-ua": self.headers.get("sec-ch-ua", ""),
                        }
                    )
                if parts.path.startswith("/dd/"):
                    scenario = parts.path.split("/")[2]
                    cookie = self.headers.get("cookie", "")
                    if f"datadome=cleared-{scenario}" in cookie:
                        return self._send(200, CONTENT, {"x-datadome": "protected"})
                    rt, t, frame_path, action = SCENARIOS[scenario]
                    body = BLOCK_PAGE % {
                        "rt": rt,
                        "t": t,
                        "frame_origin": json.dumps(f"http://localhost:{port}"),
                        "frame_path": json.dumps(frame_path),
                    }
                    headers = {"x-dd-b": action, "x-datadome": "protected", "server": "DataDome"}
                    if "datadome=" not in cookie:
                        headers["set-cookie"] = "datadome=initial-cookie; Path=/; SameSite=Lax"
                    return self._send(403, body, headers)
                parent = json.dumps(f"http://127.0.0.1:{port}")
                if parts.path.startswith("/interstitial/"):
                    scenario = query.get("scenario", ["pass"])[0]
                    button = (
                        '<button class="captcha_display_button_submit" style="width:180px;height:44px;margin:30px">'
                        "Confirm</button>"
                        if scenario == "confirm"
                        else ""
                    )
                    title = "Access is temporarily restricted" if scenario == "restricted" else "Verifying your device"
                    return self._send(
                        200,
                        INTERSTITIAL
                        % {"title": title, "button": button, "scenario": json.dumps(scenario), "parent_origin": parent},
                    )
                if parts.path.startswith("/captcha/"):
                    banned = "bv" in query.get("t", [])
                    simple = query.get("scenario", [""])[0] == "simple"
                    return self._send(
                        200,
                        SLIDER
                        % {
                            "parent_origin": parent,
                            "gap": state.gap,
                            "body_class": "dd-response-page--hard-block" if banned else "dd-response-page--captcha",
                            "title": "Access is temporarily restricted" if banned else "Verification required",
                            "frame_class": "simple" if simple else "",
                            "simple": "true" if simple else "false",
                        },
                    )
                return self._send(404, "<html><body>not found</body></html>")

        self.server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        self.port = self.server.server_address[1]
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()

    @property
    def frame_origin(self) -> str:
        return f"http://localhost:{self.port}"

    def url(self, path: str) -> str:
        return f"http://127.0.0.1:{self.port}{path}"

    def reset(self, gap: int | None = None) -> _State:
        with self.state.lock:
            self.state.reports.clear()
            self.state.requests.clear()
            self.state.gap = gap if gap is not None else random.Random().randrange(200, 400, 2)
        return self.state

    def close(self) -> None:
        self.server.shutdown()
        self.server.server_close()


@asynccontextmanager
async def headless_page(no_viewport: bool = True):
    """A fresh headless Chromium page (sandboxed) in a fresh context.

    ``SCRAPLING_TEST_CHROME`` may name a Chromium-compatible executable; otherwise the driver's own browser is used.
    """
    from patchright.async_api import async_playwright

    executable = os.environ.get("SCRAPLING_TEST_CHROME") or None
    async with async_playwright() as driver:
        browser = await driver.chromium.launch(
            headless=True, executable_path=executable, chromium_sandbox=True, args=["--window-position=0,0"]
        )
        try:
            options = (
                {"no_viewport": True}
                if no_viewport
                else {
                    "viewport": {"width": 1920, "height": 1080},
                    "screen": {"width": 1920, "height": 1080},
                    "device_scale_factor": 2,
                }
            )
            context = await browser.new_context(**options)
            page = await context.new_page()
            yield page
        finally:
            await browser.close()
