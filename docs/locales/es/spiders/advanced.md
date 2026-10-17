---
title: "Control del rastreo: AutoThrottle, puntos de guardado, caché y streaming"
description: "Controla la velocidad y la concurrencia del rastreo. Aprende a usar la caché, pausar y reanudar, recibir elementos en tiempo real y guardar el estado."
---

# Usos avanzados {#advanced-usages}

## Introducción {#introduction}

!!! success "Antes de empezar"

    1. Lee la página [Primeros pasos](getting-started.md) para aprender a crear y ejecutar un spider básico.

Esta página explica las funciones avanzadas de los spiders: control de concurrencia, pausa y reanudación, streaming, hooks del ciclo de vida, estadísticas y registros.

## Control de concurrencia {#concurrency-control}

El sistema de spiders usa estos atributos de clase para controlar el ritmo del rastreo:

| Atributo | Valor predeterminado | Descripción |
|----------|----------------------|-------------|
| `concurrent_requests` | `4` | Número máximo de solicitudes que se procesan al mismo tiempo |
| `concurrent_requests_per_domain` | `0` | Número máximo de solicitudes simultáneas por dominio. 0 significa que no hay límite por dominio |
| `download_delay` | `0.0` | Segundos de espera antes de cada solicitud |
| `robots_txt_obey` | `False` | Respeta las reglas de robots.txt: Disallow, Crawl-delay y Request-rate |

```python
class PoliteSpider(Spider):
    name = "polite"
    start_urls = ["https://example.com"]

    # Be gentle with the server
    concurrent_requests = 4
    concurrent_requests_per_domain = 2
    download_delay = 1.0  # Wait 1 second between requests

    async def parse(self, response: Response):
        yield {"title": response.css("title::text").get("")}
```

Si defines `concurrent_requests_per_domain`, cada dominio tiene su propio límite de concurrencia, además del límite global. Esto es útil al rastrear varios dominios a la vez: puedes permitir muchas solicitudes en total sin sobrecargar cada dominio.

!!! tip "Consejo"

    `download_delay` añade una espera fija antes de cada solicitud, sin importar el dominio. Úsalo para limitar el ritmo de forma sencilla.

## AutoThrottle {#autothrottle}

Elegir un `download_delay` fijo requiere probar: si es muy bajo, te pueden bloquear; si es muy alto, el rastreo tarda demasiado. AutoThrottle observa cuánto tarda el sitio en responder y ajusta la espera de cada dominio. Así acelera con los servidores rápidos y reduce el ritmo con los lentos o los que bloquean solicitudes.

| Atributo | Valor predeterminado | Descripción |
|----------|----------------------|-------------|
| `autothrottle_enabled` | `False` | Activa el ajuste automático de la espera |
| `autothrottle_start_delay` | `5.0` | Espera que se usa para la primera solicitud a un dominio |
| `autothrottle_max_delay` | `60.0` | Espera máxima permitida |
| `autothrottle_target_concurrency` | `None` | Número de solicitudes simultáneas que se intenta mantener por dominio, como se explica abajo |
| `autothrottle_block_backoff` | `True` | Duplica la espera de un dominio cada vez que bloquea una solicitud |

```python
class AdaptiveSpider(Spider):
    name = "adaptive"
    start_urls = ["https://example.com"]

    concurrent_requests = 8
    concurrent_requests_per_domain = 1

    autothrottle_enabled = True
    autothrottle_start_delay = 2.0
    autothrottle_max_delay = 30.0

    async def parse(self, response: Response):
        yield {"title": response.css("title::text").get("")}
```

Después de cada respuesta, la espera se acerca al tiempo que tardó el servidor en responder. Por ejemplo, si responde en 0,5 segundos, la espera se estabiliza cerca de 0,5 segundos, lo que mantiene aproximadamente una solicitud activa. El número de solicitudes que se intenta mantener por dominio se elige en este orden: `autothrottle_target_concurrency` si lo defines; si no, `concurrent_requests_per_domain`; y, por último, 1. Normalmente no necesitas definir un objetivo aparte: se usa el límite por dominio que ya configuraste y se divide la espera entre ese valor. Los aumentos bruscos del tiempo de respuesta se aplican de inmediato, sin promediarlos. Así, el spider reduce el ritmo en cuanto el servidor empieza a tener problemas y solo vuelve a acelerarlo de forma gradual.

### Reducir el ritmo ante bloqueos {#backing-off-when-blocked}

El tiempo de respuesta por sí solo no detecta los límites de solicitudes. Una respuesta `429`, `403` o una página con captcha suele llegar *más rápido* que el contenido real. Si solo se midiera ese tiempo, el spider aceleraría. Por eso, una respuesta con un código fuera de 2xx o que `is_blocked()` marque como bloqueada **duplica** la espera del dominio:

```
0.5s -> 1s -> 2s -> 4s -> 8s ...   (up to autothrottle_max_delay)
```

El spider sigue reduciendo el ritmo mientras el sitio rechace las solicitudes. Cuando vuelven las respuestas correctas, el ajuste normal reduce la espera poco a poco hasta acercarla a la velocidad real del servidor. No necesitas reiniciar nada.

Si una respuesta `429` o `503` incluye una cabecera `Retry-After`, se usa esa espera en lugar de duplicarla. Se admite tanto el formato numérico (`Retry-After: 120`) como el formato de fecha HTTP.

Configura `autothrottle_block_backoff = False` para desactivar este comportamiento y ajustar el ritmo solo según el tiempo de respuesta. En ese caso, un bloqueo solo impide que el spider acelere.

Puedes consultar la espera final de cada dominio en las estadísticas:

```python
result = AdaptiveSpider().start()
print(result.stats.autothrottle_delays)  # {'example.com': 0.62}
```

!!! note "Notas"

    * `download_delay` y las esperas de robots.txt fijan un mínimo, pero `autothrottle_max_delay` también limita ese mínimo. Usa un máximo que sea al menos igual a la espera configurada o exigida por robots.txt.<br/>
    * `concurrent_requests_per_domain` cumple dos funciones: limita las solicitudes activas de un dominio y sirve como objetivo de AutoThrottle. Por eso, normalmente no hace falta configurar otro objetivo. Conviene definirlo porque, mientras una solicitud espera, ocupa una plaza del límite global. Sin un límite por dominio, esas esperas pueden ocupar las plazas que necesitan los demás dominios.<br/>
    * El tiempo medido incluye toda la descarga, con sus reintentos internos y, en las sesiones de navegador, el tiempo de renderizado de la página.<br/>
    * `autothrottle_max_delay` limita todas las esperas, incluida `Retry-After`. Si un sitio pide esperar más, aumenta `autothrottle_max_delay` para respetarlo.<br/>
    * Las esperas aprendidas no se incluyen en los puntos de guardado. Al pausar y reanudar, cada dominio vuelve a empezar con `autothrottle_start_delay`.

## Usar uvloop {#using-uvloop}

El método `start()` acepta `use_uvloop` para usar el bucle de eventos más rápido de [uvloop](https://github.com/MagicStack/uvloop)/[winloop](https://github.com/nicktimko/winloop), si está disponible:

```python
result = MySpider().start(use_uvloop=True)
```

Esto puede mejorar el rendimiento en rastreos con muchas operaciones de entrada y salida. Debes instalar `uvloop` en Linux/macOS o `winloop` en Windows por separado.

## Pausar y reanudar {#pause-resume}

El spider permite pausar y reanudar el rastreo con puntos de guardado. Para activarlos, pasa un directorio `crawldir` al constructor:

```python
spider = MySpider(crawldir="crawl_data/my_spider")
result = spider.start()

if result.paused:
    print("Crawl was paused. Run again to resume.")
else:
    print("Crawl completed!")
```

### Cómo funciona {#how-it-works}

1. **Pausar**: pulsa `Ctrl+C` durante el rastreo. El spider espera a que terminen las solicitudes activas, guarda las pendientes y el conjunto de huellas de solicitudes ya vistas, y luego se cierra.
2. **Forzar el cierre**: pulsa `Ctrl+C` por segunda vez para detenerlo de inmediato, sin esperar a las tareas activas.
3. **Reanudar**: ejecuta otra vez el spider con el mismo `crawldir`. Detecta el punto de guardado, restaura la cola y las huellas ya vistas, y continúa donde se detuvo, sin ejecutar `start_requests()`.
4. **Limpiar**: cuando el rastreo termina por completo, sin quedar en pausa, los archivos de guardado se eliminan de forma automática.

**También se crean puntos de guardado durante el rastreo, cada 5 minutos de forma predeterminada.**

Puedes cambiar el intervalo así:

```python
# Save checkpoint every 2 minutes
spider = MySpider(crawldir="crawl_data/my_spider", interval=120.0)
```

Para escribir un punto de guardado, se usa un archivo temporal. El punto anterior solo se reemplaza cuando la escritura termina correctamente.

!!! warning "Datos del punto de guardado"

    Al activar `crawldir`, los valores de las solicitudes pendientes, incluidos `meta` y los argumentos de las solicitudes, deben poder guardarse con el módulo `pickle` de Python. Si un valor no se puede guardar, falla la creación del punto de guardado y el rastreo se detiene. Un `Selector` puede funcionar en un callback, pero no se puede guardar de esta forma.

    Guarda los valores extraídos, como cadenas de texto o números, en lugar de objetos `Selector`. Las listas y los diccionarios también deben contener solo valores que se puedan guardar:

    ```python
    yield response.follow("/details", meta={"title": str(response.css("h1::text").get(""))})
    ```

!!! tip "Consejo"

    Con `start()`, pulsar `Ctrl+C` cierra el spider de forma ordenada aunque no hayas activado los puntos de guardado. Si lo pulsas de nuevo sin esperar, fuerzas el cierre inmediato.

### Saber si estás reanudando un rastreo {#knowing-if-youre-resuming}

El hook `on_start()` recibe el indicador `resuming`:

```python
async def on_start(self, resuming: bool = False):
    if resuming:
        self.logger.info("Resuming from checkpoint!")
    else:
        self.logger.info("Starting fresh crawl")
```

## Modo de desarrollo {#development-mode}

Al ajustar la lógica de `parse()`, volver a descargar las páginas en cada ejecución consume tiempo y genera solicitudes innecesarias. El modo de desarrollo guarda las respuestas en disco durante la primera ejecución y las reutiliza después. Así puedes cambiar los selectores y ejecutar el spider tantas veces como necesites sin volver a descargar esas páginas.

Actívalo con `development_mode = True` en tu spider:

```python
class MySpider(Spider):
    name = "my_spider"
    start_urls = ["https://example.com"]
    development_mode = True

    async def parse(self, response: Response):
        yield {"title": response.css("title::text").get("")}
```

La primera ejecución descarga las páginas y guarda cada respuesta en disco. En las siguientes, las mismas solicitudes se resuelven desde la caché. Si usas `robots_txt_obey=True`, las reglas de robots.txt se comprueban antes de consultar la caché.

### Ubicación de la caché {#cache-location}

De forma predeterminada, las respuestas se guardan en `.scrapling_cache/{spider.name}/`, dentro del directorio de trabajo actual. Es el directorio desde el que ejecutaste el spider, **no** el que contiene su archivo. Puedes cambiarlo con `development_cache_dir`:

```python
class MySpider(Spider):
    name = "my_spider"
    start_urls = ["https://example.com"]
    development_mode = True
    development_cache_dir = "/tmp/my_spider_cache"
```

### Cómo funciona {#how-it-works_1}

1. **Clave de caché**: cada respuesta se identifica por la huella de la solicitud. Cambiar los atributos que afectan a esa huella (`fp_include_kwargs`, `fp_include_headers`, `fp_keep_fragments`) hará que se descargue de nuevo.
2. **Formato**: se guarda un archivo JSON por respuesta, con el nombre `{fingerprint_hex}.json`. El cuerpo se codifica en base64 para conservar exactamente los datos binarios. La escritura es atómica: se crea un archivo temporal y luego se renombra.
3. **Reutilización**: si hay una respuesta en caché, el motor omite la descarga, `download_delay`, los límites de ritmo y los reintentos de `is_blocked()`. La respuesta guardada pasa directamente al callback.
4. **Estadísticas**: las solicitudes resueltas desde la caché se incluyen en `requests_count`, `response_bytes` y los contadores por código de estado, igual que en un rastreo normal. Los contadores `cache_hits` y `cache_misses` muestran cuántas solicitudes encontraron una respuesta guardada y cuántas no.

### Vaciar la caché {#clearing-the-cache}

La caché no caduca de forma automática. Para descargar todo de nuevo, elimina su directorio o llama directamente al método `clear()` del gestor.

!!! warning "Aviso"

    Este modo está pensado para desarrollo, no para producción. Las respuestas guardadas nunca caducan y, al reutilizarlas, no se aplican los límites de ritmo ni los reintentos de solicitudes bloqueadas. No publiques un spider con `development_mode = True`.

## Streaming {#streaming}

Para spiders que tardan mucho o aplicaciones que necesitan recibir los datos en tiempo real, usa `stream()` en lugar de `start()`:

```python
import anyio

async def main():
    spider = MySpider()
    async for item in spider.stream():
        print(f"Got item: {item}")
        # Access real-time stats
        print(f"Items so far: {spider.stats.items_scraped}")
        print(f"Requests made: {spider.stats.requests_count}")

anyio.run(main)
```

Diferencias principales con `start()`:

- Debes llamar a `stream()` desde un contexto asíncrono.
- Los elementos se entregan uno a uno al extraerlos, en lugar de reunirse en una lista.
- Puedes consultar `spider.stats` durante la iteración para ver estadísticas en tiempo real.

!!! abstract "Más información"

    La sección [Resultados y estadísticas](#results-statistics) explica todas las estadísticas disponibles en `spider.stats`.

También puedes combinarlo con los puntos de guardado. Así puedes crear interfaces que muestren datos en tiempo real y permitan pausar y reanudar el rastreo.

```python
import anyio

async def main():
    spider = MySpider(crawldir="crawl_data/my_spider")
    async for item in spider.stream():
        print(f"Got item: {item}")
        # Access real-time stats
        print(f"Items so far: {spider.stats.items_scraped}")
        print(f"Requests made: {spider.stats.requests_count}")

anyio.run(main)
```

También puedes usar `spider.pause()` para detener el spider del ejemplo anterior. Si no has activado los puntos de guardado, solo se cerrará el rastreo.

## Hooks del ciclo de vida {#lifecycle-hooks}

El spider ofrece varios hooks, métodos que puedes redefinir para añadir tu propia lógica en distintas etapas del rastreo:

### on_start {#on_start}

Se llama antes de empezar. Úsalo para preparar el trabajo, como cargar datos o iniciar recursos:

```python
async def on_start(self, resuming: bool = False):
    self.logger.info("Spider starting up")
    # Load seed URLs from a database, initialize counters, etc.
```

### on_close {#on_close}

Se llama cuando termina el rastreo, tanto si se completó como si se pausó. Úsalo para liberar recursos:

```python
async def on_close(self):
    self.logger.info("Spider shutting down")
    # Close database connections, flush buffers, etc.
```

### on_error {#on_error}

Se llama cuando una solicitud falla con una excepción. Úsalo para registrar el error o aplicar tu propia lógica de recuperación:

```python
async def on_error(self, request: Request, error: Exception):
    self.logger.error(f"Failed: {request.url} - {error}")
    # Log to error tracker, save failed URL for later, etc.
```

### on_scraped_item {#on_scraped_item}

Se llama para cada elemento extraído antes de añadirlo a los resultados. Devuelve el elemento, con o sin cambios, para conservarlo. Devuelve `None` para descartarlo:

```python
async def on_scraped_item(self, item: dict) -> dict | None:
    # Drop items without a title
    if not item.get("title"):
        return None

    # Modify items (e.g., add timestamps)
    item["scraped_at"] = "2026-01-01"
    return item
```

!!! tip "Consejo"

    También puedes usar este hook para enviar los elementos a tu propio proceso de datos y excluirlos de los resultados del spider.

### start_requests {#start_requests}

Redefine `start_requests()` para generar tus propias solicitudes iniciales en lugar de usar `start_urls`:

```python
async def start_requests(self):
    # POST request to log in first
    yield Request(
        "https://example.com/login",
        method="POST",
        data={"user": "admin", "pass": "secret"},
        callback=self.after_login,
    )

async def after_login(self, response: Response):
    # Now crawl the authenticated pages
    yield response.follow("/dashboard", callback=self.parse)
```

## Resultados y estadísticas {#results-statistics}

El `CrawlResult` que devuelve `start()` contiene los elementos extraídos y estadísticas detalladas:

```python
result = MySpider().start()

# Items
print(f"Total items: {len(result.items)}")
result.items.to_json("output.json", indent=True)

# Did the crawl complete?
print(f"Completed: {result.completed}")
print(f"Paused: {result.paused}")

# Statistics
stats = result.stats
print(f"Requests: {stats.requests_count}")
print(f"Failed: {stats.failed_requests_count}")
print(f"Blocked: {stats.blocked_requests_count}")
print(f"Offsite filtered: {stats.offsite_requests_count}")
print(f"Robots.txt disallowed: {stats.robots_disallowed_count}")
print(f"Cache hits: {stats.cache_hits}")
print(f"Cache misses: {stats.cache_misses}")
print(f"Items scraped: {stats.items_scraped}")
print(f"Items dropped: {stats.items_dropped}")
print(f"Response bytes: {stats.response_bytes}")
print(f"Duration: {stats.elapsed_seconds:.1f}s")
print(f"Speed: {stats.requests_per_second:.1f} req/s")
```

### Estadísticas detalladas {#detailed-stats}

El objeto `CrawlStats` registra información detallada:

```python
stats = result.stats

# Status code distribution
print(stats.response_status_count)
# {'status_200': 150, 'status_404': 3, 'status_403': 1}

# Bytes downloaded per domain
print(stats.domains_response_bytes)
# {'example.com': 1234567, 'api.example.com': 45678}

# Requests per session
print(stats.sessions_requests_count)
# {'http': 120, 'stealth': 34}

# Proxies used during the crawl
print(stats.proxies)
# ['http://proxy1:8080', 'http://proxy2:8080']

# Log level counts
print(stats.log_levels_counter)
# {'debug': 200, 'info': 50, 'warning': 3, 'error': 1, 'critical': 0}

# Timing information
print(stats.start_time)       # Unix timestamp when crawl started
print(stats.end_time)         # Unix timestamp when crawl finished
print(stats.download_delay)   # The download delay used (seconds)

# Concurrency settings used
print(stats.concurrent_requests)             # Global concurrency limit
print(stats.concurrent_requests_per_domain)  # Per-domain concurrency limit

# AutoThrottle
print(stats.autothrottle_enabled)  # Whether the adaptive delay was on
print(stats.autothrottle_delays)   # Final delay per domain, {'example.com': 0.62}

# Custom stats (set by your spider code)
print(stats.custom_stats)
# {'login_attempts': 3, 'pages_with_errors': 5}

# Export everything as a dict
print(stats.to_dict())
```

## Registros {#logging}

El spider tiene un logger integrado, disponible en `self.logger`. Ya está configurado con el nombre del spider y permite estos ajustes:

| Atributo | Valor predeterminado | Descripción |
|----------|----------------------|-------------|
| `logging_level` | `logging.DEBUG` | Nivel mínimo que se registra |
| `logging_format` | `"[%(asctime)s]:({spider_name}) %(levelname)s: %(message)s"` | Formato de los mensajes |
| `logging_date_format` | `"%Y-%m-%d %H:%M:%S"` | Formato de la fecha en los mensajes |
| `log_file` | `None` | Ruta de un archivo de registro, además de la salida en consola |

```python
import logging

class MySpider(Spider):
    name = "my_spider"
    start_urls = ["https://example.com"]
    logging_level = logging.INFO
    log_file = "logs/my_spider.log"

    async def parse(self, response: Response):
        self.logger.info(f"Processing {response.url}")
        yield {"title": response.css("title::text").get("")}
```

Si el directorio del archivo de registro no existe, se crea de forma automática. La consola y el archivo usan el mismo formato.
