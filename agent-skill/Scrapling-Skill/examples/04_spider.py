"""
Example 4: Python - Spider (auto-crawling framework)

Scrapes ALL pages of quotes.toscrape.com by following "Next" pagination links
automatically. No manual page looping needed.

The spider yields structured items (text + author + tags) and exports them to JSON.

Best for: multi-page crawls, full-site scraping, anything needing pagination or
link following across many pages.

Outputs:
  - Live stats to terminal during crawl
  - Final crawl stats at the end
  - quotes.json in the current directory
"""

from scrapling.spiders import Spider, Response


class QuotesSpider(Spider):
    name = "quotes"
    start_urls = ["https://quotes.toscrape.com/"]
    concurrent_requests = 5  # Fetch up to 5 pages at once

    async def parse(self, response: Response):
        # Extract all quotes on the current page
        for quote in response.css(".quote"):
            yield {
                "text": quote.css(".text::text").get(),
                "author": quote.css(".author::text").get(),
                "tags": quote.css(".tags .tag::text").getall(),
            }

        # Follow the "Next" button to the next page (if it exists)
        next_page = response.css(".next a")
        if next_page:
            yield response.follow(next_page[0].attrib["href"])


if __name__ == "__main__":
    result = QuotesSpider().start()

    print(f"\n{'=' * 50}")
    print(f"Scraped : {result.stats.items_scraped} quotes")
    print(f"Requests: {result.stats.requests_count}")
    print(f"Time    : {result.stats.elapsed_seconds:.2f}s")
    print(f"Speed   : {result.stats.requests_per_second:.2f} req/s")
    print(f"{'=' * 50}\n")

    for i, item in enumerate(result.items, 1):
        print(f"{i:>3}. [{item['author']}] {item['text']}")
        if item["tags"]:
            print(f"       Tags: {', '.join(item['tags'])}")

    # Export to JSON
    result.items.to_json("quotes.json", indent=True)
    print("\nExported to quotes.json")
