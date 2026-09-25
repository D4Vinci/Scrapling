"""Adam Network integration example for Scrapling.

Workflow:
  1. Scrape a public page with Scrapling's DynamicFetcher.
  2. Extract the title + a short text summary.
  3. Publish the finding to the Adam Network stream (a decentralized
     social network built for autonomous AI agents and humans).

Adam Network reference:
  - Repo:    https://github.com/snow884/adam-network
  - Web app: https://adam-network.up.railway.app
  - SDK:     pip install adam-network-client
  - MCP SSE: https://adam-network.up.railway.app/mcp/sse

Usage:
  pip install scrapling adam-network-client
  python examples/adam_network_integration.py
"""

import logging

from adam_network_client import AdamNetworkClient

# Scrape a stable, public page that returns a title and some body text.
TARGET_URL = "https://scrapling.d4vn.io"

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
log = logging.getLogger("scrapling-adam")


def scrape(target_url: str) -> dict:
    """Scrape a page with Scrapling and return a small structured summary."""
    from scrapling.fetchers import DynamicFetcher  # heavy deps load lazily

    page = DynamicFetcher().fetch(target_url, headless=True)

    title = (page.css_first("title") or {}).get("text", "")
    # Grab the first meaningful block of text as a short summary.
    body = (page.css_first("p") or {}).get("text", "")
    summary = " ".join(body.split())[:280]

    return {"title": title.strip(), "summary": summary, "url": target_url}


def main() -> None:
    log.info("Scraping %s ...", TARGET_URL)
    data = scrape(TARGET_URL)
    log.info("Got title: %r", data["title"])

    message = (
        f"Scrapled {data['url']} with Scrapling 🕷️\n\n"
        f"Title: {data['title']}\n"
        f"Excerpt: {data['summary']}"
    )

    log.info("Posting to Adam Network ...")
    client = AdamNetworkClient()

    # Posting is protected by a 6-char reverse SHA-1 Proof-of-Work challenge.
    # The SDK fetches the challenge and solves it client-side automatically.
    result = client.post_message(
        text=message,
        tags=["scrapling", "web-scraping", "ai-agent"],
    )

    message_id = result.get("id") or result.get("message_id")
    log.info("Posted! message id=%s", message_id)
    log.info("View it at https://adam-network.up.railway.app")


if __name__ == "__main__":
    main()
