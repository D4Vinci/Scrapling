"""DataDome: the solve loop against a local stand-in (see ``dd_server``), plus the pure helpers.

The stand-in serves its challenge frames from ``http://localhost:<port>``; the tests let the handler treat that
origin as DataDome's challenge host, which in production is only ``https://*.captcha-delivery.com``.
"""

import logging
from time import monotonic

import pytest

from scrapling.engines.antibot import datadome
from scrapling.engines.antibot.base import Detection, Signal, page_signal
from scrapling.engines.antibot.datadome import DataDomeHandler, _data_url_bytes, dd_challenge_markers
from scrapling.engines.antibot.headless import get_hardening, harden_page, quiet_evaluate

from .dd_server import DataDomeFixture, headless_page

log = logging.getLogger("tests.antibot.datadome")

PNG = (
    "data:image/png;base64,"
    "iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAAKUlEQVR4nGNkYPj/n4GBgYGJgYGBgYGBgYGBgYGBgYGBgYGBgYGBgQEAX7UEAZ0X"
    "B1EAAAAASUVORK5CYII="
)


class TestHelpers:
    def test_verdict_markers(self):
        assert dd_challenge_markers("<script>var dd={'rt':'i','cid':'x'}</script>")
        assert dd_challenge_markers('<script src="https://ct.captcha-delivery.com/c.js"></script>')
        # A cleared page keeps the tags.js sensor and may name the host in its config.
        assert not dd_challenge_markers(
            "<script>window.ddoptions={endpoint:'https://api-js.datadome.co/js/',x:'captcha-delivery.com'}</script>"
            '<script src="https://js.datadome.co/tags.js"></script><p>content</p>'
        )
        assert not dd_challenge_markers("")

    def test_data_url_bytes(self):
        assert _data_url_bytes(PNG).startswith(b"\x89PNG")
        assert _data_url_bytes("data:image/png;base64,AAAA") is None  # too small to be an image
        assert _data_url_bytes(None) is None
        assert _data_url_bytes("https://example.com/a.png") is None


class TestFinalVerdicts:
    @pytest.mark.asyncio
    async def test_ban_returns_at_once_without_touching_the_page(self):
        det = Detection("datadome", "ban", "dd.hard", {})
        result = await DataDomeHandler().solve(object(), det, deadline=monotonic() + 30, solver=None, log=log)
        assert (result.solved, result.reason) == (False, "ban")

    @pytest.mark.asyncio
    async def test_block_returns_at_once(self):
        det = Detection("datadome", "block", "dd.block", {})
        result = await DataDomeHandler().solve(object(), det, deadline=monotonic() + 30, solver=None, log=log)
        assert (result.solved, result.reason) == (False, "blocked")


@pytest.fixture(scope="module")
def server():
    srv = DataDomeFixture()
    yield srv
    srv.close()


@pytest.fixture
def local_frames(server, monkeypatch):
    """Let the handler treat the fixture's frame origin as DataDome's challenge host."""
    original = datadome.is_dd_frame

    def is_dd_frame(url: str) -> bool:
        return (url or "").startswith(server.frame_origin + "/") or original(url)

    monkeypatch.setattr(datadome, "is_dd_frame", is_dd_frame)
    return server


async def _open(page, url):
    response = await page.goto(url, wait_until="load")
    await page.wait_for_timeout(300)  # the inline script inserts the frame
    return await page_signal(page, status=response.status, headers=await response.all_headers())


async def _content(page) -> str:
    return await page.evaluate("document.body ? document.body.innerText : ''")


class FakeSolver:
    """Answers the slider from the fixture's known gap, and records what it was sent."""

    name = "fake"

    def __init__(self, gap: int):
        self.gap = gap
        self.calls = []

    def supports(self, kind: str) -> bool:
        return kind in ("datadome_slider", "slider")

    async def solve_token(self, kind, sitekey, page_url, **extra):  # pragma: no cover - not used
        raise NotImplementedError

    async def recognize(self, kind, images, **extra):
        self.calls.append((kind, [bytes(i[:8]) for i in images], sorted(extra)))
        return {"distance": self.gap, "provider": "fake", "task_id": None, "cost_usd": 0.0, "raw": {}}


class TestDeviceCheck:
    @pytest.mark.asyncio
    async def test_waits_for_the_cookie_and_the_frame_to_leave(self, local_frames):
        local_frames.reset()
        handler = DataDomeHandler()
        async with headless_page() as page:
            await harden_page(page)
            det = handler.detect(await _open(page, local_frames.url("/dd/pass")))
            assert det is not None and (det.kind, det.rule) == ("device_check", "dd.frame_device")
            deadline = monotonic() + 25
            result = await handler.solve(page, det, deadline=deadline, solver=None, log=log)
            assert monotonic() <= deadline
            assert (result.solved, result.reason, result.cookies) == (True, "solved", ["datadome"])
            assert "Products" in await _content(page)

    @pytest.mark.asyncio
    async def test_hardened_page_passes_a_consistency_check_that_a_plain_one_fails(self, local_frames):
        """The fixture's check compares the frame with the top page (screen, window, brands, UA), like DataDome's."""
        handler = DataDomeHandler()
        state = local_frames.reset()
        async with headless_page() as page:  # no hardening: the frame sees headless defaults
            det = handler.detect(await _open(page, local_frames.url("/dd/check")))
            result = await handler.solve(page, det, deadline=monotonic() + 20, solver=None, log=log)
            assert (result.solved, result.reason) == (False, "slider")
        plain = [r["why"] for r in state.reports if "why" in r]
        assert plain and plain[0], plain

        state = local_frames.reset()
        async with headless_page() as page:
            hardening = await harden_page(page)
            det = handler.detect(await _open(page, local_frames.url("/dd/check")))
            result = await handler.solve(page, det, deadline=monotonic() + 20, solver=None, log=log)
            assert result.solved, (result, [r for r in state.reports])
            assert hardening.children and hardening.children.attached.get("iframe", 0) >= 1
        assert [r["why"] for r in state.reports if "why" in r] == [[]]

    @pytest.mark.asyncio
    async def test_viewport_emulation_is_mirrored_into_the_frame(self, local_frames):
        """With Scrapling's default viewport emulation the frames still agree with the top page."""
        handler = DataDomeHandler()
        state = local_frames.reset()
        async with headless_page(no_viewport=False) as page:
            hardening = await harden_page(page)
            assert hardening.emulated_viewport
            det = handler.detect(await _open(page, local_frames.url("/dd/check")))
            result = await handler.solve(page, det, deadline=monotonic() + 20, solver=None, log=log)
            assert result.solved, [r for r in state.reports]

    @pytest.mark.asyncio
    async def test_clicks_the_confirm_button_with_a_trusted_click(self, local_frames):
        local_frames.reset()
        handler = DataDomeHandler()
        async with headless_page() as page:
            await harden_page(page)
            det = handler.detect(await _open(page, local_frames.url("/dd/confirm")))
            result = await handler.solve(page, det, deadline=monotonic() + 25, solver=None, log=log)
            assert (result.solved, result.reason) == (True, "solved")
            assert "Products" in await _content(page)

    @pytest.mark.asyncio
    async def test_restricted_device_stops(self, local_frames):
        local_frames.reset()
        handler = DataDomeHandler()
        async with headless_page() as page:
            await harden_page(page)
            det = handler.detect(await _open(page, local_frames.url("/dd/restricted")))
            start = monotonic()
            result = await handler.solve(page, det, deadline=start + 25, solver=None, log=log)
            assert (result.solved, result.reason) == (False, "blocked")
            assert monotonic() - start < 10

    @pytest.mark.asyncio
    async def test_never_runs_past_the_deadline(self, local_frames):
        local_frames.reset()
        handler = DataDomeHandler()
        async with headless_page() as page:
            await harden_page(page)
            det = handler.detect(await _open(page, local_frames.url("/dd/hang")))
            deadline = monotonic() + 4
            result = await handler.solve(page, det, deadline=deadline, solver=None, log=log)
            assert (result.solved, result.reason) == (False, "timeout")
            assert monotonic() <= deadline + 0.6  # one in-flight browser read may finish

    @pytest.mark.asyncio
    async def test_reads_leave_no_user_activation(self, local_frames):
        """The solver's reads never mark a frame as user-activated (Playwright evaluations and content() do)."""
        local_frames.reset()
        handler = DataDomeHandler()
        activated = "navigator.userActivation.hasBeenActive"
        async with headless_page() as page:
            await harden_page(page)
            response = await page.goto(local_frames.url("/dd/hang"), wait_until="load")
            await page.wait_for_timeout(300)
            html = await quiet_evaluate(page, page.main_frame, "document.documentElement.outerHTML")
            signal = Signal(
                url=page.url,
                status=response.status,
                headers=await response.all_headers(),
                html=html,
                frame_urls=[f.url for f in page.frames if f is not page.main_frame],
            )
            det = handler.detect(signal)
            assert det is not None
            await handler.solve(page, det, deadline=monotonic() + 3, solver=None, log=log)
            frame = handler._challenge_frame(page)
            assert frame is not None
            assert await quiet_evaluate(page, frame, activated) is False
            assert await quiet_evaluate(page, page.main_frame, activated) is False
            # For contrast: Playwright's own read sends a user gesture.
            await page.content()
            assert await quiet_evaluate(page, page.main_frame, activated) is True


class TestCaptcha:
    @pytest.mark.asyncio
    async def test_ban_in_the_frame_url_stops_at_once(self, local_frames):
        local_frames.reset()
        handler = DataDomeHandler()
        async with headless_page() as page:
            det = handler.detect(await _open(page, local_frames.url("/dd/ban")))
            assert det is not None and (det.kind, det.rule) == ("ban", "dd.hard")
            result = await handler.solve(page, det, deadline=monotonic() + 20, solver=None, log=log)
            assert (result.solved, result.reason) == (False, "ban")
            # The same verdict when the caller only knew it was a captcha.
            det = Detection("datadome", "captcha", "dd.captcha", {})
            start = monotonic()
            result = await handler.solve(page, det, deadline=start + 20, solver=None, log=log)
            assert result.reason == "ban" and monotonic() - start < 2

    @pytest.mark.asyncio
    async def test_slider_without_a_solver_stops_with_reason_slider(self, local_frames):
        local_frames.reset()
        handler = DataDomeHandler()
        async with headless_page() as page:
            await harden_page(page)
            det = handler.detect(await _open(page, local_frames.url("/dd/slider")))
            assert det is not None and det.kind == "captcha"
            start = monotonic()
            result = await handler.solve(page, det, deadline=start + 20, solver=None, log=log)
            assert (result.solved, result.reason, result.used_solver) == (False, "slider", None)
            assert result.solver_kind == "datadome_slider"  # a solver could take it from here
            assert monotonic() - start < 6

    @pytest.mark.asyncio
    async def test_slider_with_a_solver_is_dragged_into_place(self, local_frames):
        state = local_frames.reset()
        solver = FakeSolver(state.gap)
        handler = DataDomeHandler()
        async with headless_page() as page:
            await harden_page(page)
            det = handler.detect(await _open(page, local_frames.url("/dd/slider")))
            deadline = monotonic() + 30
            result = await handler.solve(page, det, deadline=deadline, solver=solver, log=log)
            assert monotonic() <= deadline
            assert (result.solved, result.reason, result.used_solver) == (True, "solved", "fake"), state.reports
            assert "Products" in await _content(page)
        kind, heads, options = solver.calls[0]
        assert kind == "datadome_slider"
        assert all(h.startswith(b"\x89PNG") for h in heads) and len(heads) == 2
        assert "proxy" not in options and "page_url" not in options  # only the two images leave the machine
        drags = [r["slider"] for r in state.reports if "slider" in r]
        assert drags and drags[-1]["ok"] and drags[-1]["trusted"]

    @pytest.mark.asyncio
    async def test_slide_to_target_variant_needs_no_recognition(self, local_frames):
        """DataDome's "simple" slider shows its target; with a solver configured it is dragged there unpaid."""
        state = local_frames.reset()
        solver = FakeSolver(state.gap)
        handler = DataDomeHandler()
        async with headless_page() as page:
            await harden_page(page)
            det = handler.detect(await _open(page, local_frames.url("/dd/simple")))
            result = await handler.solve(page, det, deadline=monotonic() + 30, solver=solver, log=log)
            assert (result.solved, result.reason) == (True, "solved"), state.reports
        assert solver.calls == []
        drags = [r["slider"] for r in state.reports if "slider" in r]
        assert drags and drags[-1]["ok"] and drags[-1]["trusted"]

    @pytest.mark.asyncio
    async def test_slide_to_target_needs_no_solver_at_all(self, local_frames):
        """The simple slider shows its target, so it is dragged there even with no solver configured."""
        state = local_frames.reset()
        handler = DataDomeHandler()
        async with headless_page() as page:
            await harden_page(page)
            det = handler.detect(await _open(page, local_frames.url("/dd/simple")))
            result = await handler.solve(page, det, deadline=monotonic() + 30, solver=None, log=log)
            assert (result.solved, result.reason, result.used_solver) == (True, "solved", None), state.reports
            assert "Products" in await _content(page)
        drags = [r["slider"] for r in state.reports if "slider" in r]
        assert drags and drags[-1]["ok"] and drags[-1]["trusted"]

    @pytest.mark.asyncio
    async def test_slide_to_target_dragging_can_be_turned_off(self, local_frames):
        state = local_frames.reset()
        handler = DataDomeHandler(drag_simple_slider=False)
        async with headless_page() as page:
            await harden_page(page)
            det = handler.detect(await _open(page, local_frames.url("/dd/simple")))
            result = await handler.solve(page, det, deadline=monotonic() + 20, solver=None, log=log)
            assert (result.solved, result.reason, result.solver_kind) == (False, "slider", None)
        assert not [r for r in state.reports if "slider" in r]

    @pytest.mark.asyncio
    async def test_wrong_answers_end_with_slider_failed(self, local_frames):
        state = local_frames.reset()
        solver = FakeSolver(state.gap + 120)  # always 60 CSS px off
        handler = DataDomeHandler(max_slider_attempts=2)
        async with headless_page() as page:
            await harden_page(page)
            det = handler.detect(await _open(page, local_frames.url("/dd/slider")))
            result = await handler.solve(page, det, deadline=monotonic() + 40, solver=solver, log=log)
            assert (result.solved, result.reason, result.used_solver) == (False, "slider_failed", "fake")
        assert len(solver.calls) == 2

    @pytest.mark.asyncio
    async def test_hardening_is_kept_per_page(self, local_frames):
        async with headless_page() as page:
            first = await harden_page(page)
            assert get_hardening(page) is first
            assert await harden_page(page) is first


class TestHeaderOnlyDetection:
    """A check detected from headers alone has no verdict in the DOM to watch, so only a new cookie or a new
    document counts; an unchanged page is never reported solved."""

    @staticmethod
    def _page(monkeypatch, html):
        from .iak_fakes import FakePage

        async def fake_quiet(page, frame, expression, timeout=2.0):
            return page.html

        monkeypatch.setattr(datadome, "quiet_evaluate", fake_quiet)
        page = FakePage("https://www.example.test/item", html)
        page.context.store["datadome"] = "same"
        return page

    HTML = "<html><head><title>x</title></head><body><p>Please enable JS and disable any ad blocker</p></body></html>"

    @pytest.mark.asyncio
    async def test_an_unchanged_page_ends_as_no_challenge(self, monkeypatch):
        page = self._page(monkeypatch, self.HTML)
        signal = Signal(url=page.url, status=403, headers={"x-dd-b": "3"}, cookies={"datadome": "same"}, html=self.HTML)
        handler = DataDomeHandler(no_frame_grace=0.6)
        det = handler.detect(signal)
        assert det is not None and (det.kind, det.rule) == ("device_check", "dd.device")
        result = await handler.solve(page, det, deadline=monotonic() + 5, solver=None, log=log)
        assert (result.solved, result.reason) == (False, "no_challenge")

    @pytest.mark.asyncio
    async def test_a_new_document_without_the_verdict_is_solved(self, monkeypatch):
        page = self._page(monkeypatch, self.HTML)
        page.at(0.3, lambda p: p.navigate("<html><body>" + "<p>Products and prices.</p>" * 20 + "</body></html>"))
        signal = Signal(url=page.url, status=403, headers={"x-dd-b": "3"}, cookies={"datadome": "same"}, html=self.HTML)
        handler = DataDomeHandler(no_frame_grace=2.0, poll=0.1)
        det = handler.detect(signal)
        result = await handler.solve(page, det, deadline=monotonic() + 5, solver=None, log=log)
        assert (result.solved, result.reason) == (True, "solved")
