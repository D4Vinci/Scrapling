---
title: "Crea tu primer rastreador web en Python con Scrapling"
description: "Crea un spider que extraiga datos, siga la paginación y exporte los resultados. Aprende a usar URL iniciales, callbacks, límites de dominio y robots.txt."
---

# Primeros pasos {#getting-started}

## Introducción {#introduction}

!!! success "Antes de empezar"

    1. Lee la página [Conceptos básicos de los fetchers](../fetching/choosing.md) para conocer los distintos tipos de fetcher y cuándo usar cada uno.
    2. Lee la página [Clases principales](../parsing/main_classes.md) para conocer las clases [Selector](../parsing/main_classes.md#selector) y [Response](../fetching/choosing.md#response-object).
    3. Lee la página [Arquitectura](architecture.md) para entender cómo funciona el sistema de spiders.

El sistema de spiders te permite rastrear varias páginas a la vez con unas pocas líneas de código. Si ya has usado Scrapy, reconocerás su forma de trabajar. Si no, esta guía explica todo lo que necesitas para empezar.

## Tu primer spider {#your-first-spider}

Un spider es una clase que define cómo recorrer sitios web y extraer sus datos. Este es el ejemplo más sencillo:

```python
from scrapling.spiders import Spider, Response

class QuotesSpider(Spider):
    name = "quotes"
    start_urls = ["https://quotes.toscrape.com"]

    async def parse(self, response: Response):
        for quote in response.css("div.quote"):
            yield {
                "text": quote.css("span.text::text").get(""),
                "author": quote.css("small.author::text").get(""),
            }
```

Cada spider necesita tres cosas:

1. **`name`**: un nombre único para el spider.
2. **`start_urls`**: una lista de URL desde las que empezar el rastreo.
3. **`parse()`**: un método generador asíncrono que procesa cada respuesta y entrega los resultados.

El método `parse()` contiene la lógica de extracción. Usa los mismos métodos de selección de [Selector](../parsing/main_classes.md#selector)/[Response](../fetching/choosing.md#response-object) de Scrapling y entrega los elementos extraídos como diccionarios con `yield`.

## Ejecutar el spider {#running-the-spider}

Para ejecutar tu spider, crea una instancia y llama a `start()`:

```python
result = QuotesSpider().start()
```

El método `start()` se encarga de la ejecución asíncrona, así que no necesitas gestionar bucles de eventos. Mientras el spider se ejecuta, registra lo que ocurre en la terminal. Al terminar, muestra estadísticas detalladas.

También puedes consultar esas estadísticas en el objeto `CrawlResult` que devuelve:

```python
result = QuotesSpider().start()

# Access scraped items
for item in result.items:
    print(item["text"], "-", item["author"])

# Check statistics
print(f"Scraped {result.stats.items_scraped} items")
print(f"Made {result.stats.requests_count} requests")
print(f"Took {result.stats.elapsed_seconds:.1f} seconds")

# Did the crawl finish or was it paused?
print(f"Completed: {result.completed}")
```

## Seguir enlaces {#following-links}

La mayoría de los rastreos necesitan seguir enlaces entre varias páginas. Usa `response.follow()` para crear las siguientes solicitudes:

```python
from scrapling.spiders import Spider, Response

class QuotesSpider(Spider):
    name = "quotes"
    start_urls = ["https://quotes.toscrape.com"]

    async def parse(self, response: Response):
        # Extract items from the current page
        for quote in response.css("div.quote"):
            yield {
                "text": quote.css("span.text::text").get(""),
                "author": quote.css("small.author::text").get(""),
            }

        # Follow the "next page" link
        next_page = response.css("li.next a::attr(href)").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)
```

`response.follow()` resuelve las URL relativas con la URL de la página actual. También usa esa página como valor de la cabecera `Referer` de forma predeterminada.

Puedes enviar las solicitudes a distintos callbacks según el tipo de página:

```python
async def parse(self, response: Response):
    for link in response.css("a.product-link::attr(href)").getall():
        yield response.follow(link, callback=self.parse_product)

async def parse_product(self, response: Response):
    yield {
        "name": response.css("h1::text").get(""),
        "price": response.css(".price::text").get(""),
    }
```

!!! note "Nota"

    Todos los callbacks deben ser métodos generadores asíncronos, con `async def` y `yield`.

## Exportar datos {#exporting-data}

El objeto `ItemList` de `result.items` incluye métodos para exportar los datos:

```python
result = QuotesSpider().start()

# Export as JSON
result.items.to_json("quotes.json")

# Export as JSON with pretty-printing
result.items.to_json("quotes.json", indent=True)

# Export as JSON Lines (one JSON object per line)
result.items.to_jsonl("quotes.jsonl")

# Export as CSV or XML
result.items.to_csv("quotes.csv")
result.items.to_xml("quotes.xml")
```

Todos crean los directorios necesarios si aún no existen.

`to_csv()` crea una columna para cada clave que encuentre en los elementos. Si un elemento no tiene una clave, deja esa celda vacía. Usa `fields=[...]` para elegir las columnas y su orden, o `delimiter="\t"` para crear un archivo TSV. `to_xml()` coloca cada elemento dentro de una etiqueta `<item>`, bajo una raíz `<items>`. Puedes cambiar ambos nombres con `root_tag` y `item_tag`.

En ambos formatos, los valores que no sean escalares simples, como una lista o un diccionario anidado, se guardan como JSON para no perder datos.

## Limitar los dominios {#filtering-domains}

Usa `allowed_domains` para limitar el spider a ciertos dominios. Así evitas que siga por error enlaces a otros sitios:

```python
class MySpider(Spider):
    name = "my_spider"
    start_urls = ["https://example.com"]
    allowed_domains = {"example.com"}

    async def parse(self, response: Response):
        for link in response.css("a::attr(href)").getall():
            # Links to other domains are silently dropped
            yield response.follow(link, callback=self.parse)
```

Los subdominios se incluyen de forma automática. Por ejemplo, `allowed_domains = {"example.com"}` también permite `sub.example.com`, `blog.example.com`, etc.

Cada solicitud descartada se cuenta en `stats.offsite_requests_count`, para que puedas ver cuántas se omitieron.

## Respetar robots.txt {#robotstxt-compliance}

Configura `robots_txt_obey = True` para que el spider consulte las reglas de robots.txt antes de rastrear un dominio:

```python
class PoliteSpider(Spider):
    name = "polite"
    start_urls = ["https://example.com"]
    robots_txt_obey = True

    async def parse(self, response: Response):
        for link in response.css("a::attr(href)").getall():
            yield response.follow(link, callback=self.parse)
```

Al activar esta opción, el spider:

1. **Descarga robots.txt** para todos los dominios de `start_urls` antes de empezar el rastreo. Estas descargas se hacen al mismo tiempo.
2. **Comprueba cada solicitud** con las reglas `Disallow` del dominio. Descarta las solicitudes no permitidas sin mostrar mensajes y las cuenta en `stats.robots_disallowed_count`.
3. **Respeta las instrucciones `Crawl-delay` y `Request-rate`** usando el mayor valor entre la instrucción y tu `download_delay`. Así, robots.txt puede aumentar la espera, pero nunca reducirla. Si AutoThrottle está activo, su espera máxima también limita este valor. Configura `autothrottle_max_delay` con un valor suficiente para respetar la espera necesaria.

Los archivos robots.txt se descargan con la sesión predeterminada del spider y se guardan en caché por dominio durante todo el rastreo. Si se descubre un dominio que no estaba en `start_urls`, su robots.txt se descarga antes de la primera solicitud a ese dominio.

**Nota:** `robots_txt_obey` está desactivado de forma predeterminada para evitar cambios de comportamiento inesperados. Al activarlo, no cambia la configuración de concurrencia (`concurrent_requests`, `concurrent_requests_per_domain`). Solo ajusta la espera entre solicitudes.

Si prefieres no elegir un `download_delay` a mano, configura `autothrottle_enabled = True`. El spider ajustará la espera de cada dominio según lo rápido que responda y reducirá el ritmo si detecta bloqueos. Consulta [AutoThrottle](advanced.md#autothrottle).

## Siguientes pasos {#whats-next}

Ahora que conoces lo básico, puedes consultar:

- [Solicitudes y respuestas](requests-responses.md): prioridad, eliminación de duplicados, metadatos y más.
- [Sesiones](sessions.md): distintos tipos de fetcher (HTTP, navegador y navegador con protección contra detección) en un mismo spider.
- [Gestión de proxies y bloqueos](proxy-blocking.md): rotación de proxies entre solicitudes y gestión de bloqueos.
- [Funciones avanzadas](advanced.md): control de concurrencia, AutoThrottle, pausa y reanudación, streaming, hooks del ciclo de vida y registros.
