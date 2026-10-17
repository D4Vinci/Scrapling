---
title: "Alternez les proxies et réessayez les requêtes bloquées"
description: "Utilisez des proxies et des stratégies de rotation dans les spiders de Scrapling. Détectez les blocages, réessayez les requêtes et passez d’une session HTTP à un navigateur."
---

# Gérer les proxies et les blocages {#proxy-management-and-handling-blocks}

## Introduction {#introduction}

!!! success "Avant de commencer"

    1. Lisez la page [Premiers pas](getting-started.md) pour apprendre à créer et exécuter un spider simple.
    2. Lisez la page [Sessions](sessions.md) pour apprendre à les configurer.

Pour extraire beaucoup de données, vous aurez souvent besoin d’alterner entre plusieurs proxies afin d’éviter les limites de requêtes et les blocages. `ProxyRotator` de Scrapling simplifie ce travail. Il fonctionne avec tous les types de session et s’intègre au système de nouvelles tentatives du spider.

Si vous ne savez pas ce qu’est un proxy ou comment en choisir un, [ce guide peut vous aider](https://substack.thewebscraping.club/p/everything-about-proxies).

## ProxyRotator {#proxyrotator}

La classe `ProxyRotator` gère une liste de proxies et les utilise à tour de rôle. Passez-la à n’importe quel type de session par le paramètre `proxy_rotator` :

```python
from scrapling.spiders import Spider, Response
from scrapling.fetchers import FetcherSession, ProxyRotator

class MySpider(Spider):
    name = "my_spider"
    start_urls = ["https://example.com"]

    def configure_sessions(self, manager):
        rotator = ProxyRotator([
            "http://proxy1:8080",
            "http://proxy2:8080",
            "http://user:pass@proxy3:8080",
        ])
        manager.add("default", FetcherSession(proxy_rotator=rotator))

    async def parse(self, response: Response):
        # Check which proxy was used
        print(f"Proxy used: {response.meta.get('proxy')}")
        yield {"title": response.css("title::text").get("")}
```

Chaque requête reçoit automatiquement le proxy suivant. Le proxy utilisé est enregistré dans `response.meta["proxy"]`, pour que vous sachiez lequel a récupéré chaque page.

Pour l’utiliser avec des sessions de navigateur, configurez-le ainsi :

```python
from scrapling.fetchers import AsyncStealthySession, ProxyRotator

# String proxies work for all session types
rotator = ProxyRotator([
    "http://proxy1:8080",
    "http://proxy2:8080",
])

# Dict proxies (Playwright format) work for browser sessions
rotator = ProxyRotator([
    {"server": "http://proxy1:8080", "username": "user", "password": "pass"},
    {"server": "http://proxy2:8080"},
])

# Then inside the spider
def configure_sessions(self, manager):
    rotator = ProxyRotator(["http://proxy1:8080", "http://proxy2:8080"])
    manager.add("browser", AsyncStealthySession(proxy_rotator=rotator))
```

!!! info "Information"

    1. Vous ne pouvez pas utiliser `proxy_rotator` avec les paramètres fixes `proxy` ou `proxies` dans la même session. Choisissez une approche lors de la configuration. Vous pourrez ensuite choisir un autre proxy pour une requête précise, comme expliqué plus loin.
    2. Par défaut, les sessions de navigateur utilisent un contexte persistant avec un groupe d’onglets. Les navigateurs ne permettent pas de choisir un proxy par onglet. Avec `ProxyRotator`, le fetcher ouvre donc un contexte séparé pour chaque proxy, avec un onglet par contexte. Quand le travail de l’onglet est terminé, l’onglet et son contexte sont fermés.

## Stratégies de rotation personnalisées {#custom-rotation-strategies}

Par défaut, `ProxyRotator` parcourt les proxies dans l’ordre puis revient au premier après le dernier.

Vous pouvez fournir une fonction avec votre propre stratégie pour changer ce comportement. Elle doit avoir cette signature :

```python
from scrapling.core._types import ProxyType

def my_strategy(proxies: list, current_index: int) -> tuple[ProxyType, int]:
    ...
```

La fonction reçoit la liste des proxies et l’indice actuel. Elle doit renvoyer le proxy choisi et l’indice suivant.

Voici quelques exemples de stratégies que vous pouvez utiliser.

### Rotation aléatoire {#random-rotation}

```python
import random
from scrapling.fetchers import ProxyRotator

def random_strategy(proxies, current_index):
    idx = random.randint(0, len(proxies) - 1)
    return proxies[idx], idx

rotator = ProxyRotator(
    ["http://proxy1:8080", "http://proxy2:8080", "http://proxy3:8080"],
    strategy=random_strategy,
)
```

### Rotation pondérée {#weighted-rotation}

```python
import random

def weighted_strategy(proxies, current_index):
    # First proxy gets 60% of traffic, others split the rest
    weights = [60] + [40 // (len(proxies) - 1)] * (len(proxies) - 1)
    proxy = random.choices(proxies, weights=weights, k=1)[0]
    return proxy, current_index  # Index doesn't matter for weighted

rotator = ProxyRotator(proxies, strategy=weighted_strategy)
```

## Choisir un proxy pour une requête {#per-request-proxy-override}

Vous pouvez ignorer le rotateur pour une requête précise en passant l’argument `proxy=` :

```python
async def parse(self, response: Response):
    # This request uses the rotator's next proxy
    yield response.follow("/page1", callback=self.parse_page)

    # This request uses a specific proxy, bypassing the rotator
    yield response.follow(
        "/special-page",
        callback=self.parse_page,
        proxy="http://special-proxy:8080",
    )
```

C’est utile quand une page exige un proxy précis, par exemple situé dans une région donnée pour accéder à du contenu local.

## Traiter les requêtes bloquées {#blocked-request-handling}

Le spider intègre la détection des blocages et les nouvelles tentatives. Par défaut, il considère les réponses avec ces codes HTTP comme bloquées : `401`, `403`, `407`, `429`, `444`, `500`, `502`, `503` et `504`.

Le système de nouvelles tentatives fonctionne ainsi :

1. Quand une réponse arrive, le spider appelle `is_blocked(response)`.
2. S’il détecte un blocage, il copie la requête et appelle `retry_blocked_request()` pour vous permettre de la modifier avant de réessayer.
3. La requête retourne dans la file avec `dont_filter=True`, pour autoriser le doublon, et une priorité plus faible pour ne pas être répétée immédiatement.
4. Le processus se répète jusqu’à `max_blocked_retries` fois. La valeur par défaut est 3.

!!! tip "Conseil"

    1. Avant la nouvelle tentative, les arguments `proxy`/`proxies` sont retirés de la requête pour que le rotateur choisisse un nouveau proxy.
    2. `max_blocked_retries` est indépendant des nouvelles tentatives de la session. Les compteurs sont séparés.

### Personnaliser la détection des blocages {#custom-block-detection}

Redéfinissez `is_blocked()` pour ajouter votre propre logique :

```python
class MySpider(Spider):
    name = "my_spider"
    start_urls = ["https://example.com"]

    async def is_blocked(self, response: Response) -> bool:
        # Check status codes (default behavior)
        if response.status in {403, 429, 503}:
            return True

        # Check response content
        body = response.body.decode("utf-8", errors="ignore")
        if "access denied" in body.lower() or "rate limit" in body.lower():
            return True

        return False

    async def parse(self, response: Response):
        yield {"title": response.css("title::text").get("")}
```

### Personnaliser les nouvelles tentatives {#customizing-retries}

Redéfinissez `retry_blocked_request()` pour modifier la requête avant de réessayer. L’attribut `max_blocked_retries` indique combien de fois une requête bloquée est répétée. Sa valeur par défaut est 3 :

```python
from scrapling.spiders import Spider, SessionManager, Request, Response
from scrapling.fetchers import FetcherSession, AsyncStealthySession


class MySpider(Spider):
    name = "my_spider"
    start_urls = ["https://example.com"]
    max_blocked_retries = 5

    def configure_sessions(self, manager: SessionManager) -> None:
        manager.add('requests', FetcherSession(impersonate=['chrome', 'firefox', 'safari']))
        manager.add('stealth', AsyncStealthySession(block_webrtc=True), lazy=True)

    async def retry_blocked_request(self, request: Request, response: Response) -> Request:
        request.sid = "stealth"
        self.logger.info(f"Retrying blocked request: {request.url}")
        return request

    async def parse(self, response: Response):
        yield {"title": response.css("title::text").get("")}
```

Dans cet exemple, la détection des blocages par défaut est conservée. Le spider utilise des requêtes HTTP jusqu’à un blocage, puis passe au navigateur furtif.

Nous pouvons maintenant tout combiner :

```python
from scrapling.spiders import Spider, SessionManager, Request, Response
from scrapling.fetchers import FetcherSession, AsyncStealthySession, ProxyRotator


cheap_proxies = ProxyRotator([ "http://proxy1:8080", "http://proxy2:8080"])

# A format acceptable by the browser
expensive_proxies = ProxyRotator([
    {"server": "http://residential_proxy1:8080", "username": "user", "password": "pass"},
    {"server": "http://residential_proxy2:8080", "username": "user", "password": "pass"},
    {"server": "http://mobile_proxy1:8080", "username": "user", "password": "pass"},
    {"server": "http://mobile_proxy2:8080", "username": "user", "password": "pass"},
])


class MySpider(Spider):
    name = "my_spider"
    start_urls = ["https://example.com"]
    max_blocked_retries = 5

    def configure_sessions(self, manager: SessionManager) -> None:
        manager.add('requests', FetcherSession(impersonate=['chrome', 'firefox', 'safari'], proxy_rotator=cheap_proxies))
        manager.add('stealth', AsyncStealthySession(block_webrtc=True, proxy_rotator=expensive_proxies), lazy=True)

    async def retry_blocked_request(self, request: Request, response: Response) -> Request:
        request.sid = "stealth"
        self.logger.info(f"Retrying blocked request: {request.url}")
        return request

    async def parse(self, response: Response):
        yield {"title": response.css("title::text").get("")}
```

La logique est la suivante : les requêtes utilisent des proxies bon marché, comme ceux de centres de données, jusqu’à un blocage. Elles sont alors réessayées avec des proxies de meilleure qualité, comme des proxies résidentiels ou mobiles.
