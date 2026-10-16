---
title: "استخدم تحليل Scrapling داخل عنكبوت Scrapy"
description: "حوّل استجابات Scrapy إلى Scrapling أو أضف decorator إلى دالة callback. احتفظ بزاحف Scrapy واستخدم محددات Scrapling والتحليل التكيفي."
---

# دمج Scrapling مع Scrapy {#integrating-scrapling-into-scrapy}

إذا كان لديك مشروع Scrapy، فلا تحتاج إلى إعادة كتابته للاستفادة من API التحليل في Scrapling. يحوّل تكامل Scrapy الاستجابات إلى كائنات [Response](../fetching/choosing.md#response-object) من Scrapling مباشرة داخل دوال callback في العنكبوت. بذلك يستمر Scrapy في إدارة الزحف، بينما تتولى Scrapling التحليل.

!!! note "التثبيت"

    يعمل هذا التكامل مع التثبيت الأساسي لـ Scrapling، أي `pip install scrapling`، دون متطلبات إضافية. يحتاج فقط إلى تثبيت Scrapy، وهو موجود بالفعل في مشروع Scrapy.

## الاستخدام {#usage}

أضف decorator باسم `scrapling_response` إلى أي دالة callback في العنكبوت، وسيصبح المعامل `response` الذي تستقبله كائن `Response` من Scrapling:

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
            card = quote.parent
            yield {
                "text": quote.get_all_text(strip=True),
                "author": card.find("small", class_="author").text,
                "tags": [tag.text for tag in card.find_all("a", class_="tag")],
            }
        next_page = response.css("li.next a::attr(href)").get()
        if next_page:
            yield scrapy.Request(response.urljoin(next_page), callback=self.parse)
```

يعمل هذا الـ decorator مع جميع أنواع callback التي يدعمها Scrapy: الدوال العادية، والمولّدات، وcoroutines، والمولّدات غير المتزامنة. ويحتفظ الغلاف بنوع الدالة واسمها وdocstring الخاصة بها، فتظل آليات فحص دوال callback وعقود اختبارها في Scrapy تعمل.

يمكنك أيضًا تمرير إعدادات [Selector](../parsing/main_classes.md#selector) إلى الـ decorator، وستُمرّر إلى كائن `Response` الناتج:

```python
    @scrapling_response(adaptive=True, keep_comments=True)
    def parse_product(self, response):
        ...
```

إذا كان لديك كائن استجابة من Scrapy خارج دالة callback، مثل middleware أو pipeline، فاستخدم دالة التحويل مباشرة:

```python
from scrapling.integrations.scrapy import convert_response

scrapling_response = convert_response(scrapy_response, keep_comments=False)
```

## ملاحظات {#notes}

- أرجع طلبات الصفحات التالية باستخدام yield مع `scrapy.Request(response.urljoin(href))` كما في المثال أعلاه. تنشئ دالة `Response.follow()` في Scrapling طلبات خاصة بـ [نظام عناكب Scrapling](../spiders/getting-started.md)، ولا يفهمها Scrapy.
- يُنسخ قاموس `meta` في الاستجابة نسخًا سطحيًا، لذلك تظل الكائنات التي خزّنها middleware آخر متاحة. مثلًا، عند استخدام `scrapy-playwright`، تظل الصفحة موجودة في `response.meta["playwright_page"]`.
- تُقرأ cookies من ترويسات `Set-Cookie` الخام وتُضاف إلى قاموس `cookies` في الاستجابة.
