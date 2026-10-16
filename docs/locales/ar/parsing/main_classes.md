---
title: "Selector وSelectors في Scrapling: البيانات والتنقل"
description: "تعرّف على حفظ HTML والنص والخصائص في Selector وSelectors، واستخراج القيم وحل الروابط والتنقل بين الآباء والأبناء والأشقاء."
---

# الفئات الأساسية لتحليل الصفحات {#parsing-main-classes}

!!! success "قبل البدء"

    - اقرأ [البحث عن العناصر](../parsing/selection.md) لتعرف كيف تجد العناصر وتستخرجها من كائن [Selector](../parsing/main_classes.md#selector).

بعد استكشاف طرق اختيار العناصر وميزاتها في Scrapling، لنراجع فئة [Selector](#selector) والكائنات الأخرى لنفهم محلّل الصفحات بصورة أفضل.

فئة [Selector](#selector) هي أساس محلّل Scrapling، وتوفر تحليل HTML واختيار العناصر. يمكنك استيرادها بأي من الطريقتين:
```python
from scrapling import Selector
from scrapling.parser import Selector
```
ثم استخدمها مباشرة كما تعلمت في [النظرة العامة](../overview.md):
```python
page = Selector(
    '<html>...</html>',
    url='https://example.com'
)

# Then select elements as you like
elements = page.css('.product')
```
بعد تمرير HTML أو جلب موقع، يكون الكائن الأساسي الذي تتعامل معه في Scrapling هو [Selector](#selector). وتعيد عمليات الاختيار والتنقل وغيرها كائن [Selector](#selector) أو [Selectors](#selectors)، عندما تكون النتيجة عنصرًا أو مجموعة عناصر من الصفحة، وليست نصًا أو ما شابه.

أي أن الصفحة نفسها كائن [Selector](#selector)، وكذلك عناصرها كائنات [Selector](#selector). أما النص، سواء كان داخل العنصر أو في قيمة خاصية له، فهو كائن [TextHandler](#texthandler). وتُحفظ خصائص العنصر في [AttributesHandler](#attributeshandler). سنعود إليهما لاحقًا، ولنركز الآن على [Selector](#selector).

## Selector {#selector}
### شرح الخيارات {#arguments-explained}
أهم خيار هو `content`، وتمرّر فيه HTML المراد تحليله، كنص `str` أو بايتات `bytes`.

يحدد `url` رابط الصفحة لحل الروابط النسبية وفصل بيانات adaptive المحفوظة حسب النطاق. وتُستخدم `adaptive` و`storage` و`storage_args` مع ميزة [adaptive](adaptive.md)، ولا تؤثر إذا لم تستخدم الميزة.

ثم توجد خيارات لضبط التحليل أو تعديل HTML أثناء تحليله:

- **encoding**: الترميز المستخدم في تحليل HTML. الافتراضي `UTF-8`.
- **keep_comments**: يحدد هل تحتفظ المكتبة بتعليقات HTML أثناء التحليل. معطّل افتراضيًا لأنها قد تسبب مشكلات مختلفة في جمع البيانات.

تركت `huge_tree` و`root` خارج هذا الشرح حتى لا تصبح الصفحة أعقد من اللازم.
قد تلاحظ أنني أفعل ذلك مع ميزات متقدمة لا تحتاج إليها لاستخدام المكتبة. يغطي قسم التطوير هذه التفاصيل إذا أردت التعمق.

تُحمّل معظم خصائص الصفحة وعناصرها عند الحاجة فقط، أي لا تُنشأ حتى تستخدمها، مثل النص داخل الصفحة أو العنصر. هذا أحد أسباب سرعة Scrapling :)

### الخصائص {#properties}
رأيت كثيرًا من هذا في [النظرة العامة](../overview.md)، لكن لا تقلق إن لم تقرأها. سنراجعه بتفصيل أكبر وأمثلة أكثر تقدمًا. وللتوضيح، فصلنا خصائص التنقل في قسم [التنقل](#traversal) أدناه.

للتبسيط، لنفترض أننا نحلّل صفحة HTML التالية:
```html
<html>
  <head>
    <title>Some page</title>
  </head>
  <body>
    <div class="product-list">
      <article class="product" data-id="1">
        <h3>Product 1</h3>
        <p class="description">This is product 1</p>
        <span class="price">$10.99</span>
        <div class="hidden stock">In stock: 5</div>
      </article>
    
      <article class="product" data-id="2">
        <h3>Product 2</h3>
        <p class="description">This is product 2</p>
        <span class="price">$20.99</span>
        <div class="hidden stock">In stock: 3</div>
      </article>
    
      <article class="product" data-id="3">
        <h3>Product 3</h3>
        <p class="description">This is product 3</p>
        <span class="price">$15.99</span>
        <div class="hidden stock">Out of stock</div>
      </article>
    </div>

    <script id="page-data" type="application/json">
      {
        "lastUpdated": "2024-09-22T10:30:00Z",
        "totalProducts": 3
      }
    </script>
  </body>
</html>
```
حمّل الصفحة مباشرة كما سبق:
```python
from scrapling import Selector
page = Selector(html_doc)
```
احصل على كل نص الصفحة، بما فيه نص العناصر المتداخلة:
```python
>>> page.get_all_text()
'Some page\n\n    \n\n      \nProduct 1\nThis is product 1\n$10.99\nIn stock: 5\nProduct 2\nThis is product 2\n$20.99\nIn stock: 3\nProduct 3\nThis is product 3\n$15.99\nOut of stock'
```
احصل على أول عنصر article كما شرحنا. سنستخدمه في المثال:
```python
article = page.find('article')
```
بالطريقة نفسها، احصل على كل نص العنصر، بما فيه العناصر المتداخلة:
```python
>>> article.get_all_text()
'Product 1\nThis is product 1\n$10.99\nIn stock: 5'
```
أما النص المباشر، فسيكون فارغًا لأن العنصر لا يحتوي نصًا مباشرًا في HTML السابق:
```python
>>> article.text
''
```
تقبل `get_all_text` الخيارات الاختيارية التالية:

1. **separator**: الفاصل الذي يربط أجزاء النص المجمّعة. الافتراضي '\n'.
2. **strip**: يزيل المسافات البيضاء من طرفَي النصوص قبل جمعها. معطّل افتراضيًا.
3. **ignore_tags**: tuple بأسماء الوسوم التي تريد تجاهلها مع كل العناصر داخلها. الافتراضي `('script', 'style',)`.
4. **valid_values**: عند تفعيله، تُجمع النصوص ذات القيم الفعلية فقط، وتُتجاهل العناصر ذات النص الفارغ أو المسافات البيضاء فقط. مفعّل افتراضيًا.

النص المعاد هنا كائن [TextHandler](#texthandler)، وليس نصًا عاديًا. سنشرح ذلك لاحقًا. إذا أمكن تحويل المحتوى إلى JSON، استخدم `.json()`:
```python
>>> script = page.find('script')
>>> script.json()
{'lastUpdated': '2024-09-22T10:30:00Z', 'totalProducts': 3}
```
لنحصل الآن على اسم وسم العنصر:
```python
>>> article.tag
'article'
```
إذا استخدمتها على الصفحة مباشرة، فستتعامل مع العنصر الجذري `html`:
```python
>>> page.tag
'html'
```
بهذا اتضحت العلاقة بين `page` و`element`، ولن نكررها.

احصل على خصائص العنصر:
```python
>>> print(article.attrib)
{'class': 'product', 'data-id': '1'}
```
اقرأ خاصية معينة بأي من الطرق التالية:
```python
article.attrib['class']
article.attrib.get('class')
article['class']  # new in v0.3
```
تحقق من وجود خاصية بأي من الطرق التالية:
```python
'class' in article.attrib
'class' in article  # new in v0.3
```
احصل على HTML الخاص بالعنصر:
```python
>>> article.html_content
'<article class="product" data-id="1"><h3>Product 1</h3>\n        <p class="description">This is product 1</p>\n        <span class="price">$10.99</span>\n        <div class="hidden stock">In stock: 5</div>\n      </article>'
```
احصل على نسخة منسقة من HTML الخاص بالعنصر:
```python
print(article.prettify())
```
```html
<article class="product" data-id="1"><h3>Product 1</h3>
    <p class="description">This is product 1</p>
    <span class="price">$10.99</span>
    <div class="hidden stock">In stock: 5</div>
</article>
```
استخدم `.body` للمحتوى الخام للصفحة. منذ v0.4، تعيد `.body` دائمًا `bytes` إذا كان الكائن `Response` صادرًا من أداة جلب.
```python
>>> page.body
'<html>\n  <head>\n    <title>Some page</title>\n  </head>\n  ...'
```
احصل على كل أسلاف العنصر في شجرة DOM:
```python
>>> article.path
[<data='<div class="product-list"> <article clas...' parent='<body> <div class="product-list"> <artic...'>,
 <data='<body> <div class="product-list"> <artic...' parent='<html><head><title>Some page</title></he...'>,
 <data='<html><head><title>Some page</title></he...'>]
```
أنشئ محدد CSS مختصرًا إن أمكن، أو المحدد الكامل:
```python
>>> article.generate_css_selector
'body > div > article'
>>> article.generate_full_css_selector
'body > div > article'
```
وينطبق الأمر نفسه على XPath:
```python
>>> article.generate_xpath_selector
"//body/div/article"
>>> article.generate_full_xpath_selector
"//body/div/article"
```

### التنقل {#traversal}
سنستخدم العناصر السابقة لشرح خصائص ودوال التنقل في الصفحة بالتفصيل.

إذا لم تكن تعرف شجرة DOM أو بنية الشجرة عمومًا، فقد يبدو هذا القسم محيرًا. أنصحك بالبحث عن هذه المفاهيم لفهمها بصورة أفضل.

وإذا أردت شرحًا سريعًا، فهذه الفكرة باختصار.<br/>
العنصر `html` هو جذر شجرة الموقع، لأن كل صفحة تبدأ به.<br/>
يأتي هذا العنصر مباشرة فوق `head` و`body`. وهما «أبناء» له، وهو «الأب» لهما. أما `body` و`head` فهما «شقيقان» لأن لهما الأب نفسه.

الوصول إلى أب العنصر:
```python
>>> article.parent
<data='<div class="product-list"> <article clas...' parent='<body> <div class="product-list"> <artic...'>
>>> article.parent.tag
'div'
```
يمكنك تكرار الوصول بهذه الطريقة، وينطبق ذلك على كل الخصائص والدوال المشابهة التي سنراجعها:
```python
>>> article.parent.parent.tag
'body'
```
احصل على أبناء العنصر:
```python
>>> article.children
[<data='<h3>Product 1</h3>' parent='<article class="product" data-id="1"><h3...'>,
 <data='<p class="description">This is product 1...' parent='<article class="product" data-id="1"><h3...'>,
 <data='<span class="price">$10.99</span>' parent='<article class="product" data-id="1"><h3...'>,
 <data='<div class="hidden stock">In stock: 5</d...' parent='<article class="product" data-id="1"><h3...'>]
```
احصل على كل العناصر الموجودة تحت العنصر. تعمل كنسخة متداخلة من `children`:
```python
>>> article.below_elements
[<data='<h3>Product 1</h3>' parent='<article class="product" data-id="1"><h3...'>,
 <data='<p class="description">This is product 1...' parent='<article class="product" data-id="1"><h3...'>,
 <data='<span class="price">$10.99</span>' parent='<article class="product" data-id="1"><h3...'>,
 <data='<div class="hidden stock">In stock: 5</d...' parent='<article class="product" data-id="1"><h3...'>]
```
تعيد هنا النتيجة نفسها التي تعيدها `children`، لأن أبناء هذا العنصر ليس لهم أبناء.

يوضح المثال التالي، باستخدام العنصر ذي class باسم `product-list`، الفرق بين `children` و`below_elements`:
```python
>>> products_list = page.css('.product-list')[0]
>>> products_list.children
[<data='<article class="product" data-id="1"><h3...' parent='<div class="product-list"> <article clas...'>,
 <data='<article class="product" data-id="2"><h3...' parent='<div class="product-list"> <article clas...'>,
 <data='<article class="product" data-id="3"><h3...' parent='<div class="product-list"> <article clas...'>]

>>> products_list.below_elements
[<data='<article class="product" data-id="1"><h3...' parent='<div class="product-list"> <article clas...'>,
 <data='<h3>Product 1</h3>' parent='<article class="product" data-id="1"><h3...'>,
 <data='<p class="description">This is product 1...' parent='<article class="product" data-id="1"><h3...'>,
 <data='<span class="price">$10.99</span>' parent='<article class="product" data-id="1"><h3...'>,
 <data='<div class="hidden stock">In stock: 5</d...' parent='<article class="product" data-id="1"><h3...'>,
 <data='<article class="product" data-id="2"><h3...' parent='<div class="product-list"> <article clas...'>,
...]
```
احصل على أشقاء العنصر:
```python
>>> article.siblings
[<data='<article class="product" data-id="2"><h3...' parent='<div class="product-list"> <article clas...'>,
 <data='<article class="product" data-id="3"><h3...' parent='<div class="product-list"> <article clas...'>]
```
احصل على العنصر التالي للعنصر الحالي:
```python
>>> article.next
<data='<article class="product" data-id="2"><h3...' parent='<div class="product-list"> <article clas...'>
```
وينطبق المنطق نفسه على `previous`:
```python
>>> article.previous  # It's the first child, so it doesn't have a previous element
>>> second_article = page.css('.product[data-id="2"]')[0]
>>> second_article.previous
<data='<article class="product" data-id="1"><h3...' parent='<div class="product-list"> <article clas...'>
```
تحقق بسهولة وسرعة من وجود اسم class معين:
```python
>>> article.has_class('product')
True
```
إذا احتجت إلى أكثر من الأب المباشر، مرّ على كل أسلاف العنصر كما يلي:
```python
for ancestor in article.iterancestors():
    # do something with it...
```
يمكنك البحث عن سلف يحقق شرطًا. مرّر دالة تستقبل كائن [Selector](#selector) وتعيد `True` عند تحقق الشرط، أو `False` خلاف ذلك:
```python
>>> article.find_ancestor(lambda ancestor: ancestor.has_class('product-list'))
<data='<div class="product-list"> <article clas...' parent='<body> <div class="product-list"> <artic...'>

>>> article.find_ancestor(lambda ancestor: ancestor.css('.product-list'))  # Same result, different approach
<data='<div class="product-list"> <article clas...' parent='<body> <div class="product-list"> <artic...'>
```
## Selectors {#selectors}
فئة `Selectors` هي نسخة القائمة من [Selector](#selector). ترث من نوع `List` القياسي في Python، فتشترك معه في الخصائص والدوال، وتضيف طرقًا تسهّل التعامل مع كائنات [Selector](#selector) داخلها.

في فئة [Selector](#selector)، تعيد كل الدوال والخصائص التي تنتج مجموعة عناصر كائنًا من [Selectors](#selectors).

منذ v0.4، تعيد كل طرق الاختيار كائنات [Selector](#selector) أو [Selectors](#selectors) بصورة ثابتة، حتى للعقد النصية وقيم الخصائص. تُغلّف النتائج المختارة عبر `::text` أو `/text()` أو `::attr()` أو `/@attr` في كائنات [Selector](#selector). تكون `tag` فيها `"#text"`، وتعيد خاصية `text` قيمة النص. ويمكنك الوصول إلى القيمة مباشرة، بينما تعيد بقية الخصائص قيمًا فارغة أو افتراضية دون خطأ.

```python
page.css('a::text')              # -> Selectors (of text node Selectors)
page.xpath('//a/text()')         # -> Selectors
page.css('a::text').get()        # -> TextHandler (the first text value)
page.css('a::text').getall()     # -> TextHandlers (all text values)
page.css('a::attr(href)')        # -> Selectors
page.xpath('//a/@href')          # -> Selectors
page.css('.price_color')         # -> Selectors
```

### دوال استخراج البيانات {#data-extraction-methods}
منذ v0.4، توفر [Selector](#selector) و[Selectors](#selectors) الدالتين `get()` و`getall()`، والاسمين البديلين `extract_first` و`extract` وفق أسلوب Scrapy. أُزيلت الدالة القديمة `get_all()`.

**في كائن [Selector](#selector):**

- تعيد `get()` كائن `TextHandler`: قيمة النص للعقد النصية، أو HTML الخارجي كاملًا للعناصر.
- تعيد `getall()` قائمة `TextHandlers` تحتوي النص الناتج الواحد.
- `extract_first` اسم بديل لـ`get()`، و`extract` اسم بديل لـ`getall()`.

```python
>>> page.css('h3')[0].get()        # Outer HTML of the element
'<h3>Product 1</h3>'

>>> page.css('h3::text')[0].get()  # Text value of the text node
'Product 1'
```

**في كائن [Selectors](#selectors):**

- تعيد `get(default=None)` النص الناتج من العنصر **الأول**، أو `default` إذا كانت القائمة فارغة.
- تحوّل `getall()` **كل** العناصر إلى نصوص، وتعيد قائمة `TextHandlers`.
- `extract_first` اسم بديل لـ`get()`، و`extract` اسم بديل لـ`getall()`.

```python
>>> page.css('.price::text').get()      # First price text
'$10.99'

>>> page.css('.price::text').getall()   # All price texts
['$10.99', '$20.99', '$15.99']

>>> page.css('.price::text').get('')    # With default value
'$10.99'
```

تعمل هذه الدوال مع كل طرق الاختيار، مثل CSS وXPath و`find`، وهي الطريقة الموصى بها لاستخراج النص وقيم الخصائص بأسلوب متوافق مع Scrapy.

لنرَ الآن ما تضيفه فئة [Selectors](#selectors).
### الخصائص {#properties_1}
إلى جانب عمليات قوائم Python المعتادة، مثل المرور على العناصر وتقطيع القوائم،

يمكنك فعل ما يلي:

نفّذ محددات CSS وXPath مباشرة على كائنات [Selector](#selector) داخل القائمة. أنواع النتائج هي نفسها في دالتي `css` و`xpath` على [Selector](#selector)، والخيارات متشابهة، لكن `adaptive` غير متاح هنا. يجعل ذلك ربط الدوال ببعضها سهلًا.
```pycon
>>> page.css('.product h3::text').getall()
['Product 1', 'Product 2', 'Product 3']
>>> page.css('.product').css('h3::text').getall()
['Product 1', 'Product 2', 'Product 3']
```
شغّل `re` و`re_first` مباشرة بالخيارات نفسها التي تقبلها [Selector](#selector). سنشرح الدالتين في قسم [TextHandler](#texthandler) أدناه.

لكن `re_first` هنا تعمل بطريقة مختلفة: تشغّل `re` على كل [Selector](#selector) وتعيد أول نتيجة تجدها. أما `re` فتعيد كائن [TextHandlers](#texthandlers) كالمعتاد، وتجمع كل كائنات [TextHandler](#texthandler) الناتجة في كائن [TextHandlers](#texthandlers) واحد.
```pycon
>>> page.css('.price::text').re(r'[\d.]+')
['10.99', '20.99', '15.99']
>>> page.css('.product h3::text').re(r'Product (\d+)')
['1', '2', '3']
```
باستخدام `search`، ابحث بسرعة داخل كائنات [Selector](#selector) الموجودة. يجب أن تستقبل الدالة الممرّرة كائن [Selector](#selector) كأول مُدخل، وتعيد True أو False. تعيد `search` أول كائن [Selector](#selector) يحقق الشرط، أو `None` إذا لم تجده.

```pycon
>>> product = page.css('.product').search(lambda p: p.css('.price::text').get() == '$20.99')
>>> product.css('h3::text').get()
'Product 2'
```
يمكنك استخدام `filter` أيضًا. تستقبل دالة مثل `search`، لكنها تعيد `Selectors` يحتوي **كل** كائنات [Selector](#selector) التي تحقق الشرط:

```pycon
>>> products = page.css('.product').filter(lambda p: float(p.css('.price::text').re_first(r'[\d.]+')) > 15)
>>> products.css('h3::text').getall()
['Product 2', 'Product 3']
```
يمكنك الوصول إلى أول عنصر أو آخر عنصر بأمان دون أخطاء الفهرسة:
```python
>>> page.css('.product').first   # First Selector or None
<data='<article class="product" data-id="1"><h3...'>
>>> page.css('.product').last    # Last Selector or None
<data='<article class="product" data-id="3"><h3...'>
>>> page.css('.nonexistent').first  # Returns None instead of raising IndexError
```

لمعرفة عدد كائنات [Selector](#selector) داخل [Selectors](#selectors) بطريقة مختصرة، استخدم:
```python
page.css('.product').length
```
وهو يساوي:
```python
len(page.css('.product'))
```
نعم، مثل JavaScript :)

## TextHandler {#texthandler}
من المهم فهم هذه الفئة، لأن الدوال والخصائص التي تعيد نصًا ستعيد `TextHandler`، والتي تعيد قائمة نصوص ستعيد [TextHandlers](#texthandlers).

ترث TextHandler من النص القياسي في Python، لذلك يمكنك إجراء كل عمليات نصوص Python عليها. فما الذي يميزها؟

تضيف TextHandler دوال وخصائص غير موجودة في النصوص العادية. سنراجعها الآن. تذكر أن كل دوال وخصائص الفئات التي تعيد نصوصًا تستخدم TextHandler، وهذا يتيح ربط العمليات ويجعل الكود أقصر وأوضح. ويمكنك استيرادها واستخدامها على أي نص، كما سنشرح [لاحقًا](../development/scrapling_custom_types.md).
### الاستخدام {#usage}
قبل شرح الإضافات، اعلم أن عمليات مثل التقطيع والوصول بالفهرس، ودوال مثل `split` و`replace` و`strip`، تعيد `TextHandler` مرة أخرى، فيمكنك ربطها كما تريد. إذا وجدت دالة أو خاصية تعيد نصًا عاديًا بدلًا منها، افتح issue لنعدّلها أيضًا.

نبدأ بـ`re` و`re_first`. هما الدالتان الموجودتان في الفئات الأخرى، أي [Selector](#selector) و[Selectors](#selectors) و[TextHandlers](#texthandlers)، ولذلك تقبلان الخيارات نفسها.

- تستقبل `re` نص التعبير المنتظم أو نمطًا مُجهّزًا كأول مُدخل، وتبحث عن كل النصوص المطابقة وتعيدها في [TextHandlers](#texthandlers). تقبل `re_first` الخيارات نفسها وتعمل بالطريقة نفسها، لكنها تعيد النتيجة الأولى فقط ككائن `TextHandler`.
    
    وتقبل أيضًا الخيارات المفيدة التالية:
    
    - **replace_entities**: مفعّل افتراضيًا. يستبدل مراجع كيانات الأحرف بالأحرف التي تمثلها.
    - **clean_match**: معطّل افتراضيًا. ينظف المسافات البيضاء، بما فيها المسافات المتكررة، قبل المطابقة.
    - **case_sensitive**: مفعّل افتراضيًا. عند تعطيله، يتجاهل التعبير المنتظم الفرق بين الأحرف الكبيرة والصغيرة أثناء تجهيزه.
  
    رأيت هذه الأمثلة من قبل. النتيجة من نوع [TextHandlers](#texthandlers) لأننا استخدمنا `re`.
    ```pycon
    >>> page.css('.price::text').re(r'[\d.]+')
    ['10.99', '20.99', '15.99']
    >>> page.css('.product h3::text').re(r'Product (\d+)')
    ['1', '2', '3']
    ```
    لتوضيح الخيارات الأخرى، سنستخدم نصًا خاصًا في كل مثال:
    ```python
    >>> from scrapling import TextHandler
    >>> test_string = TextHandler('hi  there')  # Hence the two spaces
    >>> test_string.re('hi there')
    >>> test_string.re('hi there', clean_match=True)  # Using `clean_match` will clean the string before matching the regex
    ['hi there']
    
    >>> test_string2 = TextHandler('Oh, Hi Mark')
    >>> test_string2.re_first('oh, hi Mark')
    >>> test_string2.re_first('oh, hi Mark', case_sensitive=False)  # Hence disabling `case_sensitive`
    'Oh, Hi Mark'
    
    # Mixing arguments
    >>> test_string.re('hi there', clean_match=True, case_sensitive=False)
    ['hi there']
    ```
    من فوائد استخدام `TextHandler` بدل النصوص أن خاصية مثل `html_content` تعيده أيضًا، فتستطيع البحث بتعبير منتظم في HTML نفسه:
    ```python
    >>> page.html_content.re('div class=".*">(.*)</div')
    ['In stock: 5', 'In stock: 3', 'Out of stock']
    ```

- توجد أيضًا `.json()` التي تحاول تحويل المحتوى إلى كائن JSON بسرعة إن أمكن، وإلا ترفع خطأ:
  ```python
  >>> page.css('#page-data::text').get()
    '\n      {\n        "lastUpdated": "2024-09-22T10:30:00Z",\n        "totalProducts": 3\n      }\n    '
  >>> page.css('#page-data::text').get().json()
    {'lastUpdated': '2024-09-22T10:30:00Z', 'totalProducts': 3}
  ```
  إذا لم تختَر عقدة نصية عند اختيار العنصر، مثل نصه أو قيمة خاصية، يُستخدم محتواه النصي تلقائيًا:
  ```python
  >>> page.css('#page-data')[0].json()
  {'lastUpdated': '2024-09-22T10:30:00Z', 'totalProducts': 3}
  ```
  تضيف فئة [Selector](#selector) سلوكًا آخر هنا. لنفترض أن هذه هي الصفحة:
  ```html
  <html>
      <body>
          <div>
            <script id="page-data" type="application/json">
              {
                "lastUpdated": "2024-09-22T10:30:00Z",
                "totalProducts": 3
              }
            </script>
          </div>
      </body>
  </html>
  ```
  كما تعرف الآن، توفر [Selector](#selector) دالة `get_all_text` التي تعيد `TextHandler`.<br/><br/>
  إذا كتبت مثلًا:
  ```python
  >>> page.css('div::text').get().json()
  ```
  فستحصل على خطأ، لأن `div` لا يحتوي نصًا مباشرًا يمكن تحويله إلى JSON. في الواقع، لا يحتوي نصًا مباشرًا أصلًا.<br/><br/>
  هنا تساعدك `get_all_text`:
  ```python
  >>> page.css('div')[0].get_all_text(ignore_tags=[]).json()
    {'lastUpdated': '2024-09-22T10:30:00Z', 'totalProducts': 3}
  ```
  استخدمت `ignore_tags` هنا لأن قيمته الافتراضية `('script', 'style',)` كما تعرف.<br/><br/>
  وهناك سلوك مرتبط ستراه عند استخدام أدوات الجلب التي سنشرحها لاحقًا. إذا كان لديك رد JSON مثل هذا:
  ```python
  >>> page = Selector("""{"some_key": "some_value"}""")
  ```
  بما أن [Selector](#selector) مصممة لصفحات HTML، فستتعامل معه كـHTML غير مكتمل وتصلحه. لذلك تعطي `html_content` هذه النتيجة:
  ```python
  >>> page.html_content
  '<html><body><p>{"some_key": "some_value"}</p></body></html>'
  ```
  لكن يمكنك استخدام `json` مباشرة وستعمل:
  ```python
  >>> page.json()
  {'some_key': 'some_value'}
  ```
  قد تتساءل كيف نجح ذلك، مع أن `html` لا يحتوي نصًا مباشرًا.<br/>
  لحالات مثل ردود JSON، تحتفظ [Selector](#selector) بنسخة خام من المحتوى المستلم. عند استخدام `.json()`، تتحقق من هذه النسخة وتحولها إلى JSON. إن لم توجد، كما في العناصر، تتحقق من النص المباشر للعنصر، وإلا تستخدم `get_all_text` مباشرة.<br/>

- دالة مفيدة أخرى هي `.clean()`، وتزيل المسافات البيضاء الزائدة وتجمع المسافات المتكررة في مسافة واحدة، ثم تعيد `TextHandler` جديدًا:
```python
>>> TextHandler('\n wonderful  idea, \reh?').clean()
'wonderful idea, eh?'
```
يمكنك أيضًا تمرير `remove_entities` لتستبدل `clean` كيانات HTML بالأحرف التي تمثلها.

- قد تفيدك أيضًا `.sort()` لترتيب أحرف النص، كما تفعل مع القوائم:
```python
>>> TextHandler('acb').sort()
'abc'
```
أو ترتيبها عكسيًا:
```python
>>> TextHandler('acb').sort(reverse=True)
'cba'
```

ستُضاف دوال وخصائص أخرى مع الوقت. تذكر أن هذه الفئة تحل محل النصوص في معظم أجزاء المكتبة.

## TextHandlers {#texthandlers}
كما قد تتوقع، العلاقة هنا تشبه العلاقة بين [Selectors](#selectors) و[Selector](#selector). ترث الفئة سلوك القوائم القياسية ودوالها، وتضيف `re` و`re_first` فقط.

الاختلاف الوحيد أن `re_first` تشغّل `re` على كل [TextHandler](#texthandler) وتعيد أول نتيجة أو `None`. لا يوجد جديد آخر لشرحه، لكن ستُضاف دوال أخرى مع الوقت.

## AttributesHandler {#attributeshandler}
هذه نسخة للقراءة فقط من قاموس Python القياسي `dict`، وتُستخدم لحفظ خصائص كل عنصر أو كائن [Selector](#selector).
```python
>>> print(page.find('script').attrib)
{'id': 'page-data', 'type': 'application/json'}
>>> type(page.find('script').attrib).__name__
'AttributesHandler'
```
لأنها للقراءة فقط، تستخدم موارد أقل من القاموس القياسي. ومع ذلك توفر دوال القاموس وخصائصه نفسها، باستثناء ما يسمح بتعديل البيانات أو استبدالها.

تضيف حاليًا ميزتين بسيطتين:

- دالة `search_values`

    في القاموس العادي، يمكنك استخدام `dict.get("key_name")` للتحقق من وجود مفتاح. لكن البحث بالقيم بدل المفاتيح يحتاج إلى كود إضافي. تفعل هذه الدالة ذلك نيابة عنك، وتبحث في قيم الخصائص الحالية وتعيد قاموسًا لكل عنصر مطابق.
    
    مثال بسيط:
    ```python
    >>> for i in page.find('script').attrib.search_values('page-data'):
            print(i)
    {'id': 'page-data'}
    ```
    وتوفر الدالة `partial` للبحث بجزء من القيمة:
    ```python
    >>> for i in page.find('script').attrib.search_values('page', partial=True):
            print(i)
    {'id': 'page-data'}
    ```
    المثال الأقرب للاستخدام الفعلي هو دمجها مع `find_all` للعثور على كل العناصر التي تحتوي خصائصها قيمة محددة:
    ```python
    >>> page.find_all(lambda element: list(element.attrib.search_values('product')))
    [<data='<article class="product" data-id="1"><h3...' parent='<div class="product-list"> <article clas...'>,
     <data='<article class="product" data-id="2"><h3...' parent='<div class="product-list"> <article clas...'>,
     <data='<article class="product" data-id="3"><h3...' parent='<div class="product-list"> <article clas...'>]
    ```
    كل هذه العناصر لها القيمة 'product' في الخاصية `class`.
    
    استخدمت `list` لأن `search_values` تعيد generator، وهو مولّد قيم يُعد True بحد ذاته لكل العناصر حتى إن لم ينتج نتائج.

- خاصية `json_string`

    تحول الخصائص الحالية إلى JSON إذا أمكن، وإلا ترفع خطأ.
  
    ```python
    >>>page.find('script').attrib.json_string
    b'{"id":"page-data","type":"application/json"}'
    ```
