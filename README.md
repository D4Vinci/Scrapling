<p align=center>
  <br>
  <a href="https://scrapling.readthedocs.io/en/latest/" target="_blank"><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/poster.png" style="width: 50%; height: 100%;"/></a>
  <br>
  <i><code>Easy, effortless Web Scraping as it should be!</code></i>
</p>
<p align="center">
    <a href="https://github.com/D4Vinci/Scrapling/actions/workflows/tests.yml" alt="Tests">
        <img alt="Tests" src="https://github.com/D4Vinci/Scrapling/actions/workflows/tests.yml/badge.svg"></a>
    <a href="https://badge.fury.io/py/Scrapling" alt="PyPI version">
        <img alt="PyPI version" src="https://badge.fury.io/py/Scrapling.svg"></a>
    <a href="https://pepy.tech/project/scrapling" alt="PyPI Downloads">
        <img alt="PyPI Downloads" src="https://static.pepy.tech/personalized-badge/scrapling?period=total&units=INTERNATIONAL_SYSTEM&left_color=GRAY&right_color=GREEN&left_text=Downloads"></a>
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
    <a href="https://scrapling.readthedocs.io/en/latest/#installation">
        Installation
    </a>
    ·
    <a href="https://scrapling.readthedocs.io/en/latest/overview/">
        Overview
    </a>
    ·
    <a href="https://scrapling.readthedocs.io/en/latest/parsing/selection/">
        Selection methods
    </a>
    ·
    <a href="https://scrapling.readthedocs.io/en/latest/fetching/choosing/">
        Choosing a fetcher
    </a>
    ·
    <a href="https://scrapling.readthedocs.io/en/latest/tutorials/migrating_from_beautifulsoup/">
        Migrating from Beautifulsoup
    </a>
</p>

**Stop fighting anti-bot systems. Stop rewriting selectors after every website update.**

Scrapling isn't just another Web Scraping library. It's the first **adaptive** scraping library that learns from website changes and evolves with them. While other libraries break when websites update their structure, Scrapling automatically relocates your elements and keeps your scrapers running.

Built for the modern Web, Scrapling has its own rapid parsing engine and its fetchers to handle all Web Scraping challenges you are facing or will face. Built by Web Scrapers for Web Scrapers and regular users, there's something for everyone.

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

<a href="https://evomi.com?utm_source=github&utm_medium=banner&utm_campaign=d4vinci-scrapling" target="_blank" title="Evomi is your Swiss Quality Proxy Provider, starting at $0.49/GB"><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/evomi.png"></a>
<a href="https://petrosky.io/d4vinci" target="_blank" title="PetroSky delivers cutting-edge VPS hosting."><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/petrosky.png"></a>
<a href="https://www.swiftproxy.net/" target="_blank" title="Unlock Reliable Proxy Services with Swiftproxy!"><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/swiftproxy.png"></a>
<a href="https://serpapi.com/?utm_source=scrapling" target="_blank" title="Scrape Google and other search engines with SerpApi"><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/SerpApi.png"></a>

<!-- /sponsors -->

<i><sub>Do you want to show your ad here? Click [here](https://github.com/sponsors/D4Vinci) and choose the tier that suites you!</sub></i>

---

## Key Features

### Advanced Websites Fetching with Session Support
- **HTTP Requests**: Fast and stealthy HTTP requests with the `Fetcher` class. Can impersonate browsers' TLS fingerprint, headers, and use HTTP3.
- **Dynamic Loading**: Fetch dynamic websites with full browser automation through the `DynamicFetcher` class supporting Playwright's Chromium, real Chrome, and custom stealth mode.
- **Anti-bot Bypass**: Advanced stealth capabilities with `StealthyFetcher` using a modified version of Firefox and fingerprint spoofing. Can bypass all levels of Cloudflare's Turnstile with automation easily.
- **Session Management**: Persistent session support with `FetcherSession`, `StealthySession`, and `DynamicSession` classes for cookie and state management across requests.
- **Async Support**: Complete async support across all fetchers and dedicated async session classes.

### Adaptive Scraping & AI Integration
- 🔄 **Smart Element Tracking**: Relocate elements after website changes using intelligent similarity algorithms.
- 🎯 **Smart Flexible Selection**: CSS selectors, XPath selectors, filter-based search, text search, regex search, and more. 
- 🔍 **Find Similar Elements**: Automatically locate elements similar to found elements.
- 🤖 **MCP Server to be used with AI**: Built-in MCP server for AI-assisted Web Scraping and data extraction. The MCP server features custom, powerful capabilities that utilize Scrapling to extract targeted content before passing it to the AI (Claude/Cursor/etc), thereby speeding up operations and reducing costs by minimizing token usage.

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

### New Session Architecture
Scrapling 0.3 introduces a completely revamped session system:
- **Persistent Sessions**: Maintain cookies, headers, and authentication across multiple requests
- **Automatic Session Management**: Smart session lifecycle handling with proper cleanup
- **Session Inheritance**: All fetchers support both one-off requests and persistent session usage
- **Concurrent Session Support**: Run multiple isolated sessions simultaneously

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
    page = session.fetch('https://nopecha.com/demo/cloudflare')
    data = page.css('#padded_content a')

# Or use one-off request style, it opens the browser for this request, then closes it after finishing
page = StealthyFetcher.fetch('https://nopecha.com/demo/cloudflare')
data = page.css('#padded_content a')
    
# Full browser automation (Keep the browser open until you finish)
with DynamicSession(headless=True, disable_resources=False, network_idle=True) as session:
    page = session.fetch('https://quotes.toscrape.com/')
    data = page.xpath('//span[@class="text"]/text()')  # XPath selector if you prefer it

# Or use one-off request style, it opens the browser for this request, then closes it after finishing
page = DynamicFetcher.fetch('https://quotes.toscrape.com/')
data = page.css('.quote .text::text')
```

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
And it works exactly the same way!

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

```bash
# Launch interactive Web Scraping shell
scrapling shell

# Extract pages to a file directly without programming (Extracts the content inside `body` tag by default)
# If the output file ends with `.txt`, then the text content of the target will be extracted.
# If ended with `.md`, it will be a markdown representation of the HTML content, and `.html` will be the HTML content right away.
scrapling extract get 'https://example.com' content.md
scrapling extract get 'https://example.com' content.txt --css-selector '#fromSkipToProducts' --impersonate 'chrome'  # All elements matching the CSS selector '#fromSkipToProducts'
scrapling extract fetch 'https://example.com' content.md --css-selector '#fromSkipToProducts' --no-headless
scrapling extract stealthy-fetch 'https://nopecha.com/demo/cloudflare' captchas.html --css-selector '#padded_content a' --solve-cloudflare
```

> [!NOTE]
> There are many additional features, but we want to keep this page short, like the MCP server and the interactive Web Scraping Shell. Check out the full documentation [here](https://scrapling.readthedocs.io/en/latest/)

## Performance Benchmarks

Scrapling isn't just powerful—it's also blazing fast, and version 0.3 delivers exceptional performance improvements across all operations!

### Text Extraction Speed Test (5000 nested elements)

| # |      Library      | Time (ms) | vs Scrapling | 
|---|:-----------------:|:---------:|:------------:|
| 1 |     Scrapling     |   1.88    |     1.0x     |
| 2 |   Parsel/Scrapy   |   1.96    |    1.043x    |
| 3 |     Raw Lxml      |   2.32    |    1.234x    |
| 4 |      PyQuery      |   20.2    |     ~11x     |
| 5 |    Selectolax     |   85.2    |     ~45x     |
| 6 |  MechanicalSoup   |  1305.84  |    ~695x     |
| 7 |   BS4 with Lxml   |  1307.92  |    ~696x     |
| 8 | BS4 with html5lib |  3336.28  |    ~1775x    |

### Element Similarity & Text Search Performance

Scrapling's adaptive element finding capabilities significantly outperform alternatives:

|   Library   | Time (ms) | vs Scrapling |
|-------------|:---------:|:------------:|
|  Scrapling  |   2.02    |     1.0x     |
| AutoScraper |   10.26   |    5.08x     |


> All benchmarks represent averages of 100+ runs. See [benchmarks.py](https://github.com/D4Vinci/Scrapling/blob/main/benchmarks.py) for methodology.

## Installation

Scrapling requires Python 3.10 or higher:

```bash
pip install scrapling
```

#### Fetchers Setup

If you are going to use any of the fetchers or their classes, then install browser dependencies with
```bash
scrapling install
```

This downloads all browsers with their system dependencies and fingerprint manipulation dependencies.

### Optional Dependencies

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

## Contributing

We welcome contributions! Please read our [contributing guidelines](https://github.com/D4Vinci/Scrapling/blob/main/CONTRIBUTING.md) before getting started.

## Disclaimer

> [!CAUTION]
> This library is provided for educational and research purposes only. By using this library, you agree to comply with local and international data scraping and privacy laws. The authors and contributors are not responsible for any misuse of this software. Always respect website terms of service and robots.txt files.

## License

This work is licensed under the BSD-3-Clause License.

## Acknowledgments

This project includes code adapted from:
- Parsel (BSD License)—Used for [translator](https://github.com/D4Vinci/Scrapling/blob/main/scrapling/core/translator.py) submodule

## Thanks and References

- [Daijro](https://github.com/daijro)'s brilliant work on [BrowserForge](https://github.com/daijro/browserforge) and [Camoufox](https://github.com/daijro/camoufox)
- [Vinyzu](https://github.com/Vinyzu)'s work on [Botright](https://github.com/Vinyzu/Botright)
- [brotector](https://github.com/kaliiiiiiiiii/brotector) for browser detection bypass techniques
- [fakebrowser](https://github.com/kkoooqq/fakebrowser) for fingerprinting research
- [rebrowser-patches](https://github.com/rebrowser/rebrowser-patches) for stealth improvements

---
<div align="center"><small>Designed & crafted with ❤️ by Karim Shoair.</small></div><br>
