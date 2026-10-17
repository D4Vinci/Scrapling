---
title: "Referência da API de ProxyRotator"
description: "Veja ProxyRotator e as estratégias de seleção e rotação de proxies para sessões HTTP e de navegador."
---

# Rotação de proxies {#proxy-rotation}

A classe `ProxyRotator` permite alternar proxies com segurança entre threads em qualquer fetcher ou sessão.

Você pode importá-la diretamente:

```python
from scrapling.fetchers import ProxyRotator
```

## ::: scrapling.engines.toolbelt.proxy_rotation.ProxyRotator
    handler: python
    :docstring:
