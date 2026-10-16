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

建议在回调中使用 `response.follow()` 创建后续请求。相比直接创建 `Request` 对象，它有以下优点：

- **相对 URL** 会自动根据当前页面 URL 解析。
- **Referer 请求头**默认设为当前页面 URL。
- **会话参数**会从原请求继承，包括请求头、代理设置等，但不包括 `method`、`params`、`data`、`json`、`files` 和 `multipart`。因此，跟随链接时会发送普通 GET 请求。
- **回调、会话 ID 和优先级**如果未指定，会从原请求继承。

```python
async def parse(self, response: Response):
    # Minimal - inherits callback, sid, priority from current request
    yield response.follow("/next-page")

    # Override specific fields
    yield response.follow(
        "/product/123",
        callback=self.parse_product,
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
|------|------|--------|------|
| `url` | `str` | *必填* | 要跟随的 URL，可为绝对或相对 URL |
| `sid` | `str` | `""` | 会话 ID，为空时继承原请求的值 |
| `callback` | `callable` | `None` | 回调方法，为 `None` 时继承原请求的值 |
| `priority` | `int` | `None` | 优先级，为 `None` 时继承原请求的值 |
| `dont_filter` | `bool` | `False` | 跳过去重 |
| `meta` | `dict` | `None` | 与响应现有元数据合并的元数据 |
| **`referer_flow`** | `bool` | `True` | 将当前 URL 设为 Referer 请求头 |
| `**kwargs` | | | 与原请求的会话参数合并 |

### 关闭 Referer 传递 {#disabling-referer-flow}

默认情况下，`response.follow()` 会将 `Referer` 请求头设为当前页面 URL。可以这样关闭：

```python
yield response.follow("/page", referer_flow=False)
```

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

使用 `response.follow()` 时，如果没有指定新的优先级，就会继承原请求的优先级。

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

使用 `response.follow()` 时，当前响应的元数据会与新传入的元数据合并，新值优先。

Spider 系统也会自动保存一些元数据。例如，启用代理轮换后，可以通过 `response.meta["proxy"]` 获取该请求使用的代理。
