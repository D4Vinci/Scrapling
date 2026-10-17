---
title: "مرجع API لجلب الصفحات عبر HTTP والمتصفح"
description: "تعرّف على API للفئات Fetcher وAsyncFetcher وStealthyFetcher والجلسات، مع خيارات الطلبات وإعدادات المتصفح وأنواع القيم المعادة."
---

# فئات Fetchers {#fetchers-classes}

هذا مرجع لكل معاملات فئات Fetchers وخصائصها وطرقها.

يمكنك استيرادها كلها كما يلي:

```python
from scrapling.fetchers import (
    Fetcher, AsyncFetcher, StealthyFetcher,
    FetcherSession, AsyncStealthySession, StealthySession
)
```

## ::: scrapling.fetchers.Fetcher
    handler: python
    :docstring:

## ::: scrapling.fetchers.AsyncFetcher
    handler: python
    :docstring:

## ::: scrapling.fetchers.StealthyFetcher
    handler: python
    :docstring:


## فئات الجلسات {#session-classes}

### جلسات HTTP {#http-sessions}

## ::: scrapling.fetchers.FetcherSession
    handler: python
    :docstring:

### جلسات التخفي {#stealth-sessions}

## ::: scrapling.fetchers.StealthySession
    handler: python
    :docstring:

## ::: scrapling.fetchers.AsyncStealthySession
    handler: python
    :docstring:
