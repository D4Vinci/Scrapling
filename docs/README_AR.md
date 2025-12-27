<p align=center>
  <br>
  <a href="https://scrapling.readthedocs.io/en/latest/" target="_blank"><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/poster.png" style="width: 50%; height: 100%;" alt="main poster"/></a>
  <br>
  <i><code>استخراج بيانات الويب بسهولة ويسر كما يجب أن يكون!</code></i>
</p>
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
    <a href="https://scrapling.readthedocs.io/en/latest/parsing/selection/">
        طرق الاختيار
    </a>
    ·
    <a href="https://scrapling.readthedocs.io/en/latest/fetching/choosing/">
        اختيار الجالب
    </a>
    ·
    <a href="https://scrapling.readthedocs.io/en/latest/cli/overview/">
        واجهة سطر الأوامر
    </a>
    ·
    <a href="https://scrapling.readthedocs.io/en/latest/ai/mcp-server/">
        وضع MCP
    </a>
    ·
    <a href="https://scrapling.readthedocs.io/en/latest/tutorials/migrating_from_beautifulsoup/">
        الانتقال من Beautifulsoup
    </a>
</p>

**توقف عن محاربة أنظمة مكافحة الروبوتات. توقف عن إعادة كتابة المحددات بعد كل تحديث للموقع.**

Scrapling ليست مجرد مكتبة أخرى لاستخراج بيانات الويب. إنها أول مكتبة استخراج **تكيفية** تتعلم من تغييرات المواقع وتتطور معها. بينما تتعطل المكتبات الأخرى عندما تحدث المواقع بنيتها، يعيد Scrapling تحديد موقع عناصرك تلقائياً ويحافظ على عمل أدوات الاستخراج الخاصة بك.

مبني للويب الحديث، يتميز Scrapling **بمحرك تحليل سريع خاص به** وجوالب للتعامل مع جميع تحديات استخراج بيانات الويب التي تواجهها أو ستواجهها. مبني بواسطة مستخرجي الويب لمستخرجي الويب والمستخدمين العاديين، هناك شيء للجميع.

```python
>> from scrapling.fetchers import Fetcher, AsyncFetcher, StealthyFetcher, DynamicFetcher
>> StealthyFetcher.adaptive = True
# احصل على كود المصدر للمواقع بشكل خفي!
>> page = StealthyFetcher.fetch('https://example.com', headless=True, network_idle=True)
>> print(page.status)
200
>> products = page.css('.product', auto_save=True)  # استخرج البيانات التي تنجو من تغييرات تصميم الموقع!
>> # لاحقاً، إذا تغيرت بنية الموقع، مرر `adaptive=True`
>> products = page.css('.product', adaptive=True)  # و Scrapling لا يزال يجدها!
```

# الرعاة 

<!-- sponsors -->

<a href="https://www.scrapeless.com/en?utm_source=official&utm_term=scrapling" target="_blank" title="Effortless Web Scraping Toolkit for Business and Developers"><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/scrapeless.jpg"></a>
<a href="https://www.thordata.com/?ls=github&lk=github" target="_blank" title="Unblockable proxies and scraping infrastructure, delivering real-time, reliable web data to power AI models and workflows."><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/thordata.jpg"></a>
<a href="https://evomi.com?utm_source=github&utm_medium=banner&utm_campaign=d4vinci-scrapling" target="_blank" title="Evomi is your Swiss Quality Proxy Provider, starting at $0.49/GB"><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/evomi.png"></a>
<a href="https://serpapi.com/?utm_source=scrapling" target="_blank" title="Scrape Google and other search engines with SerpApi"><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/SerpApi.png"></a>
<a href="https://visit.decodo.com/Dy6W0b" target="_blank" title="Try the Most Efficient Residential Proxies for Free"><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/decodo.png"></a>
<a href="https://petrosky.io/d4vinci" target="_blank" title="PetroSky delivers cutting-edge VPS hosting."><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/petrosky.png"></a>
<a href="https://www.swiftproxy.net/" target="_blank" title="Unlock Reliable Proxy Services with Swiftproxy!"><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/swiftproxy.png"></a>
<a href="https://www.rapidproxy.io/?ref=d4v" target="_blank" title="Affordable Access to the Proxy World – bypass CAPTCHAs blocks, and avoid additional costs."><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/rapidproxy.jpg"></a>
<a href="https://browser.cash/?utm_source=D4Vinci&utm_medium=referral" target="_blank" title="Browser Automation & AI Browser Agent Platform"><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/browserCash.png"></a>

<!-- /sponsors -->

<i><sub>هل تريد عرض إعلانك هنا؟ انقر [هنا](https://github.com/sponsors/D4Vinci) واختر المستوى الذي يناسبك!</sub></i>

---

## الميزات الرئيسية

### جلب متقدم للمواقع مع دعم الجلسات
- **طلبات HTTP**: طلبات HTTP سريعة وخفية مع فئة `Fetcher`. يمكنها تقليد بصمة TLS للمتصفح والرؤوس واستخدام HTTP3.
- **التحميل الديناميكي**: جلب المواقع الديناميكية مع أتمتة كاملة للمتصفح من خلال فئة `DynamicFetcher` التي تدعم Chromium من Playwright و Google Chrome.
- **تجاوز مكافحة الروبوتات**: قدرات تخفي متقدمة مع `StealthyFetcher` وانتحال البصمات. يمكنه تجاوز جميع أنواع Turnstile/Interstitial من Cloudflare بسهولة بالأتمتة.
- **إدارة الجلسات**: دعم الجلسات المستمرة مع فئات `FetcherSession` و`StealthySession` و`DynamicSession` لإدارة ملفات تعريف الارتباط والحالة عبر الطلبات.
- **دعم Async**: دعم async كامل عبر جميع الجوالب وفئات الجلسات async المخصصة.

### الاستخراج التكيفي والتكامل مع الذكاء الاصطناعي
- 🔄 **تتبع العناصر الذكي**: إعادة تحديد موقع العناصر بعد تغييرات الموقع باستخدام خوارزميات التشابه الذكية.
- 🎯 **الاختيار المرن الذكي**: محددات CSS، محددات XPath، البحث القائم على الفلاتر، البحث النصي، البحث بالتعبيرات العادية والمزيد.
- 🔍 **البحث عن عناصر مشابهة**: تحديد العناصر المشابهة للعناصر الموجودة تلقائياً.
- 🤖 **خادم MCP للاستخدام مع الذكاء الاصطناعي**: خادم MCP مدمج لاستخراج بيانات الويب بمساعدة الذكاء الاصطناعي واستخراج البيانات. يتميز خادم MCP بقدرات قوية مخصصة تستفيد من Scrapling لاستخراج المحتوى المستهدف قبل تمريره إلى الذكاء الاصطناعي (Claude/Cursor/إلخ)، وبالتالي تسريع العمليات وتقليل التكاليف عن طريق تقليل استخدام الرموز. ([فيديو توضيحي](https://www.youtube.com/watch?v=qyFk3ZNwOxE))

### بنية عالية الأداء ومختبرة في المعارك
- 🚀 **سريع كالبرق**: أداء محسّن يتفوق على معظم مكتبات استخراج Python.
- 🔋 **فعال في استخدام الذاكرة**: هياكل بيانات محسّنة وتحميل كسول لأقل استخدام للذاكرة.
- ⚡ **تسلسل JSON سريع**: أسرع 10 مرات من المكتبة القياسية.
- 🏗️ **مُختبر في المعارك**: لا يمتلك Scrapling فقط تغطية اختبار بنسبة 92٪ وتغطية كاملة لتلميحات الأنواع، ولكن تم استخدامه يومياً من قبل مئات مستخرجي الويب خلال العام الماضي.

### تجربة صديقة للمطورين/مستخرجي الويب
- 🎯 **غلاف استخراج ويب تفاعلي**: غلاف IPython مدمج اختياري مع تكامل Scrapling، واختصارات، وأدوات جديدة لتسريع تطوير سكريبتات استخراج الويب، مثل تحويل طلبات curl إلى طلبات Scrapling وعرض نتائج الطلبات في متصفحك.
- 🚀 **استخدمه مباشرة من الطرفية**: اختيارياً، يمكنك استخدام Scrapling لاستخراج عنوان URL دون كتابة سطر واحد من الكود!
- 🛠️ **واجهة برمجة تطبيقات التنقل الغنية**: اجتياز DOM متقدم مع طرق التنقل بين الوالدين والأشقاء والأطفال.
- 🧬 **معالجة نصوص محسّنة**: تعبيرات عادية مدمجة وطرق تنظيف وعمليات سلسلة محسّنة.
- 📝 **إنشاء محدد تلقائي**: إنشاء محددات CSS/XPath قوية لأي عنصر.
- 🔌 **واجهة برمجة تطبيقات مألوفة**: مشابه لـ Scrapy/BeautifulSoup مع نفس العناصر الزائفة المستخدمة في Scrapy/Parsel.
- 📘 **تغطية كاملة للأنواع**: تلميحات نوع كاملة لدعم IDE ممتاز وإكمال الكود.
- 🔋 **صورة Docker جاهزة**: مع كل إصدار، يتم بناء ودفع صورة Docker تحتوي على جميع المتصفحات تلقائياً.

## البدء

### الاستخدام الأساسي
```python
from scrapling.fetchers import Fetcher, StealthyFetcher, DynamicFetcher
from scrapling.fetchers import FetcherSession, StealthySession, DynamicSession

# طلبات HTTP مع دعم الجلسات
with FetcherSession(impersonate='chrome') as session:  # استخدم أحدث إصدار من بصمة TLS لـ Chrome
    page = session.get('https://quotes.toscrape.com/', stealthy_headers=True)
    quotes = page.css('.quote .text::text')

# أو استخدم طلبات لمرة واحدة
page = Fetcher.get('https://quotes.toscrape.com/')
quotes = page.css('.quote .text::text')

# وضع التخفي المتقدم (احتفظ بالمتصفح مفتوحاً حتى تنتهي)
with StealthySession(headless=True, solve_cloudflare=True) as session:
    page = session.fetch('https://nopecha.com/demo/cloudflare', google_search=False)
    data = page.css('#padded_content a')

# أو استخدم نمط الطلب لمرة واحدة، يفتح المتصفح لهذا الطلب، ثم يغلقه بعد الانتهاء
page = StealthyFetcher.fetch('https://nopecha.com/demo/cloudflare')
data = page.css('#padded_content a')
    
# أتمتة المتصفح الكاملة (احتفظ بالمتصفح مفتوحاً حتى تنتهي)
with DynamicSession(headless=True) as session:
    page = session.fetch('https://quotes.toscrape.com/', network_idle=True)
    quotes = page.css('.quote .text::text')

# أو استخدم نمط الطلب لمرة واحدة
page = DynamicFetcher.fetch('https://quotes.toscrape.com/', network_idle=True)
quotes = page.css('.quote .text::text')
```

### اختيار العناصر
```python
# محددات CSS
page.css('a::text')                      # استخراج النص
page.css('a::attr(href)')                # استخراج السمات
page.css('a', recursive=False)           # العناصر المباشرة فقط
page.css('a', auto_save=True)            # حفظ مواضع العناصر تلقائياً

# XPath
page.xpath('//a/text()')

# بحث مرن
page.find_by_text('Python', first_match=True)  # البحث بالنص
page.find_by_regex(r'\d{4}')                   # البحث بنمط التعبير العادي
page.find('div', {'class': 'container'})       # البحث بالسمات

# التنقل
element.parent                           # الحصول على العنصر الوالد
element.next_sibling                     # الحصول على الشقيق التالي
element.children                         # الحصول على الأطفال

# عناصر مشابهة
similar = page.get_similar(element)      # البحث عن عناصر مشابهة

# الاستخراج التكيفي
saved_elements = page.css('.product', auto_save=True)
# لاحقاً، عندما يتغير الموقع:
page.css('.product', adaptive=True)      # البحث عن العناصر باستخدام المواضع المحفوظة
```

### استخدام الجلسة
```python
from scrapling.fetchers import FetcherSession, AsyncFetcherSession

# جلسة متزامنة
with FetcherSession() as session:
    # يتم الاحتفاظ بملفات تعريف الارتباط تلقائياً
    page1 = session.get('https://quotes.toscrape.com/login')
    page2 = session.post('https://quotes.toscrape.com/login', data={'username': 'admin', 'password': 'admin'})
    
    # تبديل بصمة المتصفح إذا لزم الأمر
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

## واجهة سطر الأوامر والغلاف التفاعلي

يتضمن Scrapling v0.3 واجهة سطر أوامر قوية:

[![asciicast](https://asciinema.org/a/736339.svg)](https://asciinema.org/a/736339)

تشغيل غلاف استخراج الويب التفاعلي
```bash
scrapling shell
```
استخراج الصفحات إلى ملف مباشرة دون برمجة (يستخرج المحتوى داخل وسم `body` افتراضياً). إذا انتهى ملف الإخراج بـ `.txt`، فسيتم استخراج محتوى النص للهدف. إذا انتهى بـ `.md`، فسيكون تمثيل Markdown لمحتوى HTML؛ إذا انتهى بـ `.html`، فسيكون محتوى HTML نفسه.
```bash
scrapling extract get 'https://example.com' content.md
scrapling extract get 'https://example.com' content.txt --css-selector '#fromSkipToProducts' --impersonate 'chrome'  # جميع العناصر المطابقة لمحدد CSS '#fromSkipToProducts'
scrapling extract fetch 'https://example.com' content.md --css-selector '#fromSkipToProducts' --no-headless
scrapling extract stealthy-fetch 'https://nopecha.com/demo/cloudflare' captchas.html --css-selector '#padded_content a' --solve-cloudflare
```

> [!NOTE]
> هناك العديد من الميزات الإضافية، لكننا نريد إبقاء هذه الصفحة موجزة، مثل خادم MCP وغلاف استخراج الويب التفاعلي. تحقق من الوثائق الكاملة [هنا](https://scrapling.readthedocs.io/en/latest/)

## معايير الأداء

Scrapling ليس قوياً فقط - إنه أيضاً سريع بشكل مذهل، والتحديثات منذ الإصدار 0.3 قدمت تحسينات أداء استثنائية عبر جميع العمليات. تقارن المعايير التالية محلل Scrapling مع المكتبات الشائعة الأخرى.

### اختبار سرعة استخراج النص (5000 عنصر متداخل)

| # |      المكتبة      | الوقت (ms) | vs Scrapling | 
|---|:-----------------:|:----------:|:------------:|
| 1 |     Scrapling     |    1.99    |     1.0x     |
| 2 |   Parsel/Scrapy   |    2.01    |    1.01x     |
| 3 |     Raw Lxml      |    2.5     |    1.256x    |
| 4 |      PyQuery      |   22.93    |    ~11.5x    |
| 5 |    Selectolax     |   80.57    |    ~40.5x    |
| 6 |   BS4 with Lxml   |  1541.37   |   ~774.6x    |
| 7 |  MechanicalSoup   |  1547.35   |   ~777.6x    |
| 8 | BS4 with html5lib |  3410.58   |   ~1713.9x   |


### أداء تشابه العناصر والبحث النصي

قدرات العثور على العناصر التكيفية لـ Scrapling تتفوق بشكل كبير على البدائل:

| المكتبة     | الوقت (ms) | vs Scrapling |
|-------------|:----------:|:------------:|
| Scrapling   |    2.46    |     1.0x     |
| AutoScraper |    13.3    |    5.407x    |


> تمثل جميع المعايير متوسطات أكثر من 100 تشغيل. انظر [benchmarks.py](https://github.com/D4Vinci/Scrapling/blob/main/benchmarks.py) للمنهجية.

## التثبيت

يتطلب Scrapling Python 3.10 أو أعلى:

```bash
pip install scrapling
```

بدءاً من v0.3.2، يتضمن هذا التثبيت فقط محرك المحلل وتبعياته، بدون أي جوالب أو تبعيات سطر أوامر.

### التبعيات الاختيارية

1. إذا كنت ستستخدم أياً من الميزات الإضافية أدناه، أو الجوالب، أو فئاتها، فستحتاج إلى تثبيت تبعيات الجوالب وتبعيات المتصفح الخاصة بها على النحو التالي:
    ```bash
    pip install "scrapling[fetchers]"
    
    scrapling install
    ```

    يقوم هذا بتنزيل جميع المتصفحات، إلى جانب تبعيات النظام وتبعيات معالجة البصمات الخاصة بها.

2. ميزات إضافية:
   - تثبيت ميزة خادم MCP:
       ```bash
       pip install "scrapling[ai]"
       ```
   - تثبيت ميزات الغلاف (غلاف استخراج الويب وأمر `extract`):
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
- Parsel (ترخيص BSD) - يستخدم للوحدة الفرعية [translator](https://github.com/D4Vinci/Scrapling/blob/main/scrapling/core/translator.py)

## الشكر والمراجع

- العمل الرائع لـ [Daijro](https://github.com/daijro) على [BrowserForge](https://github.com/daijro/browserforge) و[Camoufox](https://github.com/daijro/camoufox)
- العمل الرائع لـ [Vinyzu](https://github.com/Vinyzu) على [Botright](https://github.com/Vinyzu/Botright) و[PatchRight](https://github.com/Kaliiiiiiiiii-Vinyzu/patchright)
- [brotector](https://github.com/kaliiiiiiiiii/brotector) لتقنيات تجاوز اكتشاف المتصفح
- [fakebrowser](https://github.com/kkoooqq/fakebrowser) و[BotBrowser](https://github.com/botswin/BotBrowser) لأبحاث البصمات

---
<div align="center"><small>مصمم ومصنوع بـ ❤️ بواسطة كريم شعير.</small></div><br>