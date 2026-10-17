---
title: "تبديل البروكسي وإعادة طلبات الزحف المحظورة"
description: "استخدم البروكسي واستراتيجيات تبديله في عناكب Scrapling. اكتشف الردود المحظورة وأعد الطلبات وانتقل من جلسات HTTP إلى جلسات المتصفح."
---

# إدارة البروكسي والتعامل مع الحظر {#proxy-management-and-handling-blocks}

## مقدمة {#introduction}

!!! success "قبل البدء"

    1. اقرأ صفحة [البداية](getting-started.md) وتعرّف على إنشاء عنكبوت بسيط وتشغيله.
    2. اقرأ صفحة [الجلسات](sessions.md) وتعرّف على كيفية إعدادها.

عند استخراج البيانات على نطاق واسع، قد تحتاج إلى التبديل بين عدة خوادم بروكسي لتجنب حدود معدل الطلبات والحظر. يجعل `ProxyRotator` في Scrapling هذا الأمر سهلًا. يعمل مع جميع أنواع الجلسات، ويتكامل مع نظام إعادة الطلبات المحظورة في العنكبوت.

إذا لم تكن تعرف ما هو البروكسي أو كيف تختار بروكسي جيدًا، فيمكن أن يساعدك [هذا الدليل](https://substack.thewebscraping.club/p/everything-about-proxies).

## ProxyRotator {#proxyrotator}

يدير الكلاس `ProxyRotator` قائمة خوادم البروكسي ويبدّل بينها تلقائيًا. مرّره إلى أي نوع جلسة عبر المعامل `proxy_rotator`:

```python
from scrapling.spiders import Spider, Response
from scrapling.fetchers import FetcherSession, ProxyRotator

class MySpider(Spider):
    name = "my_spider"
    start_urls = ["https://example.com"]

    def configure_sessions(self, manager):
        rotator = ProxyRotator([
            "http://proxy1:8080",
            "http://proxy2:8080",
            "http://user:pass@proxy3:8080",
        ])
        manager.add("default", FetcherSession(proxy_rotator=rotator))

    async def parse(self, response: Response):
        # Check which proxy was used
        print(f"Proxy used: {response.meta.get('proxy')}")
        yield {"title": response.css("title::text").get("")}
```

يحصل كل طلب تلقائيًا على البروكسي التالي في الترتيب. يُحفظ البروكسي المستخدم في `response.meta["proxy"]`، لتعرف أي بروكسي جلب كل صفحة.

عند استخدامه مع جلسات المتصفح، تحتاج إلى بعض التعديلات، كما في المثال التالي:

```python
from scrapling.fetchers import AsyncStealthySession, ProxyRotator

# String proxies work for all session types
rotator = ProxyRotator([
    "http://proxy1:8080",
    "http://proxy2:8080",
])

# Dict proxies (Playwright format) work for browser sessions
rotator = ProxyRotator([
    {"server": "http://proxy1:8080", "username": "user", "password": "pass"},
    {"server": "http://proxy2:8080"},
])

# Then inside the spider
def configure_sessions(self, manager):
    rotator = ProxyRotator(["http://proxy1:8080", "http://proxy2:8080"])
    manager.add("browser", AsyncStealthySession(proxy_rotator=rotator))
```

!!! info "معلومة"

    1. لا يمكنك استخدام `proxy_rotator` مع `proxy` أو `proxies` الثابتة في الجلسة نفسها. اختر طريقة واحدة عند إعداد الجلسة، ويمكنك تغيير البروكسي لطلبات محددة لاحقًا، كما سنوضح.
    2. تذكّر أن كل جلسات المتصفح تستخدم افتراضيًا سياق متصفح دائمًا مع مجموعة تبويبات. لكن المتصفحات لا تتيح تحديد بروكسي لكل تبويب. لذلك، عند استخدام `ProxyRotator`، تنشئ أداة الجلب سياقًا منفصلًا لكل بروكسي، مع تبويب واحد لكل سياق. وبمجرد انتهاء عمل التبويب، يُغلق هو وسياقه.

## استراتيجيات تبديل مخصّصة {#custom-rotation-strategies}

يستخدم `ProxyRotator` التبديل الدوري افتراضيًا، فيمرّ على البروكسي بالترتيب ثم يعود إلى البداية بعد آخر واحد.

يمكنك تمرير دالة استراتيجية مخصّصة لتغيير هذا السلوك، لكن يجب أن تلتزم بالتوقيع التالي:

```python
from scrapling.core._types import ProxyType

def my_strategy(proxies: list, current_index: int) -> tuple[ProxyType, int]:
    ...
```

تستقبل الدالة قائمة البروكسي والفهرس الحالي، ويجب أن تعيد البروكسي المختار والفهرس التالي.

فيما يلي بعض أمثلة استراتيجيات التبديل المخصّصة التي يمكنك استخدامها.

### التبديل العشوائي {#random-rotation}

```python
import random
from scrapling.fetchers import ProxyRotator

def random_strategy(proxies, current_index):
    idx = random.randint(0, len(proxies) - 1)
    return proxies[idx], idx

rotator = ProxyRotator(
    ["http://proxy1:8080", "http://proxy2:8080", "http://proxy3:8080"],
    strategy=random_strategy,
)
```

### التبديل حسب الأوزان {#weighted-rotation}

```python
import random

def weighted_strategy(proxies, current_index):
    # First proxy gets 60% of traffic, others split the rest
    weights = [60] + [40 // (len(proxies) - 1)] * (len(proxies) - 1)
    proxy = random.choices(proxies, weights=weights, k=1)[0]
    return proxy, current_index  # Index doesn't matter for weighted

rotator = ProxyRotator(proxies, strategy=weighted_strategy)
```

## تغيير البروكسي لطلب محدد {#per-request-proxy-override}

يمكنك تجاوز اختيار `ProxyRotator` لطلب معين بتمرير `proxy=` كمعامل مسمّى:

```python
async def parse(self, response: Response):
    # This request uses the rotator's next proxy
    yield response.follow("/page1", callback=self.parse_page)

    # This request uses a specific proxy, bypassing the rotator
    yield response.follow(
        "/special-page",
        callback=self.parse_page,
        proxy="http://special-proxy:8080",
    )
```

يفيد ذلك عندما تحتاج صفحات معينة إلى بروكسي محدد، مثل بروكسي من بلد معين للوصول إلى محتوى خاص بتلك المنطقة.

## التعامل مع الطلبات المحظورة {#blocked-request-handling}

يحتوي العنكبوت على دعم مدمج لاكتشاف الطلبات المحظورة وإعادتها. يعتبر رموز حالة HTTP التالية حظرًا افتراضيًا: `401` و`403` و`407` و`429` و`444` و`500` و`502` و`503` و`504`.

يعمل نظام إعادة المحاولة كما يلي:

1. بعد وصول الرد، يستدعي العنكبوت `is_blocked(response)`.
2. إذا كان الطلب محظورًا، ينسخ الطلب ويستدعي `retry_blocked_request()`، لتتمكن من تعديله قبل إعادة المحاولة.
3. يُعاد الطلب إلى الطابور مع `dont_filter=True` لتجاوز منع التكرار، وبأولوية أقل حتى لا يُعاد فورًا.
4. تتكرر العملية حتى `max_blocked_retries` مرة، والقيمة الافتراضية هي 3.

!!! tip "نصيحة"

    1. عند إعادة المحاولة، تُحذف قيم `proxy` و`proxies` السابقة من معاملات الطلب تلقائيًا، ليختار `ProxyRotator` بروكسي جديدًا.
    2. تختلف الخاصية `max_blocked_retries` عن محاولات الإعادة داخل الجلسة، ولا تشاركها عداد المحاولات.

### تخصيص اكتشاف الحظر {#custom-block-detection}

أعد تعريف `is_blocked()` لإضافة طريقة اكتشاف خاصة بك:

```python
class MySpider(Spider):
    name = "my_spider"
    start_urls = ["https://example.com"]

    async def is_blocked(self, response: Response) -> bool:
        # Check status codes (default behavior)
        if response.status in {403, 429, 503}:
            return True

        # Check response content
        body = response.body.decode("utf-8", errors="ignore")
        if "access denied" in body.lower() or "rate limit" in body.lower():
            return True

        return False

    async def parse(self, response: Response):
        yield {"title": response.css("title::text").get("")}
```

### تخصيص إعادة المحاولة {#customizing-retries}

أعد تعريف `retry_blocked_request()` لتعديل الطلب قبل إعادته. تحدد `max_blocked_retries` عدد مرات إعادة الطلب المحظور، وقيمتها الافتراضية هي 3:

```python
from scrapling.spiders import Spider, SessionManager, Request, Response
from scrapling.fetchers import FetcherSession, AsyncStealthySession


class MySpider(Spider):
    name = "my_spider"
    start_urls = ["https://example.com"]
    max_blocked_retries = 5

    def configure_sessions(self, manager: SessionManager) -> None:
        manager.add('requests', FetcherSession(impersonate=['chrome', 'firefox', 'safari']))
        manager.add('stealth', AsyncStealthySession(block_webrtc=True), lazy=True)

    async def retry_blocked_request(self, request: Request, response: Response) -> Request:
        request.sid = "stealth"
        self.logger.info(f"Retrying blocked request: {request.url}")
        return request

    async def parse(self, response: Response):
        yield {"title": response.css("title::text").get("")}
```

في المثال السابق، تركت طريقة اكتشاف الحظر كما هي، وجعلت العنكبوت يعتمد على طلبات HTTP حتى يُحظر، ثم ينتقل إلى متصفح Stealth.

هذا مثال يجمع كل ما سبق:

```python
from scrapling.spiders import Spider, SessionManager, Request, Response
from scrapling.fetchers import FetcherSession, AsyncStealthySession, ProxyRotator


cheap_proxies = ProxyRotator([ "http://proxy1:8080", "http://proxy2:8080"])

# A format acceptable by the browser
expensive_proxies = ProxyRotator([
    {"server": "http://residential_proxy1:8080", "username": "user", "password": "pass"},
    {"server": "http://residential_proxy2:8080", "username": "user", "password": "pass"},
    {"server": "http://mobile_proxy1:8080", "username": "user", "password": "pass"},
    {"server": "http://mobile_proxy2:8080", "username": "user", "password": "pass"},
])


class MySpider(Spider):
    name = "my_spider"
    start_urls = ["https://example.com"]
    max_blocked_retries = 5

    def configure_sessions(self, manager: SessionManager) -> None:
        manager.add('requests', FetcherSession(impersonate=['chrome', 'firefox', 'safari'], proxy_rotator=cheap_proxies))
        manager.add('stealth', AsyncStealthySession(block_webrtc=True, proxy_rotator=expensive_proxies), lazy=True)

    async def retry_blocked_request(self, request: Request, response: Response) -> Request:
        request.sid = "stealth"
        self.logger.info(f"Retrying blocked request: {request.url}")
        return request

    async def parse(self, response: Response):
        yield {"title": response.css("title::text").get("")}
```

الفكرة هنا هي إرسال الطلبات ببروكسي منخفض التكلفة، مثل بروكسي مراكز البيانات، حتى تُحظر. ثم تُعاد باستخدام بروكسي أعلى جودة، مثل البروكسي السكني أو بروكسي شبكات الهاتف المحمول.
