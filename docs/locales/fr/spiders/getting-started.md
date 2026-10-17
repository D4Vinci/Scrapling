---
title: "Créez votre premier robot d’exploration web en Python avec Scrapling"
description: "Créez un spider qui extrait des données, suit la pagination et exporte les résultats. Découvrez les URL de départ, les callbacks, les limites de domaine et robots.txt."
---

# Premiers pas {#getting-started}

## Introduction {#introduction}

!!! success "Avant de commencer"

    1. Lisez la page [Bases des fetchers](../fetching/choosing.md) pour connaître les types de fetcher et savoir quand utiliser chacun.
    2. Lisez la page [Classes principales](../parsing/main_classes.md) pour découvrir les classes [Selector](../parsing/main_classes.md#selector) et [Response](../fetching/choosing.md#response-object).
    3. Lisez la page [Architecture](architecture.md) pour comprendre le fonctionnement du système de spiders.

Le système de spiders permet d’explorer plusieurs pages en même temps avec quelques lignes de code. Si vous avez déjà utilisé Scrapy, son fonctionnement vous sera familier. Sinon, ce guide explique tout ce dont vous avez besoin pour commencer.

## Votre premier spider {#your-first-spider}

Un spider est une classe qui définit comment parcourir des sites et extraire leurs données. Voici l’exemple le plus simple :

```python
from scrapling.spiders import Spider, Response

class QuotesSpider(Spider):
    name = "quotes"
    start_urls = ["https://quotes.toscrape.com"]

    async def parse(self, response: Response):
        for quote in response.css("div.quote"):
            yield {
                "text": quote.css("span.text::text").get(""),
                "author": quote.css("small.author::text").get(""),
            }
```

Chaque spider a besoin de trois éléments :

1. **`name`** : un nom unique pour le spider.
2. **`start_urls`** : une liste d’URL à partir desquelles lancer l’exploration.
3. **`parse()`** : une méthode génératrice asynchrone qui traite chaque réponse et produit les résultats.

La méthode `parse()` contient la logique d’extraction. Vous utilisez les mêmes méthodes de sélection que dans les objets [Selector](../parsing/main_classes.md#selector)/[Response](../fetching/choosing.md#response-object) de Scrapling et produisez les éléments extraits sous forme de dictionnaires avec `yield`.

## Exécuter le spider {#running-the-spider}

Pour exécuter votre spider, créez une instance et appelez `start()` :

```python
result = QuotesSpider().start()
```

La méthode `start()` gère l’exécution asynchrone : vous n’avez pas à gérer les boucles d’événements. Pendant l’exécution, le spider écrit les événements dans le terminal. À la fin, il affiche des statistiques détaillées.

Ces statistiques sont aussi disponibles dans l’objet `CrawlResult` renvoyé :

```python
result = QuotesSpider().start()

# Access scraped items
for item in result.items:
    print(item["text"], "-", item["author"])

# Check statistics
print(f"Scraped {result.stats.items_scraped} items")
print(f"Made {result.stats.requests_count} requests")
print(f"Took {result.stats.elapsed_seconds:.1f} seconds")

# Did the crawl finish or was it paused?
print(f"Completed: {result.completed}")
```

## Suivre des liens {#following-links}

La plupart des explorations doivent suivre des liens entre plusieurs pages. Utilisez `response.follow()` pour créer les requêtes suivantes :

```python
from scrapling.spiders import Spider, Response

class QuotesSpider(Spider):
    name = "quotes"
    start_urls = ["https://quotes.toscrape.com"]

    async def parse(self, response: Response):
        # Extract items from the current page
        for quote in response.css("div.quote"):
            yield {
                "text": quote.css("span.text::text").get(""),
                "author": quote.css("small.author::text").get(""),
            }

        # Follow the "next page" link
        next_page = response.css("li.next a::attr(href)").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)
```

`response.follow()` résout les URL relatives à partir de l’URL de la page actuelle. Par défaut, il utilise aussi cette page comme valeur de l’en-tête `Referer`.

Vous pouvez envoyer les requêtes vers différents callbacks selon le type de page :

```python
async def parse(self, response: Response):
    for link in response.css("a.product-link::attr(href)").getall():
        yield response.follow(link, callback=self.parse_product)

async def parse_product(self, response: Response):
    yield {
        "name": response.css("h1::text").get(""),
        "price": response.css(".price::text").get(""),
    }
```

!!! note "Note"

    Tous les callbacks doivent être des méthodes génératrices asynchrones, avec `async def` et `yield`.

## Exporter les données {#exporting-data}

L’objet `ItemList` dans `result.items` contient des méthodes d’exportation :

```python
result = QuotesSpider().start()

# Export as JSON
result.items.to_json("quotes.json")

# Export as JSON with pretty-printing
result.items.to_json("quotes.json", indent=True)

# Export as JSON Lines (one JSON object per line)
result.items.to_jsonl("quotes.jsonl")

# Export as CSV or XML
result.items.to_csv("quotes.csv")
result.items.to_xml("quotes.xml")
```

Toutes créent les dossiers nécessaires s’ils n’existent pas encore.

`to_csv()` crée une colonne pour chaque clé trouvée dans les éléments. Si un élément n’a pas une clé, la cellule reste vide. Utilisez `fields=[...]` pour choisir les colonnes et leur ordre, ou `delimiter="\t"` pour créer un fichier TSV. `to_xml()` place chaque élément dans une balise `<item>`, sous une racine `<items>`. Vous pouvez changer ces deux noms avec `root_tag` et `item_tag`.

Dans les deux formats, les valeurs qui ne sont pas des scalaires simples, comme une liste ou un dictionnaire imbriqué, sont écrites en JSON pour ne perdre aucune donnée.

## Limiter les domaines {#filtering-domains}

Utilisez `allowed_domains` pour limiter le spider à certains domaines. Cela évite qu’il suive par erreur des liens vers d’autres sites :

```python
class MySpider(Spider):
    name = "my_spider"
    start_urls = ["https://example.com"]
    allowed_domains = {"example.com"}

    async def parse(self, response: Response):
        for link in response.css("a::attr(href)").getall():
            # Links to other domains are silently dropped
            yield response.follow(link, callback=self.parse)
```

Les sous-domaines sont inclus automatiquement. Par exemple, `allowed_domains = {"example.com"}` autorise aussi `sub.example.com`, `blog.example.com`, etc.

Chaque requête écartée est comptée dans `stats.offsite_requests_count`, pour que vous puissiez voir combien ont été ignorées.

## Respecter robots.txt {#robotstxt-compliance}

Définissez `robots_txt_obey = True` pour que le spider consulte les règles de robots.txt avant d’explorer un domaine :

```python
class PoliteSpider(Spider):
    name = "polite"
    start_urls = ["https://example.com"]
    robots_txt_obey = True

    async def parse(self, response: Response):
        for link in response.css("a::attr(href)").getall():
            yield response.follow(link, callback=self.parse)
```

Quand cette option est active, le spider :

1. **Télécharge robots.txt** pour tous les domaines de `start_urls` avant de commencer. Ces téléchargements se font en parallèle.
2. **Vérifie chaque requête** avec les règles `Disallow` du domaine. Les requêtes interdites sont écartées sans message et comptées dans `stats.robots_disallowed_count`.
3. **Respecte les directives `Crawl-delay` et `Request-rate`** en utilisant la plus grande valeur entre la directive et votre `download_delay`. robots.txt peut donc augmenter l’attente, mais jamais la réduire. Si AutoThrottle est actif, son délai maximal limite aussi cette valeur. Choisissez un `autothrottle_max_delay` assez élevé pour respecter l’attente demandée.

Les fichiers robots.txt sont téléchargés avec la session par défaut du spider et gardés en cache par domaine pendant toute l’exploration. Si un domaine absent de `start_urls` est découvert en cours de route, son robots.txt est téléchargé avant la première requête vers ce domaine.

**Note :** `robots_txt_obey` est désactivé par défaut pour éviter les changements de comportement inattendus. Son activation ne modifie pas les limites de concurrence (`concurrent_requests`, `concurrent_requests_per_domain`). Seule l’attente entre les requêtes est ajustée.

Si vous préférez ne pas choisir un `download_delay` à la main, définissez `autothrottle_enabled = True`. Le spider ajustera l’attente de chaque domaine selon la vitesse des réponses et ralentira en cas de blocage. Consultez [AutoThrottle](advanced.md#autothrottle).

## Pour aller plus loin {#whats-next}

Maintenant que vous connaissez les bases, vous pouvez consulter :

- [Requêtes et réponses](requests-responses.md) : priorité, suppression des doublons, métadonnées et plus encore.
- [Sessions](sessions.md) : différents types de fetcher, comme HTTP, navigateur et navigateur furtif, dans un même spider.
- [Gestion des proxies et des blocages](proxy-blocking.md) : rotation des proxies entre les requêtes et traitement des blocages.
- [Fonctions avancées](advanced.md) : contrôle de la concurrence, AutoThrottle, pause et reprise, streaming, hooks du cycle de vie et journaux.
