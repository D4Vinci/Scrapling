
import pytest
import asyncio

import pytest_httpbin

from scrapling.fetchers import AsyncStealthySession


@pytest_httpbin.use_class_based_httpbin
@pytest.mark.asyncio
class TestAsyncStealthySession:
    """Test AsyncStealthySession"""

    # The `AsyncStealthySession` is inheriting from `StealthySession` class so no need to repeat all the tests
    @pytest.fixture
    def urls(self, httpbin):
        return {
            "basic": f"{httpbin.url}/get",
            "html": f"{httpbin.url}/html",
        }

    async def test_concurrent_async_requests(self, urls):
        """Test concurrent requests with async session"""
        async with AsyncStealthySession(max_pages=3) as session:
            # Launch multiple concurrent requests
            tasks = [
                session.fetch(urls["basic"]),
                session.fetch(urls["html"]),
                session.fetch(urls["basic"])
            ]

            assert session.max_pages == 3
            assert session.page_pool.max_pages == 3
            assert session.context is not None

            responses = await asyncio.gather(*tasks)

            # All should succeed
            assert all(r.status == 200 for r in responses)

            # Check pool stats
            stats = session.get_pool_stats()
            assert stats["total_pages"] <= 3

        # After exit, should be closed
        assert session._is_alive is False

        # Should raise RuntimeError when used after closing
        with pytest.raises(RuntimeError):
            await session.fetch(urls["basic"])

    async def test_page_pool_management(self, urls):
        """Test page pool creation and reuse"""
        async with AsyncStealthySession() as session:
            # The first request creates a page, and it stays open afterwards
            response = await session.fetch(urls["basic"])
            assert response.status == 200
            assert session.page_pool.pages_count == 1
            page = session.page_pool.pages[0].page
            assert session.page_pool.pages[0].state == "ready"

            # The second request reuses the same tab
            response = await session.fetch(urls["html"])
            assert response.status == 200
            assert session.page_pool.pages_count == 1
            assert session.page_pool.pages[0].page is page

            # Check pool stats
            stats = session.get_pool_stats()
            assert stats["total_pages"] == 1
            assert stats["busy_pages"] == 0
            assert stats["max_pages"] == 1

    async def test_close_pages(self, urls):
        """Closing the tabs empties the pool, and the next request opens a fresh one"""
        async with AsyncStealthySession() as session:
            await session.fetch(urls["basic"])
            page = session.page_pool.pages[0].page

            await session.close_pages()
            assert session.page_pool.pages_count == 0
            assert page.is_closed()

            response = await session.fetch(urls["html"])
            assert response.status == 200
            assert session.page_pool.pages_count == 1
            assert session.page_pool.pages[0].page is not page

    async def test_per_request_headers_do_not_leak_into_the_next_request(self, httpbin):
        """A reused tab gets its settings reset, so headers from the previous request are gone"""
        async with AsyncStealthySession() as session:
            response = await session.fetch(f"{httpbin.url}/headers", extra_headers={"X-Scrapling-First": "1"})
            assert "X-Scrapling-First" in response.get_all_text()

            response = await session.fetch(f"{httpbin.url}/headers", extra_headers={"X-Scrapling-Second": "2"})
            assert "X-Scrapling-Second" in response.get_all_text()
            assert "X-Scrapling-First" not in response.get_all_text(), "the new headers must replace the old ones"

            response = await session.fetch(f"{httpbin.url}/headers")
            assert "X-Scrapling-Second" not in response.get_all_text()
            assert "X-Scrapling-First" not in response.get_all_text()

    async def test_resource_blocking_does_not_leak_into_the_next_request(self, httpbin):
        """Routes registered for one request are removed before the tab is reused"""
        js = """async () => {
            const img = document.createElement('img');
            const done = new Promise(r => { img.onload = () => r('loaded'); img.onerror = () => r('blocked'); });
            img.src = '/image/png?' + Math.random();
            document.body.appendChild(img);
            return await done;
        }"""
        results = []

        async def probe(page):
            results.append(await page.evaluate(js))

        async with AsyncStealthySession() as session:
            await session.fetch(f"{httpbin.url}/html", disable_resources=True, page_action=probe)
            await session.fetch(f"{httpbin.url}/html", page_action=probe)
            assert results == ["blocked", "loaded"]
            assert session.page_pool.pages_count == 1

    async def test_stealthy_session_with_options(self, urls):
        """Test AsyncStealthySession with various options"""
        async with AsyncStealthySession(
                max_pages=1,
                block_webrtc=True,
                allow_webgl=True
        ) as session:
            response = await session.fetch(urls["html"])
            assert response.status == 200

    async def test_error_handling_in_fetch(self, urls):
        """Test error handling during fetch"""
        async with AsyncStealthySession() as session:
            # Test with invalid URL
            with pytest.raises(Exception):
                await session.fetch("invalid://url")
            assert session.page_pool.pages_count == 0, "errored tabs are closed and evicted"
