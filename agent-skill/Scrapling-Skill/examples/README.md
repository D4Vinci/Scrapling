# Scrapling Examples

These examples scrape [quotes.toscrape.com](https://quotes.toscrape.com), a site built for scraping practice. They show HTTP sessions, browser sessions, and spiders.

The demo site has **100 quotes across 10 pages**. Each example follows pagination to collect them.

## Quick Start

Make sure Scrapling is installed:

```bash
pip install "scrapling[all]>=0.5"
scrapling install
```

## Examples

| File                     | Tool              | Type                        | Best For                              |
|--------------------------|-------------------|-----------------------------|---------------------------------------|
| `01_fetcher_session.py`  | `FetcherSession`  | Python - persistent HTTP    | APIs, fast multi-page scraping        |
| `02_browser_session.py`  | `StealthySession`  | Python - browser automation | Dynamic/SPA pages                     |
| `03_stealthy_session.py` | `StealthySession` | Python - stealth browser    | Cloudflare, fingerprint bypass        |
| `04_spider.py`           | `Spider`          | Python - auto-crawling      | Multi-page crawls, full-site scraping |

## Escalation Guide

Start with the fastest, lightest option and escalate only if needed:

```
get / FetcherSession
  └─ If JavaScript or anti-bot handling is needed → fetch / StealthySession
       └─ If multi-page → Spider
```
