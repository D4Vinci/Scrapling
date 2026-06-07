"""Tests for the ResponseCacheManager and development_mode integration."""

import tempfile
from pathlib import Path

import anyio
import pytest

from scrapling.spiders.cache import ResponseCacheManager
from scrapling.spiders.engine import CrawlerEngine
from scrapling.spiders.request import Request
from scrapling.spiders.session import SessionManager
from scrapling.engines.toolbelt.custom import Response
from scrapling.core._types import Any, Dict, Set, AsyncGenerator


def _make_response(url: str = "https://example.com", body: bytes = b"<html>hello</html>", status: int = 200) -> Response:
    return Response(
        url=url,
        content=body,
        status=status,
        reason="OK",
        encoding="utf-8",
        cookies={},
        headers={"content-type": "text/html"},
        request_headers={"user-agent": "test"},
        method="GET",
    )


class TestResponseCacheManager:

    @pytest.mark.anyio
    async def test_put_get_roundtrip(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            cache = ResponseCacheManager(tmpdir)
            fp = b"\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0a\x0b\x0c\x0d\x0e\x0f\x10\x11\x12\x13\x14"
            original = _make_response(body=b"<html>test content</html>")

            await cache.put(fp, original, "GET")
            restored = await cache.get(fp)

            assert restored is not None
            assert restored.url == original.url
            assert restored.body == original.body
            assert restored.status == original.status
            assert restored.reason == original.reason
            assert restored.encoding == original.encoding
            assert dict(restored.headers) == dict(original.headers)
            assert dict(restored.request_headers) == dict(original.request_headers)

    @pytest.mark.anyio
    async def test_put_overwrites_existing_entry(self):
        """Re-caching the same fingerprint must replace the stored response.

        Regression test for a Windows-only failure: ``Path.rename`` cannot
        overwrite an existing destination on Windows (raising ``WinError 183``),
        so the second ``put`` was caught by the error handler, the temp file was
        removed, and ``get`` kept returning the stale body. ``Path.replace``
        overwrites atomically on every platform.
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            cache = ResponseCacheManager(tmpdir)
            fp = b"\x05" * 20

            await cache.put(fp, _make_response(body=b"<html>first</html>"), "GET")
            await cache.put(fp, _make_response(body=b"<html>second</html>"), "GET")

            restored = await cache.get(fp)
            assert restored is not None
            assert restored.body == b"<html>second</html>"

    @pytest.mark.anyio
    async def test_get_cache_miss(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            cache = ResponseCacheManager(tmpdir)
            result = await cache.get(b"\x00" * 20)
            assert result is None

    @pytest.mark.anyio
    async def test_get_corrupt_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            cache = ResponseCacheManager(tmpdir)
            fp = b"\xaa" * 20
            corrupt_path = Path(tmpdir) / f"{fp.hex()}.json"
            corrupt_path.write_text("not valid json{{{")

            result = await cache.get(fp)
            assert result is None

    @pytest.mark.anyio
    async def test_clear(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            cache = ResponseCacheManager(tmpdir)
            fp1 = b"\x01" * 20
            fp2 = b"\x02" * 20

            await cache.put(fp1, _make_response(url="https://a.com"), "GET")
            await cache.put(fp2, _make_response(url="https://b.com"), "GET")

            assert await cache.get(fp1) is not None
            assert await cache.get(fp2) is not None

            await cache.clear()

            assert await cache.get(fp1) is None
            assert await cache.get(fp2) is None

    @pytest.mark.anyio
    async def test_creates_cache_dir(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            nested = Path(tmpdir) / "sub" / "dir"
            cache = ResponseCacheManager(str(nested))
            await cache.put(b"\x03" * 20, _make_response(), "GET")
            assert nested.exists()

    @pytest.mark.anyio
    async def test_preserves_binary_body(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            cache = ResponseCacheManager(tmpdir)
            fp = b"\x04" * 20
            binary_body = bytes(range(256))
            await cache.put(fp, _make_response(body=binary_body), "GET")
            restored = await cache.get(fp)
            assert restored is not None
            assert restored.body == binary_body


# ---------------------------------------------------------------------------
# Integration tests
# ---------------------------------------------------------------------------


class MockSession:
    def __init__(self):
        self._is_alive = False
        self.fetch_count = 0

    async def __aenter__(self):
        self._is_alive = True
        return self

    async def __aexit__(self, *args):
        self._is_alive = False

    async def fetch(self, url: str, **kwargs):
        self.fetch_count += 1
        return _make_response(url=url, body=b"<html>fetched</html>")


class _LogCounterStub:
    def get_counts(self) -> Dict[str, int]:
        return {"debug": 0, "info": 0, "warning": 0, "error": 0, "critical": 0}


class MockSpider:
    def __init__(self, cache_dir: str):
        self.concurrent_requests = 4
        self.concurrent_requests_per_domain = 0
        self.download_delay = 0.0
        self.max_blocked_retries = 3
        self.allowed_domains: Set[str] = set()
        self.fp_include_kwargs = False
        self.fp_include_headers = False
        self.fp_keep_fragments = False
        self.robots_txt_obey = False
        self.development_mode = True
        self.development_cache_dir = cache_dir
        self.start_urls: list[str] = []
        self.name = "test_cache_spider"
        self._log_counter = _LogCounterStub()
        self.scraped_items: list[dict] = []

    async def parse(self, response) -> AsyncGenerator[Dict[str, Any] | Request | None, None]:
        yield {"url": str(response)}

    async def on_start(self, resuming: bool = False) -> None:
        pass

    async def on_close(self) -> None:
        pass

    async def on_error(self, request: Request, error: Exception) -> None:
        pass

    async def on_scraped_item(self, item: Dict[str, Any]) -> Dict[str, Any] | None:
        self.scraped_items.append(item)
        return item

    async def is_blocked(self, response) -> bool:
        return False

    async def retry_blocked_request(self, request: Request, response) -> Request:
        return request

    async def start_requests(self) -> AsyncGenerator[Request, None]:
        yield Request("https://example.com/page1", sid="default")


class TestDevelopmentModeIntegration:

    @pytest.mark.anyio
    async def test_first_run_fetches_and_caches(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            session = MockSession()
            spider = MockSpider(cache_dir=tmpdir)
            sm = SessionManager()
            sm.add("default", session)
            engine = CrawlerEngine(spider, sm)

            await engine.crawl()

            assert session.fetch_count == 1
            assert engine.stats.cache_misses == 1
            assert engine.stats.cache_hits == 0
            assert engine.stats.items_scraped == 1

    @pytest.mark.anyio
    async def test_second_run_uses_cache(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            session = MockSession()
            spider = MockSpider(cache_dir=tmpdir)
            sm = SessionManager()
            sm.add("default", session)
            engine = CrawlerEngine(spider, sm)

            await engine.crawl()
            assert session.fetch_count == 1

            session2 = MockSession()
            spider2 = MockSpider(cache_dir=tmpdir)
            sm2 = SessionManager()
            sm2.add("default", session2)
            engine2 = CrawlerEngine(spider2, sm2)

            await engine2.crawl()
            assert session2.fetch_count == 0
            assert engine2.stats.cache_hits == 1
            assert engine2.stats.cache_misses == 0
            assert engine2.stats.items_scraped == 1

    @pytest.mark.anyio
    async def test_disabled_by_default(self):
        spider = MockSpider(cache_dir="unused")
        spider.development_mode = False
        sm = SessionManager()
        sm.add("default", MockSession())
        engine = CrawlerEngine(spider, sm)
        assert engine._cache_manager is None
