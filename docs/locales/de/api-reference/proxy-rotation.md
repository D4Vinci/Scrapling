---
title: "API-Referenz für ProxyRotator"
description: "Sehen Sie sich ProxyRotator und Strategien zur Auswahl und Rotation von Proxys für HTTP- und Browsersitzungen an."
---

# Proxy-Rotation {#proxy-rotation}

Mit `ProxyRotator` können Sie Proxys in jedem Fetcher und jeder Sitzung wechseln, auch sicher aus mehreren Threads.

Sie können die Klasse direkt importieren:

```python
from scrapling.fetchers import ProxyRotator
```

## ::: scrapling.engines.toolbelt.proxy_rotation.ProxyRotator
    handler: python
    :docstring:
