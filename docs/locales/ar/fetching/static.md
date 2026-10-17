---
title: "جمع البيانات عبر HTTP في Python باستخدام Fetcher وFetcherSession"
description: "أرسل طلبات HTTP متزامنة أو غير متزامنة مع محاكاة المتصفحات وملفات تعريف الارتباط والبروكسي والجلسات القابلة لإعادة الاستخدام، واستخرج البيانات من الرد باستخدام Scrapling."
---

# طلبات HTTP {#http-requests}

توفر فئة `Fetcher` طلبات HTTP سريعة وخفيفة باستخدام مكتبة `curl_cffi` عالية الأداء، مع كثير من ميزات التخفي.

!!! success "قبل البدء"

    1. اقرأ [أساسيات أدوات الجلب](../fetching/choosing.md) لتفهم [كائن Response](../fetching/choosing.md#response-object) وتختار أداة الجلب المناسبة.
    2. اقرأ [البحث عن العناصر](../parsing/selection.md) لتعرف كيف تجد العناصر وتستخرجها من كائن [Selector](../parsing/main_classes.md#selector) أو [Response](../fetching/choosing.md#response-object).
    3. اقرأ [الفئات الأساسية](../parsing/main_classes.md) لتعرف الخصائص والدوال التي ترثها [Response](../fetching/choosing.md#response-object) من [Selector](../parsing/main_classes.md#selector).

## الاستخدام الأساسي {#basic-usage}
هذه طريقة الاستيراد الأساسية، وهي نفسها لكل أدوات الجلب:

```python
from scrapling.fetchers import Fetcher
```
تعرّف على إعداد خيارات التحليل [هنا](choosing.md#parser-configuration-in-all-fetchers).

### الخيارات المشتركة {#shared-arguments}
تشترك كل دوال إرسال الطلبات هنا في بعض الخيارات، فلنشرحها أولًا.

- **url**: الرابط المطلوب.
- **stealthy_headers**: ينشئ ترويسات متصفح حقيقية ويضيفها عند تفعيله، وهو مفعّل افتراضيًا. يضيف أيضًا ترويسة referer من Google.
- **follow_redirects**: يتحكم في إعادة التوجيه. **القيمة الافتراضية `"safe"`** تتبع إعادة التوجيه، لكنها ترفض الوجهات ذات عناوين IP الداخلية أو الخاصة للحماية من SSRF. استخدم `True` لتتبعها بلا قيود، أو `False` لتعطيلها تمامًا.
- **timeout**: أقصى مدة انتظار اكتمال كل طلب بالثواني. **القيمة الافتراضية 30 ثانية**.
- **retries**: أقصى عدد لمحاولات الطلب الفاشل، بما فيها المحاولة الأولى. **القيمة الافتراضية 3**.
- **retry_delay**: مدة الانتظار بالثواني بين المحاولات. **القيمة الافتراضية ثانية واحدة**.
- **impersonate**: يحاكي بصمات TLS لمتصفحات محددة. يقبل اسم متصفح أو قائمة أسماء، مثل `"chrome110"` أو `"firefox102"` أو `"safari15_5"` لإصدارات محددة، أو `"chrome"` و`"firefox"` و`"safari"` و`"edge"` لاستخدام أحدث إصدار متاح تلقائيًا. تبدو الطلبات بذلك كطلبات متصفح حقيقي على مستوى TLS. عند تمرير قائمة، يختار اسمًا عشوائيًا لكل طلب. **الافتراضي هو أحدث إصدار Chrome متاح.**
- **http3**: يستخدم HTTP/3 للطلبات. **القيمة الافتراضية False**. قد يسبب مشكلات عند استخدامه مع `impersonate`.
- **cookies**: ملفات تعريف الارتباط المستخدمة في الطلب. يقبل قاموسًا من `name→value` أو قائمة قواميس.
- **proxy**: البروكسي الذي تمر عبره حركة HTTP وHTTPS لهذا الطلب. الصيغة المقبولة هي `http://username:password@localhost:8030`.
- **proxy_auth**: بيانات HTTP Basic Auth للبروكسي، كزوج من اسم المستخدم وكلمة المرور.
- **proxies**: قاموس البروكسيات بالصيغة `{"http": proxy_url, "https": proxy_url}`.
- **proxy_rotator**: كائن `ProxyRotator` لتبديل البروكسي تلقائيًا. لا يمكن جمعه مع `proxy` أو `proxies`.
- **headers**: ترويسات إضافية للطلب. يمكنها استبدال أي ترويسة ينشئها `stealthy_headers`.
- **max_redirects**: أقصى عدد لعمليات إعادة التوجيه. **القيمة الافتراضية 30**. استخدم -1 لإزالة الحد.
- **verify**: هل تُفحص شهادات HTTPS؟ **القيمة الافتراضية True**.
- **cert**: زوج من اسمَي ملف الشهادة والمفتاح لشهادة العميل.
- **selector_config**: قاموس خيارات تحليل مخصصة يُستخدم عند إنشاء كائن `Selector` أو `Response` النهائي.

!!! note "ملاحظات:"

    1. المتصفحات المتاحة حاليًا للمحاكاة هي (`"edge"`, `"chrome"`, `"chrome_android"`, `"safari"`, `"safari_beta"`, `"safari_ios"`, `"safari_ios_beta"`, `"firefox"`, `"tor"`).<br/>
    2. تظهر المتصفحات المتاحة وإصداراتها تلقائيًا في الإكمال التلقائي للخيارات، وتتحدث مع كل تحديث لـ`curl_cffi`.<br/>
    3. عند تفعيل `impersonate` أو `stealthy_headers`، تنشئ أدوات الجلب تلقائيًا ترويسات حقيقية تطابق إصدار المتصفح المستخدم.

للمزيد من التخصيص، يمكنك تمرير أي خيار تدعمه `curl_cffi` إلى أي دالة لا تدعمه بالفعل.

### ترميز النص {#text-encoding}

إذا ظهر النص مشوّهًا في صفحة لا تستخدم UTF-8، مرّر `default_encoding="shift_jis"`، أو ترميز الصفحة، مع الطلب. يحدد هذا الترميز البديل عندما لا تحتوي ترويسة `Content-Type` على charset. ولا يستبدل ترميزًا حدده الخادم.

إذا أرسل الخادم charset غير صحيح، افرض الترميز الصحيح باستخدام `selector_config={"encoding": "shift_jis"}`.

### طرق HTTP {#http-methods}
توجد خيارات إضافية حسب طريقة الطلب، مثل `params` لطلبات GET، و`data` أو `json` لطلبات POST وPUT وDELETE.

الأمثلة أفضل طريقة للتوضيح:

> ملاحظة: الطريقتان `OPTIONS` و`HEAD` غير مدعومتين.
#### GET {#get}
```python
from scrapling.fetchers import Fetcher
# Basic GET
page = Fetcher.get('https://example.com')
page = Fetcher.get('https://scrapling.requestcatcher.com/get', stealthy_headers=True)
page = Fetcher.get('https://scrapling.requestcatcher.com/get', proxy='http://username:password@localhost:8030')
# With parameters
page = Fetcher.get('https://example.com/search', params={'q': 'query'})

# With headers
page = Fetcher.get('https://example.com', headers={'User-Agent': 'Custom/1.0'})
# Basic HTTP authentication
page = Fetcher.get("https://example.com", auth=("my_user", "password123"))
# Browser impersonation
page = Fetcher.get('https://example.com', impersonate='chrome')
# HTTP/3 support
page = Fetcher.get('https://example.com', http3=True)
```
للطلبات غير المتزامنة، يكفي تعديل بسيط:
```python
from scrapling.fetchers import AsyncFetcher
# Basic GET
page = await AsyncFetcher.get('https://example.com')
page = await AsyncFetcher.get('https://scrapling.requestcatcher.com/get', stealthy_headers=True)
page = await AsyncFetcher.get('https://scrapling.requestcatcher.com/get', proxy='http://username:password@localhost:8030')
# With parameters
page = await AsyncFetcher.get('https://example.com/search', params={'q': 'query'})
# With headers
page = await AsyncFetcher.get('https://example.com', headers={'User-Agent': 'Custom/1.0'})
# Basic HTTP authentication
page = await AsyncFetcher.get("https://example.com", auth=("my_user", "password123"))
# Browser impersonation
page = await AsyncFetcher.get('https://example.com', impersonate='chrome110')
# HTTP/3 support
page = await AsyncFetcher.get('https://example.com', http3=True)
```
في كل الحالات، يكون `page` كائن [Response](choosing.md#response-object)، وهو أيضًا [Selector](../parsing/main_classes.md#selector) كما ذكرنا، لذلك يمكنك استخدامه مباشرة:
```python
page.css('.something.something')

page = Fetcher.get('https://api.github.com/events')
>>> page.json()
[{'id': '<redacted>',
  'type': 'PushEvent',
  'actor': {'id': '<redacted>',
   'login': '<redacted>',
   'display_login': '<redacted>',
   'gravatar_id': '',
   'url': 'https://api.github.com/users/<redacted>',
   'avatar_url': 'https://avatars.githubusercontent.com/u/<redacted>'},
  'repo': {'id': '<redacted>',
...
```
#### POST {#post}
```python
from scrapling.fetchers import Fetcher
# Basic POST
page = Fetcher.post('https://scrapling.requestcatcher.com/post', data={'key': 'value'}, params={'q': 'query'})
page = Fetcher.post('https://scrapling.requestcatcher.com/post', data={'key': 'value'}, stealthy_headers=True)
page = Fetcher.post('https://scrapling.requestcatcher.com/post', data={'key': 'value'}, proxy='http://username:password@localhost:8030', impersonate="chrome")
# Another example of form-encoded data
page = Fetcher.post('https://example.com/submit', data={'username': 'user', 'password': 'pass'}, http3=True)
# JSON data
page = Fetcher.post('https://example.com/api', json={'key': 'value'})
```
للطلبات غير المتزامنة، يكفي تعديل بسيط:
```python
from scrapling.fetchers import AsyncFetcher
# Basic POST
page = await AsyncFetcher.post('https://scrapling.requestcatcher.com/post', data={'key': 'value'})
page = await AsyncFetcher.post('https://scrapling.requestcatcher.com/post', data={'key': 'value'}, stealthy_headers=True)
page = await AsyncFetcher.post('https://scrapling.requestcatcher.com/post', data={'key': 'value'}, proxy='http://username:password@localhost:8030', impersonate="chrome")
# Another example of form-encoded data
page = await AsyncFetcher.post('https://example.com/submit', data={'username': 'user', 'password': 'pass'}, http3=True)
# JSON data
page = await AsyncFetcher.post('https://example.com/api', json={'key': 'value'})
```
#### PUT {#put}
```python
from scrapling.fetchers import Fetcher
# Basic PUT
page = Fetcher.put('https://example.com/update', data={'status': 'updated'})
page = Fetcher.put('https://example.com/update', data={'status': 'updated'}, stealthy_headers=True, impersonate="chrome")
page = Fetcher.put('https://example.com/update', data={'status': 'updated'}, proxy='http://username:password@localhost:8030')
# Another example of form-encoded data
page = Fetcher.put("https://scrapling.requestcatcher.com/put", data={'key': ['value1', 'value2']})
```
للطلبات غير المتزامنة، يكفي تعديل بسيط:
```python
from scrapling.fetchers import AsyncFetcher
# Basic PUT
page = await AsyncFetcher.put('https://example.com/update', data={'status': 'updated'})
page = await AsyncFetcher.put('https://example.com/update', data={'status': 'updated'}, stealthy_headers=True, impersonate="chrome")
page = await AsyncFetcher.put('https://example.com/update', data={'status': 'updated'}, proxy='http://username:password@localhost:8030')
# Another example of form-encoded data
page = await AsyncFetcher.put("https://scrapling.requestcatcher.com/put", data={'key': ['value1', 'value2']})
```

#### DELETE {#delete}
```python
from scrapling.fetchers import Fetcher
page = Fetcher.delete('https://example.com/resource/123')
page = Fetcher.delete('https://example.com/resource/123', stealthy_headers=True, impersonate="chrome")
page = Fetcher.delete('https://example.com/resource/123', proxy='http://username:password@localhost:8030')
```
للطلبات غير المتزامنة، يكفي تعديل بسيط:
```python
from scrapling.fetchers import AsyncFetcher
page = await AsyncFetcher.delete('https://example.com/resource/123')
page = await AsyncFetcher.delete('https://example.com/resource/123', stealthy_headers=True, impersonate="chrome")
page = await AsyncFetcher.delete('https://example.com/resource/123', proxy='http://username:password@localhost:8030')
```

## إدارة الجلسات {#session-management}

لإرسال عدة طلبات بالإعدادات نفسها، استخدم `FetcherSession`. تعمل الفئة مع الكود المتزامن وغير المتزامن، وتحدد نوع الجلسة وتغيره تلقائيًا دون الحاجة إلى استيراد مختلف.

تقبل `FetcherSession` معظم خيارات دوال الطلبات. يمكنك تحديد إعدادات للجلسة كلها، ثم تغييرها لطلب معين بسهولة، كما في الأمثلة التالية.

```python
from scrapling.fetchers import FetcherSession

# Create a session with default configuration
with FetcherSession(
    impersonate='chrome',
    http3=True,
    stealthy_headers=True,
    timeout=30,
    retries=3
) as session:
    # Make multiple requests with the same settings and the same cookies
    page1 = session.get('https://scrapling.requestcatcher.com/get')
    page2 = session.post('https://scrapling.requestcatcher.com/post', data={'key': 'value'})
    page3 = session.get('https://api.github.com/events')

    # All requests share the same session and connection pool
```

يمكنك أيضًا استخدام `ProxyRotator` مع `FetcherSession` لتبديل البروكسي تلقائيًا بين الطلبات:

```python
from scrapling.fetchers import FetcherSession, ProxyRotator

rotator = ProxyRotator([
    'http://proxy1:8080',
    'http://proxy2:8080',
    'http://proxy3:8080',
])

with FetcherSession(proxy_rotator=rotator, impersonate='chrome') as session:
    # Each request automatically uses the next proxy in rotation
    page1 = session.get('https://example.com/page1')
    page2 = session.get('https://example.com/page2')

    # You can check which proxy was used via the response metadata
    print(page1.meta['proxy'])
```

ويمكنك استبدال بروكسي الجلسة أو أداة التبديل لطلب معين بتمرير `proxy=` مباشرة إلى دالة الطلب:

```python
with FetcherSession(proxy='http://default-proxy:8080') as session:
    # Uses the session proxy
    page1 = session.get('https://example.com/page1')

    # Override the proxy for this specific request
    page2 = session.get('https://example.com/page2', proxy='http://special-proxy:9090')
```

وهذا مثال غير متزامن:

```python
async with FetcherSession(impersonate='firefox', http3=True) as session:
    # All standard HTTP methods available
    response = await session.get('https://example.com')
    response = await session.post('https://scrapling.requestcatcher.com/post', json={'data': 'value'})
    response = await session.put('https://scrapling.requestcatcher.com/put', data={'update': 'info'})
    response = await session.delete('https://scrapling.requestcatcher.com/delete')
```
أو بشكل أفضل:
```python
import asyncio
from scrapling.fetchers import FetcherSession

# Async session usage
async with FetcherSession(impersonate="safari") as session:
    urls = ['https://example.com/page1', 'https://example.com/page2']

    tasks = [
        session.get(url) for url in urls
    ]

    pages = await asyncio.gather(*tasks)
```

تستخدم فئة `Fetcher` فئة `FetcherSession` لإنشاء جلسة مؤقتة لكل طلب.

### فوائد الجلسات {#session-benefits}

- **سرعة أكبر**: أسرع بعشر مرات من إنشاء جلسة مستقلة لكل طلب.
- **الاحتفاظ بملفات تعريف الارتباط**: إدارة تلقائية لها بين الطلبات.
- **استخدام أفضل للموارد**: تقليل استهلاك الذاكرة والمعالج عند إرسال عدة طلبات.
- **إعدادات مركزية**: مكان واحد لإدارة إعدادات الطلبات.

## أمثلة {#examples}
أمثلة متكاملة لمساعدة من يبدأ في جمع بيانات الويب.

### طلب HTTP بسيط {#basic-http-request}

```python
from scrapling.fetchers import Fetcher

# Make a request
page = Fetcher.get('https://example.com')

# Check the status
if page.status == 200:
    # Extract title
    title = page.css('title::text').get()
    print(f"Page title: {title}")

    # Extract all links
    links = page.css('a::attr(href)').getall()
    print(f"Found {len(links)} links")
```

### جمع بيانات المنتجات {#product-scraping}

```python
from scrapling.fetchers import Fetcher

def scrape_products():
    page = Fetcher.get('https://example.com/products')
    
    # Find all product elements
    products = page.css('.product')
    
    results = []
    for product in products:
        results.append({
            'title': product.css('.title::text').get(),
            'price': product.css('.price::text').re_first(r'\d+\.\d{2}'),
            'description': product.css('.description::text').get(),
            'in_stock': product.has_class('in-stock')
        })
    
    return results
```

### تنزيل الملفات {#downloading-files}

```python
from scrapling.fetchers import Fetcher

page = Fetcher.get('https://raw.githubusercontent.com/D4Vinci/Scrapling/main/docs/assets/main_cover.png')
with open(file='main_cover.png', mode='wb') as f:
   f.write(page.body)
```

### التنقل بين صفحات النتائج {#pagination-handling}

```python
from scrapling.fetchers import Fetcher

def scrape_all_pages():
    base_url = 'https://example.com/products?page={}'
    page_num = 1
    all_products = []
    
    while True:
        # Get current page
        page = Fetcher.get(base_url.format(page_num))
        
        # Find products
        products = page.css('.product')
        if not products:
            break
            
        # Process products
        for product in products:
            all_products.append({
                'name': product.css('.name::text').get(),
                'price': product.css('.price::text').get()
            })
            
        # Next page
        page_num += 1
        
    return all_products
```

### إرسال نموذج {#form-submission}

```python
from scrapling.fetchers import Fetcher

# Submit login form
response = Fetcher.post(
    'https://example.com/login',
    data={
        'username': 'user@example.com',
        'password': 'password123'
    }
)

# Check login success
if response.status == 200:
    # Extract user info
    user_name = response.css('.user-name::text').get()
    print(f"Logged in as: {user_name}")
```

### استخراج جدول {#table-extraction}

```python
from scrapling.fetchers import Fetcher

def extract_table():
    page = Fetcher.get('https://example.com/data')
    
    # Find table
    table = page.css('table')[0]
    
    # Extract headers
    headers = [
        th.text for th in table.css('thead th')
    ]
    
    # Extract rows
    rows = []
    for row in table.css('tbody tr'):
        cells = [td.text for td in row.css('td')]
        rows.append(dict(zip(headers, cells)))
        
    return rows
```

### قائمة التنقل {#navigation-menu}

```python
from scrapling.fetchers import Fetcher

def extract_menu():
    page = Fetcher.get('https://example.com')
    
    # Find navigation
    nav = page.css('nav')[0]
    
    menu = {}
    for item in nav.css('li'):
        links = item.css('a')
        if links:
            link = links[0]
            menu[link.text] = {
                'url': link['href'],
                'has_submenu': bool(item.css('.submenu'))
            }
            
    return menu
```

## متى تستخدم كل أداة؟ {#when-to-use}

استخدم `Fetcher` عندما:

- تحتاج إلى طلبات HTTP سريعة.
- تريد أقل استهلاك إضافي للموارد.
- لا تحتاج إلى تشغيل JavaScript، ويمكن جمع بيانات الموقع بالطلبات فقط.
- تحتاج إلى بعض ميزات التخفي، مثل التعامل مع موقع يستخدم حماية دون اختبارات JavaScript.

استخدم `FetcherSession` عندما:

- ترسل عدة طلبات إلى الموقع نفسه أو مواقع مختلفة.
- تحتاج إلى حفظ ملفات تعريف الارتباط أو المصادقة بين الطلبات.
- تريد إعادة استخدام الاتصالات لتحسين الأداء.
- تحتاج إلى إعدادات ثابتة بين الطلبات.
- تتعامل مع APIs تتطلب الاحتفاظ بحالة الجلسة.

استخدم أدوات جلب أخرى عندما:

- تحتاج إلى أتمتة المتصفح.
- تحتاج إلى ميزات متقدمة للتخفي أو تجاوز كشف البوتات.
- تحتاج إلى تشغيل JavaScript أو التفاعل مع المحتوى الديناميكي.
