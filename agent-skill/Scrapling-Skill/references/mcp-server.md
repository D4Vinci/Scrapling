# Scrapling MCP Server

The Scrapling MCP server exposes nine web scraping tools over the MCP protocol. It supports CSS-selector-based content narrowing (reducing tokens by extracting only relevant elements before returning results), three levels of scraping capability (plain HTTP, browser-rendered, and stealth/anti-bot bypass), and persistent browser session management.

All scraping tools return a `ResponseModel` with fields: `status` (int), `content` (list of strings), `url` (str).

## Tools

### `get` -- HTTP request (single URL)

Fast HTTP GET with browser fingerprint impersonation (TLS, headers). Suitable for static pages with no/low bot protection.

**Key parameters:**

| Parameter           | Type                               | Default      | Description                                                        |
|---------------------|------------------------------------|--------------|--------------------------------------------------------------------|
| `url`               | str                                | required     | URL to fetch                                                       |
| `extraction_type`   | `"markdown"` / `"html"` / `"text"` | `"markdown"` | Output format                                                      |
| `css_selector`      | str or null                        | null         | CSS selector to narrow content (applied after `main_content_only`) |
| `main_content_only` | bool                               | true         | Restrict to `<body>` content                                       |
| `impersonate`       | str                                | `"chrome"`   | Browser fingerprint to impersonate                                 |
| `proxy`             | str or null                        | null         | Proxy URL, e.g. `"http://user:pass@host:port"`                     |
| `proxy_auth`        | dict or null                       | null         | `{"username": "...", "password": "..."}`                           |
| `auth`              | dict or null                       | null         | HTTP basic auth, same format as proxy_auth                         |
| `timeout`           | number                             | 30           | Seconds before timeout                                             |
| `retries`           | int                                | 3            | Retry attempts on failure                                          |
| `retry_delay`       | int                                | 1            | Seconds between retries                                            |
| `stealthy_headers`  | bool                               | true         | Generate realistic browser headers and Google referer       |
| `http3`             | bool                               | false        | Use HTTP/3 (may conflict with `impersonate`)                       |
| `follow_redirects`  | bool or "safe"                     | "safe"       | Follow redirects. "safe" rejects redirects to internal/private IPs |
| `max_redirects`     | int                                | 30           | Max redirects (-1 for unlimited)                                   |
| `headers`           | dict or null                       | null         | Custom request headers                                             |
| `cookies`           | dict or null                       | null         | Request cookies                                                    |
| `params`            | dict or null                       | null         | Query string parameters                                            |
| `verify`            | bool                               | true         | Verify HTTPS certificates                                          |

### `bulk_get` -- HTTP request (multiple URLs)

Async concurrent version of `get`. Same parameters except `url` is replaced by `urls` (list of strings). All URLs are fetched in parallel. Returns a list of `ResponseModel`.

### `fetch` -- Browser fetch (single URL)

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
| `disable_resources`   | bool                | false        | Block fonts, images, media, stylesheets, etc. for speed                         |
| `google_search`       | bool                | true         | Set a Google referer header                                            |
| `real_chrome`         | bool                | false        | Use locally installed Chrome instead of bundled Chromium                        |
| `cdp_url`             | str or null         | null         | Connect to existing browser via CDP URL                                         |
| `extra_headers`       | dict or null        | null         | Additional request headers                                                      |
| `useragent`           | str or null         | null         | Custom user-agent (auto-generated if null)                                      |
| `cookies`             | list or null        | null         | Playwright-format cookies                                                       |
| `timezone_id`         | str or null         | null         | Browser timezone, e.g. `"America/New_York"`                                     |
| `locale`              | str or null         | null         | Browser locale, e.g. `"en-GB"`                                                  |
| `session_id`          | str or null         | null         | Reuse a persistent session from `open_session` instead of creating a new browser |

### `bulk_fetch` -- Browser fetch (multiple URLs)

Concurrent browser version of `fetch`. Same parameters (including `session_id`) except `url` is replaced by `urls` (list of strings). Each URL opens in a separate browser tab. Returns a list of `ResponseModel`.

### `stealthy_fetch` -- Stealth browser fetch (single URL)

Anti-bot bypass fetcher with fingerprint spoofing. Use this for sites with Cloudflare Turnstile/Interstitial or other strong protections.

**Additional parameters (beyond those in `fetch`):**

| Parameter          | Type         | Default | Description                                                      |
|--------------------|--------------|---------|------------------------------------------------------------------|
| `solve_cloudflare` | bool         | false   | Automatically solve Cloudflare Turnstile/Interstitial challenges |
| `hide_canvas`      | bool         | false   | Add noise to canvas operations to prevent fingerprinting         |
| `block_webrtc`     | bool         | false   | Force WebRTC to respect proxy settings (prevents IP leak)        |
| `allow_webgl`      | bool         | true    | Keep WebGL enabled (disabling is detectable by WAFs)             |
| `additional_args`  | dict or null | null    | Extra Playwright context args (overrides Scrapling defaults)     |
| `session_id`       | str or null  | null    | Reuse a persistent stealthy session from `open_session`          |

All parameters from `fetch` are also accepted.

### `bulk_stealthy_fetch` -- Stealth browser fetch (multiple URLs)

Concurrent stealth version. Same parameters (including `session_id`) as `stealthy_fetch` except `url` is replaced by `urls` (list of strings). Returns a list of `ResponseModel`.

### `open_session` -- Create a persistent browser session

Opens a browser session that stays alive across multiple fetch calls, avoiding the overhead of launching a new browser each time. Returns a `SessionCreatedModel` with `session_id`, `session_type`, `created_at`, `is_alive`, and `message`.

**Key parameters:**

| Parameter          | Type                        | Default      | Description                                                         |
|--------------------|-----------------------------|--------------|---------------------------------------------------------------------|
| `session_type`     | `"dynamic"` / `"stealthy"`  | required     | Type of browser session to create                                   |
| `headless`         | bool                        | true         | Run browser hidden or visible                                       |
| `max_pages`        | int                         | 5            | Max concurrent browser tabs (1-50)                                  |
| `proxy`            | str or dict or null         | null         | Proxy for all requests in this session                              |
| `timeout`          | number                      | 30000        | Default timeout in ms                                               |
| `solve_cloudflare` | bool                        | false        | (Stealthy only) Auto-solve Cloudflare challenges                    |
| `hide_canvas`      | bool                        | false        | (Stealthy only) Canvas fingerprint noise                            |
| `block_webrtc`     | bool                        | false        | (Stealthy only) Block WebRTC IP leak                                |
| `allow_webgl`      | bool                        | true         | (Stealthy only) Keep WebGL enabled                                  |

Plus all other browser session parameters (`google_search`, `real_chrome`, `cdp_url`, `locale`, `timezone_id`, `useragent`, `extra_headers`, `cookies`, `disable_resources`, `network_idle`, `wait_selector`, `wait_selector_state`).

A dynamic session can only be used with `fetch`/`bulk_fetch`. A stealthy session can only be used with `stealthy_fetch`/`bulk_stealthy_fetch`.

### `close_session` -- Close a persistent browser session

Closes a session and frees its browser resources. Always close sessions when done.

| Parameter    | Type | Default  | Description                      |
|--------------|------|----------|----------------------------------|
| `session_id` | str  | required | Session ID from `open_session`   |

Returns a `SessionClosedModel` with `session_id` and `message`.

### `list_sessions` -- List active sessions

Returns a list of `SessionInfo` objects, each with `session_id`, `session_type`, `created_at`, and `is_alive`.

No parameters.

## Tool selection guide

| Scenario                                 | Tool                                                          |
|------------------------------------------|---------------------------------------------------------------|
| Static page, no bot protection           | `get`                                                         |
| Multiple static pages                    | `bulk_get`                                                    |
| JavaScript-rendered / SPA page           | `fetch`                                                       |
| Multiple JS-rendered pages               | `bulk_fetch`                                                  |
| Cloudflare or strong anti-bot protection | `stealthy_fetch` (with `solve_cloudflare=true` for Turnstile) |
| Multiple protected pages                 | `bulk_stealthy_fetch`                                         |
| Multiple pages from the same site        | `open_session` + `fetch`/`stealthy_fetch` with `session_id`  |

Start with `get` (fastest, lowest resource cost). Escalate to `fetch` if content requires JS rendering. Escalate to `stealthy_fetch` only if blocked. For multiple pages from the same site, use a persistent session to avoid browser launch overhead.

## Content extraction tips

- Use `css_selector` to narrow results before they reach the model -- this saves significant tokens.
- `main_content_only=true` (default) strips nav/footer by restricting to `<body>`.
- `extraction_type="markdown"` (default) is best for readability. Use `"text"` for minimal output, `"html"` when structure matters.
- If a `css_selector` matches multiple elements, all are returned in the `content` list.

## Prompt injection protection

When `main_content_only=true` (the default), the server automatically sanitizes scraped content to prevent prompt injection from malicious websites. It strips:

- CSS-hidden elements (`display:none`, `visibility:hidden`, `opacity:0`, `font-size:0`, `height:0`, `width:0`)
- `aria-hidden="true"` elements
- `<template>` tags
- HTML comments
- Zero-width unicode characters

Keep `main_content_only=true` for maximum protection.

## Ad blocking

All browser-based tools (`fetch`, `bulk_fetch`, `stealthy_fetch`, `bulk_stealthy_fetch`) and persistent sessions (`open_session`) automatically block requests to ~3,500 known ad and tracker domains. This is always enabled in the MCP server to save tokens and speed up page loads. No configuration needed.

## Setup

Start the server (stdio transport, used by most MCP clients):

```bash
scrapling mcp
```

Or with Streamable HTTP transport:

```bash
scrapling mcp --http
scrapling mcp --http --host 127.0.0.1 --port 8000
```

Docker alternative:

```bash
docker pull pyd4vinci/scrapling
docker run -i --rm scrapling mcp
```

The MCP server name when registering with a client is `ScraplingServer`. The command is the path to the `scrapling` binary and the argument is `mcp`.