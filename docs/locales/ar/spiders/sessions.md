---
title: "استخدام جلسات HTTP والمتصفح في زاحف واحد"
description: "أعدّ جلسات بأسماء ووجّه طلبات العنكبوت إلى أدوات جلب HTTP أو المتصفح. أعد استخدام ملفات تعريف الارتباط وشغّل الجلسات عند الحاجة وافحص سجل ردود API."
---

# جلسات العناكب {#spiders-sessions}

!!! success "قبل البدء"

    1. اقرأ صفحة [البداية](getting-started.md) وتعرّف على إنشاء عنكبوت بسيط وتشغيله.
    2. تعرّف على [أساسيات أدوات الجلب](../fetching/choosing.md) والفرق بين جلسات HTTP وجلسات Stealthy.

يمكن للعنكبوت استخدام عدة جلسات جلب في الوقت نفسه. مثلًا، جلسة HTTP سريعة للصفحات البسيطة، وجلسة متصفح Stealth للصفحات المحمية. تشرح هذه الصفحة كيفية إعداد الجلسات واستخدامها.

## ما هي الجلسات؟ {#what-are-sessions}

الجلسة هي كائن جلب بإعدادات جاهزة يظل يعمل طوال عملية الزحف. يعيد العنكبوت استخدام الجلسات بدلًا من إنشاء اتصال أو متصفح جديد لكل طلب، مما يزيد السرعة ويقلل استهلاك الموارد.

ينشئ كل عنكبوت جلسة [FetcherSession](../fetching/static.md) واحدة افتراضيًا. يمكنك إضافة جلسات أو تغيير الجلسة الافتراضية بإعادة تعريف `configure_sessions()`، لكن يجب استخدام النسخة غير المتزامنة فقط من كل نوع، كما يوضح الجدول:

| نوع الجلسة | الاستخدام |
|------------|-----------|
| [FetcherSession](../fetching/static.md) | طلبات HTTP سريعة دون JavaScript |
| [AsyncStealthySession](../fetching/stealthy.md) | تشغيل JavaScript، والتحكم الآلي في المتصفح، وتجاوز أنظمة مكافحة البوتات |

## إعداد الجلسات {#configuring-sessions}

أعد تعريف `configure_sessions()` في العنكبوت لإعداد الجلسات. المعامل `manager` هو كائن `SessionManager`. استخدم `manager.add()` لتسجيل الجلسات:

```python
from scrapling.spiders import Spider, Response
from scrapling.fetchers import FetcherSession

class MySpider(Spider):
    name = "my_spider"
    start_urls = ["https://example.com"]

    def configure_sessions(self, manager):
        manager.add("default", FetcherSession())

    async def parse(self, response: Response):
        yield {"title": response.css("title::text").get("")}
```

تقبل `manager.add()` المعاملات التالية:

| المعامل | النوع | القيمة الافتراضية | الوصف |
|---------|-------|-------------------|-------|
| `session_id` | `str` | *مطلوب* | اسم لاختيار الجلسة في الطلبات |
| `session` | `Session` | *مطلوب* | كائن الجلسة |
| `default` | `bool` | `False` | جعل هذه الجلسة هي الافتراضية |
| `lazy` | `bool` | `False` | تشغيل الجلسة عند أول استخدام فقط |

!!! note "ملاحظات"

    1. إذا لم تحدد جلسة في الطلب، تُستخدم الجلسة الافتراضية. تُحدد هذه الجلسة بإحدى طريقتين:
        1. تصبح أول جلسة تضيفها إلى المدير هي الافتراضية تلقائيًا.
        2. تصبح الجلسة التي تضيفها مع `default=True` هي الافتراضية.
    2. لا تحتاج إلى تشغيل كائنات الجلسات قبل إضافتها. يفحص العنكبوت الجلسات ويشغّل كل جلسة لم تبدأ بعد.
    3. إذا أردت تشغيل جلسة عند الحاجة فقط، فاستخدم `lazy` عند إضافتها إلى المدير. مثلًا، يمكنك تأخير تشغيل المتصفح حتى تحتاجه، بدلًا من تشغيله مع بداية العنكبوت.

## عنكبوت بجلسات متعددة {#multi-session-spider}

هذا مثال عملي يستخدم جلسة HTTP سريعة لصفحات القوائم، ومتصفح Stealth لصفحات التفاصيل التي تستخدم حماية ضد البوتات:

```python
from scrapling.spiders import Spider, Response
from scrapling.fetchers import FetcherSession, AsyncStealthySession

class ProductSpider(Spider):
    name = "products"
    start_urls = ["https://shop.example.com/products"]

    def configure_sessions(self, manager):
        # Fast HTTP for listing pages (default)
        manager.add("http", FetcherSession())

        self.browser_session = AsyncStealthySession(
            headless=True,
            network_idle=True,
            record_requests=True,
        )
        manager.add("stealth", self.browser_session)

    async def parse(self, response: Response):
        for link in response.css("a.product::attr(href)").getall():
            # Route product pages through the stealth session
            yield response.follow(link, sid="stealth", callback=self.parse_product)

        next_page = response.css("a.next::attr(href)").get()
        if next_page:
            yield response.follow(next_page)

    async def parse_product(self, response: Response):
        yield {
            "name": response.css("h1::text").get(""),
            "price": response.css(".price::text").get(""),
        }

    async def on_close(self):
        for api_response in self.browser_session.network.search(
            url_pattern=r"https://api\.shop\.example\.com/.*", limit=None
        ):
            self.logger.info(f"Saved API response: {api_response.url} ({api_response.status})")
```

يحتفظ المثال بكائن المتصفح، ويقرأ سجل ردود API المحفوظ مرة واحدة داخل `on_close()` قبل إغلاق الجلسات. يشمل السجل جميع صفحات المنتجات، ويظل قابلًا للقراءة بعد الإغلاق. لا ينتظر الكود عمليات التسجيل التي لم تكتمل بعد، وتظل حدود الاحتفاظ بالسجل مطبّقة.

المعامل الأساسي هنا هو `sid`، فهو يحدد الجلسة المستخدمة لكل طلب. عند استدعاء `response.follow()` دون `sid`، يُورث معرّف الجلسة من الطلب الأصلي.

لا يلزم أن تكون الجلسات من كلاسات مختلفة. يمكن إنشاء عدة كائنات من كلاس الجلسة نفسه، بإعدادات مختلفة، كما في المثال التالي:

```python
from scrapling.spiders import Spider, Response
from scrapling.fetchers import FetcherSession

class ProductSpider(Spider):
    name = "products"
    start_urls = ["https://shop.example.com/products"]

    def configure_sessions(self, manager):
        chrome_requests = FetcherSession(impersonate="chrome")
        firefox_requests = FetcherSession(impersonate="firefox")

        manager.add("chrome", chrome_requests)
        manager.add("firefox", firefox_requests)

    async def parse(self, response: Response):
        for link in response.css("a.product::attr(href)").getall():
            yield response.follow(link, callback=self.parse_product)

        next_page = response.css("a.next::attr(href)").get()
        if next_page:
            yield response.follow(next_page, sid="firefox")

    async def parse_product(self, response: Response):
        yield {
            "name": response.css("h1::text").get(""),
            "price": response.css(".price::text").get(""),
        }
```

ويمكنك أيضًا تخصيص جلسة بطلبات معينة، بحيث تحتفظ بملفات تعريف الارتباط والحالة الخاصة بهذه الطلبات، وغير ذلك.

## معاملات الجلسة {#session-arguments}

تُمرّر المعاملات المسماة الإضافية التي تضعها في `Request`، أو في `response.follow(**kwargs)`، إلى دالة الجلب في الجلسة. يتيح ذلك تخصيص كل طلب دون تغيير إعدادات الجلسة:

```python
async def parse(self, response: Response):
    # Pass extra headers for this specific request
    yield Request(
        "https://api.example.com/data",
        headers={"Authorization": "Bearer token123"},
        callback=self.parse_api,
    )

    # Use a different HTTP method
    yield Request(
        "https://example.com/submit",
        method="POST",
        data={"field": "value"},
        sid="firefox",
        callback=self.parse_result,
    )
```

!!! warning "تنبيه"

    عند استخدام `FetcherSession` أو `Fetcher` أو `AsyncFetcher` عادةً، تختار طريقة HTTP باستدعاء الدالة المناسبة مثل `.get()` أو `.post()`. لكن هذا لا ينطبق على `FetcherSession` داخل العناكب. يكون الطلب افتراضيًا من نوع _HTTP GET_. لاستخدام طريقة أخرى، مرّرها إلى المعامل `method` كما في المثال السابق. الهدف هو توحيد واجهة `Request` بين جميع أنواع الجلسات.

بعد تسجيل جلسة `"stealth"` من نوع `AsyncStealthySession` كما في مثال الجلسات المتعددة، يمكنك تمرير معاملات خاصة بالمتصفح، مثل `wait_selector` و`page_action` و`extra_headers`:

```python
async def parse(self, response: Response):
    # Use Cloudflare solver with the `AsyncStealthySession` we configured above
    yield Request(
        "https://nopecha.com/demo/cloudflare",
        sid="stealth",
        callback=self.parse_result,
        solve_cloudflare=True,
        block_webrtc=True,
        hide_canvas=True,
        google_search=True,
    )

    yield response.follow(
        "/dynamic-page",
        sid="stealth",
        callback=self.parse_dynamic,
        wait_selector="div.loaded",
        network_idle=True,
    )
```

!!! warning "تنبيه"

    ترث `response.follow()` معاملات الجلسة `**kwargs` من الطلب الأصلي، باستثناء `method` و`params` و`data` و`json` و`files` و`multipart`. لذلك تؤدي متابعة رابط بعد طلب POST إلى إرسال GET عادي. تتقدم المعاملات الجديدة على المعاملات الموروثة إذا تكرر الاسم.

```python
from scrapling.spiders import Spider, Response
from scrapling.fetchers import FetcherSession

class ProductSpider(Spider):
    name = "products"
    start_urls = ["https://shop.example.com/products"]

    def configure_sessions(self, manager):
        manager.add("http", FetcherSession(impersonate='chrome'))

    async def parse(self, response: Response):
        # I don't want the follow request to impersonate a desktop Chrome like the previous request, but a mobile one
        # so I override it like this
        for link in response.css("a.product::attr(href)").getall():
            yield response.follow(link, impersonate="chrome131_android", callback=self.parse_product)

        next_page = response.css("a.next::attr(href)").get()
        if next_page:
            yield response.follow(next_page)

    async def parse_product(self, response: Response):
        yield {
            "name": response.css("h1::text").get(""),
            "price": response.css(".price::text").get(""),
        }
```

!!! info "معلومة"

    عند إغلاق العنكبوت، يفحص مدير الجلسات تلقائيًا أي جلسات لا تزال تعمل ويغلقها قبل إغلاق العنكبوت.
