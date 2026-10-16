---
title: "Use a extração de dados do Scrapling em um spider do Scrapy"
description: "Converta respostas do Scrapy para Scrapling ou adicione um decorador a um callback. Mantenha seu rastreador do Scrapy e use os seletores e a busca adaptativa do Scrapling."
---

# Integrar Scrapling ao Scrapy {#integrating-scrapling-into-scrapy}

Se você já tem um projeto Scrapy, não precisa reescrevê-lo para usar a API de análise do Scrapling. A integração converte respostas do Scrapy em objetos [Response](../fetching/choosing.md#response-object) do Scrapling dentro dos callbacks do spider. Assim, o Scrapy continua cuidando do rastreamento, enquanto o Scrapling analisa o conteúdo.

!!! note "Instalação"

    Esta integração funciona com a instalação padrão do Scrapling (`pip install scrapling`), sem extras. Ela só precisa do Scrapy instalado, o que já acontece em um projeto Scrapy.

## Uso {#usage}

Adicione o decorador `scrapling_response` a qualquer callback do spider. O argumento `response` que ele recebe passa a ser um `Response` do Scrapling:

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

O decorador funciona com todos os tipos de callback aceitos pelo Scrapy: funções comuns, geradores, corrotinas e geradores assíncronos. Ele preserva o tipo, o nome e a docstring do callback, para que a inspeção de callbacks e os contratos do Scrapy continuem funcionando.

Você também pode passar configurações de [Selector](../parsing/main_classes.md#selector) ao decorador. Elas serão repassadas ao `Response` gerado:

```python
    @scrapling_response(adaptive=True, keep_comments=True)
    def parse_product(self, response):
        ...
```

Se você tiver uma resposta do Scrapy fora de um callback, por exemplo em middlewares ou pipelines, use o conversor diretamente:

```python
from scrapling.integrations.scrapy import convert_response

scrapling_response = convert_response(scrapy_response, keep_comments=False)
```

## Notas {#notes}

- Use yield com `scrapy.Request(response.urljoin(href))` para visitar as próximas páginas, como no exemplo acima. O método `Response.follow()` do Scrapling cria solicitações para o [sistema de spiders do Scrapling](../spiders/getting-started.md), que o Scrapy não entende.
- É feita uma cópia rasa do dicionário `meta` da resposta. Assim, os objetos salvos por outros middlewares continuam acessíveis. Por exemplo, com `scrapy-playwright`, a página continua em `response.meta["playwright_page"]`.
- Os cookies são lidos dos cabeçalhos `Set-Cookie` originais e colocados no dicionário `cookies` da resposta.
