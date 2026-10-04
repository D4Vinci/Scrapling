import asyncio
from unittest.mock import AsyncMock, Mock

import pytest

from scrapling.engines._browsers._base import AsyncSession, SyncSession
from tests.fetchers.test_network_history import request


def _session(asynchronous=False):
    session = AsyncSession(record_requests=True) if asynchronous else SyncSession(record_requests=True)
    context, browser, playwright = Mock(), Mock(), Mock()
    if asynchronous:
        context.close, browser.close, playwright.stop = AsyncMock(), AsyncMock(), AsyncMock()
    session.context, session.browser, session.playwright = context, browser, playwright
    session._is_alive = True
    session.network._attach(context)
    capture = dict(call.args for call in context.on.call_args_list)["requestfinished"]
    return session, context, browser, playwright, capture


def _closed(session, context, browser, playwright):
    assert not session._is_alive and not session.network._contexts
    assert session.context is session.browser is session.playwright is None
    context.close.assert_called_once_with()
    browser.close.assert_called_once_with()
    playwright.stop.assert_called_once_with()
    assert {call.args[0] for call in context.remove_listener.call_args_list} == {"requestfinished", "close"}


def test_sync_session_close_during_capture_does_not_restore_late_response():
    session, context, browser, playwright, capture = _session()
    capture(request(body=b"saved"))
    saved = session.network.get(1)

    def close_before_body_returns():
        session.close()
        return b"late"

    native = request()
    native.existing_response.body.side_effect = close_before_body_returns
    capture(native)
    session.close()
    _closed(session, context, browser, playwright)
    assert session.network.search() == [saved] and saved.response.body == b"saved"
    assert session.network.last_id == 1


@pytest.mark.asyncio
@pytest.mark.parametrize("read_error", [False, True])
async def test_async_session_close_does_not_wait_for_running_capture(read_error):
    session, context, browser, playwright, capture = _session(asynchronous=True)
    await capture(request(body=b"saved", asynchronous=True))
    saved = session.network.get(1)
    reading, release = asyncio.Event(), asyncio.Event()

    async def held_body():
        reading.set()
        await release.wait()
        if read_error:
            raise RuntimeError("Browser closed while reading")
        return b"late"

    native = request(asynchronous=True)
    native.existing_response.body.side_effect = held_body
    task = asyncio.create_task(capture(native))
    try:
        await asyncio.wait_for(reading.wait(), timeout=2)
        await asyncio.wait_for(session.close(), timeout=2)
        assert not task.done() and not release.is_set()
        _closed(session, context, browser, playwright)
        context.close.assert_awaited_once_with()
        browser.close.assert_awaited_once_with()
        playwright.stop.assert_awaited_once_with()
        release.set()
        await asyncio.wait_for(task, timeout=2)
        await session.close()
        assert session.network.search() == [saved] and saved.response.body == b"saved"
        assert session.network.last_id == 1
    finally:
        release.set()
        await asyncio.wait_for(asyncio.gather(task, return_exceptions=True), timeout=2)
        await session.close()
