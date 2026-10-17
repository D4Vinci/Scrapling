---
title: "Websites mit Scrapling für RAG in Markdown umwandeln"
description: "Wandeln Sie Seitenantworten in Markdown um oder sammeln Sie eine Website mit ContentSpider. Bereiten Sie Texte zum Aufteilen und Indexieren in einem RAG-System vor."
---

# RAG-Systeme mit Scrapling erstellen {#building-rag-systems-with-scrapling}

RAG-Systeme sind nur so gut wie der Text, den sie erhalten. Rohes HTML verbraucht Tokens für Markup, Navigation, Skripte und Tracking-Inhalte. Es kann sogar versteckte Anweisungen für Prompt Injection an Ihr LLM weitergeben. Scrapling wandelt Seiten und ganze Websites in sauberes Markdown um und entfernt solche Inhalte. Dafür ist kein LLM nötig. So ist die Datenerfassung schnell und kostet nichts pro Seite.

## Installation {#installation}

```bash
pip install "scrapling[rag]"

scrapling install
```

Das Extra `rag` installiert die Fetcher mit Markdown-Unterstützung. Die Extras `ai`, `shell` und `all` enthalten sie ebenfalls. Der Befehl `scrapling install` lädt die Browser-Abhängigkeiten herunter. Diese brauchen Sie nur für Fetcher, die einen Browser verwenden.

## Eine Seite in Markdown umwandeln {#one-page-to-markdown}

Jedes [Response](../fetching/choosing.md#response-object)-Objekt hat eine Methode `markdown()`:

```python
from scrapling.fetchers import Fetcher

markdown = Fetcher.get("https://example.com").markdown(main_content_only=True)
```

Sie funktioniert mit allen Fetchern. Damit können Sie auch Seiten hinter Cloudflare mit einer Zeile abrufen:

```python
from scrapling.fetchers import StealthyFetcher

markdown = StealthyFetcher.fetch("https://protected.example.com", solve_cloudflare=True).markdown(main_content_only=True)
```

Zwei Argumente steuern die Ausgabe:

- `main_content_only`: Wandelt nur den Inhalt innerhalb des `<body>`-Tags der Seite um.
- `css_selector`: Wandelt nur die Elemente um, die zu einem CSS-Selektor passen, und verbindet alle Treffer. Nutzen Sie dies, um genau den benötigten Teil zu extrahieren und Tokens zu sparen:

```python
markdown = Fetcher.get("https://example.com/docs/page").markdown(css_selector="article")
```

Unabhängig von den Argumenten werden Skripte, Styles und versteckte Inhalte vor der Umwandlung immer entfernt. Dies ist dieselbe Bereinigung, mit der der [MCP-Server](mcp-server.md) KI-Agenten vor Prompt Injection schützt. Sie entfernt durch Inline-Styles versteckte Elemente, Elemente mit `aria-hidden="true"`, versteckte Slots, `<template>`-Tags, HTML-Kommentare und Zeichen mit der Breite null. Der MCP-Server nutzt diese Bereinigung mit `main_content_only=True`.

## Eine ganze Website in Markdown-Dateien umwandeln {#a-whole-website-to-a-markdown-corpus}

Die Vorlage `ContentSpider` crawlt eine Website und wandelt jede Seite um. Sie nutzt das [Spider-Framework](../spiders/architecture.md). Damit sind gleichzeitige Anfragen, AutoThrottle, die Beachtung von robots.txt sowie Pause und Fortsetzung bereits enthalten:

```python
from scrapling.spiders import ContentSpider

class DocsSpider(ContentSpider):
    name = "docs"
    start_urls = ["https://example.com/docs/"]
    allowed_domains = {"example.com"}
    output_dir = "docs_markdown"
    max_pages = 200

result = DocsSpider().start()
result.items.to_jsonl("docs.jsonl")
```

Jede besuchte Seite wird zu einem Datensatz mit den Schlüsseln `url`, `title` und `markdown`. Wenn Sie `output_dir` festlegen, wird jede Seite auch in eine Markdown-Datei geschrieben, deren Name auf ihrer URL beruht. Das Beispiel oben erzeugt also einen Ordner mit `.md`-Dateien und eine `docs.jsonl`, die Sie direkt weiterverarbeiten können.

Die Vorlage erfordert `allowed_domains`, damit der Crawl auf die gewünschte Website beschränkt bleibt. Folgende Optionen sind verfügbar:

- `css_selector` / `main_content_only`: Werden für jede Seite an `markdown()` übergeben. `main_content_only` ist standardmäßig aktiviert.
- `output_dir`: Wenn gesetzt, wird pro Seite eine Markdown-Datei geschrieben.
- `max_pages`: Maximale Anzahl der umzuwandelnden Seiten. Anfragen, die beim Erreichen der Grenze schon in der Warteschlange stehen, können noch abgerufen werden. Ihre Seiten werden aber nicht umgewandelt. Der Standardwert `0` schaltet die Grenze aus.

Standardmäßig werden alle Seitenlinks innerhalb von `allowed_domains` verfolgt. Da die Vorlage auf [CrawlSpider](../spiders/generic-templates.md#crawlspider) aufbaut, können Sie `rules()` mit einem eigenen [LinkExtractor](../spiders/generic-templates.md#linkextractor-reference) überschreiben, um den Crawl zu steuern. `allow` beschränkt ihn auf gewünschte URL-Muster. `deny` schließt unerwünschte Muster aus, etwa die von Anmeldeseiten, Tag-Listen oder Druckansichten:

```python
from scrapling.spiders import CrawlRule, LinkExtractor, ContentSpider

class DocsSpider(ContentSpider):
    name = "docs"
    start_urls = ["https://example.com/"]
    allowed_domains = {"example.com"}

    def rules(self):
        return [CrawlRule(LinkExtractor(allow=r"/docs/", deny=[r"/docs/changelog/", r"\?print="]))]
```

`deny` hat Vorrang vor `allow`. Wie bei jedem **CrawlSpider** kann eine Regel eine `priority` oder einen Hook `process_request` enthalten.

## Daten in einen Vektorspeicher laden {#feeding-a-vector-store}

Die JSONL-Ausgabe lässt sich in jede Embedding-Pipeline einbinden. Ein einfaches Beispiel:

```python
import json

with open("docs.jsonl", encoding="utf-8") as f:
    for line in f:
        page = json.loads(line)
        for chunk in split_into_chunks(page["markdown"]):
            vector_store.add(text=chunk, metadata={"url": page["url"], "title": page["title"]})
```

Entfernen Sie wiederkehrende Inhalte mit `css_selector` im Spider, bevor Sie den Text in Abschnitte aufteilen. So müssen Sie ihn später nicht mehr bereinigen. Je weniger unnötige Inhalte in den Embeddings stecken, desto besser werden die Suchergebnisse.

## Interaktive Alternativen {#interactive-alternatives}

Wenn Sie Daten lieber im Gespräch extrahieren, gibt der [MCP-Server](mcp-server.md) Ihrem KI-Chatbot Werkzeuge mit derselben Markdown-Extraktion. Der [Agent Skill](agent-skill.md) bringt Coding-Agenten bei, diesen Code selbst zu schreiben.
