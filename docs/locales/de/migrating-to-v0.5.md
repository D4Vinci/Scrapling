---
title: "Migration auf v0.5"
description: "Wechseln Sie von Scrapling v0.4.15 auf v0.5. Aktualisieren Sie Browser-Imports, Netzwerkaufzeichnung, MCP-Tools, CLI-Befehle, Parser-Einstellungen und das Verhalten Ihrer Spider."
---

# Migration auf v0.5 {#migrating-to-v05}

Diese Anleitung beschreibt die Änderungen, die Sie beim Wechsel von **v0.4.15 auf v0.5** prüfen sollten. Sie enthält entfernte APIs, umbenannte Tools und Korrekturen, die Ihre Crawl-Ergebnisse oder gespeicherten Dateien verändern können.

## Kurze Checkliste für die Migration {#quick-migration-checklist}

| Wenn Sie Folgendes verwenden... | Was Sie ändern müssen |
| --- | --- |
| `DynamicFetcher`, `DynamicSession` oder `AsyncDynamicSession` | Verwenden Sie die passende Stealth-Klasse. |
| `capture_xhr` oder `response.captured_xhr` | Verwenden Sie eine Browsersitzung mit `record_requests=True` und `session.network`. |
| `keep_cdata` | Entfernen Sie die Option aus den Parser- und Fetcher-Einstellungen. |
| `scrapling extract stealthy-fetch` oder `stealthy_fetch()` in der Shell | Verwenden Sie stattdessen `fetch`. |
| MCP-Tools | Aktualisieren Sie die Tool-Namen, Screenshot-Aufrufe und die Verarbeitung der Antwort beim Erstellen einer Sitzung. |
| `response.follow()` nach einer POST-Anfrage oder einer Anfrage mit Abfrageparametern | Übergeben Sie Methode, Abfrageparameter und Body erneut, wenn Sie diese benötigen. |
| Gespeicherte Crawl-Checkpoints oder Antwort-Caches | Starten Sie einen neuen Crawl, wenn Ihre Anfragen die geänderten Fingerprint-Eingaben verwenden. |
| `robots_txt_obey=True` | Behandeln Sie Fehler beim Abrufen von robots.txt. Diese blockieren jetzt das Crawling für die betroffene Domain. |

## Abrufen mit dem Browser {#browser-fetching}

### Ersetzen Sie die dynamischen Browserklassen {#replace-the-dynamic-browser-classes}

Das Browser-Backend, das Playwright direkt verwendet hat, wurde entfernt. Alle Browserabrufe nutzen jetzt das Stealth-Backend auf Basis von Patchright.

| Entfernte API | Ersatz |
| --- | --- |
| `scrapling.DynamicFetcher` | `scrapling.StealthyFetcher` |
| `scrapling.fetchers.DynamicFetcher` | `scrapling.fetchers.StealthyFetcher` |
| `scrapling.fetchers.chrome.PlayWrightFetcher` | `scrapling.fetchers.StealthyFetcher` |
| `scrapling.fetchers.DynamicSession` | `scrapling.fetchers.StealthySession` |
| `scrapling.fetchers.AsyncDynamicSession` | `scrapling.fetchers.AsyncStealthySession` |

Das Modul `scrapling.fetchers.chrome` und das private Modul `_browsers._controllers` wurden entfernt. Verwenden Sie die oben genannten öffentlichen Imports.

**Vorher:**

```python
from scrapling.fetchers import DynamicFetcher

page = DynamicFetcher.fetch("https://example.com", headless=True)
```

**Jetzt:**

```python
from scrapling.fetchers import StealthyFetcher

page = StealthyFetcher.fetch("https://example.com", headless=True)
```

Ersetzen Sie bei Sitzungen `DynamicSession` durch `StealthySession` oder `AsyncDynamicSession` durch `AsyncStealthySession`. Ändern Sie auch die Methode `configure_sessions()` Ihres Spiders entsprechend. Die Verwendung von `fetch()` und `async with` bleibt gleich.

Wenn Ihre Callbacks Browsertypen importieren oder Browserfehler abfangen, ersetzen Sie `playwright.sync_api` durch `patchright.sync_api` oder `playwright.async_api` durch `patchright.async_api`. Dazu gehören `Page`, `Locator`, `Error` und `TimeoutError`.

Patchright führt JavaScript standardmäßig in einem isolierten Kontext aus. Wenn ein Callback die JavaScript-Variablen der Seite selbst liest, verwenden Sie `page.evaluate(..., isolated_context=False)`.

Neben dem Importnamen ändert sich auch das Verhalten des Browsers. Prüfen Sie Ihre Browser-Flags und Fingerprint-Einstellungen. Das Lösen von Cloudflare-Prüfungen erfordert weiterhin `solve_cloudflare=True` und ist standardmäßig nicht aktiviert. Außerdem ergänzt `extra_flags` jetzt die eingebauten Stealth-Flags, statt sie zu ersetzen.

Die aktuellen Optionen finden Sie unter [Abrufen mit dem Browser](fetching/stealthy.md).

### Ersetzen Sie die XHR-Erfassung durch den Netzwerkverlauf der Sitzung {#replace-xhr-capture-with-session-network-history}

Der Parameter `capture_xhr` und das Attribut `Response.captured_xhr` wurden entfernt. Entfernen Sie den Parameter auch dann, wenn sein Wert `None` ist. Ein Einzelabruf hängt keine XHR-Liste mehr an seine Antwort an.

Eigene Integrationen, die `ResponseFactory.from_playwright_response()` oder `ResponseFactory.from_async_playwright_response()` aufrufen, müssen ebenfalls `xhr_captured` entfernen. Übergeben Sie `collect_history` als benanntes Argument, um Probleme durch die geänderte Reihenfolge der Positionsargumente zu vermeiden.

**Vorher:**

```python
from scrapling.fetchers import StealthyFetcher

page = StealthyFetcher.fetch("https://example.com", capture_xhr="/api/")
for response in page.captured_xhr:
    print(response.url, response.body)
```

**Jetzt:**

```python
from scrapling.fetchers import StealthySession

with StealthySession(record_requests=True) as session:
    page = session.fetch("https://example.com", network_idle=True)
    for response in session.network.search(url_pattern=r"/api/", limit=None):
        print(response.url, response.body)
```

Verwenden Sie für asynchronen Code `AsyncStealthySession` und `await session.fetch(...)`. Zum Lesen von `session.network` ist kein `await` nötig.

Es gibt einige wichtige Unterschiede:

- Setzen Sie `record_requests=True`, wenn Sie die Sitzung erstellen. Dies ist eine Sitzungseinstellung und keine Einstellung für einzelne Abrufe.
- Der Verlauf gehört zur **gesamten Sitzung**, über Tabs, Seitenaufrufe und Aktionen hinweg. Verwenden Sie `after_id`, Filter oder `session.network.clear()`, wenn Sie einen kleineren Bereich benötigen.
- Verwenden Sie den bisherigen regulären Ausdruck aus `capture_xhr` beim Durchsuchen des Verlaufs als `url_pattern`.
- `search()` gibt gespeicherte `Response`-Objekte zurück. Lesen Sie `.url`, `.status`, `.headers`, `.body` oder `.json()` direkt. Die Aufzeichnungs-ID, der Ressourcentyp und der gesendete Body stehen in `response.meta["network_id"]`, `response.meta["resource_type"]` und `response.meta["request_body"]`.
- Der Python-Verlauf enthält standardmäßig alle Ressourcentypen. Verwenden Sie `resource_type="xhr"` oder `resource_type="fetch"`, um einen auszuwählen, oder `include_static=False` für XHR/fetch-Anfragen zusammen mit HTTP-Fehlern.
- `search()` gibt standardmäßig höchstens 100 Treffer zurück. Übergeben Sie `limit=None` für alle gespeicherten Treffer. Sitzungen behalten standardmäßig höchstens 1.000 Anfragen; ändern Sie dies mit `max_recorded_requests`.
- Nur abgeschlossene Anfragen werden gespeichert. Die Body-Erfassung ist auf unterstützte Textinhaltstypen, 1 MiB pro Antwort und insgesamt 20 MiB gespeicherte Body-Daten begrenzt. Ältere Einträge können beim Erreichen der Grenzen entfernt werden. In `response.meta.get("body_note")` finden Sie den Grund, warum ein Body ausgelassen wurde.
- Das Lesen des Verlaufs oder das Schließen der Sitzung wartet nicht auf ausstehende Aufzeichnungen. Warten Sie auf die benötigten Daten, bevor Sie sie lesen. Der gespeicherte Python-Verlauf bleibt nach dem Schließen der Sitzung lesbar.

Filter und Grenzen finden Sie unter [Netzwerkverlauf](fetching/stealthy.md#network-history).

## Parser-Einstellungen {#parser-settings}

### Entfernen Sie `keep_cdata` {#remove-keep_cdata}

`keep_cdata` wurde aus `Selector`, der Fetcher-Konfiguration und den von `display_config()` zurückgegebenen Einstellungen entfernt. Entfernen Sie die Option aus direkten Parser-Aufrufen, `Fetcher.configure(...)` und den `selector_config`-Dictionaries, die Sie an Fetcher oder Integrationen übergeben.

**Vorher:**

```python
from scrapling import Selector

page = Selector("<p>Hello</p>", keep_cdata=True)
```

**Jetzt:**

```python
from scrapling import Selector

page = Selector("<p>Hello</p>")
```

Es gibt keine Ersatzeinstellung. Sie hatte keinen Einfluss auf die Ausgabe des HTML-Parsers. Wenn Sie Parser-Optionen als Positionsargumente übergeben haben, entfernen Sie das alte Argument `keep_cdata` und verwenden Sie für `adaptive` und die Speicheroptionen benannte Argumente.

## Kommandozeile und interaktive Shell {#command-line-and-interactive-shell}

### Verwenden Sie `fetch` für Browseranfragen {#use-fetch-for-browser-requests}

Die CLI hat jetzt nur noch einen Browserbefehl: `scrapling extract fetch`. Er verwendet `StealthyFetcher`.

**Vorher:**

```bash
scrapling extract stealthy-fetch "https://example.com" page.md
```

**Jetzt:**

```bash
scrapling extract fetch "https://example.com" page.md
```

Wenn Sie bereits `scrapling extract fetch` verwenden, bleibt der Befehlsname gleich. Das Backend wechselt aber von `DynamicFetcher` zu `StealthyFetcher`. Optionen wie `--solve-cloudflare` gehören jetzt zu `fetch`.

Ersetzen Sie in `scrapling shell` den Aufruf `stealthy_fetch(...)` durch `fetch(...)`. Die vorhandene Kurzform `fetch(...)` ruft jetzt `StealthyFetcher.fetch` auf. Die dynamischen Klassen werden nicht mehr zum Namensraum der Shell hinzugefügt.

### Lesen Sie Markdown- und Textdateien als UTF-8 {#read-markdown-and-text-files-as-utf-8}

Die Extraktionsbefehle und `Convertor.write_content_to_file()` schreiben `.md`- und `.txt`-Dateien jetzt in **UTF-8**, unabhängig vom Zeichensatz der Quellseite. Aktualisieren Sie Code, der diese Dateien mit der ursprünglichen Kodierung der Seite liest. Die `.html`-Ausgabe verwendet weiterhin `page.encoding`.

Markdown aus mehreren ausgewählten Elementen enthält jetzt Leerzeilen zwischen den Elementen. Das gilt für `Response.markdown()` und die Ausgabe in Markdown-Dateien. Aktualisieren Sie exakte Ausgabevergleiche oder gespeicherte Hashes, die vom zusammengefügten Text abhingen.

## MCP-Server {#mcp-server}

Aktualisieren Sie gespeicherte Prompts, Listen erlaubter Tools, Wrapper und die Tool-Definitionen Ihres MCP-Clients. Starten Sie den MCP-Client nach der Serveraktualisierung neu oder verbinden Sie ihn erneut, damit er die aktuellen Tools einliest.

### Aktualisieren Sie Tool-Namen und Sammelaufrufe {#update-tool-names-and-bulk-calls}

| Tool in v0.4.15 | Ersatz in v0.5 |
| --- | --- |
| `fetch`, `stealthy_fetch` | `browser_fetch_once` |
| `open_session` | `browser_open` |
| `session_fetch` | `browser_fetch` |
| `screenshot` | `browser_screenshot` |
| `bulk_fetch`, `bulk_stealthy_fetch` | Ein Aufruf von `browser_fetch_once` pro URL oder wiederholte Aufrufe von `browser_fetch` über eine offene Sitzung |
| `bulk_get` | Ein Aufruf von `make_request` oder `session_make_request` pro URL |

Alle Tools für Sammelabrufe wurden entfernt. Abruf-Tools für eine einzelne URL geben ein `ResponseModel` mit `status`, `content` und `url` zurück, keine Liste von Antworten. `content` selbst bleibt eine Liste von Zeichenfolgen.

Alle MCP-Browsertools verwenden jetzt das Stealth-Backend. Entfernen Sie `session_type` aus Aufrufen von `browser_open`; die Auswahl eines dynamischen Browsers entfällt. Das Ergebnis enthält `session_type="stealthy"`. HTTP-Sitzungen verwenden weiterhin `open_request_session` und geben `session_type="static"` zurück.

Python-Integrationen dürfen auch `BrowserSessionType` nicht mehr importieren, da dieser Typ entfernt wurde. `SessionType` akzeptiert jetzt nur noch `"stealthy"` und `"static"`.

Aufrufe über dieselbe Browsersitzung müssen nacheinander ausgeführt werden, weil sie eine Seite gemeinsam nutzen. Schließen Sie Sitzungen mit `close_session`, wenn Sie fertig sind.

### Lesen Sie Einstellungen über `list_sessions` {#read-settings-through-list_sessions}

`browser_open` und `open_request_session` geben jetzt nur noch Folgendes zurück:

```json
{
  "session_id": "my-session",
  "session_type": "stealthy"
}
```

Das Ergebnis der Sitzungserstellung enthält nicht mehr `created_at`, `is_alive`, `settings` oder `message`. Rufen Sie `list_sessions` für die ersten drei Felder auf. Die Bestätigung `message` wurde entfernt. Code, der davon ausgeht, dass `SessionCreatedModel` alle Felder von `SessionInfo` enthält, muss ebenfalls angepasst werden.

### Rufen Sie die Seite vor einem Screenshot ab {#fetch-before-taking-a-screenshot}

`browser_screenshot` erfasst die **aktuelle Seite, ohne sie neu zu laden**. Das Tool akzeptiert keine URL und keine der alten Navigations- und Warteoptionen mehr: `wait`, `wait_selector`, `wait_selector_state` und `network_idle`.

Gehen Sie in dieser Reihenfolge vor:

1. Rufen Sie `browser_open` auf.
2. Rufen Sie `browser_fetch` mit der URL und den benötigten Optionen zum Laden der Seite auf.
3. Rufen Sie bei Bedarf `browser_actions` auf, um mit der Seite zu interagieren oder auf Inhalte zu warten.
4. Rufen Sie `browser_screenshot` mit der Sitzungs-ID auf.
5. Rufen Sie `close_session` auf, wenn Sie fertig sind.

Die Argumente für einen Screenshot der gesamten Seite sehen zum Beispiel so aus:

```json
{
  "session_id": "my-session",
  "full_page": true
}
```

`timeout` begrenzt bei diesem Tool jetzt die Erstellung des Screenshots. Das Tool lädt keine Seite. Verwenden Sie für den Screenshot eines Elements entweder `selector` oder `ref` und setzen Sie nicht `full_page=true`.

Screenshots geben weiterhin Bild- und Textinhaltsblöcke zurück. Der Textblock enthält die URL der aktuellen Seite. Sie geben kein Abruf-`ResponseModel` zurück.

Die vollständigen Schemas finden Sie in der [MCP-Anleitung](ai/mcp-server.md) und der [API-Referenz](api-reference/mcp-server.md).

## Spider und HTTP-Anfragen {#spiders-and-http-requests}

### Übergeben Sie Anfragedaten erneut, wenn Sie einem Link folgen {#pass-request-data-again-when-following-a-link}

`response.follow()` kopiert `method`, `params`, `data`, `json`, `files` oder `multipart` nicht mehr aus der vorherigen Anfrage. Außerdem werden geerbte `Content-Length`-Header aus `headers` und `extra_headers` entfernt.

Ein verfolgter Link beginnt jetzt als einfache GET-Anfrage, sofern Sie keine Anfragedaten ausdrücklich übergeben. Andere gemeinsame Einstellungen wie Sitzung, Proxy und Callbacks folgen weiterhin den bestehenden Vererbungsregeln.

Wenn Ihr bisheriger Code auf geerbte POST-Daten angewiesen war, ersetzen Sie:

```python
yield response.follow("/next")
```

durch:

```python
yield response.follow("/next", method="POST", json={"page": 2})
```

Übergeben Sie auch `params` ausdrücklich, wenn die nächste Anfrage sie benötigt. Lassen Sie den HTTP-Client den neuen `Content-Length` berechnen.

### Prüfen Sie Anfrage-Fingerprints und den gespeicherten Crawl-Zustand {#check-request-fingerprints-and-saved-crawl-state}

Ein Anfrage-Fingerprint ist der Schlüssel, mit dem doppelte Anfragen erkannt und Antworten im Cache gefunden werden. Drei Fälle werden bei seinen Eingaben jetzt anders behandelt:

- `params` werden vor der Schlüsselbildung in die URL aufgenommen. Anfragen an dieselbe URL mit unterschiedlichen Abfrageparametern gelten standardmäßig nicht mehr als Duplikate.
- JSON-Bodys wie `{}`, `[]`, `false`, `0` und `""` bleiben im Schlüssel erhalten. Sie haben nicht mehr denselben Schlüssel wie ein fehlender Body. `None` bedeutet weiterhin, dass kein JSON-Body vorhanden ist.
- Bei `fp_include_headers=True` ändert eine andere Einfügereihenfolge der Header allein den Schlüssel nicht mehr.

Wenn Ihr Crawl diese Eingaben verwendet, schließen Sie ihn vor der Aktualisierung ab oder starten Sie einen neuen Crawl mit einem neuen Checkpoint und einem neuen Verzeichnis für den Antwort-Cache. Alte gespeicherte Schlüssel können von den neuen abweichen. Dies ändert die Identität einer Anfrage, nicht das Dateiformat der Checkpoints.

Der Entwicklungsmodus schreibt Antworten jetzt erst nach der Prüfung auf blockierte Antworten in den Cache. Blockierte Seiten werden nicht als erfolgreiche Ergebnisse im Cache gespeichert. Vorhandene Cache-Dateien werden nicht automatisch bereinigt. Löschen Sie veraltete Einträge, wenn Sie zuvor eine Prüfseite im Cache gespeichert haben.

Fehlgeschlagene Crawls behalten jetzt ihre Checkpoint-Dateien. Prüfen Sie Ihren Bereinigungscode, falls er davon ausging, dass diese Dateien nach einem Fehler verschwinden. Siehe [Pausieren und fortsetzen](spiders/advanced.md#pause-resume) und [Entwicklungsmodus](spiders/advanced.md#development-mode).

### Prüfen Sie Fehler beim Abrufen von robots.txt {#check-robotstxt-failures}

Mit `robots_txt_obey=True` blockiert eine Ausnahme beim Abrufen von robots.txt oder eine Antwort außerhalb von HTTP 200 oder 4xx jetzt Anfragen an diese Domain. Zuvor erlaubten solche Fehler das Crawling. HTTP 200 liefert weiterhin die Regeln, und HTTP 4xx erlaubt weiterhin den Zugriff.

Das Ergebnis wird für den gesamten Crawl zwischengespeichert. Beheben Sie das Zugriffsproblem bei robots.txt und starten Sie einen neuen Crawl. Spätere Anfragen im selben Crawl wiederholen den fehlgeschlagenen Abruf nicht. Der Standardwert `robots_txt_obey=False` bleibt unverändert.

### Prüfen Sie Link-Einschränkungen und Sitemap-Callbacks {#check-link-restrictions-and-sitemap-callbacks}

- Eine `LinkExtractor`-Einschränkung ohne Treffer gibt jetzt keine Links zurück. Sie greift nicht mehr auf die gesamte Seite zurück. Korrigieren Sie den Ausdruck `restrict_css` oder `restrict_xpath`, wenn Ihr Crawl jetzt weniger Links findet.
- Eine Einschränkung kann jetzt das Link-Element selbst auswählen, nicht nur ein übergeordnetes Element. Dadurch können Links hinzukommen, die zuvor fehlten. Prüfen Sie die erwarteten URL-Mengen.
- `SitemapSpider` sendet Seiten-URLs jetzt an `parse()`, wenn keine Regeln vorhanden sind oder eine passende Regel `callback=None` hat. Diese HTML-Seiten werden nicht mehr an den Sitemap-Parser zurückgesendet. Implementieren Sie für diese Fälle `parse()` und entfernen Sie Umgehungslösungen für die alte Weiterleitung.
- Ein führendes Unicode-Byte-Order-Mark wird aus robots.txt und CSV-Feeds entfernt. Die erste robots-Anweisung wird jetzt wirksam, und die erste CSV-Spaltenüberschrift beginnt nicht mehr mit `\ufeff`. Wenn Sie eigene `headers` festlegen, wird die Markierung stattdessen aus dem ersten Feldwert entfernt. Aktualisieren Sie Code, der dieses unsichtbare Präfix umgangen hat. XML-Kommentare und Verarbeitungsanweisungen in Sitemaps werden ebenfalls übersprungen, statt einen Parserfehler auszulösen.

### Prüfen Sie Formulardaten, Header und CLI-JSON {#check-form-data-headers-and-cli-json}

Bei Formulardaten in Dictionaries werden Listen- und Tupelwerte jetzt als wiederholte Schlüssel gesendet. Zum Beispiel sendet `data={"tag": ["a", "b"]}` die Daten `tag=a&tag=b`. Eine leere Liste sendet keinen Eintrag für diesen Schlüssel. Wenn Sie keinen eigenen Content-Type-Header angegeben haben, wird standardmäßig `Content-Type: application/x-www-form-urlencoded` hinzugefügt.

Wenn Sie ein anderes Übertragungsformat benötigen, übergeben Sie eine ausdrücklich kodierte Zeichenfolge oder Bytes. `json`, rohe `content`-Daten und Multipart-Uploads behalten ihre eigene Body-Verarbeitung. `None`-Werte werden **nicht entfernt**, weder aus Formulardaten noch aus Abfrageparametern. Sie bleiben als Zeichenfolge `None` erhalten.

HTTP-Header einzelner Anfragen überschreiben jetzt Sitzungs-Header unabhängig von der Groß- und Kleinschreibung. Ein Anfrage-Header namens `authorization` ersetzt den `Authorization`-Header der Sitzung, statt beide zu senden. Entfernen Sie Code, der doppelte Headernamen umgangen hat.

Die CLI-JSON-Werte `{}`, `[]`, `false`, `0` und `""` werden jetzt gesendet, statt ohne Hinweis ausgelassen zu werden. Außerdem übernimmt `curl2fetcher()` jetzt den User-Agent aus der curl-Option `-A` und übergibt Proxys aus `-x` korrekt als URL-Zeichenfolge. Ein ausdrücklich angegebener curl-Header `-H 'User-Agent: ...'` hat weiterhin Vorrang vor `-A`.

## Weitere Änderungen an der Ausgabe prüfen {#other-output-changes-to-check}

Diese Korrekturen entfernen keine APIs, können aber gespeicherte Ergebnisse und Tests mit exakten Ausgabevergleichen verändern:

- Erzeugte CSS- und XPath-Selektoren enthalten jetzt bei Bedarf `:nth-of-type(1)` oder `[1]`, um das erste von mehreren gleichnamigen Geschwisterelementen zu erkennen. Aktualisieren Sie erwartete Selektor-Zeichenfolgen. Entfernen Sie die neue Positionsangabe nicht.
- Bei der Bereinigung von KI-Inhalten bleiben jetzt sichtbare Elemente mit Werten wie `opacity:0.95` erhalten. Die Bereinigung erkennt mehr Varianten von Inline-Stilen zum Ausblenden und entfernt die betroffenen Elemente. Sie entfernt auch `<slot hidden>`-Elemente sowie alle passenden störenden Tags, selbst wenn diese verschachtelt sind. Prüfen Sie erneut die exakte Ausgabe von Markdown, Text und bereinigtem HTML.
- Die Umwandlung von Browserantworten liest jetzt charset-Angaben mit abweichender Groß- und Kleinschreibung, Leerzeichen oder Werten in Anführungszeichen, etwa `text/plain; CHARSET = "iso-8859-15"`. Antworten ohne HTML mit diesen Headern verwenden jetzt die angegebene Kodierung, statt auf UTF-8 zurückzufallen. Prüfen Sie den aus diesen Antworten dekodierten Text erneut.

## Prüfen Sie Ihre Aktualisierung {#verify-your-upgrade}

Führen Sie vor dem vollständigen Auftrag einen kleinen Crawl aus. Prüfen Sie die extrahierten Daten, die verfolgten URLs, die gesendeten Anfrage-Bodys, die Kodierung gespeicherter Dateien und das Verhalten von Cache und Checkpoints, auf das Sie angewiesen sind. Prüfen Sie bei MCP-Integrationen die Tool-Eingaben und die zurückgegebenen Daten anhand der aktuellen Schemas.

Änderungen älterer Versionen finden Sie im [Änderungsprotokoll](changelog.md).
