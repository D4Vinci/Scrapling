"""The synthetic pointer model used by the press-and-hold and sensor handlers."""

import math
import random
from time import monotonic

import pytest

from scrapling.engines.antibot._pointer import Tremor, human_path, move_along, sleep_until, wander


class FakeMouse:
    def __init__(self):
        self.moves = []
        self.wheels = []

    async def move(self, x, y):
        self.moves.append((monotonic(), x, y))

    async def wheel(self, dx, dy):
        self.wheels.append((dx, dy))


class FakePage:
    viewport_size = {"width": 1280, "height": 800}

    def __init__(self):
        self.mouse = FakeMouse()


@pytest.mark.parametrize("seed", range(20))
def test_human_path_shape(seed):
    rng = random.Random(seed)
    start, end = (rng.uniform(0, 1200), rng.uniform(0, 800)), (rng.uniform(0, 1200), rng.uniform(0, 800))
    path = human_path(start, end, rng=rng)
    times = [t for t, _, _ in path]
    assert path[-1][1:] == end
    assert all(b > a for a, b in zip(times, times[1:]))
    distance = math.dist(start, end)
    # Fitts-like duration: a few hundred ms, not instantaneous and not seconds-long.
    assert 0.1 <= times[-1] <= 2.0 or distance < 1
    # Sampled like real input (roughly 50-125 Hz), and never far off the start-end corridor.
    if len(times) > 2:
        gaps = [b - a for a, b in zip(times, times[1:])]
        assert max(gaps) <= 0.2
    for _, x, y in path:
        assert min(start[0], end[0]) - distance <= x <= max(start[0], end[0]) + distance


def test_human_path_is_not_a_straight_line():
    rng = random.Random(4)
    path = human_path((100, 100), (900, 500), rng=rng, overshoot_chance=0)
    (x0, y0), (x1, y1) = (100, 100), (900, 500)
    deviations = [
        abs((y1 - y0) * x - (x1 - x0) * y + x1 * y0 - y1 * x0) / math.dist((x0, y0), (x1, y1)) for _, x, y in path
    ]
    assert max(deviations) > 5


def test_tremor_stays_on_the_button():
    rng = random.Random(9)
    tremor = Tremor(limit=4.0)
    offsets = [tremor.step(0.08, rng) for _ in range(500)]
    assert all(abs(dx) <= 4.0 and abs(dy) <= 4.0 for dx, dy in offsets)
    assert len({(round(dx, 2), round(dy, 2)) for dx, dy in offsets}) > 100  # it moves


@pytest.mark.asyncio
async def test_sleep_until_respects_the_deadline():
    start = monotonic()
    assert await sleep_until(start + 0.2, 0.05) is True
    assert await sleep_until(start + 0.15, 5.0) is False
    assert monotonic() - start < 0.4


@pytest.mark.asyncio
async def test_move_along_replays_in_real_time_and_stops_at_the_deadline():
    page = FakePage()
    path = human_path((10, 10), (600, 400), rng=random.Random(2), overshoot_chance=0)
    start = monotonic()
    assert await move_along(page, path, start + 10) is True
    assert page.mouse.moves[-1][1:] == (600, 400)
    assert monotonic() - start >= path[-1][0] * 0.9

    page = FakePage()
    start = monotonic()
    assert await move_along(page, human_path((0, 0), (1200, 800), rng=random.Random(3)), start + 0.05) is False
    assert monotonic() - start < 0.2


@pytest.mark.asyncio
async def test_wander_stays_inside_the_viewport():
    page = FakePage()
    start = monotonic()
    await wander(page, start + 5, 1.2, rng=random.Random(6))
    assert 1.0 <= monotonic() - start < 1.6
    assert page.mouse.moves
    assert all(0 <= x <= 1280 and 0 <= y <= 800 for _, x, y in page.mouse.moves)
