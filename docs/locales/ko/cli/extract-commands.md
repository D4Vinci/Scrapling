---
title: "CLI로 웹페이지를 Markdown, HTML, 텍스트로 저장하기"
description: "scrapling extract로 HTTP나 브라우저에서 가져온 결과를 저장하세요. CSS로 내용을 걸러 내고, 요청 옵션과 출력 형식을 선택할 수 있습니다."
---

# Scrapling 추출 명령 안내 {#scrapling-extract-command-guide}

**프로그래밍 없이 터미널에서 웹 스크래핑을 할 수 있습니다!**

`scrapling extract` 명령은 코드를 작성하지 않고도 터미널에서 웹사이트의 내용을 다운로드하고 추출합니다. 초보자, 연구자, 웹 데이터를 빠르게 가져와야 하는 사람에게 적합합니다.

!!! success "시작하기 전에"

    1. [Fetcher 기초](../fetching/choosing.md)를 읽고 [Response 객체](../fetching/choosing.md#response-object)와 Fetcher 선택 방법을 이해하세요.
    2. [요소 찾기](../parsing/selection.md)를 읽고 [Selector](../parsing/main_classes.md#selector)/[Response](../fetching/choosing.md#response-object)에서 요소를 찾고 추출하는 방법을 이해하세요.
    3. [주요 클래스](../parsing/main_classes.md)를 읽고 [Response](../fetching/choosing.md#response-object)가 [Selector](../parsing/main_classes.md#selector)에서 물려받는 속성과 메서드를 알아두세요.
    4. 사용할 Fetcher에 맞게 [HTTP 요청](../fetching/static.md) 또는 [브라우저로 가져오기](../fetching/stealthy.md) 중 하나 이상을 읽으세요.


## extract 명령 그룹이란? {#what-is-the-extract-command-group}

extract는 다음 기능을 제공하는 간단한 터미널 도구 모음입니다.

- **웹페이지를 다운로드**하고 내용을 파일에 저장합니다.
- **HTML을 읽기 쉬운 형식으로 변환**합니다. Markdown으로 바꾸거나, HTML로 유지하거나, 텍스트만 추출할 수 있습니다.
- **직접 지정한 CSS 선택자**로 페이지의 특정 부분을 추출합니다.
- **HTTP 요청과 브라우저를 통한 가져오기**를 지원합니다.
- **세부 설정이 가능합니다.** 헤더, 쿠키, 프록시 등을 지정할 수 있습니다. 코드에서 사용할 수 있는 거의 모든 옵션을 명령줄에서도 사용할 수 있습니다.

!!! tip "AI용 모드"

    모든 추출 명령은 `--ai-targeted` 플래그를 지원합니다. 켜면 본문만 추출하고 불필요한 태그(script, style, noscript, svg)를 제거합니다. 프롬프트 인젝션에 쓰일 수 있는 숨겨진 요소(인라인 스타일로 숨긴 요소, aria-hidden, 숨겨진 슬롯, template 태그), 너비가 0인 Unicode 문자, HTML 주석도 제거합니다. 브라우저 명령(`fetch`)에서는 광고 차단도 자동으로 켭니다. 결과를 AI 모델에 전달할 때 적합합니다.

## 빠른 시작 {#quick-start}

- **기본 페이지 다운로드**

    웹사이트 내용을 깔끔하고 읽기 쉬운 텍스트로 다운로드합니다.
    ```bash
    scrapling extract get "https://example.com" page_content.txt
    ```
    HTTP GET 요청을 보내고 페이지 텍스트를 `page_content.txt`에 저장합니다.

- **다른 형식으로 저장하기**

    파일 확장자를 바꿔 출력 형식을 선택합니다.
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

- **특정 내용 추출하기**

    모든 명령에서 `--css-selector` 또는 `-s`로 CSS 선택자를 전달해 페이지의 특정 부분을 추출할 수 있습니다. 아래 예제에서 사용법을 확인할 수 있습니다.

## 사용할 수 있는 명령 {#available-commands}

`scrapling extract --help`를 실행하면 다음 명령 목록을 확인할 수 있습니다.
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

아래에서 각 명령을 자세히 설명합니다.

### HTTP 요청 {#http-requests}

1. **GET 요청**

    웹사이트 내용을 다운로드할 때 가장 많이 쓰는 명령입니다.
    
    ```bash
    scrapling extract get [URL] [OUTPUT_FILE] [OPTIONS]
    ```
    
    **예제:**
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
    `scrapling extract get --help`로 사용할 수 있는 옵션을 확인합니다.
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
    다른 요청 명령에서도 옵션은 같은 방식으로 작동하므로 설명을 반복하지 않겠습니다.

2. **POST 요청**
    
    ```bash
    scrapling extract post [URL] [OUTPUT_FILE] [OPTIONS]
    ```
    
    **예제:**
    ```bash
    # Submit form data
    scrapling extract post "https://api.site.com/search" results.html --data "query=python&type=tutorial"
    
    # Send JSON data
    scrapling extract post "https://api.site.com" response.txt --json '{"username": "test", "action": "search"}'
    ```
    `scrapling extract post --help`로 사용할 수 있는 옵션을 확인합니다.
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

3. **PUT 요청**
    
    ```bash
    scrapling extract put [URL] [OUTPUT_FILE] [OPTIONS]
    ```
    
    **예제:**
    ```bash
    # Send data
    scrapling extract put "https://scrapling.requestcatcher.com/put" results.html --data "update=info" --impersonate "firefox"
    
    # Send JSON data
    scrapling extract put "https://scrapling.requestcatcher.com/put" response.txt --json '{"username": "test", "action": "search"}'
    ```
    `scrapling extract put --help`로 사용할 수 있는 옵션을 확인합니다.
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

4. **DELETE 요청**
    
    ```bash
    scrapling extract delete [URL] [OUTPUT_FILE] [OPTIONS]
    ```
    
    **예제:**
    ```bash
    # Send data
    scrapling extract delete "https://scrapling.requestcatcher.com/delete" results.html
    
    # Send JSON data
    scrapling extract delete "https://scrapling.requestcatcher.com/" response.txt --impersonate "chrome"
    ```
    `scrapling extract delete --help`로 사용할 수 있는 옵션을 확인합니다.
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

### 브라우저로 가져오기 {#browser-fetching}

JavaScript 페이지, 브라우저 자동화, 보호된 사이트에는 `fetch`를 사용하세요. `StealthyFetcher`를 실행하며 모든 스텔스 옵션을 사용할 수 있습니다.

```bash
scrapling extract fetch "https://scrapling.requestcatcher.com/" content.md --network-idle
scrapling extract fetch "https://scrapling.requestcatcher.com/" data.txt --wait-selector ".content-loaded"
scrapling extract fetch "https://scrapling.requestcatcher.com/" page.html --no-headless --disable-resources
scrapling extract fetch "https://nopecha.com/demo/cloudflare" data.txt --solve-cloudflare --css-selector "#padded_content a"
scrapling extract fetch "https://site.com" content.md --proxy "http://proxy-server:8080"
```

열린 Shadow DOM의 내용을 포함하려면 `--pierce-shadow`를 사용하세요. 기본으로 꺼져 있으며, `--no-pierce-shadow`로 명시적으로 끌 수도 있습니다. 선택자 예제와 제한 사항은 [Shadow DOM](../fetching/stealthy.md#shadow-dom)을 참고하세요.

```bash
scrapling extract fetch "https://example.com" content.md --pierce-shadow
```

`scrapling extract fetch --help`로 모든 옵션을 확인하세요.

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

## 명령 선택하기 {#when-to-use-each-command}

웹 스크래핑에 익숙하지 않아 어떤 명령을 쓸지 고민된다면 다음 기준으로 선택하세요.

- 간단한 사이트, 블로그, 뉴스 기사에는 **`get`**을 사용합니다.
- JavaScript 페이지, 브라우저 자동화, Cloudflare 등으로 보호된 사이트에는 **`fetch`**를 사용합니다.

## 법적·윤리적 고려 사항 {#legal-and-ethical-considerations}

⚠️ **중요한 지침:**

- **robots.txt 확인**: `https://website.com/robots.txt`에서 수집 규칙을 확인하세요.
- **요청 빈도 제한 준수**: 서버에 지나치게 많은 요청을 보내지 마세요.
- **이용 약관**: 사이트의 약관을 읽고 지키세요.
- **저작권**: 지식재산권을 존중하세요.
- **개인정보**: 개인정보 보호법을 고려하세요.
- **상업적 이용**: 업무 목적에 필요한 허가가 있는지 확인하세요.

---

*즐겁게 스크래핑하세요! 사이트 정책과 적용되는 법률 및 규정을 항상 지켜 주세요.*
