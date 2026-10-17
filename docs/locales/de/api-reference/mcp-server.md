---
title: "API-Referenz für den MCP-Server von Scrapling"
description: "Sehen Sie sich die Werkzeuge des MCP-Servers sowie seine Modelle für Anfragen, Antworten und Sitzungen zur Datenextraktion mit HTTP oder Browsern an."
---

# Referenz des MCP-Servers {#mcp-server-api-reference}

Der **MCP-Server von Scrapling** bietet sechzehn Werkzeuge zum Extrahieren von Daten und zur Bedienung des Browsers über das Model Context Protocol (MCP). Binden Sie Scrapling in Assistenten und KI-Agenten ein, um Daten per Gespräch zu extrahieren, mit Funktionen gegen Bot-Erkennung.

Starten Sie den MCP-Server mit diesem Befehl:

```bash
scrapling mcp
```

Oder importieren Sie die Serverklasse direkt:

```python
from scrapling.core.ai import ScraplingMCPServer

server = ScraplingMCPServer()
server.serve(http=False, host="127.0.0.1", port=8000)
```

Um Ihre eigene ausführbare Datei eines Chromium-kompatiblen Browsers zu verwenden, übergeben Sie `executable_path`:

```python
server = ScraplingMCPServer(executable_path="/path/to/chromium")
```

## Antwortmodell {#response-model}

Die Werkzeuge zum Abrufen von Seiten und für HTTP-Anfragen geben diese Struktur zurück, mit einer Antwort pro Aufruf. Die Werkzeuge zur Sitzungsverwaltung verwenden die folgenden Modelle. `browser_screenshot` gibt ein Bild der Seite oder eines Elements zusammen mit der aktuellen URL als Bild- und Textblöcke zurück. `browser_extract` und `browser_actions` geben einfachen Text zurück. Die beiden Netzwerkwerkzeuge geben strukturiertes JSON über die folgenden Modelle zurück. `browser_evaluate` gibt das Ergebnis als JSON in einem Textblock zurück.

## ::: scrapling.core.ai.server.ResponseModel
    handler: python
    :docstring:

## Modelle für Netzwerkanfragen {#network-request-models}

`browser_network_requests` gibt `NetworkRequestsModel` mit `requests`, `next_cursor`, `has_more` und `dropped_count` zurück. Jedes `NetworkRequestInfo` enthält `id`, `url`, `method`, `resource_type` und `status`. Zum Fortsetzen übergeben Sie `next_cursor` als `after_id`. `has_more` zeigt an, ob der aktuelle Verlauf weitere Treffer enthält.

`browser_network_request` gibt `NetworkRequestModel` mit `request_id`, `part`, `data` und `note` zurück. Zusammenfassungen und Header sind Objekte. Der vollständig gespeicherte Inhalt wird als Zeichenkette zurückgegeben, auch wenn die Antwort JSON enthält. `note` erklärt, ob Inhaltsdaten fehlen oder Header unvollständig sind.

## ::: scrapling.core.ai._network_formatting.NetworkRequestInfo
    handler: python
    :docstring:

## ::: scrapling.core.ai.server.NetworkRequestsModel
    handler: python
    :docstring:

## ::: scrapling.core.ai._network_formatting.NetworkRequestModel
    handler: python
    :docstring:

## Sitzungsmodelle {#session-models}

Modellklassen zur Verwaltung von Sitzungen:

## ::: scrapling.core.ai.server.SessionInfo
    handler: python
    :docstring:

## ::: scrapling.core.ai.server.SessionCreatedModel
    handler: python
    :docstring:

## ::: scrapling.core.ai.server.SessionClosedModel
    handler: python
    :docstring:

## Klasse des MCP-Servers {#mcp-server-class}

Die Hauptklasse des MCP-Servers bietet diese Werkzeuge:

- **`make_request`**: Ruft eine URL über HTTP ab, bildet einen Browser nach und schließt den Client automatisch. Unterstützt GET, POST, PUT und DELETE.
- **`browser_fetch_once`**: Ruft eine URL mit einem Stealth-Browser ab, führt JavaScript aus, behandelt Cloudflare und schließt den Browser. Nutzen Sie eine dauerhafte Sitzung, wenn Sie danach Aktionen ausführen oder den Netzwerkverlauf lesen möchten.

- **`browser_extract`**: Liest die aktuelle Seite oder ein Element als strukturierte Ansicht für KI, HTML, Markdown oder Text, ohne neu zu laden. Ergebnisse von Formularen und Aktionen bleiben erhalten. Die strukturierten Ansichten enthalten Rollen, Namen, Referenzen, Positionen und Größen der Elemente. Die Suche mit regulären Ausdrücken liefert passende Zeilen, den nahen Kontext und Elternknoten.
- **`browser_actions`**: Verknüpft Mausbewegungen, Bewegen des Zeigers über Elemente, Klicks, Scrollen, Feldeingaben, Tastenkürzel, Antworten auf Dialoge und Wartezeiten in einem Aufruf. Akzeptieren oder schließen Sie Meldungen und Bestätigungen, oder geben Sie Text in Eingabedialoge ein. Sie können ein Suchfeld ausfüllen, die Suche absenden, auf Ergebnisse warten und eines öffnen, ohne einen Aufruf pro Schritt zu machen.

    Bewegungen und Klicks akzeptieren Selektoren, Referenzen aus strukturierten Ansichten oder Koordinaten. Das Werkzeug wartet auf Elemente und scrollt sie in den sichtbaren Bereich. Es unterstützt Bewegungen in Schritten, linke, rechte und mittlere Mausklicks, Doppelklicks und Scrollen in verschachtelten Bereichen.

    Wählen Sie Felder mit Selektoren oder Referenzen aus strukturierten Ansichten. Geben Sie Text ein, aktivieren oder deaktivieren Sie Kontrollkästchen, wählen Sie Optionsfelder und eine oder mehrere Optionen nativer Listen anhand ihrer Beschriftung. Ersetzen oder löschen Sie Text, oder schreiben Sie an der Cursorposition weiter. Tastenkürzel nutzen den aktuellen Fokus. Der langsame Modus fügt zufällige Pausen zwischen Zeichen und Aktionen ein.

    Warten Sie mit Selektoren oder Referenzen aus strukturierten Ansichten auf Inhalte oder Ladeanzeigen. Sie können auch auf Ladeereignisse, das Ende der Netzwerkaktivität oder eine feste Zeitspanne warten.

- **`browser_evaluate`**: Führt JavaScript auf der aktuellen Seite aus, um eigene Daten zu extrahieren, Berechnungen auszuführen, den Anwendungszustand zu lesen oder Inhalte zu ändern. Unterstützt asynchrone Skripte und gibt deren Ergebnisse als JSON zurück.
- **`browser_network_requests`**: Durchsucht abgeschlossene Browseranfragen über Tabs, Seitenwechsel und Aktionen hinweg. Finden Sie gespeicherte API-Aufrufe, HTTP-Fehler und Weiterleitungen. Statische Ressourcen werden standardmäßig ausgeblendet, um die Ergebnismenge zu verringern. Fehlgeschlagene oder unvollständige Anfragen werden ausgelassen. Gibt strukturierte Daten mit Seiteneinteilung zurück.
- **`browser_network_request`**: Liest die Zusammenfassung, Header, gesendeten Daten oder den Textinhalt einer gespeicherten Anfrage als strukturiertes JSON, ohne die Anfrage zu wiederholen. Gibt den gewählten Teil vollständig zurück. Gespeicherte Antworten bleiben nach Seitenwechseln verfügbar, auch HTTP-Antworten mit 4xx und 5xx. Einträge erscheinen, sobald die Aufzeichnung abgeschlossen ist. Lesen des Verlaufs oder Schließen der Sitzung wartet nicht auf laufende Aufzeichnungen. Diese können bei einem Seitenwechsel oder beim Schließen verloren gehen. Die Bytes stammen von Playwright und können von den vom Server gesendeten Bytes abweichen. Für den Text wird die UTF-8-Dekodierung von Playwright genutzt, wenn sie gültig ist, sonst der angegebene Zeichensatz. Nur Inhalte mit einem unterstützten textbasierten `Content-Type` werden gelesen und gespeichert. Bei binären, fehlenden oder unbekannten Typen bleiben Metadaten und Header erhalten, ohne den Inhalt zu lesen. Das Laden der Seite ändert sich dadurch nicht. Der Verlauf hat Größenlimits. Ein optionaler Hinweis erklärt, ob der Inhalt kein Text ist, zu groß ist oder nicht gelesen werden kann. Lesen Sie benötigte Daten, bevor Sie die MCP-Sitzung schließen.
- **`browser_fetch`**: Ruft eine Seite in einer offenen Stealth-Browsersitzung ab und extrahiert HTML, Markdown, Text oder eine strukturierte Ansicht. Die Ansicht kann die ganze Seite oder ein Element umfassen und enthält Referenzen, Positionen und Größen für spätere Aktionen.

## ::: scrapling.core.ai.server.ScraplingMCPServer
    handler: python
    :docstring:
