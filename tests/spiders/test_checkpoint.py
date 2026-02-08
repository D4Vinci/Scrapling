"""Tests for the CheckpointManager and CheckpointData classes."""

import pickle
import tempfile
from pathlib import Path

import pytest
import anyio

from scrapling.spiders.request import Request
from scrapling.spiders.checkpoint import CheckpointData, CheckpointManager


class TestCheckpointData:
    """Test CheckpointData dataclass."""

    def test_default_values(self):
        """Test CheckpointData with default values."""
        data = CheckpointData()

        assert data.requests == []
        assert data.seen == set()

    def test_with_requests_and_seen(self):
        """Test CheckpointData with requests and seen URLs."""
        requests = [
            Request("https://example.com/1", priority=10),
            Request("https://example.com/2", priority=5),
        ]
        seen = {"url1", "url2", "url3"}

        data = CheckpointData(requests=requests, seen=seen)

        assert len(data.requests) == 2
        assert data.requests[0].url == "https://example.com/1"
        assert data.seen == {"url1", "url2", "url3"}

    def test_pickle_roundtrip(self):
        """Test that CheckpointData can be pickled and unpickled."""
        requests = [Request("https://example.com", priority=5)]
        seen = {"fingerprint1", "fingerprint2"}
        data = CheckpointData(requests=requests, seen=seen)

        pickled = pickle.dumps(data)
        restored = pickle.loads(pickled)

        assert len(restored.requests) == 1
        assert restored.requests[0].url == "https://example.com"
        assert restored.seen == {"fingerprint1", "fingerprint2"}


class TestCheckpointManagerInit:
    """Test CheckpointManager initialization."""

    def test_init_with_string_path(self):
        """Test initialization with string path."""
        manager = CheckpointManager("/tmp/test_crawl")

        assert str(manager.crawldir) == "/tmp/test_crawl"
        assert manager.interval == 300.0

    def test_init_with_pathlib_path(self):
        """Test initialization with pathlib.Path."""
        path = Path("/tmp/test_crawl")
        manager = CheckpointManager(path)

        assert str(manager.crawldir) == "/tmp/test_crawl"

    def test_init_with_custom_interval(self):
        """Test initialization with custom interval."""
        manager = CheckpointManager("/tmp/test", interval=60.0)
        assert manager.interval == 60.0

    def test_init_with_zero_interval(self):
        """Test initialization with zero interval (disable periodic checkpoints)."""
        manager = CheckpointManager("/tmp/test", interval=0)
        assert manager.interval == 0

    def test_init_with_negative_interval_raises(self):
        """Test that negative interval raises ValueError."""
        with pytest.raises(ValueError, match="greater than 0"):
            CheckpointManager("/tmp/test", interval=-1)

    def test_init_with_invalid_interval_type_raises(self):
        """Test that invalid interval type raises TypeError."""
        with pytest.raises(TypeError, match="integer or float"):
            CheckpointManager("/tmp/test", interval="invalid")  # type: ignore

    def test_checkpoint_file_path(self):
        """Test that checkpoint file path is correctly constructed."""
        manager = CheckpointManager("/tmp/test_crawl")

        expected_path = "/tmp/test_crawl/checkpoint.pkl"
        assert str(manager._checkpoint_path) == expected_path


class TestCheckpointManagerOperations:
    """Test CheckpointManager save/load/cleanup operations."""

    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for testing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    @pytest.mark.asyncio
    async def test_has_checkpoint_false_when_no_file(self, temp_dir: Path):
        """Test has_checkpoint returns False when no checkpoint exists."""
        manager = CheckpointManager(temp_dir / "crawl")

        result = await manager.has_checkpoint()

        assert result is False

    @pytest.mark.asyncio
    async def test_save_creates_checkpoint_file(self, temp_dir: Path):
        """Test that save creates the checkpoint file."""
        crawl_dir = temp_dir / "crawl"
        manager = CheckpointManager(crawl_dir)

        data = CheckpointData(
            requests=[Request("https://example.com")],
            seen={"fp1", "fp2"},
        )

        await manager.save(data)

        checkpoint_path = crawl_dir / "checkpoint.pkl"
        assert checkpoint_path.exists()

    @pytest.mark.asyncio
    async def test_save_creates_directory_if_not_exists(self, temp_dir: Path):
        """Test that save creates the directory if it doesn't exist."""
        crawl_dir = temp_dir / "nested" / "crawl" / "dir"
        manager = CheckpointManager(crawl_dir)

        data = CheckpointData()
        await manager.save(data)

        assert crawl_dir.exists()

    @pytest.mark.asyncio
    async def test_has_checkpoint_true_after_save(self, temp_dir: Path):
        """Test has_checkpoint returns True after saving."""
        manager = CheckpointManager(temp_dir / "crawl")

        data = CheckpointData()
        await manager.save(data)

        result = await manager.has_checkpoint()
        assert result is True

    @pytest.mark.asyncio
    async def test_load_returns_none_when_no_checkpoint(self, temp_dir: Path):
        """Test load returns None when no checkpoint exists."""
        manager = CheckpointManager(temp_dir / "crawl")

        result = await manager.load()

        assert result is None

    @pytest.mark.asyncio
    async def test_save_and_load_roundtrip(self, temp_dir: Path):
        """Test saving and loading checkpoint data."""
        manager = CheckpointManager(temp_dir / "crawl")

        original_data = CheckpointData(
            requests=[
                Request("https://example.com/1", priority=10),
                Request("https://example.com/2", priority=5),
            ],
            seen={"fp1", "fp2", "fp3"},
        )

        await manager.save(original_data)
        loaded_data = await manager.load()

        assert loaded_data is not None
        assert len(loaded_data.requests) == 2
        assert loaded_data.requests[0].url == "https://example.com/1"
        assert loaded_data.requests[0].priority == 10
        assert loaded_data.seen == {"fp1", "fp2", "fp3"}

    @pytest.mark.asyncio
    async def test_save_is_atomic(self, temp_dir: Path):
        """Test that save uses atomic write (temp file + rename)."""
        crawl_dir = temp_dir / "crawl"
        manager = CheckpointManager(crawl_dir)

        data = CheckpointData(requests=[Request("https://example.com")])
        await manager.save(data)

        # Temp file should not exist after successful save
        temp_path = crawl_dir / "checkpoint.tmp"
        assert not temp_path.exists()

        # Checkpoint file should exist
        checkpoint_path = crawl_dir / "checkpoint.pkl"
        assert checkpoint_path.exists()

    @pytest.mark.asyncio
    async def test_cleanup_removes_checkpoint_file(self, temp_dir: Path):
        """Test that cleanup removes the checkpoint file."""
        crawl_dir = temp_dir / "crawl"
        manager = CheckpointManager(crawl_dir)

        # Save a checkpoint first
        data = CheckpointData()
        await manager.save(data)

        checkpoint_path = crawl_dir / "checkpoint.pkl"
        assert checkpoint_path.exists()

        # Cleanup should remove it
        await manager.cleanup()

        assert not checkpoint_path.exists()

    @pytest.mark.asyncio
    async def test_cleanup_no_error_when_no_file(self, temp_dir: Path):
        """Test that cleanup doesn't raise error when no file exists."""
        manager = CheckpointManager(temp_dir / "crawl")

        # Should not raise
        await manager.cleanup()

    @pytest.mark.asyncio
    async def test_load_returns_none_on_corrupt_file(self, temp_dir: Path):
        """Test load returns None when checkpoint file is corrupt."""
        crawl_dir = temp_dir / "crawl"
        crawl_dir.mkdir(parents=True)

        checkpoint_path = crawl_dir / "checkpoint.pkl"
        checkpoint_path.write_bytes(b"not valid pickle data")

        manager = CheckpointManager(crawl_dir)

        result = await manager.load()

        assert result is None

    @pytest.mark.asyncio
    async def test_multiple_saves_overwrite(self, temp_dir: Path):
        """Test that multiple saves overwrite the checkpoint."""
        manager = CheckpointManager(temp_dir / "crawl")

        # First save
        data1 = CheckpointData(
            requests=[Request("https://example.com/1")],
            seen={"fp1"},
        )
        await manager.save(data1)

        # Second save
        data2 = CheckpointData(
            requests=[Request("https://example.com/2"), Request("https://example.com/3")],
            seen={"fp2", "fp3"},
        )
        await manager.save(data2)

        # Load should return the second save
        loaded = await manager.load()

        assert loaded is not None
        assert len(loaded.requests) == 2
        assert loaded.requests[0].url == "https://example.com/2"
        assert loaded.seen == {"fp2", "fp3"}


class TestCheckpointManagerEdgeCases:
    """Test edge cases for CheckpointManager."""

    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for testing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    @pytest.mark.asyncio
    async def test_save_empty_checkpoint(self, temp_dir: Path):
        """Test saving empty checkpoint data."""
        manager = CheckpointManager(temp_dir / "crawl")

        data = CheckpointData(requests=[], seen=set())
        await manager.save(data)

        loaded = await manager.load()

        assert loaded is not None
        assert loaded.requests == []
        assert loaded.seen == set()

    @pytest.mark.asyncio
    async def test_save_large_checkpoint(self, temp_dir: Path):
        """Test saving checkpoint with many requests."""
        manager = CheckpointManager(temp_dir / "crawl")

        # Create 1000 requests
        requests = [
            Request(f"https://example.com/{i}", priority=i % 10)
            for i in range(1000)
        ]
        seen = {f"fp_{i}" for i in range(2000)}

        data = CheckpointData(requests=requests, seen=seen)
        await manager.save(data)

        loaded = await manager.load()

        assert loaded is not None
        assert len(loaded.requests) == 1000
        assert len(loaded.seen) == 2000

    @pytest.mark.asyncio
    async def test_requests_preserve_metadata(self, temp_dir: Path):
        """Test that request metadata is preserved through checkpoint."""
        manager = CheckpointManager(temp_dir / "crawl")

        original_request = Request(
            url="https://example.com",
            sid="my_session",
            priority=42,
            dont_filter=True,
            meta={"item_id": 123, "page": 5},
            proxy="http://proxy:8080",
        )

        data = CheckpointData(requests=[original_request], seen=set())
        await manager.save(data)

        loaded = await manager.load()

        assert loaded is not None
        restored = loaded.requests[0]

        assert restored.url == "https://example.com"
        assert restored.sid == "my_session"
        assert restored.priority == 42
        assert restored.dont_filter is True
        assert restored.meta == {"item_id": 123, "page": 5}
        assert restored._session_kwargs == {"proxy": "http://proxy:8080"}
