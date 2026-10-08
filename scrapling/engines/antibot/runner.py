"""The anti-bot pass of a browser fetch: prepare the page, detect after navigation, solve layer by layer.

The stealth sessions call these when ``solve_antibot`` is on:

1. :func:`prepare_page` before navigation: makes a headless page describe one coherent machine in every frame and
   worker (:func:`~scrapling.engines.antibot.headless.harden_page`) and starts keeping Kasada's tokens.
2. :func:`solve_page` after the page loaded: reads a :class:`~scrapling.engines.antibot.base.Signal` without
   touching the page's own JavaScript world, runs :func:`~scrapling.engines.antibot.detect.detect`, and hands a
   detection to its vendor's handler within the fetch's deadline. A solved page is read and detected again, because
   vendors are layered (Imperva in front of DataDome, for example); a vendor that is still detected after its own
   handler reported success is reported unsolved, never solved twice. Until a new main-frame document arrives the
   re-read keeps the detected document's status and headers, so a block page that never changed is never taken
   for a solved one.
3. :func:`release_page` before the page goes back to the pool.

The outcome is a JSON-safe dict for ``response.meta["antibot"]``: the deciding layer's ``vendor``, ``kind``,
``rule``, ``solved`` and ``reason`` at the top level, every layer under ``layers`` (each with the ``solver_kind`` a
captcha solver would need when the layer stopped at one), and the captcha solver's summary (attempts, estimated
cost, never keys or tokens) under ``solver`` when one was used. A page with nothing detected reports
``vendor: None`` and ``reason: "none"``.
"""

from __future__ import annotations

from asyncio import TimeoutError as AsyncTimeoutError, wait_for
from time import monotonic
from urllib.parse import urlsplit

from scrapling.core._types import Any, Callable, Dict, List, Optional
from scrapling.core.utils import log as default_log
from scrapling.engines.antibot import registry
from scrapling.engines.antibot._kasada_solver import unwatch_kasada, watch_kasada
from scrapling.engines.antibot._pagestate import bounded, looks_empty
from scrapling.engines.antibot.base import MAX_HTML_CHARS, Detection, Signal, SolveResult, remaining
from scrapling.engines.antibot.detect import detect
from scrapling.engines.antibot.headless import harden_page, quiet_evaluate

__all__ = [
    "MAX_LAYERS",
    "antibot_deadline",
    "error_outcome",
    "prepare_page",
    "read_signal",
    "release_page",
    "solve_page",
]

#: Vendors solved one after another on one fetch (a CDN vendor, a bot manager, and one spare).
MAX_LAYERS = 3
#: Seconds a handler may overrun its deadline before it is cut off. Handlers keep their own deadline; this only
#: guards against a bug, and leaves room for the half-second mouse-up the pointer code may take after it.
SOLVE_GRACE = 2.0
#: Below this many seconds before the deadline no new solve is started.
MIN_SOLVE_S = 1.0
#: Seconds :func:`prepare_page` may spend hardening a page.
HARDEN_TIMEOUT = 5.0

_HTML_JS = "document.documentElement ? document.documentElement.outerHTML.slice(0, %d) : ''" % MAX_HTML_CHARS


def antibot_deadline(started: float, timeout_ms: float) -> float:
    """The :func:`time.monotonic` deadline for the anti-bot pass of a fetch that started at ``started``.

    The pass shares the fetch's ``timeout`` and leaves a tenth of it (between 1 and 3 seconds) for the page action
    and for building the response.
    """
    budget = max(0.0, float(timeout_ms) / 1000.0)
    return started + budget - min(3.0, max(1.0, budget * 0.1))


async def prepare_page(page: Any, *, harden: bool = True, locale: Optional[str] = None) -> Dict[str, Any]:
    """Get ``page`` ready before it navigates: headless hardening and the Kasada token watcher.

    Never raises: a hardening step the browser refuses is recorded in the returned summary instead.

    :param page: A Patchright/Playwright async page (or the sync bridge's view of one).
    :param harden: Apply :func:`~scrapling.engines.antibot.headless.harden_page`.
    :param locale: The session locale, for the hardened ``Accept-Language`` client hints.
    :return: ``{"hardened": bool, "errors": int}``.
    """
    out: Dict[str, Any] = {"hardened": False, "errors": 0}
    if harden:
        try:
            hardening = await wait_for(harden_page(page, locale=locale), HARDEN_TIMEOUT)
            summary = hardening.summary()
            out["hardened"] = True
            out["errors"] = len(summary.get("errors") or ())
        except Exception as error:
            default_log.debug(f"Anti-bot: page hardening failed: {error!r}")
    try:
        watch_kasada(page)
    except Exception as error:  # pragma: no cover - a page that is already closed
        default_log.debug(f"Anti-bot: Kasada watcher failed: {error!r}")
    return out


def release_page(page: Any) -> None:
    """Undo what :func:`prepare_page` attached that must not outlive the fetch (pages are pooled)."""
    try:
        unwatch_kasada(page)
    except Exception:  # pragma: no cover
        pass


async def _document_facts(response: Any, deadline: float) -> tuple:
    if response is None:
        return None, {}
    try:
        status = int(response.status)
    except Exception:
        status = None
    headers = await bounded(response.all_headers(), deadline, None, cap=2.0)
    if headers is None:
        try:
            headers = dict(response.headers or {})
        except Exception:
            headers = {}
    return status, headers


async def read_signal(
    page: Any, *, status: Optional[int] = None, headers: Optional[Dict[str, str]] = None, deadline: float
) -> Signal:
    """Read a :class:`Signal` from the live page without the page noticing.

    The DOM is serialised in a fresh isolated world with no user gesture
    (:func:`~scrapling.engines.antibot.headless.quiet_evaluate`); Playwright's ``page.content()`` would mark the
    page as user-activated, which DataDome's device check reads. Cookies are the ones the browser would send to the
    page URL.
    """
    url = ""
    try:
        url = page.url or ""
    except Exception:  # pragma: no cover - a closed page
        pass
    html = None
    for _ in range(2):
        if remaining(deadline) <= 0.2:
            break
        html = await quiet_evaluate(page, page.main_frame, _HTML_JS, timeout=min(3.0, remaining(deadline)))
        if isinstance(html, str):
            break
        # Mid-navigation: the execution context went away under the read. Let the next document commit.
        await bounded(page.wait_for_load_state("domcontentloaded"), deadline, None, cap=2.0)
    cookies: Dict[str, str] = {}
    if url.startswith(("http://", "https://")):
        for cookie in await bounded(page.context.cookies([url]), deadline, [], cap=2.0) or []:
            if cookie.get("name"):
                cookies[cookie["name"]] = cookie.get("value", "")
    frames: List[str] = []
    try:
        main = page.main_frame
        frames = [frame.url for frame in page.frames if frame is not main and frame.url]
    except Exception:  # pragma: no cover
        pass
    return Signal(
        url=url,
        status=status,
        headers=dict(headers or {}),
        cookies=cookies,
        html=html if isinstance(html, str) else "",
        frame_urls=frames,
    )


def _fetch_scope(solver: Any) -> Any:
    """The solver scope for one fetch: ``solver`` itself when it already is a scope, else a new one."""
    if solver is None or getattr(solver, "is_scope", False) or not hasattr(solver, "scope"):
        return solver
    return solver.scope()


async def _read_document(page: Any, document: Callable[[], Any], deadline: float) -> Signal:
    """Read a signal whose status and headers belong to the document it shows.

    The status and headers come from the main frame's latest response (``document()``), so a page that did not
    reload keeps the status it was detected with. A document that arrives while the page is read (a challenge
    reloading under the read) is read again with its own response: a new page is never judged by the old one's
    status, nor an old page by the new one's.
    """
    response = document()
    status, headers = await _document_facts(response, deadline)
    signal = await read_signal(page, status=status, headers=headers, deadline=deadline)
    for _ in range(2):
        latest = document()
        if latest is response or remaining(deadline) <= 0.5:
            break
        response = latest
        status, headers = await _document_facts(response, deadline)
        signal = await read_signal(page, status=status, headers=headers, deadline=deadline)
    return signal


def error_outcome(error: BaseException) -> Dict[str, Any]:
    """The ``response.meta["antibot"]`` value when the anti-bot pass itself failed (the fetch still returns)."""
    return {
        "vendor": None,
        "kind": None,
        "rule": None,
        "solved": False,
        "reason": f"error:{type(error).__name__}",
        "layers": [],
        "elapsed_s": 0.0,
    }


def _layer(det: Detection, result: SolveResult, elapsed: float) -> Dict[str, Any]:
    return {
        "vendor": det.vendor,
        "kind": det.kind,
        "rule": det.rule,
        "solved": bool(result.solved),
        "reason": result.reason,
        "cookies": list(result.cookies or ()),
        "used_solver": result.used_solver,
        "solver_kind": None if result.solved else result.solver_kind,
        "elapsed_s": round(elapsed, 2),
    }


async def solve_page(
    page: Any,
    *,
    document: Callable[[], Any],
    deadline: float,
    solver: Any = None,
    log: Any = None,
    max_layers: int = MAX_LAYERS,
) -> Dict[str, Any]:
    """Detect a bot-protection vendor on the loaded ``page`` and get past it before ``deadline``.

    :param page: The Patchright/Playwright async page (or the sync bridge's view of one), after navigation.
    :param document: Returns the main frame's latest document response (async API shape), or ``None``.
    :param deadline: :func:`time.monotonic` value the pass never runs past (plus :data:`SOLVE_GRACE` at most).
    :param solver: A paid captcha-solving :class:`~scrapling.engines.antibot.solvers.SolverRouter`. A router gets one
        new scope per call, so its per-fetch caps apply to this page; a scope (``router.scope()``) is used as it
        is, so a caller that retries a fetch can keep one budget and one spend ledger across the attempts.
    :param log: Logger (Scrapling's by default).
    :param max_layers: Vendors solved one after another before giving up.
    :return: The outcome for ``response.meta["antibot"]`` (see the module docstring).
    """
    log = log or default_log
    started = monotonic()
    scope = _fetch_scope(solver)
    layers: List[Dict[str, Any]] = []

    signal = await _read_document(page, document, deadline)
    det = detect(signal)
    if det is None and looks_empty(signal.html) and remaining(deadline) > 3.0:
        # Read while a challenge was replacing the document: look once more after the next load.
        await bounded(page.wait_for_load_state("load"), deadline, None, cap=2.0)
        signal = await _read_document(page, document, deadline)
        det = detect(signal)

    solved_vendors: List[str] = []
    host = urlsplit(signal.url).hostname or ""
    while det is not None:
        if len(layers) >= max_layers:
            layers.append(_layer(det, SolveResult(False, "max_layers"), 0.0))
            break
        handler = registry.get(det.vendor)
        if det.vendor in solved_vendors:
            # The vendor's own handler said it was done, yet its challenge or block is still here.
            layers.append(_layer(det, SolveResult(False, "still_detected"), 0.0))
            break
        if det.kind == "ban" or handler is None:
            layers.append(_layer(det, SolveResult(False, "ban" if det.kind == "ban" else "no_handler"), 0.0))
            break
        if remaining(deadline) < MIN_SOLVE_S:
            layers.append(_layer(det, SolveResult(False, "timeout"), 0.0))
            break
        log.info(f"Anti-bot: {det.vendor} {det.kind} ({det.rule}) on {host}")
        began = monotonic()
        try:
            result = await wait_for(
                handler.solve(page, det, deadline=deadline, solver=scope, log=log),
                timeout=remaining(deadline) + SOLVE_GRACE,
            )
        except AsyncTimeoutError:
            result = SolveResult(False, "timeout")
        except Exception as error:
            log.debug(f"Anti-bot: {det.vendor} handler failed: {error!r}")
            result = SolveResult(False, f"error:{type(error).__name__}")
        layers.append(_layer(det, result, monotonic() - began))
        log.info(f"Anti-bot: {det.vendor} {'solved' if result.solved else 'not solved'} ({result.reason})")
        if not result.solved:
            break
        solved_vendors.append(det.vendor)
        # Without a new document the page is still the one that was detected, so its status and headers still
        # apply: a block page that never reloaded must read as the block it is, whatever the handler said.
        signal = await _read_document(page, document, deadline)
        det = detect(signal)

    last = layers[-1] if layers else None
    outcome: Dict[str, Any] = {
        "vendor": last["vendor"] if last else None,
        "kind": last["kind"] if last else None,
        "rule": last["rule"] if last else None,
        "solved": bool(layers) and all(layer["solved"] for layer in layers),
        "reason": last["reason"] if last else "none",
        "layers": layers,
        "elapsed_s": round(monotonic() - started, 2),
    }
    summary = getattr(scope, "summary", None)
    if callable(summary):
        try:
            used = summary()
            if isinstance(used, dict) and used.get("attempts"):
                outcome["solver"] = used
        except Exception:  # pragma: no cover - a custom solver object
            pass
    return outcome
