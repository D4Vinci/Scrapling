# Proxy management and handling Blocks

## Introduction

!!! success "Prerequisites"

    1. You've read the [Getting started](getting-started.md) page and know how to create and run a basic spider.
    2. You've read the [Sessions](sessions.md) page and understand how to configure sessions.

When scraping at scale, you'll often need to rotate through multiple proxies to avoid rate limits and blocks. Scrapling's `ProxyRotator` makes this straightforward — it works with all session types and integrates with the spider's blocked request retry system.

If you don't know what a proxy is or how to choose a good one, [this guide can help](https://substack.thewebscraping.club/p/everything-about-proxies).

## ProxyRotator

The `ProxyRotator` class manages a list of proxies and rotates through them automatically. Pass it to any session type via the `proxy_rotator` parameter:

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

Each request automatically gets the next proxy in the rotation. The proxy used is stored in `response.meta["proxy"]` so you can track which proxy fetched which page.


When you use it with browser sessions, you will need some adjustments, like below:

```python
from scrapling.fetchers import AsyncDynamicSession, AsyncStealthySession, ProxyRotator

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

    1. You cannot use the `proxy_rotator` argument together with the static `proxy` or `proxies` parameters on the same session. Pick one approach when configuring the session, and override it per request later if you want, as we will show later.
    2. Remember that by default, all browser-based sessions use a persistent browser context with a pool of tabs. However, since browsers can't set a proxy per tab, when you use a `ProxyRotator`, the fetcher will automatically open a separate context for each proxy, with one tab per context. Once the tab's job is done, both the tab and its context are closed.

## Custom Rotation Strategies

By default, `ProxyRotator` uses cyclic rotation — it iterates through proxies sequentially, wrapping around at the end.

You can provide a custom strategy function to change this behavior, but it has to match the below signature:

```python
from scrapling.core._types import ProxyType

def my_strategy(proxies: list, current_index: int) -> tuple[ProxyType, int]:
    ...
```

It receives the list of proxies and the current index, and must return the chosen proxy and the next index.

Below are some examples of custom rotation strategies you can use.

### Random Rotation

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

### Weighted Rotation

```python
import random

def weighted_strategy(proxies, current_index):
    # First proxy gets 60% of traffic, others split the rest
    weights = [60] + [40 // (len(proxies) - 1)] * (len(proxies) - 1)
    proxy = random.choices(proxies, weights=weights, k=1)[0]
    return proxy, current_index  # Index doesn't matter for weighted

rotator = ProxyRotator(proxies, strategy=weighted_strategy)
```


## Per-Request Proxy Override

You can override the rotator for individual requests by passing `proxy=` as a keyword argument:

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

This is useful when certain pages require a specific proxy (e.g., a geo-located proxy for region-specific content).

## Blocked Request Handling

The spider has built-in blocked request detection and retry. By default, it considers the following HTTP status codes blocked: `401`, `403`, `407`, `429`, `444`, `500`, `502`, `503`, `504`.

The retry system works like this:

1. After a response comes back, the spider calls the `is_blocked(response)` method.
2. If blocked, it copies the request and calls the `retry_blocked_request()` method so you can modify it before retrying.
3. The retried request is re-queued with `dont_filter=True` (bypassing deduplication) and lower priority, so it's not retried right away.
4. This repeats up to `max_blocked_retries` times (default: 3).

!!! tip

    1. On retry, the previous `proxy`/`proxies` kwargs are cleared from the request automatically, so the rotator assigns a fresh proxy.
    2. The `max_blocked_retries` attribute is different than the session retries and doesn't share the counter.

### Custom Block Detection

Override `is_blocked()` to add your own detection logic:

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

### Customizing Retries

Override `retry_blocked_request()` to modify the request before retrying. The `max_blocked_retries` attribute controls how many times a blocked request is retried (default: 3):

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

What happened above is that I left the blocking detection logic unchanged and made the spider mainly use requests until it gets blocked, then it switches to the stealthy browser.


Putting it all together:

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
The above logic is: requests are made with cheap proxies, such as datacenter proxies, until they are blocked, then retried with higher-quality proxies, such as residential or mobile proxies.