---
title: "Requêtes, callbacks et Response.follow dans les spiders"
description: "Créez des requêtes, transmettez des métadonnées et suivez des liens avec response.follow. Découvrez les callbacks, les priorités et la suppression des doublons."
---

# Requêtes et réponses {#requests-responses}

!!! success "Avant de commencer"

    1. Lisez la page [Premiers pas](getting-started.md) pour apprendre à créer et exécuter un spider simple.

Cette page explique l’objet `Request` : comment créer des requêtes, transmettre des données entre callbacks, gérer la priorité et les doublons, et suivre des liens avec `response.follow()`.

## L’objet Request {#the-request-object}

Un `Request` représente une URL à récupérer. Vous pouvez créer des requêtes directement ou avec `response.follow()` :

```python
from scrapling.spiders import Request

# Direct construction
request = Request(
    "https://example.com/page",
    callback=self.parse_page,
    priority=5,
)

# Via response.follow (preferred in callbacks)
request = response.follow("/page", callback=self.parse_page)
```

Voici tous les arguments acceptés par `Request` :

| Argument | Type | Valeur par défaut | Description |
|----------|------|-------------------|-------------|
| `url` | `str` | *obligatoire* | URL à récupérer |
| `sid` | `str` | `""` | Identifiant de session. Envoie la requête vers une session précise (voir [Sessions](sessions.md)) |
| `callback` | `callable` | `None` | Méthode génératrice asynchrone qui traite la réponse. Utilise `parse()` par défaut |
| `priority` | `int` | `0` | Les valeurs les plus élevées sont traitées en premier |
| `dont_filter` | `bool` | `False` | Si la valeur est `True`, autorise les requêtes en double |
| `meta` | `dict` | `{}` | Métadonnées de votre choix transmises à la réponse |
| `**kwargs` | | | Arguments supplémentaires transmis à la méthode de récupération de la session, comme `headers`, `method` ou `data` |

Les arguments supplémentaires sont envoyés directement à la session. Par exemple, pour faire une requête POST :

```python
yield Request(
    "https://example.com/api",
    method="POST",
    data={"key": "value"},
    callback=self.parse_result,
)
```

## Response.follow() {#responsefollow}

`response.follow()` est la méthode recommandée pour créer de nouvelles requêtes dans un callback. Elle offre plusieurs avantages par rapport à la création directe d’objets `Request` :

- Les **URL relatives** sont résolues à partir de l’URL de la page actuelle.
- L’**en-tête Referer** utilise l’URL de la page actuelle par défaut.
- Les **arguments de session** de la requête d’origine sont repris, comme les en-têtes et les réglages du proxy, sauf `method`, `params`, `data`, `json`, `files` et `multipart`. Les liens sont donc suivis avec de simples requêtes GET.
- Le **callback, l’identifiant de session et la priorité** sont repris de la requête d’origine si vous ne les indiquez pas.

```python
async def parse(self, response: Response):
    # Minimal - inherits callback, sid, priority from current request
    yield response.follow("/next-page")

    # Override specific fields
    yield response.follow(
        "/product/123",
        callback=self.parse_product,
        priority=10,
    )

    # Pass additional metadata to
    yield response.follow(
        "/details",
        callback=self.parse_details,
        meta={"category": "electronics"},
    )
```

| Argument | Type | Valeur par défaut | Description |
|----------|------|-------------------|-------------|
| `url` | `str` | *obligatoire* | URL à suivre, absolue ou relative |
| `sid` | `str` | `""` | Identifiant de session. Repris de la requête d’origine s’il est vide |
| `callback` | `callable` | `None` | Méthode callback. Reprise de la requête d’origine si la valeur est `None` |
| `priority` | `int` | `None` | Priorité. Reprise de la requête d’origine si la valeur est `None` |
| `dont_filter` | `bool` | `False` | Autorise les requêtes en double |
| `meta` | `dict` | `None` | Métadonnées combinées avec celles de la réponse |
| **`referer_flow`** | `bool` | `True` | Utilise l’URL actuelle comme en-tête Referer |
| `**kwargs` | | | Combinés avec les arguments de session de la requête d’origine |

### Désactiver l’envoi de Referer {#disabling-referer-flow}

Par défaut, `response.follow()` utilise l’URL de la page actuelle comme en-tête `Referer`. Pour le désactiver :

```python
yield response.follow("/page", referer_flow=False)
```

## Callbacks {#callbacks}

Les callbacks sont des méthodes génératrices asynchrones du spider qui traitent les réponses. Elles doivent utiliser `yield` pour produire un de ces trois types :

- **`dict`** : un élément extrait, ajouté aux résultats.
- **`Request`** : une nouvelle requête, ajoutée à la file.
- **`None`** : ignoré sans message.

```python
class MySpider(Spider):
    name = "my_spider"
    start_urls = ["https://example.com"]

    async def parse(self, response: Response):
        # Yield items (dicts)
        yield {"url": response.url, "title": response.css("title::text").get("")}

        # Yield follow-up requests
        for link in response.css("a::attr(href)").getall():
            yield response.follow(link, callback=self.parse_page)

    async def parse_page(self, response: Response):
        yield {"content": response.css("article::text").get("")}
```

!!! tip "Note"

    Tous les callbacks doivent utiliser `async def` et `yield`, pas `return`. Même si un callback produit seulement des éléments, sans nouvelle requête, il doit rester un générateur asynchrone.

## Priorité des requêtes {#request-priority}

Les requêtes dont la priorité est la plus élevée sont traitées en premier. Cela sert quand certaines pages doivent être traitées avant les autres :

```python
async def parse(self, response: Response):
    # High priority - process product pages first
    for link in response.css("a.product::attr(href)").getall():
        yield response.follow(link, callback=self.parse_product, priority=10)

    # Low priority - pagination links processed after products
    next_page = response.css("a.next::attr(href)").get()
    if next_page:
        yield response.follow(next_page, callback=self.parse, priority=0)
```

Avec `response.follow()`, la priorité est reprise de la requête d’origine, sauf si vous en définissez une autre.

## Supprimer les doublons {#deduplication}

Le spider évite les requêtes en double grâce à une empreinte calculée à partir de l’URL, de la méthode HTTP, du corps et de l’identifiant de session. Si deux requêtes ont la même empreinte, la seconde est écartée sans message.

Pour autoriser une requête en double, par exemple pour revenir sur une page après une connexion, utilisez `dont_filter=True` :

```python
yield Request("https://example.com/dashboard", dont_filter=True, callback=self.parse_dashboard)

# Or with response.follow
yield response.follow("/dashboard", dont_filter=True, callback=self.parse_dashboard)
```

Vous pouvez choisir les données incluses dans l’empreinte avec ces attributs de classe du spider :

| Attribut | Valeur par défaut | Effet |
|----------|-------------------|-------|
| `fp_include_kwargs` | `False` | Inclut dans l’empreinte les arguments supplémentaires transmis à la méthode de récupération de la session, comme les en-têtes |
| `fp_keep_fragments` | `False` | Garde les fragments d’URL (`#section`) lors du calcul de l’empreinte |
| `fp_include_headers` | `False` | Inclut les en-têtes de la requête dans l’empreinte |

Par exemple, pour traiter `https://example.com/page#section1` et `https://example.com/page#section2` comme des URL différentes :

```python
class MySpider(Spider):
    name = "my_spider"
    fp_keep_fragments = True
    # ...
```

## Métadonnées de la requête {#request-meta}

Le dictionnaire `meta` permet de transmettre des données entre callbacks. Il est utile quand vous avez besoin d’informations d’une page pour en traiter une autre :

```python
async def parse(self, response: Response):
    for product in response.css("div.product"):
        category = product.css("span.category::text").get("")
        link = product.css("a::attr(href)").get()
        if link:
            yield response.follow(
                link,
                callback=self.parse_product,
                meta={"category": category},
            )

async def parse_product(self, response: Response):
    yield {
        "name": response.css("h1::text").get(""),
        "price": response.css(".price::text").get(""),
        # Access meta from the request
        "category": response.meta.get("category", ""),
    }
```

Avec `response.follow()`, les métadonnées de la réponse actuelle sont combinées avec les nouvelles valeurs fournies. Les nouvelles valeurs ont priorité.

Le système de spiders enregistre aussi certaines métadonnées automatiquement. Par exemple, quand la rotation des proxies est active, le proxy utilisé pour une requête est disponible dans `response.meta["proxy"]`.
