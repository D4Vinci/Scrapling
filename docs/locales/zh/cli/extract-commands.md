---
title: "通过 CLI 将网页保存为 Markdown、HTML 或文本"
description: "使用 scrapling extract 保存 HTTP 请求或浏览器获取的结果。用 CSS 筛选内容，设置请求选项，并选择输出格式。"
---

# Scrapling 提取命令指南 {#scrapling-extract-command-guide}

**无需编程，直接在终端中抓取网页！**

`scrapling extract` 命令可以直接在终端中下载和提取网站内容，无需编写代码。它适合初学者、研究人员，以及需要快速获取网页数据的人。

!!! success "前置知识"

    1. 阅读 [Fetcher 基础](../fetching/choosing.md)，了解 [Response 对象](../fetching/choosing.md#response-object)并选择合适的 Fetcher。
    2. 阅读[元素查询](../parsing/selection.md)，学习如何从 [Selector](../parsing/main_classes.md#selector)/[Response](../fetching/choosing.md#response-object) 对象中查找和提取元素。
    3. 阅读[主要类](../parsing/main_classes.md)，了解 [Response](../fetching/choosing.md#response-object) 从 [Selector](../parsing/main_classes.md#selector) 继承了哪些属性和方法。
    4. 至少阅读 Fetcher 部分的一篇相关指南：[HTTP 请求](../fetching/static.md)或[通过浏览器获取页面](../fetching/stealthy.md)。

## Extract 命令组是什么？ {#what-is-the-extract-command-group}

这是一组简单的终端工具，可以：

- **下载网页**，并将内容保存到文件。
- **将 HTML 转为易读的格式**，例如 Markdown，也可以保留 HTML 或只提取页面文本。
- **使用自定义 CSS 选择器**，提取页面的特定部分。
- **发送 HTTP 请求或通过浏览器获取页面**。
- **调整几乎所有选项**，包括请求头、Cookie 和代理。代码中可用的大部分选项也能在命令行中使用。

!!! tip "面向 AI 的模式"

    所有提取命令都支持 `--ai-targeted` 选项。启用后，只提取页面正文中的主要内容，并移除无用标签（script、style、noscript、svg）、可能用于提示词注入的隐藏元素（通过内联样式隐藏的元素、aria-hidden、隐藏的 slot 和 template 标签）、Unicode 零宽字符和 HTML 注释。对于浏览器命令（`fetch`），它还会自动启用广告拦截。输出要交给 AI 模型时，适合使用此模式。

## 快速开始 {#quick-start}

- **下载网页**

    将网页内容下载为干净、易读的文本：
    ```bash
    scrapling extract get "https://example.com" page_content.txt
    ```
    该命令发送 HTTP GET 请求，并把页面文本保存到 `page_content.txt`。

- **保存为其他格式**

    修改文件扩展名即可选择输出格式：
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

- **提取指定内容**

    所有命令都可以通过 `--css-selector` 或 `-s` 使用 CSS 选择器，提取页面的特定部分。下面的示例会展示用法。

## 可用命令 {#available-commands}

运行 `scrapling extract --help`，即可看到以下命令列表：
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

下面逐一介绍。

### HTTP 请求 {#http-requests}

1. **GET 请求**

    最常用的网页内容下载命令：

    ```bash
    scrapling extract get [URL] [OUTPUT_FILE] [OPTIONS]
    ```

    **示例：**
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
    用 `scrapling extract get --help` 查看可用选项：
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
    这些选项在其他请求命令中的用法相同，因此不再重复说明。

2. **POST 请求**

    ```bash
    scrapling extract post [URL] [OUTPUT_FILE] [OPTIONS]
    ```

    **示例：**
    ```bash
    # Submit form data
    scrapling extract post "https://api.site.com/search" results.html --data "query=python&type=tutorial"
    
    # Send JSON data
    scrapling extract post "https://api.site.com" response.txt --json '{"username": "test", "action": "search"}'
    ```
    用 `scrapling extract post --help` 查看可用选项：
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

3. **PUT 请求**

    ```bash
    scrapling extract put [URL] [OUTPUT_FILE] [OPTIONS]
    ```

    **示例：**
    ```bash
    # Send data
    scrapling extract put "https://scrapling.requestcatcher.com/put" results.html --data "update=info" --impersonate "firefox"
    
    # Send JSON data
    scrapling extract put "https://scrapling.requestcatcher.com/put" response.txt --json '{"username": "test", "action": "search"}'
    ```
    用 `scrapling extract put --help` 查看可用选项：
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

4. **DELETE 请求**

    ```bash
    scrapling extract delete [URL] [OUTPUT_FILE] [OPTIONS]
    ```

    **示例：**
    ```bash
    # Send data
    scrapling extract delete "https://scrapling.requestcatcher.com/delete" results.html
    
    # Send JSON data
    scrapling extract delete "https://scrapling.requestcatcher.com/" response.txt --impersonate "chrome"
    ```
    用 `scrapling extract delete --help` 查看可用选项：
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

### 通过浏览器获取页面 {#browser-fetching}

对于 JavaScript 页面、浏览器自动化和受保护的网站，使用 `fetch`。它调用 `StealthyFetcher`，并支持全部隐身选项。

```bash
scrapling extract fetch "https://scrapling.requestcatcher.com/" content.md --network-idle
scrapling extract fetch "https://scrapling.requestcatcher.com/" data.txt --wait-selector ".content-loaded"
scrapling extract fetch "https://scrapling.requestcatcher.com/" page.html --no-headless --disable-resources
scrapling extract fetch "https://nopecha.com/demo/cloudflare" data.txt --solve-cloudflare --css-selector "#padded_content a"
scrapling extract fetch "https://site.com" content.md --proxy "http://proxy-server:8080"
```

使用 `--pierce-shadow` 可以包含开放 Shadow DOM 中的内容。该选项默认关闭，也可以用 `--no-pierce-shadow` 明确关闭。选择器示例和限制请参阅 [Shadow DOM](../fetching/stealthy.md#shadow-dom)。

```bash
scrapling extract fetch "https://example.com" content.md --pierce-shadow
```

运行 `scrapling extract fetch --help` 查看全部选项：

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

## 何时使用各个命令 {#when-to-use-each-command}

如果刚接触网页抓取，可以按以下规则选择：

- 简单网站、博客或新闻文章，使用 **`get`**。
- JavaScript 页面、浏览器自动化或受保护的网站（包括 Cloudflare），使用 **`fetch`**。

## 法律与伦理 {#legal-and-ethical-considerations}

⚠️ **重要原则：**

- **检查 robots.txt**：访问 `https://website.com/robots.txt`，查看爬取规则。
- **遵守请求频率限制**：不要用大量请求压垮服务器。
- **服务条款**：阅读并遵守网站条款。
- **版权**：尊重知识产权。
- **隐私**：遵守个人数据保护法律。
- **商业用途**：确保已获得商业使用许可。

---

*祝抓取顺利！请始终遵守网站规则以及适用的法律法规。*
