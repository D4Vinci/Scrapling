from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, HttpUrl
from typing import List, Dict, Any
import uvicorn
import anyio

# Import your custom scrapers
from crawler_scrapling import ScraplingCrawler
from concurrent_crawler import ConcurrentScraplingCrawler
from searxng_spider import SmartScraplingSpider

app = FastAPI(
    title="Scrapling Stealth API",
    description="A high-performance scraping API with built-in Cloudflare bypass and Markdown extraction.",
    version="1.0.0"
)

# --- MODELS ---
class SingleUrlRequest(BaseModel):
    url: HttpUrl

class MultiUrlRequest(BaseModel):
    urls: List[HttpUrl]

# --- ENDPOINTS ---

@app.get("/health")
async def health_check():
    """Simple health check to verify the API is online."""
    return {"status": "online", "engine": "scrapling"}

@app.post("/scraper/single")
async def scrape_single(request: SingleUrlRequest):
    """
    Scrapes a single URL using the 'Smart Retry' logic.
    Used for one-off high-security page extraction.
    """
    try:
        crawler = ScraplingCrawler(headless=True)
        # Convert HttpUrl to string for Scrapling
        result = await crawler.arun(str(request.url))
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scraper Error: {str(e)}")

@app.post("/scraper/multiple")
async def scrape_multiple(request: MultiUrlRequest):
    """
    Scrapes multiple URLs concurrently using a shared browser session.
    Ideal for bulk processing search results or product lists.
    """
    try:
        # We reuse the ConcurrentScraplingCrawler we built
        crawler = ConcurrentScraplingCrawler(headless=True, max_concurrent=5)
        # Convert List[HttpUrl] to List[str]
        url_strings = [str(u) for u in request.urls]
        results = await crawler.arun(url_strings)
        return {"count": len(results), "results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Concurrent Scraper Error: {str(e)}")

@app.post("/scraper/spider")
async def scrape_with_spider(request: MultiUrlRequest):
    """
    Handles bulk requests using the professional SmartScraplingSpider.
    Features: built-in retries, automatic session switching, and detailed stats.
    """
    try:
        # Convert List[HttpUrl] to List[str] for the spider constructor
        url_strings = [str(u) for u in request.urls]
        
        # Instantiate and run the spider in a separate thread to avoid asyncio loop clashes
        spider = SmartScraplingSpider(urls=url_strings)
        
        # anyio.to_thread.run_sync allows the spider to start its own event loop safely
        crawl_result = await anyio.to_thread.run_sync(spider.start) 
        
        return {
            "stats": crawl_result.stats,
            "items": crawl_result.items
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Spider Crawl Error: {str(e)}")

# This allows running the file directly for testing
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
