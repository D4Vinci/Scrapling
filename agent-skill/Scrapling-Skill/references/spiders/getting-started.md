# Getting started

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

1. **`name`**: A unique identifier for the spider.
2. **`start_urls`**: A list of URLs to start crawling from.
3. **`parse()`**: An async generator method that processes each response and yields results.

The `parse()` method processes each response. You use the same selection methods you'd use with Scrapling's [Selector](../parsing/main_classes.md#selector)/[Response](../fetching/choosing.md#response-object), and `yield` dictionaries to output scraped items.

## Running the Spider

To run your spider, create an instance and call `start()`:

```python
result = QuotesSpider().start()
```

The `start()` method handles all the async machinery internally, so there is no need to worry about event loops. While the spider is running, everything that happens is logged to the terminal, and at the end of the crawl, you get very detailed stats.

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

`response.follow()` handles relative URLs automatically by joining them with the current page's URL. It also sets the current page as the `Referer` header by default.

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

**Note:** All callback methods must be async generators (using `async def` and `yield`).

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

# Export as CSV or XML
result.items.to_csv("quotes.csv")
result.items.to_xml("quotes.xml")
```

All of them create parent directories automatically if they don't exist.

`to_csv()` writes a column for every key found across your items, so items that don't all share the same keys are still exported with the missing cells left empty. Pass `fields=[...]` to pick the columns and their order yourself, or `delimiter="\t"` for a TSV file. `to_xml()` wraps each item in an `<item>` element inside an `<items>` root, both renameable through `root_tag` and `item_tag`.

In both formats, values that aren't simple scalars (a nested dictionary or a list) are written as JSON so nothing is silently dropped.

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

Subdomains are matched automatically, so setting `allowed_domains = {"example.com"}` also allows `sub.example.com`, `blog.example.com`, etc.

When a request is filtered out, it's counted in `stats.offsite_requests_count` so you can see how many were dropped.

## Robots.txt Compliance

Set `robots_txt_obey = True` to make the spider respect robots.txt rules before crawling any domain:

```python
class PoliteSpider(Spider):
    name = "polite"
    start_urls = ["https://example.com"]
    robots_txt_obey = True

    async def parse(self, response: Response):
        for link in response.css("a::attr(href)").getall():
            yield response.follow(link, callback=self.parse)
```

When enabled, the spider will:

1. **Pre-fetch robots.txt** for all domains in `start_urls` before the crawl begins (concurrently).
2. **Check every request** against the domain's robots.txt `Disallow` rules. Disallowed requests are silently dropped and counted in `stats.robots_disallowed_count`.
3. **Respect `Crawl-delay` and `Request-rate` directives** by taking the maximum of the directive and your configured `download_delay`. This means robots.txt delays never reduce your configured delay, only increase it when needed.

Robots.txt files are fetched using the spider's default session and cached per domain for the entire crawl. Domains discovered mid-crawl (not in `start_urls`) have their robots.txt fetched on the first request to that domain.

**Note:** `robots_txt_obey` is turned off by default. It does not affect your concurrency settings -- only the delay between requests is adjusted.

If you don't want to pick a `download_delay` by hand, set `autothrottle_enabled = True` and the spider will tune the delay of every domain on its own from how fast it responds, backing off when it gets blocked. See [AutoThrottle](advanced.md#autothrottle).

