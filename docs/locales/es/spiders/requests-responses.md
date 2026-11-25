---
title: "Solicitudes, callbacks y Response.follow en los spiders"
description: "Crea solicitudes, pasa metadatos y sigue enlaces con response.follow. Aprende a usar callbacks, prioridades y eliminación de solicitudes duplicadas."
---

# Solicitudes y respuestas {#requests-responses}

!!! success "Antes de empezar"

    1. Lee la página [Primeros pasos](getting-started.md) para aprender a crear y ejecutar un spider básico.

Esta página explica el objeto `Request`: cómo crear solicitudes, pasar datos entre callbacks, controlar la prioridad y los duplicados, y seguir enlaces con `response.follow()`.

## El objeto Request {#the-request-object}

Un `Request` representa una URL que quieres obtener. Puedes crear solicitudes directamente o mediante `response.follow()`:

```python
from scrapling.spiders import Request

# Direct construction
request = Request(
    "https://example.com/page",
    callback=self.parse_page,
    priority=5,
)

# Via response.follow (preferred in callbacks)
request = response.follow("/page", callback=self.parse_page)
```

Estos son todos los argumentos que acepta `Request`:

| Argumento | Tipo | Valor predeterminado | Descripción |
|-----------|------|----------------------|-------------|
| `url` | `str` | *obligatorio* | URL que se va a obtener |
| `sid` | `str` | `""` | ID de sesión. Envía la solicitud a una sesión concreta (consulta [Sesiones](sessions.md)) |
| `callback` | `callable` | `None` | Método generador asíncrono que procesa la respuesta. Usa `parse()` de forma predeterminada |
| `priority` | `int` | `0` | Los valores más altos se procesan primero |
| `dont_filter` | `bool` | `False` | Si es `True`, permite solicitudes duplicadas |
| `meta` | `dict` | `{}` | Metadatos de cualquier tipo que se pasan a la respuesta |
| `**kwargs` | | | Argumentos adicionales que se pasan al método de descarga de la sesión, como `headers`, `method` o `data` |

Los argumentos adicionales se envían directamente a la sesión. Por ejemplo, para hacer una solicitud POST:

```python
yield Request(
    "https://example.com/api",
    method="POST",
    data={"key": "value"},
    callback=self.parse_result,
)
```

## Response.follow() {#responsefollow}

`response.follow()` crea un objeto `Request` nuevo y resuelve las URL relativas con la URL de la respuesta. Conserva la sesión, el callback y la prioridad asociados, salvo que indiques otros valores.

`sid=""`, `callback=None` y `priority=None` heredan los valores de la solicitud asociada. `priority=0` sustituye la prioridad heredada de forma explícita. Los metadatos están vacíos por defecto. No se copian cabeceras, cookies, credenciales, proxy ni opciones de obtención de la solicitud anterior, incluso al seguir un enlace al mismo dominio.

La configuración y el almacén de cookies de la sesión elegida siguen activos. Elige otra sesión con `sid` si no quieres usar esos ajustes.

Seguir un enlace después de un POST envía un GET, salvo que indiques otro valor de `method`.

```python
async def parse(self, response: Response):
    # Minimal - inherits callback, sid, priority from current request
    yield response.follow("/next-page")

    # Override specific fields
    yield response.follow(
        "/product/123",
        callback=self.parse_product,
        sid="stealth",
        priority=10,
    )

    # Pass additional metadata to
    yield response.follow(
        "/details",
        callback=self.parse_details,
        meta={"category": "electronics"},
    )
```

| Argumento | Tipo | Valor predeterminado | Descripción |
| --- | --- | --- | --- |
| `url` | `str` | *obligatorio* | URL absoluta o relativa |
| `sid` | `str` | `""` | Si está vacío, hereda la sesión de la solicitud asociada |
| `callback` | `callable` | `None` | Si es `None`, hereda el callback de la solicitud asociada |
| `priority` | `int` o `None` | `None` | Si es `None`, hereda la prioridad asociada; `0` la sustituye explícitamente |
| `dont_filter` | `bool` | `False` | Permite solicitudes duplicadas |
| `meta` | `dict` | `None` | Solo los metadatos de esta solicitud, vacíos por defecto |
| `referer_flow` | `bool` | `True` | Añade la URL de la respuesta actual como Referer |
| `**kwargs` | |  | Opciones explícitas que se pasan a la sesión |

### Desactivar el envío de Referer {#disabling-referer-flow}

`referer_flow=True` sigue siendo el valor predeterminado. `follow()` añade la URL actual como Referer para HTTP y el navegador, y establece `google_search=False`. No copia las cabeceras de la solicitud anterior. Para desactivar estos valores automáticos:

```python
yield response.follow("/page", referer_flow=False)
```

Con `referer_flow=False`, el método no añade Referer ni cambia `google_search`. Las cabeceras que indiques y los ajustes predeterminados de la sesión o del motor siguen activos. Para indicar otro Referer para HTTP:

```python
yield response.follow(
    "/page",
    referer_flow=False,
    headers={"Referer": "https://example.com/"},
)
```

Para el navegador, usa `extra_headers` y establece `google_search=False` si es necesario.

## Callbacks {#callbacks}

Los callbacks son métodos generadores asíncronos del spider que procesan las respuestas. Deben usar `yield` para entregar uno de estos tres tipos:

- **`dict`**: un elemento extraído que se añade a los resultados.
- **`Request`**: una nueva solicitud que se añade a la cola.
- **`None`**: se ignora sin mostrar mensajes.

```python
class MySpider(Spider):
    name = "my_spider"
    start_urls = ["https://example.com"]

    async def parse(self, response: Response):
        # Yield items (dicts)
        yield {"url": response.url, "title": response.css("title::text").get("")}

        # Yield follow-up requests
        for link in response.css("a::attr(href)").getall():
            yield response.follow(link, callback=self.parse_page)

    async def parse_page(self, response: Response):
        yield {"content": response.css("article::text").get("")}
```

!!! tip "Nota"

    Todos los callbacks deben usar `async def` y `yield`, no `return`. Aunque un callback solo entregue elementos y no genere nuevas solicitudes, debe seguir siendo un generador asíncrono.

## Prioridad de las solicitudes {#request-priority}

Las solicitudes con un valor de prioridad más alto se procesan primero. Esto resulta útil cuando necesitas procesar unas páginas antes que otras:

```python
async def parse(self, response: Response):
    # High priority - process product pages first
    for link in response.css("a.product::attr(href)").getall():
        yield response.follow(link, callback=self.parse_product, priority=10)

    # Low priority - pagination links processed after products
    next_page = response.css("a.next::attr(href)").get()
    if next_page:
        yield response.follow(next_page, callback=self.parse, priority=0)
```

Sin `priority`, `response.follow()` hereda la prioridad de la solicitud asociada. Pasa `priority=0` para restablecerla a cero de forma explícita.

## Eliminar duplicados {#deduplication}

El spider evita repetir solicitudes mediante una huella calculada a partir de la URL, el método HTTP, el cuerpo y el ID de sesión. Si dos solicitudes generan la misma huella, la segunda se descarta sin mostrar mensajes.

Para permitir solicitudes duplicadas, por ejemplo al volver a una página después de iniciar sesión, usa `dont_filter=True`:

```python
yield Request("https://example.com/dashboard", dont_filter=True, callback=self.parse_dashboard)

# Or with response.follow
yield response.follow("/dashboard", dont_filter=True, callback=self.parse_dashboard)
```

Puedes ajustar qué datos se incluyen en la huella con estos atributos de clase del spider:

| Atributo | Valor predeterminado | Efecto |
|----------|----------------------|--------|
| `fp_include_kwargs` | `False` | Incluye en la huella los argumentos adicionales de la solicitud que pasaste al método de descarga de la sesión, como las cabeceras |
| `fp_keep_fragments` | `False` | Conserva los fragmentos de la URL (`#section`) al calcular la huella |
| `fp_include_headers` | `False` | Incluye las cabeceras de la solicitud en la huella |

Por ejemplo, para tratar `https://example.com/page#section1` y `https://example.com/page#section2` como URL distintas:

```python
class MySpider(Spider):
    name = "my_spider"
    fp_keep_fragments = True
    # ...
```

## Metadatos de la solicitud {#request-meta}

El diccionario `meta` permite pasar datos entre callbacks. Es útil cuando necesitas información de una página para procesar otra:

```python
async def parse(self, response: Response):
    for product in response.css("div.product"):
        category = product.css("span.category::text").get("")
        link = product.css("a::attr(href)").get()
        if link:
            yield response.follow(
                link,
                callback=self.parse_product,
                meta={"category": category},
            )

async def parse_product(self, response: Response):
    yield {
        "name": response.css("h1::text").get(""),
        "price": response.css(".price::text").get(""),
        # Access meta from the request
        "category": response.meta.get("category", ""),
    }
```

`response.follow()` usa solo los metadatos que pases en `meta`. No los combina con los de la respuesta anterior. Pasa las claves que necesite la solicitud nueva.

El sistema de spiders también guarda algunos metadatos de forma automática. Por ejemplo, si la rotación de proxies está activa, el proxy usado en una solicitud está disponible en `response.meta["proxy"]`.
