---
title: "Scrapling 入門：解析、HTTP リクエスト、ステルスブラウザ"
description: "CSS、XPath、テキスト検索、HTTP リクエスト、ステルスブラウザの例で Scrapling の使い方を学びます。"
---

# Scrapling を使ってみる {#get-started-with-scrapling}

## 目的から選ぶ {#pick-your-path}

何から始めるか迷ったら、やりたいことに合う項目を選んでください。

| やりたいこと | 最初に読むページ |
|:---|:---|
| 手元にある **HTML を解析する** | [要素の選択](parsing/selection.md)：CSS、XPath、テキストによる検索 |
| **ページをすぐに取得して**試す | [Fetcher を選んで](fetching/choosing.md)試すか、[対話型シェル](cli/interactive-shell.md)を起動します |
| 多くのページを処理する**クローラーを作る** | [Spider](spiders/getting-started.md)：並行処理、複数のセッション、一時停止と再開 |
| **コードを書かずに取得する** | [CLI の抽出コマンド](cli/extract-commands.md)を使うか、[MCP サーバー](ai/mcp-server.md)を AI ツールに接続します |
| 他のライブラリから**移行する** | [BeautifulSoup からの移行](tutorials/migrating_from_beautifulsoup.md)、または [Scrapy との比較](spiders/architecture.md#comparison-with-scrapy) |

---

まずページの解析方法を見ていきます。その後、ブラウザでのページ取得、リクエストの送信、レスポンスの解析を試します。

このページでは、ChatGPT が生成した次の HTML を使います。
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
まず、この HTML を読み込みます。
```python
import re
from scrapling.parser import Selector
page = Selector(html_doc)
page  # <data='<html><head><title>Complex Web Page</tit...'>
```
入れ子の要素も含め、ページ内のすべてのテキストを取得します。
```python
page.get_all_text(ignore_tags=('script', 'style'))
# 'Complex Web Page\nHome\nAbout\nContact\nProducts\nProduct 1\nThis is product 1\n$10.99\nIn stock: 5\nProduct 2\nThis is product 2\n$20.99\nIn stock: 3\nProduct 3\nThis is product 3\n$15.99\nOut of stock\nCustomer Reviews\nGreat product!\nJohn Doe\nGood value for money.\nJane Smith'
```

## 要素を探す {#finding-elements}
いくつかの方法を組み合わせて、必要な要素を探せます。

最初の HTML `section` 要素を探します。
```python
section_element = page.find('section')
# <data='<section id="products" schema='{"jsonabl...' parent='<main><section id="products" schema='{"j...'>
```
すべての `section` 要素を探します。
```python
section_elements = page.find_all('section')
# [<data='<section id="products" schema='{"jsonabl...' parent='<main><section id="products" schema='{"j...'>, <data='<section id="reviews"><h2>Customer Revie...' parent='<main><section id="products" schema='{"j...'>]
```
`id` 属性が `products` の `section` 要素をすべて探します。
```python
section_elements = page.find_all('section', {'id':"products"})
# Same as
section_elements = page.find_all('section', id="products")
# [<data='<section id="products" schema='{"jsonabl...' parent='<main><section id="products" schema='{"j...'>]
```
`id` 属性に `product` を含む `section` 要素をすべて探します。
```python
section_elements = page.find_all('section', {'id*':"product"})
```
テキストが正規表現 `Product \d` に一致する `h3` 要素を探します。
```python
page.find_all('h3', re.compile(r'Product \d'))
# [<data='<h3>Product 1</h3>' parent='<article class="product" data-id="1"><h3...'>, <data='<h3>Product 2</h3>' parent='<article class="product" data-id="2"><h3...'>, <data='<h3>Product 3</h3>' parent='<article class="product" data-id="3"><h3...'>]
```
テキストが正規表現 `Product` に一致する `h3` 要素と `h2` 要素を探します。
```python
page.find_all(['h3', 'h2'], re.compile(r'Product'))
# [<data='<h3>Product 1</h3>' parent='<article class="product" data-id="1"><h3...'>, <data='<h3>Product 2</h3>' parent='<article class="product" data-id="2"><h3...'>, <data='<h3>Product 3</h3>' parent='<article class="product" data-id="3"><h3...'>, <data='<h2>Products</h2>' parent='<section id="products" schema='{"jsonabl...'>]
```
テキストが `Products` と完全に一致する要素を探します。空白は無視します。
```python
page.find_by_text('Products', first_match=False)
# [<data='<h2>Products</h2>' parent='<section id="products" schema='{"jsonabl...'>]
```
正規表現 `Product \d` に一致するテキストを持つ要素も探せます。
```python
page.find_by_regex(r'Product \d', first_match=False)
# [<data='<h3>Product 1</h3>' parent='<article class="product" data-id="1"><h3...'>, <data='<h3>Product 2</h3>' parent='<article class="product" data-id="2"><h3...'>, <data='<h3>Product 3</h3>' parent='<article class="product" data-id="3"><h3...'>]
```
指定した要素に似た要素を探します。
```python
target_element = page.find_by_regex(r'Product \d', first_match=True)
# <data='<h3>Product 1</h3>' parent='<article class="product" data-id="1"><h3...'>
target_element.find_similar()
# [<data='<h3>Product 2</h3>' parent='<article class="product" data-id="2"><h3...'>, <data='<h3>Product 3</h3>' parent='<article class="product" data-id="3"><h3...'>]
```
CSS セレクターに一致する最初の要素を探します。
```python
page.css('.product-list [data-id="1"]')[0]
# <data='<article class="product" data-id="1"><h3...' parent='<div class="product-list"> <article clas...'>
```
CSS セレクターに一致するすべての要素を探します。
```python
page.css('.product-list article')
# [<data='<article class="product" data-id="1"><h3...' parent='<div class="product-list"> <article clas...'>, <data='<article class="product" data-id="2"><h3...' parent='<div class="product-list"> <article clas...'>, <data='<article class="product" data-id="3"><h3...' parent='<div class="product-list"> <article clas...'>]
```
XPath セレクターに一致する最初の要素を探します。
```python
page.xpath("//*[@id='products']/div/article")[0]
# <data='<article class="product" data-id="1"><h3...' parent='<div class="product-list"> <article clas...'>
```
XPath セレクターに一致するすべての要素を探します。
```python
page.xpath("//*[@id='products']/div/article")
# [<data='<article class="product" data-id="1"><h3...' parent='<div class="product-list"> <article clas...'>, <data='<article class="product" data-id="2"><h3...' parent='<div class="product-list"> <article clas...'>, <data='<article class="product" data-id="3"><h3...' parent='<div class="product-list"> <article clas...'>]
```

ここでは基本的な使い方を紹介しました。各メソッドの詳しいオプションは後で説明します。
## 要素のデータを読む {#accessing-elements-data}
次のようにデータを取得できます。
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

## 要素をたどる {#navigation}
先ほど見つけた要素を使います。

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
親要素だけでなく、祖先要素全体を順番にたどることもできます。
```python
for ancestor in section_element.iterancestors():
    print(ancestor.tag)
```
条件を満たす祖先要素も探せます。`Selector` を受け取り、条件を満たす場合は `True`、それ以外は `False` を返す関数を渡します。
```pycon
>>> section_element.find_ancestor(lambda ancestor: ancestor.css('nav'))
<data='<body> <header><nav><ul><li> <a href="#h...' parent='<html><head><title>Complex Web Page</tit...'>
```

## ウェブページを取得する {#fetching-websites}
HTML を Scrapling に渡すほかに、HTTP リクエストやブラウザでサイトのレスポンスを取得することもできます。

目的に合う Fetcher を選んでください。

### HTTP リクエスト {#http-requests}
`Fetcher` クラスをインポートして、HTTP リクエストを送ります。
```python
from scrapling.fetchers import Fetcher
page = Fetcher.get('https://scrapling.requestcatcher.com/get', impersonate="chrome")
```
各 HTTP メソッドは次のように使います。
```python
from scrapling.fetchers import Fetcher
page = Fetcher.get('https://scrapling.requestcatcher.com/get', stealthy_headers=True)
page = Fetcher.post('https://scrapling.requestcatcher.com/post', data={'key': 'value'}, proxy='http://username:password@localhost:8030')
page = Fetcher.put('https://scrapling.requestcatcher.com/put', data={'key': 'value'})
page = Fetcher.delete('https://scrapling.requestcatcher.com/delete')
```
非同期リクエストには、インポートを次のように変更します。
```python
from scrapling.fetchers import AsyncFetcher
page = await AsyncFetcher.get('https://scrapling.requestcatcher.com/get', stealthy_headers=True)
page = await AsyncFetcher.post('https://scrapling.requestcatcher.com/post', data={'key': 'value'}, proxy='http://username:password@localhost:8030')
page = await AsyncFetcher.put('https://scrapling.requestcatcher.com/put', data={'key': 'value'})
page = await AsyncFetcher.delete('https://scrapling.requestcatcher.com/delete')
```

!!! note "補足"

    1. `stealthy_headers` は、Google の Referer を含む実際のブラウザのヘッダーを生成します。既定で有効です。
    2. `impersonate` は、指定したブラウザのバージョンの TLS フィンガープリントを模倣します。
    3. `http3` は HTTP/3 を有効にして、実際のブラウザに近いリクエストを送ります。

そのほかのオプションは [HTTP リクエストのガイド](fetching/static.md)をご覧ください。

### 動的なページの読み込み {#dynamic-loading}
JavaScript で内容を読み込むサイトにも対応できます。

`StealthyFetcher` は、Chromium ベースのブラウザでページを取得するための多くのオプションを備えています。
```python
from scrapling.fetchers import StealthyFetcher
page = StealthyFetcher.fetch('https://quotes.toscrape.com/js/', disable_resources=True, block_ads=True, wait_selector='.quote')
print(len(page.css(".quote")))  # -> 10

# The async version of fetch
page = await StealthyFetcher.async_fetch('https://quotes.toscrape.com/js/', disable_resources=True, block_ads=True, wait_selector='.quote')
print(len(page.css(".quote")))  # -> 10
```
自動化の痕跡を隠す変更を加えた [Playwright](https://playwright.dev/python/) を使っています。同梱の Chromium、`real_chrome=True` で指定するインストール済みの Google Chrome、`cdp_url` で接続する起動中のブラウザを使えます。

### ボット検出を避ける機能 {#anti-bot-features}

主に次の機能があります。

1. `solve_cloudflare=True` で、Cloudflare Turnstile と Interstitial の各種検証を自動処理します。
2. CDP Runtime と WebRTC のリークを防ぎます。
3. JavaScript の実行環境を分離し、多くの Playwright の痕跡を消し、よく知られたボットの動作による検出を避けます。
4. Canvas にノイズを加え、フィンガープリントによる識別を防ぎます。
5. 既知のヘッドレスモード検出方法に対応し、タイムゾーンの不一致による検出を防ぐオプションも提供します。
6. そのほかにも検出を避けるオプションがあります。

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

詳しい説明とすべての引数は、[ブラウザのガイド](fetching/stealthy.md)をご覧ください。

---

以上が Scrapling の基本です。さらに詳しく知りたい場合は、次のセクションに進んでください。
