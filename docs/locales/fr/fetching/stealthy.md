---
title: "Extrayez les données de sites JavaScript avec StealthyFetcher"
description: "Chargez des pages, attendez les données, réutilisez l’état de connexion et lisez les réponses d’API en arrière-plan avec les sessions de navigateur Scrapling. Configurez les proxies et la résolution des défis."
---

# Récupérer des pages avec StealthyFetcher {#browser-fetching-with-stealthyfetcher}

`StealthyFetcher` charge les pages JavaScript et automatise Chromium ou Google Chrome avec des fonctions contre la détection de bots. Il utilise l’[API de Playwright](https://playwright.dev/python/docs/intro) avec des correctifs pour masquer l’automatisation.

Pour automatiser une page, vous aurez besoin de connaître un peu l’[API Page de Playwright](https://playwright.dev/python/docs/api/class-page), comme nous le verrons plus loin.

!!! success "Avant de commencer"

    1. Lisez [Les bases des fetchers](../fetching/choosing.md) pour comprendre l’[objet Response](../fetching/choosing.md#response-object) et choisir un fetcher.
    2. Lisez [Rechercher des éléments](../parsing/selection.md) pour savoir comment trouver et extraire des éléments de [Selector](../parsing/main_classes.md#selector)/[Response](../fetching/choosing.md#response-object).
    3. Lisez [Classes principales](../parsing/main_classes.md) pour connaître les propriétés et méthodes de [Selector](../parsing/main_classes.md#selector) dont hérite [Response](../fetching/choosing.md#response-object).

## Utilisation de base {#basic-usage}
La principale façon d’importer ce fetcher est la même que pour les autres :

```python
from scrapling.fetchers import StealthyFetcher
```
Consultez la configuration du parser [ici](choosing.md#parser-configuration-in-all-fetchers).

Nous allons présenter les principaux arguments avec des exemples. Pour consulter directement le tableau complet, [allez à cette section](#full-list-of-arguments).

!!! abstract "Note"

    La version asynchrone de `fetch` se nomme `async_fetch`.


Ce fetcher propose trois grandes options d’exécution, que vous pouvez combiner selon vos besoins.

Les voici :

### 1. Chromium inclus {#1-bundled-chromium}
```python
StealthyFetcher.fetch('https://example.com')
```
Ouvre le navigateur Chromium inclus, applique les réglages de discrétion par défaut et charge la page.

### 2. Google Chrome installé {#2-real-chrome}
```python
StealthyFetcher.fetch('https://example.com', real_chrome=True)
```
Utilisez cette option si Google Chrome est installé. Elle fonctionne comme la précédente, mais ouvre votre copie de Google Chrome à la place de Chromium. Cela rend vos requêtes plus réalistes et moins faciles à détecter.

Si vous n’avez pas Google Chrome, vous pouvez l’installer pour la bibliothèque avec cette commande dans le terminal :
```commandline
playwright install chrome
```

### 3. Connexion CDP {#3-cdp-connection}
```python
StealthyFetcher.fetch('https://example.com', cdp_url='ws://localhost:9222')
```
Au lieu de lancer un navigateur local, vous pouvez vous connecter à un navigateur distant via le [Chrome DevTools Protocol](https://chromedevtools.github.io/devtools-protocol/).

L’URL peut être une adresse WebSocket (`ws://`/`wss://`), comme celles fournies par les services de navigateurs, ou l’adresse HTTP d’un navigateur, par exemple `http://localhost:9222`.


## Que fait-il ? {#what-does-it-do}

StealthyFetcher propose ces fonctions contre la détection de bots :

1. Résout automatiquement tous les types de Cloudflare Turnstile et Interstitial avec `solve_cloudflare=True`.
2. Évite les fuites liées à l’environnement d’exécution CDP et à WebRTC.
3. Isole l’exécution de JavaScript, supprime de nombreuses traces de Playwright et évite la détection de certains comportements typiques des bots.
4. Ajoute du bruit au canvas pour empêcher son utilisation comme empreinte.
5. Corrige des méthodes connues de détection du mode sans interface et propose une option contre la détection par différence de fuseau horaire.
6. Inclut d’autres options pour contourner les protections.

## Liste complète des arguments {#full-list-of-arguments}
Ce fetcher et ses classes de session proposent de nombreuses options. Avant les [exemples](#examples), voici la liste complète :


| Argument | Description | Facultatif |
|:---------------------:|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|:--------:|
|          url          | URL cible. |    ❌     |
|       headless        | Utilisez `True` pour exécuter le navigateur sans interface visible (**par défaut**), ou `False` pour l’afficher. |    ✔️    |
|   disable_resources   | Ignore les ressources inutiles pour accélérer le chargement. Bloque les types `font`, `image`, `media`, `beacon`, `object`, `imageset`, `texttrack`, `websocket`, `csp_report` et `stylesheet`. |    ✔️    |
|        cookies        | Cookies de la prochaine requête. |    ✔️    |
|       useragent       | Chaîne de user agent à utiliser. **Sans valeur personnalisée, le fetcher en génère une réelle pour le même navigateur et la même version.** |    ✔️    |
|     network_idle      | Attend que la page passe au moins 500 ms sans connexion réseau. |    ✔️    |
|       load_dom        | Attend l’état `domcontentloaded` pour le chargement et l’exécution de JavaScript. Activé par défaut. |    ✔️    |
|     pierce_shadow     | Inclut le contenu du Shadow DOM ouvert dans le HTML de la réponse. Vaut `False` par défaut. Peut être défini pour la session ou modifié par requête. |    ✔️    |
|        timeout        | Délai maximal en millisecondes pour les opérations et les attentes de la page. Par défaut : 30 000 ms, soit 30 secondes. |    ✔️    |
|         wait          | Millisecondes d’attente après toutes les opérations, avant de fermer la page et de renvoyer `Response`. |    ✔️    |
|      page_action      | Fonction d’automatisation qui reçoit `page` et s’exécute après la navigation. |    ✔️    |
|      page_setup       | Fonction qui reçoit `page` et s’exécute avant la navigation. Sert à enregistrer des événements ou des routes avant le chargement. |    ✔️    |
|     wait_selector     | Attend qu’un sélecteur CSS atteigne un état précis. |    ✔️    |
|      init_script      | Chemin absolu d’un fichier JavaScript exécuté à la création de chaque page de la session. |    ✔️    |
|  wait_selector_state  | État que doit atteindre le sélecteur fourni à `wait_selector`. _Par défaut : `attached`._ |    ✔️    |
|     google_search     | Définit un referer Google. Activé par défaut. |    ✔️    |
|     extra_headers     | Dictionnaire d’en-têtes supplémentaires. _Le referer défini par `google_search` a priorité sur celui indiqué ici._ |    ✔️    |
|         proxy         | Proxy des requêtes. Accepte une chaîne ou un dictionnaire avec les clés 'server', 'username' et 'password'. |    ✔️    |
|      real_chrome      | Activez cette option pour ouvrir et utiliser le Google Chrome installé sur votre appareil. |    ✔️    |
|        locale         | Paramètres régionaux, comme `en-GB` ou `de-DE`. Affectent `navigator.language`, l’en-tête `Accept-Language` et les formats des nombres et des dates. Utilisent les valeurs du système par défaut. |    ✔️    |
|      timezone_id      | Fuseau horaire du navigateur. Celui du système par défaut. |    ✔️    |
|        cdp_url        | URL CDP à laquelle se connecter pour contrôler un navigateur existant au lieu d’en ouvrir un. |    ✔️    |
|     user_data_dir     | Dossier de données du navigateur, comme les cookies et le stockage local. Un dossier temporaire est créé par défaut. **Fonctionne uniquement avec les sessions.** |    ✔️    |
|      extra_flags      | Liste d’options supplémentaires passées au lancement du navigateur. |    ✔️    |
|   solve_cloudflare    | Résout les différents types de défis Turnstile et Interstitial de Cloudflare avant de renvoyer la réponse. Vaut `False` par défaut. |    ✔️    |
|     block_webrtc      | Force WebRTC à respecter les réglages du proxy pour éviter de révéler l’IP locale. |    ✔️    |
|      hide_canvas      | Ajoute du bruit aléatoire au canvas pour empêcher son utilisation comme empreinte. |    ✔️    |
|      allow_webgl      | Activé par défaut. Le désactiver supprime toute prise en charge de WebGL et WebGL 2.0. Ce n’est pas conseillé : de nombreux WAF vérifient si WebGL est disponible. |    ✔️    |
|    additional_args    | Réglages supplémentaires pour le contexte Playwright. Ils ont priorité sur ceux de Scrapling. |    ✔️    |
|    selector_config    | Dictionnaire de réglages du parser pour créer l’objet `Selector`/`Response` final. |    ✔️    |
|    blocked_domains    | Ensemble de domaines à bloquer, y compris leurs sous-domaines. Par exemple, `"example.com"` bloque aussi `"sub.example.com"`. |    ✔️    |
|       block_ads       | Bloque les requêtes vers environ 3 500 domaines connus de publicité et de suivi. Peut être combiné avec `blocked_domains`. |    ✔️    |
|    dns_over_https     | Envoie les requêtes DNS via le DNS-over-HTTPS de Cloudflare pour éviter les fuites lors de l’utilisation de proxies. |    ✔️    |
|     proxy_rotator     | Objet `ProxyRotator` pour changer automatiquement de proxy. Ne peut pas être combiné avec `proxy`. |    ✔️    |
|        retries        | Nombre de tentatives pour les requêtes échouées. 3 par défaut. |    ✔️    |
|      retry_delay      | Secondes d’attente entre les tentatives. 1 par défaut. |    ✔️    |
|    record_requests    | Conserve les requêtes terminées et les réponses enregistrées dans `session.network`. Réservé aux sessions. Vaut `False` par défaut. |    ✔️    |
| max_recorded_requests | Nombre maximal de requêtes conservées par session. 1 000 par défaut. Le contenu enregistré a aussi des limites de taille fixes. |    ✔️    |
|    executable_path    | Chemin absolu d’un exécutable de navigateur personnalisé à utiliser à la place du Chromium inclus. Utile pour les installations ou versions particulières. |    ✔️    |

Dans les classes de session, vous pouvez définir ces arguments pour toute la session. Vous pouvez aussi modifier par requête les réglages propres à l’onglet : `google_search`, `timeout`, `wait`, `page_action`, `page_setup`, `extra_headers`, `disable_resources`, `wait_selector`, `wait_selector_state`, `network_idle`, `load_dom`, `pierce_shadow`, `solve_cloudflare`, `blocked_domains`, `proxy` et `selector_config`.

!!! note "Notes"

    1. Dans mes tests, `disable_resources` a accéléré les requêtes d’environ 25 % sur certains sites. Il peut aussi réduire le trafic du proxy. Utilisez-le avec prudence : certains sites pourraient ne jamais finir de charger.
    2. `google_search` est activé par défaut et définit le referer sur `https://www.google.com/`. Si vous utilisez aussi `extra_headers`, il a priorité sur le referer indiqué dans ce dictionnaire.
    3. Si vous ne définissez pas de user agent et utilisez le mode sans interface, un user agent réel est généré pour la même version du navigateur. Sans user agent personnalisé et avec un navigateur visible, celui du navigateur est utilisé, comme dans les versions actuelles des navigateurs ordinaires.
    4. `init_script` est enregistré dans le contexte du navigateur et exécuté à la création des pages. Le mode discret utilise par défaut l’environnement isolé de Patchright. Si `page_action` doit lire des variables que le script place dans `window`, appelez `page.evaluate(..., isolated_context=False)` dans l’action.

## Gestion des sessions {#session-management}

Pour garder le navigateur ouvert et envoyer plusieurs requêtes avec les mêmes réglages, utilisez `StealthySession`/`AsyncStealthySession`. Ces classes acceptent tous les arguments de `fetch` pour configurer toute la session.

```python
from scrapling.fetchers import StealthySession


with StealthySession(
    headless=True,
    disable_resources=True,
    real_chrome=True
) as session:

    page1 = session.fetch('https://example1.com')
    page2 = session.fetch('https://example2.com')
    page3 = session.fetch('https://dynamic-site.com')


```

### Utiliser les sessions asynchrones {#async-session-usage}

```python
import asyncio
from scrapling.fetchers import AsyncStealthySession

async def scrape_multiple_sites():
    async with AsyncStealthySession(
        network_idle=True,
        timeout=30000,
        max_pages=3
    ) as session:

        pages = await asyncio.gather(
            session.fetch('https://spa-app1.com'),
            session.fetch('https://spa-app2.com'),
            session.fetch('https://dynamic-content.com')
        )
        return pages
```

L’argument `max_pages` définit le nombre maximal d’onglets ouverts en même temps. La session garde un **ensemble d’onglets réutilisables**. Chaque onglet reste ouvert à la fin de sa requête. Pour chaque nouvelle requête, la bibliothèque procède ainsi :

1. Réutilise un onglet libre s’il y en a un. Elle applique les réglages de la requête (`timeout`, `extra_headers`, `disable_resources`, `blocked_domains`, etc.) pour ne pas conserver ceux de la précédente.
2. S’il n’y a pas d’onglet libre, elle en ouvre un autre tant que `max_pages` n’est pas atteint.
3. Si la limite est atteinte, elle vérifie plusieurs fois par seconde si un onglet se libère, pendant 60 secondes. Elle lève ensuite `TimeoutError`. Cela peut arriver si le site ne répond plus.

Les onglets qui rencontrent une erreur sont fermés et remplacés. Vous pouvez aussi tous les fermer avec `session.close_pages()`. La prochaine requête en ouvrira un nouveau.

Cela permet de récupérer plusieurs URL en même temps dans le même navigateur, en économisant des ressources et en gagnant beaucoup de temps :)

Comme l’onglet reste ouvert, la page précédente s’y trouve toujours. Le `page_setup` de la prochaine requête s’exécute avant de la quitter. Cela permet d’enchaîner des actions entre les requêtes.

Les versions 0.3.2 à 0.4.14 fermaient chaque onglet à la fin de la requête, car leur réutilisation laissait passer des réglages d’une requête à l’autre. Depuis la 0.4.15, les réglages sont réinitialisés à chaque réutilisation et les onglets restent ouverts.

### Enregistrer et charger l’état de session {#save-and-load-session-state}

Utilisez `save_state(path)` pour enregistrer les cookies, le stockage local et IndexedDB dans un fichier JSON. Utilisez `load_state(path)` pour le restaurer dans une autre session ou remplacer l’état de la session actuelle. Les deux méthodes acceptent une chaîne ou un `pathlib.Path` et renvoient `None`. Le format est compatible avec les fichiers d’état de Playwright.

```python
from scrapling.fetchers import StealthySession

with StealthySession() as session:
    session.fetch('https://example.com')
    session.save_state('state.json')

with StealthySession() as session:
    session.load_state('state.json')
    page = session.fetch('https://example.com')
```

Enregistrez l’état après la connexion au site ou après vos actions dans le navigateur. Appelez les deux méthodes dans une session démarrée, une fois les requêtes en cours terminées. Le chargement remplace les cookies, le stockage local et IndexedDB existants. Récupérez ou rechargez la page pour utiliser la connexion restaurée : charger l’état ne change pas les pages déjà ouvertes.

Avec `AsyncStealthySession`, utilisez `await` :

```python
from scrapling.fetchers import AsyncStealthySession

async def restore_session():
    async with AsyncStealthySession() as session:
        await session.load_state('state.json')
        page = await session.fetch('https://example.com')
        await session.save_state('state.json')
        return page
```

Ces méthodes enregistrent et restaurent seulement le contexte partagé du navigateur. Elles ne touchent pas les contextes temporaires de proxy par requête. Les sessions avec `proxy_rotator` n’ont pas de contexte partagé : ces méthodes lèvent donc `RuntimeError`. Un `proxy` fixe pour la session fonctionne normalement.

Le fichier ne contient ni `sessionStorage`, ni les onglets ouverts, ni les réglages du navigateur. L’enregistrement remplace le fichier existant et exige que son dossier parent existe. Les erreurs de fichier ou de JSON sont transmises au code appelant.

### Avantages des sessions {#session-benefits}

- **Navigateur réutilisé** : les requêtes suivantes sont bien plus rapides grâce au même navigateur.
- **Cookies persistants** : gestion automatique des cookies et de l’état, comme dans tout navigateur.
- **Empreinte stable** : la même empreinte de navigateur pour toutes les requêtes.
- **Moins de mémoire utilisée** : consomme moins de ressources que le lancement d’un navigateur pour chaque page.


## Exemples {#examples}
Les exemples permettent de mieux comprendre. En voici quelques-uns.

### Contrôle des ressources {#resource-control}

```python

page = StealthyFetcher.fetch('https://example.com', disable_resources=True)
```

### Shadow DOM {#shadow-dom}

Certaines pages placent du contenu dans des racines de Shadow DOM ouvertes. Ce contenu n’apparaît pas dans le HTML normal de la page. Activez `pierce_shadow` pour l’inclure dans la réponse, puis utilisez CSS ou XPath comme d’habitude :

```python
from scrapling.fetchers import StealthyFetcher

page = StealthyFetcher.fetch('https://example.com', pierce_shadow=True)
titles = page.css('product-card .title::text').getall()
```

La valeur par défaut est `False`. Vous pouvez aussi l’activer pour une session et la désactiver pour une requête précise :

```python
from scrapling.fetchers import StealthySession

with StealthySession(pierce_shadow=True) as session:
    page = session.fetch('https://example.com')
    plain_page = session.fetch('https://example.com', pierce_shadow=False)
```

La même option fonctionne avec `async_fetch` et les sessions asynchrones.

Seules les racines ouvertes sont incluses. Les racines fermées et les documents dans les iframes ne sont pas parcourus. Utilisez `wait_selector` si un composant se charge après la page.

Chaque racine ouverte devient un conteneur `<shadow-root>` dans la réponse. Les slots gardent leurs balises et attributs, et contiennent les nœuds qui leur sont attribués, ou leur contenu de repli si aucun nœud ne leur est attribué. Les enfants du DOM normal sans slot attribué sont omis. La page dans le navigateur ne change pas.

```html
<product-card>
  <shadow-root>
    <div class="title">Product name</div>
    <slot name="price"><span class="price">20</span></slot>
  </shadow-root>
</product-card>
```

Les sélecteurs de descendants traversent ces éléments. Les sélecteurs d’enfants directs doivent inclure les conteneurs et les slots :

```python
titles = page.css('product-card .title::text').getall()
titles = page.css('product-card > shadow-root > .title::text').getall()
prices = page.css('product-card > shadow-root > slot[name="price"] > .price::text').getall()
```

Les conteneurs et les slots apparaissent dans les chemins XPath, `.children`, `response.body` et les exports HTML. L’extraction en Markdown ou en texte renvoie leur contenu sans afficher les balises. Les attributs qui masquent les slots restent disponibles pour nettoyer le contenu.

La copie conserve l’ordre du contenu, mais ne calcule ni sa visibilité CSS ni sa disposition. Les sélecteurs contenant `<shadow-root>` s’appliquent à la réponse de Scrapling, pas à la page dans le navigateur. D’autres parsers HTML peuvent traiter différemment les imbrications inhabituelles.

### Bloquer des domaines {#domain-blocking}

```python

page = StealthyFetcher.fetch('https://example.com', blocked_domains={"ads.example.com", "tracker.net"})
```

### Contrôle du réseau {#network-control}

```python

page = StealthyFetcher.fetch('https://example.com', network_idle=True)


page = StealthyFetcher.fetch('https://example.com', timeout=30000)


page = StealthyFetcher.fetch('https://example.com', proxy='http://username:password@host:port')
```

### Télécharger des fichiers {#downloading-files}

```python
page = StealthyFetcher.fetch('https://raw.githubusercontent.com/D4Vinci/Scrapling/main/docs/assets/main_cover.png')

with open(file='main_cover.png', mode='wb') as f:
    f.write(page.body)
```

L’attribut `body` de `Response` renvoie toujours des `bytes`.

### Configuration avant la navigation {#pre-navigation-setup}
Pour enregistrer des événements, des routes ou des scripts avant de charger la page, utilisez `page_setup`. Cette fonction reçoit `page` et s’exécute avant l’appel à `page.goto()`.

```python
from patchright.sync_api import Page

def capture_websockets(page: Page):
    page.on("websocket", lambda ws: print(f"WebSocket opened: {ws.url}"))

page = StealthyFetcher.fetch('https://example.com', page_setup=capture_websockets)
```
Version asynchrone :
```python
from patchright.async_api import Page

async def capture_websockets(page: Page):
    page.on("websocket", lambda ws: print(f"WebSocket opened: {ws.url}"))

page = await StealthyFetcher.async_fetch('https://example.com', page_setup=capture_websockets)
```

Vous pouvez combiner cette option avec `page_action` : `page_setup` s’exécute avant la navigation, et `page_action` après.

### Cloudflare et options de discrétion {#cloudflare-and-stealth-options}

```python

page = StealthyFetcher.fetch('https://nopecha.com/demo/cloudflare', solve_cloudflare=True)


page = StealthyFetcher.fetch(
    'https://protected-site.com',
    solve_cloudflare=True,
    block_webrtc=True,
    real_chrome=True,
    hide_canvas=True,
    google_search=True,
    proxy='http://username:password@host:port',  # It can also be a dictionary with only the keys 'server', 'username', and 'password'.
)
```

`solve_cloudflare` active la détection et la résolution automatique de tous les types de défis Turnstile et Interstitial de Cloudflare :

- Défis JavaScript gérés.
- Défis interactifs, comme cliquer sur une case de vérification.
- Défis invisibles, avec vérification automatique en arrière-plan.

Il résout aussi les pages personnalisées avec un CAPTCHA intégré.

!!! notes "**Notes importantes**"

    1. Sur les sites ayant une implémentation particulière, vous devrez peut-être utiliser `wait_selector` pour attendre le vrai contenu après le CAPTCHA. Certains sites sont des cas très spécifiques, même si nous cherchons à fournir une solution générale.
    2. Prévoyez un timeout d’au moins 60 secondes pour laisser le temps de résoudre les défis Cloudflare.
    3. Cette fonction marche avec les proxies et les autres options de discrétion.

### Automatisation du navigateur {#browser-automation}
C’est ici que votre connaissance de l’[API Page de Playwright](https://playwright.dev/python/docs/api/class-page) intervient. La fonction fournie reçoit l’objet page de Playwright, exécute les actions, puis laisse le fetcher continuer.

Elle s’exécute juste après l’attente de `network_idle`, si activée, et avant celle de `wait_selector`. Vous pouvez l’utiliser pour automatiser des actions ou modifier la page.

Cet exemple utilise les [événements de souris](https://playwright.dev/python/docs/api/class-mouse) pour faire défiler la page avec la molette, puis déplacer la souris.
```python
from patchright.sync_api import Page

def scroll_page(page: Page):
    page.mouse.wheel(10, 0)
    page.mouse.move(100, 400)
    page.mouse.up()

page = StealthyFetcher.fetch('https://example.com', page_action=scroll_page)
```
Si vous utilisez la récupération asynchrone, la fonction doit aussi être asynchrone.
```python
from patchright.async_api import Page

async def scroll_page(page: Page):
   await page.mouse.wheel(10, 0)
   await page.mouse.move(100, 400)
   await page.mouse.up()

page = await StealthyFetcher.async_fetch('https://example.com', page_action=scroll_page)
```

### Conditions d’attente {#wait-conditions}

```python

page = StealthyFetcher.fetch(
    'https://quotes.toscrape.com/js-delayed/',
    wait_selector='.quote',
    wait_selector_state='visible'
)
```
Si activée, cette condition est la dernière attente avant de renvoyer la réponse. Passez un sélecteur CSS à `wait_selector` et un état à `wait_selector_state`. Par défaut, l’état attendu est `attached`, qui signifie que l’élément est présent dans le DOM.

Ensuite, si `load_dom` est activé, comme par défaut, le fetcher attend de nouveau l’état `domcontentloaded` pour vérifier le chargement et l’exécution de JavaScript. Si vous avez activé `network_idle`, il attend aussi de nouveau `network_idle`.

Voici les états disponibles ([source](https://playwright.dev/python/docs/api/class-page#page-wait-for-selector)) :

- `attached` : attend que l’élément soit présent dans le DOM.
- `detached` : attend que l’élément ne soit plus présent dans le DOM.
- `visible` : attend que l’élément ait une zone de taille non nulle et n’utilise pas `visibility:hidden`. Un élément sans contenu ou avec `display:none` a une zone vide et n’est pas considéré comme visible.
- `hidden` : attend que l’élément soit retiré du DOM, ait une zone vide ou utilise `visibility:hidden`. C’est l’inverse de `'visible'`.

### Historique réseau {#network-history}

Activez `record_requests` dans une session de navigateur pour consulter les requêtes terminées au fil des chargements, actions et onglets. L’historique couvre les contextes de la session, y compris les contextes temporaires de proxy, et enregistre les réponses sous forme d’objets `Response` de Scrapling. Recherchez les appels d’API, les erreurs HTTP et les redirections sans renvoyer de requêtes. Vous pouvez lire leurs en-têtes et leur contenu même après la fermeture de la session. Les requêtes échouées ou inachevées sont omises. Les réponses HTTP 4xx et 5xx terminées sont incluses.

```python
from scrapling.fetchers import StealthySession

with StealthySession(record_requests=True, max_recorded_requests=1000) as session:
    session.fetch('https://example.com', network_idle=True)

for response in session.network.search(resource_type='document', limit=None):
    print(response.meta['network_id'], response.url, response.status)
    if note := response.meta.get('body_note'):
        print(note)
    else:
        print(response.body)
        print(response.css('title::text').get())

session.network.clear()
```

La même API fonctionne avec `AsyncStealthySession`. L’enregistrement est désactivé par défaut. À la création de la session, définissez `record_requests=True` et, si nécessaire, `max_recorded_requests`.

- `session.network.search(url_pattern=None, method=None, resource_type=None, status=None, after_id=0, limit=100, include_static=True)` renvoie les objets `Response` enregistrés dans l’ordre de leur ID réseau. Avec `limit=None`, renvoie toutes les correspondances conservées. `url_pattern` est une expression régulière appliquée à la recherche ; une expression invalide produit une erreur à ce moment-là. `after_id` sélectionne les réponses dont l’ID est supérieur. `include_static=False` inclut les requêtes XHR/fetch et les erreurs HTTP. Utilisez `True` pour tous les types de ressources et les redirections enregistrées.
- `session.network.get(request_id)` renvoie un `Response` enregistré, ou `None` s’il n’est plus conservé.
- `session.network.clear()` efface l’historique. Les ID continuent d’augmenter et ne sont jamais réutilisés.

Chaque `Response` enregistré fournit directement `.url`, `.method`, `.status`, `.headers`, `.request_headers`, `.body` en octets, `.json()` et les méthodes CSS/XPath. Son `.meta` contient `network_id`, `resource_type` et `request_body`, qui vaut des octets ou `None`. Les en-têtes peuvent être partiels si leur lecture complète échoue. Ces lectures sont locales, même dans les sessions asynchrones : n’utilisez pas await et n’appelez pas `.body()`. Si le contenu ne peut pas être analysé, ses octets sont conservés, mais CSS et XPath utilisent un document vide.

Pour rechercher le trafic d’API par URL, utilisez `session.network.search(url_pattern=r'https://api\.example\.com/.*', limit=None)`. Ajoutez `resource_type='fetch'` ou `resource_type='xhr'` si vous voulez un seul type de requête.

Seul le contenu des réponses ayant un `Content-Type` textuel pris en charge est enregistré : `text/*`, types `+json`/`+xml`, y compris SVG, JSON, XML, JavaScript, GraphQL et données de formulaire encodées comme URL. Les types binaires, inconnus ou sans `Content-Type` gardent leurs métadonnées, mais pas les octets du contenu. Le navigateur charge toujours les ressources normalement.

Les octets enregistrés viennent de Playwright et peuvent différer des octets originaux du serveur. S’ils forment du UTF-8 valide, le texte est décodé en UTF-8, comme dans Playwright. Sinon, l’encodage déclaré est utilisé. Les en-têtes restent inchangés.

Si le contenu est omis, trop volumineux ou illisible, il renvoie `b''` et indique la raison dans `response.meta.get('body_note')`. Pour un contenu non textuel, la note est `Non-text body; not saved.`. Les métadonnées et les en-têtes disponibles sont conservés. Le texte enregistré, même vide, n’a pas de note. Les réponses HEAD et les statuts 204, 205 et 304 restent vides, sans note.

Les méthodes `search`, `get` et `clear` sont locales et synchrones, même dans les sessions asynchrones. Une entrée apparaît seulement après la conversion et l’enregistrement de sa réponse. Les événements du navigateur sont traités pendant que Playwright est actif. Les captures asynchrones nécessitent aussi une boucle d’événements en cours d’exécution. Lire l’historique n’attend pas les captures en cours.

La fermeture d’une session n’attend pas non plus les captures. Celles qui sont encore en cours lors d’une navigation ou de la fermeture du contexte peuvent être omises. Les réponses déjà enregistrées restent lisibles après la fermeture.

Par défaut, l’historique conserve jusqu’à 1 000 requêtes. Chaque corps de réponse est limité à 1 MiB, avec une limite totale de 20 MiB. Les anciennes entrées sont supprimées quand une limite est atteinte. Les limites de contenu sont fixes, pas des réglages de session. Elles couvrent les entrées conservées et les octets des réponses, pas la mémoire totale du navigateur, les captures simultanées, les lectures temporaires complètes, le HTML analysé ou les corps de requête.

#### Migrer vers la v5 {#migrating-in-v5}

`capture_xhr` et `response.captured_xhr` ont été supprimés en v5. Utilisez une session de navigateur explicite avec `record_requests=True`, puis consultez `session.network.search(url_pattern=..., limit=None)`. Cela remplace aussi la capture d’API avec les fetchers à appel unique : conservez donc l’objet de session. Les filtres s’appliquent à l’historique enregistré de toute la session, pas à la capture ni à une seule récupération de page. Seuls les corps de réponse textuels pris en charge sont enregistrés. `search()` renvoie au plus 100 correspondances par défaut. `limit=None` renvoie toutes les correspondances conservées sans changer les limites de l’historique.

### En-têtes et paramètres régionaux du navigateur {#browser-headers-and-locale}

```python
page = StealthyFetcher.fetch(
    'https://example.com',
    google_search=True,
    useragent='Mozilla/5.0...',
    locale='en-US',
)
```

### Exemple général {#general-example}
```python
from scrapling.fetchers import StealthyFetcher

def scrape_dynamic_content():

    page = StealthyFetcher.fetch(
        'https://example.com/dynamic',
        network_idle=True,
        wait_selector='.content'
    )


    content = page.css('.content')

    return {
        'title': content.css('h1::text').get(),
        'items': [
            item.text for item in content.css('.item')
        ]
    }
```

### Rotation des proxies {#proxy-rotation}

```python
from scrapling.fetchers import StealthySession, ProxyRotator


rotator = ProxyRotator([
    "http://proxy1:8080",
    "http://proxy2:8080",
    "http://proxy3:8080",
])


with StealthySession(proxy_rotator=rotator, headless=True) as session:
    page1 = session.fetch('https://example1.com')
    page2 = session.fetch('https://example2.com')


    page3 = session.fetch('https://example3.com', proxy='http://specific-proxy:8080')
```

!!! warning "Attention"

    Par défaut, les fetchers de navigateur et leurs sessions utilisent un contexte persistant avec un ensemble d’onglets. Les navigateurs ne permettent pas de définir un proxy par onglet. Avec `ProxyRotator`, le fetcher ouvre donc un contexte distinct pour chaque proxy, avec un onglet par contexte. Quand le travail de cet onglet est terminé, l’onglet et son contexte sont fermés.

## Quand l’utiliser {#when-to-use}

Utilisez StealthyFetcher si vous :

- Devez contourner des protections contre les bots.
- Avez besoin d’une empreinte de navigateur fiable.
- Avez besoin d’une prise en charge complète de JavaScript.
- Voulez des fonctions automatiques pour éviter la détection.
- Devez automatiser un navigateur.
- Travaillez avec des sites protégés par Cloudflare.
