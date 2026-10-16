---
title: "轮换代理并重试被封锁的抓取请求"
description: "在 Scrapling Spider 中使用代理和轮换策略。检测被封锁的响应、重试请求，并从 HTTP 会话切换到浏览器会话。"
---

# 代理管理与封锁处理 {#proxy-management-and-handling-blocks}

## 简介 {#introduction}

!!! success "前提条件"

    1. 已阅读[入门](getting-started.md)，知道如何创建并运行一个简单的 Spider。
    2. 已阅读[会话](sessions.md)，了解如何配置会话。

大规模抓取时，通常需要在多个代理之间轮换，以避免频率限制和封锁。Scrapling 的 `ProxyRotator` 让这件事更简单。它支持所有会话类型，并能与 Spider 的封锁重试系统配合使用。

如果还不了解代理，或不知道如何选择合适的代理，可以阅读[这篇指南](https://substack.thewebscraping.club/p/everything-about-proxies)。

## ProxyRotator {#proxyrotator}

`ProxyRotator` 类管理一个代理列表，并自动轮换使用。通过 `proxy_rotator` 参数，可以将它传给任意会话类型：

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

每个请求都会自动分配到轮换中的下一个代理。使用的代理保存在 `response.meta["proxy"]` 中，方便追踪每个页面由哪个代理获取。


在浏览器会话中使用时，需要做一些调整：

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

    1. 同一个会话中，不能同时使用 `proxy_rotator` 与固定的 `proxy` 或 `proxies` 参数。配置会话时选择其中一种方式，之后仍可为单个请求覆盖代理，后文会介绍。
    2. 默认情况下，浏览器会话使用一个持久浏览器上下文和一个标签页池。但浏览器无法为每个标签页设置独立代理。因此，使用 `ProxyRotator` 时，Fetcher 会为每个代理自动创建单独的上下文，每个上下文只有一个标签页。任务完成后，标签页和上下文都会关闭。

## 自定义轮换策略 {#custom-rotation-strategies}

`ProxyRotator` 默认循环轮换，按顺序使用代理，到列表末尾后再从头开始。

可以提供自定义策略函数来改变这一行为，但函数必须符合以下签名：

```python
from scrapling.core._types import ProxyType

def my_strategy(proxies: list, current_index: int) -> tuple[ProxyType, int]:
    ...
```

它接收代理列表和当前索引，必须返回所选代理及下一个索引。

下面是几个自定义轮换策略的例子。

### 随机轮换 {#random-rotation}

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

### 加权轮换 {#weighted-rotation}

```python
import random

def weighted_strategy(proxies, current_index):
    # First proxy gets 60% of traffic, others split the rest
    weights = [60] + [40 // (len(proxies) - 1)] * (len(proxies) - 1)
    proxy = random.choices(proxies, weights=weights, k=1)[0]
    return proxy, current_index  # Index doesn't matter for weighted

rotator = ProxyRotator(proxies, strategy=weighted_strategy)
```


## 为单个请求指定代理 {#per-request-proxy-override}

传入关键字参数 `proxy=`，可以为单个请求覆盖轮换器的选择：

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

当某些页面需要特定代理时，这很有用。例如，使用指定地区的代理获取该地区的内容。

## 处理被封锁的请求 {#blocked-request-handling}

Spider 内置封锁检测和重试功能。默认将以下 HTTP 状态码视为封锁：`401`、`403`、`407`、`429`、`444`、`500`、`502`、`503`、`504`。

重试流程如下：

1. 收到响应后，Spider 调用 `is_blocked(response)`。
2. 如果被封锁，就复制请求并调用 `retry_blocked_request()`，让你在重试前修改请求。
3. 重试请求以 `dont_filter=True` 重新加入队列，跳过去重，并降低优先级，避免立即重试。
4. 最多重复 `max_blocked_retries` 次，默认 3 次。

!!! tip

    1. 重试时，请求中原有的 `proxy`/`proxies` 参数会自动清除，让轮换器分配新的代理。
    2. `max_blocked_retries` 与会话自身的重试不同，两者不共用计数器。

### 自定义封锁检测 {#custom-block-detection}

重写 `is_blocked()` 可以添加自己的检测逻辑：

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

### 自定义重试 {#customizing-retries}

重写 `retry_blocked_request()` 可以在重试前修改请求。`max_blocked_retries` 控制被封锁请求的最大重试次数，默认 3 次：

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

上例保留了原有的封锁检测逻辑。Spider 主要使用 HTTP 请求，遇到封锁后才切换到隐身浏览器。


将这些功能组合起来：

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
上例的逻辑是：先用数据中心代理等便宜的代理发送请求，遇到封锁后，再用住宅代理或移动代理等质量更高的代理重试。
