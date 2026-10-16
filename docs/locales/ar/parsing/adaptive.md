---
title: "تتبع عناصر HTML والعثور عليها بعد تغير الصفحة"
description: "احفظ تفاصيل العناصر واعثر عليها بعد تغير HTML. تعرّف على تفعيل التحليل التكيفي واستخدام save وretrieve وrelocate."
---

# جمع البيانات مع تغيّر الصفحة {#adaptive-scraping}

!!! success "قبل البدء"

    1. اقرأ صفحة [البحث عن العناصر](../parsing/selection.md) لتعرف كيف تجد العناصر وتستخرجها من كائن [Selector](../parsing/main_classes.md#selector).
    2. اقرأ صفحة [الفئات الأساسية](../parsing/main_classes.md) لتفهم فئة [Selector](../parsing/main_classes.md#selector).

التحليل التكيفي Adaptive scraping، المعروف سابقًا باسم automatch، من أقوى ميزات Scrapling. يساعد برنامجك على الاستمرار بعد تغيّر الموقع، بتتبع العناصر والعثور على أماكنها الجديدة.

لنفترض أنك تجمع بيانات صفحة بهذا الشكل:
```html
<div class="container">
    <section class="products">
        <article class="product" id="p1">
            <h3>Product 1</h3>
            <p class="description">Description 1</p>
        </article>
        <article class="product" id="p2">
            <h3>Product 2</h3>
            <p class="description">Description 2</p>
        </article>
    </section>
</div>
```
وتريد جمع بيانات المنتج الأول، الذي يحمل المعرّف `p1`. غالبًا ستكتب محددًا مثل هذا:
```python
page.css('#p1')
```
إذا غيّر أصحاب الموقع بنية الصفحة إلى الشكل التالي:
```html
<div class="new-container">
    <div class="product-wrapper">
        <section class="products">
            <article class="product new-class" data-id="p1">
                <div class="product-info">
                    <h3>Product 1</h3>
                    <p class="new-description">Description 1</p>
                </div>
            </article>
            <article class="product new-class" data-id="p2">
                <div class="product-info">
                    <h3>Product 2</h3>
                    <p class="new-description">Description 2</p>
                </div>
            </article>
        </section>
    </div>
</div>
```
فلن يعمل المحدد بعد ذلك، وسيحتاج الكود إلى تعديل. هنا تأتي فائدة `adaptive` في Scrapling.

فعّل `adaptive` عند اختيار العنصر أول مرة. وعندما تبحث عنه لاحقًا ولا تجده، يتذكر Scrapling خصائصه ويبحث في الموقع عن العنصر الأعلى تشابهًا معه، دون ذكاء اصطناعي :)

```python
from scrapling import Selector, Fetcher
# Before the change
page = Selector(page_source, adaptive=True, url='example.com')
# or
Fetcher.adaptive = True
page = Fetcher.get('https://example.com')
# then
element = page.css('#p1', auto_save=True)
if not element:  # One day website changes?
    element = page.css('#p1', adaptive=True)  # Scrapling still finds it!
# the rest of your code...
```
سأعرض مثالًا أولًا، ثم أشرح طريقة الاستخدام والتفاصيل. تعمل هذه الميزة مع كل طرق اختيار العناصر، وليس CSS وXPath فقط.

## مثال من موقع حقيقي {#real-world-scenario}
لنستخدم موقعًا حقيقيًا ونجلب مصدره بأحد أدوات الجلب. نحتاج إلى موقع سيتغير تصميمه أو بنيته قريبًا، لننسخ المصدر ثم ننتظر التغيير. يصعب معرفة ذلك ما لم أكن أعرف صاحب الموقع، لكن هذا سيجعل الاختبار مُعدًّا مسبقًا، ههه.

لحل ذلك سأستخدم [Wayback Machine](https://web.archive.org/) من [The Web Archive](https://archive.org/). هذه نسخة من [موقع StackOverflow في 2010](https://web.archive.org/web/20100102003420/http://stackoverflow.com/)، قديمة فعلًا!<br/>لنرَ هل تستطيع ميزة adaptive استخراج الزر نفسه من تصميم 2010 والتصميم الحالي بالمحدد نفسه :)

لاستخراج زر Questions من التصميم القديم، يمكنني استخدام `#hmenus > div:nth-child(1) > ul > li:nth-child(1) > a`. هذا المحدد شديد التحديد لأن Google Chrome أنشأه.


لنجرّب المحدد نفسه مع النسختين:
```python
from scrapling import Fetcher
selector = '#hmenus > div:nth-child(1) > ul > li:nth-child(1) > a'
old_url = "https://web.archive.org/web/20100102003420/http://stackoverflow.com/"
new_url = "https://stackoverflow.com/"
Fetcher.configure(adaptive = True, adaptive_domain='stackoverflow.com')
page = Fetcher.get(old_url, timeout=30)
element1 = page.css(selector, auto_save=True)[0]
# Same selector but used in the updated website
page = Fetcher.get(new_url)
element2 = page.css(selector, adaptive=True)[0]

if element1.text == element2.text:
    print('Scrapling found the same element in the old and new designs!')  # Spoiler alert: it does!
```
لاحظ الخيار الجديد `adaptive_domain`. يرى Scrapling أن `archive.org` و`stackoverflow.com` نطاقان مختلفان، ولذلك يفصل بيانات `adaptive` بينهما. لنعلمه أنهما الموقع نفسه، نمرّر نطاقًا مخصصًا يُستخدم عند حفظ بيانات الاثنين، فلا يفصلها.

في الاستخدام الفعلي، سيكون الكود نفسه لكن الطلبين يستخدمان الرابط نفسه، فلن تحتاج إلى `adaptive_domain`. هذا أقرب مثال عملي يمكنني تقديمه، وأتمنى أن يكون واضحًا :)

استخدمت `Selector` و`Fetcher` في المثالين السابقين لتوضيح أن طريقة عمل adaptive واحدة في الحالتين.

!!! info "معلومة"

    السبب الأساسي لإضافة `adaptive_domain` هو التعامل مع تغيّر رابط الموقع عند تغيّر تصميمه أو بنيته. يمكنك عندها متابعة استخدام بيانات adaptive المحفوظة مع الرابط الجديد. دون ذلك، سيعتبره Scrapling موقعًا جديدًا ولن يستخدم البيانات القديمة.

## كيف تعمل ميزة adaptive؟ {#how-the-adaptive-scraping-feature-works}
تعمل على مرحلتين:

1. **الحفظ**: تخزين الخصائص المميزة للعناصر.
2. **المطابقة**: البحث لاحقًا عن عناصر ذات خصائص مشابهة.

لنفترض أنك اخترت عنصرًا بأي طريقة، وتريد أن تعثر عليه المكتبة في المرة التالية، حتى لو تغير تصميم الموقع أو بنيته.

بأقل قدر من التفاصيل التقنية، تعمل الميزة كما يلي:

  1. تطلب من Scrapling حفظ خصائص العنصر المميزة بإحدى الطرق التي سنعرضها لاحقًا.
  2. يحفظ Scrapling هذه الخصائص في قاعدة البيانات المحددة، وهي SQLite افتراضيًا.
  3. لأن صاحب الموقع قد يغير أو يزيل أي خاصية، فلا تصلح أي منها كمعرّف ثابت في قاعدة البيانات. لذلك يعتمد نظام التخزين على شيئين:
     1. نطاق الموقع الحالي. مرّره عند إنشاء `Selector`، أو دع أداة الجلب تستخرجه من الرابط تلقائيًا.
     2. معرّف `identifier` لاسترجاع خصائص العنصر من قاعدة البيانات. لا تحتاج دائمًا إلى تحديده بنفسك، وسنشرح ذلك لاحقًا.

     يُستخدم الاثنان معًا لاحقًا لاسترجاع الخصائص المميزة من قاعدة البيانات.

  4. عندما تتغير بنية الموقع، فعّل `adaptive` واطلب من Scrapling العثور على العنصر. يسترجع خصائصه المحفوظة، ويقارن بها كل عناصر الصفحة، ثم يحسب درجة تشابه لكل عنصر. تأخذ المقارنة كل التفاصيل في الحسبان، كما سنرى.
  5. تُعاد العناصر التي تحقق أعلى درجة تشابه مع العنصر المطلوب.

### الخصائص المميزة {#the-unique-properties}
قد تتساءل: ما الخصائص المميزة التي نعتمد عليها إذا كان يمكن تغيير كل خصائص العنصر أو إزالتها؟

يعتمد Scrapling على ما يلي:

- اسم وسم العنصر، ونصه، وخصائصه بأسمائها وقيمها، وأشقائه بأسماء وسومهم فقط، ومساره بأسماء الوسوم فقط.
- اسم وسم العنصر الأب، وخصائصه بأسمائها وقيمها، ونصه.

المقارنة لا تشترط التطابق الكامل، بل تقيس مدى التشابه. لذلك تأخذ كل شيء في الحسبان، حتى ترتيب القيم، مثل ترتيب أسماء class في العنصر قبل التغيير وبعده.

## استخدام ميزة adaptive {#how-to-use-adaptive-feature}
يمكن تطبيق الميزة على أي عنصر تجده. وتتوفر أيضًا كخيارات في دوال CSS وXPath كما رأيت، وسنعود إلى ذلك لاحقًا.

أولًا، فعّل الميزة بتمرير `adaptive=True` عند إنشاء [Selector](main_classes.md#selector)، أو فعّلها في أداة الجلب التي تستخدمها كما يلي.

أمثلة:
```python
from scrapling import Selector, Fetcher
page = Selector(html_doc, adaptive=True)
# OR
Fetcher.adaptive = True
page = Fetcher.get('https://example.com')
```
إذا كنت تستخدم [Selector](main_classes.md#selector)، مرّر رابط الموقع عبر `url` حتى يفصل Scrapling الخصائص المحفوظة للعناصر حسب النطاق.

إذا لم تمرّر رابطًا، تُستخدم الكلمة `default` مكانه عند حفظ الخصائص. يسبب ذلك مشكلة فقط إذا استخدمت المعرّف نفسه لاحقًا لموقع آخر، ولم تمرّر `url` عند إنشائه. تحل البيانات الجديدة محل القديمة عند الحفظ، وتستخدم `adaptive` آخر خصائص محفوظة فقط.

توجد أيضًا خيارات `storage` و`storage_args` للاتصال بقاعدة البيانات. تُستخدم فئة SQLite المرفقة بالمكتبة افتراضيًا. غالبًا لن تحتاج إلى تعديلها إلا إذا أردت كتابة نظام تخزين خاص بك، وهو ما نشرحه في [صفحة مستقلة بقسم التطوير](../development/adaptive_storage_system.md).

بعد تفعيل `adaptive` على المستوى العام، توجد طريقتان أساسيتان لاستخدامها.

### باستخدام CSS أو XPath {#the-cssxpath-selection-way}
كما رأيت، استخدم أولًا `auto_save` عند اختيار عنصر موجود في الصفحة:
```python
element = page.css('#p1', auto_save=True)
```
وعندما لا يعود العنصر موجودًا بالمحدد نفسه، استخدم `adaptive` لتبحث المكتبة عنه:
```python
element = page.css('#p1', adaptive=True)
```
بسيط، أليس كذلك؟

لكن هناك عمل يحدث في الخلفية. هل تتذكر المعرّف المطلوب لاسترجاع العنصر؟ في دالتي `css` و`xpath`، يُستخدم المحدد الذي مرّرته كمعرّف تلقائيًا لتسهيل الاستخدام :)

ويمكنك تمرير `identifier` إلى أي من هذه الدوال لتعيين المعرّف بنفسك. يفيد ذلك في بعض الحالات، كما يمكنك استخدامه عند الحفظ مع `auto_save`.

### الطريقة اليدوية {#the-manual-way}
يمكنك حفظ خصائص العنصر واسترجاعها، ثم العثور على مكانه الجديد يدويًا ضمن ميزة `adaptive`. تتيح هذه الطريقة إعادة العثور على أي عنصر، مهما كانت طريقة اختياره.

لنفترض أنك وجدت العنصر بالنص:
```python
element = page.find_by_text('Tipping the Velvet', first_match=True)
```
احفظ خصائصه المميزة باستخدام `save`، لكن يجب أن تحدد المعرّف بنفسك. اخترت هنا `my_special_element`، والأفضل استخدام معرّف واضح المعنى، مثل أسماء المتغيرات الواضحة :)
```python
page.save(element, 'my_special_element')
```
لاحقًا، استرجع الخصائص واعثر على العنصر داخل الصفحة باستخدام `adaptive` كما يلي:
```python
>>> element_dict = page.retrieve('my_special_element')
>>> page.relocate(element_dict, selector_type=True)
[<data='<a href="catalogue/tipping-the-velvet_99...' parent='<h3><a href="catalogue/tipping-the-velve...'>]
>>> page.relocate(element_dict, selector_type=True).css('::text').getall()
['Tipping the Velvet']
```
نستخدم هنا الدالتين `retrieve` و`relocate`.

إذا أردت إبقاء النتيجة ككائن `lxml.etree`، فلا تمرّر `selector_type`:
```python
>>> page.relocate(element_dict)
[<Element a at 0x105a2a7b0>]
```

## حل المشكلات {#troubleshooting}

### لم يُعثر على عناصر مطابقة {#no-matches-found}
```python
# 1. Check if data was saved
element_data = page.retrieve('identifier')
if not element_data:
    print("No data saved for this identifier")

# 2. Try with different identifier
products = page.css('.product', adaptive=True, identifier='old_selector')

# 3. Save again with new identifier
products = page.css('.new-product', auto_save=True, identifier='new_identifier')
```

### العثور على عناصر غير صحيحة {#wrong-elements-matched}
```python
# Use more specific selectors
products = page.css('.product-list .product', auto_save=True)

# Or save with more context
product = page.find_by_text('Product Name').parent
page.save(product, 'specific_product')
```

## مشكلات معروفة {#known-issues}
عند الحفظ باستخدام `adaptive`، تُحفظ خصائص أول عنصر فقط من نتائج الاختيار. لذلك إذا كان المحدد يختار عناصر مختلفة في مواضع أخرى من الصفحة، فقد تعيد `adaptive` العنصر الأول فقط عند البحث عنه لاحقًا. لا يشمل ذلك محددات CSS المجمعة بفواصل، لأن كل محدد منها يُفصل ويُنفّذ وحده.

## ملاحظات أخيرة {#final-thoughts}
شرح هذه الميزة بالتفصيل وببساطة كان صعبًا. إذا بقي شيء غير واضح، اسأل في [قسم النقاشات](https://github.com/D4Vinci/Scrapling/discussions)، وسأرد بأسرع ما يمكن. يمكنك أيضًا استخدام خادم Discord أو التواصل معي مباشرة :)
