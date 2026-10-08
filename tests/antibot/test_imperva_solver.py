"""Imperva: the in-page solver against scripted pages (reese84 interstitial, ``___utmvc``, incident + hCaptcha)."""

from time import monotonic

import pytest

from scrapling.engines.antibot import _imperva_solver as solver_module
from scrapling.engines.antibot.base import Signal
from scrapling.engines.antibot.imperva import ImpervaHandler

from .iak_fakes import CONTENT, FakeFrame, FakePage, FakeResponse, FakeSolver, no_wander

URL = "https://www.example.com/uk/en-gb/toys/c/SM0601"
LOADER = '<script src="/_Incapsula_Resource?SWJIYLWA=719d34d31c8e3a6e6fffd425f7e032f3"></script>'
INTERSTITIAL = (
    f"<!doctype html><html><head><title>Pardon Our Interruption</title>{LOADER}"
    "<script>window.reeseSkipExpirationCheck = true;</script></head>"
    '<body><div id="interstitial-inprogress"><h1>Pardon Our Interruption</h1>'
    "<p>As you were browsing something about your browser made us think you were a bot.</p></div></body></html>"
)
UTMVC = f"<html><head>{LOADER}</head><body><script>/* sets ___utmvc, then reloads */</script></body></html>"
INCIDENT = (
    f'<html style="height:100%"><head><meta name="ROBOTS" content="NOINDEX, NOFOLLOW">{LOADER}</head>'
    '<body style="margin:0px;height:100%"><iframe id="main-iframe" src="/_Incapsula_Resource?SWUDNSAI=31&amp;xinfo=8-1&amp;'
    'incident_id=1687-1068&amp;edet=12&amp;cinfo=0e00&amp;rpinfo=0&amp;mth=GET" frameborder=0 width="100%" height="100%">'
    "Request unsuccessful. Incapsula incident ID: 1687-1068</iframe></body></html>"
)
INCIDENT_FRAME_URL = "https://www.example.com/_Incapsula_Resource?SWUDNSAI=31&xinfo=8-1&incident_id=1687-1068&edet=12"
SITEKEY = "a5f74b19-9e45-40e0-b45d-47ff91b7a6c2"
POST_PATH = "/_Incapsula_Resource?SWCGHOEL=v2&dai=1068&cts=XlV9lAHtmM6i"
INCIDENT_FRAME_HTML = (
    f'<html><body><div class="h-captcha" data-sitekey="{SITEKEY}" data-callback="onCaptchaFinished"></div>'
    '<script>function onCaptchaFinished(token) { var xhr = new XMLHttpRequest();'
    f' xhr.open("POST", "{POST_PATH}", true); xhr.send("g-recaptcha-response=" + token); }}</script></body></html>'
)
GEETEST_FRAME_HTML = (
    '<html><body><div id="captcha"></div><script>/* initGeetest({gt: "...", challenge: "...", product: "float"}) */'
    "</script></body></html>"
)
CHECKBOX_URL = (
    "https://newassets.hcaptcha.com/captcha/v1/7b6ab9f/static/hcaptcha.html"
    f"#frame=checkbox&id=0xyz&host=www.example.com&sitekey={SITEKEY}&theme=light"
)


@pytest.fixture(autouse=True)
def fast(monkeypatch):
    monkeypatch.setattr(solver_module, "wander", no_wander)
    monkeypatch.setattr(solver_module, "RELOAD_AFTER", 0.3)
    monkeypatch.setattr(solver_module, "WIDGET_WAIT", 1.5)
    monkeypatch.setattr(solver_module, "CLICK_RESULT_WAIT", 1.0)


def detect(html: str, status: int = 200, frames=(), headers=None):
    return ImpervaHandler().detect(Signal(url=URL, status=status, headers=headers or {}, html=html, frame_urls=list(frames)))


async def solve(page: FakePage, det, timeout: float = 5.0, solver=None):
    start = monotonic()
    result = await ImpervaHandler().solve(page, det, deadline=start + timeout, solver=solver, log=None)
    return result, monotonic() - start


class TestDetection:
    def test_rules(self):
        assert detect(INTERSTITIAL).rule == "imperva.interstitial"
        assert detect(UTMVC).rule == "imperva.utmvc"
        found = detect(INCIDENT)
        assert (found.kind, found.rule, found.details["edet"]) == ("captcha", "imperva.incident", "12")
        assert detect(INCIDENT, frames=[INCIDENT_FRAME_URL, CHECKBOX_URL]).details["widget"] == "hcaptcha"

    def test_content_pages_with_the_loader_are_not_detected(self):
        assert detect(CONTENT.replace("</head>", LOADER + "</head>")) is None
        assert detect(CONTENT, headers={"x-iinfo": "8-1", "x-cdn": "Imperva"}) is None

    def test_datadome_behind_imperva_edge_is_not_imperva(self):
        dd = "<html><body><script>var dd={'rt':'i','cid':'x','host':'geo.captcha-delivery.com'}</script></body></html>"
        assert detect(dd, status=403, headers={"x-iinfo": "8-1", "x-cdn": "Imperva"}) is None


class TestSensor:
    @pytest.mark.asyncio
    async def test_interstitial_clears_when_the_sensor_reloads(self):
        page = FakePage(URL, INTERSTITIAL)
        page.context.store.update({"incap_ses_605_2483049": "s", "visid_incap_2483049": "v"})
        page.at(0.3, lambda p: p.context.store.update(reese84="3:tok"))
        page.at(0.5, lambda p: p.navigate(CONTENT))
        result, elapsed = await solve(page, detect(INTERSTITIAL))
        assert result.solved and result.reason == "solved"
        assert result.cookies == ["incap_ses_605_2483049", "reese84", "visid_incap_2483049"]
        assert page.reloads == 0 and elapsed < 3

    @pytest.mark.asyncio
    async def test_reloads_once_when_the_cookie_changed_without_a_reload(self):
        page = FakePage(URL, UTMVC)
        page.at(0.2, lambda p: p.context.store.update(___utmvc="abc"))
        page.on_reload = lambda p: p.navigate(CONTENT)
        result, _ = await solve(page, detect(UTMVC))
        assert result.solved and page.reloads == 1
        assert "___utmvc" in result.cookies

    @pytest.mark.asyncio
    async def test_an_empty_document_mid_reload_is_not_success(self):
        page = FakePage(URL, INTERSTITIAL)
        page.at(0.2, lambda p: p.navigate("<html><head></head><body></body></html>"))
        result, elapsed = await solve(page, detect(INTERSTITIAL), timeout=1.5)
        assert not result.solved and result.reason == "timeout"
        assert elapsed < 1.5 + 0.5

    @pytest.mark.asyncio
    async def test_never_runs_past_the_deadline(self):
        page = FakePage(URL, INTERSTITIAL)
        result, elapsed = await solve(page, detect(INTERSTITIAL), timeout=1.2)
        assert not result.solved
        assert elapsed < 1.2 + 0.5

    @pytest.mark.asyncio
    async def test_records_renew_in_sec_from_the_token_response(self):
        page = FakePage(URL, INTERSTITIAL)
        body = {"token": "3:tok", "renewInSec": 896, "cookieDomain": "www.example.com"}
        page.at(0.2, lambda p: p.emit(FakeResponse(URL + "?d=www.example.com", resource_type="xhr", method="POST", json_body=body)))
        page.at(0.4, lambda p: p.navigate(CONTENT))
        det = detect(INTERSTITIAL)
        result, _ = await solve(page, det)
        assert result.solved and det.details["renew_in_sec"] == 896

    @pytest.mark.asyncio
    async def test_escalation_to_a_widgetless_incident_page_is_reported(self):
        page = FakePage(URL, INTERSTITIAL)
        page.at(0.2, lambda p: p.navigate(INCIDENT))
        det = detect(INTERSTITIAL)
        result, _ = await solve(page, det)
        assert not result.solved
        assert result.reason == "blocked:no_widget"
        assert det.details["escalated"] == "unknown" and det.details["widget"] == "none"


def incident_page(evaluate=200):
    page = FakePage(URL, INCIDENT)
    incident = FakeFrame(INCIDENT_FRAME_URL, INCIDENT_FRAME_HTML, evaluate=evaluate)
    checkbox = FakeFrame(CHECKBOX_URL, "", box={"x": 400.0, "y": 300.0, "width": 302.0, "height": 76.0})
    page.child_frames = [incident, checkbox]
    return page, incident


class TestIncident:
    @pytest.mark.asyncio
    async def test_clicks_the_checkbox_once_then_needs_a_captcha_solver(self):
        page, incident = incident_page()
        result, _ = await solve(page, detect(INCIDENT, frames=[f.url for f in page.child_frames]))
        assert not result.solved and result.reason == "captcha_required:hcaptcha"
        assert result.solver_kind == "hcaptcha"
        assert len(page.mouse.downs) == 1 and page.mouse.ups == 1
        x, y = page.mouse.downs[0]
        assert 400 + 27 <= x <= 400 + 33 and 300 + 33 <= y <= 300 + 39
        assert incident.evaluations == []

    @pytest.mark.asyncio
    async def test_a_click_that_passes_clears_the_page(self):
        page, _ = incident_page()
        original_up = page.mouse.up

        async def up(**kwargs):
            await original_up(**kwargs)
            page.navigate(CONTENT)

        page.mouse.up = up
        result, _ = await solve(page, detect(INCIDENT))
        assert result.solved and result.reason == "solved:checkbox"

    @pytest.mark.asyncio
    async def test_solver_token_is_posted_to_imperva_and_the_page_reloaded(self):
        page, incident = incident_page()
        page.on_reload = lambda p: (p.context.store.update(incap_sh_2483049="sh"), p.navigate(CONTENT))
        solver = FakeSolver(("hcaptcha",), token="P1_hcaptcha_token")
        result, _ = await solve(page, detect(INCIDENT), timeout=8, solver=solver)
        assert result.solved and result.reason == "solved:hcaptcha_token"
        assert result.used_solver == "fakeprov" and "incap_sh_2483049" in result.cookies
        kind, sitekey, page_url, extra = solver.calls[0]
        assert (kind, sitekey, page_url) == ("hcaptcha", SITEKEY, URL)
        assert extra["deadline"] < monotonic() + 8
        assert incident.evaluations[0][1] == [POST_PATH, "P1_hcaptcha_token"]
        assert page.reloads == 1

    @pytest.mark.asyncio
    async def test_a_rejected_token_post_is_reported(self):
        page, _ = incident_page(evaluate=403)
        result, _ = await solve(page, detect(INCIDENT), timeout=8, solver=FakeSolver(("hcaptcha",)))
        assert not result.solved and result.reason == "captcha_required:hcaptcha:post_failed"
        assert result.used_solver == "fakeprov" and page.reloads == 0

    @pytest.mark.asyncio
    async def test_a_solver_without_hcaptcha_is_not_called(self):
        page, _ = incident_page()
        solver = FakeSolver(("turnstile",))
        result, _ = await solve(page, detect(INCIDENT), solver=solver)
        assert result.reason == "captcha_required:hcaptcha" and solver.calls == []

    @pytest.mark.asyncio
    async def test_geetest_without_a_rendered_button_is_reported_without_a_click(self):
        page = FakePage(URL, INCIDENT)
        page.child_frames = [FakeFrame(INCIDENT_FRAME_URL, GEETEST_FRAME_HTML)]
        result, _ = await solve(page, detect(INCIDENT), solver=FakeSolver(("geetest_v3", "geetest_v4")))
        assert result.reason == "captcha_required:geetest" and page.mouse.downs == []
        assert result.solver_kind is None  # no solver route for Imperva's GeeTest

    @pytest.mark.asyncio
    async def test_geetest_click_to_verify_gets_one_click(self):
        page = FakePage(URL, INCIDENT)
        frame = FakeFrame(INCIDENT_FRAME_URL, GEETEST_FRAME_HTML)
        frame.locator_box = {"x": 500.0, "y": 200.0, "width": 300.0, "height": 44.0}
        page.child_frames = [frame]
        original_up = page.mouse.up

        async def up(**kwargs):
            await original_up(**kwargs)
            page.navigate(CONTENT)

        page.mouse.up = up
        result, _ = await solve(page, detect(INCIDENT))
        assert result.solved and result.reason == "solved:checkbox"
        x, y = page.mouse.downs[0]
        assert 500 + 147 <= x <= 500 + 153 and 200 + 19 <= y <= 200 + 25


BLOCK = (
    "<html><head><title>Access denied</title><style>" + "body{margin:0;padding:0}" * 300 + "</style></head>"
    "<body><h1>Access denied</h1><p>Error 15. This request was blocked by our security service. "
    "Incapsula incident ID: 123000450123456789-12345</p></body></html>"
)


class TestBlock:
    """A block page has no sensor that clears it in place: an unchanged one is never reported solved."""

    @pytest.mark.asyncio
    async def test_an_unchanged_block_page_is_blocked(self, monkeypatch):
        monkeypatch.setattr(solver_module, "BLOCK_PATIENCE", 1.0)
        det = detect(BLOCK, status=403, headers={"x-iinfo": "1-2-3", "x-cdn": "Imperva"})
        assert det is not None and (det.kind, det.rule) == ("block", "imperva.block")
        page = FakePage(URL, BLOCK)
        result, elapsed = await solve(page, det)
        assert (result.solved, result.reason) == (False, "blocked") and elapsed < 2.5
        assert result.solver_kind is None

    @pytest.mark.asyncio
    async def test_a_block_whose_status_is_unknown_still_needs_a_new_document(self, monkeypatch):
        """Without the detected status the page reads clean; only a reload into content counts."""
        monkeypatch.setattr(solver_module, "BLOCK_PATIENCE", 1.0)
        det = detect(BLOCK, status=403)
        det.signal = None  # a caller-built detection: the re-check has no status to go on
        result, _ = await solve(FakePage(URL, BLOCK), det)
        assert (result.solved, result.reason) == (False, "blocked")

    @pytest.mark.asyncio
    async def test_a_block_that_reloads_into_content_is_solved(self, monkeypatch):
        monkeypatch.setattr(solver_module, "BLOCK_PATIENCE", 3.0)
        page = FakePage(URL, BLOCK)
        page.at(0.3, lambda p: p.navigate(CONTENT))
        result, _ = await solve(page, detect(BLOCK, status=403))
        assert (result.solved, result.reason) == (True, "solved")
