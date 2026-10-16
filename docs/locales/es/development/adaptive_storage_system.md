---
title: "Crea un sistema de almacenamiento para el análisis adaptativo"
description: "Implementa save y retrieve para el análisis adaptativo de Scrapling. Crea un sistema con Redis para guardar y recuperar las propiedades de los elementos."
---

# Crea tu propio sistema de almacenamiento {#writing-your-retrieval-system}

Scrapling usa SQLite de forma predeterminada. En esta guía aprenderás a crear tu propio sistema para guardar las propiedades de los elementos que usa la función `adaptive`.

Por ejemplo, puedes usar Firebase para compartir una base de datos entre varios spiders en distintas máquinas. Una base de datos en línea permite que los spiders compartan los datos adaptativos.

Para que tu clase de almacenamiento funcione, debe cumplir tres requisitos:

1. Heredar de la clase abstracta `scrapling.core.storage.StorageSystemMixin` y aceptar un argumento de cadena `url`, para mantener la lógica de la biblioteca.
2. Usar el decorador `functools.lru_cache` sobre la clase para seguir el patrón Singleton, igual que las otras clases.
3. Implementar los métodos `save` y `retrieve` según sus anotaciones de tipo:
    - El método `save` no devuelve nada y recibe dos argumentos de la biblioteca:
        * El primero es el propio elemento, de tipo `lxml.html.HtmlElement`. Debes convertirlo en un diccionario con la función `element_to_dict` del submódulo `scrapling.core.utils._StorageTools` para conservar el mismo formato. Después puedes guardarlo en tu base de datos.
        * El segundo es una cadena con el identificador que se usa para recuperarlo. La combinación de este identificador y el argumento `url` recibido al crear la instancia debe ser única para cada fila. Si no lo es, se mezclarán los datos de `adaptive`.
    - El método `retrieve` recibe una cadena con el identificador. Usa ese identificador junto con la `url` recibida al crear la instancia para recuperar el diccionario del elemento. Devuelve el diccionario si existe, o `None` si no lo encuentra.

> Puedes ver un ejemplo con SQLite3 en el archivo [storage_adaptors](https://github.com/D4Vinci/Scrapling/blob/main/scrapling/core/storage.py).

Si tu clase cumple estos requisitos, el resto es sencillo. Si vas a usar la biblioteca en una aplicación con varios hilos, asegúrate de que tu clase los admita de forma segura. La clase predeterminada ya lo hace.

La clase abstracta también incluye funciones auxiliares que puedes usar. Puedes verlas en el [código](https://github.com/D4Vinci/Scrapling/blob/main/scrapling/core/storage.py), que tiene muchos comentarios :)

## Ejemplo práctico: almacenamiento con Redis {#real-world-example-redis-storage}

Este es un ejemplo práctico con Redis, generado por IA:

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
