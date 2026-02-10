# Introduction

Here, we will discuss the `StealthyFetcher` class. This class is very similar to the [DynamicFetcher](dynamic.md#introduction) class, including the browsers, the automation, and the use of [Playwright's API](https://playwright.dev/python/docs/intro). The main difference is that this class provides advanced anti-bot protection bypass capabilities; most of them are handled automatically under the hood, and the rest is up to you to enable.

As with [DynamicFetcher](dynamic.md#introduction), you will need some knowledge about [Playwright's Page API](https://playwright.dev/python/docs/api/class-page) to automate the page, as we will explain later.

!!! success "Prerequisites"

    1. You've completed or read the [DynamicFetcher](dynamic.md#introduction) page since this class builds upon it, and we won't repeat the same information here for that reason.
    2. You've completed or read the [Fetchers basics](../fetching/choosing.md) page to understand what the [Response object](../fetching/choosing.md#response-object) is and which fetcher to use.
    3. You've completed or read the [Querying elements](../parsing/selection.md) page to understand how to find/extract elements from the [Selector](../parsing/main_classes.md#selector)/[Response](../fetching/choosing.md#response-object) object.
    4. You've completed or read the [Main classes](../parsing/main_classes.md) page to know what properties/methods the [Response](../fetching/choosing.md#response-object) class is inheriting from the [Selector](../parsing/main_classes.md#selector) class.

## Basic Usage
You have one primary way to import this Fetcher, which is the same for all fetchers.

```python
>>> from scrapling.fetchers import StealthyFetcher
```
Check out how to configure the parsing options [here](choosing.md#parser-configuration-in-all-fetchers)

> Note: The async version of the `fetch` method is the `async_fetch` method, of course.

## What does it do?

The `StealthyFetcher` class is a stealthy version of the [DynamicFetcher](dynamic.md#introduction) class, and here are some of the things it does:

1. It easily bypasses all types of Cloudflare's Turnstile/Interstitial automatically. 
2. It bypasses CDP runtime leaks and WebRTC leaks.
3. It isolates JS execution, removes many Playwright fingerprints, and stops detection through some of the known behaviors that bots do.
4. It generates canvas noise to prevent fingerprinting through canvas.
5. It automatically patches known methods to detect running in headless mode and provides an option to defeat timezone mismatch attacks.
6. It makes requests look as if they came from Google's search page of the requested website.
7. and other anti-protection options...

## Full list of arguments
Scrapling provides many options with this fetcher and its session classes. Before jumping to the [examples](#examples), here's the full list of arguments


|      Argument       | Description                                                                                                                                                                                                                         | Optional |
|:-------------------:|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|:--------:|
|         url         | Target url                                                                                                                                                                                                                          |    ❌     |
|      headless       | Pass `True` to run the browser in headless/hidden (**default**) or `False` for headful/visible mode.                                                                                                                                |    ✔️    |
|  disable_resources  | Drop requests for unnecessary resources for a speed boost. Requests dropped are of type `font`, `image`, `media`, `beacon`, `object`, `imageset`, `texttrack`, `websocket`, `csp_report`, and `stylesheet`.                         |    ✔️    |
|       cookies       | Set cookies for the next request.                                                                                                                                                                                                   |    ✔️    |
|      useragent      | Pass a useragent string to be used. **Otherwise, the fetcher will generate and use a real Useragent of the same browser and version.**                                                                                              |    ✔️    |
|    network_idle     | Wait for the page until there are no network connections for at least 500 ms.                                                                                                                                                       |    ✔️    |
|      load_dom       | Enabled by default, wait for all JavaScript on page(s) to fully load and execute (wait for the `domcontentloaded` state).                                                                                                           |    ✔️    |
|       timeout       | The timeout (milliseconds) used in all operations and waits through the page. The default is 30,000 ms (30 seconds).                                                                                                                |    ✔️    |
|        wait         | The time (milliseconds) the fetcher will wait after everything finishes before closing the page and returning the `Response` object.                                                                                                |    ✔️    |
|     page_action     | Added for automation. Pass a function that takes the `page` object and does the necessary automation.                                                                                                                               |    ✔️    |
|    wait_selector    | Wait for a specific css selector to be in a specific state.                                                                                                                                                                         |    ✔️    |
|     init_script     | An absolute path to a JavaScript file to be executed on page creation for all pages in this session.                                                                                                                                |    ✔️    |
| wait_selector_state | Scrapling will wait for the given state to be fulfilled for the selector given with `wait_selector`. _Default state is `attached`._                                                                                                 |    ✔️    |
|    google_search    | Enabled by default, Scrapling will set the referer header as if this request came from a Google search of this website's domain name.                                                                                               |    ✔️    |
|    extra_headers    | A dictionary of extra headers to add to the request. _The referer set by the `google_search` argument takes priority over the referer set here if used together._                                                                   |    ✔️    |
|        proxy        | The proxy to be used with requests. It can be a string or a dictionary with only the keys 'server', 'username', and 'password'.                                                                                                     |    ✔️    |
|     real_chrome     | If you have a Chrome browser installed on your device, enable this, and the Fetcher will launch and use an instance of your browser.                                                                                                |    ✔️    |
|       locale        | Specify user locale, for example, `en-GB`, `de-DE`, etc. Locale will affect `navigator.language` value, `Accept-Language` request header value, as well as number and date formatting rules. Defaults to the system default locale. |    ✔️    |
|     timezone_id     | Changes the timezone of the browser. Defaults to the system timezone.                                                                                                                                                               |    ✔️    |
|       cdp_url       | Instead of launching a new browser instance, connect to this CDP URL to control real browsers through CDP.                                                                                                                          |    ✔️    |
|    user_data_dir    | Path to a User Data Directory, which stores browser session data like cookies and local storage. The default is to create a temporary directory. **Only Works with sessions**                                                       |    ✔️    |
|     extra_flags     | A list of additional browser flags to pass to the browser on launch.                                                                                                                                                                |    ✔️    |
|  solve_cloudflare   | When enabled, fetcher solves all types of Cloudflare's Turnstile/Interstitial challenges before returning the response to you.                                                                                                      |    ✔️    |
|    block_webrtc     | Forces WebRTC to respect proxy settings to prevent local IP address leak.                                                                                                                                                           |    ✔️    |
|     hide_canvas     | Add random noise to canvas operations to prevent fingerprinting.                                                                                                                                                                    |    ✔️    |
|     allow_webgl     | Enabled by default. Disabling it disables WebGL and WebGL 2.0 support entirely. Disabling WebGL is not recommended, as many WAFs now check if WebGL is enabled.                                                                     |    ✔️    |
|   additional_args   | Additional arguments to be passed to Playwright's context as additional settings, and they take higher priority than Scrapling's settings.                                                                                          |    ✔️    |
|   selector_config   | A dictionary of custom parsing arguments to be used when creating the final `Selector`/`Response` class.                                                                                                                            |    ✔️    |
| blocked_domains     | A set of domain names to block requests to. Subdomains are also matched (e.g., `"example.com"` blocks `"sub.example.com"` too).                                                                                                     |    ✔️    |
|   proxy_rotator     | A `ProxyRotator` instance for automatic proxy rotation. Cannot be combined with `proxy`.                                                                                                                                            |    ✔️    |
|       retries       | Number of retry attempts for failed requests. Defaults to 3.                                                                                                                                                                        |    ✔️    |
|     retry_delay     | Seconds to wait between retry attempts. Defaults to 1.                                                                                                                                                                              |    ✔️    |

In session classes, all these arguments can be set globally for the session. Still, you can configure each request individually by passing some of the arguments here that can be configured on the browser tab level like: `google_search`, `timeout`, `wait`, `page_action`, `extra_headers`, `disable_resources`, `wait_selector`, `wait_selector_state`, `network_idle`, `load_dom`, `solve_cloudflare`, `blocked_domains`, `proxy`, and `selector_config`.

> 🔍 Notes:
> 
> 1. It's basically the same arguments as [DynamicFetcher](dynamic.md#introduction) class but with these additional arguments `solve_cloudflare`, `block_webrtc`, `hide_canvas`, and `allow_webgl`.
> 2. The `disable_resources` option made requests ~25% faster in my tests for some websites and can help save your proxy usage, but be careful with it, as it can cause some websites to never finish loading.
> 3. The `google_search` argument is enabled by default for all requests, making the request appear to come from a Google search page. So, a request for `https://example.com` will set the referer to `https://www.google.com/search?q=example`. Also, if used together, it takes priority over the referer set by the `extra_headers` argument.
> 4. If you didn't set a user agent and enabled headless mode, the fetcher will generate a real user agent for the same browser version and use it. If you didn't set a user agent and didn't enable headless mode, the fetcher will use the browser's default user agent, which is the same as in standard browsers in the latest versions.

## Examples
It's easier to understand with examples, so we will now review most of the arguments individually. Since it's the same class as the [DynamicFetcher](dynamic.md#introduction), you can refer to that page for more examples, as we won't repeat all the examples from there.

### Cloudflare and stealth options

```python
# Automatic Cloudflare solver
page = StealthyFetcher.fetch('https://nopecha.com/demo/cloudflare', solve_cloudflare=True)

# Works with other stealth options
page = StealthyFetcher.fetch(
    'https://protected-site.com',
    solve_cloudflare=True,
    block_webrtc=True,
    real_chrome=True,
    hide_canvas=True,
    google_search=True,
    proxy='http://username:password@host:port',  # It can also be a dictionary with only the keys 'server', 'username', and 'password'.
)
```

The `solve_cloudflare` parameter enables automatic detection and solving all types of Cloudflare's Turnstile/Interstitial challenges:

- JavaScript challenges (managed)
- Interactive challenges (clicking verification boxes)
- Invisible challenges (automatic background verification)

And even solves the custom pages with embedded captcha.

> 🔍 **Important notes:**
> 
> 1. Sometimes, with websites that use custom implementations, you will need to use `wait_selector` to make sure Scrapling waits for the real website content to be loaded after solving the captcha. Some websites can be the real definition of an edge case while we are trying to make the solver as generic as possible.
> 2. The timeout should be at least 60 seconds when using the Cloudflare solver for sufficient challenge-solving time.
> 3. This feature works seamlessly with proxies and other stealth options.

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

page = StealthyFetcher.fetch('https://example.com', page_action=scroll_page)
```
Of course, if you use the async fetch version, the function must also be async.
```python
from playwright.async_api import Page

async def scroll_page(page: Page):
   await page.mouse.wheel(10, 0)
   await page.mouse.move(100, 400)
   await page.mouse.up()

page = await StealthyFetcher.async_fetch('https://example.com', page_action=scroll_page)
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


### Real-world example (Amazon)
This is for educational purposes only; this example was generated by AI, which also shows how easy it is to work with Scrapling through AI
```python
def scrape_amazon_product(url):
    # Use StealthyFetcher to bypass protection
    page = StealthyFetcher.fetch(url)

    # Extract product details
    return {
        'title': page.css('#productTitle::text').get().clean(),
        'price': page.css('.a-price .a-offscreen::text').get(),
        'rating': page.css('[data-feature-name="averageCustomerReviews"] .a-popover-trigger .a-color-base::text').get(),
        'reviews_count': page.css('#acrCustomerReviewText::text').re_first(r'[\d,]+'),
        'features': [
            li.clean() for li in page.css('#feature-bullets li span::text')
        ],
        'availability': page.css('#availability')[0].get_all_text(strip=True),
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
    real_chrome=True,
    block_webrtc=True,
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
        real_chrome=True,
        block_webrtc=True,
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

You may have noticed the `max_pages` argument. This is a new argument that enables the fetcher to create a **rotating pool of Browser tabs**. Instead of using a single tab for all your requests, you set a limit on the maximum number of pages that can be displayed at once. With each request, the library will close all tabs that have finished their task and check if the number of the current tabs is lower than the maximum allowed number of pages/tabs, then:

1. If you are within the allowed range, the fetcher will create a new tab for you, and then all is as normal.
2. Otherwise, it will keep checking every subsecond if creating a new tab is allowed or not for 60 seconds, then raise `TimeoutError`. This can happen when the website you are fetching becomes unresponsive.

This logic allows for multiple URLs to be fetched at the same time in the same browser, which saves a lot of resources, but most importantly, is so fast :)

In versions 0.3 and 0.3.1, the pool was reusing finished tabs to save more resources/time. That logic proved flawed, as it's nearly impossible to protect pages/tabs from contamination by the previous configuration used in the request before this one.

### Session Benefits

- **Browser reuse**: Much faster subsequent requests by reusing the same browser instance.
- **Cookie persistence**: Automatic cookie and session state handling as any browser does automatically.
- **Consistent fingerprint**: Same browser fingerprint across all requests.
- **Memory efficiency**: Better resource usage compared to launching new browsers with each fetch.

## Using Camoufox as an engine

This fetcher was using a custom version of [Camoufox](https://github.com/daijro/camoufox) as an engine before version 0.3.13, which was replaced now with [patchright](https://github.com/Kaliiiiiiiiii-Vinyzu/patchright) for many reasons. If you see that Camoufox is stable on your device, has no high memory issues, and want to continue using it. This section is for you.

First, you will need to install the Camoufox library, browser, and Firefox system dependencies if you didn't already:
```commandline
pip install camoufox
playwright install-deps firefox
camoufox fetch
```
Then you will inherit from `StealthySession` and set it as below:
```python
from scrapling.fetchers import StealthySession
from playwright.sync_api import sync_playwright
from camoufox.utils import launch_options as generate_launch_options

class StealthySession(StealthySession):
    def start(self):
        """Create a browser for this instance and context."""
        if not self.playwright:
            self.playwright = sync_playwright().start()
            # Configure camoufox run options here
            launch_options = generate_launch_options(**{"headless": True, "user_data_dir": ''})
            # Here's an example, part of what we have been doing before v0.3.13
            launch_options = generate_launch_options(**{
                "geoip": False,
                "proxy": self._config.proxy,
                "headless": self._config.headless,
                "humanize": True if self._config.solve_cloudflare else False,  # Better enable humanize for Cloudflare, otherwise it's up to you
                "i_know_what_im_doing": True,  # To turn warnings off with the user configurations
                "allow_webgl": self._config.allow_webgl,
                "block_webrtc": self._config.block_webrtc,
                "os": None,
                "user_data_dir": self._config.user_data_dir,
                "firefox_user_prefs": {
                    # This is what enabling `enable_cache` does internally, so we do it from here instead
                    "browser.sessionhistory.max_entries": 10,
                    "browser.sessionhistory.max_total_viewers": -1,
                    "browser.cache.memory.enable": True,
                    "browser.cache.disk_cache_ssl": True,
                    "browser.cache.disk.smart_size.enabled": True,
                },
                # etc...
            })
            self.context = self.playwright.firefox.launch_persistent_context(**launch_options)
        else:
            raise RuntimeError("Session has been already started")
```
After that, you can use it normally as before, even for solving Cloudflare challenges:
```python
with StealthySession(solve_cloudflare=True, headless=True) as session:
    page = session.fetch('https://sergiodemo.com/security/challenge/legacy-challenge')
    if page.css('#page-not-found-404'):
        print('Cloudflare challenge solved successfully!')
```

The same logic applies to the `AsyncStealthySession` class with a few differences:
```python
from scrapling.fetchers import AsyncStealthySession
from playwright.async_api import async_playwright
from camoufox.utils import launch_options as generate_launch_options

class AsyncStealthySession(AsyncStealthySession):
    async def start(self):
        """Create a browser for this instance and context."""
        if not self.playwright:
            self.playwright = await async_playwright().start()
            # Configure camoufox run options here
            launch_options = generate_launch_options(**{"headless": True, "user_data_dir": ''})
            # or set the launch options as in the above example
            self.context = await self.playwright.firefox.launch_persistent_context(**launch_options)
        else:
            raise RuntimeError("Session has been already started")
 
async with AsyncStealthySession(solve_cloudflare=True, headless=True) as session:
    page = await session.fetch('https://sergiodemo.com/security/challenge/legacy-challenge')
    if page.css('#page-not-found-404'):
        print('Cloudflare challenge solved successfully!')
```

Enjoy! :)

## When to Use

Use StealthyFetcher when:

- Bypassing anti-bot protection
- Need a reliable browser fingerprint
- Full JavaScript support needed
- Want automatic stealth features
- Need browser automation
- Dealing with Cloudflare protection