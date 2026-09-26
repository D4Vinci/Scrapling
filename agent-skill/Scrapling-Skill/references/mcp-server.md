# Scrapling MCP Server

The Scrapling MCP server exposes seventeen tools over the MCP protocol. It supports CSS-selector-based content narrowing (reducing tokens by extracting only relevant elements before returning results), three levels of scraping capability (plain HTTP, browser-rendered, and stealth/anti-bot bypass), persistent browser session management, mouse actions, batch field filling, keyboard shortcuts, and page screenshots returned as real image content blocks. Fetch tools come in two modes: one-shot tools (`browser_fetch_once`, `browser_fetch_many_once`, `browser_stealth_fetch_once`, `browser_stealth_fetch_many_once`) each launch and close their own browser, while `browser_fetch` and `session_make_request` work through sessions opened with `browser_open`/`open_request_session`.

Fetch and HTTP request tools return a `ResponseModel` with fields: `status` (int), `content` (list of strings), `url` (str). Bulk tools return a list of these responses. The `browser_screenshot` tool returns a list of MCP content blocks: an `ImageContent` (the screenshot bytes) followed by a `TextContent` (the post-redirect URL). `browser_snapshot`, `browser_mouse`, `browser_fill_fields`, and `browser_press_key` return plain text.

## Shadow DOM

Set `pierce_shadow=true` on `browser_fetch_once`, `browser_fetch_many_once`, `browser_stealth_fetch_once`, `browser_stealth_fetch_many_once`, or `browser_fetch` to include open Shadow DOM content. It defaults to `false`. For persistent sessions, pass it on each `browser_fetch` call. See [Shadow DOM](fetching/dynamic.md#shadow-dom) for selector examples and limits.


## One-shot tools

### `make_request` -- HTTP request, any method (single URL)

Fast HTTP request with browser fingerprint impersonation (TLS, headers). Supports GET (default), POST, PUT, and DELETE via the `method` parameter. Suitable for static pages with no/low bot protection.

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
| `retries`           | int                                       | 3            | Retry attempts on failure                                          |
| `retry_delay`       | int                                       | 1            | Seconds between retries                                            |
| `stealthy_headers`  | bool                                      | true         | Generate realistic browser headers and Google referer              |
| `http3`             | bool                                      | false        | Use HTTP/3 (may conflict with `impersonate`)                       |
| `follow_redirects`  | bool or "safe"                            | "safe"       | Follow redirects. "safe" rejects redirects to internal/private IPs |
| `max_redirects`     | int                                       | 30           | Max redirects (-1 for unlimited)                                   |
| `headers`           | dict or null                              | null         | Custom request headers                                             |
| `cookies`           | dict or null                              | null         | Request cookies                                                    |
| `params`            | dict or null                              | null         | Query string parameters                                            |
| `verify`            | bool                                      | true         | Verify HTTPS certificates                                          |

### `bulk_get` -- HTTP GET request (multiple URLs)

Async concurrent GET-only version of `make_request`. Same parameters except `url` is replaced by `urls` (list of strings) and there are no `method`/`data`/`json` parameters. All URLs are fetched in parallel. Returns a list of `ResponseModel`.

### `browser_fetch_once` -- Browser fetch (single URL)

Opens a Chromium browser via Playwright to render JavaScript. Suitable for dynamic/SPA pages with no/low bot protection.

**Key parameters (beyond shared ones):**

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

This is a one-shot tool: it always launches its own browser. To fetch through a persistent session, use `browser_fetch`.

### `browser_fetch_many_once` -- Browser fetch (multiple URLs)

Concurrent browser version of `browser_fetch_once`. Same parameters except `url` is replaced by `urls` (list of strings). Each URL opens in a separate browser tab. Returns a list of `ResponseModel`.

### `browser_stealth_fetch_once` -- Stealth browser fetch (single URL)

Anti-bot bypass fetcher with fingerprint spoofing. Use this for sites with Cloudflare Turnstile/Interstitial or other strong protections.

**Additional parameters (beyond those in `browser_fetch_once`):**

| Parameter          | Type         | Default | Description                                                      |
|--------------------|--------------|---------|------------------------------------------------------------------|
| `solve_cloudflare` | bool         | false   | Automatically solve Cloudflare Turnstile/Interstitial challenges |
| `hide_canvas`      | bool         | false   | Add noise to canvas operations to prevent fingerprinting         |
| `block_webrtc`     | bool         | false   | Force WebRTC to respect proxy settings (prevents IP leak)        |
| `allow_webgl`      | bool         | true    | Keep WebGL enabled (disabling is detectable by WAFs)             |
| `additional_args`  | dict or null | null    | Extra Playwright context args (overrides Scrapling defaults)     |

All parameters from `browser_fetch_once` are also accepted. Like `browser_fetch_once`, this is a one-shot tool that launches its own browser; use `browser_fetch` for a stealthy session.

### `browser_stealth_fetch_many_once` -- Stealth browser fetch (multiple URLs)

Concurrent stealth version. Same parameters as `browser_stealth_fetch_once` except `url` is replaced by `urls` (list of strings). Returns a list of `ResponseModel`.

## Session tools

### `browser_open` -- Create a persistent browser session

Opens a browser session that stays alive across multiple `browser_fetch` calls, avoiding the overhead of launching a new browser each time. It holds the browser-level configuration only; per-request options are passed to `browser_fetch`. For plain HTTP requests without a browser, use `open_request_session` instead. Returns a `SessionCreatedModel` with `session_id`, `session_type`, `created_at`, `is_alive`, `settings` (the session's effective configuration for the AI agent; empty for CDP sessions), and `message`.

**Key parameters:**

| Parameter          | Type                        | Default      | Description                                                                                           |
|--------------------|-----------------------------|--------------|-------------------------------------------------------------------------------------------------------|
| `session_type`     | `"dynamic"` / `"stealthy"`  | required     | Type of browser session to create                                                                     |
| `session_id`       | str or null                 | null         | Custom ID for the session. If omitted, a random 12-char hex ID is generated. Raises if already in use |
| `headless`         | bool                        | true         | Run browser hidden or visible                                                                         |
| `hide_canvas`      | bool                        | false        | (Stealthy only) Canvas fingerprint noise                                                              |
| `block_webrtc`     | bool                        | false        | (Stealthy only) Block WebRTC IP leak                                                                  |
| `allow_webgl`      | bool                        | true         | (Stealthy only) Keep WebGL enabled                                                                    |

Plus the other browser-level session parameters (`proxy`, `real_chrome`, `cdp_url`, `locale`, `timezone_id`, `useragent`, `cookies`, `executable_path`, `additional_args`). Per-request options (`timeout`, `wait`, `google_search`, `network_idle`, `disable_resources`, `wait_selector`, `wait_selector_state`, `extra_headers`, `solve_cloudflare`) are not set here; pass them to `browser_fetch`.

One `browser_fetch` works with either browser session type; `solve_cloudflare` only applies to a stealthy session.

### `open_request_session` -- Create a persistent HTTP requests session

Opens an HTTP session (no browser) that stays alive across multiple `session_make_request` calls, keeping cookies, connections, and the browser fingerprint between requests. Returns the same `SessionCreatedModel` receipt and shows in `list_sessions` as a `static` session.

| Parameter     | Type        | Default    | Description                                                                                           |
|---------------|-------------|------------|-------------------------------------------------------------------------------------------------------|
| `session_id`  | str or null | null       | Custom ID for the session. If omitted, a random 12-char hex ID is generated. Raises if already in use |
| `impersonate` | str         | `"chrome"` | Browser fingerprint to impersonate on every request                                                   |
| `proxy`       | str or null | null       | Proxy URL used for every request, e.g. `"http://user:pass@host:port"`                                 |

### `browser_fetch` -- Fetch through an open browser session (single URL)

Fetches one URL through a browser session opened with `browser_open` (dynamic or stealthy). The session holds the browser-level configuration; every parameter here applies to this request only. Raises on a requests session; use `session_make_request` there instead.

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
| `solve_cloudflare`    | bool         | false        | (Stealthy sessions only) Auto-solve Cloudflare challenges; errors on a dynamic session |

With `extraction_type="snapshot"`, the response keeps `status` and `url` and returns one unchanged AI ARIA snapshot string in `content`. These snapshots always include element positions and sizes in viewport CSS pixels. `css_selector` must match exactly one element; omit it for the whole page. `main_content_only` and `pierce_shadow` do not filter snapshots. Snapshot extraction is only available on `browser_fetch`.

### `browser_snapshot` -- Read the current page without navigation

Returns a plain-text AI ARIA snapshot of the current whole page, including element roles, names, and references. Takes `session_id` from `browser_open` and optional `depth` to limit the tree. Element positions and sizes in viewport CSS pixels are included by default; set `boxes=false` to omit them. Use it after `browser_fetch` finishes. Raises for an unknown or HTTP session, or a missing, closed, or busy page.

### `browser_mouse` -- Chain mouse moves, hovers, clicks, and scrolling

Runs native mouse actions in order on the existing page in a dynamic or stealthy browser session. Call `browser_fetch` first. Use `browser_snapshot` to find current references or coordinates.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `session_id` | str | required | ID of an open browser session |
| `actions` | list[object] | required | Nonempty ordered list of `move`, `click`, or `wheel` actions |

| Action `type` | Fields | Behavior |
|---------------|--------|----------|
| `move` | Target, `steps=1`, `timeout=30000` | Hover over an element or move to coordinates; `steps` is the number of coordinate mousemove events, at least 1, and is ignored for element targets |
| `click` | Target, `button="left"`, `click_count=1`, `delay=0`, `timeout=30000` | Click with the left, right, or middle button; `click_count` must be at least 1, with 2 for a double-click; `delay` is finite nonnegative milliseconds between press and release |
| `wheel` | `delta_x=0`, `delta_y=0` | Scroll at the current pointer position; finite CSS pixel deltas allow fractions and zero; positive moves right/down, negative moves left/up |

Each move or click needs exactly one target: a nonempty Playwright `selector`, a nonempty snapshot `ref` such as `"e2"`, or both `x` and `y`. Coordinates must be finite viewport CSS pixels measured from the main frame's top-left, not full-page screenshot coordinates. Selectors must match exactly one element. Refresh stale references with `browser_snapshot`.

Element targets use native locator hover or click, which waits for readiness and scrolls into view. Their per-action `timeout` is finite nonnegative milliseconds; 0 disables it. Coordinate actions use the native mouse without automatic waiting or scrolling and ignore `timeout`. Coordinate clicks move the mouse, then press and release, without waiting for navigation. Wheel actions neither move the pointer nor wait for scrolling, animations, or loaded content to finish. The page may prevent scrolling, or the scrollable area may be at its edge.

For example, hover over a panel and scroll it in one call:

```json
{
  "session_id": "browser",
  "actions": [
    {"type": "move", "selector": "#results"},
    {"type": "wheel", "delta_y": 500}
  ]
}
```

The whole list is validated before execution, and the page stays reserved for the full sequence. The first action error stops the batch and reports its one-based action number, type, and native error. Cancellation also stops the batch and remains cancellation. Earlier actions stay in effect and are never retried. A cancelled or timed-out click attempts to release the button while the page is open; this does not undo the click. The page reservation is released after success, error, or cancellation.

Returns `Mouse actions completed.` as plain text without a snapshot. Use `browser_snapshot` before retrying after an error or when the next action depends on a page change. Invalid targets, unknown or HTTP sessions, and missing, closed, or busy pages return an error.

### `browser_fill_fields` -- Fill one or more page fields in order

Fills fields anywhere on the existing page in a dynamic or stealthy browser session. Fields do not need a `<form>` parent. Call `browser_fetch` first. Each field needs exactly one nonempty `selector` or snapshot `ref`, plus its `type` and `value`.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `session_id` | str | required | ID of an open browser session |
| `fields` | list[object] | required | Nonempty ordered list of field targets, types, and values |
| `timeout` | number | 30000 | Finite nonnegative timeout in milliseconds per operation; 0 disables the limit |
| `slowly` | bool | false | Add fresh random delays: 50-150 ms per character, 100-300 ms between fields |

| Field `type` | `value` | Behavior |
|--------------|---------|----------|
| `textbox` | str | By default, replace text in an input, textarea, or contenteditable element; an empty string clears it |
| `checkbox` | bool | `true` checks the box; `false` unchecks it |
| `radio` | `true` | Select the radio option; `false` is not supported |
| `combobox` | str or list[str] | Select native `<select>` options by label; use a list for multiple selections or `[]` to clear |

Textbox fields also accept `clear` (bool, default `true`). With `clear=false`, native `press_sequentially` types at the current caret or selection without clearing first, even when `slowly=false`. An empty value preserves existing content when `clear=false`; otherwise it clears the field.

Selectors must match exactly one element. Use current snapshot references, such as `"e2"`. MCP validates all field types and values before execution, and target combinations are checked before reserving the page. One page stays reserved for the whole batch. Native locator `fill`, `press_sequentially`, `set_checked`, and `select_option(label=...)` run in list order. Combobox fields support native `<select>` elements, not custom dropdown widgets.

With `slowly=true`, native `press_sequentially` types each character with a fresh random delay of 50-150 ms, clearing first unless the field has `clear=false`. All field types get a fresh random pause of 100-300 ms before the next field, with no pause before the first or after the last. The timeout applies separately to each native action, including clearing and each character press; pauses between fields are outside it.

Returns `Fields filled.` as plain text without echoing values, submitting forms, or taking a snapshot. An error or cancellation stops the remaining fields; completed changes stay and are not retried. The page reservation is released afterward. Use `browser_snapshot` to check the page before retrying. To submit with Enter, use `browser_press_key` with `keys=["Enter"]`; first focus the intended control with a `browser_mouse` click action if needed, since the batch may end on another field. Unknown or HTTP sessions and missing, closed, or busy pages return an error.

### `browser_press_key` -- Chain keys and shortcuts at the current focus

Presses each item in order through native `page.keyboard.press` on the existing page in a dynamic or stealthy browser session. The page stays reserved for the full sequence. Call `browser_fetch` first. Use a `browser_mouse` click action to focus a control before pressing when needed; later presses follow any focus changes caused by earlier ones.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `session_id` | str | required | ID of an open browser session |
| `keys` | list[str] | required | Nonempty ordered list of nonempty native key names, characters, or shortcuts |

Use `["ControlOrMeta+A", "Backspace"]` to select all with the platform's modifier and then delete, or `["Tab", "Enter"]` to move focus and activate a control. Keep a shortcut in one item; separate items are separate presses. Use `["Escape"]` for one press; a space (`" "`) and plus (`"+"`) are valid list items. MCP validates the whole list and its string items before execution; the native API validates each key name or shortcut when pressed.

Returns `Keys pressed.` as plain text without an automatic snapshot or a wait for navigation. An error or cancellation stops the remaining presses; completed actions are not undone or retried. The page reservation is released after success, failure, or cancellation. Use `browser_snapshot` to check partial effects before retrying. Invalid keys, unknown or HTTP sessions, and missing, closed, or busy pages return an error.

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

### `browser_screenshot` -- Capture a page screenshot

Navigates to a URL inside an existing browser session and returns the screenshot as an MCP `ImageContent` block (the bytes the model can see directly, not a base64 string in JSON) followed by a `TextContent` block carrying the post-redirect URL.

Requires an open browser session. Call `browser_open` first, then pass the `session_id` here. Both `dynamic` and `stealthy` sessions are accepted.

| Parameter             | Type                  | Default      | Description                                                                          |
|-----------------------|-----------------------|--------------|--------------------------------------------------------------------------------------|
| `url`                 | str                   | required     | URL to navigate to and capture                                                       |
| `session_id`          | str                   | required     | ID of an open browser session created with `browser_open`                            |
| `image_type`          | `"png"` / `"jpeg"`    | `"png"`      | Image format. Use `"jpeg"` for smaller payloads                                      |
| `full_page`           | bool                  | false        | Capture the full scrollable page instead of just the viewport                        |
| `quality`             | int or null           | null         | JPEG quality 0-100. Raises if passed with `image_type="png"`                         |
| `wait`                | number                | 0            | Extra wait (ms) after page load before capture                                       |
| `wait_selector`       | str or null           | null         | CSS selector to wait for before capture                                              |
| `wait_selector_state` | str                   | `"attached"` | State for `wait_selector`: `"attached"` / `"visible"` / `"hidden"` / `"detached"`    |
| `network_idle`        | bool                  | false        | Wait until no network activity for 500ms                                             |
| `timeout`             | number                | 30000        | Timeout in milliseconds                                                              |

## Tool selection guide

| Scenario                                 | Tool                                                          |
|------------------------------------------|---------------------------------------------------------------|
| Static page, no bot protection           | `make_request`                                                |
| Multiple static pages                    | `bulk_get`                                                    |
| JavaScript-rendered / SPA page           | `browser_fetch_once`                                                       |
| Multiple JS-rendered pages               | `browser_fetch_many_once`                                                  |
| Cloudflare or strong anti-bot protection | `browser_stealth_fetch_once` (with `solve_cloudflare=true` for Turnstile) |
| Multiple protected pages                 | `browser_stealth_fetch_many_once`                                         |
| Multiple pages from the same site        | `browser_open` + `browser_fetch` per page                     |
| Multiple plain HTTP requests to one site | `open_request_session` + `session_make_request` per request   |
| Need a screenshot of a page              | `browser_open` + `browser_screenshot` with `session_id`               |
| Read the current page's AI ARIA snapshot  | `browser_snapshot` with `session_id`                          |
| Move, hover, click, or scroll in order    | `browser_mouse` with `session_id`                          |
| Fill one or more page fields in order   | `browser_fill_fields` with `session_id`                      |
| Chain keys or keyboard shortcuts         | `browser_press_key` with `session_id`                      |

Start with `make_request` (fastest, lowest resource cost). Escalate to `browser_fetch_once` if content requires JS rendering. Escalate to `browser_stealth_fetch_once` only if blocked. For multiple pages from the same site, use a persistent session to avoid browser launch overhead.

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

All browser-based tools (`browser_fetch_once`, `browser_fetch_many_once`, `browser_stealth_fetch_once`, `browser_stealth_fetch_many_once`) and persistent sessions (`browser_open`) automatically block requests to ~3,500 known ad and tracker domains. This is always enabled in the MCP server to save tokens and speed up page loads. No configuration needed.

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

Browser-based tools (`browser_fetch_once`, `browser_fetch_many_once`, `browser_stealth_fetch_once`, `browser_stealth_fetch_many_once`, and `browser_open`) can use a custom Chromium-compatible browser executable instead of the bundled Chromium. This is useful for custom browser builds or lightweight browser engines.

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

You can also set the `SCRAPLING_EXECUTABLE_PATH` environment variable before starting the server. Tool calls can still pass `executable_path` directly when a single request or session needs a different browser executable. The `scrapling extract fetch` and `scrapling extract stealthy-fetch` CLI commands support the same `--executable-path` option and environment variable fallback.

The MCP server name when registering with a client is `ScraplingServer`. The command is the path to the `scrapling-mcp` binary with no arguments (or the `scrapling` binary with `mcp` as the argument on versions before 0.4.13).

## Connecting to remote browsers

`browser_open` doesn't have to launch a browser locally. Pass a `cdp_url` and it connects to an already-running browser through the Chrome DevTools Protocol, whether that browser is on the same machine, another host, or a managed browser provider. Both session types (`dynamic` and `stealthy`) accept it, and the `session_id` you get back is used with `browser_fetch`, `browser_snapshot`, `browser_mouse`, `browser_fill_fields`, `browser_press_key`, and `browser_screenshot` as usual.

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
