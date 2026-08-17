from urllib.parse import urldefrag, urljoin, urlparse
from scrapling.spiders import Request, Response, Spider

TARGET = "https://devconsoleconsulting.com/"
HOSTS = {"devconsoleconsulting.com", "www.devconsoleconsulting.com"}
SKIP = (".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg", ".ico", ".pdf", ".zip", ".mp4", ".mp3", ".css", ".js", ".xml", ".json", ".woff", ".woff2", ".ttf")


def clean_url(base, href):
    href = (href or "").strip()
    if not href or href.startswith(("#", "mailto:", "tel:", "javascript:")):
        return None
    url, _ = urldefrag(urljoin(base, href))
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"} or parsed.hostname not in HOSTS:
        return None
    if parsed.path.lower().endswith(SKIP):
        return None
    if any(x in parsed.path.lower() for x in ("/wp-admin", "/wp-login", "/feed/")):
        return None
    return url


class DevConsoleSpider(Spider):
    name = "devconsoleconsulting"
    start_urls = [TARGET]
    concurrent_requests = 4
    robots_txt_obey = True
    autothrottle_enabled = True

    async def parse(self, response: Response):
        links = sorted({u for href in response.css("a::attr(href)").getall() if (u := clean_url(response.url, href))})
        yield {
            "url": response.url,
            "title": response.css("title::text").get(),
            "meta_description": response.css('meta[name="description"]::attr(content)').get(),
            "canonical": response.css('link[rel="canonical"]::attr(href)').get(),
            "lang": response.css("html::attr(lang)").get(),
            "h1": response.css("h1::text").getall(),
            "h2": response.css("h2::text").getall(),
            "headings": response.css("h1::text, h2::text, h3::text").getall(),
            "paragraphs": response.css("p::text").getall(),
            "internal_links": links,
        }
        for url in links:
            yield Request(url, callback=self.parse)


if __name__ == "__main__":
    result = DevConsoleSpider(crawldir="./crawl_data/devconsole").start()
    result.items.to_json("devconsoleconsulting-scrape.json")
    print(f"Scraped {len(result.items)} pages -> devconsoleconsulting-scrape.json")
