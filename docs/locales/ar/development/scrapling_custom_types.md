---
title: "استخدم أنواع النصوص والخصائص من Scrapling في الكود"
description: "استخدم TextHandler وTextHandlers وAttributesHandler خارج المحلل. تعرّف على أنواع Python التي ترث منها، ودوال JSON المساعدة، والخصائص للقراءة فقط."
---

# استخدام الأنواع الخاصة بـ Scrapling {#using-scraplings-custom-types}

> يمكنك استخدام الأنواع التي أُنشئت لـ Scrapling خارج المكتبة أيضًا. وهذا أفضل من نسخ كودها :)

### يمكن استيراد جميع الأنواع الحالية منفردة كما يلي {#all-current-types-can-be-imported-alone-like-below}

```python
from scrapling.core.custom_types import TextHandler, AttributesHandler

somestring = TextHandler('{}')
parsed = somestring.json()
somedict_1 = AttributesHandler({'a': 1})
somedict_2 = AttributesHandler(a=1)
```

يرث `TextHandler` من النوع `str` في Python، لذا تعمل معه جميع العمليات والدوال القياسية التي تعمل مع النصوص في Python.
قيمة `parsed` هي القاموس `{}`، وليست النص `'{}'`. للتحقق من كائن، استخدم `isinstance(somestring, TextHandler)`. وللتحقق من صنف، استخدم `issubclass(TextHandler, str)`.

يرث الصنف `AttributesHandler` من `collections.abc.Mapping`، لذلك لا يمكن تعديل بياناته، أي إنه للقراءة فقط، ويرث عملياته منه. يمكنك الوصول إلى البيانات التي مرّرتها لاحقًا عبر الخاصية `_data`، لكن انتبه: نوعها هو `types.MappingProxyType`، وهي أيضًا للقراءة فقط، وأسرع من `collections.abc.Mapping` بأجزاء من الثانية.

ببساطة، إذا كنت جديدًا في Python، فإن عمليات ودوال النوع القياسي `dict` تعمل مع `AttributesHandler`، باستثناء العمليات التي تحاول تعديل البيانات نفسها.

إذا أردت تعديل بيانات `AttributesHandler`، فحوّلها أولًا إلى قاموس باستخدام الدالة `dict` مثلًا، ثم عدّل القاموس خارج الكائن.
