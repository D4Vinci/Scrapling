# Spiders sessions

!!! success "Prerequisites"

    1. You've read the [Getting started](getting-started.md) page and know how to create and run a basic spider.
    2. You're familiar with [Fetchers basics](../fetching/choosing.md) and the differences between HTTP, Dynamic, and Stealthy sessions.

A spider can use multiple fetcher sessions simultaneously — for example, a fast HTTP session for simple pages and a stealth browser session for protected pages. This page shows you how to configure and use sessions.

## What are Sessions?

As you should already know, a session is a pre-configured fetcher instance that stays alive for the duration of the crawl. Instead of creating a new connection or browser for every request, the spider reuses sessions, which is faster and more resource-efficient.

By default, every spider creates a single [FetcherSession](../fetching/static.md). You can add more sessions or swap the default by overriding the `configure_sessions()` method, but you have to use the async version of each session only, as the table shows below:


| Session Type                                    | Use Case                                 |
|-------------------------------------------------|------------------------------------------|
| [FetcherSession](../fetching/static.md)         | Fast HTTP requests, no JavaScript        |
| [AsyncDynamicSession](../fetching/dynamic.md)   | Browser automation, JavaScript rendering |
| [AsyncStealthySession](../fetching/stealthy.md) | Anti-bot bypass, Cloudflare, etc.        |


## Configuring Sessions

Override `configure_sessions()` on your spider to set up sessions. The `manager` parameter is a `SessionManager` instance — use `manager.add()` to register sessions:

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

The `manager.add()` method takes:

| Argument     | Type      | Default    | Description                                  |
|--------------|-----------|------------|----------------------------------------------|
| `session_id` | `str`     | *required* | A name to reference this session in requests |
| `session`    | `Session` | *required* | The session instance                         |
| `default`    | `bool`    | `False`    | Make this the default session                |
| `lazy`       | `bool`    | `False`    | Start the session only when first used       |

!!! note "Notes:"

    1. In all requests, if you don't specify which session to use, the default session is used. The default session is determined in one of two ways:
        1. The first session you add to the managed becomes the default automatically.
        2. The session that gets `default=True` while added to the manager.
    2. The instances you pass of each session don't have to be already started by you; the spider checks on all sessions if they are not already started and starts them.
    3. If you want a specific session to start when used only, then use the `lazy` argument while adding that session to the manager. Example: start the browser only when you need it, not with the spider start.

## Multi-Session Spider

Here's a practical example: use a fast HTTP session for listing pages and a stealth browser for detail pages that have bot protection:

```python
from scrapling.spiders import Spider, Response
from scrapling.fetchers import FetcherSession, AsyncStealthySession

class ProductSpider(Spider):
    name = "products"
    start_urls = ["https://shop.example.com/products"]

    def configure_sessions(self, manager):
        # Fast HTTP for listing pages (default)
        manager.add("http", FetcherSession())

        # Stealth browser for protected product pages
        manager.add("stealth", AsyncStealthySession(
            headless=True,
            network_idle=True,
        ))

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
```

The key is the `sid` parameter — it tells the spider which session to use for each request. When you call `response.follow()` without `sid`, the session ID from the original request is inherited.

Note that the sessions don't have to be from different classes only, but can be the same session, but different instances with different configurations, for example, like below:

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

Or you can separate concerns and keep a session with its cookies/state for specific requests, etc...

## Session Arguments

Extra keyword arguments passed to a `Request` (or through `response.follow(**kwargs)`) are forwarded to the session's fetch method. This lets you customize individual requests without changing the session configuration:

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

    Normally, when you use `FetcherSession`, `Fetcher`, or `AsyncFetcher`, you specify the HTTP method to use with the corresponding method like `.get()` and `.post()`. But while using `FetcherSession` in spiders, you can't do this. By default, the request is an _HTTP GET_ request; if you want to use another HTTP method, you have to pass it to the `method` argument, as in the above example. The reason for this is to unify the `Request` interface across all session types.

For browser sessions (`AsyncDynamicSession`, `AsyncStealthySession`), you can pass browser-specific arguments like `wait_selector`, `page_action`, or `extra_headers`:

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
        sid="browser",
        callback=self.parse_dynamic,
        wait_selector="div.loaded",
        network_idle=True,
    )
```

!!! warning

    Session arguments (**kwargs) passed from the original request are inherited by `response.follow()`. New kwargs take precedence over inherited ones.

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
            yield Request(next_page)

    async def parse_product(self, response: Response):
        yield {
            "name": response.css("h1::text").get(""),
            "price": response.css(".price::text").get(""),
        }
```
!!! info

    No need to mention that, upon spider closure, the manager automatically checks whether any sessions are still running and closes them before closing the spider.