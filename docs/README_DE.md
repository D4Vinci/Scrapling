<!-- mcp-name: io.github.D4Vinci/Scrapling -->

<h1 align="center">
    <a href="https://scrapling.readthedocs.io/de/latest/">
        <picture>
          <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/docs/assets/cover_dark.svg?sanitize=true">
          <img alt="Scrapling-Titelbild" src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/docs/assets/cover_light.svg?sanitize=true">
        </picture>
    </a>
    <br>
    <small>Daten aus dem modernen Web einfach extrahieren</small>
</h1>

<p align="center">
    <a href="https://github.com/D4Vinci/Scrapling/actions/workflows/tests.yml" alt="Tests">
        <img alt="Tests" src="https://github.com/D4Vinci/Scrapling/actions/workflows/tests.yml/badge.svg"></a>
    <a href="https://badge.fury.io/py/Scrapling" alt="Version auf PyPI">
        <img alt="Version auf PyPI" src="https://badge.fury.io/py/Scrapling.svg"></a>
    <a href="https://hub.docker.com/r/pyd4vinci/scrapling" target="_blank">
        <img alt="Docker-Downloads" src="https://img.shields.io/docker/pulls/pyd4vinci/scrapling?labelColor=%20%23FDB062&logo=Docker&labelColor=%20%23528bff"></a>
    <a href="https://clickpy.clickhouse.com/dashboard/scrapling" rel="nofollow"><img src="https://img.shields.io/pypi/dm/scrapling" alt="Paket-Downloads auf PyPI"></a>
    <a href="https://scrapling.readthedocs.io/de/latest/ai/agent-skill.html" alt="Skill für KI-Agenten">
        <img alt="Agent-Skill-Badge" src="https://img.shields.io/badge/Skill-black?style=flat&label=Agent&link=https%3A%2F%2Fscrapling.readthedocs.io%2Fde%2Flatest%2Fai%2Fagent-skill.html"></a>
    <a href="https://clawhub.ai/D4Vinci/scrapling-official" alt="Skill für OpenClaw">
        <img alt="Skill für OpenClaw" src="https://img.shields.io/badge/Clawhub-darkred?style=flat&label=OpenClaw&link=https%3A%2F%2Fclawhub.ai%2FD4Vinci%2Fscrapling-official"></a>
    <br/>
    <a href="https://discord.gg/EMgGbDceNQ" alt="Discord" target="_blank">
      <img alt="Discord" src="https://img.shields.io/discord/1360786381042880532?style=social&logo=discord&link=https%3A%2F%2Fdiscord.gg%2FEMgGbDceNQ">
    </a>
    <a href="https://x.com/Scrapling_dev" alt="X (ehemals Twitter)">
      <img alt="Auf X (ehemals Twitter) folgen" src="https://img.shields.io/twitter/follow/Scrapling_dev?style=social&logo=x&link=https%3A%2F%2Fx.com%2FScrapling_dev">
    </a>
    <br/>
    <a href="https://pypi.org/project/scrapling/" alt="Unterstützte Python-Versionen">
        <img alt="Unterstützte Python-Versionen" src="https://img.shields.io/pypi/pyversions/scrapling.svg"></a>
</p>

<p align="center">
    <a href="https://scrapling.readthedocs.io/de/latest/parsing/selection.html"><strong>Auswahlmethoden</strong></a>
    &middot;
    <a href="https://scrapling.readthedocs.io/de/latest/fetching/choosing.html"><strong>Einen Fetcher wählen</strong></a>
    &middot;
    <a href="https://scrapling.readthedocs.io/de/latest/spiders/architecture.html"><strong>Spider</strong></a>
    &middot;
    <a href="https://scrapling.readthedocs.io/de/latest/spiders/proxy-blocking.html"><strong>Proxy-Rotation</strong></a>
    &middot;
    <a href="https://scrapling.readthedocs.io/de/latest/cli/overview.html"><strong>CLI</strong></a>
    &middot;
    <a href="https://scrapling.readthedocs.io/de/latest/ai/mcp-server.html"><strong>MCP-Modus</strong></a>
</p>

Scrapling ist ein Web-Scraping-Framework für Python. Es vereint schnelle HTTP-Anfragen, Stealth-Browser, die Auswertung von Seiten und paralleles Crawling in einer Bibliothek.

Extrahieren Sie Daten aus statischen Seiten, führen Sie JavaScript aus, bedienen Sie Websites und greifen Sie auf deren APIs zu. Erstellen Sie Crawler mit wiederverwendbaren Sitzungen, Proxy-Rotation, automatischen Wiederholungsversuchen, Pause und Fortsetzung sowie integriertem Datenexport.

Nutzen Sie Scrapling in Python, im Terminal oder mit Ihrem KI-Agenten über den MCP-Server und den Agent Skill. Es deckt den ganzen Ablauf ab: von wenigen Feldern bis zum Speichern einer ganzen Website als saubere Markdown-Dateien.

## Was Sie mit Scrapling machen können

- **[Seiten abrufen und bedienen](https://scrapling.readthedocs.io/de/latest/fetching/choosing.html)**: Schnelle HTTP-Anfragen, Stealth-Browser, JavaScript-Ausführung, Umgang mit Cloudflare Turnstile und Interstitial, dauerhafte Sitzungen und Aufzeichnung von API-Antworten im Hintergrund.
- **[Seiten auswerten und Daten extrahieren](https://scrapling.readthedocs.io/de/latest/parsing/selection.html)**: Suche mit CSS, XPath, Text und regulären Ausdrücken, Wiederfinden von Elementen nach Änderungen der Seite, Suche nach ähnlichen Elementen und saubere Markdown-Ausgabe.
- **[Crawlen und exportieren](https://scrapling.readthedocs.io/de/latest/spiders/getting-started.html)**: Parallele Spider, Proxy-Rotation, Wiederholungsversuche, AutoThrottle, Pause und Fortsetzung, Streaming, fertige Vorlagen und Export nach JSON, JSONL, CSV und XML.
- **[Daten mit KI oder im Terminal extrahieren](https://scrapling.readthedocs.io/de/latest/ai/mcp-server.html)**: Ein MCP-Server zum Browsen und Extrahieren von Daten mit KI-Agenten, ein Agent Skill, CLI-Befehle und eine interaktive Shell.

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

Das gibt `10` aus und speichert Zitate und Autoren in `quotes.json`.

<p align="center">
    <a href="https://dataimpulse.com/?utm_source=scrapling&utm_medium=banner&utm_campaign=scrapling" target="_blank" style="display:flex; justify-content:center; padding:4px 0;">
        <img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/DataImpulse.png" alt="At DataImpulse, we specialize in developing custom proxy services for your business. Make requests from anywhere, collect data, and enjoy fast connections with our premium proxies." style="max-height:60px;">
    </a>
</p>

# Platin-Sponsoren
<table>
  <tr>
    <td width="200">
      <a href="https://go.nodemaven.com/scraplingoctober" target="_blank" title="Proxies with the Highest IP Scores">
        <img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/NodeMaven.jpg" width="240" height="100">
      </a>
    </td>
    <td>
    <a href="https://go.nodemaven.com/scraplingoctober" target="_blank">NodeMaven</a> - der effizienteste Proxy-Anbieter für Web Scraping und Automatisierung mit der höchsten IP-Qualität auf dem Markt. Nutzen Sie den Code SCRAPLING35 für 35 % Rabatt.
    </td>
  </tr>
  <tr>
    <td width="200">
      <a href="https://hypersolutions.co/?utm_source=github&utm_medium=readme&utm_campaign=scrapling" target="_blank" title="Bot Protection Bypass API for Akamai, DataDome, Incapsula & Kasada">
        <img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/HyperSolutions.png">
      </a>
    </td>
    <td> Scrapling bewältigt Cloudflare Turnstile. Für Schutz auf Unternehmensebene bietet <a href="https://hypersolutions.co?utm_source=github&utm_medium=readme&utm_campaign=scrapling">
        <b>Hyper Solutions</b>
      </a> API-Endpunkte, die gültige Antibot-Tokens für <b>Akamai</b>, <b>DataDome</b>, <b>Kasada</b> und <b>Incapsula</b> generieren. Einfache API-Aufrufe, keine Browser-Automatisierung nötig. </td>
  </tr>
  <tr>
    <td width="200">
      <a href="https://evomi.com?utm_source=github&utm_medium=banner&utm_campaign=d4vinci-scrapling" target="_blank" title="Evomi is your Swiss Quality Proxy Provider, starting at $0.49/GB">
        <img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/evomi.png">
      </a>
    </td>
    <td>
      <a href="https://evomi.com?utm_source=github&utm_medium=banner&utm_campaign=d4vinci-scrapling">
        <b>Evomi</b>
      </a>: Residential-Proxys ab 0,49 $/GB. Scraping-Browser auf Chromium-Basis mit vollständig veränderten Fingerprints, Residential-IPs, automatischer CAPTCHA-Lösung und Anti-Bot-Umgehung. </br>
      <b>Scraper-API für problemlose Ergebnisse. MCP- und N8N-Integrationen verfügbar.</b>
    </td>
  </tr>
  <tr>
    <td width="200">
      <a href="https://substack.thewebscraping.club/p/scrapling-hands-on-guide?utm_source=github&utm_medium=repo&utm_campaign=scrapling" target="_blank" title="The #1 newsletter dedicated to Web Scraping">
        <img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/TWSC.png">
      </a>
    </td>
    <td>
    Lesen Sie eine vollständige Rezension von <a href="https://substack.thewebscraping.club/p/scrapling-hands-on-guide?utm_source=github&utm_medium=repo&utm_campaign=scrapling" target="_blank">Scrapling auf The Web Scraping Club</a> (Nov. 2025), dem führenden Newsletter für Web Scraping.
    </td>
  </tr>
  <tr>
    <td width="200">
      <a href="https://www.swiftproxy.net/?ref=D4Vinci" target="_blank" title="Scalable Solutions for Web Data Access">
        <img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/SwiftProxy.png">
      </a>
    </td>
    <td>
    <a href="https://www.swiftproxy.net/?ref=D4Vinci" target="_blank">Swiftproxy</a> bietet skalierbare Residential-Proxys mit über 80 Mio. IPs in mehr als 195 Ländern und liefert schnelle, zuverlässige Verbindungen, automatische Rotation und wirksamen Schutz vor Sperren. Kostenlose Testversion verfügbar.
    </td>
  </tr>
  <tr>
    <td width="200">
      <a href="https://byteful.com/?utm_source=github&utm_medium=github-sponsor&utm_campaign=scrapling_github_sponsor" target="_blank" title="Ethically sourced residential proxy infrastructure powering web scraping and AI agents">
        <img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/byteful.png">
      </a>
    </td>
    <td>
    <a href="https://byteful.com/?utm_source=github&utm_medium=github-sponsor&utm_campaign=scrapling_github_sponsor" target="_blank">Byteful</a> bietet ethisch beschaffte Residential-, Mobil-, ISP- und Datacenter-Proxys sowie Tools für Web Scraping und KI-Automatisierung. Mit dem Code SCRAPLING10 erhalten Sie 10 % Rabatt auf Residential-Proxys.
    </td>
  </tr>
  <tr>
    <td width="200">
      <a href="https://proxylane.dev/?utm_source=scrapling&utm_medium=partnership&utm_campaign=scrapling_platinum_202609&utm_content=github_readme" target="_blank" title="28M+ clean residential IPs for browser automation. No Blocks. No CAPTCHAs. Pay-as-you-Go.">
        <img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/proxylane.png">
      </a>
    </td>
    <td>
    <a href="https://proxylane.dev/?utm_source=scrapling&utm_medium=partnership&utm_campaign=scrapling_platinum_202609&utm_content=github_readme" target="_blank">ProxyLane</a>: Reduzieren Sie Sperren und CAPTCHAs um 90 %. 28 Mio. Premium-Residential-IPs für umfangreiches Web Scraping. 195 Länder. Gezielte Auswahl nach Stadt/ISP/Postleitzahl. Sitzungen mit fester oder rotierender IP. Datenvolumen ohne Ablaufdatum ab $2/GB. Code <strong>SCRAPEANDTAKE</strong>: <em>25 % Rabatt</em>.
    </td>
  </tr>
  <tr>
    <td width="200">
      <a href="https://www.lundproxy.com/unlimited-residential-bandwidth.html?utm_source=github&utm_medium=sponsorship&utm_campaign=scrapling&utm_content=banner" target="_blank" title="Unlimited residential traffic, sized only by bandwidth.">
        <img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/lundproxy.png">
      </a>
    </td>
    <td>
    <a href="https://www.lundproxy.com?utm_source=github&utm_medium=sponsorship&utm_campaign=scrapling&utm_content=text" target="_blank">LundProxy</a>: Zahlen Sie nicht länger pro GB. Unbegrenzter Residential-Traffic, über 100 Mio. IPs, mehr als 190 Länder. Zahlen Sie nach Bandbreite. Fordern Sie einen kostenlosen Test der Residential-Proxys mit 50 Mbps an.
    </td>
  </tr>
  <tr>
    <td width="200">
      <a href="https://dataimpulse.com/?utm_source=website&utm_medium=github_readme&utm_campaign=scrapling_platinum" target="_blank" title="Buy Pay-as-you-go proxies from $1/GB">
        <img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/DataImpulse_Platinum.png">
      </a>
    </td>
    <td>
    $1/GB bei <a href="https://dataimpulse.com/?utm_source=website&utm_medium=github_readme&utm_campaign=scrapling_platinum" target="_blank">DataImpulse</a>. Ethisch bezogene Proxys aus erster Hand. Über 90 Mio. IPs, mehr als 195 Länder. Residential-, Datacenter- und Mobilproxys. Nutzungsabhängige Zahlung = kein Abo. Datenvolumen verfällt nie.
    </td>
  </tr>
</table>

<i><sub>Möchten Sie Ihre Anzeige hier zeigen? Klicken Sie [hier](https://github.com/sponsors/D4Vinci/sponsorships?tier_id=586646)</sub></i>
# Sponsoren

<!-- sponsors -->

<a href="https://cloro.dev/?utm_source=referral&utm_medium=scrapling" target="_blank" title="The search API for the AI era"><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/cloro.jpg"></a>

<br/>

<a href="https://serpapi.com/?utm_source=scrapling" target="_blank" title="Scrape Google and other search engines with SerpApi"><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/SerpApi.png"></a>
<a href="https://visit.decodo.com/Dy6W0b" target="_blank" title="Try the Most Efficient Residential Proxies for Free"><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/decodo.png"></a>
<a href="https://proxyempire.io/?ref=scrapling&utm_source=github&utm_medium=paid_referral&utm_campaign=open_source_sponsorship&utm_content=scrapling" target="_blank" title="Collect The Data Your Project Needs with the Best Residential Proxies"><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/ProxyEmpire.png"></a>
<a href="https://www.webshare.io/?referral_code=48r2m2cd5uz1" target="_blank" title="The Most Reliable Proxy with Unparalleled Performance"><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/webshare.png"></a>
<a href="https://proxiware.com/?ref=scrapling" target="_blank" title="Collect Any Data. At Any Scale."><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/proxiware.png"></a>


<!-- /sponsors -->

<i><sub>Möchten Sie Ihre Anzeige hier zeigen? Klicken Sie [hier](https://github.com/sponsors/D4Vinci) und wählen Sie die Stufe, die zu Ihnen passt!</sub></i>

---

## Wichtige Funktionen

### Spider: ein vollständiges Crawling-Framework

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

### Seiten mit Sitzungen abrufen

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

### Seiten auswerten und Daten extrahieren

- 🔄 **Elemente wiederfinden**: Finden Sie Elemente nach Änderungen der Website mit Algorithmen zur Ähnlichkeitssuche wieder.
- 🎯 **Flexible Auswahl**: Nutzen Sie CSS, XPath, Filter, Text, reguläre Ausdrücke und mehr.
- 🔍 **Ähnliche Elemente**: Finden Sie automatisch Elemente, die den bereits gefundenen ähneln.

### KI-Funktionen

- 🤖 **MCP-Server**: Ermöglicht Assistenten und KI-Agenten wie Claude und Cursor, Daten mit Scrapling zu extrahieren. Dazu dienen HTTP-Anfragen, Browseraktionen, Screenshots, ein gespeicherter Anmeldezustand und API-Antworten im Hintergrund. Er nutzt unseren Stealth-Browser und Werkzeuge, mit denen geeignete Modelle CAPTCHAs lösen können, zusätzlich zum Cloudflare-Löser. Er verringert den an das Modell gesendeten Inhalt, blockiert Werbung und schützt vor Prompt Injection. Entfernte Browser über CDP und HTTP-Verbindungen mit Authentifizierungsoptionen sind ebenfalls möglich. ([Demovideo](https://www.youtube.com/watch?v=qyFk3ZNwOxE))
- 🧠 **Agent Skill**: Ein [Agent Skill](https://scrapling.readthedocs.io/de/latest/ai/agent-skill.html) zum Installieren, der Coding-Agenten die Bibliothek erklärt. So schreiben sie Code, der zur aktuellen API passt.
- 📚 **Markdown für RAG**: Wandeln Sie eine Seite mit einer Zeile (`page.markdown()`) in sauberes Markdown für Sprachmodelle um, oder speichern Sie mit der Vorlage `ContentSpider` eine ganze Website als Markdown-Dateien. Dafür ist kein Sprachmodell nötig. ([Dokumentation](https://scrapling.readthedocs.io/de/latest/ai/building-rag-systems.html))

### Schnell und im Alltag erprobt

- 🚀 **Hohe Geschwindigkeit**: Optimierte Leistung, die die meisten Web-Scraping-Bibliotheken für Python übertrifft.
- 🔋 **Geringer Speicherbedarf**: Optimierte Datenstrukturen und Laden bei Bedarf.
- ⚡ **Schnelle JSON-Ausgabe**: 10-mal schneller als die Standardbibliothek.
- 🏗️ **In der Praxis getestet**: Tests decken 92 % von Scrapling ab, und der gesamte Code hat Typannotationen. Hunderte Menschen haben es im letzten Jahr täglich zur Datenextraktion verwendet.

### Werkzeuge für Entwicklung und Datenextraktion

- 🎯 **Interaktive Shell**: Eine optionale IPython-Shell mit Scrapling, Kurzbefehlen und Werkzeugen für die schnelle Entwicklung von Skripten. Wandeln Sie curl-Anfragen in Scrapling-Anfragen um und zeigen Sie Ergebnisse im Browser an.
- 🚀 **Nutzung im Terminal**: Extrahieren Sie die Daten einer URL, ohne Code zu schreiben.
- 🛠️ **Navigation im DOM**: Greifen Sie auf Eltern-, Geschwister- und Kindelemente zu.
- 🧬 **Textverarbeitung**: Reguläre Ausdrücke, Textbereinigung und optimierte Arbeit mit Zeichenketten.
- 📝 **Selektoren erzeugen**: Erstellen Sie zuverlässige CSS- und XPath-Selektoren für jedes Element.
- 🔌 **Vertraute API**: Ähnlich wie Scrapy und BeautifulSoup, mit denselben Pseudoelementen wie Scrapy und Parsel.
- 🤝 **Direkte Integration mit Scrapy**: Ergänzen Sie einen Callback um den Dekorator `scrapling_response`, um die bereits abgerufenen Antworten mit dem Scrapling-Parser auszuwerten. Sie müssen Ihr Programm nicht neu schreiben.
- 📘 **Vollständige Typannotationen**: Sie helfen dem Editor, Code zu prüfen und zu vervollständigen. Der gesamte Code wird bei jeder Änderung automatisch mit **PyRight** und **MyPy** geprüft.
- 🔋 **Fertiges Docker-Image**: Bei jeder Version wird automatisch ein Docker-Image mit allen Browsern erstellt und veröffentlicht.

## Erste Schritte

Hier sehen Sie einige Beispiele für Scrapling.

### Grundlegende Verwendung
HTTP-Anfragen mit Sitzungen
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
page = StealthyFetcher.fetch('https://nopecha.com/demo/cloudflare', solve_cloudflare=True)
data = page.css('#padded_content a').getall()
```
Vollständige Browser-Automatisierung
```python
from scrapling.fetchers import StealthyFetcher, StealthySession

with StealthySession(headless=True, disable_resources=False, network_idle=True) as session:  # Browser offen halten, bis Sie fertig sind
    page = session.fetch('https://quotes.toscrape.com/', load_dom=False)
    data = page.xpath('//span[@class="text"]/text()').getall()  # XPath-Selektor, falls bevorzugt

# Oder einmaligen Anfragenstil verwenden: öffnet den Browser für diese Anfrage und schließt ihn nach Abschluss
page = StealthyFetcher.fetch('https://quotes.toscrape.com/')
data = page.css('.quote .text::text').getall()
```

### Spider
Erstellen Sie vollständige Crawler mit parallelen Anfragen, mehreren Sitzungstypen, Pause und Fortsetzung:
```python
from scrapling.spiders import Spider, Response

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
Verwenden Sie mehrere Sitzungstypen im selben Spider:
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
Speichern Sie den Fortschritt, um lange Crawls zu pausieren und fortzusetzen. Starten Sie den Spider so:
```python
QuotesSpider(crawldir="./crawl_data").start()
```
Mit gesetztem `crawldir` speichert Strg+C ausstehende Anfragen und bereits besuchte URLs. Starten Sie mit demselben `crawldir` neu, um fortzufahren. Speichern Sie extrahierte Daten separat.

Sie können auch eine fertige Vorlage verwenden. Rufen Sie zum Beispiel den ganzen Katalog eines Shopify-Shops ab:
```python
from scrapling.spiders import ShopifySpider

class MyStore(ShopifySpider):
    target_website = "example.com"

result = MyStore().start()  # Alle Produkte im Shop, ein Item pro Variante
```
Die Vorlage liest Produkte aus den öffentlichen Endpunkten der Kollektionen, mit einem Element pro Variante.

### Erweiterte Auswertung und Navigation
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
quotes = page.find_by_text('Albert Einstein', first_match=False)

# Erweiterte Navigation
quote_text = page.css('.quote')[0].css('.text::text').get()
quote_texts = page.css('.quote').css('.text::text').getall()  # Verkettete Selektoren
first_quote = page.css('.quote')[0]
author = first_quote.css('.author::text').get()
next_quote = first_quote.next
parent_container = first_quote.parent

# Elementbeziehungen und Ähnlichkeit
similar_elements = first_quote.find_similar()
below_elements = first_quote.below_elements
```
Sie können den Parser direkt verwenden, ohne eine Webseite abzurufen:
```python
from scrapling.parser import Selector

page = Selector("<html>...</html>")
```
Er funktioniert auf dieselbe Weise.

### Beispiele für asynchrone Sitzungen
```python
import asyncio
from scrapling.fetchers import FetcherSession, AsyncStealthySession

async def main():
    async with FetcherSession(http3=True) as http_session:  # `FetcherSession` passt sich dem Kontext an und funktioniert synchron wie asynchron
        page1 = await http_session.get('https://quotes.toscrape.com/')
        page2 = await http_session.get('https://quotes.toscrape.com/page/2/', impersonate='chrome')
        print(len(page1.css('.quote')), len(page2.css('.quote')))

    async with AsyncStealthySession(max_pages=2) as browser_session:
        urls = ['https://quotes.toscrape.com/js/', 'https://quotes.toscrape.com/js/page/2/']
        pages = await asyncio.gather(*(browser_session.fetch(url, wait_selector='.quote') for url in urls))
        print([len(page.css('.quote')) for page in pages])

asyncio.run(main())
```

## CLI und interaktive Shell

Sie können Scrapling auch im Terminal verwenden:

[![asciicast](https://asciinema.org/a/736339.svg)](https://asciinema.org/a/736339)

Starten Sie die interaktive Web-Scraping-Shell:
```bash
pip install "scrapling[shell]"
scrapling shell
```
Seiten direkt ohne Programmierung in eine Datei extrahieren. Wählen Sie Inhalte mit `--css-selector` aus oder verwenden Sie `--ai-targeted`, um den `body`-Inhalt auszuwählen und zu bereinigen. Nutzen Sie `.txt` für Text, `.md` für Markdown oder `.html` für HTML.
```bash
scrapling extract get 'https://quotes.toscrape.com/' quotes.md
scrapling extract get 'https://quotes.toscrape.com/' quotes.txt --css-selector '.quote' --impersonate 'chrome'
scrapling extract fetch 'https://quotes.toscrape.com/js/' quotes.md --css-selector '.quote' --wait-selector '.quote' --no-headless
scrapling extract fetch 'https://nopecha.com/demo/cloudflare' captchas.html --css-selector '#padded_content a' --solve-cloudflare
```

> [!NOTE]
> Weitere Funktionen, darunter der MCP-Server und die interaktive Shell, stehen in der [vollständigen Dokumentation](https://scrapling.readthedocs.io/de/latest/).

## Leistungstests

Scrapling zeichnet sich auch durch seine Geschwindigkeit aus. Diese Tests vergleichen seinen Parser mit den neuesten Versionen anderer bekannter Bibliotheken.

### Geschwindigkeit der Textextraktion (5.000 verschachtelte Elemente)

| # |    Bibliothek     | Zeit (ms) | Im Vergleich zu Scrapling |
|---|:-----------------:|:---------:|:------------:|
| 1 |     Scrapling     |   1,99    |     1,0x     |
| 2 |   Parsel/Scrapy   |   2,06    |    1,035     |
| 3 |     Lxml allein      |   2,56    |    1,286     |
| 4 |      PyQuery      |   23,98   |     ~12x     |
| 5 |    Selectolax     |  197,02   |     ~99x     |
| 6 |  MechanicalSoup   |  1545,15  |   ~776,5x    |
| 7 |   BS4 mit Lxml   |  1562,1  |   ~785,0x    |
| 8 | BS4 mit html5lib |  3412,73  |   ~1714,9x   |


### Suche nach ähnlichen Elementen und Text

Die adaptive Elementsuche von Scrapling ist schneller als die Alternativen:

| Bibliothek  | Zeit (ms) | Im Vergleich zu Scrapling |
|-------------|:---------:|:------------:|
| Scrapling   |   2,3    |     1,0x     |
| AutoScraper |   12,58   |    5,47x    |


> Jedes Ergebnis ist der Durchschnitt aus mindestens 100 Durchläufen. Die Methode steht in [benchmarks.py](https://github.com/D4Vinci/Scrapling/blob/main/benchmarks.py).

## Installation

Scrapling benötigt Python 3.10 oder neuer:

```bash
pip install scrapling
```

> [!IMPORTANT]
> Dieser Befehl installiert nur den Parser und seine Abhängigkeiten, ohne Fetcher oder Werkzeuge für die Kommandozeile. Wenn Sie nur das installieren, führt ein Import aus `scrapling.fetchers` oder `scrapling.spiders`, wie in den Beispielen oben, zu `ModuleNotFoundError`. Für Fetcher oder Spider müssen Sie zuerst die Fetcher-Abhängigkeiten wie unten gezeigt installieren.

### Optionale Abhängigkeiten

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
   - Die Abhängigkeiten zum [Aufbau von RAG-Systemen](https://scrapling.readthedocs.io/de/latest/ai/building-rag-systems.html) installieren:
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

### Docker
Sie können auch ein Docker-Image mit allen Extras und Browsern von DockerHub herunterladen:
```bash
docker pull pyd4vinci/scrapling
```
Oder aus der GitHub-Registry herunterladen:
```bash
docker pull ghcr.io/d4vinci/scrapling:latest
```
Das Image wird aus dem Hauptbranch des Repositorys erstellt und von GitHub Actions automatisch veröffentlicht.

## Mitwirken

Wir freuen uns über Beiträge! Bitte lesen Sie unsere [Beitragsrichtlinien](https://github.com/D4Vinci/Scrapling/blob/main/CONTRIBUTING.md), bevor Sie beginnen.

## Haftungsausschluss

> [!CAUTION]
> Diese Bibliothek dient nur der Bildung und Forschung. Mit ihrer Nutzung stimmen Sie zu, die lokalen und internationalen Gesetze zur Datenextraktion und zum Datenschutz einzuhalten. Die Autoren und Mitwirkenden sind nicht für den Missbrauch dieser Software verantwortlich. Beachten Sie die Nutzungsbedingungen der Websites und die robots.txt-Dateien.

## 🎓 Zitieren
Wenn Sie diese Bibliothek in Ihrer Forschung verwendet haben, zitieren Sie sie mit dieser Referenz:
```text
  @misc{scrapling,
    author = {Karim Shoair},
    title = {Scrapling},
    year = {2024},
    url = {https://github.com/D4Vinci/Scrapling},
    note = {A Python Web Scraping framework for everything from a single request to a full-scale crawl!}
  }
```

## Lizenz

Dieses Projekt nutzt die BSD-3-Clause-Lizenz.

## Danksagungen

Dieses Projekt enthält angepassten Code von:
- Parsel (BSD-Lizenz): verwendet für das Submodul [translator](https://github.com/D4Vinci/Scrapling/blob/main/scrapling/core/translator.py)

---
<div align="center"><small>Entworfen und hergestellt mit ❤️ von Karim Shoair.</small></div><br>
