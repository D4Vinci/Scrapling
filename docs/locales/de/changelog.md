---
title: "Änderungsverlauf von Scrapling"
description: "Versionshinweise zu Scrapling mit neuen Funktionen, Fehlerbehebungen und inkompatiblen Änderungen."
---

# Änderungsverlauf {#changelog}

Alle wichtigen Änderungen an Scrapling aus den [GitHub-Releases](https://github.com/D4Vinci/Scrapling/releases).

## [v0.5](https://github.com/D4Vinci/Scrapling/releases/tag/v0.5) - 2026-10-17 {#v0.5}

**Scrapling v0.5 verbessert fast alles: Abrufen, Parsen, Spider, Browser-Automatisierung, KI-Werkzeuge und Dokumentation in zehn Sprachen 🚀**

!!! warning "Warnung"

    **Diese Version enthält so viele inkompatible Änderungen, dass sie hier nicht alle aufgeführt werden können. Lesen Sie vor dem Update den [Leitfaden zur Migration auf v0.5](migrating-to-v0.5.md).**

### 🚀 Neuerungen und Verbesserungen der Bedienung {#v0.5-new-stuff-and-quality-of-life-changes}

- **Ein deutlich leistungsfähigerer MCP-Server für KI-Agenten, der fast jedes CAPTCHA lösen kann** (siehe [Dokumentation](ai/mcp-server.md)):

    - **Vollständige Browser-Abläufe**: Formulare ausfüllen, klicken, den Mauszeiger über Elemente bewegen, scrollen, die Tastatur verwenden, Dialoge bedienen und auf Ergebnisse warten, alles in einer geordneten Folge. Unterstützt verschiedene Feldtypen und langsamere Interaktionen. Die Aktionen stoppen beim ersten Fehler.
    - **Die aktuelle Seite ohne Neuladen lesen und durchsuchen**: HTML, Markdown oder Text aus einer ganzen Seite oder einem einzelnen Element extrahieren. Durchsuchbare Seitenansichten zeigen Rollen, Namen und Positionen der Elemente. Gezielte Ansichten behalten den umgebenden Kontext bei.
    - **Eigenes JavaScript ausführen und gezielte Screenshots aufnehmen**: Skripte ausführen, auch mit asynchronen Vorgängen und Zugriff auf das JavaScript der Seite. Einzelne Elemente, den sichtbaren Bereich oder die ganze Seite als PNG oder JPEG aufnehmen.
    - **Netzwerkaktivität prüfen und Anmeldungen wiederverwenden**: Aufgezeichnete Anfragen und Antworten untersuchen, den Anmeldestatus des Browsers speichern und wiederherstellen und mit Elementen in offenem oder geschlossenem Shadow DOM interagieren. Lesen Sie den aufgezeichneten Datenverkehr, bevor Sie die Sitzung schließen.
    - **Weniger Tokens verwenden und klarere Fehler erhalten**: Kürzere Werkzeugbeschreibungen und gemeinsame Hinweise vermeiden Wiederholungen. Fehler bei Browsern und Anfragen erreichen die Agenten mit hilfreichen Meldungen.

- **Sehen Sie die Anfragen hinter der Seite**. Aktivieren Sie `record_requests=True`, um abgeschlossenen Datenverkehr über Ladevorgänge, Aktionen und Tabs hinweg aufzuzeichnen. Prüfen Sie dann die gespeicherten Antworten, ohne Anfragen erneut zu senden. (Siehe [Dokumentation](fetching/stealthy.md#network-history))

    ```python
    from scrapling.fetchers import StealthySession

    with StealthySession(record_requests=True) as session:
        session.fetch("https://example.com", network_idle=True)
        for response in session.network.search(url_pattern=r"/api/", limit=None):
            print(response.url, response.status, response.body)
    ```

    - Nach URL, Methode, Ressourcentyp oder Status filtern und eine einzelne Antwort anhand ihrer ID abrufen. Header, gesendete Daten, API-Antworten, HTTP-Fehler und Weiterleitungen über die gewohnte `Response`-API prüfen.
    - Speichert unterstützte Textkörper innerhalb der Größenlimits sowie Metadaten und einen Grund, wenn ein Antwortkörper nicht gespeichert werden kann. Das Standardlimit beträgt 1.000 Anfragen. Funktioniert mit synchronen und asynchronen Sitzungen. Der gespeicherte Python-Verlauf bleibt nach dem Schließen lesbar.

- **Speichern Sie eine Anmeldung einmal und verwenden Sie sie bei weiteren Läufen wieder**. `save_state(path)` und `load_state(path)` speichern Cookies, lokalen Speicher und IndexedDB in Playwright-kompatiblem JSON. Sowohl synchrone als auch asynchrone Browser-Sitzungen unterstützen sie. (Siehe [Dokumentation](fetching/stealthy.md#save-and-load-session-state))
    - Laden Sie den Zustand, bevor Sie eine Seite abrufen oder neu laden. Erfordert einen gestarteten, gemeinsam genutzten Browser-Kontext ohne `proxy_rotator`. Tabs, Browser-Einstellungen und `sessionStorage` werden nicht gespeichert.

- **Extrahieren Sie offenes Shadow DOM mit `pierce_shadow=True`** und verwenden Sie anschließend CSS oder XPath wie gewohnt. Verfügbar in Browser-Fetchern, Sitzungen und über die CLI-Option `--pierce-shadow`. Behält Slot-Inhalte bei, ohne die aktive Seite zu ändern. Geschlossene Wurzeln und iframe-Dokumente sind in der HTML-Erfassung nicht enthalten. (Siehe [Dokumentation](fetching/stealthy.md#shadow-dom))

- **Wählen Sie, wie Ihr Spider eine Website durchsucht**. `CrawlSpider` und seine Unterklassen, darunter `ContentSpider`, unterstützen `crawl_strategy="bfs"`, um die ältesten Anfragen zuerst einzuplanen, oder `"dfs"` für die neuesten zuerst. Die Priorität hat weiterhin Vorrang. Parallel verarbeitete Seiten können in einer anderen Reihenfolge fertig werden. (Siehe [Dokumentation](spiders/generic-templates.md#crawl-order))

### 🐛 Fehlerbehebungen {#v0.5-bug-fixes}

- **Verbessertes Lösen von Cloudflare-Prüfungen** durch Erkennung verzögert erscheinender Widgets, weniger unnötige Wartezeiten und begrenzte Wiederholungsschleifen für passive Prüfungen und versteckte Frames. Behebt [#468](https://github.com/D4Vinci/Scrapling/issues/468) und [#509](https://github.com/D4Vinci/Scrapling/issues/509).
- **Browser-Start aus einer Windows-Shell mit Administratorrechten korrigiert**. Behebt [#463](https://github.com/D4Vinci/Scrapling/issues/463).
- **Integrierte Stealth-Flags bleiben beim Hinzufügen eigener Browser-Flags erhalten**, von @alkaz-nodemaven in [#430](https://github.com/D4Vinci/Scrapling/pull/430).
- **Verbessertes Parsen der Zeichensatzangaben in Browser-Antworten**, auch bei unterschiedlicher Groß- und Kleinschreibung, Leerzeichen oder Werten in Anführungszeichen.
- **Das Fehlen einer Cloudflare-Prüfung wird nicht mehr als Fehler protokolliert**, wenn keine Prüfung gelöst werden muss. Behebt [#459](https://github.com/D4Vinci/Scrapling/issues/459).

- **Anfrage-Fingerprints korrigiert** für URL-Parameter von @yetval in [#448](https://github.com/D4Vinci/Scrapling/pull/448), leere oder als falsch ausgewertete JSON-Körper von @ac1982 in [#480](https://github.com/D4Vinci/Scrapling/pull/480) und die Einfügereihenfolge der Header von @SarwadnyaMahajan in [#466](https://github.com/D4Vinci/Scrapling/pull/466).
- **Unbeabsichtigte Übernahme von Anfragedaten beim Folgen von Links behoben**, einschließlich veralteter Header für den Anfragekörper, von @yetval in [#462](https://github.com/D4Vinci/Scrapling/pull/462).
- **Blockierte Antworten werden nicht mehr als erfolgreiche Einträge im Entwicklungscache gespeichert**, von @Kuang-xianxin in [#446](https://github.com/D4Vinci/Scrapling/pull/446).
- **Checkpoint-Dateien bleiben erhalten, wenn ein Crawl mit einer Ausnahme fehlschlägt**, von @SulimanAbdulrazzaq in [#486](https://github.com/D4Vinci/Scrapling/pull/486).
- **Fehlerbehandlung für robots.txt korrigiert**, damit fehlgeschlagene Abfragen nicht als Erlaubnis zum Crawlen zwischengespeichert werden, von @prateekraawat1 in [#443](https://github.com/D4Vinci/Scrapling/pull/443).
- **Link-Extraktion mit einschränkenden Selektoren korrigiert**, einschließlich leerer Treffer und Selektoren, die das Link-Element selbst auswählen, von @SulimanAbdulrazzaq in [#452](https://github.com/D4Vinci/Scrapling/pull/452) und [#483](https://github.com/D4Vinci/Scrapling/pull/483).
- **Auswahl der Sitemap-Callbacks korrigiert**, von @SulimanAbdulrazzaq in [#458](https://github.com/D4Vinci/Scrapling/pull/458), **sowie XML-Parsing mit Kommentaren oder Verarbeitungsanweisungen**, von @sup3dev in [#450](https://github.com/D4Vinci/Scrapling/pull/450).
- **Führende Byte-Reihenfolgemarkierungen in robots.txt und CSV-Feeds werden berücksichtigt**, von @SulimanAbdulrazzaq in [#453](https://github.com/D4Vinci/Scrapling/pull/453).
- **Behandlung von `stealthy_headers` in HTTP-Sitzungen von Spidern korrigiert**: Die Option wird an die Sitzung statt direkt an `curl_cffi` übergeben, von @Yigtwxx in [#475](https://github.com/D4Vinci/Scrapling/pull/475).

- **Formularkodierung von Dictionaries für Listen- und Tupelwerte korrigiert**, unter Beibehaltung des Vorrangs der Anfragekörper und der bisherigen Behandlung von `None`, mit Beiträgen von @SulimanAbdulrazzaq in [#485](https://github.com/D4Vinci/Scrapling/pull/485).
- **Zusammenführen von HTTP-Headern aus Sitzung und einzelner Anfrage ohne Beachtung der Groß- und Kleinschreibung korrigiert**, von @SulimanAbdulrazzaq in [#487](https://github.com/D4Vinci/Scrapling/pull/487).
- **Behoben: CLI-Anfragen verwarfen leere oder als falsch ausgewertete JSON-Körper ohne Hinweis**, von @SulimanAbdulrazzaq in [#484](https://github.com/D4Vinci/Scrapling/pull/484).
- **Markdown- und Textdateien werden nun durchgängig als UTF-8 exportiert**. Konvertierungsfehler kürzen bestehende Ausgabedateien nicht mehr, von @SulimanAbdulrazzaq in [#488](https://github.com/D4Vinci/Scrapling/pull/488).
- **Behandlung der User-Agent- und Proxy-Optionen von curl in `curl2fetcher()` korrigiert**, von @SulimanAbdulrazzaq in [#490](https://github.com/D4Vinci/Scrapling/pull/490).

- **Zusammenlaufende Markdown-Blöcke korrigiert**, wenn mehrere ausgewählte Elemente mit `Response.markdown()` oder der CLI-Extraktion umgewandelt werden, mit Beiträgen von @Yigtwxx in [#432](https://github.com/D4Vinci/Scrapling/pull/432).
- **Bereinigung versteckter Inhalte für KI-Ausgaben korrigiert**, um sichtbare Inhalte wie `opacity:0.95` beizubehalten, weitere versteckende Stile zu erkennen und versteckte Slots zu entfernen, mit Beiträgen von @Yigtwxx in [#460](https://github.com/D4Vinci/Scrapling/pull/460).
- **Behoben: Das Entfernen störender Tags brach bei verschachtelten Tags zu früh ab**, von @Yigtwxx in [#474](https://github.com/D4Vinci/Scrapling/pull/474).
- **Generierte CSS- und XPath-Selektoren für das erste von mehreren Geschwisterelementen mit demselben Tag korrigiert**, von @yellow-dog-dog in [#495](https://github.com/D4Vinci/Scrapling/pull/495).
- **Eine Veraltungswarnung des lxml-HTML-Parsers behoben**, von @afsuyadi in [#493](https://github.com/D4Vinci/Scrapling/pull/493).

### Dokumentation {#v0.5-docs}

- **Die gesamte Website spricht jetzt zehn Sprachen**: Englisch, Arabisch, Spanisch, brasilianisches Portugiesisch, Französisch, Deutsch, vereinfachtes Chinesisch, Japanisch, Russisch und Koreanisch. Leitfäden, API-Referenzen, Tutorials und der [Änderungsverlauf](changelog.md) sind übersetzt. Arabisch unterstützt die Leserichtung von rechts nach links. Beim Sprachwechsel bleiben Seite und Abschnitt erhalten.
- **Klarere Leitfäden, README-Beispiele und Einrichtungsschritte**, die Checkpoint-Daten, Browser-Kodierungen, gespeicherten Zustand, Netzwerkverlauf, Shadow DOM und Crawl-Reihenfolge abdecken.
- **Den Agent Skill aktualisiert**, einschließlich Beispielen, Referenzen und herunterladbarem Archiv, für die aktuellen Browser- und MCP-Werkzeuge.
- **Den Änderungsverlauf auf die Website verschoben** und Zugriff auf den Markdown-Quelltext jeder Seite hinzugefügt.

### Projekt {#v0.5-project}

- Scraplings Logo, Titelbilder und Website-Darstellung erneuert.
- Tests für Browser-Aktionen, Dialoge, Extraktion, Screenshots, JavaScript, Netzwerkaufzeichnung, Zustandsdateien, Shadow DOM und Crawler-Korrekturen erweitert.
- Einen Marker für Browser-Tests und getrennte Läufe für Browser-, asynchrone und parallele Tests hinzugefügt. Windows-Kompatibilität der Checkpoint- und CSV-Tests verbessert, von @diegobravtraps-oss in [#457](https://github.com/D4Vinci/Scrapling/pull/457).
- Gemeinsame Build-Konfiguration der mehrsprachigen Dokumentation und Hinweise für Beiträge aktualisiert.

## [v0.4.15](https://github.com/D4Vinci/Scrapling/releases/tag/v0.4.15) - 2026-08-23 {#v0.4.15}

**Eine der größten Veröffentlichungen dieses Jahres: ein überarbeiteter MCP-Server, Markdown für RAG mit einer Zeile Code, besseres Lösen von Cloudflare-Prüfungen und Browser-Tabs, die für die Automatisierung offen bleiben 🚀**

!!! warning "Warnung"

    **Diese Version enthält inkompatible Änderungen am MCP-Server. Lesen Sie vor dem Update den Abschnitt zu den [inkompatiblen Änderungen](https://github.com/D4Vinci/Scrapling/blob/v0.4.15/docs/ai/mcp-server.md#breaking-changes).**

### 🚀 Neuerungen und Verbesserungen der Bedienung {#v0.4.15-new-stuff-and-quality-of-life-changes}

- **Browser-Tabs bleiben jetzt offen und werden für weitere Anfragen wiederverwendet** (siehe [Dokumentation](fetching/stealthy.md#session-management)):
    - Alle Browser-Sitzungen behalten ihre Tabs nach einer Anfrage. Die nächste Anfrage nutzt einen freien Tab, statt einen neuen zu öffnen.
    - Jede Anfrage wendet ihre eigenen Einstellungen (Zeitlimits, Header und Ressourcensperren) erneut auf den zugewiesenen Tab an. So gelangen keine Einstellungen von einer Anfrage in die nächste.
    - Tabs mit Fehlern werden geschlossen und ersetzt. Die neue Methode `close_pages()` schließt alle offenen Tabs.
    - Die abgerufene Seite bleibt geladen. Eine Funktion `page_setup` in der nächsten Anfrage läuft deshalb auf dieser Seite, bevor der Browser zu einer anderen wechselt. Damit lassen sich Automatisierungsschritte über mehrere Anfragen verknüpfen.

- **Wandeln Sie jede Seite mit `Response.markdown()` in sauberes Markdown für LLMs um** (siehe [Dokumentation](ai/building-rag-systems.md)):

    ```python
    from scrapling.fetchers import Fetcher

    markdown = Fetcher.get("https://example.com").markdown(main_content_only=True)
    ```

    - Skripte, Stile und versteckte Inhalte für Prompt Injection werden immer zuerst entfernt, mit derselben Bereinigung wie im MCP-Server.
    - Übergeben Sie `css_selector`, um nur die benötigten Elemente umzuwandeln.
    - Verfügbar über das neue Extra `rag` (`pip install "scrapling[rag]"`), das auch in den Extras `ai`/`shell`/`all` enthalten ist.

- **Neue Vorlage `SiteToMarkdownSpider`, um eine ganze Website zu crawlen und eine Markdown-Sammlung für RAG-Pipelines zu erstellen** (siehe [Dokumentation](ai/building-rag-systems.md)):

    ```python
    from scrapling.spiders import SiteToMarkdownSpider

    class DocsSpider(SiteToMarkdownSpider):
        name = "docs"
        start_urls = ["https://example.com/docs/"]
        allowed_domains = {"example.com"}
        output_dir = "docs_markdown"

    result = DocsSpider().start()
    result.items.to_jsonl("docs.jsonl")
    ```

    - Liefert einen Datensatz pro Seite mit `url`/`title`/`markdown`. Der optionale Parameter `output_dir` schreibt eine Markdown-Datei pro Seite.
    - `max_pages` begrenzt den Crawl. Da die Vorlage auf `CrawlSpider` aufbaut, haben Sie durch Überschreiben von `rules()` volle Kontrolle über die verfolgten Links.

- **Der MCP-Server wurde überarbeitet (inkompatible Änderung)** (siehe [inkompatible Änderungen](https://github.com/D4Vinci/Scrapling/blob/v0.4.15/docs/ai/mcp-server.md#breaking-changes) und [Dokumentation](ai/mcp-server.md)):
    - Die 13 Werkzeuge sind jetzt in zwei Modi aufgeteilt: Werkzeuge für einzelne Aufrufe (`fetch`, `bulk_fetch`, `stealthy_fetch`, `bulk_stealthy_fetch`), die immer ihren eigenen Browser starten und ihre tatsächlichen Standardwerte anzeigen, sowie Sitzungswerkzeuge, die eine einmal geöffnete Sitzung nutzen.
    - Das neue Werkzeug `session_fetch` ruft Seiten über eine Browser-Sitzung ab. `open_session` enthält jetzt nur noch Einstellungen auf Browser-Ebene und gibt dem KI-Agenten die tatsächlich verwendeten Einstellungen der Sitzung zurück.
    - Das Werkzeug `get` wurde in `make_request` umbenannt und unterstützt jetzt jede HTTP-Methode.
    - Die neuen Werkzeuge `open_request_session` und `session_make_request` geben der KI dauerhafte HTTP-Sitzungen, die Cookies und den Browser-Fingerprint zwischen Anfragen behalten.
    - Damit setzen Abrufe auch nicht mehr die Sitzungseinstellungen zurück. Dieses Problem wurde zuerst von @Yigtwxx in [#418](https://github.com/D4Vinci/Scrapling/pull/418) behoben.

- **Der HTTP-Transport des MCP-Servers erfordert jetzt eine Authentifizierung und lauscht standardmäßig auf localhost (inkompatible Änderung)**, von @yamantaka-singh in [#414](https://github.com/D4Vinci/Scrapling/pull/414) (behebt [#413](https://github.com/D4Vinci/Scrapling/issues/413), siehe [Dokumentation](ai/mcp-server.md#authentication)):
    - Übergeben Sie `--auth-token` (oder die Umgebungsvariable `SCRAPLING_MCP_AUTH_TOKEN`), um ein Bearer-Token zu verlangen. Mit `--no-auth` betreiben Sie den Server bewusst ohne Authentifizierung.
    - Übergeben Sie `--host 0.0.0.0`, um Verbindungen aus dem Netzwerk anzunehmen.

### 🐛 Fehlerbehebungen {#v0.4.15-bug-fixes}

- **Cloudflare Turnstile/Interstitial wird jetzt unabhängig von den Sprach- und Regionseinstellungen des Browsers gelöst. Interaktive Prüfungen im Headless-Modus führen nicht mehr zu Endlosschleifen**. Seiten im getarnten Browser stürzen auch nicht mehr während der Lösung ab, mit Beiträgen von @subediparas5 in [#412](https://github.com/D4Vinci/Scrapling/pull/412). (Behebt [#411](https://github.com/D4Vinci/Scrapling/issues/411) und [#422](https://github.com/D4Vinci/Scrapling/issues/422))
- **Behoben: `find`/`find_all` mit `class_` übersahen ohne Hinweis Elemente mit mehreren Klassen**, von @yetval in [#410](https://github.com/D4Vinci/Scrapling/pull/410), **sowie leere `class_`-Werte und nicht maskierte CSS-Zeichenfolgen**, von @yamantaka-singh in [#417](https://github.com/D4Vinci/Scrapling/pull/417).
- **Behoben: Antworten aus dem Cache verloren beim erneuten Verwenden im `development_mode` die Metadaten der Anfrage**, von @Yigtwxx in [#419](https://github.com/D4Vinci/Scrapling/pull/419).
- **Behoben: HTTP-Anfragen mit `retries` unter 1 schlugen fehl, ohne die Anfrage zu senden**, von @Yigtwxx in [#420](https://github.com/D4Vinci/Scrapling/pull/420).

### Dokumentation {#v0.4.15-docs}

- **Die Website-Bereiche wurden neu geordnet**: Der neue Bereich „Mit KI verwenden“ enthält den MCP-Server, die neue Seite zum [Agent Skill](ai/agent-skill.md) und die Anleitung zum [Aufbau von RAG-Systemen](ai/building-rag-systems.md). Die Anleitung zum Wechsel von BeautifulSoup steht jetzt neben der Scrapy-Integration unter „Integrationen und Migrationen“.
- **Ein [Änderungsverlauf](changelog.md) wurde hinzugefügt**, der die Hinweise zu allen bisher veröffentlichten Versionen im Repository enthält.

## [v0.4.14](https://github.com/D4Vinci/Scrapling/releases/tag/v0.4.14) - 2026-08-10 {#v0.4.14}

**Ein schnelles Wartungsupdate zur Behebung der Installation mit `uv` 🔧**

### 🐛 Fehlerbehebungen {#v0.4.14-bug-fixes}

- **Behoben: `uv` weigerte sich standardmäßig, v0.4.13 zu installieren, und wechselte ohne Hinweis zu einer älteren Version**. Die vorherige Version verlangte eine Vorabversion von `curl_cffi`. `uv` erlaubt das nur, wenn es ausdrücklich aktiviert wird.
Alle Abhängigkeiten lassen sich jetzt mit stabilen Versionen auflösen. (Behebt [#407](https://github.com/D4Vinci/Scrapling/issues/407))

## [v0.4.13](https://github.com/D4Vinci/Scrapling/releases/tag/v0.4.13) - 2026-08-09 {#v0.4.13}

**Ein neues Update mit Feed-Spidern und einem intelligenteren MCP-Server 🎉**

### 🚀 Neuerungen und Verbesserungen der Bedienung {#v0.4.13-new-stuff-and-quality-of-life-changes}

- **Neue Spider-Vorlagen für Feeds**. `XMLFeedSpider` durchläuft die Knoten beliebiger XML-Feeds (RSS, Atom, Produkt-Feeds usw.), und `CSVFeedSpider` durchläuft CSV-Zeilen als Dictionaries. Beide entpacken mit gzip komprimierte Feeds automatisch. (Siehe [Dokumentation](spiders/generic-templates.md))

  ```python
  from scrapling.spiders import XMLFeedSpider

  class RSSSpider(XMLFeedSpider):
      name = "rss"
      start_urls = ["https://example.com/feed.xml"]

      async def parse_node(self, response, node):
          yield {"title": node.findtext("title"), "link": node.findtext("link")}

  result = RSSSpider().start()
  ```

- **Der MCP-Server wurde auf MCP SDK v2 umgestellt und verbessert**. Er enthält jetzt Anweisungen, die Ihrem KI-Agenten die effiziente Nutzung der Werkzeuge erklären. Jedes Werkzeug gibt Annotationen an, damit Clients wie Claude Code rein lesende Werkzeuge automatisch genehmigen können. Kürzere Beschreibungen sparen Tokens, und der Server meldet seine Version und sein Logo an MCP-Clients. (Siehe [Dokumentation](ai/mcp-server.md))
- **Der Befehl `scrapling-mcp` wurde hinzugefügt**. Er führt direkt `scrapling mcp` aus. So lässt sich Scrapling mit einer Zeile bei MCP-Clients und Verzeichnissen registrieren, die einen einzelnen Befehl erwarten.
- **Playwright/Patchright und Browser sind nicht mehr auf feste Versionen begrenzt**. Der erzeugte User-Agent passt jetzt immer genau zur Chromium-Version, die Ihre installierte Version von Playwright/Patchright steuert. Deshalb legt Scrapling deren Versionen nicht mehr fest, und Sie können sie frei aktualisieren. Führen Sie nach dem Update `scrapling install --force` aus, um die Browser zu aktualisieren.

### 🐛 Fehlerbehebungen {#v0.4.13-bug-fixes}

- **Behoben: Der Import von Scrapling brach mit einem ValueError von `browserforge` ab**, wenn das Datenpaket für Fingerprints hinter den Browser-Versionen zurücklag. (Behebt [#394](https://github.com/D4Vinci/Scrapling/issues/394), [#396](https://github.com/D4Vinci/Scrapling/issues/396) und [#400](https://github.com/D4Vinci/Scrapling/issues/400))
- **Falsche Größen der Seiten-Pools in den MCP-Browser-Werkzeugen für Stapelabrufe wurden korrigiert**. Wegen dieses Fehlers schlug `bulk_fetch` bei mehr als 50 URLs fehl, und `bulk_stealthy_fetch` rief alle URLs über einen einzigen Tab ab. Von @Yigtwxx in [#393](https://github.com/D4Vinci/Scrapling/pull/393).

### Projekt {#v0.4.13-project}

- **Neue [Richtlinie für KI-gestützte Beiträge](https://github.com/D4Vinci/Scrapling/blob/main/AI_POLICY.md)**: Beiträge mit KI-Unterstützung sind willkommen, müssen aber im PR oder Issue gekennzeichnet werden. Beiträge, die ohne Kennzeichnung nach KI-Ausgaben aussehen, erhalten ein Label und werden geschlossen.

## [v0.4.12](https://github.com/D4Vinci/Scrapling/releases/tag/v0.4.12) - 2026-07-26 {#v0.4.12}

**Eine Version, mit der Ihre Spider intelligenter auf die gecrawlten Websites reagieren**

### 🚀 Neuerungen und Verbesserungen der Bedienung {#v0.4.12-new-stuff-and-quality-of-life-changes}

- **Spider können ihre Geschwindigkeit jetzt mit AutoThrottle selbst anpassen.** Statt einen `download_delay` zu schätzen, der entweder zu langsam ist oder zu einer Sperre führt, misst der Spider die Antwortgeschwindigkeit jeder Website und passt die Wartezeit pro Domain selbst an. Sobald eine Website Sie sperrt oder die Anfragerate begrenzt, verdoppelt er die Wartezeit (oder wartet genau so lange, wie der Header `Retry-After` verlangt), bis das aufhört. Danach wird er wieder schneller. Ihr `download_delay` und jeder `Crawl-delay` aus robots.txt gelten weiterhin als Mindestwert. (Siehe [Dokumentation](spiders/advanced.md#autothrottle))

    ```python
    class MySpider(Spider):
        name = "adaptive"
        start_urls = ["https://example.com"]
        autothrottle_enabled = True
        autothrottle_start_delay = 2.0
        autothrottle_max_delay = 30.0
        autothrottle_block_backoff = True
    ```

- **Exportieren Sie Ihre Ergebnisse als CSV und XML**, zusätzlich zu den bisherigen JSON/JSONL-Exporten. Auch Datensätze mit unterschiedlichen Schlüsseln werden ohne Verluste exportiert. Verschachtelte Werte werden als JSON geschrieben. (Siehe [Dokumentation](spiders/getting-started.md))

    ```python
    result = MySpider().start()
    result.items.to_csv("products.csv")
    result.items.to_xml("products.xml")
    ```

- **Der MCP-Server kann jetzt eine Authentifizierung verlangen**. So können Sie ihn sicher bereitstellen, statt ihn nur auf Ihrem eigenen Rechner zu betreiben. Jede Anfrage ohne Token wird abgelehnt. Sie können auch einschränken, auf welche Hostnamen der Server antwortet. (Siehe [Dokumentation](ai/mcp-server.md))

    ```bash
    scrapling mcp --http --auth-token "$(openssl rand -hex 32)"
    ```

- **Browser akzeptieren jetzt CDP-URLs über HTTP**, nicht nur über WebSocket. Neben den `wss://`-Endpunkten verwalteter Browser-Anbieter können Sie jeden Browser-Fetcher oder jede MCP-Sitzung mit einem selbst gestarteten Chrome mit `--remote-debugging-port=9222` verbinden.

- **Veröffentlichte Docker-Images tragen jetzt ein Tag mit ihrer Versionsnummer**, statt nur `latest`. So können Sie genau die gewünschte Version festlegen. Von @JanRK in [#384](https://github.com/D4Vinci/Scrapling/pull/384).

### 🐛 Fehlerbehebungen {#v0.4.12-bug-fixes}

- **Behoben: Antworten aus dem Cache verloren alle Cookies, wenn sie von einem Browser kamen**. Dadurch funktionierte im Entwicklungsmodus der Spider die Sitzungs- oder Authentifizierungslogik, die diese Cookies brauchte, ohne Hinweis nicht mehr. Von @amitvijapur in [#379](https://github.com/D4Vinci/Scrapling/pull/379). (Behebt [#376](https://github.com/D4Vinci/Scrapling/issues/376))

- **Behoben: `StealthyFetcher` erzwang die Regionseinstellung `en-US`** für jeden Browser, statt die Systemeinstellung zu übernehmen. Websites erkannten dadurch einen Widerspruch zwischen Ihren Sprach- und Regionseinstellungen und Ihrer IP-Adresse und stuften Sie als verdächtig ein. Google antwortete zum Beispiel mit 429. (Behebt [#381](https://github.com/D4Vinci/Scrapling/issues/381))

- **Eine irreführende Fehlermeldung im Speichersystem wurde korrigiert**, und ein ungenutzter Aufruf nach Einfügevorgängen wurde entfernt. Von @fix2015 in [#377](https://github.com/D4Vinci/Scrapling/pull/377).

### Leistung {#v0.4.12-performance}

- **Die Laufzeit von `get_all_text()` wächst jetzt proportional zur Anzahl der Knoten, O(nodes)**, statt die Vorfahren jedes einzelnen Textknotens zu durchlaufen. Das macht die Methode auf tief verschachtelten Seiten etwa 5-6-mal schneller. Von @yetval in [#378](https://github.com/D4Vinci/Scrapling/pull/378).

## [v0.4.11](https://github.com/D4Vinci/Scrapling/releases/tag/v0.4.11) - 2026-07-12 {#v0.4.11}

**Ein großes Update mit der ersten Spider-Vorlage für eine Plattform, einem schnelleren Parser und wichtigen Fehlerbehebungen 🎉**

### 🚀 Neuerungen und Verbesserungen der Bedienung {#v0.4.11-new-stuff-and-quality-of-life-changes}

- **`ShopifySpider`, die erste Spider-Vorlage für eine Plattform, wurde hinzugefügt!** Extrahieren Sie alle Produkte eines Shopify-Shops über dessen JSON-API, ohne das HTML der Website zu verwenden. Erstellen Sie eine Unterklasse, setzen Sie die Shop-Domain, und schon sind Sie fertig (siehe [Dokumentation](spiders/platform-templates.md))

  ```python
  from scrapling.spiders import ShopifySpider

  class MyStore(ShopifySpider):
      target_website = "example.com"

  result = MyStore().start()
  ```

- **`--executable-path` wurde zu den Browser-Befehlen der CLI hinzugefügt**. Sowohl `scrapling extract fetch` als auch `scrapling extract stealthy-fetch` akzeptieren jetzt eine eigene ausführbare Browser-Datei, die mit Chromium kompatibel ist. Ohne diese Option verwenden sie die Umgebungsvariable `SCRAPLING_EXECUTABLE_PATH`. Damit bieten sie denselben Funktionsumfang wie der MCP-Server (löst [#371](https://github.com/D4Vinci/Scrapling/issues/371))

  ```bash
  scrapling extract fetch "https://example.com" page.html --executable-path "/path/to/chromium"
  ```

### 🤖 Verbesserungen der Bedienung {#v0.4.11-quality-of-life-changes}
- **`find_by_text` und `find_by_regex` sind jetzt bis zu etwa 2-mal schneller**, wenn `first_match` aktiviert ist (Standard). Elemente werden erst bei Bedarf in Objekte umgewandelt, sodass die Suche beim ersten Treffer endet. Von @yetval in [#370](https://github.com/D4Vinci/Scrapling/pull/370)
- **Die Benchmarks wurden mit neuen Zahlen und den neuesten Versionen aller Bibliotheken aktualisiert.**
- **Die Beitragsregeln wurden aktualisiert**

### 🐛 Fehlerbehebungen {#v0.4.11-bug-fixes}

- **Abstürze der Abrufwerkzeuge des MCP-Servers auf Seiten mit Steuerzeichen wurden behoben**. Dabei erschien der Fehler `All strings must be XML compatible`. Von @yetval in [#368](https://github.com/D4Vinci/Scrapling/pull/368) (behebt [#366](https://github.com/D4Vinci/Scrapling/issues/366))

## [v0.4.10](https://github.com/D4Vinci/Scrapling/releases/tag/v0.4.10) - 2026-07-04 {#v0.4.10}

**Ein neues Update mit einer neuen Scrapy-Integration und mehreren Korrekturen aus der Community 🎉**

### 🚀 Neuerungen und Verbesserungen der Bedienung {#v0.4.10-new-stuff-and-quality-of-life-changes}

- **Eine Scrapy-Integration wurde hinzugefügt**, damit Sie die Parsing-API von Scrapling in vorhandenen Scrapy-Projekten nutzen können, ohne sie neu zu schreiben. Setzen Sie den Dekorator `scrapling_response` auf einen Spider-Callback. Die empfangene Antwort wird dann zu einer `Response` von Scrapling, während Scrapy weiterhin den Crawl steuert (siehe [Dokumentation](integrations/scrapy.md)):

    ```python
    import scrapy
    from scrapling.integrations.scrapy import scrapling_response

    class QuotesSpider(scrapy.Spider):
        name = "quotes"
        start_urls = ["https://quotes.toscrape.com"]

        @scrapling_response
        def parse(self, response):  # `response` is now a Scrapling Response
            first_quote = response.find_by_text("The world as we have created it", partial=True)
            for quote in [first_quote, *first_quote.find_similar()]:
                yield {"text": quote.get_all_text(strip=True)}
    ```

- **Der MCP-Server kann jetzt einen eigenen, mit Chromium kompatiblen Browser nutzen**, und zwar für alle Browser-Werkzeuge. Legen Sie ihn einmal mit `scrapling mcp --executable-path "/path/to/chromium"` oder der Umgebungsvariable `SCRAPLING_EXECUTABLE_PATH` fest, oder pro Anfrage mit dem Argument `executable_path`. Von @samrusani in [#360](https://github.com/D4Vinci/Scrapling/pull/360) (löst [#347](https://github.com/D4Vinci/Scrapling/issues/347))
- **Alle Browser und Fingerprints wurden aktualisiert**. Führen Sie nach dem Update `scrapling install --force` aus, um sie zu erneuern.

### 🐛 Fehlerbehebungen {#v0.4.10-bug-fixes}

- **Unlesbarer Text (Mojibake) von Browser-Fetchern auf Websites ohne UTF-8 wurde behoben**, von @yehudalevy-collab in [#365](https://github.com/D4Vinci/Scrapling/pull/365) (behebt [#364](https://github.com/D4Vinci/Scrapling/issues/364)).
- **Behoben: `LinkExtractor` filterte zusammengesetzte Dateiendungen wie `.tar.gz` nicht**, von @renbkna in [#359](https://github.com/D4Vinci/Scrapling/pull/359) (behebt [#349](https://github.com/D4Vinci/Scrapling/issues/349)).
- **Der Verlust laufender Anfragen in Checkpoints pausierter Crawls wurde behoben. Beim Fortsetzen werden sie jetzt nicht mehr übersprungen**, von @yetval in [#358](https://github.com/D4Vinci/Scrapling/pull/358).
- **Falsch berechnete Crawl-Wartezeiten aus den robots.txt-Regeln `Request-rate` wurden behoben**, durch das Protego-Update und angepasste Tests von @Disaster-Terminator in [#355](https://github.com/D4Vinci/Scrapling/pull/355).

### Dokumentation {#v0.4.10-docs}

- **Das Zusammenspiel von `init_script` mit dem isolierten Ausführungskontext von Patchright im Stealth-Modus wurde erklärt**, von @mturac in [#353](https://github.com/D4Vinci/Scrapling/pull/353) (löst [#350](https://github.com/D4Vinci/Scrapling/issues/350)).
- **Die Installation des Agent Skills über [skills.sh](https://skills.sh/D4Vinci/Scrapling) wurde hinzugefügt**, von @ob-aion in [#363](https://github.com/D4Vinci/Scrapling/pull/363).

## [v0.4.9](https://github.com/D4Vinci/Scrapling/releases/tag/v0.4.9) - 2026-06-07 {#v0.4.9}

**Ein Wartungsupdate mit vielen Fehlerbehebungen zu Meldungen aus der Community 🛠️**

### 🚀 Neuerungen und Verbesserungen der Bedienung {#v0.4.9-new-stuff-and-quality-of-life-changes}

- **Alle Browser und Fingerprints wurden aktualisiert**. Führen Sie nach dem Update `scrapling install --force` aus, um sie zu erneuern.
- **Die Option `--version` wurde zur CLI hinzugefügt**, von @ETM-Code in [#303](https://github.com/D4Vinci/Scrapling/pull/303) (löst [#299](https://github.com/D4Vinci/Scrapling/issues/299))

### 🐛 Fehlerbehebungen {#v0.4.9-bug-fixes}

- **Behoben: Das Argument `proxy` auf Sitzungsebene wurde in HTTP-Sitzungen ohne Hinweis ignoriert**, wodurch Ihre echte IP sichtbar werden konnte (löst [#295](https://github.com/D4Vinci/Scrapling/issues/295)). Wenn Sie jetzt einen `proxy` auf Sitzungsebene mit dem Argument `proxies` pro Anfrage kombinieren (oder umgekehrt), wird ein Fehler ausgelöst. Es wird nicht mehr eines der Argumente ohne Hinweis verworfen.
- **Fehler bei der Browser-Navigation beim Kombinieren von `init_script` mit `user_data_dir` wurden behoben** (löst [#294](https://github.com/D4Vinci/Scrapling/issues/294)).
- **Die Erkennung der Zeichenkodierung wurde korrigiert, wenn Websites den charset-Wert im Header `Content-Type` in Anführungszeichen setzen**, von @Bortlesboat in [#323](https://github.com/D4Vinci/Scrapling/pull/323).
- **Ein `IndexError` beim adaptiven Wiederfinden von Elementen mit aktiviertem `auto_save` wurde behoben**, von @Mubashirrrr in [#340](https://github.com/D4Vinci/Scrapling/pull/340).
- **Abstürze beim Speichern von Checkpoints und Cache der Spider unter Windows wurden behoben**, von @MrStarkEG in [#344](https://github.com/D4Vinci/Scrapling/pull/344).
- **Falsche Ähnlichkeitswerte in `find_similar` für Elemente mit unterschiedlich vielen Attributen wurden korrigiert** (löst [#322](https://github.com/D4Vinci/Scrapling/issues/322)).

### Dokumentation {#v0.4.9-docs}

- **Es wurde klargestellt, dass die Standardinstallation nur den Parser enthält** und Fetcher sowie Spider die Extras benötigen (löst [#343](https://github.com/D4Vinci/Scrapling/issues/343)).
- **Der Name des Docker-Images wurde in den übrigen Beispielen korrigiert**, von @evanclan in [#315](https://github.com/D4Vinci/Scrapling/pull/315).
- **Ein defekter Link in der Beitragsanleitung wurde korrigiert**, von @Bortlesboat in [#320](https://github.com/D4Vinci/Scrapling/pull/320).

## [v0.4.8](https://github.com/D4Vinci/Scrapling/releases/tag/v0.4.8) - 2026-05-11 {#v0.4.8}

**Ein großes Spider-Update, das das Crawl-System weiter verbessert 🕷️**

### 🚀 Neuerungen und Verbesserungen der Bedienung {#v0.4.8-new-stuff-and-quality-of-life-changes}

- **Das Werkzeug `LinkExtractor` wurde hinzugefügt**, unter `scrapling.spiders.LinkExtractor`, um URLs aus einer `Response` zu lesen. Es bietet viele Einstellmöglichkeiten (siehe [Dokumentation](spiders/generic-templates.md))

    ```python
    from scrapling.spiders import LinkExtractor

    extractor = LinkExtractor(allow=r"/posts/", deny_domains=["ads.example.com"])
    ```

- **Die allgemeinen Spider-Vorlagen `CrawlSpider` und `CrawlRule` wurden hinzugefügt**. Sie müssen damit nicht mehr immer denselben Code für „Links verfolgen, die zu diesem Muster passen“ schreiben. Überschreiben Sie `rules()`, um eine Liste von `CrawlRule`-Objekten zurückzugeben, die jeweils mit einem `LinkExtractor` verbunden sind. (Siehe [Dokumentation](spiders/generic-templates.md))

    ```python
    from scrapling.spiders import CrawlSpider, CrawlRule, LinkExtractor

    class QuotesSpider(CrawlSpider):
        name = "blog"
        start_urls = ["https://quotes.toscrape.com/"]

        def rules(self):
            return [
                CrawlRule(LinkExtractor(allow=r"/author/"), callback=self.parse_author),
                CrawlRule(LinkExtractor(allow=r"/page/\d+/")),  # pagination, no callback
            ]

        async def parse_author(self, response):
            yield {
                "name": response.css(".author-title::text").get(),
                "birthday": response.css(".author-born-date::text").get(),
                "url": response.url,
            }
    ```

- **Die Vorlage `SitemapSpider` wurde hinzugefügt**. Sie startet einen Crawl direkt aus einer Sitemap oder über URLs zu `robots.txt`-Dateien. Sie verarbeitet gzip-komprimierte Sitemaps und bietet viele Einstellmöglichkeiten. URLs werden über die Crawl-Regeln zugeordnet, wie oben für **CrawlSpider** gezeigt. (Siehe [Dokumentation](spiders/generic-templates.md))

    ```python
    from scrapling.spiders import SitemapSpider, CrawlRule, LinkExtractor

    class NewsSitemap(SitemapSpider):
        name = "news"
        sitemap_urls = ["https://example.com/robots.txt"]

        def rules(self):
            return [
                CrawlRule(LinkExtractor(allow=r"/articles/"), callback=self.parse_article),
            ]

        async def parse_article(self, response):
            yield {"url": response.url, "title": response.css("h1::text").get()}
    ```

- **Das adaptive Wiederfinden nutzt jetzt in allen Methoden standardmäßig eine Ähnlichkeitsschwelle von 40 %** statt `0`. Dadurch arbeitet die adaptive Funktion besser. Wenn kein Element den Grenzwert überschreitet, zeigt eine Warnung jetzt den höchsten gefundenen Wert an. So können Sie `percentage` bei Bedarf bewusst senken.

- **Alle Browser und Fingerprints wurden aktualisiert**. Führen Sie nach dem Update erneut `scrapling install  --force` aus, um die Browser und Fingerprints zu erneuern.

### 🐛 Fehlerbehebungen {#v0.4.8-bug-fixes}

- **Behoben: `Fetcher.configure(...)` wurde nicht auf Aufrufe einzelner Anfragen angewendet**. Dieselbe Korrektur gilt für `AsyncFetcher`.
- **Falsche Anfrage-Fingerprints, die zu doppelten Anfragen in Spidern führten, wurden korrigiert**, von @yetval in [#255](https://github.com/D4Vinci/Scrapling/pull/255).
- **Die adaptive Scraping-Engine warnt jetzt bei schwachen Übereinstimmungen.** Zusammen mit der geänderten Schwelle erhalten Sie bei fehlgeschlagenem Wiederfinden jetzt eine Warnung statt eines irreführenden Elements als „beste Schätzung“.

### Dokumentation {#v0.4.8-docs}

- **Ältere Codebeispiele wurden in der gesamten Dokumentation aktualisiert**, damit sie zur aktuellen Version passen.
- **Das Kopieren und Einfügen von Code auf der Dokumentationswebsite wurde verbessert**, und der Agent Skill wurde gekürzt, damit er bei jedem Aufruf weniger Tokens benötigt.

## [v0.4.7](https://github.com/D4Vinci/Scrapling/releases/tag/v0.4.7) - 2026-04-17 {#v0.4.7}

**Ein Update, mit dem Ihre KI-Agenten Seiten sehen können 📸**

### 🚀 Neuerungen und Verbesserungen der Bedienung {#v0.4.7-new-stuff-and-quality-of-life-changes}

- **Das MCP-Werkzeug `screenshot` wurde hinzugefügt**. Es erstellt ein Bild der Seite und gibt es als echten MCP-Block vom Typ `ImageContent` zurück, damit das Modell es sehen kann. Das Werkzeug braucht eine offene Browser-Sitzung. Rufen Sie daher zuerst `open_session` auf (mit `dynamic` oder `stealthy`) und übergeben Sie hier die `session_id`. Unterstützt werden PNG und JPEG, Aufnahmen ganzer Seiten, JPEG-Qualität und die üblichen Warteeinstellungen (`wait`, `wait_selector`, `network_idle`, `timeout`). (Setzt [#244](https://github.com/D4Vinci/Scrapling/issues/244) um)
- **Ein eigener Parameter `session_id` wurde zu `open_session` hinzugefügt**. So können Sie Sitzungen sinnvoll benennen (`"search"`, `"checkout"`), statt den zufälligen hexadezimalen Standardwert mit 12 Zeichen zu nutzen. Von @hauntedhost in [#243](https://github.com/D4Vinci/Scrapling/pull/243)

### 🐛 Fehlerbehebungen {#v0.4.7-bug-fixes}

- **Fehler im Zustand von `FetcherSession` und ein Absturz beim Schließen einer verzögert gestarteten Sitzung wurden behoben**. Von @yetval in [#245](https://github.com/D4Vinci/Scrapling/pull/245)
- **`TypeError: Session.request() got an unexpected keyword argument 'block_ads'` wurde behoben**, wenn die CLI-Option `--ai-targeted` mit HTTP-Befehlen verwendet wird. Von @voidborne-d in [#249](https://github.com/D4Vinci/Scrapling/pull/249) (behebt [#247](https://github.com/D4Vinci/Scrapling/issues/247))

### Übersetzungen {#v0.4.7-translations}

- **Eine brasilianisch-portugiesische Übersetzung der README wurde hinzugefügt**, von @rgomids in [#250](https://github.com/D4Vinci/Scrapling/pull/250)

## [v0.4.6](https://github.com/D4Vinci/Scrapling/releases/tag/v0.4.6) - 2026-04-13 {#v0.4.6}

**Ein Update mit Schwerpunkt auf Browser-Tarnung, Datenschutz und der Arbeit von Entwicklern 🔒**

### 🚀 Neuerungen und Verbesserungen der Bedienung {#v0.4.6-new-stuff-and-quality-of-life-changes}

- **Integrierter Werbeblocker für Browser-Fetcher hinzugefügt**. Übergeben Sie `block_ads=True`, um Anfragen an etwa 3.500 bekannte Werbe- und Tracking-Domains direkt beim Abfangen der Route zu blockieren: kein DNS, kein TCP, sofortiger Abbruch. Mit `blocked_domains` können Sie eigene Listen ergänzen. Der MCP-Server und der CLI-Modus `--ai-targeted` schalten dies automatisch ein, um Tokens zu sparen und Seiten schneller zu laden.

    ```python
    page = StealthyFetcher.fetch('https://example.com', block_ads=True)
    ```

- **Unterstützung für DNS-over-HTTPS hinzugefügt**, um DNS-Lecks bei der Nutzung von Proxys zu vermeiden. Übergeben Sie `dns_over_https=True`, um DNS-Anfragen über Cloudflares DoH-Dienst zu leiten. So wird Ihr echter Standort nicht durch die DNS-Auflösung sichtbar, auch wenn Ihr HTTP-Verkehr durch einen Proxy läuft.

    ```python
    page = StealthyFetcher.fetch('https://example.com', proxy='http://proxy:8080', dns_over_https=True)
    ```

- **Der Callback `page_setup` wurde für Browser-Fetcher hinzugefügt**. Diese Funktion läuft vor `page.goto()`. Damit können Sie Ereignis-Listener, Routen oder Skripte registrieren, die vor der Navigation eingerichtet sein müssen. Sie ergänzt `page_action` (wird nach der Navigation ausgeführt). (Löst [#237](https://github.com/D4Vinci/Scrapling/issues/237))

    ```python
    def capture_websockets(page):
        page.on("websocket", lambda ws: print(f"WS: {ws.url}"))

    page = DynamicFetcher.fetch('https://example.com', page_setup=capture_websockets)
    ```

- **Die CLI-Optionen `--block-ads` und `--dns-over-https` wurden hinzugefügt**, sowohl für `fetch` als auch für `stealthy-fetch`.

### 🐛 Fehlerbehebungen {#v0.4.6-bug-fixes}

- **Der Typalias `Seconds` wurde korrigiert**, der Dezimalwerte ablehnte. `wait=1.5` oder `timeout=500.0` verursachten bei Browser-Fetchern einen Typfehler, weil der Alias `float` fälschlich als Metadaten statt als Typ behandelte. Von @kuishou68 in [#240](https://github.com/D4Vinci/Scrapling/pull/240)
- **Doppelte ID-Abschnitte beim Erzeugen vollständiger Selektorpfade wurden behoben**. Bei Elementen mit `id`-Attributen wurde der Selektor beim Erzeugen vollständiger CSS/XPath-Pfade doppelt angehängt. Das führte zu Selektoren wie `body > #main > #main > #target > #target`. Auch alleinstehende Bedingungen wie `[@id='x']` (ungültiges XPath) statt `*[@id='x']` in vollständigen XPath-Pfaden wurden korrigiert. Von @sjhddh in [#241](https://github.com/D4Vinci/Scrapling/pull/241)
- **Fehlende Parameter in den Shell-Signaturen wurden ergänzt**. In den Funktionssignaturen der interaktiven Shell fehlten `blocked_domains`, `block_ads`, `retries`, `retry_delay`, `capture_xhr`, `executable_path` und `dns_over_https`.

## [v0.4.5](https://github.com/D4Vinci/Scrapling/releases/tag/v0.4.5) - 2026-04-07 {#v0.4.5}

**Ein Update mit einer großen Erleichterung für Spider-Entwickler und einigen wichtigen Fehlerbehebungen 🎉**

### 🚀 Neuerungen und Verbesserungen der Bedienung {#v0.4.5-new-stuff-and-quality-of-life-changes}

- **Entwicklungsmodus für Spider**: Änderungen an der `parse()`-Logik eines Spiders erforderten bisher bei jedem Lauf neue Zugriffe auf die Zielserver. Das ist langsam, erzeugt unnötigen Verkehr und kann dazu führen, dass der Server Ihre Anfragerate begrenzt, während Sie noch an den Selektoren arbeiten. Der neue Entwicklungsmodus speichert beim ersten Lauf jede Antwort auf der Festplatte und liest sie bei späteren Läufen wieder von dort. So können Sie Ihre Callbacks ändern und beliebig oft neu starten, ohne eine einzige Netzwerkanfrage zu senden. Aktivieren Sie ihn mit einem Klassenattribut:

    ```python
    class MySpider(Spider):
        name = "my_spider"
        start_urls = ["https://example.com"]
        development_mode = True

        async def parse(self, response):
            yield {"title": response.css("title::text").get("")}
    ```

    Der Cache liegt standardmäßig unter `.scrapling_cache/{spider.name}/`. Mit `development_cache_dir` können Sie ihn an einen anderen Ort verlegen. Zwei neue Zähler, `cache_hits` und `cache_misses`, zeigen die Cache-Nutzung. Beim Lesen aus dem Cache werden `download_delay`, Begrenzungen der Anfragerate und erneute Versuche für gesperrte Anfragen übersprungen. So sind die Testläufe so schnell, wie die Festplatte es zulässt. Setzen Sie `development_mode = True` nicht im Produktivbetrieb ein. Das ist ein Entwicklungswerkzeug, kein Produktions-Cache. Alle Einzelheiten stehen in der [Dokumentation](spiders/advanced.md#development-mode).

- **Sicherere Weiterleitungen als Standard**: `follow_redirects` hat jetzt bei allen HTTP-Fetchern, im MCP-Server und in der Shell den Standardwert `"safe"`. Weiterleitungen werden weiterhin verfolgt, aber Ziele mit internen oder privaten IP-Adressen (Loopback, private Netzwerke, Link-Local) werden abgelehnt. Das schützt vor SSRF beim Scraping von URLs, die Benutzer eingeben. Übergeben Sie `follow_redirects="all"` für das bisherige Verhalten oder `False`, um Weiterleitungen ganz abzuschalten.

### 🐛 Fehlerbehebungen {#v0.4.5-bug-fixes}

- **Ein erzwungener Stopp verliert Ihren Checkpoint nicht mehr**: Zweimaliges Drücken von Ctrl+C (erzwungener Stopp) bei einem Spider mit aktiviertem `crawldir` konnte bisher mit dem Schreiben des Checkpoints kollidieren. Der Cancel-Scope beendete die Aufgabe, bevor das Pickle fertig war. Dabei blieb `paused=False` gesetzt und die Bereinigung wurde ausgelöst, die den vorherigen Checkpoint *löscht*. Bei einem langen Crawl konnte so der gesamte Fortschritt verloren gehen, den Sie gerade sichern wollten. Die Engine schreibt den Checkpoint jetzt **vor** dem Aufruf von `cancel_scope.cancel()`. So bleibt bei einem erzwungenen Stopp immer der neueste ausstehende Zustand erhalten. Von @voidborne-d in [#230](https://github.com/D4Vinci/Scrapling/pull/230).

## [v0.4.4](https://github.com/D4Vinci/Scrapling/releases/tag/v0.4.4) - 2026-04-05 {#v0.4.4}

**Ein neues Update mit wichtigen Spider-Verbesserungen und Fehlerbehebungen 🎉**

### 🚀 Neuerungen und Verbesserungen der Bedienung {#v0.4.4-new-stuff-and-quality-of-life-changes}
- **Das Spider-System beachtet jetzt robots.txt** über die neue Option `robots_txt_obey`. Wenn sie aktiviert ist, ruft der Spider robots.txt vor dem Crawl automatisch ab und hält sich an die Regeln, darunter `Disallow`, `Crawl-delay` und `Request-rate`. Die robots.txt-Dateien werden parallel abgerufen und pro Domain für den gesamten Crawl im Cache gespeichert. Von @AbdullahY36 in [#226](https://github.com/D4Vinci/Scrapling/pull/226)
- **Der robots.txt-Cache wird jetzt vorab gefüllt**. Alle robots.txt-Dateien der Domains aus start_urls werden vor Beginn der Crawl-Schleife abgerufen und geparst. So gibt es bei der ersten Anfrage an eine Domain keine zusätzliche Wartezeit.
- **Die neue Statistik `robots_disallowed_count` wurde zu `CrawlStats` hinzugefügt**, um die während eines Crawls durch robots.txt-Regeln blockierten Anfragen zu zählen.

Weitere Informationen finden Sie auf der Website [hier](spiders/getting-started.md#robotstxt-compliance)

### 🐛 Fehlerbehebungen {#v0.4.4-bug-fixes}
- **Ein schwerwiegendes MRO-Problem mit `ProxyRotator` wurde behoben**: Die Platzhaltermethode `_build_context_with_proxy` verdeckte die tatsächliche Implementierung der Unterklassen. Dadurch löste die Proxy-Rotation immer `NotImplementedError` aus (behebt [#215](https://github.com/D4Vinci/Scrapling/issues/215)). Danke, @yetval
- **Ein Leck im Seiten-Pool wurde behoben**, das bei Proxy-Rotation pro Anfrage in Browser-Sitzungen auftrat. Seiten aus temporären Kontexten wurden bei der Bereinigung nicht aus dem Pool entfernt, sodass sich mit der Zeit veraltete Referenzen ansammelten. Von @yetval in [#223](https://github.com/D4Vinci/Scrapling/pull/223)
- **Eine fehlende Typprüfung im statischen Fetcher wurde ergänzt**. `curl_cffi` konnte den Wert `None` aus `session.request()` zurückgeben, was später zu Fehlern führte.

### Weitere Änderungen {#v0.4.4-other}
- Die Abhängigkeiten wurden aktualisiert, einschließlich der neuesten Fingerprints und weiterer Bestandteile.
- `protego` wurde als neue Abhängigkeit in der optionalen Gruppe `fetchers` hinzugefügt, um robots.txt zu parsen.

## [v0.4.3](https://github.com/D4Vinci/Scrapling/releases/tag/v0.4.3) - 2026-03-30 {#v0.4.3}

**Ein neues Update mit vielen wichtigen Änderungen 🎉**

### 🚀 Neuerungen und Verbesserungen der Bedienung {#v0.4.3-new-stuff-and-quality-of-life-changes}
- **Ein neues MCP-Werkzeug wurde hinzugefügt**, um einen dauerhaften normalen oder getarnten Browser zu öffnen und mit den anderen Werkzeugen weiterzuverwenden. Ein weiteres neues Werkzeug schließt ihn. ([Beispiele](https://github.com/D4Vinci/Scrapling/blob/v0.4.3/docs/ai/mcp-server.md#examples))
- **Ein neues MCP-Werkzeug wurde hinzugefügt**, das alle vorhandenen Browser-Sitzungen auflistet. Es ist für die Nutzung mit den neuen Werkzeugen gedacht.
- **Eine neue Option für Browser-Sitzungen wurde hinzugefügt**, die während einer Anfrage automatisch alle Hintergrundanfragen sammelt (löst [#159](https://github.com/D4Vinci/Scrapling/pull/159)) [[Beispiele](https://github.com/D4Vinci/Scrapling/blob/v0.4.3/docs/fetching/dynamic.md#capturing-xhrfetch-requests)].
- **Eine neue Bereinigung wurde hinzugefügt**, um den MCP-Server durch das Entfernen versteckter oder unsichtbarer Inhalte vor üblichen Prompt-Injection-Angriffen zu schützen.
- **Eine neue Kommandozeilenoption namens `--ai-targeted` wurde hinzugefügt**, um die Ausgabe der Web-Scraping-Befehle für KI aufzubereiten und wie beim MCP-Server vor üblichen Prompt-Injection-Angriffen zu schützen.
- **Eine neue Option für Browser-Sitzungen namens `executable_path` wurde hinzugefügt**, um einen eigenen Browser-Pfad anzugeben (löst [#202](https://github.com/D4Vinci/Scrapling/pull/202))
- **Der Code des MCP-Servers wurde umstrukturiert**, um die Wartung zu vereinfachen. Alle Werkzeuge arbeiten jetzt asynchron.
- **Der Code der CLI-Befehle wurde umstrukturiert**, um die Wartung zu vereinfachen und ihn um 210 Zeilen zu kürzen.

### 🐛 Fehlerbehebungen {#v0.4.3-bug-fixes}
- Korrektur zur Beibehaltung der HTTP-Methode bei erneuten Versuchen in einer Spider-Sitzung, von @karesansui-u in [#201](https://github.com/D4Vinci/Scrapling/pull/201)
- Eine Höchstzahl für erneute Versuche zum Abrufen des Seiteninhalts wurde hinzugefügt, um Endlosschleifen zu vermeiden, von @haosenwang1018 und @D4Vinci in [#197](https://github.com/D4Vinci/Scrapling/pull/197)
- Ein alleinstehendes `raise` wurde durch `return False` in `_restore_from_checkpoint` ersetzt, von @haosenwang1018 in [#196](https://github.com/D4Vinci/Scrapling/pull/196)
- `get_all` wurde durch `getall` in `Texthandler` ersetzt, um zur Klasse Selector zu passen.

### Verbesserungen der Tests und Testabdeckung {#v0.4.3-coverage-tests-improvement}
- Tests für Randfälle von `_normalize_credentials` wurden hinzugefügt, von @Bortlesboat in [#192](https://github.com/D4Vinci/Scrapling/pull/192)
- Tests für das Speichern und anschließende Abrufen sowie für die grundlegende Speicherung wurden hinzugefügt, von @haosenwang1018 in [#193](https://github.com/D4Vinci/Scrapling/pull/193)
- Testabdeckung für die Regex-Pfade von `TextHandler` und `TextHandlers.re()` wurde hinzugefügt, von @haosenwang1018 in [#194](https://github.com/D4Vinci/Scrapling/pull/194)
- Tests für Randfälle von `filter`, `iterancestors` und `find_similar` wurden hinzugefügt, von @awanawana in [#200](https://github.com/D4Vinci/Scrapling/pull/200)

### Verbesserungen am Agent Skill {#v0.4.3-agent-skill-improvement}
- Defekte Markdown-Links in den Skill-Referenzen wurden korrigiert, von @yetval in [#204](https://github.com/D4Vinci/Scrapling/pull/204)
- Die Struktur des Skills wurde verbessert, damit sie die Prüfung von [Clawhub](https://clawhub.ai/d4vinci/scrapling-official) besser erfüllt.
- Der Skill muss jetzt beim Scraping über die Kommandozeile die Option `--ai-targeted` verwenden.

### Verbesserungen der Dokumentation {#v0.4.3-docs-improvement}
- Eine koreanische README-Übersetzung wurde hinzugefügt, von @greatsk55 in [#187](https://github.com/D4Vinci/Scrapling/pull/187)
- Abstände zwischen CJK- und lateinischen Zeichen in den chinesischen und japanischen READMEs wurden korrigiert.
- Defekte Links aus dem alten Website-Design wurden korrigiert.

## [v0.4.2](https://github.com/D4Vinci/Scrapling/releases/tag/v0.4.2) - 2026-03-08 {#v0.4.2}

**Ein neues Wartungsupdate mit wichtigen Änderungen**

#### Fehlerbehebungen {#v0.4.2-bug-fixes}
- Die Funktion `get_all_text()` erfasst jetzt auch Textknoten, die auf Elemente folgen. Dadurch können der MCP-Server und die Befehle Text lesen, der zuvor fehlte ([#168](https://github.com/D4Vinci/Scrapling/pull/168)). Danke @mhillebrand
- Referer gibt jetzt die einfache Google-URL statt einer Google-Such-URL zurück. Die bisherige Logik war falsch und konnte ein Merkmal zur Erkennung des Browser-Fingerabdrucks erzeugen ([#179](https://github.com/D4Vinci/Scrapling/pull/179)). Danke @Bortlesboat
- Ein Problem beim Zusammenfügen zusätzlicher Startoptionen wurde in allen Browsern behoben. Danke @rostchri
- Ein Problem mit Typannotationen wurde behoben, das bei Python-Versionen vor 3.12 zu Abstürzen führte. (Behebt [#163](https://github.com/D4Vinci/Scrapling/issues/163))

#### Sonstige Änderungen {#v0.4.2-other}
- Ein Agent Skill für Claude Code / OpenClaw und andere Werkzeuge für KI-Agenten wurde hinzugefügt.
- Der Agent Skill wurde zu Clawhub hinzugefügt.
- Alle Browser und Playwright wurden auf die neuesten Versionen aktualisiert.
- Eine französische Übersetzung der Haupt-README wurde hinzugefügt.

## [v0.4.1](https://github.com/D4Vinci/Scrapling/releases/tag/v0.4.1) - 2026-02-27 {#v0.4.1}

**Ein neues Update mit vielen wichtigen Änderungen**

### 🚀 Neuerungen und Verbesserungen der Bedienung {#v0.4.1-new-stuff-and-quality-of-life-changes}
- **Genauere reguläre Ausdrücke** zur Erkennung von Cloudflare-Challenges (Danke an @Rinz27 [#133](https://github.com/D4Vinci/Scrapling/pull/133))
- **Schnellere und effizientere Lösung** von Cloudflare-Challenges. Sie ist jetzt fast doppelt so schnell.
- **Verbesserte Lösung von Cloudflare-Challenges** für Websites, die manchmal zweimal die Cloudflare-Seite anzeigen, bevor sie zur eigentlichen Website weiterleiten.
- **Bessere Tarnung und höhere Geschwindigkeit des getarnten Browsers** durch das Entfernen der injizierten JS-Dateien.
- **Verbessertes MCP-Schema**, das von OpenCode akzeptiert wird (Danke an @robin-ede [#137](https://github.com/D4Vinci/Scrapling/pull/137))
- **Noch bessere Übereinstimmung des MCP-Schemas mit dem Protokoll**, damit VS Code Copilot und andere streng prüfende Werkzeuge es akzeptieren. (Behebt #150 )
- **Deutlich geringerer Token-Verbrauch des MCP-Servers**, weil unnötige HTML-Tags bei aktivierter Option `main_content_only` entfernt werden.
- Die PyPI-Seite wurde korrigiert. Dateien zur Registrierung des MCP-Servers im MCP-Serververzeichnis wurden hinzugefügt.
- Ein neues Codebeispiel zeigt, wie Sie die Browser-Abhängigkeiten per Code statt über die Kommandozeile installieren, um die Automatisierung zu erleichtern.
- Alle Workflows wurden durch die Verwendung der neuesten Action-Versionen verbessert (Danke an @salmanmkc [#143](https://github.com/D4Vinci/Scrapling/pull/143)/[#144](https://github.com/D4Vinci/Scrapling/pull/144))

## [v0.4](https://github.com/D4Vinci/Scrapling/releases/tag/v0.4) - 2026-02-15 {#v0.4}

**Die bisher größte Scrapling-Version: Spider-Framework, Proxy-Rotation und große Verbesserungen am Parser**

Diese Version bringt ein vollständig asynchrones Spider- und Crawling-Framework, intelligente Proxy-Verwaltung und wichtige API-Änderungen, die Scrapling leistungsfähiger und einheitlicher machen. Lesen Sie vor dem Update den Abschnitt zu inkompatiblen Änderungen sorgfältig durch.

### 🕷️ Spider-Framework {#v0.4-spider-framework}

Ein neues asynchrones Crawling-Framework auf Basis von `anyio` für strukturiertes Scraping in großem Umfang:

```python
from scrapling.spiders import Spider, Response

class MySpider(Spider):
  name = "demo"
  start_urls = ["https://example.com/"]

  async def parse(self, response: Response):
      for item in response.css('.product'):
          yield {"title": item.css('h2::text').get()}

MySpider().start()
```

-  **Spider-API ähnlich wie in Scrapy**: Definieren Sie Spider mit `start_urls`, asynchronen `parse`-Callbacks, `Request`/`Response`-Objekten und einer Prioritätswarteschlange.
- **Gleichzeitiges Crawling**: Einstellbare Grenzen für gleichzeitige Anfragen, Drosselung je Domain und Wartezeiten zwischen Downloads.
- **Unterstützung mehrerer Sitzungen**: Einheitliche Schnittstelle für HTTP-Anfragen und getarnte Browser ohne sichtbares Fenster in einem Spider. Leiten Sie Anfragen anhand der ID an verschiedene Sitzungen weiter. Sitzungen lassen sich bei Bedarf starten.
- **Pausieren und Fortsetzen**: Der Zustand des Crawls wird mit Checkpoints gespeichert. Drücken Sie Ctrl+C für ein geordnetes Beenden und starten Sie dann erneut, um an derselben Stelle fortzufahren.
- **Streaming-Modus**: Empfangen Sie extrahierte Einträge sofort über `async for item in spider.stream()`, mit Statistiken in Echtzeit. Ideal für Benutzeroberflächen, Pipelines und lange Crawls.
- **Erkennung blockierter Anfragen**: Blockierte Anfragen werden automatisch erkannt und wiederholt. Die Logik ist anpassbar.
- **Integrierter Export**: Exportieren Sie Ergebnisse über Hooks und Ihre eigene Pipeline oder nutzen Sie den integrierten JSON/JSONL-Export mit `result.items.to_json()` bzw. `result.items.to_jsonl()`.
- **Hooks für den Lebenszyklus**: `on_start()`, `on_close()`, `on_error()`, `on_scraped_item()` und weitere Hooks bieten volle Kontrolle über den Ablauf des Crawls.
- **Detaillierte Crawl-Statistiken**: Verfolgen Sie Anfragen, Antworten, Bytes, Statuscodes, Proxys, Details je Domain und Sitzung, die Anzahl der Logmeldungen je Stufe und mehr.
- **uvloop-Unterstützung**: Übergeben Sie `use_uvloop=True` an `spider.start()`, um die asynchrone Ausführung zu beschleunigen, wenn uvloop verfügbar ist.

Ein neuer Abschnitt auf der Website enthält alle Details. Klicken Sie [hier](spiders/architecture.md)

### 🔄 Proxy-Rotation {#v0.4-proxy-rotation}

* Neue Klasse `ProxyRotator` mit threadsicherer Rotation. Sie funktioniert mit allen Fetchern und Sitzungen:

  ```python
  from scrapling import ProxyRotator
  rotator = ProxyRotator(["http://proxy1:8080", "http://proxy2:8080"])
  Fetcher.get(url, proxy_rotator=rotator)
  ```

* **Eigene Rotationsstrategien**: Erstellen Sie Ihre eigene Logik zur Proxy-Rotation
* **Proxy je Anfrage ersetzen**: Übergeben Sie `proxy=` an einen einzelnen Aufruf von `get()`/`post()`/`fetch()`, um für diese Anfrage einen anderen Proxy als den der Sitzung zu verwenden.

### 🌐 Verbesserungen an Browser-Fetchern {#v0.4-browser-fetcher-improvements}

* **Domains blockieren**: Neuer Parameter `blocked_domains` in `DynamicFetcher`/`StealthyFetcher`, um Anfragen an bestimmte Domains zu blockieren. Subdomains werden automatisch einbezogen.
* **Automatische Wiederholungen**: Browser-Fetcher wiederholen fehlgeschlagene Anfragen jetzt mit den Parametern `retries` (Standard: 3) und `retry_delay` (Standard: 1s). Dazu gehört die Erkennung von Proxy-Fehlern.
* **Antwortmetadaten**: Das Dictionary `Response.meta` speichert automatisch den verwendeten Proxy und übernimmt die Metadaten der Anfrage.
* **Response.follow()**: Erstellen Sie `Request`-Objekte für Folgeanfragen mit automatischer Referer-Verwaltung. Diese Funktion ist für das Spider-System vorgesehen.
* **Keine automatische Wiedergabe**: Browser-Sitzungen blockieren jetzt automatisch abgespielte Inhalte, die zuvor Probleme verursacht haben.
* **Geschwindigkeit**: Bessere Tarnung und höhere Geschwindigkeit durch angepasste Browser-Startoptionen.

### 🔧 Fehlerbehebungen und Verbesserungen {#v0.4-bug-fixes-improvements}
- **Parser-Optimierung**: Der Parser wurde für wiederholte Vorgänge optimiert, um die Leistung zu verbessern.
- **Fehlerhafte Seiten**: Ein Fehler wurde behoben, durch den der Browser bei Seitenfehlern nicht geschlossen wurde.
- **Leerer Inhalt**: Antworten mit leerem Body werden verarbeitet.
- **Playwright-Schleife**: Ein Problem wurde behoben, bei dem die Playwright-Schleife nach einer fehlgeschlagenen CDP-Verbindung offen blieb
- **Typsicherheit**: Alle mypy-Fehler wurden behoben. Typannotationen wurden in bisher untypisierten Funktionskörpern ergänzt. mypy und pyright wurden zum CI-Workflow hinzugefügt.

### ⚠️ Inkompatible Änderungen {#v0.4-breaking-changes}

* **`css_first`/`xpath_first` entfernt**: Verwenden Sie stattdessen `css('.selector').first`, `css('.selector')[0]` oder `css('.selector').get()`.
* **Alle Auswahlmethoden geben jetzt `Selectors` zurück**: `css('::text')`, `xpath('//text()')`, `css('::attr(href)')` und `xpath('//@href')` geben jetzt `Selectors` zurück, wobei Textknoten in `Selector`-Objekte mit `tag="#text"` eingebettet werden. Zuvor wurde `TextHandlers` zurückgegeben. Das vereinheitlicht die API über alle Auswahlmethoden und Typannotationen hinweg.
* **`Response.body` ist immer `bytes`**: Zuvor konnte der Wert `str` oder `bytes` sein. Jetzt wird immer `bytes` zurückgegeben.
* **Verhalten von `get()`/`getall()`**: Bei `Selector` gibt `get()` ein `TextHandler`-Objekt zurück, also serialisiertes HTML oder einen Textwert. `getall()` gibt `TextHandlers` zurück. Aliase: `extract_first = get`, `extract = getall`. Das alte `get_all()` von `Selectors` wurde entfernt.
* **`Selectors.first`/`.last`**: Sicherer Zugriff, der `Selector | None` zurückgibt, statt `IndexError` auszulösen.
* **Interne Konstanten umbenannt**: `DEFAULT_FLAGS` → `DEFAULT_ARGS`, `DEFAULT_STEALTH_FLAGS` → `STEALTH_ARGS`, `HARMFUL_DEFAULT_ARGS` → `HARMFUL_ARGS`, `DEFAULT_DISABLED_RESOURCES` → `EXTRA_RESOURCES`.

### 🔨 Sonstige Änderungen {#v0.4-other-changes}

* **Geänderte Abhängigkeiten**: `tldextract` wurde durch `tld` ersetzt. Die interne Datei `_html_utils.py` wurde zugunsten von `w3lib.html.replace_entities` entfernt. `typing_extensions` ist jetzt zwingend erforderlich.
* **Überarbeitete Dokumentation**: Vollständiger Wechsel von MkDocs zu Zensical, ein neuer Abschnitt zur Spider-Dokumentation, aktualisierte bestehende Seiten und neue API-Referenzen.

## [v0.3.14](https://github.com/D4Vinci/Scrapling/releases/tag/v0.3.14) - 2026-01-03 {#v0.3.14}

**Ein kleines Wartungsupdate für Probleme, die mit v0.3.13 auf einigen Geräten aufgetreten sind**

- Der Inkognitomodus wurde in `StealthyFetcher` und seinen Sitzungsklassen deaktiviert, weil Cookies unter Windows dadurch nicht über mehrere Seiten hinweg erhalten blieben. Unter MacOS und Linux trat das nicht auf (Behebt [#123](https://github.com/D4Vinci/Scrapling/issues/123); danke an @frugality4121 für den Hinweis und an @gembleman für die Lösung).
- Die neueste browserforge-Version wurde fest vorgegeben, um Probleme mit alten Header-Modellen bei Benutzern zu lösen, die bereits eine alte browserforge-Version installiert hatten.

## [v0.3.13](https://github.com/D4Vinci/Scrapling/releases/tag/v0.3.13) - 2026-01-01 {#v0.3.13}

**Ein großes Update mit vielen Verbesserungen in vielen Bereichen, aber auch mit zahlreichen begründeten inkompatiblen Änderungen. Lesen Sie die folgenden Hinweise vor dem Update**

* Aus mehreren Gründen verwenden wir Camoufox ab jetzt nicht mehr. Falls die Entwicklung fortgesetzt wird, könnten wir in Zukunft darauf zurückkommen. Wenn Sie Camoufox wie vor dieser Version weiterverwenden möchten, finden Sie in diesem [Abschnitt](https://github.com/D4Vinci/Scrapling/blob/v0.3.13/docs/fetching/stealthy.md#using-camoufox-as-an-engine) eine Anleitung.

* Bisher haben wir patchright im Tarnmodus von `DynamicFetcher` und seinen Sitzungsklassen verwendet. Dieser Modus wurde dort entfernt. Stattdessen verwenden wir patchright jetzt in `StealthyFetcher` und seinen Sitzungsklassen, mit SEHR VIELEN Verbesserungen, wie Sie sehen werden. Sie verbessern die Tarnung zusätzlich zu den Funktionen von patchright.

**Dadurch sind `StealthyFetcher` und seine Sitzungsklassen 101 % schneller, benötigen weniger Arbeitsspeicher und Speicherplatz und haben etwa ~400 Codezeilen weniger. Vor allem sind sie stabiler als bei der früheren Verwendung von Camoufox.**

Das verkürzt auch die Installation mit `scrapling install`, verkleinert das Docker-Image, verbessert den Ablauf der Tests in der GitHub-CI und macht scrapling für neue Benutzer verständlicher.

### Inkompatible Änderungen {#v0.3.13-breaking-changes}
1. Das Argument `stealth` wurde aus `DynamicFetcher` und seiner Sitzungsklasse entfernt. `hide_canvas` wurde nach `StealthyFetcher` und in dessen Sitzungsklassen verschoben.
2.  Das Argument `disable_webgl` wurde von `DynamicFetcher` in die Klasse `StealthyFetcher` verschoben und in `allow_webgl` umbenannt. Das gilt auch für alle Sitzungsklassen.
3. Die Klasse `StealthyFetcher` ist jetzt im Wesentlichen die neue getarnte Version von `DynamicFetcher`. Daher wurden diese Argumente entfernt: `block_images`, `humanize`, `addons`, `os_randomize`, `disable_ads` und `geoip`. Ich habe versucht, sie in Chromium nachzubilden, aber jedes davon hatte ein eigenes Problem. Das könnte sich in kommenden Versionen vor v0.4 ändern.

Nun zu den guten Nachrichten: Wir haben vieles verbessert und behoben :)

### Verbesserungen {#v0.3.13-improvements}
- Sie wissen bereits, dass `StealthyFetcher` und seine Sitzungsklassen jetzt 101 % schneller sind. Auch `DynamicFetcher` und seine Sitzungsklasse sind jetzt 20 % schneller.
- Der Algorithmus zum Lösen von Cloudflare-Challenges wurde verbessert, um schneller fertig zu werden und mehr Fälle abzudecken. Dank der überarbeiteten Struktur können Sie außerdem eine doppelt so schnelle Captcha-Lösung erwarten!
- Alle Fetcher benötigen jetzt weniger Arbeitsspeicher.
- Der MCP-Server verbraucht weniger Tokens und spart dadurch mehr Geld!
- Das Docker-Image ist jetzt 60 % kleiner.
- Die gesamte Dokumentationswebsite wurde um die neuen Funktionen ergänzt. Gleichzeitig wurden Erklärungen verständlicher, viele Abschnitte kürzer und weitere Beispiele sowie fehlende Argumente ergänzt. Die API-Referenz erhielt Diagramme, dazu kamen viele weitere Verbesserungen. Die Website lädt jetzt 130 % schneller, verbraucht weniger Daten und ist besser für SEO geeignet.

### Fehlerbehebungen {#v0.3.13-fixes}
- Fehlende Argumente wurden in den Kurzbefehlen der Web-Scraping-Shell ergänzt. Die Kurzbefehle wurden außerdem genauer gemacht.
- Ein Problem wurde behoben, bei dem `google_search` auch für localhost- oder IP-URLs einen Google-Referer erzeugte.

## [v0.3.12](https://github.com/D4Vinci/Scrapling/releases/tag/v0.3.12) - 2025-12-18 {#v0.3.12}

### Was sich geändert hat {#v0.3.12-what-s-changed}
- Die Klassen `DynamicSession`/`AsyncDynamicSession` haben ein neues Argument namens `timezone_id`. Damit können Sie die Zeitzone des Browsers an die des verwendeten Proxys oder VPNs anpassen. Websites können den Proxy dann nicht anhand unterschiedlicher Zeitzonen erkennen.
- Die automatische Umwandlung von Antworten in JSON wurde verbessert.
- Die interne Funktion `__create__` wurde in den Sitzungsklassen der Fetcher in `start` umbenannt, um die Verwendung außerhalb des `with`-Kontexts zu erleichtern.
- `curl_cffi` und weitere Abhängigkeiten wurden auf die neuesten Versionen aktualisiert.

## [v0.3.11](https://github.com/D4Vinci/Scrapling/releases/tag/v0.3.11) - 2025-12-03 {#v0.3.11}

### Was sich geändert hat {#v0.3.11-what-s-changed}
- Die Behandlung von Zeitüberschreitungen wurde verbessert, wenn `network_idle` auf instabilen Websites verwendet wird, etwa auf Seiten mit laufender Medienwiedergabe.
- Die Autovervollständigung für den Kurzbefehl `stealthy_fetch` in der Web-Scraping-Shell wurde korrigiert

## [v0.3.10](https://github.com/D4Vinci/Scrapling/releases/tag/v0.3.10) - 2025-11-26 {#v0.3.10}

**Ein Wartungsupdate mit vielen wichtigen und möglicherweise inkompatiblen Änderungen**

- **Alle Kodierungsprobleme behoben** durch einen besseren Ansatz, der Webseiten mit falsch deklarierter Kodierung verarbeitet (Danke an @Kemsty2 für den Einsatz und die Hinweise in [#110](https://github.com/D4Vinci/Scrapling/issues/110) [#111](https://github.com/D4Vinci/Scrapling/pull/111) )
- **Ein Logikproblem behoben**, das seit v0.3 beim Überschreiben von Sitzungsparametern durch Anfrageparameter in allen Browser-Fetchern bestand
- **Die Signaturen der Kurzbefehle korrigiert** in der interaktiven Web-Scraping-Shell. Dadurch funktioniert ihre Autovervollständigung vollständig. Auch dieses Problem bestand seit v0.3.
- **Die Maxmind-Datenbank aktualisiert**, was das Argument `geoip` von `StealthyFetcher` und seinen Sitzungsklassen verbessert.
- **Alle verwendeten Browser aktualisiert** auf die neuesten verfügbaren Versionen.
- **INKOMPATIBLE ÄNDERUNGEN**: Alle Fetcher wurden umfassend überarbeitet. Daraus ergeben sich einige interessante Änderungen, die Ihren Code beeinträchtigen könnten:
    1. Der Code von Scrapling ist jetzt etwa ~750 Zeilen kürzer. Viele Änderungen erleichtern die künftige Wartung und verringern den Ressourcenverbrauch etwas.
    2. Die Validierung aller Fetcher und ihrer Sitzungsklassen ist deutlich schneller, was auch ihre Gesamtgeschwindigkeit verbessert.
    3. Dafür akzeptieren die Fetcher keine Positionsargumente außer `url` mehr. Alle übrigen Argumente müssen mit ihrem Namen übergeben werden. Verwenden Sie also `Fetcher.get('https://google.com', stealthy_headers=True)` statt `Fetcher.get('https://google.com', True)`, falls Sie das aus irgendeinem Grund bisher so gemacht haben!
    4. Seit v0.3 gab es einen störenden Unterschied zwischen Browser-Fetchern und ihren Sitzungsklassen: Das Argument für Parser-Einstellungen je Anfrage hieß `custom_config`, in den Sitzungsklassen dagegen `selector_config`. Durch die Überarbeitung konnten wir den Namen zu `selector_config` vereinheitlichen, ohne Ihren Code zu beschädigen. Der Hauptname ist jetzt `selector_config`, das alte Argument `custom_config` bleibt aus Kompatibilitätsgründen unterstützt. Autovervollständigung gibt es nur für `selector_config`.
    5. Dafür mussten auch die Typannotationen der Fetcher-Funktionen dynamisch erzeugt werden. Falls die Autovervollständigung in Ihrer IDE nicht richtig funktioniert, stellen Sie sicher, dass Sie eine aktuelle Version verwenden. Wir haben fast alle bekannten IDEs und Editoren getestet.

> Wir haben auch alle Benchmark-Tabellen mit den aktuellen Zahlen im Vergleich zu den neuesten Versionen aller alternativen Bibliotheken aktualisiert.

## [v0.3.9](https://github.com/D4Vinci/Scrapling/releases/tag/v0.3.9) - 2025-11-17 {#v0.3.9}

**Ein neues Update mit vielen wichtigen Änderungen**

### 🚀 Neuerungen und Verbesserungen der Bedienung {#v0.3.9-new-stuff-and-quality-of-life-changes}
- Das Argument `impersonate` in `Fetcher` und `FetcherSession` akzeptiert jetzt eine Browser-Liste. Die Bibliothek wählt daraus bei jeder Anfrage zufällig einen Browser aus.

```python
from scrapling.fetchers import FetcherSession

with FetcherSession(impersonate=['chrome', 'firefox', 'safari']) as s:
  s.get('https://github.com/D4Vinci/Scrapling')
```

- Ein neues Argument der Methode `clean` in `TextHandler` entfernt HTML-Entitäten einfach aus dem aktuellen Text.
- Große Verbesserungen an der Dokumentation mit genaueren Erklärungen vieler Bereiche und automatischen Übersetzungen der Hauptdatei `README.md`.

### 🐛 Fehlerbehebungen {#v0.3.9-bug-fixes}
- Ein großes Problem beim Abrufen von Antworten mit Browser-Fetchern wurde behoben. Eine intelligente Erkennung des Inhaltstyps stellt jetzt sicher, dass `response.body` nur bei HTML den vom Browser gerenderten Inhalt enthält. Andernfalls enthält es den Rohinhalt der letzten Anfrage. So können Sie Binär- und Textdateien herunterladen, ohne dass sie in HTML-Tags verpackt werden. Gleichzeitig können Sie weiterhin den gerenderten Inhalt einer Website abrufen, wenn Sie ihn benötigen.

### 🔨 Sonstige Änderungen {#v0.3.9-misc}
- Der Leitfaden für Beiträge wurde verständlicher und einfacher gestaltet.
- Ein neuer Workflow erzwingt die Verwendung der Werkzeuge zur Codequalität. Es sind dieselben wie bei den Pre-commit-Hooks.

## [v0.3.8](https://github.com/D4Vinci/Scrapling/releases/tag/v0.3.8) - 2025-10-27 {#v0.3.8}

**Ein neues Update mit vielen wichtigen Änderungen**

### 🚀 Neuerungen und Verbesserungen der Bedienung {#v0.3.8-new-stuff-and-quality-of-life-changes}
- Bei allen Browser-Fetchern führen Websites, deren Anfragen nie fertig laden, mit `network_idle` nicht mehr zum Absturz des Codes.
- Die Logik zum Sammeln und Prüfen von Seiteninhalten in Browser-Fetchern wurde geändert, damit Browser unter Windows so stabil wie unter Linux/MacOS laufen. Dieser Verhaltensunterschied liegt an der anderen Implementierung von Playwright unter Windows.
- Die gesamte Validierungslogik wurde überarbeitet, wodurch Anfragen aller Browser-Fetcher 8-15 % schneller sind
- Die neue Option `extra_flags` in `DynamicFetcher` und seiner Sitzung erlaubt zusätzliche eigene Chrome-Startoptionen neben den bestehenden Optionen.
- Beim Einsatz von `page_action` wird wieder die alte Routing-Logik zur Erfassung von Antworten verwendet, die in der letzten Version geändert worden war. So lässt sich der neueste Seiteninhalt erfassen, wenn `page_action` ihn ohne neue Anfrage verändert. (Danke an @gembleman für den Hinweis in [#100](https://github.com/D4Vinci/Scrapling/issues/100) und [#102](https://github.com/D4Vinci/Scrapling/pull/102) )

### 🐛 Fehlerbehebungen {#v0.3.8-bug-fixes}
- Ein Tippfehler in `load_dom` in der Methode async_fetch von DynamicSession wurde korrigiert
- Ein Problem beim Lösen von Cloudflare-Challenges wurde behoben: Bei eingebetteten Captchas, die nach dem Lösen sichtbar bleiben, wurde endlos auf ihr Verschwinden gewartet. Nach 30 Sekunden wird nun angenommen, dass es sich um diesen Captcha-Typ handelt (Behebt #100 )

### 🔨 Sonstige Änderungen {#v0.3.8-misc}
- Das Docker-Image wird jetzt zur einfacheren Nutzung automatisch auf Dockerhub und in der Container-Registry von GitHub veröffentlicht.
- Eine [neue Dokumentationsseite](https://github.com/D4Vinci/Scrapling/blob/v0.3.8/docs/tutorials/external.md) zeigt, wie Sie den Scrapeless-Browser mit Scrapling verwenden.

## [v0.3.7](https://github.com/D4Vinci/Scrapling/releases/tag/v0.3.7) - 2025-10-12 {#v0.3.7}

**Ein neues Update mit vielen wichtigen Änderungen**

### 🚀 Neuerungen und Verbesserungen der Bedienung {#v0.3.7-new-stuff-and-quality-of-life-changes}
- Das Argument `solve_cloudflare` in `StealthyFetcher` wurde überarbeitet, um alle Arten eigener Turnstile-Implementierungen lösen zu können.
- Der gesamte Code wurde überarbeitet, um die Prüfungen von Pyright zu bestehen. Das verbessert die Arbeit in allen IDEs und behebt viele Fehler.
- Die Anfragelogik wurde übersichtlicher und schneller gestaltet (Behebt auch #97 )
- Die neue Option `user_data_dir` in allen Browser-Sitzungsklassen ermöglicht es, Browserdaten aus früheren Sitzungen wiederzuverwenden, etwa Cookies und gespeicherte Daten. Ohne diese Option verwendet Playwright bei jedem Start wie bisher ein zufälliges Verzeichnis.
- Die neue Anpassungsoption `additional_args` in `Dynamic fetcher` und seiner Sitzungsklasse erlaubt zusätzliche Argumente für den Playwright-Kontext. Das war zuvor bereits mit `StealthyFetcher` möglich.
- Die Routing-Logik zur Erfassung der letzten Navigationsantwort wurde für alle Browser verbessert. Rohe Antworten können jetzt an den Parser gehen, bevor der Browser sie verarbeitet, statt wie bisher zuerst im Browser verarbeitet zu werden. Das ist besonders für Text- und JSON-Antworten hilfreich.

### 🐛 Fehlerbehebungen {#v0.3.7-bug-fixes}
- Die überarbeitete Routing-Logik behebt ein Problem beim Abrufen instabiler Websites auf einigen Windows-Geräten.
- Die Überarbeitungen dieser Version beheben viele zuvor schwer erkennbare Fehler sowie ungewöhnliche Probleme mit der Autovervollständigung in einigen IDEs.
- Viele Korrekturen an der Dokumentationswebsite

## [v0.3.6](https://github.com/D4Vinci/Scrapling/releases/tag/v0.3.6) - 2025-10-01 {#v0.3.6}

### 🚀 Neuerungen {#v0.3.6-new-stuff}
- Das Argument `solve_cloudflare` in `StealthyFetcher` und seinen Sitzungsklassen wurde verbessert, um alle Arten von Turnstile- und Cloudflare-Zwischenseiten-Challenges zu lösen 🎉
- Der MCP-Server kann jetzt `Streamable HTTP` verwenden, damit Sie ihn einfach über das Netzwerk bereitstellen können.
- Docker-Unterstützung wurde hinzugefügt. Bei jeder Veröffentlichung wird automatisch ein Image mit allen Browsern erstellt und auf Docker Hub veröffentlicht

### 🐛 Fehlerbehebungen {#v0.3.6-bug-fixes}
- Ein Kodierungsproblem im Parser wurde behoben, das in einigen Fällen auftrat: der bekannte Fehler `invalid start byte`
- Mehrere Teile der Bibliothek wurden umstrukturiert, um Speicherlecks zu beheben. Je nach Konfiguration wird jetzt deutlich weniger Speicher benötigt (Behebt auch #92 )
- Typannotationen wurden in vielen Teilen des Codes verbessert, um die Arbeit in der IDE zu erleichtern (Behebt auch #93 )

## [v0.3.5](https://github.com/D4Vinci/Scrapling/releases/tag/v0.3.5) - 2025-09-20 {#v0.3.5}

**Eine notwendige Version, die mehrere Probleme behebt**

### 🚀 Neuerungen {#v0.3.5-new-stuff}
- Alle Browser-Fetcher (`DynamicFetcher`/`StealthyFetcher`/...) und ihre Sitzungsklassen rufen Websites jetzt 15-20 % schneller ab:
    1. Die Seitenverwaltung ist dank der verbesserten Logik von @AbdullahY36 in #87 deutlich schneller
    2. Die allgemeine Validierungslogik und die Erstellung von Seiten für synchrone Abrufe wurden optimiert. Zusammen bringen diese Änderungen große Geschwindigkeitsgewinne

- Große Verbesserungen am Tarnmodus von `DynamicFetcher` und seinen Sitzungsklassen durch den Ersatz von `rebrowser-playwright` durch `PatchRight`:
    1. Vor diesem Update wurde `rebrowser-playwright` deaktiviert, wenn Sie `stealth` und `real_chrome` aktivierten, weil beide nicht gut zusammenarbeiteten. Mit `PatchRight` besteht dieses Problem nicht mehr
    2. Sie können jetzt mit geschlossenen Shadow Roots interagieren, da `PatchRight` automatisch mit ihnen umgehen kann.

### 🐛 Fehlerbehebungen {#v0.3.5-bug-fixes}
- Ein Fehler bei der Verwendung der Methode `re` aus der Klasse `Selectors` wurde behoben.
- Ein Fehler in den Befehlen `uncurl` und `curl2fetcher` der Web-Scraping-Shell wurde behoben, durch den die curl-Option `--data-raw` falsch verarbeitet wurde.
- Ein Fehler im Befehl `view` der Web-Scraping-Shell wurde behoben, dessen Auftreten von der Kodierung der Website abhing.
- Ein Fehler bei der Inhaltskonvertierung wurde behoben, der den Modus `mcp` und die Befehle `extract` betraf.

### Neue Mitwirkende {#v0.3.5-new-contributors}
- @AbdullahY36 hat mit #87 erstmals beigetragen

## [v0.3.4](https://github.com/D4Vinci/Scrapling/releases/tag/v0.3.4) - 2025-09-16 {#v0.3.4}

**Eine notwendige Version, die mehrere Probleme behebt**

### 🚀 Neuerungen {#v0.3.4-new-stuff}
- Alle Sitzungsklassen der Fetcher wurden zur interaktiven Shell hinzugefügt und sind dort ohne Import sofort verfügbar.

### 🐛 Fehlerbehebungen {#v0.3.4-bug-fixes}
- Eine Umgehung für einen Fehler in der Playwright-API unter Windows wurde hinzugefügt, der beim Abrufen von Inhalten während der Lösung von Cloudflare-Challenges auftrat.
- Ein Kodierungsproblem im Befehl `view` der interaktiven Shell wurde behoben
- Ein Fehler im Argument `max_pages` von `AsyncStealthySession` wurde behoben, der den Code abstürzen ließ.
- Ein Problem der letzten Updates wurde behoben, bei dem die Eigenschaften `html_content` und `prettify` von `Selector` abhängig von der Kodierung Bytes zurückgaben. Beide geben wieder Strings zurück.

## [v0.3.3](https://github.com/D4Vinci/Scrapling/releases/tag/v0.3.3) - 2025-09-15 {#v0.3.3}

- Die Logik zum Schließen des Standardtabs in Browser-Fetchern wurde entfernt, da sie einen Absturz auslöste. Das trat nicht auf dem Mac auf und konnte nur unter Windows und Linux reproduziert werden

## [v0.3.2](https://github.com/D4Vinci/Scrapling/releases/tag/v0.3.2) - 2025-09-15 {#v0.3.2}

Versionshinweise für v0.3.2

### 🚀 Neuerungen {#v0.3.2-new-stuff}

- **Optionale Fetcher-Abhängigkeiten**: Alle Fetcher gehören jetzt zu optionalen Abhängigkeitsgruppen. Das verkleinert das Basispaket. Das Basismodul `scrapling` enthält nur noch den Parser. Für Fetcher oder Kommandozeilenoptionen führen Sie `pip install "scrapling[fetchers]"` aus. Die ausführliche Installationsanleitung finden Sie [hier](index.md#installation)
- **Konfiguration je Seite in Sitzungen**: Die Sitzungsklassen der Browser-Fetcher erlauben jetzt getrennte Einstellungen für jede Seite. Alle Parameter für einzelne Abrufe werden wie Sitzungsparameter validiert. Weitere Details stehen [hier](fetching/stealthy.md#full-list-of-arguments) auf der Dokumentationswebsite
    <br>Beispiel:

    ```python
    with StealthySession(headless=True, solve_cloudflare=True) as session:
        page = session.fetch('https://nopecha.com/demo/cloudflare', google_search=False)
    ```

- **Verbesserte Browser-Fetcher**
    - Eine neue Option steuert, ob auf das Ende der JavaScript-Ausführung auf einer Seite gewartet wird. Sie ist wie bisher standardmäßig aktiviert

        ```python
        with DynamicSession(headless=True, disable_resources=False, network_idle=True) as session:
           page = session.fetch('https://quotes.toscrape.com/', load_dom=False)
        ```

    - Der Tarnmodus in `DynamicFetcher` und seinen Sitzungsklassen ist jetzt zuverlässiger.
    - `DynamicFetcher` und `StealthyFetcher` benötigen weniger Ressourcen, indem sie den von persistenten Playwright-Kontexten geöffneten Standardtab automatisch finden und schließen
    - Ein wichtiger Logikfehler bei der Seitenrotation der Browser-Fetcher wurde behoben. Vorherige Seiten werden jetzt durch neue ersetzt, weil wiederverwendete Tabs noch durch frühere Einstellungen beeinflusst sein konnten
    - `StealthyFetcher` und seine Sitzungsklassen sind jetzt etwas schneller (5 %)

- **Verbesserte Eigenschaft `.body`**: Sie gibt den übergebenen Inhalt jetzt unverändert und ohne Verarbeitung zurück. Das ermöglicht Dateidownloads und Anfragen ohne HTML-Antwort. Hier ist ein Beispiel für den Download eines Bildes:

    ```python
    from scrapling.fetchers import Fetcher

    page = Fetcher.get('https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/poster.png')
    with open(file='poster.png', mode='wb') as f:
        f.write(page.body)
    ```

### 🐛 Fehlerbehebungen {#v0.3.2-bug-fixes}

- **Kodierungsprobleme behoben**: Mehrere Kodierungsprobleme mit einigen Websites im Parser, im Modus mcp und in den extract-Befehlen wurden behoben (Behebt auch #80 und #81)
- **Schnelleres Parsen**: Viele Änderungen in verschiedenen Bereichen machen die Bibliothek schneller. Das zeigen auch die aktualisierten Benchmarks

### 🔨 Sonstige Änderungen {#v0.3.2-misc}

- **Aktualisierte Benchmarks**: Die Leistungsmessungen wurden aktualisiert, um die aktuellen Geschwindigkeitsgewinne mit den neuesten Versionen ähnlicher Bibliotheken zu vergleichen
- **Viel Code überarbeitet und ungenutzten Code durch bessere Implementierungen ersetzt**: Weniger und übersichtlicherer Code, einfachere Wartung
- **YouTube-Video hinzugefügt**: Die MCP-Dokumentation wurde um Videoinhalte ergänzt.
- **Neue Issue-Vorlage**: Eine einfache Vorlage für Benutzer, die die bestehenden Vorlagen nicht nutzen können.
- **CI-Workflow optimiert**: Der Test-Workflow überspringt jetzt Ausführungen, wenn nur die Dokumentation oder andere Dateien ohne Code geändert wurden.
- **Abhängigkeiten aktualisiert**: Verschiedene Abhängigkeiten wurden auf die neuesten Versionen aktualisiert.
- **Codestil verbessert**: Neue ruff-Regeln wurden auf alle Dateien angewendet.
- **Pre-commit-Hooks**: Die Pre-commit-Konfiguration wurde aktualisiert.

### 🎯 Inkompatible Änderungen {#v0.3.2-breaking-changes}

- Der Parameter `max_pages` wurde aus der synchronen Version von `StealthySession` entfernt, um das Verhalten an `DynamicSession` anzugleichen. In der synchronen Version ist er nicht sinnvoll

## [v0.3.1](https://github.com/D4Vinci/Scrapling/releases/tag/v0.3.1) - 2025-09-02 {#v0.3.1}

1. Ein Problem bei der Installation von scrapling ohne das Extra `shell` wurde behoben (#76 )
2. Alle Browser-Fetcher und ihre Sitzungsklassen haben ein neues Argument für eine JS-Datei, die beim Erstellen der Seite ausgeführt wird (#56) :

```python
from scrapling.fetchers import StealthyFetcher

StealthyFetcher.fetch('https://example.com', init_script="/absolute/path/to/js/script.js")
```

## [v0.3](https://github.com/D4Vinci/Scrapling/releases/tag/v0.3) - 2025-09-01 {#v0.3}

🎉 **Große Version - Vollständige Überarbeitung der Architektur**

Scrapling v0.3 ist das bisher größte Update des Projekts. Die Architektur wurde komplett neu geschrieben, die Leistung deutlich verbessert und viele neue Funktionen ergänzt, darunter die KI-Integration und eine interaktive Shell für Web-Scraping.

Diese Version enthält mehrere inkompatible Änderungen. Bitte lesen Sie die Versionshinweise sorgfältig.

### 🚀 Wichtige neue Funktionen {#v0.3-major-new-features}

#### Architektur auf Basis von Sitzungen {#v0.3-session-based-architecture}
- **Neue Sitzungsklassen**: Vollständig neu geschrieben, mit Unterstützung für dauerhafte Sitzungen
    - `FetcherSession` - HTTP-Anfragen mit dauerhaftem Zustand, sowohl für synchronen als auch für asynchronen Code
    - `DynamicSession`/`AsyncDynamicSession` - Browser-Automatisierung, bei der der Browser offen bleibt, bis Sie fertig sind
    - `StealthySession`/`AsyncStealthySession` - Browser-Nutzung im Stealth-Modus, bei der der Browser offen bleibt, bis Sie fertig sind
- **Asynchrone Verwaltung von Browser-Tabs**: Das neue Argument `max_pages` stellt einen Pool von Tabs bereit, die für gleichzeitige Browser-Abrufe abwechselnd genutzt werden
- **Gleichzeitige Sitzungen**: Führen Sie mehrere voneinander getrennte Sitzungen gleichzeitig aus

Weitere Informationen finden Sie im Abschnitt `Fetching` auf der Website.

#### Viele neue Funktionen zur Tarnung und gegen Bot-Erkennung {#v0.3-a-lot-of-new-stealth-anti-bot-capabilities}
- **🤖 Cloudflare-Prüfungen lösen**: Automatisches [Lösen von Cloudflare-Turnstile-Prüfungen](fetching/stealthy.md#cloudflare-and-stealth-options) in `StealthyFetcher` und seinen Sitzungsklassen
- **Browser-Fingerprints nachbilden**: Die vollständig neue Klasse [Fetcher](fetching/static.md) bildet TLS-Fingerprints echter Browser nach, erzeugt zur Browserversion passende Header und unterstützt HTTP/3 und mehr
- **Verbesserter Stealth-Modus**: Der Stealth-Modus von `DynamicFetcher` und seinen Sitzungsklassen ist jetzt robuster und zuverlässiger (auch als `PlayWrightFetcher` bekannt)

#### KI-Integration und MCP-Server {#v0.3-ai-integration-mcp-server}
- **Integrierter MCP-Server**: Ein Server für das Model Context Protocol für KI-gestütztes Web-Scraping
- **6 leistungsfähige Werkzeuge**: `get`, `bulk_get`, `fetch`, `bulk_fetch`, `stealthy_fetch`, `bulk_stealthy_fetch`
- **Intelligente Inhaltsextraktion**: Wandeln Sie Webseiten oder Elemente in Markdown oder HTML um, oder extrahieren Sie eine bereinigte Fassung des Textinhalts
- **Unterstützung für CSS-Selektoren**: Wählen Sie mit der Scrapling-Engine gezielt einzelne Elemente aus, bevor Sie den Inhalt an die KI übergeben
- **Bot-Schutz umgehen**: Bewältigen Sie Cloudflare Turnstile und andere Schutzmaßnahmen
- **Proxy-Unterstützung**: Nutzen Sie Proxys für Anonymität und Anfragen aus bestimmten Regionen
- **Browser nachbilden**: Bilden Sie echte Browser mit TLS-Fingerprints, echten Headern passend zur Browserversion und mehr nach
- **Parallele Verarbeitung**: Lesen Sie mehrere URLs gleichzeitig aus, um effizienter zu arbeiten
- [und mehr...](ai/mcp-server.md)

#### Neue interaktive Shell für Web-Scraping {#v0.3-new-interactive-web-scraping-shell}
- **Eine neue Shell**: Eine angepasste IPython-Shell mit vielen praktischen integrierten Kurzbefehlen wie `get`, `post`, `put`, `delete`, `fetch` und `stealthy_fetch`
- **Intelligente Seitenverwaltung**: Die neuen Befehle `page` und `pages` speichern automatisch die aktuelle Seite und den Verlauf aller Anfragen aus der Shell
- **Curl-Integration**: Wandeln Sie curl-Befehle aus den DevTools des Browsers mit den Funktionen `uncurl` und `curl2fetcher` in `Fetcher`-Anfragen um
- [und mehr...](cli/interactive-shell.md)

#### Websites im Terminal auslesen, ohne zu programmieren {#v0.3-scrape-from-the-terminal-without-programming}
- **Neue Extract-Befehle**: Web-Scraping im Terminal ohne Programmierung
    - `scrapling extract get/post/put/delete` - Einfache HTTP-Anfragen
    - `scrapling extract fetch` - Dynamische Inhalte auslesen
    - `scrapling extract stealthy-fetch` - Bot-Schutz umgehen
- **Lädt Webseiten herunter** und speichert ihren Inhalt in Dateien.
- **Wandelt HTML in lesbare Formate um**, etwa Markdown, behält es als HTML bei oder extrahiert nur den Textinhalt der Seite.
- **Unterstützt eigene CSS-Selektoren**, um bestimmte Teile der Seite zu extrahieren.
- **Verarbeitet HTTP-Anfragen und Seitenabrufe über Browser.**
- **Umfassend anpassbar** mit eigenen Headern, Cookies, Proxys und weiteren Optionen. Fast alle Optionen, die im Code verfügbar sind, können Sie auch im Terminal nutzen.
- [und mehr...](cli/extract-commands.md)

### 🔧 Technische Verbesserungen {#v0.3-technical-improvements}

#### Leistungsverbesserungen {#v0.3-performance-enhancements}
- **Fetcher ist jetzt 4-mal schneller** - Ja, Sie haben richtig gelesen!
- **DynamicFetcher ist jetzt etwa 60 % schneller** - Je nach Konfiguration deutlich schneller, besonders im Stealth-Modus
- **StealthyFetcher ist jetzt 20–30 % schneller** - Dank der neuen Struktur und unserer eigenen Implementierung, die wir nun statt der Python-Schnittstelle von `Camoufox` einsetzen
- **Zusammen 50 % oder mehr Geschwindigkeitsgewinn** bei den wichtigsten Auswahlmethoden (`find_by_text`, `find_similar`, `find_by_regex`, `relocate` usw.) 🚀
- **Etwa 10 % mehr Geschwindigkeit bei CSS/XPath-Methoden für den ersten Treffer** - `css_first` und `xpath_first` sind jetzt schneller als `css` und `xpath`
- **Die Methode `get_all_text()` ist 40 % schneller** bei der Inhaltsextraktion
- **20 % mehr Geschwindigkeit** beim adaptiven Wiederfinden von Elementen
- **Navigationseigenschaften optimiert** - Eigenschaften wie `next`, `previous`, `below_elements` und weitere sind jetzt spürbar schneller
- **5-mal schnellere Textbereinigung**
- **Geringerer Speicherbedarf** durch optimierte Imports und weniger Verwaltungsaufwand
- **⚡ Blitzschnelle Imports**: Kürzere Startzeit durch optimiertes Laden von Modulen
- **Bessere Benchmarks**: Durch all diese Verbesserungen ist Scrapling im Vergleich zu anderen Bibliotheken noch viel schneller als zuvor (1775-mal schneller als BeautifulSoup und 5,1-mal schneller als AutoScraper, siehe [Benchmarks](benchmarks.md))

#### Architektur, Codequalität und Bedienung {#v0.3-architecture-code-quality-and-quality-of-life}
- **Dauerhafter Kontext**: Alle Browser-Fetcher verwenden jetzt standardmäßig einen dauerhaften Kontext. (Löst auch #64)
- **Schnelle Prüfung aller Browser-Fetcher mit msgspec**, bevor Anfragen ausgeführt werden. So lassen sich Fehler leichter finden.
- **Alle Cookies**, die Fetcher zurückgeben, entsprechen jetzt dem Format, das derselbe Fetcher akzeptiert. Sie können Cookies also abrufen und erneut an alle Fetcher und ihre Sitzungsklassen übergeben.
- **Schnellere Codeprüfung und Formatierung** durch den Wechsel zu `ruff`
- **Modernes Build-System**: Wechsel von setup.py zu pyproject.toml 📦
- **Bessere GitHub Actions und Workflows** für einfachere Entwicklung und Tests
- **🎨 Verbesserte Typangaben**: Vollständige Typangaben nach modernen Python-Standards für bessere IDE-Unterstützung und mehr Zuverlässigkeit
- **Aufgeräumter Code**: Nicht mehr genutzten Code entfernt und Kernfunktionen optimiert 🧹
- **🚀 Abwärtskompatibilität**: Kurzformen ergänzt, damit älterer Code weiter funktioniert

### Inkompatible Änderungen {#v0.3-breaking-changes}

#### Erforderliche Python-Version {#v0.3-minimum-python-version}
- **Python 3.10+ erforderlich**: Python 3.9 und ältere Versionen werden nicht mehr unterstützt

#### Namen von Klassen und Methoden {#v0.3-class-and-method-naming}
Diese Umbenennungen sollen die Namen klarer und einheitlicher machen, besonders für neue Nutzer.

- **`Adaptor` → `Selector`**: Die zentrale Parser-Klasse wurde umbenannt (kann zur Abwärtskompatibilität weiterhin als `Adaptor` importiert werden)
- **`Adaptors` → `Selectors`**: Die Sammlungsklasse wurde umbenannt (kann zur Abwärtskompatibilität weiterhin als `Adaptors` importiert werden)
- **`auto_match` → `adaptive`**: Parameter in allen Methoden umbenannt
- **`adaptor_arguments` → `selector_config`**: Konfigurationsparameter umbenannt
- **`automatch_domain` → `adaptive_domain`**: Domain-Parameter umbenannt
- **`additional_arguments` → `additional_args`**: Parametername verkürzt
- **⚠️ `text/body` → `content`**: Der Parameter des Selector-Konstruktors akzeptiert jetzt sowohl `str` als auch `bytes`
- **`PlayWrightFetcher` → `DynamicFetcher`**: Die Klasse für Browser-Automatisierung wurde umbenannt (kann zur Abwärtskompatibilität weiterhin als `PlayWrightFetcher` importiert werden)
- **DynamicFetcher enthält die NSTBrowser-Logik und ihre Argumente nicht mehr**, da es keinen Sinn mehr hat, sie beizubehalten.
- **Das Argument headless von StealthyFetcher akzeptiert 'virtual' nicht mehr**, da wir die Camoufox-Bibliothek nur noch verwenden, um den Installationspfad des Browsers und die übrigen Startoptionen zu ermitteln

### 🐛 Fehlerbehebungen {#v0.3-bug-fixes}

- Das Zählen verschachtelter Kindelemente in ignorierten Tags für `get_all_text` korrigiert (#61)
- Installationsprobleme durch Leerzeichen im Pfad zur ausführbaren Python-Datei behoben (#57)
- Threading-Probleme im Speichersystem bei der Verarbeitung von Rekursionen mit aktivierter adaptiver Funktion behoben
- Probleme mit der Rangfolge von Argumenten in `FetcherSession` durch das Sentinel-Muster behoben
- Die Verarbeitung von Proxy-Typen in `StealthyFetcher` korrigiert
- Konflikte zwischen den Argumenten `referer` und `google_search` behoben
- Probleme beim asynchronen Einfügen von Skripten zur Tarnung behoben

## [v0.2.99](https://github.com/D4Vinci/Scrapling/releases/tag/v0.2.99) - 2025-04-08 {#v0.2.99}

**Dieses Update ist für alle wichtig, die Scrapling in vollem Umfang nutzen möchten.**

### Was sich geändert hat {#v0.2.99-what-s-changed}
#### Neue Website mit vollständiger Dokumentation {#v0.2.99-new-full-documentation-website}
- Ja, endlich 😄 Schauen Sie [hier](index.md) vorbei
#### Einheitliche Import-Logik für Fetcher {#v0.2.99-unified-import-logic-for-fetchers}
- Sie können jetzt alle Fetcher mit `from scrapling.fetchers import Fetcher, AsyncFetcher, StealthyFetcher, PlayWrightFetcher` importieren und ohne Initialisierung direkt verwenden, etwa mit `page = Fetcher.get(...)`.<br/> Dies ersetzt den alten Import `from scrapling.defaults import Fetcher, AsyncFetcher, StealthyFetcher, PlayWrightFetcher`.
#### Inkompatible Änderung: automatch ist jetzt standardmäßig deaktiviert {#v0.2.99-breaking-change-automatch-is-now-turned-off-by-default}
- Es gibt jetzt eine neue Vorgehensweise, um automatch oder andere Parser-Optionen über Fetcher zu aktivieren. Einzelheiten finden Sie auf der [Dokumentationsseite](fetching/choosing.md#parser-configuration-in-all-fetchers).
>  Die alten Imports und die alte Logik bleiben zur Abwärtskompatibilität nutzbar, geben aber eine Warnung aus.
#### Neue Optionen für Fetcher {#v0.2.99-new-options-added-to-fetchers}
- Sowohl `StealthyFetcher` als auch `PlayWrightFetcher` haben jetzt beim Abrufen das neue Argument `wait`. Damit wartet der Fetcher eine bestimmte Zeit in Millisekunden, bevor er die Seite schließt und die Antwort zurückgibt.
- Die Methoden von `StealthyFetcher`, `fetch` und `async_fetch`, haben jetzt das Argument `additional_arguments`. Damit können Sie zusätzliche Einstellungen an Camoufox übergeben, die Vorrang vor den Scrapling-Einstellungen haben (#54 )
#### Fehlerbehebungen {#v0.2.99-bugs-squashed}
- Einen Fehler beim Erfassen von Weiterleitungen in `async_fetch` in den Klassen `StealthyFetcher` und `PlayWrightFetcher` behoben.

**_Vielen Dank für Ihre Unterstützung und Spenden!_**

## [v0.2.98](https://github.com/D4Vinci/Scrapling/releases/tag/v0.2.98) - 2025-03-17 {#v0.2.98}

**Dieses Update ist für alle wichtig, die Scrapling in vollem Umfang nutzen möchten**

### Was sich geändert hat {#v0.2.98-what-s-changed}
#### Verschiedene Verbesserungen bei Speicherbedarf und Geschwindigkeit {#v0.2.98-various-memory-usage-and-speed-optimizations}
- Alle Auswahlmethoden benötigen nur noch etwa 40 % des bisherigen Speichers und sind etwas schneller.
- Alle Untermodule der Bibliothek werden jetzt erst bei Bedarf geladen. Sie laden also nur, was Sie verwenden. Zum Beispiel:
Vor dem Update benötigte der Import `from scrapling import Adaptor` `30-40mb` RAM, weil dabei auch alle Fetcher und weitere Teile geladen wurden. Jetzt sind es nur noch `~1.2mb`.
- Durch das letzte Update benötigte die Bibliothek bei einem großen Anfrage-Pool nur noch etwa 32 % des bisherigen Speichers. Jetzt haben wir den Cache weiter angepasst, um noch weniger zu verbrauchen.
- Der Parser ist insgesamt um 2-5 % schneller

**_Vielen Dank für Ihre Unterstützung und Spenden!_**

## [v0.2.97](https://github.com/D4Vinci/Scrapling/releases/tag/v0.2.97) - 2025-03-15 {#v0.2.97}

**Dieses Update ist für alle wichtig, die Scrapling in vollem Umfang nutzen möchten**

### Was sich geändert hat {#v0.2.97-what-s-changed}
#### Weniger Speicherbedarf und etwas mehr Geschwindigkeit bei allen Fetchern. {#v0.2.97-lower-memory-usage-and-small-speed-increase-across-all-fetchers}
- Neue Grenzen für die Cache-Größe in der gesamten Bibliothek senken den Speicherbedarf deutlich, wenn Sie viele Anfragen oder Operationen ausführen.
- Große Teile der Fetcher wurden überarbeitet, um die Wartung zu erleichtern und die Geschwindigkeit etwas zu erhöhen.

#### Fehlerbehebungen {#v0.2.97-bugs-fixed}
- Einen Fehler in `TextHandler` behoben: Wenn die Klasse allein importiert wurde, wandelte sie Werte, die keine Zeichenketten waren, in eine leere Zeichenkette um. Jetzt wird jeder Wert für `TextHandler` zuerst in eine Zeichenkette und dann in `TextHandler` umgewandelt. Das gilt für jeden übergebenen Wert. Schließlich soll `TextHandler`, wie der Name sagt, nur mit Zeichenketten arbeiten! (#45 )
- Einen Fehler behoben, bei dem die `retries`-Argumente in den meisten Methoden von AsyncFetcher nicht berücksichtigt wurden.

#### Sonstiges {#v0.2.97-miscellaneous}
- Die Typangaben für die meisten Argumente aller Fetcher wurden klarer und genauer gemacht.

**_Vielen Dank für Ihre Unterstützung und Spenden!_**

## [v0.2.96](https://github.com/D4Vinci/Scrapling/releases/tag/v0.2.96) - 2025-03-05 {#v0.2.96}

**Dieses Update ist für alle wichtig, die Scrapling in vollem Umfang nutzen möchten**

### Was sich geändert hat {#v0.2.96-what-s-changed}
1. Die Option `-f` für `scrapling install` ergänzt, um die Neuinstallation der Browser-Abhängigkeiten zu erzwingen. Ich empfehle, jetzt `scrapling install -f` auszuführen, damit Sie den großen Geschwindigkeitsgewinn von `StealthyFetcher` mit der neuen Camoufox-Browserversion nutzen können :)
2. Einen Fehler in `TextHandler` behoben, bei dem Slicing ein `TextHandlers`-Objekt statt eines `TextHandler`-Objekts zurückgab. Auch die Typangabe wurde korrigiert (#41 )
3. Ein Problem behoben, bei dem `scrapling install` in manchen Fällen eine Python-Shell öffnete!

## [v0.2.95](https://github.com/D4Vinci/Scrapling/releases/tag/v0.2.95) - 2025-02-25 {#v0.2.95}

**Dieses Update ist für alle wichtig, die Scrapling in vollem Umfang nutzen möchten**

### Was sich geändert hat {#v0.2.95-what-s-changed}
1. Einen Fehler in `Fetcher` behoben, bei dem die mit dem Argument `stealthy_headers` erzeugten Header einige vom Nutzer gesetzte Header wie `Accept` überschrieben (#39 )
2. Die Erzeugung der Header etwas verbessert. Das sollte die Geschwindigkeit leicht erhöhen.

## [v0.2.94](https://github.com/D4Vinci/Scrapling/releases/tag/v0.2.94) - 2025-02-22 {#v0.2.94}

**Dieses Update ist für alle wichtig, die Scrapling in vollem Umfang nutzen möchten**

### Was sich geändert hat {#v0.2.94-what-s-changed}
1. Die Eigenschaft `history` für alle Fetcher ergänzt, um Weiterleitungen anzuzeigen (#32 )
2. Die Logik des Arguments `case_sensitive` für alle `re`/`re_first`-Methoden korrigiert. Wenn Sie dieses Argument genutzt haben, kann Ihr Code jetzt andere Ergebnisse liefern (aber vielleicht haben Sie das verdient, wenn Sie den Fehler bemerkt und kein Issue eröffnet haben, LOL).
3. Abhängigkeiten aktualisiert und `coop` in der Camoufox-Engine (StealthyFetcher) wieder aktiviert.

## [v0.2.93](https://github.com/D4Vinci/Scrapling/releases/tag/v0.2.93) - 2025-01-31 {#v0.2.93}

**Dieses Update ist für alle wichtig, die Scrapling in vollem Umfang nutzen möchten**

### Was sich geändert hat {#v0.2.93-what-s-changed}
1. Der Rückgabetyp ist jetzt im gesamten Parser einheitlich. Sie erhalten immer einen dieser Typen: `Adaptor`, `Adaptors`, `TextHandler`, `TextHandlers`, `None` oder eine Liste bei gemischten Ergebnissen, etwa durch einen kombinierten CSS-Selektor. Das erleichtert das Programmieren mit weniger manuellen Typprüfungen, macht die Bibliothek stabiler und ermöglicht immer das Verketten von Methoden.
2. Große Teile des Parsers, besonders die Klasse `Adaptor`, wurden überarbeitet und sind jetzt übersichtlicher und vor allem schneller. Fast alle Methoden und Eigenschaften, besonders die Suchmethoden, sind jetzt 5-40 % schneller. Manche haben noch mehr zugelegt: `find_by_regex` ist etwa 60 % schneller! Die automatch-Funktion ist etwa 5 % schneller.
3. Logikfehler in den Methoden `find_all`/`find` behoben, durch die übergebene Filter manchmal mit ODER und manchmal mit UND verknüpft wurden. Jetzt müssen alle zurückgegebenen Elemente alle übergebenen Filter erfüllen.
4. Alle Methoden für reguläre Ausdrücke geben jetzt `TextHandler`/`TextHandlers` zurück, damit sich Methoden leichter verketten lassen.
5. **Die neue Eigenschaft** `below_elements` ergänzt. Sie gibt ein `Adaptors`-Objekt mit allen Elementen unterhalb des aktuellen Elements im DOM-Baum zurück.
6. Alle Methoden und Eigenschaften, die HTML-Quelltext als Zeichenkette zurückgaben, geben ihn jetzt als `TextHandler` zurück. So können Sie darauf leichter reguläre Ausdrücke und weitere Funktionen anwenden.
7. StealthyFetcher ist jetzt etwas schneller und besser getarnt. Außerdem können Sie jetzt auf Captchas in iframes klicken, etwa auf **Cloudflare Turnstile**.
8. Die automatische Vervollständigung und die Typangaben wurden in fast der Hälfte der Bibliothek deutlich verbessert, besonders bei `Adaptor`, `TextHandler` und `TextHandlers`.
9. Ein `TextHandler` gibt beim Slicing, bei Indexzugriffen oder bei Verwendung der Methode `split` jetzt ein weiteres `TextHandler`-Objekt statt einer normalen Python-Zeichenkette zurück. Fast alle üblichen Zeichenkettenoperationen und Methoden geben jetzt weitere `Texthandler`-Objekte statt normaler Zeichenketten zurück, damit sich Methoden und Funktionen immer verketten lassen.
10. Einige kleine Fehler und Tippfehler behoben. Zum Beispiel führte Fetcher async_put eine POST-Anfrage statt einer PUT-Anfrage aus 😶‍🌫️
11. Die README etwas verbessert, bis ich die Dokumentationswebsite fertig habe.

Dies sollte nur ein kleines Update vor Version 0.3 werden, aber ich wollte es noch etwas besser machen.

## [v0.2.92](https://github.com/D4Vinci/Scrapling/releases/tag/v0.2.92) - 2024-12-26 {#v0.2.92}

### Was sich geändert hat {#v0.2.92-what-s-changed}
- Antworten von Browser-Fetchern nutzen jetzt zuverlässigere Datenquellen, wenn die geladene Seite viele iframes enthält.
- **Die Installation von `Scrapling` ist jetzt noch einfacher: Installieren Sie es mit pip, führen Sie dann `scrapling install` im Terminal aus, und Sie können loslegen!**
- Eine ungenaue Typangabe im Parser korrigiert.

## [v0.2.91](https://github.com/D4Vinci/Scrapling/releases/tag/v0.2.91) - 2024-12-19 {#v0.2.91}

### Was sich geändert hat {#v0.2.91-what-s-changed}
- Einen Fehler behoben, bei dem die Protokollmeldung zum Seitenabruf nur bei der ersten Anfrage erschien.
- Beim Aufrufen einer Seite gibt die Playwright-API standardmäßig die erste Antwort zurück, die den an `goto` übergebenen Ladezustand `["load", "domcontentloaded", "networkidle"]` erfüllt. Wenn eine Website zuerst eine Warteseite wie die von Cloudflare zeigt und danach zur eigentlichen Website weiterleitet, gibt Playwright den ersten Statuscode zurück, etwa 403. Dieses Update löst das Problem für `PlaywrightFetcher` und `StealthyFetcher`, die beide die Playwright-API nutzen. Das Ergebnis hängt also nicht mehr vom Standardverhalten von Playwright ab.
- Unterstützung für SOCKS-Proxys in der Klasse `Fetcher` ergänzt.
- Die Typangabe des Arguments `wait_selector_state` korrigiert, damit die automatische Vervollständigung die richtigen möglichen Werte anzeigt.

## [v0.2.9](https://github.com/D4Vinci/Scrapling/releases/tag/v0.2.9) - 2024-12-16 {#v0.2.9}

### Was sich geändert hat {#v0.2.9-what-s-changed}
##### Neue Funktionen {#v0.2.9-new-features}
1. Die **lang erwartete** Unterstützung für asynchronen Code ist da! Es gibt jetzt die Klasse `AsyncFetcher` als asynchrone Variante von `Fetcher`. Außerdem haben `StealthyFetcher` und `PlayWrightFetcher` die neue Methode `async_fetch` mit denselben Optionen.

```python
>> from scrapling import StealthyFetcher
>> page = await StealthyFetcher().async_fetch('https://www.browserscan.net/bot-detection')  # the async version of fetch
>> page.status == 200
True
```

2. Die Klasse `StealthyFetcher` hat jetzt das Argument `geoip` in ihren Abrufmethoden. Wenn es aktiviert ist, verwendet die Klasse automatisch Längengrad, Breitengrad, Zeitzone, Land und regionale Einstellungen der IP-Adresse und passt dann die WebRTC-IP-Adresse entsprechend an. Sie bestimmt außerdem die Browsersprache anhand der Verteilung der Sprachen in der Zielregion und stellt sie entsprechend ein.
3. Das Argument `retries` zu den Klassen `Fetcher`/`AsyncFetcher` hinzugefügt. Damit können Sie festlegen, wie oft jede über `httpx` ausgeführte Anfrage erneut versucht wird.
4. Die Methode `url_join` zu `Adaptor` und den Fetchern hinzugefügt. Sie verbindet eine relative URL mit der aktuellen URL zu einer vollständigen absoluten URL!
5. Die Methode `keep_cdata` zu `Adaptor` und den Fetchern hinzugefügt, damit Sie bei Bedarf verhindern können, dass der Parser CDATA entfernt.
6. In `Adaptor`/`Response` gibt die Methode `body` jetzt nach Möglichkeit die rohe HTML-Antwort zurück, ohne sie in der Bibliothek zu verarbeiten.
7. Protokollierung zur Klasse `Response` hinzugefügt. Wenn Sie Fetcher verwenden, erhalten Sie jetzt eine Protokollmeldung mit Informationen zur Antwort.
Beispiel:

   ```python
   >> from scrapling.defaults import Fetcher
   >> Fetcher.get('https://books.toscrape.com/index.html')
   [2024-12-16 13:33:36] INFO: Fetched (200) <GET https://books.toscrape.com/index.html> (referer: https://www.google.com/search?q=toscrape)
   >>
   ```

8. Wenn Sie übliche Zeichenkettenmethoden auf einem `TextHandler` verwenden, etwa `.replace()`, erhalten Sie jetzt ein weiteres `TextHandler`-Objekt. Zuvor wurde eine normale Zeichenkette zurückgegeben.
9. Deutliche Geschwindigkeitsverbesserungen in der gesamten Bibliothek und insgesamt bessere Tarnung in den Fetcher-Klassen.
10. Einfache Funktionen wie `extract_first`\`extract` ergänzt, die dasselbe Ergebnis wie das übergeordnete Objekt zurückgeben. Sie sind nur dazu da, Code bei Bedarf leichter von Scrapy/Parsel nach Scrapling zu kopieren, da diese Funktionen dort verwendet werden!
11. Da große Teile des Codes überarbeitet wurden und Caching an den richtigen Stellen eingesetzt wird, sind viele Anfragen auf einmal jetzt deutlich schneller.

##### Inkompatible Änderungen {#v0.2.9-breaking-changes}
- Python 3.8 wird nicht mehr unterstützt. (Hauptsächlich, weil Playwright die Unterstützung beendet hat, aber diese Version war ohnehin problematisch.)
- Das Argument `debug` wurde aus der gesamten Bibliothek entfernt. Wenn Sie Debugging aktivieren möchten, führen Sie nach dem Import der Bibliothek Folgendes aus:

   ```python
   >>> import logging
   >>> logging.getLogger("scrapling").setLevel(logging.DEBUG)
   ```

##### Fehlerbehebungen {#v0.2.9-bugs-squashed}
1. WebGL ist jetzt standardmäßig aktiviert, da viele Schutzsysteme inzwischen prüfen, ob es aktiviert ist.
2. Einige Fehler und Tippfehler in der Dokumentation und README korrigiert.

##### Verbesserungen der Bedienung {#v0.2.9-quality-of-life-changes}
1. Die gesamte Protokollierung läuft jetzt unter dem Logger-Namen `scrapling`, damit sie sich einfacher und übersichtlicher steuern lässt. Zuvor wurde der Root-Logger verwendet.
2. Den Testordner übersichtlicher aufgebaut und Tests für die neuen Funktionen ergänzt. Alle Tests wurden übersichtlicher neu geschrieben und weitere Tests für eine höhere Abdeckung hinzugefügt.
3. Einen großen Teil des Codes überarbeitet, damit er übersichtlicher und leichter zu warten ist.

> All diese Änderungen waren ursprünglich für 0.3 geplant. Ich habe sie aber schon hier aufgenommen, weil es bis zur nächsten Version noch etwas dauern wird. Als Nächstes werde ich die ausführliche Dokumentationswebsite fertigstellen und dann an Version 0.3 arbeiten.

## [v0.2.8](https://github.com/D4Vinci/Scrapling/releases/tag/v0.2.8) - 2024-11-30 {#v0.2.8}

### Was sich geändert hat {#v0.2.8-what-s-changed}
- Dieses kleine Update enthält einige wichtige Verbesserungen für die Nutzung des Codes und korrigiert einen Tippfehler in der Haupt-README (#20).

## [v0.2.7](https://github.com/D4Vinci/Scrapling/releases/tag/v0.2.7) - 2024-11-26 {#v0.2.7}

### Was sich geändert hat {#v0.2.7-what-s-changed}
##### Neue Funktionen {#v0.2.7-new-features}
- Wenn Sie das Argument `wait_selector` mit den Klassen `StealthyFetcher` und `PlayWrightFetcher` verwenden, wartet Scrapling danach erneut wie üblich darauf, dass JavaScript vollständig geladen und ausgeführt wird. Wenn Sie das Argument `network_idle` verwenden, wartet Scrapling anschließend auch erneut auf diesen Zustand. Sind alle Zustände bereits erreicht, gibt es natürlich keine Wartezeit.
- In `StealthyFetcher` können Sie mit dem Argument `disable_ads` jetzt Werbung zulassen oder blockieren. Die Option ist standardmäßig aktiviert und installiert die Erweiterung `ublock origin`.
- Die regionalen Einstellungen von `PlayWrightFetcher` können Sie jetzt mit dem Argument `locale` festlegen. Der Standardwert bleibt `en-US`.
- Einfache Anfragen über `Fetcher` akzeptieren jetzt Proxys im Format `http://username:password@localhost:8030`.
- Der Stealth-Modus von `PlayWrightFetcher` wurde etwas verbessert.

##### Fehlerbehebungen und Verbesserungen {#v0.2.7-bugs-squashed-improvements}
1. Die Aktivierung von Proxys in der Klasse `PlayWrightFetcher` hängt jetzt nicht mehr davon ab, ob der Modus `stealth` aktiviert ist (danke an [@AbdullahY36](https://github.com/AbdullahY36) für den Hinweis).
2. `ResponseEncoding` prüft jetzt, ob die in der Antwort angegebene Kodierung für die Seite verwendet werden kann. Führt sie zu einem Fehler, verwendet Scrapling `utf-8`.

## [v0.2.6](https://github.com/D4Vinci/Scrapling/releases/tag/v0.2.6) - 2024-11-24 {#v0.2.6}

### Was sich geändert hat {#v0.2.6-what-s-changed}
##### Neue Funktionen {#v0.2.6-new-features}
- `PlayWrightFetcher` kann jetzt den echten Browser direkt verwenden. Übergeben Sie dazu das Argument `real_chrome` an `PlayWrightFetcher.fetch`. Dafür muss Chrome installiert sein. Scrapling startet eine Instanz Ihres Chrome-Browsers, und Sie können die meisten Optionen wie gewohnt verwenden. (Zuvor war dies nur mit dem Argument `cdp_url` möglich.)
- Die Versionsangabe der für echte Browser erzeugten Header erhöht.

##### Fehlerbehebungen {#v0.2.6-bugs-squashed}
1. Das Format der von `BrowserForge` erzeugten Browser-Header war veraltet. Dadurch erkannten einige Schutzsysteme Scrapling. Deshalb wird `BrowserForge` jetzt nur noch verwendet, um einen echten User-Agent zu erzeugen.
2. Das Argument `hide_canvas` ist jetzt standardmäßig deaktiviert, da Googles ReCaptcha es erkennt.

## [v0.2.5](https://github.com/D4Vinci/Scrapling/releases/tag/v0.2.5) - 2024-11-23 {#v0.2.5}

### Was sich geändert hat {#v0.2.5-what-s-changed}

##### Fehlerbehebungen {#v0.2.5-bugs-squashed}
- Einen Fehler beim Argument 'wait_selector' behoben, wenn es mehr als 1 Element fand. Dies betrifft die Klassen `StealthyFetcher` und `PlayWrightFetcher`.
- Den Kodierungstyp korrigiert, wenn der Header `content_type` einen Wert mit Parametern wie `charset` enthält (danke an @andyfcx für [#12](https://github.com/D4Vinci/Scrapling/issues/12) ).

##### Verbesserungen der Bedienung {#v0.2.5-quality-of-life}
- Weitere Tests für neue Teile des Codes ergänzt. Die Tests werden jetzt in Threads ausgeführt.
- Ich habe die Docstrings angepasst, damit Sphinx apidoc und ähnliche Werkzeuge sie korrekt darstellen können.

##### Neue Mitwirkende {#v0.2.5-new-contributors}
- @andyfcx hat in [#13 ](https://github.com/D4Vinci/Scrapling/pull/13) erstmals mitgewirkt

## [v0.2.4](https://github.com/D4Vinci/Scrapling/releases/tag/v0.2.4) - 2024-11-20 {#v0.2.4}

### Was sich geändert hat {#v0.2.4-what-s-changed}

##### Fehlerbehebungen {#v0.2.4-bugs-squashed}
- Einen Fehler beim Abrufen der Antwort-Bytes nach Verwendung des Arguments `network_idle` in den Klassen `StealthyFetcher` und `PlayWrightFetcher` behoben. <br/> Er verursachte die folgende Fehlermeldung:

    ```
    Response.body: Protocol error (Network.getResponseBody): No resource with given identifier found
    ```

- Die PlayWright-API gibt bei Antworten manchmal einen leeren Statustext zurück. In diesem Fall ermittelt `Scrapling` ihn jetzt selbst. Dies betrifft die Klassen `StealthyFetcher` und `PlayWrightFetcher`.

## [v0.2.3](https://github.com/D4Vinci/Scrapling/releases/tag/v0.2.3) - 2024-11-19 {#v0.2.3}

### Was sich geändert hat {#v0.2.3-what-s-changed}

##### Fehlerbehebungen {#v0.2.3-bugs-squashed}
- Einen Fehler bei der Installation mit pip behoben, durch den der Stealth-Modus des PlayWright-Fetchers überhaupt nicht funktionierte.

## [v0.2.2](https://github.com/D4Vinci/Scrapling/releases/tag/v0.2.2) - 2024-11-16 {#v0.2.2}

### Was sich geändert hat {#v0.2.2-what-s-changed}
##### Neue Funktionen {#v0.2.2-new-features}
- Wenn Sie dem erzeugten `Adaptor`-Objekt keine Argumente übergeben und die Standardwerte nutzen möchten, können Sie für übersichtlicheren Code stattdessen diesen Import verwenden

    ```python
    >> from scrapling.default import Fetcher, StealthyFetcher, PlayWrightFetcher
    >> page = Fetcher.get('https://example.com', stealthy_headers=True)
    ```

    Andernfalls

    ```python
    >> from scrapling import Fetcher, StealthyFetcher, PlayWrightFetcher
    >> page = Fetcher(auto_match=False).get('https://example.com', stealthy_headers=True)
    ```

##### Fehlerbehebungen {#v0.2.2-bugs-squashed}
1. Einen Fehler mit dem `Response`-Objekt behoben, der gestern mit Patch v0.2.1 eingeführt wurde und in manchen Fällen bei verschachtelter Auswahl oder Analyse auftrat.

## [v0.2.1](https://github.com/D4Vinci/Scrapling/releases/tag/v0.2.1) - 2024-11-15 {#v0.2.1}

### Was sich geändert hat {#v0.2.1-what-s-changed}
##### Neue Funktionen {#v0.2.1-new-features}
1. Das von allen Fetchern zurückgegebene `Response`-Objekt entspricht jetzt dem `Adaptor`-Objekt, hat aber zusätzlich diese Attribute: `status`, `reason`, `cookies`, `headers` und `request_headers`. Die Attribute `cookies`, `headers` und `request_headers` sind immer vom Typ `dictionary`. <br/>Ihr Code kann jetzt also so aussehen:

    ```python
    >> from scrapling import Fetcher
    >> page = Fetcher().get('https://example.com', stealthy_headers=True)
    >> print(page.status)
    200
    >> products = page.css('.product')
    ```

    Statt wie bisher

    ```python
    >> from scrapling import Fetcher
    >> fetcher = Fetcher().get('https://example.com', stealthy_headers=True)
    >> print(fetcher.status)
    200
    >> page = fetcher.adaptor
    >> products = page.css('.product')
    ```

    Die Eigenschaft `.adaptor` funktioniert zur Abwärtskompatibilität aber weiterhin.

2. Die Klassen `StealthyFetcher` und `PlayWrightFetcher` akzeptieren jetzt beim Abrufen ein Argument `proxy`, das eine Zeichenkette oder ein Dictionary sein kann.
3. Die Klasse `StealthyFetcher` hat jetzt das Argument `os_randomize` in der Methode `fetch`. Wenn es aktiviert ist, wählt Scrapling die Betriebssystem-Fingerprints zufällig aus. Standardmäßig passen die Fingerprints zum aktuellen Betriebssystem.

##### Fehlerbehebungen {#v0.2.1-bugs-squashed}
1. Einen Fehler beim Übergeben von Headern mit der Klasse `Fetcher` behoben.
2. Einen Fehler beim Parsen von JSON-Antworten aus Fetcher-Klassen behoben.

##### Verbesserungen der Bedienung {#v0.2.1-quality-of-life-changes}
1. Die Textfunktion versuchte bisher, HTML-Kommentare vor der Rückgabe des Textes zu entfernen. Das führte in manchen Fällen zu Fehlern und machte den Code unnötig kompliziert. Jetzt verwendet sie wieder das Standardverhalten von lxml. **Alle Operationen, die den Text von Elementen nutzen, etwa Selektoren, sind dadurch etwas schneller.** Wenn Scrapling HTML-Kommentare aus Elementen vor der Textrückgabe entfernen soll, um das ungewöhnliche Aufteilen des Textes in lxml/parsel/scrapy zu vermeiden, lassen Sie das Argument `keep_comments` einfach wie standardmäßig auf True gesetzt.

## [v0.2](https://github.com/D4Vinci/Scrapling/releases/tag/v0.2) - 2024-11-11 {#v0.2}

### Was sich geändert hat {#v0.2-what-s-changed}
##### Neue Funktionen {#v0.2-new-features}
1. Die neue Funktion `Fetchers` mit 3 Haupttypen ist da. Damit ruft Scrapling Seiten für Sie ab, mit VIELEN Optionen!
    - Die Klasse `Fetcher` für einfache HTTP-Anfragen
    - Die Klasse `StealthyFetcher` ist ein vollständig getarnter Fetcher, der eine [zur Tarnung angepasste Firefox-Version](https://github.com/daijro/camoufox) nutzt.
    - Die Klasse `PlayWrightFetcher` ermöglicht Browser-Anfragen mit unverändertem PlayWright, mit meinem Stealth-Modus für PlayWright, mit echten Browsern über CDP und mit [NSTBrowser](https://app.nstbrowser.io/r/1vO5e5) über dessen [Docker-Browserless-Image](https://hub.docker.com/r/nstbrowser/browserless)!
2. Die völlig neuen Methoden `find_all`/`find` hinzugefügt, mit denen Sie Elemente auf der Seite ganz einfach wie durch dunkle Magie finden!
3. Die Methoden `filter` und `search` zur Klasse `Adaptors` hinzugefügt, um Gruppen von `Adaptor`-Objekten leichter gemeinsam zu verarbeiten.
4. Die Methoden `css_first` und `xpath_first` für eine einfachere Nutzung hinzugefügt.
5. Den neuen Klassentyp `TextHandlers` hinzugefügt. Damit können Sie `TextHandler`-Objekte gemeinsam verarbeiten, ähnlich wie mit der Klasse `Adaptors`.
6. Die Methoden `generate_full_css_selector` und `generate_full_xpath_selector` hinzugefügt.

##### Fehlerbehebungen {#v0.2-bugs-squashed}
1. Die Klasse `Adaptors` gibt mit `re_first` jetzt das erste passende Ergebnis aus allen enthaltenen `Adaptor`-Objekten zurück. Zuvor gab sie fälschlicherweise die Ergebnisse von `re_first` aller `Adaptor`-Objekte zurück.
2. Wenn Sie Text aus ausgewählten Elementen abrufen, etwa mit der CSS-Funktion `::text` über Methoden wie `.css` oder `.xpath`, gibt das `Adaptor`-Objekt jetzt `TextHandlers` statt einer Liste von Zeichenketten zurück. Sie können also jetzt `page.css('something::text').re_first(r'regex_pattern').json()` statt `page.css('something::text')[0].re_first(r'regex_pattern').json()` verwenden.
3. Die Argumente von re/re_first in `Adaptor`/`Adaptors` stimmen jetzt mit denen von `TextHandler` überein. Sie haben also jetzt die Argumente `clean_match` und `case_sensitive`.
4. Das Argument `auto_match` ist jetzt bei der Initialisierung von `Adaptor` standardmäßig aktiviert. Sie müssen es aber weiterhin bei der Elementauswahl aktivieren, wenn Sie die Funktion nutzen möchten. (Kein Fehler, sondern eine Designentscheidung.)
5. Viele Typangaben an verschiedenen Stellen korrigiert, um die automatische Vervollständigung beim Programmieren mit Scrapling zu verbessern.

##### Verbesserungen der Bedienung {#v0.2-quality-of-life-changes}
1. Die Methoden `css_selector` und `xpath_selector` in `generate_css_selector` und `generate_xpath_selector` umbenannt. Das macht die Namen klarer und stört die automatische Vervollständigung beim Programmieren nicht mehr.
2. Den größten Teil des alten Codes in ein Unterpaket `core` verschoben und weitere Designentscheidungen getroffen, um den Code übersichtlicher und die spätere Wartung einfacher zu machen.
3. Den Testordner übersichtlicher aufgebaut und Tests für die neuen Funktionen ergänzt. Außerdem werden tox-Umgebungen jetzt auf GitHub zwischengespeichert, damit die automatischen Tests bei jedem Commit schneller laufen.

## [v0.1.2](https://github.com/D4Vinci/Scrapling/releases/tag/v0.1.2) - 2024-10-16 {#v0.1.2}

**Änderungsverlauf**:

- Einen Fehler behoben, bei dem das Argument `keep_comments` nicht wie vorgesehen funktionierte.
- Die Textfunktion so angepasst, dass sie HTML-Kommentare vor dem Extrahieren des Textes automatisch aus Elementen entfernt, um das abweichende Verhalten von Lxml zu vermeiden. Zum Beispiel:

    ```python
    >>> page = Adaptor('<span>CONDITION: <!-- -->Excellent</span>', keep_comments=True)
    >>> page.css('span::text')
    ['CONDITION: ', 'Excellent']
    ```

    Dies war zuvor wegen des Standardverhaltens von Lxml das Ergebnis. Jetzt wird der vollständige Text 'CONDITION: Excellent' zurückgegeben.
    Dieses Verhalten ist auch aus parsel\scrapy bekannt. Deshalb wollte ich es hier abfangen.

- Einen Fehler behoben, bei dem die von der Bibliothek erzeugte SQLite-Datenbankdatei bei `pip uninstall scrapling` oder ähnlichen Befehlen nicht gelöscht wurde.

## [v0.1.1](https://github.com/D4Vinci/Scrapling/releases/tag/v0.1.1) - 2024-10-14 {#v0.1.1}

Kleine Korrekturen

## [v0.1](https://github.com/D4Vinci/Scrapling/releases/tag/v0.1) - 2024-10-13 {#v0.1}

**Vollständiger Änderungsverlauf**: <https://github.com/D4Vinci/Scrapling/commits/v0.1>
