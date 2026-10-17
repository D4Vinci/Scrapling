---
title: "抓取控制：AutoThrottle、检查点、缓存和流式输出"
description: "控制抓取速度和并发。了解响应缓存、暂停与恢复、数据项流式输出，以及检查点保存的状态。"
---

# 高级用法 {#advanced-usages}

## 简介 {#introduction}

!!! success "前提条件"

    1. 已阅读[入门](getting-started.md)，知道如何创建并运行一个简单的 Spider。

本页介绍 Spider 系统的高级功能：并发控制、暂停与恢复、流式输出、生命周期钩子、统计信息和日志。

## 并发控制 {#concurrency-control}

Spider 系统通过以下类属性控制抓取强度：

| 属性 | 默认值 | 说明 |
|------|--------|------|
| `concurrent_requests` | `4` | 同时处理的最大请求数 |
| `concurrent_requests_per_domain` | `0` | 每个域名的最大并发请求数，0 表示不单独限制域名 |
| `download_delay` | `0.0` | 每次请求前等待的秒数 |
| `robots_txt_obey` | `False` | 遵守 robots.txt 规则，包括 Disallow、Crawl-delay 和 Request-rate |

```python
class PoliteSpider(Spider):
    name = "polite"
    start_urls = ["https://example.com"]

    # Be gentle with the server
    concurrent_requests = 4
    concurrent_requests_per_domain = 2
    download_delay = 1.0  # Wait 1 second between requests

    async def parse(self, response: Response):
        yield {"title": response.css("title::text").get("")}
```

设置 `concurrent_requests_per_domain` 后，每个域名除了受全局限制，还会有自己的并发限制。同时抓取多个域名时，这样既能保持较高的总并发量，又不会给单个域名带来太大压力。

!!! tip

    `download_delay` 会在每次请求前加入固定等待时间，不考虑域名。可以用它做简单的频率限制。

## AutoThrottle {#autothrottle}

固定的 `download_delay` 只能靠估计。太小容易被封锁，太大又可能让抓取持续一整晚。AutoThrottle 会观察网站实际的响应速度，然后单独调整每个域名的延迟。服务器响应快就加速，响应慢或出现封锁就减速。

| 属性 | 默认值 | 说明 |
|------|--------|------|
| `autothrottle_enabled` | `False` | 启用自动调整延迟 |
| `autothrottle_start_delay` | `5.0` | 首次请求某个域名时使用的延迟 |
| `autothrottle_max_delay` | `60.0` | 允许的最大延迟 |
| `autothrottle_target_concurrency` | `None` | 每个域名的目标并发请求数，详见下文 |
| `autothrottle_block_backoff` | `True` | 每次被封锁时，将该域名的延迟翻倍 |

```python
class AdaptiveSpider(Spider):
    name = "adaptive"
    start_urls = ["https://example.com"]

    concurrent_requests = 8
    concurrent_requests_per_domain = 1

    autothrottle_enabled = True
    autothrottle_start_delay = 2.0
    autothrottle_max_delay = 30.0

    async def parse(self, response: Response):
        yield {"title": response.css("title::text").get("")}
```

每次响应后，延迟都会向服务器实际的响应时间靠近。例如，网站用 0.5 秒响应，延迟会稳定在 0.5 秒左右，大致相当于同一时间有一个请求正在处理。每个域名的目标并发数按以下顺序确定：已设置的 `autothrottle_target_concurrency`，否则使用 `concurrent_requests_per_domain`，再否则使用 1。通常无需额外设置目标值，因为已经配置的域名并发上限会作为目标，延迟也会除以这个值。响应时间突然升高时会立即生效，不会先取平均。因此，服务器一旦开始吃力，Spider 就会减速，而提速只会逐步进行。

### 遇到封锁时减速 {#backing-off-when-blocked}

只看响应时间无法识别频率限制。`429`、`403` 或验证码页面通常比正常内容返回得*更快*。如果只看时间，反而会认为可以加速。因此，异常响应会让该域名的延迟**翻倍**，包括非 2xx 状态码，以及被 `is_blocked()` 判定为封锁的响应：

```
0.5s -> 1s -> 2s -> 4s -> 8s ...   (up to autothrottle_max_delay)
```

只要网站继续拒绝请求，Spider 就会继续减速。当正常响应恢复后，平均计算会逐渐降低延迟，让它重新接近服务器的实际速度，无需重启。

如果网站在 `429` 或 `503` 响应中，通过 `Retry-After` 响应头明确给出等待时间，就会使用该值，而不是将延迟翻倍。支持数字形式（`Retry-After: 120`）和 HTTP 日期形式。

设置 `autothrottle_block_backoff = False` 可关闭这一行为，回到只根据响应时间调整延迟的方式。此时，封锁只能阻止 Spider 继续加速。

可以在统计信息中查看每个域名最终的延迟：

```python
result = AdaptiveSpider().start()
print(result.stats.autothrottle_delays)  # {'example.com': 0.62}
```

!!! note "注意事项"

    * `download_delay` 和 robots.txt 要求的延迟构成下限，但 `autothrottle_max_delay` 仍会限制这个下限。最大值至少应达到已配置或 robots.txt 要求的等待时间。<br/>
    * `concurrent_requests_per_domain` 在这里有两个作用：限制每个域名正在处理的请求数，并作为 AutoThrottle 的目标值。因此，通常无需单独配置目标。建议设置这个限制，因为等待中的请求也会占用全局并发名额。如果不限制单个域名，这些等待请求可能占满其他域名也需要使用的名额。<br/>
    * 测量的响应时间包括整个获取过程，也包括内部重试。对于浏览器会话，还包括页面渲染时间。<br/>
    * `autothrottle_max_delay` 限制所有延迟，包括 `Retry-After`。如果网站要求的等待时间超过上限，请提高 `autothrottle_max_delay`，以遵守该要求。<br/>
    * 自动计算出的延迟不会保存到检查点。暂停后恢复时，每个域名都从 `autothrottle_start_delay` 重新开始。

## 使用 uvloop {#using-uvloop}

`start()` 方法支持 `use_uvloop` 参数，用于在可用时使用更快的 [uvloop](https://github.com/MagicStack/uvloop)/[winloop](https://github.com/nicktimko/winloop) 事件循环实现：

```python
result = MySpider().start(use_uvloop=True)
```

这可以提升以 I/O 操作为主的抓取任务的吞吐量。需要单独安装 `uvloop`（Linux/macOS）或 `winloop`（Windows）。

## 暂停与恢复 {#pause-resume}

Spider 通过检查点支持正常暂停和恢复。向 Spider 构造函数传入 `crawldir` 目录即可启用：

```python
spider = MySpider(crawldir="crawl_data/my_spider")
result = spider.start()

if result.paused:
    print("Crawl was paused. Run again to resume.")
else:
    print("Crawl completed!")
```

### 工作方式 {#how-it-works}

1. **暂停**：抓取时按 `Ctrl+C`。Spider 会等待所有运行中的请求完成，保存检查点（待处理请求和已访问请求的指纹集合），然后退出。
2. **强制停止**：再次按 `Ctrl+C`，不等待正在运行的任务，立即停止。
3. **恢复**：使用同一个 `crawldir` 再次运行 Spider。它会发现检查点，恢复队列和已访问指纹集合，跳过 `start_requests()`，从上次停止的位置继续。
4. **清理**：抓取正常完成而非暂停后，检查点文件会自动删除。

**抓取过程中也会定期保存检查点，默认每 5 分钟一次。**

可以这样修改保存间隔：

```python
# Save checkpoint every 2 minutes
spider = MySpider(crawldir="crawl_data/my_spider", interval=120.0)
```

检查点先写入临时文件，仅在写入成功后才替换之前的检查点。

!!! warning "检查点数据"

    启用 `crawldir` 时，待处理请求中的值（包括 `meta` 和请求参数）必须能用 Python 的 `pickle` 模块保存。如果某个值无法保存，检查点保存就会失败，抓取也会停止。`Selector` 可以在回调中使用，但不能以这种方式保存。

    保存提取出的字符串或数字等值，而不是 `Selector` 对象。列表和字典也必须只包含可保存的值：

    ```python
    yield response.follow("/details", meta={"title": str(response.css("h1::text").get(""))})
    ```

!!! tip

    使用 `start()` 时，即使没有启用检查点系统，抓取中按 `Ctrl+C` 也会让 Spider 正常关闭。若还没关闭就再次按下，会强制立即关闭。

### 判断是否正在恢复 {#knowing-if-youre-resuming}

`on_start()` 钩子会接收 `resuming` 标志：

```python
async def on_start(self, resuming: bool = False):
    if resuming:
        self.logger.info("Resuming from checkpoint!")
    else:
        self.logger.info("Starting fresh crawl")
```

## 开发模式 {#development-mode}

反复调整 Spider 的 `parse()` 逻辑时，每次都请求目标服务器既慢，又会产生不必要的请求。开发模式会在第一次运行时将所有响应缓存到磁盘，后续运行直接读取缓存。因此，可以修改选择器并反复运行 Spider，而无需再次获取这些页面。

在 Spider 中设置 `development_mode = True` 即可启用：

```python
class MySpider(Spider):
    name = "my_spider"
    start_urls = ["https://example.com"]
    development_mode = True

    async def parse(self, response: Response):
        yield {"title": response.css("title::text").get("")}
```

第一次运行会正常获取页面，并将每个响应存到磁盘。后续运行中，相同请求会直接使用缓存，跳过页面获取。如果设置了 `robots_txt_obey=True`，会先检查 robots.txt 规则，再查询缓存。

### 缓存位置 {#cache-location}

默认缓存目录是相对于当前工作目录的 `.scrapling_cache/{spider.name}/`。当前工作目录是运行 Spider 命令的位置，**不是** Spider 脚本所在的位置。可以用 `development_cache_dir` 指定其他目录：

```python
class MySpider(Spider):
    name = "my_spider"
    start_urls = ["https://example.com"]
    development_mode = True
    development_cache_dir = "/tmp/my_spider_cache"
```

### 工作方式 {#how-it-works_1}

1. **缓存键**：每个响应以请求指纹为键。修改影响指纹的属性（`fp_include_kwargs`、`fp_include_headers`、`fp_keep_fragments`）后，会重新获取页面。
2. **存储格式**：每个响应一个 JSON 文件，名称为 `{fingerprint_hex}.json`。响应体使用 Base64 编码，确保二进制内容完整保留。写入采用原子操作，先写临时文件再重命名。
3. **重用缓存**：命中缓存时，引擎会跳过页面获取，包括 `download_delay`、频率限制以及 `is_blocked()` 重试流程。缓存响应会直接交给回调。
4. **统计信息**：缓存请求仍会计入 `requests_count`、`response_bytes` 和各状态码的计数，因此统计输出与正常抓取一致。额外的 `cache_hits` 和 `cache_misses` 计数器可以显示缓存的使用情况。

### 清空缓存 {#clearing-the-cache}

缓存不会自动过期。如需强制重新抓取，请删除缓存目录，或直接调用管理器的 `clear()` 方法。

!!! warning

    开发模式用于开发，不适合生产环境。缓存响应永不过期，读取缓存会跳过频率限制和封锁重试。不要将带有 `development_mode = True` 的 Spider 用于生产环境。

## 流式输出 {#streaming}

对于长时间运行的 Spider，或需要实时获取数据项的应用，请使用 `stream()`，而不是 `start()`：

```python
import anyio

async def main():
    spider = MySpider()
    async for item in spider.stream():
        print(f"Got item: {item}")
        # Access real-time stats
        print(f"Items so far: {spider.stats.items_scraped}")
        print(f"Requests made: {spider.stats.requests_count}")

anyio.run(main)
```

与 `start()` 的主要区别：

- `stream()` 必须在异步上下文中调用。
- 数据项会在提取后逐个产出，而不是收集到列表中。
- 遍历过程中，可以通过 `spider.stats` 查看实时统计信息。

!!! abstract

    `spider.stats` 支持的完整统计信息列表见[下文](#results-statistics)。

流式输出也可以与检查点系统一起使用。这样便于在 Spider 之上构建界面，显示实时数据，并支持暂停和恢复。

```python
import anyio

async def main():
    spider = MySpider(crawldir="crawl_data/my_spider")
    async for item in spider.stream():
        print(f"Got item: {item}")
        # Access real-time stats
        print(f"Items so far: {spider.stats.items_scraped}")
        print(f"Requests made: {spider.stats.requests_count}")

anyio.run(main)
```
在上例中，也可以使用 `spider.pause()` 从代码中停止 Spider。如果没有启用检查点系统，它只会结束抓取。

## 生命周期钩子 {#lifecycle-hooks}

Spider 提供了多个可重写的钩子，用于在抓取的不同阶段添加自定义行为：

### on_start {#on_start}

抓取开始前调用。可用于加载数据、初始化资源等准备工作：

```python
async def on_start(self, resuming: bool = False):
    self.logger.info("Spider starting up")
    # Load seed URLs from a database, initialize counters, etc.
```

### on_close {#on_close}

抓取结束后调用，无论是完成还是暂停。可用于清理资源：

```python
async def on_close(self):
    self.logger.info("Spider shutting down")
    # Close database connections, flush buffers, etc.
```

### on_error {#on_error}

请求因异常失败时调用。可用于记录错误或自定义恢复逻辑：

```python
async def on_error(self, request: Request, error: Exception):
    self.logger.error(f"Failed: {request.url} - {error}")
    # Log to error tracker, save failed URL for later, etc.
```

### on_scraped_item {#on_scraped_item}

每个数据项加入结果前都会调用。返回原数据项或修改后的数据项即可保留它；返回 `None` 则丢弃：

```python
async def on_scraped_item(self, item: dict) -> dict | None:
    # Drop items without a title
    if not item.get("title"):
        return None

    # Modify items (e.g., add timestamps)
    item["scraped_at"] = "2026-01-01"
    return item
```

!!! tip

    也可以通过此钩子将数据项交给自己的处理流水线，并从 Spider 的结果中移除。

### start_requests {#start_requests}

重写 `start_requests()`，可以自行生成初始请求，不再使用 `start_urls`：

```python
async def start_requests(self):
    # POST request to log in first
    yield Request(
        "https://example.com/login",
        method="POST",
        data={"user": "admin", "pass": "secret"},
        callback=self.after_login,
    )

async def after_login(self, response: Response):
    # Now crawl the authenticated pages
    yield response.follow("/dashboard", callback=self.parse)
```

## 结果与统计信息 {#results-statistics}

`start()` 返回的 `CrawlResult` 同时包含提取的数据项和详细统计信息：

```python
result = MySpider().start()

# Items
print(f"Total items: {len(result.items)}")
result.items.to_json("output.json", indent=True)

# Did the crawl complete?
print(f"Completed: {result.completed}")
print(f"Paused: {result.paused}")

# Statistics
stats = result.stats
print(f"Requests: {stats.requests_count}")
print(f"Failed: {stats.failed_requests_count}")
print(f"Blocked: {stats.blocked_requests_count}")
print(f"Offsite filtered: {stats.offsite_requests_count}")
print(f"Robots.txt disallowed: {stats.robots_disallowed_count}")
print(f"Cache hits: {stats.cache_hits}")
print(f"Cache misses: {stats.cache_misses}")
print(f"Items scraped: {stats.items_scraped}")
print(f"Items dropped: {stats.items_dropped}")
print(f"Response bytes: {stats.response_bytes}")
print(f"Duration: {stats.elapsed_seconds:.1f}s")
print(f"Speed: {stats.requests_per_second:.1f} req/s")
```

### 详细统计信息 {#detailed-stats}

`CrawlStats` 对象记录详细信息：

```python
stats = result.stats

# Status code distribution
print(stats.response_status_count)
# {'status_200': 150, 'status_404': 3, 'status_403': 1}

# Bytes downloaded per domain
print(stats.domains_response_bytes)
# {'example.com': 1234567, 'api.example.com': 45678}

# Requests per session
print(stats.sessions_requests_count)
# {'http': 120, 'stealth': 34}

# Proxies used during the crawl
print(stats.proxies)
# ['http://proxy1:8080', 'http://proxy2:8080']

# Log level counts
print(stats.log_levels_counter)
# {'debug': 200, 'info': 50, 'warning': 3, 'error': 1, 'critical': 0}

# Timing information
print(stats.start_time)       # Unix timestamp when crawl started
print(stats.end_time)         # Unix timestamp when crawl finished
print(stats.download_delay)   # The download delay used (seconds)

# Concurrency settings used
print(stats.concurrent_requests)             # Global concurrency limit
print(stats.concurrent_requests_per_domain)  # Per-domain concurrency limit

# AutoThrottle
print(stats.autothrottle_enabled)  # Whether the adaptive delay was on
print(stats.autothrottle_delays)   # Final delay per domain, {'example.com': 0.62}

# Custom stats (set by your spider code)
print(stats.custom_stats)
# {'login_attempts': 3, 'pages_with_errors': 5}

# Export everything as a dict
print(stats.to_dict())
```

## 日志 {#logging}

Spider 内置日志记录器，可通过 `self.logger` 使用。它已配置好 Spider 名称，并支持以下选项：

| 属性 | 默认值 | 说明 |
|------|--------|------|
| `logging_level` | `logging.DEBUG` | 最低日志级别 |
| `logging_format` | `"[%(asctime)s]:({spider_name}) %(levelname)s: %(message)s"` | 日志消息格式 |
| `logging_date_format` | `"%Y-%m-%d %H:%M:%S"` | 日志中的日期格式 |
| `log_file` | `None` | 日志文件路径，除控制台输出外也写入文件 |

```python
import logging

class MySpider(Spider):
    name = "my_spider"
    start_urls = ["https://example.com"]
    logging_level = logging.INFO
    log_file = "logs/my_spider.log"

    async def parse(self, response: Response):
        self.logger.info(f"Processing {response.url}")
        yield {"title": response.css("title::text").get("")}
```

如果日志文件的目录不存在，会自动创建。控制台和文件输出使用相同格式。
