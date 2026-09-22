---
search:
  exclude: true
---

# MCP Server API Reference

The **Scrapling MCP Server** provides fourteen powerful tools for web scraping through the Model Context Protocol (MCP). This server integrates Scrapling's capabilities directly into AI chatbots and agents, allowing conversational web scraping with advanced anti-bot bypass features.

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

The standardized response structure returned by the fetch and HTTP request tools. Bulk tools return a list of these responses. Session management tools use the models below, `screenshot` returns image and text content blocks, and `browser_snapshot` returns plain text.

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

`browser_snapshot(session_id, depth=None, boxes=False)` returns a plain-text AI ARIA snapshot of the current whole page in a dynamic or stealthy session. Use it after `session_fetch` finishes. It reads the existing page without navigation and includes element references. `depth` limits the tree depth, and `boxes=True` adds element positions and sizes in viewport CSS pixels. An unknown session, an HTTP request session, or a missing, closed, or busy page returns an error.

`session_fetch` also accepts `extraction_type="snapshot"` to take an AI ARIA snapshot after loading the requested URL. It returns the usual `status`, `url`, and `content` fields, with one unchanged snapshot string in `content`. The existing `css_selector` can scope the snapshot to exactly one element; zero or multiple matches return an error. Without a selector, the snapshot covers the whole page. `main_content_only` and `pierce_shadow` do not filter snapshots. This extraction type is only available on the MCP `session_fetch` tool; browser fetchers still return the same `Response` object.

## ::: scrapling.core.ai.ScraplingMCPServer
    handler: python
    :docstring:
