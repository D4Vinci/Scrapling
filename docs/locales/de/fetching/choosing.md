---
title: "HTTP-Anfragen oder Browser für Web Scraping auswählen"
description: "Wählen Sie Fetcher oder StealthyFetcher für Ihre Aufgabe. Erfahren Sie, wann direkte HTTP-Anfragen, JavaScript-Rendering und wiederverwendbare Sitzungen passen."
---

# Grundlagen der Fetcher {#fetchers-basics}

## Einführung {#introduction}
Fetcher sind Klassen, mit denen Sie in einer Zeile Anfragen senden oder Seiten abrufen können. Sie bieten viele Funktionen und geben ein [Response](#response-object)-Objekt zurück. Seit v0.3 gibt es für alle Fetcher eigene Klassen, die eine Sitzung offen halten. Ein Browser-Fetcher kann so denselben Browser für alle Anfragen nutzen, statt mehrere Browser zu öffnen. Welche Variante passt, hängt von Ihrem Anwendungsfall ab.

Vor v0.2 war Scrapling nur ein Parser. Die Fetcher kamen dazu, damit die Bibliothek Schritt für Schritt alles abdecken kann, was Sie für Web Scraping brauchen.

> Fetcher sind keine einfachen Wrapper um andere Bibliotheken. Sie nutzen diese Bibliotheken als Engine zum Senden von Anfragen und Abrufen von Seiten. Alle Fetcher bieten Funktionen, die ihre Engines selbst nicht haben. Dabei nutzen sie deren Möglichkeiten vollständig und optimieren sie für Web Scraping.

## Überblick über die Fetcher {#fetchers-overview}

Scrapling bietet HTTP-Fetcher (`Fetcher` und `AsyncFetcher`) und einen Browser-Fetcher (`StealthyFetcher`). Für wiederholte Anfragen gibt es Sitzungsklassen.

Die folgende Tabelle hilft Ihnen bei der Auswahl.


| Funktion | Fetcher | StealthyFetcher |
|--------------------|---------------------------------------------------|--------------------------------------------------------------------------------------------|
| Relative Geschwindigkeit | 🐇🐇🐇🐇🐇 | 🐇🐇🐇 |
| Tarnung | ⭐⭐ | ⭐⭐⭐⭐⭐ |
| Optionen gegen Bot-Erkennung | ⭐⭐ | ⭐⭐⭐⭐⭐ |
| JavaScript laden | ❌ | ✅ |
| Speicherbedarf | ⭐ | ⭐⭐⭐ |
| Besonders geeignet für | Einfaches Scraping, wenn HTTP-Anfragen ausreichen | - Dynamisch geladene Websites <br/>- Kleine Automatisierungen <br/>- Einfache bis komplexe Schutzmaßnahmen |
| Browser | ❌ | Chromium und Google Chrome |
| Verwendete Browser-API | ❌ | Playwright |
| Einrichtung | Einfach | Einfach |

Auf den nächsten Seiten erklären wir die einzelnen Fetcher genauer.

## Parser für alle Fetcher konfigurieren {#parser-configuration-in-all-fetchers}
Alle Fetcher werden auf dieselbe Weise importiert, wie Sie auf den nächsten Seiten sehen:
```python
from scrapling.fetchers import Fetcher, AsyncFetcher, StealthyFetcher
```
Danach können Sie den Fetcher direkt verwenden, ohne eine Instanz zu erstellen. Er nutzt die Standardeinstellungen des Parsers:
```python
page = StealthyFetcher.fetch('https://example.com') 
```
Wenn Sie den Parser ([Klasse Selector](../parsing/main_classes.md#selector)) einstellen möchten, der die Antwort vor der Rückgabe verarbeitet, machen Sie zuerst Folgendes:
```python
from scrapling.fetchers import Fetcher
Fetcher.configure(adaptive=True, keep_comments=False)  # and the rest
```
oder
```python
from scrapling.fetchers import Fetcher
Fetcher.adaptive=True
Fetcher.keep_comments=False
```
Danach setzen Sie Ihren Code wie gewohnt fort.

Die verfügbaren Argumente sind `adaptive`, `adaptive_domain`, `huge_tree`, `keep_comments`, `storage` und `storage_args`. Es sind dieselben wie bei der Klasse [Selector](../parsing/main_classes.md#selector). Mit `<fetcher_class>.display_config()` können Sie die aktuelle Konfiguration jederzeit anzeigen.

!!! info

    Das Argument `adaptive` ist standardmäßig deaktiviert. Sie müssen es aktivieren, um diese Funktion zu nutzen.

### Parser für einzelne Anfragen konfigurieren {#set-parser-config-per-request}
Die oben gezeigte Konfiguration gilt global für alle Anfragen und Abrufe über diese Klasse. Das hält die Nutzung einfach.

Wenn Sie für jede Anfrage andere Einstellungen brauchen, übergeben Sie der Anfragemethode (`fetch`/`get`/`post`/...) ein Dictionary im Argument `selector_config`.

## Das Response-Objekt {#response-object}
Das Objekt `Response` basiert auf der Klasse [Selector](../parsing/main_classes.md#selector). Es enthält zusätzlich Angaben zur Antwort, zum Beispiel Header, Status und Cookies:
```python
from scrapling.fetchers import Fetcher
page = Fetcher.get('https://example.com')

page.status          # HTTP status code
page.reason          # Status message
page.cookies         # Response cookies as a dictionary
page.headers         # Response headers
page.request_headers # Request headers
page.history         # Response history of redirections, if any
page.body            # Raw response body as bytes
page.encoding        # Response encoding
page.meta            # Response metadata dictionary (e.g., proxy used). Mainly helpful with the spiders system.
```
Alle Fetcher geben ein `Response`-Objekt zurück. Browser-Sitzungen mit `record_requests=True` liefern über `session.network.search(limit=None)` und `session.network.get(request_id)` ebenfalls gespeicherte `Response`-Objekte. Unter [Netzwerkverlauf](stealthy.md#network-history) erfahren Sie mehr über gespeicherte API-Antworten und den Umstieg auf v5.

Das Objekt `Response` kann die Seite auch in einer Zeile in bereinigtes Markdown für LLMs umwandeln:
```python
markdown = Fetcher.get('https://example.com').markdown(main_content_only=True)
```
Vor der Umwandlung werden immer Skripte, Styles sowie versteckte Inhalte und Inhalte zur Prompt Injection entfernt. Mit `css_selector` können Sie die Umwandlung auf bestimmte Elemente beschränken. Dafür ist das Extra `rag` nötig, das auch in `ai`/`shell`/`all` enthalten ist. Die Seite [RAG-Systeme erstellen](../ai/building-rag-systems.md) erklärt die Details.

!!! note

    Anders als bei der Klasse [Selector](../parsing/main_classes.md#selector) ist der Antwortinhalt der Klasse `Response` seit v0.4 immer vom Typ bytes.
