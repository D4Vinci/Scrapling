# from scrapling.spiders import Spider, Response, Request
# from scrapling.fetchers import AsyncStealthySession

# class SearxngScraplingSpider(Spider):
#     name = "searxng_iherb"
    
#     def configure_sessions(self, manager):
#         # We still need the stealthy browser because both SearXNG and iHerb have bot protections
#         manager.add("stealth", AsyncStealthySession(headless=True, wait=2000), lazy=True)

#     async def start_requests(self):
#         # 1. Phase One: SearXNG
#         # We query a prominent public SearXNG instance (search.disroot.org). 
#         # Using "site:iherb.com" strictly limits DuckDuckGo/Google results to our target store.
#         query = "site:iherb.com Vitamin C 1000mg"
#         search_url = f"https://search.disroot.org/search?q={query.replace(' ', '+')}"
        
#         print(f"STARTING Launching SearXNG Query: {search_url}")
        
#         yield Request(
#             url=search_url, 
#             sid="stealth", 
#             callback=self.parse
#         )

#     async def parse(self, response: Response):
#         print(f"\nSUCCESS Successfully breached SearXNG! Extracting Top 5 links...")
        
#         # 2. Extract links from SearXNG's result page
#         # SearXNG uses clean HTML without heavily obfuscated classes
#         all_links = response.css('a::attr(href)').getall()
#         product_urls = []
        
#         for link in all_links:
#             # We strictly hunt for valid iHerb product links 
#             if 'iherb.com/pr/' in link and link not in product_urls:
#                 product_urls.append(link)
#                 if len(product_urls) == 5:  # Get Top 5 as requested!
#                     break
                    
#         print(f"TARGET Extracted exactly {len(product_urls)} links! Dispatching Scrapling directly to iHerb...")
        
#         # 3. Phase Two: Scrapling
#         # Fire Scrapling Stealthy Fetchers at those 5 links concurrently!
#         for url in product_urls:
#             yield Request(
#                 url=url, 
#                 sid="stealth", 
#                 callback=self.parse_product
#             )

#     async def parse_product(self, response: Response):
#         print(f"DATA Scraping Data directly from iHerb: {response.url}")
        
#         # Exact same robust CSS selectors parsing the Schema data
#         title = response.css('.product-title::text, h1::text, [itemprop="name"]::text').get()
#         price = response.css('[itemprop="price"]::attr(content), [itemprop="price"]::text, [data-qa="price"]::text, bdi::text, #price::text').get()
        
#         desc_raw = response.css('[itemprop="description"] *::text, section[aria-labelledby="product-overview"] *::text, article *::text').getall()
#         description = " ".join([text.strip() for text in desc_raw if text.strip()])

#         yield {
#             "title": title.strip() if title else "Not Found",
#             "price": price.strip() if price else "Not Found",
#             "description_preview": description[:120] + "..." if description else "Not Found",
#             "url": response.url
#         }


# if __name__ == "__main__":
#     spider_result = SearxngScraplingSpider().start()
#     spider_result.items.to_json("searxng_combined_results.json")
#     print("\nSUCCESS Finished! Architecture Complete. Data saved to 'searxng_combined_results.json'")















# This is an advanced web crawler (Spider) using Scrapling.

# It:

# Crawls multiple URLs 
# First tries fast scraping 
# If blocked → switches to Cloudflare solver 
# Extracts main content as Markdown 
# Saves everything into a file

import asyncio
from typing import AsyncGenerator, Dict, Any
from scrapling.spiders import Spider, Request, Response
from scrapling.fetchers import AsyncStealthySession
from scrapling.core.shell import Convertor
import time

class SmartScraplingSpider(Spider):
    """
    A professional Scrapling Spider that uses 'Smart Retry' logic.
    It attempts a fast fetch first and only switches to the 
    intensive Cloudflare solver if a block is detected.
    """
    name = "smart_markdown_spider"
    
    # Increase concurrency to 5 (default is 4)
    concurrent_requests = 10

    def configure_sessions(self, manager):
        """
        Define two session profiles:
        1. 'fast' - Quick stealthy browser, no active solver.
        2. 'solver' - High-security solver for Cloudflare challenges.
        """
        # Session 1: High-Stealth but Passive (Fast)
        manager.add("fast", AsyncStealthySession(headless=True), lazy=True)
        
        # Session 2: Active Solver (Powerful but Slower)
        manager.add("solver", AsyncStealthySession(headless=True, solve_cloudflare=True), lazy=True)

    def __init__(self, urls: list[str] = None):
        """
        Allows the spider to be initialized with a custom list of URLs.
        If none provided, it defaults to the test list.
        """
        super().__init__()
        self.start_urls = urls or [
            "https://www.google.com",
            "https://nopecha.com/demo/cloudflare",
            "https://www.amazon.com/products"
        ]

    async def start_requests(self):
        """Yield the initial URLs using the 'fast' session from the provided list."""
        for url in self.start_urls:
            yield Request(url, sid="fast", meta={"start_time": time.time()})

    def is_cloudflare_blocked(self, response: Response) -> bool:
        """Custom detection for Cloudflare, AWS WAF, and GrubHub splash screens."""
        title = (response.xpath("//title/text()").get() or "").strip()
        # 403/503/202 status or known challenge titles
        is_blocked_status = response.status in (403, 503, 429, 202)
        is_challenge_title = any(keyword in title for keyword in [
            "Just a moment...", "Robot Check", "Security Verification", 
            "Prepare your taste buds", "Attention Required!"
        ])
        
        # If status is 200 but title is missing or contains 'Access Denied', it's a block
        return is_blocked_status or is_challenge_title or not title or "Access Denied" in title

    async def is_blocked(self, response: Response) -> bool:
        """Link the custom detection to the Spider's internal retry engine."""
        return self.is_cloudflare_blocked(response)

    async def retry_blocked_request(self, request: Request, response: Response) -> Request:
        """
        When a block is detected, this hook is called.
        We use it to upgrade the session to 'solver' for the next try.
        """
        if request.sid == "fast":
            self.logger.warning(f"🔄 UPGRADE: Switching {request.url} to 'solver' session...")
            request.sid = "solver"
            # Reset retry count if needed or just let it continue
        return request

    async def parse(self, response: Response) -> AsyncGenerator[Dict[str, Any] | Request, None]:
        """
        Process successful responses. 
        If we are here, it means the page passed the is_blocked check.
        """
        url = response.url
        sid = response.request.sid

        self.logger.info(f"✅ SUCCESS: {url} retrieved using '{sid}' session.")

        start_time = response.request.meta.get("start_time", time.time())
        elapsed_time = round(time.time() - start_time, 2)
        
        # --- Convert to Markdown ---
        markdown_gen = Convertor._extract_content(
            response, 
            extraction_type="markdown", 
            main_content_only=True
        )
        markdown_content = "".join(list(markdown_gen))
        
        yield {
            "url": url,
            "status": response.status,
            "session_used": sid,
            "title": response.xpath("//title/text()").get(),
            "time": f"{elapsed_time}s",
            "markdown": markdown_content
        }

if __name__ == "__main__":
    spider = SmartScraplingSpider()
    result = spider.start()

    output_file = "spider_results.md"
    # result.items.to_json("spider_results.json")

    with open(output_file, "w", encoding="utf-8") as f:
        for i, item in enumerate(result.items):
            f.write(f"# URL {i+1}: {item['url']}\n")
            f.write(f"**Status:** {item['status']} | **Session:** {item['session_used']} | **Time:** {item['time']}\n\n")
            f.write(f"**Title:** {item['title']}\n\n")
            f.write(item['markdown'])
            f.write("\n\n" + "-"*60 + "\n\n")

    print(f"Results saved to: {output_file}")

    print("\n" + "="*50)
    print("🏁 SPIDER CRAWL COMPLETE")
    print("="*50)
    print(f"Total Items: {len(result.items)}")
    print("="*50)
    



# Start spider
#    ↓
# Send all URLs (fast session)
#    ↓
# For each URL:
#    ↓
# Try fast fetch
#    ↓
# If success → parse → done 
#    ↓
# If blocked → retry_blocked_request()
#    ↓
# Switch to solver
#    ↓
# Solve Cloudflare
#    ↓
# Success → parse → done 
#    ↓
# Convert to markdown
#    ↓
# Save results