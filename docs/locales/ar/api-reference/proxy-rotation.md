---
title: "مرجع API للفئة ProxyRotator"
description: "تعرّف على ProxyRotator وطرق اختيار Proxy وتبديله. اضبط عناوين Proxy لجلسات HTTP والمتصفح."
---

# تبديل Proxy {#proxy-rotation}

تتيح الفئة `ProxyRotator` تبديل عناوين Proxy لأي Fetcher أو جلسة، مع دعم آمن لاستخدامها من عدة threads.

يمكنك استيرادها كما يلي:

```python
from scrapling.fetchers import ProxyRotator
```

## ::: scrapling.engines.toolbelt.proxy_rotation.ProxyRotator
    handler: python
    :docstring:
