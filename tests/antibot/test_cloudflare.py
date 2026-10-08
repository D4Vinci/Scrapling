"""The Cloudflare handler's solve: Scrapling's own solver, bounded by the deadline, then a re-check of the page."""

import asyncio
import logging
from time import monotonic
from types import SimpleNamespace

import pytest

from scrapling.engines._browsers._stealth import AsyncStealthySession
from scrapling.engines.antibot.base import Detection, Signal
from scrapling.engines.antibot.cloudflare import CloudflareHandler

LOG = logging.getLogger("antibot-test")
CHALLENGE = (
    "<html><head><title>Just a moment...</title></head><body><script>window._cf_chl_opt = {cType: 'managed'};"
    '</script><script src="/cdn-cgi/challenge-platform/h/b/orchestrate/chl_page/v1?ray=1"></script></body></html>'
)
CLEARED = "<html><head><title>Example</title></head><body>" + "<p>Real content.</p>" * 200 + "</body></html>"
TURNSTILE_GATE = (
    '<html><head><title>Verify</title></head><body><form><div class="cf-turnstile" data-sitekey="0x4AAAAAAAExample" '
    'data-action="login" data-callback="onOk"></div><input type="hidden" name="cf-turnstile-response" value="">'
    "</form></body></html>"
)


class FakePage:
    """Just enough of a Patchright page for the handler and Scrapling's solver to run against."""

    def __init__(self, html, cookies=None):
        self.url = "https://www.example.com/"
        self.html = html
        self.cookie_jar = list(cookies or [])
        self.timeouts = []
        self.evaluated = []
        self.on_evaluate = None
        self.main_frame = SimpleNamespace(url=self.url)
        self.frames = [self.main_frame]
        self.context = SimpleNamespace(cookies=self._cookies)

    async def content(self):
        return self.html

    async def _cookies(self):
        return list(self.cookie_jar)

    def set_default_timeout(self, ms):
        self.timeouts.append(ms)

    async def wait_for_load_state(self, state="load", timeout=None):
        return None

    async def evaluate(self, expression, arg=None, *, isolated_context=True):
        self.evaluated.append((expression, arg, isolated_context))
        if self.on_evaluate:
            self.on_evaluate(arg)


def clear(page):
    page.html = CLEARED
    page.cookie_jar.append({"name": "cf_clearance", "value": "new", "domain": ".example.com"})


@pytest.fixture
def handler():
    return CloudflareHandler()


def detection_for(html, status=403):
    det = CloudflareHandler().detect(Signal("https://www.example.com/", status, {"server": "cloudflare"}, {}, html, []))
    assert det is not None
    return det


@pytest.mark.asyncio
async def test_blocks_are_not_attempted(handler, monkeypatch):
    called = []

    async def solver(self, page, _attempts=0):
        called.append(page)

    monkeypatch.setattr(AsyncStealthySession, "_cloudflare_solver", solver)
    det = Detection("cloudflare", "block", "cf.waf")
    result = await handler.solve(FakePage(CHALLENGE), det, deadline=monotonic() + 30, solver=None, log=LOG)
    assert (result.solved, result.reason) == (False, "block:cf.waf")
    assert called == []


@pytest.mark.asyncio
async def test_no_time_left(handler):
    det = detection_for(CHALLENGE)
    result = await handler.solve(FakePage(CHALLENGE), det, deadline=monotonic() + 0.5, solver=None, log=LOG)
    assert (result.solved, result.reason) == (False, "timeout")


@pytest.mark.asyncio
async def test_solved_challenge_reports_the_clearance_cookie(handler, monkeypatch):
    async def solver(self, page, _attempts=0):
        clear(page)

    monkeypatch.setattr(AsyncStealthySession, "_cloudflare_solver", solver)
    page = FakePage(CHALLENGE, cookies=[{"name": "__cf_bm", "value": "same", "domain": ".example.com"}])
    result = await handler.solve(page, detection_for(CHALLENGE), deadline=monotonic() + 30, solver=None, log=LOG)
    assert result.solved and result.reason == "solved"
    assert result.cookies == ["cf_clearance"]
    # Every wait inside Scrapling's solver is capped, and the page gets the rest of the budget back afterwards.
    assert page.timeouts[0] <= 5000 and page.timeouts[-1] >= 1000


@pytest.mark.asyncio
async def test_challenge_still_present(handler, monkeypatch):
    runs = []

    async def solver(self, page, _attempts=0):
        runs.append(page)

    monkeypatch.setattr(AsyncStealthySession, "_cloudflare_solver", solver)
    result = await handler.solve(FakePage(CHALLENGE), detection_for(CHALLENGE), deadline=monotonic() + 30, solver=None, log=LOG)
    assert (result.solved, result.reason) == (False, "unsolved:cf.interstitial")
    assert len(runs) == 2  # one repeat, no more


@pytest.mark.asyncio
async def test_a_run_that_fails_part_way_is_repeated(handler, monkeypatch):
    runs = []

    async def solver(self, page, _attempts=0):
        runs.append(page)
        if len(runs) == 1:
            raise TimeoutError("Locator.bounding_box: Timeout 5000ms exceeded.")
        clear(page)

    monkeypatch.setattr(AsyncStealthySession, "_cloudflare_solver", solver)
    result = await handler.solve(FakePage(CHALLENGE), detection_for(CHALLENGE), deadline=monotonic() + 30, solver=None, log=LOG)
    assert result.solved and len(runs) == 2


@pytest.mark.asyncio
async def test_challenge_that_turns_into_a_block(handler, monkeypatch):
    async def solver(self, page, _attempts=0):
        page.html = (
            "<html><head><title>Attention Required! | Cloudflare</title></head><body><h1>Sorry, you have been blocked</h1>"
            "<p>Cloudflare Ray ID: 8a1b2c3d4e5f6789</p></body></html>"
        )

    monkeypatch.setattr(AsyncStealthySession, "_cloudflare_solver", solver)
    result = await handler.solve(FakePage(CHALLENGE), detection_for(CHALLENGE), deadline=monotonic() + 30, solver=None, log=LOG)
    assert (result.solved, result.reason) == (False, "block:cf.waf")


@pytest.mark.asyncio
async def test_solver_errors_are_contained(handler, monkeypatch):
    async def solver(self, page, _attempts=0):
        raise RuntimeError("Target page, context or browser has been closed")

    monkeypatch.setattr(AsyncStealthySession, "_cloudflare_solver", solver)
    result = await handler.solve(FakePage(CHALLENGE), detection_for(CHALLENGE), deadline=monotonic() + 30, solver=None, log=LOG)
    assert not result.solved


@pytest.mark.asyncio
async def test_a_hanging_solver_never_outlives_the_deadline(handler, monkeypatch):
    async def solver(self, page, _attempts=0):
        await asyncio.sleep(30)

    monkeypatch.setattr(AsyncStealthySession, "_cloudflare_solver", solver)
    started = monotonic()
    deadline = started + 2.5
    result = await handler.solve(FakePage(CHALLENGE), detection_for(CHALLENGE), deadline=deadline, solver=None, log=LOG)
    assert monotonic() <= deadline
    assert (result.solved, result.reason) == (False, "timeout")


@pytest.mark.asyncio
async def test_the_real_scrapling_solver_runs_against_the_page(handler, monkeypatch):
    """No patching of the solver itself: a non-interactive challenge that clears on the first poll."""
    page = FakePage(CHALLENGE.replace("managed", "non-interactive"))

    async def wait_for_timeout(ms):
        clear(page)

    page.wait_for_timeout = wait_for_timeout
    result = await handler.solve(page, detection_for(page.html), deadline=monotonic() + 30, solver=None, log=LOG)
    assert result.solved and result.cookies == ["cf_clearance"]


class FakeRouter:
    name = "router"

    def __init__(self):
        self.calls = []

    async def solve_token(self, kind, sitekey, page_url, **extra):
        self.calls.append((kind, sitekey, page_url, extra))
        token = type("Token", (str,), {})("tok-123")
        token.provider = "capmonster"
        return token


@pytest.mark.asyncio
async def test_turnstile_gate_uses_the_captcha_solver(handler, monkeypatch):
    async def solver(self, page, _attempts=0):
        return None  # the click does not clear this widget

    monkeypatch.setattr(AsyncStealthySession, "_cloudflare_solver", solver)
    page = FakePage(TURNSTILE_GATE)
    page.on_evaluate = lambda arg: clear(page)
    router = FakeRouter()
    det = detection_for(TURNSTILE_GATE, status=200)
    assert det.kind == "captcha"
    result = await handler.solve(page, det, deadline=monotonic() + 30, solver=router, log=LOG)
    assert result.solved and result.used_solver == "capmonster"
    kind, sitekey, url, extra = router.calls[0]
    assert (kind, sitekey, url) == ("turnstile", "0x4AAAAAAAExample", "https://www.example.com/")
    assert extra["action"] == "login" and "deadline" in extra
    expression, arg, isolated = page.evaluated[0]
    assert arg == ["tok-123", "onOk"] and isolated is False
    assert "cf-turnstile-response" in expression


@pytest.mark.asyncio
async def test_turnstile_without_a_solver_is_unsolved(handler, monkeypatch):
    async def solver(self, page, _attempts=0):
        return None

    monkeypatch.setattr(AsyncStealthySession, "_cloudflare_solver", solver)
    det = detection_for(TURNSTILE_GATE, status=200)
    result = await handler.solve(FakePage(TURNSTILE_GATE), det, deadline=monotonic() + 30, solver=None, log=LOG)
    assert (result.solved, result.reason) == (False, "unsolved:cf.turnstile")


@pytest.mark.asyncio
async def test_turnstile_token_that_is_not_accepted(handler, monkeypatch):
    async def solver(self, page, _attempts=0):
        return None

    monkeypatch.setattr(AsyncStealthySession, "_cloudflare_solver", solver)
    det = detection_for(TURNSTILE_GATE, status=200)
    page = FakePage(TURNSTILE_GATE)
    result = await handler.solve(page, det, deadline=monotonic() + 30, solver=FakeRouter(), log=LOG)
    assert (result.solved, result.reason, result.used_solver) == (False, "unsolved:turnstile_token_not_accepted", "capmonster")
