---
title: "Scrapling-CLI: Daten über das Terminal extrahieren"
description: "Installieren Sie die Terminal-Werkzeuge von Scrapling. Wählen Sie zwischen Extraktionsbefehlen, der interaktiven Shell und dem MCP-Server und nutzen Sie die passende Anleitung."
---

# Befehlszeilenschnittstelle {#command-line-interface}

Seit Version 0.3 enthält Scrapling eine Befehlszeilenschnittstelle mit drei Hauptfunktionen:

1. **Interaktive Shell**: Eine Web-Scraping-Shell auf Basis von IPython mit vielen Kurzbefehlen und nützlichen Werkzeugen.
2. **Extraktionsbefehle**: Extrahieren Sie Daten von Websites über das Terminal, ohne zu programmieren.
3. **Hilfsbefehle**: Werkzeuge zur Installation und Verwaltung.

```bash
# Launch interactive shell
scrapling shell

# Convert the content of a page to markdown and save it to a file
scrapling extract get "https://example.com" content.md

# Get help for any command
scrapling --help
scrapling extract --help
```

## Voraussetzungen {#requirements}

Für die Werkzeuge in diesem Abschnitt müssen Sie die zusätzliche Abhängigkeitsgruppe `shell` installieren:
```bash
pip install "scrapling[shell]"
```
Um Seiten mit einem Browser abzurufen, installieren Sie auch die Browser-Abhängigkeiten:
```bash
scrapling install
```
Dieser Befehl lädt Chromium und seine Systemabhängigkeiten herunter und aktualisiert die TLD-Liste. Für HTTP-Anfragen ist dieser Schritt nicht nötig.
