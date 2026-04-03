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
from scrapling.core._types import Any, Dict, Set, AsyncGenerator


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
    def __init__(self, delay: float = 0.0):
        self._is_alive = False
        self._delay = delay

    async def __aenter__(self):
        self._is_alive = True
        return self

    async def __aexit__(self, *args):
        self._is_alive = False

    async def fetch(self, url: str, **kwargs):
        if self._delay:
            await anyio.sleep(self._delay)
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
        self.allowed_domains = set()
        self.fp_include_kwargs = False
        self.fp_include_headers = False
        self.fp_keep_fragments = False
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
            # Use a slow session so tasks are in-flight when we force-stop
            session = MockSession(delay=0.5)
            engine = _make_engine(spider, session, crawldir=tmpdir, interval=0)

            checkpoint_path = Path(tmpdir) / "checkpoint.pkl"

            async def force_stop_after_delay():
                """Simulate two rapid Ctrl+C presses."""
                # Wait for some tasks to start
                await anyio.sleep(0.1)
                engine.request_pause()  # First Ctrl+C
                await anyio.sleep(0.05)
                engine.request_pause()  # Second Ctrl+C (force stop)

            async with anyio.create_task_group() as tg:
                tg.start_soon(force_stop_after_delay)
                await engine.crawl()

            # The checkpoint file MUST exist after force-stop
            assert checkpoint_path.exists(), (
                "Checkpoint file was not saved (or was deleted) after force-stop. "
                "This means the cancel_scope.cancel() ran before _save_checkpoint()."
            )
            # Engine must report as paused
            assert engine.paused is True

    @pytest.mark.anyio
    async def test_graceful_pause_still_saves_checkpoint(self):
        """Single Ctrl+C (graceful pause) should save checkpoint as before."""
        with tempfile.TemporaryDirectory() as tmpdir:
            spider = SlowSpider(num_urls=5)
            session = MockSession(delay=0.3)
            engine = _make_engine(spider, session, crawldir=tmpdir, interval=0)

            checkpoint_path = Path(tmpdir) / "checkpoint.pkl"

            async def pause_after_delay():
                await anyio.sleep(0.1)
                engine.request_pause()

            async with anyio.create_task_group() as tg:
                tg.start_soon(pause_after_delay)
                await engine.crawl()

            assert checkpoint_path.exists(), "Checkpoint not saved on graceful pause"
            assert engine.paused is True

    @pytest.mark.anyio
    async def test_force_stop_checkpoint_is_loadable(self):
        """Checkpoint saved during force-stop must be valid and loadable."""
        with tempfile.TemporaryDirectory() as tmpdir:
            spider = SlowSpider(num_urls=15)
            session = MockSession(delay=0.4)
            engine = _make_engine(spider, session, crawldir=tmpdir, interval=0)

            async def force_stop():
                await anyio.sleep(0.1)
                engine.request_pause()
                await anyio.sleep(0.05)
                engine.request_pause()

            async with anyio.create_task_group() as tg:
                tg.start_soon(force_stop)
                await engine.crawl()

            # Load the checkpoint and verify it's valid
            manager = CheckpointManager(tmpdir)
            data = await manager.load()
            assert data is not None, "Checkpoint data could not be loaded"
            assert isinstance(data, CheckpointData)
            # seen set should have some entries (requests were enqueued)
            assert len(data.seen) > 0

    @pytest.mark.anyio
    async def test_normal_completion_cleans_up_checkpoint(self):
        """Normal completion (no pause) should still clean up checkpoint files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            spider = SlowSpider(num_urls=2)
            session = MockSession(delay=0.0)
            engine = _make_engine(spider, session, crawldir=tmpdir, interval=0)

            await engine.crawl()

            checkpoint_path = Path(tmpdir) / "checkpoint.pkl"
            # No pause → checkpoint should be cleaned up
            assert not checkpoint_path.exists()
            assert engine.paused is False

    @pytest.mark.anyio
    async def test_force_stop_without_checkpoint_system(self):
        """Force-stop without crawldir should not crash."""
        spider = SlowSpider(num_urls=10)
        session = MockSession(delay=0.3)
        engine = _make_engine(spider, session, crawldir=None)

        async def force_stop():
            await anyio.sleep(0.1)
            engine.request_pause()
            await anyio.sleep(0.05)
            engine.request_pause()

        async with anyio.create_task_group() as tg:
            tg.start_soon(force_stop)
            await engine.crawl()

        # Should not crash and should not be marked as paused
        # (no checkpoint system = no pause state)
        assert engine.paused is False

    @pytest.mark.anyio
    async def test_force_stop_preserves_existing_checkpoint(self):
        """If a checkpoint already exists, force-stop must not delete it."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # First run: do a graceful pause to create a checkpoint
            spider1 = SlowSpider(num_urls=10)
            session1 = MockSession(delay=0.2)
            engine1 = _make_engine(spider1, session1, crawldir=tmpdir, interval=0)

            async def pause1():
                await anyio.sleep(0.1)
                engine1.request_pause()

            async with anyio.create_task_group() as tg:
                tg.start_soon(pause1)
                await engine1.crawl()

            checkpoint_path = Path(tmpdir) / "checkpoint.pkl"
            assert checkpoint_path.exists(), "First run should create checkpoint"
            first_checkpoint_size = checkpoint_path.stat().st_size

            # Second run: force-stop (the fix ensures checkpoint is updated, not deleted)
            spider2 = SlowSpider(num_urls=10)
            session2 = MockSession(delay=0.3)
            engine2 = _make_engine(spider2, session2, crawldir=tmpdir, interval=0)

            async def force_stop2():
                await anyio.sleep(0.1)
                engine2.request_pause()
                await anyio.sleep(0.05)
                engine2.request_pause()

            async with anyio.create_task_group() as tg:
                tg.start_soon(force_stop2)
                await engine2.crawl()

            # Checkpoint must still exist (updated, not deleted)
            assert checkpoint_path.exists(), (
                "Force-stop deleted the checkpoint instead of preserving it"
            )
