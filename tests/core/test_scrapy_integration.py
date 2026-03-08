from scrapling.integrations.scrapy import ScraplingScrapyResponse, use_scrapling


class DummyResponse:
    def __init__(self):
        self.url = "https://example.com"
        self.text = "<html><body><a href='/x'>X</a></body></html>"
        self.status = 200


class Spider:
    @use_scrapling
    def parse(self, response):
        return response.css("a::attr(href)").get()


def test_response_adapter_proxies_response_fields():
    response = ScraplingScrapyResponse(DummyResponse())
    assert response.status == 200
    assert response.css("a::attr(href)").get() == "/x"


def test_use_scrapling_decorator_wraps_response():
    spider = Spider()
    assert spider.parse(DummyResponse()) == "/x"
