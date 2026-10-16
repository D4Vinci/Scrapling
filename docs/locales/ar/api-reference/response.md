---
title: "مرجع API للفئة Response في Scrapling"
description: "تعرّف على حالة الاستجابة وترويساتها ومحتواها وبياناتها الوصفية والتحويل إلى Markdown وطريقة follow. استخدم طرق Selector الموروثة لاستخراج البيانات."
---

# الفئة Response {#response-class}

تجمع الفئة `Response` استجابات HTTP من كل Fetchers في شكل واحد. تتيح قراءة الحالة والترويسات والمحتوى وملفات تعريف الارتباط، مع `Selector` لتحليل المحتوى.

يمكنك استيراد الفئة `Response` كما يلي:

```python
from scrapling.engines.toolbelt.custom import Response
```

## ::: scrapling.engines.toolbelt.custom.Response
    handler: python
    :docstring:
