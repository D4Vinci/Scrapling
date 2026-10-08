"""Deadline-bounded reads of a live page for the anti-bot handlers.

The handlers poll a page while a vendor's own script works (Imperva's reese84
sensor, AWS WAF's ``challenge.js``, Kasada's ``ips.js``). Every read here is
capped by the handler's ``deadline`` (``time.monotonic()`` seconds), swallows
the errors a navigating page throws ("execution context was destroyed",
"target closed") and returns a neutral value instead, so a poll loop never
hangs or raises halfway through a reload.

Nothing here touches the page's main JavaScript world: Patchright evaluates in
an isolated world by default, and these helpers only read the DOM, cookies and
frame URLs.
"""

from __future__ import annotations

import re
from asyncio import iscoroutine, wait_for
from time import monotonic

from scrapling.core._types import TYPE_CHECKING, Any, Awaitable, Dict, List, Optional, Tuple
from scrapling.engines.antibot._pointer import sleep_until
from scrapling.engines.antibot.base import page_signal, remaining

if TYPE_CHECKING:  # pragma: no cover
    from scrapling.engines.antibot.base import Detection, Signal

__all__ = [
    "bounded",
    "page_html",
    "site_cookies",
    "frame_urls",
    "reload_page",
    "looks_empty",
    "supports",
    "solver_name",
    "DocumentTracker",
    "Recheck",
]

_SPACE = re.compile(r"\s+")


def looks_empty(html: Optional[str]) -> bool:
    """True for a document that is not built yet (``<html><head></head><body></body></html>`` and the like)."""
    return html is None or len(_SPACE.sub("", html)) < 60


def supports(solver: Any, kind: str) -> bool:
    """``solver.supports(kind)``; False for a missing solver or one that raises."""
    if solver is None:
        return False
    try:
        return bool(solver.supports(kind))
    except Exception:
        return False


def solver_name(solver: Any) -> Optional[str]:
    """The solver's ``name`` (the router's, until a token names the provider that actually solved)."""
    if solver is None:
        return None
    return getattr(solver, "name", None) or type(solver).__name__


async def bounded(awaitable: Awaitable[Any], deadline: float, default: Any = None, cap: Optional[float] = None) -> Any:
    """Await ``awaitable`` but give up at ``deadline`` (or after ``cap`` seconds) and return ``default``.

    Any exception raised by the awaitable also yields ``default``; cancellation of the caller still propagates.

    :param awaitable: The coroutine or future to wait for.
    :param deadline: ``time.monotonic()`` value after which nothing is awaited.
    :param default: What to return on timeout or error.
    :param cap: Optional per-call limit in seconds, applied on top of the deadline.
    """
    left = deadline - monotonic()
    if cap is not None:
        left = min(left, cap)
    if left <= 0:
        if iscoroutine(awaitable):
            awaitable.close()
        return default
    try:
        return await wait_for(awaitable, left)
    except Exception:
        return default


async def page_html(page: Any, deadline: float, cap: float = 3.0) -> Optional[str]:
    """The page's current DOM serialized as HTML, or ``None`` when it cannot be read right now (mid-navigation)."""
    return await bounded(page.content(), deadline, None, cap)


async def site_cookies(page: Any, deadline: float, cap: float = 3.0) -> Dict[str, str]:
    """Cookies that apply to the page's current URL, as ``{name: value}``."""
    url = getattr(page, "url", "") or ""
    try:
        pending = page.context.cookies([url]) if url.startswith(("http://", "https://")) else page.context.cookies()
    except Exception:
        return {}
    cookies = await bounded(pending, deadline, [], cap) or []
    out: Dict[str, str] = {}
    for cookie in cookies:
        name = cookie.get("name")
        if name:
            out[name] = cookie.get("value", "")
    return out


def frame_urls(page: Any) -> List[str]:
    """URLs of every frame except the main one (nested frames included)."""
    try:
        main = page.main_frame
        return [frame.url for frame in page.frames if frame is not main and frame.url]
    except Exception:
        return []


async def reload_page(page: Any, deadline: float, cap: float = 15.0) -> bool:
    """Reload the current URL (never another one), waiting for ``domcontentloaded`` within the deadline.

    :return: True when the reload committed in time.
    """
    left = min(cap, deadline - monotonic())
    if left <= 0.2:
        return False
    marker = object()
    result = await bounded(page.reload(wait_until="domcontentloaded", timeout=int(left * 1000)), deadline, marker, cap)
    return result is not marker


class DocumentTracker:
    """Follows the main frame's document responses (status and headers) while a handler waits.

    Vendor scripts finish by reloading the page; the tracker tells the handler that a new document arrived and
    what it answered, without another request. Detach it when done: pages are pooled and reused.
    """

    def __init__(self, page: Any) -> None:
        self.page = page
        self.count = 0
        self.status: Optional[int] = None
        self.headers: Dict[str, str] = {}
        self.url: str = ""
        self._attached = False
        try:
            page.on("response", self._on_response)
            self._attached = True
        except Exception:
            pass

    def _on_response(self, response: Any) -> None:
        try:
            if response.request.resource_type != "document" or response.frame != self.page.main_frame:
                return
            self.count += 1
            self.status = response.status
            self.headers = {str(k).lower(): str(v) for k, v in (response.headers or {}).items()}
            self.url = response.url
        except Exception:
            return

    def detach(self) -> None:
        """Remove the response listener (idempotent)."""
        if self._attached:
            self._attached = False
            try:
                self.page.remove_listener("response", self._on_response)
            except Exception:
                pass


class Recheck:
    """Re-runs a handler's ``detect`` on the live page while its solver waits.

    Until a new main-frame document arrives the page is still the document that was detected, so the re-check uses
    the detection's own status and headers (:attr:`Detection.signal`): a block page that never changed keeps
    reading as a block, whatever its DOM says. Once a document arrives during the solve, its status and headers
    (through a :class:`DocumentTracker`) replace them. A page in the middle of its own reload can read as clean for
    an instant, so "cleared" takes two clean reads.

    :param status: The detected document's status, when the detection carries no signal.
    :param headers: The detected document's headers, when the detection carries no signal.
    """

    def __init__(
        self,
        handler: Any,
        page: Any,
        det: "Detection",
        *,
        status: Optional[int] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> None:
        self.handler = handler
        self.page = page
        self.det = det
        origin = getattr(det, "signal", None)
        self.origin_status: Optional[int] = origin.status if origin is not None else status
        self.origin_headers: Dict[str, str] = dict(origin.headers if origin is not None else headers or {})
        self.tracker = DocumentTracker(page)

    @property
    def reloaded(self) -> bool:
        """True once a new main-frame document arrived during the solve."""
        return self.tracker.count > 0

    def detach(self) -> None:
        self.tracker.detach()

    async def read(self, stop: float) -> Optional[Tuple["Signal", Optional["Detection"]]]:
        """``(signal, detection)`` for the page as it is now; ``None`` while it cannot be read or is still empty."""
        if self.tracker.count:
            status, headers = self.tracker.status, self.tracker.headers
        else:
            status, headers = self.origin_status, self.origin_headers
        signal = await bounded(page_signal(self.page, status=status, headers=headers), stop, None, 5.0)
        if signal is None or looks_empty(signal.html):
            return None
        return signal, self.handler.detect(signal)

    async def current(self, stop: float) -> Optional["Detection"]:
        """The detection on the page now, or ``None`` only after two clean reads 0.4 s apart.

        An unreadable or empty page counts as still challenged (the original detection is returned).
        """
        first = await self.read(stop)
        if first is None:
            return self.det
        if first[1] is not None:
            return first[1]
        await sleep_until(stop, 0.4)
        second = await self.read(stop)
        return self.det if second is None else second[1]

    async def wait_cleared(self, deadline: float, timeout: float) -> bool:
        """Poll until the page is clean, for at most ``timeout`` seconds and never past ``deadline``."""
        stop = min(deadline, monotonic() + timeout)
        while remaining(stop) > 0.1:
            if await self.current(stop) is None:
                return True
            await sleep_until(stop, 0.4)
        return False
