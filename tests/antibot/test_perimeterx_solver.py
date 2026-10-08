"""HUMAN (PerimeterX): detection on fixtures, and the press-and-hold solver against a local stand-in page."""

import logging
import random
from time import monotonic

import pytest

from scrapling.engines.antibot._px_solver import MIN_HOLD, PROGRESS_JS
from scrapling.engines.antibot.base import Detection, Signal, page_signal
from scrapling.engines.antibot.perimeterx import PerimeterXHandler

from .pxak_server import FixtureServer, browser_page, fixture

log = logging.getLogger("tests.antibot.px")


def signal(html: str, status: int = 200, **kwargs) -> Signal:
    return Signal(url="https://www.example.com/search?q=x", status=status, html=html, **kwargs)


class TestDetect:
    handler = PerimeterXHandler()

    def test_block_page_with_widget_is_a_press_and_hold(self):
        det = self.handler.detect(signal(fixture("px_block.html"), 403))
        assert det is not None
        assert (det.vendor, det.kind, det.rule) == ("perimeterx", "captcha", "px.hold")
        assert det.details["app_id"] == "PXtest1234"

    def test_robot_or_human_page_served_with_200(self):
        det = self.handler.detect(signal(fixture("px_robot_or_human.html"), 200))
        assert det is not None and det.rule == "px.hold"

    def test_widget_frame_url_counts_as_the_widget(self):
        html = "<html><head><title>Access to this page has been denied</title></head><body>wait</body></html>"
        det = self.handler.detect(signal(html, 403, frame_urls=["https://captcha.px-cdn.net/PXabc123/captcha"]))
        assert det is not None and det.rule == "px.hold"

    def test_header_without_widget_is_a_block(self):
        det = self.handler.detect(signal("<html><body>blocked</body></html>", 403, headers={"X-PX-Blocked": "1"}))
        assert det is not None and (det.kind, det.rule) == ("block", "px.header")

    def test_sensor_only_page_is_not_a_detection(self):
        # A content page loading HUMAN's sensor, with a "px-captcha-container" class that must not match the id.
        assert (
            self.handler.detect(signal(fixture("px_presence.html"), 200, cookies={"_px3": "x", "_pxvid": "y"})) is None
        )

    def test_content_page_with_200_and_widget_id_but_much_text_is_not_a_detection(self):
        html = fixture("content.html").replace("<main>", '<main><div id="px-captcha"></div>')
        assert self.handler.detect(signal(html, 200)) is None


@pytest.fixture(scope="module")
def server():
    srv = FixtureServer()
    yield srv
    srv.close()


async def _open(page, url):
    response = await page.goto(url)
    await page.wait_for_load_state("load")
    return await page_signal(page, status=response.status, headers=await response.all_headers())


class TestPressAndHold:
    @pytest.mark.asyncio
    async def test_hold_until_the_bar_fills_clears_the_page(self, server):
        state = server.reset(px_need_ms=3000, px_fill_ms=3000)
        handler = PerimeterXHandler(rng=random.Random(7))
        async with browser_page() as page:
            det = handler.detect(await _open(page, server.url("/px/protected")))
            assert det is not None and det.rule == "px.hold"
            start = monotonic()
            deadline = start + 45
            result = await handler.solve(page, det, deadline=deadline, solver=None, log=log)
            assert monotonic() <= deadline
            assert result.solved, result
            assert result.reason == "solved:press_and_hold"
            assert "_px3" in result.cookies
            assert "Cordless drills" in await page.content()
            # The hold respected the honeypot floor and moved the pointer while held.
            outcome, data = state.px_holds[-1]
            assert outcome == "ok" and data["held"] >= MIN_HOLD * 1000 and data["moves"] >= 5
            assert handler.detect(await page_signal(page, status=200)) is None

    @pytest.mark.asyncio
    async def test_fast_fill_honeypot_is_held_past_the_floor(self, server):
        # The bar is full after 1 s but the check wants 5 s: releasing on the bar alone would fail.
        state = server.reset(px_need_ms=int(MIN_HOLD * 1000), px_fill_ms=1000)
        handler = PerimeterXHandler(rng=random.Random(11))
        async with browser_page() as page:
            det = handler.detect(await _open(page, server.url("/px/protected")))
            result = await handler.solve(page, det, deadline=monotonic() + 45, solver=None, log=log)
            assert result.solved, result
            assert [o for o, _ in state.px_holds] == ["ok"]

    @pytest.mark.asyncio
    async def test_progress_bar_is_read_in_the_widget_frame(self, server):
        server.reset(px_need_ms=3000, px_fill_ms=2000)
        async with browser_page() as page:
            await _open(page, server.url("/px/protected"))
            await page.wait_for_selector("#px-captcha iframe[src='/px/widget']")
            frame = next(f for f in page.frames if f.url.endswith("/px/widget"))
            await frame.wait_for_selector("[role=button]")
            assert await frame.evaluate(PROGRESS_JS) == 0
            box = await frame.locator("[role=button]").bounding_box()
            await page.mouse.move(box["x"] + 50, box["y"] + 30)
            await page.mouse.down()
            await page.wait_for_timeout(1200)
            fill = await frame.evaluate(PROGRESS_JS)
            await page.mouse.up()
            assert 0.3 < fill < 0.9

    @pytest.mark.asyncio
    async def test_widget_that_always_says_try_again_gives_up(self, server):
        state = server.reset(px_need_ms=1000, px_fill_ms=1000, px_always_fail=True)
        handler = PerimeterXHandler(max_attempts=1, rng=random.Random(3))
        async with browser_page() as page:
            det = handler.detect(await _open(page, server.url("/px/protected")))
            result = await handler.solve(page, det, deadline=monotonic() + 40, solver=None, log=log)
            assert not result.solved
            assert result.reason == "unsolved:attempts_exhausted"
            assert [o for o, _ in state.px_holds] == ["fail"]

    @pytest.mark.asyncio
    async def test_never_runs_past_the_deadline_and_releases_the_button(self, server):
        state = server.reset(px_need_ms=60000, px_fill_ms=60000)
        handler = PerimeterXHandler(rng=random.Random(5))
        async with browser_page() as page:
            det = handler.detect(await _open(page, server.url("/px/protected")))
            deadline = monotonic() + 12
            result = await handler.solve(page, det, deadline=deadline, solver=None, log=log)
            assert monotonic() <= deadline + 0.05
            assert not result.solved
            assert result.reason in ("timeout", "unsolved:attempts_exhausted")
            # mouseup reached the widget: the hold was reported (as a failure) instead of staying pressed.
            assert [o for o, _ in state.px_holds] == ["fail"]

    @pytest.mark.asyncio
    async def test_block_page_after_the_hold_is_not_reported_as_solved(self, server):
        server.reset(px_need_ms=3000, px_fill_ms=3000, px_block_after_hold=True)
        handler = PerimeterXHandler(rng=random.Random(13))
        async with browser_page() as page:
            det = handler.detect(await _open(page, server.url("/px/protected")))
            result = await handler.solve(page, det, deadline=monotonic() + 45, solver=None, log=log)
            assert (result.solved, result.reason) == (False, "unsolved:blocked_after_hold")

    @pytest.mark.asyncio
    async def test_block_without_widget_returns_quickly(self, server):
        handler = PerimeterXHandler()
        async with browser_page() as page:
            await page.goto(server.url("/nothing-here"))
            det = Detection(vendor="perimeterx", kind="block", rule="px.header", details={})
            start = monotonic()
            result = await handler.solve(page, det, deadline=start + 30, solver=None, log=log)
            assert (result.solved, result.reason) == (False, "unsolved:no_widget")
            assert monotonic() - start < 5
