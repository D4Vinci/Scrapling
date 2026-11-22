---
title: "Spider のリクエスト、コールバック、Response.follow"
description: "クロール用のリクエストを作り、メタデータを渡し、response.follow でリンクをたどります。コールバック、優先度、重複排除を学びます。"
---

# リクエストとレスポンス {#requests-responses}

!!! success "前提知識"

    1. [はじめに](getting-started.md)を読み、簡単な Spider の作成と実行ができること。

このページでは `Request` オブジェクトを詳しく説明します。リクエストの作成、コールバック間のデータ受け渡し、優先度と重複排除の制御、`response.follow()` によるリンクの取得を扱います。

## Request オブジェクト {#the-request-object}

`Request` は、取得する URL を表します。直接作成するか、`response.follow()` を使って作成できます。

```python
from scrapling.spiders import Request

# Direct construction
request = Request(
    "https://example.com/page",
    callback=self.parse_page,
    priority=5,
)

# Via response.follow (preferred in callbacks)
request = response.follow("/page", callback=self.parse_page)
```

`Request` には次の引数を渡せます。

| 引数 | 型 | デフォルト | 説明 |
|------|----|------------|------|
| `url` | `str` | *必須* | 取得する URL |
| `sid` | `str` | `""` | 使用するセッションの ID。[セッション](sessions.md)を参照 |
| `callback` | `callable` | `None` | レスポンスを処理する非同期ジェネレーターメソッド。デフォルトは `parse()` |
| `priority` | `int` | `0` | 大きい値を先に処理 |
| `dont_filter` | `bool` | `False` | `True` なら重複排除を省略し、同じリクエストを許可 |
| `meta` | `dict` | `{}` | レスポンスに渡す任意のメタデータ |
| `**kwargs` | | | セッションの取得メソッドに渡す追加のキーワード引数。たとえば `headers`、`method`、`data` |

追加のキーワード引数は、そのままセッションに渡されます。たとえば、POST リクエストは次のように送信します。

```python
yield Request(
    "https://example.com/api",
    method="POST",
    data={"key": "value"},
    callback=self.parse_result,
)
```

## Response.follow() {#responsefollow}

`response.follow()` は相対 URL を現在のページ URL と結合し、新しい `Request` を作成します。`sid`、`callback`、`priority` を省略すると、紐づいた `response.request` の値を引き継ぎます。値を明示すると上書きできます。

前のリクエストのヘッダー、Cookie、認証、プロキシ設定、ブラウザ設定、その他のリクエスト単位の引数、メタデータはコピーしません。同じサイトのリンクにも、別のサイトのリンクにも適用されます。

`sid=""`、`callback=None`、`priority=None` の場合は、紐づいた元のリクエストの値を引き継ぎます。`priority=0` を明示すると、元の優先度を上書きします。メタデータはデフォルトで空、重複排除は有効です。選択したセッションの共有設定と Cookie jar は引き続き適用されます。

POST の後でリンクをたどると、別の `method` を指定しない限り GET を送信します。

```python
async def parse(self, response: Response):
    # Minimal - inherits callback, sid, priority from current request
    yield response.follow("/next-page")

    # Override specific fields
    yield response.follow(
        "/product/123",
        callback=self.parse_product,
        sid="stealth",
        priority=10,
    )

    # Pass additional metadata to
    yield response.follow(
        "/details",
        callback=self.parse_details,
        meta={"category": "electronics"},
    )
```

| 引数 | 型 | デフォルト | 説明 |
| --- | --- | --- | --- |
| `url` | `str` | *必須* | たどる URL。絶対 URL、相対 URL の両方に対応 |
| `sid` | `str` | `""` | 空なら元のリクエストのセッション ID を継承 |
| `callback` | `callable` | `None` | `None` なら元のリクエストのコールバックを継承 |
| `priority` | `int` / `None` | `None` | `None` なら元のリクエストの優先度を継承。明示した `0` でも上書き可能 |
| `dont_filter` | `bool` | `False` | 重複排除を省略 |
| `meta` | `dict` | `None` | このリクエストだけのメタデータ |
| `referer_flow` | `bool` | `True` | 現在のページ URL を Referer に設定 |
| `**kwargs` |  |  | セッションの取得メソッドに渡す明示的な引数 |

### Referer の引き継ぎを無効にする {#disabling-referer-flow}

デフォルトでは、`response.follow()` は HTTP とブラウザのリクエストに現在のページ URL を `Referer` として設定します。ブラウザがこの Referer を使うように `google_search=False` も設定します。無効にするには、次のようにします。

```python
yield response.follow("/page", referer_flow=False)
```

`referer_flow=False` の場合、このヘルパーは Referer を追加せず、`google_search` も変更しません。明示的に渡したヘッダーや、セッションとブラウザのデフォルト設定は引き続き適用されます。HTTP リクエストに別の Referer を設定する場合：

```python
yield response.follow(
    "/page",
    referer_flow=False,
    headers={"Referer": "https://example.com/"},
)
```

ブラウザのリクエストでは `extra_headers` を使い、必要に応じて `google_search=False` を設定します。

## コールバック {#callbacks}

コールバックは、レスポンスを処理する Spider の非同期ジェネレーターメソッドです。次のいずれかを `yield` で返す必要があります。

- **`dict`**：抽出したデータ項目です。結果に追加します。
- **`Request`**：次のリクエストです。キューに追加します。
- **`None`**：何もせずに無視します。

```python
class MySpider(Spider):
    name = "my_spider"
    start_urls = ["https://example.com"]

    async def parse(self, response: Response):
        # Yield items (dicts)
        yield {"url": response.url, "title": response.css("title::text").get("")}

        # Yield follow-up requests
        for link in response.css("a::attr(href)").getall():
            yield response.follow(link, callback=self.parse_page)

    async def parse_page(self, response: Response):
        yield {"content": response.css("article::text").get("")}
```

!!! tip "注意"

    すべてのコールバックメソッドは `async def` で定義し、`return` ではなく `yield` を使う必要があります。データ項目だけを返し、次のリクエストを作らない場合も、非同期ジェネレーターにしてください。

## リクエストの優先度 {#request-priority}

優先度の値が大きいリクエストから処理します。重要なページを先に処理したい場合に便利です。

```python
async def parse(self, response: Response):
    # High priority - process product pages first
    for link in response.css("a.product::attr(href)").getall():
        yield response.follow(link, callback=self.parse_product, priority=10)

    # Low priority - pagination links processed after products
    next_page = response.css("a.next::attr(href)").get()
    if next_page:
        yield response.follow(next_page, callback=self.parse, priority=0)
```

`response.follow()` の `priority` はデフォルトで `None` で、元のリクエストの優先度を引き継ぎます。`priority=0` を含め、値を明示すると引き継ぐ優先度を上書きします。

## 重複排除 {#deduplication}

Spider は、URL、HTTP メソッド、リクエストボディ、セッション ID から作ったフィンガープリントで重複を判定します。同じフィンガープリントを持つリクエストが 2 つあれば、2 つ目を通知せずに破棄します。

ログイン後に同じページを再取得する場合など、重複を許可したいときは `dont_filter=True` にします。

```python
yield Request("https://example.com/dashboard", dont_filter=True, callback=self.parse_dashboard)

# Or with response.follow
yield response.follow("/dashboard", dont_filter=True, callback=self.parse_dashboard)
```

Spider のクラス属性で、フィンガープリントに含める内容を調整できます。

| 属性 | デフォルト | 効果 |
|------|------------|------|
| `fp_include_kwargs` | `False` | セッションの取得メソッドに渡した追加のリクエスト引数を含めます。ヘッダーなどが該当します |
| `fp_keep_fragments` | `False` | 計算時に URL フラグメント（`#section`）を残します |
| `fp_include_headers` | `False` | リクエストヘッダーを含めます |

たとえば、`https://example.com/page#section1` と `https://example.com/page#section2` を異なる URL として扱う場合は、次のようにします。

```python
class MySpider(Spider):
    name = "my_spider"
    fp_keep_fragments = True
    # ...
```

## リクエストのメタデータ {#request-meta}

`meta` 辞書を使うと、コールバック間で任意のデータを渡せます。あるページの処理に、別のページで取得した情報が必要な場合に便利です。

```python
async def parse(self, response: Response):
    for product in response.css("div.product"):
        category = product.css("span.category::text").get("")
        link = product.css("a::attr(href)").get()
        if link:
            yield response.follow(
                link,
                callback=self.parse_product,
                meta={"category": category},
            )

async def parse_product(self, response: Response):
    yield {
        "name": response.css("h1::text").get(""),
        "price": response.css(".price::text").get(""),
        # Access meta from the request
        "category": response.meta.get("category", ""),
    }
```

`response.follow()` は明示的に渡した `meta` だけを使います。前の値が必要な場合は、必要なキーを選んで渡してください。

Spider は一部のメタデータを自動でも保存します。たとえば、プロキシのローテーションが有効な場合、使用したプロキシを `response.meta["proxy"]` で取得できます。
