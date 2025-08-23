## Introduction
Fetchers are classes that can do requests or fetch pages for you easily in a single-line fashion with many features and then return a [Response](#response-object) object.

This feature was introduced because the only option before v0.2 was to fetch the page as you wanted, then pass it manually to the `Adaptor` class and start playing with it.

> Fetchers are not wrappers built on top of other libraries, but they use these libraries as an engine to make requests/fetch pages easily for you while fully utilizing that engine and adding features for you that aren't included in those engines

## Fetchers Overview

Scrapling provides three different fetcher classes, each designed for specific use cases.

The following table compares them and can be quickly used for guidance.


| Feature            | Fetcher        | PlayWrightFetcher                                                              | StealthyFetcher                                                                      |
|--------------------|----------------|--------------------------------------------------------------------------------|--------------------------------------------------------------------------------------|
| Relative speed     | ⭐⭐⭐⭐⭐          | ⭐⭐⭐                                                                            | ⭐⭐                                                                                   |
| Stealth            | ⭐              | ⭐⭐                                                                             | ⭐⭐⭐⭐                                                                                 |
| Anti-Bot options   | ⭐              | ⭐⭐                                                                             | ⭐⭐⭐⭐                                                                                 |
| JavaScript loading | ❌              | ✅                                                                              | ✅                                                                                    |
| Memory Usage       | ⭐              | ⭐⭐⭐                                                                            | ⭐⭐⭐                                                                                  |
| Best used for      | Basic scraping | - Dynamically loaded websites <br/>- Small automation<br/>- Slight protections | - Dynamically loaded websites <br/>- Small automation <br/>- Complicated protections |
| Browser(s)         | ❌              | Chromium and Google Chrome                                                     | Modified Firefox                                                                     |
| Browser API used   | ❌              | PlayWright                                                                     | PlayWright                                                                           |
| Setup Complexity   | Simple         | Simple                                                                         | Simple                                                                               |

In the following pages, we will talk about each one in detail.

## Parser configuration in all fetchers
All fetchers classes share the same import, as you will see in the upcoming pages
```python
>>> from scrapling.fetchers import Fetcher, AsyncFetcher, StealthyFetcher, PlayWrightFetcher
```
Then you use it right away without initializing like this, and it will use the default parser settings:
```python
>>> page = StealthyFetcher.fetch('https://example.com') 
```
If you want to configure the parser ([Adaptor class](../parsing/main_classes.md#adaptor)) that will be used on the response before returning it for you, then do this first:
```python
>>> from scrapling.fetchers import Fetcher
>>> Fetcher.configure(auto_match=True, encoding="utf8", keep_comments=False, keep_cdata=False)  # and the rest
```
or
```python
>>> from scrapling.fetchers import Fetcher
>>> Fetcher.auto_match=True
>>> Fetcher.encoding="utf8"
>>> Fetcher.keep_comments=False
>>> Fetcher.keep_cdata=False  # and the rest
```
Then, continue your code as usual.

The available configuration arguments are: `auto_match`, `huge_tree`, `keep_comments`, `keep_cdata`, `storage`, and `storage_args`, which are the same ones you give to the `Adaptor` class. You can display the current configuration anytime by running `<fetcher_class>.display_config()`.

> Note: The `auto_match` argument is disabled by default; you must enable it to use that feature.

### Set parser config per request
As you probably understood, the logic above for setting the parser config will work globally for all requests/fetches done through that class, and it's intended for simplicity.

If your use case requires a different configuration for each request/fetch, you can pass a dictionary to the request method (`fetch`/`get`/`post`/...) to an argument named `custom_config`.

## Response Object
The `Response` object is the same as the [Adaptor](../parsing/main_classes.md#adaptor) class, but it has added details about the response like response headers, status, cookies, etc... as shown below:
```python
>>> from scrapling.fetchers import Fetcher
>>> page = Fetcher.get('https://example.com')

>>> page.status          # HTTP status code
>>> page.reason          # Status message
>>> page.cookies         # Response cookies as a dictionary
>>> page.headers         # Response headers
>>> page.request_headers # Request headers
>>> page.history         # Response history of redirections, if any
>>> page.body            # Raw response body
>>> page.encoding        # Response encoding
```
All fetchers return the `Response` object.