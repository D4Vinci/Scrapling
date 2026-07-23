# Platform Spider Templates

Generic templates cover crawl *patterns* (follow links, walk sitemaps). Platform templates cover *platforms*: site builders that expose the same machine-readable structure across many independent websites, so the spider already knows where the data lives. You only point it at a domain.

## ShopifySpider

`ShopifySpider` extracts every product from any Shopify-powered store through Shopify's JSON API, without touching the website's HTML.

```python
from scrapling.spiders import ShopifySpider

class MyStore(ShopifySpider):
    target_website = "example.com"

result = MyStore().start()
print(result.items[0])
```

Set `target_website` to the store's domain. When it's empty, the spider falls back to the first entry in `start_urls`, then `allowed_domains`, and raises `ValueError` if all three are empty. Full URLs are normalized to their domain automatically.

### How it works

1. Pages through `https://<store>/collections.json` (250 collections per page, the platform's cap).
2. For every collection that reports products, pages through `/collections/<handle>/products.json`.
3. Yields one item per product variant, deduplicating variants that appear in multiple collections.

### Item fields

| Field         | Source                                                                    |
|---------------|---------------------------------------------------------------------------|
| `name`        | Product title, plus the variant title when it isn't the default one       |
| `price`       | Variant price (a string, exactly as Shopify returns it)                   |
| `category`    | Collection handle, title-cased (`summer-sale` becomes `Summer Sale`)      |
| `brand`       | Product vendor                                                            |
| `identifier`  | Variant id                                                                |
| `sku`         | Variant SKU, or `""` when the store doesn't set one                       |
| `stock`       | `None` when the variant is available, `0` when it's out of stock          |
| `image_url`   | First product image, or `""`                                              |
| `url`         | The product's page inside the collection                                  |
| `description` | Product `body_html` with the HTML tags stripped                           |
| `old_price`   | `compare_at_price` when it's a real pre-sale price, else `""`             |
| `barcode`     | Variant barcode, or `""` (most stores don't expose it in these endpoints) |

These fields are not mandatory; override the `_process_product()` method in your subclass to change the item structure or extract different fields from the product data.

### Notes and limits

- The JSON endpoints only expose products published to the online-store channel, so a collection's `products_count` can be higher than what's actually retrievable. The spider treats it as "nonzero means fetch this collection", never as an expected total.
- This template most likely won't work on stores behind extra protections or password-protected ones, and if it can work at all, it will need a lot of overrides from your side.
- Everything from `Spider` still applies: concurrency settings, delays, robots.txt compliance, checkpoints, and the lifecycle hooks.

### What qualifies as a platform template

Platform templates are accepted for platforms that expose a uniform, machine-readable structure across many independent websites, like Shopify does. Spiders for one specific website don't belong in the library, no matter how popular the website is.
