---
title: "用于链接、Sitemap、Feed 和 Markdown 的 Spider 模板"
description: "选择 CrawlSpider、SitemapSpider、XMLFeedSpider、CSVFeedSpider 或 ContentSpider。设置规则，收集页面、Feed 数据行或 Markdown 文档集。"
---

# 通用 Spider 模板 {#generic-spider-templates}

大多数抓取任务属于两种模式之一：“跟随符合指定模式的链接”，或“抓取网站 Sitemap 中列出的所有 URL”。Scrapling 为这两种情况提供了模板，避免每次都重写相同的 `parse()` 基础代码。

`CrawlSpider` 和 `SitemapSpider` 都基于 `LinkExtractor`。它能从 `Response` 中提取 URL，也能通过 `matches()` 过滤单个 URL。`SitemapSpider` 还会在内部解析 sitemap.xml 和 sitemap_index.xml 的内容，无论是否经过 gzip 压缩。

也可以在普通的 `Spider.parse()` 中直接使用 `LinkExtractor`。模板只是帮你省去连接这些组件的工作。

## CrawlSpider {#crawlspider}

`CrawlSpider` 会根据声明的规则自动跟随链接。

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

一条 `CrawlRule` 将 `LinkExtractor` 与可选的 `callback` 配对。回调是 Spider 上的绑定方法。规则还可包含 `priority`，用于覆盖生成的 `Request` 的优先级，以及 `process_request`，用于在产出每个 `Request` 前修改它，后者也是一个绑定方法。默认的 `parse()` 会对每个响应应用所有规则，并为每个匹配的 URL 产出一个 `Request`。

如果规则没有回调，匹配的 URL 会交给 Spider 默认的 `parse()`。这很适合分页：提取下一页链接即可继续抓取，无需单独编写处理方法。

### 抓取顺序 {#crawl-order}

在 `CrawlSpider` 或其子类（包括 `ContentSpider`）中设置 `crawl_strategy`，可以选择下一条待处理请求：

| `crawl_strategy` | `Request.priority` 相同时的顺序 |
|------------------|--------------------------------|
| `"bfs"`（默认） | 最早入队的请求优先 |
| `"dfs"` | 最晚入队的请求优先 |

调度器始终先处理 `Request.priority` 较高的请求。这个策略只决定优先级相同的请求之间的顺序。

设置 `concurrent_requests = 1`，即可按所选队列顺序逐个处理请求。重复 URL 仍会被过滤；再次发现同一个 URL 不会改变其请求在队列中的位置。并发请求可能以不同顺序完成，不同层级或分支也可能同时处理。

从检查点恢复时，请保持相同的 `crawl_strategy`。

### 将规则与自定义逻辑结合 {#combining-rules-with-custom-logic}

重写 `parse()` 并调用 `super().parse(response)`，即可同时使用规则和自己的产出逻辑：

```python
class MySpider(CrawlSpider):
    def rules(self):
        return [CrawlRule(LinkExtractor(allow=r"/posts/"), callback=self.parse_post)]

    async def parse(self, response):
        yield {"page_url": response.url}
        async for req in super().parse(response):
            yield req
```

### 用 `process_request` 修改请求 {#mutating-requests-with-process_request}

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

## SitemapSpider {#sitemapspider}

`SitemapSpider` 从 sitemap.xml 中的 URL 开始抓取。它使用与 `CrawlSpider` 相同的 `rules()` API，因此用法也相同。

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

### URL 的分配方式 {#how-urls-are-dispatched}

对于 Sitemap 中的每个 URL，`SitemapSpider` 会依次检查各规则的 `LinkExtractor.matches(url)`。第一条匹配的规则生效，并产出使用该规则回调的 `Request`。如果没有规则匹配，且 `rules()` 非空，该 URL 会被丢弃。如果 `rules()` 返回空列表，所有 URL 都会交给 Spider 的 `parse()` 方法。若未重写此方法，它默认会抛出 `NotImplementedError`。

### Sitemap 索引 {#sitemap-indexes}

遇到 `<sitemapindex>`，也就是列出其他 Sitemap 的索引时，`SitemapSpider` 会自动进入每个子 Sitemap。可以将 `sitemap_follow` 设为一个 `LinkExtractor`，过滤要跟随的子 Sitemap：

```python
class MySitemap(SitemapSpider):
    name = "sm"
    sitemap_urls = ["https://example.com/sitemap.xml"]
    sitemap_follow = LinkExtractor(allow=r"/posts-sitemap-\d+\.xml")  # only post sitemaps
```

### robots.txt 支持 {#robotstxt-support}

将 `robots.txt` 的 URL 直接放入 `sitemap_urls`，`SitemapSpider` 会自动识别它，提取其中列出的所有 Sitemap，并逐个跟随：

```python
class MySitemap(SitemapSpider):
    name = "sm"
    sitemap_urls = ["https://example.com/robots.txt"]
```

### 其他语言的 URL {#alternate-language-urls}

设置 `sitemap_alternate_links = True`，也会通过你的规则处理 `<xhtml:link rel="alternate" hreflang="...">` 中的 URL。

## XMLFeedSpider {#xmlfeedspider}

`XMLFeedSpider` 遍历 XML Feed 中的节点，例如 RSS、Atom 和商品 Feed。将 `itertag` 设为需要的节点名称，默认为 `"item"`，并重写 `parse_node()`。每个匹配节点都会调用一次此方法：

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

与其他回调一样，`parse_node()` 也可以产出 `Request` 对象，例如 `response.follow(node.findtext("link"), callback=self.parse_post)`，以抓取 Feed 链接指向的页面。

### 节点匹配与解析 {#how-nodes-are-matched-and-parsed}

传给 `parse_node()` 的每个节点都是去除了所有命名空间的 `lxml` 元素。因此，`node.findtext("title")`、`node.find("thumbnail").get("url")` 和区分大小写的 `node.xpath(...)` 都能直接使用，无需命名空间映射。简单的 `itertag`，例如 `"entry"`，会按节点名称匹配，不考虑命名空间。这适合 Atom 和大多数带命名空间的 Feed。若要匹配某个特定命名空间中的节点，请使用带前缀的 `itertag`，并在 `namespaces` 中定义该前缀：

```python
class ThumbnailSpider(XMLFeedSpider):
    name = "thumbs"
    start_urls = ["https://example.com/feed.xml"]
    itertag = "media:thumbnail"
    namespaces = (("media", "http://search.yahoo.com/mrss/"),)

    async def parse_node(self, response, node):
        yield {"thumbnail": node.get("url")}
```

gzip 压缩的 Feed（`.xml.gz`，或使用 gzip 内容类型返回的 Feed）会自动解压，并采用与 Sitemap Spider 相同的保护措施。格式错误的 XML 只会记录警告，不会导致抓取崩溃。

## CSVFeedSpider {#csvfeedspider}

`CSVFeedSpider` 遍历 CSV Feed 中的数据行。重写 `parse_row()`，它会接收每一行对应的字典，键为列名：

```python
from scrapling.spiders import CSVFeedSpider

class PriceSpider(CSVFeedSpider):
    name = "prices"
    start_urls = ["https://example.com/products.csv"]

    async def parse_row(self, response, row):
        yield {"product": row["title"], "price": float(row["price"])}

result = PriceSpider().start()
```

默认使用 Feed 的第一行作为表头。如果没有表头，可自行通过 `headers` 指定列名。对于不使用标准逗号格式的 Feed，可以设置 `delimiter`/`quotechar`：

```python
class PriceSpider(CSVFeedSpider):
    name = "prices"
    start_urls = ["https://example.com/products.csv"]
    headers = ["title", "price", "url"]
    delimiter = ";"
```

这里也会自动解压 gzip 格式的 Feed，与上面的 **XMLFeedSpider** 相同。

<a id="sitetomarkdownspider"></a>

## ContentSpider {#contentspider}

`ContentSpider` 基于 **CrawlSpider**，抓取网站并将每个页面转换为适合 LLM 使用的干净 Markdown。每个页面产出一个数据项，还可以选择为每页写入一个 Markdown 文件：

```python
from scrapling.spiders import ContentSpider

class DocsSpider(ContentSpider):
    name = "docs"
    start_urls = ["https://example.com/docs/"]
    allowed_domains = {"example.com"}
    output_dir = "docs_markdown"

result = DocsSpider().start()
```

它要求设置 `allowed_domains`，以将抓取范围限制在目标网站内。完整指南、所有选项以及如何将输出交给 RAG 流水线，详见[构建 RAG 系统](../ai/building-rag-systems.md)。

## 直接使用 `LinkExtractor` {#using-linkextractor-directly}

不一定要使用模板。`LinkExtractor` 可以在任何普通 `Spider` 中使用：

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

## LinkExtractor 参数参考 {#linkextractor-reference}

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `allow` | `()` | 要保留的 URL 模式。为空表示全部匹配。可传字符串、编译后的 `Pattern`，或包含这两者的可迭代对象。 |
| `deny` | `()` | 要丢弃的 URL 模式，始终优先于 `allow`。 |
| `allow_domains` | `()` | 要保留的主机名，自动匹配子域名（`example.com` 也匹配 `api.example.com`）。 |
| `deny_domains` | `()` | 要丢弃的主机名。 |
| `restrict_css` | `()` | 将 DOM 提取范围限制在指定区域的 CSS 选择器。 |
| `restrict_xpath` | `()` | 将 DOM 提取范围限制在指定区域的 XPath 选择器。 |
| `tags` | `("a", "area")` | 要从中查找链接的元素标签。 |
| `attrs` | `("href",)` | 从这些标签的哪些属性中读取 URL。 |
| `canonicalize` | `True` | 排序查询参数，并规范化路径。 |
| `strip` | `True` | 去除所提取 URL 两端的空白。 |
| `keep_fragment` | `False` | 规范化时保留 `#fragment`。 |
| `deny_extensions` | `IGNORED_EXTENSIONS` | 要丢弃的文件扩展名，例如 PDF、ZIP、图片和视频。 |
| `process` | `None` | 过滤前对每个提取的 URL 调用的可选函数。返回假值（falsy）时丢弃该 URL。 |

`LinkExtractor.extract(response)` 返回一个 `list[str]`，其中包含已过滤且去重的绝对 URL。

`LinkExtractor.matches(url)` 返回 `bool`，只根据 URL 的允许与拒绝规则、域名和扩展名进行过滤。`SitemapSpider` 用它在没有 `Response` 的情况下分配 URL。
