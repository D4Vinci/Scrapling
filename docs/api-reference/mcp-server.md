---
search:
  exclude: true
---

# MCP Server API Reference

The **Scrapling MCP Server** provides fourteen tools for web scraping and browser interaction through the Model Context Protocol (MCP). This server integrates Scrapling's capabilities directly into AI chatbots and agents, allowing conversational web scraping with advanced anti-bot bypass features.

You can start the MCP server by running:

```bash
scrapling mcp
```

Or import the server class directly:

```python
from scrapling.core.ai import ScraplingMCPServer

server = ScraplingMCPServer()
server.serve(http=False, host="127.0.0.1", port=8000)
```

To set a custom Chromium-compatible browser executable for browser-based MCP tools, pass `executable_path`:

```python
server = ScraplingMCPServer(executable_path="/path/to/chromium")
```

## Response Model

The standardized response structure returned by the fetch and HTTP request tools, with one response per call. Session management tools use the models below, `browser_screenshot` returns an image of the current page or one element, plus the current page URL, as image and text content blocks, and `browser_extract` and `browser_actions` return plain text. Both network tools return structured JSON using the models below. `browser_evaluate` returns its result as JSON in a plain text block.

## ::: scrapling.core.ai.server.ResponseModel
    handler: python
    :docstring:

## Network Request Models

`browser_network_requests` returns `NetworkRequestsModel` with `requests`, `next_cursor`, `has_more`, and `dropped_count`. Each `NetworkRequestInfo` contains `id`, `url`, `method`, `resource_type`, and `status`. Pass `next_cursor` as `after_id` to continue; `has_more` indicates more current matches.

`browser_network_request` returns `NetworkRequestModel` with `request_id`, `part`, `data`, and `note`. Summaries and headers are objects; the full saved body text is returned as a string, including JSON response text. `note` explains missing body data or partial headers.

## ::: scrapling.core.ai._network_formatting.NetworkRequestInfo
    handler: python
    :docstring:

## ::: scrapling.core.ai.server.NetworkRequestsModel
    handler: python
    :docstring:

## ::: scrapling.core.ai._network_formatting.NetworkRequestModel
    handler: python
    :docstring:

## Session Models

Model classes for session management:

## ::: scrapling.core.ai.server.SessionInfo
    handler: python
    :docstring:

## ::: scrapling.core.ai.server.SessionCreatedModel
    handler: python
    :docstring:

## ::: scrapling.core.ai.server.SessionClosedModel
    handler: python
    :docstring:

## MCP Server Class

The main MCP server class that provides all web scraping tools:

- **`make_request`**: Fetch one URL through HTTP with browser impersonation and automatic client cleanup. Supports GET, POST, PUT, and DELETE.
- **`browser_fetch_once`**: Fetch one URL through a stealthy browser with JavaScript rendering and Cloudflare handling, then close the browser. Use a persistent session for later actions or network history.

- **`browser_extract`**: Read the current page or one element as an AI snapshot, HTML, Markdown, or text without reloading it. Keep results from forms and page actions. Snapshots include element roles, names, references, positions, and sizes; regex search returns matching lines with nearby context and parent nodes.
- **`browser_actions`**: Chain mouse moves, hovers, clicks, scrolling, field filling, keyboard shortcuts, dialog replies, and waits in one call. Accept or dismiss alerts and confirmations, or enter text in prompts. Fill a search box, submit it, wait for results, and open a result without a separate call for each step.

    Moves and clicks target selectors, snapshot references, or coordinates; element targets wait and scroll into view. Supports movement in multiple steps, left, right, and middle clicks, double-clicks, and scrolling nested panels.

    Target fields anywhere on the page through selectors or snapshot references. Fill text, check or uncheck boxes, select radio buttons, and choose one or more native dropdown options by label. Replace or clear text, or type at the current caret. Keyboard shortcuts use the current focus. Slow mode adds random pauses between typed characters and all actions.

    Wait for content or loading overlays through selectors or snapshot references, wait for page load events or settled network activity, or add a fixed pause before continuing.

- **`browser_evaluate`**: Run JavaScript on the current page to extract custom data, calculate results, read application state, or update page content. Supports asynchronous scripts and returns their results as JSON.
- **`browser_network_requests`**: Search completed browser requests across tabs, navigation, and actions. Find API calls, HTTP errors, and saved redirects, with static resources hidden by default for smaller results. Failed and unfinished requests are omitted. Returns structured request details with pagination.
- **`browser_network_request`**: Read a recorded request's summary, headers, sent data, or text response body as structured JSON without repeating the request. Returns the selected part in full, including saved body text. Saved responses remain available after page changes, including HTTP 4xx and 5xx responses. Entries appear after capture finishes; reading history or closing the session does not wait. Captures still running at navigation or closure may be omitted. Saved bytes come from Playwright and can differ from the server's bytes. Recorded text follows Playwright's UTF-8 decoding when valid, with the declared charset as a fallback. Only response bodies with a supported text `Content-Type` are read and saved. Binary, missing, or unrecognized types keep metadata and headers without body reads; browser loading is unchanged. Size limits bound the saved history, and an optional note explains non-text, oversized, or unreadable bodies. Read needed details before closing the MCP session.
- **`browser_fetch`**: Fetch a page through an open stealthy browser session and extract HTML, Markdown, text, or a structured snapshot. Snapshots can cover the whole page or a chosen element and include element references, positions, and sizes for later interaction.

## ::: scrapling.core.ai.server.ScraplingMCPServer
    handler: python
    :docstring:
