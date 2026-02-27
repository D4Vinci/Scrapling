<!-- mcp-name: io.github.D4Vinci/Scrapling -->

<h1 align="center">
    <a href="https://scrapling.readthedocs.io">
        <picture>
          <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/docs/assets/cover_dark.svg?sanitize=true">
          <img alt="Scrapling Poster" src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/docs/assets/cover_light.svg?sanitize=true">
        </picture>
    </a>
    <br>
    <small>Effortless Web Scraping for the Modern Web</small>
</h1>

<p align="center">
    <a href="https://github.com/D4Vinci/Scrapling/actions/workflows/tests.yml" alt="Tests">
        <img alt="Tests" src="https://github.com/D4Vinci/Scrapling/actions/workflows/tests.yml/badge.svg"></a>
    <a href="https://badge.fury.io/py/Scrapling" alt="PyPI version">
        <img alt="PyPI version" src="https://badge.fury.io/py/Scrapling.svg"></a>
    <a href="https://pepy.tech/project/scrapling" alt="PyPI Downloads">
        <img alt="PyPI Downloads" src="https://static.pepy.tech/personalized-badge/scrapling?period=total&units=INTERNATIONAL_SYSTEM&left_color=GREY&right_color=GREEN&left_text=Downloads"></a>
    <br/>
    <a href="https://discord.gg/EMgGbDceNQ" alt="Discord" target="_blank">
      <img alt="Discord" src="https://img.shields.io/discord/1360786381042880532?style=social&logo=discord&link=https%3A%2F%2Fdiscord.gg%2FEMgGbDceNQ">
    </a>
    <a href="https://x.com/Scrapling_dev" alt="X (formerly Twitter)">
      <img alt="X (formerly Twitter) Follow" src="https://img.shields.io/twitter/follow/Scrapling_dev?style=social&logo=x&link=https%3A%2F%2Fx.com%2FScrapling_dev">
    </a>
    <br/>
    <a href="https://pypi.org/project/scrapling/" alt="Supported Python versions">
        <img alt="Supported Python versions" src="https://img.shields.io/pypi/pyversions/scrapling.svg"></a>
</p>

<p align="center">
    <a href="https://scrapling.readthedocs.io/en/latest/parsing/selection/"><strong>طرق الاختيار</strong></a>
    &middot;
    <a href="https://scrapling.readthedocs.io/en/latest/fetching/choosing/"><strong>اختيار Fetcher</strong></a>
    &middot;
    <a href="https://scrapling.readthedocs.io/en/latest/spiders/architecture.html"><strong>العناكب</strong></a>
    &middot;
    <a href="https://scrapling.readthedocs.io/en/latest/spiders/proxy-blocking.html"><strong>تدوير البروكسي</strong></a>
    &middot;
    <a href="https://scrapling.readthedocs.io/en/latest/cli/overview/"><strong>واجهة سطر الأوامر</strong></a>
    &middot;
    <a href="https://scrapling.readthedocs.io/en/latest/ai/mcp-server/"><strong>وضع MCP</strong></a>
</p>

Scrapling هو إطار عمل تكيفي لـ Web Scraping يتعامل مع كل شيء من طلب واحد إلى زحف كامل النطاق.

محلله يتعلم من تغييرات المواقع ويعيد تحديد موقع عناصرك تلقائياً عند تحديث الصفحات. جوالبه تتجاوز أنظمة مكافحة الروبوتات مثل Cloudflare Turnstile مباشرةً. وإطار عمل Spider الخاص به يتيح لك التوسع إلى عمليات زحف متزامنة ومتعددة الجلسات مع إيقاف/استئناف وتدوير تلقائي لـ Proxy - كل ذلك في بضعة أسطر من Python. مكتبة واحدة، بدون تنازلات.

زحف سريع للغاية مع إحصائيات فورية و Streaming. مبني بواسطة مستخرجي الويب لمستخرجي الويب والمستخدمين العاديين، هناك شيء للجميع.

```python
from scrapling.fetchers import Fetcher, AsyncFetcher, StealthyFetcher, DynamicFetcher
StealthyFetcher.adaptive = True
p = StealthyFetcher.fetch('https://example.com', headless=True, network_idle=True)  # احصل على الموقع بشكل خفي!
products = p.css('.product', auto_save=True)                                        # استخرج بيانات تنجو من تغييرات تصميم الموقع!
products = p.css('.product', adaptive=True)                                         # لاحقاً، إذا تغيرت بنية الموقع، مرر `adaptive=True` للعثور عليها!
```
أو توسع إلى عمليات زحف كاملة
```python
from scrapling.spiders import Spider, Response

class MySpider(Spider):
  name = "demo"
  start_urls = ["https://example.com/"]

  async def parse(self, response: Response):
      for item in response.css('.product'):
          yield {"title": item.css('h2::text').get()}

MySpider().start()
```


# الرعاة البلاتينيون

<i><sub>هل تريد أن تكون أول شركة تظهر هنا؟ انقر [هنا](https://github.com/sponsors/D4Vinci/sponsorships?tier_id=586646)</sub></i>
# الرعاة

<!-- sponsors -->

<a href="https://www.thordata.com/?ls=github&lk=github" target="_blank" title="Unblockable proxies and scraping infrastructure, delivering real-time, reliable web data to power AI models and workflows."><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/thordata.jpg"></a>
<a href="https://evomi.com?utm_source=github&utm_medium=banner&utm_campaign=d4vinci-scrapling" target="_blank" title="Evomi is your Swiss Quality Proxy Provider, starting at $0.49/GB"><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/evomi.png"></a>
<a href="https://serpapi.com/?utm_source=scrapling" target="_blank" title="Scrape Google and other search engines with SerpApi"><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/SerpApi.png"></a>
<a href="https://visit.decodo.com/Dy6W0b" target="_blank" title="Try the Most Efficient Residential Proxies for Free"><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/decodo.png"></a>
<a href="https://petrosky.io/d4vinci" target="_blank" title="PetroSky delivers cutting-edge VPS hosting."><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/petrosky.png"></a>
<a href="https://hasdata.com/?utm_source=github&utm_medium=banner&utm_campaign=D4Vinci" target="_blank" title="The web scraping service that actually beats anti-bot systems!"><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/hasdata.png"></a>
<a href="https://proxyempire.io/" target="_blank" title="Collect The Data Your Project Needs with the Best Residential Proxies"><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/ProxyEmpire.png"></a>
<a href="https://hypersolutions.co/?utm_source=github&utm_medium=readme&utm_campaign=scrapling" target="_blank" title="Bot Protection Bypass API for Akamai, DataDome, Incapsula & Kasada"><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/HyperSolutions.png"></a>


<a href="https://www.swiftproxy.net/" target="_blank" title="Unlock Reliable Proxy Services with Swiftproxy!"><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/swiftproxy.png"></a>
<a href="https://www.rapidproxy.io/?ref=d4v" target="_blank" title="Affordable Access to the Proxy World – bypass CAPTCHAs blocks, and avoid additional costs."><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/rapidproxy.jpg"></a>
<a href="https://browser.cash/?utm_source=D4Vinci&utm_medium=referral" target="_blank" title="Browser Automation & AI Browser Agent Platform"><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/browserCash.png"></a>

<!-- /sponsors -->

<i><sub>هل تريد عرض إعلانك هنا؟ انقر [هنا](https://github.com/sponsors/D4Vinci) واختر المستوى الذي يناسبك!</sub></i>

---

## الميزات الرئيسية

### Spiders — إطار عمل زحف كامل
- 🕷️ **واجهة Spider شبيهة بـ Scrapy**: عرّف Spiders مع `start_urls`، و async `parse` callbacks، وكائنات `Request`/`Response`.
- ⚡ **زحف متزامن**: حدود تزامن قابلة للتكوين، وتحكم بالسرعة حسب النطاق، وتأخيرات التنزيل.
- 🔄 **دعم الجلسات المتعددة**: واجهة موحدة لطلبات HTTP، ومتصفحات خفية بدون واجهة في Spider واحد — وجّه الطلبات إلى جلسات مختلفة بالمعرّف.
- 💾 **إيقاف واستئناف**: استمرارية الزحف القائمة على Checkpoint. اضغط Ctrl+C للإيقاف بسلاسة؛ أعد التشغيل للاستئناف من حيث توقفت.
- 📡 **وضع Streaming**: بث العناصر المستخرجة فور وصولها عبر `async for item in spider.stream()` مع إحصائيات فورية — مثالي لواجهات المستخدم وخطوط الأنابيب وعمليات الزحف الطويلة.
- 🛡️ **كشف الطلبات المحظورة**: كشف تلقائي وإعادة محاولة للطلبات المحظورة مع منطق قابل للتخصيص.
- 📦 **تصدير مدمج**: صدّر النتائج عبر الخطافات وخط الأنابيب الخاص بك أو JSON/JSONL المدمج مع `result.items.to_json()` / `result.items.to_jsonl()` على التوالي.

### جلب متقدم للمواقع مع دعم الجلسات
- **طلبات HTTP**: طلبات HTTP سريعة وخفية مع فئة `Fetcher`. يمكنها تقليد بصمة TLS للمتصفح والرؤوس واستخدام HTTP/3.
- **التحميل الديناميكي**: جلب المواقع الديناميكية مع أتمتة كاملة للمتصفح من خلال فئة `DynamicFetcher` التي تدعم Chromium من Playwright و Google Chrome.
- **تجاوز مكافحة الروبوتات**: قدرات تخفي متقدمة مع `StealthyFetcher` وانتحال fingerprint. يمكنه تجاوز جميع أنواع Turnstile/Interstitial من Cloudflare بسهولة بالأتمتة.
- **إدارة الجلسات**: دعم الجلسات المستمرة مع فئات `FetcherSession` و`StealthySession` و`DynamicSession` لإدارة ملفات تعريف الارتباط والحالة عبر الطلبات.
- **تدوير Proxy**: `ProxyRotator` مدمج مع استراتيجيات التدوير الدوري أو المخصصة عبر جميع أنواع الجلسات، بالإضافة إلى تجاوزات Proxy لكل طلب.
- **حظر النطاقات**: حظر الطلبات إلى نطاقات محددة (ونطاقاتها الفرعية) في الجوالب المعتمدة على المتصفح.
- **دعم Async**: دعم async كامل عبر جميع الجوالب وفئات الجلسات async المخصصة.

### الاستخراج التكيفي والتكامل مع الذكاء الاصطناعي
- 🔄 **تتبع العناصر الذكي**: إعادة تحديد موقع العناصر بعد تغييرات الموقع باستخدام خوارزميات التشابه الذكية.
- 🎯 **الاختيار المرن الذكي**: محددات CSS، محددات XPath، البحث القائم على الفلاتر، البحث النصي، البحث بالتعبيرات العادية والمزيد.
- 🔍 **البحث عن عناصر مشابهة**: تحديد العناصر المشابهة للعناصر الموجودة تلقائياً.
- 🤖 **خادم MCP للاستخدام مع الذكاء الاصطناعي**: خادم MCP مدمج لـ Web Scraping بمساعدة الذكاء الاصطناعي واستخراج البيانات. يتميز خادم MCP بقدرات قوية مخصصة تستفيد من Scrapling لاستخراج المحتوى المستهدف قبل تمريره إلى الذكاء الاصطناعي (Claude/Cursor/إلخ)، وبالتالي تسريع العمليات وتقليل التكاليف عن طريق تقليل استخدام الرموز. ([فيديو توضيحي](https://www.youtube.com/watch?v=qyFk3ZNwOxE))

### بنية عالية الأداء ومختبرة ميدانياً
- 🚀 **سريع كالبرق**: أداء محسّن يتفوق على معظم مكتبات Web Scraping في Python.
- 🔋 **فعال في استخدام الذاكرة**: هياكل بيانات محسّنة وتحميل كسول لأقل استخدام للذاكرة.
- ⚡ **تسلسل JSON سريع**: أسرع 10 مرات من المكتبة القياسية.
- 🏗️ **مُختبر ميدانياً**: لا يمتلك Scrapling فقط تغطية اختبار بنسبة 92٪ وتغطية كاملة لتلميحات الأنواع، بل تم استخدامه يومياً من قبل مئات مستخرجي الويب خلال العام الماضي.

### تجربة صديقة للمطورين/مستخرجي الويب
- 🎯 **Shell تفاعلي لـ Web Scraping**: Shell IPython مدمج اختياري مع تكامل Scrapling، واختصارات، وأدوات جديدة لتسريع تطوير سكريبتات Web Scraping، مثل تحويل طلبات curl إلى طلبات Scrapling وعرض نتائج الطلبات في متصفحك.
- 🚀 **استخدمه مباشرة من الطرفية**: اختيارياً، يمكنك استخدام Scrapling لاستخراج عنوان URL دون كتابة سطر واحد من الكود!
- 🛠️ **واجهة تنقل غنية**: اجتياز DOM متقدم مع طرق التنقل بين العناصر الوالدية والشقيقة والفرعية.
- 🧬 **معالجة نصوص محسّنة**: تعبيرات عادية مدمجة وطرق تنظيف وعمليات نصية محسّنة.
- 📝 **إنشاء محددات تلقائي**: إنشاء محددات CSS/XPath قوية لأي عنصر.
- 🔌 **واجهة مألوفة**: مشابه لـ Scrapy/BeautifulSoup مع نفس العناصر الزائفة المستخدمة في Scrapy/Parsel.
- 📘 **تغطية كاملة للأنواع**: تلميحات نوع كاملة لدعم IDE ممتاز وإكمال الكود. يتم فحص قاعدة الكود بالكامل تلقائياً بواسطة **PyRight** و**MyPy** مع كل تغيير.
- 🔋 **صورة Docker جاهزة**: مع كل إصدار، يتم بناء ودفع صورة Docker تحتوي على جميع المتصفحات تلقائياً.

## البدء

لنلقِ نظرة سريعة على ما يمكن لـ Scrapling فعله دون التعمق.

### الاستخدام الأساسي
طلبات HTTP مع دعم الجلسات
```python
from scrapling.fetchers import Fetcher, FetcherSession

with FetcherSession(impersonate='chrome') as session:  # استخدم أحدث إصدار من بصمة TLS لـ Chrome
    page = session.get('https://quotes.toscrape.com/', stealthy_headers=True)
    quotes = page.css('.quote .text::text').getall()

# أو استخدم طلبات لمرة واحدة
page = Fetcher.get('https://quotes.toscrape.com/')
quotes = page.css('.quote .text::text').getall()
```
وضع التخفي المتقدم
```python
from scrapling.fetchers import StealthyFetcher, StealthySession

with StealthySession(headless=True, solve_cloudflare=True) as session:  # أبقِ المتصفح مفتوحاً حتى تنتهي
    page = session.fetch('https://nopecha.com/demo/cloudflare', google_search=False)
    data = page.css('#padded_content a').getall()

# أو استخدم نمط الطلب لمرة واحدة، يفتح المتصفح لهذا الطلب، ثم يغلقه بعد الانتهاء
page = StealthyFetcher.fetch('https://nopecha.com/demo/cloudflare')
data = page.css('#padded_content a').getall()
```
أتمتة المتصفح الكاملة
```python
from scrapling.fetchers import DynamicFetcher, DynamicSession

with DynamicSession(headless=True, disable_resources=False, network_idle=True) as session:  # أبقِ المتصفح مفتوحاً حتى تنتهي
    page = session.fetch('https://quotes.toscrape.com/', load_dom=False)
    data = page.xpath('//span[@class="text"]/text()').getall()  # محدد XPath إذا كنت تفضله

# أو استخدم نمط الطلب لمرة واحدة، يفتح المتصفح لهذا الطلب، ثم يغلقه بعد الانتهاء
page = DynamicFetcher.fetch('https://quotes.toscrape.com/')
data = page.css('.quote .text::text').getall()
```

### Spiders
ابنِ زواحف كاملة مع طلبات متزامنة وأنواع جلسات متعددة وإيقاف/استئناف:
```python
from scrapling.spiders import Spider, Request, Response

class QuotesSpider(Spider):
    name = "quotes"
    start_urls = ["https://quotes.toscrape.com/"]
    concurrent_requests = 10

    async def parse(self, response: Response):
        for quote in response.css('.quote'):
            yield {
                "text": quote.css('.text::text').get(),
                "author": quote.css('.author::text').get(),
            }

        next_page = response.css('.next a')
        if next_page:
            yield response.follow(next_page[0].attrib['href'])

result = QuotesSpider().start()
print(f"Scraped {len(result.items)} quotes")
result.items.to_json("quotes.json")
```
استخدم أنواع جلسات متعددة في Spider واحد:
```python
from scrapling.spiders import Spider, Request, Response
from scrapling.fetchers import FetcherSession, AsyncStealthySession

class MultiSessionSpider(Spider):
    name = "multi"
    start_urls = ["https://example.com/"]

    def configure_sessions(self, manager):
        manager.add("fast", FetcherSession(impersonate="chrome"))
        manager.add("stealth", AsyncStealthySession(headless=True), lazy=True)

    async def parse(self, response: Response):
        for link in response.css('a::attr(href)').getall():
            # وجّه الصفحات المحمية عبر جلسة التخفي
            if "protected" in link:
                yield Request(link, sid="stealth")
            else:
                yield Request(link, sid="fast", callback=self.parse)  # callback صريح
```
أوقف واستأنف عمليات الزحف الطويلة مع Checkpoints بتشغيل Spider هكذا:
```python
QuotesSpider(crawldir="./crawl_data").start()
```
اضغط Ctrl+C للإيقاف بسلاسة — يتم حفظ التقدم تلقائياً. لاحقاً، عند تشغيل Spider مرة أخرى، مرر نفس `crawldir`، وسيستأنف من حيث توقف.

### التحليل المتقدم والتنقل
```python
from scrapling.fetchers import Fetcher

# اختيار عناصر غني وتنقل
page = Fetcher.get('https://quotes.toscrape.com/')

# احصل على الاقتباسات بطرق اختيار متعددة
quotes = page.css('.quote')  # محدد CSS
quotes = page.xpath('//div[@class="quote"]')  # XPath
quotes = page.find_all('div', {'class': 'quote'})  # بأسلوب BeautifulSoup
# نفس الشيء مثل
quotes = page.find_all('div', class_='quote')
quotes = page.find_all(['div'], class_='quote')
quotes = page.find_all(class_='quote')  # وهكذا...
# البحث عن عنصر بمحتوى النص
quotes = page.find_by_text('quote', tag='div')

# التنقل المتقدم
quote_text = page.css('.quote')[0].css('.text::text').get()
quote_text = page.css('.quote').css('.text::text').getall()  # محددات متسلسلة
first_quote = page.css('.quote')[0]
author = first_quote.next_sibling.css('.author::text')
parent_container = first_quote.parent

# علاقات العناصر والتشابه
similar_elements = first_quote.find_similar()
below_elements = first_quote.below_elements()
```
يمكنك استخدام المحلل مباشرة إذا كنت لا تريد جلب المواقع كما يلي:
```python
from scrapling.parser import Selector

page = Selector("<html>...</html>")
```
وهو يعمل بنفس الطريقة تماماً!

### أمثلة إدارة الجلسات بشكل Async
```python
import asyncio
from scrapling.fetchers import FetcherSession, AsyncStealthySession, AsyncDynamicSession

async with FetcherSession(http3=True) as session:  # `FetcherSession` واعٍ بالسياق ويعمل في كلا النمطين المتزامن/async
    page1 = session.get('https://quotes.toscrape.com/')
    page2 = session.get('https://quotes.toscrape.com/', impersonate='firefox135')

# استخدام جلسة async
async with AsyncStealthySession(max_pages=2) as session:
    tasks = []
    urls = ['https://example.com/page1', 'https://example.com/page2']

    for url in urls:
        task = session.fetch(url)
        tasks.append(task)

    print(session.get_pool_stats())  # اختياري - حالة مجموعة علامات تبويب المتصفح (مشغول/حر/خطأ)
    results = await asyncio.gather(*tasks)
    print(session.get_pool_stats())
```

## واجهة سطر الأوامر والـ Shell التفاعلي

يتضمن Scrapling واجهة سطر أوامر قوية:

[![asciicast](https://asciinema.org/a/736339.svg)](https://asciinema.org/a/736339)

تشغيل Shell الـ Web Scraping التفاعلي
```bash
scrapling shell
```
استخرج الصفحات إلى ملف مباشرة دون برمجة (يستخرج المحتوى داخل وسم `body` افتراضياً). إذا انتهى ملف الإخراج بـ `.txt`، فسيتم استخراج محتوى النص للهدف. إذا انتهى بـ `.md`، فسيكون تمثيل Markdown لمحتوى HTML؛ إذا انتهى بـ `.html`، فسيكون محتوى HTML نفسه.
```bash
scrapling extract get 'https://example.com' content.md
scrapling extract get 'https://example.com' content.txt --css-selector '#fromSkipToProducts' --impersonate 'chrome'  # جميع العناصر المطابقة لمحدد CSS '#fromSkipToProducts'
scrapling extract fetch 'https://example.com' content.md --css-selector '#fromSkipToProducts' --no-headless
scrapling extract stealthy-fetch 'https://nopecha.com/demo/cloudflare' captchas.html --css-selector '#padded_content a' --solve-cloudflare
```

> [!NOTE]
> هناك العديد من الميزات الإضافية، لكننا نريد إبقاء هذه الصفحة موجزة، بما في ذلك خادم MCP والـ Shell التفاعلي لـ Web Scraping. تحقق من الوثائق الكاملة [هنا](https://scrapling.readthedocs.io/en/latest/)

## معايير الأداء

Scrapling ليس قوياً فحسب — بل هو أيضاً سريع بشكل مذهل. تقارن المعايير التالية محلل Scrapling مع أحدث إصدارات المكتبات الشائعة الأخرى.

### اختبار سرعة استخراج النص (5000 عنصر متداخل)

| # |      المكتبة      | الوقت (ms) | vs Scrapling |
|---|:-----------------:|:----------:|:------------:|
| 1 |     Scrapling     |    2.02    |     1.0x     |
| 2 |   Parsel/Scrapy   |    2.04    |     1.01     |
| 3 |     Raw Lxml      |    2.54    |    1.257     |
| 4 |      PyQuery      |   24.17    |     ~12x     |
| 5 |    Selectolax     |   82.63    |     ~41x     |
| 6 |  MechanicalSoup   |  1549.71   |   ~767.1x    |
| 7 |   BS4 with Lxml   |  1584.31   |   ~784.3x    |
| 8 | BS4 with html5lib |  3391.91   |   ~1679.1x   |


### أداء تشابه العناصر والبحث النصي

قدرات العثور على العناصر التكيفية لـ Scrapling تتفوق بشكل كبير على البدائل:

| المكتبة     | الوقت (ms) | vs Scrapling |
|-------------|:----------:|:------------:|
| Scrapling   |    2.39    |     1.0x     |
| AutoScraper |   12.45    |    5.209x    |


> تمثل جميع المعايير متوسطات أكثر من 100 تشغيل. انظر [benchmarks.py](https://github.com/D4Vinci/Scrapling/blob/main/benchmarks.py) للمنهجية.

## التثبيت

يتطلب Scrapling إصدار Python 3.10 أو أعلى:

```bash
pip install scrapling
```

يتضمن هذا التثبيت فقط محرك المحلل وتبعياته، بدون أي جوالب أو تبعيات سطر الأوامر.

### التبعيات الاختيارية

1. إذا كنت ستستخدم أياً من الميزات الإضافية أدناه، أو الجوالب، أو فئاتها، فستحتاج إلى تثبيت تبعيات الجوالب وتبعيات المتصفح الخاصة بها على النحو التالي:
    ```bash
    pip install "scrapling[fetchers]"

    scrapling install           # normal install
    scrapling install  --force  # force reinstall
    ```

    يقوم هذا بتنزيل جميع المتصفحات، إلى جانب تبعيات النظام وتبعيات معالجة fingerprint الخاصة بها.

    أو يمكنك تثبيتها من الكود بدلاً من تشغيل أمر كالتالي:
    ```python
    from scrapling.cli import install

    install([], standalone_mode=False)          # normal install
    install(["--force"], standalone_mode=False) # force reinstall
    ```

2. ميزات إضافية:
   - تثبيت ميزة خادم MCP:
       ```bash
       pip install "scrapling[ai]"
       ```
   - تثبيت ميزات Shell (Shell الـ Web Scraping وأمر `extract`):
       ```bash
       pip install "scrapling[shell]"
       ```
   - تثبيت كل شيء:
       ```bash
       pip install "scrapling[all]"
       ```
   تذكر أنك تحتاج إلى تثبيت تبعيات المتصفح مع `scrapling install` بعد أي من هذه الإضافات (إذا لم تكن قد فعلت ذلك بالفعل)

### Docker
يمكنك أيضاً تثبيت صورة Docker مع جميع الإضافات والمتصفحات باستخدام الأمر التالي من DockerHub:
```bash
docker pull pyd4vinci/scrapling
```
أو تنزيلها من سجل GitHub:
```bash
docker pull ghcr.io/d4vinci/scrapling:latest
```
يتم بناء هذه الصورة ودفعها تلقائياً باستخدام GitHub Actions والفرع الرئيسي للمستودع.

## المساهمة

نرحب بالمساهمات! يرجى قراءة [إرشادات المساهمة](https://github.com/D4Vinci/Scrapling/blob/main/CONTRIBUTING.md) قبل البدء.

## إخلاء المسؤولية

> [!CAUTION]
> يتم توفير هذه المكتبة للأغراض التعليمية والبحثية فقط. باستخدام هذه المكتبة، فإنك توافق على الامتثال لقوانين استخراج البيانات والخصوصية المحلية والدولية. المؤلفون والمساهمون غير مسؤولين عن أي إساءة استخدام لهذا البرنامج. احترم دائماً شروط خدمة المواقع وملفات robots.txt.

## الترخيص

هذا العمل مرخص بموجب ترخيص BSD-3-Clause.

## الشكر والتقدير

يتضمن هذا المشروع كوداً معدلاً من:
- Parsel (ترخيص BSD) — يُستخدم للوحدة الفرعية [translator](https://github.com/D4Vinci/Scrapling/blob/main/scrapling/core/translator.py)

---
<div align="center"><small>مصمم ومصنوع بـ ❤️ بواسطة كريم شعير.</small></div><br>
