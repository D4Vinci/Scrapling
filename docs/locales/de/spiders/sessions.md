---
title: "HTTP- und Browser-Sitzungen in einem Crawler verwenden"
description: "Richten Sie benannte Sitzungen ein und leiten Sie Spider-Anfragen über HTTP- oder Browser-Fetcher. Verwenden Sie Cookies erneut, starten Sie Sitzungen bei Bedarf und lesen Sie den API-Verlauf."
---

# Spider-Sitzungen {#spiders-sessions}

!!! success "Voraussetzungen"

    1. Sie haben die Seite [Erste Schritte](getting-started.md) gelesen und wissen, wie Sie einen einfachen Spider erstellen und starten.
    2. Sie kennen die [Fetcher-Grundlagen](../fetching/choosing.md) und die Unterschiede zwischen HTTP- und Stealthy-Sitzungen.

Ein Spider kann mehrere Fetcher-Sitzungen gleichzeitig verwenden. Zum Beispiel eine schnelle HTTP-Sitzung für einfache Seiten und einen Stealth-Browser für geschützte Seiten. Diese Seite zeigt, wie Sie Sitzungen einrichten und verwenden.

## Was sind Sitzungen? {#what-are-sessions}

Eine Sitzung ist eine vorkonfigurierte Fetcher-Instanz, die während des gesamten Crawls aktiv bleibt. Statt für jede Anfrage eine neue Verbindung oder einen neuen Browser zu erstellen, verwendet der Spider die Sitzungen erneut. Das ist schneller und braucht weniger Ressourcen.

Standardmäßig erstellt jeder Spider eine [FetcherSession](../fetching/static.md). Überschreiben Sie `configure_sessions()`, um weitere Sitzungen hinzuzufügen oder die Standardsitzung zu ersetzen. Sie dürfen dabei nur die asynchrone Variante der jeweiligen Sitzung verwenden, wie die Tabelle zeigt:


| Sitzungstyp                                     | Einsatzzweck                             |
|-------------------------------------------------|------------------------------------------|
| [FetcherSession](../fetching/static.md)          | Schnelle HTTP-Anfragen ohne JavaScript    |
| [AsyncStealthySession](../fetching/stealthy.md)   | JavaScript, Browser-Automatisierung, Umgehen von Bot-Schutz |


## Sitzungen konfigurieren {#configuring-sessions}

Überschreiben Sie `configure_sessions()` in Ihrem Spider, um Sitzungen einzurichten. Der Parameter `manager` ist eine Instanz von `SessionManager`. Registrieren Sie Sitzungen mit `manager.add()`:

```python
from scrapling.spiders import Spider, Response
from scrapling.fetchers import FetcherSession

class MySpider(Spider):
    name = "my_spider"
    start_urls = ["https://example.com"]

    def configure_sessions(self, manager):
        manager.add("default", FetcherSession())

    async def parse(self, response: Response):
        yield {"title": response.css("title::text").get("")}
```

Die Methode `manager.add()` nimmt diese Argumente an:

| Argument     | Typ       | Standard       | Beschreibung                                  |
|--------------|-----------|----------------|-----------------------------------------------|
| `session_id` | `str`     | *erforderlich* | Name, mit dem Anfragen diese Sitzung auswählen |
| `session`    | `Session` | *erforderlich* | Die Sitzungsinstanz                            |
| `default`    | `bool`    | `False`        | Diese Sitzung als Standardsitzung festlegen    |
| `lazy`       | `bool`    | `False`        | Sitzung erst bei der ersten Verwendung starten |

!!! note "Hinweise:"

    1. Wenn Sie in einer Anfrage keine Sitzung angeben, wird die Standardsitzung verwendet. Sie wird auf eine von zwei Arten festgelegt:
        1. Die erste hinzugefügte Sitzung wird automatisch zur Standardsitzung.
        2. Beim Hinzufügen einer Sitzung setzen Sie `default=True`.
    2. Sie müssen die übergebenen Sitzungsinstanzen nicht selbst starten. Der Spider prüft alle Sitzungen und startet die, die noch nicht laufen.
    3. Mit dem Argument `lazy` beim Hinzufügen startet eine Sitzung erst bei Bedarf. So startet zum Beispiel der Browser erst, wenn er gebraucht wird, und nicht gleich mit dem Spider.

## Spider mit mehreren Sitzungen {#multi-session-spider}

Ein praktisches Beispiel: Verwenden Sie eine schnelle HTTP-Sitzung für Übersichtsseiten und einen Stealth-Browser für Detailseiten mit Bot-Schutz:

```python
from scrapling.spiders import Spider, Response
from scrapling.fetchers import FetcherSession, AsyncStealthySession

class ProductSpider(Spider):
    name = "products"
    start_urls = ["https://shop.example.com/products"]

    def configure_sessions(self, manager):
        # Fast HTTP for listing pages (default)
        manager.add("http", FetcherSession())

        self.browser_session = AsyncStealthySession(
            headless=True,
            network_idle=True,
            record_requests=True,
        )
        manager.add("stealth", self.browser_session)

    async def parse(self, response: Response):
        for link in response.css("a.product::attr(href)").getall():
            # Route product pages through the stealth session
            yield response.follow(link, sid="stealth", callback=self.parse_product)

        next_page = response.css("a.next::attr(href)").get()
        if next_page:
            yield response.follow(next_page)

    async def parse_product(self, response: Response):
        yield {
            "name": response.css("h1::text").get(""),
            "price": response.css(".price::text").get(""),
        }

    async def on_close(self):
        for api_response in self.browser_session.network.search(
            url_pattern=r"https://api\.shop\.example\.com/.*", limit=None
        ):
            self.logger.info(f"Saved API response: {api_response.url} ({api_response.status})")
```

Das Beispiel behält die Browser-Instanz und liest den gespeicherten API-Verlauf einmal in `on_close()`, bevor die Sitzungen geschlossen werden. Der Verlauf enthält alle Produktseiten und bleibt auch nach dem Schließen lesbar. Noch laufende Aufzeichnungen werden nicht abgewartet. Die Speichergrenzen gelten weiterhin.

Entscheidend ist der Parameter `sid`. Er sagt dem Spider, welche Sitzung er für die jeweilige Anfrage verwenden soll. Wenn Sie `response.follow()` ohne `sid` aufrufen, wird die Sitzungs-ID der ursprünglichen Anfrage übernommen.

Sitzungen müssen nicht aus unterschiedlichen Klassen stammen. Sie können auch mehrere Instanzen derselben Klasse mit verschiedenen Einstellungen verwenden:

```python
from scrapling.spiders import Spider, Response
from scrapling.fetchers import FetcherSession

class ProductSpider(Spider):
    name = "products"
    start_urls = ["https://shop.example.com/products"]

    def configure_sessions(self, manager):
        chrome_requests = FetcherSession(impersonate="chrome")
        firefox_requests = FetcherSession(impersonate="firefox")

        manager.add("chrome", chrome_requests)
        manager.add("firefox", firefox_requests)

    async def parse(self, response: Response):
        for link in response.css("a.product::attr(href)").getall():
            yield response.follow(link, callback=self.parse_product)

        next_page = response.css("a.next::attr(href)").get()
        if next_page:
            yield response.follow(next_page, sid="firefox")

    async def parse_product(self, response: Response):
        yield {
            "name": response.css("h1::text").get(""),
            "price": response.css(".price::text").get(""),
        }
```

Sie können auch eine eigene Sitzung mit ihren Cookies und ihrem Zustand für bestimmte Anfragen behalten.

## Sitzungsargumente {#session-arguments}

Zusätzliche Schlüsselwortargumente an `Request` oder über `response.follow(**kwargs)` werden an die Abrufmethode der Sitzung weitergegeben. So passen Sie einzelne Anfragen an, ohne die Sitzungskonfiguration zu ändern:

```python
async def parse(self, response: Response):
    # Pass extra headers for this specific request
    yield Request(
        "https://api.example.com/data",
        headers={"Authorization": "Bearer token123"},
        callback=self.parse_api,
    )

    # Use a different HTTP method
    yield Request(
        "https://example.com/submit",
        method="POST",
        data={"field": "value"},
        sid="firefox",
        callback=self.parse_result,
    )
```

!!! warning

    Normalerweise wählen Sie bei `FetcherSession`, `Fetcher` oder `AsyncFetcher` die HTTP-Methode durch den Aufruf von `.get()` oder `.post()`. Bei `FetcherSession` innerhalb von Spidern geht das nicht. Standardmäßig wird eine _HTTP-GET_-Anfrage gesendet. Für eine andere HTTP-Methode müssen Sie das Argument `method` übergeben, wie im Beispiel oben. Dadurch bleibt die Schnittstelle von `Request` für alle Sitzungstypen gleich.

Mit der Sitzung `"stealth"` (`AsyncStealthySession`) aus dem Beispiel oben können Sie browserspezifische Argumente wie `wait_selector`, `page_action` oder `extra_headers` übergeben:

```python
async def parse(self, response: Response):
    # Use Cloudflare solver with the `AsyncStealthySession` we configured above
    yield Request(
        "https://nopecha.com/demo/cloudflare",
        sid="stealth",
        callback=self.parse_result,
        solve_cloudflare=True,
        block_webrtc=True,
        hide_canvas=True,
        google_search=True,
    )

    yield response.follow(
        "/dynamic-page",
        sid="stealth",
        callback=self.parse_dynamic,
        wait_selector="div.loaded",
        network_idle=True,
    )
```

!!! warning

    `response.follow()` übernimmt die Sitzungsargumente (**kwargs) der ursprünglichen Anfrage, außer `method`, `params`, `data`, `json`, `files` und `multipart`. Nach einer POST-Anfrage wird ein Link daher mit einem einfachen GET abgerufen. Neue Argumente haben Vorrang vor übernommenen Werten.

```python
from scrapling.spiders import Spider, Response
from scrapling.fetchers import FetcherSession

class ProductSpider(Spider):
    name = "products"
    start_urls = ["https://shop.example.com/products"]

    def configure_sessions(self, manager):
        manager.add("http", FetcherSession(impersonate='chrome'))

    async def parse(self, response: Response):
        # I don't want the follow request to impersonate a desktop Chrome like the previous request, but a mobile one
        # so I override it like this
        for link in response.css("a.product::attr(href)").getall():
            yield response.follow(link, impersonate="chrome131_android", callback=self.parse_product)

        next_page = response.css("a.next::attr(href)").get()
        if next_page:
            yield response.follow(next_page)

    async def parse_product(self, response: Response):
        yield {
            "name": response.css("h1::text").get(""),
            "price": response.css(".price::text").get(""),
        }
```
!!! info

    Beim Beenden des Spiders prüft der Manager automatisch, ob noch Sitzungen laufen, und schließt sie, bevor der Spider beendet wird.
