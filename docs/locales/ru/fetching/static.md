---
title: "Сбор данных по HTTP в Python с Fetcher и FetcherSession"
description: "Отправляйте синхронные и асинхронные HTTP-запросы с имитацией браузера, cookie, прокси и повторным использованием сессий. Извлекайте данные из ответа с Scrapling."
---

# HTTP-запросы {#http-requests}

Класс `Fetcher` отправляет быстрые HTTP-запросы с небольшими затратами ресурсов. Он использует высокопроизводительную библиотеку `curl_cffi` и предоставляет много возможностей для скрытной работы.

!!! success "Перед началом"

    1. Прочитайте [Основы работы с Fetcher](../fetching/choosing.md), чтобы понять, что такое [объект Response](../fetching/choosing.md#response-object) и какой Fetcher выбрать.
    2. Прочитайте [Поиск элементов](../parsing/selection.md), чтобы понять, как находить и извлекать элементы из [Selector](../parsing/main_classes.md#selector)/[Response](../fetching/choosing.md#response-object).
    3. Прочитайте [Основные классы](../parsing/main_classes.md), чтобы узнать, какие свойства и методы [Response](../fetching/choosing.md#response-object) наследует от [Selector](../parsing/main_classes.md#selector).

## Основы использования {#basic-usage}
Основной способ импорта этого Fetcher такой же, как и для остальных:

```python
from scrapling.fetchers import Fetcher
```
О настройке парсера читайте [здесь](choosing.md#parser-configuration-in-all-fetchers).

### Общие аргументы {#shared-arguments}
У всех методов отправки запросов есть общие аргументы. Начнём с них.

- **url**: URL назначения.
- **stealthy_headers**: при включении (по умолчанию) создаёт и добавляет заголовки настоящего браузера, а также заголовок Referer для Google.
- **follow_redirects**: управляет перенаправлениями. **По умолчанию `"safe"`**: перенаправления разрешены, но переходы на внутренние и частные IP-адреса отклоняются для защиты от SSRF. `True` разрешает все перенаправления без ограничений, а `False` полностью их отключает.
- **timeout**: время ожидания завершения каждого запроса в секундах. **По умолчанию 30 секунд**.
- **retries**: максимальное число попыток при ошибках запроса, включая первую попытку. **По умолчанию 3**.
- **retry_delay**: пауза между повторными попытками в секундах. **По умолчанию 1 секунда**.
- **impersonate**: имитирует TLS-отпечатки браузеров. Принимает имя браузера или список имён. Значения вроде `"chrome110"`, `"firefox102"`, `"safari15_5"` выбирают конкретные версии, а `"chrome"`, `"firefox"`, `"safari"`, `"edge"` выбирают последние доступные версии. На уровне TLS запрос выглядит как запрос настоящего браузера. Если передан список, для каждого запроса случайно выбирается один браузер. **По умолчанию используется последняя доступная версия Chrome.**
- **http3**: использует HTTP/3. **По умолчанию False**. При совместном использовании с `impersonate` возможны проблемы.
- **cookies**: cookie для запроса. Можно передать словарь `name→value` или список словарей.
- **proxy**: прокси, через который идёт весь HTTP- и HTTPS-трафик запроса. Формат: `http://username:password@localhost:8030`.
- **proxy_auth**: HTTP Basic-аутентификация для прокси, кортеж (username, password).
- **proxies**: словарь прокси в формате `{"http": proxy_url, "https": proxy_url}`.
- **proxy_rotator**: экземпляр `ProxyRotator` для автоматической смены прокси. Нельзя использовать вместе с `proxy` или `proxies`.
- **headers**: заголовки запроса. Могут переопределить любой заголовок, созданный через `stealthy_headers`.
- **max_redirects**: максимальное число перенаправлений. **По умолчанию 30**. Значение -1 убирает ограничение.
- **verify**: проверять ли сертификаты HTTPS. **По умолчанию True**.
- **cert**: кортеж имён файлов (cert, key) для клиентского сертификата.
- **selector_config**: словарь настроек парсера для создания итогового объекта `Selector`/`Response`.

!!! note "Примечания"

    1. Сейчас доступны следующие браузеры для имитации: `"edge"`, `"chrome"`, `"chrome_android"`, `"safari"`, `"safari_beta"`, `"safari_ios"`, `"safari_ios_beta"`, `"firefox"`, `"tor"`.<br/>
    2. Браузеры и их версии показываются в автодополнении аргументов и обновляются вместе с `curl_cffi`.<br/>
    3. Если включён `impersonate` или `stealthy_headers`, Fetcher автоматически создаёт заголовки настоящего браузера, соответствующие выбранной версии.

Для более тонкой настройки можно передать любому методу дополнительные аргументы, которые поддерживает `curl_cffi` и которые ещё не обрабатывает сам метод.

### Кодировка текста {#text-encoding}

Если на странице не в UTF-8 текст отображается неправильно, передайте в запросе `default_encoding="shift_jis"` или нужную кодировку страницы. Это задаёт запасную кодировку на случай, если в `Content-Type` нет charset. Кодировка, указанная сервером, не переопределяется.

Если сервер указал неверную кодировку, задайте правильную принудительно через `selector_config={"encoding": "shift_jis"}`.

### HTTP-методы {#http-methods}
У каждого метода есть свои дополнительные аргументы, например `params` для GET и `data`/`json` для POST/PUT/DELETE.

Лучше всего это видно на примерах:

> Методы `OPTIONS` и `HEAD` не поддерживаются.
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
Для асинхронных запросов достаточно небольшого изменения:
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
Во всех случаях `page` является объектом [Response](choosing.md#response-object), основанным на [Selector](../parsing/main_classes.md#selector). Его можно сразу использовать для разбора:
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
Для асинхронных запросов достаточно небольшого изменения:
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
Для асинхронных запросов достаточно небольшого изменения:
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
Для асинхронных запросов достаточно небольшого изменения:
```python
from scrapling.fetchers import AsyncFetcher
page = await AsyncFetcher.delete('https://example.com/resource/123')
page = await AsyncFetcher.delete('https://example.com/resource/123', stealthy_headers=True, impersonate="chrome")
page = await AsyncFetcher.delete('https://example.com/resource/123', proxy='http://username:password@localhost:8030')
```

## Управление сессиями {#session-management}

Для нескольких запросов с общими настройками используйте `FetcherSession`. Этот класс работает и в синхронном, и в асинхронном коде. Он сам определяет тип сессии, поэтому менять импорт не нужно.

`FetcherSession` принимает почти все аргументы методов запросов. Можно задать настройки всей сессии, а затем легко изменить их для отдельного запроса, как в примерах ниже.

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

Для автоматической смены прокси между запросами используйте `ProxyRotator` вместе с `FetcherSession`:

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

Для отдельного запроса можно переопределить прокси сессии или механизм его смены, передав `proxy=` прямо в метод запроса:

```python
with FetcherSession(proxy='http://default-proxy:8080') as session:
    # Uses the session proxy
    page1 = session.get('https://example.com/page1')

    # Override the proxy for this specific request
    page2 = session.get('https://example.com/page2', proxy='http://special-proxy:9090')
```

Пример для асинхронного кода:

```python
async with FetcherSession(impersonate='firefox', http3=True) as session:
    # All standard HTTP methods available
    response = await session.get('https://example.com')
    response = await session.post('https://scrapling.requestcatcher.com/post', json={'data': 'value'})
    response = await session.put('https://scrapling.requestcatcher.com/put', data={'update': 'info'})
    response = await session.delete('https://scrapling.requestcatcher.com/delete')
```
Или более удобный вариант:
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

Класс `Fetcher` использует `FetcherSession` для создания временной сессии при каждом запросе.

### Преимущества сессий {#session-benefits}

- **Выше скорость**: в 10 раз быстрее, чем создавать отдельную сессию для каждого запроса.
- **Сохранение cookie**: автоматическая обработка cookie между запросами.
- **Экономия ресурсов**: меньше затрат памяти и процессора при нескольких запросах.
- **Общие настройки**: все настройки запросов в одном месте.

## Примеры {#examples}
Несколько полных примеров для тех, кто только начинает собирать данные с сайтов.

### Простой HTTP-запрос {#basic-http-request}

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

### Сбор данных о товарах {#product-scraping}

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

### Скачивание файлов {#downloading-files}

```python
from scrapling.fetchers import Fetcher

page = Fetcher.get('https://raw.githubusercontent.com/D4Vinci/Scrapling/main/docs/assets/main_cover.png')
with open(file='main_cover.png', mode='wb') as f:
   f.write(page.body)
```

### Переход по страницам {#pagination-handling}

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

### Отправка формы {#form-submission}

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

### Извлечение таблицы {#table-extraction}

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

### Меню навигации {#navigation-menu}

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

## Когда использовать {#when-to-use}

Используйте `Fetcher`, если:

- Нужны быстрые HTTP-запросы.
- Важны небольшие затраты ресурсов.
- Не требуется выполнение JavaScript: данные можно получить обычными запросами.
- Нужны некоторые средства скрытной работы. Например, на сайте есть защита, но нет проверок через JavaScript.

Используйте `FetcherSession`, если:

- Отправляете несколько запросов на один или разные сайты.
- Нужно сохранять cookie и авторизацию между запросами.
- Хотите повторно использовать соединения для повышения скорости.
- Нужны одинаковые настройки для нескольких запросов.
- Работаете с API, которое требует сохранения состояния сессии.

Используйте другие Fetcher, если:

- Нужна автоматизация браузера.
- Нужны расширенные средства обхода защиты от ботов и скрытной работы.
- Нужно выполнять JavaScript или взаимодействовать с динамическим содержимым.
