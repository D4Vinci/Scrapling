<h1 align="center">
    <a href="https://scrapling.readthedocs.io">
        <picture>
          <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/D4Vinci/Scrapling/v4/docs/assets/cover_dark.svg?sanitize=true">
          <img alt="Scrapling Poster" src="https://raw.githubusercontent.com/D4Vinci/Scrapling/v4/docs/assets/cover_light.svg?sanitize=true">
        </picture>
    </a>
    <br>
    <small>Web Scraping have never been easier!</small>
</h1>
<p align="center">
    <a href="https://github.com/D4Vinci/Scrapling/actions/workflows/tests.yml" alt="Tests">
        <img alt="Tests" src="https://github.com/D4Vinci/Scrapling/actions/workflows/tests.yml/badge.svg"></a>
    <a href="https://badge.fury.io/py/Scrapling" alt="PyPI version">
        <img alt="PyPI version" src="https://badge.fury.io/py/Scrapling.svg"></a>
    <a href="https://pepy.tech/project/scrapling" alt="PyPI Downloads">
        <img alt="PyPI Downloads" src="https://static.pepy.tech/personalized-badge/scrapling?period=total&units=INTERNATIONAL_SYSTEM&left_color=GREY&right_color=GREEN&left_text=Downloads"></a>
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
    <a href="https://scrapling.readthedocs.io/en/latest/parsing/selection/">
        Métodos de selección
    </a>
    ·
    <a href="https://scrapling.readthedocs.io/en/latest/fetching/choosing/">
        Elegir un fetcher
    </a>
    ·
    <a href="https://scrapling.readthedocs.io/en/latest/cli/overview/">
        CLI
    </a>
    ·
    <a href="https://scrapling.readthedocs.io/en/latest/ai/mcp-server/">
        Modo MCP
    </a>
    ·
    <a href="https://scrapling.readthedocs.io/en/latest/tutorials/migrating_from_beautifulsoup/">
        Migrar desde Beautifulsoup
    </a>
</p>

**Deja de luchar contra sistemas anti-bot. Deja de reescribir selectores después de cada actualización del sitio web.**

Scrapling no es solo otra biblioteca de Web Scraping. Es la primera biblioteca de scraping **adaptativa** que aprende de los cambios de los sitios web y evoluciona con ellos. Mientras que otras bibliotecas se rompen cuando los sitios web actualizan su estructura, Scrapling relocaliza automáticamente tus elementos y mantiene tus scrapers funcionando.

Construido para la Web moderna, Scrapling presenta **su propio motor de análisis rápido** y fetchers para manejar todos los desafíos de Web Scraping que enfrentas o enfrentarás. Construido por Web Scrapers para Web Scrapers y usuarios regulares, hay algo para todos.

```python
>> from scrapling.fetchers import Fetcher, AsyncFetcher, StealthyFetcher, DynamicFetcher
>> StealthyFetcher.adaptive = True
# ¡Obtén el código fuente de sitios web bajo el radar!
>> page = StealthyFetcher.fetch('https://example.com', headless=True, network_idle=True)
>> print(page.status)
200
>> products = page.css('.product', auto_save=True)  # ¡Extrae datos que sobreviven a cambios de diseño del sitio web!
>> # Más tarde, si la estructura del sitio web cambia, pasa `adaptive=True`
>> products = page.css('.product', adaptive=True)  # ¡y Scrapling aún los encuentra!
```

# Patrocinadores 

<!-- sponsors -->

<a href="https://www.scrapeless.com/en?utm_source=official&utm_term=scrapling" target="_blank" title="Effortless Web Scraping Toolkit for Business and Developers"><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/scrapeless.jpg"></a>
<a href="https://www.thordata.com/?ls=github&lk=github" target="_blank" title="Unblockable proxies and scraping infrastructure, delivering real-time, reliable web data to power AI models and workflows."><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/thordata.jpg"></a>
<a href="https://evomi.com?utm_source=github&utm_medium=banner&utm_campaign=d4vinci-scrapling" target="_blank" title="Evomi is your Swiss Quality Proxy Provider, starting at $0.49/GB"><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/evomi.png"></a>
<a href="https://serpapi.com/?utm_source=scrapling" target="_blank" title="Scrape Google and other search engines with SerpApi"><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/SerpApi.png"></a>
<a href="https://visit.decodo.com/Dy6W0b" target="_blank" title="Try the Most Efficient Residential Proxies for Free"><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/decodo.png"></a>
<a href="https://petrosky.io/d4vinci" target="_blank" title="PetroSky delivers cutting-edge VPS hosting."><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/petrosky.png"></a>
<a href="https://hasdata.com/?utm_source=github&utm_medium=banner&utm_campaign=D4Vinci" target="_blank" title="The web scraping service that actually beats anti-bot systems!"><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/hasdata.png"></a>
<a href="https://hypersolutions.co/?utm_source=github&utm_medium=readme&utm_campaign=scrapling" target="_blank" title="Bot Protection Bypass API for Akamai, DataDome, Incapsula & Kasada"><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/HyperSolutions.png"></a>
<a href="https://www.swiftproxy.net/" target="_blank" title="Unlock Reliable Proxy Services with Swiftproxy!"><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/swiftproxy.png"></a>
<a href="https://www.rapidproxy.io/?ref=d4v" target="_blank" title="Affordable Access to the Proxy World – bypass CAPTCHAs blocks, and avoid additional costs."><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/rapidproxy.jpg"></a>
<a href="https://browser.cash/?utm_source=D4Vinci&utm_medium=referral" target="_blank" title="Browser Automation & AI Browser Agent Platform"><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/browserCash.png"></a>

<!-- /sponsors -->

<i><sub>¿Quieres mostrar tu anuncio aquí? ¡Haz clic [aquí](https://github.com/sponsors/D4Vinci) y elige el nivel que te convenga!</sub></i>

---

## Características Principales

### Obtención Avanzada de Sitios Web con Soporte de Sesión
- **Solicitudes HTTP**: Solicitudes HTTP rápidas y sigilosas con la clase `Fetcher`. Puede imitar la huella TLS de los navegadores, encabezados y usar HTTP3.
- **Carga Dinámica**: Obtén sitios web dinámicos con automatización completa del navegador a través de la clase `DynamicFetcher` compatible con Chromium de Playwright y Google Chrome.
- **Evasión Anti-bot**: Capacidades de sigilo avanzadas con `StealthyFetcher` y falsificación de huellas digitales. Puede evadir fácilmente todos los tipos de Turnstile/Interstitial de Cloudflare con automatización.
- **Gestión de Sesión**: Soporte de sesión persistente con las clases `FetcherSession`, `StealthySession` y `DynamicSession` para la gestión de cookies y estado entre solicitudes.
- **Soporte Async**: Soporte async completo en todos los fetchers y clases de sesión async dedicadas.

### Scraping Adaptativo e Integración con IA
- 🔄 **Seguimiento Inteligente de Elementos**: Relocaliza elementos después de cambios en el sitio web usando algoritmos inteligentes de similitud.
- 🎯 **Selección Flexible Inteligente**: Selectores CSS, selectores XPath, búsqueda basada en filtros, búsqueda de texto, búsqueda regex y más.
- 🔍 **Encontrar Elementos Similares**: Localiza automáticamente elementos similares a los elementos encontrados.
- 🤖 **Servidor MCP para usar con IA**: Servidor MCP integrado para Web Scraping asistido por IA y extracción de datos. El servidor MCP presenta capacidades poderosas y personalizadas que aprovechan Scrapling para extraer contenido específico antes de pasarlo a la IA (Claude/Cursor/etc), acelerando así las operaciones y reduciendo costos al minimizar el uso de tokens. ([video demo](https://www.youtube.com/watch?v=qyFk3ZNwOxE))

### Arquitectura de Alto Rendimiento y Probada en Batalla
- 🚀 **Ultrarrápido**: Rendimiento optimizado que supera a la mayoría de las bibliotecas de scraping de Python.
- 🔋 **Eficiente en Memoria**: Estructuras de datos optimizadas y carga diferida para una huella de memoria mínima.
- ⚡ **Serialización JSON Rápida**: 10 veces más rápido que la biblioteca estándar.
- 🏗️ **Probado en batalla**: Scrapling no solo tiene una cobertura de prueba del 92% y cobertura completa de type hints, sino que ha sido utilizado diariamente por cientos de Web Scrapers durante el último año.

### Experiencia Amigable para Desarrolladores/Web Scrapers
- 🎯 **Shell Interactivo de Web Scraping**: Shell IPython integrado opcional con integración de Scrapling, atajos y nuevas herramientas para acelerar el desarrollo de scripts de Web Scraping, como convertir solicitudes curl a solicitudes Scrapling y ver resultados de solicitudes en tu navegador.
- 🚀 **Úsalo directamente desde la Terminal**: Opcionalmente, ¡puedes usar Scrapling para hacer scraping de una URL sin escribir ni una sola línea de código!
- 🛠️ **API de Navegación Rica**: Recorrido avanzado del DOM con métodos de navegación de padres, hermanos e hijos.
- 🧬 **Procesamiento de Texto Mejorado**: Métodos integrados de regex, limpieza y operaciones de cadena optimizadas.
- 📝 **Generación Automática de Selectores**: Genera selectores CSS/XPath robustos para cualquier elemento.
- 🔌 **API Familiar**: Similar a Scrapy/BeautifulSoup con los mismos pseudo-elementos usados en Scrapy/Parsel.
- 📘 **Cobertura Completa de Tipos**: Type hints completos para excelente soporte de IDE y autocompletado de código.
- 🔋 **Imagen Docker Lista**: Con cada lanzamiento, se construye y publica automáticamente una imagen Docker que contiene todos los navegadores.

## Empezando

### Uso Básico
```python
from scrapling.fetchers import Fetcher, StealthyFetcher, DynamicFetcher
from scrapling.fetchers import FetcherSession, StealthySession, DynamicSession

# Solicitudes HTTP con soporte de sesión
with FetcherSession(impersonate='chrome') as session:  # Usa la última versión de la huella TLS de Chrome
    page = session.get('https://quotes.toscrape.com/', stealthy_headers=True)
    quotes = page.css('.quote .text::text')

# O usa solicitudes de una sola vez
page = Fetcher.get('https://quotes.toscrape.com/')
quotes = page.css('.quote .text::text')

# Modo sigiloso avanzado (Mantén el navegador abierto hasta que termines)
with StealthySession(headless=True, solve_cloudflare=True) as session:
    page = session.fetch('https://nopecha.com/demo/cloudflare', google_search=False)
    data = page.css('#padded_content a')

# O usa el estilo de solicitud de una sola vez, abre el navegador para esta solicitud, luego lo cierra después de terminar
page = StealthyFetcher.fetch('https://nopecha.com/demo/cloudflare')
data = page.css('#padded_content a')
    
# Automatización completa del navegador (Mantén el navegador abierto hasta que termines)
with DynamicSession(headless=True) as session:
    page = session.fetch('https://quotes.toscrape.com/', network_idle=True)
    quotes = page.css('.quote .text::text')

# O usa el estilo de solicitud de una sola vez
page = DynamicFetcher.fetch('https://quotes.toscrape.com/', network_idle=True)
quotes = page.css('.quote .text::text')
```

### Selección de Elementos
```python
# CSS selectors
page.css('a::text')                      # Extracta texto
page.css('a::attr(href)')                # Extracta atributos
page.css('a', recursive=False)           # Solo elementos directos
page.css('a', auto_save=True)            # Guarda posiciones de los elementos automáticamente

# XPath
page.xpath('//a/text()')

# Búsqueda flexible
page.find_by_text('Python', first_match=True)  # Encuentra por texto
page.find_by_regex(r'\d{4}')                   # Encuentra por patrón regex
page.find('div', {'class': 'container'})       # Encuentra por atributos

# Navegación
element.parent                           # Obtener elemento padre
element.next_sibling                     # Obtener siguiente hermano
element.children                         # Obtener hijos

# Elementos similares
similar = page.get_similar(element)      # Encuentra elementos similares

# Scraping adaptativo
saved_elements = page.css('.product', auto_save=True)
# Más tarde, cuando el sitio web cambia:
page.css('.product', adaptive=True)      # Encuentra elementos usando posiciones guardadas
```

### Uso de Sesión
```python
from scrapling.fetchers import FetcherSession, AsyncFetcherSession

# Sesión sincrónica
with FetcherSession() as session:
    # Las cookies se mantienen automáticamente
    page1 = session.get('https://quotes.toscrape.com/login')
    page2 = session.post('https://quotes.toscrape.com/login', data={'username': 'admin', 'password': 'admin'})
    
    # Cambiar fingerprint del navegador si es necesario
    page2 = session.get('https://quotes.toscrape.com/', impersonate='firefox135')

# Uso de sesión async
async with AsyncStealthySession(max_pages=2) as session:
    tasks = []
    urls = ['https://example.com/page1', 'https://example.com/page2']
    
    for url in urls:
        task = session.fetch(url)
        tasks.append(task)
    
    print(session.get_pool_stats())  # Opcional - El estado del pool de pestañas del navegador (ocupado/libre/error)
    results = await asyncio.gather(*tasks)
    print(session.get_pool_stats())
```

## CLI y Shell Interactivo

Scrapling v0.3 incluye una poderosa interfaz de línea de comandos:

[![asciicast](https://asciinema.org/a/736339.svg)](https://asciinema.org/a/736339)

Lanzar shell interactivo de Web Scraping
```bash
scrapling shell
```
Extraer páginas a un archivo directamente sin programar (Extrae el contenido dentro de la etiqueta `body` por defecto). Si el archivo de salida termina con `.txt`, entonces se extraerá el contenido de texto del objetivo. Si termina con `.md`, será una representación Markdown del contenido HTML; si termina con `.html`, será el contenido HTML en sí mismo.
```bash
scrapling extract get 'https://example.com' content.md
scrapling extract get 'https://example.com' content.txt --css-selector '#fromSkipToProducts' --impersonate 'chrome'  # Todos los elementos que coinciden con el selector CSS '#fromSkipToProducts'
scrapling extract fetch 'https://example.com' content.md --css-selector '#fromSkipToProducts' --no-headless
scrapling extract stealthy-fetch 'https://nopecha.com/demo/cloudflare' captchas.html --css-selector '#padded_content a' --solve-cloudflare
```

> [!NOTE]
> Hay muchas características adicionales, pero queremos mantener esta página concisa, como el servidor MCP y el Shell Interactivo de Web Scraping. Consulta la documentación completa [aquí](https://scrapling.readthedocs.io/en/latest/)

## Benchmarks de Rendimiento

Scrapling no solo es poderoso, también es increíblemente rápido, y las actualizaciones desde la versión 0.3 han brindado mejoras de rendimiento excepcionales en todas las operaciones. Los siguientes benchmarks comparan el analizador de Scrapling con otras bibliotecas populares.

### Prueba de Velocidad de Extracción de Texto (5000 elementos anidados)

| # |    Biblioteca     | Tiempo (ms) | vs Scrapling | 
|---|:-----------------:|:-----------:|:------------:|
| 1 |     Scrapling     |    1.99     |     1.0x     |
| 2 |   Parsel/Scrapy   |    2.01     |    1.01x     |
| 3 |     Raw Lxml      |     2.5     |    1.256x    |
| 4 |      PyQuery      |    22.93    |    ~11.5x    |
| 5 |    Selectolax     |    80.57    |    ~40.5x    |
| 6 |   BS4 with Lxml   |   1541.37   |   ~774.6x    |
| 7 |  MechanicalSoup   |   1547.35   |   ~777.6x    |
| 8 | BS4 with html5lib |   3410.58   |   ~1713.9x   |


### Rendimiento de Similitud de Elementos y Búsqueda de Texto

Las capacidades de búsqueda adaptativa de elementos de Scrapling superan significativamente a las alternativas:

| Biblioteca  | Tiempo (ms) | vs Scrapling |
|-------------|:-----------:|:------------:|
| Scrapling   |    2.46     |     1.0x     |
| AutoScraper |    13.3     |    5.407x    |


> Todos los benchmarks representan promedios de más de 100 ejecuciones. Ver [benchmarks.py](https://github.com/D4Vinci/Scrapling/blob/main/benchmarks.py) para la metodología.

## Instalación

Scrapling requiere Python 3.10 o superior:

```bash
pip install scrapling
```

A partir de v0.3.2, esta instalación solo incluye el motor de análisis y sus dependencias, sin ningún fetcher o dependencias de línea de comandos.

### Dependencias Opcionales

1. Si vas a usar alguna de las características adicionales a continuación, los fetchers, o sus clases, necesitarás instalar las dependencias de los fetchers y sus dependencias del navegador de la siguiente manera:
    ```bash
    pip install "scrapling[fetchers]"
    
    scrapling install
    ```

    Esto descarga todos los navegadores, junto con sus dependencias del sistema y dependencias de manipulación de huellas digitales.

2. Características adicionales:
   - Instalar la característica del servidor MCP:
       ```bash
       pip install "scrapling[ai]"
       ```
   - Instalar características del shell (shell de Web Scraping y el comando `extract`): 
       ```bash
       pip install "scrapling[shell]"
       ```
   - Instalar todo: 
       ```bash
       pip install "scrapling[all]"
       ```
   Recuerda que necesitas instalar las dependencias del navegador con `scrapling install` después de cualquiera de estos extras (si no lo hiciste ya)

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

## Descargo de Responsabilidad

> [!CAUTION]
> Esta biblioteca se proporciona solo con fines educativos y de investigación. Al usar esta biblioteca, aceptas cumplir con las leyes locales e internacionales de scraping de datos y privacidad. Los autores y contribuyentes no son responsables de ningún mal uso de este software. Respeta siempre los términos de servicio de los sitios web y los archivos robots.txt.

## Licencia

Este trabajo está licenciado bajo la Licencia BSD-3-Clause.

## Agradecimientos

Este proyecto incluye código adaptado de:
- Parsel (Licencia BSD)—Usado para el submódulo [translator](https://github.com/D4Vinci/Scrapling/blob/main/scrapling/core/translator.py)

## Agradecimientos y Referencias

- El brillante trabajo de [Daijro](https://github.com/daijro) en [BrowserForge](https://github.com/daijro/browserforge) y [Camoufox](https://github.com/daijro/camoufox)
- El brillante trabajo de [Vinyzu](https://github.com/Vinyzu) en [Botright](https://github.com/Vinyzu/Botright) y [PatchRight](https://github.com/Kaliiiiiiiiii-Vinyzu/patchright)
- [brotector](https://github.com/kaliiiiiiiiii/brotector) por técnicas de evasión de detección de navegador
- [fakebrowser](https://github.com/kkoooqq/fakebrowser) y [BotBrowser](https://github.com/botswin/BotBrowser) por investigación de huellas digitales

---
<div align="center"><small>Diseñado y elaborado con ❤️ por Karim Shoair.</small></div><br>