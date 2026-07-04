import inspect

import pytest
import scrapy
from scrapy.http import HtmlResponse
from scrapy.http import Request as ScrapyRequest
from scrapy.http import Response as ScrapyBaseResponse

from scrapling.engines.toolbelt.custom import Response
from scrapling.integrations.scrapy import convert_response, scrapling_response

PAGE = b"""<html>
  <head><title>Test page</title></head>
  <body>
    <!-- hidden comment -->
    <h1>Hello</h1>
    <a href="/next">Next</a>
  </body>
</html>"""


def make_response(**kwargs):
    """Build a Scrapy HtmlResponse with an attached request, no network involved"""
    if "request" not in kwargs:
        kwargs["request"] = ScrapyRequest(
            "http://example.com/page", headers={"User-Agent": "pytest"}, meta={"depth": 1}
        )
    defaults = {
        "url": "http://example.com/page",
        "body": PAGE,
        "headers": {"Content-Type": "text/html; charset=utf-8"},
        "status": 200,
    }
    defaults.update(kwargs)
    return HtmlResponse(**defaults)


class TestConvertResponse:
    """Test converting Scrapy responses to Scrapling responses directly"""

    def test_field_mapping(self):
        scrapy_response = make_response()
        response = convert_response(scrapy_response)

        assert isinstance(response, Response)
        assert response.url == "http://example.com/page"
        assert response.body == PAGE
        assert response.status == 200
        assert response.reason == "OK"
        assert response.encoding == "utf-8"
        assert response.headers["Content-Type"] == "text/html; charset=utf-8"
        assert response.request_headers["User-Agent"] == "pytest"
        assert response.meta == {"depth": 1}
        assert response.meta is not scrapy_response.meta
        assert response.css("h1::text").get() == "Hello"
        assert response.urljoin("/next") == "http://example.com/next"

    def test_cookies_parsed_from_raw_set_cookie_headers(self):
        # The `Expires` date contains a comma, which corrupts comma-joined header dicts
        response = convert_response(
            make_response(
                headers={
                    "Set-Cookie": [
                        "sid=abc123; Path=/; Expires=Wed, 09 Jun 2027 10:18:14 GMT",
                        "lang=en; Path=/",
                    ]
                }
            )
        )

        assert response.cookies == {"sid": "abc123", "lang": "en"}

    def test_response_without_request(self):
        response = convert_response(make_response(request=None))

        assert response.meta == {}
        assert response.request_headers == {}
        assert response.css("h1::text").get() == "Hello"

    def test_binary_response_encoding_fallback(self):
        # The base Scrapy Response class has no `encoding` attribute
        binary = ScrapyBaseResponse("http://example.com/file.bin", body=b"\x00\x01\x02", status=200)
        response = convert_response(binary)

        assert response.encoding == "utf-8"
        assert response.body == b"\x00\x01\x02"

    def test_unknown_status_code_reason(self):
        response = convert_response(make_response(status=599))

        assert response.status == 599
        assert response.reason == "Unknown Status Code"

    def test_selector_config_is_forwarded(self):
        default = convert_response(make_response())
        with_comments = convert_response(make_response(), keep_comments=True)

        assert not default.xpath("//comment()")
        assert with_comments.xpath("//comment()")


class TestScraplingResponseDecorator:
    """Test the decorator over all the callback kinds Scrapy supports"""

    def test_generator_callback_on_spider_method(self):
        class TestSpider(scrapy.Spider):
            name = "test_spider"

            @scrapling_response
            def parse(self, response):
                """Parse the page title"""
                yield {"title": response.css("title::text").get(), "is_scrapling": isinstance(response, Response)}

        spider = TestSpider()
        assert inspect.isgeneratorfunction(spider.parse)
        assert spider.parse.__name__ == "parse"
        assert spider.parse.__doc__ == "Parse the page title"

        items = list(spider.parse(make_response()))
        assert items == [{"title": "Test page", "is_scrapling": True}]

    def test_regular_callback(self):
        @scrapling_response
        def parse(response):
            return response.css("h1::text").get()

        assert not inspect.isgeneratorfunction(parse)
        assert parse(make_response()) == "Hello"

    @pytest.mark.asyncio
    async def test_coroutine_callback(self):
        @scrapling_response
        async def parse(response):
            return response.css("h1::text").get()

        assert inspect.iscoroutinefunction(parse)
        assert await parse(make_response()) == "Hello"

    @pytest.mark.asyncio
    async def test_async_generator_callback(self):
        @scrapling_response
        async def parse(response):
            yield response.css("h1::text").get()

        assert inspect.isasyncgenfunction(parse)
        assert [item async for item in parse(make_response())] == ["Hello"]

    def test_parameterized_form(self):
        @scrapling_response(keep_comments=True)
        def parse(response):
            return response.xpath("//comment()")

        assert parse(make_response())

    def test_cb_kwargs_passthrough(self):
        @scrapling_response
        def parse(response, category=None):
            return category, response.status

        assert parse(make_response(), category="books") == ("books", 200)

    def test_response_passed_as_keyword(self):
        @scrapling_response
        def parse(response):
            return type(response)

        assert parse(response=make_response()) is Response

    def test_positional_response_wins_over_keyword(self):
        @scrapling_response
        def parse(response, other=None):
            return type(response), type(other)

        assert parse(make_response(), other=make_response()) == (Response, HtmlResponse)

    def test_no_response_in_arguments_raises(self):
        @scrapling_response
        def parse(response):
            return response  # pragma: no cover

        with pytest.raises(TypeError, match="No Scrapy response found"):
            parse("not a response")
