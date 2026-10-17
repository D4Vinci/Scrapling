---
title: "الانتقال إلى v0.5"
description: "انتقل من Scrapling v0.4.15 إلى v0.5. حدّث استيرادات المتصفح، وتسجيل طلبات الشبكة، وأدوات MCP، وأوامر CLI، وإعدادات المحلّل، وسلوك Spiders."
---

# الانتقال إلى v0.5 {#migrating-to-v05}

يغطي هذا الدليل التغييرات التي تحتاج إلى مراجعتها عند الانتقال من **v0.4.15 إلى v0.5**. ويشمل واجهات API المحذوفة، والأدوات التي تغيّرت أسماؤها، والإصلاحات التي قد تغيّر نتائج الزحف أو الملفات المحفوظة.

## قائمة سريعة للانتقال {#quick-migration-checklist}

| إذا كنت تستخدم... | ما يجب تغييره |
| --- | --- |
| `DynamicFetcher` أو `DynamicSession` أو `AsyncDynamicSession` | استخدم فئة التخفي المقابلة. |
| `capture_xhr` أو `response.captured_xhr` | استخدم جلسة متصفح مع `record_requests=True` و`session.network`. |
| `keep_cdata` | احذفه من إعدادات المحلّل وFetcher. |
| `scrapling extract stealthy-fetch` أو `stealthy_fetch()` في البيئة التفاعلية | استخدم `fetch` بدلًا منه. |
| أدوات MCP | حدّث أسماء الأدوات واستدعاءات لقطات الشاشة وطريقة التعامل مع استجابة إنشاء الجلسة. |
| `response.follow()` بعد طلب POST أو طلب يحتوي على معاملات استعلام | مرّر الطريقة والاستعلام والمحتوى من جديد عند الحاجة إليها. |
| نقاط استئناف الزحف أو ذاكرة الاستجابات المؤقتة المحفوظة | ابدأ زحفًا جديدًا إذا كانت طلباتك تستخدم مدخلات بصمة الطلب التي تغيّرت. |
| `robots_txt_obey=True` | تعامل مع فشل جلب robots.txt، فهو يمنع الزحف إلى ذلك النطاق الآن. |

## الجلب بالمتصفح {#browser-fetching}

### استبدل فئات المتصفح الديناميكي {#replace-the-dynamic-browser-classes}

حُذف محرك المتصفح الذي يستخدم Playwright مباشرة. كل عمليات الجلب بالمتصفح تستخدم الآن محرك التخفي المبني على Patchright.

| واجهة API المحذوفة | البديل |
| --- | --- |
| `scrapling.DynamicFetcher` | `scrapling.StealthyFetcher` |
| `scrapling.fetchers.DynamicFetcher` | `scrapling.fetchers.StealthyFetcher` |
| `scrapling.fetchers.chrome.PlayWrightFetcher` | `scrapling.fetchers.StealthyFetcher` |
| `scrapling.fetchers.DynamicSession` | `scrapling.fetchers.StealthySession` |
| `scrapling.fetchers.AsyncDynamicSession` | `scrapling.fetchers.AsyncStealthySession` |

حُذفت وحدة `scrapling.fetchers.chrome` والوحدة الخاصة `_browsers._controllers`. استخدم الاستيرادات العامة المذكورة أعلاه.

**قبل:**

```python
from scrapling.fetchers import DynamicFetcher

page = DynamicFetcher.fetch("https://example.com", headless=True)
```

**الآن:**

```python
from scrapling.fetchers import StealthyFetcher

page = StealthyFetcher.fetch("https://example.com", headless=True)
```

للجلسات، استبدل `DynamicSession` بـ`StealthySession`، أو `AsyncDynamicSession` بـ`AsyncStealthySession`. طبّق التغيير نفسه في طريقة `configure_sessions()` داخل Spider. تظل طريقة استخدام `fetch()` و`async with` كما هي.

إذا كانت دوال callback تستورد أنواع المتصفح أو تلتقط أخطاءه، غيّر `playwright.sync_api` إلى `patchright.sync_api`، أو `playwright.async_api` إلى `patchright.async_api`. يشمل ذلك `Page` و`Locator` و`Error` و`TimeoutError`.

ينفّذ Patchright كود JavaScript في سياق معزول افتراضيًا. إذا كانت دالة callback تقرأ متغيرات JavaScript الخاصة بالصفحة، استخدم `page.evaluate(..., isolated_context=False)`.

يتغيّر سلوك المتصفح إلى جانب اسم الاستيراد. راجع خيارات المتصفح وإعدادات البصمة. ما زال حل Cloudflare يتطلب `solve_cloudflare=True`؛ فهو غير مفعّل افتراضيًا. كذلك، يضيف `extra_flags` الآن إلى خيارات التخفي المدمجة بدلًا من استبدالها.

راجع [الجلب بالمتصفح](fetching/stealthy.md) لمعرفة الخيارات الحالية.

### استبدل التقاط XHR بسجل شبكة الجلسة {#replace-xhr-capture-with-session-network-history}

حُذف المعامل `capture_xhr` والخاصية `Response.captured_xhr`. احذف المعامل حتى لو كانت قيمته `None`. لم تعد عملية الجلب المنفردة تُرفق قائمة XHR باستجابتها.

يجب أن تحذف التكاملات المخصصة التي تستدعي `ResponseFactory.from_playwright_response()` أو `ResponseFactory.from_async_playwright_response()` المعامل `xhr_captured` أيضًا. مرّر `collect_history` باسمه لتجنب أثر تغيّر ترتيب المعاملات الموضعية.

**قبل:**

```python
from scrapling.fetchers import StealthyFetcher

page = StealthyFetcher.fetch("https://example.com", capture_xhr="/api/")
for response in page.captured_xhr:
    print(response.url, response.body)
```

**الآن:**

```python
from scrapling.fetchers import StealthySession

with StealthySession(record_requests=True) as session:
    page = session.fetch("https://example.com", network_idle=True)
    for response in session.network.search(url_pattern=r"/api/", limit=None):
        print(response.url, response.body)
```

استخدم `AsyncStealthySession` و`await session.fetch(...)` للكود غير المتزامن. لا تحتاج قراءة `session.network` إلى `await`.

هناك بعض الفروق المهمة:

- اضبط `record_requests=True` عند إنشاء الجلسة. هذا إعداد للجلسة، وليس لكل عملية جلب.
- يخص السجل **الجلسة كلها**، بما فيها علامات التبويب وعمليات تحميل الصفحات والإجراءات. استخدم `after_id` أو المرشحات أو `session.network.clear()` إذا كنت تحتاج إلى نطاق أصغر.
- انقل التعبير النمطي القديم في `capture_xhr` إلى `url_pattern` عند البحث في السجل.
- تعيد `search()` كائنات `Response` محفوظة. اقرأ `.url` أو `.status` أو `.headers` أو `.body` أو `.json()` مباشرة. تجد معرّف التسجيل ونوع المورد والمحتوى المرسَل في `response.meta["network_id"]` و`response.meta["resource_type"]` و`response.meta["request_body"]`.
- يشمل سجل Python كل أنواع الموارد افتراضيًا. استخدم `resource_type="xhr"` أو `resource_type="fetch"` لاختيار أحدهما، أو `include_static=False` لطلبات XHR/fetch مع أخطاء HTTP.
- تعيد `search()` ما يصل إلى 100 نتيجة افتراضيًا. مرّر `limit=None` للحصول على كل النتائج المحفوظة. تحتفظ الجلسات بما يصل إلى 1,000 طلب افتراضيًا؛ غيّر ذلك باستخدام `max_recorded_requests`.
- تُحفظ الطلبات المكتملة فقط. يقتصر تسجيل المحتوى على أنواع المحتوى النصي المدعومة، بحد 1 MiB لكل استجابة و20 MiB لإجمالي بيانات المحتوى المحفوظة. قد تُحذف السجلات الأقدم عند الوصول إلى الحدود. راجع `response.meta.get("body_note")` لمعرفة سبب تخطي المحتوى.
- لا تنتظر قراءة السجل أو إغلاق الجلسة عمليات التسجيل المعلّقة. انتظر البيانات التي تحتاج إليها قبل قراءتها. يظل سجل Python المحفوظ قابلًا للقراءة بعد إغلاق الجلسة.

راجع [سجل الشبكة](fetching/stealthy.md#network-history) لمعرفة المرشحات والحدود.

## إعدادات المحلّل {#parser-settings}

### احذف `keep_cdata` {#remove-keep_cdata}

حُذف `keep_cdata` من `Selector` وإعدادات Fetcher والإعدادات التي تعيدها `display_config()`. احذفه من استدعاءات المحلّل المباشرة و`Fetcher.configure(...)` وقواميس `selector_config` التي تمرّرها إلى Fetchers أو التكاملات.

**قبل:**

```python
from scrapling import Selector

page = Selector("<p>Hello</p>", keep_cdata=True)
```

**الآن:**

```python
from scrapling import Selector

page = Selector("<p>Hello</p>")
```

لا يوجد إعداد بديل. لم يكن هذا الإعداد يؤثر في ناتج محلّل HTML. إذا كنت تمرّر خيارات المحلّل حسب ترتيبها دون أسماء، فاحذف المعامل القديم `keep_cdata`، ومرّر `adaptive` وخيارات التخزين بأسمائها.

## سطر الأوامر والبيئة التفاعلية {#command-line-and-interactive-shell}

### استخدم `fetch` لطلبات المتصفح {#use-fetch-for-browser-requests}

تحتوي CLI الآن على أمر واحد للمتصفح: `scrapling extract fetch`. ويستخدم `StealthyFetcher`.

**قبل:**

```bash
scrapling extract stealthy-fetch "https://example.com" page.md
```

**الآن:**

```bash
scrapling extract fetch "https://example.com" page.md
```

إذا كنت تستخدم `scrapling extract fetch` بالفعل، يظل اسم الأمر كما هو، لكن محركه يتغيّر من `DynamicFetcher` إلى `StealthyFetcher`. أصبحت خيارات مثل `--solve-cloudflare` تابعة لـ`fetch`.

في `scrapling shell`، استبدل `stealthy_fetch(...)` بـ`fetch(...)`. يستدعي الاختصار الحالي `fetch(...)` الآن `StealthyFetcher.fetch`. لم تعد الفئات الديناميكية تُضاف إلى نطاق أسماء البيئة التفاعلية.

### اقرأ ملفات Markdown والنص بترميز UTF-8 {#read-markdown-and-text-files-as-utf-8}

تكتب أوامر الاستخراج و`Convertor.write_content_to_file()` الآن ملفات `.md` و`.txt` بترميز **UTF-8**، بصرف النظر عن ترميز الصفحة الأصلية. حدّث أي كود يقرأ تلك الملفات بترميز الصفحة الأصلي. ما زال ناتج `.html` يستخدم `page.encoding`.

يحتوي Markdown المستخرج من عدة عناصر محددة الآن على أسطر فارغة بين العناصر. ينطبق هذا على `Response.markdown()` وملفات Markdown الناتجة. حدّث الاختبارات التي تقارن الناتج حرفيًا أو قيم التجزئة المحفوظة التي كانت تعتمد على النص المتصل.

## خادم MCP {#mcp-server}

حدّث التعليمات المحفوظة وقوائم الأدوات المسموح بها والدوال الوسيطة وتعريفات أدوات عميل MCP. أعد تشغيل عميل MCP أو توصيله بعد تحديث الخادم كي يقرأ الأدوات الحالية.

### حدّث أسماء الأدوات والاستدعاءات المجمّعة {#update-tool-names-and-bulk-calls}

| أداة v0.4.15 | البديل في v0.5 |
| --- | --- |
| `fetch`, `stealthy_fetch` | `browser_fetch_once` |
| `open_session` | `browser_open` |
| `session_fetch` | `browser_fetch` |
| `screenshot` | `browser_screenshot` |
| `bulk_fetch`, `bulk_stealthy_fetch` | استدعاء واحد لـ`browser_fetch_once` لكل URL، أو استدعاءات متكررة لـ`browser_fetch` عبر جلسة مفتوحة |
| `bulk_get` | استدعاء واحد لـ`make_request` أو `session_make_request` لكل URL |

حُذفت كل أدوات العمليات المجمّعة. تعيد أدوات جلب URL واحد كائن `ResponseModel` واحدًا يحتوي على `status` و`content` و`url`، وليس قائمة استجابات. ما زال `content` نفسه قائمة نصوص.

تستخدم كل أدوات متصفح MCP الآن محرك التخفي. احذف `session_type` من استدعاءات `browser_open`؛ لم يعد هناك خيار للمتصفح الديناميكي. تحتوي نتيجته على `session_type="stealthy"`. ما زالت جلسات HTTP تستخدم `open_request_session` وتعيد `session_type="static"`.

يجب أن تتوقف تكاملات Python أيضًا عن استيراد `BrowserSessionType`، فقد حُذف. يقبل `SessionType` الآن `"stealthy"` و`"static"` فقط.

يجب تشغيل الاستدعاءات عبر جلسة متصفح واحدة بالترتيب لأنها تشترك في صفحة. أغلق الجلسات باستخدام `close_session` عند الانتهاء.

### اقرأ الإعدادات عبر `list_sessions` {#read-settings-through-list_sessions}

تعيد `browser_open` و`open_request_session` الآن ما يلي فقط:

```json
{
  "session_id": "my-session",
  "session_type": "stealthy"
}
```

لم تعد نتيجة الإنشاء تتضمن `created_at` أو `is_alive` أو `settings` أو `message`. استدعِ `list_sessions` للحصول على الحقول الثلاثة الأولى. حُذفت رسالة التأكيد `message`. يجب أيضًا تغيير الكود الذي كان يفترض أن `SessionCreatedModel` يحتوي على كل حقول `SessionInfo`.

### اجلب الصفحة قبل أخذ لقطة شاشة {#fetch-before-taking-a-screenshot}

تلتقط `browser_screenshot` **الصفحة الحالية دون إعادة تحميلها**. لم تعد تقبل URL أو خيارات التنقل والانتظار القديمة: `wait` و`wait_selector` و`wait_selector_state` و`network_idle`.

استخدم هذا الترتيب:

1. استدعِ `browser_open`.
2. استدعِ `browser_fetch` مع URL وأي خيارات لتحميل الصفحة.
3. عند الحاجة، استدعِ `browser_actions` للتفاعل مع الصفحة أو انتظار المحتوى.
4. استدعِ `browser_screenshot` مع معرّف الجلسة.
5. استدعِ `close_session` عند الانتهاء.

مثلًا، معاملات لقطة شاشة للصفحة كاملة هي:

```json
{
  "session_id": "my-session",
  "full_page": true
}
```

يحدد `timeout` في هذه الأداة الآن مهلة أخذ اللقطة فقط. لا تحمّل الأداة صفحة. لأخذ لقطة لعنصر، استخدم `selector` أو `ref`، ولا تضبط `full_page=true`.

ما زالت لقطات الشاشة تعيد كتل محتوى للصور والنص، مع URL الصفحة الحالية في كتلة النص. ولا تعيد `ResponseModel` الخاص بالجلب.

راجع [دليل MCP](ai/mcp-server.md) و[مرجع API](api-reference/mcp-server.md) لمعرفة بنية المدخلات والنتائج كاملة.

## Spiders وطلبات HTTP {#spiders-and-http-requests}

### مرّر بيانات الطلب من جديد عند متابعة رابط {#pass-request-data-again-when-following-a-link}

لم تعد `response.follow()` تنسخ `method` أو `params` أو `data` أو `json` أو `files` أو `multipart` من الطلب السابق. وتحذف أيضًا ترويسات `Content-Length` الموروثة من `headers` و`extra_headers`.

يبدأ الرابط الذي تتابعه الآن بطلب GET عادي ما لم تمرّر بيانات الطلب صراحة. ما زالت الإعدادات المشتركة الأخرى، مثل الجلسة وProxy ودوال callback، تتبع قواعد التوريث الحالية.

إذا كان كودك القديم يعتمد على بيانات POST الموروثة، غيّر:

```python
yield response.follow("/next")
```

إلى:

```python
yield response.follow("/next", method="POST", json={"page": 2})
```

مرّر `params` صراحة أيضًا عندما يحتاج إليها الطلب التالي. اترك عميل HTTP يحسب `Content-Length` الجديد.

### راجع بصمات الطلبات وحالة الزحف المحفوظة {#check-request-fingerprints-and-saved-crawl-state}

بصمة الطلب هي المفتاح المستخدم لاكتشاف الطلبات المكررة والعثور على الاستجابات المخزنة مؤقتًا. تتعامل مدخلاتها الآن مع ثلاث حالات بطريقة مختلفة:

- تُدمج `params` في URL قبل إنشاء المفتاح. لم تعد الطلبات إلى URL نفسه بمعاملات استعلام مختلفة تُعد مكررة افتراضيًا.
- تُحفظ محتويات JSON مثل `{}` و`[]` و`false` و`0` و`""` في المفتاح. لم تعد تشترك في مفتاح الطلب الذي لا يحتوي على محتوى. ما زالت `None` تعني عدم وجود محتوى JSON.
- عند ضبط `fp_include_headers=True`، لم يعد تغيير ترتيب إدراج الترويسات وحده يغيّر المفتاح.

إذا كان الزحف يستخدم هذه المدخلات، أنهِه قبل الترقية أو ابدأ زحفًا جديدًا بنقطة استئناف جديدة ومجلد جديد لذاكرة الاستجابات المؤقتة. قد تختلف المفاتيح القديمة المحفوظة عن المفاتيح الجديدة. هذا تغيير في هوية الطلب، وليس في تنسيق ملف نقطة الاستئناف.

يكتب وضع التطوير الآن الاستجابات في الذاكرة المؤقتة فقط بعد التحقق من حظر الاستجابة. لا تُحفظ صفحات الحظر كنتائج ناجحة في الذاكرة المؤقتة. لا تُنظف الملفات الموجودة تلقائيًا؛ احذف السجلات القديمة إذا كنت قد خزّنت صفحة تحقق سابقًا.

تحتفظ عمليات الزحف الفاشلة الآن بملفات نقاط الاستئناف. راجع كود التنظيف إذا كان يفترض اختفاء تلك الملفات بعد الخطأ. راجع [الإيقاف والاستئناف](spiders/advanced.md#pause-resume) و[وضع التطوير](spiders/advanced.md#development-mode).

### راجع حالات فشل robots.txt {#check-robotstxt-failures}

عند ضبط `robots_txt_obey=True`، تُمنع الطلبات إلى النطاق إذا حدث استثناء أثناء جلب robots.txt أو كانت حالة الاستجابة غير HTTP 200 أو 4xx. كانت هذه الحالات تسمح بالزحف سابقًا. ما زالت HTTP 200 توفّر القواعد، وHTTP 4xx تسمح بالوصول.

تُخزن النتيجة طوال عملية الزحف. أصلح مشكلة الوصول إلى robots.txt وابدأ زحفًا جديدًا؛ لن تعيد الطلبات اللاحقة في عملية الزحف نفسها محاولة الجلب الفاشلة. لا يغيّر ذلك القيمة الافتراضية `robots_txt_obey=False`.

### راجع قيود الروابط ودوال callback لخرائط الموقع {#check-link-restrictions-and-sitemap-callbacks}

- يعيد قيد `LinkExtractor` الذي لا يطابق أي عنصر الآن قائمة بلا روابط. لم يعد يرجع إلى الصفحة كلها. أصلح تعبير `restrict_css` أو `restrict_xpath` إذا أصبح الزحف يعثر على روابط أقل.
- يمكن للقيد الآن اختيار عنصر الرابط نفسه، وليس عنصرًا أبًا فقط. قد يضيف ذلك روابط لم تكن تظهر سابقًا. راجع مجموعات عناوين URL المتوقعة.
- يرسل `SitemapSpider` الآن عناوين URL للصفحات إلى `parse()` عند عدم وجود قواعد، أو عندما تحتوي قاعدة مطابقة على `callback=None`. لم يعد يرسل صفحات HTML هذه إلى محلّل خريطة الموقع مرة أخرى. اكتب `parse()` لهذه الحالات واحذف الحلول البديلة التي عالجت التوجيه القديم.
- تُحذف علامة ترتيب بايتات Unicode من بداية robots.txt وتغذيات CSV. يعمل الآن أول توجيه في robots، ولم يعد عنوان أول عمود CSV يبدأ بـ`\ufeff`. إذا حددت `headers` مخصصة، تُحذف العلامة من قيمة أول حقل بدلًا من ذلك. حدّث الكود الذي كان يعالج هذه البادئة المخفية. تُتخطى أيضًا تعليقات XML وتعليمات المعالجة في خرائط الموقع بدلًا من التسبب في فشل التحليل.

### راجع بيانات النماذج والترويسات وJSON في CLI {#check-form-data-headers-and-cli-json}

توسّع بيانات النماذج في القواميس الآن قيم القوائم وtuples إلى مفاتيح متكررة. مثلًا، ترسل `data={"tag": ["a", "b"]}` القيمة `tag=a&tag=b`. لا يُرسل المفتاح إذا كانت قيمته قائمة فارغة. تُضاف الترويسة الافتراضية `Content-Type: application/x-www-form-urlencoded` إذا لم توفّرها.

إذا كنت تحتاج إلى تنسيق إرسال مختلف، مرّر نصًا أو bytes مرمّزة صراحة. تحتفظ `json` و`content` الخام وعمليات رفع multipart بطريقة معالجة محتواها. قيم `None` **لا تُحذف** من بيانات النماذج أو معاملات الاستعلام؛ وتظل النص `None`.

تتجاوز ترويسات HTTP لكل طلب الآن ترويسات الجلسة بصرف النظر عن حالة الأحرف. تستبدل ترويسة الطلب المسماة `authorization` ترويسة الجلسة `Authorization` بدلًا من إرسال الاثنتين. احذف الكود الذي كان يعالج تكرار أسماء الترويسات.

تُرسل الآن قيم JSON في CLI مثل `{}` و`[]` و`false` و`0` و`""` بدلًا من حذفها بصمت. كذلك، تطبّق `curl2fetcher()` الآن User-Agent المحدد بخيار curl ‏`-A`، وتمرّر Proxy المحدد بخيار `-x` بشكل صحيح كنص URL. ما زالت ترويسة curl الصريحة `-H 'User-Agent: ...'` لها الأولوية على `-A`.

## تغييرات أخرى في الناتج يجب مراجعتها {#other-output-changes-to-check}

لا تحذف هذه الإصلاحات واجهات API، لكنها قد تغيّر النتائج المحفوظة واختبارات التطابق التام للناتج:

- تتضمن محددات CSS وXPath المُنشأة الآن `:nth-of-type(1)` أو `[1]` عند الحاجة إلى تحديد أول عنصر بين عدة عناصر شقيقة لها الوسم نفسه. حدّث نصوص المحددات المتوقعة؛ لا تحذف علامة الموضع الجديدة.
- يحتفظ محتوى AI المنظّف الآن بالعناصر المرئية ذات القيم مثل `opacity:0.95`، ويزيل العناصر التي تخفيها أشكال إضافية من الأنماط المضمنة وعناصر `<slot hidden>`، ويزيل كل وسوم الضوضاء المطابقة حتى عندما تكون متداخلة. راجع التطابق التام لناتج Markdown والنص وHTML المنظّف.
- يقرأ تحويل استجابات المتصفح الآن تعريفات charset التي تختلف فيها حالة الأحرف أو تحتوي على مسافات أو قيم بين علامتي اقتباس، مثل `text/plain; CHARSET = "iso-8859-15"`. تستخدم الاستجابات غير المكتوبة بصيغة HTML التي تحمل هذه الترويسات الآن الترميز المحدد بدلًا من الرجوع إلى UTF-8. راجع النص المستخرج من تلك الاستجابات بعد فك ترميزه.

## تحقق من الترقية {#verify-your-upgrade}

شغّل زحفًا صغيرًا قبل المهمة الكاملة. تحقق من البيانات المستخرجة وعناوين URL التي يتابعها الزحف ومحتويات الطلبات المرسلة وترميز الملفات المحفوظة وأي سلوك تعتمد عليه للذاكرة المؤقتة أو نقاط الاستئناف. لتكاملات MCP، راجع مدخلات الأدوات والبيانات التي تعيدها وفق البنية الحالية.

لتغييرات الإصدارات الأقدم، راجع [سجل التغييرات](changelog.md).
