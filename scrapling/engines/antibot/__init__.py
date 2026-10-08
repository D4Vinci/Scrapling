"""Anti-bot vendor detection and in-browser solving for the stealth fetchers.

``detect(signal)`` names the vendor and kind of challenge on a page (Cloudflare, AWS WAF, DataDome, Kasada,
HUMAN/PerimeterX, Akamai, Imperva); ``get(vendor).solve(page, detection, ...)`` tries to get past it inside a
deadline. See :mod:`scrapling.engines.antibot.base` for the contract every handler follows.

The stealth fetchers run all of this for you with ``solve_antibot=True`` (:mod:`scrapling.engines.antibot.runner`),
and hand interactive captchas to paid captcha-solving services given as ``captcha_solver``
(:class:`scrapling.engines.antibot.solvers.SolverRouter`).
"""

from scrapling.engines.antibot.base import (
    KINDS,
    SOLVABLE_KINDS,
    Detection,
    Handler,
    Kind,
    Signal,
    SolveResult,
    page_signal,
)
from scrapling.engines.antibot.detect import detect, detect_all
from scrapling.engines.antibot.registry import HANDLERS, VENDORS, get, normalize_vendor

__all__ = [
    "KINDS",
    "SOLVABLE_KINDS",
    "Kind",
    "Signal",
    "Detection",
    "SolveResult",
    "Handler",
    "page_signal",
    "detect",
    "detect_all",
    "HANDLERS",
    "VENDORS",
    "get",
    "normalize_vendor",
]
