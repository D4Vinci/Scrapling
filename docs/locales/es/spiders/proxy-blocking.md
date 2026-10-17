---
title: "Rota proxies y reintenta las solicitudes bloqueadas"
description: "Usa proxies y estrategias de rotación en los spiders de Scrapling. Detecta bloqueos, reintenta solicitudes y cambia de sesiones HTTP a sesiones de navegador."
---

# Gestión de proxies y bloqueos {#proxy-management-and-handling-blocks}

## Introducción {#introduction}

!!! success "Antes de empezar"

    1. Lee la página [Primeros pasos](getting-started.md) para aprender a crear y ejecutar un spider básico.
    2. Lee la página [Sesiones](sessions.md) para aprender a configurarlas.

Al extraer muchos datos, a menudo necesitarás alternar entre varios proxies para evitar límites de solicitudes y bloqueos. `ProxyRotator` de Scrapling facilita este proceso. Funciona con todos los tipos de sesión y se integra con los reintentos de solicitudes bloqueadas del spider.

Si no sabes qué es un proxy o cómo elegir uno, [esta guía puede ayudarte](https://substack.thewebscraping.club/p/everything-about-proxies).

## ProxyRotator {#proxyrotator}

La clase `ProxyRotator` gestiona una lista de proxies y alterna entre ellos de forma automática. Pásala a cualquier tipo de sesión mediante `proxy_rotator`:

```python
from scrapling.spiders import Spider, Response
from scrapling.fetchers import FetcherSession, ProxyRotator

class MySpider(Spider):
    name = "my_spider"
    start_urls = ["https://example.com"]

    def configure_sessions(self, manager):
        rotator = ProxyRotator([
            "http://proxy1:8080",
            "http://proxy2:8080",
            "http://user:pass@proxy3:8080",
        ])
        manager.add("default", FetcherSession(proxy_rotator=rotator))

    async def parse(self, response: Response):
        # Check which proxy was used
        print(f"Proxy used: {response.meta.get('proxy')}")
        yield {"title": response.css("title::text").get("")}
```

Cada solicitud recibe el siguiente proxy de la rotación. El proxy usado se guarda en `response.meta["proxy"]`, para que puedas saber cuál obtuvo cada página.

Para usarlo con sesiones de navegador, puedes configurarlo así:

```python
from scrapling.fetchers import AsyncStealthySession, ProxyRotator

# String proxies work for all session types
rotator = ProxyRotator([
    "http://proxy1:8080",
    "http://proxy2:8080",
])

# Dict proxies (Playwright format) work for browser sessions
rotator = ProxyRotator([
    {"server": "http://proxy1:8080", "username": "user", "password": "pass"},
    {"server": "http://proxy2:8080"},
])

# Then inside the spider
def configure_sessions(self, manager):
    rotator = ProxyRotator(["http://proxy1:8080", "http://proxy2:8080"])
    manager.add("browser", AsyncStealthySession(proxy_rotator=rotator))
```

!!! info "Información"

    1. No puedes usar `proxy_rotator` junto con los parámetros fijos `proxy` o `proxies` en la misma sesión. Elige una opción al configurar la sesión. Después puedes indicar un proxy distinto en una solicitud concreta, como se explica más adelante.
    2. De forma predeterminada, las sesiones de navegador usan un contexto persistente con un grupo de pestañas. Los navegadores no permiten elegir un proxy por pestaña. Por eso, al usar `ProxyRotator`, el fetcher abre un contexto independiente para cada proxy, con una pestaña por contexto. Cuando termina el trabajo de la pestaña, se cierran tanto la pestaña como su contexto.

## Estrategias de rotación propias {#custom-rotation-strategies}

De forma predeterminada, `ProxyRotator` recorre los proxies en orden y vuelve al primero cuando llega al final.

Puedes pasar una función con tu propia estrategia para cambiar este comportamiento. Debe tener esta firma:

```python
from scrapling.core._types import ProxyType

def my_strategy(proxies: list, current_index: int) -> tuple[ProxyType, int]:
    ...
```

La función recibe la lista de proxies y el índice actual. Debe devolver el proxy elegido y el siguiente índice.

Estos son algunos ejemplos de estrategias que puedes usar.

### Rotación aleatoria {#random-rotation}

```python
import random
from scrapling.fetchers import ProxyRotator

def random_strategy(proxies, current_index):
    idx = random.randint(0, len(proxies) - 1)
    return proxies[idx], idx

rotator = ProxyRotator(
    ["http://proxy1:8080", "http://proxy2:8080", "http://proxy3:8080"],
    strategy=random_strategy,
)
```

### Rotación por pesos {#weighted-rotation}

```python
import random

def weighted_strategy(proxies, current_index):
    # First proxy gets 60% of traffic, others split the rest
    weights = [60] + [40 // (len(proxies) - 1)] * (len(proxies) - 1)
    proxy = random.choices(proxies, weights=weights, k=1)[0]
    return proxy, current_index  # Index doesn't matter for weighted

rotator = ProxyRotator(proxies, strategy=weighted_strategy)
```

## Elegir un proxy para una solicitud {#per-request-proxy-override}

Puedes omitir la rotación en una solicitud concreta pasando el argumento `proxy=`:

```python
async def parse(self, response: Response):
    # This request uses the rotator's next proxy
    yield response.follow("/page1", callback=self.parse_page)

    # This request uses a specific proxy, bypassing the rotator
    yield response.follow(
        "/special-page",
        callback=self.parse_page,
        proxy="http://special-proxy:8080",
    )
```

Esto es útil cuando una página requiere un proxy concreto, por ejemplo uno de una región específica para acceder a contenido local.

## Gestionar solicitudes bloqueadas {#blocked-request-handling}

El spider incluye detección de bloqueos y reintentos. De forma predeterminada, considera bloqueadas las respuestas con estos códigos HTTP: `401`, `403`, `407`, `429`, `444`, `500`, `502`, `503` y `504`.

El sistema de reintentos funciona así:

1. Cuando llega una respuesta, el spider llama a `is_blocked(response)`.
2. Si detecta un bloqueo, copia la solicitud y llama a `retry_blocked_request()` para que puedas modificarla antes de reintentarla.
3. La solicitud vuelve a la cola con `dont_filter=True`, para permitir el duplicado, y con menor prioridad, para que no se reintente de inmediato.
4. El proceso se repite hasta `max_blocked_retries` veces. El valor predeterminado es 3.

!!! tip "Consejo"

    1. Antes del reintento, se eliminan los argumentos `proxy`/`proxies` de la solicitud para que el rotador asigne un nuevo proxy.
    2. `max_blocked_retries` es independiente de los reintentos de la sesión. Sus contadores son distintos.

### Personalizar la detección de bloqueos {#custom-block-detection}

Redefine `is_blocked()` para añadir tu propia lógica:

```python
class MySpider(Spider):
    name = "my_spider"
    start_urls = ["https://example.com"]

    async def is_blocked(self, response: Response) -> bool:
        # Check status codes (default behavior)
        if response.status in {403, 429, 503}:
            return True

        # Check response content
        body = response.body.decode("utf-8", errors="ignore")
        if "access denied" in body.lower() or "rate limit" in body.lower():
            return True

        return False

    async def parse(self, response: Response):
        yield {"title": response.css("title::text").get("")}
```

### Personalizar los reintentos {#customizing-retries}

Redefine `retry_blocked_request()` para modificar la solicitud antes de reintentarla. El atributo `max_blocked_retries` indica cuántas veces se reintenta una solicitud bloqueada. Su valor predeterminado es 3:

```python
from scrapling.spiders import Spider, SessionManager, Request, Response
from scrapling.fetchers import FetcherSession, AsyncStealthySession


class MySpider(Spider):
    name = "my_spider"
    start_urls = ["https://example.com"]
    max_blocked_retries = 5

    def configure_sessions(self, manager: SessionManager) -> None:
        manager.add('requests', FetcherSession(impersonate=['chrome', 'firefox', 'safari']))
        manager.add('stealth', AsyncStealthySession(block_webrtc=True), lazy=True)

    async def retry_blocked_request(self, request: Request, response: Response) -> Request:
        request.sid = "stealth"
        self.logger.info(f"Retrying blocked request: {request.url}")
        return request

    async def parse(self, response: Response):
        yield {"title": response.css("title::text").get("")}
```

En este ejemplo se mantiene la detección de bloqueos predeterminada. El spider usa solicitudes HTTP hasta que recibe un bloqueo y, en ese momento, cambia al navegador con protección contra detección.

Ahora podemos combinarlo todo:

```python
from scrapling.spiders import Spider, SessionManager, Request, Response
from scrapling.fetchers import FetcherSession, AsyncStealthySession, ProxyRotator


cheap_proxies = ProxyRotator([ "http://proxy1:8080", "http://proxy2:8080"])

# A format acceptable by the browser
expensive_proxies = ProxyRotator([
    {"server": "http://residential_proxy1:8080", "username": "user", "password": "pass"},
    {"server": "http://residential_proxy2:8080", "username": "user", "password": "pass"},
    {"server": "http://mobile_proxy1:8080", "username": "user", "password": "pass"},
    {"server": "http://mobile_proxy2:8080", "username": "user", "password": "pass"},
])


class MySpider(Spider):
    name = "my_spider"
    start_urls = ["https://example.com"]
    max_blocked_retries = 5

    def configure_sessions(self, manager: SessionManager) -> None:
        manager.add('requests', FetcherSession(impersonate=['chrome', 'firefox', 'safari'], proxy_rotator=cheap_proxies))
        manager.add('stealth', AsyncStealthySession(block_webrtc=True, proxy_rotator=expensive_proxies), lazy=True)

    async def retry_blocked_request(self, request: Request, response: Response) -> Request:
        request.sid = "stealth"
        self.logger.info(f"Retrying blocked request: {request.url}")
        return request

    async def parse(self, response: Response):
        yield {"title": response.css("title::text").get("")}
```

La lógica es la siguiente: las solicitudes usan proxies baratos, como los de centros de datos, hasta que reciben un bloqueo. Entonces se reintentan con proxies de mayor calidad, como los residenciales o móviles.
