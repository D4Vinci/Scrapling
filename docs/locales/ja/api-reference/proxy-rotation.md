---
title: "ProxyRotator の API リファレンス"
description: "HTTP とブラウザのセッションで使える ProxyRotator と、プロキシの選択・切り替え方法を確認します。"
---

# プロキシの切り替え {#proxy-rotation}

`ProxyRotator` は、すべての Fetcher とセッションでプロキシを切り替えます。複数のスレッドからも安全に使えます。

次のように直接インポートできます。

```python
from scrapling.fetchers import ProxyRotator
```

## ::: scrapling.engines.toolbelt.proxy_rotation.ProxyRotator
    handler: python
    :docstring:
