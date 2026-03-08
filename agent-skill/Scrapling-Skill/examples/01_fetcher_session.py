"""
Example 1: Python - FetcherSession (persistent HTTP session with Chrome TLS fingerprint)

Scrapes all 10 pages of quotes.toscrape.com using a single HTTP session.
No browser launched — fast and lightweight.

Best for: static or semi-static sites, APIs, pages that don't require JavaScript.
"""

from scrapling.fetchers import FetcherSession

all_quotes = []

with FetcherSession(impersonate="chrome") as session:
    for i in range(1, 11):
        page = session.get(
            f"https://quotes.toscrape.com/page/{i}/",
            stealthy_headers=True,
        )
        quotes = page.css(".quote .text::text").getall()
        all_quotes.extend(quotes)
        print(f"Page {i}: {len(quotes)} quotes (status {page.status})")

print(f"\nTotal: {len(all_quotes)} quotes\n")
for i, quote in enumerate(all_quotes, 1):
    print(f"{i:>3}. {quote}")
