"""Tests for the tab reuse lifecycle of the browser sessions, with mocked Playwright objects."""

from unittest.mock import AsyncMock, Mock

import pytest

from scrapling.engines._browsers._base import AsyncSession, SyncSession


def _sync_page() -> Mock:
    page = Mock()
    page.is_closed.return_value = False
    return page


def _async_page() -> Mock:
    page = Mock()
    page.is_closed.return_value = False
    page.set_extra_http_headers = AsyncMock()
    page.unroute_all = AsyncMock()
    page.route = AsyncMock()
    page.close = AsyncMock()
    return page


def _sync_session(max_pages: int = 1) -> SyncSession:
    session = SyncSession(max_pages=max_pages)
    session.context = Mock()
    session.context.new_page.side_effect = lambda: _sync_page()
    return session


def _async_session(max_pages: int = 1) -> AsyncSession:
    session = AsyncSession(max_pages=max_pages)
    session.context = Mock()
    session.context.new_page = AsyncMock(side_effect=lambda: _async_page())
    return session


class TestSyncTabReuse:
    def test_second_request_reuses_the_tab_and_resets_its_settings(self):
        session = _sync_session()
        with session._page_generator(1000, {"x-test": "1"}, True) as first:
            first_page = first.page
        assert session.page_pool.pages_count == 1
        assert first.state == "ready"

        with session._page_generator(2000, None, False) as second:
            assert second.page is first_page
            assert second.state == "busy"
        assert session.context.new_page.call_count == 1
        first_page.set_default_timeout.assert_called_with(2000)
        first_page.set_extra_http_headers.assert_called_with({})
        assert first_page.unroute_all.call_count == 2
        first_page.route.assert_called_once()

    def test_errored_tab_is_closed_and_evicted(self):
        session = _sync_session()
        with session._page_generator(1000, None, False) as page_info:
            page_info.mark_error()
        page_info.page.close.assert_called_once()
        assert session.page_pool.pages_count == 0

        with session._page_generator(1000, None, False):
            pass
        assert session.context.new_page.call_count == 2

    def test_tab_closed_by_the_browser_is_evicted(self):
        session = _sync_session()
        with session._page_generator(1000, None, False) as page_info:
            page_info.page.is_closed.return_value = True
        assert session.page_pool.pages_count == 0

    def test_close_pages_closes_every_tab_and_the_next_request_opens_a_new_one(self):
        session = _sync_session()
        with session._page_generator(1000, None, False) as page_info:
            pass
        session.close_pages()
        page_info.page.close.assert_called_once()
        assert session.page_pool.pages_count == 0

        with session._page_generator(1000, None, False) as fresh:
            assert fresh.page is not page_info.page
        assert session.page_pool.pages_count == 1


class TestAsyncTabReuse:
    @pytest.mark.asyncio
    async def test_second_request_reuses_the_tab_and_resets_its_settings(self):
        session = _async_session()
        async with session._page_generator(1000, {"x-test": "1"}, True) as first:
            first_page = first.page
        assert session.page_pool.pages_count == 1
        assert first.state == "ready"

        async with session._page_generator(2000, None, False) as second:
            assert second.page is first_page
            assert second.state == "busy"
        assert session.context.new_page.await_count == 1
        first_page.set_default_timeout.assert_called_with(2000)
        first_page.set_extra_http_headers.assert_awaited_with({})
        assert first_page.unroute_all.await_count == 2
        first_page.route.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_errored_tab_is_closed_and_evicted(self):
        session = _async_session()
        async with session._page_generator(1000, None, False) as page_info:
            page_info.mark_error()
        page_info.page.close.assert_awaited_once()
        assert session.page_pool.pages_count == 0

    @pytest.mark.asyncio
    async def test_pool_waits_for_a_ready_tab_at_capacity(self):
        session = _async_session(max_pages=1)
        session._max_wait_for_page = 1
        async with session._page_generator(1000, None, False):
            with pytest.raises(TimeoutError, match="No pages finished"):
                async with session._page_generator(1000, None, False):
                    pass

    @pytest.mark.asyncio
    async def test_close_pages_closes_every_tab(self):
        session = _async_session(max_pages=2)
        async with session._page_generator(1000, None, False) as page_info:
            pass
        await session.close_pages()
        page_info.page.close.assert_awaited_once()
        assert session.page_pool.pages_count == 0
