---
title: "اختبارات أداء محلّلات HTML في Python: Scrapling ومكتبات أخرى"
description: "قارن أداء Scrapling مع مكتبات Python الشائعة في تحليل HTML واستخراج النص والبحث عن العناصر المتشابهة."
---

# اختبارات الأداء {#performance-benchmarks}

إلى جانب قدراته، يتميز Scrapling بسرعته العالية. تقارن الاختبارات التالية محلّل Scrapling بمكتبات أخرى شائعة.

### اختبار سرعة استخراج النص من 5000 عنصر متداخل {#text-extraction-speed-test-5000-nested-elements}

| # | المكتبة | الوقت (ms) | مقارنة بـScrapling |
|---|:-----------------:|:---------:|:------------:|
| 1 |     Scrapling     |   1.99    |     1.0x     |
| 2 |   Parsel/Scrapy   |   2.06    |    1.035     |
| 3 |     Raw Lxml      |   2.56    |    1.286     |
| 4 |      PyQuery      |   23.98   |     ~12x     |
| 5 |    Selectolax     |  197.02   |     ~99x     |
| 6 |  MechanicalSoup   |  1545.15  |   ~776.5x    |
| 7 |   BS4 with Lxml   |  1562.1  |   ~785.0x    |
| 8 | BS4 with html5lib |  3412.73  |   ~1714.9x   |


### أداء البحث عن النص والعناصر المتشابهة {#element-similarity-text-search-performance}

تتفوق قدرة Scrapling على العثور على العناصر بعد تغيّر الصفحة على البدائل بفارق واضح:

| المكتبة | الوقت (ms) | مقارنة بـScrapling |
|-------------|:---------:|:------------:|
| Scrapling   |   2.3    |     1.0x     |
| AutoScraper |   12.58   |    5.47x    |

> تمثل النتائج متوسط 100 تشغيل مع قياس الوقت. راجع [benchmarks.py](https://github.com/D4Vinci/Scrapling/blob/main/benchmarks.py) لمعرفة طريقة الاختبار.
