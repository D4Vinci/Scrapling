---
title: "Scrapling: Web-Scraping-Framework für Python"
description: "Scrapling: Daten aus dem modernen Web einfach extrahieren."
---

<style>
.md-typeset h1 {
  display: none;
}
[data-md-color-scheme="default"] .only-dark { display: none; }
[data-md-color-scheme="slate"] .only-light { display: none; }
</style>

<br/>
<div align="center">
    <a href="index.html" alt="Titelbild">
        <img alt="Scrapling" src="assets/cover_light.svg" class="only-light">
        <img alt="Scrapling" src="assets/cover_dark.svg" class="only-dark">
    </a>
</div>

<h2 align="center"><i>Daten aus dem modernen Web einfach extrahieren</i></h2><br>

Scrapling ist ein Web-Scraping-Framework für Python. Es vereint schnelle HTTP-Anfragen, Stealth-Browser, die Auswertung von Seiten und paralleles Crawling in einer Bibliothek.

Extrahieren Sie Daten aus statischen Seiten, führen Sie JavaScript aus, bedienen Sie Websites und greifen Sie auf deren APIs zu. Erstellen Sie Crawler mit wiederverwendbaren Sitzungen, Proxy-Rotation, automatischen Wiederholungsversuchen, Pause und Fortsetzung sowie integriertem Datenexport.

Nutzen Sie Scrapling in Python, im Terminal oder mit Ihrem KI-Agenten über den MCP-Server und den Agent Skill. Es deckt den ganzen Ablauf ab: von wenigen Feldern bis zum Speichern einer ganzen Website als saubere Markdown-Dateien.

## Was Sie mit Scrapling machen können {#what-you-can-do-with-scrapling}

- **[Seiten abrufen und bedienen](fetching/choosing.md)**: Schnelle HTTP-Anfragen, Stealth-Browser, JavaScript-Ausführung, Umgang mit Cloudflare Turnstile und Interstitial, dauerhafte Sitzungen und Aufzeichnung von API-Antworten im Hintergrund.
- **[Seiten auswerten und Daten extrahieren](parsing/selection.md)**: Suche mit CSS, XPath, Text und regulären Ausdrücken, Wiederfinden von Elementen nach Änderungen der Seite, Suche nach ähnlichen Elementen und saubere Markdown-Ausgabe.
- **[Crawlen und exportieren](spiders/getting-started.md)**: Parallele Spider, Proxy-Rotation, Wiederholungsversuche, AutoThrottle, Pause und Fortsetzung, Streaming, fertige Vorlagen und Export nach JSON, JSONL, CSV und XML.
- **[Daten mit KI oder im Terminal extrahieren](ai/mcp-server.md)**: Ein MCP-Server zum Browsen und Extrahieren von Daten mit KI-Agenten, ein Agent Skill, CLI-Befehle und eine interaktive Shell.

Beginnen Sie mit einer einzelnen Seite:

```python
from scrapling.fetchers import Fetcher

page = Fetcher.get('https://quotes.toscrape.com/')
quotes = page.css('.quote .text::text').getall()
print(quotes)
```

Oder extrahieren Sie mehr Daten mit einem Spider:

```python
from scrapling.spiders import Spider, Response

class QuotesSpider(Spider):
    name = "quotes"
    start_urls = ["https://quotes.toscrape.com/"]

    async def parse(self, response: Response):
        for quote in response.css('.quote'):
            yield {
                "text": quote.css('.text::text').get(),
                "author": quote.css('.author::text').get(),
            }

result = QuotesSpider().start()
print(len(result.items))
result.items.to_json("quotes.json")
```

Dieses Beispiel gibt `10` aus und speichert die Zitate und ihre Autoren in `quotes.json`.

## Hauptsponsoren {#top-sponsors}

--8<-- "sponsors.html"

<i><sub>Möchten Sie hier werben? Klicken Sie [hier](https://github.com/sponsors/D4Vinci), wählen Sie ein Angebot und nutzen Sie die Vorteile.</sub></i>

## Wichtige Funktionen {#key-features}

### Spider: ein vollständiges Crawling-Framework {#spiders-a-full-crawling-framework}
- 🕷️ **Spider-API ähnlich wie Scrapy**: Definieren Sie Spider mit `start_urls`, asynchronen `parse`-Callbacks sowie `Request`- und `Response`-Objekten.
- ⚡ **Paralleles Crawling**: Legen Sie die Anzahl gleichzeitiger Anfragen, die Grenzen pro Domain und die Wartezeit zwischen Downloads fest.
- 🔄 **Mehrere Sitzungen**: Nutzen Sie HTTP-Anfragen und Stealth-Browser ohne grafische Oberfläche im selben Spider. Leiten Sie Anfragen über die ID an unterschiedliche Sitzungen weiter.
- 💾 **Pause und Fortsetzung**: Speichern Sie ausstehende Anfragen und besuchte URLs mit `crawldir`. Drücken Sie Strg+C, um sicher anzuhalten, und starten Sie mit demselben Ordner erneut.
- 📡 **Ergebnisse als Stream**: Empfangen Sie Elemente direkt nach dem Extrahieren mit `async for item in spider.stream()`, zusammen mit Statistiken in Echtzeit. Das eignet sich für Oberflächen, Datenverarbeitung und lange Crawls.
- 🛡️ **Blockierte Anfragen erkennen**: Erkennen und wiederholen Sie blockierte Anfragen automatisch. Sie können das Verhalten anpassen.
- 🚦 **AutoThrottle**: Der Spider passt die Wartezeit pro Domain an die Antwortgeschwindigkeit der Website an. Blockiert oder begrenzt die Website Anfragen, verdoppelt er die Wartezeit oder hält die von `Retry-After` angegebene Zeit ein. Danach beschleunigt er wieder.
- 🤖 **robots.txt beachten**: Aktivieren Sie `robots_txt_obey`, um die Vorgaben `Disallow`, `Crawl-delay` und `Request-rate` zu beachten. Die Angaben werden pro Domain zwischengespeichert.
- 🧪 **Entwicklungsmodus**: Speichern Sie Antworten beim ersten Lauf auf der Festplatte und nutzen Sie sie danach erneut. So können Sie `parse()` anpassen, ohne neue Anfragen an die Server zu senden.
- 🧩 **Fertige Spider-Vorlagen**: Nutzen Sie `CrawlSpider`, um Links nach Regeln zu folgen, `SitemapSpider` für Crawls über Sitemaps oder robots.txt, `XMLFeedSpider` und `CSVFeedSpider` zum Lesen von XML-, RSS- und CSV-Feeds sowie `ShopifySpider` zum Sammeln von Produkten aus öffentlichen Shopify-Shops, mit einem Element pro Variante.
- 🔗 **Links extrahieren**: `LinkExtractor` erlaubt oder verwirft Links anhand von Mustern, filtert Domains und Dateiendungen, begrenzt die Suche mit CSS oder XPath und vereinheitlicht URLs. Nutzen Sie ihn mit den Vorlagen oder einzeln.
- 📦 **Integrierter Export**: Exportieren Sie Ergebnisse mit Hooks und Ihrer eigenen Datenverarbeitung oder mit den integrierten Formaten JSON, JSONL, CSV und XML: `result.items.to_json()`, `to_jsonl()`, `to_csv()` und `to_xml()`.

### Seiten mit Sitzungen abrufen {#advanced-websites-fetching-with-session-support}
- **HTTP-Anfragen**: Senden Sie schnelle und unauffällige HTTP-Anfragen mit `Fetcher`. Sie können TLS-Fingerprints und Header eines Browsers nachbilden und HTTP/3 nutzen.
- **Dynamisches Laden**: Rufen Sie dynamische Websites mit vollständiger Browserautomatisierung über `StealthyFetcher` ab. Er unterstützt das Chromium von Playwright und Google Chrome.
- **Antibot-Systeme umgehen**: `StealthyFetcher` verbirgt die Automatisierung und bildet Browser-Fingerprints nach. Er kann verschiedene Arten von Cloudflare Turnstile und Interstitial automatisch lösen.
- **Sitzungen verwalten**: `FetcherSession` und `StealthySession` behalten Cookies und den Zustand zwischen Anfragen bei.
- **Proxy-Rotation**: `ProxyRotator` wechselt Proxys zyklisch oder nach eigenen Regeln in allen Sitzungstypen. Sie können auch einen Proxy für eine einzelne Anfrage wählen.
- **Domains und Werbung blockieren**: Blockieren Sie Anfragen an bestimmte Domains und deren Subdomains, oder aktivieren Sie den Werbeblocker der Browser-Fetcher. Er umfasst etwa 3.500 bekannte Werbe- und Tracking-Domains.
- **DNS-Lecks verhindern**: Aktivieren Sie DNS-over-HTTPS, um DNS-Anfragen über den DoH-Dienst von Cloudflare zu senden und Lecks bei der Nutzung von Proxys zu verhindern.
- **Entfernte Browser**: Verbinden Sie sich über CDP und `cdp_url` mit einem laufenden Browser, auf Ihrem Computer, einem anderen Server oder bei einem Browserdienst. Mit `executable_path` können Sie auch Ihre eigene Chromium-Version für jeden Browser-Fetcher verwenden.
- **API-Antworten im Hintergrund aufzeichnen**: Aktivieren Sie `record_requests=True` in einer Browsersitzung und suchen Sie gespeicherte Antworten mit `session.network.search(limit=None)`. Lesen Sie API-Daten und HTTP-Fehler aus mehreren Seitenaufrufen, ohne die Anfragen zu wiederholen. Der Verlauf ist in seiner Größe begrenzt und speichert den Inhalt von Textantworten.
- **Asynchroner Betrieb**: Alle Fetcher lassen sich asynchron nutzen. Dafür gibt es eigene Sitzungsklassen.

### Seiten auswerten und Daten extrahieren {#parsing-and-data-extraction}
- 🔄 **Elemente wiederfinden**: Finden Sie Elemente nach Änderungen der Website mit Algorithmen zur Ähnlichkeitssuche wieder.
- 🎯 **Flexible Auswahl**: Nutzen Sie CSS, XPath, Filter, Text, reguläre Ausdrücke und mehr.
- 🔍 **Ähnliche Elemente**: Finden Sie automatisch Elemente, die den bereits gefundenen ähneln.

### KI-Funktionen {#ai-features}
- 🤖 **MCP-Server**: Ermöglicht Assistenten und KI-Agenten wie Claude und Cursor, Daten mit Scrapling zu extrahieren. Dazu dienen HTTP-Anfragen, Browseraktionen, Screenshots, ein gespeicherter Anmeldezustand und API-Antworten im Hintergrund. Er nutzt unseren Stealth-Browser und Werkzeuge, mit denen geeignete Modelle CAPTCHAs lösen können, zusätzlich zum Cloudflare-Löser. Er verringert den an das Modell gesendeten Inhalt, blockiert Werbung und schützt vor Prompt Injection. Entfernte Browser über CDP und HTTP-Verbindungen mit Authentifizierungsoptionen sind ebenfalls möglich. ([Demovideo](https://www.youtube.com/watch?v=qyFk3ZNwOxE))
- 🧠 **Agent Skill**: Ein [Agent Skill](ai/agent-skill.md) zum Installieren, der Coding-Agenten die Bibliothek erklärt. So schreiben sie Code, der zur aktuellen API passt.
- 📚 **Markdown für RAG**: Wandeln Sie eine Seite mit einer Zeile (`page.markdown()`) in sauberes Markdown für Sprachmodelle um, oder speichern Sie mit der Vorlage `ContentSpider` eine ganze Website als Markdown-Dateien. Dafür ist kein Sprachmodell nötig. ([Dokumentation](ai/building-rag-systems.md))

### Schnell und im Alltag erprobt {#high-performance-battle-tested-architecture}
- 🚀 **Hohe Geschwindigkeit**: Optimierte Leistung, die die meisten Web-Scraping-Bibliotheken für Python übertrifft.
- 🔋 **Geringer Speicherbedarf**: Optimierte Datenstrukturen und Laden bei Bedarf.
- ⚡ **Schnelle JSON-Ausgabe**: 10-mal schneller als die Standardbibliothek.
- 🏗️ **In der Praxis getestet**: Tests decken 92 % von Scrapling ab, und der gesamte Code hat Typannotationen. Hunderte Menschen haben es im letzten Jahr täglich zur Datenextraktion verwendet.

### Werkzeuge für Entwicklung und Datenextraktion {#developerweb-scraper-friendly-experience}
- 🎯 **Interaktive Shell**: Eine optionale IPython-Shell mit Scrapling, Kurzbefehlen und Werkzeugen für die schnelle Entwicklung von Skripten. Wandeln Sie curl-Anfragen in Scrapling-Anfragen um und zeigen Sie Ergebnisse im Browser an.
- 🚀 **Nutzung im Terminal**: Extrahieren Sie die Daten einer URL, ohne Code zu schreiben.
- 🛠️ **Navigation im DOM**: Greifen Sie auf Eltern-, Geschwister- und Kindelemente zu.
- 🧬 **Textverarbeitung**: Reguläre Ausdrücke, Textbereinigung und optimierte Arbeit mit Zeichenketten.
- 📝 **Selektoren erzeugen**: Erstellen Sie zuverlässige CSS- und XPath-Selektoren für jedes Element.
- 🔌 **Vertraute API**: Ähnlich wie Scrapy und BeautifulSoup, mit denselben Pseudoelementen wie Scrapy und Parsel.
- 🤝 **Direkte Integration mit Scrapy**: Ergänzen Sie einen Callback um den Dekorator `scrapling_response`, um die bereits abgerufenen Antworten mit dem Scrapling-Parser auszuwerten. Sie müssen Ihr Programm nicht neu schreiben.
- 📘 **Vollständige Typannotationen**: Sie helfen dem Editor, Code zu prüfen und zu vervollständigen. Der gesamte Code wird bei jeder Änderung automatisch mit **PyRight** und **MyPy** geprüft.
- 🔋 **Fertiges Docker-Image**: Bei jeder Version wird automatisch ein Docker-Image mit allen Browsern erstellt und veröffentlicht.


## Sterne auf GitHub {#star-history}
Die Zahl der GitHub-Sterne von Scrapling wächst seit seiner Veröffentlichung, wie die Grafik zeigt.

<div id="chartContainer">
  <a href="https://github.com/D4Vinci/Scrapling">
    <img id="chartImage" alt="Verlauf der GitHub-Sterne" loading="lazy" src="https://api.star-history.com/svg?repos=D4Vinci/Scrapling&type=Date" height="400"/>
  </a>
</div>

<script>
const observer = new MutationObserver((mutations) => {
  mutations.forEach((mutation) => {
    if (mutation.attributeName === 'data-md-color-media') {
      const colorMedia = document.body.getAttribute('data-md-color-media');
      const isDarkScheme = document.body.getAttribute('data-md-color-scheme') === 'slate';
      const chartImg = document.querySelector('#chartImage');
      const baseUrl = 'https://api.star-history.com/svg?repos=D4Vinci/Scrapling&type=Date';
      
      if (colorMedia === '(prefers-color-scheme)' ? isDarkScheme : colorMedia.includes('dark')) {
        chartImg.src = `${baseUrl}&theme=dark`;
      } else {
        chartImg.src = baseUrl;
      }
    }
  });
});

observer.observe(document.body, {
  attributes: true,
  attributeFilter: ['data-md-color-media', 'data-md-color-scheme']
});
</script>


## Installation {#installation}
Scrapling benötigt Python 3.10 oder neuer:

```bash
pip install scrapling
```

!!! warning "Achtung"

    Dieser Befehl installiert nur den Parser und seine Abhängigkeiten, ohne Fetcher oder Werkzeuge für die Kommandozeile. Wenn Sie nur das installieren, führt ein Import aus `scrapling.fetchers` oder `scrapling.spiders`, wie in den Beispielen oben, zu `ModuleNotFoundError`. Für Fetcher oder Spider müssen Sie zuerst die Fetcher-Abhängigkeiten wie unten gezeigt installieren.

### Optionale Abhängigkeiten {#optional-dependencies}

1. Für Fetcher, deren Klassen oder die folgenden Zusatzfunktionen installieren Sie die Abhängigkeiten der Fetcher und Browser:
    ```bash
    pip install "scrapling[fetchers]"
    
    scrapling install           # normal install
    scrapling install  --force  # force reinstall
    ```

    Dadurch werden alle Browser, ihre Systemabhängigkeiten und die Werkzeuge zum Ändern der Browser-Fingerprints heruntergeladen.

    Sie können sie auch aus Python installieren, statt einen Befehl auszuführen:
    ```python
    from scrapling.cli import install
    
    install([], standalone_mode=False)          # normal install
    install(["--force"], standalone_mode=False) # force reinstall
    ```

2. Zusatzfunktionen:


     - Den MCP-Server installieren:
       ```bash
       pip install "scrapling[ai]"
       ```
     - Die Abhängigkeiten zum [Aufbau von RAG-Systemen](ai/building-rag-systems.md) installieren:
       ```bash
       pip install "scrapling[rag]"
       ```
     - Die interaktive Shell und den Befehl `extract` installieren:
         ```bash
         pip install "scrapling[shell]"
         ```
     - Alles installieren:
         ```bash
         pip install "scrapling[all]"
         ```
   Führen Sie `scrapling install` aus, wenn Sie Browser-Fetcher nutzen möchten. HTTP-Anfragen benötigen keinen Browser.

### Docker {#docker}
Sie können auch ein Docker-Image mit allen Extras und Browsern von DockerHub herunterladen:
```bash
docker pull pyd4vinci/scrapling
```
Oder aus der GitHub-Registry herunterladen:
```bash
docker pull ghcr.io/d4vinci/scrapling:latest
```
Das Image wird aus dem Hauptbranch des Repositorys erstellt und von GitHub Actions automatisch veröffentlicht.

## Aufbau der Dokumentation {#how-the-documentation-is-organized}
Die Scrapling-Dokumentation ist umfangreich. Deshalb folgen wir dem [Diátaxis-Modell für Dokumentation](https://diataxis.fr/).

## Unterstützung {#support}

Wenn Ihnen Scrapling gefällt und Sie die Entwicklung unterstützen möchten:

- ⭐ Geben Sie dem [GitHub-Repository](https://github.com/D4Vinci/Scrapling) einen Stern.
- 🚀 Folgen Sie uns auf [Twitter](https://x.com/Scrapling_dev) und treten Sie dem [Discord-Server](https://discord.gg/EMgGbDceNQ) bei.
- 💝 Sie können [das Projekt sponsern oder mir einen Kaffee spendieren](donate.md). :wink:
- 🐛 Melden Sie Fehler und schlagen Sie Funktionen auf [GitHub Issues](https://github.com/D4Vinci/Scrapling/issues) vor.

## Lizenz {#license}

Dieses Projekt nutzt die BSD-3-Lizenz. Weitere Angaben stehen in der Datei [LICENSE](https://github.com/D4Vinci/Scrapling/blob/main/LICENSE).
