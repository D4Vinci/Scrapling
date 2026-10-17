---
title: "Spider-Anfragen, Callbacks und Response.follow"
description: "Erstellen Sie Crawl-Anfragen, übergeben Sie Metadaten und folgen Sie Links mit response.follow. Lernen Sie Callbacks, Prioritäten und die Erkennung doppelter Anfragen kennen."
---

# Anfragen und Antworten {#requests-responses}

!!! success "Voraussetzungen"

    1. Sie haben die Seite [Erste Schritte](getting-started.md) gelesen und wissen, wie Sie einen einfachen Spider erstellen und starten.

Diese Seite erklärt das Objekt `Request` im Detail: Anfragen erstellen, Daten zwischen Callbacks übergeben, Prioritäten und doppelte Anfragen steuern sowie Links mit `response.follow()` folgen.

## Das Request-Objekt {#the-request-object}

Ein `Request` steht für eine abzurufende URL. Sie erstellen Anfragen entweder direkt oder mit `response.follow()`:

```python
from scrapling.spiders import Request

# Direct construction
request = Request(
    "https://example.com/page",
    callback=self.parse_page,
    priority=5,
)

# Via response.follow (preferred in callbacks)
request = response.follow("/page", callback=self.parse_page)
```

Sie können folgende Argumente an `Request` übergeben:

| Argument      | Typ        | Standard   | Beschreibung                                                                                           |
|---------------|------------|------------|--------------------------------------------------------------------------------------------------------|
| `url`         | `str`      | *erforderlich* | Die abzurufende URL                                                                                |
| `sid`         | `str`      | `""`       | Sitzungs-ID, die die Anfrage an eine bestimmte Sitzung leitet (siehe [Sitzungen](sessions.md))          |
| `callback`    | `callable` | `None`     | Asynchrone Generatormethode zum Verarbeiten der Antwort. Standardmäßig `parse()`                         |
| `priority`    | `int`      | `0`        | Höhere Werte werden zuerst verarbeitet                                                                 |
| `dont_filter` | `bool`     | `False`    | Wenn `True`, werden doppelte Anfragen zugelassen                                                        |
| `meta`        | `dict`     | `{}`       | Beliebige Metadaten, die an die Antwort weitergegeben werden                                             |
| `**kwargs`    |            |            | Weitere Schlüsselwortargumente für die Abrufmethode der Sitzung, etwa `headers`, `method` und `data`    |

Alle zusätzlichen Schlüsselwortargumente werden direkt an die verwendete Sitzung weitergegeben. So erstellen Sie zum Beispiel eine POST-Anfrage:

```python
yield Request(
    "https://example.com/api",
    method="POST",
    data={"key": "value"},
    callback=self.parse_result,
)
```

## Response.follow() {#responsefollow}

Mit `response.follow()` erstellen Sie Folgeanfragen innerhalb von Callbacks. Das ist der empfohlene Weg und bietet gegenüber dem direkten Erstellen von `Request`-Objekten mehrere Vorteile:

- **Relative URLs** werden automatisch anhand der URL der aktuellen Seite aufgelöst.
- **Der Referer-Header** wird standardmäßig auf die URL der aktuellen Seite gesetzt.
- **Sitzungsargumente** der ursprünglichen Anfrage werden übernommen, etwa Header und Proxy-Einstellungen. Ausgenommen sind `method`, `params`, `data`, `json`, `files` und `multipart`. Links werden daher mit einfachen GET-Anfragen abgerufen.
- **Callback, Sitzungs-ID und Priorität** werden von der ursprünglichen Anfrage übernommen, wenn Sie keine neuen Werte angeben.

```python
async def parse(self, response: Response):
    # Minimal - inherits callback, sid, priority from current request
    yield response.follow("/next-page")

    # Override specific fields
    yield response.follow(
        "/product/123",
        callback=self.parse_product,
        priority=10,
    )

    # Pass additional metadata to
    yield response.follow(
        "/details",
        callback=self.parse_details,
        meta={"category": "electronics"},
    )
```

| Argument           | Typ        | Standard   | Beschreibung                                                |
|--------------------|------------|------------|-------------------------------------------------------------|
| `url`              | `str`      | *erforderlich* | Zu verfolgende URL, absolut oder relativ                  |
| `sid`              | `str`      | `""`       | Sitzungs-ID. Bei leerem Wert aus der ursprünglichen Anfrage übernommen |
| `callback`         | `callable` | `None`     | Callback-Methode. Bei `None` aus der ursprünglichen Anfrage übernommen |
| `priority`         | `int`      | `None`     | Priorität. Bei `None` aus der ursprünglichen Anfrage übernommen |
| `dont_filter`      | `bool`     | `False`    | Doppelte Anfragen zulassen                                  |
| `meta`             | `dict`     | `None`     | Metadaten, die mit denen der Antwort zusammengeführt werden  |
| **`referer_flow`** | `bool`     | `True`     | Aktuelle URL als Referer-Header setzen                       |
| `**kwargs`         |            |            | Werden mit den Sitzungsargumenten der ursprünglichen Anfrage zusammengeführt |

### Referer-Weitergabe ausschalten {#disabling-referer-flow}

Standardmäßig setzt `response.follow()` den Header `Referer` auf die URL der aktuellen Seite. So schalten Sie das aus:

```python
yield response.follow("/page", referer_flow=False)
```

## Callbacks {#callbacks}

Callbacks sind asynchrone Generatormethoden Ihres Spiders, die Antworten verarbeiten. Sie müssen mit `yield` einen dieser drei Typen liefern:

- **`dict`** - Ein extrahierter Datensatz, der zu den Ergebnissen hinzugefügt wird.
- **`Request`** - Eine Folgeanfrage, die in die Warteschlange kommt.
- **`None`** - Wird ohne Meldung ignoriert.

```python
class MySpider(Spider):
    name = "my_spider"
    start_urls = ["https://example.com"]

    async def parse(self, response: Response):
        # Yield items (dicts)
        yield {"url": response.url, "title": response.css("title::text").get("")}

        # Yield follow-up requests
        for link in response.css("a::attr(href)").getall():
            yield response.follow(link, callback=self.parse_page)

    async def parse_page(self, response: Response):
        yield {"content": response.css("article::text").get("")}
```

!!! tip "Hinweis:"

    Alle Callback-Methoden müssen mit `async def` definiert sein und `yield` statt `return` verwenden. Auch wenn ein Callback nur Datensätze und keine Folgeanfragen liefert, muss er ein asynchroner Generator sein.

## Priorität von Anfragen {#request-priority}

Anfragen mit höheren Prioritätswerten werden zuerst verarbeitet. Das ist nützlich, wenn Sie bestimmte Seiten vor anderen verarbeiten müssen:

```python
async def parse(self, response: Response):
    # High priority - process product pages first
    for link in response.css("a.product::attr(href)").getall():
        yield response.follow(link, callback=self.parse_product, priority=10)

    # Low priority - pagination links processed after products
    next_page = response.css("a.next::attr(href)").get()
    if next_page:
        yield response.follow(next_page, callback=self.parse, priority=0)
```

Bei `response.follow()` wird die Priorität der ursprünglichen Anfrage übernommen, sofern Sie keinen neuen Wert angeben.

## Doppelte Anfragen vermeiden {#deduplication}

Der Spider erkennt doppelte Anfragen automatisch anhand eines Fingerprints aus URL, HTTP-Methode, Anfrage-Body und Sitzungs-ID. Erzeugen zwei Anfragen denselben Fingerprint, wird die zweite ohne Meldung verworfen.

Mit `dont_filter=True` erlauben Sie doppelte Anfragen, etwa um eine Seite nach der Anmeldung erneut aufzurufen:

```python
yield Request("https://example.com/dashboard", dont_filter=True, callback=self.parse_dashboard)

# Or with response.follow
yield response.follow("/dashboard", dont_filter=True, callback=self.parse_dashboard)
```

Mit Klassenattributen Ihres Spiders steuern Sie genauer, was in den Fingerprint einfließt:

| Attribut             | Standard | Wirkung                                                                                                         |
|----------------------|----------|-----------------------------------------------------------------------------------------------------------------|
| `fp_include_kwargs`  | `False`  | Zusätzliche Anfrageargumente aufnehmen, die Sie an die Abrufmethode der Sitzung übergeben haben, etwa Header    |
| `fp_keep_fragments`  | `False`  | URL-Fragmente (`#section`) bei der Berechnung des Fingerprints beibehalten                                       |
| `fp_include_headers` | `False`  | Anfrage-Header in den Fingerprint aufnehmen                                                                      |

So behandeln Sie zum Beispiel `https://example.com/page#section1` und `https://example.com/page#section2` als unterschiedliche URLs:

```python
class MySpider(Spider):
    name = "my_spider"
    fp_keep_fragments = True
    # ...
```

## Metadaten von Anfragen {#request-meta}

Über das Dictionary `meta` übergeben Sie beliebige Daten zwischen Callbacks. Das ist nützlich, wenn Sie Angaben von einer Seite brauchen, um eine andere zu verarbeiten:

```python
async def parse(self, response: Response):
    for product in response.css("div.product"):
        category = product.css("span.category::text").get("")
        link = product.css("a::attr(href)").get()
        if link:
            yield response.follow(
                link,
                callback=self.parse_product,
                meta={"category": category},
            )

async def parse_product(self, response: Response):
    yield {
        "name": response.css("h1::text").get(""),
        "price": response.css(".price::text").get(""),
        # Access meta from the request
        "category": response.meta.get("category", ""),
    }
```

Bei `response.follow()` werden die Metadaten der aktuellen Antwort mit den neu übergebenen Metadaten zusammengeführt. Neue Werte haben Vorrang.

Das Spider-System speichert auch einige Metadaten automatisch. Wenn die Proxy-Rotation aktiv ist, steht zum Beispiel der für eine Anfrage verwendete Proxy in `response.meta["proxy"]`.
