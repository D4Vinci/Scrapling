# Advanced usages

## Introduction

!!! success "Prerequisites"

    1. You've read the [Getting started](getting-started.md) page and know how to create and run a basic spider.

This page covers the spider system's advanced features: concurrency control, pause/resume, streaming, lifecycle hooks, statistics, and logging.

## Concurrency Control

The spider system uses three class attributes to control how aggressively it crawls:

| Attribute                        | Default | Description                                                      |
|----------------------------------|---------|------------------------------------------------------------------|
| `concurrent_requests`            | `4`     | Maximum number of requests being processed at the same time      |
| `concurrent_requests_per_domain` | `0`     | Maximum concurrent requests per domain (0 = no per-domain limit) |
| `download_delay`                 | `0.0`   | Seconds to wait before each request                              |

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

When `concurrent_requests_per_domain` is set, each domain gets its own concurrency limiter in addition to the global limit. This is useful when crawling multiple domains simultaneously — you can allow high global concurrency while being polite to each individual domain.

!!! tip

    The `download_delay` parameter adds a fixed wait before every request, regardless of the domain. Use it for simple rate limiting.

### Using uvloop

The `start()` method accepts a `use_uvloop` parameter to use the faster [uvloop](https://github.com/MagicStack/uvloop)/[winloop](https://github.com/nicktimko/winloop) event loop implementation, if available:

```python
result = MySpider().start(use_uvloop=True)
```

This can improve throughput for I/O-heavy crawls. You'll need to install `uvloop` (Linux/macOS) or `winloop` (Windows) separately.

## Pause & Resume

The spider supports graceful pause-and-resume via checkpointing. To enable it, pass a `crawldir` directory to the spider constructor:

```python
spider = MySpider(crawldir="crawl_data/my_spider")
result = spider.start()

if result.paused:
    print("Crawl was paused. Run again to resume.")
else:
    print("Crawl completed!")
```

### How It Works

1. **Pausing**: Press `Ctrl+C` during a crawl. The spider waits for all in-flight requests to finish, saves a checkpoint (pending requests + a set of seen request fingerprints), and then exits.
2. **Force stopping**: Press `Ctrl+C` a second time to stop immediately without waiting for active tasks.
3. **Resuming**: Run the spider again with the same `crawldir`. It detects the checkpoint, restores the queue and seen set, and continues from where it left off — skipping `start_requests()`.
4. **Cleanup**: When a crawl completes normally (not paused), the checkpoint files are deleted automatically.

**Checkpoints are also saved periodically during the crawl (every 5 minutes by default).** 

You can change the interval as follows:

```python
# Save checkpoint every 2 minutes
spider = MySpider(crawldir="crawl_data/my_spider", interval=120.0)
```

The writing to the disk is atomic, so it's totally safe.

!!! tip

    Pressing `Ctrl+C` during a crawl always causes the spider to close gracefully, even if the checkpoint system is not enabled. Doing it again without waiting forces the spider to close immediately.

### Knowing If You're Resuming

The `on_start()` hook receives a `resuming` flag:

```python
async def on_start(self, resuming: bool = False):
    if resuming:
        self.logger.info("Resuming from checkpoint!")
    else:
        self.logger.info("Starting fresh crawl")
```

## Streaming

For long-running spiders or applications that need real-time access to scraped items, use the `stream()` method instead of `start()`:

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

Key differences from `start()`:

- `stream()` must be called from an async context
- Items are yielded one by one as they're scraped, not collected into a list
- You can access `spider.stats` during iteration for real-time statistics

!!! abstract 

    The full list of all stats that can be accessed by `spider.stats` is explained below [here](#results--statistics)

You can use it with the checkpoint system too, so it's easy to build UI on top of spiders. UIs that have real-time data and can be paused/resumed.

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
You can also use `spider.pause()` to shut down the spider in the code above. If you used it without enabling the checkpoint system, it will just close the crawl.

## Lifecycle Hooks

The spider provides several hooks you can override to add custom behavior at different stages of the crawl:

### on_start

Called before crawling begins. Use it for setup tasks like loading data or initializing resources:

```python
async def on_start(self, resuming: bool = False):
    self.logger.info("Spider starting up")
    # Load seed URLs from a database, initialize counters, etc.
```

### on_close

Called after crawling finishes (whether completed or paused). Use it for cleanup:

```python
async def on_close(self):
    self.logger.info("Spider shutting down")
    # Close database connections, flush buffers, etc.
```

### on_error

Called when a request fails with an exception. Use it for error tracking or custom recovery logic:

```python
async def on_error(self, request: Request, error: Exception):
    self.logger.error(f"Failed: {request.url} - {error}")
    # Log to error tracker, save failed URL for later, etc.
```

### on_scraped_item

Called for every scraped item before it's added to the results. Return the item (modified or not) to keep it, or return `None` to drop it:

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

    This hook can also be used to direct items through your own pipelines and drop them from the spider.

### start_requests

Override `start_requests()` for custom initial request generation instead of using `start_urls`:

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

## Results & Statistics

The `CrawlResult` returned by `start()` contains both the scraped items and detailed statistics:

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
print(f"Items scraped: {stats.items_scraped}")
print(f"Items dropped: {stats.items_dropped}")
print(f"Response bytes: {stats.response_bytes}")
print(f"Duration: {stats.elapsed_seconds:.1f}s")
print(f"Speed: {stats.requests_per_second:.1f} req/s")
```

### Detailed Stats

The `CrawlStats` object tracks granular information:

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

# Custom stats (set by your spider code)
print(stats.custom_stats)
# {'login_attempts': 3, 'pages_with_errors': 5}

# Export everything as a dict
print(stats.to_dict())
```

## Logging

The spider has a built-in logger accessible via `self.logger`. It's pre-configured with the spider's name and supports several customization options:

| Attribute             | Default                                                      | Description                                        |
|-----------------------|--------------------------------------------------------------|----------------------------------------------------|
| `logging_level`       | `logging.DEBUG`                                              | Minimum log level                                  |
| `logging_format`      | `"[%(asctime)s]:({spider_name}) %(levelname)s: %(message)s"` | Log message format                                 |
| `logging_date_format` | `"%Y-%m-%d %H:%M:%S"`                                        | Date format in log messages                        |
| `log_file`            | `None`                                                       | Path to a log file (in addition to console output) |

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

The log file directory is created automatically if it doesn't exist. Both console and file output use the same format.