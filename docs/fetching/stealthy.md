# Introduction

Here, we will discuss the `StealthyFetcher` class. This class is similar to [DynamicFetcher](dynamic.md#introduction) in many ways, such as browser automation and utilizing [Playwright's API](https://playwright.dev/python/docs/intro). The main difference is that this class provides advanced anti-bot protection bypass capabilities and a custom version of a modified Firefox browser called [Camoufox](https://github.com/daijro/camoufox), from which most stealth comes.

As with [DynamicFetcher](dynamic.md#introduction), you will need some knowledge about [Playwright's Page API](https://playwright.dev/python/docs/api/class-page) to automate the page, as we will explain later.

## Basic Usage
You have one primary way to import this Fetcher, which is the same for all fetchers.

```python
>>> from scrapling.fetchers import StealthyFetcher
```
Check out how to configure the parsing options [here](choosing.md#parser-configuration-in-all-fetchers)

> Notes: 
> 
> 1. Every time you fetch a website with this fetcher, it waits by default for all JavaScript to fully load and execute, so you don't have to (wait for the `domcontentloaded` state).
> 2. Of course, the async version of the `fetch` method is the `async_fetch` method.

## Full list of arguments
Before jumping to [examples](#examples), here's the full list of arguments


|      Argument       | Description                                                                                                                                                                                                                                                                                                                                                                                                                | Optional |
|:-------------------:|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|:--------:|
|         url         | Target url                                                                                                                                                                                                                                                                                                                                                                                                                 |    ❌     |
|      headless       | Pass `True` to run the browser in headless/hidden (**default**) or `False` for headful/visible mode.                                                                                                                                                                                                                                                                                                                       |    ✔️    |
|    block_images     | Prevent the loading of images through Firefox preferences. _This can help save your proxy usage, but be cautious with this option, as it may cause some websites to never finish loading._                                                                                                                                                                                                                                 |    ✔️    |
|  disable_resources  | Drop requests of unnecessary resources for a speed boost. It depends, but it made requests ~25% faster in my tests for some websites.<br/>Requests dropped are of type `font`, `image`, `media`, `beacon`, `object`, `imageset`, `texttrack`, `websocket`, `csp_report`, and `stylesheet`. _This can help save your proxy usage, but be cautious with this option, as it may cause some websites to never finish loading._ |    ✔️    |
|       cookies       | Set cookies for the next request.                                                                                                                                                                                                                                                                                                                                                                                          |    ✔️    |
|    google_search    | Enabled by default, Scrapling will set the referer header as if this request came from a Google search of this website's domain name.                                                                                                                                                                                                                                                                                      |    ✔️    |
|    extra_headers    | A dictionary of extra headers to add to the request. _The referer set by the `google_search` argument takes priority over the referer set here if used together._                                                                                                                                                                                                                                                          |    ✔️    |
|    block_webrtc     | Blocks WebRTC entirely.                                                                                                                                                                                                                                                                                                                                                                                                    |    ✔️    |
|     page_action     | Added for automation. Pass a function that takes the `page` object and does the necessary automation, then returns `page` again.                                                                                                                                                                                                                                                                                           |    ✔️    |
|       addons        | List of Firefox addons to use. **Must be paths to extracted addons.**                                                                                                                                                                                                                                                                                                                                                      |    ✔️    |
|      humanize       | Humanize the cursor movement. The cursor movement takes either True or the maximum duration in seconds. The cursor typically takes up to 1.5 seconds to move across the window.                                                                                                                                                                                                                                                |    ✔️    |
|     allow_webgl     | Enabled by default. Disabling WebGL is not recommended, as many WAFs now check if WebGL is enabled.                                                                                                                                                                                                                                                                                                                        |    ✔️    |
|        geoip        | Recommended to use with proxies; Automatically use IP's longitude, latitude, timezone, country, locale, & spoof the WebRTC IP address. It will also calculate and spoof the browser's language based on the distribution of language speakers in the target region.                                                                                                                                                        |    ✔️    |
|    os_randomize     | If enabled, Scrapling will randomize the OS fingerprints used. The default is matching the fingerprints with the current OS.                                                                                                                                                                                                                                                                                               |    ✔️    |
|     disable_ads     | Disabled by default; this installs the `uBlock Origin` addon on the browser if enabled.                                                                                                                                                                                                                                                                                                                                    |    ✔️    |
|  solve_cloudflare   | When enabled, fetcher solves all three types of Cloudflare's Turnstile wait/captcha page before returning the response to you.                                                                                                                                                                                                                                                                                         |    ✔️    |
|    network_idle     | Wait for the page until there are no network connections for at least 500 ms.                                                                                                                                                                                                                                                                                                                                              |    ✔️    |
|       timeout       | The timeout used in all operations and waits through the page. It's in milliseconds, and the default is 30000.                                                                                                                                                                                                                                                                                                             |    ✔️    |
|        wait         | The time (milliseconds) the fetcher will wait after everything finishes before closing the page and returning the `Response` object.                                                                                                                                                                                                                                                                                       |    ✔️    |
|    wait_selector    | Wait for a specific css selector to be in a specific state.                                                                                                                                                                                                                                                                                                                                                                |    ✔️    |
| wait_selector_state | Scrapling will wait for the given state to be fulfilled for the selector given with `wait_selector`. _Default state is `attached`._                                                                                                                                                                                                                                                                                        |    ✔️    |
|        proxy        | The proxy to be used with requests. It can be a string or a dictionary with the keys 'server', 'username', and 'password' only.                                                                                                                                                                                                                                                                                            |    ✔️    |
|   additional_args   | Additional arguments to be passed to Camoufox as additional settings, and they take higher priority than Scrapling's settings.                                                                                                                                                                                                                                                                                              |    ✔️    |
|   selector_config   | A dictionary of custom parsing arguments to be used when creating the final `Selector`/`Response` class.                                                                                                                                                                                                                                                                                                                   |    ✔️    |


## Examples
It's easier to understand with examples, so we will now review most of the arguments individually with examples.

### Browser Modes

```python
# Headless/hidden mode (default)
page = StealthyFetcher.fetch('https://example.com', headless=True)

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

### Cloudflare Protection Bypass

```python
# Automatic Cloudflare solver
page = StealthyFetcher.fetch(
    'https://nopecha.com/demo/cloudflare',
    solve_cloudflare=True  # Automatically solve Cloudflare challenges
)

# Works with other stealth options
page = StealthyFetcher.fetch(
    'https://protected-site.com',
    solve_cloudflare=True,
    humanize=True,
    geoip=True,
    os_randomize=True
)
```

The `solve_cloudflare` parameter enables automatic detection and solving all three types of Cloudflare's Turnstile challenges:

- JavaScript challenges (managed)
- Interactive challenges (clicking verification boxes)
- Invisible challenges (automatic background verification)

**Important notes:**

- When `solve_cloudflare=True` is enabled, `humanize=True` is automatically activated for more realistic behavior
- The timeout should be at least 60 seconds when using Cloudflare solver for sufficient challenge-solving time
- This feature works seamlessly with proxies and other stealth options

### Additional stealth options

```python
page = StealthyFetcher.fetch(
   'https://example.com',
   block_webrtc=True,  # Block WebRTC
   allow_webgl=False,  # Disable WebGL
   humanize=True,      # Make the mouse move as a human would move it
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

The `google_search` argument is enabled by default, making the request look as if it came from a Google search page. So, a request for `https://example.com` will set the referer to `https://www.google.com/search?q=example`. Also, if used together, it takes priority over the referer set by the `extra_headers` argument.

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
This is where your knowledge about [Playwright's Page API](https://playwright.dev/python/docs/api/class-page) comes into play. The function you pass here takes the page object from Playwright's API, performs the desired action, and then returns it for the current fetcher to continue processing.

This function is executed immediately after waiting for `network_idle` (if enabled) and before waiting for the `wait_selector` argument, allowing it to be used for various purposes, not just automation. You can alter the page as you want.

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

After that, the fetcher will check again to see if all JS files are loaded and executed (the `domcontentloaded` state) or continue waiting. If you have enabled `network_idle`, the fetcher will wait for `network_idle` to be fulfilled again, as explained above.

The states the fetcher can wait for can be any of the following ([source](https://playwright.dev/python/docs/api/class-page#page-wait-for-selector)):

- `attached`: Wait for an element to be present in the DOM.
- `detached`: Wait for an element to not be present in the DOM.
- `visible`: wait for an element to have a non-empty bounding box and no `visibility:hidden`. Note that an element without any content or with `display:none` has an empty bounding box and is not considered visible.
- `hidden`: wait for an element to be either detached from the DOM, or have an empty bounding box, or `visibility:hidden`. This is opposite to the `'visible'` option.

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
This is for educational purposes only; this example was generated by AI, which shows how easy it is to work with Scrapling through AI
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

## Session Management

To keep the browser open until you make multiple requests with the same configuration, use `StealthySession`/`AsyncStealthySession` classes. Those classes can accept all the arguments that the `fetch` function can take, which enables you to specify a config for the entire session.

```python
from scrapling.fetchers import StealthySession

# Create a session with default configuration
with StealthySession(
    headless=True,
    geoip=True,
    humanize=True,
    solve_cloudflare=True
) as session:
    # Make multiple requests with the same browser instance
    page1 = session.fetch('https://example1.com')
    page2 = session.fetch('https://example2.com') 
    page3 = session.fetch('https://nopecha.com/demo/cloudflare')
    
    # All requests reuse the same tab on the same browser instance
```

### Async Session Usage

```python
import asyncio
from scrapling.fetchers import AsyncStealthySession

async def scrape_multiple_sites():
    async with AsyncStealthySession(
        geoip=True,
        os_randomize=True,
        solve_cloudflare=True,
        timeout=60000,  # 60 seconds for Cloudflare challenges
        max_pages=3
    ) as session:
        # Make async requests with shared browser configuration
        pages = await asyncio.gather(
            session.fetch('https://site1.com'),
            session.fetch('https://site2.com'), 
            session.fetch('https://protected-site.com')
        )
        return pages
```

You may have noticed the `max_pages` argument. This is a new argument that enables the fetcher to create a **pool of Browser tabs** that will be rotated automatically. Instead of waiting for one browser tab to become ready, it checks if the next tab in the pool is ready to be used and uses it. This allows for multiple websites to be fetched at the same time in the same browser, which saves a lot of resources, but most importantly, is so fast :)

When all tabs inside the pool are busy, the fetcher checks every subsecond if a tab becomes ready. If none become free within a 30-second interval, it raises a `TimeoutError` error. This can happen when the website you are fetching becomes unresponsive for some reason.

### Session Benefits

- **Browser reuse**: Much faster subsequent requests by reusing the same browser instance.
- **Cookie persistence**: Automatic cookie and session state handling as any browser does automatically.
- **Consistent fingerprint**: Same browser fingerprint across all requests.
- **Memory efficiency**: Better resource usage compared to launching new browsers with each fetch.

## When to Use

Use StealthyFetcher when:

- Bypassing anti-bot protection
- Need a reliable browser fingerprint
- Full JavaScript support needed
- Want automatic stealth features
- Need browser automation
- Dealing with Cloudflare protection