import pickle
from pathlib import Path
from dataclasses import dataclass, field

import anyio
from anyio import Path as AsyncPath

from scrapling.core.utils import log
from scrapling.core._types import Set, List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from scrapling.spiders.request import Request


@dataclass
class CheckpointData:
    """Container for checkpoint state."""

    requests: List["Request"] = field(default_factory=list)
    seen: Set[bytes] = field(default_factory=set)


class CheckpointManager:
    """Manages saving and loading checkpoint state to/from disk."""

    CHECKPOINT_FILE = "checkpoint.pkl"

    def __init__(self, crawldir: str | Path | AsyncPath, interval: float = 300.0):
        self.crawldir = AsyncPath(crawldir)
        self._checkpoint_path = self.crawldir / self.CHECKPOINT_FILE
        self.interval = interval
        self._reported_failures: Set[str] = set()
        if not isinstance(interval, (int, float)):
            raise TypeError("Checkpoints interval must be integer or float.")
        else:
            if interval < 0:
                raise ValueError("Checkpoints interval must be equal or greater than 0.")

    async def has_checkpoint(self) -> bool:
        """Check if a checkpoint exists."""
        return await self._checkpoint_path.exists()

    async def save(self, data: CheckpointData, raise_on_error: bool = True) -> None:
        """Save checkpoint data to disk atomically.

        :param data: The checkpoint data to save.
        :param raise_on_error: If False, a failure is logged as a warning (once per distinct message) and swallowed,
            leaving the previous checkpoint, if any, untouched.
        """
        temp_path = self._checkpoint_path.with_suffix(".tmp")

        try:
            await self.crawldir.mkdir(parents=True, exist_ok=True)
            serialized = pickle.dumps(data, protocol=pickle.HIGHEST_PROTOCOL)
            async with await anyio.open_file(temp_path, "wb") as f:
                await f.write(serialized)

            await temp_path.replace(self._checkpoint_path)

            log.info(f"Checkpoint saved: {len(data.requests)} requests, {len(data.seen)} seen URLs")
        except Exception as e:
            # Clean up temp file if it exists
            if await temp_path.exists():
                await temp_path.unlink()
            if raise_on_error:
                log.error(f"Failed to save checkpoint: {e}")
                raise

            # A periodic save would otherwise repeat the same warning at every interval
            if str(e) not in self._reported_failures:
                self._reported_failures.add(str(e))
                log.warning(f"Failed to save checkpoint, the previous checkpoint, if any, is kept: {e}")

    async def load(self) -> Optional[CheckpointData]:
        """Load checkpoint data from disk.

        Returns None if no checkpoint exists or if loading fails.
        """
        if not await self.has_checkpoint():
            return None

        try:
            async with await anyio.open_file(self._checkpoint_path, "rb") as f:
                content = await f.read()
                data: CheckpointData = pickle.loads(content)

            log.info(f"Checkpoint loaded: {len(data.requests)} requests, {len(data.seen)} seen URLs")
            return data

        except Exception as e:
            log.error(f"Failed to load checkpoint (starting fresh): {e}")
            return None

    async def cleanup(self) -> None:
        """Delete checkpoint file after successful completion."""
        try:
            if await self._checkpoint_path.exists():
                await self._checkpoint_path.unlink()
            log.debug("Checkpoint file cleaned up")
        except Exception as e:
            log.warning(f"Failed to cleanup checkpoint file: {e}")
