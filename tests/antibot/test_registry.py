"""The handler registry and the detection entry points."""

import inspect

import pytest

import scrapling.engines.antibot as antibot
from scrapling.engines.antibot import HANDLERS, VENDORS, Signal, detect, detect_all, get, normalize_vendor


def test_detection_order():
    assert VENDORS == ("cloudflare", "aws_waf", "datadome", "kasada", "perimeterx", "akamai", "imperva")


@pytest.mark.parametrize("handler", HANDLERS, ids=VENDORS)
def test_handlers_follow_the_protocol(handler):
    assert isinstance(handler.vendor, str) and handler.vendor
    assert callable(handler.detect)
    assert inspect.iscoroutinefunction(handler.solve)
    params = inspect.signature(handler.solve).parameters
    for name in ("page", "det", "deadline", "solver", "log"):
        assert name in params
    for name in ("deadline", "solver", "log"):
        assert params[name].kind is inspect.Parameter.KEYWORD_ONLY


@pytest.mark.parametrize(
    "name, vendor",
    [
        ("cloudflare", "cloudflare"),
        ("CF", "cloudflare"),
        ("awswaf", "aws_waf"),
        ("aws-waf", "aws_waf"),
        ("aws_waf", "aws_waf"),
        ("DataDome", "datadome"),
        ("px", "perimeterx"),
        ("HUMAN", "perimeterx"),
        ("incapsula", "imperva"),
        ("akamai", "akamai"),
        ("kasada", "kasada"),
    ],
)
def test_get_accepts_aliases(name, vendor):
    assert normalize_vendor(name) == vendor
    assert get(name).vendor == vendor


def test_get_unknown_vendor():
    assert get("nope") is None
    assert get("") is None


def test_no_detection_on_an_empty_signal():
    assert detect(Signal("https://example.com/", 200, {}, {}, "", [])) is None
    assert detect_all(Signal("", None)) == []


def test_detect_returns_the_first_of_detect_all():
    s = Signal(
        "https://www.example.com/",
        403,
        {"cf-mitigated": "challenge", "server": "cloudflare"},
        {},
        "<html><body><script>var dd={'rt':'c','host':'geo.captcha-delivery.com'}</script><div id=\"px-captcha\"></div></body></html>",
        [],
    )
    everything = detect_all(s)
    assert [d.vendor for d in everything] == ["cloudflare", "datadome", "perimeterx"]
    assert detect(s) == everything[0]


def test_package_exports():
    for name in ("Signal", "Detection", "SolveResult", "Handler", "detect", "detect_all", "get", "HANDLERS", "page_signal"):
        assert hasattr(antibot, name)
