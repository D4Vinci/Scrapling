---
title: "Scrapling の Web クローラーの仕組み"
description: "Spider、リクエスト、セッション、スケジューラー、クロールエンジンの連携を学びます。Scrapy の流れと比較し、使い始める方法を確認します。"
---

# Spider のアーキテクチャ {#spiders-architecture}

!!! success "前提知識"

    1. [Fetcher の基本](../fetching/choosing.md)を読み、Fetcher の種類と使い分けを理解していること。
    2. [主要なクラス](../parsing/main_classes.md)を読み、[Selector](../parsing/main_classes.md#selector) と [Response](../fetching/choosing.md#response-object) を理解していること。

Scrapling の Spider は、Scrapy を参考にした非同期クロールの仕組みです。並行リクエスト、複数のセッション、一時停止と再開をサポートします。Scrapling の解析エンジンと Fetcher を共通のクロール API にまとめ、スケジューリング、並行処理の制御、チェックポイントを追加しています。

Scrapy を知っていれば、すぐに使い方がわかります。初めてでも使いやすい構成です。

## データの流れ {#data-flow}

次の図は、クロール中にデータがどのように流れるかを示しています。

<img src="../assets/spider_architecture.png" title="@TrueSkills による Spider の構成図" alt="@TrueSkills による Spider の構成図" style="width: 70%;"/>

Spider を実行すると、大まかには次の処理が行われます。

1. **Spider** が最初の `Request` オブジェクトを作ります。デフォルトでは `start_urls` の各 URL に 1 つずつ作ります。独自の処理が必要なら、`start_requests()` をオーバーライドできます。
2. **スケジューラー**がリクエストを受け取り、優先度付きキューに入れて、フィンガープリントを作ります。優先度が高いリクエストから取り出されます。
3. **クロールエンジン**が**スケジューラー**に次のリクエストを要求します。その際、全体とドメインごとの並行数の上限、およびダウンロードの待機時間を守ります。`robots_txt_obey` が有効な場合は、先にドメインの robots.txt を確認し、禁止されたリクエストを通知せずに破棄します。**クロールエンジン**は受け取ったリクエストを**セッションマネージャー**に渡します。セッションマネージャーは `sid`（セッション ID）で適切なセッションを選びます。
4. **セッション**がページを取得し、[Response](../fetching/choosing.md#response-object) オブジェクトを**クロールエンジン**に返します。エンジンは統計を記録し、レスポンスがブロックされていないか確認します。ブロックされていたら、最大 `max_blocked_retries` 回リクエストを再試行します。ブロックの検出方法と再試行の処理は変更できます。
5. **クロールエンジン**が [Response](../fetching/choosing.md#response-object) をリクエストのコールバックに渡します。コールバックは、抽出したデータ項目として扱われる辞書か、スケジューラーのキューに追加される次のリクエストを出力します。
6. キューが空になり、実行中のタスクもなくなるか、Spider が一時停止されるまで、手順 2 から繰り返します。
7. Spider の開始時に `crawldir` を指定すると、**クロールエンジン**がチェックポイントを定期的にディスクへ保存します。内容は、未処理のリクエストと訪問済み URL の集合です。Ctrl+C による通常の終了時にも、最後のチェックポイントを保存します。次回同じ `crawldir` で実行すると、`start_requests()` を省略してスケジューラーの状態を復元し、中断した位置から再開します。


## 構成要素 {#components}

### Spider {#spider}

主に操作するクラスです。`Spider` のサブクラスを作り、`start_urls` と `parse()` を定義します。必要に応じてセッションを設定し、ライフサイクルフックをオーバーライドします。

```python
from scrapling.spiders import Spider, Response, Request

class MySpider(Spider):
    name = "my_spider"
    start_urls = ["https://example.com"]

    async def parse(self, response: Response):
        for link in response.css("a::attr(href)").getall():
            yield response.follow(link, callback=self.parse_page)

    async def parse_page(self, response: Response):
        yield {"title": response.css("h1::text").get("")}
```

### クロールエンジン {#crawler-engine}

エンジンはクロール全体を管理します。メインループを動かし、並行数を制限し、セッションマネージャーを通してリクエストを送信し、コールバックの結果を処理します。直接操作する必要はありません。`Spider.start()` と `Spider.stream()` が管理します。

### スケジューラー {#scheduler}

URL の重複排除を組み込んだ優先度付きキューです。リクエストのフィンガープリントは、URL、HTTP メソッド、ボディ、セッション ID から作ります。チェックポイント用に `snapshot()` と `restore()` を提供し、クロールの状態を保存して再開できます。

### セッションマネージャー {#session-manager}

名前付きのセッションを 1 つ以上管理します。各セッションには次のいずれかを使います。

- [FetcherSession](../fetching/static.md)
- [AsyncStealthySession](../fetching/stealthy.md)

リクエストを受け取ると、`sid` フィールドに応じて適切なセッションに渡します。セッションはデフォルトで Spider と同時に開始しますが、初めて使う時まで開始を遅らせることもできます。

### チェックポイント {#checkpoint-system}

有効にすると、クローラーの状態を pickle ファイルとしてディスクに保存するオプション機能です。状態には、未処理のリクエストと訪問済み URL のフィンガープリントが含まれます。一時ファイルを書いてから名前を変更するアトミックな書き込みを使い、ファイルの破損を防ぎます。保存は設定した間隔と通常の終了時に行います。クロールが一時停止ではなく正常に完了すると、チェックポイントのファイルは自動で削除します。

### レスポンスキャッシュ {#response-cache}

開発モードで使えるオプションのキャッシュです。取得したすべてのレスポンスをディスクに保存し、次回以降の実行で再利用します。リクエストのフィンガープリントをキーにして JSON で保存し、ボディは Base64 でエンコードしてバイナリデータも保ちます。対象サーバーへ再アクセスせずに `parse()` を調整するための機能で、本番用ではありません。

### 出力 {#output}

抽出したデータ項目は `ItemList` に集めます。これは list のサブクラスで、`to_json()`、`to_jsonl()`、`to_csv()`、`to_xml()` のエクスポートメソッドがあります。クロールの統計は、多くの情報を持つデータクラス `CrawlStats` に記録します。


## Scrapy との比較 {#comparison-with-scrapy}

Scrapy から移行する場合は、次の対応表が参考になります。

| 概念 | Scrapy | Scrapling |
|------|--------|-----------|
| Spider の定義 | `scrapy.Spider` のサブクラス | `scrapling.spiders.Spider` のサブクラス |
| 最初のリクエスト | `start_requests()` | `async start_requests()` |
| コールバック | `def parse(self, response)` | `async def parse(self, response)` |
| リンクをたどる | `response.follow(url)` | `response.follow(url)` |
| データ項目の出力 | `yield dict` または `yield Item` | `yield dict` |
| リクエストの予定管理 | スケジューラー + Dupefilter | 重複排除を組み込んだスケジューラー |
| ダウンロード | Downloader + Middleware | 複数のセッションを扱うセッションマネージャー |
| データ項目の処理 | Item Pipelines | `on_scraped_item()` フック |
| ブロックの検出 | 独自の Middleware | 組み込みの `is_blocked()` + `retry_blocked_request()` フック |
| 並行処理 | `CONCURRENT_REQUESTS` 設定 | `concurrent_requests` クラス属性 |
| ドメインの制限 | `allowed_domains` | `allowed_domains` |
| robots.txt | `ROBOTSTXT_OBEY` 設定 | `robots_txt_obey` クラス属性 |
| 一時停止と再開 | `JOBDIR` 設定 | コンストラクター引数 `crawldir` |
| エクスポート | Feed exports | `result.items.to_json()` / `to_jsonl()` / `to_csv()` / `to_xml()`、またはフックで独自に実装 |
| 実行 | `scrapy crawl spider_name` | `MySpider().start()` |
| ストリーミング | 非対応 | `async for item in spider.stream()` |
| 複数のセッション | 非対応 | 1 つの Spider で異なる種類のセッションを使用 |
