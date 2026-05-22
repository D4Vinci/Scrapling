# Using Scrapling with Scrapy

Scrapy remains responsible for scheduling, networking, and item pipelines. This integration adds an **optional** bridge so each Scrapy response can be turned into Scrapling’s [`Response`](../api-reference/response.md) (the same type fetchers return): one object for CSS, XPath, text helpers, and [adaptive](../parsing/adaptive.md) parsing when you enable it.

## Install

```bash
pip install "scrapling[scrapy]"
```

Core Scrapling does not depend on Scrapy; the extra pulls in a supported **Scrapy 2.x** release.

## What this is not (v1)

- It does **not** replace Scrapy’s built-in **parsel** implementation: `response.css` / `response.xpath` on the Scrapy object are unchanged and keep returning parsel types.
- It does **not** try to be a drop-in swap for `response.selector`. Instead you use a **second** object (the Scrapling `Response`) for Scrapling-specific behavior.

## Factory: `scrapling_response_from_scrapy`

Useful in tests, one-off scripts, or custom middleware:

```python
from scrapy.http import HtmlResponse
from scrapling.contrib.scrapy import scrapling_response_from_scrapy

def parse(self, response):
    sl = scrapling_response_from_scrapy(response, adaptive=False)
    yield {"title": sl.css("title::text").get(default="")}
```

`scrapling_response_from_scrapy` forwards keyword arguments to [`Selector`](../api-reference/selector.md) (`adaptive`, `storage_args`, `keep_comments`, `adaptive_domain`, …).

### Memory / CPU note

Scrapy may already hold a parsel tree for the same HTML. Building a Scrapling `Response` **parses the body again** with lxml. For very large documents, prefer using **either** parsel **or** Scrapling for that page when possible.

### Adaptive storage with several spiders

[`SQLiteStorageSystem`](../development/adaptive_storage_system.md) is thread-safe, but you should still give each spider (or crawl) its own `storage_file` in `storage_args` so databases stay isolated.

```python
sl = scrapling_response_from_scrapy(
    response,
    adaptive=True,
    storage_args={"storage_file": f"/tmp/{self.name}.sqlite", "url": response.url},
)
```

If you extend storage with manual connections, close them in Scrapy’s `closed()` spider hook.

### Logging

Scrapling’s `Response` constructor emits an **INFO** log line per built object. In large crawls you may want to set the `scrapling` logger to `WARNING` in Scrapy’s `LOGGING` configuration.

## Middleware: `ScraplingMiddleware`

Attach the bridge automatically so callbacks read a pre-built object from `response.meta`.

`settings.py`:

```python
DOWNLOADER_MIDDLEWARES = {
    # After HttpCompressionMiddleware (usually 590) so bodies are decoded when needed.
    "scrapling.contrib.scrapy.middleware.ScraplingMiddleware": 585,
}

SCRAPLING_ENABLED = True
SCRAPLING_META_KEY = "scrapling"  # key in response.meta
SCRAPLING_SELECTOR_KWARGS = {
    "adaptive": False,
    # "storage_args": {"storage_file": "/tmp/myspider.sqlite", "url": None},  # set url per-response if needed
}
```

`SCRAPLING_SELECTOR_KWARGS` is merged into every `scrapling_response_from_scrapy(...)` call. Keys mirror scrapy settings constants:

- `scrapling.contrib.scrapy.middleware.SCRAPLING_ENABLED`
- `scrapling.contrib.scrapy.middleware.SCRAPLING_META_KEY`
- `scrapling.contrib.scrapy.middleware.SCRAPLING_SELECTOR_KWARGS`

Spider callback:

```python
def parse(self, response):
    sl = response.meta["scrapling"]
    yield {"h1": sl.css("h1::text").get()}
```

## Authenticating to target sites

Use normal Scrapy mechanisms (middlewares, `meta`, cookies, custom headers). Pass the resulting Scrapy `response` into `scrapling_response_from_scrapy` or through the middleware; Scrapling only sees the final body and headers you already retrieved.
