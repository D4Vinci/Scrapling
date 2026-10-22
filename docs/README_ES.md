<!-- mcp-name: io.github.D4Vinci/Scrapling -->

<h1 align="center">
    <a href="https://scrapling.readthedocs.io/es/latest/">
        <picture>
          <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/docs/assets/cover_dark.svg?sanitize=true">
          <img alt="Scrapling Poster" src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/docs/assets/cover_light.svg?sanitize=true">
        </picture>
    </a>
    <br>
    <small>Extrae datos de la web moderna de forma sencilla</small>
</h1>

<p align="center">
    <a href="https://github.com/D4Vinci/Scrapling/actions/workflows/tests.yml" alt="Tests">
        <img alt="Tests" src="https://github.com/D4Vinci/Scrapling/actions/workflows/tests.yml/badge.svg"></a>
    <a href="https://badge.fury.io/py/Scrapling" alt="PyPI version">
        <img alt="PyPI version" src="https://badge.fury.io/py/Scrapling.svg"></a>
    <a href="https://hub.docker.com/r/pyd4vinci/scrapling" target="_blank">
        <img alt="Docker Pulls" src="https://img.shields.io/docker/pulls/pyd4vinci/scrapling?labelColor=%20%23FDB062&logo=Docker&labelColor=%20%23528bff"></a>
    <a href="https://clickpy.clickhouse.com/dashboard/scrapling" rel="nofollow"><img src="https://img.shields.io/pypi/dm/scrapling" alt="PyPI package downloads"></a>
    <a href="https://scrapling.readthedocs.io/es/latest/ai/agent-skill.html" alt="AI Agent Skill">
        <img alt="Static Badge" src="https://img.shields.io/badge/Skill-black?style=flat&label=Agent&link=https%3A%2F%2Fscrapling.readthedocs.io%2Fes%2Flatest%2Fai%2Fagent-skill.html"></a>
    <a href="https://clawhub.ai/D4Vinci/scrapling-official" alt="OpenClaw Skill">
        <img alt="OpenClaw Skill" src="https://img.shields.io/badge/Clawhub-darkred?style=flat&label=OpenClaw&link=https%3A%2F%2Fclawhub.ai%2FD4Vinci%2Fscrapling-official"></a>
    <br/>
    <a href="https://discord.gg/EMgGbDceNQ" alt="Discord" target="_blank">
      <img alt="Discord" src="https://img.shields.io/discord/1360786381042880532?style=social&logo=discord&link=https%3A%2F%2Fdiscord.gg%2FEMgGbDceNQ">
    </a>
    <a href="https://x.com/Scrapling_dev" alt="X (formerly Twitter)">
      <img alt="X (formerly Twitter) Follow" src="https://img.shields.io/twitter/follow/Scrapling_dev?style=social&logo=x&link=https%3A%2F%2Fx.com%2FScrapling_dev">
    </a>
    <br/>
    <a href="https://pypi.org/project/scrapling/" alt="Supported Python versions">
        <img alt="Supported Python versions" src="https://img.shields.io/pypi/pyversions/scrapling.svg"></a>
</p>

<p align="center">
    <a href="https://scrapling.readthedocs.io/es/latest/parsing/selection.html"><strong>Métodos de selección</strong></a>
    &middot;
    <a href="https://scrapling.readthedocs.io/es/latest/fetching/choosing.html"><strong>Elegir un fetcher</strong></a>
    &middot;
    <a href="https://scrapling.readthedocs.io/es/latest/spiders/architecture.html"><strong>Spiders</strong></a>
    &middot;
    <a href="https://scrapling.readthedocs.io/es/latest/spiders/proxy-blocking.html"><strong>Rotación de proxy</strong></a>
    &middot;
    <a href="https://scrapling.readthedocs.io/es/latest/cli/overview.html"><strong>CLI</strong></a>
    &middot;
    <a href="https://scrapling.readthedocs.io/es/latest/ai/mcp-server.html"><strong>Servidor MCP</strong></a>
</p>

Scrapling es un framework de web scraping para Python. Reúne solicitudes HTTP rápidas, navegadores sigilosos, análisis de páginas y rastreo concurrente en una sola biblioteca.

Extrae datos de páginas estáticas, ejecuta JavaScript, interactúa con sitios web y accede a las API que usan. Crea crawlers con sesiones reutilizables, rotación de proxies, reintentos automáticos, pausa y reanudación, y exportación de datos integrada.

Úsalo desde Python, la terminal o tu agente de IA mediante el servidor MCP y Agent Skill. Scrapling cubre todo el proceso, desde extraer unos campos hasta guardar un sitio completo como archivos Markdown limpios.

## Qué puedes hacer con Scrapling

- **[Obtener páginas e interactuar](https://scrapling.readthedocs.io/es/latest/fetching/choosing.html)**: Solicitudes HTTP rápidas, navegadores sigilosos, ejecución de JavaScript, gestión de Cloudflare Turnstile e Interstitial, sesiones persistentes y captura de respuestas de API en segundo plano.
- **[Analizar y extraer](https://scrapling.readthedocs.io/es/latest/parsing/selection.html)**: Búsqueda con CSS, XPath, texto y expresiones regulares, seguimiento de elementos cuando cambia la página, búsqueda de elementos similares y salida en Markdown limpio.
- **[Rastrear y exportar](https://scrapling.readthedocs.io/es/latest/spiders/getting-started.html)**: Spiders concurrentes, rotación de proxies, reintentos, AutoThrottle, pausa y reanudación, resultados en streaming, plantillas listas para usar y exportación a JSON, JSONL, CSV y XML.
- **[Extraer datos con IA o desde la terminal](https://scrapling.readthedocs.io/es/latest/ai/mcp-server.html)**: Un servidor MCP para que los agentes de IA naveguen y extraigan datos, un Agent Skill, comandos CLI y una consola interactiva.

Empieza con una sola página:

```python
from scrapling.fetchers import Fetcher

page = Fetcher.get('https://quotes.toscrape.com/')
quotes = page.css('.quote .text::text').getall()
print(quotes)
```

O escala con un Spider:

```python
from scrapling.spiders import Spider, Response

class QuotesSpider(Spider):
    name = "quotes"
    start_urls = ["https://quotes.toscrape.com/"]

    async def parse(self, response: Response):
        for quote in response.css('.quote'):
            yield {
                "text": quote.css('.text::text').get(),
                "author": quote.css('.author::text').get(),
            }

result = QuotesSpider().start()
print(len(result.items))
result.items.to_json("quotes.json")
```

Imprime `10` y guarda las citas y sus autores en `quotes.json`.

<p align="center">
    <a href="https://dataimpulse.com/?utm_source=scrapling&utm_medium=banner&utm_campaign=scrapling" target="_blank" style="display:flex; justify-content:center; padding:4px 0;">
        <img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/DataImpulse.png" alt="At DataImpulse, we specialize in developing custom proxy services for your business. Make requests from anywhere, collect data, and enjoy fast connections with our premium proxies." style="max-height:60px;">
    </a>
</p>

# Patrocinadores Platino
<table>
  <tr>
    <td width="200">
      <a href="https://go.nodemaven.com/scraplingoctober" target="_blank" title="Proxies with the Highest IP Scores">
        <img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/NodeMaven.jpg" width="240" height="100">
      </a>
    </td>
    <td>
    <a href="https://go.nodemaven.com/scraplingoctober" target="_blank">NodeMaven</a> - el proveedor de proxies más eficiente para Web Scraping y automatización, con la mayor calidad de IP del mercado. Usa el código SCRAPLING35 para obtener un 35% de descuento.
    </td>
  </tr>
  <tr>
    <td width="200">
      <a href="https://hypersolutions.co/?utm_source=github&utm_medium=readme&utm_campaign=scrapling" target="_blank" title="Bot Protection Bypass API for Akamai, DataDome, Incapsula & Kasada">
        <img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/HyperSolutions.png">
      </a>
    </td>
    <td> Scrapling maneja Cloudflare Turnstile. Para protección de nivel empresarial, <a href="https://hypersolutions.co?utm_source=github&utm_medium=readme&utm_campaign=scrapling">
        <b>Hyper Solutions</b>
      </a> proporciona endpoints API que generan tokens antibot válidos para <b>Akamai</b>, <b>DataDome</b>, <b>Kasada</b> e <b>Incapsula</b>. Simples llamadas API, sin automatización de navegador. </td>
  </tr>
  <tr>
    <td width="200">
      <a href="https://evomi.com?utm_source=github&utm_medium=banner&utm_campaign=d4vinci-scrapling" target="_blank" title="Evomi is your Swiss Quality Proxy Provider, starting at $0.49/GB">
        <img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/evomi.png">
      </a>
    </td>
    <td>
      <a href="https://evomi.com?utm_source=github&utm_medium=banner&utm_campaign=d4vinci-scrapling">
        <b>Evomi</b>
      </a>: proxies residenciales desde 0,49 $/GB. Navegador de scraping con Chromium con la huella completamente modificada, IPs residenciales, resolución automática de CAPTCHA y evasión anti-bot. </br>
      <b>API Scraper para resultados sin complicaciones. Integraciones MCP y N8N disponibles.</b>
    </td>
  </tr>
  <tr>
    <td width="200">
      <a href="https://substack.thewebscraping.club/p/scrapling-hands-on-guide?utm_source=github&utm_medium=repo&utm_campaign=scrapling" target="_blank" title="The #1 newsletter dedicated to Web Scraping">
        <img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/TWSC.png">
      </a>
    </td>
    <td>
    Lee una reseña completa de <a href="https://substack.thewebscraping.club/p/scrapling-hands-on-guide?utm_source=github&utm_medium=repo&utm_campaign=scrapling" target="_blank">Scrapling en The Web Scraping Club</a> (nov. 2025), el boletín número uno dedicado al Web Scraping.
    </td>
  </tr>
  <tr>
    <td width="200">
      <a href="https://www.swiftproxy.net/?ref=D4Vinci" target="_blank" title="Scalable Solutions for Web Data Access">
        <img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/SwiftProxy.png">
      </a>
    </td>
    <td>
    <a href="https://www.swiftproxy.net/?ref=D4Vinci" target="_blank">Swiftproxy</a> ofrece proxies residenciales escalables con más de 80 millones de IPs en más de 195 países, brindando conexiones rápidas y fiables, rotación automática y un sólido rendimiento anti-bloqueo. Prueba gratuita disponible.
    </td>
  </tr>
  <tr>
    <td width="200">
      <a href="https://byteful.com/?utm_source=github&utm_medium=github-sponsor&utm_campaign=scrapling_github_sponsor" target="_blank" title="Ethically sourced residential proxy infrastructure powering web scraping and AI agents">
        <img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/byteful.png">
      </a>
    </td>
    <td>
    <a href="https://byteful.com/?utm_source=github&utm_medium=github-sponsor&utm_campaign=scrapling_github_sponsor" target="_blank">Byteful</a> ofrece proxies residenciales, móviles, ISP y de centros de datos de origen ético, además de herramientas de scraping y automatización con IA. Usa el código SCRAPLING10 para obtener un 10% de descuento en proxies residenciales.
    </td>
  </tr>
  <tr>
    <td width="200">
      <a href="https://proxylane.dev/?utm_source=scrapling&utm_medium=partnership&utm_campaign=scrapling_platinum_202609&utm_content=github_readme" target="_blank" title="28M+ clean residential IPs for browser automation. No Blocks. No CAPTCHAs. Pay-as-you-Go.">
        <img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/proxylane.png">
      </a>
    </td>
    <td>
    <a href="https://proxylane.dev/?utm_source=scrapling&utm_medium=partnership&utm_campaign=scrapling_platinum_202609&utm_content=github_readme" target="_blank">ProxyLane</a>: Reduce los bloqueos y los CAPTCHAs en un 90%. 28 millones de IPs residenciales premium para scraping web intensivo. 195 países. Segmentación por ciudad/ISP/código postal. Sesiones persistentes o rotativas. Tráfico sin caducidad desde $2/GB. Código <strong>SCRAPEANDTAKE</strong>: <em>25% de descuento</em>.
    </td>
  </tr>
  <tr>
    <td width="200">
      <a href="https://www.lundproxy.com/unlimited-residential-bandwidth.html?utm_source=github&utm_medium=sponsorship&utm_campaign=scrapling&utm_content=banner" target="_blank" title="Unlimited residential traffic, sized only by bandwidth.">
        <img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/lundproxy.png">
      </a>
    </td>
    <td>
    <a href="https://www.lundproxy.com?utm_source=github&utm_medium=sponsorship&utm_campaign=scrapling&utm_content=text" target="_blank">LundProxy</a>: Deja de pagar por GB. Tráfico residencial ilimitado, más de 100 millones de IPs, más de 190 países. Paga según el ancho de banda. Solicita una prueba gratuita de proxies residenciales de 50 Mbps.
    </td>
  </tr>
  <tr>
    <td width="200">
      <a href="https://dataimpulse.com/?utm_source=website&utm_medium=github_readme&utm_campaign=scrapling_platinum" target="_blank" title="Buy Pay-as-you-go proxies from $1/GB">
        <img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/DataImpulse_Platinum.png">
      </a>
    </td>
    <td>
    $1/GB en <a href="https://dataimpulse.com/?utm_source=website&utm_medium=github_readme&utm_campaign=scrapling_platinum" target="_blank">DataImpulse</a>. Proxies de primera mano de origen ético. Más de 90 millones de IPs, más de 195 países. Residenciales, de centros de datos y móviles. Pago por uso = sin suscripción. El tráfico nunca caduca.
    </td>
  </tr>
</table>

<i><sub>¿Quieres mostrar tu anuncio aquí? Haz clic [aquí](https://github.com/sponsors/D4Vinci/sponsorships?tier_id=586646)</sub></i>
# Patrocinadores

<!-- sponsors -->

<a href="https://cloro.dev/?utm_source=referral&utm_medium=scrapling" target="_blank" title="The search API for the AI era"><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/cloro.jpg"></a>

<br/>

<a href="https://serpapi.com/?utm_source=scrapling" target="_blank" title="Scrape Google and other search engines with SerpApi"><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/SerpApi.png"></a>
<a href="https://visit.decodo.com/Dy6W0b" target="_blank" title="Try the Most Efficient Residential Proxies for Free"><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/decodo.png"></a>
<a href="https://proxyempire.io/?ref=scrapling&utm_source=github&utm_medium=paid_referral&utm_campaign=open_source_sponsorship&utm_content=scrapling" target="_blank" title="Collect The Data Your Project Needs with the Best Residential Proxies"><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/ProxyEmpire.png"></a>
<a href="https://www.webshare.io/?referral_code=48r2m2cd5uz1" target="_blank" title="The Most Reliable Proxy with Unparalleled Performance"><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/webshare.png"></a>
<a href="https://proxiware.com/?ref=scrapling" target="_blank" title="Collect Any Data. At Any Scale."><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/proxiware.png"></a>


<!-- /sponsors -->

<i><sub>¿Quieres mostrar tu anuncio aquí? ¡Haz clic [aquí](https://github.com/sponsors/D4Vinci) y elige el nivel que te convenga!</sub></i>

---

## Funciones principales

### Spiders: un framework completo de rastreo
- 🕷️ **API de Spider similar a Scrapy**: Define spiders con `start_urls`, callbacks `parse` asíncronos y objetos `Request` y `Response`.
- ⚡ **Rastreo concurrente**: Configura el número de solicitudes simultáneas, los límites por dominio y la espera entre descargas.
- 🔄 **Varias sesiones**: Usa solicitudes HTTP y navegadores sigilosos sin interfaz gráfica en un mismo spider. Envía las solicitudes a distintas sesiones mediante su ID.
- 💾 **Pausa y reanudación**: Guarda las solicitudes pendientes y las URL visitadas con `crawldir`. Pulsa Ctrl+C para detener el proceso de forma segura y vuelve a iniciarlo con el mismo directorio.
- 📡 **Resultados en streaming**: Recibe los elementos a medida que se extraen con `async for item in spider.stream()`, junto con estadísticas en tiempo real. Es útil para interfaces, procesos de datos y rastreos largos.
- 🛡️ **Detección de solicitudes bloqueadas**: Detecta y reintenta las solicitudes bloqueadas de forma automática. Puedes personalizar este comportamiento.
- 🚦 **AutoThrottle**: El spider ajusta la espera de cada dominio según la velocidad de respuesta del sitio. Si el sitio bloquea o limita las solicitudes, duplica la espera o respeta el tiempo indicado por `Retry-After`. Vuelve a acelerar cuando termina la limitación.
- 🤖 **Respeto de robots.txt**: Activa `robots_txt_obey` para respetar las directivas `Disallow`, `Crawl-delay` y `Request-rate`, con caché por dominio.
- 🧪 **Modo de desarrollo**: Guarda las respuestas en disco durante la primera ejecución y reutilízalas después. Así puedes ajustar `parse()` sin enviar nuevas solicitudes a los servidores.
- 🧩 **Plantillas de spider listas para usar**: Usa `CrawlSpider` para seguir enlaces según reglas, `SitemapSpider` para rastrear desde sitemaps o robots.txt, `XMLFeedSpider` y `CSVFeedSpider` para leer fuentes XML, RSS y CSV, y `ShopifySpider` para recoger productos de tiendas públicas de Shopify, con un elemento por variante.
- 🔗 **Extracción de enlaces**: `LinkExtractor` permite aceptar o rechazar enlaces con patrones, filtrar dominios y extensiones, limitar la búsqueda con CSS o XPath y normalizar las URL. Úsalo con las plantillas o por separado.
- 📦 **Exportación integrada**: Exporta los resultados con hooks y tu propio proceso de datos, o usa los formatos JSON, JSONL, CSV y XML integrados: `result.items.to_json()`, `to_jsonl()`, `to_csv()` y `to_xml()`.

### Obtención de páginas con soporte de sesiones
- **Solicitudes HTTP**: Envía solicitudes HTTP rápidas y sigilosas con `Fetcher`. Puedes imitar la huella TLS y las cabeceras de un navegador, y usar HTTP/3.
- **Carga dinámica**: Obtén sitios dinámicos con automatización completa del navegador mediante `StealthyFetcher`, compatible con Chromium de Playwright y Google Chrome.
- **Evasión de sistemas antibot**: `StealthyFetcher` oculta la automatización e imita huellas del navegador. Puede superar automáticamente los distintos tipos de Cloudflare Turnstile e Interstitial.
- **Gestión de sesiones**: `FetcherSession` y `StealthySession` mantienen las cookies y el estado entre solicitudes.
- **Rotación de proxies**: `ProxyRotator` permite rotar los proxies de forma cíclica o personalizada en todos los tipos de sesión. También puedes elegir un proxy para una solicitud concreta.
- **Bloqueo de dominios y anuncios**: Bloquea solicitudes a dominios y subdominios concretos, o activa el bloqueo de anuncios integrado en los fetchers de navegador. Incluye unos 3500 dominios conocidos de anuncios y seguimiento.
- **Prevención de fugas DNS**: Activa DNS-over-HTTPS para enviar las consultas DNS mediante el servicio DoH de Cloudflare y evitar fugas al usar proxies.
- **Navegadores remotos**: Conecta con un navegador que ya esté en ejecución mediante CDP y `cdp_url`, en tu equipo, en otro servidor o en un servicio de navegadores. También puedes usar tu propia versión de Chromium con cualquier fetcher de navegador mediante `executable_path`.
- **Captura de API en segundo plano**: Activa `record_requests=True` en una sesión de navegador y busca las respuestas guardadas con `session.network.search(limit=None)`. Lee datos de API y errores HTTP de distintas cargas de página sin repetir las solicitudes. El historial tiene un tamaño limitado y guarda el contenido de las respuestas de texto.
- **Soporte asíncrono**: Todos los fetchers admiten el uso asíncrono, con clases de sesión dedicadas.

### Análisis de páginas y extracción de datos
- 🔄 **Seguimiento de elementos**: Encuentra los elementos después de que cambie el sitio mediante algoritmos de similitud.
- 🎯 **Selección flexible**: Usa selectores CSS y XPath, filtros, texto, expresiones regulares y más.
- 🔍 **Elementos similares**: Encuentra automáticamente elementos parecidos a los que ya has localizado.

### Funciones de IA
- 🤖 **Servidor MCP**: Permite que los asistentes y agentes de IA, como Claude y Cursor, extraigan datos con Scrapling mediante solicitudes HTTP, acciones del navegador, capturas de pantalla, estado de inicio de sesión guardado y respuestas de API en segundo plano. Usa nuestro navegador sigiloso y herramientas que ayudan a los modelos adecuados a resolver CAPTCHA, además del solucionador de Cloudflare. Reduce el contenido enviado al modelo, bloquea anuncios y lo protege de la inyección de instrucciones (prompt injection). También admite navegadores remotos por CDP y conexiones HTTP con opciones de autenticación. ([Vídeo de demostración](https://www.youtube.com/watch?v=qyFk3ZNwOxE))
- 🧠 **Agent Skill**: Un [Agent Skill](https://scrapling.readthedocs.io/es/latest/ai/agent-skill.html) listo para instalar que enseña la biblioteca a los agentes de programación, para que escriban código que coincida con la API actual.
- 📚 **Markdown listo para RAG**: Convierte una página en Markdown limpio y preparado para modelos de lenguaje con una línea (`page.markdown()`), o guarda un sitio completo como archivos Markdown con la plantilla `ContentSpider`. No requiere un modelo de lenguaje durante el proceso. ([Documentación](https://scrapling.readthedocs.io/es/latest/ai/building-rag-systems.html))

### Alto rendimiento y uso probado
- 🚀 **Alta velocidad**: Rendimiento optimizado que supera a la mayoría de las bibliotecas de web scraping para Python.
- 🔋 **Bajo consumo de memoria**: Estructuras de datos optimizadas y carga solo cuando se necesita.
- ⚡ **Conversión rápida a JSON**: 10 veces más rápida que la biblioteca estándar.
- 🏗️ **Probado en la práctica**: Las pruebas cubren el 92% de Scrapling y todo el código tiene anotaciones de tipos. Cientos de personas lo han usado a diario para extraer datos durante el último año.

### Herramientas para desarrollar y extraer datos
- 🎯 **Consola interactiva**: Consola IPython opcional integrada con Scrapling, con atajos y herramientas para escribir scripts más rápido. Convierte solicitudes curl en solicitudes de Scrapling y muestra los resultados en el navegador.
- 🚀 **Uso desde la terminal**: Extrae los datos de una URL sin escribir código.
- 🛠️ **Navegación por el DOM**: Recorre los elementos padre, hermanos e hijos.
- 🧬 **Procesamiento de texto**: Expresiones regulares, limpieza de texto y operaciones de cadenas optimizadas.
- 📝 **Generación de selectores**: Genera selectores CSS y XPath fiables para cualquier elemento.
- 🔌 **API conocida**: Similar a Scrapy y BeautifulSoup, con los mismos pseudoelementos que Scrapy y Parsel.
- 🤝 **Integración directa con Scrapy**: Añade el decorador `scrapling_response` a un callback para analizar las respuestas que ya obtienes con el parser de Scrapling, sin reescribir tu programa.
- 📘 **Anotaciones de tipos completas**: Ayudan al editor a comprobar y completar el código. Todo el código se revisa automáticamente con **PyRight** y **MyPy** en cada cambio.
- 🔋 **Imagen Docker lista para usar**: Con cada versión se crea y publica automáticamente una imagen Docker que contiene todos los navegadores.

## Primeros pasos

Estos ejemplos muestran cómo empezar con Scrapling.

### Uso básico
Solicitudes HTTP con soporte de sesión
```python
from scrapling.fetchers import Fetcher, FetcherSession

with FetcherSession(impersonate='chrome') as session:  # Usa la última versión del fingerprint TLS de Chrome
    page = session.get('https://quotes.toscrape.com/', stealthy_headers=True)
    quotes = page.css('.quote .text::text').getall()

# O usa solicitudes de una sola vez
page = Fetcher.get('https://quotes.toscrape.com/')
quotes = page.css('.quote .text::text').getall()
```
Modo sigiloso avanzado
```python
from scrapling.fetchers import StealthyFetcher, StealthySession

with StealthySession(headless=True, solve_cloudflare=True) as session:  # Mantén el navegador abierto hasta que termines
    page = session.fetch('https://nopecha.com/demo/cloudflare', google_search=False)
    data = page.css('#padded_content a').getall()

# O usa el estilo de solicitud de una sola vez, abre el navegador para esta solicitud, luego lo cierra después de terminar
page = StealthyFetcher.fetch('https://nopecha.com/demo/cloudflare', solve_cloudflare=True)
data = page.css('#padded_content a').getall()
```
Automatización completa del navegador
```python
from scrapling.fetchers import StealthyFetcher, StealthySession

with StealthySession(headless=True, disable_resources=False, network_idle=True) as session:  # Mantén el navegador abierto hasta que termines
    page = session.fetch('https://quotes.toscrape.com/', load_dom=False)
    data = page.xpath('//span[@class="text"]/text()').getall()  # Selector XPath si lo prefieres

# O usa el estilo de solicitud de una sola vez, abre el navegador para esta solicitud, luego lo cierra después de terminar
page = StealthyFetcher.fetch('https://quotes.toscrape.com/')
data = page.css('.quote .text::text').getall()
```

### Spiders
Crea spiders con solicitudes concurrentes, varios tipos de sesión, pausa y reanudación:
```python
from scrapling.spiders import Spider, Response

class QuotesSpider(Spider):
    name = "quotes"
    start_urls = ["https://quotes.toscrape.com/"]
    concurrent_requests = 10

    async def parse(self, response: Response):
        for quote in response.css('.quote'):
            yield {
                "text": quote.css('.text::text').get(),
                "author": quote.css('.author::text').get(),
            }

        next_page = response.css('.next a')
        if next_page:
            yield response.follow(next_page[0].attrib['href'])

result = QuotesSpider().start()
print(f"Se extrajeron {len(result.items)} citas")
result.items.to_json("quotes.json")
```
Usa varios tipos de sesión en un mismo spider:
```python
from scrapling.spiders import Spider, Request, Response
from scrapling.fetchers import FetcherSession, AsyncStealthySession

class MultiSessionSpider(Spider):
    name = "multi"
    start_urls = ["https://example.com/"]

    def configure_sessions(self, manager):
        manager.add("fast", FetcherSession(impersonate="chrome"))
        manager.add("stealth", AsyncStealthySession(headless=True), lazy=True)

    async def parse(self, response: Response):
        for link in response.css('a::attr(href)').getall():
            # Enruta las páginas protegidas a través de la sesión sigilosa
            if "protected" in link:
                yield Request(link, sid="stealth")
            else:
                yield Request(link, sid="fast", callback=self.parse)  # callback explícito
```
Para guardar el progreso y continuar un rastreo más tarde, inicia el spider así:
```python
QuotesSpider(crawldir="./crawl_data").start()
```
Con `crawldir` configurado, pulsa Ctrl+C para guardar las solicitudes pendientes y las URL ya vistas. Reinicia con el mismo `crawldir` para continuar. Guarda los datos extraídos por separado.

O usa una plantilla lista para usar, como esta para extraer el catálogo completo de una tienda Shopify:
```python
from scrapling.spiders import ShopifySpider

class MyStore(ShopifySpider):
    target_website = "example.com"

result = MyStore().start()  # Todos los productos de la tienda, un elemento por variante
```
La plantilla obtiene los productos mediante las API públicas de las colecciones y devuelve un elemento por variante.

### Análisis avanzado y navegación
```python
from scrapling.fetchers import Fetcher

# Selección rica de elementos y navegación
page = Fetcher.get('https://quotes.toscrape.com/')

# Obtén citas con múltiples métodos de selección
quotes = page.css('.quote')  # Selector CSS
quotes = page.xpath('//div[@class="quote"]')  # XPath
quotes = page.find_all('div', {'class': 'quote'})  # Estilo BeautifulSoup
# Igual que
quotes = page.find_all('div', class_='quote')
quotes = page.find_all(['div'], class_='quote')
quotes = page.find_all(class_='quote')  # y así sucesivamente...
# Encuentra elementos por contenido de texto
quotes = page.find_by_text('Albert Einstein', first_match=False)

# Navegación avanzada
quote_text = page.css('.quote')[0].css('.text::text').get()
quote_texts = page.css('.quote').css('.text::text').getall()  # Selectores encadenados
first_quote = page.css('.quote')[0]
author = first_quote.css('.author::text').get()
next_quote = first_quote.next
parent_container = first_quote.parent

# Relaciones y similitud de elementos
similar_elements = first_quote.find_similar()
below_elements = first_quote.below_elements
```
Si ya tienes el HTML, puedes usar el parser directamente:
```python
from scrapling.parser import Selector

page = Selector("<html>...</html>")
```
Puedes usar los mismos métodos de selección.

### Gestión de sesiones asíncronas
```python
import asyncio
from scrapling.fetchers import FetcherSession, AsyncStealthySession

async def main():
    async with FetcherSession(http3=True) as http_session:  # `FetcherSession` se adapta al contexto y funciona tanto con sync como con async
        page1 = await http_session.get('https://quotes.toscrape.com/')
        page2 = await http_session.get('https://quotes.toscrape.com/page/2/', impersonate='chrome')
        print(len(page1.css('.quote')), len(page2.css('.quote')))

    async with AsyncStealthySession(max_pages=2) as browser_session:
        urls = ['https://quotes.toscrape.com/js/', 'https://quotes.toscrape.com/js/page/2/']
        pages = await asyncio.gather(*(browser_session.fetch(url, wait_selector='.quote') for url in urls))
        print([len(page.css('.quote')) for page in pages])

asyncio.run(main())
```

## Línea de comandos y consola interactiva

Puedes usar Scrapling desde la línea de comandos:

[![asciicast](https://asciinema.org/a/736339.svg)](https://asciinema.org/a/736339)

Para abrir la consola interactiva de web scraping:
```bash
pip install "scrapling[shell]"
scrapling shell
```
Extrae páginas directamente a un archivo sin programar. Usa `--css-selector` para elegir el contenido o `--ai-targeted` para seleccionar y limpiar el contenido de `body`. Usa `.txt` para texto, `.md` para Markdown o `.html` para HTML.
```bash
scrapling extract get 'https://quotes.toscrape.com/' quotes.md
scrapling extract get 'https://quotes.toscrape.com/' quotes.txt --css-selector '.quote' --impersonate 'chrome'
scrapling extract fetch 'https://quotes.toscrape.com/js/' quotes.md --css-selector '.quote' --wait-selector '.quote' --no-headless
scrapling extract fetch 'https://nopecha.com/demo/cloudflare' captchas.html --css-selector '#padded_content a' --solve-cloudflare
```

> [!NOTE]
> Estos son ejemplos breves. Para conocer más funciones, incluido el servidor MCP y la consola interactiva, consulta la documentación completa [aquí](https://scrapling.readthedocs.io/es/latest/)

## Pruebas de rendimiento

Scrapling no solo es potente, también es ultrarrápido. Los siguientes benchmarks comparan el parser de Scrapling con las últimas versiones de otras bibliotecas populares.

### Velocidad de extracción de texto (5000 elementos anidados)

| # |    Biblioteca     | Tiempo (ms) | vs Scrapling |
|---|:-----------------:|:-----------:|:------------:|
| 1 |     Scrapling     |    1,99     |     1,0x     |
| 2 |   Parsel/Scrapy   |    2,06     |     1,035    |
| 3 |     Raw Lxml      |    2,56     |    1,286     |
| 4 |      PyQuery      |    23,98    |     ~12x     |
| 5 |    Selectolax     |    197,02   |     ~99x     |
| 6 |  MechanicalSoup   |   1545,15   |   ~776,5x    |
| 7 |   BS4 with Lxml   |   1562,1    |   ~785,0x    |
| 8 | BS4 with html5lib |   3412,73   |   ~1714,9x   |


### Rendimiento de similitud de elementos y búsqueda de texto

Las capacidades de búsqueda adaptativa de elementos de Scrapling superan significativamente a las alternativas:

| Biblioteca  | Tiempo (ms) | vs Scrapling |
|-------------|:-----------:|:------------:|
| Scrapling   |     2,3     |     1,0x     |
| AutoScraper |    12,58    |    5,47x     |


> Todos los benchmarks representan promedios de más de 100 ejecuciones. Ver [benchmarks.py](https://github.com/D4Vinci/Scrapling/blob/main/benchmarks.py) para la metodología.

## Instalación

Scrapling requiere Python 3.10 o superior:

```bash
pip install scrapling
```

> [!IMPORTANT]
> Este comando solo instala el parser y sus dependencias, sin fetchers ni herramientas de línea de comandos. Si no instalas nada más, importar desde `scrapling.fetchers` o `scrapling.spiders`, como en los ejemplos anteriores, produce `ModuleNotFoundError`. Para usar fetchers o spiders, instala primero sus dependencias como se indica a continuación.

### Dependencias opcionales

1. Para usar los fetchers, sus clases o las funciones adicionales siguientes, instala las dependencias de los fetchers y los navegadores:
    ```bash
    pip install "scrapling[fetchers]"

    scrapling install           # normal install
    scrapling install  --force  # force reinstall
    ```

    Esto descarga todos los navegadores, sus dependencias del sistema y las herramientas para modificar las huellas del navegador.

    O puedes instalarlos desde el código en lugar de ejecutar un comando:
    ```python
    from scrapling.cli import install

    install([], standalone_mode=False)          # normal install
    install(["--force"], standalone_mode=False) # force reinstall
    ```

2. Características adicionales:
   - Instalar el servidor MCP:
       ```bash
       pip install "scrapling[ai]"
       ```
   - Instalar dependencias para ([construir sistemas RAG](https://scrapling.readthedocs.io/es/latest/ai/building-rag-systems.html)):
       ```bash
       pip install "scrapling[rag]"
       ```
   - Instalar la consola interactiva y el comando `extract`:
       ```bash
       pip install "scrapling[shell]"
       ```
   - Instalar todo:
       ```bash
       pip install "scrapling[all]"
       ```
   Ejecuta `scrapling install` cuando necesites fetchers de navegador. Las solicitudes HTTP no requieren instalar un navegador.

### Docker
También puedes instalar una imagen Docker con todos los extras y navegadores con el siguiente comando desde DockerHub:
```bash
docker pull pyd4vinci/scrapling
```
O descárgala desde el registro de GitHub:
```bash
docker pull ghcr.io/d4vinci/scrapling:latest
```
Esta imagen se construye y publica automáticamente usando GitHub Actions y la rama principal del repositorio.

## Contribuir

¡Damos la bienvenida a las contribuciones! Por favor lee nuestras [pautas de contribución](https://github.com/D4Vinci/Scrapling/blob/main/CONTRIBUTING.md) antes de comenzar.

## Descargo de responsabilidad

> [!CAUTION]
> Esta biblioteca se proporciona solo con fines educativos y de investigación. Al usar esta biblioteca, aceptas cumplir con las leyes locales e internacionales de scraping de datos y privacidad. Los autores y contribuyentes no son responsables de ningún mal uso de este software. Respeta siempre los términos de servicio de los sitios web y los archivos robots.txt.

## 🎓 Citas
Si has utilizado nuestra biblioteca con fines de investigación, por favor cítanos con la siguiente referencia:
```text
  @misc{scrapling,
    author = {Karim Shoair},
    title = {Scrapling},
    year = {2024},
    url = {https://github.com/D4Vinci/Scrapling},
    note = {A Python Web Scraping framework for everything from a single request to a full-scale crawl!}
  }
```

## Licencia

Este trabajo está licenciado bajo la Licencia BSD-3-Clause.

## Agradecimientos

Este proyecto incluye código adaptado de:
- Parsel (Licencia BSD), usado para el submódulo [translator](https://github.com/D4Vinci/Scrapling/blob/main/scrapling/core/translator.py)

---
<div align="center"><small>Diseñado y elaborado con ❤️ por Karim Shoair.</small></div><br>
