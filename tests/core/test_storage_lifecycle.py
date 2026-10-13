"""Closed adaptive storage must be safe to close again and reopen."""

from pathlib import Path

from lxml.html import fromstring

from scrapling.core.storage import SQLiteStorageSystem


def test_close_can_be_called_more_than_once(tmp_path: Path) -> None:
    """Cleanup paths may explicitly close before object destruction."""
    storage = SQLiteStorageSystem(storage_file=str(tmp_path / "elements.db"))

    storage.close()
    storage.close()


def test_constructor_reopens_closed_cached_storage(tmp_path: Path) -> None:
    """A later crawl must be able to open the same database after cleanup."""
    path = str(tmp_path / "elements.db")
    storage = SQLiteStorageSystem(storage_file=path, url="https://example.com")
    storage.save(fromstring("<p>Saved before close</p>"), "target")
    storage.close()

    reopened = SQLiteStorageSystem(storage_file=path, url="https://example.com")
    try:
        saved = reopened.retrieve("target")
        assert saved is not None
        assert saved["text"] == "Saved before close"
        reopened.save(fromstring("<p>Saved after reopen</p>"), "new")
        assert reopened.retrieve("new")["text"] == "Saved after reopen"
    finally:
        if reopened is not storage:
            reopened.close()


def test_closing_older_storage_preserves_another_open_cached_instance() -> None:
    """Closing one database must not evict a different live in-memory database."""
    first = SQLiteStorageSystem(storage_file=":memory:", url="https://first.example.com")
    second = SQLiteStorageSystem(storage_file=":memory:", url="https://second.example.com")
    try:
        second.save(fromstring("<p>Still here</p>"), "target")
        first.close()

        assert SQLiteStorageSystem(storage_file=":memory:", url="https://second.example.com") is second
        assert second.retrieve("target")["text"] == "Still here"
    finally:
        second.close()
