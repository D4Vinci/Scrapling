---
title: "Spider-Vorlagen für Links, Sitemaps, Feeds und Markdown"
description: "Wählen Sie CrawlSpider, SitemapSpider, XMLFeedSpider, CSVFeedSpider oder ContentSpider. Legen Sie Regeln fest, um Seiten, Feed-Zeilen oder eine Markdown-Sammlung zu erfassen."
---

# Allgemeine Spider-Vorlagen {#generic-spider-templates}

Die meisten Crawls folgen einem von zwei Mustern: „Links verfolgen, die zu diesem Muster passen“ oder „alle URLs aus der Sitemap abrufen“. Scrapling bietet Vorlagen für beide. So müssen Sie nicht jedes Mal denselben Grundaufbau für `parse()` schreiben.

`CrawlSpider` und `SitemapSpider` bauen auf `LinkExtractor` auf. Dieser liest URLs aus einer `Response` oder prüft einzelne URLs mit `matches()`. `SitemapSpider` verarbeitet außerdem die Inhalte von sitemap.xml und sitemap_index.xml, mit oder ohne gzip-Komprimierung.

Sie können `LinkExtractor` direkt in jeder normalen Methode `Spider.parse()` verwenden. Die Vorlagen nehmen Ihnen nur das Verknüpfen der Teile ab.

## CrawlSpider {#crawlspider}

`CrawlSpider` folgt Links automatisch anhand festgelegter Regeln.

```python
from scrapling.spiders import CrawlSpider, CrawlRule, LinkExtractor

class QuotesSpider(CrawlSpider):
    name = "blog"
    start_urls = ["https://quotes.toscrape.com/"]

    def rules(self):
        return [
            CrawlRule(LinkExtractor(allow=r"/author/"), callback=self.parse_author),
            CrawlRule(LinkExtractor(allow=r"/page/\d+/")),  # follow pagination, no callback
        ]

    async def parse_author(self, response):
        yield {
            '.author-title': response.css('.author-title::text').get(),
            "birthday": response.css('.author-born-date::text').get(),
            "url": response.url,
        }

result = QuotesSpider().start()
```

Eine `CrawlRule` verbindet einen `LinkExtractor` mit einem optionalen `callback`, einer gebundenen Methode des Spiders. Dazu kommen eine optionale `priority` für den erzeugten `Request` und ein optionales `process_request`. Letzteres ist eine gebundene Methode, die jeden `Request` vor der Ausgabe ändert. Die Standardmethode `parse()` wendet jede Regel auf jede Antwort an und liefert einen `Request` pro passender URL.

Hat eine Regel keinen Callback, werden die passenden URLs an die Standardmethode `parse()` des Spiders weitergegeben. Das ist praktisch für Folgeseiten: Sie extrahieren die Links zur nächsten Seite und setzen den Crawl fort, ohne eine eigene Methode dafür zu brauchen.

### Reihenfolge des Crawls {#crawl-order}

Setzen Sie `crawl_strategy` auf `CrawlSpider` oder seinen Unterklassen, einschließlich `ContentSpider`, um die nächste offene Anfrage auszuwählen:

| `crawl_strategy` | Reihenfolge bei gleicher `Request.priority` |
|------------------|---------------------------------------------|
| `"bfs"` (Standard) | Älteste Anfrage in der Warteschlange zuerst |
| `"dfs"` | Neueste Anfrage in der Warteschlange zuerst |

Der Scheduler nimmt offene Anfragen mit höherer `Request.priority` zuerst. Die Strategie legt nur die Reihenfolge bei gleicher Priorität fest.

Mit `concurrent_requests = 1` wird jeweils eine Anfrage in der gewählten Reihenfolge verarbeitet. Doppelte URLs werden weiterhin gefiltert. Wird eine URL erneut gefunden, ändert sich die Position ihrer Anfrage nicht. Bei parallelen Anfragen können Seiten in anderer Reihenfolge fertig werden und sich Ebenen oder Zweige überschneiden.

Behalten Sie beim Fortsetzen aus einem Checkpoint dieselbe `crawl_strategy` bei.

### Regeln mit eigener Logik verbinden {#combining-rules-with-custom-logic}

Überschreiben Sie `parse()` und rufen Sie `super().parse(response)` auf, um die Regeln zusammen mit Ihren eigenen Ausgaben zu verwenden:

```python
class MySpider(CrawlSpider):
    def rules(self):
        return [CrawlRule(LinkExtractor(allow=r"/posts/"), callback=self.parse_post)]

    async def parse(self, response):
        yield {"page_url": response.url}
        async for req in super().parse(response):
            yield req
```

### Anfragen mit `process_request` ändern {#mutating-requests-with-process_request}

```python
def add_priority(self, request, response):
    request.priority = 10
    return request

def rules(self):
    return [CrawlRule(
        LinkExtractor(allow=r"/posts/"),
        callback=self.parse_post,
        process_request=self.add_priority,
    )]
```

## SitemapSpider {#sitemapspider}

`SitemapSpider` startet einen Crawl mit URLs aus sitemap.xml. Er verwendet dieselbe `rules()`-API wie `CrawlSpider`, sodass der Aufbau gleich bleibt.

```python
from scrapling.spiders import SitemapSpider, CrawlRule, LinkExtractor

class MySitemap(SitemapSpider):
    name = "sm"
    sitemap_urls = ["https://example.com/sitemap.xml"]

    def rules(self):
        return [
            CrawlRule(LinkExtractor(allow=r"/posts/"), callback=self.parse_post),
            CrawlRule(LinkExtractor(allow=r"/products/"), callback=self.parse_product),
        ]

    async def parse_post(self, response):
        yield {"title": response.css("h1::text").get()}

    async def parse_product(self, response):
        yield {"sku": response.css(".sku::text").get()}

result = MySitemap().start()
```

### URLs zuordnen {#how-urls-are-dispatched}

Für jede URL in der Sitemap prüft `SitemapSpider` nacheinander `LinkExtractor.matches(url)` jeder Regel. Die erste passende Regel gewinnt. Es wird ein `Request` mit dem Callback dieser Regel geliefert. Passt keine Regel und ist `rules()` nicht leer, wird die URL verworfen. Gibt `rules()` eine leere Liste zurück, wird jede URL an die Methode `parse()` des Spiders geleitet. Wenn Sie diese nicht überschreiben, löst sie standardmäßig `NotImplementedError` aus.

### Sitemap-Indizes {#sitemap-indexes}

Wenn `SitemapSpider` auf einen `<sitemapindex>` trifft, also eine Sitemap mit weiteren Sitemaps, folgt er diesen automatisch. Mit einem `LinkExtractor` in `sitemap_follow` filtern Sie, welchen untergeordneten Sitemaps er folgen soll:

```python
class MySitemap(SitemapSpider):
    name = "sm"
    sitemap_urls = ["https://example.com/sitemap.xml"]
    sitemap_follow = LinkExtractor(allow=r"/posts-sitemap-\d+\.xml")  # only post sitemaps
```

### Unterstützung für robots.txt {#robotstxt-support}

Tragen Sie eine `robots.txt`-URL direkt in `sitemap_urls` ein. `SitemapSpider` erkennt sie, extrahiert alle angegebenen Sitemaps und folgt ihnen:

```python
class MySitemap(SitemapSpider):
    name = "sm"
    sitemap_urls = ["https://example.com/robots.txt"]
```

### URLs für andere Sprachen {#alternate-language-urls}

Setzen Sie `sitemap_alternate_links = True`, um auch URLs aus `<xhtml:link rel="alternate" hreflang="...">` anhand Ihrer Regeln zu verarbeiten.

## XMLFeedSpider {#xmlfeedspider}

`XMLFeedSpider` durchläuft die Knoten eines XML-Feeds, etwa RSS, Atom oder Produktfeeds. Setzen Sie `itertag` auf den gewünschten Knotennamen, standardmäßig `"item"`. Überschreiben Sie `parse_node()`, das einmal pro passendem Knoten aufgerufen wird:

```python
from scrapling.spiders import XMLFeedSpider

class RSSSpider(XMLFeedSpider):
    name = "rss"
    start_urls = ["https://example.com/feed.xml"]
    itertag = "item"

    async def parse_node(self, response, node):
        yield {
            "title": node.findtext("title"),
            "link": node.findtext("link"),
            "date": node.findtext("pubDate"),
        }

result = RSSSpider().start()
```

Wie die anderen Callbacks kann `parse_node()` auch `Request`-Objekte liefern, zum Beispiel `response.follow(node.findtext("link"), callback=self.parse_post)`. So ruft der Spider die Seiten auf, auf die der Feed verweist.

### Knoten auswählen und verarbeiten {#how-nodes-are-matched-and-parsed}

Jeder an `parse_node()` übergebene Knoten ist ein `lxml`-Element ohne Namespaces. Deshalb funktionieren `node.findtext("title")`, `node.find("thumbnail").get("url")` und `node.xpath(...)` mit jedem Feed ohne Namespace-Zuordnung. XPath unterscheidet dabei zwischen Groß- und Kleinschreibung. Ein einfaches `itertag` wie `"entry"` wählt Knoten nach ihrem Namen aus, unabhängig vom Namespace. Das passt für Atom und die meisten Feeds mit Namespaces. Für Knoten aus einem bestimmten Namespace verwenden Sie ein `itertag` mit Präfix und definieren dieses in `namespaces`:

```python
class ThumbnailSpider(XMLFeedSpider):
    name = "thumbs"
    start_urls = ["https://example.com/feed.xml"]
    itertag = "media:thumbnail"
    namespaces = (("media", "http://search.yahoo.com/mrss/"),)

    async def parse_node(self, response, node):
        yield {"thumbnail": node.get("url")}
```

Mit gzip komprimierte Feeds, etwa `.xml.gz` oder Inhalte mit einem gzip-Content-Type, werden automatisch entpackt. Dabei gelten dieselben Schutzmaßnahmen wie beim Sitemap-Spider. Fehlerhaftes XML führt zu einer Warnung im Protokoll, statt den Crawl abzubrechen.

## CSVFeedSpider {#csvfeedspider}

`CSVFeedSpider` durchläuft die Zeilen eines CSV-Feeds. Überschreiben Sie `parse_row()`. Die Methode erhält jede Zeile als Dictionary mit den Spaltennamen als Schlüsseln:

```python
from scrapling.spiders import CSVFeedSpider

class PriceSpider(CSVFeedSpider):
    name = "prices"
    start_urls = ["https://example.com/products.csv"]

    async def parse_row(self, response, row):
        yield {"product": row["title"], "price": float(row["price"])}

result = PriceSpider().start()
```

Standardmäßig dient die erste Zeile als Kopfzeile. Hat der Feed keine Kopfzeile, geben Sie die Spaltennamen selbst in `headers` an. Für Feeds, die nicht das übliche Kommaformat verwenden, stellen Sie `delimiter`/`quotechar` ein:

```python
class PriceSpider(CSVFeedSpider):
    name = "prices"
    start_urls = ["https://example.com/products.csv"]
    headers = ["title", "price", "url"]
    delimiter = ";"
```

Auch hier werden gzip-komprimierte Feeds automatisch entpackt, wie oben bei **XMLFeedSpider** beschrieben.

<a id="sitetomarkdownspider"></a>

## ContentSpider {#contentspider}

`ContentSpider` baut auf **CrawlSpider** auf. Er durchsucht eine Website und wandelt jede Seite in bereinigtes Markdown für LLMs um. Er liefert einen Datensatz pro Seite und kann zusätzlich je Seite eine Markdown-Datei schreiben:

```python
from scrapling.spiders import ContentSpider

class DocsSpider(ContentSpider):
    name = "docs"
    start_urls = ["https://example.com/docs/"]
    allowed_domains = {"example.com"}
    output_dir = "docs_markdown"

result = DocsSpider().start()
```

Er benötigt `allowed_domains`, damit der Crawl auf die Zielwebsite begrenzt bleibt. Die vollständige Anleitung mit allen Optionen und der Weitergabe an RAG-Pipelines finden Sie unter [RAG-Systeme erstellen](../ai/building-rag-systems.md).

## `LinkExtractor` direkt verwenden {#using-linkextractor-directly}

Sie müssen die Vorlagen nicht verwenden. `LinkExtractor` funktioniert in jedem normalen `Spider`:

```python
from scrapling.spiders import Spider, LinkExtractor

class CustomSpider(Spider):
    name = "custom"
    start_urls = ["https://example.com"]

    def __init__(self):
        super().__init__()
        self._links = LinkExtractor(allow=r"/posts/", deny_domains="ads.example.com")

    async def parse(self, response):
        for url in self._links.extract(response):
            yield response.follow(url, callback=self.parse_post)

    async def parse_post(self, response):
        yield {"title": response.css("h1::text").get()}
```

## LinkExtractor-Referenz {#linkextractor-reference}

| Argument          | Standard             | Beschreibung                                                                                       |
|-------------------|----------------------|----------------------------------------------------------------------------------------------------|
| `allow`           | `()`                 | Erlaubte URL-Muster. Leer bedeutet „alle“. String, kompiliertes `Pattern` oder Iterable aus beiden. |
| `deny`            | `()`                 | Zu verwerfende URL-Muster. Hat immer Vorrang vor `allow`.                                            |
| `allow_domains`   | `()`                 | Erlaubte Hostnamen. Subdomains passen automatisch (`example.com` schließt `api.example.com` ein).   |
| `deny_domains`    | `()`                 | Zu verwerfende Hostnamen.                                                                           |
| `restrict_css`    | `()`                 | CSS-Selektoren, die die Extraktion aus dem DOM auf einen Bereich begrenzen.                          |
| `restrict_xpath`  | `()`                 | XPath-Selektoren, die die Extraktion aus dem DOM auf einen Bereich begrenzen.                        |
| `tags`            | `("a", "area")`      | Element-Tags, in denen nach Links gesucht wird.                                                     |
| `attrs`           | `("href",)`          | Attribute dieser Tags, aus denen URLs gelesen werden.                                              |
| `canonicalize`    | `True`               | Query-Parameter sortieren und den Pfad vereinheitlichen.                                            |
| `strip`           | `True`               | Leerraum am Anfang und Ende extrahierter URLs entfernen.                                            |
| `keep_fragment`   | `False`              | `#fragment` beim Vereinheitlichen beibehalten.                                                      |
| `deny_extensions` | `IGNORED_EXTENSIONS` | Zu verwerfende Dateiendungen, etwa PDF, ZIP, Bilder und Videos.                                     |
| `process`         | `None`               | Optionale Funktion für jede extrahierte URL vor dem Filtern. Ein als falsch ausgewerteter Wert verwirft die URL.       |

`LinkExtractor.extract(response)` gibt eine `list[str]` mit absoluten, gefilterten URLs ohne Duplikate zurück.

`LinkExtractor.matches(url)` gibt einen `bool` zurück. Die Methode filtert nur die URL nach erlaubten und ausgeschlossenen Mustern, Domain und Dateiendung. `SitemapSpider` verwendet sie, um URLs ohne `Response` zuzuordnen.
