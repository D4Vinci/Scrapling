<h1 align="center">
    <a href="https://scrapling.readthedocs.io">
        <picture>
          <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/D4Vinci/Scrapling/v4/docs/assets/cover_dark.svg?sanitize=true">
          <img alt="Scrapling Poster" src="https://raw.githubusercontent.com/D4Vinci/Scrapling/v4/docs/assets/cover_light.svg?sanitize=true">
        </picture>
    </a>
    <br>
    <small>Web Scraping have never been easier!</small>
</h1>

<p align="center">
    <a href="https://github.com/D4Vinci/Scrapling/blob/v4//README_AR.md">العربيه</a> | <a href="https://github.com/D4Vinci/Scrapling/blob/v4//README_ES.md">Español</a> | <a href="https://github.com/D4Vinci/Scrapling/blob/v4//README_DE.md">Deutsch</a> | <a href="https://github.com/D4Vinci/Scrapling/blob/v4//README_CN.md">简体中文</a> | <a href="https://github.com/D4Vinci/Scrapling/blob/v4//README_JP.md">日本語</a> |  <a href="https://github.com/D4Vinci/Scrapling/blob/v4//README_RU.md">Русский</a>
    <br/>
    <a href="https://github.com/D4Vinci/Scrapling/actions/workflows/tests.yml" alt="Tests">
        <img alt="Tests" src="https://github.com/D4Vinci/Scrapling/actions/workflows/tests.yml/badge.svg"></a>
    <a href="https://badge.fury.io/py/Scrapling" alt="PyPI version">
        <img alt="PyPI version" src="https://badge.fury.io/py/Scrapling.svg"></a>
    <a href="https://pepy.tech/project/scrapling" alt="PyPI Downloads">
        <img alt="PyPI Downloads" src="https://static.pepy.tech/personalized-badge/scrapling?period=total&units=INTERNATIONAL_SYSTEM&left_color=GREY&right_color=GREEN&left_text=Downloads"></a>
    <br/>
    <a href="https://discord.gg/EMgGbDceNQ" alt="Discord" target="_blank">
      <img alt="Discord" src="https://img.shields.io/discord/1360786381042880532?style=social&logo=discord&link=https%3A%2F%2Fdiscord.gg%2FEMgGbDceNQ">
    </a>
    <a href="https://x.com/Scrapling_dev" alt="X (formerly Twitter)">
      <img alt="X (formerly Twitter) Follow" src="https://img.shields.io/twitter/follow/Scrapling_dev?style=social&logo=x&link=https%3A%2F%2Fx.com%2FScrapling_dev">
    </a>
    <br/>
    <a href="https://pypi.org/project/scrapling/" alt="Supported Python versions">
        <img alt="Supported Python versions" src="https://img.shields.io/pypi/pyversions/scrapling.svg"></a>
</p>

<p align="center">
    <a href="https://scrapling.readthedocs.io/en/latest/parsing/selection/">
        Selection methods
    </a>
    ·
    <a href="https://scrapling.readthedocs.io/en/latest/fetching/choosing/">
        Choosing a fetcher
    </a>
    ·
    <a href="https://scrapling.readthedocs.io/en/latest/cli/overview/">
        CLI
    </a>
    ·
    <a href="https://scrapling.readthedocs.io/en/latest/ai/mcp-server/">
        MCP mode
    </a>
    ·
    <a href="https://scrapling.readthedocs.io/en/latest/tutorials/migrating_from_beautifulsoup/">
        Migrating from Beautifulsoup
    </a>
</p>

**Stop fighting anti-bot systems. Stop rewriting selectors after every website update.**

Scrapling isn't just another Web Scraping library. It's the first **adaptive** scraping library that learns from website changes and evolves with them. While other libraries break when websites update their structure, Scrapling automatically relocates your elements and keeps your scrapers running.

Built for the modern Web, Scrapling features **its own rapid parsing engine** and fetchers to handle all Web Scraping challenges you face or will face. Built by Web Scrapers for Web Scrapers and regular users, there's something for everyone.

```python
>> from scrapling.fetchers import Fetcher, AsyncFetcher, StealthyFetcher, DynamicFetcher
>> StealthyFetcher.adaptive = True
# Fetch websites' source under the radar!
>> page = StealthyFetcher.fetch('https://example.com', headless=True, network_idle=True)
>> print(page.status)
200
>> products = page.css('.product', auto_save=True)  # Scrape data that survives website design changes!
>> # Later, if the website structure changes, pass `adaptive=True`
>> products = page.css('.product', adaptive=True)  # and Scrapling still finds them!
```

# Sponsors 

<!-- sponsors -->

<a href="https://www.scrapeless.com/en?utm_source=official&utm_term=scrapling" target="_blank" title="Effortless Web Scraping Toolkit for Business and Developers"><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/scrapeless.jpg"></a>
<a href="https://www.thordata.com/?ls=github&lk=github" target="_blank" title="Unblockable proxies and scraping infrastructure, delivering real-time, reliable web data to power AI models and workflows."><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/thordata.jpg"></a>
<a href="https://evomi.com?utm_source=github&utm_medium=banner&utm_campaign=d4vinci-scrapling" target="_blank" title="Evomi is your Swiss Quality Proxy Provider, starting at $0.49/GB"><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/evomi.png"></a>
<a href="https://serpapi.com/?utm_source=scrapling" target="_blank" title="Scrape Google and other search engines with SerpApi"><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/SerpApi.png"></a>
<a href="https://visit.decodo.com/Dy6W0b" target="_blank" title="Try the Most Efficient Residential Proxies for Free"><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/decodo.png"></a>
<a href="https://petrosky.io/d4vinci" target="_blank" title="PetroSky delivers cutting-edge VPS hosting."><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/petrosky.png"></a>
<a href="https://hasdata.com/?utm_source=github&utm_medium=banner&utm_campaign=D4Vinci" target="_blank" title="The web scraping service that actually beats anti-bot systems!"><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/hasdata.png"></a>
<a href="https://hypersolutions.co/?utm_source=github&utm_medium=readme&utm_campaign=scrapling" target="_blank" title="Bot Protection Bypass API for Akamai, DataDome, Incapsula & Kasada"><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/HyperSolutions.png"></a>
<a href="https://www.swiftproxy.net/" target="_blank" title="Unlock Reliable Proxy Services with Swiftproxy!"><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/swiftproxy.png"></a>
<a href="https://www.rapidproxy.io/?ref=d4v" target="_blank" title="Affordable Access to the Proxy World – bypass CAPTCHAs blocks, and avoid additional costs."><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/rapidproxy.jpg"></a>
<a href="https://browser.cash/?utm_source=D4Vinci&utm_medium=referral" target="_blank" title="Browser Automation & AI Browser Agent Platform"><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/browserCash.png"></a>

<!-- /sponsors -->

<i><sub>Do you want to show your ad here? Click [here](https://github.com/sponsors/D4Vinci) and choose the tier that suites you!</sub></i>

---

## Key Features

### Advanced Websites Fetching with Session Support
- **HTTP Requests**: Fast and stealthy HTTP requests with the `Fetcher` class. Can impersonate browsers' TLS fingerprint, headers, and use HTTP3.
- **Dynamic Loading**: Fetch dynamic websites with full browser automation through the `DynamicFetcher` class supporting Playwright's Chromium and Google's Chrome.
- **Anti-bot Bypass**: Advanced stealth capabilities with `StealthyFetcher` and fingerprint spoofing. Can easily bypass all types of Cloudflare's Turnstile/Interstitial with automation.
- **Session Management**: Persistent session support with `FetcherSession`, `StealthySession`, and `DynamicSession` classes for cookie and state management across requests.
- **Async Support**: Complete async support across all fetchers and dedicated async session classes.

### Adaptive Scraping & AI Integration
- 🔄 **Smart Element Tracking**: Relocate elements after website changes using intelligent similarity algorithms.
- 🎯 **Smart Flexible Selection**: CSS selectors, XPath selectors, filter-based search, text search, regex search, and more. 
- 🔍 **Find Similar Elements**: Automatically locate elements similar to found elements.
- 🤖 **MCP Server to be used with AI**: Built-in MCP server for AI-assisted Web Scraping and data extraction. The MCP server features powerful, custom capabilities that leverage Scrapling to extract targeted content before passing it to the AI (Claude/Cursor/etc), thereby speeding up operations and reducing costs by minimizing token usage. ([demo video](https://www.youtube.com/watch?v=qyFk3ZNwOxE))

### High-Performance & battle-tested Architecture
- 🚀 **Lightning Fast**: Optimized performance outperforming most Python scraping libraries.
- 🔋 **Memory Efficient**: Optimized data structures and lazy loading for a minimal memory footprint.
- ⚡ **Fast JSON Serialization**: 10x faster than the standard library.
- 🏗️ **Battle tested**: Not only does Scrapling have 92% test coverage and full type hints coverage, but it has been used daily by hundreds of Web Scrapers over the past year.

### Developer/Web Scraper Friendly Experience
- 🎯 **Interactive Web Scraping Shell**: Optional built-in IPython shell with Scrapling integration, shortcuts, and new tools to speed up Web Scraping scripts development, like converting curl requests to Scrapling requests and viewing requests results in your browser.
- 🚀 **Use it directly from the Terminal**: Optionally, you can use Scrapling to scrape a URL without writing a single code!
- 🛠️ **Rich Navigation API**: Advanced DOM traversal with parent, sibling, and child navigation methods.
- 🧬 **Enhanced Text Processing**: Built-in regex, cleaning methods, and optimized string operations.
- 📝 **Auto Selector Generation**: Generate robust CSS/XPath selectors for any element.
- 🔌 **Familiar API**: Similar to Scrapy/BeautifulSoup with the same pseudo-elements used in Scrapy/Parsel.
- 📘 **Complete Type Coverage**: Full type hints for excellent IDE support and code completion.
- 🔋 **Ready Docker image**: With each release, a Docker image containing all browsers is automatically built and pushed.

## Getting Started

### Basic Usage
```python
from scrapling.fetchers import Fetcher, StealthyFetcher, DynamicFetcher
from scrapling.fetchers import FetcherSession, StealthySession, DynamicSession

# HTTP requests with session support
with FetcherSession(impersonate='chrome') as session:  # Use latest version of Chrome's TLS fingerprint
    page = session.get('https://quotes.toscrape.com/', stealthy_headers=True)
    quotes = page.css('.quote .text::text')

# Or use one-off requests
page = Fetcher.get('https://quotes.toscrape.com/')
quotes = page.css('.quote .text::text')

# Advanced stealth mode (Keep the browser open until you finish)
with StealthySession(headless=True, solve_cloudflare=True) as session:
    page = session.fetch('https://nopecha.com/demo/cloudflare', google_search=False)
    data = page.css('#padded_content a')

# Or use one-off request style, it opens the browser for this request, then closes it after finishing
page = StealthyFetcher.fetch('https://nopecha.com/demo/cloudflare')
data = page.css('#padded_content a')
    
# Full browser automation (Keep the browser open until you finish)
with DynamicSession(headless=True, disable_resources=False, network_idle=True) as session:
    page = session.fetch('https://quotes.toscrape.com/', load_dom=False)
    data = page.xpath('//span[@class="text"]/text()')  # XPath selector if you prefer it

# Or use one-off request style, it opens the browser for this request, then closes it after finishing
page = DynamicFetcher.fetch('https://quotes.toscrape.com/')
data = page.css('.quote .text::text')
```

> [!NOTE]
> There's a wonderful guide to get you started quickly with Scrapling [here](https://substack.thewebscraping.club/p/scrapling-hands-on-guide) written by The Web Scraping Club. In case you find it easier to get you started than the [documentation website](https://scrapling.readthedocs.io/en/latest/).

### Advanced Parsing & Navigation
```python
from scrapling.fetchers import Fetcher

# Rich element selection and navigation
page = Fetcher.get('https://quotes.toscrape.com/')

# Get quotes with multiple selection methods
quotes = page.css('.quote')  # CSS selector
quotes = page.xpath('//div[@class="quote"]')  # XPath
quotes = page.find_all('div', {'class': 'quote'})  # BeautifulSoup-style
# Same as
quotes = page.find_all('div', class_='quote')
quotes = page.find_all(['div'], class_='quote')
quotes = page.find_all(class_='quote')  # and so on...
# Find element by text content
quotes = page.find_by_text('quote', tag='div')

# Advanced navigation
first_quote = page.css_first('.quote')
quote_text = first_quote.css('.text::text')
quote_text = page.css('.quote').css_first('.text::text')  # Chained selectors
quote_text = page.css_first('.quote .text').text  # Using `css_first` is faster than `css` if you want the first element
author = first_quote.next_sibling.css('.author::text')
parent_container = first_quote.parent

# Element relationships and similarity
similar_elements = first_quote.find_similar()
below_elements = first_quote.below_elements()
```
You can use the parser right away if you don't want to fetch websites like below:
```python
from scrapling.parser import Selector

page = Selector("<html>...</html>")
```
And it works precisely the same way!

### Async Session Management Examples
```python
import asyncio
from scrapling.fetchers import FetcherSession, AsyncStealthySession, AsyncDynamicSession

async with FetcherSession(http3=True) as session:  # `FetcherSession` is context-aware and can work in both sync/async patterns
    page1 = session.get('https://quotes.toscrape.com/')
    page2 = session.get('https://quotes.toscrape.com/', impersonate='firefox135')

# Async session usage
async with AsyncStealthySession(max_pages=2) as session:
    tasks = []
    urls = ['https://example.com/page1', 'https://example.com/page2']
    
    for url in urls:
        task = session.fetch(url)
        tasks.append(task)
    
    print(session.get_pool_stats())  # Optional - The status of the browser tabs pool (busy/free/error)
    results = await asyncio.gather(*tasks)
    print(session.get_pool_stats())
```

## CLI & Interactive Shell

Scrapling v0.3 includes a powerful command-line interface:

[![asciicast](https://asciinema.org/a/736339.svg)](https://asciinema.org/a/736339)

Launch the interactive Web Scraping shell
```bash
scrapling shell
```
Extract pages to a file directly without programming (Extracts the content inside the `body` tag by default). If the output file ends with `.txt`, then the text content of the target will be extracted. If it ends in `.md`, it will be a Markdown representation of the HTML content; if it ends in `.html`, it will be the HTML content itself.
```bash
scrapling extract get 'https://example.com' content.md
scrapling extract get 'https://example.com' content.txt --css-selector '#fromSkipToProducts' --impersonate 'chrome'  # All elements matching the CSS selector '#fromSkipToProducts'
scrapling extract fetch 'https://example.com' content.md --css-selector '#fromSkipToProducts' --no-headless
scrapling extract stealthy-fetch 'https://nopecha.com/demo/cloudflare' captchas.html --css-selector '#padded_content a' --solve-cloudflare
```

> [!NOTE]
> There are many additional features, but we want to keep this page concise, such as the MCP server and the interactive Web Scraping Shell. Check out the full documentation [here](https://scrapling.readthedocs.io/en/latest/)

## Performance Benchmarks

Scrapling isn't just powerful—it's also blazing fast, and the updates since version 0.3 have delivered exceptional performance improvements across all operations. The following benchmarks compare Scrapling's parser with other popular libraries.

### Text Extraction Speed Test (5000 nested elements)

| # |      Library      | Time (ms) | vs Scrapling | 
|---|:-----------------:|:---------:|:------------:|
| 1 |     Scrapling     |   1.99    |     1.0x     |
| 2 |   Parsel/Scrapy   |   2.01    |    1.01x     |
| 3 |     Raw Lxml      |    2.5    |    1.256x    |
| 4 |      PyQuery      |   22.93   |    ~11.5x    |
| 5 |    Selectolax     |   80.57   |    ~40.5x    |
| 6 |   BS4 with Lxml   |  1541.37  |   ~774.6x    |
| 7 |  MechanicalSoup   |  1547.35  |   ~777.6x    |
| 8 | BS4 with html5lib |  3410.58  |   ~1713.9x   |


### Element Similarity & Text Search Performance

Scrapling's adaptive element finding capabilities significantly outperform alternatives:

|   Library   | Time (ms) | vs Scrapling |
|-------------|:---------:|:------------:|
| Scrapling   |   2.46    |     1.0x     |
| AutoScraper |   13.3    |    5.407x    |


> All benchmarks represent averages of 100+ runs. See [benchmarks.py](https://github.com/D4Vinci/Scrapling/blob/main/benchmarks.py) for methodology.

## Installation

Scrapling requires Python 3.10 or higher:

```bash
pip install scrapling
```

Starting with v0.3.2, this installation only includes the parser engine and its dependencies, without any fetchers or commandline dependencies.

### Optional Dependencies

1. If you are going to use any of the extra features below, the fetchers, or their classes, you will need to install fetchers' dependencies and their browser dependencies as follows:
    ```bash
    pip install "scrapling[fetchers]"
    
    scrapling install
    ```

    This downloads all browsers, along with their system dependencies and fingerprint manipulation dependencies.

2. Extra features:
   - Install the MCP server feature:
       ```bash
       pip install "scrapling[ai]"
       ```
   - Install shell features (Web Scraping shell and the `extract` command): 
       ```bash
       pip install "scrapling[shell]"
       ```
   - Install everything: 
       ```bash
       pip install "scrapling[all]"
       ```
   Remember that you need to install the browser dependencies with `scrapling install` after any of these extras (if you didn't already)

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

## Contributing

We welcome contributions! Please read our [contributing guidelines](https://github.com/D4Vinci/Scrapling/blob/main/CONTRIBUTING.md) before getting started.

## Disclaimer

> [!CAUTION]
> This library is provided for educational and research purposes only. By using this library, you agree to comply with local and international data scraping and privacy laws. The authors and contributors are not responsible for any misuse of this software. Always respect the terms of service of websites and robots.txt files.

## License

This work is licensed under the BSD-3-Clause License.

## Acknowledgments

This project includes code adapted from:
- Parsel (BSD License)—Used for [translator](https://github.com/D4Vinci/Scrapling/blob/main/scrapling/core/translator.py) submodule

## Thanks and References

- [Daijro](https://github.com/daijro)'s brilliant work on [BrowserForge](https://github.com/daijro/browserforge) and [Camoufox](https://github.com/daijro/camoufox)
- [Vinyzu](https://github.com/Vinyzu)'s brilliant work on [Botright](https://github.com/Vinyzu/Botright) and [PatchRight](https://github.com/Kaliiiiiiiiii-Vinyzu/patchright)
- [brotector](https://github.com/kaliiiiiiiiii/brotector) for browser detection bypass techniques
- [fakebrowser](https://github.com/kkoooqq/fakebrowser) and [BotBrowser](https://github.com/botswin/BotBrowser) for fingerprinting research

---
<div align="center"><small>Designed & crafted with ❤️ by Karim Shoair.</small></div><br>