---
title: "Сохранение веб-страниц в Markdown, HTML или текст из CLI"
description: "Используйте scrapling extract для сохранения результатов HTTP-запросов или браузера. Фильтруйте содержимое с помощью CSS, задавайте параметры запросов и выбирайте формат вывода."
---

# Команды извлечения Scrapling {#scrapling-extract-command-guide}

**Собирайте данные с сайтов через терминал без программирования!**

Команда `scrapling extract` позволяет скачивать и извлекать содержимое сайтов прямо из терминала, не написав ни строки кода. Она подходит новичкам, исследователям и всем, кому нужно быстро получить данные из интернета.

!!! success "Перед началом"

    1. Прочитайте [основы Fetcher](../fetching/choosing.md), чтобы понять, что такое [объект Response](../fetching/choosing.md#response-object) и какой Fetcher выбрать.
    2. Прочитайте [поиск элементов](../parsing/selection.md), чтобы научиться находить и извлекать элементы из [Selector](../parsing/main_classes.md#selector)/[Response](../fetching/choosing.md#response-object).
    3. Прочитайте [основные классы](../parsing/main_classes.md), чтобы узнать, какие свойства и методы [Response](../fetching/choosing.md#response-object) наследует от [Selector](../parsing/main_classes.md#selector).
    4. Прочитайте хотя бы одну страницу о Fetcher, который будете использовать: [HTTP-запросы](../fetching/static.md) или [загрузка через браузер](../fetching/stealthy.md).


## Что такое группа команд extract {#what-is-the-extract-command-group}

Это набор простых инструментов для терминала, который позволяет:

- **Скачивать веб-страницы** и сохранять содержимое в файлы.
- **Преобразовывать HTML в удобные форматы**, например Markdown, сохранять исходный HTML или извлекать только текст страницы.
- **Использовать свои CSS-селекторы**, чтобы извлекать отдельные части страницы.
- **Отправлять HTTP-запросы и загружать страницы через браузер**.
- **Подробно настраивать работу**: задавать заголовки, Cookie, прокси и другие параметры. Почти все параметры, доступные в коде, есть и в командной строке.

!!! tip "Режим для ИИ"

    Все команды извлечения поддерживают флаг `--ai-targeted`. Он оставляет только основное содержимое страницы, удаляет служебные теги (script, style, noscript, svg), скрытые элементы, которые могут содержать инструкции для ИИ (элементы со встроенными скрывающими стилями, aria-hidden, скрытые слоты, template), символы Unicode нулевой ширины и HTML-комментарии. В команде браузера (`fetch`) он также автоматически включает блокировку рекламы. Этот режим подходит для передачи результата модели ИИ.

## Быстрый старт {#quick-start}

- **Обычное скачивание страницы**

    Скачайте содержимое сайта в виде чистого, удобного для чтения текста:
    ```bash
    scrapling extract get "https://example.com" page_content.txt
    ```
    Команда отправит HTTP GET-запрос и сохранит текст страницы в `page_content.txt`.

- **Сохранение в разных форматах**

    Выберите формат вывода, изменив расширение файла:
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

- **Извлечение нужного содержимого**

    Во всех командах можно передать CSS-селектор через `--css-selector` или `-s`, чтобы извлечь отдельную часть страницы. Ниже приведены примеры.

## Доступные команды {#available-commands}

Команда `scrapling extract --help` показывает следующий список:
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

Далее разберём каждую команду подробнее.

### HTTP-запросы {#http-requests}

1. **GET-запрос**

    Самая распространённая команда для скачивания содержимого сайта:
    
    ```bash
    scrapling extract get [URL] [OUTPUT_FILE] [OPTIONS]
    ```
    
    **Примеры:**
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
    Чтобы увидеть доступные параметры, выполните `scrapling extract get --help`:
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
    В остальных командах запросов параметры работают так же, поэтому повторять описание не будем.

2. **POST-запрос**
    
    ```bash
    scrapling extract post [URL] [OUTPUT_FILE] [OPTIONS]
    ```
    
    **Примеры:**
    ```bash
    # Submit form data
    scrapling extract post "https://api.site.com/search" results.html --data "query=python&type=tutorial"
    
    # Send JSON data
    scrapling extract post "https://api.site.com" response.txt --json '{"username": "test", "action": "search"}'
    ```
    Чтобы увидеть доступные параметры, выполните `scrapling extract post --help`:
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

3. **PUT-запрос**
    
    ```bash
    scrapling extract put [URL] [OUTPUT_FILE] [OPTIONS]
    ```
    
    **Примеры:**
    ```bash
    # Send data
    scrapling extract put "https://scrapling.requestcatcher.com/put" results.html --data "update=info" --impersonate "firefox"
    
    # Send JSON data
    scrapling extract put "https://scrapling.requestcatcher.com/put" response.txt --json '{"username": "test", "action": "search"}'
    ```
    Чтобы увидеть доступные параметры, выполните `scrapling extract put --help`:
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

4. **DELETE-запрос**
    
    ```bash
    scrapling extract delete [URL] [OUTPUT_FILE] [OPTIONS]
    ```
    
    **Примеры:**
    ```bash
    # Send data
    scrapling extract delete "https://scrapling.requestcatcher.com/delete" results.html
    
    # Send JSON data
    scrapling extract delete "https://scrapling.requestcatcher.com/" response.txt --impersonate "chrome"
    ```
    Чтобы увидеть доступные параметры, выполните `scrapling extract delete --help`:
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

### Загрузка через браузер {#browser-fetching}

Используйте `fetch` для страниц с JavaScript, автоматизации браузера и защищённых сайтов. Команда запускает `StealthyFetcher` со всеми доступными параметрами скрытности.

```bash
scrapling extract fetch "https://scrapling.requestcatcher.com/" content.md --network-idle
scrapling extract fetch "https://scrapling.requestcatcher.com/" data.txt --wait-selector ".content-loaded"
scrapling extract fetch "https://scrapling.requestcatcher.com/" page.html --no-headless --disable-resources
scrapling extract fetch "https://nopecha.com/demo/cloudflare" data.txt --solve-cloudflare --css-selector "#padded_content a"
scrapling extract fetch "https://site.com" content.md --proxy "http://proxy-server:8080"
```

Чтобы включить содержимое открытого Shadow DOM, используйте `--pierce-shadow`. По умолчанию эта возможность выключена; `--no-pierce-shadow` явно отключает её. Примеры селекторов и ограничения описаны в разделе [Shadow DOM](../fetching/stealthy.md#shadow-dom).

```bash
scrapling extract fetch "https://example.com" content.md --pierce-shadow
```

Все параметры можно посмотреть командой `scrapling extract fetch --help`:

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

## Как выбрать команду {#when-to-use-each-command}

Если вы пока не уверены, какую команду выбрать, используйте это простое правило:

- **`get`** подходит для простых сайтов, блогов и новостных статей.
- **`fetch`** подходит для страниц с JavaScript, автоматизации браузера и защищённых сайтов, в том числе с Cloudflare.

## Правовые и этические вопросы {#legal-and-ethical-considerations}

⚠️ **Важные правила:**

- **Проверяйте robots.txt**: откройте `https://website.com/robots.txt`, чтобы узнать правила сбора данных.
- **Соблюдайте ограничения частоты**: не перегружайте сервер запросами.
- **Условия использования**: прочитайте правила сайта и следуйте им.
- **Авторское право**: уважайте права на интеллектуальную собственность.
- **Конфиденциальность**: учитывайте законы о защите персональных данных.
- **Коммерческое использование**: убедитесь, что у вас есть нужное разрешение для деловых целей.

---

*Удачного сбора данных! Всегда уважайте правила сайтов и соблюдайте применимые законы и нормы.*
