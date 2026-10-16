---
title: "Webseiten über die CLI als Markdown, HTML oder Text speichern"
description: "Speichern Sie mit scrapling extract die Ergebnisse von HTTP-Anfragen oder Browser-Aufrufen. Filtern Sie Inhalte mit CSS, legen Sie Anfrageoptionen fest und wählen Sie das Ausgabeformat."
---

# Anleitung zum Extraktionsbefehl von Scrapling {#scrapling-extract-command-guide}

**Web Scraping über das Terminal, ohne zu programmieren!**

Mit `scrapling extract` können Sie Inhalte von Websites direkt im Terminal herunterladen und extrahieren, ohne Code zu schreiben. Der Befehl eignet sich für Einsteiger, Forschende und alle, die schnell Daten aus dem Web brauchen.

!!! success "Voraussetzungen"

    1. Lesen Sie die [Grundlagen der Fetcher](../fetching/choosing.md), um das [Response-Objekt](../fetching/choosing.md#response-object) zu verstehen und einen Fetcher auszuwählen.
    2. Lesen Sie die Seite zur [Elementauswahl](../parsing/selection.md), um Elemente in einem [Selector](../parsing/main_classes.md#selector)/[Response](../fetching/choosing.md#response-object) zu finden und zu extrahieren.
    3. Lesen Sie die Seite über die [Hauptklassen](../parsing/main_classes.md), um zu erfahren, welche Eigenschaften und Methoden [Response](../fetching/choosing.md#response-object) von [Selector](../parsing/main_classes.md#selector) erbt.
    4. Lesen Sie mindestens eine Seite im Fetcher-Abschnitt zu den Anfragen, die Sie hier verwenden werden: [HTTP-Anfragen](../fetching/static.md) oder [Seiten mit einem Browser abrufen](../fetching/stealthy.md).

## Was ist die Befehlsgruppe Extract? {#what-is-the-extract-command-group}

Die Befehlsgruppe enthält einfache Terminal-Werkzeuge mit diesen Funktionen:

- **Webseiten herunterladen** und ihren Inhalt in Dateien speichern.
- **HTML in lesbare Formate umwandeln**, zum Beispiel Markdown, als HTML behalten oder nur den Text der Seite extrahieren.
- **Eigene CSS-Selektoren verwenden**, um bestimmte Teile einer Seite zu extrahieren.
- **HTTP-Anfragen senden und Seiten mit Browsern abrufen**.
- **Fast alle Optionen anpassen**, die auch im Code verfügbar sind, etwa Header, Cookies und Proxies.

!!! tip "Modus für KI"

    Alle Extraktionsbefehle unterstützen die Option `--ai-targeted`. Wenn sie aktiviert ist, wird nur der Hauptinhalt des Seitenkörpers extrahiert. Außerdem entfernt sie Tags ohne nützlichen Text (script, style, noscript, svg), versteckte Elemente, die für Prompt Injection verwendet werden könnten (durch Inline-Styles versteckte Elemente, aria-hidden, versteckte Slots und template-Tags), Unicode-Zeichen mit der Breite null und HTML-Kommentare. Beim Browser-Befehl (`fetch`) aktiviert sie auch den Werbeblocker. Dieser Modus eignet sich, wenn die Ausgabe für ein KI-Modell bestimmt ist.

## Schnellstart {#quick-start}

- **Eine Webseite herunterladen**

    Laden Sie den Inhalt einer Webseite als sauberen, lesbaren Text herunter:
    ```bash
    scrapling extract get "https://example.com" page_content.txt
    ```
    Dieser Befehl sendet eine HTTP-GET-Anfrage und speichert den Text der Seite in `page_content.txt`.

- **In anderen Formaten speichern**

    Wählen Sie das Ausgabeformat, indem Sie die Dateiendung ändern:
    ```bash
    # Convert the HTML content to Markdown, then save it to the file (great for documentation)
    scrapling extract get "https://blog.example.com" article.md
    
    # Save the HTML content as it is to the file
    scrapling extract get "https://example.com" page.html
    
    # Save a clean version of the text content of the webpage to the file
    scrapling extract get "https://example.com" content.txt
  
    # Or use the Docker image with something like this:
    docker run -v $(pwd)/output:/output pyd4vinci/scrapling extract get "https://blog.example.com" /output/article.md 
    ```

- **Bestimmte Inhalte extrahieren**

    Alle Befehle können mit `--css-selector` oder `-s` bestimmte Teile einer Seite über CSS-Selektoren extrahieren. Die folgenden Beispiele zeigen dies.

## Verfügbare Befehle {#available-commands}

Mit `scrapling extract --help` erhalten Sie diese Liste der verfügbaren Befehle:
```bash
Usage: scrapling extract [OPTIONS] COMMAND [ARGS]...

  Fetch web pages using various fetchers and extract full/selected HTML content as HTML, Markdown, or extract text content.

Options:
  --help  Show this message and exit.

Commands:
  get             Perform a GET request and save the content to a file.
  post            Perform a POST request and save the content to a file.
  put             Perform a PUT request and save the content to a file.
  delete          Perform a DELETE request and save the content to a file.
  fetch           Use StealthyFetcher to fetch content with advanced stealth features.
```

Im Folgenden gehen wir jeden Befehl durch.

### HTTP-Anfragen {#http-requests}

1. **GET-Anfrage**

    Der häufigste Befehl zum Herunterladen von Website-Inhalten:

    ```bash
    scrapling extract get [URL] [OUTPUT_FILE] [OPTIONS]
    ```

    **Beispiele:**
    ```bash
    # Basic download
    scrapling extract get "https://news.site.com" news.md
    
    # Download with custom timeout
    scrapling extract get "https://example.com" content.txt --timeout 60
    
    # Extract only specific content using CSS selectors
    scrapling extract get "https://blog.example.com" articles.md --css-selector "article"
   
    # Send a request with cookies
    scrapling extract get "https://scrapling.requestcatcher.com" content.md --cookies "session=abc123; user=john"
   
    # Add user agent
    scrapling extract get "https://api.site.com" data.txt -H "User-Agent: MyBot 1.0"
    
    # Add multiple headers
    scrapling extract get "https://site.com" page.html -H "Accept: text/html" -H "Accept-Language: en-US"
    ```
    Zeigen Sie die verfügbaren Optionen mit `scrapling extract get --help` an:
    ```bash
    Usage: scrapling extract get [OPTIONS] URL OUTPUT_FILE
    
      Perform a GET request and save the content to a file.
    
      The output file path can be an HTML file, a Markdown file of the HTML content, or the text content itself. Use file extensions (`.html`/`.md`/`.txt`) respectively.
    
    Options:
      -H, --headers TEXT                             HTTP headers in format "Key: Value" (can be used multiple times)
      --cookies TEXT                                 Cookies string in format "name1=value1;name2=value2"
      --timeout INTEGER                              Request timeout in seconds (default: 30)
      --proxy TEXT                                   Proxy URL in format "http://username:password@host:port"
      -s, --css-selector TEXT                        CSS selector to extract specific content from the page. It returns all matches.
      -p, --params TEXT                              Query parameters in format "key=value" (can be used multiple times)
      --follow-redirects / --no-follow-redirects     Whether to follow redirects (default: True)
      --verify / --no-verify                         Whether to verify SSL certificates (default: True)
      --impersonate TEXT                             Browser to impersonate (e.g., chrome, firefox).
      --stealthy-headers / --no-stealthy-headers     Use stealthy browser headers (default: True)
      --ai-targeted                                  Extract only main content and sanitize hidden elements for AI consumption (default: False)
      --help                                         Show this message and exit.
    
    ```
    Die Optionen funktionieren bei den anderen Anfragebefehlen genauso. Wir müssen sie also nicht erneut erklären.

2. **POST-Anfrage**

    ```bash
    scrapling extract post [URL] [OUTPUT_FILE] [OPTIONS]
    ```

    **Beispiele:**
    ```bash
    # Submit form data
    scrapling extract post "https://api.site.com/search" results.html --data "query=python&type=tutorial"
    
    # Send JSON data
    scrapling extract post "https://api.site.com" response.txt --json '{"username": "test", "action": "search"}'
    ```
    Zeigen Sie die verfügbaren Optionen mit `scrapling extract post --help` an:
    ```bash
    Usage: scrapling extract post [OPTIONS] URL OUTPUT_FILE
    
      Perform a POST request and save the content to a file.
    
      The output file path can be an HTML file, a Markdown file of the HTML content, or the text content itself. Use file extensions (`.html`/`.md`/`.txt`) respectively.
    
    Options:
      -d, --data TEXT                                Form data to include in the request body (as string, ex: "param1=value1&param2=value2")
      -j, --json TEXT                                JSON data to include in the request body (as string)
      -H, --headers TEXT                             HTTP headers in format "Key: Value" (can be used multiple times)
      --cookies TEXT                                 Cookies string in format "name1=value1;name2=value2"
      --timeout INTEGER                              Request timeout in seconds (default: 30)
      --proxy TEXT                                   Proxy URL in format "http://username:password@host:port"
      -s, --css-selector TEXT                        CSS selector to extract specific content from the page. It returns all matches.
      -p, --params TEXT                              Query parameters in format "key=value" (can be used multiple times)
      --follow-redirects / --no-follow-redirects     Whether to follow redirects (default: True)
      --verify / --no-verify                         Whether to verify SSL certificates (default: True)
      --impersonate TEXT                             Browser to impersonate (e.g., chrome, firefox).
      --stealthy-headers / --no-stealthy-headers     Use stealthy browser headers (default: True)
      --ai-targeted                                  Extract only main content and sanitize hidden elements for AI consumption (default: False)
      --help                                         Show this message and exit.
    
    ```

3. **PUT-Anfrage**

    ```bash
    scrapling extract put [URL] [OUTPUT_FILE] [OPTIONS]
    ```

    **Beispiele:**
    ```bash
    # Send data
    scrapling extract put "https://scrapling.requestcatcher.com/put" results.html --data "update=info" --impersonate "firefox"
    
    # Send JSON data
    scrapling extract put "https://scrapling.requestcatcher.com/put" response.txt --json '{"username": "test", "action": "search"}'
    ```
    Zeigen Sie die verfügbaren Optionen mit `scrapling extract put --help` an:
    ```bash
    Usage: scrapling extract put [OPTIONS] URL OUTPUT_FILE
    
      Perform a PUT request and save the content to a file.
    
      The output file path can be an HTML file, a Markdown file of the HTML content, or the text content itself. Use file extensions (`.html`/`.md`/`.txt`) respectively.
    
    Options:
      -d, --data TEXT                                Form data to include in the request body
      -j, --json TEXT                                JSON data to include in the request body (as string)
      -H, --headers TEXT                             HTTP headers in format "Key: Value" (can be used multiple times)
      --cookies TEXT                                 Cookies string in format "name1=value1;name2=value2"
      --timeout INTEGER                              Request timeout in seconds (default: 30)
      --proxy TEXT                                   Proxy URL in format "http://username:password@host:port"
      -s, --css-selector TEXT                        CSS selector to extract specific content from the page. It returns all matches.
      -p, --params TEXT                              Query parameters in format "key=value" (can be used multiple times)
      --follow-redirects / --no-follow-redirects     Whether to follow redirects (default: True)
      --verify / --no-verify                         Whether to verify SSL certificates (default: True)
      --impersonate TEXT                             Browser to impersonate (e.g., chrome, firefox).
      --stealthy-headers / --no-stealthy-headers     Use stealthy browser headers (default: True)
      --ai-targeted                                  Extract only main content and sanitize hidden elements for AI consumption (default: False)
      --help                                         Show this message and exit.
    ```

4. **DELETE-Anfrage**

    ```bash
    scrapling extract delete [URL] [OUTPUT_FILE] [OPTIONS]
    ```

    **Beispiele:**
    ```bash
    # Send data
    scrapling extract delete "https://scrapling.requestcatcher.com/delete" results.html
    
    # Send JSON data
    scrapling extract delete "https://scrapling.requestcatcher.com/" response.txt --impersonate "chrome"
    ```
    Zeigen Sie die verfügbaren Optionen mit `scrapling extract delete --help` an:
    ```bash
    Usage: scrapling extract delete [OPTIONS] URL OUTPUT_FILE
    
      Perform a DELETE request and save the content to a file.
    
      The output file path can be an HTML file, a Markdown file of the HTML content, or the text content itself. Use file extensions (`.html`/`.md`/`.txt`) respectively.
    
    Options:
      -H, --headers TEXT                             HTTP headers in format "Key: Value" (can be used multiple times)
      --cookies TEXT                                 Cookies string in format "name1=value1;name2=value2"
      --timeout INTEGER                              Request timeout in seconds (default: 30)
      --proxy TEXT                                   Proxy URL in format "http://username:password@host:port"
      -s, --css-selector TEXT                        CSS selector to extract specific content from the page. It returns all matches.
      -p, --params TEXT                              Query parameters in format "key=value" (can be used multiple times)
      --follow-redirects / --no-follow-redirects     Whether to follow redirects (default: True)
      --verify / --no-verify                         Whether to verify SSL certificates (default: True)
      --impersonate TEXT                             Browser to impersonate (e.g., chrome, firefox).
      --stealthy-headers / --no-stealthy-headers     Use stealthy browser headers (default: True)
      --ai-targeted                                  Extract only main content and sanitize hidden elements for AI consumption (default: False)
      --help                                         Show this message and exit.
    ```

### Seiten mit einem Browser abrufen {#browser-fetching}

Nutzen Sie `fetch` für JavaScript-Seiten, Browser-Automatisierung und geschützte Websites. Der Befehl verwendet `StealthyFetcher` mit allen verfügbaren Optionen gegen Erkennung.

```bash
scrapling extract fetch "https://scrapling.requestcatcher.com/" content.md --network-idle
scrapling extract fetch "https://scrapling.requestcatcher.com/" data.txt --wait-selector ".content-loaded"
scrapling extract fetch "https://scrapling.requestcatcher.com/" page.html --no-headless --disable-resources
scrapling extract fetch "https://nopecha.com/demo/cloudflare" data.txt --solve-cloudflare --css-selector "#padded_content a"
scrapling extract fetch "https://site.com" content.md --proxy "http://proxy-server:8080"
```

Mit `--pierce-shadow` können Sie Inhalte offener Shadow DOMs einbeziehen. Die Option ist standardmäßig ausgeschaltet. `--no-pierce-shadow` schaltet sie ausdrücklich aus. Im Abschnitt [Shadow DOM](../fetching/stealthy.md#shadow-dom) finden Sie Selektorbeispiele und Einschränkungen.

```bash
scrapling extract fetch "https://example.com" content.md --pierce-shadow
```

Mit `scrapling extract fetch --help` sehen Sie alle Optionen:

```text
Usage: scrapling extract fetch [OPTIONS] URL OUTPUT_FILE

  Use StealthyFetcher to fetch content with advanced stealth features.

Options:
  --headless / --no-headless                  Run browser in headless mode (default: True)
  --disable-resources / --enable-resources    Drop unnecessary resources for speed boost (default: False)
  --block-webrtc / --allow-webrtc             Block WebRTC entirely (default: False)
  --solve-cloudflare / --no-solve-cloudflare  Solve Cloudflare challenges (default: False)
  --allow-webgl / --block-webgl               Allow WebGL (default: True)
  --pierce-shadow / --no-pierce-shadow        Include open Shadow DOM content (default: False)
  --network-idle / --no-network-idle          Wait for network idle (default: False)
  --real-chrome/--no-real-chrome              If you have a Chrome browser installed on your device, enable this, and the Fetcher will launch an instance of your browser and use it. (default: False)
  --timeout INTEGER                           Timeout in milliseconds (default: 30000)
  --wait INTEGER                              Additional wait time in milliseconds after page load (default: 0)
  -s, --css-selector TEXT                     CSS selector to extract specific content from the page. It returns all matches.
  --wait-selector TEXT                        CSS selector to wait for before proceeding
  --hide-canvas / --show-canvas               Add noise to canvas operations (default: False)
  --locale TEXT                               Specify user locale. Defaults to the system default locale.
  --proxy TEXT                                Proxy URL in format "http://username:password@host:port"
  -H, --extra-headers TEXT                    Extra headers in format "Key: Value" (can be used multiple times)
  --dns-over-https / --no-dns-over-https   Route DNS through Cloudflare's DoH to prevent DNS leaks when using proxies (default: False)
  --block-ads / --no-block-ads               Block requests to known ad and tracker domains (default: False)
  --executable-path TEXT                      Path to a custom Chromium-compatible browser executable. Falls back to the SCRAPLING_EXECUTABLE_PATH environment variable when not set.
  --ai-targeted                              Extract only main content and sanitize hidden elements for AI consumption (default: False)
  --help                                      Show this message and exit.
```

## Wann Sie welchen Befehl verwenden sollten {#when-to-use-each-command}

Wenn Sie neu im Web Scraping sind, helfen Ihnen diese Regeln bei der Auswahl:

- Nutzen Sie **`get`** für einfache Websites, Blogs oder Nachrichtenartikel.
- Nutzen Sie **`fetch`** für JavaScript-Seiten, Browser-Automatisierung oder geschützte Websites, einschließlich Cloudflare.

## Rechtliche und ethische Hinweise {#legal-and-ethical-considerations}

⚠️ **Wichtige Regeln:**

- **robots.txt prüfen**: Öffnen Sie `https://website.com/robots.txt`, um die Crawling-Regeln zu lesen.
- **Anfragelimits beachten**: Überlasten Sie Server nicht mit Anfragen.
- **Nutzungsbedingungen**: Lesen und beachten Sie die Bedingungen der Website.
- **Urheberrecht**: Achten Sie die Rechte am geistigen Eigentum.
- **Datenschutz**: Beachten Sie die Gesetze zum Schutz personenbezogener Daten.
- **Geschäftliche Nutzung**: Stellen Sie sicher, dass Sie die Daten geschäftlich nutzen dürfen.

---

*Viel Erfolg beim Scraping! Beachten Sie die Regeln der Websites und alle geltenden Gesetze und Vorschriften.*
