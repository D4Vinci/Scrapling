# Scrapling MCP Server Guide

<iframe width="560" height="315" src="https://www.youtube.com/embed/qyFk3ZNwOxE?si=3FHzgcYCb66iJ6e3" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>

The **Scrapling MCP Server** is a new feature that brings Scrapling's powerful Web Scraping capabilities directly to your favorite AI chatbot or AI agent. This integration allows you to scrape websites, extract data, and bypass anti-bot protections conversationally through Claude's AI interface or any interface that supports MCP.

## Features

The Scrapling MCP Server provides thirteen powerful tools for web scraping, split into two modes: one-shot tools that each launch and close their own browser/client, and session tools that open a browser or an HTTP session once and then work through it.

### One-shot tools

#### 🚀 Basic HTTP Scraping
- **`make_request`**: Fast HTTP requests with any method (GET, POST, PUT, DELETE) and browser fingerprint impersonation, generating real browser headers matching the TLS version, HTTP/3, and more!
- **`bulk_get`**: An async GET-only version of the above tool that allows scraping of multiple URLs at the same time!

#### 🌐 Dynamic Content Scraping
- **`fetch`**: Rapidly fetch dynamic content with Chromium/Chrome browser with complete control over the request/browser, and more!
- **`bulk_fetch`**: An async version of the above tool that allows scraping of multiple URLs in different browser tabs at the same time!

#### 🔒 Stealth Scraping
- **`stealthy_fetch`**: Uses our Stealthy browser to bypass Cloudflare Turnstile/Interstitial and other anti-bot systems with complete control over the request/browser!
- **`bulk_stealthy_fetch`**: An async version of the above tool that allows stealth scraping of multiple URLs in different browser tabs at the same time!

### Session tools

#### 🔌 Session Management
- **`open_session`**: Create a persistent browser session (dynamic or stealthy) that stays open across multiple `session_fetch` calls, avoiding the overhead of launching a new browser each time. It holds the browser-level configuration and returns the session's effective `settings` for the AI agent (empty for CDP sessions).
- **`open_request_session`**: Create a persistent HTTP requests session (no browser) used with `session_make_request`, keeping cookies, connections, and the browser fingerprint (`impersonate`) between requests. It returns the same `settings` receipt and shows in `list_sessions` as a `static` session.
- **`close_session`**: Close a persistent session (browser or requests) and free its resources.
- **`list_sessions`**: List all active sessions with their details and `settings`.

#### 🎯 Fetching Through a Session
- **`session_fetch`**: Fetch a single URL through an open browser session (dynamic or stealthy), carrying the per-request options for that call. This is the session counterpart of `fetch`/`stealthy_fetch`.
- **`session_make_request`**: Make an HTTP request with any method through a session opened with `open_request_session`, reusing its cookies, connections, and browser fingerprint. This is the session counterpart of `make_request`.

#### 📸 Screenshots
- **`screenshot`**: Capture a PNG or JPEG screenshot of a page using an open browser session, returned as an image content block the model can actually see (not a base64 string blob). Supports full-page captures, JPEG quality, and the usual readiness controls (`wait`, `wait_selector`, `network_idle`).

### Key Capabilities
- **Smart Content Extraction**: Convert web pages/elements to Markdown, HTML, or extract a clean version of the text content
- **CSS Selector Support**: Use the Scrapling engine to target specific elements with precision before handing the content to the AI
- **Anti-Bot Bypass**: Handle Cloudflare Turnstile, Interstitial, and other protections
- **Proxy Support**: Use proxies for anonymity and geo-targeting
- **Browser Impersonation**: Mimic real browsers with TLS fingerprinting, real browser headers matching that version, and more
- **Parallel Processing**: Scrape multiple URLs concurrently for efficiency
- **Session Persistence**: Reuse browser sessions across multiple requests for better performance
- **Ad Blocking**: All browser-based tools automatically block requests to ~3,500 known ad and tracker domains, saving tokens and speeding up page loads
- **Prompt Injection Protection**: Automatic sanitization of hidden content (CSS-hidden elements, aria-hidden, zero-width characters, HTML comments, template tags) that could be used for prompt injection attacks

#### But why use Scrapling MCP Server instead of other available tools?

Aside from its stealth capabilities and ability to bypass Cloudflare Turnstile/Interstitial, Scrapling's server is the only one that lets you select specific elements to pass to the AI, saving a lot of time and tokens!

The way other servers work is that they extract the content, then pass it all to the AI to extract the fields you want. This causes the AI to consume far more tokens than needed (from irrelevant content). Scrapling solves this problem by allowing you to pass a CSS selector to narrow down the content you want before passing it to the AI, which makes the whole process much faster and more efficient.

If you don't know how to write/use CSS selectors, don't worry. You can tell the AI in the prompt to write selectors to match possible fields for you and watch it try different combinations until it finds the right one, as we will show in the examples section.

## Breaking changes

Since version 0.4.15, the MCP server is reworked. If you are upgrading, note:

1. **The Streamable HTTP transport now requires authentication and binds to localhost.** `scrapling-mcp --http` on its own refuses to start; pass `--auth-token` (or the `SCRAPLING_MCP_AUTH_TOKEN` environment variable), or `--no-auth` to serve it unauthenticated on purpose. The default host is now `127.0.0.1` instead of `0.0.0.0`; pass `--host 0.0.0.0` to accept connections from the network.
2. **The one-shot fetch tools no longer accept `session_id`.** `fetch`, `bulk_fetch`, `stealthy_fetch`, and `bulk_stealthy_fetch` always launch their own browser. To fetch through a session, use the new **`session_fetch`** tool (one URL per call, works with dynamic and stealthy sessions).
3. **`open_session` takes browser-level parameters only.** The per-request options (`wait`, `timeout`, `google_search`, `network_idle`, `disable_resources`, `wait_selector`, `wait_selector_state`, `extra_headers`, `solve_cloudflare`) moved to `session_fetch` and are supplied on each call. `proxy` stays on `open_session` (it applies to the whole session, which runs a single tab). `max_pages` was removed too, since a session manages a single page per call now.
4. **The `get` tool is renamed to `make_request`.** It now takes a `method` parameter and supports GET (default), POST, PUT, and DELETE, with `data`/`json` for request bodies. `bulk_get` is unchanged.

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

Browser-based tools (`fetch`, `bulk_fetch`, `stealthy_fetch`, `bulk_stealthy_fetch`, and `open_session`) can use a custom Chromium-compatible browser executable instead of the bundled Chromium. This is useful for custom browser builds or lightweight browser engines.

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

You can also set the `SCRAPLING_EXECUTABLE_PATH` environment variable before starting the server. Tool calls can still pass `executable_path` directly when a single request or session needs a different browser executable.

### Connecting to Remote Browsers

`open_session` doesn't have to launch a browser locally. Pass a CDP url and it will connect to an already-running browser through the [Chrome DevTools Protocol](https://chromedevtools.github.io/devtools-protocol/), whether that browser is on the same machine, another host, or a managed browser provider:
```
Open a stealthy browser session on wss://cdp.provider.example/session/abc123, then use it to scrape the product details from https://shop.example.com. Close the session when you're done.
```
Both browser session types (`dynamic` and `stealthy`) accept it, and the `session_id` you get back is used with `session_fetch` and `screenshot` as usual.

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
    
    Claude will use the `make_request` tool to fetch the page and return clean, readable content. If it fails, it will continue retrying every second for 3 attempts, unless you instruct it otherwise. If it fails to retrieve content for any reason, such as protection or if it's a dynamic website, it will automatically try the other tools. If Claude didn't do that automatically for some reason, you can add that to the prompt.
    
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
    Extract product information from these e-commerce URLs using bulk browser fetches:
    - https://shop1.com/product-a
    - https://shop2.com/product-b  
    - https://shop3.com/product-c
    
    Get the product names, prices, and descriptions from each page.
    ```
    
    Claude will use `bulk_fetch` to concurrently scrape all URLs, then analyze the extracted data.

4. **More advanced workflow**

    Let's say I want to get all the action games available on PlayStation's store first page right now. I can use the following prompt to do that:
    ```
    Extract the URLs of all games in this page, then do a bulk request to them and return a list of all action games: https://store.playstation.com/en-us/pages/browse
    ```
    Note that I instructed it to use a bulk request for all the URLs collected. If I hadn't mentioned it, sometimes it works as intended, and other times it makes a separate request to each URL, which takes significantly longer. This prompt takes approximately one minute to complete.
    
    However, because I wasn't specific enough, it actually used the `stealthy_fetch` here and the `bulk_stealthy_fetch` in the second step, which unnecessarily consumed a large number of tokens. A better prompt would be:
    ```
    Use normal requests to extract the URLs of all games in this page, then do a bulk request to them and return a list of all action games: https://store.playstation.com/en-us/pages/browse
    ```
    And if you know how to write CSS selectors, you can instruct Claude to apply the selectors to the elements you want, and it will nearly complete the task immediately.
    ```
    Use normal requests to extract the URLs of all games on the page below, then perform a bulk request to them and return a list of all action games.
    The selector for games in the first page is `[href*="/concept/"]` and the selector for the genre in the second request is `[data-qa="gameInfo#releaseInformation#genre-value"]`.
    
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
    Go to the following category URL and extract all product URLs using the CSS selector "a". Then, fetch the first 3 product pages in parallel and extract each product’s price and details.
    
    Keep the output in markdown format to reduce irrelevant content.
    
    Category URL:
    https://www.arnotts.ie/furniture/bedroom/bed-frames/
    ```

7. **Using Persistent Sessions**

    When scraping multiple pages from the same site, use a persistent browser session to avoid the overhead of launching a new browser for each request:
    ```
    Open a stealthy browser session, then use it to scrape the main details from the first 5 product pages on https://shop.example.com. Close the session when you're done.
    ```
    Claude will use `open_session` to create a persistent browser, call `session_fetch` for each product page through that session, and then call `close_session` at the end. This is significantly faster than launching a new browser for each page.

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
- **`make_request`**: Fast, simple websites
- **`fetch`**: Sites with JavaScript/dynamic content  
- **`stealthy_fetch`**: Protected sites, Cloudflare, anti-bot systems

### 2. Optimize Performance
- Use bulk tools for multiple URLs
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

This protection runs automatically on all MCP tool responses. Keep `main_content_only=true` (the default) for maximum protection.

### 6. Use Sessions for Multiple Requests
- Use `open_session` to create a persistent browser session when scraping multiple pages, then call `session_fetch` for each page through that session
- For multiple plain HTTP requests, use `open_request_session` instead and call `session_make_request` per request; it keeps cookies, connections, and the browser fingerprint (`impersonate`) across calls without a browser
- Sessions hold the session-level configuration set when opened (headless, locale, cookies, stealth toggles, etc. for browsers; `impersonate` and `proxy` for requests sessions); the per-request options (timeout, wait_selector, network_idle, solve_cloudflare, etc.) are passed to `session_fetch`/`session_make_request` on each call, with their defaults shown in the tool schemas
- One `session_fetch` works with both browser session types; `solve_cloudflare` only applies to a stealthy session and raises a clear error on a dynamic one
- The one-shot tools (`make_request`, `bulk_get`, `fetch`, `bulk_fetch`, `stealthy_fetch`, `bulk_stealthy_fetch`) never take a session
- Always close sessions with `close_session` when done to free resources
- Use `list_sessions` to check which sessions are still active and see the `settings` each was created with (returned for the AI agent; empty for CDP sessions)
- Pass a custom `session_id` to the open tools to give sessions meaningful names (e.g. `"search"`, `"checkout"`) instead of the random hex default. They raise if the chosen ID is already in use, so you can detect collisions up front

### 7. Capturing Screenshots
- `screenshot` only works through an existing browser session, so call `open_session` first (either `dynamic` or `stealthy` works)
- The image is returned as a real `ImageContent` block, not a base64 string in JSON, so the model sees the page directly
- Use `full_page=True` when you need everything below the fold; the default captures only the visible viewport
- Pick `image_type="jpeg"` with a `quality` value (0-100) for smaller payloads when pixel-perfect color isn't needed
- The same `wait`, `wait_selector`, `network_idle`, and `timeout` controls used by `fetch` are available here too

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
