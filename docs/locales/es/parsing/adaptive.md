---
title: "Sigue y encuentra elementos HTML con el análisis adaptativo"
description: "Guarda los datos de un elemento y encuentra coincidencias cuando cambie el HTML. Aprende a activar el análisis adaptativo y a usar save, retrieve y relocate."
---

# Scraping adaptativo {#adaptive-scraping}

!!! success "Antes de empezar"

    1. Lee la página [Buscar elementos](../parsing/selection.md) para saber cómo buscar y extraer elementos de un objeto [Selector](../parsing/main_classes.md#selector).
    2. Lee la página [Clases principales](../parsing/main_classes.md) para conocer la clase [Selector](../parsing/main_classes.md#selector).

El scraping adaptativo, antes llamado automatch, es una de las funciones más potentes de Scrapling. Permite que tu scraper siga funcionando cuando cambia un sitio web: guarda los datos de los elementos y los vuelve a encontrar.

Supongamos que quieres extraer datos de una página con esta estructura:
```html
<div class="container">
    <section class="products">
        <article class="product" id="p1">
            <h3>Product 1</h3>
            <p class="description">Description 1</p>
        </article>
        <article class="product" id="p2">
            <h3>Product 2</h3>
            <p class="description">Description 2</p>
        </article>
    </section>
</div>
```
Quieres extraer el primer producto, el que tiene el ID `p1`. Probablemente usarías este selector:
```python
page.css('#p1')
```
Si los dueños del sitio cambian la estructura a algo como esto:
```html
<div class="new-container">
    <div class="product-wrapper">
        <section class="products">
            <article class="product new-class" data-id="p1">
                <div class="product-info">
                    <h3>Product 1</h3>
                    <p class="new-description">Description 1</p>
                </div>
            </article>
            <article class="product new-class" data-id="p2">
                <div class="product-info">
                    <h3>Product 2</h3>
                    <p class="new-description">Description 2</p>
                </div>
            </article>
        </section>
    </div>
</div>
```
El selector dejará de funcionar y tendrás que modificar tu código. Aquí entra en juego la función `adaptive` de Scrapling.

Puedes activar `adaptive` la primera vez que seleccionas un elemento. Si la próxima vez el selector ya no lo encuentra, Scrapling recordará sus propiedades y buscará el elemento más parecido de la página. Y lo hace sin IA :)

```python
from scrapling import Selector, Fetcher
# Before the change
page = Selector(page_source, adaptive=True, url='example.com')
# or
Fetcher.adaptive = True
page = Fetcher.get('https://example.com')
# then
element = page.css('#p1', auto_save=True)
if not element:  # One day website changes?
    element = page.css('#p1', adaptive=True)  # Scrapling still finds it!
# the rest of your code...
```
A continuación verás un ejemplo y luego los detalles de uso. Esta función sirve con todos los métodos de selección, no solo con CSS y XPath.

## Un ejemplo real {#real-world-scenario}
Vamos a usar un sitio real y una herramienta de descarga para obtener su código. Para probar un cambio de diseño, necesitaríamos guardar el código antes del cambio y esperar a la actualización. Es casi imposible saber cuándo ocurrirá, salvo que conozcamos al dueño. Pero eso sería preparar la prueba de antemano, jaja.

Para resolverlo, usaré [The Web Archive](https://archive.org/) y su [Wayback Machine](https://web.archive.org/). Esta es una copia del [sitio de StackOverFlow en 2010](https://web.archive.org/web/20100102003420/http://stackoverflow.com/). Tiene unos cuantos años, ¿verdad?</br>Veamos si la función adaptativa puede extraer el mismo botón del diseño de 2010 y del actual con un solo selector :)

Para extraer el botón Questions del diseño antiguo, puedo usar `#hmenus > div:nth-child(1) > ul > li:nth-child(1) > a`. Es un selector muy específico porque lo generó Google Chrome.


Probemos el mismo selector en ambas versiones:
```python
from scrapling import Fetcher
selector = '#hmenus > div:nth-child(1) > ul > li:nth-child(1) > a'
old_url = "https://web.archive.org/web/20100102003420/http://stackoverflow.com/"
new_url = "https://stackoverflow.com/"
Fetcher.configure(adaptive = True, adaptive_domain='stackoverflow.com')
page = Fetcher.get(old_url, timeout=30)
element1 = page.css(selector, auto_save=True)[0]
# Same selector but used in the updated website
page = Fetcher.get(new_url)
element2 = page.css(selector, adaptive=True)[0]

if element1.text == element2.text:
    print('Scrapling found the same element in the old and new designs!')  # Spoiler alert: it does!
```
Aquí aparece un argumento nuevo: `adaptive_domain`. Para Scrapling, `archive.org` y `stackoverflow.com` son dominios distintos, por lo que guarda sus datos de `adaptive` por separado. Para indicar que se trata del mismo sitio, pasamos el mismo dominio personalizado al guardar los datos de `adaptive` de ambos.

En un caso real, el código sería igual, pero usaría la misma URL en ambas solicitudes. No necesitarías `adaptive_domain`. Es el ejemplo más cercano a un caso real que puedo mostrar. Espero que se entienda :)

En los dos ejemplos anteriores usé las clases `Selector` y `Fetcher` para mostrar que la lógica adaptativa es la misma.

!!! info "Información"

    El motivo principal para añadir `adaptive_domain` fue permitir que un sitio cambie su URL al cambiar el diseño o la estructura. Con este argumento puedes seguir usando los datos adaptativos guardados con la nueva URL. Sin él, Scrapling lo considera otro sitio y deja de usar los datos anteriores.

## Cómo funciona el scraping adaptativo {#how-the-adaptive-scraping-feature-works}
El scraping adaptativo tiene dos fases:

1. **Guardar**: almacena las propiedades que distinguen a cada elemento.
2. **Buscar coincidencias**: encuentra después elementos con propiedades parecidas.

Imagina que seleccionas un elemento con cualquier método y quieres que la biblioteca lo encuentre la próxima vez, aunque cambie la estructura o el diseño del sitio.

Sin entrar en demasiados detalles técnicos, estos son los pasos:

  1. Le indicas a Scrapling que guarde las propiedades del elemento mediante uno de los métodos que veremos abajo.
  2. Scrapling guarda esas propiedades en la base de datos configurada, que por defecto es SQLite.
  3. Los dueños del sitio pueden cambiar o borrar cualquier dato del elemento. Por eso no se puede usar uno de esos datos como identificador único en la base de datos. Para resolverlo, el sistema de almacenamiento usa dos valores:
     1. El dominio del sitio actual. Si usas `Selector`, pásalo al crear el objeto. Si usas una herramienta de descarga, se toma automáticamente de la URL.
     2. Un `identifier` para buscar las propiedades del elemento en la base de datos. No siempre tienes que definirlo tú, como veremos más adelante.

     Juntos permiten recuperar después las propiedades del elemento.

  4. Cuando cambia la estructura del sitio, activas `adaptive` para buscar el elemento. Scrapling recupera sus propiedades guardadas y las compara con las de todos los elementos de la página. Calcula una puntuación según lo parecidos que sean, teniendo en cuenta todos los datos que veremos a continuación.
  5. Devuelve el elemento o los elementos con la puntuación más alta.

### Las propiedades del elemento {#the-unique-properties}
Quizá te preguntes qué propiedades se pueden usar si todas pueden cambiar o desaparecer.

Scrapling usa estos datos:

- El nombre de la etiqueta, el texto, los atributos con sus nombres y valores, las etiquetas de los elementos hermanos y las etiquetas de la ruta del elemento.
- El nombre de la etiqueta del padre, sus atributos con nombres y valores, y su texto.

La comparación no exige que los valores sean idénticos. Mide cuánto se parecen. Tiene en cuenta incluso el orden de los valores, como el orden de los nombres de clase antes y después del cambio.

## Cómo usar la función adaptativa {#how-to-use-adaptive-feature}
Puedes aplicar la función adaptativa a cualquier elemento que hayas encontrado. También está disponible mediante argumentos en los métodos CSS y XPath, como ya vimos. Volveremos a ello más adelante.

Primero, activa `adaptive` pasando `adaptive=True` al crear un [Selector](main_classes.md#selector), o actívalo en la herramienta de descarga que uses, como veremos a continuación.

Ejemplos:
```python
from scrapling import Selector, Fetcher
page = Selector(html_doc, adaptive=True)
# OR
Fetcher.adaptive = True
page = Fetcher.get('https://example.com')
```
Si usas la clase [Selector](main_classes.md#selector), pasa la URL del sitio mediante el argumento `url`. Así Scrapling separa las propiedades guardadas por dominio.

Si no pasas una URL, se usa `default` en ese campo al guardar las propiedades. Esto solo causa un problema si luego usas el mismo identificador para otro sitio sin pasar su URL. Cada guardado reemplaza los datos anteriores y `adaptive` solo usa las últimas propiedades guardadas.

También están `storage` y `storage_args`, que configuran la conexión a la base de datos. Por defecto se usa la clase SQLite incluida en la biblioteca. Solo necesitas estos argumentos si quieres crear tu propio sistema de almacenamiento. Lo veremos en [otra página de la sección de desarrollo](../development/adaptive_storage_system.md).

Una vez activada `adaptive` de forma global, tienes dos formas principales de usarla.

### Mediante selección CSS o XPath {#the-cssxpath-selection-way}
Como en el ejemplo anterior, primero usa `auto_save` al seleccionar un elemento que exista en la página:
```python
element = page.css('#p1', auto_save=True)
```
Si el selector deja de encontrarlo, usa el mismo selector con `adaptive` y la biblioteca lo buscará:
```python
element = page.css('#p1', adaptive=True)
```
Bastante sencillo, ¿verdad?

Por dentro ocurren varios pasos. ¿Recuerdas el identificador que permite recuperar el elemento? Los métodos `css` y `xpath` usan automáticamente el selector como identificador para facilitarte el trabajo :)

También puedes pasar `identifier` a estos métodos para elegirlo tú. Puede ser útil en algunos casos, incluso al guardar propiedades con `auto_save`.

### De forma manual {#the-manual-way}
Puedes guardar y recuperar un elemento manualmente, y después volver a encontrarlo con `adaptive`. Así puedes usar elementos obtenidos con cualquier método de selección.

Por ejemplo, supongamos que encuentras un elemento por su texto:
```python
element = page.find_by_text('Tipping the Velvet', first_match=True)
```
Guarda sus propiedades con `save`, pero en este caso debes elegir el identificador. Aquí usé `my_special_element`. En tu código conviene elegir uno que describa el elemento, igual que haces con los nombres de variables :)
```python
page.save(element, 'my_special_element')
```
Más adelante, puedes recuperar sus datos y buscarlo en la página con `adaptive`:
```python
>>> element_dict = page.retrieve('my_special_element')
>>> page.relocate(element_dict, selector_type=True)
[<data='<a href="catalogue/tipping-the-velvet_99...' parent='<h3><a href="catalogue/tipping-the-velve...'>]
>>> page.relocate(element_dict, selector_type=True).css('::text').getall()
['Tipping the Velvet']
```
Para ello se usan los métodos `retrieve` y `relocate`.

Si quieres mantenerlo como un objeto `lxml.etree`, omite `selector_type`:
```python
>>> page.relocate(element_dict)
[<Element a at 0x105a2a7b0>]
```

## Solución de problemas {#troubleshooting}

### No se encuentran coincidencias {#no-matches-found}
```python
# 1. Check if data was saved
element_data = page.retrieve('identifier')
if not element_data:
    print("No data saved for this identifier")

# 2. Try with different identifier
products = page.css('.product', adaptive=True, identifier='old_selector')

# 3. Save again with new identifier
products = page.css('.new-product', auto_save=True, identifier='new_identifier')
```

### Se encuentran elementos incorrectos {#wrong-elements-matched}
```python
# Use more specific selectors
products = page.css('.product-list .product', auto_save=True)

# Or save with more context
product = page.find_by_text('Product Name').parent
page.save(product, 'specific_product')
```

## Problemas conocidos {#known-issues}
Al guardar con `adaptive`, solo se guardan las propiedades del primer elemento de los resultados. Si tu selector encuentra varios elementos en distintas partes de la página, `adaptive` solo volverá a encontrar el primero. Esto no se aplica a los selectores CSS combinados, por ejemplo, separados por comas. Estos se separan y se ejecutan uno por uno.

## Para terminar {#final-thoughts}
Explicar esta función con detalle y sin complicarla no fue fácil. Si algo no queda claro, escribe en la [sección de debates](https://github.com/D4Vinci/Scrapling/discussions) y te responderé lo antes posible. También puedes usar el servidor de Discord o escribirme en privado :)
