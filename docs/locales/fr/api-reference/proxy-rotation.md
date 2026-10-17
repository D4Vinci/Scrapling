---
title: "Référence de l’API de ProxyRotator"
description: "Consultez ProxyRotator et les stratégies de sélection et de rotation des proxies pour les sessions HTTP et de navigateur."
---

# Rotation des proxies {#proxy-rotation}

La classe `ProxyRotator` permet de changer de proxy en toute sécurité depuis plusieurs threads, dans tout fetcher ou toute session.

Vous pouvez l’importer directement :

```python
from scrapling.fetchers import ProxyRotator
```

## ::: scrapling.engines.toolbelt.proxy_rotation.ProxyRotator
    handler: python
    :docstring:
