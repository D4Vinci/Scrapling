---
title: "用 Python 抓取 Shopify 商品数据"
description: "用 ShopifySpider 抓取 Shopify 商店的商品目录。设置商店 URL，收集商品变体，并了解每个数据项的字段。"
---

# 平台专用 Spider 模板 {#platform-spider-templates}

通用模板针对抓取*模式*，例如跟随链接、遍历 Sitemap。平台模板针对的是*平台*：这些建站平台会在许多独立网站中提供相同的机器可读结构，因此 Spider 已经知道数据在哪里。只需指定域名即可。

## ShopifySpider {#shopifyspider}

`ShopifySpider` 通过 Shopify 的 JSON API 提取商店中的所有商品，不读取网站的 HTML。

```python
from scrapling.spiders import ShopifySpider

class MyStore(ShopifySpider):
    target_website = "example.com"

result = MyStore().start()
print(result.items[0])
```

将 `target_website` 设为商店域名。如果为空，Spider 会先尝试 `start_urls` 中的第一个条目，再尝试 `allowed_domains` 中的第一个条目。如果三者都为空，则抛出 `ValueError`。完整 URL 会自动转换为域名。

### 工作方式 {#how-it-works}

1. 逐页获取 `https://<store>/collections.json`，每页最多 250 个商品集合，这是平台规定的上限。
2. 对于每个包含商品的集合，逐页获取 `/collections/<handle>/products.json`。
3. 每个商品变体产出一个数据项。出现在多个集合中的同一变体只输出一次。

### 数据项字段 {#item-fields}

| 字段 | 来源 |
|------|------|
| `name` | 商品标题；如果变体标题不是默认值，还会附加变体标题 |
| `price` | 变体价格，保留 Shopify 返回的原始字符串 |
| `category` | 商品集合的 handle，也就是 URL 中的标识，并将每个词的首字母大写（`summer-sale` 变为 `Summer Sale`） |
| `brand` | 商品供应商 |
| `identifier` | 变体 ID |
| `sku` | 变体 SKU；商店未设置时为 `""` |
| `stock` | 变体有货时为 `None`，缺货时为 `0` |
| `image_url` | 第一张商品图片，或 `""` |
| `url` | 商品在该集合中的页面 |
| `description` | 去除 HTML 标签后的商品 `body_html` |
| `old_price` | 如果 `compare_at_price` 是真实的促销前价格，则使用该值，否则为 `""` |
| `barcode` | 变体条码，或 `""`（大多数商店不会在这些接口中提供条码） |

这些字段不是固定要求。可以在子类中重写 `_process_product()`，修改数据项结构，或从商品数据中提取其他字段。

### 注意事项与限制 {#notes-and-limits}

- JSON 接口只返回发布到在线商店渠道的商品。因此，集合的 `products_count` 可能大于实际能获取的数量。Spider 只用它判断是否需要获取该集合：非零就获取，不会把它当作预期总数。
- 如果商店有额外防护或密码保护，这个模板很可能无法使用。即使能用，也通常需要自行重写许多方法。
- `Spider` 的所有功能仍然适用，包括并发设置、延迟、robots.txt 规则、检查点和生命周期钩子。

### 什么样的平台适合添加模板 {#what-qualifies-as-a-platform-template}

只有像 Shopify 这样，在许多独立网站上提供统一、机器可读结构的平台，才适合加入平台模板。针对单个网站的 Spider 不会加入本库，无论该网站多受欢迎。
