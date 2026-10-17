---
title: "Usa la extracción de datos de Scrapling en un spider de Scrapy"
description: "Convierte respuestas de Scrapy a Scrapling o añade un decorador a un callback. Conserva tu rastreador de Scrapy y usa los selectores y la búsqueda adaptativa de Scrapling."
---

# Integrar Scrapling en Scrapy {#integrating-scrapling-into-scrapy}

Si ya tienes un proyecto de Scrapy, no necesitas reescribirlo para usar la API de análisis de Scrapling. La integración convierte las respuestas de Scrapy en objetos [Response](../fetching/choosing.md#response-object) de Scrapling dentro de los callbacks de tu spider. Así, Scrapy sigue a cargo del rastreo y Scrapling se encarga de analizar el contenido.

!!! note "Instalación"

    Esta integración funciona con la instalación básica de Scrapling (`pip install scrapling`), sin extras. Solo requiere que Scrapy esté instalado, como ya lo está en un proyecto de Scrapy.

## Uso {#usage}

Añade el decorador `scrapling_response` a cualquier callback del spider. El argumento `response` que recibe será un `Response` de Scrapling:

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
            card = quote.parent
            yield {
                "text": quote.get_all_text(strip=True),
                "author": card.find("small", class_="author").text,
                "tags": [tag.text for tag in card.find_all("a", class_="tag")],
            }
        next_page = response.css("li.next a::attr(href)").get()
        if next_page:
            yield scrapy.Request(response.urljoin(next_page), callback=self.parse)
```

El decorador funciona con todos los tipos de callback que admite Scrapy: funciones normales, generadores, corrutinas y generadores asíncronos. Conserva el tipo, el nombre y el docstring del callback, por lo que la inspección de callbacks y los contratos de Scrapy siguen funcionando.

También puedes pasar la configuración de [Selector](../parsing/main_classes.md#selector) al decorador, que la enviará al `Response` generado:

```python
    @scrapling_response(adaptive=True, keep_comments=True)
    def parse_product(self, response):
        ...
```

Si tienes una respuesta de Scrapy fuera de un callback, por ejemplo en middlewares o pipelines, usa el conversor directamente:

```python
from scrapling.integrations.scrapy import convert_response

scrapling_response = convert_response(scrapy_response, keep_comments=False)
```

## Notas {#notes}

- Para visitar las páginas siguientes, devuelve `scrapy.Request(response.urljoin(href))` con yield, como en el ejemplo anterior. El método `Response.follow()` de Scrapling crea solicitudes para el [sistema de spiders de Scrapling](../spiders/getting-started.md), que Scrapy no entiende.
- Se crea una copia superficial del diccionario `meta` de la respuesta. Los objetos que otros middlewares guardan dentro siguen disponibles. Por ejemplo, con `scrapy-playwright`, la página sigue en `response.meta["playwright_page"]`.
- Las cookies se leen de los encabezados `Set-Cookie` originales y se guardan en el diccionario `cookies` de la respuesta.
