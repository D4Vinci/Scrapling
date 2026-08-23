# Generic Spider Templates

Most crawls fall into one of two patterns: "follow links matching this pattern" or "crawl every URL listed in the site's sitemap". Scrapling ships templates for both so you don't have to hand-write the same `parse()` boilerplate every time.

All templates build on `LinkExtractor`, which pulls URLs out of a `Response` (or filters a single URL via `matches()`). `SitemapSpider` additionally parses sitemap.xml / sitemap_index.xml bodies internally (gzip-compressed or not).

You can use `LinkExtractor` directly inside any plain `Spider.parse()`. The templates just save you the wiring.

## CrawlSpider

`CrawlSpider` follows links automatically based on declarative rules.

```python
from scrapling.spiders import CrawlSpider, CrawlRule, LinkExtractor

class QuotesSpider(CrawlSpider):
    name = "blog"
    start_urls = ["https://quotes.toscrape.com/"]

    def rules(self):
        return [
            CrawlRule(LinkExtractor(allow=r"/author/"), callback=self.parse_author),
            CrawlRule(LinkExtractor(allow=r"/page/\d+/")),  # follow pagination, no callback
        ]

    async def parse_author(self, response):
        yield {
            '.author-title': response.css('.author-title::text').get(),
            "birthday": response.css('.author-born-date::text').get(),
            "url": response.url,
        }

result = QuotesSpider().start()
```

A `CrawlRule` pairs a `LinkExtractor` with an optional `callback` (a bound method on the spider), an optional `priority` override for the dispatched `Request`, and an optional `process_request` (a bound method that mutates each `Request` before it's yielded). The default `parse()` runs every rule against every response and yields a `Request` per matched URL.

If a rule has no callback, the matched URLs fall through to the spider's default `parse()`. This is convenient for pagination: extract the next-page links to keep the crawl going, without needing a separate handler.

### Combining rules with custom logic

Override `parse()` and call `super().parse(response)` to get the rule behavior plus your own yields:

```python
class MySpider(CrawlSpider):
    def rules(self):
        return [CrawlRule(LinkExtractor(allow=r"/posts/"), callback=self.parse_post)]

    async def parse(self, response):
        yield {"page_url": response.url}
        async for req in super().parse(response):
            yield req
```

### Mutating Requests with `process_request`

```python
def add_priority(self, request, response):
    request.priority = 10
    return request

def rules(self):
    return [CrawlRule(
        LinkExtractor(allow=r"/posts/"),
        callback=self.parse_post,
        process_request=self.add_priority,
    )]
```

## SitemapSpider

`SitemapSpider` seeds a crawl from sitemap.xml URLs. It uses the same `rules()` API as `CrawlSpider`, so the mental model is shared.

```python
from scrapling.spiders import SitemapSpider, CrawlRule, LinkExtractor

class MySitemap(SitemapSpider):
    name = "sm"
    sitemap_urls = ["https://example.com/sitemap.xml"]

    def rules(self):
        return [
            CrawlRule(LinkExtractor(allow=r"/posts/"), callback=self.parse_post),
            CrawlRule(LinkExtractor(allow=r"/products/"), callback=self.parse_product),
        ]

    async def parse_post(self, response):
        yield {"title": response.css("h1::text").get()}

    async def parse_product(self, response):
        yield {"sku": response.css(".sku::text").get()}

result = MySitemap().start()
```

### How URLs are dispatched

For each URL in the sitemap, `SitemapSpider` checks every rule's `LinkExtractor.matches(url)` in order. The first matching rule wins, and a `Request` is yielded with that rule's callback. If no rule matches and `rules()` is non-empty, the URL is dropped. If `rules()` returns an empty list, every URL is routed to the spider's `parse()` method, which raises `NotImplementedError` by default if not overridden.

### Sitemap indexes

When `SitemapSpider` encounters a `<sitemapindex>` (a sitemap of sitemaps), it descends into each child sitemap automatically. To filter which child sitemaps to descend into, set `sitemap_follow` to a `LinkExtractor`:

```python
class MySitemap(SitemapSpider):
    name = "sm"
    sitemap_urls = ["https://example.com/sitemap.xml"]
    sitemap_follow = LinkExtractor(allow=r"/posts-sitemap-\d+\.xml")  # only post sitemaps
```

### Robots.txt support

Put a `robots.txt` URL directly in `sitemap_urls` and `SitemapSpider` will detect it, extract every sitemap shown, and follow each one:

```python
class MySitemap(SitemapSpider):
    name = "sm"
    sitemap_urls = ["https://example.com/robots.txt"]
```

### Alternate-language URLs

Set `sitemap_alternate_links = True` to also dispatch `<xhtml:link rel="alternate" hreflang="...">` URLs through your rules.

## XMLFeedSpider

`XMLFeedSpider` iterates over the nodes of an XML feed (RSS, Atom, product feeds, etc.). Set `itertag` to the node name you want (default: `"item"`) and override `parse_node()`, which is called once per matching node:

```python
from scrapling.spiders import XMLFeedSpider

class RSSSpider(XMLFeedSpider):
    name = "rss"
    start_urls = ["https://example.com/feed.xml"]
    itertag = "item"

    async def parse_node(self, response, node):
        yield {
            "title": node.findtext("title"),
            "link": node.findtext("link"),
            "date": node.findtext("pubDate"),
        }

result = RSSSpider().start()
```

Like the other callbacks, `parse_node()` can also yield `Request` objects (for example, `response.follow(node.findtext("link"), callback=self.parse_post)`) to crawl into the pages the feed points to.

### How nodes are matched and parsed

Each node passed to `parse_node()` is an `lxml` element with all namespaces stripped, so `node.findtext("title")`, `node.find("thumbnail").get("url")`, and case-sensitive `node.xpath(...)` work on any feed without namespace maps. A plain `itertag` like `"entry"` matches nodes by name regardless of their namespace, which is what you want for Atom and most namespaced feeds. To match a node in one specific namespace, use a prefixed `itertag` and define the prefix in `namespaces`:

```python
class ThumbnailSpider(XMLFeedSpider):
    name = "thumbs"
    start_urls = ["https://example.com/feed.xml"]
    itertag = "media:thumbnail"
    namespaces = (("media", "http://search.yahoo.com/mrss/"),)

    async def parse_node(self, response, node):
        yield {"thumbnail": node.get("url")}
```

Gzipped feeds (`.xml.gz` or served with a gzip content-type) are decompressed automatically with the same protections the sitemap spider uses, and malformed XML logs a warning instead of crashing the crawl.

## CSVFeedSpider

`CSVFeedSpider` iterates over the rows of a CSV feed. Override `parse_row()`, which receives each row as a dictionary keyed by the column names:

```python
from scrapling.spiders import CSVFeedSpider

class PriceSpider(CSVFeedSpider):
    name = "prices"
    start_urls = ["https://example.com/products.csv"]

    async def parse_row(self, response, row):
        yield {"product": row["title"], "price": float(row["price"])}

result = PriceSpider().start()
```

By default, the first row of the feed is used as the header. If the feed has no header row, set `headers` to the column names yourself, and use `delimiter`/`quotechar` for feeds that don't follow the standard comma format:

```python
class PriceSpider(CSVFeedSpider):
    name = "prices"
    start_urls = ["https://example.com/products.csv"]
    headers = ["title", "price", "url"]
    delimiter = ";"
```

Gzipped feeds are decompressed automatically here as well, as shown above for **XMLFeedSpider**.

## SiteToMarkdownSpider

`SiteToMarkdownSpider` builds on **CrawlSpider** to crawl a website and convert every page to clean, LLM-ready Markdown, yielding one item per page and optionally writing one Markdown file per page:

```python
from scrapling.spiders import SiteToMarkdownSpider

class DocsSpider(SiteToMarkdownSpider):
    name = "docs"
    start_urls = ["https://example.com/docs/"]
    allowed_domains = {"example.com"}
    output_dir = "docs_markdown"

result = DocsSpider().start()
```

It requires `allowed_domains` to keep the crawl bound to the target website. The full guide, including all its options and how to feed the output to RAG pipelines, is on the [Building RAG systems](../ai/building-rag-systems.md) page.

## Using `LinkExtractor` directly

You don't have to use the templates. `LinkExtractor` works inside any plain `Spider`:

```python
from scrapling.spiders import Spider, LinkExtractor

class CustomSpider(Spider):
    name = "custom"
    start_urls = ["https://example.com"]

    def __init__(self):
        super().__init__()
        self._links = LinkExtractor(allow=r"/posts/", deny_domains="ads.example.com")

    async def parse(self, response):
        for url in self._links.extract(response):
            yield response.follow(url, callback=self.parse_post)

    async def parse_post(self, response):
        yield {"title": response.css("h1::text").get()}
```

## LinkExtractor reference

| Argument          | Default              | Description                                                                                       |
|-------------------|----------------------|---------------------------------------------------------------------------------------------------|
| `allow`           | `()`                 | URL patterns to keep. Empty means "match all". String, compiled `Pattern`, or iterable of either. |
| `deny`            | `()`                 | URL patterns to drop. Always overrides `allow`.                                                   |
| `allow_domains`   | `()`                 | Hostnames to keep. Subdomains match automatically (`example.com` matches `api.example.com`).      |
| `deny_domains`    | `()`                 | Hostnames to drop.                                                                                |
| `restrict_css`    | `()`                 | CSS selectors that scope DOM extraction to a region.                                              |
| `restrict_xpath`  | `()`                 | XPath selectors that scope DOM extraction to a region.                                            |
| `tags`            | `("a", "area")`      | Element tags to look for links in.                                                                |
| `attrs`           | `("href",)`          | Attributes on those tags to read URLs from.                                                       |
| `canonicalize`    | `True`               | Sort query params and normalize the path.                                                         |
| `strip`           | `True`               | Strip whitespace from extracted URLs.                                                             |
| `keep_fragment`   | `False`              | Preserve the `#fragment` when canonicalizing.                                                     |
| `deny_extensions` | `IGNORED_EXTENSIONS` | File extensions to drop (pdf, zip, images, video, etc.).                                          |
| `process`         | `None`               | Optional callable applied to each extracted URL before filtering. Return a falsy value to drop.   |

`LinkExtractor.extract(response)` returns a `list[str]` of absolute, filtered, deduped URLs.

`LinkExtractor.matches(url)` returns a `bool` - the URL-only filter (allow/deny/domain/extension), used by `SitemapSpider` to dispatch URLs without a `Response`.
