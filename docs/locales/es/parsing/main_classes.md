---
title: "Selector y Selectors de Scrapling: datos y navegación"
description: "Aprende cómo Selector y Selectors guardan HTML, texto y atributos. Extrae valores, resuelve URL y recorre padres, hijos y hermanos."
---

# Clases principales del analizador {#parsing-main-classes}

!!! success "Antes de empezar"

    - Lee la página [Buscar elementos](../parsing/selection.md) para saber cómo buscar y extraer elementos de un objeto [Selector](../parsing/main_classes.md#selector).

Después de ver las formas de seleccionar elementos y sus funciones, vamos a conocer la clase [Selector](#selector) y los demás objetos. Así entenderás mejor cómo funciona el analizador.

La clase [Selector](#selector) es la base del analizador de Scrapling. Analiza HTML y permite seleccionar elementos. Puedes importarla de cualquiera de estas formas:
```python
from scrapling import Selector
from scrapling.parser import Selector
```
Después úsala directamente, como vimos en la [introducción](../overview.md):
```python
page = Selector(
    '<html>...</html>',
    url='https://example.com'
)

# Then select elements as you like
elements = page.css('.product')
```
Al pasar código HTML o descargar un sitio, el objeto principal con el que trabajas es un [Selector](#selector). Las operaciones de selección o navegación que devuelven elementos de la página te dan un [Selector](#selector) o un [Selectors](#selectors). Esto no se aplica a las operaciones que devuelven texto u otros valores.

La página es un [Selector](#selector), y cada elemento dentro de ella también es un [Selector](#selector). El texto de los elementos y de sus atributos usa [TextHandler](#texthandler). Los atributos de cada elemento se guardan en [AttributesHandler](#attributeshandler). Veremos ambos más adelante. Primero, vamos con [Selector](#selector).

## Selector {#selector}
### Argumentos {#arguments-explained}
El más importante es `content`: recibe el HTML que quieres analizar, como `str` o `bytes`.

`url` establece la URL de la página. Se usa para resolver enlaces relativos y separar los datos adaptativos por dominio. Los argumentos `adaptive`, `storage` y `storage_args` configuran la función [adaptativa](adaptive.md). No afectan al uso normal si no la activas.

Estos argumentos controlan cómo se procesa el HTML:

- **encoding**: codificación del HTML. Por defecto es `UTF-8`.
- **keep_comments**: indica si se conservan los comentarios HTML al analizar la página. Está desactivado por defecto, ya que los comentarios pueden causar problemas al extraer datos.

Dejaremos `huge_tree` y `root` para más adelante para no complicar esta página.
Son funciones avanzadas que no necesitas para empezar. La sección de desarrollo cubre esos detalles si quieres profundizar.

La mayoría de las propiedades de la página y sus elementos se calculan solo cuando las usas, como el contenido de texto. Esta carga diferida es una de las razones de la velocidad de Scrapling :)

### Propiedades {#properties}
Ya vimos parte de esto en la [introducción](../overview.md), pero aquí lo explicaremos con más detalle y ejemplos más completos. Las propiedades para recorrer la página están en su propia sección de [navegación](#traversal).

Para los ejemplos, vamos a analizar esta página HTML:
```html
<html>
  <head>
    <title>Some page</title>
  </head>
  <body>
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

    <script id="page-data" type="application/json">
      {
        "lastUpdated": "2024-09-22T10:30:00Z",
        "totalProducts": 3
      }
    </script>
  </body>
</html>
```
Carga la página como antes:
```python
from scrapling import Selector
page = Selector(html_doc)
```
Obtén todo el texto de la página, incluidos sus elementos internos:
```python
>>> page.get_all_text()
'Some page\n\n    \n\n      \nProduct 1\nThis is product 1\n$10.99\nIn stock: 5\nProduct 2\nThis is product 2\n$20.99\nIn stock: 3\nProduct 3\nThis is product 3\n$15.99\nOut of stock'
```
Obtén el primer artículo, que usaremos como ejemplo:
```python
article = page.find('article')
```
De la misma forma, obtén todo el texto del elemento y sus elementos internos:
```python
>>> article.get_all_text()
'Product 1\nThis is product 1\n$10.99\nIn stock: 5'
```
Si intentas leer solo su texto directo, estará vacío. En el HTML anterior no tiene texto fuera de sus elementos hijos:
```python
>>> article.text
''
```
El método `get_all_text` admite estos argumentos opcionales:

1. **separator**: separador con el que se unen los textos encontrados. Por defecto es '\n'.
2. **strip**: quita los espacios de los extremos de cada texto antes de unirlos. Está desactivado por defecto.
3. **ignore_tags**: tupla de etiquetas que se ignoran junto con todo su contenido. Por defecto es `('script', 'style',)`.
4. **valid_values**: recoge solo textos con contenido. Ignora los vacíos y los que solo tienen espacios. Está activado por defecto.

El texto devuelto es un [TextHandler](#texthandler), no una cadena normal. Lo veremos después. Si contiene JSON válido, puedes usar `.json()`:
```python
>>> script = page.find('script')
>>> script.json()
{'lastUpdated': '2024-09-22T10:30:00Z', 'totalProducts': 3}
```
Obtén la etiqueta del elemento:
```python
>>> article.tag
'article'
```
Si lo haces sobre la página, estarás trabajando con su elemento raíz `html`:
```python
>>> page.tag
'html'
```
La misma idea se aplica tanto a `page` como a `element`, así que no la repetiremos.

Obtén los atributos del elemento:
```python
>>> print(article.attrib)
{'class': 'product', 'data-id': '1'}
```
Accede a un atributo concreto de cualquiera de estas formas:
```python
article.attrib['class']
article.attrib.get('class')
article['class']  # new in v0.3
```
Comprueba si existe un atributo con alguno de estos métodos:
```python
'class' in article.attrib
'class' in article  # new in v0.3
```
Obtén el HTML del elemento:
```python
>>> article.html_content
'<article class="product" data-id="1"><h3>Product 1</h3>\n        <p class="description">This is product 1</p>\n        <span class="price">$10.99</span>\n        <div class="hidden stock">In stock: 5</div>\n      </article>'
```
Obtén una versión del HTML con formato más fácil de leer:
```python
print(article.prettify())
```
```html
<article class="product" data-id="1"><h3>Product 1</h3>
    <p class="description">This is product 1</p>
    <span class="price">$10.99</span>
    <div class="hidden stock">In stock: 5</div>
</article>
```
Usa `.body` para obtener el contenido original de la página. Desde v0.4, en los objetos `Response` de las herramientas de descarga, `.body` siempre devuelve `bytes`.
```python
>>> page.body
'<html>\n  <head>\n    <title>Some page</title>\n  </head>\n  ...'
```
Obtén todos los antecesores del elemento en el árbol DOM:
```python
>>> article.path
[<data='<div class="product-list"> <article clas...' parent='<body> <div class="product-list"> <artic...'>,
 <data='<body> <div class="product-list"> <artic...' parent='<html><head><title>Some page</title></he...'>,
 <data='<html><head><title>Some page</title></he...'>]
```
Genera un selector CSS corto si es posible. Si no, genera uno completo:
```python
>>> article.generate_css_selector
'body > div > article'
>>> article.generate_full_css_selector
'body > div > article'
```
Lo mismo con XPath:
```python
>>> article.generate_xpath_selector
"//body/div/article"
>>> article.generate_full_xpath_selector
"//body/div/article"
```

### Navegación {#traversal}
Con los elementos anteriores, veamos las propiedades y métodos para recorrer la página.

Si no conoces el árbol DOM o las estructuras de árbol, esta sección puede resultar algo confusa. Te recomiendo leer sobre esos conceptos para entenderlos mejor.

Aquí tienes una explicación rápida para empezar.<br/>
El elemento `html` es la raíz del árbol de la página, ya que toda página empieza con un elemento `html`.<br/>
Justo debajo están elementos como `head` y `body`. Son hijos de `html`, y ese elemento `html` es su padre. A su vez, `head` y `body` son hermanos porque comparten el mismo padre.

Accede al padre de un elemento:
```python
>>> article.parent
<data='<div class="product-list"> <article clas...' parent='<body> <div class="product-list"> <artic...'>
>>> article.parent.tag
'div'
```
Puedes encadenar esta propiedad. Lo mismo se aplica a las propiedades y métodos similares que veremos.
```python
>>> article.parent.parent.tag
'body'
```
Obtén los hijos de un elemento:
```python
>>> article.children
[<data='<h3>Product 1</h3>' parent='<article class="product" data-id="1"><h3...'>,
 <data='<p class="description">This is product 1...' parent='<article class="product" data-id="1"><h3...'>,
 <data='<span class="price">$10.99</span>' parent='<article class="product" data-id="1"><h3...'>,
 <data='<div class="hidden stock">In stock: 5</d...' parent='<article class="product" data-id="1"><h3...'>]
```
Obtén todos los elementos que hay debajo, incluidos los de niveles más profundos. Es como `children`, pero recorre todos los niveles:
```python
>>> article.below_elements
[<data='<h3>Product 1</h3>' parent='<article class="product" data-id="1"><h3...'>,
 <data='<p class="description">This is product 1...' parent='<article class="product" data-id="1"><h3...'>,
 <data='<span class="price">$10.99</span>' parent='<article class="product" data-id="1"><h3...'>,
 <data='<div class="hidden stock">In stock: 5</d...' parent='<article class="product" data-id="1"><h3...'>]
```
En este caso devuelve lo mismo que `children`, porque sus hijos no tienen otros hijos.

Este ejemplo con el elemento de clase `product-list` muestra mejor la diferencia entre `children` y `below_elements`:
```python
>>> products_list = page.css('.product-list')[0]
>>> products_list.children
[<data='<article class="product" data-id="1"><h3...' parent='<div class="product-list"> <article clas...'>,
 <data='<article class="product" data-id="2"><h3...' parent='<div class="product-list"> <article clas...'>,
 <data='<article class="product" data-id="3"><h3...' parent='<div class="product-list"> <article clas...'>]

>>> products_list.below_elements
[<data='<article class="product" data-id="1"><h3...' parent='<div class="product-list"> <article clas...'>,
 <data='<h3>Product 1</h3>' parent='<article class="product" data-id="1"><h3...'>,
 <data='<p class="description">This is product 1...' parent='<article class="product" data-id="1"><h3...'>,
 <data='<span class="price">$10.99</span>' parent='<article class="product" data-id="1"><h3...'>,
 <data='<div class="hidden stock">In stock: 5</d...' parent='<article class="product" data-id="1"><h3...'>,
 <data='<article class="product" data-id="2"><h3...' parent='<div class="product-list"> <article clas...'>,
...]
```
Obtén los hermanos de un elemento:
```python
>>> article.siblings
[<data='<article class="product" data-id="2"><h3...' parent='<div class="product-list"> <article clas...'>,
 <data='<article class="product" data-id="3"><h3...' parent='<div class="product-list"> <article clas...'>]
```
Obtén el siguiente elemento:
```python
>>> article.next
<data='<article class="product" data-id="2"><h3...' parent='<div class="product-list"> <article clas...'>
```
La misma lógica se aplica a `previous`:
```python
>>> article.previous  # It's the first child, so it doesn't have a previous element
>>> second_article = page.css('.product[data-id="2"]')[0]
>>> second_article.previous
<data='<article class="product" data-id="1"><h3...' parent='<div class="product-list"> <article clas...'>
```
Comprueba de forma rápida si un elemento tiene una clase concreta:
```python
>>> article.has_class('product')
True
```
Si necesitas ir más allá del padre, puedes recorrer todos los antecesores de un elemento:
```python
for ancestor in article.iterancestors():
    # do something with it...
```
También puedes buscar un antecesor que cumpla una condición. Pasa una función que reciba un [Selector](#selector) y devuelva `True` si cumple la condición, o `False` si no:
```python
>>> article.find_ancestor(lambda ancestor: ancestor.has_class('product-list'))
<data='<div class="product-list"> <article clas...' parent='<body> <div class="product-list"> <artic...'>

>>> article.find_ancestor(lambda ancestor: ancestor.css('.product-list'))  # Same result, different approach
<data='<div class="product-list"> <article clas...' parent='<body> <div class="product-list"> <artic...'>
```
## Selectors {#selectors}
`Selectors` es la versión en lista de [Selector](#selector). Hereda del tipo `List` de Python, así que conserva las propiedades y métodos de `List`. Además, añade métodos para trabajar con los objetos [Selector](#selector) que contiene.

En [Selector](#selector), los métodos y propiedades que devuelven varios elementos los entregan como un objeto [Selectors](#selectors).

Desde v0.4, todos los métodos de selección devuelven objetos [Selector](#selector)/[Selectors](#selectors), incluso al seleccionar texto o atributos. Los nodos de texto obtenidos con `::text`, `/text()`, `::attr()` o `/@attr` se envuelven en objetos [Selector](#selector). Su `tag` es `"#text"` y su propiedad `text` devuelve el valor de texto. Las demás propiedades devuelven valores vacíos o por defecto sin causar errores.

```python
page.css('a::text')              # -> Selectors (of text node Selectors)
page.xpath('//a/text()')         # -> Selectors
page.css('a::text').get()        # -> TextHandler (the first text value)
page.css('a::text').getall()     # -> TextHandlers (all text values)
page.css('a::attr(href)')        # -> Selectors
page.xpath('//a/@href')          # -> Selectors
page.css('.price_color')         # -> Selectors
```

### Métodos para extraer datos {#data-extraction-methods}
Desde v0.4, [Selector](#selector) y [Selectors](#selectors) ofrecen `get()`, `getall()` y sus alias `extract_first` y `extract`, siguiendo las convenciones de Scrapy. El antiguo método `get_all()` se eliminó.

**En un objeto [Selector](#selector):**

- `get()` devuelve un `TextHandler`: el valor de texto si es un nodo de texto, o el HTML externo completo como cadena si es un elemento HTML.
- `getall()` devuelve una lista `TextHandlers` con esa única cadena.
- `extract_first` es un alias de `get()`, y `extract` es un alias de `getall()`.

```python
>>> page.css('h3')[0].get()        # Outer HTML of the element
'<h3>Product 1</h3>'

>>> page.css('h3::text')[0].get()  # Text value of the text node
'Product 1'
```

**En un objeto [Selectors](#selectors):**

- `get(default=None)` devuelve la cadena del **primer** elemento, o `default` si la lista está vacía.
- `getall()` convierte **todos** los elementos en cadenas y devuelve una lista `TextHandlers`.
- `extract_first` es un alias de `get()`, y `extract` es un alias de `getall()`.

```python
>>> page.css('.price::text').get()      # First price text
'$10.99'

>>> page.css('.price::text').getall()   # All price texts
['$10.99', '$20.99', '$15.99']

>>> page.css('.price::text').get('')    # With default value
'$10.99'
```

Estos métodos sirven con todos los tipos de selección, como CSS, XPath y `find`. Son la forma recomendada de extraer texto y atributos con un estilo compatible con Scrapy.

Veamos ahora qué más ofrece [Selectors](#selectors).
### Propiedades {#properties_1}
Además de las operaciones normales de las listas de Python, como recorrerlas o tomar una parte,

puedes hacer lo siguiente:

Ejecutar selectores CSS y XPath directamente sobre los objetos [Selector](#selector) de la lista. Los tipos devueltos son los mismos que en `css` y `xpath` de [Selector](#selector). Los argumentos también son parecidos, salvo que aquí no está disponible `adaptive`. Esto facilita encadenar métodos.
```pycon
>>> page.css('.product h3::text').getall()
['Product 1', 'Product 2', 'Product 3']
>>> page.css('.product').css('h3::text').getall()
['Product 1', 'Product 2', 'Product 3']
```
Ejecutar `re` y `re_first` directamente, con los mismos argumentos que en [Selector](#selector). Los explicaremos en la sección de [TextHandler](#texthandler).

Aquí `re_first` funciona de otra forma: ejecuta `re` sobre cada [Selector](#selector) y devuelve el primero que tenga un resultado. `re` devuelve un [TextHandlers](#texthandlers) que reúne todos los objetos [TextHandler](#texthandler) en un solo [TextHandlers](#texthandlers).
```pycon
>>> page.css('.price::text').re(r'[\d.]+')
['10.99', '20.99', '15.99']
>>> page.css('.product h3::text').re(r'Product (\d+)')
['1', '2', '3']
```
Con `search` puedes buscar entre los objetos [Selector](#selector) de la lista. Pasa una función que reciba un [Selector](#selector) como primer argumento y devuelva True o False. El método devuelve el primer [Selector](#selector) que cumpla la condición, o `None` si no hay ninguno.

```pycon
>>> product = page.css('.product').search(lambda p: p.css('.price::text').get() == '$20.99')
>>> product.css('h3::text').get()
'Product 2'
```
También puedes usar `filter`. Recibe una función como `search`, pero devuelve un `Selectors` con todos los objetos [Selector](#selector) que cumplan la condición.

```pycon
>>> products = page.css('.product').filter(lambda p: float(p.css('.price::text').re_first(r'[\d.]+')) > 15)
>>> products.css('h3::text').getall()
['Product 2', 'Product 3']
```
Puedes acceder al primer o al último elemento sin preocuparte por errores de índice:
```python
>>> page.css('.product').first   # First Selector or None
<data='<article class="product" data-id="1"><h3...'>
>>> page.css('.product').last    # Last Selector or None
<data='<article class="product" data-id="3"><h3...'>
>>> page.css('.nonexistent').first  # Returns None instead of raising IndexError
```

Para saber cuántos objetos [Selector](#selector) hay en un [Selectors](#selectors), puedes hacer esto:
```python
page.css('.product').length
```
Es lo mismo que:
```python
len(page.css('.product'))
```
Sí, como en JavaScript :)

## TextHandler {#texthandler}
Esta clase es importante: los métodos y propiedades que devuelven una cadena usan `TextHandler`. Los que devuelven una lista de cadenas usan [TextHandlers](#texthandlers).

TextHandler hereda de la cadena de texto de Python, así que permite todas sus operaciones. Entonces, ¿por qué tiene otro nombre?

Porque añade métodos y propiedades que las cadenas normales no tienen. Como se usa para el texto en toda la biblioteca, puedes combinar esas funciones para escribir código más corto y claro. También puedes importarla y usarla con cualquier cadena, como veremos [más adelante](../development/scrapling_custom_types.md).
### Uso {#usage}
Las operaciones como tomar una parte, acceder por índice o llamar a `split`, `replace` y `strip` vuelven a devolver `TextHandler`. Así puedes encadenarlas. Si encuentras una que devuelva una cadena normal en lugar de `TextHandler`, abre una incidencia para que también la adaptemos.

Empecemos por `re` y `re_first`. Son los mismos métodos que en [Selector](#selector), [Selectors](#selectors) y [TextHandlers](#texthandlers), y aceptan los mismos argumentos.

- `re` recibe como primer argumento una expresión regular en forma de cadena o ya compilada. Busca todas las coincidencias y las devuelve en un [TextHandlers](#texthandlers). `re_first` acepta los mismos argumentos, pero devuelve solo la primera coincidencia como `TextHandler`.
    
    También admite estos argumentos:
    
    - **replace_entities**: reemplaza las referencias a entidades por sus caracteres. Está activado por defecto.
    - **clean_match**: ignora los espacios en blanco, incluidos los espacios seguidos, al comparar. Está desactivado por defecto.
    - **case_sensitive**: distingue entre mayúsculas y minúsculas. Está activado por defecto. Si lo desactivas, la expresión regular se compila sin esa distinción.
  
    Ya vimos estos ejemplos. Devuelven [TextHandlers](#texthandlers) porque usan `re`:
    ```pycon
    >>> page.css('.price::text').re(r'[\d.]+')
    ['10.99', '20.99', '15.99']
    >>> page.css('.product h3::text').re(r'Product (\d+)')
    ['1', '2', '3']
    ```
    Para mostrar los otros argumentos, usaremos una cadena distinta en cada ejemplo:
    ```python
    >>> from scrapling import TextHandler
    >>> test_string = TextHandler('hi  there')  # Hence the two spaces
    >>> test_string.re('hi there')
    >>> test_string.re('hi there', clean_match=True)  # Using `clean_match` will clean the string before matching the regex
    ['hi there']
    
    >>> test_string2 = TextHandler('Oh, Hi Mark')
    >>> test_string2.re_first('oh, hi Mark')
    >>> test_string2.re_first('oh, hi Mark', case_sensitive=False)  # Hence disabling `case_sensitive`
    'Oh, Hi Mark'
    
    # Mixing arguments
    >>> test_string.re('hi there', clean_match=True, case_sensitive=False)
    ['hi there']
    ```
    Usar `TextHandler` en toda la biblioteca tiene otra ventaja: como `html_content` devuelve `TextHandler`, puedes aplicar expresiones regulares directamente al HTML:
    ```python
    >>> page.html_content.re('div class=".*">(.*)</div')
    ['In stock: 5', 'In stock: 3', 'Out of stock']
    ```

- `.json()` intenta convertir el contenido a un objeto JSON de forma rápida. Si no es posible, produce un error:
  ```python
  >>> page.css('#page-data::text').get()
    '\n      {\n        "lastUpdated": "2024-09-22T10:30:00Z",\n        "totalProducts": 3\n      }\n    '
  >>> page.css('#page-data::text').get().json()
    {'lastUpdated': '2024-09-22T10:30:00Z', 'totalProducts': 3}
  ```
  Si al seleccionar un elemento no indicas un nodo de texto o un atributo, se usa automáticamente su contenido de texto:
  ```python
  >>> page.css('#page-data')[0].json()
  {'lastUpdated': '2024-09-22T10:30:00Z', 'totalProducts': 3}
  ```
  La clase [Selector](#selector) añade otro detalle. Supongamos que trabajamos con esta página:
  ```html
  <html>
      <body>
          <div>
            <script id="page-data" type="application/json">
              {
                "lastUpdated": "2024-09-22T10:30:00Z",
                "totalProducts": 3
              }
            </script>
          </div>
      </body>
  </html>
  ```
  [Selector](#selector) tiene el método `get_all_text`, que devuelve un `TextHandler`.<br/><br/>
  Si haces esto:
  ```python
  >>> page.css('div::text').get().json()
  ```
  Obtendrás un error porque el `div` no tiene texto directo que se pueda convertir a JSON. De hecho, no tiene texto directo de ningún tipo.<br/><br/>
  En este caso puedes usar `get_all_text`:
  ```python
  >>> page.css('div')[0].get_all_text(ignore_tags=[]).json()
    {'lastUpdated': '2024-09-22T10:30:00Z', 'totalProducts': 3}
  ```
  Usé `ignore_tags` porque su valor por defecto es `('script', 'style',)`.<br/><br/>
  Hay otro caso relacionado cuando usas una herramienta de descarga. Supongamos que recibes una respuesta JSON como esta:
  ```python
  >>> page = Selector("""{"some_key": "some_value"}""")
  ```
  Como [Selector](#selector) está pensado para páginas HTML, trata ese contenido como HTML incompleto y lo corrige. Si usas `html_content`, obtienes esto:
  ```python
  >>> page.html_content
  '<html><body><p>{"some_key": "some_value"}</p></body></html>'
  ```
  Aquí puedes usar `json` directamente:
  ```python
  >>> page.json()
  {'some_key': 'some_value'}
  ```
  Quizá te preguntes cómo funciona si `html` no tiene texto directo.<br/>
  Para respuestas como JSON, [Selector](#selector) conserva una copia del contenido original. Al llamar a `.json()`, primero intenta convertir esa copia. Si no la tiene, como ocurre con los elementos internos, usa el texto directo del elemento. Si tampoco lo hay, llama a `get_all_text`.<br/>

- `.clean()` elimina los espacios en blanco y los espacios seguidos, y devuelve un nuevo `TextHandler`:
```python
>>> TextHandler('\n wonderful  idea, \reh?').clean()
'wonderful idea, eh?'
```
También puedes pasar `remove_entities` para que `clean` reemplace las entidades HTML por sus caracteres.

- `.sort()` ordena los caracteres de una cadena, de forma parecida a como ordenas una lista:
```python
>>> TextHandler('acb').sort()
'abc'
```
O en orden inverso:
```python
>>> TextHandler('acb').sort(reverse=True)
'cba'
```

Se añadirán otros métodos y propiedades con el tiempo. Recuerda que esta clase reemplaza a las cadenas normales en casi toda la biblioteca.

## TextHandlers {#texthandlers}
Esta clase sigue una idea parecida a [Selectors](#selectors) y [Selector](#selector). Hereda las operaciones de las listas normales y añade `re` y `re_first`.

Aquí `re_first` ejecuta `re` sobre cada [TextHandler](#texthandler) y devuelve el primer resultado, o `None`. El resto funciona como ya vimos. Se añadirán más métodos con el tiempo.

## AttributesHandler {#attributeshandler}
Es una versión de solo lectura del diccionario `dict` de Python. Se usa para guardar los atributos de cada elemento u objeto [Selector](#selector).
```python
>>> print(page.find('script').attrib)
{'id': 'page-data', 'type': 'application/json'}
>>> type(page.find('script').attrib).__name__
'AttributesHandler'
```
Al ser de solo lectura, usa menos recursos que un diccionario normal. Conserva los métodos y propiedades de los diccionarios, salvo los que permiten modificar los datos.

Añade dos funciones sencillas:

- El método `search_values`:

    En un diccionario puedes usar `dict.get("key_name")` para buscar una clave. Buscar por valores requiere más código. Este método lo hace por ti: busca entre los valores de los atributos y devuelve un diccionario por cada coincidencia.
    
    Un ejemplo sencillo:
    ```python
    >>> for i in page.find('script').attrib.search_values('page-data'):
            print(i)
    {'id': 'page-data'}
    ```
    También admite `partial` para buscar por una parte del valor:
    ```python
    >>> for i in page.find('script').attrib.search_values('page', partial=True):
            print(i)
    {'id': 'page-data'}
    ```
    Un caso más habitual sería combinarlo con `find_all` para buscar elementos que tengan un valor concreto en sus atributos:
    ```python
    >>> page.find_all(lambda element: list(element.attrib.search_values('product')))
    [<data='<article class="product" data-id="1"><h3...' parent='<div class="product-list"> <article clas...'>,
     <data='<article class="product" data-id="2"><h3...' parent='<div class="product-list"> <article clas...'>,
     <data='<article class="product" data-id="3"><h3...' parent='<div class="product-list"> <article clas...'>]
    ```
    Todos estos elementos tienen 'product' como valor de `class`.
    
    Uso `list` porque `search_values` devuelve un generador. Sin convertirlo a lista, la condición sería `True` para todos los elementos.

- La propiedad `json_string`:

    Convierte los atributos a una cadena JSON. Si no se pueden convertir, produce un error.
  
    ```python
    >>>page.find('script').attrib.json_string
    b'{"id":"page-data","type":"application/json"}'
    ```