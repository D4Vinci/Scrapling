import sqlite3
import threading
from abc import ABC, abstractmethod
from hashlib import sha256

import orjson
from lxml import html
from tldextract import extract as tld

from scrapling.core._types import Dict, Optional, Union
from scrapling.core.utils import _StorageTools, log, lru_cache


class StorageSystemMixin(ABC):
    # If you want to make your own storage system, you have to inherit from this
    def __init__(self, url: Union[str, None] = None):
        """
        :param url: URL of the website we are working on to separate it from other websites data
        """
        self.url = url

    @lru_cache(None, typed=True)
    def _get_base_url(self, default_value: str = 'default') -> str:
        if not self.url or type(self.url) is not str:
            return default_value

        try:
            extracted = tld(self.url)
            return extracted.registered_domain or extracted.domain or default_value
        except AttributeError:
            return default_value

    @abstractmethod
    def save(self, element: html.HtmlElement, identifier: str) -> None:
        """Saves the element's unique properties to the storage for retrieval and relocation later

        :param element: The element itself that we want to save to storage.
        :param identifier: This is the identifier that will be used to retrieve the element later from the storage. See
            the docs for more info.
        """
        raise NotImplementedError('Storage system must implement `save` method')

    @abstractmethod
    def retrieve(self, identifier: str) -> Optional[Dict]:
        """Using the identifier, we search the storage and return the unique properties of the element

        :param identifier: This is the identifier that will be used to retrieve the element from the storage. See
            the docs for more info.
        :return: A dictionary of the unique properties
        """
        raise NotImplementedError('Storage system must implement `save` method')

    @staticmethod
    @lru_cache(None, typed=True)
    def _get_hash(identifier: str) -> str:
        """If you want to hash identifier in your storage system, use this safer"""
        identifier = identifier.lower().strip()
        if isinstance(identifier, str):
            # Hash functions have to take bytes
            identifier = identifier.encode('utf-8')

        hash_value = sha256(identifier).hexdigest()
        return f"{hash_value}_{len(identifier)}"  # Length to reduce collision chance


@lru_cache(None, typed=True)
class SQLiteStorageSystem(StorageSystemMixin):
    """The recommended system to use, it's race condition safe and thread safe.
    Mainly built so the library can run in threaded frameworks like scrapy or threaded tools
    > It's optimized for threaded applications but running it without threads shouldn't make it slow."""
    def __init__(self, storage_file: str, url: Union[str, None] = None):
        """
        :param storage_file: File to be used to store elements
        :param url: URL of the website we are working on to separate it from other websites data

        """
        super().__init__(url)
        self.storage_file = storage_file
        # We use a threading.Lock to ensure thread-safety instead of relying on thread-local storage.
        self.lock = threading.Lock()
        # >SQLite default mode in earlier version is 1 not 2 (1=thread-safe 2=serialized)
        # `check_same_thread=False` to allow it to be used across different threads.
        self.connection = sqlite3.connect(self.storage_file, check_same_thread=False)
        # WAL (Write-Ahead Logging) allows for better concurrency.
        self.connection.execute("PRAGMA journal_mode=WAL")
        self.cursor = self.connection.cursor()
        self._setup_database()
        log.debug(
            f'Storage system loaded with arguments (storage_file="{storage_file}", url="{url}")'
        )

    def _setup_database(self) -> None:
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS storage (
                id INTEGER PRIMARY KEY,
                url TEXT,
                identifier TEXT,
                element_data TEXT,
                UNIQUE (url, identifier)
            )
        """)
        self.connection.commit()

    def save(self, element: html.HtmlElement, identifier: str):
        """Saves the elements unique properties to the storage for retrieval and relocation later

        :param element: The element itself that we want to save to storage.
        :param identifier: This is the identifier that will be used to retrieve the element later from the storage. See
            the docs for more info.
        """
        url = self._get_base_url()
        element_data = _StorageTools.element_to_dict(element)
        with self.lock:
            self.cursor.execute("""
                INSERT OR REPLACE INTO storage (url, identifier, element_data)
                VALUES (?, ?, ?)
            """, (url, identifier, orjson.dumps(element_data)))
            self.cursor.fetchall()
            self.connection.commit()

    def retrieve(self, identifier: str) -> Optional[Dict]:
        """Using the identifier, we search the storage and return the unique properties of the element

        :param identifier: This is the identifier that will be used to retrieve the element from the storage. See
            the docs for more info.
        :return: A dictionary of the unique properties
        """
        url = self._get_base_url()
        with self.lock:
            self.cursor.execute(
                "SELECT element_data FROM storage WHERE url = ? AND identifier = ?",
                (url, identifier)
            )
            result = self.cursor.fetchone()
            if result:
                return orjson.loads(result[0])
            return None

    def close(self):
        """Close all connections, will be useful when with some things like scrapy Spider.closed() function/signal"""
        with self.lock:
            self.connection.commit()
            self.cursor.close()
            self.connection.close()

    def __del__(self):
        """To ensure all connections are closed when the object is destroyed."""
        self.close()
