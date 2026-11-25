"""Tests for force-stop checkpoint preservation in CrawlerEngine.

Regression tests for the bug where force-stop (second Ctrl+C) called
cancel_scope.cancel() BEFORE saving the checkpoint, causing:
1. _save_checkpoint() to be aborted by anyio's Cancelled exception
2. self.paused never set to True
3. The finally block to DELETE the previous checkpoint (cleanup runs on non-paused exit)

Total progress loss: user's checkpoint from a long crawl is irrecoverably deleted.
"""

import tempfile
from pathlib import Path

import anyio
import pytest

from scrapling.spiders.engine import CrawlerEngine
from scrapling.spiders.request import Request
from scrapling.spiders.session import SessionManager
from scrapling.spiders.checkpoint import CheckpointManager, CheckpointData
from scrapling.core._types import Any, Dict, AsyncGenerator


# ---------------------------------------------------------------------------
# Mock helpers (minimal, matching test_engine.py conventions)
# ---------------------------------------------------------------------------


class MockResponse:
    def __init__(self, status=200, body=b"ok", url="https://example.com"):
        self.status = status
        self.body = body
        self.url = url
        self.request: Any = None
        self.meta: Dict[str, Any] = {}

    def __str__(self):
        return self.url


class MockSession:
    def __init__(self, blocked: bool = False):
        self._is_alive = False
        self.started = anyio.Event()
        self.release = anyio.Event()
        if not blocked:
            self.release.set()

    async def __aenter__(self):
        self._is_alive = True
        return self

    async def __aexit__(self, *args):
        self._is_alive = False

    async def fetch(self, url: str, **kwargs):
        self.started.set()
        await self.release.wait()
        resp = MockResponse(url=url)
        return resp


class _LogCounterStub:
    def get_counts(self):
        return {"debug": 0, "info": 0, "warning": 0, "error": 0, "critical": 0}


class SlowSpider:
    """Spider with slow-responding requests to simulate in-flight tasks during force-stop."""

    def __init__(self, num_urls: int = 10):
        self.concurrent_requests = 4
        self.concurrent_requests_per_domain = 0
        self.download_delay = 0.0
        self.max_blocked_retries = 3
        self.autothrottle_enabled = False
        self.autothrottle_start_delay = 5.0
        self.autothrottle_max_delay = 60.0
        self.autothrottle_target_concurrency = None
        self.autothrottle_block_backoff = True
        self.allowed_domains = set()
        self.fp_include_kwargs = False
        self.fp_include_headers = False
        self.fp_keep_fragments = False
        self.robots_txt_obey = False
        self.development_mode = False
        self.development_cache_dir = None
        self.start_urls = []
        self.name = "slow_spider"
        self._log_counter = _LogCounterStub()
        self._num_urls = num_urls
        self.on_start_calls = []
        self.on_close_calls = 0

    async def parse(self, response) -> AsyncGenerator[Dict[str, Any] | Request | None, None]:
        yield {"url": str(response)}

    async def on_start(self, resuming=False):
        self.on_start_calls.append({"resuming": resuming})

    async def on_close(self):
        self.on_close_calls += 1

    async def on_error(self, request, error):
        pass

    async def on_scraped_item(self, item):
        return item

    async def is_blocked(self, response):
        return False

    async def retry_blocked_request(self, request, response):
        return request

    async def start_requests(self) -> AsyncGenerator[Request, None]:
        for i in range(self._num_urls):
            yield Request(f"https://example.com/page/{i}", sid="default")


def _make_engine(spider=None, session=None, crawldir=None, interval=300.0):
    spider = spider or SlowSpider()
    sm = SessionManager()
    sm.add("default", session or MockSession())
    return CrawlerEngine(spider, sm, crawldir=crawldir, interval=interval)


async def _crawl_until_pause(engine: CrawlerEngine, session: MockSession, force: bool = False):
    async def pause():
        await session.started.wait()
        engine.request_pause()
        if force:
            engine.request_pause()
        else:
            session.release.set()

    with anyio.fail_after(10):
        async with anyio.create_task_group() as group:
            group.start_soon(pause)
            await engine.crawl()


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestForceStopCheckpointPreservation:
    """Verify checkpoint is saved BEFORE cancel_scope.cancel() on force-stop."""

    @pytest.mark.anyio
    async def test_force_stop_saves_checkpoint_before_cancel(self):
        """Core regression test: force-stop must save checkpoint, not delete it."""
        with tempfile.TemporaryDirectory() as tmpdir:
            spider = SlowSpider(num_urls=20)
            session = MockSession(blocked=True)
            engine = _make_engine(spider, session, crawldir=tmpdir, interval=0)

            checkpoint_path = Path(tmpdir) / "checkpoint.pkl"

            await _crawl_until_pause(engine, session, force=True)

            # The checkpoint file MUST exist after force-stop
            assert checkpoint_path.exists(), (
                "Checkpoint file was not saved (or was deleted) after force-stop. "
                "This means the cancel_scope.cancel() ran before _save_checkpoint()."
            )
            # Engine must report as paused
            assert engine.paused is True
            data = await CheckpointManager(tmpdir).load()
            assert data is not None, "Checkpoint data could not be loaded"
            assert isinstance(data, CheckpointData)
            assert len(data.seen) > 0

    @pytest.mark.anyio
    async def test_graceful_pause_still_saves_checkpoint(self):
        """Single Ctrl+C (graceful pause) should save checkpoint as before."""
        with tempfile.TemporaryDirectory() as tmpdir:
            spider = SlowSpider(num_urls=5)
            session = MockSession(blocked=True)
            engine = _make_engine(spider, session, crawldir=tmpdir, interval=0)

            checkpoint_path = Path(tmpdir) / "checkpoint.pkl"

            await _crawl_until_pause(engine, session)

            assert checkpoint_path.exists(), "Checkpoint not saved on graceful pause"
            assert engine.paused is True

    @pytest.mark.anyio
    async def test_normal_completion_cleans_up_checkpoint(self):
        """Normal completion (no pause) should still clean up checkpoint files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            spider = SlowSpider(num_urls=2)
            session = MockSession()
            engine = _make_engine(spider, session, crawldir=tmpdir, interval=0)

            await engine.crawl()

            checkpoint_path = Path(tmpdir) / "checkpoint.pkl"
            # No pause → checkpoint should be cleaned up
            assert not checkpoint_path.exists()
            assert engine.paused is False

    @pytest.mark.anyio
    async def test_crash_keeps_checkpoint(self):
        """A crawl that ends with an exception must leave the checkpoint on disk."""

        class CrashingSpider(SlowSpider):
            async def is_blocked(self, response):
                if response.url.endswith("/page/5"):
                    raise RuntimeError("boom")
                return False

        with tempfile.TemporaryDirectory() as tmpdir:
            spider = CrashingSpider(num_urls=20)
            session = MockSession(blocked=True)
            engine = _make_engine(spider, session, crawldir=tmpdir, interval=0)

            async def save_before_crash():
                await session.started.wait()
                await engine._save_checkpoint()
                session.release.set()

            with anyio.fail_after(10):
                async with anyio.create_task_group() as group:
                    group.start_soon(save_before_crash)
                    with pytest.raises(Exception) as error:
                        await engine.crawl()
                    assert "boom" in repr(error.value)

            assert (Path(tmpdir) / "checkpoint.pkl").exists(), "Checkpoint was deleted after the crawl crashed"
            assert engine.paused is False
            assert spider.on_close_calls == 1

    @pytest.mark.anyio
    async def test_force_stop_without_checkpoint_system(self):
        """Force-stop without crawldir should not crash."""
        spider = SlowSpider(num_urls=10)
        session = MockSession(blocked=True)
        engine = _make_engine(spider, session, crawldir=None)

        await _crawl_until_pause(engine, session, force=True)

        # Should not crash and should not be marked as paused
        # (no checkpoint system = no pause state)
        assert engine.paused is False

    @pytest.mark.anyio
    async def test_force_stop_preserves_existing_checkpoint(self):
        """If a checkpoint already exists, force-stop must not delete it."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # First run: do a graceful pause to create a checkpoint
            spider1 = SlowSpider(num_urls=10)
            session1 = MockSession(blocked=True)
            engine1 = _make_engine(spider1, session1, crawldir=tmpdir, interval=0)

            await _crawl_until_pause(engine1, session1)

            checkpoint_path = Path(tmpdir) / "checkpoint.pkl"
            assert checkpoint_path.exists(), "First run should create checkpoint"

            # Second run: force-stop (the fix ensures checkpoint is updated, not deleted)
            spider2 = SlowSpider(num_urls=10)
            session2 = MockSession(blocked=True)
            engine2 = _make_engine(spider2, session2, crawldir=tmpdir, interval=0)

            await _crawl_until_pause(engine2, session2, force=True)

            # Checkpoint must still exist (updated, not deleted)
            assert checkpoint_path.exists(), (
                "Force-stop deleted the checkpoint instead of preserving it"
            )
