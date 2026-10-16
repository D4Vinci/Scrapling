---
title: "在同一个爬虫中使用 HTTP 和浏览器会话"
description: "设置有名称的会话，让 Spider 请求使用 HTTP 或浏览器 Fetcher。复用 Cookie、按需启动会话，并查看 API 历史记录。"
---

# Spider 会话 {#spiders-sessions}

!!! success "前提条件"

    1. 已阅读[入门](getting-started.md)，知道如何创建并运行一个简单的 Spider。
    2. 熟悉 [Fetcher 基础](../fetching/choosing.md)，了解 HTTP 会话和 Stealthy 会话的区别。

一个 Spider 可以同时使用多个 Fetcher 会话。例如，用快速的 HTTP 会话获取简单页面，用隐身浏览器会话获取受保护页面。本页介绍如何配置和使用会话。

## 什么是会话？ {#what-are-sessions}

会话是一个预先配置好的 Fetcher 实例，会在整个抓取过程中保持运行。Spider 会复用会话，而不是为每个请求创建新连接或浏览器。这样速度更快，也更节省资源。

默认情况下，每个 Spider 都会创建一个 [FetcherSession](../fetching/static.md)。重写 `configure_sessions()` 可以添加更多会话，或替换默认会话。这里只能使用各会话的异步版本，如下表所示：


| 会话类型 | 适用场景 |
|----------|----------|
| [FetcherSession](../fetching/static.md) | 快速 HTTP 请求，不运行 JavaScript |
| [AsyncStealthySession](../fetching/stealthy.md) | JavaScript、浏览器自动化、绕过反机器人保护 |


## 配置会话 {#configuring-sessions}

在 Spider 中重写 `configure_sessions()` 来配置会话。参数 `manager` 是一个 `SessionManager` 实例。使用 `manager.add()` 注册会话：

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

`manager.add()` 方法支持以下参数：

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `session_id` | `str` | *必填* | 在请求中引用此会话的名称 |
| `session` | `Session` | *必填* | 会话实例 |
| `default` | `bool` | `False` | 将此会话设为默认会话 |
| `lazy` | `bool` | `False` | 第一次使用时才启动会话 |

!!! note "注意事项"

    1. 如果请求没有指定会话，就会使用默认会话。默认会话通过以下两种方式之一确定：
        1. 第一个加入管理器的会话会自动成为默认会话。
        2. 添加会话时传入 `default=True`。
    2. 不需要自行提前启动传入的会话实例。Spider 会检查所有会话，并启动尚未运行的会话。
    3. 如果希望某个会话只在需要时启动，添加时使用 `lazy` 参数即可。例如，让浏览器在真正需要时才启动，而不是随 Spider 一起启动。

## 多会话 Spider {#multi-session-spider}

下面是一个实际例子：用快速 HTTP 会话获取列表页，用隐身浏览器获取有反机器人保护的详情页：

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

示例保留了浏览器实例，并在会话关闭前，通过 `on_close()` 读取一次已保存的 API 历史记录。记录涵盖所有商品页面，关闭后仍可读取。尚未完成的记录不会被等待，记录数量限制仍然有效。

关键是 `sid` 参数，它告诉 Spider 每个请求应该使用哪个会话。调用 `response.follow()` 时如果未指定 `sid`，就会继承原请求的会话 ID。

会话不必来自不同的类。也可以使用同一个类的多个实例，并为它们设置不同的配置：

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

也可以为某类请求保留一个独立会话，让它保有自己的 Cookie 和状态。

## 会话参数 {#session-arguments}

传给 `Request` 或通过 `response.follow(**kwargs)` 传入的额外关键字参数，会交给会话的获取方法。这样就能单独调整请求，而不必改变会话配置：

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

    通常使用 `FetcherSession`、`Fetcher` 或 `AsyncFetcher` 时，会通过 `.get()`、`.post()` 等方法选择 HTTP 方法。但在 Spider 中使用 `FetcherSession` 时不能这样做。请求默认为 _HTTP GET_；若要使用其他 HTTP 方法，必须通过 `method` 参数指定，如上例所示。这是为了让所有会话类型使用统一的 `Request` 接口。

对于上面多会话示例中注册的 `"stealth"` 会话（`AsyncStealthySession`），可以传入 `wait_selector`、`page_action` 或 `extra_headers` 等浏览器专用参数：

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

    `response.follow()` 会继承原请求的会话参数（**kwargs），但不包括 `method`、`params`、`data`、`json`、`files` 和 `multipart`。因此，POST 请求之后跟随链接时，会发送普通 GET 请求。新传入的参数优先于继承的参数。

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

    Spider 关闭时，管理器会自动检查是否还有运行中的会话，并在 Spider 结束前关闭它们。
