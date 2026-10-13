"""Adaptive persistence must support the same deep trees as Selector."""

from pathlib import Path

import pytest
from lxml.html import Element

from scrapling.core.storage import SQLiteStorageSystem


@pytest.mark.parametrize("depth", [1005, 1250])
def test_save_deep_element_path_without_python_recursion(tmp_path: Path, depth: int) -> None:
    """Round-trip a valid deep DOM with an independently constructed path."""
    root = Element("section")
    parent = root
    for _ in range(depth):
        child = Element("div")
        parent.append(child)
        parent = child
    target = Element("p")
    target.text = "Deep target"
    parent.append(target)
    storage = SQLiteStorageSystem(storage_file=str(tmp_path / "elements.db"))
    try:
        storage.save(target, "deep-target")

        saved = storage.retrieve("deep-target")
        assert saved is not None
        assert saved["path"] == ["section"] + ["div"] * depth + ["p"]
        assert saved["text"] == "Deep target"
    finally:
        storage.close()
