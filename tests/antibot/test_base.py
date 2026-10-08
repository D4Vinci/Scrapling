"""The shared anti-bot types: Signal normalisation, its predicates and the small helpers handlers use."""

from time import monotonic
from types import SimpleNamespace

import pytest

from scrapling.engines.antibot.base import (
    MAX_HTML_CHARS,
    Detection,
    Signal,
    SolveResult,
    cookie_domain_matches,
    host_matches,
    page_signal,
    remaining,
    visible_text,
)


class TestSignal:
    def test_headers_are_lower_cased_and_lists_joined(self):
        s = Signal(
            url="https://www.example.com/",
            status="403",
            headers={"X-DataDome": "protected", "Set-Cookie": ["a=1", "b=2"], "Server": "cloudflare"},
            cookies={"datadome": "v"},
            html="",
            frame_urls=[],
        )
        assert s.status == 403
        assert s.headers == {"x-datadome": "protected", "set-cookie": "a=1, b=2", "server": "cloudflare"}
        assert s.header("SERVER") == "cloudflare"
        assert s.header("missing") == ""

    def test_repeated_header_names_are_merged(self):
        s = Signal("https://example.com/", 200, {"Via": "1.1 a", "via": "1.1 b"}, {}, "", [])
        assert s.headers["via"] == "1.1 a, 1.1 b"

    def test_html_is_capped_and_frames_cleaned(self):
        s = Signal("https://example.com/", None, {}, {}, "x" * (MAX_HTML_CHARS + 10), ["", None, "https://a.test/"])
        assert len(s.html) == MAX_HTML_CHARS
        assert s.frame_urls == ["https://a.test/"]
        assert s.status is None

    def test_none_fields_become_empty(self):
        s = Signal(url=None, status=None, headers=None, cookies=None, html=None, frame_urls=None)
        assert (s.url, s.headers, s.cookies, s.html, s.frame_urls) == ("", {}, {}, "", [])
        assert s.text == "" and s.title == "" and s.host == ""

    def test_derived_views(self):
        s = Signal(
            "https://WWW.Example.com/path",
            200,
            {},
            {"_abck": "x", "incap_ses_1_2": "y"},
            "<html><head><title> Just  a\nmoment&hellip; </title></head><body><p>Hi &amp; bye</p></body></html>",
            [],
        )
        assert s.title == "just a moment…"
        assert s.text == "Hi & bye"
        assert s.host == "www.example.com"
        assert s.has("<p>hi") and not s.has("absent")
        assert s.has_cookie("_abck") and not s.has_cookie("bm_sz")
        assert s.has_cookie_prefix("incap_ses_") and not s.has_cookie_prefix("visid_incap_")

    def test_status_predicates(self):
        assert Signal("u", 403).status_in(403, 429)
        assert not Signal("u", 200).status_in(403)
        assert Signal("u", None).status_in(403, unknown=True)
        assert not Signal("u", None).status_in(403)
        assert Signal("u", 503).is_error and not Signal("u", 302).is_error and not Signal("u", None).is_error

    def test_gate(self):
        assert Signal("u", 200, html="<body><p>short</p></body>").gate()
        assert not Signal("u", 200, html="<body>" + "word " * 1000 + "</body>").gate()
        assert not Signal("u", 200, html="<body>" + "w" * 300 + "</body>").gate(256)

    def test_frames_on_matches_hosts_not_substrings(self):
        s = Signal(
            "https://example.com/",
            200,
            frame_urls=[
                "https://geo.captcha-delivery.com/captcha/?x=1",
                "https://evil.test/?u=captcha-delivery.com",
                "https://captcha-delivery.com.evil.test/",
            ],
        )
        assert s.frames_on("captcha-delivery.com") == ["https://geo.captcha-delivery.com/captcha/?x=1"]

    def test_vendor_markers(self):
        s = Signal("u", 403, html="<div id='px-captcha'></div>")
        assert s.marked_by("perimeterx")
        assert s.marked_by_other("akamai")
        assert not s.marked_by_other("perimeterx")
        assert not Signal("u", 403, html="<p>plain</p>").marked_by_other("akamai")


def test_visible_text_drops_non_visible_parts():
    html = (
        "<html><head><title>T</title><style>p{}</style></head><body><!-- c --><script>var a = '<p>x</p>';</script>"
        "<noscript>Enable JavaScript</noscript><template><p>t</p></template><svg><text>s</text></svg>"
        "<p>Visible&nbsp;text</p>\n\n<div>more</div></body></html>"
    )
    assert visible_text(html) == "Visible text more"  # &nbsp; collapses like any other space
    assert visible_text("") == ""


@pytest.mark.parametrize(
    "url, domains, expected",
    [
        ("https://geo.captcha-delivery.com/x", ("captcha-delivery.com",), True),
        ("https://captcha-delivery.com/", ("captcha-delivery.com",), True),
        ("https://captcha-delivery.com./", ("captcha-delivery.com",), True),
        ("http://a.b.example.com/", ("example.com", "other.test"), True),
        ("https://notcaptcha-delivery.com/", ("captcha-delivery.com",), False),
        ("https://captcha-delivery.com.evil.test/", ("captcha-delivery.com",), False),
        ("https://evil.test/?captcha-delivery.com", ("captcha-delivery.com",), False),
        ("javascript:alert(1)//captcha-delivery.com", ("captcha-delivery.com",), False),
        ("about:blank", ("captcha-delivery.com",), False),
        ("https://[::1", ("captcha-delivery.com",), False),
    ],
)
def test_host_matches(url, domains, expected):
    assert host_matches(url, *domains) is expected


@pytest.mark.parametrize(
    "host, domain, expected",
    [
        ("www.example.com", ".example.com", True),
        ("www.example.com", "www.example.com", True),
        ("example.com", ".example.com", True),
        ("www.example.com", "other.com", False),
        ("badexample.com", "example.com", False),
        ("", "example.com", False),
        ("example.com", "", False),
    ],
)
def test_cookie_domain_matches(host, domain, expected):
    assert cookie_domain_matches(host, domain) is expected


def test_remaining_is_never_negative():
    assert remaining(monotonic() - 5) == 0.0
    assert 9 < remaining(monotonic() + 10) <= 10


def test_result_types_have_safe_defaults():
    a, b = SolveResult(False, "timeout"), SolveResult(True, "solved")
    a.cookies.append("x")
    assert b.cookies == [] and b.used_solver is None
    d1, d2 = Detection("akamai", "block", "akamai.block"), Detection("akamai", "block", "akamai.block")
    d1.details["x"] = 1
    assert d2.details == {}


class FakePage:
    def __init__(self, url, html, cookies, frames, fail=False):
        self.url = url
        self._html = html
        self._cookies = cookies
        self._fail = fail
        self.main_frame = SimpleNamespace(url=url)
        self.frames = [self.main_frame] + [SimpleNamespace(url=u) for u in frames]
        self.context = SimpleNamespace(cookies=self._read_cookies)

    async def content(self):
        if self._fail:
            raise RuntimeError("Execution context was destroyed")
        return self._html

    async def _read_cookies(self):
        if self._fail:
            raise RuntimeError("Target closed")
        return self._cookies


@pytest.mark.asyncio
async def test_page_signal_reads_the_page_and_filters_cookies():
    page = FakePage(
        "https://www.example.com/a",
        "<html><body>hello</body></html>",
        [
            {"name": "datadome", "value": "v1", "domain": ".example.com"},
            {"name": "own", "value": "v2", "domain": "www.example.com"},
            {"name": "other", "value": "v3", "domain": ".other.com"},
            {"name": "sub", "value": "v4", "domain": "api.example.com"},
        ],
        ["https://geo.captcha-delivery.com/captcha/"],
    )
    s = await page_signal(page, status=403, headers={"X-DD-B": "3"})
    assert s.url == "https://www.example.com/a" and s.status == 403
    assert s.headers == {"x-dd-b": "3"}
    assert s.cookies == {"datadome": "v1", "own": "v2"}
    assert s.html == "<html><body>hello</body></html>"
    assert s.frame_urls == ["https://geo.captcha-delivery.com/captcha/"]


@pytest.mark.asyncio
async def test_page_signal_survives_a_navigating_page():
    page = FakePage("https://www.example.com/", "", [], [], fail=True)
    s = await page_signal(page)
    assert s.html == "" and s.cookies == {} and s.status is None
