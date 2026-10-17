---
title: "Guide de Scrapling : analyse de pages, HTTP et navigateurs furtifs"
description: "Découvrez Scrapling avec des exemples de CSS, XPath, recherche de texte, requêtes HTTP et navigateurs furtifs."
---

# Premiers pas avec Scrapling {#get-started-with-scrapling}

## Choisissez par où commencer {#pick-your-path}

Vous ne savez pas par où commencer ? Choisissez ce que vous voulez faire :

| Je veux… | Commencez ici |
|:---|:---|
| **Analyser du HTML** que j’ai déjà | [Sélection d’éléments](parsing/selection.md) : CSS, XPath et recherche par texte |
| **Extraire une page rapidement** et tester une idée | Choisissez un [fetcher](fetching/choosing.md) et essayez-le, ou ouvrez le [shell interactif](cli/interactive-shell.md) |
| **Créer un crawler** capable de traiter plus de pages | [Spiders](spiders/getting-started.md) : exploration simultanée avec plusieurs sessions, pause et reprise |
| **Extraire des données sans écrire de code** | Utilisez les [commandes d’extraction](cli/extract-commands.md) ou connectez le [serveur MCP](ai/mcp-server.md) à votre outil d’IA |
| **Migrer** depuis une autre bibliothèque | [Depuis BeautifulSoup](tutorials/migrating_from_beautifulsoup.md) ou [comparaison avec Scrapy](spiders/architecture.md#comparison-with-scrapy) |

---

Nous allons d’abord analyser des pages. Ensuite, nous récupérerons des pages avec des navigateurs, enverrons des requêtes et analyserons les réponses.

Nous utiliserons ce document HTML généré par ChatGPT dans les exemples de cette page :
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
Commencez par charger le HTML précédent :
```python
import re
from scrapling.parser import Selector
page = Selector(html_doc)
page  # <data='<html><head><title>Complex Web Page</tit...'>
```
Récupérez tout le texte de la page, y compris celui des éléments imbriqués :
```python
page.get_all_text(ignore_tags=('script', 'style'))
# 'Complex Web Page\nHome\nAbout\nContact\nProducts\nProduct 1\nThis is product 1\n$10.99\nIn stock: 5\nProduct 2\nThis is product 2\n$20.99\nIn stock: 3\nProduct 3\nThis is product 3\n$15.99\nOut of stock\nCustomer Reviews\nGreat product!\nJohn Doe\nGood value for money.\nJane Smith'
```

## Rechercher des éléments {#finding-elements}
Vous pouvez combiner plusieurs méthodes pour trouver les éléments dont vous avez besoin.

Trouvez le premier élément HTML `section` :
```python
section_element = page.find('section')
# <data='<section id="products" schema='{"jsonabl...' parent='<main><section id="products" schema='{"j...'>
```
Trouvez tous les éléments `section` :
```python
section_elements = page.find_all('section')
# [<data='<section id="products" schema='{"jsonabl...' parent='<main><section id="products" schema='{"j...'>, <data='<section id="reviews"><h2>Customer Revie...' parent='<main><section id="products" schema='{"j...'>]
```
Trouvez tous les éléments `section` dont l’attribut `id` vaut `products` :
```python
section_elements = page.find_all('section', {'id':"products"})
# Same as
section_elements = page.find_all('section', id="products")
# [<data='<section id="products" schema='{"jsonabl...' parent='<main><section id="products" schema='{"j...'>]
```
Trouvez tous les éléments `section` dont l’attribut `id` contient `product` :
```python
section_elements = page.find_all('section', {'id*':"product"})
```
Trouvez les éléments `h3` dont le texte correspond à l’expression régulière `Product \d` :
```python
page.find_all('h3', re.compile(r'Product \d'))
# [<data='<h3>Product 1</h3>' parent='<article class="product" data-id="1"><h3...'>, <data='<h3>Product 2</h3>' parent='<article class="product" data-id="2"><h3...'>, <data='<h3>Product 3</h3>' parent='<article class="product" data-id="3"><h3...'>]
```
Trouvez les éléments `h3` et `h2` dont le texte correspond à l’expression régulière `Product` :
```python
page.find_all(['h3', 'h2'], re.compile(r'Product'))
# [<data='<h3>Product 1</h3>' parent='<article class="product" data-id="1"><h3...'>, <data='<h3>Product 2</h3>' parent='<article class="product" data-id="2"><h3...'>, <data='<h3>Product 3</h3>' parent='<article class="product" data-id="3"><h3...'>, <data='<h2>Products</h2>' parent='<section id="products" schema='{"jsonabl...'>]
```
Trouvez les éléments dont le texte est exactement `Products`. Les espaces ne sont pas pris en compte :
```python
page.find_by_text('Products', first_match=False)
# [<data='<h2>Products</h2>' parent='<section id="products" schema='{"jsonabl...'>]
```
Ou trouvez les éléments dont le texte correspond à l’expression régulière `Product \d` :
```python
page.find_by_regex(r'Product \d', first_match=False)
# [<data='<h3>Product 1</h3>' parent='<article class="product" data-id="1"><h3...'>, <data='<h3>Product 2</h3>' parent='<article class="product" data-id="2"><h3...'>, <data='<h3>Product 3</h3>' parent='<article class="product" data-id="3"><h3...'>]
```
Trouvez des éléments similaires à celui que vous avez choisi :
```python
target_element = page.find_by_regex(r'Product \d', first_match=True)
# <data='<h3>Product 1</h3>' parent='<article class="product" data-id="1"><h3...'>
target_element.find_similar()
# [<data='<h3>Product 2</h3>' parent='<article class="product" data-id="2"><h3...'>, <data='<h3>Product 3</h3>' parent='<article class="product" data-id="3"><h3...'>]
```
Trouvez le premier élément qui correspond à un sélecteur CSS :
```python
page.css('.product-list [data-id="1"]')[0]
# <data='<article class="product" data-id="1"><h3...' parent='<div class="product-list"> <article clas...'>
```
Trouvez tous les éléments qui correspondent à un sélecteur CSS :
```python
page.css('.product-list article')
# [<data='<article class="product" data-id="1"><h3...' parent='<div class="product-list"> <article clas...'>, <data='<article class="product" data-id="2"><h3...' parent='<div class="product-list"> <article clas...'>, <data='<article class="product" data-id="3"><h3...' parent='<div class="product-list"> <article clas...'>]
```
Trouvez le premier élément qui correspond à un sélecteur XPath :
```python
page.xpath("//*[@id='products']/div/article")[0]
# <data='<article class="product" data-id="1"><h3...' parent='<div class="product-list"> <article clas...'>
```
Trouvez tous les éléments qui correspondent à un sélecteur XPath :
```python
page.xpath("//*[@id='products']/div/article")
# [<data='<article class="product" data-id="1"><h3...' parent='<div class="product-list"> <article clas...'>, <data='<article class="product" data-id="2"><h3...' parent='<div class="product-list"> <article clas...'>, <data='<article class="product" data-id="3"><h3...' parent='<div class="product-list"> <article clas...'>]
```

Ce sont les usages de base. Nous verrons d’autres options de ces méthodes de sélection plus loin.
## Lire les données des éléments {#accessing-elements-data}
Vous pouvez lire les données ainsi :
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
Utilisez les éléments trouvés précédemment :

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
Pour aller au-delà du parent d’un élément, vous pouvez parcourir tous ses ancêtres :
```python
for ancestor in section_element.iterancestors():
    print(ancestor.tag)
```
Vous pouvez aussi chercher un ancêtre qui remplit une condition. Passez une fonction qui reçoit un objet `Selector` et renvoie `True` s’il remplit la condition, ou `False` sinon :
```pycon
>>> section_element.find_ancestor(lambda ancestor: ancestor.css('nav'))
<data='<body> <header><nav><ul><li> <a href="#h...' parent='<html><head><title>Complex Web Page</tit...'>
```

## Récupérer des pages web {#fetching-websites}
Au lieu de fournir du HTML à Scrapling, vous pouvez récupérer la réponse d’un site par des requêtes HTTP ou un navigateur.

Choisissez le fetcher adapté à votre cas.

### Requêtes HTTP {#http-requests}
Pour envoyer des requêtes HTTP, importez et utilisez la classe `Fetcher` :
```python
from scrapling.fetchers import Fetcher
page = Fetcher.get('https://scrapling.requestcatcher.com/get', impersonate="chrome")
```
Ces exemples montrent comment utiliser les différentes méthodes HTTP :
```python
from scrapling.fetchers import Fetcher
page = Fetcher.get('https://scrapling.requestcatcher.com/get', stealthy_headers=True)
page = Fetcher.post('https://scrapling.requestcatcher.com/post', data={'key': 'value'}, proxy='http://username:password@localhost:8030')
page = Fetcher.put('https://scrapling.requestcatcher.com/put', data={'key': 'value'})
page = Fetcher.delete('https://scrapling.requestcatcher.com/delete')
```
Pour envoyer des requêtes asynchrones, changez l’importation :
```python
from scrapling.fetchers import AsyncFetcher
page = await AsyncFetcher.get('https://scrapling.requestcatcher.com/get', stealthy_headers=True)
page = await AsyncFetcher.post('https://scrapling.requestcatcher.com/post', data={'key': 'value'}, proxy='http://username:password@localhost:8030')
page = await AsyncFetcher.put('https://scrapling.requestcatcher.com/put', data={'key': 'value'})
page = await AsyncFetcher.delete('https://scrapling.requestcatcher.com/delete')
```

!!! note "Notes"

    1. `stealthy_headers` génère des en-têtes de navigateur réels, dont un en-tête de provenance Google. Cette option est activée par défaut.
    2. `impersonate` permet d’imiter l’empreinte TLS d’une version précise de navigateur.
    3. `http3` active HTTP/3 pour rapprocher les requêtes de celles d’un vrai navigateur.

Consultez les autres options dans le [guide des requêtes HTTP](fetching/static.md).

### Chargement dynamique {#dynamic-loading}
Vous pouvez aussi travailler avec des sites qui chargent leur contenu par JavaScript.

`StealthyFetcher` propose de nombreuses options pour récupérer et charger des pages avec des navigateurs basés sur Chromium.
```python
from scrapling.fetchers import StealthyFetcher
page = StealthyFetcher.fetch('https://quotes.toscrape.com/js/', disable_resources=True, block_ads=True, wait_selector='.quote')
print(len(page.css(".quote")))  # -> 10

# The async version of fetch
page = await StealthyFetcher.async_fetch('https://quotes.toscrape.com/js/', disable_resources=True, block_ads=True, wait_selector='.quote')
print(len(page.css(".quote")))  # -> 10
```
Il utilise [Playwright](https://playwright.dev/python/) avec des changements pour masquer l’automatisation. Utilisez le Chromium inclus, votre Google Chrome installé avec `real_chrome=True` ou un navigateur déjà ouvert via `cdp_url`.

### Fonctions contre la détection des bots {#anti-bot-features}

Voici quelques-unes de ses fonctions :

1. Franchit automatiquement les différents types de Cloudflare Turnstile et Interstitial avec `solve_cloudflare=True`.
2. Évite les fuites de CDP runtime et WebRTC.
3. Isole l’exécution de JavaScript, supprime de nombreuses traces de Playwright et évite la détection de certains comportements connus des bots.
4. Ajoute du bruit au canvas pour empêcher son usage comme empreinte du navigateur.
5. Corrige les méthodes connues de détection des navigateurs sans interface graphique et permet d’éviter la détection par les différences de fuseau horaire.
6. Inclut d’autres options pour éviter la détection.

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

Consultez le [guide de navigation](fetching/stealthy.md) pour connaître les détails et la liste complète des paramètres.

---

Vous avez maintenant une vue d’ensemble de Scrapling. Passez à la section suivante pour découvrir d’autres fonctions.
