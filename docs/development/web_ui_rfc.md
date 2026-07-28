# RFC: Optional local Web UI

**Status:** Proof of concept  
**Proposed by:** Ibrahim Khan Jagwal

## Summary

Add an optional, local-first Web UI for users who do not use MCP and want to operate Scrapling without writing code. The UI should remain a thin interface over Scrapling's public fetcher and parser APIs.

The proof of concept introduces:

- `scrapling ui`
- HTTP, dynamic, and stealth fetching modes
- CSS and XPath extraction
- Text, HTML, and Markdown representations
- Indexed job history in SQLite
- JSON and CSV exports
- Localhost-only binding and private-network target blocking by default

## Motivation

Scrapling currently serves Python developers, command-line users, and MCP-compatible AI clients. A browser interface makes selector experimentation and one-off extraction accessible to users who do not belong to those groups.

The UI is not intended to replace Python spiders or become a hosted scraping service. Its first role is a local extraction workbench.

## Architecture

```text
Browser UI
    |
Local Starlette application
    |-- Fetcher
    |-- DynamicFetcher
    |-- StealthyFetcher
    |-- Selector engine
    `-- SQLite job index
```

MCP remains an independent transport. A later iteration can extract common operation services shared by the UI and MCP adapters when doing so removes proven duplication.

## Packaging

The UI belongs behind an optional dependency:

```bash
pip install "scrapling[ui]"
```

Core parser users should not receive Starlette, Uvicorn, or browser dependencies unless they request the UI.

## Data model

The initial index stores one row per extraction:

- stable job identifier
- creation timestamp
- requested and final URLs
- fetch mode
- selector and selector type
- output representation
- response status
- duration
- title
- item count
- extracted values
- error information

SQLite is deliberately sufficient for a local proof of concept. A future crawler-oriented index should use a storage abstraction before adding page graphs, content hashes, full-text search, or schema inference.

## Security

The default design:

- binds to `127.0.0.1`
- accepts only `http` and `https` URLs
- resolves target hosts and rejects non-global IP addresses
- limits request timeouts
- escapes extracted values before rendering
- exposes only controlled database exports
- does not accept arbitrary output paths

Before supporting public deployment, the project would need authentication, CSRF protection, request and crawl quotas, stronger DNS-rebinding and redirect validation, secret handling, and an explicit remote-deployment threat model.

## Follow-up work

1. Saved projects and reusable extraction schemas.
2. Crawl progress, cancellation, and checkpoint controls.
3. Page-link graph and content-hash indexing.
4. Full-text search across extracted records.
5. Interactive selector highlighting in a sandboxed preview.
6. Configurable structured field mappings.
7. Authentication for deliberate remote deployments.

These should be discussed and reviewed separately instead of being bundled into the initial UI contribution.
