---
title: "Historial de cambios de Scrapling"
description: "Notas de las versiones de Scrapling, con nuevas funciones, correcciones y cambios incompatibles."
---

# Historial de cambios {#changelog}

Todos los cambios importantes de Scrapling, tomados de las [versiones de GitHub](https://github.com/D4Vinci/Scrapling/releases).

## [v0.5](https://github.com/D4Vinci/Scrapling/releases/tag/v0.5) - 2026-10-17 {#v0.5}

**Scrapling v0.5 mejora casi todo: obtención de páginas, análisis, spiders, automatización del navegador, herramientas de IA y documentación en diez idiomas 🚀**

!!! warning "Advertencia"

    **Esta versión introduce muchos cambios incompatibles que no caben aquí. Consulta la [guía de migración a v0.5](migrating-to-v0.5.md) antes de actualizar.**

### 🚀 Novedades y mejoras de uso {#v0.5-new-stuff-and-quality-of-life-changes}

- **Un servidor MCP mucho más capaz para agentes de IA que pueden resolver casi cualquier CAPTCHA** (consulta la [documentación](ai/mcp-server.md)):

    - **Flujos completos en el navegador**: rellena formularios, haz clic, pasa el cursor sobre elementos, desplázate, usa el teclado, gestiona diálogos y espera resultados en una sola secuencia ordenada. Admite distintos tipos de campos e interacciones más lentas, y las acciones se detienen ante el primer error.
    - **Lee y busca en la página actual sin recargarla**: extrae HTML, Markdown o texto de una página completa o de un elemento. Las instantáneas de página permiten buscar y muestran los roles, nombres y posiciones de los elementos, con vistas enfocadas que conservan el contexto que los rodea.
    - **Ejecuta JavaScript propio y toma capturas de zonas concretas**: ejecuta scripts, incluidas tareas asíncronas, con acceso al JavaScript de la propia página. Captura elementos individuales, el área visible o la página completa en PNG o JPEG.
    - **Inspecciona la actividad de red y reutiliza los inicios de sesión**: examina solicitudes y respuestas registradas, guarda y restaura el estado de inicio de sesión del navegador e interactúa con elementos dentro de Shadow DOM abierto o cerrado. Lee el tráfico registrado antes de cerrar la sesión.
    - **Usa menos tokens y recibe errores más claros**: las descripciones más breves de las herramientas y las instrucciones compartidas reducen el texto repetido, mientras que los fallos del navegador y de las solicitudes llegan a los agentes con mensajes de error útiles.

- **Ve las solicitudes que hay detrás de la página**. Activa `record_requests=True` para registrar el tráfico completado durante cargas, acciones y entre pestañas, y luego inspecciona las respuestas guardadas sin volver a enviar solicitudes. (Consulta la [documentación](fetching/stealthy.md#network-history))

    ```python
    from scrapling.fetchers import StealthySession

    with StealthySession(record_requests=True) as session:
        session.fetch("https://example.com", network_idle=True)
        for response in session.network.search(url_pattern=r"/api/", limit=None):
            print(response.url, response.status, response.body)
    ```

    - Filtra por URL, método, tipo de recurso o estado; recupera una respuesta por su ID. Inspecciona cabeceras, datos enviados, respuestas de API, errores HTTP y redirecciones mediante la API habitual de `Response`.
    - Conserva los cuerpos de texto admitidos con límites de tamaño, junto con los metadatos y el motivo cuando un cuerpo no se puede guardar. El límite predeterminado es de 1000 solicitudes. Funciona con sesiones síncronas y asíncronas; el historial guardado en Python sigue disponible para lectura después del cierre.

- **Guarda un inicio de sesión una vez y reutilízalo entre ejecuciones**. `save_state(path)` y `load_state(path)` guardan y cargan cookies, almacenamiento local e IndexedDB en JSON compatible con Playwright. Las sesiones de navegador síncronas y asíncronas admiten ambos métodos. (Consulta la [documentación](fetching/stealthy.md#save-and-load-session-state))
    - Carga el estado antes de obtener o recargar una página. Requiere un contexto de navegador compartido ya iniciado y sin `proxy_rotator`; no se guardan las pestañas, los ajustes del navegador ni `sessionStorage`.

- **Extrae Shadow DOM abierto con `pierce_shadow=True`** y luego usa CSS o XPath como siempre. Disponible en los fetchers de navegador, las sesiones y la opción `--pierce-shadow` de la CLI. Conserva el contenido de los slots sin cambiar la página activa. La captura de HTML excluye las raíces cerradas y los documentos de iframes. (Consulta la [documentación](fetching/stealthy.md#shadow-dom))

- **Elige cómo explora tu spider un sitio**. `CrawlSpider` y sus subclases, incluida `ContentSpider`, admiten `crawl_strategy="bfs"` para programar primero las solicitudes más antiguas o `"dfs"` para programar primero las más recientes. La prioridad sigue prevaleciendo, y las páginas procesadas de forma concurrente pueden terminar en otro orden. (Consulta la [documentación](spiders/generic-templates.md#crawl-order))

### 🐛 Correcciones de errores {#v0.5-bug-fixes}

- **Mejorada la resolución de Cloudflare** con detección de widgets que aparecen tarde, menos esperas innecesarias y límites en los bucles de reintentos para desafíos pasivos e iframes ocultos. Corrige [#468](https://github.com/D4Vinci/Scrapling/issues/468) y [#509](https://github.com/D4Vinci/Scrapling/issues/509).
- **Corregido el inicio del navegador desde una consola de Windows con permisos de administrador**. Corrige [#463](https://github.com/D4Vinci/Scrapling/issues/463).
- **Se conservan las opciones de ocultación integradas al añadir opciones propias del navegador**, por @alkaz-nodemaven en [#430](https://github.com/D4Vinci/Scrapling/pull/430).
- **Mejorada la lectura de la codificación de caracteres en las respuestas del navegador**, incluidas las declaraciones con distintas mayúsculas y minúsculas, espacios o valores entre comillas.
- **Ya no se registra como error la ausencia de un desafío de Cloudflare** cuando no hay ningún desafío que resolver. Corrige [#459](https://github.com/D4Vinci/Scrapling/issues/459).

- **Corregidas las huellas de las solicitudes** para los parámetros de consulta, por @yetval en [#448](https://github.com/D4Vinci/Scrapling/pull/448), los cuerpos JSON vacíos o con valores evaluados como falsos, por @ac1982 en [#480](https://github.com/D4Vinci/Scrapling/pull/480), y el orden de inserción de cabeceras, por @SarwadnyaMahajan en [#466](https://github.com/D4Vinci/Scrapling/pull/466).
- **Corregida la transferencia no deseada de datos de la solicitud a los enlaces seguidos**, incluidas las cabeceras antiguas relacionadas con el cuerpo, por @yetval en [#462](https://github.com/D4Vinci/Scrapling/pull/462).
- **Se impide guardar las respuestas bloqueadas como entradas correctas en la caché de desarrollo**, por @Kuang-xianxin en [#446](https://github.com/D4Vinci/Scrapling/pull/446).
- **Se conservan los archivos de puntos de control cuando un rastreo falla con una excepción**, por @SulimanAbdulrazzaq en [#486](https://github.com/D4Vinci/Scrapling/pull/486).
- **Corregida la gestión de errores de robots.txt** para que las consultas fallidas no se guarden en caché como permiso para rastrear, por @prateekraawat1 en [#443](https://github.com/D4Vinci/Scrapling/pull/443).
- **Corregida la extracción de enlaces con selectores que limitan el ámbito**, incluidas las coincidencias vacías y los selectores que apuntan al propio elemento del enlace, por @SulimanAbdulrazzaq en [#452](https://github.com/D4Vinci/Scrapling/pull/452) y [#483](https://github.com/D4Vinci/Scrapling/pull/483).
- **Corregida la asignación de callbacks del mapa del sitio**, por @SulimanAbdulrazzaq en [#458](https://github.com/D4Vinci/Scrapling/pull/458), **y el análisis de XML con comentarios o instrucciones de procesamiento**, por @sup3dev en [#450](https://github.com/D4Vinci/Scrapling/pull/450).
- **Se manejan las marcas de orden de bytes al inicio de robots.txt y de los feeds CSV**, por @SulimanAbdulrazzaq en [#453](https://github.com/D4Vinci/Scrapling/pull/453).
- **Corregido el manejo de `stealthy_headers` en las sesiones HTTP de los spiders**, pasando la opción a la sesión en lugar de enviarla directamente a `curl_cffi`, por @Yigtwxx en [#475](https://github.com/D4Vinci/Scrapling/pull/475).

- **Corregida la codificación de formularios a partir de diccionarios con valores de tipo lista o tupla**, manteniendo la precedencia del cuerpo de la solicitud y el manejo existente de `None`, con aportes de @SulimanAbdulrazzaq en [#485](https://github.com/D4Vinci/Scrapling/pull/485).
- **Corregida la combinación de cabeceras HTTP de sesión y de cada solicitud sin distinguir mayúsculas de minúsculas**, por @SulimanAbdulrazzaq en [#487](https://github.com/D4Vinci/Scrapling/pull/487).
- **Corregidas las solicitudes de la CLI que descartaban sin avisar los cuerpos JSON vacíos o con valores evaluados como falsos**, por @SulimanAbdulrazzaq en [#484](https://github.com/D4Vinci/Scrapling/pull/484).
- **Las exportaciones a archivos Markdown y de texto ahora usan siempre UTF-8**, y los errores de conversión ya no truncan un archivo de salida existente, por @SulimanAbdulrazzaq en [#488](https://github.com/D4Vinci/Scrapling/pull/488).
- **Corregido el manejo de las opciones de agente de usuario y proxy de curl en `curl2fetcher()`**, por @SulimanAbdulrazzaq en [#490](https://github.com/D4Vinci/Scrapling/pull/490).

- **Corregidos los bloques Markdown que se unían sin separación** al convertir varios elementos seleccionados mediante `Response.markdown()` o la extracción de la CLI, con aportes de @Yigtwxx en [#432](https://github.com/D4Vinci/Scrapling/pull/432).
- **Corregida la limpieza del contenido oculto en la salida para IA** para conservar contenido visible como `opacity:0.95`, reconocer más estilos que ocultan contenido y eliminar slots ocultos, con aportes de @Yigtwxx en [#460](https://github.com/D4Vinci/Scrapling/pull/460).
- **Corregida la eliminación de etiquetas de ruido que se detenía antes de tiempo ante etiquetas anidadas**, por @Yigtwxx en [#474](https://github.com/D4Vinci/Scrapling/pull/474).
- **Corregidos los selectores CSS y XPath generados para el primero de varios elementos hermanos con la misma etiqueta**, por @yellow-dog-dog en [#495](https://github.com/D4Vinci/Scrapling/pull/495).
- **Resuelta una advertencia de obsolescencia del analizador HTML de lxml**, por @afsuyadi en [#493](https://github.com/D4Vinci/Scrapling/pull/493).

### Documentación {#v0.5-docs}

- **El sitio completo ahora está en diez idiomas**: inglés, árabe, español, portugués de Brasil, francés, alemán, chino simplificado, japonés, ruso y coreano. Las guías, las referencias de API, los tutoriales y el [historial de cambios](changelog.md) están traducidos, con escritura de derecha a izquierda para el árabe y cambios de idioma que conservan la página y la sección.
- **Guías, ejemplos del README y pasos de configuración más claros**, que abarcan los datos de puntos de control, las codificaciones del navegador, el estado guardado, el historial de red, Shadow DOM y el orden de rastreo.
- **Actualizada la habilidad para agentes**, junto con sus ejemplos, referencias y archivo descargable, para las herramientas actuales del navegador y de MCP.
- **El historial de cambios se ha trasladado al sitio web** y se ha añadido acceso al código fuente Markdown de cada página.

### Proyecto {#v0.5-project}

- Renovados el logotipo de Scrapling, las imágenes de portada y la presentación del sitio web.
- Ampliadas las pruebas de acciones del navegador, diálogos, extracción, capturas de pantalla, JavaScript, registro de red, archivos de estado, Shadow DOM y correcciones del rastreador.
- Añadido un marcador para las pruebas del navegador y ejecuciones separadas de las pruebas de navegador, asíncronas y en paralelo. Mejorada la compatibilidad con Windows de las pruebas de puntos de control y CSV, por @diegobravtraps-oss en [#457](https://github.com/D4Vinci/Scrapling/pull/457).
- Actualizada la configuración compartida para compilar la documentación multilingüe y las instrucciones para contribuir.

## [v0.4.15](https://github.com/D4Vinci/Scrapling/releases/tag/v0.4.15) - 2026-08-23 {#v0.4.15}

**Una de las mayores versiones de este año: un servidor MCP renovado, Markdown listo para RAG en una línea, un solucionador de Cloudflare mejorado y pestañas del navegador que siguen abiertas para la automatización 🚀**

!!! warning "Advertencia"

    **Esta versión introduce cambios incompatibles en el servidor MCP. Consulta la sección de [cambios incompatibles](https://github.com/D4Vinci/Scrapling/blob/v0.4.15/docs/ai/mcp-server.md#breaking-changes) antes de actualizar.**

### 🚀 Novedades y mejoras de uso {#v0.4.15-new-stuff-and-quality-of-life-changes}

- **Las pestañas del navegador ahora siguen abiertas y se reutilizan entre solicitudes** (consulta la [documentación](fetching/stealthy.md#session-management)):
    - Todas las sesiones del navegador conservan sus pestañas tras una solicitud, y la siguiente reutiliza una pestaña libre en lugar de abrir otra.
    - Cada solicitud vuelve a aplicar sus propios ajustes (tiempos de espera, cabeceras y bloqueo de recursos) a la pestaña que recibe, por lo que los ajustes no pasan de una solicitud a otra.
    - Las pestañas que dan error se cierran y se reemplazan, y el nuevo método `close_pages()` cierra todas las pestañas abiertas.
    - La página que obtuviste sigue cargada, de modo que una función `page_setup` en la siguiente solicitud se ejecuta sobre ella antes de navegar a otra página. Esto permite encadenar pasos de automatización entre solicitudes.

- **Convierte cualquier página en Markdown limpio y listo para LLM con `Response.markdown()`** (consulta la [documentación](ai/building-rag-systems.md)):

    ```python
    from scrapling.fetchers import Fetcher

    markdown = Fetcher.get("https://example.com").markdown(main_content_only=True)
    ```

    - Primero se eliminan siempre los scripts, los estilos y el contenido oculto de inyección de prompts, con la misma limpieza que hace el servidor MCP.
    - Pasa `css_selector` para convertir solo los elementos que necesitas.
    - Disponible mediante el nuevo extra `rag` (`pip install "scrapling[rag]"`), también incluido en los extras `ai`/`shell`/`all`.

- **Nueva plantilla `SiteToMarkdownSpider` para rastrear un sitio completo y crear una colección de documentos Markdown para procesos RAG** (consulta la [documentación](ai/building-rag-systems.md)):

    ```python
    from scrapling.spiders import SiteToMarkdownSpider

    class DocsSpider(SiteToMarkdownSpider):
        name = "docs"
        start_urls = ["https://example.com/docs/"]
        allowed_domains = {"example.com"}
        output_dir = "docs_markdown"

    result = DocsSpider().start()
    result.items.to_jsonl("docs.jsonl")
    ```

    - Produce un elemento por página con `url`/`title`/`markdown`, y el ajuste opcional `output_dir` escribe un archivo Markdown por página.
    - `max_pages` limita el rastreo y, como se basa en `CrawlSpider`, redefinir `rules()` te da control total sobre los enlaces que se siguen.

- **El servidor MCP se ha rediseñado (cambio incompatible)** (consulta los [cambios incompatibles](https://github.com/D4Vinci/Scrapling/blob/v0.4.15/docs/ai/mcp-server.md#breaking-changes) y la [documentación](ai/mcp-server.md)):
    - Las 13 herramientas ahora se dividen en dos modos: herramientas de una sola ejecución (`fetch`, `bulk_fetch`, `stealthy_fetch`, `bulk_stealthy_fetch`), que siempre abren su propio navegador y muestran sus valores predeterminados reales, y herramientas de sesión, que usan una sesión abierta una sola vez.
    - La nueva herramienta `session_fetch` obtiene páginas mediante una sesión del navegador, mientras que `open_session` ahora solo guarda los ajustes del navegador y devuelve los ajustes efectivos de la sesión al agente de IA.
    - La herramienta `get` pasa a llamarse `make_request` y ahora admite cualquier método HTTP.
    - Las nuevas herramientas `open_request_session` y `session_make_request` dan a la IA sesiones HTTP persistentes que conservan las cookies y la huella del navegador entre solicitudes.
    - Esto también evita que las operaciones de obtención restablezcan los ajustes de la sesión, un problema que @Yigtwxx corrigió primero en [#418](https://github.com/D4Vinci/Scrapling/pull/418).

- **El transporte HTTP del servidor MCP ahora exige autenticación y escucha en localhost de forma predeterminada (cambio incompatible)**, por @yamantaka-singh en [#414](https://github.com/D4Vinci/Scrapling/pull/414) (corrige [#413](https://github.com/D4Vinci/Scrapling/issues/413); consulta la [documentación](ai/mcp-server.md#authentication)):
    - Pasa `--auth-token` (o la variable de entorno `SCRAPLING_MCP_AUTH_TOKEN`) para exigir un token bearer, o `--no-auth` si quieres servirlo sin autenticación de forma explícita.
    - Pasa `--host 0.0.0.0` para aceptar conexiones desde la red.

### 🐛 Correcciones de errores {#v0.4.15-bug-fixes}

- **La resolución de Cloudflare Turnstile/Interstitial ahora funciona sin importar la configuración regional del navegador y ya no entra en un bucle infinito con desafíos interactivos en modo headless**. Las páginas del navegador sigiloso también dejan de fallar durante la resolución, con aportes de @subediparas5 en [#412](https://github.com/D4Vinci/Scrapling/pull/412). (Corrige [#411](https://github.com/D4Vinci/Scrapling/issues/411) y [#422](https://github.com/D4Vinci/Scrapling/issues/422))
- **Corregido el problema por el que `find`/`find_all` con `class_` omitían sin avisar elementos con varias clases**, por @yetval en [#410](https://github.com/D4Vinci/Scrapling/pull/410), **y los valores vacíos de `class_` y las cadenas CSS sin escapar**, por @yamantaka-singh en [#417](https://github.com/D4Vinci/Scrapling/pull/417).
- **Corregida la pérdida de metadatos de la solicitud al reutilizar respuestas en caché en `development_mode`**, por @Yigtwxx en [#419](https://github.com/D4Vinci/Scrapling/pull/419).
- **Corregidas las solicitudes HTTP con `retries` inferior a 1 que fallaban sin enviar la solicitud**, por @Yigtwxx en [#420](https://github.com/D4Vinci/Scrapling/pull/420).

### Documentación {#v0.4.15-docs}

- **Se han reorganizado las secciones del sitio**: la nueva sección "Uso con IA" contiene el servidor MCP, la nueva página de [habilidad para agentes](ai/agent-skill.md) y la guía para [crear sistemas RAG](ai/building-rag-systems.md). La guía de migración desde BeautifulSoup pasó junto a la integración con Scrapy en "Integraciones y migraciones".
- **Añadido un [historial de cambios](changelog.md)** al repositorio con las notas de todas las versiones publicadas hasta ahora.

## [v0.4.14](https://github.com/D4Vinci/Scrapling/releases/tag/v0.4.14) - 2026-08-10 {#v0.4.14}

**Una versión de mantenimiento rápida para corregir la instalación con `uv` 🔧**

### 🐛 Correcciones de errores {#v0.4.14-bug-fixes}

- **Corregido el problema por el que `uv` rechazaba instalar v0.4.13 de forma predeterminada y usaba una versión anterior sin avisar**. La versión anterior exigía una versión preliminar de `curl_cffi`, que `uv` no permite salvo que lo actives de forma explícita.
Todas las dependencias ahora se resuelven con versiones estables. (Corrige [#407](https://github.com/D4Vinci/Scrapling/issues/407))

## [v0.4.13](https://github.com/D4Vinci/Scrapling/releases/tag/v0.4.13) - 2026-08-09 {#v0.4.13}

**Una nueva actualización con spiders para feeds y un servidor MCP más inteligente 🎉**

### 🚀 Novedades y mejoras de uso {#v0.4.13-new-stuff-and-quality-of-life-changes}

- **Nuevas plantillas de spiders para feeds**. `XMLFeedSpider` recorre los nodos de cualquier feed XML (RSS, Atom, feeds de productos, etc.), y `CSVFeedSpider` recorre las filas CSV como diccionarios. Ambos descomprimen automáticamente los feeds comprimidos con gzip. (Consulta la [documentación](spiders/generic-templates.md))

  ```python
  from scrapling.spiders import XMLFeedSpider

  class RSSSpider(XMLFeedSpider):
      name = "rss"
      start_urls = ["https://example.com/feed.xml"]

      async def parse_node(self, response, node):
          yield {"title": node.findtext("title"), "link": node.findtext("link")}

  result = RSSSpider().start()
  ```

- **El servidor MCP se ha actualizado a MCP SDK v2 y ahora es más inteligente**. El servidor incluye instrucciones que enseñan a tu agente de IA a usar las herramientas con eficiencia; cada herramienta declara anotaciones para que clientes como Claude Code puedan aprobar automáticamente las que solo leen; las descripciones son más breves para ahorrar tokens; y el servidor informa de su versión y logotipo a los clientes MCP. (Consulta la [documentación](ai/mcp-server.md))
- **Añadido el comando `scrapling-mcp`**, que ejecuta directamente `scrapling mcp`, para registrar Scrapling en clientes y registros MCP que esperan un único comando con una sola línea.
- **Las versiones de Playwright/Patchright y de los navegadores ya no están fijadas**. El User-Agent generado ahora siempre coincide con la versión exacta de Chromium que controla tu instalación de Playwright/Patchright, por lo que Scrapling ya no fija sus versiones y puedes actualizarlas libremente. Ejecuta `scrapling install --force` después de actualizar para renovar los navegadores.

### 🐛 Correcciones de errores {#v0.4.13-bug-fixes}

- **Corregido el fallo al importar Scrapling con un ValueError de `browserforge`** cuando el paquete de datos de huellas se queda atrás respecto a las versiones de los navegadores. (Corrige [#394](https://github.com/D4Vinci/Scrapling/issues/394), [#396](https://github.com/D4Vinci/Scrapling/issues/396) y [#400](https://github.com/D4Vinci/Scrapling/issues/400))
- **Corregido el tamaño incorrecto de los grupos de páginas en las herramientas de navegador por lotes de MCP**, que hacía fallar `bulk_fetch` con lotes de más de 50 URL y que `bulk_stealthy_fetch` obtuviera todas las URL desde una sola pestaña, por @Yigtwxx en [#393](https://github.com/D4Vinci/Scrapling/pull/393).

### Proyecto {#v0.4.13-project}

- **Nueva [política de contribuciones con IA](https://github.com/D4Vinci/Scrapling/blob/main/AI_POLICY.md)**: las contribuciones asistidas por IA son bienvenidas, pero debes indicarlo en la solicitud de cambios o en la incidencia; los envíos que parezcan generados por IA sin indicarlo se etiquetan y se cierran.

## [v0.4.12](https://github.com/D4Vinci/Scrapling/releases/tag/v0.4.12) - 2026-07-26 {#v0.4.12}

**Una versión centrada en que tus spiders se adapten mejor a los sitios que rastrean**

### 🚀 Novedades y mejoras de uso {#v0.4.12-new-stuff-and-quality-of-life-changes}

- **Los spiders ahora pueden ajustar su propia velocidad con AutoThrottle.** En lugar de adivinar un `download_delay` que puede ser demasiado lento o provocar un bloqueo, el spider mide cuánto tarda cada sitio en responder y ajusta la espera de cada dominio por su cuenta. Cuando un sitio empieza a bloquearte o limitar tus solicitudes, duplica la espera (o espera exactamente lo que indique la cabecera `Retry-After`) hasta que deje de hacerlo, y después vuelve a acelerar. Tu `download_delay` y cualquier `Crawl-delay` de robots.txt siguen siendo el mínimo. (Consulta la [documentación](spiders/advanced.md#autothrottle))

    ```python
    class MySpider(Spider):
        name = "adaptive"
        start_urls = ["https://example.com"]
        autothrottle_enabled = True
        autothrottle_start_delay = 2.0
        autothrottle_max_delay = 30.0
        autothrottle_block_backoff = True
    ```

- **Exporta tus resultados a CSV y XML**, además de los exportadores JSON/JSONL que ya tenías. Los elementos que no comparten todas las claves se siguen exportando sin perder datos, y los valores anidados se escriben como JSON. (Consulta la [documentación](spiders/getting-started.md))

    ```python
    result = MySpider().start()
    result.items.to_csv("products.csv")
    result.items.to_xml("products.xml")
    ```

- **El servidor MCP ahora puede exigir autenticación**, para que puedas exponerlo de forma segura en lugar de mantenerlo solo en tu equipo. Se rechaza cualquier solicitud sin el token, y también puedes limitar los nombres de host a los que responde el servidor. (Consulta la [documentación](ai/mcp-server.md))

    ```bash
    scrapling mcp --http --auth-token "$(openssl rand -hex 32)"
    ```

- **Los navegadores ahora aceptan URL de CDP por HTTP**, además de las de WebSocket. Así, junto a los endpoints `wss://` de los proveedores de navegadores gestionados, puedes conectar cualquier fetcher de navegador o sesión MCP a un Chrome que hayas iniciado con `--remote-debugging-port=9222`.

- **Las imágenes Docker publicadas ahora llevan una etiqueta con su versión**, en lugar de solo `latest`, para que puedas fijar la versión exacta que quieras, por @JanRK en [#384](https://github.com/D4Vinci/Scrapling/pull/384).

### 🐛 Correcciones de errores {#v0.4.12-bug-fixes}

- **Corregida la pérdida de todas las cookies en las respuestas en caché** cuando procedían de un motor de navegador, lo que rompía sin avisar la lógica de sesión o autenticación que dependía de ellas al usar el modo de desarrollo de los spiders, por @amitvijapur en [#379](https://github.com/D4Vinci/Scrapling/pull/379). (Corrige [#376](https://github.com/D4Vinci/Scrapling/issues/376))

- **Corregido el problema por el que `StealthyFetcher` imponía la configuración regional `en-US`** a todos los navegadores en lugar de seguir la del sistema. Esto hacía que los sitios detectaran una diferencia entre tu configuración regional y tu dirección IP y te trataran como sospechoso, por ejemplo con respuestas 429 de Google. (Corrige [#381](https://github.com/D4Vinci/Scrapling/issues/381))

- **Corregido un mensaje de error engañoso en el sistema de almacenamiento** y eliminada una llamada sin uso que quedaba tras las inserciones, por @fix2015 en [#377](https://github.com/D4Vinci/Scrapling/pull/377).

### Rendimiento {#v0.4.12-performance}

- **El tiempo de ejecución de `get_all_text()` ahora crece en proporción al número de nodos, O(nodes)** en lugar de recorrer los ancestros de cada nodo de texto, lo que lo hace unas 5-6 veces más rápido en páginas con muchos niveles anidados, por @yetval en [#378](https://github.com/D4Vinci/Scrapling/pull/378).

## [v0.4.11](https://github.com/D4Vinci/Scrapling/releases/tag/v0.4.11) - 2026-07-12 {#v0.4.11}

**Una actualización importante con la primera plantilla de spider para una plataforma, un parser más rápido y correcciones importantes 🎉**

### 🚀 Novedades y mejoras de uso {#v0.4.11-new-stuff-and-quality-of-life-changes}

- **¡Añadido `ShopifySpider`, la primera plantilla de spider para una plataforma!** Extrae todos los productos de cualquier tienda Shopify mediante su API JSON sin usar el HTML del sitio. Crea una subclase, define el dominio de la tienda y listo (consulta la [documentación](spiders/platform-templates.md))

  ```python
  from scrapling.spiders import ShopifySpider

  class MyStore(ShopifySpider):
      target_website = "example.com"

  result = MyStore().start()
  ```

- **Añadido `--executable-path` a los comandos de navegador de la CLI**. Tanto `scrapling extract fetch` como `scrapling extract stealthy-fetch` ahora aceptan un ejecutable de navegador personalizado compatible con Chromium, y usan la variable de entorno `SCRAPLING_EXECUTABLE_PATH` cuando no pasas la opción. Así ofrecen lo mismo que el servidor MCP (resuelve [#371](https://github.com/D4Vinci/Scrapling/issues/371))

  ```bash
  scrapling extract fetch "https://example.com" page.html --executable-path "/path/to/chromium"
  ```

### 🤖 Mejoras de uso {#v0.4.11-quality-of-life-changes}
- **`find_by_text` y `find_by_regex` ahora son hasta unas 2 veces más rápidos** cuando `first_match` está activado (valor predeterminado), porque los elementos se convierten en objetos solo cuando hace falta y la búsqueda se detiene en la primera coincidencia, por @yetval en [#370](https://github.com/D4Vinci/Scrapling/pull/370)
- **Actualizadas las pruebas de rendimiento con las cifras nuevas frente a las últimas versiones de todas las bibliotecas.**
- **Actualizadas las reglas de contribución**

### 🐛 Correcciones de errores {#v0.4.11-bug-fixes}

- **Corregidos los fallos de las herramientas de obtención del servidor MCP en páginas con caracteres de control**, que daban el error `All strings must be XML compatible`, por @yetval en [#368](https://github.com/D4Vinci/Scrapling/pull/368) (corrige [#366](https://github.com/D4Vinci/Scrapling/issues/366))

## [v0.4.10](https://github.com/D4Vinci/Scrapling/releases/tag/v0.4.10) - 2026-07-04 {#v0.4.10}

**Una nueva actualización con una integración con Scrapy y varias correcciones de la comunidad 🎉**

### 🚀 Novedades y mejoras de uso {#v0.4.10-new-stuff-and-quality-of-life-changes}

- **Añadida una integración con Scrapy** para usar la API de análisis de Scrapling en tus proyectos Scrapy actuales sin reescribirlos. Aplica el decorador `scrapling_response` a cualquier callback de un spider y la respuesta que recibe se convierte en una `Response` de Scrapling, mientras Scrapy sigue gestionando el rastreo (consulta la [documentación](integrations/scrapy.md)):

    ```python
    import scrapy
    from scrapling.integrations.scrapy import scrapling_response

    class QuotesSpider(scrapy.Spider):
        name = "quotes"
        start_urls = ["https://quotes.toscrape.com"]

        @scrapling_response
        def parse(self, response):  # `response` is now a Scrapling Response
            first_quote = response.find_by_text("The world as we have created it", partial=True)
            for quote in [first_quote, *first_quote.find_similar()]:
                yield {"text": quote.get_all_text(strip=True)}
    ```

- **El servidor MCP ahora puede usar un navegador personalizado compatible con Chromium** para todas las herramientas basadas en navegador. Defínelo una vez con `scrapling mcp --executable-path "/path/to/chromium"` o con la variable de entorno `SCRAPLING_EXECUTABLE_PATH`, o por solicitud con el argumento `executable_path`, por @samrusani en [#360](https://github.com/D4Vinci/Scrapling/pull/360) (resuelve [#347](https://github.com/D4Vinci/Scrapling/issues/347))
- **Actualizados todos los navegadores y las huellas**. Ejecuta `scrapling install --force` después de actualizar para renovarlos.

### 🐛 Correcciones de errores {#v0.4.10-bug-fixes}

- **Corregido el texto ilegible (mojibake) de los fetchers de navegador en sitios que no usan UTF-8**, por @yehudalevy-collab en [#365](https://github.com/D4Vinci/Scrapling/pull/365) (corrige [#364](https://github.com/D4Vinci/Scrapling/issues/364)).
- **Corregido el problema por el que `LinkExtractor` no filtraba extensiones de archivo compuestas como `.tar.gz`**, por @renbkna en [#359](https://github.com/D4Vinci/Scrapling/pull/359) (corrige [#349](https://github.com/D4Vinci/Scrapling/issues/349)).
- **Corregida la pérdida de solicitudes en curso en los puntos de guardado de rastreos pausados, para que ya no se omitan al reanudar**, por @yetval en [#358](https://github.com/D4Vinci/Scrapling/pull/358).
- **Corregido el cálculo incorrecto de las esperas de rastreo a partir de las directivas `Request-rate` de robots.txt** mediante la actualización de Protego, con pruebas ajustadas por @Disaster-Terminator en [#355](https://github.com/D4Vinci/Scrapling/pull/355).

### Documentación {#v0.4.10-docs}

- **Aclarada la interacción de `init_script` con el contexto de ejecución aislado de Patchright en modo sigiloso**, por @mturac en [#353](https://github.com/D4Vinci/Scrapling/pull/353) (resuelve [#350](https://github.com/D4Vinci/Scrapling/issues/350)).
- **Añadido el método de instalación de la habilidad para agentes mediante [skills.sh](https://skills.sh/D4Vinci/Scrapling)**, por @ob-aion en [#363](https://github.com/D4Vinci/Scrapling/pull/363).

## [v0.4.9](https://github.com/D4Vinci/Scrapling/releases/tag/v0.4.9) - 2026-06-07 {#v0.4.9}

**Una actualización de mantenimiento llena de correcciones de problemas que comunicó la comunidad 🛠️**

### 🚀 Novedades y mejoras de uso {#v0.4.9-new-stuff-and-quality-of-life-changes}

- **Actualizados todos los navegadores y las huellas**. Ejecuta `scrapling install --force` después de actualizar para renovarlos.
- **Añadida la opción `--version` a la CLI**, por @ETM-Code en [#303](https://github.com/D4Vinci/Scrapling/pull/303) (resuelve [#299](https://github.com/D4Vinci/Scrapling/issues/299))

### 🐛 Correcciones de errores {#v0.4.9-bug-fixes}

- **Corregido el problema por el que el argumento `proxy` de la sesión se ignoraba sin avisar en las sesiones HTTP**, lo que podía revelar tu IP real (resuelve [#295](https://github.com/D4Vinci/Scrapling/issues/295)). Ten en cuenta que combinar un `proxy` de sesión con un argumento `proxies` por solicitud (o al revés) ahora genera un error en lugar de ignorar uno de ellos sin avisar.
- **Corregidos los fallos de navegación al combinar `init_script` con `user_data_dir`** (resuelve [#294](https://github.com/D4Vinci/Scrapling/issues/294)).
- **Corregida la detección de codificación cuando los sitios ponen entre comillas el valor charset de la cabecera `Content-Type`**, por @Bortlesboat en [#323](https://github.com/D4Vinci/Scrapling/pull/323).
- **Corregido un `IndexError` en la reubicación adaptativa de elementos cuando `auto_save` está activado**, por @Mubashirrrr en [#340](https://github.com/D4Vinci/Scrapling/pull/340).
- **Corregidos los fallos al guardar los puntos de guardado y la caché de los spiders en Windows**, por @MrStarkEG en [#344](https://github.com/D4Vinci/Scrapling/pull/344).
- **Corregido el cálculo de similitud de `find_similar` para elementos con distinto número de atributos** (resuelve [#322](https://github.com/D4Vinci/Scrapling/issues/322)).

### Documentación {#v0.4.9-docs}

- **Aclarado que la instalación predeterminada solo incluye el motor de análisis**, y que los fetchers y los spiders necesitan los extras (resuelve [#343](https://github.com/D4Vinci/Scrapling/issues/343)).
- **Corregido el nombre de la imagen Docker en los ejemplos restantes**, por @evanclan en [#315](https://github.com/D4Vinci/Scrapling/pull/315).
- **Corregido un enlace roto en la guía de contribución**, por @Bortlesboat en [#320](https://github.com/D4Vinci/Scrapling/pull/320).

## [v0.4.8](https://github.com/D4Vinci/Scrapling/releases/tag/v0.4.8) - 2026-05-11 {#v0.4.8}

**Una gran actualización de spiders que mejora el sistema de rastreo 🕷️**

### 🚀 Novedades y mejoras de uso {#v0.4.8-new-stuff-and-quality-of-life-changes}

- **Añadida la herramienta `LinkExtractor`** en `scrapling.spiders.LinkExtractor` para extraer URL de una `Response`. Tiene muchos controles (consulta la [documentación](spiders/generic-templates.md))

    ```python
    from scrapling.spiders import LinkExtractor

    extractor = LinkExtractor(allow=r"/posts/", deny_domains=["ads.example.com"])
    ```

- **Añadidas las plantillas de spider genéricas `CrawlSpider` y `CrawlRule`** para que ya no tengas que escribir una y otra vez el mismo código para "seguir enlaces que coincidan con este patrón". Redefine `rules()` para devolver una lista de objetos `CrawlRule`, cada uno asociado a un `LinkExtractor`. (Consulta la [documentación](spiders/generic-templates.md))

    ```python
    from scrapling.spiders import CrawlSpider, CrawlRule, LinkExtractor

    class QuotesSpider(CrawlSpider):
        name = "blog"
        start_urls = ["https://quotes.toscrape.com/"]

        def rules(self):
            return [
                CrawlRule(LinkExtractor(allow=r"/author/"), callback=self.parse_author),
                CrawlRule(LinkExtractor(allow=r"/page/\d+/")),  # pagination, no callback
            ]

        async def parse_author(self, response):
            yield {
                "name": response.css(".author-title::text").get(),
                "birthday": response.css(".author-born-date::text").get(),
                "url": response.url,
            }
    ```

- **Añadida una plantilla `SitemapSpider`** que inicia un rastreo directamente desde un mapa del sitio o URL de `robots.txt`. Admite mapas del sitio comprimidos con gzip y muchos controles y opciones. Las URL se distribuyen mediante las reglas de rastreo, como en el ejemplo de **CrawlSpider** anterior. (Consulta la [documentación](spiders/generic-templates.md))

    ```python
    from scrapling.spiders import SitemapSpider, CrawlRule, LinkExtractor

    class NewsSitemap(SitemapSpider):
        name = "news"
        sitemap_urls = ["https://example.com/robots.txt"]

        def rules(self):
            return [
                CrawlRule(LinkExtractor(allow=r"/articles/"), callback=self.parse_article),
            ]

        async def parse_article(self, response):
            yield {"url": response.url, "title": response.css("h1::text").get()}
    ```

- **La reubicación adaptativa ahora usa un umbral de similitud del 40% de forma predeterminada**, en lugar de `0`, en todos los métodos. Esto mejora el funcionamiento de la función adaptativa. Cuando ningún elemento supera el umbral, una advertencia muestra la puntuación más alta encontrada, para que puedas reducir `percentage` de forma consciente si hace falta.

- **Actualizados todos los navegadores y las huellas**. Vuelve a ejecutar `scrapling install  --force` después de actualizar para renovar los navegadores y las huellas.

### 🐛 Correcciones de errores {#v0.4.8-bug-fixes}

- **Corregido el problema por el que `Fetcher.configure(...)` no se aplicaba a las llamadas por solicitud**. La misma corrección se aplicó a `AsyncFetcher`.
- **Corregido el cálculo incorrecto de huellas de solicitudes que causaba solicitudes duplicadas en los spiders**, por @yetval en [#255](https://github.com/D4Vinci/Scrapling/pull/255).
- **Corregido el silencio del motor de extracción adaptativa ante coincidencias débiles.** Junto con el cambio de umbral anterior, ahora recibes una advertencia en lugar de un elemento engañoso como "mejor aproximación" cuando falla la reubicación.

### Documentación {#v0.4.8-docs}

- **Actualizados los ejemplos de código antiguos** de la documentación para que coincidan con la versión actual.
- **Mejorada la experiencia al copiar y pegar código** en el sitio de documentación y acortada la habilidad para agentes para que use menos tokens en cada invocación.

## [v0.4.7](https://github.com/D4Vinci/Scrapling/releases/tag/v0.4.7) - 2026-04-17 {#v0.4.7}

**Una actualización centrada en dar visión a tus agentes de IA 📸**

### 🚀 Novedades y mejoras de uso {#v0.4.7-new-stuff-and-quality-of-life-changes}

- **Añadida una herramienta MCP `screenshot`** que captura una página y la devuelve como un bloque MCP real de tipo `ImageContent`, para que el modelo pueda verla. La herramienta exige una sesión de navegador abierta: primero llama a `open_session` (con `dynamic` o `stealthy`) y pasa aquí el `session_id`. Admite PNG y JPEG, capturas de página completa, calidad JPEG y los controles de espera habituales (`wait`, `wait_selector`, `network_idle`, `timeout`). (Implementa [#244](https://github.com/D4Vinci/Scrapling/issues/244))
- **Añadido un parámetro `session_id` personalizado a `open_session`** para dar a las sesiones nombres útiles (`"search"`, `"checkout"`) en lugar del valor hexadecimal aleatorio de 12 caracteres que se usa por defecto. Por @hauntedhost en [#243](https://github.com/D4Vinci/Scrapling/pull/243)

### 🐛 Correcciones de errores {#v0.4.7-bug-fixes}

- **Corregida la corrupción del estado de `FetcherSession` y un fallo al cerrar una sesión de inicio diferido**. Por @yetval en [#245](https://github.com/D4Vinci/Scrapling/pull/245)
- **Corregido `TypeError: Session.request() got an unexpected keyword argument 'block_ads'`** al usar la opción `--ai-targeted` de la CLI con comandos HTTP. Por @voidborne-d en [#249](https://github.com/D4Vinci/Scrapling/pull/249) (corrige [#247](https://github.com/D4Vinci/Scrapling/issues/247))

### Traducciones {#v0.4.7-translations}

- **Añadida una traducción del README al portugués de Brasil**, por @rgomids en [#250](https://github.com/D4Vinci/Scrapling/pull/250)

## [v0.4.6](https://github.com/D4Vinci/Scrapling/releases/tag/v0.4.6) - 2026-04-13 {#v0.4.6}

**Una actualización centrada en el sigilo del navegador, la privacidad y la experiencia de desarrollo 🔒**

### 🚀 Novedades y mejoras de uso {#v0.4.6-new-stuff-and-quality-of-life-changes}

- **Añadido el bloqueo de anuncios integrado** para los fetchers de navegador. Pasa `block_ads=True` para bloquear solicitudes a unos 3500 dominios conocidos de anuncios y rastreadores al interceptar la ruta: sin DNS, sin TCP y con cancelación inmediata. Puedes combinarlo con `blocked_domains` para usar listas propias. El servidor MCP y el modo `--ai-targeted` de la CLI lo activan automáticamente para ahorrar tokens y acelerar la carga de las páginas.

    ```python
    page = StealthyFetcher.fetch('https://example.com', block_ads=True)
    ```

- **Añadido soporte para DNS-over-HTTPS** para evitar fugas de DNS al usar proxies. Pasa `dns_over_https=True` para dirigir las consultas DNS al servicio DoH de Cloudflare, de modo que la resolución DNS no revele tu ubicación real aunque el tráfico HTTP pase por un proxy.

    ```python
    page = StealthyFetcher.fetch('https://example.com', proxy='http://proxy:8080', dns_over_https=True)
    ```

- **Añadido el callback `page_setup`** para los fetchers de navegador. Es una función que se ejecuta antes de `page.goto()` y permite registrar detectores de eventos, rutas o scripts que deben prepararse antes de navegar. Se combina con `page_action` (que se ejecuta después de navegar). (Resuelve [#237](https://github.com/D4Vinci/Scrapling/issues/237))

    ```python
    def capture_websockets(page):
        page.on("websocket", lambda ws: print(f"WS: {ws.url}"))

    page = DynamicFetcher.fetch('https://example.com', page_setup=capture_websockets)
    ```

- **Añadidas las opciones de CLI `--block-ads` y `--dns-over-https`** a los comandos `fetch` y `stealthy-fetch`.

### 🐛 Correcciones de errores {#v0.4.6-bug-fixes}

- **Corregido el alias de tipo `Seconds`**, que rechazaba valores decimales. Pasar `wait=1.5` o `timeout=500.0` a los fetchers de navegador fallaba con un error de tipo porque el alias trataba `float` como metadatos en lugar de como un tipo. Por @kuishou68 en [#240](https://github.com/D4Vinci/Scrapling/pull/240)
- **Corregidos los segmentos ID duplicados al generar selectores con la ruta completa**. El selector de los elementos con atributos `id` se añadía dos veces al generar rutas CSS/XPath completas y producía selectores como `body > #main > #main > #target > #target`. También se corrigió la generación de condiciones `[@id='x']` sueltas (XPath no válido) en lugar de `*[@id='x']` en rutas XPath completas. Por @sjhddh en [#241](https://github.com/D4Vinci/Scrapling/pull/241)
- **Corregidos los parámetros que faltaban en las firmas del shell**. En las firmas de las funciones del shell interactivo faltaban `blocked_domains`, `block_ads`, `retries`, `retry_delay`, `capture_xhr`, `executable_path` y `dns_over_https`.

## [v0.4.5](https://github.com/D4Vinci/Scrapling/releases/tag/v0.4.5) - 2026-04-07 {#v0.4.5}

**Una actualización con una gran mejora de uso para quienes desarrollan spiders y un par de correcciones importantes 🎉**

### 🚀 Novedades y mejoras de uso {#v0.4.5-new-stuff-and-quality-of-life-changes}

- **Modo de desarrollo de spiders**: probar cambios en la lógica de `parse()` de un spider antes exigía volver a consultar los servidores del sitio en cada ejecución. Esto es lento, genera tráfico y puede hacer que limiten tus solicitudes mientras todavía ajustas los selectores. El nuevo modo de desarrollo guarda cada respuesta en disco en la primera ejecución y la reutiliza desde el disco en las siguientes. Así puedes ajustar los callbacks y ejecutar tantas veces como quieras sin hacer ninguna solicitud de red. Actívalo con un atributo de clase:

    ```python
    class MySpider(Spider):
        name = "my_spider"
        start_urls = ["https://example.com"]
        development_mode = True

        async def parse(self, response):
            yield {"title": response.css("title::text").get("")}
    ```

    La caché se guarda en `.scrapling_cache/{spider.name}/` de forma predeterminada, y puedes cambiar su ubicación con `development_cache_dir`. Dos contadores nuevos, `cache_hits` y `cache_misses`, muestran cómo ha funcionado la caché. Al reutilizarla, se omiten `download_delay`, los límites de solicitudes y la ruta de reintentos de solicitudes bloqueadas, para que las pruebas sean tan rápidas como permita el disco. No publiques un spider con `development_mode = True`: es una herramienta de desarrollo, no una caché para producción. Consulta la [documentación](spiders/advanced.md#development-mode) para ver todos los detalles.

- **Redirecciones más seguras de forma predeterminada**: el valor predeterminado de `follow_redirects` ahora es `"safe"` en todos los fetchers HTTP, el servidor MCP y el shell. Las redirecciones se siguen, pero se rechazan las que apuntan a IP internas o privadas (loopback, redes privadas y link-local). Esto te protege frente a SSRF al extraer datos de URL que aportan los usuarios. Pasa `follow_redirects="all"` para recuperar el comportamiento anterior, o `False` para desactivar las redirecciones por completo.

### 🐛 Correcciones de errores {#v0.4.5-bug-fixes}

- **La detención forzada ya no pierde tu punto de guardado**: pulsar Ctrl+C dos veces (detención forzada) en un spider con `crawldir` activado antes podía coincidir con la escritura del punto de guardado. El ámbito de cancelación terminaba la tarea antes de completar el pickle, dejaba `paused=False` y activaba la limpieza que *elimina* el punto de guardado anterior. Así, detener por la fuerza un rastreo largo podía perder todo el progreso que intentabas guardar. El motor ahora escribe el punto de guardado **antes** de llamar a `cancel_scope.cancel()`, de modo que una detención forzada siempre conserva el último estado pendiente. Por @voidborne-d en [#230](https://github.com/D4Vinci/Scrapling/pull/230).

## [v0.4.4](https://github.com/D4Vinci/Scrapling/releases/tag/v0.4.4) - 2026-04-05 {#v0.4.4}

**Una nueva actualización con mejoras importantes en los spiders y correcciones de errores 🎉**

### 🚀 Novedades y mejoras de uso {#v0.4.4-new-stuff-and-quality-of-life-changes}
- **Añadido el cumplimiento de robots.txt al sistema de spiders** con la nueva opción `robots_txt_obey`. Al activarla, el spider obtiene y respeta automáticamente las reglas de robots.txt antes de rastrear, incluidas las directivas `Disallow`, `Crawl-delay` y `Request-rate`. Los archivos robots.txt se obtienen de forma concurrente y se guardan en caché por dominio durante todo el rastreo. Por @AbdullahY36 en [#226](https://github.com/D4Vinci/Scrapling/pull/226)
- **Añadida la preparación previa de la caché de robots.txt**, para obtener y analizar los archivos robots.txt de todos los dominios de start_urls antes de iniciar el bucle de rastreo. Así se evitan esperas en la primera solicitud a cada dominio.
- **Añadida la nueva estadística `robots_disallowed_count`** a `CrawlStats` para contar cuántas solicitudes bloquearon las reglas de robots.txt durante el rastreo.

Puedes verlo en el sitio desde [aquí](spiders/getting-started.md#robotstxt-compliance)

### 🐛 Correcciones de errores {#v0.4.4-bug-fixes}
- **Corregido un problema importante de MRO con `ProxyRotator`**, en el que el método provisional `_build_context_with_proxy` ocultaba la implementación real de las clases hijas y hacía que la rotación de proxies siempre lanzara `NotImplementedError` (corrige [#215](https://github.com/D4Vinci/Scrapling/issues/215)). Gracias, @yetval
- **Corregida una fuga en el grupo de páginas** al usar rotación de proxies por solicitud en sesiones de navegador. Las páginas creadas en contextos temporales no se eliminaban del grupo al limpiar, por lo que se acumulaban referencias obsoletas con el tiempo. Por @yetval en [#223](https://github.com/D4Vinci/Scrapling/pull/223)
- **Corregida una comprobación de tipo que faltaba** en el fetcher estático: `curl_cffi` podía devolver `None` desde `session.request()` y causar errores más adelante.

### Otros cambios {#v0.4.4-other}
- Actualizadas las dependencias para incluir las últimas huellas y otras novedades.
- Añadido `protego` como nueva dependencia del grupo opcional `fetchers` para analizar robots.txt.

## [v0.4.3](https://github.com/D4Vinci/Scrapling/releases/tag/v0.4.3) - 2026-03-30 {#v0.4.3}

**Una nueva actualización con muchos cambios importantes 🎉**

### 🚀 Novedades y mejoras de uso {#v0.4.3-new-stuff-and-quality-of-life-changes}
- **Añadida una nueva herramienta MCP** para abrir un navegador normal o sigiloso persistente y seguir usándolo con las demás herramientas, y otra nueva herramienta para cerrarlo. ([Ejemplos](https://github.com/D4Vinci/Scrapling/blob/v0.4.3/docs/ai/mcp-server.md#examples))
- **Añadida una nueva herramienta MCP** para listar todas las sesiones de navegador existentes, pensada para usarse con las herramientas nuevas.
- **Añadida una nueva opción a las sesiones de navegador** para recoger automáticamente todas las solicitudes en segundo plano que ocurren durante una solicitud (resuelve [#159](https://github.com/D4Vinci/Scrapling/pull/159)) [[Ejemplos](https://github.com/D4Vinci/Scrapling/blob/v0.4.3/docs/fetching/dynamic.md#capturing-xhrfetch-requests)].
- **Añadido un nuevo limpiador** para proteger el servidor MCP de ataques comunes de inyección de prompts eliminando el contenido oculto o invisible.
- **Añadida una nueva opción de línea de comandos**, llamada `--ai-targeted`, a los comandos de extracción web para preparar el contenido para la IA y protegerlo frente a ataques comunes de inyección de prompts, como hace el servidor MCP.
- **Añadida una nueva opción a las sesiones de navegador**, llamada `executable_path`, para definir una ruta de navegador personalizada (resuelve [#202](https://github.com/D4Vinci/Scrapling/pull/202))
- **Reorganizado** el código del servidor MCP para facilitar su mantenimiento, y unificadas todas las herramientas para que sean asíncronas.
- **Reorganizado** el código de los comandos de la CLI para facilitar su mantenimiento y reducirlo en 210 líneas.

### 🐛 Correcciones de errores {#v0.4.3-bug-fixes}
- Corregido un error para conservar el método HTTP entre reintentos en la sesión del spider, por @karesansui-u en [#201](https://github.com/D4Vinci/Scrapling/pull/201)
- Añadido un límite máximo de reintentos al obtener el contenido de la página para evitar un bucle infinito, por @haosenwang1018 y @D4Vinci en [#197](https://github.com/D4Vinci/Scrapling/pull/197)
- Sustituido el `raise` sin argumento por `return False` en `_restore_from_checkpoint`, por @haosenwang1018 en [#196](https://github.com/D4Vinci/Scrapling/pull/196)
- Sustituido `get_all` por `getall` en `Texthandler` para coincidir con la clase Selector.

### Mejoras de las pruebas y su cobertura {#v0.4.3-coverage-tests-improvement}
- Añadidas pruebas de casos límite de `_normalize_credentials`, por @Bortlesboat en [#192](https://github.com/D4Vinci/Scrapling/pull/192)
- Añadidas pruebas del ciclo de guardado y recuperación y del almacenamiento principal, por @haosenwang1018 en [#193](https://github.com/D4Vinci/Scrapling/pull/193)
- Añadida cobertura de las rutas de regex de `TextHandler` y de `TextHandlers.re()`, por @haosenwang1018 en [#194](https://github.com/D4Vinci/Scrapling/pull/194)
- Añadidas pruebas de casos límite de `filter`, `iterancestors` y `find_similar`, por @awanawana en [#200](https://github.com/D4Vinci/Scrapling/pull/200)

### Mejoras de la habilidad para agentes {#v0.4.3-agent-skill-improvement}
- Corregidos enlaces Markdown rotos en las referencias de la habilidad, por @yetval en [#204](https://github.com/D4Vinci/Scrapling/pull/204)
- Mejorada la estructura de la habilidad para superar mejor la validación de [Clawhub](https://clawhub.ai/d4vinci/scrapling-official).
- La habilidad ahora exige usar la opción de línea de comandos `--ai-targeted` al extraer datos mediante comandos.

### Mejoras de la documentación {#v0.4.3-docs-improvement}
- Añadida una traducción del README al coreano, por @greatsk55 en [#187](https://github.com/D4Vinci/Scrapling/pull/187)
- Corregidos los espacios entre caracteres CJK y latinos en los README chino y japonés.
- Corregidos enlaces rotos del diseño anterior del sitio.

## [v0.4.2](https://github.com/D4Vinci/Scrapling/releases/tag/v0.4.2) - 2026-03-08 {#v0.4.2}

**Una nueva actualización de mantenimiento con cambios importantes**

#### Correcciones de errores {#v0.4.2-bug-fixes}
- La función `get_all_text()` ahora recoge también los nodos de texto que siguen a los elementos. Así, el servidor MCP y los comandos pueden leer texto que antes se perdía ([#168](https://github.com/D4Vinci/Scrapling/pull/168)). Gracias, @mhillebrand
- Referer ahora devuelve la URL base de Google en lugar de una URL de búsqueda de Google. La lógica anterior era incorrecta y podía generar una señal que facilitara detectar la huella del navegador ([#179](https://github.com/D4Vinci/Scrapling/pull/179)). Gracias, @Bortlesboat
- Se corrigió un problema al unir las opciones de inicio adicionales en todos los navegadores. Gracias, @rostchri
- Se corrigió un problema con las anotaciones de tipos que causaba fallos en versiones de Python anteriores a 3.12. (Resuelve [#163](https://github.com/D4Vinci/Scrapling/issues/163))

#### Otros cambios {#v0.4.2-other}
- Se añadió una habilidad para agentes para Claude Code / OpenClaw y otras herramientas de agentes de IA.
- Se añadió la habilidad para agentes a Clawhub.
- Se actualizaron todos los navegadores y Playwright a sus últimas versiones.
- Se añadió una traducción al francés del archivo README principal.

## [v0.4.1](https://github.com/D4Vinci/Scrapling/releases/tag/v0.4.1) - 2026-02-27 {#v0.4.1}

**Una nueva actualización con muchos cambios importantes**

### 🚀 Novedades y mejoras de uso {#v0.4.1-new-stuff-and-quality-of-life-changes}
- **Mayor precisión de las expresiones regulares** para detectar desafíos de Cloudflare (Gracias a @Rinz27 [#133](https://github.com/D4Vinci/Scrapling/pull/133))
- **Mayor velocidad y eficiencia** al resolver desafíos de Cloudflare. Ahora es casi el doble de rápido.
- **Mejoras al resolver desafíos de Cloudflare** para los casos en que un sitio muestra la página de Cloudflare dos veces antes de redirigir al sitio principal.
- **Mejoras en el modo de sigilo y la velocidad del navegador sigiloso** al eliminar los archivos JS inyectados.
- **Mejoras en el esquema MCP** para que OpenCode lo acepte (Gracias a @robin-ede [#137](https://github.com/D4Vinci/Scrapling/pull/137))
- **Mayor compatibilidad del esquema MCP con el protocolo** para que VS Code Copilot y otras herramientas estrictas lo acepten. (Resuelve #150 )
- **Gran reducción del consumo de tokens del servidor MCP** al eliminar etiquetas HTML innecesarias cuando la opción `main_content_only` está activada.
- Se corrigió la página de PyPI y se añadieron los archivos necesarios para registrar el servidor MCP en el registro de servidores MCP.
- Se añadió un ejemplo de código que muestra cómo instalar las dependencias de los navegadores desde código, en lugar de usar la línea de comandos, para facilitar la automatización.
- Se mejoraron todos los workflows usando las últimas versiones de las acciones (Gracias a @salmanmkc [#143](https://github.com/D4Vinci/Scrapling/pull/143)/[#144](https://github.com/D4Vinci/Scrapling/pull/144))

## [v0.4](https://github.com/D4Vinci/Scrapling/releases/tag/v0.4) - 2026-02-15 {#v0.4}

**La mayor versión de Scrapling hasta la fecha: framework de spiders, rotación de proxies y grandes mejoras en el analizador**

Esta versión incorpora un framework de spiders y rastreo totalmente asíncrono, gestión inteligente de proxies y cambios importantes en la API que hacen Scrapling más potente y coherente. Lee con atención la sección de cambios incompatibles antes de actualizar.

### 🕷️ Framework de spiders {#v0.4-spider-framework}

Un nuevo framework de rastreo asíncrono basado en `anyio` para extraer datos de forma organizada y a gran escala:

```python
from scrapling.spiders import Spider, Response

class MySpider(Spider):
  name = "demo"
  start_urls = ["https://example.com/"]

  async def parse(self, response: Response):
      for item in response.css('.product'):
          yield {"title": item.css('h2::text').get()}

MySpider().start()
```

-  **API de spiders similar a Scrapy**: Define spiders con `start_urls`, callbacks `parse` asíncronos, objetos `Request`/`Response` y una cola de prioridad.
- **Rastreo concurrente**: Límites de concurrencia, control de la frecuencia por dominio y pausas entre descargas configurables.
- **Compatibilidad con varias sesiones**: Una interfaz común para peticiones HTTP y navegadores sigilosos sin interfaz gráfica en un solo spider. Dirige las peticiones a distintas sesiones mediante su ID. Permite iniciar las sesiones solo cuando se necesitan.
- **Pausar y reanudar**: Guarda el estado del rastreo mediante puntos de guardado. Pulsa Ctrl+C para cerrar de forma ordenada y vuelve a iniciar para continuar donde lo dejaste.
- **Modo streaming**: Recibe los datos extraídos en cuanto llegan mediante `async for item in spider.stream()`, con estadísticas en tiempo real. Ideal para interfaces, pipelines y rastreos largos.
- **Detección de peticiones bloqueadas**: Detecta y reintenta las peticiones bloqueadas de forma automática, con lógica personalizable.
- **Exportación integrada**: Exporta los resultados mediante hooks y tu propio pipeline, o usa la exportación integrada a JSON/JSONL con `result.items.to_json()` / `result.items.to_jsonl()`, respectivamente.
- **Hooks del ciclo de vida**: `on_start()`, `on_close()`, `on_error()`, `on_scraped_item()` y otros hooks para controlar todo el ciclo de vida del rastreo.
- **Estadísticas detalladas del rastreo**: Registra peticiones, respuestas, bytes, códigos de estado, proxies, detalles por dominio y sesión, recuentos por nivel de log y más.
- **Compatibilidad con uvloop**: Pasa `use_uvloop=True` a `spider.start()` para acelerar la ejecución asíncrona cuando esté disponible.

Se ha añadido una nueva sección al sitio web con todos los detalles. Haz clic [aquí](spiders/architecture.md)

### 🔄 Rotación de proxies {#v0.4-proxy-rotation}

* Nueva clase `ProxyRotator` con rotación segura entre hilos. Funciona con todos los fetchers y sesiones:

  ```python
  from scrapling import ProxyRotator
  rotator = ProxyRotator(["http://proxy1:8080", "http://proxy2:8080"])
  Fetcher.get(url, proxy_rotator=rotator)
  ```

* **Estrategias de rotación personalizadas**: Crea tu propia lógica de rotación de proxies
* **Cambio de proxy por petición**: Pasa `proxy=` a cualquier llamada individual a `get()`/`post()`/`fetch()` para reemplazar el proxy de la sesión en esa petición.

### 🌐 Mejoras en los fetchers de navegador {#v0.4-browser-fetcher-improvements}

* **Bloqueo de dominios**: Nuevo parámetro `blocked_domains` en `DynamicFetcher`/`StealthyFetcher` para bloquear peticiones a dominios concretos. Los subdominios se incluyen automáticamente.
* **Reintentos automáticos**: Los fetchers de navegador ahora reintentan las peticiones que fallan mediante los parámetros `retries` (valor predeterminado: 3) y `retry_delay` (valor predeterminado: 1s). Incluye detección de errores relacionados con proxies.
* **Metadatos de la respuesta**: El diccionario `Response.meta` guarda automáticamente el proxy usado e incorpora los metadatos de la petición.
* **Response.follow()**: Crea objetos `Request` para peticiones posteriores con gestión automática del referer, diseñados para el sistema de spiders.
* **Sin reproducción automática**: Las sesiones de navegador ahora bloquean el contenido con reproducción automática, que antes causaba problemas.
* **Velocidad**: Mejoras en el sigilo y la velocidad al ajustar las opciones de inicio del navegador.

### 🔧 Correcciones de errores y mejoras {#v0.4-bug-fixes-improvements}
- **Optimización del analizador**: Se optimizó el analizador para operaciones repetidas, mejorando su rendimiento.
- **Páginas con errores**: Se corrigió un error que impedía cerrar el navegador cuando las páginas daban errores.
- **Cuerpo vacío**: Se gestionan las respuestas con el cuerpo vacío.
- **Bucle de Playwright**: Se resolvió un problema que dejaba abierto el bucle de Playwright cuando fallaba la conexión CDP
- **Seguridad de tipos**: Se corrigieron todos los errores de mypy y se añadieron anotaciones de tipos en los cuerpos de funciones que no las tenían. Se añadieron mypy y pyright al workflow de CI.

### ⚠️ Cambios incompatibles {#v0.4-breaking-changes}

* **Se eliminaron `css_first`/`xpath_first`**: Usa `css('.selector').first`, `css('.selector')[0]` o `css('.selector').get()` en su lugar.
* **Todas las selecciones devuelven ahora `Selectors`**: `css('::text')`, `xpath('//text()')`, `css('::attr(href)')` y `xpath('//@href')` ahora devuelven `Selectors`, que envuelve los nodos de texto en objetos `Selector` con `tag="#text"`, en lugar de `TextHandlers`. Esto hace que la API sea coherente entre los métodos de selección y las anotaciones de tipos.
* **`Response.body` siempre es `bytes`**: Antes podía ser `str` o `bytes`; ahora siempre devuelve `bytes`.
* **Comportamiento de `get()`/`getall()`**: En `Selector`, `get()` devuelve `TextHandler` (HTML serializado o un valor de texto) y `getall()` devuelve `TextHandlers`. Alias: `extract_first = get`, `extract = getall`. Se eliminó el antiguo `get_all()` de `Selectors`.
* **`Selectors.first`/`.last`**: Propiedades de acceso seguras que devuelven `Selector | None` en lugar de lanzar `IndexError`.
* **Nuevos nombres para las constantes internas**: `DEFAULT_FLAGS` → `DEFAULT_ARGS`, `DEFAULT_STEALTH_FLAGS` → `STEALTH_ARGS`, `HARMFUL_DEFAULT_ARGS` → `HARMFUL_ARGS`, `DEFAULT_DISABLED_RESOURCES` → `EXTRA_RESOURCES`.

### 🔨 Otros cambios {#v0.4-other-changes}

* **Cambios en las dependencias**: Se reemplazó `tldextract` por `tld`, se eliminó el archivo interno `_html_utils.py` para usar `w3lib.html.replace_entities` y se añadió `typing_extensions` como requisito obligatorio.
* **Renovación de la documentación**: Migración completa de MkDocs a Zensical, nueva sección sobre spiders, actualización de todas las páginas existentes y nuevas referencias de la API.

## [v0.3.14](https://github.com/D4Vinci/Scrapling/releases/tag/v0.3.14) - 2026-01-03 {#v0.3.14}

**Una pequeña actualización de mantenimiento para corregir problemas que aparecieron en algunos equipos con v0.3.13**

- Se desactivó el modo incógnito en `StealthyFetcher` y sus clases de sesión, porque impedía conservar las cookies entre páginas en equipos Windows. Esto no ocurría en MacOS ni Linux (Corrige [#123](https://github.com/D4Vinci/Scrapling/issues/123); gracias a @frugality4121 por avisar y a @gembleman por señalar la solución).
- Se fijó la última versión de browserforge para resolver el problema con los modelos de cabeceras antiguos en instalaciones que ya tenían una versión antigua de browserforge.

## [v0.3.13](https://github.com/D4Vinci/Scrapling/releases/tag/v0.3.13) - 2026-01-01 {#v0.3.13}

**Una gran actualización con mejoras en muchas partes, pero también con numerosos cambios incompatibles por buenas razones. Lee lo siguiente antes de actualizar**

* Por varios motivos, hemos decidido dejar de usar Camoufox por completo a partir de ahora. Puede que volvamos a usarlo en el futuro si su desarrollo continúa. Si prefieres seguir usando Camoufox como antes de esta versión, encontrarás instrucciones en esta [sección](https://github.com/D4Vinci/Scrapling/blob/v0.3.13/docs/fetching/stealthy.md#using-camoufox-as-an-engine).

* Antes usábamos patchright en el modo de sigilo de `DynamicFetcher` y sus clases de sesión. Ahora hemos eliminado ese modo de estas clases y hemos empezado a usar patchright en `StealthyFetcher` y sus clases de sesión, con MUCHAS mejoras, como verás, que aumentan el sigilo sobre lo que ya ofrece patchright.

**Esto hace que `StealthyFetcher` y sus clases de sesión sean un 101% más rápidos, usen menos memoria y espacio y tengan unas ~400 líneas de código menos. Pero, sobre todo, son más estables que cuando usábamos Camoufox.**

Esto también reduce el tiempo de instalación del comando `scrapling install` y el tamaño de la imagen Docker, mejora la ejecución de las pruebas en el CI de GitHub y hace que scrapling resulte menos confuso para los nuevos usuarios.

### Cambios incompatibles {#v0.3.13-breaking-changes}
1. Se eliminó el argumento `stealth` de `DynamicFetcher` y su clase de sesión, mientras que el argumento `hide_canvas` pasó a `StealthyFetcher` y sus clases de sesión.
2.  El argumento `disable_webgl` pasó de `DynamicFetcher` a la clase `StealthyFetcher` y se renombró como `allow_webgl`. Lo mismo ocurre en todas las clases de sesión.
3. La clase `StealthyFetcher` es ahora, en esencia, la nueva versión sigilosa de `DynamicFetcher`, así que se eliminaron los argumentos `block_images`, `humanize`, `addons`, `os_randomize`, `disable_ads` y `geoip`. Intenté reproducirlos en Chromium, pero cada uno tenía su propio problema. Esto podría cambiar en las próximas versiones anteriores a v0.4.

Ahora, las buenas noticias: hemos mejorado y corregido muchas cosas :)

### Mejoras {#v0.3.13-improvements}
- Ya sabes que `StealthyFetcher` y sus clases de sesión son ahora un 101% más rápidos, pero `DynamicFetcher` y su clase de sesión también son un 20% más rápidos.
- Se mejoró el algoritmo que resuelve los desafíos de Cloudflare para que termine antes y cubra más casos. Además, gracias a la reorganización del código, ¡puedes esperar que resuelva los captcha el doble de rápido!
- Todos los fetchers usan ahora menos memoria.
- ¡El servidor MCP usa menos tokens para ahorrar más dinero!
- La imagen Docker es ahora un 60% más pequeña.
- Se actualizó todo el sitio de documentación con las novedades. También se aclararon las explicaciones, se acortaron muchas secciones, se añadieron más ejemplos y argumentos que faltaban, se incorporaron gráficos a la referencia de la API y se hicieron muchas otras mejoras. El sitio ahora carga un 130% más rápido, consume menos datos y está mejor preparado para SEO.

### Correcciones {#v0.3.13-fixes}
- Se añadieron los argumentos que faltaban en los atajos de la consola de web scraping y se hicieron más precisos.
- Se corrigió un problema por el que el argumento `google_search` generaba un referer de Google incluso cuando la URL era localhost o una IP.

## [v0.3.12](https://github.com/D4Vinci/Scrapling/releases/tag/v0.3.12) - 2025-12-18 {#v0.3.12}

### Qué ha cambiado {#v0.3.12-what-s-changed}
- Se añadió a las clases `DynamicSession`/`AsyncDynamicSession` un argumento llamado `timezone_id`. Permite configurar la zona horaria del navegador para que coincida con la del proxy o VPN que usas. Así, los sitios no pueden detectar el proxy por una diferencia de zona horaria.
- Se mejoró la conversión automática de respuestas a JSON.
- Se cambió el nombre de la función interna `__create__` a `start` en las clases de sesión de los fetchers para facilitar su uso fuera del contexto `with`.
- Se actualizaron `curl_cffi` y otras dependencias a sus últimas versiones.

## [v0.3.11](https://github.com/D4Vinci/Scrapling/releases/tag/v0.3.11) - 2025-12-03 {#v0.3.11}

### Qué ha cambiado {#v0.3.11-what-s-changed}
- Se mejoró la lógica para gestionar errores de tiempo de espera cuando se usa `network_idle` en un sitio inestable, como uno con contenido multimedia en reproducción.
- Se corrigió el autocompletado del atajo `stealthy_fetch` en la consola de web scraping

## [v0.3.10](https://github.com/D4Vinci/Scrapling/releases/tag/v0.3.10) - 2025-11-26 {#v0.3.10}

**Una actualización de mantenimiento con muchos cambios importantes y posibles cambios incompatibles**

- **Se resolvieron** todos los problemas de codificación mediante un enfoque mejor que gestiona las páginas que no declaran correctamente su codificación (Gracias a @Kemsty2 por el esfuerzo de señalarlo en [#110](https://github.com/D4Vinci/Scrapling/issues/110) [#111](https://github.com/D4Vinci/Scrapling/pull/111) )
- **Se resolvió** un problema de lógica al reemplazar parámetros de sesión con parámetros de petición en todos los fetchers de navegador, presente desde v0.3
- **Se corrigieron** las firmas de los atajos de la consola interactiva de web scraping, logrando un autocompletado completo de esos atajos. Este problema también estaba presente desde v0.3.
- **Se actualizó** la versión de la base de datos Maxmind, lo que mejora el argumento `geoip` de `StealthyFetcher` y sus clases de sesión.
- **Se actualizaron** todos los navegadores usados a las últimas versiones disponibles.
- **CAMBIOS INCOMPATIBLES**: Todos los fetchers pasaron por una gran reorganización del código, que dio lugar a algunos cambios interesantes que podrían afectar a tu código:
    1. El código de Scrapling tiene ahora unas ~750 líneas menos e incluye muchos cambios que facilitan el mantenimiento futuro y reducen un poco el uso de recursos.
    2. La validación de todos los fetchers y sus clases de sesión es mucho más rápida, lo que mejora su velocidad general.
    3. Para lograrlo, los fetchers ya no aceptan argumentos posicionales aparte de `url`. El resto debe pasarse por nombre, así que tu código debe usar `Fetcher.get('https://google.com', stealthy_headers=True)` y no `Fetcher.get('https://google.com', True)`, ¡si lo hacías así por algún motivo!
    4. Desde v0.3 existía una diferencia molesta entre los fetchers de navegador y sus clases de sesión: el argumento para pasar ajustes del analizador por petición se llamaba `custom_config`, pero en las clases de sesión se llamaba `selector_config`. Esta reorganización permitió unificar el nombre como `selector_config` sin romper tu código. Ahora el nombre principal es `selector_config`, con compatibilidad para el antiguo argumento `custom_config`. El autocompletado solo estará disponible para `selector_config`.
    5. Además, para lograr todo esto, las anotaciones de tipos de las funciones de los fetchers ahora se generan de forma dinámica. Si el autocompletado de tu IDE no funciona bien, asegúrate de usar una versión reciente. Hemos probado casi todos los IDE y editores conocidos.

> También hemos actualizado todas las tablas de rendimiento con los datos actuales frente a las últimas versiones de todas las bibliotecas alternativas.

## [v0.3.9](https://github.com/D4Vinci/Scrapling/releases/tag/v0.3.9) - 2025-11-17 {#v0.3.9}

**Una nueva actualización con muchos cambios importantes**

### 🚀 Novedades y mejoras de uso {#v0.3.9-new-stuff-and-quality-of-life-changes}
- El argumento `impersonate` de `Fetcher` y `FetcherSession` ahora acepta una lista de navegadores. La biblioteca elige uno al azar para cada petición.

```python
from scrapling.fetchers import FetcherSession

with FetcherSession(impersonate=['chrome', 'firefox', 'safari']) as s:
  s.get('https://github.com/D4Vinci/Scrapling')
```

- Un nuevo argumento en el método `clean` de `TextHandler` permite eliminar fácilmente las entidades HTML del texto actual.
- Grandes mejoras en la documentación, con explicaciones más precisas de muchas partes y traducciones automáticas del archivo `README.md` principal.

### 🐛 Correcciones de errores {#v0.3.9-bug-fixes}
- Se corrigió un problema importante al obtener respuestas de los fetchers de navegador. Ahora se detecta de forma inteligente el tipo de contenido para que `response.body` solo contenga el contenido renderizado del navegador cuando sea HTML. En los demás casos, contiene el contenido sin procesar de la última petición. Esto permite descargar archivos binarios y de texto sin que aparezcan envueltos en etiquetas HTML, y seguir obteniendo el contenido renderizado del sitio cuando lo necesitas.

### 🔨 Otros cambios {#v0.3.9-misc}
- Se actualizó la guía de contribución para hacerla más clara y sencilla.
- Se añadió un workflow para exigir el uso de las herramientas de calidad de código, las mismas que se usan como hooks de pre-commit.

## [v0.3.8](https://github.com/D4Vinci/Scrapling/releases/tag/v0.3.8) - 2025-10-27 {#v0.3.8}

**Una nueva actualización con muchos cambios importantes**

### 🚀 Novedades y mejoras de uso {#v0.3.8-new-stuff-and-quality-of-life-changes}
- En todos los fetchers de navegador, los sitios cuyas peticiones nunca terminan de cargar ya no hacen fallar el código cuando usas `network_idle`.
- Se cambió la lógica para recoger y comprobar el contenido de las páginas en los fetchers de navegador, para que los navegadores sean tan estables en Windows como en Linux/MacOS. Esta diferencia de comportamiento se debe a la implementación de Playwright en Windows.
- Se reorganizó toda la lógica de validación, lo que aceleró las peticiones de todos los fetchers de navegador entre un 8-15%
- Se añadió la opción `extra_flags` a `DynamicFetcher` y su sesión para agregar opciones de Chrome personalizadas a las existentes al iniciar el navegador.
- Se restauró la lógica anterior de rutas para capturar respuestas cuando se usa `page_action`, que había cambiado en la última versión. Esto permite recoger el contenido más reciente de la página si `page_action` lo cambia sin hacer una petición. (Gracias a @gembleman por señalarlo en [#100](https://github.com/D4Vinci/Scrapling/issues/100) y [#102](https://github.com/D4Vinci/Scrapling/pull/102) )

### 🐛 Correcciones de errores {#v0.3.8-bug-fixes}
- Se corrigió un error de escritura en `load_dom` dentro de async_fetch de DynamicSession
- Se corrigió un problema al resolver desafíos de Cloudflare que hacía esperar indefinidamente a que desaparecieran los captcha incrustados que permanecen visibles tras resolverse. Ahora se espera 30 segundos y, después, se asume que es un captcha de ese tipo (Corrige #100 )

### 🔨 Otros cambios {#v0.3.8-misc}
- La imagen Docker se publica ahora de forma automática en Dockerhub y en el registro de contenedores de GitHub para facilitar su uso.
- Se añadió una [nueva página de documentación](https://github.com/D4Vinci/Scrapling/blob/v0.3.8/docs/tutorials/external.md) que explica cómo usar el navegador Scrapeless con Scrapling.

## [v0.3.7](https://github.com/D4Vinci/Scrapling/releases/tag/v0.3.7) - 2025-10-12 {#v0.3.7}

**Una nueva actualización con muchos cambios importantes**

### 🚀 Novedades y mejoras de uso {#v0.3.7-new-stuff-and-quality-of-life-changes}
- Se rediseñó el argumento `solve_cloudflare` de `StealthyFetcher` para resolver todo tipo de implementaciones personalizadas de Turnstile.
- Se reorganizó todo el código para que pase las comprobaciones de Pyright, mejorando el uso de todos los IDE y corrigiendo muchos errores.
- Se reorganizó la lógica de las peticiones para hacerla más clara y rápida (También resuelve #97 )
- Se añadió la opción `user_data_dir` a todas las clases de sesión de navegador para reutilizar los datos del navegador de sesiones anteriores, como cookies y almacenamiento. Si no la indicas, Playwright usa un directorio aleatorio en cada ejecución, como hacía antes.
- Se añadió la opción de personalización `additional_args` a `Dynamic fetcher` y su clase de sesión para pasar argumentos adicionales al contexto de Playwright, como ya se podía hacer con `StealthyFetcher`.
- Se mejoró la lógica de rutas que recoge la última respuesta de navegación de todos los navegadores. Esto permite pasar las respuestas sin procesar al analizador, en lugar de hacerlo después de que las procese el navegador como antes. Resulta muy útil para respuestas de texto y JSON.

### 🐛 Correcciones de errores {#v0.3.7-bug-fixes}
- La nueva lógica de rutas resolvió un problema al obtener el contenido de sitios inestables en algunos equipos Windows.
- Las reorganizaciones del código de esta versión corrigieron muchos errores difíciles de detectar y problemas extraños de autocompletado en algunos IDE.
- Muchas correcciones en el sitio de documentación

## [v0.3.6](https://github.com/D4Vinci/Scrapling/releases/tag/v0.3.6) - 2025-10-01 {#v0.3.6}

### 🚀 Novedades {#v0.3.6-new-stuff}
- Se mejoró el argumento `solve_cloudflare` de `StealthyFetcher` y sus clases de sesión para resolver todos los tipos de desafíos Turnstile y de páginas intermedias de Cloudflare 🎉
- El servidor MCP ahora permite usar `Streamable HTTP` para ofrecer acceso al servidor fácilmente.
- Se añadió compatibilidad con Docker. Ahora se crea y publica una imagen en Docker Hub de forma automática con cada versión, que incluye todos los navegadores

### 🐛 Correcciones de errores {#v0.3.6-bug-fixes}
- Se corrigió un problema de codificación del analizador que ocurría en algunos casos, el conocido error `invalid start byte`
- Se reorganizaron varias partes de la biblioteca para corregir fugas de memoria. Ahora consume notablemente menos memoria según tu configuración (También resuelve #92 )
- Se mejoraron las anotaciones de tipos en muchas partes del código para facilitar el trabajo en el IDE (También resuelve #93 )

## [v0.3.5](https://github.com/D4Vinci/Scrapling/releases/tag/v0.3.5) - 2025-09-20 {#v0.3.5}

**Una versión necesaria que corrige varios problemas**

### 🚀 Novedades {#v0.3.5-new-stuff}
- Todos los fetchers de navegador (`DynamicFetcher`/`StealthyFetcher`/...) y sus clases de sesión obtienen ahora las páginas un 15-20% más rápido:
    1. La gestión de páginas es mucho más rápida gracias a la mejora de lógica de @AbdullahY36 en #87
    2. Se optimizó la lógica de validación general y se mejoró la creación de páginas para las peticiones síncronas. Juntos, estos cambios aportaron grandes mejoras de velocidad

- Grandes mejoras en el modo de sigilo de `DynamicFetcher` y sus clases de sesión al reemplazar `rebrowser-playwright` por `PatchRight`:
    1. Antes de esta actualización, `rebrowser-playwright` se desactivaba al activar `stealth` y `real_chrome`, porque no funcionaban bien juntos. Con `PatchRight` ya no existe este problema
    2. Ahora puedes interactuar con los Shadow Roots cerrados, porque `PatchRight` los gestiona automáticamente.

### 🐛 Correcciones de errores {#v0.3.5-bug-fixes}
- Se corrigió un error al usar el método `re` de la clase `Selectors`.
- Se corrigió un error de los comandos `uncurl` y `curl2fetcher` en la consola de web scraping que hacía interpretar mal la opción `--data-raw` de curl.
- Se corrigió un error del comando `view` en la consola de web scraping que aparecía según la codificación del sitio.
- Se corrigió un error de conversión de contenido que afectaba al modo `mcp` y a los comandos `extract`.

### Nuevos colaboradores {#v0.3.5-new-contributors}
- @AbdullahY36 hizo su primera contribución en #87

## [v0.3.4](https://github.com/D4Vinci/Scrapling/releases/tag/v0.3.4) - 2025-09-16 {#v0.3.4}

**Una versión necesaria que corrige varios problemas**

### 🚀 Novedades {#v0.3.4-new-stuff}
- Se añadieron todas las clases de sesión de los fetchers a la consola interactiva para poder usarlas directamente, sin importarlas.

### 🐛 Correcciones de errores {#v0.3.4-bug-fixes}
- Se añadió una solución alternativa para un error de la API de Playwright en Windows al obtener contenido mientras se resolvían desafíos de Cloudflare.
- Se corrigió un problema de codificación del comando `view` en la consola interactiva
- Se corrigió un error del argumento `max_pages` en `AsyncStealthySession` que hacía fallar el código.
- Se corrigió un problema de las últimas actualizaciones que hacía que las propiedades `html_content` y `prettify` de `Selector` devolvieran bytes según la codificación. Ambas vuelven a devolver cadenas de texto.

## [v0.3.3](https://github.com/D4Vinci/Scrapling/releases/tag/v0.3.3) - 2025-09-15 {#v0.3.3}

- Se eliminó la lógica que cerraba la pestaña predeterminada del navegador en los fetchers de navegador, porque causaba un fallo. No ocurría en Mac; solo se pudo reproducir en Windows y Linux

## [v0.3.2](https://github.com/D4Vinci/Scrapling/releases/tag/v0.3.2) - 2025-09-15 {#v0.3.2}

Notas de la versión v0.3.2

### 🚀 Novedades {#v0.3.2-new-stuff}

- **Dependencias opcionales de los fetchers**: Todos los fetchers forman ahora parte de grupos de dependencias opcionales, lo que reduce el tamaño del paquete base. El módulo base `scrapling` contiene solo el analizador. Para usar los fetchers o las opciones de línea de comandos, ejecuta `pip install "scrapling[fetchers]"`. Consulta las instrucciones detalladas de instalación [aquí](index.md#installation)
- **Configuración por página en las sesiones**: Las clases de sesión de los fetchers de navegador permiten configurar cada página por separado. Todos los parámetros de las peticiones se validan ahora como los de las sesiones. Tienes más detalles en el sitio de documentación [aquí](fetching/stealthy.md#full-list-of-arguments)
    <br>Ejemplo:

    ```python
    with StealthySession(headless=True, solve_cloudflare=True) as session:
        page = session.fetch('https://nopecha.com/demo/cloudflare', google_search=False)
    ```

- **Mejoras en los fetchers de navegador**
    - Una nueva opción permite elegir si se debe esperar a que termine la ejecución de JavaScript en las páginas. Está activada de forma predeterminada, como antes

        ```python
        with DynamicSession(headless=True, disable_resources=False, network_idle=True) as session:
           page = session.fetch('https://quotes.toscrape.com/', load_dom=False)
        ```

    - El modo de sigilo es ahora más fiable en `DynamicFetcher` y sus clases de sesión.
    - `DynamicFetcher` y `StealthyFetcher` usan ahora menos recursos, al encontrar y cerrar automáticamente la pestaña predeterminada que abren los contextos persistentes de la API de Playwright
    - Se corrigió un error importante de lógica en la rotación de páginas de los fetchers de navegador. Las páginas anteriores ahora se reemplazan por otras nuevas, ya que las pestañas reutilizadas podían conservar ajustes de usos anteriores
    - `StealthyFetcher` y sus clases de sesión son ahora un poco más rápidos (5%)

- **Mejoras en la propiedad `.body`**: Ahora devuelve el contenido recibido tal cual, sin procesarlo, lo que permite descargar archivos y gestionar peticiones que no devuelven HTML. Este ejemplo muestra cómo descargar una imagen:

    ```python
    from scrapling.fetchers import Fetcher

    page = Fetcher.get('https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/poster.png')
    with open(file='poster.png', mode='wb') as f:
        f.write(page.body)
    ```

### 🐛 Correcciones de errores {#v0.3.2-bug-fixes}

- **Problemas de codificación resueltos**: Se corrigieron varios problemas de codificación con algunos sitios en el analizador, el modo mcp y los comandos extract (También resuelve #80 y #81)
- **Análisis más rápido**: Gracias a muchos cambios en distintas partes, la biblioteca es ahora más rápida, como muestran las pruebas de rendimiento actualizadas

### 🔨 Otros cambios {#v0.3.2-misc}

- **Pruebas de rendimiento actualizadas**: Se actualizaron las mediciones para comparar las mejoras de velocidad actuales con las últimas versiones de bibliotecas similares
- **Se reorganizó gran parte del código y se reemplazó el código sin uso por mejores implementaciones**: Menos código, más claro y más fácil de mantener
- **Nuevo vídeo de YouTube**: Se añadió contenido en vídeo a la documentación de MCP.
- **Nueva plantilla de incidencias**: Una plantilla sencilla para quienes no pueden usar las actuales.
- **Optimización del workflow de CI**: El workflow de pruebas ya no se ejecuta cuando solo cambia la documentación u otros archivos que no son código.
- **Dependencias actualizadas**: Se actualizaron varias dependencias a sus últimas versiones.
- **Mejoras en el estilo de código**: Se aplicaron nuevas reglas de ruff en todos los archivos.
- **Hooks de pre-commit**: Se actualizó la configuración de pre-commit.

### 🎯 Cambios incompatibles {#v0.3.2-breaking-changes}

- Se eliminó el parámetro `max_pages` de la versión síncrona de `StealthySession` para igualarla a `DynamicSession`, porque no tiene sentido en la versión síncrona

## [v0.3.1](https://github.com/D4Vinci/Scrapling/releases/tag/v0.3.1) - 2025-09-02 {#v0.3.1}

1. Se corrigió un problema al instalar scrapling sin el extra `shell` (#76 )
2. Se añadió un argumento a todos los fetchers de navegador y sus clases de sesión para pasar un archivo JS que se ejecuta al crear la página (#56) :

```python
from scrapling.fetchers import StealthyFetcher

StealthyFetcher.fetch('https://example.com', init_script="/absolute/path/to/js/script.js")
```

## [v0.3](https://github.com/D4Vinci/Scrapling/releases/tag/v0.3) - 2025-09-01 {#v0.3}

🎉 **Versión principal - Renovación completa de la arquitectura**

Scrapling v0.3 es la mayor actualización en la historia del proyecto. Incluye una reescritura completa de la arquitectura, mejoras importantes de rendimiento y nuevas funciones potentes, como la integración con IA y una consola interactiva de web scraping.

Esta versión incluye varios cambios incompatibles. Lee las notas de la versión con atención.

### 🚀 Principales novedades {#v0.3-major-new-features}

#### Arquitectura basada en sesiones {#v0.3-session-based-architecture}
- **Nuevas clases de sesión**: Reescritura completa que añade soporte para sesiones persistentes
    - `FetcherSession` - Peticiones HTTP con gestión de estado persistente, tanto para código síncrono como asíncrono
    - `DynamicSession`/`AsyncDynamicSession` - Automatización del navegador, que permanece abierto hasta que termines
    - `StealthySession`/`AsyncStealthySession` - Navegación sigilosa, con el navegador abierto hasta que termines
- **Gestión asíncrona de pestañas del navegador**: Nuevo grupo de pestañas mediante el argumento `max_pages`, que alterna entre ellas para hacer peticiones concurrentes con el navegador
- **Sesiones concurrentes**: Ejecuta varias sesiones aisladas al mismo tiempo

Consulta la sección `Fetching` del sitio web para más detalles.

#### Muchas funciones nuevas de sigilo y evasión de sistemas antibots {#v0.3-a-lot-of-new-stealth-anti-bot-capabilities}
- **🤖 Resolución de Cloudflare**: [Resolución automática de desafíos de Cloudflare Turnstile](fetching/stealthy.md#cloudflare-and-stealth-options) en `StealthyFetcher` y sus clases de sesión
- **Imitación de huellas del navegador**: Imita las huellas TLS de navegadores reales, usa cabeceras que coincidan con su versión y aprovecha el soporte para HTTP/3 y otras funciones con la nueva clase [Fetcher](fetching/static.md)
- **Modo sigiloso mejorado**: El modo sigiloso de `DynamicFetcher` y sus clases de sesión ahora es más sólido y fiable (también conocido como `PlayWrightFetcher`)

#### Integración con IA y servidor MCP {#v0.3-ai-integration-mcp-server}
- **Servidor MCP integrado**: Servidor Model Context Protocol para web scraping asistido por IA
- **6 herramientas potentes**: `get`, `bulk_get`, `fetch`, `bulk_fetch`, `stealthy_fetch`, `bulk_stealthy_fetch`
- **Extracción inteligente de contenido**: Convierte páginas o elementos web a Markdown o HTML, o extrae una versión limpia del texto
- **Soporte para selectores CSS**: Usa el motor de Scrapling para seleccionar elementos concretos con precisión antes de enviar el contenido a la IA
- **Evasión de sistemas antibots**: Gestiona Cloudflare Turnstile y otras protecciones
- **Soporte para proxies**: Usa proxies para mantener el anonimato y elegir la ubicación geográfica
- **Imitación de navegadores**: Imita navegadores reales con huellas TLS, cabeceras reales que coincidan con su versión y más
- **Procesamiento en paralelo**: Extrae datos de varias URL al mismo tiempo para ganar eficiencia
- [y más...](ai/mcp-server.md)

#### Nueva consola interactiva de web scraping {#v0.3-new-interactive-web-scraping-shell}
- **Nueva consola**: Consola IPython personalizada con muchos atajos inteligentes integrados, como `get`, `post`, `put`, `delete`, `fetch` y `stealthy_fetch`
- **Gestión inteligente de páginas**: Nuevos comandos `page` y `pages` para guardar automáticamente la página actual y el historial de todas las peticiones hechas desde la consola
- **Integración con Curl**: Usa las funciones `uncurl` y `curl2fetcher` para convertir comandos curl de las herramientas de desarrollo del navegador en peticiones de `Fetcher`
- [y más...](cli/interactive-shell.md)

#### Extrae datos desde la terminal sin programar {#v0.3-scrape-from-the-terminal-without-programming}
- **Nuevos comandos de extracción**: Extrae datos desde la terminal sin programar
    - `scrapling extract get/post/put/delete` - Peticiones HTTP sencillas
    - `scrapling extract fetch` - Extracción de contenido dinámico
    - `scrapling extract stealthy-fetch` - Evasión de sistemas antibots
- **Descarga páginas web** y guarda su contenido en archivos.
- **Convierte HTML a formatos legibles** como Markdown, lo conserva como HTML o extrae solo el texto de la página.
- **Admite selectores CSS personalizados** para extraer partes concretas de la página.
- **Gestiona peticiones HTTP y la obtención de páginas con navegadores.**
- **Muy configurable**, con cabeceras, cookies, proxies y otras opciones personalizadas. Casi todas las opciones disponibles en el código también están disponibles desde la terminal.
- [y más...](cli/extract-commands.md)

### 🔧 Mejoras técnicas {#v0.3-technical-improvements}

#### Mejoras de rendimiento {#v0.3-performance-enhancements}
- **Fetcher ahora es 4 veces más rápido** - ¡Sí, has leído bien!
- **DynamicFetcher ahora es ~60% más rápido** - Una versión mucho más rápida según tu configuración (sobre todo el modo sigiloso)
- **StealthyFetcher ahora es 20–30% más rápido** - Gracias a la nueva estructura y al uso de nuestra propia implementación en lugar de la interfaz Python de `Camoufox`
- **Mejora conjunta de velocidad de 50%+** en los métodos principales de selección (`find_by_text`, `find_similar`, `find_by_regex`, `relocate`, etc.) 🚀
- **Aumento de ~10% en la velocidad de los métodos que obtienen la primera coincidencia CSS/XPath** - `css_first` y `xpath_first` ahora son más rápidos que `css` y `xpath`
- **El método `get_all_text()` es 40% más rápido** al extraer contenido
- **Mejora de velocidad del 20%** al volver a localizar elementos de forma adaptativa
- **Optimización de las propiedades de navegación** - Propiedades como `next`, `previous`, `below_elements` y otras ahora son notablemente más rápidas
- **Limpieza de texto 5 veces más rápida**
- **Mejor uso de la memoria** con importaciones optimizadas y menos trabajo adicional
- **⚡ Importaciones muy rápidas**: Menor tiempo de inicio gracias a una carga de módulos optimizada
- **Mejores resultados en las pruebas de rendimiento**: Todas las mejoras de velocidad hacen que Scrapling sea mucho más rápido que antes frente a otras bibliotecas (1775 veces más rápido que BeautifulSoup y 5.1 veces más rápido que AutoScraper; consulta las [pruebas de rendimiento](benchmarks.md))

#### Arquitectura, calidad del código y mejoras de uso {#v0.3-architecture-code-quality-and-quality-of-life}
- **Contexto persistente**: Todos los fetchers basados en navegador usan ahora un contexto persistente por defecto. (También resuelve #64)
- **Uso de msgspec para validar muy rápido la configuración de todos los fetchers basados en navegador** antes de ejecutar las peticiones, lo que facilita detectar errores.
- **Todas las cookies** que devuelven los fetchers tienen ahora el formato que acepta ese mismo fetcher. Así puedes obtener cookies y volver a pasarlas a todos los fetchers y sus clases de sesión.
- **Análisis y formato de código más rápidos** tras migrar a `ruff`
- **Sistema de construcción moderno**: Migración de setup.py a pyproject.toml 📦
- **Mejores acciones y flujos de trabajo de GitHub** para facilitar el desarrollo y las pruebas
- **🎨 Mejores anotaciones de tipos**: Cobertura completa de tipos con estándares modernos de Python para mejorar el soporte del IDE y la fiabilidad
- **Código más limpio**: Eliminación de código sin uso y optimización de las funciones principales 🧹
- **🚀 Compatibilidad con versiones anteriores**: Nuevos atajos para mantener la compatibilidad con código antiguo

### Cambios incompatibles {#v0.3-breaking-changes}

#### Versión mínima de Python {#v0.3-minimum-python-version}
- **Se requiere Python 3.10+**: Se elimina el soporte para Python 3.9 y anteriores

#### Nombres de clases y métodos {#v0.3-class-and-method-naming}
Estos cambios de nombre buscan dar más claridad y coherencia, sobre todo para los usuarios nuevos.

- **`Adaptor` → `Selector`**: Se cambia el nombre de la clase principal de análisis (aún se puede importar como `Adaptor` para mantener la compatibilidad)
- **`Adaptors` → `Selectors`**: Se cambia el nombre de la clase de colección (aún se puede importar como `Adaptors` para mantener la compatibilidad)
- **`auto_match` → `adaptive`**: Se cambia el nombre del parámetro en todos los métodos
- **`adaptor_arguments` → `selector_config`**: Se cambia el nombre del parámetro de configuración
- **`automatch_domain` → `adaptive_domain`**: Se cambia el nombre del parámetro de dominio
- **`additional_arguments` → `additional_args`**: Se acorta el nombre del parámetro
- **⚠️ `text/body` → `content`**: El parámetro del constructor de Selector ahora acepta tanto `str` como `bytes`
- **`PlayWrightFetcher` → `DynamicFetcher`**: Se cambia el nombre de la clase de automatización del navegador (aún se puede importar como `PlayWrightFetcher` para mantener la compatibilidad)
- **DynamicFetcher ya no incluye la lógica ni los argumentos de NSTBrowser**, porque ya no tiene sentido mantenerlos.
- **El argumento headless de StealthyFetcher ya no acepta 'virtual'** porque ahora solo usamos la biblioteca Camoufox para obtener la ruta de instalación del navegador y las demás opciones de inicio

### 🐛 Correcciones de errores {#v0.3-bug-fixes}

- Se corrige el recuento de hijos anidados en etiquetas ignoradas por `get_all_text` (#61)
- Se corrige el problema de instalación causado por espacios en la ruta del ejecutable de Python (#57)
- Se resuelven problemas de hilos en el almacenamiento, con gestión de la recursión cuando la función adaptativa está activada
- Se corrigen problemas de prioridad de argumentos mediante el patrón Sentinel en `FetcherSession`
- Se corrige la gestión de tipos de proxy en `StealthyFetcher`
- Se corrigen conflictos entre los argumentos `referer` y `google_search`
- Se corrigen problemas al inyectar scripts de sigilo de forma asíncrona

## [v0.2.99](https://github.com/D4Vinci/Scrapling/releases/tag/v0.2.99) - 2025-04-08 {#v0.2.99}

**Esta es una actualización importante para que todos puedan disfrutar plenamente de Scrapling tal como se diseñó.**

### Qué ha cambiado {#v0.2.99-what-s-changed}
#### Nuevo sitio web con toda la documentación {#v0.2.99-new-full-documentation-website}
- Sí, por fin 😄 Puedes verlo [aquí](index.md)
#### Importación unificada de fetchers {#v0.2.99-unified-import-logic-for-fetchers}
- Ahora puedes importar todos los fetchers con `from scrapling.fetchers import Fetcher, AsyncFetcher, StealthyFetcher, PlayWrightFetcher` y usarlos directamente, como en `page = Fetcher.get(...)`, sin crear una instancia.<br/> Esto sustituye a la importación anterior `from scrapling.defaults import Fetcher, AsyncFetcher, StealthyFetcher, PlayWrightFetcher`.
#### Cambio incompatible: automatch ahora está desactivado por defecto {#v0.2.99-breaking-change-automatch-is-now-turned-off-by-default}
- Ahora hay una nueva forma de activar automatch desde los fetchers y las demás opciones de análisis. Consulta la [documentación](fetching/choosing.md#parser-configuration-in-all-fetchers) para más detalles.
>  Las importaciones y la lógica anteriores siguen disponibles, con una advertencia, para mantener la compatibilidad.
#### Nuevas opciones para los fetchers {#v0.2.99-new-options-added-to-fetchers}
- Ahora `StealthyFetcher` y `PlayWrightFetcher` tienen un nuevo argumento llamado `wait` al obtener páginas. Hace que el fetcher espere un tiempo concreto en milisegundos antes de cerrar la página y devolver la respuesta.
- Los métodos de `StealthyFetcher` llamados `fetch` y `async_fetch` tienen ahora el argumento `additional_arguments` para pasar opciones adicionales a Camoufox. Estas tienen prioridad sobre la configuración de Scrapling (#54 )
#### Correcciones de errores {#v0.2.99-bugs-squashed}
- Se corrige un error al detectar redirecciones en `async_fetch` de las clases `StealthyFetcher` y `PlayWrightFetcher`.

**_¡Gracias por todo tu apoyo y tus donaciones!_**

## [v0.2.98](https://github.com/D4Vinci/Scrapling/releases/tag/v0.2.98) - 2025-03-17 {#v0.2.98}

**Esta es una actualización importante para que todos puedan disfrutar plenamente de Scrapling tal como se diseñó**

### Qué ha cambiado {#v0.2.98-what-s-changed}
#### Mejoras en el uso de memoria y la velocidad {#v0.2.98-various-memory-usage-and-speed-optimizations}
- El uso de memoria de todos los métodos de selección es ahora ~40% del anterior, con un pequeño aumento de velocidad.
- Se aplica la carga diferida a todos los submódulos de la biblioteca: ahora solo se carga lo que usas. Por ejemplo:
Antes de la actualización, la importación `from scrapling import Adaptor` usaba `30-40mb` de RAM porque también cargaba todos los fetchers y otros componentes. Ahora usa `~1.2mb`.
- La última actualización hizo que la biblioteca usara ~32% de la memoria que usaba antes con un grupo grande de peticiones. Ahora ajustamos más la caché para usar todavía menos.
- Pequeño aumento general de velocidad del analizador, de 2-5%

**_¡Gracias por todo tu apoyo y tus donaciones!_**

## [v0.2.97](https://github.com/D4Vinci/Scrapling/releases/tag/v0.2.97) - 2025-03-15 {#v0.2.97}

**Esta es una actualización importante para que todos puedan disfrutar plenamente de Scrapling tal como se diseñó**

### Qué ha cambiado {#v0.2.97-what-s-changed}
#### Menor uso de memoria y un pequeño aumento de velocidad en todos los fetchers {#v0.2.97-lower-memory-usage-and-small-speed-increase-across-all-fetchers}
- Los nuevos límites de tamaño de la caché en toda la biblioteca reducen mucho el uso de memoria al hacer grandes cantidades de peticiones u operaciones.
- Se reorganizan grandes partes de los fetchers para facilitar su mantenimiento y aumentar un poco la velocidad.

#### Correcciones de errores {#v0.2.97-bugs-fixed}
- Se corrige un error de `TextHandler` que convertía un valor no textual en una cadena vacía al importarlo por separado. Ahora cualquier valor que se pase a `TextHandler` se convierte primero en una cadena y luego en `TextHandler`. Esto se aplica a todos los valores: ¡`TextHandler`, como indica su nombre, está pensado para trabajar solo con texto! (#45 )
- Se corrige un error que hacía que la mayoría de los métodos de AsyncFetcher ignoraran el argumento `retries`.

#### Otros cambios {#v0.2.97-miscellaneous}
- Se actualizan las anotaciones de tipos de la mayoría de los argumentos en todos los fetchers para que sean más claras y precisas.

**_¡Gracias por todo tu apoyo y tus donaciones!_**

## [v0.2.96](https://github.com/D4Vinci/Scrapling/releases/tag/v0.2.96) - 2025-03-05 {#v0.2.96}

**Esta es una actualización importante para que todos puedan disfrutar plenamente de Scrapling tal como se diseñó**

### Qué ha cambiado {#v0.2.96-what-s-changed}
1. Se añade la opción `-f` a `scrapling install` para forzar la reinstalación de las dependencias del navegador. Te recomiendo ejecutar `scrapling install -f` ahora para aprovechar la gran mejora de velocidad de `StealthyFetcher` con la nueva versión del navegador Camoufox :)
2. Se corrige un error de `TextHandler` que devolvía `TextHandlers` en lugar de `TextHandler` al obtener una porción del texto, y se corrige su anotación de tipo (#41 )
3. Se corrige un problema que hacía que `scrapling install` abriera una consola Python en algunos casos.

## [v0.2.95](https://github.com/D4Vinci/Scrapling/releases/tag/v0.2.95) - 2025-02-25 {#v0.2.95}

**Esta es una actualización importante para que todos puedan disfrutar plenamente de Scrapling tal como se diseñó**

### Qué ha cambiado {#v0.2.95-what-s-changed}
1. Se corrige un error de `Fetcher` que hacía que las cabeceras generadas por el argumento `stealthy_headers` sobrescribieran algunas cabeceras del usuario, como `Accept` (#39 )
2. Se mejora un poco la lógica de generación de cabeceras, lo que debería aumentar ligeramente la velocidad.

## [v0.2.94](https://github.com/D4Vinci/Scrapling/releases/tag/v0.2.94) - 2025-02-22 {#v0.2.94}

**Esta es una actualización importante para que todos puedan disfrutar plenamente de Scrapling tal como se diseñó**

### Qué ha cambiado {#v0.2.94-what-s-changed}
1. Se añade la propiedad `history` a todos los fetchers para mostrar las redirecciones (#32 )
2. Se corrige la lógica del argumento `case_sensitive` en todos los métodos `re`/`re_first`. Si lo usabas, esto puede cambiar los resultados de tu código (aunque quizá te lo merezcas por haber visto que no funcionaba bien sin abrir una incidencia, jajaja)
3. Se actualizan las dependencias y se vuelve a activar `coop` en el motor Camoufox (StealthyFetcher).

## [v0.2.93](https://github.com/D4Vinci/Scrapling/releases/tag/v0.2.93) - 2025-01-31 {#v0.2.93}

**Esta es una actualización importante para que todos puedan disfrutar plenamente de Scrapling tal como se diseñó**

### Qué ha cambiado {#v0.2.93-what-s-changed}
1. El tipo de retorno es ahora coherente en todo el motor de análisis. Siempre recibirás uno de estos tipos: `Adaptor`, `Adaptors`, `TextHandler`, `TextHandlers`, `None`, o una lista si hay resultados mixtos, como con un selector CSS combinado. Esto facilita la programación con menos comprobaciones manuales de tipos, hace que la biblioteca sea más estable y permite encadenar métodos en todos los casos.
2. Se reorganiza la mayor parte del motor de análisis, sobre todo la clase `Adaptor`, para que sea más limpio y, lo más importante, más rápido. Casi todos los métodos y propiedades, sobre todo los de búsqueda, ganan entre 5-40% de velocidad. Algunos mejoran aún más, como `find_by_regex`, que gana ~60%. La función automatch gana alrededor de ~5%.
3. Se corrigen errores en la lógica de `find_all`/`find` que aplicaban los filtros con OR en unos casos y con AND en otros. Ahora todos los elementos devueltos deben cumplir todos los filtros que pases.
4. Todos los métodos relacionados con regex devuelven ahora `TextHandler`/`TextHandlers` para facilitar el encadenamiento de métodos.
5. **Se añade una nueva** propiedad `below_elements`, que devuelve un objeto `Adaptors` con todos los elementos situados bajo el elemento actual en el árbol DOM.
6. Todos los métodos y propiedades que devolvían código HTML como cadena ahora lo devuelven como `TextHandler`, para que puedas aplicar regex y otras operaciones con facilidad...
7. StealthyFetcher ahora es un poco más rápido y sigiloso. También permite pulsar CAPTCHA dentro de iframes, como **Cloudflare Turnstile**.
8. Se mejoran mucho el autocompletado y las anotaciones de tipos en casi la mitad de la biblioteca, sobre todo en `Adaptor`, `TextHandler` y `TextHandlers`.
9. Al obtener una porción de `TextHandler`, acceder por índice o usar el método `split`, ahora recibes otro `TextHandler` en lugar de una cadena estándar de Python. Casi todas las operaciones y métodos estándar de cadenas devuelven ahora otro `Texthandler` para que siempre puedas encadenar métodos y funciones.
10. Se corrigen algunos errores pequeños y erratas. Por ejemplo, async_put de Fetcher hacía una petición post en lugar de put 😶‍🌫️
11. Se mejora un poco el README mientras termino el sitio web de documentación.

Iba a ser una pequeña actualización antes de la versión 0.3, pero decidí mejorarla un poco más.

## [v0.2.92](https://github.com/D4Vinci/Scrapling/releases/tag/v0.2.92) - 2024-12-26 {#v0.2.92}

### Qué ha cambiado {#v0.2.92-what-s-changed}
- Las respuestas de los fetchers basados en navegador usan ahora fuentes de datos más fiables cuando la página cargada contiene muchos iframes.
- **¡Instalar `Scrapling` ahora es aún más fácil: instálalo con pip, ejecuta `scrapling install` en la terminal y listo!**
- Se corrige una anotación de tipo imprecisa en el analizador.

## [v0.2.91](https://github.com/D4Vinci/Scrapling/releases/tag/v0.2.91) - 2024-12-19 {#v0.2.91}

### Qué ha cambiado {#v0.2.91-what-s-changed}
- Se corrige un error que hacía que el mensaje de registro de obtención de páginas solo apareciera en la primera petición.
- Por defecto, la API de Playwright devuelve la primera respuesta que cumple el estado de carga indicado al método `goto`: `["load", "domcontentloaded", "networkidle"]`. Si un sitio tiene una página de espera, como la de Cloudflare, que luego te redirige al sitio real, Playwright devuelve el primer código de estado, que podría ser 403. Esta actualización resuelve el problema en `PlaywrightFetcher` y `StealthyFetcher`, ya que ambos usan la API de Playwright. El resultado ya no depende de ese comportamiento por defecto.
- Se añade soporte para proxies SOCKS en la clase `Fetcher`.
- Se corrige la anotación de tipo del argumento `wait_selector_state` para que el autocompletado muestre los valores correctos que puedes usar.

## [v0.2.9](https://github.com/D4Vinci/Scrapling/releases/tag/v0.2.9) - 2024-12-16 {#v0.2.9}

### Qué ha cambiado {#v0.2.9-what-s-changed}
##### Nuevas funciones {#v0.2.9-new-features}
1. ¡Llega el **tan esperado** soporte asíncrono para Scrapling! Ahora tienes `AsyncFetcher`, la versión asíncrona de `Fetcher`, y tanto `StealthyFetcher` como `PlayWrightFetcher` tienen un nuevo método llamado `async_fetch` con las mismas opciones.

```python
>> from scrapling import StealthyFetcher
>> page = await StealthyFetcher().async_fetch('https://www.browserscan.net/bot-detection')  # the async version of fetch
>> page.status == 200
True
```

2. La clase `StealthyFetcher` tiene ahora el argumento `geoip` en sus métodos de obtención. Al activarlo, usa automáticamente la longitud, latitud, zona horaria, país y configuración regional de la IP, y modifica la dirección IP que expone WebRTC. También calcula y simula el idioma del navegador según la distribución de hablantes de cada idioma en la región de destino.
3. Se añade el argumento `retries` a las clases `Fetcher`/`AsyncFetcher` para que puedas fijar el número de reintentos de cada petición hecha con `httpx`.
4. Se añade el método `url_join` a `Adaptor` y a los fetchers. Recibe una URL relativa y la combina con la URL actual para crear una URL absoluta completa.
5. Se añade el método `keep_cdata` a `Adaptor` y a los fetchers para evitar que el analizador elimine cdata cuando necesites conservarlo.
6. En `Adaptor`/`Response`, el método `body` devuelve ahora la respuesta HTML original cuando es posible, sin procesarla en la biblioteca.
7. Se añade registro de eventos a la clase `Response`. Al usar los fetchers, ahora recibes un registro con información sobre la respuesta.
Ejemplo:

   ```python
   >> from scrapling.defaults import Fetcher
   >> Fetcher.get('https://books.toscrape.com/index.html')
   [2024-12-16 13:33:36] INFO: Fetched (200) <GET https://books.toscrape.com/index.html> (referer: https://www.google.com/search?q=toscrape)
   >>
   ```

8. Al usar métodos estándar de cadenas sobre un `TextHandler`, como `.replace()`, ahora recibes otro `TextHandler`. Antes devolvían una cadena estándar.
9. Grandes mejoras de velocidad en toda la biblioteca y mejoras de sigilo en las clases de fetchers en general.
10. Se añaden funciones de compatibilidad como `extract_first`\`extract` que devuelven el mismo resultado que el objeto original. Se incluyen solo para facilitar la copia de código de Scrapy/Parsel a Scrapling cuando haga falta, porque allí se usan estas funciones.
11. Las peticiones por lotes ahora son mucho más rápidas gracias a la reorganización de gran parte del código y al uso de caché en los lugares adecuados.

##### Cambios incompatibles {#v0.2.9-breaking-changes}
- Se elimina el soporte para Python 3.8. (Sobre todo porque Playwright dejó de admitirlo, aunque ya era una versión problemática)
- Se elimina el argumento `debug` de toda la biblioteca. Si quieres activar la depuración, haz esto después de importarla:

   ```python
   >>> import logging
   >>> logging.getLogger("scrapling").setLevel(logging.DEBUG)
   ```

##### Correcciones de errores {#v0.2.9-bugs-squashed}
1. WebGL ahora está activado por defecto porque muchas protecciones comprueban si está habilitado.
2. Se corrigen algunos errores y erratas en la documentación y el README.

##### Mejoras de uso {#v0.2.9-quality-of-life-changes}
1. Todos los registros usan ahora el logger llamado `scrapling` para facilitar su control. Antes usábamos el logger raíz.
2. Se reorganiza la carpeta de pruebas para que sea más clara y se añaden pruebas de las nuevas funciones. Se reescriben todas las pruebas de forma más limpia y se añaden más para aumentar la cobertura.
3. Se reorganiza gran parte del código para que sea más limpio y fácil de mantener.

> Todos estos cambios estaban previstos para la versión 0.3, pero decidí incluirlos aquí porque aún falta un tiempo para la siguiente versión. El próximo paso es terminar el sitio web de documentación detallada y luego trabajar en la versión 0.3

## [v0.2.8](https://github.com/D4Vinci/Scrapling/releases/tag/v0.2.8) - 2024-11-30 {#v0.2.8}

### Qué ha cambiado {#v0.2.8-what-s-changed}
- Pequeña actualización con mejoras de uso necesarias en el código y la corrección de una errata en el README principal (#20)

## [v0.2.7](https://github.com/D4Vinci/Scrapling/releases/tag/v0.2.7) - 2024-11-26 {#v0.2.7}

### Qué ha cambiado {#v0.2.7-what-s-changed}
##### Nuevas funciones {#v0.2.7-new-features}
- Si usas el argumento `wait_selector` con las clases `StealthyFetcher` y `PlayWrightFetcher`, Scrapling vuelve a esperar a que JS se cargue y se ejecute por completo, como de costumbre. Si usas `network_idle`, también vuelve a esperar ese estado después. Si todos los estados ya se cumplen, no espera.
- Ahora puedes activar y desactivar los anuncios en `StealthyFetcher` con el argumento `disable_ads`. El bloqueo está activado por defecto e instala la extensión `ublock origin`.
- Ahora puedes definir la configuración regional de `PlayWrightFetcher` con el argumento `locale`. El valor por defecto sigue siendo `en-US`.
- Las peticiones básicas hechas con `Fetcher` ahora aceptan proxies con el formato `http://username:password@localhost:8030`.
- Se mejora un poco el modo sigiloso de `PlayWrightFetcher`.

##### Correcciones de errores y mejoras {#v0.2.7-bugs-squashed-improvements}
1. Activar proxies en la clase `PlayWrightFetcher` ya no depende de si el modo `stealth` está activado o no (gracias a [@AbdullahY36](https://github.com/AbdullahY36) por avisar)
2. Ahora `ResponseEncoding` comprueba si la codificación indicada en la respuesta sirve para la página. Si esa codificación provoca un error, Scrapling usa `utf-8` por defecto

## [v0.2.6](https://github.com/D4Vinci/Scrapling/releases/tag/v0.2.6) - 2024-11-24 {#v0.2.6}

### Qué ha cambiado {#v0.2.6-what-s-changed}
##### Nuevas funciones {#v0.2.6-new-features}
- Ahora `PlayWrightFetcher` puede usar directamente el navegador real si pasas `real_chrome` a la función `PlayWrightFetcher.fetch`, pero necesitas tener Chrome instalado. Scrapling inicia una instancia de tu navegador Chrome y puedes usar la mayoría de las opciones como siempre. (Antes solo tenías el argumento `cdp_url` para hacerlo)
- Se actualiza la versión que reflejan las cabeceras generadas para navegadores reales.

##### Correcciones de errores {#v0.2.6-bugs-squashed}
1. El formato de las cabeceras de navegador generadas por `BrowserForge` estaba desactualizado, lo que permitía que algunas protecciones detectaran Scrapling. Ahora `BrowserForge` solo se usa para generar un useragent real.
2. El argumento `hide_canvas` ahora está desactivado por defecto porque ReCaptcha de Google lo detecta.

## [v0.2.5](https://github.com/D4Vinci/Scrapling/releases/tag/v0.2.5) - 2024-11-23 {#v0.2.5}

### Qué ha cambiado {#v0.2.5-what-s-changed}

##### Correcciones de errores {#v0.2.5-bugs-squashed}
- Se controla un error del argumento 'wait_selector' cuando coincide con más de 1 elemento. Afecta a las clases `StealthyFetcher` y `PlayWrightFetcher`.
- Se corrige el tipo de codificación cuando la cabecera `content_type` contiene parámetros como `charset` (gracias a @andyfcx por [#12](https://github.com/D4Vinci/Scrapling/issues/12) )

##### Mejoras de uso {#v0.2.5-quality-of-life}
- Se añaden pruebas para cubrir nuevas partes del código y las pruebas pasan a ejecutarse en hilos.
- Se actualizan los docstrings para que se muestren correctamente en apidoc de Sphinx y herramientas similares.

##### Nuevos colaboradores {#v0.2.5-new-contributors}
- @andyfcx hizo su primera contribución en [#13 ](https://github.com/D4Vinci/Scrapling/pull/13)

## [v0.2.4](https://github.com/D4Vinci/Scrapling/releases/tag/v0.2.4) - 2024-11-20 {#v0.2.4}

### Qué ha cambiado {#v0.2.4-what-s-changed}

##### Correcciones de errores {#v0.2.4-bugs-squashed}
- Se corrige un error al obtener los bytes de la respuesta después de usar `network_idle` en las clases `StealthyFetcher` y `PlayWrightFetcher`. <br/> Provocaba el siguiente mensaje de error:

    ```
    Response.body: Protocol error (Network.getResponseBody): No resource with given identifier found
    ```

- La API de PlayWright a veces devuelve respuestas con el texto de estado vacío. Ahora `Scrapling` lo calcula por su cuenta si eso ocurre. Afecta a las clases `StealthyFetcher` y `PlayWrightFetcher`.

## [v0.2.3](https://github.com/D4Vinci/Scrapling/releases/tag/v0.2.3) - 2024-11-19 {#v0.2.3}

### Qué ha cambiado {#v0.2.3-what-s-changed}

##### Correcciones de errores {#v0.2.3-bugs-squashed}
- Se corrige un error de instalación con pip que impedía por completo el funcionamiento del modo sigiloso de PlayWright Fetcher.

## [v0.2.2](https://github.com/D4Vinci/Scrapling/releases/tag/v0.2.2) - 2024-11-16 {#v0.2.2}

### Qué ha cambiado {#v0.2.2-what-s-changed}
##### Nuevas funciones {#v0.2.2-new-features}
- Si no quieres pasar argumentos al objeto `Adaptor` generado y prefieres los valores por defecto, puedes usar esta importación para que el código sea más limpio

    ```python
    >> from scrapling.default import Fetcher, StealthyFetcher, PlayWrightFetcher
    >> page = Fetcher.get('https://example.com', stealthy_headers=True)
    ```

    En caso contrario

    ```python
    >> from scrapling import Fetcher, StealthyFetcher, PlayWrightFetcher
    >> page = Fetcher(auto_match=False).get('https://example.com', stealthy_headers=True)
    ```

##### Correcciones de errores {#v0.2.2-bugs-squashed}
1. Se corrige un error del objeto `Response`, introducido en el parche v0.2.1 de ayer, que aparecía en algunos casos de selección o análisis anidados.

## [v0.2.1](https://github.com/D4Vinci/Scrapling/releases/tag/v0.2.1) - 2024-11-15 {#v0.2.1}

### Qué ha cambiado {#v0.2.1-what-s-changed}
##### Nuevas funciones {#v0.2.1-new-features}
1. El objeto `Response` que devuelven todos los fetchers ahora es igual al objeto `Adaptor`, pero con estos atributos adicionales: `status`, `reason`, `cookies`, `headers` y `request_headers`. Los atributos `cookies`, `headers` y `request_headers` siempre son de tipo `dictionary`. <br/>Así, tu código ahora puede ser:

    ```python
    >> from scrapling import Fetcher
    >> page = Fetcher().get('https://example.com', stealthy_headers=True)
    >> print(page.status)
    200
    >> products = page.css('.product')
    ```

    En lugar del código anterior

    ```python
    >> from scrapling import Fetcher
    >> fetcher = Fetcher().get('https://example.com', stealthy_headers=True)
    >> print(fetcher.status)
    200
    >> page = fetcher.adaptor
    >> products = page.css('.product')
    ```

    He mantenido la propiedad `.adaptor` para conservar la compatibilidad con versiones anteriores.

2. Las clases `StealthyFetcher` y `PlayWrightFetcher` ahora aceptan un argumento `proxy` en el método de obtención, que puede ser una cadena o un diccionario.
3. La clase `StealthyFetcher` tiene ahora el argumento `os_randomize` en el método `fetch`. Si lo activas, Scrapling elige al azar las huellas de sistema operativo. Por defecto, las huellas coinciden con el sistema operativo actual.

##### Correcciones de errores {#v0.2.1-bugs-squashed}
1. Se corrige un error al pasar cabeceras con la clase `Fetcher`.
2. Se corrige un error al analizar respuestas JSON recibidas de las clases de fetchers.

##### Mejoras de uso {#v0.2.1-quality-of-life-changes}
1. Las funciones de texto intentaban eliminar los comentarios HTML antes de devolver el texto, pero eso causaba errores en algunos casos y complicaba el código sin necesidad. Ahora vuelven al comportamiento por defecto de lxml: **notarás un pequeño aumento de velocidad en las operaciones que dependen del texto de los elementos, como los selectores**. Si quieres que Scrapling quite los comentarios HTML antes de devolver el texto para evitar la extraña división de texto de lxml/parsel/scrapy, deja el argumento `keep_comments` en True, como está por defecto.

## [v0.2](https://github.com/D4Vinci/Scrapling/releases/tag/v0.2) - 2024-11-11 {#v0.2}

### Qué ha cambiado {#v0.2-what-s-changed}
##### Nuevas funciones {#v0.2-new-features}
1. ¡Llega la función `Fetchers`, con 3 nuevos tipos principales para que Scrapling obtenga páginas por ti con MUCHAS opciones!
    - La clase `Fetcher`, para peticiones HTTP básicas
    - La clase `StealthyFetcher`, un fetcher totalmente sigiloso que usa una [versión modificada de Firefox para navegar con sigilo](https://github.com/daijro/camoufox).
    - La clase `PlayWrightFetcher`, para hacer peticiones con el navegador mediante PlayWright sin modificar, PlayWright con un modo sigiloso creado por mí, navegadores reales por CDP y [NSTBrowser](https://app.nstbrowser.io/r/1vO5e5) con su [docker browserless](https://hub.docker.com/r/nstbrowser/browserless).
2. Se añaden los métodos completamente nuevos `find_all`/`find` para encontrar elementos en la página con facilidad y un poco de magia negra.
3. Se añaden los métodos `filter` y `search` a la clase `Adaptors` para facilitar las operaciones por lotes en grupos de objetos `Adaptor`.
4. Se añaden los métodos `css_first` y `xpath_first` para facilitar el uso.
5. Se añade la nueva clase `TextHandlers`, que permite hacer operaciones por lotes con objetos `TextHandler`, igual que la clase `Adaptors`.
6. Se añaden los métodos `generate_full_css_selector` y `generate_full_xpath_selector`.

##### Correcciones de errores {#v0.2-bugs-squashed}
1. En la clase `Adaptors`, `re_first` devuelve ahora la primera coincidencia entre todos los objetos `Adaptor` que contiene, en lugar de devolver por error los resultados de `re_first` de todos los objetos `Adaptor`.
2. Si seleccionas contenido de texto de los elementos (como con la función CSS `::text`) mediante un método como `.css` o `.xpath`, el objeto `Adaptor` devuelve ahora la clase `TextHandlers` en lugar de una lista de cadenas. Así puedes usar `page.css('something::text').re_first(r'regex_pattern').json()` en lugar de `page.css('something::text')[0].re_first(r'regex_pattern').json()`
3. Los argumentos re/re_first de `Adaptor`/`Adaptors` ahora son coherentes con los de `TextHandler`. Ahora tienes los argumentos `clean_match` y `case_sensitive`.
4. El argumento `auto_match` está activado por defecto al crear `Adaptor`, pero aún debes activarlo al seleccionar elementos si quieres usarlo. (No es un error, sino una decisión de diseño)
5. Se corrigen muchas anotaciones de tipos para mejorar el autocompletado al programar con Scrapling.

##### Mejoras de uso {#v0.2-quality-of-life-changes}
1. Se cambian los nombres de los métodos `css_selector` y `xpath_selector` a `generate_css_selector` y `generate_xpath_selector` para dar más claridad y no interferir con el autocompletado al programar.
2. Se reorganiza la mayor parte del código antiguo en un subpaquete `core`, junto con otras decisiones de diseño para facilitar el mantenimiento futuro.
3. Se reorganiza la carpeta de pruebas y se añaden pruebas de las nuevas funciones. Ahora los entornos de tox se guardan en caché en GitHub para acelerar las pruebas automáticas de cada commit.

## [v0.1.2](https://github.com/D4Vinci/Scrapling/releases/tag/v0.1.2) - 2024-10-16 {#v0.1.2}

**Historial de cambios**:

- Se corrige un error que impedía que el argumento `keep_comments` funcionara como debía.
- Se ajusta la función de texto para eliminar automáticamente los comentarios HTML de los elementos antes de extraer su texto y evitar el comportamiento distinto de Lxml. Por ejemplo:

    ```python
    >>> page = Adaptor('<span>CONDITION: <!-- -->Excellent</span>', keep_comments=True)
    >>> page.css('span::text')
    ['CONDITION: ', 'Excellent']
    ```

    Antes se obtenía este resultado por el comportamiento por defecto de Lxml, pero ahora se devuelve el texto completo 'CONDITION: Excellent'
    Este comportamiento también se conoce en parsel\scrapy, así que quería resolverlo aquí.

- Se corrige un error que impedía eliminar el archivo de base de datos SQLite creado por la biblioteca al ejecutar `pip uninstall scrapling` o un comando similar.

## [v0.1.1](https://github.com/D4Vinci/Scrapling/releases/tag/v0.1.1) - 2024-10-14 {#v0.1.1}

Pequeñas correcciones

## [v0.1](https://github.com/D4Vinci/Scrapling/releases/tag/v0.1) - 2024-10-13 {#v0.1}

**Historial completo de cambios**: <https://github.com/D4Vinci/Scrapling/commits/v0.1>
