---
title: "Plantillas de spiders para enlaces, mapas del sitio, feeds y Markdown"
description: "Elige entre CrawlSpider, SitemapSpider, XMLFeedSpider, CSVFeedSpider y ContentSpider. Define reglas para recopilar páginas, filas de feeds o documentos Markdown."
---

# Plantillas generales de spiders {#generic-spider-templates}

La mayoría de los rastreos siguen uno de estos dos patrones: seguir enlaces que coincidan con una regla o recorrer todas las URL de un mapa del sitio. Scrapling incluye plantillas para ambos, para que no tengas que repetir la misma lógica de `parse()` cada vez.

`CrawlSpider` y `SitemapSpider` usan `LinkExtractor`, que extrae URL de un `Response` o filtra una URL con `matches()`. `SitemapSpider` también analiza el contenido de sitemap.xml y sitemap_index.xml, con o sin compresión gzip.

Puedes usar `LinkExtractor` directamente dentro de cualquier `Spider.parse()`. Las plantillas solo te ahorran el trabajo de conectar estas piezas.

## CrawlSpider {#crawlspider}

`CrawlSpider` sigue enlaces de forma automática según las reglas que definas.

```python
from scrapling.spiders import CrawlSpider, CrawlRule, LinkExtractor

class QuotesSpider(CrawlSpider):
    name = "blog"
    start_urls = ["https://quotes.toscrape.com/"]

    def rules(self):
        return [
            CrawlRule(LinkExtractor(allow=r"/author/"), callback=self.parse_author),
            CrawlRule(LinkExtractor(allow=r"/page/\d+/")),  # follow pagination, no callback
        ]

    async def parse_author(self, response):
        yield {
            '.author-title': response.css('.author-title::text').get(),
            "birthday": response.css('.author-born-date::text').get(),
            "url": response.url,
        }

result = QuotesSpider().start()
```

Un `CrawlRule` combina un `LinkExtractor` con tres opciones: `callback`, un método del spider; `priority`, para cambiar la prioridad del `Request` generado; y `process_request`, un método que modifica cada `Request` antes de entregarlo. El método `parse()` predeterminado aplica todas las reglas a cada respuesta y entrega un `Request` por cada URL que coincida.

Si una regla no tiene callback, las URL que coincidan pasan al `parse()` predeterminado del spider. Esto es útil para la paginación: puedes extraer los enlaces a las siguientes páginas sin crear otro método para procesarlos.

### Orden de rastreo {#crawl-order}

Configura `crawl_strategy` en `CrawlSpider` o en sus subclases, incluido `ContentSpider`, para elegir la siguiente solicitud pendiente:

| `crawl_strategy` | Orden entre solicitudes con el mismo `Request.priority` |
|------------------|---------------------------------------------------------|
| `"bfs"` (predeterminado) | Primero la solicitud que lleva más tiempo en la cola |
| `"dfs"` | Primero la última solicitud añadida a la cola |

El Scheduler siempre elige primero las solicitudes con mayor `Request.priority`. La estrategia solo ordena las que tienen la misma prioridad.

Usa `concurrent_requests = 1` para procesar una solicitud a la vez en el orden elegido. Se siguen descartando las URL duplicadas: encontrar una URL de nuevo no cambia la posición de su solicitud en la cola. Con varias solicitudes en paralelo, las páginas pueden terminar en otro orden y los niveles o ramas del rastreo pueden mezclarse.

Mantén el mismo `crawl_strategy` al reanudar desde un punto de guardado.

### Combinar reglas con tu propia lógica {#combining-rules-with-custom-logic}

Redefine `parse()` y llama a `super().parse(response)` para mantener las reglas y añadir tus propios resultados:

```python
class MySpider(CrawlSpider):
    def rules(self):
        return [CrawlRule(LinkExtractor(allow=r"/posts/"), callback=self.parse_post)]

    async def parse(self, response):
        yield {"page_url": response.url}
        async for req in super().parse(response):
            yield req
```

### Modificar solicitudes con `process_request` {#mutating-requests-with-process_request}

```python
def add_priority(self, request, response):
    request.priority = 10
    return request

def rules(self):
    return [CrawlRule(
        LinkExtractor(allow=r"/posts/"),
        callback=self.parse_post,
        process_request=self.add_priority,
    )]
```

## SitemapSpider {#sitemapspider}

`SitemapSpider` inicia el rastreo con las URL de sitemap.xml. Usa la misma API `rules()` que `CrawlSpider`, así que se configura de una forma similar.

```python
from scrapling.spiders import SitemapSpider, CrawlRule, LinkExtractor

class MySitemap(SitemapSpider):
    name = "sm"
    sitemap_urls = ["https://example.com/sitemap.xml"]

    def rules(self):
        return [
            CrawlRule(LinkExtractor(allow=r"/posts/"), callback=self.parse_post),
            CrawlRule(LinkExtractor(allow=r"/products/"), callback=self.parse_product),
        ]

    async def parse_post(self, response):
        yield {"title": response.css("h1::text").get()}

    async def parse_product(self, response):
        yield {"sku": response.css(".sku::text").get()}

result = MySitemap().start()
```

### Cómo se elige el callback de cada URL {#how-urls-are-dispatched}

Para cada URL del mapa del sitio, `SitemapSpider` comprueba `LinkExtractor.matches(url)` de cada regla en orden. Usa la primera regla que coincida y entrega un `Request` con su callback. Si ninguna coincide y `rules()` contiene reglas, descarta la URL. Si `rules()` devuelve una lista vacía, todas las URL pasan al método `parse()` del spider. Debes redefinir ese método, ya que de forma predeterminada lanza `NotImplementedError`.

### Índices de mapas del sitio {#sitemap-indexes}

Cuando `SitemapSpider` encuentra un `<sitemapindex>`, que es un mapa de otros mapas del sitio, recorre cada mapa hijo de forma automática. Para elegir cuáles seguir, asigna un `LinkExtractor` a `sitemap_follow`:

```python
class MySitemap(SitemapSpider):
    name = "sm"
    sitemap_urls = ["https://example.com/sitemap.xml"]
    sitemap_follow = LinkExtractor(allow=r"/posts-sitemap-\d+\.xml")  # only post sitemaps
```

### Soporte para robots.txt {#robotstxt-support}

Añade una URL de `robots.txt` directamente a `sitemap_urls`. `SitemapSpider` la detectará, extraerá todos los mapas del sitio que indique y seguirá cada uno:

```python
class MySitemap(SitemapSpider):
    name = "sm"
    sitemap_urls = ["https://example.com/robots.txt"]
```

### URL en otros idiomas {#alternate-language-urls}

Configura `sitemap_alternate_links = True` para que las URL de `<xhtml:link rel="alternate" hreflang="...">` también pasen por tus reglas.

## XMLFeedSpider {#xmlfeedspider}

`XMLFeedSpider` recorre los nodos de un feed XML, como RSS, Atom o feeds de productos. Asigna a `itertag` el nombre del nodo que quieres leer, que es `"item"` de forma predeterminada, y redefine `parse_node()`. Este método se llama una vez por cada nodo que coincida:

```python
from scrapling.spiders import XMLFeedSpider

class RSSSpider(XMLFeedSpider):
    name = "rss"
    start_urls = ["https://example.com/feed.xml"]
    itertag = "item"

    async def parse_node(self, response, node):
        yield {
            "title": node.findtext("title"),
            "link": node.findtext("link"),
            "date": node.findtext("pubDate"),
        }

result = RSSSpider().start()
```

Como los demás callbacks, `parse_node()` también puede entregar objetos `Request`. Por ejemplo, puedes usar `response.follow(node.findtext("link"), callback=self.parse_post)` para recorrer las páginas enlazadas desde el feed.

### Cómo se buscan y analizan los nodos {#how-nodes-are-matched-and-parsed}

Cada nodo que recibe `parse_node()` es un elemento de `lxml` al que se le han quitado todos los espacios de nombres. Así puedes usar `node.findtext("title")`, `node.find("thumbnail").get("url")` y `node.xpath(...)`, que distingue mayúsculas y minúsculas, sin definir mapas de espacios de nombres. Un `itertag` simple como `"entry"` busca nodos por nombre, sin importar su espacio de nombres. Esto sirve para Atom y para la mayoría de los feeds que usan espacios de nombres. Para buscar en uno concreto, usa un `itertag` con prefijo y define ese prefijo en `namespaces`:

```python
class ThumbnailSpider(XMLFeedSpider):
    name = "thumbs"
    start_urls = ["https://example.com/feed.xml"]
    itertag = "media:thumbnail"
    namespaces = (("media", "http://search.yahoo.com/mrss/"),)

    async def parse_node(self, response, node):
        yield {"thumbnail": node.get("url")}
```

Los feeds comprimidos con gzip, ya sea con extensión `.xml.gz` o con un content-type de gzip, se descomprimen de forma automática con las mismas protecciones del spider de mapas del sitio. Si el XML está mal formado, se registra un aviso en lugar de detener el rastreo.

## CSVFeedSpider {#csvfeedspider}

`CSVFeedSpider` recorre las filas de un feed CSV. Redefine `parse_row()`, que recibe cada fila como un diccionario cuyas claves son los nombres de las columnas:

```python
from scrapling.spiders import CSVFeedSpider

class PriceSpider(CSVFeedSpider):
    name = "prices"
    start_urls = ["https://example.com/products.csv"]

    async def parse_row(self, response, row):
        yield {"product": row["title"], "price": float(row["price"])}

result = PriceSpider().start()
```

De forma predeterminada, la primera fila contiene los nombres de las columnas. Si el feed no tiene esa fila, indica los nombres con `headers`. Usa `delimiter`/`quotechar` si el archivo no sigue el formato habitual con comas:

```python
class PriceSpider(CSVFeedSpider):
    name = "prices"
    start_urls = ["https://example.com/products.csv"]
    headers = ["title", "price", "url"]
    delimiter = ";"
```

Los feeds con gzip también se descomprimen de forma automática, igual que con **XMLFeedSpider**.

<a id="sitetomarkdownspider"></a>

## ContentSpider {#contentspider}

`ContentSpider` se basa en **CrawlSpider** para recorrer un sitio y convertir cada página en Markdown limpio, listo para usar con un LLM. Entrega un elemento por página y, si lo deseas, guarda cada página en su propio archivo Markdown:

```python
from scrapling.spiders import ContentSpider

class DocsSpider(ContentSpider):
    name = "docs"
    start_urls = ["https://example.com/docs/"]
    allowed_domains = {"example.com"}
    output_dir = "docs_markdown"

result = DocsSpider().start()
```

Debes definir `allowed_domains` para limitar el rastreo al sitio elegido. La página [Crear sistemas RAG](../ai/building-rag-systems.md) explica todas las opciones y cómo usar los resultados en un proceso RAG.

## Usar `LinkExtractor` directamente {#using-linkextractor-directly}

No necesitas usar las plantillas. `LinkExtractor` funciona dentro de cualquier `Spider`:

```python
from scrapling.spiders import Spider, LinkExtractor

class CustomSpider(Spider):
    name = "custom"
    start_urls = ["https://example.com"]

    def __init__(self):
        super().__init__()
        self._links = LinkExtractor(allow=r"/posts/", deny_domains="ads.example.com")

    async def parse(self, response):
        for url in self._links.extract(response):
            yield response.follow(url, callback=self.parse_post)

    async def parse_post(self, response):
        yield {"title": response.css("h1::text").get()}
```

## Referencia de LinkExtractor {#linkextractor-reference}

| Argumento | Valor predeterminado | Descripción |
|-----------|----------------------|-------------|
| `allow` | `()` | Patrones de URL que se permiten. Si está vacío, se permiten todas. Acepta una cadena, un `Pattern` compilado o un iterable de cualquiera de los dos |
| `deny` | `()` | Patrones de URL que se descartan. Siempre tienen prioridad sobre `allow` |
| `allow_domains` | `()` | Nombres de host permitidos. Incluye sus subdominios de forma automática: `example.com` incluye `api.example.com` |
| `deny_domains` | `()` | Nombres de host que se descartan |
| `restrict_css` | `()` | Selectores CSS que limitan la extracción a una zona del DOM |
| `restrict_xpath` | `()` | Selectores XPath que limitan la extracción a una zona del DOM |
| `tags` | `("a", "area")` | Etiquetas de los elementos en los que se buscan enlaces |
| `attrs` | `("href",)` | Atributos de esas etiquetas de los que se leen las URL |
| `canonicalize` | `True` | Ordena los parámetros de consulta y normaliza la ruta |
| `strip` | `True` | Elimina los espacios en blanco de los extremos de las URL extraídas |
| `keep_fragment` | `False` | Conserva `#fragment` al normalizar la URL |
| `deny_extensions` | `IGNORED_EXTENSIONS` | Extensiones que se descartan, como pdf, zip, imágenes o videos |
| `process` | `None` | Función opcional que se aplica a cada URL extraída antes de filtrarla. Devuelve un valor falso para descartarla |

`LinkExtractor.extract(response)` devuelve una `list[str]` de URL absolutas, filtradas y sin duplicados.

`LinkExtractor.matches(url)` devuelve un `bool`. Aplica los filtros de patrones permitidos y excluidos, dominios y extensiones a una URL. `SitemapSpider` lo usa para elegir las URL sin necesitar un `Response`.
