---
title: "1 つのクローラーで HTTP とブラウザのセッションを使う"
description: "名前付きセッションを設定し、Spider のリクエストを HTTP またはブラウザの Fetcher に渡します。Cookie の再利用、必要時の起動、API 履歴の確認を学びます。"
---

# Spider のセッション {#spiders-sessions}

!!! success "前提知識"

    1. [はじめに](getting-started.md)を読み、簡単な Spider の作成と実行ができること。
    2. [Fetcher の基本](../fetching/choosing.md)を読み、HTTP セッションと Stealthy セッションの違いを理解していること。

Spider は、複数の Fetcher セッションを同時に使えます。たとえば、単純なページには高速な HTTP セッション、保護されたページにはステルスブラウザのセッションを使います。このページでは、セッションの設定と使い方を説明します。

## セッションとは {#what-are-sessions}

セッションは、あらかじめ設定された Fetcher のインスタンスで、クロール中は起動したままになります。リクエストごとに接続やブラウザを作らず、同じセッションを再利用するため、高速でリソースの消費も少なくなります。

デフォルトでは、各 Spider が 1 つの [FetcherSession](../fetching/static.md) を作ります。`configure_sessions()` をオーバーライドすると、セッションを追加したりデフォルトを変更したりできます。ただし、次の表のように、各セッションの非同期版を使う必要があります。


| セッションの種類 | 用途 |
|------------------|------|
| [FetcherSession](../fetching/static.md) | 高速な HTTP リクエスト。JavaScript は実行しません |
| [AsyncStealthySession](../fetching/stealthy.md) | JavaScript、ブラウザの自動操作、ボット対策の回避 |


## セッションを設定する {#configuring-sessions}

Spider の `configure_sessions()` をオーバーライドします。`manager` は `SessionManager` のインスタンスです。`manager.add()` でセッションを登録します。

```python
from scrapling.spiders import Spider, Response
from scrapling.fetchers import FetcherSession

class MySpider(Spider):
    name = "my_spider"
    start_urls = ["https://example.com"]

    def configure_sessions(self, manager):
        manager.add("default", FetcherSession())

    async def parse(self, response: Response):
        yield {"title": response.css("title::text").get("")}
```

`manager.add()` には次の引数を渡せます。

| 引数 | 型 | デフォルト | 説明 |
|------|----|------------|------|
| `session_id` | `str` | *必須* | リクエストからこのセッションを指定するための名前 |
| `session` | `Session` | *必須* | セッションのインスタンス |
| `default` | `bool` | `False` | デフォルトセッションに設定 |
| `lazy` | `bool` | `False` | 最初に使うときだけ起動 |

!!! note "注意点"

    1. リクエストでセッションを指定しなければ、デフォルトセッションを使います。デフォルトは次のいずれかで決まります。
        1. 最初に追加したセッションが、自動でデフォルトになります。
        2. セッションの追加時に `default=True` を指定します。
    2. 渡すセッションのインスタンスを自分で起動しておく必要はありません。Spider が各セッションを確認し、未起動なら起動します。
    3. 必要になるまで起動を遅らせるには、追加時に `lazy` を指定します。たとえば、Spider の開始時ではなく、ブラウザが必要になった時点で起動できます。

## 複数のセッションを使う Spider {#multi-session-spider}

一覧ページには高速な HTTP セッション、ボット対策のある詳細ページにはステルスブラウザを使う例です。

```python
from scrapling.spiders import Spider, Response
from scrapling.fetchers import FetcherSession, AsyncStealthySession

class ProductSpider(Spider):
    name = "products"
    start_urls = ["https://shop.example.com/products"]

    def configure_sessions(self, manager):
        # Fast HTTP for listing pages (default)
        manager.add("http", FetcherSession())

        self.browser_session = AsyncStealthySession(
            headless=True,
            network_idle=True,
            record_requests=True,
        )
        manager.add("stealth", self.browser_session)

    async def parse(self, response: Response):
        for link in response.css("a.product::attr(href)").getall():
            # Route product pages through the stealth session
            yield response.follow(link, sid="stealth", callback=self.parse_product)

        next_page = response.css("a.next::attr(href)").get()
        if next_page:
            yield response.follow(next_page)

    async def parse_product(self, response: Response):
        yield {
            "name": response.css("h1::text").get(""),
            "price": response.css(".price::text").get(""),
        }

    async def on_close(self):
        for api_response in self.browser_session.network.search(
            url_pattern=r"https://api\.shop\.example\.com/.*", limit=None
        ):
            self.logger.info(f"Saved API response: {api_response.url} ({api_response.status})")
```

この例ではブラウザのインスタンスを保持し、セッションを閉じる前に `on_close()` で保存済みの API 履歴を 1 回読みます。履歴にはすべての商品ページが含まれ、終了後も読み取れます。まだ記録中の処理は待機せず、保存件数の制限も適用されます。

重要なのは `sid` です。リクエストごとに使うセッションを指定します。`response.follow()` で `sid` を省略すると、元のリクエストのセッション ID を引き継ぎます。

セッションは異なるクラスである必要はありません。同じクラスのインスタンスを、異なる設定で使うこともできます。

```python
from scrapling.spiders import Spider, Response
from scrapling.fetchers import FetcherSession

class ProductSpider(Spider):
    name = "products"
    start_urls = ["https://shop.example.com/products"]

    def configure_sessions(self, manager):
        chrome_requests = FetcherSession(impersonate="chrome")
        firefox_requests = FetcherSession(impersonate="firefox")

        manager.add("chrome", chrome_requests)
        manager.add("firefox", firefox_requests)

    async def parse(self, response: Response):
        for link in response.css("a.product::attr(href)").getall():
            yield response.follow(link, callback=self.parse_product)

        next_page = response.css("a.next::attr(href)").get()
        if next_page:
            yield response.follow(next_page, sid="firefox")

    async def parse_product(self, response: Response):
        yield {
            "name": response.css("h1::text").get(""),
            "price": response.css(".price::text").get(""),
        }
```

特定のリクエスト用にセッションを分け、専用の Cookie や状態を保つこともできます。

## セッション引数 {#session-arguments}

`Request` や `response.follow(**kwargs)` に渡した追加のキーワード引数は、セッションの取得メソッドに渡されます。セッション設定を変えずに、個々のリクエストを調整できます。

```python
async def parse(self, response: Response):
    # Pass extra headers for this specific request
    yield Request(
        "https://api.example.com/data",
        headers={"Authorization": "Bearer token123"},
        callback=self.parse_api,
    )

    # Use a different HTTP method
    yield Request(
        "https://example.com/submit",
        method="POST",
        data={"field": "value"},
        sid="firefox",
        callback=self.parse_result,
    )
```

!!! warning

    通常、`FetcherSession`、`Fetcher`、`AsyncFetcher` では、`.get()` や `.post()` で HTTP メソッドを選びます。しかし、Spider 内の `FetcherSession` ではこの方法は使えません。デフォルトは _HTTP GET_ です。ほかの HTTP メソッドを使うには、上の例のように `method` 引数で指定します。これは、すべてのセッションで `Request` のインターフェースを共通にするためです。

上の例で登録した `"stealth"` セッション（`AsyncStealthySession`）には、`wait_selector`、`page_action`、`extra_headers` など、ブラウザ専用の引数を渡せます。

```python
async def parse(self, response: Response):
    # Use Cloudflare solver with the `AsyncStealthySession` we configured above
    yield Request(
        "https://nopecha.com/demo/cloudflare",
        sid="stealth",
        callback=self.parse_result,
        solve_cloudflare=True,
        block_webrtc=True,
        hide_canvas=True,
        google_search=True,
    )

    yield response.follow(
        "/dynamic-page",
        sid="stealth",
        callback=self.parse_dynamic,
        wait_selector="div.loaded",
        network_idle=True,
    )
```

!!! warning

    `response.follow()` は元のリクエストのセッション引数（**kwargs）を引き継ぎます。ただし、`method`、`params`、`data`、`json`、`files`、`multipart` は除きます。そのため、POST のあとでリンクをたどると、通常の GET を送信します。新しく指定した値が、引き継いだ値より優先されます。

```python
from scrapling.spiders import Spider, Response
from scrapling.fetchers import FetcherSession

class ProductSpider(Spider):
    name = "products"
    start_urls = ["https://shop.example.com/products"]

    def configure_sessions(self, manager):
        manager.add("http", FetcherSession(impersonate='chrome'))

    async def parse(self, response: Response):
        # I don't want the follow request to impersonate a desktop Chrome like the previous request, but a mobile one
        # so I override it like this
        for link in response.css("a.product::attr(href)").getall():
            yield response.follow(link, impersonate="chrome131_android", callback=self.parse_product)

        next_page = response.css("a.next::attr(href)").get()
        if next_page:
            yield response.follow(next_page)

    async def parse_product(self, response: Response):
        yield {
            "name": response.css("h1::text").get(""),
            "price": response.css(".price::text").get(""),
        }
```
!!! info

    Spider を終了するときは、マネージャーが実行中のセッションを自動で確認し、先にすべて閉じます。
