---
title: "Tester l’extraction de données dans le shell interactif de Scrapling"
description: "Récupérez des pages, testez des sélecteurs et vérifiez les résultats dans un shell IPython. Convertissez des commandes curl, réutilisez les réponses récentes et testez votre code."
---

# Guide du shell interactif de Scrapling {#scrapling-interactive-shell-guide}

<script src="https://asciinema.org/a/736339.js" id="asciicast-736339" async data-autoplay="1" data-loop="1" data-cols="225" data-rows="40" data-start-at="00:06" data-speed="1.5" data-theme="tango"></script>

**Un environnement REPL d’extraction de données web pour les développeurs et les spécialistes des données**

Le shell interactif de Scrapling est un environnement basé sur IPython, conçu pour extraire des données web. Il donne accès à toutes les fonctions de Scrapling, à des raccourcis pratiques, à la gestion automatique des pages et à des outils comme la conversion de commandes curl.

!!! success "Avant de commencer"

    1. Lisez la page sur les [bases des fetchers](../fetching/choosing.md) pour comprendre l’[objet Response](../fetching/choosing.md#response-object) et choisir un fetcher.
    2. Lisez la page sur la [sélection d’éléments](../parsing/selection.md) pour apprendre à trouver et extraire des éléments d’un objet [Selector](../parsing/main_classes.md#selector)/[Response](../fetching/choosing.md#response-object).
    3. Lisez la page des [classes principales](../parsing/main_classes.md) pour connaître les propriétés et méthodes héritées par [Response](../fetching/choosing.md#response-object) de [Selector](../parsing/main_classes.md#selector).
    4. Lisez au moins une page de la section des fetchers pour les requêtes que vous utiliserez ici : [requêtes HTTP](../fetching/static.md) ou [récupération avec un navigateur](../fetching/stealthy.md).

## Pourquoi utiliser le shell interactif ? {#why-use-the-interactive-shell}

Le shell interactif permet d’explorer et de tester tout de suite, sans modifier puis exécuter un script à chaque essai. Il est utile pour :

- **Créer rapidement des prototypes** : Testez vos méthodes d’extraction sur le moment.
- **Explorer les données** : Parcourez des sites et extrayez leurs données de façon interactive.
- **Apprendre Scrapling** : Essayez ses fonctions en temps réel.
- **Déboguer des scrapers** : Suivez les requêtes et vérifiez leurs résultats étape par étape.
- **Convertir des commandes** : Transformez une commande curl des DevTools du navigateur en requête Fetcher avec une ligne.

## Premiers pas {#getting-started}

### Lancer le shell {#launch-the-shell}

```bash
# Start the interactive shell
scrapling shell

# Execute code and exit (useful for scripting)
scrapling shell -c "get('https://quotes.toscrape.com'); print(len(page.css('.quote')))"

# Set logging level
scrapling shell --loglevel info
```

Au lancement, vous verrez la bannière de Scrapling et pourrez commencer à extraire des données, comme dans la vidéo ci-dessus :

```python
# No imports needed - everything is ready!
get('https://news.ycombinator.com')

# Explore the page structure
page.css('a')[:5]  # Look at first 5 links

# Refine your selectors
stories = page.css('.titleline>a')
len(stories)  # 30

# Extract specific data
for story in stories[:3]:
    title = story.text
    url = story['href']
    print(f"{title}: {url}")

# Try different approaches
titles = page.css('.titleline>a::text')  # Direct text extraction
urls = page.css('.titleline>a::attr(href)')  # Direct attribute extraction
```

## Raccourcis intégrés {#built-in-shortcuts}

Le shell propose des raccourcis pour éviter le code répétitif :

- **`get(url, **kwargs)`** - Requête HTTP GET (au lieu de `Fetcher.get`).
- **`post(url, **kwargs)`** - Requête HTTP POST (au lieu de `Fetcher.post`).
- **`put(url, **kwargs)`** - Requête HTTP PUT (au lieu de `Fetcher.put`).
- **`delete(url, **kwargs)`** - Requête HTTP DELETE (au lieu de `Fetcher.delete`).
- **`fetch(url, **kwargs)`** - Récupération avec le navigateur Stealthy (au lieu de `StealthyFetcher.fetch`).

Les classes les plus courantes sont disponibles sans importation, notamment `Fetcher`, `AsyncFetcher`, `StealthyFetcher` et `Selector`.

### Gestion automatique des pages {#smart-page-management}

Le shell suit vos requêtes et vos pages :

- **Accès à la page actuelle**

    `page` et `response` sont mis à jour automatiquement avec la dernière page récupérée :

    ```python
    get('https://quotes.toscrape.com')
    # 'page' and 'response' both refer to the last fetched page
    page.url  # 'https://quotes.toscrape.com'
    response.status  # Prints 200; Same as page.status
    ```

- **Historique des pages**

    `pages` conserve les cinq dernières pages dans un objet `Selectors` :

    ```python
    get('https://site1.com')
    get('https://site2.com')
    get('https://site3.com')
    
    # Access last 5 pages
    len(pages)  # `Selectors` object with `page` history -> 3
    pages[0].url  # First page in history -> 'https://site1.com'
    pages[-1].url  # Most recent page -> 'https://site3.com'
    
    # Work with historical pages
    for i, old_page in enumerate(pages):
        print(f"Page {i}: {old_page.url} - {old_page.status}")
    ```

## Autres commandes utiles {#additional-helpful-commands}

### Afficher la page {#page-visualization}

Ouvrez les pages récupérées dans votre navigateur :

```python
get('https://quotes.toscrape.com')
view(page)  # Opens the page HTML in your default browser
```

### Intégration des commandes curl {#curl-command-integration}

Le shell fournit les fonctions `uncurl` et `curl2fetcher` pour convertir les commandes curl des DevTools du navigateur en requêtes `Fetcher`.

Commencez par copier une requête sous forme de commande curl :

<img src="../assets/scrapling_shell_curl.png" title="Copier une requête de Chrome sous forme de commande curl" alt="Copier une requête de Chrome sous forme de commande curl" style="width: 70%;"/>

- **Convertir une commande curl en objet de requête**

    ```python
    curl_cmd = '''curl 'https://scrapling.requestcatcher.com/post' \
      -X POST \
      -H 'Content-Type: application/json' \
      -d '{"name": "test", "value": 123}' '''
    
    request = uncurl(curl_cmd)
    request.method  # -> 'post'
    request.url  # -> 'https://scrapling.requestcatcher.com/post'
    request.headers  # -> {'Content-Type': 'application/json'}
    ```

- **Exécuter directement une commande curl**

    ```python
    # Convert and execute in one step
    curl2fetcher(curl_cmd)
    page.status  # -> 200
    ```

### Fonctions d’IPython {#ipython-features}

Le shell hérite de toutes les fonctions d’IPython :

```python
# Magic commands
%time page = get('https://example.com')  # Time execution
%history  # Show command history
%save filename.py 1-10  # Save commands 1-10 to file

# Tab completion works everywhere
page.c<TAB>  # Shows: css, cookies, headers, etc.
Fetcher.<TAB>  # Shows all Fetcher methods

# Object inspection
get? # Show get documentation
```

## Exemples {#examples}

Voici quelques exemples générés avec l’IA :

#### Collecter des données de boutiques en ligne {#e-commerce-data-collection}

```python
# Start with product listing page
catalog = get('https://shop.example.com/products')

# Find product links
product_links = catalog.css('.product-link::attr(href)').getall()
print(f"Found {len(product_links)} products")

# Sample a few products first
for link in product_links[:3]:
    product = get(catalog.urljoin(link))
    name = product.css('.product-name::text').get('')
    price = product.css('.price::text').get('')
    print(f"{name}: {price}")

# Scale up with sessions for efficiency
from scrapling.fetchers import FetcherSession
with FetcherSession() as session:
    products = []
    for link in product_links:
        product = session.get(catalog.urljoin(link))
        products.append({
            'name': product.css('.product-name::text').get(''),
            'price': product.css('.price::text').get(''),
            'url': link
        })
```

#### Intégrer et tester des API {#api-integration-and-testing}

```python
>>> # Test API endpoints interactively
>>> response = get('https://jsonplaceholder.typicode.com/posts/1')
>>> response.json()
{'userId': 1, 'id': 1, 'title': 'sunt aut...', 'body': 'quia et...'}

>>> # Test POST requests
>>> new_post = post('https://jsonplaceholder.typicode.com/posts', 
...                 json={'title': 'Test Post', 'body': 'Test content', 'userId': 1})
>>> new_post.json()['id']
101

>>> # Test with different data
>>> updated = put('https://jsonplaceholder.typicode.com/posts/1',
...               json={'title': 'Updated Title'})
```

## Obtenir de l’aide {#getting-help}

Si vous avez besoin d’aide au-delà de celle proposée dans le terminal, consultez :

- [Documentation de Scrapling](https://scrapling.readthedocs.io/fr/latest/)
- [Communauté Discord](https://discord.gg/EMgGbDceNQ)
- [Tickets GitHub](https://github.com/D4Vinci/Scrapling/issues)

Voilà ! Bonne extraction. Avec le shell, extraire des données web devient aussi simple qu’une conversation.
