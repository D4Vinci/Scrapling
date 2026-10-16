---
title: "Guarda páginas como Markdown, HTML o texto desde la CLI"
description: "Usa scrapling extract para guardar resultados de solicitudes HTTP o del navegador. Filtra con CSS, ajusta las solicitudes y elige el formato de salida."
---

# Guía del comando de extracción de Scrapling {#scrapling-extract-command-guide}

**¡Extrae datos web desde la terminal sin programar!**

El comando `scrapling extract` permite descargar y extraer contenido de sitios web directamente desde la terminal sin escribir código. Es útil para principiantes, investigadores y cualquier persona que necesite obtener datos web con rapidez.

!!! success "Requisitos previos"

    1. Lee la página de [conceptos básicos de los fetchers](../fetching/choosing.md) para entender qué es el [objeto Response](../fetching/choosing.md#response-object) y qué fetcher usar.
    2. Lee la página de [selección de elementos](../parsing/selection.md) para aprender a buscar y extraer elementos de un objeto [Selector](../parsing/main_classes.md#selector)/[Response](../fetching/choosing.md#response-object).
    3. Lee la página de [clases principales](../parsing/main_classes.md) para conocer las propiedades y los métodos que la clase [Response](../fetching/choosing.md#response-object) hereda de [Selector](../parsing/main_classes.md#selector).
    4. Lee al menos una página de la sección de fetchers para las solicitudes que usarás aquí: [solicitudes HTTP](../fetching/static.md) u [obtención con navegador](../fetching/stealthy.md).

## ¿Qué es el grupo de comandos Extract? {#what-is-the-extract-command-group}

Es un conjunto de herramientas sencillas para la terminal que permite:

- **Descargar páginas web** y guardar su contenido en archivos.
- **Convertir HTML a formatos fáciles de leer**, como Markdown, conservarlo como HTML o extraer solo el texto de la página.
- **Usar selectores CSS propios** para extraer partes concretas de la página.
- **Hacer solicitudes HTTP y obtener páginas con navegadores**.
- **Ajustar casi todas las opciones** disponibles desde el código, como encabezados, cookies y proxies, también desde la línea de comandos.

!!! tip "Modo para IA"

    Todos los comandos de extracción admiten la opción `--ai-targeted`. Al activarla, se extrae solo el contenido principal del cuerpo de la página. También se quitan etiquetas que no aportan texto (script, style, noscript, svg), elementos ocultos que podrían usarse para inyectar instrucciones (estilos ocultos en línea, aria-hidden, slots ocultos y etiquetas template), caracteres Unicode de ancho cero y comentarios HTML. En el comando de navegador (`fetch`), también se activa el bloqueo de anuncios. Este modo es útil cuando vas a enviar el resultado a un modelo de IA.

## Inicio rápido {#quick-start}

- **Descargar una página**

    Descarga el contenido de una página como texto limpio y fácil de leer:
    ```bash
    scrapling extract get "https://example.com" page_content.txt
    ```
    Este comando hace una solicitud HTTP GET y guarda el texto de la página en `page_content.txt`.

- **Guardar en otros formatos**

    Elige el formato de salida al cambiar la extensión del archivo:
    ```bash
    # Convert the HTML content to Markdown, then save it to the file (great for documentation)
    scrapling extract get "https://blog.example.com" article.md
    
    # Save the HTML content as it is to the file
    scrapling extract get "https://example.com" page.html
    
    # Save a clean version of the text content of the webpage to the file
    scrapling extract get "https://example.com" content.txt
  
    # Or use the Docker image with something like this:
    docker run -v $(pwd)/output:/output pyd4vinci/scrapling extract get "https://blog.example.com" /output/article.md 
    ```

- **Extraer contenido concreto**

    Todos los comandos pueden usar selectores CSS para extraer partes de la página con `--css-selector` o `-s`, como muestran los ejemplos siguientes.

## Comandos disponibles {#available-commands}

Ejecuta `scrapling extract --help` para ver esta lista de comandos:
```bash
Usage: scrapling extract [OPTIONS] COMMAND [ARGS]...

  Fetch web pages using various fetchers and extract full/selected HTML content as HTML, Markdown, or extract text content.

Options:
  --help  Show this message and exit.

Commands:
  get             Perform a GET request and save the content to a file.
  post            Perform a POST request and save the content to a file.
  put             Perform a PUT request and save the content to a file.
  delete          Perform a DELETE request and save the content to a file.
  fetch           Use StealthyFetcher to fetch content with advanced stealth features.
```

A continuación se explica cada uno.

### Solicitudes HTTP {#http-requests}

1. **Solicitud GET**

    El comando más habitual para descargar contenido web:

    ```bash
    scrapling extract get [URL] [OUTPUT_FILE] [OPTIONS]
    ```

    **Ejemplos:**
    ```bash
    # Basic download
    scrapling extract get "https://news.site.com" news.md
    
    # Download with custom timeout
    scrapling extract get "https://example.com" content.txt --timeout 60
    
    # Extract only specific content using CSS selectors
    scrapling extract get "https://blog.example.com" articles.md --css-selector "article"
   
    # Send a request with cookies
    scrapling extract get "https://scrapling.requestcatcher.com" content.md --cookies "session=abc123; user=john"
   
    # Add user agent
    scrapling extract get "https://api.site.com" data.txt -H "User-Agent: MyBot 1.0"
    
    # Add multiple headers
    scrapling extract get "https://site.com" page.html -H "Accept: text/html" -H "Accept-Language: en-US"
    ```
    Consulta las opciones con `scrapling extract get --help`:
    ```bash
    Usage: scrapling extract get [OPTIONS] URL OUTPUT_FILE
    
      Perform a GET request and save the content to a file.
    
      The output file path can be an HTML file, a Markdown file of the HTML content, or the text content itself. Use file extensions (`.html`/`.md`/`.txt`) respectively.
    
    Options:
      -H, --headers TEXT                             HTTP headers in format "Key: Value" (can be used multiple times)
      --cookies TEXT                                 Cookies string in format "name1=value1;name2=value2"
      --timeout INTEGER                              Request timeout in seconds (default: 30)
      --proxy TEXT                                   Proxy URL in format "http://username:password@host:port"
      -s, --css-selector TEXT                        CSS selector to extract specific content from the page. It returns all matches.
      -p, --params TEXT                              Query parameters in format "key=value" (can be used multiple times)
      --follow-redirects / --no-follow-redirects     Whether to follow redirects (default: True)
      --verify / --no-verify                         Whether to verify SSL certificates (default: True)
      --impersonate TEXT                             Browser to impersonate (e.g., chrome, firefox).
      --stealthy-headers / --no-stealthy-headers     Use stealthy browser headers (default: True)
      --ai-targeted                                  Extract only main content and sanitize hidden elements for AI consumption (default: False)
      --help                                         Show this message and exit.
    
    ```
    Estas opciones funcionan igual en los demás comandos de solicitud, por lo que no hace falta repetir su explicación.

2. **Solicitud POST**

    ```bash
    scrapling extract post [URL] [OUTPUT_FILE] [OPTIONS]
    ```

    **Ejemplos:**
    ```bash
    # Submit form data
    scrapling extract post "https://api.site.com/search" results.html --data "query=python&type=tutorial"
    
    # Send JSON data
    scrapling extract post "https://api.site.com" response.txt --json '{"username": "test", "action": "search"}'
    ```
    Consulta las opciones con `scrapling extract post --help`:
    ```bash
    Usage: scrapling extract post [OPTIONS] URL OUTPUT_FILE
    
      Perform a POST request and save the content to a file.
    
      The output file path can be an HTML file, a Markdown file of the HTML content, or the text content itself. Use file extensions (`.html`/`.md`/`.txt`) respectively.
    
    Options:
      -d, --data TEXT                                Form data to include in the request body (as string, ex: "param1=value1&param2=value2")
      -j, --json TEXT                                JSON data to include in the request body (as string)
      -H, --headers TEXT                             HTTP headers in format "Key: Value" (can be used multiple times)
      --cookies TEXT                                 Cookies string in format "name1=value1;name2=value2"
      --timeout INTEGER                              Request timeout in seconds (default: 30)
      --proxy TEXT                                   Proxy URL in format "http://username:password@host:port"
      -s, --css-selector TEXT                        CSS selector to extract specific content from the page. It returns all matches.
      -p, --params TEXT                              Query parameters in format "key=value" (can be used multiple times)
      --follow-redirects / --no-follow-redirects     Whether to follow redirects (default: True)
      --verify / --no-verify                         Whether to verify SSL certificates (default: True)
      --impersonate TEXT                             Browser to impersonate (e.g., chrome, firefox).
      --stealthy-headers / --no-stealthy-headers     Use stealthy browser headers (default: True)
      --ai-targeted                                  Extract only main content and sanitize hidden elements for AI consumption (default: False)
      --help                                         Show this message and exit.
    
    ```

3. **Solicitud PUT**

    ```bash
    scrapling extract put [URL] [OUTPUT_FILE] [OPTIONS]
    ```

    **Ejemplos:**
    ```bash
    # Send data
    scrapling extract put "https://scrapling.requestcatcher.com/put" results.html --data "update=info" --impersonate "firefox"
    
    # Send JSON data
    scrapling extract put "https://scrapling.requestcatcher.com/put" response.txt --json '{"username": "test", "action": "search"}'
    ```
    Consulta las opciones con `scrapling extract put --help`:
    ```bash
    Usage: scrapling extract put [OPTIONS] URL OUTPUT_FILE
    
      Perform a PUT request and save the content to a file.
    
      The output file path can be an HTML file, a Markdown file of the HTML content, or the text content itself. Use file extensions (`.html`/`.md`/`.txt`) respectively.
    
    Options:
      -d, --data TEXT                                Form data to include in the request body
      -j, --json TEXT                                JSON data to include in the request body (as string)
      -H, --headers TEXT                             HTTP headers in format "Key: Value" (can be used multiple times)
      --cookies TEXT                                 Cookies string in format "name1=value1;name2=value2"
      --timeout INTEGER                              Request timeout in seconds (default: 30)
      --proxy TEXT                                   Proxy URL in format "http://username:password@host:port"
      -s, --css-selector TEXT                        CSS selector to extract specific content from the page. It returns all matches.
      -p, --params TEXT                              Query parameters in format "key=value" (can be used multiple times)
      --follow-redirects / --no-follow-redirects     Whether to follow redirects (default: True)
      --verify / --no-verify                         Whether to verify SSL certificates (default: True)
      --impersonate TEXT                             Browser to impersonate (e.g., chrome, firefox).
      --stealthy-headers / --no-stealthy-headers     Use stealthy browser headers (default: True)
      --ai-targeted                                  Extract only main content and sanitize hidden elements for AI consumption (default: False)
      --help                                         Show this message and exit.
    ```

4. **Solicitud DELETE**

    ```bash
    scrapling extract delete [URL] [OUTPUT_FILE] [OPTIONS]
    ```

    **Ejemplos:**
    ```bash
    # Send data
    scrapling extract delete "https://scrapling.requestcatcher.com/delete" results.html
    
    # Send JSON data
    scrapling extract delete "https://scrapling.requestcatcher.com/" response.txt --impersonate "chrome"
    ```
    Consulta las opciones con `scrapling extract delete --help`:
    ```bash
    Usage: scrapling extract delete [OPTIONS] URL OUTPUT_FILE
    
      Perform a DELETE request and save the content to a file.
    
      The output file path can be an HTML file, a Markdown file of the HTML content, or the text content itself. Use file extensions (`.html`/`.md`/`.txt`) respectively.
    
    Options:
      -H, --headers TEXT                             HTTP headers in format "Key: Value" (can be used multiple times)
      --cookies TEXT                                 Cookies string in format "name1=value1;name2=value2"
      --timeout INTEGER                              Request timeout in seconds (default: 30)
      --proxy TEXT                                   Proxy URL in format "http://username:password@host:port"
      -s, --css-selector TEXT                        CSS selector to extract specific content from the page. It returns all matches.
      -p, --params TEXT                              Query parameters in format "key=value" (can be used multiple times)
      --follow-redirects / --no-follow-redirects     Whether to follow redirects (default: True)
      --verify / --no-verify                         Whether to verify SSL certificates (default: True)
      --impersonate TEXT                             Browser to impersonate (e.g., chrome, firefox).
      --stealthy-headers / --no-stealthy-headers     Use stealthy browser headers (default: True)
      --ai-targeted                                  Extract only main content and sanitize hidden elements for AI consumption (default: False)
      --help                                         Show this message and exit.
    ```

### Obtener páginas con un navegador {#browser-fetching}

Usa `fetch` para páginas con JavaScript, automatización del navegador y sitios protegidos. Ejecuta `StealthyFetcher` con todas las opciones de ocultación disponibles.

```bash
scrapling extract fetch "https://scrapling.requestcatcher.com/" content.md --network-idle
scrapling extract fetch "https://scrapling.requestcatcher.com/" data.txt --wait-selector ".content-loaded"
scrapling extract fetch "https://scrapling.requestcatcher.com/" page.html --no-headless --disable-resources
scrapling extract fetch "https://nopecha.com/demo/cloudflare" data.txt --solve-cloudflare --css-selector "#padded_content a"
scrapling extract fetch "https://site.com" content.md --proxy "http://proxy-server:8080"
```

Usa `--pierce-shadow` para incluir el contenido de Shadow DOM abierto. Está desactivado de forma predeterminada; `--no-pierce-shadow` lo desactiva de forma explícita. Consulta [Shadow DOM](../fetching/stealthy.md#shadow-dom) para ver ejemplos de selectores y sus límites.

```bash
scrapling extract fetch "https://example.com" content.md --pierce-shadow
```

Ejecuta `scrapling extract fetch --help` para ver todas las opciones:

```text
Usage: scrapling extract fetch [OPTIONS] URL OUTPUT_FILE

  Use StealthyFetcher to fetch content with advanced stealth features.

Options:
  --headless / --no-headless                  Run browser in headless mode (default: True)
  --disable-resources / --enable-resources    Drop unnecessary resources for speed boost (default: False)
  --block-webrtc / --allow-webrtc             Block WebRTC entirely (default: False)
  --solve-cloudflare / --no-solve-cloudflare  Solve Cloudflare challenges (default: False)
  --allow-webgl / --block-webgl               Allow WebGL (default: True)
  --pierce-shadow / --no-pierce-shadow        Include open Shadow DOM content (default: False)
  --network-idle / --no-network-idle          Wait for network idle (default: False)
  --real-chrome/--no-real-chrome              If you have a Chrome browser installed on your device, enable this, and the Fetcher will launch an instance of your browser and use it. (default: False)
  --timeout INTEGER                           Timeout in milliseconds (default: 30000)
  --wait INTEGER                              Additional wait time in milliseconds after page load (default: 0)
  -s, --css-selector TEXT                     CSS selector to extract specific content from the page. It returns all matches.
  --wait-selector TEXT                        CSS selector to wait for before proceeding
  --hide-canvas / --show-canvas               Add noise to canvas operations (default: False)
  --locale TEXT                               Specify user locale. Defaults to the system default locale.
  --proxy TEXT                                Proxy URL in format "http://username:password@host:port"
  -H, --extra-headers TEXT                    Extra headers in format "Key: Value" (can be used multiple times)
  --dns-over-https / --no-dns-over-https   Route DNS through Cloudflare's DoH to prevent DNS leaks when using proxies (default: False)
  --block-ads / --no-block-ads               Block requests to known ad and tracker domains (default: False)
  --executable-path TEXT                      Path to a custom Chromium-compatible browser executable. Falls back to the SCRAPLING_EXECUTABLE_PATH environment variable when not set.
  --ai-targeted                              Extract only main content and sanitize hidden elements for AI consumption (default: False)
  --help                                      Show this message and exit.
```

## Cuándo usar cada comando {#when-to-use-each-command}

Si aún no tienes experiencia con la extracción de datos web, estas reglas te ayudarán a elegir:

- Usa **`get`** para sitios sencillos, blogs o artículos de noticias.
- Usa **`fetch`** para páginas con JavaScript, automatización del navegador o sitios protegidos, incluidos los que usan Cloudflare.

## Aspectos legales y éticos {#legal-and-ethical-considerations}

⚠️ **Pautas importantes:**

- **Consulta robots.txt**: Visita `https://website.com/robots.txt` para ver las reglas de rastreo.
- **Respeta los límites de solicitudes**: No sobrecargues los servidores.
- **Condiciones del servicio**: Lee y cumple las condiciones del sitio.
- **Derechos de autor**: Respeta los derechos de propiedad intelectual.
- **Privacidad**: Ten en cuenta las leyes de protección de datos personales.
- **Uso comercial**: Asegúrate de tener permiso para usar los datos con fines comerciales.

---

*¡Que disfrutes extrayendo datos! Recuerda respetar las políticas de los sitios web y cumplir todas las leyes y normas aplicables.*
