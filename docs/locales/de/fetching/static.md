---
title: "HTTP-Scraping mit Python, Fetcher und FetcherSession"
description: "Senden Sie synchrone oder asynchrone HTTP-Anfragen mit Browser-Imitation, Cookies, Proxys und wiederverwendbaren Sitzungen. Lesen Sie mit Scrapling Daten aus der Antwort aus."
---

# HTTP-Anfragen {#http-requests}

Die Klasse `Fetcher` sendet schnelle HTTP-Anfragen mit geringem Ressourcenbedarf. Sie nutzt die leistungsfähige Bibliothek `curl_cffi` und bietet viele Funktionen gegen Bot-Erkennung.

!!! success "Voraussetzungen"

    1. Sie haben die Seite [Grundlagen der Fetcher](../fetching/choosing.md) gelesen. Sie wissen, was ein [Response-Objekt](../fetching/choosing.md#response-object) ist und welchen Fetcher Sie verwenden möchten.
    2. Sie haben die Seite [Elemente auswählen](../parsing/selection.md) gelesen und wissen, wie Sie Elemente in einem [Selector](../parsing/main_classes.md#selector)/[Response](../fetching/choosing.md#response-object)-Objekt finden und extrahieren.
    3. Sie haben die Seite [Hauptklassen](../parsing/main_classes.md) gelesen und kennen die Eigenschaften und Methoden, die [Response](../fetching/choosing.md#response-object) von [Selector](../parsing/main_classes.md#selector) erbt.

## Grundlegende Verwendung {#basic-usage}
Sie importieren diesen Fetcher auf dieselbe Weise wie alle anderen Fetcher:

```python
from scrapling.fetchers import Fetcher
```
Wie Sie die Parser-Optionen einstellen, erfahren Sie [hier](choosing.md#parser-configuration-in-all-fetchers).

### Gemeinsame Argumente {#shared-arguments}
Alle Methoden zum Senden von Anfragen teilen einige Argumente. Diese erklären wir zuerst.

- **url**: Die Ziel-URL.
- **stealthy_headers**: Erzeugt und ergänzt echte Browser-Header, einschließlich eines Google-Referer-Headers. Standardmäßig aktiviert.
- **follow_redirects**: Steuert Weiterleitungen. **Der Standardwert `"safe"`** folgt Weiterleitungen, lehnt aber Ziele mit internen oder privaten IP-Adressen ab. Das schützt vor SSRF. Mit `True` folgen Sie allen Weiterleitungen ohne Einschränkung. Mit `False` deaktivieren Sie sie vollständig.
- **timeout**: Maximale Wartezeit in Sekunden für den Abschluss jeder Anfrage. **Standardwert: 30 Sekunden**.
- **retries**: Maximale Anzahl der Versuche für fehlgeschlagene Anfragen, einschließlich des ersten Versuchs. **Standardwert: 3**.
- **retry_delay**: Wartezeit in Sekunden zwischen erneuten Versuchen. **Standardwert: 1 Sekunde**.
- **impersonate**: Imitiert den TLS-Fingerprint bestimmter Browser. Nimmt einen Browsernamen oder eine Liste an, etwa `"chrome110"`, `"firefox102"`, `"safari15_5"` für bestimmte Versionen. Mit `"chrome"`, `"firefox"`, `"safari"` oder `"edge"` wird die neueste verfügbare Version genutzt. So sehen die Anfragen auf TLS-Ebene aus wie die eines echten Browsers. Bei einer Liste wird für jede Anfrage zufällig ein Eintrag gewählt. **Standardwert: die neueste verfügbare Chrome-Version.**
- **http3**: Verwendet HTTP/3 für die Anfragen. **Standardwert: False**. Zusammen mit `impersonate` kann dies Probleme verursachen.
- **cookies**: Cookies für die Anfrage. Möglich sind ein Dictionary mit `name→value` oder eine Liste von Dictionarys.
- **proxy**: Leitet den gesamten HTTP- und HTTPS-Verkehr dieser Anfrage über einen Proxy. Das Format ist `http://username:password@localhost:8030`.
- **proxy_auth**: HTTP-Basic-Authentifizierung für den Proxy als Tupel (username, password).
- **proxies**: Dictionary mit den zu verwendenden Proxys. Format: `{"http": proxy_url, "https": proxy_url}`.
- **proxy_rotator**: Eine `ProxyRotator`-Instanz für den automatischen Proxy-Wechsel. Kann nicht mit `proxy` oder `proxies` kombiniert werden.
- **headers**: Header für die Anfrage. Sie können alle durch `stealthy_headers` erzeugten Header überschreiben.
- **max_redirects**: Maximale Anzahl der Weiterleitungen. **Standardwert: 30**. Mit -1 gibt es keine Begrenzung.
- **verify**: Legt fest, ob HTTPS-Zertifikate geprüft werden. **Standardwert: True**.
- **cert**: Tupel (cert, key) mit den Dateinamen des Client-Zertifikats und seines Schlüssels.
- **selector_config**: Dictionary mit eigenen Parser-Argumenten zum Erstellen des endgültigen `Selector`/`Response`-Objekts.

!!! note "Hinweise:"

    1. Derzeit können diese Browser imitiert werden: (`"edge"`, `"chrome"`, `"chrome_android"`, `"safari"`, `"safari_beta"`, `"safari_ios"`, `"safari_ios_beta"`, `"firefox"`, `"tor"`)<br/>
    2. Die verfügbaren Browser und Versionen erscheinen automatisch in der Autovervollständigung des Arguments. Sie werden mit jedem Update von `curl_cffi` aktualisiert.<br/>
    3. Wenn `impersonate` oder `stealthy_headers` aktiviert ist, erzeugen die Fetcher automatisch echte Browser-Header passend zur verwendeten Browserversion.

Für weitere Anpassungen können Sie jeder Methode außerdem die von `curl_cffi` unterstützten Argumente übergeben, die sie nicht bereits selbst anbietet.

### Zeichenkodierung {#text-encoding}

Wenn der Text einer Seite ohne UTF-8-Kodierung falsch dargestellt wird, übergeben Sie `default_encoding="shift_jis"` oder die tatsächliche Kodierung der Seite. Diese wird verwendet, wenn der Header `Content-Type` keinen Zeichensatz nennt. Ein vom Server angegebener Zeichensatz wird damit nicht überschrieben.

Wenn der Server einen falschen Zeichensatz angibt, erzwingen Sie die richtige Kodierung mit `selector_config={"encoding": "shift_jis"}`.

### HTTP-Methoden {#http-methods}
Je nach Methode gibt es weitere Argumente, etwa `params` für GET-Anfragen und `data`/`json` für POST-, PUT- und DELETE-Anfragen.

Die Beispiele zeigen es am besten:

> Hinweis: Die Methoden `OPTIONS` und `HEAD` werden nicht unterstützt.
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
Für asynchrone Anfragen ist nur eine kleine Änderung nötig:
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
Das Objekt `page` ist dabei immer ein [Response](choosing.md#response-object)-Objekt und damit auch ein [Selector](../parsing/main_classes.md#selector). Sie können es also direkt verwenden:
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
Für asynchrone Anfragen ist nur eine kleine Änderung nötig:
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
Für asynchrone Anfragen ist nur eine kleine Änderung nötig:
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
Für asynchrone Anfragen ist nur eine kleine Änderung nötig:
```python
from scrapling.fetchers import AsyncFetcher
page = await AsyncFetcher.delete('https://example.com/resource/123')
page = await AsyncFetcher.delete('https://example.com/resource/123', stealthy_headers=True, impersonate="chrome")
page = await AsyncFetcher.delete('https://example.com/resource/123', proxy='http://username:password@localhost:8030')
```

## Sitzungen verwalten {#session-management}

Für mehrere Anfragen mit derselben Konfiguration verwenden Sie `FetcherSession`. Die Klasse funktioniert in synchronem und asynchronem Code. Sie erkennt die benötigte Sitzungsart automatisch, ohne dass Sie eine andere Klasse importieren müssen.

`FetcherSession` nimmt fast alle Argumente der Anfragemethoden an. So legen Sie die Konfiguration für die gesamte Sitzung fest und können einzelne Anfragen bei Bedarf anders konfigurieren, wie die folgenden Beispiele zeigen.

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

Mit `ProxyRotator` und `FetcherSession` wechseln Sie den Proxy automatisch zwischen Anfragen:

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

Für eine einzelne Anfrage können Sie den Sitzungs-Proxy oder den Rotator mit `proxy=` direkt in der Anfragemethode überschreiben:

```python
with FetcherSession(proxy='http://default-proxy:8080') as session:
    # Uses the session proxy
    page1 = session.get('https://example.com/page1')

    # Override the proxy for this specific request
    page2 = session.get('https://example.com/page2', proxy='http://special-proxy:9090')
```

Ein asynchrones Beispiel:

```python
async with FetcherSession(impersonate='firefox', http3=True) as session:
    # All standard HTTP methods available
    response = await session.get('https://example.com')
    response = await session.post('https://scrapling.requestcatcher.com/post', json={'data': 'value'})
    response = await session.put('https://scrapling.requestcatcher.com/put', data={'update': 'info'})
    response = await session.delete('https://scrapling.requestcatcher.com/delete')
```
Oder besser:
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

Die Klasse `Fetcher` nutzt `FetcherSession`, um für jede Anfrage eine vorübergehende Sitzung zu erstellen.

### Vorteile von Sitzungen {#session-benefits}

- **Deutlich schneller**: Zehnmal schneller, als für jede Anfrage eine eigene Sitzung zu erstellen.
- **Cookies behalten**: Automatische Cookie-Verwaltung über mehrere Anfragen hinweg.
- **Ressourcen sparen**: Weniger Speicher- und CPU-Bedarf bei mehreren Anfragen.
- **Zentrale Konfiguration**: Alle Anfrageeinstellungen an einer Stelle verwalten.

## Beispiele {#examples}
Einige ausführliche Beispiele für den Einstieg in Web Scraping.

### Einfache HTTP-Anfrage {#basic-http-request}

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

### Produkte auslesen {#product-scraping}

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

### Dateien herunterladen {#downloading-files}

```python
from scrapling.fetchers import Fetcher

page = Fetcher.get('https://raw.githubusercontent.com/D4Vinci/Scrapling/main/docs/assets/main_cover.png')
with open(file='main_cover.png', mode='wb') as f:
   f.write(page.body)
```

### Mehrere Ergebnisseiten durchlaufen {#pagination-handling}

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

### Formulare absenden {#form-submission}

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

### Tabellen auslesen {#table-extraction}

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

### Navigationsmenü {#navigation-menu}

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

## Wann eignet sich dieser Fetcher? {#when-to-use}

Verwenden Sie `Fetcher`, wenn Sie:

- schnelle HTTP-Anfragen brauchen.
- den zusätzlichen Ressourcenbedarf klein halten möchten.
- kein JavaScript ausführen müssen, weil sich die Website über HTTP-Anfragen auslesen lässt.
- einige Funktionen gegen Bot-Erkennung brauchen, etwa für Websites mit Schutzmaßnahmen ohne JavaScript-Prüfungen.

Verwenden Sie `FetcherSession`, wenn Sie:

- mehrere Anfragen an dieselbe oder verschiedene Websites senden.
- Cookies und Anmeldedaten zwischen Anfragen behalten müssen.
- Verbindungen wiederverwenden möchten, um die Leistung zu verbessern.
- dieselbe Konfiguration für mehrere Anfragen brauchen.
- mit APIs arbeiten, die einen Sitzungszustand benötigen.

Verwenden Sie andere Fetcher, wenn Sie:

- einen Browser automatisieren müssen.
- erweiterte Funktionen gegen Bot-Erkennung brauchen.
- JavaScript ausführen oder mit dynamischen Inhalten interagieren müssen.
