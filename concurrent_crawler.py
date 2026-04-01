# import asyncio
# import time
# import json
# from typing import List, Dict, Any
# from scrapling.fetchers import AsyncStealthySession
# from scrapling.core.shell import Convertor

# class ConcurrentScraplingCrawler:
#     """
#     A High-Performance Concurrent Crawler powered by Scrapling.
#     Features:
#     - Shared Browser Session (saves memory/time)
#     - Smart Retry (try fast fetch -> if blocked, try solver)
#     - Markdown Output (ready for LLM ingestion)
#     """

#     def __init__(self, headless=True, max_concurrent=5):
#         self.headless = headless
#         self.max_concurrent = max_concurrent
#         self.semaphore = asyncio.Semaphore(max_concurrent)

#     def is_cloudflare_blocked(self, page) -> bool:
#         """Passive detection of Cloudflare protection screens."""
#         title = page.xpath("//title/text()").get() or ""
#         # 403/503 are standard WAF codes; "Just a moment..." is the Turnstile title
#         return page.status in (403, 503, 429) or "Just a moment..." in title

#     async def _scrape_url(self, session: AsyncStealthySession, url: str) -> Dict[str, Any]:
#         """The core logic for a single URL: Fast Fetch -> Detection -> Solver Retry."""
#         async with self.semaphore:
#             start_time = time.time()
#             try:
#                 # --- PHASE 1: QUICK FETCH (No Solver) ---
#                 print(f"[*] Quick Fetch: {url}")
#                 page = await session.fetch(url, solve_cloudflare=False, network_idle=False)

#                 # --- PHASE 2: DETECTION & RETRY ---
#                 if self.is_cloudflare_blocked(page):
#                     print(f"[!] {url}: Cloudflare Detected! Retrying with Solver...")
#                     # Re-fetch using the interactive solver (this takes ~10-30s)
#                     page = await session.fetch(url, solve_cloudflare=True, network_idle=False)
#                 else:
#                     print(f"[+] {url}: Success (Fast Pass).")

#                 # --- PHASE 3: MARKDOWN CONVERSION ---
#                 # We use Scrapling's built-in converter logic
#                 markdown_gen = Convertor._extract_content(
#                     page, 
#                     extraction_type="markdown", 
#                     main_content_only=True
#                 )
#                 markdown_content = "".join(list(markdown_gen))
                
#                 elapsed_time = round(time.time() - start_time, 2)
                
#                 return {
#                     "url": url,
#                     "status": page.status,
#                     "success": page.status == 200,
#                     "time": f"{elapsed_time}s",
#                     "markdown": markdown_content if page.status == 200 else "Failed to extract content.",
#                     "title": page.xpath("//title/text()").get() or "No Title"
#                 }

#             except Exception as e:
#                 print(f"[X] {url}: Execution Error: {str(e)}")
#                 return {
#                     "url": url,
#                     "status": 0,
#                     "success": False,
#                     "error": str(e),
#                     "markdown": ""
#                 }

#     async def arun(self, urls: List[str]) -> List[Dict[str, Any]]:
#         """Manager for concurrent requests using a shared session."""
#         print(f"🚀 Starting Concurrent Crawl for {len(urls)} URLs...")
        
#         # We share ONE browser session across ALL requests to be efficient
#         async with AsyncStealthySession(headless=self.headless) as session:
#             tasks = [self._scrape_url(session, url) for url in urls]
#             results = await asyncio.gather(*tasks)
#             return results

# async def test_concurrent():
#     # LIST OF TARGETS: Mix of Easy and Hard sites
#     test_urls = [
#         "https://www.google.com",               # Easy (Fast Fetch)
#         "https://nopecha.com/pricing",  # Hard (Requires Solver)
#         "https://www.amazon.com/products"       # High Security
#     ]
    
#     crawler = ConcurrentScraplingCrawler(headless=True, max_concurrent=3)
    
#     start_total = time.time()
#     results = await crawler.arun(test_urls)
#     end_total = time.time()

#     for i, r in enumerate(results):
#         filename = f"output_{i+1}.md"
        
#         with open(filename, "w", encoding="utf-8") as f:
#             f.write(r['markdown'])
        
#         print(f"Saved: {filename}")
#     # with open("concurrent_results.json", "w", encoding="utf-8") as f:
#     #     json.dump(results, f, indent=4, ensure_ascii=False)

#     # print("✅ Saved all results to concurrent_results.json")

#     print("\n" + "="*50)
#     print("🏁 CONCURRENT CRAWL SUMMARY")
#     print("="*50)
#     for r in results:
#         status_msg = "✅ PASS" if r.get("success") else "❌ FAIL"
#         print(f"{status_msg} | {r['time']:<8} | {r['url']}")
    
#     print("="*50)
#     print(f"Total Time for all: {round(end_total - start_total, 2)} seconds")
#     print("="*50)

# if __name__ == "__main__":
#     asyncio.run(test_concurrent())



import asyncio
import time
import json
from typing import List, Dict, Any
from scrapling.fetchers import AsyncStealthySession
from scrapling.core.shell import Convertor

class ConcurrentScraplingCrawler:
    """
    A High-Performance Concurrent Crawler powered by Scrapling.
    Features:
    - Shared Browser Session (saves memory/time)
    - Smart Retry (try fast fetch -> if blocked, try solver)
    - Markdown Output (ready for LLM ingestion)
    """

    def __init__(self, headless=True, max_concurrent=5):
        self.headless = headless
        self.max_concurrent = max_concurrent
        self.semaphore = asyncio.Semaphore(max_concurrent)

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

    async def _scrape_url(self, session: AsyncStealthySession, url: str) -> Dict[str, Any]:
        """The core logic for a single URL: Fast Fetch -> Detection -> Solver Retry."""
        async with self.semaphore:
            start_time = time.time()
            try:
                # --- PHASE 1: QUICK FETCH (No Solver) ---
                print(f"[*] Quick Fetch: {url}")
                page = await session.fetch(url, solve_cloudflare=False, network_idle=False)

                # --- PHASE 2: DETECTION & RETRY ---
                if self.is_cloudflare_blocked(page):
                    print(f"[!] {url}: Block/Challenge Detected! Retrying with Solver...")
                    # Re-fetch using the interactive solver (this takes ~10-30s)
                    page = await session.fetch(url, solve_cloudflare=True, network_idle=False)
                else:
                    print(f"[+] {url}: Success (Fast Pass).")

                # --- PHASE 3: MARKDOWN CONVERSION ---
                # We use Scrapling's built-in converter logic
                markdown_gen = Convertor._extract_content(
                    page, 
                    extraction_type="markdown", 
                    main_content_only=True
                )
                markdown_content = "".join(list(markdown_gen))
                
                elapsed_time = round(time.time() - start_time, 2)
                
                return {
                    "url": url,
                    "status": page.status,
                    "success": page.status == 200,
                    "time": f"{elapsed_time}s",
                    "markdown": markdown_content if page.status == 200 else "Failed to extract content.",
                    "title": page.xpath("//title/text()").get() or "No Title"
                }

            except Exception as e:
                print(f"[X] {url}: Execution Error: {str(e)}")
                return {
                    "url": url,
                    "status": 0,
                    "success": False,
                    "error": str(e),
                    "markdown": ""
                }

    async def arun(self, urls: List[str]) -> List[Dict[str, Any]]:
        """Manager for concurrent requests using a shared session."""
        print(f"🚀 Starting Concurrent Crawl for {len(urls)} URLs...")
        
        # We share ONE browser session across ALL requests to be efficient
        async with AsyncStealthySession(headless=self.headless) as session:
            tasks = [self._scrape_url(session, url) for url in urls]
            results = await asyncio.gather(*tasks)
            return results

async def test_concurrent():
    # LIST OF TARGETS: Mix of Easy and Hard sites
    test_urls = [
        # "https://www.cloudflare.com",
        # "https://www.g2.com",
        # "https://www.ticketmaster.com",
        # "https://www.nike.com",
        # "https://www.stubhub.com"



        "https://www.google.com",               # Easy (Fast Fetch)
        "https://nopecha.com/pricing",
        "https://nopecha.com/demo/cloudflare",  # Hard (Requires Solver)
        "https://www.amazon.com/products"   
            # High Security
    ]
    
    crawler = ConcurrentScraplingCrawler(headless=True, max_concurrent=5)
    
    start_total = time.time()
    results = await crawler.arun(test_urls)
    end_total = time.time()

    # Save all results into a single file
    output_filename = "combined_results.md"
    with open(output_filename, "w", encoding="utf-8") as f:
        for i, r in enumerate(results):
            f.write(f"# URL {i+1}: {r['url']}\n")
            f.write(f"**Status:** {r['status']} | **Time:** {r['time']}\n\n")
            f.write(r['markdown'])
            f.write("\n\n" + "-"*50 + "\n\n")  # Add a separator between contents
            
    print(f"✅ Saved all results to {output_filename}")
    # with open("concurrent_results.json", "w", encoding="utf-8") as f:
    #     json.dump(results, f, indent=4, ensure_ascii=False)

    # print("✅ Saved all results to concurrent_results.json")

    print("\n" + "="*50)
    print("🏁 CONCURRENT CRAWL SUMMARY")
    print("="*50)
    for r in results:
        status_msg = "✅ PASS" if r.get("success") else "❌ FAIL"
        print(f"{status_msg} | {r['time']:<8} | {r['url']}")
    
    print("="*50)
    print(f"Total Time for all: {round(end_total - start_total, 2)} seconds")
    print("="*50)

if __name__ == "__main__":
    asyncio.run(test_concurrent())








# Start
#   ↓
# Open shared browser
#   ↓
# For each URL:
#    ↓
#    Quick Fetch ⚡
#    ↓
#    Blocked? → YES → Solve Challenge 🛡️
#              NO  → Continue
#    ↓
#    Extract Markdown 📄
#    ↓
# Return result
#   ↓
# Save all results
#   ↓
# Print summary



