---
title: "اكتب نظام تخزين خاصًا للتحليل التكيفي"
description: "نفّذ save وretrieve لميزة التحليل التكيفي في Scrapling. اكتب نظام تخزين باستخدام Redis لحفظ خصائص العناصر واسترجاعها."
---

# كتابة نظام الاسترجاع الخاص بك {#writing-your-retrieval-system}

تستخدم Scrapling قاعدة SQLite افتراضيًا. يشرح هذا الدليل كيفية كتابة نظام التخزين الخاص بك لحفظ خصائص العناصر التي تستخدمها ميزة `adaptive`.

قد ترغب مثلًا في استخدام Firebase ومشاركة قاعدة البيانات بين عدة عناكب على أجهزة مختلفة. هذه فكرة مفيدة، لأن قاعدة البيانات المتاحة عبر الإنترنت تسمح للعناكب بمشاركة بيانات التحليل التكيفي.

لكي يعمل صنف التخزين الخاص بك، يجب أن يحقق هذه المتطلبات الثلاثة:

1. أن يرث من الصنف المجرد `scrapling.core.storage.StorageSystemMixin`، وأن يقبل معاملًا نصيًا باسم `url` للحفاظ على طريقة عمل المكتبة.
2. أن يستخدم decorator باسم `functools.lru_cache` فوق الصنف، ليتبع نمط Singleton مثل الأصناف الأخرى.
3. أن ينفّذ الدالتين `save` و`retrieve` وفقًا لتلميحات الأنواع:
    - لا تُرجع دالة `save` قيمة، وتستقبل معاملين من المكتبة:
        * الأول من نوع `lxml.html.HtmlElement`، وهو العنصر نفسه. يجب تحويله إلى قاموس باستخدام الدالة `element_to_dict` في `scrapling.core.utils._StorageTools` للحفاظ على التنسيق نفسه، ثم حفظه في قاعدة البيانات بالطريقة التي تريدها.
        * الثاني نص يمثل المعرّف المستخدم للاسترجاع. يجب أن يكون الجمع بين هذا المعرّف ومعامل `url` الممرّر عند الإنشاء فريدًا لكل سجل، وإلا ستختلط بيانات `adaptive`.
    - تستقبل دالة `retrieve` نصًا يمثل المعرّف. تستخدمه مع `url` الممرّر عند الإنشاء لاسترجاع قاموس العنصر من قاعدة البيانات. إذا كان موجودًا تُرجعه، وإلا تُرجع `None`.

> إذا احتجت إلى مثال أوضح، يمكنك مراجعة تنفيذي باستخدام SQLite3 في ملف [storage_adaptors](https://github.com/D4Vinci/Scrapling/blob/main/scrapling/core/storage.py).

إذا استوفى الصنف هذه الشروط، فبقية الخطوات بسيطة. وإذا كنت ستستخدم المكتبة في تطبيق متعدد threads، فتأكد أن الصنف يدعم ذلك بأمان. الصنف الافتراضي آمن للاستخدام مع threads متعددة.

أضفنا بعض الدوال المساعدة إلى الصنف المجرد لتستخدمها عند الحاجة. يمكنك الاطلاع عليها في [الكود](https://github.com/D4Vinci/Scrapling/blob/main/scrapling/core/storage.py)، حيث توجد تعليقات كثيرة تشرحها :)

## مثال عملي: التخزين باستخدام Redis {#real-world-example-redis-storage}

إليك مثالًا عمليًا أكثر باستخدام Redis، أنشأه الذكاء الاصطناعي:

```python
import redis
import orjson
from functools import lru_cache
from scrapling.core.storage import StorageSystemMixin
from scrapling.core.utils import _StorageTools

@lru_cache(None)
class RedisStorage(StorageSystemMixin):
    def __init__(self, host='localhost', port=6379, db=0, url=None):
        super().__init__(url)
        self.redis = redis.Redis(
            host=host,
            port=port,
            db=db,
            decode_responses=False
        )
        
    def save(self, element, identifier: str) -> None:
        # Convert element to dictionary
        element_dict = _StorageTools.element_to_dict(element)
        
        # Create key
        key = f"scrapling:{self._get_base_url()}:{identifier}"
        
        # Store as JSON
        self.redis.set(
            key,
            orjson.dumps(element_dict)
        )
        
    def retrieve(self, identifier: str) -> dict | None:
        # Get data
        key = f"scrapling:{self._get_base_url()}:{identifier}"
        data = self.redis.get(key)
        
        # Parse JSON if exists
        if data:
            return orjson.loads(data)
        return None
```
