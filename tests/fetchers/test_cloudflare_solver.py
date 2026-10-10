from unittest.mock import AsyncMock, MagicMock

import pytest
from patchright._impl._errors import Error as PatchrightError

from scrapling.engines.toolbelt.convertor import ResponseFactory
from scrapling.engines._browsers import _stealth
from scrapling.engines._browsers._stealth import (
    StealthySession,
    AsyncStealthySession,
    __CF_MAX_SOLVE_ATTEMPTS__,
    __CF_SOLVE_TIMEOUT__,
)

FRENCH_CHALLENGE = (
    "<html><head><title>Un instant…</title></head><body><script>cType: 'interactive'</script></body></html>"
)
CLEAN_PAGE = "<html><head><title>La Redoute</title></head><body>content</body></html>"


class TestChallengeCleared:
    def test_localized_challenge_is_not_cleared(self):
        """The check must catch the challenge markers no matter what language the page is displayed with"""
        assert StealthySession._challenge_cleared(FRENCH_CHALLENGE, "interactive") is False

    def test_clean_page_is_cleared(self):
        assert StealthySession._challenge_cleared(CLEAN_PAGE, "interactive") is True

    def test_embedded_is_always_cleared(self):
        """Embedded widgets stay in the page after solving, so they are always reported as cleared"""
        content = '<script src="https://challenges.cloudflare.com/turnstile/v0/api.js"></script>'
        assert StealthySession._challenge_cleared(content, "embedded") is True


def _make_sync_page():
    page = MagicMock()
    page.frame.return_value = None
    page.locator.return_value.last.bounding_box.return_value = {"x": 100, "y": 200}
    return page


def _make_invisible_iframe():
    """A Turnstile frame whose widget never becomes visible and never reports a box"""
    iframe = MagicMock()
    iframe.frame_element.return_value.is_visible.return_value = False
    iframe.frame_element.return_value.bounding_box.return_value = None
    return iframe


def _make_async_invisible_iframe():
    """The awaitable twin of `_make_invisible_iframe`"""
    iframe = MagicMock()
    iframe.frame_element = AsyncMock()
    iframe.frame_element.return_value.is_visible = AsyncMock(return_value=False)
    iframe.frame_element.return_value.bounding_box = AsyncMock(return_value=None)
    return iframe


class TestSyncSolver:
    def _solver_setup(self, monkeypatch, content_state):
        monkeypatch.setattr(ResponseFactory, "_get_page_content", staticmethod(lambda page: content_state["content"]))
        monkeypatch.setattr(StealthySession, "_wait_for_networkidle", lambda self, page, timeout=None: None)
        monkeypatch.setattr(
            StealthySession, "_wait_for_page_stability", lambda self, page, load_dom, network_idle: None
        )
        return object.__new__(StealthySession)

    def test_solver_clicks_localized_challenge(self, monkeypatch):
        """A localized challenge page must still be detected, clicked, and confirmed as solved"""
        state = {"content": FRENCH_CHALLENGE}
        session = self._solver_setup(monkeypatch, state)
        page = _make_sync_page()
        page.mouse.click.side_effect = lambda *args, **kwargs: state.update(content=CLEAN_PAGE)

        assert session._cloudflare_solver(page) is None
        assert page.mouse.click.call_count == 1
        x, y = page.mouse.click.call_args.args
        assert 126 <= x <= 128
        assert 225 <= y <= 227

    def test_solver_stops_after_max_attempts(self, monkeypatch):
        """A challenge that never clears must stop after the attempts cap instead of retrying forever"""
        state = {"content": FRENCH_CHALLENGE}
        session = self._solver_setup(monkeypatch, state)
        page = _make_sync_page()

        assert session._cloudflare_solver(page) is None
        assert page.mouse.click.call_count == __CF_MAX_SOLVE_ATTEMPTS__


class TestAsyncSolver:
    def _solver_setup(self, monkeypatch, content_state):
        async def content(page):
            return content_state["content"]

        monkeypatch.setattr(ResponseFactory, "_get_async_page_content", staticmethod(content))
        monkeypatch.setattr(AsyncStealthySession, "_wait_for_networkidle", AsyncMock())
        monkeypatch.setattr(AsyncStealthySession, "_wait_for_page_stability", AsyncMock())
        return object.__new__(AsyncStealthySession)

    @pytest.mark.asyncio
    async def test_solver_clicks_localized_challenge(self, monkeypatch):
        state = {"content": FRENCH_CHALLENGE}
        session = self._solver_setup(monkeypatch, state)
        page = MagicMock()
        page.frame.return_value = None
        page.wait_for_timeout = AsyncMock()
        page.wait_for_load_state = AsyncMock()
        page.locator.return_value.last.bounding_box = AsyncMock(return_value={"x": 100, "y": 200})
        page.mouse.click = AsyncMock(side_effect=lambda *args, **kwargs: state.update(content=CLEAN_PAGE))

        assert await session._cloudflare_solver(page) is None
        assert page.mouse.click.await_count == 1
        x, y = page.mouse.click.await_args.args
        assert 126 <= x <= 128
        assert 225 <= y <= 227

    @pytest.mark.asyncio
    async def test_solver_stops_after_max_attempts(self, monkeypatch):
        state = {"content": FRENCH_CHALLENGE}
        session = self._solver_setup(monkeypatch, state)
        page = MagicMock()
        page.frame.return_value = None
        page.wait_for_timeout = AsyncMock()
        page.wait_for_load_state = AsyncMock()
        page.locator.return_value.last.bounding_box = AsyncMock(return_value={"x": 100, "y": 200})
        page.mouse.click = AsyncMock()

        assert await session._cloudflare_solver(page) is None
        assert page.mouse.click.await_count == __CF_MAX_SOLVE_ATTEMPTS__


class TestSolveBudget:
    """A solve must never outlive the `timeout` the fetch call asked for"""

    @pytest.fixture
    def clock(self, monkeypatch):
        """A monotonic clock that only moves while the fake page is waiting, so the tests stay instant"""
        state = {"now": 1000.0}

        def wait(milliseconds):
            state["now"] += milliseconds / 1000
            if state["now"] > 1400:
                raise AssertionError("The solve kept waiting after its deadline instead of giving up")

        monkeypatch.setattr(_stealth, "monotonic", lambda: state["now"])
        return state, wait

    def _setup(self, monkeypatch, content):
        monkeypatch.setattr(ResponseFactory, "_get_page_content", staticmethod(lambda page: content))
        monkeypatch.setattr(StealthySession, "_wait_for_networkidle", lambda self, page, timeout=None: None)
        monkeypatch.setattr(
            StealthySession, "_wait_for_page_stability", lambda self, page, load_dom, network_idle: None
        )
        return object.__new__(StealthySession)

    def _setup_async(self, monkeypatch, content):
        async def page_content(page):
            return content

        monkeypatch.setattr(ResponseFactory, "_get_async_page_content", staticmethod(page_content))
        monkeypatch.setattr(AsyncStealthySession, "_wait_for_networkidle", AsyncMock())
        monkeypatch.setattr(AsyncStealthySession, "_wait_for_page_stability", AsyncMock())
        return object.__new__(AsyncStealthySession)

    def test_invisible_iframe_stops_at_the_deadline(self, monkeypatch, clock):
        """A widget iframe that never turns visible must not spin past the deadline"""
        state, wait = clock
        session = self._setup(monkeypatch, FRENCH_CHALLENGE)
        page = _make_sync_page()
        page.wait_for_timeout.side_effect = wait
        page.locator.return_value.last.bounding_box.return_value = None
        page.frame.return_value = _make_invisible_iframe()

        assert session._cloudflare_solver(page, _deadline=state["now"] + 1.5) is None
        assert state["now"] == 1001.5
        assert page.mouse.click.call_count == 0

    def test_never_matching_locator_gets_a_bounded_timeout(self, monkeypatch, clock):
        """The widget locator that never matches must not inherit the browser's default timeout"""
        state, wait = clock
        session = self._setup(monkeypatch, FRENCH_CHALLENGE)
        page = _make_sync_page()
        page.wait_for_timeout.side_effect = wait
        page.locator.return_value.last.bounding_box.return_value = None

        assert session._cloudflare_solver(page, _deadline=state["now"] + 1.5) is None
        assert page.locator.return_value.last.bounding_box.call_args.kwargs["timeout"] <= 1500

    def test_exhausted_deadline_leaves_the_page_untouched(self, monkeypatch, clock):
        """A deadline that is already spent must return the page as is before touching the browser"""
        state, _ = clock
        session = self._setup(monkeypatch, FRENCH_CHALLENGE)
        page = _make_sync_page()

        assert session._cloudflare_solver(page, _deadline=state["now"] - 1) is None
        assert page.frame.call_count == 0
        assert page.locator.call_count == 0

    def test_missing_deadline_falls_back_to_the_default_budget(self, monkeypatch, clock):
        """Without a deadline the solve budgets itself with the default solve timeout"""
        state, wait = clock
        session = self._setup(monkeypatch, FRENCH_CHALLENGE)
        page = _make_sync_page()
        page.wait_for_timeout.side_effect = wait
        page.locator.return_value.last.bounding_box.return_value = None

        assert session._cloudflare_solver(page) is None
        assert state["now"] == 1000 + __CF_SOLVE_TIMEOUT__ / 1000

    @pytest.mark.asyncio
    async def test_async_invisible_iframe_stops_at_the_deadline(self, monkeypatch, clock):
        state, wait = clock
        session = self._setup_async(monkeypatch, FRENCH_CHALLENGE)
        page = MagicMock()
        page.wait_for_timeout = AsyncMock(side_effect=wait)
        page.wait_for_load_state = AsyncMock()
        page.mouse.click = AsyncMock()
        page.locator.return_value.last.bounding_box = AsyncMock(return_value=None)
        page.frame.return_value = _make_async_invisible_iframe()

        assert await session._cloudflare_solver(page, _deadline=state["now"] + 1.5) is None
        assert state["now"] == 1001.5
        assert page.mouse.click.await_count == 0

    @pytest.mark.asyncio
    async def test_async_never_matching_locator_gets_a_bounded_timeout(self, monkeypatch, clock):
        state, wait = clock
        session = self._setup_async(monkeypatch, FRENCH_CHALLENGE)
        page = MagicMock()
        page.frame.return_value = None
        page.wait_for_timeout = AsyncMock(side_effect=wait)
        page.wait_for_load_state = AsyncMock()
        page.locator.return_value.last.bounding_box = AsyncMock(return_value=None)

        assert await session._cloudflare_solver(page, _deadline=state["now"] + 1.5) is None
        assert page.locator.return_value.last.bounding_box.await_args.kwargs["timeout"] <= 1500


class TestPageContentRetries:
    def test_sync_content_errors_are_retried(self):
        """Patchright errors must trigger the retry workaround"""
        page = MagicMock()
        page.content.side_effect = [PatchrightError("Page.content: page is navigating"), CLEAN_PAGE]

        assert ResponseFactory._get_page_content(page) == CLEAN_PAGE
        assert page.wait_for_timeout.call_count == 1

    @pytest.mark.asyncio
    async def test_async_content_errors_are_retried(self):
        page = MagicMock()
        page.content = AsyncMock(side_effect=[PatchrightError("Page.content: page is navigating"), CLEAN_PAGE])
        page.wait_for_timeout = AsyncMock()

        assert await ResponseFactory._get_async_page_content(page) == CLEAN_PAGE
        assert page.wait_for_timeout.await_count == 1

    def test_sync_content_gives_up_after_max_retries(self):
        page = MagicMock()
        page.content.side_effect = PatchrightError("Page.content: page is navigating")

        with pytest.raises(RuntimeError, match="Failed to retrieve the page content"):
            ResponseFactory._get_page_content(page, max_retries=3)
        assert page.content.call_count == 3


class TestLocaleLaunchFlags:
    def test_locale_becomes_launch_flags(self):
        """The locale must be set browser-wide via launch flags, not the detectable context override"""
        session = StealthySession(locale="fr-FR")
        assert "--lang=fr-FR" in session._browser_options["args"]
        assert "--accept-lang=fr-FR,fr" in session._browser_options["args"]
        assert "locale" not in session._context_options

    def test_no_locale_adds_no_flags(self):
        session = StealthySession()
        assert not [f for f in session._browser_options["args"] if f.startswith(("--lang=", "--accept-lang="))]
        assert "locale" not in session._context_options

    def test_cdp_url_keeps_context_locale(self):
        """Remote browsers can't take launch flags, so the context option is the best effort left"""
        session = StealthySession(locale="fr-FR", cdp_url="ws://127.0.0.1:9222/devtools/browser/x")
        assert session._context_options.get("locale") == "fr-FR"
