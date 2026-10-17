---
title: "Scrapling 대화형 셸에서 웹 스크래핑 테스트하기"
description: "IPython 셸에서 페이지를 가져오고 선택자를 시험하며 결과를 확인하세요. curl 명령을 변환하고 최근 응답을 재사용하며 코드를 테스트할 수 있습니다."
---

# Scrapling 대화형 셸 안내 {#scrapling-interactive-shell-guide}

<script src="https://asciinema.org/a/736339.js" id="asciicast-736339" async data-autoplay="1" data-loop="1" data-cols="225" data-rows="40" data-start-at="00:06" data-speed="1.5" data-theme="tango"></script>

**개발자와 데이터 과학자를 위한 웹 스크래핑 REPL**

Scrapling 대화형 셸은 웹 스크래핑에 맞게 확장한 IPython 기반 환경입니다. 모든 Scrapling 기능을 바로 사용할 수 있습니다. 편리한 단축 함수, 자동 페이지 관리, curl 명령 변환 같은 기능도 제공합니다.

!!! success "시작하기 전에"

    1. [Fetcher 기초](../fetching/choosing.md)를 읽고 [Response 객체](../fetching/choosing.md#response-object)와 Fetcher 선택 방법을 이해하세요.
    2. [요소 찾기](../parsing/selection.md)를 읽고 [Selector](../parsing/main_classes.md#selector)/[Response](../fetching/choosing.md#response-object)에서 요소를 찾고 추출하는 방법을 이해하세요.
    3. [주요 클래스](../parsing/main_classes.md)를 읽고 [Response](../fetching/choosing.md#response-object)가 [Selector](../parsing/main_classes.md#selector)에서 물려받는 속성과 메서드를 알아두세요.
    4. 사용할 Fetcher에 맞게 [HTTP 요청](../fetching/static.md) 또는 [브라우저로 가져오기](../fetching/stealthy.md) 중 하나 이상을 읽으세요.


## 대화형 셸을 사용하는 이유 {#why-use-the-interactive-shell}

대화형 셸에서는 스크립트를 작성하고 실행하는 과정을 매번 반복하지 않아도 됩니다. 그 자리에서 빠르게 시도하며 스크래핑할 수 있습니다. 다음 작업에 적합합니다.

- **빠른 프로토타입 작성**: 스크래핑 방법을 바로 테스트합니다.
- **데이터 탐색**: 대화형으로 웹사이트를 살펴보고 데이터를 추출합니다.
- **Scrapling 학습**: 기능을 직접 실행하며 배웁니다.
- **스크래퍼 디버깅**: 요청을 단계별로 실행하고 결과를 확인합니다.
- **작업 방식 변환**: 브라우저 DevTools의 curl 명령을 한 줄로 Fetcher 요청으로 바꿉니다.

## 시작하기 {#getting-started}

### 셸 실행 {#launch-the-shell}

```bash
# Start the interactive shell
scrapling shell

# Execute code and exit (useful for scripting)
scrapling shell -c "get('https://quotes.toscrape.com'); print(len(page.css('.quote')))"

# Set logging level
scrapling shell --loglevel info
```

실행하면 Scrapling 배너가 표시됩니다. 위 영상처럼 바로 스크래핑을 시작할 수 있습니다.

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

## 기본 제공 단축 함수 {#built-in-shortcuts}

반복되는 코드를 줄이기 위한 단축 함수를 제공합니다.

- **`get(url, **kwargs)`**: HTTP GET 요청. `Fetcher.get` 대신 사용합니다.
- **`post(url, **kwargs)`**: HTTP POST 요청. `Fetcher.post` 대신 사용합니다.
- **`put(url, **kwargs)`**: HTTP PUT 요청. `Fetcher.put` 대신 사용합니다.
- **`delete(url, **kwargs)`**: HTTP DELETE 요청. `Fetcher.delete` 대신 사용합니다.
- **`fetch(url, **kwargs)`**: 스텔스 브라우저로 가져오기. `StealthyFetcher.fetch` 대신 사용합니다.

`Fetcher`, `AsyncFetcher`, `StealthyFetcher`, `Selector`처럼 자주 쓰는 클래스는 가져오기 구문 없이 바로 사용할 수 있습니다.

### 자동 페이지 관리 {#smart-page-management}

셸은 요청과 페이지를 자동으로 추적합니다.

- **현재 페이지 접근**

    `page`와 `response`는 마지막으로 가져온 페이지로 자동 갱신됩니다.
    
    ```python
    get('https://quotes.toscrape.com')
    # 'page' and 'response' both refer to the last fetched page
    page.url  # 'https://quotes.toscrape.com'
    response.status  # Prints 200; Same as page.status
    ```

- **페이지 기록**

    `pages`는 최근 다섯 페이지를 보관하는 `Selectors` 객체입니다.
    
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

## 기타 유용한 명령 {#additional-helpful-commands}

### 페이지 보기 {#page-visualization}

가져온 페이지를 브라우저에서 확인하세요.

```python
get('https://quotes.toscrape.com')
view(page)  # Opens the page HTML in your default browser
```

### curl 명령 연동 {#curl-command-integration}

브라우저 DevTools의 curl 명령을 `Fetcher` 요청으로 바꿀 수 있도록 `uncurl`과 `curl2fetcher` 함수를 제공합니다.

먼저 다음과 같이 요청을 curl 명령으로 복사하세요.

<img src="../assets/scrapling_shell_curl.png" title="Chrome의 요청을 curl 명령으로 복사하기" alt="Chrome의 요청을 curl 명령으로 복사하기" style="width: 70%;"/>

- **curl 명령을 Request 객체로 변환하기**

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

- **curl 명령 바로 실행하기**

    ```python
    # Convert and execute in one step
    curl2fetcher(curl_cmd)
    page.status  # -> 200
    ```

### IPython 기능 {#ipython-features}

셸은 IPython의 모든 기능을 지원합니다.

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

## 예제 {#examples}

AI로 생성한 몇 가지 예제입니다.

#### 쇼핑몰 데이터 수집 {#e-commerce-data-collection}

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

#### API 연동과 테스트 {#api-integration-and-testing}

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

## 도움말 {#getting-help}

터미널에 있는 도움말로 부족하다면 다음을 이용하세요.

- [Scrapling 문서](https://scrapling.readthedocs.io/ko/latest/)
- [Discord 커뮤니티](https://discord.gg/EMgGbDceNQ)
- [GitHub Issues](https://github.com/D4Vinci/Scrapling/issues)

이제 준비가 끝났습니다. 즐겁게 스크래핑하세요! 셸을 사용하면 대화하듯 쉽게 웹 스크래핑을 진행할 수 있습니다.
