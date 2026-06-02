import pytest

from scrapling.engines._browsers._base import SyncSession, AsyncSession


class _Closable:
    def __init__(self):
        self.closed = False

    def close(self):
        self.closed = True


class _AsyncClosable:
    def __init__(self):
        self.closed = False

    async def close(self):
        self.closed = True


class _Stopper:
    def __init__(self):
        self.stopped = False

    def stop(self):
        self.stopped = True


class _AsyncStopper:
    def __init__(self):
        self.stopped = False

    async def stop(self):
        self.stopped = True


def test_sync_session_close_is_idempotent_and_closes_resources():
    session = SyncSession()
    session.context = _Closable()
    session.browser = _Closable()
    session.playwright = _Stopper()
    session._is_alive = True

    context = session.context
    browser = session.browser
    playwright = session.playwright

    session.close()
    session.close()

    assert context.closed is True
    assert browser.closed is True
    assert playwright.stopped is True
    assert session._is_alive is False


@pytest.mark.anyio
async def test_async_session_close_is_idempotent_and_closes_resources():
    session = AsyncSession()
    session.context = _AsyncClosable()
    session.browser = _AsyncClosable()
    session.playwright = _AsyncStopper()
    session._is_alive = True

    context = session.context
    browser = session.browser
    playwright = session.playwright

    await session.close()
    await session.close()

    assert context.closed is True
    assert browser.closed is True
    assert playwright.stopped is True
    assert session._is_alive is False
