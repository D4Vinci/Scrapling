---
title: "التحكم في الزحف: AutoThrottle ونقاط الاستكمال والذاكرة المؤقتة واستقبال البيانات"
description: "تحكّم في سرعة الزحف والتزامن. تعرّف على تخزين الردود مؤقتًا والإيقاف المؤقت والاستكمال واستقبال البيانات أثناء الزحف والحالة المحفوظة في نقاط الاستكمال."
---

# استخدامات متقدمة {#advanced-usages}

## مقدمة {#introduction}

!!! success "قبل البدء"

    1. اقرأ صفحة [البداية](getting-started.md) وتعرّف على إنشاء عنكبوت بسيط وتشغيله.

تشرح هذه الصفحة الميزات المتقدمة في نظام العناكب: التحكم في التزامن، والإيقاف المؤقت والاستكمال، واستقبال البيانات أثناء الزحف، ودوال مراحل التشغيل، والإحصاءات، والسجلات.

## التحكم في التزامن {#concurrency-control}

يستخدم نظام العناكب ثلاث خصائص للكلاس للتحكم في مقدار الضغط الذي تسببه الطلبات:

| الخاصية | القيمة الافتراضية | الوصف |
|---------|-------------------|-------|
| `concurrent_requests` | `4` | أقصى عدد طلبات تُعالج في الوقت نفسه |
| `concurrent_requests_per_domain` | `0` | أقصى عدد طلبات متزامنة لكل نطاق. القيمة 0 تعني عدم وضع حد لكل نطاق |
| `download_delay` | `0.0` | عدد ثواني الانتظار قبل كل طلب |
| `robots_txt_obey` | `False` | الالتزام بقواعد robots.txt، وهي Disallow وCrawl-delay وRequest-rate |

```python
class PoliteSpider(Spider):
    name = "polite"
    start_urls = ["https://example.com"]

    # Be gentle with the server
    concurrent_requests = 4
    concurrent_requests_per_domain = 2
    download_delay = 1.0  # Wait 1 second between requests

    async def parse(self, response: Response):
        yield {"title": response.css("title::text").get("")}
```

عند تحديد `concurrent_requests_per_domain`، يحصل كل نطاق على حد تزامن خاص به، بالإضافة إلى الحد العام. يفيد ذلك عند الزحف إلى عدة نطاقات في الوقت نفسه، إذ يمكنك السماح بتزامن عام مرتفع مع الحد من الضغط على كل نطاق.

!!! tip "نصيحة"

    يضيف `download_delay` انتظارًا ثابتًا قبل كل طلب، بغض النظر عن النطاق. استخدمه للتحكم البسيط في معدل الطلبات.

## AutoThrottle {#autothrottle}

اختيار `download_delay` ثابت يعتمد على التخمين. إذا كان منخفضًا جدًا فقد تُحظر، وإذا كان مرتفعًا جدًا فقد يستغرق الزحف وقتًا طويلًا. يراقب AutoThrottle سرعة رد الموقع الفعلية، ثم يضبط فترة الانتظار لكل نطاق بشكل مستقل. فيسرع مع الخوادم السريعة، ويبطئ مع الخوادم البطيئة أو التي تحظر الطلبات.

| الخاصية | القيمة الافتراضية | الوصف |
|---------|-------------------|-------|
| `autothrottle_enabled` | `False` | تفعيل فترة الانتظار التي تتغير تلقائيًا |
| `autothrottle_start_delay` | `5.0` | فترة الانتظار المستخدمة لأول طلب إلى النطاق |
| `autothrottle_max_delay` | `60.0` | أقصى فترة انتظار مسموح بها |
| `autothrottle_target_concurrency` | `None` | عدد الطلبات المتزامنة المستهدف لكل نطاق، كما سنوضح أدناه |
| `autothrottle_block_backoff` | `True` | مضاعفة فترة انتظار النطاق في كل مرة يحظرك فيها |

```python
class AdaptiveSpider(Spider):
    name = "adaptive"
    start_urls = ["https://example.com"]

    concurrent_requests = 8
    concurrent_requests_per_domain = 1

    autothrottle_enabled = True
    autothrottle_start_delay = 2.0
    autothrottle_max_delay = 30.0

    async def parse(self, response: Response):
        yield {"title": response.css("title::text").get("")}
```

بعد كل رد، تتجه فترة الانتظار نحو الوقت الذي استغرقه الخادم للرد. فالموقع الذي يرد خلال 0.5 ثانية يستقر عادةً قرب انتظار قدره 0.5 ثانية، أي نحو طلب واحد قيد التنفيذ في الوقت نفسه. يُحدد عدد الطلبات المستهدف لكل نطاق بهذا الترتيب: `autothrottle_target_concurrency` إذا حددته، وإلا `concurrent_requests_per_domain`، وإلا 1. لذلك غالبًا لا تحتاج إلى تحديد هدف منفصل، لأن الحد الذي ضبطته لكل نطاق يُستخدم كهدف، وتُقسم فترة الانتظار عليه. إذا زاد وقت الرد فجأة، تُطبّق الزيادة فورًا بدلًا من إدخالها تدريجيًا في المتوسط. وهكذا يبطئ العنكبوت بمجرد أن يبدأ الخادم في مواجهة صعوبة، ولا يزيد سرعته إلا تدريجيًا.

### الإبطاء عند الحظر {#backing-off-when-blocked}

وقت الرد وحده لا يكشف حدود معدل الطلبات. غالبًا يصل رد `429` أو `403` أو صفحة captcha *أسرع* من المحتوى الحقيقي، مما قد يوحي بأن الموقع يسمح بسرعة أعلى إذا اعتمدنا على الوقت فقط. لذلك فإن أي رد غير سليم، أي حالة خارج 2xx أو رد تعتبره `is_blocked()` محظورًا، **يضاعف** فترة انتظار النطاق:

```
0.5s -> 1s -> 2s -> 4s -> 8s ...   (up to autothrottle_max_delay)
```

يستمر العنكبوت في الإبطاء ما دام الموقع يرفض الطلبات. وعندما تعود الردود السليمة، يخفض حساب المتوسط فترة الانتظار تدريجيًا نحو سرعة الخادم الفعلية. وهكذا يعود للعمل بصورة طبيعية دون إعادة تشغيل.

إذا حدد الموقع مدة الانتظار في ترويسة `Retry-After` مع رد `429` أو `503`، تُستخدم هذه القيمة بدلًا من المضاعفة. يدعم النظام الصيغة الرقمية، مثل `Retry-After: 120`، وصيغة تاريخ HTTP.

اضبط `autothrottle_block_backoff = False` لتعطيل هذا السلوك والعودة إلى ضبط السرعة حسب وقت الرد فقط. في هذه الحالة، يستطيع الحظر منع العنكبوت من زيادة السرعة، لكنه لا يضاعف فترة الانتظار.

تتوفر فترة الانتظار النهائية لكل نطاق في الإحصاءات:

```python
result = AdaptiveSpider().start()
print(result.stats.autothrottle_delays)  # {'example.com': 0.62}
```

!!! note "ملاحظات"

    * تضع `download_delay` وفترات انتظار robots.txt حدًا أدنى، لكن `autothrottle_max_delay` يضع سقفًا لهذا الحد أيضًا. اجعل الحد الأقصى مساويًا على الأقل لفترة الانتظار التي ضبطتها أو التي يطلبها robots.txt.<br/>
    * تؤدي `concurrent_requests_per_domain` دورين: تحدد أقصى عدد طلبات قيد التنفيذ إلى النطاق، وتُستخدم كهدف لـ AutoThrottle. لذلك لا تحتاج غالبًا إلى ضبط هدف منفصل. يُنصح بتحديدها، لأن النطاق الذي ينتظر يحتفظ بموضع من الحد العام للتزامن. وإذا تركت عدد الطلبات لكل نطاق غير محدود، فقد تستنفد هذه الطلبات المنتظرة المواضع المشتركة مع النطاقات الأخرى.<br/>
    * يشمل وقت الرد المقاس عملية الجلب كاملة، بما فيها أي محاولات إعادة داخلية، ووقت عرض الصفحة في جلسات المتصفح.<br/>
    * يضع `autothrottle_max_delay` سقفًا لكل شيء، بما فيه `Retry-After`. إذا طلب الموقع انتظارًا أطول من هذا السقف، فارفع `autothrottle_max_delay` للالتزام به.<br/>
    * لا تُحفظ فترات الانتظار التي تعلّمها النظام في نقاط الاستكمال. بعد الإيقاف المؤقت والاستكمال، يبدأ كل نطاق مجددًا من `autothrottle_start_delay`.

## استخدام uvloop {#using-uvloop}

تقبل `start()` المعامل `use_uvloop` لاستخدام event loop الأسرع [uvloop](https://github.com/MagicStack/uvloop) أو [winloop](https://github.com/nicktimko/winloop)، إذا كان متاحًا:

```python
result = MySpider().start(use_uvloop=True)
```

قد يحسّن ذلك عدد الطلبات التي تُعالج في وقت معين عندما يعتمد الزحف كثيرًا على عمليات الإدخال والإخراج. تحتاج إلى تثبيت `uvloop` على Linux أو macOS، أو `winloop` على Windows، بشكل منفصل.

## الإيقاف المؤقت والاستكمال {#pause-resume}

يدعم العنكبوت الإيقاف المؤقت المنظم والاستكمال باستخدام نقاط محفوظة. لتفعيل ذلك، مرّر مجلد `crawldir` عند إنشاء العنكبوت:

```python
spider = MySpider(crawldir="crawl_data/my_spider")
result = spider.start()

if result.paused:
    print("Crawl was paused. Run again to resume.")
else:
    print("Crawl completed!")
```

### كيف يعمل {#how-it-works}

1. **الإيقاف المؤقت**: اضغط `Ctrl+C` أثناء الزحف. ينتظر العنكبوت اكتمال الطلبات الجارية، ثم يحفظ نقطة استكمال تضم الطلبات المعلّقة ومجموعة بصمات الطلبات التي سبق رصدها، ثم يخرج.
2. **الإيقاف الفوري**: اضغط `Ctrl+C` مرة ثانية للإيقاف فورًا دون انتظار المهام الجارية.
3. **الاستكمال**: شغّل العنكبوت مجددًا بقيمة `crawldir` نفسها. يكتشف النقطة المحفوظة، ويستعيد الطابور ومجموعة البصمات، ويكمل من حيث توقف، دون تشغيل `start_requests()`.
4. **التنظيف**: عند اكتمال الزحف بصورة طبيعية دون إيقاف مؤقت، تُحذف ملفات نقاط الاستكمال تلقائيًا.

**تُحفظ نقاط الاستكمال أيضًا بصورة دورية أثناء الزحف، كل 5 دقائق افتراضيًا.**

يمكنك تغيير الفاصل الزمني كما يلي:

```python
# Save checkpoint every 2 minutes
spider = MySpider(crawldir="crawl_data/my_spider", interval=120.0)
```

تستخدم كتابة نقطة الاستكمال ملفًا مؤقتًا، ولا تُستبدل نقطة الاستكمال السابقة إلا بعد نجاح الكتابة.

!!! warning "بيانات نقطة الاستكمال"

    عند تفعيل `crawldir`، يجب أن تكون القيم في الطلبات المعلّقة، بما فيها `meta` ومعاملات الطلب، قابلة للحفظ باستخدام وحدة `pickle` في Python. إذا تعذّر حفظ إحدى القيم، يفشل حفظ نقطة الاستكمال ويتوقف الزحف. يمكن استخدام كائن `Selector` داخل دالة callback، لكن لا يمكن حفظه بهذه الطريقة.

    احفظ القيم المستخرجة، مثل النصوص أو الأرقام، بدلًا من كائنات `Selector`. ويجب أن تحتوي القوائم والقواميس أيضًا على قيم قابلة للحفظ فقط:

    ```python
    yield response.follow("/details", meta={"title": str(response.css("h1::text").get(""))})
    ```

!!! tip "نصيحة"

    عند استخدام `start()`، يؤدي ضغط `Ctrl+C` أثناء الزحف إلى إغلاق منظم، حتى لو لم تفعّل نظام نقاط الاستكمال. الضغط مرة ثانية دون انتظار يُغلق العنكبوت فورًا.

### معرفة ما إذا كنت تستكمل زحفًا سابقًا {#knowing-if-youre-resuming}

تستقبل الدالة `on_start()` القيمة `resuming`:

```python
async def on_start(self, resuming: bool = False):
    if resuming:
        self.logger.info("Resuming from checkpoint!")
    else:
        self.logger.info("Starting fresh crawl")
```

## وضع التطوير {#development-mode}

عند تعديل منطق `parse()` وتجربته، تكون إعادة الطلبات إلى خوادم الموقع في كل تشغيل بطيئة وتسبب طلبات كثيرة. يحفظ وضع التطوير كل رد على القرص عند التشغيل الأول، ثم يعيد استخدامه من القرص في مرات التشغيل التالية. لذلك يمكنك تعديل المحددات وإعادة تشغيل العنكبوت كما تريد دون جلب الصفحات نفسها مجددًا.

فعّله بضبط `development_mode = True` في العنكبوت:

```python
class MySpider(Spider):
    name = "my_spider"
    start_urls = ["https://example.com"]
    development_mode = True

    async def parse(self, response: Response):
        yield {"title": response.css("title::text").get("")}
```

يجلب التشغيل الأول الصفحات بالطريقة المعتادة ويحفظ كل رد على القرص. تستخدم مرات التشغيل التالية الذاكرة المؤقتة للطلبات نفسها بدلًا من جلب الصفحات. عند استخدام `robots_txt_obey=True`، تُفحص قواعد robots.txt قبل البحث في الذاكرة المؤقتة.

### مكان الذاكرة المؤقتة {#cache-location}

تُحفظ الردود افتراضيًا في `.scrapling_cache/{spider.name}/` نسبةً إلى مجلد العمل الحالي، أي المجلد الذي شغّلت العنكبوت منه، **وليس** المجلد الذي يحتوي على ملف العنكبوت. يمكنك تغيير المكان باستخدام `development_cache_dir`:

```python
class MySpider(Spider):
    name = "my_spider"
    start_urls = ["https://example.com"]
    development_mode = True
    development_cache_dir = "/tmp/my_spider_cache"
```

### كيف يعمل {#how-it-works_1}

1. **مفتاح التخزين**: تُحفظ كل استجابة تحت بصمة الطلب. لذلك فإن تغيير أي خاصية تؤثر في البصمة، مثل `fp_include_kwargs` أو `fp_include_headers` أو `fp_keep_fragments`، يؤدي إلى جلب جديد.
2. **صيغة التخزين**: ملف JSON لكل رد، باسم `{fingerprint_hex}.json`. يُرمّز المحتوى باستخدام base64 للحفاظ على البيانات الثنائية كما هي تمامًا. تتم الكتابة بإنشاء ملف مؤقت ثم إعادة تسميته.
3. **إعادة الاستخدام**: عند العثور على رد محفوظ، يتجاوز المحرك جلب الصفحة، بما فيه `download_delay` وحدود معدل الطلبات ومسار إعادة المحاولة عبر `is_blocked()`. يصل الرد المحفوظ مباشرة إلى دالة callback.
4. **الإحصاءات**: تظل الطلبات المحفوظة تُحسب ضمن `requests_count` و`response_bytes` وعدادات حالات الرد، فتبدو الإحصاءات مثل الزحف العادي. يوضح العدادان الإضافيان `cache_hits` و`cache_misses` عدد مرات العثور على رد محفوظ وعدد مرات عدم العثور عليه.

### مسح الذاكرة المؤقتة {#clearing-the-cache}

لا تنتهي صلاحية الردود تلقائيًا. لفرض جلب جديد، احذف مجلد الذاكرة المؤقتة أو استدعِ `clear()` مباشرة من مديرها.

!!! warning "تنبيه"

    وضع التطوير مخصّص للتطوير، وليس للتشغيل الفعلي. لا تنتهي صلاحية الردود المحفوظة، وإعادة استخدامها تتجاوز حدود معدل الطلبات وإعادة الطلبات المحظورة. لا تنشر عنكبوتًا مع `development_mode = True`.

## استقبال البيانات أثناء الزحف {#streaming}

للعناكب التي تعمل طويلًا، أو للتطبيقات التي تحتاج إلى البيانات المستخرجة فورًا، استخدم `stream()` بدلًا من `start()`:

```python
import anyio

async def main():
    spider = MySpider()
    async for item in spider.stream():
        print(f"Got item: {item}")
        # Access real-time stats
        print(f"Items so far: {spider.stats.items_scraped}")
        print(f"Requests made: {spider.stats.requests_count}")

anyio.run(main)
```

الفروق الأساسية عن `start()`:

- يجب استدعاء `stream()` من سياق غير متزامن.
- تُخرج البيانات واحدة تلو الأخرى عند استخراجها، بدلًا من جمعها في قائمة.
- يمكنك قراءة `spider.stats` أثناء المرور على البيانات للحصول على إحصاءات مباشرة.

!!! abstract "تفاصيل"

    تجد شرح القائمة الكاملة للإحصاءات المتاحة عبر `spider.stats` [أدناه](#results-statistics).

يمكنك استخدامها مع نقاط الاستكمال أيضًا، مما يسهل إنشاء واجهات تعرض بيانات مباشرة وتدعم الإيقاف المؤقت والاستكمال.

```python
import anyio

async def main():
    spider = MySpider(crawldir="crawl_data/my_spider")
    async for item in spider.stream():
        print(f"Got item: {item}")
        # Access real-time stats
        print(f"Items so far: {spider.stats.items_scraped}")
        print(f"Requests made: {spider.stats.requests_count}")

anyio.run(main)
```

يمكنك أيضًا استخدام `spider.pause()` لإيقاف العنكبوت في الكود السابق. إذا استخدمتها دون تفعيل نظام نقاط الاستكمال، فستغلق عملية الزحف فقط.

## دوال مراحل التشغيل {#lifecycle-hooks}

يوفر العنكبوت عدة دوال يمكنك إعادة تعريفها لإضافة سلوك مخصّص في مراحل الزحف المختلفة:

### on_start {#on_start}

تُستدعى قبل بدء الزحف. استخدمها للإعداد، مثل تحميل البيانات أو تهيئة الموارد:

```python
async def on_start(self, resuming: bool = False):
    self.logger.info("Spider starting up")
    # Load seed URLs from a database, initialize counters, etc.
```

### on_close {#on_close}

تُستدعى بعد انتهاء الزحف، سواء اكتمل أم توقف مؤقتًا. استخدمها للتنظيف والإغلاق:

```python
async def on_close(self):
    self.logger.info("Spider shutting down")
    # Close database connections, flush buffers, etc.
```

### on_error {#on_error}

تُستدعى عند فشل طلب بسبب استثناء. استخدمها لتتبع الأخطاء أو لإضافة طريقة استرداد مخصّصة:

```python
async def on_error(self, request: Request, error: Exception):
    self.logger.error(f"Failed: {request.url} - {error}")
    # Log to error tracker, save failed URL for later, etc.
```

### on_scraped_item {#on_scraped_item}

تُستدعى لكل عنصر بيانات قبل إضافته إلى النتائج. أعد العنصر، مع تعديله أو دونه، للاحتفاظ به، أو أعد `None` لاستبعاده:

```python
async def on_scraped_item(self, item: dict) -> dict | None:
    # Drop items without a title
    if not item.get("title"):
        return None

    # Modify items (e.g., add timestamps)
    item["scraped_at"] = "2026-01-01"
    return item
```

!!! tip "نصيحة"

    يمكنك أيضًا استخدام هذه الدالة لتمرير البيانات إلى مراحل المعالجة الخاصة بك، ثم استبعادها من نتائج العنكبوت.

### start_requests {#start_requests}

أعد تعريف `start_requests()` لإنشاء الطلبات الأولى بطريقة مخصّصة بدلًا من استخدام `start_urls`:

```python
async def start_requests(self):
    # POST request to log in first
    yield Request(
        "https://example.com/login",
        method="POST",
        data={"user": "admin", "pass": "secret"},
        callback=self.after_login,
    )

async def after_login(self, response: Response):
    # Now crawl the authenticated pages
    yield response.follow("/dashboard", callback=self.parse)
```

## النتائج والإحصاءات {#results-statistics}

يحتوي `CrawlResult` الذي تعيده `start()` على البيانات المستخرجة والإحصاءات المفصّلة:

```python
result = MySpider().start()

# Items
print(f"Total items: {len(result.items)}")
result.items.to_json("output.json", indent=True)

# Did the crawl complete?
print(f"Completed: {result.completed}")
print(f"Paused: {result.paused}")

# Statistics
stats = result.stats
print(f"Requests: {stats.requests_count}")
print(f"Failed: {stats.failed_requests_count}")
print(f"Blocked: {stats.blocked_requests_count}")
print(f"Offsite filtered: {stats.offsite_requests_count}")
print(f"Robots.txt disallowed: {stats.robots_disallowed_count}")
print(f"Cache hits: {stats.cache_hits}")
print(f"Cache misses: {stats.cache_misses}")
print(f"Items scraped: {stats.items_scraped}")
print(f"Items dropped: {stats.items_dropped}")
print(f"Response bytes: {stats.response_bytes}")
print(f"Duration: {stats.elapsed_seconds:.1f}s")
print(f"Speed: {stats.requests_per_second:.1f} req/s")
```

### الإحصاءات المفصّلة {#detailed-stats}

يتتبع كائن `CrawlStats` المعلومات التفصيلية التالية:

```python
stats = result.stats

# Status code distribution
print(stats.response_status_count)
# {'status_200': 150, 'status_404': 3, 'status_403': 1}

# Bytes downloaded per domain
print(stats.domains_response_bytes)
# {'example.com': 1234567, 'api.example.com': 45678}

# Requests per session
print(stats.sessions_requests_count)
# {'http': 120, 'stealth': 34}

# Proxies used during the crawl
print(stats.proxies)
# ['http://proxy1:8080', 'http://proxy2:8080']

# Log level counts
print(stats.log_levels_counter)
# {'debug': 200, 'info': 50, 'warning': 3, 'error': 1, 'critical': 0}

# Timing information
print(stats.start_time)       # Unix timestamp when crawl started
print(stats.end_time)         # Unix timestamp when crawl finished
print(stats.download_delay)   # The download delay used (seconds)

# Concurrency settings used
print(stats.concurrent_requests)             # Global concurrency limit
print(stats.concurrent_requests_per_domain)  # Per-domain concurrency limit

# AutoThrottle
print(stats.autothrottle_enabled)  # Whether the adaptive delay was on
print(stats.autothrottle_delays)   # Final delay per domain, {'example.com': 0.62}

# Custom stats (set by your spider code)
print(stats.custom_stats)
# {'login_attempts': 3, 'pages_with_errors': 5}

# Export everything as a dict
print(stats.to_dict())
```

## السجلات {#logging}

يحتوي العنكبوت على logger مدمج يمكنك الوصول إليه عبر `self.logger`. يُعدّ مسبقًا باسم العنكبوت، ويدعم الخيارات التالية:

| الخاصية | القيمة الافتراضية | الوصف |
|---------|-------------------|-------|
| `logging_level` | `logging.DEBUG` | أقل مستوى رسائل يُسجّل |
| `logging_format` | `"[%(asctime)s]:({spider_name}) %(levelname)s: %(message)s"` | تنسيق رسالة السجل |
| `logging_date_format` | `"%Y-%m-%d %H:%M:%S"` | تنسيق التاريخ في الرسائل |
| `log_file` | `None` | مسار ملف السجل، بالإضافة إلى الرسائل في الطرفية |

```python
import logging

class MySpider(Spider):
    name = "my_spider"
    start_urls = ["https://example.com"]
    logging_level = logging.INFO
    log_file = "logs/my_spider.log"

    async def parse(self, response: Response):
        self.logger.info(f"Processing {response.url}")
        yield {"title": response.css("title::text").get("")}
```

يُنشأ مجلد ملف السجل تلقائيًا إذا لم يكن موجودًا. تستخدم الرسائل في الطرفية والملف التنسيق نفسه.
