import tempfile
import os
import threading

from lxml.html import fromstring

from scrapling.core.storage import SQLiteStorageSystem, StorageSystemMixin
from scrapling.core.utils import _StorageTools


class TestGetBaseUrl:
    """Test StorageSystemMixin._get_base_url()"""

    def _make_storage(self, url=None):
        # Clear lru_cache between tests to avoid cross-test pollution
        StorageSystemMixin._get_base_url.cache_clear()
        return SQLiteStorageSystem(storage_file=":memory:", url=url)

    def test_returns_default_when_url_is_none(self):
        storage = self._make_storage(url=None)
        assert storage._get_base_url() == "default"

    def test_returns_default_when_url_is_empty(self):
        storage = self._make_storage(url="")
        assert storage._get_base_url() == "default"

    def test_returns_fld_for_valid_url(self):
        storage = self._make_storage(url="https://www.example.com/page")
        result = storage._get_base_url()
        assert result == "example.com"

    def test_url_is_lowercased(self):
        storage = self._make_storage(url="https://WWW.EXAMPLE.COM/Page")
        assert storage.url == "https://www.example.com/page"


class TestGetHash:
    """Test StorageSystemMixin._get_hash()"""

    def setup_method(self):
        StorageSystemMixin._get_hash.cache_clear()

    def test_deterministic_output(self):
        h1 = StorageSystemMixin._get_hash("test-identifier")
        h2 = StorageSystemMixin._get_hash("test-identifier")
        assert h1 == h2

    def test_different_input_different_output(self):
        h1 = StorageSystemMixin._get_hash("identifier-a")
        h2 = StorageSystemMixin._get_hash("identifier-b")
        assert h1 != h2

    def test_strips_and_lowercases(self):
        h1 = StorageSystemMixin._get_hash("  Hello  ")
        h2 = StorageSystemMixin._get_hash("hello")
        assert h1 == h2

    def test_includes_length_suffix(self):
        result = StorageSystemMixin._get_hash("test")
        # Format: {sha256_hex}_{byte_length}
        assert "_" in result
        hex_part, length_part = result.rsplit("_", 1)
        assert len(hex_part) == 64  # SHA-256 hex length
        assert length_part == str(len("test".encode("utf-8")))


class TestSQLiteStorageSystem:
    """Test SQLiteStorageSystem functionality"""

    def test_sqlite_storage_creation(self):
        """Test SQLite storage system creation"""
        storage = SQLiteStorageSystem(storage_file=":memory:")
        assert storage is not None

    def test_sqlite_storage_with_file(self):
        """Test SQLite storage with an actual file"""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp_file:
            db_path = tmp_file.name

        storage = None
        try:
            storage = SQLiteStorageSystem(storage_file=db_path)
            assert storage is not None
            assert os.path.exists(db_path)
        finally:
            if storage is not None:
                storage.close()
            if os.path.exists(db_path):
                os.unlink(db_path)

    def test_sqlite_storage_initialization_args(self):
        """Test SQLite storage with various initialization arguments"""
        storage = SQLiteStorageSystem(
            storage_file=":memory:",
            url="https://example.com"
        )
        assert storage is not None
        assert storage.url == "https://example.com"


class TestSaveRetrieveRoundTrip:
    """Test the save/retrieve round-trip — the core of the adaptive feature."""

    def _make_storage(self, url="https://example.com"):
        StorageSystemMixin._get_base_url.cache_clear()
        SQLiteStorageSystem.cache_clear()
        return SQLiteStorageSystem(storage_file=":memory:", url=url)

    def _make_element(self, html_str="<div><p id='target' class='main'>Hello</p></div>"):
        tree = fromstring(html_str)
        return tree.cssselect("p")[0] if tree.cssselect("p") else tree

    def test_save_and_retrieve(self):
        storage = self._make_storage()
        element = self._make_element()
        storage.save(element, "test-element")

        result = storage.retrieve("test-element")
        assert result is not None
        assert result["tag"] == "p"
        assert result["attributes"]["id"] == "target"
        assert result["attributes"]["class"] == "main"
        assert result["text"] == "Hello"

    def test_retrieve_nonexistent_returns_none(self):
        storage = self._make_storage()
        assert storage.retrieve("does-not-exist") is None

    def test_save_overwrites_existing(self):
        storage = self._make_storage()
        elem1 = self._make_element("<div><p id='v1'>First</p></div>")
        elem2 = self._make_element("<div><p id='v2'>Second</p></div>")

        storage.save(elem1, "my-element")
        storage.save(elem2, "my-element")

        result = storage.retrieve("my-element")
        assert result is not None
        assert result["attributes"]["id"] == "v2"
        assert result["text"] == "Second"

    def test_url_isolation(self):
        """Elements saved under one URL should not be retrievable under another."""
        SQLiteStorageSystem.cache_clear()
        StorageSystemMixin._get_base_url.cache_clear()

        # Use file-based storage so both instances share the same DB
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            db_path = tmp.name

        try:
            storage_a = SQLiteStorageSystem(storage_file=db_path, url="https://site-a.com")
            element = self._make_element()
            storage_a.save(element, "shared-id")

            SQLiteStorageSystem.cache_clear()
            StorageSystemMixin._get_base_url.cache_clear()

            storage_b = SQLiteStorageSystem(storage_file=db_path, url="https://site-b.com")
            assert storage_b.retrieve("shared-id") is None
        finally:
            storage_a.close()
            storage_b.close()
            if os.path.exists(db_path):
                os.unlink(db_path)

    def test_element_path_is_stored(self):
        storage = self._make_storage()
        element = self._make_element("<html><body><div><p>Text</p></div></body></html>")
        storage.save(element, "path-test")

        result = storage.retrieve("path-test")
        assert result is not None
        assert "path" in result
        # Path should be a list of tag names from root to element
        assert result["path"][-1] == "p"

    def test_element_without_parent(self):
        """A root element (no parent) should still be savable."""
        storage = self._make_storage()
        tree = fromstring("<div>Root element</div>")
        storage.save(tree, "root-elem")

        result = storage.retrieve("root-elem")
        assert result is not None
        assert "parent_name" not in result

    def test_element_with_children_and_siblings(self):
        storage = self._make_storage()
        html_str = "<div><p>Sibling</p><span id='target'><b>Child</b><i>Child2</i></span></div>"
        tree = fromstring(html_str)
        element = tree.cssselect("#target")[0]
        storage.save(element, "with-children")

        result = storage.retrieve("with-children")
        assert result is not None
        assert "children" in result
        assert "b" in result["children"]
        assert "i" in result["children"]
        assert "siblings" in result
        assert "p" in result["siblings"]


class TestStorageThreadSafety:
    """Test that SQLiteStorageSystem is safe under concurrent access."""

    def test_concurrent_saves(self):
        SQLiteStorageSystem.cache_clear()
        StorageSystemMixin._get_base_url.cache_clear()

        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            db_path = tmp.name

        storage = SQLiteStorageSystem(storage_file=db_path, url="https://example.com")
        errors = []

        def save_element(idx):
            try:
                html_str = f"<div><p id='elem-{idx}'>Text {idx}</p></div>"
                tree = fromstring(html_str)
                element = tree.cssselect("p")[0]
                storage.save(element, f"element-{idx}")
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=save_element, args=(i,)) for i in range(20)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(errors) == 0, f"Thread safety errors: {errors}"

        # Verify all elements were saved
        for i in range(20):
            result = storage.retrieve(f"element-{i}")
            assert result is not None, f"element-{i} not found after concurrent save"

        storage.close()
        if os.path.exists(db_path):
            os.unlink(db_path)


class TestStorageToolsElementToDict:
    """Test _StorageTools.element_to_dict() directly."""

    def test_basic_element(self):
        tree = fromstring("<div><p class='foo'>Hello</p></div>")
        elem = tree.cssselect("p")[0]
        result = _StorageTools.element_to_dict(elem)

        assert result["tag"] == "p"
        assert result["attributes"]["class"] == "foo"
        assert result["text"] == "Hello"
        assert "parent_name" in result
        assert result["parent_name"] == "div"

    def test_element_no_text(self):
        tree = fromstring("<div><p class='empty'></p></div>")
        elem = tree.cssselect("p")[0]
        result = _StorageTools.element_to_dict(elem)
        assert result["text"] is None

    def test_element_no_attributes(self):
        tree = fromstring("<div><p>Plain</p></div>")
        elem = tree.cssselect("p")[0]
        result = _StorageTools.element_to_dict(elem)
        assert result["attributes"] == {}

    def test_element_strips_whitespace_attributes(self):
        tree = fromstring('<div><p data-val="  "></p></div>')
        elem = tree.cssselect("p")[0]
        result = _StorageTools.element_to_dict(elem)
        # Whitespace-only attribute values should be filtered out
        assert "data-val" not in result["attributes"]


class TestStorageToolsGetElementPath:
    """Test _StorageTools._get_element_path()."""

    def test_nested_path(self):
        tree = fromstring("<html><body><div><p>Text</p></div></body></html>")
        elem = tree.cssselect("p")[0]
        path = _StorageTools._get_element_path(elem)
        assert path[-1] == "p"
        assert "div" in path
        assert "body" in path

    def test_root_element_path(self):
        tree = fromstring("<div>Root</div>")
        path = _StorageTools._get_element_path(tree)
        assert path == ("div",)
