"""``solve_antibot`` and ``captcha_solver`` on the stealth sessions and fetcher.

The unit tests drive :func:`scrapling.engines.antibot.runner.solve_page` with fake handlers. The browser tests run
real headless sessions (sandbox on) against the local stand-in sites, in both the async session and the sync one,
whose pages reach the async handlers through the greenlet bridge. ``SCRAPLING_TEST_CHROME`` may point at a
Chromium-compatible executable; otherwise the driver's own browser is used.
"""

import json
import logging
import os
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from time import monotonic
from urllib.parse import parse_qs, urlsplit

import pytest

from scrapling.engines._browsers._validators import StealthConfig, validate
from scrapling.engines.antibot import _awswaf_solver, _imperva_solver, _kasada_solver, datadome, runner
from scrapling.engines.antibot._sync_bridge import AsyncView, _async_kind, unwrap, wrap
from scrapling.engines.antibot.base import Detection, Signal, SolveResult
from scrapling.engines.antibot.solvers import SolverRouter
from scrapling.fetchers import AsyncStealthySession, StealthyFetcher, StealthySession

from .dd_server import DataDomeFixture
from .iak_server import IakServer
from .solvers.mock_providers import MockProviders

log = logging.getLogger("tests.antibot.session")
CHROME = os.environ.get("SCRAPLING_TEST_CHROME") or None
LONG_TEXT = "<p>" + "A paragraph of catalogue text that a reader would see. " * 60 + "</p>"


def _session_kwargs(**extra):
    kwargs = dict(headless=True, google_search=False, timeout=25000, retries=1)
    if CHROME:
        kwargs["executable_path"] = CHROME
    kwargs.update(extra)
    return kwargs


# --------------------------------------------------------------------------------------------------- options


class TestOptions:
    def test_config_takes_a_solver_and_refuses_other_objects(self):
        router = SolverRouter([])
        config = validate({"solve_antibot": True, "captcha_solver": router}, StealthConfig)
        assert config.solve_antibot is True and config.captcha_solver is router
        with pytest.raises(TypeError, match="captcha_solver"):
            validate({"captcha_solver": "capmonster-key"}, StealthConfig)

    def test_defaults_are_off(self):
        config = validate({}, StealthConfig)
        assert config.solve_antibot is False and config.captcha_solver is None

    def test_headless_launch_is_hardened_only_at_launch(self):
        session = AsyncStealthySession(headless=True, solve_antibot=True)
        assert "--window-position=0,0" in session._browser_options["args"]  # what callers see and may edit
        launched = session._launch_options()["args"]
        assert "--window-position=0,0" not in launched and "--hide-scrollbars" not in launched
        assert any(a.startswith("--screen-info=") for a in launched)
        assert any(a.startswith("--window-size=") for a in launched)
        assert session._context_options.get("no_viewport") is True
        assert "viewport" not in session._context_options and "screen" not in session._context_options

    def test_launch_is_left_alone_without_antibot_or_when_headful(self):
        for kwargs in ({"headless": True}, {"headless": False, "solve_antibot": True}):
            session = StealthySession(**kwargs)
            assert session._launch_options()["args"] == session._browser_options["args"]
            assert session._context_options["viewport"] == {"width": 1920, "height": 1080}

    def test_an_explicit_viewport_is_kept(self):
        session = AsyncStealthySession(solve_antibot=True, additional_args={"viewport": {"width": 1280, "height": 800}})
        assert session._context_options["viewport"] == {"width": 1280, "height": 800}
        assert "no_viewport" not in session._context_options

    def test_deadline_leaves_room_for_the_response(self):
        assert runner.antibot_deadline(100.0, 30000) == pytest.approx(127.0)
        assert runner.antibot_deadline(100.0, 5000) == pytest.approx(104.0)
        assert runner.antibot_deadline(100.0, 60000) == pytest.approx(157.0)


# ------------------------------------------------------------------------------------------- the solve loop


class _Handler:
    def __init__(self, vendor, results, delay=0.0, error=None, after=None):
        self.vendor = vendor
        self.results = list(results)
        self.delay = delay
        self.error = error
        self.after = after
        self.calls = []

    def detect(self, s):  # pragma: no cover - detection is faked below
        return None

    async def solve(self, page, det, *, deadline, solver, log):
        import asyncio

        self.calls.append((det.rule, round(deadline - monotonic(), 1), solver))
        if self.delay:
            await asyncio.sleep(self.delay)
        if self.error:
            raise self.error
        if self.after:
            self.after()
        return self.results.pop(0)


class _Scope:
    name = "router"

    def __init__(self, attempts):
        self.attempts = attempts

    def summary(self):
        return {"solves": self.attempts, "attempts": self.attempts, "cost_usd": 0.001, "records": []}


class _Router:
    def __init__(self, attempts=1):
        self.scopes = []
        self.attempts = attempts

    def scope(self):
        self.scopes.append(_Scope(self.attempts))
        return self.scopes[-1]


@pytest.fixture
def fake_loop(monkeypatch):
    """Replaces page reads, detection and the registry; returns a function that sets them up."""

    def setup(detections, handlers, html="<html><body>" + LONG_TEXT + "</body></html>"):
        queue = list(detections)
        signals = []

        async def read_signal(page, *, status=None, headers=None, deadline):
            signals.append((status, dict(headers or {})))
            return Signal(url="https://shop.test/", status=status, headers=headers or {}, html=html)

        monkeypatch.setattr(runner, "read_signal", read_signal)
        monkeypatch.setattr(runner, "detect", lambda s: queue.pop(0) if queue else None)
        by_vendor = {h.vendor: h for h in handlers}
        monkeypatch.setattr(runner.registry, "get", lambda vendor: by_vendor.get(vendor))
        return signals

    return setup


class _Response:
    def __init__(self, status, headers):
        self.status = status
        self.headers = headers

    async def all_headers(self):
        return dict(self.headers)


def _det(vendor, kind="challenge", rule=None):
    return Detection(vendor=vendor, kind=kind, rule=rule or f"{vendor}.rule")


class TestSolveLoop:
    @pytest.mark.asyncio
    async def test_nothing_detected(self, fake_loop):
        fake_loop([], [])
        out = await runner.solve_page(object(), document=lambda: None, deadline=monotonic() + 10)
        assert (out["vendor"], out["solved"], out["reason"], out["layers"]) == (None, False, "none", [])

    @pytest.mark.asyncio
    async def test_layered_vendors_are_solved_in_turn(self, fake_loop):
        first = _Response(403, {"x-cdn": "Imperva"})
        reloaded = _Response(200, {"server": "nginx"})
        current = [first]
        imperva = _Handler("imperva", [SolveResult(True, "solved", ["reese84"])])
        dd = _Handler("datadome", [SolveResult(True, "solved", ["datadome"])], after=lambda: current.__setitem__(0, reloaded))
        signals = fake_loop([_det("imperva"), _det("datadome", "device_check")], [imperva, dd])
        out = await runner.solve_page(object(), document=lambda: current[0], deadline=monotonic() + 20)
        assert out["solved"] is True and out["vendor"] == "datadome" and out["reason"] == "solved"
        assert [(layer["vendor"], layer["solved"]) for layer in out["layers"]] == [
            ("imperva", True),
            ("datadome", True),
        ]
        assert out["layers"][0]["cookies"] == ["reese84"]
        # Solved in place, no new document: the re-read keeps the detected document's status and headers. After
        # DataDome reloaded the page, the new document's own status is used.
        assert signals == [(403, {"x-cdn": "Imperva"}), (403, {"x-cdn": "Imperva"}), (200, {"server": "nginx"})]

    @pytest.mark.asyncio
    async def test_a_document_that_arrives_during_the_read_is_read_again(self, fake_loop):
        first = _Response(202, {"x-amzn-waf-action": "challenge"})
        reloaded = _Response(200, {"server": "nginx"})
        calls = []

        def document():
            calls.append(1)
            return first if len(calls) == 1 else reloaded

        signals = fake_loop([], [])
        out = await runner.solve_page(object(), document=document, deadline=monotonic() + 20)
        assert out["reason"] == "none"
        assert signals == [(202, {"x-amzn-waf-action": "challenge"}), (200, {"server": "nginx"})]

    @pytest.mark.asyncio
    async def test_a_vendor_still_there_after_its_solve_is_reported_unsolved(self, fake_loop):
        akamai = _Handler("akamai", [SolveResult(True, "solved:warmup")])
        fake_loop([_det("akamai", "block"), _det("akamai", "block")], [akamai])
        out = await runner.solve_page(object(), document=lambda: None, deadline=monotonic() + 20)
        assert out["solved"] is False and out["reason"] == "still_detected"
        assert len(akamai.calls) == 1

    @pytest.mark.asyncio
    async def test_a_ban_is_not_attempted(self, fake_loop):
        dd = _Handler("datadome", [])
        fake_loop([_det("datadome", "ban", "dd.hard")], [dd])
        out = await runner.solve_page(object(), document=lambda: None, deadline=monotonic() + 20)
        assert (out["kind"], out["solved"], out["reason"]) == ("ban", False, "ban") and not dd.calls

    @pytest.mark.asyncio
    async def test_an_unsolved_layer_stops_the_loop(self, fake_loop):
        px = _Handler("perimeterx", [SolveResult(False, "unsolved:no_widget")])
        fake_loop([_det("perimeterx", "block"), _det("akamai")], [px])
        out = await runner.solve_page(object(), document=lambda: None, deadline=monotonic() + 20)
        assert (out["vendor"], out["reason"], len(out["layers"])) == ("perimeterx", "unsolved:no_widget", 1)

    @pytest.mark.asyncio
    async def test_a_failing_handler_never_breaks_the_fetch(self, fake_loop):
        fake_loop([_det("kasada")], [_Handler("kasada", [], error=RuntimeError("boom"))])
        out = await runner.solve_page(object(), document=lambda: None, deadline=monotonic() + 20)
        assert (out["solved"], out["reason"]) == (False, "error:RuntimeError")

    @pytest.mark.asyncio
    async def test_a_handler_that_overruns_is_cut_off(self, fake_loop, monkeypatch):
        monkeypatch.setattr(runner, "SOLVE_GRACE", 0.2)
        fake_loop([_det("kasada")], [_Handler("kasada", [SolveResult(True, "solved")], delay=30)])
        began = monotonic()
        out = await runner.solve_page(object(), document=lambda: None, deadline=monotonic() + 1.5)
        assert monotonic() - began < 2.5
        assert (out["solved"], out["reason"]) == (False, "timeout")

    @pytest.mark.asyncio
    async def test_no_solve_starts_without_time_left(self, fake_loop):
        cf = _Handler("cloudflare", [SolveResult(True, "solved")])
        fake_loop([_det("cloudflare")], [cf])
        out = await runner.solve_page(object(), document=lambda: None, deadline=monotonic() + 0.5)
        assert out["reason"] == "timeout" and not cf.calls

    @pytest.mark.asyncio
    async def test_one_solver_scope_per_fetch_and_its_summary(self, fake_loop):
        router = _Router(attempts=1)
        cf = _Handler("cloudflare", [SolveResult(True, "solved", used_solver="capmonster")])
        fake_loop([_det("cloudflare", "captcha", "cf.turnstile")], [cf])
        out = await runner.solve_page(object(), document=lambda: None, deadline=monotonic() + 20, solver=router)
        assert len(router.scopes) == 1 and cf.calls[0][2] is router.scopes[0]
        assert out["layers"][0]["used_solver"] == "capmonster" and out["solver"]["attempts"] == 1

    @pytest.mark.asyncio
    async def test_a_scope_passed_in_is_used_as_it_is(self, fake_loop):
        """A caller that retries a fetch keeps one budget and one ledger by passing ``router.scope()``."""
        scope = SolverRouter([]).scope()
        cf = _Handler("cloudflare", [SolveResult(False, "unsolved:solver_error", solver_kind="turnstile")])
        fake_loop([_det("cloudflare", "captcha", "cf.turnstile")], [cf])
        out = await runner.solve_page(object(), document=lambda: None, deadline=monotonic() + 20, solver=scope)
        assert scope.is_scope and cf.calls[0][2] is scope
        assert out["layers"][0]["solver_kind"] == "turnstile"

    @pytest.mark.asyncio
    async def test_layers_are_capped(self, fake_loop):
        handlers = [_Handler(v, [SolveResult(True, "solved")]) for v in ("cloudflare", "aws_waf", "kasada", "imperva")]
        fake_loop([_det(h.vendor) for h in handlers], handlers)
        out = await runner.solve_page(object(), document=lambda: None, deadline=monotonic() + 20, max_layers=3)
        assert out["reason"] == "max_layers" and out["solved"] is False and len(out["layers"]) == 4


# ------------------------------------------- real detection and handlers: an unchanged page is never solved

_INCIDENT_BLOCK = (
    "<html><head><title>Access denied</title><style>" + "body{margin:0;padding:0}" * 300 + "</style></head>"
    "<body><h1>Access denied</h1><p>Error 15. This request was blocked by our security service. "
    "Incapsula incident ID: 123000450123456789-12345</p></body></html>"
)
_DD_HEADER_ONLY = "<html><head><title>x</title></head><body><p>Please enable JS and disable any ad blocker</p></body></html>"
_AWS_GATE = "<html><body><h1>Forbidden</h1></body></html>"


@pytest.fixture
def unchanged_page(monkeypatch):
    """A fake page whose document never changes, read the way the runner reads a live one."""
    from .iak_fakes import FakePage, FakeResponse, no_wander

    async def quiet(page, frame, expression, timeout=2.0):
        return page.html

    monkeypatch.setattr(runner, "quiet_evaluate", quiet)
    monkeypatch.setattr(datadome, "quiet_evaluate", quiet)
    monkeypatch.setattr(_imperva_solver, "wander", no_wander)
    monkeypatch.setattr(_awswaf_solver, "wander", no_wander)
    monkeypatch.setattr(_imperva_solver, "BLOCK_PATIENCE", 1.0)
    monkeypatch.setattr(_awswaf_solver, "TOKEN_STATUS_PATIENCE", 1.0)
    monkeypatch.setitem(runner.registry._BY_VENDOR, "datadome", datadome.DataDomeHandler(no_frame_grace=1.0))

    def make(html, status, headers, cookies):
        page = FakePage("https://www.example.test/item", html)
        page.context.store.update(cookies)
        response = FakeResponse(page.url, status, headers, frame=page.main_frame)

        async def all_headers():
            return dict(response.headers)

        response.all_headers = all_headers
        return page, (lambda: response)

    return make


class TestUnchangedPages:
    CASES = [
        ("imperva", _INCIDENT_BLOCK, 403, {"x-iinfo": "1-2-3", "x-cdn": "Imperva"}, {"visid_incap_1": "v"}, "blocked"),
        ("datadome", _DD_HEADER_ONLY, 403, {"x-dd-b": "3", "x-datadome": "protected"}, {"datadome": "same"}, "no_challenge"),
        ("aws_waf", _AWS_GATE, 403, {}, {"aws-waf-token": "tok"}, "blocked"),
    ]

    @pytest.mark.asyncio
    @pytest.mark.parametrize("vendor,html,status,headers,cookies,reason", CASES, ids=[c[0] for c in CASES])
    async def test_the_handler_reports_it_unsolved(self, unchanged_page, vendor, html, status, headers, cookies, reason):
        page, document = unchanged_page(html, status, headers, cookies)
        out = await runner.solve_page(page, document=document, deadline=monotonic() + 8)
        assert (out["vendor"], out["solved"], out["reason"]) == (vendor, False, reason), out

    @pytest.mark.asyncio
    @pytest.mark.parametrize("vendor,html,status,headers,cookies,reason", CASES, ids=[c[0] for c in CASES])
    async def test_a_handler_that_claims_success_is_caught(
        self, unchanged_page, monkeypatch, vendor, html, status, headers, cookies, reason
    ):
        page, document = unchanged_page(html, status, headers, cookies)
        monkeypatch.setitem(runner.registry._BY_VENDOR, vendor, _Handler(vendor, [SolveResult(True, "solved")]))
        out = await runner.solve_page(page, document=document, deadline=monotonic() + 8)
        assert (out["vendor"], out["solved"], out["reason"]) == (vendor, False, "still_detected"), out


# ------------------------------------------------------------------------------------------------ the bridge


class TestSyncBridge:
    def test_async_shapes_are_read_from_the_async_api(self):
        from patchright.sync_api import Frame, Mouse, Page

        assert _async_kind(Page, "goto") == "coroutine"
        assert _async_kind(Page, "url") == "property"
        assert _async_kind(Page, "frame") == "plain"
        assert _async_kind(Frame, "evaluate") == "coroutine"
        assert _async_kind(Mouse, "move") == "coroutine"

    def test_plain_values_pass_through(self):
        value = {"a": [1, ("b", None)]}
        assert wrap(value) == value and unwrap(value) == value
        assert not isinstance(wrap(object()), AsyncView)


# ------------------------------------------------------------------------------------------- in the browser


@pytest.fixture(scope="module")
def iak():
    server = IakServer()
    yield server
    server.close()


@pytest.fixture(autouse=True)
def quick_reloads(monkeypatch):
    for module in (_imperva_solver, _awswaf_solver, _kasada_solver):
        monkeypatch.setattr(module, "RELOAD_AFTER", 1.0)


@pytest.fixture(scope="module")
def dd_site():
    server = DataDomeFixture()
    yield server
    server.close()


@pytest.fixture
def dd_frames(dd_site, monkeypatch):
    """Let the DataDome handler treat the fixture's frame origin as DataDome's challenge host."""
    original = datadome.is_dd_frame
    monkeypatch.setattr(
        datadome, "is_dd_frame", lambda url: (url or "").startswith(dd_site.frame_origin + "/") or original(url)
    )
    return dd_site


_GATE = """<html><head><title>One more step</title></head><body>
<form id="f" action="/done" method="get"><div class="cf-turnstile" data-sitekey="0x4AAAAAAATESTKEY" data-callback="onToken"></div>
<input type="hidden" name="cf-turnstile-response"></form>
<script>function onToken(token) { document.getElementById('f').submit(); }</script></body></html>"""


class _GateHandler(BaseHTTPRequestHandler):
    def log_message(self, *_):
        pass

    def do_GET(self):  # noqa: N802
        url = urlsplit(self.path)
        if url.path == "/gate":
            body = _GATE
        elif url.path == "/done" and parse_qs(url.query).get("cf-turnstile-response", [""])[0].startswith("TOKEN-"):
            body = "<html><head><title>Results</title></head><body>" + LONG_TEXT + "</body></html>"
        else:
            body = "<html><body>" + LONG_TEXT + "</body></html>"
        data = body.encode()
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)


@pytest.fixture(scope="module")
def gate_site():
    httpd = ThreadingHTTPServer(("127.0.0.1", 0), _GateHandler)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    yield f"http://127.0.0.1:{httpd.server_address[1]}"
    httpd.shutdown()
    httpd.server_close()


@pytest.fixture
def providers():
    server = MockProviders().start()
    try:
        yield server
    finally:
        server.stop()


def _text(response) -> str:
    return " ".join(response.css("body ::text").getall())


class TestAsyncSession:
    @pytest.mark.asyncio
    async def test_challenges_are_solved_and_recorded(self, iak):
        async with AsyncStealthySession(**_session_kwargs(solve_antibot=True)) as session:
            for path, vendor in (("/kasada", "kasada"), ("/aws/challenge", "aws_waf"), ("/imperva", "imperva")):
                iak.reset()
                response = await session.fetch(iak.url(path))
                outcome = response.meta["antibot"]
                assert (outcome["vendor"], outcome["solved"], outcome["reason"]) == (vendor, True, "solved"), outcome
                assert response.status == 200 and "Catalogue" in _text(response)
                json.dumps(outcome)  # JSON-safe
            clean = await session.fetch(iak.url("/missing"))
            assert clean.meta["antibot"]["reason"] == "none"

    @pytest.mark.asyncio
    async def test_the_option_can_be_turned_on_per_fetch(self, iak):
        async with AsyncStealthySession(**_session_kwargs()) as session:
            iak.reset()
            plain = await session.fetch(iak.url("/aws/challenge?stall=1"))
            assert "antibot" not in plain.meta
            iak.reset()
            solved = await session.fetch(iak.url("/kasada"), solve_antibot=True)
            assert solved.meta["antibot"]["solved"] is True

    @pytest.mark.asyncio
    async def test_a_failing_pass_never_fails_the_fetch(self, iak, monkeypatch):
        async def broken(*args, **kwargs):
            raise RuntimeError("detector exploded")

        monkeypatch.setattr(runner, "solve_page", broken)
        async with AsyncStealthySession(**_session_kwargs(solve_antibot=True)) as session:
            response = await session.fetch(iak.url("/missing"))
        assert response.status == 404
        assert (response.meta["antibot"]["solved"], response.meta["antibot"]["reason"]) == (False, "error:RuntimeError")

    @pytest.mark.asyncio
    async def test_hardened_session_passes_datadomes_frame_consistency_check(self, dd_frames):
        state = dd_frames.reset()
        async with AsyncStealthySession(**_session_kwargs(solve_antibot=True)) as session:
            response = await session.fetch(dd_frames.url("/dd/check"))
        outcome = response.meta["antibot"]
        assert (outcome["vendor"], outcome["solved"]) == ("datadome", True), (outcome, state.reports)
        assert [r["why"] for r in state.reports if "why" in r] == [[]]
        assert response.status == 200 and "Products" in _text(response)

    @pytest.mark.asyncio
    async def test_turnstile_gate_with_a_captcha_solver(self, gate_site, providers):
        router = SolverRouter.from_config(
            {"capmonster": providers.key, "api_bases": {"capmonster": providers.base("capmonster")}}
        )
        for solver in router._shared.solvers.values():
            solver.token_first_poll = solver.poll_interval = 0.01
        async with AsyncStealthySession(**_session_kwargs(solve_antibot=True, captcha_solver=router)) as session:
            response = await session.fetch(f"{gate_site}/gate")
        outcome = response.meta["antibot"]
        assert (outcome["vendor"], outcome["rule"], outcome["solved"]) == ("cloudflare", "cf.turnstile", True), outcome
        assert outcome["layers"][0]["used_solver"] == "capmonster"
        assert outcome["solver"]["attempts"] == 1 and outcome["solver"]["records"][0]["ok"] is True
        task = providers.created("capmonster")[0]
        assert task["type"] == "TurnstileTask" and task["websiteKey"] == "0x4AAAAAAATESTKEY"
        assert not any(k.startswith("proxy") for k in task)
        assert "Results" in response.css("title::text").get()
        assert providers.key not in json.dumps(outcome)


class TestSyncSession:
    def test_fetcher_solves_through_the_sync_api(self, iak):
        iak.reset()
        response = StealthyFetcher.fetch(iak.url("/aws/challenge"), **_session_kwargs(solve_antibot=True))
        outcome = response.meta["antibot"]
        assert (outcome["vendor"], outcome["solved"]) == ("aws_waf", True), outcome
        assert "Catalogue" in _text(response)

    def test_sync_session_hardens_frames_and_solves_datadome(self, dd_frames):
        state = dd_frames.reset()
        with StealthySession(**_session_kwargs(solve_antibot=True)) as session:
            response = session.fetch(dd_frames.url("/dd/check"))
            again = session.fetch(dd_frames.url("/dd/check"))  # a pooled page keeps its hardening
        assert response.meta["antibot"]["solved"] is True, (response.meta["antibot"], state.reports)
        assert [r["why"] for r in state.reports if "why" in r] in ([[]], [[], []])
        assert again.meta["antibot"]["reason"] in ("none", "solved")
