---
title: "Scrapling 시작하기: 파싱, HTTP 요청, 스텔스 브라우저"
description: "CSS, XPath, 텍스트 검색, HTTP 요청, 스텔스 브라우저 예제로 Scrapling의 주요 기능을 알아보세요."
---

# Scrapling 시작하기 {#get-started-with-scrapling}

## 목적에 맞게 시작하기 {#pick-your-path}

어디서 시작할지 모르겠다면 하려는 작업을 고르세요:

| 하고 싶은 일 | 시작할 문서 |
|:---|:---|
| 이미 가진 **HTML 파싱하기** | [요소 찾기](parsing/selection.md): CSS, XPath, 텍스트로 선택하기 |
| **페이지를 빠르게 가져와** 시험하기 | [Fetcher](fetching/choosing.md)를 골라 바로 시험하거나 [대화형 셸](cli/interactive-shell.md)을 실행하세요 |
| 많은 페이지를 처리할 **크롤러 만들기** | [스파이더](spiders/getting-started.md): 동시 요청, 여러 세션, 일시 정지와 재개 |
| **코드 없이 수집하기** | [CLI 추출 명령어](cli/extract-commands.md)를 쓰거나 [MCP 서버](ai/mcp-server.md)를 AI 도구에 연결하세요 |
| 다른 라이브러리에서 **옮기기** | [BeautifulSoup에서 옮기기](tutorials/migrating_from_beautifulsoup.md) 또는 [Scrapy와 비교](spiders/architecture.md#comparison-with-scrapy) |

---

먼저 파싱 기능을 살펴보겠습니다. 이어서 브라우저로 사이트를 가져오고, 요청을 보내고, 응답을 파싱합니다.

이 페이지에서는 ChatGPT가 만든 다음 HTML을 예제로 사용합니다:
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
먼저 위 HTML을 불러옵니다:
```python
import re
from scrapling.parser import Selector
page = Selector(html_doc)
page  # <data='<html><head><title>Complex Web Page</tit...'>
```
중첩된 요소를 포함해 페이지의 모든 텍스트를 가져옵니다:
```python
page.get_all_text(ignore_tags=('script', 'style'))
# 'Complex Web Page\nHome\nAbout\nContact\nProducts\nProduct 1\nThis is product 1\n$10.99\nIn stock: 5\nProduct 2\nThis is product 2\n$20.99\nIn stock: 3\nProduct 3\nThis is product 3\n$15.99\nOut of stock\nCustomer Reviews\nGreat product!\nJohn Doe\nGood value for money.\nJane Smith'
```

## 요소 찾기 {#finding-elements}
원하는 요소를 찾을 수 있습니다! 여러 검색 방법을 자유롭게 조합해 보세요.

첫 번째 HTML `section` 요소를 찾습니다:
```python
section_element = page.find('section')
# <data='<section id="products" schema='{"jsonabl...' parent='<main><section id="products" schema='{"j...'>
```
모든 `section` 요소를 찾습니다:
```python
section_elements = page.find_all('section')
# [<data='<section id="products" schema='{"jsonabl...' parent='<main><section id="products" schema='{"j...'>, <data='<section id="reviews"><h2>Customer Revie...' parent='<main><section id="products" schema='{"j...'>]
```
`id` 속성이 `products`인 모든 `section` 요소를 찾습니다:
```python
section_elements = page.find_all('section', {'id':"products"})
# Same as
section_elements = page.find_all('section', id="products")
# [<data='<section id="products" schema='{"jsonabl...' parent='<main><section id="products" schema='{"j...'>]
```
`id` 속성에 `product`가 포함된 모든 `section` 요소를 찾습니다:
```python
section_elements = page.find_all('section', {'id*':"product"})
```
텍스트가 정규식 `Product \d`와 일치하는 `h3` 요소를 찾습니다:
```python
page.find_all('h3', re.compile(r'Product \d'))
# [<data='<h3>Product 1</h3>' parent='<article class="product" data-id="1"><h3...'>, <data='<h3>Product 2</h3>' parent='<article class="product" data-id="2"><h3...'>, <data='<h3>Product 3</h3>' parent='<article class="product" data-id="3"><h3...'>]
```
텍스트가 정규식 `Product`와 일치하는 `h3`와 `h2` 요소를 찾습니다:
```python
page.find_all(['h3', 'h2'], re.compile(r'Product'))
# [<data='<h3>Product 1</h3>' parent='<article class="product" data-id="1"><h3...'>, <data='<h3>Product 2</h3>' parent='<article class="product" data-id="2"><h3...'>, <data='<h3>Product 3</h3>' parent='<article class="product" data-id="3"><h3...'>, <data='<h2>Products</h2>' parent='<section id="products" schema='{"jsonabl...'>]
```
텍스트가 정확히 `Products`인 요소를 찾습니다. 공백은 무시합니다:
```python
page.find_by_text('Products', first_match=False)
# [<data='<h2>Products</h2>' parent='<section id="products" schema='{"jsonabl...'>]
```
텍스트가 정규식 `Product \d`와 일치하는 요소를 찾을 수도 있습니다:
```python
page.find_by_regex(r'Product \d', first_match=False)
# [<data='<h3>Product 1</h3>' parent='<article class="product" data-id="1"><h3...'>, <data='<h3>Product 2</h3>' parent='<article class="product" data-id="2"><h3...'>, <data='<h3>Product 3</h3>' parent='<article class="product" data-id="3"><h3...'>]
```
지정한 요소와 비슷한 요소를 찾습니다:
```python
target_element = page.find_by_regex(r'Product \d', first_match=True)
# <data='<h3>Product 1</h3>' parent='<article class="product" data-id="1"><h3...'>
target_element.find_similar()
# [<data='<h3>Product 2</h3>' parent='<article class="product" data-id="2"><h3...'>, <data='<h3>Product 3</h3>' parent='<article class="product" data-id="3"><h3...'>]
```
CSS 선택자와 일치하는 첫 요소를 찾습니다:
```python
page.css('.product-list [data-id="1"]')[0]
# <data='<article class="product" data-id="1"><h3...' parent='<div class="product-list"> <article clas...'>
```
CSS 선택자와 일치하는 모든 요소를 찾습니다:
```python
page.css('.product-list article')
# [<data='<article class="product" data-id="1"><h3...' parent='<div class="product-list"> <article clas...'>, <data='<article class="product" data-id="2"><h3...' parent='<div class="product-list"> <article clas...'>, <data='<article class="product" data-id="3"><h3...' parent='<div class="product-list"> <article clas...'>]
```
XPath 선택자와 일치하는 첫 요소를 찾습니다:
```python
page.xpath("//*[@id='products']/div/article")[0]
# <data='<article class="product" data-id="1"><h3...' parent='<div class="product-list"> <article clas...'>
```
XPath 선택자와 일치하는 모든 요소를 찾습니다:
```python
page.xpath("//*[@id='products']/div/article")
# [<data='<article class="product" data-id="1"><h3...' parent='<div class="product-list"> <article clas...'>, <data='<article class="product" data-id="2"><h3...' parent='<div class="product-list"> <article clas...'>, <data='<article class="product" data-id="3"><h3...' parent='<div class="product-list"> <article clas...'>]
```

여기서는 기본 기능만 살펴봤습니다. 각 선택 메서드의 추가 옵션은 뒤에서 설명합니다.
## 요소의 데이터 읽기 {#accessing-elements-data}
다음처럼 간단히 읽을 수 있습니다:
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

## 요소 사이 이동 {#navigation}
앞에서 찾은 요소를 사용합니다:

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
부모 요소뿐 아니라 조상 요소 전체를 차례로 살펴볼 수도 있습니다:
```python
for ancestor in section_element.iterancestors():
    print(ancestor.tag)
```
조건에 맞는 조상 요소를 찾을 수도 있습니다. `Selector`를 받아 조건을 만족하면 `True`, 아니면 `False`를 반환하는 함수를 전달하세요:
```pycon
>>> section_element.find_ancestor(lambda ancestor: ancestor.css('nav'))
<data='<body> <header><nav><ul><li> <a href="#h...' parent='<html><head><title>Complex Web Page</tit...'>
```

## 사이트 가져오기 {#fetching-websites}
Scrapling에 HTML을 직접 전달하는 대신 HTTP 요청이나 브라우저로 사이트의 응답을 가져올 수 있습니다.

작업에 맞는 Fetcher를 선택하세요.

### HTTP 요청 {#http-requests}
간단한 HTTP 요청에는 `Fetcher` 클래스를 가져와 사용합니다:
```python
from scrapling.fetchers import Fetcher
page = Fetcher.get('https://scrapling.requestcatcher.com/get', impersonate="chrome")
```
각 HTTP 메서드는 다음과 같이 사용합니다:
```python
from scrapling.fetchers import Fetcher
page = Fetcher.get('https://scrapling.requestcatcher.com/get', stealthy_headers=True)
page = Fetcher.post('https://scrapling.requestcatcher.com/post', data={'key': 'value'}, proxy='http://username:password@localhost:8030')
page = Fetcher.put('https://scrapling.requestcatcher.com/put', data={'key': 'value'})
page = Fetcher.delete('https://scrapling.requestcatcher.com/delete')
```
비동기 요청에는 가져오는 클래스를 다음처럼 바꾸세요:
```python
from scrapling.fetchers import AsyncFetcher
page = await AsyncFetcher.get('https://scrapling.requestcatcher.com/get', stealthy_headers=True)
page = await AsyncFetcher.post('https://scrapling.requestcatcher.com/post', data={'key': 'value'}, proxy='http://username:password@localhost:8030')
page = await AsyncFetcher.put('https://scrapling.requestcatcher.com/put', data={'key': 'value'})
page = await AsyncFetcher.delete('https://scrapling.requestcatcher.com/delete')
```

!!! note "참고"

    1. `stealthy_headers`를 켜면 Google Referer를 포함한 실제 브라우저 헤더를 생성해 사용합니다. 기본으로 켜져 있습니다.
    2. `impersonate`는 지정한 브라우저 버전의 TLS 지문을 흉내 냅니다.
    3. `http3`를 켜면 HTTP/3로 요청을 보내 실제 브라우저의 요청과 더 비슷하게 만듭니다.

이 밖에도 많은 기능이 있습니다. [HTTP 요청 가이드](fetching/static.md)를 확인하세요.

### 동적 페이지 불러오기 {#dynamic-loading}
JavaScript로 내용을 불러오는 동적 사이트도 처리할 수 있습니다!

`StealthyFetcher`는 Chromium 기반 브라우저로 페이지를 가져오는 다양한 옵션을 제공합니다.
```python
from scrapling.fetchers import StealthyFetcher
page = StealthyFetcher.fetch('https://quotes.toscrape.com/js/', disable_resources=True, block_ads=True, wait_selector='.quote')
print(len(page.css(".quote")))  # -> 10

# The async version of fetch
page = await StealthyFetcher.async_fetch('https://quotes.toscrape.com/js/', disable_resources=True, block_ads=True, wait_selector='.quote')
print(len(page.css(".quote")))  # -> 10
```
자동화 흔적을 숨기도록 수정한 [Playwright](https://playwright.dev/python/)를 사용합니다. 포함된 Chromium, `real_chrome=True`로 지정하는 설치된 Google Chrome, `cdp_url`로 연결하는 실행 중인 브라우저를 사용할 수 있습니다.

### 봇 탐지 우회 기능 {#anti-bot-features}

주요 기능은 다음과 같습니다:

1. `solve_cloudflare=True`로 모든 유형의 Cloudflare Turnstile과 Interstitial 검사를 자동으로 통과합니다.
2. CDP Runtime과 WebRTC 유출을 막습니다.
3. JavaScript 실행 환경을 분리하고 여러 Playwright 흔적을 없애며, 알려진 봇 행동에 따른 탐지를 막습니다.
4. Canvas에 노이즈를 넣어 브라우저 지문 수집을 막습니다.
5. 알려진 헤드리스 탐지 방법에 대응하며, 시간대 불일치를 이용한 탐지를 막는 옵션도 제공합니다.
6. 이 밖에도 보호 기능을 우회하는 여러 옵션이 있습니다.

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

자세한 설명과 전체 인수 목록은 [브라우저 가이드](fetching/stealthy.md)를 확인하세요.

---

Scrapling의 기본 기능을 살펴봤습니다. 더 알아보려면 다음 섹션으로 진행하세요.
