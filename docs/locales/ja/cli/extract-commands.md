---
title: "CLI で Web ページを Markdown、HTML、テキストとして保存する"
description: "scrapling extract で HTTP やブラウザの取得結果を保存します。CSS による絞り込み、リクエスト設定、出力形式の選び方を紹介します。"
---

# Scrapling 抽出コマンドの使い方 {#scrapling-extract-command-guide}

**プログラムを書かずに、ターミナルから Web スクレイピングできます！**

`scrapling extract` コマンドを使うと、コードを書かずに、ターミナルから直接 Web サイトの内容をダウンロードして抽出できます。初心者や研究者など、Web データをすぐに取り出したい方に適しています。

!!! success "前提条件"

    1. [Fetcher の基礎](../fetching/choosing.md)を読み、[Response オブジェクト](../fetching/choosing.md#response-object)と Fetcher の選び方を理解していること。
    2. [要素の検索](../parsing/selection.md)を読み、[Selector](../parsing/main_classes.md#selector)/[Response](../fetching/choosing.md#response-object) オブジェクトから要素を検索、抽出する方法を理解していること。
    3. [主要なクラス](../parsing/main_classes.md)を読み、[Response](../fetching/choosing.md#response-object) が [Selector](../parsing/main_classes.md#selector) から継承するプロパティとメソッドを理解していること。
    4. リクエストに使う Fetcher について、[HTTP リクエスト](../fetching/static.md)または[ブラウザでの取得](../fetching/stealthy.md)の少なくとも一方を読んでいること。


## extract コマンド群とは {#what-is-the-extract-command-group}

extract は、次の機能を持つシンプルなターミナルツール群です。

- **Web ページをダウンロード**し、内容をファイルに保存します。
- **HTML を読みやすい形式に変換**します。Markdown にするほか、HTML のまま保存したり、ページのテキストだけを抽出したりできます。
- **独自の CSS セレクターに対応**し、ページの特定部分を抽出できます。
- **HTTP リクエストとブラウザでの取得に対応**しています。
- **細かく設定できます**。独自のヘッダー、Cookie、プロキシなどを指定できます。コードで使えるオプションのほぼすべてを、コマンドラインからも利用できます。

!!! tip "AI 向けモード"

    すべての抽出コマンドで `--ai-targeted` フラグを使えます。有効にすると本文だけを抽出し、不要なタグ（script、style、noscript、svg）を除去します。プロンプトインジェクションに使われる可能性のある隠し要素（インラインスタイルで隠された要素、aria-hidden、隠されたスロット、template タグ）、ゼロ幅 Unicode 文字、HTML コメントも取り除きます。ブラウザコマンド（`fetch`）では、広告のブロックも自動で有効になります。AI モデルに渡す出力に適しています。

## クイックスタート {#quick-start}

- **基本的なページのダウンロード**

    Web サイトの内容を、読みやすいテキストとしてダウンロードします。
    ```bash
    scrapling extract get "https://example.com" page_content.txt
    ```
    HTTP GET リクエストを送り、ページのテキストを `page_content.txt` に保存します。

- **別の形式で保存する**

    ファイルの拡張子を変えて出力形式を選びます。
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

- **特定の内容を抽出する**

    すべてのコマンドで、`--css-selector` または `-s` に CSS セレクターを渡し、ページの特定部分を抽出できます。以下の例で使い方を紹介します。

## 利用できるコマンド {#available-commands}

`scrapling extract --help` を実行すると、次のコマンド一覧を表示できます。
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

以下で各コマンドを詳しく説明します。

### HTTP リクエスト {#http-requests}

1. **GET リクエスト**

    Web サイトの内容をダウンロードする際に、最もよく使うコマンドです。
    
    ```bash
    scrapling extract get [URL] [OUTPUT_FILE] [OPTIONS]
    ```
    
    **例：**
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
    `scrapling extract get --help` で利用できるオプションを確認します。
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
    オプションは他のリクエストコマンドでも同じように動作するため、説明は繰り返しません。

2. **POST リクエスト**
    
    ```bash
    scrapling extract post [URL] [OUTPUT_FILE] [OPTIONS]
    ```
    
    **例：**
    ```bash
    # Submit form data
    scrapling extract post "https://api.site.com/search" results.html --data "query=python&type=tutorial"
    
    # Send JSON data
    scrapling extract post "https://api.site.com" response.txt --json '{"username": "test", "action": "search"}'
    ```
    `scrapling extract post --help` で利用できるオプションを確認します。
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

3. **PUT リクエスト**
    
    ```bash
    scrapling extract put [URL] [OUTPUT_FILE] [OPTIONS]
    ```
    
    **例：**
    ```bash
    # Send data
    scrapling extract put "https://scrapling.requestcatcher.com/put" results.html --data "update=info" --impersonate "firefox"
    
    # Send JSON data
    scrapling extract put "https://scrapling.requestcatcher.com/put" response.txt --json '{"username": "test", "action": "search"}'
    ```
    `scrapling extract put --help` で利用できるオプションを確認します。
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

4. **DELETE リクエスト**
    
    ```bash
    scrapling extract delete [URL] [OUTPUT_FILE] [OPTIONS]
    ```
    
    **例：**
    ```bash
    # Send data
    scrapling extract delete "https://scrapling.requestcatcher.com/delete" results.html
    
    # Send JSON data
    scrapling extract delete "https://scrapling.requestcatcher.com/" response.txt --impersonate "chrome"
    ```
    `scrapling extract delete --help` で利用できるオプションを確認します。
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

### ブラウザでの取得 {#browser-fetching}

JavaScript を使うページ、ブラウザの自動操作、保護されたサイトには `fetch` を使います。`StealthyFetcher` を実行し、すべてのステルスオプションを利用できます。

```bash
scrapling extract fetch "https://scrapling.requestcatcher.com/" content.md --network-idle
scrapling extract fetch "https://scrapling.requestcatcher.com/" data.txt --wait-selector ".content-loaded"
scrapling extract fetch "https://scrapling.requestcatcher.com/" page.html --no-headless --disable-resources
scrapling extract fetch "https://nopecha.com/demo/cloudflare" data.txt --solve-cloudflare --css-selector "#padded_content a"
scrapling extract fetch "https://site.com" content.md --proxy "http://proxy-server:8080"
```

オープンな Shadow DOM の内容を含めるには `--pierce-shadow` を使います。デフォルトでは無効です。`--no-pierce-shadow` を指定すると明示的に無効にできます。セレクターの例と制限については [Shadow DOM](../fetching/stealthy.md#shadow-dom) をご覧ください。

```bash
scrapling extract fetch "https://example.com" content.md --pierce-shadow
```

すべてのオプションは `scrapling extract fetch --help` で確認できます。

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

## コマンドの選び方 {#when-to-use-each-command}

Web スクレイピングに慣れておらず、どのコマンドを選ぶか迷ったら、次を目安にしてください。

- シンプルなサイト、ブログ、ニュース記事には **`get`** を使います。
- JavaScript を使うページ、ブラウザの自動操作、Cloudflare などで保護されたサイトには **`fetch`** を使います。

## 法律と倫理への配慮 {#legal-and-ethical-considerations}

⚠️ **大切な指針：**

- **robots.txt を確認する**：`https://website.com/robots.txt` でスクレイピングのルールを確認します。
- **レート制限を守る**：大量のリクエストでサーバーに負荷をかけないようにします。
- **利用規約**：サイトの規約を読み、守ります。
- **著作権**：知的財産権を尊重します。
- **プライバシー**：個人情報保護に関する法律に注意します。
- **商用利用**：業務目的での利用に必要な許可があることを確認します。

---

*スクレイピングを楽しんでください。サイトの方針を尊重し、適用される法律や規制を必ず守りましょう。*
