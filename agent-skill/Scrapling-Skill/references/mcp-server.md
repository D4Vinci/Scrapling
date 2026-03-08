# Scrapling MCP Server

The Scrapling MCP server exposes six web scraping tools over the MCP protocol. It supports CSS-selector-based content narrowing (reducing tokens by extracting only relevant elements before returning results) and three levels of scraping capability: plain HTTP, browser-rendered, and stealth (anti-bot bypass).

All tools return a `ResponseModel` with fields: `status` (int), `content` (list of strings), `url` (str).

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
| `follow_redirects`  | bool                               | true         | Follow HTTP redirects                                              |
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

### `bulk_fetch` -- Browser fetch (multiple URLs)

Concurrent browser version of `fetch`. Same parameters except `url` is replaced by `urls` (list of strings). Each URL opens in a separate browser tab. Returns a list of `ResponseModel`.

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

All parameters from `fetch` are also accepted.

### `bulk_stealthy_fetch` -- Stealth browser fetch (multiple URLs)

Concurrent stealth version. Same parameters as `stealthy_fetch` except `url` is replaced by `urls` (list of strings). Returns a list of `ResponseModel`.

## Tool selection guide

| Scenario                                 | Tool                                                          |
|------------------------------------------|---------------------------------------------------------------|
| Static page, no bot protection           | `get`                                                         |
| Multiple static pages                    | `bulk_get`                                                    |
| JavaScript-rendered / SPA page           | `fetch`                                                       |
| Multiple JS-rendered pages               | `bulk_fetch`                                                  |
| Cloudflare or strong anti-bot protection | `stealthy_fetch` (with `solve_cloudflare=true` for Turnstile) |
| Multiple protected pages                 | `bulk_stealthy_fetch`                                         |

Start with `get` (fastest, lowest resource cost). Escalate to `fetch` if content requires JS rendering. Escalate to `stealthy_fetch` only if blocked.

## Content extraction tips

- Use `css_selector` to narrow results before they reach the model -- this saves significant tokens.
- `main_content_only=true` (default) strips nav/footer by restricting to `<body>`.
- `extraction_type="markdown"` (default) is best for readability. Use `"text"` for minimal output, `"html"` when structure matters.
- If a `css_selector` matches multiple elements, all are returned in the `content` list.

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