from scrapling.spiders import Spider, Response, Request
from scrapling.fetchers import AsyncStealthySession

class MySpider(Spider):
    name = "multi_site_spider"

    def configure_sessions(self, manager):
        # This properly registers the "Invisible Browser"
        manager.add("stealth", AsyncStealthySession(headless=True, wait=2000), lazy=True)

    async def start_requests(self):
        urls = [
            "https://www.linkedin.com/jobs",
            "https://www.amazon.com/products",
            "https://nopecha.com",
        ]
        for url in urls:
            # We must tell the request to use the 'stealth' session we registered
            yield Request(url, sid="stealth")

    async def parse(self, response: Response):
        # 1. Grab the visible page Title
        title = response.css('title::text').get()
        
        # 2. Grab the Meta Description (what shows up in Google search results)
        # We check both the standard name="description" and the social og:description
        description = response.css('meta[name="description"]::attr(content), meta[property="og:description"]::attr(content)').get()

        yield {
            "url": response.url,
            "title": title.strip() if title else "Not Found",
            "description": description.strip() if description else "Not Found"
        }

if __name__ == "__main__":
    print("STARTING Running Clean Data Spider...")
    spider_result = MySpider().start()
    spider_result.items.to_json("multi_site_clean_results.json")
    print("\nSUCCESS Finished! Data saved to 'multi_site_clean_results.json'")
