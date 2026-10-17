---
title: "Créez un système de stockage pour l’analyse adaptative"
description: "Implémentez save et retrieve pour l’analyse adaptative de Scrapling. Créez un système Redis pour enregistrer et retrouver les propriétés des éléments."
---

# Créer votre propre système de stockage {#writing-your-retrieval-system}

Scrapling utilise SQLite par défaut. Ce guide montre comment créer votre propre système pour enregistrer les propriétés des éléments utilisées par la fonction `adaptive`.

Vous pouvez par exemple utiliser Firebase pour partager une base de données entre plusieurs spiders sur différentes machines. Une base de données en ligne leur permet de partager les données adaptatives.

Pour fonctionner, votre classe de stockage doit respecter trois conditions :

1. Hériter de la classe abstraite `scrapling.core.storage.StorageSystemMixin` et accepter un argument de type chaîne, `url`, pour conserver la logique de la bibliothèque.
2. Utiliser le décorateur `functools.lru_cache` sur la classe pour suivre le modèle Singleton, comme les autres classes.
3. Implémenter les méthodes `save` et `retrieve` selon leurs annotations de type :
    - La méthode `save` ne renvoie rien et reçoit deux arguments de la bibliothèque :
        * Le premier est l’élément lui-même, de type `lxml.html.HtmlElement`. Convertissez-le en dictionnaire avec la fonction `element_to_dict` du sous-module `scrapling.core.utils._StorageTools` pour garder le même format, puis enregistrez-le dans votre base de données.
        * Le second est une chaîne contenant l’identifiant utilisé pour retrouver l’élément. La combinaison de cet identifiant et de l’argument `url` reçu à la création de l’instance doit être unique pour chaque ligne. Sinon, les données de `adaptive` seront mélangées.
    - La méthode `retrieve` reçoit une chaîne contenant l’identifiant. Utilisez-le avec l’`url` reçue à la création de l’instance pour retrouver le dictionnaire de l’élément. Renvoyez ce dictionnaire s’il existe, ou `None` sinon.

> Vous pouvez consulter un exemple avec SQLite3 dans le fichier [storage_adaptors](https://github.com/D4Vinci/Scrapling/blob/main/scrapling/core/storage.py).

Si votre classe respecte ces conditions, la suite est simple. Si vous prévoyez d’utiliser la bibliothèque dans une application avec plusieurs threads, assurez-vous que votre classe le permet sans conflit. La classe par défaut le permet déjà.

La classe abstraite contient aussi des fonctions utilitaires que vous pouvez utiliser. Consultez le [code](https://github.com/D4Vinci/Scrapling/blob/main/scrapling/core/storage.py), qui contient de nombreux commentaires :)

## Exemple pratique : stockage avec Redis {#real-world-example-redis-storage}

Voici un exemple pratique avec Redis, généré par IA :

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
