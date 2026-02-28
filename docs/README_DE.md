<!-- mcp-name: io.github.D4Vinci/Scrapling -->

<h1 align="center">
    <a href="https://scrapling.readthedocs.io">
        <picture>
          <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/docs/assets/cover_dark.svg?sanitize=true">
          <img alt="Scrapling Poster" src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/docs/assets/cover_light.svg?sanitize=true">
        </picture>
    </a>
    <br>
    <small>Effortless Web Scraping for the Modern Web</small>
</h1>

<p align="center">
    <a href="https://github.com/D4Vinci/Scrapling/actions/workflows/tests.yml" alt="Tests">
        <img alt="Tests" src="https://github.com/D4Vinci/Scrapling/actions/workflows/tests.yml/badge.svg"></a>
    <a href="https://badge.fury.io/py/Scrapling" alt="PyPI version">
        <img alt="PyPI version" src="https://badge.fury.io/py/Scrapling.svg"></a>
    <a href="https://pepy.tech/project/scrapling" alt="PyPI Downloads">
        <img alt="PyPI Downloads" src="https://static.pepy.tech/personalized-badge/scrapling?period=total&units=INTERNATIONAL_SYSTEM&left_color=GREY&right_color=GREEN&left_text=Downloads"></a>
    <br/>
    <a href="https://discord.gg/EMgGbDceNQ" alt="Discord" target="_blank">
      <img alt="Discord" src="https://img.shields.io/discord/1360786381042880532?style=social&logo=discord&link=https%3A%2F%2Fdiscord.gg%2FEMgGbDceNQ">
    </a>
    <a href="https://x.com/Scrapling_dev" alt="X (formerly Twitter)">
      <img alt="X (formerly Twitter) Follow" src="https://img.shields.io/twitter/follow/Scrapling_dev?style=social&logo=x&link=https%3A%2F%2Fx.com%2FScrapling_dev">
    </a>
    <br/>
    <a href="https://pypi.org/project/scrapling/" alt="Supported Python versions">
        <img alt="Supported Python versions" src="https://img.shields.io/pypi/pyversions/scrapling.svg"></a>
</p>

<p align="center">
    <a href="https://scrapling.readthedocs.io/en/latest/parsing/selection/"><strong>Auswahlmethoden</strong></a>
    &middot;
    <a href="https://scrapling.readthedocs.io/en/latest/fetching/choosing/"><strong>Einen Fetcher wählen</strong></a>
    &middot;
    <a href="https://scrapling.readthedocs.io/en/latest/spiders/architecture.html"><strong>Spiders</strong></a>
    &middot;
    <a href="https://scrapling.readthedocs.io/en/latest/spiders/proxy-blocking.html"><strong>Proxy-Rotation</strong></a>
    &middot;
    <a href="https://scrapling.readthedocs.io/en/latest/cli/overview/"><strong>CLI</strong></a>
    &middot;
    <a href="https://scrapling.readthedocs.io/en/latest/ai/mcp-server/"><strong>MCP-Modus</strong></a>
</p>

Scrapling ist ein adaptives Web-Scraping-Framework, das alles abdeckt -- von einer einzelnen Anfrage bis hin zu einem umfassenden Crawl.

Sein Parser lernt aus Website-Änderungen und lokalisiert Ihre Elemente automatisch neu, wenn sich Seiten aktualisieren. Seine Fetcher umgehen Anti-Bot-Systeme wie Cloudflare Turnstile direkt ab Werk. Und sein Spider-Framework ermöglicht es Ihnen, auf parallele Multi-Session-Crawls mit Pause & Resume und automatischer Proxy-Rotation hochzuskalieren -- alles in wenigen Zeilen Python. Eine Bibliothek, keine Kompromisse.

Blitzschnelle Crawls mit Echtzeit-Statistiken und Streaming. Von Web Scrapern für Web Scraper und normale Benutzer entwickelt, ist für jeden etwas dabei.

```python
from scrapling.fetchers import Fetcher, AsyncFetcher, StealthyFetcher, DynamicFetcher
StealthyFetcher.adaptive = True
p = StealthyFetcher.fetch('https://example.com', headless=True, network_idle=True)  # Website unbemerkt abrufen!
products = p.css('.product', auto_save=True)                                        # Daten scrapen, die Website-Designänderungen überleben!
products = p.css('.product', adaptive=True)                                         # Später, wenn sich die Website-Struktur ändert, `adaptive=True` übergeben, um sie zu finden!
```
Oder auf vollständige Crawls hochskalieren
```python
from scrapling.spiders import Spider, Response

class MySpider(Spider):
  name = "demo"
  start_urls = ["https://example.com/"]

  async def parse(self, response: Response):
      for item in response.css('.product'):
          yield {"title": item.css('h2::text').get()}

MySpider().start()
```


# Platin-Sponsoren

<i><sub>Möchten Sie das erste Unternehmen sein, das hier erscheint? Klicken Sie [hier](https://github.com/sponsors/D4Vinci/sponsorships?tier_id=586646)</sub></i>
# Sponsoren

<!-- sponsors -->

<a href="https://www.thordata.com/?ls=github&lk=github" target="_blank" title="Unblockable proxies and scraping infrastructure, delivering real-time, reliable web data to power AI models and workflows."><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/thordata.jpg"></a>
<a href="https://evomi.com?utm_source=github&utm_medium=banner&utm_campaign=d4vinci-scrapling" target="_blank" title="Evomi is your Swiss Quality Proxy Provider, starting at $0.49/GB"><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/evomi.png"></a>
<a href="https://serpapi.com/?utm_source=scrapling" target="_blank" title="Scrape Google and other search engines with SerpApi"><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/SerpApi.png"></a>
<a href="https://visit.decodo.com/Dy6W0b" target="_blank" title="Try the Most Efficient Residential Proxies for Free"><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/decodo.png"></a>
<a href="https://petrosky.io/d4vinci" target="_blank" title="PetroSky delivers cutting-edge VPS hosting."><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/petrosky.png"></a>
<a href="https://hasdata.com/?utm_source=github&utm_medium=banner&utm_campaign=D4Vinci" target="_blank" title="The web scraping service that actually beats anti-bot systems!"><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/hasdata.png"></a>
<a href="https://proxyempire.io/?ref=scrapling&utm_source=scrapling" target="_blank" title="Collect The Data Your Project Needs with the Best Residential Proxies"><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/ProxyEmpire.png"></a>
<a href="https://hypersolutions.co/?utm_source=github&utm_medium=readme&utm_campaign=scrapling" target="_blank" title="Bot Protection Bypass API for Akamai, DataDome, Incapsula & Kasada"><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/HyperSolutions.png"></a>


<a href="https://www.swiftproxy.net/" target="_blank" title="Unlock Reliable Proxy Services with Swiftproxy!"><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/swiftproxy.png"></a>
<a href="https://www.rapidproxy.io/?ref=d4v" target="_blank" title="Affordable Access to the Proxy World – bypass CAPTCHAs blocks, and avoid additional costs."><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/rapidproxy.jpg"></a>
<a href="https://browser.cash/?utm_source=D4Vinci&utm_medium=referral" target="_blank" title="Browser Automation & AI Browser Agent Platform"><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/browserCash.png"></a>

<!-- /sponsors -->

<i><sub>Möchten Sie Ihre Anzeige hier zeigen? Klicken Sie [hier](https://github.com/sponsors/D4Vinci) und wählen Sie die Stufe, die zu Ihnen passt!</sub></i>

---

## Hauptmerkmale

### Spiders -- Ein vollständiges Crawling-Framework
- 🕷️ **Scrapy-ähnliche Spider-API**: Definieren Sie Spiders mit `start_urls`, async `parse` Callbacks und `Request`/`Response`-Objekten.
- ⚡ **Paralleles Crawling**: Konfigurierbare Parallelitätslimits, domainbezogenes Throttling und Download-Verzögerungen.
- 🔄 **Multi-Session-Unterstützung**: Einheitliche Schnittstelle für HTTP-Anfragen und heimliche Headless-Browser in einem einzigen Spider -- leiten Sie Anfragen per ID an verschiedene Sessions weiter.
- 💾 **Pause & Resume**: Checkpoint-basierte Crawl-Persistenz. Drücken Sie Strg+C für ein kontrolliertes Herunterfahren; starten Sie neu, um dort fortzufahren, wo Sie aufgehört haben.
- 📡 **Streaming-Modus**: Gescrapte Elemente in Echtzeit streamen über `async for item in spider.stream()` mit Echtzeit-Statistiken -- ideal für UI, Pipelines und lang laufende Crawls.
- 🛡️ **Erkennung blockierter Anfragen**: Automatische Erkennung und Wiederholung blockierter Anfragen mit anpassbarer Logik.
- 📦 **Integrierter Export**: Ergebnisse über Hooks und Ihre eigene Pipeline oder den integrierten JSON/JSONL-Export mit `result.items.to_json()` / `result.items.to_jsonl()` exportieren.

### Erweitertes Website-Abrufen mit Session-Unterstützung
- **HTTP-Anfragen**: Schnelle und heimliche HTTP-Anfragen mit der `Fetcher`-Klasse. Kann Browser-TLS-Fingerprints und Header imitieren und HTTP/3 verwenden.
- **Dynamisches Laden**: Dynamische Websites mit vollständiger Browser-Automatisierung über die `DynamicFetcher`-Klasse abrufen, die Playwrights Chromium und Google Chrome unterstützt.
- **Anti-Bot-Umgehung**: Erweiterte Stealth-Fähigkeiten mit `StealthyFetcher` und Fingerprint-Spoofing. Kann alle Arten von Cloudflares Turnstile/Interstitial einfach mit Automatisierung umgehen.
- **Session-Verwaltung**: Persistente Session-Unterstützung mit den Klassen `FetcherSession`, `StealthySession` und `DynamicSession` für Cookie- und Zustandsverwaltung über Anfragen hinweg.
- **Proxy-Rotation**: Integrierter `ProxyRotator` mit zyklischen oder benutzerdefinierten Rotationsstrategien über alle Session-Typen hinweg, plus Proxy-Überschreibungen pro Anfrage.
- **Domain-Blockierung**: Anfragen an bestimmte Domains (und deren Subdomains) in browserbasierten Fetchern blockieren.
- **Async-Unterstützung**: Vollständige async-Unterstützung über alle Fetcher und dedizierte async Session-Klassen hinweg.

### Adaptives Scraping & KI-Integration
- 🔄 **Intelligente Element-Verfolgung**: Elemente nach Website-Änderungen mit intelligenten Ähnlichkeitsalgorithmen neu lokalisieren.
- 🎯 **Intelligente flexible Auswahl**: CSS-Selektoren, XPath-Selektoren, filterbasierte Suche, Textsuche, Regex-Suche und mehr.
- 🔍 **Ähnliche Elemente finden**: Elemente, die gefundenen Elementen ähnlich sind, automatisch lokalisieren.
- 🤖 **MCP-Server für die Verwendung mit KI**: Integrierter MCP-Server für KI-unterstütztes Web Scraping und Datenextraktion. Der MCP-Server verfügt über leistungsstarke, benutzerdefinierte Funktionen, die Scrapling nutzen, um gezielten Inhalt zu extrahieren, bevor er an die KI (Claude/Cursor/etc.) übergeben wird, wodurch Vorgänge beschleunigt und Kosten durch Minimierung der Token-Nutzung gesenkt werden. ([Demo-Video](https://www.youtube.com/watch?v=qyFk3ZNwOxE))

### Hochleistungs- und praxiserprobte Architektur
- 🚀 **Blitzschnell**: Optimierte Leistung, die die meisten Python-Scraping-Bibliotheken übertrifft.
- 🔋 **Speichereffizient**: Optimierte Datenstrukturen und Lazy Loading für einen minimalen Speicher-Footprint.
- ⚡ **Schnelle JSON-Serialisierung**: 10x schneller als die Standardbibliothek.
- 🏗️ **Praxiserprobt**: Scrapling hat nicht nur eine Testabdeckung von 92% und eine vollständige Type-Hints-Abdeckung, sondern wird seit dem letzten Jahr täglich von Hunderten von Web Scrapern verwendet.

### Entwickler-/Web-Scraper-freundliche Erfahrung
- 🎯 **Interaktive Web-Scraping-Shell**: Optionale integrierte IPython-Shell mit Scrapling-Integration, Shortcuts und neuen Tools zur Beschleunigung der Web-Scraping-Skriptentwicklung, wie das Konvertieren von Curl-Anfragen in Scrapling-Anfragen und das Anzeigen von Anfrageergebnissen in Ihrem Browser.
- 🚀 **Direkt vom Terminal aus verwenden**: Optional können Sie Scrapling verwenden, um eine URL zu scrapen, ohne eine einzige Codezeile zu schreiben!
- 🛠️ **Umfangreiche Navigations-API**: Erweiterte DOM-Traversierung mit Eltern-, Geschwister- und Kind-Navigationsmethoden.
- 🧬 **Verbesserte Textverarbeitung**: Integrierte Regex, Bereinigungsmethoden und optimierte String-Operationen.
- 📝 **Automatische Selektorgenerierung**: Robuste CSS/XPath-Selektoren für jedes Element generieren.
- 🔌 **Vertraute API**: Ähnlich wie Scrapy/BeautifulSoup mit denselben Pseudo-Elementen, die in Scrapy/Parsel verwendet werden.
- 📘 **Vollständige Typabdeckung**: Vollständige Type Hints für hervorragende IDE-Unterstützung und Code-Vervollständigung. Die gesamte Codebasis wird bei jeder Änderung automatisch mit **PyRight** und **MyPy** gescannt.
- 🔋 **Fertiges Docker-Image**: Mit jeder Veröffentlichung wird automatisch ein Docker-Image erstellt und gepusht, das alle Browser enthält.

## Erste Schritte

Hier ein kurzer Überblick über das, was Scrapling kann, ohne zu sehr ins Detail zu gehen.

### Grundlegende Verwendung
HTTP-Anfragen mit Session-Unterstützung
```python
from scrapling.fetchers import Fetcher, FetcherSession

with FetcherSession(impersonate='chrome') as session:  # Neueste Version von Chromes TLS-Fingerprint verwenden
    page = session.get('https://quotes.toscrape.com/', stealthy_headers=True)
    quotes = page.css('.quote .text::text').getall()

# Oder einmalige Anfragen verwenden
page = Fetcher.get('https://quotes.toscrape.com/')
quotes = page.css('.quote .text::text').getall()
```
Erweiterter Stealth-Modus
```python
from scrapling.fetchers import StealthyFetcher, StealthySession

with StealthySession(headless=True, solve_cloudflare=True) as session:  # Browser offen halten, bis Sie fertig sind
    page = session.fetch('https://nopecha.com/demo/cloudflare', google_search=False)
    data = page.css('#padded_content a').getall()

# Oder einmaligen Anfragenstil verwenden: öffnet den Browser für diese Anfrage und schließt ihn nach Abschluss
page = StealthyFetcher.fetch('https://nopecha.com/demo/cloudflare')
data = page.css('#padded_content a').getall()
```
Vollständige Browser-Automatisierung
```python
from scrapling.fetchers import DynamicFetcher, DynamicSession

with DynamicSession(headless=True, disable_resources=False, network_idle=True) as session:  # Browser offen halten, bis Sie fertig sind
    page = session.fetch('https://quotes.toscrape.com/', load_dom=False)
    data = page.xpath('//span[@class="text"]/text()').getall()  # XPath-Selektor, falls bevorzugt

# Oder einmaligen Anfragenstil verwenden: öffnet den Browser für diese Anfrage und schließt ihn nach Abschluss
page = DynamicFetcher.fetch('https://quotes.toscrape.com/')
data = page.css('.quote .text::text').getall()
```

### Spiders
Vollständige Crawler mit parallelen Anfragen, mehreren Session-Typen und Pause & Resume erstellen:
```python
from scrapling.spiders import Spider, Request, Response

class QuotesSpider(Spider):
    name = "quotes"
    start_urls = ["https://quotes.toscrape.com/"]
    concurrent_requests = 10

    async def parse(self, response: Response):
        for quote in response.css('.quote'):
            yield {
                "text": quote.css('.text::text').get(),
                "author": quote.css('.author::text').get(),
            }

        next_page = response.css('.next a')
        if next_page:
            yield response.follow(next_page[0].attrib['href'])

result = QuotesSpider().start()
print(f"{len(result.items)} Zitate gescrapt")
result.items.to_json("quotes.json")
```
Mehrere Session-Typen in einem einzigen Spider verwenden:
```python
from scrapling.spiders import Spider, Request, Response
from scrapling.fetchers import FetcherSession, AsyncStealthySession

class MultiSessionSpider(Spider):
    name = "multi"
    start_urls = ["https://example.com/"]

    def configure_sessions(self, manager):
        manager.add("fast", FetcherSession(impersonate="chrome"))
        manager.add("stealth", AsyncStealthySession(headless=True), lazy=True)

    async def parse(self, response: Response):
        for link in response.css('a::attr(href)').getall():
            # Geschützte Seiten über die Stealth-Session leiten
            if "protected" in link:
                yield Request(link, sid="stealth")
            else:
                yield Request(link, sid="fast", callback=self.parse)  # Expliziter Callback
```
Lange Crawls mit Checkpoints pausieren und fortsetzen, indem Sie den Spider so starten:
```python
QuotesSpider(crawldir="./crawl_data").start()
```
Drücken Sie Strg+C, um kontrolliert zu pausieren -- der Fortschritt wird automatisch gespeichert. Wenn Sie den Spider später erneut starten, übergeben Sie dasselbe `crawldir`, und er setzt dort fort, wo er aufgehört hat.

### Erweitertes Parsing & Navigation
```python
from scrapling.fetchers import Fetcher

# Umfangreiche Elementauswahl und Navigation
page = Fetcher.get('https://quotes.toscrape.com/')

# Zitate mit verschiedenen Auswahlmethoden abrufen
quotes = page.css('.quote')  # CSS-Selektor
quotes = page.xpath('//div[@class="quote"]')  # XPath
quotes = page.find_all('div', {'class': 'quote'})  # BeautifulSoup-Stil
# Gleich wie
quotes = page.find_all('div', class_='quote')
quotes = page.find_all(['div'], class_='quote')
quotes = page.find_all(class_='quote')  # und so weiter...
# Element nach Textinhalt finden
quotes = page.find_by_text('quote', tag='div')

# Erweiterte Navigation
quote_text = page.css('.quote')[0].css('.text::text').get()
quote_text = page.css('.quote').css('.text::text').getall()  # Verkettete Selektoren
first_quote = page.css('.quote')[0]
author = first_quote.next_sibling.css('.author::text')
parent_container = first_quote.parent

# Elementbeziehungen und Ähnlichkeit
similar_elements = first_quote.find_similar()
below_elements = first_quote.below_elements()
```
Sie können den Parser direkt verwenden, wenn Sie keine Websites abrufen möchten, wie unten gezeigt:
```python
from scrapling.parser import Selector

page = Selector("<html>...</html>")
```
Und es funktioniert genau auf die gleiche Weise!

### Beispiele für async Session-Verwaltung
```python
import asyncio
from scrapling.fetchers import FetcherSession, AsyncStealthySession, AsyncDynamicSession

async with FetcherSession(http3=True) as session:  # `FetcherSession` ist kontextbewusst und kann sowohl in sync- als auch in async-Mustern arbeiten
    page1 = session.get('https://quotes.toscrape.com/')
    page2 = session.get('https://quotes.toscrape.com/', impersonate='firefox135')

# Async-Session-Verwendung
async with AsyncStealthySession(max_pages=2) as session:
    tasks = []
    urls = ['https://example.com/page1', 'https://example.com/page2']

    for url in urls:
        task = session.fetch(url)
        tasks.append(task)

    print(session.get_pool_stats())  # Optional - Der Status des Browser-Tab-Pools (beschäftigt/frei/Fehler)
    results = await asyncio.gather(*tasks)
    print(session.get_pool_stats())
```

## CLI & Interaktive Shell

Scrapling enthält eine leistungsstarke Befehlszeilenschnittstelle:

[![asciicast](https://asciinema.org/a/736339.svg)](https://asciinema.org/a/736339)

Interaktive Web-Scraping-Shell starten
```bash
scrapling shell
```
Seiten direkt ohne Programmierung in eine Datei extrahieren (extrahiert standardmäßig den Inhalt im `body`-Tag). Wenn die Ausgabedatei mit `.txt` endet, wird der Textinhalt des Ziels extrahiert. Wenn sie mit `.md` endet, ist es eine Markdown-Darstellung des HTML-Inhalts; wenn sie mit `.html` endet, ist es der HTML-Inhalt selbst.
```bash
scrapling extract get 'https://example.com' content.md
scrapling extract get 'https://example.com' content.txt --css-selector '#fromSkipToProducts' --impersonate 'chrome'  # Alle Elemente, die dem CSS-Selektor '#fromSkipToProducts' entsprechen
scrapling extract fetch 'https://example.com' content.md --css-selector '#fromSkipToProducts' --no-headless
scrapling extract stealthy-fetch 'https://nopecha.com/demo/cloudflare' captchas.html --css-selector '#padded_content a' --solve-cloudflare
```

> [!NOTE]
> Es gibt viele zusätzliche Funktionen, aber wir möchten diese Seite prägnant halten, einschließlich des MCP-Servers und der interaktiven Web-Scraping-Shell. Schauen Sie sich die vollständige Dokumentation [hier](https://scrapling.readthedocs.io/en/latest/) an

## Leistungsbenchmarks

Scrapling ist nicht nur leistungsstark -- es ist auch blitzschnell. Die folgenden Benchmarks vergleichen Scraplings Parser mit den neuesten Versionen anderer beliebter Bibliotheken.

### Textextraktions-Geschwindigkeitstest (5000 verschachtelte Elemente)

| # |    Bibliothek     | Zeit (ms) | vs Scrapling |
|---|:-----------------:|:---------:|:------------:|
| 1 |     Scrapling     |   2.02    |     1.0x     |
| 2 |   Parsel/Scrapy   |   2.04    |     1.01     |
| 3 |     Raw Lxml      |   2.54    |    1.257     |
| 4 |      PyQuery      |   24.17   |     ~12x     |
| 5 |    Selectolax     |   82.63   |     ~41x     |
| 6 |  MechanicalSoup   |  1549.71  |   ~767.1x    |
| 7 |   BS4 with Lxml   |  1584.31  |   ~784.3x    |
| 8 | BS4 with html5lib |  3391.91  |   ~1679.1x   |


### Element-Ähnlichkeit & Textsuche-Leistung

Scraplings adaptive Element-Finding-Fähigkeiten übertreffen Alternativen deutlich:

| Bibliothek  | Zeit (ms) | vs Scrapling |
|-------------|:---------:|:------------:|
| Scrapling   |   2.39    |     1.0x     |
| AutoScraper |   12.45   |    5.209x    |


> Alle Benchmarks stellen Durchschnittswerte von über 100 Durchläufen dar. Siehe [benchmarks.py](https://github.com/D4Vinci/Scrapling/blob/main/benchmarks.py) für die Methodik.

## Installation

Scrapling erfordert Python 3.10 oder höher:

```bash
pip install scrapling
```

Diese Installation enthält nur die Parser-Engine und ihre Abhängigkeiten, ohne Fetcher oder Kommandozeilenabhängigkeiten.

### Optionale Abhängigkeiten

1. Wenn Sie eine der folgenden zusätzlichen Funktionen, die Fetcher oder ihre Klassen verwenden möchten, müssen Sie die Abhängigkeiten der Fetcher und ihre Browser-Abhängigkeiten wie folgt installieren:
    ```bash
    pip install "scrapling[fetchers]"

    scrapling install           # normal install
    scrapling install  --force  # force reinstall
    ```

    Dies lädt alle Browser zusammen mit ihren Systemabhängigkeiten und Fingerprint-Manipulationsabhängigkeiten herunter.

    Oder Sie können sie aus dem Code heraus installieren, anstatt einen Befehl auszuführen:
    ```python
    from scrapling.cli import install

    install([], standalone_mode=False)          # normal install
    install(["--force"], standalone_mode=False) # force reinstall
    ```

2. Zusätzliche Funktionen:
   - MCP-Server-Funktion installieren:
       ```bash
       pip install "scrapling[ai]"
       ```
   - Shell-Funktionen installieren (Web-Scraping-Shell und der `extract`-Befehl):
       ```bash
       pip install "scrapling[shell]"
       ```
   - Alles installieren:
       ```bash
       pip install "scrapling[all]"
       ```
   Denken Sie daran, dass Sie nach einem dieser Extras (falls noch nicht geschehen) die Browser-Abhängigkeiten mit `scrapling install` installieren müssen

### Docker
Sie können auch ein Docker-Image mit allen Extras und Browsern mit dem folgenden Befehl von DockerHub installieren:
```bash
docker pull pyd4vinci/scrapling
```
Oder laden Sie es aus der GitHub-Registry herunter:
```bash
docker pull ghcr.io/d4vinci/scrapling:latest
```
Dieses Image wird automatisch mit GitHub Actions und dem Hauptzweig des Repositorys erstellt und gepusht.

## Beitragen

Wir freuen uns über Beiträge! Bitte lesen Sie unsere [Beitragsrichtlinien](https://github.com/D4Vinci/Scrapling/blob/main/CONTRIBUTING.md), bevor Sie beginnen.

## Haftungsausschluss

> [!CAUTION]
> Diese Bibliothek wird nur zu Bildungs- und Forschungszwecken bereitgestellt. Durch die Nutzung dieser Bibliothek erklären Sie sich damit einverstanden, lokale und internationale Gesetze zum Daten-Scraping und Datenschutz einzuhalten. Die Autoren und Mitwirkenden sind nicht verantwortlich für Missbrauch dieser Software. Respektieren Sie immer die Nutzungsbedingungen von Websites und robots.txt-Dateien.

## 🎓 Zitierungen
Wenn Sie unsere Bibliothek für Forschungszwecke verwendet haben, zitieren Sie uns bitte mit der folgenden Referenz:
```text
  @misc{scrapling,
    author = {Karim Shoair},
    title = {Scrapling},
    year = {2024},
    url = {https://github.com/D4Vinci/Scrapling},
    note = {An adaptive Web Scraping framework that handles everything from a single request to a full-scale crawl!}
  }
```

## Lizenz

Diese Arbeit ist unter der BSD-3-Clause-Lizenz lizenziert.

## Danksagungen

Dieses Projekt enthält angepassten Code von:
- Parsel (BSD-Lizenz) -- Verwendet für das [translator](https://github.com/D4Vinci/Scrapling/blob/main/scrapling/core/translator.py)-Submodul

---
<div align="center"><small>Entworfen und hergestellt mit ❤️ von Karim Shoair.</small></div><br>
