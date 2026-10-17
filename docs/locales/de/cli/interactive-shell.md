---
title: "Web Scraping in der interaktiven Shell von Scrapling testen"
description: "Rufen Sie Seiten ab, testen Sie Selektoren und prüfen Sie Ergebnisse in einer IPython-Shell. Wandeln Sie curl-Befehle um, verwenden Sie frühere Antworten erneut und testen Sie Scraping-Code."
---

# Anleitung zur interaktiven Shell von Scrapling {#scrapling-interactive-shell-guide}

<script src="https://asciinema.org/a/736339.js" id="asciicast-736339" async data-autoplay="1" data-loop="1" data-cols="225" data-rows="40" data-start-at="00:06" data-speed="1.5" data-theme="tango"></script>

**Eine Web-Scraping-REPL für Entwickler und Data Scientists**

Die interaktive Shell von Scrapling ist eine Umgebung auf Basis von IPython, die für Web Scraping entwickelt wurde. Sie bietet direkten Zugriff auf alle Scrapling-Funktionen, praktische Kurzbefehle, automatische Seitenverwaltung und Werkzeuge wie die Umwandlung von curl-Befehlen.

!!! success "Voraussetzungen"

    1. Lesen Sie die [Grundlagen der Fetcher](../fetching/choosing.md), um das [Response-Objekt](../fetching/choosing.md#response-object) zu verstehen und einen Fetcher auszuwählen.
    2. Lesen Sie die Seite zur [Elementauswahl](../parsing/selection.md), um Elemente in einem [Selector](../parsing/main_classes.md#selector)/[Response](../fetching/choosing.md#response-object) zu finden und zu extrahieren.
    3. Lesen Sie die Seite über die [Hauptklassen](../parsing/main_classes.md), um zu erfahren, welche Eigenschaften und Methoden [Response](../fetching/choosing.md#response-object) von [Selector](../parsing/main_classes.md#selector) erbt.
    4. Lesen Sie mindestens eine Seite im Fetcher-Abschnitt zu den Anfragen, die Sie hier verwenden werden: [HTTP-Anfragen](../fetching/static.md) oder [Seiten mit einem Browser abrufen](../fetching/stealthy.md).

## Warum die interaktive Shell verwenden? {#why-use-the-interactive-shell}

In der interaktiven Shell können Sie sofort ausprobieren und prüfen. Sie müssen nicht für jeden Versuch ein Skript ändern und neu ausführen. Das ist hilfreich für:

- **Schnelle Prototypen**: Testen Sie Ihre Scraping-Ansätze direkt.
- **Daten untersuchen**: Durchsuchen Sie Websites interaktiv und extrahieren Sie Daten.
- **Scrapling lernen**: Probieren Sie Funktionen in Echtzeit aus.
- **Scraper debuggen**: Gehen Sie Anfragen schrittweise durch und prüfen Sie die Ergebnisse.
- **Befehle umwandeln**: Wandeln Sie einen curl-Befehl aus den Browser-DevTools mit einer Zeile in eine Fetcher-Anfrage um.

## Erste Schritte {#getting-started}

### Shell starten {#launch-the-shell}

```bash
# Start the interactive shell
scrapling shell

# Execute code and exit (useful for scripting)
scrapling shell -c "get('https://quotes.toscrape.com'); print(len(page.css('.quote')))"

# Set logging level
scrapling shell --loglevel info
```

Nach dem Start sehen Sie das Scrapling-Banner und können sofort mit dem Scraping beginnen, wie im Video oben:

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

## Eingebaute Kurzbefehle {#built-in-shortcuts}

Die Shell bietet Kurzbefehle, mit denen Sie wiederholten Code vermeiden:

- **`get(url, **kwargs)`** - HTTP-GET-Anfrage (statt `Fetcher.get`).
- **`post(url, **kwargs)`** - HTTP-POST-Anfrage (statt `Fetcher.post`).
- **`put(url, **kwargs)`** - HTTP-PUT-Anfrage (statt `Fetcher.put`).
- **`delete(url, **kwargs)`** - HTTP-DELETE-Anfrage (statt `Fetcher.delete`).
- **`fetch(url, **kwargs)`** - Abruf mit dem Stealthy-Browser (statt `StealthyFetcher.fetch`).

Die häufigsten Klassen sind ohne Import verfügbar, darunter `Fetcher`, `AsyncFetcher`, `StealthyFetcher` und `Selector`.

### Automatische Seitenverwaltung {#smart-page-management}

Die Shell behält Ihre Anfragen und Seiten im Blick:

- **Zugriff auf die aktuelle Seite**

    `page` und `response` werden automatisch mit der zuletzt abgerufenen Seite aktualisiert:

    ```python
    get('https://quotes.toscrape.com')
    # 'page' and 'response' both refer to the last fetched page
    page.url  # 'https://quotes.toscrape.com'
    response.status  # Prints 200; Same as page.status
    ```

- **Seitenverlauf**

    `pages` enthält die letzten fünf Seiten in einem `Selectors`-Objekt:

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

## Weitere nützliche Befehle {#additional-helpful-commands}

### Seite anzeigen {#page-visualization}

Öffnen Sie abgerufene Seiten in Ihrem Browser:

```python
get('https://quotes.toscrape.com')
view(page)  # Opens the page HTML in your default browser
```

### curl-Befehle einbinden {#curl-command-integration}

Die Shell bietet die Funktionen `uncurl` und `curl2fetcher`. Damit wandeln Sie curl-Befehle aus den Browser-DevTools in `Fetcher`-Anfragen um.

Kopieren Sie zunächst eine Anfrage als curl-Befehl:

<img src="../assets/scrapling_shell_curl.png" title="Eine Anfrage aus Chrome als curl-Befehl kopieren" alt="Eine Anfrage aus Chrome als curl-Befehl kopieren" style="width: 70%;"/>

- **curl-Befehl in ein Anfrageobjekt umwandeln**

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

- **curl-Befehl direkt ausführen**

    ```python
    # Convert and execute in one step
    curl2fetcher(curl_cmd)
    page.status  # -> 200
    ```

### IPython-Funktionen {#ipython-features}

Die Shell erbt alle Funktionen von IPython:

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

## Beispiele {#examples}

Hier sind einige mit KI erstellte Beispiele:

#### Daten von Online-Shops sammeln {#e-commerce-data-collection}

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

#### APIs einbinden und testen {#api-integration-and-testing}

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

## Hilfe erhalten {#getting-help}

Wenn Sie neben der Hilfe im Terminal weitere Unterstützung brauchen, finden Sie sie hier:

- [Scrapling-Dokumentation](https://scrapling.readthedocs.io/de/latest/)
- [Discord-Community](https://discord.gg/EMgGbDceNQ)
- [GitHub-Issues](https://github.com/D4Vinci/Scrapling/issues)

Das war’s! Viel Erfolg beim Scraping. Mit der Shell wird Web Scraping so einfach wie ein Gespräch.
