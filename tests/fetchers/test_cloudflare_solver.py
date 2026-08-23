from unittest.mock import AsyncMock, MagicMock

import pytest
from patchright._impl._errors import Error as PatchrightError
from playwright._impl._errors import Error as PlaywrightError

from scrapling.engines.toolbelt.convertor import ResponseFactory
from scrapling.engines._browsers._stealth import StealthySession, AsyncStealthySession, __CF_MAX_SOLVE_ATTEMPTS__

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


class TestPageContentRetries:
    @pytest.mark.parametrize("error_class", [PatchrightError, PlaywrightError])
    def test_sync_content_errors_are_retried(self, error_class):
        """Both patchright and playwright errors must trigger the retry workaround, not crash"""
        page = MagicMock()
        page.content.side_effect = [error_class("Page.content: page is navigating"), CLEAN_PAGE]

        assert ResponseFactory._get_page_content(page) == CLEAN_PAGE
        assert page.wait_for_timeout.call_count == 1

    @pytest.mark.asyncio
    @pytest.mark.parametrize("error_class", [PatchrightError, PlaywrightError])
    async def test_async_content_errors_are_retried(self, error_class):
        page = MagicMock()
        page.content = AsyncMock(side_effect=[error_class("Page.content: page is navigating"), CLEAN_PAGE])
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

    def test_dynamic_session_gets_the_same_flags(self):
        from scrapling.engines._browsers._controllers import DynamicSession

        session = DynamicSession(locale="en-GB")
        assert "--lang=en-GB" in session._browser_options["args"]
        assert "--accept-lang=en-GB,en" in session._browser_options["args"]
        assert "locale" not in session._context_options
