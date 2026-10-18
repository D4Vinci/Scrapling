---
title: "Servidor MCP de Scrapling: configuración y extracción de datos"
description: "Conecta un cliente de IA a Scrapling para extraer datos por HTTP o con un navegador. Usa sesiones, inicios de sesión guardados, acciones, filtros e historial de API."
---

# Guía del servidor MCP de Scrapling {#scrapling-mcp-server-guide}

<iframe width="560" height="315" src="https://www.youtube.com/embed/NHwWEiTOoPQ" title="Reproductor de vídeo de YouTube" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>

El **servidor MCP de Scrapling** lleva las funciones de extracción de datos web de Scrapling a tu chatbot o agente de IA. Puedes pedirle que visite sitios, extraiga datos y supere protecciones contra bots mediante una conversación en Claude o en cualquier interfaz compatible con MCP.

## Funciones {#features}

El servidor MCP de Scrapling ofrece dieciséis herramientas para extraer datos web e interactuar con el navegador. Las herramientas de un solo uso obtienen una URL y cierran su propio navegador o cliente. Las herramientas de sesión conservan las cookies y la configuración entre llamadas, para que la IA pueda seguir trabajando en la misma pestaña y consultar el historial de red.

### Herramientas de un solo uso {#one-shot-tools}

#### 🚀 Extracción básica por HTTP {#basic-http-scraping}

- **`make_request`**: Solicitudes HTTP rápidas con cualquier método (GET, POST, PUT, DELETE) e imitación de la huella del navegador. Genera encabezados reales de navegador que coinciden con la versión de TLS, admite HTTP/3 y más.

#### 🔒 Extracción con navegador Stealthy {#stealth-browser-scraping}

- **`browser_fetch_once`**: Ejecuta JavaScript y extrae datos de páginas dinámicas con nuestro navegador Stealthy. Permite modificar la huella del navegador, superar Turnstile e Interstitial de Cloudflare y controlar tanto el navegador como la solicitud.

### Herramientas de sesión {#session-tools}

#### 🔌 Gestión de sesiones {#session-management}

- **`browser_open`**: Crea una sesión persistente de navegador Stealthy que permanece abierta entre llamadas a `browser_fetch`. Así no hace falta abrir un navegador cada vez. Guarda la configuración del navegador y solo devuelve `session_id` y `session_type`. Usa `list_sessions` para ver su configuración efectiva en `settings`, que está vacía en las sesiones CDP.
- **`open_request_session`**: Crea una sesión HTTP persistente sin navegador para usar con `session_make_request`. Conserva cookies, conexiones y la huella del navegador (`impersonate`) entre solicitudes. Solo devuelve `session_id` y `session_type`, con el tipo `static`. Usa `list_sessions` para ver su configuración efectiva en `settings`.
- **`close_session`**: Cierra una sesión persistente, de navegador o de solicitudes, y libera sus recursos.
- **`list_sessions`**: Muestra todas las sesiones activas con sus detalles y su `settings`.

#### Estado del navegador {#browser-state}

- **`browser_save_state`**: Guarda las cookies, el almacenamiento local e IndexedDB en un archivo JSON compatible con Playwright. Así puedes reutilizar el inicio de sesión después de cerrar el navegador. Si el archivo ya existe, se sustituye.
- **`browser_load_state`**: Restaura un archivo guardado en una sesión de navegador abierta, incluso antes de cargar la primera página. Sustituye el estado almacenado actual sin cerrar las pestañas ni cambiar su página. Obtén o recarga la página para usar el inicio de sesión restaurado.

Los archivos de estado se guardan en el equipo donde se ejecuta el servidor MCP. No incluyen `sessionStorage`, las pestañas abiertas ni la configuración del navegador.

#### 🎯 Obtener páginas mediante una sesión {#fetching-through-a-session}

- **`browser_fetch`**: Ejecuta JavaScript y extrae datos de una URL a través de una sesión abierta de navegador Stealthy. Permite modificar la huella del navegador y superar Turnstile e Interstitial de Cloudflare. También puede obtener una vista estructurada de la página con referencias, posiciones y tamaños de los elementos para ayudar a la IA a identificar controles y planear acciones del ratón.
- **`session_make_request`**: Hace solicitudes HTTP rápidas con cualquier método (GET, POST, PUT, DELETE), imitación de la huella del navegador, encabezados acordes y soporte para HTTP/3. Reutiliza cookies, conexiones y la huella del navegador mediante una sesión abierta con `open_request_session`.

#### 📸 Capturas de pantalla {#screenshots}

- **`browser_screenshot`**: Captura la página actual o un elemento en PNG o JPEG sin recargarla. Sirve para revisar campos rellenados, menús abiertos, gráficos o tarjetas de resultados. Al capturar un solo elemento, se reduce el contenido que no interesa. Permite capturar el área visible, la página completa o un elemento, y ajustar la calidad de JPEG. Devuelve un bloque de imagen real que el modelo puede ver directamente.

#### Contenido de la página actual {#current-page-content}

- **`browser_extract`**: Lee la página actual o un elemento como vista estructurada para IA, HTML, Markdown o texto, sin recargarla. Extrae resultados después de rellenar formularios o cargar más contenido. Las vistas incluyen roles, nombres, referencias, posiciones y tamaños de los elementos para acciones posteriores. La búsqueda con expresiones regulares devuelve las líneas que coinciden, con el contexto cercano y los nodos padre.

#### Acciones del navegador {#browser-actions}

- **`browser_actions`**: Encadena acciones del ratón, entrada de texto, atajos de teclado, respuestas a diálogos y esperas en una sola llamada. Acepta o descarta alertas y confirmaciones del navegador, o introduce texto en sus diálogos. Por ejemplo, rellena un campo de búsqueda, envía la consulta, espera los resultados y abre uno. La IA puede agrupar los pasos que ya conoce y obtener vistas de la página por separado cuando necesita revisar un cambio. Así no es necesario volver al agente entre un paso y el siguiente, lo que ayuda con menús que desaparecen pronto y otros controles que necesitan una acción rápida a continuación.

    Muestra menús y ayudas al pasar el ratón, pulsa botones y enlaces, o mueve el ratón sobre un panel anidado para desplazarlo en vertical u horizontal. Los movimientos y clics admiten selectores, referencias de la vista estructurada o coordenadas. Si el destino es un elemento, esperan y lo desplazan hasta dejarlo visible de forma automática. Admiten movimientos por coordenadas en varios pasos, clic izquierdo, derecho y central, además de doble clic.

    Localiza campos en cualquier parte de la página mediante selectores o referencias. Rellena texto, marca o desmarca casillas, selecciona botones de opción y elige una o varias opciones de listas desplegables nativas por su etiqueta visible. Puedes sustituir el texto, borrarlo o continuar desde la posición del cursor. Los atajos de teclado permiten seleccionar y borrar texto, cambiar el foco, enviar formularios o cerrar menús. El modo lento escribe un carácter cada vez, con pausas aleatorias entre caracteres y entre todas las acciones.

    Espera a que aparezcan resultados, desaparezcan capas de carga o se produzcan eventos de carga de la página antes de la siguiente acción. También admite pausas fijas y esperar a que se calme la actividad de red.

#### JavaScript {#javascript}

- **`browser_evaluate`**: Ejecuta JavaScript en la página actual para extraer datos a medida, hacer cálculos y realizar tareas propias de la página. La IA puede reunir datos de varios elementos, leer el estado de la aplicación o actualizar el contenido. Admite scripts asíncronos y devuelve sus resultados como JSON.

#### Historial de red {#network-history}

- **`browser_network_requests`**: Busca solicitudes completadas entre pestañas, cargas de página y acciones del navegador. Descubre las llamadas a API que hay detrás de los datos de una página, revisa errores HTTP y sigue redirecciones guardadas. Los recursos estáticos se ocultan de forma predeterminada para reducir el resultado. Devuelve los detalles como JSON, con paginación para historiales largos.
- **`browser_network_request`**: Consulta el resumen, los encabezados, los datos enviados o el cuerpo de texto de la respuesta de una solicitud registrada. Devuelve la parte elegida completa como JSON estructurado, sin cargar la página ni repetir la solicitud. Las respuestas guardadas siguen disponibles después de cambiar de página. Los límites de tamaño mantienen acotado el historial; una nota explica los cuerpos que no son texto, son demasiado grandes o no se pueden leer. Lee los datos que necesites antes de cerrar la sesión MCP.

Los cuerpos de respuesta solo se leen y guardan para valores de `Content-Type` de texto compatibles, como HTML, JSON, XML o JavaScript. Para tipos binarios, ausentes o no reconocidos, se conservan los metadatos y encabezados de la solicitud, pero no se lee ni guarda su cuerpo. El navegador sigue cargando los recursos con normalidad.

Solo se guardan las solicitudes completadas, incluidas las respuestas HTTP 4xx y 5xx. Se omiten las solicitudes fallidas o pendientes. Las entradas aparecen cuando termina la captura; consultar el historial o cerrar la sesión no espera a que terminen. Pueden omitirse capturas que sigan en curso al navegar o cerrar. Los bytes guardados proceden del navegador y pueden ser distintos de los del servidor. El texto registrado usa la decodificación UTF-8 de Playwright cuando es válida y, en caso contrario, la codificación declarada.

### Shadow DOM {#shadow-dom}

Define `pierce_shadow=true` en `browser_fetch_once` o en cada llamada a `browser_fetch` para incluir contenido de Shadow DOM abierto. Su valor predeterminado es `false`. Consulta [Shadow DOM](../fetching/stealthy.md#shadow-dom) para ver ejemplos de selectores y sus límites.

Los selectores del navegador también permiten localizar elementos dentro de un Shadow DOM cerrado e interactuar con ellos.

### Funciones principales {#key-capabilities}

- **Extracción de contenido**: Convierte páginas o elementos a Markdown o HTML, o extrae una versión limpia de su texto.
- **Selectores CSS**: Usa el motor de Scrapling para elegir elementos concretos antes de pasar el contenido a la IA.
- **Protección contra bots**: Maneja Turnstile, Interstitial y otras protecciones de Cloudflare.
- **Proxies**: Usa proxies para ocultar tu dirección y elegir la ubicación de las solicitudes.
- **Imitación del navegador**: Imita navegadores reales mediante la huella TLS, encabezados que coinciden con su versión y otras opciones.
- **Sesiones persistentes**: Reutiliza sesiones de navegador entre solicitudes para mejorar el rendimiento.
- **Bloqueo de anuncios**: Todas las herramientas de navegador bloquean automáticamente solicitudes a unos 3.500 dominios conocidos de anuncios y seguimiento. Esto ahorra tokens y acelera la carga.
- **Protección contra inyección de instrucciones**: Elimina automáticamente contenido oculto que podría usarse para atacar al modelo: elementos ocultos con estilos en línea, aria-hidden, slots ocultos, caracteres de ancho cero, comentarios HTML y etiquetas template.

## Instalación {#installation}

Instala Scrapling con soporte para MCP y comprueba que también estén instaladas las dependencias del navegador.

```bash
# Install Scrapling with MCP server dependencies
pip install "scrapling[ai]"

# Install browser dependencies
scrapling install
```

También puedes usar la imagen Docker directamente desde su registro:
```bash
docker pull pyd4vinci/scrapling
```
O descargarla desde el registro de GitHub:
```bash
docker pull ghcr.io/d4vinci/scrapling:latest
```

## Configurar el servidor MCP {#setting-up-the-mcp-server}

Aquí explicamos cómo añadir el servidor MCP de Scrapling a [Claude Desktop](https://claude.ai/download) y [Claude Code](https://www.anthropic.com/claude-code). Los mismos pasos generales sirven para otros chatbots compatibles con MCP:

!!! note "Nota"
    El comando `scrapling-mcp` de los ejemplos se añadió en la versión 0.4.13 como atajo de `scrapling mcp`. Facilita añadir Scrapling a registros y clientes MCP que esperan un único comando. Si usas una versión anterior, usa el comando `scrapling` con `mcp` como primer argumento.

### Claude Desktop {#claude-desktop}

1. Abre Claude Desktop.
2. Pulsa el menú (☰) de la esquina superior izquierda y ve a Settings → Developer → Edit Config.
3. Añade la configuración del servidor MCP de Scrapling:
```json
"ScraplingServer": {
  "command": "scrapling-mcp"
}
```
Si es el primer servidor MCP que añades, usa este contenido para el archivo:
```json
{
  "mcpServers": {
    "ScraplingServer": {
      "command": "scrapling-mcp"
    }
  }
}
```
Según el [artículo oficial](https://modelcontextprotocol.io/quickstart/user), esta acción crea un archivo de configuración si aún no existe o abre el que ya tienes. El archivo está en:

1. **MacOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
2. **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

Para asegurarte de que funciona, usa la ruta completa del ejecutable `scrapling-mcp`. Puedes encontrarla con:

1. **MacOS**: `which scrapling-mcp`
2. **Windows**: `where scrapling-mcp`

En mi Mac, devolvió `/Users/<MyUsername>/.venv/bin/scrapling-mcp`, así que terminé usando esta configuración:
```json
{
  "mcpServers": {
    "ScraplingServer": {
      "command": "/Users/<MyUsername>/.venv/bin/scrapling-mcp"
    }
  }
}
```
#### Docker {#docker}

Si usas la imagen Docker, la configuración sería parecida a esta:
```json
{
  "mcpServers": {
    "ScraplingServer": {
      "command": "docker",
      "args": [
        "run", "-i", "--rm", "pyd4vinci/scrapling", "mcp"
      ]
    }
  }
}
```

El mismo enfoque sirve para [Cursor](https://cursor.com/docs/context/mcp), [WindSurf](https://windsurf.com/university/tutorials/configuring-first-mcp-server) y otros clientes.

### Claude Code {#claude-code}

Con [Claude Code](https://www.anthropic.com/claude-code) es más sencillo:

```bash
claude mcp add ScraplingServer "/Users/<MyUsername>/.venv/bin/scrapling-mcp"
```
Para obtener la ruta del ejecutable de Scrapling:

1. **MacOS**: `which scrapling-mcp`
2. **Windows**: `where scrapling-mcp`

Consulta el artículo de Anthropic sobre [cómo añadir servidores MCP a Claude Code](https://docs.anthropic.com/en/docs/claude-code/mcp#option-1%3A-add-a-local-stdio-server) para ver más detalles.

Después de añadir el servidor, cierra por completo y vuelve a abrir la aplicación. En Claude Desktop, deberías ver el indicador de servidor MCP (🔧) en la esquina inferior derecha del campo de chat, o `ScraplingServer` en el menú `Search and tools` de ese campo.

### Ejecutable de navegador personalizado {#custom-browser-executable}

Las herramientas `browser_fetch_once` y `browser_open` pueden usar un ejecutable de navegador compatible con Chromium en lugar del Chromium incluido. Esto resulta útil si usas versiones propias del navegador o motores ligeros.

Para definirlo una sola vez para todo el servidor MCP, pasa la ruta del ejecutable al iniciar el servidor:

```bash
scrapling-mcp --executable-path "/path/to/chromium"
```

En la configuración de Claude Desktop, añade la opción a los argumentos del servidor:

```json
{
  "mcpServers": {
    "ScraplingServer": {
      "command": "/Users/<MyUsername>/.venv/bin/scrapling-mcp",
      "args": [
        "--executable-path",
        "/path/to/chromium"
      ]
    }
  }
}
```

También puedes definir la variable de entorno `SCRAPLING_EXECUTABLE_PATH` antes de iniciar el servidor. La IA aún puede elegir otro ejecutable para una obtención con `browser_fetch_once` o al abrir una sesión con `browser_open`.

### Conectar con navegadores remotos {#connecting-to-remote-browsers}

`browser_open` no necesita iniciar un navegador local. Si le pasas una URL de CDP, se conecta a un navegador que ya está abierto mediante el [Chrome DevTools Protocol](https://chromedevtools.github.io/devtools-protocol/). Puede estar en el mismo equipo, en otro o en un servicio de navegadores gestionados:
```
Open a stealthy browser session on wss://cdp.provider.example/session/abc123, then use it to scrape the product details from https://shop.example.com. Close the session when you're done.
```
El `session_id` que recibes se usa como siempre con `browser_fetch`, `browser_extract`, `browser_actions`, `browser_evaluate`, `browser_screenshot`, `browser_network_requests`, `browser_network_request`, `browser_save_state` y `browser_load_state`.

La URL puede ser un endpoint WebSocket (`ws://`/`wss://`), como los que entregan los servicios de navegadores, o el endpoint HTTP de un navegador que hayas iniciado con el puerto de depuración remota activado:
```commandline
chrome --remote-debugging-port=9222
```
En ese caso, conéctate con `cdp_url="http://localhost:9222"`, o con la dirección del equipo si el navegador está en otro lugar.

!!! note "Notas"

    * Como el navegador ya está abierto, las sesiones CDP ignoran las opciones que solo se aplican al iniciarlo: `headless`, `real_chrome` y `executable_path`, incluida la opción predeterminada del servidor descrita antes.<br/>
    * Las demás opciones siguen funcionando (`locale`, `useragent`, `proxy`, `cookies`, `timezone_id`, etc.), porque cada sesión crea su propio contexto en el navegador remoto.

### Streamable HTTP {#streamable-http}

Desde la versión 0.3.6, el servidor MCP puede usar el transporte 'Streamable HTTP' en lugar del transporte tradicional 'stdio'.

En vez de usar este comando para 'stdio':
```bash
scrapling-mcp
```
Usa el siguiente para activar 'Streamable HTTP':
```bash
scrapling-mcp --http
```
De forma predeterminada, el servidor escucha en '127.0.0.1' y en el puerto 8000. Puedes cambiar ambos valores:
```bash
scrapling-mcp --http --host '0.0.0.0' --port 8000
```
La configuración predeterminada solo acepta conexiones del mismo equipo. Usa `--host '0.0.0.0'` si quieres que se pueda acceder al servidor desde la red. Esta opción es independiente de la autenticación que se explica más abajo.

Si ejecutas 'Streamable HTTP' dentro de Docker, debes usar '0.0.0.0' y definir un token. De lo contrario, el puerto publicado no podrá llegar al servidor, porque '127.0.0.1' del contenedor solo es visible desde dentro:
```bash
docker run -p 8000:8000 -e SCRAPLING_MCP_AUTH_TOKEN="<your-token>" pyd4vinci/scrapling mcp --http --host '0.0.0.0'
```

### Autenticación {#authentication}

Solo el programa que inicia el servidor puede acceder al transporte 'stdio'. En cambio, con 'Streamable HTTP', cualquiera que pueda llegar al puerto puede usar todas las herramientas. Eso incluye solicitar cualquier URL desde el equipo donde se ejecuta el servidor. Por eso, 'Streamable HTTP' requiere autenticación: `--http` por sí solo no inicia el servidor y pide un token:
```bash
scrapling-mcp --http --auth-token "$(openssl rand -hex 32)"
```
Los clientes deben enviar ese token en un encabezado `Authorization`. Las solicitudes que no lo incluyan se rechazan con un `401`:
```json
{
  "mcpServers": {
    "ScraplingServer": {
      "url": "https://your-server.example.com/mcp",
      "headers": {
        "Authorization": "Bearer <your-token>"
      }
    }
  }
}
```
Si pasas el token por la línea de comandos, queda en el historial del shell y en la lista de procesos. Por eso, es mejor usar la variable de entorno `SCRAPLING_MCP_AUTH_TOKEN`:
```bash
export SCRAPLING_MCP_AUTH_TOKEN="<your-token>"
scrapling-mcp --http
```
Si necesitas un servidor sin autenticación, por ejemplo para hacer pruebas locales en '127.0.0.1', debes indicarlo con `--no-auth`:
```bash
scrapling-mcp --http --no-auth
```
Combinar `--no-auth` con `--host '0.0.0.0'` permite usar todas las herramientas a cualquiera que tenga acceso al puerto. Evita esa combinación fuera de una red de confianza.

Si el servidor escucha en una dirección pública, también debes indicar qué nombres de host acepta. Esto activa la protección contra ataques de DNS rebinding, en los que una página que visitas intenta comunicarse con tu servidor. Puedes repetir la opción:
```bash
scrapling-mcp --http --allowed-host 'your-server.example.com:8000'
```

!!! note "Notas"

    * La autenticación solo se aplica a 'Streamable HTTP'. Con 'stdio' se ignora y el servidor registra una advertencia.<br/>
    * HTTP sin cifrado envía el token como texto legible. Antes de exponer el servidor a Internet, colócalo detrás de un proxy inverso que termine la conexión TLS.<br/>
    * Se usa una única clave compartida, no credenciales distintas por cliente. Todos los clientes usan el mismo token y hay que reiniciar el servidor para cambiarlo.<br/>
    * Si inicias el servidor con `--http --no-auth`, se registra una advertencia de que no hay autenticación.<br/>
    * Si pasas `--auth-token` y `--no-auth` a la vez, se conserva el token y el servidor mantiene la autenticación.

## Ejemplos {#examples}

Estos son algunos de los prompts que usamos para probar el servidor MCP. Seguro que se te ocurren otros mejores :)

Iremos de las instrucciones más sencillas a las más complejas. Los ejemplos usan Claude Desktop, pero el mismo enfoque sirve para los demás clientes.

1. **Extracción básica de datos web**

    Extrae el contenido principal de una página como Markdown:

    ```
    Scrape the main content from https://example.com and convert it to markdown format.
    ```

    Claude puede usar `make_request` para obtener la página y devolver contenido limpio y fácil de leer. Las solicitudes HTTP tienen tres intentos de forma predeterminada, con un segundo de espera entre ellos. Si la página necesita JavaScript o bloquea las solicitudes HTTP, la IA puede usar `browser_fetch_once`. Ambas herramientas cierran sus propios recursos al terminar la llamada.

    Una versión más precisa del mismo prompt sería:
    ```
    Use regular requests to scrape the main content from https://example.com and convert it to markdown format.
    ```
    Así le dices a Claude qué herramienta usar y no tiene que adivinarlo. A veces empieza con solicitudes normales y otras elige un navegador sin una razón clara. Como regla general, indica qué herramienta debe usar para ahorrar tiempo y dinero y obtener resultados constantes.

2. **Extracción de datos concretos**

    Extrae elementos específicos con selectores CSS:

    ```
    Get all product titles from https://shop.example.com using the CSS selector '.product-title'. If the request fails, retry up to 5 times every 10 seconds.
    ```

    El servidor extrae solo los elementos que coinciden con el selector y los devuelve en una lista estructurada. En el ejemplo pedí hasta cinco intentos por si el sitio tiene problemas de conexión, aunque el valor predeterminado suele bastar.

3. **Recopilar datos de tiendas en línea**

    Este prompt es un poco más complejo:
    ```
    Open a stealthy browser session and visit these e-commerce URLs one at a time:
    - https://shop1.com/product-a
    - https://shop2.com/product-b  
    - https://shop3.com/product-c
    
    Get the product names, prices, and descriptions from each page. Close the session when done.
    ```

    Claude puede reutilizar una sesión de navegador, llamar a `browser_fetch` para cada URL en orden y después analizar los datos extraídos.

4. **Un proceso más avanzado**

    Supongamos que quiero obtener todos los juegos de acción de la primera página de la tienda de PlayStation. Puedo usar este prompt:
    ```
    Extract the URLs of all games on this page, then visit each game in order and return a list of all action games: https://store.playstation.com/en-us/pages/browse
    ```
    Pide a la IA que reutilice una sesión HTTP para evitar abrir un navegador cuando los datos están disponibles con solicitudes normales:
    ```
    Open an HTTP session, extract the URLs of all games on this page, then fetch each game in order and return a list of all action games. Close the session when done: https://store.playstation.com/en-us/pages/browse
    ```
    Si sabes escribir selectores CSS, también puedes limitar el contenido antes de que lo lea la IA:
    ```
    Use an HTTP session to extract the URLs of all games on the page below, then fetch each game in order and return a list of all action games.
    The selector for games in the first page is `[href*="/concept/"]` and the selector for the genre in each game page is `[data-qa="gameInfo#releaseInformation#genre-value"]`.
    Close the session when done.

    URL: https://store.playstation.com/en-us/pages/browse
    ```

5. **Obtener datos de un sitio protegido por Cloudflare**

    Si crees que el sitio usa Cloudflare, díselo a Claude para que no tenga que descubrirlo por su cuenta.
    ```
    What's the price of this product? Be cautious, as it utilizes Cloudflare's Turnstile protection. Make the browser visible while you work.

    https://ao.com/product/oo101uk-ninja-woodfire-outdoor-pizza-oven-brown-99357-685.aspx
    ```

6. **Un proceso largo**

    Puedes usar un prompt como este:
    ```
    Extract all product URLs for the following category, then return the prices and details for the first 3 products.
    
    https://www.arnotts.ie/furniture/bedroom/bed-frames/
    ```
    Pero sería mejor este:
    ```
    Go to the following category URL and extract all product URLs using the CSS selector "a". Then, reuse the session to fetch the first 3 product pages in order and extract each product’s price and details. Close the session when done.
    
    Keep the output in markdown format to reduce irrelevant content.
    
    Category URL:
    https://www.arnotts.ie/furniture/bedroom/bed-frames/
    ```

7. **Usar sesiones persistentes**

    Si extraes datos de varias páginas del mismo sitio, usa una sesión de navegador persistente para evitar abrir un navegador en cada solicitud:
    ```
    Open a stealthy browser session, then use it to scrape the main details from the first 5 product pages on https://shop.example.com. Close the session when you're done.
    ```
    Claude usa `browser_open` para crear un navegador persistente, llama a `browser_fetch` para cada página de producto mediante esa sesión y termina con `close_session`. Esto es mucho más rápido que abrir un navegador para cada página.

    !!! danger "Peligro"

        ¡Cierra siempre las sesiones persistentes al terminar! Si no lo haces, seguirán abiertas.

8. **Usar una sesión persistente en un proceso largo**

    Otro ejemplo largo que hace pensar a Claude:

    ```
    Use Scrapling MCP to do the following in this order:

    1. Open a stealthy browser session with headless mode off.
    2. Go to this page and collect the number of stars: https://github.com/D4Vinci/Scrapling
    3. From the README, get the URL that shows the number of downloads and go to it.
    4. Get the number of downloads and the top 3 countries from the graph.
    5. Prepare a report with the results.
    6. Close the browser.
    ```

Y así sucesivamente. Aquí, tu creatividad es lo que cuenta.

## Buenas prácticas {#best-practices}

Estos consejos técnicos te ayudarán a usar el servidor.

### 1. Elegir la herramienta adecuada {#1-choose-the-right-tool}

- **`make_request`**: Solicitudes HTTP rápidas para una sola página o llamada a una API.
- **`browser_fetch_once`**: Una página dinámica o con JavaScript, o un sitio protegido, incluido Cloudflare.
- **Herramientas de sesión**: Solicitudes relacionadas, acciones del navegador, capturas de pantalla e historial de red.

### 2. Mejorar el rendimiento {#2-optimize-performance}

- Reutiliza una sesión y obtén cada URL en orden.
- Desactiva los recursos que no necesitas.
- Define tiempos de espera adecuados.
- Usa selectores CSS para extraer solo lo que buscas.

### 3. Manejar contenido dinámico {#3-handle-dynamic-content}

- Usa `network_idle` para aplicaciones de una sola página (SPA).
- Define `wait_selector` para esperar elementos concretos.
- Aumenta el tiempo de espera en sitios que cargan despacio.

### 4. Calidad de los datos {#4-data-quality}

- Usa `main_content_only=true` para elegir y limpiar el cuerpo de la página.
- Elige un `extraction_type` adecuado para tu tarea.

### 5. Protección contra inyección de instrucciones {#5-prompt-injection-protection}

El servidor MCP limpia automáticamente el contenido extraído cuando `main_content_only` está activado, como ocurre de forma predeterminada. Quita el contenido oculto que un sitio malicioso podría usar para introducir instrucciones en el contexto de la IA:

- **Estilos ocultos en línea**: `display:none`, `visibility:hidden` y valores cero de opacidad, tamaño de fuente, altura, anchura, altura máxima y anchura máxima.
- **Elementos ocultos por accesibilidad**: `aria-hidden="true"`.
- **Etiquetas de plantilla y slots ocultos**: Elementos `<template>` y `<slot hidden>`.
- **Comentarios HTML**: `<!-- ... -->`.
- **Caracteres de ancho cero**: Caracteres Unicode invisibles, como los espacios de ancho cero.

Esta protección se aplica automáticamente al extraer HTML, Markdown o texto. Mantén `main_content_only=true`, el valor predeterminado, para obtener la máxima protección.

### 6. Gestionar sesiones {#6-manage-sessions}

- Usa `make_request` o `browser_fetch_once` para obtener una página de forma independiente. Cierran sus propios recursos y no dejan una sesión abierta para llamadas posteriores.
- Usa `browser_open` para crear una sesión persistente cuando trabajes con varias páginas. Después, llama a `browser_fetch` para cada página mediante esa sesión.
- Para varias solicitudes HTTP sin navegador, usa `open_request_session` y llama a `session_make_request` para cada una. Conserva cookies, conexiones y la huella del navegador (`impersonate`) entre llamadas.
- Las sesiones conservan la configuración definida al abrirlas: headless, locale, cookies y opciones de ocultación para navegadores; `impersonate` y `proxy` para sesiones HTTP. Las opciones de cada solicitud, como timeout, wait_selector, network_idle o solve_cloudflare, se pasan a `browser_fetch`/`session_make_request` en cada llamada. Sus valores predeterminados aparecen en los esquemas de las herramientas.
- `browser_fetch` puede resolver desafíos de Cloudflare mediante la sesión abierta de navegador Stealthy.
- Cierra siempre las sesiones con `close_session` al terminar para liberar recursos.
- Usa `list_sessions` para comprobar qué sesiones siguen activas y consultar el `settings` con el que se creó cada una. Se devuelve al agente de IA y está vacío en las sesiones CDP.
- Pasa un `session_id` propio a las herramientas que abren sesiones para darles nombres claros, como `"search"` o `"checkout"`, en lugar del valor hexadecimal aleatorio. Si el identificador ya está en uso, generan un error para que puedas detectar el conflicto desde el principio.

### 7. Capturas de pantalla {#7-capturing-screenshots}

- `browser_screenshot` captura la página ya abierta con `browser_fetch` en una sesión de navegador Stealthy. No la recarga, por lo que la IA puede revisar campos rellenados, menús abiertos y otros resultados de sus acciones.
- La imagen se devuelve como un bloque `ImageContent` real para que el modelo vea la página directamente.
- Captura el área visible o la página completa, incluido el contenido que queda fuera de la pantalla.
- Captura un campo, gráfico, tarjeta o resultado para revisarlo sin tanto contenido alrededor. La captura de un elemento puede desplazar la página hasta mostrarlo.
- Elige PNG para imágenes sin pérdida o JPEG con calidad ajustable para reducir el tamaño.
- La IA puede usar `browser_actions` para esperar al contenido o terminar las acciones antes de capturar.

## Aspectos legales y éticos {#legal-and-ethical-considerations}

⚠️ **Pautas importantes:**

- **Consulta robots.txt**: Visita `https://website.com/robots.txt` para ver las reglas de rastreo.
- **Respeta los límites de solicitudes**: No sobrecargues los servidores.
- **Condiciones del servicio**: Lee y cumple las condiciones del sitio.
- **Derechos de autor**: Respeta los derechos de propiedad intelectual.
- **Privacidad**: Ten en cuenta las leyes de protección de datos personales.
- **Uso comercial**: Asegúrate de tener permiso para usar los datos con fines comerciales.

---

*Creado con ❤️ por el equipo de Scrapling. ¡Disfruta extrayendo datos!*
