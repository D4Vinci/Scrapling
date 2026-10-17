---
title: "مرجع API لفئات Spiders والطلبات ونتائج الجمع"
description: "تعرّف على hooks لمراحل عمل Spider وخيارات الطلبات وإدارة الجلسات وإحصاءات الجمع وطرق تصدير العناصر."
---

# فئات Spider {#spider-classes}

هذا مرجع لكل معاملات فئات إطار Spiders وخصائصها وطرقها.

يمكنك استيرادها كما يلي:

```python
from scrapling.spiders import Spider, Request, CrawlResult, SessionManager, Response
```

## ::: scrapling.spiders.Spider
    handler: python
    :docstring:

## ::: scrapling.spiders.Request
    handler: python
    :docstring:

## فئات النتائج {#result-classes}

## ::: scrapling.spiders.result.CrawlResult
    handler: python
    :docstring:

## ::: scrapling.spiders.result.CrawlStats
    handler: python
    :docstring:

## ::: scrapling.spiders.result.ItemList
    handler: python
    :docstring:

## إدارة الجلسات {#session-management}

## ::: scrapling.spiders.session.SessionManager
    handler: python
    :docstring:
