---
title: "Scrapling で初めての Python Web クローラーを作る"
description: "データを抽出し、ページ送りのリンクをたどり、結果を出力する Spider を作ります。開始 URL、コールバック、ドメイン制限、robots.txt の設定を学びます。"
---

# はじめに {#getting-started}

## 概要 {#introduction}

!!! success "前提知識"

    1. [Fetcher の基本](../fetching/choosing.md)を読み、Fetcher の種類と使い分けを理解していること。
    2. [主要なクラス](../parsing/main_classes.md)を読み、[Selector](../parsing/main_classes.md#selector) と [Response](../fetching/choosing.md#response-object) を理解していること。
    3. [アーキテクチャ](architecture.md)を読み、Spider の仕組みを大まかに理解していること。

Spider の仕組みを使うと、複数のページを並行して取得するクローラーを数行のコードで作れます。Scrapy を使ったことがあれば、なじみのある書き方です。初めての場合も、このガイドで必要なことを順に説明します。

## 初めての Spider {#your-first-spider}

Spider は、Web サイトをクロールしてデータを抽出する方法を定義するクラスです。最も簡単な例を見てみましょう。

```python
from scrapling.spiders import Spider, Response

class QuotesSpider(Spider):
    name = "quotes"
    start_urls = ["https://quotes.toscrape.com"]

    async def parse(self, response: Response):
        for quote in response.css("div.quote"):
            yield {
                "text": quote.css("span.text::text").get(""),
                "author": quote.css("small.author::text").get(""),
            }
```

すべての Spider に、次の 3 つが必要です。

1. **`name`**：Spider を識別する一意の名前です。
2. **`start_urls`**：クロールを開始する URL のリストです。
3. **`parse()`**：各レスポンスを処理して結果を返す、非同期ジェネレーターメソッドです。

処理の中心となるのは `parse()` メソッドです。Scrapling の [Selector](../parsing/main_classes.md#selector)/[Response](../fetching/choosing.md#response-object) と同じ選択メソッドを使い、抽出したデータを辞書として `yield` で出力します。

## Spider を実行する {#running-the-spider}

インスタンスを作成し、`start()` を呼び出します。

```python
result = QuotesSpider().start()
```

`start()` が非同期処理を内部で管理するので、イベントループを自分で扱う必要はありません。実行中の処理はターミナルに記録され、クロールの終了時には詳しい統計が表示されます。

統計は、戻り値の `CrawlResult` オブジェクトにも含まれています。

```python
result = QuotesSpider().start()

# Access scraped items
for item in result.items:
    print(item["text"], "-", item["author"])

# Check statistics
print(f"Scraped {result.stats.items_scraped} items")
print(f"Made {result.stats.requests_count} requests")
print(f"Took {result.stats.elapsed_seconds:.1f} seconds")

# Did the crawl finish or was it paused?
print(f"Completed: {result.completed}")
```

## リンクをたどる {#following-links}

多くのクロールでは、リンクをたどって複数のページを取得します。`response.follow()` で次のリクエストを作成できます。

```python
from scrapling.spiders import Spider, Response

class QuotesSpider(Spider):
    name = "quotes"
    start_urls = ["https://quotes.toscrape.com"]

    async def parse(self, response: Response):
        # Extract items from the current page
        for quote in response.css("div.quote"):
            yield {
                "text": quote.css("span.text::text").get(""),
                "author": quote.css("small.author::text").get(""),
            }

        # Follow the "next page" link
        next_page = response.css("li.next a::attr(href)").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)
```

`response.follow()` は相対 URL を現在のページの URL と自動で結合します。また、デフォルトでは現在のページの URL を `Referer` ヘッダーに設定します。

ページの種類に応じて、次のリクエストに異なるコールバックメソッドを指定できます。

```python
async def parse(self, response: Response):
    for link in response.css("a.product-link::attr(href)").getall():
        yield response.follow(link, callback=self.parse_product)

async def parse_product(self, response: Response):
    yield {
        "name": response.css("h1::text").get(""),
        "price": response.css(".price::text").get(""),
    }
```

!!! note

    すべてのコールバックメソッドは、`async def` と `yield` を使う非同期ジェネレーターである必要があります。

## データをエクスポートする {#exporting-data}

`result.items` が返す `ItemList` には、エクスポート用のメソッドがあります。

```python
result = QuotesSpider().start()

# Export as JSON
result.items.to_json("quotes.json")

# Export as JSON with pretty-printing
result.items.to_json("quotes.json", indent=True)

# Export as JSON Lines (one JSON object per line)
result.items.to_jsonl("quotes.jsonl")

# Export as CSV or XML
result.items.to_csv("quotes.csv")
result.items.to_xml("quotes.xml")
```

いずれのメソッドも、親ディレクトリがなければ自動で作成します。

`to_csv()` は、すべてのデータ項目に現れるキーごとに列を作ります。項目ごとにキーが異なっていても出力でき、値がないセルは空欄になります。`fields=[...]` を渡すと列と順序を指定でき、`delimiter="\t"` を渡すと TSV ファイルにできます。`to_xml()` は各項目を `<item>` 要素に入れ、`<items>` をルート要素にします。これらの名前は `root_tag` と `item_tag` で変更できます。

どちらの形式でも、入れ子の辞書やリストなど、単純なスカラー値でない値は JSON として書き込みます。データが知らないうちに失われることを防ぎます。

## ドメインを制限する {#filtering-domains}

`allowed_domains` で、Spider がアクセスするドメインを制限できます。外部サイトへのリンクを誤ってたどることを防ぎます。

```python
class MySpider(Spider):
    name = "my_spider"
    start_urls = ["https://example.com"]
    allowed_domains = {"example.com"}

    async def parse(self, response: Response):
        for link in response.css("a::attr(href)").getall():
            # Links to other domains are silently dropped
            yield response.follow(link, callback=self.parse)
```

サブドメインは自動で一致します。たとえば `allowed_domains = {"example.com"}` とすると、`sub.example.com` や `blog.example.com` なども許可されます。

除外されたリクエストは `stats.offsite_requests_count` に記録されるので、その件数を確認できます。

## robots.txt に従う {#robotstxt-compliance}

`robots_txt_obey = True` にすると、Spider は各ドメインをクロールする前に robots.txt のルールを確認します。

```python
class PoliteSpider(Spider):
    name = "polite"
    start_urls = ["https://example.com"]
    robots_txt_obey = True

    async def parse(self, response: Response):
        for link in response.css("a::attr(href)").getall():
            yield response.follow(link, callback=self.parse)
```

有効にすると、次の処理を行います。

1. **robots.txt を先に取得します。** クロール開始前に、`start_urls` のすべてのドメインから並行して取得します。
2. **すべてのリクエストを確認します。** ドメインの robots.txt にある `Disallow` ルールに照らして確認します。禁止されたリクエストは通知せずに破棄し、`stats.robots_disallowed_count` に記録します。
3. **`Crawl-delay` と `Request-rate` に従います。** 指示された待機時間と設定済みの `download_delay` のうち、大きい値を使います。robots.txt によって待機時間が短くなることはなく、必要な場合だけ長くなります。AutoThrottle が有効な場合は、その最大待機時間も上限になります。必要な待機時間を守れるよう、`autothrottle_max_delay` を十分に大きくしてください。

robots.txt は Spider のデフォルトセッションで取得し、クロール全体を通してドメインごとにキャッシュします。クロール中に見つかった、`start_urls` にないドメインでは、そのドメインへの最初のリクエスト時に取得します。

**注意：**予期しない動作を避けるため、`robots_txt_obey` はデフォルトで無効です。有効にしても並行処理の設定（`concurrent_requests`、`concurrent_requests_per_domain`）は変わりません。調整されるのは、リクエスト間の待機時間だけです。

`download_delay` を手動で決めたくない場合は、`autothrottle_enabled = True` にしてください。Spider が各ドメインの応答速度に応じて待機時間を調整し、ブロックされた場合は速度を落とします。[AutoThrottle](advanced.md#autothrottle) を参照してください。

## 次のステップ {#whats-next}

基本がわかったら、次のページに進めます。

- [リクエストとレスポンス](requests-responses.md)：優先順位、重複排除、メタデータなどを説明します。
- [セッション](sessions.md)：1 つの Spider で HTTP、ブラウザ、ステルスブラウザなどの Fetcher を使います。
- [プロキシ管理とブロックへの対応](proxy-blocking.md)：リクエストごとにプロキシを切り替え、ブロックに対応します。
- [高度な機能](advanced.md)：並行処理の制御、AutoThrottle、一時停止と再開、ストリーミング、ライフサイクルフック、ログを説明します。
