"""Human-paced pointer input for the anti-bot handlers.

Everything here goes through Playwright's ``page.mouse``, which sends CDP
``Input.dispatchMouseEvent`` events. Those reach the page the same way in a
headless browser as in a headed one, so no window is ever needed.

The timing model follows the press-and-hold work in Averyy/wafer
(``wafer/browser/_perimeterx.py``, Apache-2.0, see NOTICE): a pre-hold idle,
a path to the target, a short hover pause, a hold with small hand tremor and
a human reaction delay before release. Wafer replays recorded human traces;
this module synthesises comparable ones instead, so the fork ships no
recordings:

* paths are cubic Bezier curves walked with a minimum-jerk velocity profile,
  timed by Fitts' law, with sub-pixel noise and an occasional overshoot;
* the hold tremor is an Ornstein-Uhlenbeck process around the anchor point.

Every coroutine takes a ``deadline`` (``time.monotonic()`` seconds) and never
sleeps past it.
"""

from __future__ import annotations

import math
import random
from asyncio import sleep as asyncio_sleep
from dataclasses import dataclass
from time import monotonic

from scrapling.core._types import Any, List, Optional, Tuple
from scrapling.engines.antibot.base import remaining

__all__ = [
    "Point",
    "remaining",
    "sleep_until",
    "human_path",
    "move_along",
    "Tremor",
    "viewport_size",
    "wander",
]

Point = Tuple[float, float]


async def sleep_until(deadline: float, seconds: float) -> bool:
    """Sleep ``seconds`` or until ``deadline``, whichever comes first.

    :return: ``True`` when the full ``seconds`` were slept, ``False`` when the deadline cut the sleep short.
    """
    left = remaining(deadline)
    if seconds <= left:
        if seconds > 0:
            await asyncio_sleep(seconds)
        return True
    if left > 0:
        await asyncio_sleep(left)
    return False


def _min_jerk(tau: float) -> float:
    """Minimum-jerk position profile on [0, 1] (bell-shaped velocity)."""
    return tau * tau * tau * (10.0 - 15.0 * tau + 6.0 * tau * tau)


def _bezier(p0: Point, p1: Point, p2: Point, p3: Point, t: float) -> Point:
    u = 1.0 - t
    a, b, c, d = u * u * u, 3 * u * u * t, 3 * u * t * t, t * t * t
    return (
        a * p0[0] + b * p1[0] + c * p2[0] + d * p3[0],
        a * p0[1] + b * p1[1] + c * p2[1] + d * p3[1],
    )


def _segment(
    start: Point, end: Point, rng: random.Random, target_width: float, t0: float
) -> List[Tuple[float, float, float]]:
    """One Bezier stroke from ``start`` to ``end`` as ``(t, x, y)`` samples starting at ``t0``."""
    dx, dy = end[0] - start[0], end[1] - start[1]
    distance = math.hypot(dx, dy)
    if distance < 1.0:
        return [(t0, end[0], end[1])]

    # Fitts' law: MT = a + b * log2(1 + D / W), with per-stroke variation.
    a = rng.uniform(0.12, 0.22)
    b = rng.uniform(0.09, 0.14)
    duration = a + b * math.log2(1.0 + distance / max(4.0, target_width))

    # Control points bow the stroke to one side, like a wrist pivot.
    nx, ny = -dy / distance, dx / distance
    bow = rng.uniform(0.05, 0.25) * distance * rng.choice((-1.0, 1.0))
    p1 = (start[0] + dx * rng.uniform(0.2, 0.4) + nx * bow, start[1] + dy * rng.uniform(0.2, 0.4) + ny * bow)
    p2 = (
        start[0] + dx * rng.uniform(0.6, 0.8) + nx * bow * 0.5,
        start[1] + dy * rng.uniform(0.6, 0.8) + ny * bow * 0.5,
    )

    samples: List[Tuple[float, float, float]] = []
    elapsed = 0.0
    while elapsed < duration:
        elapsed = min(duration, elapsed + rng.uniform(0.008, 0.018))
        x, y = _bezier(start, p1, p2, end, _min_jerk(elapsed / duration))
        if elapsed < duration:
            x += rng.gauss(0.0, 0.35)
            y += rng.gauss(0.0, 0.35)
        samples.append((t0 + elapsed, x, y))
    samples[-1] = (samples[-1][0], end[0], end[1])
    return samples


def human_path(
    start: Point,
    end: Point,
    *,
    rng: Optional[random.Random] = None,
    target_width: float = 40.0,
    overshoot_chance: float = 0.3,
) -> List[Tuple[float, float, float]]:
    """A human-looking pointer path from ``start`` to ``end``.

    :param start: Starting point in CSS pixels.
    :param end: Final point in CSS pixels; the last sample lands exactly on it.
    :param rng: Random source (pass a seeded one for reproducible paths).
    :param target_width: Width of the target, which sets the Fitts' law index of difficulty.
    :param overshoot_chance: Chance of overshooting a long move and correcting back.
    :return: ``(t, x, y)`` samples, ``t`` in seconds from the start, strictly increasing.
    """
    rng = rng or random.Random()
    distance = math.hypot(end[0] - start[0], end[1] - start[1])
    if distance > 150 and rng.random() < overshoot_chance:
        dx, dy = (end[0] - start[0]) / distance, (end[1] - start[1]) / distance
        over = rng.uniform(4.0, 12.0)
        mid = (end[0] + dx * over + rng.gauss(0, 2), end[1] + dy * over + rng.gauss(0, 2))
        first = _segment(start, mid, rng, target_width, 0.0)
        pause = first[-1][0] + rng.uniform(0.04, 0.12)
        return first + _segment(mid, end, rng, target_width, pause)
    return _segment(start, end, rng, target_width, 0.0)


async def move_along(page: Any, path: List[Tuple[float, float, float]], deadline: float) -> bool:
    """Replay a path from :func:`human_path` on ``page.mouse`` in real time.

    :return: ``True`` when the whole path was replayed, ``False`` when the deadline stopped it.
    """
    t_start = monotonic()
    for t, x, y in path:
        wait = t - (monotonic() - t_start)
        if wait > 0 and not await sleep_until(deadline, wait):
            return False
        if remaining(deadline) <= 0:
            return False
        await page.mouse.move(x, y)
    return True


@dataclass
class Tremor:
    """Hand tremor while a button is held: an Ornstein-Uhlenbeck drift around an anchor.

    :param theta: Pull back towards the anchor, per second.
    :param sigma: Noise strength in pixels per square-root second.
    :param limit: Hard clip on the offset from the anchor, in pixels, so the pointer never leaves the button.
    """

    theta: float = 2.5
    sigma: float = 2.2
    limit: float = 4.0
    dx: float = 0.0
    dy: float = 0.0

    def step(self, dt: float, rng: random.Random) -> Point:
        """Advance the drift by ``dt`` seconds and return the new ``(dx, dy)`` offset."""
        dt = max(0.0, dt)
        scale = self.sigma * math.sqrt(dt)
        self.dx += -self.theta * self.dx * dt + scale * rng.gauss(0.0, 1.0)
        self.dy += -self.theta * self.dy * dt + scale * rng.gauss(0.0, 1.0)
        self.dx = max(-self.limit, min(self.limit, self.dx))
        self.dy = max(-self.limit, min(self.limit, self.dy))
        return self.dx, self.dy


async def viewport_size(page: Any) -> Tuple[float, float]:
    """The page's layout viewport, even when the context has no viewport emulation."""
    size = getattr(page, "viewport_size", None)
    if size and size.get("width", 0) > 0 and size.get("height", 0) > 0:
        return float(size["width"]), float(size["height"])
    try:
        width, height = await page.evaluate("[innerWidth, innerHeight]")
        if width > 0 and height > 0:
            return float(width), float(height)
    except Exception:
        pass
    return 1280.0, 720.0


async def wander(
    page: Any,
    deadline: float,
    duration: float,
    *,
    rng: Optional[random.Random] = None,
    start: Optional[Point] = None,
    scroll: bool = True,
) -> Point:
    """Browse-like pointer activity for ``duration`` seconds: short strokes, pauses and the odd wheel tick.

    Behavioural sensors (Akamai ``bmak``, HUMAN's collector) post when they see input; this gives them input
    without clicking or typing anything.

    :return: The last pointer position.
    """
    rng = rng or random.Random()
    width, height = await viewport_size(page)
    x, y = start if start else (rng.uniform(0.3, 0.7) * width, rng.uniform(0.25, 0.6) * height)
    stop = min(deadline, monotonic() + max(0.0, duration))
    try:
        await page.mouse.move(x, y)
    except Exception:
        return x, y
    while remaining(stop) > 0.05:
        target = (
            min(width - 2.0, max(2.0, x + rng.gauss(0, width * 0.15))),
            min(height - 2.0, max(2.0, y + rng.gauss(0, height * 0.12))),
        )
        try:
            path = [
                (t, min(width - 1.0, max(1.0, px)), min(height - 1.0, max(1.0, py)))
                for t, px, py in human_path((x, y), target, rng=rng, target_width=80.0)
            ]
            if not await move_along(page, path, stop):
                break
            x, y = target
            if scroll and rng.random() < 0.25:
                await page.mouse.wheel(0, rng.choice((1, 1, 1, -1)) * rng.uniform(60, 240))
        except Exception:
            break
        if not await sleep_until(stop, rng.uniform(0.15, 0.6)):
            break
    return x, y
