---
title: "Extrae datos HTML con CSS, XPath, texto y regex"
description: "Selecciona elementos HTML con CSS, XPath, texto y regex. Encuentra elementos parecidos y extrae datos con ejemplos de Scrapling."
---

# Buscar elementos {#querying-elements}
La clase `Selector` analiza HTML. Esto se debe a que la función adaptativa no funciona con XML. Para fuentes XML, RSS o Atom, usa [XMLFeedSpider](../spiders/generic-templates.md#xmlfeedspider). Usa un analizador XML y te entrega cada nodo de la fuente directamente.

Scrapling ofrece cinco formas principales de buscar elementos:

1. Selectores CSS3.
2. Selectores XPath.
3. Filtros o condiciones.
4. Un texto concreto dentro del contenido.
5. Una expresión regular que coincida con el contenido.

Hay otras formas indirectas de encontrar elementos, pero aquí veremos las principales. También veremos una función destacada: encontrar elementos parecidos a uno que ya tienes. Puedes ir directamente a [esa sección](#finding-similar-elements).

Si estás empezando con web scraping, no tienes mucha experiencia con selectores y quieres avanzar rápido, te recomiendo empezar por los métodos `find`/`find_all` [aquí](#filters-based-searching).

## Selectores CSS y XPath {#cssxpath-selectors}

### ¿Qué son los selectores CSS? {#what-are-css-selectors}
[CSS](https://en.wikipedia.org/wiki/CSS) es un lenguaje que aplica estilos a documentos HTML. Sus selectores indican a qué elementos se aplica cada estilo.

Scrapling admite selectores CSS3 según la [especificación del W3C](http://www.w3.org/TR/2011/REC-css3-selectors-20110929/). Usa `cssselect` para ello. Consulta los [selectores admitidos por cssselect](https://cssselect.readthedocs.io/en/latest/#supported-selectors), incluidas sus pseudofunciones y pseudoelementos.

Scrapling también incluye algunos pseudoelementos que no forman parte del estándar:

* Para seleccionar nodos de texto, usa ``::text``.
* Para seleccionar valores de atributos, usa ``::attr(name)``, donde name es el nombre del atributo.

Si vienes de Scrapy o Parsel, reconocerás la misma lógica. Así no tienes que aprender otra forma de usar los selectores :)

Para seleccionar con CSS, usa `css`, que devuelve `Selectors`. Usa `[0]` para obtener el primer elemento, o `.get()` / `.getall()` para extraer valores de los pseudoselectores de texto y atributos.

### ¿Qué son los selectores XPath? {#what-are-xpath-selectors}
[XPath](https://en.wikipedia.org/wiki/XPath) es un lenguaje para seleccionar nodos en documentos XML, y también funciona con HTML. Esta [guía rápida](https://devhints.io/xpath) sirve para aprender [XPath](https://en.wikipedia.org/wiki/XPath). Scrapling lo incorpora directamente mediante [lxml](https://lxml.de/).

Como con CSS, si vienes de Scrapy o Parsel encontrarás la misma lógica. Sin embargo, Scrapling no incluye la función XPath `has-class`. En su lugar, ofrece el método `has_class` para comprobar las clases de los elementos encontrados.

Para seleccionar con XPath, usa `xpath`. Sigue la misma lógica que el método CSS anterior.

> Los métodos `css` y `xpath` tienen otros argumentos relacionados con la función adaptativa. Los veremos en su propia página.

### Ejemplos de selectores {#selectors-examples}
Veamos algunos ejemplos equivalentes con CSS y XPath.

Selecciona todos los elementos de clase `product`:
```python
products = page.css('.product')
products = page.xpath('//*[@class="product"]')
```
!!! info "Nota"

    El XPath no será preciso si el elemento tiene otra clase. **Es mejor usar CSS para seleccionar por clase.**

Selecciona el primer elemento de clase `product`:
```python
product = page.css('.product')[0]
product = page.xpath('//*[@class="product"]')[0]
```
Obtén el texto del primer elemento con etiqueta `h1`:
```python
title = page.css('h1::text').get()
title = page.xpath('//h1//text()').get()
```
Es lo mismo que hacer esto:
```python
title = page.css('h1')[0].text
title = page.xpath('//h1')[0].text
```
Obtén el atributo `href` del primer elemento con etiqueta `a`:
```python
link = page.css('a::attr(href)').get()
link = page.xpath('//a/@href').get()
```
Selecciona el texto del primer `h1` que contenga `Phone` y esté dentro de un elemento de clase `product`:
```python
title = page.css('.product h1:contains("Phone")::text').get()
title = page.xpath('//*[@class="product"]//h1[contains(text(),"Phone")]/text()').get()
```
Puedes anidar y encadenar selectores siempre que devuelvan resultados:
```python
page.css('.product')[0].css('h1:contains("Phone")::text').get()
page.xpath('//*[@class="product"]')[0].xpath('.//h1[contains(text(),"Phone")]/text()').get()
page.xpath('//*[@class="product"]')[0].css('h1:contains("Phone")::text').get()
```
Usa `.//` para que XPath busque desde el elemento actual. Si empieza por `//`, busca en todo el documento, incluso después de seleccionar un producto.

Otro ejemplo:

Todos los enlaces que contienen 'image' en su atributo 'href':
```python
links = page.css('a[href*="image"]')
links = page.xpath('//a[contains(@href, "image")]')
for index, link in enumerate(links):
    link_value = link.attrib['href']  # Cleaner than link.css('::attr(href)').get()
    link_text = link.text
    print(f'Link number {index} points to this url {link_value} with text content as "{link_text}"')
```

## Selección por contenido de texto {#text-content-selection}
Scrapling permite buscar por el texto directo de cada elemento de dos formas:

1. Con `find_by_text`, busca elementos cuyo texto directo contenga el texto indicado. Ofrece varias opciones.
2. Con `find_by_regex`, busca elementos cuyo texto directo coincida con una expresión regular. También ofrece varias opciones.

Si sabes usar expresiones regulares, puedes hacer con `find_by_regex` lo mismo que con `find_by_text`. Ofrecemos ambos métodos para que todos puedan usarlos con facilidad.

El primer argumento de `find_by_text` es el texto que buscas. El de `find_by_regex` es la expresión regular. Ambos comparten estos argumentos:

* **first_match**: si es `True`, el valor por defecto, devuelve solo el primer resultado.
* **case_sensitive**: si es `True`, distingue entre mayúsculas y minúsculas.
* **clean_match**: si es `True`, reemplaza los espacios en blanco y los espacios seguidos por un solo espacio antes de comparar.

Por defecto, `find_by_text` busca una coincidencia exacta. El texto del elemento debe ser SOLO el texto indicado. Para cambiar esto, ofrece otro argumento:

* **partial**: al activarlo, `find_by_text` devuelve elementos que contengan el texto indicado, aunque tengan más texto.

!!! abstract "Nota"

    `find_by_regex` acepta tanto una cadena normal como una expresión regular compilada como primer argumento. Lo veremos en los ejemplos.

### Buscar elementos parecidos {#finding-similar-elements}
Una de las funciones más útiles de Scrapling es buscar elementos parecidos a uno que ya tienes. Está inspirada en AutoScraper, pero aquí funciona con elementos encontrados por cualquier método. Suele ser útil después de una búsqueda por texto, como ocurre en AutoScraper, por eso la explicamos aquí.

¿Cómo funciona?

Imagina que encuentras un producto por su título y quieres extraer los otros productos de la misma tabla o contenedor. Llama a `.find_similar()` sobre ese elemento y Scrapling hará lo siguiente:

1. Busca todos los elementos con la misma profundidad en el árbol DOM.
2. Descarta los que no tengan la misma etiqueta, etiqueta del padre y etiqueta del abuelo.
3. Es muy probable que los elementos restantes sean los que buscas. Como última comprobación, compara sus atributos y descarta los que no se parecen lo suficiente. Puedes ajustar el porcentaje de similitud, pero conviene mantener el valor por defecto salvo que no encuentre los elementos que necesitas.

Son varios pasos, pero ayudan a entender el método. Veremos ejemplos en la próxima sección. Estos son sus argumentos:

* **similarity_threshold**: controla la comparación de atributos del paso 3. El valor por defecto es 0.2, es decir, los atributos deben parecerse al menos un 20%. Con 0 desactivas esta comprobación. Antes de hacerlo, revisa los otros argumentos.
* **ignore_attributes**: nombres de atributos que se ignoran en la última comparación. El valor por defecto es `('href', 'src',)`, porque las URL pueden variar mucho entre elementos y no son una referencia fiable.
* **match_text**: si es `True`, también compara el texto del elemento en el paso 3. No suele ser necesario, aunque depende del caso.

Veamos los ejemplos.

### Ejemplos {#examples}
Estos ejemplos muestran búsquedas por texto y expresiones regulares.

Usaré la clase `Fetcher`, que explicaremos con detalle más adelante.
```python
from scrapling.fetchers import Fetcher
page = Fetcher.get('https://books.toscrape.com/index.html')
```
Busca el primer elemento cuyo texto coincida por completo con este texto:
```python
>>> page.find_by_text('Tipping the Velvet')
<data='<a href="catalogue/tipping-the-velvet_99...' parent='<h3><a href="catalogue/tipping-the-velve...'>
```
Combínalo con `page.urljoin` para convertir el `href` relativo en una URL completa:
```python
>>> page.find_by_text('Tipping the Velvet').attrib['href']
'catalogue/tipping-the-velvet_999/index.html'
>>> page.urljoin(page.find_by_text('Tipping the Velvet').attrib['href'])
'https://books.toscrape.com/catalogue/tipping-the-velvet_999/index.html'
```
Obtén todas las coincidencias, si hay varias. Fíjate en que devuelve una lista:
```python
>>> page.find_by_text('Tipping the Velvet', first_match=False)
[<data='<a href="catalogue/tipping-the-velvet_99...' parent='<h3><a href="catalogue/tipping-the-velve...'>]
```
Obtén todos los elementos que contengan la palabra `the`, mediante una coincidencia parcial:
```python
>>> results = page.find_by_text('the', partial=True, first_match=False)
>>> [i.text for i in results]
['A Light in the ...',
 'Tipping the Velvet',
 'The Requiem Red',
 'The Dirty Little Secrets ...',
 'The Coming Woman: A ...',
 'The Boys in the ...',
 'The Black Maria',
 'Mesaerion: The Best Science ...',
 "It's Only the Himalayas"]
```
La búsqueda no distingue entre mayúsculas y minúsculas. Por eso incluye `The` además de `the`. Limitemos los resultados a `the`:
```python
>>> results = page.find_by_text('the', partial=True, first_match=False, case_sensitive=True)
>>> [i.text for i in results]
['A Light in the ...',
 'Tipping the Velvet',
 'The Boys in the ...',
 "It's Only the Himalayas"]
```
Obtén el primer elemento cuyo texto coincida con esta expresión regular de precios:
```python
>>> page.find_by_regex(r'£[\d\.]+')
<data='<p class="price_color">£51.77</p>' parent='<div class="product_price"> <p class="pr...'>
>>> page.find_by_regex(r'£[\d\.]+').text
'£51.77'
```
También puedes pasar una expresión regular compilada. Scrapling detecta el tipo de entrada y la usa:
```python
>>> import re
>>> regex = re.compile(r'£[\d\.]+')
>>> page.find_by_regex(regex)
<data='<p class="price_color">£51.77</p>' parent='<div class="product_price"> <p class="pr...'>
>>> page.find_by_regex(regex).text
'£51.77'
```
Obtén todos los elementos que coincidan con la expresión regular:
```python
>>> page.find_by_regex(r'£[\d\.]+', first_match=False)
[<data='<p class="price_color">£51.77</p>' parent='<div class="product_price"> <p class="pr...'>,
 <data='<p class="price_color">£53.74</p>' parent='<div class="product_price"> <p class="pr...'>,
 <data='<p class="price_color">£50.10</p>' parent='<div class="product_price"> <p class="pr...'>,
 <data='<p class="price_color">£47.82</p>' parent='<div class="product_price"> <p class="pr...'>,
 ...]
```
Y así sucesivamente...

Busca todos los elementos parecidos al actual por su posición y sus atributos. En este caso, ignora el atributo 'title' al comparar:
```python
>>> element = page.find_by_text('Tipping the Velvet')
>>> element.find_similar(ignore_attributes=['title'])
[<data='<a href="catalogue/a-light-in-the-attic_...' parent='<h3><a href="catalogue/a-light-in-the-at...'>,
 <data='<a href="catalogue/soumission_998/index....' parent='<h3><a href="catalogue/soumission_998/in...'>,
 <data='<a href="catalogue/sharp-objects_997/ind...' parent='<h3><a href="catalogue/sharp-objects_997...'>,
...]
```
Hay 19 elementos en vez de 20 porque el elemento actual no se incluye en los resultados.
```python
>>> len(element.find_similar(ignore_attributes=['title']))
19
```
Obtén el atributo `href` de todos los elementos parecidos:
```python
>>> [
    element.attrib['href']
    for element in element.find_similar(ignore_attributes=['title'])
]
['catalogue/a-light-in-the-attic_1000/index.html',
 'catalogue/soumission_998/index.html',
 'catalogue/sharp-objects_997/index.html',
 ...]
```
Ahora un ejemplo algo más completo: extraer todos los datos de los libros usando ese elemento como punto de partida.
```python
>>> first_product = element.parent.parent
>>> for product in [first_product, *first_product.find_similar()]:
        print({
            "name": product.css('h3 a::text').get(),
            "price": product.css('.price_color')[0].re_first(r'[\d\.]+'),
            "stock": product.css('.availability::text').getall()[-1].clean()
        })
{'name': 'Tipping the Velvet', 'price': '53.74', 'stock': 'In stock'}
{'name': 'A Light in the ...', 'price': '51.77', 'stock': 'In stock'}
{'name': 'Soumission', 'price': '50.10', 'stock': 'In stock'}
{'name': 'Sharp Objects', 'price': '47.82', 'stock': 'In stock'}
...
```
### Ejemplos avanzados {#advanced-examples}
Veamos casos más completos de uso de `find_similar`.

Extraer productos de una tienda:
```python
def extract_product_grid(page):
    # Find the first product card
    first_product = page.find_by_text('Add to Cart').find_ancestor(
        lambda e: e.has_class('product-card')
    )

    # Find similar product cards
    products = [first_product, *first_product.find_similar()]

    return [
        {
            'name': p.css('h3::text').get(),
            'price': p.css('.price::text').re_first(r'\d+\.\d{2}'),
            'stock': 'In stock' in p.get_all_text(),
            'rating': p.css('.rating')[0].attrib.get('data-rating')
        }
        for p in products
    ]
```
Extraer filas de una tabla:
```python
def extract_table_data(page):
    # Find the first data row
    first_row = page.css('table tbody tr')[0]

    # Find similar rows
    rows = [first_row, *first_row.find_similar()]

    return [
        {
            'column1': row.css('td:nth-child(1)::text').get(),
            'column2': row.css('td:nth-child(2)::text').get(),
            'column3': row.css('td:nth-child(3)::text').get()
        }
        for row in rows
    ]
```
Extraer campos de un formulario:
```python
def extract_form_fields(page):
    # Find first form field container
    first_field = page.css('input')[0].find_ancestor(
        lambda e: e.has_class('form-field')
    )

    # Find similar field containers
    fields = [first_field, *first_field.find_similar()]

    return [
        {
            'label': f.css('label::text').get(),
            'type': f.css('input')[0].attrib.get('type'),
            'required': 'required' in f.css('input')[0].attrib
        }
        for f in fields
    ]
```
Extraer reseñas de un sitio:
```python
def extract_reviews(page):
    # Find first review
    first_review = page.find_by_text('Great product!')
    review_container = first_review.find_ancestor(
        lambda e: e.has_class('review')
    )
    
    # Find similar reviews
    all_reviews = [review_container, *review_container.find_similar()]
    
    return [
        {
            'text': r.css('.review-text::text').get(),
            'rating': r.attrib.get('data-rating'),
            'author': r.css('.reviewer::text').get()
        }
        for r in all_reviews
    ]
```
## Búsqueda por filtros {#filters-based-searching}
Este método es una de las mejores formas de buscar elementos en Scrapling. Es potente y suele resultar más fácil de aprender que los selectores para quienes empiezan con web scraping.

Inspirados en `find_all` de BeautifulSoup, los métodos `find_all` y `find` aceptan varios filtros y buscan los elementos que cumplen todas las condiciones.

Cada tipo de argumento se interpreta así:

* Una cadena es un nombre de etiqueta.
* Un iterable, como List, Tuple o Set, contiene nombres de etiquetas.
* Un diccionario relaciona los nombres de atributos HTML con sus valores.
* Una expresión regular filtra por contenido, como `find_by_regex`.
* Una función filtra los elementos.
* Un argumento con nombre representa un atributo HTML y su valor.

El método reúne todos los argumentos y aplica los filtros en cadena. Cada filtro recibe los resultados del anterior.

Los filtros se aplican a los elementos de la página o del elemento actual en este orden:

1. Recoge los elementos con los nombres de etiqueta indicados.
2. Busca los que cumplan todos los atributos indicados. Si ya se aplicó un filtro, solo revisa sus resultados.
3. Busca los que coincidan con todas las expresiones regulares. Si ya se aplicaron filtros, solo revisa sus resultados.
4. Busca los que cumplan todas las funciones. Si ya se aplicaron filtros, solo revisa sus resultados.

!!! note "Notas"

    1. El proceso empieza por el primer filtro disponible según el orden anterior. Si no pasas etiquetas, pero sí atributos, empieza por el paso 2.
    2. El orden en que pases los argumentos no importa. Solo se usa el orden explicado arriba.

Los ejemplos ayudan a verlo mejor :)

### Ejemplos {#examples_1}
```python
from scrapling.fetchers import Fetcher
page = Fetcher.get('https://quotes.toscrape.com/')
```
Busca todos los elementos con etiqueta `div`:
```python
>>> page.find_all('div')
[<data='<div class="container"> <div class="row...' parent='<body> <div class="container"> <div clas...'>,
 <data='<div class="row header-box"> <div class=...' parent='<div class="container"> <div class="row...'>,
...]
```
Busca todos los div cuya clase sea `quote`:
```python
>>> page.find_all('div', class_='quote')
[<data='<div class="quote" itemscope itemtype="h...' parent='<div class="col-md-8"> <div class="quote...'>,
 <data='<div class="quote" itemscope itemtype="h...' parent='<div class="col-md-8"> <div class="quote...'>,
...]
```
Lo mismo que antes:
```python
>>> page.find_all('div', {'class': 'quote'})
[<data='<div class="quote" itemscope itemtype="h...' parent='<div class="col-md-8"> <div class="quote...'>,
 <data='<div class="quote" itemscope itemtype="h...' parent='<div class="col-md-8"> <div class="quote...'>,
...]
```
Busca todos los elementos cuya clase sea `quote`:
```python
>>> page.find_all({'class': 'quote'})
[<data='<div class="quote" itemscope itemtype="h...' parent='<div class="col-md-8"> <div class="quote...'>,
 <data='<div class="quote" itemscope itemtype="h...' parent='<div class="col-md-8"> <div class="quote...'>,
...]
```
Busca todos los div cuya clase sea `quote` y que contengan un elemento `.text` con la palabra 'world':
```python
>>> page.find_all('div', {'class': 'quote'}, lambda e: "world" in e.css('.text::text').get())
[<data='<div class="quote" itemscope itemtype="h...' parent='<div class="col-md-8"> <div class="quote...'>]
```
Busca todos los elementos que tengan hijos:
```python
>>> page.find_all(lambda element: len(element.children) > 0)
[<data='<html lang="en"><head><meta charset="UTF...'>,
 <data='<head><meta charset="UTF-8"><title>Quote...' parent='<html lang="en"><head><meta charset="UTF...'>,
 <data='<body> <div class="container"> <div clas...' parent='<html lang="en"><head><meta charset="UTF...'>,
...]
```
Busca todos los elementos que contengan la palabra 'world' en su texto:
```python
>>> page.find_all(lambda element: "world" in element.text)
[<data='<span class="text" itemprop="text">“The...' parent='<div class="quote" itemscope itemtype="h...'>,
 <data='<a class="tag" href="/tag/world/page/1/"...' parent='<div class="tags"> Tags: <meta class="ke...'>]
```
Busca todos los span que coincidan con la expresión regular:
```python
>>> page.find_all('span', re.compile(r'world'))
[<data='<span class="text" itemprop="text">“The...' parent='<div class="quote" itemscope itemtype="h...'>]
```
Busca los div y span de clase 'quote'. No hay ningún span así, por lo que solo se devuelven div:
```python
>>> page.find_all(['div', 'span'], {'class': 'quote'})
[<data='<div class="quote" itemscope itemtype="h...' parent='<div class="col-md-8"> <div class="quote...'>,
 <data='<div class="quote" itemscope itemtype="h...' parent='<div class="col-md-8"> <div class="quote...'>,
...]
```
Combina varios filtros:
```python
>>> page.find_all({'itemtype':"http://schema.org/CreativeWork"}, 'div').css('.author::text').getall()
['Albert Einstein',
 'J.K. Rowling',
...]
```
Un truco más: busca los elementos cuyo atributo `href` termine en 'Einstein':
```python
>>> page.find_all({'href$': 'Einstein'})
[<data='<a href="/author/Albert-Einstein">(about...' parent='<span>by <small class="author" itemprop=...'>,
 <data='<a href="/author/Albert-Einstein">(about...' parent='<span>by <small class="author" itemprop=...'>,
 <data='<a href="/author/Albert-Einstein">(about...' parent='<span>by <small class="author" itemprop=...'>]
```
Otro truco: busca los elementos cuyo atributo `href` contenga '/author/':
```python
>>> page.find_all({'href*': '/author/'})
[<data='<a href="/author/Albert-Einstein">(about...' parent='<span>by <small class="author" itemprop=...'>,
 <data='<a href="/author/J-K-Rowling">(about)</a...' parent='<span>by <small class="author" itemprop=...'>,
 <data='<a href="/author/Albert-Einstein">(about...' parent='<span>by <small class="author" itemprop=...'>,
...]
```
Y así sucesivamente...

## Generar selectores {#generating-selectors}
Puedes generar selectores CSS y XPath para cualquier elemento y volver a usarlos aquí o en otro lugar. No importa qué método hayas usado para encontrar el elemento.

Genera un selector CSS corto para `url_element`. Si no es posible, genera uno completo:
```python
>>> url_element = page.find({'href*': '/author/'})
>>> url_element.generate_css_selector
'body > div > div:nth-of-type(2) > div > div > span:nth-of-type(2) > a'
```
Genera un selector CSS completo para `url_element`, desde el inicio de la página:
```python
>>> url_element.generate_full_css_selector
'body > div > div:nth-of-type(2) > div > div > span:nth-of-type(2) > a'
```
Genera un selector XPath corto para `url_element`. Si no es posible, genera uno completo:
```python
>>> url_element.generate_xpath_selector
'//body/div/div[2]/div/div/span[2]/a'
```
Genera un selector XPath completo para `url_element`, desde el inicio de la página:
```python
>>> url_element.generate_full_xpath_selector
'//body/div/div[2]/div/div/span[2]/a'
```
!!! abstract "Nota"

    Para crear un selector corto, Scrapling busca un elemento único que sirva de punto de partida, por ejemplo, uno con atributo `id`. En este caso no hay ninguno, por lo que el selector corto y el completo son iguales.

## Usar selectores con expresiones regulares {#using-selectors-with-regular-expressions}
Como en `parsel`/`scrapy`, puedes usar `re` y `re_first` para extraer datos con expresiones regulares. En Scrapling están disponibles en casi todas las clases, como `Selector`/`Selectors`/`TextHandler` y `TextHandlers`. Esto permite usarlos directamente sobre un elemento sin seleccionar antes un nodo de texto.

Los veremos con detalle al explicar [TextHandler](main_classes.md#texthandler). Por ahora, estos ejemplos muestran cómo funcionan:
```python
>>> page.css('.price_color')[0].re_first(r'[\d\.]+')
'51.77'

>>> page.css('.price_color').re_first(r'[\d\.]+')
'51.77'

>>> page.css('.price_color').re(r'[\d\.]+')
['51.77',
 '53.74',
 '50.10',
 '47.82',
 '54.23',
...]

>>> page.css('.product_pod h3 a::attr(href)').re(r'catalogue/(.*)/index.html')
['a-light-in-the-attic_1000',
 'tipping-the-velvet_999',
 'soumission_998',
 'sharp-objects_997',
...]

>>> filtering_function = lambda e: e.parent.tag == 'h3' and e.parent.parent.has_class('product_pod')  # As above selector
>>> page.find('a', filtering_function).attrib['href'].re(r'catalogue/(.*)/index.html')
['a-light-in-the-attic_1000']

>>> page.find_by_text('Tipping the Velvet').attrib['href'].re(r'catalogue/(.*)/index.html')
['tipping-the-velvet_999']
```
Y así sucesivamente. Veremos más detalles en la próxima página, junto con la clase [TextHandler](main_classes.md#texthandler).
