"""Akamai: the ported Hyper SDK helpers, and the in-page solver against a local stand-in site."""

import base64
import hashlib
import json
import logging
import random
from time import monotonic

import pytest

from scrapling.engines.antibot import _akamai_solver as solver_module
from scrapling.engines.antibot._akamai_solver import (
    SecCptChallenge,
    SecCptChallengeData,
    is_cookie_invalidated,
    is_cookie_valid,
    json_document,
    parse_sbsd,
    parse_script_path,
    sec_cpt_from_page,
    solve_sec_cpt_answers,
)
from scrapling.engines.antibot.akamai import AkamaiHandler
from scrapling.engines.antibot.base import page_signal

from .pxak_server import FixtureServer, browser_page, fixture, hyper_pow_ok

log = logging.getLogger("tests.antibot.akamai")

CHALLENGE = {
    "token": "AAQAAAAJ____9z",
    "timestamp": 1759900000,
    "nonce": "0f7c9e91cbd8ab5f6008",
    "difficulty": 2000,
    "count": 3,
}


def interstitial(provider: str = "crypto", duration: int = 5) -> str:
    encoded = base64.b64encode(json.dumps(CHALLENGE).encode()).decode()
    return fixture("akamai_sec_cpt.html", PROVIDER=provider, CHALLENGE=encoded, DURATION=duration, SELF="")


class TestStopSignal:
    @pytest.mark.parametrize(
        "cookie, posts, valid",
        [
            ("A1B2~0~YAAQ~-1~-1~-1", 0, True),
            ("A1B2~-1~YAAQ~-1~-1~-1", 5, False),
            ("A1B2~3~YAAQ~-1~-1~-1", 2, False),
            ("A1B2~3~YAAQ~-1~-1~-1", 3, True),
            ("A1B2~x~YAAQ", 9, False),
            ("garbage", 9, False),
        ],
    )
    def test_is_cookie_valid(self, cookie, posts, valid):
        assert is_cookie_valid(cookie, posts) is valid

    @pytest.mark.parametrize(
        "cookie, invalidated",
        [("A1B2~0~YAAQ~-1~-1~-1", False), ("A1B2~0~YAAQ~0~-1~-1", True), ("A1B2~0~YAAQ", False), ("A~0~Y~z", False)],
    )
    def test_is_cookie_invalidated(self, cookie, invalidated):
        assert is_cookie_invalidated(cookie) is invalidated


class TestSecCpt:
    def test_parse_interstitial(self):
        challenge = SecCptChallenge.parse(interstitial("crypto", 5))
        assert challenge.provider == "crypto"
        assert challenge.duration == 5
        assert challenge.challenge_path == "/_sec/cp_challenge/ak-challenge-4-3.htm"
        assert challenge.challenge_data == SecCptChallengeData(**CHALLENGE)

    def test_parse_json_keeps_count_and_behavioural_fields(self):
        payload = dict(
            CHALLENGE,
            provider="adaptive",
            chlg_duration=30,
            branding_cust_url="/challenge-assets/v7/captcha.html",
            verify_url="abc/def",
            **{"sec-cp-challenge": "true"},
        )
        challenge = SecCptChallenge.parse_from_json(json.dumps(payload))
        assert challenge.challenge_data is not None and challenge.challenge_data.count == 3
        assert (challenge.provider, challenge.duration) == ("adaptive", 30)
        assert challenge.branding_url == "/challenge-assets/v7/captcha.html"
        assert challenge.verify_url == "abc/def"

    def test_parse_json_behavioural_has_no_proof_of_work(self):
        challenge = SecCptChallenge.parse_from_json(
            {"sec-cp-challenge": "true", "provider": "behavioral", "verify_url": "x/y"}
        )
        assert challenge.challenge_data is None and challenge.provider == "behavioral"

    def test_parse_rejects_pages_without_a_challenge(self):
        with pytest.raises(ValueError):
            SecCptChallenge.parse("<html><body>hello</body></html>")
        with pytest.raises(ValueError):
            SecCptChallenge.parse('<iframe challenge="not base64!" data-duration=5 src="/x"></iframe>')

    def test_answers_pass_akamais_check(self):
        sec = "9F3E1C0A77B2D4E6"
        answers = solve_sec_cpt_answers(sec, SecCptChallengeData(**CHALLENGE))
        assert len(answers) == 3 and all(a.startswith("0.") for a in answers)
        assert hyper_pow_ok(sec, CHALLENGE, answers)
        # The difficulty rises after each answer, so the same answers do not pass at a constant difficulty.
        assert not hyper_pow_ok(sec, dict(CHALLENGE, difficulty=CHALLENGE["difficulty"] + 1), answers)

    def test_payload(self):
        challenge = SecCptChallenge.parse(interstitial())
        payload = json.loads(challenge.generate_sec_cpt_payload("9F3E1C0A77B2D4E6~1~abc~-1"))
        assert payload["token"] == CHALLENGE["token"]
        assert hyper_pow_ok("9F3E1C0A77B2D4E6", CHALLENGE, payload["answers"])
        with pytest.raises(ValueError):
            challenge.generate_sec_cpt_payload("no-separator")

    def test_proof_of_work_stops_at_the_deadline(self):
        hard = SecCptChallengeData(token="t", timestamp=1, nonce="n", difficulty=10**12, count=1)
        start = monotonic()
        with pytest.raises(TimeoutError):
            solve_sec_cpt_answers("S", hard, deadline=start + 0.2)
        assert monotonic() - start < 2

    def test_challenge_from_page_reads_both_forms(self):
        assert sec_cpt_from_page(interstitial()).challenge_data is not None
        document = (
            '<html><head></head><body><pre>{"sec-cp-challenge":"true","provider":"crypto","chlg_duration":2,'
            '"token":"t","timestamp":1,"nonce":"n","difficulty":10,"count":1}</pre></body></html>'
        )
        challenge = sec_cpt_from_page(document)
        assert challenge is not None and challenge.duration == 2 and challenge.challenge_data.difficulty == 10
        assert sec_cpt_from_page("<html><body>plain</body></html>") is None


class TestParsers:
    def test_script_path(self):
        assert parse_script_path(fixture("akamai_root.html")) == "/x5Kq/Ab1/cd2/EfG3/sensor"
        assert parse_script_path("<script src='/app.js'></script>") is None

    def test_sbsd(self):
        assert parse_sbsd(fixture("akamai_sbsd.html")) == {
            "path": "/Gq7p/Rf/k2/sbsd",
            "v": "99b02ce6-f91f-0f49-40ae-6f8493e30211",
            "t": "183446611",
        }
        passive = parse_sbsd('<script src="/a/b?v=99b02ce6-f91f-0f49-40ae-6f8493e30211"></script>')
        assert passive is not None and passive["t"] == ""

    def test_json_document(self):
        assert json_document('<html><body><pre>{"t":"1"}</pre></body></html>') == {"t": "1"}
        assert json_document("<html><body>nope</body></html>") is None


# ------------------------------------------------------------------------------------------------ in the browser


@pytest.fixture(scope="module")
def server():
    srv = FixtureServer()
    yield srv
    srv.close()


@pytest.fixture
def quick(monkeypatch):
    """Shorter self-clear waits, so the local-fallback paths run in test time."""
    monkeypatch.setattr(solver_module, "SEC_GRACE_POW", 1.5)
    monkeypatch.setattr(solver_module, "SEC_GRACE_SENSOR", 1.5)
    monkeypatch.setattr(solver_module, "SBSD_WAIT", (3.0, 2.0))
    monkeypatch.setattr(solver_module, "WARMUP_SENSOR_WAIT", 6.0)


async def _open(page, url):
    response = await page.goto(url)
    await page.wait_for_load_state("load")
    return await page_signal(page, status=response.status, headers=await response.all_headers())


async def _solve(page, det, budget=40.0, **kwargs):
    deadline = monotonic() + budget
    result = await AkamaiHandler().solve(page, det, deadline=deadline, solver=None, log=log, **kwargs)
    assert monotonic() <= deadline, "the solve ran past its deadline"
    return result


class TestInBrowser:
    @pytest.mark.asyncio
    async def test_sec_cpt_interstitial_that_clears_itself(self, server):
        server.reset(sec_self_solve=True, sec_duration=1)
        async with browser_page() as page:
            det = AkamaiHandler().detect(await _open(page, server.url("/sec/page")))
            assert det is not None and det.rule == "akamai.sec_cpt_html"
            result = await _solve(page, det)
            assert result.solved, result
            assert result.reason == "solved:sec_cpt"
            assert "sec_cpt" in result.cookies
            assert "Cordless drills" in await page.content()
            assert server.state.sec_verify_posts == []  # the page did it, no local proof of work

    @pytest.mark.asyncio
    async def test_stalled_sec_cpt_interstitial_is_solved_locally(self, server, quick):
        state = server.reset(sec_self_solve=False, sec_duration=2, sec_difficulty=3000, sec_count=2)
        async with browser_page() as page:
            det = AkamaiHandler().detect(await _open(page, server.url("/sec/page")))
            assert det is not None and det.rule == "akamai.sec_cpt_html"
            result = await _solve(page, det)
            assert result.solved, result
            assert result.reason == "solved:sec_cpt_pow"
            assert state.sec_verify_posts == [{"provider": "crypto", "answers": 2}]
            assert "Cordless drills" in await page.content()

    @pytest.mark.asyncio
    async def test_interstitial_reloading_into_itself_is_not_taken_for_cleared(self, server, quick):
        state = server.reset()
        async with browser_page() as page:
            det = AkamaiHandler().detect(await _open(page, server.url("/sec/loop")))
            assert det is not None and det.rule == "akamai.sec_cpt_html"
            result = await _solve(page, det, budget=25)
            assert not result.solved
            assert result.reason == "unsolved:akamai.sec_cpt_html"
            assert state.sec_verify_posts == []  # behavioural: no proof of work to post

    @pytest.mark.asyncio
    async def test_428_json_is_solved_locally_after_the_mandatory_wait(self, server):
        state = server.reset(sec_duration=2, sec_difficulty=2500, sec_count=1)
        async with browser_page() as page:
            det = AkamaiHandler().detect(await _open(page, server.url("/sec/api")))
            assert det is not None and det.rule == "akamai.sec_cpt"
            start = monotonic()
            result = await _solve(page, det)
            assert result.solved, result
            assert result.reason == "solved:sec_cpt_pow"
            assert monotonic() - start >= 2  # the server rejects answers posted before chlg_duration
            assert state.sec_verify_posts == [{"provider": "crypto", "answers": 1}]
            assert '"items"' in await page.content()

    @pytest.mark.asyncio
    async def test_sbsd_page_reloads_itself(self, server):
        state = server.reset(sbsd_delay_ms=600)
        async with browser_page() as page:
            det = AkamaiHandler().detect(await _open(page, server.url("/sbsd/page")))
            assert det is not None and det.rule == "akamai.sbsd_html"
            result = await _solve(page, det)
            assert result.solved, result
            assert result.reason == "solved:sbsd"
            assert state.sbsd_posts == 1 and "sbsd" in result.cookies
            assert "Cordless drills" in await page.content()

    @pytest.mark.asyncio
    async def test_sbsd_page_that_never_posts_is_retried_once_then_reported(self, server, quick):
        server.reset(sbsd_delay_ms=-1)
        async with browser_page() as page:
            det = AkamaiHandler().detect(await _open(page, server.url("/sbsd/page")))
            result = await _solve(page, det, budget=30)
            assert not result.solved
            assert result.reason == "unsolved:akamai.sbsd_html"
            gets = [p for m, p in server.state.paths if m == "GET" and p == "/sbsd/page"]
            assert len(gets) == 3  # the first load and one reload per attempt, no more

    @pytest.mark.asyncio
    async def test_passive_sbsd_block_page_posts_then_navigates_again(self, server, quick):
        state = server.reset()
        async with browser_page() as page:
            det = AkamaiHandler().detect(await _open(page, server.url("/sbsd/passive")))
            assert det is not None and det.rule == "akamai.sbsd_html"
            result = await _solve(page, det)
            assert result.solved, result
            assert result.reason == "solved:sbsd_passive"
            assert state.sbsd_posts == 2
            assert "Cordless drills" in await page.content()

    @pytest.mark.asyncio
    async def test_edge_block_clears_after_a_same_origin_warm_up(self, server, quick):
        state = server.reset(sensor_posts_needed=2)
        async with browser_page() as page:
            det = AkamaiHandler().detect(await _open(page, server.url("/strict/search")))
            assert det is not None and det.rule == "akamai.block"
            result = await _solve(page, det)
            assert result.solved, result
            assert result.reason == "solved:warmup"
            assert state.sensor_posts >= 2 and "_abck" in result.cookies
            assert page.url == server.url("/strict/search")
            assert "Cordless drills" in await page.content()
            # Only same-origin navigations: the root, then the target again.
            documents = [p for m, p in state.paths if m == "GET" and p in ("/", "/strict/search")]
            assert documents == ["/strict/search", "/", "/strict/search"]

    @pytest.mark.asyncio
    async def test_edge_block_with_blocked_root_stops_after_one_look(self, server, quick):
        state = server.reset(root_blocked=True)
        async with browser_page() as page:
            det = AkamaiHandler().detect(await _open(page, server.url("/strict/search")))
            start = monotonic()
            result = await _solve(page, det)
            assert (result.solved, result.reason) == (False, "unsolved:root_blocked")
            assert monotonic() - start < 10
            documents = [p for m, p in state.paths if m == "GET" and p in ("/", "/strict/search")]
            assert documents == ["/strict/search", "/"]

    @pytest.mark.asyncio
    async def test_no_time_to_navigate_is_never_reported_as_solved(self, server, quick):
        server.reset()
        async with browser_page() as page:
            det = AkamaiHandler().detect(await _open(page, server.url("/strict/search")))
            result = await _solve(page, det, budget=1.2)
            assert not result.solved

    @pytest.mark.asyncio
    async def test_tight_deadline_is_respected(self, server):
        server.reset(sec_self_solve=False, sec_duration=30)
        async with browser_page() as page:
            det = AkamaiHandler().detect(await _open(page, server.url("/sec/page")))
            result = await _solve(page, det, budget=6)
            assert not result.solved


def test_answers_hash_matches_hyper_reference_loop():
    """int.from_bytes(...) % d equals Hyper's byte-by-byte reduction for random inputs."""
    rng = random.Random(1)
    for _ in range(200):
        digest = hashlib.sha256(str(rng.random()).encode()).digest()
        d = rng.randint(2, 10**6)
        loop = 0
        for byte in digest:
            loop = ((loop << 8) | byte) % d
        assert loop == int.from_bytes(digest, "big") % d
