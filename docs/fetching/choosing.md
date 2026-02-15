# Fetchers basics

## Introduction
Fetchers are classes that can do requests or fetch pages for you easily in a single-line fashion with many features and then return a [Response](#response-object) object. Starting with v0.3, all fetchers have separate classes to keep the session running, so for example, a fetcher that uses a browser will keep the browser open till you finish all your requests through it instead of opening multiple browsers. So it depends on your use case.

This feature was introduced because, before v0.2, Scrapling was only a parsing engine. The target here is to gradually become the one-stop shop for all Web Scraping needs.

> Fetchers are not wrappers built on top of other libraries. However, they only use these libraries as an engine to request/fetch pages. To further clarify this, all fetchers have features that the underlying engines don't, while still fully leveraging those engines and optimizing them for Web Scraping.

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

In the following pages, we will talk about each one in detail.

## Parser configuration in all fetchers
All fetchers share the same import method, as you will see in the upcoming pages
```python
>>> from scrapling.fetchers import Fetcher, AsyncFetcher, StealthyFetcher, DynamicFetcher
```
Then you use it right away without initializing like this, and it will use the default parser settings:
```python
>>> page = StealthyFetcher.fetch('https://example.com') 
```
If you want to configure the parser ([Selector class](../parsing/main_classes.md#selector)) that will be used on the response before returning it for you, then do this first:
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

The available configuration arguments are: `adaptive`, `adaptive_domain`, `huge_tree`, `keep_comments`, `keep_cdata`, `storage`, and `storage_args`, which are the same ones you give to the [Selector](../parsing/main_classes.md#selector) class. You can display the current configuration anytime by running `<fetcher_class>.display_config()`.

!!! info

    The `adaptive` argument is disabled by default; you must enable it to use that feature.

### Set parser config per request
As you probably understand, the logic above for setting the parser config will apply globally to all requests/fetches made through that class, and it's intended for simplicity.

If your use case requires a different configuration for each request/fetch, you can pass a dictionary to the request method (`fetch`/`get`/`post`/...) to an argument named `selector_config`.

## Response Object
The `Response` object is the same as the [Selector](../parsing/main_classes.md#selector) class, but it has additional details about the response, like response headers, status, cookies, etc., as shown below:
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

!!! note

    Unlike the [Selector](../parsing/main_classes.md#selector) class, the `Response` class's body is always bytes since v0.4.