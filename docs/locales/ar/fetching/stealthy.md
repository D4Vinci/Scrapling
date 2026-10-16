---
title: "جمع بيانات مواقع JavaScript باستخدام StealthyFetcher"
description: "حمّل الصفحات وانتظر البيانات وأعد استخدام تسجيل الدخول واقرأ ردود API في الخلفية عبر جلسات متصفح Scrapling، مع إعداد البروكسي والتعامل مع اختبارات الحماية."
---

# جلب الصفحات بالمتصفح باستخدام StealthyFetcher {#browser-fetching-with-stealthyfetcher}

تحمّل فئة `StealthyFetcher` صفحات JavaScript وتؤتمت Chromium أو Google Chrome مع ميزات لتجاوز كشف البوتات. تستخدم [واجهة Playwright](https://playwright.dev/python/docs/intro) مع تعديلات للتخفي.

كما سنوضح لاحقًا، تحتاج إلى بعض المعرفة بـ[واجهة Page في Playwright](https://playwright.dev/python/docs/api/class-page) لأتمتة الصفحة.

!!! success "قبل البدء"

    1. اقرأ [أساسيات أدوات الجلب](../fetching/choosing.md) لتفهم [كائن Response](../fetching/choosing.md#response-object) وتختار أداة الجلب المناسبة.
    2. اقرأ [البحث عن العناصر](../parsing/selection.md) لتعرف كيف تجد العناصر وتستخرجها من كائن [Selector](../parsing/main_classes.md#selector) أو [Response](../fetching/choosing.md#response-object).
    3. اقرأ [الفئات الأساسية](../parsing/main_classes.md) لتعرف الخصائص والدوال التي ترثها [Response](../fetching/choosing.md#response-object) من [Selector](../parsing/main_classes.md#selector).

## الاستخدام الأساسي {#basic-usage}
هذه طريقة الاستيراد الأساسية، وهي نفسها لكل أدوات الجلب:

```python
from scrapling.fetchers import StealthyFetcher
```
تعرّف على إعداد خيارات التحليل [هنا](choosing.md#parser-configuration-in-all-fetchers).

سنراجع معظم الخيارات واحدًا تلو الآخر مع أمثلة. للوصول مباشرة إلى جدول كل الخيارات، [اضغط هنا](#full-list-of-arguments).

!!! abstract "معلومة سريعة"

    النسخة غير المتزامنة من دالة `fetch` هي `async_fetch`.


توفر أداة الجلب حاليًا ثلاثة خيارات أساسية للتشغيل، ويمكن الجمع بين الخيارات حسب الحاجة.

وهي:

### 1. Chromium المرفق {#1-bundled-chromium}
```python
StealthyFetcher.fetch('https://example.com')
```
يفتح هذا Chromium المرفق بإعدادات التخفي الافتراضية، ثم يحمّل الصفحة.

### 2. Chrome الحقيقي {#2-real-chrome}
```python
StealthyFetcher.fetch('https://example.com', real_chrome=True)
```
استخدم هذا الخيار إذا كان Google Chrome مثبّتًا لديك. يعمل مثل الخيار الأول، لكنه يستخدم Chrome المثبّت على جهازك بدلًا من Chromium. بذلك تبدو الطلبات أقرب إلى استخدام متصفح حقيقي، فيصعب كشفها وتحصل على نتائج أفضل.

إذا لم يكن Chrome مثبّتًا وتريد هذا الخيار، يمكنك تثبيته للمكتبة من الطرفية بدلًا من تثبيته يدويًا:
```commandline
playwright install chrome
```

### 3. الاتصال عبر CDP {#3-cdp-connection}
```python
StealthyFetcher.fetch('https://example.com', cdp_url='ws://localhost:9222')
```
بدلًا من تشغيل Chromium أو Chrome محليًا، يمكنك الاتصال بمتصفح بعيد عبر [Chrome DevTools Protocol](https://chromedevtools.github.io/devtools-protocol/).

يمكن أن يكون الرابط عنوان WebSocket يبدأ بـ`ws://` أو `wss://`، وهو ما يقدمه مزودو المتصفحات، أو عنوان HTTP للمتصفح مثل `http://localhost:9222`.


## ما الذي توفره الأداة؟ {#what-does-it-do}

يدعم StealthyFetcher الميزات التالية لتجاوز كشف البوتات:

1. تجاوز أنواع Cloudflare Turnstile وInterstitial تلقائيًا باستخدام `solve_cloudflare=True`.
2. منع تسريبات بيئة تشغيل CDP وتسريبات WebRTC.
3. عزل تنفيذ JavaScript، وإزالة كثير من بصمات Playwright، وتجنب بعض سلوكيات البوتات المعروفة.
4. إضافة تشويش إلى canvas لمنع استخدامه في تكوين بصمة للمتصفح.
5. تعديل الطرق المعروفة لكشف وضع المتصفح بلا واجهة تلقائيًا، مع خيار لتجنب الكشف بسبب اختلاف المنطقة الزمنية.
6. وخيارات أخرى لتجاوز الحماية...

## قائمة الخيارات الكاملة {#full-list-of-arguments}
يوفر Scrapling خيارات كثيرة لهذه الأداة وفئات جلساتها. قبل الانتقال إلى [الأمثلة](#examples)، هذه قائمة الخيارات كاملة:


| الخيار | الوصف | اختياري |
|:---------------------:|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|:--------:|
| url | الرابط المطلوب. | ❌ |
| headless | استخدم `True` لتشغيل المتصفح بلا واجهة ظاهرة، وهو **الافتراضي**، أو `False` لعرضه. | ✔️ |
| disable_resources | يمنع تحميل الموارد غير الضرورية لزيادة السرعة. الأنواع المحظورة هي `font` و`image` و`media` و`beacon` و`object` و`imageset` و`texttrack` و`websocket` و`csp_report` و`stylesheet`. | ✔️ |
| cookies | يحدد ملفات تعريف الارتباط للطلب التالي. | ✔️ |
| useragent | نص User-Agent المطلوب. **دون تحديده، تنشئ الأداة User-Agent حقيقيًا للمتصفح نفسه وإصداره وتستخدمه.** | ✔️ |
| network_idle | ينتظر حتى تخلو الصفحة من اتصالات الشبكة لمدة 500 ms على الأقل. | ✔️ |
| load_dom | مفعّل افتراضيًا. ينتظر تحميل JavaScript في الصفحات وتنفيذه، أي حالة `domcontentloaded`. | ✔️ |
| pierce_shadow | يضم محتوى Shadow DOM المفتوح إلى HTML الرد. الافتراضي `False`. يمكن ضبطه للجلسة أو تغييره لكل طلب. | ✔️ |
| timeout | المهلة بالميلي ثانية لكل العمليات والانتظار في الصفحة. الافتراضي 30,000 ms، أي 30 ثانية. | ✔️ |
| wait | مدة انتظار إضافية بالميلي ثانية بعد اكتمال كل شيء، قبل إغلاق الصفحة وإعادة كائن `Response`. | ✔️ |
| page_action | لأتمتة الصفحة. مرّر دالة تستقبل كائن `page` وتعمل بعد الانتقال لتنفيذ الخطوات المطلوبة. | ✔️ |
| page_setup | دالة تستقبل كائن `page` وتعمل قبل الانتقال. استخدمها لتسجيل مستمعي الأحداث أو routes التي يجب إعدادها قبل تحميل الصفحة. | ✔️ |
| wait_selector | ينتظر وصول عنصر يطابق محدد CSS إلى حالة معينة. | ✔️ |
| init_script | مسار مطلق لملف JavaScript يُنفّذ عند إنشاء كل صفحة في الجلسة. | ✔️ |
| wait_selector_state | الحالة التي ينتظرها Scrapling للمحدد الممرّر عبر `wait_selector`. _الافتراضي `attached`._ | ✔️ |
| google_search | مفعّل افتراضيًا. يضيف ترويسة referer من Google. | ✔️ |
| extra_headers | قاموس ترويسات إضافية للطلب. _إذا استُخدم مع `google_search`، تكون الأولوية لقيمة referer التي يحددها `google_search`._ | ✔️ |
| proxy | البروكسي المستخدم للطلبات. يقبل نصًا أو قاموسًا بالمفاتيح 'server' و'username' و'password' فقط. | ✔️ |
| real_chrome | فعّله إذا كان Chrome مثبّتًا على جهازك، لتشغّل أداة الجلب نسخة منه وتستخدمها. | ✔️ |
| locale | لغة المستخدم وإعداداته المحلية، مثل `en-GB` أو `de-DE`. يؤثر في `navigator.language` وترويسة `Accept-Language` وقواعد تنسيق الأرقام والتواريخ. يستخدم إعداد النظام افتراضيًا. | ✔️ |
| timezone_id | يغيّر المنطقة الزمنية للمتصفح. الافتراضي هو منطقة النظام الزمنية. | ✔️ |
| cdp_url | يتصل بهذا الرابط للتحكم بمتصفح عبر CDP بدلًا من تشغيل متصفح جديد. | ✔️ |
| user_data_dir | مسار مجلد بيانات المستخدم، الذي يحفظ ملفات تعريف الارتباط والتخزين المحلي. ينشئ مجلدًا مؤقتًا افتراضيًا. **يعمل مع الجلسات فقط.** | ✔️ |
| extra_flags | قائمة خيارات إضافية تُمرّر إلى المتصفح عند تشغيله. | ✔️ |
| solve_cloudflare | يحل كل أنواع اختبارات Cloudflare Turnstile وInterstitial قبل إعادة الرد. الافتراضي `False`. | ✔️ |
| block_webrtc | يُلزم WebRTC باتباع إعدادات البروكسي لمنع تسريب عنوان IP المحلي. | ✔️ |
| hide_canvas | يضيف تشويشًا عشوائيًا إلى عمليات canvas لمنع تكوين بصمة. | ✔️ |
| allow_webgl | مفعّل افتراضيًا. تعطيله يوقف WebGL وWebGL 2.0 تمامًا. لا يُنصح بذلك، لأن كثيرًا من أنظمة WAF تتحقق الآن من تفعيل WebGL. | ✔️ |
| additional_args | إعدادات إضافية تُمرّر إلى سياق Playwright، ولها أولوية أعلى من إعدادات Scrapling. | ✔️ |
| selector_config | قاموس خيارات تحليل مخصصة يُستخدم عند إنشاء كائن `Selector` أو `Response` النهائي. | ✔️ |
| blocked_domains | مجموعة أسماء نطاقات لحظر الطلبات إليها، بما فيها النطاقات الفرعية. مثلًا، يحظر `"example.com"` النطاق `"sub.example.com"` أيضًا. | ✔️ |
| block_ads | يحظر الطلبات إلى نحو 3,500 نطاق إعلانات وتتبع معروف. يمكن جمعه مع `blocked_domains`. | ✔️ |
| dns_over_https | يوجّه استعلامات DNS عبر DNS-over-HTTPS من Cloudflare لمنع تسريب DNS عند استخدام البروكسي. | ✔️ |
| proxy_rotator | كائن `ProxyRotator` لتبديل البروكسي تلقائيًا. لا يمكن جمعه مع `proxy`. | ✔️ |
| retries | عدد محاولات الطلبات الفاشلة. الافتراضي 3. | ✔️ |
| retry_delay | مدة الانتظار بالثواني بين المحاولات. الافتراضي ثانية واحدة. | ✔️ |
| record_requests | يحتفظ بالطلبات المكتملة والردود المحفوظة في `session.network`. للجلسات فقط، والافتراضي `False`. | ✔️ |
| max_recorded_requests | أقصى عدد طلبات محفوظة لكل جلسة. الافتراضي 1,000. توجد أيضًا حدود ثابتة لحجم محتوى الردود المحفوظ. | ✔️ |
| executable_path | مسار مطلق لملف متصفح تنفيذي مخصص بدلًا من Chromium المرفق. يفيد في التثبيتات غير المعتادة أو نسخ المتصفح المخصصة. | ✔️ |

يمكن ضبط كل هذه الخيارات للجلسة كاملة. ويمكن أيضًا ضبط كل طلب وحده بتمرير الخيارات التي تعمل على مستوى علامة تبويب المتصفح، مثل `google_search` و`timeout` و`wait` و`page_action` و`page_setup` و`extra_headers` و`disable_resources` و`wait_selector` و`wait_selector_state` و`network_idle` و`load_dom` و`pierce_shadow` و`solve_cloudflare` و`blocked_domains` و`proxy` و`selector_config`.

!!! note "ملاحظات:"

    1. زاد `disable_resources` سرعة الطلبات بنحو 25% في اختباراتي لبعض المواقع، وقد يقلل استخدام البروكسي. لكن استخدمه بحذر، لأنه قد يمنع بعض المواقع من إكمال التحميل.
    2. الخيار `google_search` مفعّل افتراضيًا لكل الطلبات، ويضبط referer على `https://www.google.com/`. وله أولوية على قيمة referer في `extra_headers` عند استخدامهما معًا.
    3. إذا لم تحدد User-Agent وفعّلت وضع headless، تنشئ الأداة User-Agent حقيقيًا لإصدار المتصفح نفسه. وإذا لم تحدده ولم تفعّل headless، تستخدم User-Agent الافتراضي للمتصفح، وهو نفسه المستخدم في المتصفحات المعتادة في الإصدارات الحديثة.
    4. يُسجّل `init_script` مع سياق المتصفح ليعمل عند إنشاء الصفحات. يستخدم وضع التخفي سياق التنفيذ المعزول في Patchright افتراضيًا. إذا احتاجت `page_action` إلى قراءة متغيرات عامة يضعها السكربت على `window`، استدعِ `page.evaluate(..., isolated_context=False)` داخل الدالة.

## إدارة الجلسات {#session-management}

لإبقاء المتصفح مفتوحًا أثناء إرسال عدة طلبات بالإعدادات نفسها، استخدم `StealthySession` أو `AsyncStealthySession`. تقبل الفئتان كل خيارات `fetch`، فتستطيع تحديد إعدادات للجلسة كلها.

```python
from scrapling.fetchers import StealthySession


with StealthySession(
    headless=True,
    disable_resources=True,
    real_chrome=True
) as session:

    page1 = session.fetch('https://example1.com')
    page2 = session.fetch('https://example2.com')
    page3 = session.fetch('https://dynamic-site.com')


```

### استخدام جلسة غير متزامنة {#async-session-usage}

```python
import asyncio
from scrapling.fetchers import AsyncStealthySession

async def scrape_multiple_sites():
    async with AsyncStealthySession(
        network_idle=True,
        timeout=30000,
        max_pages=3
    ) as session:

        pages = await asyncio.gather(
            session.fetch('https://spa-app1.com'),
            session.fetch('https://spa-app2.com'),
            session.fetch('https://dynamic-content.com')
        )
        return pages
```

ربما لاحظت `max_pages`. يتيح الاحتفاظ **بمجموعة علامات تبويب للمتصفح**، وتحدد به أقصى عدد مفتوح في الوقت نفسه. تبقى علامات التبويب مفتوحة بعد انتهاء طلباتها. مع كل طلب، تفعل المكتبة التالي:

1. تعيد استخدام علامة تبويب متاحة إن وجدت. يطبّق كل طلب إعداداته الخاصة، مثل `timeout` و`extra_headers` و`disable_resources` و`blocked_domains`، فلا تنتقل إعدادات الطلب السابق إليه.
2. أو تفتح علامة تبويب جديدة إذا كان العدد الحالي أقل من `max_pages`.
3. وإلا تتحقق على فترات تقل عن ثانية من توفر علامة تبويب، لمدة 60 ثانية، ثم ترفع `TimeoutError`. قد يحدث ذلك إذا توقف الموقع عن الاستجابة.

تُغلق علامات التبويب التي يحدث فيها خطأ وتُستبدل. ويمكنك إغلاقها كلها في أي وقت باستخدام `session.close_pages()`، وسيفتح الطلب التالي علامة جديدة.

يسمح هذا بجلب عدة روابط في الوقت نفسه داخل المتصفح نفسه، فيوفر الموارد ويزيد السرعة كثيرًا :)

بقاء علامات التبويب مفتوحة يعني أيضًا أن الصفحة السابقة تبقى متاحة للطلب التالي. تعمل `page_setup` في الطلب التالي عليها قبل الانتقال إلى صفحة أخرى. هذا أساس ربط خطوات الأتمتة بين الطلبات.

كانت الإصدارات من 0.3.2 إلى 0.4.14 تغلق كل علامة تبويب بعد الطلب، لأن إعادة استخدامها كانت تنقل الإعدادات بين الطلبات. منذ 0.4.15، تُعاد تهيئة الإعدادات عند كل استخدام، ولذلك تبقى العلامات مفتوحة.

### حفظ حالة الجلسة واستعادتها {#save-and-load-session-state}

استخدم `save_state(path)` لحفظ ملفات تعريف الارتباط والتخزين المحلي وIndexedDB في ملف JSON. واستخدم `load_state(path)` لاستعادته في جلسة أخرى أو استبدال الحالة المخزنة للجلسة الحالية. تقبل الدالتان نصًا أو `pathlib.Path` وتعيدان `None`. الصيغة متوافقة مع ملفات حالة التخزين في Playwright.

```python
from scrapling.fetchers import StealthySession

with StealthySession() as session:
    session.fetch('https://example.com')
    session.save_state('state.json')

with StealthySession() as session:
    session.load_state('state.json')
    page = session.fetch('https://example.com')
```

احفظ الحالة بعد انتهاء تسجيل الدخول أو خطوات المتصفح الأخرى. استدعِ الدالتين داخل جلسة بدأت بالفعل، وبعد اكتمال طلبات الجلب المعلقة. تحل الحالة المحمّلة محل ملفات تعريف الارتباط والتخزين المحلي وIndexedDB الحالية. اجلب الصفحة أو أعد تحميلها لاستخدام تسجيل الدخول المستعاد، لأن تحميل الحالة لا ينقل علامات التبويب المفتوحة.

استخدم `await` مع `AsyncStealthySession`:

```python
from scrapling.fetchers import AsyncStealthySession

async def restore_session():
    async with AsyncStealthySession() as session:
        await session.load_state('state.json')
        page = await session.fetch('https://example.com')
        await session.save_state('state.json')
        return page
```

تحفظ هذه الدوال سياق المتصفح المشترك وتستعيده فقط. لا تؤثر في سياقات البروكسي المؤقتة لكل طلب. جلسات `proxy_rotator` ليس لها سياق مشترك، لذلك ترفع الدوال فيها `RuntimeError`. أما `proxy` الثابت للجلسة فيعمل كالمعتاد.

لا يحتوي الملف على `sessionStorage` أو علامات التبويب المفتوحة أو إعدادات المتصفح. يستبدل الحفظ الملف الموجود، ويجب أن يكون المجلد الأب موجودًا. تُمرّر أخطاء الملفات وJSON إلى المستدعي.

### فوائد الجلسات {#session-benefits}

- **إعادة استخدام المتصفح**: طلبات لاحقة أسرع بكثير باستخدام المتصفح نفسه.
- **حفظ ملفات تعريف الارتباط**: إدارة تلقائية لها ولحالة الجلسة، كما يفعل أي متصفح.
- **بصمة ثابتة**: بصمة المتصفح نفسها في كل الطلبات.
- **استخدام أفضل للذاكرة**: استهلاك أقل للموارد مقارنة بتشغيل متصفح جديد لكل طلب.


## أمثلة {#examples}
الأمثلة تجعل الشرح أوضح، فلنرَ بعضها.

### التحكم في الموارد {#resource-control}

```python

page = StealthyFetcher.fetch('https://example.com', disable_resources=True)
```

### Shadow DOM {#shadow-dom}

تحتفظ بعض الصفحات بمحتوى داخل shadow roots مفتوحة لا تظهر في HTML المعتاد للصفحة. فعّل `pierce_shadow` لضم هذا المحتوى إلى الرد، ثم استخدم CSS أو XPath كالمعتاد:

```python
from scrapling.fetchers import StealthyFetcher

page = StealthyFetcher.fetch('https://example.com', pierce_shadow=True)
titles = page.css('product-card .title::text').getall()
```

الافتراضي `False`. يمكنك تفعيله للجلسة وتعطيله لطلب معين:

```python
from scrapling.fetchers import StealthySession

with StealthySession(pierce_shadow=True) as session:
    page = session.fetch('https://example.com')
    plain_page = session.fetch('https://example.com', pierce_shadow=False)
```

يعمل الخيار نفسه مع `async_fetch` والجلسات غير المتزامنة.

تُضم الجذور المفتوحة فقط. لا يجري المرور على الجذور المغلقة أو مستندات iframe. استخدم `wait_selector` عندما يُحمّل مكوّن بعد الصفحة.

يتحول كل جذر مفتوح إلى غلاف `<shadow-root>` في الرد. تحتفظ عناصر slot بوسومها وخصائصها، وتحتوي العقد المخصصة لها أو المحتوى البديل عند عدم تخصيص شيء. تُحذف عناصر light DOM التابعة غير المخصصة. لا تتغير الصفحة الفعلية في المتصفح.

```html
<product-card>
  <shadow-root>
    <div class="title">Product name</div>
    <slot name="price"><span class="price">20</span></slot>
  </shadow-root>
</product-card>
```

تعمل محددات العناصر المتداخلة عبر هذه العناصر. أما محددات الابن المباشر، فيجب أن تتضمن الأغلفة وعناصر slot:

```python
titles = page.css('product-card .title::text').getall()
titles = page.css('product-card > shadow-root > .title::text').getall()
prices = page.css('product-card > shadow-root > slot[name="price"] > .price::text').getall()
```

تظهر الأغلفة وعناصر slot في مسارات XPath و`.children` و`response.body` وتصدير HTML. يعيد استخراج Markdown والنص محتواها دون طباعة الوسوم. وتظل خصائص إخفاء slot متاحة لأدوات تنظيف المحتوى.

تتبع النسخة المحفوظة ترتيب المحتوى، لكنها لا تحسب ظهور العناصر أو تخطيطها وفق CSS. المحددات التي تحتوي `<shadow-root>` تعمل على رد Scrapling، وليس صفحة المتصفح الفعلية. وقد تتعامل محلّلات HTML الأخرى مع التداخل غير المعتاد بصورة مختلفة.

### حظر النطاقات {#domain-blocking}

```python

page = StealthyFetcher.fetch('https://example.com', blocked_domains={"ads.example.com", "tracker.net"})
```

### التحكم في الشبكة {#network-control}

```python

page = StealthyFetcher.fetch('https://example.com', network_idle=True)


page = StealthyFetcher.fetch('https://example.com', timeout=30000)


page = StealthyFetcher.fetch('https://example.com', proxy='http://username:password@host:port')
```

### تنزيل الملفات {#downloading-files}

```python
page = StealthyFetcher.fetch('https://raw.githubusercontent.com/D4Vinci/Scrapling/main/docs/assets/main_cover.png')

with open(file='main_cover.png', mode='wb') as f:
    f.write(page.body)
```

تعيد خاصية `body` في كائن `Response` قيمة من نوع `bytes` دائمًا.

### الإعداد قبل الانتقال {#pre-navigation-setup}
لإعداد مستمعي الأحداث أو routes أو السكربتات التي يجب تسجيلها قبل انتقال الصفحة، استخدم `page_setup`. تستقبل الدالة كائن `page` وتعمل قبل استدعاء `page.goto()`.

```python
from patchright.sync_api import Page

def capture_websockets(page: Page):
    page.on("websocket", lambda ws: print(f"WebSocket opened: {ws.url}"))

page = StealthyFetcher.fetch('https://example.com', page_setup=capture_websockets)
```
النسخة غير المتزامنة:
```python
from patchright.async_api import Page

async def capture_websockets(page: Page):
    page.on("websocket", lambda ws: print(f"WebSocket opened: {ws.url}"))

page = await StealthyFetcher.async_fetch('https://example.com', page_setup=capture_websockets)
```

يمكنك جمعها مع `page_action`. تعمل `page_setup` قبل الانتقال، وتعمل `page_action` بعده.

### خيارات Cloudflare والتخفي {#cloudflare-and-stealth-options}

```python

page = StealthyFetcher.fetch('https://nopecha.com/demo/cloudflare', solve_cloudflare=True)


page = StealthyFetcher.fetch(
    'https://protected-site.com',
    solve_cloudflare=True,
    block_webrtc=True,
    real_chrome=True,
    hide_canvas=True,
    google_search=True,
    proxy='http://username:password@host:port',  # It can also be a dictionary with only the keys 'server', 'username', and 'password'.
)
```

يفعّل `solve_cloudflare` الكشف التلقائي وحل كل أنواع اختبارات Cloudflare Turnstile وInterstitial:

- اختبارات JavaScript المُدارة.
- الاختبارات التفاعلية، مثل النقر على مربعات التحقق.
- الاختبارات غير المرئية، أي التحقق التلقائي في الخلفية.

ويحل أيضًا الصفحات المخصصة التي تحتوي CAPTCHA مدمجة.

!!! notes "**ملاحظات مهمة:**"

    1. في بعض المواقع ذات الإعدادات المخصصة، قد تحتاج إلى `wait_selector` لضمان انتظار المحتوى الحقيقي بعد حل CAPTCHA. بعض المواقع حالات خاصة جدًا، بينما نحاول جعل الحل عامًا قدر الإمكان.
    2. يجب أن تكون المهلة 60 ثانية على الأقل عند استخدام أداة حل Cloudflare، لتوفير وقت كافٍ للحل.
    3. تعمل هذه الميزة مع البروكسي وخيارات التخفي الأخرى.

### أتمتة المتصفح {#browser-automation}
هنا تستخدم معرفتك بـ[واجهة Page في Playwright](https://playwright.dev/python/docs/api/class-page). تستقبل الدالة التي تمرّرها كائن الصفحة من Playwright، وتنفّذ الإجراء المطلوب، ثم تواصل أداة الجلب عملها.

تُنفّذ هذه الدالة مباشرة بعد انتظار `network_idle` إن كان مفعّلًا، وقبل انتظار `wait_selector`. لذلك يمكن استخدامها لأغراض أخرى غير الأتمتة، ويمكنك تعديل الصفحة كما تريد.

في المثال التالي، استخدمت [أحداث الفأرة](https://playwright.dev/python/docs/api/class-mouse) لتمرير الصفحة بعجلة الفأرة، ثم تحريك المؤشر:
```python
from patchright.sync_api import Page

def scroll_page(page: Page):
    page.mouse.wheel(10, 0)
    page.mouse.move(100, 400)
    page.mouse.up()

page = StealthyFetcher.fetch('https://example.com', page_action=scroll_page)
```
إذا استخدمت نسخة الجلب غير المتزامنة، يجب أن تكون الدالة غير متزامنة أيضًا.
```python
from patchright.async_api import Page

async def scroll_page(page: Page):
   await page.mouse.wheel(10, 0)
   await page.mouse.move(100, 400)
   await page.mouse.up()

page = await StealthyFetcher.async_fetch('https://example.com', page_action=scroll_page)
```

### شروط الانتظار {#wait-conditions}

```python

page = StealthyFetcher.fetch(
    'https://quotes.toscrape.com/js-delayed/',
    wait_selector='.quote',
    wait_selector_state='visible'
)
```
هذا آخر شرط انتظار للعنصر قبل إعادة الرد إذا فعّلته. مرّر محدد CSS عبر `wait_selector`، وستنتظر الأداة تحقق الحالة المحددة في `wait_selector_state`. الافتراضي `attached`، أي وجود العنصر في DOM.

بعد ذلك، إذا كان `load_dom` مفعّلًا، وهو الافتراضي، تتحقق الأداة مجددًا من تحميل JavaScript وتنفيذه، أي حالة `domcontentloaded`، أو تواصل الانتظار. وإذا فعّلت `network_idle`، تنتظر تحققه مجددًا كما شرحنا سابقًا.

يمكن الانتظار لأي من الحالات التالية ([المصدر](https://playwright.dev/python/docs/api/class-page#page-wait-for-selector)):

- `attached`: انتظار وجود العنصر في DOM.
- `detached`: انتظار غياب العنصر عن DOM.
- `visible`: انتظار مساحة عرض غير فارغة للعنصر، وعدم وجود `visibility:hidden`. العنصر بلا محتوى أو ذو `display:none` تكون مساحة عرضه فارغة، ولا يُعد ظاهرًا.
- `hidden`: انتظار انفصال العنصر عن DOM، أو فراغ مساحة عرضه، أو وجود `visibility:hidden`. هذا عكس `'visible'`.

### سجل الشبكة {#network-history}

فعّل `record_requests` في جلسة المتصفح لفحص الطلبات المكتملة عبر تحميل الصفحات والإجراءات وعلامات التبويب. يغطي السجل سياقات الجلسة، بما فيها سياقات البروكسي المؤقتة، ويحفظ الردود ككائنات `Response` من Scrapling. ابحث عن طلبات API وأخطاء HTTP وإعادة التوجيه دون إعادة إرسال الطلبات، واقرأ الترويسات والمحتوى حتى بعد إغلاق الجلسة. لا تُحفظ الطلبات الفاشلة أو غير المكتملة، لكن تُحفظ ردود HTTP المكتملة ذات الرموز 4xx و5xx.

```python
from scrapling.fetchers import StealthySession

with StealthySession(record_requests=True, max_recorded_requests=1000) as session:
    session.fetch('https://example.com', network_idle=True)

for response in session.network.search(resource_type='document', limit=None):
    print(response.meta['network_id'], response.url, response.status)
    if note := response.meta.get('body_note'):
        print(note)
    else:
        print(response.body)
        print(response.css('title::text').get())

session.network.clear()
```

تعمل الواجهة نفسها مع `AsyncStealthySession`. التسجيل معطّل افتراضيًا. حدد `record_requests=True`، ومعه `max_recorded_requests` عند الحاجة، أثناء إنشاء الجلسة.

- تعيد `session.network.search(url_pattern=None, method=None, resource_type=None, status=None, after_id=0, limit=100, include_static=True)` كائنات `Response` المحفوظة بترتيب معرّف الشبكة. تعيد `limit=None` كل النتائج المطابقة المحتفظ بها. يقبل `url_pattern` تعبيرًا منتظمًا يُطبّق عند البحث، ويُرفع خطأ حينها إذا كان غير صالح. يختار `after_id` الردود ذات المعرّفات الأكبر منه. تحتفظ `include_static=False` بطلبات XHR وfetch وأخطاء HTTP في النتائج. استخدم `True` لكل أنواع الموارد وإعادة التوجيه المحفوظة.
- تعيد `session.network.get(request_id)` ردًا محفوظًا واحدًا من نوع `Response`، أو `None` إذا لم يعد موجودًا في السجل.
- تحذف `session.network.clear()` السجل. تستمر معرّفات الطلبات في الزيادة ولا تُستخدم مرة أخرى.

يوفر كل `Response` محفوظ خصائص `.url` و`.method` و`.status` و`.headers` و`.request_headers` و`.body` من نوع bytes، ودالة `.json()` ودوال CSS وXPath مباشرة. يحتوي `.meta` على `network_id` و`resource_type` و`request_body`، والأخير bytes أو `None`. قد تكون الترويسات جزئية إذا فشلت قراءتها كاملة. هذه قراءات محلية حتى في الجلسات غير المتزامنة، فلا تستخدم await معها ولا تستدعِ `.body()`. إذا تعذر تحليل المحتوى المحفوظ، تبقى البايتات محفوظة، لكن دوال CSS وXPath تستخدم مستندًا فارغًا.

للبحث عن طلبات API حسب الرابط، استخدم `session.network.search(url_pattern=r'https://api\.example\.com/.*', limit=None)`. أضف `resource_type='fetch'` أو `resource_type='xhr'` عندما تحتاج إلى نوع واحد من الطلبات.

يقرأ المسجّل محتوى الرد ويحفظه للقيم النصية المدعومة من `Content-Type` فقط: `text/*`، والأنواع المنتهية بـ`+json` أو `+xml` بما فيها SVG، وJSON وXML وJavaScript وGraphQL وبيانات النماذج بترميز URL. تحتفظ الأنواع الثنائية وغير المعروفة والردود بلا `Content-Type` ببياناتها الوصفية دون محتوى الرد. يستمر المتصفح في تحميل الموارد كالمعتاد.

تأتي البايتات المحفوظة من Playwright، وقد تختلف عن البايتات الأصلية للخادم. يستخدم النص المسجّل UTF-8 إذا كانت البايتات صالحة بهذا الترميز، بما يطابق Playwright، وإلا يستخدم charset المعلن. لا تتغير ترويسات الرد.

المحتوى المتجاهَل أو الأكبر من الحد أو الذي تعذر قراءته يعيد `b''`، مع السبب في `response.meta.get('body_note')`. للمحتوى غير النصي تكون الرسالة `Non-text body; not saved.`. تبقى البيانات الوصفية والترويسات المتاحة محفوظة. لا توجد ملاحظة للنص المحفوظ، حتى لو كان فارغًا. وتبقى ردود HEAD والرموز 204 و205 و304 فارغة بلا ملاحظة.

دوال `search` و`get` و`clear` محلية ومتزامنة حتى في الجلسات غير المتزامنة. لا يظهر الإدخال إلا بعد تحويل الرد وحفظه. تعمل أحداث المتصفح أثناء نشاط Playwright، ويحتاج الحفظ غير المتزامن أيضًا إلى عمل حلقة الأحداث. قراءة السجل لا تنتظر اكتمال عمليات الحفظ.

إغلاق الجلسة لا ينتظر اكتمال الحفظ. قد تُفقد العمليات التي ما زالت جارية عند انتقال الصفحة أو إغلاق سياق المتصفح. تظل الردود التي حُفظت بالفعل قابلة للقراءة بعد الإغلاق.

يحتفظ السجل افتراضيًا بما يصل إلى 1,000 طلب. الحد الأقصى لمحتوى كل رد محفوظ هو 1 MiB، وللمجموع 20 MiB. تُحذف السجلات القديمة عند بلوغ الحدود. حدود المحتوى ثابتة وليست إعدادات للجلسة. تشمل هذه الحدود الإدخالات والبايتات المحتفظ بها فقط، ولا تشمل ذاكرة المتصفح الكلية، أو عمليات الحفظ المتزامنة، أو القراءة المؤقتة للمحتوى الكامل، أو HTML المحلّل، أو محتوى الطلبات.

#### الانتقال إلى v5 {#migrating-in-v5}

أُزيل `capture_xhr` و`response.captured_xhr` في v5. استخدم جلسة متصفح صريحة مع `record_requests=True`، ثم اقرأ `session.network.search(url_pattern=..., limit=None)`. يحل هذا أيضًا محل حفظ API عبر أدوات الجلب ذات الطلب الواحد، لذلك احتفظ بكائن الجلسة. تُطبّق المرشحات على السجل المحفوظ للجلسة كلها، وليس على عملية الحفظ أو طلب جلب واحد. يُحفظ محتوى الردود النصية المدعومة فقط. تعيد `search()` حتى 100 نتيجة افتراضيًا، وتعيد `limit=None` كل النتائج المطابقة المحتفظ بها دون تغيير حدود السجل.

### ترويسات المتصفح والإعدادات المحلية {#browser-headers-and-locale}

```python
page = StealthyFetcher.fetch(
    'https://example.com',
    google_search=True,
    useragent='Mozilla/5.0...',
    locale='en-US',
)
```

### مثال عام {#general-example}
```python
from scrapling.fetchers import StealthyFetcher

def scrape_dynamic_content():

    page = StealthyFetcher.fetch(
        'https://example.com/dynamic',
        network_idle=True,
        wait_selector='.content'
    )


    content = page.css('.content')

    return {
        'title': content.css('h1::text').get(),
        'items': [
            item.text for item in content.css('.item')
        ]
    }
```

### تبديل البروكسي {#proxy-rotation}

```python
from scrapling.fetchers import StealthySession, ProxyRotator


rotator = ProxyRotator([
    "http://proxy1:8080",
    "http://proxy2:8080",
    "http://proxy3:8080",
])


with StealthySession(proxy_rotator=rotator, headless=True) as session:
    page1 = session.fetch('https://example1.com')
    page2 = session.fetch('https://example2.com')


    page3 = session.fetch('https://example3.com', proxy='http://specific-proxy:8080')
```

!!! warning "تنبيه"

    تستخدم كل أدوات جلب المتصفح وجلساتها افتراضيًا سياق متصفح مستمرًا مع مجموعة علامات تبويب. لكن المتصفحات لا تسمح ببروكسي مستقل لكل علامة. لذلك عند استخدام `ProxyRotator`، تفتح الأداة تلقائيًا سياقًا مستقلًا لكل بروكسي، بعلامة تبويب واحدة لكل سياق. وعند انتهاء المهمة، تُغلق العلامة وسياقها معًا.

## متى تستخدم الأداة؟ {#when-to-use}

استخدم StealthyFetcher عندما:

- تريد تجاوز حماية كشف البوتات.
- تحتاج إلى بصمة متصفح موثوقة.
- تحتاج إلى دعم JavaScript كامل.
- تريد ميزات تخفٍّ تلقائية.
- تحتاج إلى أتمتة المتصفح.
- تتعامل مع حماية Cloudflare.
