"""Tests for `ShopifySpider`."""

import orjson
import pytest

from scrapling.engines.toolbelt.custom import Response
from scrapling.spiders.request import Request
from scrapling.spiders.templates import ShopifySpider
from scrapling.core._types import Any, Dict


COLLECTIONS_PAGE = {
    "collections": [
        {"handle": "lipsticks", "title": "Lipsticks", "products_count": 2},
        {"handle": "empty-collection", "title": "Empty", "products_count": 0},
    ]
}

PRODUCTS_PAGE = {
    "products": [
        {
            "id": 1,
            "title": "Matte Lipstick",
            "handle": "matte-lipstick",
            "vendor": "Acme",
            "body_html": "<p>A <b>matte</b> lipstick</p>",
            "images": [{"src": "https://cdn.shopify.com/lipstick.jpg"}],
            "variants": [
                {
                    "id": 11,
                    "title": "Red",
                    "sku": "LIP-RED",
                    "price": "9.00",
                    "available": True,
                    "compare_at_price": "12.00",
                },
                {
                    "id": 12,
                    "title": "Nude",
                    "sku": None,
                    "price": "9.00",
                    "available": False,
                    "compare_at_price": "0.00",
                },
            ],
        },
        {
            "id": 2,
            "title": "Brow Pencil",
            "handle": "brow-pencil",
            "vendor": "Acme",
            "body_html": None,
            "images": [],
            "variants": [
                {"id": 21, "title": "Default Title", "sku": "BROW-1", "price": "7.50", "available": True},
            ],
        },
    ]
}


def _make_response(url: str, payload: Dict[str, Any], meta: Dict[str, Any] | None = None) -> Response:
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


class ExampleStoreSpider(ShopifySpider):
    target_website = "example.com"


class TestDomainResolution:
    def test_from_target_website(self):
        assert ExampleStoreSpider().target_website == "example.com"

    def test_target_website_normalized_from_url(self):
        class S(ShopifySpider):
            target_website = "https://example.com/collections/all"

        assert S().target_website == "example.com"

    def test_from_start_urls(self):
        class S(ShopifySpider):
            start_urls = ["https://www.example.com/collections/mens"]

        assert S().target_website == "www.example.com"

    def test_from_allowed_domains(self):
        class S(ShopifySpider):
            allowed_domains = {"example.com"}

        assert S().target_website == "example.com"

    def test_no_source_raises(self):
        with pytest.raises(ValueError, match="must set"):
            ShopifySpider()


class TestParsing:
    @pytest.mark.asyncio
    async def test_start_requests(self):
        spider = ExampleStoreSpider()
        requests = [r async for r in spider.start_requests()]
        assert len(requests) == 1
        assert requests[0].url == "https://example.com/collections.json?page=1&limit=250"
        assert requests[0].meta == {"page": 1}

    @pytest.mark.asyncio
    async def test_parse_dispatches_collections_and_next_page(self):
        spider = ExampleStoreSpider()
        response = _make_response(
            "https://example.com/collections.json?page=1&limit=250", COLLECTIONS_PAGE, {"page": 1}
        )
        results = [r async for r in spider.parse(response)]

        assert all(isinstance(r, Request) for r in results)
        assert len(results) == 2
        assert results[0].url == "https://example.com/collections/lipsticks/products.json?page=1&limit=250"
        assert results[0].meta == {"handle": "lipsticks", "page": 1}
        assert results[1].url == "https://example.com/collections.json?page=2&limit=250"
        assert results[1].meta == {"page": 2}

    @pytest.mark.asyncio
    async def test_parse_stops_on_empty_page(self):
        spider = ExampleStoreSpider()
        response = _make_response(
            "https://example.com/collections.json?page=3&limit=250", {"collections": []}, {"page": 3}
        )
        assert [r async for r in spider.parse(response)] == []

    @pytest.mark.asyncio
    async def test_parse_collection_yields_items_and_next_page(self):
        spider = ExampleStoreSpider()
        response = _make_response(
            "https://example.com/collections/lipsticks/products.json?page=1&limit=250",
            PRODUCTS_PAGE,
            {"handle": "lipsticks", "page": 1},
        )
        results = [r async for r in spider.parse_collection(response)]
        items = [r for r in results if isinstance(r, dict)]
        requests = [r for r in results if isinstance(r, Request)]

        assert len(items) == 3
        assert len(requests) == 1
        assert requests[0].url == "https://example.com/collections/lipsticks/products.json?page=2&limit=250"
        assert requests[0].meta == {"handle": "lipsticks", "page": 2}

    @pytest.mark.asyncio
    async def test_parse_collection_stops_on_empty_page(self):
        spider = ExampleStoreSpider()
        response = _make_response(
            "https://example.com/collections/lipsticks/products.json?page=2&limit=250",
            {"products": []},
            {"handle": "lipsticks", "page": 2},
        )
        assert [r async for r in spider.parse_collection(response)] == []


class TestItemProcessing:
    def test_variant_expansion_and_fields(self):
        spider = ExampleStoreSpider()
        items = list(spider._process_product(PRODUCTS_PAGE["products"][0], "lipsticks"))

        assert len(items) == 2
        assert items[0] == {
            "name": "Matte Lipstick - Red",
            "price": "9.00",
            "category": "Lipsticks",
            "brand": "Acme",
            "identifier": 11,
            "sku": "LIP-RED",
            "stock": None,
            "image_url": "https://cdn.shopify.com/lipstick.jpg",
            "url": "https://example.com/collections/lipsticks/products/matte-lipstick",
            "description": "A matte lipstick",
            "old_price": "12.00",
            "barcode": "",
        }
        assert items[1]["sku"] == ""
        assert items[1]["stock"] == 0
        assert items[1]["old_price"] == ""

    def test_default_title_variant_keeps_product_name(self):
        spider = ExampleStoreSpider()
        items = list(spider._process_product(PRODUCTS_PAGE["products"][1], "brow-pencils"))

        assert len(items) == 1
        assert items[0]["name"] == "Brow Pencil"
        assert items[0]["category"] == "Brow Pencils"
        assert items[0]["image_url"] == ""
        assert items[0]["description"] == ""

    def test_variants_deduplicated_across_collections(self):
        spider = ExampleStoreSpider()
        product = PRODUCTS_PAGE["products"][0]

        assert len(list(spider._process_product(product, "lipsticks"))) == 2
        assert list(spider._process_product(product, "bestsellers")) == []

    def test_dedup_state_is_per_instance(self):
        product = PRODUCTS_PAGE["products"][0]
        assert len(list(ExampleStoreSpider()._process_product(product, "lipsticks"))) == 2
        assert len(list(ExampleStoreSpider()._process_product(product, "lipsticks"))) == 2
