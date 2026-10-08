"""Imperva, AWS WAF and Kasada solvers in a real headless browser, against the local stand-in site (``iak_server``).

Uses the same headless Chromium launcher as the Akamai/HUMAN browser tests (``SCRAPLING_TEST_CHROME`` may point at
a Chromium-compatible executable); the tests are skipped when no browser can be launched.
"""

import logging
from time import monotonic

import pytest

from scrapling.engines.antibot import _awswaf_solver, _imperva_solver, _kasada_solver
from scrapling.engines.antibot._kasada_solver import kasada_tokens, unwatch_kasada, watch_kasada
from scrapling.engines.antibot.awswaf import AwsWafHandler
from scrapling.engines.antibot.base import page_signal
from scrapling.engines.antibot.imperva import ImpervaHandler
from scrapling.engines.antibot.kasada import KasadaHandler

from .iak_fakes import FakeSolver
from .iak_server import AWS_ANSWER, IakServer
from .pxak_server import browser_page

log = logging.getLogger("tests.antibot.iak")


@pytest.fixture(scope="module")
def server():
    srv = IakServer()
    yield srv
    srv.close()


@pytest.fixture(autouse=True)
def quick(monkeypatch):
    for module in (_imperva_solver, _awswaf_solver, _kasada_solver):
        monkeypatch.setattr(module, "RELOAD_AFTER", 1.0)
    monkeypatch.setattr(_awswaf_solver, "PROBLEM_WAIT", 1.5)
    monkeypatch.setattr(_awswaf_solver, "AWS_HOSTS", ("awswaf.com", "127.0.0.1"))


async def _open(page, url):
    response = await page.goto(url)
    return await page_signal(page, status=response.status, headers=await response.all_headers())


async def _solve(handler, page, det, budget=20.0, solver=None):
    deadline = monotonic() + budget
    result = await handler.solve(page, det, deadline=deadline, solver=solver, log=log)
    assert monotonic() <= deadline + 0.05, "the solve ran past its deadline"
    return result


async def _content(page):
    return await page.content()


class TestImperva:
    @pytest.mark.asyncio
    async def test_reese84_interstitial_clears_itself(self, server):
        state = server.reset()
        async with browser_page() as page:
            det = ImpervaHandler().detect(await _open(page, server.url("/imperva")))
            assert det is not None and det.rule == "imperva.interstitial"
            result = await _solve(ImpervaHandler(), page, det)
            assert result.solved and result.reason == "solved", result
            assert "reese84" in result.cookies and state.sensor_posts == 1
            assert det.details.get("renew_in_sec") in (None, 896)
            assert "Catalogue" in await _content(page)

    @pytest.mark.asyncio
    async def test_stalled_interstitial_is_reloaded_once(self, server):
        server.reset()
        async with browser_page() as page:
            det = ImpervaHandler().detect(await _open(page, server.url("/imperva?stall=1")))
            result = await _solve(ImpervaHandler(), page, det)
            assert result.solved, result
            assert "Catalogue" in await _content(page)


class TestAwsWaf:
    @pytest.mark.asyncio
    async def test_challenge_clears_itself(self, server):
        server.reset()
        async with browser_page() as page:
            det = AwsWafHandler().detect(await _open(page, server.url("/aws/challenge")))
            assert det is not None and det.rule == "aws.challenge"
            result = await _solve(AwsWafHandler(), page, det)
            assert result.solved and result.cookies == ["aws-waf-token"], result

    @pytest.mark.asyncio
    async def test_stalled_challenge_is_reloaded_once(self, server):
        server.reset()
        async with browser_page() as page:
            det = AwsWafHandler().detect(await _open(page, server.url("/aws/challenge?stall=1")))
            result = await _solve(AwsWafHandler(), page, det)
            assert result.solved, result

    @pytest.mark.asyncio
    async def test_captcha_without_a_solver(self, server):
        server.reset()
        async with browser_page() as page:
            det = AwsWafHandler().detect(await _open(page, server.url("/aws/captcha")))
            assert det is not None and det.kind == "captcha"
            result = await _solve(AwsWafHandler(), page, det)
            assert (result.solved, result.reason) == (False, "captcha_required")

    @pytest.mark.asyncio
    async def test_captcha_by_recognition_clicks_the_right_cells(self, server):
        state = server.reset()
        solver = FakeSolver(("awswaf_images",), answer={"objects": AWS_ANSWER})
        async with browser_page() as page:
            det = AwsWafHandler().detect(await _open(page, server.url("/aws/captcha")))
            result = await _solve(AwsWafHandler(), page, det, budget=30.0, solver=solver)
            assert result.solved and result.reason == "solved:awswaf_images", result
            assert result.used_solver == "fakeprov"
            kind, n_images, _, extra = solver.calls[0]
            assert (kind, n_images, extra["question"]) == ("awswaf_images", 9, "aws:grid:bed")
            assert state.verify == [AWS_ANSWER]
            assert "Catalogue" in await _content(page)


class TestKasada:
    @pytest.mark.asyncio
    async def test_challenge_clears_and_tokens_are_kept(self, server):
        state = server.reset()
        async with browser_page() as page:
            watch_kasada(page)
            try:
                det = KasadaHandler().detect(await _open(page, server.url("/kasada")))
                assert det is not None and det.rule == "kasada.header"
                result = await _solve(KasadaHandler(), page, det)
                assert result.solved, result
                assert result.cookies == ["KP_UIDz", "KP_UIDz-ssn"] and state.tl_posts == 1
                tokens = kasada_tokens(page)
                assert tokens["st"] == 1759149934586
                assert tokens["ct"] in ("02tlvalue", "03refreshed") and tokens["ct_source"] == "header"
            finally:
                unwatch_kasada(page)
