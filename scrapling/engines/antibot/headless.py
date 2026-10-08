"""Make a headless Chrome describe one coherent machine in every frame and worker.

Bot-management vendors read the browser from inside their own cross-site iframes. DataDome's device check runs in
``geo.captcha-delivery.com/interstitial/``, which Chrome's site isolation puts in an out-of-process iframe (OOPIF),
and compares what that frame sees with what the page claims. Headless Chrome under Playwright leaks there, measured
on Chrome for Testing 155.0.8059.39 with Patchright 1.63 on an Apple Silicon Mac:

* **Screen.** Playwright's viewport and screen emulation (``Emulation.setDeviceMetricsOverride``) is applied to the
  main frame only, and Chrome refuses the command on an OOPIF ("Command can only be executed on top-level targets").
  The OOPIF sees headless Chrome's virtual 800x600 screen with ``colorDepth`` 24 and ``devicePixelRatio`` 1 under a
  top document that claims 1920x1080 at 2x.
* **Window.** ``outerHeight == innerHeight`` (no toolbar) and, with ``--window-position=0,0``, a window at the
  screen origin, so ``screenX`` equals ``clientX`` for every pointer event.
* **User agent.** ``HeadlessChrome/<v>`` in the UA, a Chrome for Testing brand list without "Google Chrome", and a
  context-level UA from Playwright that reports ``architecture: x86`` and ``platformVersion: 10.15.7`` on Apple
  Silicon in every frame it reaches.

What fixes them, all through CDP on the page's own session (no init scripts, nothing in the page's JavaScript):

* ``Emulation.updateScreen`` (headless only) replaces the virtual screen itself, so every frame and worker reads the
  same display natively: size, work area (menu bar and Dock), ``colorDepth`` and scale. Which display that is
  follows :func:`set_display_policy`: by default one common display for the platform (:func:`canonical_displays`),
  so pages never learn the machine's own monitors, their layout or its menu bar and Dock settings; with ``"host"``
  the machine's real displays, extra ones added with ``Emulation.addScreen`` so ``screen.isExtended`` matches a
  multi-monitor desk. The frames only need to agree with each other, which either policy gives.
* ``Browser.setWindowBounds`` (headless only) gives the window a toolbar's height above the page and a normal
  position inside the work area.
* ``Emulation.setUserAgentOverride`` with the browser's own version and full UA client-hint metadata is sent to the
  page and, through ``Target.setAutoAttach`` with ``waitForDebuggerOnStart``, to every OOPIF (recursively) and
  dedicated or service worker while it is still paused, so its first script already sees it.
* ``Emulation.setEmulatedMedia`` sets ``color-gamut: p3`` on a wide-gamut display.

Launch flags and context options that complete the picture are exposed for the session that owns the launch:
:func:`launch_args` (``--screen-info`` and friends, the flags to drop) and :func:`context_options`
(``no_viewport``). With viewport emulation still on, :func:`harden_page` mirrors the emulated screen into every
frame instead, which keeps the frames consistent with each other but cannot give the page a toolbar.

Parts are ported from Averyy/wafer (Apache-2.0, https://github.com/Averyy/wafer), ``wafer/browser/_solver.py``:
the macOS display query, the ``--screen-info`` switch, the 87 px toolbar measurement, the unflattened target
router and the list of child-target commands. Changes: async only, runtime ``Emulation.updateScreen`` and
``Browser.setWindowBounds`` instead of an init script, Chromium's GREASE brand algorithm for the brand list, and
isolated-world reads without a user gesture (:func:`quiet_evaluate`). See NOTICE.
"""

from __future__ import annotations

import asyncio
import itertools
import json
import platform as _platform
import re
import subprocess
import sys
from dataclasses import dataclass, field, replace
from weakref import WeakKeyDictionary

from scrapling.core._types import Any, Callable, Dict, Iterable, List, Optional, Sequence, Tuple
from scrapling.core.utils import log

__all__ = [
    "DEFAULT_BRAND",
    "MAC_TOOLBAR_HEIGHT",
    "DROP_ARGS",
    "Display",
    "Identity",
    "PageHardening",
    "brand_list",
    "context_options",
    "default_viewport",
    "grease_brand",
    "harden_page",
    "get_hardening",
    "host_displays",
    "canonical_displays",
    "display_policy",
    "set_display_policy",
    "session_displays",
    "launch_args",
    "quiet_evaluate",
    "scrub_headless_ua",
    "accept_language_for",
]

#: The brand real Chrome adds to the client-hint brand list. Chrome for Testing and Chromium send only "Chromium"
#: and the GREASE brand, which no stock Chrome on a desktop does. ``None`` keeps the binary's own list.
DEFAULT_BRAND: Optional[str] = "Google Chrome"

#: What Chrome on macOS draws above the page (tab strip and toolbar): headed ``outerHeight - innerHeight``,
#: measured by wafer on Chrome 154 and here on 155 (a window sized with ``Browser.setWindowBounds``).
MAC_TOOLBAR_HEIGHT = 87
_TOOLBAR_HEIGHT = {"darwin": MAC_TOOLBAR_HEIGHT, "win32": 79, "linux": 79}

#: Where Chrome places a new, unmaximized window: this far right of and below the work area's corner.
_WINDOW_OFFSET = 22

#: Scrapling and Playwright launch switches that create headless tells DataDome reads (fk2 section 3): the window
#: pinned to the screen origin, a forced sRGB profile (colorDepth 24 on a P3 Mac), hidden scrollbars, no font
#: hinting, a touch-style pointer, synchronous scrolling and animation, and a no-op maximise.
DROP_ARGS: Tuple[str, ...] = (
    "--window-position=0,0",
    "--force-color-profile=srgb",
    "--hide-scrollbars",
    "--font-render-hinting=none",
    "--disable-threaded-animation",
    "--disable-threaded-scrolling",
    "--start-maximized",
)
_DROP_PREFIXES: Tuple[str, ...] = (
    "--blink-settings=",
    "--window-size=",
    "--screen-info=",
    "--force-device-scale-factor=",
)

#: Common desktop page sizes (CSS px). The default viewport is the largest that fits the display with a toolbar.
_VIEWPORTS: Tuple[Tuple[int, int], ...] = (
    (1920, 1080),
    (1680, 1050),
    (1600, 900),
    (1536, 864),
    (1440, 900),
    (1366, 768),
    (1280, 800),
    (1280, 720),
)

#: How many levels of OOPIFs are attached. Each level nests a routed message in one more JSON string.
MAX_CHILD_DEPTH = 4

_AUTO_ATTACH = ("Target.setAutoAttach", {"autoAttach": True, "waitForDebuggerOnStart": True, "flatten": False})

# NSScreen through JavaScript for Automation: every screen's frame (bottom-left origin), visible frame, backing
# scale, P3 coverage and potential EDR headroom, main screen first. From wafer's _SCREEN_QUERY, extended to all
# screens and HDR. It opens no window and needs no permission.
_SCREEN_QUERY = (
    'ObjC.import("AppKit");'
    "var all = $.NSScreen.screens, main = $.NSScreen.mainScreen, out = [];"
    "function d(s){var f = s.frame, v = s.visibleFrame; return [f.origin.x, f.origin.y, f.size.width,"
    " f.size.height, v.origin.x, v.origin.y, v.size.width, v.size.height, s.backingScaleFactor,"
    " s.canRepresentDisplayGamut($.NSDisplayGamutP3), s.maximumPotentialExtendedDynamicRangeColorComponentValue];}"
    "out.push(d(main));"
    "for (var i = 0; i < all.count; i++) { var s = all.objectAtIndex(i);"
    " if (!s.isEqual(main)) out.push(d(s)); }"
    "JSON.stringify(out)"
)


# --------------------------------------------------------------------------------------------------------------
# Displays
# --------------------------------------------------------------------------------------------------------------


@dataclass(frozen=True)
class Display:
    """One display in CSS pixels, as Chrome reports it to pages.

    :param width: Screen width (``screen.width``).
    :param height: Screen height (``screen.height``).
    :param scale: Device pixel ratio.
    :param color_depth: ``screen.colorDepth``: 30 on a P3 Mac display, 24 elsewhere.
    :param inset_top: Work-area inset at the top (the macOS menu bar).
    :param inset_bottom: Work-area inset at the bottom (Dock or taskbar).
    :param inset_left: Work-area inset at the left (a side Dock).
    :param inset_right: Work-area inset at the right.
    :param left: Left edge in the desktop's coordinates (top-left origin, primary display at 0, 0).
    :param top: Top edge in the desktop's coordinates.
    :param hdr: The display supports high dynamic range.
    """

    width: int
    height: int
    scale: float = 1.0
    color_depth: int = 24
    inset_top: int = 0
    inset_bottom: int = 0
    inset_left: int = 0
    inset_right: int = 0
    left: int = 0
    top: int = 0
    hdr: bool = False

    @property
    def work_width(self) -> int:
        return self.width - self.inset_left - self.inset_right

    @property
    def work_height(self) -> int:
        return self.height - self.inset_top - self.inset_bottom

    @property
    def wide_gamut(self) -> bool:
        return self.color_depth >= 30

    def _px(self, value: float) -> int:
        return int(round(value * self.scale))

    def screen_params(self) -> Dict[str, Any]:
        """Parameters for ``Emulation.updateScreen`` / ``Emulation.addScreen`` (device pixels)."""
        return {
            "left": self._px(self.left),
            "top": self._px(self.top),
            "width": self._px(self.width),
            "height": self._px(self.height),
            "workAreaInsets": {
                "top": self._px(self.inset_top),
                "bottom": self._px(self.inset_bottom),
                "left": self._px(self.inset_left),
                "right": self._px(self.inset_right),
            },
            "devicePixelRatio": self.scale,
            "colorDepth": self.color_depth,
        }

    def screen_info_switch(self) -> str:
        """The ``--screen-info`` launch switch describing this display (headless Chrome 142+, device pixels)."""
        p = self.screen_params()
        insets = p["workAreaInsets"]
        return (
            f"--screen-info={{{p['left']},{p['top']} {p['width']}x{p['height']} colorDepth={self.color_depth} "
            f"workAreaTop={insets['top']} workAreaBottom={insets['bottom']} "
            f"workAreaLeft={insets['left']} workAreaRight={insets['right']}}}"
        )


#: The common displays the browser describes by default (and the fallbacks when the host's cannot be read): a 14"
#: MacBook Pro at default scaling with the Dock hidden, and a 1080p desktop with a taskbar at the bottom.
DEFAULT_MAC_DISPLAY = Display(1512, 982, scale=2.0, color_depth=30, inset_top=34)
DEFAULT_DISPLAY = Display(1920, 1080, scale=1.0, color_depth=24, inset_bottom=48)

#: Display policies for :func:`set_display_policy`.
DISPLAY_POLICIES: Tuple[str, ...] = ("canonical", "host")

_HOST_DISPLAYS: List[Tuple[Display, ...]] = []
_DISPLAY_POLICY: List[str] = ["canonical"]


def _parse_mac_screens(output: str) -> Tuple[Display, ...]:
    """Turn the JXA query's JSON into displays (top-left desktop origin, main display first)."""
    rows = json.loads(output)
    displays: List[Display] = []
    main_height = None
    for row in rows:
        fx, fy, fw, fh, vx, vy, vw, vh, scale, p3, edr = row
        if main_height is None:
            main_height = fh
        fx, fy, fw, fh = round(fx), round(fy), round(fw), round(fh)
        vx, vy, vw, vh = round(vx), round(vy), round(vw), round(vh)
        display = Display(
            width=fw,
            height=fh,
            scale=float(max(1, round(scale))),
            color_depth=30 if p3 else 24,
            inset_top=(fy + fh) - (vy + vh),
            inset_bottom=vy - fy,
            inset_left=vx - fx,
            inset_right=(fx + fw) - (vx + vw),
            left=fx,
            # AppKit's origin is the main display's bottom-left corner, y up.
            top=round(main_height) - (fy + fh),
            hdr=bool(edr and float(edr) > 1.0),
        )
        if (
            display.width <= 0
            or display.height <= 0
            or min(display.inset_top, display.inset_bottom, display.inset_left, display.inset_right) < 0
        ):
            raise ValueError("implausible display geometry")
        displays.append(display)
    if not displays:
        raise ValueError("no displays")
    return tuple(displays)


def host_displays(refresh: bool = False) -> Tuple[Display, ...]:
    """The machine's displays, main display first, read once per process.

    On macOS this asks AppKit through ``osascript`` (no window, no permission prompt). Elsewhere, and when the
    query fails (no window server), a common default is returned.
    """
    if _HOST_DISPLAYS and not refresh:
        return _HOST_DISPLAYS[0]
    displays: Optional[Tuple[Display, ...]] = None
    if sys.platform == "darwin":
        try:
            result = subprocess.run(  # nosec B603 - a fixed system binary and a constant script, no shell
                ["/usr/bin/osascript", "-l", "JavaScript", "-e", _SCREEN_QUERY],
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode == 0:
                displays = _parse_mac_screens(result.stdout.strip())
        except (OSError, subprocess.SubprocessError, ValueError, TypeError):
            displays = None
        if displays is None:
            log.debug("Could not read the Mac's displays; using a default")
            displays = (DEFAULT_MAC_DISPLAY,)
    else:
        displays = (DEFAULT_DISPLAY,)
    _HOST_DISPLAYS[:] = [displays]
    return displays


def canonical_displays(host: Optional[str] = None) -> Tuple[Display, ...]:
    """One common display for ``host`` (``sys.platform`` by default): :data:`DEFAULT_MAC_DISPLAY` on macOS,
    :data:`DEFAULT_DISPLAY` elsewhere. Nothing about the machine's own monitors is read."""
    return (DEFAULT_MAC_DISPLAY,) if (host or sys.platform) == "darwin" else (DEFAULT_DISPLAY,)


def set_display_policy(policy: str) -> None:
    """Choose the displays a hardened browser describes when no ``displays`` are passed.

    * ``"canonical"`` (the default): one common display (:func:`canonical_displays`). Every frame still sees the same
      screen, which is all the cross-frame checks compare, and a page learns nothing about the machine's monitors.
    * ``"host"``: the machine's own displays (:func:`host_displays`), all of them, with their real geometry, menu bar
      and Dock insets. Only for a browser whose pages may see that.
    """
    if policy not in DISPLAY_POLICIES:
        raise ValueError(f"display policy must be one of {DISPLAY_POLICIES}")
    _DISPLAY_POLICY[0] = policy


def display_policy() -> str:
    """The current display policy (see :func:`set_display_policy`)."""
    return _DISPLAY_POLICY[0]


def session_displays(host: Optional[str] = None) -> Tuple[Display, ...]:
    """The displays to describe under the current policy."""
    return host_displays() if _DISPLAY_POLICY[0] == "host" else canonical_displays(host)


def toolbar_height(host: Optional[str] = None) -> int:
    """Height Chrome draws above the page on ``host`` (``sys.platform`` by default)."""
    host = host or sys.platform
    return _TOOLBAR_HEIGHT.get("linux" if host.startswith("linux") else host, MAC_TOOLBAR_HEIGHT)


def default_viewport(display: Display, host: Optional[str] = None) -> Tuple[int, int]:
    """The largest common page size whose window (page plus toolbar) fits ``display``'s work area."""
    chrome = toolbar_height(host)
    room_w = display.work_width - _WINDOW_OFFSET
    room_h = display.work_height - _WINDOW_OFFSET
    fitting = [(w, h) for w, h in _VIEWPORTS if w <= room_w and h + chrome <= room_h]
    if fitting:
        return max(fitting, key=lambda v: v[0] * v[1])
    return max(320, display.work_width), max(240, display.work_height - chrome)


def window_bounds(display: Display, viewport: Tuple[int, int], host: Optional[str] = None) -> Dict[str, int]:
    """Where a normal (unmaximised) window holding a ``viewport`` page sits on ``display``, in CSS pixels."""
    width, height = viewport[0], viewport[1] + toolbar_height(host)
    left = display.left + display.inset_left + min(_WINDOW_OFFSET, max(0, display.work_width - width))
    top = display.top + display.inset_top + min(_WINDOW_OFFSET, max(0, display.work_height - height))
    return {"left": int(left), "top": int(top), "width": int(width), "height": int(height)}


# --------------------------------------------------------------------------------------------------------------
# User agent and client hints
# --------------------------------------------------------------------------------------------------------------

_GREASE_CHARS = (" ", "(", ":", "-", ".", "/", ")", ";", "=", "?", "_")
_GREASE_VERSIONS = ("8", "99", "24")
_BRAND_ORDERS = ((0, 1, 2), (0, 2, 1), (1, 0, 2), (1, 2, 0), (2, 0, 1), (2, 1, 0))


def grease_brand(major: int) -> Tuple[str, str]:
    """Chromium's GREASE brand and version for ``major`` (``components/embedder_support/user_agent_utils.cc``).

    >>> grease_brand(155)
    ('Not(A:Brand', '24')
    >>> grease_brand(131)
    ('Not_A Brand', '24')
    """
    name = f"Not{_GREASE_CHARS[major % len(_GREASE_CHARS)]}A{_GREASE_CHARS[(major + 1) % len(_GREASE_CHARS)]}Brand"
    return name, _GREASE_VERSIONS[major % len(_GREASE_VERSIONS)]


def brand_list(version: str, brand: Optional[str] = DEFAULT_BRAND, *, full: bool = False) -> List[Dict[str, str]]:
    """The client-hint brand list Chrome ``version`` sends, in Chromium's seeded order.

    :param version: Full browser version, e.g. ``155.0.8059.39``.
    :param brand: The product brand (``"Google Chrome"``) or ``None`` for a Chromium build.
    :param full: Full versions (``Sec-CH-UA-Full-Version-List``) instead of majors (``Sec-CH-UA``).
    """
    major = int(version.split(".")[0])
    grease_name, grease_major = grease_brand(major)
    product = version if full else str(major)
    grease = {"brand": grease_name, "version": f"{grease_major}.0.0.0" if full else grease_major}
    chromium = {"brand": "Chromium", "version": product}
    if brand:
        order = _BRAND_ORDERS[major % 6]
        out: List[Dict[str, str]] = [{}, {}, {}]
        out[order[0]] = grease
        out[order[1]] = chromium
        out[order[2]] = {"brand": brand, "version": product}
        return out
    out = [{}, {}]
    first = major % 2
    out[first] = grease
    out[(first + 1) % 2] = chromium
    return out


def scrub_headless_ua(user_agent: str) -> str:
    """Replace the ``HeadlessChrome`` token headless Chrome puts in its own user agent."""
    return user_agent.replace("HeadlessChrome/", "Chrome/") if user_agent else user_agent


def accept_language_for(locale: Optional[str]) -> Optional[str]:
    """The ``Accept-Language`` value Scrapling launches with for ``locale`` (``en-US`` -> ``en-US,en``)."""
    if not locale:
        return None
    base = locale.split("-")[0].lower()
    return f"{locale},{base}" if base != locale.lower() else locale


def _platform_version(host: str) -> str:
    """What Chrome reports as ``platformVersion`` on this machine."""
    if host == "darwin":
        version = _platform.mac_ver()[0] or "15.0.0"
        parts = (version.split(".") + ["0", "0"])[:3]
        return ".".join(parts)
    if host == "win32":  # pragma: no cover - not measured off macOS
        # Chrome reports the Windows.Foundation.UniversalApiContract version; map it from the build number.
        try:
            build = int(_platform.version().split(".")[2])
        except (IndexError, ValueError):
            build = 0
        for minimum, contract in ((26100, "19.0.0"), (22621, "15.0.0"), (22000, "14.0.0"), (19041, "10.0.0")):
            if build >= minimum:
                return contract
        return "1.0.0"
    numbers = re.findall(r"\d+", _platform.release())  # pragma: no cover - not measured off macOS
    return ".".join((numbers + ["0", "0", "0"])[:3])  # pragma: no cover


@dataclass(frozen=True)
class Identity:
    """The user agent and client hints one browser reports everywhere.

    Build it with :meth:`from_version` from the browser's own ``Browser.getVersion`` so the version stays truthful.
    """

    user_agent: str
    full_version: str
    brand: Optional[str] = DEFAULT_BRAND
    platform: str = "macOS"
    platform_version: str = ""
    architecture: str = "arm"
    bitness: str = "64"
    navigator_platform: str = "MacIntel"
    accept_language: Optional[str] = None

    @classmethod
    def from_version(
        cls,
        version: Dict[str, Any],
        *,
        brand: Optional[str] = DEFAULT_BRAND,
        locale: Optional[str] = None,
        host: Optional[str] = None,
        machine: Optional[str] = None,
    ) -> "Identity":
        """Identity of the browser whose ``Browser.getVersion`` result is ``version``.

        :param version: The CDP ``Browser.getVersion`` result (``product``, ``userAgent``).
        :param brand: Product brand for the client hints, or ``None`` to send only Chromium's.
        :param locale: The session locale; sets ``Accept-Language`` and ``navigator.languages`` like the launch does.
        :param host: Platform to describe (``sys.platform`` by default).
        :param machine: CPU (``platform.machine()`` by default).
        """
        host = host or sys.platform
        machine = (machine or _platform.machine() or "").lower()
        product = str(version.get("product", ""))
        match = re.search(r"(\d+\.\d+\.\d+\.\d+)", product) or re.search(
            r"Chrome/(\d+\.\d+\.\d+\.\d+)", str(version.get("userAgent", ""))
        )
        full_version = match.group(1) if match else "0.0.0.0"
        user_agent = scrub_headless_ua(str(version.get("userAgent", "")))
        if host == "darwin":
            ua_platform, nav_platform = "macOS", "MacIntel"
        elif host == "win32":
            ua_platform, nav_platform = "Windows", "Win32"
        else:
            ua_platform, nav_platform = (
                "Linux",
                "Linux x86_64" if "x86" in machine or "amd64" in machine else "Linux aarch64",
            )
        arm = machine.startswith(("arm", "aarch"))
        return cls(
            user_agent=user_agent,
            full_version=full_version,
            brand=brand,
            platform=ua_platform,
            platform_version=_platform_version(host),
            architecture="arm" if arm else "x86",
            bitness="64",
            navigator_platform=nav_platform,
            accept_language=accept_language_for(locale),
        )

    @property
    def major(self) -> int:
        return int(self.full_version.split(".")[0])

    def metadata(self) -> Dict[str, Any]:
        """``userAgentMetadata`` for ``Emulation.setUserAgentOverride`` (every high-entropy hint)."""
        return {
            "brands": brand_list(self.full_version, self.brand),
            "fullVersionList": brand_list(self.full_version, self.brand, full=True),
            "fullVersion": self.full_version,
            "platform": self.platform,
            "platformVersion": self.platform_version,
            "architecture": self.architecture,
            "model": "",
            "mobile": False,
            "bitness": self.bitness,
            "wow64": False,
            "formFactors": ["Desktop"],
        }

    def override_params(self) -> Dict[str, Any]:
        """Parameters for ``Emulation.setUserAgentOverride`` / ``Network.setUserAgentOverride``."""
        params: Dict[str, Any] = {
            "userAgent": self.user_agent,
            "platform": self.navigator_platform,
            "userAgentMetadata": self.metadata(),
        }
        if self.accept_language:
            params["acceptLanguage"] = self.accept_language
        return params


# --------------------------------------------------------------------------------------------------------------
# Launch and context options for the session that owns the launch
# --------------------------------------------------------------------------------------------------------------


def launch_args(
    args: Iterable[str],
    *,
    displays: Optional[Sequence[Display]] = None,
    viewport: Optional[Tuple[int, int]] = None,
    user_agent: Optional[str] = None,
    host: Optional[str] = None,
) -> List[str]:
    """Rewrite headless launch ``args`` so the browser starts as one ordinary desktop browser.

    ``displays`` defaults to :func:`session_displays` (one common display unless the policy is ``"host"``).
    Drops :data:`DROP_ARGS`, then adds ``--screen-info`` for the main display, its scale factor, a window of
    ``viewport`` plus the toolbar, an HDR colour profile on a wide-gamut Mac (so ``(color: 10)`` and
    ``(dynamic-range: high)`` agree with ``colorDepth`` 30), and ``--user-agent`` when given (the only switch that
    reaches shared workers). :func:`harden_page` makes the same geometry true at runtime, so these are an
    optimisation for the first document, not a requirement.
    """
    host = host or sys.platform
    displays = tuple(displays or session_displays(host))
    main = displays[0]
    viewport = viewport or default_viewport(main, host)
    out = [a for a in args if a not in DROP_ARGS and not a.startswith(_DROP_PREFIXES)]
    out.append(main.screen_info_switch())
    out.append(f"--force-device-scale-factor={main.scale:g}")
    out.append(f"--window-size={viewport[0]},{viewport[1] + toolbar_height(host)}")
    if host == "darwin" and main.wide_gamut:
        out = [a for a in out if not a.startswith("--force-color-profile=")]
        out.append("--force-color-profile=scrgb-linear")
    if user_agent:
        out = [a for a in out if not a.startswith("--user-agent=")]
        out.append(f"--user-agent={scrub_headless_ua(user_agent)}")
    return out


def context_options(options: Dict[str, Any]) -> Dict[str, Any]:
    """A copy of Playwright context ``options`` without viewport, screen and scale emulation (``no_viewport``).

    Emulation reaches only the main frame; without it every frame reports the window and screen
    :func:`harden_page` sets up.
    """
    out = {k: v for k, v in options.items() if k not in ("viewport", "screen", "device_scale_factor", "is_mobile")}
    out["no_viewport"] = True
    return out


# --------------------------------------------------------------------------------------------------------------
# Per-page hardening
# --------------------------------------------------------------------------------------------------------------


class _ChildTargets:
    """Auto-attaches every child target of one CDP session, unflattened and paused, and hardens it.

    A child is addressed by the path of session ids from the root session; messages to it are nested in one
    ``Target.sendMessageToTarget`` per level (wafer's ``_TargetRouter``). Every child is resumed even when hardening
    it fails: a paused frame or worker would hang the page.
    """

    def __init__(self, cdp: Any, plan: Callable[[str, int], List[Tuple[str, Dict[str, Any]]]]):
        self.cdp = cdp
        self.plan = plan
        self.ids = itertools.count(1)
        self.attached: Dict[str, int] = {}
        self.errors: List[str] = []

    def wrap(self, path: Tuple[str, ...], method: str, params: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
        message: Dict[str, Any] = {"id": next(self.ids), "method": method, "params": params}
        for session_id in reversed(path[1:]):
            message = {
                "id": next(self.ids),
                "method": "Target.sendMessageToTarget",
                "params": {"sessionId": session_id, "message": json.dumps(message)},
            }
        return "Target.sendMessageToTarget", {"sessionId": path[0], "message": json.dumps(message)}

    async def send(self, path: Tuple[str, ...], method: str, params: Dict[str, Any]) -> None:
        await self.cdp.send(*self.wrap(path, method, params))

    async def on_attached(self, parent: Tuple[str, ...], event: Dict[str, Any]) -> None:
        path = parent + (event["sessionId"],)
        kind = event.get("targetInfo", {}).get("type", "")
        self.attached[kind] = self.attached.get(kind, 0) + 1
        try:
            for method, params in self.plan(kind, len(path)):
                # Commands to a paused target run in order, so the resume below lands after them.
                await self.send(path, method, params)
        except Exception as error:  # the target went away, or the browser refused a command
            self.errors.append(f"{kind}: {error}")
        finally:
            try:
                await self.send(path, "Runtime.runIfWaitingForDebugger", {})
            except Exception:
                pass

    async def on_root_attached(self, event: Dict[str, Any]) -> None:
        await self.on_attached((), event)

    async def on_message(self, event: Dict[str, Any]) -> None:
        try:
            path: Tuple[str, ...] = (event["sessionId"],)
            message = json.loads(event["message"])
            while message.get("method") == "Target.receivedMessageFromTarget":
                inner = message.get("params") or {}
                path += (inner["sessionId"],)
                message = json.loads(inner["message"])
            if message.get("method") == "Target.attachedToTarget":
                await self.on_attached(path, message.get("params") or {})
            elif "error" in message:
                self.errors.append(str(message["error"].get("message", message["error"])))
        except Exception:  # pragma: no cover - malformed or late message
            pass

    async def start(self) -> None:
        self.cdp.on("Target.attachedToTarget", self.on_root_attached)
        self.cdp.on("Target.receivedMessageFromTarget", self.on_message)
        await self.cdp.send(*_AUTO_ATTACH)


@dataclass
class PageHardening:
    """What :func:`harden_page` applied to one page. Keep it referenced: its CDP session carries the overrides."""

    cdp: Any
    identity: Identity
    displays: Tuple[Display, ...]
    viewport: Optional[Tuple[int, int]]
    headless: bool
    emulated_viewport: bool
    window: Optional[Dict[str, int]] = None
    errors: List[str] = field(default_factory=list)
    children: Optional[_ChildTargets] = None

    def summary(self) -> Dict[str, Any]:
        """A JSON-safe description for logs and ``response.meta``."""
        return {
            "headless": self.headless,
            "emulated_viewport": self.emulated_viewport,
            "screen": [self.displays[0].width, self.displays[0].height] if self.displays else None,
            "viewport": list(self.viewport) if self.viewport else None,
            "window": self.window,
            "user_agent_major": self.identity.major,
            "children": dict(self.children.attached) if self.children else {},
            "errors": list(self.errors) + (list(self.children.errors) if self.children else []),
        }


_HARDENED: "WeakKeyDictionary[Any, PageHardening]" = WeakKeyDictionary()
_LOCKS: "WeakKeyDictionary[Any, asyncio.Lock]" = WeakKeyDictionary()


def get_hardening(page: Any) -> Optional[PageHardening]:
    """The hardening applied to ``page``, if any."""
    try:
        return _HARDENED.get(page)
    except TypeError:  # pragma: no cover - unhashable test doubles
        return None


async def _send(cdp: Any, method: str, params: Optional[Dict[str, Any]], errors: List[str]) -> Any:
    try:
        return await cdp.send(method, params or {})
    except Exception as error:
        errors.append(f"{method}: {error}")
        return None


async def harden_page(
    page: Any,
    *,
    identity: Optional[Identity] = None,
    displays: Optional[Sequence[Display]] = None,
    viewport: Optional[Tuple[int, int]] = None,
    brand: Optional[str] = DEFAULT_BRAND,
    locale: Optional[str] = None,
    host: Optional[str] = None,
) -> PageHardening:
    """Make ``page`` and every frame and worker it creates report one machine. Idempotent per page.

    Call it before the page navigates (Scrapling's ``page_setup``). Called later it still covers everything created
    from then on, including the next document of an existing iframe.

    :param page: A Patchright/Playwright async ``Page``.
    :param identity: User agent and client hints; read from the browser itself by default.
    :param displays: Displays to describe; by default :func:`session_displays` (see :func:`set_display_policy`).
    :param viewport: Page size for the window when the context has no viewport emulation; by default the largest
        common size that fits the main display (:func:`default_viewport`).
    :param brand: Product brand for the client hints when ``identity`` is not given.
    :param locale: Session locale for ``Accept-Language`` when ``identity`` is not given.
    :param host: Platform to describe (``sys.platform`` by default).
    :return: The applied :class:`PageHardening`; its ``cdp`` session must stay attached.
    """
    lock = _LOCKS.setdefault(page, asyncio.Lock())
    async with lock:
        existing = _HARDENED.get(page)
        if existing is not None:
            return existing
        host = host or sys.platform
        cdp = await page.context.new_cdp_session(page)
        errors: List[str] = []
        version = await _send(cdp, "Browser.getVersion", None, errors) or {}
        identity = identity or Identity.from_version(version, brand=brand, locale=locale, host=host)
        headless = "HeadlessChrome" in str(version.get("userAgent", ""))
        displays = tuple(displays or session_displays(host))
        emulated = getattr(page, "viewport_size", None) is not None

        if emulated:
            # The main frame's screen is Playwright's emulation, which no other frame sees. Mirror it into the
            # virtual screen so every frame agrees (the emulated screen has no work area).
            size = page.viewport_size
            viewport = (int(size["width"]), int(size["height"]))
            shown = await quiet_evaluate(
                page, page.main_frame, "[screen.width, screen.height, devicePixelRatio]", timeout=2.0
            )
            main = displays[0]
            if isinstance(shown, list) and len(shown) == 3 and shown[0] and shown[1]:
                main = Display(int(shown[0]), int(shown[1]), scale=float(shown[2] or 1), color_depth=main.color_depth)
            displays = (main,)
            log.debug("Viewport emulation is on; frames get the emulated screen. Use no_viewport for full fidelity.")
        else:
            viewport = viewport or default_viewport(displays[0], host)

        ua_params = identity.override_params()
        media = (
            {"features": [{"name": "color-gamut", "value": "p3"}]}
            if headless and displays[0].wide_gamut and host == "darwin"
            else None
        )
        frame_commands: List[Tuple[str, Dict[str, Any]]] = [("Emulation.setUserAgentOverride", ua_params)]
        if media:
            frame_commands.append(("Emulation.setEmulatedMedia", media))

        def plan(kind: str, depth: int) -> List[Tuple[str, Dict[str, Any]]]:
            if kind == "iframe":
                return frame_commands + ([_AUTO_ATTACH] if depth < MAX_CHILD_DEPTH else [])
            if kind in ("worker", "service_worker"):
                return [("Emulation.setUserAgentOverride", ua_params), ("Network.setUserAgentOverride", ua_params)]
            return []

        for method, params in frame_commands:
            await _send(cdp, method, params, errors)

        window = None
        if headless:
            infos = await _send(cdp, "Emulation.getScreenInfos", None, errors) or {}
            screens = infos.get("screenInfos") or []
            primary = next((s for s in screens if s.get("isPrimary")), screens[0] if screens else None)
            if primary is not None:
                await _send(
                    cdp, "Emulation.updateScreen", {"screenId": primary["id"], **displays[0].screen_params()}, errors
                )
                if len(screens) == 1:
                    for extra in displays[1:]:
                        await _send(cdp, "Emulation.addScreen", extra.screen_params(), errors)
            target = await _send(cdp, "Browser.getWindowForTarget", None, errors) or {}
            if "windowId" in target and viewport:
                window = window_bounds(displays[0], viewport, host)
                await _send(cdp, "Browser.setWindowBounds", {"windowId": target["windowId"], "bounds": window}, errors)

        children: Optional[_ChildTargets] = None
        attacher = _ChildTargets(cdp, plan)
        try:
            await attacher.start()
            children = attacher
        except Exception as error:
            errors.append(f"Target.setAutoAttach: {error}")

        hardening = PageHardening(
            cdp=cdp,
            identity=identity,
            displays=displays,
            viewport=viewport,
            headless=headless,
            emulated_viewport=emulated,
            window=window,
            errors=errors,
            children=children,
        )
        if errors:
            log.debug(f"Headless hardening: {errors}")
        _HARDENED[page] = hardening
        return hardening


# --------------------------------------------------------------------------------------------------------------
# Reads that leave no trace
# --------------------------------------------------------------------------------------------------------------

_FRAME_SESSIONS: "WeakKeyDictionary[Any, Any]" = WeakKeyDictionary()


async def _session_for(page: Any, frame: Any) -> Tuple[Any, Optional[str]]:
    """A CDP session for ``frame`` and the CDP id of the frame inside it."""
    session = _FRAME_SESSIONS.get(frame)
    if session is None:
        if frame is page.main_frame:
            hardening = get_hardening(page)
            session = hardening.cdp if hardening else await page.context.new_cdp_session(page)
        else:
            # Works for an out-of-process iframe; Playwright refuses a frame that shares its parent's process.
            session = await page.context.new_cdp_session(frame)
        _FRAME_SESSIONS[frame] = session
    tree = await session.send("Page.getFrameTree")
    return session, tree["frameTree"]["frame"]["id"]


async def quiet_evaluate(page: Any, frame: Any, expression: str, *, timeout: float = 2.0) -> Any:
    """Evaluate ``expression`` in ``frame`` without the page noticing, returning a JSON value or ``None``.

    Playwright evaluations (``evaluate``, locators, ``content()``) are sent with ``userGesture: true``, which sets
    ``navigator.userActivation.hasBeenActive`` on the frame and its ancestors, and Patchright's isolated world is
    created by Playwright. This runs in a fresh isolated world created over CDP, with no user gesture, so the page's
    own scripts can neither see the code nor tell that anything was read.

    :param timeout: Seconds to wait for the browser; ``None`` is returned after it.
    """

    async def run() -> Any:
        session, frame_id = await _session_for(page, frame)
        world = await session.send(
            "Page.createIsolatedWorld", {"frameId": frame_id, "worldName": "", "grantUniveralAccess": False}
        )
        result = await session.send(
            "Runtime.evaluate",
            {
                "expression": expression,
                "contextId": world["executionContextId"],
                "returnByValue": True,
                "awaitPromise": True,
                "userGesture": False,
            },
        )
        if "exceptionDetails" in result:
            return None
        return result.get("result", {}).get("value")

    try:
        return await asyncio.wait_for(run(), timeout=max(0.05, timeout))
    except Exception:
        _FRAME_SESSIONS.pop(frame, None)
        return None


def replace_display(display: Display, **changes: Any) -> Display:
    """A copy of ``display`` with ``changes`` (for callers and tests)."""
    return replace(display, **changes)
