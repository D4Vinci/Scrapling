---
title: "Référence de l’API de Response"
description: "Consultez le statut, les en-têtes, le contenu, les métadonnées, la conversion Markdown et follow. Extrayez des données avec les méthodes héritées de Selector."
---

# Classe Response {#response-class}

La classe `Response` contient les réponses HTTP de tous les fetchers. Elle donne accès au statut, aux en-têtes, au contenu et aux cookies, et permet d’utiliser un `Selector` pour analyser la réponse.

Vous pouvez importer la classe `Response` ainsi :

```python
from scrapling.engines.toolbelt.custom import Response
```

## ::: scrapling.engines.toolbelt.custom.Response
    handler: python
    :docstring:
