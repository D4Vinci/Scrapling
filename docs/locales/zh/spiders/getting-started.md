---
title: "用 Scrapling 创建第一个 Python 网络爬虫"
description: "创建一个能提取数据、跟随分页链接并导出结果的 Spider。了解起始 URL、回调、域名限制和 robots.txt 设置。"
---

# 入门 {#getting-started}

## 简介 {#introduction}

!!! success "前提条件"

    1. 已阅读 [Fetcher 基础](../fetching/choosing.md)，了解不同 Fetcher 的类型和适用场景。
    2. 已阅读[主要类](../parsing/main_classes.md)，了解 [Selector](../parsing/main_classes.md#selector) 和 [Response](../fetching/choosing.md#response-object) 类。
    3. 已阅读[架构](architecture.md)，大致了解 Spider 系统的工作方式。

Spider 系统只需几行代码，就能创建并发抓取多个页面的爬虫。如果用过 Scrapy，你会很熟悉这些用法。如果没有，本指南会介绍入门所需的内容。

## 第一个 Spider {#your-first-spider}

Spider 是一个类，用来定义如何抓取网站并提取数据。下面是最简单的 Spider：

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

每个 Spider 都需要三个部分：

1. **`name`**：Spider 的唯一名称。
2. **`start_urls`**：开始抓取的 URL 列表。
3. **`parse()`**：处理每个响应并产出结果的异步生成器方法。

主要的处理逻辑写在 `parse()` 方法中。这里使用的选择方法与 Scrapling 的 [Selector](../parsing/main_classes.md#selector)/[Response](../fetching/choosing.md#response-object) 相同，并通过 `yield` 输出字典形式的数据项。

## 运行 Spider {#running-the-spider}

创建实例并调用 `start()`，即可运行 Spider：

```python
result = QuotesSpider().start()
```

`start()` 方法会在内部处理所有异步操作，无需自行管理事件循环。Spider 运行时，所有活动都会记录到终端。抓取结束后，还会提供详细的统计信息。

这些统计信息都在返回的 `CrawlResult` 对象中：

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

## 跟随链接 {#following-links}

大多数抓取任务需要跟随链接访问多个页面。使用 `response.follow()` 创建后续请求：

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

`response.follow()` 会自动将相对 URL 与当前页面的 URL 合并。默认情况下，它还会将当前页面的 URL 设为 `Referer` 请求头。

对于不同类型的页面，可以让后续请求使用不同的回调方法：

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

    所有回调方法都必须是异步生成器，也就是使用 `async def` 和 `yield`。

## 导出数据 {#exporting-data}

`result.items` 返回的 `ItemList` 提供了内置导出方法：

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

如果父目录不存在，这些方法都会自动创建。

`to_csv()` 会为所有数据项中出现的每个键创建一列。因此，即使数据项的键不同，也能正常导出，缺少的单元格会留空。传入 `fields=[...]` 可自行选择列及其顺序，传入 `delimiter="\t"` 可生成 TSV 文件。`to_xml()` 会将每个数据项放在 `<item>` 元素中，并以 `<items>` 为根元素。可以通过 `root_tag` 和 `item_tag` 修改这两个名称。

这两种格式都会将非简单标量值，例如嵌套字典或列表，写成 JSON，避免数据被悄悄丢弃。

## 限制域名 {#filtering-domains}

使用 `allowed_domains` 将 Spider 限制在指定域名内，避免意外跟随链接访问外部网站：

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

子域名会自动匹配。例如，设置 `allowed_domains = {"example.com"}` 后，也会允许 `sub.example.com`、`blog.example.com` 等子域名。

被过滤掉的请求会计入 `stats.offsite_requests_count`，方便查看丢弃了多少请求。

## 遵守 robots.txt {#robotstxt-compliance}

设置 `robots_txt_obey = True`，让 Spider 在抓取任何域名前先遵守其 robots.txt 规则：

```python
class PoliteSpider(Spider):
    name = "polite"
    start_urls = ["https://example.com"]
    robots_txt_obey = True

    async def parse(self, response: Response):
        for link in response.css("a::attr(href)").getall():
            yield response.follow(link, callback=self.parse)
```

启用后，Spider 会：

1. **提前获取 robots.txt**：抓取开始前，并发获取 `start_urls` 中所有域名的 robots.txt。
2. **检查每个请求**：根据域名的 robots.txt 中的 `Disallow` 规则检查请求。不允许的请求会被静默丢弃，并计入 `stats.robots_disallowed_count`。
3. **遵守 `Crawl-delay` 和 `Request-rate` 指令**：取指令要求的延迟与配置的 `download_delay` 中较大的值。robots.txt 只会在需要时增加等待时间，不会缩短已配置的等待时间。启用 AutoThrottle 后，其最大延迟也会限制这个值。请将 `autothrottle_max_delay` 设得足够大，以满足规定的等待时间。

robots.txt 文件通过 Spider 的默认会话获取，并按域名缓存到本次抓取结束。对于抓取过程中才发现、不在 `start_urls` 中的域名，会在首次请求该域名时获取其 robots.txt。

**注意：**为了避免意外行为，`robots_txt_obey` 默认关闭。启用它不会改变并发设置（`concurrent_requests`、`concurrent_requests_per_domain`），只会调整请求之间的等待时间。

如果不想手动选择 `download_delay`，可以设置 `autothrottle_enabled = True`。Spider 会根据各域名的响应速度自动调整等待时间，并在遇到封锁时降低速度。详见 [AutoThrottle](advanced.md#autothrottle)。

## 下一步 {#whats-next}

掌握基础后，可以继续阅读：

- [请求与响应](requests-responses.md)：了解请求优先级、去重、元数据等。
- [会话](sessions.md)：在同一个 Spider 中使用 HTTP、浏览器和隐身浏览器等不同类型的 Fetcher。
- [代理管理与封锁处理](proxy-blocking.md)：在请求之间轮换代理，并处理 Spider 遇到的封锁。
- [高级功能](advanced.md)：并发控制、AutoThrottle、暂停与恢复、流式输出、生命周期钩子和日志。
