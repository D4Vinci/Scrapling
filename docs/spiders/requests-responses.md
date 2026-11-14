---
title: "Spider Requests, Callbacks and Response.follow"
description: "Create crawl requests, pass metadata and follow links with response.follow. Learn callbacks, priorities and request deduplication."
---

# Requests & Responses

!!! success "Prerequisites"

    1. You've read the [Getting started](getting-started.md) page and know how to create and run a basic spider.

This page covers the `Request` object in detail: how to construct requests, pass data between callbacks, control priority and deduplication, and use `response.follow()` for link-following.

## The Request Object

A `Request` represents a URL to be fetched. You create requests either directly or via `response.follow()`:

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

Here are all the arguments you can pass to `Request`:

| Argument      | Type       | Default    | Description                                                                                           |
|---------------|------------|------------|-------------------------------------------------------------------------------------------------------|
| `url`         | `str`      | *required* | The URL to fetch                                                                                      |
| `sid`         | `str`      | `""`       | Session ID - routes the request to a specific session (see [Sessions](sessions.md))                   |
| `callback`    | `callable` | `None`     | Async generator method to process the response. Defaults to `parse()`                                 |
| `priority`    | `int`      | `0`        | Higher values are processed first                                                                     |
| `dont_filter` | `bool`     | `False`    | If `True`, skip deduplication (allow duplicate requests)                                              |
| `meta`        | `dict`     | `{}`       | Arbitrary metadata passed through to the response                                                     |
| `**kwargs`    |            |            | Additional keyword arguments passed to the session's fetch method (e.g., `headers`, `method`, `data`) |

Any extra keyword arguments are forwarded directly to the underlying session. For example, to make a POST request:

```python
yield Request(
    "https://example.com/api",
    method="POST",
    data={"key": "value"},
    callback=self.parse_result,
)
```

## Response.follow()

`response.follow()` joins a relative URL with the current page URL and creates a new `Request`. When you leave `sid`, `callback`, or `priority` unset, it uses those values from the attached `response.request`. You can pass new values to override them.

Headers, cookies, authentication, proxy settings, browser options, and metadata are not copied from the previous request. Pass the fetch options and metadata that the next request needs. This applies to both same-site and cross-site links.

Metadata starts empty and duplicate filtering stays enabled. Shared session settings and cookie jars still apply. Referer flow remains enabled by default.

Following a link after a POST sends a GET unless you pass a different `method`.

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

| Argument       | Type            | Default    | Description                                                |
|----------------|-----------------|------------|------------------------------------------------------------|
| `url`          | `str`           | *required* | URL to follow (absolute or relative)                       |
| `sid`          | `str`           | `""`       | Empty inherits the parent session ID                       |
| `callback`     | `callable`      | `None`     | `None` inherits the parent callback                        |
| `priority`     | `int` or `None` | `None`     | `None` inherits parent priority; explicit `0` overrides it |
| `dont_filter`  | `bool`          | `False`    | Skip deduplication                                         |
| `meta`         | `dict`          | `None`     | Metadata for this request only                             |
| `referer_flow` | `bool`          | `True`     | Set the current page URL as Referer                        |
| `**kwargs`     |                 |            | Explicit arguments passed to the session's fetch method    |

### Disabling Referer Flow {#disabling-referer-flow}

By default, `response.follow()` sets the current page URL as `Referer` for HTTP and browser requests. It also sets `google_search=False` so the browser uses this Referer. To disable this behavior:

```python
yield response.follow("/page", referer_flow=False)
```

With `referer_flow=False`, the helper does not add a Referer or change `google_search`. Headers you pass and session or browser defaults still apply. To set a different Referer for an HTTP request:

```python
yield response.follow(
    "/page",
    referer_flow=False,
    headers={"Referer": "https://example.com/"},
)
```

For a browser request, use `extra_headers` and set `google_search=False` if needed.

## Callbacks

Callbacks are async generator methods on your spider that process responses. They must `yield` one of three types:

- **`dict`** - A scraped item, added to the results
- **`Request`** - A follow-up request, added to the queue
- **`None`** - Silently ignored

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

!!! tip "Note:"

    All callback methods must be `async def` and use `yield` (not `return`). Even if a callback only yields items with no follow-up requests, it must still be an async generator.

## Request Priority

Requests with higher priority values are processed first. This is useful when some pages are more important to be processed first before others:

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

`response.follow()` inherits priority from the attached request when `priority` is `None`. Pass a number, including `0`, to override it.

## Deduplication

The spider automatically deduplicates requests based on a fingerprint computed from the URL, HTTP method, request body, and session ID. If two requests produce the same fingerprint, the second one is silently dropped.

To allow duplicate requests (e.g., re-visiting a page after login), set `dont_filter=True`:

```python
yield Request("https://example.com/dashboard", dont_filter=True, callback=self.parse_dashboard)

# Or with response.follow
yield response.follow("/dashboard", dont_filter=True, callback=self.parse_dashboard)
```

You can fine-tune what goes into the fingerprint using class attributes on your spider:

| Attribute            | Default | Effect                                                                                                          |
|----------------------|---------|-----------------------------------------------------------------------------------------------------------------|
| `fp_include_kwargs`  | `False` | Include extra request kwargs (arguments you passed to the session fetch, like headers, etc.) in the fingerprint |
| `fp_keep_fragments`  | `False` | Keep URL fragments (`#section`) when computing fingerprints                                                     |
| `fp_include_headers` | `False` | Include request headers in the fingerprint                                                                      |

For example, if you need to treat `https://example.com/page#section1` and `https://example.com/page#section2` as different URLs:

```python
class MySpider(Spider):
    name = "my_spider"
    fp_keep_fragments = True
    # ...
```

## Request Meta

The `meta` dictionary lets you pass arbitrary data between callbacks. This is useful when you need context from one page to process another:

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

`response.follow()` only uses the `meta` you pass. To carry a value forward, select it explicitly, such as `meta={"category": response.meta["category"]}`.

The spider system also automatically stores some metadata. For example, the proxy used for a request is available as `response.meta["proxy"]` when proxy rotation is enabled.
