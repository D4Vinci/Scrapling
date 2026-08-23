# Building RAG Systems with Scrapling

RAG pipelines are only as good as the text you feed them. Raw HTML wastes tokens on markup, navigation, scripts, and tracking noise, and it can even carry hidden prompt-injection content straight into your LLM. Scrapling turns pages and whole websites into clean, sanitized Markdown with no LLM in the loop, so your ingestion runs fast and costs nothing per page.

## Installation

```bash
pip install "scrapling[rag]"

scrapling install
```

The `rag` extra installs the fetchers with Markdown conversion support (the `ai`, `shell`, and `all` extras include it too). The `scrapling install` command downloads the browser dependencies, which you only need for the browser-based fetchers.

## One page to Markdown

Every [Response](../fetching/choosing.md#response-object) has a `markdown()` method:

```python
from scrapling.fetchers import Fetcher

markdown = Fetcher.get("https://example.com").markdown(main_content_only=True)
```

It works with all fetchers, so pages behind Cloudflare are one line away too:

```python
from scrapling.fetchers import StealthyFetcher

markdown = StealthyFetcher.fetch("https://protected.example.com", solve_cloudflare=True).markdown(main_content_only=True)
```

Two arguments control the output:

- `main_content_only`: Convert only the content inside the page's `<body>` tag.
- `css_selector`: Convert only the elements matching a CSS selector (all matches are concatenated). Use it to extract exactly the part your pipeline needs and save tokens:

```python
markdown = Fetcher.get("https://example.com/docs/page").markdown(css_selector="article")
```

Whatever you pass, scripts, styles, and hidden content are always removed before conversion. This is the same cleaning the [MCP server](mcp-server.md) uses to protect AI agents from prompt injection: CSS-hidden elements, `aria-hidden` elements, `<template>` tags, HTML comments, and zero-width characters never reach your model.

## A whole website to a Markdown corpus

The `SiteToMarkdownSpider` template crawls a website and converts every page, powered by the [spiders framework](../spiders/architecture.md), so you get concurrency, autothrottle, robots.txt compliance, and pause/resume for free:

```python
from scrapling.spiders import SiteToMarkdownSpider

class DocsSpider(SiteToMarkdownSpider):
    name = "docs"
    start_urls = ["https://example.com/docs/"]
    allowed_domains = {"example.com"}
    output_dir = "docs_markdown"
    max_pages = 200

result = DocsSpider().start()
result.items.to_jsonl("docs.jsonl")
```

Each crawled page becomes one item with `url`, `title`, and `markdown` keys. With `output_dir` set, each page is also written to a Markdown file named after its URL, so the run above gives you both a folder of `.md` files and a `docs.jsonl` ready for ingestion.

The template requires `allowed_domains` so the crawl stays bound to the target website. The options:

- `css_selector` / `main_content_only`: Passed to `markdown()` for every page, with `main_content_only` enabled by default.
- `output_dir`: When set, writes one Markdown file per page.
- `max_pages`: Maximum number of pages to convert. Requests already queued when the cap hits may still be fetched, but they aren't converted. `0` (the default) disables it.

Every page link inside `allowed_domains` is followed by default. Since the template builds on [CrawlSpider](../spiders/generic-templates.md#crawlspider), override `rules()` with your own [LinkExtractor](../spiders/generic-templates.md#linkextractor-reference) to control the crawl: `allow` narrows it to the URL patterns you want, and `deny` drops the patterns you don't (login pages, tag listings, print views, etc.):

```python
from scrapling.spiders import CrawlRule, LinkExtractor, SiteToMarkdownSpider

class DocsSpider(SiteToMarkdownSpider):
    name = "docs"
    start_urls = ["https://example.com/"]
    allowed_domains = {"example.com"}

    def rules(self):
        return [CrawlRule(LinkExtractor(allow=r"/docs/", deny=[r"/docs/changelog/", r"\?print="]))]
```

`deny` wins over `allow`, and a rule can carry a `priority` or a `process_request` hook as with any **CrawlSpider**.

## Feeding a vector store

The JSONL output plugs into any embedding pipeline. A minimal example:

```python
import json

with open("docs.jsonl") as f:
    for line in f:
        page = json.loads(line)
        for chunk in split_into_chunks(page["markdown"]):
            vector_store.add(text=chunk, metadata={"url": page["url"], "title": page["title"]})
```

Use `css_selector` on the spider to cut boilerplate before chunking instead of cleaning it downstream. The less noise you embed, the better your retrieval.

## Interactive alternatives

For conversational scraping instead of pipelines, the [MCP server](mcp-server.md) gives your AI chatbot the same Markdown extraction as tools, and the [Agent skill](agent-skill.md) teaches coding agents to write this code themselves.
