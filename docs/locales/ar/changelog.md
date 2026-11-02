---
title: "سجل تغييرات Scrapling"
description: "ملاحظات إصدارات Scrapling، بما فيها الميزات الجديدة والإصلاحات والتغييرات التي قد تؤثر في الكود الحالي."
---

# سجل التغييرات {#changelog}

كل التغييرات المهمة في Scrapling، نقلًا عن [إصدارات GitHub](https://github.com/D4Vinci/Scrapling/releases).

## [v0.5](https://github.com/D4Vinci/Scrapling/releases/tag/v0.5) - 2026-10-17 {#v0.5}

**يحسّن Scrapling v0.5 كل شيء تقريبًا: جلب الصفحات، وتحليلها، والعناكب، وأتمتة المتصفح، وأدوات الذكاء الاصطناعي، والتوثيق بعشر لغات 🚀**

!!! warning "تنبيه"

    **يتضمن هذا الإصدار تغييرات كثيرة قد تؤثر في الكود الحالي ولا تتسع لها هذه الصفحة. راجع [دليل الانتقال إلى v0.5](migrating-to-v0.5.md) قبل التحديث.**

### 🚀 الجديد وتحسينات الاستخدام {#v0.5-new-stuff-and-quality-of-life-changes}

- **خادم MCP بقدرات أكبر لوكلاء الذكاء الاصطناعي يمكنه حل أي CAPTCHA تقريبًا** (راجع [التوثيق](ai/mcp-server.md)):

    - **تنفيذ خطوات كاملة في المتصفح**: املأ النماذج، وانقر، وحرّك المؤشر فوق العناصر، ومرّر الصفحة، واستخدم لوحة المفاتيح، وتعامل مع مربعات الحوار، وانتظر النتائج في تسلسل واحد مرتب. يدعم أنواعًا مختلفة من الحقول والتفاعل البطيء، وتتوقف الإجراءات عند أول خطأ.
    - **اقرأ الصفحة الحالية وابحث فيها دون إعادة تحميلها**: استخرج HTML أو Markdown أو النص من الصفحة كاملة أو من عنصر واحد. تعرض لقطات الصفحة القابلة للبحث أدوار العناصر وأسماءها ومواضعها، مع عروض مركزة تحتفظ بالسياق المحيط.
    - **شغّل JavaScript مخصصًا والتقط صورًا لأجزاء محددة**: نفّذ السكربتات، بما فيها العمليات غير المتزامنة، مع الوصول إلى JavaScript الخاص بالصفحة. التقط صورة لعنصر واحد أو للجزء الظاهر أو للصفحة كاملة بصيغة PNG أو JPEG.
    - **افحص نشاط الشبكة وأعد استخدام تسجيل الدخول**: افحص الطلبات والردود المسجلة، واحفظ حالة تسجيل الدخول في المتصفح واستعدها، وتفاعل مع العناصر داخل Shadow DOM المفتوح أو المغلق. اقرأ حركة الشبكة المسجلة قبل إغلاق الجلسة.
    - **استهلك tokens أقل واحصل على أخطاء أوضح**: تقلل أوصاف الأدوات الأقصر والإرشادات المشتركة النص المكرر، وتصل أخطاء المتصفح والطلبات إلى الوكلاء برسائل مفيدة.

- **شاهد الطلبات التي تعمل خلف الصفحة**. فعّل `record_requests=True` لتسجيل حركة الشبكة المكتملة عبر تحميل الصفحات والإجراءات والتبويبات، ثم افحص الردود المحفوظة دون إرسال الطلبات مجددًا. (راجع [التوثيق](fetching/stealthy.md#network-history))

    ```python
    from scrapling.fetchers import StealthySession

    with StealthySession(record_requests=True) as session:
        session.fetch("https://example.com", network_idle=True)
        for response in session.network.search(url_pattern=r"/api/", limit=None):
            print(response.url, response.status, response.body)
    ```

    - صفِّ النتائج حسب الرابط أو طريقة الطلب أو نوع المورد أو الحالة، واسترجع ردًا واحدًا بمعرّفه. افحص الترويسات والبيانات المرسلة وردود API وأخطاء HTTP وإعادة التوجيه عبر واجهة `Response` المعتادة.
    - يحتفظ بمحتوى الردود النصية المدعومة ضمن حدود للحجم، مع البيانات الوصفية وسبب عدم حفظ المحتوى عند تعذر ذلك. الحد الافتراضي هو 1,000 طلب. يعمل مع الجلسات المتزامنة وغير المتزامنة، ويبقى السجل المحفوظ في Python قابلًا للقراءة بعد الإغلاق.

- **احفظ تسجيل الدخول مرة واحدة وأعد استخدامه في مرات التشغيل التالية**. تحفظ `save_state(path)` و`load_state(path)` ملفات cookies والتخزين المحلي وIndexedDB في JSON متوافق مع Playwright وتستعيدها. تدعمهما جلسات المتصفح المتزامنة وغير المتزامنة. (راجع [التوثيق](fetching/stealthy.md#save-and-load-session-state))
    - حمّل الحالة قبل جلب الصفحة أو إعادة تحميلها. تتطلب هذه الميزة سياق متصفح مشتركًا بدأ تشغيله دون `proxy_rotator`؛ ولا تُحفظ التبويبات أو إعدادات المتصفح أو `sessionStorage`.

- **استخرج Shadow DOM المفتوح باستخدام `pierce_shadow=True`**، ثم استخدم CSS أو XPath كالمعتاد. تتوفر الميزة في أدوات جلب الصفحات بالمتصفح والجلسات والخيار `--pierce-shadow` في CLI. تحتفظ بمحتوى slot دون تغيير الصفحة المفتوحة. لا يشمل HTML الملتقط جذور Shadow DOM المغلقة أو مستندات iframe. (راجع [التوثيق](fetching/stealthy.md#shadow-dom))

- **اختر كيف يستكشف عنكبوتك الموقع**. يدعم `CrawlSpider` والأصناف المشتقة منه، بما فيها `ContentSpider`، الخيار `crawl_strategy="bfs"` لجدولة الأقدم أولًا أو `"dfs"` لجدولة الأحدث أولًا. تبقى الأولوية هي العامل الأهم، وقد تكتمل الصفحات التي تُجلب بالتوازي بترتيب مختلف. (راجع [التوثيق](spiders/generic-templates.md#crawl-order))

### 🐛 إصلاحات الأخطاء {#v0.5-bug-fixes}

- **تحسين حل تحديات Cloudflare** باكتشاف أداة التحدي التي تظهر متأخرة، وتقليل الانتظار غير الضروري، ووضع حد لحلقات إعادة المحاولة مع التحديات غير التفاعلية والإطارات المخفية. يصلح [#468](https://github.com/D4Vinci/Scrapling/issues/468) و[#509](https://github.com/D4Vinci/Scrapling/issues/509).
- **إصلاح تشغيل المتصفح من طرفية Windows بصلاحيات المسؤول**. يصلح [#463](https://github.com/D4Vinci/Scrapling/issues/463).
- **الإبقاء على خيارات التخفي المدمجة عند إضافة خيارات متصفح مخصصة**، بمساهمة @alkaz-nodemaven في [#430](https://github.com/D4Vinci/Scrapling/pull/430).
- **تحسين قراءة تعريف ترميز الأحرف في ردود المتصفح**، بما فيها التعريفات التي تختلف فيها حالة الأحرف أو تتضمن مسافات أو قيمًا بين علامتي اقتباس.
- **إيقاف تسجيل غياب تحدي Cloudflare كخطأ** عندما لا يوجد تحدٍّ يحتاج إلى حل. يصلح [#459](https://github.com/D4Vinci/Scrapling/issues/459).

- **تصحيح بصمات الطلبات** لمعاملات الرابط، بمساهمة @yetval في [#448](https://github.com/D4Vinci/Scrapling/pull/448)، ولمحتوى JSON الفارغ أو ذي القيمة التي تُعدّ خاطئة منطقيًا، بمساهمة @ac1982 في [#480](https://github.com/D4Vinci/Scrapling/pull/480)، ولترتيب إضافة الترويسات، بمساهمة @SarwadnyaMahajan في [#466](https://github.com/D4Vinci/Scrapling/pull/466).
- **إصلاح انتقال بيانات الطلب إلى الروابط المتبوعة**، بما فيها الترويسات القديمة المرتبطة بمحتوى الطلب، بمساهمة @yetval في [#462](https://github.com/D4Vinci/Scrapling/pull/462).
- **منع تخزين الردود المحظورة كنتائج ناجحة في ذاكرة التخزين المؤقت لوضع التطوير**، بمساهمة @Kuang-xianxin في [#446](https://github.com/D4Vinci/Scrapling/pull/446).
- **الإبقاء على ملفات نقاط الحفظ عند فشل الزحف بسبب استثناء**، بمساهمة @SulimanAbdulrazzaq في [#486](https://github.com/D4Vinci/Scrapling/pull/486).
- **تصحيح التعامل مع فشل جلب robots.txt** حتى لا يُخزّن الفشل مؤقتًا بوصفه سماحًا بالزحف، بمساهمة @prateekraawat1 في [#443](https://github.com/D4Vinci/Scrapling/pull/443).
- **إصلاح استخراج الروابط باستخدام محددات لتقييد نطاق البحث**، بما فيها النتائج الفارغة والمحددات التي تستهدف عنصر الرابط نفسه، بمساهمة @SulimanAbdulrazzaq في [#452](https://github.com/D4Vinci/Scrapling/pull/452) و[#483](https://github.com/D4Vinci/Scrapling/pull/483).
- **إصلاح توجيه روابط خريطة الموقع إلى دوال معالجتها**، بمساهمة @SulimanAbdulrazzaq في [#458](https://github.com/D4Vinci/Scrapling/pull/458)، **وتحليل XML الذي يحتوي على تعليقات أو تعليمات معالجة**، بمساهمة @sup3dev في [#450](https://github.com/D4Vinci/Scrapling/pull/450).
- **معالجة علامات ترتيب البايتات في بداية robots.txt وخلاصات CSV**، بمساهمة @SulimanAbdulrazzaq في [#453](https://github.com/D4Vinci/Scrapling/pull/453).
- **إصلاح التعامل مع `stealthy_headers` في جلسات HTTP للعناكب**، بتمرير الخيار إلى الجلسة بدلًا من تمريره مباشرة إلى `curl_cffi`، بمساهمة @Yigtwxx في [#475](https://github.com/D4Vinci/Scrapling/pull/475).

- **إصلاح ترميز بيانات النماذج من القواميس عندما تكون القيم قوائم أو tuples**، مع الحفاظ على أسبقية محتوى الطلب وطريقة التعامل الحالية مع `None`، بمساهمات من @SulimanAbdulrazzaq في [#485](https://github.com/D4Vinci/Scrapling/pull/485).
- **إصلاح دمج ترويسات HTTP للجلسة والطلب دون حساسية لحالة الأحرف**، بمساهمة @SulimanAbdulrazzaq في [#487](https://github.com/D4Vinci/Scrapling/pull/487).
- **إصلاح إسقاط طلبات CLI لمحتوى JSON الفارغ أو ذي القيمة التي تُعدّ خاطئة منطقيًا دون تنبيه**، بمساهمة @SulimanAbdulrazzaq في [#484](https://github.com/D4Vinci/Scrapling/pull/484).
- **استخدام UTF-8 دائمًا عند تصدير ملفات Markdown والنصوص** ومنع أخطاء التحويل من اقتطاع ملف إخراج موجود، بمساهمة @SulimanAbdulrazzaq في [#488](https://github.com/D4Vinci/Scrapling/pull/488).
- **إصلاح تعامل `curl2fetcher()` مع خياري وكيل المستخدم والوكيل الشبكي في curl**، بمساهمة @SulimanAbdulrazzaq في [#490](https://github.com/D4Vinci/Scrapling/pull/490).

- **إصلاح تلاصق كتل Markdown** عند تحويل عدة عناصر محددة عبر `Response.markdown()` أو استخراج CLI، بمساهمات من @Yigtwxx في [#432](https://github.com/D4Vinci/Scrapling/pull/432).
- **إصلاح تنظيف المحتوى المخفي في مخرجات الذكاء الاصطناعي** للإبقاء على المحتوى الظاهر مثل `opacity:0.95`، والتعرف على مزيد من الأنماط التي تخفي المحتوى، وإزالة عناصر slot المخفية، بمساهمات من @Yigtwxx في [#460](https://github.com/D4Vinci/Scrapling/pull/460).
- **إصلاح توقف إزالة الوسوم غير المرغوبة مبكرًا عند وجود وسوم متداخلة**، بمساهمة @Yigtwxx في [#474](https://github.com/D4Vinci/Scrapling/pull/474).
- **إصلاح محددات CSS وXPath المُولّدة لأول عنصر من عدة عناصر شقيقة لها الوسم نفسه**، بمساهمة @yellow-dog-dog في [#495](https://github.com/D4Vinci/Scrapling/pull/495).
- **إزالة تحذير الإهمال من محلل HTML في lxml**، بمساهمة @afsuyadi في [#493](https://github.com/D4Vinci/Scrapling/pull/493).

### التوثيق {#v0.5-docs}

- **الموقع كاملًا متاح الآن بعشر لغات**: الإنجليزية والعربية والإسبانية والبرتغالية البرازيلية والفرنسية والألمانية والصينية المبسطة واليابانية والروسية والكورية. تُرجمت الأدلة ومراجع API والدروس و[سجل التغييرات](changelog.md)، مع دعم اتجاه الكتابة من اليمين إلى اليسار للعربية وتبديل اللغة مع الاحتفاظ بالصفحة والقسم الحاليين.
- **أدلة وأمثلة README وخطوات إعداد أوضح**، تشمل بيانات نقاط الحفظ وترميزات المتصفح والحالة المحفوظة وسجل الشبكة وShadow DOM وترتيب الزحف.
- **تحديث مهارة الوكيل** وأمثلتها ومراجعها وأرشيفها القابل للتنزيل لتوافق أدوات المتصفح وMCP الحالية.
- **نقل سجل التغييرات إلى الموقع** وإتاحة مصدر Markdown لكل صفحة.

### المشروع {#v0.5-project}

- تحديث شعار Scrapling وصور الغلاف وطريقة عرض الموقع.
- توسيع اختبارات إجراءات المتصفح ومربعات الحوار والاستخراج ولقطات الشاشة وJavaScript وتسجيل الشبكة وملفات الحالة وShadow DOM وإصلاحات الزاحف.
- إضافة علامة لاختبارات المتصفح وتشغيل اختبارات المتصفح والاختبارات غير المتزامنة والمتوازية بصورة منفصلة. تحسين توافق اختبارات نقاط الحفظ وCSV مع Windows، بمساهمة @diegobravtraps-oss في [#457](https://github.com/D4Vinci/Scrapling/pull/457).
- تحديث إعداد البناء المشترك للتوثيق متعدد اللغات وإرشادات المساهمة.

## [v0.4.15](https://github.com/D4Vinci/Scrapling/releases/tag/v0.4.15) - 2026-08-23 {#v0.4.15}

**أحد أكبر إصدارات هذا العام: إعادة تصميم خادم MCP، وتحويل الصفحات إلى Markdown جاهز لـ RAG بسطر واحد، وتحسين حل تحديات Cloudflare، وإبقاء تبويبات المتصفح مفتوحة للأتمتة 🚀**

!!! warning "تنبيه"

    **يتضمن هذا الإصدار تغييرات في خادم MCP قد تؤثر في الكود الحالي. راجع قسم [هذه التغييرات](https://github.com/D4Vinci/Scrapling/blob/v0.4.15/docs/ai/mcp-server.md#breaking-changes) قبل التحديث.**

### 🚀 الجديد وتحسينات الاستخدام {#v0.4.15-new-stuff-and-quality-of-life-changes}

- **تبقى تبويبات المتصفح مفتوحة الآن وتُستخدم مجددًا في الطلبات التالية** (راجع [التوثيق](fetching/stealthy.md#session-management)):
    - تحتفظ كل جلسات المتصفح بتبويباتها بعد الطلب، ويستخدم الطلب التالي تبويبًا متاحًا بدلًا من فتح تبويب جديد.
    - يعيد كل طلب تطبيق إعداداته الخاصة، مثل المهل الزمنية والترويسات وحظر الموارد، على التبويب الذي يستخدمه. لذلك لا تنتقل إعدادات طلب إلى آخر.
    - تُغلق التبويبات التي يحدث فيها خطأ وتُستبدل، وتغلق الدالة الجديدة `close_pages()` كل التبويبات المفتوحة.
    - تبقى الصفحة التي جلبتها محمّلة، فتعمل دالة `page_setup` للطلب التالي عليها قبل الانتقال إلى صفحة أخرى. يتيح ذلك ربط خطوات الأتمتة عبر عدة طلبات.

- **حوّل أي صفحة إلى Markdown نظيف وجاهز لنماذج اللغة الكبيرة باستخدام `Response.markdown()`** (راجع [التوثيق](ai/building-rag-systems.md)):

    ```python
    from scrapling.fetchers import Fetcher

    markdown = Fetcher.get("https://example.com").markdown(main_content_only=True)
    ```

    - تُزال دائمًا السكربتات والأنماط والمحتوى المخفي الذي قد يُستخدم في هجمات Prompt Injection أولًا، بنفس طريقة التنظيف التي يستخدمها خادم MCP.
    - مرّر `css_selector` لتحويل العناصر التي تحتاجها فقط.
    - تتوفر هذه الميزة عبر الإضافة الاختيارية الجديدة `rag` (`pip install "scrapling[rag]"`)، وتشملها أيضًا إضافات `ai`/`shell`/`all`.

- **قالب `SiteToMarkdownSpider` جديد للزحف إلى موقع كامل وتحويله إلى مجموعة ملفات Markdown لأنظمة RAG** (راجع [التوثيق](ai/building-rag-systems.md)):

    ```python
    from scrapling.spiders import SiteToMarkdownSpider

    class DocsSpider(SiteToMarkdownSpider):
        name = "docs"
        start_urls = ["https://example.com/docs/"]
        allowed_domains = {"example.com"}
        output_dir = "docs_markdown"

    result = DocsSpider().start()
    result.items.to_jsonl("docs.jsonl")
    ```

    - يُنتج عنصرًا واحدًا لكل صفحة يحتوي على `url`/`title`/`markdown`، ويتيح الخيار الاختياري `output_dir` كتابة ملف Markdown لكل صفحة.
    - يحدد `max_pages` أقصى عدد صفحات للزحف. ولأن القالب مبني على `CrawlSpider`، فإن إعادة تعريف `rules()` تمنحك تحكمًا كاملًا في الروابط التي يتبعها.

- **إعادة تصميم خادم MCP (تغييرات قد تؤثر في الكود الحالي)** (راجع [هذه التغييرات](https://github.com/D4Vinci/Scrapling/blob/v0.4.15/docs/ai/mcp-server.md#breaking-changes) و[التوثيق](ai/mcp-server.md)):
    - تنقسم الأدوات الـ 13 الآن إلى وضعين: أدوات تعمل مرة واحدة (`fetch`، `bulk_fetch`، `stealthy_fetch`، `bulk_stealthy_fetch`) وتفتح دائمًا متصفحًا خاصًا بها وتعرض إعداداتها الافتراضية الفعلية، وأدوات تستخدم جلسة تُفتح مرة واحدة.
    - تجلب الأداة الجديدة `session_fetch` الصفحات عبر جلسة متصفح، بينما أصبح `open_session` يحتفظ بإعدادات المتصفح فقط ويعيد الإعدادات الفعلية للجلسة إلى وكيل الذكاء الاصطناعي.
    - تغيّر اسم الأداة `get` إلى `make_request`، وهي تدعم الآن أي طريقة HTTP.
    - تمنح الأداتان الجديدتان `open_request_session` و`session_make_request` الذكاء الاصطناعي جلسات HTTP مستمرة تحتفظ بملفات cookies وبصمة المتصفح بين الطلبات.
    - ينهي هذا أيضًا مشكلة إعادة ضبط إعدادات الجلسة عند جلب الصفحات، والتي أصلحها @Yigtwxx أولًا في [#418](https://github.com/D4Vinci/Scrapling/pull/418).

- **يتطلب اتصال HTTP بخادم MCP التحقق من الهوية الآن، ويستمع على localhost افتراضيًا (تغييرات قد تؤثر في الكود الحالي)**، بمساهمة @yamantaka-singh في [#414](https://github.com/D4Vinci/Scrapling/pull/414) (يصلح [#413](https://github.com/D4Vinci/Scrapling/issues/413)، راجع [التوثيق](ai/mcp-server.md#authentication)):
    - مرّر `--auth-token` (أو متغير البيئة `SCRAPLING_MCP_AUTH_TOKEN`) لطلب رمز bearer، أو `--no-auth` إذا أردت تشغيله دون التحقق من الهوية.
    - مرّر `--host 0.0.0.0` لقبول الاتصالات من الشبكة.

### 🐛 إصلاحات الأخطاء {#v0.4.15-bug-fixes}

- **أصبح حل تحديات Cloudflare Turnstile/Interstitial يعمل بصرف النظر عن لغة المتصفح ومنطقته، ولم يعد يكرر المحاولة بلا نهاية مع التحديات التفاعلية في وضع headless**. كما لم تعد صفحات المتصفح الخفي تتعطل أثناء الحل، بمساهمات من @subediparas5 في [#412](https://github.com/D4Vinci/Scrapling/pull/412). (يصلح [#411](https://github.com/D4Vinci/Scrapling/issues/411) و[#422](https://github.com/D4Vinci/Scrapling/issues/422))
- **إصلاح تجاهل `find`/`find_all` للعناصر ذات الأصناف المتعددة عند استخدام `class_` دون تنبيه**، بمساهمة @yetval في [#410](https://github.com/D4Vinci/Scrapling/pull/410)، **وإصلاح قيم `class_` الفارغة والقيم النصية في CSS التي لم تُعالج محارفها الخاصة**، بمساهمة @yamantaka-singh في [#417](https://github.com/D4Vinci/Scrapling/pull/417).
- **إصلاح فقدان بيانات الطلب الإضافية عند إعادة استخدام الردود المخزنة مؤقتًا في `development_mode`**، بمساهمة @Yigtwxx في [#419](https://github.com/D4Vinci/Scrapling/pull/419).
- **إصلاح فشل طلبات HTTP دون إرسالها عندما تكون قيمة `retries` أقل من 1**، بمساهمة @Yigtwxx في [#420](https://github.com/D4Vinci/Scrapling/pull/420).

### التوثيق {#v0.4.15-docs}

- **إعادة تنظيم أقسام الموقع**: يضم قسم "الاستخدام مع الذكاء الاصطناعي" الجديد خادم MCP، وصفحة [مهارة الوكيل](ai/agent-skill.md) الجديدة، ودليل [بناء أنظمة RAG](ai/building-rag-systems.md). وانتقل دليل الانتقال من BeautifulSoup إلى جانب التكامل مع Scrapy ضمن قسم "التكامل والانتقال من مكتبات أخرى".
- **إضافة [سجل تغييرات](changelog.md)** إلى المستودع يضم ملاحظات كل الإصدارات حتى الآن.

## [v0.4.14](https://github.com/D4Vinci/Scrapling/releases/tag/v0.4.14) - 2026-08-10 {#v0.4.14}

**إصدار صيانة سريع لإصلاح التثبيت باستخدام `uv` 🔧**

### 🐛 إصلاحات الأخطاء {#v0.4.14-bug-fixes}

- **إصلاح رفض `uv` تثبيت v0.4.13 افتراضيًا والعودة إلى إصدار أقدم دون تنبيه**. كان الإصدار السابق يتطلب نسخة تجريبية من `curl_cffi`، وهو ما لا يسمح به `uv` إلا عند تفعيله صراحةً.
أصبحت كل الاعتمادات تستخدم إصدارات مستقرة. (يصلح [#407](https://github.com/D4Vinci/Scrapling/issues/407))

## [v0.4.13](https://github.com/D4Vinci/Scrapling/releases/tag/v0.4.13) - 2026-08-09 {#v0.4.13}

**تحديث جديد يضيف عناكب لملفات الخلاصات وخادم MCP أذكى 🎉**

### 🚀 الجديد وتحسينات الاستخدام {#v0.4.13-new-stuff-and-quality-of-life-changes}

- **قوالب عناكب جديدة للخلاصات**. يمر `XMLFeedSpider` على عُقد أي خلاصة XML (مثل RSS وAtom وخلاصات المنتجات)، ويمر `CSVFeedSpider` على صفوف CSV كقواميس. كلاهما يفك ضغط الخلاصات المضغوطة بـ gzip تلقائيًا. (راجع [التوثيق](spiders/generic-templates.md))

  ```python
  from scrapling.spiders import XMLFeedSpider

  class RSSSpider(XMLFeedSpider):
      name = "rss"
      start_urls = ["https://example.com/feed.xml"]

      async def parse_node(self, response, node):
          yield {"title": node.findtext("title"), "link": node.findtext("link")}

  result = RSSSpider().start()
  ```

- **ترقية خادم MCP إلى MCP SDK v2 وجعله أذكى**. يتضمن الخادم الآن تعليمات تشرح لوكيل الذكاء الاصطناعي كيفية استخدام الأدوات بكفاءة؛ وتعلن كل أداة عن خصائصها حتى تتمكن برامج مثل Claude Code من الموافقة تلقائيًا على الأدوات التي تقرأ فقط؛ وأصبحت أوصاف الأدوات أقصر لتقليل استهلاك tokens؛ ويعرض الخادم إصداره وشعاره لبرامج MCP. (راجع [التوثيق](ai/mcp-server.md))
- **إضافة الأمر `scrapling-mcp`** الذي يشغّل `scrapling mcp` مباشرةً، فأصبح تسجيل Scrapling في برامج وسجلات MCP التي تتوقع أمرًا واحدًا ممكنًا بسطر واحد.
- **إلغاء فرض إصدارات محددة من Playwright/Patchright والمتصفحات**. يطابق User-Agent الذي يُنشأ للمتصفح الآن دائمًا إصدار Chromium الفعلي الذي تشغّله نسخة Playwright/Patchright المثبتة لديك. لذلك لم يعد Scrapling يفرض إصدارات محددة منها ويمكنك ترقيتها بحرية. شغّل `scrapling install --force` بعد التحديث لتحديث المتصفحات.

### 🐛 إصلاحات الأخطاء {#v0.4.13-bug-fixes}

- **إصلاح تعطل استيراد Scrapling بخطأ ValueError من `browserforge`** عندما تكون حزمة بيانات البصمات أقدم من إصدارات المتصفح. (يصلح [#394](https://github.com/D4Vinci/Scrapling/issues/394)، و[#396](https://github.com/D4Vinci/Scrapling/issues/396)، و[#400](https://github.com/D4Vinci/Scrapling/issues/400))
- **إصلاح تحديد عدد الصفحات بشكل خاطئ في أدوات المتصفح الجماعية في MCP**، وهو ما كان يجعل `bulk_fetch` يفشل مع دفعات تزيد على 50 رابطًا، ويجعل `bulk_stealthy_fetch` يجلب كل الروابط عبر تبويب واحد، بمساهمة @Yigtwxx في [#393](https://github.com/D4Vinci/Scrapling/pull/393).

### المشروع {#v0.4.13-project}

- **[سياسة جديدة للمساهمات بمساعدة الذكاء الاصطناعي](https://github.com/D4Vinci/Scrapling/blob/main/AI_POLICY.md)**: نرحب بالمساهمات بمساعدة الذكاء الاصطناعي، لكن يجب ذكر ذلك في طلب الدمج أو البلاغ. تُضاف علامة إلى المساهمات التي تبدو مولّدة بالذكاء الاصطناعي دون الإفصاح عن ذلك، ثم تُغلق.

## [v0.4.12](https://github.com/D4Vinci/Scrapling/releases/tag/v0.4.12) - 2026-07-26 {#v0.4.12}

**إصدار يركز على جعل العناكب أذكى في التعامل مع المواقع التي تزحف إليها**

### 🚀 الجديد وتحسينات الاستخدام {#v0.4.12-new-stuff-and-quality-of-life-changes}

- **تستطيع العناكب الآن ضبط سرعتها تلقائيًا باستخدام AutoThrottle.** بدلًا من تخمين قيمة `download_delay` قد تكون بطيئة جدًا أو تؤدي إلى حظرك، يقيس العنكبوت سرعة رد كل موقع ويضبط فترة الانتظار لكل نطاق بنفسه. عندما يبدأ الموقع في حظرك أو تقييد معدل طلباتك، يضاعف فترة الانتظار (أو ينتظر المدة التي تطلبها ترويسة `Retry-After` بالضبط) حتى يتوقف ذلك، ثم يزيد السرعة مجددًا. تبقى قيمة `download_delay` وأي `Crawl-delay` في robots.txt حدًا أدنى. (راجع [التوثيق](spiders/advanced.md#autothrottle))

    ```python
    class MySpider(Spider):
        name = "adaptive"
        start_urls = ["https://example.com"]
        autothrottle_enabled = True
        autothrottle_start_delay = 2.0
        autothrottle_max_delay = 30.0
        autothrottle_block_backoff = True
    ```

- **تصدير النتائج إلى CSV وXML**، إلى جانب التصدير إلى JSON/JSONL المتاح سابقًا. تُصدَّر العناصر دون فقدان أي بيانات حتى لو اختلفت مفاتيحها، وتُكتب القيم المتداخلة بصيغة JSON. (راجع [التوثيق](spiders/getting-started.md))

    ```python
    result = MySpider().start()
    result.items.to_csv("products.csv")
    result.items.to_xml("products.xml")
    ```

- **يمكن لخادم MCP الآن طلب التحقق من الهوية**، حتى تتمكن من إتاحته بأمان بدلًا من حصره في جهازك. يُرفض أي طلب لا يحتوي على الرمز، ويمكنك أيضًا تحديد أسماء المضيفين التي يرد عليها الخادم. (راجع [التوثيق](ai/mcp-server.md))

    ```bash
    scrapling mcp --http --auth-token "$(openssl rand -hex 32)"
    ```

- **تقبل المتصفحات الآن روابط CDP عبر HTTP**، إلى جانب روابط WebSocket. فبالإضافة إلى عناوين `wss://` التي توفرها خدمات المتصفحات المُدارة، يمكنك الآن توصيل أي أداة جلب بالمتصفح أو جلسة MCP بمتصفح Chrome شغّلته بنفسك باستخدام `--remote-debugging-port=9222`.

- **أصبحت صور Docker المنشورة تحمل وسم رقم إصدارها** بدلًا من الاكتفاء بـ `latest`، حتى تتمكن من تثبيت الإصدار الذي تريده بالضبط، بمساهمة @JanRK في [#384](https://github.com/D4Vinci/Scrapling/pull/384).

### 🐛 إصلاحات الأخطاء {#v0.4.12-bug-fixes}

- **إصلاح فقدان كل ملفات cookies في الردود المخزنة مؤقتًا** عندما يأتي الرد من محرك متصفح، وهو ما كان يعطّل دون تنبيه أي منطق للجلسات أو التحقق من الهوية يعتمد عليها أثناء استخدام وضع تطوير العناكب، بمساهمة @amitvijapur في [#379](https://github.com/D4Vinci/Scrapling/pull/379). (يصلح [#376](https://github.com/D4Vinci/Scrapling/issues/376))

- **إصلاح فرض `StealthyFetcher` إعداد اللغة والمنطقة `en-US`** على كل متصفح بدلًا من اتباع إعداد نظامك. كان ذلك يجعل المواقع ترى اختلافًا بين إعداد اللغة والمنطقة وعنوان IP وتتعامل معك بشك، مثل ردود Google برمز 429. (يصلح [#381](https://github.com/D4Vinci/Scrapling/issues/381))

- **إصلاح رسالة خطأ مضللة في نظام التخزين** وإزالة استدعاء غير مستخدم كان متبقيًا بعد عمليات الإدراج، بمساهمة @fix2015 في [#377](https://github.com/D4Vinci/Scrapling/pull/377).

### الأداء {#v0.4.12-performance}

- **أصبح وقت تنفيذ `get_all_text()` يتناسب مع عدد العقد، أي O(nodes)** بدلًا من المرور على كل أسلاف كل عقدة نصية، مما يجعله أسرع بنحو 5-6 أضعاف في الصفحات ذات التداخل العميق، بمساهمة @yetval في [#378](https://github.com/D4Vinci/Scrapling/pull/378).

## [v0.4.11](https://github.com/D4Vinci/Scrapling/releases/tag/v0.4.11) - 2026-07-12 {#v0.4.11}

**تحديث يضيف أول قالب عنكبوت لمنصة محددة، ومحللًا أسرع، وإصلاحات مهمة 🎉**

### 🚀 الجديد وتحسينات الاستخدام {#v0.4.11-new-stuff-and-quality-of-life-changes}

- **إضافة `ShopifySpider`، أول قالب عنكبوت لمنصة محددة!** استخرج كل المنتجات من أي متجر يعمل بـ Shopify عبر JSON API دون التعامل مع HTML الموقع. أنشئ كلاس يرث منه، وحدد نطاق المتجر، وهذا كل ما تحتاجه (راجع [التوثيق](spiders/platform-templates.md))

  ```python
  from scrapling.spiders import ShopifySpider

  class MyStore(ShopifySpider):
      target_website = "example.com"

  result = MyStore().start()
  ```

- **إضافة `--executable-path` إلى أوامر المتصفح في CLI**. يقبل كل من `scrapling extract fetch` و`scrapling extract stealthy-fetch` الآن مسار ملف تشغيل متصفح مخصص متوافق مع Chromium، ويستخدمان متغير البيئة `SCRAPLING_EXECUTABLE_PATH` عند عدم تمرير الخيار، ليصبحا متوافقين تمامًا مع خادم MCP (يحل [#371](https://github.com/D4Vinci/Scrapling/issues/371))

  ```bash
  scrapling extract fetch "https://example.com" page.html --executable-path "/path/to/chromium"
  ```

### 🤖 تحسينات الاستخدام {#v0.4.11-quality-of-life-changes}
- **تسريع `find_by_text` و`find_by_regex` حتى نحو ضعفين** عند تفعيل `first_match` (وهو الإعداد الافتراضي)، بتحويل العناصر إلى كائنات عند الحاجة فقط حتى يتوقف البحث عند أول تطابق، بمساهمة @yetval في [#370](https://github.com/D4Vinci/Scrapling/pull/370)
- **تحديث اختبارات الأداء بالأرقام الجديدة مقارنةً بأحدث إصدارات كل المكتبات.**
- **تحديث قواعد المساهمة**

### 🐛 إصلاحات الأخطاء {#v0.4.11-bug-fixes}

- **إصلاح تعطل أدوات الجلب في خادم MCP مع الصفحات التي تحتوي على محارف تحكم** بالخطأ `All strings must be XML compatible`، بمساهمة @yetval في [#368](https://github.com/D4Vinci/Scrapling/pull/368) (يصلح [#366](https://github.com/D4Vinci/Scrapling/issues/366))

## [v0.4.10](https://github.com/D4Vinci/Scrapling/releases/tag/v0.4.10) - 2026-07-04 {#v0.4.10}

**تحديث جديد يضيف تكاملًا جديدًا مع Scrapy ومجموعة إصلاحات من المجتمع 🎉**

### 🚀 الجديد وتحسينات الاستخدام {#v0.4.10-new-stuff-and-quality-of-life-changes}

- **إضافة تكامل مع Scrapy** حتى تتمكن من استخدام واجهة التحليل في Scrapling داخل مشاريع Scrapy الحالية دون إعادة كتابتها. ضع الـ decorator المسمى `scrapling_response` على أي دالة callback للعنكبوت، فيصبح الرد الذي تستقبله كائن `Response` من Scrapling، بينما يواصل Scrapy إدارة الزحف (راجع [التوثيق](integrations/scrapy.md)):

    ```python
    import scrapy
    from scrapling.integrations.scrapy import scrapling_response

    class QuotesSpider(scrapy.Spider):
        name = "quotes"
        start_urls = ["https://quotes.toscrape.com"]

        @scrapling_response
        def parse(self, response):  # `response` is now a Scrapling Response
            first_quote = response.find_by_text("The world as we have created it", partial=True)
            for quote in [first_quote, *first_quote.find_similar()]:
                yield {"text": quote.get_all_text(strip=True)}
    ```

- **يمكن لخادم MCP الآن استخدام متصفح مخصص متوافق مع Chromium** لكل الأدوات التي تعتمد على المتصفح. اضبطه مرة واحدة باستخدام `scrapling mcp --executable-path "/path/to/chromium"` أو متغير البيئة `SCRAPLING_EXECUTABLE_PATH`، أو لكل طلب باستخدام الوسيط `executable_path`، بمساهمة @samrusani في [#360](https://github.com/D4Vinci/Scrapling/pull/360) (يحل [#347](https://github.com/D4Vinci/Scrapling/issues/347))
- **تحديث كل المتصفحات والبصمات**. شغّل `scrapling install --force` بعد التحديث لتحديثها.

### 🐛 إصلاحات الأخطاء {#v0.4.10-bug-fixes}

- **إصلاح النص المشوّه (mojibake) الناتج من أدوات الجلب بالمتصفح على مواقع لا تستخدم UTF-8**، بمساهمة @yehudalevy-collab في [#365](https://github.com/D4Vinci/Scrapling/pull/365) (يصلح [#364](https://github.com/D4Vinci/Scrapling/issues/364)).
- **إصلاح عدم تصفية `LinkExtractor` لامتدادات الملفات المركبة مثل `.tar.gz`**، بمساهمة @renbkna في [#359](https://github.com/D4Vinci/Scrapling/pull/359) (يصلح [#349](https://github.com/D4Vinci/Scrapling/issues/349)).
- **إصلاح فقدان الطلبات قيد التنفيذ من نقاط الاستكمال عند إيقاف الزحف مؤقتًا، فأصبح الاستكمال لا يتخطاها**، بمساهمة @yetval في [#358](https://github.com/D4Vinci/Scrapling/pull/358).
- **إصلاح حساب العناكب لفترات انتظار خاطئة من تعليمات `Request-rate` في robots.txt** عبر ترقية Protego، مع تحديث الاختبارات بما يناسب ذلك بمساهمة @Disaster-Terminator في [#355](https://github.com/D4Vinci/Scrapling/pull/355).

### التوثيق {#v0.4.10-docs}

- **توضيح كيفية تفاعل `init_script` مع سياق التنفيذ المعزول في Patchright في وضع التخفي**، بمساهمة @mturac في [#353](https://github.com/D4Vinci/Scrapling/pull/353) (يحل [#350](https://github.com/D4Vinci/Scrapling/issues/350)).
- **إضافة طريقة تثبيت مهارة الوكيل عبر [skills.sh](https://skills.sh/D4Vinci/Scrapling)**، بمساهمة @ob-aion في [#363](https://github.com/D4Vinci/Scrapling/pull/363).

## [v0.4.9](https://github.com/D4Vinci/Scrapling/releases/tag/v0.4.9) - 2026-06-07 {#v0.4.9}

**تحديث صيانة يضم الكثير من الإصلاحات التي أبلغ عنها المجتمع 🛠️**

### 🚀 الجديد وتحسينات الاستخدام {#v0.4.9-new-stuff-and-quality-of-life-changes}

- **تحديث كل المتصفحات والبصمات**. شغّل `scrapling install --force` بعد التحديث لتحديثها.
- **إضافة الخيار `--version` إلى CLI**، بمساهمة @ETM-Code في [#303](https://github.com/D4Vinci/Scrapling/pull/303) (يحل [#299](https://github.com/D4Vinci/Scrapling/issues/299))

### 🐛 إصلاحات الأخطاء {#v0.4.9-bug-fixes}

- **إصلاح تجاهل الوسيط `proxy` المحدد للجلسة دون تنبيه في جلسات HTTP**، وهو ما قد يكشف عنوان IP الحقيقي (يحل [#295](https://github.com/D4Vinci/Scrapling/issues/295)). لاحظ أن الجمع بين `proxy` على مستوى الجلسة والوسيط `proxies` على مستوى الطلب (أو العكس) يسبب الآن خطأ بدلًا من تجاهل أحدهما دون تنبيه.
- **إصلاح فشل الانتقال بين الصفحات عند الجمع بين `init_script` و`user_data_dir`** (يحل [#294](https://github.com/D4Vinci/Scrapling/issues/294)).
- **إصلاح اكتشاف الترميز عندما تضع المواقع قيمة charset بين علامتي اقتباس في ترويسة `Content-Type`**، بمساهمة @Bortlesboat في [#323](https://github.com/D4Vinci/Scrapling/pull/323).
- **إصلاح خطأ `IndexError` عند إعادة العثور على العناصر تكيفيًا مع تفعيل `auto_save`**، بمساهمة @Mubashirrrr في [#340](https://github.com/D4Vinci/Scrapling/pull/340).
- **إصلاح تعطل حفظ نقاط الاستكمال والذاكرة المؤقتة للعناكب على Windows**، بمساهمة @MrStarkEG في [#344](https://github.com/D4Vinci/Scrapling/pull/344).
- **إصلاح حساب نسبة تشابه خاطئة في `find_similar` للعناصر التي تختلف في عدد السمات** (يحل [#322](https://github.com/D4Vinci/Scrapling/issues/322)).

### التوثيق {#v0.4.9-docs}

- **توضيح أن التثبيت الافتراضي يشمل محرك التحليل فقط**، وأن أدوات الجلب والعناكب تحتاج إلى الإضافات الاختيارية (يحل [#343](https://github.com/D4Vinci/Scrapling/issues/343)).
- **إصلاح اسم صورة Docker في بقية الأمثلة**، بمساهمة @evanclan في [#315](https://github.com/D4Vinci/Scrapling/pull/315).
- **إصلاح رابط لا يعمل في دليل المساهمة**، بمساهمة @Bortlesboat في [#320](https://github.com/D4Vinci/Scrapling/pull/320).

## [v0.4.8](https://github.com/D4Vinci/Scrapling/releases/tag/v0.4.8) - 2026-05-11 {#v0.4.8}

**تحديث كبير للعناكب يطوّر نظام الزحف 🕷️**

### 🚀 الجديد وتحسينات الاستخدام {#v0.4.8-new-stuff-and-quality-of-life-changes}

- **إضافة أداة `LinkExtractor`** في `scrapling.spiders.LinkExtractor` لاستخراج الروابط من `Response`. توفر الكثير من خيارات التحكم (راجع [التوثيق](spiders/generic-templates.md))

    ```python
    from scrapling.spiders import LinkExtractor

    extractor = LinkExtractor(allow=r"/posts/", deny_domains=["ads.example.com"])
    ```

- **إضافة قالبي العناكب العامين `CrawlSpider` و`CrawlRule`** حتى لا تضطر إلى تكرار كتابة كود "اتبع الروابط التي تطابق هذا النمط". أعد تعريف `rules()` لإرجاع قائمة من كائنات `CrawlRule`، يرتبط كل منها بكائن `LinkExtractor`. (راجع [التوثيق](spiders/generic-templates.md))

    ```python
    from scrapling.spiders import CrawlSpider, CrawlRule, LinkExtractor

    class QuotesSpider(CrawlSpider):
        name = "blog"
        start_urls = ["https://quotes.toscrape.com/"]

        def rules(self):
            return [
                CrawlRule(LinkExtractor(allow=r"/author/"), callback=self.parse_author),
                CrawlRule(LinkExtractor(allow=r"/page/\d+/")),  # pagination, no callback
            ]

        async def parse_author(self, response):
            yield {
                "name": response.css(".author-title::text").get(),
                "birthday": response.css(".author-born-date::text").get(),
                "url": response.url,
            }
    ```

- **إضافة قالب `SitemapSpider`** الذي يبدأ الزحف مباشرةً من خريطة موقع أو روابط `robots.txt`. يدعم خرائط المواقع المضغوطة بـ gzip، ويوفر الكثير من خيارات التحكم والإعدادات. تُوزَّع الروابط باستخدام قواعد الزحف كما في مثال **CrawlSpider** أعلاه. (راجع [التوثيق](spiders/generic-templates.md))

    ```python
    from scrapling.spiders import SitemapSpider, CrawlRule, LinkExtractor

    class NewsSitemap(SitemapSpider):
        name = "news"
        sitemap_urls = ["https://example.com/robots.txt"]

        def rules(self):
            return [
                CrawlRule(LinkExtractor(allow=r"/articles/"), callback=self.parse_article),
            ]

        async def parse_article(self, response):
            yield {"url": response.url, "title": response.css("h1::text").get()}
    ```

- **أصبحت إعادة العثور على العناصر تكيفيًا تستخدم حد تشابه افتراضيًا قدره 40%** بدلًا من `0` في كل الدوال. يحسّن هذا عمل الميزة التكيفية. وعندما لا يتجاوز أي عنصر هذا الحد، يخبرك تحذير الآن بأعلى نسبة تشابه عُثر عليها، لتتمكن من خفض `percentage` عن قصد عند الحاجة.

- **تحديث كل المتصفحات والبصمات**. شغّل `scrapling install  --force` من جديد بعد التحديث لتحديث المتصفحات والبصمات.

### 🐛 إصلاحات الأخطاء {#v0.4.8-bug-fixes}

- **إصلاح عدم تطبيق `Fetcher.configure(...)` على الاستدعاءات لكل طلب**. طُبق الإصلاح نفسه على `AsyncFetcher`.
- **إصلاح حساب بصمات الطلبات بشكل خاطئ مما تسبب في تكرار الطلبات في العناكب**، بمساهمة @yetval في [#255](https://github.com/D4Vinci/Scrapling/pull/255).
- **إصلاح عدم تنبيه محرك الاستخراج التكيفي عند ضعف التطابق.** مع تغيير حد التشابه أعلاه، يظهر الآن تحذير بدلًا من عنصر مضلل باعتباره "أفضل تخمين" عندما تفشل إعادة العثور على العنصر.

### التوثيق {#v0.4.8-docs}

- **تحديث أمثلة الكود القديمة** في التوثيق لتطابق الإصدار الحالي.
- **تحسين نسخ الكود ولصقه** من موقع التوثيق، واختصار مهارة الوكيل لتستهلك عددًا أقل من tokens في كل استدعاء.

## [v0.4.7](https://github.com/D4Vinci/Scrapling/releases/tag/v0.4.7) - 2026-04-17 {#v0.4.7}

**تحديث يتيح لوكلاء الذكاء الاصطناعي رؤية الصفحات 📸**

### 🚀 الجديد وتحسينات الاستخدام {#v0.4.7-new-stuff-and-quality-of-life-changes}

- **إضافة أداة MCP باسم `screenshot`** تلتقط صورة للصفحة وتعيدها ككتلة MCP فعلية من نوع `ImageContent` حتى يتمكن النموذج من رؤيتها. تتطلب الأداة جلسة متصفح مفتوحة، لذلك استدعِ `open_session` أولًا (إما `dynamic` أو `stealthy`) ومرّر `session_id` هنا. تدعم PNG وJPEG، والتقاط الصفحة كاملة، وجودة JPEG، وخيارات انتظار الجاهزية المعتادة (`wait`، `wait_selector`، `network_idle`، `timeout`). (ينفذ [#244](https://github.com/D4Vinci/Scrapling/issues/244))
- **إضافة وسيط `session_id` مخصص إلى `open_session`** حتى تتمكن من تسمية الجلسات بأسماء واضحة (`"search"`، `"checkout"`) بدلًا من الاسم الافتراضي العشوائي المكوّن من 12 محرفًا بنظام hex. بمساهمة @hauntedhost في [#243](https://github.com/D4Vinci/Scrapling/pull/243)

### 🐛 إصلاحات الأخطاء {#v0.4.7-bug-fixes}

- **إصلاح تلف حالة `FetcherSession` والتعطل عند إغلاق جلسة مؤجلة البدء**. بمساهمة @yetval في [#245](https://github.com/D4Vinci/Scrapling/pull/245)
- **إصلاح الخطأ `TypeError: Session.request() got an unexpected keyword argument 'block_ads'`** عند استخدام خيار CLI المسمى `--ai-targeted` مع أوامر HTTP. بمساهمة @voidborne-d في [#249](https://github.com/D4Vinci/Scrapling/pull/249) (يصلح [#247](https://github.com/D4Vinci/Scrapling/issues/247))

### الترجمات {#v0.4.7-translations}

- **إضافة ترجمة README إلى البرتغالية البرازيلية** بمساهمة @rgomids في [#250](https://github.com/D4Vinci/Scrapling/pull/250)

## [v0.4.6](https://github.com/D4Vinci/Scrapling/releases/tag/v0.4.6) - 2026-04-13 {#v0.4.6}

**تحديث يركز على تخفي المتصفح والخصوصية وتجربة المطور 🔒**

### 🚀 الجديد وتحسينات الاستخدام {#v0.4.6-new-stuff-and-quality-of-life-changes}

- **إضافة حظر إعلانات مدمج** لأدوات الجلب بالمتصفح. مرّر `block_ads=True` لحظر الطلبات إلى نحو 3,500 نطاق معروف للإعلانات والتتبع عند اعتراض مسار الطلب، فيُلغى فورًا دون DNS أو TCP. يمكن الجمع بينه وبين `blocked_domains` لقوائم مخصصة. يفعّل خادم MCP ووضع CLI المسمى `--ai-targeted` هذا الخيار تلقائيًا لتقليل استهلاك tokens وتسريع تحميل الصفحات.

    ```python
    page = StealthyFetcher.fetch('https://example.com', block_ads=True)
    ```

- **إضافة دعم DNS-over-HTTPS** لمنع تسرب DNS عند استخدام proxies. مرّر `dns_over_https=True` لتوجيه استعلامات DNS عبر خدمة DoH من Cloudflare، حتى لا يكشف حل أسماء DNS موقعك الحقيقي عندما تمر حركة HTTP عبر proxy.

    ```python
    page = StealthyFetcher.fetch('https://example.com', proxy='http://proxy:8080', dns_over_https=True)
    ```

- **إضافة دالة callback باسم `page_setup`** لأدوات الجلب بالمتصفح. تعمل هذه الدالة قبل `page.goto()`، فتتيح لك تسجيل مستمعي الأحداث أو المسارات أو السكربتات التي يجب إعدادها قبل انتقال الصفحة. تعمل مع `page_action` (التي تُنفذ بعد الانتقال). (يحل [#237](https://github.com/D4Vinci/Scrapling/issues/237))

    ```python
    def capture_websockets(page):
        page.on("websocket", lambda ws: print(f"WS: {ws.url}"))

    page = DynamicFetcher.fetch('https://example.com', page_setup=capture_websockets)
    ```

- **إضافة خياري CLI المسمّيين `--block-ads` و`--dns-over-https`** إلى الأمرين `fetch` و`stealthy-fetch`.

### 🐛 إصلاحات الأخطاء {#v0.4.6-bug-fixes}

- **إصلاح رفض الاسم البديل للنوع `Seconds`** للقيم العشرية. كان تمرير `wait=1.5` أو `timeout=500.0` إلى أدوات الجلب بالمتصفح يفشل بخطأ نوع، لأن الاسم البديل كان يتعامل مع `float` كبيانات وصفية بدلًا من نوع. بمساهمة @kuishou68 في [#240](https://github.com/D4Vinci/Scrapling/pull/240)
- **إصلاح تكرار أجزاء ID عند إنشاء المحددات ذات المسار الكامل**. كانت محددات العناصر التي تحتوي على سمة `id` تُضاف مرتين عند إنشاء مسارات CSS/XPath الكاملة، فتنتج محددات مثل `body > #main > #main > #target > #target`. وأُصلح أيضًا إنتاج شروط `[@id='x']` وحدها (وهي XPath غير صالح) بدلًا من `*[@id='x']` في مسارات XPath الكاملة. بمساهمة @sjhddh في [#241](https://github.com/D4Vinci/Scrapling/pull/241)
- **إصلاح المعاملات الناقصة في تعريفات دوال shell**. كانت تعريفات الدوال في shell التفاعلية تفتقد `blocked_domains` و`block_ads` و`retries` و`retry_delay` و`capture_xhr` و`executable_path` و`dns_over_https`.

## [v0.4.5](https://github.com/D4Vinci/Scrapling/releases/tag/v0.4.5) - 2026-04-07 {#v0.4.5}

**تحديث يضيف ميزة كبيرة تسهّل عمل مطوري العناكب مع بعض الإصلاحات المهمة 🎉**

### 🚀 الجديد وتحسينات الاستخدام {#v0.4.5-new-stuff-and-quality-of-life-changes}

- **وضع تطوير العناكب**: كان تعديل منطق `parse()` في العنكبوت يتطلب إرسال طلبات إلى خوادم الموقع في كل تشغيل، وهو أمر بطيء ويزيد الضغط عليها، وقد يؤدي إلى تقييد معدل طلباتك وأنت ما زلت تضبط محدداتك. يخزّن وضع التطوير الجديد كل رد على القرص في أول تشغيل، ويعيد استخدامه من القرص في كل تشغيل لاحق. يمكنك بذلك تعديل دوال callback وإعادة التشغيل كما تريد دون إرسال أي طلب للشبكة. فعّله بخاصية واحدة في الكلاس:

    ```python
    class MySpider(Spider):
        name = "my_spider"
        start_urls = ["https://example.com"]
        development_mode = True

        async def parse(self, response):
            yield {"title": response.css("title::text").get("")}
    ```

    توجد الذاكرة المؤقتة افتراضيًا في `.scrapling_cache/{spider.name}/`، ويمكن تغيير مكانها باستخدام `development_cache_dir`. ويتيح لك عدّادان جديدان، `cache_hits` و`cache_misses`، معرفة أداء الذاكرة المؤقتة. تتجاوز إعادة استخدام الردود المخزنة `download_delay` وتقييد معدل الطلبات ومسار إعادة محاولة الطلبات المحظورة، لتصبح التجربة بأقصى سرعة يسمح بها القرص. لا تنشر عنكبوتًا مع `development_mode = True`؛ فهو أداة للتطوير وليس ذاكرة مؤقتة للاستخدام الفعلي. راجع [التوثيق](spiders/advanced.md#development-mode) للتفاصيل.

- **إعادة توجيه أكثر أمانًا افتراضيًا**: أصبحت القيمة الافتراضية لـ `follow_redirects` هي `"safe"` في كل أدوات جلب HTTP وخادم MCP وshell. لا يزال النظام يتبع عمليات إعادة التوجيه، لكنه يرفض ما يستهدف عناوين IP داخلية أو خاصة (loopback والشبكات الخاصة وlink-local). يحميك هذا من SSRF عند استخراج البيانات من روابط يقدمها المستخدمون. مرّر `follow_redirects="all"` للعودة إلى السلوك السابق، أو `False` لتعطيل إعادة التوجيه تمامًا.

### 🐛 إصلاحات الأخطاء {#v0.4.5-bug-fixes}

- **لم يعد الإيقاف الإجباري يفقد نقطة الاستكمال**: كان الضغط على Ctrl+C مرتين (الإيقاف الإجباري) لعنكبوت فعّل `crawldir` يتزامن مع كتابة نقطة الاستكمال. كان نطاق الإلغاء ينهي المهمة قبل اكتمال pickle، ويترك `paused=False` ويشغّل مسار التنظيف الذي *يحذف* نقطة الاستكمال السابقة. لذلك كان إيقاف زحف طويل إجباريًا قد يفقدك كل التقدم الذي تحاول حفظه. يكتب المحرك الآن نقطة الاستكمال **قبل** استدعاء `cancel_scope.cancel()`، فيحفظ الإيقاف الإجباري دائمًا أحدث حالة للطلبات المعلقة. بمساهمة @voidborne-d في [#230](https://github.com/D4Vinci/Scrapling/pull/230).

## [v0.4.4](https://github.com/D4Vinci/Scrapling/releases/tag/v0.4.4) - 2026-04-05 {#v0.4.4}

**تحديث جديد يضيف تحسينات مهمة للعناكب وإصلاحات للأخطاء 🎉**

### 🚀 الجديد وتحسينات الاستخدام {#v0.4.4-new-stuff-and-quality-of-life-changes}
- **إضافة الالتزام بقواعد robots.txt إلى نظام العناكب** عبر الخيار الجديد `robots_txt_obey`. عند تفعيله، يجلب العنكبوت قواعد robots.txt تلقائيًا ويلتزم بها قبل الزحف، بما فيها `Disallow` و`Crawl-delay` و`Request-rate`. تُجلب ملفات robots.txt بالتزامن وتُخزّن مؤقتًا لكل نطاق طوال الزحف. بمساهمة @AbdullahY36 في [#226](https://github.com/D4Vinci/Scrapling/pull/226)
- **إضافة تجهيز مسبق لذاكرة robots.txt المؤقتة** بحيث تُجلب وتُحلل ملفات robots.txt لكل نطاقات start_urls قبل بدء حلقة الزحف، لتجنب التأخير عند أول طلب لكل نطاق.
- **إضافة الإحصائية الجديدة `robots_disallowed_count`** إلى `CrawlStats` لمعرفة عدد الطلبات التي منعتها قواعد robots.txt أثناء الزحف.

اطلع عليها في الموقع من [هنا](spiders/getting-started.md#robotstxt-compliance)

### 🐛 إصلاحات الأخطاء {#v0.4.4-bug-fixes}
- **إصلاح مشكلة مهمة في ترتيب البحث عن الدوال MRO مع `ProxyRotator`**، حيث كان التعريف المبدئي لـ `_build_context_with_proxy` يحجب التنفيذ الفعلي في الكلاسات الفرعية، فتسبب تدوير proxies دائمًا في الخطأ `NotImplementedError` (يصلح [#215](https://github.com/D4Vinci/Scrapling/issues/215)). شكرًا @yetval
- **إصلاح تسرب في مجموعة الصفحات** عند استخدام تدوير proxies لكل طلب مع جلسات المتصفح. لم تكن الصفحات المنشأة داخل سياقات مؤقتة تُحذف من المجموعة عند التنظيف، مما أدى إلى تراكم مراجع قديمة مع الوقت. بمساهمة @yetval في [#223](https://github.com/D4Vinci/Scrapling/pull/223)
- **إصلاح غياب فحص يؤكد النوع** في أداة الجلب الثابتة، حيث كان يمكن أن تعيد `curl_cffi` القيمة `None` من `session.request()`، مما يسبب أخطاء لاحقًا.

### تغييرات أخرى {#v0.4.4-other}
- تحديث الاعتمادات، لتتوفر أحدث البصمات والتحديثات الأخرى.
- إضافة `protego` كاعتماد جديد ضمن المجموعة الاختيارية `fetchers` لتحليل robots.txt.

## [v0.4.3](https://github.com/D4Vinci/Scrapling/releases/tag/v0.4.3) - 2026-03-30 {#v0.4.3}

**تحديث جديد يضم الكثير من التغييرات المهمة 🎉**

### 🚀 الجديد وتحسينات الاستخدام {#v0.4.3-new-stuff-and-quality-of-life-changes}
- **إضافة أداة MCP جديدة** لفتح متصفح عادي أو خفي مستمر لاستخدامه مع بقية الأدوات، وأداة جديدة أخرى لإغلاقه. ([أمثلة](https://github.com/D4Vinci/Scrapling/blob/v0.4.3/docs/ai/mcp-server.md#examples))
- **إضافة أداة MCP جديدة** لعرض كل جلسات المتصفح الحالية، لاستخدامها مع الأدوات الجديدة.
- **إضافة خيار جديد إلى جلسات المتصفح** لجمع كل طلبات الخلفية التي تحدث أثناء الطلب تلقائيًا (يحل [#159](https://github.com/D4Vinci/Scrapling/pull/159)) [[أمثلة](https://github.com/D4Vinci/Scrapling/blob/v0.4.3/docs/fetching/dynamic.md#capturing-xhrfetch-requests)].
- **إضافة أداة تنظيف جديدة** لحماية خادم MCP من هجمات Prompt Injection الشائعة بإزالة المحتوى المخفي وغير المرئي.
- **إضافة خيار سطر أوامر جديد** باسم `--ai-targeted` إلى أوامر استخراج بيانات الويب لجعل المحتوى مناسبًا للذكاء الاصطناعي وآمنًا من هجمات Prompt Injection الشائعة كما في خادم MCP.
- **إضافة خيار جديد إلى جلسات المتصفح** باسم `executable_path` لتحديد مسار متصفح مخصص (يحل [#202](https://github.com/D4Vinci/Scrapling/pull/202))
- **إعادة تنظيم** كود خادم MCP لتسهيل صيانته، وجعل كل الأدوات تعمل بشكل غير متزامن.
- **إعادة تنظيم** كود أوامر CLI لتسهيل صيانته، واختصاره بمقدار 210 أسطر.

### 🐛 إصلاحات الأخطاء {#v0.4.3-bug-fixes}
- إصلاح يحافظ على طريقة HTTP عند إعادة المحاولة في جلسة العنكبوت، بمساهمة @karesansui-u في [#201](https://github.com/D4Vinci/Scrapling/pull/201)
- إضافة حد أقصى لمحاولات جلب محتوى الصفحة لمنع التكرار بلا نهاية، بمساهمة @haosenwang1018 و@D4Vinci في [#197](https://github.com/D4Vinci/Scrapling/pull/197)
- استبدال `raise` دون وسيط بـ `return False` في `_restore_from_checkpoint`، بمساهمة @haosenwang1018 في [#196](https://github.com/D4Vinci/Scrapling/pull/196)
- استبدال `get_all` بـ `getall` في `Texthandler` لتطابق كلاس Selector.

### تحسين الاختبارات وتغطيتها {#v0.4.3-coverage-tests-improvement}
- إضافة اختبارات للحالات الطرفية في `_normalize_credentials`، بمساهمة @Bortlesboat في [#192](https://github.com/D4Vinci/Scrapling/pull/192)
- إضافة اختبارات لعملية الحفظ ثم الاسترجاع وللتخزين الأساسي، بمساهمة @haosenwang1018 في [#193](https://github.com/D4Vinci/Scrapling/pull/193)
- إضافة اختبارات لمسارات regex في `TextHandler` ولـ `TextHandlers.re()`، بمساهمة @haosenwang1018 في [#194](https://github.com/D4Vinci/Scrapling/pull/194)
- إضافة اختبارات للحالات الطرفية في `filter` و`iterancestors` و`find_similar`، بمساهمة @awanawana في [#200](https://github.com/D4Vinci/Scrapling/pull/200)

### تحسين مهارة الوكيل {#v0.4.3-agent-skill-improvement}
- إصلاح روابط Markdown التي لا تعمل في مراجع المهارة، بمساهمة @yetval في [#204](https://github.com/D4Vinci/Scrapling/pull/204)
- تحسين تنظيم المهارة لتجتاز فحوص [Clawhub](https://clawhub.ai/d4vinci/scrapling-official) بصورة أفضل.
- إلزام المهارة باستخدام خيار سطر الأوامر `--ai-targeted` عند استخراج البيانات عبر أوامر سطر الأوامر.

### تحسين التوثيق {#v0.4.3-docs-improvement}
- إضافة ترجمة README إلى الكورية، بمساهمة @greatsk55 في [#187](https://github.com/D4Vinci/Scrapling/pull/187)
- إصلاح المسافات بين محارف CJK واللاتينية في ملفي README الصيني والياباني.
- إصلاح روابط لا تعمل من تصميم الموقع القديم.

## [v0.4.2](https://github.com/D4Vinci/Scrapling/releases/tag/v0.4.2) - 2026-03-08 {#v0.4.2}

**تحديث صيانة جديد مع تغييرات مهمة**

#### إصلاحات الأخطاء {#v0.4.2-bug-fixes}
- تلتقط الدالة `get_all_text()` الآن النص الذي يأتي بعد العناصر أيضًا. يتيح ذلك لخادم MCP والأوامر قراءة نص كان يفوتها من قبل ([#168](https://github.com/D4Vinci/Scrapling/pull/168)). شكرًا @mhillebrand
- أصبح Referer يعيد عنوان Google الأساسي بدلًا من رابط بحث Google. كان المنطق السابق غير صحيح، وقد يعطي المواقع علامة تساعدها في اكتشاف بصمة المتصفح ([#179](https://github.com/D4Vinci/Scrapling/pull/179)). شكرًا @Bortlesboat
- إصلاح مشكلة في دمج خيارات التشغيل الإضافية في جميع المتصفحات. شكرًا @rostchri
- إصلاح مشكلة في تلميحات الأنواع كانت تتسبب في تعطل الكود مع إصدارات Python الأقدم من 3.12. (يحل [#163](https://github.com/D4Vinci/Scrapling/issues/163))

#### تغييرات أخرى {#v0.4.2-other}
- إضافة Agent Skill لأدوات Claude Code / OpenClaw وغيرها من أدوات وكلاء الذكاء الاصطناعي.
- إضافة Agent Skill إلى Clawhub.
- تحديث جميع المتصفحات وPlaywright إلى أحدث الإصدارات.
- إضافة ترجمة فرنسية لملف README الرئيسي.

## [v0.4.1](https://github.com/D4Vinci/Scrapling/releases/tag/v0.4.1) - 2026-02-27 {#v0.4.1}

**تحديث جديد مع تغييرات مهمة كثيرة**

### 🚀 الجديد وتحسينات الاستخدام {#v0.4.1-new-stuff-and-quality-of-life-changes}
- **تحسين دقة regex** لاكتشاف تحديات Cloudflare (شكرًا @Rinz27 [#133](https://github.com/D4Vinci/Scrapling/pull/133))
- **تحسين سرعة وكفاءة** أداة حل تحديات Cloudflare. أصبحت الآن أسرع بنحو الضعف.
- **تحسين أداة حل تحديات Cloudflare** للتعامل مع المواقع التي تعرض صفحة Cloudflare مرتين أحيانًا قبل الانتقال إلى الموقع الأساسي.
- **تحسين التخفي وسرعة المتصفح المتخفي** بإزالة ملفات JS التي كانت تُحقن في الصفحات.
- **تحسين مخطط MCP** ليقبله OpenCode (شكرًا @robin-ede [#137](https://github.com/D4Vinci/Scrapling/pull/137))
- **تحسين توافق مخطط MCP مع المعيار** ليقبله VS Code Copilot وغيره من الأدوات التي تتحقق منه بدقة. (يحل #150 )
- **تقليل استهلاك خادم MCP للتوكنات** بدرجة كبيرة بإزالة وسوم HTML غير المفيدة عند تفعيل الخيار `main_content_only`.
- إصلاح صفحة PyPI وإضافة الملفات اللازمة لتسجيل خادم MCP في سجل خوادم MCP.
- إضافة مثال برمجي جديد يوضح تثبيت متطلبات المتصفحات من الكود بدلًا من سطر الأوامر، لتسهيل الأتمتة.
- تحسين جميع workflows باستخدام أحدث إصدارات actions (شكرًا @salmanmkc [#143](https://github.com/D4Vinci/Scrapling/pull/143)/[#144](https://github.com/D4Vinci/Scrapling/pull/144))

## [v0.4](https://github.com/D4Vinci/Scrapling/releases/tag/v0.4) - 2026-02-15 {#v0.4}

**أكبر إصدار من Scrapling حتى الآن - يقدم نظام العناكب وتدوير البروكسي وتحسينات كبيرة في محلل الصفحات**

يضيف هذا الإصدار نظام عناكب وزحف غير متزامن بالكامل، وإدارة ذكية للبروكسي، وتغييرات مهمة في API تجعل Scrapling أقوى وأكثر اتساقًا. يرجى قراءة قسم التغييرات التي قد تؤثر في الكود الحالي بعناية قبل التحديث.

### 🕷️ نظام العناكب {#v0.4-spider-framework}

نظام زحف جديد غير متزامن، مبني على `anyio` لاستخراج البيانات بصورة منظمة وعلى نطاق واسع:

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

-  **واجهة عناكب شبيهة بـ Scrapy**: عرّف العناكب باستخدام `start_urls` ودوال callback غير متزامنة باسم `parse` وكائنات `Request`/`Response` وطابور حسب الأولوية.
- **زحف بطلبات متزامنة**: يمكنك ضبط حدود التزامن، وسرعة الطلبات لكل نطاق، وفترات الانتظار بين التنزيلات.
- **دعم جلسات متعددة**: واجهة موحدة لطلبات HTTP والمتصفحات المتخفية التي تعمل دون واجهة داخل عنكبوت واحد. وجّه الطلبات إلى جلسات مختلفة حسب المعرّف. ويمكن تهيئة الجلسة عند أول استخدام فقط.
- **الإيقاف المؤقت والاستكمال**: حفظ حالة الزحف باستخدام نقاط الاستكمال. اضغط Ctrl+C للإغلاق المنظم، ثم شغّل العنكبوت مجددًا ليكمل من حيث توقف.
- **وضع البث**: استقبل البيانات فور استخراجها عبر `async for item in spider.stream()` مع إحصاءات مباشرة. يناسب واجهات المستخدم ومسارات معالجة البيانات وعمليات الزحف الطويلة.
- **اكتشاف الطلبات المحظورة**: اكتشاف الطلبات المحظورة وإعادة المحاولة تلقائيًا، مع إمكانية تخصيص المنطق.
- **تصدير مدمج**: صدّر النتائج عبر دوال hooks ومسار معالجة البيانات الذي تنشئه، أو إلى JSON/JSONL باستخدام `result.items.to_json()` / `result.items.to_jsonl()` على الترتيب.
- **دوال مراحل التشغيل**: `on_start()` و`on_close()` و`on_error()` و`on_scraped_item()` وغيرها للتحكم الكامل في مراحل الزحف.
- **إحصاءات زحف مفصلة**: تتبّع الطلبات والردود والبايتات وأكواد الحالة والبروكسي، وتفاصيل كل نطاق وجلسة، وعدد رسائل كل مستوى من مستويات السجل، وغيرها.
- **دعم uvloop**: مرّر `use_uvloop=True` إلى `spider.start()` لتسريع التنفيذ غير المتزامن عند توفره.

أُضيف قسم جديد إلى الموقع يحتوي على التفاصيل الكاملة. اضغط [هنا](spiders/architecture.md)

### 🔄 تدوير البروكسي {#v0.4-proxy-rotation}

* كلاس `ProxyRotator` جديد يدعم التدوير بأمان بين الخيوط. يعمل مع جميع أدوات الجلب والجلسات:

  ```python
  from scrapling import ProxyRotator
  rotator = ProxyRotator(["http://proxy1:8080", "http://proxy2:8080"])
  Fetcher.get(url, proxy_rotator=rotator)
  ```

* **طرق تدوير مخصّصة**: أنشئ منطق تدوير البروكسي الخاص بك
* **تغيير البروكسي لطلب واحد**: مرّر `proxy=` إلى أي استدعاء منفرد لـ `get()`/`post()`/`fetch()` لاستخدام بروكسي مختلف عن بروكسي الجلسة في هذا الطلب.

### 🌐 تحسينات أدوات الجلب بالمتصفح {#v0.4-browser-fetcher-improvements}

* **حظر النطاقات**: معامل `blocked_domains` جديد في `DynamicFetcher`/`StealthyFetcher` لحظر الطلبات إلى نطاقات محددة، ويشمل نطاقاتها الفرعية تلقائيًا.
* **إعادة المحاولة تلقائيًا**: تعيد أدوات الجلب بالمتصفح المحاولة الآن عند الفشل باستخدام المعاملين `retries` (الافتراضي: 3) و`retry_delay` (الافتراضي: 1s). ويشمل ذلك اكتشاف الأخطاء المرتبطة بالبروكسي.
* **بيانات الرد الإضافية**: يحفظ قاموس `Response.meta` البروكسي المستخدم تلقائيًا، ويدمج بيانات الطلب الإضافية.
* **Response.follow()**: إنشاء كائنات `Request` للمتابعة مع ضبط referer تلقائيًا، وهي مصمّمة لنظام العناكب.
* **منع التشغيل التلقائي**: تحظر جلسات المتصفح الآن تشغيل المحتوى تلقائيًا، لأنه كان يسبب مشكلات من قبل.
* **السرعة**: تحسين التخفي والسرعة بضبط خيارات تشغيل المتصفح.

### 🔧 إصلاحات الأخطاء والتحسينات {#v0.4-bug-fixes-improvements}
- **تحسين محلل الصفحات**: تحسين العمليات المتكررة في المحلل لرفع الأداء.
- **الصفحات التي تعطي أخطاء**: إصلاح خطأ كان يمنع إغلاق المتصفح عندما تعطي الصفحات أخطاء.
- **محتوى فارغ**: التعامل مع الردود التي لا تحتوي على محتوى.
- **حلقة Playwright**: حل مشكلة بقاء حلقة Playwright مفتوحة عند فشل اتصال CDP
- **سلامة الأنواع**: إصلاح جميع أخطاء mypy وإضافة تلميحات الأنواع داخل الدوال التي لم تكن تحدد الأنواع. وإضافة mypy وpyright إلى workflow الخاص بـ CI.

### ⚠️ تغييرات قد تؤثر في الكود الحالي {#v0.4-breaking-changes}

* **إزالة `css_first`/`xpath_first`**: استخدم `css('.selector').first` أو `css('.selector')[0]` أو `css('.selector').get()` بدلًا منهما.
* **جميع عمليات الاختيار تعيد `Selectors` الآن**: تعيد `css('::text')` و`xpath('//text()')` و`css('::attr(href)')` و`xpath('//@href')` الآن `Selectors`، مع تغليف العقد النصية في كائنات `Selector` لها `tag="#text"`، بدلًا من `TextHandlers`. يجعل هذا API متسقًا في جميع طرق الاختيار وتلميحات الأنواع.
* **`Response.body` دائمًا من نوع `bytes`**: كان من الممكن أن يكون `str` أو `bytes`، لكنه يعيد الآن `bytes` دائمًا.
* **سلوك `get()`/`getall()`**: في `Selector`: تعيد `get()` كائن `TextHandler`، أي HTML محوّلًا إلى نص أو القيمة النصية، وتعيد `getall()` كائن `TextHandlers`. الأسماء البديلة: `extract_first = get` و`extract = getall`. أُزيلت `get_all()` القديمة من `Selectors`.
* **`Selectors.first`/`.last`**: وصول آمن يعيد `Selector | None` بدلًا من إصدار `IndexError`.
* **تغيير أسماء الثوابت الداخلية**: `DEFAULT_FLAGS` → `DEFAULT_ARGS` و`DEFAULT_STEALTH_FLAGS` → `STEALTH_ARGS` و`HARMFUL_DEFAULT_ARGS` → `HARMFUL_ARGS` و`DEFAULT_DISABLED_RESOURCES` → `EXTRA_RESOURCES`.

### 🔨 تغييرات أخرى {#v0.4-other-changes}

* **تغييرات المتطلبات**: استبدال `tldextract` بـ `tld`، وإزالة `_html_utils.py` الداخلية واستخدام `w3lib.html.replace_entities` بدلًا منها، وإضافة `typing_extensions` كمتطلب أساسي.
* **تحديث شامل للتوثيق**: الانتقال الكامل من MkDocs إلى Zensical، وإضافة قسم لتوثيق العناكب، وتحديث جميع الصفحات الحالية، وإضافة مراجع API جديدة.

## [v0.3.14](https://github.com/D4Vinci/Scrapling/releases/tag/v0.3.14) - 2026-01-03 {#v0.3.14}

**تحديث صيانة صغير لإصلاح مشكلات ظهرت على بعض الأجهزة في v0.3.13**

- تعطيل وضع التصفح الخاص في `StealthyFetcher` وكلاسات جلساته، لأنه كان يمنع بقاء ملفات تعريف الارتباط بين الصفحات على أجهزة Windows. لم تظهر هذه المشكلة على MacOS وLinux (يصلح [#123](https://github.com/D4Vinci/Scrapling/issues/123)، شكرًا @frugality4121 على الإبلاغ عنها و@gembleman على توضيح الحل).
- تثبيت أحدث إصدار من browserforge لحل مشكلة نماذج headers القديمة لدى المستخدمين الذين لديهم إصدار قديم من browserforge.

## [v0.3.13](https://github.com/D4Vinci/Scrapling/releases/tag/v0.3.13) - 2026-01-01 {#v0.3.13}

**تحديث كبير مع تحسينات في أجزاء كثيرة، ومعه تغييرات كثيرة قد تؤثر في الكود الحالي لأسباب مهمة. يرجى قراءة ما يلي قبل التحديث**

* قررنا لأسباب كثيرة التوقف تمامًا عن استخدام Camoufox من الآن، وقد نعود إليه في المستقبل إذا استمر تطويره. إذا كنت تفضّل الاستمرار في استخدام Camoufox كما كان قبل هذا الإصدار، فستجد التعليمات في هذا [القسم](https://github.com/D4Vinci/Scrapling/blob/v0.3.13/docs/fetching/stealthy.md#using-camoufox-as-an-engine).

* كنا نستخدم patchright في وضع التخفي داخل `DynamicFetcher` وكلاسات جلساته. أزلنا الآن وضع التخفي منها وبدأنا استخدام patchright داخل `StealthyFetcher` وكلاسات جلساته، مع تحسينات كثيرة جدًا كما سترى، لتحسين التخفي فوق ما يقدمه patchright.

**يجعل هذا `StealthyFetcher` وكلاسات جلساته أسرع بنسبة 101%، مع استهلاك أقل للذاكرة والمساحة وكود أقصر بنحو ~400 سطر. والأهم أنها أصبحت أكثر استقرارًا مقارنة باستخدام Camoufox من قبل.**

سيقلل ذلك أيضًا وقت التثبيت عبر الأمر `scrapling install`، وحجم صورة Docker، ويحسن سير الاختبارات في CI على GitHub، ويجعل scrapling أوضح للمستخدمين الجدد.

### تغييرات قد تؤثر في الكود الحالي {#v0.3.13-breaking-changes}
1. أُزيل المعامل `stealth` من كلاس `DynamicFetcher` وكلاس جلسته، ونُقل المعامل `hide_canvas` إلى `StealthyFetcher` وكلاسات جلساته.
2.  نُقل المعامل `disable_webgl` من `DynamicFetcher` إلى كلاس `StealthyFetcher` وتغير اسمه إلى `allow_webgl`. وينطبق ذلك على جميع كلاسات الجلسات أيضًا.
3. أصبح كلاس `StealthyFetcher` هو النسخة المتخفية الجديدة من `DynamicFetcher`، لذا أُزيلت المعاملات التالية: `block_images` و`humanize` و`addons` و`os_randomize` و`disable_ads` و`geoip`. حاولت توفيرها في Chromium، لكن لكل منها مشكلة خاصة بها. قد يتغير هذا في الإصدارات القادمة قبل v0.4.

والآن إلى الأخبار الجيدة، فقد أجرينا تحسينات وإصلاحات كثيرة :)

### التحسينات {#v0.3.13-improvements}
- تعرف بالفعل أن كلاس `StealthyFetcher` وكلاسات جلساته أصبحت أسرع بنسبة 101%، لكن كلاس `DynamicFetcher` وكلاس جلسته أصبحا أسرع بنسبة 20% أيضًا.
- تحسين خوارزمية حل تحديات Cloudflare لتعمل أسرع وتتعامل مع حالات أكثر. وبفضل إعادة تنظيم الكود، يمكنك توقع حل captcha بضعف السرعة!
- جميع أدوات الجلب تستهلك الآن ذاكرة أقل.
- خادم MCP يستخدم الآن توكنات أقل لتوفير المزيد من المال!
- أصبحت صورة Docker أصغر بنسبة 60%.
- تحديث موقع التوثيق بالكامل بالمزايا الجديدة. وجعل الشرح أوضح، واختصار أقسام كثيرة، وإضافة أمثلة أكثر والمعاملات التي كانت ناقصة، وتحديث قسم مرجع API برسوم توضيحية، وإجراء تحسينات أخرى كثيرة. أصبح الموقع الآن أسرع في التحميل بنسبة 130%، ويستهلك بيانات أقل، وأفضل لمحركات البحث SEO.

### الإصلاحات {#v0.3.13-fixes}
- إضافة المعاملات التي كانت ناقصة في اختصارات Web Scraping shell وجعلها أدق.
- إصلاح مشكلة كان فيها المعامل `google_search` ينشئ Google referrer حتى لو كان عنوان URL يشير إلى localhost/IP.

## [v0.3.12](https://github.com/D4Vinci/Scrapling/releases/tag/v0.3.12) - 2025-12-18 {#v0.3.12}

### ما الذي تغير {#v0.3.12-what-s-changed}
- إضافة معامل جديد إلى كلاسَي `DynamicSession`/`AsyncDynamicSession` باسم `timezone_id`، يتيح ضبط المنطقة الزمنية للمتصفح لتطابق منطقة البروكسي/VPN الذي تستخدمه. بهذه الطريقة، لا تستطيع المواقع اكتشاف استخدامك للبروكسي من اختلاف المنطقة الزمنية.
- تحسين التحويل التلقائي للرد إلى JSON.
- تغيير اسم الدالة الداخلية `__create__` إلى `start` داخل كلاسات جلسات أدوات الجلب لتسهيل استخدامها خارج سياق `with`.
- تحديث `curl_cffi` والمتطلبات الأخرى إلى أحدث الإصدارات.

## [v0.3.11](https://github.com/D4Vinci/Scrapling/releases/tag/v0.3.11) - 2025-12-03 {#v0.3.11}

### ما الذي تغير {#v0.3.11-what-s-changed}
- تحسين منطق التعامل مع أخطاء انتهاء المهلة عند استخدام المعامل `network_idle` مع موقع غير مستقر، مثل المواقع التي تشغّل وسائط باستمرار.
- إصلاح الإكمال التلقائي للاختصار `stealthy_fetch` في Web Scraping Shell

## [v0.3.10](https://github.com/D4Vinci/Scrapling/releases/tag/v0.3.10) - 2025-11-26 {#v0.3.10}

**تحديث صيانة مع تغييرات مهمة كثيرة، وبعضها قد يؤثر في الكود الحالي**

- **حل** جميع مشكلات الترميز باستخدام طريقة أفضل تتعامل مع صفحات الويب التي لا تحدد الترميز بصورة صحيحة (شكرًا @Kemsty2 على الجهد المبذول في توضيح المشكلة في [#110](https://github.com/D4Vinci/Scrapling/issues/110) [#111](https://github.com/D4Vinci/Scrapling/pull/111) )
- **حل** مشكلة منطقية في استبدال معاملات الجلسة بمعاملات الطلب في جميع أدوات الجلب بالمتصفح، وكانت موجودة منذ v0.3
- **إصلاح** تعريفات اختصارات shell التفاعلي لاستخراج البيانات من الويب، مما جعل الإكمال التلقائي لهذه الاختصارات يعمل بصورة كاملة. كانت هذه المشكلة موجودة منذ v0.3 أيضًا.
- **تحديث** إصدار قاعدة بيانات Maxmind، مما يحسن عمل المعامل `geoip` في `StealthyFetcher` وكلاسات جلساته.
- **تحديث** جميع المتصفحات المستخدمة إلى أحدث الإصدارات المتاحة.
- **تغييرات قد تؤثر في الكود الحالي** - أُعيد تنظيم جميع أدوات الجلب بشكل كبير، مما نتج عنه تغييرات مهمة قد تؤثر في كودك:
    1. أصبح كود Scrapling أقصر بنحو ~750 سطرًا، مع تغييرات كثيرة تجعل صيانته أسهل في المستقبل وتقلل استهلاك الموارد قليلًا.
    2. أصبح التحقق من المعاملات أسرع بكثير في جميع أدوات الجلب وكلاسات جلساتها، مما يرفع سرعتها عمومًا.
    3. لتحقيق ذلك، لم تعد أدوات الجلب تقبل معاملات موضعية غير المعامل `url`. يجب تمرير بقية المعاملات بأسمائها، فيكون كودك مثل `Fetcher.get('https://google.com', stealthy_headers=True)` وليس `Fetcher.get('https://google.com', True)` إذا كنت تفعل ذلك لأي سبب!
    4. كان هناك اختلاف مزعج بين أدوات الجلب بالمتصفح وكلاسات جلساتها منذ v0.3: المعامل المستخدم لتمرير إعدادات مخصّصة للمحلل لكل طلب كان اسمه `custom_config`، بينما كان اسمه `selector_config` في كلاسات الجلسات. أتاحت إعادة تنظيم الكود توحيد الاسم إلى `selector_config` دون تعطيل كودك، ليصبح الاسم الأساسي الآن `selector_config` مع استمرار دعم المعامل القديم `custom_config`. سيتوفر الإكمال التلقائي للمعامل `selector_config` فقط.
    5. ولتحقيق كل ذلك، أصبح من الضروري توليد تلميحات الأنواع لدوال أدوات الجلب تلقائيًا. إذا لم يعمل الإكمال التلقائي جيدًا في IDE، فتأكد من استخدام إصدار حديث منه. اختبرنا تقريبًا جميع بيئات التطوير والمحررات المعروفة.

> حدّثنا أيضًا جميع جداول قياس الأداء بالأرقام الحالية، مع المقارنة بأحدث إصدارات جميع المكتبات البديلة.

## [v0.3.9](https://github.com/D4Vinci/Scrapling/releases/tag/v0.3.9) - 2025-11-17 {#v0.3.9}

**تحديث جديد مع تغييرات مهمة كثيرة**

### 🚀 الجديد وتحسينات الاستخدام {#v0.3.9-new-stuff-and-quality-of-life-changes}
- يقبل المعامل `impersonate` في `Fetcher` و`FetcherSession` الآن قائمة متصفحات تختار منها المكتبة متصفحًا عشوائيًا مع كل طلب.

```python
from scrapling.fetchers import FetcherSession

with FetcherSession(impersonate=['chrome', 'firefox', 'safari']) as s:
  s.get('https://github.com/D4Vinci/Scrapling')
```

- إضافة معامل جديد إلى الدالة `clean` في `TextHandler` لإزالة HTML entities من النص الحالي بسهولة.
- تحسينات كبيرة في التوثيق مع شرح أدق لأجزاء كثيرة وترجمات آلية لملف `README.md` الرئيسي.

### 🐛 إصلاحات الأخطاء {#v0.3.9-bug-fixes}
- إصلاح مشكلة كبيرة في استرجاع الردود من أدوات الجلب بالمتصفح. يوجد الآن اكتشاف ذكي لنوع المحتوى، يضمن أن `response.body` يحتوي على المحتوى الذي عرضه المتصفح فقط إذا كان المحتوى HTML. وفي غير ذلك، يحتوي على المحتوى الخام لآخر طلب. يتيح هذا تنزيل الملفات الثنائية والنصية دون تغليفها بوسوم HTML، مع الاحتفاظ بإمكانية استرجاع محتوى الموقع بعد عرضه في المتصفح عند جلبه.

### 🔨 تغييرات متنوعة {#v0.3.9-misc}
- تحديث دليل المساهمة ليكون أوضح وأسهل.
- إضافة workflow جديد لفرض استخدام أدوات جودة الكود، وهي الأدوات نفسها المستخدمة في pre-commit hooks.

## [v0.3.8](https://github.com/D4Vinci/Scrapling/releases/tag/v0.3.8) - 2025-10-27 {#v0.3.8}

**تحديث جديد مع تغييرات مهمة كثيرة**

### 🚀 الجديد وتحسينات الاستخدام {#v0.3.8-new-stuff-and-quality-of-life-changes}
- في جميع أدوات الجلب بالمتصفح: لن تتسبب المواقع التي لا تنتهي طلباتها من التحميل في تعطل الكود عند استخدام `network_idle` معها.
- تغيير منطق جمع محتوى الصفحة والتحقق منه في أدوات الجلب بالمتصفح، لجعل المتصفحات على Windows مستقرة مثل Linux/MacOS. يرجع هذا الاختلاف في السلوك إلى اختلاف طريقة عمل Playwright على Windows.
- إعادة تنظيم منطق التحقق من المعاملات بالكامل، مما جعل الطلبات في جميع أدوات الجلب بالمتصفح أسرع بنسبة 8-15%
- إضافة خيار جديد باسم `extra_flags` إلى `DynamicFetcher` وجلسته، ليتيح إضافة خيارات Chrome مخصّصة إلى الخيارات الحالية عند تشغيل المتصفح.
- إعادة منطق توجيه الطلبات لالتقاط الردود، الذي تغير في الإصدار السابق، إلى الطريقة القديمة عند استخدام `page_action`. يتيح هذا جمع أحدث محتوى للصفحة إذا غيّره `page_action` دون إرسال طلب. (شكرًا @gembleman على توضيح ذلك في [#100](https://github.com/D4Vinci/Scrapling/issues/100) و[#102](https://github.com/D4Vinci/Scrapling/pull/102) )

### 🐛 إصلاحات الأخطاء {#v0.3.8-bug-fixes}
- إصلاح خطأ كتابي في `load_dom` داخل async_fetch في DynamicSession
- إصلاح مشكلة في أداة حل تحديات Cloudflare كانت تجعلها تنتظر دون نهاية عند التعامل مع captcha مضمنة لا تختفي بعد حلها. تنتظر الآن 30 ثانية حتى تختفي، ثم تفترض أنها من النوع الذي لا يختفي (يصلح #100 )

### 🔨 تغييرات متنوعة {#v0.3.8-misc}
- تُرفع صورة Docker الآن تلقائيًا إلى Dockerhub وسجل الحاويات في GitHub لتسهيل استخدامها.
- إضافة [صفحة توثيق جديدة](https://github.com/D4Vinci/Scrapling/blob/v0.3.8/docs/tutorials/external.md) توضح كيفية استخدام متصفح Scrapeless مع Scrapling.

## [v0.3.7](https://github.com/D4Vinci/Scrapling/releases/tag/v0.3.7) - 2025-10-12 {#v0.3.7}

**تحديث جديد مع تغييرات مهمة كثيرة**

### 🚀 الجديد وتحسينات الاستخدام {#v0.3.7-new-stuff-and-quality-of-life-changes}
- إعادة تصميم المعامل `solve_cloudflare` في `StealthyFetcher` ليحل جميع صور الاستخدام المخصّص لـ Turnstile.
- إعادة تنظيم الكود بالكامل ليقبله Pyright، لتحسين العمل في جميع بيئات التطوير وحل أخطاء كثيرة.
- إعادة تنظيم منطق الطلبات ليكون أبسط وأسرع (يحل #97 أيضًا )
- إضافة خيار جديد باسم `user_data_dir` إلى جميع كلاسات جلسات المتصفح، ليتيح إعادة استخدام بيانات المتصفح من جلسات سابقة، مثل cookies والتخزين وغيرها. تركه دون قيمة يجعل Playwright يستخدم مجلدًا عشوائيًا في كل تشغيل، كما كان يحدث من قبل.
- إضافة خيار تخصيص جديد باسم `additional_args` إلى `Dynamic fetcher` وكلاس جلسته، لتمرير معاملات إضافية إلى سياق Playwright، كما كان متاحًا من قبل مع `StealthyFetcher`.
- تحسين منطق توجيه الطلبات لجمع آخر رد ناتج عن التنقل في جميع المتصفحات، مما يتيح تمرير الردود الخام إلى المحلل قبل أن تعالجها المتصفحات كما كان يحدث من قبل. يفيد هذا كثيرًا مع الردود النصية وردود JSON.

### 🐛 إصلاحات الأخطاء {#v0.3.7-bug-fixes}
- حل تغيير منطق توجيه الطلبات مشكلة استرجاع محتوى المواقع غير المستقرة على بعض أجهزة Windows.
- أدت إعادة تنظيم الكود في هذا الإصدار إلى حل أخطاء كثيرة كان من الصعب ملاحظتها، ومشكلات غريبة في الإكمال التلقائي ببعض بيئات التطوير.
- إصلاحات كثيرة في موقع التوثيق

## [v0.3.6](https://github.com/D4Vinci/Scrapling/releases/tag/v0.3.6) - 2025-10-01 {#v0.3.6}

### 🚀 الجديد {#v0.3.6-new-stuff}
- تحسين المعامل `solve_cloudflare` في `StealthyFetcher` وكلاسات جلساته ليحل جميع أنواع Turnstile وتحديات Cloudflare التي تظهر في صفحة وسيطة 🎉
- خادم MCP يدعم الآن خيار `Streamable HTTP`، لتسهيل إتاحة الخادم عبر الشبكة.
- إضافة دعم Docker، مع بناء صورة ورفعها تلقائيًا إلى Docker Hub مع كل إصدار، وتشمل جميع المتصفحات

### 🐛 إصلاحات الأخطاء {#v0.3.6-bug-fixes}
- إصلاح مشكلة ترميز في المحلل كانت تحدث في بعض الحالات، وهي رسالة الخطأ المعروفة `invalid start byte`
- إعادة تنظيم أجزاء متعددة من المكتبة لإصلاح بعض حالات تسرب الذاكرة، مما يقلل استهلاك الذاكرة بصورة ملحوظة حسب إعداداتك (يحل #92 أيضًا )
- تحسين تلميحات الأنواع في أجزاء كثيرة من الكود لتسهيل العمل في IDE (يحل #93 أيضًا )

## [v0.3.5](https://github.com/D4Vinci/Scrapling/releases/tag/v0.3.5) - 2025-09-20 {#v0.3.5}

**إصدار ضروري لإصلاح عدة مشكلات**

### 🚀 الجديد {#v0.3.5-new-stuff}
- جميع أدوات الجلب بالمتصفح (`DynamicFetcher`/`StealthyFetcher`/...) وكلاسات جلساتها تجلب المواقع الآن أسرع بنسبة 15-20%:
    1. أصبحت إدارة الصفحات أسرع بكثير بفضل تحسين المنطق من @AbdullahY36 في #87
    2. تحسين منطق التحقق من المعاملات عمومًا، وتحسين إنشاء الصفحات في عمليات الجلب المتزامنة. أدت هذه التغييرات معًا إلى تحسينات كبيرة في السرعة

- تحسينات كبيرة لوضع التخفي في `DynamicFetcher` وكلاسات جلساته باستبدال `rebrowser-playwright` بـ `PatchRight`:
    1. قبل هذا التحديث، كان `rebrowser-playwright` يتوقف عند تفعيل `stealth` و`real_chrome` لأنهما لم يكونا يعملان جيدًا معًا. لم تعد هذه المشكلة موجودة مع `PatchRight`
    2. يمكنك الآن التعامل مع Closed-Shadow Roots لأن `PatchRight` يتعامل معها تلقائيًا.

### 🐛 إصلاحات الأخطاء {#v0.3.5-bug-fixes}
- إصلاح خطأ يحدث عند استخدام الدالة `re` من كلاس `Selectors`.
- إصلاح خطأ في أمرَي `uncurl` و`curl2fetcher` في Web Scraping Shell كان يسبب تحليلًا غير صحيح لخيار curl المسمى `--data-raw`.
- إصلاح خطأ في الأمر `view` في Web Scraping Shell كان ظهوره مرتبطًا بترميز الموقع.
- إصلاح خطأ في تحويل المحتوى كان يؤثر في وضع `mcp` وأوامر `extract`.

### مساهمون جدد {#v0.3.5-new-contributors}
- قدّم @AbdullahY36 أول مساهمة له في #87

## [v0.3.4](https://github.com/D4Vinci/Scrapling/releases/tag/v0.3.4) - 2025-09-16 {#v0.3.4}

**إصدار ضروري لإصلاح عدة مشكلات**

### 🚀 الجديد {#v0.3.4-new-stuff}
- إضافة جميع كلاسات جلسات أدوات الجلب إلى shell التفاعلي لتكون متاحة مباشرة دون استيراد.

### 🐛 إصلاحات الأخطاء {#v0.3.4-bug-fixes}
- إضافة حل بديل لخطأ في Playwright API على Windows كان يحدث عند استرجاع المحتوى أثناء حل تحديات Cloudflare.
- إصلاح مشكلة ترميز في الأمر `view` داخل shell التفاعلي
- إصلاح خطأ في المعامل `max_pages` في `AsyncStealthySession` كان يتسبب في تعطل الكود.
- إصلاح مشكلة ظهرت مع التحديثات الأخيرة وجعلت الخاصيتين `html_content` و`prettify` في كلاس `Selector` تعيدان bytes حسب الترميز. عادتا إلى إرجاع نصوص كما كانتا.

## [v0.3.3](https://github.com/D4Vinci/Scrapling/releases/tag/v0.3.3) - 2025-09-15 {#v0.3.3}

- إزالة منطق إغلاق تبويب المتصفح الافتراضي من أدوات الجلب بالمتصفح لأنه تسبب في خطأ يعطّل الكود. لم يحدث على Mac، وأمكن تكراره على Windows وLinux فقط

## [v0.3.2](https://github.com/D4Vinci/Scrapling/releases/tag/v0.3.2) - 2025-09-15 {#v0.3.2}

ملاحظات إصدار v0.3.2

### 🚀 الجديد {#v0.3.2-new-stuff}

- **متطلبات اختيارية لأدوات الجلب**: أصبحت جميع أدوات الجلب ضمن مجموعات متطلبات اختيارية، لتقليل حجم الحزمة الأساسية. تحتوي حزمة `scrapling` الأساسية الآن على المحلل فقط، ولاستخدام أدوات الجلب أو خيارات سطر الأوامر، نفّذ: `pip install "scrapling[fetchers]"`. راجع تعليمات التثبيت المفصلة [هنا](index.md#installation)
- **إعدادات لكل صفحة داخل الجلسات**: تدعم كلاسات جلسات أدوات الجلب بالمتصفح الآن إعدادات منفصلة لكل صفحة في الجلسة. يجري التحقق من جميع معاملات الجلب مثل معاملات الجلسة. التفاصيل على موقع التوثيق [هنا](fetching/stealthy.md#full-list-of-arguments)
    <br>مثال:

    ```python
    with StealthySession(headless=True, solve_cloudflare=True) as session:
        page = session.fetch('https://nopecha.com/demo/cloudflare', google_search=False)
    ```

- **تحسين أدوات الجلب بالمتصفح**
    - خيار جديد للتحكم في انتظار انتهاء تنفيذ JavaScript في الصفحات. الخيار مفعّل افتراضيًا الآن، كما كان من قبل

        ```python
        with DynamicSession(headless=True, disable_resources=False, network_idle=True) as session:
           page = session.fetch('https://quotes.toscrape.com/', load_dom=False)
        ```

    - أصبح وضع التخفي أكثر موثوقية في `DynamicFetcher` وكلاسات جلساته.
    - يستخدم `DynamicFetcher` و`StealthyFetcher` الآن موارد أقل، باكتشاف التبويب الافتراضي الذي تفتحه السياقات الدائمة في Playwright API وإغلاقه تلقائيًا
    - إصلاح خطأ مهم في منطق تدوير الصفحات بأدوات الجلب بالمتصفح. تُستبدل الصفحات السابقة الآن بصفحات جديدة، لأن التبويبات التي يُعاد استخدامها قد تحتفظ بآثار الإعدادات السابقة
    - أصبح `StealthyFetcher` وكلاسات جلساته أسرع قليلًا (5%)

- **تحسين الخاصية `.body`**: تعيد الآن المحتوى الممرّر كما هو دون معالجة، مما يتيح تنزيل الملفات والتعامل مع الطلبات التي لا تعيد HTML. المثال التالي يوضح تنزيل صورة:

    ```python
    from scrapling.fetchers import Fetcher

    page = Fetcher.get('https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/poster.png')
    with open(file='poster.png', mode='wb') as f:
        f.write(page.body)
    ```

### 🐛 إصلاحات الأخطاء {#v0.3.2-bug-fixes}

- **حل مشكلات الترميز**: إصلاح مشكلات ترميز متعددة ظهرت مع بعض المواقع في المحلل ووضع mcp وأوامر extract (يحل #80 و#81 أيضًا)
- **تحليل أسرع**: بفضل تغييرات كثيرة في أجزاء مختلفة، أصبحت المكتبة أسرع، وهو ما يظهر في نتائج قياس الأداء المحدّثة

### 🔨 تغييرات متنوعة {#v0.3.2-misc}

- **تحديث قياسات الأداء**: تحديث القياسات لمقارنة تحسينات السرعة الحالية بأحدث إصدارات المكتبات المشابهة
- **إعادة تنظيم أجزاء كثيرة من الكود واستبدال الكود غير المستخدم بطرق أفضل**: كود أقل وأبسط وصيانة أسهل
- **إضافة فيديو YouTube**: إضافة محتوى فيديو إلى توثيق MCP.
- **نموذج جديد للمشكلات**: نموذج جديد وسهل للمستخدمين الذين لا يستطيعون استخدام النماذج الحالية.
- **تحسين workflow الخاص بـ CI**: تتجاوز اختبارات workflow التشغيل الآن عندما تقتصر التغييرات على التوثيق أو الملفات التي لا تحتوي على كود.
- **تحديث المتطلبات**: تحديث متطلبات مختلفة إلى أحدث الإصدارات.
- **تحسين أسلوب الكود**: تطبيق قواعد ruff جديدة على جميع الملفات.
- **Pre-commit hooks**: تحديث إعدادات pre-commit.

### 🎯 تغييرات قد تؤثر في الكود الحالي {#v0.3.2-breaking-changes}

- إزالة المعامل `max_pages` من النسخة المتزامنة من `StealthySession` لتطابق `DynamicSession`، لأنه لا فائدة منه في النسخة المتزامنة

## [v0.3.1](https://github.com/D4Vinci/Scrapling/releases/tag/v0.3.1) - 2025-09-02 {#v0.3.1}

1. إصلاح مشكلة في تثبيت scrapling عند تثبيته دون الإضافة `shell` (#76 )
2. إضافة معامل جديد إلى جميع أدوات الجلب بالمتصفح وكلاسات جلساتها لإضافة ملف JS يُنفّذ عند إنشاء الصفحة (#56) :

```python
from scrapling.fetchers import StealthyFetcher

StealthyFetcher.fetch('https://example.com', init_script="/absolute/path/to/js/script.js")
```

## [v0.3](https://github.com/D4Vinci/Scrapling/releases/tag/v0.3) - 2025-09-01 {#v0.3}

🎉 **إصدار رئيسي - إعادة بناء كاملة**

يمثل Scrapling v0.3 أكبر تحديث في تاريخ المشروع. يشمل إعادة كتابة كاملة للبنية، وتحسينات كبيرة في الأداء، وميزات قوية جديدة، منها التكامل مع الذكاء الاصطناعي وبيئة تفاعلية لاستخراج البيانات من الويب.

يتضمن هذا الإصدار عدة تغييرات قد تؤثر في الكود الحالي. اقرأ ملاحظات الإصدار بعناية.

### 🚀 أهم الميزات الجديدة {#v0.3-major-new-features}

#### بنية تعتمد على الجلسات {#v0.3-session-based-architecture}
- **فئات جديدة للجلسات**: إعادة كتابة كاملة لإضافة دعم الجلسات التي تبقى مفتوحة
    - `FetcherSession` - طلبات HTTP مع حفظ حالة الجلسة، وتعمل مع الكود المتزامن وغير المتزامن
    - `DynamicSession`/`AsyncDynamicSession` - أتمتة المتصفح مع إبقائه مفتوحًا حتى تنتهي
    - `StealthySession`/`AsyncStealthySession` - تصفح متخفٍ مع إبقاء المتصفح مفتوحًا حتى تنتهي
- **إدارة تبويبات المتصفح بشكل غير متزامن**: مجموعة جديدة من التبويبات عبر الخيار `max_pages`، يعاد استخدامها بالتناوب لجلب الصفحات في الوقت نفسه
- **جلسات متوازية**: تشغيل عدة جلسات مستقلة في الوقت نفسه

راجع قسم `Fetching` في الموقع لمعرفة المزيد.

#### ميزات كثيرة جديدة للتخفي وتجاوز أنظمة مكافحة الروبوتات {#v0.3-a-lot-of-new-stealth-anti-bot-capabilities}
- **🤖 حل تحديات Cloudflare**: [حل تحديات Cloudflare Turnstile تلقائيًا](fetching/stealthy.md#cloudflare-and-stealth-options) في `StealthyFetcher` وفئات الجلسات الخاصة به
- **محاكاة بصمة المتصفح**: محاكاة بصمات TLS للمتصفحات الحقيقية، وترويسات تطابق إصدار المتصفح، ودعم HTTP/3، والمزيد مع فئة [Fetcher](fetching/static.md) الجديدة بالكامل
- **تحسين وضع التخفي**: أصبح وضع التخفي في `DynamicFetcher` وفئات الجلسات الخاصة به أقوى وأكثر موثوقية (المعروف أيضًا باسم `PlayWrightFetcher`)

#### التكامل مع الذكاء الاصطناعي وخادم MCP {#v0.3-ai-integration-mcp-server}
- **خادم MCP مدمج**: خادم Model Context Protocol لاستخراج البيانات من الويب بمساعدة الذكاء الاصطناعي
- **6 أدوات قوية**: `get`, `bulk_get`, `fetch`, `bulk_fetch`, `stealthy_fetch`, `bulk_stealthy_fetch`
- **استخراج ذكي للمحتوى**: تحويل صفحات الويب أو عناصرها إلى Markdown أو HTML، أو استخراج نسخة نظيفة من النص
- **دعم محددات CSS**: استخدام محرك Scrapling لتحديد عناصر معينة بدقة قبل إرسال المحتوى إلى الذكاء الاصطناعي
- **تجاوز أنظمة مكافحة الروبوتات**: التعامل مع Cloudflare Turnstile وغيرها من أنظمة الحماية
- **دعم البروكسي**: استخدام البروكسي لإخفاء الهوية والوصول إلى المواقع من مناطق جغرافية محددة
- **محاكاة المتصفحات**: محاكاة المتصفحات الحقيقية باستخدام بصمات TLS وترويسات متصفح حقيقية تطابق إصداره، والمزيد
- **معالجة متوازية**: استخراج البيانات من عدة روابط في الوقت نفسه لزيادة الكفاءة
- [والمزيد...](ai/mcp-server.md)

#### بيئة تفاعلية جديدة لاستخراج البيانات من الويب {#v0.3-new-interactive-web-scraping-shell}
- **بيئة تفاعلية جديدة**: بيئة IPython مخصصة مع اختصارات ذكية مدمجة كثيرة، مثل `get` و`post` و`put` و`delete` و`fetch` و`stealthy_fetch`
- **إدارة ذكية للصفحات**: أمران جديدان، `page` و`pages`، لحفظ الصفحة الحالية وسجل جميع الطلبات المنفذة عبر البيئة التفاعلية تلقائيًا
- **التكامل مع Curl**: استخدام الدالتين `uncurl` و`curl2fetcher` لتحويل أوامر curl من أدوات المطور في المتصفح إلى طلبات `Fetcher`
- [والمزيد...](cli/interactive-shell.md)

#### استخراج البيانات من الطرفية دون برمجة {#v0.3-scrape-from-the-terminal-without-programming}
- **أوامر جديدة لاستخراج البيانات**: استخراج البيانات من الطرفية دون برمجة
    - `scrapling extract get/post/put/delete` - طلبات HTTP بسيطة
    - `scrapling extract fetch` - استخراج المحتوى الديناميكي
    - `scrapling extract stealthy-fetch` - تجاوز أنظمة مكافحة الروبوتات
- **تنزيل صفحات الويب** وحفظ محتواها في ملفات.
- **تحويل HTML إلى صيغ سهلة القراءة** مثل Markdown، أو الاحتفاظ به كـ HTML، أو استخراج نص الصفحة فقط.
- **دعم محددات CSS مخصصة** لاستخراج أجزاء معينة من الصفحة.
- **التعامل مع طلبات HTTP وجلب الصفحات عبر المتصفحات.**
- **خيارات تخصيص كثيرة** للترويسات وملفات تعريف الارتباط والبروكسي وغيرها. معظم الخيارات المتاحة في الكود متاحة أيضًا من الطرفية.
- [والمزيد...](cli/extract-commands.md)

### 🔧 تحسينات تقنية {#v0.3-technical-improvements}

#### تحسينات الأداء {#v0.3-performance-enhancements}
- **Fetcher أسرع الآن 4 مرات** - نعم، قرأت ذلك بشكل صحيح!
- **DynamicFetcher أسرع الآن بنحو ~60%** - زيادة كبيرة في السرعة حسب إعداداتك (خاصة وضع التخفي)
- **StealthyFetcher أسرع الآن بنسبة 20–30%** - بفضل البنية الجديدة والبدء في استخدام الكود الخاص بنا بدلًا من واجهة Python في `Camoufox`
- **زيادة مجمعة في السرعة بنسبة 50%+** لدوال تحديد العناصر الأساسية (`find_by_text` و`find_similar` و`find_by_regex` و`relocate` وغيرها) 🚀
- **زيادة بنحو ~10% في سرعة دوال اختيار أول نتيجة من CSS/XPath** - أصبحت `css_first` و`xpath_first` أسرع من `css` و`xpath`
- **الدالة `get_all_text()` أسرع بنسبة 40%** عند استخراج المحتوى
- **زيادة في السرعة بنسبة 20%** عند العثور على العناصر مجددًا باستخدام الميزة التكيفية
- **تحسين خصائص التنقل** - أصبحت خصائص مثل `next` و`previous` و`below_elements` وغيرها أسرع بشكل ملحوظ
- **تنظيف النصوص أسرع 5 مرات**
- **تحسين استخدام الذاكرة** عبر تحسين الاستيراد وتقليل العمليات الإضافية
- **⚡ استيراد سريع جدًا**: تقليل وقت بدء التشغيل بتحسين تحميل الوحدات
- **نتائج أفضل في اختبارات الأداء**: جعلت تحسينات السرعة Scrapling أسرع بكثير من قبل مقارنة بالمكتبات الأخرى (أسرع من BeautifulSoup بمقدار 1775 مرة، ومن AutoScraper بمقدار 5.1 مرة، راجع [اختبارات الأداء](benchmarks.md))

#### تحسين البنية وجودة الكود وسهولة الاستخدام {#v0.3-architecture-code-quality-and-quality-of-life}
- **سياق متصفح دائم**: أصبحت كل أدوات جلب الصفحات عبر المتصفح تستخدم سياقًا دائمًا افتراضيًا. (يحل #64 أيضًا)
- **استخدام msgspec للتحقق بسرعة كبيرة من إعدادات كل أدوات جلب الصفحات عبر المتصفح** قبل تنفيذ الطلبات، لتسهيل اكتشاف الأخطاء.
- **كل ملفات تعريف الارتباط** التي تعيدها أدوات الجلب أصبحت بالتنسيق الذي تقبله الأداة نفسها. يمكنك استرجاعها وتمريرها مجددًا إلى كل أدوات الجلب وفئات جلساتها.
- **فحص الكود وتنسيقه أسرع** بعد الانتقال إلى `ruff`
- **نظام بناء حديث**: الانتقال من setup.py إلى pyproject.toml 📦
- **تحسين GitHub Actions وسير العمل** لتسهيل التطوير والاختبار
- **🎨 تحسين تلميحات الأنواع**: تغطية كاملة للأنواع وفق معايير Python الحديثة لتحسين دعم محررات الكود والموثوقية
- **كود أنظف**: إزالة الكود غير المستخدم وتحسين الدوال الأساسية 🧹
- **🚀 التوافق مع الإصدارات السابقة**: إضافة اختصارات للحفاظ على عمل الكود القديم

### تغييرات قد تؤثر في الكود الحالي {#v0.3-breaking-changes}

#### أقل إصدار مدعوم من Python {#v0.3-minimum-python-version}
- **يتطلب Python 3.10+**: إيقاف دعم Python 3.9 والإصدارات الأقدم

#### أسماء الفئات والدوال {#v0.3-class-and-method-naming}
تهدف تغييرات الأسماء إلى جعلها أوضح وأكثر اتساقًا، خاصة للمستخدمين الجدد.

- **`Adaptor` → `Selector`**: تغيير اسم فئة التحليل الأساسية (لا يزال استيرادها باسم `Adaptor` ممكنًا للتوافق مع الكود القديم)
- **`Adaptors` → `Selectors`**: تغيير اسم فئة المجموعة (لا يزال استيرادها باسم `Adaptors` ممكنًا للتوافق مع الكود القديم)
- **`auto_match` → `adaptive`**: تغيير اسم الخيار في جميع الدوال
- **`adaptor_arguments` → `selector_config`**: تغيير اسم خيار الإعدادات
- **`automatch_domain` → `adaptive_domain`**: تغيير اسم خيار النطاق
- **`additional_arguments` → `additional_args`**: اختصار اسم الخيار
- **⚠️ `text/body` → `content`**: أصبح خيار إنشاء Selector يقبل كلًا من `str` و`bytes`
- **`PlayWrightFetcher` → `DynamicFetcher`**: تغيير اسم فئة أتمتة المتصفح (لا يزال استيرادها باسم `PlayWrightFetcher` ممكنًا للتوافق مع الكود القديم)
- **إزالة الكود والخيارات الخاصة بـ NSTBrowser من DynamicFetcher** لعدم الحاجة إليها الآن.
- **لم يعد خيار headless في StealthyFetcher يقبل القيمة 'virtual'** لأن استخدام مكتبة Camoufox أصبح مقتصرًا على معرفة مسار تثبيت المتصفح وبقية خيارات تشغيله

### 🐛 إصلاحات الأخطاء {#v0.3-bug-fixes}

- إصلاح حساب العناصر الفرعية المتداخلة داخل الوسوم التي تتجاهلها `get_all_text` (#61)
- إصلاح مشكلة في التثبيت عند وجود مسافات في مسار ملف تشغيل Python (#57)
- إصلاح مشكلات خيوط التنفيذ في التخزين، مع التعامل مع الدوال التي تستدعي نفسها عند تفعيل الميزة التكيفية
- إصلاح أولوية الخيارات باستخدام نمط Sentinel في `FetcherSession`
- إصلاح التعامل مع أنواع البروكسي في `StealthyFetcher`
- إصلاح التعارض بين الخيارين `referer` و`google_search`
- إصلاح مشكلات حقن سكربتات التخفي في الكود غير المتزامن

## [v0.2.99](https://github.com/D4Vinci/Scrapling/releases/tag/v0.2.99) - 2025-04-08 {#v0.2.99}

**هذا تحديث مهم للجميع للاستفادة الكاملة من Scrapling كما صُممت.**

### ما الذي تغير {#v0.2.99-what-s-changed}
#### موقع جديد للتوثيق الكامل {#v0.2.99-new-full-documentation-website}
- نعم، أخيرًا 😄 يمكنك زيارته من [هنا](index.md)
#### طريقة موحدة لاستيراد أدوات جلب الصفحات {#v0.2.99-unified-import-logic-for-fetchers}
- يمكنك الآن استيراد جميع أدوات جلب الصفحات باستخدام `from scrapling.fetchers import Fetcher, AsyncFetcher, StealthyFetcher, PlayWrightFetcher`، ثم استخدامها مباشرة مثل `page = Fetcher.get(...)` دون إنشاء كائن أولًا.<br/> يحل هذا محل الاستيراد القديم `from scrapling.defaults import Fetcher, AsyncFetcher, StealthyFetcher, PlayWrightFetcher`.
#### تغيير قد يؤثر في الكود الحالي: تعطيل automatch افتراضيًا {#v0.2.99-breaking-change-automatch-is-now-turned-off-by-default}
- توجد الآن طريقة جديدة لتفعيل automatch من أدوات جلب الصفحات أو خيارات التحليل الأخرى. راجع [صفحة التوثيق](fetching/choosing.md#parser-configuration-in-all-fetchers) للتفاصيل.
>  تظل طرق الاستيراد والاستخدام القديمة متاحة مع تحذير، للحفاظ على التوافق مع الكود القديم.
#### خيارات جديدة لأدوات جلب الصفحات {#v0.2.99-new-options-added-to-fetchers}
- أصبح لدى `StealthyFetcher` و`PlayWrightFetcher` خيار جديد عند جلب الصفحات باسم `wait`. يجعل الأداة تنتظر مدة محددة بالمللي ثانية قبل إغلاق الصفحة وإعادة الاستجابة إليك.
- أصبح `StealthyFetcher` يقبل في الدالتين `fetch` و`async_fetch` الخيار `additional_arguments` لتمرير إعدادات إضافية إلى Camoufox، وتكون لها أولوية أعلى من إعدادات Scrapling (#54 )
#### إصلاحات الأخطاء {#v0.2.99-bugs-squashed}
- إصلاح خطأ في التعامل مع عمليات إعادة التوجيه في `async_fetch` داخل الفئتين `StealthyFetcher` و`PlayWrightFetcher`.

**_شكرًا لكم على كل الدعم والتبرعات!_**

## [v0.2.98](https://github.com/D4Vinci/Scrapling/releases/tag/v0.2.98) - 2025-03-17 {#v0.2.98}

**هذا تحديث مهم للجميع للاستفادة الكاملة من Scrapling كما صُممت**

### ما الذي تغير {#v0.2.98-what-s-changed}
#### تحسينات متنوعة لاستخدام الذاكرة والسرعة {#v0.2.98-various-memory-usage-and-speed-optimizations}
- أصبح استخدام الذاكرة في جميع دوال تحديد العناصر نحو ~40% من الاستخدام السابق، مع زيادة بسيطة في السرعة.
- تطبيق التحميل عند الحاجة على كل الوحدات الفرعية للمكتبة، بحيث لا يُحمّل إلا ما تستخدمه، مثلًا:
قبل التحديث، كان الاستيراد `from scrapling import Adaptor` يستخدم `30-40mb` من الذاكرة لأنه يحمّل أيضًا كل أدوات الجلب وغيرها. الآن يستخدم `~1.2mb`.
- جعل التحديث السابق المكتبة تستخدم نحو ~32% من الذاكرة التي كانت تستخدمها مع مجموعة كبيرة من الطلبات. والآن حُسّن التخزين المؤقت أكثر لتستخدم ذاكرة أقل.
- زيادة بسيطة في السرعة العامة لمحلل الصفحات بنسبة 2-5%

**_شكرًا لكم على كل الدعم والتبرعات!_**

## [v0.2.97](https://github.com/D4Vinci/Scrapling/releases/tag/v0.2.97) - 2025-03-15 {#v0.2.97}

**هذا تحديث مهم للجميع للاستفادة الكاملة من Scrapling كما صُممت**

### ما الذي تغير {#v0.2.97-what-s-changed}
#### استخدام أقل للذاكرة وزيادة بسيطة في سرعة جميع أدوات جلب الصفحات {#v0.2.97-lower-memory-usage-and-small-speed-increase-across-all-fetchers}
- مع الحدود الجديدة لحجم التخزين المؤقت في المكتبة، ستلاحظ انخفاضًا كبيرًا في استخدام الذاكرة عند تنفيذ عدد كبير من الطلبات أو العمليات.
- إعادة تنظيم أجزاء كبيرة من أدوات جلب الصفحات لتسهيل صيانتها وزيادة سرعتها قليلًا.

#### إصلاحات الأخطاء {#v0.2.97-bugs-fixed}
- إصلاح خطأ في `TextHandler` كان يحوّل القيمة غير النصية إلى نص فارغ عند استيراده وحده. الآن تُحوّل أي قيمة تُمرر إلى `TextHandler` إلى نص أولًا، ثم إلى `TextHandler`. يُطبق ذلك على كل قيمة، فـ `TextHandler`، كما يدل اسمه، مخصص للتعامل مع النصوص فقط! (#45 )
- إصلاح خطأ كان يجعل معظم دوال AsyncFetcher تتجاهل الخيار `retries`.

#### تغييرات أخرى {#v0.2.97-miscellaneous}
- تحديث تلميحات الأنواع لمعظم الخيارات في جميع أدوات جلب الصفحات لتكون أوضح وأدق.

**_شكرًا لكم على كل الدعم والتبرعات!_**

## [v0.2.96](https://github.com/D4Vinci/Scrapling/releases/tag/v0.2.96) - 2025-03-05 {#v0.2.96}

**هذا تحديث مهم للجميع للاستفادة الكاملة من Scrapling كما صُممت**

### ما الذي تغير {#v0.2.96-what-s-changed}
1. إضافة الخيار `-f` إلى `scrapling install` لفرض إعادة تثبيت متطلبات المتصفح. أنصح بتشغيل `scrapling install -f` الآن للاستفادة من الزيادة الكبيرة في سرعة `StealthyFetcher` مع إصدار Camoufox الجديد :)
2. إصلاح خطأ في `TextHandler` كان يجعل أخذ جزء من النص يعيد `TextHandlers` بدلًا من `TextHandler`، مع تصحيح تلميح النوع (#41 )
3. إصلاح مشكلة كانت تجعل `scrapling install` يفتح بيئة Python التفاعلية في بعض الحالات!

## [v0.2.95](https://github.com/D4Vinci/Scrapling/releases/tag/v0.2.95) - 2025-02-25 {#v0.2.95}

**هذا تحديث مهم للجميع للاستفادة الكاملة من Scrapling كما صُممت**

### ما الذي تغير {#v0.2.95-what-s-changed}
1. إصلاح خطأ في `Fetcher` كان يجعل الترويسات الناتجة عن الخيار `stealthy_headers` تستبدل بعض الترويسات التي قدمها المستخدم، مثل `Accept` (#39 )
2. تحسين طريقة إنشاء الترويسات قليلًا، مما يُفترض أن يزيد السرعة بشكل بسيط.

## [v0.2.94](https://github.com/D4Vinci/Scrapling/releases/tag/v0.2.94) - 2025-02-22 {#v0.2.94}

**هذا تحديث مهم للجميع للاستفادة الكاملة من Scrapling كما صُممت**

### ما الذي تغير {#v0.2.94-what-s-changed}
1. إضافة الخاصية `history` إلى جميع أدوات جلب الصفحات لعرض عمليات إعادة التوجيه (#32 )
2. إصلاح طريقة عمل الخيار `case_sensitive` في جميع دوال `re`/`re_first`. قد يعيد الكود نتائج مختلفة إذا كنت تستخدمه (لكن ربما تستحق ذلك لأنك لاحظت أنه لا يعمل كما ينبغي ولم تبلغ عن المشكلة، ههه)
3. تحديث المكتبات المطلوبة وإعادة تفعيل `coop` في محرك Camoufox (StealthyFetcher).

## [v0.2.93](https://github.com/D4Vinci/Scrapling/releases/tag/v0.2.93) - 2025-01-31 {#v0.2.93}

**هذا تحديث مهم للجميع للاستفادة الكاملة من Scrapling كما صُممت**

### ما الذي تغير {#v0.2.93-what-s-changed}
1. أصبح نوع النتيجة متسقًا في محرك التحليل كله. ستكون النتيجة دائمًا من نوع `Adaptor` أو `Adaptors` أو `TextHandler` أو `TextHandlers` أو `None`، أو قائمة عند وجود نتائج مختلطة، مثل محدد CSS مركب. هذا يسهّل كتابة الكود ويقلل الحاجة إلى فحص الأنواع يدويًا، ويجعل المكتبة أكثر استقرارًا ويسمح دائمًا بتسلسل استدعاءات الدوال.
2. إعادة تنظيم معظم محرك التحليل، خاصة فئة `Adaptor`، لجعل الكود أنظف وأسرع. زادت سرعة معظم الدوال والخصائص، خاصة دوال البحث، بنسبة 5-40%. بعض الدوال حصلت على زيادة أكبر، مثل `find_by_regex` التي زادت سرعتها بنحو ~60%! وزادت سرعة ميزة automatch بنحو ~5%.
3. إصلاح أخطاء في الدالتين `find_all`/`find` كانت تجعل شروط التصفية تعمل بمنطق OR أحيانًا وAND أحيانًا أخرى. الآن يجب أن تحقق كل العناصر الناتجة جميع الشروط التي تمررها.
4. أصبحت كل الدوال المرتبطة بالتعبيرات النمطية تعيد `TextHandler`/`TextHandlers` لتسهيل تسلسل استدعاءات الدوال.
5. **إضافة خاصية جديدة** باسم `below_elements` تعيد كائن `Adaptors` يضم جميع العناصر الموجودة أسفل العنصر الحالي في شجرة DOM.
6. أصبحت كل الدوال والخصائص التي كانت تعيد كود HTML كنص تعيده الآن كـ `TextHandler`، لتسهيل استخدام التعبيرات النمطية عليه وغيرها من العمليات...
7. أصبح StealthyFetcher أسرع قليلًا وأفضل في التخفي. ويمكن الآن النقر على اختبارات Captcha داخل iframes، مثل **Cloudflare Turnstile**.
8. تحسين الإكمال التلقائي وتلميحات الأنواع كثيرًا في نحو نصف المكتبة، خاصة `Adaptor` و`TextHandler` و`TextHandlers`.
9. أصبح أخذ جزء من `TextHandler`، أو الوصول إلى حرف برقم موضعه، أو استخدام الدالة `split`، يعيد `TextHandler` آخر بدلًا من نص Python العادي. معظم عمليات ودوال النصوص القياسية تعيد الآن `Texthandler` بدلًا من النص العادي، للسماح دائمًا بتسلسل استدعاءات الدوال.
10. إصلاح بعض الأخطاء الصغيرة وأخطاء الكتابة. مثلًا، كانت async_put في Fetcher تنفذ طلب post بدلًا من put 😶‍🌫️
11. تحسين README قليلًا إلى أن أنتهي من موقع التوثيق.

كان من المفترض أن يكون هذا تحديثًا صغيرًا قبل الإصدار 0.3، لكنني قررت تحسينه أكثر.

## [v0.2.92](https://github.com/D4Vinci/Scrapling/releases/tag/v0.2.92) - 2024-12-26 {#v0.2.92}

### ما الذي تغير {#v0.2.92-what-s-changed}
- أصبحت الاستجابة التي تعيدها أدوات جلب الصفحات عبر المتصفح تعتمد على مصادر بيانات أكثر موثوقية عندما تحتوي الصفحة على كثير من Iframes.
- **أصبح تثبيت `Scrapling` أسهل: ثبّتها باستخدام pip، ثم شغّل `scrapling install` في الطرفية، وستكون جاهزًا!**
- تصحيح تلميح نوع غير دقيق في محلل الصفحات.

## [v0.2.91](https://github.com/D4Vinci/Scrapling/releases/tag/v0.2.91) - 2024-12-19 {#v0.2.91}

### ما الذي تغير {#v0.2.91-what-s-changed}
- إصلاح خطأ كان يجعل رسالة سجل جلب الصفحة تظهر مع الطلب الأول فقط.
- السلوك الافتراضي لـ Playwright API عند تصفح صفحة هو إعادة أول استجابة تحقق حالة التحميل المحددة للدالة `goto`: `["load", "domcontentloaded", "networkidle"]`. لذلك، إذا كان الموقع يعرض صفحة انتظار مثل صفحة Cloudflare ثم يعيد توجيهك إلى الموقع الحقيقي، يعيد Playwright رمز الحالة الأول، وقد يكون مثلًا 403. يحل هذا التحديث المشكلة في `PlaywrightFetcher` و`StealthyFetcher`، إذ يستخدم كلاهما Playwright API، ولم تعد النتيجة تعتمد على سلوكه الافتراضي.
- إضافة دعم بروكسي SOCKS في فئة `Fetcher`.
- تصحيح تلميح النوع للخيار `wait_selector_state`، ليعرض الإكمال التلقائي القيم الصحيحة التي يمكنك استخدامها.

## [v0.2.9](https://github.com/D4Vinci/Scrapling/releases/tag/v0.2.9) - 2024-12-16 {#v0.2.9}

### ما الذي تغير {#v0.2.9-what-s-changed}
##### ميزات جديدة {#v0.2.9-new-features}
1. إضافة دعم الكود غير المتزامن إلى Scrapling، وهو **ما انتظرناه طويلًا**! أصبحت فئة `AsyncFetcher` النسخة غير المتزامنة من `Fetcher`، وحصلت الفئتان `StealthyFetcher` و`PlayWrightFetcher` على دالة جديدة باسم `async_fetch` بالخيارات نفسها.

```python
>> from scrapling import StealthyFetcher
>> page = await StealthyFetcher().async_fetch('https://www.browserscan.net/bot-detection')  # the async version of fetch
>> page.status == 200
True
```

2. أصبح لدى فئة `StealthyFetcher` خيار `geoip` في دوال الجلب. عند تفعيله، تستخدم تلقائيًا خط الطول وخط العرض والمنطقة الزمنية والبلد والإعدادات المحلية المرتبطة بعنوان IP، ثم تغيّر عنوان IP الذي يظهر عبر WebRTC. وتحدد أيضًا لغة المتصفح وتحاكيها حسب توزيع متحدثي اللغات في المنطقة المستهدفة.
3. إضافة الخيار `retries` إلى الفئتين `Fetcher`/`AsyncFetcher`، لتحديد عدد مرات إعادة محاولة كل طلب ينفذه `httpx`.
4. إضافة الدالة `url_join` إلى `Adaptor` وأدوات جلب الصفحات. تأخذ رابطًا نسبيًا وتجمعه مع الرابط الحالي لإنشاء رابط كامل!
5. إضافة الدالة `keep_cdata` إلى `Adaptor` وأدوات جلب الصفحات لمنع محلل الصفحات من إزالة cdata عند الحاجة.
6. أصبحت `Adaptor`/`Response` تعيد عبر الدالة `body` استجابة HTML الخام إن أمكن (دون معالجتها داخل المكتبة).
7. إضافة تسجيل الأحداث لفئة `Response`. عند استخدام أدوات جلب الصفحات، ستحصل الآن على سجل يعرض معلومات عن الاستجابة.
مثال:

   ```python
   >> from scrapling.defaults import Fetcher
   >> Fetcher.get('https://books.toscrape.com/index.html')
   [2024-12-16 13:33:36] INFO: Fetched (200) <GET https://books.toscrape.com/index.html> (referer: https://www.google.com/search?q=toscrape)
   >>
   ```

8. أصبح استخدام دوال النصوص القياسية على `TextHandler`، مثل `.replace()`، يعيد `TextHandler` آخر. كان يعيد نصًا عاديًا من قبل.
9. تحسينات كبيرة في السرعة في المكتبة كلها، وتحسين التخفي في أدوات جلب الصفحات بشكل عام.
10. إضافة دوال توافق مثل `extract_first`\`extract` تعيد النتيجة نفسها التي يعيدها الكائن الأصلي. أُضيفت فقط لتسهيل نقل الكود من Scrapy/Parsel إلى Scrapling عند الحاجة، لأن هذه الدوال مستخدمة هناك!
11. أصبحت الطلبات الجماعية أسرع بكثير بفضل إعادة تنظيم أجزاء كثيرة من الكود واستخدام التخزين المؤقت في الأماكن المناسبة.

##### تغييرات قد تؤثر في الكود الحالي {#v0.2.9-breaking-changes}
- إيقاف دعم Python 3.8. (السبب الرئيسي هو توقف Playwright عن دعمه، لكنه كان إصدارًا كثير المشكلات على أي حال)
- إزالة الخيار `debug` من المكتبة كلها. لتفعيل وضع تصحيح الأخطاء، نفّذ ما يلي بعد استيراد المكتبة:

   ```python
   >>> import logging
   >>> logging.getLogger("scrapling").setLevel(logging.DEBUG)
   ```

##### إصلاحات الأخطاء {#v0.2.9-bugs-squashed}
1. تفعيل WebGL افتراضيًا لأن كثيرًا من أنظمة الحماية تتحقق الآن من تفعيله.
2. إصلاح بعض الأخطاء وأخطاء الكتابة في التوثيق وREADME.

##### تحسينات الاستخدام {#v0.2.9-quality-of-life-changes}
1. توحيد كل السجلات تحت اسم `scrapling` لتسهيل التحكم بها. كنا نستخدم root logger من قبل.
2. إعادة تنظيم مجلد الاختبارات وإضافة اختبارات للميزات الجديدة. أُعيدت كتابة كل الاختبارات بشكل أوضح، وأُضيف المزيد منها لتغطية أجزاء أكثر من الكود.
3. إعادة تنظيم جزء كبير من الكود ليكون أنظف وأسهل في الصيانة.

> كانت كل هذه التغييرات ضمن ما خططت لإضافته في 0.3، لكنني قررت إضافتها هنا لأن الإصدار التالي سيحتاج إلى بعض الوقت. الخطوة التالية هي إكمال موقع التوثيق المفصل، ثم العمل على الإصدار 0.3

## [v0.2.8](https://github.com/D4Vinci/Scrapling/releases/tag/v0.2.8) - 2024-11-30 {#v0.2.8}

### ما الذي تغير {#v0.2.8-what-s-changed}
- تحديث صغير يتضمن تحسينات ضرورية لتسهيل استخدام الكود، وتصحيح خطأ كتابة في ملف README الرئيسي (#20)

## [v0.2.7](https://github.com/D4Vinci/Scrapling/releases/tag/v0.2.7) - 2024-11-26 {#v0.2.7}

### ما الذي تغير {#v0.2.7-what-s-changed}
##### ميزات جديدة {#v0.2.7-new-features}
- عند استخدام الخيار `wait_selector` مع `StealthyFetcher` و`PlayWrightFetcher`، تنتظر Scrapling مجددًا اكتمال تحميل JS وتنفيذه كالمعتاد. وإذا استخدمت الخيار `network_idle`، فستنتظر تحققه مجددًا بعد ذلك أيضًا. وبالطبع، لا يحدث انتظار إذا كانت جميع الحالات قد تحققت بالفعل.
- يمكنك الآن تفعيل الإعلانات أو تعطيلها في `StealthyFetcher` باستخدام الخيار `disable_ads`. حظر الإعلانات مفعّل افتراضيًا، ويثبّت إضافة `ublock origin`.
- يمكنك الآن تحديد الإعدادات المحلية التي يستخدمها `PlayWrightFetcher` عبر الخيار `locale`. تظل القيمة الافتراضية `en-US`.
- أصبحت الطلبات الأساسية عبر `Fetcher` تقبل البروكسي بالتنسيق `http://username:password@localhost:8030`.
- تحسين وضع التخفي قليلًا في `PlayWrightFetcher`.

##### إصلاحات الأخطاء والتحسينات {#v0.2.7-bugs-squashed-improvements}
1. لم يعد تفعيل البروكسي في فئة `PlayWrightFetcher` مرتبطًا بتفعيل وضع `stealth` أو تعطيله (شكرًا لـ [@AbdullahY36](https://github.com/AbdullahY36) على التنبيه)
2. أصبحت `ResponseEncoding` تتحقق من إمكانية استخدام الترميز الوارد في الاستجابة مع الصفحة. إذا سبب هذا الترميز خطأ، تستخدم Scrapling الترميز الافتراضي `utf-8`

## [v0.2.6](https://github.com/D4Vinci/Scrapling/releases/tag/v0.2.6) - 2024-11-24 {#v0.2.6}

### ما الذي تغير {#v0.2.6-what-s-changed}
##### ميزات جديدة {#v0.2.6-new-features}
- يمكن الآن لـ `PlayWrightFetcher` استخدام المتصفح الحقيقي مباشرة عبر تمرير الخيار `real_chrome` إلى الدالة `PlayWrightFetcher.fetch`، بشرط تثبيت متصفح Chrome. تشغّل Scrapling نسخة من Chrome لديك، ويمكنك استخدام معظم الخيارات كالمعتاد. (كان الخيار `cdp_url` هو الطريقة الوحيدة لذلك من قبل)
- تحديث الإصدار الذي تعكسه الترويسات المولّدة للمتصفحات الحقيقية.

##### إصلاحات الأخطاء {#v0.2.6-bugs-squashed}
1. اتضح أن تنسيق ترويسات المتصفح التي يولدها `BrowserForge` كان قديمًا، مما جعل بعض أنظمة الحماية تكتشف Scrapling. لذلك أصبح `BrowserForge` يُستخدم فقط لتوليد useragent حقيقي.
2. تعطيل الخيار `hide_canvas` افتراضيًا لأن ReCaptcha من Google تكتشفه.

## [v0.2.5](https://github.com/D4Vinci/Scrapling/releases/tag/v0.2.5) - 2024-11-23 {#v0.2.5}

### ما الذي تغير {#v0.2.5-what-s-changed}

##### إصلاحات الأخطاء {#v0.2.5-bugs-squashed}
- معالجة خطأ يحدث مع الخيار 'wait_selector' عندما يطابق أكثر من 1 عنصر. يؤثر ذلك في الفئتين `StealthyFetcher` و`PlayWrightFetcher`.
- تصحيح نوع الترميز عندما تحتوي قيمة ترويسة `content_type` على خيارات مثل `charset` (شكرًا لـ @andyfcx على [#12](https://github.com/D4Vinci/Scrapling/issues/12) )

##### تحسينات الاستخدام {#v0.2.5-quality-of-life}
- إضافة اختبارات لتغطية أجزاء جديدة من الكود، وتشغيل الاختبارات في خيوط تنفيذ.
- تحديث نصوص التوثيق داخل الكود لتظهر بشكل صحيح في أداة apidoc من Sphinx والأدوات المشابهة.

##### مساهمون جدد {#v0.2.5-new-contributors}
- قدّم @andyfcx مساهمته الأولى في [#13 ](https://github.com/D4Vinci/Scrapling/pull/13)

## [v0.2.4](https://github.com/D4Vinci/Scrapling/releases/tag/v0.2.4) - 2024-11-20 {#v0.2.4}

### ما الذي تغير {#v0.2.4-what-s-changed}

##### إصلاحات الأخطاء {#v0.2.4-bugs-squashed}
- إصلاح خطأ عند استرجاع بايتات الاستجابة بعد استخدام الخيار `network_idle` في الفئتين `StealthyFetcher` و`PlayWrightFetcher`. <br/> كان يسبب رسالة الخطأ التالية:

    ```
    Response.body: Protocol error (Network.getResponseBody): No resource with given identifier found
    ```

- تعيد PlayWright API أحيانًا نص حالة فارغًا مع الاستجابة، لذا تحسبه `Scrapling` الآن بنفسها عند حدوث ذلك. يؤثر هذا في الفئتين `StealthyFetcher` و`PlayWrightFetcher`.

## [v0.2.3](https://github.com/D4Vinci/Scrapling/releases/tag/v0.2.3) - 2024-11-19 {#v0.2.3}

### ما الذي تغير {#v0.2.3-what-s-changed}

##### إصلاحات الأخطاء {#v0.2.3-bugs-squashed}
- إصلاح خطأ في التثبيت باستخدام pip كان يمنع وضع التخفي في PlayWright Fetcher من العمل تمامًا.

## [v0.2.2](https://github.com/D4Vinci/Scrapling/releases/tag/v0.2.2) - 2024-11-16 {#v0.2.2}

### ما الذي تغير {#v0.2.2-what-s-changed}
##### ميزات جديدة {#v0.2.2-new-features}
- إذا أردت استخدام القيم الافتراضية دون تمرير خيارات إلى كائن `Adaptor` الناتج، يمكنك استخدام الاستيراد التالي ليكون الكود أبسط

    ```python
    >> from scrapling.default import Fetcher, StealthyFetcher, PlayWrightFetcher
    >> page = Fetcher.get('https://example.com', stealthy_headers=True)
    ```

    وإلا

    ```python
    >> from scrapling import Fetcher, StealthyFetcher, PlayWrightFetcher
    >> page = Fetcher(auto_match=False).get('https://example.com', stealthy_headers=True)
    ```

##### إصلاحات الأخطاء {#v0.2.2-bugs-squashed}
1. إصلاح خطأ في كائن `Response` ظهر مع تحديث v0.2.1 بالأمس، وكان يحدث في بعض حالات التحديد أو التحليل المتداخل.

## [v0.2.1](https://github.com/D4Vinci/Scrapling/releases/tag/v0.2.1) - 2024-11-15 {#v0.2.1}

### ما الذي تغير {#v0.2.1-what-s-changed}
##### ميزات جديدة {#v0.2.1-new-features}
1. أصبح كائن `Response` الذي تعيده جميع أدوات جلب الصفحات مماثلًا لكائن `Adaptor`، مع إضافة الخصائص التالية: `status` و`reason` و`cookies` و`headers` و`request_headers`. تكون `cookies` و`headers` و`request_headers` دائمًا من نوع `dictionary`. <br/>يمكن أن يصبح الكود الآن بهذا الشكل:

    ```python
    >> from scrapling import Fetcher
    >> page = Fetcher().get('https://example.com', stealthy_headers=True)
    >> print(page.status)
    200
    >> products = page.css('.product')
    ```

    بدلًا من الشكل السابق

    ```python
    >> from scrapling import Fetcher
    >> fetcher = Fetcher().get('https://example.com', stealthy_headers=True)
    >> print(fetcher.status)
    200
    >> page = fetcher.adaptor
    >> products = page.css('.product')
    ```

    لكنني أبقيت الخاصية `.adaptor` تعمل للتوافق مع الكود القديم.

2. أصبحت الفئتان `StealthyFetcher` و`PlayWrightFetcher` تقبلان الخيار `proxy` في دالة الجلب، ويقبل نصًا أو قاموسًا.
3. أصبح لدى فئة `StealthyFetcher` الخيار `os_randomize` في الدالة `fetch`. عند تفعيله، تختار Scrapling بصمات نظام التشغيل عشوائيًا. أما افتراضيًا، فتطابق البصمات نظام التشغيل الحالي.

##### إصلاحات الأخطاء {#v0.2.1-bugs-squashed}
1. إصلاح خطأ يحدث عند تمرير الترويسات مع فئة `Fetcher`.
2. إصلاح خطأ في تحليل استجابات JSON التي تأتي من أدوات جلب الصفحات.

##### تحسينات الاستخدام {#v0.2.1-quality-of-life-changes}
1. كانت دوال النصوص تحاول إزالة تعليقات HTML قبل إعادة النص، لكن ذلك سبب أخطاء في بعض الحالات وجعل الكود أعقد من اللازم. عادت الآن إلى السلوك الافتراضي لـ lxml، **وستلاحظ زيادة بسيطة في سرعة كل العمليات التي تعتمد على نص العناصر، مثل المحددات**. إذا أردت أن تزيل Scrapling تعليقات HTML من العناصر قبل إعادة النص، لتجنب سلوك تقسيم النص الغريب في lxml/parsel/scrapy، أبقِ الخيار `keep_comments` مضبوطًا على True كما هو افتراضيًا.

## [v0.2](https://github.com/D4Vinci/Scrapling/releases/tag/v0.2) - 2024-11-11 {#v0.2}

### ما الذي تغير {#v0.2-what-s-changed}
##### ميزات جديدة {#v0.2-new-features}
1. إضافة ميزة `Fetchers` مع 3 أنواع رئيسية جديدة، لتجلب Scrapling الصفحات لك بخيارات كثيرة جدًا!
    - فئة `Fetcher` لطلبات HTTP الأساسية
    - فئة `StealthyFetcher` لجلب الصفحات بتخفٍ كامل باستخدام [نسخة معدّلة من Firefox للتخفي](https://github.com/daijro/camoufox).
    - فئة `PlayWrightFetcher` لطلبات المتصفح عبر PlayWright العادي، أو PlayWright مع وضع التخفي الذي طورته، أو متصفحات حقيقية عبر CDP، أو [NSTBrowser](https://app.nstbrowser.io/r/1vO5e5) عبر [docker browserless](https://hub.docker.com/r/nstbrowser/browserless)!
2. إضافة الدالتين الجديدتين بالكامل `find_all`/`find` للعثور على عناصر الصفحة بسهولة وبشيء من السحر!
3. إضافة الدالتين `filter` و`search` إلى فئة `Adaptors` لتسهيل العمليات الجماعية على مجموعات كائنات `Adaptor`.
4. إضافة الدالتين `css_first` و`xpath_first` لتسهيل الاستخدام.
5. إضافة الفئة الجديدة `TextHandlers` لتنفيذ عمليات جماعية على كائنات `TextHandler`، مثل فئة `Adaptors`.
6. إضافة الدالتين `generate_full_css_selector` و`generate_full_xpath_selector`.

##### إصلاحات الأخطاء {#v0.2-bugs-squashed}
1. أصبحت فئة `Adaptors` تعيد عبر `re_first` أول نتيجة مطابقة من جميع كائنات `Adaptor` الموجودة فيها، بدلًا من السلوك الخاطئ الذي كان يعيد نتائج `re_first` لكل كائنات `Adaptor`.
2. عند اختيار محتوى نصي من العناصر (مثل دالة CSS المسماة `::text`) بأي دالة مثل `.css` أو `.xpath`، يعيد كائن `Adaptor` الآن فئة `TextHandlers` بدلًا من قائمة نصوص كما كان من قبل. يمكنك الآن كتابة `page.css('something::text').re_first(r'regex_pattern').json()` بدلًا من `page.css('something::text')[0].re_first(r'regex_pattern').json()`
3. أصبحت خيارات re/re_first في `Adaptor`/`Adaptors` متسقة مع خيارات `TextHandler`. أصبح الخياران `clean_match` و`case_sensitive` متاحين.
4. تفعيل الخيار `auto_match` افتراضيًا عند إنشاء `Adaptor`، لكن لا يزال عليك تفعيله عند تحديد العناصر إذا أردت استخدامه. (هذا قرار تصميم، وليس خطأ)
5. تصحيح كثير من تلميحات الأنواع لتحسين الإكمال التلقائي أثناء كتابة الكود باستخدام Scrapling.

##### تحسينات الاستخدام {#v0.2-quality-of-life-changes}
1. تغيير اسمي الدالتين `css_selector` و`xpath_selector` إلى `generate_css_selector` و`generate_xpath_selector` لزيادة الوضوح ومنع التداخل مع الإكمال التلقائي أثناء كتابة الكود.
2. نقل معظم الكود القديم إلى حزمة فرعية باسم `core`، مع قرارات تصميم أخرى لجعل الصيانة مستقبلًا أسهل وأوضح.
3. إعادة تنظيم مجلد الاختبارات وإضافة اختبارات للميزات الجديدة. وأصبحت بيئات tox تُحفظ مؤقتًا على GitHub لتسريع الاختبارات الآلية مع كل commit.

## [v0.1.2](https://github.com/D4Vinci/Scrapling/releases/tag/v0.1.2) - 2024-10-16 {#v0.1.2}

**سجل التغييرات**:

- إصلاح خطأ كان يجعل الخيار `keep_comments` لا يعمل كما ينبغي.
- تعديل دالة النصوص لإزالة تعليقات HTML من العناصر تلقائيًا قبل استخراج نصها، لتجنب اختلاف سلوك Lxml، مثلًا:

    ```python
    >>> page = Adaptor('<span>CONDITION: <!-- -->Excellent</span>', keep_comments=True)
    >>> page.css('span::text')
    ['CONDITION: ', 'Excellent']
    ```

    كان هذا هو الناتج سابقًا بسبب السلوك الافتراضي لـ Lxml، لكن الناتج الآن هو النص الكامل 'CONDITION: Excellent'
    هذا السلوك معروف أيضًا في parsel\scrapy، لذا أردت معالجته هنا.

- إصلاح خطأ كان يمنع حذف ملف قاعدة بيانات SQLite الذي تنشئه المكتبة عند تشغيل `pip uninstall scrapling` أو أمر مشابه.

## [v0.1.1](https://github.com/D4Vinci/Scrapling/releases/tag/v0.1.1) - 2024-10-14 {#v0.1.1}

إصلاحات بسيطة

## [v0.1](https://github.com/D4Vinci/Scrapling/releases/tag/v0.1) - 2024-10-13 {#v0.1}

**سجل التغييرات الكامل**: <https://github.com/D4Vinci/Scrapling/commits/v0.1>
