---
title: "طلبات العناكب ودوال callback واستخدام Response.follow"
description: "أنشئ طلبات الزحف ومرّر البيانات الإضافية وتابع الروابط عبر response.follow. تعرّف على دوال callback والأولويات ومنع تكرار الطلبات."
---

# الطلبات والردود {#requests-responses}

!!! success "قبل البدء"

    1. اقرأ صفحة [البداية](getting-started.md) وتعرّف على إنشاء عنكبوت بسيط وتشغيله.

تشرح هذه الصفحة كائن `Request` بالتفصيل: إنشاء الطلبات، وتمرير البيانات بين دوال callback، والتحكم في الأولوية ومنع التكرار، واستخدام `response.follow()` لمتابعة الروابط.

## كائن Request {#the-request-object}

يمثل `Request` عنوان URL تريد جلبه. يمكنك إنشاء الطلب مباشرة أو عبر `response.follow()`:

```python
from scrapling.spiders import Request

# Direct construction
request = Request(
    "https://example.com/page",
    callback=self.parse_page,
    priority=5,
)

# Via response.follow (preferred in callbacks)
request = response.follow("/page", callback=self.parse_page)
```

هذه هي جميع المعاملات التي يمكنك تمريرها إلى `Request`:

| المعامل | النوع | القيمة الافتراضية | الوصف |
|---------|-------|-------------------|-------|
| `url` | `str` | *مطلوب* | عنوان URL المراد جلبه |
| `sid` | `str` | `""` | معرّف الجلسة، ويوجّه الطلب إلى جلسة محددة. انظر [الجلسات](sessions.md) |
| `callback` | `callable` | `None` | دالة async generator لمعالجة الرد. تكون `parse()` افتراضيًا |
| `priority` | `int` | `0` | تُعالج القيم الأعلى أولًا |
| `dont_filter` | `bool` | `False` | عند `True`، يتجاوز منع التكرار ويسمح بالطلبات المكررة |
| `meta` | `dict` | `{}` | بيانات إضافية تختارها وتنتقل إلى الرد |
| `**kwargs` | | | معاملات مسماة إضافية تُمرّر إلى دالة الجلب في الجلسة، مثل `headers` و`method` و`data` |

تُمرّر أي معاملات مسماة إضافية مباشرة إلى الجلسة المستخدمة. مثلًا، لإرسال طلب POST:

```python
yield Request(
    "https://example.com/api",
    method="POST",
    data={"key": "value"},
    callback=self.parse_result,
)
```

## Response.follow() {#responsefollow}

الطريقة الموصى بها لإنشاء طلبات المتابعة داخل دوال callback هي `response.follow()`. وهي توفر مزايا عديدة مقارنة بإنشاء كائنات `Request` مباشرة:

- **عناوين URL النسبية** تُكمّل تلقائيًا باستخدام عنوان الصفحة الحالية.
- **ترويسة Referer** تُضبط افتراضيًا على عنوان الصفحة الحالية.
- **معاملات الجلسة** تُورث من الطلب الأصلي، مثل الترويسات وإعدادات البروكسي. تُستثنى `method` و`params` و`data` و`json` و`files` و`multipart`، حتى تكون متابعة الروابط بطلبات GET عادية.
- **دالة callback ومعرّف الجلسة والأولوية** تُورث من الطلب الأصلي إذا لم تحدد قيمًا جديدة لها.

```python
async def parse(self, response: Response):
    # Minimal - inherits callback, sid, priority from current request
    yield response.follow("/next-page")

    # Override specific fields
    yield response.follow(
        "/product/123",
        callback=self.parse_product,
        priority=10,
    )

    # Pass additional metadata to
    yield response.follow(
        "/details",
        callback=self.parse_details,
        meta={"category": "electronics"},
    )
```

| المعامل | النوع | القيمة الافتراضية | الوصف |
|---------|-------|-------------------|-------|
| `url` | `str` | *مطلوب* | عنوان URL المراد متابعته، سواء كان كاملًا أو نسبيًا |
| `sid` | `str` | `""` | معرّف الجلسة. يُورث من الطلب الأصلي إذا كان فارغًا |
| `callback` | `callable` | `None` | دالة callback. تُورث من الطلب الأصلي إذا كانت `None` |
| `priority` | `int` | `None` | الأولوية. تُورث من الطلب الأصلي إذا كانت `None` |
| `dont_filter` | `bool` | `False` | تجاوز منع التكرار |
| `meta` | `dict` | `None` | بيانات إضافية تُدمج مع `meta` الموجودة في الرد |
| **`referer_flow`** | `bool` | `True` | استخدام عنوان الصفحة الحالية كترويسة Referer |
| `**kwargs` | | | تُدمج مع معاملات الجلسة في الطلب الأصلي |

### تعطيل تمرير Referer {#disabling-referer-flow}

تضبط `response.follow()` ترويسة `Referer` على عنوان الصفحة الحالية افتراضيًا. لتعطيل ذلك:

```python
yield response.follow("/page", referer_flow=False)
```

## دوال callback {#callbacks}

دوال callback هي دوال async generator في العنكبوت، وتُستخدم لمعالجة الردود. يجب أن تُخرج باستخدام `yield` أحد الأنواع الثلاثة التالية:

- **`dict`**: عنصر بيانات مستخرج يُضاف إلى النتائج.
- **`Request`**: طلب متابعة يُضاف إلى الطابور.
- **`None`**: تُتجاهل دون رسالة.

```python
class MySpider(Spider):
    name = "my_spider"
    start_urls = ["https://example.com"]

    async def parse(self, response: Response):
        # Yield items (dicts)
        yield {"url": response.url, "title": response.css("title::text").get("")}

        # Yield follow-up requests
        for link in response.css("a::attr(href)").getall():
            yield response.follow(link, callback=self.parse_page)

    async def parse_page(self, response: Response):
        yield {"content": response.css("article::text").get("")}
```

!!! tip "ملاحظة"

    يجب تعريف كل دوال callback باستخدام `async def`، واستخدام `yield` فيها بدلًا من `return`. حتى إذا كانت الدالة تُخرج بيانات فقط دون طلبات متابعة، فيجب أن تظل async generator.

## أولوية الطلبات {#request-priority}

تُعالج الطلبات ذات الأولوية الأعلى أولًا. يفيد ذلك عندما تكون بعض الصفحات أهم وتريد معالجتها قبل غيرها:

```python
async def parse(self, response: Response):
    # High priority - process product pages first
    for link in response.css("a.product::attr(href)").getall():
        yield response.follow(link, callback=self.parse_product, priority=10)

    # Low priority - pagination links processed after products
    next_page = response.css("a.next::attr(href)").get()
    if next_page:
        yield response.follow(next_page, callback=self.parse, priority=0)
```

عند استخدام `response.follow()`، تُورث الأولوية من الطلب الأصلي ما لم تحدد قيمة جديدة.

## منع التكرار {#deduplication}

يمنع العنكبوت تكرار الطلبات تلقائيًا باستخدام بصمة تُحسب من عنوان URL وطريقة HTTP ومحتوى الطلب ومعرّف الجلسة. إذا أعطى طلبان البصمة نفسها، يُتجاهل الثاني دون رسالة.

للسماح بطلبات مكررة، مثل إعادة زيارة صفحة بعد تسجيل الدخول، اضبط `dont_filter=True`:

```python
yield Request("https://example.com/dashboard", dont_filter=True, callback=self.parse_dashboard)

# Or with response.follow
yield response.follow("/dashboard", dont_filter=True, callback=self.parse_dashboard)
```

يمكنك تحديد ما يدخل في حساب البصمة باستخدام خصائص الكلاس التالية في العنكبوت:

| الخاصية | القيمة الافتراضية | التأثير |
|---------|-------------------|---------|
| `fp_include_kwargs` | `False` | إضافة معاملات الطلب الإضافية إلى البصمة، أي المعاملات التي مرّرتها إلى دالة الجلب في الجلسة، مثل الترويسات |
| `fp_keep_fragments` | `False` | إبقاء جزء URL الذي يبدأ بـ `#`، مثل `#section`، عند حساب البصمة |
| `fp_include_headers` | `False` | إضافة ترويسات الطلب إلى البصمة |

مثلًا، إذا أردت التعامل مع `https://example.com/page#section1` و`https://example.com/page#section2` كعنوانين مختلفين:

```python
class MySpider(Spider):
    name = "my_spider"
    fp_keep_fragments = True
    # ...
```

## بيانات الطلب الإضافية {#request-meta}

يتيح قاموس `meta` تمرير أي بيانات تختارها بين دوال callback. يفيد ذلك عندما تحتاج معلومات من صفحة لمعالجة صفحة أخرى:

```python
async def parse(self, response: Response):
    for product in response.css("div.product"):
        category = product.css("span.category::text").get("")
        link = product.css("a::attr(href)").get()
        if link:
            yield response.follow(
                link,
                callback=self.parse_product,
                meta={"category": category},
            )

async def parse_product(self, response: Response):
    yield {
        "name": response.css("h1::text").get(""),
        "price": response.css(".price::text").get(""),
        # Access meta from the request
        "category": response.meta.get("category", ""),
    }
```

عند استخدام `response.follow()`، تُدمج `meta` من الرد الحالي مع البيانات الجديدة التي تمرّرها. إذا تكرر مفتاح، تُستخدم القيمة الجديدة.

يحفظ نظام العناكب بعض البيانات الإضافية تلقائيًا أيضًا. مثلًا، عند تفعيل تبديل البروكسي، يمكنك معرفة البروكسي المستخدم للطلب من `response.meta["proxy"]`.
