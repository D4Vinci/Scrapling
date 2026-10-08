"""Kasada: the in-page waiter against scripted pages (429 bootstrap page, /tl tokens, cookie mirror)."""

from time import monotonic

import pytest

from scrapling.engines.antibot import _kasada_solver as solver_module
from scrapling.engines.antibot._kasada_solver import kasada_tokens, unwatch_kasada, watch_kasada
from scrapling.engines.antibot.base import Signal
from scrapling.engines.antibot.kasada import KasadaHandler

from .iak_fakes import CONTENT, FakePage, FakeResponse, no_wander

URL = "https://www.example.com/explore-hotels"
SCRIPT = "/149e9513-01fa-4fb0-aad4-566afd725d1b/2d206a39-8ed7-437e-a3be-862e0f06eea3"
BLOCK = (
    "<!DOCTYPE html><html><head></head><body><script>window.KPSDK={};KPSDK.now=typeof performance!=='undefined'"
    "&&performance.now?performance.now.bind(performance):Date.now.bind(Date);KPSDK.start=KPSDK.now();</script>"
    f'<script src="{SCRIPT}/ips.js?tkrm_alpekz_s1.3=0Zhprgz&amp;x-kpsdk-im=AAIHh6y"></script></body></html>'
)
TL = f"https://www.example.com{SCRIPT}/tl"


@pytest.fixture(autouse=True)
def fast(monkeypatch):
    monkeypatch.setattr(solver_module, "wander", no_wander)
    monkeypatch.setattr(solver_module, "RELOAD_AFTER", 0.3)
    monkeypatch.setattr(solver_module, "SETTLE", 0.3)


def detect(html: str = BLOCK, status: int = 429):
    return KasadaHandler().detect(Signal(url=URL, status=status, headers={"x-kpsdk-ct": "0init", "x-kpsdk-r": "1-B"}, html=html))


async def solve(page: FakePage, det, timeout: float = 5.0):
    start = monotonic()
    result = await KasadaHandler().solve(page, det, deadline=start + timeout, solver=None, log=None)
    return result, monotonic() - start


def tl_answer(page: FakePage, ct: str = "02Rrkf95YyBb", st: str = "1759149934586") -> None:
    page.context.store.update({"tkrm_alpekz_s1.3": ct, "tkrm_alpekz_s1.3-ssn": ct})
    page.emit(FakeResponse(TL, 200, {"x-kpsdk-ct": ct, "x-kpsdk-st": st}, resource_type="fetch", method="POST"))


class TestKasada:
    @pytest.mark.asyncio
    async def test_waits_for_the_sdk_reload_and_keeps_ct_and_st(self):
        page = FakePage(URL, BLOCK)
        page.at(0.3, tl_answer)
        page.at(0.5, lambda p: p.navigate(CONTENT, 200, {"x-kpsdk-ct": "03latest"}))
        det = detect()
        result, elapsed = await solve(page, det)
        assert result.solved and result.reason == "solved" and elapsed < 3
        assert result.cookies == ["tkrm_alpekz_s1.3", "tkrm_alpekz_s1.3-ssn"]
        tokens = kasada_tokens(page)
        assert tokens["ct"] == "03latest" and tokens["st"] == 1759149934586 and tokens["ct_source"] == "header"
        assert det.details["tokens"] == {"ct": True, "ct_source": "header", "st": 1759149934586}
        assert page.listeners.get("response") == []
        assert page.reloads == 0

    @pytest.mark.asyncio
    async def test_reloads_once_when_the_token_arrived_but_the_page_stayed(self):
        page = FakePage(URL, BLOCK)
        page.at(0.2, tl_answer)
        page.on_reload = lambda p: p.navigate(CONTENT)
        result, _ = await solve(page, detect())
        assert result.solved and page.reloads == 1

    @pytest.mark.asyncio
    async def test_falls_back_to_the_cookie_mirror_when_tl_was_missed(self):
        page = FakePage(URL, BLOCK)
        page.at(0.2, lambda p: (p.context.store.update(KP_UIDz="0kpuid", **{"KP_UIDz-ssn": "0kpuid"}), p.navigate(CONTENT)))
        result, _ = await solve(page, detect())
        assert result.solved
        tokens = kasada_tokens(page)
        assert tokens["ct"] == "0kpuid" and tokens["ct_source"] == "cookie:KP_UIDz" and tokens["st"] is None

    @pytest.mark.asyncio
    async def test_a_watcher_attached_before_navigation_catches_the_first_tl(self):
        page = FakePage(URL, BLOCK)
        watch_kasada(page)
        tl_answer(page, ct="0early", st="1700000000000")  # before solve() is called
        page.at(0.1, lambda p: p.navigate(CONTENT))
        result, _ = await solve(page, detect())
        assert result.solved and kasada_tokens(page)["st"] == 1700000000000
        assert len(page.listeners["response"]) == 1, "a caller's watcher stays attached until it unwatches"
        unwatch_kasada(page)
        assert page.listeners["response"] == []

    @pytest.mark.asyncio
    async def test_never_runs_past_the_deadline(self):
        page = FakePage(URL, BLOCK)
        result, elapsed = await solve(page, detect(), timeout=1.2)
        assert not result.solved and result.reason == "timeout"
        assert elapsed < 1.2 + 0.5 and page.reloads == 0

    @pytest.mark.asyncio
    async def test_never_blocks_or_routes_requests(self):
        """The waiter only listens: no route handlers, no init scripts, no evaluations in the page."""
        page = FakePage(URL, BLOCK)
        page.at(0.2, lambda p: p.navigate(CONTENT))
        result, _ = await solve(page, detect())
        assert result.solved and page.evaluations == [] and set(page.listeners) == {"response"}
