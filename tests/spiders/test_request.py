"""Tests for the Request class."""

import pickle

import pytest

from scrapling.spiders.request import Request
from scrapling.core._types import Any, Dict, AsyncGenerator


class TestRequestCreation:
    """Test Request initialization and basic attributes."""

    def test_basic_request_creation(self):
        """Test creating a request with just a URL."""
        request = Request("https://example.com")

        assert request.url == "https://example.com"
        assert request.sid == ""
        assert request.callback is None
        assert request.priority == 0
        assert request.dont_filter is False
        assert request.meta == {}
        assert request._retry_count == 0
        assert request._session_kwargs == {}

    def test_request_with_all_parameters(self):
        """Test creating a request with all parameters."""

        async def my_callback(response) -> AsyncGenerator[Dict[str, Any] | Request | None, None]:
            yield {"test": "data"}

        request = Request(
            url="https://example.com/page",
            sid="my_session",
            callback=my_callback,
            priority=10,
            dont_filter=True,
            meta={"key": "value"},
            _retry_count=2,
            proxy="http://proxy:8080",
            timeout=30,
        )

        assert request.url == "https://example.com/page"
        assert request.sid == "my_session"
        assert request.callback == my_callback
        assert request.priority == 10
        assert request.dont_filter is True
        assert request.meta == {"key": "value"}
        assert request._retry_count == 2
        assert request._session_kwargs == {"proxy": "http://proxy:8080", "timeout": 30}

    def test_request_meta_default_is_empty_dict(self):
        """Test that meta defaults to empty dict, not shared reference."""
        r1 = Request("https://example.com")
        r2 = Request("https://example.com")

        r1.meta["key"] = "value"

        assert r1.meta == {"key": "value"}
        assert r2.meta == {}


class TestRequestProperties:
    """Test Request computed properties."""

    def test_domain_extraction(self):
        """Test domain property extracts netloc correctly."""
        request = Request("https://www.example.com/path/page.html?query=1")
        assert request.domain == "www.example.com"

    def test_domain_with_port(self):
        """Test domain extraction with port number."""
        request = Request("http://localhost:8080/api")
        assert request.domain == "localhost:8080"

    def test_domain_with_subdomain(self):
        """Test domain extraction with subdomains."""
        request = Request("https://api.v2.example.com/endpoint")
        assert request.domain == "api.v2.example.com"

    def test_fingerprint_returns_bytes(self):
        """Test fingerprint generation returns bytes."""
        request = Request("https://example.com")
        fp = request.update_fingerprint()
        assert isinstance(fp, bytes)
        assert len(fp) == 20  # SHA1 produces 20 bytes

    def test_fingerprint_is_deterministic(self):
        """Test same request produces same fingerprint."""
        r1 = Request("https://example.com", data={"key": "value"})
        r2 = Request("https://example.com", data={"key": "value"})
        assert r1.update_fingerprint() == r2.update_fingerprint()

    def test_fingerprint_different_urls(self):
        """Test different URLs produce different fingerprints."""
        r1 = Request("https://example.com/page1")
        r2 = Request("https://example.com/page2")
        assert r1.update_fingerprint() != r2.update_fingerprint()


class TestRequestCopy:
    """Test Request copy functionality."""

    def test_copy_creates_independent_request(self):
        """Test that copy creates a new independent request."""

        async def callback(response) -> AsyncGenerator[Dict[str, Any] | Request | None, None]:
            yield None

        original = Request(
            url="https://example.com",
            sid="session",
            callback=callback,
            priority=5,
            dont_filter=True,
            meta={"original": True},
            _retry_count=1,
            proxy="http://proxy:8080",
        )

        copied = original.copy()

        # Check all values are copied
        assert copied.url == original.url
        assert copied.sid == original.sid
        assert copied.callback == original.callback
        assert copied.priority == original.priority
        assert copied.dont_filter == original.dont_filter
        assert copied.meta == original.meta
        assert copied._retry_count == original._retry_count
        assert copied._session_kwargs == original._session_kwargs

        # Check they are different objects
        assert copied is not original
        assert copied.meta is not original.meta  # Meta should be a copy

    def test_copy_meta_is_independent(self):
        """Test that modifying copied meta doesn't affect original."""
        original = Request("https://example.com", meta={"key": "original"})
        copied = original.copy()

        copied.meta["key"] = "modified"
        copied.meta["new_key"] = "new_value"

        assert original.meta == {"key": "original"}
        assert copied.meta == {"key": "modified", "new_key": "new_value"}


class TestRequestComparison:
    """Test Request comparison operators."""

    def test_priority_less_than(self):
        """Test less than comparison by priority."""
        low_priority = Request("https://example.com/1", priority=1)
        high_priority = Request("https://example.com/2", priority=10)

        assert low_priority < high_priority
        assert not high_priority < low_priority

    def test_priority_greater_than(self):
        """Test greater than comparison by priority."""
        low_priority = Request("https://example.com/1", priority=1)
        high_priority = Request("https://example.com/2", priority=10)

        assert high_priority > low_priority
        assert not low_priority > high_priority

    def test_equality_by_fingerprint(self):
        """Test equality comparison by fingerprint."""
        r1 = Request("https://example.com")
        r2 = Request("https://example.com")
        r3 = Request("https://example.com/other")

        # Generate fingerprints first (required for equality)
        r1.update_fingerprint()
        r2.update_fingerprint()
        r3.update_fingerprint()

        assert r1 == r2
        assert r1 != r3

    def test_equality_different_priorities_same_fingerprint(self):
        """Test requests with same fingerprint are equal despite different priorities."""
        r1 = Request("https://example.com", priority=1)
        r2 = Request("https://example.com", priority=100)

        # Generate fingerprints first
        r1.update_fingerprint()
        r2.update_fingerprint()

        assert r1 == r2  # Same fingerprint means equal

    def test_comparison_with_non_request(self):
        """Test comparison with non-Request types returns NotImplemented."""
        request = Request("https://example.com")

        assert request.__lt__("not a request") == NotImplemented
        assert request.__gt__("not a request") == NotImplemented
        assert request.__eq__("not a request") == NotImplemented


class TestRequestStringRepresentation:
    """Test Request string representations."""

    def test_str_returns_url(self):
        """Test __str__ returns the URL."""
        request = Request("https://example.com/page")
        assert str(request) == "https://example.com/page"

    def test_repr_without_callback(self):
        """Test __repr__ without callback."""
        request = Request("https://example.com", priority=5)
        repr_str = repr(request)

        assert "Request" in repr_str
        assert "https://example.com" in repr_str
        assert "priority=5" in repr_str
        assert "callback=None" in repr_str

    def test_repr_with_callback(self):
        """Test __repr__ with named callback."""

        async def my_custom_callback(response) -> AsyncGenerator[Dict[str, Any] | Request | None, None]:
            yield None

        request = Request("https://example.com", callback=my_custom_callback)
        repr_str = repr(request)

        assert "callback=my_custom_callback" in repr_str


class TestRequestPickling:
    """Test Request serialization for checkpointing."""

    def test_pickle_without_callback(self):
        """Test pickling request without callback."""
        original = Request(
            url="https://example.com",
            sid="session",
            priority=5,
            meta={"key": "value"},
        )

        pickled = pickle.dumps(original)
        restored = pickle.loads(pickled)

        assert restored.url == original.url
        assert restored.sid == original.sid
        assert restored.priority == original.priority
        assert restored.meta == original.meta
        assert restored.callback is None

    def test_pickle_with_callback_stores_name(self):
        """Test that callback name is stored when pickling."""

        async def parse_page(response) -> AsyncGenerator[Dict[str, Any] | Request | None, None]:
            yield {"data": "test"}

        original = Request("https://example.com", callback=parse_page)

        # Check getstate stores callback name
        state = original.__getstate__()
        assert state["_callback_name"] == "parse_page"
        assert state["callback"] is None

    def test_pickle_with_none_callback(self):
        """Test pickling with None callback."""
        original = Request("https://example.com", callback=None)

        state = original.__getstate__()
        assert state["_callback_name"] is None
        assert state["callback"] is None

    def test_setstate_stores_callback_name(self):
        """Test that setstate correctly handles callback name."""
        request = Request("https://example.com")
        state = {
            "url": "https://example.com",
            "sid": "",
            "callback": None,
            "priority": 0,
            "dont_filter": False,
            "meta": {},
            "_retry_count": 0,
            "_session_kwargs": {},
            "_callback_name": "custom_parse",
        }

        request.__setstate__(state)

        assert hasattr(request, "_callback_name")
        assert request._callback_name == "custom_parse"

    def test_pickle_roundtrip_preserves_session_kwargs(self):
        """Test that session kwargs are preserved through pickle."""
        original = Request(
            "https://example.com",
            proxy="http://proxy:8080",
            timeout=30,
            headers={"User-Agent": "test"},
        )

        pickled = pickle.dumps(original)
        restored = pickle.loads(pickled)

        assert restored._session_kwargs == {
            "proxy": "http://proxy:8080",
            "timeout": 30,
            "headers": {"User-Agent": "test"},
        }


class TestRequestRestoreCallback:
    """Test callback restoration from spider."""

    def test_restore_callback_from_spider(self):
        """Test restoring callback from spider instance."""

        class MockSpider:
            async def parse(self, response) -> AsyncGenerator[Dict[str, Any] | Request | None, None]:
                yield None

            async def parse_detail(self, response) -> AsyncGenerator[Dict[str, Any] | Request | None, None]:
                yield {"detail": True}

        spider = MockSpider()
        request = Request("https://example.com")
        request._callback_name = "parse_detail"

        request._restore_callback(spider)  # type: ignore[arg-type]

        assert request.callback == spider.parse_detail
        assert not hasattr(request, "_callback_name")

    def test_restore_callback_falls_back_to_parse(self):
        """Test that missing callback falls back to spider.parse."""

        class MockSpider:
            async def parse(self, response) -> AsyncGenerator[Dict[str, Any] | Request | None, None]:
                yield None

        spider = MockSpider()
        request = Request("https://example.com")
        request._callback_name = "nonexistent_method"

        request._restore_callback(spider)  # type: ignore[arg-type]

        assert request.callback == spider.parse
        assert not hasattr(request, "_callback_name")

    def test_restore_callback_with_none_name(self):
        """Test restore callback when _callback_name is None."""

        class MockSpider:
            async def parse(self, response) -> AsyncGenerator[Dict[str, Any] | Request | None, None]:
                yield None

        spider = MockSpider()
        request = Request("https://example.com")
        request._callback_name = None

        request._restore_callback(spider)  # type: ignore[arg-type]

        # Should clean up _callback_name attribute
        assert not hasattr(request, "_callback_name")

    def test_restore_callback_without_callback_name_attr(self):
        """Test restore callback when _callback_name attribute doesn't exist."""

        class MockSpider:
            async def parse(self, response) -> AsyncGenerator[Dict[str, Any] | Request | None, None]:
                yield None

        spider = MockSpider()
        request = Request("https://example.com")
        # Don't set _callback_name

        # Should not raise an error
        request._restore_callback(spider)  # type: ignore[arg-type]
