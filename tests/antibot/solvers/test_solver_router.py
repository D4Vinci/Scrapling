"""SolverRouter: routing table, fallback, caps, cooldowns, proxies and config, against the local provider mock."""

import asyncio
import json
import logging
import time

import pytest

from scrapling.engines.antibot.solvers import (
    DEFAULT_ROUTES,
    Solver,
    SolverBadRequest,
    SolverBudgetExceeded,
    SolverConfigError,
    SolverProxyNotAllowed,
    SolverRouter,
    SolverTimeout,
    SolverUnsolvable,
    SolverUnsupported,
    Token,
)

from .conftest import fast

PAGE = "https://example.com/"
TS_KEY = "0x4AAAAAAABUYP0XeMJF0xoy"
RC_KEY = "6LcR_okUAAAAAPYrPe-HK_0RULO1aZM15ENyM-Mf"


def build(mock, providers=("capmonster", "capsolver", "2captcha"), **options):
    config = {name: mock.key for name in providers}
    config["api_bases"] = {name: mock.base(name) for name in providers}
    config.update(options)
    router = SolverRouter.from_config(config)
    for solver in router._shared.solvers.values():
        fast(solver)
    return router


def providers_called(mock):
    return [p for p, m, _ in mock.requests if m == "createTask"]


# ---- config ----------------------------------------------------------------------------------------------------


def test_from_config_without_keys_returns_none():
    assert SolverRouter.from_config(None) is None
    assert SolverRouter.from_config({}) is None
    assert SolverRouter.from_config({"capmonster": "", "2captcha": None, "allow_proxy": False}) is None


def test_from_config_validates_without_echoing_values():
    with pytest.raises(SolverConfigError) as info:
        SolverRouter.from_config({"capmonster": "k" * 10, "capmonstr": "SECRET-VALUE"})
    assert "capmonstr" in str(info.value) and "SECRET-VALUE" not in str(info.value)
    with pytest.raises(SolverConfigError):
        SolverRouter.from_config({"capmonster": 12345})
    with pytest.raises(SolverConfigError):
        SolverRouter.from_config({"2captcha": "a" * 8, "twocaptcha": "b" * 8})
    with pytest.raises(SolverConfigError):
        SolverRouter.from_config({"capmonster": "a" * 8, "routes": {"not_a_kind": ["capmonster"]}})


def test_from_config_builds_providers_and_options():
    router = SolverRouter.from_config(
        {"capmonster": "a" * 8, "twocaptcha": "b" * 8, "allow_proxy": False, "max_solves_per_fetch": 3, "timeout": 50}
    )
    assert router.providers == ["2captcha", "capmonster"]
    assert router.max_solves_per_fetch == 3 and router.timeout == 50 and router.allow_proxy is False
    assert "a" * 8 not in repr(router)
    assert isinstance(router, Solver)


def test_default_routing_table(mock):
    router = build(mock)
    assert router.route("turnstile") == ["capmonster", "capsolver", "2captcha"]
    assert router.route("recaptcha_v2") == ["capmonster", "2captcha", "capsolver"]
    assert router.route("geetest_v4") == ["capmonster", "2captcha", "capsolver"]
    assert router.route("awswaf") == ["capmonster", "capsolver"]
    assert router.route("funcaptcha") == ["2captcha"]
    assert router.route("hcaptcha") == ["capmonster"]
    assert router.route("recaptcha_grid") == ["capsolver", "capmonster", "2captcha"]
    assert router.route("datadome_slider") == ["capsolver"]
    assert router.route("awswaf_images") == ["capsolver"]
    assert set(DEFAULT_ROUTES) == set(__import__("scrapling.engines.antibot.solvers", fromlist=["ALL_KINDS"]).ALL_KINDS)
    assert not router.supports("turnstile_challenge") and not router.supports("datadome_slider")
    assert build(mock, experimental=True).supports("datadome_slider")


def test_custom_routes(mock):
    router = build(mock, routes={"turnstile": ["2captcha", "capmonster"]})
    assert router.route("turnstile") == ["2captcha", "capmonster"]


# ---- solving ---------------------------------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_primary_provider_answers(mock):
    router = build(mock).scope()
    token = await router.solve_token("turnstile", TS_KEY, PAGE, action="login")
    assert isinstance(token, Token) and token.provider == "capmonster"
    assert providers_called(mock) == ["capmonster"]
    summary = router.summary()
    assert summary["solves"] == 1 and summary["attempts"] == 1
    assert summary["cost_usd"] == pytest.approx(0.0013)
    json.dumps(summary)


@pytest.mark.asyncio
async def test_falls_back_on_unsolvable(mock):
    mock.fail["capmonster"] = ("ERROR_CAPTCHA_UNSOLVABLE", "")
    router = build(mock).scope()
    token = await router.solve_token("recaptcha_v2", RC_KEY, PAGE)
    assert token.provider == "2captcha"
    assert providers_called(mock) == ["capmonster", "2captcha"]
    assert [(r.provider, r.ok) for r in router.records] == [("capmonster", False), ("2captcha", True)]
    assert router.spent_usd == pytest.approx(0.00145)  # 2Captcha's reported cost; failed attempt costs nothing


@pytest.mark.asyncio
async def test_balance_error_cools_provider_down(mock):
    mock.create_fail["capmonster"] = ("ERROR_ZERO_BALANCE", "")
    router = build(mock)
    first = await router.scope().solve_token("turnstile", TS_KEY, PAGE)
    assert first.provider == "capsolver"
    assert router.route("turnstile") == ["capsolver", "2captcha"]
    second = await router.scope().solve_token("turnstile", TS_KEY, PAGE)
    assert second.provider == "capsolver"
    assert providers_called(mock) == ["capmonster", "capsolver", "capsolver"]


@pytest.mark.asyncio
async def test_no_fallback_for_caller_errors(mock):
    router = build(mock).scope()
    with pytest.raises(SolverBadRequest):
        await router.solve_token("geetest_v3", "gt-value", PAGE)  # missing challenge: every provider would refuse
    assert providers_called(mock) == []
    with pytest.raises(SolverBadRequest):
        await router.solve_token("turnstile", TS_KEY, PAGE, sitekey_typo="x")
    with pytest.raises(SolverUnsupported):
        await router.solve_token("image_text", "", PAGE)


@pytest.mark.asyncio
async def test_all_providers_fail(mock):
    for p in ("capmonster", "capsolver", "2captcha"):
        mock.fail[p] = ("ERROR_CAPTCHA_UNSOLVABLE", "")
    router = build(mock).scope()
    with pytest.raises(SolverUnsolvable) as info:
        await router.solve_token("turnstile", TS_KEY, PAGE)
    assert info.value.provider == "router"
    assert "capmonster=ERROR_CAPTCHA_UNSOLVABLE" in str(info.value) and "2captcha=" in str(info.value)
    assert len(info.value.errors) == 3


@pytest.mark.asyncio
async def test_max_attempts_per_solve(mock):
    mock.fail["capmonster"] = ("ERROR_CAPTCHA_UNSOLVABLE", "")
    router = build(mock, max_attempts_per_solve=1).scope()
    with pytest.raises(SolverUnsolvable):
        await router.solve_token("turnstile", TS_KEY, PAGE)
    assert providers_called(mock) == ["capmonster"]


@pytest.mark.asyncio
async def test_max_solves_per_fetch_and_scopes(mock):
    router = build(mock, max_solves_per_fetch=2)
    fetch = router.scope()
    await fetch.solve_token("turnstile", TS_KEY, PAGE)
    await fetch.recognize("recaptcha_grid", [b"x" * 200], question="crosswalks")
    with pytest.raises(SolverBudgetExceeded):
        await fetch.solve_token("turnstile", TS_KEY, PAGE)
    assert len(providers_called(mock)) == 2  # the refused solve sent nothing
    other = router.scope()
    await other.solve_token("turnstile", TS_KEY, PAGE)
    assert fetch.solves_used == 2 and other.solves_used == 1
    assert len(router.all_records) == 3
    assert router.total_spent_usd == pytest.approx(fetch.spent_usd + other.spent_usd)


@pytest.mark.asyncio
async def test_spend_caps(mock):
    router = build(mock, max_cost_usd_per_fetch=0.00125)  # below CapMonster's Turnstile price (0.0013)
    token = await router.scope().solve_token("turnstile", TS_KEY, PAGE)
    assert token.provider == "capsolver"  # 0.0012 fits under the cap
    with pytest.raises(SolverBudgetExceeded):
        await build(mock, max_cost_usd_per_fetch=0.0001).scope().solve_token("turnstile", TS_KEY, PAGE)

    total = build(mock, max_cost_usd_total=0.0015)
    await total.scope().solve_token("turnstile", TS_KEY, PAGE)
    with pytest.raises(SolverBudgetExceeded):
        await total.scope().solve_token("turnstile", TS_KEY, PAGE)


@pytest.mark.asyncio
async def test_proxy_policy(mock):
    router = build(mock).scope()
    with pytest.raises(SolverProxyNotAllowed):
        await router.solve_token("recaptcha_v2", RC_KEY, PAGE, proxy="http://u:p@1.2.3.4:80")
    with pytest.raises(SolverProxyNotAllowed):
        await build(mock, allow_proxy=True).scope().recognize("slider", [b"a", b"b"], proxy="http://1.2.3.4:80")
    assert mock.requests == []
    allowed = build(mock, allow_proxy=True).scope()
    token = await allowed.solve_token("recaptcha_v2", RC_KEY, PAGE, proxy="http://u:p@1.2.3.4:80")
    assert token.provider == "capmonster" and mock.created("capmonster")[-1]["proxyAddress"] == "1.2.3.4"


@pytest.mark.asyncio
async def test_experimental_kinds_need_opt_in(mock):
    args = dict(action="managed", cdata="c", page_data="p", user_agent="UA")
    with pytest.raises(SolverUnsupported) as info:
        await build(mock).scope().solve_token("turnstile_challenge", TS_KEY, PAGE, **args)
    assert info.value.code == "EXPERIMENTAL"
    token = await build(mock, experimental=True).scope().solve_token("turnstile_challenge", TS_KEY, PAGE, **args)
    assert token.provider == "capmonster"


@pytest.mark.asyncio
async def test_no_provider_for_kind(mock):
    router = build(mock, providers=("capsolver",)).scope()
    with pytest.raises(SolverUnsupported) as info:
        await router.solve_token("funcaptcha", "6220FF23-9856-3A6F-9FF1-A14F88123F55", PAGE)
    assert info.value.code == "NO_PROVIDER"


@pytest.mark.asyncio
async def test_router_deadline(mock):
    for p in ("capmonster", "capsolver", "2captcha"):
        mock.hang.add(p)
    router = build(mock, min_attempt_s=0.5).scope()
    for solver in router._shared.solvers.values():
        solver.max_polls = 10_000
        solver.poll_interval = 0.05
    started = time.monotonic()
    with pytest.raises(SolverTimeout):
        await router.solve_token("turnstile", TS_KEY, PAGE, deadline=time.monotonic() + 1.0)
    elapsed = time.monotonic() - started
    assert 0.9 <= elapsed < 1.6
    # The first provider used the whole budget, so no second provider was started without enough time left.
    assert providers_called(mock) == ["capmonster"]


@pytest.mark.asyncio
async def test_recognition_fallback(mock):
    mock.create_fail["capsolver"] = ("ERROR_CAPTCHA_UNSOLVABLE", "")
    router = build(mock).scope()
    result = await router.recognize("recaptcha_grid", [b"x" * 200], question="Select all images with cars")
    assert result["provider"] == "capmonster" and result["objects"] == [1, 4]


@pytest.mark.asyncio
async def test_crashing_custom_solver_falls_back(mock, caplog):
    class Broken:
        name = "broken"
        prices = {}

        def supports(self, kind):
            return True

        async def solve_token(self, kind, sitekey, page_url, **extra):
            raise RuntimeError("bug")

        async def recognize(self, kind, images, **extra):
            raise RuntimeError("bug")

    class Fine:
        name = "fine"
        prices = {}

        def supports(self, kind):
            return True

        async def solve_token(self, kind, sitekey, page_url, **extra):
            assert "deadline" in extra
            return Token("tok", kind=kind, provider="fine", cost_usd=0.002, cost_source="estimated")

        async def recognize(self, kind, images, **extra):
            return {"text": "x", "provider": "fine", "cost_usd": None}

    router = SolverRouter(
        [Broken(), Fine()], routes={"turnstile": ["broken", "fine"], "image_text": ["broken", "fine"]}
    )
    caplog.set_level(logging.INFO, logger="scrapling")
    token = await router.solve_token("turnstile", TS_KEY, PAGE)
    assert token == "tok" and router.spent_usd == pytest.approx(0.002)
    assert (await router.recognize("image_text", [b"img"]))["text"] == "x"
    assert any("broken" in r.getMessage() and "crashed" in r.getMessage() for r in caplog.records)


@pytest.mark.asyncio
async def test_concurrent_scopes_share_cooldowns(mock):
    mock.create_fail["capmonster"] = ("ERROR_KEY_DOES_NOT_EXIST", "")
    router = build(mock)
    tokens = await asyncio.gather(*(router.scope().solve_token("turnstile", TS_KEY, PAGE) for _ in range(4)))
    assert all(t.provider == "capsolver" for t in tokens)
    assert providers_called(mock).count("capmonster") <= 4
    assert "capmonster" not in router.route("turnstile")


@pytest.mark.asyncio
async def test_router_logs_no_secrets(mock, caplog):
    caplog.set_level(logging.DEBUG, logger="scrapling")
    mock.fail["capmonster"] = ("ERROR_CAPTCHA_UNSOLVABLE", f"bad {mock.key}")
    router = build(mock).scope()
    token = await router.solve_token("turnstile", TS_KEY, PAGE)
    text = " ".join(r.getMessage() for r in caplog.records) + json.dumps(router.summary())
    assert mock.key not in text and str(token) not in text


# ---- spend accounting: booked when a task is sent ----------------------------------------------------------------


class _Priced:
    """A custom solver with a price list that fails (or answers) the way it is told."""

    def __init__(self, name, error=None, prices=None, cost=None):
        self.name = name
        self.error = error
        self.prices = {"turnstile": 2.0} if prices is None else prices
        self.cost = cost
        self.calls = 0

    def supports(self, kind):
        return True

    async def solve_token(self, kind, sitekey, page_url, **extra):
        self.calls += 1
        if self.error is not None:
            raise self.error
        return Token("tok", kind=kind, provider=self.name, cost_usd=self.cost, cost_source="reported" if self.cost else None)

    async def recognize(self, kind, images, **extra):  # pragma: no cover - not used
        raise NotImplementedError


@pytest.mark.asyncio
async def test_a_task_abandoned_at_the_deadline_is_still_booked(mock):
    mock.hang.add("capmonster")
    router = build(mock, min_attempt_s=0.5).scope()
    for solver in router._shared.solvers.values():
        solver.max_polls = 10_000
        solver.poll_interval = 0.05
    with pytest.raises(SolverTimeout):
        await router.solve_token("turnstile", TS_KEY, PAGE, deadline=time.monotonic() + 0.8)
    # CapMonster accepted the task and may still finish and bill it: its estimate stays on the ledger.
    assert router.spent_usd == pytest.approx(0.0013) and router.summary()["cost_usd"] == pytest.approx(0.0013)
    assert router.records[-1].cost_source == "estimated"


@pytest.mark.asyncio
async def test_a_cancelled_call_keeps_its_booking(mock):
    mock.hang.add("capmonster")
    router = build(mock).scope()
    with pytest.raises(asyncio.TimeoutError):
        await asyncio.wait_for(router.solve_token("turnstile", TS_KEY, PAGE), 0.6)
    assert router.spent_usd == pytest.approx(0.0013) and router.records[-1].error_code == "CANCELLED"
    assert router.total_spent_usd == pytest.approx(0.0013)


@pytest.mark.asyncio
async def test_refused_tasks_are_refunded(mock):
    mock.create_fail["capmonster"] = ("ERROR_ZERO_BALANCE", "")
    router = build(mock).scope()
    token = await router.solve_token("turnstile", TS_KEY, PAGE)
    assert token.provider == "capsolver" and router.spent_usd == pytest.approx(0.0012)


@pytest.mark.asyncio
async def test_a_provider_that_fails_after_accepting_the_task_is_not_followed_by_another():
    from scrapling.engines.antibot.solvers import SolverUnavailable

    lost = _Priced("first", error=SolverUnavailable("network", code="NETWORK", task_created=True))
    second = _Priced("second")
    router = SolverRouter([lost, second], routes={"turnstile": ["first", "second"]}).scope()
    with pytest.raises(SolverUnavailable):
        await router.solve_token("turnstile", TS_KEY, PAGE)
    assert (lost.calls, second.calls) == (1, 0)
    assert router.spent_usd == pytest.approx(0.002)  # the lost task may be billed
    # The same failure before any task existed falls back, and costs nothing.
    early = _Priced("first", error=SolverUnavailable("network", code="NETWORK", task_created=False))
    router = SolverRouter([early, _Priced("second", cost=0.0015)], routes={"turnstile": ["first", "second"]}).scope()
    assert (await router.solve_token("turnstile", TS_KEY, PAGE)) == "tok"
    assert router.spent_usd == pytest.approx(0.0015)  # the provider's reported cost replaces the estimate


@pytest.mark.asyncio
async def test_a_kind_without_a_price_is_refused_under_a_spend_cap():
    unpriced = _Priced("unpriced", prices={})
    capped = SolverRouter([unpriced], routes={"turnstile": ["unpriced"]}, max_cost_usd_total=1.0).scope()
    with pytest.raises(SolverBudgetExceeded) as info:
        await capped.solve_token("turnstile", TS_KEY, PAGE)
    assert info.value.code == "NO_PRICE" and unpriced.calls == 0
    uncapped = SolverRouter([unpriced], routes={"turnstile": ["unpriced"]}).scope()
    assert (await uncapped.solve_token("turnstile", TS_KEY, PAGE)) == "tok"


def test_every_built_in_kind_has_a_price():
    from scrapling.engines.antibot.solvers import CapMonsterSolver, CapSolverSolver, TwoCaptchaSolver

    for cls in (CapMonsterSolver, CapSolverSolver, TwoCaptchaSolver):
        assert (cls.token_kinds | cls.recognition_kinds) <= set(cls.default_prices), cls.name


def test_per_image_kinds_are_estimated_per_image():
    from scrapling.engines.antibot.solvers import CapMonsterSolver
    from scrapling.engines.antibot.solvers.router import _price

    solver = CapMonsterSolver("k" * 12)
    assert _price(solver, "recaptcha_grid", 9) == pytest.approx(9 * 0.04 / 1000)
    assert _price(solver, "turnstile", 9) == pytest.approx(1.30 / 1000)
    assert _price(solver, "no_such_kind") is None


def test_scopes_say_they_are_scopes(mock):
    router = build(mock)
    assert router.is_scope is False and router.scope().is_scope is True


# ---- what providers are told about the page ----------------------------------------------------------------------


@pytest.mark.asyncio
async def test_providers_get_the_page_host_and_path_only(mock):
    router = build(mock).scope()
    await router.solve_token(
        "turnstile", TS_KEY, "https://user:pw@shop.example.com:8443/checkout/pay?session=abc&code=xyz#frag"
    )
    assert mock.created("capmonster")[-1]["websiteURL"] == "https://shop.example.com:8443/checkout/pay"


def test_provider_url():
    from scrapling.engines.antibot.solvers import provider_url

    assert provider_url("https://Example.com/a/b?x=1#y") == "https://example.com/a/b"
    assert provider_url("https://example.com") == "https://example.com/"
    assert provider_url("http://[::1]:8080/p?q") == "http://[::1]:8080/p"
    assert provider_url("javascript:alert(1)") == "" and provider_url("") == ""
