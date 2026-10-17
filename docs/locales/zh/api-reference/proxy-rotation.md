---
title: "ProxyRotator API 参考"
description: "查看 ProxyRotator 的代理选择和轮换策略，用于 HTTP 和浏览器会话。"
---

# 代理轮换 {#proxy-rotation}

`ProxyRotator` 可以在任何 Fetcher 和会话中切换代理，也能安全地供多个线程使用。

可以直接导入这个类：

```python
from scrapling.fetchers import ProxyRotator
```

## ::: scrapling.engines.toolbelt.proxy_rotation.ProxyRotator
    handler: python
    :docstring:
