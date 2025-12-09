<p align=center>
  <br>
  <a href="https://scrapling.readthedocs.io/en/latest/" target="_blank"><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/poster.png" style="width: 50%; height: 100%;" alt="main poster"/></a>
  <br>
  <i><code>Einfaches, müheloses Web Scraping, wie es sein sollte!</code></i>
</p>
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
    <a href="https://scrapling.readthedocs.io/en/latest/parsing/selection/">
        Auswahlmethoden
    </a>
    ·
    <a href="https://scrapling.readthedocs.io/en/latest/fetching/choosing/">
        Fetcher wählen
    </a>
    ·
    <a href="https://scrapling.readthedocs.io/en/latest/cli/overview/">
        CLI
    </a>
    ·
    <a href="https://scrapling.readthedocs.io/en/latest/ai/mcp-server/">
        MCP-Modus
    </a>
    ·
    <a href="https://scrapling.readthedocs.io/en/latest/tutorials/migrating_from_beautifulsoup/">
        Migration von Beautifulsoup
    </a>
</p>

**Hören Sie auf, gegen Anti-Bot-Systeme zu kämpfen. Hören Sie auf, Selektoren nach jedem Website-Update neu zu schreiben.**

Scrapling ist nicht nur eine weitere Web-Scraping-Bibliothek. Es ist die erste **adaptive** Scraping-Bibliothek, die von Website-Änderungen lernt und sich mit ihnen weiterentwickelt. Während andere Bibliotheken brechen, wenn Websites ihre Struktur aktualisieren, lokalisiert Scrapling Ihre Elemente automatisch neu und hält Ihre Scraper am Laufen.

Für das moderne Web entwickelt, bietet Scrapling **seine eigene schnelle Parsing-Engine** und Fetcher, um alle Web-Scraping-Herausforderungen zu bewältigen, denen Sie begegnen oder begegnen werden. Von Web Scrapern für Web Scraper und normale Benutzer entwickelt, ist für jeden etwas dabei.

```python
>> from scrapling.fetchers import Fetcher, AsyncFetcher, StealthyFetcher, DynamicFetcher
>> StealthyFetcher.adaptive = True
# Holen Sie sich Website-Quellcode unter dem Radar!
>> page = StealthyFetcher.fetch('https://example.com', headless=True, network_idle=True)
>> print(page.status)
200
>> products = page.css('.product', auto_save=True)  # Scrapen Sie Daten, die Website-Designänderungen überleben!
>> # Später, wenn sich die Website-Struktur ändert, übergeben Sie `adaptive=True`
>> products = page.css('.product', adaptive=True)  # und Scrapling findet sie trotzdem!
```

# Sponsoren 

<!-- sponsors -->

<a href="https://www.scrapeless.com/en?utm_source=official&utm_term=scrapling" target="_blank" title="Effortless Web Scraping Toolkit for Business and Developers"><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/scrapeless.jpg"></a>
<a href="https://www.thordata.com/?ls=github&lk=github" target="_blank" title="Unblockable proxies and scraping infrastructure, delivering real-time, reliable web data to power AI models and workflows."><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/thordata.jpg"></a>
<a href="https://evomi.com?utm_source=github&utm_medium=banner&utm_campaign=d4vinci-scrapling" target="_blank" title="Evomi is your Swiss Quality Proxy Provider, starting at $0.49/GB"><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/evomi.png"></a>
<a href="https://serpapi.com/?utm_source=scrapling" target="_blank" title="Scrape Google and other search engines with SerpApi"><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/SerpApi.png"></a>
<a href="https://visit.decodo.com/Dy6W0b" target="_blank" title="Try the Most Efficient Residential Proxies for Free"><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/decodo.png"></a>
<a href="https://petrosky.io/d4vinci" target="_blank" title="PetroSky delivers cutting-edge VPS hosting."><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/petrosky.png"></a>
<a href="https://www.swiftproxy.net/" target="_blank" title="Unlock Reliable Proxy Services with Swiftproxy!"><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/swiftproxy.png"></a>
<a href="https://www.rapidproxy.io/?ref=d4v" target="_blank" title="Affordable Access to the Proxy World – bypass CAPTCHAs blocks, and avoid additional costs."><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/rapidproxy.jpg"></a>
<a href="https://browser.cash/?utm_source=D4Vinci&utm_medium=referral" target="_blank" title="Browser Automation & AI Browser Agent Platform"><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/browserCash.png"></a>

<!-- /sponsors -->

<i><sub>Möchten Sie Ihre Anzeige hier zeigen? Klicken Sie [hier](https://github.com/sponsors/D4Vinci) und wählen Sie die Stufe, die zu Ihnen passt!</sub></i>

---

## Hauptmerkmale

### Erweiterte Website-Abruf mit Sitzungsunterstützung
- **HTTP-Anfragen**: Schnelle und heimliche HTTP-Anfragen mit der `Fetcher`-Klasse. Kann Browser-TLS-Fingerabdrücke, Header imitieren und HTTP3 verwenden.
- **Dynamisches Laden**: Abrufen dynamischer Websites mit vollständiger Browser-Automatisierung über die `DynamicFetcher`-Klasse, die Playwrights Chromium, echtes Chrome und benutzerdefinierten Stealth-Modus unterstützt.
- **Anti-Bot-Umgehung**: Erweiterte Stealth-Fähigkeiten mit `StealthyFetcher` unter Verwendung einer modifizierten Firefox-Version und Fingerabdruck-Spoofing. Kann alle Arten von Cloudflares Turnstile und Interstitial einfach mit Automatisierung umgehen.
- **Sitzungsverwaltung**: Persistente Sitzungsunterstützung mit den Klassen `FetcherSession`, `StealthySession` und `DynamicSession` für Cookie- und Zustandsverwaltung über Anfragen hinweg.
- **Async-Unterstützung**: Vollständige Async-Unterstützung über alle Fetcher und dedizierte Async-Sitzungsklassen hinweg.

### Adaptives Scraping & KI-Integration
- 🔄 **Intelligente Element-Verfolgung**: Elemente nach Website-Änderungen mit intelligenten Ähnlichkeitsalgorithmen neu lokalisieren.
- 🎯 **Intelligente flexible Auswahl**: CSS-Selektoren, XPath-Selektoren, filterbasierte Suche, Textsuche, Regex-Suche und mehr.
- 🔍 **Ähnliche Elemente finden**: Elemente, die gefundenen Elementen ähnlich sind, automatisch lokalisieren.
- 🤖 **MCP-Server für die Verwendung mit KI**: Integrierter MCP-Server für KI-unterstütztes Web Scraping und Datenextraktion. Der MCP-Server verfügt über benutzerdefinierte, leistungsstarke Funktionen, die Scrapling nutzen, um gezielten Inhalt zu extrahieren, bevor er an die KI (Claude/Cursor/etc.) übergeben wird, wodurch Vorgänge beschleunigt und Kosten durch Minimierung der Token-Nutzung gesenkt werden. ([Demo-Video](https://www.youtube.com/watch?v=qyFk3ZNwOxE))

### Hochleistungs- und praxiserprobte Architektur
- 🚀 **Blitzschnell**: Optimierte Leistung, die die meisten Python-Scraping-Bibliotheken übertrifft.
- 🔋 **Speichereffizient**: Optimierte Datenstrukturen und Lazy Loading für einen minimalen Speicher-Footprint.
- ⚡ **Schnelle JSON-Serialisierung**: 10x schneller als die Standardbibliothek.
- 🏗️ **Praxiserprobt**: Scrapling hat nicht nur eine Testabdeckung von 92% und eine vollständige Type-Hints-Abdeckung, sondern wird seit dem letzten Jahr täglich von Hunderten von Web Scrapern verwendet.

### Entwickler/Web-Scraper-freundliche Erfahrung
- 🎯 **Interaktive Web-Scraping-Shell**: Optionale integrierte IPython-Shell mit Scrapling-Integration, Shortcuts und neuen Tools zur Beschleunigung der Web-Scraping-Skriptentwicklung, wie das Konvertieren von Curl-Anfragen in Scrapling-Anfragen und das Anzeigen von Anfrageergebnissen in Ihrem Browser.
- 🚀 **Direkt vom Terminal aus verwenden**: Optional können Sie Scrapling verwenden, um eine URL zu scrapen, ohne eine einzige Codezeile zu schreiben!
- 🛠️ **Umfangreiche Navigations-API**: Erweiterte DOM-Traversierung mit Eltern-, Geschwister- und Kind-Navigationsmethoden.
- 🧬 **Verbesserte Textverarbeitung**: Integrierte Regex, Bereinigungsmethoden und optimierte String-Operationen.
- 📝 **Automatische Selektorgenerierung**: Robuste CSS/XPath-Selektoren für jedes Element generieren.
- 🔌 **Vertraute API**: Ähnlich wie Scrapy/BeautifulSoup mit denselben Pseudo-Elementen, die in Scrapy/Parsel verwendet werden.
- 📘 **Vollständige Typabdeckung**: Vollständige Type Hints für hervorragende IDE-Unterstützung und Code-Vervollständigung.
- 🔋 **Fertiges Docker-Image**: Mit jeder Veröffentlichung wird automatisch ein Docker-Image erstellt und gepusht, das alle Browser enthält.

## Erste Schritte

### Grundlegende Verwendung
```python
from scrapling.fetchers import Fetcher, StealthyFetcher, DynamicFetcher
from scrapling.fetchers import FetcherSession, StealthySession, DynamicSession

# HTTP-Anfragen mit Sitzungsunterstützung
with FetcherSession(impersonate='chrome') as session:  # Verwenden Sie die neueste Version von Chromes TLS-Fingerabdruck
    page = session.get('https://quotes.toscrape.com/', stealthy_headers=True)
    quotes = page.css('.quote .text::text')

# Oder verwenden Sie einmalige Anfragen
page = Fetcher.get('https://quotes.toscrape.com/')
quotes = page.css('.quote .text::text')

# Erweiterter Stealth-Modus (Browser offen halten, bis Sie fertig sind)
with StealthySession(headless=True, solve_cloudflare=True) as session:
    page = session.fetch('https://nopecha.com/demo/cloudflare', google_search=False)
    data = page.css('#padded_content a')

# Oder verwenden Sie den einmaligen Anfragenstil, öffnet den Browser für diese Anfrage und schließt ihn dann nach Abschluss
page = StealthyFetcher.fetch('https://nopecha.com/demo/cloudflare')
data = page.css('#padded_content a')
    
# Vollständige Browser-Automatisierung (Browser offen halten, bis Sie fertig sind)
with DynamicSession(headless=True) as session:
    page = session.fetch('https://quotes.toscrape.com/', network_idle=True)
    quotes = page.css('.quote .text::text')

# Oder verwenden Sie den einmaligen Anfragenstil
page = DynamicFetcher.fetch('https://quotes.toscrape.com/', network_idle=True)
quotes = page.css('.quote .text::text')
```

### Elementauswahl
```python
# CSS-Selektoren
page.css('a::text')                      # Text extrahieren
page.css('a::attr(href)')                # Attribute extrahieren
page.css('a', recursive=False)           # Nur direkte Elemente
page.css('a', auto_save=True)            # Elementpositionen automatisch speichern

# XPath
page.xpath('//a/text()')

# Flexible Suche
page.find_by_text('Python', first_match=True)  # Nach Text suchen
page.find_by_regex(r'\d{4}')                   # Nach Regex-Muster suchen
page.find('div', {'class': 'container'})       # Nach Attributen suchen

# Navigation
element.parent                           # Elternelement abrufen
element.next_sibling                     # Nächstes Geschwister abrufen
element.children                         # Kindelemente abrufen

# Ähnliche Elemente
similar = page.get_similar(element)      # Ähnliche Elemente finden

# Adaptives Scraping
saved_elements = page.css('.product', auto_save=True)
# Später, wenn sich die Website ändert:
page.css('.product', adaptive=True)      # Elemente mithilfe gespeicherter Positionen finden
```

### Sitzungsverwendung
```python
from scrapling.fetchers import FetcherSession, AsyncFetcherSession

# Synchrone Sitzung
with FetcherSession() as session:
    # Cookies werden automatisch beibehalten
    page1 = session.get('https://quotes.toscrape.com/login')
    page2 = session.post('https://quotes.toscrape.com/login', data={'username': 'admin', 'password': 'admin'})
    
    # Bei Bedarf Browser-Fingerabdruck wechseln
    page2 = session.get('https://quotes.toscrape.com/', impersonate='firefox135')

# Async-Sitzungsverwendung
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

Scrapling v0.3 enthält eine leistungsstarke Befehlszeilenschnittstelle:

[![asciicast](https://asciinema.org/a/736339.svg)](https://asciinema.org/a/736339)

```bash
# Interaktive Web-Scraping-Shell starten
scrapling shell

# Seiten direkt ohne Programmierung in eine Datei extrahieren (Extrahiert standardmäßig den Inhalt im `body`-Tag)
# Wenn die Ausgabedatei mit `.txt` endet, wird der Textinhalt des Ziels extrahiert.
# Wenn sie mit `.md` endet, ist es eine Markdown-Darstellung des HTML-Inhalts, und `.html` ist direkt der HTML-Inhalt.
scrapling extract get 'https://example.com' content.md
scrapling extract get 'https://example.com' content.txt --css-selector '#fromSkipToProducts' --impersonate 'chrome'  # Alle Elemente, die dem CSS-Selektor '#fromSkipToProducts' entsprechen
scrapling extract fetch 'https://example.com' content.md --css-selector '#fromSkipToProducts' --no-headless
scrapling extract stealthy-fetch 'https://nopecha.com/demo/cloudflare' captchas.html --css-selector '#padded_content a' --solve-cloudflare
```

> [!NOTE]
> Es gibt viele zusätzliche Funktionen, aber wir möchten diese Seite prägnant halten, wie den MCP-Server und die interaktive Web-Scraping-Shell. Schauen Sie sich die vollständige Dokumentation [hier](https://scrapling.readthedocs.io/en/latest/) an

## Leistungsbenchmarks

Scrapling ist nicht nur leistungsstark – es ist auch blitzschnell, und die Updates seit Version 0.3 haben außergewöhnliche Leistungsverbesserungen bei allen Operationen gebracht.

### Textextraktions-Geschwindigkeitstest (5000 verschachtelte Elemente)

| # |    Bibliothek     | Zeit (ms) | vs Scrapling | 
|---|:-----------------:|:---------:|:------------:|
| 1 |     Scrapling     |   1.99    |     1.0x     |
| 2 |   Parsel/Scrapy   |   2.01    |    1.01x     |
| 3 |     Raw Lxml      |    2.5    |    1.256x    |
| 4 |      PyQuery      |   22.93   |    ~11.5x    |
| 5 |    Selectolax     |   80.57   |    ~40.5x    |
| 6 |   BS4 with Lxml   |  1541.37  |   ~774.6x    |
| 7 |  MechanicalSoup   |  1547.35  |   ~777.6x    |
| 8 | BS4 with html5lib |  3410.58  |   ~1713.9x   |


### Element-Ähnlichkeit & Textsuche-Leistung

Scraplings adaptive Element-Finding-Fähigkeiten übertreffen Alternativen deutlich:

| Bibliothek  | Zeit (ms) | vs Scrapling |
|-------------|:---------:|:------------:|
| Scrapling   |   2.46    |     1.0x     |
| AutoScraper |   13.3    |    5.407x    |


> Alle Benchmarks stellen Durchschnittswerte von über 100 Durchläufen dar. Siehe [benchmarks.py](https://github.com/D4Vinci/Scrapling/blob/main/benchmarks.py) für die Methodik.

## Installation

Scrapling erfordert Python 3.10 oder höher:

```bash
pip install scrapling
```

Ab v0.3.2 enthält diese Installation nur die Parser-Engine und ihre Abhängigkeiten, ohne Fetcher oder Kommandozeilenabhängigkeiten.

### Optionale Abhängigkeiten

1. Wenn Sie eine der folgenden zusätzlichen Funktionen, die Fetcher oder ihre Klassen verwenden möchten, müssen Sie die Abhängigkeiten der Fetcher installieren und dann ihre Browser-Abhängigkeiten mit
    ```bash
    pip install "scrapling[fetchers]"
    
    scrapling install
    ```

    Dies lädt alle Browser mit ihren Systemabhängigkeiten und Fingerabdruck-Manipulationsabhängigkeiten herunter.

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
Dieses Image wird automatisch über GitHub Actions im Hauptzweig des Repositorys erstellt und gepusht.

## Beitragen

Wir freuen uns über Beiträge! Bitte lesen Sie unsere [Beitragsrichtlinien](https://github.com/D4Vinci/Scrapling/blob/main/CONTRIBUTING.md), bevor Sie beginnen.

## Haftungsausschluss

> [!CAUTION]
> Diese Bibliothek wird nur zu Bildungs- und Forschungszwecken bereitgestellt. Durch die Nutzung dieser Bibliothek erklären Sie sich damit einverstanden, lokale und internationale Gesetze zum Daten-Scraping und Datenschutz einzuhalten. Die Autoren und Mitwirkenden sind nicht verantwortlich für Missbrauch dieser Software. Respektieren Sie immer die Nutzungsbedingungen von Websites und robots.txt-Dateien.

## Lizenz

Diese Arbeit ist unter der BSD-3-Clause-Lizenz lizenziert.

## Danksagungen

Dieses Projekt enthält angepassten Code von:
- Parsel (BSD-Lizenz) – Verwendet für [translator](https://github.com/D4Vinci/Scrapling/blob/main/scrapling/core/translator.py)-Submodul

## Dank und Referenzen

- [Daijros](https://github.com/daijro) brillante Arbeit an [BrowserForge](https://github.com/daijro/browserforge) und [Camoufox](https://github.com/daijro/camoufox)
- [Vinyzus](https://github.com/Vinyzu) brillante Arbeit an [Botright](https://github.com/Vinyzu/Botright) und [PatchRight](https://github.com/Kaliiiiiiiiii-Vinyzu/patchright)
- [brotector](https://github.com/kaliiiiiiiiii/brotector) für Browser-Erkennungs-Umgehungstechniken
- [fakebrowser](https://github.com/kkoooqq/fakebrowser) und [BotBrowser](https://github.com/botswin/BotBrowser) für Fingerprinting-Forschung

---
<div align="center"><small>Entworfen und hergestellt mit ❤️ von Karim Shoair.</small></div><br>