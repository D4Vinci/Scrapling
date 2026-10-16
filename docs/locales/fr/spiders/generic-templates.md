---
title: "Modèles de spiders pour les liens, plans de site, flux et Markdown"
description: "Choisissez CrawlSpider, SitemapSpider, XMLFeedSpider, CSVFeedSpider ou ContentSpider. Définissez des règles pour collecter des pages, des lignes de flux ou des documents Markdown."
---

# Modèles génériques de spiders {#generic-spider-templates}

La plupart des explorations suivent l’un de ces deux modèles : suivre les liens qui correspondent à une règle, ou parcourir toutes les URL d’un plan de site. Scrapling fournit des modèles pour les deux, pour vous éviter de réécrire la même logique de `parse()` à chaque fois.

`CrawlSpider` et `SitemapSpider` utilisent `LinkExtractor`, qui extrait les URL d’un `Response` ou filtre une URL avec `matches()`. `SitemapSpider` analyse aussi le contenu de sitemap.xml et sitemap_index.xml, avec ou sans compression gzip.

Vous pouvez utiliser `LinkExtractor` directement dans n’importe quel `Spider.parse()`. Les modèles vous évitent simplement de relier ces composants vous-même.

## CrawlSpider {#crawlspider}

`CrawlSpider` suit les liens automatiquement selon les règles que vous définissez.

```python
from scrapling.spiders import CrawlSpider, CrawlRule, LinkExtractor

class QuotesSpider(CrawlSpider):
    name = "blog"
    start_urls = ["https://quotes.toscrape.com/"]

    def rules(self):
        return [
            CrawlRule(LinkExtractor(allow=r"/author/"), callback=self.parse_author),
            CrawlRule(LinkExtractor(allow=r"/page/\d+/")),  # follow pagination, no callback
        ]

    async def parse_author(self, response):
        yield {
            '.author-title': response.css('.author-title::text').get(),
            "birthday": response.css('.author-born-date::text').get(),
            "url": response.url,
        }

result = QuotesSpider().start()
```

Un `CrawlRule` associe un `LinkExtractor` à trois options : `callback`, une méthode du spider ; `priority`, pour changer la priorité du `Request` produit ; et `process_request`, une méthode qui modifie chaque `Request` avant qu’il soit produit. Le `parse()` par défaut applique toutes les règles à chaque réponse et produit un `Request` pour chaque URL correspondante.

Si une règle n’a pas de callback, les URL correspondantes passent au `parse()` par défaut du spider. C’est pratique pour la pagination : vous pouvez extraire les liens des pages suivantes sans créer une méthode distincte pour les traiter.

### Ordre d’exploration {#crawl-order}

Définissez `crawl_strategy` sur `CrawlSpider` ou ses sous-classes, dont `ContentSpider`, pour choisir la prochaine requête en attente :

| `crawl_strategy` | Ordre des requêtes avec le même `Request.priority` |
|------------------|---------------------------------------------------|
| `"bfs"` (par défaut) | La requête la plus ancienne dans la file passe en premier |
| `"dfs"` | La dernière requête ajoutée passe en premier |

Le Scheduler choisit toujours les requêtes avec le plus grand `Request.priority` en premier. La stratégie ne trie que les requêtes de même priorité.

Définissez `concurrent_requests = 1` pour traiter une requête à la fois dans l’ordre choisi. Les URL en double restent filtrées : retrouver une URL ne déplace pas sa requête dans la file. Avec des requêtes parallèles, le traitement des pages peut se terminer dans un autre ordre et les niveaux ou branches de l’exploration peuvent se chevaucher.

Gardez le même `crawl_strategy` quand vous reprenez depuis un point de reprise.

### Combiner les règles avec votre propre logique {#combining-rules-with-custom-logic}

Redéfinissez `parse()` et appelez `super().parse(response)` pour garder le comportement des règles et ajouter vos propres résultats :

```python
class MySpider(CrawlSpider):
    def rules(self):
        return [CrawlRule(LinkExtractor(allow=r"/posts/"), callback=self.parse_post)]

    async def parse(self, response):
        yield {"page_url": response.url}
        async for req in super().parse(response):
            yield req
```

### Modifier les requêtes avec `process_request` {#mutating-requests-with-process_request}

```python
def add_priority(self, request, response):
    request.priority = 10
    return request

def rules(self):
    return [CrawlRule(
        LinkExtractor(allow=r"/posts/"),
        callback=self.parse_post,
        process_request=self.add_priority,
    )]
```

## SitemapSpider {#sitemapspider}

`SitemapSpider` démarre l’exploration avec les URL de sitemap.xml. Il utilise la même API `rules()` que `CrawlSpider`, donc la configuration est similaire.

```python
from scrapling.spiders import SitemapSpider, CrawlRule, LinkExtractor

class MySitemap(SitemapSpider):
    name = "sm"
    sitemap_urls = ["https://example.com/sitemap.xml"]

    def rules(self):
        return [
            CrawlRule(LinkExtractor(allow=r"/posts/"), callback=self.parse_post),
            CrawlRule(LinkExtractor(allow=r"/products/"), callback=self.parse_product),
        ]

    async def parse_post(self, response):
        yield {"title": response.css("h1::text").get()}

    async def parse_product(self, response):
        yield {"sku": response.css(".sku::text").get()}

result = MySitemap().start()
```

### Choisir le callback de chaque URL {#how-urls-are-dispatched}

Pour chaque URL du plan de site, `SitemapSpider` vérifie `LinkExtractor.matches(url)` pour chaque règle dans l’ordre. La première règle correspondante est retenue, et un `Request` est produit avec son callback. Si aucune règle ne correspond et que `rules()` contient des règles, l’URL est écartée. Si `rules()` renvoie une liste vide, toutes les URL passent à la méthode `parse()` du spider. Vous devez redéfinir cette méthode, car elle lève `NotImplementedError` par défaut.

### Index de plans de site {#sitemap-indexes}

Quand `SitemapSpider` rencontre un `<sitemapindex>`, un plan qui répertorie d’autres plans de site, il parcourt automatiquement chaque plan enfant. Pour choisir ceux à suivre, affectez un `LinkExtractor` à `sitemap_follow` :

```python
class MySitemap(SitemapSpider):
    name = "sm"
    sitemap_urls = ["https://example.com/sitemap.xml"]
    sitemap_follow = LinkExtractor(allow=r"/posts-sitemap-\d+\.xml")  # only post sitemaps
```

### Prise en charge de robots.txt {#robotstxt-support}

Ajoutez une URL de `robots.txt` directement à `sitemap_urls`. `SitemapSpider` la détectera, extraira tous les plans de site indiqués et les suivra :

```python
class MySitemap(SitemapSpider):
    name = "sm"
    sitemap_urls = ["https://example.com/robots.txt"]
```

### URL dans d’autres langues {#alternate-language-urls}

Définissez `sitemap_alternate_links = True` pour que les URL de `<xhtml:link rel="alternate" hreflang="...">` passent aussi par vos règles.

## XMLFeedSpider {#xmlfeedspider}

`XMLFeedSpider` parcourt les nœuds d’un flux XML, comme RSS, Atom ou un flux de produits. Définissez `itertag` avec le nom du nœud à lire, `"item"` par défaut, et redéfinissez `parse_node()`. Cette méthode est appelée une fois pour chaque nœud correspondant :

```python
from scrapling.spiders import XMLFeedSpider

class RSSSpider(XMLFeedSpider):
    name = "rss"
    start_urls = ["https://example.com/feed.xml"]
    itertag = "item"

    async def parse_node(self, response, node):
        yield {
            "title": node.findtext("title"),
            "link": node.findtext("link"),
            "date": node.findtext("pubDate"),
        }

result = RSSSpider().start()
```

Comme les autres callbacks, `parse_node()` peut aussi produire des objets `Request`. Par exemple, utilisez `response.follow(node.findtext("link"), callback=self.parse_post)` pour parcourir les pages liées dans le flux.

### Recherche et analyse des nœuds {#how-nodes-are-matched-and-parsed}

Chaque nœud reçu par `parse_node()` est un élément `lxml` dont tous les espaces de noms ont été retirés. Vous pouvez donc utiliser `node.findtext("title")`, `node.find("thumbnail").get("url")` et `node.xpath(...)`, qui distingue les majuscules des minuscules, sans définir de correspondances d’espaces de noms. Un `itertag` simple comme `"entry"` recherche les nœuds par leur nom, quel que soit leur espace de noms. Cela convient à Atom et à la plupart des flux avec des espaces de noms. Pour chercher dans un espace de noms précis, utilisez un `itertag` avec un préfixe et définissez ce préfixe dans `namespaces` :

```python
class ThumbnailSpider(XMLFeedSpider):
    name = "thumbs"
    start_urls = ["https://example.com/feed.xml"]
    itertag = "media:thumbnail"
    namespaces = (("media", "http://search.yahoo.com/mrss/"),)

    async def parse_node(self, response, node):
        yield {"thumbnail": node.get("url")}
```

Les flux compressés avec gzip, avec une extension `.xml.gz` ou un content-type gzip, sont décompressés automatiquement avec les mêmes protections que le spider de plans de site. Un XML mal formé produit un avertissement dans les journaux au lieu d’arrêter l’exploration.

## CSVFeedSpider {#csvfeedspider}

`CSVFeedSpider` parcourt les lignes d’un flux CSV. Redéfinissez `parse_row()`, qui reçoit chaque ligne sous forme de dictionnaire avec les noms des colonnes comme clés :

```python
from scrapling.spiders import CSVFeedSpider

class PriceSpider(CSVFeedSpider):
    name = "prices"
    start_urls = ["https://example.com/products.csv"]

    async def parse_row(self, response, row):
        yield {"product": row["title"], "price": float(row["price"])}

result = PriceSpider().start()
```

Par défaut, la première ligne contient les noms des colonnes. Si le flux n’a pas cette ligne, indiquez les noms avec `headers`. Utilisez `delimiter`/`quotechar` pour les fichiers qui ne suivent pas le format habituel avec des virgules :

```python
class PriceSpider(CSVFeedSpider):
    name = "prices"
    start_urls = ["https://example.com/products.csv"]
    headers = ["title", "price", "url"]
    delimiter = ";"
```

Les flux gzip sont également décompressés automatiquement, comme avec **XMLFeedSpider**.

<a id="sitetomarkdownspider"></a>

## ContentSpider {#contentspider}

`ContentSpider` s’appuie sur **CrawlSpider** pour parcourir un site et convertir chaque page en Markdown propre, prêt pour un LLM. Il produit un élément par page et peut aussi enregistrer chaque page dans son propre fichier Markdown :

```python
from scrapling.spiders import ContentSpider

class DocsSpider(ContentSpider):
    name = "docs"
    start_urls = ["https://example.com/docs/"]
    allowed_domains = {"example.com"}
    output_dir = "docs_markdown"

result = DocsSpider().start()
```

Vous devez définir `allowed_domains` pour limiter l’exploration au site choisi. La page [Créer des systèmes RAG](../ai/building-rag-systems.md) explique toutes les options et comment intégrer les résultats dans un traitement RAG.

## Utiliser `LinkExtractor` directement {#using-linkextractor-directly}

Vous n’avez pas besoin des modèles. `LinkExtractor` fonctionne dans n’importe quel `Spider` :

```python
from scrapling.spiders import Spider, LinkExtractor

class CustomSpider(Spider):
    name = "custom"
    start_urls = ["https://example.com"]

    def __init__(self):
        super().__init__()
        self._links = LinkExtractor(allow=r"/posts/", deny_domains="ads.example.com")

    async def parse(self, response):
        for url in self._links.extract(response):
            yield response.follow(url, callback=self.parse_post)

    async def parse_post(self, response):
        yield {"title": response.css("h1::text").get()}
```

## Référence de LinkExtractor {#linkextractor-reference}

| Argument | Valeur par défaut | Description |
|----------|-------------------|-------------|
| `allow` | `()` | Motifs d’URL autorisés. Une valeur vide autorise tout. Accepte une chaîne, un `Pattern` compilé ou un itérable contenant l’un ou l’autre |
| `deny` | `()` | Motifs d’URL écartés. Ils ont toujours priorité sur `allow` |
| `allow_domains` | `()` | Noms d’hôtes autorisés. Les sous-domaines sont inclus automatiquement : `example.com` inclut `api.example.com` |
| `deny_domains` | `()` | Noms d’hôtes écartés |
| `restrict_css` | `()` | Sélecteurs CSS qui limitent l’extraction à une zone du DOM |
| `restrict_xpath` | `()` | Sélecteurs XPath qui limitent l’extraction à une zone du DOM |
| `tags` | `("a", "area")` | Balises des éléments où chercher les liens |
| `attrs` | `("href",)` | Attributs de ces balises dans lesquels lire les URL |
| `canonicalize` | `True` | Trie les paramètres de requête et normalise le chemin |
| `strip` | `True` | Retire les espaces au début et à la fin des URL extraites |
| `keep_fragment` | `False` | Garde `#fragment` lors de la normalisation de l’URL |
| `deny_extensions` | `IGNORED_EXTENSIONS` | Extensions écartées, comme pdf, zip, images ou vidéos |
| `process` | `None` | Fonction facultative appliquée à chaque URL extraite avant le filtrage. Renvoyez une valeur évaluée comme fausse pour l’écarter |

`LinkExtractor.extract(response)` renvoie une `list[str]` d’URL absolues, filtrées et sans doublons.

`LinkExtractor.matches(url)` renvoie un `bool`. Il applique à une URL les filtres de motifs autorisés ou exclus, de domaines et d’extensions. `SitemapSpider` l’utilise pour choisir les URL sans avoir besoin d’un `Response`.
