"""Spider template for extracting products from WooCommerce-powered websites."""

from urllib.parse import urlparse

from w3lib.html import remove_tags

from scrapling.spiders.request import Request
from scrapling.spiders.spider import Spider
from scrapling.core._types import (
    TYPE_CHECKING,
    Any,
    AsyncGenerator,
    Dict,
    List,
    Optional,
    Union,
)

if TYPE_CHECKING:
    from scrapling.engines.toolbelt.custom import Response

__all__ = ["WooCommerceSpider"]


class WooCommerceSpider(Spider):
    """A spider that extracts all products from any WooCommerce-powered website through its public Store API.

    Set `target_website` to the store's domain (or set `start_urls`/`allowed_domains` instead), and the
    spider walks the store's `/wp-json/wc/store/v1/products` pages, then each variable product's
    `/variations` endpoint, yielding one item per product (or per variation) without touching the
    website's HTML. The Store API is enabled by default on WooCommerce sites using the block-based
    cart/checkout; stores that disabled it will return a 404/403 for every request this spider makes.
    """

    name = "woocommerce"
    target_website = ""
    products_url = "https://{website}/wp-json/wc/store/v1/products?page={page}&per_page=100"
    variations_url = "https://{website}/wp-json/wc/store/v1/products/{product_id}/variations?per_page=100"

    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        source = self.target_website or next(iter(self.start_urls or ()), "") or next(iter(self.allowed_domains), "")
        if not source:
            raise ValueError(f"{self.__class__.__name__} must set `target_website`, `start_urls`, or `allowed_domains`")
        self.target_website = urlparse(source if "://" in source else f"https://{source}").netloc

    async def start_requests(self) -> AsyncGenerator[Request, None]:
        yield Request(
            self.products_url.format(website=self.target_website, page=1),
            callback=self.parse,
            meta={"page": 1},
        )

    async def parse(self, response: "Response") -> AsyncGenerator[Union[Dict[str, Any], Request, None], None]:
        products = response.json()
        if products:
            for product in products:
                if product.get("type") == "variable" and product.get("id"):
                    yield Request(
                        self.variations_url.format(website=self.target_website, product_id=product["id"]),
                        callback=self.parse_variations,
                        meta={"product": product},
                    )
                else:
                    yield self._process_product(product)

            next_page = response.meta.get("page", 1) + 1
            yield Request(
                self.products_url.format(website=self.target_website, page=next_page),
                callback=self.parse,
                meta={"page": next_page},
            )

    async def parse_variations(self, response: "Response") -> AsyncGenerator[Dict[str, Any], None]:
        product = response.meta["product"]
        variations = response.json()
        if variations:
            for variation in variations:
                yield self._process_product(product, variation)
        else:
            # No variations came back (e.g. the parent was marked "variable" without any), fall back
            # to a single item built from the parent product itself so the product isn't dropped.
            yield self._process_product(product)

    @staticmethod
    def _format_price(prices: Dict[str, Any], key: str) -> str:
        raw = prices.get(key)
        if raw in (None, ""):
            return ""

        minor_unit = int(prices.get("currency_minor_unit", 2))
        try:
            return f"{int(raw) / (10**minor_unit):.{minor_unit}f}"
        except (TypeError, ValueError):
            return ""

    def _variation_name(self, product_name: str, variation: Optional[Dict[str, Any]]) -> str:
        if not variation:
            return product_name

        attributes: List[Dict[str, Any]] = variation.get("attributes") or []
        values = [attribute["value"] for attribute in attributes if attribute.get("value")]
        return f"{product_name} - {' / '.join(values)}" if values else product_name

    def _process_product(self, product: Dict[str, Any], variation: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        item = variation or product
        prices = item.get("prices") or {}
        price = self._format_price(prices, "price")
        regular_price = self._format_price(prices, "regular_price")
        images = item.get("images") or ([item["image"]] if item.get("image") else None) or product.get("images") or []
        categories = product.get("categories") or []

        return {
            "name": self._variation_name(product.get("name", ""), variation),
            "price": price,
            "category": categories[0]["name"] if categories else "",
            "brand": "",
            "identifier": item.get("id"),
            "sku": item.get("sku") or "",
            "stock": None if item.get("is_in_stock", True) else 0,
            "image_url": images[0]["src"] if images else "",
            "url": product.get("permalink", ""),
            "description": remove_tags(product.get("description") or ""),
            "old_price": regular_price if product.get("on_sale") and regular_price and regular_price != price else "",
            "barcode": "",
        }
