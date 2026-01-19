"""Tests for the Scheduler class."""

import pytest

from scrapling.spiders.request import Request
from scrapling.spiders.scheduler import Scheduler
from scrapling.spiders.checkpoint import CheckpointData


class TestSchedulerInit:
    """Test Scheduler initialization."""

    def test_scheduler_starts_empty(self):
        """Test that scheduler starts with empty queue."""
        scheduler = Scheduler()

        assert len(scheduler) == 0
        assert scheduler.is_empty is True


class TestSchedulerEnqueue:
    """Test Scheduler enqueue functionality."""

    @pytest.mark.asyncio
    async def test_enqueue_single_request(self):
        """Test enqueueing a single request."""
        scheduler = Scheduler()
        request = Request("https://example.com")

        result = await scheduler.enqueue(request)

        assert result is True
        assert len(scheduler) == 1
        assert scheduler.is_empty is False

    @pytest.mark.asyncio
    async def test_enqueue_multiple_requests(self):
        """Test enqueueing multiple requests."""
        scheduler = Scheduler()

        for i in range(5):
            request = Request(f"https://example.com/{i}")
            await scheduler.enqueue(request)

        assert len(scheduler) == 5

    @pytest.mark.asyncio
    async def test_enqueue_duplicate_filtered(self):
        """Test that duplicate requests are filtered by default."""
        scheduler = Scheduler()

        request1 = Request("https://example.com", sid="s1")
        request2 = Request("https://example.com", sid="s1")  # Same fingerprint

        result1 = await scheduler.enqueue(request1)
        result2 = await scheduler.enqueue(request2)

        assert result1 is True
        assert result2 is False  # Duplicate filtered
        assert len(scheduler) == 1

    @pytest.mark.asyncio
    async def test_enqueue_duplicate_allowed_with_dont_filter(self):
        """Test that dont_filter allows duplicate requests."""
        scheduler = Scheduler()

        request1 = Request("https://example.com", sid="s1")
        request2 = Request("https://example.com", sid="s1", dont_filter=True)

        result1 = await scheduler.enqueue(request1)
        result2 = await scheduler.enqueue(request2)

        assert result1 is True
        assert result2 is True
        assert len(scheduler) == 2

    @pytest.mark.asyncio
    async def test_enqueue_different_sessions_not_duplicate(self):
        """Test that same URL with different sessions are not duplicates."""
        scheduler = Scheduler()

        request1 = Request("https://example.com", sid="session1")
        request2 = Request("https://example.com", sid="session2")

        result1 = await scheduler.enqueue(request1)
        result2 = await scheduler.enqueue(request2)

        assert result1 is True
        assert result2 is True
        assert len(scheduler) == 2


class TestSchedulerDequeue:
    """Test Scheduler dequeue functionality."""

    @pytest.mark.asyncio
    async def test_dequeue_returns_request(self):
        """Test that dequeue returns the enqueued request."""
        scheduler = Scheduler()
        original = Request("https://example.com")

        await scheduler.enqueue(original)
        dequeued = await scheduler.dequeue()

        assert dequeued.url == original.url

    @pytest.mark.asyncio
    async def test_dequeue_respects_priority_order(self):
        """Test that higher priority requests are dequeued first."""
        scheduler = Scheduler()

        low = Request("https://example.com/low", priority=1)
        high = Request("https://example.com/high", priority=10)
        medium = Request("https://example.com/medium", priority=5)

        await scheduler.enqueue(low)
        await scheduler.enqueue(high)
        await scheduler.enqueue(medium)

        # Should get high priority first
        first = await scheduler.dequeue()
        assert first.url == "https://example.com/high"

        second = await scheduler.dequeue()
        assert second.url == "https://example.com/medium"

        third = await scheduler.dequeue()
        assert third.url == "https://example.com/low"

    @pytest.mark.asyncio
    async def test_dequeue_fifo_for_same_priority(self):
        """Test FIFO ordering for requests with same priority."""
        scheduler = Scheduler()

        for i in range(3):
            request = Request(f"https://example.com/{i}", priority=5)
            await scheduler.enqueue(request)

        first = await scheduler.dequeue()
        second = await scheduler.dequeue()
        third = await scheduler.dequeue()

        # Should be in FIFO order since same priority
        assert first.url == "https://example.com/0"
        assert second.url == "https://example.com/1"
        assert third.url == "https://example.com/2"

    @pytest.mark.asyncio
    async def test_dequeue_updates_length(self):
        """Test that dequeue decreases the queue length."""
        scheduler = Scheduler()

        await scheduler.enqueue(Request("https://example.com/1"))
        await scheduler.enqueue(Request("https://example.com/2"))

        assert len(scheduler) == 2

        await scheduler.dequeue()
        assert len(scheduler) == 1

        await scheduler.dequeue()
        assert len(scheduler) == 0
        assert scheduler.is_empty is True


class TestSchedulerSnapshot:
    """Test Scheduler snapshot functionality for checkpointing."""

    @pytest.mark.asyncio
    async def test_snapshot_empty_scheduler(self):
        """Test snapshot of empty scheduler."""
        scheduler = Scheduler()

        requests, seen = scheduler.snapshot()

        assert requests == []
        assert seen == set()

    @pytest.mark.asyncio
    async def test_snapshot_captures_pending_requests(self):
        """Test snapshot captures all pending requests."""
        scheduler = Scheduler()

        await scheduler.enqueue(Request("https://example.com/1", priority=5))
        await scheduler.enqueue(Request("https://example.com/2", priority=10))
        await scheduler.enqueue(Request("https://example.com/3", priority=1))

        requests, seen = scheduler.snapshot()

        assert len(requests) == 3
        # Should be sorted by priority (highest first due to negative priority in queue)
        assert requests[0].url == "https://example.com/2"  # priority 10
        assert requests[1].url == "https://example.com/1"  # priority 5
        assert requests[2].url == "https://example.com/3"  # priority 1

    @pytest.mark.asyncio
    async def test_snapshot_captures_seen_set(self):
        """Test snapshot captures seen URLs."""
        scheduler = Scheduler()

        await scheduler.enqueue(Request("https://example.com/1", sid="s1"))
        await scheduler.enqueue(Request("https://example.com/2", sid="s1"))

        requests, seen = scheduler.snapshot()

        assert len(seen) == 2
        assert "s1:https://example.com/1" in seen
        assert "s1:https://example.com/2" in seen

    @pytest.mark.asyncio
    async def test_snapshot_returns_copies(self):
        """Test that snapshot returns copies, not references."""
        scheduler = Scheduler()

        await scheduler.enqueue(Request("https://example.com"))

        requests, seen = scheduler.snapshot()

        # Modifying snapshot shouldn't affect scheduler
        requests.append(Request("https://modified.com"))
        seen.add("new_fingerprint")

        original_requests, original_seen = scheduler.snapshot()

        assert len(original_requests) == 1
        assert "new_fingerprint" not in original_seen

    @pytest.mark.asyncio
    async def test_snapshot_excludes_dequeued_requests(self):
        """Test snapshot only includes pending requests."""
        scheduler = Scheduler()

        await scheduler.enqueue(Request("https://example.com/1"))
        await scheduler.enqueue(Request("https://example.com/2"))
        await scheduler.enqueue(Request("https://example.com/3"))

        # Dequeue one
        await scheduler.dequeue()

        requests, seen = scheduler.snapshot()

        # Snapshot should only have 2 pending requests
        assert len(requests) == 2
        # But seen should still have all 3 (deduplication tracking)
        assert len(seen) == 3


class TestSchedulerRestore:
    """Test Scheduler restore functionality from checkpoint."""

    @pytest.mark.asyncio
    async def test_restore_requests(self):
        """Test restoring requests from checkpoint data."""
        scheduler = Scheduler()

        checkpoint_requests = [
            Request("https://example.com/1", priority=10),
            Request("https://example.com/2", priority=5),
        ]
        checkpoint_seen = {"fp1", "fp2", "fp3"}

        data = CheckpointData(requests=checkpoint_requests, seen=checkpoint_seen)

        scheduler.restore(data)

        assert len(scheduler) == 2

    @pytest.mark.asyncio
    async def test_restore_seen_set(self):
        """Test that restore sets up seen fingerprints."""
        scheduler = Scheduler()

        data = CheckpointData(
            requests=[],
            seen={"fp1", "fp2"},
        )

        scheduler.restore(data)

        # Now try to enqueue a request with matching fingerprint
        request = Request("https://example.com")
        request.sid = ""  # Empty sid
        # Manually set fingerprint that matches seen
        # Since fingerprint is sid:url, we need to create matching ones

        # Verify seen set was restored
        _, seen = scheduler.snapshot()
        assert seen == {"fp1", "fp2"}

    @pytest.mark.asyncio
    async def test_restore_maintains_priority_order(self):
        """Test that restored requests maintain priority order."""
        scheduler = Scheduler()

        # Requests should already be sorted by priority in checkpoint
        checkpoint_requests = [
            Request("https://example.com/high", priority=10),
            Request("https://example.com/low", priority=1),
        ]

        data = CheckpointData(requests=checkpoint_requests, seen=set())
        scheduler.restore(data)

        # Dequeue should return high priority first
        first = await scheduler.dequeue()
        assert first.url == "https://example.com/high"

        second = await scheduler.dequeue()
        assert second.url == "https://example.com/low"

    @pytest.mark.asyncio
    async def test_restore_empty_checkpoint(self):
        """Test restoring from empty checkpoint."""
        scheduler = Scheduler()

        data = CheckpointData(requests=[], seen=set())
        scheduler.restore(data)

        assert len(scheduler) == 0
        assert scheduler.is_empty is True


class TestSchedulerIntegration:
    """Integration tests for Scheduler with checkpoint roundtrip."""

    @pytest.mark.asyncio
    async def test_snapshot_and_restore_roundtrip(self):
        """Test that snapshot -> restore works correctly."""
        # Create and populate original scheduler
        original = Scheduler()

        await original.enqueue(Request("https://example.com/1", sid="s1", priority=10))
        await original.enqueue(Request("https://example.com/2", sid="s1", priority=5))
        await original.enqueue(Request("https://example.com/3", sid="s2", priority=7))

        # Snapshot
        requests, seen = original.snapshot()
        data = CheckpointData(requests=requests, seen=seen)

        # Restore to new scheduler
        restored = Scheduler()
        restored.restore(data)

        # Verify state matches
        assert len(restored) == len(original)

        # Dequeue from both and compare
        for _ in range(3):
            orig_req = await original.dequeue()
            rest_req = await restored.dequeue()
            assert orig_req.url == rest_req.url
            assert orig_req.priority == rest_req.priority

    @pytest.mark.asyncio
    async def test_partial_processing_then_checkpoint(self):
        """Test checkpointing after partial processing."""
        scheduler = Scheduler()

        # Enqueue 5 requests
        for i in range(5):
            await scheduler.enqueue(Request(f"https://example.com/{i}"))

        # Process 2
        await scheduler.dequeue()
        await scheduler.dequeue()

        # Snapshot should show 3 pending, 5 seen
        requests, seen = scheduler.snapshot()

        assert len(requests) == 3
        assert len(seen) == 5

    @pytest.mark.asyncio
    async def test_deduplication_after_restore(self):
        """Test that deduplication works after restore."""
        scheduler = Scheduler()

        await scheduler.enqueue(Request("https://example.com", sid="s1"))

        requests, seen = scheduler.snapshot()
        data = CheckpointData(requests=requests, seen=seen)

        # Restore to new scheduler
        new_scheduler = Scheduler()
        new_scheduler.restore(data)

        # Try to add duplicate - should be filtered
        result = await new_scheduler.enqueue(Request("https://example.com", sid="s1"))

        assert result is False  # Duplicate filtered based on restored seen set
