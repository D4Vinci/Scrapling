<!-- mcp-name: io.github.D4Vinci/Scrapling -->

<h1 align="center">
    <a href="https://scrapling.readthedocs.io">
        <picture>
          <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/docs/assets/cover_dark.svg?sanitize=true">
          <img alt="Scrapling Poster" src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/docs/assets/cover_light.svg?sanitize=true">
        </picture>
    </a>
    <br>
    <small>Effortless Web Scraping for the Modern Web</small>
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
    <a href="https://scrapling.readthedocs.io/en/latest/parsing/selection/"><strong>Métodos de selección</strong></a>
    &middot;
    <a href="https://scrapling.readthedocs.io/en/latest/fetching/choosing/"><strong>Elegir un fetcher</strong></a>
    &middot;
    <a href="https://scrapling.readthedocs.io/en/latest/spiders/architecture.html"><strong>Spiders</strong></a>
    &middot;
    <a href="https://scrapling.readthedocs.io/en/latest/spiders/proxy-blocking.html"><strong>Rotación de proxy</strong></a>
    &middot;
    <a href="https://scrapling.readthedocs.io/en/latest/cli/overview/"><strong>CLI</strong></a>
    &middot;
    <a href="https://scrapling.readthedocs.io/en/latest/ai/mcp-server/"><strong>Modo MCP</strong></a>
</p>

Scrapling es un framework de Web Scraping adaptativo que se encarga de todo, desde una sola solicitud hasta un rastreo a gran escala.

Su parser aprende de los cambios de los sitios web y relocaliza automáticamente tus elementos cuando las páginas se actualizan. Sus fetchers evaden sistemas anti-bot como Cloudflare Turnstile de forma nativa. Y su framework Spider te permite escalar a rastreos concurrentes con múltiples sesiones, con Pause & Resume y rotación automática de Proxy, todo en unas pocas líneas de Python. Una biblioteca, cero compromisos.

Rastreos ultrarrápidos con estadísticas en tiempo real y Streaming. Construido por Web Scrapers para Web Scrapers y usuarios regulares, hay algo para todos.

```python
from scrapling.fetchers import Fetcher, AsyncFetcher, StealthyFetcher, DynamicFetcher
StealthyFetcher.adaptive = True
p = StealthyFetcher.fetch('https://example.com', headless=True, network_idle=True)  # ¡Obtén el sitio web bajo el radar!
products = p.css('.product', auto_save=True)                                        # ¡Extrae datos que sobreviven a cambios de diseño del sitio web!
products = p.css('.product', adaptive=True)                                         # Más tarde, si la estructura del sitio web cambia, ¡pasa `adaptive=True` para encontrarlos!
```
O escala a rastreos completos
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


# Patrocinadores Platino

<i><sub>¿Quieres ser la primera empresa en aparecer aquí? Haz clic [aquí](https://github.com/sponsors/D4Vinci/sponsorships?tier_id=586646)</sub></i>
# Patrocinadores

<!-- sponsors -->

<a href="https://www.thordata.com/?ls=github&lk=github" target="_blank" title="Unblockable proxies and scraping infrastructure, delivering real-time, reliable web data to power AI models and workflows."><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/thordata.jpg"></a>
<a href="https://evomi.com?utm_source=github&utm_medium=banner&utm_campaign=d4vinci-scrapling" target="_blank" title="Evomi is your Swiss Quality Proxy Provider, starting at $0.49/GB"><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/evomi.png"></a>
<a href="https://serpapi.com/?utm_source=scrapling" target="_blank" title="Scrape Google and other search engines with SerpApi"><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/SerpApi.png"></a>
<a href="https://visit.decodo.com/Dy6W0b" target="_blank" title="Try the Most Efficient Residential Proxies for Free"><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/decodo.png"></a>
<a href="https://petrosky.io/d4vinci" target="_blank" title="PetroSky delivers cutting-edge VPS hosting."><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/petrosky.png"></a>
<a href="https://hasdata.com/?utm_source=github&utm_medium=banner&utm_campaign=D4Vinci" target="_blank" title="The web scraping service that actually beats anti-bot systems!"><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/hasdata.png"></a>
<a href="https://proxyempire.io/?ref=scrapling&utm_source=scrapling" target="_blank" title="Collect The Data Your Project Needs with the Best Residential Proxies"><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/ProxyEmpire.png"></a>
<a href="https://hypersolutions.co/?utm_source=github&utm_medium=readme&utm_campaign=scrapling" target="_blank" title="Bot Protection Bypass API for Akamai, DataDome, Incapsula & Kasada"><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/HyperSolutions.png"></a>


<a href="https://www.swiftproxy.net/" target="_blank" title="Unlock Reliable Proxy Services with Swiftproxy!"><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/swiftproxy.png"></a>
<a href="https://www.rapidproxy.io/?ref=d4v" target="_blank" title="Affordable Access to the Proxy World – bypass CAPTCHAs blocks, and avoid additional costs."><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/rapidproxy.jpg"></a>
<a href="https://browser.cash/?utm_source=D4Vinci&utm_medium=referral" target="_blank" title="Browser Automation & AI Browser Agent Platform"><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/browserCash.png"></a>

<!-- /sponsors -->

<i><sub>¿Quieres mostrar tu anuncio aquí? ¡Haz clic [aquí](https://github.com/sponsors/D4Vinci) y elige el nivel que te convenga!</sub></i>

---

## Características Principales

### Spiders — Un Framework Completo de Rastreo
- 🕷️ **API de Spider al estilo Scrapy**: Define spiders con `start_urls`, callbacks async `parse`, y objetos `Request`/`Response`.
- ⚡ **Rastreo Concurrente**: Límites de concurrencia configurables, limitación por dominio y retrasos de descarga.
- 🔄 **Soporte Multi-Session**: Interfaz unificada para solicitudes HTTP y navegadores headless sigilosos en un solo Spider — enruta solicitudes a diferentes sesiones por ID.
- 💾 **Pause & Resume**: Persistencia de rastreo basada en Checkpoint. Presiona Ctrl+C para un cierre ordenado; reinicia para continuar desde donde lo dejaste.
- 📡 **Modo Streaming**: Transmite elementos extraídos a medida que llegan con `async for item in spider.stream()` con estadísticas en tiempo real — ideal para UI, pipelines y rastreos de larga duración.
- 🛡️ **Detección de Solicitudes Bloqueadas**: Detección automática y reintento de solicitudes bloqueadas con lógica personalizable.
- 📦 **Exportación Integrada**: Exporta resultados a través de hooks y tu propio pipeline o el JSON/JSONL integrado con `result.items.to_json()` / `result.items.to_jsonl()` respectivamente.

### Obtención Avanzada de Sitios Web con Soporte de Session
- **Solicitudes HTTP**: Solicitudes HTTP rápidas y sigilosas con la clase `Fetcher`. Puede imitar el fingerprint TLS de los navegadores, encabezados y usar HTTP/3.
- **Carga Dinámica**: Obtén sitios web dinámicos con automatización completa del navegador a través de la clase `DynamicFetcher` compatible con Chromium de Playwright y Google Chrome.
- **Evasión Anti-bot**: Capacidades de sigilo avanzadas con `StealthyFetcher` y falsificación de fingerprint. Puede evadir fácilmente todos los tipos de Turnstile/Interstitial de Cloudflare con automatización.
- **Gestión de Session**: Soporte de sesión persistente con las clases `FetcherSession`, `StealthySession` y `DynamicSession` para la gestión de cookies y estado entre solicitudes.
- **Rotación de Proxy**: `ProxyRotator` integrado con estrategias de rotación cíclica o personalizadas en todos los tipos de sesión, además de sobrescrituras de Proxy por solicitud.
- **Bloqueo de Dominios**: Bloquea solicitudes a dominios específicos (y sus subdominios) en fetchers basados en navegador.
- **Soporte Async**: Soporte async completo en todos los fetchers y clases de sesión async dedicadas.

### Scraping Adaptativo e Integración con IA
- 🔄 **Seguimiento Inteligente de Elementos**: Relocaliza elementos después de cambios en el sitio web usando algoritmos inteligentes de similitud.
- 🎯 **Selección Flexible Inteligente**: Selectores CSS, selectores XPath, búsqueda basada en filtros, búsqueda de texto, búsqueda regex y más.
- 🔍 **Encontrar Elementos Similares**: Localiza automáticamente elementos similares a los elementos encontrados.
- 🤖 **Servidor MCP para usar con IA**: Servidor MCP integrado para Web Scraping asistido por IA y extracción de datos. El servidor MCP presenta capacidades potentes y personalizadas que aprovechan Scrapling para extraer contenido específico antes de pasarlo a la IA (Claude/Cursor/etc), acelerando así las operaciones y reduciendo costos al minimizar el uso de tokens. ([video demo](https://www.youtube.com/watch?v=qyFk3ZNwOxE))

### Arquitectura de Alto Rendimiento y Probada en Batalla
- 🚀 **Ultrarrápido**: Rendimiento optimizado que supera a la mayoría de las bibliotecas de Web Scraping de Python.
- 🔋 **Eficiente en Memoria**: Estructuras de datos optimizadas y carga diferida para una huella de memoria mínima.
- ⚡ **Serialización JSON Rápida**: 10 veces más rápido que la biblioteca estándar.
- 🏗️ **Probado en batalla**: Scrapling no solo tiene una cobertura de pruebas del 92% y cobertura completa de type hints, sino que ha sido utilizado diariamente por cientos de Web Scrapers durante el último año.

### Experiencia Amigable para Desarrolladores/Web Scrapers
- 🎯 **Shell Interactivo de Web Scraping**: Shell IPython integrado opcional con integración de Scrapling, atajos y nuevas herramientas para acelerar el desarrollo de scripts de Web Scraping, como convertir solicitudes curl a solicitudes Scrapling y ver resultados de solicitudes en tu navegador.
- 🚀 **Úsalo directamente desde la Terminal**: Opcionalmente, ¡puedes usar Scrapling para hacer scraping de una URL sin escribir ni una sola línea de código!
- 🛠️ **API de Navegación Rica**: Recorrido avanzado del DOM con métodos de navegación de padres, hermanos e hijos.
- 🧬 **Procesamiento de Texto Mejorado**: Métodos integrados de regex, limpieza y operaciones de cadena optimizadas.
- 📝 **Generación Automática de Selectores**: Genera selectores CSS/XPath robustos para cualquier elemento.
- 🔌 **API Familiar**: Similar a Scrapy/BeautifulSoup con los mismos pseudo-elementos usados en Scrapy/Parsel.
- 📘 **Cobertura Completa de Tipos**: Type hints completos para excelente soporte de IDE y autocompletado de código. Todo el código fuente se escanea automáticamente con **PyRight** y **MyPy** en cada cambio.
- 🔋 **Imagen Docker Lista**: Con cada lanzamiento, se construye y publica automáticamente una imagen Docker que contiene todos los navegadores.

## Primeros Pasos

Aquí tienes un vistazo rápido de lo que Scrapling puede hacer sin entrar en profundidad.

### Uso Básico
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
page = StealthyFetcher.fetch('https://nopecha.com/demo/cloudflare')
data = page.css('#padded_content a').getall()
```
Automatización completa del navegador
```python
from scrapling.fetchers import DynamicFetcher, DynamicSession

with DynamicSession(headless=True, disable_resources=False, network_idle=True) as session:  # Mantén el navegador abierto hasta que termines
    page = session.fetch('https://quotes.toscrape.com/', load_dom=False)
    data = page.xpath('//span[@class="text"]/text()').getall()  # Selector XPath si lo prefieres

# O usa el estilo de solicitud de una sola vez, abre el navegador para esta solicitud, luego lo cierra después de terminar
page = DynamicFetcher.fetch('https://quotes.toscrape.com/')
data = page.css('.quote .text::text').getall()
```

### Spiders
Construye rastreadores completos con solicitudes concurrentes, múltiples tipos de sesión y Pause & Resume:
```python
from scrapling.spiders import Spider, Request, Response

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
Usa múltiples tipos de sesión en un solo Spider:
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
Pausa y reanuda rastreos largos con checkpoints ejecutando el Spider así:
```python
QuotesSpider(crawldir="./crawl_data").start()
```
Presiona Ctrl+C para pausar de forma ordenada — el progreso se guarda automáticamente. Después, cuando inicies el Spider de nuevo, pasa el mismo `crawldir`, y continuará desde donde se detuvo.

### Análisis Avanzado y Navegación
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
quotes = page.find_by_text('quote', tag='div')

# Navegación avanzada
quote_text = page.css('.quote')[0].css('.text::text').get()
quote_text = page.css('.quote').css('.text::text').getall()  # Selectores encadenados
first_quote = page.css('.quote')[0]
author = first_quote.next_sibling.css('.author::text')
parent_container = first_quote.parent

# Relaciones y similitud de elementos
similar_elements = first_quote.find_similar()
below_elements = first_quote.below_elements()
```
Puedes usar el parser directamente si no necesitas obtener sitios web, como se muestra a continuación:
```python
from scrapling.parser import Selector

page = Selector("<html>...</html>")
```
¡Y funciona exactamente de la misma manera!

### Ejemplos de Gestión de Session Async
```python
import asyncio
from scrapling.fetchers import FetcherSession, AsyncStealthySession, AsyncDynamicSession

async with FetcherSession(http3=True) as session:  # `FetcherSession` es consciente del contexto y puede funcionar tanto en patrones sync/async
    page1 = session.get('https://quotes.toscrape.com/')
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

Scrapling incluye una poderosa interfaz de línea de comandos:

[![asciicast](https://asciinema.org/a/736339.svg)](https://asciinema.org/a/736339)

Lanzar el Shell interactivo de Web Scraping
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
> Hay muchas características adicionales, pero queremos mantener esta página concisa, incluyendo el servidor MCP y el Shell Interactivo de Web Scraping. Consulta la documentación completa [aquí](https://scrapling.readthedocs.io/en/latest/)

## Benchmarks de Rendimiento

Scrapling no solo es potente, también es ultrarrápido. Los siguientes benchmarks comparan el parser de Scrapling con las últimas versiones de otras bibliotecas populares.

### Prueba de Velocidad de Extracción de Texto (5000 elementos anidados)

| # |    Biblioteca     | Tiempo (ms) | vs Scrapling |
|---|:-----------------:|:-----------:|:------------:|
| 1 |     Scrapling     |    2.02     |     1.0x     |
| 2 |   Parsel/Scrapy   |    2.04     |     1.01     |
| 3 |     Raw Lxml      |    2.54     |    1.257     |
| 4 |      PyQuery      |    24.17    |     ~12x     |
| 5 |    Selectolax     |    82.63    |     ~41x     |
| 6 |  MechanicalSoup   |   1549.71   |   ~767.1x    |
| 7 |   BS4 with Lxml   |   1584.31   |   ~784.3x    |
| 8 | BS4 with html5lib |   3391.91   |   ~1679.1x   |


### Rendimiento de Similitud de Elementos y Búsqueda de Texto

Las capacidades de búsqueda adaptativa de elementos de Scrapling superan significativamente a las alternativas:

| Biblioteca  | Tiempo (ms) | vs Scrapling |
|-------------|:-----------:|:------------:|
| Scrapling   |    2.39     |     1.0x     |
| AutoScraper |    12.45    |    5.209x    |


> Todos los benchmarks representan promedios de más de 100 ejecuciones. Ver [benchmarks.py](https://github.com/D4Vinci/Scrapling/blob/main/benchmarks.py) para la metodología.

## Instalación

Scrapling requiere Python 3.10 o superior:

```bash
pip install scrapling
```

Esta instalación solo incluye el motor de análisis y sus dependencias, sin ningún fetcher ni dependencias de línea de comandos.

### Dependencias Opcionales

1. Si vas a usar alguna de las características adicionales a continuación, los fetchers, o sus clases, necesitarás instalar las dependencias de los fetchers y sus dependencias del navegador de la siguiente manera:
    ```bash
    pip install "scrapling[fetchers]"

    scrapling install           # normal install
    scrapling install  --force  # force reinstall
    ```

    Esto descarga todos los navegadores, junto con sus dependencias del sistema y dependencias de manipulación de fingerprint.

    O puedes instalarlos desde el código en lugar de ejecutar un comando:
    ```python
    from scrapling.cli import install

    install([], standalone_mode=False)          # normal install
    install(["--force"], standalone_mode=False) # force reinstall
    ```

2. Características adicionales:
   - Instalar la característica del servidor MCP:
       ```bash
       pip install "scrapling[ai]"
       ```
   - Instalar características del Shell (Shell de Web Scraping y el comando `extract`):
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

## 🎓 Citas
Si has utilizado nuestra biblioteca con fines de investigación, por favor cítanos con la siguiente referencia:
```text
  @misc{scrapling,
    author = {Karim Shoair},
    title = {Scrapling},
    year = {2024},
    url = {https://github.com/D4Vinci/Scrapling},
    note = {An adaptive Web Scraping framework that handles everything from a single request to a full-scale crawl!}
  }
```

## Licencia

Este trabajo está licenciado bajo la Licencia BSD-3-Clause.

## Agradecimientos

Este proyecto incluye código adaptado de:
- Parsel (Licencia BSD)—Usado para el submódulo [translator](https://github.com/D4Vinci/Scrapling/blob/main/scrapling/core/translator.py)

---
<div align="center"><small>Diseñado y elaborado con ❤️ por Karim Shoair.</small></div><br>
