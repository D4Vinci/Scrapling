"""DataDome detection (and the browser-side solver).

DataDome answers a low-trust request with a 401/403 page whose inline ``var dd={...}`` object names the verdict:

* ``'rt':'i'``: the invisible device check (``ct.captcha-delivery.com/i.js``), run in a
  ``geo.captcha-delivery.com/interstitial/`` iframe; a real browser clears it on its own.
* ``'rt':'c'``: the captcha (slider), in a ``geo.captcha-delivery.com/captcha/`` iframe.
* ``'t':'bv'``: the visitor (usually the IP) is banned; solving has no effect.

The ``x-dd-b`` header carries the same verdict in its low byte (1 captcha/block, 2 hard block, 3 device check; the
0x100 bit marks invisible mode). XHR endpoints answer with JSON ``{"url": "https://geo.captcha-delivery.com/..."}``.
A device check can escalate to the captcha while the page is open, so a live ``captcha-delivery.com`` frame is the
most current evidence and wins over the page's initial verdict.

Solving (:meth:`DataDomeHandler.solve`) never generates DataDome payloads; the browser earns the cookie itself:

* **Device check.** DataDome's proof of work runs in the interstitial iframe and, when it accepts the device, sets a
  new ``datadome`` cookie and reloads the page. The handler waits for exactly that: a changed cookie *and* the
  challenge frame gone *and* no verdict left on the page. A changed cookie while the frame stays is a rejection
  (DataDome's next attempt), not a clearance. Whether the check passes depends on the browser looking like one
  machine in every frame, which is what :func:`~scrapling.engines.antibot.headless.harden_page` does; the handler
  applies it to the page if the session has not.
* **Confirm button.** Some interstitials show a "confirm you are human" button; it is clicked once, with a human
  pointer path.
* **Ban.** ``t=bv`` (in the verdict, the page URL or a frame URL) stops at once with ``reason="ban"``: solving
  cannot change it and every retry adds to the IP's record.
* **Slider.** The "simple" slide-to-target variant (what DataDome served live on 2026-10-08:
  ``#captcha__frame.simple``, puzzle canvases never drawn) is dragged onto its visible ``.sliderTarget`` with no
  solver at all. The jigsaw variant (``SliderCaptcha``) needs the gap's position: with a configured solver its piece
  and background go to the solver's recognition task (``datadome_slider``, CapSolver ``VisionEngine``; only the two
  images leave the machine), and without one the handler stops with ``reason="slider"`` and
  ``solver_kind="datadome_slider"``. The drag goes through ``page.mouse`` and is corrected against the piece's (or
  handle's) real position while the button is held.
* **Restricted.** A "restricted" or "blocked" device frame that does not move on stops with ``reason="blocked"``.

A check detected from headers alone (``x-dd-b``, ``x-datadome``) or from DataDome's host in the page leaves no
verdict in the DOM to watch for, so it only counts as passed on a new ``datadome`` cookie or a new document; a page
that never changes ends as ``no_challenge``.

DOM reads inside the challenge frames go through
:func:`~scrapling.engines.antibot.headless.quiet_evaluate` (a CDP isolated world, no user gesture), so reading the
challenge never marks the frame as user-activated.

The wait logic is ported from Averyy/wafer ``wafer/browser/_datadome.py`` (Apache-2.0,
https://github.com/Averyy/wafer, see NOTICE): wait for the cookie to change and the iframe to leave, click a shown
confirm button once, stop on ``t=bv``, and never count a still-pending check as a success. Changes: async, bounded
by the caller's deadline, quiet frame reads, a frame-gone/marker check before success, and an optional
solver-backed slider instead of an unconditional bail-out. The slider geometry follows SeleniumBase's
``sb_cdp.py`` (MIT, ``div.slider``/``div.sliderTarget``) and ArgoZhang's SliderCaptcha, which DataDome's captcha
bundle embeds.
"""

from __future__ import annotations

import base64
import random
from asyncio import sleep as asyncio_sleep
from re import compile as re_compile
from time import monotonic
from urllib.parse import parse_qs, urlsplit

from scrapling.core._types import TYPE_CHECKING, Any, Dict, List, Optional, Tuple, cast
from scrapling.engines.antibot._pagestate import DocumentTracker, bounded, frame_urls, site_cookies
from scrapling.engines.antibot._pointer import human_path, move_along, sleep_until
from scrapling.engines.antibot.base import Detection, Kind, Signal, SolveResult, host_matches
from scrapling.engines.antibot.headless import get_hardening, harden_page, quiet_evaluate

if TYPE_CHECKING:  # pragma: no cover
    from scrapling.engines.antibot.solvers.router import SolverRouter

__all__ = [
    "DataDomeHandler",
    "DD_HOST",
    "DD_COOKIE",
    "parse_dd_object",
    "dd_header_action",
    "is_dd_frame",
    "dd_frame_kind",
    "dd_challenge_markers",
]

#: DataDome's clearance cookie.
DD_COOKIE = "datadome"

#: DataDome's challenge host (``geo.``/``ct.`` subdomains serve the frames and scripts).
DD_HOST = "captcha-delivery.com"

_DD_OBJECT = re_compile(r"(?s)\bvar\s+dd\s*=\s*\{([^{}]{0,4000})\}")
_DD_PAIR = re_compile(r"""['"]([A-Za-z_][\w-]{0,31})['"]\s*:\s*(?:'([^']{0,2048})'|"([^"]{0,2048})"|(-?\d{1,20}))""")
_DD_JSON_URL = re_compile(r'"url"\s*:\s*"(https://[a-z0-9.-]*captcha-delivery\.com/[^"\s]{0,2048})"')


def parse_dd_object(html: str) -> Optional[Dict[str, str]]:
    """Parse the ``var dd={...}`` verdict object of a DataDome block page into a ``{key: value}`` dict of strings.

    Returns ``None`` when the page has no such object.
    """
    if not html or "dd" not in html:
        return None
    match = _DD_OBJECT.search(html)
    if not match:
        return None
    out: Dict[str, str] = {}
    for key, single, double, number in _DD_PAIR.findall(match.group(1)):
        out[key] = single or double or number
    return out


def dd_header_action(value: str) -> Tuple[int, bool]:
    """Decode the ``x-dd-b`` header: ``(action, invisible)``.

    The low byte is the action (1 captcha/block, 2 hard block, 3 device check) and the 0x100 bit marks invisible
    mode, so ``259`` is ``(3, True)``. Anything that is not a short decimal number decodes as ``(0, False)``.
    """
    value = (value or "").strip()
    if not value.isdigit() or len(value) > 6:
        return 0, False
    number = int(value)
    return number & 0xFF, bool(number & 0x100)


def is_dd_frame(url: str) -> bool:
    """True if ``url`` is served by DataDome's challenge host (https, ``captcha-delivery.com`` or a subdomain)."""
    return (url or "").lower().startswith("https://") and host_matches(url, DD_HOST)


def dd_frame_kind(url: str) -> Optional[str]:
    """What a DataDome URL shows: ``ban`` (``t=bv``), ``captcha`` (``/captcha/``), ``device_check``
    (``/interstitial/``), or ``None`` for any other URL."""
    if not is_dd_frame(url):
        return None
    try:
        parts = urlsplit(url)
    except ValueError:
        return None
    if "bv" in parse_qs(parts.query).get("t", []):
        return "ban"
    path = parts.path.lower()
    if path.startswith("/captcha"):
        return "captcha"
    if path.startswith("/interstitial"):
        return "device_check"
    return None


_VERDICT_MARKERS = ("ct.captcha-delivery.com/i.js", "ct.captcha-delivery.com/c.js")


def dd_challenge_markers(html: str) -> bool:
    """True while ``html`` is still a DataDome verdict page (its ``var dd={'rt':...}`` object or challenge script).

    A cleared page may keep DataDome's ``tags.js`` sensor and mention ``captcha-delivery.com`` in its config, so
    neither counts.
    """
    if not html:
        return False
    low = html.lower()
    if any(m in low for m in _VERDICT_MARKERS):
        return True
    dd = parse_dd_object(html) if "dd" in low else None
    return bool(dd and (dd.get("rt") or dd.get("t")))


# Quiet reads (see headless.quiet_evaluate). Each is an expression, evaluated in an isolated world of its frame.

#: The page's own document, cut to 2 MiB.
_HTML_JS = "document.documentElement ? document.documentElement.outerHTML.slice(0, 2097152) : ''"

#: What a DataDome frame shows: the page kind (DataDome marks its response page's ``<body>`` with
#: ``dd-response-page--captcha`` or ``dd-response-page--hard-block`` in every language), the title text, the confirm
#: button, and the slider widget with its geometry. Measured on DataDome's live captcha (2026-10-08): the background
#: ``canvas`` and the ``canvas.block`` piece layer are both 280 px wide, drawn after the images load (height 0 until
#: then), with the piece somewhere inside its layer; ``.slider`` sits in ``.sliderContainer`` next to
#: ``.sliderTarget``. ``images`` adds the background and the piece cropped to its opaque pixels as PNG data URLs
#: (same-origin inside the frame, so readable), plus the piece's offset inside its layer.
_WIDGET_JS = r"""(function (images) {
  function box(el) {
    if (!el) return null;
    var b = el.getBoundingClientRect();
    if (!(b.width > 0 && b.height > 0)) return null;
    var s = getComputedStyle(el);
    if (s.visibility === 'hidden' || s.display === 'none' || parseFloat(s.opacity) === 0) return null;
    return {x: b.left, y: b.top, w: b.width, h: b.height};
  }
  function png(c) { try { return c ? c.toDataURL('image/png') : null; } catch (e) { return null; } }
  function opaque(c) {
    try {
      var d = c.getContext('2d').getImageData(0, 0, c.width, c.height).data, x0 = c.width, y0 = c.height, x1 = -1, y1 = -1;
      for (var y = 0; y < c.height; y++) for (var x = 0; x < c.width; x++) {
        if (d[(y * c.width + x) * 4 + 3] > 16) { if (x < x0) x0 = x; if (x > x1) x1 = x; if (y < y0) y0 = y; if (y > y1) y1 = y; }
      }
      if (x1 < 0) return null;
      var out = document.createElement('canvas'); out.width = x1 - x0 + 1; out.height = y1 - y0 + 1;
      out.getContext('2d').drawImage(c, x0, y0, out.width, out.height, 0, 0, out.width, out.height);
      return {x: x0, y: y0, w: out.width, h: out.height, png: png(out)};
    } catch (e) { return null; }
  }
  var body = document.body;
  var cls = body ? (body.className || '') : '';
  var title = document.querySelector('[data-dd-captcha-human-title]') || document.querySelector('.captcha__human__title');
  var piece = document.querySelector('canvas.block');
  var canvases = Array.prototype.slice.call(document.querySelectorAll('canvas'));
  var bg = canvases.filter(function (c) { return c !== piece && c.width >= 100; })[0] || null;
  var confirm = document.querySelector('button.captcha_display_button_submit');
  var cut = images && piece && piece.height > 0 ? opaque(piece) : null;
  return {
    hardBlock: cls.indexOf('dd-response-page--hard-block') >= 0,
    simple: !!document.querySelector('#captcha__frame.simple'),
    captchaPage: cls.indexOf('dd-response-page--captcha') >= 0,
    title: ((title && title.textContent) || '').trim().toLowerCase().slice(0, 300),
    text: (body ? (body.innerText || '') : '').trim().toLowerCase().slice(0, 600),
    confirm: box(confirm),
    handle: box(document.querySelector('.slider')),
    target: box(document.querySelector('.sliderTarget')),
    track: box(document.querySelector('.sliderContainer')),
    piece: box(piece),
    background: box(bg),
    backgroundWidth: bg ? bg.width : 0,
    backgroundHeight: bg ? bg.height : 0,
    pieceWidth: piece ? piece.width : 0,
    ready: !!(bg && bg.height > 0 && piece && piece.height > 0),
    audio: !!box(document.querySelector('#captcha__audio.toggled, .audio-captcha-play-button')),
    pieceCut: cut ? {x: cut.x, y: cut.y, w: cut.w, h: cut.h} : null,
    pieceImage: cut ? cut.png : null,
    backgroundImage: images ? png(bg) : null
  };
})(__IMAGES__)"""

#: Where the piece layer is now, relative to the background (CSS px), while the slider is held.
_PIECE_JS = r"""(function () {
  var piece = document.querySelector('canvas.block');
  var canvases = Array.prototype.slice.call(document.querySelectorAll('canvas'));
  var bg = canvases.filter(function (c) { return c !== piece && c.width >= 100; })[0] || null;
  if (!piece || !bg) return null;
  return piece.getBoundingClientRect().left - bg.getBoundingClientRect().left;
})()"""

#: Where the slider handle's centre is now, relative to its track (CSS px), while it is held.
_HANDLE_JS = r"""(function () {
  var handle = document.querySelector('.slider'), track = document.querySelector('.sliderContainer');
  if (!handle || !track) return null;
  var h = handle.getBoundingClientRect();
  return h.left + h.width / 2 - track.getBoundingClientRect().left;
})()"""

_BLOCKED_WORDS = ("restricted", "blocked", "unusual activity", "access denied")


def _data_url_bytes(value: Any) -> Optional[bytes]:
    """The bytes of a ``data:image/...;base64,`` URL, or ``None``."""
    if not isinstance(value, str) or ";base64," not in value:
        return None
    try:
        data = base64.b64decode(value.split(";base64,", 1)[1], validate=False)
    except (ValueError, TypeError):
        return None
    return data if len(data) > 64 else None


def _center(box: Dict[str, float], origin: Tuple[float, float]) -> Tuple[float, float]:
    return origin[0] + box["x"] + box["w"] / 2.0, origin[1] + box["y"] + box["h"] / 2.0


class _Run:
    """Per-solve state."""

    def __init__(self, started: float, initial_cookie: Optional[str], marked: bool = True):
        self.started = started
        self.initial = initial_cookie
        #: The detected page carried a verdict in its DOM (``var dd={...}`` or a challenge script) whose removal is
        #: evidence on its own; a detection from headers or the host string alone needs a cookie or a new document.
        self.marked = marked
        self.frame_seen: Optional[float] = None
        self.captcha_seen: Optional[float] = None
        self.confirmed = False
        self.slider_attempts = 0
        self.used_solver: Optional[str] = None
        self.pointer: Optional[Tuple[float, float]] = None


class DataDomeHandler:
    """Detects DataDome device checks, captchas and bans, and waits out or solves them in the browser.

    :param harden: Apply :func:`~scrapling.engines.antibot.headless.harden_page` at solve time when the session did
        not apply it before navigation. Off by default: changing the user agent, screen and window of a document
        whose device check already ran is itself a signal. Sessions should harden pages in ``page_setup``.
    :param click_confirm: Click the interstitial's "confirm" button when one is shown.
    :param max_slider_attempts: Slider attempts per visit.
    :param drag_simple_slider: Drag the slide-to-target slider onto its target (no solver needed). Off, that slider
        ends as ``slider`` with no ``solver_kind`` (no solver can help), so a caller can retry in a fresh context
        instead: on 2026-10-08 one live drag ended in DataDome's hard-block page.
    :param slider_kind: The solver recognition kind used for the slider.
    :param no_frame_grace: Seconds to wait for a challenge frame before deciding the check is not running.
    :param settle_timeout: Seconds to wait, after the cookie changed, for the frame and verdict to leave.
    :param poll: Seconds between checks.
    """

    vendor = "datadome"

    def __init__(
        self,
        *,
        harden: bool = False,
        click_confirm: bool = True,
        max_slider_attempts: int = 2,
        drag_simple_slider: bool = True,
        slider_kind: str = "datadome_slider",
        no_frame_grace: float = 8.0,
        settle_timeout: float = 10.0,
        poll: float = 0.5,
    ) -> None:
        self.harden = harden
        self.click_confirm = click_confirm
        self.max_slider_attempts = max(0, int(max_slider_attempts))
        self.drag_simple_slider = bool(drag_simple_slider)
        self.slider_kind = slider_kind
        self.no_frame_grace = no_frame_grace
        self.settle_timeout = settle_timeout
        self.poll = poll

    def detect(self, s: Signal) -> Optional[Detection]:
        """Recognise a DataDome verdict.

        Rules, first match wins:

        * ``dd.hard`` (``ban``): ``'t':'bv'`` in the verdict object or a frame URL, or ``x-dd-b`` action 2.
        * ``dd.frame_captcha`` / ``dd.frame_device`` (``captcha`` / ``device_check``): a live
          ``captcha-delivery.com`` frame on ``/captcha/`` or ``/interstitial/``, at any status (DataDome's tag also
          opens the captcha over a served page when one of its XHRs is blocked).
        * ``dd.json``: the XHR form, a JSON ``url`` on ``captcha-delivery.com`` (kind from the URL's path).
        * ``dd.device`` / ``dd.captcha``: the page's verdict object (``rt``), challenge script or ``x-dd-b`` action,
          on an error status or a gate-sized page.
        * ``dd.challenge``: an error status with DataDome's challenge host on the page but no readable verdict.
        * ``dd.block``: an error status from DataDome (``x-datadome``, ``x-dd-b`` or ``server: DataDome``) on a
          gate-sized page with no challenge at all.
        """
        html_has_host = s.has(DD_HOST)
        dd = parse_dd_object(s.html) if ("dd=" in s.lower or "dd =" in s.lower) else None
        action, invisible = dd_header_action(s.headers.get("x-dd-b", ""))
        dd_header = "x-datadome" in s.headers or "x-dd-b" in s.headers or "datadome" in s.header("server")
        frames = [(u, dd_frame_kind(u)) for u in s.frame_urls if is_dd_frame(u)]
        page_kind = dd_frame_kind(s.url)
        if not (dd or html_has_host or frames or page_kind or dd_header):
            return None

        details: Dict[str, Any] = {}
        if dd:
            details["dd"] = dd
        if "x-dd-b" in s.headers:
            details.update(x_dd_b=s.headers["x-dd-b"], action=action, invisible=invisible)
        if frames:
            details["frame_url"] = frames[0][0]

        def found(kind: Kind, rule: str, **extra: Any) -> Detection:
            return Detection(vendor=self.vendor, kind=kind, rule=rule, details={**details, **extra}, signal=s)

        # A ban first: nothing else matters once the visitor is banned.
        banned_frame = next((u for u, k in frames if k == "ban"), None)
        if (dd and dd.get("t") == "bv") or banned_frame or page_kind == "ban":
            return found("ban", "dd.hard", **({"frame_url": banned_frame} if banned_frame else {}))
        if action == 2 and (s.is_error or s.status is None):
            return found("ban", "dd.hard")

        # The live frame is the current state: a device check may already have turned into the captcha.
        captcha_frame = next((u for u, k in frames if k == "captcha"), None)
        if captcha_frame or page_kind == "captcha":
            return found("captcha", "dd.frame_captcha", frame_url=captcha_frame or s.url)
        device_frame = next((u for u, k in frames if k == "device_check"), None)
        if device_frame or page_kind == "device_check":
            return found("device_check", "dd.frame_device", frame_url=device_frame or s.url)

        # Without a frame, read the page itself, but only on a block status or a gate-sized page, so an article that
        # quotes the markup is not taken for the block page.
        if not (s.is_error or s.status is None or s.gate()):
            return None
        json_url = _DD_JSON_URL.search(s.html.replace("\\/", "/")) if html_has_host and not dd else None
        if json_url:
            kind = cast(Kind, dd_frame_kind(json_url.group(1)) or "challenge")
            return found(kind, "dd.json", challenge_url=json_url.group(1))
        rt = (dd or {}).get("rt", "")
        if rt == "i" or s.has("ct.captcha-delivery.com/i.js", "captcha-delivery.com/interstitial/"):
            return found("device_check", "dd.device")
        if rt == "c" or s.has("ct.captcha-delivery.com/c.js", "captcha-delivery.com/captcha/"):
            return found("captcha", "dd.captcha")
        if s.is_error and action == 3:
            return found("device_check", "dd.device")
        if s.is_error and action == 1 and html_has_host:
            return found("captcha", "dd.captcha")
        if s.is_error and (html_has_host or dd):
            return found("challenge", "dd.challenge")
        if s.is_error and dd_header and s.gate():
            return found("block", "dd.block")
        return None

    async def solve(
        self,
        page: Any,
        det: Detection,
        *,
        deadline: float,
        solver: Optional["SolverRouter"] = None,
        log: Any = None,
    ) -> SolveResult:
        """Wait out (or, with a solver, solve) the DataDome check on ``page`` before ``deadline``.

        Reasons: ``solved``; ``ban`` (``t=bv``, stop and do not retry this IP); ``blocked`` (a restricted device or a
        block verdict); ``slider`` (the captcha slider and no solver); ``slider_failed`` (the solver's answers were
        rejected); ``slider_unreadable``; ``solver_error:<code>``; ``captcha`` (another interactive widget, such as
        audio); ``no_challenge`` (no challenge frame appeared and the verdict stayed); ``timeout``.

        :param page: The Patchright/Playwright async page that holds the challenge.
        :param det: This handler's detection for the page.
        :param deadline: :func:`time.monotonic` value the call never runs past.
        :param solver: Optional captcha solver router, used only for the slider.
        :param log: A logger (Scrapling's by default).
        """
        if log is None:
            from scrapling.core.utils import log as default_log

            log = default_log
        if det.kind == "ban":
            return SolveResult(False, "ban")
        if det.kind == "block":
            return SolveResult(False, "blocked")
        if get_hardening(page) is None:
            if self.harden:
                await bounded(harden_page(page), deadline, None, cap=5.0)
            else:
                log.debug("DataDome: the page was not hardened before navigation; the device check sees headless")
        tracker = DocumentTracker(page)
        try:
            return await self._wait(page, det, deadline, solver, log, tracker)
        finally:
            tracker.detach()

    # -- the wait ---------------------------------------------------------------------------------------------------

    async def _wait(
        self, page: Any, det: Detection, deadline: float, solver: Optional["SolverRouter"], log: Any, tracker: Any
    ) -> SolveResult:
        cookies = await site_cookies(page, deadline, cap=2.0)
        if det.signal is not None:
            marked = dd_challenge_markers(det.signal.html)
        else:
            marked = dd_challenge_markers(await self._html(page, deadline) or "")
        run = _Run(monotonic(), cookies.get(DD_COOKIE), marked)
        documents = tracker.count
        while monotonic() < deadline:
            if self._banned(page):
                log.warning("DataDome: blocked visitor (t=bv); not retrying")
                return SolveResult(False, "ban", used_solver=run.used_solver)

            cookies = await site_cookies(page, deadline, cap=2.0)
            value = cookies.get(DD_COOKIE)
            if value and value != run.initial:
                outcome = await self._settle(page, deadline)
                if outcome == "solved":
                    log.info("DataDome: check passed (new datadome cookie, challenge frame gone)")
                    await self._loaded(page, deadline)
                    return SolveResult(True, "solved", [DD_COOKIE], run.used_solver)
                if outcome == "ban":
                    return SolveResult(False, "ban", used_solver=run.used_solver)
                # The cookie changed but the challenge stayed: a rejection and DataDome's next attempt.
                log.debug("DataDome: cookie changed but the challenge stayed (rejected attempt)")
                run.initial, run.confirmed = value, False
                continue

            frame = self._challenge_frame(page)
            now = monotonic()
            if frame is not None:
                if run.frame_seen is None:
                    run.frame_seen = now
                kind = dd_frame_kind(frame.url)
                result: Optional[SolveResult] = None
                if kind == "captcha":
                    result = await self._captcha(page, frame, run, deadline, solver, log)
                elif kind == "device_check":
                    result = await self._interstitial(page, frame, run, deadline, log)
                if result is not None:
                    return result
            elif tracker.count > documents or run.frame_seen is not None or now - run.started > self.no_frame_grace:
                html = await self._html(page, deadline)
                if html is not None:
                    dd = parse_dd_object(html) if "dd" in html else None
                    if (dd or {}).get("t") == "bv":
                        return SolveResult(False, "ban", used_solver=run.used_solver)
                    gone = not dd_challenge_markers(html) and self._challenge_frame(page) is None
                    # Without a verdict in the DOM to begin with, only a new document shows the page moved on.
                    if gone and (run.marked or tracker.count > documents):
                        log.info("DataDome: challenge gone from the page")
                        await self._loaded(page, deadline)
                        return SolveResult(True, "solved", [DD_COOKIE] if value else [], run.used_solver)
                if run.frame_seen is None and now - run.started > self.no_frame_grace:
                    return SolveResult(False, "no_challenge", used_solver=run.used_solver)
            await sleep_until(deadline, self.poll)
        return SolveResult(False, "timeout", used_solver=run.used_solver)

    @staticmethod
    def _challenge_frame(page: Any) -> Optional[Any]:
        """The first DataDome challenge frame on the page (https on ``captcha-delivery.com``), or ``None``."""
        try:
            main = page.main_frame
            for frame in page.frames:
                if frame is not main and dd_frame_kind(frame.url):
                    return frame
        except Exception:
            pass
        return None

    @staticmethod
    def _banned(page: Any) -> bool:
        try:
            url = page.url or ""
        except Exception:
            url = ""
        return dd_frame_kind(url) == "ban" or any(dd_frame_kind(u) == "ban" for u in frame_urls(page))

    @staticmethod
    async def _loaded(page: Any, deadline: float) -> None:
        """Let the document DataDome reloaded into finish loading (bounded), so the caller reads the content."""
        for state, cap in (("domcontentloaded", 8.0), ("load", 5.0)):
            left = min(cap, deadline - monotonic())
            if left <= 0.2:
                return
            await bounded(page.wait_for_load_state(state, timeout=int(left * 1000)), deadline, None, cap=cap)

    @staticmethod
    async def _html(page: Any, deadline: float) -> Optional[str]:
        left = deadline - monotonic()
        if left <= 0.05:
            return None
        return await quiet_evaluate(page, page.main_frame, _HTML_JS, timeout=min(3.0, left))

    @staticmethod
    async def _read(page: Any, frame: Any, expression: str, deadline: float, cap: float = 2.0) -> Any:
        left = deadline - monotonic()
        if left <= 0.05:
            return None
        return await quiet_evaluate(page, frame, expression, timeout=min(cap, left))

    async def _settle(self, page: Any, deadline: float) -> str:
        """After the cookie changed: ``solved`` once the frame and the verdict are gone, ``ban``, or ``pending``."""
        stop = min(deadline, monotonic() + self.settle_timeout)
        while monotonic() < stop:
            if self._banned(page):
                return "ban"
            if self._challenge_frame(page) is None:
                html = await self._html(page, stop)
                if html is not None and not dd_challenge_markers(html):
                    return "solved"
            await sleep_until(stop, self.poll)
        return "pending"

    async def _interstitial(self, page: Any, frame: Any, run: _Run, deadline: float, log: Any) -> Optional[SolveResult]:
        """The device check runs by itself; touch its DOM only after it had time to collect, then once a poll."""
        elapsed = monotonic() - (run.frame_seen or monotonic())
        if elapsed < 1.5:
            return None
        widget = await self._read(page, frame, _WIDGET_JS.replace("__IMAGES__", "false"), deadline)
        if not isinstance(widget, dict):
            return None
        if self.click_confirm and not run.confirmed and widget.get("confirm"):
            if await self._click(page, frame, widget["confirm"], run, deadline):
                log.info("DataDome: clicked the confirm button")
                run.confirmed = True
                await sleep_until(deadline, 2.0)
            return None
        if elapsed > 5.0 and self._blocked(widget):
            log.warning("DataDome: device check reports a restricted device")
            return SolveResult(False, "blocked", used_solver=run.used_solver)
        return None

    @staticmethod
    def _blocked(widget: Dict[str, Any]) -> bool:
        if widget.get("hardBlock"):
            return True
        text = f"{widget.get('title', '')} {widget.get('text', '')}"
        return any(word in text for word in _BLOCKED_WORDS)

    async def _captcha(
        self, page: Any, frame: Any, run: _Run, deadline: float, solver: Optional["SolverRouter"], log: Any
    ) -> Optional[SolveResult]:
        now = monotonic()
        if run.captcha_seen is None:
            run.captcha_seen = now
        waited = now - run.captcha_seen
        if waited < 1.0:  # let the widget render
            return None
        widget = await self._read(page, frame, _WIDGET_JS.replace("__IMAGES__", "false"), deadline)
        if isinstance(widget, dict) and widget.get("hardBlock"):
            # DataDome's hard-block response page (the ``t=bv`` verdict, whatever the URL says).
            log.warning("DataDome: hard-block page; not retrying")
            return SolveResult(False, "ban", used_solver=run.used_solver)
        if not isinstance(widget, dict) or not widget.get("handle"):
            if isinstance(widget, dict) and waited > 2.0 and self._blocked(widget):
                return SolveResult(False, "blocked", used_solver=run.used_solver)
            if waited > 6.0:
                return SolveResult(False, "captcha", used_solver=run.used_solver)
            return None
        if widget.get("simple") and not self.drag_simple_slider:
            log.info("DataDome: slide-to-target slider, dragging is off")
            return SolveResult(False, "slider")
        if solver is None and not widget.get("simple"):
            log.info("DataDome: jigsaw slider and no solver configured")
            return SolveResult(False, "slider", solver_kind=self.slider_kind)
        if run.slider_attempts >= self.max_slider_attempts:
            return SolveResult(
                False, "slider_failed", used_solver=run.used_solver, solver_kind=self._solver_kind(widget)
            )
        run.slider_attempts += 1
        result = await self._slide(page, frame, run, deadline, solver, log)
        if result is not None:
            return result
        # Wait for the verdict: a new cookie and a reload, or a fresh puzzle.
        await sleep_until(deadline, 2.5)
        run.captcha_seen = monotonic()
        return None

    # -- input --------------------------------------------------------------------------------------------------------

    @staticmethod
    async def _frame_origin(page: Any, frame: Any, deadline: float) -> Optional[Tuple[float, float]]:
        """Top-left corner of ``frame``'s viewport in page coordinates (CSS px)."""
        element = await bounded(frame.frame_element(), deadline, None, cap=2.0)
        if element is None:
            return None
        box = await bounded(element.bounding_box(), deadline, None, cap=2.0)
        if not box:
            return None
        return float(box["x"]), float(box["y"])

    @staticmethod
    def _viewport(page: Any) -> Tuple[float, float]:
        hardening = get_hardening(page)
        if hardening is not None and hardening.viewport:
            return float(hardening.viewport[0]), float(hardening.viewport[1])
        size = getattr(page, "viewport_size", None)
        if size:
            return float(size["width"]), float(size["height"])
        return 1280.0, 720.0

    async def _move_to(self, page: Any, point: Tuple[float, float], run: _Run, deadline: float, width: float) -> bool:
        rng = random.Random()
        if run.pointer is None:
            vw, vh = self._viewport(page)
            run.pointer = (rng.uniform(0.25, 0.75) * vw, rng.uniform(0.2, 0.6) * vh)
            await bounded(page.mouse.move(*run.pointer), deadline, None, cap=2.0)
        done = await move_along(page, human_path(run.pointer, point, rng=rng, target_width=width), deadline)
        run.pointer = point
        return done

    async def _click(self, page: Any, frame: Any, box: Dict[str, float], run: _Run, deadline: float) -> bool:
        """Click the centre of ``box`` (frame coordinates) with a human path, a hover pause and a real press."""
        origin = await self._frame_origin(page, frame, deadline)
        if origin is None:
            return False
        rng = random.Random()
        x, y = _center(box, origin)
        x += rng.uniform(-0.2, 0.2) * box["w"]
        y += rng.uniform(-0.2, 0.2) * box["h"]
        if not await self._move_to(page, (x, y), run, deadline, box["w"]):
            return False
        if not await sleep_until(deadline, rng.uniform(0.12, 0.35)):
            return False
        await bounded(page.mouse.down(), deadline, None, cap=2.0)
        await sleep_until(deadline, rng.uniform(0.06, 0.14))
        await bounded(page.mouse.up(), deadline, None, cap=2.0)
        return True

    def _solver_kind(self, widget: Any) -> Optional[str]:
        """The solver kind that would help with ``widget``: the jigsaw needs recognition, the simple slider none."""
        return None if isinstance(widget, dict) and widget.get("simple") else self.slider_kind

    async def _slide(
        self, page: Any, frame: Any, run: _Run, deadline: float, solver: Optional["SolverRouter"], log: Any
    ) -> Optional[SolveResult]:
        """One slider attempt, then ``None`` (the caller waits for DataDome's verdict) or a final result.

        DataDome serves two sliders. The jigsaw (``SliderCaptcha``) needs the gap's position, which comes from the
        solver's recognition task; the "simple" slide-to-target variant (``#captcha__frame.simple``, puzzle canvases
        never drawn) shows its target in the page, so it needs no solver at all. Either way the drag is closed-loop:
        while the button is held, the handler reads where the piece (or handle) really is and corrects.
        """
        widget: Any = None
        started = monotonic()
        ready_by = min(deadline, started + 5.0)
        images = "true" if solver is not None else "false"  # the puzzle images are only read for a solver
        while monotonic() < ready_by:
            widget = await self._read(page, frame, _WIDGET_JS.replace("__IMAGES__", images), deadline, cap=4.0)
            if isinstance(widget, dict):
                if widget.get("ready") and (widget.get("pieceImage") or solver is None):
                    break
                if widget.get("simple") and widget.get("target") and monotonic() - started > 1.5:
                    break
            await sleep_until(ready_by, 0.3)
        unreadable = SolveResult(
            False, "slider_unreadable", used_solver=run.used_solver, solver_kind=self._solver_kind(widget)
        )
        if not isinstance(widget, dict) or not widget.get("handle"):
            return unreadable
        origin = await self._frame_origin(page, frame, deadline)
        if origin is None:
            return unreadable
        if widget.get("simple") and widget.get("target") and widget.get("track"):
            plan = self._target_plan(widget)
        elif widget.get("ready") and solver is None:
            return SolveResult(False, "slider", solver_kind=self.slider_kind)
        elif widget.get("ready") and widget.get("pieceImage") and solver is not None:
            plan = await self._puzzle_plan(page, widget, run, deadline, solver, log)
        elif widget.get("target") and widget.get("track"):
            plan = self._target_plan(widget)
        else:
            return unreadable
        if isinstance(plan, SolveResult):
            return plan
        goal, start_value, ratio, read_js = plan
        if not await self._drag(
            page, frame, run, deadline, widget["handle"], origin, goal, start_value, ratio, read_js
        ):
            return SolveResult(False, "timeout", used_solver=run.used_solver)
        log.info(f"DataDome: slider dragged (attempt {run.slider_attempts}, solver {run.used_solver})")
        return None

    async def _puzzle_plan(
        self, page: Any, widget: Dict[str, Any], run: _Run, deadline: float, solver: "SolverRouter", log: Any
    ) -> Any:
        """Ask the solver where the gap is; returns ``(goal, start, ratio, read_js)`` for :meth:`_drag`."""
        from scrapling.engines.antibot.solvers.base import SolverError

        piece_png = _data_url_bytes(widget.get("pieceImage"))
        background_png = _data_url_bytes(widget.get("backgroundImage"))
        background, cut = widget.get("background"), widget.get("pieceCut")
        kind = self.slider_kind
        if not (piece_png and background_png and background and cut and widget.get("backgroundWidth")):
            return SolveResult(False, "slider_unreadable", used_solver=run.used_solver, solver_kind=kind)
        if deadline - monotonic() < 3.0:
            return SolveResult(False, "timeout", used_solver=run.used_solver, solver_kind=kind)
        try:
            # Only the two puzzle images leave the machine (no page URL).
            answer = await solver.recognize(kind, [piece_png, background_png], deadline=deadline)
        except SolverError as error:
            code = error.code or type(error).__name__
            log.warning(f"DataDome: slider recognition failed ({code})")
            if code in ("EXPERIMENTAL", "NO_PROVIDER", "KIND_UNSUPPORTED"):
                return SolveResult(False, "slider", used_solver=run.used_solver, solver_kind=kind)
            return SolveResult(False, f"solver_error:{code}", used_solver=run.used_solver, solver_kind=kind)
        except Exception as error:  # a misbehaving third-party solver
            log.warning(f"DataDome: slider recognition crashed ({type(error).__name__})")
            return SolveResult(False, "solver_error:crash", used_solver=run.used_solver, solver_kind=kind)
        run.used_solver = (answer or {}).get("provider") or getattr(solver, "name", None) or run.used_solver
        try:
            distance = float(answer["distance"])
        except (KeyError, TypeError, ValueError):
            return SolveResult(False, "solver_error:no_distance", used_solver=run.used_solver, solver_kind=kind)
        # The solver answers in background-image pixels; the canvases may be drawn at another CSS size. The piece
        # sits ``cut.x`` image pixels inside its layer, and the layer is what moves.
        scale = background["w"] / float(widget["backgroundWidth"])
        piece = widget.get("piece")
        piece_scale = (piece["w"] / float(widget["pieceWidth"])) if piece and widget.get("pieceWidth") else scale
        goal = distance * scale - cut["x"] * piece_scale  # where the layer's left edge must land, vs the background
        piece_start = (piece["x"] - background["x"]) if piece else 0.0
        # SliderCaptcha moves the piece (W - 60) / (W - 40) of the handle's travel; corrected from the DOM.
        width = background["w"]
        ratio = (width - 60.0) / (width - 40.0) if width > 100 else 1.0
        return goal, piece_start, ratio, _PIECE_JS

    @staticmethod
    def _target_plan(widget: Dict[str, Any]) -> Any:
        """Slide-to-target: move the handle's centre onto ``.sliderTarget``'s, a few pixels past like a hand."""
        track, handle, target = widget["track"], widget["handle"], widget["target"]
        start = handle["x"] + handle["w"] / 2.0 - track["x"]
        goal = target["x"] + target["w"] / 2.0 - track["x"] + random.uniform(2.0, 6.0)
        return goal, start, 1.0, _HANDLE_JS

    async def _drag(
        self,
        page: Any,
        frame: Any,
        run: _Run,
        deadline: float,
        handle: Dict[str, float],
        origin: Tuple[float, float],
        goal: float,
        start_value: float,
        ratio: float,
        read_js: str,
    ) -> bool:
        """Press the handle, move until ``read_js`` (a frame-relative x) reaches ``goal``, release.

        ``ratio`` is the first estimate of how far the measured x moves per pointer pixel; it is re-measured while
        the button is held and the pointer is corrected up to twice. Returns ``False`` when the deadline cut it.
        """
        rng = random.Random()
        start = _center(handle, origin)
        start = (start[0] + rng.uniform(-3, 3), start[1] + rng.uniform(-3, 3))
        if not await self._move_to(page, start, run, deadline, handle["w"]):
            return False
        await sleep_until(deadline, rng.uniform(0.15, 0.4))
        pressed = False
        try:
            await bounded(page.mouse.down(), deadline, None, cap=2.0)
            pressed = True
            await sleep_until(deadline, rng.uniform(0.08, 0.2))
            current = start
            target = (start[0] + (goal - start_value) / ratio, start[1] + rng.uniform(-3, 3))
            path = human_path(current, target, rng=rng, target_width=8, overshoot_chance=0.0)
            if not await move_along(page, path, deadline):
                return False
            current = target
            for _ in range(2):  # close the loop on where the piece (or handle) really is
                await sleep_until(deadline, rng.uniform(0.12, 0.25))
                where = await self._read(page, frame, read_js, deadline, cap=1.0)
                if not isinstance(where, (int, float)):
                    break
                moved = current[0] - start[0]
                if moved > 5 and where - start_value > 1:
                    ratio = (where - start_value) / moved
                error = goal - where
                if abs(error) < 1.0:
                    break
                step = (current[0] + error / max(ratio, 0.2), current[1] + rng.uniform(-1, 1))
                path = human_path(current, step, rng=rng, target_width=4, overshoot_chance=0.0)
                await move_along(page, path, deadline)
                current = step
            await sleep_until(deadline, rng.uniform(0.1, 0.3))
            run.pointer = current
            return True
        finally:
            if pressed:
                # Never leave the button held: release even at the deadline (one input event, a few ms).
                await bounded(page.mouse.up(), max(deadline, monotonic() + 0.5), None, cap=0.5)
