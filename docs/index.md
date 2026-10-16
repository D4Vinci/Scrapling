---
title: "Scrapling: Python Web Scraping Framework"
description: "Scrapling - Effortless Web Scraping for the Modern Web!"
---

<style>
.md-typeset h1 {
  display: none;
}
[data-md-color-scheme="default"] .only-dark { display: none; }
[data-md-color-scheme="slate"] .only-light { display: none; }
</style>

<br/>
<div align="center">
    <a href="https://scrapling.readthedocs.io/en/latest/" alt="poster">
        <img alt="Scrapling" src="assets/cover_light.svg" class="only-light">
        <img alt="Scrapling" src="assets/cover_dark.svg" class="only-dark">
    </a>
</div>

<h2 align="center"><i>Effortless Web Scraping for the Modern Web</i></h2><br>

Scrapling is a Python Web Scraping framework that brings fast HTTP requests, stealth browsers, powerful parsing, and concurrent crawling into one library.

Scrape static pages, render JavaScript, interact with websites, and extract data from the API calls behind them. Build crawlers with reusable sessions, proxy rotation, automatic retries, pause/resume, and built-in data exports.

Use it from Python, the terminal, or your AI agent through its MCP server and Agent Skill. From extracting a few fields to collecting a whole website as clean Markdown, Scrapling covers the full scraping workflow.

## What you can do with Scrapling

- **[Fetch & interact](fetching/choosing.md)**: Fast HTTP requests, stealth browsers, JavaScript rendering, Cloudflare Turnstile/Interstitial handling, persistent sessions, and background API capture.
- **[Parse & extract](parsing/selection.md)**: CSS, XPath, text and regex search, adaptive element tracking, similar-element matching, and clean Markdown output.
- **[Crawl & export](spiders/getting-started.md)**: Concurrent spiders, proxy rotation, retries, AutoThrottle, pause/resume, streaming, ready-made templates, and JSON/JSONL/CSV/XML exports.
- **[Scrape with AI or from your terminal](ai/mcp-server.md)**: An MCP server for AI agents to browse and extract data, an Agent Skill, CLI commands, and an interactive shell.

Start with a single page:

```python
from scrapling.fetchers import Fetcher

page = Fetcher.get('https://quotes.toscrape.com/')
quotes = page.css('.quote .text::text').getall()
print(quotes)
```

Or scale up with a spider:

```python
from scrapling.spiders import Spider, Response

class QuotesSpider(Spider):
    name = "quotes"
    start_urls = ["https://quotes.toscrape.com/"]

    async def parse(self, response: Response):
        for quote in response.css('.quote'):
            yield {
                "text": quote.css('.text::text').get(),
                "author": quote.css('.author::text').get(),
            }

result = QuotesSpider().start()
print(len(result.items))
result.items.to_json("quotes.json")
```

This prints `10` and saves the quotes and authors to `quotes.json`.

## Top Sponsors 

--8<-- "sponsors.html"

<i><sub>Do you want to show your ad here? Click [here](https://github.com/sponsors/D4Vinci), choose a plan, and enjoy the rest of the perks!</sub></i>

## Key Features

### Spiders - A Full Crawling Framework
- 🕷️ **Scrapy-like Spider API**: Define spiders with `start_urls`, async `parse` callbacks, and `Request`/`Response` objects.
- ⚡ **Concurrent Crawling**: Configurable concurrency limits, per-domain throttling, and download delays.
- 🔄 **Multi-Session Support**: Unified interface for HTTP requests, and stealthy headless browsers in a single spider - route requests to different sessions by ID.
- 💾 **Pause & Resume**: Save pending requests and seen URLs with `crawldir`. Press Ctrl+C to stop gracefully and restart with the same directory.
- 📡 **Streaming Mode**: Stream scraped items as they arrive via `async for item in spider.stream()` with real-time stats - ideal for UI, pipelines, and long-running crawls.
- 🛡️ **Blocked Request Detection**: Automatic detection and retry of blocked requests with customizable logic.
- 🚦 **AutoThrottle**: Stop guessing delays. The spider tunes the delay of each domain on its own from how fast the website responds, then doubles it (or waits what `Retry-After` asks) whenever the website starts blocking or rate-limiting you, and speeds back up once it stops.
- 🤖 **Robots.txt Compliance**: Optional `robots_txt_obey` flag that respects `Disallow`, `Crawl-delay`, and `Request-rate` directives with per-domain caching.
- 🧪 **Development Mode**: Cache responses to disk on the first run and replay them on subsequent runs - iterate on your `parse()` logic without re-hitting the target servers.
- 🧩 **Ready-made Spider Templates**: Skip the boilerplate with `CrawlSpider` for rule-based link following, `SitemapSpider` for sitemap/robots.txt-driven crawls, `XMLFeedSpider`/`CSVFeedSpider` for iterating XML/RSS and CSV feeds, and `ShopifySpider` to collect products from public Shopify stores, one item per variant.
- 🔗 **Link Extraction**: A standalone `LinkExtractor` primitive with allow/deny patterns, domain filters, CSS/XPath scoping, extension filtering, and canonicalization - use it inside the templates or on its own.
- 📦 **Built-in Export**: Export results through hooks and your own pipeline or the built-in JSON/JSONL/CSV/XML exporters with `result.items.to_json()`, `to_jsonl()`, `to_csv()`, and `to_xml()`.

### Advanced Websites Fetching with Session Support
- **HTTP Requests**: Fast and stealthy HTTP requests with the `Fetcher` class. Can impersonate browsers' TLS fingerprint, headers, and use HTTP/3.
- **Dynamic Loading**: Fetch dynamic websites with full browser automation through the `StealthyFetcher` class supporting Playwright's Chromium and Google's Chrome.
- **Anti-bot Bypass**: Advanced stealth capabilities with `StealthyFetcher` and fingerprint spoofing. Can easily bypass all types of Cloudflare's Turnstile/Interstitial with automation.
- **Session Management**: Persistent session support with `FetcherSession` and `StealthySession` classes for cookie and state management across requests.
- **Proxy Rotation**: Built-in `ProxyRotator` with cyclic or custom rotation strategies across all session types, plus per-request proxy overrides.
- **Domain & Ad Blocking**: Block requests to specific domains (and their subdomains) or enable built-in ad blocking (~3,500 known ad/tracker domains) in browser-based fetchers.
- **DNS Leak Prevention**: Optional DNS-over-HTTPS support to route DNS queries through Cloudflare's DoH, preventing DNS leaks when using proxies.
- **Remote Browsers**: Instead of launching a browser locally, connect to one that's already running through CDP with `cdp_url`, whether it's on the same machine, another host, or a managed browser provider. You can also point any browser fetcher at your own Chromium build with `executable_path`.
- **Background API Capture**: Enable `record_requests=True` on a browser session, then search its saved responses with `session.network.search(limit=None)`. Read API data and HTTP errors across page loads without sending requests again. History is bounded and saves text response bodies.
- **Async Support**: Complete async support across all fetchers and dedicated async session classes.

### Parsing and Data Extraction
- 🔄 **Smart Element Tracking**: Relocate elements after website changes using intelligent similarity algorithms.
- 🎯 **Smart Flexible Selection**: CSS selectors, XPath selectors, filter-based search, text search, regex search, and more.
- 🔍 **Find Similar Elements**: Automatically locate elements similar to found elements.

### AI Features
- 🤖 **MCP Server**: Let AI chatbots and agents (Claude/Cursor/etc) scrape through Scrapling with HTTP requests, browser actions, screenshots, saved login state, and background API responses. Uses our stealthy browser with the right tools to enable suitable AI models to bypass any CAPTCHA it faces while working (not to mention our Cloudflare solver). It uses a lot of methods to reduce the content sent to the model, block ads, and protect it against Prompt-Injection. Remote browsers over CDP and HTTP transport with authentication options are included. ([demo video](https://www.youtube.com/watch?v=qyFk3ZNwOxE))
- 🧠 **Agent Skill**: A ready-to-install [Agent Skill](ai/agent-skill.md) that teaches coding agents the whole library, so the code they write with Scrapling matches the current API instead of guessing.
- 📚 **RAG-ready Markdown**: Turn any page into clean, sanitized, LLM-ready Markdown with one line (`page.markdown()`), or crawl a whole website into a Markdown corpus with the `ContentSpider` template, all without an LLM in the loop. ([docs](ai/building-rag-systems.md))

### High-Performance & battle-tested Architecture
- 🚀 **Lightning Fast**: Optimized performance outperforming most Python scraping libraries.
- 🔋 **Memory Efficient**: Optimized data structures and lazy loading for a minimal memory footprint.
- ⚡ **Fast JSON Serialization**: 10x faster than the standard library.
- 🏗️ **Battle tested**: Not only does Scrapling have 92% test coverage and full type hints coverage, but it has been used daily by hundreds of Web Scrapers over the past year.

### Developer/Web Scraper Friendly Experience
- 🎯 **Interactive Web Scraping Shell**: Optional built-in IPython shell with Scrapling integration, shortcuts, and new tools to speed up Web Scraping scripts development, like converting curl requests to Scrapling requests and viewing requests results in your browser.
- 🚀 **Use it directly from the Terminal**: Optionally, you can use Scrapling to scrape a URL without writing a single line of code!
- 🛠️ **Rich Navigation API**: Advanced DOM traversal with parent, sibling, and child navigation methods.
- 🧬 **Enhanced Text Processing**: Built-in regex, cleaning methods, and optimized string operations.
- 📝 **Auto Selector Generation**: Generate robust CSS/XPath selectors for any element.
- 🔌 **Familiar API**: Similar to Scrapy/BeautifulSoup with the same pseudo-elements used in Scrapy/Parsel.
- 🤝 **Drop-in Scrapy Integration**: Already invested in Scrapy? Decorate any callback with `scrapling_response` to parse the responses you already fetch with Scrapling's parser, no rewrite needed.
- 📘 **Complete Type Coverage**: Full type hints for excellent IDE support and code completion. The entire codebase is automatically scanned with **PyRight** and **MyPy** with each change.
- 🔋 **Ready Docker image**: With each release, a Docker image containing all browsers is automatically built and pushed.


## Star History
Scrapling’s GitHub stars have grown steadily since its release (see chart below).

<div id="chartContainer">
  <a href="https://github.com/D4Vinci/Scrapling">
    <img id="chartImage" alt="Star History Chart" loading="lazy" src="https://api.star-history.com/svg?repos=D4Vinci/Scrapling&type=Date" height="400"/>
  </a>
</div>

<script>
const observer = new MutationObserver((mutations) => {
  mutations.forEach((mutation) => {
    if (mutation.attributeName === 'data-md-color-media') {
      const colorMedia = document.body.getAttribute('data-md-color-media');
      const isDarkScheme = document.body.getAttribute('data-md-color-scheme') === 'slate';
      const chartImg = document.querySelector('#chartImage');
      const baseUrl = 'https://api.star-history.com/svg?repos=D4Vinci/Scrapling&type=Date';
      
      if (colorMedia === '(prefers-color-scheme)' ? isDarkScheme : colorMedia.includes('dark')) {
        chartImg.src = `${baseUrl}&theme=dark`;
      } else {
        chartImg.src = baseUrl;
      }
    }
  });
});

observer.observe(document.body, {
  attributes: true,
  attributeFilter: ['data-md-color-media', 'data-md-color-scheme']
});
</script>


## Installation
Scrapling requires Python 3.10 or higher:

```bash
pip install scrapling
```

!!! warning

    This installation only includes the parser engine and its dependencies, without any fetchers or commandline dependencies. So importing anything from `scrapling.fetchers` or `scrapling.spiders`, like in the examples above, will raise `ModuleNotFoundError` with this installation alone. If you are going to use any of the fetchers or spiders, install the fetchers' dependencies first as shown below.

### Optional Dependencies

1. If you are going to use any of the extra features below, the fetchers, or their classes, you will need to install fetchers' dependencies and their browser dependencies as follows:
    ```bash
    pip install "scrapling[fetchers]"
    
    scrapling install           # normal install
    scrapling install  --force  # force reinstall
    ```

    This downloads all browsers, along with their system dependencies and fingerprint manipulation dependencies.

    Or you can install them from the code instead of running a command like this:
    ```python
    from scrapling.cli import install
    
    install([], standalone_mode=False)          # normal install
    install(["--force"], standalone_mode=False) # force reinstall
    ```

2. Extra features:


     - Install the MCP server feature:
       ```bash
       pip install "scrapling[ai]"
       ```
     - Install dependencies for ([building RAG systems](ai/building-rag-systems.md)):
       ```bash
       pip install "scrapling[rag]"
       ```
     - Install shell features (Web Scraping shell and the `extract` command): 
         ```bash
         pip install "scrapling[shell]"
         ```
     - Install everything: 
         ```bash
         pip install "scrapling[all]"
         ```
   Run `scrapling install` when you need browser fetchers. HTTP requests do not need a browser installation.

### Docker
You can also install a Docker image with all extras and browsers with the following command from DockerHub:
```bash
docker pull pyd4vinci/scrapling
```
Or download it from the GitHub registry:
```bash
docker pull ghcr.io/d4vinci/scrapling:latest
```
This image is automatically built and pushed using GitHub Actions and the repository's main branch.

## How the documentation is organized
Scrapling has extensive documentation, so we try to follow the [Diátaxis documentation framework](https://diataxis.fr/).

## Support

If you like Scrapling and want to support its development:

- ⭐ Star the [GitHub repository](https://github.com/D4Vinci/Scrapling)
- 🚀 Follow us on [Twitter](https://x.com/Scrapling_dev) and join the [discord server](https://discord.gg/EMgGbDceNQ)
- 💝 Consider [sponsoring the project or buying me a coffee](donate.md) :wink:
- 🐛 Report bugs and suggest features through [GitHub Issues](https://github.com/D4Vinci/Scrapling/issues)

## License

This project is licensed under the BSD-3 License. See the [LICENSE](https://github.com/D4Vinci/Scrapling/blob/main/LICENSE) file for details.
