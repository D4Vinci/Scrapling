"""Tests for pickle-free checkpoint persistence."""

import os
import stat
import tempfile
from pathlib import Path

import orjson
import pytest

from scrapling.spiders.checkpoint import CheckpointData, CheckpointManager
from scrapling.spiders.request import Request


class TestCheckpointData:
    """Test CheckpointData dataclass."""

    def test_default_values(self):
        data = CheckpointData()
        assert data.requests == []
        assert data.seen == set()

    def test_with_requests_and_seen(self):
        requests = [
            Request("https://example.com/1", priority=10),
            Request("https://example.com/2", priority=5),
        ]
        seen = {b"url1", b"url2", b"url3"}

        data = CheckpointData(requests=requests, seen=seen)

        assert len(data.requests) == 2
        assert data.requests[0].url == "https://example.com/1"
        assert data.seen == {b"url1", b"url2", b"url3"}

    def test_json_encoding_is_plain_data(self):
        data = CheckpointData(requests=[Request("https://example.com", priority=5)], seen={b"fingerprint"})

        payload = orjson.loads(CheckpointManager._encode(data))

        assert payload["version"] == 1
        assert payload["requests"][0]["url"] == "https://example.com"
        assert payload["seen"] == [b"fingerprint".hex()]


class TestCheckpointManagerInit:
    """Test CheckpointManager initialization."""

    def test_init_with_string_path(self):
        manager = CheckpointManager("/tmp/test_crawl")
        assert str(manager.crawldir) == "/tmp/test_crawl"
        assert manager.interval == 300.0

    def test_init_with_pathlib_path(self):
        path = Path("/tmp/test_crawl")
        manager = CheckpointManager(path)
        assert str(manager.crawldir) == "/tmp/test_crawl"

    def test_init_with_custom_interval(self):
        manager = CheckpointManager("/tmp/test", interval=60.0)
        assert manager.interval == 60.0

    def test_init_with_zero_interval(self):
        manager = CheckpointManager("/tmp/test", interval=0)
        assert manager.interval == 0

    def test_init_with_negative_interval_raises(self):
        with pytest.raises(ValueError, match="greater than 0"):
            CheckpointManager("/tmp/test", interval=-1)

    def test_init_with_invalid_interval_type_raises(self):
        with pytest.raises(TypeError, match="integer or float"):
            CheckpointManager("/tmp/test", interval="invalid")  # type: ignore[arg-type]

    def test_checkpoint_file_path(self):
        manager = CheckpointManager("/tmp/test_crawl")
        assert str(manager._checkpoint_path) == "/tmp/test_crawl/checkpoint.json"


class TestCheckpointManagerOperations:
    """Test CheckpointManager save/load/cleanup operations."""

    @pytest.fixture
    def temp_dir(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    @pytest.mark.asyncio
    async def test_has_checkpoint_false_when_no_file(self, temp_dir: Path):
        manager = CheckpointManager(temp_dir / "crawl")
        assert await manager.has_checkpoint() is False

    @pytest.mark.asyncio
    async def test_save_creates_checkpoint_file_with_private_permissions(self, temp_dir: Path):
        crawl_dir = temp_dir / "crawl"
        manager = CheckpointManager(crawl_dir)
        data = CheckpointData(requests=[Request("https://example.com")], seen={b"fp1", b"fp2"})

        await manager.save(data)

        checkpoint_path = crawl_dir / "checkpoint.json"
        assert checkpoint_path.exists()
        assert stat.S_IMODE(os.stat(checkpoint_path).st_mode) == 0o600
        assert orjson.loads(checkpoint_path.read_bytes())["seen"] == sorted([b"fp1".hex(), b"fp2".hex()])

    @pytest.mark.asyncio
    async def test_save_creates_directory_if_not_exists(self, temp_dir: Path):
        crawl_dir = temp_dir / "nested" / "crawl" / "dir"
        manager = CheckpointManager(crawl_dir)
        await manager.save(CheckpointData())
        assert crawl_dir.exists()

    @pytest.mark.asyncio
    async def test_has_checkpoint_true_after_save(self, temp_dir: Path):
        manager = CheckpointManager(temp_dir / "crawl")
        await manager.save(CheckpointData())
        assert await manager.has_checkpoint() is True

    @pytest.mark.asyncio
    async def test_load_returns_none_when_no_checkpoint(self, temp_dir: Path):
        manager = CheckpointManager(temp_dir / "crawl")
        assert await manager.load() is None

    @pytest.mark.asyncio
    async def test_save_and_load_roundtrip(self, temp_dir: Path):
        manager = CheckpointManager(temp_dir / "crawl")
        original_data = CheckpointData(
            requests=[
                Request("https://example.com/1", priority=10),
                Request("https://example.com/2", priority=5),
            ],
            seen={b"fp1", b"fp2", b"fp3"},
        )

        await manager.save(original_data)
        loaded_data = await manager.load()

        assert loaded_data is not None
        assert len(loaded_data.requests) == 2
        assert loaded_data.requests[0].url == "https://example.com/1"
        assert loaded_data.requests[0].priority == 10
        assert loaded_data.seen == {b"fp1", b"fp2", b"fp3"}

    @pytest.mark.asyncio
    async def test_save_is_atomic(self, temp_dir: Path):
        crawl_dir = temp_dir / "crawl"
        manager = CheckpointManager(crawl_dir)

        await manager.save(CheckpointData(requests=[Request("https://example.com")]))

        assert not (crawl_dir / "checkpoint.tmp").exists()
        assert (crawl_dir / "checkpoint.json").exists()

    @pytest.mark.asyncio
    async def test_cleanup_removes_checkpoint_files(self, temp_dir: Path):
        crawl_dir = temp_dir / "crawl"
        manager = CheckpointManager(crawl_dir)
        await manager.save(CheckpointData())
        (crawl_dir / "checkpoint.pkl").write_bytes(b"legacy pickle must not be loaded")

        await manager.cleanup()

        assert not (crawl_dir / "checkpoint.json").exists()
        assert not (crawl_dir / "checkpoint.pkl").exists()

    @pytest.mark.asyncio
    async def test_cleanup_no_error_when_no_file(self, temp_dir: Path):
        manager = CheckpointManager(temp_dir / "crawl")
        await manager.cleanup()

    @pytest.mark.asyncio
    async def test_load_returns_none_on_corrupt_json_file(self, temp_dir: Path):
        crawl_dir = temp_dir / "crawl"
        crawl_dir.mkdir(parents=True)
        (crawl_dir / "checkpoint.json").write_bytes(b"not valid json")

        manager = CheckpointManager(crawl_dir)
        assert await manager.load() is None

    @pytest.mark.asyncio
    async def test_legacy_pickle_checkpoint_is_ignored(self, temp_dir: Path):
        crawl_dir = temp_dir / "crawl"
        crawl_dir.mkdir(parents=True)
        (crawl_dir / "checkpoint.pkl").write_bytes(b"\x80\x04unsafe")

        manager = CheckpointManager(crawl_dir)
        assert await manager.load() is None

    @pytest.mark.asyncio
    async def test_multiple_saves_overwrite(self, temp_dir: Path):
        manager = CheckpointManager(temp_dir / "crawl")
        await manager.save(CheckpointData(requests=[Request("https://example.com/1")], seen={b"fp1"}))
        await manager.save(
            CheckpointData(
                requests=[Request("https://example.com/2"), Request("https://example.com/3")],
                seen={b"fp2", b"fp3"},
            )
        )

        loaded = await manager.load()

        assert loaded is not None
        assert len(loaded.requests) == 2
        assert loaded.requests[0].url == "https://example.com/2"
        assert loaded.seen == {b"fp2", b"fp3"}


class TestCheckpointManagerEdgeCases:
    """Test edge cases for CheckpointManager."""

    @pytest.fixture
    def temp_dir(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    @pytest.mark.asyncio
    async def test_save_empty_checkpoint(self, temp_dir: Path):
        manager = CheckpointManager(temp_dir / "crawl")
        await manager.save(CheckpointData(requests=[], seen=set()))
        loaded = await manager.load()
        assert loaded is not None
        assert loaded.requests == []
        assert loaded.seen == set()

    @pytest.mark.asyncio
    async def test_save_large_checkpoint(self, temp_dir: Path):
        manager = CheckpointManager(temp_dir / "crawl")
        requests = [Request(f"https://example.com/{i}", priority=i % 10) for i in range(1000)]
        seen = {f"fp_{i}".encode() for i in range(2000)}

        await manager.save(CheckpointData(requests=requests, seen=seen))
        loaded = await manager.load()

        assert loaded is not None
        assert len(loaded.requests) == 1000
        assert len(loaded.seen) == 2000

    @pytest.mark.asyncio
    async def test_requests_preserve_metadata(self, temp_dir: Path):
        manager = CheckpointManager(temp_dir / "crawl")
        original_request = Request(
            url="https://example.com",
            sid="my_session",
            priority=42,
            dont_filter=True,
            meta={"item_id": 123, "page": 5},
            proxy="http://proxy:8080",
        )

        await manager.save(CheckpointData(requests=[original_request], seen=set()))
        loaded = await manager.load()

        assert loaded is not None
        restored = loaded.requests[0]
        assert restored.url == "https://example.com"
        assert restored.sid == "my_session"
        assert restored.priority == 42
        assert restored.dont_filter is True
        assert restored.meta == {"item_id": 123, "page": 5}
        assert restored._session_kwargs == {"proxy": "http://proxy:8080"}

    @pytest.mark.asyncio
    async def test_checkpoint_redacts_secrets_by_default_and_normalizes_unjsonable_meta(self, temp_dir: Path):
        manager = CheckpointManager(temp_dir / "crawl")
        request = Request(
            "https://example.com",
            meta={"raw": {"a", "b"}, "token": "secret-token", "callback": lambda: None},
            proxy="http://user:pass@proxy.local:8080",
            headers={"Authorization": "Bearer secret", "Accept": "text/html"},
            data=b"payload",
        )

        await manager.save(CheckpointData(requests=[request], seen=set()))
        payload = orjson.loads((temp_dir / "crawl" / "checkpoint.json").read_bytes())
        text = (temp_dir / "crawl" / "checkpoint.json").read_text()
        assert "pass" not in text
        assert "secret-token" not in text
        assert "Bearer secret" not in text
        state = payload["requests"][0]
        assert state["_session_kwargs"]["proxy"] == "http://***@proxy.local:8080"
        assert state["_session_kwargs"]["headers"]["Authorization"] == "***"
        assert state["_session_kwargs"]["data"]["__type__"] == "bytes"

    @pytest.mark.asyncio
    async def test_corrupt_checkpoint_is_quarantined(self, temp_dir: Path):
        crawl_dir = temp_dir / "crawl"
        crawl_dir.mkdir(parents=True)
        (crawl_dir / "checkpoint.json").write_bytes(b"not-json")
        manager = CheckpointManager(crawl_dir)

        assert await manager.load() is None
        assert not (crawl_dir / "checkpoint.json").exists()
        assert list(crawl_dir.glob("checkpoint.json.invalid.*"))
