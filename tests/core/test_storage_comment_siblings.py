"""Retained comments must not make adaptive element data unserializable."""

from pathlib import Path

from scrapling import Selector
from scrapling.core.storage import SQLiteStorageSystem


def test_adaptive_save_round_trips_with_comment_siblings(tmp_path: Path) -> None:
    """Keep comments in the page while storing only element sibling tags."""
    storage = SQLiteStorageSystem(storage_file=str(tmp_path / "elements.db"))
    try:
        page = Selector(
            "<div><!--before--><p id='target'>Widget</p><!--after--><span>Other</span></div>",
            adaptive=True,
            keep_comments=True,
            _storage=storage,
        )
        page.css("#target", auto_save=True)

        saved = page.retrieve("#target")
        assert saved is not None
        assert saved["text"] == "Widget"
        assert saved["siblings"] == ["span"]
    finally:
        storage.close()
