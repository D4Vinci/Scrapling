# Scrapling MCP Server

The Scrapling MCP server exposes fourteen tools over the MCP protocol. It supports CSS-selector-based content narrowing (reducing tokens by extracting only relevant elements before returning results), plain HTTP requests and stealth browser rendering with anti-bot bypass, persistent browser session management, mouse actions, batch field filling, keyboard shortcuts, page waits, custom JavaScript, network history, and page screenshots returned as real image content blocks. Every fetch takes one URL. One-shot tools (`make_request`, `browser_fetch_once`) close their own client or browser after the call. Use sessions opened with `browser_open` or `open_request_session` for related requests, browser actions, or network history. Browser session calls reuse one tab, so fetch pages and run actions in order. Close each persistent session when done.

Fetch and HTTP request tools return a `ResponseModel` with fields: `status` (int), `content` (list of strings), `url` (str). The `browser_screenshot` tool returns a list of MCP content blocks: an `ImageContent` (the screenshot bytes) followed by a `TextContent` (the current page URL). `browser_snapshot` and `browser_actions` return plain text. Both network tools return structured JSON; the request list supports pagination. `browser_evaluate` returns compact JSON in one plain text block.

## Shadow DOM

Set `pierce_shadow=true` on `browser_fetch_once` or each `browser_fetch` call to include open Shadow DOM content. It defaults to `false`. See [Shadow DOM](fetching/dynamic.md#shadow-dom) for selector examples and limits.


## One-shot tools

### `make_request` -- HTTP request, any method (single URL)

Fast HTTP request with browser fingerprint impersonation (TLS, headers). Supports GET (default), POST, PUT, and DELETE via the `method` parameter. Suitable for static pages with no/low bot protection. Closes its own HTTP client after the call; use `session_make_request` for a persistent session.

**Key parameters:**

| Parameter           | Type                                      | Default      | Description                                                        |
|---------------------|-------------------------------------------|--------------|--------------------------------------------------------------------|
| `url`               | str                                       | required     | URL to fetch                                                       |
| `method`            | `"GET"` / `"POST"` / `"PUT"` / `"DELETE"` | `"GET"`      | HTTP method                                                        |
| `data`              | dict or str or null                       | null         | Request body (form data). POST/PUT/DELETE only                     |
| `json`              | dict or list or null                      | null         | Request body (JSON). POST/PUT/DELETE only                          |
| `extraction_type`   | `"markdown"` / `"html"` / `"text"`        | `"markdown"` | Output format                                                      |
| `css_selector`      | str or null                               | null         | CSS selector to narrow content (applied after `main_content_only`) |
| `main_content_only` | bool                                      | true         | Restrict to `<body>` content                                       |
| `impersonate`       | str                                       | `"chrome"`   | Browser fingerprint to impersonate                                 |
| `proxy`             | str or null                               | null         | Proxy URL, e.g. `"http://user:pass@host:port"`                     |
| `proxy_auth`        | dict or null                              | null         | `{"username": "...", "password": "..."}`                           |
| `auth`              | dict or null                              | null         | HTTP basic auth, same format as proxy_auth                         |
| `timeout`           | number                                    | 30           | Seconds before timeout                                             |
| `retries`           | int                                       | 3            | Maximum attempts, including the first                              |
| `retry_delay`       | int                                       | 1            | Seconds between retries                                            |
| `stealthy_headers`  | bool                                      | true         | Generate realistic browser headers and Google referer              |
| `http3`             | bool                                      | false        | Use HTTP/3 (may conflict with `impersonate`)                       |
| `follow_redirects`  | bool or "safe"                            | "safe"       | Follow redirects. "safe" rejects redirects to internal/private IPs |
| `max_redirects`     | int                                       | 30           | Max redirects (-1 for unlimited)                                   |
| `headers`           | dict or null                              | null         | Custom request headers                                             |
| `cookies`           | dict or null                              | null         | Request cookies                                                    |
| `params`            | dict or null                              | null         | Query string parameters                                            |
| `verify`            | bool                                      | true         | Verify HTTPS certificates                                          |

### `browser_fetch_once` -- Stealth browser fetch (single URL)

Uses a stealthy Chromium browser through Patchright for JavaScript rendering, fingerprint spoofing, and anti-bot bypass. Supports dynamic/SPA pages and sites with Cloudflare Turnstile/Interstitial or other strong protections.

**Key parameters:**

| Parameter             | Type                | Default      | Description                                                                     |
|-----------------------|---------------------|--------------|---------------------------------------------------------------------------------|
| `url`                 | str                 | required     | URL to fetch                                                                    |
| `extraction_type`     | str                 | `"markdown"` | `"markdown"` / `"html"` / `"text"`                                              |
| `css_selector`        | str or null         | null         | Narrow content before extraction                                                |
| `main_content_only`   | bool                | true         | Restrict to `<body>`                                                            |
| `headless`            | bool                | true         | Run browser hidden (true) or visible (false)                                    |
| `proxy`               | str or dict or null | null         | String URL or `{"server": "...", "username": "...", "password": "..."}`         |
| `timeout`             | number              | 30000        | Timeout in **milliseconds**                                                     |
| `wait`                | number              | 0            | Extra wait (ms) after page load before extraction                               |
| `wait_selector`       | str or null         | null         | CSS selector to wait for before extraction                                      |
| `wait_selector_state` | str                 | `"attached"` | State for wait_selector: `"attached"` / `"visible"` / `"hidden"` / `"detached"` |
| `network_idle`        | bool                | false        | Wait until no network activity for 500ms                                        |
| `pierce_shadow`       | bool                | false        | Include open Shadow DOM content in this request.                                |
| `disable_resources`   | bool                | false        | Block fonts, images, media, stylesheets, etc. for speed                         |
| `google_search`       | bool                | true         | Set a Google referer header                                                     |
| `real_chrome`         | bool                | false        | Use locally installed Chrome instead of bundled Chromium                        |
| `cdp_url`             | str or null         | null         | Connect to existing browser via CDP URL                                         |
| `extra_headers`       | dict or null        | null         | Additional request headers                                                      |
| `useragent`           | str or null         | null         | Custom user-agent (auto-generated if null)                                      |
| `cookies`             | list or null        | null         | Playwright-format cookies                                                       |
| `timezone_id`         | str or null         | null         | Browser timezone, e.g. `"America/New_York"`                                     |
| `locale`              | str or null         | null         | Browser locale, e.g. `"en-GB"`                                                  |
| `solve_cloudflare` | bool         | false   | Automatically solve Cloudflare Turnstile/Interstitial challenges |
| `hide_canvas`      | bool         | false   | Add noise to canvas operations                                  |
| `block_webrtc`     | bool         | false   | Disable non-proxied WebRTC UDP to reduce IP leaks                 |
| `allow_webgl`      | bool         | true    | Keep WebGL enabled; disabling it can trigger bot detection        |
| `additional_args`  | dict or null | null    | Extra Playwright context args (overrides Scrapling defaults)     |

This one-shot tool creates and closes its own stealthy browser session. For related fetches, later browser actions, or network history, use `browser_open` and `browser_fetch`.

## Session tools

### `browser_open` -- Create a persistent stealthy browser session

Opens a stealthy browser session that stays alive across multiple `browser_fetch` calls, avoiding the overhead of launching a new browser each time. It holds the browser-level configuration only; per-request options are passed to `browser_fetch`. For plain HTTP requests without a browser, use `open_request_session` instead. Returns a `SessionCreatedModel` with `session_id`, `session_type="stealthy"`, `created_at`, `is_alive`, `settings` (the session's effective configuration for the AI agent; empty for CDP sessions), and `message`.

**Key parameters:**

| Parameter          | Type                        | Default      | Description                                                                                           |
|--------------------|-----------------------------|--------------|-------------------------------------------------------------------------------------------------------|
| `session_id`       | str or null                 | null         | Custom ID for the session. If omitted, a random 12-char hex ID is generated. Raises if already in use |
| `headless`         | bool                        | true         | Run browser hidden or visible                                                                         |
| `hide_canvas`      | bool                        | false        | Canvas fingerprint noise                                                              |
| `block_webrtc`     | bool                        | false        | Block WebRTC IP leak                                                                  |
| `allow_webgl`      | bool                        | true         | Keep WebGL enabled                                                                    |

Plus the other browser-level session parameters (`proxy`, `real_chrome`, `cdp_url`, `locale`, `timezone_id`, `useragent`, `cookies`, `executable_path`, `additional_args`). Per-request options (`timeout`, `wait`, `google_search`, `network_idle`, `disable_resources`, `wait_selector`, `wait_selector_state`, `extra_headers`, `solve_cloudflare`) are not set here; pass them to `browser_fetch`.

Use `solve_cloudflare` on `browser_fetch` to solve Cloudflare challenges through the session.

Recording of completed requests starts automatically for this session. Use `browser_network_requests` to find traffic and `browser_network_request` to inspect a recorded request.

### `open_request_session` -- Create a persistent HTTP requests session

Opens an HTTP session (no browser) that stays alive across multiple `session_make_request` calls, keeping cookies, connections, and the browser fingerprint between requests. Returns the same `SessionCreatedModel` receipt and shows in `list_sessions` as a `static` session.

| Parameter     | Type        | Default    | Description                                                                                           |
|---------------|-------------|------------|-------------------------------------------------------------------------------------------------------|
| `session_id`  | str or null | null       | Custom ID for the session. If omitted, a random 12-char hex ID is generated. Raises if already in use |
| `impersonate` | str         | `"chrome"` | Browser fingerprint to impersonate on every request                                                   |
| `proxy`       | str or null | null       | Proxy URL used for every request, e.g. `"http://user:pass@host:port"`                                 |

### `browser_fetch` -- Fetch through an open browser session (single URL)

Fetches one URL through a stealthy Chromium session opened with `browser_open`, with JavaScript rendering, fingerprint spoofing, and Cloudflare Turnstile/Interstitial bypass. The session holds the browser-level configuration; every parameter here applies to this request only. Raises on a requests session; use `session_make_request` there instead.

| Parameter             | Type         | Default      | Description                                                                            |
|-----------------------|--------------|--------------|----------------------------------------------------------------------------------------|
| `url`                 | str          | required     | URL to fetch                                                                           |
| `session_id`          | str          | required     | ID of an open session created with `browser_open`                                      |
| `extraction_type`     | str          | `"markdown"` | `"markdown"` / `"html"` / `"text"` / `"snapshot"`                                      |
| `css_selector`        | str or null  | null         | Narrow content before extraction                                                       |
| `main_content_only`   | bool         | true         | Restrict to `<body>`                                                                   |
| `wait`                | number       | 0            | Extra wait (ms) after page load before extraction                                      |
| `timeout`             | number       | 30000        | Timeout in **milliseconds**                                                            |
| `google_search`       | bool         | true         | Set a Google referer header                                                            |
| `network_idle`        | bool         | false        | Wait until no network activity for 500ms                                               |
| `pierce_shadow`       | bool         | false        | Include open Shadow DOM content in this request.                                       |
| `load_dom`            | bool         | true         | Wait for the page's JavaScript to fully load and execute                               |
| `disable_resources`   | bool         | false        | Block fonts, images, media, stylesheets, etc. for speed                                |
| `wait_selector`       | str or null  | null         | CSS selector to wait for before extraction                                             |
| `wait_selector_state` | str          | `"attached"` | State for wait_selector: `"attached"` / `"visible"` / `"hidden"` / `"detached"`        |
| `extra_headers`       | dict or null | null         | Additional request headers                                                             |
| `blocked_domains`     | list or null | null         | Domain names to block for this request (subdomains matched too)                        |
| `solve_cloudflare`    | bool         | false        | Auto-solve Cloudflare Turnstile/Interstitial challenges |

With `extraction_type="snapshot"`, the response keeps `status` and `url` and returns one unchanged AI ARIA snapshot string in `content`. These snapshots always include element positions and sizes in viewport CSS pixels. `css_selector` must match exactly one element; omit it for the whole page. `main_content_only` and `pierce_shadow` do not filter snapshots. Snapshot extraction is only available on `browser_fetch`.

### `browser_snapshot` -- Read the current page without navigation

Returns a plain-text AI ARIA snapshot of the current whole page, including element roles, names, and references. Takes `session_id` from `browser_open` and optional `depth` to limit the tree. Element positions and sizes in viewport CSS pixels are included by default; set `boxes=false` to omit them. Use it after `browser_fetch` finishes. Raises for an unknown or HTTP session, or a missing, closed, or busy page.

Set `search` to nonempty text for a case-insensitive literal search. Set `regex=true` to treat it as a Python regular expression instead; regex matching is case-sensitive unless you use an inline flag such as `(?i)`. Regex mode requires `search`, and invalid patterns fail before capture. Omit `search` for the unchanged full snapshot.

Search applies to each line of the captured snapshot, after the `depth` limit. Results include all matching lines, three lines before and after each match, and parent nodes. Overlapping context appears once; `...` marks omitted lines. Refs and boxes are preserved. If no lines match, the result is an empty string. Search does not navigate or reload the page.

```json
{"session_id": "browser", "search": "Next"}
```

### `browser_actions` -- Chain mouse, field, keyboard, and wait actions

Runs actions in order on the existing page in a stealthy browser session. Call `browser_fetch` first. The flat `actions` list can mix any of the eleven action types below; use `browser_snapshot` when you need to inspect the page before choosing later actions.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `session_id` | str | required | ID of an open browser session |
| `actions` | list[object] | required | Nonempty ordered list; each item has a `type` and that type's fields |
| `slowly` | bool | false | Fresh random delays of 50-150 ms per typed character and 100-300 ms between all actions, including waits |

| Action `type` | Fields | Behavior |
|---------------|--------|----------|
| `move` | Target, `steps=1`, `timeout=30000` | Hover over an element or move to coordinates; `steps` is the number of coordinate mousemove events, at least 1, and is ignored for element targets |
| `click` | Target, `button="left"`, `click_count=1`, `delay=0`, `timeout=30000` | Click with the left, right, or middle button; `click_count` must be at least 1, with 2 for a double-click; `delay` is finite nonnegative milliseconds between press and release |
| `wheel` | `delta_x=0`, `delta_y=0` | Scroll at the current pointer position; finite CSS pixel deltas allow fractions and zero; positive moves right/down, negative moves left/up |
| `textbox` | Target, `value`, `clear=true`, `timeout=30000` | By default, replace text in an input, textarea, or contenteditable element with a string; an empty string clears it; `clear=false` types at the current caret or selection without clearing |
| `checkbox` | Target, `value`, `timeout=30000` | Boolean `true` checks the box; `false` unchecks it |
| `radio` | Target, `value`, `timeout=30000` | Select the radio option; `value` is required and only `true` is supported |
| `combobox` | Target, `value`, `timeout=30000` | Select native `<select>` options by label; use a string, a list of strings for multiple selections, or `[]` to clear |
| `press_key` | `key` | Press a nonempty native key name, character, or shortcut at the current focus |
| `wait_time` | `milliseconds` | Fixed pause in finite nonnegative milliseconds |
| `wait_element` | `target`, `state="visible"`, `timeout=30000` | Wait for an element to reach `"visible"`, `"hidden"`, `"attached"`, or `"detached"` |
| `wait_load` | `state`, `timeout=30000` | Wait for `"domcontentloaded"`, `"load"`, or `"networkidle"` |

**Targets and timing.** Element actions use a nonempty `target`: a Playwright selector such as `"#search"` or a snapshot reference as `"aria-ref=e2"`. Bare reference strings such as `"e2"` are treated as selectors. Each move or click needs either `target` or both `x` and `y`. Coordinates must be finite viewport CSS pixels from the main frame's top-left, not full-page screenshot coordinates. Field actions need `target` and can target fields anywhere on the page without a `<form>` parent. Element waits also use `target`. Mouse and field targets must match exactly one element. Use current snapshot references; do not build a chain with references that need a future snapshot.

Each action with a `timeout` accepts finite nonnegative milliseconds, default 30000; 0 disables the limit. Mouse coordinate actions ignore it. For text input, the limit applies separately to each native operation, including clearing and each character press in slow mode. Keyboard, wheel, and fixed-pause actions have no timeout option. Pauses between actions are outside action timeouts.

**Mouse actions.** Element targets use native locator hover or click, which waits for readiness and scrolls into view. Coordinate actions use the native mouse without automatic waiting or scrolling. Coordinate clicks move the mouse, then press and release, without waiting for navigation. Wheel actions neither move the pointer nor wait for scrolling, animations, or loaded content to finish. The page may prevent scrolling, or the scrollable area may be at its edge.

**Fields and keys.** Field actions use native locator `fill`, `press_sequentially`, `set_checked`, and `select_option(label=...)`. Combobox actions support native `<select>` elements, not custom dropdown widgets. With `clear=false`, text uses `press_sequentially` even when `slowly=false`; an empty value preserves existing content. With `slowly=true`, text clears first unless `clear=false`, then each character gets a fresh 50-150 ms delay. Every pair of actions also gets a fresh 100-300 ms pause, including explicit wait actions, with no leading or trailing pause.

Each `press_key` uses native `page.keyboard.press` at the current focus. Keep a shortcut such as `"ControlOrMeta+A"` in one `key` string, then use another `press_key` action with `"Backspace"` to delete. A space (`" "`) and plus (`"+"`) are valid key strings. The native API validates key names and shortcuts when pressed. Use a click action to focus the intended control before an Enter press when needed. Key presses do not wait for navigation.

**Waits.** Element waits are strict: multiple matches return an error. `attached` means present in the DOM, and `detached` means absent. `visible` requires a nonempty bounding box and no `visibility:hidden`; `hidden` also succeeds when the element is absent. Load waits observe the current committed document and return immediately if the state was already reached. A click or key press followed by `wait_load` does not guarantee waiting for delayed future navigation. `domcontentloaded` waits for DOMContentLoaded, not all future JavaScript work; `load` waits for the load event; `networkidle` requires no active network connections for at least 500 ms and does not prove application readiness. Prefer a specific result element when it signals readiness.

For example, fill and submit a search, wait for its results, then hover over the results panel and scroll it:

```json
{
  "session_id": "browser",
  "actions": [
    {"type": "textbox", "target": "#search", "value": "books"},
    {"type": "press_key", "key": "Enter"},
    {"type": "wait_element", "target": "#results"},
    {"type": "move", "target": "#results"},
    {"type": "wheel", "delta_y": 500}
  ]
}
```

MCP validates the entire action schema, and all target combinations are checked before execution. Targets are resolved only when their action runs, so earlier actions can create later targets. One page stays reserved for the whole sequence, including waits and random pauses. The first runtime failure stops the chain and reports its one-based action number, type, and native error. Earlier effects remain, and the failed action itself may partly apply. Nothing is retried or rolled back. Cancellation also stops the chain and remains cancellation. A cancelled or timed-out click attempts to release its button while the page is open, preserving the original error if release fails. The page reservation is released after success, failure, or cancellation.

Returns `Actions completed.` as plain text without echoing field values or taking a snapshot. Use `browser_snapshot` before retrying after an error or when later actions depend on inspecting a page change. Unknown or HTTP sessions and missing, closed, or busy pages return an error.

### `browser_evaluate` -- Run JavaScript on the current page

Runs a native JavaScript expression or function on the existing page. Call `browser_open`, then `browser_fetch` first. Functions are invoked with the optional JSON object argument, and returned promises are awaited.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `session_id` | str | required | ID of an open browser session with a page |
| `expression` | str | required | Nonempty JavaScript expression or function to invoke |
| `arg` | object or null | null | One JSON object passed to the function; nested values can contain any JSON data |
| `isolated_context` | bool | true | Use a separate JavaScript context; `false` accesses the page's own variables |

The isolated context shares the page's DOM but does not share its JavaScript variables. Use `isolated_context=false` to access application globals.

For example, collect text from the first matching links:

```json
{
  "session_id": "browser",
  "expression": "({selector, limit}) => [...document.querySelectorAll(selector)].slice(0, limit).map(element => element.textContent)",
  "arg": {"selector": "a", "limit": 10}
}
```

Return JSON-compatible data: null, strings, booleans, finite numbers, arrays, or objects. Convert special objects such as DOM nodes, dates, maps, and sets into plain data in JavaScript. Both `null` and `undefined` return `null`. Circular data, non-finite numbers, and other results that cannot be encoded as JSON return an error.

The result is compact JSON in one `TextContent` block with `structured_output=False`: strings are JSON-quoted, arrays stay in one block, and null is retained. No automatic snapshot, navigation, reload, retry, or tool timeout is added.

The page stays reserved during evaluation and is released after success, failure, or cancellation. Scripts can change page state or make requests. Errors and cancellation do not undo those effects or guarantee that browser-side JavaScript stops. Use `browser_snapshot` or another read to check effects before repeating a script. Unknown or HTTP sessions and missing, closed, or busy pages return an error; JavaScript errors propagate.

### `browser_network_requests` -- Search recorded browser requests

Reads completed requests from a session opened with `browser_open`, across page loads, actions, tabs, and navigation. It does not navigate, reserve a page, or send requests. Recording starts automatically and saves response headers and supported text bodies. Completed HTTP 4xx and 5xx responses are included; failed and unfinished requests are omitted. The history retains up to 1,000 requests, with fixed limits of 1 MiB per response body and 20 MiB combined; old records are removed when retention limits are reached.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `session_id` | str | required | ID from `browser_open` |
| `url_pattern` | str or null | null | Regular expression to match request URLs |
| `include_static` | bool | false | Include all resource types; otherwise keep XHR/fetch and HTTP errors |
| `after_id` | int | 0 | Nonnegative cursor; return requests with larger IDs |
| `limit` | int | 50 | Maximum returned requests, from 1 to 200 |

Returns structured JSON with `requests`, `next_cursor`, `has_more`, and `dropped_count`. Each request contains integer `id` and `status` fields, plus string `url`, `method`, and `resource_type` fields. `dropped_count` counts older entries removed by the history limits.

Pass `next_cursor` as `after_id` to read later entries. `has_more` means more retained entries currently match the same filters. An empty result has `requests=[]` and `has_more=false`; `next_cursor` is the greater of `after_id` and the latest saved request ID. Use `include_static=true` to include successful document requests and saved redirects. Entries receive increasing IDs when capture finishes. Reads do not wait for captures; use browser actions to wait for the page when needed.

Both network tools provide an MCP output schema and `structured_content`. The SDK also returns the JSON in a text block for clients that read text content.

### `browser_network_request` -- Inspect one recorded request

Reads one recorded request without navigating, reserving a page, or sending it again. All parts use saved data, which remains available after page changes and temporary-context closure. Reads do not call browser methods. An entry appears only after its response has been converted and saved.

The recorder reads and saves response bodies only for supported text `Content-Type` values: `text/*`, `+json`/`+xml` types (including SVG), JSON, XML, JavaScript, GraphQL, and URL-encoded form data. Binary or unrecognized types, and responses without `Content-Type`, keep their metadata but no body bytes. The browser still loads resources normally.

Saved response bytes come from Playwright and can differ from the server's original bytes. Recorded text uses UTF-8 when the saved bytes are valid UTF-8, matching Playwright; otherwise it uses the declared charset. Response headers stay unchanged.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `session_id` | str | required | ID from `browser_open` |
| `request_id` | int | required | Positive recorded request ID from `browser_network_requests` |
| `part` | str | `"summary"` | `"summary"`, `"request_headers"`, `"request_body"`, `"response_headers"`, or `"response_body"` |

Returns structured JSON with `request_id`, `part`, `data`, and `note`.

- Summary `data` is an object with `id`, `url`, `method`, `resource_type`, and `status`.
- Header `data` is an object of header names and values. Partial headers keep that object and add a `note`.
- Body `data` is the full saved text for any text resource type, including documents and API calls. JSON response bodies stay strings; they are not parsed into objects.

Saved empty text, HEAD responses, and status codes 204, 205, and 304 return `data=""` and `note=null`. Missing, unreadable, oversized, or non-text body data returns `data=null` and a `note` with the reason. Skipped non-text responses use `Non-text body; not saved.`. A missing or evicted request ID returns an error.

Saved response data survives browser cleanup. Closing a session does not wait for captures; captures still running at navigation or closure may be omitted. The limits cover retained request entries and response bytes, not total browser memory, concurrent captures, temporary full-body reads, parsed HTML, or request bodies.

Both network tools reject unknown or HTTP sessions. Read needed details before `close_session`, which removes the MCP session.

### `session_make_request` -- HTTP request through an open requests session

Makes an HTTP request (any method) through a session opened with `open_request_session`, reusing its cookies, connections, and browser fingerprint across calls. Same parameters as `make_request` plus a required `session_id`, minus the session-level `impersonate`, `proxy`, and `proxy_auth`. Raises on a browser session.

### `close_session` -- Close a persistent session

Closes a session (browser or requests) and frees its resources. Always close sessions when done.

| Parameter    | Type | Default  | Description                      |
|--------------|------|----------|----------------------------------|
| `session_id` | str  | required | Session ID from `browser_open`   |

Returns a `SessionClosedModel` with `session_id` and `message`.

### `list_sessions` -- List active sessions

Returns a list of `SessionInfo` objects, each with `session_id`, `session_type`, `created_at`, `is_alive`, and `settings` (same as `browser_open` returns).

No parameters.

### `browser_screenshot` -- Capture the current page or an element

Captures the existing page or one element without reloading or navigating. Element capture can scroll the target into view. Returns an MCP `ImageContent` block followed by a `TextContent` block with the current page URL. The tool uses `structured_output=False`, so the model receives real image content rather than image data duplicated in a structured JSON result.

Call `browser_open`, then `browser_fetch` to open a page first. Use `browser_actions` for waits or interactions before capture; this tool does not accept a URL or readiness controls.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `session_id` | str | required | ID of an open browser session with a page |
| `selector` | str or null | null | Nonempty Playwright selector for one element; cannot combine with `ref` |
| `ref` | str or null | null | Nonempty current snapshot reference, such as `e2`; cannot combine with `selector` |
| `image_type` | `"png"` / `"jpeg"` | `"png"` | Image format; JPEG allows smaller payloads |
| `full_page` | bool | false | Capture the full scrollable page; cannot combine with an element target |
| `quality` | int or null | null | JPEG quality 0-100; an error if supplied for PNG |
| `timeout` | number | 30000 | Finite nonnegative capture timeout in milliseconds; 0 disables it |

Omit both `selector` and `ref` for the viewport or full-page capture. For an element, pass exactly one target and leave `full_page=false`. Native element capture requires exactly one match, waits for the element to be ready, and may scroll it into view. Refresh stale references with `browser_snapshot`.

The element image is clipped to its bounding box. A scrollable container includes only its currently visible contents, not all content inside it. Content covered by another element stays covered in the image.

For example, capture a result card through its selector:

```json
{"session_id": "browser", "selector": "#result-card"}
```

Or use a reference from the current snapshot:

```json
{"session_id": "browser", "ref": "e2"}
```

The page stays reserved during capture and is released after success, failure, or cancellation. Unknown or HTTP sessions and missing, closed, or busy pages return an error. Capture errors propagate.

## Tool selection guide

| Scenario                                 | Tool                                                          |
|------------------------------------------|---------------------------------------------------------------|
| Single static page or API request | `make_request` |
| Single JavaScript-rendered / SPA page | `browser_fetch_once` |
| Single page with Cloudflare protection | `browser_fetch_once` with `solve_cloudflare=true` |
| Related HTTP requests | `open_request_session` + `session_make_request` per URL |
| Browser automation or network history | `browser_open` + `browser_fetch` per URL |
| Capture the current page or an element   | `browser_screenshot` after `browser_open` + `browser_fetch` |
| Read the current page's AI ARIA snapshot  | `browser_snapshot` with `session_id`                          |
| Chain mouse, field, keyboard, or wait actions | `browser_actions` with `session_id`                       |
| Custom JavaScript extraction or page tasks | `browser_evaluate` with `session_id`                        |
| Find API calls, HTTP errors, or redirects  | `browser_network_requests` with `session_id`                |
| Read recorded request headers or body data | `browser_network_request` with `session_id` and `request_id` |

Start with `make_request` for a standalone HTTP request, then use `browser_fetch_once` if JavaScript rendering is needed or HTTP requests are blocked. Enable `solve_cloudflare` for Cloudflare challenges. Use persistent sessions for related requests, browser actions, screenshots, or network history. Reuse the session and fetch URLs in order. Always call `close_session` when done with a persistent session.

## Content extraction tips

- Use `css_selector` to narrow results before they reach the model -- this saves significant tokens.
- `main_content_only=true` (default) restricts HTML, Markdown, and text extraction to `<body>`.
- `extraction_type="markdown"` (default) is best for readability. Use `"text"` for minimal output, `"html"` when structure matters.
- If a `css_selector` matches multiple elements, HTML, Markdown, and text extraction return all matches in the `content` list. Snapshot extraction requires exactly one match.

## Prompt injection protection

For HTML, Markdown, and text extraction, `main_content_only=true` (the default) sanitizes scraped content to prevent prompt injection from malicious websites. It strips:

- CSS-hidden elements (`display:none`, `visibility:hidden`, `opacity:0`, `font-size:0`, `height:0`, `width:0`)
- `aria-hidden="true"` elements
- `<template>` tags
- HTML comments
- Zero-width unicode characters

Keep `main_content_only=true` for maximum protection.

## Ad blocking

The `browser_fetch_once` tool and browser sessions opened with `browser_open` automatically block requests to ~3,500 known ad and tracker domains. This is always enabled in the MCP server to save tokens and speed up page loads. No configuration needed.

## Setup

Start the server (stdio transport, used by most MCP clients):

```bash
scrapling-mcp
```

**Note:** The `scrapling-mcp` command was added in v0.4.13 as a shortcut that maps directly to `scrapling mcp`, making it easier to add Scrapling to MCP registries and clients that expect a single command. On older versions, use the `scrapling` command with `mcp` as the first argument instead.

Or with Streamable HTTP transport:

```bash
scrapling-mcp --http
scrapling-mcp --http --host 0.0.0.0 --port 8000
```

The host defaults to `127.0.0.1`, so the server only accepts connections from the same machine. Pass `--host 0.0.0.0` to make it reachable from the network.

Docker alternative:

```bash
docker pull pyd4vinci/scrapling
docker run -i --rm pyd4vinci/scrapling mcp
```

That runs the stdio transport. To use Streamable HTTP inside Docker, bind to `0.0.0.0` yourself and set a token, since the container's `127.0.0.1` is not reachable through the published port:

```bash
docker run -p 8000:8000 -e SCRAPLING_MCP_AUTH_TOKEN="<your-token>" pyd4vinci/scrapling mcp --http --host 0.0.0.0
```

## Custom browser executable

The `browser_fetch_once` and `browser_open` tools can use a custom Chromium-compatible browser executable instead of the bundled Chromium. This is useful for custom browser builds or lightweight browser engines.

To configure it once for the whole MCP server, pass the executable path when starting the server:

```bash
scrapling-mcp --executable-path "/path/to/chromium"
```

In a Claude Desktop configuration, add the option to the server arguments:

```json
{
  "mcpServers": {
    "ScraplingServer": {
      "command": "/Users/<MyUsername>/.venv/bin/scrapling-mcp",
      "args": [
        "--executable-path",
        "/path/to/chromium"
      ]
    }
  }
}
```

You can also set the `SCRAPLING_EXECUTABLE_PATH` environment variable before starting the server. Pass `executable_path` to `browser_fetch_once` or `browser_open` when a single fetch or session needs a different browser executable. The `scrapling extract fetch` and `scrapling extract stealthy-fetch` CLI commands support the same `--executable-path` option and environment variable fallback.

The MCP server name when registering with a client is `ScraplingServer`. The command is the path to the `scrapling-mcp` binary with no arguments (or the `scrapling` binary with `mcp` as the argument on versions before 0.4.13).

## Connecting to remote browsers

`browser_open` doesn't have to launch a browser locally. Pass a `cdp_url` and it connects to an already-running browser through the Chrome DevTools Protocol, whether that browser is on the same machine, another host, or a managed browser provider. The `session_id` you get back is used with `browser_fetch`, `browser_snapshot`, `browser_actions`, `browser_evaluate`, `browser_screenshot`, `browser_network_requests`, and `browser_network_request` as usual.

The URL can be a WebSocket endpoint (`ws://`/`wss://`), which is what managed browser providers hand out, or the HTTP endpoint of a browser started with `--remote-debugging-port=9222`, reached as `cdp_url="http://localhost:9222"`.

**Notes:**

- The browser is already running, so options that only apply while launching one are ignored for CDP sessions: `headless`, `real_chrome`, and `executable_path` (including the server-wide default).
- Everything else still applies (`locale`, `useragent`, `proxy`, `cookies`, `timezone_id`, and so on), as each session creates its own browser context on the remote browser.

## Authentication

The stdio transport is only reachable by the program that started it, but with Streamable HTTP anyone who can reach the port can call every tool, including fetching any URL from the machine running the server. That's why Streamable HTTP requires authentication, so `--http` on its own refuses to start and asks you for a token:

```bash
scrapling-mcp --http --auth-token "$(openssl rand -hex 32)"
```

Clients then have to send that token in an `Authorization` header, and any request without it is rejected with a `401`:

```json
{
  "mcpServers": {
    "ScraplingServer": {
      "url": "https://your-server.example.com/mcp",
      "headers": {
        "Authorization": "Bearer <your-token>"
      }
    }
  }
}
```

Passing the token on the command line leaves it in the shell history and the process list, so prefer the `SCRAPLING_MCP_AUTH_TOKEN` environment variable:

```bash
export SCRAPLING_MCP_AUTH_TOKEN="<your-token>"
scrapling-mcp --http
```

If you really want an unauthenticated server, for example while testing locally on the default `127.0.0.1`, you have to ask for it with `--no-auth`:

```bash
scrapling-mcp --http --no-auth
```

Combining `--no-auth` with `--host 0.0.0.0` leaves every tool open to anyone who can reach the port, so avoid that pair outside a trusted network.

When the server listens on a public address, also tell it which host names to accept, which turns on protection against DNS-rebinding attacks. The option can be repeated:

```bash
scrapling-mcp --http --allowed-host 'your-server.example.com:8000'
```

**Notes:**

- Authentication applies to the Streamable HTTP transport only. It's ignored with stdio, and the server logs a warning to say so.
- Plain HTTP sends the token in cleartext, so put the server behind a reverse proxy that terminates TLS before exposing it to the internet.
- This is a single shared key, not per-client credentials, so every client uses the same token and rotating it means restarting the server.
- Starting with `--http --no-auth` still logs a warning that it's unauthenticated.
- Passing both `--auth-token` and `--no-auth` keeps the token, so the server stays authenticated instead of quietly dropping it.
