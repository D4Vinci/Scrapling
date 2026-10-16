---
title: "جرّب استخراج بيانات الويب في بيئة Scrapling التفاعلية"
description: "اجلب الصفحات وجرّب المحددات وافحص النتائج في بيئة IPython. حوّل أوامر curl، وأعد استخدام الاستجابات الأخيرة، واختبر كود استخراج البيانات."
---

# دليل بيئة Scrapling التفاعلية {#scrapling-interactive-shell-guide}

<script src="https://asciinema.org/a/736339.js" id="asciicast-736339" async data-autoplay="1" data-loop="1" data-cols="225" data-rows="40" data-start-at="00:06" data-speed="1.5" data-theme="tango"></script>

**بيئة REPL قوية لاستخراج بيانات الويب للمطورين وعلماء البيانات**

بيئة Scrapling التفاعلية مبنية على IPython ومطوّرة خصيصًا لمهام استخراج بيانات الويب. تتيح الوصول الفوري إلى كل ميزات Scrapling، واختصارات مفيدة، وإدارة تلقائية للصفحات، وأدوات متقدمة مثل تحويل أوامر curl.

!!! success "قبل البدء"

    1. اقرأ صفحة [أساسيات أدوات الجلب](../fetching/choosing.md) لتفهم [كائن Response](../fetching/choosing.md#response-object) وتعرف أداة الجلب المناسبة.
    2. اقرأ صفحة [البحث عن العناصر](../parsing/selection.md) لتعرف كيفية العثور على العناصر واستخراجها من كائن [Selector](../parsing/main_classes.md#selector) أو [Response](../fetching/choosing.md#response-object).
    3. اقرأ صفحة [الأصناف الرئيسية](../parsing/main_classes.md) لتعرف الخصائص والدوال التي يرثها [Response](../fetching/choosing.md#response-object) من [Selector](../parsing/main_classes.md#selector).
    4. اقرأ صفحة واحدة على الأقل من قسم أدوات الجلب لاستخدامها هنا: [طلبات HTTP](../fetching/static.md) أو [الجلب بالمتصفح](../fetching/stealthy.md).

## لماذا تستخدم البيئة التفاعلية؟ {#why-use-the-interactive-shell}

تحوّل البيئة التفاعلية استخراج البيانات من دورة بطيئة لكتابة السكربت وتشغيله إلى تجربة سريعة للاستكشاف. وهي مناسبة لـ:

- **إنشاء نماذج أولية بسرعة**: جرّب طرق استخراج البيانات فورًا.
- **استكشاف البيانات**: تنقّل في المواقع واستخرج البيانات بشكل تفاعلي.
- **تعلّم Scrapling**: جرّب الميزات وشاهد النتائج فورًا.
- **تصحيح أدوات الاستخراج**: نفّذ الطلبات خطوة بخطوة وافحص النتائج.
- **تحويل طريقة العمل**: حوّل أمر curl من أدوات المطور في المتصفح إلى طلب Fetcher في سطر واحد.

## البدء {#getting-started}

### تشغيل البيئة التفاعلية {#launch-the-shell}

```bash
# Start the interactive shell
scrapling shell

# Execute code and exit (useful for scripting)
scrapling shell -c "get('https://quotes.toscrape.com'); print(len(page.css('.quote')))"

# Set logging level
scrapling shell --loglevel info
```

بعد التشغيل، تظهر لافتة Scrapling ويمكنك البدء مباشرة، كما يوضح الفيديو أعلاه:

```python
# No imports needed - everything is ready!
get('https://news.ycombinator.com')

# Explore the page structure
page.css('a')[:5]  # Look at first 5 links

# Refine your selectors
stories = page.css('.titleline>a')
len(stories)  # 30

# Extract specific data
for story in stories[:3]:
    title = story.text
    url = story['href']
    print(f"{title}: {url}")

# Try different approaches
titles = page.css('.titleline>a::text')  # Direct text extraction
urls = page.css('.titleline>a::attr(href)')  # Direct attribute extraction
```

## الاختصارات المدمجة {#built-in-shortcuts}

توفر البيئة اختصارات مريحة لتقليل الكود المتكرر:

- **`get(url, **kwargs)`**: طلب HTTP GET بدلًا من `Fetcher.get`.
- **`post(url, **kwargs)`**: طلب HTTP POST بدلًا من `Fetcher.post`.
- **`put(url, **kwargs)`**: طلب HTTP PUT بدلًا من `Fetcher.put`.
- **`delete(url, **kwargs)`**: طلب HTTP DELETE بدلًا من `Fetcher.delete`.
- **`fetch(url, **kwargs)`**: جلب بمتصفح Stealthy بدلًا من `StealthyFetcher.fetch`.

تتوفر الأصناف الأكثر استخدامًا تلقائيًا دون استيراد، ومنها `Fetcher` و`AsyncFetcher` و`StealthyFetcher` و`Selector`.

### إدارة الصفحات تلقائيًا {#smart-page-management}

تتابع البيئة طلباتك وصفحاتك تلقائيًا:

- **الوصول إلى الصفحة الحالية**

    تُحدّث قيمتا `page` و`response` تلقائيًا لتشيرا إلى آخر صفحة جُلبت:

    ```python
    get('https://quotes.toscrape.com')
    # 'page' and 'response' both refer to the last fetched page
    page.url  # 'https://quotes.toscrape.com'
    response.status  # Prints 200; Same as page.status
    ```

- **سجل الصفحات**

    تحتفظ `pages` بآخر خمس صفحات، وهي كائن من نوع `Selectors`:

    ```python
    get('https://site1.com')
    get('https://site2.com')
    get('https://site3.com')
    
    # Access last 5 pages
    len(pages)  # `Selectors` object with `page` history -> 3
    pages[0].url  # First page in history -> 'https://site1.com'
    pages[-1].url  # Most recent page -> 'https://site3.com'
    
    # Work with historical pages
    for i, old_page in enumerate(pages):
        print(f"Page {i}: {old_page.url} - {old_page.status}")
    ```

## أوامر مفيدة أخرى {#additional-helpful-commands}

### عرض الصفحة {#page-visualization}

اعرض الصفحات التي جلبتها داخل المتصفح:

```python
get('https://quotes.toscrape.com')
view(page)  # Opens the page HTML in your default browser
```

### التكامل مع أوامر curl {#curl-command-integration}

توفر البيئة دالتين لتحويل أوامر curl من أدوات المطور في المتصفح إلى طلبات `Fetcher`: وهما `uncurl` و`curl2fetcher`.

أولًا، انسخ طلبًا على هيئة أمر curl كما يلي:

<img src="../assets/scrapling_shell_curl.png" title="نسخ طلب من Chrome على هيئة أمر curl" alt="نسخ طلب من Chrome على هيئة أمر curl" style="width: 70%;"/>

- **تحويل أمر curl إلى كائن Request**

    ```python
    curl_cmd = '''curl 'https://scrapling.requestcatcher.com/post' \
      -X POST \
      -H 'Content-Type: application/json' \
      -d '{"name": "test", "value": 123}' '''
    
    request = uncurl(curl_cmd)
    request.method  # -> 'post'
    request.url  # -> 'https://scrapling.requestcatcher.com/post'
    request.headers  # -> {'Content-Type': 'application/json'}
    ```

- **تنفيذ أمر curl مباشرة**

    ```python
    # Convert and execute in one step
    curl2fetcher(curl_cmd)
    page.status  # -> 200
    ```

### ميزات IPython {#ipython-features}

ترث البيئة كل قدرات IPython:

```python
# Magic commands
%time page = get('https://example.com')  # Time execution
%history  # Show command history
%save filename.py 1-10  # Save commands 1-10 to file

# Tab completion works everywhere
page.c<TAB>  # Shows: css, cookies, headers, etc.
Fetcher.<TAB>  # Shows all Fetcher methods

# Object inspection
get? # Show get documentation
```

## أمثلة {#examples}

إليك بعض الأمثلة التي أنشأها الذكاء الاصطناعي:

#### جمع بيانات المتاجر الإلكترونية {#e-commerce-data-collection}

```python
# Start with product listing page
catalog = get('https://shop.example.com/products')

# Find product links
product_links = catalog.css('.product-link::attr(href)').getall()
print(f"Found {len(product_links)} products")

# Sample a few products first
for link in product_links[:3]:
    product = get(catalog.urljoin(link))
    name = product.css('.product-name::text').get('')
    price = product.css('.price::text').get('')
    print(f"{name}: {price}")

# Scale up with sessions for efficiency
from scrapling.fetchers import FetcherSession
with FetcherSession() as session:
    products = []
    for link in product_links:
        product = session.get(catalog.urljoin(link))
        products.append({
            'name': product.css('.product-name::text').get(''),
            'price': product.css('.price::text').get(''),
            'url': link
        })
```

#### التكامل مع API واختبارها {#api-integration-and-testing}

```python
>>> # Test API endpoints interactively
>>> response = get('https://jsonplaceholder.typicode.com/posts/1')
>>> response.json()
{'userId': 1, 'id': 1, 'title': 'sunt aut...', 'body': 'quia et...'}

>>> # Test POST requests
>>> new_post = post('https://jsonplaceholder.typicode.com/posts', 
...                 json={'title': 'Test Post', 'body': 'Test content', 'userId': 1})
>>> new_post.json()['id']
101

>>> # Test with different data
>>> updated = put('https://jsonplaceholder.typicode.com/posts/1',
...               json={'title': 'Updated Title'})
```

## الحصول على المساعدة {#getting-help}

إذا احتجت إلى مساعدة إضافية غير الموجودة في الطرفية، يمكنك الرجوع إلى:

- [توثيق Scrapling](../index.md)
- [مجتمع Discord](https://discord.gg/EMgGbDceNQ)
- [بلاغات GitHub](https://github.com/D4Vinci/Scrapling/issues)

هذا كل شيء! نتمنى لك تجربة موفقة. تجعل البيئة التفاعلية استخراج بيانات الويب سهلًا مثل المحادثة.
