---
title: "Guia do Scrapling: análise de páginas, HTTP e navegadores furtivos"
description: "Conheça o Scrapling com exemplos de CSS, XPath, busca de texto, solicitações HTTP e navegadores furtivos."
---

# Primeiros passos com o Scrapling {#get-started-with-scrapling}

## Escolha por onde começar {#pick-your-path}

Não sabe por onde começar? Escolha a opção que corresponde ao que você quer fazer:

| Quero... | Comece aqui |
|:---|:---|
| **Analisar HTML** que já tenho | [Seleção de elementos](parsing/selection.md): CSS, XPath e busca por texto |
| **Extrair uma página rápido** e testar uma ideia | Escolha um [fetcher](fetching/choosing.md) e experimente, ou abra o [shell interativo](cli/interactive-shell.md) |
| **Criar um crawler** que consiga lidar com mais trabalho | [Spiders](spiders/getting-started.md): rastreamento simultâneo com várias sessões, pausa e retomada |
| **Extrair dados sem escrever código** | Use os [comandos de extração](cli/extract-commands.md) ou conecte o [servidor MCP](ai/mcp-server.md) à sua ferramenta de IA |
| **Migrar** de outra biblioteca | [De BeautifulSoup](tutorials/migrating_from_beautifulsoup.md) ou [comparação com Scrapy](spiders/architecture.md#comparison-with-scrapy) |

---

Primeiro vamos ver como analisar páginas. Depois vamos obter páginas com navegadores, enviar solicitações e analisar as respostas.

Usaremos este documento HTML gerado pelo ChatGPT nos exemplos desta página:
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
Comece carregando o HTML anterior:
```python
import re
from scrapling.parser import Selector
page = Selector(html_doc)
page  # <data='<html><head><title>Complex Web Page</tit...'>
```
Obtenha todo o texto da página, incluindo o dos elementos internos:
```python
page.get_all_text(ignore_tags=('script', 'style'))
# 'Complex Web Page\nHome\nAbout\nContact\nProducts\nProduct 1\nThis is product 1\n$10.99\nIn stock: 5\nProduct 2\nThis is product 2\n$20.99\nIn stock: 3\nProduct 3\nThis is product 3\n$15.99\nOut of stock\nCustomer Reviews\nGreat product!\nJohn Doe\nGood value for money.\nJane Smith'
```

## Buscar elementos {#finding-elements}
Você pode combinar métodos diferentes para encontrar os elementos de que precisa.

Busque o primeiro elemento HTML `section`:
```python
section_element = page.find('section')
# <data='<section id="products" schema='{"jsonabl...' parent='<main><section id="products" schema='{"j...'>
```
Busque todos os elementos `section`:
```python
section_elements = page.find_all('section')
# [<data='<section id="products" schema='{"jsonabl...' parent='<main><section id="products" schema='{"j...'>, <data='<section id="reviews"><h2>Customer Revie...' parent='<main><section id="products" schema='{"j...'>]
```
Busque todos os elementos `section` cujo atributo `id` seja `products`:
```python
section_elements = page.find_all('section', {'id':"products"})
# Same as
section_elements = page.find_all('section', id="products")
# [<data='<section id="products" schema='{"jsonabl...' parent='<main><section id="products" schema='{"j...'>]
```
Busque todos os elementos `section` cujo atributo `id` contenha `product`:
```python
section_elements = page.find_all('section', {'id*':"product"})
```
Busque os elementos `h3` cujo texto corresponda à expressão regular `Product \d`:
```python
page.find_all('h3', re.compile(r'Product \d'))
# [<data='<h3>Product 1</h3>' parent='<article class="product" data-id="1"><h3...'>, <data='<h3>Product 2</h3>' parent='<article class="product" data-id="2"><h3...'>, <data='<h3>Product 3</h3>' parent='<article class="product" data-id="3"><h3...'>]
```
Busque os elementos `h3` e `h2` cujo texto corresponda à expressão regular `Product`:
```python
page.find_all(['h3', 'h2'], re.compile(r'Product'))
# [<data='<h3>Product 1</h3>' parent='<article class="product" data-id="1"><h3...'>, <data='<h3>Product 2</h3>' parent='<article class="product" data-id="2"><h3...'>, <data='<h3>Product 3</h3>' parent='<article class="product" data-id="3"><h3...'>, <data='<h2>Products</h2>' parent='<section id="products" schema='{"jsonabl...'>]
```
Busque os elementos cujo texto seja exatamente `Products`. Os espaços em branco são ignorados:
```python
page.find_by_text('Products', first_match=False)
# [<data='<h2>Products</h2>' parent='<section id="products" schema='{"jsonabl...'>]
```
Ou busque os elementos cujo texto corresponda à expressão regular `Product \d`:
```python
page.find_by_regex(r'Product \d', first_match=False)
# [<data='<h3>Product 1</h3>' parent='<article class="product" data-id="1"><h3...'>, <data='<h3>Product 2</h3>' parent='<article class="product" data-id="2"><h3...'>, <data='<h3>Product 3</h3>' parent='<article class="product" data-id="3"><h3...'>]
```
Busque elementos semelhantes ao que você escolheu:
```python
target_element = page.find_by_regex(r'Product \d', first_match=True)
# <data='<h3>Product 1</h3>' parent='<article class="product" data-id="1"><h3...'>
target_element.find_similar()
# [<data='<h3>Product 2</h3>' parent='<article class="product" data-id="2"><h3...'>, <data='<h3>Product 3</h3>' parent='<article class="product" data-id="3"><h3...'>]
```
Busque o primeiro elemento que corresponda a um seletor CSS:
```python
page.css('.product-list [data-id="1"]')[0]
# <data='<article class="product" data-id="1"><h3...' parent='<div class="product-list"> <article clas...'>
```
Busque todos os elementos que correspondam a um seletor CSS:
```python
page.css('.product-list article')
# [<data='<article class="product" data-id="1"><h3...' parent='<div class="product-list"> <article clas...'>, <data='<article class="product" data-id="2"><h3...' parent='<div class="product-list"> <article clas...'>, <data='<article class="product" data-id="3"><h3...' parent='<div class="product-list"> <article clas...'>]
```
Busque o primeiro elemento que corresponda a um seletor XPath:
```python
page.xpath("//*[@id='products']/div/article")[0]
# <data='<article class="product" data-id="1"><h3...' parent='<div class="product-list"> <article clas...'>
```
Busque todos os elementos que correspondam a um seletor XPath:
```python
page.xpath("//*[@id='products']/div/article")
# [<data='<article class="product" data-id="1"><h3...' parent='<div class="product-list"> <article clas...'>, <data='<article class="product" data-id="2"><h3...' parent='<div class="product-list"> <article clas...'>, <data='<article class="product" data-id="3"><h3...' parent='<div class="product-list"> <article clas...'>]
```

Esses são os usos básicos. Mais adiante veremos outras opções desses métodos de seleção.
## Ler os dados dos elementos {#accessing-elements-data}
Você pode ler os dados assim:
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

## Navegação {#navigation}
Use os elementos que encontramos antes:

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
Para ir além do pai de um elemento, você pode percorrer todos os seus ancestrais:
```python
for ancestor in section_element.iterancestors():
    print(ancestor.tag)
```
Você também pode buscar um ancestral que atenda a uma condição. Passe uma função que receba um objeto `Selector` e retorne `True` se ele atender à condição, ou `False` caso contrário:
```pycon
>>> section_element.find_ancestor(lambda ancestor: ancestor.css('nav'))
<data='<body> <header><nav><ul><li> <a href="#h...' parent='<html><head><title>Complex Web Page</tit...'>
```

## Obter páginas da web {#fetching-websites}
Em vez de passar HTML ao Scrapling, você pode obter a resposta de um site por solicitações HTTP ou por um navegador.

Escolha o fetcher que atende ao seu caso.

### Solicitações HTTP {#http-requests}
Para enviar solicitações HTTP, importe e use a classe `Fetcher`:
```python
from scrapling.fetchers import Fetcher
page = Fetcher.get('https://scrapling.requestcatcher.com/get', impersonate="chrome")
```
Estes exemplos mostram como usar os diferentes métodos HTTP:
```python
from scrapling.fetchers import Fetcher
page = Fetcher.get('https://scrapling.requestcatcher.com/get', stealthy_headers=True)
page = Fetcher.post('https://scrapling.requestcatcher.com/post', data={'key': 'value'}, proxy='http://username:password@localhost:8030')
page = Fetcher.put('https://scrapling.requestcatcher.com/put', data={'key': 'value'})
page = Fetcher.delete('https://scrapling.requestcatcher.com/delete')
```
Para enviar solicitações assíncronas, mude a importação:
```python
from scrapling.fetchers import AsyncFetcher
page = await AsyncFetcher.get('https://scrapling.requestcatcher.com/get', stealthy_headers=True)
page = await AsyncFetcher.post('https://scrapling.requestcatcher.com/post', data={'key': 'value'}, proxy='http://username:password@localhost:8030')
page = await AsyncFetcher.put('https://scrapling.requestcatcher.com/put', data={'key': 'value'})
page = await AsyncFetcher.delete('https://scrapling.requestcatcher.com/delete')
```

!!! note "Notas"

    1. `stealthy_headers` gera cabeçalhos reais de navegador, incluindo um cabeçalho de referência do Google. Está ativado por padrão.
    2. `impersonate` permite imitar a impressão digital TLS de uma versão específica de navegador.
    3. `http3` ativa HTTP/3 para que as solicitações se pareçam mais com as de um navegador real.

Veja as outras opções no [guia de solicitações HTTP](fetching/static.md).

### Carregamento dinâmico {#dynamic-loading}
Você também pode trabalhar com sites que carregam o conteúdo por JavaScript.

`StealthyFetcher` tem várias opções para obter e carregar páginas com navegadores baseados em Chromium.
```python
from scrapling.fetchers import StealthyFetcher
page = StealthyFetcher.fetch('https://quotes.toscrape.com/js/', disable_resources=True, block_ads=True, wait_selector='.quote')
print(len(page.css(".quote")))  # -> 10

# The async version of fetch
page = await StealthyFetcher.async_fetch('https://quotes.toscrape.com/js/', disable_resources=True, block_ads=True, wait_selector='.quote')
print(len(page.css(".quote")))  # -> 10
```
Ele usa [Playwright](https://playwright.dev/python/) com mudanças para ocultar a automação. Use o Chromium incluído, seu Google Chrome instalado com `real_chrome=True` ou um navegador em execução por meio de `cdp_url`.

### Recursos contra a detecção de bots {#anti-bot-features}

Estes são alguns dos recursos:

1. Supera automaticamente os diferentes tipos de Cloudflare Turnstile e Interstitial com `solve_cloudflare=True`.
2. Evita vazamentos de CDP runtime e WebRTC.
3. Isola a execução de JavaScript, remove várias marcas do Playwright e evita a detecção de alguns comportamentos conhecidos de bots.
4. Adiciona ruído ao canvas para evitar seu uso como impressão digital do navegador.
5. Corrige formas conhecidas de detectar navegadores sem interface gráfica e permite evitar a detecção por diferenças de fuso horário.
6. Inclui outras opções para evitar a detecção.

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

Veja o [guia de navegação](fetching/stealthy.md) para conhecer todos os detalhes e a lista completa de parâmetros.

---

Esta foi uma visão geral do Scrapling. Continue na próxima seção para conhecer mais recursos.
