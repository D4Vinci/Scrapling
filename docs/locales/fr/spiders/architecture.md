---
title: "Comment fonctionnent les robots d’exploration de Scrapling"
description: "Comprenez le rôle des spiders, requêtes, sessions, files d’attente et du moteur d’exploration. Comparez le fonctionnement avec Scrapy et choisissez par où commencer."
---

# Architecture des spiders {#spiders-architecture}

!!! success "Avant de commencer"

    1. Lisez la page [Bases des fetchers](../fetching/choosing.md) pour connaître les types de fetcher et savoir quand utiliser chacun.
    2. Lisez la page [Classes principales](../parsing/main_classes.md) pour découvrir les classes [Selector](../parsing/main_classes.md#selector) et [Response](../fetching/choosing.md#response-object).

Le système de spiders de Scrapling s’inspire de Scrapy. Il permet une exploration asynchrone avec plusieurs requêtes et sessions à la fois, ainsi que la pause et la reprise. Il réunit l’analyseur et les fetchers de Scrapling dans une seule API d’exploration, avec une file de requêtes, un contrôle de la concurrence et des points de reprise.

Si vous connaissez Scrapy, vous retrouverez vos habitudes. Sinon, pas d’inquiétude : le système est conçu pour être simple à utiliser.

## Circulation des données {#data-flow}

Ce schéma montre comment les données circulent dans le système pendant une exploration :

<img src="../assets/spider_architecture.png" title="Schéma de l’architecture des spiders par @TrueSkills" alt="Schéma de l’architecture des spiders par @TrueSkills" style="width: 70%;"/>

Voici les principales étapes quand vous lancez un spider :

1. Le **Spider** produit le premier groupe d’objets `Request`. Par défaut, il crée une requête par URL de `start_urls`. Vous pouvez redéfinir `start_requests()` pour changer cette logique.
2. Le **Scheduler** reçoit les requêtes, calcule leurs empreintes et les place dans une file de priorité. Les requêtes les plus prioritaires sortent en premier.
3. Le **moteur d’exploration** demande la prochaine requête au **Scheduler**, en respectant les limites de concurrence globales et par domaine ainsi que les délais entre les téléchargements. Si `robots_txt_obey` est actif, il vérifie les règles de robots.txt du domaine et écarte les requêtes interdites sans message. Il envoie ensuite la requête au **gestionnaire de sessions**, qui choisit la session selon le champ `sid`, l’identifiant de session.
4. La **session** récupère la page et renvoie un objet [Response](../fetching/choosing.md#response-object) au **moteur d’exploration**. Le moteur enregistre des statistiques et vérifie si la réponse indique un blocage. Si c’est le cas, il réessaie la requête jusqu’à `max_blocked_retries` fois. Vous pouvez personnaliser la détection et la logique des nouvelles tentatives.
5. Le **moteur d’exploration** passe l’objet [Response](../fetching/choosing.md#response-object) au callback de la requête. Le callback produit soit un dictionnaire, enregistré comme élément extrait, soit une nouvelle requête, envoyée au Scheduler pour rejoindre la file.
6. Le cycle reprend à l’étape 2 jusqu’à ce que la file soit vide et qu’aucune tâche ne soit active, ou que le spider soit mis en pause.
7. Si vous définissez `crawldir` au lancement, le **moteur d’exploration** enregistre régulièrement un point de reprise sur disque avec les requêtes en attente et les URL déjà vues. Lors d’un arrêt propre avec Ctrl+C, il enregistre un dernier point. Au prochain lancement avec le même `crawldir`, le spider restaure la file et continue là où il s’était arrêté, sans exécuter `start_requests()`.

## Composants {#components}

### Spider {#spider}

C’est la classe principale que vous utilisez. Créez une sous-classe de `Spider` et définissez `start_urls` et la méthode `parse()`. Vous pouvez aussi configurer des sessions et redéfinir les hooks des différentes étapes de l’exploration.

```python
from scrapling.spiders import Spider, Response, Request

class MySpider(Spider):
    name = "my_spider"
    start_urls = ["https://example.com"]

    async def parse(self, response: Response):
        for link in response.css("a::attr(href)").getall():
            yield response.follow(link, callback=self.parse_page)

    async def parse_page(self, response: Response):
        yield {"title": response.css("h1::text").get("")}
```

### Moteur d’exploration {#crawler-engine}

Le moteur coordonne toute l’exploration. Il gère la boucle principale, applique les limites de concurrence, envoie les requêtes par le gestionnaire de sessions et traite les résultats des callbacks. Vous ne l’utilisez pas directement : `Spider.start()` et `Spider.stream()` s’en chargent.

### Scheduler {#scheduler}

C’est une file de priorité qui évite les URL en double. Elle calcule l’empreinte de chaque requête à partir de son URL, de sa méthode HTTP, de son corps et de son identifiant de session. Les méthodes `snapshot()` et `restore()` permettent d’enregistrer et de restaurer l’état de l’exploration grâce aux points de reprise.

### Gestionnaire de sessions {#session-manager}

Il gère une ou plusieurs sessions identifiées par un nom. Chaque session peut être :

- [FetcherSession](../fetching/static.md)
- [AsyncStealthySession](../fetching/stealthy.md)

Quand une requête arrive, le gestionnaire choisit la session selon son champ `sid`. Les sessions peuvent démarrer avec le spider, ce qui est le comportement par défaut, ou à leur première utilisation.

### Système de points de reprise {#checkpoint-system}

Ce système facultatif enregistre l’état du robot dans un fichier pickle : les requêtes en attente et les empreintes des URL déjà vues. Les écritures sont atomiques : un fichier temporaire est créé puis renommé pour éviter de corrompre les données. L’état est enregistré à intervalles réglables et lors d’un arrêt propre. Quand l’exploration se termine complètement, sans rester en pause, les fichiers sont supprimés automatiquement.

### Cache des réponses {#response-cache}

Quand le mode développement est actif, ce cache facultatif enregistre les réponses sur disque et les réutilise lors des exécutions suivantes. Chaque réponse est identifiée par l’empreinte de la requête et enregistrée en JSON, avec le corps encodé en base64 pour préserver les données binaires. Il sert à ajuster la logique de `parse()` sans envoyer de nouvelles requêtes aux serveurs. Il n’est pas prévu pour la production.

### Résultats {#output}

Les éléments extraits sont réunis dans un `ItemList`, une sous-classe de liste avec les méthodes d’exportation `to_json()`, `to_jsonl()`, `to_csv()` et `to_xml()`. Les statistiques sont enregistrées dans une dataclass `CrawlStats`, qui contient des informations détaillées sur l’exécution.

## Comparaison avec Scrapy {#comparison-with-scrapy}

Si vous utilisez déjà Scrapy, voici les équivalences dans Scrapling :

| Concept | Scrapy | Scrapling |
|---------|--------|-----------|
| Définition du spider | Sous-classe de `scrapy.Spider` | Sous-classe de `scrapling.spiders.Spider` |
| Requêtes initiales | `start_requests()` | `async start_requests()` |
| Callbacks | `def parse(self, response)` | `async def parse(self, response)` |
| Suivi des liens | `response.follow(url)` | `response.follow(url)` |
| Production d’éléments | `yield dict` ou `yield Item` | `yield dict` |
| File de requêtes | Scheduler + Dupefilter | Scheduler avec suppression des doublons intégrée |
| Téléchargement | Downloader + Middlewares | Gestionnaire de sessions avec prise en charge de plusieurs sessions |
| Traitement des éléments | Item Pipelines | Hook `on_scraped_item()` |
| Détection des blocages | Par des middlewares personnalisés | Hooks intégrés `is_blocked()` + `retry_blocked_request()` |
| Concurrence | Réglage `CONCURRENT_REQUESTS` | Attribut de classe `concurrent_requests` |
| Filtrage des domaines | `allowed_domains` | `allowed_domains` |
| Robots.txt | Réglage `ROBOTSTXT_OBEY` | Attribut de classe `robots_txt_obey` |
| Pause et reprise | Réglage `JOBDIR` | Argument `crawldir` du constructeur |
| Exportation | Feed exports | `result.items.to_json()` / `to_jsonl()` / `to_csv()` / `to_xml()`, ou par des hooks personnalisés |
| Exécution | `scrapy crawl spider_name` | `MySpider().start()` |
| Streaming | Non disponible | `async for item in spider.stream()` |
| Plusieurs sessions | Non disponible | Plusieurs sessions de types différents par spider |
