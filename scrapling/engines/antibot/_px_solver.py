"""Solving HUMAN's (PerimeterX) press-and-hold challenge in the page (the body of :meth:`PerimeterXHandler.solve`).

HUMAN answers a low-score visit with a "Press & Hold" page: a ``#px-captcha`` container that loads ``captcha.js``,
which builds the widget inside an iframe next to several invisible decoy iframes with the same title. Holding the
button fills a progress bar; when it is full the collector posts, HUMAN sets a fresh ``_px3`` (or ``_px2``) cookie
and the page reloads into the content.

The solver drives ``page.mouse`` (CDP input, works headless) and is ported from Averyy/wafer
``wafer/browser/_perimeterx.py`` (Apache-2.0, see NOTICE):

* find the real widget frame by its "Human verification" title and a visible ``role="button"``, skipping the
  0x0 decoys, and fall back to a visible iframe inside ``#px-captcha``, then to the container itself;
* idle for a moment, travel to the button along a human path, pause, press, and add hand tremor while holding;
* read the progress bar inside the widget frame and release 300-600 ms after it is full, but never before 5 s
  (HUMAN fakes fast fills as a honeypot); hold at most 20 s when the bar cannot be read;
* treat "Please try again" as a failed attempt and the removal of ``#px-captcha`` as success, then wait briefly
  for the refreshed ``_px3``. Up to three holds.

Wafer replays recorded human traces; this port synthesises them (see :mod:`._pointer`), so it ships no recordings.
"""

from __future__ import annotations

import random
from asyncio import wait_for
from time import monotonic

from scrapling.core._types import Any, Dict, List, Optional, Tuple
from scrapling.engines.antibot._pointer import Tremor, human_path, move_along, sleep_until, viewport_size, wander
from scrapling.engines.antibot.base import Detection, SolveResult, remaining

__all__ = [
    "solve_perimeterx",
    "PX_COOKIES",
    "PROGRESS_JS",
    "MIN_HOLD",
    "MAX_HOLD",
    "find_button",
    "find_widget_frame",
    "hold",
    "wait_for_result",
]

#: Cookies HUMAN sets for a cleared session, in the order they matter for replay.
PX_COOKIES = ("_px3", "_px2", "_pxhd", "_pxvid", "pxcts", "_pxde")

#: Fraction of the hold progress bar that is filled, read inside the widget frame (-1 when there is no bar).
#: The bar is the absolutely positioned, ``z-index: -1`` div inside ``role="button"`` (wafer's finding).
#: Written as an IIFE expression: Playwright would call a bare function string instead of evaluating it.
PROGRESS_JS = """(function() {
    var btn = document.querySelector('[role="button"]');
    if (!btn) return -1;
    var divs = btn.querySelectorAll('div');
    for (var i = 0; i < divs.length; i++) {
        var cs = getComputedStyle(divs[i]);
        if (cs.position === 'absolute' && cs.zIndex === '-1' && cs.height !== '0px') {
            var pw = divs[i].parentElement.getBoundingClientRect().width;
            var ew = divs[i].getBoundingClientRect().width;
            return pw > 0 ? ew / pw : 0;
        }
    }
    return -1;
})()"""

#: HUMAN fakes fast fills as a honeypot; real fills take 6-10 s, so never release before this.
MIN_HOLD = 5.0
#: Safety ceiling for a hold whose progress cannot be read.
MAX_HOLD = 20.0
_MAX_ATTEMPTS = 3
_RESULT_WAIT = 20.0
_BLOCK_TITLE = "access to this page has been denied"


async def solve_perimeterx(
    page: Any,
    det: Detection,
    *,
    deadline: float,
    log: Any,
    rng: Optional[random.Random] = None,
    max_attempts: int = _MAX_ATTEMPTS,
) -> SolveResult:
    """Press and hold HUMAN's button until the challenge clears, within ``deadline``.

    :param page: The Patchright/Playwright page showing the challenge.
    :param det: The detection; a ``block`` kind only gets a short look for a widget before giving up.
    :param deadline: ``time.monotonic()`` value the solve must finish by (including the button release).
    :param log: Logger.
    :param rng: Random source for the pointer model (seed it in tests).
    :param max_attempts: Holds to try; HUMAN serves a new widget after a failed hold.
    """
    rng = rng or random.Random()
    initial_px3 = await _cookie_value(page, ("_px3", "_px2"))

    if not await _wait_for_widget(page, deadline, 10.0 if det.kind == "captcha" else 3.0):
        if det.kind != "captcha":
            return SolveResult(solved=False, reason="unsolved:no_widget")
        # The widget never rendered: HUMAN sometimes clears on its own once the collector posts.
        if await _passive_clear(page, deadline, initial_px3, 5.0):
            return await _done(page, deadline, initial_px3, "solved:no_hold", log)
        return SolveResult(solved=False, reason="unsolved:no_widget")

    for attempt in range(1, max(1, max_attempts) + 1):
        if remaining(deadline) < MIN_HOLD + 2.0:
            return SolveResult(solved=False, reason="timeout")
        await _wait_for_widget_frame(page, deadline, 15.0)
        await sleep_until(deadline, rng.uniform(0.5, 1.0))

        found = await find_button(page, deadline, timeout=15.0, rng=rng)
        if found is None:
            if not await _has_widget(page):
                return await _done(page, deadline, initial_px3, "solved:no_hold", log)
            return SolveResult(solved=False, reason="unsolved:button_not_found")
        x, y, frame = found
        log.info(
            f"PerimeterX: hold attempt {attempt} at ({x:.0f}, {y:.0f}){'' if frame else ' without the widget frame'}"
        )

        await _approach(page, x, y, deadline, rng)
        await sleep_until(deadline, rng.uniform(0.3, 0.8))
        outcome = await hold(page, x, y, frame, deadline, rng=rng)
        log.debug(f"PerimeterX: hold ended ({outcome})")

        verdict = await wait_for_result(page, deadline, timeout=_RESULT_WAIT)
        if verdict == "solved":
            return await _done(page, deadline, initial_px3, "solved:press_and_hold", log)
        log.info(f"PerimeterX: attempt {attempt} did not clear ({verdict})")
        if verdict == "deadline":
            return SolveResult(solved=False, reason="timeout")
        await sleep_until(deadline, rng.uniform(1.0, 2.0))
        if not await _has_widget(page):
            return await _done(page, deadline, initial_px3, "solved:press_and_hold", log)

    return SolveResult(solved=False, reason="unsolved:attempts_exhausted")


async def _approach(page: Any, x: float, y: float, deadline: float, rng: random.Random) -> None:
    """Idle a moment somewhere on the page, then travel to the button."""
    width, height = await viewport_size(page)
    origin = (rng.uniform(0.3, 0.7) * width, rng.uniform(0.2, 0.5) * height)
    here = await wander(page, deadline, rng.uniform(0.6, 1.4), rng=rng, start=origin, scroll=False)
    await move_along(page, human_path(here, (x, y), rng=rng, target_width=60.0), deadline)


async def hold(
    page: Any, x: float, y: float, frame: Any, deadline: float, *, rng: Optional[random.Random] = None
) -> str:
    """Press at ``(x, y)``, tremble while the bar fills, release after a human reaction delay.

    The button is always released, including on errors and at the deadline, and the release happens before the
    deadline.

    :return: ``"filled"``, ``"frame_gone"``, ``"max_hold"`` or ``"deadline"``.
    """
    rng = rng or random.Random()
    tremor = Tremor()
    release_delay = rng.uniform(0.3, 0.6)
    start = monotonic()
    ceiling = start + MAX_HOLD
    stop = min(ceiling, deadline - release_delay - 0.25)
    outcome = "deadline" if stop < ceiling else "max_hold"
    await page.mouse.move(x, y)
    await page.mouse.down()
    last_move = last_check = start
    next_move = rng.uniform(0.04, 0.12)
    try:
        while monotonic() < stop:
            now = monotonic()
            if now - last_move >= next_move:
                dx, dy = tremor.step(now - last_move, rng)
                await page.mouse.move(x + dx, y + dy)
                last_move, next_move = now, rng.uniform(0.04, 0.12)
            if frame is not None and now - last_check >= 0.3:
                last_check = now
                fill = await _progress(frame)
                if fill is None:
                    outcome = "frame_gone"
                    break
                if fill >= 0.99 and now - start >= MIN_HOLD:
                    outcome = "filled"
                    break
            await sleep_until(stop, 0.03)
    finally:
        await sleep_until(deadline - 0.1, release_delay)
        try:
            await page.mouse.up()
        except Exception:  # pragma: no cover - the page may be navigating away
            pass
    return outcome


async def _done(page: Any, deadline: float, initial_px3: Optional[str], reason: str, log: Any) -> SolveResult:
    """Let the page settle and wait (briefly) for HUMAN to refresh ``_px3``."""
    budget = min(5.0, remaining(deadline) - 0.25)
    if budget > 0.1:
        try:
            await page.wait_for_load_state("load", timeout=int(budget * 1000))
        except Exception:
            pass
    stop = min(deadline - 0.25, monotonic() + 3.0)
    while monotonic() < stop:
        value = await _cookie_value(page, ("_px3", "_px2"))
        if value and value != initial_px3:
            break
        await sleep_until(stop, 0.25)
    if await _has_widget(page) or _BLOCK_TITLE in (await _title(page, deadline)).lower():
        # The widget came back, or the hold was answered with a plain block page.
        log.info("PerimeterX: still blocked after the hold")
        return SolveResult(solved=False, reason="unsolved:blocked_after_hold")
    names = await _cookie_names(page)
    log.info(f"PerimeterX: cleared ({reason})")
    return SolveResult(solved=True, reason=reason, cookies=[n for n in PX_COOKIES if n in names])


async def _title(page: Any, deadline: float) -> str:
    try:
        return str(await wait_for(page.title(), max(0.1, min(2.0, remaining(deadline)))))
    except Exception:
        return ""


# ---------------------------------------------------------------------- page helpers


async def _cookies(page: Any) -> List[Dict[str, Any]]:
    try:
        return await page.context.cookies([page.url])
    except Exception:
        return []


async def _cookie_names(page: Any) -> set:
    return {c.get("name") for c in await _cookies(page)}


async def _cookie_value(page: Any, names: Tuple[str, ...]) -> Optional[str]:
    for cookie in await _cookies(page):
        if cookie.get("name") in names:
            return cookie.get("value")
    return None


async def _has_widget(page: Any) -> bool:
    try:
        return await page.locator("#px-captcha").count() > 0
    except Exception:
        return False


async def _wait_for_widget(page: Any, deadline: float, timeout: float) -> bool:
    stop = min(deadline, monotonic() + timeout)
    while True:
        if await _has_widget(page):
            return True
        if not await sleep_until(stop, 0.5):
            return await _has_widget(page)


async def _wait_for_widget_frame(page: Any, deadline: float, timeout: float) -> None:
    """HUMAN injects the widget iframe a moment after the container."""
    stop = min(deadline, monotonic() + timeout)
    while monotonic() < stop:
        try:
            if await page.locator("#px-captcha iframe").count() > 0:
                return
        except Exception:
            pass
        await sleep_until(stop, 0.25)


async def _frame_title(frame: Any) -> str:
    try:
        return str(await wait_for(frame.evaluate("document.title"), 1.0) or "")
    except Exception:
        return ""


async def _progress(frame: Any) -> Optional[float]:
    """The bar's fill fraction (-1 when unreadable); ``None`` once the widget frame is gone."""
    if frame.is_detached():
        return None
    try:
        value = await wait_for(frame.evaluate(PROGRESS_JS), 1.0)
        return float(value) if isinstance(value, (int, float)) else -1.0
    except Exception:
        return None if frame.is_detached() else -1.0


def _point_in(
    box: Dict[str, float], rng: random.Random, xs: Tuple[float, float], ys: Tuple[float, float]
) -> Tuple[float, float]:
    return box["x"] + box["width"] * rng.uniform(*xs), box["y"] + box["height"] * rng.uniform(*ys)


def _visible(box: Optional[Dict[str, float]]) -> bool:
    return bool(box) and box["width"] > 10 and box["height"] > 10  # type: ignore[index]


async def _candidate_frames(page: Any) -> List[Any]:
    """Frames inside ``#px-captcha`` (and their children); every child frame when the container has none.

    Looking inside the container first keeps the title probe off the dozens of ad frames a retail page carries.
    """
    found: List[Any] = []
    try:
        iframes = page.locator("#px-captcha iframe")
        for index in range(await iframes.count()):
            handle = await iframes.nth(index).element_handle(timeout=500)
            frame = await handle.content_frame() if handle else None
            if frame is not None:
                found.append(frame)
    except Exception:
        pass
    queue = list(found)
    while queue:
        children = list(queue.pop(0).child_frames)
        found.extend(children)
        queue.extend(children)
    if found:
        return found
    return [frame for frame in page.frames if frame != page.main_frame]


async def find_widget_frame(page: Any) -> Optional[Any]:
    """The frame that holds the real, visible hold button (decoy frames have 0x0 buttons)."""
    for frame in await _candidate_frames(page):
        if "human verification" not in (await _frame_title(frame)).lower():
            continue
        try:
            button = frame.locator('[role="button"]')
            if await button.count() and _visible(await button.first.bounding_box(timeout=500)):
                return frame
        except Exception:  # nosec B112 - a decoy or detached frame: try the next one
            continue
    return None


async def find_button(
    page: Any, deadline: float, *, timeout: float = 15.0, rng: Optional[random.Random] = None
) -> Optional[Tuple[float, float, Optional[Any]]]:
    """Locate a point on the hold button, polling until it renders.

    The point is off-centre (20-80% of the width, 30-60% of the height) like a human press. Bounding boxes of
    elements inside iframes are relative to the main viewport, which is what ``page.mouse`` uses.

    :return: ``(x, y, frame)``; ``frame`` is the widget frame for progress reads, or ``None`` when only the
        container could be found. ``None`` when nothing visible appeared in time.
    """
    rng = rng or random.Random()
    stop = min(deadline, monotonic() + timeout)
    while True:
        frame = await find_widget_frame(page)
        if frame is not None:
            try:
                box = await frame.locator('[role="button"]').first.bounding_box(timeout=500)
                if _visible(box):
                    x, y = _point_in(box, rng, (0.2, 0.8), (0.3, 0.6))
                    return x, y, frame
            except Exception:
                pass
        # A visible iframe inside the container (the widget frame may have no title yet).
        try:
            iframes = page.locator("#px-captcha iframe")
            for index in range(await iframes.count()):
                box = await iframes.nth(index).bounding_box(timeout=500)
                if _visible(box):
                    x, y = _point_in(box, rng, (0.2, 0.8), (0.3, 0.6))
                    handle = await iframes.nth(index).element_handle(timeout=500)
                    inner = await handle.content_frame() if handle else None
                    return x, y, inner
        except Exception:
            pass
        if not await sleep_until(stop, 0.5):
            break
    # Last resort: the upper part of the container, where the button iframe sits.
    try:
        box = await page.locator("#px-captcha").first.bounding_box(timeout=500)
        if _visible(box):
            x, y = _point_in(box, rng, (0.3, 0.7), (0.15, 0.4))
            return x, y, None
    except Exception:
        pass
    return None


async def wait_for_result(page: Any, deadline: float, *, timeout: float = _RESULT_WAIT) -> str:
    """Watch the page after a hold.

    :return: ``"solved"`` when ``#px-captcha`` is gone (HUMAN reloads into the content), ``"try_again"`` when the
        widget asks for another hold, ``"timeout"``, or ``"deadline"`` when the solve's deadline cut the wait.
    """
    stop = min(deadline, monotonic() + timeout)
    while True:
        try:
            gone = await page.locator("#px-captcha").count() == 0
        except Exception:
            gone = False  # navigating
        if gone:
            return "solved"
        frame = await find_widget_frame(page)
        if frame is not None:
            try:
                text = str(await wait_for(frame.evaluate("document.body ? document.body.innerText : ''"), 1.0))
                if "try again" in text.lower():
                    return "try_again"
            except Exception:
                pass
        if not await sleep_until(stop, 0.5):
            return "deadline" if stop >= deadline else "timeout"


async def _passive_clear(page: Any, deadline: float, initial_px3: Optional[str], timeout: float) -> bool:
    """No widget rendered: wait briefly for a fresh ``_px3`` and the container to go away."""
    stop = min(deadline, monotonic() + timeout)
    while True:
        value = await _cookie_value(page, ("_px3", "_px2"))
        if value and value != initial_px3 and not await _has_widget(page):
            return True
        if not await sleep_until(stop, 0.5):
            return False
