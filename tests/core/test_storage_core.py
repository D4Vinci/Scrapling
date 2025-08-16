import tempfile
import os

from scrapling.core.storage import SQLiteStorageSystem


class TestSQLiteStorageSystem:
    """Test SQLiteStorageSystem functionality"""
    
    def test_sqlite_storage_creation(self):
        """Test SQLite storage system creation"""
        # Use an in-memory database for testing
        storage = SQLiteStorageSystem(storage_file=":memory:")
        assert storage is not None
    
    def test_sqlite_storage_with_file(self):
        """Test SQLite storage with an actual file"""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp_file:
            db_path = tmp_file.name
        
        try:
            storage = SQLiteStorageSystem(storage_file=db_path)
            assert storage is not None
            assert os.path.exists(db_path)
        finally:
            if os.path.exists(db_path):
                os.unlink(db_path)
    
    def test_sqlite_storage_initialization_args(self):
        """Test SQLite storage with various initialization arguments"""
        # Test with URL parameter
        storage = SQLiteStorageSystem(
            storage_file=":memory:",
            url="https://example.com"
        )
        assert storage is not None
        assert storage.url == "https://example.com"
