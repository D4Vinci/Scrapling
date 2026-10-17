---
title: "اختر طلبات HTTP أو المتصفح لجمع بيانات الويب"
description: "اختر Fetcher أو StealthyFetcher حسب مهمتك. تعرّف على وقت استخدام HTTP المباشر وتشغيل JavaScript والجلسات القابلة لإعادة الاستخدام."
---

# أساسيات أدوات الجلب {#fetchers-basics}

## مقدمة {#introduction}
أدوات الجلب Fetchers هي فئات ترسل الطلبات أو تجلب الصفحات بسطر واحد، مع ميزات كثيرة، ثم تعيد كائن [Response](#response-object). منذ الإصدار v0.3، لكل أداة جلب فئة جلسة مستقلة تُبقي الجلسة مفتوحة. مثلًا، تبقي أداة جلب المتصفح المتصفح مفتوحًا حتى تنتهي من كل طلباتك، بدلًا من فتح عدة متصفحات. اختر حسب حاجتك.

أُضيفت هذه الميزة لأن Scrapling كان قبل الإصدار v0.2 محلّل صفحات فقط. الهدف هو أن يغطي تدريجيًا كل احتياجات جمع بيانات الويب.

> أدوات الجلب ليست مجرد أغلفة لمكتبات أخرى. هي تستخدم هذه المكتبات كمحركات لإرسال الطلبات وجلب الصفحات، وتضيف ميزات لا توفرها المحركات نفسها، مع الاستفادة من قدراتها وتحسينها لجمع بيانات الويب.

## نظرة على أدوات الجلب {#fetchers-overview}

يوفر Scrapling أداتي HTTP، وهما `Fetcher` و`AsyncFetcher`، وأداة متصفح هي `StealthyFetcher`، مع فئات جلسات للطلبات المتكررة.

يساعدك الجدول التالي على المقارنة والاختيار بسرعة.


| الميزة | Fetcher | StealthyFetcher |
|--------------------|---------------------------------------------------|--------------------------------------------------------------------------------------------|
| السرعة النسبية | 🐇🐇🐇🐇🐇 | 🐇🐇🐇 |
| التخفي | ⭐⭐ | ⭐⭐⭐⭐⭐ |
| خيارات تجاوز كشف البوتات | ⭐⭐ | ⭐⭐⭐⭐⭐ |
| تشغيل JavaScript | ❌ | ✅ |
| استهلاك الذاكرة | ⭐ | ⭐⭐⭐ |
| الاستخدام الأنسب | جمع البيانات البسيط عندما تكفي طلبات HTTP | مواقع تُحمّل ديناميكيًا <br/> أتمتة محدودة <br/> حمايات بسيطة أو معقدة |
| المتصفحات | ❌ | Chromium وGoogle Chrome |
| واجهة المتصفح المستخدمة | ❌ | Playwright |
| صعوبة الإعداد | بسيط | بسيط |

سنشرح كل أداة بالتفصيل في الصفحات التالية.

## إعداد محلّل الصفحات في كل أدوات الجلب {#parser-configuration-in-all-fetchers}
تُستورد كل أدوات الجلب بالطريقة نفسها، كما سترى في الصفحات التالية:
```python
from scrapling.fetchers import Fetcher, AsyncFetcher, StealthyFetcher
```
ثم استخدمها مباشرة دون إنشاء كائن. ستستخدم إعدادات المحلّل الافتراضية:
```python
page = StealthyFetcher.fetch('https://example.com') 
```
إذا أردت إعداد المحلّل، أي [فئة Selector](../parsing/main_classes.md#selector)، الذي سيُستخدم على الرد قبل إعادته، نفّذ هذا أولًا:
```python
from scrapling.fetchers import Fetcher
Fetcher.configure(adaptive=True, keep_comments=False)  # and the rest
```
أو:
```python
from scrapling.fetchers import Fetcher
Fetcher.adaptive=True
Fetcher.keep_comments=False
```
ثم أكمل الكود كالمعتاد.

خيارات الإعداد المتاحة هي `adaptive` و`adaptive_domain` و`huge_tree` و`keep_comments` و`storage` و`storage_args`. وهي الخيارات نفسها التي تمرّرها إلى [Selector](../parsing/main_classes.md#selector). اعرض الإعدادات الحالية في أي وقت باستخدام `<fetcher_class>.display_config()`.

!!! info "معلومة"

    خيار `adaptive` معطّل افتراضيًا. يجب تفعيله لاستخدام هذه الميزة.

### إعداد المحلّل لكل طلب {#set-parser-config-per-request}
تُطبّق الإعدادات السابقة على كل الطلبات التي ترسلها الفئة نفسها، وذلك لتبسيط الاستخدام.

إذا احتجت إلى إعدادات مختلفة لكل طلب، مرّر قاموسًا إلى الخيار `selector_config` في دالة الطلب، مثل `fetch` أو `get` أو `post` وغيرها.

## كائن Response {#response-object}
كائن `Response` يشبه فئة [Selector](../parsing/main_classes.md#selector)، مع تفاصيل إضافية عن الرد مثل الترويسات ورمز الحالة وملفات تعريف الارتباط، كما يلي:
```python
from scrapling.fetchers import Fetcher
page = Fetcher.get('https://example.com')

page.status          # HTTP status code
page.reason          # Status message
page.cookies         # Response cookies as a dictionary
page.headers         # Response headers
page.request_headers # Request headers
page.history         # Response history of redirections, if any
page.body            # Raw response body as bytes
page.encoding        # Response encoding
page.meta            # Response metadata dictionary (e.g., proxy used). Mainly helpful with the spiders system.
```
تعيد كل أدوات الجلب كائن `Response`. وتعيد جلسات المتصفح التي تفعّل `record_requests=True` كائنات `Response` محفوظة أيضًا عبر `session.network.search(limit=None)` و`session.network.get(request_id)`. راجع [سجل الشبكة](stealthy.md#network-history) لمعرفة كيفية قراءة ردود API المحفوظة والانتقال إلى v5.

يمكن لكائن `Response` تحويل الصفحة إلى Markdown نظيف وجاهز لنماذج اللغة بسطر واحد:
```python
markdown = Fetcher.get('https://example.com').markdown(main_content_only=True)
```
تُزال دائمًا السكربتات والأنماط والمحتوى المخفي ومحتوى حقن التعليمات قبل التحويل. ويمكنك تمرير `css_selector` لتحويل عناصر محددة فقط. تتطلب هذه الميزة إضافة `rag`، وهي موجودة أيضًا ضمن `ai` و`shell` و`all`. تشرحها صفحة [بناء أنظمة RAG](../ai/building-rag-systems.md) بالتفصيل.

!!! note "ملاحظة"

    منذ الإصدار v0.4، يكون محتوى `body` في فئة `Response` دائمًا من نوع bytes، بخلاف فئة [Selector](../parsing/main_classes.md#selector).
