<!-- mcp-name: io.github.D4Vinci/Scrapling -->

<h1 align="center">
    <a href="https://scrapling.readthedocs.io/ar/latest/">
        <picture>
          <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/docs/assets/cover_dark.svg?sanitize=true">
          <img alt="Scrapling Poster" src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/docs/assets/cover_light.svg?sanitize=true">
        </picture>
    </a>
    <br>
    <small>اجمع بيانات الويب الحديث بسهولة</small>
</h1>

<p align="center">
    <a href="https://github.com/D4Vinci/Scrapling/actions/workflows/tests.yml" alt="Tests">
        <img alt="Tests" src="https://github.com/D4Vinci/Scrapling/actions/workflows/tests.yml/badge.svg"></a>
    <a href="https://badge.fury.io/py/Scrapling" alt="PyPI version">
        <img alt="PyPI version" src="https://badge.fury.io/py/Scrapling.svg"></a>
    <a href="https://hub.docker.com/r/pyd4vinci/scrapling" target="_blank">
        <img alt="Docker Pulls" src="https://img.shields.io/docker/pulls/pyd4vinci/scrapling?labelColor=%20%23FDB062&logo=Docker&labelColor=%20%23528bff"></a>
    <a href="https://clickpy.clickhouse.com/dashboard/scrapling" rel="nofollow"><img src="https://img.shields.io/pypi/dm/scrapling" alt="PyPI package downloads"></a>
    <a href="https://scrapling.readthedocs.io/ar/latest/ai/agent-skill.html" alt="AI Agent Skill">
        <img alt="Static Badge" src="https://img.shields.io/badge/Skill-black?style=flat&label=Agent&link=https%3A%2F%2Fscrapling.readthedocs.io%2Far%2Flatest%2Fai%2Fagent-skill.html"></a>
    <a href="https://clawhub.ai/D4Vinci/scrapling-official" alt="OpenClaw Skill">
        <img alt="OpenClaw Skill" src="https://img.shields.io/badge/Clawhub-darkred?style=flat&label=OpenClaw&link=https%3A%2F%2Fclawhub.ai%2FD4Vinci%2Fscrapling-official"></a>
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
    <a href="https://scrapling.readthedocs.io/ar/latest/parsing/selection.html"><strong>اختيار العناصر</strong></a>
    &middot;
    <a href="https://scrapling.readthedocs.io/ar/latest/fetching/choosing.html"><strong>اختيار Fetcher</strong></a>
    &middot;
    <a href="https://scrapling.readthedocs.io/ar/latest/spiders/architecture.html"><strong>Spiders</strong></a>
    &middot;
    <a href="https://scrapling.readthedocs.io/ar/latest/spiders/proxy-blocking.html"><strong>تبديل البروكسي</strong></a>
    &middot;
    <a href="https://scrapling.readthedocs.io/ar/latest/cli/overview.html"><strong>واجهة سطر الأوامر</strong></a>
    &middot;
    <a href="https://scrapling.readthedocs.io/ar/latest/ai/mcp-server.html"><strong>خادم MCP</strong></a>
</p>

Scrapling إطار عمل بلغة Python لجمع بيانات الويب. يجمع طلبات HTTP السريعة، والمتصفحات الخفية، وتحليل الصفحات، والزحف المتزامن في مكتبة واحدة.

اجمع بيانات الصفحات الثابتة، وشغّل JavaScript، وتفاعل مع المواقع، واستخرج البيانات من طلبات API التي تعمل خلفها. أنشئ برامج زحف بجلسات قابلة لإعادة الاستخدام، وتبديل البروكسي، وإعادة المحاولة تلقائيًا، والإيقاف والاستئناف، وتصدير البيانات بأدوات مدمجة.

استخدمه من Python أو الطرفية أو وكيل الذكاء الاصطناعي عبر خادم MCP وAgent Skill. يغطي Scrapling خطوات جمع البيانات كاملة، من استخراج بضعة حقول إلى جمع موقع كامل في ملفات Markdown نظيفة.

## ما الذي يمكنك فعله باستخدام Scrapling؟

- **[الجلب والتفاعل](https://scrapling.readthedocs.io/ar/latest/fetching/choosing.html)**: طلبات HTTP سريعة، ومتصفحات خفية، وتشغيل JavaScript، والتعامل مع Cloudflare Turnstile وInterstitial، وجلسات مستمرة، وحفظ ردود طلبات API في الخلفية.
- **[التحليل والاستخراج](https://scrapling.readthedocs.io/ar/latest/parsing/selection.html)**: البحث باستخدام CSS وXPath والنص والتعبيرات المنتظمة، وتتبع العناصر عند تغير الصفحة، والعثور على العناصر المتشابهة، وإخراج Markdown نظيف.
- **[الزحف والتصدير](https://scrapling.readthedocs.io/ar/latest/spiders/getting-started.html)**: برامج Spider متزامنة، وتبديل البروكسي، وإعادة المحاولة، وAutoThrottle، والإيقاف والاستئناف، وبث النتائج، وقوالب جاهزة، وتصدير JSON وJSONL وCSV وXML.
- **[جمع البيانات بالذكاء الاصطناعي أو من الطرفية](https://scrapling.readthedocs.io/ar/latest/ai/mcp-server.html)**: خادم MCP لوكلاء الذكاء الاصطناعي لتصفح المواقع واستخراج البيانات، وAgent Skill، وأوامر CLI، وواجهة تفاعلية.

ابدأ بصفحة واحدة:

```python
from scrapling.fetchers import Fetcher

page = Fetcher.get('https://quotes.toscrape.com/')
quotes = page.css('.quote .text::text').getall()
print(quotes)
```

أو اجمع بيانات أكثر باستخدام Spider:

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

يطبع هذا المثال `10` ويحفظ الاقتباسات وأسماء المؤلفين في `quotes.json`.

<p align="center">
    <a href="https://dataimpulse.com/?utm_source=scrapling&utm_medium=banner&utm_campaign=scrapling" target="_blank" style="display:flex; justify-content:center; padding:4px 0;">
        <img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/DataImpulse.png" alt="At DataImpulse, we specialize in developing custom proxy services for your business. Make requests from anywhere, collect data, and enjoy fast connections with our premium proxies." style="max-height:60px;">
    </a>
</p>

# الرعاة البلاتينيون
<table>
  <tr>
    <td width="200">
      <a href="https://go.nodemaven.com/scraplingoctober" target="_blank" title="Proxies with the Highest IP Scores">
        <img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/NodeMaven.jpg" width="240" height="100">
      </a>
    </td>
    <td>
    <a href="https://go.nodemaven.com/scraplingoctober" target="_blank">NodeMaven</a> - أكفأ مزود بروكسيات لجمع بيانات الويب والأتمتة، مع أعلى جودة لعناوين IP في السوق. استخدم الكود SCRAPLING35 للحصول على خصم 35%.
    </td>
  </tr>
  <tr>
    <td width="200">
      <a href="https://hypersolutions.co/?utm_source=github&utm_medium=readme&utm_campaign=scrapling" target="_blank" title="Bot Protection Bypass API for Akamai, DataDome, Incapsula & Kasada">
        <img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/HyperSolutions.png">
      </a>
    </td>
    <td> Scrapling يتعامل مع Cloudflare Turnstile. لتجاوز أنظمة الحماية التي تستخدمها المؤسسات، توفر <a href="https://hypersolutions.co?utm_source=github&utm_medium=readme&utm_campaign=scrapling">
        <b>Hyper Solutions</b>
      </a> واجهات API تولّد رموز antibot صالحة لـ <b>Akamai</b>، <b>DataDome</b>، <b>Kasada</b> و <b>Incapsula</b>. طلبات API بسيطة دون الحاجة إلى أتمتة المتصفح. </td>
  </tr>
  <tr>
    <td width="200">
      <a href="https://evomi.com?utm_source=github&utm_medium=banner&utm_campaign=d4vinci-scrapling" target="_blank" title="Evomi is your Swiss Quality Proxy Provider, starting at $0.49/GB">
        <img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/evomi.png">
      </a>
    </td>
    <td>
      <a href="https://evomi.com?utm_source=github&utm_medium=banner&utm_campaign=d4vinci-scrapling">
        <b>Evomi</b>
      </a>: بروكسيات سكنية تبدأ من 0.49$/جيجابايت. متصفح لجمع البيانات يستخدم Chromium مع تمويه كامل لبصمته، وعناوين IP سكنية، وحل تلقائي لـ CAPTCHA، وتجاوز أنظمة كشف البوتات. </br>
      <b>واجهة Scraper API لنتائج بدون عناء. يدعم الربط مع MCP و N8N.</b>
    </td>
  </tr>
  <tr>
    <td width="200">
      <a href="https://substack.thewebscraping.club/p/scrapling-hands-on-guide?utm_source=github&utm_medium=repo&utm_campaign=scrapling" target="_blank" title="The #1 newsletter dedicated to Web Scraping">
        <img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/TWSC.png">
      </a>
    </td>
    <td>
    اقرأ مراجعة كاملة عن <a href="https://substack.thewebscraping.club/p/scrapling-hands-on-guide?utm_source=github&utm_medium=repo&utm_campaign=scrapling" target="_blank">Scrapling على The Web Scraping Club</a> (نوفمبر 2025)، النشرة الإخبارية الأولى المخصصة لجمع بيانات الويب.
    </td>
  </tr>
  <tr>
    <td width="200">
      <a href="https://www.swiftproxy.net/?ref=D4Vinci" target="_blank" title="Scalable Solutions for Web Data Access">
        <img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/SwiftProxy.png">
      </a>
    </td>
    <td>
    يوفر <a href="https://www.swiftproxy.net/?ref=D4Vinci" target="_blank">Swiftproxy</a> بروكسيات سكنية تناسب زيادة حجم العمل، مع أكثر من 80 مليون عنوان IP في أكثر من 195 دولة. يقدم اتصالات سريعة وموثوقة، وتبديلًا تلقائيًا للبروكسي، وقدرة عالية على تجنب الحظر. تجربة مجانية متاحة.
    </td>
  </tr>
  <tr>
    <td width="200">
      <a href="https://byteful.com/?utm_source=github&utm_medium=github-sponsor&utm_campaign=scrapling_github_sponsor" target="_blank" title="Ethically sourced residential proxy infrastructure powering web scraping and AI agents">
        <img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/byteful.png">
      </a>
    </td>
    <td>
    توفر <a href="https://byteful.com/?utm_source=github&utm_medium=github-sponsor&utm_campaign=scrapling_github_sponsor" target="_blank">Byteful</a> بروكسيات سكنية ومحمولة وبروكسيات ISP ومراكز بيانات من مصادر أخلاقية، إلى جانب أدوات لاستخراج بيانات الويب وأتمتة الذكاء الاصطناعي. استخدم الكود SCRAPLING10 للحصول على خصم 10% على البروكسيات السكنية.
    </td>
  </tr>
  <tr>
    <td width="200">
      <a href="https://proxylane.dev/?utm_source=scrapling&utm_medium=partnership&utm_campaign=scrapling_platinum_202609&utm_content=github_readme" target="_blank" title="28M+ clean residential IPs for browser automation. No Blocks. No CAPTCHAs. Pay-as-you-Go.">
        <img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/proxylane.png">
      </a>
    </td>
    <td>
    <a href="https://proxylane.dev/?utm_source=scrapling&utm_medium=partnership&utm_campaign=scrapling_platinum_202609&utm_content=github_readme" target="_blank">ProxyLane</a>: قلّل الحظر واختبارات CAPTCHA بنسبة 90%. 28 مليون عنوان IP سكني عالي الجودة لاستخراج بيانات الويب بكثافة. 195 دولة. استهداف حسب المدينة/ISP/الرمز البريدي (ZIP). جلسات بعنوان IP ثابت أو متغير. رصيد بيانات لا تنتهي صلاحيته يبدأ من $2/GB. الكود <strong>SCRAPEANDTAKE</strong>: <em>خصم 25%</em>.
    </td>
  </tr>
  <tr>
    <td width="200">
      <a href="https://www.lundproxy.com/unlimited-residential-bandwidth.html?utm_source=github&utm_medium=sponsorship&utm_campaign=scrapling&utm_content=banner" target="_blank" title="Unlimited residential traffic, sized only by bandwidth.">
        <img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/lundproxy.png">
      </a>
    </td>
    <td>
    <a href="https://www.lundproxy.com?utm_source=github&utm_medium=sponsorship&utm_campaign=scrapling&utm_content=text" target="_blank">LundProxy</a>: توقّف عن الدفع لكل GB. نقل بيانات بلا حد عبر بروكسيات سكنية، وأكثر من 100 مليون عنوان IP في أكثر من 190 دولة. ادفع حسب سرعة الاتصال (bandwidth). اطلب تجربة مجانية للبروكسيات السكنية بسرعة 50 Mbps.
    </td>
  </tr>
  <tr>
    <td width="200">
      <a href="https://dataimpulse.com/?utm_source=website&utm_medium=github_readme&utm_campaign=scrapling_platinum" target="_blank" title="Buy Pay-as-you-go proxies from $1/GB">
        <img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/DataImpulse_Platinum.png">
      </a>
    </td>
    <td>
    $1/GB لدى <a href="https://dataimpulse.com/?utm_source=website&utm_medium=github_readme&utm_campaign=scrapling_platinum" target="_blank">DataImpulse</a>. بروكسيات من شبكة الشركة نفسها، وبمصادر أخلاقية. أكثر من 90 مليون عنوان IP في أكثر من 195 دولة. بروكسيات سكنية ومراكز بيانات ومحمولة. الدفع حسب الاستخدام = بدون اشتراك. رصيد البيانات لا تنتهي صلاحيته.
    </td>
  </tr>
</table>

<i><sub>هل تريد عرض إعلانك هنا؟ اضغط [هنا](https://github.com/sponsors/D4Vinci/sponsorships?tier_id=586646)</sub></i>
# الرعاة

<!-- sponsors -->

<a href="https://cloro.dev/?utm_source=referral&utm_medium=scrapling" target="_blank" title="The search API for the AI era"><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/cloro.jpg"></a>

<br/>

<a href="https://serpapi.com/?utm_source=scrapling" target="_blank" title="Scrape Google and other search engines with SerpApi"><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/SerpApi.png"></a>
<a href="https://visit.decodo.com/Dy6W0b" target="_blank" title="Try the Most Efficient Residential Proxies for Free"><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/decodo.png"></a>
<a href="https://proxyempire.io/?ref=scrapling&utm_source=github&utm_medium=paid_referral&utm_campaign=open_source_sponsorship&utm_content=scrapling" target="_blank" title="Collect The Data Your Project Needs with the Best Residential Proxies"><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/ProxyEmpire.png"></a>
<a href="https://www.webshare.io/?referral_code=48r2m2cd5uz1" target="_blank" title="The Most Reliable Proxy with Unparalleled Performance"><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/webshare.png"></a>
<a href="https://proxiware.com/?ref=scrapling" target="_blank" title="Collect Any Data. At Any Scale."><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/proxiware.png"></a>


<!-- /sponsors -->

<i><sub>هل تريد عرض إعلانك هنا؟ اضغط [هنا](https://github.com/sponsors/D4Vinci) واختر الخطة التي تناسبك!</sub></i>

---

## الميزات الأساسية

### Spiders: إطار عمل كامل للزحف
- 🕷️ **واجهة Spider تشبه Scrapy**: عرّف برامج Spider باستخدام `start_urls`، ودوال `parse` غير المتزامنة، وكائنات `Request` و`Response`.
- ⚡ **زحف متزامن**: اضبط عدد الطلبات المتزامنة، وحدود كل نطاق، ومدة الانتظار بين التنزيلات.
- 🔄 **دعم عدة جلسات**: واجهة واحدة لطلبات HTTP والمتصفحات الخفية بلا واجهة ضمن Spider واحد. وجّه الطلبات إلى جلسات مختلفة باستخدام المعرّف.
- 💾 **الإيقاف والاستئناف**: احفظ الطلبات المعلقة والروابط التي زرتها باستخدام `crawldir`. اضغط Ctrl+C للإيقاف الآمن، ثم أعد التشغيل مع المجلد نفسه.
- 📡 **بث النتائج**: استقبل العناصر فور جمعها عبر `async for item in spider.stream()`، مع إحصاءات مباشرة. يناسب الواجهات وخطوات معالجة البيانات وعمليات الزحف الطويلة.
- 🛡️ **كشف الطلبات المحظورة**: كشف الطلبات المحظورة وإعادة محاولتها تلقائيًا، مع إمكانية تخصيص السلوك.
- 🚦 **AutoThrottle**: لا تحتاج إلى تخمين مدة الانتظار. يضبط Spider المدة لكل نطاق حسب سرعة رد الموقع، ثم يضاعفها، أو ينتظر المدة التي يطلبها `Retry-After`، عندما يبدأ الموقع في الحظر أو تقييد معدل الطلبات. ويعود إلى السرعة الأعلى عند توقف ذلك.
- 🤖 **الالتزام بملف robots.txt**: خيار `robots_txt_obey` يحترم تعليمات `Disallow` و`Crawl-delay` و`Request-rate`، مع تخزين مؤقت لكل نطاق.
- 🧪 **وضع التطوير**: احفظ الردود على القرص في أول تشغيل، ثم أعد استخدامها في التشغيلات التالية. عدّل دالة `parse()` دون إرسال طلبات جديدة إلى الخوادم.
- 🧩 **قوالب Spider جاهزة**: استخدم `CrawlSpider` لتتبع الروابط وفق قواعد، و`SitemapSpider` للزحف من خرائط الموقع أو robots.txt، و`XMLFeedSpider` و`CSVFeedSpider` لقراءة خلاصات XML وRSS وCSV، و`ShopifySpider` لجمع منتجات متاجر Shopify العامة، بعنصر مستقل لكل نوع من المنتج (variant).
- 🔗 **استخراج الروابط**: أداة `LinkExtractor` مستقلة تدعم أنماط السماح والمنع، وتصفية النطاقات والامتدادات، وحصر البحث باستخدام CSS وXPath، وتوحيد صيغة الروابط. استخدمها داخل القوالب أو وحدها.
- 📦 **تصدير مدمج**: صدّر النتائج عبر hooks وخط معالجة خاص بك، أو استخدم أدوات JSON وJSONL وCSV وXML المدمجة: `result.items.to_json()` و`to_jsonl()` و`to_csv()` و`to_xml()`.

### جلب متقدم للمواقع مع دعم الجلسات
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

### تحليل الصفحات واستخراج البيانات
- 🔄 **تتبع ذكي للعناصر**: اعثر على العناصر بعد تغير الموقع باستخدام خوارزميات مقارنة التشابه.
- 🎯 **اختيار مرن للعناصر**: محددات CSS وXPath، والبحث بالشروط أو بالنص أو بالتعبيرات المنتظمة، والمزيد.
- 🔍 **العثور على العناصر المتشابهة**: ابحث تلقائيًا عن عناصر تشبه العناصر التي وجدتها.

### ميزات الذكاء الاصطناعي
- 🤖 **خادم MCP**: يتيح لوكلاء ومساعدي الذكاء الاصطناعي، مثل Claude وCursor، جمع البيانات عبر Scrapling باستخدام طلبات HTTP، والتفاعل مع المتصفح، ولقطات الشاشة، وحالة تسجيل دخول محفوظة، وردود API في الخلفية. يستخدم متصفحنا الخفي مع أدوات تساعد النماذج المناسبة على تجاوز CAPTCHA أثناء العمل، إلى جانب أداة حل Cloudflare. ويقلل المحتوى المرسل إلى النموذج، ويحظر الإعلانات، ويحميه من حقن التعليمات Prompt Injection. يدعم أيضًا المتصفحات البعيدة عبر CDP والاتصال عبر HTTP مع خيارات المصادقة. ([فيديو توضيحي](https://www.youtube.com/watch?v=qyFk3ZNwOxE))
- 🧠 **Agent Skill**: [مهارة جاهزة للتثبيت](https://scrapling.readthedocs.io/ar/latest/ai/agent-skill.html) تعرّف وكلاء البرمجة على المكتبة كاملة، ليكتبوا كودًا يطابق واجهتها الحالية بدلًا من التخمين.
- 📚 **Markdown جاهز لأنظمة RAG**: حوّل أي صفحة إلى Markdown نظيف ومنقّى وجاهز لنماذج اللغة بسطر واحد (`page.markdown()`)، أو اجمع موقعًا كاملًا في مجموعة ملفات Markdown باستخدام قالب `ContentSpider`، دون الحاجة إلى نموذج لغة أثناء العملية. ([التوثيق](https://scrapling.readthedocs.io/ar/latest/ai/building-rag-systems.html))

### أداء عالٍ وتصميم مجرّب
- 🚀 **سرعة عالية**: أداء محسّن يتفوق على معظم مكتبات جمع بيانات الويب في Python.
- 🔋 **استهلاك قليل للذاكرة**: هياكل بيانات محسّنة وتحميل عند الحاجة لتقليل استخدام الذاكرة.
- ⚡ **تحويل سريع إلى JSON**: أسرع بعشر مرات من المكتبة القياسية.
- 🏗️ **مجرّب عمليًا**: تغطي الاختبارات 92% من Scrapling، وتوجد تلميحات أنواع للكود كله. كما استخدمه مئات العاملين في جمع بيانات الويب يوميًا خلال العام الماضي.

### تجربة مناسبة للمطورين وجمع البيانات
- 🎯 **واجهة تفاعلية لجمع البيانات**: واجهة IPython اختيارية مدمجة مع Scrapling، واختصارات وأدوات تسرّع كتابة البرامج، مثل تحويل طلبات curl إلى طلبات Scrapling وعرض نتائج الطلبات في المتصفح.
- 🚀 **استخدام مباشر من الطرفية**: يمكنك جمع بيانات رابط دون كتابة أي كود.
- 🛠️ **طرق كثيرة للتنقل**: تنقل في شجرة DOM بين الآباء والأشقاء والأبناء.
- 🧬 **معالجة نصوص محسّنة**: تعبيرات منتظمة وطرق لتنظيف النص وعمليات نصية محسّنة مدمجة.
- 📝 **إنشاء محددات تلقائيًا**: أنشئ محددات CSS وXPath موثوقة لأي عنصر.
- 🔌 **واجهة مألوفة**: تشبه Scrapy وBeautifulSoup، وتستخدم pseudo-elements نفسها الموجودة في Scrapy وParsel.
- 🤝 **تكامل مباشر مع Scrapy**: إذا كنت تستخدم Scrapy، أضف decorator باسم `scrapling_response` إلى أي callback لتحليل الردود التي تجلبها بالفعل بمحلّل Scrapling، دون إعادة كتابة البرنامج.
- 📘 **تلميحات أنواع كاملة**: دعم جيد لمحرر الكود والإكمال التلقائي. يُفحص الكود كله تلقائيًا باستخدام **PyRight** و**MyPy** مع كل تغيير.
- 🔋 **صورة Docker جاهزة**: تُبنى صورة Docker تحتوي كل المتصفحات وتُنشر تلقائيًا مع كل إصدار.

## البدء

إليك أمثلة سريعة على استخدام Scrapling.

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
page = StealthyFetcher.fetch('https://nopecha.com/demo/cloudflare', solve_cloudflare=True)
data = page.css('#padded_content a').getall()
```
أتمتة المتصفح الكاملة
```python
from scrapling.fetchers import StealthyFetcher, StealthySession

with StealthySession(headless=True, disable_resources=False, network_idle=True) as session:  # أبقِ المتصفح مفتوحاً حتى تنتهي
    page = session.fetch('https://quotes.toscrape.com/', load_dom=False)
    data = page.xpath('//span[@class="text"]/text()').getall()  # محدد XPath إذا كنت تفضله

# أو استخدم نمط الطلب لمرة واحدة، يفتح المتصفح لهذا الطلب، ثم يغلقه بعد الانتهاء
page = StealthyFetcher.fetch('https://quotes.toscrape.com/')
data = page.css('.quote .text::text').getall()
```

### Spiders
أنشئ برامج Spider ترسل عدة طلبات في الوقت نفسه، وتستخدم أنواع جلسات مختلفة، وتدعم الإيقاف والاستئناف:
```python
from scrapling.spiders import Spider, Response

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
لحفظ تقدم الزحف وإكماله لاحقًا، شغّل Spider هكذا:
```python
QuotesSpider(crawldir="./crawl_data").start()
```
عند استخدام `crawldir`، اضغط Ctrl+C لحفظ الطلبات المعلقة والروابط التي زرتها. أعد التشغيل مع `crawldir` نفسه لإكمال الزحف. احفظ البيانات التي جمعتها بشكل منفصل.

أو استخدم قالبًا جاهزًا بدلًا من كتابة كود الزحف بنفسك، مثل هذا القالب لجمع كل منتجات متجر Shopify:
```python
from scrapling.spiders import ShopifySpider

class MyStore(ShopifySpider):
    target_website = "example.com"

result = MyStore().start()  # كل منتج في المتجر، مع عنصر لكل variant
```
يجمع القالب المنتجات المتاحة عبر واجهات API العامة للمجموعات، ويحفظ نتيجة منفصلة لكل نوع من المنتج (variant).

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
quotes = page.find_by_text('Albert Einstein', first_match=False)

# التنقل المتقدم
quote_text = page.css('.quote')[0].css('.text::text').get()
quote_texts = page.css('.quote').css('.text::text').getall()  # محددات متسلسلة
first_quote = page.css('.quote')[0]
author = first_quote.css('.author::text').get()
next_quote = first_quote.next
parent_container = first_quote.parent

# علاقات العناصر والتشابه
similar_elements = first_quote.find_similar()
below_elements = first_quote.below_elements
```
إذا كان لديك محتوى HTML بالفعل، يمكنك تحليله مباشرة:
```python
from scrapling.parser import Selector

page = Selector("<html>...</html>")
```
يمكنك استخدام طرق اختيار العناصر نفسها.

### إدارة الجلسات باستخدام Async
```python
import asyncio
from scrapling.fetchers import FetcherSession, AsyncStealthySession

async def main():
    async with FetcherSession(http3=True) as http_session:  # تتكيف `FetcherSession` مع السياق وتعمل بالنمطين المتزامن وغير المتزامن
        page1 = await http_session.get('https://quotes.toscrape.com/')
        page2 = await http_session.get('https://quotes.toscrape.com/page/2/', impersonate='chrome')
        print(len(page1.css('.quote')), len(page2.css('.quote')))

    async with AsyncStealthySession(max_pages=2) as browser_session:
        urls = ['https://quotes.toscrape.com/js/', 'https://quotes.toscrape.com/js/page/2/']
        pages = await asyncio.gather(*(browser_session.fetch(url, wait_selector='.quote') for url in urls))
        print([len(page.css('.quote')) for page in pages])

asyncio.run(main())
```

## سطر الأوامر وShell التفاعلي

يمكنك استخدام Scrapling من سطر الأوامر:

[![asciicast](https://asciinema.org/a/736339.svg)](https://asciinema.org/a/736339)

لتشغيل Shell التفاعلي لجمع البيانات:
```bash
pip install "scrapling[shell]"
scrapling shell
```
احفظ محتوى الصفحات في ملف مباشرة دون كتابة كود. استخدم `--css-selector` لاختيار المحتوى، أو `--ai-targeted` لاختيار محتوى `body` وإزالة الأجزاء غير المطلوبة. استخدم `.txt` للنص، أو `.md` لصيغة Markdown، أو `.html` لصيغة HTML.
```bash
scrapling extract get 'https://quotes.toscrape.com/' quotes.md
scrapling extract get 'https://quotes.toscrape.com/' quotes.txt --css-selector '.quote' --impersonate 'chrome'
scrapling extract fetch 'https://quotes.toscrape.com/js/' quotes.md --css-selector '.quote' --wait-selector '.quote' --no-headless
scrapling extract fetch 'https://nopecha.com/demo/cloudflare' captchas.html --css-selector '#padded_content a' --solve-cloudflare
```

> [!NOTE]
> هذه أمثلة مختصرة. للمزيد من الميزات والتفاصيل، بما فيها خادم MCP وShell التفاعلي، اقرأ التوثيق الكامل [هنا](https://scrapling.readthedocs.io/ar/latest/)

## اختبارات الأداء

Scrapling سريع أيضًا. تقارن الاختبارات التالية محلّل Scrapling بأحدث إصدارات مكتبات شائعة أخرى.

### اختبار سرعة استخراج النص (5000 عنصر متداخل)

| # |      المكتبة      | الوقت (ms) | vs Scrapling |
|---|:-----------------:|:----------:|:------------:|
| 1 |     Scrapling     |    1.99    |     1.0x     |
| 2 |   Parsel/Scrapy   |    2.06    |     1.035    |
| 3 |     Raw Lxml      |    2.56    |    1.286     |
| 4 |      PyQuery      |   23.98    |     ~12x     |
| 5 |    Selectolax     |   197.02   |     ~99x     |
| 6 |  MechanicalSoup   |  1545.15   |   ~776.5x    |
| 7 |   BS4 with Lxml   |  1562.1   |   ~785.0x    |
| 8 | BS4 with html5lib |  3412.73   |   ~1714.9x   |


### أداء تشابه العناصر والبحث النصي

يعثر Scrapling على العناصر بعد تغير الصفحة بسرعة أكبر من البدائل:

| المكتبة     | الوقت (ms) | vs Scrapling |
|-------------|:----------:|:------------:|
| Scrapling   |    2.3    |     1.0x     |
| AutoScraper |   12.58    |    5.47x    |


> كل نتيجة هي متوسط أكثر من 100 تشغيل. لمعرفة طريقة الاختبار، راجع [benchmarks.py](https://github.com/D4Vinci/Scrapling/blob/main/benchmarks.py).

## التثبيت

يتطلب Scrapling إصدار Python 3.10 أو أحدث:

```bash
pip install scrapling
```

> [!IMPORTANT]
> يثبّت هذا الأمر محلّل الصفحات ومتطلباته فقط، دون أدوات الجلب أو متطلبات سطر الأوامر. إذا اكتفيت بهذا التثبيت، سيظهر الخطأ `ModuleNotFoundError` عند استيراد أي شيء من `scrapling.fetchers` أو `scrapling.spiders`، كما في الأمثلة السابقة. لاستخدام أدوات الجلب أو Spiders، ثبّت متطلبات أدوات الجلب أولًا كما يلي.

### المتطلبات الاختيارية

1. لاستخدام أدوات الجلب أو فئاتها أو الميزات الإضافية التالية، ثبّت متطلبات أدوات الجلب والمتصفحات كما يلي:
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

2. ميزات إضافية:
   - تثبيت خادم MCP:
       ```bash
       pip install "scrapling[ai]"
       ```
   - تثبيت متطلبات [بناء أنظمة RAG](https://scrapling.readthedocs.io/ar/latest/ai/building-rag-systems.html):
       ```bash
       pip install "scrapling[rag]"
       ```
   - تثبيت Shell التفاعلي وأمر `extract`:
       ```bash
       pip install "scrapling[shell]"
       ```
   - تثبيت كل شيء:
       ```bash
       pip install "scrapling[all]"
       ```
   شغّل `scrapling install` عند استخدام أدوات جلب المتصفح. طلبات HTTP لا تحتاج إلى تثبيت متصفح.

### Docker
يمكنك تنزيل صورة Docker تحتوي كل الإضافات والمتصفحات من DockerHub:
```bash
docker pull pyd4vinci/scrapling
```
أو تنزيلها من سجل GitHub:
```bash
docker pull ghcr.io/d4vinci/scrapling:latest
```
تُبنى هذه الصورة من الفرع الرئيسي للمستودع وتُنشر تلقائيًا باستخدام GitHub Actions.

## المساهمة

نرحب بالمساهمات! يرجى قراءة [إرشادات المساهمة](https://github.com/D4Vinci/Scrapling/blob/main/CONTRIBUTING.md) قبل البدء.

## إخلاء المسؤولية

> [!CAUTION]
> هذه المكتبة للتعليم والبحث فقط. باستخدامها، توافق على الالتزام بقوانين جمع البيانات والخصوصية المحلية والدولية. المؤلفون والمساهمون غير مسؤولين عن أي إساءة استخدام لهذا البرنامج. احترم دائماً شروط خدمة المواقع وملفات robots.txt.

## 🎓 الاستشهادات
إذا استخدمت المكتبة في بحث، أضف المرجع التالي:
```text
  @misc{scrapling,
    author = {Karim Shoair},
    title = {Scrapling},
    year = {2024},
    url = {https://github.com/D4Vinci/Scrapling},
    note = {A Python Web Scraping framework for everything from a single request to a full-scale crawl!}
  }
```

## الترخيص

هذا العمل مرخص بموجب ترخيص BSD-3-Clause.

## الشكر والتقدير

يتضمن هذا المشروع كوداً معدلاً من:
- Parsel (ترخيص BSD) - يُستخدم للوحدة الفرعية [translator](https://github.com/D4Vinci/Scrapling/blob/main/scrapling/core/translator.py)

---
<div align="center"><small>مصمم ومصنوع بـ ❤️ بواسطة كريم شعير.</small></div><br>
