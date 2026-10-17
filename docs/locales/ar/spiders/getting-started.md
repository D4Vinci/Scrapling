---
title: "أنشئ أول زاحف ويب باستخدام Python وScrapling"
description: "أنشئ عنكبوتًا يستخرج البيانات ويتابع الصفحات ويصدّر النتائج. تعرّف على عناوين البداية ودوال callback وحدود النطاقات وإعدادات robots.txt."
---

# البداية {#getting-started}

## مقدمة {#introduction}

!!! success "قبل البدء"

    1. اقرأ صفحة [أساسيات أدوات الجلب](../fetching/choosing.md) لفهم أنواع أدوات الجلب المختلفة ومتى تستخدم كل نوع.
    2. اقرأ صفحة [الكلاسات الأساسية](../parsing/main_classes.md) لفهم كلاس [Selector](../parsing/main_classes.md#selector) وكلاس [Response](../fetching/choosing.md#response-object).
    3. اقرأ صفحة [البنية](architecture.md) للحصول على فكرة عامة عن عمل نظام العناكب.

يتيح لك نظام العناكب إنشاء زواحف لصفحات متعددة، مع تنفيذ طلبات متزامنة، في بضعة أسطر من الكود. إذا سبق لك استخدام Scrapy، فستجد الأنماط مألوفة. وإذا لم تستخدمه من قبل، فسيشرح لك هذا الدليل كل ما تحتاجه للبدء.

## أول عنكبوت لك {#your-first-spider}

العنكبوت هو كلاس يحدد كيفية تصفح المواقع واستخراج بياناتها. هذا أبسط مثال:

```python
from scrapling.spiders import Spider, Response

class QuotesSpider(Spider):
    name = "quotes"
    start_urls = ["https://quotes.toscrape.com"]

    async def parse(self, response: Response):
        for quote in response.css("div.quote"):
            yield {
                "text": quote.css("span.text::text").get(""),
                "author": quote.css("small.author::text").get(""),
            }
```

يحتاج كل عنكبوت إلى ثلاثة أشياء:

1. **`name`**: اسم يميّز العنكبوت عن غيره.
2. **`start_urls`**: قائمة عناوين URL التي يبدأ منها الزحف.
3. **`parse()`**: دالة async generator تعالج كل رد وتُخرج النتائج باستخدام `yield`.

تجري عملية الاستخراج داخل `parse()`. تستخدم فيها طرق الاختيار نفسها التي تستخدمها مع [Selector](../parsing/main_classes.md#selector) أو [Response](../fetching/choosing.md#response-object) في Scrapling، وتُخرج قواميس البيانات المستخرجة باستخدام `yield`.

## تشغيل العنكبوت {#running-the-spider}

لتشغيل العنكبوت، أنشئ كائنًا منه واستدعِ `start()`:

```python
result = QuotesSpider().start()
```

تدير `start()` كل ما يتعلق بالتشغيل غير المتزامن داخليًا، فلا تحتاج إلى إعداد event loop بنفسك. أثناء التشغيل، تُسجّل الأحداث في الطرفية، وتحصل عند انتهاء الزحف على إحصاءات مفصّلة جدًا.

توجد هذه الإحصاءات في كائن `CrawlResult` الذي تعيده الدالة، وهو يحتوي على كل ما تحتاجه:

```python
result = QuotesSpider().start()

# Access scraped items
for item in result.items:
    print(item["text"], "-", item["author"])

# Check statistics
print(f"Scraped {result.stats.items_scraped} items")
print(f"Made {result.stats.requests_count} requests")
print(f"Took {result.stats.elapsed_seconds:.1f} seconds")

# Did the crawl finish or was it paused?
print(f"Completed: {result.completed}")
```

## متابعة الروابط {#following-links}

تحتاج معظم عمليات الزحف إلى متابعة الروابط عبر عدة صفحات. استخدم `response.follow()` لإنشاء طلبات المتابعة:

```python
from scrapling.spiders import Spider, Response

class QuotesSpider(Spider):
    name = "quotes"
    start_urls = ["https://quotes.toscrape.com"]

    async def parse(self, response: Response):
        # Extract items from the current page
        for quote in response.css("div.quote"):
            yield {
                "text": quote.css("span.text::text").get(""),
                "author": quote.css("small.author::text").get(""),
            }

        # Follow the "next page" link
        next_page = response.css("li.next a::attr(href)").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)
```

تتعامل `response.follow()` مع عناوين URL النسبية تلقائيًا، وتدمجها مع عنوان الصفحة الحالية. كما تضبط ترويسة `Referer` على عنوان الصفحة الحالية افتراضيًا.

يمكنك اختيار دوال callback مختلفة لطلبات المتابعة حسب نوع الصفحة:

```python
async def parse(self, response: Response):
    for link in response.css("a.product-link::attr(href)").getall():
        yield response.follow(link, callback=self.parse_product)

async def parse_product(self, response: Response):
    yield {
        "name": response.css("h1::text").get(""),
        "price": response.css(".price::text").get(""),
    }
```

!!! note "ملاحظة"

    يجب أن تكون كل دوال callback من نوع async generator، أي تستخدم `async def` و`yield`.

## تصدير البيانات {#exporting-data}

تحتوي `ItemList` الموجودة في `result.items` على دوال تصدير مدمجة:

```python
result = QuotesSpider().start()

# Export as JSON
result.items.to_json("quotes.json")

# Export as JSON with pretty-printing
result.items.to_json("quotes.json", indent=True)

# Export as JSON Lines (one JSON object per line)
result.items.to_jsonl("quotes.jsonl")

# Export as CSV or XML
result.items.to_csv("quotes.csv")
result.items.to_xml("quotes.xml")
```

تنشئ كل هذه الدوال المجلدات التي يحتويها المسار تلقائيًا إذا لم تكن موجودة.

تكتب `to_csv()` عمودًا لكل مفتاح موجود في أي عنصر. لذلك تُصدّر العناصر حتى لو كانت مفاتيحها مختلفة، وتترك الخلايا التي لا تتوفر لها قيمة فارغة. استخدم `fields=[...]` لاختيار الأعمدة وترتيبها بنفسك، أو `delimiter="\t"` لإنشاء ملف TSV. تضع `to_xml()` كل عنصر بيانات داخل عنصر `<item>` ضمن الجذر `<items>`، ويمكن تغيير الاسمين باستخدام `root_tag` و`item_tag`.

في الصيغتين، تُكتب القيم التي ليست مفردة وبسيطة، مثل القواميس المتداخلة والقوائم، بصيغة JSON حتى لا تُحذف أي بيانات دون تنبيه.

## تحديد النطاقات المسموح بها {#filtering-domains}

استخدم `allowed_domains` لحصر الزحف في نطاقات محددة. يمنع ذلك العنكبوت من متابعة روابط مواقع خارجية دون قصد:

```python
class MySpider(Spider):
    name = "my_spider"
    start_urls = ["https://example.com"]
    allowed_domains = {"example.com"}

    async def parse(self, response: Response):
        for link in response.css("a::attr(href)").getall():
            # Links to other domains are silently dropped
            yield response.follow(link, callback=self.parse)
```

تُقبل النطاقات الفرعية تلقائيًا. فمثلًا، يسمح `allowed_domains = {"example.com"}` أيضًا بالنطاقين `sub.example.com` و`blog.example.com` وغيرهما.

يُحسب كل طلب مستبعد في `stats.offsite_requests_count`، لتعرف عدد الطلبات التي استُبعدت.

## الالتزام بملف robots.txt {#robotstxt-compliance}

اضبط `robots_txt_obey = True` ليلتزم العنكبوت بقواعد robots.txt قبل الزحف إلى أي نطاق:

```python
class PoliteSpider(Spider):
    name = "polite"
    start_urls = ["https://example.com"]
    robots_txt_obey = True

    async def parse(self, response: Response):
        for link in response.css("a::attr(href)").getall():
            yield response.follow(link, callback=self.parse)
```

عند التفعيل، يقوم العنكبوت بما يلي:

1. **يجلب robots.txt مسبقًا** لكل نطاق في `start_urls` قبل بدء الزحف، مع جلب الملفات بالتزامن.
2. **يفحص كل طلب** وفقًا لقواعد `Disallow` في robots.txt الخاص بالنطاق. يتجاهل الطلبات غير المسموح بها دون رسالة، ويحسبها في `stats.robots_disallowed_count`.
3. **يلتزم بتوجيهات `Crawl-delay` و`Request-rate`** باختيار القيمة الأكبر بين فترة الانتظار المطلوبة و`download_delay` الذي حددته. لذلك لا تُنقص توجيهات robots.txt فترة الانتظار التي ضبطتها، بل تزيدها عند الحاجة فقط. عند تفعيل AutoThrottle، يضع الحد الأقصى له سقفًا لهذه القيمة أيضًا. اضبط `autothrottle_max_delay` على قيمة تكفي للالتزام بالانتظار المطلوب.

تُجلب ملفات robots.txt باستخدام الجلسة الافتراضية للعنكبوت، وتُحفظ لكل نطاق طوال عملية الزحف. إذا اكتشف العنكبوت نطاقًا أثناء الزحف لم يكن ضمن `start_urls`، يجلب robots.txt عند أول طلب لذلك النطاق.

**ملاحظة:** يكون `robots_txt_obey` غير مفعّل افتراضيًا لتجنب سلوك غير متوقع. تفعيله لا يغيّر إعدادات التزامن `concurrent_requests` و`concurrent_requests_per_domain`، بل يغيّر فترة الانتظار بين الطلبات فقط.

إذا لم ترد اختيار `download_delay` يدويًا، فاضبط `autothrottle_enabled = True`. سيعدّل العنكبوت فترة الانتظار لكل نطاق حسب سرعة ردوده، ويبطئ عند الحظر. انظر [AutoThrottle](advanced.md#autothrottle).

## الخطوة التالية {#whats-next}

بعد تعلّم الأساسيات، يمكنك قراءة:

- [الطلبات والردود](requests-responses.md): أولوية الطلبات ومنع التكرار والبيانات الإضافية وغيرها.
- [الجلسات](sessions.md): استخدام أدوات جلب مختلفة، مثل HTTP والمتصفح وStealth، داخل عنكبوت واحد.
- [إدارة البروكسي والتعامل مع الحظر](proxy-blocking.md): تبديل البروكسي بين الطلبات ومعالجة الحظر داخل العنكبوت.
- [الميزات المتقدمة](advanced.md): التحكم في التزامن وAutoThrottle والإيقاف المؤقت والاستكمال واستقبال البيانات أثناء الزحف ودوال مراحل التشغيل والسجلات.
