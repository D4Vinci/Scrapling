"""HUMAN (PerimeterX) detection and the press-and-hold solver.

HUMAN answers a low-score visit with a "Press & Hold" page (``#px-captcha``, title "Access to this page has been
denied", served with a 403, or a 200 "Robot or human?" page on some sites) or, at the edge, with
``x-px-blocked: 1``. A page that only loads HUMAN's sensor (``_pxAppId``, ``_px3`` cookies) is not a detection.
The press-and-hold solver lives in :mod:`._px_solver`.
"""

from __future__ import annotations

import random
from re import compile as re_compile

from scrapling.core._types import TYPE_CHECKING, Any, Dict, Optional
from scrapling.engines.antibot._px_solver import PX_COOKIES, solve_perimeterx
from scrapling.engines.antibot.base import Detection, Signal, SolveResult

if TYPE_CHECKING:  # pragma: no cover
    from scrapling.engines.antibot.solvers.router import SolverRouter

__all__ = ["PerimeterXHandler", "PX_COOKIES"]

# An element whose id is exactly px-captcha; class names such as "px-captcha-container" must not match.
_WIDGET_ID = re_compile(r"""(?i)\bid\s*=\s*["']?px-captcha["'\s>/]""")
_APP_ID = re_compile(r"""_pxAppId\s*[=:]\s*["'](PX[A-Za-z0-9]{4,16})["']""")
_PX_MARKERS = (
    "captcha.px-cdn.net",
    "captcha.px-cloud.net",
    "client.px-cloud.net",
    "client.perimeterx.net",
    "px-cdn.net",
    "px-cloud.net",
    "_pxappid",
    "_pxuuid",
    "_pxjsclientsrc",
)
_HOLD_PHRASES = ("press &amp; hold", "press & hold", "press and hold", "robot or human")
_BLOCK_TITLE = "access to this page has been denied"
_WIDGET_FRAME_HOSTS = ("captcha.px-cdn.net", "captcha.px-cloud.net")


class PerimeterXHandler:
    """Detects HUMAN (PerimeterX) blocks and solves its press-and-hold challenge in the page."""

    vendor = "perimeterx"

    def __init__(self, *, max_attempts: int = 3, rng: Optional[random.Random] = None) -> None:
        """
        :param max_attempts: Holds to try before giving up (HUMAN serves a new widget after a failed hold).
        :param rng: Random source for the pointer model (seed it in tests).
        """
        self.max_attempts = max(1, max_attempts)
        self._rng = rng

    def detect(self, s: Signal) -> Optional[Detection]:
        """Recognise a HUMAN block or press-and-hold page.

        Rules, first match wins:

        * ``px.hold`` (``captcha``): a ``#px-captcha`` element (or the widget frame) on a gate-sized page that is
          served with 403/429, carries ``x-px-blocked: 1``, says "Press & Hold"/"Robot or human?" or has HUMAN's
          block title.
        * ``px.header`` (``block``): ``x-px-blocked: 1`` and no widget.
        * ``px.block`` (``block``): a gate-sized 403/429 with HUMAN's markers and no widget.
        """
        blocked_header = s.header("x-px-blocked") == "1"
        widget = bool(_WIDGET_ID.search(s.html)) or bool(s.frames_on(*_WIDGET_FRAME_HOSTS))
        markers = [m for m in _PX_MARKERS if m in s.lower]
        if not (widget or blocked_header or markers):
            return None

        details: Dict[str, Any] = {"blocked_header": blocked_header}
        app_id = _APP_ID.search(s.html)
        if app_id:
            details["app_id"] = app_id.group(1)

        if widget and s.gate():
            if s.status_in(403, 429) or blocked_header or s.has(*_HOLD_PHRASES) or _BLOCK_TITLE in s.title:
                return Detection(
                    vendor=self.vendor,
                    kind="captcha",
                    rule="px.hold",
                    details={**details, "challenge": "press_and_hold"},
                    signal=s,
                )
        if blocked_header:
            return Detection(vendor=self.vendor, kind="block", rule="px.header", details=details, signal=s)
        if s.status_in(403, 429) and markers and s.gate() and not s.marked_by_other(self.vendor):
            return Detection(vendor=self.vendor, kind="block", rule="px.block", details=details, signal=s)
        return None

    async def solve(
        self,
        page: Any,
        det: Detection,
        *,
        deadline: float,
        solver: Optional["SolverRouter"] = None,
        log: Any,
    ) -> SolveResult:
        """Press and hold HUMAN's button until the challenge clears, within ``deadline``.

        ``solver`` is not used: no paid solver can hold a button in this browser from this IP.
        """
        return await solve_perimeterx(
            page, det, deadline=deadline, log=log, rng=self._rng, max_attempts=self.max_attempts
        )
