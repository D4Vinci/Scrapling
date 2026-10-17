import asyncio
from unittest.mock import AsyncMock, MagicMock

import pytest
from patchright.sync_api import Error as PatchrightError, TimeoutError as PlaywrightTimeoutError

from scrapling.core._types import Any
from scrapling.engines._browsers import _stealth


CHALLENGE = "<script>window._cf_chl_opt = {cType: 'interactive'};</script>"
CLEAN = "<p>Done</p>"


def call(value, asynchronous):
    return asyncio.run(value) if asynchronous else value


def setup(monkeypatch, asynchronous, matches):
    session_type = _stealth.AsyncStealthySession if asynchronous else _stealth.StealthySession
    mock = AsyncMock if asynchronous else MagicMock
    monkeypatch.setattr(session_type, "_wait_for_networkidle", mock())
    monkeypatch.setattr(session_type, "_wait_for_page_stability", mock())
    session = object.__new__(session_type)
    state: dict[str, Any] = {"content": CHALLENGE, "elapsed": 0.0}
    page, element = MagicMock(), MagicMock()

    def sleep(milliseconds):
        state["elapsed"] += milliseconds
        assert state["elapsed"] <= 60_000, "Solver did not stop polling"

    page.content = mock(side_effect=lambda: state["content"])
    page.wait_for_timeout = mock(side_effect=sleep)
    page.wait_for_load_state = mock()
    page.mouse.click = mock(side_effect=lambda *args, **kwargs: state.update(content=CLEAN))
    page.frame.return_value = None
    element.bounding_box = mock(return_value={"x": 100, "y": 200})
    element.dispose = mock()
    page.locator.return_value.last.element_handles = mock(side_effect=matches(element, state))
    return session, page, element, state


@pytest.mark.parametrize("asynchronous", [False, True])
def test_challenge_clears_during_absent_widget_lookup(monkeypatch, asynchronous):
    def matches(element, state):
        def absent():
            state["content"] = CLEAN
            return []

        return absent

    session, page, element, state = setup(monkeypatch, asynchronous, matches)

    def auto_wait():
        state.update(content=CLEAN, elapsed=state["elapsed"] + 60_000)
        raise PlaywrightTimeoutError("Waiting for missing locator")

    mock = AsyncMock if asynchronous else MagicMock
    page.locator.return_value.last.bounding_box = mock(side_effect=auto_wait)
    assert call(session._cloudflare_solver(page), asynchronous) is None
    assert state["elapsed"] == 11_000
    page.locator.return_value.last.bounding_box.assert_not_called()
    page.mouse.click.assert_not_called()


@pytest.mark.parametrize("asynchronous", [False, True])
def test_permanently_missing_widget_uses_existing_attempt_cap(monkeypatch, asynchronous):
    session, page, element, state = setup(monkeypatch, asynchronous, lambda element, state: lambda: [])
    assert call(session._cloudflare_solver(page), asynchronous) is None
    assert page.locator.return_value.last.element_handles.call_count == _stealth.__CF_MAX_SOLVE_ATTEMPTS__
    assert state["elapsed"] == 33_000
    page.mouse.click.assert_not_called()


@pytest.mark.parametrize("asynchronous", [False, True])
def test_late_widget_is_clicked_on_next_attempt(monkeypatch, asynchronous):
    session, page, element, state = setup(monkeypatch, asynchronous, lambda element, state: [[], [element]])
    assert call(session._cloudflare_solver(page), asynchronous) is None
    assert page.locator.return_value.last.element_handles.call_count == 2
    assert page.mouse.click.call_count == 1
    element.dispose.assert_called_once()


@pytest.mark.parametrize("asynchronous", [False, True])
def test_hidden_widget_retries_and_disposes_handles(monkeypatch, asynchronous):
    session, page, element, state = setup(monkeypatch, asynchronous, lambda element, state: lambda: [element])
    element.bounding_box.return_value = None
    assert call(session._cloudflare_solver(page), asynchronous) is None
    assert element.dispose.call_count == _stealth.__CF_MAX_SOLVE_ATTEMPTS__
    page.mouse.click.assert_not_called()


@pytest.mark.parametrize("asynchronous", [False, True])
def test_query_errors_are_not_hidden(monkeypatch, asynchronous):
    session, page, element, state = setup(
        monkeypatch, asynchronous, lambda element, state: PatchrightError("Page closed")
    )
    with pytest.raises(PatchrightError, match="Page closed"):
        call(session._cloudflare_solver(page), asynchronous)
    page.mouse.click.assert_not_called()


PASSIVE = "<script>window._cf_chl_opt = {cType: 'non-interactive'};</script>"


@pytest.mark.parametrize("asynchronous", [False, True])
def test_passive_challenge_stops_after_existing_attempt_limit(monkeypatch, asynchronous):
    session, page, element, state = setup(monkeypatch, asynchronous, lambda element, state: lambda: [])
    state["content"] = PASSIVE
    logger = MagicMock()
    monkeypatch.setattr(_stealth, "log", logger)

    assert call(session._cloudflare_solver(page), asynchronous) is None
    assert page.wait_for_timeout.call_count == 30
    assert page.wait_for_load_state.call_count == 30
    assert state["elapsed"] == 30_000
    page.mouse.click.assert_not_called()
    logger.error.assert_called_once()
    assert all(args.args != ("Cloudflare captcha is solved",) for args in logger.info.call_args_list)


@pytest.mark.parametrize("asynchronous", [False, True])
@pytest.mark.parametrize("clear_after", [1000, 10_000, 30_000])
def test_passive_clearance_is_seen_after_last_sleep(monkeypatch, asynchronous, clear_after):
    session, page, element, state = setup(monkeypatch, asynchronous, lambda element, state: lambda: [])
    state["content"] = PASSIVE

    def sleep(milliseconds):
        state["elapsed"] += milliseconds
        if state["elapsed"] >= clear_after:
            state["content"] = CLEAN

    page.wait_for_timeout.side_effect = sleep
    assert call(session._cloudflare_solver(page), asynchronous) is None
    assert state["elapsed"] == clear_after
    page.mouse.click.assert_not_called()


@pytest.mark.parametrize("asynchronous", [False, True])
def test_passive_challenge_switches_to_interactive(monkeypatch, asynchronous):
    session, page, element, state = setup(monkeypatch, asynchronous, lambda element, state: lambda: [element])
    state["content"] = PASSIVE

    def sleep(milliseconds):
        state["elapsed"] += milliseconds
        if state["content"] == PASSIVE:
            state["content"] = CHALLENGE

    page.wait_for_timeout.side_effect = sleep
    assert call(session._cloudflare_solver(page), asynchronous) is None
    page.mouse.click.assert_called_once()
    assert state["content"] == CLEAN


def setup_hidden_frame(page, asynchronous, visible):
    mock = AsyncMock if asynchronous else MagicMock
    frame, element = MagicMock(), MagicMock()
    frame.frame_element = mock(return_value=element)
    element.is_visible = mock(side_effect=visible)
    element.bounding_box = mock(return_value={"x": 100, "y": 200})
    page.frame.return_value = frame
    return frame, element


@pytest.mark.parametrize("asynchronous", [False, True])
def test_hidden_frame_stops_without_clicking(monkeypatch, asynchronous):
    session, page, element, state = setup(monkeypatch, asynchronous, lambda element, state: lambda: [])
    frame, frame_element = setup_hidden_frame(page, asynchronous, lambda: False)
    logger = MagicMock()
    monkeypatch.setattr(_stealth, "log", logger)

    assert call(session._cloudflare_solver(page), asynchronous) is None
    assert page.wait_for_timeout.call_count == 60
    assert state["elapsed"] == 30_000
    page.mouse.click.assert_not_called()
    frame_element.bounding_box.assert_not_called()
    page.locator.assert_not_called()
    logger.error.assert_called_once()
    assert all(args.args != ("Cloudflare captcha is solved",) for args in logger.info.call_args_list)


@pytest.mark.parametrize("asynchronous", [False, True])
@pytest.mark.parametrize("visible_after", [0, 500, 10_500, 29_500])
def test_late_frame_uses_existing_attempts(monkeypatch, asynchronous, visible_after):
    session, page, element, state = setup(monkeypatch, asynchronous, lambda element, state: lambda: [])
    frame, frame_element = setup_hidden_frame(page, asynchronous, lambda: state["elapsed"] >= visible_after)

    assert call(session._cloudflare_solver(page), asynchronous) is None
    assert state["elapsed"] == visible_after
    page.mouse.click.assert_called_once()
    assert state["content"] == CLEAN


@pytest.mark.parametrize("asynchronous", [False, True])
def test_cleared_challenge_with_hidden_frame_is_not_clicked(monkeypatch, asynchronous):
    session, page, element, state = setup(monkeypatch, asynchronous, lambda element, state: lambda: [])
    frame, frame_element = setup_hidden_frame(page, asynchronous, lambda: False)

    def sleep(milliseconds):
        state["elapsed"] += milliseconds
        state["content"] = CLEAN

    page.wait_for_timeout.side_effect = sleep
    assert call(session._cloudflare_solver(page), asynchronous) is None
    assert state["elapsed"] == 10_000
    page.mouse.click.assert_not_called()
    frame_element.bounding_box.assert_not_called()


@pytest.mark.parametrize("asynchronous", [False, True])
def test_passive_wait_preserves_load_state_check(monkeypatch, asynchronous):
    session, page, element, state = setup(monkeypatch, asynchronous, lambda element, state: lambda: [])
    state["content"] = PASSIVE

    def wait_for_load():
        state["content"] = CLEAN

    page.wait_for_load_state.side_effect = wait_for_load
    assert call(session._cloudflare_solver(page), asynchronous) is None
    page.wait_for_load_state.assert_called_once()
    page.mouse.click.assert_not_called()
