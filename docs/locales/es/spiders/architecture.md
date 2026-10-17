---
title: "Cómo funcionan los rastreadores web de Scrapling"
description: "Conoce la relación entre spiders, solicitudes, sesiones, colas y el motor de rastreo. Compara el flujo con Scrapy y elige por dónde empezar."
---

# Arquitectura de los spiders {#spiders-architecture}

!!! success "Antes de empezar"

    1. Lee la página [Conceptos básicos de los fetchers](../fetching/choosing.md) para conocer los distintos tipos de fetcher y cuándo usar cada uno.
    2. Lee la página [Clases principales](../parsing/main_classes.md) para conocer las clases [Selector](../parsing/main_classes.md#selector) y [Response](../fetching/choosing.md#response-object).

El sistema de spiders de Scrapling está inspirado en Scrapy. Permite rastrear de forma asíncrona, con varias solicitudes y sesiones a la vez, y pausar y reanudar el trabajo. Une el motor de análisis y los fetchers de Scrapling en una sola API de rastreo, con una cola de solicitudes, control de concurrencia y puntos de guardado.

Si conoces Scrapy, te resultará familiar. Si no, no te preocupes: el sistema está pensado para ser fácil de usar.

## Flujo de datos {#data-flow}

Este diagrama muestra cómo pasan los datos por el sistema durante un rastreo:

<img src="../assets/spider_architecture.png" title="Diagrama de la arquitectura de spiders por @TrueSkills" alt="Diagrama de la arquitectura de spiders por @TrueSkills" style="width: 70%;"/>

Estos son los pasos principales al ejecutar un spider:

1. El **Spider** genera el primer grupo de objetos `Request`. De forma predeterminada, crea una solicitud por cada URL de `start_urls`. Puedes redefinir `start_requests()` para cambiar esta lógica.
2. El **Scheduler** recibe las solicitudes, calcula sus huellas y las coloca en una cola de prioridad. Las de mayor prioridad salen primero.
3. El **motor de rastreo** pide al **Scheduler** la siguiente solicitud y respeta los límites de concurrencia, tanto globales como por dominio, y las esperas entre descargas. Si `robots_txt_obey` está activo, comprueba las reglas de robots.txt del dominio y descarta las solicitudes no permitidas sin mostrar mensajes. Luego envía la solicitud al **gestor de sesiones**, que elige la sesión según el campo `sid` (ID de sesión).
4. La **sesión** obtiene la página y devuelve un objeto [Response](../fetching/choosing.md#response-object) al **motor de rastreo**. El motor registra estadísticas y comprueba si la respuesta indica un bloqueo. Si lo detecta, reintenta la solicitud hasta `max_blocked_retries` veces. Puedes personalizar tanto la detección como la lógica de reintentos.
5. El **motor de rastreo** pasa el objeto [Response](../fetching/choosing.md#response-object) al callback de la solicitud. El callback puede entregar un diccionario, que se guarda como un elemento extraído, o una nueva solicitud, que se envía al Scheduler para añadirla a la cola.
6. El ciclo vuelve al paso 2 hasta que la cola queda vacía y no hay tareas activas, o hasta que se pausa el spider.
7. Si defines `crawldir` al iniciar el spider, el **motor de rastreo** guarda periódicamente un punto de guardado en disco con las solicitudes pendientes y las URL ya vistas. Al cerrar de forma ordenada con Ctrl+C, guarda un último punto. Si vuelves a ejecutar el spider con el mismo `crawldir`, restaura la cola y continúa donde se detuvo, sin ejecutar `start_requests()`.

## Componentes {#components}

### Spider {#spider}

Es la clase principal con la que trabajas. Crea una subclase de `Spider` y define `start_urls` y el método `parse()`. También puedes configurar sesiones y redefinir hooks para las distintas etapas del rastreo.

```python
from scrapling.spiders import Spider, Response, Request

class MySpider(Spider):
    name = "my_spider"
    start_urls = ["https://example.com"]

    async def parse(self, response: Response):
        for link in response.css("a::attr(href)").getall():
            yield response.follow(link, callback=self.parse_page)

    async def parse_page(self, response: Response):
        yield {"title": response.css("h1::text").get("")}
```

### Motor de rastreo {#crawler-engine}

El motor coordina todo el rastreo. Gestiona el bucle principal, aplica los límites de concurrencia, envía solicitudes mediante el gestor de sesiones y procesa los resultados de los callbacks. No necesitas usarlo directamente: los métodos `Spider.start()` y `Spider.stream()` se encargan de ello.

### Scheduler {#scheduler}

Es una cola de prioridad que evita repetir URL. Calcula la huella de cada solicitud a partir de su URL, método HTTP, cuerpo e ID de sesión. Los métodos `snapshot()` y `restore()` permiten guardar y restaurar el estado del rastreo mediante el sistema de puntos de guardado.

### Gestor de sesiones {#session-manager}

Gestiona una o varias sesiones identificadas por un nombre. Cada sesión puede ser:

- [FetcherSession](../fetching/static.md)
- [AsyncStealthySession](../fetching/stealthy.md)

Cuando llega una solicitud, el gestor elige la sesión según su campo `sid`. Las sesiones pueden iniciarse junto con el spider, que es el comportamiento predeterminado, o cuando se usan por primera vez.

### Sistema de puntos de guardado {#checkpoint-system}

Este sistema opcional guarda el estado del rastreador en un archivo pickle: las solicitudes pendientes y las huellas de las URL ya vistas. Las escrituras son atómicas, con un archivo temporal que luego se renombra, para evitar daños en los datos. El estado se guarda a intervalos configurables y al cerrar de forma ordenada. Si el rastreo termina por completo, sin quedar en pausa, los archivos se eliminan de forma automática.

### Caché de respuestas {#response-cache}

Al activar el modo de desarrollo, esta caché opcional guarda las respuestas en disco y las reutiliza en ejecuciones posteriores. Cada respuesta se identifica por la huella de la solicitud y se guarda como JSON, con el cuerpo codificado en base64 para conservar el contenido binario. Sirve para ajustar la lógica de `parse()` sin volver a enviar solicitudes a los servidores. No está pensada para producción.

### Resultados {#output}

Los elementos extraídos se guardan en un `ItemList`, una subclase de lista con los métodos de exportación `to_json()`, `to_jsonl()`, `to_csv()` y `to_xml()`. Las estadísticas del rastreo se guardan en una dataclass `CrawlStats`, que contiene información detallada de la ejecución.

## Comparación con Scrapy {#comparison-with-scrapy}

Si ya usas Scrapy, esta tabla muestra las equivalencias con Scrapling:

| Concepto | Scrapy | Scrapling |
|----------|--------|-----------|
| Definición del spider | Subclase de `scrapy.Spider` | Subclase de `scrapling.spiders.Spider` |
| Solicitudes iniciales | `start_requests()` | `async start_requests()` |
| Callbacks | `def parse(self, response)` | `async def parse(self, response)` |
| Seguir enlaces | `response.follow(url)` | `response.follow(url)` |
| Entrega de elementos | `yield dict` o `yield Item` | `yield dict` |
| Cola de solicitudes | Scheduler + Dupefilter | Scheduler con eliminación de duplicados integrada |
| Descarga | Downloader + Middlewares | Gestor de sesiones con soporte para varias sesiones |
| Procesamiento de elementos | Item Pipelines | Hook `on_scraped_item()` |
| Detección de bloqueos | Mediante middlewares personalizados | Hooks integrados `is_blocked()` + `retry_blocked_request()` |
| Concurrencia | Ajuste `CONCURRENT_REQUESTS` | Atributo de clase `concurrent_requests` |
| Filtro de dominios | `allowed_domains` | `allowed_domains` |
| Robots.txt | Ajuste `ROBOTSTXT_OBEY` | Atributo de clase `robots_txt_obey` |
| Pausa y reanudación | Ajuste `JOBDIR` | Argumento `crawldir` del constructor |
| Exportación | Feed exports | `result.items.to_json()` / `to_jsonl()` / `to_csv()` / `to_xml()`, o mediante hooks propios |
| Ejecución | `scrapy crawl spider_name` | `MySpider().start()` |
| Streaming | No disponible | `async for item in spider.stream()` |
| Varias sesiones | No disponible | Varias sesiones de distintos tipos por spider |
