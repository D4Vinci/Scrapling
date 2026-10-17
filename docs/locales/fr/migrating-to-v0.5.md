---
title: "Migrer vers la v0.5"
description: "Passez de Scrapling v0.4.15 à la v0.5. Mettez à jour les imports du navigateur, la capture réseau, les outils MCP, les commandes CLI, les réglages de l’analyseur et le comportement des spiders."
---

# Migrer vers la v0.5 {#migrating-to-v05}

Ce guide présente les changements à vérifier lors du passage de la **v0.4.15 à la v0.5**. Il couvre les API supprimées, les outils renommés et les corrections qui peuvent modifier les résultats de votre exploration ou vos fichiers enregistrés.

## Liste rapide de migration {#quick-migration-checklist}

| Si vous utilisez... | Ce qu’il faut changer |
| --- | --- |
| `DynamicFetcher`, `DynamicSession` ou `AsyncDynamicSession` | Utilisez la classe furtive correspondante. |
| `capture_xhr` ou `response.captured_xhr` | Utilisez une session de navigateur avec `record_requests=True` et `session.network`. |
| `keep_cdata` | Supprimez-le des réglages de l’analyseur et du fetcher. |
| `scrapling extract stealthy-fetch` ou `stealthy_fetch()` dans le shell | Utilisez `fetch` à la place. |
| Les outils MCP | Mettez à jour les noms des outils, les appels de capture d’écran et le traitement de la réponse de création de session. |
| `response.follow()` après un POST ou une requête avec des paramètres de requête | Transmettez à nouveau la méthode, les paramètres de requête et le corps quand vous en avez besoin. |
| Des points de reprise d’exploration ou des caches de réponses enregistrés | Démarrez une nouvelle exploration si vos requêtes utilisent les données d’entrée de l’empreinte qui ont changé. |
| `robots_txt_obey=True` | Gérez les échecs de récupération de robots.txt, qui bloquent maintenant l’exploration de ce domaine. |

## Récupération avec un navigateur {#browser-fetching}

### Remplacez les classes de navigateur dynamique {#replace-the-dynamic-browser-classes}

Le moteur de navigateur qui utilisait directement Playwright a été supprimé. Toute récupération avec un navigateur utilise maintenant le moteur furtif basé sur Patchright.

| API supprimée | Remplacement |
| --- | --- |
| `scrapling.DynamicFetcher` | `scrapling.StealthyFetcher` |
| `scrapling.fetchers.DynamicFetcher` | `scrapling.fetchers.StealthyFetcher` |
| `scrapling.fetchers.chrome.PlayWrightFetcher` | `scrapling.fetchers.StealthyFetcher` |
| `scrapling.fetchers.DynamicSession` | `scrapling.fetchers.StealthySession` |
| `scrapling.fetchers.AsyncDynamicSession` | `scrapling.fetchers.AsyncStealthySession` |

Le module `scrapling.fetchers.chrome` et le module privé `_browsers._controllers` ont été supprimés. Utilisez les imports publics ci-dessus.

**Avant :**

```python
from scrapling.fetchers import DynamicFetcher

page = DynamicFetcher.fetch("https://example.com", headless=True)
```

**Maintenant :**

```python
from scrapling.fetchers import StealthyFetcher

page = StealthyFetcher.fetch("https://example.com", headless=True)
```

Pour les sessions, remplacez `DynamicSession` par `StealthySession`, ou `AsyncDynamicSession` par `AsyncStealthySession`. Faites le même changement dans la méthode `configure_sessions()` de votre spider. Les modes d’utilisation de `fetch()` et de `async with` restent valables.

Si vos callbacks importent des types du navigateur ou interceptent ses erreurs, remplacez `playwright.sync_api` par `patchright.sync_api`, ou `playwright.async_api` par `patchright.async_api`. Cela concerne notamment `Page`, `Locator`, `Error` et `TimeoutError`.

Patchright évalue le JavaScript dans un contexte isolé par défaut. Si un callback lit les variables JavaScript propres à la page, utilisez `page.evaluate(..., isolated_context=False)`.

Le comportement du navigateur change en plus du nom de l’import. Vérifiez les options du navigateur et les réglages de son empreinte. La résolution de Cloudflare nécessite toujours `solve_cloudflare=True` ; elle n’est pas activée par défaut. De plus, `extra_flags` complète maintenant les options furtives intégrées au lieu de les remplacer.

Consultez [Récupération avec un navigateur](fetching/stealthy.md) pour connaître les options actuelles.

### Remplacez la capture XHR par l’historique réseau de la session {#replace-xhr-capture-with-session-network-history}

Le paramètre `capture_xhr` et l’attribut `Response.captured_xhr` ont été supprimés. Supprimez le paramètre même si sa valeur est `None`. Une récupération ponctuelle n’ajoute plus de liste XHR à sa réponse.

Les intégrations personnalisées qui appellent `ResponseFactory.from_playwright_response()` ou `ResponseFactory.from_async_playwright_response()` doivent aussi supprimer `xhr_captured`. Transmettez `collect_history` par son nom pour éviter les problèmes liés au changement d’ordre des arguments positionnels.

**Avant :**

```python
from scrapling.fetchers import StealthyFetcher

page = StealthyFetcher.fetch("https://example.com", capture_xhr="/api/")
for response in page.captured_xhr:
    print(response.url, response.body)
```

**Maintenant :**

```python
from scrapling.fetchers import StealthySession

with StealthySession(record_requests=True) as session:
    page = session.fetch("https://example.com", network_idle=True)
    for response in session.network.search(url_pattern=r"/api/", limit=None):
        print(response.url, response.body)
```

Utilisez `AsyncStealthySession` et `await session.fetch(...)` pour le code asynchrone. Lire `session.network` ne nécessite pas `await`.

Voici quelques différences importantes :

- Définissez `record_requests=True` lors de la création de la session. C’est un réglage de session, pas un réglage par récupération.
- L’historique appartient à **toute la session**, y compris les onglets, les chargements de pages et les actions. Utilisez `after_id`, des filtres ou `session.network.clear()` si vous avez besoin d’un périmètre plus réduit.
- Déplacez l’ancienne expression régulière de `capture_xhr` vers `url_pattern` lors des recherches dans l’historique.
- `search()` renvoie des objets `Response` enregistrés. Lisez directement `.url`, `.status`, `.headers`, `.body` ou `.json()`. L’identifiant d’enregistrement, le type de ressource et le corps envoyé sont dans `response.meta["network_id"]`, `response.meta["resource_type"]` et `response.meta["request_body"]`.
- L’historique Python inclut tous les types de ressources par défaut. Utilisez `resource_type="xhr"` ou `resource_type="fetch"` pour en choisir un, ou `include_static=False` pour les requêtes XHR/fetch et les erreurs HTTP.
- `search()` renvoie au maximum 100 résultats par défaut. Transmettez `limit=None` pour obtenir tous les résultats conservés. Les sessions conservent au maximum 1 000 requêtes par défaut ; modifiez cette limite avec `max_recorded_requests`.
- Seules les requêtes terminées sont enregistrées. La capture du corps se limite aux types de contenu textuel pris en charge, à 1 MiB par réponse et à 20 MiB de données de corps conservées au total. Les anciens enregistrements peuvent être supprimés lorsque les limites sont atteintes. Consultez `response.meta.get("body_note")` pour savoir pourquoi un corps a été ignoré.
- La lecture de l’historique et la fermeture de la session n’attendent pas la fin des captures en cours. Attendez les données dont vous avez besoin avant de les lire. L’historique Python enregistré reste lisible après la fermeture de la session.

Consultez [Historique réseau](fetching/stealthy.md#network-history) pour connaître les filtres et les limites.

## Réglages de l’analyseur {#parser-settings}

### Supprimez `keep_cdata` {#remove-keep_cdata}

`keep_cdata` a été supprimé de `Selector`, de la configuration des fetchers et des réglages renvoyés par `display_config()`. Supprimez-le des appels directs à l’analyseur, de `Fetcher.configure(...)` et des dictionnaires `selector_config` transmis aux fetchers ou aux intégrations.

**Avant :**

```python
from scrapling import Selector

page = Selector("<p>Hello</p>", keep_cdata=True)
```

**Maintenant :**

```python
from scrapling import Selector

page = Selector("<p>Hello</p>")
```

Il n’existe pas de réglage de remplacement. Ce réglage n’affectait pas la sortie de l’analyseur HTML. Si vous transmettiez les options de l’analyseur par position, supprimez l’ancien argument `keep_cdata` et utilisez des arguments nommés pour `adaptive` et les options de stockage.

## Ligne de commande et shell interactif {#command-line-and-interactive-shell}

### Utilisez `fetch` pour les requêtes du navigateur {#use-fetch-for-browser-requests}

La CLI n’a plus qu’une commande de navigateur : `scrapling extract fetch`. Elle utilise `StealthyFetcher`.

**Avant :**

```bash
scrapling extract stealthy-fetch "https://example.com" page.md
```

**Maintenant :**

```bash
scrapling extract fetch "https://example.com" page.md
```

Si vous utilisez déjà `scrapling extract fetch`, le nom de la commande reste le même, mais son moteur passe de `DynamicFetcher` à `StealthyFetcher`. Les options telles que `--solve-cloudflare` appartiennent maintenant à `fetch`.

Dans `scrapling shell`, remplacez `stealthy_fetch(...)` par `fetch(...)`. Le raccourci existant `fetch(...)` appelle maintenant `StealthyFetcher.fetch`. Les classes dynamiques ne sont plus ajoutées à l’espace de noms du shell.

### Lisez les fichiers Markdown et texte en UTF-8 {#read-markdown-and-text-files-as-utf-8}

Les commandes d’extraction et `Convertor.write_content_to_file()` écrivent maintenant les fichiers `.md` et `.txt` en **UTF-8**, quel que soit le jeu de caractères de la page source. Mettez à jour le code qui lit ces fichiers avec l’encodage d’origine de la page. La sortie `.html` utilise toujours `page.encoding`.

Le Markdown provenant de plusieurs éléments sélectionnés comporte maintenant des lignes vides entre les éléments. Cela s’applique à `Response.markdown()` et aux fichiers Markdown produits. Mettez à jour les comparaisons exactes de la sortie ou les empreintes de hachage enregistrées qui dépendaient du texte concaténé.

## Serveur MCP {#mcp-server}

Mettez à jour les prompts enregistrés, les listes d’outils autorisés, les wrappers et les définitions d’outils du client MCP. Redémarrez ou reconnectez votre client MCP après la mise à jour du serveur pour qu’il lise les outils actuels.

### Mettez à jour les noms d’outils et les appels par lot {#update-tool-names-and-bulk-calls}

| Outil de la v0.4.15 | Remplacement dans la v0.5 |
| --- | --- |
| `fetch`, `stealthy_fetch` | `browser_fetch_once` |
| `open_session` | `browser_open` |
| `session_fetch` | `browser_fetch` |
| `screenshot` | `browser_screenshot` |
| `bulk_fetch`, `bulk_stealthy_fetch` | Un appel à `browser_fetch_once` par URL, ou plusieurs appels à `browser_fetch` dans une session ouverte |
| `bulk_get` | Un appel à `make_request` ou à `session_make_request` par URL |

Tous les outils par lot ont été supprimés. Les outils qui récupèrent une seule URL renvoient un seul `ResponseModel` avec `status`, `content` et `url`, pas une liste de réponses. `content` reste lui-même une liste de chaînes.

Tous les outils de navigateur MCP utilisent maintenant le moteur furtif. Supprimez `session_type` des appels à `browser_open` ; le navigateur dynamique n’est plus proposé. Le résultat contient `session_type="stealthy"`. Les sessions HTTP utilisent toujours `open_request_session` et renvoient `session_type="static"`.

Les intégrations Python doivent aussi cesser d’importer `BrowserSessionType`, qui a été supprimé. `SessionType` n’accepte maintenant que `"stealthy"` et `"static"`.

Les appels dans une même session de navigateur doivent s’exécuter dans l’ordre, car ils partagent une page. Fermez les sessions avec `close_session` quand vous avez terminé.

### Lisez les réglages avec `list_sessions` {#read-settings-through-list_sessions}

`browser_open` et `open_request_session` renvoient maintenant uniquement :

```json
{
  "session_id": "my-session",
  "session_type": "stealthy"
}
```

Le résultat de création n’inclut plus `created_at`, `is_alive`, `settings` ni `message`. Appelez `list_sessions` pour obtenir les trois premiers champs. Le `message` de confirmation a été supprimé. Le code qui supposait que `SessionCreatedModel` possédait tous les champs de `SessionInfo` doit aussi changer.

### Récupérez la page avant de faire une capture d’écran {#fetch-before-taking-a-screenshot}

`browser_screenshot` capture la **page actuelle sans la recharger**. Cet outil n’accepte plus d’URL ni les anciennes options de navigation et d’attente : `wait`, `wait_selector`, `wait_selector_state` et `network_idle`.

Suivez cet ordre :

1. Appelez `browser_open`.
2. Appelez `browser_fetch` avec l’URL et les options de chargement de page nécessaires.
3. Si nécessaire, appelez `browser_actions` pour interagir avec la page ou attendre du contenu.
4. Appelez `browser_screenshot` avec l’identifiant de session.
5. Appelez `close_session` quand vous avez terminé.

Par exemple, les arguments pour une capture de la page entière sont :

```json
{
  "session_id": "my-session",
  "full_page": true
}
```

Le `timeout` de cet outil limite maintenant l’opération de capture d’écran. L’outil ne charge pas de page. Pour capturer un élément, utilisez `selector` ou `ref`, et ne définissez pas `full_page=true`.

Les captures d’écran renvoient toujours des blocs de contenu image et texte, avec l’URL de la page actuelle dans le bloc texte. Elles ne renvoient pas de `ResponseModel` de récupération.

Consultez le [guide MCP](ai/mcp-server.md) et la [référence de l’API](api-reference/mcp-server.md) pour connaître les schémas complets.

## Spiders et requêtes HTTP {#spiders-and-http-requests}

### Transmettez à nouveau les données de requête quand vous suivez un lien {#pass-request-data-again-when-following-a-link}

`response.follow()` ne copie plus `method`, `params`, `data`, `json`, `files` ni `multipart` depuis la requête précédente. Cette méthode supprime aussi les en-têtes `Content-Length` hérités de `headers` et `extra_headers`.

Un lien suivi commence maintenant par une simple requête GET, sauf si vous transmettez explicitement les données de requête. Les autres réglages partagés, comme la session, le proxy et les callbacks, suivent toujours les règles d’héritage existantes.

Si votre ancien code dépendait de données POST héritées, remplacez :

```python
yield response.follow("/next")
```

par :

```python
yield response.follow("/next", method="POST", json={"page": 2})
```

Transmettez aussi explicitement `params` lorsque la requête suivante en a besoin. Laissez le client HTTP calculer le nouveau `Content-Length`.

### Vérifiez les empreintes des requêtes et l’état d’exploration enregistré {#check-request-fingerprints-and-saved-crawl-state}

L’empreinte d’une requête est la clé utilisée pour détecter les doublons et trouver les réponses en cache. Ses données d’entrée traitent maintenant trois cas différemment :

- Les `params` sont fusionnés avec l’URL avant la création de la clé. Les requêtes vers la même URL avec des paramètres de requête différents ne sont plus considérées comme des doublons par défaut.
- Les corps JSON tels que `{}`, `[]`, `false`, `0` et `""` sont conservés dans la clé. Ils ne partagent plus la clé d’un corps absent. `None` signifie toujours qu’il n’y a pas de corps JSON.
- Avec `fp_include_headers=True`, changer uniquement l’ordre d’insertion des en-têtes ne change plus la clé.

Si votre exploration utilise ces données d’entrée, terminez-la avant la mise à jour ou démarrez une nouvelle exploration avec un nouveau point de reprise et un nouveau répertoire de cache de réponses. Les anciennes clés enregistrées peuvent différer des nouvelles. Il s’agit d’un changement d’identité des requêtes, pas d’un nouveau format de fichier de point de reprise.

Le mode développement n’écrit maintenant les réponses dans le cache qu’après avoir vérifié si elles sont bloquées. Les pages bloquées ne sont pas enregistrées comme des résultats réussis dans le cache. Les fichiers de cache existants ne sont pas nettoyés automatiquement ; supprimez les entrées obsolètes si vous avez déjà mis en cache une page de vérification.

Les explorations qui échouent conservent maintenant leurs fichiers de points de reprise. Vérifiez votre code de nettoyage s’il supposait que ces fichiers disparaissaient après une erreur. Consultez [Pause et reprise](spiders/advanced.md#pause-resume) et [Mode développement](spiders/advanced.md#development-mode).

### Vérifiez les échecs de robots.txt {#check-robotstxt-failures}

Avec `robots_txt_obey=True`, une exception lors de la récupération de robots.txt ou une réponse autre que HTTP 200 ou 4xx bloque maintenant les requêtes vers ce domaine. Auparavant, ces échecs autorisaient l’exploration. HTTP 200 fournit toujours les règles, et HTTP 4xx autorise toujours l’accès.

Le résultat est mis en cache pour toute l’exploration. Corrigez le problème d’accès à robots.txt et démarrez une nouvelle exploration ; les requêtes suivantes de la même exploration ne réessaieront pas la récupération qui a échoué. Cela ne change pas la valeur par défaut `robots_txt_obey=False`.

### Vérifiez les restrictions de liens et les callbacks de sitemaps {#check-link-restrictions-and-sitemap-callbacks}

- Une restriction de `LinkExtractor` qui ne correspond à rien ne renvoie maintenant aucun lien. Elle ne revient plus à la page entière. Corrigez l’expression `restrict_css` ou `restrict_xpath` si votre exploration trouve maintenant moins de liens.
- Une restriction peut maintenant sélectionner l’élément du lien lui-même, pas seulement un parent. Cela peut ajouter des liens qui étaient ignorés auparavant. Vérifiez les ensembles d’URL attendus.
- `SitemapSpider` envoie maintenant les URL des pages à `parse()` lorsqu’il n’y a pas de règles, ou lorsqu’une règle correspondante a `callback=None`. Il ne renvoie plus ces pages HTML à l’analyseur de sitemap. Implémentez `parse()` pour ces cas et supprimez les contournements de l’ancien routage.
- La marque d’ordre des octets Unicode en début de robots.txt et des flux CSV est supprimée. La première directive robots prend maintenant effet, et le premier en-tête CSV ne commence plus par `\ufeff`. Si vous définissez des `headers` personnalisés, la marque est supprimée de la valeur du premier champ à la place. Mettez à jour le code qui contournait ce préfixe invisible. Les commentaires XML et les instructions de traitement des sitemaps sont aussi ignorés au lieu de provoquer un échec de l’analyse.

### Vérifiez les données de formulaire, les en-têtes et le JSON de la CLI {#check-form-data-headers-and-cli-json}

Les données de formulaire sous forme de dictionnaire développent maintenant les valeurs de listes et de tuples en clés répétées. Par exemple, `data={"tag": ["a", "b"]}` envoie `tag=a&tag=b`. Une liste vide n’envoie aucune entrée pour cette clé. L’en-tête par défaut `Content-Type: application/x-www-form-urlencoded` est ajouté lorsque vous n’en fournissez pas.

Si vous avez besoin d’un autre format d’envoi, transmettez une chaîne ou des octets explicitement encodés. `json`, le `content` brut et les envois multipart conservent leur propre traitement du corps. Les valeurs `None` **ne sont pas supprimées** des données de formulaire ni des paramètres de requête ; elles restent la chaîne `None`.

Les en-têtes HTTP de chaque requête remplacent maintenant ceux de la session sans distinguer les majuscules des minuscules. Un en-tête de requête nommé `authorization` remplace l’`Authorization` de la session au lieu d’envoyer les deux. Supprimez le code qui contournait les noms d’en-têtes en double.

Les valeurs JSON de la CLI `{}`, `[]`, `false`, `0` et `""` sont maintenant envoyées au lieu d’être ignorées sans avertissement. De plus, `curl2fetcher()` applique maintenant l’agent utilisateur de l’option `-A` de curl et transmet correctement les proxies de `-x` sous forme de chaîne URL. Un en-tête curl explicite `-H 'User-Agent: ...'` reste prioritaire sur `-A`.

## Autres changements de sortie à vérifier {#other-output-changes-to-check}

Ces corrections ne suppriment pas d’API, mais elles peuvent modifier les résultats enregistrés et les tests de sortie exacte :

- Les sélecteurs CSS et XPath générés incluent maintenant `:nth-of-type(1)` ou `[1]` lorsque c’est nécessaire pour identifier le premier de plusieurs éléments frères de même balise. Mettez à jour les chaînes de sélecteurs attendues ; ne supprimez pas le nouveau repère de position.
- Le contenu nettoyé pour l’IA conserve maintenant les éléments visibles avec des valeurs comme `opacity:0.95`, supprime les éléments masqués par davantage de variantes de styles en ligne et les éléments `<slot hidden>`, et supprime toutes les balises parasites correspondantes, même imbriquées. Vérifiez à nouveau la sortie exacte en Markdown, en texte et en HTML assaini.
- La conversion des réponses du navigateur lit maintenant les déclarations de charset avec des différences de majuscules et de minuscules, des espaces ou des valeurs entre guillemets, comme `text/plain; CHARSET = "iso-8859-15"`. Les réponses non HTML avec ces en-têtes utilisent maintenant l’encodage déclaré au lieu de se rabattre sur UTF-8. Vérifiez à nouveau le texte décodé à partir de ces réponses.

## Vérifiez la mise à jour {#verify-your-upgrade}

Exécutez une petite exploration avant votre tâche complète. Vérifiez les données extraites, les URL suivies, les corps des requêtes envoyées, l’encodage des fichiers enregistrés et les comportements du cache ou des points de reprise dont vous dépendez. Pour les intégrations MCP, vérifiez les données d’entrée des outils et les données renvoyées par rapport aux schémas actuels.

Pour les changements des versions précédentes, consultez le [journal des modifications](changelog.md).
