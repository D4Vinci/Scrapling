"""Kasada detection (and the browser-side solver).

Kasada's first answer to a new visitor is HTTP 429 with a near-empty page that bootstraps ``window.KPSDK`` and loads
``/<uuid>/<uuid>/ips.js`` (newer deployments: ``p.js``; the first UUID is ``149e9513-01fa-4fb0-aad4-566afd725d1b``
on every site). The script runs a proof of work, posts to ``/tl``, receives ``x-kpsdk-ct`` and reloads the page.
Served pages keep loading the SDK and keep the ``x-kpsdk-*`` response headers, so only a 403/429 (or an unknown
status on a near-empty bootstrap page) is a detection.

The status gating and the ``x-kpsdk-*``/``ips.js``/``p.js`` markers follow Averyy/wafer ``wafer/_challenge.py``
(Apache-2.0, see NOTICE).
"""

from __future__ import annotations

from re import compile as re_compile

from scrapling.core._types import TYPE_CHECKING, Any, Dict, Optional
from scrapling.engines.antibot.base import Detection, Signal, SolveResult

if TYPE_CHECKING:  # pragma: no cover
    from scrapling.engines.antibot.solvers.router import SolverRouter

__all__ = ["KasadaHandler", "KASADA_PATH_ID", "kasada_script"]

#: The first path segment of every Kasada endpoint (``/149e9513-.../<site uuid>/ips.js``, ``/fp``, ``/tl``).
KASADA_PATH_ID = "149e9513-01fa-4fb0-aad4-566afd725d1b"

_UUID = r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}"
_SCRIPT = re_compile(rf"(?i)((?:https?://[a-z0-9.-]+)?/{_UUID}/{_UUID}/(?:ips|p)\.js(?:\?[^\"'\s<>]*)?)")
_BOOTSTRAP = ("window.kpsdk", "kpsdk.now", "kpsdk.start", "kpsdk.scriptstart")


def kasada_script(html: str) -> Optional[str]:
    """The ``/<uuid>/<uuid>/ips.js`` (or ``p.js``) script URL on the page, HTML entities decoded."""
    match = _SCRIPT.search(html or "")
    return match.group(1).replace("&amp;", "&") if match else None


class KasadaHandler:
    """Detects Kasada's proof-of-work challenge."""

    vendor = "kasada"

    def detect(self, s: Signal) -> Optional[Detection]:
        """Recognise a Kasada challenge.

        Rules, first match wins:

        * ``kasada.header`` (``challenge``): 403/429 with an ``x-kpsdk-*`` response header.
        * ``kasada.body`` (``challenge``): 403/429 with the KPSDK bootstrap or the ``ips.js``/``p.js`` script.
        * ``kasada.page`` (``challenge``): any other status (or an unknown one) on a near-empty page that bootstraps
          KPSDK and loads the script, which is what the browser shows while the proof of work runs.
        """
        kp_headers = sorted(k for k in s.headers if k.startswith("x-kpsdk-"))
        marked = s.has("kpsdk", KASADA_PATH_ID) or "/ips.js" in s.lower or "/p.js" in s.lower
        if not (kp_headers or marked):
            return None
        script = kasada_script(s.html)
        details: Dict[str, Any] = {}
        if script:
            details["script_url"] = script
            details["flow"] = "ips" if "/ips.js" in script.lower() else "p"
        if kp_headers:
            details["headers"] = kp_headers

        def found(rule: str) -> Detection:
            return Detection(vendor=self.vendor, kind="challenge", rule=rule, details=details, signal=s)

        if s.status_in(403, 429):
            if kp_headers:
                return found("kasada.header")
            if s.has(*_BOOTSTRAP) or script:
                return found("kasada.body")
            return None
        if s.has(*_BOOTSTRAP) and script and s.gate(256):
            return found("kasada.page")
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
        """Wait for Kasada's own script to clear the page, keeping ``x-kpsdk-ct``/``x-kpsdk-st`` (``solver`` is unused).
        See :func:`scrapling.engines.antibot._kasada_solver.solve_kasada`.
        """
        from scrapling.engines.antibot._kasada_solver import solve_kasada

        return await solve_kasada(self, page, det, deadline=deadline, solver=solver, log=log)
