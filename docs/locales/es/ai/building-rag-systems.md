---
title: "Convierte sitios web a Markdown para RAG con Scrapling"
description: "Convierte respuestas a Markdown o usa ContentSpider para recopilar un sitio web. Prepara textos para dividirlos e indexarlos en un sistema RAG."
---

# Crear sistemas RAG con Scrapling {#building-rag-systems-with-scrapling}

La calidad de un sistema RAG depende del texto que recibe. El HTML sin procesar gasta tokens en etiquetas, navegación, scripts y contenido de seguimiento. Incluso puede llevar instrucciones maliciosas ocultas hasta tu LLM. Scrapling convierte páginas y sitios enteros en Markdown limpio, elimina ese contenido oculto y no necesita un LLM en el proceso. Así, la carga de datos es rápida y no tiene un coste por página.

## Instalación {#installation}

```bash
pip install "scrapling[rag]"

scrapling install
```

El extra `rag` instala los fetchers con soporte para convertir a Markdown. Los extras `ai`, `shell` y `all` también lo incluyen. El comando `scrapling install` descarga las dependencias del navegador, que solo necesitas para los fetchers que usan un navegador.

## Convertir una página a Markdown {#one-page-to-markdown}

Cada [Response](../fetching/choosing.md#response-object) tiene un método `markdown()`:

```python
from scrapling.fetchers import Fetcher

markdown = Fetcher.get("https://example.com").markdown(main_content_only=True)
```

Funciona con todos los fetchers, así que también puedes obtener páginas protegidas por Cloudflare con una sola línea:

```python
from scrapling.fetchers import StealthyFetcher

markdown = StealthyFetcher.fetch("https://protected.example.com", solve_cloudflare=True).markdown(main_content_only=True)
```

Dos argumentos controlan el resultado:

- `main_content_only`: Convierte solo el contenido dentro de la etiqueta `<body>` de la página.
- `css_selector`: Convierte solo los elementos que coinciden con un selector CSS y une todas las coincidencias. Úsalo para extraer la parte que necesitas y ahorrar tokens:

```python
markdown = Fetcher.get("https://example.com/docs/page").markdown(css_selector="article")
```

Sin importar los argumentos que uses, los scripts, estilos y contenidos ocultos siempre se eliminan antes de la conversión. Es la misma limpieza que usa el [servidor MCP](mcp-server.md) para proteger a los agentes de IA de la inyección de instrucciones. Elimina elementos ocultos mediante estilos en línea, elementos con `aria-hidden="true"`, slots ocultos, etiquetas `<template>`, comentarios HTML y caracteres de ancho cero. El servidor MCP aplica esta limpieza con `main_content_only=True`.

## Convertir un sitio entero en una colección de Markdown {#a-whole-website-to-a-markdown-corpus}

La plantilla `ContentSpider` rastrea un sitio web y convierte cada página. Usa el [sistema de spiders](../spiders/architecture.md), que ya incluye concurrencia, AutoThrottle, respeto de robots.txt y pausa y reanudación:

```python
from scrapling.spiders import ContentSpider

class DocsSpider(ContentSpider):
    name = "docs"
    start_urls = ["https://example.com/docs/"]
    allowed_domains = {"example.com"}
    output_dir = "docs_markdown"
    max_pages = 200

result = DocsSpider().start()
result.items.to_jsonl("docs.jsonl")
```

Cada página rastreada se convierte en un elemento con las claves `url`, `title` y `markdown`. Si defines `output_dir`, cada página también se guarda en un archivo Markdown cuyo nombre se basa en su URL. Así, el ejemplo anterior genera tanto una carpeta de archivos `.md` como un archivo `docs.jsonl` listo para cargar.

La plantilla requiere `allowed_domains` para limitar el rastreo al sitio indicado. Estas son las opciones:

- `css_selector` / `main_content_only`: Se pasan a `markdown()` para cada página. `main_content_only` está activado de forma predeterminada.
- `output_dir`: Si se define, escribe un archivo Markdown por página.
- `max_pages`: Número máximo de páginas que se convertirán. Las solicitudes que ya estén en la cola al llegar al límite aún pueden obtenerse, pero no se convierten. El valor `0`, predeterminado, desactiva el límite.

De forma predeterminada, se siguen todos los enlaces dentro de `allowed_domains`. Como la plantilla se basa en [CrawlSpider](../spiders/generic-templates.md#crawlspider), puedes redefinir `rules()` con tu propio [LinkExtractor](../spiders/generic-templates.md#linkextractor-reference) para controlar el rastreo. `allow` lo limita a los patrones de URL que quieres, y `deny` excluye los que no quieres, como páginas de acceso, listas de etiquetas o versiones para imprimir:

```python
from scrapling.spiders import CrawlRule, LinkExtractor, ContentSpider

class DocsSpider(ContentSpider):
    name = "docs"
    start_urls = ["https://example.com/"]
    allowed_domains = {"example.com"}

    def rules(self):
        return [CrawlRule(LinkExtractor(allow=r"/docs/", deny=[r"/docs/changelog/", r"\?print="]))]
```

`deny` tiene prioridad sobre `allow`. Una regla puede incluir `priority` o un hook `process_request`, como en cualquier **CrawlSpider**.

## Cargar los datos en un almacén de vectores {#feeding-a-vector-store}

Puedes usar el archivo JSONL en cualquier proceso de creación de embeddings. Este es un ejemplo básico:

```python
import json

with open("docs.jsonl", encoding="utf-8") as f:
    for line in f:
        page = json.loads(line)
        for chunk in split_into_chunks(page["markdown"]):
            vector_store.add(text=chunk, metadata={"url": page["url"], "title": page["title"]})
```

Usa `css_selector` en el spider para quitar el contenido repetido antes de dividir el texto, en lugar de limpiarlo después. Cuanto menos contenido irrelevante incluyas en los embeddings, mejores serán los resultados de búsqueda.

## Alternativas interactivas {#interactive-alternatives}

Si prefieres extraer datos mediante una conversación, el [servidor MCP](mcp-server.md) da a tu chatbot de IA herramientas con la misma extracción a Markdown. La [Agent skill](agent-skill.md) enseña a los agentes de programación a escribir este código por su cuenta.
