---
title: "Usa sesiones HTTP y de navegador en un mismo rastreador"
description: "Configura sesiones con nombre y envía las solicitudes del spider por HTTP o mediante un navegador. Reutiliza cookies, inicia sesiones cuando las necesites y consulta el historial de API."
---

# Sesiones de los spiders {#spiders-sessions}

!!! success "Antes de empezar"

    1. Lee la página [Primeros pasos](getting-started.md) para aprender a crear y ejecutar un spider básico.
    2. Revisa los [Conceptos básicos de los fetchers](../fetching/choosing.md) y las diferencias entre las sesiones HTTP y Stealthy.

Un spider puede usar varias sesiones de fetcher al mismo tiempo. Por ejemplo, una sesión HTTP rápida para páginas sencillas y un navegador con protección contra detección para páginas protegidas. Esta página explica cómo configurar y usar las sesiones.

## ¿Qué son las sesiones? {#what-are-sessions}

Una sesión es una instancia de un fetcher ya configurada que permanece activa durante el rastreo. En lugar de crear una conexión o un navegador para cada solicitud, el spider reutiliza las sesiones. Así trabaja más rápido y usa menos recursos.

De forma predeterminada, cada spider crea una sola [FetcherSession](../fetching/static.md). Puedes añadir más sesiones o cambiar la predeterminada redefiniendo `configure_sessions()`. Debes usar la versión asíncrona de cada sesión, como muestra esta tabla:

| Tipo de sesión | Uso |
|----------------|-----|
| [FetcherSession](../fetching/static.md) | Solicitudes HTTP rápidas, sin JavaScript |
| [AsyncStealthySession](../fetching/stealthy.md) | JavaScript, automatización del navegador y evasión de sistemas antibot |

## Configurar sesiones {#configuring-sessions}

Redefine `configure_sessions()` en tu spider para configurar las sesiones. El parámetro `manager` es una instancia de `SessionManager`. Usa `manager.add()` para registrar cada sesión:

```python
from scrapling.spiders import Spider, Response
from scrapling.fetchers import FetcherSession

class MySpider(Spider):
    name = "my_spider"
    start_urls = ["https://example.com"]

    def configure_sessions(self, manager):
        manager.add("default", FetcherSession())

    async def parse(self, response: Response):
        yield {"title": response.css("title::text").get("")}
```

El método `manager.add()` acepta estos argumentos:

| Argumento | Tipo | Valor predeterminado | Descripción |
|-----------|------|----------------------|-------------|
| `session_id` | `str` | *obligatorio* | Nombre con el que se identifica esta sesión en las solicitudes |
| `session` | `Session` | *obligatorio* | Instancia de la sesión |
| `default` | `bool` | `False` | Usa esta sesión como predeterminada |
| `lazy` | `bool` | `False` | Inicia la sesión cuando se use por primera vez |

!!! note "Notas"

    1. Si una solicitud no indica qué sesión debe usar, se usa la predeterminada. Se elige de una de estas formas:
        1. La primera sesión que añades al gestor pasa a ser la predeterminada.
        2. Puedes elegir otra al añadirla con `default=True`.
    2. No necesitas iniciar las sesiones antes de pasarlas al gestor. El spider comprueba cuáles están sin iniciar y las inicia.
    3. Para iniciar una sesión solo cuando se necesite, usa el argumento `lazy` al añadirla. Por ejemplo, puedes abrir el navegador en su primer uso en lugar de hacerlo al iniciar el spider.

## Spider con varias sesiones {#multi-session-spider}

En este ejemplo se usa una sesión HTTP rápida para las páginas de listados y un navegador con protección contra detección para las páginas de detalles que tienen sistemas antibot:

```python
from scrapling.spiders import Spider, Response
from scrapling.fetchers import FetcherSession, AsyncStealthySession

class ProductSpider(Spider):
    name = "products"
    start_urls = ["https://shop.example.com/products"]

    def configure_sessions(self, manager):
        # Fast HTTP for listing pages (default)
        manager.add("http", FetcherSession())

        self.browser_session = AsyncStealthySession(
            headless=True,
            network_idle=True,
            record_requests=True,
        )
        manager.add("stealth", self.browser_session)

    async def parse(self, response: Response):
        for link in response.css("a.product::attr(href)").getall():
            # Route product pages through the stealth session
            yield response.follow(link, sid="stealth", callback=self.parse_product)

        next_page = response.css("a.next::attr(href)").get()
        if next_page:
            yield response.follow(next_page)

    async def parse_product(self, response: Response):
        yield {
            "name": response.css("h1::text").get(""),
            "price": response.css(".price::text").get(""),
        }

    async def on_close(self):
        for api_response in self.browser_session.network.search(
            url_pattern=r"https://api\.shop\.example\.com/.*", limit=None
        ):
            self.logger.info(f"Saved API response: {api_response.url} ({api_response.status})")
```

El ejemplo conserva la instancia del navegador y consulta una sola vez su historial de respuestas de API en `on_close()`, antes de cerrar las sesiones. El historial incluye todas las páginas de productos y se puede seguir leyendo después del cierre. No se espera a que terminen las capturas pendientes y se siguen aplicando los límites del historial.

El parámetro `sid` indica al spider qué sesión debe usar para cada solicitud. Si llamas a `response.follow()` sin `sid`, se hereda el ID de sesión de la solicitud original.

Las sesiones no tienen que ser de clases distintas. También puedes usar varias instancias de la misma clase con configuraciones diferentes:

```python
from scrapling.spiders import Spider, Response
from scrapling.fetchers import FetcherSession

class ProductSpider(Spider):
    name = "products"
    start_urls = ["https://shop.example.com/products"]

    def configure_sessions(self, manager):
        chrome_requests = FetcherSession(impersonate="chrome")
        firefox_requests = FetcherSession(impersonate="firefox")

        manager.add("chrome", chrome_requests)
        manager.add("firefox", firefox_requests)

    async def parse(self, response: Response):
        for link in response.css("a.product::attr(href)").getall():
            yield response.follow(link, callback=self.parse_product)

        next_page = response.css("a.next::attr(href)").get()
        if next_page:
            yield response.follow(next_page, sid="firefox")

    async def parse_product(self, response: Response):
        yield {
            "name": response.css("h1::text").get(""),
            "price": response.css(".price::text").get(""),
        }
```

También puedes reservar una sesión, con sus propias cookies y su estado, para ciertas solicitudes.

## Argumentos de la sesión {#session-arguments}

Los argumentos adicionales de un `Request`, o de `response.follow(**kwargs)`, se pasan al método de descarga de la sesión. Así puedes ajustar una solicitud concreta sin cambiar la configuración de toda la sesión:

```python
async def parse(self, response: Response):
    # Pass extra headers for this specific request
    yield Request(
        "https://api.example.com/data",
        headers={"Authorization": "Bearer token123"},
        callback=self.parse_api,
    )

    # Use a different HTTP method
    yield Request(
        "https://example.com/submit",
        method="POST",
        data={"field": "value"},
        sid="firefox",
        callback=self.parse_result,
    )
```

!!! warning "Aviso"

    Normalmente, con `FetcherSession`, `Fetcher` o `AsyncFetcher`, eliges el método HTTP llamando a `.get()`, `.post()` u otro método. Dentro de un spider no puedes hacerlo así con `FetcherSession`. Las solicitudes usan _HTTP GET_ de forma predeterminada. Para usar otro método HTTP, pásalo en el argumento `method`, como en el ejemplo anterior. Esto permite que todos los tipos de sesión compartan la misma interfaz `Request`.

Con la sesión `"stealth"` (`AsyncStealthySession`) del ejemplo anterior, puedes pasar argumentos propios del navegador, como `wait_selector`, `page_action` o `extra_headers`:

```python
async def parse(self, response: Response):
    # Use Cloudflare solver with the `AsyncStealthySession` we configured above
    yield Request(
        "https://nopecha.com/demo/cloudflare",
        sid="stealth",
        callback=self.parse_result,
        solve_cloudflare=True,
        block_webrtc=True,
        hide_canvas=True,
        google_search=True,
    )

    yield response.follow(
        "/dynamic-page",
        sid="stealth",
        callback=self.parse_dynamic,
        wait_selector="div.loaded",
        network_idle=True,
    )
```

!!! warning "Aviso"

    `response.follow()` hereda los argumentos de sesión (**kwargs) de la solicitud original, salvo `method`, `params`, `data`, `json`, `files` y `multipart`. Por eso, al seguir un enlace después de un POST se envía un GET simple. Los argumentos nuevos tienen prioridad sobre los heredados.

```python
from scrapling.spiders import Spider, Response
from scrapling.fetchers import FetcherSession

class ProductSpider(Spider):
    name = "products"
    start_urls = ["https://shop.example.com/products"]

    def configure_sessions(self, manager):
        manager.add("http", FetcherSession(impersonate='chrome'))

    async def parse(self, response: Response):
        # I don't want the follow request to impersonate a desktop Chrome like the previous request, but a mobile one
        # so I override it like this
        for link in response.css("a.product::attr(href)").getall():
            yield response.follow(link, impersonate="chrome131_android", callback=self.parse_product)

        next_page = response.css("a.next::attr(href)").get()
        if next_page:
            yield response.follow(next_page)

    async def parse_product(self, response: Response):
        yield {
            "name": response.css("h1::text").get(""),
            "price": response.css(".price::text").get(""),
        }
```

!!! info "Información"

    Al cerrar el spider, el gestor comprueba si quedan sesiones activas y las cierra antes de terminar.
