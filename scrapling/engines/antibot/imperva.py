"""Imperva (Incapsula) detection (and the browser-side solver).

A browser meets three kinds of Imperva pages:

* **reese84 interstitial** ("Pardon Our Interruption"): the ``_Incapsula_Resource`` loader plus script hooks that
  only this page carries. Its sensor posts to the site's reese84 path, stores ``reese84`` and reloads.
* **``___utmvc`` page**: a tiny page whose ``/_Incapsula_Resource?SWJIYLWA=`` script sets ``___utmvc`` and reloads.
* **Incident page**: ``<iframe id="main-iframe" src="/_Incapsula_Resource?SWUDNSAI=...">`` ("Request unsuccessful.
  Incapsula incident ID"). When Imperva escalates, the frame holds an hCaptcha or GeeTest widget.

The ``_Incapsula_Resource`` loader is on every page Imperva protects and ``x-iinfo``/``x-cdn: Imperva`` on every
response, so neither is a detection on its own; another vendor's challenge served through Imperva's edge (DataDome
behind Imperva on some retailers) belongs to that vendor. Rules and hooks are ported from Averyy/wafer
``wafer/_challenge.py`` (Apache-2.0, see NOTICE). The solver lives in :mod:`._imperva_solver`.
"""

from __future__ import annotations

from re import compile as re_compile

from scrapling.core._types import TYPE_CHECKING, Any, Dict, Optional
from scrapling.engines.antibot.base import Detection, Kind, Signal, SolveResult

if TYPE_CHECKING:  # pragma: no cover
    from scrapling.engines.antibot.solvers.router import SolverRouter

__all__ = ["ImpervaHandler", "INTERSTITIAL_HOOKS", "is_interstitial", "incident_widget"]

#: Script hooks only the reese84 interstitial carries (wafer ``IMPERVA_INTERSTITIAL_HOOKS``); they hold at any size.
INTERSTITIAL_HOOKS = (
    "reeseskipexpirationcheck",
    "__imperva_interstitial_started__",
    'id="interstitial-inprogress"',
    "x-spa-interstitial",
)

_RESOURCE = "_incapsula_resource"
# The incident frame's query starts with SWUDNSAI (CWUDNSAI on older pages).
_INCIDENT = ("_incapsula_resource?swudnsai=", "_incapsula_resource?cwudnsai=")
#: Cookie names (exact or prefixes) Imperva sets; with ``x-iinfo``/``x-cdn`` they tie a page to Imperva.
_COOKIE_PREFIXES = ("incap_ses_", "visid_incap_", "nlbi_", "reese84", "___utmvc")
_UTMVC_SCRIPT = "_incapsula_resource?swjiylwa="
_INCIDENT_FRAME = re_compile(r"""(?i)<iframe\b[^>]*\bsrc\s*=\s*["']?[^"'>]*_Incapsula_Resource\?[SC]WUDNSAI=""")
_EDET = re_compile(r"(?i)[?&](?:amp;)?edet=(\d+)")
#: wafer: the classic "Request unsuccessful" page and the ``___utmvc`` page are well under 5 KB.
_TINY = 5_000


def is_interstitial(html: str) -> bool:
    """True for the reese84 interstitial, which a browser can solve in place (wafer ``is_imperva_interstitial``)."""
    lower = (html or "").lower()
    return _RESOURCE in lower and any(hook in lower for hook in INTERSTITIAL_HOOKS)


def incident_widget(s: Signal) -> str:
    """The captcha an incident page shows: ``hcaptcha``, ``geetest`` or ``unknown`` (the frame may still load)."""
    if s.frames_on("hcaptcha.com") or s.has("hcaptcha"):
        return "hcaptcha"
    if s.frames_on("geetest.com") or s.has("geetest"):
        return "geetest"
    return "unknown"


class ImpervaHandler:
    """Detects Imperva interstitials, incident (captcha) pages and blocks."""

    vendor = "imperva"

    def detect(self, s: Signal) -> Optional[Detection]:
        """Recognise an Imperva challenge, captcha or block.

        Rules, first match wins:

        * ``imperva.incident`` (``captcha``): the ``SWUDNSAI`` (or older ``CWUDNSAI``) incident iframe in the page or
          among its frames.
          ``details['widget']`` is ``hcaptcha``, ``geetest`` or ``unknown``; ``details['edet']`` is Imperva's
          error detail code when present.
        * ``imperva.interstitial`` (``challenge``): the loader plus an interstitial-only hook, or "Pardon Our
          Interruption" on a gate-sized page with the loader or Imperva's headers/cookies.
        * ``imperva.utmvc`` (``challenge``): a tiny page that loads the ``SWJIYLWA`` (``___utmvc``) script.
        * ``imperva.block`` (``block``): any other tiny page with the loader, or a 403/429/503 gate-sized page that
          names Incapsula. Never when another vendor's challenge markers are on the page.
        """
        frames = [u.lower() for u in s.frame_urls]
        loader = s.has(_RESOURCE) or any(_RESOURCE in u for u in frames)
        edge = (
            "x-iinfo" in s.headers
            or any(v in s.header("x-cdn") for v in ("imperva", "incapsula"))
            or s.has_cookie_prefix(*_COOKIE_PREFIXES)
        )
        pardon = s.has("pardon our interruption")
        if not (loader or s.has("incapsula") or (pardon and edge)):
            return None

        def found(kind: Kind, rule: str, **details: Any) -> Detection:
            details["status"] = s.status
            return Detection(vendor=self.vendor, kind=kind, rule=rule, details=details, signal=s)

        incident_frames = [u for u in frames if any(i in u for i in _INCIDENT)]
        if incident_frames or _INCIDENT_FRAME.search(s.html):
            edet = _EDET.search(s.html) or next((m for m in map(_EDET.search, incident_frames) if m), None)
            return found("captcha", "imperva.incident", widget=incident_widget(s), edet=edet.group(1) if edet else None)
        if loader and s.has(*INTERSTITIAL_HOOKS):
            return found("challenge", "imperva.interstitial")
        if (loader or edge) and pardon and s.gate():
            return found("challenge", "imperva.interstitial", matched="title")
        if s.has(_UTMVC_SCRIPT) and len(s.html) < _TINY:
            return found("challenge", "imperva.utmvc")
        if s.marked_by_other(self.vendor):
            return None
        if loader and len(s.html) < _TINY and s.gate(256):
            return found("block", "imperva.block")
        if s.status_in(403, 429, 503) and s.has("incapsula incident id", "incapsula") and s.gate():
            return found("block", "imperva.block")
        return None

    async def solve(
        self,
        page: Any,
        det: Detection,
        *,
        deadline: float,
        solver: Optional["SolverRouter"],
        log: Any,
    ) -> SolveResult:
        """Let Imperva's script clear the page; on an hCaptcha incident page click once, then use ``solver``.

        See :func:`scrapling.engines.antibot._imperva_solver.solve_imperva`.
        """
        from scrapling.engines.antibot._imperva_solver import solve_imperva

        return await solve_imperva(self, page, det, deadline=deadline, solver=solver, log=log)
