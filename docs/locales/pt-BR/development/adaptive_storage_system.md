---
title: "Crie um sistema de armazenamento para a análise adaptativa"
description: "Implemente save e retrieve para a análise adaptativa do Scrapling. Crie um sistema com Redis para salvar e recuperar as propriedades dos elementos."
---

# Crie seu próprio sistema de armazenamento {#writing-your-retrieval-system}

O Scrapling usa SQLite por padrão. Este guia mostra como criar seu próprio sistema para guardar as propriedades dos elementos usadas pelo recurso `adaptive`.

Por exemplo, você pode usar Firebase para compartilhar um banco de dados entre vários spiders em máquinas diferentes. Um banco de dados online permite que eles compartilhem os dados adaptativos.

Para funcionar, sua classe de armazenamento deve cumprir três requisitos:

1. Herdar da classe abstrata `scrapling.core.storage.StorageSystemMixin` e aceitar um argumento `url` do tipo string, para manter a lógica da biblioteca.
2. Usar o decorador `functools.lru_cache` sobre a classe para seguir o padrão Singleton, como as outras classes.
3. Implementar os métodos `save` e `retrieve` conforme as anotações de tipo:
    - O método `save` não retorna nada e recebe dois argumentos da biblioteca:
        * O primeiro é o próprio elemento, do tipo `lxml.html.HtmlElement`. Converta-o em um dicionário com a função `element_to_dict` do submódulo `scrapling.core.utils._StorageTools` para manter o mesmo formato. Depois, salve-o no seu banco de dados.
        * O segundo é uma string com o identificador usado para recuperar o elemento. A combinação desse identificador com o argumento `url` recebido na criação da instância deve ser única para cada linha. Caso contrário, os dados de `adaptive` serão misturados.
    - O método `retrieve` recebe uma string com o identificador. Use-o junto com a `url` recebida na criação da instância para buscar o dicionário do elemento. Retorne o dicionário se ele existir, ou `None` se não for encontrado.

> Você pode ver um exemplo com SQLite3 no arquivo [storage_adaptors](https://github.com/D4Vinci/Scrapling/blob/main/scrapling/core/storage.py).

Se sua classe cumpre esses requisitos, o restante é simples. Se você pretende usar a biblioteca em uma aplicação com várias threads, verifique se sua classe permite esse uso com segurança. A classe padrão já permite.

A classe abstrata também inclui funções auxiliares que você pode usar. Veja o [código](https://github.com/D4Vinci/Scrapling/blob/main/scrapling/core/storage.py), que tem vários comentários :)

## Exemplo prático: armazenamento com Redis {#real-world-example-redis-storage}

Este é um exemplo prático com Redis, gerado por IA:

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
