# Fetchers basics

## Introduction
Fetchers are classes that do requests or fetch pages in a single-line fashion with many features and return a [Response](#response-object) object. All fetchers have separate session classes to keep the session running (e.g., a browser fetcher keeps the browser open until you finish all requests).

Fetchers are not wrappers built on top of other libraries. They use these libraries as an engine to request/fetch pages but add features the underlying engines don't have, while still fully leveraging and optimizing them for web scraping.

## Fetchers Overview

Scrapling provides three different fetcher classes with their session classes; each fetcher is designed for a specific use case.

The following table compares them and can be quickly used for guidance.


| Feature            | Fetcher                                           | DynamicFetcher                                                                    | StealthyFetcher                                                                            |
|--------------------|---------------------------------------------------|-----------------------------------------------------------------------------------|--------------------------------------------------------------------------------------------|
| Relative speed     | 🐇🐇🐇🐇🐇                                        | 🐇🐇🐇                                                                            | 🐇🐇🐇                                                                                     |
| Stealth            | ⭐⭐                                                | ⭐⭐⭐                                                                               | ⭐⭐⭐⭐⭐                                                                                      |
| Anti-Bot options   | ⭐⭐                                                | ⭐⭐⭐                                                                               | ⭐⭐⭐⭐⭐                                                                                      |
| JavaScript loading | ❌                                                 | ✅                                                                                 | ✅                                                                                          |
| Memory Usage       | ⭐                                                 | ⭐⭐⭐                                                                               | ⭐⭐⭐                                                                                        |
| Best used for      | Basic scraping when HTTP requests alone can do it | - Dynamically loaded websites <br/>- Small automation<br/>- Small-Mid protections | - Dynamically loaded websites <br/>- Small automation <br/>- Small-Complicated protections |
| Browser(s)         | ❌                                                 | Chromium and Google Chrome                                                        | Chromium and Google Chrome                                                                 |
| Browser API used   | ❌                                                 | PlayWright                                                                        | PlayWright                                                                                 |
| Setup Complexity   | Simple                                            | Simple                                                                            | Simple                                                                                     |

## Parser configuration in all fetchers
All fetchers share the same import method, as you will see in the upcoming pages
```python
>>> from scrapling.fetchers import Fetcher, AsyncFetcher, StealthyFetcher, DynamicFetcher
```
Then you use it right away without initializing like this, and it will use the default parser settings:
```python
>>> page = StealthyFetcher.fetch('https://example.com') 
```
If you want to configure the parser ([Selector class](parsing/main_classes.md#selector)) that will be used on the response before returning it for you, then do this first:
```python
>>> from scrapling.fetchers import Fetcher
>>> Fetcher.configure(adaptive=True, keep_comments=False, keep_cdata=False)  # and the rest
```
or
```python
>>> from scrapling.fetchers import Fetcher
>>> Fetcher.adaptive=True
>>> Fetcher.keep_comments=False
>>> Fetcher.keep_cdata=False  # and the rest
```
Then, continue your code as usual.

The available configuration arguments are: `adaptive`, `adaptive_domain`, `huge_tree`, `keep_comments`, `keep_cdata`, `storage`, and `storage_args`, which are the same ones you give to the [Selector](parsing/main_classes.md#selector) class. You can display the current configuration anytime by running `<fetcher_class>.display_config()`.

**Info:** The `adaptive` argument is disabled by default; you must enable it to use that feature.

### Set parser config per request
As you probably understand, the logic above for setting the parser config will apply globally to all requests/fetches made through that class, and it's intended for simplicity.

If your use case requires a different configuration for each request/fetch, you can pass a dictionary to the request method (`fetch`/`get`/`post`/...) to an argument named `selector_config`.

## Response Object
The `Response` object is the same as the [Selector](parsing/main_classes.md#selector) class, but it has additional details about the response, like response headers, status, cookies, etc., as shown below:
```python
>>> from scrapling.fetchers import Fetcher
>>> page = Fetcher.get('https://example.com')

>>> page.status          # HTTP status code
>>> page.reason          # Status message
>>> page.cookies         # Response cookies as a dictionary
>>> page.headers         # Response headers
>>> page.request_headers # Request headers
>>> page.history         # Response history of redirections, if any
>>> page.body            # Raw response body as bytes
>>> page.encoding        # Response encoding
>>> page.meta            # Response metadata dictionary (e.g., proxy used). Mainly helpful with the spiders system.
```
All fetchers return the `Response` object.

**Note:** Unlike the [Selector](parsing/main_classes.md#selector) class, the `Response` class's body is always bytes since v0.4.