---
title: "Scrapling 网络爬虫的工作方式"
description: "了解 Spider、请求、会话、调度器和抓取引擎如何协作。对比 Scrapy 的工作流程，选择适合的入门方式。"
---

# Spider 架构 {#spiders-architecture}

!!! success "前提条件"

    1. 已阅读 [Fetcher 基础](../fetching/choosing.md)，了解不同 Fetcher 的类型和适用场景。
    2. 已阅读[主要类](../parsing/main_classes.md)，了解 [Selector](../parsing/main_classes.md#selector) 和 [Response](../fetching/choosing.md#response-object) 类。

Scrapling 的 Spider 系统是一个受 Scrapy 启发的异步抓取框架，支持并发请求、多会话以及暂停和恢复。它将 Scrapling 的解析引擎和 Fetcher 整合到统一的抓取 API 中，并提供请求调度、并发控制和检查点功能。

如果熟悉 Scrapy，你会很快上手。如果不熟悉也不用担心，这个系统的设计很直观。

## 数据流 {#data-flow}

下图展示了抓取过程中数据在 Spider 系统中的流转方式：

<img src="../assets/spider_architecture.png" title="@TrueSkills 绘制的 Spider 架构图" alt="@TrueSkills 绘制的 Spider 架构图" style="width: 70%;"/>

运行 Spider 时，主要流程如下：

1. **Spider** 生成第一批 `Request` 对象。默认会为 `start_urls` 中的每个 URL 创建一个请求，也可以重写 `start_requests()` 来定义自己的逻辑。
2. **调度器**接收请求，将其放入优先级队列，并创建请求指纹。优先级较高的请求先出队。
3. **抓取引擎**向**调度器**请求下一个待处理请求，同时遵守全局和每个域名的并发限制，以及下载延迟。如果启用了 `robots_txt_obey`，引擎会先检查该域名的 robots.txt 规则，静默丢弃不允许的请求。**抓取引擎**收到请求后，将其交给**会话管理器**。后者根据请求的 `sid`（会话 ID）选择对应会话。
4. **会话**获取页面，并向**抓取引擎**返回 [Response](../fetching/choosing.md#response-object) 对象。引擎记录统计信息，并检查响应是否被封锁。如果被封锁，会重试请求，最多 `max_blocked_retries` 次。封锁检测和重试逻辑都可以自定义。
5. **抓取引擎**将 [Response](../fetching/choosing.md#response-object) 传给请求的回调。回调可以产出一个字典，作为提取的数据项；也可以产出后续请求，由调度器加入队列。
6. 从第 2 步开始重复，直到调度器为空且没有正在运行的任务，或者 Spider 被暂停。
7. 如果启动 Spider 时设置了 `crawldir`，**抓取引擎**会定期将检查点保存到磁盘，其中包含待处理请求和已访问 URL 的集合。正常关闭时（Ctrl+C），还会保存最后一个检查点。下次使用同一个 `crawldir` 运行时，Spider 会恢复调度器状态，跳过 `start_requests()`，从上次停止的位置继续。


## 组件 {#components}

### Spider {#spider}

这是主要使用的类。创建 `Spider` 的子类，定义 `start_urls` 和 `parse()` 方法，并按需配置会话、重写生命周期钩子。

```python
from scrapling.spiders import Spider, Response, Request

class MySpider(Spider):
    name = "my_spider"
    start_urls = ["https://example.com"]

    async def parse(self, response: Response):
        for link in response.css("a::attr(href)").getall():
            yield response.follow(link, callback=self.parse_page)

    async def parse_page(self, response: Response):
        yield {"title": response.css("h1::text").get("")}
```

### 抓取引擎 {#crawler-engine}

引擎负责整个抓取流程。它管理主循环，执行并发限制，通过会话管理器发送请求，并处理回调结果。无需直接操作引擎，`Spider.start()` 和 `Spider.stream()` 会代为处理。

### 调度器 {#scheduler}

这是一个内置 URL 去重功能的优先级队列。请求指纹由 URL、HTTP 方法、请求体和会话 ID 生成。调度器通过 `snapshot()` 和 `restore()` 支持检查点系统，用于保存和恢复抓取状态。

### 会话管理器 {#session-manager}

管理一个或多个有名称的会话实例。每个会话可以是以下类型之一：

- [FetcherSession](../fetching/static.md)
- [AsyncStealthySession](../fetching/stealthy.md)

收到请求后，会话管理器会根据请求的 `sid` 字段，将请求交给对应会话。会话默认随 Spider 启动，也可以延迟到第一次使用时启动。

### 检查点系统 {#checkpoint-system}

这是一个可选系统。启用后，会将爬虫状态（待处理请求和已访问 URL 的指纹集合）保存为磁盘上的 pickle 文件。写入采用原子操作，先写入临时文件再重命名，以防文件损坏。检查点会按可配置的时间间隔保存，也会在正常关闭时保存。抓取成功完成而非暂停后，检查点文件会自动清理。

### 响应缓存 {#response-cache}

这是一个可选缓存。启用开发模式后，它会将所有获取的响应保存到磁盘，并在后续运行中重用。每个响应以请求指纹为键，保存为 JSON。响应体使用 Base64 编码，保留二进制内容。它用于反复调整 `parse()` 逻辑，避免重复请求目标服务器，不适合生产环境。

### 输出 {#output}

提取的数据项收集在 `ItemList` 中。它是 list 的子类，提供 `to_json()`、`to_jsonl()`、`to_csv()` 和 `to_xml()` 导出方法。抓取统计信息记录在 `CrawlStats` 数据类中，包含许多实用信息。


## 与 Scrapy 对比 {#comparison-with-scrapy}

如果从 Scrapy 转过来，可以参考下面的对应关系：

| 概念 | Scrapy | Scrapling |
|------|--------|-----------|
| 定义 Spider | `scrapy.Spider` 子类 | `scrapling.spiders.Spider` 子类 |
| 初始请求 | `start_requests()` | `async start_requests()` |
| 回调 | `def parse(self, response)` | `async def parse(self, response)` |
| 跟随链接 | `response.follow(url)` | `response.follow(url)` |
| 输出数据项 | `yield dict` 或 `yield Item` | `yield dict` |
| 请求调度 | 调度器 + Dupefilter | 内置去重功能的调度器 |
| 下载 | 下载器 + 中间件 | 支持多会话的会话管理器 |
| 数据项处理 | Item Pipelines | `on_scraped_item()` 钩子 |
| 封锁检测 | 自定义中间件 | 内置 `is_blocked()` + `retry_blocked_request()` 钩子 |
| 并发 | `CONCURRENT_REQUESTS` 设置 | `concurrent_requests` 类属性 |
| 域名过滤 | `allowed_domains` | `allowed_domains` |
| robots.txt | `ROBOTSTXT_OBEY` 设置 | `robots_txt_obey` 类属性 |
| 暂停与恢复 | `JOBDIR` 设置 | 构造函数参数 `crawldir` |
| 导出 | Feed 导出 | `result.items.to_json()` / `to_jsonl()` / `to_csv()` / `to_xml()`，或通过钩子自定义 |
| 运行 | `scrapy crawl spider_name` | `MySpider().start()` |
| 流式输出 | 不支持 | `async for item in spider.stream()` |
| 多会话 | 不支持 | 每个 Spider 可使用多个不同类型的会话 |
