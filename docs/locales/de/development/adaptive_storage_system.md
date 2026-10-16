---
title: "Ein eigenes Speichersystem für adaptives Parsing schreiben"
description: "Implementieren Sie save und retrieve für Scraplings adaptives Parsing. Erstellen Sie ein Redis-Speichersystem, um Elementeigenschaften zu speichern und abzurufen."
---

# Ein eigenes Speichersystem schreiben {#writing-your-retrieval-system}

Scrapling verwendet standardmäßig SQLite. Diese Anleitung zeigt, wie Sie ein eigenes Speichersystem für die Elementeigenschaften der Funktion `adaptive` schreiben.

Vielleicht möchten Sie zum Beispiel Firebase verwenden und eine Datenbank zwischen Spidern auf verschiedenen Rechnern teilen. Mit einer solchen Onlinedatenbank können die Spider ihre adaptiven Daten gemeinsam nutzen.

Ihre Speicherklasse muss zuerst drei Anforderungen erfüllen:

1. Sie erbt von der abstrakten Klasse `scrapling.core.storage.StorageSystemMixin` und nimmt das String-Argument `url` an, damit die Logik der Bibliothek erhalten bleibt.
2. Sie verwendet den Dekorator `functools.lru_cache` über der Klasse, um wie die anderen Klassen dem Singleton-Entwurfsmuster zu folgen.
3. Sie implementiert die Methoden `save` und `retrieve`, wie in den Typannotationen angegeben:
    - Die Methode `save` gibt nichts zurück und erhält zwei Argumente von der Bibliothek.
        * Das erste ist das Element selbst, vom Typ `lxml.html.HtmlElement`. Es muss mit der Funktion `element_to_dict` aus dem Untermodul `scrapling.core.utils._StorageTools` in ein Dictionary umgewandelt werden. So bleibt das Format gleich. Danach speichern Sie es in Ihrer Datenbank.
        * Das zweite ist ein String mit der Kennung zum späteren Abrufen. Die Kombination dieser Kennung mit dem bei der Initialisierung übergebenen Argument `url` muss für jede Zeile eindeutig sein. Sonst werden die Daten für `adaptive` falsch zugeordnet.
    - Die Methode `retrieve` erhält die Kennung als String. Zusammen mit der bei der Initialisierung übergebenen `url` ruft sie das Dictionary des Elements aus der Datenbank ab und gibt es zurück. Wenn kein Eintrag vorhanden ist, gibt sie `None` zurück.

> Falls die Schritte noch unklar sind, sehen Sie sich meine SQLite3-Implementierung in der Datei [storage_adaptors](https://github.com/D4Vinci/Scrapling/blob/main/scrapling/core/storage.py) an.

Wenn Ihre Klasse diese Anforderungen erfüllt, ist der Rest einfach. Soll die Bibliothek in einer Anwendung mit mehreren Threads laufen, muss Ihre Klasse das unterstützen. Die Standardklasse ist threadsicher.

Die abstrakte Klasse enthält auch einige Hilfsfunktionen, die Sie verwenden können. Sehen Sie sich am besten den ausführlich kommentierten [Code](https://github.com/D4Vinci/Scrapling/blob/main/scrapling/core/storage.py) an :)


## Praxisbeispiel: Redis als Speicher {#real-world-example-redis-storage}

Hier ist ein praktisches, von KI erstelltes Beispiel mit Redis:

```python
import redis
import orjson
from functools import lru_cache
from scrapling.core.storage import StorageSystemMixin
from scrapling.core.utils import _StorageTools

@lru_cache(None)
class RedisStorage(StorageSystemMixin):
    def __init__(self, host='localhost', port=6379, db=0, url=None):
        super().__init__(url)
        self.redis = redis.Redis(
            host=host,
            port=port,
            db=db,
            decode_responses=False
        )
        
    def save(self, element, identifier: str) -> None:
        # Convert element to dictionary
        element_dict = _StorageTools.element_to_dict(element)
        
        # Create key
        key = f"scrapling:{self._get_base_url()}:{identifier}"
        
        # Store as JSON
        self.redis.set(
            key,
            orjson.dumps(element_dict)
        )
        
    def retrieve(self, identifier: str) -> dict | None:
        # Get data
        key = f"scrapling:{self._get_base_url()}:{identifier}"
        data = self.redis.get(key)
        
        # Parse JSON if exists
        if data:
            return orjson.loads(data)
        return None
```
