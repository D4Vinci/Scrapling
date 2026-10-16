---
title: "プロキシを切り替え、ブロックされたクロールを再試行する"
description: "Scrapling の Spider でプロキシとローテーション戦略を使います。ブロックを検出して再試行し、HTTP からブラウザのセッションへ切り替えます。"
---

# プロキシ管理とブロックへの対応 {#proxy-management-and-handling-blocks}

## 概要 {#introduction}

!!! success "前提知識"

    1. [はじめに](getting-started.md)を読み、簡単な Spider の作成と実行ができること。
    2. [セッション](sessions.md)を読み、設定方法を理解していること。

大量のページを取得する場合、レート制限やブロックを避けるために複数のプロキシを切り替えることがあります。Scrapling の `ProxyRotator` を使うと簡単に設定できます。すべてのセッションで使え、Spider のブロック再試行の仕組みとも連携します。

プロキシの仕組みや選び方がわからない場合は、[こちらのガイド](https://substack.thewebscraping.club/p/everything-about-proxies)が参考になります。

## ProxyRotator {#proxyrotator}

`ProxyRotator` はプロキシのリストを管理し、自動で切り替えます。セッションの `proxy_rotator` パラメーターに渡して使います。

```python
from scrapling.spiders import Spider, Response
from scrapling.fetchers import FetcherSession, ProxyRotator

class MySpider(Spider):
    name = "my_spider"
    start_urls = ["https://example.com"]

    def configure_sessions(self, manager):
        rotator = ProxyRotator([
            "http://proxy1:8080",
            "http://proxy2:8080",
            "http://user:pass@proxy3:8080",
        ])
        manager.add("default", FetcherSession(proxy_rotator=rotator))

    async def parse(self, response: Response):
        # Check which proxy was used
        print(f"Proxy used: {response.meta.get('proxy')}")
        yield {"title": response.css("title::text").get("")}
```

各リクエストには、順番に次のプロキシが割り当てられます。使ったプロキシは `response.meta["proxy"]` に保存されるので、どのプロキシでどのページを取得したか確認できます。


ブラウザのセッションでは、次のような調整が必要です。

```python
from scrapling.fetchers import AsyncStealthySession, ProxyRotator

# String proxies work for all session types
rotator = ProxyRotator([
    "http://proxy1:8080",
    "http://proxy2:8080",
])

# Dict proxies (Playwright format) work for browser sessions
rotator = ProxyRotator([
    {"server": "http://proxy1:8080", "username": "user", "password": "pass"},
    {"server": "http://proxy2:8080"},
])

# Then inside the spider
def configure_sessions(self, manager):
    rotator = ProxyRotator(["http://proxy1:8080", "http://proxy2:8080"])
    manager.add("browser", AsyncStealthySession(proxy_rotator=rotator))
```

!!! info

    1. 同じセッションで、`proxy_rotator` と固定の `proxy` または `proxies` は併用できません。設定時にどちらかを選んでください。あとから個々のリクエストで上書きすることはできます。後ほど例を紹介します。
    2. デフォルトでは、ブラウザのセッションは永続ブラウザコンテキストとタブのプールを使います。ただし、ブラウザはタブごとにプロキシを設定できません。そのため、`ProxyRotator` を使うと、Fetcher はプロキシごとに別のコンテキストを作り、そこにタブを 1 つ開きます。処理が終わると、タブとコンテキストの両方を閉じます。

## 独自のローテーション戦略 {#custom-rotation-strategies}

`ProxyRotator` はデフォルトでプロキシを順に使い、最後まで進むと最初に戻ります。

独自の戦略関数を渡して変更することもできます。関数は次のシグネチャに合わせてください。

```python
from scrapling.core._types import ProxyType

def my_strategy(proxies: list, current_index: int) -> tuple[ProxyType, int]:
    ...
```

プロキシのリストと現在のインデックスを受け取り、選んだプロキシと次のインデックスを返します。

次に、独自の戦略の例を示します。

### ランダムに切り替える {#random-rotation}

```python
import random
from scrapling.fetchers import ProxyRotator

def random_strategy(proxies, current_index):
    idx = random.randint(0, len(proxies) - 1)
    return proxies[idx], idx

rotator = ProxyRotator(
    ["http://proxy1:8080", "http://proxy2:8080", "http://proxy3:8080"],
    strategy=random_strategy,
)
```

### 重みを付けて切り替える {#weighted-rotation}

```python
import random

def weighted_strategy(proxies, current_index):
    # First proxy gets 60% of traffic, others split the rest
    weights = [60] + [40 // (len(proxies) - 1)] * (len(proxies) - 1)
    proxy = random.choices(proxies, weights=weights, k=1)[0]
    return proxy, current_index  # Index doesn't matter for weighted

rotator = ProxyRotator(proxies, strategy=weighted_strategy)
```


## リクエストごとにプロキシを指定する {#per-request-proxy-override}

キーワード引数 `proxy=` を渡すと、そのリクエストだけローテーションの選択を上書きできます。

```python
async def parse(self, response: Response):
    # This request uses the rotator's next proxy
    yield response.follow("/page1", callback=self.parse_page)

    # This request uses a specific proxy, bypassing the rotator
    yield response.follow(
        "/special-page",
        callback=self.parse_page,
        proxy="http://special-proxy:8080",
    )
```

特定のページに決まったプロキシが必要な場合に便利です。たとえば、地域限定の内容を取得するために、その地域のプロキシを使えます。

## ブロックされたリクエストへの対応 {#blocked-request-handling}

Spider は、ブロックの検出と再試行に対応しています。デフォルトでは、次の HTTP ステータスコードをブロックとみなします。`401`、`403`、`407`、`429`、`444`、`500`、`502`、`503`、`504`。

再試行は次のように行います。

1. レスポンスを受け取ると、`is_blocked(response)` を呼び出します。
2. ブロックされていたらリクエストをコピーし、`retry_blocked_request()` を呼び出します。再試行前にリクエストを変更できます。
3. リクエストを `dont_filter=True` にして重複排除を省略し、優先度を下げてキューに戻します。すぐに再試行しないようにするためです。
4. これを最大 `max_blocked_retries` 回、デフォルトで 3 回繰り返します。

!!! tip

    1. 再試行時には、以前の `proxy`/`proxies` 引数をリクエストから自動で消します。ローテーターが新しいプロキシを割り当てられるようにするためです。
    2. `max_blocked_retries` はセッションの再試行とは別で、カウンターも共有しません。

### 独自のブロック検出 {#custom-block-detection}

`is_blocked()` をオーバーライドすると、独自の検出処理を追加できます。

```python
class MySpider(Spider):
    name = "my_spider"
    start_urls = ["https://example.com"]

    async def is_blocked(self, response: Response) -> bool:
        # Check status codes (default behavior)
        if response.status in {403, 429, 503}:
            return True

        # Check response content
        body = response.body.decode("utf-8", errors="ignore")
        if "access denied" in body.lower() or "rate limit" in body.lower():
            return True

        return False

    async def parse(self, response: Response):
        yield {"title": response.css("title::text").get("")}
```

### 再試行を変更する {#customizing-retries}

`retry_blocked_request()` をオーバーライドすると、再試行前にリクエストを変更できます。`max_blocked_retries` はブロックされたリクエストの再試行回数を指定し、デフォルトは 3 回です。

```python
from scrapling.spiders import Spider, SessionManager, Request, Response
from scrapling.fetchers import FetcherSession, AsyncStealthySession


class MySpider(Spider):
    name = "my_spider"
    start_urls = ["https://example.com"]
    max_blocked_retries = 5

    def configure_sessions(self, manager: SessionManager) -> None:
        manager.add('requests', FetcherSession(impersonate=['chrome', 'firefox', 'safari']))
        manager.add('stealth', AsyncStealthySession(block_webrtc=True), lazy=True)

    async def retry_blocked_request(self, request: Request, response: Response) -> Request:
        request.sid = "stealth"
        self.logger.info(f"Retrying blocked request: {request.url}")
        return request

    async def parse(self, response: Response):
        yield {"title": response.css("title::text").get("")}
```

この例ではブロックの検出方法は変えず、通常は HTTP リクエストを使います。ブロックされたら、ステルスブラウザに切り替えます。


すべてを組み合わせると、次のようになります。

```python
from scrapling.spiders import Spider, SessionManager, Request, Response
from scrapling.fetchers import FetcherSession, AsyncStealthySession, ProxyRotator


cheap_proxies = ProxyRotator([ "http://proxy1:8080", "http://proxy2:8080"])

# A format acceptable by the browser
expensive_proxies = ProxyRotator([
    {"server": "http://residential_proxy1:8080", "username": "user", "password": "pass"},
    {"server": "http://residential_proxy2:8080", "username": "user", "password": "pass"},
    {"server": "http://mobile_proxy1:8080", "username": "user", "password": "pass"},
    {"server": "http://mobile_proxy2:8080", "username": "user", "password": "pass"},
])


class MySpider(Spider):
    name = "my_spider"
    start_urls = ["https://example.com"]
    max_blocked_retries = 5

    def configure_sessions(self, manager: SessionManager) -> None:
        manager.add('requests', FetcherSession(impersonate=['chrome', 'firefox', 'safari'], proxy_rotator=cheap_proxies))
        manager.add('stealth', AsyncStealthySession(block_webrtc=True, proxy_rotator=expensive_proxies), lazy=True)

    async def retry_blocked_request(self, request: Request, response: Response) -> Request:
        request.sid = "stealth"
        self.logger.info(f"Retrying blocked request: {request.url}")
        return request

    async def parse(self, response: Response):
        yield {"title": response.css("title::text").get("")}
```
この例は、まずデータセンタープロキシなどの安価なプロキシを使います。ブロックされたら、家庭回線やモバイル回線のプロキシなど、品質の高いプロキシで再試行します。
