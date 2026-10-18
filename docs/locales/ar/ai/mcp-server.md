---
title: "خادم Scrapling MCP: الإعداد وطرق استخراج البيانات"
description: "اربط عميل ذكاء اصطناعي بـ Scrapling للجلب عبر HTTP والمتصفح. استخدم الجلسات وحالة تسجيل الدخول المحفوظة والإجراءات والاستخراج المحدد وسجل API."
---

# دليل خادم Scrapling MCP {#scrapling-mcp-server-guide}

<iframe width="560" height="315" src="https://www.youtube.com/embed/NHwWEiTOoPQ" title="مشغّل فيديو YouTube" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>

**خادم Scrapling MCP** ميزة جديدة توفر قدرات Scrapling القوية لاستخراج بيانات الويب مباشرة داخل مساعد الذكاء الاصطناعي أو الوكيل الذي تفضّله. يتيح هذا التكامل جلب المواقع واستخراج بياناتها وتجاوز الحماية من البوتات بالمحادثة، عبر واجهة Claude أو أي واجهة تدعم MCP.

## الميزات {#features}

يوفر خادم Scrapling MCP ست عشرة أداة لاستخراج بيانات الويب والتفاعل مع المتصفح. تجلب أدوات الاستخدام الواحد رابطًا واحدًا، ثم تغلق المتصفح أو العميل الذي فتحته. أما أدوات الجلسات فتحتفظ بـ cookies والإعدادات بين الاستدعاءات، ليواصل الذكاء الاصطناعي إجراءات المتصفح في التبويب نفسه ويفحص سجل الشبكة.

### أدوات الاستخدام الواحد {#one-shot-tools}

#### 🚀 استخراج سريع عبر HTTP {#basic-http-scraping}

- **`make_request`**: طلبات HTTP سريعة بأي طريقة، مثل GET وPOST وPUT وDELETE، مع محاكاة بصمة المتصفح وتوليد ترويسات متصفح حقيقية تطابق إصدار TLS، ودعم HTTP/3، وغير ذلك!

#### 🔒 استخراج بمتصفح Stealthy {#stealth-browser-scraping}

- **`browser_fetch_once`**: شغّل JavaScript واستخرج بيانات الصفحات الديناميكية باستخدام متصفح Stealthy. يدعم تعديل البصمة وتجاوز Cloudflare Turnstile وInterstitial، والتحكم في المتصفح والطلب!

### أدوات الجلسات {#session-tools}

#### 🔌 إدارة الجلسات {#session-management}

- **`browser_open`**: ينشئ جلسة متصفح Stealthy مستمرة تظل مفتوحة عبر عدة استدعاءات لـ `browser_fetch`، لتجنب تكلفة تشغيل متصفح جديد كل مرة. تحفظ إعدادات المتصفح وتُرجع `session_id` و`session_type` فقط. استخدم `list_sessions` للاطلاع على `settings` الفعلية، وهي فارغة في جلسات CDP.
- **`open_request_session`**: ينشئ جلسة HTTP مستمرة دون متصفح، لاستخدامها مع `session_make_request`. تحتفظ بـ cookies والاتصالات وبصمة المتصفح `impersonate` بين الطلبات. تُرجع `session_id` و`session_type` فقط، ويكون النوع `static`. استخدم `list_sessions` للاطلاع على `settings` الفعلية.
- **`close_session`**: يغلق جلسة مستمرة، سواء للمتصفح أو للطلبات، ويحرر مواردها.
- **`list_sessions`**: يعرض كل الجلسات النشطة مع تفاصيلها و`settings`.

#### حالة المتصفح {#browser-state}

- **`browser_save_state`**: يحفظ cookies وlocal storage وIndexedDB في ملف JSON متوافق مع Playwright، لتتمكن من إعادة استخدام حالة تسجيل الدخول بعد انتهاء جلسة المتصفح. يحل الحفظ محل الملف إذا كان موجودًا.
- **`browser_load_state`**: يستعيد ملفًا محفوظًا داخل جلسة متصفح مفتوحة، حتى قبل أول تحميل لصفحة. يستبدل الحالة المخزنة الحالية دون إغلاق التبويبات الموجودة أو تغيير صفحاتها. اجلب الصفحة أو أعد تحميلها لاستخدام تسجيل الدخول المستعاد.

تُحفظ ملفات الحالة على الجهاز الذي يشغّل خادم MCP. ولا تشمل `sessionStorage` أو التبويبات المفتوحة أو إعدادات المتصفح.

#### 🎯 الجلب عبر جلسة {#fetching-through-a-session}

- **`browser_fetch`**: يشغّل JavaScript ويستخرج بيانات رابط واحد عبر جلسة متصفح Stealthy مفتوحة، مع تعديل البصمة وتجاوز Cloudflare Turnstile وInterstitial. ويمكنه أيضًا أخذ وصف منظم للصفحة يشمل مراجع العناصر ومواضعها وأحجامها، لمساعدة الذكاء الاصطناعي على تحديد عناصر التحكم وتخطيط حركة الفأرة.
- **`session_make_request`**: يرسل طلبات HTTP سريعة بأي طريقة، مثل GET وPOST وPUT وDELETE، مع محاكاة بصمة المتصفح والترويسات المطابقة ودعم HTTP/3. يعيد استخدام cookies والاتصالات وبصمة المتصفح عبر جلسة مفتوحة باستخدام `open_request_session`.

#### 📸 لقطات الشاشة {#screenshots}

- **`browser_screenshot`**: يلتقط الصفحة الحالية أو عنصرًا محددًا بصيغة PNG أو JPEG دون إعادة تحميلها. افحص الحقول المملوءة والقوائم المفتوحة والرسوم وبطاقات النتائج، مع تقليل المحتوى غير المرتبط عند تصوير عنصر واحد. يدعم الجزء المرئي والصفحة الكاملة والعنصر الواحد، مع إمكانية ضبط جودة JPEG. تُرجع اللقطة ككتلة صورة فعلية يستطيع النموذج رؤيتها مباشرة.

#### محتوى الصفحة الحالية {#current-page-content}

- **`browser_extract`**: يقرأ الصفحة الحالية أو عنصرًا واحدًا كوصف منظم للذكاء الاصطناعي، أو HTML أو Markdown أو نص، دون إعادة تحميل الصفحة. استخرج النتائج بعد ملء النماذج أو تحميل مزيد من المحتوى. يتضمن الوصف أدوار العناصر وأسماءها ومراجعها ومواضعها وأحجامها لاستخدامها في إجراءات لاحقة. ويُرجع البحث باستخدام regex أسطر الوصف المطابقة مع السياق القريب والعناصر الآباء.

#### إجراءات المتصفح {#browser-actions}

- **`browser_actions`**: يجمع حركات الفأرة وملء الحقول واختصارات لوحة المفاتيح والرد على مربعات الحوار والانتظار في استدعاء واحد. اقبل تنبيهات المتصفح ورسائل التأكيد أو ارفضها، أو أدخل نصًا في مربعات الطلب. مثلًا: املأ مربع بحث، وأرسل البحث، وانتظر النتائج، ثم افتح نتيجة. يستطيع الذكاء الاصطناعي جمع الخطوات المعروفة، وأخذ وصف الصفحة بشكل منفصل عندما يحتاج إلى فحص تغيير فيها. وهذا يجنّب الحاجة إلى الرجوع للوكيل بين كل خطوة والخطوة التالية، ويساعد مع القوائم التي تختفي سريعًا وعناصر التحكم الأخرى التي تحتاج إلى إجراء تالٍ سريع.

    أظهر القوائم والتلميحات التي تظهر عند مرور الفأرة، وانقر الأزرار والروابط، أو حرّك الفأرة فوق لوحة داخلية ومرّرها رأسيًا أو أفقيًا. تدعم الحركة والنقر المحددات ومراجع وصف الصفحة والإحداثيات، مع الانتظار التلقائي وتمرير العنصر إلى الجزء المرئي عند استهداف عنصر. كما تدعم الحركة بالإحداثيات على عدة خطوات، والنقر بالزر الأيسر والأيمن والأوسط، والنقر المزدوج.

    استهدف الحقول في أي مكان باستخدام المحددات أو مراجع وصف الصفحة. املأ النصوص، وحدّد مربعات الاختيار أو ألغِها، واختر أزرار radio، وحدّد خيارًا أو أكثر من القوائم المنسدلة الأصلية حسب النص الظاهر. يمكن للنص أن يستبدل المحتوى الحالي أو يمسحه أو يُضاف عند موضع المؤشر. تستطيع اختصارات لوحة المفاتيح تحديد النص وحذفه ونقل التركيز وإرسال النماذج وإغلاق القوائم. يكتب الوضع البطيء حرفًا واحدًا في كل مرة، مع فترات توقف عشوائية بين الأحرف وكل الإجراءات.

    انتظر ظهور النتائج أو اختفاء طبقات التحميل أو وقوع أحداث تحميل الصفحة قبل الإجراء التالي. تدعم الأداة أيضًا فترات انتظار ثابتة وانتظار استقرار نشاط الشبكة.

#### JavaScript {#javascript}

- **`browser_evaluate`**: يشغّل JavaScript في الصفحة الحالية لاستخراج بيانات مخصصة، وإجراء حسابات، وتنفيذ مهام خاصة بالصفحة. يستطيع الذكاء الاصطناعي جمع بيانات عدة عناصر أو قراءة حالة التطبيق أو تحديث محتوى الصفحة. يدعم السكربتات غير المتزامنة ويُرجع نتائجها بصيغة JSON.

#### سجل الشبكة {#network-history}

- **`browser_network_requests`**: يبحث عن الطلبات المكتملة عبر التبويبات وتحميلات الصفحات وإجراءات المتصفح. اكتشف استدعاءات API التي توفر بيانات الصفحة، وافحص أخطاء HTTP، وتتبّع عمليات إعادة التوجيه المحفوظة. تُخفى الموارد الثابتة افتراضيًا لتقليل حجم النتائج. تُرجع تفاصيل الطلبات بصيغة JSON، مع تقسيم السجلات الطويلة إلى صفحات.
- **`browser_network_request`**: يفحص ملخص طلب مسجل واحد أو ترويساته أو بياناته المُرسلة أو نص استجابته بصيغة JSON منظمة. يُرجع الجزء المحدد كاملًا دون تحميل الصفحة أو إرسال الطلب مجددًا. تبقى الاستجابات المحفوظة متاحة بعد تغير الصفحة. تحدّ حدود الحجم من حجم السجل، وتوضح ملاحظة سبب عدم حفظ المحتوى غير النصي أو الكبير أو غير القابل للقراءة. اقرأ التفاصيل التي تحتاجها قبل إغلاق جلسة MCP.

تُقرأ أجسام الاستجابات وتُحفظ فقط عندما تكون قيمة `Content-Type` من الأنواع النصية المدعومة، مثل HTML وJSON وXML وJavaScript. أما الأنواع الثنائية أو المفقودة أو غير المعروفة، فتُحفظ بيانات الطلب وترويساته دون قراءة جسم الاستجابة أو حفظه. ويواصل المتصفح تحميل الموارد كالمعتاد.

تُحفظ الطلبات المكتملة فقط، بما فيها استجابات HTTP من فئتي 4xx و5xx. تُستبعد الطلبات الفاشلة وغير المكتملة. تظهر السجلات بعد انتهاء التقاطها، ولا تنتظر قراءة السجل أو إغلاق الجلسة اكتمال الالتقاط. قد تُستبعد عمليات الالتقاط التي ما زالت جارية عند الانتقال أو الإغلاق. تأتي البايتات المحفوظة من المتصفح، وقد تختلف عن بايتات الخادم. يتبع النص المسجل فك ترميز UTF-8 في Playwright عندما يكون صالحًا، ويستخدم الترميز المعلن كبديل.

### Shadow DOM {#shadow-dom}

اضبط `pierce_shadow=true` في `browser_fetch_once` أو في كل استدعاء لـ `browser_fetch` لتضمين محتوى Shadow DOM المفتوح. قيمته الافتراضية `false`. راجع [Shadow DOM](../fetching/stealthy.md#shadow-dom) لأمثلة المحددات وحدود الدعم.

تستطيع محددات المتصفح أيضًا استهداف العناصر داخل Shadow DOM المغلق والتفاعل معها.

### القدرات الرئيسية {#key-capabilities}

- **استخراج المحتوى بذكاء**: حوّل الصفحات والعناصر إلى Markdown أو HTML، أو استخرج نسخة نظيفة من النص.
- **دعم محددات CSS**: استخدم محرك Scrapling لاستهداف عناصر معينة بدقة قبل إرسال المحتوى إلى الذكاء الاصطناعي.
- **تجاوز الحماية من البوتات**: تعامل مع Cloudflare Turnstile وInterstitial وغيرها من وسائل الحماية.
- **دعم proxies**: استخدمها لإخفاء هويتك أو استهداف موقع جغرافي.
- **محاكاة المتصفح**: حاكِ المتصفحات الحقيقية عبر بصمة TLS وترويسات حقيقية تطابق الإصدار، وغير ذلك.
- **استمرار الجلسات**: أعد استخدام جلسات المتصفح عبر عدة طلبات لتحسين الأداء.
- **حظر الإعلانات**: تحظر جميع أدوات المتصفح تلقائيًا الطلبات إلى نحو 3,500 نطاق معروف للإعلانات والتتبع، لتوفير الرموز وتسريع تحميل الصفحات.
- **الحماية من حقن التعليمات**: يزيل المحتوى المخفي تلقائيًا، مثل العناصر المخفية بأنماط مباشرة وaria-hidden وعناصر slot المخفية والمحارف عديمة العرض وتعليقات HTML ووسوم template، التي قد تُستخدم لحقن تعليمات ضارة.

## التثبيت {#installation}

ثبّت Scrapling مع دعم MCP، ثم تأكد من تثبيت متطلبات المتصفح.

```bash
# Install Scrapling with MCP server dependencies
pip install "scrapling[ai]"

# Install browser dependencies
scrapling install
```

أو استخدم صورة Docker مباشرة من سجل Docker:

```bash
docker pull pyd4vinci/scrapling
```

أو نزّلها من سجل GitHub:

```bash
docker pull ghcr.io/d4vinci/scrapling:latest
```

## إعداد خادم MCP {#setting-up-the-mcp-server}

نشرح هنا إضافة خادم Scrapling MCP إلى [Claude Desktop](https://claude.ai/download) و[Claude Code](https://www.anthropic.com/claude-code)، لكن الفكرة نفسها تنطبق على أي مساعد يدعم MCP:

!!! note "ملاحظة:"

    أُضيف أمر `scrapling-mcp` المستخدم أدناه في الإصدار 0.4.13 كاختصار مباشر لـ `scrapling mcp`، لتسهيل إضافة Scrapling إلى سجلات MCP والعملاء الذين يتوقعون أمرًا واحدًا. إذا كنت تستخدم إصدارًا أقدم، فاستخدم `scrapling` مع `mcp` كأول معامل.

### Claude Desktop {#claude-desktop}

1. افتح Claude Desktop.
2. انقر قائمة ☰ في أعلى اليسار، ثم Settings، ثم Developer، ثم Edit Config.
3. أضف إعداد خادم Scrapling MCP:

```json
"ScraplingServer": {
  "command": "scrapling-mcp"
}
```

إذا كان هذا أول خادم MCP تضيفه، فاجعل محتوى الملف كما يلي:

```json
{
  "mcpServers": {
    "ScraplingServer": {
      "command": "scrapling-mcp"
    }
  }
}
```

وفقًا لـ [المقال الرسمي](https://modelcontextprotocol.io/quickstart/user)، تُنشئ هذه الخطوة ملف إعداد جديدًا إذا لم يكن موجودًا، أو تفتح الملف الحالي. يوجد الملف في:

1. **MacOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
2. **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

للتأكد من عمل الإعداد، استخدم المسار الكامل للملف التنفيذي `scrapling-mcp`:

1. **MacOS**: `which scrapling-mcp`
2. **Windows**: `where scrapling-mcp`

على جهاز Mac الخاص بي، كانت النتيجة `/Users/<MyUsername>/.venv/bin/scrapling-mcp`، لذا استخدمت الإعداد التالي:

```json
{
  "mcpServers": {
    "ScraplingServer": {
      "command": "/Users/<MyUsername>/.venv/bin/scrapling-mcp"
    }
  }
}
```

#### Docker {#docker}

إذا كنت تستخدم صورة Docker، فسيكون الإعداد مثل هذا:

```json
{
  "mcpServers": {
    "ScraplingServer": {
      "command": "docker",
      "args": [
        "run", "-i", "--rm", "pyd4vinci/scrapling", "mcp"
      ]
    }
  }
}
```

تنطبق الفكرة نفسها على [Cursor](https://cursor.com/docs/context/mcp) و[WindSurf](https://windsurf.com/university/tutorials/configuring-first-mcp-server) وغيرهما.

### Claude Code {#claude-code}

الإعداد هنا أبسط بكثير. مع [Claude Code](https://www.anthropic.com/claude-code):

```bash
claude mcp add ScraplingServer "/Users/<MyUsername>/.venv/bin/scrapling-mcp"
```

للحصول على مسار الملف التنفيذي لـ Scrapling:

1. **MacOS**: `which scrapling-mcp`
2. **Windows**: `where scrapling-mcp`

للتفاصيل، راجع مقال Anthropic الرئيسي عن [إضافة خوادم MCP إلى Claude Code](https://docs.anthropic.com/en/docs/claude-code/mcp#option-1%3A-add-a-local-stdio-server).

بعد إضافة الخادم، أغلق التطبيق الذي استخدمته بالكامل وأعد تشغيله. في Claude Desktop، يفترض أن يظهر مؤشر خادم MCP، وهو 🔧، أسفل يمين مربع المحادثة، أو يظهر `ScraplingServer` في قائمة `Search and tools` داخل مربع الإدخال.

### استخدام ملف متصفح تنفيذي مخصص {#custom-browser-executable}

تستطيع أداتا `browser_fetch_once` و`browser_open` استخدام ملف تنفيذي لمتصفح متوافق مع Chromium بدلًا من Chromium المرفق. يفيد ذلك مع نسخ المتصفحات المخصصة أو محركات المتصفح الخفيفة.

لإعداده مرة واحدة لخادم MCP كله، مرّر مسار الملف التنفيذي عند بدء الخادم:

```bash
scrapling-mcp --executable-path "/path/to/chromium"
```

في إعداد Claude Desktop، أضف الخيار إلى معاملات الخادم:

```json
{
  "mcpServers": {
    "ScraplingServer": {
      "command": "/Users/<MyUsername>/.venv/bin/scrapling-mcp",
      "args": [
        "--executable-path",
        "/path/to/chromium"
      ]
    }
  }
}
```

يمكنك أيضًا تعيين متغير البيئة `SCRAPLING_EXECUTABLE_PATH` قبل بدء الخادم. ويستطيع الذكاء الاصطناعي اختيار ملف متصفح مختلف لجلب واحد باستخدام `browser_fetch_once` أو عند فتح جلسة باستخدام `browser_open`.

### الاتصال بمتصفحات بعيدة {#connecting-to-remote-browsers}

لا يحتاج `browser_open` إلى تشغيل متصفح محلي. مرّر رابط CDP ليتصل بمتصفح يعمل بالفعل عبر [Chrome DevTools Protocol](https://chromedevtools.github.io/devtools-protocol/)، سواء كان على الجهاز نفسه أو جهاز آخر أو لدى مزوّد متصفحات مُدارة:

```
Open a stealthy browser session on wss://cdp.provider.example/session/abc123, then use it to scrape the product details from https://shop.example.com. Close the session when you're done.
```

تستخدم `session_id` الناتج كالمعتاد مع `browser_fetch` و`browser_extract` و`browser_actions` و`browser_evaluate` و`browser_screenshot` و`browser_network_requests` و`browser_network_request` و`browser_save_state` و`browser_load_state`.

يمكن أن يكون الرابط عنوان WebSocket يبدأ بـ `ws://` أو `wss://`، كما يوفره مزوّدو المتصفحات المُدارة، أو عنوان HTTP لمتصفح شغّلته بنفسك مع تفعيل منفذ تصحيح الأخطاء عن بعد:

```commandline
chrome --remote-debugging-port=9222
```

يمكن الوصول إلى هذا المتصفح باستخدام `cdp_url="http://localhost:9222"`، أو عنوان الجهاز إذا كان المتصفح يعمل على جهاز آخر.

!!! note "ملاحظات:"

    * المتصفح يعمل بالفعل، لذلك تُتجاهل الخيارات الخاصة بالتشغيل فقط في جلسات CDP: وهي `headless` و`real_chrome` و`executable_path`، بما فيها القيمة الافتراضية للخادم الموضحة أعلاه.<br/>
    * تظل بقية الخيارات فعالة، مثل `locale` و`useragent` و`proxy` و`cookies` و`timezone_id`، لأن كل جلسة تنشئ سياق متصفح خاصًا بها على المتصفح البعيد.

### Streamable HTTP {#streamable-http}

منذ الإصدار 0.3.6، يمكن تشغيل خادم MCP بوضع النقل Streamable HTTP بدلًا من وضع stdio التقليدي.

بدلًا من الأمر التالي الذي يستخدم stdio:

```bash
scrapling-mcp
```

استخدم هذا الأمر لتفعيل Streamable HTTP:

```bash
scrapling-mcp --http
```

العنوان الافتراضي الذي يستمع إليه الخادم هو `127.0.0.1`، والمنفذ هو 8000. ويمكن تغييرهما كما يلي:

```bash
scrapling-mcp --http --host '0.0.0.0' --port 8000
```

الإعداد الافتراضي يقبل الاتصالات من الجهاز نفسه فقط. مرّر `--host '0.0.0.0'` عندما تريد إتاحة الخادم عبر الشبكة. هذا قرار منفصل عن إعداد المصادقة أدناه.

إذا شغّلت Streamable HTTP داخل Docker، فيجب الاستماع على `0.0.0.0` وتعيين token، وإلا فلن يصل المنفذ المنشور إلى الخادم، لأن `127.0.0.1` داخل الحاوية لا يظهر إلا لها:

```bash
docker run -p 8000:8000 -e SCRAPLING_MCP_AUTH_TOKEN="<your-token>" pyd4vinci/scrapling mcp --http --host '0.0.0.0'
```

### المصادقة {#authentication}

لا يستطيع الوصول إلى وضع stdio إلا البرنامج الذي بدأه. لكن عند الانتقال إلى Streamable HTTP، يستطيع أي شخص يصل إلى المنفذ استدعاء كل الأدوات، بما فيها جلب أي رابط من الجهاز الذي يشغّل الخادم. لذلك يتطلب Streamable HTTP المصادقة، ويرفض `--http` وحده بدء التشغيل ويطلب token:

```bash
scrapling-mcp --http --auth-token "$(openssl rand -hex 32)"
```

يجب أن يرسل العميل هذا token في ترويسة `Authorization`. ويُرفض أي طلب لا يحتوي عليه برمز `401`:

```json
{
  "mcpServers": {
    "ScraplingServer": {
      "url": "https://your-server.example.com/mcp",
      "headers": {
        "Authorization": "Bearer <your-token>"
      }
    }
  }
}
```

تمرير token في سطر الأوامر يتركه في سجل الطرفية وقائمة العمليات، لذا يُفضّل استخدام متغير البيئة `SCRAPLING_MCP_AUTH_TOKEN`:

```bash
export SCRAPLING_MCP_AUTH_TOKEN="<your-token>"
scrapling-mcp --http
```

إذا أردت خادمًا دون مصادقة، مثل الاختبار محليًا على العنوان الافتراضي `127.0.0.1`، فاطلب ذلك صراحة باستخدام `--no-auth`:

```bash
scrapling-mcp --http --no-auth
```

الجمع بين `--no-auth` و`--host '0.0.0.0'` يتيح كل الأدوات لأي شخص يصل إلى المنفذ، لذا تجنّب هذا الجمع خارج شبكة موثوقة.

عندما يستمع الخادم على عنوان عام، حدّد أيضًا أسماء المضيفين التي يقبلها. هذا يفعّل الحماية من هجمات DNS rebinding، حيث يحاول موقع تزوره الاتصال بخادمك عبر المتصفح. ويمكن تكرار الخيار:

```bash
scrapling-mcp --http --allowed-host 'your-server.example.com:8000'
```

!!! note "ملاحظات:"

    * تنطبق المصادقة على Streamable HTTP فقط. تُتجاهل مع stdio، ويسجل الخادم تحذيرًا بذلك.<br/>
    * يرسل HTTP العادي token دون تشفير، لذا ضع الخادم خلف reverse proxy يتولى اتصال TLS قبل إتاحته على الإنترنت.<br/>
    * يُستخدم مفتاح واحد مشترك، وليس بيانات دخول منفصلة لكل عميل. لذا تستخدم كل التطبيقات token نفسه، ويتطلب تغييره إعادة تشغيل الخادم.<br/>
    * يسجل الخادم تحذيرًا عند تشغيله باستخدام `--http --no-auth` لإبلاغك بأن المصادقة غير مفعّلة.<br/>
    * عند تمرير `--auth-token` و`--no-auth` معًا، يبقى token فعالًا وتستمر المصادقة بدلًا من إلغائها دون تنبيه.

## أمثلة {#examples}

نعرض هنا بعض prompts التي استخدمناها عند اختبار خادم MCP. وربما تكون أكثر إبداعًا منا في كتابة الطلبات :)

سنبدأ بطلبات بسيطة ثم ننتقل تدريجيًا إلى طلبات أكثر تعقيدًا. نستخدم Claude Desktop في الأمثلة، لكن الفكرة نفسها تنطبق على بقية التطبيقات.

1. **استخراج بيانات بسيط**

    استخرج المحتوى الرئيسي من صفحة بصيغة Markdown:

    ```
    Scrape the main content from https://example.com and convert it to markdown format.
    ```

    يستطيع Claude استخدام `make_request` لجلب الصفحة وإرجاع محتوى نظيف وسهل القراءة. تستخدم طلبات HTTP ثلاث محاولات افتراضيًا، مع ثانية واحدة بين المحاولات. وإذا كانت الصفحة تحتاج إلى JavaScript أو تمنع طلبات HTTP، يمكن استخدام `browser_fetch_once`. تغلق الأداتان مواردهما بعد الاستدعاء.

    ويمكن تحسين الطلب نفسه كما يلي:

    ```
    Use regular requests to scrape the main content from https://example.com and convert it to markdown format.
    ```

    يوضح هذا لـ Claude الأداة المطلوبة، فلا يحتاج إلى التخمين. أحيانًا يبدأ بطلبات HTTP العادية بنفسه، وأحيانًا يفترض أن المتصفح أنسب للموقع دون سبب واضح. كقاعدة عامة، حدّد له الأداة دائمًا لتوفير الوقت والتكلفة والحصول على نتائج متسقة.

2. **استخراج بيانات محددة**

    استخرج عناصر معينة باستخدام محددات CSS:

    ```
    Get all product titles from https://shop.example.com using the CSS selector '.product-title'. If the request fails, retry up to 5 times every 10 seconds.
    ```

    يستخرج الخادم العناصر المطابقة للمحدد فقط ويُرجعها في قائمة منظمة. لاحظ أنني طلبت ضبط الأداة على خمس محاولات عند وجود مشاكل اتصال بالموقع، لكن الإعداد الافتراضي مناسب لمعظم الحالات.

3. **جمع بيانات المتاجر الإلكترونية**

    مثال آخر لطلب أكثر تعقيدًا قليلًا:

    ```
    Open a stealthy browser session and visit these e-commerce URLs one at a time:
    - https://shop1.com/product-a
    - https://shop2.com/product-b  
    - https://shop3.com/product-c
    
    Get the product names, prices, and descriptions from each page. Close the session when done.
    ```

    يستطيع Claude إعادة استخدام جلسة متصفح واحدة، واستدعاء `browser_fetch` لكل رابط بالترتيب، ثم تحليل البيانات المستخرجة.

4. **خطوات عمل أكثر تقدمًا**

    لنفترض أنني أريد كل ألعاب الأكشن الموجودة الآن في الصفحة الأولى من متجر PlayStation. يمكنني استخدام الطلب التالي:

    ```
    Extract the URLs of all games on this page, then visit each game in order and return a list of all action games: https://store.playstation.com/en-us/pages/browse
    ```

    اطلب من الذكاء الاصطناعي إعادة استخدام جلسة HTTP لتجنب تشغيل متصفح عندما تكون البيانات متاحة بالطلبات العادية:

    ```
    Open an HTTP session, extract the URLs of all games on this page, then fetch each game in order and return a list of all action games. Close the session when done: https://store.playstation.com/en-us/pages/browse
    ```

    وإذا كنت تعرف كتابة محددات CSS، فيمكنك تقليل المحتوى قبل أن يقرأه النموذج:

    ```
    Use an HTTP session to extract the URLs of all games on the page below, then fetch each game in order and return a list of all action games.
    The selector for games in the first page is `[href*="/concept/"]` and the selector for the genre in each game page is `[data-qa="gameInfo#releaseInformation#genre-value"]`.
    Close the session when done.

    URL: https://store.playstation.com/en-us/pages/browse
    ```

5. **استخراج بيانات موقع محمي بـ Cloudflare**

    إذا كنت تعتقد أن الموقع يستخدم حماية Cloudflare، فأخبر Claude بدلًا من تركه يكتشف ذلك بنفسه.

    ```
    What's the price of this product? Be cautious, as it utilizes Cloudflare's Turnstile protection. Make the browser visible while you work.

    https://ao.com/product/oo101uk-ninja-woodfire-outdoor-pizza-oven-brown-99357-685.aspx
    ```

6. **خطوات عمل طويلة**

    يمكنك مثلًا استخدام طلب كهذا:

    ```
    Extract all product URLs for the following category, then return the prices and details for the first 3 products.
    
    https://www.arnotts.ie/furniture/bedroom/bed-frames/
    ```

    لكن الطلب التالي أفضل:

    ```
    Go to the following category URL and extract all product URLs using the CSS selector "a". Then, reuse the session to fetch the first 3 product pages in order and extract each product’s price and details. Close the session when done.
    
    Keep the output in markdown format to reduce irrelevant content.
    
    Category URL:
    https://www.arnotts.ie/furniture/bedroom/bed-frames/
    ```

7. **استخدام الجلسات المستمرة**

    عند استخراج بيانات عدة صفحات من الموقع نفسه، استخدم جلسة متصفح مستمرة لتجنب تشغيل متصفح جديد لكل طلب:

    ```
    Open a stealthy browser session, then use it to scrape the main details from the first 5 product pages on https://shop.example.com. Close the session when you're done.
    ```

    يستخدم Claude أداة `browser_open` لإنشاء متصفح مستمر، ثم `browser_fetch` لكل صفحة منتج عبر الجلسة نفسها، وأخيرًا `close_session`. هذا أسرع بكثير من تشغيل متصفح جديد لكل صفحة.

    !!! danger "تنبيه"

        عند استخدام الجلسات المستمرة، تذكّر إغلاق الجلسة بعد الانتهاء، وإلا ستظل مفتوحة!

8. **استخدام جلسة مستمرة في مهمة طويلة**

    مثال اختبار طويل آخر يتطلب من Claude التفكير:

    ```
    Use Scrapling MCP to do the following in this order:

    1. Open a stealthy browser session with headless mode off.
    2. Go to this page and collect the number of stars: https://github.com/D4Vinci/Scrapling
    3. From the README, get the URL that shows the number of downloads and go to it.
    4. Get the number of downloads and the top 3 countries from the graph.
    5. Prepare a report with the results.
    6. Close the browser.
    ```

وهكذا. إبداعك هو الأساس هنا.

## أفضل الممارسات {#best-practices}

إليك بعض النصائح التقنية.

### 1. اختر الأداة المناسبة {#1-choose-the-right-tool}

- **`make_request`**: طلبات HTTP سريعة لصفحة واحدة أو استدعاء API.
- **`browser_fetch_once`**: صفحة JavaScript واحدة أو صفحة ديناميكية أو موقع محمي، بما في ذلك Cloudflare.
- **أدوات الجلسات**: طلبات مترابطة، وإجراءات المتصفح، ولقطات الشاشة، وسجل الشبكة.

### 2. حسّن الأداء {#2-optimize-performance}

- أعد استخدام جلسة واحدة واجلب الروابط بالترتيب.
- عطّل الموارد غير المطلوبة.
- اضبط مهل انتظار مناسبة.
- استخدم محددات CSS لاستخراج المحتوى المطلوب فقط.

### 3. تعامل مع المحتوى الديناميكي {#3-handle-dynamic-content}

- استخدم `network_idle` مع تطبيقات الصفحة الواحدة، أو SPA.
- اضبط `wait_selector` لانتظار عناصر معينة.
- زِد مهلة الانتظار للمواقع بطيئة التحميل.

### 4. جودة البيانات {#4-data-quality}

- استخدم `main_content_only=true` لاختيار محتوى body وتنظيفه.
- اختر قيمة `extraction_type` المناسبة لمهمتك.

### 5. الحماية من حقن التعليمات {#5-prompt-injection-protection}

ينظّف خادم MCP المحتوى المستخرج تلقائيًا عند تفعيل `main_content_only`، وهو الإعداد الافتراضي. يزيل هذا المحتوى المخفي الذي قد تستخدمه مواقع ضارة لإدخال تعليمات إلى سياق الذكاء الاصطناعي:

- **أنماط الإخفاء المباشرة**: مثل `display:none` و`visibility:hidden`، والقيم الصفرية للشفافية وحجم الخط والارتفاع والعرض وmax-height وmax-width.
- **عناصر مخفية عن أدوات تسهيل الوصول**: `aria-hidden="true"`.
- **وسوم template وعناصر slot المخفية**: عناصر `<template>` و`<slot hidden>`.
- **تعليقات HTML**: `<!-- ... -->`.
- **محارف عديمة العرض**: محارف Unicode غير المرئية، مثل المسافات عديمة العرض.

تعمل هذه الحماية تلقائيًا مع استخراج HTML وMarkdown والنص. أبقِ `main_content_only=true`، وهو الإعداد الافتراضي، للحصول على أقصى حماية.

### 6. إدارة الجلسات {#6-manage-sessions}

- استخدم `make_request` أو `browser_fetch_once` للجلب المنفرد. تغلقان مواردهما ولا تتركان جلسة للاستدعاءات اللاحقة.
- استخدم `browser_open` لإنشاء جلسة متصفح مستمرة عند جلب عدة صفحات، ثم استدعِ `browser_fetch` لكل صفحة عبر هذه الجلسة.
- لطلبات HTTP العادية المتعددة، استخدم `open_request_session` ثم `session_make_request` لكل طلب. تحتفظ الجلسة بـ cookies والاتصالات وبصمة المتصفح `impersonate` بين الاستدعاءات دون متصفح.
- تحتفظ الجلسات بإعدادات مستوى الجلسة التي عُيّنت عند فتحها، مثل headless وlocale وcookies وخيارات التخفي للمتصفح، و`impersonate` و`proxy` لجلسات الطلبات. أما خيارات كل طلب، مثل timeout وwait_selector وnetwork_idle وsolve_cloudflare، فتُمرّر إلى `browser_fetch` أو `session_make_request` في كل استدعاء. تظهر قيمها الافتراضية في مخططات الأدوات.
- يستطيع `browser_fetch` حل تحديات Cloudflare عبر جلسة متصفح Stealthy المفتوحة.
- أغلق الجلسات دائمًا باستخدام `close_session` بعد الانتهاء لتحرير الموارد.
- استخدم `list_sessions` لمعرفة الجلسات التي ما زالت نشطة، والاطلاع على `settings` التي أُنشئت بها كل جلسة. تُرجع الإعدادات لوكيل الذكاء الاصطناعي، وتكون فارغة لجلسات CDP.
- مرّر `session_id` مخصصًا إلى أدوات فتح الجلسات لإعطائها أسماء واضحة، مثل `"search"` أو `"checkout"`، بدلًا من المعرّف السداسي العشري العشوائي. تُرجع الأدوات خطأ إذا كان المعرّف مستخدمًا، لتكتشف التعارض مبكرًا.

### 7. التقاط صور الشاشة {#7-capturing-screenshots}

- تلتقط `browser_screenshot` الصفحة المفتوحة بالفعل عبر `browser_fetch` في جلسة متصفح Stealthy. لا تعيد تحميل الصفحة، ليستطيع الذكاء الاصطناعي فحص الحقول المملوءة والقوائم المفتوحة ونتائج إجراءاته.
- تُرجع الصورة في كتلة `ImageContent` فعلية، ليراها النموذج مباشرة.
- التقط الجزء المرئي أو الصفحة كاملة، بما فيها المحتوى أسفل الجزء الظاهر.
- التقط حقلًا أو رسمًا أو بطاقة أو نتيجة واحدة لفحصها دون محتوى كثير حولها. قد تمرّر لقطة العنصر الصفحة لإظهاره.
- اختر PNG لصور دون فقدان جودة، أو JPEG بجودة قابلة للضبط لتقليل حجم البيانات.
- يستطيع الذكاء الاصطناعي استخدام `browser_actions` لانتظار المحتوى أو إكمال التفاعل قبل التصوير.

## اعتبارات قانونية وأخلاقية {#legal-and-ethical-considerations}

⚠️ **إرشادات مهمة:**

- **افحص robots.txt**: افتح `https://website.com/robots.txt` لمعرفة قواعد استخراج البيانات.
- **احترم حدود الطلبات**: لا تُثقل الخوادم بكثرة الطلبات.
- **شروط الخدمة**: اقرأ شروط الموقع والتزم بها.
- **حقوق النشر**: احترم حقوق الملكية الفكرية.
- **الخصوصية**: راعِ قوانين حماية البيانات الشخصية.
- **الاستخدام التجاري**: تأكد من امتلاك الإذن المطلوب لأغراض العمل.

---

*صُنع بحب ❤️ بواسطة فريق Scrapling. نتمنى لك تجربة موفقة في استخراج البيانات!*
