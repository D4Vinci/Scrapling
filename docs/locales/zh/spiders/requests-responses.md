---
title: "Spider 请求、回调与 Response.follow"
description: "创建抓取请求、传递元数据，并用 response.follow 跟随链接。了解回调、优先级和请求去重。"
---

# 请求与响应 {#requests-responses}

!!! success "前提条件"

    1. 已阅读[入门](getting-started.md)，知道如何创建并运行一个简单的 Spider。

本页详细介绍 `Request` 对象：如何创建请求、在回调之间传递数据、控制优先级和去重，以及用 `response.follow()` 跟随链接。

## Request 对象 {#the-request-object}

`Request` 表示一个待获取的 URL。可以直接创建请求，也可以通过 `response.follow()` 创建：

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

`Request` 支持以下参数：

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `url` | `str` | *必填* | 要获取的 URL |
| `sid` | `str` | `""` | 会话 ID，将请求交给指定会话，详见[会话](sessions.md) |
| `callback` | `callable` | `None` | 处理响应的异步生成器方法，默认为 `parse()` |
| `priority` | `int` | `0` | 值越大，越先处理 |
| `dont_filter` | `bool` | `False` | 为 `True` 时跳过去重，允许重复请求 |
| `meta` | `dict` | `{}` | 传递给响应的任意元数据 |
| `**kwargs` | | | 传给会话获取方法的其他关键字参数，例如 `headers`、`method`、`data` |

额外的关键字参数会直接传给底层会话。例如，发送 POST 请求：

```python
yield Request(
    "https://example.com/api",
    method="POST",
    data={"key": "value"},
    callback=self.parse_result,
)
```

## Response.follow() {#responsefollow}

`response.follow()` 将相对 URL 与当前页面 URL 合并，并创建新的 `Request`。未指定 `sid`、`callback` 或 `priority` 时，它会继承关联的 `response.request` 中的值。显式传入新值即可覆盖。

它不会复制上一个请求的请求头、Cookie、认证信息、代理设置、浏览器选项、其他单次请求参数或元数据。同站点和跨站点链接都遵循此规则。

`sid=""`、`callback=None` 和 `priority=None` 会继承关联的原请求的值。显式设置 `priority=0` 会覆盖原优先级。元数据默认为空，去重保持启用。所选会话的共享设置和 Cookie 存储仍然生效。

在 POST 之后跟随链接会发送 GET，除非传入不同的 `method`。

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

| 参数 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `url` | `str` | *必填* | 要跟随的 URL，可为绝对或相对 URL |
| `sid` | `str` | `""` | 为空时继承原请求的会话 ID |
| `callback` | `callable` | `None` | 为 `None` 时继承原请求的回调 |
| `priority` | `int` / `None` | `None` | 为 `None` 时继承原优先级；显式传入 `0` 也会覆盖原值 |
| `dont_filter` | `bool` | `False` | 跳过去重 |
| `meta` | `dict` | `None` | 仅用于此请求的元数据 |
| `referer_flow` | `bool` | `True` | 将当前页面 URL 设为 Referer |
| `**kwargs` |  |  | 显式传给会话获取方法的参数 |

### 关闭 Referer 传递 {#disabling-referer-flow}

默认情况下，`response.follow()` 会将 HTTP 和浏览器请求的 `Referer` 设为当前页面 URL，同时设置 `google_search=False`，让浏览器使用此 Referer。可以这样关闭：

```python
yield response.follow("/page", referer_flow=False)
```

设置 `referer_flow=False` 后，此方法不会添加 Referer，也不会修改 `google_search`。显式传入的请求头以及会话和浏览器的默认设置仍然生效。为 HTTP 请求设置其他 Referer 的写法：

```python
yield response.follow(
    "/page",
    referer_flow=False,
    headers={"Referer": "https://example.com/"},
)
```

浏览器请求使用 `extra_headers`，并在需要时设置 `google_search=False`。

## 回调 {#callbacks}

回调是 Spider 中用于处理响应的异步生成器方法。它必须通过 `yield` 产出以下三种类型之一：

- **`dict`**：提取的数据项，会加入结果。
- **`Request`**：后续请求，会加入队列。
- **`None`**：静默忽略。

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

    所有回调方法都必须使用 `async def` 定义，并使用 `yield`，不能用 `return` 代替。即使回调只产出数据项，不创建后续请求，也必须是异步生成器。

## 请求优先级 {#request-priority}

优先级值较大的请求会先处理。如果某些页面需要优先处理，可以这样设置：

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

`response.follow()` 的 `priority` 默认为 `None`，会继承原请求的优先级。显式传入的值会覆盖继承的优先级，包括 `priority=0`。

## 去重 {#deduplication}

Spider 会根据 URL、HTTP 方法、请求体和会话 ID 计算指纹，自动去除重复请求。如果两个请求的指纹相同，第二个请求会被静默丢弃。

设置 `dont_filter=True` 可以允许重复请求，例如登录后再次访问同一页面：

```python
yield Request("https://example.com/dashboard", dont_filter=True, callback=self.parse_dashboard)

# Or with response.follow
yield response.follow("/dashboard", dont_filter=True, callback=self.parse_dashboard)
```

通过 Spider 的类属性，可以更精确地控制指纹包含的内容：

| 属性 | 默认值 | 作用 |
|------|--------|------|
| `fp_include_kwargs` | `False` | 将额外的请求参数纳入指纹，也就是传给会话获取方法的参数，例如请求头 |
| `fp_keep_fragments` | `False` | 计算指纹时保留 URL 片段（`#section`） |
| `fp_include_headers` | `False` | 将请求头纳入指纹 |

例如，需要将 `https://example.com/page#section1` 和 `https://example.com/page#section2` 视为不同 URL 时：

```python
class MySpider(Spider):
    name = "my_spider"
    fp_keep_fragments = True
    # ...
```

## 请求元数据 {#request-meta}

`meta` 字典可以在回调之间传递任意数据。当处理一个页面需要用到另一个页面的信息时，这很有用：

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

`response.follow()` 只使用显式传入的 `meta`。如需复用之前的值，请选择并传入需要的键。

Spider 系统也会自动保存一些元数据。例如，启用代理轮换后，可以通过 `response.meta["proxy"]` 获取该请求使用的代理。
