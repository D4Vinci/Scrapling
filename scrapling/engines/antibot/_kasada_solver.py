"""Kasada in the browser (the body of :meth:`KasadaHandler.solve`).

Kasada's challenge page bootstraps ``window.KPSDK`` and loads ``/<uuid>/<uuid>/ips.js`` (or ``p.js``). The script
fingerprints the browser, solves a proof of work, posts to ``/tl`` and gets ``x-kpsdk-ct`` (and ``x-kpsdk-st``, the
server time the per-request ``x-kpsdk-cd`` proof of work is built from) back, plus the cookie mirror of ``ct``
(``KP_UIDz``/``tkrm_alpekz_s1.3`` and their ``-ssn`` twins); then it reloads the page.

The solver never blocks, routes or rewrites Kasada's requests and injects nothing: it waits while the page's own SDK
works, gives it pointer input, reloads once if ``ct`` arrived but the page did not reload, and returns as soon as
the challenge page is gone. Along the way it keeps the latest ``x-kpsdk-ct`` / ``x-kpsdk-st`` response headers;
read them with :func:`kasada_tokens`. The ``/tl`` answer can arrive before ``solve`` is called, so a caller that
wants the tokens attaches :func:`watch_kasada` before navigating (``page_setup``); otherwise the cookie mirror of
``ct`` is used and ``st`` stays unknown.

Ported from Averyy/wafer ``wafer/browser/_kasada.py`` (``setup_kasada_listener``/``wait_for_kasada``,
Apache-2.0, see NOTICE). Token and cookie names follow Hyper Solutions' public Kasada documentation.
"""

from __future__ import annotations

import random
from time import monotonic
from weakref import WeakKeyDictionary

from scrapling.core._types import TYPE_CHECKING, Any, Dict, List, Optional
from scrapling.engines.antibot._pagestate import Recheck, reload_page, site_cookies
from scrapling.engines.antibot._pointer import sleep_until, wander
from scrapling.engines.antibot.base import Detection, SolveResult, remaining

if TYPE_CHECKING:  # pragma: no cover
    from scrapling.engines.antibot.kasada import KasadaHandler
    from scrapling.engines.antibot.solvers.router import SolverRouter

__all__ = ["solve_kasada", "watch_kasada", "unwatch_kasada", "kasada_tokens", "kasada_cookie_names", "KasadaWatcher"]

#: Cookie name prefixes Kasada uses for the ``ct`` mirror (``KP_UIDz``, ``KP_UIDz-ssn``, ``tkrm_alpekz_s1.3``...).
COOKIE_PREFIXES = ("KP_UID", "tkrm_alpekz", "KP_IM")
RELOAD_AFTER = 3.0  # seconds ``ct`` may wait for the SDK's own reload
SETTLE = 1.5  # after the page cleared, how long to wait for ``ct`` if it has not been seen yet

_WATCHERS: "WeakKeyDictionary[Any, KasadaWatcher]" = WeakKeyDictionary()
_TOKENS: "WeakKeyDictionary[Any, Dict[str, Any]]" = WeakKeyDictionary()


def kasada_cookie_names(cookies: Dict[str, str]) -> List[str]:
    """Kasada's cookie names present in ``cookies``, sorted."""
    return sorted(n for n in cookies if n.startswith(COOKIE_PREFIXES))


class KasadaWatcher:
    """Keeps the latest ``x-kpsdk-ct`` and ``x-kpsdk-st`` response headers a page receives (read-only listener)."""

    def __init__(self, page: Any) -> None:
        self.page = page
        self.ct: Optional[str] = None
        self.st: Optional[int] = None
        self.ct_at: Optional[float] = None
        self.ct_count = 0
        self._attached = False
        try:
            page.on("response", self._on_response)
            self._attached = True
        except Exception:
            pass

    def _on_response(self, response: Any) -> None:
        try:
            headers = response.headers or {}
            ct = headers.get("x-kpsdk-ct")
            st = headers.get("x-kpsdk-st")
        except Exception:
            return
        if ct:
            # "Only the most recent ct works": responses refresh it, so always keep the latest.
            self.ct, self.ct_at = ct, monotonic()
            self.ct_count += 1
        if st:
            try:
                self.st = int(st)
            except ValueError:
                pass

    def detach(self) -> None:
        if self._attached:
            self._attached = False
            try:
                self.page.remove_listener("response", self._on_response)
            except Exception:
                pass


def watch_kasada(page: Any) -> KasadaWatcher:
    """Start keeping Kasada's tokens for ``page`` (idempotent). Call it before navigating to catch the first ``/tl``."""
    watcher = _WATCHERS.get(page)
    if watcher is None:
        watcher = KasadaWatcher(page)
        _WATCHERS[page] = watcher
    return watcher


def unwatch_kasada(page: Any) -> None:
    """Stop the watcher :func:`watch_kasada` attached (pages are pooled, so detach before reuse)."""
    watcher = _WATCHERS.pop(page, None)
    if watcher is not None:
        watcher.detach()


def kasada_tokens(page: Any) -> Optional[Dict[str, Any]]:
    """The Kasada tokens the last solve on ``page`` saw: ``{"ct", "st", "ct_source", "cookies"}``, or ``None``.

    ``ct`` is the latest ``x-kpsdk-ct`` (from a response header, else from its cookie mirror), ``st`` the
    ``x-kpsdk-st`` server time (``None`` when the ``/tl`` answer was missed), ``cookies`` Kasada's cookie names.
    These are bearer values for the target site: keep them out of logs.
    """
    tokens = _TOKENS.get(page)
    return dict(tokens) if tokens else None


async def solve_kasada(
    handler: "KasadaHandler",
    page: Any,
    det: Detection,
    *,
    deadline: float,
    solver: Optional["SolverRouter"] = None,
    log: Any = None,
    rng: Optional[random.Random] = None,
) -> SolveResult:
    """Wait for Kasada's own script to clear ``page``, keeping its tokens, never past ``deadline``.

    ``solver`` is unused: Kasada has no widget to solve.
    """
    rng = rng or random.Random()
    owned = page not in _WATCHERS
    watcher = watch_kasada(page)
    check = Recheck(handler, page, det)
    try:
        initial = {n: v for n, v in (await site_cookies(page, deadline)).items() if n.startswith(COOKIE_PREFIXES)}
        initial_ct_count = watcher.ct_count
        progress_at: Optional[float] = None
        docs_at_progress = 0
        reloaded = False
        next_wander = monotonic() + rng.uniform(0.3, 1.0)
        while remaining(deadline) > 0.2:
            if await check.current(deadline) is None:
                if watcher.ct is None:
                    settle = min(deadline, monotonic() + SETTLE)
                    while watcher.ct is None and remaining(settle) > 0.05:
                        await sleep_until(settle, 0.2)
                return await _finish(page, det, watcher, deadline, True, "solved")

            cookies = {n: v for n, v in (await site_cookies(page, deadline)).items() if n.startswith(COOKIE_PREFIXES)}
            progressed = watcher.ct_count > initial_ct_count or any(initial.get(n) != v for n, v in cookies.items())
            if progress_at is None:
                if progressed:
                    progress_at, docs_at_progress = monotonic(), check.tracker.count
            elif not reloaded and check.tracker.count == docs_at_progress and monotonic() - progress_at >= RELOAD_AFTER:
                reloaded = True
                if log is not None:
                    log.debug("Kasada issued a token but the page did not reload; reloading it")
                await reload_page(page, deadline)
                continue
            if monotonic() >= next_wander:
                await wander(page, deadline, rng.uniform(0.4, 1.0), rng=rng, scroll=False)
                next_wander = monotonic() + rng.uniform(2.0, 4.0)
            else:
                await sleep_until(deadline, 0.4)
        return await _finish(page, det, watcher, deadline, False, "timeout")
    finally:
        check.detach()
        if owned:
            unwatch_kasada(page)


async def _finish(
    page: Any, det: Detection, watcher: KasadaWatcher, deadline: float, solved: bool, reason: str
) -> SolveResult:
    cookies = await site_cookies(page, deadline)
    names = kasada_cookie_names(cookies)
    ct, source = watcher.ct, "header" if watcher.ct else None
    if ct is None:
        mirror = next((n for n in ("KP_UIDz", "tkrm_alpekz_s1.3") if cookies.get(n)), None)
        mirror = mirror or next((n for n in names if not n.endswith("-ssn") and not n.startswith("KP_IM")), None)
        if mirror:
            ct, source = cookies[mirror], f"cookie:{mirror}"
    tokens = {"ct": ct, "st": watcher.st, "ct_source": source, "cookies": names}
    try:
        _TOKENS[page] = tokens
    except TypeError:  # pragma: no cover - a page type that cannot be weakly referenced
        pass
    # Only non-secret facts go into the detection (it may be logged): whether ct was seen, and st.
    det.details["tokens"] = {"ct": ct is not None, "ct_source": source, "st": watcher.st}
    return SolveResult(solved=solved, reason=reason, cookies=names)
