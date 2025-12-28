# Introduction

Here, we will discuss the `StealthyFetcher` class. This class is similar to [DynamicFetcher](dynamic.md#introduction) in many ways, including browser automation and the use of [Playwright's API](https://playwright.dev/python/docs/intro). The main difference is that this class provides advanced anti-bot protection bypass capabilities and a custom version of a modified Firefox browser called [Camoufox](https://github.com/daijro/camoufox), from which most stealth comes.

As with [DynamicFetcher](dynamic.md#introduction), you will need some knowledge about [Playwright's Page API](https://playwright.dev/python/docs/api/class-page) to automate the page, as we will explain later.

> 💡 **Prerequisites:**
> 
> 1. You’ve completed or read the [Fetchers basics](../fetching/choosing.md) page to understand what the [Response object](../fetching/choosing.md#response-object) is and which fetcher to use.
> 2. You’ve completed or read the [Querying elements](../parsing/selection.md) page to understand how to find/extract elements from the [Selector](../parsing/main_classes.md#selector)/[Response](../fetching/choosing.md#response-object) object.
> 3. You’ve completed or read the [Main classes](../parsing/main_classes.md) page to know what properties/methods the [Response](../fetching/choosing.md#response-object) class is inheriting from the [Selector](../parsing/main_classes.md#selector) class.

## Basic Usage
You have one primary way to import this Fetcher, which is the same for all fetchers.

```python
>>> from scrapling.fetchers import StealthyFetcher
```
Check out how to configure the parsing options [here](choosing.md#parser-configuration-in-all-fetchers)

> Note: The async version of the `fetch` method is the `async_fetch` method, of course.

## Full list of arguments
Scrapling provides many options with this fetcher and its session classes. Before jumping to the [examples](#examples), here's the full list of arguments


|      Argument       | Description                                                                                                                                                                                                                                                         | Optional |
|:-------------------:|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|:--------:|
|         url         | Target url                                                                                                                                                                                                                                                          |    ❌     |
|      headless       | Pass `True` to run the browser in headless/hidden (**default**) or `False` for headful/visible mode.                                                                                                                                                                |    ✔️    |
|    block_images     | Prevent the loading of images through Firefox preferences. _This can help save your proxy usage, but be cautious with this option, as it may cause some websites to never finish loading._                                                                          |    ✔️    |
|  disable_resources  | Drop requests for unnecessary resources for a speed boost. Requests dropped are of type `font`, `image`, `media`, `beacon`, `object`, `imageset`, `texttrack`, `websocket`, `csp_report`, and `stylesheet`.                                                         |    ✔️    |
|       cookies       | Set cookies for the next request.                                                                                                                                                                                                                                   |    ✔️    |
|    google_search    | Enabled by default, Scrapling will set the referer header as if this request came from a Google search of this website's domain name.                                                                                                                               |    ✔️    |
|    extra_headers    | A dictionary of extra headers to add to the request. _The referer set by the `google_search` argument takes priority over the referer set here if used together._                                                                                                   |    ✔️    |
|    block_webrtc     | Blocks WebRTC entirely.                                                                                                                                                                                                                                             |    ✔️    |
|     page_action     | Added for automation. Pass a function that takes the `page` object and does the necessary automation.                                                                                                                                                               |    ✔️    |
|       addons        | List of Firefox addons to use. **Must be paths to extracted addons.**                                                                                                                                                                                               |    ✔️    |
|      humanize       | Humanize the cursor movement. The cursor movement takes either True or the maximum duration in seconds. The cursor typically takes up to 1.5 seconds to move across the window.                                                                                     |    ✔️    |
|     allow_webgl     | Enabled by default. Disabling WebGL is not recommended, as many WAFs now check if WebGL is enabled.                                                                                                                                                                 |    ✔️    |
|        geoip        | Recommended to use with proxies; Automatically use IPs' longitude, latitude, timezone, country, locale, & spoof the WebRTC IP address. It will also calculate and spoof the browser's language based on the distribution of language speakers in the target region. |    ✔️    |
|    os_randomize     | If enabled, Scrapling will randomize the OS fingerprints used. The default is matching the fingerprints with the current OS.                                                                                                                                        |    ✔️    |
|     disable_ads     | Disabled by default; this installs the `uBlock Origin` addon on the browser if enabled.                                                                                                                                                                             |    ✔️    |
|  solve_cloudflare   | When enabled, fetcher solves all types of Cloudflare's Turnstile/Interstitial challenges before returning the response to you.                                                                                                                                      |    ✔️    |
|    network_idle     | Wait for the page until there are no network connections for at least 500 ms.                                                                                                                                                                                       |    ✔️    |
|      load_dom       | Enabled by default, wait for all JavaScript on page(s) to fully load and execute (wait for the `domcontentloaded` state).                                                                                                                                           |    ✔️    |
|       timeout       | The timeout used in all operations and waits through the page. It's in milliseconds, and the default is 30000.                                                                                                                                                      |    ✔️    |
|        wait         | The time (milliseconds) the fetcher will wait after everything finishes before closing the page and returning the `Response` object.                                                                                                                                |    ✔️    |
|    wait_selector    | Wait for a specific css selector to be in a specific state.                                                                                                                                                                                                         |    ✔️    |
|     init_script     | An absolute path to a JavaScript file to be executed on page creation for all pages in this session.                                                                                                                                                                |    ✔️    |
| wait_selector_state | Scrapling will wait for the given state to be fulfilled for the selector given with `wait_selector`. _Default state is `attached`._                                                                                                                                 |    ✔️    |
|        proxy        | The proxy to be used with requests. It can be a string or a dictionary with only the keys 'server', 'username', and 'password'.                                                                                                                                     |    ✔️    |
|    user_data_dir    | Path to a User Data Directory, which stores browser session data like cookies and local storage. The default is to create a temporary directory. **Only Works with sessions**                                                                                       |    ✔️    |
|   additional_args   | Additional arguments to be passed to Camoufox as additional settings, and they take higher priority than Scrapling's settings.                                                                                                                                      |    ✔️    |
|   selector_config   | A dictionary of custom parsing arguments to be used when creating the final `Selector`/`Response` class.                                                                                                                                                            |    ✔️    |

In session classes, all these arguments can be set globally for the session. Still, you can configure each request individually by passing some of the arguments here that can be configured on the browser tab level like: `google_search`, `timeout`, `wait`, `page_action`, `extra_headers`, `disable_resources`, `wait_selector`, `wait_selector_state`, `network_idle`, `load_dom`, `solve_cloudflare`, and `selector_config`.

## Examples
It's easier to understand with examples, so we will now review most of the arguments individually.

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

The `solve_cloudflare` parameter enables automatic detection and solving all types of Cloudflare's Turnstile/Interstitial challenges:

- JavaScript challenges (managed)
- Interactive challenges (clicking verification boxes)
- Invisible challenges (automatic background verification)

And even solves the custom pages.

**Important notes:**

- Sometimes, with websites that use custom implementations, you will need to use `wait_selector` to make sure Scrapling waits for the real website content to be loaded after solving the captcha. Some websites can be the real definition of an edge case while we are trying to make the solver as generic as possible.
- When `solve_cloudflare=True` is enabled, `humanize=True` is automatically activated for more realistic behavior
- The timeout should be at least 60 seconds when using the Cloudflare solver for sufficient challenge-solving time
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

The `google_search` argument is enabled by default, making the request appear to come from a Google search page. So, a request for `https://example.com` will set the referer to `https://www.google.com/search?q=example`. Also, if used together, it takes priority over the referer set by the `extra_headers` argument.

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

### Downloading Files

```python
page = StealthyFetcher.fetch('https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/poster.png')

with open(file='poster.png', mode='wb') as f:
    f.write(page.body)
```

The `body` attribute of the `Response` object is a `bytes` object containing the response body in case of Non-HTML responses.

### Browser Automation
This is where your knowledge about [Playwright's Page API](https://playwright.dev/python/docs/api/class-page) comes into play. The function you pass here takes the page object from Playwright's API, performs the desired action, and then the fetcher continues.

This function is executed immediately after waiting for `network_idle` (if enabled) and before waiting for the `wait_selector` argument, allowing it to be used for purposes beyond automation. You can alter the page as you want.

In the example below, I used the pages' [mouse events](https://playwright.dev/python/docs/api/class-mouse) to scroll the page with the mouse wheel, then move the mouse.
```python
from playwright.sync_api import Page

def scroll_page(page: Page):
    page.mouse.wheel(10, 0)
    page.mouse.move(100, 400)
    page.mouse.up()

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

After that, if `load_dom` is enabled (the default), the fetcher will check again to see if all JavaScript files are loaded and executed (in the `domcontentloaded` state) or continue waiting. If you have enabled `network_idle`, the fetcher will wait for `network_idle` to be fulfilled again, as explained above.

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
The paths here must point to extracted addons that will be installed automatically upon browser launch.

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

You may have noticed the `max_pages` argument. This is a new argument that enables the fetcher to create a **rotating pool of Browser tabs**. Instead of using a single tab for all your requests, you set a limit on the maximum number of pages. With each request, the library will close all tabs that have finished their task and check if the number of the current tabs is lower than the maximum allowed number of pages/tabs, then:

1. If you are within the allowed range, the fetcher will create a new tab for you, and then all is as normal.
2. Otherwise, it will keep checking every subsecond if creating a new tab is allowed or not for 60 seconds, then raise `TimeoutError`. This can happen when the website you are fetching becomes unresponsive.

This logic allows for multiple websites to be fetched at the same time in the same browser, which saves a lot of resources, but most importantly, is so fast :)

In versions 0.3 and 0.3.1, the pool was reusing finished tabs to save more resources/time. That logic proved flawed, as it's nearly impossible to protect pages/tabs from contamination by the previous configuration used in the request before this one.

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