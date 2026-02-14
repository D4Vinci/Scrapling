## Introduction

!!! success "Prerequisites"

    1. You've completed or read the [Fetchers basics](../fetching/choosing.md) page to understand the different fetcher types and when to use each one.
    2. You've completed or read the [Main classes](../parsing/main_classes.md) page to understand the [Selector](../parsing/main_classes.md#selector) and [Response](../fetching/choosing.md#response-object) classes.
    3. You've read the [Architecture](architecture.md) page for a high-level overview of how the spider system works.

The spider system lets you build concurrent, multi-page crawlers in just a few lines of code. If you've used Scrapy before, the patterns will feel familiar. If not, this guide will walk you through everything you need to get started.

## Your First Spider

A spider is a class that defines how to crawl and extract data from websites. Here's the simplest possible spider:

```python
from scrapling.spiders import Spider, Response

class QuotesSpider(Spider):
    name = "quotes"
    start_urls = ["https://quotes.toscrape.com"]

    async def parse(self, response: Response):
        for quote in response.css("div.quote"):
            yield {
                "text": quote.css("span.text::text").get(""),
                "author": quote.css("small.author::text").get(""),
            }
```

Every spider needs three things:

1. **`name`** — A unique identifier for the spider.
2. **`start_urls`** — A list of URLs to start crawling from.
3. **`parse()`** — An async generator method that processes each response and yields results.

The `parse()` method is where the magic happens. You use the same selection methods you'd use with Scrapling's [Selector](../parsing/main_classes.md#selector)/[Response](../fetching/choosing.md#response-object), and `yield` dictionaries to output scraped items.

## Running the Spider

To run your spider, create an instance and call `start()`:

```python
result = QuotesSpider().start()
```

The `start()` method handles all the async machinery internally — no need to worry about event loops. While the spider is running, everything that happens is logged to the terminal, and at the end of the crawl, you get very detailed stats.

Those stats are in the returned `CrawlResult` object, which gives you everything you need:

```python
result = QuotesSpider().start()

# Access scraped items
for item in result.items:
    print(item["text"], "-", item["author"])

# Check statistics
print(f"Scraped {result.stats.items_scraped} items")
print(f"Made {result.stats.requests_count} requests")
print(f"Took {result.stats.elapsed_seconds:.1f} seconds")

# Did the crawl finish or was it paused?
print(f"Completed: {result.completed}")
```

## Following Links

Most crawls need to follow links across multiple pages. Use `response.follow()` to create follow-up requests:

```python
from scrapling.spiders import Spider, Response

class QuotesSpider(Spider):
    name = "quotes"
    start_urls = ["https://quotes.toscrape.com"]

    async def parse(self, response: Response):
        # Extract items from the current page
        for quote in response.css("div.quote"):
            yield {
                "text": quote.css("span.text::text").get(""),
                "author": quote.css("small.author::text").get(""),
            }

        # Follow the "next page" link
        next_page = response.css("li.next a::attr(href)").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)
```

`response.follow()` handles relative URLs automatically — it joins them with the current page's URL. It also sets the current page as the `Referer` header by default.

You can point follow-up requests at different callback methods for different page types:

```python
async def parse(self, response: Response):
    for link in response.css("a.product-link::attr(href)").getall():
        yield response.follow(link, callback=self.parse_product)

async def parse_product(self, response: Response):
    yield {
        "name": response.css("h1::text").get(""),
        "price": response.css(".price::text").get(""),
    }
```

!!! note

    All callback methods must be async generators (using `async def` and `yield`).

## Exporting Data

The `ItemList` returned in `result.items` has built-in export methods:

```python
result = QuotesSpider().start()

# Export as JSON
result.items.to_json("quotes.json")

# Export as JSON with pretty-printing
result.items.to_json("quotes.json", indent=True)

# Export as JSON Lines (one JSON object per line)
result.items.to_jsonl("quotes.jsonl")
```

Both methods create parent directories automatically if they don't exist.

## Filtering Domains

Use `allowed_domains` to restrict the spider to specific domains. This prevents it from accidentally following links to external websites:

```python
class MySpider(Spider):
    name = "my_spider"
    start_urls = ["https://example.com"]
    allowed_domains = {"example.com"}

    async def parse(self, response: Response):
        for link in response.css("a::attr(href)").getall():
            # Links to other domains are silently dropped
            yield response.follow(link, callback=self.parse)
```

Subdomains are matched automatically — setting `allowed_domains = {"example.com"}` also allows `sub.example.com`, `blog.example.com`, etc.

When a request is filtered out, it's counted in `stats.offsite_requests_count` so you can see how many were dropped.

## What's Next

Now that you have the basics, you can explore:

- [Requests & Responses](requests-responses.md) — learn about request priority, deduplication, metadata, and more.
- [Sessions](sessions.md) — use multiple fetcher types (HTTP, browser, stealth) in a single spider.
- [Proxy management & blocking](proxy-blocking.md) — rotate proxies across requests and how to handle blocking in the spider.
- [Advanced features](advanced.md) — concurrency control, pause/resume, streaming, lifecycle hooks, and logging.