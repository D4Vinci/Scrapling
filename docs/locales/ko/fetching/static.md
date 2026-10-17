---
title: "Fetcher와 FetcherSession으로 Python에서 HTTP 스크래핑하기"
description: "브라우저 모방, 쿠키, 프록시, 재사용 가능한 세션으로 동기 및 비동기 HTTP 요청을 보내고 Scrapling으로 응답에서 데이터를 추출하세요."
---

# HTTP 요청 {#http-requests}

`Fetcher`는 고성능 라이브러리 `curl_cffi`를 사용해 빠르고 가벼운 HTTP 요청을 보냅니다. 탐지를 피하는 기능도 다양하게 제공합니다.

!!! success "사전 준비"

    1. [Fetcher 기초](../fetching/choosing.md)를 읽고 [Response 객체](../fetching/choosing.md#response-object)와 Fetcher를 고르는 방법을 알아두세요.
    2. [요소 찾기](../parsing/selection.md)를 읽고 [Selector](../parsing/main_classes.md#selector)/[Response](../fetching/choosing.md#response-object)에서 요소를 찾고 추출하는 방법을 알아두세요.
    3. [주요 클래스](../parsing/main_classes.md)를 읽고 [Response](../fetching/choosing.md#response-object)가 [Selector](../parsing/main_classes.md#selector)에서 상속하는 속성과 메서드를 알아두세요.

## 기본 사용법 {#basic-usage}
이 Fetcher를 가져오는 기본 방법은 다른 Fetcher와 같습니다.

```python
from scrapling.fetchers import Fetcher
```
파서 설정 방법은 [여기](choosing.md#parser-configuration-in-all-fetchers)를 참고하세요.

### 공통 인수 {#shared-arguments}
모든 요청 메서드에서 사용하는 공통 인수부터 살펴보겠습니다.

- **url**: 대상 URL입니다.
- **stealthy_headers**: 켜면 실제 브라우저의 헤더를 생성해 추가합니다. Google Referer 헤더도 설정합니다. 기본적으로 켜져 있습니다.
- **follow_redirects**: 리디렉션을 제어합니다. **기본값은 `"safe"`**입니다. 리디렉션을 따르되 내부 또는 사설 IP로 가는 리디렉션은 차단해 SSRF를 방지합니다. `True`는 제한 없이 모두 따르고, `False`는 리디렉션을 모두 끕니다.
- **timeout**: 각 요청의 완료를 기다리는 시간입니다. **기본값은 30초**입니다.
- **retries**: 실패한 요청의 최대 시도 횟수이며 첫 번째 시도도 포함합니다. **기본값은 3**입니다.
- **retry_delay**: 재시도 사이에 기다리는 초 단위 시간입니다. **기본값은 1초**입니다.
- **impersonate**: 특정 브라우저의 TLS 지문을 모방합니다. 브라우저 문자열 또는 문자열 리스트를 받습니다. `"chrome110"`, `"firefox102"`, `"safari15_5"`는 특정 버전을 사용하고, `"chrome"`, `"firefox"`, `"safari"`, `"edge"`는 사용 가능한 최신 버전을 사용합니다. TLS 수준에서 실제 브라우저의 요청처럼 보이게 합니다. 리스트를 전달하면 요청마다 무작위로 하나를 선택합니다. **기본값은 사용 가능한 최신 Chrome 버전입니다.**
- **http3**: HTTP/3을 사용합니다. **기본값은 False**입니다. `impersonate`와 함께 사용하면 문제가 생길 수 있습니다.
- **cookies**: 요청에 사용할 쿠키입니다. `name→value` 딕셔너리 또는 딕셔너리 리스트를 받습니다.
- **proxy**: 요청의 HTTP 및 HTTPS 트래픽을 보낼 프록시입니다. 형식은 `http://username:password@localhost:8030`입니다.
- **proxy_auth**: 프록시의 HTTP Basic 인증입니다. (username, password) 튜플로 전달합니다.
- **proxies**: 사용할 프록시 딕셔너리입니다. 형식은 `{"http": proxy_url, "https": proxy_url}`입니다.
- **proxy_rotator**: 자동 프록시 순환에 사용할 `ProxyRotator` 객체입니다. `proxy` 또는 `proxies`와 함께 사용할 수 없습니다.
- **headers**: 요청에 포함할 헤더입니다. `stealthy_headers`가 생성한 헤더를 덮어쓸 수 있습니다.
- **max_redirects**: 최대 리디렉션 횟수입니다. **기본값은 30**이며, -1은 제한을 없앱니다.
- **verify**: HTTPS 인증서를 검증할지 정합니다. **기본값은 True**입니다.
- **cert**: 클라이언트 인증서 파일 이름의 (cert, key) 튜플입니다.
- **selector_config**: 최종 `Selector`/`Response` 객체를 만들 때 사용할 파서 설정 딕셔너리입니다.

!!! note "참고"

    1. 현재 모방할 수 있는 브라우저는 `"edge"`, `"chrome"`, `"chrome_android"`, `"safari"`, `"safari_beta"`, `"safari_ios"`, `"safari_ios_beta"`, `"firefox"`, `"tor"`입니다.<br/>
    2. 브라우저와 버전 목록은 인수 자동 완성에 표시되며 `curl_cffi`가 업데이트될 때 함께 갱신됩니다.<br/>
    3. `impersonate` 또는 `stealthy_headers`가 켜져 있으면 Fetcher가 해당 브라우저 버전에 맞는 실제 헤더를 자동 생성합니다.

더 세밀하게 설정하려면 각 메서드가 직접 지원하지 않는 인수도 전달할 수 있습니다. `curl_cffi`가 지원하는 인수여야 합니다.

### 텍스트 인코딩 {#text-encoding}

UTF-8이 아닌 페이지에서 글자가 깨지면 요청에 `default_encoding="shift_jis"` 또는 해당 페이지의 인코딩을 전달하세요. `Content-Type`에 charset이 없을 때 사용할 대체 인코딩을 설정합니다. 서버가 지정한 charset을 덮어쓰지는 않습니다.

서버가 잘못된 charset을 보냈다면 `selector_config={"encoding": "shift_jis"}`로 올바른 인코딩을 강제할 수 있습니다.

### HTTP 메서드 {#http-methods}
메서드마다 추가 인수가 있습니다. 예를 들어 GET은 `params`, POST/PUT/DELETE는 `data`/`json`을 받습니다.

예제로 살펴보겠습니다.

> `OPTIONS`와 `HEAD` 메서드는 지원하지 않습니다.
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
비동기 요청에는 조금만 바꾸면 됩니다.
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
모든 경우에 `page`는 [Response](choosing.md#response-object) 객체입니다. [Selector](../parsing/main_classes.md#selector)를 기반으로 하므로 바로 파싱에 사용할 수 있습니다.
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
비동기 요청에는 조금만 바꾸면 됩니다.
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
비동기 요청에는 조금만 바꾸면 됩니다.
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
비동기 요청에는 조금만 바꾸면 됩니다.
```python
from scrapling.fetchers import AsyncFetcher
page = await AsyncFetcher.delete('https://example.com/resource/123')
page = await AsyncFetcher.delete('https://example.com/resource/123', stealthy_headers=True, impersonate="chrome")
page = await AsyncFetcher.delete('https://example.com/resource/123', proxy='http://username:password@localhost:8030')
```

## 세션 관리 {#session-management}

같은 설정으로 여러 요청을 보내려면 `FetcherSession`을 사용하세요. 동기 코드와 비동기 코드 모두에서 사용할 수 있습니다. 클래스가 세션 타입을 자동으로 판단하므로 다른 클래스를 가져올 필요가 없습니다.

`FetcherSession`은 요청 메서드의 인수를 거의 모두 받습니다. 세션 전체의 설정을 지정한 뒤, 특정 요청에서만 다른 설정을 사용할 수 있습니다.

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

`FetcherSession`에 `ProxyRotator`를 사용하면 요청 사이에 프록시를 자동으로 바꿀 수 있습니다.

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

요청 메서드에 `proxy=`를 직접 전달하면 해당 요청에서 세션의 프록시나 순환 설정을 덮어쓸 수 있습니다.

```python
with FetcherSession(proxy='http://default-proxy:8080') as session:
    # Uses the session proxy
    page1 = session.get('https://example.com/page1')

    # Override the proxy for this specific request
    page2 = session.get('https://example.com/page2', proxy='http://special-proxy:9090')
```

비동기 예제입니다.

```python
async with FetcherSession(impersonate='firefox', http3=True) as session:
    # All standard HTTP methods available
    response = await session.get('https://example.com')
    response = await session.post('https://scrapling.requestcatcher.com/post', json={'data': 'value'})
    response = await session.put('https://scrapling.requestcatcher.com/put', data={'update': 'info'})
    response = await session.delete('https://scrapling.requestcatcher.com/delete')
```
더 좋은 방법은 다음과 같습니다.
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

`Fetcher`는 요청마다 `FetcherSession`으로 임시 세션을 만듭니다.

### 세션의 장점 {#session-benefits}

- **더 빠른 속도**: 요청마다 새 세션을 만드는 것보다 10배 빠릅니다.
- **쿠키 유지**: 요청 사이의 쿠키를 자동으로 관리합니다.
- **리소스 절약**: 여러 요청에서 메모리와 CPU를 더 효율적으로 사용합니다.
- **설정 통합**: 요청 설정을 한곳에서 관리합니다.

## 예제 {#examples}
웹 스크래핑을 처음 시작하는 분들을 위한 전체 예제입니다.

### 기본 HTTP 요청 {#basic-http-request}

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

### 상품 데이터 수집 {#product-scraping}

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

### 파일 다운로드 {#downloading-files}

```python
from scrapling.fetchers import Fetcher

page = Fetcher.get('https://raw.githubusercontent.com/D4Vinci/Scrapling/main/docs/assets/main_cover.png')
with open(file='main_cover.png', mode='wb') as f:
   f.write(page.body)
```

### 여러 페이지 처리 {#pagination-handling}

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

### 폼 제출 {#form-submission}

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

### 표 추출 {#table-extraction}

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

### 탐색 메뉴 {#navigation-menu}

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

## 언제 사용하나요? {#when-to-use}

다음 경우에는 `Fetcher`를 사용하세요.

- 빠른 HTTP 요청이 필요할 때.
- 리소스 사용량을 줄이고 싶을 때.
- JavaScript 실행 없이 요청만으로 사이트를 수집할 수 있을 때.
- 탐지 회피 기능이 일부 필요할 때. 예를 들어 사이트에 보호 기능은 있지만 JavaScript 검사는 없을 때입니다.

다음 경우에는 `FetcherSession`을 사용하세요.

- 같은 사이트나 여러 사이트에 반복해서 요청할 때.
- 요청 사이에 쿠키나 인증 상태를 유지해야 할 때.
- 연결을 재사용해 속도를 높이고 싶을 때.
- 요청마다 같은 설정이 필요할 때.
- 세션 상태가 필요한 API를 사용할 때.

다음 경우에는 다른 Fetcher를 사용하세요.

- 브라우저 자동화가 필요할 때.
- 고급 봇 차단 우회나 탐지 회피 기능이 필요할 때.
- JavaScript 실행이나 동적 콘텐츠와의 상호작용이 필요할 때.
