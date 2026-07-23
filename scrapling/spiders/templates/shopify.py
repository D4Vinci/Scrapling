"""Spider template for extracting products from Shopify-powered websites."""

from urllib.parse import urlparse

from w3lib.html import remove_tags

from scrapling.spiders.request import Request
from scrapling.spiders.spider import Spider
from scrapling.core._types import (
    TYPE_CHECKING,
    Any,
    AsyncGenerator,
    Dict,
    Generator,
    Set,
    Union,
)

if TYPE_CHECKING:
    from scrapling.engines.toolbelt.custom import Response

__all__ = ["ShopifySpider"]


class ShopifySpider(Spider):
    """A spider that extracts all products from any Shopify-powered website through its JSON API.

    Set `target_website` to the store's domain (or set `start_urls`/`allowed_domains` instead), and the
    spider walks the store's `/collections.json` pages, then each collection's `products.json` pages,
    yielding one item per product variant without touching the website's HTML.
    """

    name = "shopify"
    target_website = ""
    collections_url = "https://{website}/collections.json?page={page}&limit=250"
    products_url = "https://{website}/collections/{handle}/products.json?page={page}&limit=250"
    product_url = "https://{website}/collections/{handle}/products/{product_handle}"

    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        source = self.target_website or next(iter(self.start_urls or ()), "") or next(iter(self.allowed_domains), "")
        if not source:
            raise ValueError(f"{self.__class__.__name__} must set `target_website`, `start_urls`, or `allowed_domains`")
        self.target_website = urlparse(source if "://" in source else f"https://{source}").netloc
        self.collected_ids: Set[int] = set()

    async def start_requests(self) -> AsyncGenerator[Request, None]:
        yield Request(
            self.collections_url.format(website=self.target_website, page=1),
            callback=self.parse,
            meta={"page": 1},
        )

    async def parse(self, response: "Response") -> AsyncGenerator[Union[Dict[str, Any], Request, None], None]:
        collections = response.json()["collections"]
        if collections:
            for collection in collections:
                if collection["products_count"]:
                    yield Request(
                        self.products_url.format(website=self.target_website, handle=collection["handle"], page=1),
                        callback=self.parse_collection,
                        meta={"handle": collection["handle"], "page": 1},
                    )

            next_page = response.meta.get("page", 1) + 1
            yield Request(
                self.collections_url.format(website=self.target_website, page=next_page),
                callback=self.parse,
                meta={"page": next_page},
            )

    def _process_product(self, product: Dict, collection_handle: str) -> Generator[Dict[str, Any], None, None]:
        for variant in product["variants"]:
            if variant["id"] in self.collected_ids:
                continue

            self.collected_ids.add(variant["id"])
            old_price = variant.get("compare_at_price")
            yield {
                "name": product["title"] + (f" - {variant['title']}" if variant["title"] != "Default Title" else ""),
                "price": variant["price"],
                "category": collection_handle.replace("-", " ").title().strip(),
                "brand": product["vendor"],
                "identifier": variant["id"],
                "sku": variant.get("sku") or "",
                "stock": None if variant.get("available") else 0,
                "image_url": product["images"][0]["src"] if product["images"] else "",
                "url": self.product_url.format(
                    website=self.target_website, handle=collection_handle, product_handle=product["handle"]
                ),
                "description": remove_tags(product.get("body_html") or ""),
                "old_price": old_price if old_price and float(old_price) else "",
                "barcode": variant.get("barcode") or "",
            }

    async def parse_collection(
        self, response: "Response"
    ) -> AsyncGenerator[Union[Dict[str, Any], Request, None], None]:
        collection_handle, current_page = response.meta["handle"], response.meta.get("page", 1)
        products = response.json()["products"]
        if products:
            for product in products:
                for item in self._process_product(product, collection_handle):
                    yield item

            yield Request(
                self.products_url.format(website=self.target_website, handle=collection_handle, page=current_page + 1),
                callback=self.parse_collection,
                meta={"handle": collection_handle, "page": current_page + 1},
            )
        else:
            self.logger.debug(f"Extracted all products from collection {collection_handle}")
