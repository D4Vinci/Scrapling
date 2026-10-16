---
title: "نظرة على Scrapling: تحليل الصفحات وطلبات HTTP والمتصفحات الخفية"
description: "تعرّف على تحليل الصفحات وجلبها في Scrapling، مع أمثلة على CSS وXPath والبحث في النص وطلبات HTTP والمتصفحات الخفية."
---

# ابدأ مع Scrapling {#get-started-with-scrapling}

## اختر نقطة البداية {#pick-your-path}

لا تعرف من أين تبدأ؟ اختر ما يناسب ما تريد عمله:

| أريد أن... | ابدأ هنا |
|---:|---:|
| **أحلّل HTML** موجودًا لدي | [البحث عن العناصر](parsing/selection.md): الاختيار باستخدام CSS وXPath والنص |
| **أجمع بيانات صفحة بسرعة** وأجرّب فكرة | اختر [أداة جلب](fetching/choosing.md) وابدأ التجربة، أو شغّل [الواجهة التفاعلية](cli/interactive-shell.md) |
| **أبني برنامج زحف** يمكن توسيعه | [Spiders](spiders/getting-started.md): زحف متزامن بعدة جلسات، مع الإيقاف والاستئناف |
| **أجمع البيانات دون كتابة كود** | [أوامر الاستخراج من الطرفية](cli/extract-commands.md)، أو اربط [خادم MCP](ai/mcp-server.md) بأداة الذكاء الاصطناعي المفضلة لديك |
| **أنتقل** من مكتبة أخرى | [الانتقال من BeautifulSoup](tutorials/migrating_from_beautifulsoup.md) أو [المقارنة مع Scrapy](spiders/architecture.md#comparison-with-scrapy) |

---

سنبدأ بنظرة سريعة على أدوات تحليل الصفحات. ثم سنجلب المواقع باستخدام متصفحات مخصصة، ونرسل الطلبات، ونحلّل الردود.

سنستخدم مستند HTML التالي، الذي أنشأه ChatGPT، في أمثلة هذه الصفحة:
```python
html_doc = """<html>
  <head>
    <title>Complex Web Page</title>
    <style>
      .hidden { display: none; }
    </style>
  </head>
  <body>
    <header>
      <nav>
        <ul>
          <li> <a href="#home">Home</a> </li>
          <li> <a href="#about">About</a> </li>
          <li> <a href="#contact">Contact</a> </li>
        </ul>
      </nav>
    </header>
    <main>
      <section id="products" schema='{"jsonable": "data"}'>
        <h2>Products</h2>
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
      </section>
      
      <section id="reviews">
        <h2>Customer Reviews</h2>
        <div class="review-list">
          <div class="review" data-rating="5">
            <p class="review-text">Great product!</p>
            <span class="reviewer">John Doe</span>
          </div>
          <div class="review" data-rating="4">
            <p class="review-text">Good value for money.</p>
            <span class="reviewer">Jane Smith</span>
          </div>
        </div>
      </section>
    </main>
    <script id="page-data" type="application/json">
      {
        "lastUpdated": "2024-09-22T10:30:00Z",
        "totalProducts": 3
      }
    </script>
  </body>
</html>"""
```
ابدأ بتحميل HTML السابق بهذه الطريقة:
```python
import re
from scrapling.parser import Selector
page = Selector(html_doc)
page  # <data='<html><head><title>Complex Web Page</tit...'>
```
احصل على كل النص في الصفحة، بما فيه نص العناصر المتداخلة:
```python
page.get_all_text(ignore_tags=('script', 'style'))
# 'Complex Web Page\nHome\nAbout\nContact\nProducts\nProduct 1\nThis is product 1\n$10.99\nIn stock: 5\nProduct 2\nThis is product 2\n$20.99\nIn stock: 3\nProduct 3\nThis is product 3\n$15.99\nOut of stock\nCustomer Reviews\nGreat product!\nJohn Doe\nGood value for money.\nJane Smith'
```

## البحث عن العناصر {#finding-elements}
إذا أردت الوصول إلى عنصر في الصفحة، فستجد طريقة للوصول إليه. يمكنك الجمع بين طرق البحث كما تحتاج.

ابحث عن أول عنصر HTML من نوع `section`:
```python
section_element = page.find('section')
# <data='<section id="products" schema='{"jsonabl...' parent='<main><section id="products" schema='{"j...'>
```
ابحث عن كل عناصر `section`:
```python
section_elements = page.find_all('section')
# [<data='<section id="products" schema='{"jsonabl...' parent='<main><section id="products" schema='{"j...'>, <data='<section id="reviews"><h2>Customer Revie...' parent='<main><section id="products" schema='{"j...'>]
```
ابحث عن كل عناصر `section` التي تساوي فيها قيمة الخاصية `id` النص `products`:
```python
section_elements = page.find_all('section', {'id':"products"})
# Same as
section_elements = page.find_all('section', id="products")
# [<data='<section id="products" schema='{"jsonabl...' parent='<main><section id="products" schema='{"j...'>]
```
ابحث عن كل عناصر `section` التي تحتوي فيها قيمة الخاصية `id` على النص `product`:
```python
section_elements = page.find_all('section', {'id*':"product"})
```
ابحث عن كل عناصر `h3` التي يطابق نصها التعبير المنتظم `Product \d`:
```python
page.find_all('h3', re.compile(r'Product \d'))
# [<data='<h3>Product 1</h3>' parent='<article class="product" data-id="1"><h3...'>, <data='<h3>Product 2</h3>' parent='<article class="product" data-id="2"><h3...'>, <data='<h3>Product 3</h3>' parent='<article class="product" data-id="3"><h3...'>]
```
ابحث عن كل عناصر `h3` و`h2` التي يطابق نصها التعبير المنتظم `Product` فقط:
```python
page.find_all(['h3', 'h2'], re.compile(r'Product'))
# [<data='<h3>Product 1</h3>' parent='<article class="product" data-id="1"><h3...'>, <data='<h3>Product 2</h3>' parent='<article class="product" data-id="2"><h3...'>, <data='<h3>Product 3</h3>' parent='<article class="product" data-id="3"><h3...'>, <data='<h2>Products</h2>' parent='<section id="products" schema='{"jsonabl...'>]
```
ابحث عن كل العناصر التي يساوي نصها `Products` بالضبط، دون احتساب المسافات البيضاء:
```python
page.find_by_text('Products', first_match=False)
# [<data='<h2>Products</h2>' parent='<section id="products" schema='{"jsonabl...'>]
```
أو ابحث عن كل العناصر التي يطابق نصها التعبير المنتظم `Product \d`:
```python
page.find_by_regex(r'Product \d', first_match=False)
# [<data='<h3>Product 1</h3>' parent='<article class="product" data-id="1"><h3...'>, <data='<h3>Product 2</h3>' parent='<article class="product" data-id="2"><h3...'>, <data='<h3>Product 3</h3>' parent='<article class="product" data-id="3"><h3...'>]
```
ابحث عن كل العناصر المشابهة للعنصر الذي تريده:
```python
target_element = page.find_by_regex(r'Product \d', first_match=True)
# <data='<h3>Product 1</h3>' parent='<article class="product" data-id="1"><h3...'>
target_element.find_similar()
# [<data='<h3>Product 2</h3>' parent='<article class="product" data-id="2"><h3...'>, <data='<h3>Product 3</h3>' parent='<article class="product" data-id="3"><h3...'>]
```
ابحث عن أول عنصر يطابق محدد CSS:
```python
page.css('.product-list [data-id="1"]')[0]
# <data='<article class="product" data-id="1"><h3...' parent='<div class="product-list"> <article clas...'>
```
ابحث عن كل العناصر التي تطابق محدد CSS:
```python
page.css('.product-list article')
# [<data='<article class="product" data-id="1"><h3...' parent='<div class="product-list"> <article clas...'>, <data='<article class="product" data-id="2"><h3...' parent='<div class="product-list"> <article clas...'>, <data='<article class="product" data-id="3"><h3...' parent='<div class="product-list"> <article clas...'>]
```
ابحث عن أول عنصر يطابق محدد XPath:
```python
page.xpath("//*[@id='products']/div/article")[0]
# <data='<article class="product" data-id="1"><h3...' parent='<div class="product-list"> <article clas...'>
```
ابحث عن كل العناصر التي تطابق محدد XPath:
```python
page.xpath("//*[@id='products']/div/article")
# [<data='<article class="product" data-id="1"><h3...' parent='<div class="product-list"> <article clas...'>, <data='<article class="product" data-id="2"><h3...' parent='<div class="product-list"> <article clas...'>, <data='<article class="product" data-id="3"><h3...' parent='<div class="product-list"> <article clas...'>]
```

هذه بداية بسيطة فقط. سنعرض لاحقًا خيارات أكثر تقدمًا لطرق البحث هذه.
## الوصول إلى بيانات العناصر {#accessing-elements-data}
الأمر بهذه البساطة:
```pycon
>>> section_element.tag
'section'
>>> print(section_element.attrib)
{'id': 'products', 'schema': '{"jsonable": "data"}'}
>>> section_element.attrib['schema'].json()  # If an attribute value can be converted to json, then use `.json()` to convert it
{'jsonable': 'data'}
>>> section_element.text  # Direct text content
''
>>> section_element.get_all_text()  # All text content recursively
'Products\nProduct 1\nThis is product 1\n$10.99\nIn stock: 5\nProduct 2\nThis is product 2\n$20.99\nIn stock: 3\nProduct 3\nThis is product 3\n$15.99\nOut of stock'
>>> section_element.html_content  # The HTML content of the element
'<section id="products" schema=\'{"jsonable": "data"}\'><h2>Products</h2>\n        <div class="product-list">\n          <article class="product" data-id="1"><h3>Product 1</h3>\n            <p class="description">This is product 1</p>\n            <span class="price">$10.99</span>\n            <div class="hidden stock">In stock: 5</div>\n          </article><article class="product" data-id="2"><h3>Product 2</h3>\n            <p class="description">This is product 2</p>\n            <span class="price">$20.99</span>\n            <div class="hidden stock">In stock: 3</div>\n          </article><article class="product" data-id="3"><h3>Product 3</h3>\n            <p class="description">This is product 3</p>\n            <span class="price">$15.99</span>\n            <div class="hidden stock">Out of stock</div>\n          </article></div>\n      </section>'
>>> print(section_element.prettify())  # The prettified version
'''
<section id="products" schema='{"jsonable": "data"}'><h2>Products</h2>
    <div class="product-list">
      <article class="product" data-id="1"><h3>Product 1</h3>
        <p class="description">This is product 1</p>
        <span class="price">$10.99</span>
        <div class="hidden stock">In stock: 5</div>
      </article><article class="product" data-id="2"><h3>Product 2</h3>
        <p class="description">This is product 2</p>
        <span class="price">$20.99</span>
        <div class="hidden stock">In stock: 3</div>
      </article><article class="product" data-id="3"><h3>Product 3</h3>
        <p class="description">This is product 3</p>
        <span class="price">$15.99</span>
        <div class="hidden stock">Out of stock</div>
      </article>
    </div>
</section>
'''
>>> section_element.path  # All the ancestors in the DOM tree of this element
[<data='<main><section id="products" schema='{"j...' parent='<body> <header><nav><ul><li> <a href="#h...'>,
 <data='<body> <header><nav><ul><li> <a href="#h...' parent='<html><head><title>Complex Web Page</tit...'>,
 <data='<html><head><title>Complex Web Page</tit...'>]
>>> section_element.generate_css_selector
'#products'
>>> section_element.generate_full_css_selector
'body > main > #products'
>>> section_element.generate_xpath_selector
"//*[@id='products']"
>>> section_element.generate_full_xpath_selector
"//body/main/*[@id='products']"
```

## التنقل بين العناصر {#navigation}
نستخدم هنا العناصر التي وجدناها في الأمثلة السابقة:

```pycon
>>> section_element.parent
<data='<main><section id="products" schema='{"j...' parent='<body> <header><nav><ul><li> <a href="#h...'>
>>> section_element.parent.tag
'main'
>>> section_element.parent.parent.tag
'body'
>>> section_element.children
[<data='<h2>Products</h2>' parent='<section id="products" schema='{"jsonabl...'>,
 <data='<div class="product-list"> <article clas...' parent='<section id="products" schema='{"jsonabl...'>]
>>> section_element.siblings
[<data='<section id="reviews"><h2>Customer Revie...' parent='<main><section id="products" schema='{"j...'>]
>>> section_element.next  # gets the next element, the same logic applies to `quote.previous`.
<data='<section id="reviews"><h2>Customer Revie...' parent='<main><section id="products" schema='{"j...'>
>>> section_element.children.css('h2::text').getall()
['Products']
>>> page.css('[data-id="1"]')[0].has_class('product')
True
```
إذا احتجت إلى أكثر من العنصر الأب المباشر، يمكنك المرور على كل أسلاف العنصر في شجرة DOM، كما يلي:
```python
for ancestor in section_element.iterancestors():
    print(ancestor.tag)
```
يمكنك البحث عن سلف محدد يحقق شرطًا. مرّر دالة تستقبل كائن `Selector` وتعيد `True` عند تحقق الشرط، أو `False` خلاف ذلك:
```pycon
>>> section_element.find_ancestor(lambda ancestor: ancestor.css('nav'))
<data='<body> <header><nav><ul><li> <a href="#h...' parent='<html><head><title>Complex Web Page</tit...'>
```

## جلب المواقع {#fetching-websites}
بدلًا من تمرير HTML مباشرة إلى Scrapling، يمكنك جلب رد الموقع عبر طلب HTTP أو تحميله في متصفح.

توجد أداة جلب تناسب كل حالة استخدام.

### طلبات HTTP {#http-requests}
لإرسال طلبات HTTP بسيطة، استورد فئة `Fetcher` واستخدمها كما يلي:
```python
from scrapling.fetchers import Fetcher
page = Fetcher.get('https://scrapling.requestcatcher.com/get', impersonate="chrome")
```
وهكذا تستخدم طرق HTTP المختلفة:
```python
from scrapling.fetchers import Fetcher
page = Fetcher.get('https://scrapling.requestcatcher.com/get', stealthy_headers=True)
page = Fetcher.post('https://scrapling.requestcatcher.com/post', data={'key': 'value'}, proxy='http://username:password@localhost:8030')
page = Fetcher.put('https://scrapling.requestcatcher.com/put', data={'key': 'value'})
page = Fetcher.delete('https://scrapling.requestcatcher.com/delete')
```
للطلبات غير المتزامنة، استبدل الاستيراد كما يلي:
```python
from scrapling.fetchers import AsyncFetcher
page = await AsyncFetcher.get('https://scrapling.requestcatcher.com/get', stealthy_headers=True)
page = await AsyncFetcher.post('https://scrapling.requestcatcher.com/post', data={'key': 'value'}, proxy='http://username:password@localhost:8030')
page = await AsyncFetcher.put('https://scrapling.requestcatcher.com/put', data={'key': 'value'})
page = await AsyncFetcher.delete('https://scrapling.requestcatcher.com/delete')
```

!!! note "ملاحظات:"

    1. عند تفعيل `stealthy_headers`، تُنشأ ترويسات متصفح حقيقية وتُستخدم في الطلبات، بما فيها ترويسة referer من Google. هذا الخيار مفعّل افتراضيًا.
    2. يتيح لك `impersonate` محاكاة بصمة TLS لإصدار محدد من المتصفح.
    3. عند تفعيل `http3`، تستخدم أداة الجلب HTTP/3 في الطلبات، فتبدو الطلبات أقرب إلى طلبات المتصفح الحقيقي.

هذه بعض قدرات أداة الجلب فقط. اقرأ بقية التفاصيل [هنا](fetching/static.md).

### التحميل الديناميكي {#dynamic-loading}
يمكنك أيضًا التعامل مع المواقع الديناميكية، وهي شائعة اليوم.

توفر فئة `StealthyFetcher` خيارات كثيرة لجلب صفحات الويب وتحميلها باستخدام متصفحات مبنية على Chromium.
```python
from scrapling.fetchers import StealthyFetcher
page = StealthyFetcher.fetch('https://quotes.toscrape.com/js/', disable_resources=True, block_ads=True, wait_selector='.quote')
print(len(page.css(".quote")))  # -> 10

# The async version of fetch
page = await StealthyFetcher.async_fetch('https://quotes.toscrape.com/js/', disable_resources=True, block_ads=True, wait_selector='.quote')
print(len(page.css(".quote")))  # -> 10
```
تعتمد على [Playwright](https://playwright.dev/python/) مع تعديلات لإخفاء الأتمتة. استخدم Chromium المرفق، أو Google Chrome المثبّت لديك مع `real_chrome=True`، أو متصفحًا يعمل بالفعل عبر `cdp_url`.

### تجاوز أنظمة كشف البوتات {#anti-bot-features}

من بين ما توفره:

1. تجاوز أنواع Cloudflare Turnstile وInterstitial تلقائيًا باستخدام `solve_cloudflare=True`.
2. منع تسريبات بيئة تشغيل CDP وتسريبات WebRTC.
3. عزل تنفيذ JavaScript، وإزالة كثير من بصمات Playwright، وتجنب بعض السلوكيات المعروفة التي تكشف البوتات.
4. إضافة تشويش إلى canvas لمنع استخدامه في تكوين بصمة للمتصفح.
5. تعديل الطرق المعروفة لكشف وضع المتصفح بلا واجهة تلقائيًا، مع خيار لتجنب الكشف بسبب اختلاف المنطقة الزمنية.
6. وخيارات أخرى لتجاوز أنظمة الحماية...

```python
from scrapling.fetchers import StealthyFetcher
page = StealthyFetcher.fetch('https://www.browserscan.net/bot-detection')  # Running headless by default
page.status == 200  # -> True

page = StealthyFetcher.fetch('https://nopecha.com/demo/cloudflare', solve_cloudflare=True)  # Solve Cloudflare captcha automatically if presented
page.status == 200  # -> True

page = StealthyFetcher.fetch('https://www.browserscan.net/bot-detection', block_webrtc=True, hide_canvas=True, dns_over_https=True) # and the rest of arguments...
# The async version of fetch
page = await StealthyFetcher.async_fetch('https://www.browserscan.net/bot-detection')
page.status == 200  # -> True
```

هذه أيضًا بعض القدرات فقط. اقرأ [هذه الصفحة](fetching/stealthy.md) لكل التفاصيل والقائمة الكاملة للخيارات.

---

هذه نظرة سريعة على Scrapling. تابع إلى القسم التالي لمعرفة المزيد.
