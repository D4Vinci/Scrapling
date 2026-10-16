---
title: "Utilisez les types de texte et d’attributs de Scrapling dans votre code"
description: "Utilisez TextHandler, TextHandlers et AttributesHandler hors de l’analyseur. Découvrez leurs types de base Python, les fonctions JSON et les attributs en lecture seule."
---

# Utiliser les types propres à Scrapling {#using-scraplings-custom-types}

> Vous pouvez utiliser les types créés pour Scrapling en dehors de la bibliothèque. C’est plus simple que de copier leur code :)

### Vous pouvez importer chaque type séparément {#all-current-types-can-be-imported-alone-like-below}

```python
from scrapling.core.custom_types import TextHandler, AttributesHandler

somestring = TextHandler('{}')
parsed = somestring.json()
somedict_1 = AttributesHandler({'a': 1})
somedict_2 = AttributesHandler(a=1)
```

`TextHandler` est une sous-classe de `str` de Python. Toutes les opérations et méthodes habituelles des chaînes fonctionnent donc avec elle.
`parsed` est le dictionnaire `{}`, pas la chaîne `'{}'`. Pour vérifier une instance, utilisez `isinstance(somestring, TextHandler)`. Pour vérifier une classe, utilisez `issubclass(TextHandler, str)`.

`AttributesHandler` est une sous-classe de `collections.abc.Mapping`. Elle est immuable, donc en lecture seule, et hérite de ses opérations. Vous pouvez accéder aux données par la propriété `_data`, mais elle est aussi en lecture seule : son type est `types.MappingProxyType`, un peu plus rapide que `collections.abc.Mapping`.

Si vous débutez en Python, voyez `AttributesHandler` comme un `dict` que vous pouvez consulter, mais dont vous ne pouvez pas modifier les données. Les opérations et méthodes habituelles des dictionnaires fonctionnent, sauf celles qui changent les données.

Pour modifier les données de `AttributesHandler`, convertissez-les d’abord en dictionnaire, par exemple avec `dict`, puis modifiez cette copie.
