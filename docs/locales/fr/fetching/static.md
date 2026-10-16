---
title: "Web scraping HTTP en Python avec Fetcher et FetcherSession"
description: "Envoyez des requêtes HTTP synchrones ou asynchrones avec imitation de navigateur, cookies, proxies et sessions réutilisables. Extrayez les données des réponses avec Scrapling."
---

# Requêtes HTTP {#http-requests}

`Fetcher` envoie des requêtes HTTP rapides et légères grâce à `curl_cffi`, une bibliothèque performante qui propose de nombreuses options pour éviter la détection.

!!! success "Avant de commencer"

    1. Lisez [Les bases des fetchers](../fetching/choosing.md) pour comprendre l’[objet Response](../fetching/choosing.md#response-object) et choisir un fetcher.
    2. Lisez [Rechercher des éléments](../parsing/selection.md) pour savoir comment trouver et extraire des éléments de [Selector](../parsing/main_classes.md#selector)/[Response](../fetching/choosing.md#response-object).
    3. Lisez [Classes principales](../parsing/main_classes.md) pour connaître les propriétés et méthodes de [Selector](../parsing/main_classes.md#selector) dont hérite [Response](../fetching/choosing.md#response-object).

## Utilisation de base {#basic-usage}
La principale façon d’importer ce fetcher est la même que pour les autres :

```python
from scrapling.fetchers import Fetcher
```
Consultez la configuration du parser [ici](choosing.md#parser-configuration-in-all-fetchers).

### Arguments communs {#shared-arguments}
Toutes les méthodes de requête partagent ces arguments :

- **url** : URL cible.
- **stealthy_headers** : génère et ajoute des en-têtes de navigateur réel, dont un referer Google. Activé par défaut.
- **follow_redirects** : contrôle les redirections. **La valeur par défaut est `"safe"`** : suit les redirections, mais refuse celles vers des IP internes ou privées pour protéger contre le SSRF. Utilisez `True` pour les suivre sans restriction, ou `False` pour les désactiver.
- **timeout** : délai maximal en secondes pour terminer chaque requête. **30 secondes par défaut**.
- **retries** : nombre maximal de tentatives lorsqu’une requête échoue, première tentative comprise. **3 par défaut**.
- **retry_delay** : secondes d’attente entre les tentatives. **1 seconde par défaut**.
- **impersonate** : imite l’empreinte TLS d’un navigateur. Accepte une chaîne ou une liste, comme `"chrome110"`, `"firefox102"` ou `"safari15_5"` pour des versions précises. Utilisez `"chrome"`, `"firefox"`, `"safari"` ou `"edge"` pour la dernière version disponible. Les requêtes semblent ainsi venir d’un vrai navigateur au niveau TLS. Avec une liste, une option est choisie au hasard pour chaque requête. **Par défaut, utilise la dernière version de Chrome disponible.**
- **http3** : utilise HTTP/3. **False par défaut**. Peut poser problème avec `impersonate`.
- **cookies** : cookies de la requête. Accepte un dictionnaire `name→value` ou une liste de dictionnaires.
- **proxy** : proxy utilisé pour acheminer tout le trafic HTTP et HTTPS de cette requête. Le format est `http://username:password@localhost:8030`.
- **proxy_auth** : authentification HTTP Basic du proxy, sous forme de tuple (nom d’utilisateur, mot de passe).
- **proxies** : dictionnaire de proxies au format `{"http": proxy_url, "https": proxy_url}`.
- **proxy_rotator** : objet `ProxyRotator` pour changer automatiquement de proxy. Ne peut pas être combiné avec `proxy` ou `proxies`.
- **headers** : en-têtes de la requête. Ils peuvent remplacer ceux générés par `stealthy_headers`.
- **max_redirects** : nombre maximal de redirections. **30 par défaut**. Utilisez -1 pour ne pas limiter.
- **verify** : indique si les certificats HTTPS doivent être vérifiés. **True par défaut**.
- **cert** : tuple des noms de fichiers (certificat, clé) pour le certificat client.
- **selector_config** : dictionnaire de réglages du parser pour créer l’objet `Selector`/`Response` final.

!!! note "Notes"

    1. Les navigateurs disponibles pour l’imitation sont (`"edge"`, `"chrome"`, `"chrome_android"`, `"safari"`, `"safari_beta"`, `"safari_ios"`, `"safari_ios_beta"`, `"firefox"`, `"tor"`).<br/>
    2. Les navigateurs et leurs versions apparaissent dans l’autocomplétion de l’argument et sont actualisés à chaque mise à jour de `curl_cffi`.<br/>
    3. Si `impersonate` ou `stealthy_headers` est activé, les fetchers génèrent des en-têtes réels correspondant à la version du navigateur utilisée.

Pour d’autres réglages, vous pouvez passer à chaque méthode les arguments acceptés par `curl_cffi` qu’elle ne gère pas déjà.

### Encodage du texte {#text-encoding}

Si une page qui n’utilise pas UTF-8 affiche des caractères incorrects, passez `default_encoding="shift_jis"`, ou l’encodage réel de la page, avec la requête. Il sera utilisé si l’en-tête `Content-Type` ne précise pas d’encodage. Il ne remplace pas l’encodage fourni par le serveur.

Si le serveur indique un mauvais encodage, vous pouvez imposer le bon avec `selector_config={"encoding": "shift_jis"}`.

### Méthodes HTTP {#http-methods}
Chaque méthode a ses propres arguments, comme `params` pour GET et `data`/`json` pour POST, PUT et DELETE.

Voici quelques exemples :

> Les méthodes `OPTIONS` et `HEAD` ne sont pas disponibles.
#### GET {#get}
```python
from scrapling.fetchers import Fetcher
# Basic GET
page = Fetcher.get('https://example.com')
page = Fetcher.get('https://scrapling.requestcatcher.com/get', stealthy_headers=True)
page = Fetcher.get('https://scrapling.requestcatcher.com/get', proxy='http://username:password@localhost:8030')
# With parameters
page = Fetcher.get('https://example.com/search', params={'q': 'query'})

# With headers
page = Fetcher.get('https://example.com', headers={'User-Agent': 'Custom/1.0'})
# Basic HTTP authentication
page = Fetcher.get("https://example.com", auth=("my_user", "password123"))
# Browser impersonation
page = Fetcher.get('https://example.com', impersonate='chrome')
# HTTP/3 support
page = Fetcher.get('https://example.com', http3=True)
```
Pour les requêtes asynchrones, un petit ajustement suffit :
```python
from scrapling.fetchers import AsyncFetcher
# Basic GET
page = await AsyncFetcher.get('https://example.com')
page = await AsyncFetcher.get('https://scrapling.requestcatcher.com/get', stealthy_headers=True)
page = await AsyncFetcher.get('https://scrapling.requestcatcher.com/get', proxy='http://username:password@localhost:8030')
# With parameters
page = await AsyncFetcher.get('https://example.com/search', params={'q': 'query'})
# With headers
page = await AsyncFetcher.get('https://example.com', headers={'User-Agent': 'Custom/1.0'})
# Basic HTTP authentication
page = await AsyncFetcher.get("https://example.com", auth=("my_user", "password123"))
# Browser impersonation
page = await AsyncFetcher.get('https://example.com', impersonate='chrome110')
# HTTP/3 support
page = await AsyncFetcher.get('https://example.com', http3=True)
```
Dans tous les cas, `page` est un [Response](choosing.md#response-object), qui est aussi un [Selector](../parsing/main_classes.md#selector). Vous pouvez l’utiliser directement :
```python
page.css('.something.something')

page = Fetcher.get('https://api.github.com/events')
>>> page.json()
[{'id': '<redacted>',
  'type': 'PushEvent',
  'actor': {'id': '<redacted>',
   'login': '<redacted>',
   'display_login': '<redacted>',
   'gravatar_id': '',
   'url': 'https://api.github.com/users/<redacted>',
   'avatar_url': 'https://avatars.githubusercontent.com/u/<redacted>'},
  'repo': {'id': '<redacted>',
...
```
#### POST {#post}
```python
from scrapling.fetchers import Fetcher
# Basic POST
page = Fetcher.post('https://scrapling.requestcatcher.com/post', data={'key': 'value'}, params={'q': 'query'})
page = Fetcher.post('https://scrapling.requestcatcher.com/post', data={'key': 'value'}, stealthy_headers=True)
page = Fetcher.post('https://scrapling.requestcatcher.com/post', data={'key': 'value'}, proxy='http://username:password@localhost:8030', impersonate="chrome")
# Another example of form-encoded data
page = Fetcher.post('https://example.com/submit', data={'username': 'user', 'password': 'pass'}, http3=True)
# JSON data
page = Fetcher.post('https://example.com/api', json={'key': 'value'})
```
Pour les requêtes asynchrones, un petit ajustement suffit :
```python
from scrapling.fetchers import AsyncFetcher
# Basic POST
page = await AsyncFetcher.post('https://scrapling.requestcatcher.com/post', data={'key': 'value'})
page = await AsyncFetcher.post('https://scrapling.requestcatcher.com/post', data={'key': 'value'}, stealthy_headers=True)
page = await AsyncFetcher.post('https://scrapling.requestcatcher.com/post', data={'key': 'value'}, proxy='http://username:password@localhost:8030', impersonate="chrome")
# Another example of form-encoded data
page = await AsyncFetcher.post('https://example.com/submit', data={'username': 'user', 'password': 'pass'}, http3=True)
# JSON data
page = await AsyncFetcher.post('https://example.com/api', json={'key': 'value'})
```
#### PUT {#put}
```python
from scrapling.fetchers import Fetcher
# Basic PUT
page = Fetcher.put('https://example.com/update', data={'status': 'updated'})
page = Fetcher.put('https://example.com/update', data={'status': 'updated'}, stealthy_headers=True, impersonate="chrome")
page = Fetcher.put('https://example.com/update', data={'status': 'updated'}, proxy='http://username:password@localhost:8030')
# Another example of form-encoded data
page = Fetcher.put("https://scrapling.requestcatcher.com/put", data={'key': ['value1', 'value2']})
```
Pour les requêtes asynchrones, un petit ajustement suffit :
```python
from scrapling.fetchers import AsyncFetcher
# Basic PUT
page = await AsyncFetcher.put('https://example.com/update', data={'status': 'updated'})
page = await AsyncFetcher.put('https://example.com/update', data={'status': 'updated'}, stealthy_headers=True, impersonate="chrome")
page = await AsyncFetcher.put('https://example.com/update', data={'status': 'updated'}, proxy='http://username:password@localhost:8030')
# Another example of form-encoded data
page = await AsyncFetcher.put("https://scrapling.requestcatcher.com/put", data={'key': ['value1', 'value2']})
```

#### DELETE {#delete}
```python
from scrapling.fetchers import Fetcher
page = Fetcher.delete('https://example.com/resource/123')
page = Fetcher.delete('https://example.com/resource/123', stealthy_headers=True, impersonate="chrome")
page = Fetcher.delete('https://example.com/resource/123', proxy='http://username:password@localhost:8030')
```
Pour les requêtes asynchrones, un petit ajustement suffit :
```python
from scrapling.fetchers import AsyncFetcher
page = await AsyncFetcher.delete('https://example.com/resource/123')
page = await AsyncFetcher.delete('https://example.com/resource/123', stealthy_headers=True, impersonate="chrome")
page = await AsyncFetcher.delete('https://example.com/resource/123', proxy='http://username:password@localhost:8030')
```

## Gestion des sessions {#session-management}

Utilisez `FetcherSession` pour envoyer plusieurs requêtes avec la même configuration. Elle fonctionne en code synchrone et asynchrone : elle détecte le mode utilisé et adapte la session sans nécessiter une autre importation.

`FetcherSession` accepte presque tous les arguments des méthodes de requête. Vous pouvez définir des réglages pour toute la session, puis les modifier pour une requête précise, comme dans les exemples suivants.

```python
from scrapling.fetchers import FetcherSession

# Create a session with default configuration
with FetcherSession(
    impersonate='chrome',
    http3=True,
    stealthy_headers=True,
    timeout=30,
    retries=3
) as session:
    # Make multiple requests with the same settings and the same cookies
    page1 = session.get('https://scrapling.requestcatcher.com/get')
    page2 = session.post('https://scrapling.requestcatcher.com/post', data={'key': 'value'})
    page3 = session.get('https://api.github.com/events')

    # All requests share the same session and connection pool
```

Vous pouvez aussi utiliser `ProxyRotator` avec `FetcherSession` pour changer automatiquement de proxy entre les requêtes :

```python
from scrapling.fetchers import FetcherSession, ProxyRotator

rotator = ProxyRotator([
    'http://proxy1:8080',
    'http://proxy2:8080',
    'http://proxy3:8080',
])

with FetcherSession(proxy_rotator=rotator, impersonate='chrome') as session:
    # Each request automatically uses the next proxy in rotation
    page1 = session.get('https://example.com/page1')
    page2 = session.get('https://example.com/page2')

    # You can check which proxy was used via the response metadata
    print(page1.meta['proxy'])
```

Pour une requête précise, remplacez le proxy ou le rotateur de la session en passant `proxy=` à la méthode :

```python
with FetcherSession(proxy='http://default-proxy:8080') as session:
    # Uses the session proxy
    page1 = session.get('https://example.com/page1')

    # Override the proxy for this specific request
    page2 = session.get('https://example.com/page2', proxy='http://special-proxy:9090')
```

Un exemple asynchrone :

```python
async with FetcherSession(impersonate='firefox', http3=True) as session:
    # All standard HTTP methods available
    response = await session.get('https://example.com')
    response = await session.post('https://scrapling.requestcatcher.com/post', json={'data': 'value'})
    response = await session.put('https://scrapling.requestcatcher.com/put', data={'update': 'info'})
    response = await session.delete('https://scrapling.requestcatcher.com/delete')
```
Ou, mieux encore :
```python
import asyncio
from scrapling.fetchers import FetcherSession

# Async session usage
async with FetcherSession(impersonate="safari") as session:
    urls = ['https://example.com/page1', 'https://example.com/page2']

    tasks = [
        session.get(url) for url in urls
    ]

    pages = await asyncio.gather(*tasks)
```

`Fetcher` utilise `FetcherSession` pour créer une session temporaire à chaque requête.

### Avantages des sessions {#session-benefits}

- **Plus rapides** : 10 fois plus rapides que la création d’une session par requête.
- **Cookies persistants** : gestion automatique des cookies entre les requêtes.
- **Moins de ressources** : meilleure utilisation de la mémoire et du processeur pour plusieurs requêtes.
- **Configuration centralisée** : un seul endroit pour gérer les réglages.

## Exemples {#examples}
Des exemples complets pour débuter en web scraping.

### Requête HTTP simple {#basic-http-request}

```python
from scrapling.fetchers import Fetcher

# Make a request
page = Fetcher.get('https://example.com')

# Check the status
if page.status == 200:
    # Extract title
    title = page.css('title::text').get()
    print(f"Page title: {title}")

    # Extract all links
    links = page.css('a::attr(href)').getall()
    print(f"Found {len(links)} links")
```

### Extraire des produits {#product-scraping}

```python
from scrapling.fetchers import Fetcher

def scrape_products():
    page = Fetcher.get('https://example.com/products')
    
    # Find all product elements
    products = page.css('.product')
    
    results = []
    for product in products:
        results.append({
            'title': product.css('.title::text').get(),
            'price': product.css('.price::text').re_first(r'\d+\.\d{2}'),
            'description': product.css('.description::text').get(),
            'in_stock': product.has_class('in-stock')
        })
    
    return results
```

### Télécharger des fichiers {#downloading-files}

```python
from scrapling.fetchers import Fetcher

page = Fetcher.get('https://raw.githubusercontent.com/D4Vinci/Scrapling/main/docs/assets/main_cover.png')
with open(file='main_cover.png', mode='wb') as f:
   f.write(page.body)
```

### Parcourir les pages de résultats {#pagination-handling}

```python
from scrapling.fetchers import Fetcher

def scrape_all_pages():
    base_url = 'https://example.com/products?page={}'
    page_num = 1
    all_products = []
    
    while True:
        # Get current page
        page = Fetcher.get(base_url.format(page_num))
        
        # Find products
        products = page.css('.product')
        if not products:
            break
            
        # Process products
        for product in products:
            all_products.append({
                'name': product.css('.name::text').get(),
                'price': product.css('.price::text').get()
            })
            
        # Next page
        page_num += 1
        
    return all_products
```

### Envoyer des formulaires {#form-submission}

```python
from scrapling.fetchers import Fetcher

# Submit login form
response = Fetcher.post(
    'https://example.com/login',
    data={
        'username': 'user@example.com',
        'password': 'password123'
    }
)

# Check login success
if response.status == 200:
    # Extract user info
    user_name = response.css('.user-name::text').get()
    print(f"Logged in as: {user_name}")
```

### Extraire des tableaux {#table-extraction}

```python
from scrapling.fetchers import Fetcher

def extract_table():
    page = Fetcher.get('https://example.com/data')
    
    # Find table
    table = page.css('table')[0]
    
    # Extract headers
    headers = [
        th.text for th in table.css('thead th')
    ]
    
    # Extract rows
    rows = []
    for row in table.css('tbody tr'):
        cells = [td.text for td in row.css('td')]
        rows.append(dict(zip(headers, cells)))
        
    return rows
```

### Menu de navigation {#navigation-menu}

```python
from scrapling.fetchers import Fetcher

def extract_menu():
    page = Fetcher.get('https://example.com')
    
    # Find navigation
    nav = page.css('nav')[0]
    
    menu = {}
    for item in nav.css('li'):
        links = item.css('a')
        if links:
            link = links[0]
            menu[link.text] = {
                'url': link['href'],
                'has_submenu': bool(item.css('.submenu'))
            }
            
    return menu
```

## Quand utiliser chaque option {#when-to-use}

Utilisez `Fetcher` si vous :

- Avez besoin de requêtes HTTP rapides.
- Voulez limiter l’utilisation des ressources.
- N’avez pas besoin d’exécuter JavaScript, car les données sont accessibles par requêtes HTTP.
- Avez besoin d’éviter certaines détections, par exemple si le site est protégé mais n’utilise pas de défis JavaScript.

Utilisez `FetcherSession` si vous :

- Envoyez plusieurs requêtes au même site ou à des sites différents.
- Devez conserver des cookies ou une authentification entre les requêtes.
- Voulez réutiliser les connexions pour améliorer les performances.
- Devez garder les mêmes réglages entre les requêtes.
- Travaillez avec des API qui nécessitent un état de session.

Utilisez d’autres fetchers si vous :

- Devez automatiser un navigateur.
- Avez besoin d’options avancées pour éviter la détection de bots.
- Devez exécuter JavaScript ou interagir avec du contenu dynamique.
