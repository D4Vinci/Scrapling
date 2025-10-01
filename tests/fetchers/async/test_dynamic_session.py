import pytest
import asyncio

import pytest_httpbin

from scrapling.fetchers import AsyncDynamicSession


@pytest_httpbin.use_class_based_httpbin
@pytest.mark.asyncio
class TestAsyncDynamicSession:
    """Test AsyncDynamicSession"""

    # The `AsyncDynamicSession` is inheriting from `DynamicSession` class so no need to repeat all the tests
    @pytest.fixture
    def urls(self, httpbin):
        return {
            "basic": f"{httpbin.url}/get",
            "html": f"{httpbin.url}/html",
        }

    async def test_concurrent_async_requests(self, urls):
        """Test concurrent requests with async session"""
        async with AsyncDynamicSession(max_pages=3) as session:
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
        async with AsyncDynamicSession() as session:
            # The first request creates a page
            response = await session.fetch(urls["basic"])
            assert response.status == 200
            assert session.page_pool.pages_count == 0
            
            # The second request should reuse the page
            response = await session.fetch(urls["html"])
            assert response.status == 200
            assert session.page_pool.pages_count == 0

            # Check pool stats
            stats = session.get_pool_stats()
            assert stats["total_pages"] == 0
            assert stats["max_pages"] == 1

    async def test_dynamic_session_with_options(self, urls):
        """Test AsyncDynamicSession with various options"""
        async with AsyncDynamicSession(
                headless=False,
                stealth=True,
                disable_resources=True,
                extra_headers={"X-Test": "value"}
        ) as session:
            response = await session.fetch(urls["html"])
            assert response.status == 200

    async def test_error_handling_in_fetch(self, urls):
        """Test error handling during fetch"""
        async with AsyncDynamicSession() as session:
            # Test with invalid URL
            with pytest.raises(Exception):
                await session.fetch("invalid://url")
