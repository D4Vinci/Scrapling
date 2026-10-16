---
title: "حوّل المواقع إلى Markdown لأنظمة RAG باستخدام Scrapling"
description: "حوّل استجابات الصفحات إلى Markdown أو استخدم ContentSpider لجمع موقع كامل. جهّز النصوص للتقسيم والفهرسة في نظام RAG."
---

# بناء أنظمة RAG باستخدام Scrapling {#building-rag-systems-with-scrapling}

جودة أنظمة RAG تعتمد على جودة النصوص التي تدخل إليها. يستهلك HTML الخام الرموز في الوسوم وقوائم التنقل والسكربتات وعناصر التتبع غير المفيدة. وقد يحمل أيضًا محتوى مخفيًا لحقن التعليمات في النموذج اللغوي. تحوّل Scrapling الصفحات والمواقع الكاملة إلى Markdown نظيف، وتزيل المحتوى المخفي دون استخدام نموذج لغوي. بذلك تكون عملية جمع النصوص سريعة، ولا تدفع تكلفة نموذج لكل صفحة.

## التثبيت {#installation}

```bash
pip install "scrapling[rag]"

scrapling install
```

تثبّت مجموعة `rag` أدوات الجلب مع دعم التحويل إلى Markdown. وتشمل مجموعات `ai` و`shell` و`all` هذا الدعم أيضًا. ينزّل أمر `scrapling install` متطلبات المتصفح، وهي مطلوبة فقط لأدوات الجلب التي تستخدم المتصفح.

## تحويل صفحة واحدة إلى Markdown {#one-page-to-markdown}

يحتوي كل كائن [Response](../fetching/choosing.md#response-object) على الدالة `markdown()`:

```python
from scrapling.fetchers import Fetcher

markdown = Fetcher.get("https://example.com").markdown(main_content_only=True)
```

تعمل مع جميع أدوات الجلب، لذا يمكنك تحويل الصفحات المحمية بـ Cloudflare بسطر واحد أيضًا:

```python
from scrapling.fetchers import StealthyFetcher

markdown = StealthyFetcher.fetch("https://protected.example.com", solve_cloudflare=True).markdown(main_content_only=True)
```

يتحكم معاملان في الناتج:

- `main_content_only`: يحوّل المحتوى الموجود داخل وسم `<body>` فقط.
- `css_selector`: يحوّل العناصر المطابقة لمحدد CSS فقط، ويجمع جميع النتائج المطابقة معًا. استخدمه لاستخراج الجزء الذي تحتاج إليه بالضبط وتقليل استهلاك الرموز:

```python
markdown = Fetcher.get("https://example.com/docs/page").markdown(css_selector="article")
```

بغض النظر عن المعاملات التي تمرّرها، تُزال السكربتات والأنماط والمحتوى المخفي دائمًا قبل التحويل. هذا هو التنظيف نفسه الذي يستخدمه [خادم MCP](mcp-server.md) لحماية وكلاء الذكاء الاصطناعي من حقن التعليمات: يزيل العناصر المخفية بأنماط مباشرة، وعناصر `aria-hidden="true"`، وعناصر slot المخفية، ووسوم `<template>`، وتعليقات HTML، والمحارف عديمة العرض. يستخدم خادم MCP هذا التنظيف مع `main_content_only=True`.

## تحويل موقع كامل إلى مجموعة ملفات Markdown {#a-whole-website-to-a-markdown-corpus}

يزحف قالب `ContentSpider` إلى الموقع ويحوّل كل صفحة باستخدام [إطار العناكب](../spiders/architecture.md). بذلك تحصل على التزامن، وضبط السرعة تلقائيًا، واحترام robots.txt، والإيقاف والاستكمال دون إعداد هذه الميزات بنفسك:

```python
from scrapling.spiders import ContentSpider

class DocsSpider(ContentSpider):
    name = "docs"
    start_urls = ["https://example.com/docs/"]
    allowed_domains = {"example.com"}
    output_dir = "docs_markdown"
    max_pages = 200

result = DocsSpider().start()
result.items.to_jsonl("docs.jsonl")
```

تنتج كل صفحة عنصرًا واحدًا يحتوي على المفاتيح `url` و`title` و`markdown`. وعند تعيين `output_dir`، تُحفظ كل صفحة أيضًا في ملف Markdown اسمه مشتق من رابطها. لذا ينتج المثال أعلاه مجلدًا من ملفات `.md` وملف `docs.jsonl` جاهزًا للمعالجة.

يتطلب القالب تعيين `allowed_domains` ليبقى الزحف داخل الموقع المطلوب. الخيارات هي:

- `css_selector` / `main_content_only`: يُمرّران إلى `markdown()` لكل صفحة. ويكون `main_content_only` مفعّلًا افتراضيًا.
- `output_dir`: عند تعيينه، يُكتب ملف Markdown لكل صفحة.
- `max_pages`: أقصى عدد صفحات للتحويل. قد تُجلب الطلبات الموجودة بالفعل في قائمة الانتظار عند بلوغ الحد، لكنها لن تُحوّل. القيمة `0`، وهي الافتراضية، تلغي هذا الحد.

يتبع القالب افتراضيًا كل رابط صفحة داخل `allowed_domains`. ولأنه مبني على [CrawlSpider](../spiders/generic-templates.md#crawlspider)، يمكنك تعريف `rules()` مع [LinkExtractor](../spiders/generic-templates.md#linkextractor-reference) الخاص بك للتحكم في الزحف: يحدد `allow` أنماط الروابط المطلوبة، ويستبعد `deny` الأنماط غير المطلوبة، مثل صفحات تسجيل الدخول وقوائم الوسوم ونسخ الطباعة:

```python
from scrapling.spiders import CrawlRule, LinkExtractor, ContentSpider

class DocsSpider(ContentSpider):
    name = "docs"
    start_urls = ["https://example.com/"]
    allowed_domains = {"example.com"}

    def rules(self):
        return [CrawlRule(LinkExtractor(allow=r"/docs/", deny=[r"/docs/changelog/", r"\?print="]))]
```

تكون الأولوية لـ `deny` على `allow`. ويمكن أن تتضمن القاعدة `priority` أو دالة `process_request` كما في أي **CrawlSpider**.

## إدخال البيانات إلى مخزن المتجهات {#feeding-a-vector-store}

يمكن استخدام ملف JSONL الناتج مع أي مسار عمل لإنشاء embeddings، أي تمثيلات رقمية للنصوص. مثال بسيط:

```python
import json

with open("docs.jsonl", encoding="utf-8") as f:
    for line in f:
        page = json.loads(line)
        for chunk in split_into_chunks(page["markdown"]):
            vector_store.add(text=chunk, metadata={"url": page["url"], "title": page["title"]})
```

استخدم `css_selector` في العنكبوت لإزالة المحتوى المتكرر قبل تقسيم النص، بدلًا من تنظيفه لاحقًا. كلما قل المحتوى غير المفيد في البيانات التي تحوّلها إلى متجهات، تحسّنت نتائج الاسترجاع.

## بدائل تفاعلية {#interactive-alternatives}

إذا كنت تفضّل استخراج البيانات عبر المحادثة بدلًا من مسارات المعالجة، فإن [خادم MCP](mcp-server.md) يتيح لمساعد الذكاء الاصطناعي أدوات استخراج Markdown نفسها. كما تعلّم [مهارة الوكيل](agent-skill.md) وكلاء البرمجة كتابة هذا الكود بأنفسهم.
