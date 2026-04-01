# import asyncio
# import time
# from scrapling.fetchers import AsyncStealthySession
# from scrapling.core.shell import Convertor

# class ScraplingCrawler:
#     """
#     A drop-in replacement for Crawl4AI's AsyncWebCrawler.
#     Uses Scrapling's Stealth Engine to bypass Cloudflare while returning Markdown.
#     """
    
#     def __init__(self, headless=True):
#         self.headless = headless

#     async def arun(self, url, solve_cloudflare=True):
#         """
#         Mimics Crawl4AI's arun method, but with Scrapling's bypass powers.
#         Returns a dictionary similar to CrawlResult.
#         """
#         # 1. Start the timer
#         start_time = time.time()
        
#         # 2. We use Scrapling's Stealth Engine for the actual bypass
#         async with AsyncStealthySession(headless=self.headless) as session:
#             print(f"[*] Navigating to {url}...")
            
#             # Fetch the page with specialized Cloudflare solving
#             page = await session.fetch(
#                 url, 
#                 solve_cloudflare=solve_cloudflare
#             )
            
#             if page.status != 200:
#                 print(f"[!] Error: Status Code {page.status}")

#             # Use Scrapling's built-in Markdown converter (inside Convertor class)
#             # This handles noise removal (scripts, styles) and formatting
#             print("[*] Converting HTML to Clean Markdown...")
#             markdown_gen = Convertor._extract_content(
#                 page, 
#                 extraction_type="markdown", 
#                 main_content_only=True
#             )
            
#             # 5. End the timer
#             # Convertor returns a generator, we join it into a single string
#             markdown_content = "".join(list(markdown_gen))
#             end_time = time.time()
#             elapsed_time = round(end_time - start_time, 2)

#             return {
#                 "url": url,
#                 "status": page.status,
#                 "success": page.status == 200,
#                 "markdown": markdown_content,
#                 "elapsed_time": elapsed_time,
#                 "metadata": {
#                     "title": page.xpath("//title/text()").get(),
#                     "final_url": page.url
#                 }
#             }

# async def main():
#     # TEST CASE: The NopeCHA Cloudflare Demo
#     url="https://nopecha.com/pricing"

    
#     crawler = ScraplingCrawler()
#     result = await crawler.arun(url)
    
#     print("\n" + "="*40)
#     print("🚀 SCRAPLING-BASED CRAWLER RESULT")
#     print("="*40)
#     print(f"Status:  {result['status']}")
#     print(f"Time:    {result['elapsed_time']} seconds")
#     print(f"Title:   {result['metadata']['title']}")
#     print("-" * 40)
#     print("MARKDOWN PREVIEW (First 500 chars):")
#     print("-" * 40)
#     # print(result['markdown'][:2000] + "...")
#     print(result['markdown'])
#     print("="*40)

# if __name__ == "__main__":
#     asyncio.run(main())







import asyncio
import time
from scrapling.fetchers import AsyncStealthySession
from scrapling.core.shell import Convertor

class ScraplingCrawler:
    def __init__(self, headless=True):
        self.headless = headless

    def is_cloudflare_blocked(self, page) -> bool:
        """Checks if the page is a splash screen or challenge page (Cloudflare, AWS WAF, GrubHub, etc)."""
        title = (page.xpath("//title/text()").get() or "").strip()
        # 403/503/202 status or known challenge titles
        is_blocked_status = page.status in (202, 403, 503, 429)
        is_challenge_title = any(keyword in title for keyword in [
            "Just a moment...", "Robot Check", "Security Verification", 
            "Prepare your taste buds", "Attention Required!"
        ])
        
        # If status is 200 but title is missing or contains 'Access Denied', it's a block
        return is_blocked_status or is_challenge_title or not title or "Access Denied" in title

    async def arun(self, url):
        start_time = time.time()
        
        async with AsyncStealthySession(headless=self.headless) as session:
            # --- PHASE 1: QUICK FETCH (No Solver) ---
            print(f"[*] Quick Fetch: {url}")
            page = await session.fetch(url, solve_cloudflare=False, network_idle=False)

            # --- PHASE 2: DETECTION & RETRY ---
            if self.is_cloudflare_blocked(page):
                print(f"[!] {url}: Block/Challenge Detected! Retrying with Solver...")
                # Re-fetch with the active solver enabled
                page = await session.fetch(url, solve_cloudflare=True, network_idle=False)
            else:
                print(f"[+] {url}: Success (Fast Pass).")

            # --- PHASE 3: CONVERSION ---
            markdown_gen = Convertor._extract_content(page, extraction_type="markdown", main_content_only=True)
            markdown_content = "".join(list(markdown_gen))
            
            elapsed_time = round(time.time() - start_time, 2)
            return {
                "url": url,
                "status": page.status,
                "markdown": markdown_content,
                "elapsed_time": elapsed_time,
                # "metadata": {"title": page.xpath("//title/text()").get()}
            }

async def main():
    # TEST CASE: The NopeCHA Cloudflare Demo
    # url="https://nopecha.com/pricing"
    # url="https://www.amazon.com/products"
    # url="https://www.stubhub.com"
    # url="https://www.zillow.com"
    # url="https://www.leboncoin.fr/"
    url="https://www.grubhub.com/"
    

    
    crawler = ScraplingCrawler()
    result = await crawler.arun(url)
    
    print("\n" + "="*40)
    print("SCRAPLING-BASED CRAWLER RESULT")
    print("="*40)
    print(f"Status:  {result['status']}")
    print(f"Time:    {result['elapsed_time']} seconds")
    # print(f"Title:   {result['metadata']['title']}")
    print("-" * 40)
    print("MARKDOWN PREVIEW:")
    print("-" * 40)
    # print(result['markdown'][:2000] + "...")
    print(result['markdown'])
    print("="*40)

if __name__ == "__main__":
    asyncio.run(main())
