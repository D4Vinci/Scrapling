"""Clearing Imperva (Incapsula) pages in the browser (the body of :meth:`ImpervaHandler.solve`).

What the page can be stuck on, and what :func:`solve_imperva` does:

* **reese84 interstitial** (``imperva.interstitial``) and **``___utmvc`` page** (``imperva.utmvc``). Imperva's own
  script interrogates the browser (the reese84 sensor sometimes adds a proof of work), posts to the site's sensor
  path (``...?d=<host>``), stores ``reese84``/``___utmvc`` and reloads. The solver waits for that while giving the
  sensor pointer input, reloads once if a cookie changed but no new document arrived, and reads ``renewInSec``
  from the token response when it sees one (``det.details['renew_in_sec']``).
* **Block page** (``imperva.block``). It has no sensor to wait for: the solver gives Imperva's script a few seconds
  to set a cookie and reload (reloading once itself if a cookie changed), and only a new document that no longer
  reads as Imperva counts as cleared; otherwise the result is ``blocked``.
* **Incident page** (``imperva.incident``: the ``_Incapsula_Resource?SWUDNSAI=`` iframe). When it carries an
  hCaptcha, the solver clicks the checkbox once (free; trusted browsers pass). If the page stays, and a solver
  router that supports ``hcaptcha`` was passed, it gets a token, posts it to Imperva's own
  ``/_Incapsula_Resource?SWCGHOEL=...`` endpoint on the same origin (``g-recaptcha-response=<token>``, which sets
  ``incap_sh_*``) and reloads. A GeeTest widget gets one click on its "click to verify" button and otherwise
  ends as ``captcha_required:geetest``; an incident page without a widget ends as ``blocked:no_widget``.

The page is re-detected with :meth:`ImpervaHandler.detect` after every step; a step only counts when the page shows
content, not a transient empty document. Wait-for-cookie logic ported from Averyy/wafer
``wafer/browser/_imperva.py`` (Apache-2.0, see NOTICE); the incident flow follows Hyper Solutions' public Incapsula
documentation and the checkbox offset follows SeleniumBase ``__cdp_click_incapsula_hcaptcha`` (MIT).
"""

from __future__ import annotations

import random
import re
from asyncio import ensure_future, wait_for
from dataclasses import dataclass
from time import monotonic
from urllib.parse import parse_qs, urlsplit

from scrapling.core._types import TYPE_CHECKING, Any, Dict, List, Optional, Set, Tuple
from scrapling.engines.antibot._pagestate import Recheck, bounded, reload_page, site_cookies, solver_name, supports
from scrapling.engines.antibot._pointer import human_path, move_along, sleep_until, viewport_size, wander
from scrapling.engines.antibot.base import Detection, SolveResult, remaining
from scrapling.engines.antibot.solvers.base import provider_url

if TYPE_CHECKING:  # pragma: no cover
    from scrapling.engines.antibot.imperva import ImpervaHandler
    from scrapling.engines.antibot.solvers.router import SolverRouter

__all__ = ["solve_imperva", "imperva_cookie_names", "SOLVE_COOKIES", "COOKIE_PREFIXES"]

#: Cookies that carry an Imperva clearance (exported for replay by name, never by value).
SOLVE_COOKIES = ("reese84", "___utmvc")
COOKIE_PREFIXES = ("incap_ses_", "visid_incap_", "nlbi_", "incap_sh_")

_RESOURCE = "_incapsula_resource"
_INCIDENT = ("_incapsula_resource?swudnsai=", "_incapsula_resource?cwudnsai=")
_POST_PATH = re.compile(r"""["'](/_Incapsula_Resource\?SWCGHOEL=[^"']+)["']""", re.IGNORECASE)
#: GeeTest v3 ("radar") and v4 "click to verify" buttons.
GEETEST_BUTTONS = ".geetest_radar_tip, .geetest_radar_btn, .geetest_btn_click, .geetest_btn"
_SITEKEY_ATTR = re.compile(r"""data-sitekey\s*=\s*["']([0-9A-Za-z_-]{8,64})["']""")

RELOAD_AFTER = 3.0  # seconds a changed solve cookie may wait for the page's own reload
BLOCK_PATIENCE = 6.0  # a hookless block has no sensor to wait for
WIDGET_WAIT = 10.0  # time the incident frame gets to build its captcha widget
CLICK_RESULT_WAIT = 8.0
SOLVER_MARGIN = 3.0  # seconds kept back from a solver call for posting the token and reloading

_SUBMIT_JS = """async ([path, token]) => {
    const r = await fetch(path, {method: 'POST', credentials: 'include',
        headers: {'Content-Type': 'application/x-www-form-urlencoded'},
        body: 'g-recaptcha-response=' + encodeURIComponent(token)});
    return r.status;
}"""


def imperva_cookie_names(cookies: Dict[str, str]) -> List[str]:
    """The Imperva clearance cookie names present in ``cookies``, sorted."""
    return sorted(n for n in cookies if n in SOLVE_COOKIES or n.startswith(COOKIE_PREFIXES))


def _solve_values(cookies: Dict[str, str]) -> Dict[str, str]:
    return {n: v for n, v in cookies.items() if n in SOLVE_COOKIES or n.startswith("incap_ses_")}


class _RenewWatcher:
    """Reads ``renewInSec`` from reese84 token responses seen while the solver waits."""

    def __init__(self, page: Any) -> None:
        self.page = page
        self.renew_in_sec: Optional[int] = None
        self._tasks: Set[Any] = set()
        try:
            page.on("response", self._on_response)
        except Exception:
            pass

    def _on_response(self, response: Any) -> None:
        try:
            request = response.request
            if request.method != "POST" or "?d=" not in response.url or request.resource_type not in ("xhr", "fetch"):
                return
        except Exception:
            return
        task = ensure_future(self._read(response))
        self._tasks.add(task)
        task.add_done_callback(self._tasks.discard)

    async def _read(self, response: Any) -> None:
        try:
            data = await response.json()
            if isinstance(data, dict) and "renewInSec" in data:
                self.renew_in_sec = int(data["renewInSec"])
        except Exception:
            return

    def detach(self) -> None:
        try:
            self.page.remove_listener("response", self._on_response)
        except Exception:
            pass
        for task in list(self._tasks):
            task.cancel()


@dataclass
class _Widget:
    kind: Optional[str]  # "hcaptcha", "geetest" or None
    incident_frame: Any = None
    checkbox_frame: Any = None
    sitekey: Optional[str] = None
    post_path: Optional[str] = None


async def solve_imperva(
    handler: "ImpervaHandler",
    page: Any,
    det: Detection,
    *,
    deadline: float,
    solver: Optional["SolverRouter"] = None,
    log: Any = None,
    rng: Optional[random.Random] = None,
) -> SolveResult:
    """Get ``page`` past the Imperva page ``det`` describes, never past ``deadline``.

    Only reloads the current URL and posts the captcha token to Imperva's ``_Incapsula_Resource`` endpoint on the
    page's own origin.
    """
    run = _Run(handler, page, det, deadline, solver, log, rng or random.Random())
    try:
        if det.rule == "imperva.incident":
            return await run.incident()
        return await run.sensor(BLOCK_PATIENCE if det.kind == "block" else None)
    finally:
        run.close()


class _Run:
    def __init__(
        self, handler: Any, page: Any, det: Detection, deadline: float, solver: Any, log: Any, rng: random.Random
    ):
        self.handler = handler
        self.page = page
        self.det = det
        self.deadline = deadline
        self.solver = solver
        self.log = log
        self.rng = rng
        self.check = Recheck(handler, page, det)
        self.renew = _RenewWatcher(page)

    @property
    def tracker(self) -> Any:
        return self.check.tracker

    def close(self) -> None:
        self.check.detach()
        self.renew.detach()
        if self.renew.renew_in_sec is not None:
            self.det.details["renew_in_sec"] = self.renew.renew_in_sec

    def _debug(self, message: str) -> None:
        if self.log is not None:
            self.log.debug(message)

    async def clear_streak(self, stop: float) -> Optional[Detection]:
        return await self.check.current(stop)

    async def cleared(self, reason: str = "solved", used_solver: Optional[str] = None) -> SolveResult:
        names = imperva_cookie_names(await site_cookies(self.page, self.deadline))
        return SolveResult(solved=True, reason=reason, cookies=names, used_solver=used_solver)

    async def unsolved(self, reason: str, used_solver: Optional[str] = None) -> SolveResult:
        names = imperva_cookie_names(await site_cookies(self.page, self.deadline))
        # Only the hCaptcha incident has a solver route; GeeTest, a missing widget and blocks have none.
        solver_kind = "hcaptcha" if reason.startswith("captcha_required:hcaptcha") else None
        return SolveResult(solved=False, reason=reason, cookies=names, used_solver=used_solver, solver_kind=solver_kind)

    # ----------------------------------------------------------- the sensor

    async def sensor(self, patience: Optional[float]) -> SolveResult:
        """Poll until the interstitial (or ``___utmvc`` page) gives way to content (wafer ``wait_for_imperva``)."""
        stop = self.deadline if patience is None else min(self.deadline, monotonic() + patience)
        initial = _solve_values(await site_cookies(self.page, stop))
        changed_at: Optional[float] = None
        docs_at_change = 0
        reloaded = False
        next_wander = monotonic() + self.rng.uniform(0.3, 1.0)
        while remaining(stop) > 0.2:
            current_det = await self.clear_streak(stop)
            if current_det is None and self.det.kind == "block" and not self.check.reloaded:
                # A block page has no sensor that clears it in place: only a new document can be past it.
                current_det = self.det
            elif current_det is None:
                return await self.cleared()
            if current_det.rule == "imperva.incident":
                self._debug("Imperva escalated to its incident page")
                self.det.details["escalated"] = current_det.details.get("widget", "unknown")
                return await self.incident()
            if current_det.vendor != self.det.vendor:  # pragma: no cover - handler.detect only returns imperva
                return await self.cleared()

            current = _solve_values(await site_cookies(self.page, stop))
            if changed_at is None:
                if any(initial.get(name) != value for name, value in current.items()):
                    changed_at, docs_at_change = monotonic(), self.tracker.count
            elif not reloaded and self.tracker.count == docs_at_change and monotonic() - changed_at >= RELOAD_AFTER:
                reloaded = True
                self._debug("Imperva cookie changed but the page did not reload; reloading it")
                await reload_page(self.page, stop)
                continue
            if monotonic() >= next_wander:
                await wander(self.page, stop, self.rng.uniform(0.5, 1.2), rng=self.rng, scroll=False)
                next_wander = monotonic() + self.rng.uniform(2.0, 4.0)
            else:
                await sleep_until(stop, 0.5)
        if self.det.kind == "block":
            return await self.unsolved("blocked")
        return await self.unsolved("timeout")

    # ------------------------------------------------------------ incident

    async def find_widget(self, stop: float) -> _Widget:
        """Locate the incident frame and the captcha it renders (hCaptcha frames or GeeTest markup)."""
        page = self.page
        try:
            frames = list(page.frames)
            main = page.main_frame
        except Exception:
            return _Widget(kind=None)
        incident = next((f for f in frames if any(i in (f.url or "").lower() for i in _INCIDENT)), None)
        if incident is None:
            incident = next((f for f in frames if f is not main and _RESOURCE + "?" in (f.url or "").lower()), None)
        hcaptcha = [f for f in frames if "hcaptcha.com" in (urlsplit(f.url or "").hostname or "")]
        checkbox = next(
            (f for f in hcaptcha if "frame=checkbox" in (f.url or "").lower()), hcaptcha[0] if hcaptcha else None
        )

        sitekey = None
        if checkbox is not None:
            parts = urlsplit(checkbox.url)
            params = parse_qs(parts.fragment)
            params.update(parse_qs(parts.query))
            sitekey = (params.get("sitekey") or [None])[0]
        incident_html = (await bounded(incident.content(), stop, "", 3.0) or "") if incident is not None else ""
        incident_low = incident_html.lower()
        if not sitekey and incident_html:
            match = _SITEKEY_ATTR.search(incident_html)
            sitekey = match.group(1) if match else None
        post = _POST_PATH.search(incident_html)

        kind = None
        if checkbox is not None or "hcaptcha" in incident_low:
            kind = "hcaptcha"
        elif "geetest" in incident_low or any("geetest" in (f.url or "").lower() for f in frames):
            kind = "geetest"
        return _Widget(
            kind=kind,
            incident_frame=incident,
            checkbox_frame=checkbox,
            sitekey=sitekey,
            post_path=post.group(1).replace("&amp;", "&") if post else None,
        )

    async def wait_cleared(self, timeout: float) -> bool:
        return await self.check.wait_cleared(self.deadline, timeout)

    async def incident(self) -> SolveResult:
        """One free click on the widget (hCaptcha checkbox or GeeTest button); then, for hCaptcha only and when
        configured, a token from the solver router."""
        widget = _Widget(kind=None)
        button: Optional[Dict[str, float]] = None
        wait_until = min(self.deadline, monotonic() + WIDGET_WAIT)
        while remaining(wait_until) > 0.1:
            if await self.clear_streak(wait_until) is None:
                return await self.cleared()
            widget = await self.find_widget(wait_until)
            if widget.kind == "hcaptcha" and widget.checkbox_frame is not None:
                break
            if widget.kind == "geetest":
                button = await self.geetest_button(widget, wait_until)
                if button is not None:
                    break
            await sleep_until(wait_until, 0.5)

        self.det.details["widget"] = widget.kind or "none"
        if widget.kind is None:
            return await self.unsolved("blocked:no_widget")
        if widget.kind == "geetest":
            # GeeTest's "click to verify" passes a trusted browser on the click alone; anything harder (slide,
            # icon puzzle) is left to the caller: no token route, because Imperva's GeeTest submit format is unverified.
            if button is not None and await self.click_box(button, (button["width"] / 2, button["height"] / 2)):
                if await self.wait_cleared(CLICK_RESULT_WAIT):
                    return await self.cleared("solved:checkbox")
            return await self.unsolved("captcha_required:geetest")

        if widget.checkbox_frame is not None:
            element = await bounded(widget.checkbox_frame.frame_element(), self.deadline, None, 3.0)
            box = await bounded(element.bounding_box(), self.deadline, None, 3.0) if element is not None else None
            # SeleniumBase clicks 30/36 px into the checkbox frame (the box sits at its left edge).
            if box and await self.click_box(box, (min(30.0, box["width"] / 2), min(36.0, box["height"] / 2))):
                if await self.wait_cleared(CLICK_RESULT_WAIT):
                    return await self.cleared("solved:checkbox")

        if not supports(self.solver, "hcaptcha"):
            return await self.unsolved("captcha_required:hcaptcha")
        return await self.token_route(widget)

    async def geetest_button(self, widget: _Widget, stop: float) -> Optional[Dict[str, float]]:
        """The bounding box of GeeTest's visible "click to verify" button inside the incident frame, if rendered."""
        if widget.incident_frame is None:
            return None
        try:
            locator = widget.incident_frame.locator(GEETEST_BUTTONS).first
        except Exception:
            return None
        box = await bounded(locator.bounding_box(), stop, None, 2.0)
        if not box or box.get("width", 0) < 10 or box.get("height", 0) < 10:
            return None
        return box

    async def click_box(self, box: Dict[str, float], offset: Tuple[float, float]) -> bool:
        """One human-paced click at ``offset`` inside ``box`` (page coordinates), with a few pixels of jitter."""
        page, rng, deadline = self.page, self.rng, self.deadline
        if not box or box.get("width", 0) < 10 or box.get("height", 0) < 10:
            return False
        x = box["x"] + offset[0] + rng.uniform(-3, 3)
        y = box["y"] + offset[1] + rng.uniform(-3, 3)
        width, height = await viewport_size(page)
        start = (rng.uniform(0.3, 0.7) * width, rng.uniform(0.3, 0.7) * height)
        try:
            await page.mouse.move(*start)
            if not await move_along(page, human_path(start, (x, y), rng=rng, target_width=24.0), deadline):
                return False
            await sleep_until(deadline, rng.uniform(0.08, 0.25))
            await page.mouse.down()
            await sleep_until(deadline, rng.uniform(0.06, 0.14))
            await page.mouse.up()
        except Exception:
            return False
        return True

    async def token_route(self, widget: _Widget) -> SolveResult:
        """Get an hCaptcha token from the solver router, post it to Imperva's endpoint and reload."""
        provider = solver_name(self.solver)
        if not widget.sitekey or not widget.post_path:
            widget = await self.find_widget(self.deadline)
        if not widget.sitekey:
            return await self.unsolved("captcha_required:hcaptcha:no_sitekey")
        if not widget.post_path:
            return await self.unsolved("captcha_required:hcaptcha:no_submit_path")
        left = remaining(self.deadline) - SOLVER_MARGIN
        if left <= 1.0:
            return await self.unsolved("captcha_required:hcaptcha:no_time")
        try:
            token = await wait_for(
                self.solver.solve_token(
                    "hcaptcha", widget.sitekey, provider_url(self.page.url), deadline=self.deadline - SOLVER_MARGIN
                ),
                timeout=left,
            )
        except Exception as error:
            self.det.details["solver_error"] = type(error).__name__
            return await self.unsolved("captcha_required:hcaptcha:solver_error", provider)
        provider = getattr(token, "provider", None) or provider
        target = widget.incident_frame or self.page.main_frame
        status = await bounded(target.evaluate(_SUBMIT_JS, [widget.post_path, str(token)]), self.deadline, None, 10.0)
        if not isinstance(status, int) or status >= 400:
            self.det.details["token_post_status"] = status
            return await self.unsolved("captcha_required:hcaptcha:post_failed", provider)
        await reload_page(self.page, self.deadline)
        if await self.wait_cleared(remaining(self.deadline)):
            return await self.cleared("solved:hcaptcha_token", provider)
        return await self.unsolved("captcha_required:hcaptcha:rejected", provider)
