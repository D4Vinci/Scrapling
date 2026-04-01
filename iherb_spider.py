from scrapling.spiders import Spider, Response, Request
from scrapling.fetchers import AsyncStealthySession

class IHerbSpider(Spider):
    name = "iherb_vitamins"
    
    def configure_sessions(self, manager):
        # Register a stealth browser under the name ID "stealth"
        manager.add("stealth", AsyncStealthySession(headless=True, wait=2000), lazy=True)

    # Instead of 'start_urls', we use 'start_requests' to strictly force the 
    # stealth session right from the very first search page
    async def start_requests(self):
        yield Request(
            url="https://www.iherb.com/search?kw=Vitamin+C+1000mg", 
            sid="stealth",               # Route through the Stealthy browser
            callback=self.parse          # Tell the spider where to send the HTML once loaded
        )

    # PAGE 1: The Search Results
    async def parse(self, response: Response):
        print(f"\n✅ Fetched Search Results: {response.url}")
        
        # 1. Grab all links
        all_links = response.css('a::attr(href)').getall()
        product_urls = []
        
        # 2. Filter for 3 product links
        for link in all_links:
            if '/pr/' in link and link not in product_urls:
                product_urls.append(link)
                if len(product_urls) == 3:  # Stop at 3
                    break
        
        print(f"🎯 Found {len(product_urls)} products! Dispatching spiders...")
        
        # 3. Tell the Spider to navigate to the 3 newly discovered links
        for url in product_urls:
            yield Request(
                url=url, 
                sid="stealth",                # Must stay stealthy!
                callback=self.parse_product   # Send these pages to our product extractor below!
            )

    # PAGE 2: The Individual Products
    async def parse_product(self, response: Response):
        print(f"📦 Scraping Product: {response.url}")
        
        title = response.css('.product-title::text, h1::text, [itemprop="name"]::text').get()
        price = response.css('[itemprop="price"]::attr(content), [itemprop="price"]::text, [data-qa="price"]::text, bdi::text, #price::text').get()
        
        desc_raw = response.css('[itemprop="description"] *::text, section[aria-labelledby="product-overview"] *::text, article *::text').getall()
        description = " ".join([text.strip() for text in desc_raw if text.strip()])

        # 4. By 'yielding' a dictionary instead of a Request, Scrapling 
        # recognizes this as final extracted Data rather than a link to follow!
        yield {
            "title": title.strip() if title else "Not Found",
            "price": price.strip() if price else "Not Found",
            "description_preview": description[:150] + "..." if description else "Not Found",
            "url": response.url
        }


if __name__ == "__main__":
    print("🚀 Running IHerb Spider...")
    
    # Start the spider crawler
    spider_result = IHerbSpider().start()
    
    # The magical one-liner! Takes all dictionaries yielded across 
    # all concurrent pages and merges them into a single clean JSON file
    spider_result.items.to_json("iherb_spider_results.json")
    print("\n✅ Finished! Data safely written to 'iherb_spider_results.json'")
