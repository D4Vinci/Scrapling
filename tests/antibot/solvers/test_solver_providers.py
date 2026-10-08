"""Provider clients against the local mock of each provider's documented API."""

import json
import logging
import socket
import time

import pytest

from scrapling.engines.antibot.solvers import (
    CapMonsterSolver,
    CapSolverSolver,
    Solver,
    SolverAuthError,
    SolverBadRequest,
    SolverBalanceError,
    SolverConfigError,
    SolverError,
    SolverProxyNotAllowed,
    SolverRateLimited,
    SolverTimeout,
    SolverUnavailable,
    SolverUnsolvable,
    SolverUnsupported,
    Token,
    TwoCaptchaSolver,
    recaptcha_label_id,
    recaptcha_label_text,
)
from scrapling.engines.antibot.solvers._client import ProxySpec, parse_grid

PAGE = "https://example.com/login"
TS_KEY = "0x4AAAAAAABUYP0XeMJF0xoy"
RC_KEY = "6LcR_okUAAAAAPYrPe-HK_0RULO1aZM15ENyM-Mf"

# (provider, kind, sitekey, extra, expected task fields, expected token prefix)
TOKEN_CASES = [
    # CapMonster: turnstile-task.mdx / turnstile-challenge-task.mdx
    (
        "capmonster",
        "turnstile",
        TS_KEY,
        {"action": "login", "cdata": "cd-1"},
        {"type": "TurnstileTask", "websiteKey": TS_KEY, "pageAction": "login", "data": "cd-1"},
        "TOKEN-capmonster",
    ),
    (
        "capmonster",
        "turnstile_challenge",
        TS_KEY,
        {"action": "managed", "cdata": "cd", "page_data": "pd", "user_agent": "UA/1"},
        {"type": "TurnstileTask", "cloudflareTaskType": "token", "pageData": "pd", "data": "cd", "userAgent": "UA/1"},
        "TOKEN-capmonster",
    ),
    # no-captcha-task.mdx, recaptcha-v2-enterprise-task.mdx, recaptcha-v3-task.mdx, recaptcha-v3-enterprise-task.mdx
    (
        "capmonster",
        "recaptcha_v2",
        RC_KEY,
        {"invisible": True, "data_s": "sss"},
        {"type": "RecaptchaV2Task", "isInvisible": True, "recaptchaDataSValue": "sss"},
        "TOKEN-capmonster",
    ),
    (
        "capmonster",
        "recaptcha_v2_enterprise",
        RC_KEY,
        {"enterprise_payload": {"s": "x"}, "api_domain": "recaptcha.net"},
        {"type": "RecaptchaV2EnterpriseTask", "enterprisePayload": {"s": "x"}, "apiDomain": "recaptcha.net"},
        "TOKEN-capmonster",
    ),
    (
        "capmonster",
        "recaptcha_v3",
        RC_KEY,
        {"action": "verify", "min_score": 0.7},
        {"type": "RecaptchaV3TaskProxyless", "minScore": 0.7, "pageAction": "verify", "isEnterprise": False},
        "TOKEN-capmonster",
    ),
    (
        "capmonster",
        "recaptcha_v3_enterprise",
        RC_KEY,
        {"action": "login"},
        {"type": "RecaptchaV3EnterpriseTask", "pageAction": "login"},
        "TOKEN-capmonster",
    ),
    # hcaptcha-task.mdx
    (
        "capmonster",
        "hcaptcha",
        "10000000-ffff-ffff-ffff-000000000001",
        {"invisible": True},
        {"type": "HCaptchaTask", "isInvisible": True},
        "TOKEN-capmonster",
    ),
    # geetest-task.mdx
    (
        "capmonster",
        "geetest_v3",
        "81388ea1fc187e0c335c0a8907ff2625",
        {"challenge": "c" * 32, "api_server": "api.geetest.com"},
        {
            "type": "GeeTestTask",
            "version": 3,
            "gt": "81388ea1fc187e0c335c0a8907ff2625",
            "geetestApiServerSubdomain": "api.geetest.com",
        },
        "VALIDATE-",
    ),
    (
        "capmonster",
        "geetest_v4",
        "e392e1d7fd421dc63325744d5a2b9c73",
        {"risk_type": "slide"},
        {"type": "GeeTestTask", "version": 4, "initParameters": {"riskType": "slide"}},
        "OUTPUT-",
    ),
    # amazon-task.mdx (variant 1, cookieSolution)
    (
        "capmonster",
        "awswaf",
        "h15hX7brbaRTR",
        {"aws_captcha_script": "https://x.captcha-sdk.awswaf.com/jsapi.js"},
        {"type": "AmazonTask", "cookieSolution": True, "websiteKey": "h15hX7brbaRTR"},
        "AWS-",
    ),
    # CapSolver: cloudflare_turnstile, ReCaptchaV2, ReCaptchaV3, Geetest, awsWaf guides
    (
        "capsolver",
        "turnstile",
        TS_KEY,
        {"action": "login", "cdata": "cd-1"},
        {"type": "AntiTurnstileTaskProxyLess", "metadata": {"action": "login", "cdata": "cd-1"}},
        "TOKEN-capsolver",
    ),
    (
        "capsolver",
        "recaptcha_v2",
        RC_KEY,
        {"invisible": True, "api_domain": "google.com"},
        {"type": "ReCaptchaV2TaskProxyLess", "isInvisible": True, "apiDomain": "google.com"},
        "TOKEN-capsolver",
    ),
    (
        "capsolver",
        "recaptcha_v2_enterprise",
        RC_KEY,
        {"enterprise_payload": {"s": "x"}},
        {"type": "ReCaptchaV2EnterpriseTaskProxyLess", "enterprisePayload": {"s": "x"}},
        "TOKEN-capsolver",
    ),
    (
        "capsolver",
        "recaptcha_v3",
        RC_KEY,
        {"action": "submit", "min_score": 0.9},
        {"type": "ReCaptchaV3TaskProxyLess", "pageAction": "submit"},
        "TOKEN-capsolver",
    ),
    (
        "capsolver",
        "recaptcha_v3_enterprise",
        RC_KEY,
        {"action": "submit"},
        {"type": "ReCaptchaV3EnterpriseTaskProxyLess", "pageAction": "submit"},
        "TOKEN-capsolver",
    ),
    (
        "capsolver",
        "geetest_v3",
        "81388ea1fc187e0c335c0a8907ff2625",
        {"challenge": "c" * 32},
        {"type": "GeeTestTaskProxyLess", "gt": "81388ea1fc187e0c335c0a8907ff2625", "challenge": "c" * 32},
        "VALIDATE-",
    ),
    (
        "capsolver",
        "geetest_v4",
        "e392e1d7fd421dc63325744d5a2b9c73",
        {},
        {"type": "GeeTestTaskProxyLess", "captchaId": "e392e1d7fd421dc63325744d5a2b9c73"},
        "OUTPUT-",
    ),
    (
        "capsolver",
        "awswaf",
        "AQIDAHjcYu",
        {"aws_iv": "iv", "aws_context": "ctx", "aws_challenge_script": "https://x.token.awswaf.com/challenge.js"},
        {"type": "AntiAwsWafTaskProxyLess", "awsKey": "AQIDAHjcYu", "awsIv": "iv", "awsContext": "ctx"},
        "AWS-",
    ),
    # 2Captcha API v2: cloudflare-turnstile, recaptcha-v2(-enterprise), recaptcha-v3, geetest, amazon-aws-waf-captcha, arkoselabs-funcaptcha
    (
        "2captcha",
        "turnstile",
        TS_KEY,
        {"action": "login", "cdata": "cd-1"},
        {"type": "TurnstileTaskProxyless", "action": "login", "data": "cd-1"},
        "TOKEN-2captcha",
    ),
    (
        "2captcha",
        "turnstile_challenge",
        TS_KEY,
        {"action": "managed", "cdata": "cd", "page_data": "pd"},
        {"type": "TurnstileTaskProxyless", "pagedata": "pd", "data": "cd", "action": "managed"},
        "TOKEN-2captcha",
    ),
    (
        "2captcha",
        "recaptcha_v2",
        RC_KEY,
        {"cookies": "a=1; b=2"},
        {"type": "RecaptchaV2TaskProxyless", "cookies": "a=1; b=2"},
        "TOKEN-2captcha",
    ),
    (
        "2captcha",
        "recaptcha_v2_enterprise",
        RC_KEY,
        {"enterprise_payload": {"s": "x"}},
        {"type": "RecaptchaV2EnterpriseTaskProxyless", "enterprisePayload": {"s": "x"}},
        "TOKEN-2captcha",
    ),
    (
        "2captcha",
        "recaptcha_v3",
        RC_KEY,
        {"min_score": 0.5, "action": "home"},
        {"type": "RecaptchaV3TaskProxyless", "minScore": 0.7, "isEnterprise": False, "pageAction": "home"},
        "TOKEN-2captcha",
    ),
    (
        "2captcha",
        "recaptcha_v3_enterprise",
        RC_KEY,
        {},
        {"type": "RecaptchaV3TaskProxyless", "minScore": 0.3, "isEnterprise": True},
        "TOKEN-2captcha",
    ),
    (
        "2captcha",
        "geetest_v3",
        "81388ea1fc187e0c335c0a8907ff2625",
        {"challenge": "c" * 32},
        {"type": "GeeTestTaskProxyless", "gt": "81388ea1fc187e0c335c0a8907ff2625"},
        "VALIDATE-",
    ),
    (
        "2captcha",
        "geetest_v4",
        "e392e1d7fd421dc63325744d5a2b9c73",
        {},
        {
            "type": "GeeTestTaskProxyless",
            "version": 4,
            "initParameters": {"captcha_id": "e392e1d7fd421dc63325744d5a2b9c73"},
        },
        "OUTPUT-",
    ),
    (
        "2captcha",
        "awswaf_voucher",
        "AQIDAHjcYu",
        {"aws_iv": "iv", "aws_context": "ctx"},
        {"type": "AmazonTaskProxyless", "websiteKey": "AQIDAHjcYu", "iv": "iv", "context": "ctx"},
        "VOUCHER-",
    ),
    (
        "2captcha",
        "funcaptcha",
        "6220FF23-9856-3A6F-9FF1-A14F88123F55",
        {"data": {"blob": "B"}, "funcaptcha_subdomain": "client-api.arkoselabs.com"},
        {
            "type": "FunCaptchaTaskProxyless",
            "data": '{"blob":"B"}',
            "funcaptchaApiJSSubdomain": "client-api.arkoselabs.com",
        },
        "TOKEN-2captcha",
    ),
]


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "provider,kind,sitekey,extra,expected,prefix", TOKEN_CASES, ids=[f"{c[0]}-{c[1]}" for c in TOKEN_CASES]
)
async def test_token_task_shapes_and_solutions(mock, make, provider, kind, sitekey, extra, expected, prefix):
    solver = make(provider)
    assert solver.supports(kind)
    token = await solver.solve_token(kind, sitekey, PAGE, timeout=10, **extra)

    sent = mock.created(provider)[-1]
    assert sent["websiteURL"] == PAGE
    for field, value in expected.items():
        assert sent[field] == value, field
    assert not any(f.startswith("proxy") for f in sent), "token tasks must be proxyless by default"

    assert isinstance(token, Token) and isinstance(token, str)
    assert token.startswith(prefix)
    assert token.kind == kind and token.provider == provider and token.task_id
    assert token.elapsed_s >= 0 and not token.expired
    if provider == "2captcha":
        assert token.cost_usd == pytest.approx(0.00145) and token.cost_source == "reported"
    elif kind in solver.prices:
        assert token.cost_usd == pytest.approx(solver.prices[kind] / 1000) and token.cost_source == "estimated"
    else:  # no published price (CapMonster hCaptcha): cost is unknown rather than guessed
        assert token.cost_usd is None and token.cost_source is None
    assert str(token) not in repr(token)
    assert solver.records[-1].ok and solver.records[-1].kind == kind


@pytest.mark.asyncio
async def test_token_fields_carry_full_solution(mock, make):
    v4 = await make("capmonster").solve_token("geetest_v4", "e392e1d7fd421dc63325744d5a2b9c73", PAGE)
    assert set(v4.fields) >= {"lot_number", "pass_token", "gen_time", "captcha_output"}
    voucher = await make("2captcha").solve_token("awswaf_voucher", "AQIDAHjcYu", PAGE, aws_iv="iv", aws_context="ctx")
    assert voucher.fields["existing_token"].startswith("EXISTING-")
    ts = await make("capsolver").solve_token("turnstile", TS_KEY, PAGE)
    assert ts.user_agent == "Mozilla/5.0 (solver UA)"


@pytest.mark.asyncio
async def test_polling_waits_until_ready(mock, make):
    mock.polls_needed = 3
    solver = make("capmonster")
    token = await solver.solve_token("turnstile", TS_KEY, PAGE)
    assert token.startswith("TOKEN-")
    polls = [b for p, m, b in mock.requests if m == "getTaskResult"]
    assert len(polls) == 3
    assert all(isinstance(b["taskId"], int) for b in polls)  # numeric task ids are sent back as numbers


RECOGNITION_CASES = [
    # CapSolver ReCaptchaV2Classification: one image, /m/ question id, synchronous
    (
        "capsolver",
        "recaptcha_grid",
        1,
        {"question": "Select all images with crosswalks"},
        {"type": "ReCaptchaV2Classification", "question": "/m/014xcs"},
        {"objects": [0, 4, 8], "has_object": True},
    ),
    # CapSolver VisionEngine slider_1: [piece, background] -> distance
    ("capsolver", "slider", 2, {}, {"type": "VisionEngine", "module": "slider_1"}, {"distance": 213.0}),
    ("capsolver", "datadome_slider", 2, {}, {"type": "VisionEngine", "module": "slider_1"}, {"distance": 213.0}),
    ("capsolver", "geetest_slide", 2, {}, {"type": "VisionEngine", "module": "slider_1"}, {"distance": 213.0}),
    ("capsolver", "rotate", 1, {}, {"type": "VisionEngine", "module": "rotate_1"}, {"angle": 45.5}),
    # CapSolver AwsWafClassification
    (
        "capsolver",
        "awswaf_images",
        9,
        {"question": "aws:grid:bag"},
        {"type": "AwsWafClassification", "question": "aws:grid:bag"},
        {"objects": [0, 3, 7]},
    ),
    ("capsolver", "image_text", 1, {}, {"type": "ImageToTextTask"}, {"text": "w93bx"}),
    # CapMonster ComplexImageTask recaptcha (recaptcha-click.mdx): answer booleans per image
    (
        "capmonster",
        "recaptcha_grid",
        9,
        {"question": "/m/015qff"},
        {"type": "ComplexImageTask", "class": "recaptcha", "metadata": {"Grid": "3x3", "TaskDefinition": "/m/015qff"}},
        {"objects": [1, 4], "has_object": True, "size": 9},
    ),
    (
        "capmonster",
        "recaptcha_grid",
        9,
        {"question": "Select all squares with street lamps"},
        {"type": "ComplexImageTask", "metadata": {"Grid": "3x3", "Task": "Select all squares with street lamps"}},
        {"objects": [1, 4]},
    ),
    ("capmonster", "image_text", 1, {}, {"type": "ImageToTextTask"}, {"text": "w93bx"}),
    # 2Captcha GridTask (1-based clicks) / CoordinatesTask / ImageToTextTask
    (
        "2captcha",
        "recaptcha_grid",
        1,
        {"question": "/m/0k4j", "grid": "4x4"},
        {"type": "GridTask", "comment": "cars", "rows": 4, "columns": 4, "imgType": "recaptcha"},
        {"objects": [0, 4, 8], "size": 16},
    ),
    (
        "2captcha",
        "coordinates",
        1,
        {"comment": "click the cat", "max_clicks": 2},
        {"type": "CoordinatesTask", "comment": "click the cat", "maxClicks": 2},
        {"points": [(10.0, 20.0), (30.5, 40.0)]},
    ),
    ("2captcha", "image_text", 1, {}, {"type": "ImageToTextTask"}, {"text": "w93bx"}),
]


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "provider,kind,n_images,extra,expected,result_subset",
    RECOGNITION_CASES,
    ids=[f"{c[0]}-{c[1]}-{i}" for i, c in enumerate(RECOGNITION_CASES)],
)
async def test_recognition_shapes_and_normalization(
    mock, make, provider, kind, n_images, extra, expected, result_subset
):
    solver = make(provider)
    images = [bytes([i]) * 120 for i in range(n_images)]
    result = await solver.recognize(kind, images, timeout=10, **extra)
    sent = mock.created(provider)[-1]
    for field, value in expected.items():
        assert sent[field] == value, field
    for field, value in result_subset.items():
        assert result[field] == value, field
    assert result["provider"] == provider
    assert result["cost_usd"] is not None and "raw" in result
    if provider == "capsolver":
        # CapSolver recognition answers synchronously from createTask: no polling.
        assert not [1 for p, m, _ in mock.requests if p == "capsolver" and m == "getTaskResult"]


@pytest.mark.asyncio
async def test_recognition_images_are_base64(mock, make):
    await make("capsolver").recognize("slider", [b"piece", "YmFja2dyb3VuZA=="])
    sent = mock.created("capsolver")[-1]
    assert sent["image"] == "cGllY2U=" and sent["imageBackground"] == "YmFja2dyb3VuZA=="


@pytest.mark.asyncio
async def test_capmonster_grid_cost_is_per_image(mock, make):
    result = await make("capmonster").recognize("recaptcha_grid", [b"x" * 200] * 9, question="/m/0k4j")
    assert result["cost_usd"] == pytest.approx(9 * 0.04 / 1000)


# ---- errors ----------------------------------------------------------------------------------------------------


@pytest.mark.asyncio
@pytest.mark.parametrize("provider", ["capmonster", "capsolver", "2captcha"])
async def test_bad_key_maps_to_auth_error(mock, make, provider):
    solver = make(provider, key="definitely-wrong-key-123")
    with pytest.raises(SolverAuthError) as info:
        await solver.solve_token("recaptcha_v2", RC_KEY, PAGE)
    assert info.value.cooldown_s and info.value.fallback
    assert "definitely-wrong-key-123" not in str(info.value) + repr(info.value)
    with pytest.raises(SolverAuthError):
        await solver.get_balance()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "provider,code,exc",
    [
        ("capmonster", "ERROR_ZERO_BALANCE", SolverBalanceError),
        ("capsolver", "ERROR_ZERO_BALANCE", SolverBalanceError),
        ("2captcha", "ERROR_ZERO_BALANCE", SolverBalanceError),
        ("capmonster", "ERROR_CAPTCHA_UNSOLVABLE", SolverUnsolvable),
        ("capsolver", "ERROR_CAPTCHA_UNSOLVABLE", SolverUnsolvable),
        ("2captcha", "ERROR_CAPTCHA_UNSOLVABLE", SolverUnsolvable),
        ("capsolver", "ERROR_SERVICE_UNAVALIABLE", SolverUnavailable),
        ("2captcha", "ERROR_NO_SLOT_AVAILABLE", SolverRateLimited),
        ("capmonster", "ERROR_RECAPTCHA_INVALID_SITEKEY", SolverBadRequest),
        ("capmonster", "ERROR_SOMETHING_NEW", SolverError),
    ],
)
async def test_error_mapping(mock, make, provider, code, exc):
    mock.fail[provider] = (code, "nope")
    with pytest.raises(exc) as info:
        await make(provider).solve_token("recaptcha_v2", RC_KEY, PAGE)
    assert info.value.code == code and info.value.provider == provider
    assert info.value.fallback is True
    if code == "ERROR_ZERO_BALANCE":
        assert info.value.cooldown_s


@pytest.mark.asyncio
async def test_capsolver_malformed_key_is_an_auth_error(mock, make):
    # Observed live: a key that is not in CapSolver's "CAP-…" format gets ERROR_INVALID_TASK_DATA "clientKey is invalid"
    # from createTask and ERROR_KEY_DOES_NOT_EXIST from getBalance.
    mock.create_fail["capsolver"] = ("ERROR_INVALID_TASK_DATA", "clientKey is invalid")
    with pytest.raises(SolverAuthError) as info:
        await make("capsolver").solve_token("turnstile", TS_KEY, PAGE)
    assert info.value.cooldown_s


@pytest.mark.asyncio
async def test_error_descriptions_are_redacted(mock, make):
    mock.create_fail["capmonster"] = ("ERROR_KEY_DOES_NOT_EXIST", f"key {mock.key} is not valid")
    with pytest.raises(SolverAuthError) as info:
        await make("capmonster").solve_token("turnstile", TS_KEY, PAGE)
    assert mock.key not in str(info.value) and "***" in str(info.value)


@pytest.mark.asyncio
async def test_unsupported_kinds(make):
    with pytest.raises(SolverUnsupported):
        await make("capsolver").solve_token("hcaptcha", "10000000-ffff-ffff-ffff-000000000001", PAGE)
    with pytest.raises(SolverUnsupported):
        await make("capsolver").solve_token("funcaptcha", "6220FF23-9856-3A6F-9FF1-A14F88123F55", PAGE)
    with pytest.raises(SolverUnsupported):
        await make("2captcha").solve_token("hcaptcha", "10000000-ffff-ffff-ffff-000000000001", PAGE)
    with pytest.raises(SolverUnsupported):
        await make("capmonster").recognize("slider", [b"a", b"b"])
    assert not make("capmonster").supports("funcaptcha")
    assert make("2captcha").supports("funcaptcha")


@pytest.mark.asyncio
async def test_missing_parameters_are_rejected_before_spend(mock, make):
    with pytest.raises(SolverBadRequest) as info:
        await make("capmonster").solve_token("geetest_v3", "gt", PAGE)
    assert info.value.fallback is False
    with pytest.raises(SolverBadRequest):
        await make("2captcha").solve_token("turnstile_challenge", TS_KEY, PAGE, action="managed")
    with pytest.raises(SolverBadRequest):
        await make("capmonster").solve_token("awswaf", "", PAGE)
    with pytest.raises(SolverBadRequest):
        await make("capsolver").recognize("slider", [b"only-one"])
    with pytest.raises(SolverBadRequest) as info:
        await make("capsolver").solve_token("turnstile", TS_KEY, PAGE, actoin="typo")
    assert "actoin" in str(info.value)
    assert mock.created() == []


@pytest.mark.asyncio
async def test_http_error_body_maps_to_unavailable(mock, make):
    mock.http_error["capsolver"] = 502
    with pytest.raises(SolverUnavailable) as info:
        await make("capsolver").solve_token("turnstile", TS_KEY, PAGE)
    assert info.value.code == "NETWORK"


@pytest.mark.asyncio
async def test_connection_refused_maps_to_unavailable():
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        port = s.getsockname()[1]
    solver = CapMonsterSolver("k" * 16, api_base=f"http://127.0.0.1:{port}")
    with pytest.raises(SolverUnavailable):
        await solver.solve_token("turnstile", TS_KEY, PAGE, timeout=3)


@pytest.mark.asyncio
async def test_deadline_bounds_polling(mock, make):
    mock.hang.add("2captcha")
    solver = make("2captcha")
    started = time.monotonic()
    with pytest.raises(SolverTimeout):
        await solver.solve_token("turnstile", TS_KEY, PAGE, deadline=time.monotonic() + 0.4)
    assert time.monotonic() - started < 1.5
    assert solver.records[-1].ok is False


@pytest.mark.asyncio
async def test_expired_deadline_sends_nothing(mock, make):
    with pytest.raises(SolverTimeout):
        await make("capmonster").solve_token("turnstile", TS_KEY, PAGE, deadline=time.monotonic() - 1)
    assert mock.requests == []


@pytest.mark.asyncio
async def test_poll_limit(mock, make):
    mock.hang.add("capmonster")
    solver = make("capmonster")
    solver.max_polls = 3
    with pytest.raises(SolverTimeout) as info:
        await solver.solve_token("turnstile", TS_KEY, PAGE, timeout=10)
    assert info.value.code == "POLL_LIMIT"
    assert len([1 for p, m, _ in mock.requests if m == "getTaskResult"]) == 3


@pytest.mark.asyncio
async def test_empty_solution_is_an_error():
    async def transport(url, payload, timeout):
        if url.endswith("/createTask"):
            return {"errorId": 0, "taskId": 7}
        return {"errorId": 0, "status": "ready", "solution": {}}

    solver = CapMonsterSolver("k" * 16, transport=transport)
    solver.token_first_poll = 0
    with pytest.raises(SolverUnavailable) as info:
        await solver.solve_token("turnstile", TS_KEY, PAGE)
    assert info.value.code == "EMPTY_SOLUTION"


@pytest.mark.asyncio
async def test_custom_transport_crash_is_unavailable():
    async def transport(url, payload, timeout):
        raise RuntimeError(f"boom {payload['clientKey']}")

    solver = CapSolverSolver("secret-key-abcdef", transport=transport)
    with pytest.raises(SolverUnavailable) as info:
        await solver.solve_token("turnstile", TS_KEY, PAGE)
    assert "secret-key-abcdef" not in str(info.value)


# ---- proxies ---------------------------------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_proxy_refused_by_default(mock, make):
    for provider in ("capmonster", "capsolver", "2captcha"):
        with pytest.raises(SolverProxyNotAllowed):
            await make(provider).solve_token("recaptcha_v2_enterprise", RC_KEY, PAGE, proxy="http://u:p@1.2.3.4:8080")
    assert mock.requests == []


@pytest.mark.asyncio
async def test_proxy_variants_when_allowed(mock, make):
    proxy = "http://user:pa%3Ass@10.0.0.2:3128"
    await make("capmonster", allow_proxy=True).solve_token("recaptcha_v2", RC_KEY, PAGE, proxy=proxy)
    cm = mock.created("capmonster")[-1]
    assert cm["type"] == "RecaptchaV2Task" and cm["proxyAddress"] == "10.0.0.2" and cm["proxyPort"] == 3128
    assert cm["proxyLogin"] == "user" and cm["proxyPassword"] == "pa:ss"

    await make("2captcha", allow_proxy=True).solve_token(
        "turnstile", TS_KEY, PAGE, proxy={"type": "socks5", "host": "10.0.0.3", "port": 1080}
    )
    tc = mock.created("2captcha")[-1]
    assert tc["type"] == "TurnstileTask" and tc["proxyType"] == "socks5" and "proxyLogin" not in tc

    await make("capsolver", allow_proxy=True).solve_token("recaptcha_v2_enterprise", RC_KEY, PAGE, proxy=proxy)
    cs = mock.created("capsolver")[-1]
    assert cs["type"] == "ReCaptchaV2EnterpriseTask" and cs["proxy"] == "http:10.0.0.2:3128:user:pa:ss"

    with pytest.raises(SolverUnsupported):
        await make("capsolver", allow_proxy=True).solve_token("turnstile", TS_KEY, PAGE, proxy=proxy)
    with pytest.raises(SolverUnsupported):
        await make("capmonster", allow_proxy=True).solve_token("recaptcha_v3", RC_KEY, PAGE, proxy=proxy)
    with pytest.raises(SolverBadRequest):
        await make("capsolver", allow_proxy=True).recognize("slider", [b"a", b"b"], proxy=proxy)


def test_proxy_spec_parsing_and_repr():
    p = ProxySpec.parse("socks5://alice:s3cret@proxy.local:1080")
    assert (p.type, p.host, p.port, p.login, p.password) == ("socks5", "proxy.local", 1080, "alice", "s3cret")
    assert "s3cret" not in repr(p) and "alice" not in repr(p)
    p = ProxySpec.parse({"type": "http", "address": "1.2.3.4", "port": "8080", "login": "a", "password": "b"})
    assert (p.host, p.port, p.login) == ("1.2.3.4", 8080, "a")
    assert ProxySpec.parse("1.2.3.4:8080").type == "http"
    for bad in ("ftp://1.2.3.4:21", "http://host-without-port", 42):
        with pytest.raises(SolverConfigError):
            ProxySpec.parse(bad)


# ---- secrets never leak ----------------------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_keys_never_logged_or_printed(mock, make, caplog):
    caplog.set_level(logging.DEBUG, logger="scrapling")
    solver = make("2captcha")
    assert mock.key not in repr(solver) and mock.key not in str(solver)
    await solver.solve_token("turnstile", TS_KEY, PAGE)
    mock.fail["2captcha"] = ("ERROR_CAPTCHA_UNSOLVABLE", f"workers failed for {mock.key}")
    with pytest.raises(SolverUnsolvable) as info:
        await solver.solve_token("turnstile", TS_KEY, PAGE)
    assert mock.key not in str(info.value)
    assert all(mock.key not in r.getMessage() for r in caplog.records)
    assert all(mock.key not in json.dumps(r.to_dict()) for r in solver.records)


def test_empty_key_is_a_config_error():
    for cls in (CapMonsterSolver, CapSolverSolver, TwoCaptchaSolver):
        with pytest.raises(SolverConfigError):
            cls("  ")


# ---- misc API --------------------------------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_balance_and_report(mock, make):
    assert await make("capsolver").get_balance() == 12.5
    solver = make("2captcha")
    token = await solver.solve_token("recaptcha_v2", RC_KEY, PAGE)
    assert await solver.report(token.task_id, correct=False) is True
    assert mock.requests[-1][1] == "reportIncorrect" and mock.requests[-1][2]["taskId"] == int(token.task_id)


def test_protocol_conformance():
    for cls in (CapMonsterSolver, CapSolverSolver, TwoCaptchaSolver):
        assert isinstance(cls("k" * 8), Solver)


def test_recaptcha_labels_and_grid_parsing():
    assert recaptcha_label_id("Select all images with a fire hydrant") == "/m/01pns0"
    assert recaptcha_label_id("Select all squares with traffic lights") == "/m/015qff"
    assert recaptcha_label_id("school buses") == "/m/02yvhj"  # the longest keyword wins over "buses"
    assert recaptcha_label_id("/m/0k4j") == "/m/0k4j"
    assert recaptcha_label_id("Select all images with lamps") is None
    assert recaptcha_label_text("/m/014xcs") == "crosswalks"
    assert (
        parse_grid("4x4") == (4, 4)
        and parse_grid(9) == (3, 3)
        and parse_grid(None) == (3, 3)
        and parse_grid((2, 5)) == (2, 5)
    )


def test_token_ttl():
    token = Token("abc", kind="recaptcha_v2", provider="x", created_at=time.monotonic() - 121)
    assert token.expired
    assert not Token("abc", kind="turnstile", provider="x").expired


def test_urllib_transport_takes_a_verifying_ssl_context():
    import ssl
    import urllib.request

    from scrapling.engines.antibot.solvers import UrllibTransport

    context = ssl.create_default_context()
    transport = UrllibTransport(ssl_context=context)
    https = [h for h in transport._opener.handlers if isinstance(h, urllib.request.HTTPSHandler)]
    assert len(https) == 1 and https[0]._context is context

    unverified = ssl.create_default_context()
    unverified.check_hostname = False
    unverified.verify_mode = ssl.CERT_NONE
    with pytest.raises(ValueError):
        UrllibTransport(ssl_context=unverified)


@pytest.mark.asyncio
async def test_solver_with_ssl_context_transport(mock, make):
    import ssl

    from scrapling.engines.antibot.solvers import UrllibTransport

    solver = make("capmonster", transport=UrllibTransport(ssl_context=ssl.create_default_context()))
    token = await solver.solve_token("turnstile", TS_KEY, PAGE)
    assert token
