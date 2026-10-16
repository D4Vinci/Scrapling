---
title: "Pasar de BeautifulSoup a Scrapling"
description: "Compara las tareas habituales de selección, texto, atributos y navegación de BeautifulSoup con Scrapling. Revisa las diferencias de API con ejemplos prácticos."
---

# Pasar de BeautifulSoup a Scrapling {#migrating-from-beautifulsoup-to-scrapling}

Si ya conoces BeautifulSoup, te resultará fácil empezar con Scrapling. Es mucho más rápido, ofrece las mismas funciones de análisis que BS y añade otras que BS no tiene. También incluye herramientas para obtener páginas web modernas y trabajar con ellas. Esta guía te ayudará a adaptar tu código de BeautifulSoup a Scrapling.

La siguiente tabla reúne las tareas más comunes al extraer datos de páginas web. Cada fila muestra cómo hacer una tarea con BeautifulSoup y cómo hacerla con Scrapling.

Verás que algunos atajos de BeautifulSoup no están en Scrapling. Esa es una de las razones por las que BeautifulSoup es más lento. La idea es sencilla: si algo ya se puede escribir en una línea corta, no hace falta perder rendimiento para acortarla un poco más :)

| Tarea | Código de BeautifulSoup | Código de Scrapling |
|---|---|---|
| Importar el parser | `from bs4 import BeautifulSoup`                                                                               | `from scrapling.parser import Selector`                                           |
| Analizar HTML desde una cadena | `soup = BeautifulSoup(html, 'html.parser')`                                                                   | `page = Selector(html)`                                                           |
| Buscar un elemento | `element = soup.find('div', class_='example')`                                                                | `element = page.find('div', class_='example')`                                    |
| Buscar varios elementos | `elements = soup.find_all('div', class_='example')`                                                           | `elements = page.find_all('div', class_='example')`                               |
| Buscar un elemento (ejemplo 2) | `element = soup.find('div', attrs={"class": "example"})`                                                      | `element = page.find('div', {"class": "example"})`                                |
| Buscar un elemento (ejemplo 3) | `element = soup.find(re.compile("^b"))`                                                                       | `element = page.find(lambda e: re.search(r"^b", e.tag) is not None)` |
| Buscar un elemento (ejemplo 4) | `element = soup.find(lambda e: len(list(e.children)) > 0)`                                                    | `element = page.find(lambda e: len(e.children) > 0)`                              |
| Buscar un elemento (ejemplo 5) | `element = soup.find(["a", "b"])`                                                                             | `element = page.find(["a", "b"])`                                                 |
| Buscar un elemento por su texto | `element = soup.find(text="some text")`                                                                       | `element = page.find_by_text("some text", partial=False)`                         |
| Usar CSS para buscar la primera coincidencia | `elements = soup.select_one('div.example')`                                                                   | `elements = page.css('div.example').first`                                        |
| Usar CSS para buscar todas las coincidencias | `elements = soup.select('div.example')`                                                                       | `elements = page.css('div.example')`                                              |
| Obtener el código de la página o el elemento con formato legible | `prettified = soup.prettify()`                                                                                | `prettified = page.prettify()`                                                    |
| Obtener el código de la página o el elemento sin formato adicional | `source = str(soup)`                                                                                          | `source = page.html_content`                                                      |
| Obtener el nombre de etiqueta de un elemento | `name = element.name`                                                                                         | `name = element.tag`                                                              |
| Extraer el texto de un elemento | `string = element.string`                                                                                     | `string = element.text`                                                           |
| Extraer todo el texto de un documento o de una etiqueta | `text = soup.get_text(strip=True)`                                                                            | `text = page.get_all_text(strip=True)`                                            |
| Acceder al diccionario de atributos | `attrs = element.attrs`                                                                                       | `attrs = element.attrib`                                                          |
| Extraer atributos | `attr = element['href']`                                                                                      | `attr = element['href']`                                                          |
| Ir al elemento padre | `parent = element.parent`                                                                                     | `parent = element.parent`                                                         |
| Obtener todos los antepasados de un elemento | `parents = list(element.parents)`                                                                             | `parents = list(element.iterancestors())`                                         |
| Buscar un elemento entre los antepasados | `target_parent = element.find_parent("a")`                                                                    | `target_parent = element.find_ancestor(lambda p: p.tag == 'a')`                   |
| Obtener todos los elementos hermanos | No disponible                                                                                                           | `siblings = element.siblings`                                                     |
| Obtener el siguiente elemento hermano | `next_element = element.next_sibling`                                                                         | `next_element = element.next`                                                     |
| Buscar un elemento entre los hermanos | `target_sibling = element.find_next_sibling("a")`<br/>`target_sibling = element.find_previous_sibling("a")`   | `target_sibling = element.siblings.search(lambda s: s.tag == 'a')`                |
| Buscar varios elementos entre los hermanos | `target_sibling = element.find_next_siblings("a")`<br/>`target_sibling = element.find_previous_siblings("a")` | `target_sibling = element.siblings.filter(lambda s: s.tag == 'a')`                |
| Buscar un elemento entre los elementos que siguen | `target_parent = element.find_next("a")`                                                                      | `target_parent = element.below_elements.search(lambda p: p.tag == 'a')`           |
| Buscar varios elementos entre los elementos que siguen | `target_parent = element.find_all_next("a")`                                                                  | `target_parent = element.below_elements.filter(lambda p: p.tag == 'a')`           |
| Buscar un elemento entre los antepasados | `target_parent = element.find_previous("a")` ¹                                                                | `target_parent = element.path.search(lambda p: p.tag == 'a')`                     |
| Buscar varios elementos entre los antepasados | `target_parent = element.find_all_previous("a")` ¹                                                            | `target_parent = element.path.filter(lambda p: p.tag == 'a')`                     |
| Obtener el elemento hermano anterior | `prev_element = element.previous_sibling`                                                                     | `prev_element = element.previous`                                                 |
| Ir a los elementos hijos | `children = list(element.children)`                                                                           | `children = element.children`                                                     |
| Obtener todos los descendientes de un elemento | `children = list(element.descendants)`                                                                        | `children = element.below_elements`                                               |
| Seleccionar enlaces dentro de párrafos con la clase story | `group = soup.select('p.story a')`                                                             | `group = page.css('p.story a')`              |

Una expresión regular compilada que pases directamente a `find()` o `find_all()` de Scrapling busca en el texto de los elementos, no en sus nombres de etiqueta. Usa la lambda de la tabla para buscar por etiqueta, o `page.find_by_regex(r"^b")` para buscar directamente por texto.

¹ **Nota:** `find_previous`/`find_all_previous` de BS4 busca en todos los elementos anteriores según el orden del documento. En cambio, `path` de Scrapling solo devuelve los antepasados, es decir, la cadena de elementos padre. No son equivalentes exactos, pero buscar entre los antepasados cubre el caso más común.

**Un detalle importante**: BeautifulSoup ofrece funciones para modificar la página después de analizarla. Scrapling se centra en extraer los datos con rapidez y deja que después hagas lo que necesites con ellos. Ambas herramientas sirven para extraer datos web, pero una de ellas se especializa en esa tarea :)

### Un ejemplo completo {#putting-it-all-together}

Este ejemplo muestra cómo extraer todos los enlaces de una página con BeautifulSoup y con Scrapling.

**Con BeautifulSoup:**

```python
import requests
from bs4 import BeautifulSoup

url = 'https://example.com'
response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')

links = soup.find_all('a')
for link in links:
    print(link['href'])
```

**Con Scrapling:**

```python
from scrapling import Fetcher

url = 'https://example.com'
page = Fetcher.get(url)

links = page.css('a::attr(href)').getall()
for link in links:
    print(link)
```

Como ves, Scrapling une la obtención de la página y su análisis en un solo paso, lo que simplifica el código y lo hace más eficiente.

!!! abstract "**Notas adicionales:**"

    - **Distintos parsers**: BeautifulSoup permite elegir el motor de análisis, y uno de ellos es `lxml`. Scrapling usa la biblioteca `lxml` de forma predeterminada por motivos de rendimiento.
    - **Tipos de elemento**: En BeautifulSoup, los elementos son objetos `Tag`; en Scrapling, son objetos `Selector`. Ambos ofrecen métodos y propiedades similares para navegar y extraer datos.
    - **Gestión de errores**: Ambas bibliotecas devuelven `None` cuando no encuentran un elemento, por ejemplo con `soup.find()` o `page.find()`. En Scrapling, `page.css()` devuelve una lista `Selectors` vacía si no hay coincidencias. Puedes usar `page.css('.foo').first` para obtener la primera coincidencia o `None`. Para evitar errores, comprueba si recibes `None` o un resultado vacío antes de acceder a las propiedades.
    - **Extracción de texto**: Scrapling ofrece más métodos para trabajar con texto a través de `TextHandler`, como `clean()`. Este método ayuda a quitar espacios sobrantes, espacios seguidos o caracteres no deseados. Consulta la documentación para ver la lista completa.

La documentación explica las funciones de Scrapling con más detalle e incluye todos los argumentos que puedes pasar a cada método.

Esperamos que esta guía te ayude a pasar de BeautifulSoup a Scrapling de forma sencilla. ¡Disfruta extrayendo datos!
