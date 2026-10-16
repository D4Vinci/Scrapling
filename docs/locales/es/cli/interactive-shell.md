---
title: "Prueba la extracción de datos en el shell interactivo de Scrapling"
description: "Obtén páginas, prueba selectores y revisa resultados en un shell de IPython. Convierte comandos curl, reutiliza respuestas recientes y prueba tu código."
---

# Guía del shell interactivo de Scrapling {#scrapling-interactive-shell-guide}

<script src="https://asciinema.org/a/736339.js" id="asciicast-736339" async data-autoplay="1" data-loop="1" data-cols="225" data-rows="40" data-start-at="00:06" data-speed="1.5" data-theme="tango"></script>

**Un entorno REPL para extraer datos web, pensado para desarrolladores y profesionales de datos**

El shell interactivo de Scrapling es un entorno basado en IPython, preparado para extraer datos web. Da acceso inmediato a todas las funciones de Scrapling, atajos útiles, gestión automática de páginas y herramientas como la conversión de comandos curl.

!!! success "Requisitos previos"

    1. Lee la página de [conceptos básicos de los fetchers](../fetching/choosing.md) para entender qué es el [objeto Response](../fetching/choosing.md#response-object) y qué fetcher usar.
    2. Lee la página de [selección de elementos](../parsing/selection.md) para aprender a buscar y extraer elementos de un objeto [Selector](../parsing/main_classes.md#selector)/[Response](../fetching/choosing.md#response-object).
    3. Lee la página de [clases principales](../parsing/main_classes.md) para conocer las propiedades y los métodos que la clase [Response](../fetching/choosing.md#response-object) hereda de [Selector](../parsing/main_classes.md#selector).
    4. Lee al menos una página de la sección de fetchers para las solicitudes que usarás aquí: [solicitudes HTTP](../fetching/static.md) u [obtención con navegador](../fetching/stealthy.md).

## ¿Por qué usar el shell interactivo? {#why-use-the-interactive-shell}

Con el shell interactivo puedes explorar y probar al momento, sin tener que editar y ejecutar un script en cada intento. Es útil para:

- **Crear prototipos rápidos**: Prueba estrategias de extracción al instante.
- **Explorar datos**: Navega por sitios web y extrae datos de forma interactiva.
- **Aprender Scrapling**: Prueba sus funciones en tiempo real.
- **Depurar scrapers**: Revisa las solicitudes y sus resultados paso a paso.
- **Convertir procesos**: Convierte un comando curl de las DevTools del navegador en una solicitud de Fetcher con una sola línea.

## Primeros pasos {#getting-started}

### Iniciar el shell {#launch-the-shell}

```bash
# Start the interactive shell
scrapling shell

# Execute code and exit (useful for scripting)
scrapling shell -c "get('https://quotes.toscrape.com'); print(len(page.css('.quote')))"

# Set logging level
scrapling shell --loglevel info
```

Al abrirlo, verás el banner de Scrapling y podrás empezar a extraer datos, como en el vídeo anterior:

```python
# No imports needed - everything is ready!
get('https://news.ycombinator.com')

# Explore the page structure
page.css('a')[:5]  # Look at first 5 links

# Refine your selectors
stories = page.css('.titleline>a')
len(stories)  # 30

# Extract specific data
for story in stories[:3]:
    title = story.text
    url = story['href']
    print(f"{title}: {url}")

# Try different approaches
titles = page.css('.titleline>a::text')  # Direct text extraction
urls = page.css('.titleline>a::attr(href)')  # Direct attribute extraction
```

## Atajos incluidos {#built-in-shortcuts}

El shell ofrece atajos para evitar código repetido:

- **`get(url, **kwargs)`** - Solicitud HTTP GET (en lugar de `Fetcher.get`).
- **`post(url, **kwargs)`** - Solicitud HTTP POST (en lugar de `Fetcher.post`).
- **`put(url, **kwargs)`** - Solicitud HTTP PUT (en lugar de `Fetcher.put`).
- **`delete(url, **kwargs)`** - Solicitud HTTP DELETE (en lugar de `Fetcher.delete`).
- **`fetch(url, **kwargs)`** - Obtención con un navegador Stealthy (en lugar de `StealthyFetcher.fetch`).

Las clases más usadas están disponibles sin importarlas, entre ellas `Fetcher`, `AsyncFetcher`, `StealthyFetcher` y `Selector`.

### Gestión automática de páginas {#smart-page-management}

El shell lleva un registro de tus solicitudes y páginas:

- **Acceso a la página actual**

    `page` y `response` se actualizan de forma automática con la última página obtenida:

    ```python
    get('https://quotes.toscrape.com')
    # 'page' and 'response' both refer to the last fetched page
    page.url  # 'https://quotes.toscrape.com'
    response.status  # Prints 200; Same as page.status
    ```

- **Historial de páginas**

    `pages` conserva las últimas cinco páginas en un objeto `Selectors`:

    ```python
    get('https://site1.com')
    get('https://site2.com')
    get('https://site3.com')
    
    # Access last 5 pages
    len(pages)  # `Selectors` object with `page` history -> 3
    pages[0].url  # First page in history -> 'https://site1.com'
    pages[-1].url  # Most recent page -> 'https://site3.com'
    
    # Work with historical pages
    for i, old_page in enumerate(pages):
        print(f"Page {i}: {old_page.url} - {old_page.status}")
    ```

## Otros comandos útiles {#additional-helpful-commands}

### Ver la página {#page-visualization}

Abre las páginas obtenidas en tu navegador:

```python
get('https://quotes.toscrape.com')
view(page)  # Opens the page HTML in your default browser
```

### Integración con comandos curl {#curl-command-integration}

El shell incluye las funciones `uncurl` y `curl2fetcher` para convertir comandos curl de las DevTools del navegador en solicitudes de `Fetcher`.

Primero, copia una solicitud como comando curl:

<img src="../assets/scrapling_shell_curl.png" title="Copiar una solicitud como comando curl desde Chrome" alt="Copiar una solicitud como comando curl desde Chrome" style="width: 70%;"/>

- **Convertir un comando curl en un objeto de solicitud**

    ```python
    curl_cmd = '''curl 'https://scrapling.requestcatcher.com/post' \
      -X POST \
      -H 'Content-Type: application/json' \
      -d '{"name": "test", "value": 123}' '''
    
    request = uncurl(curl_cmd)
    request.method  # -> 'post'
    request.url  # -> 'https://scrapling.requestcatcher.com/post'
    request.headers  # -> {'Content-Type': 'application/json'}
    ```

- **Ejecutar un comando curl directamente**

    ```python
    # Convert and execute in one step
    curl2fetcher(curl_cmd)
    page.status  # -> 200
    ```

### Funciones de IPython {#ipython-features}

El shell hereda todas las funciones de IPython:

```python
# Magic commands
%time page = get('https://example.com')  # Time execution
%history  # Show command history
%save filename.py 1-10  # Save commands 1-10 to file

# Tab completion works everywhere
page.c<TAB>  # Shows: css, cookies, headers, etc.
Fetcher.<TAB>  # Shows all Fetcher methods

# Object inspection
get? # Show get documentation
```

## Ejemplos {#examples}

Estos son algunos ejemplos generados con IA:

#### Recopilar datos de tiendas en línea {#e-commerce-data-collection}

```python
# Start with product listing page
catalog = get('https://shop.example.com/products')

# Find product links
product_links = catalog.css('.product-link::attr(href)').getall()
print(f"Found {len(product_links)} products")

# Sample a few products first
for link in product_links[:3]:
    product = get(catalog.urljoin(link))
    name = product.css('.product-name::text').get('')
    price = product.css('.price::text').get('')
    print(f"{name}: {price}")

# Scale up with sessions for efficiency
from scrapling.fetchers import FetcherSession
with FetcherSession() as session:
    products = []
    for link in product_links:
        product = session.get(catalog.urljoin(link))
        products.append({
            'name': product.css('.product-name::text').get(''),
            'price': product.css('.price::text').get(''),
            'url': link
        })
```

#### Integrar y probar API {#api-integration-and-testing}

```python
>>> # Test API endpoints interactively
>>> response = get('https://jsonplaceholder.typicode.com/posts/1')
>>> response.json()
{'userId': 1, 'id': 1, 'title': 'sunt aut...', 'body': 'quia et...'}

>>> # Test POST requests
>>> new_post = post('https://jsonplaceholder.typicode.com/posts', 
...                 json={'title': 'Test Post', 'body': 'Test content', 'userId': 1})
>>> new_post.json()['id']
101

>>> # Test with different data
>>> updated = put('https://jsonplaceholder.typicode.com/posts/1',
...               json={'title': 'Updated Title'})
```

## Obtener ayuda {#getting-help}

Si necesitas más ayuda de la que ofrece la terminal, consulta:

- [Documentación de Scrapling](https://scrapling.readthedocs.io/es/latest/)
- [Comunidad de Discord](https://discord.gg/EMgGbDceNQ)
- [Incidencias en GitHub](https://github.com/D4Vinci/Scrapling/issues)

¡Eso es todo! Disfruta extrayendo datos. El shell hace que obtener datos web sea tan fácil como una conversación.
