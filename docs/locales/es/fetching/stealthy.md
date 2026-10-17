---
title: "Extrae datos de sitios con JavaScript usando StealthyFetcher"
description: "Carga páginas, espera datos, reutiliza inicios de sesión y lee respuestas de API en segundo plano con las sesiones de navegador de Scrapling. Configura proxies y la resolución de pruebas."
---

# Descarga con navegador mediante StealthyFetcher {#browser-fetching-with-stealthyfetcher}

`StealthyFetcher` carga páginas con JavaScript y automatiza Chromium o Google Chrome con funciones para evitar la detección de bots. Usa la [API de Playwright](https://playwright.dev/python/docs/intro) con ajustes de ocultación.

Para automatizar una página necesitarás conocer un poco la [API Page de Playwright](https://playwright.dev/python/docs/api/class-page), como veremos más adelante.

!!! success "Antes de empezar"

    1. Lee [Conceptos básicos de las herramientas de descarga](../fetching/choosing.md) para saber qué es [Response](../fetching/choosing.md#response-object) y qué herramienta elegir.
    2. Lee [Buscar elementos](../parsing/selection.md) para saber cómo buscar y extraer elementos de [Selector](../parsing/main_classes.md#selector)/[Response](../fetching/choosing.md#response-object).
    3. Lee [Clases principales](../parsing/main_classes.md) para conocer las propiedades y métodos que [Response](../fetching/choosing.md#response-object) hereda de [Selector](../parsing/main_classes.md#selector).

## Uso básico {#basic-usage}
La forma principal de importar esta herramienta es la misma que para las demás:

```python
from scrapling.fetchers import StealthyFetcher
```
Consulta cómo configurar el analizador [aquí](choosing.md#parser-configuration-in-all-fetchers).

Veremos los principales argumentos con ejemplos. Si prefieres una tabla de consulta con todos ellos, [ve a esta sección](#full-list-of-arguments).

!!! abstract "Nota"

    La versión asíncrona de `fetch` se llama `async_fetch`.


Esta herramienta ofrece tres opciones principales de ejecución que puedes combinar según lo que necesites.

Son las siguientes:

### 1. Chromium incluido {#1-bundled-chromium}
```python
StealthyFetcher.fetch('https://example.com')
```
Abre el navegador Chromium incluido, aplica los ajustes de ocultación por defecto y carga la página.

### 2. Google Chrome instalado {#2-real-chrome}
```python
StealthyFetcher.fetch('https://example.com', real_chrome=True)
```
Usa esta opción si tienes Google Chrome instalado. Funciona como la anterior, pero abre tu copia de Google Chrome en lugar de Chromium. Esto hace que las solicitudes parezcan más reales y sean más difíciles de detectar.

Si no tienes Google Chrome, puedes instalarlo para la biblioteca con este comando en la terminal:
```commandline
playwright install chrome
```

### 3. Conexión CDP {#3-cdp-connection}
```python
StealthyFetcher.fetch('https://example.com', cdp_url='ws://localhost:9222')
```
En vez de abrir un navegador local, puedes conectarte a uno remoto mediante [Chrome DevTools Protocol](https://chromedevtools.github.io/devtools-protocol/).

La URL puede ser una dirección WebSocket (`ws://`/`wss://`), como las que ofrecen los proveedores de navegadores, o la dirección HTTP de un navegador, por ejemplo, `http://localhost:9222`.


## ¿Qué hace? {#what-does-it-do}

StealthyFetcher ofrece estas funciones contra la detección de bots:

1. Resuelve automáticamente todos los tipos de Cloudflare Turnstile e Interstitial con `solve_cloudflare=True`.
2. Evita filtraciones del entorno de ejecución CDP y de WebRTC.
3. Aísla la ejecución de JavaScript, elimina muchas huellas de Playwright y evita la detección de algunos comportamientos típicos de bots.
4. Añade ruido al canvas para impedir que se use como huella.
5. Corrige métodos conocidos de detección del modo sin interfaz y ofrece una opción contra la detección por diferencias de zona horaria.
6. Incluye otras opciones para superar protecciones.

## Lista completa de argumentos {#full-list-of-arguments}
Esta herramienta y sus clases de sesión ofrecen muchas opciones. Antes de pasar a los [ejemplos](#examples), esta es la lista completa:


| Argumento | Descripción | Opcional |
|:---------------------:|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|:--------:|
|          url          | URL de destino. |    ❌     |
|       headless        | Usa `True` para ejecutar el navegador sin interfaz visible (**por defecto**) o `False` para mostrarlo. |    ✔️    |
|   disable_resources   | Omite recursos innecesarios para acelerar la carga. Bloquea los tipos `font`, `image`, `media`, `beacon`, `object`, `imageset`, `texttrack`, `websocket`, `csp_report` y `stylesheet`. |    ✔️    |
|        cookies        | Cookies para la próxima solicitud. |    ✔️    |
|       useragent       | Cadena de user agent que se usará. **Si no la indicas, se genera una real para el mismo navegador y versión.** |    ✔️    |
|     network_idle      | Espera hasta que la página pase al menos 500 ms sin conexiones de red. |    ✔️    |
|       load_dom        | Espera al estado `domcontentloaded` para la carga y ejecución de JavaScript. Está activado por defecto. |    ✔️    |
|     pierce_shadow     | Incluye el contenido de Shadow DOM abierto en el HTML de la respuesta. Por defecto es `False`. Puede definirse para la sesión o cambiarse por solicitud. |    ✔️    |
|        timeout        | Tiempo máximo, en milisegundos, para las operaciones y esperas de la página. Por defecto son 30 000 ms, es decir, 30 segundos. |    ✔️    |
|         wait          | Milisegundos de espera al terminar todo, antes de cerrar la página y devolver `Response`. |    ✔️    |
|      page_action      | Función de automatización que recibe `page` y se ejecuta después de navegar. |    ✔️    |
|      page_setup       | Función que recibe `page` y se ejecuta antes de navegar. Úsala para registrar eventos o rutas antes de que cargue la página. |    ✔️    |
|     wait_selector     | Espera a que un selector CSS alcance un estado concreto. |    ✔️    |
|      init_script      | Ruta absoluta de un archivo JavaScript que se ejecuta al crear cada página de la sesión. |    ✔️    |
|  wait_selector_state  | Estado que debe alcanzar el selector pasado a `wait_selector`. _Por defecto es `attached`._ |    ✔️    |
|     google_search     | Establece un referer de Google. Está activado por defecto. |    ✔️    |
|     extra_headers     | Diccionario de cabeceras extra. _Si se combina con `google_search`, el referer de esa opción tiene prioridad._ |    ✔️    |
|         proxy         | Proxy de las solicitudes. Acepta una cadena o un diccionario con las claves 'server', 'username' y 'password'. |    ✔️    |
|      real_chrome      | Actívalo para abrir y usar el Google Chrome instalado en tu equipo. |    ✔️    |
|        locale         | Configuración regional, como `en-GB` o `de-DE`. Afecta a `navigator.language`, la cabecera `Accept-Language` y los formatos de números y fechas. Por defecto usa la del sistema. |    ✔️    |
|      timezone_id      | Zona horaria del navegador. Por defecto usa la del sistema. |    ✔️    |
|        cdp_url        | URL CDP a la que conectarse para controlar un navegador existente en vez de abrir uno. |    ✔️    |
|     user_data_dir     | Carpeta donde se guardan datos del navegador, como cookies y almacenamiento local. Por defecto se crea una temporal. **Solo funciona con sesiones.** |    ✔️    |
|      extra_flags      | Lista de opciones extra que se pasan al iniciar el navegador. |    ✔️    |
|   solve_cloudflare    | Resuelve los distintos tipos de pruebas Turnstile e Interstitial de Cloudflare antes de devolver la respuesta. Por defecto es `False`. |    ✔️    |
|     block_webrtc      | Obliga a WebRTC a respetar los ajustes del proxy para evitar que revele la IP local. |    ✔️    |
|      hide_canvas      | Añade ruido aleatorio al canvas para impedir que se use como huella. |    ✔️    |
|      allow_webgl      | Activado por defecto. Al desactivarlo, se elimina el soporte de WebGL y WebGL 2.0. No se recomienda: muchos WAF comprueban si está disponible. |    ✔️    |
|    additional_args    | Ajustes extra para el contexto de Playwright. Tienen prioridad sobre los de Scrapling. |    ✔️    |
|    selector_config    | Diccionario de ajustes del analizador al crear el objeto `Selector`/`Response` final. |    ✔️    |
|    blocked_domains    | Conjunto de dominios que se bloquean, incluidos sus subdominios. Por ejemplo, `"example.com"` también bloquea `"sub.example.com"`. |    ✔️    |
|       block_ads       | Bloquea solicitudes a unos 3500 dominios de anuncios y rastreo conocidos. Puede combinarse con `blocked_domains`. |    ✔️    |
|    dns_over_https     | Envía las consultas DNS por DNS-over-HTTPS de Cloudflare para evitar filtraciones al usar proxies. |    ✔️    |
|     proxy_rotator     | Objeto `ProxyRotator` para cambiar de proxy automáticamente. No se puede combinar con `proxy`. |    ✔️    |
|        retries        | Número de intentos para las solicitudes fallidas. Por defecto, 3. |    ✔️    |
|      retry_delay      | Segundos de espera entre intentos. Por defecto, 1. |    ✔️    |
|    record_requests    | Conserva solicitudes completadas y respuestas guardadas en `session.network`. Solo para sesiones. Por defecto es `False`. |    ✔️    |
| max_recorded_requests | Número máximo de solicitudes guardadas por sesión. Por defecto, 1000. El contenido guardado también tiene límites de tamaño fijos. |    ✔️    |
|    executable_path    | Ruta absoluta de un ejecutable de navegador propio para usarlo en vez del Chromium incluido. Útil para instalaciones o versiones especiales. |    ✔️    |

En las clases de sesión puedes definir estos argumentos para toda la sesión. También puedes cambiar por solicitud los ajustes que pertenecen a la pestaña: `google_search`, `timeout`, `wait`, `page_action`, `page_setup`, `extra_headers`, `disable_resources`, `wait_selector`, `wait_selector_state`, `network_idle`, `load_dom`, `pierce_shadow`, `solve_cloudflare`, `blocked_domains`, `proxy` y `selector_config`.

!!! note "Notas"

    1. En mis pruebas, `disable_resources` aceleró las solicitudes cerca de un 25% en algunos sitios. También puede reducir el tráfico del proxy. Úsalo con cuidado: algunos sitios podrían no terminar de cargar.
    2. `google_search` está activado por defecto y establece el referer en `https://www.google.com/`. Si también usas `extra_headers`, tiene prioridad sobre el referer que indiques allí.
    3. Si no indicas un user agent y usas el modo sin interfaz, se genera uno real para esa versión del navegador. Si no indicas uno y el navegador es visible, se usa su user agent por defecto, igual que en las versiones actuales de los navegadores normales.
    4. `init_script` se registra en el contexto del navegador y se ejecuta al crear las páginas. El modo de ocultación usa por defecto el entorno aislado de Patchright. Si `page_action` necesita leer variables que el script deja en `window`, usa `page.evaluate(..., isolated_context=False)` dentro de la acción.

## Gestión de sesiones {#session-management}

Para mantener el navegador abierto y enviar varias solicitudes con los mismos ajustes, usa `StealthySession`/`AsyncStealthySession`. Estas clases aceptan todos los argumentos de `fetch`, por lo que puedes configurar toda la sesión.

```python
from scrapling.fetchers import StealthySession


with StealthySession(
    headless=True,
    disable_resources=True,
    real_chrome=True
) as session:

    page1 = session.fetch('https://example1.com')
    page2 = session.fetch('https://example2.com')
    page3 = session.fetch('https://dynamic-site.com')


```

### Uso de sesiones asíncronas {#async-session-usage}

```python
import asyncio
from scrapling.fetchers import AsyncStealthySession

async def scrape_multiple_sites():
    async with AsyncStealthySession(
        network_idle=True,
        timeout=30000,
        max_pages=3
    ) as session:

        pages = await asyncio.gather(
            session.fetch('https://spa-app1.com'),
            session.fetch('https://spa-app2.com'),
            session.fetch('https://dynamic-content.com')
        )
        return pages
```

El argumento `max_pages` fija el número máximo de pestañas que pueden estar abiertas a la vez. La sesión mantiene un **grupo de pestañas reutilizables**. Cada pestaña sigue abierta al terminar su solicitud. En cada nueva solicitud, la biblioteca hace lo siguiente:

1. Reutiliza una pestaña libre si hay alguna. Aplica los ajustes de esa solicitud (`timeout`, `extra_headers`, `disable_resources`, `blocked_domains`, etc.), para que no se conserven ajustes de la anterior.
2. Si no hay ninguna libre, abre otra si todavía no se alcanzó `max_pages`.
3. Si ya se alcanzó el límite, comprueba varias veces por segundo si se libera una pestaña, durante 60 segundos. Después lanza `TimeoutError`. Esto puede ocurrir si el sitio deja de responder.

Las pestañas que dan error se cierran y se reemplazan. También puedes cerrar todas con `session.close_pages()`. La siguiente solicitud abrirá una nueva.

Así puedes descargar varias URL al mismo tiempo en un navegador, ahorrar recursos y trabajar mucho más rápido :)

Como la pestaña sigue abierta, la página anterior continúa allí. El `page_setup` de la próxima solicitud se ejecuta antes de salir de ella. Esto permite encadenar acciones entre solicitudes.

Las versiones de 0.3.2 a 0.4.14 cerraban cada pestaña al terminar porque reutilizarlas dejaba pasar ajustes de una solicitud a otra. Desde 0.4.15, los ajustes se restablecen al reutilizarla y las pestañas permanecen abiertas.

### Guardar y cargar el estado de la sesión {#save-and-load-session-state}

Usa `save_state(path)` para guardar cookies, almacenamiento local e IndexedDB en un archivo JSON. Usa `load_state(path)` para restaurarlo en otra sesión o reemplazar el estado de la sesión actual. Ambos aceptan una cadena o `pathlib.Path` y devuelven `None`. El formato es compatible con los archivos de estado de Playwright.

```python
from scrapling.fetchers import StealthySession

with StealthySession() as session:
    session.fetch('https://example.com')
    session.save_state('state.json')

with StealthySession() as session:
    session.load_state('state.json')
    page = session.fetch('https://example.com')
```

Guarda el estado después de iniciar sesión o terminar las acciones del navegador. Llama a ambos métodos dentro de una sesión iniciada, cuando hayan terminado las solicitudes pendientes. Cargar el archivo reemplaza las cookies, el almacenamiento local e IndexedDB actuales. Descarga o recarga la página para usar el inicio de sesión restaurado: cargar el estado no cambia las páginas abiertas.

Con `AsyncStealthySession`, usa `await`:

```python
from scrapling.fetchers import AsyncStealthySession

async def restore_session():
    async with AsyncStealthySession() as session:
        await session.load_state('state.json')
        page = await session.fetch('https://example.com')
        await session.save_state('state.json')
        return page
```

Estos métodos solo guardan y restauran el contexto compartido del navegador. No afectan a los contextos temporales de proxy por solicitud. Las sesiones con `proxy_rotator` no tienen un contexto compartido, por lo que estos métodos lanzan `RuntimeError`. Un `proxy` fijo para la sesión funciona con normalidad.

El archivo no incluye `sessionStorage`, pestañas abiertas ni ajustes del navegador. Guardarlo reemplaza el archivo anterior y requiere que su carpeta ya exista. Los errores de archivo o JSON se pasan al código que llama al método.

### Ventajas de las sesiones {#session-benefits}

- **Reutilizar el navegador**: las siguientes solicitudes son mucho más rápidas al usar el mismo navegador.
- **Cookies persistentes**: gestión automática de cookies y del estado, como en cualquier navegador.
- **Huella constante**: la misma huella del navegador en todas las solicitudes.
- **Menor uso de memoria**: consume menos recursos que abrir un navegador para cada descarga.


## Ejemplos {#examples}
Los ejemplos ayudan a entenderlo mejor. Veamos algunos.

### Control de recursos {#resource-control}

```python

page = StealthyFetcher.fetch('https://example.com', disable_resources=True)
```

### Shadow DOM {#shadow-dom}

Algunas páginas guardan contenido en raíces de Shadow DOM abiertas. Ese contenido no aparece en el HTML normal de la página. Activa `pierce_shadow` para incluirlo en la respuesta y usa CSS o XPath como siempre:

```python
from scrapling.fetchers import StealthyFetcher

page = StealthyFetcher.fetch('https://example.com', pierce_shadow=True)
titles = page.css('product-card .title::text').getall()
```

Por defecto es `False`. También puedes activarlo para una sesión y desactivarlo en una solicitud concreta:

```python
from scrapling.fetchers import StealthySession

with StealthySession(pierce_shadow=True) as session:
    page = session.fetch('https://example.com')
    plain_page = session.fetch('https://example.com', pierce_shadow=False)
```

Funciona igual con `async_fetch` y las sesiones asíncronas.

Solo se incluyen raíces abiertas. No se recorren raíces cerradas ni documentos dentro de iframes. Usa `wait_selector` si un componente carga después de la página.

Cada raíz abierta se convierte en un contenedor `<shadow-root>` en la respuesta. Los slots conservan sus etiquetas y atributos e incluyen los nodos asignados, o su contenido alternativo si no tienen ninguno. Se omiten los hijos del DOM normal que no estén asignados. La página del navegador no cambia.

```html
<product-card>
  <shadow-root>
    <div class="title">Product name</div>
    <slot name="price"><span class="price">20</span></slot>
  </shadow-root>
</product-card>
```

Los selectores de descendientes atraviesan estos elementos. Los de hijos directos deben incluir los contenedores y slots:

```python
titles = page.css('product-card .title::text').getall()
titles = page.css('product-card > shadow-root > .title::text').getall()
prices = page.css('product-card > shadow-root > slot[name="price"] > .price::text').getall()
```

Los contenedores y slots aparecen en las rutas XPath, `.children`, `response.body` y las exportaciones HTML. La extracción a Markdown o texto devuelve su contenido sin mostrar las etiquetas. Los atributos de ocultación de los slots siguen disponibles para limpiar el contenido.

La copia conserva el orden del contenido, pero no calcula su visibilidad CSS ni su disposición. Los selectores con `<shadow-root>` se aplican a la respuesta de Scrapling, no a la página del navegador. Otros analizadores HTML pueden tratar de otra forma los elementos anidados poco habituales.

### Bloquear dominios {#domain-blocking}

```python

page = StealthyFetcher.fetch('https://example.com', blocked_domains={"ads.example.com", "tracker.net"})
```

### Control de red {#network-control}

```python

page = StealthyFetcher.fetch('https://example.com', network_idle=True)


page = StealthyFetcher.fetch('https://example.com', timeout=30000)


page = StealthyFetcher.fetch('https://example.com', proxy='http://username:password@host:port')
```

### Descargar archivos {#downloading-files}

```python
page = StealthyFetcher.fetch('https://raw.githubusercontent.com/D4Vinci/Scrapling/main/docs/assets/main_cover.png')

with open(file='main_cover.png', mode='wb') as f:
    f.write(page.body)
```

El atributo `body` de `Response` siempre devuelve `bytes`.

### Configuración antes de navegar {#pre-navigation-setup}
Para registrar eventos, rutas o scripts antes de cargar una página, usa `page_setup`. Esta función recibe `page` y se ejecuta antes de llamar a `page.goto()`.

```python
from patchright.sync_api import Page

def capture_websockets(page: Page):
    page.on("websocket", lambda ws: print(f"WebSocket opened: {ws.url}"))

page = StealthyFetcher.fetch('https://example.com', page_setup=capture_websockets)
```
Versión asíncrona:
```python
from patchright.async_api import Page

async def capture_websockets(page: Page):
    page.on("websocket", lambda ws: print(f"WebSocket opened: {ws.url}"))

page = await StealthyFetcher.async_fetch('https://example.com', page_setup=capture_websockets)
```

Puedes combinarlo con `page_action`: `page_setup` se ejecuta antes de navegar y `page_action` después.

### Cloudflare y opciones de ocultación {#cloudflare-and-stealth-options}

```python

page = StealthyFetcher.fetch('https://nopecha.com/demo/cloudflare', solve_cloudflare=True)


page = StealthyFetcher.fetch(
    'https://protected-site.com',
    solve_cloudflare=True,
    block_webrtc=True,
    real_chrome=True,
    hide_canvas=True,
    google_search=True,
    proxy='http://username:password@host:port',  # It can also be a dictionary with only the keys 'server', 'username', and 'password'.
)
```

`solve_cloudflare` activa la detección y resolución automática de todos los tipos de pruebas Turnstile e Interstitial de Cloudflare:

- Pruebas de JavaScript gestionadas.
- Pruebas interactivas, como pulsar casillas de verificación.
- Pruebas invisibles, con verificación automática en segundo plano.

También resuelve páginas personalizadas con CAPTCHA integrado.

!!! notes "**Notas importantes**"

    1. En sitios con implementaciones propias, puede que necesites `wait_selector` para esperar al contenido real después del CAPTCHA. Algunos sitios son casos muy particulares, aunque intentamos que la solución funcione de forma general.
    2. Usa un timeout de al menos 60 segundos para dar tiempo a resolver las pruebas de Cloudflare.
    3. Esta función funciona con proxies y con las demás opciones de ocultación.

### Automatización del navegador {#browser-automation}
Aquí necesitas conocer la [API Page de Playwright](https://playwright.dev/python/docs/api/class-page). La función que pases recibe el objeto de página de Playwright, realiza las acciones y luego permite que la descarga continúe.

Se ejecuta justo después de esperar a `network_idle`, si está activado, y antes de esperar a `wait_selector`. Puedes usarla para automatizar acciones o modificar la página.

Este ejemplo usa los [eventos del ratón](https://playwright.dev/python/docs/api/class-mouse) para desplazar la página con la rueda y después mover el ratón.
```python
from patchright.sync_api import Page

def scroll_page(page: Page):
    page.mouse.wheel(10, 0)
    page.mouse.move(100, 400)
    page.mouse.up()

page = StealthyFetcher.fetch('https://example.com', page_action=scroll_page)
```
Si usas la descarga asíncrona, la función también debe ser asíncrona.
```python
from patchright.async_api import Page

async def scroll_page(page: Page):
   await page.mouse.wheel(10, 0)
   await page.mouse.move(100, 400)
   await page.mouse.up()

page = await StealthyFetcher.async_fetch('https://example.com', page_action=scroll_page)
```

### Condiciones de espera {#wait-conditions}

```python

page = StealthyFetcher.fetch(
    'https://quotes.toscrape.com/js-delayed/',
    wait_selector='.quote',
    wait_selector_state='visible'
)
```
Si está activada, esta es la última condición de espera antes de devolver la respuesta. Pasa un selector CSS a `wait_selector` y un estado a `wait_selector_state`. Por defecto espera al estado `attached`, que significa que el elemento está presente en el DOM.

Después, si `load_dom` está activado, como ocurre por defecto, vuelve a esperar al estado `domcontentloaded` para comprobar la carga y ejecución de JavaScript. Si activaste `network_idle`, también vuelve a esperar a que se cumpla `network_idle`.

Los estados disponibles son estos ([fuente](https://playwright.dev/python/docs/api/class-page#page-wait-for-selector)):

- `attached`: espera a que el elemento esté presente en el DOM.
- `detached`: espera a que el elemento no esté en el DOM.
- `visible`: espera a que el elemento tenga un área con tamaño mayor que cero y no use `visibility:hidden`. Un elemento sin contenido o con `display:none` tiene un área vacía y no se considera visible.
- `hidden`: espera a que el elemento salga del DOM, tenga un área vacía o use `visibility:hidden`. Es lo opuesto a `'visible'`.

### Historial de red {#network-history}

Activa `record_requests` en una sesión de navegador para revisar solicitudes completadas entre cargas de páginas, acciones y pestañas. El historial cubre los contextos de la sesión, incluidos los temporales de proxy, y guarda las respuestas como objetos `Response` de Scrapling. Puedes buscar llamadas a API, errores HTTP y redirecciones sin volver a enviar solicitudes, y leer sus cabeceras y contenido incluso después de cerrar la sesión. Se omiten las solicitudes fallidas o sin terminar. Se incluyen las respuestas HTTP 4xx y 5xx completadas.

```python
from scrapling.fetchers import StealthySession

with StealthySession(record_requests=True, max_recorded_requests=1000) as session:
    session.fetch('https://example.com', network_idle=True)

for response in session.network.search(resource_type='document', limit=None):
    print(response.meta['network_id'], response.url, response.status)
    if note := response.meta.get('body_note'):
        print(note)
    else:
        print(response.body)
        print(response.css('title::text').get())

session.network.clear()
```

La misma API funciona con `AsyncStealthySession`. La grabación está desactivada por defecto. Al crear la sesión, usa `record_requests=True` y, si hace falta, `max_recorded_requests`.

- `session.network.search(url_pattern=None, method=None, resource_type=None, status=None, after_id=0, limit=100, include_static=True)` devuelve los objetos `Response` guardados en orden de ID de red. Con `limit=None` devuelve todas las coincidencias conservadas. `url_pattern` es una expresión regular que se aplica al buscar; si no es válida, el error aparece en ese momento. `after_id` selecciona respuestas con un ID mayor. `include_static=False` incluye solicitudes XHR/fetch y errores HTTP. Usa `True` para incluir todos los tipos de recurso y las redirecciones guardadas.
- `session.network.get(request_id)` devuelve un `Response` guardado, o `None` si ya no está en el historial.
- `session.network.clear()` borra el historial. Los ID siguen aumentando y nunca se reutilizan.

Cada `Response` guardado ofrece directamente `.url`, `.method`, `.status`, `.headers`, `.request_headers`, `.body` como bytes, `.json()` y los métodos CSS/XPath. Su `.meta` contiene `network_id`, `resource_type` y `request_body`, que puede ser bytes o `None`. Las cabeceras pueden estar incompletas si falla su lectura completa. Estas lecturas son locales incluso en sesiones asíncronas: no uses await ni llames a `.body()`. Si el contenido no se puede analizar, se conservan sus bytes, pero CSS y XPath usan un documento vacío.

Para buscar tráfico de API por URL, usa `session.network.search(url_pattern=r'https://api\.example\.com/.*', limit=None)`. Añade `resource_type='fetch'` o `resource_type='xhr'` si solo necesitas un tipo de solicitud.

Solo se guarda el contenido de respuesta de los tipos de texto admitidos en `Content-Type`: `text/*`, tipos `+json`/`+xml`, incluido SVG, JSON, XML, JavaScript, GraphQL y datos de formulario codificados como URL. Los tipos binarios, desconocidos o sin `Content-Type` conservan sus metadatos, pero no los bytes del contenido. El navegador sigue cargando los recursos con normalidad.

Los bytes guardados vienen de Playwright y pueden diferir de los originales del servidor. Si son UTF-8 válidos, el texto se interpreta como UTF-8, igual que en Playwright. En caso contrario, usa la codificación declarada. Las cabeceras no cambian.

Si el contenido se omite, supera el tamaño máximo o no se puede leer, devuelve `b''` y explica el motivo en `response.meta.get('body_note')`. El contenido que no es texto usa `Non-text body; not saved.`. Se conservan los metadatos y las cabeceras disponibles. El texto guardado, aunque esté vacío, no tiene nota. Las respuestas HEAD y los estados 204, 205 y 304 quedan vacíos sin nota.

Los métodos `search`, `get` y `clear` son locales y síncronos, incluso en sesiones asíncronas. Una entrada aparece cuando su respuesta ya está convertida y guardada. Los eventos del navegador se procesan mientras Playwright está activo. Las capturas asíncronas también necesitan que funcione el bucle de eventos. Leer el historial no espera a las capturas pendientes.

Cerrar una sesión tampoco espera a las capturas. Las que sigan en curso cuando la página cambie o se cierre el contexto pueden omitirse. Las respuestas ya guardadas siguen disponibles después del cierre.

Por defecto se conservan hasta 1000 solicitudes. Cada contenido de respuesta tiene un límite de 1 MiB, y todos juntos de 20 MiB. Al alcanzar un límite, se eliminan registros antiguos. Los límites de contenido son fijos y no se pueden cambiar en la sesión. Cubren las entradas guardadas y los bytes de respuesta, no la memoria total del navegador, las capturas simultáneas, las lecturas temporales completas, el HTML analizado ni los cuerpos de solicitud.

#### Migración a v5 {#migrating-in-v5}

En v5 se eliminaron `capture_xhr` y `response.captured_xhr`. Usa una sesión de navegador explícita con `record_requests=True` y lee `session.network.search(url_pattern=..., limit=None)`. Esto también reemplaza la captura de API con descargas de una sola llamada, por lo que debes conservar el objeto de sesión. Los filtros se aplican al historial guardado de toda la sesión, no a la captura ni a una sola descarga. Solo se guardan contenidos de respuesta de texto admitidos. `search()` devuelve hasta 100 coincidencias por defecto. `limit=None` devuelve todas las coincidencias conservadas, sin cambiar los límites del historial.

### Cabeceras y configuración regional del navegador {#browser-headers-and-locale}

```python
page = StealthyFetcher.fetch(
    'https://example.com',
    google_search=True,
    useragent='Mozilla/5.0...',
    locale='en-US',
)
```

### Ejemplo general {#general-example}
```python
from scrapling.fetchers import StealthyFetcher

def scrape_dynamic_content():

    page = StealthyFetcher.fetch(
        'https://example.com/dynamic',
        network_idle=True,
        wait_selector='.content'
    )


    content = page.css('.content')

    return {
        'title': content.css('h1::text').get(),
        'items': [
            item.text for item in content.css('.item')
        ]
    }
```

### Rotación de proxies {#proxy-rotation}

```python
from scrapling.fetchers import StealthySession, ProxyRotator


rotator = ProxyRotator([
    "http://proxy1:8080",
    "http://proxy2:8080",
    "http://proxy3:8080",
])


with StealthySession(proxy_rotator=rotator, headless=True) as session:
    page1 = session.fetch('https://example1.com')
    page2 = session.fetch('https://example2.com')


    page3 = session.fetch('https://example3.com', proxy='http://specific-proxy:8080')
```

!!! warning "Advertencia"

    Por defecto, las herramientas de navegador y sus sesiones usan un contexto persistente con un grupo de pestañas. Como los navegadores no permiten asignar un proxy por pestaña, al usar `ProxyRotator` se abre un contexto independiente para cada proxy, con una pestaña por contexto. Al terminar la tarea de esa pestaña, se cierran tanto ella como su contexto.

## Cuándo usarlo {#when-to-use}

Usa StealthyFetcher cuando:

- Necesites superar protecciones contra bots.
- Necesites una huella de navegador fiable.
- Necesites soporte completo de JavaScript.
- Quieras funciones automáticas para evitar la detección.
- Necesites automatizar un navegador.
- Trabajes con sitios protegidos por Cloudflare.
