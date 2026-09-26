---
search:
  exclude: true
---

# MCP Server API Reference

The **Scrapling MCP Server** provides twenty tools for web scraping and browser interaction through the Model Context Protocol (MCP). This server integrates Scrapling's capabilities directly into AI chatbots and agents, allowing conversational web scraping with advanced anti-bot bypass features.

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

The standardized response structure returned by the fetch and HTTP request tools. Bulk tools return a list of these responses. Session management tools use the models below, `browser_screenshot` returns image and text content blocks, and `browser_snapshot`, `browser_mouse_move`, `browser_mouse_wheel`, `browser_click`, `browser_type`, `browser_fill_fields`, and `browser_press_key` return plain text.

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
- **`browser_mouse_move`**: Reveal hover menus and tooltips with the browser's mouse. Target elements through selectors or snapshot references, with automatic waiting and scrolling into view, or use coordinates with movement in multiple steps.
- **`browser_mouse_wheel`**: Scroll pages and nested panels vertically or horizontally with native mouse wheel events. Works at the current pointer position, so mouse movement can choose the scrollable area.
- **`browser_click`**: Click buttons, links, and other controls using selectors, snapshot references, or page coordinates. Supports left, right, and middle clicks, plus double-clicks.
- **`browser_type`**: Fill search boxes, login fields, text areas, and other editable content through selectors or snapshot references. Supports replacing or clearing text, typing one character at a time for key events, and pressing Enter after entry.
- **`browser_fill_fields`**: Fill text fields, check or uncheck boxes, select radio buttons, and choose one or more native dropdown options by visible labels in one call. Targets fields anywhere on the page through selectors or snapshot references and waits for each field to be ready. Slow mode types text one character at a time with random pauses between characters and fields.
- **`browser_press_key`**: Chain keys and shortcuts in one call to move between fields, submit forms, dismiss menus, or select and delete text. Each press uses the browser's current focus.
- **`browser_fetch`**: Fetch a page through an open browser session and extract HTML, Markdown, text, or a structured snapshot. Snapshots can cover the whole page or a chosen element and include element references, positions, and sizes for later interaction.

## ::: scrapling.core.ai.ScraplingMCPServer
    handler: python
    :docstring:
