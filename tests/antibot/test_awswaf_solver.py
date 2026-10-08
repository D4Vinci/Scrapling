"""AWS WAF: the in-page solver against scripted pages (silent challenge, CAPTCHA with token/voucher solvers)."""

import base64
import json
from time import monotonic

import pytest

from scrapling.engines.antibot import _awswaf_solver as solver_module
from scrapling.engines.antibot._awswaf_solver import aws_scripts, problem_images, problem_question
from scrapling.engines.antibot.awswaf import AwsWafHandler
from scrapling.engines.antibot.base import Signal

from .iak_fakes import CONTENT, FakePage, FakeSolver, no_wander

URL = "https://www.example.com/find/?q=matrix"
TOKEN_HOST = "https://a1b2c3d4e5f6.us-east-1.token.awswaf.com/a1b2c3d4e5f6/9f8e7d6c5b4a"
CAPTCHA_HOST = "https://a1b2c3d4e5f6.us-east-1.captcha.awswaf.com/a1b2c3d4e5f6/9f8e7d6c5b4a"
GOKU = {"key": "AQIDAHjcYu/GjX+QlghicBgQ/7bFaQZ+m5FKCMDnO+vTbNg96AE", "iv": "CgAHbCe2GgAAAAAA", "context": "Q2tJ+ctx=="}
CHALLENGE = (
    f"<!DOCTYPE html><html><head><script>window.awsWafCookieDomainList = [];"
    f"window.gokuProps = {json.dumps(GOKU)};</script>"
    f'<script src="{TOKEN_HOST}/challenge.js"></script></head>'
    '<body><div id="challenge-container"></div><script>AwsWafIntegration.saveReferrer();'
    "AwsWafIntegration.checkForceRefresh().then(() => AwsWafIntegration.forceRefreshToken()).then(() =>"
    " window.location.reload(true));</script></body></html>"
)
CAPTCHA = (
    f"<!DOCTYPE html><html><head><title>Human Verification</title><script>window.gokuProps = {json.dumps(GOKU)};</script>"
    f'<script src="{TOKEN_HOST}/challenge.js"></script><script src="{CAPTCHA_HOST}/captcha.js"></script></head>'
    '<body><div id="captcha-container"></div><script>AwsWafCaptcha.renderCaptcha(document.getElementById('
    '"captcha-container"), {onSuccess: () => window.location.reload(true), dynamicWidth: true});</script></body></html>'
)


@pytest.fixture(autouse=True)
def fast(monkeypatch):
    monkeypatch.setattr(solver_module, "wander", no_wander)
    monkeypatch.setattr(solver_module, "RELOAD_AFTER", 0.3)
    monkeypatch.setattr(solver_module, "RESULT_WAIT", 1.0)


def detect(html: str, status: int, action: str = ""):
    headers = {"x-amzn-waf-action": action} if action else {}
    return AwsWafHandler().detect(Signal(url=URL, status=status, headers=headers, html=html))


async def solve(page: FakePage, det, timeout: float = 5.0, solver=None):
    start = monotonic()
    result = await AwsWafHandler().solve(page, det, deadline=start + timeout, solver=solver, log=None)
    return result, monotonic() - start


class TestHelpers:
    def test_scripts_on_both_hosts(self):
        assert aws_scripts(CAPTCHA) == {"challenge": f"{TOKEN_HOST}/challenge.js", "captcha": f"{CAPTCHA_HOST}/captcha.js"}

    def test_problem_question_and_images(self):
        image = base64.b64encode(b"\x89PNG tile").decode()
        problem = {"problem_type": "HumanCaptchaGridProblem", "assets": {"images": json.dumps([image] * 9), "target": '"bed"'}}
        assert problem_question(problem) == "aws:grid:bed"
        assert problem_images(problem) == [b"\x89PNG tile"] * 9
        assert problem_question({"problem_type": "toycarcity", "assets": {}}) == "aws:toycarcity:carcity"
        assert problem_question({"problem_type": "audio", "assets": {}}) is None


class TestChallenge:
    @pytest.mark.asyncio
    async def test_clears_when_challenge_js_stores_the_token_and_reloads(self):
        page = FakePage(URL, CHALLENGE)
        page.at(0.3, lambda p: p.context.store.update({"aws-waf-token": "tok-1"}))
        page.at(0.5, lambda p: p.navigate(CONTENT))
        result, elapsed = await solve(page, detect(CHALLENGE, 202, "challenge"))
        assert result.solved and result.reason == "solved"
        assert result.cookies == ["aws-waf-token"] and page.reloads == 0 and elapsed < 3

    @pytest.mark.asyncio
    async def test_reloads_once_when_the_token_is_set_but_the_page_stays(self):
        page = FakePage(URL, CHALLENGE)
        page.context.store["aws-waf-token"] = "stale"
        page.at(0.2, lambda p: p.context.store.update({"aws-waf-token": "fresh"}))
        page.on_reload = lambda p: p.navigate(CONTENT)
        result, _ = await solve(page, detect(CHALLENGE, 202, "challenge"))
        assert result.solved and page.reloads == 1

    @pytest.mark.asyncio
    async def test_a_stale_token_alone_does_not_trigger_a_reload(self):
        page = FakePage(URL, CHALLENGE)
        page.context.store["aws-waf-token"] = "stale"
        result, elapsed = await solve(page, detect(CHALLENGE, 202, "challenge"), timeout=1.2)
        assert not result.solved and page.reloads == 0 and elapsed < 1.7

    @pytest.mark.asyncio
    async def test_a_header_only_detection_needs_a_new_document(self):
        """Until a new document arrives the page is still the 202 challenge it was detected as, whatever its DOM."""
        page = FakePage(URL, CONTENT)
        page.context.store["aws-waf-token"] = "tok"
        result, elapsed = await solve(page, detect(CONTENT, 202, "challenge"), timeout=1.2)
        assert not result.solved and result.reason == "timeout" and elapsed < 1.7
        page = FakePage(URL, CONTENT)
        page.at(0.3, lambda p: p.navigate(CONTENT))
        result, _ = await solve(page, detect(CONTENT, 202, "challenge"))
        assert result.solved

    @pytest.mark.asyncio
    async def test_an_unchanged_token_status_page_is_a_block(self, monkeypatch):
        monkeypatch.setattr(solver_module, "TOKEN_STATUS_PATIENCE", 0.6)
        gate = "<html><body><h1>Forbidden</h1></body></html>"
        det = AwsWafHandler().detect(Signal(url=URL, status=403, cookies={"aws-waf-token": "tok"}, html=gate))
        assert det is not None and det.rule == "aws.token_status"
        page = FakePage(URL, gate)
        page.context.store["aws-waf-token"] = "tok"
        result, elapsed = await solve(page, det)
        assert (result.solved, result.reason) == (False, "blocked") and elapsed < 2.0

    @pytest.mark.asyncio
    async def test_escalation_to_captcha_without_a_solver(self):
        page = FakePage(URL, CHALLENGE)
        page.at(0.2, lambda p: p.navigate(CAPTCHA, 405, {"x-amzn-waf-action": "captcha"}))
        result, _ = await solve(page, detect(CHALLENGE, 202, "challenge"))
        assert not result.solved and result.reason == "captcha_required"
        assert result.solver_kind == "awswaf"


class TestCaptcha:
    @pytest.mark.asyncio
    async def test_without_a_solver_it_reports_captcha_required_at_once(self):
        page = FakePage(URL, CAPTCHA)
        result, elapsed = await solve(page, detect(CAPTCHA, 405, "captcha"))
        assert (result.solved, result.reason) == (False, "captcha_required") and elapsed < 0.5

    @pytest.mark.asyncio
    async def test_token_solver_sets_the_cookie_and_reloads(self):
        page = FakePage(URL, CAPTCHA)
        page.on_reload = lambda p: p.navigate(CONTENT) if p.context.store.get("aws-waf-token") == "solved" else None
        solver = FakeSolver(("awswaf",), token="solved")
        result, _ = await solve(page, detect(CAPTCHA, 405, "captcha"), solver=solver)
        assert result.solved and result.reason == "solved:awswaf"
        assert result.used_solver == "fakeprov"
        kind, sitekey, page_url, extra = solver.calls[0]
        # The provider is told the page's host and path, never its query string.
        assert (kind, sitekey, page_url) == ("awswaf", GOKU["key"], "https://www.example.com/find/")
        assert extra["aws_iv"] == GOKU["iv"] and extra["aws_context"] == GOKU["context"]
        assert extra["aws_challenge_script"] == f"{TOKEN_HOST}/challenge.js"
        assert extra["aws_captcha_script"] == f"{CAPTCHA_HOST}/captcha.js"
        cookie = page.context.added[0]
        assert (cookie["name"], cookie["url"], cookie["secure"]) == ("aws-waf-token", "https://www.example.com/", True)

    @pytest.mark.asyncio
    async def test_voucher_is_exchanged_at_the_token_host(self):
        page = FakePage(URL, CAPTCHA)
        page.evaluate_result = lambda js, arg: "exchanged" if arg[0] == f"{TOKEN_HOST}/voucher" else None
        page.on_reload = lambda p: p.navigate(CONTENT) if p.context.store.get("aws-waf-token") == "exchanged" else None
        solver = FakeSolver(("awswaf_voucher",), token="voucher-1", existing_token="old")
        result, _ = await solve(page, detect(CAPTCHA, 405, "captcha"), solver=solver)
        assert result.solved and result.reason == "solved:awswaf_voucher"
        assert page.evaluations[0][1] == [f"{TOKEN_HOST}/voucher", "voucher-1", "old"]

    @pytest.mark.asyncio
    async def test_a_rejected_token_falls_through_to_the_next_kind(self):
        page = FakePage(URL, CAPTCHA)
        page.evaluate_result = lambda js, arg: "exchanged"
        page.on_reload = lambda p: p.navigate(CONTENT) if p.context.store.get("aws-waf-token") == "exchanged" else None
        solver = FakeSolver(("awswaf", "awswaf_voucher"), token="bad")
        result, _ = await solve(page, detect(CAPTCHA, 405, "captcha"), timeout=20, solver=solver)
        assert result.solved and [c[0] for c in solver.calls] == ["awswaf", "awswaf_voucher"]

    @pytest.mark.asyncio
    async def test_unsupported_kinds_are_reported(self):
        page = FakePage(URL, CAPTCHA)
        result, _ = await solve(page, detect(CAPTCHA, 405, "captcha"), solver=FakeSolver(("turnstile",)))
        assert result.reason == "captcha_required:no_solver_kind"
