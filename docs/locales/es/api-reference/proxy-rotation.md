---
title: "Referencia de la API de ProxyRotator"
description: "Consulta ProxyRotator y las estrategias de selección y rotación de proxies para sesiones HTTP y de navegador."
---

# Rotación de proxies {#proxy-rotation}

La clase `ProxyRotator` permite rotar proxies de forma segura entre hilos con cualquier fetcher o sesión.

Puedes importarla directamente:

```python
from scrapling.fetchers import ProxyRotator
```

## ::: scrapling.engines.toolbelt.proxy_rotation.ProxyRotator
    handler: python
    :docstring:
