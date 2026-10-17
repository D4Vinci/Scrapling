---
title: "Utilisez des sessions HTTP et navigateur dans un même spider"
description: "Configurez des sessions nommées et envoyez les requêtes du spider par HTTP ou par un navigateur. Réutilisez les cookies, démarrez les sessions à la demande et consultez l’historique des API."
---

# Sessions des spiders {#spiders-sessions}

!!! success "Avant de commencer"

    1. Lisez la page [Premiers pas](getting-started.md) pour apprendre à créer et exécuter un spider simple.
    2. Consultez les [Bases des fetchers](../fetching/choosing.md) et les différences entre les sessions HTTP et Stealthy.

Un spider peut utiliser plusieurs sessions de fetcher en même temps. Par exemple, une session HTTP rapide pour les pages simples et un navigateur furtif pour les pages protégées. Cette page explique comment configurer et utiliser les sessions.

## Qu’est-ce qu’une session ? {#what-are-sessions}

Une session est une instance de fetcher déjà configurée qui reste active pendant l’exploration. Au lieu de créer une connexion ou un navigateur pour chaque requête, le spider réutilise les sessions. C’est plus rapide et cela consomme moins de ressources.

Par défaut, chaque spider crée une seule [FetcherSession](../fetching/static.md). Vous pouvez ajouter d’autres sessions ou changer celle par défaut en redéfinissant `configure_sessions()`. Utilisez uniquement la version asynchrone de chaque session, comme dans ce tableau :

| Type de session | Utilisation |
|-----------------|-------------|
| [FetcherSession](../fetching/static.md) | Requêtes HTTP rapides, sans JavaScript |
| [AsyncStealthySession](../fetching/stealthy.md) | JavaScript, automatisation du navigateur et contournement des protections antibot |

## Configurer les sessions {#configuring-sessions}

Redéfinissez `configure_sessions()` dans votre spider. Le paramètre `manager` est une instance de `SessionManager`. Utilisez `manager.add()` pour enregistrer chaque session :

```python
from scrapling.spiders import Spider, Response
from scrapling.fetchers import FetcherSession

class MySpider(Spider):
    name = "my_spider"
    start_urls = ["https://example.com"]

    def configure_sessions(self, manager):
        manager.add("default", FetcherSession())

    async def parse(self, response: Response):
        yield {"title": response.css("title::text").get("")}
```

La méthode `manager.add()` accepte ces arguments :

| Argument | Type | Valeur par défaut | Description |
|----------|------|-------------------|-------------|
| `session_id` | `str` | *obligatoire* | Nom utilisé pour désigner cette session dans les requêtes |
| `session` | `Session` | *obligatoire* | Instance de la session |
| `default` | `bool` | `False` | Utilise cette session par défaut |
| `lazy` | `bool` | `False` | Démarre la session uniquement à sa première utilisation |

!!! note "Notes"

    1. Si une requête ne précise pas la session à utiliser, la session par défaut est choisie. Elle est définie de deux façons :
        1. La première session ajoutée au gestionnaire devient celle par défaut.
        2. Vous pouvez en choisir une autre en l’ajoutant avec `default=True`.
    2. Vous n’avez pas besoin de démarrer les sessions avant de les fournir au gestionnaire. Le spider vérifie celles qui ne sont pas encore actives et les démarre.
    3. Pour démarrer une session seulement quand elle est nécessaire, utilisez `lazy` lors de son ajout. Vous pouvez ainsi ouvrir le navigateur à sa première utilisation plutôt qu’au lancement du spider.

## Spider avec plusieurs sessions {#multi-session-spider}

Cet exemple utilise une session HTTP rapide pour les pages de listes et un navigateur furtif pour les pages de détails avec des protections antibot :

```python
from scrapling.spiders import Spider, Response
from scrapling.fetchers import FetcherSession, AsyncStealthySession

class ProductSpider(Spider):
    name = "products"
    start_urls = ["https://shop.example.com/products"]

    def configure_sessions(self, manager):
        # Fast HTTP for listing pages (default)
        manager.add("http", FetcherSession())

        self.browser_session = AsyncStealthySession(
            headless=True,
            network_idle=True,
            record_requests=True,
        )
        manager.add("stealth", self.browser_session)

    async def parse(self, response: Response):
        for link in response.css("a.product::attr(href)").getall():
            # Route product pages through the stealth session
            yield response.follow(link, sid="stealth", callback=self.parse_product)

        next_page = response.css("a.next::attr(href)").get()
        if next_page:
            yield response.follow(next_page)

    async def parse_product(self, response: Response):
        yield {
            "name": response.css("h1::text").get(""),
            "price": response.css(".price::text").get(""),
        }

    async def on_close(self):
        for api_response in self.browser_session.network.search(
            url_pattern=r"https://api\.shop\.example\.com/.*", limit=None
        ):
            self.logger.info(f"Saved API response: {api_response.url} ({api_response.status})")
```

L’exemple conserve l’instance du navigateur et consulte une seule fois son historique de réponses d’API dans `on_close()`, avant la fermeture des sessions. L’historique couvre toutes les pages de produits et reste lisible après la fermeture. Les captures en cours ne sont pas attendues, et les limites de conservation restent appliquées.

Le paramètre `sid` indique au spider quelle session utiliser pour chaque requête. Si vous appelez `response.follow()` sans `sid`, l’identifiant de session de la requête d’origine est repris.

Les sessions ne doivent pas forcément être de classes différentes. Vous pouvez aussi utiliser plusieurs instances de la même classe avec des réglages différents :

```python
from scrapling.spiders import Spider, Response
from scrapling.fetchers import FetcherSession

class ProductSpider(Spider):
    name = "products"
    start_urls = ["https://shop.example.com/products"]

    def configure_sessions(self, manager):
        chrome_requests = FetcherSession(impersonate="chrome")
        firefox_requests = FetcherSession(impersonate="firefox")

        manager.add("chrome", chrome_requests)
        manager.add("firefox", firefox_requests)

    async def parse(self, response: Response):
        for link in response.css("a.product::attr(href)").getall():
            yield response.follow(link, callback=self.parse_product)

        next_page = response.css("a.next::attr(href)").get()
        if next_page:
            yield response.follow(next_page, sid="firefox")

    async def parse_product(self, response: Response):
        yield {
            "name": response.css("h1::text").get(""),
            "price": response.css(".price::text").get(""),
        }
```

Vous pouvez également réserver une session, avec ses propres cookies et son état, à certaines requêtes.

## Arguments de session {#session-arguments}

Les arguments supplémentaires d’un `Request`, ou de `response.follow(**kwargs)`, sont transmis à la méthode de récupération de la session. Vous pouvez ainsi ajuster une requête sans changer la configuration de toute la session :

```python
async def parse(self, response: Response):
    # Pass extra headers for this specific request
    yield Request(
        "https://api.example.com/data",
        headers={"Authorization": "Bearer token123"},
        callback=self.parse_api,
    )

    # Use a different HTTP method
    yield Request(
        "https://example.com/submit",
        method="POST",
        data={"field": "value"},
        sid="firefox",
        callback=self.parse_result,
    )
```

!!! warning "Attention"

    Habituellement, avec `FetcherSession`, `Fetcher` ou `AsyncFetcher`, vous choisissez la méthode HTTP en appelant `.get()`, `.post()` ou une autre méthode. Dans un spider, vous ne pouvez pas faire cela avec `FetcherSession`. Les requêtes utilisent _HTTP GET_ par défaut. Pour choisir une autre méthode HTTP, passez-la dans l’argument `method`, comme dans l’exemple précédent. Cela permet à tous les types de session de partager la même interface `Request`.

Avec la session `"stealth"` (`AsyncStealthySession`) de l’exemple précédent, vous pouvez transmettre des arguments propres au navigateur, comme `wait_selector`, `page_action` ou `extra_headers` :

```python
async def parse(self, response: Response):
    # Use Cloudflare solver with the `AsyncStealthySession` we configured above
    yield Request(
        "https://nopecha.com/demo/cloudflare",
        sid="stealth",
        callback=self.parse_result,
        solve_cloudflare=True,
        block_webrtc=True,
        hide_canvas=True,
        google_search=True,
    )

    yield response.follow(
        "/dynamic-page",
        sid="stealth",
        callback=self.parse_dynamic,
        wait_selector="div.loaded",
        network_idle=True,
    )
```

!!! warning "Attention"

    `response.follow()` reprend les arguments de session (**kwargs) de la requête d’origine, sauf `method`, `params`, `data`, `json`, `files` et `multipart`. Suivre un lien après un POST envoie donc un simple GET. Les nouveaux arguments ont priorité sur ceux qui sont repris.

```python
from scrapling.spiders import Spider, Response
from scrapling.fetchers import FetcherSession

class ProductSpider(Spider):
    name = "products"
    start_urls = ["https://shop.example.com/products"]

    def configure_sessions(self, manager):
        manager.add("http", FetcherSession(impersonate='chrome'))

    async def parse(self, response: Response):
        # I don't want the follow request to impersonate a desktop Chrome like the previous request, but a mobile one
        # so I override it like this
        for link in response.css("a.product::attr(href)").getall():
            yield response.follow(link, impersonate="chrome131_android", callback=self.parse_product)

        next_page = response.css("a.next::attr(href)").get()
        if next_page:
            yield response.follow(next_page)

    async def parse_product(self, response: Response):
        yield {
            "name": response.css("h1::text").get(""),
            "price": response.css(".price::text").get(""),
        }
```

!!! info "Information"

    À l’arrêt du spider, le gestionnaire vérifie si des sessions sont encore actives et les ferme avant de terminer.
