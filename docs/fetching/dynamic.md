# Introduction

Here, we will discuss the `DynamicFetcher` class (previously known as `PlayWrightFetcher`). This class provides flexible browser automation with multiple configuration options and some stealth capabilities.

As we will explain later, to automate the page, you need some knowledge of [Playwright's Page API](https://playwright.dev/python/docs/api/class-page).

## Basic Usage
You have one primary way to import this Fetcher, which is the same for all fetchers.

```python
>>> from scrapling.fetchers import DynamicFetcher
```
Check out how to configure the parsing options [here](choosing.md#parser-configuration-in-all-fetchers)

Now, we will review most of the arguments one by one, using examples. If you want to jump to a table of all arguments for quick reference, [click here](#full-list-of-arguments)

> Note: The async version of the `fetch` method is the `async_fetch` method, of course.


This fetcher currently provides four main run options, which can be mixed as desired.

Which are:

### 1. Vanilla Playwright
```python
DynamicFetcher.fetch('https://example.com')
```
Using it in that manner will open a Chromium browser and load the page. There are no tricks or extra features unless you enable some; it's just a plain PlayWright API.

### 2. Stealth Mode
```python
DynamicFetcher.fetch('https://example.com', stealth=True)
```
It's the same as the vanilla Playwright option, but it provides a simple stealth mode suitable for websites with a small to medium protection layer(s).

Some of the things this fetcher's stealth mode does include:

  * Patching the CDP runtime fingerprint.
  * Mimics some of the real browsers' properties by injecting several JS files and using custom options.
  * Custom flags are used on launch to hide Playwright even more and make it faster.
  * Generates real browser headers of the same type and user OS, then appends them to the request's headers.

### 3. Real Chrome
```python
DynamicFetcher.fetch('https://example.com', real_chrome=True)
```
If you have a Google Chrome browser installed, use this option. It's the same as the first option, but will use the Google Chrome browser you installed on your device instead of Chromium.

This will make your requests look more authentic, so it's less detectable, and you can even use the `stealth=True` mode with it for better results, like below:
```python
DynamicFetcher.fetch('https://example.com', real_chrome=True, stealth=True)
```
If you don't have Google Chrome installed and want to use this option, you can use the command below in the terminal to install it for the library instead of installing it manually:
```commandline
playwright install chrome
```

### 4. CDP Connection
```python
DynamicFetcher.fetch('https://example.com', cdp_url='ws://localhost:9222')
```
Instead of launching a browser locally (Chromium/Google Chrome), you can connect to a remote browser through the [Chrome DevTools Protocol](https://chromedevtools.github.io/devtools-protocol/).

## Full list of arguments
Scrapling provides many options with this fetcher. To make it as simple as possible, we will list the options here and give examples of using most of them.

|      Argument       | Description                                                                                                                                                                                                                                                                                                                                                                                                                | Optional |
|:-------------------:|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|:--------:|
|         url         | Target url                                                                                                                                                                                                                                                                                                                                                                                                                 |    ❌     |
|      headless       | Pass `True` to run the browser in headless/hidden (**default**) or `False` for headful/visible mode.                                                                                                                                                                                                                                                                                                                       |    ✔️    |
|  disable_resources  | Drop requests of unnecessary resources for a speed boost. It depends, but it made requests ~25% faster in my tests for some websites.<br/>Requests dropped are of type `font`, `image`, `media`, `beacon`, `object`, `imageset`, `texttrack`, `websocket`, `csp_report`, and `stylesheet`. _This can help save your proxy usage, but be cautious with this option, as it may cause some websites to never finish loading._ |    ✔️    |
|       cookies       | Set cookies for the next request.                                                                                                                                                                                                                                                                                                                                                                                          |    ✔️    |
|      useragent      | Pass a useragent string to be used. **Otherwise, the fetcher will generate and use a real Useragent of the same browser.**                                                                                                                                                                                                                                                                                                 |    ✔️    |
|    network_idle     | Wait for the page until there are no network connections for at least 500 ms.                                                                                                                                                                                                                                                                                                                                              |    ✔️    |
|      load_dom       | Enabled by default, wait for all JavaScript on page(s) to fully load and execute (wait for the `domcontentloaded` state).                                                                                                                                                                                                                                                                                                  |    ✔️    |
|       timeout       | The timeout (milliseconds) used in all operations and waits through the page. The default is 30,000 ms (30 seconds).                                                                                                                                                                                                                                                                                                       |    ✔️    |
|        wait         | The time (milliseconds) the fetcher will wait after everything finishes before closing the page and returning the `Response` object.                                                                                                                                                                                                                                                                                       |    ✔️    |
|     page_action     | Added for automation. Pass a function that takes the `page` object and does the necessary automation.                                                                                                                                                                                                                                                                                                                      |    ✔️    |
|    wait_selector    | Wait for a specific css selector to be in a specific state.                                                                                                                                                                                                                                                                                                                                                                |    ✔️    |
|     init_script     | An absolute path to a JavaScript file to be executed on page creation for all pages in this session.                                                                                                                                                                                                                                                                                                                       |    ✔️    |
| wait_selector_state | Scrapling will wait for the given state to be fulfilled for the selector given with `wait_selector`. _Default state is `attached`._                                                                                                                                                                                                                                                                                        |    ✔️    |
|    google_search    | Enabled by default, Scrapling will set the referer header as if this request came from a Google search of this website's domain name.                                                                                                                                                                                                                                                                                      |    ✔️    |
|    extra_headers    | A dictionary of extra headers to add to the request. _The referer set by the `google_search` argument takes priority over the referer set here if used together._                                                                                                                                                                                                                                                          |    ✔️    |
|        proxy        | The proxy to be used with requests. It can be a string or a dictionary with the keys 'server', 'username', and 'password' only.                                                                                                                                                                                                                                                                                            |    ✔️    |
|     hide_canvas     | Add random noise to canvas operations to prevent fingerprinting.                                                                                                                                                                                                                                                                                                                                                           |    ✔️    |
|    disable_webgl    | Disables WebGL and WebGL 2.0 support entirely.                                                                                                                                                                                                                                                                                                                                                                             |    ✔️    |
|       stealth       | Enables stealth mode; you should always check the documentation to see what the stealth mode does currently.                                                                                                                                                                                                                                                                                                               |    ✔️    |
|     real_chrome     | If you have a Chrome browser installed on your device, enable this, and the Fetcher will launch and use an instance of your browser.                                                                                                                                                                                                                                                                                       |    ✔️    |
|       locale        | Set the locale for the browser if wanted. The default value is `en-US`.                                                                                                                                                                                                                                                                                                                                                    |    ✔️    |
|       cdp_url       | Instead of launching a new browser instance, connect to this CDP URL to control real browsers through CDP.                                                                                                                                                                                                                                                                                                                 |    ✔️    |
|   selector_config   | A dictionary of custom parsing arguments to be used when creating the final `Selector`/`Response` class.                                                                                                                                                                                                                                                                                                                   |    ✔️    |

## Examples
It's easier to understand with examples, so let's take a look.

### Resource Control

```python
# Disable unnecessary resources
page = DynamicFetcher.fetch(
    'https://example.com',
    disable_resources=True  # Blocks fonts, images, media, etc...
)
```

### Network Control

```python
# Wait for network idle (Consider fetch to be finished when there are no network connections for at least 500 ms)
page = DynamicFetcher.fetch('https://example.com', network_idle=True)

# Custom timeout (in milliseconds)
page = DynamicFetcher.fetch('https://example.com', timeout=30000)  # 30 seconds

# Proxy support
page = DynamicFetcher.fetch(
    'https://example.com',
    proxy='http://username:password@host:port'  # Or it can be a dictionary with the keys 'server', 'username', and 'password' only
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

page = DynamicFetcher.fetch(
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

page = await DynamicFetcher.async_fetch(
    'https://example.com',
    page_action=scroll_page
)
```

### Wait Conditions

```python
# Wait for the selector
page = DynamicFetcher.fetch(
    'https://example.com',
    wait_selector='h1',
    wait_selector_state='visible'
)
```
This is the last wait the fetcher will do before returning the response (if enabled). You pass a CSS selector to the `wait_selector` argument, and the fetcher will wait for the state you passed in the `wait_selector_state` argument to be fulfilled. If you didn't pass a state, the default would be `attached`, which means it will wait for the element to be present in the DOM.

After that, if `load_dom` is enabled (the default), the fetcher will check again to see if all JS files are loaded and executed (the `domcontentloaded` state) or continue waiting. If you have enabled `network_idle`, the fetcher will wait for `network_idle` to be fulfilled again, as explained above.

The states the fetcher can wait for can be any of the following ([source](https://playwright.dev/python/docs/api/class-page#page-wait-for-selector)):

- `attached`: Wait for an element to be present in the DOM.
- `detached`: Wait for an element to not be present in the DOM.
- `visible`: wait for an element to have a non-empty bounding box and no `visibility:hidden`. Note that an element without any content or with `display:none` has an empty bounding box and is not considered visible.
- `hidden`: wait for an element to be either detached from the DOM, or have an empty bounding box, or `visibility:hidden`. This is opposite to the `'visible'` option.

### Some Stealth Features

```python
# Full stealth mode
page = DynamicFetcher.fetch(
    'https://example.com',
    stealth=True,
    hide_canvas=True,
    disable_webgl=True,
    google_search=True
)

# Custom user agent
page = DynamicFetcher.fetch(
    'https://example.com',
    useragent='Mozilla/5.0...'
)

# Set browser locale
page = DynamicFetcher.fetch(
    'https://example.com',
    locale='en-US'
)
```
Hence, the `hide_canvas` argument doesn't disable the canvas but instead hides it by adding random noise to canvas operations, preventing fingerprinting. Also, if you didn't set a user agent (preferred), the fetcher will generate a real User Agent of the same browser and use it.

The `google_search` argument is enabled by default, making the request look as if it came from a Google search page. So, a request for `https://example.com` will set the referer to `https://www.google.com/search?q=example`. Also, if used together, it takes priority over the referer set by the `extra_headers` argument.

### General example
```python
from scrapling.fetchers import DynamicFetcher

def scrape_dynamic_content():
    # Use Playwright for JavaScript content
    page = DynamicFetcher.fetch(
        'https://example.com/dynamic',
        network_idle=True,
        wait_selector='.content'
    )
    
    # Extract dynamic content
    content = page.css('.content')
    
    return {
        'title': content.css_first('h1::text'),
        'items': [
            item.text for item in content.css('.item')
        ]
    }
```

## Session Management

To keep the browser open until you make multiple requests with the same configuration, use `DynamicSession`/`AsyncDynamicSession` classes. Those classes can accept all the arguments that the `fetch` function can take, which enables you to specify a config for the entire session.

```python
from scrapling.fetchers import DynamicSession

# Create a session with default configuration
with DynamicSession(
    headless=True,
    stealth=True,
    disable_resources=True,
    real_chrome=True
) as session:
    # Make multiple requests with the same browser instance
    page1 = session.fetch('https://example1.com')
    page2 = session.fetch('https://example2.com')
    page3 = session.fetch('https://dynamic-site.com')
    
    # All requests reuse the same tab on the same browser instance
```

### Async Session Usage

```python
import asyncio
from scrapling.fetchers import AsyncDynamicSession

async def scrape_multiple_sites():
    async with AsyncDynamicSession(
        stealth=True,
        network_idle=True,
        timeout=30000,
        max_pages=3
    ) as session:
        # Make async requests with shared browser configuration
        pages = await asyncio.gather(
            session.fetch('https://spa-app1.com'),
            session.fetch('https://spa-app2.com'),
            session.fetch('https://dynamic-content.com')
        )
        return pages
```

You may have noticed the `max_pages` argument. This is a new argument that enables the fetcher to create a **pool of Browser tabs** that will be rotated automatically. Instead of using one tab for all your requests, you set a limit on the maximum number of pages allowed. With each request, the library will close all tabs that have finished their task and check if the number of the current tabs is lower than the maximum allowed number of pages/tabs, then:

1. If you are within the allowed range, the fetcher will create a new tab for you, and then all is as normal.
2. Otherwise, it will keep checking every subsecond if creating a new tab is allowed or not for 60 seconds, then raise `TimeoutError`. This can happen when the website you are fetching becomes unresponsive for some reason.

This logic allows for multiple websites to be fetched at the same time in the same browser, which saves a lot of resources, but most importantly, is so fast :)

In versions 0.3 and 0.3.1, the pool was reusing finished tabs to save more resources/time. That logic proved to have flaws since it's nearly impossible to protect pages/tabs from contamination of the previous configuration you used with the request before this one.

### Session Benefits

- **Browser reuse**: Much faster subsequent requests by reusing the same browser instance.
- **Cookie persistence**: Automatic cookie and session state handling as any browser does automatically.
- **Consistent fingerprint**: Same browser fingerprint across all requests.
- **Memory efficiency**: Better resource usage compared to launching new browsers with each fetch.

## When to Use

Use DynamicFetcher when:

- Need browser automation
- Want multiple browser options
- Using a real Chrome browser
- Need custom browser config
- Want flexible stealth options 

If you want more stealth and control without much config, check out the [StealthyFetcher](stealthy.md).