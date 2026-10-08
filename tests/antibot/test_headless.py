"""Headless identity hardening: pure helpers, and every frame agreeing in a real headless browser."""

import json
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import pytest

from scrapling.engines.antibot import headless
from scrapling.engines.antibot.headless import (
    DROP_ARGS,
    MAC_TOOLBAR_HEIGHT,
    Display,
    Identity,
    _parse_mac_screens,
    accept_language_for,
    brand_list,
    context_options,
    default_viewport,
    grease_brand,
    harden_page,
    launch_args,
    scrub_headless_ua,
    window_bounds,
)

from .dd_server import headless_page

HEADLESS_UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) "
    "HeadlessChrome/155.0.0.0 Safari/537.36"
)


class TestBrands:
    @pytest.mark.parametrize(
        "major, expected",
        [
            # Real Chrome headers: 120 and 131 from Chrome stable, 155 read from Chrome for Testing headless.
            (120, [("Not_A Brand", "8"), ("Chromium", "120"), ("Google Chrome", "120")]),
            (131, [("Google Chrome", "131"), ("Chromium", "131"), ("Not_A Brand", "24")]),
            (155, [("Google Chrome", "155"), ("Chromium", "155"), ("Not(A:Brand", "24")]),
        ],
    )
    def test_brand_list_matches_chrome(self, major, expected):
        assert [(b["brand"], b["version"]) for b in brand_list(f"{major}.0.1.2")] == expected

    def test_chromium_build_has_two_brands(self):
        # What Chrome for Testing 155 reports natively.
        assert brand_list("155.0.8059.39", None) == [
            {"brand": "Chromium", "version": "155"},
            {"brand": "Not(A:Brand", "version": "24"},
        ]

    def test_full_version_list(self):
        full = brand_list("155.0.8059.39", full=True)
        assert {"brand": "Google Chrome", "version": "155.0.8059.39"} in full
        assert {"brand": "Not(A:Brand", "version": "24.0.0.0"} in full

    def test_grease(self):
        assert grease_brand(155) == ("Not(A:Brand", "24")


class TestIdentity:
    def test_from_browser_version_on_apple_silicon(self, monkeypatch):
        monkeypatch.setattr(headless._platform, "mac_ver", lambda: ("26.6.2", ("", "", ""), "arm64"))
        identity = Identity.from_version(
            {"product": "Chrome/155.0.8059.39", "userAgent": HEADLESS_UA},
            locale="en-US",
            host="darwin",
            machine="arm64",
        )
        params = identity.override_params()
        assert "HeadlessChrome" not in params["userAgent"] and "Chrome/155.0.0.0" in params["userAgent"]
        assert params["platform"] == "MacIntel"
        assert params["acceptLanguage"] == "en-US,en"
        meta = params["userAgentMetadata"]
        assert (meta["architecture"], meta["bitness"], meta["platform"], meta["platformVersion"]) == (
            "arm",
            "64",
            "macOS",
            "26.6.2",
        )
        assert meta["fullVersion"] == "155.0.8059.39" and meta["mobile"] is False and meta["model"] == ""

    def test_intel_mac(self):
        identity = Identity.from_version(
            {"product": "Chrome/155.0.8059.39", "userAgent": HEADLESS_UA}, host="darwin", machine="x86_64"
        )
        assert identity.architecture == "x86" and identity.accept_language is None
        assert "acceptLanguage" not in identity.override_params()

    def test_helpers(self):
        assert scrub_headless_ua(HEADLESS_UA).count("HeadlessChrome") == 0
        assert accept_language_for("en-US") == "en-US,en"
        assert accept_language_for("en") == "en"
        assert accept_language_for(None) is None


class TestDisplays:
    def test_parse_mac_screens(self):
        # Main display 3200x1800 with a 30 px menu bar and an 84 px Dock, a second display to its left.
        raw = json.dumps(
            [
                [0, 0, 3200, 1800, 0, 84, 3200, 1686, 2, True, 2],
                [-2880, 0, 2880, 1620, -2880, 0, 2880, 1620, 2, True, 1],
            ]
        )
        main, second = _parse_mac_screens(raw)
        assert (main.width, main.height, main.inset_top, main.inset_bottom, main.color_depth, main.hdr) == (
            3200,
            1800,
            30,
            84,
            30,
            True,
        )
        assert (second.left, second.top, second.hdr) == (-2880, 180, False)

    def test_screen_params_are_device_pixels(self):
        d = Display(1728, 1117, scale=2, color_depth=30, inset_top=37)
        p = d.screen_params()
        assert (p["width"], p["height"], p["workAreaInsets"]["top"], p["devicePixelRatio"]) == (3456, 2234, 74, 2)
        assert d.screen_info_switch().startswith("--screen-info={0,0 3456x2234 colorDepth=30 workAreaTop=74")

    def test_viewport_and_window_fit_the_work_area(self):
        d = Display(1512, 982, scale=2, color_depth=30, inset_top=34)
        vw, vh = default_viewport(d, host="darwin")
        assert vw <= d.work_width and vh + MAC_TOOLBAR_HEIGHT <= d.work_height
        bounds = window_bounds(d, (vw, vh), host="darwin")
        assert bounds["height"] - vh == MAC_TOOLBAR_HEIGHT
        assert bounds["top"] >= d.inset_top and bounds["top"] + bounds["height"] <= d.height

    def test_launch_args_and_context_options(self):
        d = Display(1512, 982, scale=2, color_depth=30, inset_top=34)
        args = launch_args(
            list(DROP_ARGS) + ["--blink-settings=x=1", "--keep-me"], displays=[d], host="darwin", user_agent=HEADLESS_UA
        )
        assert "--keep-me" in args and not set(DROP_ARGS) & set(args)
        assert not any(a.startswith("--blink-settings=") for a in args)
        assert "--force-device-scale-factor=2" in args and "--force-color-profile=scrgb-linear" in args
        assert any(a.startswith("--user-agent=") and "HeadlessChrome" not in a for a in args)
        options = context_options(
            {"viewport": {"width": 1, "height": 1}, "screen": {}, "device_scale_factor": 2, "locale": "en-US"}
        )
        assert options == {"locale": "en-US", "no_viewport": True}


class TestDisplayPolicy:
    """By default the browser describes one common display, never the machine's own monitors."""

    @pytest.fixture(autouse=True)
    def restore(self):
        yield
        headless.set_display_policy("canonical")

    def test_canonical_by_default_and_the_host_is_never_read(self, monkeypatch):
        def boom(*_a, **_k):  # pragma: no cover - would mean the host's displays were read
            raise AssertionError("host displays read")

        monkeypatch.setattr(headless, "host_displays", boom)
        assert headless.display_policy() == "canonical"
        assert headless.session_displays("darwin") == (headless.DEFAULT_MAC_DISPLAY,)
        assert headless.session_displays("linux") == (headless.DEFAULT_DISPLAY,)
        args = launch_args(["--keep-me"], host="darwin")
        assert headless.DEFAULT_MAC_DISPLAY.screen_info_switch() in args

    def test_host_policy_describes_every_host_display(self, monkeypatch):
        main, second = Display(3200, 1800, scale=2, inset_top=30), Display(2880, 1620, scale=2, left=-2880)
        monkeypatch.setattr(headless, "host_displays", lambda refresh=False: (main, second))
        headless.set_display_policy("host")
        assert headless.session_displays("darwin") == (main, second)
        assert main.screen_info_switch() in launch_args([], host="darwin")

    def test_unknown_policy_is_refused(self):
        with pytest.raises(ValueError):
            headless.set_display_policy("all")


# -- A real headless browser: the top page and a cross-site (out-of-process) iframe must agree ----------------------

_PROBE = r"""<script>
(async function () {
  var he = await navigator.userAgentData.getHighEntropyValues(['architecture', 'platformVersion', 'fullVersionList']);
  var v = {where: location.host, ua: navigator.userAgent, brands: navigator.userAgentData.brands.map(function (b) { return b.brand; }),
           arch: he.architecture, full: he.fullVersionList.map(function (b) { return b.brand + '/' + b.version; }),
           screen: [screen.width, screen.height, screen.availWidth, screen.availHeight, screen.availTop, screen.colorDepth],
           dpr: devicePixelRatio, outer: [outerWidth, outerHeight], inner: [innerWidth, innerHeight], pos: [screenX, screenY],
           p3: matchMedia('(color-gamut: p3)').matches};
  await fetch('/report', {method: 'POST', body: JSON.stringify(v)});
})();
</script>"""


class _Probe:
    def __init__(self):
        reports, headers = self.reports, self.headers = [], []

        class Handler(BaseHTTPRequestHandler):
            def log_message(self, *args):
                pass

            def do_GET(self):
                headers.append({k.lower(): v for k, v in self.headers.items()})
                port = self.server.server_address[1]
                inner = (
                    f'<iframe src="http://localhost:{port}/frame" width="300" height="200"></iframe>'
                    if self.path == "/"
                    else ""
                )
                body = f"<html><body>{inner}{_PROBE}</body></html>".encode()
                self.send_response(200)
                self.send_header("content-type", "text/html")
                self.send_header("content-length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)

            def do_POST(self):
                reports.append(json.loads(self.rfile.read(int(self.headers.get("content-length", 0)))))
                self.send_response(204)
                self.end_headers()

        self.server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        threading.Thread(target=self.server.serve_forever, daemon=True).start()
        self.url = f"http://127.0.0.1:{self.server.server_address[1]}/"

    def close(self):
        self.server.shutdown()
        self.server.server_close()


@pytest.fixture
def probe():
    p = _Probe()
    yield p
    p.close()


async def _visit(page, probe):
    await page.goto(probe.url, wait_until="load")
    for _ in range(40):
        if len(probe.reports) >= 2:
            break
        await page.wait_for_timeout(100)
    by_where = {r["where"].split(":")[0]: r for r in probe.reports}
    return by_where["127.0.0.1"], by_where["localhost"]


class TestEveryFrameAgrees:
    @pytest.mark.asyncio
    async def test_unhardened_headless_leaks_in_the_iframe(self, probe):
        """The baseline the hardening fixes (documents the leak on the running Chrome)."""
        async with headless_page(no_viewport=False) as page:
            top, frame = await _visit(page, probe)
        assert top["screen"][:2] == [1920, 1080] and top["dpr"] == 2
        assert frame["screen"][:2] != top["screen"][:2] or frame["dpr"] != top["dpr"]

    @pytest.mark.asyncio
    @pytest.mark.parametrize("no_viewport", [True, False])
    async def test_hardened_frames_match(self, probe, no_viewport):
        async with headless_page(no_viewport=no_viewport) as page:
            hardening = await harden_page(page, locale="en-US")
            top, frame = await _visit(page, probe)
        assert not hardening.errors, hardening.summary()
        for key in ("screen", "dpr", "outer", "pos", "ua", "brands", "arch", "full", "p3"):
            assert top[key] == frame[key], (key, top[key], frame[key])
        assert "HeadlessChrome" not in top["ua"] and "Google Chrome" in top["brands"]
        assert top["outer"][1] > top["inner"][1] + 1  # a toolbar above the page
        if no_viewport:
            assert hardening.displays == headless.canonical_displays()  # one common display, not the host's
            assert top["screen"][4] == hardening.displays[0].inset_top  # its menu bar
            assert top["pos"][0] > 0  # not pinned to the screen origin
        if sys.platform == "darwin" and __import__("platform").machine() == "arm64":
            assert top["arch"] == "arm"
        # The frame's own request carried the same client hints as the page's.
        hints = {h.get("sec-ch-ua") for h in probe.headers}
        assert len(hints) == 1 and '"Google Chrome"' in hints.pop()
