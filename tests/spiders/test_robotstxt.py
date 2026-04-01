"""Tests for RobotsTxtManager."""

import asyncio

import pytest

from scrapling.spiders.robotstxt import RobotsTxtManager
from scrapling.core._types import List, Optional


# ---------------------------------------------------------------------------
# Fixtures and helpers
# ---------------------------------------------------------------------------


class MockResponse:
    """Minimal response stub matching the shape _get_parser expects."""

    def __init__(self, status: int = 200, body: bytes = b"", encoding: str = "utf-8"):
        self.status = status
        self.body = body
        self.encoding = encoding


def make_fetch_fn(status: int = 200, content: str = "", encoding: str = "utf-8"):
    """Return an async fetch callable that returns a fixed response.

    Attaches a `.calls` list so tests can assert how many times it was invoked
    and with which arguments.
    """
    calls: List[tuple] = []

    async def _fetch(url: str, sid: str) -> MockResponse:
        calls.append((url, sid))
        return MockResponse(status=status, body=content.encode(encoding), encoding=encoding)

    _fetch.calls = calls  # type: ignore[attr-defined]
    return _fetch


# ---------------------------------------------------------------------------
# Shared robots.txt fixtures
# ---------------------------------------------------------------------------

ROBOTS_BASIC = """\
User-agent: *
Disallow: /admin/
Crawl-delay: 2
"""

ROBOTS_WITH_RATE = """\
User-agent: *
Request-rate: 1/10
Disallow: /private/
"""

ROBOTS_WITH_SITEMAP = """\
User-agent: *
Disallow:

Sitemap: https://example.com/sitemap.xml
Sitemap: https://example.com/sitemap2.xml
"""

ROBOTS_ALLOW_OVERRIDE = """\
User-agent: *
Disallow: /secret/
Allow: /secret/public.html
"""

ROBOTS_DISALLOW_ALL = """\
User-agent: *
Disallow: /
"""


# ---------------------------------------------------------------------------
# Tests: can_fetch
# ---------------------------------------------------------------------------


class TestCanFetch:
    @pytest.mark.asyncio
    async def test_allowed_url_returns_true(self):
        mgr = RobotsTxtManager(make_fetch_fn(content=ROBOTS_BASIC))

        assert await mgr.can_fetch("https://example.com/products", "s1") is True

    @pytest.mark.asyncio
    async def test_disallowed_url_returns_false(self):
        mgr = RobotsTxtManager(make_fetch_fn(content=ROBOTS_BASIC))

        assert await mgr.can_fetch("https://example.com/admin/", "s1") is False

    @pytest.mark.asyncio
    async def test_disallowed_subpath_returns_false(self):
        mgr = RobotsTxtManager(make_fetch_fn(content=ROBOTS_BASIC))

        assert await mgr.can_fetch("https://example.com/admin/users", "s1") is False

    @pytest.mark.asyncio
    async def test_root_url_is_allowed(self):
        mgr = RobotsTxtManager(make_fetch_fn(content=ROBOTS_BASIC))

        assert await mgr.can_fetch("https://example.com/", "s1") is True

    @pytest.mark.asyncio
    async def test_allow_directive_overrides_disallow(self):
        mgr = RobotsTxtManager(make_fetch_fn(content=ROBOTS_ALLOW_OVERRIDE))

        assert await mgr.can_fetch("https://example.com/secret/public.html", "s1") is True
        assert await mgr.can_fetch("https://example.com/secret/private.html", "s1") is False

    @pytest.mark.asyncio
    async def test_disallow_all_blocks_every_path(self):
        mgr = RobotsTxtManager(make_fetch_fn(content=ROBOTS_DISALLOW_ALL))

        assert await mgr.can_fetch("https://example.com/", "s1") is False
        assert await mgr.can_fetch("https://example.com/page", "s1") is False
        assert await mgr.can_fetch("https://example.com/a/b/c", "s1") is False

    @pytest.mark.asyncio
    async def test_empty_robots_allows_everything(self):
        mgr = RobotsTxtManager(make_fetch_fn(content=""))

        assert await mgr.can_fetch("https://example.com/anything", "s1") is True
        assert await mgr.can_fetch("https://example.com/admin/secret", "s1") is True

    @pytest.mark.asyncio
    async def test_non_200_response_allows_everything(self):
        for status in [403, 404, 500, 503]:
            mgr = RobotsTxtManager(make_fetch_fn(status=status))
            result = await mgr.can_fetch("https://example.com/page", "s1")
            assert result is True, f"Expected True for HTTP {status}"

    @pytest.mark.asyncio
    async def test_fetch_error_allows_everything(self):
        async def failing_fetch(url: str, sid: str) -> MockResponse:
            raise ConnectionError("network failure")

        mgr = RobotsTxtManager(failing_fetch)

        assert await mgr.can_fetch("https://example.com/page", "s1") is True

    @pytest.mark.asyncio
    async def test_wildcard_path_pattern(self):
        content = "User-agent: *\nDisallow: /*.pdf$"
        mgr = RobotsTxtManager(make_fetch_fn(content=content))

        assert await mgr.can_fetch("https://example.com/report.pdf", "s1") is False
        assert await mgr.can_fetch("https://example.com/report.html", "s1") is True

    @pytest.mark.asyncio
    async def test_returns_bool(self):
        mgr = RobotsTxtManager(make_fetch_fn(content=ROBOTS_BASIC))
        result = await mgr.can_fetch("https://example.com/", "s1")
        assert isinstance(result, bool)


# ---------------------------------------------------------------------------
# Tests: get_crawl_delay
# ---------------------------------------------------------------------------


class TestGetCrawlDelay:
    @pytest.mark.asyncio
    async def test_returns_float_when_set(self):
        mgr = RobotsTxtManager(make_fetch_fn(content=ROBOTS_BASIC))

        delay = await mgr.get_crawl_delay("https://example.com/", "s1")

        assert delay == 2.0
        assert isinstance(delay, float)

    @pytest.mark.asyncio
    async def test_returns_none_when_not_set(self):
        content = "User-agent: *\nDisallow: /admin/"
        mgr = RobotsTxtManager(make_fetch_fn(content=content))

        assert await mgr.get_crawl_delay("https://example.com/", "s1") is None

    @pytest.mark.asyncio
    async def test_returns_none_for_empty_robots(self):
        mgr = RobotsTxtManager(make_fetch_fn(content=""))

        assert await mgr.get_crawl_delay("https://example.com/", "s1") is None

    @pytest.mark.asyncio
    async def test_returns_none_on_fetch_error(self):
        async def failing_fetch(url: str, sid: str) -> MockResponse:
            raise ConnectionError("network failure")

        mgr = RobotsTxtManager(failing_fetch)

        assert await mgr.get_crawl_delay("https://example.com/", "s1") is None

    @pytest.mark.asyncio
    async def test_returns_none_for_non_200_response(self):
        mgr = RobotsTxtManager(make_fetch_fn(status=404))

        assert await mgr.get_crawl_delay("https://example.com/", "s1") is None

    @pytest.mark.asyncio
    async def test_fractional_delay(self):
        content = "User-agent: *\nCrawl-delay: 0.5"
        mgr = RobotsTxtManager(make_fetch_fn(content=content))

        delay = await mgr.get_crawl_delay("https://example.com/", "s1")

        assert delay == 0.5

    @pytest.mark.asyncio
    async def test_url_path_does_not_affect_result(self):
        """Any URL on the same domain should return the same delay."""
        mgr = RobotsTxtManager(make_fetch_fn(content=ROBOTS_BASIC))

        d1 = await mgr.get_crawl_delay("https://example.com/", "s1")
        d2 = await mgr.get_crawl_delay("https://example.com/deep/path/page.html", "s1")

        assert d1 == d2


# ---------------------------------------------------------------------------
# Tests: get_request_rate
# ---------------------------------------------------------------------------


class TestGetRequestRate:
    @pytest.mark.asyncio
    async def test_returns_tuple_when_set(self):
        mgr = RobotsTxtManager(make_fetch_fn(content=ROBOTS_WITH_RATE))

        rate = await mgr.get_request_rate("https://example.com/", "s1")

        assert rate is not None
        assert isinstance(rate, tuple)
        assert len(rate) == 2

    @pytest.mark.asyncio
    async def test_tuple_contains_integers(self):
        mgr = RobotsTxtManager(make_fetch_fn(content=ROBOTS_WITH_RATE))

        rate = await mgr.get_request_rate("https://example.com/", "s1")

        assert rate is not None
        requests, seconds = rate
        assert isinstance(requests, int)
        assert isinstance(seconds, int)

    @pytest.mark.asyncio
    async def test_returns_none_when_not_set(self):
        mgr = RobotsTxtManager(make_fetch_fn(content=ROBOTS_BASIC))

        assert await mgr.get_request_rate("https://example.com/", "s1") is None

    @pytest.mark.asyncio
    async def test_returns_none_for_empty_robots(self):
        mgr = RobotsTxtManager(make_fetch_fn(content=""))

        assert await mgr.get_request_rate("https://example.com/", "s1") is None

    @pytest.mark.asyncio
    async def test_returns_none_on_fetch_error(self):
        async def failing_fetch(url: str, sid: str) -> MockResponse:
            raise ConnectionError("network failure")

        mgr = RobotsTxtManager(failing_fetch)

        assert await mgr.get_request_rate("https://example.com/", "s1") is None

    @pytest.mark.asyncio
    async def test_returns_none_for_non_200_response(self):
        mgr = RobotsTxtManager(make_fetch_fn(status=404))

        assert await mgr.get_request_rate("https://example.com/", "s1") is None


# ---------------------------------------------------------------------------
# Tests: get_sitemaps
# ---------------------------------------------------------------------------


class TestGetSitemaps:
    @pytest.mark.asyncio
    async def test_returns_list_of_sitemap_urls(self):
        mgr = RobotsTxtManager(make_fetch_fn(content=ROBOTS_WITH_SITEMAP))

        sitemaps = await mgr.get_sitemaps("https://example.com/", "s1")

        assert "https://example.com/sitemap.xml" in sitemaps
        assert "https://example.com/sitemap2.xml" in sitemaps

    @pytest.mark.asyncio
    async def test_returns_correct_count(self):
        mgr = RobotsTxtManager(make_fetch_fn(content=ROBOTS_WITH_SITEMAP))

        sitemaps = await mgr.get_sitemaps("https://example.com/", "s1")

        assert len(sitemaps) == 2

    @pytest.mark.asyncio
    async def test_returns_list_type(self):
        mgr = RobotsTxtManager(make_fetch_fn(content=ROBOTS_WITH_SITEMAP))

        sitemaps = await mgr.get_sitemaps("https://example.com/", "s1")

        assert isinstance(sitemaps, list)

    @pytest.mark.asyncio
    async def test_returns_empty_list_when_no_sitemaps(self):
        mgr = RobotsTxtManager(make_fetch_fn(content=ROBOTS_BASIC))

        assert await mgr.get_sitemaps("https://example.com/", "s1") == []

    @pytest.mark.asyncio
    async def test_returns_empty_list_for_empty_robots(self):
        mgr = RobotsTxtManager(make_fetch_fn(content=""))

        assert await mgr.get_sitemaps("https://example.com/", "s1") == []

    @pytest.mark.asyncio
    async def test_returns_empty_list_on_fetch_error(self):
        async def failing_fetch(url: str, sid: str) -> MockResponse:
            raise ConnectionError("network failure")

        mgr = RobotsTxtManager(failing_fetch)

        assert await mgr.get_sitemaps("https://example.com/", "s1") == []


# ---------------------------------------------------------------------------
# Tests: caching behaviour
# ---------------------------------------------------------------------------


class TestCachingBehaviour:
    @pytest.mark.asyncio
    async def test_second_call_same_domain_uses_cache(self):
        fetch_fn = make_fetch_fn(content=ROBOTS_BASIC)
        mgr = RobotsTxtManager(fetch_fn)

        await mgr.can_fetch("https://example.com/page1", "s1")
        await mgr.can_fetch("https://example.com/page2", "s1")

        assert len(fetch_fn.calls) == 1

    @pytest.mark.asyncio
    async def test_all_methods_share_cache(self):
        fetch_fn = make_fetch_fn(content=ROBOTS_BASIC)
        mgr = RobotsTxtManager(fetch_fn)

        await mgr.can_fetch("https://example.com/", "s1")
        await mgr.get_crawl_delay("https://example.com/", "s1")
        await mgr.get_request_rate("https://example.com/", "s1")
        await mgr.get_sitemaps("https://example.com/", "s1")

        assert len(fetch_fn.calls) == 1

    @pytest.mark.asyncio
    async def test_different_sids_use_separate_cache_entries(self):
        fetch_fn = make_fetch_fn(content=ROBOTS_BASIC)
        mgr = RobotsTxtManager(fetch_fn)

        await mgr.can_fetch("https://example.com/", "s1")
        await mgr.can_fetch("https://example.com/", "s2")

        assert len(fetch_fn.calls) == 2

    @pytest.mark.asyncio
    async def test_different_domains_use_separate_cache_entries(self):
        fetch_fn = make_fetch_fn(content=ROBOTS_BASIC)
        mgr = RobotsTxtManager(fetch_fn)

        await mgr.can_fetch("https://example.com/", "s1")
        await mgr.can_fetch("https://other.com/", "s1")

        assert len(fetch_fn.calls) == 2

    @pytest.mark.asyncio
    async def test_cache_keyed_by_domain_not_path(self):
        fetch_fn = make_fetch_fn(content=ROBOTS_BASIC)
        mgr = RobotsTxtManager(fetch_fn)

        await mgr.can_fetch("https://example.com/a/b/c", "s1")
        await mgr.can_fetch("https://example.com/x/y/z", "s1")
        await mgr.can_fetch("https://example.com/admin/", "s1")

        assert len(fetch_fn.calls) == 1

    @pytest.mark.asyncio
    async def test_sid_is_passed_to_fetch_fn(self):
        fetch_fn = make_fetch_fn(content=ROBOTS_BASIC)
        mgr = RobotsTxtManager(fetch_fn)

        await mgr.can_fetch("https://example.com/", "my_session")

        _, received_sid = fetch_fn.calls[0]
        assert received_sid == "my_session"


# ---------------------------------------------------------------------------
# Tests: robots.txt URL construction
# ---------------------------------------------------------------------------


class TestRobotsTxtUrlConstruction:
    @pytest.mark.asyncio
    async def test_http_scheme_preserved(self):
        fetch_fn = make_fetch_fn(content="")
        mgr = RobotsTxtManager(fetch_fn)

        await mgr.can_fetch("http://example.com/page", "s1")

        fetched_url, _ = fetch_fn.calls[0]
        assert fetched_url == "http://example.com/robots.txt"

    @pytest.mark.asyncio
    async def test_https_scheme_preserved(self):
        fetch_fn = make_fetch_fn(content="")
        mgr = RobotsTxtManager(fetch_fn)

        await mgr.can_fetch("https://example.com/page", "s1")

        fetched_url, _ = fetch_fn.calls[0]
        assert fetched_url == "https://example.com/robots.txt"

    @pytest.mark.asyncio
    async def test_fetched_at_domain_root_regardless_of_request_path(self):
        fetch_fn = make_fetch_fn(content="")
        mgr = RobotsTxtManager(fetch_fn)

        await mgr.can_fetch("https://example.com/deep/nested/path/page.html", "s1")

        fetched_url, _ = fetch_fn.calls[0]
        assert fetched_url == "https://example.com/robots.txt"

    @pytest.mark.asyncio
    async def test_port_included_in_url(self):
        fetch_fn = make_fetch_fn(content="")
        mgr = RobotsTxtManager(fetch_fn)

        await mgr.can_fetch("http://example.com:8080/page", "s1")

        fetched_url, _ = fetch_fn.calls[0]
        assert fetched_url == "http://example.com:8080/robots.txt"

    @pytest.mark.asyncio
    async def test_different_ports_treated_as_different_domains(self):
        fetch_fn = make_fetch_fn(content="")
        mgr = RobotsTxtManager(fetch_fn)

        await mgr.can_fetch("http://example.com:8000/page", "s1")
        await mgr.can_fetch("http://example.com:9000/page", "s1")

        assert len(fetch_fn.calls) == 2
        urls = [call[0] for call in fetch_fn.calls]
        assert "http://example.com:8000/robots.txt" in urls
        assert "http://example.com:9000/robots.txt" in urls


# ---------------------------------------------------------------------------
# Tests: encoding
# ---------------------------------------------------------------------------


class TestEncoding:
    @pytest.mark.asyncio
    async def test_non_utf8_body_decoded_with_response_encoding(self):
        content = "User-agent: *\nDisallow: /admin/\nCrawl-delay: 3"
        body = content.encode("latin-1")

        async def fetch_fn(url: str, sid: str) -> MockResponse:
            return MockResponse(status=200, body=body, encoding="latin-1")

        mgr = RobotsTxtManager(fetch_fn)
        delay = await mgr.get_crawl_delay("https://example.com/", "s1")

        assert delay == 3.0

    @pytest.mark.asyncio
    async def test_bytes_body_decoded_correctly(self):
        content = "User-agent: *\nDisallow: /private/"
        body = content.encode("utf-8")

        async def fetch_fn(url: str, sid: str) -> MockResponse:
            return MockResponse(status=200, body=body, encoding="utf-8")

        mgr = RobotsTxtManager(fetch_fn)

        assert await mgr.can_fetch("https://example.com/private/", "s1") is False
        assert await mgr.can_fetch("https://example.com/public/", "s1") is True


# ---------------------------------------------------------------------------
# Tests: clear_cache
# ---------------------------------------------------------------------------


class TestClearCache:
    @pytest.mark.asyncio
    async def test_clear_all_forces_refetch(self):
        fetch_fn = make_fetch_fn(content=ROBOTS_BASIC)
        mgr = RobotsTxtManager(fetch_fn)

        await mgr.can_fetch("https://example.com/", "s1")
        mgr.clear_cache()
        await mgr.can_fetch("https://example.com/", "s1")

        assert len(fetch_fn.calls) == 2

    @pytest.mark.asyncio
    async def test_clear_by_domain_only_invalidates_that_domain(self):
        fetch_fn = make_fetch_fn(content=ROBOTS_BASIC)
        mgr = RobotsTxtManager(fetch_fn)

        await mgr.can_fetch("https://example.com/", "s1")
        await mgr.can_fetch("https://other.com/", "s1")
        assert len(fetch_fn.calls) == 2

        mgr.clear_cache(domain="example.com")

        await mgr.can_fetch("https://example.com/", "s1")  # refetched
        await mgr.can_fetch("https://other.com/", "s1")    # still cached

        assert len(fetch_fn.calls) == 3

    @pytest.mark.asyncio
    async def test_clear_by_sid_only_invalidates_that_sid(self):
        fetch_fn = make_fetch_fn(content=ROBOTS_BASIC)
        mgr = RobotsTxtManager(fetch_fn)

        await mgr.can_fetch("https://example.com/", "s1")
        await mgr.can_fetch("https://example.com/", "s2")
        assert len(fetch_fn.calls) == 2

        mgr.clear_cache(sid="s1")

        await mgr.can_fetch("https://example.com/", "s1")  # refetched
        await mgr.can_fetch("https://example.com/", "s2")  # still cached

        assert len(fetch_fn.calls) == 3

    @pytest.mark.asyncio
    async def test_clear_by_domain_and_sid_targets_exact_entry(self):
        fetch_fn = make_fetch_fn(content=ROBOTS_BASIC)
        mgr = RobotsTxtManager(fetch_fn)

        await mgr.can_fetch("https://example.com/", "s1")
        await mgr.can_fetch("https://example.com/", "s2")
        assert len(fetch_fn.calls) == 2

        mgr.clear_cache(domain="example.com", sid="s1")

        await mgr.can_fetch("https://example.com/", "s1")  # refetched
        await mgr.can_fetch("https://example.com/", "s2")  # still cached

        assert len(fetch_fn.calls) == 3

    def test_clear_nonexistent_domain_does_not_raise(self):
        mgr = RobotsTxtManager(make_fetch_fn())
        mgr.clear_cache(domain="nevervisited.com")  # should not raise

    def test_clear_empty_cache_does_not_raise(self):
        mgr = RobotsTxtManager(make_fetch_fn())
        mgr.clear_cache()  # should not raise

    @pytest.mark.asyncio
    async def test_clear_all_empties_cache_completely(self):
        fetch_fn = make_fetch_fn(content=ROBOTS_BASIC)
        mgr = RobotsTxtManager(fetch_fn)

        await mgr.can_fetch("https://a.com/", "s1")
        await mgr.can_fetch("https://b.com/", "s1")
        await mgr.can_fetch("https://c.com/", "s1")
        assert len(fetch_fn.calls) == 3

        mgr.clear_cache()

        await mgr.can_fetch("https://a.com/", "s1")
        await mgr.can_fetch("https://b.com/", "s1")
        await mgr.can_fetch("https://c.com/", "s1")

        assert len(fetch_fn.calls) == 6


# ---------------------------------------------------------------------------
# Tests: concurrent access (double-checked locking)
# ---------------------------------------------------------------------------


class TestConcurrency:
    @pytest.mark.asyncio
    async def test_concurrent_calls_same_domain_fetch_once(self):
        """Multiple concurrent tasks for the same new domain must only trigger one fetch."""
        fetch_count = 0

        async def slow_fetch(url: str, sid: str) -> MockResponse:
            nonlocal fetch_count
            fetch_count += 1
            await asyncio.sleep(0.02)  # simulate network latency
            return MockResponse(status=200, body=ROBOTS_BASIC.encode(), encoding="utf-8")

        mgr = RobotsTxtManager(slow_fetch)

        results = await asyncio.gather(*[
            mgr.can_fetch(f"https://example.com/page{i}", "s1")
            for i in range(8)
        ])

        assert fetch_count == 1
        assert all(isinstance(r, bool) for r in results)

    @pytest.mark.asyncio
    async def test_concurrent_calls_different_domains_fetch_independently(self):
        fetch_count = 0

        async def slow_fetch(url: str, sid: str) -> MockResponse:
            nonlocal fetch_count
            fetch_count += 1
            await asyncio.sleep(0.01)
            return MockResponse(status=200, body=b"", encoding="utf-8")

        mgr = RobotsTxtManager(slow_fetch)

        await asyncio.gather(
            mgr.can_fetch("https://alpha.com/", "s1"),
            mgr.can_fetch("https://beta.com/", "s1"),
            mgr.can_fetch("https://gamma.com/", "s1"),
        )

        assert fetch_count == 3

    @pytest.mark.asyncio
    async def test_concurrent_calls_consistent_results(self):
        """All concurrent callers should see the same allow/disallow result."""
        mgr = RobotsTxtManager(make_fetch_fn(content=ROBOTS_BASIC))

        results = await asyncio.gather(*[
            mgr.can_fetch("https://example.com/admin/", "s1")
            for _ in range(6)
        ])

        assert all(r is False for r in results)

    @pytest.mark.asyncio
    async def test_different_sids_concurrent_fetch_independently(self):
        fetch_count = 0

        async def slow_fetch(url: str, sid: str) -> MockResponse:
            nonlocal fetch_count
            fetch_count += 1
            await asyncio.sleep(0.01)
            return MockResponse(status=200, body=b"", encoding="utf-8")

        mgr = RobotsTxtManager(slow_fetch)

        await asyncio.gather(
            mgr.can_fetch("https://example.com/", "s1"),
            mgr.can_fetch("https://example.com/", "s2"),
            mgr.can_fetch("https://example.com/", "s3"),
        )

        assert fetch_count == 3
