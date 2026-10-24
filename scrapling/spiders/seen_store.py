import sqlite3
from time import time
from pathlib import Path

from scrapling.core.utils import log
from scrapling.core._types import Optional


class SeenStore:
    """A SQLite file of the request fingerprints whose callback produced items, kept between runs so a spider that
    runs on a schedule doesn't download those pages again."""

    def __init__(self, path: str | Path):
        self.path = Path(path)
        self._connection: Optional[sqlite3.Connection] = None

    def open(self) -> sqlite3.Connection:
        """Open the database (creating it if needed). Errors are raised, so a bad path fails the crawl at the start."""
        if self._connection is None:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            connection = sqlite3.connect(self.path)
            # WAL lets another process read the file while this one writes, and NORMAL only syncs at checkpoints
            connection.execute("PRAGMA journal_mode=WAL")
            connection.execute("PRAGMA synchronous=NORMAL")
            connection.execute(
                "CREATE TABLE IF NOT EXISTS seen (fingerprint BLOB PRIMARY KEY, seen_at REAL NOT NULL) WITHOUT ROWID"
            )
            connection.commit()
            self._connection = connection
            return connection
        return self._connection

    def close(self) -> None:
        if self._connection is not None:
            self._connection.close()
            self._connection = None

    def __contains__(self, fingerprint: object) -> bool:
        try:
            row = self.open().execute("SELECT 1 FROM seen WHERE fingerprint = ?", (fingerprint,)).fetchone()
        except sqlite3.Error as e:
            log.warning(f"Failed to look up a fingerprint in {self.path}, treating it as unseen: {e}")
            return False
        return row is not None

    def add(self, fingerprint: bytes) -> None:
        """Remember a fingerprint. A failure only means the page gets downloaded again on the next run."""
        try:
            connection = self.open()
            connection.execute(
                "INSERT OR IGNORE INTO seen (fingerprint, seen_at) VALUES (?, ?)",
                (fingerprint, time()),
            )
            connection.commit()
        except sqlite3.Error as e:
            log.warning(f"Failed to save a fingerprint to {self.path}: {e}")

    def __len__(self) -> int:
        return self.open().execute("SELECT COUNT(*) FROM seen").fetchone()[0]

    def clear(self) -> None:
        connection = self.open()
        connection.execute("DELETE FROM seen")
        connection.commit()
        log.info(f"Cleared seen fingerprints at {self.path}")
