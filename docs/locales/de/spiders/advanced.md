---
title: "Crawls steuern: AutoThrottle, Checkpoints, Cache und Streaming"
description: "Steuern Sie die Crawl-Geschwindigkeit und parallele Anfragen. Lernen Sie den Antwort-Cache, Pausieren und Fortsetzen, Datensatz-Streaming und den Inhalt von Checkpoints kennen."
---

# Erweiterte Funktionen {#advanced-usages}

## Einführung {#introduction}

!!! success "Voraussetzungen"

    1. Sie haben die Seite [Erste Schritte](getting-started.md) gelesen und wissen, wie Sie einen einfachen Spider erstellen und starten.

Diese Seite erklärt die erweiterten Funktionen des Spider-Systems: parallele Anfragen steuern, pausieren und fortsetzen, Streaming, Lebenszyklus-Hooks, Statistiken und Protokollierung.

## Parallele Anfragen steuern {#concurrency-control}

Mit diesen Klassenattributen steuert das Spider-System, wie viele Anfragen es in welcher Zeit sendet:

| Attribut                         | Standard | Beschreibung                                                      |
|----------------------------------|----------|-------------------------------------------------------------------|
| `concurrent_requests`            | `4`      | Höchste Anzahl gleichzeitig verarbeiteter Anfragen                 |
| `concurrent_requests_per_domain` | `0`      | Höchste Anzahl paralleler Anfragen pro Domain (0 = keine Grenze pro Domain) |
| `download_delay`                 | `0.0`    | Wartezeit vor jeder Anfrage in Sekunden                            |
| `robots_txt_obey`                | `False`  | robots.txt-Regeln beachten (Disallow, Crawl-delay, Request-rate)    |

```python
class PoliteSpider(Spider):
    name = "polite"
    start_urls = ["https://example.com"]

    # Be gentle with the server
    concurrent_requests = 4
    concurrent_requests_per_domain = 2
    download_delay = 1.0  # Wait 1 second between requests

    async def parse(self, response: Response):
        yield {"title": response.css("title::text").get("")}
```

Wenn `concurrent_requests_per_domain` gesetzt ist, erhält jede Domain neben der globalen Grenze eine eigene Grenze für parallele Anfragen. So können Sie mehrere Domains gleichzeitig abrufen und insgesamt viele Anfragen verarbeiten, ohne einzelne Domains zu stark zu belasten.

!!! tip

    Der Parameter `download_delay` fügt vor jeder Anfrage eine feste Wartezeit ein, unabhängig von der Domain. Damit begrenzen Sie die Anfragerate auf einfache Weise.

## AutoThrottle {#autothrottle}

Ein fester `download_delay` ist eine Schätzung. Ist er zu niedrig, werden Sie gesperrt. Ist er zu hoch, dauert der Crawl die ganze Nacht. AutoThrottle misst stattdessen, wie schnell die Website antwortet, und passt die Wartezeit für jede Domain an. Bei schnellen Servern geht es schneller, bei langsamen oder sperrenden Servern langsamer.

| Attribut                           | Standard | Beschreibung                                                       |
|------------------------------------|----------|--------------------------------------------------------------------|
| `autothrottle_enabled`             | `False`  | Automatische Anpassung der Wartezeit einschalten                    |
| `autothrottle_start_delay`         | `5.0`    | Wartezeit vor der ersten Anfrage an eine Domain                    |
| `autothrottle_max_delay`           | `60.0`   | Höchste erlaubte Wartezeit                                         |
| `autothrottle_target_concurrency`  | `None`   | Angestrebte Anzahl paralleler Anfragen pro Domain, siehe unten      |
| `autothrottle_block_backoff`       | `True`   | Wartezeit einer Domain bei jeder Sperre verdoppeln                  |

```python
class AdaptiveSpider(Spider):
    name = "adaptive"
    start_urls = ["https://example.com"]

    concurrent_requests = 8
    concurrent_requests_per_domain = 1

    autothrottle_enabled = True
    autothrottle_start_delay = 2.0
    autothrottle_max_delay = 30.0

    async def parse(self, response: Response):
        yield {"title": response.css("title::text").get("")}
```

Nach jeder Antwort nähert sich die Wartezeit der Antwortzeit des Servers an. Antwortet eine Website in 0,5 Sekunden, stellt sich eine Wartezeit von ungefähr 0,5 Sekunden ein. Das entspricht etwa einer laufenden Anfrage. Die Zielanzahl paralleler Anfragen pro Domain wird in dieser Reihenfolge bestimmt: `autothrottle_target_concurrency`, wenn gesetzt, sonst `concurrent_requests_per_domain`, sonst 1. Meist müssen Sie also keinen eigenen Zielwert setzen. Die bereits konfigurierte Grenze pro Domain wird verwendet und die Wartezeit durch diesen Wert geteilt. Steigt die Antwortzeit stark an, wirkt sich das sofort aus und wird nicht erst gemittelt. Der Spider wird daher sofort langsamer, wenn der Server Probleme hat, und beschleunigt nur schrittweise.

### Bei Sperren langsamer werden {#backing-off-when-blocked}

Die Antwortzeit allein erkennt keine Anfragelimits. Eine Antwort mit `429`, `403` oder einer CAPTCHA-Seite kommt oft *schneller* zurück als der eigentliche Inhalt. Nur nach Antwortzeit betrachtet wäre das ein Grund, schneller zu werden. Stattdessen **verdoppelt** jede fehlerhafte Antwort die Wartezeit der Domain. Dazu zählen Statuscodes außerhalb von 2xx und Antworten, die `is_blocked()` als gesperrt einstuft:

```
0.5s -> 1s -> 2s -> 4s -> 8s ...   (up to autothrottle_max_delay)
```

Solange die Website Anfragen ablehnt, wird der Spider weiter langsamer. Sobald wieder erfolgreiche Antworten kommen, senkt die normale Mittelwertbildung die Wartezeit schrittweise auf die tatsächliche Antwortzeit. Der Spider erholt sich selbst, ohne dass Sie ihn neu starten müssen.

Wenn die Website bei `429` oder `503` über den Header `Retry-After` eine genaue Wartezeit nennt, wird dieser Wert statt der Verdopplung verwendet. Sowohl die Zahlenform (`Retry-After: 120`) als auch das HTTP-Datumsformat werden unterstützt.

Mit `autothrottle_block_backoff = False` schalten Sie dieses Verhalten aus. Dann wird nur die Antwortzeit berücksichtigt. Eine Sperre verhindert lediglich, dass der Spider schneller wird.

Die endgültige Wartezeit pro Domain finden Sie in den Statistiken:

```python
result = AdaptiveSpider().start()
print(result.stats.autothrottle_delays)  # {'example.com': 0.62}
```

!!! note "Hinweise:"

    * `download_delay` und Wartezeiten aus robots.txt bilden die Untergrenze. Doch auch diese wird durch `autothrottle_max_delay` begrenzt. Setzen Sie das Maximum mindestens so hoch wie die konfigurierte oder von robots.txt geforderte Wartezeit.<br/>
    * `concurrent_requests_per_domain` hat zwei Aufgaben: Es begrenzt laufende Anfragen pro Domain und dient als Zielwert für AutoThrottle. Meist ist deshalb kein eigener Zielwert nötig. Wir empfehlen, diese Grenze zu setzen. Eine wartende Anfrage belegt nämlich einen Platz innerhalb der globalen Grenze. Ohne Grenze pro Domain können wartende Anfragen die Plätze belegen, die alle Domains gemeinsam nutzen.<br/>
    * Die gemessene Antwortzeit umfasst den gesamten Abruf, einschließlich interner Wiederholungen und bei Browser-Sitzungen auch der Zeit zum Rendern der Seite.<br/>
    * `autothrottle_max_delay` begrenzt alle Wartezeiten, auch `Retry-After`. Fordert eine Website eine längere Pause, erhöhen Sie `autothrottle_max_delay`, um sie einzuhalten.<br/>
    * Die ermittelten Wartezeiten werden nicht in Checkpoints gespeichert. Nach dem Pausieren und Fortsetzen beginnt jede Domain wieder mit `autothrottle_start_delay`.

## uvloop verwenden {#using-uvloop}

Die Methode `start()` nimmt den Parameter `use_uvloop` an. Damit verwendet sie, falls verfügbar, die schnellere Event-Loop-Implementierung [uvloop](https://github.com/MagicStack/uvloop)/[winloop](https://github.com/nicktimko/winloop):

```python
result = MySpider().start(use_uvloop=True)
```

Das kann Crawls mit vielen Ein- und Ausgabevorgängen beschleunigen. Sie müssen `uvloop` unter Linux/macOS oder `winloop` unter Windows getrennt installieren.

## Pausieren und fortsetzen {#pause-resume}

Der Spider kann durch Checkpoints geordnet pausiert und fortgesetzt werden. Übergeben Sie dafür dem Konstruktor ein Verzeichnis als `crawldir`:

```python
spider = MySpider(crawldir="crawl_data/my_spider")
result = spider.start()

if result.paused:
    print("Crawl was paused. Run again to resume.")
else:
    print("Crawl completed!")
```

### Funktionsweise {#how-it-works}

1. **Pausieren:** Drücken Sie während des Crawls `Ctrl+C`. Der Spider wartet auf alle laufenden Anfragen, speichert offene Anfragen und Fingerprints bereits besuchter Anfragen in einem Checkpoint und beendet sich.
2. **Sofort stoppen:** Drücken Sie `Ctrl+C` ein zweites Mal, um ohne Warten auf laufende Aufgaben zu stoppen.
3. **Fortsetzen:** Starten Sie den Spider erneut mit demselben `crawldir`. Er erkennt den Checkpoint, stellt die Warteschlange und die Menge der bekannten Fingerprints wieder her und setzt den Crawl fort. Dabei wird `start_requests()` übersprungen.
4. **Aufräumen:** Wird ein Crawl normal beendet und nicht pausiert, werden die Checkpoint-Dateien automatisch gelöscht.

**Auch während des Crawls werden regelmäßig Checkpoints gespeichert, standardmäßig alle 5 Minuten.**

So ändern Sie den Abstand:

```python
# Save checkpoint every 2 minutes
spider = MySpider(crawldir="crawl_data/my_spider", interval=120.0)
```

Beim Speichern eines Checkpoints wird eine temporäre Datei verwendet. Der vorherige Checkpoint wird erst ersetzt, wenn das Schreiben erfolgreich war.

!!! warning "Checkpoint-Daten"

    Wenn Sie `crawldir` aktivieren, müssen sich die Werte in offenen Anfragen, einschließlich `meta` und Anfrageargumenten, mit Pythons Modul `pickle` speichern lassen. Kann ein Wert nicht gespeichert werden, schlägt das Speichern des Checkpoints fehl und der Crawl stoppt. Ein `Selector` kann in einem Callback verwendet werden, lässt sich aber nicht auf diese Weise speichern.

    Speichern Sie extrahierte Werte wie Zeichenfolgen oder Zahlen statt `Selector`-Objekten. Auch Listen und Dictionaries dürfen nur Werte enthalten, die sich speichern lassen:

    ```python
    yield response.follow("/details", meta={"title": str(response.css("h1::text").get(""))})
    ```

!!! tip

    Bei `start()` wird der Spider durch `Ctrl+C` auch ohne aktiviertes Checkpoint-System geordnet beendet. Ein weiterer Tastendruck, bevor er fertig ist, beendet ihn sofort.

### Erkennen, ob ein Crawl fortgesetzt wird {#knowing-if-youre-resuming}

Der Hook `on_start()` erhält das Flag `resuming`:

```python
async def on_start(self, resuming: bool = False):
    if resuming:
        self.logger.info("Resuming from checkpoint!")
    else:
        self.logger.info("Starting fresh crawl")
```

## Entwicklungsmodus {#development-mode}

Wenn Sie die `parse()`-Logik eines Spiders überarbeiten, sind neue Anfragen an die Zielserver bei jedem Lauf langsam und unnötig. Im Entwicklungsmodus werden alle Antworten beim ersten Lauf auf der Festplatte gespeichert und später von dort gelesen. So können Sie Ihre Selektoren ändern und den Spider beliebig oft neu starten, ohne diese Seiten erneut abzurufen.

Setzen Sie dafür `development_mode = True` in Ihrem Spider:

```python
class MySpider(Spider):
    name = "my_spider"
    start_urls = ["https://example.com"]
    development_mode = True

    async def parse(self, response: Response):
        yield {"title": response.css("title::text").get("")}
```

Der erste Lauf ruft die Seiten normal ab und speichert jede Antwort auf der Festplatte. Bei späteren Läufen werden dieselben Anfragen aus dem Cache beantwortet. Der Seitenabruf entfällt. Bei `robots_txt_obey=True` werden die robots.txt-Regeln vor dem Lesen aus dem Cache geprüft.

### Speicherort des Caches {#cache-location}

Standardmäßig werden Antworten unter `.scrapling_cache/{spider.name}/` gespeichert. Der Pfad ist relativ zum aktuellen Arbeitsverzeichnis, also dort, wo Sie den Spider gestartet haben, **nicht** dort, wo das Spider-Skript liegt. Mit `development_cache_dir` ändern Sie den Speicherort:

```python
class MySpider(Spider):
    name = "my_spider"
    start_urls = ["https://example.com"]
    development_mode = True
    development_cache_dir = "/tmp/my_spider_cache"
```

### Funktionsweise {#how-it-works_1}

1. **Cache-Schlüssel:** Jede Antwort wird über den Fingerprint der Anfrage zugeordnet. Ändern Sie Attribute, die den Fingerprint beeinflussen (`fp_include_kwargs`, `fp_include_headers`, `fp_keep_fragments`), wird die Seite erneut abgerufen.
2. **Speicherformat:** Pro Antwort wird eine JSON-Datei mit dem Namen `{fingerprint_hex}.json` erstellt. Der Body ist mit Base64 kodiert, damit Binärdaten exakt erhalten bleiben. Schreibvorgänge sind atomar: temporäre Datei und Umbenennen.
3. **Wiederverwendung:** Bei einem Cache-Treffer überspringt die Engine den Seitenabruf samt `download_delay`, Begrenzung der Anfragerate und Wiederholungen über `is_blocked()`. Die gespeicherte Antwort geht direkt an Ihren Callback.
4. **Statistiken:** Anfragen aus dem Cache zählen weiterhin für `requests_count`, `response_bytes` und die Zähler pro Statuscode. Die Statistik sieht also wie bei einem normalen Crawl aus. Die zusätzlichen Zähler `cache_hits` und `cache_misses` zeigen, wie oft der Cache eine Antwort liefern konnte.

### Cache leeren {#clearing-the-cache}

Cache-Einträge laufen nicht automatisch ab. Löschen Sie für einen neuen Crawl das Cache-Verzeichnis oder rufen Sie die Methode `clear()` des Managers direkt auf.

!!! warning

    Der Entwicklungsmodus ist nur für die Entwicklung gedacht. Gespeicherte Antworten laufen nie ab. Beim Lesen aus dem Cache werden Anfrageraten und Wiederholungen gesperrter Anfragen übersprungen. Setzen Sie einen Spider nicht mit `development_mode = True` im Produktivbetrieb ein.

## Streaming {#streaming}

Verwenden Sie `stream()` statt `start()` für lang laufende Spider oder Anwendungen, die sofort auf extrahierte Datensätze zugreifen müssen:

```python
import anyio

async def main():
    spider = MySpider()
    async for item in spider.stream():
        print(f"Got item: {item}")
        # Access real-time stats
        print(f"Items so far: {spider.stats.items_scraped}")
        print(f"Requests made: {spider.stats.requests_count}")

anyio.run(main)
```

Die wichtigsten Unterschiede zu `start()`:

- `stream()` muss aus einem asynchronen Kontext aufgerufen werden.
- Datensätze werden einzeln direkt nach der Extraktion geliefert, statt in einer Liste gesammelt zu werden.
- Während des Durchlaufs erhalten Sie über `spider.stats` aktuelle Statistiken.

!!! abstract

    Alle über `spider.stats` verfügbaren Statistiken werden [weiter unten](#results-statistics) erklärt.

Sie können Streaming auch mit Checkpoints verwenden. So lassen sich Oberflächen mit aktuellen Daten erstellen, in denen Crawls pausiert und fortgesetzt werden können.

```python
import anyio

async def main():
    spider = MySpider(crawldir="crawl_data/my_spider")
    async for item in spider.stream():
        print(f"Got item: {item}")
        # Access real-time stats
        print(f"Items so far: {spider.stats.items_scraped}")
        print(f"Requests made: {spider.stats.requests_count}")

anyio.run(main)
```
Mit `spider.pause()` können Sie den Spider im Beispiel auch aus dem Code heraus stoppen. Ohne aktiviertes Checkpoint-System wird der Crawl einfach beendet.

## Lebenszyklus-Hooks {#lifecycle-hooks}

Der Spider bietet mehrere Hooks, die Sie überschreiben können. Damit ergänzen Sie eigenes Verhalten in verschiedenen Phasen des Crawls:

### on_start {#on_start}

Wird vor Beginn des Crawls aufgerufen. Verwenden Sie ihn für Vorbereitungen, etwa das Laden von Daten oder Einrichten von Ressourcen:

```python
async def on_start(self, resuming: bool = False):
    self.logger.info("Spider starting up")
    # Load seed URLs from a database, initialize counters, etc.
```

### on_close {#on_close}

Wird nach dem Crawl aufgerufen, unabhängig davon, ob dieser abgeschlossen oder pausiert wurde. Verwenden Sie ihn zum Aufräumen:

```python
async def on_close(self):
    self.logger.info("Spider shutting down")
    # Close database connections, flush buffers, etc.
```

### on_error {#on_error}

Wird aufgerufen, wenn eine Anfrage mit einer Ausnahme fehlschlägt. Verwenden Sie ihn, um Fehler zu erfassen oder eine eigene Fehlerbehandlung einzubauen:

```python
async def on_error(self, request: Request, error: Exception):
    self.logger.error(f"Failed: {request.url} - {error}")
    # Log to error tracker, save failed URL for later, etc.
```

### on_scraped_item {#on_scraped_item}

Wird für jeden extrahierten Datensatz aufgerufen, bevor er zu den Ergebnissen hinzugefügt wird. Geben Sie den Datensatz unverändert oder geändert zurück, um ihn zu behalten. Geben Sie `None` zurück, um ihn zu verwerfen:

```python
async def on_scraped_item(self, item: dict) -> dict | None:
    # Drop items without a title
    if not item.get("title"):
        return None

    # Modify items (e.g., add timestamps)
    item["scraped_at"] = "2026-01-01"
    return item
```

!!! tip

    Mit diesem Hook können Sie Datensätze auch durch eigene Pipelines leiten und aus den Spider-Ergebnissen entfernen.

### start_requests {#start_requests}

Überschreiben Sie `start_requests()`, um die ersten Anfragen selbst zu erstellen, statt `start_urls` zu verwenden:

```python
async def start_requests(self):
    # POST request to log in first
    yield Request(
        "https://example.com/login",
        method="POST",
        data={"user": "admin", "pass": "secret"},
        callback=self.after_login,
    )

async def after_login(self, response: Response):
    # Now crawl the authenticated pages
    yield response.follow("/dashboard", callback=self.parse)
```

## Ergebnisse und Statistiken {#results-statistics}

Das von `start()` zurückgegebene `CrawlResult` enthält sowohl die extrahierten Datensätze als auch ausführliche Statistiken:

```python
result = MySpider().start()

# Items
print(f"Total items: {len(result.items)}")
result.items.to_json("output.json", indent=True)

# Did the crawl complete?
print(f"Completed: {result.completed}")
print(f"Paused: {result.paused}")

# Statistics
stats = result.stats
print(f"Requests: {stats.requests_count}")
print(f"Failed: {stats.failed_requests_count}")
print(f"Blocked: {stats.blocked_requests_count}")
print(f"Offsite filtered: {stats.offsite_requests_count}")
print(f"Robots.txt disallowed: {stats.robots_disallowed_count}")
print(f"Cache hits: {stats.cache_hits}")
print(f"Cache misses: {stats.cache_misses}")
print(f"Items scraped: {stats.items_scraped}")
print(f"Items dropped: {stats.items_dropped}")
print(f"Response bytes: {stats.response_bytes}")
print(f"Duration: {stats.elapsed_seconds:.1f}s")
print(f"Speed: {stats.requests_per_second:.1f} req/s")
```

### Ausführliche Statistiken {#detailed-stats}

Das Objekt `CrawlStats` erfasst detaillierte Angaben:

```python
stats = result.stats

# Status code distribution
print(stats.response_status_count)
# {'status_200': 150, 'status_404': 3, 'status_403': 1}

# Bytes downloaded per domain
print(stats.domains_response_bytes)
# {'example.com': 1234567, 'api.example.com': 45678}

# Requests per session
print(stats.sessions_requests_count)
# {'http': 120, 'stealth': 34}

# Proxies used during the crawl
print(stats.proxies)
# ['http://proxy1:8080', 'http://proxy2:8080']

# Log level counts
print(stats.log_levels_counter)
# {'debug': 200, 'info': 50, 'warning': 3, 'error': 1, 'critical': 0}

# Timing information
print(stats.start_time)       # Unix timestamp when crawl started
print(stats.end_time)         # Unix timestamp when crawl finished
print(stats.download_delay)   # The download delay used (seconds)

# Concurrency settings used
print(stats.concurrent_requests)             # Global concurrency limit
print(stats.concurrent_requests_per_domain)  # Per-domain concurrency limit

# AutoThrottle
print(stats.autothrottle_enabled)  # Whether the adaptive delay was on
print(stats.autothrottle_delays)   # Final delay per domain, {'example.com': 0.62}

# Custom stats (set by your spider code)
print(stats.custom_stats)
# {'login_attempts': 3, 'pages_with_errors': 5}

# Export everything as a dict
print(stats.to_dict())
```

## Protokollierung {#logging}

Der Spider hat einen eingebauten Logger, auf den Sie über `self.logger` zugreifen. Er verwendet bereits den Namen des Spiders und bietet diese Einstellungen:

| Attribut              | Standard                                                     | Beschreibung                                        |
|-----------------------|--------------------------------------------------------------|-----------------------------------------------------|
| `logging_level`       | `logging.DEBUG`                                              | Niedrigste protokollierte Meldungsstufe               |
| `logging_format`      | `"[%(asctime)s]:({spider_name}) %(levelname)s: %(message)s"` | Format der Protokollmeldungen                        |
| `logging_date_format` | `"%Y-%m-%d %H:%M:%S"`                                        | Datumsformat in Protokollmeldungen                   |
| `log_file`            | `None`                                                       | Pfad einer Protokolldatei zusätzlich zur Konsolenausgabe |

```python
import logging

class MySpider(Spider):
    name = "my_spider"
    start_urls = ["https://example.com"]
    logging_level = logging.INFO
    log_file = "logs/my_spider.log"

    async def parse(self, response: Response):
        self.logger.info(f"Processing {response.url}")
        yield {"title": response.css("title::text").get("")}
```

Das Verzeichnis der Protokolldatei wird bei Bedarf automatisch erstellt. Die Ausgabe in Konsole und Datei verwendet dasselbe Format.
