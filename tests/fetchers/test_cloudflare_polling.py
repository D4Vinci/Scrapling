import asyncio
from unittest.mock import AsyncMock, MagicMock

import pytest
from patchright.sync_api import Error as PlaywrightError, TimeoutError as PlaywrightTimeoutError

from scrapling.engines._browsers import _stealth


EMBEDDED = '<script src="https://challenges.cloudflare.com/turnstile/v0/api.js"></script>'


def setup(monkeypatch, asynchronous, script_at=0, frame_at=0, content_cost=0):
    mock = AsyncMock if asynchronous else MagicMock
    session_type = _stealth.AsyncStealthySession if asynchronous else _stealth.StealthySession
    monkeypatch.setattr(session_type, "_wait_for_networkidle", mock())
    monkeypatch.setattr(session_type, "_wait_for_page_stability", mock())
    session = object.__new__(session_type)
    clock = {"elapsed": 0.0}
    monkeypatch.setattr(_stealth, "monotonic", lambda: clock["elapsed"] / 1000)
    page, frame = MagicMock(), MagicMock()

    def content():
        clock["elapsed"] += content_cost
        return EMBEDDED if script_at is not None and clock["elapsed"] >= script_at else "<p>Page</p>"

    def sleep(milliseconds):
        clock["elapsed"] = round(clock["elapsed"] + milliseconds, 6)

    page.content = mock(side_effect=content)
    page.frame.side_effect = lambda **kwargs: frame if frame_at is not None and clock["elapsed"] >= frame_at else None
    page.wait_for_timeout = mock(side_effect=sleep)
    frame.locator.return_value.click = mock()
    return session, page, frame, clock


def solve(session, page, asynchronous, attempts=0):
    result = session._cloudflare_solver(page, attempts)
    if asynchronous:
        asyncio.run(result)


@pytest.mark.parametrize("asynchronous", [False, True])
@pytest.mark.parametrize(
    "script_at,frame_at,elapsed,clicks",
    [
        (0, 0, 0, 1),
        (3000, 3000, 3000, 1),
        (0, 750, 800, 1),
        (750, 750, 1000, 1),
        (5000, 5000, 5000, 1),
        (0, 5000, 5000, 1),
        (6000, 6000, 5000, 0),
        (0, 6000, 5000, 0),
        (None, None, 5000, 0),
        (0, None, 5000, 0),
    ],
)
def test_initial_readiness(monkeypatch, asynchronous, script_at, frame_at, elapsed, clicks):
    session, page, frame, clock = setup(monkeypatch, asynchronous, script_at, frame_at)
    solve(session, page, asynchronous)
    assert clock["elapsed"] == elapsed
    assert frame.locator.return_value.click.call_count == clicks
    assert page.content.call_count == elapsed // 500 + 1
    if clicks:
        frame.locator.assert_called_once_with('input[type="checkbox"]')
        assert frame.locator.return_value.click.call_args.kwargs["timeout"] == 10000
        session._wait_for_networkidle.assert_called_once_with(page, timeout=5000)
    else:
        session._wait_for_networkidle.assert_not_called()
        session._wait_for_page_stability.assert_not_called()
    page.mouse.click.assert_not_called()


@pytest.mark.parametrize("asynchronous", [False, True])
@pytest.mark.parametrize("content_cost", [250, 6000])
def test_html_reading_uses_the_same_wait_budget(monkeypatch, asynchronous, content_cost):
    session, page, frame, clock = setup(monkeypatch, asynchronous, None, None, content_cost)
    solve(session, page, asynchronous)
    assert clock["elapsed"] <= max(5000 + content_cost, content_cost)
    assert sum(call.args[0] for call in page.wait_for_timeout.call_args_list) < 5000
    session._wait_for_networkidle.assert_not_called()
    frame.locator.return_value.click.assert_not_called()


@pytest.mark.parametrize("asynchronous", [False, True])
def test_final_snapshot_is_refreshed_after_slow_html_reads(monkeypatch, asynchronous):
    session, page, frame, clock = setup(monkeypatch, asynchronous, 4950, 4950, content_cost=120)
    solve(session, page, asynchronous)
    assert 5000 <= clock["elapsed"] <= 5120
    frame.locator.return_value.click.assert_called_once()


@pytest.mark.parametrize("asynchronous", [False, True])
def test_recursive_check_has_no_new_polling_window(monkeypatch, asynchronous):
    session, page, frame, clock = setup(monkeypatch, asynchronous, 0, None)
    solve(session, page, asynchronous, attempts=1)
    assert clock["elapsed"] == 0
    page.wait_for_timeout.assert_not_called()
    session._wait_for_networkidle.assert_called_once_with(page, timeout=5000)
    frame.locator.return_value.click.assert_not_called()


@pytest.mark.parametrize("asynchronous", [False, True])
def test_attached_frame_keeps_separate_load_and_checkbox_waits(monkeypatch, asynchronous):
    session, page, frame, clock = setup(monkeypatch, asynchronous)

    def wait(target, *args):
        if target is frame:
            clock["elapsed"] += 11000

    session._wait_for_page_stability.side_effect = wait
    frame.locator.return_value.click.side_effect = lambda **kwargs: clock.update(elapsed=clock["elapsed"] + 6000)
    solve(session, page, asynchronous)
    assert clock["elapsed"] == 17000
    frame.locator.return_value.click.assert_called_once()
    page.wait_for_timeout.assert_not_called()


@pytest.mark.parametrize("asynchronous", [False, True])
@pytest.mark.parametrize("missing", [False, True])
def test_only_checkbox_timeout_is_optional(monkeypatch, asynchronous, missing):
    session, page, frame, clock = setup(monkeypatch, asynchronous)
    frame.locator.return_value.click.side_effect = (
        PlaywrightTimeoutError("No checkbox") if missing else PlaywrightError("Page closed")
    )
    logger = MagicMock()
    monkeypatch.setattr(_stealth, "log", logger)
    if missing:
        solve(session, page, asynchronous)
    else:
        with pytest.raises(PlaywrightError, match="Page closed"):
            solve(session, page, asynchronous)
    assert all(call.args != ("Cloudflare captcha is solved",) for call in logger.info.call_args_list)
    session._wait_for_networkidle.assert_not_called()
