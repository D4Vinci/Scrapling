---
title: "Ihren ersten Python-Webcrawler mit Scrapling erstellen"
description: "Erstellen Sie einen Spider, der Daten extrahiert, Folgeseiten aufruft und Ergebnisse exportiert. Lernen Sie Start-URLs, Callbacks, Domain-Grenzen und robots.txt-Einstellungen kennen."
---

# Erste Schritte {#getting-started}

## Einführung {#introduction}

!!! success "Voraussetzungen"

    1. Sie haben die Seite [Fetcher-Grundlagen](../fetching/choosing.md) gelesen und wissen, welche Fetcher es gibt und wann Sie diese verwenden.
    2. Sie haben die Seite [Hauptklassen](../parsing/main_classes.md) gelesen und kennen die Klassen [Selector](../parsing/main_classes.md#selector) und [Response](../fetching/choosing.md#response-object).
    3. Sie haben die Seite [Architektur](architecture.md) gelesen und wissen im Überblick, wie das Spider-System arbeitet.

Mit dem Spider-System erstellen Sie in wenigen Codezeilen Crawler, die mehrere Seiten parallel abrufen. Wenn Sie Scrapy kennen, werden Ihnen die Abläufe vertraut sein. Falls nicht, erklärt diese Anleitung alles, was Sie für den Einstieg brauchen.

## Ihr erster Spider {#your-first-spider}

Ein Spider ist eine Klasse, die festlegt, wie Websites durchsucht und Daten daraus extrahiert werden. Hier ist ein möglichst einfacher Spider:

```python
from scrapling.spiders import Spider, Response

class QuotesSpider(Spider):
    name = "quotes"
    start_urls = ["https://quotes.toscrape.com"]

    async def parse(self, response: Response):
        for quote in response.css("div.quote"):
            yield {
                "text": quote.css("span.text::text").get(""),
                "author": quote.css("small.author::text").get(""),
            }
```

Jeder Spider braucht drei Dinge:

1. **`name`** - Eine eindeutige Kennung für den Spider.
2. **`start_urls`** - Eine Liste der URLs, bei denen der Crawl beginnt.
3. **`parse()`** - Eine asynchrone Generatormethode, die jede Antwort verarbeitet und Ergebnisse liefert.

In der Methode `parse()` findet die Verarbeitung statt. Sie verwenden dieselben Auswahlmethoden wie bei Scraplings [Selector](../parsing/main_classes.md#selector)/[Response](../fetching/choosing.md#response-object) und geben die extrahierten Datensätze mit `yield` als Dictionaries aus.

## Den Spider starten {#running-the-spider}

Erstellen Sie eine Instanz und rufen Sie `start()` auf, um Ihren Spider zu starten:

```python
result = QuotesSpider().start()
```

Die Methode `start()` übernimmt die asynchrone Ausführung intern. Sie müssen sich also nicht um Event-Loops kümmern. Während der Spider läuft, werden alle Vorgänge im Terminal protokolliert. Am Ende des Crawls erhalten Sie ausführliche Statistiken.

Diese Statistiken stehen im zurückgegebenen Objekt `CrawlResult`, das alle nötigen Ergebnisse enthält:

```python
result = QuotesSpider().start()

# Access scraped items
for item in result.items:
    print(item["text"], "-", item["author"])

# Check statistics
print(f"Scraped {result.stats.items_scraped} items")
print(f"Made {result.stats.requests_count} requests")
print(f"Took {result.stats.elapsed_seconds:.1f} seconds")

# Did the crawl finish or was it paused?
print(f"Completed: {result.completed}")
```

## Links folgen {#following-links}

Die meisten Crawls folgen Links über mehrere Seiten. Erstellen Sie mit `response.follow()` die Folgeanfragen:

```python
from scrapling.spiders import Spider, Response

class QuotesSpider(Spider):
    name = "quotes"
    start_urls = ["https://quotes.toscrape.com"]

    async def parse(self, response: Response):
        # Extract items from the current page
        for quote in response.css("div.quote"):
            yield {
                "text": quote.css("span.text::text").get(""),
                "author": quote.css("small.author::text").get(""),
            }

        # Follow the "next page" link
        next_page = response.css("li.next a::attr(href)").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)
```

`response.follow()` verarbeitet relative URLs automatisch und verbindet sie mit der URL der aktuellen Seite. Standardmäßig setzt es diese Seite auch als Wert des Headers `Referer`.

Für verschiedene Seitentypen können Sie Folgeanfragen an unterschiedliche Callback-Methoden senden:

```python
async def parse(self, response: Response):
    for link in response.css("a.product-link::attr(href)").getall():
        yield response.follow(link, callback=self.parse_product)

async def parse_product(self, response: Response):
    yield {
        "name": response.css("h1::text").get(""),
        "price": response.css(".price::text").get(""),
    }
```

!!! note

    Alle Callback-Methoden müssen asynchrone Generatoren sein und `async def` sowie `yield` verwenden.

## Daten exportieren {#exporting-data}

Die in `result.items` zurückgegebene `ItemList` hat eingebaute Exportmethoden:

```python
result = QuotesSpider().start()

# Export as JSON
result.items.to_json("quotes.json")

# Export as JSON with pretty-printing
result.items.to_json("quotes.json", indent=True)

# Export as JSON Lines (one JSON object per line)
result.items.to_jsonl("quotes.jsonl")

# Export as CSV or XML
result.items.to_csv("quotes.csv")
result.items.to_xml("quotes.xml")
```

Alle Methoden erstellen fehlende übergeordnete Verzeichnisse automatisch.

`to_csv()` schreibt eine Spalte für jeden Schlüssel, der in Ihren Datensätzen vorkommt. Datensätze dürfen also unterschiedliche Schlüssel haben; fehlende Zellen bleiben leer. Mit `fields=[...]` wählen Sie die Spalten und ihre Reihenfolge selbst, mit `delimiter="\t"` erstellen Sie eine TSV-Datei. `to_xml()` umschließt jeden Datensatz mit einem `<item>`-Element innerhalb des Wurzelelements `<items>`. Beide Namen können Sie mit `root_tag` und `item_tag` ändern.

In beiden Formaten werden Werte, die keine einfachen Skalare sind, etwa verschachtelte Dictionaries oder Listen, als JSON gespeichert. So gehen keine Daten unbemerkt verloren.

## Domains filtern {#filtering-domains}

Mit `allowed_domains` begrenzen Sie den Spider auf bestimmte Domains. So folgt er nicht versehentlich Links zu externen Websites:

```python
class MySpider(Spider):
    name = "my_spider"
    start_urls = ["https://example.com"]
    allowed_domains = {"example.com"}

    async def parse(self, response: Response):
        for link in response.css("a::attr(href)").getall():
            # Links to other domains are silently dropped
            yield response.follow(link, callback=self.parse)
```

Subdomains sind automatisch eingeschlossen. Mit `allowed_domains = {"example.com"}` erlauben Sie also auch `sub.example.com`, `blog.example.com` usw.

Ausgefilterte Anfragen werden in `stats.offsite_requests_count` gezählt. So sehen Sie, wie viele verworfen wurden.

## robots.txt beachten {#robotstxt-compliance}

Setzen Sie `robots_txt_obey = True`, damit der Spider vor dem Abruf einer Domain deren robots.txt-Regeln beachtet:

```python
class PoliteSpider(Spider):
    name = "polite"
    start_urls = ["https://example.com"]
    robots_txt_obey = True

    async def parse(self, response: Response):
        for link in response.css("a::attr(href)").getall():
            yield response.follow(link, callback=self.parse)
```

Wenn diese Option aktiv ist, führt der Spider folgende Schritte aus:

1. **robots.txt vorab abrufen:** Vor dem Crawl lädt er die Dateien für alle Domains in `start_urls` parallel.
2. **Jede Anfrage prüfen:** Er prüft sie anhand der `Disallow`-Regeln in der robots.txt der Domain. Nicht erlaubte Anfragen werden ohne Meldung verworfen und in `stats.robots_disallowed_count` gezählt.
3. **Die Vorgaben `Crawl-delay` und `Request-rate` beachten:** Er verwendet den höheren Wert aus der Vorgabe und Ihrem eingestellten `download_delay`. robots.txt kann Ihre Wartezeit somit nur erhöhen, niemals verkürzen. Wenn AutoThrottle aktiv ist, begrenzt dessen maximale Wartezeit auch diesen Wert. Setzen Sie `autothrottle_max_delay` hoch genug, um die geforderte Wartezeit einzuhalten.

robots.txt-Dateien werden über die Standardsitzung des Spiders abgerufen und für den gesamten Crawl pro Domain zwischengespeichert. Für Domains, die erst während des Crawls gefunden werden und nicht in `start_urls` stehen, wird die Datei bei der ersten Anfrage an diese Domain abgerufen.

**Hinweis:** `robots_txt_obey` ist standardmäßig ausgeschaltet, um unerwartetes Verhalten zu vermeiden. Wenn Sie es einschalten, bleiben Ihre Einstellungen für parallele Anfragen (`concurrent_requests`, `concurrent_requests_per_domain`) gleich. Nur die Wartezeit zwischen Anfragen wird angepasst.

Wenn Sie `download_delay` nicht selbst wählen möchten, setzen Sie `autothrottle_enabled = True`. Der Spider passt dann die Wartezeit je Domain an deren Antwortgeschwindigkeit an und wartet bei Sperren länger. Siehe [AutoThrottle](advanced.md#autothrottle).

## Nächste Schritte {#whats-next}

Nachdem Sie die Grundlagen kennen, können Sie diese Themen ansehen:

- [Anfragen und Antworten](requests-responses.md) - Prioritäten, Vermeidung doppelter Anfragen, Metadaten und mehr.
- [Sitzungen](sessions.md) - Verschiedene Fetcher-Typen (HTTP, Browser, Stealth) in einem Spider verwenden.
- [Proxys und Sperren](proxy-blocking.md) - Proxys zwischen Anfragen wechseln und Sperren behandeln.
- [Erweiterte Funktionen](advanced.md) - Parallele Anfragen, AutoThrottle, Pausieren und Fortsetzen, Streaming, Lebenszyklus-Hooks und Protokollierung.
