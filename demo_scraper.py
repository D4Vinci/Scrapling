# from scrapling.spiders import Spider, Response
# from scrapling.fetchers import StealthyFetcher

# class MySpider(Spider):
#     name = "multi_site_spider"
#     fetcher ="stealthyFetcher"
    
#     # Your 4 specific URLs
#     # start_urls = [
#     #     "https://www.cloudflare.com",
#     #     "https://www.digitalocean.com",
#     #     "https://www.creativecommons.org",
#     #     "https://www.bbb.org"
#     # ]
#     start_urls = [
#     "https://www.linkedin.com/jobs",   # will block
#     "https://www.amazon.com/products", # will block
#     "https://www.ticketmaster.com",    # will block
# ]
    
#     concurrent_requests = 4  # all 4 at the same time

#     async def parse(self, response: Response):
#         yield {
#             "url": response.url,
#         "body": response.css('body *::text').getall()
#       #  "title": response.css('title::text').get()

#         }

# print("Running spider...")
# spider_result = MySpider().start()

# spider_result.items.to_json("multi_site_data_3.json")
# print("Finished! Data saved to multi_site_data_1n")





# from scrapling.fetchers import StealthyFetcher
# url = "https://nopecha.com/demo/cloudflare"
# # url="https://in.iherb.com/"
# # url="https://www.amazon.com/products"
# print("Opening a stealthy invisible browser to bypass protection...")
# page = StealthyFetcher.fetch(url, headless=True, network_idle=True,solve_cloudflare=True )
# title = page.xpath('//title/text()').get()
# print(page.xpath('//title').get())
# print(f"Success! We bypassed protection and read the title: '{title}'")






import time
from scrapling.fetchers import StealthyFetcher

# url = "https://nopecha.com/demo/cloudflare"
url="https://nopecha.com/pricing"
# url="https://www.amazon.com/products"
print(f"🚀 Starting Stealthy Fetch for: {url}")
print("🔍 Solving Cloudflare... (Please wait, this takes time)")

# 1. Start the timer
start_time = time.time()

# 2. Perform the fetch
page = StealthyFetcher.fetch(
    url, 
    headless=True,
    # network_idle=True, 
    solve_cloudflare=True 
)

# 3. Extract data
# Fixed: Scrapling uses .status instead of .status_code
status = page.status 
title_element = page.xpath('//title/text()').get()
title = title_element.strip() if title_element else "No Title Found"

# 4. Process all text
# Optional: Print first few text chunks for verification
all_text = page.css('body :not(script):not(style)::text').getall()
clean_text = [t.strip() for t in all_text if t.strip()]

# 5. End the timer
end_time = time.time()
total_duration = round(end_time - start_time, 2)

# 5. PRINT YOUR CUSTOM METADATA
print("\n" + "="*40)
print("📦 FETCH METADATA SUMMARY")
print("="*40)
print(f"✅ Status Code:    {status}")
print(f"⏱️  Total Duration: {total_duration} seconds")
print(f"🌍 Final URL:      {page.url}")
print(f"📝 Page Title:     '{title}'")
print("="*40)

print(f"\nExtracted {len(clean_text)} clean text chunks.")
print(f"Preview: {clean_text[:200]}")
