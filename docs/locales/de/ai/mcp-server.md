---
title: "Scrapling-MCP-Server: Einrichtung und Datenextraktion"
description: "Verbinden Sie einen KI-Client mit Scrapling für HTTP- und Browser-Scraping. Nutzen Sie Sitzungen, gespeicherten Anmeldestatus, Browser-Aktionen, gezielte Extraktion und den API-Verlauf."
---

# Anleitung zum MCP-Server von Scrapling {#scrapling-mcp-server-guide}

<iframe width="560" height="315" src="https://www.youtube.com/embed/NHwWEiTOoPQ" title="YouTube-Videoplayer" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>

Der **MCP-Server von Scrapling** stellt die Web-Scraping-Funktionen von Scrapling direkt in Ihrem KI-Chatbot oder KI-Agenten bereit. So können Sie im Gespräch Websites abrufen, Daten extrahieren und Bot-Schutz umgehen. Das funktioniert in Claude und jeder anderen Oberfläche, die MCP unterstützt.

## Funktionen {#features}

Der MCP-Server von Scrapling bietet sechzehn Werkzeuge für Web Scraping und Browser-Aktionen. Werkzeuge für Einzelaufrufe rufen eine URL ab und schließen danach ihren Browser oder Client. Sitzungswerkzeuge behalten Cookies und Einstellungen zwischen Aufrufen. So kann die KI im selben Tab weiterarbeiten und den Netzwerkverlauf prüfen.

### Werkzeuge für Einzelaufrufe {#one-shot-tools}

#### 🚀 Einfaches HTTP-Scraping {#basic-http-scraping}

- **`make_request`**: Schnelle HTTP-Anfragen mit beliebiger Methode (GET, POST, PUT, DELETE) und nachgebildetem Browser-Fingerprint. Das Werkzeug erzeugt echte Browser-Header passend zur TLS-Version und unterstützt HTTP/3 sowie weitere Optionen.

#### 🔒 Scraping mit dem Stealthy-Browser {#stealth-browser-scraping}

- **`browser_fetch_once`**: Führt JavaScript aus und extrahiert Daten dynamischer Seiten mit unserem Stealthy-Browser. Es unterstützt das Nachbilden von Fingerprints, das Umgehen von Cloudflare Turnstile und Interstitial sowie die Steuerung von Browser und Anfrage.

### Sitzungswerkzeuge {#session-tools}

#### 🔌 Sitzungen verwalten {#session-management}

- **`browser_open`**: Erstellt eine dauerhafte Stealthy-Browser-Sitzung, die über mehrere `browser_fetch`-Aufrufe hinweg offen bleibt. So muss nicht jedes Mal ein neuer Browser starten. Sie speichert die Browser-Konfiguration und gibt nur `session_id` und `session_type` zurück. Mit `list_sessions` sehen Sie die tatsächlich verwendeten `settings`. Bei CDP-Sitzungen ist dieser Wert leer.
- **`open_request_session`**: Erstellt eine dauerhafte HTTP-Sitzung ohne Browser zur Verwendung mit `session_make_request`. Sie behält Cookies, Verbindungen und den Browser-Fingerprint (`impersonate`) zwischen Anfragen. Sie gibt nur `session_id` und `session_type` mit dem Typ `static` zurück. Mit `list_sessions` sehen Sie die tatsächlich verwendeten `settings`.
- **`close_session`**: Schließt eine dauerhafte Browser- oder HTTP-Sitzung und gibt ihre Ressourcen frei.
- **`list_sessions`**: Listet alle aktiven Sitzungen mit ihren Details und `settings` auf.

#### Browser-Zustand {#browser-state}

- **`browser_save_state`**: Speichert Cookies, Local Storage und IndexedDB in einer mit Playwright kompatiblen JSON-Datei. So können Sie den Anmeldestatus auch nach dem Ende der Browser-Sitzung wiederverwenden. Eine vorhandene Datei wird beim Speichern ersetzt.
- **`browser_load_state`**: Lädt eine gespeicherte Datei in eine offene Browser-Sitzung, auch vor dem ersten Seitenaufruf. Der aktuelle gespeicherte Zustand wird ersetzt. Bestehende Tabs bleiben offen und wechseln nicht die Seite. Rufen Sie die Seite ab oder laden Sie sie neu, um die wiederhergestellte Anmeldung zu nutzen.

Die Zustandsdateien liegen auf dem Rechner, auf dem der MCP-Server läuft. Sie enthalten weder `sessionStorage` noch offene Tabs oder Browser-Einstellungen.

#### 🎯 Seiten in einer Sitzung abrufen {#fetching-through-a-session}

- **`browser_fetch`**: Führt JavaScript aus und extrahiert Daten einer URL in einer offenen Stealthy-Browser-Sitzung. Es unterstützt das Nachbilden von Fingerprints und das Umgehen von Cloudflare Turnstile und Interstitial. Es kann auch eine strukturierte Seitenansicht mit Referenzen, Positionen und Größen der Elemente erstellen. Damit kann die KI Bedienelemente erkennen und Mausaktionen planen.
- **`session_make_request`**: Sendet schnelle HTTP-Anfragen mit beliebiger Methode (GET, POST, PUT, DELETE), nachgebildetem Browser-Fingerprint, passenden Browser-Headern und HTTP/3-Unterstützung. Es verwendet Cookies, Verbindungen und den Browser-Fingerprint einer mit `open_request_session` geöffneten Sitzung erneut.

#### 📸 Screenshots {#screenshots}

- **`browser_screenshot`**: Erstellt einen Screenshot der aktuellen Seite oder eines Elements als PNG oder JPEG, ohne die Seite neu zu laden. Damit lassen sich ausgefüllte Felder, offene Menüs, Diagramme oder Ergebniskarten prüfen. Ein Screenshot eines einzelnen Elements enthält weniger unnötige Inhalte. Das Werkzeug unterstützt den sichtbaren Bereich, die ganze Seite oder ein Element sowie eine einstellbare JPEG-Qualität. Der Screenshot wird als echter Bildinhaltsblock zurückgegeben, den das Modell direkt sehen kann.

#### Inhalt der aktuellen Seite {#current-page-content}

- **`browser_extract`**: Liest die aktuelle Seite oder ein Element als strukturierte Ansicht für die KI, HTML, Markdown oder Text, ohne neu zu laden. Damit lassen sich Ergebnisse nach dem Ausfüllen von Formularen oder dem Nachladen von Inhalten extrahieren. Die Ansichten enthalten Rollen, Namen, Referenzen, Positionen und Größen der Elemente für weitere Aktionen. Eine Regex-Suche gibt passende Zeilen mit nahem Kontext und übergeordneten Knoten zurück.

#### Browser-Aktionen {#browser-actions}

- **`browser_actions`**: Verbindet Mausaktionen, das Ausfüllen von Feldern, Tastenkürzel, Antworten auf Dialoge und Wartebedingungen in einem Aufruf. Es kann Browser-Meldungen und Bestätigungen annehmen oder schließen und Text in Eingabedialoge schreiben. Zum Beispiel: ein Suchfeld ausfüllen, die Suche senden, Ergebnisse abwarten und ein Ergebnis öffnen. Die KI kann bekannte Schritte zusammenfassen und separate Seitenansichten anfordern, wenn sie eine Änderung prüfen muss. Dadurch muss der Agent nicht für jeden Schritt einen eigenen Aufruf senden. Das hilft bei kurz eingeblendeten Menüs und anderen Bedienelementen, die eine schnelle Folgeaktion erfordern.

    Zeigen Sie Menüs und Tooltips durch Überfahren mit der Maus an, klicken Sie auf Schaltflächen und Links oder bewegen Sie die Maus über einen verschachtelten Bereich, um dort senkrecht oder waagerecht zu scrollen. Bewegungen und Klicks unterstützen Selektoren, Referenzen aus der Seitenansicht und Koordinaten. Bei Zielelementen wartet das Werkzeug automatisch auf das Element und scrollt es ins Blickfeld. Es unterstützt Bewegungen über mehrere Koordinatenschritte, Links-, Rechts- und Mittelklicks sowie Doppelklicks.

    Wählen Sie Felder überall auf der Seite mit Selektoren oder Referenzen aus. Geben Sie Text ein, aktivieren oder deaktivieren Sie Kontrollkästchen, wählen Sie Optionsfelder und eine oder mehrere native Dropdown-Optionen anhand ihrer sichtbaren Beschriftung. Text kann den bisherigen Inhalt ersetzen, ihn löschen oder an der aktuellen Cursorposition fortsetzen. Tastenkürzel können Text auswählen und löschen, den Fokus wechseln, Formulare absenden oder Menüs schließen. Der langsame Modus tippt ein Zeichen nach dem anderen und macht zufällige Pausen zwischen Zeichen und allen Aktionen.

    Warten Sie auf Ergebnisse, das Verschwinden von Ladeanzeigen oder Ereignisse beim Laden der Seite, bevor die nächste Aktion beginnt. Feste Pausen und das Warten, bis die Netzwerkaktivität zur Ruhe kommt werden ebenfalls unterstützt.

#### JavaScript {#javascript}

- **`browser_evaluate`**: Führt JavaScript auf der aktuellen Seite aus, etwa für eigene Extraktionen, Berechnungen oder Aufgaben, die von der Seite abhängen. Die KI kann Daten aus mehreren Elementen sammeln, den Anwendungszustand lesen oder Seiteninhalte ändern. Das Werkzeug unterstützt asynchrone Skripte und gibt ihre Ergebnisse als JSON zurück.

#### Netzwerkverlauf {#network-history}

- **`browser_network_requests`**: Sucht abgeschlossene Anfragen über Tabs, Seitenaufrufe und Browser-Aktionen hinweg. Finden Sie die API-Aufrufe hinter den Daten einer Seite, prüfen Sie HTTP-Fehler und verfolgen Sie gespeicherte Weiterleitungen. Statische Ressourcen werden standardmäßig ausgeblendet, um die Ausgabe klein zu halten. Die Anfragedetails werden als JSON zurückgegeben, bei langen Verläufen auf mehrere Ergebnisseiten verteilt.
- **`browser_network_request`**: Zeigt die Zusammenfassung, Header, gesendeten Daten oder den textuellen Antwortkörper einer gespeicherten Anfrage als strukturiertes JSON. Der gewählte Teil wird vollständig zurückgegeben, ohne die Seite zu laden oder die Anfrage erneut zu senden. Gespeicherte Antworten bleiben nach einem Seitenwechsel verfügbar. Größenlimits begrenzen den Verlauf. Ein Hinweis erklärt, warum ein Antwortkörper nicht textuell, zu groß oder nicht lesbar ist. Lesen Sie benötigte Details, bevor Sie die MCP-Sitzung schließen.

Antwortkörper werden nur für unterstützte textuelle `Content-Type`-Werte gelesen und gespeichert, zum Beispiel HTML, JSON, XML oder JavaScript. Bei binären, fehlenden oder unbekannten Inhaltstypen werden nur Metadaten und Header der Anfrage behalten. Ihr Antwortkörper wird weder gelesen noch gespeichert. Der Browser lädt Ressourcen weiterhin normal.

Nur abgeschlossene Anfragen werden gespeichert, einschließlich HTTP-Antworten mit 4xx und 5xx. Fehlgeschlagene und noch laufende Anfragen werden ausgelassen. Einträge erscheinen nach Abschluss der Erfassung. Das Lesen des Verlaufs oder Schließen der Sitzung wartet nicht darauf. Erfassungen, die bei einem Seitenwechsel oder beim Schließen noch laufen, können fehlen. Gespeicherte Bytes stammen aus dem Browser und können von den Server-Bytes abweichen. Gültiger Text wird wie bei Playwright als UTF-8 dekodiert. Andernfalls wird die angegebene Zeichenkodierung verwendet.

### Shadow DOM {#shadow-dom}

Setzen Sie `pierce_shadow=true` bei `browser_fetch_once` oder jedem `browser_fetch`-Aufruf, um Inhalte offener Shadow DOMs einzubeziehen. Der Standardwert ist `false`. Im Abschnitt [Shadow DOM](../fetching/stealthy.md#shadow-dom) finden Sie Selektorbeispiele und Einschränkungen.

Browser-Selektoren können auch Elemente in geschlossenen Shadow DOMs ansprechen und mit ihnen interagieren.

### Wichtigste Möglichkeiten {#key-capabilities}

- **Inhalte extrahieren**: Wandeln Sie Webseiten oder Elemente in Markdown oder HTML um, oder extrahieren Sie bereinigten Text.
- **CSS-Selektoren**: Wählen Sie mit Scrapling bestimmte Elemente aus, bevor Sie den Inhalt an die KI übergeben.
- **Bot-Schutz umgehen**: Bewältigen Sie Cloudflare Turnstile, Interstitial und andere Schutzsysteme.
- **Proxies**: Verwenden Sie Proxies für Anonymität und Anfragen aus bestimmten Regionen.
- **Browser nachbilden**: Bilden Sie echte Browser mit TLS-Fingerprint, passenden Browser-Headern und weiteren Optionen nach.
- **Dauerhafte Sitzungen**: Verwenden Sie Browser-Sitzungen für mehrere Anfragen erneut, um die Leistung zu verbessern.
- **Werbeblocker**: Alle Browser-Werkzeuge blockieren automatisch Anfragen an etwa 3.500 bekannte Werbe- und Tracking-Domains. Das spart Tokens und beschleunigt das Laden.
- **Schutz vor Prompt Injection**: Entfernt automatisch versteckte Inhalte, die für Angriffe auf das Modell verwendet werden könnten: durch Inline-Styles versteckte Elemente, aria-hidden, versteckte Slots, Zeichen mit der Breite null, HTML-Kommentare und template-Tags.

## Installation {#installation}

Installieren Sie Scrapling mit MCP-Unterstützung und prüfen Sie, ob auch die Browser-Abhängigkeiten installiert sind.

```bash
# Install Scrapling with MCP server dependencies
pip install "scrapling[ai]"

# Install browser dependencies
scrapling install
```

Sie können auch das Docker-Image direkt aus der Docker-Registry verwenden:
```bash
docker pull pyd4vinci/scrapling
```
Oder es aus der GitHub-Registry herunterladen:
```bash
docker pull ghcr.io/d4vinci/scrapling:latest
```

## MCP-Server einrichten {#setting-up-the-mcp-server}

Hier erfahren Sie, wie Sie den MCP-Server von Scrapling zu [Claude Desktop](https://claude.ai/download) und [Claude Code](https://www.anthropic.com/claude-code) hinzufügen. Die gleichen Grundschritte gelten für andere Chatbots, die MCP unterstützen:

!!! note "Hinweis"
    Der Befehl `scrapling-mcp` in den Beispielen wurde in Version 0.4.13 als Abkürzung für `scrapling mcp` hinzugefügt. Er erleichtert die Nutzung in MCP-Verzeichnissen und Clients, die einen einzelnen Befehl erwarten. Verwenden Sie bei älteren Versionen den Befehl `scrapling` mit `mcp` als erstem Argument.

### Claude Desktop {#claude-desktop}

1. Öffnen Sie Claude Desktop.
2. Klicken Sie oben links auf das Menü (☰), dann auf Settings → Developer → Edit Config.
3. Fügen Sie die Konfiguration für den MCP-Server von Scrapling hinzu:
```json
"ScraplingServer": {
  "command": "scrapling-mcp"
}
```
Wenn dies Ihr erster MCP-Server ist, verwenden Sie diesen Dateiinhalt:
```json
{
  "mcpServers": {
    "ScraplingServer": {
      "command": "scrapling-mcp"
    }
  }
}
```
Laut dem [offiziellen Artikel](https://modelcontextprotocol.io/quickstart/user) wird dabei eine neue Konfigurationsdatei erstellt, wenn noch keine existiert. Andernfalls wird die vorhandene Datei geöffnet. Sie liegt hier:

1. **MacOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
2. **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

Verwenden Sie den vollständigen Pfad zur ausführbaren Datei `scrapling-mcp`, damit der Start funktioniert. Sie finden ihn mit:

1. **MacOS**: `which scrapling-mcp`
2. **Windows**: `where scrapling-mcp`

Auf meinem Mac war das Ergebnis `/Users/<MyUsername>/.venv/bin/scrapling-mcp`. Ich habe daher diese Konfiguration verwendet:
```json
{
  "mcpServers": {
    "ScraplingServer": {
      "command": "/Users/<MyUsername>/.venv/bin/scrapling-mcp"
    }
  }
}
```
#### Docker {#docker}

Mit dem Docker-Image sieht die Konfiguration etwa so aus:
```json
{
  "mcpServers": {
    "ScraplingServer": {
      "command": "docker",
      "args": [
        "run", "-i", "--rm", "pyd4vinci/scrapling", "mcp"
      ]
    }
  }
}
```

Das Gleiche gilt für [Cursor](https://cursor.com/docs/context/mcp), [WindSurf](https://windsurf.com/university/tutorials/configuring-first-mcp-server) und andere Clients.

### Claude Code {#claude-code}

Mit [Claude Code](https://www.anthropic.com/claude-code) geht es einfacher:

```bash
claude mcp add ScraplingServer "/Users/<MyUsername>/.venv/bin/scrapling-mcp"
```
So erhalten Sie den Pfad zur ausführbaren Datei von Scrapling:

1. **MacOS**: `which scrapling-mcp`
2. **Windows**: `where scrapling-mcp`

Weitere Details finden Sie im Artikel von Anthropic zum [Hinzufügen von MCP-Servern zu Claude Code](https://docs.anthropic.com/en/docs/claude-code/mcp#option-1%3A-add-a-local-stdio-server).

Beenden Sie die Anwendung nach dem Hinzufügen des Servers vollständig und starten Sie sie neu. In Claude Desktop sollte unten rechts im Eingabefeld ein MCP-Serversymbol (🔧) erscheinen, oder `ScraplingServer` im Menü `Search and tools` des Eingabefelds.

### Eigene ausführbare Browser-Datei {#custom-browser-executable}

Die Werkzeuge `browser_fetch_once` und `browser_open` können statt des mitgelieferten Chromium eine eigene ausführbare Browser-Datei verwenden, die mit Chromium kompatibel ist. Das eignet sich für angepasste Browser-Versionen oder schlanke Browser-Engines.

Um dies einmal für den gesamten MCP-Server festzulegen, übergeben Sie beim Start den Pfad zur ausführbaren Datei:

```bash
scrapling-mcp --executable-path "/path/to/chromium"
```

Fügen Sie die Option in der Konfiguration von Claude Desktop zu den Server-Argumenten hinzu:

```json
{
  "mcpServers": {
    "ScraplingServer": {
      "command": "/Users/<MyUsername>/.venv/bin/scrapling-mcp",
      "args": [
        "--executable-path",
        "/path/to/chromium"
      ]
    }
  }
}
```

Sie können vor dem Start auch die Umgebungsvariable `SCRAPLING_EXECUTABLE_PATH` setzen. Die KI kann weiterhin eine andere Browser-Datei für einen einzelnen Abruf mit `browser_fetch_once` oder beim Öffnen einer Sitzung mit `browser_open` wählen.

### Mit entfernten Browsern verbinden {#connecting-to-remote-browsers}

`browser_open` muss keinen lokalen Browser starten. Übergeben Sie eine CDP-URL, um über das [Chrome DevTools Protocol](https://chromedevtools.github.io/devtools-protocol/) eine Verbindung zu einem laufenden Browser herzustellen. Dieser kann auf demselben Rechner, auf einem anderen Rechner oder bei einem Browser-Anbieter laufen:
```
Open a stealthy browser session on wss://cdp.provider.example/session/abc123, then use it to scrape the product details from https://shop.example.com. Close the session when you're done.
```
Die zurückgegebene `session_id` verwenden Sie wie gewohnt mit `browser_fetch`, `browser_extract`, `browser_actions`, `browser_evaluate`, `browser_screenshot`, `browser_network_requests`, `browser_network_request`, `browser_save_state` und `browser_load_state`.

Die URL kann ein WebSocket-Endpunkt (`ws://`/`wss://`) sein, wie ihn Browser-Dienste bereitstellen. Oder sie kann der HTTP-Endpunkt eines Browsers sein, den Sie selbst mit aktiviertem Remote-Debugging-Port gestartet haben:
```commandline
chrome --remote-debugging-port=9222
```
Verwenden Sie dafür `cdp_url="http://localhost:9222"` oder die Adresse des anderen Rechners, falls der Browser dort läuft.

!!! note "Hinweise"

    * Da der Browser bereits läuft, ignorieren CDP-Sitzungen Optionen, die nur beim Start gelten: `headless`, `real_chrome` und `executable_path`, einschließlich des oben beschriebenen Server-Standardwerts.<br/>
    * Alle anderen Optionen gelten weiterhin (`locale`, `useragent`, `proxy`, `cookies`, `timezone_id` usw.). Jede Sitzung erstellt ihren eigenen Browser-Kontext im entfernten Browser.

### Streamable HTTP {#streamable-http}

Seit Version 0.3.6 kann der MCP-Server den Transport 'Streamable HTTP' statt des üblichen 'stdio' verwenden.

Statt dieses Befehls für 'stdio':
```bash
scrapling-mcp
```
verwenden Sie diesen, um 'Streamable HTTP' zu aktivieren:
```bash
scrapling-mcp --http
```
Standardmäßig lauscht der Server auf '127.0.0.1' an Port 8000. Sie können beide Werte ändern:
```bash
scrapling-mcp --http --host '0.0.0.0' --port 8000
```
Die Standardeinstellung akzeptiert nur Verbindungen vom selben Rechner. Mit `--host '0.0.0.0'` machen Sie den Server im Netzwerk erreichbar. Diese Entscheidung ist unabhängig von der unten beschriebenen Authentifizierung.

Wenn Sie 'Streamable HTTP' in Docker ausführen, müssen Sie selbst '0.0.0.0' wählen und ein Token setzen. Sonst erreicht der veröffentlichte Port den Server nicht, weil '127.0.0.1' des Containers nur innerhalb des Containers sichtbar ist:
```bash
docker run -p 8000:8000 -e SCRAPLING_MCP_AUTH_TOKEN="<your-token>" pyd4vinci/scrapling mcp --http --host '0.0.0.0'
```

### Authentifizierung {#authentication}

Auf den Transport 'stdio' kann nur das Programm zugreifen, das ihn gestartet hat. Bei 'Streamable HTTP' kann dagegen jeder, der den Port erreicht, alle Werkzeuge aufrufen. Dazu gehört auch der Abruf beliebiger URLs vom Rechner des Servers aus. Deshalb erfordert 'Streamable HTTP' eine Authentifizierung. Mit `--http` allein startet der Server nicht, sondern verlangt ein Token:
```bash
scrapling-mcp --http --auth-token "$(openssl rand -hex 32)"
```
Clients müssen dieses Token in einem `Authorization`-Header senden. Anfragen ohne Token werden mit `401` abgewiesen:
```json
{
  "mcpServers": {
    "ScraplingServer": {
      "url": "https://your-server.example.com/mcp",
      "headers": {
        "Authorization": "Bearer <your-token>"
      }
    }
  }
}
```
Wenn Sie das Token in der Befehlszeile übergeben, steht es im Shell-Verlauf und in der Prozessliste. Verwenden Sie daher besser die Umgebungsvariable `SCRAPLING_MCP_AUTH_TOKEN`:
```bash
export SCRAPLING_MCP_AUTH_TOKEN="<your-token>"
scrapling-mcp --http
```
Wenn Sie einen Server ohne Authentifizierung benötigen, etwa für einen lokalen Test auf der Standardadresse '127.0.0.1', geben Sie dies mit `--no-auth` an:
```bash
scrapling-mcp --http --no-auth
```
Die Kombination aus `--no-auth` und `--host '0.0.0.0'` macht alle Werkzeuge für jeden erreichbar, der auf den Port zugreifen kann. Vermeiden Sie diese Kombination außerhalb eines vertrauenswürdigen Netzwerks.

Wenn der Server auf einer öffentlichen Adresse lauscht, sollten Sie auch die erlaubten Hostnamen festlegen. Damit aktivieren Sie den Schutz vor DNS-Rebinding. Bei diesem Angriff versucht eine besuchte Website, mit Ihrem Server zu kommunizieren. Sie können die Option mehrfach angeben:
```bash
scrapling-mcp --http --allowed-host 'your-server.example.com:8000'
```

!!! note "Hinweise"

    * Die Authentifizierung gilt nur für 'Streamable HTTP'. Bei 'stdio' wird sie ignoriert, und der Server schreibt eine Warnung ins Log.<br/>
    * Unverschlüsseltes HTTP sendet das Token im Klartext. Stellen Sie den Server daher hinter einen Reverse Proxy, der die TLS-Verbindung übernimmt, bevor Sie ihn im Internet bereitstellen.<br/>
    * Es gibt einen gemeinsamen Schlüssel, keine eigenen Zugangsdaten pro Client. Alle Clients verwenden dasselbe Token. Um es zu ändern, müssen Sie den Server neu starten.<br/>
    * Beim Start mit `--http --no-auth` schreibt der Server trotzdem eine Warnung über die fehlende Authentifizierung ins Log.<br/>
    * Wenn Sie `--auth-token` und `--no-auth` gemeinsam übergeben, bleibt das Token erhalten und die Authentifizierung aktiv.

## Beispiele {#examples}

Hier sind einige Prompts, mit denen wir den MCP-Server getestet haben. Ihnen fallen bestimmt noch bessere ein :)

Wir beginnen mit einfachen Prompts und gehen dann zu komplexeren über. Die Beispiele nutzen Claude Desktop. Die gleiche Vorgehensweise gilt auch für andere Clients.

1. **Einfaches Web Scraping**

    Extrahieren Sie den Hauptinhalt einer Webseite als Markdown:

    ```
    Scrape the main content from https://example.com and convert it to markdown format.
    ```

    Claude kann mit `make_request` die Seite abrufen und sauberen, lesbaren Inhalt zurückgeben. HTTP-Anfragen verwenden standardmäßig drei Versuche mit einer Sekunde Pause dazwischen. Wenn die Seite JavaScript braucht oder HTTP-Anfragen blockiert, kann die KI stattdessen `browser_fetch_once` verwenden. Beide Werkzeuge schließen ihre eigenen Ressourcen nach dem Aufruf.

    Eine genauere Version desselben Prompts wäre:
    ```
    Use regular requests to scrape the main content from https://example.com and convert it to markdown format.
    ```
    Damit sagen Sie Claude, welches Werkzeug es verwenden soll. Es muss nicht raten. Manchmal beginnt es mit normalen Anfragen. Manchmal wählt es ohne klaren Grund einen Browser. Geben Sie das Werkzeug möglichst an, um Zeit und Geld zu sparen und gleichbleibende Ergebnisse zu erhalten.

2. **Gezielte Datenextraktion**

    Extrahieren Sie bestimmte Elemente mit CSS-Selektoren:

    ```
    Get all product titles from https://shop.example.com using the CSS selector '.product-title'. If the request fails, retry up to 5 times every 10 seconds.
    ```

    Der Server extrahiert nur Elemente, die zum Selektor passen, und gibt sie als strukturierte Liste zurück. In diesem Beispiel habe ich bis zu fünf Versuche bei Verbindungsproblemen verlangt. Die Standardeinstellung reicht aber meist aus.

3. **Daten von Online-Shops sammeln**

    Ein etwas komplexerer Prompt:
    ```
    Open a stealthy browser session and visit these e-commerce URLs one at a time:
    - https://shop1.com/product-a
    - https://shop2.com/product-b  
    - https://shop3.com/product-c
    
    Get the product names, prices, and descriptions from each page. Close the session when done.
    ```

    Claude kann eine Browser-Sitzung wiederverwenden, `browser_fetch` der Reihe nach für jede URL aufrufen und dann die extrahierten Daten auswerten.

4. **Ein fortgeschrittener Ablauf**

    Angenommen, ich möchte alle Actionspiele auf der ersten Seite des PlayStation Store abrufen. Dafür kann ich diesen Prompt verwenden:
    ```
    Extract the URLs of all games on this page, then visit each game in order and return a list of all action games: https://store.playstation.com/en-us/pages/browse
    ```
    Lassen Sie die KI eine HTTP-Sitzung wiederverwenden. So muss sie keinen Browser starten, wenn die Daten über normale Anfragen erreichbar sind:
    ```
    Open an HTTP session, extract the URLs of all games on this page, then fetch each game in order and return a list of all action games. Close the session when done: https://store.playstation.com/en-us/pages/browse
    ```
    Wenn Sie CSS-Selektoren schreiben können, grenzen Sie den Inhalt ein, bevor die KI ihn liest:
    ```
    Use an HTTP session to extract the URLs of all games on the page below, then fetch each game in order and return a list of all action games.
    The selector for games in the first page is `[href*="/concept/"]` and the selector for the genre in each game page is `[data-qa="gameInfo#releaseInformation#genre-value"]`.
    Close the session when done.

    URL: https://store.playstation.com/en-us/pages/browse
    ```

5. **Daten von einer mit Cloudflare geschützten Website abrufen**

    Wenn Sie vermuten, dass die Website Cloudflare verwendet, sagen Sie es Claude. Dann muss es das nicht selbst herausfinden.
    ```
    What's the price of this product? Be cautious, as it utilizes Cloudflare's Turnstile protection. Make the browser visible while you work.

    https://ao.com/product/oo101uk-ninja-woodfire-outdoor-pizza-oven-brown-99357-685.aspx
    ```

6. **Ein langer Ablauf**

    Sie können zum Beispiel einen Prompt wie diesen verwenden:
    ```
    Extract all product URLs for the following category, then return the prices and details for the first 3 products.
    
    https://www.arnotts.ie/furniture/bedroom/bed-frames/
    ```
    Besser wäre aber dieser:
    ```
    Go to the following category URL and extract all product URLs using the CSS selector "a". Then, reuse the session to fetch the first 3 product pages in order and extract each product’s price and details. Close the session when done.
    
    Keep the output in markdown format to reduce irrelevant content.
    
    Category URL:
    https://www.arnotts.ie/furniture/bedroom/bed-frames/
    ```

7. **Dauerhafte Sitzungen verwenden**

    Verwenden Sie für mehrere Seiten derselben Website eine dauerhafte Browser-Sitzung. So muss nicht für jede Anfrage ein neuer Browser starten:
    ```
    Open a stealthy browser session, then use it to scrape the main details from the first 5 product pages on https://shop.example.com. Close the session when you're done.
    ```
    Claude erstellt mit `browser_open` eine dauerhafte Browser-Sitzung, ruft darin jede Produktseite mit `browser_fetch` ab und verwendet am Ende `close_session`. Das ist deutlich schneller als ein neuer Browser für jede Seite.

    !!! danger "Gefahr"

        Schließen Sie dauerhafte Sitzungen immer, wenn Sie fertig sind. Sonst bleiben sie offen!

8. **Eine dauerhafte Sitzung für einen langen Ablauf verwenden**

    Ein weiteres langes Beispiel, das Claude zum Nachdenken bringt:

    ```
    Use Scrapling MCP to do the following in this order:

    1. Open a stealthy browser session with headless mode off.
    2. Go to this page and collect the number of stars: https://github.com/D4Vinci/Scrapling
    3. From the README, get the URL that shows the number of downloads and go to it.
    4. Get the number of downloads and the top 3 countries from the graph.
    5. Prepare a report with the results.
    6. Close the browser.
    ```

Und so weiter. Ihre Kreativität ist gefragt.

## Bewährte Vorgehensweisen {#best-practices}

Hier sind einige technische Tipps für die Nutzung.

### 1. Das passende Werkzeug wählen {#1-choose-the-right-tool}

- **`make_request`**: Schnelle HTTP-Anfragen für eine einzelne Seite oder einen API-Aufruf.
- **`browser_fetch_once`**: Eine einzelne JavaScript-Seite, dynamische Seite oder geschützte Website, auch mit Cloudflare.
- **Sitzungswerkzeuge**: Zusammenhängende Anfragen, Browser-Aktionen, Screenshots und Netzwerkverlauf.

### 2. Leistung verbessern {#2-optimize-performance}

- Verwenden Sie eine Sitzung erneut und rufen Sie die URLs der Reihe nach ab.
- Deaktivieren Sie unnötige Ressourcen.
- Wählen Sie passende Zeitlimits.
- Nutzen Sie CSS-Selektoren für gezielte Extraktion.

### 3. Dynamische Inhalte verarbeiten {#3-handle-dynamic-content}

- Nutzen Sie `network_idle` für Single-Page-Anwendungen (SPAs).
- Setzen Sie `wait_selector`, um auf bestimmte Elemente zu warten.
- Erhöhen Sie das Zeitlimit bei langsam ladenden Websites.

### 4. Datenqualität {#4-data-quality}

- Verwenden Sie `main_content_only=true`, um den Seitenkörper auszuwählen und zu bereinigen.
- Wählen Sie einen passenden `extraction_type` für Ihre Aufgabe.

### 5. Schutz vor Prompt Injection {#5-prompt-injection-protection}

Der MCP-Server bereinigt extrahierte Inhalte automatisch, wenn `main_content_only` aktiviert ist. Das ist die Standardeinstellung. Dabei werden versteckte Inhalte entfernt, mit denen bösartige Websites Anweisungen in den KI-Kontext einschleusen könnten:

- **Versteckende Inline-Styles**: `display:none`, `visibility:hidden` und Nullwerte für Deckkraft, Schriftgröße, Höhe, Breite, maximale Höhe und maximale Breite.
- **Für Barrierefreiheit ausgeblendete Elemente**: `aria-hidden="true"`.
- **Template-Tags und versteckte Slots**: Elemente mit `<template>` und `<slot hidden>`.
- **HTML-Kommentare**: `<!-- ... -->`.
- **Zeichen mit der Breite null**: Unsichtbare Unicode-Zeichen, etwa Leerzeichen ohne Breite.

Dieser Schutz läuft automatisch bei der Extraktion von HTML, Markdown und Text. Behalten Sie den Standardwert `main_content_only=true` für den größtmöglichen Schutz bei.

### 6. Sitzungen verwalten {#6-manage-sessions}

- Verwenden Sie `make_request` oder `browser_fetch_once` für einen einzelnen Abruf. Die Werkzeuge schließen ihre eigenen Ressourcen und hinterlassen keine Sitzung für weitere Aufrufe.
- Verwenden Sie `browser_open`, um für mehrere Seiten eine dauerhafte Browser-Sitzung zu erstellen. Rufen Sie dann jede Seite mit `browser_fetch` in dieser Sitzung ab.
- Für mehrere reine HTTP-Anfragen verwenden Sie `open_request_session` und dann `session_make_request` für jede Anfrage. Die Sitzung behält Cookies, Verbindungen und den Browser-Fingerprint (`impersonate`) zwischen Aufrufen, ohne einen Browser zu verwenden.
- Sitzungen behalten die beim Öffnen gesetzte Konfiguration. Dazu gehören headless, locale, Cookies und Optionen gegen Erkennung für Browser sowie `impersonate` und `proxy` für HTTP-Sitzungen. Optionen einzelner Anfragen wie timeout, wait_selector, network_idle und solve_cloudflare werden bei jedem Aufruf an `browser_fetch`/`session_make_request` übergeben. Ihre Standardwerte stehen in den Werkzeug-Schemas.
- `browser_fetch` kann Cloudflare-Prüfungen in der offenen Stealthy-Browser-Sitzung lösen.
- Schließen Sie Sitzungen am Ende immer mit `close_session`, um Ressourcen freizugeben.
- Prüfen Sie mit `list_sessions`, welche Sitzungen noch aktiv sind und mit welchen `settings` sie erstellt wurden. Diese werden dem KI-Agenten zurückgegeben und sind bei CDP-Sitzungen leer.
- Übergeben Sie den Werkzeugen zum Öffnen eine eigene `session_id`, um aussagekräftige Namen wie `"search"` oder `"checkout"` zu vergeben. Sonst wird ein zufälliger Hexadezimalwert verwendet. Wenn die gewählte ID schon belegt ist, wird ein Fehler ausgelöst. So erkennen Sie Konflikte frühzeitig.

### 7. Screenshots erstellen {#7-capturing-screenshots}

- `browser_screenshot` erfasst die Seite, die bereits mit `browser_fetch` in einer Stealthy-Browser-Sitzung geöffnet wurde. Es lädt sie nicht neu. So kann die KI ausgefüllte Felder, offene Menüs und andere Ergebnisse ihrer Aktionen prüfen.
- Das Bild wird als echter `ImageContent`-Block zurückgegeben, sodass das Modell die Seite direkt sieht.
- Erfassen Sie den sichtbaren Bereich oder die ganze Seite, einschließlich der Inhalte unterhalb des Bildschirms.
- Erfassen Sie ein einzelnes Feld, Diagramm, eine Karte oder ein Ergebnis, um weniger umgebenden Inhalt zu erhalten. Dafür kann das Zielelement ins Blickfeld gescrollt werden.
- Wählen Sie PNG für verlustfreie Bilder oder JPEG mit einstellbarer Qualität für kleinere Dateien.
- Die KI kann mit `browser_actions` vor der Aufnahme auf Inhalte warten oder Aktionen abschließen.

## Rechtliche und ethische Hinweise {#legal-and-ethical-considerations}

⚠️ **Wichtige Regeln:**

- **robots.txt prüfen**: Öffnen Sie `https://website.com/robots.txt`, um die Crawling-Regeln zu lesen.
- **Anfragelimits beachten**: Überlasten Sie Server nicht mit Anfragen.
- **Nutzungsbedingungen**: Lesen und beachten Sie die Bedingungen der Website.
- **Urheberrecht**: Achten Sie die Rechte am geistigen Eigentum.
- **Datenschutz**: Beachten Sie die Gesetze zum Schutz personenbezogener Daten.
- **Geschäftliche Nutzung**: Stellen Sie sicher, dass Sie die Daten geschäftlich nutzen dürfen.

---

*Mit ❤️ vom Scrapling-Team erstellt. Viel Erfolg beim Scraping!*
