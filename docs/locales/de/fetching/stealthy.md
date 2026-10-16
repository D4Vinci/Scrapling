---
title: "JavaScript-Websites mit StealthyFetcher auslesen"
description: "Laden Sie Seiten mit JavaScript, warten Sie auf Daten und nutzen Sie Anmeldungen in Scrapling-Browser-Sitzungen weiter. Lesen Sie API-Antworten aus und konfigurieren Sie Proxys und Schutzprüfungen."
---

# Seiten mit StealthyFetcher im Browser abrufen {#browser-fetching-with-stealthyfetcher}

Die Klasse `StealthyFetcher` lädt JavaScript-Seiten und automatisiert Chromium oder Google Chrome mit Funktionen gegen Bot-Erkennung. Sie nutzt die [Playwright-API](https://playwright.dev/python/docs/intro) mit Anpassungen zur Tarnung.

Zum Automatisieren der Seite brauchen Sie einige Kenntnisse der [Page-API von Playwright](https://playwright.dev/python/docs/api/class-page). Darauf kommen wir später zurück.

!!! success "Voraussetzungen"

    1. Sie haben die Seite [Grundlagen der Fetcher](../fetching/choosing.md) gelesen. Sie wissen, was ein [Response-Objekt](../fetching/choosing.md#response-object) ist und welchen Fetcher Sie verwenden möchten.
    2. Sie haben die Seite [Elemente auswählen](../parsing/selection.md) gelesen und wissen, wie Sie Elemente in einem [Selector](../parsing/main_classes.md#selector)/[Response](../fetching/choosing.md#response-object)-Objekt finden und extrahieren.
    3. Sie haben die Seite [Hauptklassen](../parsing/main_classes.md) gelesen und kennen die Eigenschaften und Methoden, die [Response](../fetching/choosing.md#response-object) von [Selector](../parsing/main_classes.md#selector) erbt.

## Grundlegende Verwendung {#basic-usage}
Sie importieren diesen Fetcher auf dieselbe Weise wie alle anderen Fetcher:

```python
from scrapling.fetchers import StealthyFetcher
```
Wie Sie die Parser-Optionen einstellen, erfahren Sie [hier](choosing.md#parser-configuration-in-all-fetchers).

Wir gehen die meisten Argumente einzeln mit Beispielen durch. Eine schnelle Übersicht finden Sie in der [vollständigen Tabelle der Argumente](#full-list-of-arguments).

!!! abstract "Zusammenfassung"

    Die asynchrone Variante von `fetch` heißt `async_fetch`.


Dieser Fetcher bietet drei grundlegende Betriebsarten, die Sie nach Bedarf kombinieren können.

Das sind:

### 1. Mitgeliefertes Chromium {#1-bundled-chromium}
```python
StealthyFetcher.fetch('https://example.com')
```
Dies öffnet das mitgelieferte Chromium mit den Standardeinstellungen zur Tarnung und lädt die Seite.

### 2. Echtes Chrome {#2-real-chrome}
```python
StealthyFetcher.fetch('https://example.com', real_chrome=True)
```
Nutzen Sie diese Option, wenn Google Chrome installiert ist. Sie funktioniert wie die erste Variante, verwendet aber Ihr installiertes Google Chrome statt Chromium. Dadurch wirken die Anfragen echter und lassen sich schwerer als automatisiert erkennen.

Wenn Sie Google Chrome noch nicht installiert haben, können Sie es mit diesem Terminalbefehl für die Bibliothek installieren:
```commandline
playwright install chrome
```

### 3. CDP-Verbindung {#3-cdp-connection}
```python
StealthyFetcher.fetch('https://example.com', cdp_url='ws://localhost:9222')
```
Statt Chromium oder Google Chrome lokal zu starten, können Sie sich über das [Chrome DevTools Protocol](https://chromedevtools.github.io/devtools-protocol/) mit einem entfernten Browser verbinden.

Die URL kann ein WebSocket-Endpunkt sein (`ws://`/`wss://`), wie ihn Browser-Dienste bereitstellen. Auch der HTTP-Endpunkt eines Browsers ist möglich, etwa `http://localhost:9222`.


## Was kann der Fetcher? {#what-does-it-do}

StealthyFetcher bietet diese Funktionen gegen Bot-Erkennung:

1. Mit `solve_cloudflare=True` umgeht er automatisch alle Arten von Cloudflare-Turnstile- und Interstitial-Prüfungen.
2. Er verhindert verräterische Spuren der CDP-Runtime und WebRTC-Lecks.
3. Er isoliert die JavaScript-Ausführung, entfernt viele Playwright-Fingerprints und verhindert die Erkennung anhand bestimmter bekannter Bot-Verhaltensweisen.
4. Er ergänzt zufälliges Canvas-Rauschen, um Fingerprinting über Canvas zu verhindern.
5. Er passt bekannte Merkmale automatisch an, anhand derer der Headless-Modus erkannt wird. Außerdem bietet er eine Option gegen die Erkennung durch abweichende Zeitzonen.
6. Dazu kommen weitere Optionen gegen Schutzmaßnahmen.

## Alle Argumente {#full-list-of-arguments}
Dieser Fetcher und seine Sitzungsklassen bieten viele Optionen. Vor den [Beispielen](#examples) sehen Sie hier die vollständige Liste:


| Argument | Beschreibung | Optional |
|:---------------------:|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|:--------:|
| url | Ziel-URL. | ❌ |
| headless | Mit `True` läuft der Browser ohne sichtbares Fenster (**Standard**), mit `False` mit sichtbarem Fenster. | ✔️ |
| disable_resources | Blockiert unnötige Ressourcen, um das Laden zu beschleunigen. Betroffen sind `font`, `image`, `media`, `beacon`, `object`, `imageset`, `texttrack`, `websocket`, `csp_report` und `stylesheet`. | ✔️ |
| cookies | Cookies für die nächste Anfrage. | ✔️ |
| useragent | Zu verwendende User-Agent-Zeichenkette. **Ohne Angabe erzeugt und verwendet der Fetcher einen echten User-Agent desselben Browsers und derselben Version.** | ✔️ |
| network_idle | Wartet, bis die Seite mindestens 500 ms lang keine Netzwerkverbindungen mehr hat. | ✔️ |
| load_dom | Wartet, bis das gesamte JavaScript der Seite geladen und ausgeführt wurde, also auf den Zustand `domcontentloaded`. Standardmäßig aktiviert. | ✔️ |
| pierce_shadow | Nimmt offene Shadow-DOM-Inhalte in das HTML der Antwort auf. Standardwert: `False`. Kann für die Sitzung festgelegt und pro Anfrage überschrieben werden. | ✔️ |
| timeout | Maximale Wartezeit in Millisekunden für alle Operationen und Wartevorgänge auf der Seite. Standardwert: 30.000 ms, also 30 Sekunden. | ✔️ |
| wait | Zusätzliche Wartezeit in Millisekunden nach Abschluss aller Schritte, bevor der Fetcher die Seite schließt und das `Response`-Objekt zurückgibt. | ✔️ |
| page_action | Funktion zur Automatisierung. Sie erhält das `page`-Objekt und führt nach der Navigation die gewünschten Aktionen aus. | ✔️ |
| page_setup | Funktion, die das `page`-Objekt erhält und vor der Navigation läuft. Registrieren Sie damit Event-Listener oder Routen, die vor dem Laden der Seite bereitstehen müssen. | ✔️ |
| wait_selector | Wartet, bis ein bestimmter CSS-Selektor den angegebenen Zustand erreicht. | ✔️ |
| init_script | Absoluter Pfad einer JavaScript-Datei, die beim Erstellen jeder Seite dieser Sitzung ausgeführt wird. | ✔️ |
| wait_selector_state | Zustand, auf den Scrapling für den mit `wait_selector` angegebenen Selektor wartet. _Standardwert: `attached`._ | ✔️ |
| google_search | Setzt einen Google-Referer-Header. Standardmäßig aktiviert. | ✔️ |
| extra_headers | Dictionary mit zusätzlichen Headern für die Anfrage. _Der Referer aus `google_search` hat Vorrang vor dem hier gesetzten Referer, wenn Sie beide verwenden._ | ✔️ |
| proxy | Proxy für die Anfragen. Möglich sind eine Zeichenkette oder ein Dictionary mit ausschließlich den Schlüsseln 'server', 'username' und 'password'. | ✔️ |
| real_chrome | Aktivieren Sie diese Option, wenn Chrome auf Ihrem Gerät installiert ist. Der Fetcher startet und verwendet dann diesen Browser. | ✔️ |
| locale | Regionale Einstellungen, etwa `en-GB` oder `de-DE`. Sie beeinflussen `navigator.language`, den Anfrage-Header `Accept-Language` sowie Zahlen- und Datumsformate. Standardmäßig werden die Systemeinstellungen verwendet. | ✔️ |
| timezone_id | Ändert die Zeitzone des Browsers. Standardwert: die Zeitzone des Systems. | ✔️ |
| cdp_url | Verbindet sich mit dieser CDP-URL, um einen bestehenden Browser über CDP zu steuern, statt eine neue Instanz zu starten. | ✔️ |
| user_data_dir | Pfad zum Benutzerprofilordner mit Browser-Sitzungsdaten wie Cookies und lokalem Speicher. Standardmäßig wird ein temporärer Ordner erstellt. **Nur mit Sitzungen nutzbar.** | ✔️ |
| extra_flags | Liste zusätzlicher Browser-Optionen für den Start. | ✔️ |
| solve_cloudflare | Löst alle Arten von Cloudflare-Turnstile- und Interstitial-Prüfungen, bevor die Antwort zurückgegeben wird. Standardwert: `False`. | ✔️ |
| block_webrtc | Zwingt WebRTC, die Proxy-Einstellungen zu beachten, um die lokale IP-Adresse nicht offenzulegen. | ✔️ |
| hide_canvas | Ergänzt zufälliges Rauschen bei Canvas-Operationen, um Fingerprinting zu verhindern. | ✔️ |
| allow_webgl | Standardmäßig aktiviert. Beim Deaktivieren werden WebGL und WebGL 2.0 vollständig abgeschaltet. Das ist nicht empfohlen, weil viele WAFs prüfen, ob WebGL aktiv ist. | ✔️ |
| additional_args | Zusätzliche Einstellungen für den Playwright-Kontext. Sie haben Vorrang vor den Scrapling-Einstellungen. | ✔️ |
| selector_config | Dictionary mit eigenen Parser-Argumenten zum Erstellen des endgültigen `Selector`/`Response`-Objekts. | ✔️ |
| blocked_domains | Menge von Domains, an die keine Anfragen gesendet werden. Auch Subdomains werden erfasst: `"example.com"` blockiert zum Beispiel `"sub.example.com"`. | ✔️ |
| block_ads | Blockiert Anfragen an etwa 3.500 bekannte Werbe- und Tracking-Domains. Kann mit `blocked_domains` kombiniert werden. | ✔️ |
| dns_over_https | Leitet DNS-Anfragen über Cloudflares DNS-over-HTTPS, um DNS-Lecks bei der Proxy-Nutzung zu verhindern. | ✔️ |
| proxy_rotator | Eine `ProxyRotator`-Instanz für den automatischen Proxy-Wechsel. Kann nicht mit `proxy` kombiniert werden. | ✔️ |
| retries | Anzahl erneuter Versuche bei fehlgeschlagenen Anfragen. Standardwert: 3. | ✔️ |
| retry_delay | Wartezeit in Sekunden zwischen erneuten Versuchen. Standardwert: 1. | ✔️ |
| record_requests | Speichert abgeschlossene Anfragen und Antworten in `session.network`. Nur für Sitzungen. Standardwert: `False`. | ✔️ |
| max_recorded_requests | Maximale Anzahl gespeicherter Anfrageeinträge pro Sitzung. Standardwert: 1.000. Für gespeicherte Antwortinhalte gelten außerdem feste Größenlimits. | ✔️ |
| executable_path | Absoluter Pfad zu einer eigenen Browserdatei statt des mitgelieferten Chromium. Hilfreich bei besonderen Installationen oder eigenen Browser-Builds. | ✔️ |

In Sitzungsklassen können Sie all diese Argumente für die gesamte Sitzung festlegen. Einstellungen auf Tab-Ebene lassen sich zusätzlich pro Anfrage anpassen. Dazu gehören `google_search`, `timeout`, `wait`, `page_action`, `page_setup`, `extra_headers`, `disable_resources`, `wait_selector`, `wait_selector_state`, `network_idle`, `load_dom`, `pierce_shadow`, `solve_cloudflare`, `blocked_domains`, `proxy` und `selector_config`.

!!! note "Hinweise:"

    1. Mit `disable_resources` waren Anfragen an einige Websites in meinen Tests etwa 25 % schneller. Die Option kann auch Proxy-Datenverkehr sparen. Verwenden Sie sie aber mit Bedacht: Manche Websites werden damit nie vollständig geladen.
    2. `google_search` ist für alle Anfragen standardmäßig aktiviert und setzt den Referer auf `https://www.google.com/`. Es hat Vorrang vor einem Referer in `extra_headers`.
    3. Ohne eigenen User-Agent erzeugt der Fetcher im Headless-Modus einen echten User-Agent derselben Browserversion. Bei sichtbarem Browser nutzt er dessen Standard-User-Agent. Dieser entspricht in aktuellen Versionen dem eines normalen Browsers.
    4. `init_script` wird im Browser-Kontext registriert und beim Erstellen von Seiten ausgeführt. Der Stealth-Modus verwendet standardmäßig den isolierten Ausführungskontext von Patchright. Wenn Ihre `page_action`-Funktion globale Werte lesen muss, die das Skript auf `window` setzt, rufen Sie darin `page.evaluate(..., isolated_context=False)` auf.

## Sitzungen verwalten {#session-management}

Mit `StealthySession`/`AsyncStealthySession` bleibt der Browser für mehrere Anfragen mit derselben Konfiguration offen. Diese Klassen nehmen alle Argumente von `fetch` an. So legen Sie die Einstellungen für die gesamte Sitzung fest.

```python
from scrapling.fetchers import StealthySession


with StealthySession(
    headless=True,
    disable_resources=True,
    real_chrome=True
) as session:

    page1 = session.fetch('https://example1.com')
    page2 = session.fetch('https://example2.com')
    page3 = session.fetch('https://dynamic-site.com')


```

### Asynchrone Sitzungen nutzen {#async-session-usage}

```python
import asyncio
from scrapling.fetchers import AsyncStealthySession

async def scrape_multiple_sites():
    async with AsyncStealthySession(
        network_idle=True,
        timeout=30000,
        max_pages=3
    ) as session:

        pages = await asyncio.gather(
            session.fetch('https://spa-app1.com'),
            session.fetch('https://spa-app2.com'),
            session.fetch('https://dynamic-content.com')
        )
        return pages
```

Das Argument `max_pages` begrenzt die Anzahl der gleichzeitig offenen Tabs in einem **Pool von Browser-Tabs**. Nach einer Anfrage bleiben die Tabs offen. Bei jeder neuen Anfrage geht die Bibliothek so vor:

1. Sie verwendet einen freien Tab, falls einer vorhanden ist. Jede Anfrage setzt ihre eigenen Tab-Einstellungen wie `timeout`, `extra_headers`, `disable_resources` und `blocked_domains`. So werden keine Einstellungen der vorherigen Anfrage übernommen.
2. Andernfalls öffnet sie einen neuen Tab, wenn weniger als `max_pages` Tabs offen sind.
3. Sonst prüft sie in Abständen von weniger als einer Sekunde, ob ein Tab frei wird. Nach 60 Sekunden löst sie `TimeoutError` aus. Das kann passieren, wenn die aufgerufene Website nicht mehr reagiert.

Tabs mit Fehlern werden geschlossen und ersetzt. Mit `session.close_pages()` können Sie jederzeit alle offenen Tabs schließen. Die nächste Anfrage öffnet dann einen neuen.

So können mehrere URLs gleichzeitig im selben Browser geladen werden. Das spart viele Ressourcen und ist vor allem schnell :)

Da die Tabs offen bleiben, ist die zuletzt geladene Seite bei der nächsten Anfrage noch vorhanden. Eine `page_setup`-Funktion dieser Anfrage läuft auf der alten Seite, bevor die Navigation beginnt. So können Sie Automatisierungsschritte über mehrere Anfragen verketten.

Die Versionen 0.3.2 bis 0.4.14 schlossen jeden Tab nach seiner Anfrage, weil Einstellungen bei der Wiederverwendung auf andere Anfragen übergingen. Seit 0.4.15 werden sie bei jeder Wiederverwendung zurückgesetzt. Deshalb bleiben die Tabs jetzt offen.

### Sitzungszustand speichern und laden {#save-and-load-session-state}

Mit `save_state(path)` speichern Sie Cookies, lokalen Speicher und IndexedDB in einer JSON-Datei. Mit `load_state(path)` laden Sie die Datei in einer anderen Sitzung oder ersetzen den gespeicherten Zustand der aktuellen Sitzung. Beide Methoden nehmen eine Zeichenkette oder `pathlib.Path` an und geben `None` zurück. Das Format ist mit den Speicherzustandsdateien von Playwright kompatibel.

```python
from scrapling.fetchers import StealthySession

with StealthySession() as session:
    session.fetch('https://example.com')
    session.save_state('state.json')

with StealthySession() as session:
    session.load_state('state.json')
    page = session.fetch('https://example.com')
```

Speichern Sie nach Abschluss der Anmeldung oder anderer Browser-Aktionen. Rufen Sie beide Methoden in einer gestarteten Sitzung auf, nachdem laufende Abrufe beendet sind. Das Laden ersetzt vorhandene Cookies, lokalen Speicher und IndexedDB. Laden Sie eine Seite neu oder rufen Sie sie ab, um die wiederhergestellte Anmeldung zu nutzen. Bestehende Tabs navigieren beim Laden des Zustands nicht automatisch.

Bei `AsyncStealthySession` verwenden Sie `await`:

```python
from scrapling.fetchers import AsyncStealthySession

async def restore_session():
    async with AsyncStealthySession() as session:
        await session.load_state('state.json')
        page = await session.fetch('https://example.com')
        await session.save_state('state.json')
        return page
```

Diese Methoden speichern und laden nur den gemeinsamen Browser-Kontext. Temporäre Proxy-Kontexte einzelner Anfragen bleiben unberührt. Sitzungen mit `proxy_rotator` haben keinen gemeinsamen Kontext. Daher lösen die Methoden dort `RuntimeError` aus. Ein fester Sitzungs-`proxy` funktioniert wie gewohnt.

Die Datei enthält weder `sessionStorage` noch offene Tabs oder Browser-Einstellungen. Beim Speichern wird sie überschrieben. Ihr übergeordneter Ordner muss vorhanden sein. Datei- und JSON-Fehler werden an den aufrufenden Code weitergegeben.

### Vorteile von Sitzungen {#session-benefits}

- **Browser wiederverwenden**: Weitere Anfragen sind deutlich schneller, weil dieselbe Browser-Instanz genutzt wird.
- **Cookies behalten**: Cookies und Sitzungszustand werden wie in einem normalen Browser automatisch verwaltet.
- **Gleicher Fingerprint**: Alle Anfragen nutzen denselben Browser-Fingerprint.
- **Speicher sparen**: Geringerer Ressourcenbedarf, als für jeden Abruf einen neuen Browser zu starten.


## Beispiele {#examples}
Mit Beispielen wird die Verwendung leichter verständlich.

### Ressourcen steuern {#resource-control}

```python

page = StealthyFetcher.fetch('https://example.com', disable_resources=True)
```

### Shadow DOM {#shadow-dom}

Manche Seiten speichern Inhalte in offenen Shadow-Roots. Diese fehlen im normalen HTML der Seite. Aktivieren Sie `pierce_shadow`, um sie in die Antwort aufzunehmen. Danach können Sie wie gewohnt CSS- oder XPath-Selektoren nutzen:

```python
from scrapling.fetchers import StealthyFetcher

page = StealthyFetcher.fetch('https://example.com', pierce_shadow=True)
titles = page.css('product-card .title::text').getall()
```

Die Option ist standardmäßig `False`. Sie können sie auch für eine Sitzung aktivieren und für eine einzelne Anfrage deaktivieren:

```python
from scrapling.fetchers import StealthySession

with StealthySession(pierce_shadow=True) as session:
    page = session.fetch('https://example.com')
    plain_page = session.fetch('https://example.com', pierce_shadow=False)
```

Dieselbe Option funktioniert mit `async_fetch` und asynchronen Sitzungen.

Es werden nur offene Shadow-Roots erfasst. Geschlossene Shadow-Roots und iframe-Dokumente werden nicht durchlaufen. Nutzen Sie `wait_selector`, wenn eine Komponente erst nach der Seite geladen wird.

Jeder offene Shadow-Root wird in der Antwort von einem `<shadow-root>`-Element umschlossen. Slots behalten ihre Tags und Attribute. Sie enthalten ihre zugewiesenen Knoten oder den Ersatzinhalt, wenn nichts zugewiesen ist. Nicht zugewiesene Kinder aus dem Light DOM werden weggelassen. Die echte Browser-Seite bleibt unverändert.

```html
<product-card>
  <shadow-root>
    <div class="title">Product name</div>
    <slot name="price"><span class="price">20</span></slot>
  </shadow-root>
</product-card>
```

Nachfahren-Selektoren funktionieren auch über diese Elemente hinweg. Selektoren für direkte Kinder müssen die zusätzlichen Elemente und Slots berücksichtigen:

```python
titles = page.css('product-card .title::text').getall()
titles = page.css('product-card > shadow-root > .title::text').getall()
prices = page.css('product-card > shadow-root > slot[name="price"] > .price::text').getall()
```

Diese Elemente und Slots erscheinen in XPath-Pfaden, `.children`, `response.body` und HTML-Exporten. Markdown- und Textextraktion geben ihren Inhalt ohne die Tags zurück. Slot-Attribute, die Inhalte verbergen, bleiben für die Inhaltsbereinigung verfügbar.

Die Momentaufnahme folgt der Inhaltsreihenfolge, berechnet aber weder CSS-Sichtbarkeit noch Layout. Selektoren mit `<shadow-root>` gelten für die Scrapling-Antwort, nicht für die echte Browser-Seite. Andere HTML-Parser können ungewöhnliche Verschachtelungen anders behandeln.

### Domains blockieren {#domain-blocking}

```python

page = StealthyFetcher.fetch('https://example.com', blocked_domains={"ads.example.com", "tracker.net"})
```

### Netzwerk steuern {#network-control}

```python

page = StealthyFetcher.fetch('https://example.com', network_idle=True)


page = StealthyFetcher.fetch('https://example.com', timeout=30000)


page = StealthyFetcher.fetch('https://example.com', proxy='http://username:password@host:port')
```

### Dateien herunterladen {#downloading-files}

```python
page = StealthyFetcher.fetch('https://raw.githubusercontent.com/D4Vinci/Scrapling/main/docs/assets/main_cover.png')

with open(file='main_cover.png', mode='wb') as f:
    f.write(page.body)
```

Das Attribut `body` eines `Response`-Objekts gibt immer `bytes` zurück.

### Vorbereitung vor der Navigation {#pre-navigation-setup}
Mit `page_setup` registrieren Sie Event-Listener, Routen oder Skripte, die vor der Navigation bereitstehen müssen. Die Funktion erhält das `page`-Objekt und läuft vor dem Aufruf von `page.goto()`.

```python
from patchright.sync_api import Page

def capture_websockets(page: Page):
    page.on("websocket", lambda ws: print(f"WebSocket opened: {ws.url}"))

page = StealthyFetcher.fetch('https://example.com', page_setup=capture_websockets)
```
Asynchrone Variante:
```python
from patchright.async_api import Page

async def capture_websockets(page: Page):
    page.on("websocket", lambda ws: print(f"WebSocket opened: {ws.url}"))

page = await StealthyFetcher.async_fetch('https://example.com', page_setup=capture_websockets)
```

Sie können dies mit `page_action` kombinieren. `page_setup` läuft vor der Navigation, `page_action` danach.

### Cloudflare und Tarnungsoptionen {#cloudflare-and-stealth-options}

```python

page = StealthyFetcher.fetch('https://nopecha.com/demo/cloudflare', solve_cloudflare=True)


page = StealthyFetcher.fetch(
    'https://protected-site.com',
    solve_cloudflare=True,
    block_webrtc=True,
    real_chrome=True,
    hide_canvas=True,
    google_search=True,
    proxy='http://username:password@host:port',  # It can also be a dictionary with only the keys 'server', 'username', and 'password'.
)
```

Der Parameter `solve_cloudflare` aktiviert die automatische Erkennung und Lösung aller Arten von Cloudflare-Turnstile- und Interstitial-Prüfungen:

- JavaScript-Prüfungen, die von Cloudflare gesteuert werden
- Interaktive Prüfungen mit Bestätigungskästchen
- Unsichtbare Prüfungen, die automatisch im Hintergrund laufen

Auch eigene Seiten mit eingebettetem Captcha werden unterstützt.

!!! notes "**Wichtige Hinweise:**"

    1. Bei Websites mit eigenen Umsetzungen müssen Sie manchmal `wait_selector` verwenden. So wartet Scrapling nach dem Lösen des Captchas auf den eigentlichen Seiteninhalt. Manche Websites sind echte Sonderfälle, während der Solver möglichst allgemein funktionieren soll.
    2. Für den Cloudflare-Solver sollte die maximale Wartezeit mindestens 60 Sekunden betragen, damit genug Zeit zum Lösen der Prüfung bleibt.
    3. Die Funktion arbeitet mit Proxys und den anderen Tarnungsoptionen zusammen.

### Browser-Automatisierung {#browser-automation}
Hier helfen Kenntnisse der [Page-API von Playwright](https://playwright.dev/python/docs/api/class-page). Die übergebene Funktion erhält das Page-Objekt von Playwright und führt die gewünschten Aktionen aus. Danach setzt der Fetcher seine Arbeit fort.

Die Funktion läuft direkt nach dem Warten auf `network_idle`, falls aktiviert, und vor dem Warten auf `wait_selector`. Sie eignet sich also auch für andere Aufgaben als Automatisierung. Sie können die Seite nach Bedarf verändern.

Im folgenden Beispiel nutze ich [Mausereignisse](https://playwright.dev/python/docs/api/class-mouse), um mit dem Mausrad zu scrollen und danach die Maus zu bewegen.
```python
from patchright.sync_api import Page

def scroll_page(page: Page):
    page.mouse.wheel(10, 0)
    page.mouse.move(100, 400)
    page.mouse.up()

page = StealthyFetcher.fetch('https://example.com', page_action=scroll_page)
```
Bei der asynchronen Abrufmethode muss auch diese Funktion asynchron sein.
```python
from patchright.async_api import Page

async def scroll_page(page: Page):
   await page.mouse.wheel(10, 0)
   await page.mouse.move(100, 400)
   await page.mouse.up()

page = await StealthyFetcher.async_fetch('https://example.com', page_action=scroll_page)
```

### Wartebedingungen {#wait-conditions}

```python

page = StealthyFetcher.fetch(
    'https://quotes.toscrape.com/js-delayed/',
    wait_selector='.quote',
    wait_selector_state='visible'
)
```
Dies ist die letzte ausdrücklich gewählte Wartebedingung vor der Rückgabe der Antwort. Übergeben Sie einen CSS-Selektor an `wait_selector`. Der Fetcher wartet auf den in `wait_selector_state` angegebenen Zustand. Ohne Angabe gilt `attached`: Das Element muss im DOM vorhanden sein.

Danach prüft der Fetcher bei aktiviertem `load_dom`, ob alle JavaScript-Dateien geladen und ausgeführt wurden, also der Zustand `domcontentloaded` erreicht ist. Falls nötig, wartet er weiter. Diese Option ist standardmäßig aktiviert. Wenn Sie `network_idle` aktiviert haben, wartet der Fetcher erneut auf `network_idle`.

Diese Zustände sind möglich ([Quelle](https://playwright.dev/python/docs/api/class-page#page-wait-for-selector)):

- `attached`: Wartet, bis ein Element im DOM vorhanden ist.
- `detached`: Wartet, bis ein Element nicht mehr im DOM vorhanden ist.
- `visible`: Wartet, bis das Element eine nicht leere Begrenzungsbox hat und nicht `visibility:hidden` verwendet. Ein Element ohne Inhalt oder mit `display:none` hat eine leere Begrenzungsbox und gilt nicht als sichtbar.
- `hidden`: Wartet, bis das Element aus dem DOM entfernt ist, eine leere Begrenzungsbox hat oder `visibility:hidden` verwendet. Das ist das Gegenteil von `'visible'`.

### Netzwerkverlauf {#network-history}

Aktivieren Sie `record_requests` in einer Browser-Sitzung, um abgeschlossene Anfragen über Seitenaufrufe, Aktionen und Tabs hinweg zu prüfen. Der Verlauf umfasst alle Kontexte der Sitzung, auch temporäre Proxy-Kontexte. Antworten werden als Scrapling-`Response`-Objekte gespeichert. So finden Sie API-Aufrufe, HTTP-Fehler und Weiterleitungen, ohne Anfragen erneut zu senden. Gespeicherte Header und Antwortinhalte bleiben auch nach dem Schließen der Sitzung lesbar. Fehlgeschlagene und noch laufende Anfragen werden weggelassen. Abgeschlossene HTTP-Antworten mit Status 4xx oder 5xx sind enthalten.

```python
from scrapling.fetchers import StealthySession

with StealthySession(record_requests=True, max_recorded_requests=1000) as session:
    session.fetch('https://example.com', network_idle=True)

for response in session.network.search(resource_type='document', limit=None):
    print(response.meta['network_id'], response.url, response.status)
    if note := response.meta.get('body_note'):
        print(note)
    else:
        print(response.body)
        print(response.css('title::text').get())

session.network.clear()
```

Dieselbe API funktioniert mit `AsyncStealthySession`. Die Aufzeichnung ist standardmäßig deaktiviert. Setzen Sie beim Erstellen der Sitzung `record_requests=True` und bei Bedarf `max_recorded_requests`.

- `session.network.search(url_pattern=None, method=None, resource_type=None, status=None, after_id=0, limit=100, include_static=True)` gibt gespeicherte `Response`-Objekte nach Netzwerk-ID sortiert zurück. Mit `limit=None` erhalten Sie alle noch gespeicherten Treffer. `url_pattern` ist eine Regex, die bei der Suche angewendet wird. Ein ungültiges Muster löst erst dann einen Fehler aus. `after_id` wählt Antworten mit einer höheren Netzwerk-ID aus. Mit `include_static=False` erhalten Sie XHR/fetch-Anfragen und HTTP-Fehler. Mit `True` erhalten Sie alle Ressourcentypen und gespeicherten Weiterleitungen.
- `session.network.get(request_id)` gibt eine gespeicherte `Response` zurück, oder `None`, wenn sie nicht mehr gespeichert ist.
- `session.network.clear()` entfernt den Verlauf. Anfrage-IDs steigen weiter an und werden nie erneut vergeben.

Jede gespeicherte `Response` bietet direkt `.url`, `.method`, `.status`, `.headers`, `.request_headers`, `.body` als Bytes, `.json()` sowie CSS/XPath-Methoden. `.meta` enthält `network_id`, `resource_type` und `request_body`. Letzteres enthält Bytes oder `None`. Header können unvollständig sein, wenn das vollständige Auslesen fehlschlägt. Auch in asynchronen Sitzungen sind dies lokale Zugriffe. Verwenden Sie dafür weder await noch `.body()`. Wenn gespeicherter Inhalt nicht analysiert werden kann, bleiben seine Bytes erhalten. CSS/XPath-Methoden arbeiten dann mit einem leeren Dokument.

Um API-Verkehr nach URL zu finden, verwenden Sie `session.network.search(url_pattern=r'https://api\.example\.com/.*', limit=None)`. Ergänzen Sie `resource_type='fetch'` oder `resource_type='xhr'`, wenn Sie einen bestimmten Anfragetyp brauchen.

Die Aufzeichnung liest und speichert Antwortinhalte nur für unterstützte Textwerte von `Content-Type`: `text/*`, Typen mit `+json`/`+xml` einschließlich SVG, JSON, XML, JavaScript, GraphQL und URL-kodierte Formulardaten. Bei binären oder unbekannten Typen sowie Antworten ohne `Content-Type` bleiben die Metadaten erhalten, aber keine Inhaltsbytes. Der Browser lädt die Ressourcen weiterhin normal.

Gespeicherte Antwortbytes stammen von Playwright und können von den ursprünglichen Bytes des Servers abweichen. Wenn sie gültiges UTF-8 enthalten, nutzt der aufgezeichnete Text UTF-8, wie bei Playwright. Sonst wird der angegebene Zeichensatz verwendet. Die Antwort-Header bleiben unverändert.

Übersprungene, zu große oder nicht lesbare Antwortinhalte liefern `b''`. Der Grund steht in `response.meta.get('body_note')`. Bei Nicht-Text-Inhalten lautet er `Non-text body; not saved.`. Metadaten und verfügbare Header bleiben erhalten. Gespeicherter Text, auch leerer Text, hat keinen solchen Hinweis. HEAD-Antworten und die Statuscodes 204, 205 und 304 bleiben leer und haben ebenfalls keinen Hinweis.

Die Methoden `search`, `get` und `clear` des Verlaufs sind lokale, synchrone Aufrufe, auch in asynchronen Sitzungen. Ein Eintrag erscheint erst, wenn seine Antwort umgewandelt und gespeichert wurde. Browser-Ereignisse werden verarbeitet, während Playwright aktiv ist. Asynchrone Aufzeichnungen brauchen außerdem eine laufende Event-Schleife. Das Lesen des Verlaufs wartet nicht auf laufende Aufzeichnungen.

Auch das Schließen einer Sitzung wartet nicht auf Aufzeichnungen. Was bei einer Navigation oder beim Schließen des Browser-Kontexts noch läuft, kann fehlen. Bereits gespeicherte Antworten bleiben nach dem Schließen lesbar.

Standardmäßig speichert der Verlauf bis zu 1.000 Anfragen. Für jeden Antwortinhalt gilt ein Limit von 1 MiB, für alle zusammen 20 MiB. Beim Erreichen der Speicherlimits werden ältere Einträge entfernt. Die Inhaltslimits sind fest und lassen sich nicht in den Sitzungseinstellungen ändern. Sie betreffen gespeicherte Einträge und Antwortbytes, nicht den gesamten Browserspeicher, gleichzeitige Aufzeichnungen, vorübergehendes vollständiges Auslesen, analysiertes HTML oder Anfrageinhalte.

#### Umstieg auf v5 {#migrating-in-v5}

`capture_xhr` und `response.captured_xhr` wurden in v5 entfernt. Verwenden Sie eine eigene Browser-Sitzung mit `record_requests=True` und lesen Sie dann `session.network.search(url_pattern=..., limit=None)`. Dies ersetzt auch die API-Aufzeichnung über einzelne Fetcher-Aufrufe. Behalten Sie deshalb die Sitzungsinstanz. Filter gelten für den gespeicherten Verlauf der gesamten Sitzung, nicht für die Aufzeichnung oder einen einzelnen Abruf. Es werden nur unterstützte Textinhalte gespeichert. `search()` liefert standardmäßig höchstens 100 Treffer. Mit `limit=None` erhalten Sie alle noch gespeicherten Treffer, ohne die Speicherlimits des Verlaufs zu ändern.

### Browser-Header und regionale Einstellungen {#browser-headers-and-locale}

```python
page = StealthyFetcher.fetch(
    'https://example.com',
    google_search=True,
    useragent='Mozilla/5.0...',
    locale='en-US',
)
```

### Allgemeines Beispiel {#general-example}
```python
from scrapling.fetchers import StealthyFetcher

def scrape_dynamic_content():

    page = StealthyFetcher.fetch(
        'https://example.com/dynamic',
        network_idle=True,
        wait_selector='.content'
    )


    content = page.css('.content')

    return {
        'title': content.css('h1::text').get(),
        'items': [
            item.text for item in content.css('.item')
        ]
    }
```

### Proxy-Wechsel {#proxy-rotation}

```python
from scrapling.fetchers import StealthySession, ProxyRotator


rotator = ProxyRotator([
    "http://proxy1:8080",
    "http://proxy2:8080",
    "http://proxy3:8080",
])


with StealthySession(proxy_rotator=rotator, headless=True) as session:
    page1 = session.fetch('https://example1.com')
    page2 = session.fetch('https://example2.com')


    page3 = session.fetch('https://example3.com', proxy='http://specific-proxy:8080')
```

!!! warning

    Alle Browser-Fetcher und ihre Sitzungen nutzen standardmäßig einen dauerhaften Browser-Kontext mit einem Tab-Pool. Browser können jedoch keinen eigenen Proxy pro Tab setzen. Mit `ProxyRotator` öffnet der Fetcher deshalb für jeden Proxy einen eigenen Kontext mit einem Tab. Nach Abschluss der Aufgabe werden sowohl der Tab als auch sein Kontext geschlossen.

## Wann eignet sich dieser Fetcher? {#when-to-use}

Verwenden Sie StealthyFetcher, wenn Sie:

- Schutzmaßnahmen gegen Bots umgehen müssen.
- einen zuverlässigen Browser-Fingerprint brauchen.
- vollständige JavaScript-Unterstützung brauchen.
- automatische Tarnungsfunktionen nutzen möchten.
- Browser-Automatisierung brauchen.
- mit Cloudflare-Schutz arbeiten.
