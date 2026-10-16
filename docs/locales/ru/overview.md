---
title: "Обзор Scrapling: разбор страниц, HTTP-запросы и скрытные браузеры"
description: "Познакомьтесь со Scrapling на примерах CSS, XPath, поиска по тексту, HTTP-запросов и скрытных браузеров."
---

# Начало работы со Scrapling {#get-started-with-scrapling}

## Выберите свою задачу {#pick-your-path}

Не знаете, с чего начать? Выберите подходящую задачу:

| Я хочу... | С чего начать |
|:---|:---|
| **Разобрать HTML**, который уже есть | [Поиск элементов](parsing/selection.md): CSS, XPath и текст |
| **Быстро получить страницу** и проверить идею | Выберите [Fetcher](fetching/choosing.md) или запустите [интерактивную оболочку](cli/interactive-shell.md) |
| **Создать краулер** для множества страниц | [Spider](spiders/getting-started.md): параллельный обход, несколько сессий, пауза и продолжение |
| **Собрать данные без кода** | [Команды CLI](cli/extract-commands.md) или [MCP-сервер](ai/mcp-server.md), подключённый к вашему AI-инструменту |
| **Перейти** с другой библиотеки | [Переход с BeautifulSoup](tutorials/migrating_from_beautifulsoup.md) или [сравнение со Scrapy](spiders/architecture.md#comparison-with-scrapy) |

---

Сначала посмотрим, как разбирать страницы. Затем загрузим сайты через браузеры, отправим запросы и разберём ответы.

В примерах на этой странице будем использовать HTML, который создал ChatGPT:
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
Сначала загрузим этот HTML:
```python
import re
from scrapling.parser import Selector
page = Selector(html_doc)
page  # <data='<html><head><title>Complex Web Page</tit...'>
```
Получим весь текст страницы, включая вложенные элементы:
```python
page.get_all_text(ignore_tags=('script', 'style'))
# 'Complex Web Page\nHome\nAbout\nContact\nProducts\nProduct 1\nThis is product 1\n$10.99\nIn stock: 5\nProduct 2\nThis is product 2\n$20.99\nIn stock: 3\nProduct 3\nThis is product 3\n$15.99\nOut of stock\nCustomer Reviews\nGreat product!\nJohn Doe\nGood value for money.\nJane Smith'
```

## Поиск элементов {#finding-elements}
Нужный элемент найдётся! Комбинируйте способы поиска под свою задачу.

Найдём первый HTML-элемент `section`:
```python
section_element = page.find('section')
# <data='<section id="products" schema='{"jsonabl...' parent='<main><section id="products" schema='{"j...'>
```
Найдём все элементы `section`:
```python
section_elements = page.find_all('section')
# [<data='<section id="products" schema='{"jsonabl...' parent='<main><section id="products" schema='{"j...'>, <data='<section id="reviews"><h2>Customer Revie...' parent='<main><section id="products" schema='{"j...'>]
```
Найдём все элементы `section`, у которых атрибут `id` равен `products`:
```python
section_elements = page.find_all('section', {'id':"products"})
# Same as
section_elements = page.find_all('section', id="products")
# [<data='<section id="products" schema='{"jsonabl...' parent='<main><section id="products" schema='{"j...'>]
```
Найдём все элементы `section`, у которых атрибут `id` содержит `product`:
```python
section_elements = page.find_all('section', {'id*':"product"})
```
Найдём элементы `h3`, текст которых соответствует регулярному выражению `Product \d`:
```python
page.find_all('h3', re.compile(r'Product \d'))
# [<data='<h3>Product 1</h3>' parent='<article class="product" data-id="1"><h3...'>, <data='<h3>Product 2</h3>' parent='<article class="product" data-id="2"><h3...'>, <data='<h3>Product 3</h3>' parent='<article class="product" data-id="3"><h3...'>]
```
Найдём элементы `h3` и `h2`, текст которых соответствует регулярному выражению `Product`:
```python
page.find_all(['h3', 'h2'], re.compile(r'Product'))
# [<data='<h3>Product 1</h3>' parent='<article class="product" data-id="1"><h3...'>, <data='<h3>Product 2</h3>' parent='<article class="product" data-id="2"><h3...'>, <data='<h3>Product 3</h3>' parent='<article class="product" data-id="3"><h3...'>, <data='<h2>Products</h2>' parent='<section id="products" schema='{"jsonabl...'>]
```
Найдём элементы с текстом, точно равным `Products`. Пробелы не учитываются:
```python
page.find_by_text('Products', first_match=False)
# [<data='<h2>Products</h2>' parent='<section id="products" schema='{"jsonabl...'>]
```
Или найдём элементы, текст которых соответствует регулярному выражению `Product \d`:
```python
page.find_by_regex(r'Product \d', first_match=False)
# [<data='<h3>Product 1</h3>' parent='<article class="product" data-id="1"><h3...'>, <data='<h3>Product 2</h3>' parent='<article class="product" data-id="2"><h3...'>, <data='<h3>Product 3</h3>' parent='<article class="product" data-id="3"><h3...'>]
```
Найдём элементы, похожие на выбранный:
```python
target_element = page.find_by_regex(r'Product \d', first_match=True)
# <data='<h3>Product 1</h3>' parent='<article class="product" data-id="1"><h3...'>
target_element.find_similar()
# [<data='<h3>Product 2</h3>' parent='<article class="product" data-id="2"><h3...'>, <data='<h3>Product 3</h3>' parent='<article class="product" data-id="3"><h3...'>]
```
Найдём первый элемент по CSS-селектору:
```python
page.css('.product-list [data-id="1"]')[0]
# <data='<article class="product" data-id="1"><h3...' parent='<div class="product-list"> <article clas...'>
```
Найдём все элементы по CSS-селектору:
```python
page.css('.product-list article')
# [<data='<article class="product" data-id="1"><h3...' parent='<div class="product-list"> <article clas...'>, <data='<article class="product" data-id="2"><h3...' parent='<div class="product-list"> <article clas...'>, <data='<article class="product" data-id="3"><h3...' parent='<div class="product-list"> <article clas...'>]
```
Найдём первый элемент по XPath-селектору:
```python
page.xpath("//*[@id='products']/div/article")[0]
# <data='<article class="product" data-id="1"><h3...' parent='<div class="product-list"> <article clas...'>
```
Найдём все элементы по XPath-селектору:
```python
page.xpath("//*[@id='products']/div/article")
# [<data='<article class="product" data-id="1"><h3...' parent='<div class="product-list"> <article clas...'>, <data='<article class="product" data-id="2"><h3...' parent='<div class="product-list"> <article clas...'>, <data='<article class="product" data-id="3"><h3...' parent='<div class="product-list"> <article clas...'>]
```

Это только начало. Дополнительные возможности этих методов описаны дальше.
## Чтение данных элементов {#accessing-elements-data}
Это просто:
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

## Навигация {#navigation}
Используем найденные выше элементы:

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
Если нужен не только родитель, можно пройти по всем предкам элемента:
```python
for ancestor in section_element.iterancestors():
    print(ancestor.tag)
```
Можно найти предка, который подходит под условие. Передайте функцию, которая принимает `Selector` и возвращает `True`, если условие выполнено, или `False` в противном случае:
```pycon
>>> section_element.find_ancestor(lambda ancestor: ancestor.css('nav'))
<data='<body> <header><nav><ul><li> <a href="#h...' parent='<html><head><title>Complex Web Page</tit...'>
```

## Загрузка сайтов {#fetching-websites}
Вместо передачи готового HTML можно получить ответ сайта через HTTP-запрос или браузер.

Для каждой задачи есть подходящий Fetcher.

### HTTP-запросы {#http-requests}
Для обычных HTTP-запросов импортируйте класс `Fetcher`:
```python
from scrapling.fetchers import Fetcher
page = Fetcher.get('https://scrapling.requestcatcher.com/get', impersonate="chrome")
```
Вот как использовать разные HTTP-методы:
```python
from scrapling.fetchers import Fetcher
page = Fetcher.get('https://scrapling.requestcatcher.com/get', stealthy_headers=True)
page = Fetcher.post('https://scrapling.requestcatcher.com/post', data={'key': 'value'}, proxy='http://username:password@localhost:8030')
page = Fetcher.put('https://scrapling.requestcatcher.com/put', data={'key': 'value'})
page = Fetcher.delete('https://scrapling.requestcatcher.com/delete')
```
Для асинхронных запросов замените импорт:
```python
from scrapling.fetchers import AsyncFetcher
page = await AsyncFetcher.get('https://scrapling.requestcatcher.com/get', stealthy_headers=True)
page = await AsyncFetcher.post('https://scrapling.requestcatcher.com/post', data={'key': 'value'}, proxy='http://username:password@localhost:8030')
page = await AsyncFetcher.put('https://scrapling.requestcatcher.com/put', data={'key': 'value'})
page = await AsyncFetcher.delete('https://scrapling.requestcatcher.com/delete')
```

!!! note "Примечания"

    1. Параметр `stealthy_headers` создаёт и использует заголовки настоящего браузера, включая Referer от Google. По умолчанию он включён.
    2. Параметр `impersonate` позволяет имитировать TLS-отпечаток определённой версии браузера.
    3. Параметр `http3` включает HTTP/3, чтобы запросы больше походили на запросы настоящего браузера.

Это лишь часть возможностей. Остальные описаны в [руководстве по HTTP-запросам](fetching/static.md).

### Динамическая загрузка {#dynamic-loading}
Scrapling справится и с динамическими сайтами!

`StealthyFetcher` предлагает много настроек для загрузки страниц через браузеры на основе Chromium.
```python
from scrapling.fetchers import StealthyFetcher
page = StealthyFetcher.fetch('https://quotes.toscrape.com/js/', disable_resources=True, block_ads=True, wait_selector='.quote')
print(len(page.css(".quote")))  # -> 10

# The async version of fetch
page = await StealthyFetcher.async_fetch('https://quotes.toscrape.com/js/', disable_resources=True, block_ads=True, wait_selector='.quote')
print(len(page.css(".quote")))  # -> 10
```
Он использует [Playwright](https://playwright.dev/python/) с изменениями, которые скрывают автоматизацию. Можно работать со встроенным Chromium, установленным Google Chrome через `real_chrome=True` или уже запущенным браузером через `cdp_url`.

### Обход защиты от ботов {#anti-bot-features}

Вот некоторые возможности:

1. Автоматическое прохождение всех видов Cloudflare Turnstile и Interstitial с `solve_cloudflare=True`.
2. Защита от утечек CDP Runtime и WebRTC.
3. Изоляция JavaScript, удаление многих признаков Playwright и защита от обнаружения по известным действиям ботов.
4. Добавление шума в Canvas, чтобы не дать определить отпечаток браузера.
5. Исправления против известных способов обнаружения режима без окна и настройка для защиты от проверки часового пояса.
6. И другие средства обхода защиты.

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

Все возможности и полный список аргументов описаны в [руководстве по браузеру](fetching/stealthy.md).

---

Так выглядит Scrapling в общих чертах. Продолжайте со следующего раздела, чтобы узнать больше.
