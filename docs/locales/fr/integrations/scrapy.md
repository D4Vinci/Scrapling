---
title: "Utiliser l’analyse de Scrapling dans un spider Scrapy"
description: "Convertissez les réponses Scrapy en Scrapling ou ajoutez un décorateur à un callback. Gardez votre robot Scrapy et utilisez les sélecteurs et l’analyse adaptative de Scrapling."
---

# Intégrer Scrapling à Scrapy {#integrating-scrapling-into-scrapy}

Si vous avez déjà un projet Scrapy, vous n’avez pas besoin de le réécrire pour utiliser l’API d’analyse de Scrapling. L’intégration convertit les réponses Scrapy en objets [Response](../fetching/choosing.md#response-object) de Scrapling directement dans les callbacks du spider. Scrapy continue ainsi de gérer l’exploration, tandis que Scrapling analyse le contenu.

!!! note "Installation"

    Cette intégration fonctionne avec l’installation standard de Scrapling (`pip install scrapling`), sans extras. Elle demande seulement que Scrapy soit installé, ce qui est déjà le cas dans un projet Scrapy.

## Utilisation {#usage}

Ajoutez le décorateur `scrapling_response` à un callback du spider. L’argument `response` qu’il reçoit devient un `Response` de Scrapling :

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

Le décorateur fonctionne avec tous les types de callback pris en charge par Scrapy : fonctions classiques, générateurs, coroutines et générateurs asynchrones. Il conserve le type, le nom et la docstring du callback. L’inspection des callbacks et les contrats de Scrapy continuent donc de fonctionner.

Vous pouvez aussi passer une configuration de [Selector](../parsing/main_classes.md#selector) au décorateur. Elle sera transmise au `Response` créé :

```python
    @scrapling_response(adaptive=True, keep_comments=True)
    def parse_product(self, response):
        ...
```

Si vous avez une réponse Scrapy en dehors d’un callback, par exemple dans un middleware ou un pipeline, utilisez directement le convertisseur :

```python
from scrapling.integrations.scrapy import convert_response

scrapling_response = convert_response(scrapy_response, keep_comments=False)
```

## Notes {#notes}

- Utilisez yield avec `scrapy.Request(response.urljoin(href))` pour visiter les pages suivantes, comme dans l’exemple ci-dessus. La méthode `Response.follow()` de Scrapling crée des requêtes pour le [système de spiders de Scrapling](../spiders/getting-started.md), que Scrapy ne comprend pas.
- Une copie superficielle du dictionnaire `meta` de la réponse est créée. Les objets enregistrés par d’autres middlewares restent donc accessibles. Par exemple, avec `scrapy-playwright`, la page reste dans `response.meta["playwright_page"]`.
- Les cookies sont lus dans les en-têtes `Set-Cookie` bruts et ajoutés au dictionnaire `cookies` de la réponse.
