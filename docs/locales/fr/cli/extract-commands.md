---
title: "Enregistrer des pages en Markdown, HTML ou texte depuis la CLI"
description: "Utilisez scrapling extract pour enregistrer les résultats HTTP ou du navigateur. Filtrez le contenu avec CSS, ajustez les requêtes et choisissez le format de sortie."
---

# Guide de la commande d’extraction de Scrapling {#scrapling-extract-command-guide}

**Extrayez des données web depuis le terminal sans programmer !**

La commande `scrapling extract` permet de télécharger et d’extraire le contenu de sites directement depuis le terminal, sans écrire de code. Elle est utile aux débutants, aux chercheurs et à toute personne qui veut extraire rapidement des données web.

!!! success "Avant de commencer"

    1. Lisez la page sur les [bases des fetchers](../fetching/choosing.md) pour comprendre l’[objet Response](../fetching/choosing.md#response-object) et choisir un fetcher.
    2. Lisez la page sur la [sélection d’éléments](../parsing/selection.md) pour apprendre à trouver et extraire des éléments d’un objet [Selector](../parsing/main_classes.md#selector)/[Response](../fetching/choosing.md#response-object).
    3. Lisez la page des [classes principales](../parsing/main_classes.md) pour connaître les propriétés et méthodes héritées par [Response](../fetching/choosing.md#response-object) de [Selector](../parsing/main_classes.md#selector).
    4. Lisez au moins une page de la section des fetchers pour les requêtes que vous utiliserez ici : [requêtes HTTP](../fetching/static.md) ou [récupération avec un navigateur](../fetching/stealthy.md).

## Qu’est-ce que le groupe de commandes Extract ? {#what-is-the-extract-command-group}

C’est un ensemble d’outils simples pour le terminal qui permet de :

- **Télécharger des pages web** et enregistrer leur contenu dans des fichiers.
- **Convertir le HTML dans des formats faciles à lire**, comme Markdown, le garder en HTML ou extraire seulement le texte de la page.
- **Utiliser vos propres sélecteurs CSS** pour extraire certaines parties de la page.
- **Envoyer des requêtes HTTP et récupérer des pages avec un navigateur**.
- **Régler presque toutes les options** disponibles dans le code, comme les en-têtes, les cookies et les proxies, aussi depuis la ligne de commande.

!!! tip "Mode pour l’IA"

    Toutes les commandes d’extraction acceptent l’option `--ai-targeted`. Lorsqu’elle est activée, seul le contenu principal du corps de la page est extrait. Elle supprime aussi les balises sans texte utile (script, style, noscript, svg), les éléments cachés qui pourraient servir à injecter des instructions (éléments masqués par des styles en ligne, aria-hidden, slots cachés et balises template), les caractères Unicode de largeur nulle et les commentaires HTML. Avec la commande de navigateur (`fetch`), elle active aussi le blocage des publicités. Ce mode est utile lorsque le résultat est destiné à un modèle d’IA.

## Démarrage rapide {#quick-start}

- **Télécharger une page**

    Téléchargez le contenu d’une page sous forme de texte propre et lisible :
    ```bash
    scrapling extract get "https://example.com" page_content.txt
    ```
    Cette commande envoie une requête HTTP GET et enregistre le texte de la page dans `page_content.txt`.

- **Enregistrer dans d’autres formats**

    Choisissez le format de sortie en changeant l’extension du fichier :
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

- **Extraire un contenu précis**

    Toutes les commandes peuvent utiliser des sélecteurs CSS pour extraire certaines parties de la page avec `--css-selector` ou `-s`, comme dans les exemples ci-dessous.

## Commandes disponibles {#available-commands}

Exécutez `scrapling extract --help` pour afficher cette liste de commandes :
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

Nous allons détailler chacune d’elles.

### Requêtes HTTP {#http-requests}

1. **Requête GET**

    La commande la plus courante pour télécharger le contenu d’un site :

    ```bash
    scrapling extract get [URL] [OUTPUT_FILE] [OPTIONS]
    ```

    **Exemples :**
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
    Consultez les options avec `scrapling extract get --help` :
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
    Ces options fonctionnent de la même façon pour les autres commandes de requête. Il n’est donc pas nécessaire de répéter leur explication.

2. **Requête POST**

    ```bash
    scrapling extract post [URL] [OUTPUT_FILE] [OPTIONS]
    ```

    **Exemples :**
    ```bash
    # Submit form data
    scrapling extract post "https://api.site.com/search" results.html --data "query=python&type=tutorial"
    
    # Send JSON data
    scrapling extract post "https://api.site.com" response.txt --json '{"username": "test", "action": "search"}'
    ```
    Consultez les options avec `scrapling extract post --help` :
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

3. **Requête PUT**

    ```bash
    scrapling extract put [URL] [OUTPUT_FILE] [OPTIONS]
    ```

    **Exemples :**
    ```bash
    # Send data
    scrapling extract put "https://scrapling.requestcatcher.com/put" results.html --data "update=info" --impersonate "firefox"
    
    # Send JSON data
    scrapling extract put "https://scrapling.requestcatcher.com/put" response.txt --json '{"username": "test", "action": "search"}'
    ```
    Consultez les options avec `scrapling extract put --help` :
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

4. **Requête DELETE**

    ```bash
    scrapling extract delete [URL] [OUTPUT_FILE] [OPTIONS]
    ```

    **Exemples :**
    ```bash
    # Send data
    scrapling extract delete "https://scrapling.requestcatcher.com/delete" results.html
    
    # Send JSON data
    scrapling extract delete "https://scrapling.requestcatcher.com/" response.txt --impersonate "chrome"
    ```
    Consultez les options avec `scrapling extract delete --help` :
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

### Récupérer des pages avec un navigateur {#browser-fetching}

Utilisez `fetch` pour les pages JavaScript, l’automatisation du navigateur et les sites protégés. Cette commande exécute `StealthyFetcher` avec toutes les options disponibles pour masquer l’automatisation.

```bash
scrapling extract fetch "https://scrapling.requestcatcher.com/" content.md --network-idle
scrapling extract fetch "https://scrapling.requestcatcher.com/" data.txt --wait-selector ".content-loaded"
scrapling extract fetch "https://scrapling.requestcatcher.com/" page.html --no-headless --disable-resources
scrapling extract fetch "https://nopecha.com/demo/cloudflare" data.txt --solve-cloudflare --css-selector "#padded_content a"
scrapling extract fetch "https://site.com" content.md --proxy "http://proxy-server:8080"
```

Utilisez `--pierce-shadow` pour inclure le contenu des Shadow DOM ouverts. L’option est désactivée par défaut ; `--no-pierce-shadow` la désactive explicitement. Consultez [Shadow DOM](../fetching/stealthy.md#shadow-dom) pour voir des exemples de sélecteurs et leurs limites.

```bash
scrapling extract fetch "https://example.com" content.md --pierce-shadow
```

Exécutez `scrapling extract fetch --help` pour afficher toutes les options :

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

## Quand utiliser chaque commande {#when-to-use-each-command}

Si vous débutez dans l’extraction de données web, ces règles vous aideront à choisir :

- Utilisez **`get`** pour les sites simples, les blogs ou les articles de presse.
- Utilisez **`fetch`** pour les pages JavaScript, l’automatisation du navigateur ou les sites protégés, y compris ceux qui utilisent Cloudflare.

## Aspects juridiques et éthiques {#legal-and-ethical-considerations}

⚠️ **Consignes importantes :**

- **Consultez robots.txt** : Ouvrez `https://website.com/robots.txt` pour voir les règles d’exploration.
- **Respectez les limites de requêtes** : Ne surchargez pas les serveurs.
- **Conditions d’utilisation** : Lisez et respectez les conditions du site.
- **Droits d’auteur** : Respectez les droits de propriété intellectuelle.
- **Vie privée** : Tenez compte des lois sur la protection des données personnelles.
- **Usage commercial** : Assurez-vous d’avoir l’autorisation d’utiliser les données à des fins commerciales.

---

*Bonne extraction ! Pensez à respecter les règles des sites et toutes les lois et réglementations applicables.*
