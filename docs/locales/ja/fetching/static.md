---
title: "Fetcher と FetcherSession で Python の HTTP スクレイピング"
description: "ブラウザの模倣、Cookie、プロキシ、再利用できるセッションを使い、同期・非同期の HTTP リクエストを送ります。Scrapling でレスポンスからデータを抽出できます。"
---

# HTTP リクエスト {#http-requests}

`Fetcher` は、高性能な `curl_cffi` を使い、高速で軽量な HTTP リクエストを提供します。ステルス機能も備えています。

!!! success "前提条件"

    1. [Fetcher の基本](../fetching/choosing.md)を読み、[Response オブジェクト](../fetching/choosing.md#response-object)と Fetcher の選び方を理解していること。
    2. [要素の検索](../parsing/selection.md)を読み、[Selector](../parsing/main_classes.md#selector)/[Response](../fetching/choosing.md#response-object) から要素を探して抽出する方法を理解していること。
    3. [主なクラス](../parsing/main_classes.md)を読み、[Response](../fetching/choosing.md#response-object) が [Selector](../parsing/main_classes.md#selector) から継承するプロパティやメソッドを理解していること。

## 基本的な使い方 {#basic-usage}
この Fetcher も、ほかの Fetcher と同じ形でインポートします。

```python
from scrapling.fetchers import Fetcher
```
解析の設定方法は[こちら](choosing.md#parser-configuration-in-all-fetchers)を参照してください。

### 共通の引数 {#shared-arguments}
各リクエストメソッドに共通する引数を先に説明します。

- **url**：対象の URL です。
- **stealthy_headers**：実際のブラウザのヘッダーを生成して追加します。Google の referer も設定します。標準では有効です。
- **follow_redirects**：リダイレクトを制御します。**標準は `"safe"`** で、リダイレクトには従いますが、内部やプライベート IP 宛ては拒否します。これは SSRF 対策です。`True` なら制限なくすべてに従い、`False` ならリダイレクトを無効にします。
- **timeout**：各リクエストの完了を待つ最大秒数です。**標準は 30 秒**です。
- **retries**：失敗したリクエストの最大試行回数で、最初の試行も含みます。**標準は 3 回**です。
- **retry_delay**：再試行の間に待つ秒数です。**標準は 1 秒**です。
- **impersonate**：ブラウザの TLS フィンガープリントを模倣します。文字列かそのリストを受け取り、`"chrome110"`、`"firefox102"`、`"safari15_5"` なら特定の版を、`"chrome"`、`"firefox"`、`"safari"`、`"edge"` なら利用可能な最新版を使います。これにより、TLS の段階で本物のブラウザからのリクエストに見えます。リストを渡すと、リクエストごとにランダムに選びます。**標準は利用可能な最新の Chrome です。**
- **http3**：HTTP/3 を使います。**標準は False** です。`impersonate` と組み合わせると問題が起きることがあります。
- **cookies**：リクエストに使う Cookie です。`name→value` の辞書か、辞書のリストを渡せます。
- **proxy**：このリクエストの HTTP と HTTPS の通信を通すプロキシです。形式は `http://username:password@localhost:8030` です。
- **proxy_auth**：プロキシの HTTP Basic 認証です。(username, password) のタプルを指定します。
- **proxies**：使用するプロキシの辞書です。形式は `{"http": proxy_url, "https": proxy_url}` です。
- **proxy_rotator**：プロキシを自動で切り替える `ProxyRotator` インスタンスです。`proxy` や `proxies` とは併用できません。
- **headers**：リクエストに含めるヘッダーです。`stealthy_headers` が生成したヘッダーも上書きできます。
- **max_redirects**：リダイレクトの最大回数です。**標準は 30 回**で、-1 なら無制限です。
- **verify**：HTTPS 証明書を検証するか指定します。**標準は True** です。
- **cert**：クライアント証明書と鍵のファイル名を指定する (cert, key) のタプルです。
- **selector_config**：最終的な `Selector`/`Response` の作成時に使う、解析設定の辞書です。

!!! note "注意点："

    1. 現在模倣できるブラウザは、`"edge"`、`"chrome"`、`"chrome_android"`、`"safari"`、`"safari_beta"`、`"safari_ios"`、`"safari_ios_beta"`、`"firefox"`、`"tor"` です。<br/>
    2. 対応するブラウザとバージョンは、引数の自動補完に表示され、`curl_cffi` の更新に合わせて変わります。<br/>
    3. `impersonate` または `stealthy_headers` を有効にすると、使用するブラウザのバージョンに合ったヘッダーを自動生成します。

さらに調整したい場合は、メソッド側が直接扱わない `curl_cffi` の対応引数も渡せます。

### 文字コード {#text-encoding}

UTF-8 以外のページで文字化けする場合は、`default_encoding="shift_jis"` など、そのページの文字コードを渡してください。`Content-Type` ヘッダーに文字コードがない場合に使います。サーバーが指定した文字コードは上書きしません。

サーバーの文字コード指定が誤っている場合は、`selector_config={"encoding": "shift_jis"}` で正しい文字コードを強制できます。

### HTTP メソッド {#http-methods}
メソッドごとに追加の引数があります。たとえば GET の `params` や、POST、PUT、DELETE の `data`/`json` です。

例で見てみましょう。

> 注意：`OPTIONS` と `HEAD` には対応していません。
#### GET {#get}
```python
from scrapling.fetchers import Fetcher
# Basic GET
page = Fetcher.get('https://example.com')
page = Fetcher.get('https://scrapling.requestcatcher.com/get', stealthy_headers=True)
page = Fetcher.get('https://scrapling.requestcatcher.com/get', proxy='http://username:password@localhost:8030')
# With parameters
page = Fetcher.get('https://example.com/search', params={'q': 'query'})

# With headers
page = Fetcher.get('https://example.com', headers={'User-Agent': 'Custom/1.0'})
# Basic HTTP authentication
page = Fetcher.get("https://example.com", auth=("my_user", "password123"))
# Browser impersonation
page = Fetcher.get('https://example.com', impersonate='chrome')
# HTTP/3 support
page = Fetcher.get('https://example.com', http3=True)
```
非同期リクエストでは少しだけ変えます。
```python
from scrapling.fetchers import AsyncFetcher
# Basic GET
page = await AsyncFetcher.get('https://example.com')
page = await AsyncFetcher.get('https://scrapling.requestcatcher.com/get', stealthy_headers=True)
page = await AsyncFetcher.get('https://scrapling.requestcatcher.com/get', proxy='http://username:password@localhost:8030')
# With parameters
page = await AsyncFetcher.get('https://example.com/search', params={'q': 'query'})
# With headers
page = await AsyncFetcher.get('https://example.com', headers={'User-Agent': 'Custom/1.0'})
# Basic HTTP authentication
page = await AsyncFetcher.get("https://example.com", auth=("my_user", "password123"))
# Browser impersonation
page = await AsyncFetcher.get('https://example.com', impersonate='chrome110')
# HTTP/3 support
page = await AsyncFetcher.get('https://example.com', http3=True)
```
どの場合も `page` は [Response](choosing.md#response-object) で、[Selector](../parsing/main_classes.md#selector) としてそのまま解析できます。
```python
page.css('.something.something')

page = Fetcher.get('https://api.github.com/events')
>>> page.json()
[{'id': '<redacted>',
  'type': 'PushEvent',
  'actor': {'id': '<redacted>',
   'login': '<redacted>',
   'display_login': '<redacted>',
   'gravatar_id': '',
   'url': 'https://api.github.com/users/<redacted>',
   'avatar_url': 'https://avatars.githubusercontent.com/u/<redacted>'},
  'repo': {'id': '<redacted>',
...
```
#### POST {#post}
```python
from scrapling.fetchers import Fetcher
# Basic POST
page = Fetcher.post('https://scrapling.requestcatcher.com/post', data={'key': 'value'}, params={'q': 'query'})
page = Fetcher.post('https://scrapling.requestcatcher.com/post', data={'key': 'value'}, stealthy_headers=True)
page = Fetcher.post('https://scrapling.requestcatcher.com/post', data={'key': 'value'}, proxy='http://username:password@localhost:8030', impersonate="chrome")
# Another example of form-encoded data
page = Fetcher.post('https://example.com/submit', data={'username': 'user', 'password': 'pass'}, http3=True)
# JSON data
page = Fetcher.post('https://example.com/api', json={'key': 'value'})
```
非同期リクエストでは少しだけ変えます。
```python
from scrapling.fetchers import AsyncFetcher
# Basic POST
page = await AsyncFetcher.post('https://scrapling.requestcatcher.com/post', data={'key': 'value'})
page = await AsyncFetcher.post('https://scrapling.requestcatcher.com/post', data={'key': 'value'}, stealthy_headers=True)
page = await AsyncFetcher.post('https://scrapling.requestcatcher.com/post', data={'key': 'value'}, proxy='http://username:password@localhost:8030', impersonate="chrome")
# Another example of form-encoded data
page = await AsyncFetcher.post('https://example.com/submit', data={'username': 'user', 'password': 'pass'}, http3=True)
# JSON data
page = await AsyncFetcher.post('https://example.com/api', json={'key': 'value'})
```
#### PUT {#put}
```python
from scrapling.fetchers import Fetcher
# Basic PUT
page = Fetcher.put('https://example.com/update', data={'status': 'updated'})
page = Fetcher.put('https://example.com/update', data={'status': 'updated'}, stealthy_headers=True, impersonate="chrome")
page = Fetcher.put('https://example.com/update', data={'status': 'updated'}, proxy='http://username:password@localhost:8030')
# Another example of form-encoded data
page = Fetcher.put("https://scrapling.requestcatcher.com/put", data={'key': ['value1', 'value2']})
```
非同期リクエストでは少しだけ変えます。
```python
from scrapling.fetchers import AsyncFetcher
# Basic PUT
page = await AsyncFetcher.put('https://example.com/update', data={'status': 'updated'})
page = await AsyncFetcher.put('https://example.com/update', data={'status': 'updated'}, stealthy_headers=True, impersonate="chrome")
page = await AsyncFetcher.put('https://example.com/update', data={'status': 'updated'}, proxy='http://username:password@localhost:8030')
# Another example of form-encoded data
page = await AsyncFetcher.put("https://scrapling.requestcatcher.com/put", data={'key': ['value1', 'value2']})
```

#### DELETE {#delete}
```python
from scrapling.fetchers import Fetcher
page = Fetcher.delete('https://example.com/resource/123')
page = Fetcher.delete('https://example.com/resource/123', stealthy_headers=True, impersonate="chrome")
page = Fetcher.delete('https://example.com/resource/123', proxy='http://username:password@localhost:8030')
```
非同期リクエストでは少しだけ変えます。
```python
from scrapling.fetchers import AsyncFetcher
page = await AsyncFetcher.delete('https://example.com/resource/123')
page = await AsyncFetcher.delete('https://example.com/resource/123', stealthy_headers=True, impersonate="chrome")
page = await AsyncFetcher.delete('https://example.com/resource/123', proxy='http://username:password@localhost:8030')
```

## セッション管理 {#session-management}

同じ設定で複数のリクエストを送るなら、`FetcherSession` を使います。同期と非同期のどちらにも対応し、必要な種類を自動で切り替えます。別のクラスをインポートする必要はありません。

`FetcherSession` は、各リクエストメソッドのほぼすべての引数を受け取れます。セッション全体の設定を決めた後、特定のリクエストだけを別の設定にすることも簡単です。

```python
from scrapling.fetchers import FetcherSession

# Create a session with default configuration
with FetcherSession(
    impersonate='chrome',
    http3=True,
    stealthy_headers=True,
    timeout=30,
    retries=3
) as session:
    # Make multiple requests with the same settings and the same cookies
    page1 = session.get('https://scrapling.requestcatcher.com/get')
    page2 = session.post('https://scrapling.requestcatcher.com/post', data={'key': 'value'})
    page3 = session.get('https://api.github.com/events')

    # All requests share the same session and connection pool
```

`FetcherSession` と `ProxyRotator` を組み合わせると、リクエストごとにプロキシを自動で切り替えられます。

```python
from scrapling.fetchers import FetcherSession, ProxyRotator

rotator = ProxyRotator([
    'http://proxy1:8080',
    'http://proxy2:8080',
    'http://proxy3:8080',
])

with FetcherSession(proxy_rotator=rotator, impersonate='chrome') as session:
    # Each request automatically uses the next proxy in rotation
    page1 = session.get('https://example.com/page1')
    page2 = session.get('https://example.com/page2')

    # You can check which proxy was used via the response metadata
    print(page1.meta['proxy'])
```

メソッドに直接 `proxy=` を渡せば、そのリクエストだけセッションのプロキシやローテーターを上書きできます。

```python
with FetcherSession(proxy='http://default-proxy:8080') as session:
    # Uses the session proxy
    page1 = session.get('https://example.com/page1')

    # Override the proxy for this specific request
    page2 = session.get('https://example.com/page2', proxy='http://special-proxy:9090')
```

非同期の例です。

```python
async with FetcherSession(impersonate='firefox', http3=True) as session:
    # All standard HTTP methods available
    response = await session.get('https://example.com')
    response = await session.post('https://scrapling.requestcatcher.com/post', json={'data': 'value'})
    response = await session.put('https://scrapling.requestcatcher.com/put', data={'update': 'info'})
    response = await session.delete('https://scrapling.requestcatcher.com/delete')
```
こちらの書き方もできます。
```python
import asyncio
from scrapling.fetchers import FetcherSession

# Async session usage
async with FetcherSession(impersonate="safari") as session:
    urls = ['https://example.com/page1', 'https://example.com/page2']

    tasks = [
        session.get(url) for url in urls
    ]

    pages = await asyncio.gather(*tasks)
```

`Fetcher` は、リクエストのたびに `FetcherSession` で一時的なセッションを作ります。

### セッションの利点 {#session-benefits}

- **高速**：リクエストごとにセッションを作る場合より 10 倍速くなります。
- **Cookie の維持**：リクエスト間で Cookie を自動管理します。
- **リソースの節約**：複数のリクエストでメモリや CPU を効率よく使えます。
- **設定の一元管理**：リクエストの設定を 1 か所で管理できます。

## 例 {#examples}
初めて Web スクレイピングを行う方向けに、まとまった例を紹介します。

### 基本的な HTTP リクエスト {#basic-http-request}

```python
from scrapling.fetchers import Fetcher

# Make a request
page = Fetcher.get('https://example.com')

# Check the status
if page.status == 200:
    # Extract title
    title = page.css('title::text').get()
    print(f"Page title: {title}")

    # Extract all links
    links = page.css('a::attr(href)').getall()
    print(f"Found {len(links)} links")
```

### 商品の取得 {#product-scraping}

```python
from scrapling.fetchers import Fetcher

def scrape_products():
    page = Fetcher.get('https://example.com/products')
    
    # Find all product elements
    products = page.css('.product')
    
    results = []
    for product in products:
        results.append({
            'title': product.css('.title::text').get(),
            'price': product.css('.price::text').re_first(r'\d+\.\d{2}'),
            'description': product.css('.description::text').get(),
            'in_stock': product.has_class('in-stock')
        })
    
    return results
```

### ファイルのダウンロード {#downloading-files}

```python
from scrapling.fetchers import Fetcher

page = Fetcher.get('https://raw.githubusercontent.com/D4Vinci/Scrapling/main/docs/assets/main_cover.png')
with open(file='main_cover.png', mode='wb') as f:
   f.write(page.body)
```

### ページ送りの処理 {#pagination-handling}

```python
from scrapling.fetchers import Fetcher

def scrape_all_pages():
    base_url = 'https://example.com/products?page={}'
    page_num = 1
    all_products = []
    
    while True:
        # Get current page
        page = Fetcher.get(base_url.format(page_num))
        
        # Find products
        products = page.css('.product')
        if not products:
            break
            
        # Process products
        for product in products:
            all_products.append({
                'name': product.css('.name::text').get(),
                'price': product.css('.price::text').get()
            })
            
        # Next page
        page_num += 1
        
    return all_products
```

### フォームの送信 {#form-submission}

```python
from scrapling.fetchers import Fetcher

# Submit login form
response = Fetcher.post(
    'https://example.com/login',
    data={
        'username': 'user@example.com',
        'password': 'password123'
    }
)

# Check login success
if response.status == 200:
    # Extract user info
    user_name = response.css('.user-name::text').get()
    print(f"Logged in as: {user_name}")
```

### 表の抽出 {#table-extraction}

```python
from scrapling.fetchers import Fetcher

def extract_table():
    page = Fetcher.get('https://example.com/data')
    
    # Find table
    table = page.css('table')[0]
    
    # Extract headers
    headers = [
        th.text for th in table.css('thead th')
    ]
    
    # Extract rows
    rows = []
    for row in table.css('tbody tr'):
        cells = [td.text for td in row.css('td')]
        rows.append(dict(zip(headers, cells)))
        
    return rows
```

### ナビゲーションメニュー {#navigation-menu}

```python
from scrapling.fetchers import Fetcher

def extract_menu():
    page = Fetcher.get('https://example.com')
    
    # Find navigation
    nav = page.css('nav')[0]
    
    menu = {}
    for item in nav.css('li'):
        links = item.css('a')
        if links:
            link = links[0]
            menu[link.text] = {
                'url': link['href'],
                'has_submenu': bool(item.css('.submenu'))
            }
            
    return menu
```

## 使う場面 {#when-to-use}

次の場合は `Fetcher` が適しています。

- 高速な HTTP リクエストが必要な場合。
- 追加の処理負荷を小さくしたい場合。
- JavaScript を実行せず、リクエストだけでサイトを取得できる場合。
- JavaScript チャレンジのない保護など、基本的なステルス機能が必要な場合。

次の場合は `FetcherSession` が適しています。

- 同じサイトや別のサイトに複数のリクエストを送る場合。
- リクエスト間で Cookie や認証状態を維持する場合。
- 接続を再利用して性能を高めたい場合。
- 複数のリクエストで設定をそろえる場合。
- セッション状態が必要な API を使う場合。

次の場合は、ほかの Fetcher を使ってください。

- ブラウザを自動操作する場合。
- 高度なボット対策への対応やステルス機能が必要な場合。
- JavaScript の実行や動的な内容とのやり取りが必要な場合。
