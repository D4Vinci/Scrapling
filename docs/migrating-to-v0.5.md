---
title: "Migrating to v0.5"
description: "Move from Scrapling v0.4.15 to v0.5. Update browser imports, network capture, MCP tools, CLI commands, parser settings, and spider behavior."
---

# Migrating to v0.5 {#migrating-to-v05}

This guide covers the changes you need to check when moving from **v0.4.15 to v0.5**. It includes removed APIs, renamed tools, and fixes that can change your crawl results or saved files.

## Quick migration checklist {#quick-migration-checklist}

| If you use... | What to change |
| --- | --- |
| `DynamicFetcher`, `DynamicSession`, or `AsyncDynamicSession` | Use the matching stealthy class. |
| `capture_xhr` or `response.captured_xhr` | Use a browser session with `record_requests=True` and `session.network`. |
| `keep_cdata` | Remove it from parser and fetcher settings. |
| `scrapling extract stealthy-fetch` or the shell's `stealthy_fetch()` | Use `fetch` instead. |
| MCP tools | Update tool names, screenshot calls, and session creation response handling. |
| `response.follow()` after a POST or a request with query parameters | Pass the method, query, and body again when you need them. |
| Saved crawl checkpoints or response caches | Start a fresh crawl when your requests use the changed fingerprint inputs. |
| `robots_txt_obey=True` | Handle robots.txt fetch failures, which now block crawling for that domain. |

## Browser fetching {#browser-fetching}

### Replace the dynamic browser classes {#replace-the-dynamic-browser-classes}

The plain Playwright browser backend has been removed. All browser fetching now uses the Patchright-based stealthy backend.

| Removed API | Replacement |
| --- | --- |
| `scrapling.DynamicFetcher` | `scrapling.StealthyFetcher` |
| `scrapling.fetchers.DynamicFetcher` | `scrapling.fetchers.StealthyFetcher` |
| `scrapling.fetchers.chrome.PlayWrightFetcher` | `scrapling.fetchers.StealthyFetcher` |
| `scrapling.fetchers.DynamicSession` | `scrapling.fetchers.StealthySession` |
| `scrapling.fetchers.AsyncDynamicSession` | `scrapling.fetchers.AsyncStealthySession` |

The `scrapling.fetchers.chrome` module and the private `_browsers._controllers` module are gone. Use the public imports above.

**Before:**

```python
from scrapling.fetchers import DynamicFetcher

page = DynamicFetcher.fetch("https://example.com", headless=True)
```

**Now:**

```python
from scrapling.fetchers import StealthyFetcher

page = StealthyFetcher.fetch("https://example.com", headless=True)
```

For sessions, replace `DynamicSession` with `StealthySession`, or `AsyncDynamicSession` with `AsyncStealthySession`. Make the same change in your spider's `configure_sessions()` method. The `fetch()` and `async with` patterns still apply.

If your callbacks import browser types or catch browser errors, change `playwright.sync_api` to `patchright.sync_api`, or `playwright.async_api` to `patchright.async_api`. This includes `Page`, `Locator`, `Error`, and `TimeoutError`.

Patchright evaluates JavaScript in an isolated context by default. If a callback reads the page's own JavaScript variables, use `page.evaluate(..., isolated_context=False)`.

This changes the browser's behavior as well as its import name. Review your browser flags and fingerprint settings. Cloudflare solving still requires `solve_cloudflare=True`; it is not enabled by default. Also, `extra_flags` now adds to the built-in stealth flags instead of replacing them.

See [Browser fetching](fetching/stealthy.md) for the current options.

### Replace XHR capture with session network history {#replace-xhr-capture-with-session-network-history}

The `capture_xhr` parameter and `Response.captured_xhr` attribute have been removed. Remove the parameter even when its value is `None`. A one-shot fetch no longer has an XHR list attached to its response.

Custom integrations that call `ResponseFactory.from_playwright_response()` or `ResponseFactory.from_async_playwright_response()` must also remove `xhr_captured`. Pass `collect_history` by name to avoid the changed positional argument order.

**Before:**

```python
from scrapling.fetchers import StealthyFetcher

page = StealthyFetcher.fetch("https://example.com", capture_xhr="/api/")
for response in page.captured_xhr:
    print(response.url, response.body)
```

**Now:**

```python
from scrapling.fetchers import StealthySession

with StealthySession(record_requests=True) as session:
    page = session.fetch("https://example.com", network_idle=True)
    for response in session.network.search(url_pattern=r"/api/", limit=None):
        print(response.url, response.body)
```

Use `AsyncStealthySession` and `await session.fetch(...)` for async code. Reading `session.network` does not need `await`.

There are a few important differences:

- Set `record_requests=True` when you create the session. It is a session setting, not a per-fetch setting.
- History belongs to the **whole session**, across tabs, page loads, and actions. Use `after_id`, filters, or `session.network.clear()` if you need a smaller scope.
- Move the old `capture_xhr` regular expression to `url_pattern` when you search the history.
- `search()` returns saved `Response` objects. Read `.url`, `.status`, `.headers`, `.body`, or `.json()` directly. The recording ID, resource type, and sent body are in `response.meta["network_id"]`, `response.meta["resource_type"]`, and `response.meta["request_body"]`.
- Python history includes all resource types by default. Use `resource_type="xhr"` or `resource_type="fetch"` to select one, or `include_static=False` for XHR/fetch requests plus HTTP errors.
- `search()` returns at most 100 matches by default. Pass `limit=None` for all retained matches. Sessions retain at most 1,000 requests by default; change this with `max_recorded_requests`.
- Only completed requests are saved. Body capture is limited to supported text content types, 1 MiB per response, and 20 MiB of total retained body data. Older records can be removed as limits are reached. Check `response.meta.get("body_note")` for the reason a body was skipped.
- Reading history or closing the session does not wait for pending captures. Wait for the data you need before reading it. Saved Python history remains readable after session close.

See [Network history](fetching/stealthy.md#network-history) for filters and limits.

## Parser settings {#parser-settings}

### Remove `keep_cdata` {#remove-keep_cdata}

`keep_cdata` has been removed from `Selector`, fetcher configuration, and the settings returned by `display_config()`. Remove it from direct parser calls, `Fetcher.configure(...)`, and `selector_config` dictionaries passed to fetchers or integrations.

**Before:**

```python
from scrapling import Selector

page = Selector("<p>Hello</p>", keep_cdata=True)
```

**Now:**

```python
from scrapling import Selector

page = Selector("<p>Hello</p>")
```

There is no replacement setting. It did not affect the HTML parser's output. If you passed parser options by position, remove the old `keep_cdata` argument and use names for `adaptive` and storage options.

## Command line and interactive shell {#command-line-and-interactive-shell}

### Use `fetch` for browser requests {#use-fetch-for-browser-requests}

The CLI now has one browser command: `scrapling extract fetch`. It uses `StealthyFetcher`.

**Before:**

```bash
scrapling extract stealthy-fetch "https://example.com" page.md
```

**Now:**

```bash
scrapling extract fetch "https://example.com" page.md
```

If you already use `scrapling extract fetch`, the command name stays the same, but its backend changes from `DynamicFetcher` to `StealthyFetcher`. Options such as `--solve-cloudflare` now belong to `fetch`.

In `scrapling shell`, replace `stealthy_fetch(...)` with `fetch(...)`. The existing `fetch(...)` shortcut now calls `StealthyFetcher.fetch`. The dynamic classes are no longer added to the shell namespace.

### Read Markdown and text files as UTF-8 {#read-markdown-and-text-files-as-utf-8}

The extract commands and `Convertor.write_content_to_file()` now write `.md` and `.txt` files as **UTF-8**, regardless of the source page's charset. Update any code that reads those files with the page's original encoding. `.html` output still uses `page.encoding`.

Markdown from multiple selected elements now has blank lines between elements. This applies to `Response.markdown()` and Markdown file output. Update exact output comparisons or stored hashes that depended on concatenated text.

## MCP server {#mcp-server}

Update saved prompts, tool allowlists, wrappers, and MCP client tool definitions. Restart or reconnect your MCP client after the server update so it reads the current tools.

### Update tool names and bulk calls {#update-tool-names-and-bulk-calls}

| v0.4.15 tool | v0.5 replacement |
| --- | --- |
| `fetch`, `stealthy_fetch` | `browser_fetch_once` |
| `open_session` | `browser_open` |
| `session_fetch` | `browser_fetch` |
| `screenshot` | `browser_screenshot` |
| `bulk_fetch`, `bulk_stealthy_fetch` | One `browser_fetch_once` call per URL, or repeated `browser_fetch` calls through an open session |
| `bulk_get` | One `make_request` or `session_make_request` call per URL |

All bulk tools have been removed. Single-URL fetch tools return one `ResponseModel` with `status`, `content`, and `url`, not a list of responses. `content` itself is still a list of strings.

All MCP browser tools now use the stealthy backend. Remove `session_type` from calls to `browser_open`; there is no dynamic-browser choice. Its result has `session_type="stealthy"`. HTTP sessions still use `open_request_session` and return `session_type="static"`.

Python integrations must also stop importing `BrowserSessionType`, which was removed. `SessionType` now accepts only `"stealthy"` and `"static"`.

Calls through one browser session must run in order because they share a page. Close sessions with `close_session` when you finish.

### Read settings through `list_sessions` {#read-settings-through-list_sessions}

`browser_open` and `open_request_session` now return only:

```json
{
  "session_id": "my-session",
  "session_type": "stealthy"
}
```

The creation result no longer includes `created_at`, `is_alive`, `settings`, or `message`. Call `list_sessions` for the first three fields. The confirmation `message` is gone. Code that assumed `SessionCreatedModel` had all the fields of `SessionInfo` must change too.

### Fetch before taking a screenshot {#fetch-before-taking-a-screenshot}

`browser_screenshot` captures the **current page without reloading it**. It no longer accepts a URL or the old navigation and wait options: `wait`, `wait_selector`, `wait_selector_state`, and `network_idle`.

Use this order:

1. Call `browser_open`.
2. Call `browser_fetch` with the URL and any page-load options.
3. If needed, call `browser_actions` to interact with the page or wait for content.
4. Call `browser_screenshot` with the session ID.
5. Call `close_session` when you finish.

For example, the arguments for a full-page screenshot are:

```json
{
  "session_id": "my-session",
  "full_page": true
}
```

`timeout` on this tool now limits the screenshot operation. It does not load a page. For an element screenshot, use either `selector` or `ref`, and do not set `full_page=true`.

Screenshots still return image and text content blocks, with the current page URL in the text block. They do not return a fetch `ResponseModel`.

See the [MCP guide](ai/mcp-server.md) and [API reference](api-reference/mcp-server.md) for the full schemas.

## Spiders and HTTP requests {#spiders-and-http-requests}

### Pass request data again when following a link {#pass-request-data-again-when-following-a-link}

`response.follow()` no longer copies `method`, `params`, `data`, `json`, `files`, or `multipart` from the previous request. It also removes inherited `Content-Length` headers from `headers` and `extra_headers`.

A followed link now starts as a plain GET unless you pass request data explicitly. Other shared settings, such as the session, proxy, and callbacks, still follow the existing inheritance rules.

If your old code relied on inherited POST data, change:

```python
yield response.follow("/next")
```

to:

```python
yield response.follow("/next", method="POST", json={"page": 2})
```

Pass `params` explicitly too when the next request needs them. Let the HTTP client calculate the new `Content-Length`.

### Check request fingerprints and saved crawl state {#check-request-fingerprints-and-saved-crawl-state}

A request fingerprint is the key used to detect duplicate requests and find cached responses. Its inputs now handle three cases differently:

- `params` are merged into the URL before the key is built. Requests to the same URL with different query parameters are no longer treated as duplicates by default.
- JSON bodies such as `{}`, `[]`, `false`, `0`, and `""` are kept in the key. They no longer share the key for a missing body. `None` still means no JSON body.
- When `fp_include_headers=True`, changing only the insertion order of headers no longer changes the key.

If your crawl uses these inputs, finish it before upgrading or start a new crawl with a fresh checkpoint and response cache directory. Old saved keys can differ from the new keys. This is a change to request identity, not a new checkpoint file format.

Development mode now writes responses to the cache only after the blocked-response check. Blocked pages are not saved as successful cached results. Existing cache files are not cleaned for you; clear stale entries if you previously cached a challenge page.

Failed crawls now retain their checkpoint files. Check your cleanup code if it assumed those files disappear after an error. See [Pause and resume](spiders/advanced.md#pause-resume) and [Development mode](spiders/advanced.md#development-mode).

### Check robots.txt failures {#check-robotstxt-failures}

With `robots_txt_obey=True`, a robots.txt fetch exception or a response other than HTTP 200 or 4xx now blocks requests to that domain. Previously, those failures allowed crawling. HTTP 200 still supplies the rules, and HTTP 4xx still allows access.

The result is cached for the whole crawl. Fix the robots.txt access problem and start a new crawl; later requests in the same crawl will not retry the failed lookup. This does not change the default `robots_txt_obey=False`.

### Check link restrictions and sitemap callbacks {#check-link-restrictions-and-sitemap-callbacks}

- A `LinkExtractor` restriction that matches nothing now returns no links. It no longer falls back to the whole page. Fix the `restrict_css` or `restrict_xpath` expression if your crawl now finds fewer links.
- A restriction can now select the link element itself, not just a parent. This can add links that were previously missed. Review expected URL sets.
- `SitemapSpider` now sends page URLs to `parse()` when there are no rules, or when a matching rule has `callback=None`. It no longer sends those HTML pages back to the sitemap parser. Implement `parse()` for those cases and remove workarounds for the old routing.
- A leading Unicode byte-order mark is removed from robots.txt and CSV feeds. The first robots directive now takes effect, and the first CSV header no longer starts with `\ufeff`. If you set custom `headers`, the mark is removed from the first field value instead. Update code that worked around that hidden prefix. Sitemap XML comments and processing instructions are also skipped instead of causing a parse failure.

### Check form data, headers, and CLI JSON {#check-form-data-headers-and-cli-json}

Dictionary form data now expands list and tuple values into repeated keys. For example, `data={"tag": ["a", "b"]}` sends `tag=a&tag=b`. An empty list sends no entry for that key. A default `Content-Type: application/x-www-form-urlencoded` is added when you have not supplied one.

If you need a different wire format, pass an explicitly encoded string or bytes. `json`, raw `content`, and multipart uploads keep their own body handling. `None` values are **not dropped** from form data or query parameters; they remain the string `None`.

Per-request HTTP headers now override session headers regardless of letter case. A request header named `authorization` replaces the session's `Authorization` instead of sending both. Remove code that worked around duplicate header names.

CLI JSON values `{}`, `[]`, `false`, `0`, and `""` are now sent instead of silently dropped. Also, `curl2fetcher()` now applies curl's `-A` user agent and correctly passes `-x` proxies as a URL string. An explicit curl `-H 'User-Agent: ...'` still takes priority over `-A`.

## Other output changes to check {#other-output-changes-to-check}

These fixes do not remove APIs, but they can change stored results and exact output tests:

- Generated CSS and XPath selectors now include `:nth-of-type(1)` or `[1]` when needed to identify the first of several same-tag siblings. Refresh expected selector strings; do not remove the new position marker.
- Cleaned AI content now keeps visible elements with values such as `opacity:0.95`, removes elements hidden by more forms of inline styles and `<slot hidden>` elements, and removes all matching noise tags even when they are nested. Recheck exact Markdown, text, and sanitized HTML output.
- Browser response conversion now reads charset declarations with different letter case, spaces, or quoted values, such as `text/plain; CHARSET = "iso-8859-15"`. Non-HTML responses with these headers now use the declared encoding instead of falling back to UTF-8. Recheck text decoded from those responses.

## Verify your upgrade {#verify-your-upgrade}

Run a small crawl before your full job. Check the extracted data, followed URLs, sent request bodies, saved file encoding, and any cache or checkpoint behavior you depend on. For MCP integrations, check both tool inputs and returned data against the current schemas.

For older release changes, see the [changelog](changelog.md).
