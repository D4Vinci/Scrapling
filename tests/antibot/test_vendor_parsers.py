"""The small parsers the detectors use to hand vendor parameters to the solvers."""

import pytest

from scrapling.engines.antibot.akamai import abck_state, parse_sec_cpt
from scrapling.engines.antibot.awswaf import parse_aws_challenge
from scrapling.engines.antibot.cloudflare import challenge_type, turnstile_params
from scrapling.engines.antibot.datadome import dd_frame_kind, dd_header_action, is_dd_frame, parse_dd_object
from scrapling.engines.antibot.kasada import kasada_script


class TestDataDome:
    def test_parse_dd_object(self):
        html = (
            "<script>var dd={'rt':'c','cid':'AHrlqA~~','hsh':'0B4B','t':'fe','qp':'','s':2089,'e':'aa11',"
            "'host':'geo.captcha-delivery.com','cookie':'c-v'}</script>"
        )
        assert parse_dd_object(html) == {
            "rt": "c",
            "cid": "AHrlqA~~",
            "hsh": "0B4B",
            "t": "fe",
            "qp": "",
            "s": "2089",
            "e": "aa11",
            "host": "geo.captcha-delivery.com",
            "cookie": "c-v",
        }

    def test_parse_dd_object_with_spaces_and_double_quotes(self):
        assert parse_dd_object('var dd = {"rt": "i", "t": "bv"}') == {"rt": "i", "t": "bv"}

    def test_parse_dd_object_absent(self):
        assert parse_dd_object("<p>add a dd entry</p>") is None
        assert parse_dd_object("") is None

    @pytest.mark.parametrize(
        "value, expected",
        [("1", (1, False)), ("2", (2, False)), ("3", (3, False)), ("259", (3, True)), (" 257 ", (1, True)), ("", (0, False)), ("x3", (0, False)), ("12345678", (0, False))],
    )
    def test_header_action(self, value, expected):
        assert dd_header_action(value) == expected

    @pytest.mark.parametrize(
        "url, kind",
        [
            ("https://geo.captcha-delivery.com/captcha/?initialCid=a&t=fe", "captcha"),
            ("https://geo.captcha-delivery.com/interstitial/?initialCid=a", "device_check"),
            ("https://geo.captcha-delivery.com/captcha/?initialCid=a&t=bv", "ban"),
            ("https://ct.captcha-delivery.com/c.js", None),
            ("http://geo.captcha-delivery.com/captcha/", None),
            ("https://geo.captcha-delivery.com.evil.test/captcha/", None),
            ("https://evil.test/captcha/?h=captcha-delivery.com", None),
        ],
    )
    def test_frame_kind(self, url, kind):
        assert dd_frame_kind(url) == kind
        assert is_dd_frame(url) is (kind is not None or url.startswith("https://ct."))


class TestAkamai:
    @pytest.mark.parametrize(
        "value, state",
        [("A~0~YAAQ~-1~-1", "valid"), ("A~-1~YAAQ~-1~-1", "invalid"), ("opaque", "unknown"), ("", "missing"), (None, "missing")],
    )
    def test_abck_state(self, value, state):
        assert abck_state(value) == state

    def test_parse_sec_cpt_json(self):
        body = '{"sec-cp-challenge":"true","provider":"crypto","branding_url_content":"/_sec/cp_challenge/crypto_message-4-3.htm","chlg_duration":30}'
        assert parse_sec_cpt(body) == {
            "provider": "crypto",
            "branding_url_content": "/_sec/cp_challenge/crypto_message-4-3.htm",
            "chlg_duration": 30,
        }

    def test_parse_sec_cpt_html(self):
        html = '<script>var cfg = {"provider": "behavioral", "chlg_duration": "5"};</script>'
        assert parse_sec_cpt(html) == {"provider": "behavioral", "chlg_duration": 5}
        assert parse_sec_cpt("{not json") == {}
        assert parse_sec_cpt("") == {}


class TestAwsWaf:
    def test_parse_challenge_page(self):
        html = (
            '<script>window.gokuProps = {"key":"AQID","iv":"CgAH","context":"rFz0"};</script>'
            '<script src="https://a1.b2.us-east-1.token.awswaf.com/a1/b2/challenge.js"></script>'
            "<script>AwsWafCaptcha.renderCaptcha(c, {apiKey: 'k3yk3yk3yk3y', onSuccess: f});</script>"
            '<script src="https://a1.eu-central-1.captcha-sdk.awswaf.com/a1/captcha.js"></script>'
        )
        assert parse_aws_challenge(html) == {
            "aws_key": "AQID",
            "aws_iv": "CgAH",
            "aws_context": "rFz0",
            "aws_challenge_script": "https://a1.b2.us-east-1.token.awswaf.com/a1/b2/challenge.js",
            "aws_captcha_script": "https://a1.eu-central-1.captcha-sdk.awswaf.com/a1/captcha.js",
            "aws_api_key": "k3yk3yk3yk3y",
        }

    def test_parse_nothing(self):
        assert parse_aws_challenge("<p>hello</p>") == {}


class TestKasada:
    def test_script_url(self):
        html = '<script src="/149e9513-01fa-4fb0-aad4-566afd725d1b/2d206a39-8ed7-437e-a3be-862e0f06eea3/ips.js?a=1&amp;b=2"></script>'
        assert kasada_script(html) == "/149e9513-01fa-4fb0-aad4-566afd725d1b/2d206a39-8ed7-437e-a3be-862e0f06eea3/ips.js?a=1&b=2"

    def test_absolute_script_url(self):
        html = "<script src='https://x.example.com/149e9513-01fa-4fb0-aad4-566afd725d1b/2d206a39-8ed7-437e-a3be-862e0f06eea3/p.js'>"
        assert kasada_script(html).startswith("https://x.example.com/149e9513")

    def test_no_script(self):
        assert kasada_script("<script src='/static/app.js'></script>") is None


class TestCloudflare:
    @pytest.mark.parametrize(
        "html, ctype",
        [
            ("cType: 'managed'", "managed"),
            ("cType:'interactive'", "interactive"),
            ("cType: 'non-interactive'", "non-interactive"),
            ("cType: 'something-new'", None),
            ("no challenge", None),
        ],
    )
    def test_challenge_type(self, html, ctype):
        assert challenge_type(html) == ctype

    def test_turnstile_params(self):
        html = (
            '<div class="x"><div class="cf-turnstile big" data-sitekey="0x4AAAA" data-action="login" data-cdata="c1" '
            'data-callback="done"></div><div data-sitekey="other"></div>'
        )
        assert turnstile_params(html) == {"sitekey": "0x4AAAA", "action": "login", "cdata": "c1", "callback": "done"}
        assert turnstile_params("<p>no widget</p>") == {}
