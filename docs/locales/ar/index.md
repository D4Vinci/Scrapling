---
title: "Scrapling: إطار عمل لجمع بيانات الويب باستخدام Python"
description: "Scrapling: اجمع بيانات الويب الحديث بسهولة!"
---

<style>
.md-typeset h1 {
  display: none;
}
[data-md-color-scheme="default"] .only-dark { display: none; }
[data-md-color-scheme="slate"] .only-light { display: none; }
</style>

<br/>
<div align="center">
    <a href="index.html" alt="الغلاف">
        <img alt="Scrapling" src="assets/cover_light.svg" class="only-light">
        <img alt="Scrapling" src="assets/cover_dark.svg" class="only-dark">
    </a>
</div>

<h2 align="center"><i>اجمع بيانات الويب الحديث بسهولة</i></h2><br>

Scrapling إطار عمل بلغة Python لجمع بيانات الويب. يجمع طلبات HTTP السريعة، والمتصفحات الخفية، وتحليل الصفحات، والزحف المتزامن في مكتبة واحدة.

اجمع بيانات الصفحات الثابتة، وشغّل JavaScript، وتفاعل مع المواقع، واستخرج البيانات من طلبات API التي تعمل خلفها. أنشئ برامج زحف بجلسات قابلة لإعادة الاستخدام، وتبديل البروكسي، وإعادة المحاولة تلقائيًا، والإيقاف والاستئناف، وتصدير البيانات بأدوات مدمجة.

استخدمه من Python أو الطرفية أو وكيل الذكاء الاصطناعي عبر خادم MCP وAgent Skill. يغطي Scrapling خطوات جمع البيانات كاملة، من استخراج بضعة حقول إلى جمع موقع كامل في ملفات Markdown نظيفة.

## ما الذي يمكنك فعله باستخدام Scrapling؟ {#what-you-can-do-with-scrapling}

- **[الجلب والتفاعل](fetching/choosing.md)**: طلبات HTTP سريعة، ومتصفحات خفية، وتشغيل JavaScript، والتعامل مع Cloudflare Turnstile وInterstitial، وجلسات مستمرة، وحفظ ردود API التي تعمل في الخلفية.
- **[التحليل والاستخراج](parsing/selection.md)**: البحث باستخدام CSS وXPath والنص والتعبيرات المنتظمة، وتتبع العناصر عند تغير الصفحة، والعثور على العناصر المتشابهة، وإخراج Markdown نظيف.
- **[الزحف والتصدير](spiders/getting-started.md)**: برامج Spider متزامنة، وتبديل البروكسي، وإعادة المحاولة، وAutoThrottle، والإيقاف والاستئناف، وبث النتائج، وقوالب جاهزة، وتصدير JSON وJSONL وCSV وXML.
- **[جمع البيانات بالذكاء الاصطناعي أو من الطرفية](ai/mcp-server.md)**: خادم MCP لوكلاء الذكاء الاصطناعي لتصفح المواقع واستخراج البيانات، وAgent Skill، وأوامر CLI، وواجهة تفاعلية.

ابدأ بصفحة واحدة:

```python
from scrapling.fetchers import Fetcher

page = Fetcher.get('https://quotes.toscrape.com/')
quotes = page.css('.quote .text::text').getall()
print(quotes)
```

أو وسّع العمل باستخدام Spider:

```python
from scrapling.spiders import Spider, Response

class QuotesSpider(Spider):
    name = "quotes"
    start_urls = ["https://quotes.toscrape.com/"]

    async def parse(self, response: Response):
        for quote in response.css('.quote'):
            yield {
                "text": quote.css('.text::text').get(),
                "author": quote.css('.author::text').get(),
            }

result = QuotesSpider().start()
print(len(result.items))
result.items.to_json("quotes.json")
```

يطبع هذا المثال `10` ويحفظ الاقتباسات وأسماء أصحابها في `quotes.json`.

## كبار الداعمين {#top-sponsors}

--8<-- "sponsors.html"

<i><sub>هل تريد عرض إعلانك هنا؟ اضغط [هنا](https://github.com/sponsors/D4Vinci)، واختر خطة، واستفد من بقية المزايا!</sub></i>

## الميزات الأساسية {#key-features}

### Spiders: إطار عمل كامل للزحف {#spiders-a-full-crawling-framework}
- 🕷️ **واجهة Spider تشبه Scrapy**: عرّف برامج Spider باستخدام `start_urls`، ودوال `parse` غير المتزامنة، وكائنات `Request` و`Response`.
- ⚡ **زحف متزامن**: اضبط عدد الطلبات المتزامنة، وحدود كل نطاق، ومدة الانتظار بين التنزيلات.
- 🔄 **دعم عدة جلسات**: واجهة واحدة لطلبات HTTP والمتصفحات الخفية بلا واجهة ضمن Spider واحد. وجّه الطلبات إلى جلسات مختلفة باستخدام المعرّف.
- 💾 **الإيقاف والاستئناف**: احفظ الطلبات المعلقة والروابط التي زرتها باستخدام `crawldir`. اضغط Ctrl+C للإيقاف الآمن، ثم أعد التشغيل مع المجلد نفسه.
- 📡 **بث النتائج**: استقبل العناصر فور جمعها عبر `async for item in spider.stream()`، مع إحصاءات مباشرة. يناسب الواجهات وخطوات معالجة البيانات وعمليات الزحف الطويلة.
- 🛡️ **كشف الطلبات المحظورة**: كشف الطلبات المحظورة وإعادة محاولتها تلقائيًا، مع إمكانية تخصيص السلوك.
- 🚦 **AutoThrottle**: لا تحتاج إلى تخمين مدة الانتظار. يضبط Spider المدة لكل نطاق حسب سرعة رد الموقع، ثم يضاعفها، أو ينتظر المدة التي يطلبها `Retry-After`، عندما يبدأ الموقع في الحظر أو تقييد معدل الطلبات. ويعود إلى السرعة الأعلى عند توقف ذلك.
- 🤖 **الالتزام بملف robots.txt**: خيار `robots_txt_obey` يحترم تعليمات `Disallow` و`Crawl-delay` و`Request-rate`، مع تخزين مؤقت لكل نطاق.
- 🧪 **وضع التطوير**: احفظ الردود على القرص في أول تشغيل، ثم أعد استخدامها في التشغيلات التالية. عدّل دالة `parse()` دون إرسال طلبات جديدة إلى الخوادم.
- 🧩 **قوالب Spider جاهزة**: استخدم `CrawlSpider` لتتبع الروابط وفق قواعد، و`SitemapSpider` للزحف من خرائط الموقع أو robots.txt، و`XMLFeedSpider` و`CSVFeedSpider` لقراءة خلاصات XML وRSS وCSV، و`ShopifySpider` لجمع منتجات متاجر Shopify العامة، بعنصر مستقل لكل نوع من المنتج.
- 🔗 **استخراج الروابط**: أداة `LinkExtractor` مستقلة تدعم أنماط السماح والمنع، وتصفية النطاقات والامتدادات، وحصر البحث باستخدام CSS وXPath، وتوحيد صيغة الروابط. استخدمها داخل القوالب أو وحدها.
- 📦 **تصدير مدمج**: صدّر النتائج عبر hooks وخط معالجة خاص بك، أو استخدم أدوات JSON وJSONL وCSV وXML المدمجة: `result.items.to_json()` و`to_jsonl()` و`to_csv()` و`to_xml()`.

### جلب متقدم للمواقع مع دعم الجلسات {#advanced-websites-fetching-with-session-support}
- **طلبات HTTP**: طلبات HTTP سريعة وخفية باستخدام `Fetcher`. تدعم محاكاة بصمة TLS وترويسات المتصفح واستخدام HTTP/3.
- **التحميل الديناميكي**: اجلب المواقع الديناميكية مع أتمتة كاملة للمتصفح عبر `StealthyFetcher`، الذي يدعم Chromium الخاص بـPlaywright وGoogle Chrome.
- **تجاوز كشف البوتات**: إخفاء متقدم للأتمتة ومحاكاة البصمات باستخدام `StealthyFetcher`. يمكنه تجاوز أنواع Cloudflare Turnstile وInterstitial تلقائيًا.
- **إدارة الجلسات**: تدعم `FetcherSession` و`StealthySession` الجلسات المستمرة لإدارة ملفات تعريف الارتباط وحالة المتصفح بين الطلبات.
- **تبديل البروكسي**: أداة `ProxyRotator` مدمجة تدعم التبديل الدوري أو المخصص في كل أنواع الجلسات، مع إمكانية تحديد بروكسي مستقل لكل طلب.
- **حظر النطاقات والإعلانات**: امنع الطلبات إلى نطاقات محددة ونطاقاتها الفرعية، أو فعّل حظر الإعلانات المدمج في أدوات جلب المتصفح، الذي يشمل نحو 3,500 نطاق إعلانات وتتبع معروف.
- **منع تسريب DNS**: دعم اختياري لـDNS-over-HTTPS لتوجيه استعلامات DNS عبر DoH من Cloudflare، ومنع تسريبها عند استخدام البروكسي.
- **متصفحات بعيدة**: اتصل بمتصفح يعمل بالفعل عبر CDP باستخدام `cdp_url`، سواء كان على جهازك أو جهاز آخر أو لدى مزود متصفحات، بدلًا من تشغيل متصفح محلي. ويمكنك استخدام نسخة Chromium الخاصة بك مع أي أداة جلب متصفح عبر `executable_path`.
- **حفظ ردود API في الخلفية**: فعّل `record_requests=True` في جلسة المتصفح، ثم ابحث في الردود المحفوظة عبر `session.network.search(limit=None)`. اقرأ بيانات API وأخطاء HTTP عبر عمليات تحميل الصفحات دون إعادة الطلبات. للسجل حد أقصى، ويحفظ محتوى الردود النصية.
- **الدعم غير المتزامن**: دعم كامل في كل أدوات الجلب، مع فئات جلسات مخصصة للعمل غير المتزامن.

### تحليل الصفحات واستخراج البيانات {#parsing-and-data-extraction}
- 🔄 **تتبع ذكي للعناصر**: اعثر على العناصر بعد تغير الموقع باستخدام خوارزميات مقارنة التشابه.
- 🎯 **اختيار مرن للعناصر**: محددات CSS وXPath، والبحث بالشروط أو بالنص أو بالتعبيرات المنتظمة، والمزيد.
- 🔍 **العثور على العناصر المتشابهة**: ابحث تلقائيًا عن عناصر تشبه العناصر التي وجدتها.

### ميزات الذكاء الاصطناعي {#ai-features}
- 🤖 **خادم MCP**: يتيح لوكلاء ومساعدي الذكاء الاصطناعي، مثل Claude وCursor، جمع البيانات عبر Scrapling باستخدام طلبات HTTP، والتفاعل مع المتصفح، ولقطات الشاشة، وحالة تسجيل دخول محفوظة، وردود API في الخلفية. يستخدم متصفحنا الخفي مع أدوات تساعد النماذج المناسبة على تجاوز CAPTCHA أثناء العمل، إلى جانب أداة حل Cloudflare. ويقلل المحتوى المرسل إلى النموذج، ويحظر الإعلانات، ويحميه من حقن التعليمات Prompt Injection. يدعم أيضًا المتصفحات البعيدة عبر CDP والاتصال عبر HTTP مع خيارات المصادقة. ([فيديو توضيحي](https://www.youtube.com/watch?v=qyFk3ZNwOxE))
- 🧠 **Agent Skill**: [مهارة جاهزة للتثبيت](ai/agent-skill.md) تعرّف وكلاء البرمجة على المكتبة كاملة، ليكتبوا كودًا يطابق واجهتها الحالية بدلًا من التخمين.
- 📚 **Markdown جاهز لأنظمة RAG**: حوّل أي صفحة إلى Markdown نظيف ومنقّى وجاهز لنماذج اللغة بسطر واحد (`page.markdown()`)، أو اجمع موقعًا كاملًا في مجموعة ملفات Markdown باستخدام قالب `ContentSpider`، دون الحاجة إلى نموذج لغة أثناء العملية. ([التوثيق](ai/building-rag-systems.md))

### أداء عالٍ وتصميم مجرّب {#high-performance-battle-tested-architecture}
- 🚀 **سرعة عالية**: أداء محسّن يتفوق على معظم مكتبات جمع بيانات الويب في Python.
- 🔋 **استهلاك قليل للذاكرة**: هياكل بيانات محسّنة وتحميل عند الحاجة لتقليل استخدام الذاكرة.
- ⚡ **تحويل سريع إلى JSON**: أسرع بعشر مرات من المكتبة القياسية.
- 🏗️ **مجرّب عمليًا**: تغطي الاختبارات 92% من Scrapling، وتوجد تلميحات أنواع للكود كله. كما استخدمه مئات العاملين في جمع بيانات الويب يوميًا خلال العام الماضي.

### تجربة مناسبة للمطورين وجمع البيانات {#developerweb-scraper-friendly-experience}
- 🎯 **واجهة تفاعلية لجمع البيانات**: واجهة IPython اختيارية مدمجة مع Scrapling، واختصارات وأدوات تسرّع كتابة البرامج، مثل تحويل طلبات curl إلى طلبات Scrapling وعرض نتائج الطلبات في المتصفح.
- 🚀 **استخدام مباشر من الطرفية**: يمكنك جمع بيانات رابط دون كتابة أي كود.
- 🛠️ **طرق كثيرة للتنقل**: تنقل في شجرة DOM بين الآباء والأشقاء والأبناء.
- 🧬 **معالجة نصوص محسّنة**: تعبيرات منتظمة وطرق لتنظيف النص وعمليات نصية محسّنة مدمجة.
- 📝 **إنشاء محددات تلقائيًا**: أنشئ محددات CSS وXPath موثوقة لأي عنصر.
- 🔌 **واجهة مألوفة**: تشبه Scrapy وBeautifulSoup، وتستخدم pseudo-elements نفسها الموجودة في Scrapy وParsel.
- 🤝 **تكامل مباشر مع Scrapy**: إذا كنت تستخدم Scrapy، أضف decorator باسم `scrapling_response` إلى أي callback لتحليل الردود التي تجلبها بالفعل بمحلّل Scrapling، دون إعادة كتابة البرنامج.
- 📘 **تلميحات أنواع كاملة**: دعم جيد لمحرر الكود والإكمال التلقائي. يُفحص الكود كله تلقائيًا باستخدام **PyRight** و**MyPy** مع كل تغيير.
- 🔋 **صورة Docker جاهزة**: تُبنى صورة Docker تحتوي كل المتصفحات وتُنشر تلقائيًا مع كل إصدار.


## تاريخ النجوم {#star-history}
زاد عدد نجوم Scrapling على GitHub باستمرار منذ إصداره، كما يوضح الرسم التالي.

<div id="chartContainer">
  <a href="https://github.com/D4Vinci/Scrapling">
    <img id="chartImage" alt="رسم تاريخ النجوم" loading="lazy" src="https://api.star-history.com/svg?repos=D4Vinci/Scrapling&type=Date" height="400"/>
  </a>
</div>

<script>
const observer = new MutationObserver((mutations) => {
  mutations.forEach((mutation) => {
    if (mutation.attributeName === 'data-md-color-media') {
      const colorMedia = document.body.getAttribute('data-md-color-media');
      const isDarkScheme = document.body.getAttribute('data-md-color-scheme') === 'slate';
      const chartImg = document.querySelector('#chartImage');
      const baseUrl = 'https://api.star-history.com/svg?repos=D4Vinci/Scrapling&type=Date';
      
      if (colorMedia === '(prefers-color-scheme)' ? isDarkScheme : colorMedia.includes('dark')) {
        chartImg.src = `${baseUrl}&theme=dark`;
      } else {
        chartImg.src = baseUrl;
      }
    }
  });
});

observer.observe(document.body, {
  attributes: true,
  attributeFilter: ['data-md-color-media', 'data-md-color-scheme']
});
</script>


## التثبيت {#installation}
يتطلب Scrapling إصدار Python 3.10 أو أحدث:

```bash
pip install scrapling
```

!!! warning "تنبيه"

    يثبّت هذا الأمر محلّل الصفحات ومتطلباته فقط، دون أدوات الجلب أو متطلبات سطر الأوامر. لذلك فإن استيراد أي شيء من `scrapling.fetchers` أو `scrapling.spiders`، كما في الأمثلة السابقة، سيؤدي إلى `ModuleNotFoundError` إذا اكتفيت بهذا التثبيت. لاستخدام أدوات الجلب أو Spiders، ثبّت متطلبات أدوات الجلب أولًا كما يلي.

### المتطلبات الاختيارية {#optional-dependencies}

1. إذا أردت استخدام أي من الميزات الإضافية التالية أو أدوات الجلب أو فئاتها، ثبّت متطلبات أدوات الجلب والمتصفحات كما يلي:
    ```bash
    pip install "scrapling[fetchers]"
    
    scrapling install           # normal install
    scrapling install  --force  # force reinstall
    ```

    ينزّل هذا كل المتصفحات، ومتطلبات النظام، ومتطلبات تعديل بصمات المتصفح.

    ويمكنك تثبيتها من الكود بدلًا من تشغيل أمر:
    ```python
    from scrapling.cli import install
    
    install([], standalone_mode=False)          # normal install
    install(["--force"], standalone_mode=False) # force reinstall
    ```

2. الميزات الإضافية:


     - تثبيت خادم MCP:
       ```bash
       pip install "scrapling[ai]"
       ```
     - تثبيت متطلبات [بناء أنظمة RAG](ai/building-rag-systems.md):
       ```bash
       pip install "scrapling[rag]"
       ```
     - تثبيت أدوات الطرفية، أي الواجهة التفاعلية وأمر `extract`:
         ```bash
         pip install "scrapling[shell]"
         ```
     - تثبيت كل الميزات:
         ```bash
         pip install "scrapling[all]"
         ```
   شغّل `scrapling install` عندما تحتاج إلى أدوات جلب المتصفح. لا تتطلب طلبات HTTP تثبيت متصفح.

### Docker {#docker}
يمكنك أيضًا تنزيل صورة Docker تحتوي كل الإضافات والمتصفحات من DockerHub بالأمر التالي:
```bash
docker pull pyd4vinci/scrapling
```
أو تنزيلها من سجل GitHub:
```bash
docker pull ghcr.io/d4vinci/scrapling:latest
```
تُبنى هذه الصورة وتُنشر تلقائيًا باستخدام GitHub Actions والفرع الرئيسي للمستودع.

## تنظيم التوثيق {#how-the-documentation-is-organized}
توثيق Scrapling واسع، لذلك نحاول اتباع [إطار Diátaxis للتوثيق](https://diataxis.fr/).

## الدعم {#support}

إذا أعجبك Scrapling وتريد دعم تطويره:

- ⭐ أضف نجمة إلى [مستودع GitHub](https://github.com/D4Vinci/Scrapling).
- 🚀 تابعنا على [Twitter](https://x.com/Scrapling_dev) وانضم إلى [خادم Discord](https://discord.gg/EMgGbDceNQ).
- 💝 يمكنك [رعاية المشروع أو شراء قهوة لي](donate.md). :wink:
- 🐛 أبلغ عن الأخطاء واقترح ميزات عبر [GitHub Issues](https://github.com/D4Vinci/Scrapling/issues).

## الترخيص {#license}

هذا المشروع مرخّص برخصة BSD-3. راجع ملف [LICENSE](https://github.com/D4Vinci/Scrapling/blob/main/LICENSE) للتفاصيل.
