from pathlib import Path
from dataclasses import dataclass, field
from datetime import datetime, timezone

import anyio
import orjson
from anyio import Path as AsyncPath

from scrapling.core.utils import log
from scrapling.core._types import Set, List, Optional, Mapping, Any
from scrapling.spiders.request import Request


@dataclass
class CheckpointData:
    """Container for checkpoint state."""

    requests: List[Request] = field(default_factory=list)
    seen: Set[bytes] = field(default_factory=set)


class CheckpointManager:
    """Manages saving and loading checkpoint state to/from disk.

    Checkpoints are stored as JSON instead of pickle so resuming a crawl never
    deserializes executable Python objects from disk. The file is chmod 600
    because request kwargs may still contain proxy credentials or auth headers.
    """

    CHECKPOINT_FILE = "checkpoint.json"
    LEGACY_PICKLE_FILE = "checkpoint.pkl"

    def __init__(
        self,
        crawldir: str | Path | AsyncPath,
        interval: float = 300.0,
        callback_registry: Optional[Mapping[str, Any]] = None,
        store_secrets: bool = False,
    ):
        self.crawldir = AsyncPath(crawldir)
        self._checkpoint_path = self.crawldir / self.CHECKPOINT_FILE
        self._legacy_checkpoint_path = self.crawldir / self.LEGACY_PICKLE_FILE
        self._callback_registry = dict(callback_registry or {})
        self.store_secrets = bool(store_secrets)
        self.interval = interval
        if not isinstance(interval, (int, float)):
            raise TypeError("Checkpoints interval must be integer or float.")
        else:
            if interval < 0:
                raise ValueError("Checkpoints interval must be equal or greater than 0.")

    def set_callback_registry(self, callback_registry: Mapping[str, Any]) -> None:
        """Set or replace callback names used when restoring Request objects."""
        self._callback_registry = dict(callback_registry)

    async def has_checkpoint(self) -> bool:
        """Check if a checkpoint exists."""
        return await self._checkpoint_path.exists()

    @staticmethod
    def _encode(data: CheckpointData, *, store_secrets: bool = False) -> bytes:
        return orjson.dumps(
            {
                "version": 1,
                "requests": [request.to_state(store_secrets=store_secrets) for request in data.requests],
                "seen": sorted(fp.hex() for fp in data.seen),
            }
        )

    def _decode(self, content: bytes) -> CheckpointData:
        payload = orjson.loads(content)
        if not isinstance(payload, dict):
            raise ValueError("Checkpoint payload must be a JSON object")
        if payload.get("version") != 1:
            raise ValueError(f"Unsupported checkpoint version: {payload.get('version')!r}")
        raw_requests = payload.get("requests", [])
        raw_seen = payload.get("seen", [])
        if not isinstance(raw_requests, list) or not isinstance(raw_seen, list):
            raise ValueError("Checkpoint requests/seen fields must be lists")
        requests = [
            Request.from_state(state, self._callback_registry)
            for state in raw_requests
            if isinstance(state, dict)
        ]
        seen = {bytes.fromhex(fp) for fp in raw_seen if isinstance(fp, str)}
        return CheckpointData(requests=requests, seen=seen)

    async def save(self, data: CheckpointData) -> None:
        """Save checkpoint data to disk atomically."""
        await self.crawldir.mkdir(parents=True, exist_ok=True)

        temp_path = self._checkpoint_path.with_suffix(".tmp")

        try:
            serialized = self._encode(data, store_secrets=self.store_secrets)
            async with await anyio.open_file(temp_path, "wb") as f:
                await f.write(serialized)

            await temp_path.rename(self._checkpoint_path)
            await anyio.to_thread.run_sync(lambda: Path(str(self._checkpoint_path)).chmod(0o600))

            log.info(f"Checkpoint saved: {len(data.requests)} requests, {len(data.seen)} seen URLs")
        except Exception as e:
            # Clean up temp file if it exists
            if await temp_path.exists():
                await temp_path.unlink()
            log.error(f"Failed to save checkpoint: {e}")
            raise

    async def _quarantine_invalid_checkpoint(self) -> None:
        """Move a corrupt checkpoint aside for inspection instead of retrying it forever."""
        if not await self._checkpoint_path.exists():
            return
        stamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
        target = self.crawldir / f"{self.CHECKPOINT_FILE}.invalid.{stamp}"
        try:
            await self._checkpoint_path.rename(target)
            log.warning("Corrupt checkpoint quarantined at %s", target)
        except Exception as exc:
            log.warning("Failed to quarantine corrupt checkpoint: %s", exc)

    async def load(self) -> Optional[CheckpointData]:
        """Load checkpoint data from disk.

        Returns None if no checkpoint exists or if loading fails.
        Legacy pickle checkpoints are intentionally not loaded because that
        would re-introduce arbitrary-code-execution risk during resume.
        """
        if not await self.has_checkpoint():
            if await self._legacy_checkpoint_path.exists():
                log.warning("Ignoring legacy pickle checkpoint; start fresh or re-run with a JSON checkpoint.")
            return None

        try:
            async with await anyio.open_file(self._checkpoint_path, "rb") as f:
                content = await f.read()
                data = self._decode(content)

            log.info(f"Checkpoint loaded: {len(data.requests)} requests, {len(data.seen)} seen URLs")
            return data

        except Exception as e:
            log.error(f"Failed to load checkpoint (starting fresh): {e}")
            await self._quarantine_invalid_checkpoint()
            return None

    async def cleanup(self) -> None:
        """Delete checkpoint files after successful completion."""
        try:
            if await self._checkpoint_path.exists():
                await self._checkpoint_path.unlink()
            if await self._legacy_checkpoint_path.exists():
                await self._legacy_checkpoint_path.unlink()
            log.debug("Checkpoint file cleaned up")
        except Exception as e:
            log.warning(f"Failed to cleanup checkpoint file: {e}")
