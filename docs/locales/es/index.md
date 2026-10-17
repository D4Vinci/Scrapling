---
title: "Scrapling: framework de web scraping para Python"
description: "Scrapling: extrae datos de la web moderna de forma sencilla."
---

<style>
.md-typeset h1 {
  display: none;
}
[data-md-color-scheme="default"] .only-dark { display: none; }
[data-md-color-scheme="slate"] .only-light { display: none; }
</style>

<br/>
<div align="center">
    <a href="index.html" alt="Portada">
        <img alt="Scrapling" src="assets/cover_light.svg" class="only-light">
        <img alt="Scrapling" src="assets/cover_dark.svg" class="only-dark">
    </a>
</div>

<h2 align="center"><i>Extrae datos de la web moderna de forma sencilla</i></h2><br>

Scrapling es un framework de web scraping para Python. Reúne solicitudes HTTP rápidas, navegadores sigilosos, análisis de páginas y rastreo concurrente en una sola biblioteca.

Extrae datos de páginas estáticas, ejecuta JavaScript, interactúa con sitios web y accede a las API que usan. Crea crawlers con sesiones reutilizables, rotación de proxies, reintentos automáticos, pausa y reanudación, y exportación de datos integrada.

Úsalo desde Python, la terminal o tu agente de IA mediante el servidor MCP y Agent Skill. Scrapling cubre todo el proceso, desde extraer unos campos hasta guardar un sitio completo como archivos Markdown limpios.

## Qué puedes hacer con Scrapling {#what-you-can-do-with-scrapling}

- **[Obtener páginas e interactuar](fetching/choosing.md)**: Solicitudes HTTP rápidas, navegadores sigilosos, ejecución de JavaScript, gestión de Cloudflare Turnstile e Interstitial, sesiones persistentes y captura de respuestas de API en segundo plano.
- **[Analizar y extraer](parsing/selection.md)**: Búsqueda con CSS, XPath, texto y expresiones regulares, seguimiento de elementos cuando cambia la página, búsqueda de elementos similares y salida en Markdown limpio.
- **[Rastrear y exportar](spiders/getting-started.md)**: Spiders concurrentes, rotación de proxies, reintentos, AutoThrottle, pausa y reanudación, resultados en streaming, plantillas listas para usar y exportación a JSON, JSONL, CSV y XML.
- **[Extraer datos con IA o desde la terminal](ai/mcp-server.md)**: Un servidor MCP para que los agentes de IA naveguen y extraigan datos, un Agent Skill, comandos CLI y una consola interactiva.

Empieza con una sola página:

```python
from scrapling.fetchers import Fetcher

page = Fetcher.get('https://quotes.toscrape.com/')
quotes = page.css('.quote .text::text').getall()
print(quotes)
```

O extrae más datos con un spider:

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

Este ejemplo imprime `10` y guarda las citas y sus autores en `quotes.json`.

## Patrocinadores principales {#top-sponsors}

--8<-- "sponsors.html"

<i><sub>¿Quieres mostrar tu anuncio aquí? Haz clic [aquí](https://github.com/sponsors/D4Vinci), elige un plan y aprovecha sus ventajas.</sub></i>

## Funciones principales {#key-features}

### Spiders: un framework completo de rastreo {#spiders-a-full-crawling-framework}
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

### Obtención de páginas con soporte de sesiones {#advanced-websites-fetching-with-session-support}
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

### Análisis de páginas y extracción de datos {#parsing-and-data-extraction}
- 🔄 **Seguimiento de elementos**: Encuentra los elementos después de que cambie el sitio mediante algoritmos de similitud.
- 🎯 **Selección flexible**: Usa selectores CSS y XPath, filtros, texto, expresiones regulares y más.
- 🔍 **Elementos similares**: Encuentra automáticamente elementos parecidos a los que ya has localizado.

### Funciones de IA {#ai-features}
- 🤖 **Servidor MCP**: Permite que los asistentes y agentes de IA, como Claude y Cursor, extraigan datos con Scrapling mediante solicitudes HTTP, acciones del navegador, capturas de pantalla, estado de inicio de sesión guardado y respuestas de API en segundo plano. Usa nuestro navegador sigiloso y herramientas que ayudan a los modelos adecuados a resolver CAPTCHA, además del solucionador de Cloudflare. Reduce el contenido enviado al modelo, bloquea anuncios y lo protege de la inyección de instrucciones (prompt injection). También admite navegadores remotos por CDP y conexiones HTTP con opciones de autenticación. ([Vídeo de demostración](https://www.youtube.com/watch?v=qyFk3ZNwOxE))
- 🧠 **Agent Skill**: Un [Agent Skill](ai/agent-skill.md) listo para instalar que enseña la biblioteca a los agentes de programación, para que escriban código que coincida con la API actual.
- 📚 **Markdown listo para RAG**: Convierte una página en Markdown limpio y preparado para modelos de lenguaje con una línea (`page.markdown()`), o guarda un sitio completo como archivos Markdown con la plantilla `ContentSpider`. No requiere un modelo de lenguaje durante el proceso. ([Documentación](ai/building-rag-systems.md))

### Alto rendimiento y uso probado {#high-performance-battle-tested-architecture}
- 🚀 **Alta velocidad**: Rendimiento optimizado que supera a la mayoría de las bibliotecas de web scraping para Python.
- 🔋 **Bajo consumo de memoria**: Estructuras de datos optimizadas y carga solo cuando se necesita.
- ⚡ **Conversión rápida a JSON**: 10 veces más rápida que la biblioteca estándar.
- 🏗️ **Probado en la práctica**: Las pruebas cubren el 92% de Scrapling y todo el código tiene anotaciones de tipos. Cientos de personas lo han usado a diario para extraer datos durante el último año.

### Herramientas para desarrollar y extraer datos {#developerweb-scraper-friendly-experience}
- 🎯 **Consola interactiva**: Consola IPython opcional integrada con Scrapling, con atajos y herramientas para escribir scripts más rápido. Convierte solicitudes curl en solicitudes de Scrapling y muestra los resultados en el navegador.
- 🚀 **Uso desde la terminal**: Extrae los datos de una URL sin escribir código.
- 🛠️ **Navegación por el DOM**: Recorre los elementos padre, hermanos e hijos.
- 🧬 **Procesamiento de texto**: Expresiones regulares, limpieza de texto y operaciones de cadenas optimizadas.
- 📝 **Generación de selectores**: Genera selectores CSS y XPath fiables para cualquier elemento.
- 🔌 **API conocida**: Similar a Scrapy y BeautifulSoup, con los mismos pseudoelementos que Scrapy y Parsel.
- 🤝 **Integración directa con Scrapy**: Añade el decorador `scrapling_response` a un callback para analizar las respuestas que ya obtienes con el parser de Scrapling, sin reescribir tu programa.
- 📘 **Anotaciones de tipos completas**: Ayudan al editor a comprobar y completar el código. Todo el código se revisa automáticamente con **PyRight** y **MyPy** en cada cambio.
- 🔋 **Imagen Docker lista para usar**: Con cada versión se crea y publica automáticamente una imagen Docker que contiene todos los navegadores.


## Historial de estrellas {#star-history}
Las estrellas de Scrapling en GitHub han aumentado de forma constante desde su lanzamiento, como muestra el gráfico.

<div id="chartContainer">
  <a href="https://github.com/D4Vinci/Scrapling">
    <img id="chartImage" alt="Historial de estrellas" loading="lazy" src="https://api.star-history.com/svg?repos=D4Vinci/Scrapling&type=Date" height="400"/>
  </a>
</div>

<script>
const observer = new MutationObserver((mutations) => {
  mutations.forEach((mutation) => {
    if (mutation.attributeName === 'data-md-color-media') {
      const colorMedia = document.body.getAttribute('data-md-color-media');
      const isDarkScheme = document.body.getAttribute('data-md-color-scheme') === 'slate';
      const chartImg = document.querySelector('#chartImage');
      const baseUrl = 'https://api.star-history.com/svg?repos=D4Vinci/Scrapling&type=Date';
      
      if (colorMedia === '(prefers-color-scheme)' ? isDarkScheme : colorMedia.includes('dark')) {
        chartImg.src = `${baseUrl}&theme=dark`;
      } else {
        chartImg.src = baseUrl;
      }
    }
  });
});

observer.observe(document.body, {
  attributes: true,
  attributeFilter: ['data-md-color-media', 'data-md-color-scheme']
});
</script>


## Instalación {#installation}
Scrapling requiere Python 3.10 o posterior:

```bash
pip install scrapling
```

!!! warning "Aviso"

    Este comando solo instala el parser y sus dependencias, sin fetchers ni herramientas de línea de comandos. Si no instalas nada más, importar desde `scrapling.fetchers` o `scrapling.spiders`, como en los ejemplos anteriores, produce `ModuleNotFoundError`. Para usar fetchers o spiders, instala primero las dependencias de los fetchers como se indica a continuación.

### Dependencias opcionales {#optional-dependencies}

1. Para usar los fetchers, sus clases o las funciones adicionales siguientes, instala las dependencias de los fetchers y los navegadores:
    ```bash
    pip install "scrapling[fetchers]"
    
    scrapling install           # normal install
    scrapling install  --force  # force reinstall
    ```

    Esto descarga todos los navegadores, las dependencias del sistema y las herramientas para modificar las huellas del navegador.

    También puedes instalarlos desde Python en lugar de ejecutar un comando:
    ```python
    from scrapling.cli import install
    
    install([], standalone_mode=False)          # normal install
    install(["--force"], standalone_mode=False) # force reinstall
    ```

2. Funciones adicionales:


     - Instalar el servidor MCP:
       ```bash
       pip install "scrapling[ai]"
       ```
     - Instalar las dependencias para [crear sistemas RAG](ai/building-rag-systems.md):
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
   Ejecuta `scrapling install` para usar fetchers de navegador. Las solicitudes HTTP no necesitan un navegador.

### Docker {#docker}
También puedes descargar desde DockerHub una imagen Docker con todos los extras y navegadores:
```bash
docker pull pyd4vinci/scrapling
```
O descargarla desde el registro de GitHub:
```bash
docker pull ghcr.io/d4vinci/scrapling:latest
```
La imagen se crea desde la rama principal del repositorio y se publica automáticamente con GitHub Actions.

## Organización de la documentación {#how-the-documentation-is-organized}
La documentación de Scrapling es amplia, así que seguimos el [modelo de documentación Diátaxis](https://diataxis.fr/).

## Apoyo {#support}

Si te gusta Scrapling y quieres apoyar su desarrollo:

- ⭐ Dale una estrella al [repositorio de GitHub](https://github.com/D4Vinci/Scrapling).
- 🚀 Síguenos en [Twitter](https://x.com/Scrapling_dev) y únete al [servidor de Discord](https://discord.gg/EMgGbDceNQ).
- 💝 Puedes [patrocinar el proyecto o invitarme a un café](donate.md). :wink:
- 🐛 Informa de errores y sugiere funciones en [GitHub Issues](https://github.com/D4Vinci/Scrapling/issues).

## Licencia {#license}

Este proyecto usa la licencia BSD-3. Consulta el archivo [LICENSE](https://github.com/D4Vinci/Scrapling/blob/main/LICENSE) para más detalles.
