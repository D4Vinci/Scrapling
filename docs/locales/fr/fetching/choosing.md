---
title: "Choisissez des requêtes HTTP ou un navigateur pour le web scraping"
description: "Choisissez Fetcher ou StealthyFetcher selon votre tâche. Découvrez quand utiliser HTTP directement, exécuter JavaScript et réutiliser des sessions."
---

# Les bases des fetchers {#fetchers-basics}

## Introduction {#introduction}
Les fetchers sont des classes qui envoient des requêtes ou récupèrent des pages en une ligne de code, puis renvoient un objet [Response](#response-object). Depuis la v0.3, des classes de session distinctes permettent de garder la session ouverte. Par exemple, une session de navigateur garde le navigateur ouvert jusqu’à la fin de toutes vos requêtes, au lieu d’en ouvrir plusieurs. Choisissez selon vos besoins.

Ces fonctions ont été ajoutées parce qu’avant la v0.2, Scrapling servait uniquement à analyser des pages. L’objectif est de couvrir peu à peu tous les besoins du web scraping.

> Les fetchers ne sont pas de simples enveloppes autour d’autres bibliothèques. Ils les utilisent comme moteurs pour envoyer des requêtes et récupérer des pages, mais ajoutent des fonctions absentes de ces moteurs. Ils tirent aussi parti de leurs capacités et les optimisent pour le web scraping.

## Comparaison des fetchers {#fetchers-overview}

Scrapling propose des fetchers HTTP (`Fetcher` et `AsyncFetcher`) et un fetcher de navigateur (`StealthyFetcher`), avec des classes de session pour les requêtes répétées.

Ce tableau vous aide à comparer et à choisir :


| Fonction | Fetcher | StealthyFetcher |
|--------------------|---------------------------------------------------|--------------------------------------------------------------------------------------------|
| Vitesse relative | 🐇🐇🐇🐇🐇 | 🐇🐇🐇 |
| Discrétion | ⭐⭐ | ⭐⭐⭐⭐⭐ |
| Options contre la détection de bots | ⭐⭐ | ⭐⭐⭐⭐⭐ |
| Exécution de JavaScript | ❌ | ✅ |
| Utilisation de la mémoire | ⭐ | ⭐⭐⭐ |
| Usage conseillé | Extraction simple quand les requêtes HTTP suffisent | - Sites chargés dynamiquement <br/>- Petites automatisations <br/>- Protections simples ou complexes |
| Navigateurs | ❌ | Chromium et Google Chrome |
| API de navigateur utilisée | ❌ | Playwright |
| Difficulté de configuration | Simple | Simple |

Nous détaillerons chaque outil dans les pages suivantes.

## Configurer le parser de tous les fetchers {#parser-configuration-in-all-fetchers}
Tous les fetchers s’importent de la même façon :
```python
from scrapling.fetchers import Fetcher, AsyncFetcher, StealthyFetcher
```
Vous pouvez ensuite les utiliser directement, sans créer d’objet. Les réglages par défaut du parser sont appliqués :
```python
page = StealthyFetcher.fetch('https://example.com') 
```
Pour configurer le parser, c’est-à-dire la [classe Selector](../parsing/main_classes.md#selector), qui traite la réponse avant de vous la renvoyer, faites d’abord ceci :
```python
from scrapling.fetchers import Fetcher
Fetcher.configure(adaptive=True, keep_comments=False)  # and the rest
```
Ou :
```python
from scrapling.fetchers import Fetcher
Fetcher.adaptive=True
Fetcher.keep_comments=False
```
Continuez ensuite votre code normalement.

Les arguments disponibles sont `adaptive`, `adaptive_domain`, `huge_tree`, `keep_comments`, `storage` et `storage_args`. Ce sont les mêmes que ceux de [Selector](../parsing/main_classes.md#selector). Vous pouvez afficher la configuration actuelle avec `<fetcher_class>.display_config()`.

!!! info "Information"

    `adaptive` est désactivé par défaut. Vous devez l’activer pour utiliser cette fonction.

### Configurer le parser pour chaque requête {#set-parser-config-per-request}
Les réglages précédents s’appliquent à toutes les requêtes envoyées par cette classe pour simplifier l’utilisation.

Si vous avez besoin de réglages différents pour chaque requête, passez un dictionnaire à l’argument `selector_config` de la méthode utilisée (`fetch`/`get`/`post`/...).

## Objet Response {#response-object}
`Response` fonctionne comme [Selector](../parsing/main_classes.md#selector), mais ajoute des informations sur la réponse, comme les en-têtes, le statut et les cookies :
```python
from scrapling.fetchers import Fetcher
page = Fetcher.get('https://example.com')

page.status          # HTTP status code
page.reason          # Status message
page.cookies         # Response cookies as a dictionary
page.headers         # Response headers
page.request_headers # Request headers
page.history         # Response history of redirections, if any
page.body            # Raw response body as bytes
page.encoding        # Response encoding
page.meta            # Response metadata dictionary (e.g., proxy used). Mainly helpful with the spiders system.
```
Tous les fetchers renvoient `Response`. Les sessions de navigateur avec `record_requests=True` renvoient aussi des objets `Response` enregistrés via `session.network.search(limit=None)` et `session.network.get(request_id)`. Consultez l’[historique réseau](stealthy.md#network-history) pour utiliser les réponses d’API enregistrées et migrer vers la v5.

`Response` peut aussi convertir la page en Markdown propre, prêt pour les modèles de langage, en une ligne :
```python
markdown = Fetcher.get('https://example.com').markdown(main_content_only=True)
```
Avant la conversion, les scripts, les styles, le contenu caché et les tentatives d’injection d’instructions sont toujours supprimés. Vous pouvez passer `css_selector` pour ne convertir que certains éléments. Cela nécessite l’extra `rag`, également inclus dans `ai`/`shell`/`all`. La page [Créer des systèmes RAG](../ai/building-rag-systems.md) donne plus de détails.

!!! note "Note"

    Contrairement à [Selector](../parsing/main_classes.md#selector), le corps de `Response` est toujours en octets depuis la v0.4.
