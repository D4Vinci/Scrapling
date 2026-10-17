---
title: "Scrapling 入门：解析页面、HTTP 请求和隐身浏览器"
description: "通过 CSS、XPath、文本搜索、HTTP 请求和隐身浏览器示例学习 Scrapling。"
---

# 开始使用 Scrapling {#get-started-with-scrapling}

## 选择起点 {#pick-your-path}

还不知道从哪里开始？根据你的任务选择：

| 我想…… | 从这里开始 |
|:---|:---|
| **解析已有的 HTML** | [选择元素](parsing/selection.md)：CSS、XPath 和文本搜索 |
| **快速抓取页面**，试一试想法 | 选择并试用一个 [Fetcher](fetching/choosing.md)，或打开[交互式 Shell](cli/interactive-shell.md) |
| **构建能处理更多页面的爬虫** | [Spider](spiders/getting-started.md)：并发爬取、多种会话、暂停和恢复 |
| **不写代码就提取数据** | 使用[提取命令](cli/extract-commands.md)，或将 [MCP 服务器](ai/mcp-server.md)连接到 AI 工具 |
| **从其他库迁移** | [从 BeautifulSoup 迁移](tutorials/migrating_from_beautifulsoup.md)，或查看[与 Scrapy 的对比](spiders/architecture.md#comparison-with-scrapy) |

---

先学习如何解析页面，再学习如何用浏览器获取页面、发送请求并解析响应。

本页示例使用下面这个由 ChatGPT 生成的 HTML 文档：
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
先加载上面的 HTML：
```python
import re
from scrapling.parser import Selector
page = Selector(html_doc)
page  # <data='<html><head><title>Complex Web Page</tit...'>
```
获取页面中的全部文本，包括嵌套元素的文本：
```python
page.get_all_text(ignore_tags=('script', 'style'))
# 'Complex Web Page\nHome\nAbout\nContact\nProducts\nProduct 1\nThis is product 1\n$10.99\nIn stock: 5\nProduct 2\nThis is product 2\n$20.99\nIn stock: 3\nProduct 3\nThis is product 3\n$15.99\nOut of stock\nCustomer Reviews\nGreat product!\nJohn Doe\nGood value for money.\nJane Smith'
```

## 查找元素 {#finding-elements}
可以组合不同的方法，找到需要的元素。

查找第一个 `section` HTML 元素：
```python
section_element = page.find('section')
# <data='<section id="products" schema='{"jsonabl...' parent='<main><section id="products" schema='{"j...'>
```
查找所有 `section` 元素：
```python
section_elements = page.find_all('section')
# [<data='<section id="products" schema='{"jsonabl...' parent='<main><section id="products" schema='{"j...'>, <data='<section id="reviews"><h2>Customer Revie...' parent='<main><section id="products" schema='{"j...'>]
```
查找 `id` 属性值为 `products` 的所有 `section` 元素：
```python
section_elements = page.find_all('section', {'id':"products"})
# Same as
section_elements = page.find_all('section', id="products")
# [<data='<section id="products" schema='{"jsonabl...' parent='<main><section id="products" schema='{"j...'>]
```
查找 `id` 属性值包含 `product` 的所有 `section` 元素：
```python
section_elements = page.find_all('section', {'id*':"product"})
```
查找文本匹配正则表达式 `Product \d` 的 `h3` 元素：
```python
page.find_all('h3', re.compile(r'Product \d'))
# [<data='<h3>Product 1</h3>' parent='<article class="product" data-id="1"><h3...'>, <data='<h3>Product 2</h3>' parent='<article class="product" data-id="2"><h3...'>, <data='<h3>Product 3</h3>' parent='<article class="product" data-id="3"><h3...'>]
```
查找文本匹配正则表达式 `Product` 的 `h3` 和 `h2` 元素：
```python
page.find_all(['h3', 'h2'], re.compile(r'Product'))
# [<data='<h3>Product 1</h3>' parent='<article class="product" data-id="1"><h3...'>, <data='<h3>Product 2</h3>' parent='<article class="product" data-id="2"><h3...'>, <data='<h3>Product 3</h3>' parent='<article class="product" data-id="3"><h3...'>, <data='<h2>Products</h2>' parent='<section id="products" schema='{"jsonabl...'>]
```
查找文本正好是 `Products` 的元素，忽略空白字符：
```python
page.find_by_text('Products', first_match=False)
# [<data='<h2>Products</h2>' parent='<section id="products" schema='{"jsonabl...'>]
```
也可以查找文本匹配正则表达式 `Product \d` 的元素：
```python
page.find_by_regex(r'Product \d', first_match=False)
# [<data='<h3>Product 1</h3>' parent='<article class="product" data-id="1"><h3...'>, <data='<h3>Product 2</h3>' parent='<article class="product" data-id="2"><h3...'>, <data='<h3>Product 3</h3>' parent='<article class="product" data-id="3"><h3...'>]
```
查找与当前元素相似的元素：
```python
target_element = page.find_by_regex(r'Product \d', first_match=True)
# <data='<h3>Product 1</h3>' parent='<article class="product" data-id="1"><h3...'>
target_element.find_similar()
# [<data='<h3>Product 2</h3>' parent='<article class="product" data-id="2"><h3...'>, <data='<h3>Product 3</h3>' parent='<article class="product" data-id="3"><h3...'>]
```
查找匹配 CSS 选择器的第一个元素：
```python
page.css('.product-list [data-id="1"]')[0]
# <data='<article class="product" data-id="1"><h3...' parent='<div class="product-list"> <article clas...'>
```
查找匹配 CSS 选择器的所有元素：
```python
page.css('.product-list article')
# [<data='<article class="product" data-id="1"><h3...' parent='<div class="product-list"> <article clas...'>, <data='<article class="product" data-id="2"><h3...' parent='<div class="product-list"> <article clas...'>, <data='<article class="product" data-id="3"><h3...' parent='<div class="product-list"> <article clas...'>]
```
查找匹配 XPath 选择器的第一个元素：
```python
page.xpath("//*[@id='products']/div/article")[0]
# <data='<article class="product" data-id="1"><h3...' parent='<div class="product-list"> <article clas...'>
```
查找匹配 XPath 选择器的所有元素：
```python
page.xpath("//*[@id='products']/div/article")
# [<data='<article class="product" data-id="1"><h3...' parent='<div class="product-list"> <article clas...'>, <data='<article class="product" data-id="2"><h3...' parent='<div class="product-list"> <article clas...'>, <data='<article class="product" data-id="3"><h3...' parent='<div class="product-list"> <article clas...'>]
```

这些是基本用法。后面会介绍各个选择方法的更多选项。
## 读取元素数据 {#accessing-elements-data}
可以这样读取数据：
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

## 导航 {#navigation}
使用前面找到的元素：

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
除了访问父元素，还可以遍历元素的所有祖先：
```python
for ancestor in section_element.iterancestors():
    print(ancestor.tag)
```
也可以查找符合条件的祖先元素。传入一个函数，接收 `Selector` 对象，符合条件时返回 `True`，否则返回 `False`：
```pycon
>>> section_element.find_ancestor(lambda ancestor: ancestor.css('nav'))
<data='<body> <header><nav><ul><li> <a href="#h...' parent='<html><head><title>Complex Web Page</tit...'>
```

## 获取网页 {#fetching-websites}
除了将 HTML 传给 Scrapling，还可以通过 HTTP 请求或浏览器获取网站的响应。

根据任务选择合适的 Fetcher。

### HTTP 请求 {#http-requests}
导入并使用 `Fetcher` 类发送 HTTP 请求：
```python
from scrapling.fetchers import Fetcher
page = Fetcher.get('https://scrapling.requestcatcher.com/get', impersonate="chrome")
```
下面展示了不同的 HTTP 方法：
```python
from scrapling.fetchers import Fetcher
page = Fetcher.get('https://scrapling.requestcatcher.com/get', stealthy_headers=True)
page = Fetcher.post('https://scrapling.requestcatcher.com/post', data={'key': 'value'}, proxy='http://username:password@localhost:8030')
page = Fetcher.put('https://scrapling.requestcatcher.com/put', data={'key': 'value'})
page = Fetcher.delete('https://scrapling.requestcatcher.com/delete')
```
要使用异步请求，只需修改导入：
```python
from scrapling.fetchers import AsyncFetcher
page = await AsyncFetcher.get('https://scrapling.requestcatcher.com/get', stealthy_headers=True)
page = await AsyncFetcher.post('https://scrapling.requestcatcher.com/post', data={'key': 'value'}, proxy='http://username:password@localhost:8030')
page = await AsyncFetcher.put('https://scrapling.requestcatcher.com/put', data={'key': 'value'})
page = await AsyncFetcher.delete('https://scrapling.requestcatcher.com/delete')
```

!!! note "说明"

    1. `stealthy_headers` 生成真实浏览器的请求头，包括 Google Referer，默认启用。
    2. `impersonate` 可以模拟指定浏览器版本的 TLS 指纹。
    3. `http3` 启用 HTTP/3，让请求更接近真实浏览器。

更多选项请查看 [HTTP 请求指南](fetching/static.md)。

### 动态加载 {#dynamic-loading}
也可以处理用 JavaScript 加载内容的网站。

`StealthyFetcher` 提供多种选项，通过基于 Chromium 的浏览器获取和加载页面。
```python
from scrapling.fetchers import StealthyFetcher
page = StealthyFetcher.fetch('https://quotes.toscrape.com/js/', disable_resources=True, block_ads=True, wait_selector='.quote')
print(len(page.css(".quote")))  # -> 10

# The async version of fetch
page = await StealthyFetcher.async_fetch('https://quotes.toscrape.com/js/', disable_resources=True, block_ads=True, wait_selector='.quote')
print(len(page.css(".quote")))  # -> 10
```
它使用经过修改的 [Playwright](https://playwright.dev/python/)，隐藏自动化特征。可以使用自带的 Chromium，通过 `real_chrome=True` 使用已安装的 Google Chrome，或通过 `cdp_url` 连接正在运行的浏览器。

### 反检测功能 {#anti-bot-features}

包括以下功能：

1. 设置 `solve_cloudflare=True`，自动处理多种 Cloudflare Turnstile 和 Interstitial 验证。
2. 防止 CDP Runtime 和 WebRTC 泄漏。
3. 隔离 JavaScript 执行环境，移除许多 Playwright 特征，并避免一些常见的机器人行为检测。
4. 在 Canvas 中加入噪声，防止它被用于识别浏览器指纹。
5. 修复已知的无头浏览器检测问题，并可防止因时区不一致而被识别。
6. 提供更多避免检测的选项。

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

详情和完整参数列表见[浏览器指南](fetching/stealthy.md)。

---

以上是 Scrapling 的基本用法。下一节会介绍更多功能。
