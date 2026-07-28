# Scrapling Web UI

The optional Web UI is a local visual workspace for people who want to fetch pages, try selectors, inspect values, and export results without first writing a Python scraper or configuring an MCP client.

## Installation

Install the UI and fetcher dependencies:

```bash
pip install "scrapling[ui]"
```

Browser-based modes also require Chromium:

```bash
scrapling install
```

## Starting the UI

```bash
scrapling ui
```

Open [http://127.0.0.1:8001](http://127.0.0.1:8001) in a browser. The default listener is local-only.

The database is stored at `~/.scrapling/ui.db`. Choose another location when needed:

```bash
scrapling ui --database ./workspace.db
```

## Extraction modes

| Mode | Use case |
| --- | --- |
| HTTP | Fast extraction from static HTML |
| Dynamic | Pages that require JavaScript rendering |
| Stealth | Browser-rendered pages with stronger bot protection |

Every successful extraction is added to the local index with its URL, final URL, response status, selector, duration, and extracted values. Results can be exported as JSON or CSV.

## Network safety

The UI rejects localhost, private-network, and non-HTTP targets by default. This reduces the risk of a webpage or another user turning the interface into a server-side request forgery proxy.

For deliberate local development, private targets can be enabled explicitly:

```bash
scrapling ui --allow-private-targets
```

Do not use that option on a shared or publicly reachable machine. If the UI is exposed beyond localhost, place it behind an authenticated reverse proxy.

## Relationship to MCP

The Web UI and MCP server are separate interfaces:

- `scrapling ui` is for direct human interaction in a browser.
- `scrapling mcp` exposes tools to compatible AI clients.
- Python applications can continue using Scrapling's fetchers and spiders directly.

The UI uses the same fetchers and selector engine; it does not reimplement scraping behavior.
