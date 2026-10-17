---
title: "Contrôlez l’exploration : AutoThrottle, points de reprise, cache et streaming"
description: "Contrôlez la vitesse et la concurrence de l’exploration. Découvrez le cache, la pause et la reprise, les résultats en temps réel et l’état enregistré."
---

# Usages avancés {#advanced-usages}

## Introduction {#introduction}

!!! success "Avant de commencer"

    1. Lisez la page [Premiers pas](getting-started.md) pour apprendre à créer et exécuter un spider simple.

Cette page explique les fonctions avancées des spiders : contrôle de la concurrence, pause et reprise, streaming, hooks du cycle de vie, statistiques et journaux.

## Contrôler la concurrence {#concurrency-control}

Le système de spiders utilise ces attributs de classe pour régler le rythme de l’exploration :

| Attribut | Valeur par défaut | Description |
|----------|-------------------|-------------|
| `concurrent_requests` | `4` | Nombre maximal de requêtes traitées en même temps |
| `concurrent_requests_per_domain` | `0` | Nombre maximal de requêtes simultanées par domaine. 0 signifie sans limite par domaine |
| `download_delay` | `0.0` | Secondes d’attente avant chaque requête |
| `robots_txt_obey` | `False` | Respecte les règles de robots.txt : Disallow, Crawl-delay et Request-rate |

```python
class PoliteSpider(Spider):
    name = "polite"
    start_urls = ["https://example.com"]

    # Be gentle with the server
    concurrent_requests = 4
    concurrent_requests_per_domain = 2
    download_delay = 1.0  # Wait 1 second between requests

    async def parse(self, response: Response):
        yield {"title": response.css("title::text").get("")}
```

Quand vous définissez `concurrent_requests_per_domain`, chaque domaine a sa propre limite de concurrence, en plus de la limite globale. Vous pouvez ainsi explorer plusieurs domaines avec beaucoup de requêtes au total, sans surcharger chacun d’eux.

!!! tip "Conseil"

    `download_delay` ajoute une attente fixe avant chaque requête, quel que soit le domaine. Utilisez-le pour limiter simplement le rythme.

## AutoThrottle {#autothrottle}

Choisir un `download_delay` fixe demande des essais : trop court, il risque de provoquer un blocage ; trop long, il ralentit l’exploration. AutoThrottle observe le temps de réponse du site et ajuste l’attente pour chaque domaine. Il accélère avec les serveurs rapides et ralentit avec ceux qui répondent lentement ou bloquent les requêtes.

| Attribut | Valeur par défaut | Description |
|----------|-------------------|-------------|
| `autothrottle_enabled` | `False` | Active l’ajustement automatique du délai |
| `autothrottle_start_delay` | `5.0` | Délai utilisé pour la première requête vers un domaine |
| `autothrottle_max_delay` | `60.0` | Délai maximal autorisé |
| `autothrottle_target_concurrency` | `None` | Nombre de requêtes simultanées visé par domaine, expliqué ci-dessous |
| `autothrottle_block_backoff` | `True` | Double le délai d’un domaine chaque fois qu’il bloque une requête |

```python
class AdaptiveSpider(Spider):
    name = "adaptive"
    start_urls = ["https://example.com"]

    concurrent_requests = 8
    concurrent_requests_per_domain = 1

    autothrottle_enabled = True
    autothrottle_start_delay = 2.0
    autothrottle_max_delay = 30.0

    async def parse(self, response: Response):
        yield {"title": response.css("title::text").get("")}
```

Après chaque réponse, le délai se rapproche du temps que le serveur a mis à répondre. Par exemple, avec une réponse en 0,5 seconde, le délai se stabilise autour de 0,5 seconde, ce qui maintient environ une requête active. Le nombre visé par domaine est choisi dans cet ordre : `autothrottle_target_concurrency` si vous le définissez, sinon `concurrent_requests_per_domain`, sinon 1. Vous n’avez donc généralement pas besoin de définir un objectif distinct : la limite par domaine sert d’objectif, et le délai est divisé par cette valeur. Les hausses brusques du temps de réponse sont appliquées immédiatement, sans être moyennées. Le spider ralentit dès que le serveur rencontre des difficultés et n’accélère de nouveau que progressivement.

### Ralentir en cas de blocage {#backing-off-when-blocked}

Le temps de réponse seul ne permet pas de repérer les limites de requêtes. Une réponse `429`, `403` ou une page de captcha arrive souvent *plus vite* que le vrai contenu. En se basant seulement sur ce temps, le spider accélérerait. C’est pourquoi une réponse avec un code hors 2xx ou signalée par `is_blocked()` **double** le délai de ce domaine :

```
0.5s -> 1s -> 2s -> 4s -> 8s ...   (up to autothrottle_max_delay)
```

Le spider continue de ralentir tant que le site refuse les requêtes. Quand les réponses normales reviennent, l’ajustement habituel par la moyenne réduit peu à peu l’attente pour se rapprocher de la vitesse réelle du serveur. Vous n’avez rien à redémarrer.

Si une réponse `429` ou `503` contient un en-tête `Retry-After`, le délai indiqué est utilisé au lieu du doublement. Les formats numérique (`Retry-After: 120`) et date HTTP sont tous deux acceptés.

Définissez `autothrottle_block_backoff = False` pour désactiver ce comportement et régler le rythme seulement selon le temps de réponse. Dans ce cas, un blocage peut uniquement empêcher le spider d’accélérer.

Vous pouvez consulter le délai final de chaque domaine dans les statistiques :

```python
result = AdaptiveSpider().start()
print(result.stats.autothrottle_delays)  # {'example.com': 0.62}
```

!!! note "Notes"

    * `download_delay` et les délais de robots.txt définissent un minimum, mais `autothrottle_max_delay` limite aussi ce minimum. Choisissez un maximum au moins égal au délai configuré ou demandé par robots.txt.<br/>
    * `concurrent_requests_per_domain` a deux rôles : limiter les requêtes actives d’un domaine et servir d’objectif à AutoThrottle. Il n’y a donc généralement pas d’autre objectif à définir. Il est conseillé de le régler, car une requête en attente occupe une place dans la limite globale. Sans limite par domaine, ces attentes peuvent occuper les places nécessaires aux autres domaines.<br/>
    * Le temps mesuré inclut toute la récupération, avec les nouvelles tentatives internes et, pour les sessions de navigateur, le rendu de la page.<br/>
    * `autothrottle_max_delay` limite toutes les attentes, y compris `Retry-After`. Si un site demande une attente plus longue, augmentez `autothrottle_max_delay` pour la respecter.<br/>
    * Les délais appris ne sont pas enregistrés dans les points de reprise. Après une pause et une reprise, chaque domaine repart de `autothrottle_start_delay`.

## Utiliser uvloop {#using-uvloop}

La méthode `start()` accepte `use_uvloop` pour utiliser la boucle d’événements plus rapide de [uvloop](https://github.com/MagicStack/uvloop)/[winloop](https://github.com/nicktimko/winloop), si elle est disponible :

```python
result = MySpider().start(use_uvloop=True)
```

Cela peut améliorer les performances des explorations avec beaucoup d’entrées et de sorties. Vous devez installer `uvloop` sur Linux/macOS ou `winloop` sur Windows séparément.

## Mettre en pause et reprendre {#pause-resume}

Le spider permet de mettre en pause et de reprendre l’exploration grâce aux points de reprise. Pour les activer, passez un dossier `crawldir` au constructeur :

```python
spider = MySpider(crawldir="crawl_data/my_spider")
result = spider.start()

if result.paused:
    print("Crawl was paused. Run again to resume.")
else:
    print("Crawl completed!")
```

### Fonctionnement {#how-it-works}

1. **Pause** : appuyez sur `Ctrl+C` pendant l’exploration. Le spider attend la fin des requêtes actives, enregistre les requêtes en attente et les empreintes déjà vues, puis s’arrête.
2. **Arrêt forcé** : appuyez une seconde fois sur `Ctrl+C` pour arrêter immédiatement, sans attendre les tâches actives.
3. **Reprise** : relancez le spider avec le même `crawldir`. Il détecte le point de reprise, restaure la file et les empreintes déjà vues, puis continue là où il s’était arrêté, sans exécuter `start_requests()`.
4. **Nettoyage** : quand l’exploration se termine complètement, sans rester en pause, les fichiers de reprise sont supprimés automatiquement.

**Des points de reprise sont aussi enregistrés pendant l’exploration, toutes les 5 minutes par défaut.**

Vous pouvez changer l’intervalle ainsi :

```python
# Save checkpoint every 2 minutes
spider = MySpider(crawldir="crawl_data/my_spider", interval=120.0)
```

L’enregistrement d’un point de reprise utilise un fichier temporaire et ne remplace le point précédent qu’une fois l’écriture réussie.

!!! warning "Données du point de reprise"

    Quand vous activez `crawldir`, les valeurs des requêtes en attente, y compris `meta` et les arguments des requêtes, doivent pouvoir être enregistrées avec le module Python `pickle`. Si une valeur ne peut pas être enregistrée, l’enregistrement du point de reprise échoue et l’exploration s’arrête. Un `Selector` peut fonctionner dans un callback, mais ne peut pas être enregistré de cette manière.

    Enregistrez les valeurs extraites, comme des chaînes de caractères ou des nombres, au lieu d’objets `Selector`. Les listes et les dictionnaires doivent aussi contenir uniquement des valeurs qui peuvent être enregistrées :

    ```python
    yield response.follow("/details", meta={"title": str(response.css("h1::text").get(""))})
    ```

!!! tip "Conseil"

    Avec `start()`, appuyer sur `Ctrl+C` arrête proprement le spider, même si les points de reprise ne sont pas activés. Appuyer de nouveau sans attendre force l’arrêt immédiat.

### Savoir si vous reprenez une exploration {#knowing-if-youre-resuming}

Le hook `on_start()` reçoit l’indicateur `resuming` :

```python
async def on_start(self, resuming: bool = False):
    if resuming:
        self.logger.info("Resuming from checkpoint!")
    else:
        self.logger.info("Starting fresh crawl")
```

## Mode développement {#development-mode}

Quand vous ajustez la logique de `parse()`, télécharger les pages à chaque exécution prend du temps et envoie des requêtes inutiles. Le mode développement enregistre les réponses sur disque lors de la première exécution et les réutilise ensuite. Vous pouvez ainsi modifier vos sélecteurs et relancer le spider autant de fois que nécessaire, sans télécharger ces pages de nouveau.

Activez-le avec `development_mode = True` dans votre spider :

```python
class MySpider(Spider):
    name = "my_spider"
    start_urls = ["https://example.com"]
    development_mode = True

    async def parse(self, response: Response):
        yield {"title": response.css("title::text").get("")}
```

La première exécution télécharge les pages et enregistre chaque réponse sur disque. Les suivantes utilisent le cache pour les mêmes requêtes. Avec `robots_txt_obey=True`, les règles de robots.txt sont vérifiées avant de consulter le cache.

### Emplacement du cache {#cache-location}

Par défaut, les réponses sont enregistrées dans `.scrapling_cache/{spider.name}/`, dans le dossier de travail actuel. C’est le dossier depuis lequel vous avez lancé le spider, **pas** celui qui contient son fichier. Vous pouvez changer cet emplacement avec `development_cache_dir` :

```python
class MySpider(Spider):
    name = "my_spider"
    start_urls = ["https://example.com"]
    development_mode = True
    development_cache_dir = "/tmp/my_spider_cache"
```

### Fonctionnement {#how-it-works_1}

1. **Clé du cache** : chaque réponse est identifiée par l’empreinte de la requête. Modifier les attributs qui influencent cette empreinte (`fp_include_kwargs`, `fp_include_headers`, `fp_keep_fragments`) entraîne une nouvelle récupération.
2. **Format** : un fichier JSON par réponse, nommé `{fingerprint_hex}.json`. Le corps est encodé en base64 pour garder les données binaires intactes. Les écritures sont atomiques : un fichier temporaire est créé puis renommé.
3. **Réutilisation** : si une réponse est en cache, le moteur évite la récupération, `download_delay`, les limites de rythme et les nouvelles tentatives de `is_blocked()`. La réponse enregistrée passe directement au callback.
4. **Statistiques** : les requêtes servies depuis le cache sont comptées dans `requests_count`, `response_bytes` et les compteurs par code de statut, comme dans une exploration normale. `cache_hits` et `cache_misses` indiquent combien de requêtes ont trouvé une réponse enregistrée et combien n’en ont pas trouvé.

### Vider le cache {#clearing-the-cache}

Le cache n’expire pas automatiquement. Pour tout récupérer de nouveau, supprimez son dossier ou appelez directement la méthode `clear()` du gestionnaire.

!!! warning "Attention"

    Ce mode est prévu pour le développement, pas la production. Les réponses enregistrées n’expirent jamais et leur réutilisation évite les limites de rythme et les nouvelles tentatives en cas de blocage. Ne déployez pas un spider avec `development_mode = True`.

## Streaming {#streaming}

Pour les spiders qui tournent longtemps ou les applications qui ont besoin des données en temps réel, utilisez `stream()` au lieu de `start()` :

```python
import anyio

async def main():
    spider = MySpider()
    async for item in spider.stream():
        print(f"Got item: {item}")
        # Access real-time stats
        print(f"Items so far: {spider.stats.items_scraped}")
        print(f"Requests made: {spider.stats.requests_count}")

anyio.run(main)
```

Principales différences avec `start()` :

- Vous devez appeler `stream()` depuis un contexte asynchrone.
- Les éléments sont produits un à un dès leur extraction, au lieu d’être réunis dans une liste.
- Vous pouvez consulter `spider.stats` pendant l’itération pour obtenir les statistiques en temps réel.

!!! abstract "Pour en savoir plus"

    La section [Résultats et statistiques](#results-statistics) décrit toutes les statistiques disponibles dans `spider.stats`.

Vous pouvez aussi le combiner avec les points de reprise. Cela permet de créer des interfaces qui affichent les données en temps réel et proposent la pause et la reprise.

```python
import anyio

async def main():
    spider = MySpider(crawldir="crawl_data/my_spider")
    async for item in spider.stream():
        print(f"Got item: {item}")
        # Access real-time stats
        print(f"Items so far: {spider.stats.items_scraped}")
        print(f"Requests made: {spider.stats.requests_count}")

anyio.run(main)
```

Vous pouvez également utiliser `spider.pause()` pour arrêter le spider de cet exemple. Si les points de reprise ne sont pas activés, cela arrête simplement l’exploration.

## Hooks du cycle de vie {#lifecycle-hooks}

Le spider propose plusieurs hooks, des méthodes que vous pouvez redéfinir pour ajouter votre logique à différentes étapes de l’exploration :

### on_start {#on_start}

Appelé avant le début de l’exploration. Utilisez-le pour préparer le travail, par exemple charger des données ou initialiser des ressources :

```python
async def on_start(self, resuming: bool = False):
    self.logger.info("Spider starting up")
    # Load seed URLs from a database, initialize counters, etc.
```

### on_close {#on_close}

Appelé à la fin de l’exploration, qu’elle soit terminée ou mise en pause. Utilisez-le pour libérer des ressources :

```python
async def on_close(self):
    self.logger.info("Spider shutting down")
    # Close database connections, flush buffers, etc.
```

### on_error {#on_error}

Appelé quand une requête échoue avec une exception. Utilisez-le pour enregistrer les erreurs ou appliquer votre propre logique de récupération :

```python
async def on_error(self, request: Request, error: Exception):
    self.logger.error(f"Failed: {request.url} - {error}")
    # Log to error tracker, save failed URL for later, etc.
```

### on_scraped_item {#on_scraped_item}

Appelé pour chaque élément extrait, avant son ajout aux résultats. Renvoyez l’élément, modifié ou non, pour le garder. Renvoyez `None` pour l’écarter :

```python
async def on_scraped_item(self, item: dict) -> dict | None:
    # Drop items without a title
    if not item.get("title"):
        return None

    # Modify items (e.g., add timestamps)
    item["scraped_at"] = "2026-01-01"
    return item
```

!!! tip "Conseil"

    Vous pouvez aussi utiliser ce hook pour envoyer les éléments dans votre propre traitement et les retirer des résultats du spider.

### start_requests {#start_requests}

Redéfinissez `start_requests()` pour produire vos propres requêtes initiales au lieu d’utiliser `start_urls` :

```python
async def start_requests(self):
    # POST request to log in first
    yield Request(
        "https://example.com/login",
        method="POST",
        data={"user": "admin", "pass": "secret"},
        callback=self.after_login,
    )

async def after_login(self, response: Response):
    # Now crawl the authenticated pages
    yield response.follow("/dashboard", callback=self.parse)
```

## Résultats et statistiques {#results-statistics}

Le `CrawlResult` renvoyé par `start()` contient les éléments extraits et des statistiques détaillées :

```python
result = MySpider().start()

# Items
print(f"Total items: {len(result.items)}")
result.items.to_json("output.json", indent=True)

# Did the crawl complete?
print(f"Completed: {result.completed}")
print(f"Paused: {result.paused}")

# Statistics
stats = result.stats
print(f"Requests: {stats.requests_count}")
print(f"Failed: {stats.failed_requests_count}")
print(f"Blocked: {stats.blocked_requests_count}")
print(f"Offsite filtered: {stats.offsite_requests_count}")
print(f"Robots.txt disallowed: {stats.robots_disallowed_count}")
print(f"Cache hits: {stats.cache_hits}")
print(f"Cache misses: {stats.cache_misses}")
print(f"Items scraped: {stats.items_scraped}")
print(f"Items dropped: {stats.items_dropped}")
print(f"Response bytes: {stats.response_bytes}")
print(f"Duration: {stats.elapsed_seconds:.1f}s")
print(f"Speed: {stats.requests_per_second:.1f} req/s")
```

### Statistiques détaillées {#detailed-stats}

L’objet `CrawlStats` enregistre des informations détaillées :

```python
stats = result.stats

# Status code distribution
print(stats.response_status_count)
# {'status_200': 150, 'status_404': 3, 'status_403': 1}

# Bytes downloaded per domain
print(stats.domains_response_bytes)
# {'example.com': 1234567, 'api.example.com': 45678}

# Requests per session
print(stats.sessions_requests_count)
# {'http': 120, 'stealth': 34}

# Proxies used during the crawl
print(stats.proxies)
# ['http://proxy1:8080', 'http://proxy2:8080']

# Log level counts
print(stats.log_levels_counter)
# {'debug': 200, 'info': 50, 'warning': 3, 'error': 1, 'critical': 0}

# Timing information
print(stats.start_time)       # Unix timestamp when crawl started
print(stats.end_time)         # Unix timestamp when crawl finished
print(stats.download_delay)   # The download delay used (seconds)

# Concurrency settings used
print(stats.concurrent_requests)             # Global concurrency limit
print(stats.concurrent_requests_per_domain)  # Per-domain concurrency limit

# AutoThrottle
print(stats.autothrottle_enabled)  # Whether the adaptive delay was on
print(stats.autothrottle_delays)   # Final delay per domain, {'example.com': 0.62}

# Custom stats (set by your spider code)
print(stats.custom_stats)
# {'login_attempts': 3, 'pages_with_errors': 5}

# Export everything as a dict
print(stats.to_dict())
```

## Journaux {#logging}

Le spider a un logger intégré, disponible dans `self.logger`. Il utilise déjà le nom du spider et accepte ces réglages :

| Attribut | Valeur par défaut | Description |
|----------|-------------------|-------------|
| `logging_level` | `logging.DEBUG` | Niveau minimal enregistré |
| `logging_format` | `"[%(asctime)s]:({spider_name}) %(levelname)s: %(message)s"` | Format des messages |
| `logging_date_format` | `"%Y-%m-%d %H:%M:%S"` | Format de la date dans les messages |
| `log_file` | `None` | Chemin d’un fichier journal, en plus de la sortie dans la console |

```python
import logging

class MySpider(Spider):
    name = "my_spider"
    start_urls = ["https://example.com"]
    logging_level = logging.INFO
    log_file = "logs/my_spider.log"

    async def parse(self, response: Response):
        self.logger.info(f"Processing {response.url}")
        yield {"title": response.css("title::text").get("")}
```

Si le dossier du fichier journal n’existe pas, il est créé automatiquement. La console et le fichier utilisent le même format.
