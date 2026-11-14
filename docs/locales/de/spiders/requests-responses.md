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

`response.follow()` erstellt ein neues `Request`-Objekt und löst relative URLs anhand der Antwort-URL auf. Sitzungs-ID, Callback und Priorität werden übernommen, sofern Sie keine neuen Werte angeben.

`sid=""`, `callback=None` und `priority=None` übernehmen die entsprechenden Werte der zugeordneten Anfrage. `priority=0` überschreibt die übernommene Priorität ausdrücklich. Metadaten sind standardmäßig leer. Header, Cookies, Zugangsdaten, Proxy-Einstellungen und Abrufoptionen der vorherigen Anfrage werden nicht kopiert, auch nicht für dieselbe Domain.

Die Einstellungen und der Cookie-Speicher der gewählten Sitzung gelten weiterhin. Wählen Sie mit `sid` eine andere Sitzung, wenn Sie deren Einstellungen nicht verwenden möchten.

Wenn Sie nach einem POST einem Link folgen, wird ein GET gesendet, sofern Sie keine andere `method` angeben.

```python
async def parse(self, response: Response):
    # Minimal - inherits callback, sid, priority from current request
    yield response.follow("/next-page")

    # Override specific fields
    yield response.follow(
        "/product/123",
        callback=self.parse_product,
        sid="stealth",
        priority=10,
    )

    # Pass additional metadata to
    yield response.follow(
        "/details",
        callback=self.parse_details,
        meta={"category": "electronics"},
    )
```

| Argument | Typ | Standard | Beschreibung |
| --- | --- | --- | --- |
| `url` | `str` | *erforderlich* | Absolute oder relative URL |
| `sid` | `str` | `""` | Bei leerem Wert die Sitzungs-ID der zugeordneten Anfrage |
| `callback` | `callable` | `None` | Bei `None` der Callback der zugeordneten Anfrage |
| `priority` | `int` oder `None` | `None` | Bei `None` die zugeordnete Priorität; `0` überschreibt sie ausdrücklich |
| `dont_filter` | `bool` | `False` | Doppelte Anfragen zulassen |
| `meta` | `dict` | `None` | Nur Metadaten dieser Anfrage, standardmäßig leer |
| `referer_flow` | `bool` | `True` | Aktuelle Antwort-URL als Referer setzen |
| `**kwargs` | |  | Ausdrücklich angegebene Optionen für die Sitzung |

### Referer-Weitergabe ausschalten {#disabling-referer-flow}

`referer_flow=True` bleibt der Standard. `follow()` setzt die aktuelle URL als Referer für HTTP und Browser sowie `google_search=False`. Header der vorherigen Anfrage werden nicht kopiert. So schalten Sie diese automatischen Werte aus:

```python
yield response.follow("/page", referer_flow=False)
```

Mit `referer_flow=False` fügt die Methode keinen Referer hinzu und ändert `google_search` nicht. Übergebene Header und Standardeinstellungen der Sitzung oder des Abrufmoduls gelten weiterhin. So setzen Sie einen anderen Referer für HTTP:

```python
yield response.follow(
    "/page",
    referer_flow=False,
    headers={"Referer": "https://example.com/"},
)
```

Für Browseranfragen verwenden Sie `extra_headers` und bei Bedarf `google_search=False`.

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

Ohne `priority` übernimmt `response.follow()` die Priorität der zugeordneten Anfrage. Mit `priority=0` setzen Sie die Priorität ausdrücklich auf null.

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

`response.follow()` verwendet nur die mit `meta` übergebenen Metadaten. Die Metadaten der vorherigen Antwort werden nicht damit zusammengeführt. Übergeben Sie die benötigten Schlüssel ausdrücklich.

Das Spider-System speichert auch einige Metadaten automatisch. Wenn die Proxy-Rotation aktiv ist, steht zum Beispiel der für eine Anfrage verwendete Proxy in `response.meta["proxy"]`.
