# 🕷️ Scrapling: Undetectable, Lightning-Fast, and Adaptive Web Scraping for Python
[![Tests](https://github.com/D4Vinci/Scrapling/actions/workflows/tests.yml/badge.svg)](https://github.com/D4Vinci/Scrapling/actions/workflows/tests.yml) [![PyPI version](https://badge.fury.io/py/Scrapling.svg)](https://badge.fury.io/py/Scrapling) [![Supported Python versions](https://img.shields.io/pypi/pyversions/scrapling.svg)](https://pypi.org/project/scrapling/) [![PyPI Downloads](https://static.pepy.tech/badge/scrapling)](https://pepy.tech/project/scrapling)

Dealing with failing web scrapers due to anti-bot protections or website changes? Meet Scrapling.

Scrapling is a high-performance, intelligent web scraping library for Python that automatically adapts to website changes while significantly outperforming popular alternatives. For both beginners and experts, Scrapling provides powerful features while maintaining simplicity.

```python
>> from scrapling.default import Fetcher, StealthyFetcher, PlayWrightFetcher
# Fetch websites' source under the radar!
>> page = StealthyFetcher.fetch('https://example.com', headless=True, network_idle=True)
>> print(page.status)
200
>> products = page.css('.product', auto_save=True)  # Scrape data that survives website design changes!
>> # Later, if the website structure changes, pass `auto_match=True`
>> products = page.css('.product', auto_match=True)  # and Scrapling still finds them!
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
- 🤝 **Special IP Pool selection**: Optimize for fast, quality or quantity of ips
- 🔧 **Easy Integration**: Compatible with most software and programming languages

[![Evomi Banner](https://my.evomi.com/images/brand/cta.png)](https://evomi.com?utm_source=github&utm_medium=banner&utm_campaign=d4vinci-scrapling)
---

## Table of content
  * [Key Features](#key-features)
    * [Fetch websites as you prefer](#fetch-websites-as-you-prefer)
    * [Adaptive Scraping](#adaptive-scraping)
    * [Performance](#performance)
    * [Developing Experience](#developing-experience)
  * [Getting Started](#getting-started)
  * [Parsing Performance](#parsing-performance)
    * [Text Extraction Speed Test (5000 nested elements).](#text-extraction-speed-test-5000-nested-elements)
    * [Extraction By Text Speed Test](#extraction-by-text-speed-test)
  * [Installation](#installation)
  * [Fetching Websites](#fetching-websites)
    * [Features](#features)
    * [Fetcher class](#fetcher)
    * [StealthyFetcher class](#stealthyfetcher)
    * [PlayWrightFetcher class](#playwrightfetcher)
  * [Advanced Parsing Features](#advanced-parsing-features)
    * [Smart Navigation](#smart-navigation)
    * [Content-based Selection & Finding Similar Elements](#content-based-selection--finding-similar-elements)
    * [Handling Structural Changes](#handling-structural-changes)
      * [Real World Scenario](#real-world-scenario)
    * [Find elements by filters](#find-elements-by-filters)
    * [Is That All?](#is-that-all)
  * [More Advanced Usage](#more-advanced-usage)
  * [⚡ Enlightening Questions and FAQs](#-enlightening-questions-and-faqs)
    * [How does auto-matching work?](#how-does-auto-matching-work)
    * [How does the auto-matching work if I didn't pass a URL while initializing the Adaptor object?](#how-does-the-auto-matching-work-if-i-didnt-pass-a-url-while-initializing-the-adaptor-object)
    * [If all things about an element can change or get removed, what are the unique properties to be saved?](#if-all-things-about-an-element-can-change-or-get-removed-what-are-the-unique-properties-to-be-saved)
    * [I have enabled the `auto_save`/`auto_match` parameter while selecting and it got completely ignored with a warning message](#i-have-enabled-the-auto_saveauto_match-parameter-while-selecting-and-it-got-completely-ignored-with-a-warning-message)
    * [I have done everything as the docs but the auto-matching didn't return anything, what's wrong?](#i-have-done-everything-as-the-docs-but-the-auto-matching-didnt-return-anything-whats-wrong)
    * [Can Scrapling replace code built on top of BeautifulSoup4?](#can-scrapling-replace-code-built-on-top-of-beautifulsoup4)
    * [Can Scrapling replace code built on top of AutoScraper?](#can-scrapling-replace-code-built-on-top-of-autoscraper)
    * [Is Scrapling thread-safe?](#is-scrapling-thread-safe)
  * [More Sponsors!](#more-sponsors)
  * [Contributing](#contributing)
  * [Disclaimer for Scrapling Project](#disclaimer-for-scrapling-project)
  * [License](#license)
  * [Acknowledgments](#acknowledgments)
  * [Thanks and References](#thanks-and-references)
  * [Known Issues](#known-issues)

## Key Features

### Fetch websites as you prefer
- **HTTP requests**: Stealthy and fast HTTP requests with `Fetcher`
- **Stealthy fetcher**: Annoying anti-bot protection? No problem! Scrapling can bypass almost all of them with `StealthyFetcher` with default configuration!
- **Your preferred browser**: Use your real browser with CDP, [NSTbrowser](https://app.nstbrowser.io/r/1vO5e5)'s browserless, PlayWright with stealth mode, or even vanilla PlayWright -  All is possible with `PlayWrightFetcher`!

### Adaptive Scraping
- 🔄 **Smart Element Tracking**: Locate previously identified elements after website structure changes, using an intelligent similarity system and integrated storage.
- 🎯 **Flexible Querying**: Use CSS selectors, XPath, Elements filters, text search, or regex - chain them however you want!
- 🔍 **Find Similar Elements**: Automatically locate elements similar to the element you want on the page (Ex: other products like the product you found on the page).
- 🧠 **Smart Content Scraping**: Extract data from multiple websites without specific selectors using Scrapling powerful features.

### Performance
- 🚀 **Lightning Fast**: Built from the ground up with performance in mind, outperforming most popular Python scraping libraries (outperforming BeautifulSoup in parsing by up to 620x in our tests).
- 🔋 **Memory Efficient**: Optimized data structures for minimal memory footprint.
- ⚡ **Fast JSON serialization**: 10x faster JSON serialization than the standard json library with more options.

### Developing Experience
- 🛠️ **Powerful Navigation API**: Traverse the DOM tree easily in all directions and get the info you want (parent, ancestors, sibling, children, next/previous element, and more).
- 🧬 **Rich Text Processing**: All strings have built-in methods for regex matching, cleaning, and more. All elements' attributes are read-only dictionaries that are faster than standard dictionaries with added methods.
- 📝 **Automatic Selector Generation**: Create robust CSS/XPath selectors for any element.
- 🔌 **API Similar to Scrapy/BeautifulSoup**: Familiar methods and similar pseudo-elements for Scrapy and BeautifulSoup users.
- 📘 **Type hints and test coverage**: Complete type coverage and almost full test coverage for better IDE support and fewer bugs, respectively.

## Getting Started

```python
from scrapling import Fetcher

fetcher = Fetcher(auto_match=False)

# Fetch a web page and create an Adaptor instance
page = fetcher.get('https://quotes.toscrape.com/', stealthy_headers=True)
# Get all strings in the full page
page.get_all_text(ignore_tags=('script', 'style'))

# Get all quotes, any of these methods will return a list of strings (TextHandlers)
quotes = page.css('.quote .text::text')  # CSS selector
quotes = page.xpath('//span[@class="text"]/text()')  # XPath
quotes = page.css('.quote').css('.text::text')  # Chained selectors
quotes = [element.text for element in page.css('.quote .text')]  # Slower than bulk query above

# Get the first quote element
quote = page.css_first('.quote')  # / page.css('.quote').first / page.css('.quote')[0]

# Tired of selectors? Use find_all/find
quotes = page.find_all('div', {'class': 'quote'})
# Same as
quotes = page.find_all('div', class_='quote')
quotes = page.find_all(['div'], class_='quote')
quotes = page.find_all(class_='quote')  # and so on...

# Working with elements
quote.html_content  # Inner HTML
quote.prettify()  # Prettified version of Inner HTML
quote.attrib  # Element attributes
quote.path  # DOM path to element (List)
```
To keep it simple, all methods can be chained on top of each other!

## Parsing Performance

Scrapling isn't just powerful - it's also blazing fast. Scrapling implements many best practices, design patterns, and numerous optimizations to save fractions of seconds. All of that while focusing exclusively on parsing HTML documents.
Here are benchmarks comparing Scrapling to popular Python libraries in two tests. 

### Text Extraction Speed Test (5000 nested elements).

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

As you see, Scrapling is on par with Scrapy and slightly faster than Lxml which both libraries are built on top of. These are the closest results to Scrapling. PyQuery is also built on top of Lxml but still, Scrapling is 4 times faster.

### Extraction By Text Speed Test

|   Library   | Time (ms) | vs Scrapling |
|:-----------:|:---------:|:------------:|
|  Scrapling  |   2.51    |     1.0x     |
| AutoScraper |   11.41   |    4.546x    |

Scrapling can find elements with more methods and it returns full element `Adaptor` objects not only the text like AutoScraper. So, to make this test fair, both libraries will extract an element with text, find similar elements, and then extract the text content for all of them. As you see, Scrapling is still 4.5 times faster at the same task.

> All benchmarks' results are an average of 100 runs. See our [benchmarks.py](https://github.com/D4Vinci/Scrapling/blob/main/benchmarks.py) for methodology and to run your comparisons.

## Installation
Scrapling is a breeze to get started with - Starting from version 0.2, we require at least Python 3.8 to work.
```bash
pip3 install scrapling
```
- For using the `StealthyFetcher`, go to the command line and download the browser with
<details><summary>Windows OS</summary>

```bash
camoufox fetch --browserforge
```
</details>
<details><summary>MacOS</summary>

```bash
python3 -m camoufox fetch --browserforge
```
</details>
<details><summary>Linux</summary>

```bash
python -m camoufox fetch --browserforge
```
On a fresh installation of Linux, you may also need the following Firefox dependencies:
- Debian-based distros
    ```bash
    sudo apt install -y libgtk-3-0 libx11-xcb1 libasound2
    ```
- Arch-based distros
    ```bash
    sudo pacman -S gtk3 libx11 libxcb cairo libasound alsa-lib
    ```
</details>

<small> See the official <a href="https://camoufox.com/python/installation/#download-the-browser">Camoufox documentation</a> for more info on installation</small>

- If you are going to use the `PlayWrightFetcher` options, then install Playwright's Chromium browser with:
```commandline
playwright install chromium
```
- If you are going to use normal requests only with the `Fetcher` class then update the fingerprints files with:
```commandline
python -m browserforge update
```

## Fetching Websites
Fetchers are basically interfaces that do requests or fetch pages for you in a single request fashion then return an `Adaptor` object for you. This feature was introduced because the only option we had before was to fetch the page as you want then pass it manually to the `Adaptor` class to create an `Adaptor` instance and start playing around with the page.

### Features
You might be a little bit confused by now so let me clear things up. All fetcher-type classes are imported in the same way
```python
from scrapling import Fetcher, StealthyFetcher, PlayWrightFetcher
```
And all of them can take these initialization arguments: `auto_match`, `huge_tree`, `keep_comments`, `storage`, `storage_args`, and `debug` which are the same ones you give to the `Adaptor` class.

If you don't want to pass arguments to the generated `Adaptor` object and want to use the default values, you can use this import instead for cleaner code:
```python
from scrapling.default import Fetcher, StealthyFetcher, PlayWrightFetcher
```
then use it right away without initializing like:
```python
page = StealthyFetcher.fetch('https://example.com') 
```

Also, the `Response` object returned from all fetchers is the same as `Adaptor` object except it has these added attributes: `status`, `reason`, `cookies`, `headers`, and `request_headers`. All `cookies`, `headers`, and `request_headers` are always of type `dictionary`.
> [!NOTE]
> The `auto_match` argument is enabled by default which is the one you should care about the most as you will see later.
### Fetcher
This class is built on top of [httpx](https://www.python-httpx.org/) with additional configuration options, here you can do `GET`, `POST`, `PUT`, and `DELETE` requests.

For all methods, you have `stealth_headers` which makes `Fetcher` create and use real browser's headers then create a referer header as if this request came from Google's search of this URL's domain. It's enabled by default.

You can route all traffic (HTTP and HTTPS) to a proxy for any of these methods in this format `http://username:password@localhost:8030`
```python
>> page = Fetcher().get('https://httpbin.org/get', stealth_headers=True, follow_redirects=True)
>> page = Fetcher().post('https://httpbin.org/post', data={'key': 'value'}, proxy='http://username:password@localhost:8030')
>> page = Fetcher().put('https://httpbin.org/put', data={'key': 'value'})
>> page = Fetcher().delete('https://httpbin.org/delete')
```
### StealthyFetcher
This class is built on top of [Camoufox](https://github.com/daijro/camoufox) which by default bypasses most of the anti-bot protections. Scrapling adds extra layers of flavors and configurations to increase performance and undetectability even further.
```python
>> page = StealthyFetcher().fetch('https://www.browserscan.net/bot-detection')  # Running headless by default
>> page.status == 200
True
```
> Note: all requests done by this fetcher is waiting by default for all JS to be fully loaded and executed so you don't have to :)

<details><summary><strong>For the sake of simplicity, expand this for the complete list of arguments</strong></summary>

|      Argument       | Description                                                                                                                                                                                                                                                                                                                                                                                                     | Optional |
|:-------------------:|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|:--------:|
|         url         | Target url                                                                                                                                                                                                                                                                                                                                                                                                      |    ❌     |
|      headless       | Pass `True` to run the browser in headless/hidden (**default**), `virtual` to run it in virtual screen mode, or `False` for headful/visible mode. The `virtual` mode requires having `xvfb` installed.                                                                                                                                                                                                          |    ✔️    |
|    block_images     | Prevent the loading of images through Firefox preferences. _This can help save your proxy usage but be careful with this option as it makes some websites never finish loading._                                                                                                                                                                                                                                |    ✔️    |
|  disable_resources  | Drop requests of unnecessary resources for a speed boost. It depends but it made requests ~25% faster in my tests for some websites.<br/>Requests dropped are of type `font`, `image`, `media`, `beacon`, `object`, `imageset`, `texttrack`, `websocket`, `csp_report`, and `stylesheet`. _This can help save your proxy usage but be careful with this option as it makes some websites never finish loading._ |    ✔️    |
|    google_search    | Enabled by default, Scrapling will set the referer header to be as if this request came from a Google search for this website's domain name.                                                                                                                                                                                                                                                                    |    ✔️    |
|    extra_headers    | A dictionary of extra headers to add to the request. _The referer set by the `google_search` argument takes priority over the referer set here if used together._                                                                                                                                                                                                                                               |    ✔️    |
|    block_webrtc     | Blocks WebRTC entirely.                                                                                                                                                                                                                                                                                                                                                                                         |    ✔️    |
|     page_action     | Added for automation. A function that takes the `page` object, does the automation you need, then returns `page` again.                                                                                                                                                                                                                                                                                         |    ✔️    |
|       addons        | List of Firefox addons to use. **Must be paths to extracted addons.**                                                                                                                                                                                                                                                                                                                                           |    ✔️    |
|      humanize       | Humanize the cursor movement. Takes either True or the MAX duration in seconds of the cursor movement. The cursor typically takes up to 1.5 seconds to move across the window.                                                                                                                                                                                                                                  |    ✔️    |
|     allow_webgl     | Whether to allow WebGL. To prevent leaks, only use this for special cases.                                                                                                                                                                                                                                                                                                                                      |    ✔️    |
|     disable_ads     | Enabled by default, this installs `uBlock Origin` addon on the browser if enabled.                                                                                                                                                                                                                                                                                                                              |    ✔️    |
|    network_idle     | Wait for the page until there are no network connections for at least 500 ms.                                                                                                                                                                                                                                                                                                                                   |    ✔️    |
|       timeout       | The timeout in milliseconds that is used in all operations and waits through the page. The default is 30000.                                                                                                                                                                                                                                                                                                    |    ✔️    |
|    wait_selector    | Wait for a specific css selector to be in a specific state.                                                                                                                                                                                                                                                                                                                                                     |    ✔️    |
|        proxy        | The proxy to be used with requests, it can be a string or a dictionary with the keys 'server', 'username', and 'password' only.                                                                                                                                                                                                                                                                                 |    ✔️    |
|    os_randomize     | If enabled, Scrapling will randomize the OS fingerprints used. The default is Scrapling matching the fingerprints with the current OS.                                                                                                                                                                                                                                                                          |    ✔️    |
| wait_selector_state | The state to wait for the selector given with `wait_selector`. _Default state is `attached`._                                                                                                                                                                                                                                                                                                                   |    ✔️    |

</details>

This list isn't final so expect a lot more additions and flexibility to be added in the next versions!

### PlayWrightFetcher
This class is built on top of [Playwright](https://playwright.dev/python/) which currently provides 4 main run options but they can be mixed as you want.
```python
>> page = PlayWrightFetcher().fetch('https://www.google.com/search?q=%22Scrapling%22', disable_resources=True)  # Vanilla Playwright option
>> page.css_first("#search a::attr(href)")
'https://github.com/D4Vinci/Scrapling'
```
> Note: all requests done by this fetcher is waiting by default for all JS to be fully loaded and executed so you don't have to :)

Using this Fetcher class, you can make requests with:
  1) Vanilla Playwright without any modifications other than the ones you chose.
  2) Stealthy Playwright with the stealth mode I wrote for it. It's still a WIP but it bypasses many online tests like [Sannysoft's](https://bot.sannysoft.com/).</br> Some of the things this fetcher's stealth mode does include:
     * Patching the CDP runtime fingerprint.
     * Mimics some of the real browsers' properties by injecting several JS files and using custom options.
     * Using custom flags on launch to hide Playwright even more and make it faster.
     * Generates real browser's headers of the same type and same user OS then append it to the request's headers.
  3) Real browsers by passing the `real_chrome` argument or the CDP URL of your browser to be controlled by the Fetcher and most of the options can be enabled on it.
  4) [NSTBrowser](https://app.nstbrowser.io/r/1vO5e5)'s [docker browserless](https://hub.docker.com/r/nstbrowser/browserless) option by passing the CDP URL and enabling `nstbrowser_mode` option.

> Hence using the `real_chrome` argument requires that you have chrome browser installed on your device

Add that to a lot of controlling/hiding options as you will see in the arguments list below.

<details><summary><strong>Expand this for the complete list of arguments</strong></summary>

|      Argument       | Description                                                                                                                                                                                                                                                                                                                                                                                                     | Optional |
|:-------------------:|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|:--------:|
|         url         | Target url                                                                                                                                                                                                                                                                                                                                                                                                      |    ❌     |
|      headless       | Pass `True` to run the browser in headless/hidden (**default**), or `False` for headful/visible mode.                                                                                                                                                                                                                                                                                                           |    ✔️    |
|  disable_resources  | Drop requests of unnecessary resources for a speed boost. It depends but it made requests ~25% faster in my tests for some websites.<br/>Requests dropped are of type `font`, `image`, `media`, `beacon`, `object`, `imageset`, `texttrack`, `websocket`, `csp_report`, and `stylesheet`. _This can help save your proxy usage but be careful with this option as it makes some websites never finish loading._ |    ✔️    |
|      useragent      | Pass a useragent string to be used. **Otherwise the fetcher will generate a real Useragent of the same browser and use it.**                                                                                                                                                                                                                                                                                    |    ✔️    |
|    network_idle     | Wait for the page until there are no network connections for at least 500 ms.                                                                                                                                                                                                                                                                                                                                   |    ✔️    |
|       timeout       | The timeout in milliseconds that is used in all operations and waits through the page. The default is 30000.                                                                                                                                                                                                                                                                                                    |    ✔️    |
|     page_action     | Added for automation. A function that takes the `page` object, does the automation you need, then returns `page` again.                                                                                                                                                                                                                                                                                         |    ✔️    |
|    wait_selector    | Wait for a specific css selector to be in a specific state.                                                                                                                                                                                                                                                                                                                                                     |    ✔️    |
| wait_selector_state | The state to wait for the selector given with `wait_selector`. _Default state is `attached`._                                                                                                                                                                                                                                                                                                                   |    ✔️    |
|    google_search    | Enabled by default, Scrapling will set the referer header to be as if this request came from a Google search for this website's domain name.                                                                                                                                                                                                                                                                    |    ✔️    |
|    extra_headers    | A dictionary of extra headers to add to the request. The referer set by the `google_search` argument takes priority over the referer set here if used together.                                                                                                                                                                                                                                                 |    ✔️    |
|        proxy        | The proxy to be used with requests, it can be a string or a dictionary with the keys 'server', 'username', and 'password' only.                                                                                                                                                                                                                                                                                 |    ✔️    |
|     hide_canvas     | Add random noise to canvas operations to prevent fingerprinting.                                                                                                                                                                                                                                                                                                                                                |    ✔️    |
|    disable_webgl    | Disables WebGL and WebGL 2.0 support entirely.                                                                                                                                                                                                                                                                                                                                                                  |    ✔️    |
|       stealth       | Enables stealth mode, always check the documentation to see what stealth mode does currently.                                                                                                                                                                                                                                                                                                                   |    ✔️    |
|     real_chrome     | If you have chrome browser installed on your device, enable this and the Fetcher will launch an instance of your browser and use it.                                                                                                                                                                                                                                                                            |    ✔️    |
|       locale        | Set the locale for the browser if wanted. The default value is `en-US`.                                                                                                                                                                                                                                                                                                                                         |    ✔️    |
|       cdp_url       | Instead of launching a new browser instance, connect to this CDP URL to control real browsers/NSTBrowser through CDP.                                                                                                                                                                                                                                                                                           |    ✔️    |
|   nstbrowser_mode   | Enables NSTBrowser mode, **it have to be used with `cdp_url` argument or it will get completely ignored.**                                                                                                                                                                                                                                                                                                      |    ✔️    |
|  nstbrowser_config  | The config you want to send with requests to the NSTBrowser. _If left empty, Scrapling defaults to an optimized NSTBrowser's docker browserless config._                                                                                                                                                                                                                                                        |    ✔️    |

</details>

This list isn't final so expect a lot more additions and flexibility to be added in the next versions!

## Advanced Parsing Features
### Smart Navigation
```python
>>> quote.tag
'div'

>>> quote.parent
<data='<div class="col-md-8"> <div class="quote...' parent='<div class="row"> <div class="col-md-8">...'>

>>> quote.parent.tag
'div'

>>> quote.children
[<data='<span class="text" itemprop="text">“The...' parent='<div class="quote" itemscope itemtype="h...'>,
 <data='<span>by <small class="author" itemprop=...' parent='<div class="quote" itemscope itemtype="h...'>,
 <data='<div class="tags"> Tags: <meta class="ke...' parent='<div class="quote" itemscope itemtype="h...'>]

>>> quote.siblings
[<data='<div class="quote" itemscope itemtype="h...' parent='<div class="col-md-8"> <div class="quote...'>,
 <data='<div class="quote" itemscope itemtype="h...' parent='<div class="col-md-8"> <div class="quote...'>,
...]

>>> quote.next  # gets the next element, the same logic applies to `quote.previous`
<data='<div class="quote" itemscope itemtype="h...' parent='<div class="col-md-8"> <div class="quote...'>

>>> quote.children.css_first(".author::text")
'Albert Einstein'

>>> quote.has_class('quote')
True

# Generate new selectors for any element
>>> quote.generate_css_selector
'body > div > div:nth-of-type(2) > div > div'

# Test these selectors on your favorite browser or reuse them again in the library's methods!
>>> quote.generate_xpath_selector
'//body/div/div[2]/div/div'
```
If your case needs more than the element's parent, you can iterate over the whole ancestors' tree of any element like below
```python
for ancestor in quote.iterancestors():
    # do something with it...
```
You can search for a specific ancestor of an element that satisfies a function, all you need to do is to pass a function that takes an `Adaptor` object as an argument and return `True` if the condition satisfies or `False` otherwise like below:
```python
>>> quote.find_ancestor(lambda ancestor: ancestor.has_class('row'))
<data='<div class="row"> <div class="col-md-8">...' parent='<div class="container"> <div class="row...'>
```

### Content-based Selection & Finding Similar Elements
You can select elements by their text content in multiple ways, here's a full example on another website:
```python
>>> page = Fetcher().get('https://books.toscrape.com/index.html')

>>> page.find_by_text('Tipping the Velvet')  # Find the first element whose text fully matches this text
<data='<a href="catalogue/tipping-the-velvet_99...' parent='<h3><a href="catalogue/tipping-the-velve...'>

>>> page.find_by_text('Tipping the Velvet', first_match=False)  # Get all matches if there are more
[<data='<a href="catalogue/tipping-the-velvet_99...' parent='<h3><a href="catalogue/tipping-the-velve...'>]

>>> page.find_by_regex(r'£[\d\.]+')  # Get the first element that its text content matches my price regex
<data='<p class="price_color">£51.77</p>' parent='<div class="product_price"> <p class="pr...'>

>>> page.find_by_regex(r'£[\d\.]+', first_match=False)  # Get all elements that matches my price regex
[<data='<p class="price_color">£51.77</p>' parent='<div class="product_price"> <p class="pr...'>,
 <data='<p class="price_color">£53.74</p>' parent='<div class="product_price"> <p class="pr...'>,
 <data='<p class="price_color">£50.10</p>' parent='<div class="product_price"> <p class="pr...'>,
 <data='<p class="price_color">£47.82</p>' parent='<div class="product_price"> <p class="pr...'>,
 ...]
```
Find all elements that are similar to the current element in location and attributes
```python
# For this case, ignore the 'title' attribute while matching
>>> page.find_by_text('Tipping the Velvet').find_similar(ignore_attributes=['title'])
[<data='<a href="catalogue/a-light-in-the-attic_...' parent='<h3><a href="catalogue/a-light-in-the-at...'>,
 <data='<a href="catalogue/soumission_998/index....' parent='<h3><a href="catalogue/soumission_998/in...'>,
 <data='<a href="catalogue/sharp-objects_997/ind...' parent='<h3><a href="catalogue/sharp-objects_997...'>,
...]

# You will notice that the number of elements is 19 not 20 because the current element is not included.
>>> len(page.find_by_text('Tipping the Velvet').find_similar(ignore_attributes=['title']))
19

# Get the `href` attribute from all similar elements
>>> [element.attrib['href'] for element in page.find_by_text('Tipping the Velvet').find_similar(ignore_attributes=['title'])]
['catalogue/a-light-in-the-attic_1000/index.html',
 'catalogue/soumission_998/index.html',
 'catalogue/sharp-objects_997/index.html',
 ...]
```
To increase the complexity a little bit, let's say we want to get all books' data using that element as a starting point for some reason
```python
>>> for product in page.find_by_text('Tipping the Velvet').parent.parent.find_similar():
        print({
            "name": product.css_first('h3 a::text'),
            "price": product.css_first('.price_color').re_first(r'[\d\.]+'),
            "stock": product.css('.availability::text')[-1].clean()
        })
{'name': 'A Light in the ...', 'price': '51.77', 'stock': 'In stock'}
{'name': 'Soumission', 'price': '50.10', 'stock': 'In stock'}
{'name': 'Sharp Objects', 'price': '47.82', 'stock': 'In stock'}
...
```
The [documentation](https://github.com/D4Vinci/Scrapling/tree/main/docs/Examples) will provide more advanced examples.

### Handling Structural Changes
Let's say you are scraping a page with a structure like this:
```html
<div class="container">
    <section class="products">
        <article class="product" id="p1">
            <h3>Product 1</h3>
            <p class="description">Description 1</p>
        </article>
        <article class="product" id="p2">
            <h3>Product 2</h3>
            <p class="description">Description 2</p>
        </article>
    </section>
</div>
```
And you want to scrape the first product, the one with the `p1` ID. You will probably write a selector like this
```python
page.css('#p1')
```
When website owners implement structural changes like
```html
<div class="new-container">
    <div class="product-wrapper">
        <section class="products">
            <article class="product new-class" data-id="p1">
                <div class="product-info">
                    <h3>Product 1</h3>
                    <p class="new-description">Description 1</p>
                </div>
            </article>
            <article class="product new-class" data-id="p2">
                <div class="product-info">
                    <h3>Product 2</h3>
                    <p class="new-description">Description 2</p>
                </div>
            </article>
        </section>
    </div>
</div>
```
The selector will no longer function and your code needs maintenance. That's where Scrapling's auto-matching feature comes into play.

```python
from scrapling import Adaptor
# Before the change
page = Adaptor(page_source, url='example.com')
element = page.css('#p1' auto_save=True)
if not element:  # One day website changes?
    element = page.css('#p1', auto_match=True)  # Scrapling still finds it!
# the rest of the code...
```
> How does the auto-matching work? Check the [FAQs](#-enlightening-questions-and-faqs) section for that and other possible issues while auto-matching.

#### Real-World Scenario
Let's use a real website as an example and use one of the fetchers to fetch its source. To do this we need to find a website that will change its design/structure soon, take a copy of its source then wait for the website to make the change. Of course, that's nearly impossible to know unless I know the website's owner but that will make it a staged test haha.

To solve this issue, I will use [The Web Archive](https://archive.org/)'s [Wayback Machine](https://web.archive.org/). Here is a copy of [StackOverFlow's website in 2010](https://web.archive.org/web/20100102003420/http://stackoverflow.com/), pretty old huh?</br>Let's test if the automatch feature can extract the same button in the old design from 2010 and the current design using the same selector :)

If I want to extract the Questions button from the old design I can use a selector like this `#hmenus > div:nth-child(1) > ul > li:nth-child(1) > a` This selector is too specific because it was generated by Google Chrome.
Now let's test the same selector in both versions
```python
>> from scrapling import Fetcher
>> selector = '#hmenus > div:nth-child(1) > ul > li:nth-child(1) > a'
>> old_url = "https://web.archive.org/web/20100102003420/http://stackoverflow.com/"
>> new_url = "https://stackoverflow.com/"
>> 
>> page = Fetcher(automatch_domain='stackoverflow.com').get(old_url, timeout=30)
>> element1 = page.css_first(selector, auto_save=True)
>> 
>> # Same selector but used in the updated website
>> page = Fetcher(automatch_domain="stackoverflow.com").get(new_url)
>> element2 = page.css_first(selector, auto_match=True)
>> 
>> if element1.text == element2.text:
...    print('Scrapling found the same element in the old design and the new design!')
'Scrapling found the same element in the old design and the new design!'
```
Note that I used a new argument called `automatch_domain`, this is because for Scrapling these are two different URLs, not the website so it isolates their data. To tell Scrapling they are the same website, we then pass the domain we want to use for saving auto-match data for them both so Scrapling doesn't isolate them.

In a real-world scenario, the code will be the same except it will use the same URL for both requests so you won't need to use the `automatch_domain` argument. This is the closest example I can give to real-world cases so I hope it didn't confuse you :)

**Notes:**
1. For the two examples above I used one time the `Adaptor` class and the second time the `Fetcher` class just to show you that you can create the `Adaptor` object by yourself if you have the source or fetch the source using any `Fetcher` class then it will create the `Adaptor` object for you.
2. Passing the `auto_save` argument with the `auto_match` argument set to `False` while initializing the Adaptor/Fetcher object will only result in ignoring the `auto_save` argument value and the following warning message
    ```text
    Argument `auto_save` will be ignored because `auto_match` wasn't enabled on initialization. Check docs for more info.
    ```
    This behavior is purely for performance reasons so the database gets created/connected only when you are planning to use the auto-matching features. Same case with the `auto_match` argument.

3. The `auto_match` parameter works only for `Adaptor` instances not `Adaptors` so if you do something like this you will get an error
    ```python
    page.css('body').css('#p1', auto_match=True)
    ```
    because you can't auto-match a whole list, you have to be specific and do something like
    ```python
    page.css_first('body').css('#p1', auto_match=True)
    ```

### Find elements by filters
Inspired by BeautifulSoup's `find_all` function you can find elements by using `find_all`/`find` methods. Both methods can take multiple types of filters and return all elements in the pages that all these filters apply to.

* To be more specific:
  * Any string passed is considered a tag name 
  * Any iterable passed like List/Tuple/Set is considered an iterable of tag names.
  * Any dictionary is considered a mapping of HTML element(s) attribute names and attribute values.
  * Any regex patterns passed are used as filters
  * Any functions passed are used as filters
  * Any keyword argument passed is considered as an HTML element attribute with its value.

So the way it works is after collecting all passed arguments and keywords, each filter passes its results to the following filter in a waterfall-like filtering system.
<br/>It filters all elements in the current page/element in the following order:

1. All elements with the passed tag name(s).
2. All elements that match all passed attribute(s).
3. All elements that match all passed regex patterns.
4. All elements that fulfill all passed function(s).

Note: The filtering process always starts from the first filter it finds in the filtering order above so if no tag name(s) are passed but attributes are passed, the process starts from that layer and so on. **But the order in which you pass the arguments doesn't matter.**

Examples to clear any confusion :)

```python
>> from scrapling import Fetcher
>> page = Fetcher().get('https://quotes.toscrape.com/')
# Find all elements with tag name `div`.
>> page.find_all('div')
[<data='<div class="container"> <div class="row...' parent='<body> <div class="container"> <div clas...'>,
 <data='<div class="row header-box"> <div class=...' parent='<div class="container"> <div class="row...'>,
...]

# Find all div elements with a class that equals `quote`.
>> page.find_all('div', class_='quote')
[<data='<div class="quote" itemscope itemtype="h...' parent='<div class="col-md-8"> <div class="quote...'>,
 <data='<div class="quote" itemscope itemtype="h...' parent='<div class="col-md-8"> <div class="quote...'>,
...]

# Same as above.
>> page.find_all('div', {'class': 'quote'})
[<data='<div class="quote" itemscope itemtype="h...' parent='<div class="col-md-8"> <div class="quote...'>,
 <data='<div class="quote" itemscope itemtype="h...' parent='<div class="col-md-8"> <div class="quote...'>,
...]

# Find all elements with a class that equals `quote`.
>> page.find_all({'class': 'quote'})
[<data='<div class="quote" itemscope itemtype="h...' parent='<div class="col-md-8"> <div class="quote...'>,
 <data='<div class="quote" itemscope itemtype="h...' parent='<div class="col-md-8"> <div class="quote...'>,
...]

# Find all div elements with a class that equals `quote`, and contains the element `.text` which contains the word 'world' in its content.
>> page.find_all('div', {'class': 'quote'}, lambda e: "world" in e.css_first('.text::text'))
[<data='<div class="quote" itemscope itemtype="h...' parent='<div class="col-md-8"> <div class="quote...'>]

# Find all elements that don't have children.
>> page.find_all(lambda element: len(element.children) > 0)
[<data='<html lang="en"><head><meta charset="UTF...'>,
 <data='<head><meta charset="UTF-8"><title>Quote...' parent='<html lang="en"><head><meta charset="UTF...'>,
 <data='<body> <div class="container"> <div clas...' parent='<html lang="en"><head><meta charset="UTF...'>,
...]

# Find all elements that contain the word 'world' in its content.
>> page.find_all(lambda element: "world" in element.text)
[<data='<span class="text" itemprop="text">“The...' parent='<div class="quote" itemscope itemtype="h...'>,
 <data='<a class="tag" href="/tag/world/page/1/"...' parent='<div class="tags"> Tags: <meta class="ke...'>]

# Find all span elements that match the given regex
>> page.find_all('span', re.compile(r'world'))
[<data='<span class="text" itemprop="text">“The...' parent='<div class="quote" itemscope itemtype="h...'>]

# Find all div and span elements with class 'quote' (No span elements like that so only div returned)
>> page.find_all(['div', 'span'], {'class': 'quote'})
[<data='<div class="quote" itemscope itemtype="h...' parent='<div class="col-md-8"> <div class="quote...'>,
 <data='<div class="quote" itemscope itemtype="h...' parent='<div class="col-md-8"> <div class="quote...'>,
...]

# Mix things up
>> page.find_all({'itemtype':"http://schema.org/CreativeWork"}, 'div').css('.author::text')
['Albert Einstein',
 'J.K. Rowling',
...]
```

### Is That All?
Here's what else you can do with Scrapling:

- Accessing the `lxml.etree` object itself of any element directly
    ```python
    >>> quote._root
    <Element div at 0x107f98870>
    ```
- Saving and retrieving elements manually to auto-match them outside the `css` and the `xpath` methods but you have to set the identifier by yourself.

  - To save an element to the database:
    ```python
    >>> element = page.find_by_text('Tipping the Velvet', first_match=True)
    >>> page.save(element, 'my_special_element')
    ```
  - Now later when you want to retrieve it and relocate it inside the page with auto-matching, it would be like this
    ```python
    >>> element_dict = page.retrieve('my_special_element')
    >>> page.relocate(element_dict, adaptor_type=True)
    [<data='<a href="catalogue/tipping-the-velvet_99...' parent='<h3><a href="catalogue/tipping-the-velve...'>]
    >>> page.relocate(element_dict, adaptor_type=True).css('::text')
    ['Tipping the Velvet']
    ```
  - if you want to keep it as `lxml.etree` object, leave the `adaptor_type` argument
    ```python
    >>> page.relocate(element_dict)
    [<Element a at 0x105a2a7b0>]
    ```

- Filtering results based on a function
```python
# Find all products over $50
expensive_products = page.css('.product_pod').filter(
    lambda p: float(p.css('.price_color').re_first(r'[\d\.]+')) > 50
)
```

- Searching results for the first one that matches a function
```python
# Find all the products with price '53.23'
page.css('.product_pod').search(
    lambda p: float(p.css('.price_color').re_first(r'[\d\.]+')) == 54.23
)
```

- Doing operations on element content is the same as scrapy
    ```python
    quote.re(r'regex_pattern')  # Get all strings (TextHandlers) that match the regex pattern
    quote.re_first(r'regex_pattern')  # Get the first string (TextHandler) only
    quote.json()  # If the content text is jsonable, then convert it to json using `orjson` which is 10x faster than the standard json library and provides more options
    ```
    except that you can do more with them like
    ```python
    quote.re(
        r'regex_pattern',
        replace_entities=True,  # Character entity references are replaced by their corresponding character
        clean_match=True,       # This will ignore all whitespaces and consecutive spaces while matching
        case_sensitive= False,  # Set the regex to ignore letters case while compiling it
    )
    ```
    Hence all of these methods are methods from the `TextHandler` within that contains the text content so the same can be done directly if you call the `.text` property or equivalent selector function.


- Doing operations on the text content itself includes
  - Cleaning the text from any white spaces and replacing consecutive spaces with single space
    ```python
    quote.clean()
    ```
  - You already know about the regex matching and the fast json parsing but did you know that all strings returned from the regex search are actually `TextHandler` objects too? so in cases where you have for example a JS object assigned to a JS variable inside JS code and want to extract it with regex and then convert it to json object, in other libraries, these would be more than 1 line of code but here you can do it in 1 line like this
    ```python
    page.xpath('//script/text()').re_first(r'var dataLayer = (.+);').json()
    ```
  - Sort all characters in the string as if it were a list and return the new string
    ```python
    quote.sort(reverse=False)
    ```
  > To be clear, `TextHandler` is a sub-class of Python's `str` so all normal operations/methods that work with Python strings will work with it.

- Any element's attributes are not exactly a dictionary but a sub-class of [mapping](https://docs.python.org/3/glossary.html#term-mapping) called `AttributesHandler` that's read-only so it's faster and string values returned are actually `TextHandler` objects so all operations above can be done on them, standard dictionary operations that don't modify the data, and more :)
  - Unlike standard dictionaries, here you can search by values too and can do partial searches. It might be handy in some cases (returns a generator of matches)
    ```python
    >>> for item in element.attrib.search_values('catalogue', partial=True):
            print(item)
    {'href': 'catalogue/tipping-the-velvet_999/index.html'}
    ```
  - Serialize the current attributes to JSON bytes:
    ```python
    >>> element.attrib.json_string
    b'{"href":"catalogue/tipping-the-velvet_999/index.html","title":"Tipping the Velvet"}'
    ```
  - Converting it to a normal dictionary
    ```python
    >>> dict(element.attrib)
    {'href': 'catalogue/tipping-the-velvet_999/index.html',
    'title': 'Tipping the Velvet'}
    ```

Scrapling is under active development so expect many more features coming soon :)

## More Advanced Usage

There are a lot of deep details skipped here to make this as short as possible so to take a deep dive, head to the [docs](https://github.com/D4Vinci/Scrapling/tree/main/docs) section. I will try to keep it updated as possible and add complex examples. There I will explain points like how to write your storage system, write spiders that don't depend on selectors at all, and more...

Note that implementing your storage system can be complex as there are some strict rules such as inheriting from the same abstract class, following the singleton design pattern used in other classes, and more. So make sure to read the docs first.

> [!IMPORTANT] 
> A website is needed to provide detailed library documentation.<br/> 
> I'm trying to rush creating the website, researching new ideas, and adding more features/tests/benchmarks but time is tight with too many spinning plates between work, personal life, and working on Scrapling. I have been working on Scrapling for months for free after all.<br/><br/>
> If you like `Scrapling` and want it to keep improving then this is a friendly reminder that you can help by supporting me through the [sponsor button](https://github.com/sponsors/D4Vinci).

## ⚡ Enlightening Questions and FAQs
This section addresses common questions about Scrapling, please read this section before opening an issue.

### How does auto-matching work?
  1. You need to get a working selector and run it at least once with methods `css` or `xpath` with the `auto_save` parameter set to `True` before structural changes happen.
  2. Before returning results for you, Scrapling uses its configured database and saves unique properties about that element.
  3. Now because everything about the element can be changed or removed, nothing from the element can be used as a unique identifier for the database. To solve this issue, I made the storage system rely on two things:
     1. The domain of the URL you gave while initializing the first Adaptor object
     2. The `identifier` parameter you passed to the method while selecting. If you didn't pass one, then the selector string itself will be used as an identifier but remember you will have to use it as an identifier value later when the structure changes and you want to pass the new selector.

     Together both are used to retrieve the element's unique properties from the database later.
  4. Now later when you enable the `auto_match` parameter for both the Adaptor instance and the method call. The element properties are retrieved and Scrapling loops over all elements in the page and compares each one's unique properties to the unique properties we already have for this element and a score is calculated for each one.
  5. Comparing elements is not exact but more about finding how similar these values are, so everything is taken into consideration, even the values' order, like the order in which the element class names were written before and the order in which the same element class names are written now.
  6. The score for each element is stored in the table, and the element(s) with the highest combined similarity scores are returned.

### How does the auto-matching work if I didn't pass a URL while initializing the Adaptor object?
Not a big problem as it depends on your usage. The word `default` will be used in place of the URL field while saving the element's unique properties. So this will only be an issue if you used the same identifier later for a different website that you didn't pass the URL parameter while initializing it as well. The save process will overwrite the previous data and auto-matching uses the latest saved properties only.

### If all things about an element can change or get removed, what are the unique properties to be saved?
For each element, Scrapling will extract:
- Element tag name, text, attributes (names and values), siblings (tag names only), and path (tag names only).
- Element's parent tag name, attributes (names and values), and text.

### I have enabled the `auto_save`/`auto_match` parameter while selecting and it got completely ignored with a warning message
That's because passing the `auto_save`/`auto_match` argument without setting `auto_match` to `True` while initializing the Adaptor object will only result in ignoring the `auto_save`/`auto_match` argument value. This behavior is purely for performance reasons so the database gets created only when you are planning to use the auto-matching features.

### I have done everything as the docs but the auto-matching didn't return anything, what's wrong?
It could be one of these reasons:
1. No data were saved/stored for this element before.
2. The selector passed is not the one used while storing element data. The solution is simple
   - Pass the old selector again as an identifier to the method called.
   - Retrieve the element with the retrieve method using the old selector as identifier then save it again with the save method and the new selector as identifier.
   - Start using the identifier argument more often if you are planning to use every new selector from now on.
3. The website had some extreme structural changes like a new full design. If this happens a lot with this website, the solution would be to make your code as selector-free as possible using Scrapling features.

### Can Scrapling replace code built on top of BeautifulSoup4?
Pretty much yeah, almost all features you get from BeautifulSoup can be found or achieved in Scrapling one way or another. In fact, if you see there's a feature in bs4 that is missing in Scrapling, please make a feature request from the issues tab to let me know.

### Can Scrapling replace code built on top of AutoScraper?
Of course, you can find elements by text/regex, find similar elements in a more reliable way than AutoScraper, and finally save/retrieve elements manually to use later as the model feature in AutoScraper. I have pulled all top articles about AutoScraper from Google and tested Scrapling against examples in them. In all examples, Scrapling got the same results as AutoScraper in much less time.

### Is Scrapling thread-safe?
Yes, Scrapling instances are thread-safe. Each Adaptor instance maintains its state.

## More Sponsors!
<a href="https://serpapi.com/?utm_source=scrapling"><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/SerpApi.png" height="500" alt="SerpApi Banner" ></a>


## Contributing
Everybody is invited and welcome to contribute to Scrapling. There is a lot to do!

Please read the [contributing file](https://github.com/D4Vinci/Scrapling/blob/main/CONTRIBUTING.md) before doing anything.

## Disclaimer for Scrapling Project
> [!CAUTION]
> This library is provided for educational and research purposes only. By using this library, you agree to comply with local and international laws regarding data scraping and privacy. The authors and contributors are not responsible for any misuse of this software. This library should not be used to violate the rights of others, for unethical purposes, or to use data in an unauthorized or illegal manner. Do not use it on any website unless you have permission from the website owner or within their allowed rules like the `robots.txt` file, for example.

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
- In the auto-matching save process, the unique properties of the first element from the selection results are the only ones that get saved. So if the selector you are using selects different elements on the page that are in different locations, auto-matching will probably return to you the first element only when you relocate it later. This doesn't include combined CSS selectors (Using commas to combine more than one selector for example) as these selectors get separated and each selector gets executed alone.
- Currently, Scrapling is not compatible with async/await.

---
<div align="center"><small>Designed & crafted with ❤️ by Karim Shoair.</small></div><br>
