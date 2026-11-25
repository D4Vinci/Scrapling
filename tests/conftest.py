from pathlib import Path

import pytest

from scrapling import parser
from scrapling.core._types import Iterator
from scrapling.core.storage import SQLiteStorageSystem


@pytest.fixture(autouse=True)
def isolated_adaptive_storage(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> Iterator[None]:
    monkeypatch.setattr(parser, "__DEFAULT_DB_FILE__", str(tmp_path / "adaptive.db"))
    getattr(SQLiteStorageSystem, "cache_clear")()
    yield
    getattr(SQLiteStorageSystem, "cache_clear")()
