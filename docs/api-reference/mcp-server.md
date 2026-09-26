---
search:
  exclude: true
---

# MCP Server API Reference

The **Scrapling MCP Server** provides fifteen tools for web scraping and browser interaction through the Model Context Protocol (MCP). This server integrates Scrapling's capabilities directly into AI chatbots and agents, allowing conversational web scraping with advanced anti-bot bypass features.

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

The standardized response structure returned by the fetch and HTTP request tools. Bulk tools return a list of these responses. Session management tools use the models below, `browser_screenshot` returns image and text content blocks, and `browser_snapshot` and `browser_actions` return plain text.

## ::: scrapling.core.ai.ResponseModel
    handler: python
    :docstring:

## Session Models

Model classes for session management:

## ::: scrapling.core.ai.SessionInfo
    handler: python
    :docstring:

## ::: scrapling.core.ai.SessionCreatedModel
    handler: python
    :docstring:

## ::: scrapling.core.ai.SessionClosedModel
    handler: python
    :docstring:

## MCP Server Class

The main MCP server class that provides all web scraping tools:

- **`browser_snapshot`**: Inspect the current page without reloading it. Structured text includes element roles, names, references, positions, and sizes to help the AI target page controls.
- **`browser_actions`**: Chain mouse moves, hovers, clicks, scrolling, field filling, keyboard shortcuts, and waits in one call. Fill a search box, submit it, wait for results, and open a result without a separate call for each step.

    Moves and clicks target selectors, snapshot references, or coordinates; element targets wait and scroll into view. Supports movement in multiple steps, left, right, and middle clicks, double-clicks, and scrolling nested panels.

    Target fields anywhere on the page through selectors or snapshot references. Fill text, check or uncheck boxes, select radio buttons, and choose one or more native dropdown options by label. Replace or clear text, or type at the current caret. Keyboard shortcuts use the current focus. Slow mode adds random pauses between typed characters and all actions.

    Wait for content, loading overlays, page load events, or settled network activity, or add a fixed pause before continuing.
- **`browser_fetch`**: Fetch a page through an open browser session and extract HTML, Markdown, text, or a structured snapshot. Snapshots can cover the whole page or a chosen element and include element references, positions, and sizes for later interaction.

## ::: scrapling.core.ai.ScraplingMCPServer
    handler: python
    :docstring:
