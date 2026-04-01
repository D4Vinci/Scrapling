import asyncio
from scrapling.fetchers import AsyncStealthySession

async def scrape_iherb_vitamins():
    # This matches your "query": "Vitamin C 1000mg supplement iherb"
    search_url = "https://www.iherb.com/search?kw=Vitamin+C+1000mg"
    
    # We use AsyncStealthySession to fetch multiple pages quickly while bypassing bot protection
    async with AsyncStealthySession(headless=True, wait=2000) as session:
        
        print(f"Phase 1: Searching iHerb for products...")
        search_page = await session.fetch(search_url)
        
        # Extract all links, filter to find exactly 3 product URLs (matches "max_urls": 3)
        # iHerb product links always contain '/pr/'
        all_links = search_page.css('a::attr(href)').getall()
        product_urls = []
        for link in all_links:
            if '/pr/' in link and link not in product_urls:
                product_urls.append(link)
                if len(product_urls) == 3:  # Stop at 3
                    break
                    
        print(f"Found {len(product_urls)} products! Now scraping them at the same time...")
        
        # Phase 2: Fetch all 3 product pages concurrently
        tasks = [session.fetch(url) for url in product_urls]
        product_pages = await asyncio.gather(*tasks)
        
        # Phase 3: Extract the specific CSS tags from your JSON
        results = []
        for page in product_pages:
            
            # Since real CSS class names vary, we add fallbacks (including Schema.org's itemprop) to make sure we grab the right data
            title = page.css('.product-title::text, h1::text, [itemprop="name"]::text').get()
            price = page.css('[itemprop="price"]::attr(content), [itemprop="price"]::text, [data-qa="price"]::text, bdi::text, #price::text').get()
            
            # Extract descriptions, clean whitespace, and join together
            desc_raw = page.css('[itemprop="description"] *::text, section[aria-labelledby="product-overview"] *::text, article *::text').getall()
            description = " ".join([text.strip() for text in desc_raw if text.strip()])
            
            results.append({
                "url": page.url,
                "title": title.strip() if title else "Not Found",
                "price": price.strip() if price else "Not Found",
                "description_preview": description[:150] + "..." if description else "Not Found"
            })
            
        # Print final JSON-like output
        print("\n=== FINAL RESULTS ===")
        for count, item in enumerate(results, 1):
            print(f"\nProduct #{count}:")
            print(f"Title: {item['title']}")
            print(f"Price: {item['price']}")
            print(f"URL: {item['url']}")
            print(f"Desc: {item['description_preview']}")

if __name__ == "__main__":
    # Start the async execution
    asyncio.run(scrape_iherb_vitamins())
