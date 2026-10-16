---
title: "استخراج بيانات HTML باستخدام CSS وXPath والنص والتعبيرات المنتظمة"
description: "اختر عناصر HTML باستخدام CSS وXPath والنص والتعبيرات المنتظمة، واعثر على العناصر المتشابهة واستخرج الحقول مع أمثلة Scrapling."
---

# البحث عن العناصر {#querying-elements}
تحلّل فئة `Selector` محتوى HTML. اخترنا ذلك لأن ميزة adaptive لا تعمل مع XML. لخلاصات XML أو RSS أو Atom، استخدم [XMLFeedSpider](../spiders/generic-templates.md#xmlfeedspider)، الذي يستخدم محلّل XML ويعطيك كل عقدة في الخلاصة مباشرة.

توجد خمس طرق أساسية للعثور على العناصر في Scrapling:

1. محددات CSS3.
2. محددات XPath.
3. البحث بالمرشحات أو الشروط.
4. البحث عن عناصر يحتوي نصها على نص محدد.
5. البحث عن عناصر يطابق نصها تعبيرًا منتظمًا.

توجد طرق غير مباشرة أخرى، لكننا سنشرح الطرق الأساسية هنا بالتفصيل. وسنشرح أيضًا ميزة مهمة في Scrapling: العثور على عناصر تشبه عنصرًا لديك. يمكنك الانتقال إلى ذلك القسم مباشرة [من هنا](#finding-similar-elements).

إذا كنت جديدًا في جمع بيانات الويب وليس لديك خبرة كبيرة في كتابة المحددات، وتريد بداية سريعة، أنصحك بتعلم `find` و`find_all` مباشرة [من هنا](#filters-based-searching).

## محددات CSS وXPath {#cssxpath-selectors}

### ما محددات CSS؟ {#what-are-css-selectors}
لغة [CSS](https://en.wikipedia.org/wiki/CSS) تُستخدم لتنسيق مستندات HTML. وتعرّف محددات تربط هذه التنسيقات بعناصر HTML معينة.

يدعم Scrapling محددات CSS3 كما تصفها [مواصفات W3C](http://www.w3.org/TR/2011/REC-css3-selectors-20110929/). يأتي هذا الدعم من `cssselect`، لذلك من الأفضل قراءة [المحددات التي تدعمها cssselect](https://cssselect.readthedocs.io/en/latest/#supported-selectors)، بما فيها pseudo-functions وpseudo-elements.

يدعم Scrapling أيضًا بعض pseudo-elements غير القياسية:

* لاختيار العقد النصية، استخدم ``::text``.
* لاختيار قيم الخصائص، استخدم ``::attr(name)``، حيث name اسم الخاصية المطلوبة.

إذا كنت تستخدم Scrapy أو Parsel، فستجد طريقة عمل المحددات نفسها هنا لتسهيل الانتقال. لا حاجة إلى طريقة غريبة عما اعتدنا عليه :)

استخدم `css` للاختيار بمحددات CSS، وهي تعيد `Selectors`. استخدم `[0]` لأول عنصر، أو `.get()` و`.getall()` لاستخراج القيم النصية من محددات النص والخصائص.

### ما محددات XPath؟ {#what-are-xpath-selectors}
لغة [XPath](https://en.wikipedia.org/wiki/XPath) تختار العقد في مستندات XML، ويمكن استخدامها مع HTML أيضًا. هذا [المرجع المختصر](https://devhints.io/xpath) مفيد لتعلم [XPath](https://en.wikipedia.org/wiki/XPath). يوفر Scrapling محددات XPath مباشرة عبر [lxml](https://lxml.de/).

كما في CSS، ستجد طريقة العمل مألوفة إذا كنت تستخدم Scrapy أو Parsel. لكن Scrapling لا يوفر دالة XPath الإضافية `has-class` الموجودة فيهما. بدلًا منها، يوفر `has_class` على العناصر الناتجة للغرض نفسه.

استخدم دالة `xpath` لاختيار العناصر بمحددات XPath. تتبع الطريقة نفسها التي تتبعها دالة CSS السابقة.

> توجد خيارات إضافية في `css` و`xpath` لم نشرحها هنا لأنها تخص ميزة adaptive، التي سنشرحها بالتفصيل في صفحة مستقلة لاحقًا.

### أمثلة على المحددات {#selectors-examples}
لنرَ أمثلة مشتركة على CSS وXPath.

اختر كل العناصر التي لها class باسم `product`:
```python
products = page.css('.product')
products = page.xpath('//*[@class="product"]')
```
!!! info "ملاحظة:"

    لن يكون محدد XPath هنا دقيقًا إذا كان العنصر يحمل class آخر أيضًا. **من الأفضل استخدام CSS للاختيار حسب class.**

اختر أول عنصر له class باسم `product`:
```python
product = page.css('.product')[0]
product = page.xpath('//*[@class="product"]')[0]
```
احصل على نص أول عنصر من نوع `h1`:
```python
title = page.css('h1::text').get()
title = page.xpath('//h1//text()').get()
```
ويمكنك فعل ذلك أيضًا هكذا:
```python
title = page.css('h1')[0].text
title = page.xpath('//h1')[0].text
```
احصل على قيمة `href` لأول عنصر من نوع `a`:
```python
link = page.css('a::attr(href)').get()
link = page.xpath('//a/@href').get()
```
اختر نص أول عنصر `h1` يحتوي `Phone` ويقع داخل عنصر له class باسم `product`:
```python
title = page.css('.product h1:contains("Phone")::text').get()
title = page.xpath('//*[@class="product"]//h1[contains(text(),"Phone")]/text()').get()
```
يمكنك تداخل المحددات وربطها كما تريد ما دامت تعيد نتائج:
```python
page.css('.product')[0].css('h1:contains("Phone")::text').get()
page.xpath('//*[@class="product"]')[0].xpath('.//h1[contains(text(),"Phone")]/text()').get()
page.xpath('//*[@class="product"]')[0].css('h1:contains("Phone")::text').get()
```
استخدم `.//` لجعل XPath نسبيًا للعنصر الحالي. أما البدء بـ`//` فيبحث في المستند كله، حتى بعد اختيار منتج معين.

مثال آخر:

كل الروابط التي تحتوي خاصية 'href' فيها على 'image':
```python
links = page.css('a[href*="image"]')
links = page.xpath('//a[contains(@href, "image")]')
for index, link in enumerate(links):
    link_value = link.attrib['href']  # Cleaner than link.css('::attr(href)').get()
    link_text = link.text
    print(f'Link number {index} points to this url {link_value} with text content as "{link_text}"')
```

## اختيار العناصر بالنص {#text-content-selection}
يتيح Scrapling اختيار العناصر حسب نصها المباشر بطريقتين:

1. عناصر يحتوي نصها المباشر على النص المطلوب، مع خيارات متعددة عبر `find_by_text`.
2. عناصر يطابق نصها المباشر تعبيرًا منتظمًا، مع خيارات متعددة عبر `find_by_regex`.

إذا كنت تتقن التعبيرات المنتظمة regex، يمكنك فعل ما تفعله `find_by_text` باستخدام `find_by_regex`. لكننا نوفر الطريقتين لتسهيل الاستخدام للجميع.

مرّر النص كأول مُدخل إلى `find_by_text`، أو التعبير المنتظم كأول مُدخل إلى `find_by_regex`. تشترك الدالتان في الخيارات التالية:

* **first_match**: إذا كانت `True`، وهي الافتراضية، تعيد الدالة أول نتيجة تجدها.
* **case_sensitive**: إذا كانت `True`، تميز المطابقة بين الأحرف الكبيرة والصغيرة.
* **clean_match**: إذا كانت `True`، تستبدل المسافات البيضاء والمتكررة بمسافة واحدة قبل المطابقة.

تبحث `find_by_text` افتراضيًا عن تطابق كامل، أي يجب أن يساوي نص العنصر النص الذي تمرّره فقط. ولهذا توفر خيارًا إضافيًا:

* **partial**: عند تفعيله، تعيد `find_by_text` العناصر التي تحتوي النص المطلوب ضمن نصها، دون اشتراط التطابق الكامل.

!!! abstract "ملاحظة:"

    تقبل `find_by_regex` نصًا عاديًا أو نمط regex مُجهّزًا كأول مُدخل، كما سترى في الأمثلة.

### العثور على العناصر المتشابهة {#finding-similar-elements}
من أهم ميزات Scrapling القدرة على العثور على عناصر تشبه عنصرًا لديك. جاءت الفكرة من AutoScraper، لكن Scrapling يتيح استخدامها مع عناصر وجدتها بأي طريقة. غالبًا ستستخدمها بعد البحث بالنص، كما في AutoScraper، لذلك نشرحها هنا.

كيف تعمل؟

لنفترض أنك وجدت منتجًا بعنوانه، وتريد استخراج بقية المنتجات في الجدول أو الحاوية نفسها. استدعِ `.find_similar()` على العنصر، وسيفعل Scrapling التالي:

1. يجد كل عناصر الصفحة الموجودة في العمق نفسه في شجرة DOM.
2. يفحصها ويستبعد ما لا يطابق اسم وسم العنصر واسم وسم أبيه واسم وسم جدّه.
3. نكون بذلك واثقين بدرجة كبيرة، نحو 99%، من أن العناصر مناسبة. وكفحص أخير، يستخدم Scrapling المطابقة التقريبية لاستبعاد العناصر التي لا تشبه خصائصها خصائص العنصر الأصلي. توجد نسبة للتحكم في ذلك. أنصح بتركها كما هي ما لم تفشل الإعدادات الافتراضية في الوصول إلى العناصر المطلوبة.

أعرف أن الشرح طويل، لكن التفاصيل مهمة هنا. سنرى أمثلة في القسم التالي. أولًا، هذه الخيارات التي تقبلها الدالة:

* **similarity_threshold**: نسبة التشابه المستخدمة في الخطوة 3 لمقارنة الخصائص. الافتراضي 0.2، أي يجب أن تتشابه خصائص العنصرين بنسبة 20% على الأقل. يمكنك ضبطها على 0 لتعطيل هذا الفحص، لكن أنصح بقراءة بقية الخيارات أولًا.
* **ignore_attributes**: أسماء الخصائص التي تُتجاهل في المقارنة الأخيرة. الافتراضي `('href', 'src',)`، لأن الروابط قد تختلف كثيرًا بين العناصر ولا يُعتمد عليها هنا.
* **match_text**: إذا كانت `True`، يدخل نص العنصر في المقارنة في الخطوة 3. لا يُنصح به في الحالات المعتادة، لكن القرار حسب الحالة.

لنرَ الأمثلة التالية.

### أمثلة {#examples}
أمثلة مشتركة للبحث بالنص والتعبيرات المنتظمة.

سأستخدم فئة `Fetcher` في هذه الأمثلة، وسنشرحها بالتفصيل لاحقًا.
```python
from scrapling.fetchers import Fetcher
page = Fetcher.get('https://books.toscrape.com/index.html')
```
ابحث عن أول عنصر يطابق نصه هذا النص بالكامل:
```python
>>> page.find_by_text('Tipping the Velvet')
<data='<a href="catalogue/tipping-the-velvet_99...' parent='<h3><a href="catalogue/tipping-the-velve...'>
```
ادمجها مع `page.urljoin` لتحويل `href` النسبي إلى رابط كامل:
```python
>>> page.find_by_text('Tipping the Velvet').attrib['href']
'catalogue/tipping-the-velvet_999/index.html'
>>> page.urljoin(page.find_by_text('Tipping the Velvet').attrib['href'])
'https://books.toscrape.com/catalogue/tipping-the-velvet_999/index.html'
```
احصل على كل المطابقات إن وجدت أكثر من واحدة. لاحظ أن النتيجة قائمة:
```python
>>> page.find_by_text('Tipping the Velvet', first_match=False)
[<data='<a href="catalogue/tipping-the-velvet_99...' parent='<h3><a href="catalogue/tipping-the-velve...'>]
```
احصل على كل العناصر التي تحتوي `the`، باستخدام المطابقة الجزئية:
```python
>>> results = page.find_by_text('the', partial=True, first_match=False)
>>> [i.text for i in results]
['A Light in the ...',
 'Tipping the Velvet',
 'The Requiem Red',
 'The Dirty Little Secrets ...',
 'The Coming Woman: A ...',
 'The Boys in the ...',
 'The Black Maria',
 'Mesaerion: The Best Science ...',
 "It's Only the Himalayas"]
```
البحث لا يميز افتراضيًا بين الأحرف الكبيرة والصغيرة، لذلك تظهر `The` أيضًا. لنحصر النتائج في العناصر التي تحتوي `the` بالأحرف الصغيرة فقط:
```python
>>> results = page.find_by_text('the', partial=True, first_match=False, case_sensitive=True)
>>> [i.text for i in results]
['A Light in the ...',
 'Tipping the Velvet',
 'The Boys in the ...',
 "It's Only the Himalayas"]
```
احصل على أول عنصر يطابق نصه تعبير السعر المنتظم:
```python
>>> page.find_by_regex(r'£[\d\.]+')
<data='<p class="price_color">£51.77</p>' parent='<div class="product_price"> <p class="pr...'>
>>> page.find_by_regex(r'£[\d\.]+').text
'£51.77'
```
يمكنك أيضًا تمرير نمط regex مُجهّز. يتعرف Scrapling على نوع المُدخل ويستخدمه:
```python
>>> import re
>>> regex = re.compile(r'£[\d\.]+')
>>> page.find_by_regex(regex)
<data='<p class="price_color">£51.77</p>' parent='<div class="product_price"> <p class="pr...'>
>>> page.find_by_regex(regex).text
'£51.77'
```
احصل على كل العناصر التي تطابق التعبير المنتظم:
```python
>>> page.find_by_regex(r'£[\d\.]+', first_match=False)
[<data='<p class="price_color">£51.77</p>' parent='<div class="product_price"> <p class="pr...'>,
 <data='<p class="price_color">£53.74</p>' parent='<div class="product_price"> <p class="pr...'>,
 <data='<p class="price_color">£50.10</p>' parent='<div class="product_price"> <p class="pr...'>,
 <data='<p class="price_color">£47.82</p>' parent='<div class="product_price"> <p class="pr...'>,
 ...]
```
وهكذا...

ابحث عن كل العناصر التي تشبه العنصر الحالي في الموضع والخصائص. في هذه الحالة نتجاهل 'title' أثناء المطابقة:
```python
>>> element = page.find_by_text('Tipping the Velvet')
>>> element.find_similar(ignore_attributes=['title'])
[<data='<a href="catalogue/a-light-in-the-attic_...' parent='<h3><a href="catalogue/a-light-in-the-at...'>,
 <data='<a href="catalogue/soumission_998/index....' parent='<h3><a href="catalogue/soumission_998/in...'>,
 <data='<a href="catalogue/sharp-objects_997/ind...' parent='<h3><a href="catalogue/sharp-objects_997...'>,
...]
```
لاحظ أن العدد 19 لا 20، لأن العنصر الحالي لا يُضاف إلى النتائج.
```python
>>> len(element.find_similar(ignore_attributes=['title']))
19
```
احصل على `href` من كل العناصر المشابهة:
```python
>>> [
    element.attrib['href']
    for element in element.find_similar(ignore_attributes=['title'])
]
['catalogue/a-light-in-the-attic_1000/index.html',
 'catalogue/soumission_998/index.html',
 'catalogue/sharp-objects_997/index.html',
 ...]
```
لنأخذ مثالًا أكثر تقدمًا: نريد بيانات كل الكتب، باستخدام هذا العنصر كنقطة بداية:
```python
>>> first_product = element.parent.parent
>>> for product in [first_product, *first_product.find_similar()]:
        print({
            "name": product.css('h3 a::text').get(),
            "price": product.css('.price_color')[0].re_first(r'[\d\.]+'),
            "stock": product.css('.availability::text').getall()[-1].clean()
        })
{'name': 'Tipping the Velvet', 'price': '53.74', 'stock': 'In stock'}
{'name': 'A Light in the ...', 'price': '51.77', 'stock': 'In stock'}
{'name': 'Soumission', 'price': '50.10', 'stock': 'In stock'}
{'name': 'Sharp Objects', 'price': '47.82', 'stock': 'In stock'}
...
```
### أمثلة متقدمة {#advanced-examples}
أمثلة أكثر تقدمًا وأقرب للاستخدام الفعلي مع `find_similar`.

استخراج منتجات متجر إلكتروني:
```python
def extract_product_grid(page):
    # Find the first product card
    first_product = page.find_by_text('Add to Cart').find_ancestor(
        lambda e: e.has_class('product-card')
    )

    # Find similar product cards
    products = [first_product, *first_product.find_similar()]

    return [
        {
            'name': p.css('h3::text').get(),
            'price': p.css('.price::text').re_first(r'\d+\.\d{2}'),
            'stock': 'In stock' in p.get_all_text(),
            'rating': p.css('.rating')[0].attrib.get('data-rating')
        }
        for p in products
    ]
```
استخراج صفوف جدول:
```python
def extract_table_data(page):
    # Find the first data row
    first_row = page.css('table tbody tr')[0]

    # Find similar rows
    rows = [first_row, *first_row.find_similar()]

    return [
        {
            'column1': row.css('td:nth-child(1)::text').get(),
            'column2': row.css('td:nth-child(2)::text').get(),
            'column3': row.css('td:nth-child(3)::text').get()
        }
        for row in rows
    ]
```
استخراج حقول نموذج:
```python
def extract_form_fields(page):
    # Find first form field container
    first_field = page.css('input')[0].find_ancestor(
        lambda e: e.has_class('form-field')
    )

    # Find similar field containers
    fields = [first_field, *first_field.find_similar()]

    return [
        {
            'label': f.css('label::text').get(),
            'type': f.css('input')[0].attrib.get('type'),
            'required': 'required' in f.css('input')[0].attrib
        }
        for f in fields
    ]
```
استخراج مراجعات من موقع:
```python
def extract_reviews(page):
    # Find first review
    first_review = page.find_by_text('Great product!')
    review_container = first_review.find_ancestor(
        lambda e: e.has_class('review')
    )
    
    # Find similar reviews
    all_reviews = [review_container, *review_container.find_similar()]
    
    return [
        {
            'text': r.css('.review-text::text').get(),
            'rating': r.attrib.get('data-rating'),
            'author': r.css('.reviewer::text').get()
        }
        for r in all_reviews
    ]
```
## البحث بالمرشحات {#filters-based-searching}
قد تكون هذه أفضل طريقة للبحث عن العناصر في Scrapling، لأنها قوية وأسهل للمبتدئ من كتابة المحددات.

استُلهمت `find_all` و`find` من دالة `find_all` في BeautifulSoup. تقبلان عدة مرشحات وتبحثان عن العناصر التي تحققها كلها.

بالتحديد:

* أي نص تمرّره يُعد اسم وسم.
* أي iterable، مثل List أو Tuple أو Set، يُعد مجموعة أسماء وسوم.
* أي قاموس يُعد مجموعة أسماء خصائص HTML وقيمها للعناصر المطلوبة.
* أي نمط regex يُستخدم لتصفية العناصر حسب محتواها، مثل `find_by_regex`.
* أي دالة تمرّرها تُستخدم لتصفية العناصر.
* أي خيار باسم keyword argument يُعد اسم خاصية HTML وقيمتها.

تجمع الطريقة كل المُدخلات والخيارات، ثم يمرّر كل مرشح نتائجه إلى التالي في سلسلة تصفية.

تُصفّى العناصر في الصفحة أو العنصر الحالي بالترتيب التالي:

1. جمع العناصر التي تطابق أسماء الوسوم الممرّرة.
2. جمع العناصر التي تطابق كل الخصائص الممرّرة، أو تصفية نتائج الخطوة السابقة إن استُخدمت.
3. جمع العناصر التي تطابق كل أنماط regex الممرّرة، أو تصفية نتائج الخطوات السابقة إن استُخدمت.
4. جمع العناصر التي تحقق كل الدوال الممرّرة، أو تصفية نتائج الخطوات السابقة إن استُخدمت.

!!! note "ملاحظات:"

    1. تبدأ التصفية من أول مرشح موجود وفق الترتيب السابق. إذا لم تمرّر أسماء وسوم ومرّرت خصائص، تبدأ من الخطوة 2، وهكذا.
    2. ترتيب تمرير المُدخلات لا يهم. الترتيب المعتمد هو المذكور أعلاه فقط.

ستوضح الأمثلة الفكرة :)

### أمثلة {#examples_1}
```python
from scrapling.fetchers import Fetcher
page = Fetcher.get('https://quotes.toscrape.com/')
```
ابحث عن كل العناصر ذات الوسم `div`:
```python
>>> page.find_all('div')
[<data='<div class="container"> <div class="row...' parent='<body> <div class="container"> <div clas...'>,
 <data='<div class="row header-box"> <div class=...' parent='<div class="container"> <div class="row...'>,
...]
```
ابحث عن كل عناصر div التي تساوي قيمة class فيها `quote`:
```python
>>> page.find_all('div', class_='quote')
[<data='<div class="quote" itemscope itemtype="h...' parent='<div class="col-md-8"> <div class="quote...'>,
 <data='<div class="quote" itemscope itemtype="h...' parent='<div class="col-md-8"> <div class="quote...'>,
...]
```
النتيجة نفسها بطريقة أخرى:
```python
>>> page.find_all('div', {'class': 'quote'})
[<data='<div class="quote" itemscope itemtype="h...' parent='<div class="col-md-8"> <div class="quote...'>,
 <data='<div class="quote" itemscope itemtype="h...' parent='<div class="col-md-8"> <div class="quote...'>,
...]
```
ابحث عن كل العناصر التي تساوي قيمة class فيها `quote`:
```python
>>> page.find_all({'class': 'quote'})
[<data='<div class="quote" itemscope itemtype="h...' parent='<div class="col-md-8"> <div class="quote...'>,
 <data='<div class="quote" itemscope itemtype="h...' parent='<div class="col-md-8"> <div class="quote...'>,
...]
```
ابحث عن كل عناصر div التي تساوي قيمة class فيها `quote`، وتحتوي عنصرًا يطابق `.text` ويحتوي نصه على 'world':
```python
>>> page.find_all('div', {'class': 'quote'}, lambda e: "world" in e.css('.text::text').get())
[<data='<div class="quote" itemscope itemtype="h...' parent='<div class="col-md-8"> <div class="quote...'>]
```
ابحث عن كل العناصر التي لها أبناء:
```python
>>> page.find_all(lambda element: len(element.children) > 0)
[<data='<html lang="en"><head><meta charset="UTF...'>,
 <data='<head><meta charset="UTF-8"><title>Quote...' parent='<html lang="en"><head><meta charset="UTF...'>,
 <data='<body> <div class="container"> <div clas...' parent='<html lang="en"><head><meta charset="UTF...'>,
...]
```
ابحث عن كل العناصر التي يحتوي نصها على 'world':
```python
>>> page.find_all(lambda element: "world" in element.text)
[<data='<span class="text" itemprop="text">“The...' parent='<div class="quote" itemscope itemtype="h...'>,
 <data='<a class="tag" href="/tag/world/page/1/"...' parent='<div class="tags"> Tags: <meta class="ke...'>]
```
ابحث عن كل عناصر span التي تطابق التعبير المنتظم:
```python
>>> page.find_all('span', re.compile(r'world'))
[<data='<span class="text" itemprop="text">“The...' parent='<div class="quote" itemscope itemtype="h...'>]
```
ابحث عن كل عناصر div وspan ذات class باسم 'quote'. لا توجد عناصر span مطابقة هنا، فتُعاد div فقط:
```python
>>> page.find_all(['div', 'span'], {'class': 'quote'})
[<data='<div class="quote" itemscope itemtype="h...' parent='<div class="col-md-8"> <div class="quote...'>,
 <data='<div class="quote" itemscope itemtype="h...' parent='<div class="col-md-8"> <div class="quote...'>,
...]
```
اجمع الطرق معًا:
```python
>>> page.find_all({'itemtype':"http://schema.org/CreativeWork"}, 'div').css('.author::text').getall()
['Albert Einstein',
 'J.K. Rowling',
...]
```
فكرة إضافية: ابحث عن كل العناصر التي تنتهي قيمة `href` فيها بكلمة 'Einstein':
```python
>>> page.find_all({'href$': 'Einstein'})
[<data='<a href="/author/Albert-Einstein">(about...' parent='<span>by <small class="author" itemprop=...'>,
 <data='<a href="/author/Albert-Einstein">(about...' parent='<span>by <small class="author" itemprop=...'>,
 <data='<a href="/author/Albert-Einstein">(about...' parent='<span>by <small class="author" itemprop=...'>]
```
فكرة أخرى: ابحث عن كل العناصر التي تحتوي قيمة `href` فيها على '/author/':
```python
>>> page.find_all({'href*': '/author/'})
[<data='<a href="/author/Albert-Einstein">(about...' parent='<span>by <small class="author" itemprop=...'>,
 <data='<a href="/author/J-K-Rowling">(about)</a...' parent='<span>by <small class="author" itemprop=...'>,
 <data='<a href="/author/Albert-Einstein">(about...' parent='<span>by <small class="author" itemprop=...'>,
...]
```
وهكذا...

## إنشاء المحددات {#generating-selectors}
يمكنك إنشاء محدد CSS أو XPath لأي عنصر، وإعادة استخدامه هنا أو في مكان آخر. ولا يهم بأي طريقة عثرت على العنصر.

أنشئ محدد CSS قصيرًا للعنصر `url_element` إن أمكن، وإلا أنشئ محددًا كاملًا:
```python
>>> url_element = page.find({'href*': '/author/'})
>>> url_element.generate_css_selector
'body > div > div:nth-of-type(2) > div > div > span:nth-of-type(2) > a'
```
أنشئ محدد CSS كاملًا للعنصر `url_element` بدءًا من أول الصفحة:
```python
>>> url_element.generate_full_css_selector
'body > div > div:nth-of-type(2) > div > div > span:nth-of-type(2) > a'
```
أنشئ محدد XPath قصيرًا للعنصر `url_element` إن أمكن، وإلا أنشئ محددًا كاملًا:
```python
>>> url_element.generate_xpath_selector
'//body/div/div[2]/div/div/span[2]/a'
```
أنشئ محدد XPath كاملًا للعنصر `url_element` بدءًا من أول الصفحة:
```python
>>> url_element.generate_full_xpath_selector
'//body/div/div[2]/div/div/span[2]/a'
```
!!! abstract "ملاحظة:"

    عند طلب محدد قصير، يبحث Scrapling عن عنصر مميز ليكون نقطة توقف، مثل عنصر له `id`. لم يوجد عنصر كهذا في مثالنا، لذلك تطابق المحدد القصير والكامل.

## استخدام المحددات مع التعبيرات المنتظمة {#using-selectors-with-regular-expressions}
كما في `parsel` و`scrapy`، توجد `re` و`re_first` لاستخراج البيانات بالتعبيرات المنتظمة. لكنهما هنا متاحتان في معظم الفئات، مثل `Selector` و`Selectors` و`TextHandler` و`TextHandlers`، فتستطيع استخدامهما مباشرة على العنصر دون اختيار عقدة نصية أولًا.

سنشرح ذلك بتفصيل أكبر مع فئة [TextHandler](main_classes.md#texthandler)، لكن هذه أمثلة عامة:
```python
>>> page.css('.price_color')[0].re_first(r'[\d\.]+')
'51.77'

>>> page.css('.price_color').re_first(r'[\d\.]+')
'51.77'

>>> page.css('.price_color').re(r'[\d\.]+')
['51.77',
 '53.74',
 '50.10',
 '47.82',
 '54.23',
...]

>>> page.css('.product_pod h3 a::attr(href)').re(r'catalogue/(.*)/index.html')
['a-light-in-the-attic_1000',
 'tipping-the-velvet_999',
 'soumission_998',
 'sharp-objects_997',
...]

>>> filtering_function = lambda e: e.parent.tag == 'h3' and e.parent.parent.has_class('product_pod')  # As above selector
>>> page.find('a', filtering_function).attrib['href'].re(r'catalogue/(.*)/index.html')
['a-light-in-the-attic_1000']

>>> page.find_by_text('Tipping the Velvet').attrib['href'].re(r'catalogue/(.*)/index.html')
['tipping-the-velvet_999']
```
وهكذا. سنشرح المزيد في الصفحة التالية مع فئة [TextHandler](main_classes.md#texthandler).
