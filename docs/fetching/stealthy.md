# Introduction

Here, we will discuss the `StealthyFetcher` class. This class is similar to [PlayWrightFetcher](dynamic.md#introduction) in many ways, like browser automation and using [PlayWright](https://playwright.dev/python/docs/intro) as an engine for fetching websites. The main difference is that this class provides advanced anti-bot protection bypass capabilities and a modified Firefox browser called [Camoufox](https://github.com/daijro/camoufox), from which most stealth comes.

As with [PlayWrightFetcher](dynamic.md#introduction), you will need some knowledge about [PlayWright's Page API](https://playwright.dev/python/docs/api/class-page) to automate the page, as we will explain later.

## Basic Usage
You have one primary way to import this Fetcher, which is the same for all fetchers.

```python
>>> from scrapling.fetchers import StealthyFetcher
```
Check out how to configure the parsing options [here](choosing.md#parser-configuration-in-all-fetchers)

> Notes: 
> 
> 1. Every time you fetch a website with this fetcher, it waits by default for all JavaScript to fully load and execute, so you don't have to (waits for the `domcontentloaded` state).
> 2. Of course, the async version of the `fetch` method is the `async_fetch` method.

## Full list of arguments
Before jumping to [examples](#examples), here's the full list of arguments


|       Argument       | Description                                                                                                                                                                                                                                                                                                                                                                                                       | Optional |
|:--------------------:|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|:--------:|
|         url          | Target url                                                                                                                                                                                                                                                                                                                                                                                                        |    ❌     |
|       headless       | Pass `True` to run the browser in headless/hidden (**default**), `virtual` to run it in virtual screen mode, or `False` for headful/visible mode. The `virtual` mode requires having `xvfb` installed.                                                                                                                                                                                                            |    ✔️    |
|     block_images     | Prevent the loading of images through Firefox preferences. _This can help save your proxy usage, but be careful with this option as it makes some websites never finish loading._                                                                                                                                                                                                                                 |    ✔️    |
|  disable_resources   | Drop requests of unnecessary resources for a speed boost. It depends, but it made requests ~25% faster in my tests for some websites.<br/>Requests dropped are of type `font`, `image`, `media`, `beacon`, `object`, `imageset`, `texttrack`, `websocket`, `csp_report`, and `stylesheet`. _This can help save your proxy usage, but be careful with this option as it makes some websites never finish loading._ |    ✔️    |
|    google_search     | Enabled by default, Scrapling will set the referer header as if this request came from a Google search for this website's domain name.                                                                                                                                                                                                                                                                            |    ✔️    |
|    extra_headers     | A dictionary of extra headers to add to the request. _The referer set by the `google_search` argument takes priority over the referer set here if used together._                                                                                                                                                                                                                                                 |    ✔️    |
|     block_webrtc     | Blocks WebRTC entirely.                                                                                                                                                                                                                                                                                                                                                                                           |    ✔️    |
|     page_action      | Added for automation. A function that takes the `page` object and does the automation you need, then returns `page` again.                                                                                                                                                                                                                                                                                        |    ✔️    |
|        addons        | List of Firefox addons to use. **Must be paths to extracted addons.**                                                                                                                                                                                                                                                                                                                                             |    ✔️    |
|       humanize       | Humanize the cursor movement. The cursor movement takes either True or the MAX duration in seconds. The cursor typically takes up to 1.5 seconds to move across the window.                                                                                                                                                                                                                                       |    ✔️    |
|     allow_webgl      | Enabled by default. Disabling WebGL is not recommended, as many WAFs now check if WebGL is enabled.                                                                                                                                                                                                                                                                                                               |    ✔️    |
|        geoip         | Recommended to use with proxies; Automatically use IP's longitude, latitude, timezone, country, locale, & spoof the WebRTC IP address. It will also calculate and spoof the browser's language based on the distribution of language speakers in the target region.                                                                                                                                               |    ✔️    |
|     os_randomize     | If enabled, Scrapling will randomize the OS fingerprints used. The default is matching the fingerprints with the current OS.                                                                                                                                                                                                                                                                                      |    ✔️    |
|     disable_ads      | Disabled by default; this installs the `uBlock Origin` addon on the browser if enabled.                                                                                                                                                                                                                                                                                                                           |    ✔️    |
|     network_idle     | Wait for the page until there are no network connections for at least 500 ms.                                                                                                                                                                                                                                                                                                                                     |    ✔️    |
|       timeout        | The timeout used in all operations and waits through the page. It's in milliseconds, and the default is 30000.                                                                                                                                                                                                                                                                                                    |    ✔️    |
|         wait         | The time (milliseconds) the fetcher will wait after everything finishes before closing the page and returning the `Response` object.                                                                                                                                                                                                                                                                              |    ✔️    |
|    wait_selector     | Wait for a specific css selector to be in a specific state.                                                                                                                                                                                                                                                                                                                                                       |    ✔️    |
| wait_selector_state  | Scrapling will wait for the given state to be fulfilled for the selector given with `wait_selector`. _Default state is `attached`._                                                                                                                                                                                                                                                                               |    ✔️    |
|        proxy         | The proxy to be used with requests. It can be a string or a dictionary with the keys 'server', 'username', and 'password' only.                                                                                                                                                                                                                                                                                   |    ✔️    |
| additional_arguments | Arguments passed to Camoufox as additional settings that take higher priority than Scrapling's.                                                                                                                                                                                                                                                                                                                   |    ✔️    |


## Examples
It's easier to understand with examples, so now we will go over most of the arguments individually with examples.

### Browser Modes

```python
# Headless/hidden mode (default)
page = StealthyFetcher.fetch('https://example.com', headless=True)

# Virtual display mode (requires having `xvfb` installed)
page = StealthyFetcher.fetch('https://example.com', headless='virtual')

# Visible browser mode
page = StealthyFetcher.fetch('https://example.com', headless=False)
```

### Resource Control

```python
# Block images
page = StealthyFetcher.fetch('https://example.com', block_images=True)

# Disable unnecessary resources
page = StealthyFetcher.fetch('https://example.com', disable_resources=True)  # Blocks fonts, images, media, etc.
```

### Additional stealth options

```python
page = StealthyFetcher.fetch(
   'https://example.com',
   block_webrtc=True,  # Block WebRTC
   allow_webgl=False,  # Disable WebGL
   humanize=True,      # Make the mouse move as how a human would move it
   geoip=True,         # Use IP's longitude, latitude, timezone, country, and locale, then spoof the WebRTC IP address...
   os_randomize=True,  # Randomize the OS fingerprints used. The default is matching the fingerprints with the current OS.
   disable_ads=True,   # Block ads with uBlock Origin addon (enabled by default)
   google_search=True
)

# Custom humanization duration
page = StealthyFetcher.fetch(
    'https://example.com',
    humanize=1.5  # Max 1.5 seconds for cursor movement
)
```

The `google_search` argument is enabled by default. It makes the request as if it came from Google, so for a request for `https://example.com`, it will set the referer to `https://www.google.com/search?q=example`. Also, if used together, it takes priority over the referer set by the `extra_headers` argument.

### Network Control

```python
# Wait for network idle (Consider fetch to be finished when there are no network connections for at least 500 ms)
page = StealthyFetcher.fetch('https://example.com', network_idle=True)

# Custom timeout (in milliseconds)
page = StealthyFetcher.fetch('https://example.com', timeout=30000)  # 30 seconds

# Proxy support
page = StealthyFetcher.fetch(
    'https://example.com',
    proxy='http://username:password@host:port' # Or it can be a dictionary with the keys 'server', 'username', and 'password' only
)
```

### Browser Automation
This is where your knowledge about [PlayWright's Page API](https://playwright.dev/python/docs/api/class-page) comes into play. The function you pass here takes the page object from Playwright's API, does what you want, and then returns it again for the current fetcher to continue working on it.

This function is executed right after waiting for `network_idle` (if enabled) and before waiting for the `wait_selector` argument, so it can be used for many things, not just automation. You can alter the page as you want.

In the example below, I used page [mouse events](https://playwright.dev/python/docs/api/class-mouse) to move the mouse wheel to scroll the page and then move the mouse.
```python
from playwright.sync_api import Page

def scroll_page(page: Page):
    page.mouse.wheel(10, 0)
    page.mouse.move(100, 400)
    page.mouse.up()
    return page

page = StealthyFetcher.fetch(
    'https://example.com',
    page_action=scroll_page
)
```
Of course, if you use the async fetch version, the function must also be async.
```python
from playwright.async_api import Page

async def scroll_page(page: Page):
   await page.mouse.wheel(10, 0)
   await page.mouse.move(100, 400)
   await page.mouse.up()
   return page

page = await StealthyFetcher.async_fetch(
    'https://example.com',
    page_action=scroll_page
)
```

### Wait Conditions
```python
# Wait for the selector
page = StealthyFetcher.fetch(
    'https://example.com',
    wait_selector='h1',
    wait_selector_state='visible'
)
```
This is the last wait the fetcher will do before returning the response (if enabled). You pass a CSS selector to the `wait_selector` argument, and the fetcher will wait for the state you passed in the `wait_selector_state` argument to be fulfilled. If you didn't pass a state, the default would be `attached`, which means it will wait for the element to be present in the DOM.

After that, the fetcher will check again to see if all JS files are loaded and executed (the `domcontentloaded` state) and wait for them to be. If you have enabled `network_idle` with this, the fetcher will wait for `network_idle` to be fulfilled again, as explained above.

The states the fetcher can wait for can be either ([source](https://playwright.dev/python/docs/api/class-page#page-wait-for-selector)):

- `attached`: wait for the element to be present in DOM.
- `detached`: wait for the element to not be present in DOM.
- `visible`: wait for the element to have a non-empty bounding box and no `visibility:hidden`. Note that an element without any content or with `display:none` has an empty bounding box and is not considered visible.
- `hidden`: Wait for the element to be detached from DOM, have an empty bounding box, or have `visibility:hidden`. This is opposite to the `'visible'` option.

### Firefox Addons

```python
# Custom Firefox addons
page = StealthyFetcher.fetch(
    'https://example.com',
    addons=['/path/to/addon1', '/path/to/addon2']
)
```
The paths here must be paths of extracted addons, which will be installed automatically upon browser launch.

### Real-world example (Amazon)
This is for educational purposes only; this example was generated by AI, which shows too how easy it is to work with Scrapling through AI
```python
def scrape_amazon_product(url):
    # Use StealthyFetcher to bypass protection
    page = StealthyFetcher.fetch(url)

    # Extract product details
    return {
        'title': page.css_first('#productTitle::text').clean(),
        'price': page.css_first('.a-price .a-offscreen::text'),
        'rating': page.css_first('[data-feature-name="averageCustomerReviews"] .a-popover-trigger .a-color-base::text'),
        'reviews_count': page.css('#acrCustomerReviewText::text').re_first(r'[\d,]+'),
        'features': [
            li.clean() for li in page.css('#feature-bullets li span::text')
        ],
        'availability': page.css_first('#availability').get_all_text(strip=True),
        'images': [
            img.attrib['src'] for img in page.css('#altImages img')
        ]
    }
```

## When to Use

Use StealthyFetcher when:

- Bypassing anti-bot protection
- Need a reliable browser fingerprint
- Full JavaScript support needed
- Want automatic stealth features
- Need browser automation