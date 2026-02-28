# Scrapling MCP Server Guide

<iframe width="560" height="315" src="https://www.youtube.com/embed/qyFk3ZNwOxE?si=3FHzgcYCb66iJ6e3" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>

The **Scrapling MCP Server** is a new feature that brings Scrapling's powerful Web Scraping capabilities directly to your favorite AI chatbot or AI agent. This integration allows you to scrape websites, extract data, and bypass anti-bot protections conversationally through Claude's AI interface or any interface that supports MCP.

## Features

The Scrapling MCP Server provides six powerful tools for web scraping:

### 🚀 Basic HTTP Scraping
- **`get`**: Fast HTTP requests with browser fingerprint impersonation, generating real browser headers matching the TLS version, HTTP/3, and more!
- **`bulk_get`**: An async version of the above tool that allows scraping of multiple URLs at the same time!

### 🌐 Dynamic Content Scraping  
- **`fetch`**: Rapidly fetch dynamic content with Chromium/Chrome browser with complete control over the request/browser, and more!
- **`bulk_fetch`**: An async version of the above tool that allows scraping of multiple URLs in different browser tabs at the same time!

### 🔒 Stealth Scraping
- **`stealthy_fetch`**: Uses our Stealthy browser to bypass Cloudflare Turnstile/Interstitial and other anti-bot systems with complete control over the request/browser! 
- **`bulk_stealthy_fetch`**: An async version of the above tool that allows stealth scraping of multiple URLs in different browser tabs at the same time!

### Key Capabilities
- **Smart Content Extraction**: Convert web pages/elements to Markdown, HTML, or extract a clean version of the text content
- **CSS Selector Support**: Use the Scrapling engine to target specific elements with precision before handing the content to the AI
- **Anti-Bot Bypass**: Handle Cloudflare Turnstile, Interstitial, and other protections
- **Proxy Support**: Use proxies for anonymity and geo-targeting
- **Browser Impersonation**: Mimic real browsers with TLS fingerprinting, real browser headers matching that version, and more
- **Parallel Processing**: Scrape multiple URLs concurrently for efficiency

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

### Claude Desktop

1. Open Claude Desktop
2. Click the hamburger menu (☰) at the top left → Settings → Developer → Edit Config
3. Add the Scrapling MCP server configuration:
```json
"ScraplingServer": {
  "command": "scrapling",
  "args": [
    "mcp"
  ]
}
```
If that's the first MCP server you're adding, set the content of the file to this: 
```json
{
  "mcpServers": {
    "ScraplingServer": {
      "command": "scrapling",
      "args": [
        "mcp"
      ]
    }
  }
}
```
As per the [official article](https://modelcontextprotocol.io/quickstart/user), this action either creates a new configuration file if none exists or opens your existing configuration. The file is located at

1. **MacOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
2. **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

To ensure it's working, use the full path to the `scrapling` executable. Open the terminal and execute the following command:

1. **MacOS**: `which scrapling`
2. **Windows**: `where scrapling`

For me, on my Mac, it returned `/Users/<MyUsername>/.venv/bin/scrapling`, so the config I used in the end is:
```json
{
  "mcpServers": {
    "ScraplingServer": {
      "command": "/Users/<MyUsername>/.venv/bin/scrapling",
      "args": [
        "mcp"
      ]
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
        "run", "-i", "--rm", "scrapling", "mcp"
      ]
    }
  }
}
```

The same logic applies to [Cursor](https://cursor.com/docs/context/mcp), [WindSurf](https://windsurf.com/university/tutorials/configuring-first-mcp-server), and others.

### Claude Code
Here it's much simpler to do. If you have [Claude Code](https://www.anthropic.com/claude-code) installed, open the terminal and execute the following command:

```bash
claude mcp add ScraplingServer "/Users/<MyUsername>/.venv/bin/scrapling" mcp
```
Same as above, to get Scrapling's executable path, open the terminal and execute the following command:

1. **MacOS**: `which scrapling`
2. **Windows**: `where scrapling`

Here's the main article from Anthropic on [how to add MCP servers to Claude code](https://docs.anthropic.com/en/docs/claude-code/mcp#option-1%3A-add-a-local-stdio-server) for further details.


Then, after you've added the server, you need to completely quit and restart the app you used above. In Claude Desktop, you should see an MCP server indicator (🔧) in the bottom-right corner of the chat input or see `ScraplingServer` in the `Search and tools` dropdown in the chat input box.

### Streamable HTTP
As per version 0.3.6, we have added the ability to make the MCP server use the 'Streamable HTTP' transport mode instead of the traditional 'stdio' transport.

So instead of using the following command (the 'stdio' one):
```bash
scrapling mcp
```
Use the following to enable 'Streamable HTTP' transport mode:
```bash
scrapling mcp --http
```
Hence, the default value for the host the server is listening to is '0.0.0.0' and the port is 8000, which both can be configured as below:
```bash
scrapling mcp --http --host '127.0.0.1' --port 8000
```

## Examples

Now we will show you some examples of prompts we used while testing the MCP server, but you are probably more creative than we are and better at prompt engineering than we are :)

We will gradually go from simple prompts to more complex ones. We will use Claude Desktop for the examples, but the same logic applies to the rest, of course.

1. **Basic Web Scraping**

    Extract the main content from a webpage as Markdown:
    
    ```
    Scrape the main content from https://example.com and convert it to markdown format.
    ```
    
    Claude will use the `get` tool to fetch the page and return clean, readable content. If it fails, it will continue retrying every second for 3 attempts, unless you instruct it otherwise. If it fails to retrieve content for any reason, such as protection or if it's a dynamic website, it will automatically try the other tools. If Claude didn't do that automatically for some reason, you can add that to the prompt.
    
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

And so on, you get the idea. Your creativity is the key here.

## Best Practices

Here is some technical advice for you.

### 1. Choose the Right Tool
- **`get`**: Fast, simple websites
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