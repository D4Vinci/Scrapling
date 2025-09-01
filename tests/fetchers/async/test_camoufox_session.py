
import pytest
import asyncio

import pytest_httpbin

from scrapling.engines import AsyncStealthySession


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
        assert session._closed is True

        # Should raise RuntimeError when used after closing
        with pytest.raises(RuntimeError):
            await session.fetch(urls["basic"])

    async def test_page_pool_management(self, urls):
        """Test page pool creation and reuse"""
        async with AsyncStealthySession() as session:
            # The first request creates a page
            _ = await session.fetch(urls["basic"])
            assert session.page_pool.pages_count == 1

            # The second request should reuse the page
            _ = await session.fetch(urls["html"])
            assert session.page_pool.pages_count == 1

            # Check pool stats
            stats = session.get_pool_stats()
            assert stats["total_pages"] == 1
            assert stats["max_pages"] == 1

    async def test_stealthy_session_with_options(self, urls):
        """Test AsyncStealthySession with various options"""
        async with AsyncStealthySession(
                max_pages=1,
                block_images=True,
                disable_ads=True,
                humanize=True
        ) as session:
            response = await session.fetch(urls["html"])
            assert response.status == 200

    async def test_error_handling_in_fetch(self, urls):
        """Test error handling during fetch"""
        async with AsyncStealthySession() as session:
            # Test with invalid URL
            with pytest.raises(Exception):
                await session.fetch("invalid://url")
