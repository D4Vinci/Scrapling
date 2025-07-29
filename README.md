<p align=center>
  <br>
  <a href="https://scrapling.readthedocs.io/en/latest/" target="_blank"><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/poster.png" style="width: 50%; height: 100%;"/></a>
  <br>
  <i>Easy, effortless Web Scraping as it should be!</i>
  <br>
</p>
<p align="center">
    <a href="https://github.com/D4Vinci/Scrapling/actions/workflows/tests.yml" alt="Tests">
        <img alt="Tests" src="https://github.com/D4Vinci/Scrapling/actions/workflows/tests.yml/badge.svg"></a>
    <a href="https://badge.fury.io/py/Scrapling" alt="PyPI version">
        <img alt="PyPI version" src="https://badge.fury.io/py/Scrapling.svg"></a>
    <a href="https://pepy.tech/project/scrapling" alt="PyPI Downloads">
        <img alt="PyPI Downloads" src="https://static.pepy.tech/badge/scrapling"></a>
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

Dealing with failing web scrapers due to anti-bot protections or website changes? Meet Scrapling.

Scrapling is a high-performance, intelligent web scraping library for Python that automatically adapts to website changes while significantly outperforming popular alternatives. For both beginners and experts, Scrapling provides powerful features while maintaining simplicity.

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

[Evomi](https://evomi.com?utm_source=github&utm_medium=banner&utm_campaign=d4vinci-scrapling) is your Swiss Quality Proxy Provider, starting at **$0.49/GB**

- 👩‍💻 **$0.49 per GB Residential Proxies**: Our price is unbeatable
- 👩‍💻 **24/7 Expert Support**: We will join your Slack Channel
- 🌍 **Global Presence**: Available in 150+ Countries
- ⚡ **Low Latency**
- 🔒 **Swiss Quality and Privacy**
- 🎁 **Free Trial**
- 🛡️ **99.9% Uptime**
- 🤝 **Special IP Pool selection**: Optimize for fast, quality, or quantity of ips
- 🔧 **Easy Integration**: Compatible with most software and programming languages

[![Evomi Banner](https://my.evomi.com/images/brand/cta.png)](https://evomi.com?utm_source=github&utm_medium=banner&utm_campaign=d4vinci-scrapling)
---

[Scrapeless](http://scrapeless.com/?utm_source=D4Vinci) – An all-in-one expandable and highly scalable tool for businesses & developers
- ⚡ [Scraping Browser](https://www.scrapeless.com/en/product/scraping-browser?utm_source=D4Vinci): Cloud-based browser with stealth mode, built to unlock websites at scale. Supports high concurrency, automation, and large-volume scraping. Puppeteer/Playwright compatible.
- ⚡ [Deep SerpApi](https://www.scrapeless.com/en/product/deep-serp-api?utm_source=D4Vinci): 13+ SERP types, $0.1/1K queries, 0.2s response.
- ⚡ [Scraping API](https://www.scrapeless.com/en/product/scraping-api?utm_source=D4Vinci): Access TikTok, Shopee, Amazon, and more.
- ⚡ [Universal Scraping API](https://www.scrapeless.com/en/product/universal-scraping-api?utm_source=D4Vinci): Web unlocker with IP rotation, fingerprinting, and CAPTCHA bypass.
- ⚡ [Proxies](https://www.scrapeless.com/en/product/proxies?utm_source=D4Vinci): 70M+ IPs in 195 countries, stable & low-cost at $1.8/GB.

📌 [Try now](https://app.scrapeless.com/passport/login?utm_source=D4Vinci) | [Docs](https://docs.scrapeless.com/en/scraping-browser/quickstart/introduction/?utm_source=D4Vinci)


<a href="http://scrapeless.com/?utm_source=D4Vinci"><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/scrapeless.jpg" style="width:85%" alt="Scrapeless Banner" ></a>
---
**Unlock Reliable Proxy Services with [Swiftproxy](https://www.swiftproxy.net/)**

With [Swiftproxy](https://www.swiftproxy.net/), you can access high-performance, secure proxies to enhance your web automation, privacy, and data collection efforts.
Developers and businesses trust our services to scale scraping tasks and ensure a safe online experience. Get started today at [Swiftproxy.net](https://www.swiftproxy.net/).

Anyone who signs up can use the discount code GHB5 to get 10% off their purchase at checkout

<img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/swiftproxy.jpeg" style="width:85%" alt="SwiftProxy Banner" >

---
Tired of your PC slowing you down? Can’t keep your machine on 24/7 for scraping?

**[PetroSky](https://petrosky.io/d4vinci)** delivers cutting-edge VPS hosting powered by:
- AMD EPYC 7003/9004 Series CPUs
- Up to 48GB RAM / 20 vCores
- Blazing-fast 10Gbps network
- Premium backbone with <0.7ms latency to Cloudflare, Google, AWS
- NVMe SSD

<img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/petrosky.png" style="width:80%;height:60%" alt="PetroSky Banner" >

---

<p align="center">
   <strong>Please consider <a href="https://github.com/sponsors/D4Vinci">joining them</a> to make <em>Scrapling</em>’s maintainance more sustainable!</strong>
</p>

---

## Key Features

### Fetch websites as you prefer with async support
- **HTTP Requests**: Fast and stealthy HTTP requests with the `Fetcher` class.
- **Dynamic Loading & Automation**: Fetch dynamic websites with the `DynamicFetcher` class through your real browser, Scrapling's stealth mode, Playwright's Chrome browser, or [NSTbrowser](https://app.nstbrowser.io/r/1vO5e5)'s browserless!
- **Anti-bot Protections Bypass**: Easily bypass protections with the `StealthyFetcher` and `DynamicFetcher` classes.

### Adaptive Scraping
- 🔄 **Smart Element Tracking**: Relocate elements after website changes using an intelligent similarity system and integrated storage.
- 🎯 **Flexible Selection**: CSS selectors, XPath selectors, filters-based search, text search, regex search, and more.
- 🔍 **Find Similar Elements**: Automatically locate elements similar to the element you found!
- 🧠 **Smart Content Scraping**: Extract data from multiple websites using Scrapling's powerful features without specific selectors.

### High Performance
- 🚀 **Lightning Fast**: Built from the ground up with performance in mind, outperforming most popular Python scraping libraries.
- 🔋 **Memory Efficient**: Optimized data structures for minimal memory footprint.
- ⚡ **Fast JSON serialization**: 10x faster than standard library.

### Developer Friendly
- 🛠️ **Powerful Navigation API**: Easy DOM traversal in all directions.
- 🧬 **Rich Text Processing**: All strings have built-in regex, cleaning methods, and more. All elements' attributes are optimized dictionaries with added methods that consume less memory than standard dictionaries.
- 📝 **Auto Selectors Generation**: Generate robust short and full CSS/XPath selectors for any element.
- 🔌 **Familiar API**: Similar to Scrapy/BeautifulSoup and the same pseudo-elements used in Scrapy.
- 📘 **Type hints**: Complete type/doc-strings coverage for future-proofing and best autocompletion support.

## Getting Started

```python
from scrapling.fetchers import Fetcher

# Do HTTP GET request to a web page and create a Selector instance
page = Fetcher.get('https://quotes.toscrape.com/', stealthy_headers=True)
# Get all text content from all HTML tags in the page except the `script` and `style` tags
page.get_all_text(ignore_tags=('script', 'style'))

# Get all quotes elements; any of these methods will return a list of strings directly (TextHandlers)
quotes = page.css('.quote .text::text')  # CSS selector
quotes = page.xpath('//span[@class="text"]/text()')  # XPath
quotes = page.css('.quote').css('.text::text')  # Chained selectors
quotes = [element.text for element in page.css('.quote .text')]  # Slower than bulk query above

# Get the first quote element
quote = page.css_first('.quote')  # same as page.css('.quote').first or page.css('.quote')[0]

# Tired of selectors? Use find_all/find
# Get all 'div' HTML tags that one of its 'class' values is 'quote'
quotes = page.find_all('div', {'class': 'quote'})
# Same as
quotes = page.find_all('div', class_='quote')
quotes = page.find_all(['div'], class_='quote')
quotes = page.find_all(class_='quote')  # and so on...

# Working with elements
quote.html_content  # Get the Inner HTML of this element
quote.prettify()  # Prettified version of Inner HTML above
quote.attrib  # Get that element's attributes
quote.path  # DOM path to element (List of all ancestors from <html> tag till the element itself)
```
To keep it simple, all methods can be chained on top of each other!

> [!NOTE]
> Check out the full documentation from [here](https://scrapling.readthedocs.io/en/latest/)

## Parsing Performance

Scrapling isn't just powerful - it's also blazing fast. Scrapling implements many best practices, design patterns, and numerous optimizations to save fractions of seconds. All of that while focusing exclusively on parsing HTML documents.
Here are benchmarks comparing Scrapling to popular Python libraries in two tests. 

### Text Extraction Speed Test (5000 nested elements).

This test consists of extracting the text content of 5000 nested div elements.


| # |      Library      | Time (ms) | vs Scrapling | 
|---|:-----------------:|:---------:|:------------:|
| 1 |     Scrapling     |   5.44    |     1.0x     |
| 2 |   Parsel/Scrapy   |   5.53    |    1.017x    |
| 3 |     Raw Lxml      |   6.76    |    1.243x    |
| 4 |      PyQuery      |   21.96   |    4.037x    |
| 5 |    Selectolax     |   67.12   |   12.338x    |
| 6 |   BS4 with Lxml   |  1307.03  |   240.263x   |
| 7 |  MechanicalSoup   |  1322.64  |   243.132x   |
| 8 | BS4 with html5lib |  3373.75  |   620.175x   |

As you see, Scrapling is on par with Scrapy and slightly faster than Lxml, which both libraries are built on top of. These are the closest results to Scrapling. PyQuery is also built on top of Lxml, but Scrapling is four times faster.

### Extraction By Text Speed Test

Scrapling can find elements based on its text content and find elements similar to these elements. The only known library with these two features, too, is AutoScraper.

So, we compared this to see how fast Scrapling can be in these two tasks compared to AutoScraper.

Here are the results:

|   Library   | Time (ms) | vs Scrapling |
|-------------|:---------:|:------------:|
|  Scrapling  |   2.51    |     1.0x     |
| AutoScraper |   11.41   |    4.546x    |

Scrapling can find elements with more methods and returns the entire element's `Selector` object, not only text like AutoScraper. So, to make this test fair, both libraries will extract an element with text, find similar elements, and then extract the text content for all of them. 

As you see, Scrapling is still 4.5 times faster at the same task. 

If we made Scrapling extract the elements only without stopping to extract each element's text, we would get speed twice as fast as this, but as I said, to make it fair comparison a bit :smile:

> All benchmarks' results are an average of 100 runs. See our [benchmarks.py](https://github.com/D4Vinci/Scrapling/blob/main/benchmarks.py) for methodology and to run your comparisons.

## Installation
Scrapling is a breeze to get started with. Starting from version 0.2.9, we require at least Python 3.9 to work.
```bash
pip3 install scrapling
```
Then run this command to install browsers' dependencies needed to use Fetcher classes
```bash
scrapling install
```
If you have any installation issues, please open an issue.


## More Sponsors!
<a href="https://serpapi.com/?utm_source=scrapling"><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/SerpApi.png" height="500" alt="SerpApi Banner" ></a>


## Contributing
Everybody is invited and welcome to contribute to Scrapling. There is a lot to do!

Please read the [contributing file](https://github.com/D4Vinci/Scrapling/blob/main/CONTRIBUTING.md) before doing anything.

## Disclaimer for Scrapling Project
> [!CAUTION]
> This library is provided for educational and research purposes only. By using this library, you agree to comply with local and international data scraping and privacy laws. The authors and contributors are not responsible for any misuse of this software. This library should not be used to violate the rights of others, for unethical purposes, or to use data in an unauthorized or illegal manner. Do not use it on any website unless you have permission from the website owner or within their allowed rules, such as the `robots.txt` file.

## License
This work is licensed under BSD-3

## Acknowledgments
This project includes code adapted from:
- Parsel (BSD License) - Used for [translator](https://github.com/D4Vinci/Scrapling/blob/main/scrapling/translator.py) submodule

## Thanks and References
- [Daijro](https://github.com/daijro)'s brilliant work on both [BrowserForge](https://github.com/daijro/browserforge) and [Camoufox](https://github.com/daijro/camoufox)
- [Vinyzu](https://github.com/Vinyzu)'s work on Playwright's mock on [Botright](https://github.com/Vinyzu/Botright)
- [brotector](https://github.com/kaliiiiiiiiii/brotector)
- [fakebrowser](https://github.com/kkoooqq/fakebrowser)
- [rebrowser-patches](https://github.com/rebrowser/rebrowser-patches)

## Known Issues
- In the auto-matching save process, the unique properties of the first element from the selection results are the only ones that get saved. If the selector you are using selects different elements on the page in different locations, auto-matching will return the first element to you only when you relocate it later. This doesn't include combined CSS selectors (Using commas to combine more than one selector, for example), as these selectors get separated, and each selector gets executed alone.

---
<div align="center"><small>Designed & crafted with ❤️ by Karim Shoair.</small></div><br>
