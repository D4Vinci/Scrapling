---
title: "Scrapling の対話型シェルで Web スクレイピングを試す"
description: "IPython シェルでページを取得し、セレクターを試して結果を確認します。curl コマンドの変換、最近のレスポンスの再利用、コードのテストもできます。"
---

# Scrapling 対話型シェルの使い方 {#scrapling-interactive-shell-guide}

<script src="https://asciinema.org/a/736339.js" id="asciicast-736339" async data-autoplay="1" data-loop="1" data-cols="225" data-rows="40" data-start-at="00:06" data-speed="1.5" data-theme="tango"></script>

**開発者とデータサイエンティストのための Web スクレイピング REPL**

Scrapling の対話型シェルは、Web スクレイピング向けに拡張した IPython ベースの環境です。Scrapling のすべての機能をすぐに使えます。便利なショートカット、ページの自動管理、curl コマンドの変換などの機能も用意されています。

!!! success "前提条件"

    1. [Fetcher の基礎](../fetching/choosing.md)を読み、[Response オブジェクト](../fetching/choosing.md#response-object)と Fetcher の選び方を理解していること。
    2. [要素の検索](../parsing/selection.md)を読み、[Selector](../parsing/main_classes.md#selector)/[Response](../fetching/choosing.md#response-object) オブジェクトから要素を検索、抽出する方法を理解していること。
    3. [主要なクラス](../parsing/main_classes.md)を読み、[Response](../fetching/choosing.md#response-object) が [Selector](../parsing/main_classes.md#selector) から継承するプロパティとメソッドを理解していること。
    4. リクエストに使う Fetcher について、[HTTP リクエスト](../fetching/static.md)または[ブラウザでの取得](../fetching/stealthy.md)の少なくとも一方を読んでいること。


## 対話型シェルを使う理由 {#why-use-the-interactive-shell}

対話型シェルでは、スクリプトの作成と実行を何度も繰り返さずに、その場で試しながらスクレイピングできます。次の用途に適しています。

- **すばやい試作**：スクレイピングの方法をすぐに試せます。
- **データの調査**：サイトを対話形式でたどり、データを抽出できます。
- **Scrapling の学習**：機能をその場で試せます。
- **スクレイパーのデバッグ**：リクエストを順に実行し、結果を確認できます。
- **作業手順の変換**：ブラウザの DevTools からコピーした curl コマンドを、1 行で Fetcher のリクエストに変換できます。

## はじめに {#getting-started}

### シェルを起動する {#launch-the-shell}

```bash
# Start the interactive shell
scrapling shell

# Execute code and exit (useful for scripting)
scrapling shell -c "get('https://quotes.toscrape.com'); print(len(page.css('.quote')))"

# Set logging level
scrapling shell --loglevel info
```

起動すると Scrapling のバナーが表示されます。上の動画のように、すぐにスクレイピングを始められます。

```python
# No imports needed - everything is ready!
get('https://news.ycombinator.com')

# Explore the page structure
page.css('a')[:5]  # Look at first 5 links

# Refine your selectors
stories = page.css('.titleline>a')
len(stories)  # 30

# Extract specific data
for story in stories[:3]:
    title = story.text
    url = story['href']
    print(f"{title}: {url}")

# Try different approaches
titles = page.css('.titleline>a::text')  # Direct text extraction
urls = page.css('.titleline>a::attr(href)')  # Direct attribute extraction
```

## 組み込みのショートカット {#built-in-shortcuts}

定型コードを省くための、便利なショートカットがあります。

- **`get(url, **kwargs)`**：HTTP GET リクエスト（`Fetcher.get` の代わりに使います）
- **`post(url, **kwargs)`**：HTTP POST リクエスト（`Fetcher.post` の代わりに使います）
- **`put(url, **kwargs)`**：HTTP PUT リクエスト（`Fetcher.put` の代わりに使います）
- **`delete(url, **kwargs)`**：HTTP DELETE リクエスト（`Fetcher.delete` の代わりに使います）
- **`fetch(url, **kwargs)`**：ステルスブラウザでの取得（`StealthyFetcher.fetch` の代わりに使います）

`Fetcher`、`AsyncFetcher`、`StealthyFetcher`、`Selector` など、よく使うクラスはインポートせずに使えます。

### ページの自動管理 {#smart-page-management}

シェルはリクエストとページを自動で記録します。

- **現在のページにアクセスする**

    `page` と `response` は、最後に取得したページに自動で更新されます。
    
    ```python
    get('https://quotes.toscrape.com')
    # 'page' and 'response' both refer to the last fetched page
    page.url  # 'https://quotes.toscrape.com'
    response.status  # Prints 200; Same as page.status
    ```

- **ページの履歴**

    `pages` は直近 5 ページを保持する `Selectors` オブジェクトです。
    
    ```python
    get('https://site1.com')
    get('https://site2.com')
    get('https://site3.com')
    
    # Access last 5 pages
    len(pages)  # `Selectors` object with `page` history -> 3
    pages[0].url  # First page in history -> 'https://site1.com'
    pages[-1].url  # Most recent page -> 'https://site3.com'
    
    # Work with historical pages
    for i, old_page in enumerate(pages):
        print(f"Page {i}: {old_page.url} - {old_page.status}")
    ```

## その他の便利なコマンド {#additional-helpful-commands}

### ページを表示する {#page-visualization}

取得したページをブラウザで表示できます。

```python
get('https://quotes.toscrape.com')
view(page)  # Opens the page HTML in your default browser
```

### curl コマンドとの連携 {#curl-command-integration}

ブラウザの DevTools でコピーした curl コマンドを `Fetcher` のリクエストに変換するために、`uncurl` と `curl2fetcher` という関数を用意しています。

まず、次のようにリクエストを curl コマンドとしてコピーします。

<img src="../assets/scrapling_shell_curl.png" title="Chrome のリクエストを curl コマンドとしてコピーする" alt="Chrome のリクエストを curl コマンドとしてコピーする" style="width: 70%;"/>

- **curl コマンドを Request オブジェクトに変換する**

    ```python
    curl_cmd = '''curl 'https://scrapling.requestcatcher.com/post' \
      -X POST \
      -H 'Content-Type: application/json' \
      -d '{"name": "test", "value": 123}' '''
    
    request = uncurl(curl_cmd)
    request.method  # -> 'post'
    request.url  # -> 'https://scrapling.requestcatcher.com/post'
    request.headers  # -> {'Content-Type': 'application/json'}
    ```

- **curl コマンドを直接実行する**

    ```python
    # Convert and execute in one step
    curl2fetcher(curl_cmd)
    page.status  # -> 200
    ```

### IPython の機能 {#ipython-features}

シェルは IPython のすべての機能を引き継いでいます。

```python
# Magic commands
%time page = get('https://example.com')  # Time execution
%history  # Show command history
%save filename.py 1-10  # Save commands 1-10 to file

# Tab completion works everywhere
page.c<TAB>  # Shows: css, cookies, headers, etc.
Fetcher.<TAB>  # Shows all Fetcher methods

# Object inspection
get? # Show get documentation
```

## 例 {#examples}

AI で生成した例をいくつか紹介します。

#### EC サイトのデータ収集 {#e-commerce-data-collection}

```python
# Start with product listing page
catalog = get('https://shop.example.com/products')

# Find product links
product_links = catalog.css('.product-link::attr(href)').getall()
print(f"Found {len(product_links)} products")

# Sample a few products first
for link in product_links[:3]:
    product = get(catalog.urljoin(link))
    name = product.css('.product-name::text').get('')
    price = product.css('.price::text').get('')
    print(f"{name}: {price}")

# Scale up with sessions for efficiency
from scrapling.fetchers import FetcherSession
with FetcherSession() as session:
    products = []
    for link in product_links:
        product = session.get(catalog.urljoin(link))
        products.append({
            'name': product.css('.product-name::text').get(''),
            'price': product.css('.price::text').get(''),
            'url': link
        })
```

#### API 連携とテスト {#api-integration-and-testing}

```python
>>> # Test API endpoints interactively
>>> response = get('https://jsonplaceholder.typicode.com/posts/1')
>>> response.json()
{'userId': 1, 'id': 1, 'title': 'sunt aut...', 'body': 'quia et...'}

>>> # Test POST requests
>>> new_post = post('https://jsonplaceholder.typicode.com/posts', 
...                 json={'title': 'Test Post', 'body': 'Test content', 'userId': 1})
>>> new_post.json()['id']
101

>>> # Test with different data
>>> updated = put('https://jsonplaceholder.typicode.com/posts/1',
...               json={'title': 'Updated Title'})
```

## ヘルプ {#getting-help}

ターミナル内の説明だけでは足りない場合は、次をご利用ください。

- [Scrapling ドキュメント](https://scrapling.readthedocs.io/ja/latest/)
- [Discord コミュニティ](https://discord.gg/EMgGbDceNQ)
- [GitHub Issues](https://github.com/D4Vinci/Scrapling/issues)

以上です。スクレイピングを楽しんでください。シェルを使えば、会話するように手軽に Web スクレイピングを進められます。
