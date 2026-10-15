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
    <a href="https://hub.docker.com/r/pyd4vinci/scrapling" target="_blank">
        <img alt="Docker Pulls" src="https://img.shields.io/docker/pulls/pyd4vinci/scrapling?labelColor=%20%23FDB062&logo=Docker&labelColor=%20%23528bff"></a>
    <a href="https://clickpy.clickhouse.com/dashboard/scrapling" rel="nofollow"><img src="https://img.shields.io/pypi/dm/scrapling" alt="PyPI package downloads"></a>
    <a href="https://scrapling.readthedocs.io/en/latest/ai/agent-skill.html" alt="AI Agent Skill">
        <img alt="Static Badge" src="https://img.shields.io/badge/Skill-black?style=flat&label=Agent&link=https%3A%2F%2Fscrapling.readthedocs.io%2Fen%2Flatest%2Fai%2Fagent-skill.html"></a>
    <a href="https://clawhub.ai/D4Vinci/scrapling-official" alt="OpenClaw Skill">
        <img alt="OpenClaw Skill" src="https://img.shields.io/badge/Clawhub-darkred?style=flat&label=OpenClaw&link=https%3A%2F%2Fclawhub.ai%2FD4Vinci%2Fscrapling-official"></a>
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
    <a href="https://scrapling.readthedocs.io/en/latest/parsing/selection.html"><strong>Auswahlmethoden</strong></a>
    &middot;
    <a href="https://scrapling.readthedocs.io/en/latest/fetching/choosing.html"><strong>Einen Fetcher wählen</strong></a>
    &middot;
    <a href="https://scrapling.readthedocs.io/en/latest/spiders/architecture.html"><strong>Spiders</strong></a>
    &middot;
    <a href="https://scrapling.readthedocs.io/en/latest/spiders/proxy-blocking.html"><strong>Proxy-Rotation</strong></a>
    &middot;
    <a href="https://scrapling.readthedocs.io/en/latest/cli/overview.html"><strong>CLI</strong></a>
    &middot;
    <a href="https://scrapling.readthedocs.io/en/latest/ai/mcp-server.html"><strong>MCP-Modus</strong></a>
</p>

Scrapling ist ein Web-Scraping-Framework für Python, das schnelle HTTP-Anfragen, Stealth-Browser, leistungsstarkes Parsing und paralleles Crawling in einer Bibliothek vereint.

Scrapen Sie statische Seiten, rendern Sie JavaScript, interagieren Sie mit Websites und extrahieren Sie Daten aus den API-Aufrufen dahinter. Bauen Sie Crawler mit wiederverwendbaren Sessions, Proxy-Rotation, automatischen Wiederholungsversuchen, Pause & Resume und integriertem Datenexport.

Nutzen Sie Scrapling in Python, im Terminal oder mit Ihrem KI-Agenten über den MCP-Server und den Agent Skill. Ob Sie nur ein paar Felder extrahieren oder eine ganze Website als sauberes Markdown sammeln möchten, Scrapling deckt den gesamten Scraping-Workflow ab.

## Was Sie mit Scrapling machen können

- **[Abrufen & interagieren](https://scrapling.readthedocs.io/en/latest/fetching/choosing.html)**: Schnelle HTTP-Anfragen, Stealth-Browser, JavaScript-Rendering, Umgang mit Cloudflare Turnstile/Interstitial, persistente Sessions und Aufzeichnung von API-Aufrufen im Hintergrund.
- **[Parsen & extrahieren](https://scrapling.readthedocs.io/en/latest/parsing/selection.html)**: CSS, XPath, Text- und Regex-Suche, adaptives Element-Tracking, Suche nach ähnlichen Elementen und saubere Markdown-Ausgabe.
- **[Crawlen & exportieren](https://scrapling.readthedocs.io/en/latest/spiders/getting-started.html)**: Parallele Spiders, Proxy-Rotation, Wiederholungsversuche, AutoThrottle, Pause & Resume, Streaming, fertige Vorlagen und JSON/JSONL/CSV/XML-Exporte.
- **[Scrapen mit KI oder im Terminal](https://scrapling.readthedocs.io/en/latest/ai/mcp-server.html)**: Ein MCP-Server für KI-Agenten zum Browsen und Extrahieren von Daten, ein Agent Skill, CLI-Befehle und eine interaktive Shell.

Starten Sie mit einer einzelnen Seite:

```python
from scrapling.fetchers import Fetcher

page = Fetcher.get('https://quotes.toscrape.com/')
quotes = page.css('.quote .text::text').getall()
print(quotes)
```

Oder skalieren Sie mit einem Spider:

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
      <a href="https://go.nodemaven.com/scraplingseptember" target="_blank" title="Proxies with the Highest IP Scores">
        <img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/NodeMaven.jpg" width="240" height="100">
      </a>
    </td>
    <td>
    <a href="https://go.nodemaven.com/scraplingseptember" target="_blank">NodeMaven</a> - der effizienteste Proxy-Anbieter für Web Scraping und Automatisierung mit der höchsten IP-Qualität auf dem Markt. Nutze den Code SCRAPLING35 für 35% Rabatt.
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
      </a>: Residential-Proxies ab 0,49 $/GB. Scraping-Browser mit vollständig gefälschtem Chromium, Residential-IPs, automatischer CAPTCHA-Lösung und Anti-Bot-Umgehung. </br>
      <b>Scraper-API für problemlose Ergebnisse. MCP- und N8N-Integrationen verfügbar.</b>
    </td>
  </tr>
  <tr>
    <td width="200">
      <a href="https://tikhub.io/?utm_source=github.com/D4Vinci/Scrapling&utm_medium=marketing_social&utm_campaign=retargeting&utm_content=carousel_ad" target="_blank" title="Unlock the Power of Social Media Data & AI">
        <img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/TikHub.jpg">
      </a>
    </td>
    <td>
      <a href="https://tikhub.io/?utm_source=github.com/D4Vinci/Scrapling&utm_medium=marketing_social&utm_campaign=retargeting&utm_content=carousel_ad" target="_blank">TikHub.io</a> bietet über 900 stabile APIs auf mehr als 16 Plattformen, darunter TikTok, X, YouTube und Instagram, mit über 40 Mio. Datensätzen. <br /> Bietet außerdem <a href="https://ai.tikhub.io/?ref=KarimShoair" target="_blank">vergünstigte KI-Modelle</a> - Claude, GPT, GEMINI und mehr mit bis zu 71% Rabatt.
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
    <a href="https://www.swiftproxy.net/?ref=D4Vinci" target="_blank">Swiftproxy</a> bietet skalierbare Residential-Proxys mit über 80 Mio. IPs in mehr als 195 Ländern und liefert schnelle, zuverlässige Verbindungen, automatische Rotation und starke Anti-Block-Leistung. Kostenlose Testversion verfügbar.
    </td>
  </tr>
  <tr>
    <td width="200">
      <a href="https://byteful.com/?utm_source=github&utm_medium=github-sponsor&utm_campaign=scrapling_github_sponsor" target="_blank" title="Ethically sourced residential proxy infrastructure powering web scraping and AI agents">
        <img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/byteful.png">
      </a>
    </td>
    <td>
    <a href="https://byteful.com/?utm_source=github&utm_medium=github-sponsor&utm_campaign=scrapling_github_sponsor" target="_blank">Byteful</a> bietet ethisch beschaffte Residential-, Mobil-, ISP- und Datacenter-Proxys sowie Tools für Web Scraping und KI-Automatisierung. Mit dem Code SCRAPLING10 erhalten Sie 10% Rabatt auf Residential-Proxys.
    </td>
  </tr>
  <tr>
    <td width="200">
      <a href="https://proxylane.dev/?utm_source=scrapling&utm_medium=partnership&utm_campaign=scrapling_platinum_202609&utm_content=github_readme" target="_blank" title="28M+ clean residential IPs for browser automation. No Blocks. No CAPTCHAs. Pay-as-you-Go.">
        <img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/proxylane.png">
      </a>
    </td>
    <td>
    <a href="https://proxylane.dev/?utm_source=scrapling&utm_medium=partnership&utm_campaign=scrapling_platinum_202609&utm_content=github_readme" target="_blank">ProxyLane</a>: Reduzieren Sie Sperren und CAPTCHAs um 90%. 28 Mio. Premium-Residential-IPs für umfangreiches Web Scraping. 195 Länder. Gezielte Auswahl nach Stadt/ISP/Postleitzahl. Sitzungen mit fester oder rotierender IP. Datenvolumen ohne Ablaufdatum ab $2/GB. Code <strong>SCRAPEANDTAKE</strong>: <em>25% Rabatt</em>.
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
    $1/GB bei <a href="https://dataimpulse.com/?utm_source=website&utm_medium=github_readme&utm_campaign=scrapling_platinum" target="_blank">DataImpulse</a>. Ethisch bezogene Proxys aus erster Hand. Über 90 Mio. IPs, mehr als 195 Länder. Residential-, Datacenter- und Mobilproxies. Nutzungsabhängige Zahlung = kein Abo. Datenvolumen verfällt nie.
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

## Hauptmerkmale

### Spiders -- Ein vollständiges Crawling-Framework
- 🕷️ **Scrapy-ähnliche Spider-API**: Definieren Sie Spiders mit `start_urls`, async `parse` Callbacks und `Request`/`Response`-Objekten.
- ⚡ **Paralleles Crawling**: Konfigurierbare Parallelitätslimits, domainbezogenes Throttling und Download-Verzögerungen.
- 🔄 **Multi-Session-Unterstützung**: Einheitliche Schnittstelle für HTTP-Anfragen und heimliche Headless-Browser in einem einzigen Spider -- leiten Sie Anfragen per ID an verschiedene Sessions weiter.
- 💾 **Pause & Resume**: Ausstehende Anfragen und besuchte URLs mit `crawldir` speichern. Mit Strg+C kontrolliert stoppen und mit demselben Verzeichnis neu starten.
- 📡 **Streaming-Modus**: Gescrapte Elemente in Echtzeit streamen über `async for item in spider.stream()` mit Echtzeit-Statistiken -- ideal für UI, Pipelines und lang laufende Crawls.
- 🛡️ **Erkennung blockierter Anfragen**: Automatische Erkennung und Wiederholung blockierter Anfragen mit anpassbarer Logik.
- 🚦 **AutoThrottle**: Schluss mit dem Raten von Verzögerungen. Der Spider stimmt die Verzögerung jeder Domain selbst darauf ab, wie schnell die Website antwortet, verdoppelt sie (oder wartet, was `Retry-After` verlangt), sobald die Website Sie blockiert oder ausbremst, und wird wieder schneller, sobald das aufhört.
- 🤖 **robots.txt-Konformität**: Optionales `robots_txt_obey`-Flag, das `Disallow`-, `Crawl-delay`- und `Request-rate`-Direktiven mit domainbasiertem Caching respektiert.
- 🧪 **Entwicklungsmodus**: Antworten beim ersten Lauf auf der Festplatte zwischenspeichern und bei weiteren Läufen erneut abspielen - iterieren Sie an Ihrer `parse()`-Logik, ohne die Zielserver erneut abzufragen.
- 🧩 **Fertige Spider-Vorlagen**: Sparen Sie sich den Boilerplate-Code mit `CrawlSpider` für regelbasiertes Link-Following, `SitemapSpider` für Sitemap-/robots.txt-gesteuerte Crawls, `XMLFeedSpider`/`CSVFeedSpider` für XML/RSS- und CSV-Feeds und `ShopifySpider` zum Sammeln von Produkten aus öffentlichen Shopify-Shops, ein Item pro Variante.
- 🔗 **Link-Extraktion**: Ein eigenständiges `LinkExtractor`-Primitiv mit Allow-/Deny-Mustern, Domain-Filtern, CSS-/XPath-Eingrenzung, Erweiterungsfilterung und Kanonisierung -- nutzbar innerhalb der Vorlagen oder für sich allein.
- 📦 **Integrierter Export**: Ergebnisse über Hooks und Ihre eigene Pipeline oder die integrierten JSON/JSONL/CSV/XML-Exporte mit `result.items.to_json()`, `to_jsonl()`, `to_csv()` und `to_xml()` exportieren.

### Erweitertes Website-Abrufen mit Session-Unterstützung
- **HTTP-Anfragen**: Schnelle und heimliche HTTP-Anfragen mit der `Fetcher`-Klasse. Kann Browser-TLS-Fingerprints und Header imitieren und HTTP/3 verwenden.
- **Dynamisches Laden**: Dynamische Websites mit vollständiger Browser-Automatisierung über die `StealthyFetcher`-Klasse abrufen, die Playwrights Chromium und Google Chrome unterstützt.
- **Anti-Bot-Umgehung**: Fortschrittliche Stealth-Funktionen mit `StealthyFetcher` und Fingerprint-Spoofing. Umgeht mit Automatisierung mühelos alle Arten von Cloudflare-Turnstile-/Interstitial-Challenges.
- **Session-Verwaltung**: Persistente Session-Unterstützung mit den Klassen `FetcherSession` und `StealthySession` für Cookie- und Zustandsverwaltung über Anfragen hinweg.
- **Proxy-Rotation**: Integrierter `ProxyRotator` mit zyklischen oder benutzerdefinierten Rotationsstrategien über alle Session-Typen hinweg, plus Proxy-Überschreibungen pro Anfrage.
- **Domain- & Werbeblockierung**: Anfragen an bestimmte Domains (und deren Subdomains) blockieren oder die integrierte Werbeblockierung (~3.500 bekannte Werbe-/Tracker-Domains) in browserbasierten Fetchern aktivieren.
- **DNS-Leak-Prävention**: Optionale DNS-over-HTTPS-Unterstützung zur Weiterleitung von DNS-Anfragen über Cloudflares DoH, um DNS-Leaks bei der Verwendung von Proxys zu verhindern.
- **Remote-Browser**: Statt lokal einen Browser zu starten, verbinden Sie sich per CDP mit `cdp_url` zu einem bereits laufenden Browser -- auf demselben Rechner, einem anderen Host oder bei einem Managed-Browser-Anbieter. Mit `executable_path` können Sie jeden Browser-Fetcher außerdem auf Ihren eigenen Chromium-Build verweisen.
- **Hintergrund-API-Erfassung**: Aktivieren Sie `record_requests=True` in einer Browsersitzung und durchsuchen Sie die gespeicherten Antworten mit `session.network.search(limit=None)`. Lesen Sie API-Daten und HTTP-Fehler über mehrere Seitenaufrufe hinweg, ohne Anfragen erneut zu senden. Der Verlauf ist begrenzt und speichert Text-Antwortkörper.
- **Async-Unterstützung**: Vollständige async-Unterstützung über alle Fetcher und dedizierte async Session-Klassen hinweg.

### Parsing und Datenextraktion
- 🔄 **Intelligente Element-Verfolgung**: Elemente nach Website-Änderungen mit intelligenten Ähnlichkeitsalgorithmen neu lokalisieren.
- 🎯 **Intelligente flexible Auswahl**: CSS-Selektoren, XPath-Selektoren, filterbasierte Suche, Textsuche, Regex-Suche und mehr.
- 🔍 **Ähnliche Elemente finden**: Elemente, die gefundenen Elementen ähnlich sind, automatisch lokalisieren.

### KI-Funktionen
- 🤖 **MCP-Server**: Lassen Sie KI-Chatbots und -Agenten (Claude/Cursor/usw.) über Scrapling scrapen, mit HTTP-Anfragen, Browser-Aktionen, Screenshots, gespeicherten Anmeldungen und API-Antworten im Hintergrund. Mit unserem Stealth-Browser und den passenden Tools können geeignete KI-Modelle jedes CAPTCHA umgehen, das ihnen bei der Arbeit begegnet (ganz zu schweigen von unserem Cloudflare-Löser). Verschiedene Methoden reduzieren den Inhalt für das Modell, blockieren Werbung und schützen es vor Prompt-Injection. Remote-Browser über CDP und HTTP-Transport mit Authentifizierungsoptionen sind enthalten. ([Demo-Video](https://www.youtube.com/watch?v=qyFk3ZNwOxE))
- 🧠 **Agent Skill**: Ein installationsfertiger [Agent Skill](https://scrapling.readthedocs.io/en/latest/ai/agent-skill.html), der Coding-Agents die gesamte Bibliothek beibringt, damit der Code, den sie mit Scrapling schreiben, zur aktuellen API passt, statt geraten zu werden.
- 📚 **RAG-fertiges Markdown**: Wandeln Sie jede Seite mit einer Zeile (`page.markdown()`) in sauberes, bereinigtes, LLM-fertiges Markdown um oder crawlen Sie eine ganze Website mit der Vorlage `ContentSpider` in einen Markdown-Korpus, ganz ohne LLM im Prozess. ([Dokumentation](https://scrapling.readthedocs.io/en/latest/ai/building-rag-systems.html))

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
- 🤝 **Nahtlose Scrapy-Integration**: Sie setzen bereits auf Scrapy? Versehen Sie einen beliebigen Callback mit `scrapling_response`, um die ohnehin abgerufenen Responses mit Scraplings Parser zu verarbeiten -- ganz ohne Umschreiben.
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

### Spiders
Vollständige Crawler mit parallelen Anfragen, mehreren Session-Typen und Pause & Resume erstellen:
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
Mit gesetztem `crawldir` speichert Strg+C ausstehende Anfragen und bereits besuchte URLs. Starten Sie mit demselben `crawldir` neu, um fortzufahren. Speichern Sie extrahierte Daten separat.

Oder überspringen Sie das Schreiben der Crawling-Logik komplett mit den fertigen Vorlagen, etwa um den gesamten Katalog eines Shopify-Shops abzurufen:
```python
from scrapling.spiders import ShopifySpider

class MyStore(ShopifySpider):
    target_website = "example.com"

result = MyStore().start()  # Alle Produkte im Shop, ein Item pro Variante
```
Die Vorlage liest Produkte aus öffentlichen Collection-Endpunkten, ein Item pro Variante.

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
Sie können den Parser direkt verwenden, wenn Sie keine Websites abrufen möchten, wie unten gezeigt:
```python
from scrapling.parser import Selector

page = Selector("<html>...</html>")
```
Und es funktioniert genau auf die gleiche Weise!

### Beispiele für async Session-Verwaltung
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

## CLI & Interaktive Shell

Scrapling enthält eine leistungsstarke Befehlszeilenschnittstelle:

[![asciicast](https://asciinema.org/a/736339.svg)](https://asciinema.org/a/736339)

Interaktive Web-Scraping-Shell starten
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
> Es gibt viele zusätzliche Funktionen, aber wir möchten diese Seite prägnant halten, einschließlich des MCP-Servers und der interaktiven Web-Scraping-Shell. Schauen Sie sich die vollständige Dokumentation [hier](https://scrapling.readthedocs.io/en/latest/) an

## Leistungsbenchmarks

Scrapling ist nicht nur leistungsstark -- es ist auch blitzschnell. Die folgenden Benchmarks vergleichen Scraplings Parser mit den neuesten Versionen anderer beliebter Bibliotheken.

### Textextraktions-Geschwindigkeitstest (5000 verschachtelte Elemente)

| # |    Bibliothek     | Zeit (ms) | vs Scrapling |
|---|:-----------------:|:---------:|:------------:|
| 1 |     Scrapling     |   1.99    |     1.0x     |
| 2 |   Parsel/Scrapy   |   2.06    |    1.035     |
| 3 |     Raw Lxml      |   2.56    |    1.286     |
| 4 |      PyQuery      |   23.98   |     ~12x     |
| 5 |    Selectolax     |  197.02   |     ~99x     |
| 6 |  MechanicalSoup   |  1545.15  |   ~776.5x    |
| 7 |   BS4 with Lxml   |  1562.1  |   ~785.0x    |
| 8 | BS4 with html5lib |  3412.73  |   ~1714.9x   |


### Element-Ähnlichkeit & Textsuche-Leistung

Scraplings adaptive Element-Finding-Fähigkeiten übertreffen Alternativen deutlich:

| Bibliothek  | Zeit (ms) | vs Scrapling |
|-------------|:---------:|:------------:|
| Scrapling   |   2.3    |     1.0x     |
| AutoScraper |   12.58   |    5.47x    |


> Alle Benchmarks stellen Durchschnittswerte von über 100 Durchläufen dar. Siehe [benchmarks.py](https://github.com/D4Vinci/Scrapling/blob/main/benchmarks.py) für die Methodik.

## Installation

Scrapling erfordert Python 3.10 oder höher:

```bash
pip install scrapling
```

> [!IMPORTANT]
> Diese Installation enthält nur die Parser-Engine und ihre Abhängigkeiten, ohne Fetcher oder Kommandozeilenabhängigkeiten. Daher führt der Import von allem aus `scrapling.fetchers` oder `scrapling.spiders`, wie in den Beispielen oben, mit dieser Installation allein zu einem `ModuleNotFoundError`. Wenn Sie einen der Fetcher oder Spider verwenden möchten, installieren Sie zuerst die Fetcher-Abhängigkeiten wie unten gezeigt.

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
   - Abhängigkeiten für ([RAG-Systeme erstellen](https://scrapling.readthedocs.io/en/latest/ai/building-rag-systems.html)) installieren:
       ```bash
       pip install "scrapling[rag]"
       ```
   - Shell-Funktionen installieren (Web-Scraping-Shell und der `extract`-Befehl):
       ```bash
       pip install "scrapling[shell]"
       ```
   - Alles installieren:
       ```bash
       pip install "scrapling[all]"
       ```
   Führen Sie `scrapling install` aus, wenn Sie Browser-Fetcher benötigen. HTTP-Anfragen brauchen keine Browser-Installation.

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
    note = {A Python Web Scraping framework for everything from a single request to a full-scale crawl!}
  }
```

## Lizenz

Diese Arbeit ist unter der BSD-3-Clause-Lizenz lizenziert.

## Danksagungen

Dieses Projekt enthält angepassten Code von:
- Parsel (BSD-Lizenz) -- Verwendet für das [translator](https://github.com/D4Vinci/Scrapling/blob/main/scrapling/core/translator.py)-Submodul

---
<div align="center"><small>Entworfen und hergestellt mit ❤️ von Karim Shoair.</small></div><br>
