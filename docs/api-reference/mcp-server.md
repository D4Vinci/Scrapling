---
search:
  exclude: true
---

# MCP Server API Reference

The **Scrapling MCP Server** provides six powerful tools for web scraping through the Model Context Protocol (MCP). This server integrates Scrapling's capabilities directly into AI chatbots and agents, allowing conversational web scraping with advanced anti-bot bypass features.

You can start the MCP server by running:

```bash
scrapling mcp
```

Or import the server class directly:

```python
from scrapling.core.ai import ScraplingMCPServer

server = ScraplingMCPServer()
server.serve()
```

## Response Model

The standardized response structure that's returned by all MCP server tools:

## ::: scrapling.core.ai.ResponseModel
    handler: python
    :docstring:

## MCP Server Class

The main MCP server class that provides all web scraping tools:

## ::: scrapling.core.ai.ScraplingMCPServer
    handler: python
    :docstring: