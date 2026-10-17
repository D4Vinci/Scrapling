---
title: "使用 Fetcher 和 FetcherSession 进行 Python HTTP 抓取"
description: "发送支持浏览器模拟、Cookie、代理和可复用会话的同步或异步 HTTP 请求，并使用 Scrapling 提取响应数据。"
---

# HTTP 请求 {#http-requests}

`Fetcher` 基于高性能的 `curl_cffi`，提供快速、轻量的 HTTP 请求，以及多种隐身功能。

!!! success "前提条件"

    1. 已阅读 [Fetcher 基础](../fetching/choosing.md)，了解 [Response 对象](../fetching/choosing.md#response-object)，并知道如何选择 Fetcher。
    2. 已阅读[查询元素](../parsing/selection.md)，了解如何从 [Selector](../parsing/main_classes.md#selector)/[Response](../fetching/choosing.md#response-object) 对象中查找和提取元素。
    3. 已阅读[主要类](../parsing/main_classes.md)，了解 [Response](../fetching/choosing.md#response-object) 从 [Selector](../parsing/main_classes.md#selector) 继承的属性和方法。

## 基本用法 {#basic-usage}
这个 Fetcher 的主要导入方式与其他 Fetcher 相同：

```python
from scrapling.fetchers import Fetcher
```
解析选项的配置方法见[这里](choosing.md#parser-configuration-in-all-fetchers)。

### 通用参数 {#shared-arguments}
这些请求方法共有一些参数，先介绍它们。

- **url**：目标 URL。
- **stealthy_headers**：生成并添加真实浏览器请求头，包括 Google referer，默认开启。
- **follow_redirects**：控制重定向。**默认为 `"safe"`**，跟随重定向，但拒绝指向内部或私有 IP 的目标，以防范 SSRF。传入 `True` 可不受限制地跟随所有重定向，传入 `False` 则完全关闭重定向。
- **timeout**：每次请求的最长等待时间，单位为秒。**默认 30 秒**。
- **retries**：失败请求的最大尝试次数，包含首次尝试。**默认 3 次**。
- **retry_delay**：重试之间的等待时间，单位为秒。**默认 1 秒**。
- **impersonate**：模拟指定浏览器的 TLS 指纹。可以传入浏览器字符串或列表，例如 `"chrome110"`、`"firefox102"`、`"safari15_5"` 表示指定版本，`"chrome"`、`"firefox"`、`"safari"`、`"edge"` 则自动使用最新可用版本。这样，请求在 TLS 层面看起来来自真实浏览器。传入列表时，每次请求随机选择一个。**默认使用最新可用的 Chrome 版本。**
- **http3**：使用 HTTP/3 协议发送请求。**默认为 False**。与 `impersonate` 同时使用可能出现问题。
- **cookies**：请求使用的 Cookie，可以是 `name→value` 字典或字典列表。
- **proxy**：此请求使用的代理，所有 HTTP 和 HTTPS 流量都会经过它。格式为 `http://username:password@localhost:8030`。
- **proxy_auth**：代理的 HTTP Basic 认证，格式为 (username, password) 元组。
- **proxies**：代理字典，格式为 `{"http": proxy_url, "https": proxy_url}`。
- **proxy_rotator**：用于自动轮换代理的 `ProxyRotator` 实例，不能与 `proxy` 或 `proxies` 同时使用。
- **headers**：请求中添加的请求头，可以覆盖 `stealthy_headers` 生成的任意请求头。
- **max_redirects**：最大重定向次数。**默认 30 次**，设为 -1 表示不限制。
- **verify**：是否验证 HTTPS 证书。**默认为 True**。
- **cert**：客户端证书和密钥的文件名元组，格式为 (cert, key)。
- **selector_config**：创建最终 `Selector`/`Response` 对象时使用的自定义解析参数字典。

!!! note "注意事项："

    1. 当前可模拟的浏览器有（`"edge"`、`"chrome"`、`"chrome_android"`、`"safari"`、`"safari_beta"`、`"safari_ios"`、`"safari_ios_beta"`、`"firefox"`、`"tor"`）。<br/>
    2. 可用浏览器及其版本会自动显示在参数补全中，并随 `curl_cffi` 更新。<br/>
    3. 启用 `impersonate` 或 `stealthy_headers` 后，Fetcher 会自动生成与所用浏览器版本匹配的真实请求头。

如需进一步自定义，还可以向各方法传入 `curl_cffi` 支持、而该方法尚未直接提供的参数。

### 文本编码 {#text-encoding}

如果非 UTF-8 页面出现乱码，可以随请求传入 `default_encoding="shift_jis"`，或页面实际使用的编码。只有 `Content-Type` 响应头未指定字符集时，才会使用这个后备编码。它不会覆盖服务器提供的字符集。

如果服务器提供了错误的字符集，可用 `selector_config={"encoding": "shift_jis"}` 强制指定正确编码。

### HTTP 方法 {#http-methods}
不同方法还有各自的参数，例如 GET 的 `params`，以及 POST、PUT、DELETE 的 `data`/`json`。

通过例子更容易理解：

> 注意：不支持 `OPTIONS` 和 `HEAD` 方法。
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
异步请求只需稍作调整：
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
这里的 `page` 始终是 [Response](choosing.md#response-object) 对象，也就是一种 [Selector](../parsing/main_classes.md#selector)，因此可以直接解析：
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
异步请求只需稍作调整：
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
异步请求只需稍作调整：
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
异步请求只需稍作调整：
```python
from scrapling.fetchers import AsyncFetcher
page = await AsyncFetcher.delete('https://example.com/resource/123')
page = await AsyncFetcher.delete('https://example.com/resource/123', stealthy_headers=True, impersonate="chrome")
page = await AsyncFetcher.delete('https://example.com/resource/123', proxy='http://username:password@localhost:8030')
```

## 会话管理 {#session-management}

要用相同配置发送多个请求，可以使用 `FetcherSession`。它同时支持同步和异步代码，会自动识别并切换会话类型，不需要导入另一个类。

`FetcherSession` 接受请求方法中的几乎所有参数。可以先为整个会话配置默认值，再轻松覆盖某次请求的设置，如下面的示例所示。

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

也可以给 `FetcherSession` 配置 `ProxyRotator`，在请求之间自动轮换代理：

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

向请求方法直接传入 `proxy=`，可以覆盖这次请求使用的会话代理或轮换器：

```python
with FetcherSession(proxy='http://default-proxy:8080') as session:
    # Uses the session proxy
    page1 = session.get('https://example.com/page1')

    # Override the proxy for this specific request
    page2 = session.get('https://example.com/page2', proxy='http://special-proxy:9090')
```

异步示例：

```python
async with FetcherSession(impersonate='firefox', http3=True) as session:
    # All standard HTTP methods available
    response = await session.get('https://example.com')
    response = await session.post('https://scrapling.requestcatcher.com/post', json={'data': 'value'})
    response = await session.put('https://scrapling.requestcatcher.com/put', data={'update': 'info'})
    response = await session.delete('https://scrapling.requestcatcher.com/delete')
```
更好的写法：
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

`Fetcher` 会通过 `FetcherSession` 为每次请求创建一个临时会话。

### 会话的优点 {#session-benefits}

- **速度更快**：比每次请求都创建会话快 10 倍。
- **保留 Cookie**：自动在请求之间管理 Cookie。
- **节省资源**：多个请求的内存和 CPU 使用更高效。
- **集中配置**：在同一个地方管理请求设置。

## 示例 {#examples}
下面是一些完整示例，帮助初学者开始网页抓取。

### 基本 HTTP 请求 {#basic-http-request}

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

### 抓取产品 {#product-scraping}

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

### 下载文件 {#downloading-files}

```python
from scrapling.fetchers import Fetcher

page = Fetcher.get('https://raw.githubusercontent.com/D4Vinci/Scrapling/main/docs/assets/main_cover.png')
with open(file='main_cover.png', mode='wb') as f:
   f.write(page.body)
```

### 处理分页 {#pagination-handling}

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

### 提交表单 {#form-submission}

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

### 提取表格 {#table-extraction}

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

### 导航菜单 {#navigation-menu}

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

## 适用场景 {#when-to-use}

以下情况适合使用 `Fetcher`：

- 需要快速发送 HTTP 请求。
- 希望尽量减少额外资源开销。
- 不需要执行 JavaScript，通过请求就能抓取网站。
- 需要一些隐身功能，例如网站有防护，但没有 JavaScript 挑战。

以下情况适合使用 `FetcherSession`：

- 对同一网站或不同网站发送多个请求。
- 需要在请求之间保留 Cookie 或认证状态。
- 希望通过连接复用提高性能。
- 需要让多个请求使用一致的配置。
- 使用需要会话状态的 API。

以下情况应使用其他 Fetcher：

- 需要浏览器自动化。
- 需要更高级的反机器人应对或隐身功能。
- 需要执行 JavaScript 或与动态内容交互。
