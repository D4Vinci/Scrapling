# Scrapling Extract Command Guide

**Web Scraping through the terminal without requiring any programming!**

The `scrapling extract` Command lets you download and extract content from websites directly from your terminal without writing any code. Ideal for beginners, researchers, and anyone requiring rapid web data extraction.

## What is the Extract Command group?

The extract command is a set of simple terminal tools that:

- **Downloads web pages** and saves their content to files.
- **Converts HTML to readable formats** like Markdown, keeps it as HTML, or just extracts the text content of the page.
- **Supports custom CSS selectors** to extract specific parts of the page.
- **Handles HTTP requests and fetching through browsers**
- **Highly customizable** with custom headers, cookies, proxies, and the rest of the options. Almost all the options available through the code are also accessible through the command line.

## Quick Start

- **Basic Website Download**

    Download a website's text content as clean, readable text:
    ```bash
    scrapling extract get "https://example.com" page_content.txt
    ```
    This does an HTTP GET request and saves the text content of the webpage to `page_content.txt`.

- **Save as Different Formats**

    Choose your output format by changing the file extension:
    ```bash
    # Convert the HTML content to Markdown, then save it to the file (great for documentation)
    scrapling extract get "https://blog.example.com" article.md
    
    # Save the HTML content as it is to the file
    scrapling extract get "https://example.com" page.html
    
    # Save a clean version of the text content of the webpage to the file
    scrapling extract get "https://example.com" content.txt
    ```

- **Extract Specific Content**

    All commands can use CSS selectors to extract specific parts of the page through `--css-selector` or `-s` as you will see in the examples below.

## Available Commands

You can display the available commands through `scrapling extract --help` to get the following list:
```bash
Usage: scrapling extract [OPTIONS] COMMAND [ARGS]...

  Fetch web pages using various fetchers and extract full/selected HTML content as HTML, Markdown, or extract text content.

Options:
  --help  Show this message and exit.

Commands:
  get             Perform a GET request and save the content to a file.
  post            Perform a POST request and save the content to a file.
  put             Perform a PUT request and save the content to a file.
  delete          Perform a DELETE request and save the content to a file.
  fetch           Use DynamicFetcher to fetch content with browser...
  stealthy-fetch  Use StealthyFetcher to fetch content with advanced...
```

We will go through each Command in detail below.

### HTTP Requests

1. **GET Request**

    The most common Command for downloading website content:
    
    ```bash
    scrapling extract get [URL] [OUTPUT_FILE] [OPTIONS]
    ```
    
    **Examples:**
    ```bash
    # Basic download
    scrapling extract get "https://news.site.com" news.md
    
    # Download with custom timeout
    scrapling extract get "https://example.com" content.txt --timeout 60
    
    # Extract only specific content using CSS selectors
    scrapling extract get "https://blog.example.com" articles.md --css-selector "article"
   
    # Send a request with cookies
    scrapling extract get "https://scrapling.requestcatcher.com" content.md --cookies "session=abc123; user=john"
   
    # Add user agent
    scrapling extract get "https://api.site.com" data.json -H "User-Agent: MyBot 1.0"
    
    # Add multiple headers
    scrapling extract get "https://site.com" page.html -H "Accept: text/html" -H "Accept-Language: en-US"
    ```
    Get the available options for the Command with `scrapling extract get --help` as follows:
    ```bash
    Usage: scrapling extract get [OPTIONS] URL OUTPUT_FILE
    
      Perform a GET request and save the content to a file.
    
      The output file path can be an HTML file, a Markdown file of the HTML content, or the text content itself. Use file extensions (`.html`/`.md`/`.txt`) respectively.
    
    Options:
      -H, --headers TEXT                             HTTP headers in format "Key: Value" (can be used multiple times)
      --cookies TEXT                                 Cookies string in format "name1=value1;name2=value2"
      --timeout INTEGER                              Request timeout in seconds (default: 30)
      --proxy TEXT                                   Proxy URL in format "http://username:password@host:port"
      -s, --css-selector TEXT                        CSS selector to extract specific content from the page. It returns all matches.
      -p, --params TEXT                              Query parameters in format "key=value" (can be used multiple times)
      --follow-redirects / --no-follow-redirects     Whether to follow redirects (default: True)
      --verify / --no-verify                         Whether to verify SSL certificates (default: True)
      --impersonate TEXT                             Browser to impersonate (e.g., chrome, firefox).
      --stealthy-headers / --no-stealthy-headers     Use stealthy browser headers (default: True)
      --help                                         Show this message and exit.
    
    ```
    Note that the options will work in the same way for all other request commands, so no need to repeat them.

2. **Post Request**
    
    ```bash
    scrapling extract post [URL] [OUTPUT_FILE] [OPTIONS]
    ```
    
    **Examples:**
    ```bash
    # Submit form data
    scrapling extract post "https://api.site.com/search" results.html --data "query=python&type=tutorial"
    
    # Send JSON data
    scrapling extract post "https://api.site.com" response.json --json '{"username": "test", "action": "search"}'
    ```
    Get the available options for the Command with `scrapling extract post --help` as follows:
    ```bash
    Usage: scrapling extract post [OPTIONS] URL OUTPUT_FILE
    
      Perform a POST request and save the content to a file.
    
      The output file path can be an HTML file, a Markdown file of the HTML content, or the text content itself. Use file extensions (`.html`/`.md`/`.txt`) respectively.
    
    Options:
      -d, --data TEXT                                Form data to include in the request body (as string, ex: "param1=value1&param2=value2")
      -j, --json TEXT                                JSON data to include in the request body (as string)
      -H, --headers TEXT                             HTTP headers in format "Key: Value" (can be used multiple times)
      --cookies TEXT                                 Cookies string in format "name1=value1;name2=value2"
      --timeout INTEGER                              Request timeout in seconds (default: 30)
      --proxy TEXT                                   Proxy URL in format "http://username:password@host:port"
      -s, --css-selector TEXT                        CSS selector to extract specific content from the page. It returns all matches.
      -p, --params TEXT                              Query parameters in format "key=value" (can be used multiple times)
      --follow-redirects / --no-follow-redirects     Whether to follow redirects (default: True)
      --verify / --no-verify                         Whether to verify SSL certificates (default: True)
      --impersonate TEXT                             Browser to impersonate (e.g., chrome, firefox).
      --stealthy-headers / --no-stealthy-headers     Use stealthy browser headers (default: True)
      --help                                         Show this message and exit.
    
    ```

3. **Put Request**
    
    ```bash
    scrapling extract put [URL] [OUTPUT_FILE] [OPTIONS]
    ```
    
    **Examples:**
    ```bash
    # Send data
    scrapling extract put "https://scrapling.requestcatcher.com/put" results.html --data "update=info" --impersonate "firefox"
    
    # Send JSON data
    scrapling extract put "https://scrapling.requestcatcher.com/put" response.json --json '{"username": "test", "action": "search"}'
    ```
    Get the available options for the Command with `scrapling extract put --help` as follows:
    ```bash
    Usage: scrapling extract put [OPTIONS] URL OUTPUT_FILE
    
      Perform a PUT request and save the content to a file.
    
      The output file path can be an HTML file, a Markdown file of the HTML content, or the text content itself. Use file extensions (`.html`/`.md`/`.txt`) respectively.
    
    Options:
      -d, --data TEXT                                Form data to include in the request body
      -j, --json TEXT                                JSON data to include in the request body (as string)
      -H, --headers TEXT                             HTTP headers in format "Key: Value" (can be used multiple times)
      --cookies TEXT                                 Cookies string in format "name1=value1;name2=value2"
      --timeout INTEGER                              Request timeout in seconds (default: 30)
      --proxy TEXT                                   Proxy URL in format "http://username:password@host:port"
      -s, --css-selector TEXT                        CSS selector to extract specific content from the page. It returns all matches.
      -p, --params TEXT                              Query parameters in format "key=value" (can be used multiple times)
      --follow-redirects / --no-follow-redirects     Whether to follow redirects (default: True)
      --verify / --no-verify                         Whether to verify SSL certificates (default: True)
      --impersonate TEXT                             Browser to impersonate (e.g., chrome, firefox).
      --stealthy-headers / --no-stealthy-headers     Use stealthy browser headers (default: True)
      --help                                         Show this message and exit.
    ```

4. **Delete Request**
    
    ```bash
    scrapling extract delete [URL] [OUTPUT_FILE] [OPTIONS]
    ```
    
    **Examples:**
    ```bash
    # Send data
    scrapling extract delete "https://scrapling.requestcatcher.com/delete" results.html
    
    # Send JSON data
    scrapling extract delete "https://scrapling.requestcatcher.com/" response.txt --impersonate "chrome"
    ```
    Get the available options for the Command with `scrapling extract delete --help` as follows:
    ```bash
    Usage: scrapling extract delete [OPTIONS] URL OUTPUT_FILE
    
      Perform a DELETE request and save the content to a file.
    
      The output file path can be an HTML file, a Markdown file of the HTML content, or the text content itself. Use file extensions (`.html`/`.md`/`.txt`) respectively.
    
    Options:
      -H, --headers TEXT                             HTTP headers in format "Key: Value" (can be used multiple times)
      --cookies TEXT                                 Cookies string in format "name1=value1;name2=value2"
      --timeout INTEGER                              Request timeout in seconds (default: 30)
      --proxy TEXT                                   Proxy URL in format "http://username:password@host:port"
      -s, --css-selector TEXT                        CSS selector to extract specific content from the page. It returns all matches.
      -p, --params TEXT                              Query parameters in format "key=value" (can be used multiple times)
      --follow-redirects / --no-follow-redirects     Whether to follow redirects (default: True)
      --verify / --no-verify                         Whether to verify SSL certificates (default: True)
      --impersonate TEXT                             Browser to impersonate (e.g., chrome, firefox).
      --stealthy-headers / --no-stealthy-headers     Use stealthy browser headers (default: True)
      --help                                         Show this message and exit.
    ```

### Browsers fetching

1. **fetch - Handle Dynamic Content**

    For websites that load content with dynamic content or have slight protection
    
    ```bash
    scrapling extract fetch [URL] [OUTPUT_FILE] [OPTIONS]
    ```
    
    **Examples:**
    ```bash
    # Wait for JavaScript to load content and finish network activity
    scrapling extract fetch "https://scrapling.requestcatcher.com/" content.md --network-idle
    
    # Wait for specific content to appear
    scrapling extract fetch "https://scrapling.requestcatcher.com/" data.txt --wait-selector ".content-loaded"
    
    # Run in visible browser mode (helpful for debugging)
    scrapling extract fetch "https://scrapling.requestcatcher.com/" page.html --no-headless --disable-resources
    ```
    Get the available options for the Command with `scrapling extract fetch --help` as follows:
    ```bash
    Usage: scrapling extract fetch [OPTIONS] URL OUTPUT_FILE
    
      Use DynamicFetcher to fetch content with browser automation.
    
      The output file path can be an HTML file, a Markdown file of the HTML content, or the text content itself. Use file extensions (`.html`/`.md`/`.txt`) respectively.
    
    Options:
      --headless / --no-headless                  Run browser in headless mode (default: True)
      --disable-resources / --enable-resources    Drop unnecessary resources for speed boost (default: False)
      --network-idle / --no-network-idle          Wait for network idle (default: False)
      --timeout INTEGER                           Timeout in milliseconds (default: 30000)
      --wait INTEGER                              Additional wait time in milliseconds after page load (default: 0)
      -s, --css-selector TEXT                     CSS selector to extract specific content from the page. It returns all matches.
      --wait-selector TEXT                        CSS selector to wait for before proceeding
      --locale TEXT                               Browser locale (default: en-US)
      --stealth / --no-stealth                    Enable stealth mode (default: False)
      --hide-canvas / --show-canvas               Add noise to canvas operations (default: False)
      --disable-webgl / --enable-webgl            Disable WebGL support (default: False)
      --proxy TEXT                                Proxy URL in format "http://username:password@host:port"
      -H, --extra-headers TEXT                    Extra headers in format "Key: Value" (can be used multiple times)
      --help                                      Show this message and exit.
    ```

2. **stealthy-fetch - Bypass Protection**

    For websites with anti-bot protection or Cloudflare protection
    
    ```bash
    scrapling extract stealthy-fetch [URL] [OUTPUT_FILE] [OPTIONS]
    ```
    
    **Examples:**
    ```bash
    # Bypass basic protection
    scrapling extract stealthy-fetch "https://scrapling.requestcatcher.com" content.md
    
    # Solve Cloudflare challenges
    scrapling extract stealthy-fetch "https://nopecha.com/demo/cloudflare" data.txt --solve-cloudflare --css-selector "#padded_content a"
    
    # Use proxy for anonymity
    scrapling extract stealthy-fetch "https://site.com" content.md --proxy "http://proxy-server:8080"
    ```
    Get the available options for the Command with `scrapling extract stealthy-fetch --help` as follows:
    ```bash
    Usage: scrapling extract stealthy-fetch [OPTIONS] URL OUTPUT_FILE
    
      Use StealthyFetcher to fetch content with advanced stealth features.
    
      The output file path can be an HTML file, a Markdown file of the HTML content, or the text content itself. Use file extensions (`.html`/`.md`/`.txt`) respectively.
    
    Options:
      --headless / --no-headless                  Run browser in headless mode (default: True)
      --block-images / --allow-images             Block image loading (default: False)
      --disable-resources / --enable-resources    Drop unnecessary resources for speed boost (default: False)
      --block-webrtc / --allow-webrtc             Block WebRTC entirely (default: False)
      --humanize / --no-humanize                  Humanize cursor movement (default: False)
      --solve-cloudflare / --no-solve-cloudflare  Solve Cloudflare challenges (default: False)
      --allow-webgl / --block-webgl               Allow WebGL (default: True)
      --network-idle / --no-network-idle          Wait for network idle (default: False)
      --disable-ads / --allow-ads                 Install uBlock Origin addon (default: False)
      --timeout INTEGER                           Timeout in milliseconds (default: 30000)
      --wait INTEGER                              Additional wait time in milliseconds after page load (default: 0)
      -s, --css-selector TEXT                     CSS selector to extract specific content from the page. It returns all matches.
      --wait-selector TEXT                        CSS selector to wait for before proceeding
      --geoip / --no-geoip                        Use IP/Proxy geolocation for timezone/locale (default: False)
      --proxy TEXT                                Proxy URL in format "http://username:password@host:port"
      -H, --extra-headers TEXT                    Extra headers in format "Key: Value" (can be used multiple times)
      --help                                      Show this message and exit.
    ```

## When to use each Command

If you are not a Web Scraping expert and can't decide what to choose, you can use the following formula to help you decide:

- Use **`get`** with simple websites, blogs, or news articles
- Use **`fetch`** with modern web apps, or sites with dynamic content
- Use **`stealthy-fetch`** with protected sites, Cloudflare, or anti-bot systems

## Legal and Ethical Considerations

⚠️ **Important Guidelines:**

- **Check robots.txt**: Visit `https://website.com/robots.txt` to see scraping rules
- **Respect rate limits**: Don't overwhelm servers with requests
- **Terms of Service**: Read and comply with website terms
- **Copyright**: Respect intellectual property rights
- **Privacy**: Be mindful of personal data protection laws
- **Commercial use**: Ensure you have permission for business purposes

---

*Happy scraping! Remember to always respect website policies and comply with all applicable legal requirements.*