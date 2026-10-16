---
title: "Salve páginas como Markdown, HTML ou texto pela CLI"
description: "Use scrapling extract para salvar resultados de solicitações HTTP ou do navegador. Filtre o conteúdo com CSS, ajuste as solicitações e escolha o formato de saída."
---

# Guia do comando de extração do Scrapling {#scrapling-extract-command-guide}

**Extraia dados web pelo terminal sem precisar programar!**

O comando `scrapling extract` permite baixar e extrair conteúdo de sites diretamente pelo terminal, sem escrever código. É útil para iniciantes, pesquisadores e qualquer pessoa que precise extrair dados web com rapidez.

!!! success "Antes de começar"

    1. Leia a página de [conceitos básicos dos fetchers](../fetching/choosing.md) para entender o que é o [objeto Response](../fetching/choosing.md#response-object) e qual fetcher usar.
    2. Leia a página de [seleção de elementos](../parsing/selection.md) para aprender a buscar e extrair elementos de um objeto [Selector](../parsing/main_classes.md#selector)/[Response](../fetching/choosing.md#response-object).
    3. Leia a página de [classes principais](../parsing/main_classes.md) para conhecer as propriedades e os métodos que a classe [Response](../fetching/choosing.md#response-object) herda de [Selector](../parsing/main_classes.md#selector).
    4. Leia pelo menos uma página da seção de fetchers para as solicitações que você usará aqui: [solicitações HTTP](../fetching/static.md) ou [obtenção com navegador](../fetching/stealthy.md).

## O que é o grupo de comandos Extract? {#what-is-the-extract-command-group}

É um conjunto de ferramentas simples de terminal que permite:

- **Baixar páginas web** e salvar o conteúdo em arquivos.
- **Converter HTML em formatos fáceis de ler**, como Markdown, manter o HTML ou extrair apenas o texto da página.
- **Usar seletores CSS próprios** para extrair partes específicas da página.
- **Fazer solicitações HTTP e obter páginas com navegadores**.
- **Ajustar quase todas as opções** disponíveis no código, como cabeçalhos, cookies e proxies, também pela linha de comando.

!!! tip "Modo para IA"

    Todos os comandos de extração aceitam a opção `--ai-targeted`. Quando ativada, ela extrai apenas o conteúdo principal do corpo da página. Também remove tags que não contribuem com texto (script, style, noscript, svg), elementos ocultos que poderiam ser usados para injetar instruções (elementos ocultos por estilos inline, aria-hidden, slots ocultos e tags template), caracteres Unicode de largura zero e comentários HTML. No comando de navegador (`fetch`), também ativa o bloqueio de anúncios. Esse modo é útil quando você vai enviar o resultado a um modelo de IA.

## Início rápido {#quick-start}

- **Baixar uma página**

    Baixe o conteúdo de uma página como texto limpo e fácil de ler:
    ```bash
    scrapling extract get "https://example.com" page_content.txt
    ```
    Esse comando faz uma solicitação HTTP GET e salva o texto da página em `page_content.txt`.

- **Salvar em outros formatos**

    Escolha o formato de saída mudando a extensão do arquivo:
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

- **Extrair conteúdo específico**

    Todos os comandos podem usar seletores CSS para extrair partes da página com `--css-selector` ou `-s`, como mostram os exemplos abaixo.

## Comandos disponíveis {#available-commands}

Execute `scrapling extract --help` para ver esta lista de comandos:
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

A seguir, vamos explicar cada comando.

### Solicitações HTTP {#http-requests}

1. **Solicitação GET**

    O comando mais comum para baixar conteúdo de sites:

    ```bash
    scrapling extract get [URL] [OUTPUT_FILE] [OPTIONS]
    ```

    **Exemplos:**
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
    Consulte as opções com `scrapling extract get --help`:
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
    Essas opções funcionam da mesma forma nos outros comandos de solicitação, então não é preciso repetir a explicação.

2. **Solicitação POST**

    ```bash
    scrapling extract post [URL] [OUTPUT_FILE] [OPTIONS]
    ```

    **Exemplos:**
    ```bash
    # Submit form data
    scrapling extract post "https://api.site.com/search" results.html --data "query=python&type=tutorial"
    
    # Send JSON data
    scrapling extract post "https://api.site.com" response.txt --json '{"username": "test", "action": "search"}'
    ```
    Consulte as opções com `scrapling extract post --help`:
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

3. **Solicitação PUT**

    ```bash
    scrapling extract put [URL] [OUTPUT_FILE] [OPTIONS]
    ```

    **Exemplos:**
    ```bash
    # Send data
    scrapling extract put "https://scrapling.requestcatcher.com/put" results.html --data "update=info" --impersonate "firefox"
    
    # Send JSON data
    scrapling extract put "https://scrapling.requestcatcher.com/put" response.txt --json '{"username": "test", "action": "search"}'
    ```
    Consulte as opções com `scrapling extract put --help`:
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

4. **Solicitação DELETE**

    ```bash
    scrapling extract delete [URL] [OUTPUT_FILE] [OPTIONS]
    ```

    **Exemplos:**
    ```bash
    # Send data
    scrapling extract delete "https://scrapling.requestcatcher.com/delete" results.html
    
    # Send JSON data
    scrapling extract delete "https://scrapling.requestcatcher.com/" response.txt --impersonate "chrome"
    ```
    Consulte as opções com `scrapling extract delete --help`:
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

### Obter páginas com um navegador {#browser-fetching}

Use `fetch` para páginas com JavaScript, automação do navegador e sites protegidos. Ele executa `StealthyFetcher` com todas as opções para ocultar a automação disponíveis.

```bash
scrapling extract fetch "https://scrapling.requestcatcher.com/" content.md --network-idle
scrapling extract fetch "https://scrapling.requestcatcher.com/" data.txt --wait-selector ".content-loaded"
scrapling extract fetch "https://scrapling.requestcatcher.com/" page.html --no-headless --disable-resources
scrapling extract fetch "https://nopecha.com/demo/cloudflare" data.txt --solve-cloudflare --css-selector "#padded_content a"
scrapling extract fetch "https://site.com" content.md --proxy "http://proxy-server:8080"
```

Use `--pierce-shadow` para incluir conteúdo de Shadow DOM aberto. A opção fica desativada por padrão; `--no-pierce-shadow` a desativa de forma explícita. Consulte [Shadow DOM](../fetching/stealthy.md#shadow-dom) para ver exemplos de seletores e seus limites.

```bash
scrapling extract fetch "https://example.com" content.md --pierce-shadow
```

Execute `scrapling extract fetch --help` para ver todas as opções:

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

## Quando usar cada comando {#when-to-use-each-command}

Se você ainda não tem experiência com extração de dados web, estas regras ajudam a escolher:

- Use **`get`** para sites simples, blogs ou notícias.
- Use **`fetch`** para páginas com JavaScript, automação do navegador ou sites protegidos, incluindo os que usam Cloudflare.

## Questões legais e éticas {#legal-and-ethical-considerations}

⚠️ **Orientações importantes:**

- **Consulte o robots.txt**: Visite `https://website.com/robots.txt` para ver as regras de rastreamento.
- **Respeite os limites de solicitações**: Não sobrecarregue os servidores.
- **Termos de serviço**: Leia e siga os termos do site.
- **Direitos autorais**: Respeite os direitos de propriedade intelectual.
- **Privacidade**: Leve em conta as leis de proteção de dados pessoais.
- **Uso comercial**: Garanta que você tem permissão para usar os dados com fins comerciais.

---

*Boa extração! Lembre-se de respeitar as políticas dos sites e cumprir todas as leis e normas aplicáveis.*
