---
title: "Scrapling-Anleitung: Seiten auswerten, HTTP und Stealth-Browser"
description: "Lernen Sie Scrapling mit Beispielen für CSS, XPath, Textsuche, HTTP-Anfragen und Stealth-Browser kennen."
---

# Erste Schritte mit Scrapling {#get-started-with-scrapling}

## Wählen Sie Ihren Einstieg {#pick-your-path}

Sie wissen noch nicht, wo Sie anfangen sollen? Wählen Sie die passende Aufgabe:

| Ich möchte … | Hier beginnen |
|:---|:---|
| **HTML auswerten**, das ich bereits habe | [Elemente auswählen](parsing/selection.md): CSS, XPath und Textsuche |
| **Schnell eine Seite extrahieren** und eine Idee testen | Wählen und testen Sie einen [Fetcher](fetching/choosing.md), oder öffnen Sie die [interaktive Shell](cli/interactive-shell.md) |
| **Einen Crawler erstellen**, der mehr Seiten verarbeiten kann | [Spider](spiders/getting-started.md): paralleles Crawling mit mehreren Sitzungen, Pause und Fortsetzung |
| **Daten ohne eigenen Code extrahieren** | Nutzen Sie die [Extraktionsbefehle](cli/extract-commands.md), oder verbinden Sie den [MCP-Server](ai/mcp-server.md) mit Ihrem KI-Werkzeug |
| **Von einer anderen Bibliothek wechseln** | [Von BeautifulSoup](tutorials/migrating_from_beautifulsoup.md) oder [Vergleich mit Scrapy](spiders/architecture.md#comparison-with-scrapy) |

---

Zuerst werten wir Seiten aus. Danach rufen wir Seiten mit Browsern ab, senden Anfragen und werten die Antworten aus.

Für die Beispiele auf dieser Seite verwenden wir dieses von ChatGPT erstellte HTML-Dokument:
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
Laden Sie zuerst das HTML von oben:
```python
import re
from scrapling.parser import Selector
page = Selector(html_doc)
page  # <data='<html><head><title>Complex Web Page</tit...'>
```
Rufen Sie den gesamten Text der Seite ab, auch den Text verschachtelter Elemente:
```python
page.get_all_text(ignore_tags=('script', 'style'))
# 'Complex Web Page\nHome\nAbout\nContact\nProducts\nProduct 1\nThis is product 1\n$10.99\nIn stock: 5\nProduct 2\nThis is product 2\n$20.99\nIn stock: 3\nProduct 3\nThis is product 3\n$15.99\nOut of stock\nCustomer Reviews\nGreat product!\nJohn Doe\nGood value for money.\nJane Smith'
```

## Elemente suchen {#finding-elements}
Sie können verschiedene Methoden kombinieren, um die benötigten Elemente zu finden.

Suchen Sie das erste HTML-Element `section`:
```python
section_element = page.find('section')
# <data='<section id="products" schema='{"jsonabl...' parent='<main><section id="products" schema='{"j...'>
```
Suchen Sie alle `section`-Elemente:
```python
section_elements = page.find_all('section')
# [<data='<section id="products" schema='{"jsonabl...' parent='<main><section id="products" schema='{"j...'>, <data='<section id="reviews"><h2>Customer Revie...' parent='<main><section id="products" schema='{"j...'>]
```
Suchen Sie alle `section`-Elemente, deren Attribut `id` den Wert `products` hat:
```python
section_elements = page.find_all('section', {'id':"products"})
# Same as
section_elements = page.find_all('section', id="products")
# [<data='<section id="products" schema='{"jsonabl...' parent='<main><section id="products" schema='{"j...'>]
```
Suchen Sie alle `section`-Elemente, deren Attribut `id` den Text `product` enthält:
```python
section_elements = page.find_all('section', {'id*':"product"})
```
Suchen Sie `h3`-Elemente, deren Text zum regulären Ausdruck `Product \d` passt:
```python
page.find_all('h3', re.compile(r'Product \d'))
# [<data='<h3>Product 1</h3>' parent='<article class="product" data-id="1"><h3...'>, <data='<h3>Product 2</h3>' parent='<article class="product" data-id="2"><h3...'>, <data='<h3>Product 3</h3>' parent='<article class="product" data-id="3"><h3...'>]
```
Suchen Sie `h3`- und `h2`-Elemente, deren Text zum regulären Ausdruck `Product` passt:
```python
page.find_all(['h3', 'h2'], re.compile(r'Product'))
# [<data='<h3>Product 1</h3>' parent='<article class="product" data-id="1"><h3...'>, <data='<h3>Product 2</h3>' parent='<article class="product" data-id="2"><h3...'>, <data='<h3>Product 3</h3>' parent='<article class="product" data-id="3"><h3...'>, <data='<h2>Products</h2>' parent='<section id="products" schema='{"jsonabl...'>]
```
Suchen Sie Elemente, deren Text genau `Products` ist. Leerraum wird dabei nicht berücksichtigt:
```python
page.find_by_text('Products', first_match=False)
# [<data='<h2>Products</h2>' parent='<section id="products" schema='{"jsonabl...'>]
```
Oder suchen Sie Elemente, deren Text zum regulären Ausdruck `Product \d` passt:
```python
page.find_by_regex(r'Product \d', first_match=False)
# [<data='<h3>Product 1</h3>' parent='<article class="product" data-id="1"><h3...'>, <data='<h3>Product 2</h3>' parent='<article class="product" data-id="2"><h3...'>, <data='<h3>Product 3</h3>' parent='<article class="product" data-id="3"><h3...'>]
```
Suchen Sie Elemente, die dem ausgewählten Element ähneln:
```python
target_element = page.find_by_regex(r'Product \d', first_match=True)
# <data='<h3>Product 1</h3>' parent='<article class="product" data-id="1"><h3...'>
target_element.find_similar()
# [<data='<h3>Product 2</h3>' parent='<article class="product" data-id="2"><h3...'>, <data='<h3>Product 3</h3>' parent='<article class="product" data-id="3"><h3...'>]
```
Suchen Sie das erste Element, das zu einem CSS-Selektor passt:
```python
page.css('.product-list [data-id="1"]')[0]
# <data='<article class="product" data-id="1"><h3...' parent='<div class="product-list"> <article clas...'>
```
Suchen Sie alle Elemente, die zu einem CSS-Selektor passen:
```python
page.css('.product-list article')
# [<data='<article class="product" data-id="1"><h3...' parent='<div class="product-list"> <article clas...'>, <data='<article class="product" data-id="2"><h3...' parent='<div class="product-list"> <article clas...'>, <data='<article class="product" data-id="3"><h3...' parent='<div class="product-list"> <article clas...'>]
```
Suchen Sie das erste Element, das zu einem XPath-Selektor passt:
```python
page.xpath("//*[@id='products']/div/article")[0]
# <data='<article class="product" data-id="1"><h3...' parent='<div class="product-list"> <article clas...'>
```
Suchen Sie alle Elemente, die zu einem XPath-Selektor passen:
```python
page.xpath("//*[@id='products']/div/article")
# [<data='<article class="product" data-id="1"><h3...' parent='<div class="product-list"> <article clas...'>, <data='<article class="product" data-id="2"><h3...' parent='<div class="product-list"> <article clas...'>, <data='<article class="product" data-id="3"><h3...' parent='<div class="product-list"> <article clas...'>]
```

Das sind die Grundfunktionen. Weitere Optionen dieser Auswahlmethoden folgen später.
## Daten der Elemente lesen {#accessing-elements-data}
So lesen Sie die Daten:
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

## Navigation {#navigation}
Verwenden Sie die zuvor gefundenen Elemente:

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
Um über das Elternelement hinauszugehen, können Sie alle Vorfahren eines Elements durchlaufen:
```python
for ancestor in section_element.iterancestors():
    print(ancestor.tag)
```
Sie können auch einen Vorfahren suchen, der eine Bedingung erfüllt. Übergeben Sie eine Funktion, die ein `Selector`-Objekt erhält und `True` zurückgibt, wenn es die Bedingung erfüllt, sonst `False`:
```pycon
>>> section_element.find_ancestor(lambda ancestor: ancestor.css('nav'))
<data='<body> <header><nav><ul><li> <a href="#h...' parent='<html><head><title>Complex Web Page</tit...'>
```

## Webseiten abrufen {#fetching-websites}
Statt HTML an Scrapling zu übergeben, können Sie die Antwort einer Website über HTTP-Anfragen oder einen Browser abrufen.

Wählen Sie den Fetcher, der zu Ihrer Aufgabe passt.

### HTTP-Anfragen {#http-requests}
Importieren und verwenden Sie die Klasse `Fetcher`, um HTTP-Anfragen zu senden:
```python
from scrapling.fetchers import Fetcher
page = Fetcher.get('https://scrapling.requestcatcher.com/get', impersonate="chrome")
```
Diese Beispiele zeigen die verschiedenen HTTP-Methoden:
```python
from scrapling.fetchers import Fetcher
page = Fetcher.get('https://scrapling.requestcatcher.com/get', stealthy_headers=True)
page = Fetcher.post('https://scrapling.requestcatcher.com/post', data={'key': 'value'}, proxy='http://username:password@localhost:8030')
page = Fetcher.put('https://scrapling.requestcatcher.com/put', data={'key': 'value'})
page = Fetcher.delete('https://scrapling.requestcatcher.com/delete')
```
Für asynchrone Anfragen ändern Sie den Import:
```python
from scrapling.fetchers import AsyncFetcher
page = await AsyncFetcher.get('https://scrapling.requestcatcher.com/get', stealthy_headers=True)
page = await AsyncFetcher.post('https://scrapling.requestcatcher.com/post', data={'key': 'value'}, proxy='http://username:password@localhost:8030')
page = await AsyncFetcher.put('https://scrapling.requestcatcher.com/put', data={'key': 'value'})
page = await AsyncFetcher.delete('https://scrapling.requestcatcher.com/delete')
```

!!! note "Hinweise"

    1. `stealthy_headers` erzeugt echte Browser-Header, einschließlich eines Google-Referers. Die Option ist standardmäßig aktiv.
    2. Mit `impersonate` können Sie den TLS-Fingerprint einer bestimmten Browserversion nachbilden.
    3. `http3` aktiviert HTTP/3, damit die Anfragen denen eines echten Browsers stärker ähneln.

Weitere Optionen finden Sie in der [Anleitung zu HTTP-Anfragen](fetching/static.md).

### Dynamisches Laden {#dynamic-loading}
Sie können auch mit Websites arbeiten, die ihre Inhalte über JavaScript laden.

`StealthyFetcher` bietet viele Optionen zum Abrufen und Laden von Seiten mit Browsern auf Chromium-Basis.
```python
from scrapling.fetchers import StealthyFetcher
page = StealthyFetcher.fetch('https://quotes.toscrape.com/js/', disable_resources=True, block_ads=True, wait_selector='.quote')
print(len(page.css(".quote")))  # -> 10

# The async version of fetch
page = await StealthyFetcher.async_fetch('https://quotes.toscrape.com/js/', disable_resources=True, block_ads=True, wait_selector='.quote')
print(len(page.css(".quote")))  # -> 10
```
Er nutzt [Playwright](https://playwright.dev/python/) mit Änderungen, die die Automatisierung verbergen. Verwenden Sie das mitgelieferte Chromium, Ihr installiertes Google Chrome mit `real_chrome=True` oder einen laufenden Browser über `cdp_url`.

### Funktionen gegen Bot-Erkennung {#anti-bot-features}

Dazu gehören:

1. Löst verschiedene Arten von Cloudflare Turnstile und Interstitial automatisch mit `solve_cloudflare=True`.
2. Verhindert Lecks über die CDP-Runtime und WebRTC.
3. Isoliert die JavaScript-Ausführung, entfernt viele Spuren von Playwright und verhindert die Erkennung einiger bekannter Bot-Verhaltensweisen.
4. Fügt dem Canvas Rauschen hinzu, damit er nicht als Browser-Fingerprint verwendet werden kann.
5. Behebt bekannte Möglichkeiten, Browser ohne grafische Oberfläche zu erkennen, und kann eine Erkennung durch abweichende Zeitzonen verhindern.
6. Bietet weitere Optionen, um Erkennung zu vermeiden.

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

Details und die vollständige Parameterliste stehen in der [Browser-Anleitung](fetching/stealthy.md).

---

Das war ein Überblick über Scrapling. Im nächsten Abschnitt lernen Sie weitere Funktionen kennen.
