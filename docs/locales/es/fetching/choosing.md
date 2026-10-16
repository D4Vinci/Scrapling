---
title: "Elige solicitudes HTTP o un navegador para web scraping"
description: "Elige Fetcher o StealthyFetcher según tu tarea. Aprende cuándo usar HTTP directo, ejecutar JavaScript y reutilizar sesiones."
---

# Conceptos básicos de las herramientas de descarga {#fetchers-basics}

## Introducción {#introduction}
Los fetchers son clases que envían solicitudes o descargan páginas con una sola línea de código y devuelven un objeto [Response](#response-object). Desde v0.3, tienen clases de sesión que mantienen la conexión abierta. Por ejemplo, una sesión de navegador deja el navegador abierto hasta que terminas todas las solicitudes, en vez de abrir varios. Elige según lo que necesites.

Estas funciones se añadieron porque, antes de v0.2, Scrapling solo analizaba páginas. El objetivo es cubrir poco a poco todas las necesidades de web scraping.

> Los fetchers no son simples envoltorios de otras bibliotecas. Las usan como motores para enviar solicitudes y descargar páginas, y añaden funciones que esos motores no ofrecen. También aprovechan sus capacidades y las ajustan para web scraping.

## Comparación de herramientas de descarga {#fetchers-overview}

Scrapling ofrece herramientas HTTP (`Fetcher` y `AsyncFetcher`) y una herramienta de navegador (`StealthyFetcher`), con clases de sesión para enviar varias solicitudes.

Esta tabla te ayuda a compararlas y elegir:


| Característica | Fetcher | StealthyFetcher |
|--------------------|---------------------------------------------------|--------------------------------------------------------------------------------------------|
| Velocidad relativa | 🐇🐇🐇🐇🐇 | 🐇🐇🐇 |
| Ocultación de la automatización | ⭐⭐ | ⭐⭐⭐⭐⭐ |
| Opciones contra la detección de bots | ⭐⭐ | ⭐⭐⭐⭐⭐ |
| Ejecución de JavaScript | ❌ | ✅ |
| Uso de memoria | ⭐ | ⭐⭐⭐ |
| Uso recomendado | Extracción sencilla cuando bastan las solicitudes HTTP | - Sitios con carga dinámica <br/>- Automatizaciones pequeñas <br/>- Protecciones simples o complejas |
| Navegadores | ❌ | Chromium y Google Chrome |
| API de navegador usada | ❌ | Playwright |
| Dificultad de configuración | Sencilla | Sencilla |

Veremos cada herramienta con detalle en las siguientes páginas.

## Configurar el analizador en todas las herramientas {#parser-configuration-in-all-fetchers}
Todas se importan de la misma forma:
```python
from scrapling.fetchers import Fetcher, AsyncFetcher, StealthyFetcher
```
Después puedes usarlas directamente, sin crear un objeto. Se aplican los ajustes por defecto del analizador:
```python
page = StealthyFetcher.fetch('https://example.com') 
```
Si quieres configurar el analizador, es decir, la [clase Selector](../parsing/main_classes.md#selector), que procesará la respuesta antes de devolverla, haz esto primero:
```python
from scrapling.fetchers import Fetcher
Fetcher.configure(adaptive=True, keep_comments=False)  # and the rest
```
O bien:
```python
from scrapling.fetchers import Fetcher
Fetcher.adaptive=True
Fetcher.keep_comments=False
```
Después continúa con tu código.

Los argumentos disponibles son `adaptive`, `adaptive_domain`, `huge_tree`, `keep_comments`, `storage` y `storage_args`. Son los mismos que recibe [Selector](../parsing/main_classes.md#selector). Puedes ver la configuración actual con `<fetcher_class>.display_config()`.

!!! info "Información"

    `adaptive` está desactivado por defecto. Debes activarlo para usar esa función.

### Configurar el analizador para cada solicitud {#set-parser-config-per-request}
Los ajustes anteriores se aplican a todas las solicitudes enviadas con esa clase. Esto simplifica el uso.

Si necesitas ajustes distintos para cada solicitud, pasa un diccionario al argumento `selector_config` del método que uses (`fetch`/`get`/`post`/...).

## Objeto Response {#response-object}
`Response` funciona como [Selector](../parsing/main_classes.md#selector), pero añade datos de la respuesta, como las cabeceras, el estado y las cookies:
```python
from scrapling.fetchers import Fetcher
page = Fetcher.get('https://example.com')

page.status          # HTTP status code
page.reason          # Status message
page.cookies         # Response cookies as a dictionary
page.headers         # Response headers
page.request_headers # Request headers
page.history         # Response history of redirections, if any
page.body            # Raw response body as bytes
page.encoding        # Response encoding
page.meta            # Response metadata dictionary (e.g., proxy used). Mainly helpful with the spiders system.
```
Todas las herramientas de descarga devuelven `Response`. Las sesiones de navegador con `record_requests=True` también devuelven objetos `Response` guardados mediante `session.network.search(limit=None)` y `session.network.get(request_id)`. Consulta el [historial de red](stealthy.md#network-history) para ver cómo usar las respuestas de API guardadas y migrar a v5.

`Response` también puede convertir la página a Markdown limpio y listo para modelos de lenguaje con una línea:
```python
markdown = Fetcher.get('https://example.com').markdown(main_content_only=True)
```
Antes de convertir, siempre elimina scripts, estilos, contenido oculto e intentos de inyección de instrucciones. Puedes pasar `css_selector` para convertir solo ciertos elementos. Requiere el extra `rag`, que también está incluido en `ai`/`shell`/`all`. La página [Crear sistemas RAG](../ai/building-rag-systems.md) lo explica con detalle.

!!! note "Nota"

    A diferencia de [Selector](../parsing/main_classes.md#selector), el contenido de body en `Response` siempre es bytes desde v0.4.
