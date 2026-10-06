# Scrapling MCP Server Guide

<iframe width="560" height="315" src="https://www.youtube.com/embed/qyFk3ZNwOxE?si=3FHzgcYCb66iJ6e3" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>

The **Scrapling MCP Server** is a new feature that brings Scrapling's powerful Web Scraping capabilities directly to your favorite AI chatbot or AI agent. This integration allows you to scrape websites, extract data, and bypass anti-bot protections conversationally through Claude's AI interface or any interface that supports MCP.

## Features

The Scrapling MCP Server provides fourteen tools for web scraping and browser interaction. One-shot tools fetch a single URL and close their own browser or client. Session tools keep cookies and settings across calls, so the AI can continue browser actions on the same tab and inspect network history.

### One-shot tools

#### 🚀 Basic HTTP Scraping
- **`make_request`**: Fast HTTP requests with any method (GET, POST, PUT, DELETE) and browser fingerprint impersonation, generating real browser headers matching the TLS version, HTTP/3, and more!

#### 🔒 Stealth Browser Scraping
- **`browser_fetch_once`**: Render JavaScript and scrape dynamic pages with our Stealthy browser. Supports fingerprint spoofing, Cloudflare Turnstile/Interstitial bypass, and control over the browser and request!

### Session tools

#### 🔌 Session Management
- **`browser_open`**: Create a persistent stealthy browser session that stays open across multiple `browser_fetch` calls, avoiding the overhead of launching a new browser each time. It holds the browser-level configuration and returns the session's effective `settings` for the AI agent (empty for CDP sessions).
- **`open_request_session`**: Create a persistent HTTP requests session (no browser) used with `session_make_request`, keeping cookies, connections, and the browser fingerprint (`impersonate`) between requests. It returns the same `settings` receipt and shows in `list_sessions` as a `static` session.
- **`close_session`**: Close a persistent session (browser or requests) and free its resources.
- **`list_sessions`**: List all active sessions with their details and `settings`.

#### 🎯 Fetching Through a Session
- **`browser_fetch`**: Render JavaScript and scrape a single URL through an open stealthy browser session, with fingerprint spoofing and Cloudflare Turnstile/Interstitial bypass. It can also capture a structured page snapshot with element references, positions, and sizes, helping the AI identify controls and plan mouse actions.
- **`session_make_request`**: Make fast HTTP requests with any method (GET, POST, PUT, DELETE), browser fingerprint impersonation, matching browser headers, and HTTP/3 support. Reuse cookies, connections, and the browser fingerprint through a session opened with `open_request_session`.

#### 📸 Screenshots

- **`browser_screenshot`**: Capture the current page or a chosen element as PNG or JPEG without reloading it. Inspect filled fields, open menus, charts, or result cards, with less unrelated content in element captures. Supports the visible viewport, the full page, or one element, with adjustable JPEG quality. The screenshot is returned as a real image content block the model can see directly.

#### AI Snapshots

- **`browser_snapshot`**: Give the AI a structured text view of the current page without reloading it. Includes element roles, names, references, positions, and sizes to help the AI understand the page and target clicks. Search for text to return matching lines with nearby context and parent nodes, making large pages easier to inspect.

#### Browser Actions

- **`browser_actions`**: Chain mouse actions, field filling, keyboard shortcuts, and waits in one call. For example, fill a search box, submit it, wait for results, and open a result. The AI can combine known steps while keeping snapshots separate when it needs to inspect a page change.

    Reveal hover menus and tooltips, click buttons and links, or move over a nested panel and scroll it vertically or horizontally. Moves and clicks support selectors, snapshot references, or coordinates, with automatic waiting and scrolling into view for element targets. Supports coordinate movement in multiple steps, left, right, and middle clicks, plus double-clicks.

    Target fields anywhere on the page through selectors or snapshot references. Fill text, check or uncheck boxes, select radio buttons, and choose one or more native dropdown options by their visible labels. Text can replace existing content, clear it, or continue at the current caret. Keyboard shortcuts can select and delete text, move focus, submit forms, or dismiss menus. Slow mode types one character at a time with random pauses between characters and all actions.

    Wait for results to appear, loading overlays to disappear, or page load events before the next action. Also supports fixed pauses and waiting for network activity to settle.

#### JavaScript

- **`browser_evaluate`**: Run JavaScript on the current page for custom data extraction, calculations, and page-specific tasks. The AI can collect data from several elements, read application state, or update page content. Supports asynchronous scripts and returns their results as JSON.

#### Network History

- **`browser_network_requests`**: Find completed requests across tabs, page loads, and browser actions. Discover the API calls behind a page's data, inspect HTTP errors, and follow saved redirects. Static resources are hidden by default to keep results small. Returns request details as JSON, with pagination for long histories.
- **`browser_network_request`**: Inspect one recorded request's summary, headers, sent data, or text response body as structured JSON. Returns the selected part in full without loading the page or sending the request again. Saved responses remain available after page changes. Size limits keep the history bounded; a note explains non-text, oversized, or unreadable bodies. Read needed details before closing the MCP session.

Response bodies are read and saved only for supported text `Content-Type` values, such as HTML, JSON, XML, or JavaScript. Binary, missing, or unrecognized content types keep request metadata and headers without reading or saving their response bodies. The browser still loads resources normally.

Only completed requests are saved, including HTTP 4xx and 5xx responses. Failed and unfinished requests are omitted. Entries appear after capture finishes; reading history or closing the session does not wait. Captures still running at navigation or closure may be omitted. Saved bytes come from Playwright and can differ from the server's bytes. Recorded text follows Playwright's UTF-8 decoding when valid, with the declared charset as a fallback.

### Shadow DOM

Set `pierce_shadow=true` on `browser_fetch_once` or each `browser_fetch` call to include open Shadow DOM content. It defaults to `false`. See [Shadow DOM](../fetching/dynamic.md#shadow-dom) for selector examples and limits.

### Key Capabilities
- **Smart Content Extraction**: Convert web pages/elements to Markdown, HTML, or extract a clean version of the text content
- **CSS Selector Support**: Use the Scrapling engine to target specific elements with precision before handing the content to the AI
- **Anti-Bot Bypass**: Handle Cloudflare Turnstile, Interstitial, and other protections
- **Proxy Support**: Use proxies for anonymity and geo-targeting
- **Browser Impersonation**: Mimic real browsers with TLS fingerprinting, real browser headers matching that version, and more
- **Session Persistence**: Reuse browser sessions across multiple requests for better performance
- **Ad Blocking**: All browser-based tools automatically block requests to ~3,500 known ad and tracker domains, saving tokens and speeding up page loads
- **Prompt Injection Protection**: Automatic sanitization of hidden content (CSS-hidden elements, aria-hidden, zero-width characters, HTML comments, template tags) that could be used for prompt injection attacks

#### But why use Scrapling MCP Server instead of other available tools?

Aside from its stealth capabilities and ability to bypass Cloudflare Turnstile/Interstitial, Scrapling's server is the only one that lets you select specific elements to pass to the AI, saving a lot of time and tokens!

The way other servers work is that they extract the content, then pass it all to the AI to extract the fields you want. This causes the AI to consume far more tokens than needed (from irrelevant content). Scrapling solves this problem by allowing you to pass a CSS selector to narrow down the content you want before passing it to the AI, which makes the whole process much faster and more efficient.

If you don't know how to write/use CSS selectors, don't worry. You can tell the AI in the prompt to write selectors to match possible fields for you and watch it try different combinations until it finds the right one, as we will show in the examples section.


## Installation

Install Scrapling with MCP Support, then double-check that the browser dependencies are installed.

```bash
# Install Scrapling with MCP server dependencies
pip install "scrapling[ai]"

# Install browser dependencies
scrapling install
```

Or use the Docker image directly from the Docker registry:
```bash
docker pull pyd4vinci/scrapling
```
Or download it from the GitHub registry:
```bash
docker pull ghcr.io/d4vinci/scrapling:latest
```

## Setting up the MCP Server

Here we will explain how to add Scrapling MCP Server to [Claude Desktop](https://claude.ai/download) and [Claude Code](https://www.anthropic.com/claude-code), but the same logic applies to any other chatbot that supports MCP:

!!! note "Note:"
    The `scrapling-mcp` command used below was added in v0.4.13 as a shortcut that maps directly to `scrapling mcp`, making it easier to add Scrapling to MCP registries and clients that expect a single command. If you are on an older version, use the `scrapling` command with `mcp` as the first argument instead.

### Claude Desktop

1. Open Claude Desktop
2. Click the hamburger menu (☰) at the top left → Settings → Developer → Edit Config
3. Add the Scrapling MCP server configuration:
```json
"ScraplingServer": {
  "command": "scrapling-mcp"
}
```
If that's the first MCP server you're adding, set the content of the file to this: 
```json
{
  "mcpServers": {
    "ScraplingServer": {
      "command": "scrapling-mcp"
    }
  }
}
```
As per the [official article](https://modelcontextprotocol.io/quickstart/user), this action either creates a new configuration file if none exists or opens your existing configuration. The file is located at

1. **MacOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
2. **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

To ensure it's working, use the full path to the `scrapling-mcp` executable. Open the terminal and execute the following command:

1. **MacOS**: `which scrapling-mcp`
2. **Windows**: `where scrapling-mcp`

For me, on my Mac, it returned `/Users/<MyUsername>/.venv/bin/scrapling-mcp`, so the config I used in the end is:
```json
{
  "mcpServers": {
    "ScraplingServer": {
      "command": "/Users/<MyUsername>/.venv/bin/scrapling-mcp"
    }
  }
}
```
#### Docker
If you are using the Docker image, then it would be something like
```json
{
  "mcpServers": {
    "ScraplingServer": {
      "command": "docker",
      "args": [
        "run", "-i", "--rm", "pyd4vinci/scrapling", "mcp"
      ]
    }
  }
}
```

The same logic applies to [Cursor](https://cursor.com/docs/context/mcp), [WindSurf](https://windsurf.com/university/tutorials/configuring-first-mcp-server), and others.

### Claude Code
Here it's much simpler to do. If you have [Claude Code](https://www.anthropic.com/claude-code) installed, open the terminal and execute the following command:

```bash
claude mcp add ScraplingServer "/Users/<MyUsername>/.venv/bin/scrapling-mcp"
```
Same as above, to get Scrapling's executable path, open the terminal and execute the following command:

1. **MacOS**: `which scrapling-mcp`
2. **Windows**: `where scrapling-mcp`

Here's the main article from Anthropic on [how to add MCP servers to Claude code](https://docs.anthropic.com/en/docs/claude-code/mcp#option-1%3A-add-a-local-stdio-server) for further details.


Then, after you've added the server, you need to completely quit and restart the app you used above. In Claude Desktop, you should see an MCP server indicator (🔧) in the bottom-right corner of the chat input or see `ScraplingServer` in the `Search and tools` dropdown in the chat input box.

### Custom Browser Executable

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

You can also set the `SCRAPLING_EXECUTABLE_PATH` environment variable before starting the server. The AI can still choose a different browser executable for a single fetch with `browser_fetch_once` or when opening a session with `browser_open`.

### Connecting to Remote Browsers

`browser_open` doesn't have to launch a browser locally. Pass a CDP url and it will connect to an already-running browser through the [Chrome DevTools Protocol](https://chromedevtools.github.io/devtools-protocol/), whether that browser is on the same machine, another host, or a managed browser provider:
```
Open a stealthy browser session on wss://cdp.provider.example/session/abc123, then use it to scrape the product details from https://shop.example.com. Close the session when you're done.
```
The `session_id` you get back is used with `browser_fetch`, `browser_snapshot`, `browser_actions`, `browser_evaluate`, `browser_screenshot`, `browser_network_requests`, and `browser_network_request` as usual.

The URL can be a WebSocket endpoint (`ws://`/`wss://`), which is what managed browser providers hand out, or the HTTP endpoint of a browser you started yourself with the remote debugging port enabled:
```commandline
chrome --remote-debugging-port=9222
```
That one is reached with `cdp_url="http://localhost:9222"`, or with the host's address if the browser is running on another machine.

!!! note "Notes:"

    * The browser is already running, so options that only apply while launching one are ignored for CDP sessions: `headless`, `real_chrome`, and `executable_path` (including the server-wide default above).<br/>
    * Everything else still applies (`locale`, `useragent`, `proxy`, `cookies`, `timezone_id`, and so on), as each session creates its own browser context on the remote browser.

### Streamable HTTP
Since version 0.3.6, we have added the ability to make the MCP server use the 'Streamable HTTP' transport mode instead of the traditional 'stdio' transport.

So instead of using the following command (the 'stdio' one):
```bash
scrapling-mcp
```
Use the following to enable 'Streamable HTTP' transport mode:
```bash
scrapling-mcp --http
```
Hence, the default value for the host the server is listening to is '127.0.0.1' and the port is 8000, which both can be configured as below:
```bash
scrapling-mcp --http --host '0.0.0.0' --port 8000
```
The default only accepts connections from the same machine. Pass `--host '0.0.0.0'` when you want the server to be reachable from the network, which is a separate decision from authentication below.

If you run the 'Streamable HTTP' transport inside Docker, you have to bind to '0.0.0.0' yourself and set a token, otherwise the published port can't reach the server (the container's '127.0.0.1' is only visible inside the container):
```bash
docker run -p 8000:8000 -e SCRAPLING_MCP_AUTH_TOKEN="<your-token>" pyd4vinci/scrapling mcp --http --host '0.0.0.0'
```

### Authentication

The 'stdio' transport is only reachable by the program that started it, but the moment you switch to 'Streamable HTTP', anyone who can reach the port can call every tool, and that includes fetching any URL from the machine running the server. That's why 'Streamable HTTP' requires authentication, so `--http` on its own refuses to start and asks you for a token:
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
Passing the token on the command line leaves it in your shell history and in the process list, so prefer the `SCRAPLING_MCP_AUTH_TOKEN` environment variable:
```bash
export SCRAPLING_MCP_AUTH_TOKEN="<your-token>"
scrapling-mcp --http
```
If you really want an unauthenticated server, for example while testing locally on the default '127.0.0.1', you have to ask for it with `--no-auth`:
```bash
scrapling-mcp --http --no-auth
```
Combining `--no-auth` with `--host '0.0.0.0'` leaves every tool open to anyone who can reach the port, so avoid that pair outside a trusted network.

When the server listens on a public address, you should also tell it which host names to accept, which turns on protection against DNS-rebinding attacks (a website your browser visits trying to talk to your server). The option can be repeated:
```bash
scrapling-mcp --http --allowed-host 'your-server.example.com:8000'
```

!!! note "Notes:"

    * Authentication applies to the 'Streamable HTTP' transport only. It's ignored with 'stdio', and the server logs a warning to tell you so.<br/>
    * Plain HTTP sends the token in cleartext, so put the server behind a reverse proxy that terminates TLS before exposing it to the internet.<br/>
    * This is a single shared key, not per-client credentials, so every client uses the same token, and rotating it means restarting the server.<br/>
    * Starting the server with `--http --no-auth` still logs a warning telling you that it's unauthenticated.<br/>
    * Passing both `--auth-token` and `--no-auth` keeps the token, so the server stays authenticated instead of quietly dropping it.

## Examples

Now we will show you some examples of prompts we used while testing the MCP server, but you are probably more creative than we are and better at prompt engineering than we are :)

We will gradually go from simple prompts to more complex ones. We will use Claude Desktop for the examples, but the same logic applies to the rest, of course.

1. **Basic Web Scraping**

    Extract the main content from a webpage as Markdown:
    
    ```
    Scrape the main content from https://example.com and convert it to markdown format.
    ```
    
    Claude can use `make_request` to fetch the page and return clean, readable content. HTTP requests default to three attempts with a one-second delay between attempts. If the page needs JavaScript or blocks HTTP requests, the AI can use `browser_fetch_once` instead. Both tools close their own resources after the call.
    
    A more optimized version of the same prompt would be:
    ```
    Use regular requests to scrape the main content from https://example.com and convert it to markdown format.
    ```
    This tells Claude which tool to use here, so it doesn't have to guess. Sometimes it will start using normal requests on its own, and at other times, it will assume browsers are better suited for this website without any apparent reason. As a rule of thumb, you should always tell Claude which tool to use to save time and money and get consistent results.

2. **Targeted Data Extraction**

    Extract specific elements using CSS selectors:
    
    ```
    Get all product titles from https://shop.example.com using the CSS selector '.product-title'. If the request fails, retry up to 5 times every 10 seconds.
    ```
    
    The server will extract only the elements matching your selector and return them as a structured list. Notice I told it to set the tool to try up to 5 times in case the website has connection issues, but the default setting should be fine for most cases.

3. **E-commerce Data Collection**

    Another example of a bit more complex prompt:
    ```
    Open a stealthy browser session and visit these e-commerce URLs one at a time:
    - https://shop1.com/product-a
    - https://shop2.com/product-b  
    - https://shop3.com/product-c
    
    Get the product names, prices, and descriptions from each page. Close the session when done.
    ```
    
    Claude can reuse one browser session, call `browser_fetch` for each URL in order, then analyze the extracted data.

4. **More advanced workflow**

    Let's say I want to get all the action games available on PlayStation's store first page right now. I can use the following prompt to do that:
    ```
    Extract the URLs of all games on this page, then visit each game in order and return a list of all action games: https://store.playstation.com/en-us/pages/browse
    ```
    Tell the AI to reuse an HTTP session to avoid launching a browser when the data is available through normal requests:
    ```
    Open an HTTP session, extract the URLs of all games on this page, then fetch each game in order and return a list of all action games. Close the session when done: https://store.playstation.com/en-us/pages/browse
    ```
    And if you know how to write CSS selectors, you can narrow the content before the AI reads it:
    ```
    Use an HTTP session to extract the URLs of all games on the page below, then fetch each game in order and return a list of all action games.
    The selector for games in the first page is `[href*="/concept/"]` and the selector for the genre in each game page is `[data-qa="gameInfo#releaseInformation#genre-value"]`.
    Close the session when done.

    URL: https://store.playstation.com/en-us/pages/browse
    ```

5. **Get data from a website with Cloudflare protection**

    If you think the website you are targeting has Cloudflare protection, tell Claude instead of letting it discover it on its own.
    ```
    What's the price of this product? Be cautious, as it utilizes Cloudflare's Turnstile protection. Make the browser visible while you work.

    https://ao.com/product/oo101uk-ninja-woodfire-outdoor-pizza-oven-brown-99357-685.aspx
    ```

6. **Long workflow**

    You can, for example, use a prompt like this:
    ```
    Extract all product URLs for the following category, then return the prices and details for the first 3 products.
    
    https://www.arnotts.ie/furniture/bedroom/bed-frames/
    ```
    But a better prompt would be:
    ```
    Go to the following category URL and extract all product URLs using the CSS selector "a". Then, reuse the session to fetch the first 3 product pages in order and extract each product’s price and details. Close the session when done.
    
    Keep the output in markdown format to reduce irrelevant content.
    
    Category URL:
    https://www.arnotts.ie/furniture/bedroom/bed-frames/
    ```

7. **Using Persistent Sessions**

    When scraping multiple pages from the same site, use a persistent browser session to avoid the overhead of launching a new browser for each request:
    ```
    Open a stealthy browser session, then use it to scrape the main details from the first 5 product pages on https://shop.example.com. Close the session when you're done.
    ```
    Claude will use `browser_open` to create a persistent browser, call `browser_fetch` for each product page through that session, and then call `close_session` at the end. This is significantly faster than launching a new browser for each page.

    !!! danger
    
        When using persistent sessions, always remember to close the session after you finish or it will stay open!


8. **Using Persistent Session on a long flow**

    Another long test example that makes Clause think:

    ```
    Use Scrapling MCP to do the following in this order:

    1. Open a stealthy browser session with headless mode off.
    2. Go to this page and collect the number of stars: https://github.com/D4Vinci/Scrapling
    3. From the README, get the URL that shows the number of downloads and go to it.
    4. Get the number of downloads and the top 3 countries from the graph.
    5. Prepare a report with the results.
    6. Close the browser.
    ```

And so on, you get the idea. Your creativity is the key here.

## Best Practices

Here is some technical advice for you.

### 1. Choose the Right Tool
- **`make_request`**: Fast HTTP requests for a single page or API call
- **`browser_fetch_once`**: A single JavaScript/dynamic page or protected site, including Cloudflare
- **Session tools**: Related requests, browser actions, screenshots, and network history

### 2. Optimize Performance
- Reuse a session and fetch each URL in order
- Disable unnecessary resources
- Set appropriate timeouts
- Use CSS selectors for targeted extraction

### 3. Handle Dynamic Content
- Use `network_idle` for SPAs
- Set `wait_selector` for specific elements
- Increase timeout for slow-loading sites

### 4. Data Quality
- Use `main_content_only=true` to avoid navigation/ads
- Choose an appropriate `extraction_type` for your use case

### 5. Prompt Injection Protection
The MCP server automatically sanitizes scraped content when `main_content_only` is enabled (the default). This strips hidden content that malicious websites could use to inject instructions into the AI's context:

- **CSS-hidden elements**: `display:none`, `visibility:hidden`, `opacity:0`, `font-size:0`, `height:0`, `width:0`
- **Accessibility-hidden elements**: `aria-hidden="true"`
- **Template tags**: `<template>` elements
- **HTML comments**: `<!-- ... -->`
- **Zero-width characters**: Invisible unicode characters like zero-width spaces

This protection runs automatically for HTML, Markdown, and text extraction. Keep `main_content_only=true` (the default) for maximum protection.

### 6. Manage Sessions
- Use `make_request` or `browser_fetch_once` for a standalone fetch; they close their own resources and do not leave a session for later calls
- Use `browser_open` to create a persistent browser session when scraping multiple pages, then call `browser_fetch` for each page through that session
- For multiple plain HTTP requests, use `open_request_session` instead and call `session_make_request` per request; it keeps cookies, connections, and the browser fingerprint (`impersonate`) across calls without a browser
- Sessions hold the session-level configuration set when opened (headless, locale, cookies, stealth toggles, etc. for browsers; `impersonate` and `proxy` for requests sessions); the per-request options (timeout, wait_selector, network_idle, solve_cloudflare, etc.) are passed to `browser_fetch`/`session_make_request` on each call, with their defaults shown in the tool schemas
- `browser_fetch` can solve Cloudflare challenges through the open stealthy browser session
- Always close sessions with `close_session` when done to free resources
- Use `list_sessions` to check which sessions are still active and see the `settings` each was created with (returned for the AI agent; empty for CDP sessions)
- Pass a custom `session_id` to the open tools to give sessions meaningful names (e.g. `"search"`, `"checkout"`) instead of the random hex default. They raise if the chosen ID is already in use, so you can detect collisions up front

### 7. Capturing Screenshots

- `browser_screenshot` captures the page already opened through `browser_fetch` in a stealthy browser session. It does not reload the page, so the AI can inspect filled fields, open menus, and other results of its actions.
- The image is returned as a real `ImageContent` block, so the model sees the page directly.
- Capture the visible viewport or the full page, including content below the fold.
- Capture one field, chart, card, or result to inspect it with less surrounding content. Element capture can scroll the target into view.
- Choose PNG for lossless images or JPEG with adjustable quality for smaller payloads.
- The AI can use `browser_actions` to wait for content or finish interactions before capture.

## Legal and Ethical Considerations

⚠️ **Important Guidelines:**

- **Check robots.txt**: Visit `https://website.com/robots.txt` to see scraping rules
- **Respect rate limits**: Don't overwhelm servers with requests
- **Terms of Service**: Read and comply with website terms
- **Copyright**: Respect intellectual property rights
- **Privacy**: Be mindful of personal data protection laws
- **Commercial use**: Ensure you have permission for business purposes

---

*Built with ❤️ by the Scrapling team. Happy scraping!*
