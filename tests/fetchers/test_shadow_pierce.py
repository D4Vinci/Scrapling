"""Regression tests for the `pierce_shadow` option of the browser fetchers.

Two layers:
- Parsing layer (no browser): feeds real browser serializations to `Selector` and
  checks that the flattened serialization exposes shadow-DOM content while the
  plain one does not.
- Browser layer (requires a local Chrome): fetches the shadow test page with
  `pierce_shadow` on/off and verifies both the piercing behavior and the
  zero-difference default behavior.

Environment note: on machines where Playwright's sync API dependencies
(greenlet) or msgspec/curl_cffi wheels are unavailable (e.g. 32-bit Python),
pure-Python stubs are loaded from `<workspace>/tests-bench/_stubs` and the
browser tests run through the async engines.
"""

import asyncio
import inspect
import sys
from pathlib import Path

import pytest


def _ensure_local_stubs():
    """Load pure-Python dependency stubs when the real wheels are unavailable (32-bit Python etc.)."""
    missing = False
    for module in ("greenlet", "msgspec", "curl_cffi"):
        try:
            __import__(module)
        except ModuleNotFoundError:
            missing = True
            break
    if not missing:
        return
    stubs = Path(__file__).resolve().parents[3] / "tests-bench" / "_stubs"
    if stubs.is_dir() and str(stubs) not in sys.path:
        sys.path.insert(0, str(stubs))


_ensure_local_stubs()

from scrapling.engines.toolbelt.convertor import ResponseFactory  # noqa: E402
from scrapling.engines.toolbelt._shadow_pierce import SHADOW_PIERCE_JS  # noqa: E402
from scrapling.engines._browsers._validators import validate, PlaywrightConfig, StealthConfig  # noqa: E402
from scrapling.parser import Selector  # noqa: E402

FIXTURES = Path(__file__).parent / "fixtures"

# (key, data-gt, expected values) — mirrored from the T5 bench targets
TARGETS = [
    ("price", "price", ["¥1,299.00"]),
    ("site", "site", ["示例商城"]),
    ("title", "title", ["旗舰智能手机 Pro Max"]),
    ("price-shadow", "price-shadow", ["¥1,299.00"]),
    ("original-price", "original-price", ["¥1,899.00"]),
    ("sku", "sku", ["曜石黑 / 256GB"]),
    ("stock", "stock", ["库存 42 件"]),
    ("reviewer", "reviewer", ["数码老王", "匿名用户"]),
    ("score", "score", ["5 分", "4 分"]),
    ("slot-value", "slot-value", ["slot 投影值：曜石黑"]),
    ("discount", "discount", ["限时8折"]),
    ("captcha", "captcha", ["TOKEN-9F3K2"]),
    ("closed-secret", "closed-secret", ["CLOSED-SECRET-7788"]),
]

EXPECTED_FLATTENED_HITS = {
    "price", "site", "title", "price-shadow", "original-price", "sku",
    "stock", "reviewer", "score", "slot-value", "discount", "captcha",
}  # 12/13 — "closed-secret" lives in a closed shadow root and must stay unreachable
EXPECTED_PLAIN_HITS = {"price"}


def _norm(s):
    return " ".join((s or "").split())


def _hit_keys(html):
    sel = Selector(html)
    hit = set()
    for key, gt, expected in TARGETS:
        texts = [_norm(e.get_all_text(separator=" ", strip=True)) for e in sel.css(f'[data-gt="{gt}"]')]
        if all(any(_norm(exp) in t for t in texts) for exp in expected):
            hit.add(key)
    return hit


def _chrome_available():
    """Try launching the local Chrome through Playwright's async API once."""

    async def _check():
        from playwright.async_api import async_playwright

        async with async_playwright() as p:
            browser = await p.chromium.launch(channel="chrome")
            await browser.close()

    try:
        asyncio.run(_check())
        return True
    except Exception:
        return False


CHROME_AVAILABLE = _chrome_available()
needs_chrome = pytest.mark.skipif(not CHROME_AVAILABLE, reason="Local Chrome (channel='chrome') is not available")


class TestShadowPierceParsing:
    """Parsing layer — no browser needed."""

    def test_flattened_serialization_hits_shadow_targets(self):
        """The flattened serialization exposes all open-shadow targets (12/13)."""
        html = (FIXTURES / "serialized-flattened.html").read_text(encoding="utf-8")
        assert _hit_keys(html) == EXPECTED_FLATTENED_HITS

    def test_plain_serialization_misses_shadow_targets(self):
        """The plain `page.content()` serialization only exposes the light-DOM control target."""
        html = (FIXTURES / "serialized-noshadow.html").read_text(encoding="utf-8")
        assert _hit_keys(html) == EXPECTED_PLAIN_HITS

    def test_closed_shadow_root_stays_unreachable(self):
        """Closed shadow roots can't be read from JavaScript and must not leak into the flattened output."""
        import re

        html = (FIXTURES / "serialized-flattened.html").read_text(encoding="utf-8")
        html_noscript = re.sub(r"(?is)<(script|style)[^>]*>.*?</\1>", "", html)
        assert "CLOSED-SECRET-7788" not in html_noscript

    def test_pierce_shadow_defaults_to_off(self):
        """Default behavior is byte-for-byte the old path: pierce_shadow=False everywhere by default."""
        for method in ("from_playwright_response", "from_async_playwright_response"):
            param = inspect.signature(getattr(ResponseFactory, method)).parameters["pierce_shadow"]
            assert param.default is False
        assert validate({}, PlaywrightConfig).pierce_shadow is False
        assert validate({}, StealthConfig).pierce_shadow is False

    def test_pierce_shadow_validation(self):
        """The new argument is validated like the neighboring boolean flags."""
        assert validate({"pierce_shadow": True}, PlaywrightConfig).pierce_shadow is True
        assert validate({"pierce_shadow": True}, StealthConfig).pierce_shadow is True
        with pytest.raises(TypeError):
            validate({"pierce_shadow": "yes"}, PlaywrightConfig)

    def test_fallback_when_evaluate_fails(self):
        """If the piercing evaluate throws, content extraction falls back to `page.content()`."""

        class FakePage:
            def evaluate(self, js):
                assert js == SHADOW_PIERCE_JS
                raise RuntimeError("evaluate exploded")

            def content(self):
                return "<html><body>fallback-content</body></html>"

            def wait_for_timeout(self, ms):
                pass

        assert "fallback-content" in ResponseFactory._get_page_content(FakePage(), pierce_shadow=True)

    def test_fallback_when_evaluate_returns_empty(self):
        """If the piercing evaluate returns empty, content extraction falls back to `page.content()`."""

        class FakePage:
            def evaluate(self, js):
                return ""

            def content(self):
                return "<html><body>plain-content</body></html>"

            def wait_for_timeout(self, ms):
                pass

        assert "plain-content" in ResponseFactory._get_page_content(FakePage(), pierce_shadow=True)

    @pytest.mark.asyncio
    async def test_async_fallback_when_evaluate_fails(self):
        """Async engines have the same fallback guarantee."""

        class FakeAsyncPage:
            async def evaluate(self, js):
                raise RuntimeError("evaluate exploded")

            async def content(self):
                return "<html><body>async-fallback</body></html>"

            async def wait_for_timeout(self, ms):
                pass

        content = await ResponseFactory._get_async_page_content(FakeAsyncPage(), pierce_shadow=True)
        assert "async-fallback" in content


@needs_chrome
class TestShadowPierceBrowser:
    """Browser layer — needs a local Chrome. Runs through the async engines."""

    PAGE_URI = (FIXTURES / "shadow-test-page.html").as_uri()
    PLAIN_URI = (FIXTURES / "plain-page.html").as_uri()

    @pytest.mark.asyncio
    async def test_pierce_shadow_true_finds_deepest_shadow_value(self):
        """With pierce_shadow=True, the 4th-level nested shadow content is queryable."""
        from scrapling import DynamicFetcher

        response = await DynamicFetcher.async_fetch(self.PAGE_URI, pierce_shadow=True, real_chrome=True)
        assert response.status == 200
        discount = response.css('[data-gt="discount"]')
        assert discount, "pierce_shadow=True should expose the deepest (4th level) shadow element"
        assert "限时8折" in _norm(discount[0].get_all_text(separator=" ", strip=True))

    @pytest.mark.asyncio
    async def test_pierce_shadow_default_and_false_miss_shadow_content(self):
        """Default/False keeps the old blind spot: the deepest shadow value is NOT reachable."""
        from scrapling import DynamicFetcher

        for kwargs in ({}, {"pierce_shadow": False}):
            response = await DynamicFetcher.async_fetch(self.PAGE_URI, real_chrome=True, **kwargs)
            assert response.status == 200
            assert not response.css('[data-gt="discount"]')

    @pytest.mark.asyncio
    async def test_pierce_shadow_no_shadow_page_parity(self):
        """Zero-difference regression: on a page without shadow DOM, True and False return equal content."""
        from scrapling import DynamicFetcher

        response_on = await DynamicFetcher.async_fetch(self.PLAIN_URI, pierce_shadow=True, real_chrome=True)
        response_off = await DynamicFetcher.async_fetch(self.PLAIN_URI, pierce_shadow=False, real_chrome=True)
        assert response_on.status == 200 == response_off.status
        assert response_on.body == response_off.body
        plain_value = response_on.css('[data-gt="plain-value"]')
        assert plain_value
        assert "无 Shadow 页面内容" in _norm(plain_value[0].get_all_text(separator=" ", strip=True))

    @pytest.mark.asyncio
    async def test_stealthy_pierce_shadow_true(self):
        """StealthyFetcher (isolated execution context) must pierce shadow DOM the same way."""
        from scrapling import StealthyFetcher

        response = await StealthyFetcher.async_fetch(self.PAGE_URI, pierce_shadow=True, real_chrome=True)
        assert response.status == 200
        discount = response.css('[data-gt="discount"]')
        assert discount, "StealthyFetcher with pierce_shadow=True should expose the deepest shadow element"
        assert "限时8折" in _norm(discount[0].get_all_text(separator=" ", strip=True))
