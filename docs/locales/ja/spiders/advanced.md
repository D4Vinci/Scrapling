---
title: "クロールの制御：AutoThrottle、チェックポイント、キャッシュ、ストリーミング"
description: "クロールの速度と並行処理を制御します。レスポンスのキャッシュ、一時停止と再開、データのストリーミング、チェックポイントに保存する状態を学びます。"
---

# 高度な使い方 {#advanced-usages}

## 概要 {#introduction}

!!! success "前提知識"

    1. [はじめに](getting-started.md)を読み、簡単な Spider の作成と実行ができること。

このページでは、並行処理の制御、一時停止と再開、ストリーミング、ライフサイクルフック、統計、ログを説明します。

## 並行処理を制御する {#concurrency-control}

Spider は、次のクラス属性でクロールの負荷を調整します。

| 属性 | デフォルト | 説明 |
|------|------------|------|
| `concurrent_requests` | `4` | 同時に処理するリクエストの最大数 |
| `concurrent_requests_per_domain` | `0` | ドメインごとの最大並行リクエスト数。0 はドメイン単位の制限なし |
| `download_delay` | `0.0` | 各リクエストの前に待つ秒数 |
| `robots_txt_obey` | `False` | robots.txt の Disallow、Crawl-delay、Request-rate に従う |

```python
class PoliteSpider(Spider):
    name = "polite"
    start_urls = ["https://example.com"]

    # Be gentle with the server
    concurrent_requests = 4
    concurrent_requests_per_domain = 2
    download_delay = 1.0  # Wait 1 second between requests

    async def parse(self, response: Response):
        yield {"title": response.css("title::text").get("")}
```

`concurrent_requests_per_domain` を設定すると、全体の上限に加え、各ドメインにも並行数の上限を設けます。複数のドメインを同時にクロールするとき、全体では多くのリクエストを処理しつつ、個々のドメインの負荷を抑えられます。

!!! tip

    `download_delay` はドメインに関係なく、すべてのリクエストの前に一定時間待ちます。簡単なレート制限として使えます。

## AutoThrottle {#autothrottle}

固定の `download_delay` は推測で決める値です。短すぎるとブロックされ、長すぎるとクロールが一晩かかるかもしれません。AutoThrottle はサイトの実際の応答速度を測り、ドメインごとに待機時間を調整します。速いサーバーでは速く、遅いサーバーやリクエストを拒否するサーバーでは遅く動きます。

| 属性 | デフォルト | 説明 |
|------|------------|------|
| `autothrottle_enabled` | `False` | 待機時間の自動調整を有効化 |
| `autothrottle_start_delay` | `5.0` | ドメインへの最初のリクエストに使う待機時間 |
| `autothrottle_max_delay` | `60.0` | 待機時間の上限 |
| `autothrottle_target_concurrency` | `None` | ドメインごとの目標並行リクエスト数。下記を参照 |
| `autothrottle_block_backoff` | `True` | ブロックされるたびに、そのドメインの待機時間を 2 倍にする |

```python
class AdaptiveSpider(Spider):
    name = "adaptive"
    start_urls = ["https://example.com"]

    concurrent_requests = 8
    concurrent_requests_per_domain = 1

    autothrottle_enabled = True
    autothrottle_start_delay = 2.0
    autothrottle_max_delay = 30.0

    async def parse(self, response: Response):
        yield {"title": response.css("title::text").get("")}
```

各レスポンスのあと、待機時間をサーバーの応答時間に近づけます。たとえば 0.5 秒で応答するサイトなら、待機時間も約 0.5 秒に落ち着きます。これはおおむね、同時に 1 件のリクエストが進行している状態です。ドメインごとの目標数は、設定済みの `autothrottle_target_concurrency`、次に `concurrent_requests_per_domain`、どちらもなければ 1 の順で決まります。通常は、すでに設定したドメインごとの上限が目標になり、待機時間がその数で割られるため、別の目標値は不要です。応答時間が急に長くなった場合は、平均に混ぜずにすぐ反映します。サーバーの負荷が増えたらすぐに減速し、加速するときは少しずつ行います。

### ブロックされたときに減速する {#backing-off-when-blocked}

応答時間だけではレート制限を検出できません。`429`、`403`、CAPTCHA のページは、本来の内容より*速く*返ることがあり、時間だけを見れば加速すべきと判断してしまいます。そのため、正常でないレスポンスでは、そのドメインの待機時間を**2 倍**にします。2xx 以外のステータスや、`is_blocked()` がブロックと判定したレスポンスが対象です。

```
0.5s -> 1s -> 2s -> 4s -> 8s ...   (up to autothrottle_max_delay)
```

サイトが拒否を続ける限り、Spider は速度を落とします。正常なレスポンスが戻ると、通常の平均計算で待機時間を徐々に下げ、サーバーの実際の速度に戻ります。再起動は不要です。

サイトが `429` または `503` のレスポンスで `Retry-After` ヘッダーを返す場合は、2 倍にする代わりに、その待機時間を使います。数値形式（`Retry-After: 120`）と HTTP 日付形式の両方に対応します。

`autothrottle_block_backoff = False` にすると、この動作を無効にして応答時間だけで調整します。この場合、ブロックは加速を止めるだけです。

ドメインごとの最終的な待機時間は、統計で確認できます。

```python
result = AdaptiveSpider().start()
print(result.stats.autothrottle_delays)  # {'example.com': 0.62}
```

!!! note "注意点"

    * `download_delay` と robots.txt の待機時間は下限ですが、その下限も `autothrottle_max_delay` によって制限されます。上限は、設定済みの待機時間や robots.txt の要求を満たす値にしてください。<br/>
    * `concurrent_requests_per_domain` には 2 つの役割があります。ドメインごとの同時リクエスト数を制限し、AutoThrottle の目標値にもなります。そのため、通常は別の目標設定が不要です。この上限を設定することを推奨します。待機中のリクエストも全体の並行数の枠を使うため、ドメイン単位で制限しないと、ほかのドメインと共有する枠が埋まることがあります。<br/>
    * 測る時間は取得全体の時間です。内部の再試行や、ブラウザのセッションでページを描画する時間も含みます。<br/>
    * `autothrottle_max_delay` は `Retry-After` を含むすべての待機時間を制限します。サイトが上限より長い待機を要求したら、`autothrottle_max_delay` を増やして守ってください。<br/>
    * 学習した待機時間はチェックポイントに保存しません。一時停止後に再開すると、各ドメインは `autothrottle_start_delay` から始まります。

## uvloop を使う {#using-uvloop}

`start()` の `use_uvloop` パラメーターを使うと、利用可能な場合に、より高速な [uvloop](https://github.com/MagicStack/uvloop)/[winloop](https://github.com/nicktimko/winloop) のイベントループを使えます。

```python
result = MySpider().start(use_uvloop=True)
```

I/O が多いクロールで処理量を増やせる場合があります。Linux/macOS では `uvloop`、Windows では `winloop` を別途インストールしてください。

## 一時停止と再開 {#pause-resume}

Spider はチェックポイントを使って、安全に一時停止して再開できます。コンストラクターに `crawldir` ディレクトリを渡すと有効になります。

```python
spider = MySpider(crawldir="crawl_data/my_spider")
result = spider.start()

if result.paused:
    print("Crawl was paused. Run again to resume.")
else:
    print("Crawl completed!")
```

### 仕組み {#how-it-works}

1. **一時停止**：クロール中に `Ctrl+C` を押します。実行中のリクエストが終わるまで待ち、未処理のリクエストと訪問済みリクエストのフィンガープリントをチェックポイントに保存して終了します。
2. **強制停止**：もう一度 `Ctrl+C` を押すと、実行中のタスクを待たずに停止します。
3. **再開**：同じ `crawldir` で再度実行します。チェックポイントを検出し、キューと訪問済みの集合を復元して、中断した位置から続けます。`start_requests()` は省略します。
4. **後片付け**：クロールが一時停止ではなく正常に完了すると、チェックポイントのファイルを自動で削除します。

**クロール中もチェックポイントを定期保存します。デフォルトは 5 分ごとです。**

保存間隔は次のように変更できます。

```python
# Save checkpoint every 2 minutes
spider = MySpider(crawldir="crawl_data/my_spider", interval=120.0)
```

チェックポイントの書き込みには一時ファイルを使い、書き込みに成功した場合だけ前のチェックポイントを置き換えます。

!!! warning "チェックポイントのデータ"

    `crawldir` を有効にすると、未処理のリクエストに含まれる値（`meta` やリクエストの引数を含む）は、Python の `pickle` モジュールで保存できる必要があります。保存できない値があると、チェックポイントの保存に失敗し、クロールが停止します。`Selector` はコールバック内で使えても、この方法では保存できません。

    `Selector` オブジェクトではなく、文字列や数値などの抽出した値を保存してください。リストや辞書にも、保存できる値だけを含める必要があります。

    ```python
    yield response.follow("/details", meta={"title": str(response.css("h1::text").get(""))})
    ```

!!! tip

    `start()` では、チェックポイントを有効にしていなくても、`Ctrl+C` を押すと実行中の処理を待って終了します。待たずにもう一度押すと、すぐに強制終了します。

### 再開中かどうかを知る {#knowing-if-youre-resuming}

`on_start()` フックは `resuming` フラグを受け取ります。

```python
async def on_start(self, resuming: bool = False):
    if resuming:
        self.logger.info("Resuming from checkpoint!")
    else:
        self.logger.info("Starting fresh crawl")
```

## 開発モード {#development-mode}

Spider の `parse()` を調整するとき、実行のたびに対象サーバーにアクセスすると遅くなり、不要なリクエストも増えます。開発モードは、初回のレスポンスをディスクに保存し、次回以降はそこから読みます。ページを再取得せずに、セレクターを変えて何度でも実行できます。

Spider に `development_mode = True` を設定します。

```python
class MySpider(Spider):
    name = "my_spider"
    start_urls = ["https://example.com"]
    development_mode = True

    async def parse(self, response: Response):
        yield {"title": response.css("title::text").get("")}
```

初回は通常どおりページを取得し、各レスポンスをディスクに保存します。次回以降、同じリクエストにはキャッシュを使い、ページ取得を省略します。`robots_txt_obey=True` の場合は、キャッシュの確認前に robots.txt をチェックします。

### キャッシュの場所 {#cache-location}

デフォルトでは、現在の作業ディレクトリから見た `.scrapling_cache/{spider.name}/` に保存します。これは Spider を実行した場所であり、スクリプトの置き場所**ではありません**。`development_cache_dir` で変更できます。

```python
class MySpider(Spider):
    name = "my_spider"
    start_urls = ["https://example.com"]
    development_mode = True
    development_cache_dir = "/tmp/my_spider_cache"
```

### 仕組み {#how-it-works_1}

1. **キャッシュのキー**：リクエストのフィンガープリントを使います。これに影響する属性（`fp_include_kwargs`、`fp_include_headers`、`fp_keep_fragments`）を変えると、新しく取得します。
2. **保存形式**：レスポンスごとに `{fingerprint_hex}.json` という JSON ファイルを作ります。ボディは Base64 でエンコードしてバイナリ内容を正確に保ちます。一時ファイルを作って名前を変更する、アトミックな書き込みです。
3. **再利用**：キャッシュがあれば、ページ取得に加えて `download_delay`、レート制限、`is_blocked()` の再試行処理を省略します。保存済みのレスポンスを直接コールバックに渡します。
4. **統計**：キャッシュを使うリクエストも、`requests_count`、`response_bytes`、ステータスごとの件数に含みます。そのため、通常のクロールと同じ形で統計を確認できます。追加の `cache_hits` と `cache_misses` で、キャッシュの利用状況もわかります。

### キャッシュを消す {#clearing-the-cache}

自動的な有効期限はありません。新しくクロールするには、キャッシュのディレクトリを削除するか、マネージャーの `clear()` を直接呼び出します。

!!! warning

    開発モードは開発用であり、本番用ではありません。キャッシュは期限切れにならず、再利用時はレート制限とブロックの再試行を省略します。`development_mode = True` のまま本番で使わないでください。

## ストリーミング {#streaming}

長く動く Spider や、抽出したデータをすぐに使うアプリでは、`start()` の代わりに `stream()` を使います。

```python
import anyio

async def main():
    spider = MySpider()
    async for item in spider.stream():
        print(f"Got item: {item}")
        # Access real-time stats
        print(f"Items so far: {spider.stats.items_scraped}")
        print(f"Requests made: {spider.stats.requests_count}")

anyio.run(main)
```

`start()` との主な違いは次のとおりです。

- `stream()` は非同期コンテキストから呼び出す必要があります。
- データ項目をリストに集めず、抽出するたびに 1 件ずつ返します。
- 反復処理中に `spider.stats` で最新の統計を確認できます。

!!! abstract

    `spider.stats` で確認できるすべての統計は、[後の節](#results-statistics)で説明します。

チェックポイントと組み合わせることもできます。最新のデータを表示し、一時停止と再開ができる UI を Spider の上に作れます。

```python
import anyio

async def main():
    spider = MySpider(crawldir="crawl_data/my_spider")
    async for item in spider.stream():
        print(f"Got item: {item}")
        # Access real-time stats
        print(f"Items so far: {spider.stats.items_scraped}")
        print(f"Requests made: {spider.stats.requests_count}")

anyio.run(main)
```
上のコードでは、`spider.pause()` で Spider を停止することもできます。チェックポイントが無効なら、クロールを終了するだけです。

## ライフサイクルフック {#lifecycle-hooks}

クロールの各段階に独自の処理を加えるため、次のフックをオーバーライドできます。

### on_start {#on_start}

クロール開始前に呼び出します。データの読み込みやリソースの初期化などに使います。

```python
async def on_start(self, resuming: bool = False):
    self.logger.info("Spider starting up")
    # Load seed URLs from a database, initialize counters, etc.
```

### on_close {#on_close}

クロールが完了または一時停止したあとに呼び出します。後片付けに使います。

```python
async def on_close(self):
    self.logger.info("Spider shutting down")
    # Close database connections, flush buffers, etc.
```

### on_error {#on_error}

リクエストが例外で失敗したときに呼び出します。エラーの記録や独自の復旧処理に使います。

```python
async def on_error(self, request: Request, error: Exception):
    self.logger.error(f"Failed: {request.url} - {error}")
    # Log to error tracker, save failed URL for later, etc.
```

### on_scraped_item {#on_scraped_item}

抽出した各項目を結果に追加する前に呼び出します。項目をそのまま、または変更して返すと保持します。`None` を返すと破棄します。

```python
async def on_scraped_item(self, item: dict) -> dict | None:
    # Drop items without a title
    if not item.get("title"):
        return None

    # Modify items (e.g., add timestamps)
    item["scraped_at"] = "2026-01-01"
    return item
```

!!! tip

    このフックで項目を独自のパイプラインに渡し、Spider の結果から除くこともできます。

### start_requests {#start_requests}

`start_requests()` をオーバーライドすると、`start_urls` を使わずに最初のリクエストを自分で作れます。

```python
async def start_requests(self):
    # POST request to log in first
    yield Request(
        "https://example.com/login",
        method="POST",
        data={"user": "admin", "pass": "secret"},
        callback=self.after_login,
    )

async def after_login(self, response: Response):
    # Now crawl the authenticated pages
    yield response.follow("/dashboard", callback=self.parse)
```

## 結果と統計 {#results-statistics}

`start()` が返す `CrawlResult` には、抽出したデータ項目と詳しい統計が含まれます。

```python
result = MySpider().start()

# Items
print(f"Total items: {len(result.items)}")
result.items.to_json("output.json", indent=True)

# Did the crawl complete?
print(f"Completed: {result.completed}")
print(f"Paused: {result.paused}")

# Statistics
stats = result.stats
print(f"Requests: {stats.requests_count}")
print(f"Failed: {stats.failed_requests_count}")
print(f"Blocked: {stats.blocked_requests_count}")
print(f"Offsite filtered: {stats.offsite_requests_count}")
print(f"Robots.txt disallowed: {stats.robots_disallowed_count}")
print(f"Cache hits: {stats.cache_hits}")
print(f"Cache misses: {stats.cache_misses}")
print(f"Items scraped: {stats.items_scraped}")
print(f"Items dropped: {stats.items_dropped}")
print(f"Response bytes: {stats.response_bytes}")
print(f"Duration: {stats.elapsed_seconds:.1f}s")
print(f"Speed: {stats.requests_per_second:.1f} req/s")
```

### 詳細な統計 {#detailed-stats}

`CrawlStats` は、次のような詳しい情報を記録します。

```python
stats = result.stats

# Status code distribution
print(stats.response_status_count)
# {'status_200': 150, 'status_404': 3, 'status_403': 1}

# Bytes downloaded per domain
print(stats.domains_response_bytes)
# {'example.com': 1234567, 'api.example.com': 45678}

# Requests per session
print(stats.sessions_requests_count)
# {'http': 120, 'stealth': 34}

# Proxies used during the crawl
print(stats.proxies)
# ['http://proxy1:8080', 'http://proxy2:8080']

# Log level counts
print(stats.log_levels_counter)
# {'debug': 200, 'info': 50, 'warning': 3, 'error': 1, 'critical': 0}

# Timing information
print(stats.start_time)       # Unix timestamp when crawl started
print(stats.end_time)         # Unix timestamp when crawl finished
print(stats.download_delay)   # The download delay used (seconds)

# Concurrency settings used
print(stats.concurrent_requests)             # Global concurrency limit
print(stats.concurrent_requests_per_domain)  # Per-domain concurrency limit

# AutoThrottle
print(stats.autothrottle_enabled)  # Whether the adaptive delay was on
print(stats.autothrottle_delays)   # Final delay per domain, {'example.com': 0.62}

# Custom stats (set by your spider code)
print(stats.custom_stats)
# {'login_attempts': 3, 'pages_with_errors': 5}

# Export everything as a dict
print(stats.to_dict())
```

## ログ {#logging}

Spider には、`self.logger` で使えるロガーが組み込まれています。Spider の名前が設定済みで、次のオプションを変更できます。

| 属性 | デフォルト | 説明 |
|------|------------|------|
| `logging_level` | `logging.DEBUG` | 記録する最低ログレベル |
| `logging_format` | `"[%(asctime)s]:({spider_name}) %(levelname)s: %(message)s"` | ログメッセージの形式 |
| `logging_date_format` | `"%Y-%m-%d %H:%M:%S"` | ログの日付形式 |
| `log_file` | `None` | コンソールに加えて書き込むログファイルのパス |

```python
import logging

class MySpider(Spider):
    name = "my_spider"
    start_urls = ["https://example.com"]
    logging_level = logging.INFO
    log_file = "logs/my_spider.log"

    async def parse(self, response: Response):
        self.logger.info(f"Processing {response.url}")
        yield {"title": response.css("title::text").get("")}
```

ログファイルのディレクトリがなければ自動で作成します。コンソールとファイルは同じ形式で出力します。
