"""Tests for `WooCommerceSpider`."""

import orjson
import pytest

from scrapling.engines.toolbelt.custom import Response
from scrapling.spiders.request import Request
from scrapling.spiders.templates import WooCommerceSpider
from scrapling.core._types import Any, Dict


SIMPLE_PRODUCT = {
    "id": 1,
    "name": "Ceramic Mug",
    "type": "simple",
    "sku": "MUG-01",
    "permalink": "https://example.com/product/ceramic-mug/",
    "description": "<p>A <b>ceramic</b> mug</p>",
    "on_sale": True,
    "is_in_stock": True,
    "categories": [{"id": 3, "name": "Kitchen", "slug": "kitchen"}],
    "images": [{"id": 10, "src": "https://example.com/mug.jpg"}],
    "prices": {
        "price": "1500",
        "regular_price": "2000",
        "sale_price": "1500",
        "currency_minor_unit": 2,
    },
}

OUT_OF_STOCK_PRODUCT = {
    "id": 2,
    "name": "Steel Bottle",
    "type": "simple",
    "sku": "",
    "permalink": "https://example.com/product/steel-bottle/",
    "description": None,
    "on_sale": False,
    "is_in_stock": False,
    "categories": [],
    "images": [],
    "prices": {"price": "900", "regular_price": "900", "currency_minor_unit": 2},
}

VARIABLE_PRODUCT = {
    "id": 3,
    "name": "T-Shirt",
    "type": "variable",
    "permalink": "https://example.com/product/t-shirt/",
    "description": "<p>Soft cotton tee</p>",
    "on_sale": False,
    "categories": [{"id": 4, "name": "Apparel", "slug": "apparel"}],
    "images": [{"id": 11, "src": "https://example.com/tshirt.jpg"}],
}

VARIATIONS_PAGE = [
    {
        "id": 31,
        "sku": "TSHIRT-RED-M",
        "is_in_stock": True,
        "attributes": [{"name": "Color", "value": "Red"}, {"name": "Size", "value": "M"}],
        "image": {"id": 12, "src": "https://example.com/tshirt-red.jpg"},
        "prices": {"price": "2500", "regular_price": "3000", "currency_minor_unit": 2},
    },
    {
        "id": 32,
        "sku": "TSHIRT-BLUE-L",
        "is_in_stock": False,
        "attributes": [{"name": "Color", "value": "Blue"}, {"name": "Size", "value": "L"}],
        "image": None,
        "prices": {"price": "2500", "regular_price": "2500", "currency_minor_unit": 2},
    },
]


def _make_response(url: str, payload: Any, meta: Dict[str, Any] | None = None) -> Response:
    resp = Response(
        url=url,
        content=orjson.dumps(payload),
        status=200,
        reason="OK",
        cookies={},
        headers={},
        request_headers={},
    )
    resp.request = Request(url, meta=meta or {})
    resp.meta.update(meta or {})
    return resp


class ExampleStoreSpider(WooCommerceSpider):
    target_website = "example.com"


class TestDomainResolution:
    def test_from_target_website(self):
        assert ExampleStoreSpider().target_website == "example.com"

    def test_target_website_normalized_from_url(self):
        class S(WooCommerceSpider):
            target_website = "https://example.com/shop"

        assert S().target_website == "example.com"

    def test_from_start_urls(self):
        class S(WooCommerceSpider):
            start_urls = ["https://www.example.com/shop"]

        assert S().target_website == "www.example.com"

    def test_from_allowed_domains(self):
        class S(WooCommerceSpider):
            allowed_domains = {"example.com"}

        assert S().target_website == "example.com"

    def test_no_source_raises(self):
        with pytest.raises(ValueError, match="must set"):
            WooCommerceSpider()


class TestParsing:
    @pytest.mark.asyncio
    async def test_start_requests(self):
        spider = ExampleStoreSpider()
        requests = [r async for r in spider.start_requests()]
        assert len(requests) == 1
        assert requests[0].url == "https://example.com/wp-json/wc/store/v1/products?page=1&per_page=100"
        assert requests[0].meta == {"page": 1}

    @pytest.mark.asyncio
    async def test_parse_yields_simple_products_and_next_page(self):
        spider = ExampleStoreSpider()
        response = _make_response(
            "https://example.com/wp-json/wc/store/v1/products?page=1&per_page=100",
            [SIMPLE_PRODUCT, OUT_OF_STOCK_PRODUCT],
            {"page": 1},
        )
        results = [r async for r in spider.parse(response)]
        items = [r for r in results if isinstance(r, dict)]
        requests = [r for r in results if isinstance(r, Request)]

        assert len(items) == 2
        assert len(requests) == 1
        assert requests[0].url == "https://example.com/wp-json/wc/store/v1/products?page=2&per_page=100"
        assert requests[0].meta == {"page": 2}

    @pytest.mark.asyncio
    async def test_parse_dispatches_variations_request_for_variable_products(self):
        spider = ExampleStoreSpider()
        response = _make_response(
            "https://example.com/wp-json/wc/store/v1/products?page=1&per_page=100",
            [VARIABLE_PRODUCT],
            {"page": 1},
        )
        results = [r async for r in spider.parse(response)]
        requests = [r for r in results if isinstance(r, Request) and "product" in r.meta]

        assert len(requests) == 1
        assert requests[0].url == "https://example.com/wp-json/wc/store/v1/products/3/variations?per_page=100"
        assert requests[0].meta["product"] == VARIABLE_PRODUCT

    @pytest.mark.asyncio
    async def test_parse_stops_on_empty_page(self):
        spider = ExampleStoreSpider()
        response = _make_response(
            "https://example.com/wp-json/wc/store/v1/products?page=3&per_page=100", [], {"page": 3}
        )
        assert [r async for r in spider.parse(response)] == []

    @pytest.mark.asyncio
    async def test_parse_variations_yields_one_item_per_variation(self):
        spider = ExampleStoreSpider()
        response = _make_response(
            "https://example.com/wp-json/wc/store/v1/products/3/variations?per_page=100",
            VARIATIONS_PAGE,
            {"product": VARIABLE_PRODUCT},
        )
        items = [r async for r in spider.parse_variations(response)]

        assert len(items) == 2
        assert items[0]["name"] == "T-Shirt - Red / M"
        assert items[0]["identifier"] == 31
        assert items[0]["sku"] == "TSHIRT-RED-M"
        assert items[0]["stock"] is None
        assert items[0]["image_url"] == "https://example.com/tshirt-red.jpg"
        assert items[0]["url"] == "https://example.com/product/t-shirt/"

        assert items[1]["name"] == "T-Shirt - Blue / L"
        assert items[1]["stock"] == 0
        assert items[1]["image_url"] == "https://example.com/tshirt.jpg"  # falls back to parent image

    @pytest.mark.asyncio
    async def test_parse_variations_falls_back_to_parent_when_empty(self):
        spider = ExampleStoreSpider()
        response = _make_response(
            "https://example.com/wp-json/wc/store/v1/products/3/variations?per_page=100",
            [],
            {"product": VARIABLE_PRODUCT},
        )
        items = [r async for r in spider.parse_variations(response)]
        assert len(items) == 1
        assert items[0]["name"] == "T-Shirt"


class TestItemProcessing:
    def test_simple_product_on_sale_fields(self):
        spider = ExampleStoreSpider()
        item = spider._process_product(SIMPLE_PRODUCT)

        assert item == {
            "name": "Ceramic Mug",
            "price": "15.00",
            "category": "Kitchen",
            "brand": "",
            "identifier": 1,
            "sku": "MUG-01",
            "stock": None,
            "image_url": "https://example.com/mug.jpg",
            "url": "https://example.com/product/ceramic-mug/",
            "description": "A ceramic mug",
            "old_price": "20.00",
            "barcode": "",
        }

    def test_out_of_stock_product_without_sale(self):
        spider = ExampleStoreSpider()
        item = spider._process_product(OUT_OF_STOCK_PRODUCT)

        assert item["stock"] == 0
        assert item["old_price"] == ""
        assert item["category"] == ""
        assert item["image_url"] == ""
        assert item["description"] == ""

    def test_price_formatting_respects_currency_minor_unit(self):
        spider = ExampleStoreSpider()
        product = {**SIMPLE_PRODUCT, "prices": {"price": "999", "currency_minor_unit": 3}}
        assert spider._process_product(product)["price"] == "0.999"

    def test_variation_name_without_attributes_falls_back_to_product_name(self):
        spider = ExampleStoreSpider()
        variation = {**VARIATIONS_PAGE[0], "attributes": []}
        item = spider._process_product(VARIABLE_PRODUCT, variation)
        assert item["name"] == "T-Shirt"
