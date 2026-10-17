---
title: "Migrar a v0.5"
description: "Pasa de Scrapling v0.4.15 a v0.5. Actualiza las importaciones del navegador, la captura de red, las herramientas MCP, los comandos CLI, los ajustes del parser y el comportamiento de los spiders."
---

# Migrar a v0.5 {#migrating-to-v05}

Esta guía cubre los cambios que debes revisar al pasar de **v0.4.15 a v0.5**. Incluye API eliminadas, herramientas con nuevos nombres y correcciones que pueden cambiar los resultados del rastreo o los archivos guardados.

## Lista rápida de migración {#quick-migration-checklist}

| Si usas... | Qué cambiar |
| --- | --- |
| `DynamicFetcher`, `DynamicSession` o `AsyncDynamicSession` | Usa la clase de navegación sigilosa correspondiente. |
| `capture_xhr` o `response.captured_xhr` | Usa una sesión de navegador con `record_requests=True` y `session.network`. |
| `keep_cdata` | Elimínalo de los ajustes del parser y del fetcher. |
| `scrapling extract stealthy-fetch` o `stealthy_fetch()` del shell | Usa `fetch` en su lugar. |
| Herramientas MCP | Actualiza los nombres de las herramientas, las llamadas para hacer capturas de pantalla y el manejo de la respuesta al crear sesiones. |
| `response.follow()` después de un POST o una solicitud con parámetros de consulta | Vuelve a pasar el método, la consulta y el cuerpo cuando los necesites. |
| Puntos de control de rastreo o cachés de respuestas guardados | Inicia un rastreo nuevo si tus solicitudes usan los datos de entrada de la huella que han cambiado. |
| `robots_txt_obey=True` | Maneja los fallos al obtener robots.txt, que ahora bloquean el rastreo de ese dominio. |

## Obtención con navegador {#browser-fetching}

### Sustituye las clases de navegador dinámico {#replace-the-dynamic-browser-classes}

Se ha eliminado el motor de navegador que usaba Playwright directamente. Toda la obtención con navegador usa ahora el motor sigiloso basado en Patchright.

| API eliminada | Sustitución |
| --- | --- |
| `scrapling.DynamicFetcher` | `scrapling.StealthyFetcher` |
| `scrapling.fetchers.DynamicFetcher` | `scrapling.fetchers.StealthyFetcher` |
| `scrapling.fetchers.chrome.PlayWrightFetcher` | `scrapling.fetchers.StealthyFetcher` |
| `scrapling.fetchers.DynamicSession` | `scrapling.fetchers.StealthySession` |
| `scrapling.fetchers.AsyncDynamicSession` | `scrapling.fetchers.AsyncStealthySession` |

Se han eliminado el módulo `scrapling.fetchers.chrome` y el módulo privado `_browsers._controllers`. Usa las importaciones públicas de la tabla anterior.

**Antes:**

```python
from scrapling.fetchers import DynamicFetcher

page = DynamicFetcher.fetch("https://example.com", headless=True)
```

**Ahora:**

```python
from scrapling.fetchers import StealthyFetcher

page = StealthyFetcher.fetch("https://example.com", headless=True)
```

Para las sesiones, sustituye `DynamicSession` por `StealthySession`, o `AsyncDynamicSession` por `AsyncStealthySession`. Haz el mismo cambio en el método `configure_sessions()` de tu spider. Los patrones de uso de `fetch()` y `async with` siguen siendo válidos.

Si tus callbacks importan tipos del navegador o capturan errores del navegador, cambia `playwright.sync_api` por `patchright.sync_api`, o `playwright.async_api` por `patchright.async_api`. Esto incluye `Page`, `Locator`, `Error` y `TimeoutError`.

Patchright evalúa JavaScript en un contexto aislado de forma predeterminada. Si un callback lee las variables JavaScript de la propia página, usa `page.evaluate(..., isolated_context=False)`.

Esto cambia el comportamiento del navegador además del nombre de importación. Revisa las opciones del navegador y los ajustes de su huella. Resolver Cloudflare sigue requiriendo `solve_cloudflare=True`; no está activado de forma predeterminada. Además, `extra_flags` ahora añade opciones a las de sigilo integradas en vez de sustituirlas.

Consulta [Obtención con navegador](fetching/stealthy.md) para ver las opciones actuales.

### Sustituye la captura XHR por el historial de red de la sesión {#replace-xhr-capture-with-session-network-history}

Se han eliminado el parámetro `capture_xhr` y el atributo `Response.captured_xhr`. Elimina el parámetro aunque su valor sea `None`. Una obtención de un solo uso ya no adjunta una lista XHR a su respuesta.

Las integraciones personalizadas que llaman a `ResponseFactory.from_playwright_response()` o `ResponseFactory.from_async_playwright_response()` también deben eliminar `xhr_captured`. Pasa `collect_history` por nombre para evitar problemas con el cambio de orden de los argumentos posicionales.

**Antes:**

```python
from scrapling.fetchers import StealthyFetcher

page = StealthyFetcher.fetch("https://example.com", capture_xhr="/api/")
for response in page.captured_xhr:
    print(response.url, response.body)
```

**Ahora:**

```python
from scrapling.fetchers import StealthySession

with StealthySession(record_requests=True) as session:
    page = session.fetch("https://example.com", network_idle=True)
    for response in session.network.search(url_pattern=r"/api/", limit=None):
        print(response.url, response.body)
```

Usa `AsyncStealthySession` y `await session.fetch(...)` para código asíncrono. Leer `session.network` no requiere `await`.

Hay algunas diferencias importantes:

- Establece `record_requests=True` al crear la sesión. Es un ajuste de la sesión, no de cada obtención.
- El historial pertenece a **toda la sesión**, incluidas las pestañas, las cargas de páginas y las acciones. Usa `after_id`, filtros o `session.network.clear()` si necesitas un alcance menor.
- Mueve la antigua expresión regular de `capture_xhr` a `url_pattern` al buscar en el historial.
- `search()` devuelve objetos `Response` guardados. Lee `.url`, `.status`, `.headers`, `.body` o `.json()` directamente. El ID de registro, el tipo de recurso y el cuerpo enviado están en `response.meta["network_id"]`, `response.meta["resource_type"]` y `response.meta["request_body"]`.
- El historial de Python incluye todos los tipos de recursos de forma predeterminada. Usa `resource_type="xhr"` o `resource_type="fetch"` para elegir uno, o `include_static=False` para solicitudes XHR/fetch y errores HTTP.
- `search()` devuelve un máximo de 100 coincidencias de forma predeterminada. Pasa `limit=None` para obtener todas las coincidencias guardadas. Las sesiones conservan hasta 1000 solicitudes de forma predeterminada; cambia este límite con `max_recorded_requests`.
- Solo se guardan las solicitudes completadas. La captura del cuerpo se limita a los tipos de contenido de texto admitidos, a 1 MiB por respuesta y a 20 MiB de datos de cuerpo guardados en total. Los registros más antiguos pueden eliminarse al alcanzar los límites. Consulta `response.meta.get("body_note")` para saber por qué se omitió un cuerpo.
- Al leer el historial o cerrar la sesión, no se espera a que terminen las capturas pendientes. Espera a los datos que necesitas antes de leerlos. El historial de Python guardado sigue disponible después de cerrar la sesión.

Consulta [Historial de red](fetching/stealthy.md#network-history) para ver los filtros y límites.

## Ajustes del parser {#parser-settings}

### Elimina `keep_cdata` {#remove-keep_cdata}

Se ha eliminado `keep_cdata` de `Selector`, de la configuración de los fetchers y de los ajustes que devuelve `display_config()`. Elimínalo de las llamadas directas al parser, de `Fetcher.configure(...)` y de los diccionarios `selector_config` que pases a fetchers o integraciones.

**Antes:**

```python
from scrapling import Selector

page = Selector("<p>Hello</p>", keep_cdata=True)
```

**Ahora:**

```python
from scrapling import Selector

page = Selector("<p>Hello</p>")
```

No hay ningún ajuste que lo sustituya. No afectaba al resultado del parser HTML. Si pasabas las opciones del parser por posición, elimina el antiguo argumento `keep_cdata` y usa nombres para `adaptive` y las opciones de almacenamiento.

## Línea de comandos y shell interactivo {#command-line-and-interactive-shell}

### Usa `fetch` para las solicitudes del navegador {#use-fetch-for-browser-requests}

La CLI tiene ahora un solo comando de navegador: `scrapling extract fetch`. Usa `StealthyFetcher`.

**Antes:**

```bash
scrapling extract stealthy-fetch "https://example.com" page.md
```

**Ahora:**

```bash
scrapling extract fetch "https://example.com" page.md
```

Si ya usas `scrapling extract fetch`, el nombre del comando no cambia, pero su motor pasa de `DynamicFetcher` a `StealthyFetcher`. Opciones como `--solve-cloudflare` pertenecen ahora a `fetch`.

En `scrapling shell`, sustituye `stealthy_fetch(...)` por `fetch(...)`. El atajo `fetch(...)` existente llama ahora a `StealthyFetcher.fetch`. Las clases dinámicas ya no se añaden al espacio de nombres del shell.

### Lee los archivos Markdown y de texto como UTF-8 {#read-markdown-and-text-files-as-utf-8}

Los comandos de extracción y `Convertor.write_content_to_file()` escriben ahora los archivos `.md` y `.txt` en **UTF-8**, sin importar el juego de caracteres de la página de origen. Actualiza cualquier código que lea esos archivos con la codificación original de la página. La salida `.html` sigue usando `page.encoding`.

El Markdown de varios elementos seleccionados tiene ahora líneas en blanco entre los elementos. Esto se aplica a `Response.markdown()` y a la salida en archivos Markdown. Actualiza las comparaciones exactas de la salida o los hashes guardados que dependían del texto concatenado.

## Servidor MCP {#mcp-server}

Actualiza los prompts guardados, las listas de herramientas permitidas, los wrappers y las definiciones de herramientas del cliente MCP. Reinicia o vuelve a conectar tu cliente MCP después de actualizar el servidor para que lea las herramientas actuales.

### Actualiza los nombres de herramientas y las llamadas en lote {#update-tool-names-and-bulk-calls}

| Herramienta de v0.4.15 | Sustitución en v0.5 |
| --- | --- |
| `fetch`, `stealthy_fetch` | `browser_fetch_once` |
| `open_session` | `browser_open` |
| `session_fetch` | `browser_fetch` |
| `screenshot` | `browser_screenshot` |
| `bulk_fetch`, `bulk_stealthy_fetch` | Una llamada a `browser_fetch_once` por URL, o varias llamadas a `browser_fetch` a través de una sesión abierta |
| `bulk_get` | Una llamada a `make_request` o `session_make_request` por URL |

Se han eliminado todas las herramientas en lote. Las herramientas que obtienen una sola URL devuelven un único `ResponseModel` con `status`, `content` y `url`, no una lista de respuestas. `content` sigue siendo una lista de cadenas.

Todas las herramientas de navegador MCP usan ahora el motor sigiloso. Elimina `session_type` de las llamadas a `browser_open`; ya no existe la opción de navegador dinámico. Su resultado contiene `session_type="stealthy"`. Las sesiones HTTP siguen usando `open_request_session` y devuelven `session_type="static"`.

Las integraciones de Python también deben dejar de importar `BrowserSessionType`, que se ha eliminado. `SessionType` solo acepta ahora `"stealthy"` y `"static"`.

Las llamadas a través de una misma sesión de navegador deben ejecutarse en orden porque comparten una página. Cierra las sesiones con `close_session` cuando termines.

### Lee los ajustes mediante `list_sessions` {#read-settings-through-list_sessions}

`browser_open` y `open_request_session` ahora solo devuelven:

```json
{
  "session_id": "my-session",
  "session_type": "stealthy"
}
```

El resultado de la creación ya no incluye `created_at`, `is_alive`, `settings` ni `message`. Llama a `list_sessions` para obtener los tres primeros campos. Se ha eliminado el `message` de confirmación. También debes cambiar el código que asumía que `SessionCreatedModel` tenía todos los campos de `SessionInfo`.

### Obtén la página antes de hacer una captura de pantalla {#fetch-before-taking-a-screenshot}

`browser_screenshot` captura la **página actual sin volver a cargarla**. Ya no acepta una URL ni las antiguas opciones de navegación y espera: `wait`, `wait_selector`, `wait_selector_state` y `network_idle`.

Sigue este orden:

1. Llama a `browser_open`.
2. Llama a `browser_fetch` con la URL y las opciones de carga de la página que necesites.
3. Si hace falta, llama a `browser_actions` para interactuar con la página o esperar al contenido.
4. Llama a `browser_screenshot` con el ID de sesión.
5. Llama a `close_session` cuando termines.

Por ejemplo, los argumentos para una captura de toda la página son:

```json
{
  "session_id": "my-session",
  "full_page": true
}
```

El `timeout` de esta herramienta limita ahora la operación de captura de pantalla. La herramienta no carga ninguna página. Para capturar un elemento, usa `selector` o `ref` y no establezcas `full_page=true`.

Las capturas de pantalla siguen devolviendo bloques de contenido de imagen y texto, con la URL de la página actual en el bloque de texto. No devuelven un `ResponseModel` de obtención.

Consulta la [guía MCP](ai/mcp-server.md) y la [referencia de la API](api-reference/mcp-server.md) para ver los esquemas completos.

## Spiders y solicitudes HTTP {#spiders-and-http-requests}

### Vuelve a pasar los datos de la solicitud al seguir un enlace {#pass-request-data-again-when-following-a-link}

`response.follow()` ya no copia `method`, `params`, `data`, `json`, `files` ni `multipart` de la solicitud anterior. También elimina los encabezados `Content-Length` heredados de `headers` y `extra_headers`.

Un enlace que sigues empieza ahora como una solicitud GET normal, salvo que pases los datos de la solicitud de forma explícita. Otros ajustes compartidos, como la sesión, el proxy y los callbacks, siguen las reglas de herencia existentes.

Si tu código anterior dependía de los datos POST heredados, cambia:

```python
yield response.follow("/next")
```

por:

```python
yield response.follow("/next", method="POST", json={"page": 2})
```

Pasa también `params` de forma explícita cuando la siguiente solicitud los necesite. Deja que el cliente HTTP calcule el nuevo `Content-Length`.

### Revisa las huellas de las solicitudes y el estado de rastreo guardado {#check-request-fingerprints-and-saved-crawl-state}

La huella de una solicitud es la clave que se usa para detectar solicitudes duplicadas y encontrar respuestas en caché. Sus datos de entrada ahora manejan tres casos de forma distinta:

- Los `params` se combinan con la URL antes de crear la clave. Las solicitudes a la misma URL con distintos parámetros de consulta ya no se consideran duplicadas de forma predeterminada.
- Los cuerpos JSON como `{}`, `[]`, `false`, `0` y `""` se conservan en la clave. Ya no comparten la clave de un cuerpo ausente. `None` sigue indicando que no hay cuerpo JSON.
- Con `fp_include_headers=True`, cambiar solo el orden de inserción de los encabezados ya no cambia la clave.

Si tu rastreo usa estos datos de entrada, termínalo antes de actualizar o inicia un rastreo nuevo con un nuevo punto de control y un nuevo directorio de caché de respuestas. Las claves guardadas anteriormente pueden ser distintas de las nuevas. Este es un cambio en la identidad de las solicitudes, no un formato nuevo para los archivos de puntos de control.

El modo de desarrollo ahora solo escribe las respuestas en la caché después de comprobar si están bloqueadas. Las páginas bloqueadas no se guardan como resultados correctos en caché. Los archivos de caché existentes no se limpian automáticamente; borra las entradas antiguas si antes guardaste una página de verificación.

Los rastreos fallidos conservan ahora sus archivos de puntos de control. Revisa tu código de limpieza si asumía que esos archivos desaparecían después de un error. Consulta [Pausar y reanudar](spiders/advanced.md#pause-resume) y [Modo de desarrollo](spiders/advanced.md#development-mode).

### Revisa los fallos de robots.txt {#check-robotstxt-failures}

Con `robots_txt_obey=True`, una excepción al obtener robots.txt o una respuesta distinta de HTTP 200 o 4xx ahora bloquea las solicitudes a ese dominio. Antes, esos fallos permitían el rastreo. HTTP 200 sigue proporcionando las reglas y HTTP 4xx sigue permitiendo el acceso.

El resultado se guarda en caché durante todo el rastreo. Soluciona el problema de acceso a robots.txt e inicia un rastreo nuevo; las solicitudes posteriores del mismo rastreo no volverán a intentar la consulta fallida. Esto no cambia el valor predeterminado `robots_txt_obey=False`.

### Revisa las restricciones de enlaces y los callbacks de sitemaps {#check-link-restrictions-and-sitemap-callbacks}

- Una restricción de `LinkExtractor` que no coincide con nada ahora no devuelve enlaces. Ya no recurre a la página completa. Corrige la expresión `restrict_css` o `restrict_xpath` si tu rastreo encuentra ahora menos enlaces.
- Una restricción ahora puede seleccionar el propio elemento del enlace, no solo un elemento padre. Esto puede añadir enlaces que antes se omitían. Revisa los conjuntos de URL esperados.
- `SitemapSpider` envía ahora las URL de las páginas a `parse()` cuando no hay reglas o cuando una regla coincidente tiene `callback=None`. Ya no vuelve a enviar esas páginas HTML al parser del sitemap. Implementa `parse()` para esos casos y elimina las soluciones alternativas para el enrutamiento anterior.
- Se elimina la marca de orden de bytes Unicode al principio de robots.txt y de las fuentes CSV. La primera directiva de robots ahora tiene efecto y el primer encabezado CSV ya no empieza con `\ufeff`. Si defines `headers` personalizados, la marca se elimina del valor del primer campo en su lugar. Actualiza el código que compensaba ese prefijo oculto. Los comentarios XML y las instrucciones de procesamiento de los sitemaps también se omiten en lugar de provocar un fallo de análisis.

### Revisa los datos de formularios, los encabezados y el JSON de la CLI {#check-form-data-headers-and-cli-json}

Los datos de formularios en diccionarios expanden ahora los valores de listas y tuplas en claves repetidas. Por ejemplo, `data={"tag": ["a", "b"]}` envía `tag=a&tag=b`. Una lista vacía no envía ninguna entrada para esa clave. Se añade el encabezado predeterminado `Content-Type: application/x-www-form-urlencoded` si no has proporcionado uno.

Si necesitas otro formato de envío, pasa una cadena o bytes codificados de forma explícita. `json`, el `content` sin procesar y las cargas multipart mantienen su propio manejo del cuerpo. Los valores `None` **no se eliminan** de los datos del formulario ni de los parámetros de consulta; se conservan como la cadena `None`.

Los encabezados HTTP de cada solicitud ahora sustituyen a los de la sesión sin distinguir entre mayúsculas y minúsculas. Un encabezado de solicitud llamado `authorization` sustituye al `Authorization` de la sesión en vez de enviar ambos. Elimina el código que compensaba los nombres de encabezados duplicados.

Los valores JSON de la CLI `{}`, `[]`, `false`, `0` y `""` ahora se envían en vez de omitirse sin aviso. Además, `curl2fetcher()` aplica ahora el agente de usuario de `-A` de curl y pasa correctamente los proxies de `-x` como una cadena URL. Un encabezado explícito `-H 'User-Agent: ...'` de curl sigue teniendo prioridad sobre `-A`.

## Otros cambios en la salida que debes revisar {#other-output-changes-to-check}

Estas correcciones no eliminan API, pero pueden cambiar los resultados guardados y las pruebas de salida exacta:

- Los selectores CSS y XPath generados ahora incluyen `:nth-of-type(1)` o `[1]` cuando es necesario para identificar al primero de varios elementos hermanos con la misma etiqueta. Actualiza las cadenas de selectores esperadas; no elimines la nueva marca de posición.
- El contenido limpiado para IA ahora conserva los elementos visibles con valores como `opacity:0.95`, elimina elementos ocultos por más variantes de estilos en línea y los elementos `<slot hidden>`, y elimina todas las etiquetas de ruido coincidentes aunque estén anidadas. Vuelve a comprobar la salida exacta de Markdown, texto y HTML saneado.
- La conversión de respuestas del navegador ahora lee declaraciones de charset con distintas mayúsculas y minúsculas, espacios o valores entre comillas, como `text/plain; CHARSET = "iso-8859-15"`. Las respuestas que no son HTML y tienen estos encabezados ahora usan la codificación declarada en vez de recurrir a UTF-8. Vuelve a comprobar el texto decodificado de esas respuestas.

## Verifica la actualización {#verify-your-upgrade}

Ejecuta un rastreo pequeño antes del trabajo completo. Comprueba los datos extraídos, las URL seguidas, los cuerpos de las solicitudes enviadas, la codificación de los archivos guardados y el comportamiento de la caché o de los puntos de control del que dependas. Para las integraciones MCP, comprueba los datos de entrada de las herramientas y los datos devueltos con los esquemas actuales.

Para los cambios de versiones anteriores, consulta el [registro de cambios](changelog.md).
