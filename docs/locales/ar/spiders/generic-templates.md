---
title: "قوالب العناكب للروابط وخرائط الموقع وملفات البيانات وMarkdown"
description: "اختر بين CrawlSpider وSitemapSpider وXMLFeedSpider وCSVFeedSpider وContentSpider. حدد قواعد جمع الصفحات أو صفوف البيانات أو مجموعة نصوص Markdown."
---

# قوالب العناكب العامة {#generic-spider-templates}

تتبع معظم عمليات الزحف أحد نمطين: متابعة الروابط التي تطابق نمطًا محددًا، أو زيارة كل عنوان URL في خريطة الموقع. توفر Scrapling قوالب للحالتين، حتى لا تحتاج إلى كتابة كود `parse()` المتكرر في كل مرة.

يعتمد `CrawlSpider` و`SitemapSpider` على `LinkExtractor`، الذي يستخرج عناوين URL من `Response`، أو يختبر عنوانًا واحدًا باستخدام `matches()`. كما يحلل `SitemapSpider` محتوى sitemap.xml وsitemap_index.xml داخليًا، سواء كان مضغوطًا باستخدام gzip أم لا.

يمكنك استخدام `LinkExtractor` مباشرة داخل `Spider.parse()` العادية. توفر لك القوالب فقط كود ربط الأجزاء ببعضها.

## CrawlSpider {#crawlspider}

يتابع `CrawlSpider` الروابط تلقائيًا وفقًا للقواعد التي تحددها.

```python
from scrapling.spiders import CrawlSpider, CrawlRule, LinkExtractor

class QuotesSpider(CrawlSpider):
    name = "blog"
    start_urls = ["https://quotes.toscrape.com/"]

    def rules(self):
        return [
            CrawlRule(LinkExtractor(allow=r"/author/"), callback=self.parse_author),
            CrawlRule(LinkExtractor(allow=r"/page/\d+/")),  # follow pagination, no callback
        ]

    async def parse_author(self, response):
        yield {
            '.author-title': response.css('.author-title::text').get(),
            "birthday": response.css('.author-born-date::text').get(),
            "url": response.url,
        }

result = QuotesSpider().start()
```

تجمع `CrawlRule` بين `LinkExtractor` ودالة `callback` اختيارية، وهي دالة مرتبطة بكائن العنكبوت. ويمكنها أيضًا تحديد `priority` للطلب `Request` الناتج، ودالة `process_request` اختيارية تعدّل كل `Request` قبل إخراجه. تطبّق `parse()` الافتراضية جميع القواعد على كل رد، وتُخرج `Request` لكل عنوان URL مطابق.

إذا لم تحدد callback لقاعدة، تُرسل عناوين URL المطابقة إلى `parse()` الافتراضية للعنكبوت. يفيد ذلك في متابعة الصفحات: تستخرج روابط الصفحات التالية ليستمر الزحف دون الحاجة إلى دالة معالجة منفصلة.

### ترتيب الزحف {#crawl-order}

اضبط `crawl_strategy` في `CrawlSpider` أو في الكلاسات التي ترث منه، بما فيها `ContentSpider`، لاختيار الطلب المعلّق التالي:

| `crawl_strategy` | الترتيب بين الطلبات التي لها `Request.priority` نفسها |
|------------------|------------------------------------------------------|
| `"bfs"`، الافتراضي | أقدم طلب في الطابور أولًا |
| `"dfs"` | أحدث طلب في الطابور أولًا |

يختار Scheduler أولًا الطلبات المعلّقة ذات `Request.priority` الأعلى. تؤثر الاستراتيجية فقط في ترتيب الطلبات المتساوية في الأولوية.

اضبط `concurrent_requests = 1` لمعالجة طلب واحد في كل مرة حسب ترتيب الطابور الذي اخترته. يظل منع تكرار عناوين URL مفعّلًا، والعثور على عنوان مجددًا لا يغيّر موضع طلبه في الطابور. عند تشغيل طلبات بالتوازي، قد تكتمل الصفحات بترتيب مختلف، وقد تتداخل مستويات الزحف أو فروعه.

احتفظ بقيمة `crawl_strategy` نفسها عند الاستكمال من نقطة محفوظة.

### دمج القواعد مع منطق مخصّص {#combining-rules-with-custom-logic}

أعد تعريف `parse()` واستدعِ `super().parse(response)` لتطبيق القواعد وإخراج بياناتك الإضافية:

```python
class MySpider(CrawlSpider):
    def rules(self):
        return [CrawlRule(LinkExtractor(allow=r"/posts/"), callback=self.parse_post)]

    async def parse(self, response):
        yield {"page_url": response.url}
        async for req in super().parse(response):
            yield req
```

### تعديل الطلبات باستخدام `process_request` {#mutating-requests-with-process_request}

```python
def add_priority(self, request, response):
    request.priority = 10
    return request

def rules(self):
    return [CrawlRule(
        LinkExtractor(allow=r"/posts/"),
        callback=self.parse_post,
        process_request=self.add_priority,
    )]
```

## SitemapSpider {#sitemapspider}

يبدأ `SitemapSpider` الزحف من عناوين sitemap.xml. يستخدم واجهة `rules()` نفسها التي يستخدمها `CrawlSpider`، ولذلك تتشابه طريقة التعامل معهما.

```python
from scrapling.spiders import SitemapSpider, CrawlRule, LinkExtractor

class MySitemap(SitemapSpider):
    name = "sm"
    sitemap_urls = ["https://example.com/sitemap.xml"]

    def rules(self):
        return [
            CrawlRule(LinkExtractor(allow=r"/posts/"), callback=self.parse_post),
            CrawlRule(LinkExtractor(allow=r"/products/"), callback=self.parse_product),
        ]

    async def parse_post(self, response):
        yield {"title": response.css("h1::text").get()}

    async def parse_product(self, response):
        yield {"sku": response.css(".sku::text").get()}

result = MySitemap().start()
```

### كيفية توجيه عناوين URL {#how-urls-are-dispatched}

لكل URL في خريطة الموقع، يفحص `SitemapSpider` الدالة `LinkExtractor.matches(url)` لكل قاعدة بالترتيب. تُستخدم أول قاعدة مطابقة، ويُخرج `Request` بدالة callback الخاصة بها. إذا لم تطابق أي قاعدة وكان ناتج `rules()` غير فارغ، يُستبعد العنوان. وإذا أعادت `rules()` قائمة فارغة، يُرسل كل عنوان إلى `parse()` الخاصة بالعنكبوت. هذه الدالة ترفع `NotImplementedError` افتراضيًا إذا لم تُعد تعريفها.

### فهارس خرائط الموقع {#sitemap-indexes}

إذا وجد `SitemapSpider` عنصر `<sitemapindex>`، أي خريطة تحتوي على خرائط أخرى، يدخل إلى كل خريطة فرعية تلقائيًا. لتحديد الخرائط الفرعية التي تريد متابعتها، اضبط `sitemap_follow` على `LinkExtractor`:

```python
class MySitemap(SitemapSpider):
    name = "sm"
    sitemap_urls = ["https://example.com/sitemap.xml"]
    sitemap_follow = LinkExtractor(allow=r"/posts-sitemap-\d+\.xml")  # only post sitemaps
```

### دعم robots.txt {#robotstxt-support}

ضع عنوان ملف `robots.txt` مباشرة في `sitemap_urls`. سيتعرف عليه `SitemapSpider`، ويستخرج كل خرائط الموقع المذكورة فيه، ثم يتابعها:

```python
class MySitemap(SitemapSpider):
    name = "sm"
    sitemap_urls = ["https://example.com/robots.txt"]
```

### عناوين اللغات الأخرى {#alternate-language-urls}

اضبط `sitemap_alternate_links = True` لتمرير عناوين `<xhtml:link rel="alternate" hreflang="...">` إلى القواعد أيضًا.

## XMLFeedSpider {#xmlfeedspider}

يمرّ `XMLFeedSpider` على عناصر مصدر بيانات XML، مثل RSS وAtom وملفات المنتجات. اضبط `itertag` على اسم العنصر المطلوب، والقيمة الافتراضية هي `"item"`. وأعد تعريف `parse_node()`، التي تُستدعى مرة لكل عنصر مطابق:

```python
from scrapling.spiders import XMLFeedSpider

class RSSSpider(XMLFeedSpider):
    name = "rss"
    start_urls = ["https://example.com/feed.xml"]
    itertag = "item"

    async def parse_node(self, response, node):
        yield {
            "title": node.findtext("title"),
            "link": node.findtext("link"),
            "date": node.findtext("pubDate"),
        }

result = RSSSpider().start()
```

مثل دوال callback الأخرى، يمكن لـ `parse_node()` إخراج كائنات `Request` أيضًا. مثلًا، يمكنك استخدام `response.follow(node.findtext("link"), callback=self.parse_post)` لزيارة الصفحات المشار إليها في مصدر البيانات.

### كيفية مطابقة العناصر وتحليلها {#how-nodes-are-matched-and-parsed}

كل عنصر يصل إلى `parse_node()` هو عنصر `lxml` أُزيلت منه جميع namespaces. لذلك تعمل `node.findtext("title")` و`node.find("thumbnail").get("url")` و`node.xpath(...)` الحساسة لحالة الأحرف مع أي مصدر بيانات دون خرائط namespaces. تطابق قيمة `itertag` البسيطة، مثل `"entry"`، العناصر حسب الاسم دون اعتبار للـ namespace، وهو ما تحتاجه مع Atom ومعظم مصادر البيانات التي تستخدم namespaces. لمطابقة عنصر ضمن namespace محدد فقط، استخدم `itertag` مع بادئة، وحدد هذه البادئة في `namespaces`:

```python
class ThumbnailSpider(XMLFeedSpider):
    name = "thumbs"
    start_urls = ["https://example.com/feed.xml"]
    itertag = "media:thumbnail"
    namespaces = (("media", "http://search.yahoo.com/mrss/"),)

    async def parse_node(self, response, node):
        yield {"thumbnail": node.get("url")}
```

تُفك ملفات البيانات المضغوطة باستخدام gzip تلقائيًا، سواء كان امتدادها `.xml.gz` أو كانت تُرسل بنوع محتوى gzip. تُطبّق الحماية نفسها المستخدمة في عنكبوت خرائط الموقع. وإذا كان XML غير صالح، تُسجّل رسالة تنبيه بدلًا من توقف الزحف بخطأ.

## CSVFeedSpider {#csvfeedspider}

يمرّ `CSVFeedSpider` على صفوف مصدر بيانات CSV. أعد تعريف `parse_row()`، التي تستقبل كل صف في صورة قاموس مفاتيحه أسماء الأعمدة:

```python
from scrapling.spiders import CSVFeedSpider

class PriceSpider(CSVFeedSpider):
    name = "prices"
    start_urls = ["https://example.com/products.csv"]

    async def parse_row(self, response, row):
        yield {"product": row["title"], "price": float(row["price"])}

result = PriceSpider().start()
```

يُستخدم الصف الأول كأسماء للأعمدة افتراضيًا. إذا لم يكن هناك صف أسماء، فحددها بنفسك في `headers`. واستخدم `delimiter` و`quotechar` مع الملفات التي لا تتبع صيغة الفواصل المعتادة:

```python
class PriceSpider(CSVFeedSpider):
    name = "prices"
    start_urls = ["https://example.com/products.csv"]
    headers = ["title", "price", "url"]
    delimiter = ";"
```

تُفك الملفات المضغوطة باستخدام gzip تلقائيًا هنا أيضًا، كما سبق في **XMLFeedSpider**.

<a id="sitetomarkdownspider"></a>

## ContentSpider {#contentspider}

يعتمد `ContentSpider` على **CrawlSpider** لزيارة الموقع وتحويل كل صفحة إلى Markdown نظيف وجاهز لنماذج LLM. يُخرج عنصرًا لكل صفحة، ويمكنه أيضًا كتابة ملف Markdown منفصل لكل صفحة:

```python
from scrapling.spiders import ContentSpider

class DocsSpider(ContentSpider):
    name = "docs"
    start_urls = ["https://example.com/docs/"]
    allowed_domains = {"example.com"}
    output_dir = "docs_markdown"

result = DocsSpider().start()
```

يتطلب تحديد `allowed_domains` لحصر الزحف في الموقع المستهدف. تجد الدليل الكامل، بما فيه جميع الخيارات وكيفية استخدام النتائج في مسارات عمل RAG، في صفحة [بناء أنظمة RAG](../ai/building-rag-systems.md).

## استخدام `LinkExtractor` مباشرة {#using-linkextractor-directly}

لا يلزم استخدام القوالب. يعمل `LinkExtractor` داخل أي `Spider` عادي:

```python
from scrapling.spiders import Spider, LinkExtractor

class CustomSpider(Spider):
    name = "custom"
    start_urls = ["https://example.com"]

    def __init__(self):
        super().__init__()
        self._links = LinkExtractor(allow=r"/posts/", deny_domains="ads.example.com")

    async def parse(self, response):
        for url in self._links.extract(response):
            yield response.follow(url, callback=self.parse_post)

    async def parse_post(self, response):
        yield {"title": response.css("h1::text").get()}
```

## مرجع LinkExtractor {#linkextractor-reference}

| المعامل | القيمة الافتراضية | الوصف |
|---------|-------------------|-------|
| `allow` | `()` | أنماط عناوين URL المقبولة. القيمة الفارغة تعني قبول الجميع. يقبل نصًا أو `Pattern` جاهزًا أو iterable يحتوي على أي منهما |
| `deny` | `()` | أنماط عناوين URL المستبعدة. تتقدم دائمًا على `allow` |
| `allow_domains` | `()` | أسماء المضيفين المقبولة. تُقبل النطاقات الفرعية تلقائيًا، فـ `example.com` يقبل `api.example.com` |
| `deny_domains` | `()` | أسماء المضيفين المستبعدة |
| `restrict_css` | `()` | محددات CSS تحصر استخراج الروابط من DOM في جزء معين |
| `restrict_xpath` | `()` | محددات XPath تحصر استخراج الروابط من DOM في جزء معين |
| `tags` | `("a", "area")` | وسوم العناصر التي يُبحث فيها عن الروابط |
| `attrs` | `("href",)` | خصائص هذه الوسوم التي تُقرأ منها عناوين URL |
| `canonicalize` | `True` | ترتيب معاملات الاستعلام وتوحيد صيغة المسار |
| `strip` | `True` | إزالة المسافات البيضاء من أطراف عناوين URL المستخرجة |
| `keep_fragment` | `False` | الحفاظ على `#fragment` عند توحيد صيغة العنوان |
| `deny_extensions` | `IGNORED_EXTENSIONS` | امتدادات الملفات المستبعدة، مثل pdf وzip والصور والفيديو وغيرها |
| `process` | `None` | دالة اختيارية تُطبّق على كل عنوان مستخرج قبل تصفيته. أعد قيمة falsy، أي تُعامل كقيمة غير صحيحة، لاستبعاد العنوان |

تعيد `LinkExtractor.extract(response)` قائمة `list[str]` من عناوين URL الكاملة، بعد التصفيّة وإزالة التكرار.

تعيد `LinkExtractor.matches(url)` قيمة `bool`. وهي تطبّق تصفية العناوين فقط حسب allow وdeny والنطاق والامتداد. يستخدمها `SitemapSpider` لتوجيه العناوين دون الحاجة إلى `Response`.
