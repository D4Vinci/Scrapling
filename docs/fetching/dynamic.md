# Introduction

Here, we will discuss the `PlayWrightFetcher` class. This class provides flexible browser automation with multiple configuration options and some stealth capabilities. It uses [PlayWright](https://playwright.dev/python/docs/intro) as an engine for fetching websites.

As we will explain later, to automate the page, you need some knowledge of [PlayWright's Page API](https://playwright.dev/python/docs/api/class-page).

## Basic Usage
You have one primary way to import this Fetcher, which is the same for all fetchers.

```python
>>> from scrapling.fetchers import PlayWrightFetcher
```
Check out how to configure the parsing options [here](choosing.md#parser-configuration-in-all-fetchers)

Now we will go over most of the arguments one by one with examples if you want to jump to a table of all arguments for quick reference [click here](#full-list-of-arguments)

> Notes: 
> 
> 1. Every time you fetch a website with this fetcher, it waits by default for all JavaScript to fully load and execute, so you don't have to (waits for the `domcontentloaded` state).
> 2. Of course, the async version of the `fetch` method is the `async_fetch` method.


This fetcher currently provides 4 main run options, but they can be mixed as you want.

Which are:

### 1. Vanilla Playwright
```python
PlayWrightFetcher.fetch('https://example.com')
```
Using it like that will open a Chromium browser and fetch the page. There are no tricks or extra features; it's just a plain PlayWright API.

### 2. Stealth Mode
```python
PlayWrightFetcher.fetch('https://example.com', stealth=True)
```
It's the same as the vanilla PlayWright option, but it provides a simple stealth mode suitable for websites with a small-to-medium protection layer(s).

Some of the things this fetcher's stealth mode does include:

  * Patching the CDP runtime fingerprint.
  * Mimics some of the real browsers' properties by injecting several JS files and using custom options.
  * Custom flags are used on launch to hide Playwright even more and make it faster.
  * Generates real browser headers of the same type and user OS, then append them to the request's headers.

### 3. Real Chrome
```python
PlayWrightFetcher.fetch('https://example.com', real_chrome=True)
```
If you have a Google Chrome browser installed, use this option. It's the same as the first option but will use the Google Chrome browser you installed on your device instead of Chromium.

This will make your requests look more like requests coming from an actual human, so it's less detectable, and you can even use the `stealth=True` mode with it for better results like below:
```python
PlayWrightFetcher.fetch('https://example.com', real_chrome=True, stealth=True)
```
If you don't have Google Chrome installed and want to use this option, you can use the command below in the terminal to install it for the library instead of installing it manually:
```commandline
playwright install chrome
```

### 4. CDP Connection
```python
PlayWrightFetcher.fetch('https://example.com', cdp_url='ws://localhost:9222')
```
Instead of launching a browser locally (Chromium/Google Chrome), you can connect to a remote browser through the [Chrome DevTools Protocol](https://chromedevtools.github.io/devtools-protocol/).

This fetcher takes it even a step further. You can use [NSTBrowser](https://app.nstbrowser.io/r/1vO5e5)'s [docker browserless](https://hub.docker.com/r/nstbrowser/browserless) option by passing the CDP URL and enabling `nstbrowser_mode` option like below
```python
PlayWrightFetcher.fetch('https://example.com', cdp_url='ws://localhost:9222', nstbrowser_mode=True)
```
There's also a `nstbrowser_config` argument to send the config you want to send with the requests to the NSTBrowser. If you leave it empty, Scrapling defaults to an optimized NSTBrowser's docker browserless config.

## Full list of arguments
Scrapling provides many options with this fetcher, which works in all modes except the [NSTBrowser](https://app.nstbrowser.io/r/1vO5e5) mode. To make it as simple as possible, we will list the options here and give examples of using most of them.

|      Argument       | Description                                                                                                                                                                                                                                                                                                                                                                                                       | Optional |
|:-------------------:|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|:--------:|
|         url         | Target url                                                                                                                                                                                                                                                                                                                                                                                                        |    ❌     |
|      headless       | Pass `True` to run the browser in headless/hidden (**default**) or `False` for headful/visible mode.                                                                                                                                                                                                                                                                                                              |    ✔️    |
|  disable_resources  | Drop requests of unnecessary resources for a speed boost. It depends, but it made requests ~25% faster in my tests for some websites.<br/>Requests dropped are of type `font`, `image`, `media`, `beacon`, `object`, `imageset`, `texttrack`, `websocket`, `csp_report`, and `stylesheet`. _This can help save your proxy usage, but be careful with this option as it makes some websites never finish loading._ |    ✔️    |
|      useragent      | Pass a useragent string to be used. **Otherwise, the fetcher will generate and use a real Useragent of the same browser.**                                                                                                                                                                                                                                                                                        |    ✔️    |
|    network_idle     | Wait for the page until there are no network connections for at least 500 ms.                                                                                                                                                                                                                                                                                                                                     |    ✔️    |
|       timeout       | The timeout (milliseconds) used in all operations and waits through the page. The default is 30000.                                                                                                                                                                                                                                                                                                               |    ✔️    |
|        wait         | The time (milliseconds) the fetcher will wait after everything finishes before closing the page and returning the `Response` object.                                                                                                                                                                                                                                                                              |    ✔️    |
|     page_action     | Added for automation. Pass a function that takes the `page` object and does the necessary automation, then returns `page` again.                                                                                                                                                                                                                                                                                  |    ✔️    |
|    wait_selector    | Wait for a specific css selector to be in a specific state.                                                                                                                                                                                                                                                                                                                                                       |    ✔️    |
| wait_selector_state | Scrapling will wait for the given state to be fulfilled for the selector given with `wait_selector`. _Default state is `attached`._                                                                                                                                                                                                                                                                               |    ✔️    |
|    google_search    | Enabled by default, Scrapling will set the referer header as if this request came from a Google search for this website's domain name.                                                                                                                                                                                                                                                                            |    ✔️    |
|    extra_headers    | A dictionary of extra headers to add to the request. The referer set by the `google_search` argument takes priority over the referer set here if used together.                                                                                                                                                                                                                                                   |    ✔️    |
|        proxy        | The proxy to be used with requests. It can be a string or a dictionary with the keys 'server', 'username', and 'password' only.                                                                                                                                                                                                                                                                                   |    ✔️    |
|     hide_canvas     | Add random noise to canvas operations to prevent fingerprinting.                                                                                                                                                                                                                                                                                                                                                  |    ✔️    |
|    disable_webgl    | Disables WebGL and WebGL 2.0 support entirely.                                                                                                                                                                                                                                                                                                                                                                    |    ✔️    |
|       stealth       | Enables stealth mode; you should always check the documentation to see what stealth mode does currently.                                                                                                                                                                                                                                                                                                          |    ✔️    |
|     real_chrome     | If you have a Chrome browser installed on your device, enable this, and the Fetcher will launch and use an instance of your browser and use it.                                                                                                                                                                                                                                                                   |    ✔️    |
|       locale        | Set the locale for the browser if wanted. The default value is `en-US`.                                                                                                                                                                                                                                                                                                                                           |    ✔️    |
|       cdp_url       | Instead of launching a new browser instance, connect to this CDP URL to control real browsers/NSTBrowser through CDP.                                                                                                                                                                                                                                                                                             |    ✔️    |
|   nstbrowser_mode   | Enables NSTBrowser mode, **it have to be used with `cdp_url` argument or it will get completely ignored.**                                                                                                                                                                                                                                                                                                        |    ✔️    |
|  nstbrowser_config  | The config you want to send with requests to the NSTBrowser. _Scrapling defaults to an optimized NSTBrowser's docker browserless config if you leave this argument empty._                                                                                                                                                                                                                                        |    ✔️    |


## Examples
It's easier to understand with examples, so let's look at it.

### Resource Control

```python
# Disable unnecessary resources
page = PlayWrightFetcher.fetch(
    'https://example.com',
    disable_resources=True  # Blocks fonts, images, media, etc...
)
```

### Network Control

```python
# Wait for network idle (Consider fetch to be finished when there are no network connections for at least 500 ms)
page = PlayWrightFetcher.fetch('https://example.com', network_idle=True)

# Custom timeout (in milliseconds)
page = PlayWrightFetcher.fetch('https://example.com', timeout=30000)  # 30 seconds

# Proxy support
page = PlayWrightFetcher.fetch(
    'https://example.com',
    proxy='http://username:password@host:port'  # Or it can be a dictionary with the keys 'server', 'username', and 'password' only
)
```

### Browser Automation
This is where your knowledge about [PlayWright's Page API](https://playwright.dev/python/docs/api/class-page) comes into play. The function you pass here takes the page object from Playwright's API, does what you want, and then returns it again for the current fetcher to continue working on it.

This function is executed right after waiting for network_idle (if enabled) and before waiting for the `wait_selector` argument, so it can be used for many things, not just automation. You can alter the page as you want.

In the example below, I used page [mouse events](https://playwright.dev/python/docs/api/class-mouse) to move the mouse wheel to scroll the page and then move the mouse.
```python
from playwright.sync_api import Page

def scroll_page(page: Page):
    page.mouse.wheel(10, 0)
    page.mouse.move(100, 400)
    page.mouse.up()
    return page

page = PlayWrightFetcher.fetch(
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

page = await PlayWrightFetcher.async_fetch(
    'https://example.com',
    page_action=scroll_page
)
```

### Wait Conditions

```python
# Wait for the selector
page = PlayWrightFetcher.fetch(
    'https://example.com',
    wait_selector='h1',
    wait_selector_state='visible'
)
```
This is the last wait the fetcher will do before returning the response (if enabled). You pass a CSS selector to the `wait_selector` argument, and the fetcher will wait for the state you passed in the `wait_selector_state` argument to be fulfilled. If you didn't pass a state, the default would be `attached`, which means it will wait for the element to be present in the DOM.

After that, the fetcher will check again to see if all JS files are loaded and executed (the `domcontentloaded` state) and wait for them to be. If you have enabled `network_idle` with this, the fetcher will wait for `network_idle` to be fulfilled again, as explained above.

The states the fetcher can wait for can be either ([source](https://playwright.dev/python/docs/api/class-page#page-wait-for-selector)):

- `attached`: Wait for an element to be present in DOM.
- `detached`: Wait for an element to not be present in DOM.
- `visible`: wait for an element to have a non-empty bounding box and no `visibility:hidden`. Note that an element without any content or with `display:none` has an empty bounding box and is not considered visible.
- `hidden`: wait for an element to be either detached from DOM, or have an empty bounding box or `visibility:hidden`. This is opposite to the `'visible'` option.

### Some Stealth Features

```python
# Full stealth mode
page = PlayWrightFetcher.fetch(
    'https://example.com',
    stealth=True,
    hide_canvas=True,
    disable_webgl=True,
    google_search=True
)

# Custom user agent
page = PlayWrightFetcher.fetch(
    'https://example.com',
    useragent='Mozilla/5.0...'
)

# Set browser locale
page = PlayWrightFetcher.fetch(
    'https://example.com',
    locale='en-US'
)
```
Hence, the `hide_canvas` argument doesn't disable canvas but hides it by adding random noise to canvas operations to prevent fingerprinting. Also, if you didn't set a useragent (preferred), the fetcher will generate a real Useragent of the same browser and use it.

The `google_search` argument is enabled by default, making the request look like it came from Google. So, a request for `https://example.com` will set the referer to `https://www.google.com/search?q=example`. Also, if used together, it takes priority over the referer set by the `extra_headers` argument.

### General example
```python
from scrapling.fetchers import PlayWrightFetcher

def scrape_dynamic_content():
    # Use PlayWright for JavaScript content
    page = PlayWrightFetcher.fetch(
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

## When to Use

Use PlayWrightFetcher when:

- Need browser automation
- Want multiple browser options
- Using a real Chrome browser
- Need custom browser config
- Want flexible stealth options 

If you want more stealth and control without much config, check out the [StealthyFetcher](stealthy.md).