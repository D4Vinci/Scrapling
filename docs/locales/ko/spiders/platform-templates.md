---
title: "Python으로 Shopify 상품 데이터 수집하기"
description: "ShopifySpider로 Shopify 스토어의 상품 목록을 수집하세요. 스토어 URL을 설정하고 상품 옵션 조합별 데이터를 모으며 각 항목의 필드를 확인합니다."
---

# 플랫폼별 스파이더 템플릿 {#platform-spider-templates}

일반 템플릿은 링크 따라가기나 사이트맵 방문 같은 크롤링 *방식*을 다룹니다. 플랫폼 템플릿은 *플랫폼*을 다룹니다. 여러 독립된 사이트에서 같은 기계 판독용 구조를 제공하는 사이트 제작 플랫폼이 대상입니다. 스파이더가 데이터 위치를 이미 알고 있으므로 도메인만 지정하면 됩니다.

## ShopifySpider {#shopifyspider}

`ShopifySpider`는 Shopify의 JSON API로 스토어의 모든 상품을 추출합니다. 웹사이트의 HTML은 사용하지 않습니다.

```python
from scrapling.spiders import ShopifySpider

class MyStore(ShopifySpider):
    target_website = "example.com"

result = MyStore().start()
print(result.items[0])
```

`target_website`에 스토어 도메인을 설정하세요. 비어 있으면 `start_urls`의 첫 항목, 다음으로 `allowed_domains`를 사용합니다. 셋 다 비어 있으면 `ValueError`가 발생합니다. 전체 URL을 전달하면 자동으로 도메인으로 변환합니다.

### 동작 방식 {#how-it-works}

1. `https://<store>/collections.json`의 페이지를 순서대로 가져옵니다. 페이지당 컬렉션은 플랫폼 제한인 250개입니다.
2. 상품이 있다고 표시된 각 컬렉션에서 `/collections/<handle>/products.json`의 페이지를 가져옵니다.
3. 상품 옵션 조합별로 항목 하나를 내보냅니다. 여러 컬렉션에 나타나는 같은 옵션 조합은 중복 제거합니다.

### 항목 필드 {#item-fields}

| 필드 | 출처 |
|---------------|---------------------------------------------------------------------------|
| `name` | 상품 이름과 옵션 이름입니다. 기본 옵션이면 옵션 이름은 넣지 않습니다 |
| `price` | Shopify가 반환한 그대로의 옵션 가격 문자열 |
| `category` | 컬렉션 URL의 이름 부분에서 각 단어의 첫 글자를 대문자로 바꿉니다. `summer-sale`은 `Summer Sale`이 됩니다 |
| `brand` | 상품 공급업체 |
| `identifier` | 옵션 ID |
| `sku` | 옵션 SKU입니다. 스토어에서 설정하지 않으면 `""`입니다 |
| `stock` | 옵션을 구매할 수 있으면 `None`, 품절이면 `0` |
| `image_url` | 첫 상품 이미지 또는 `""` |
| `url` | 컬렉션 안의 상품 페이지 |
| `description` | HTML 태그를 제거한 상품의 `body_html` |
| `old_price` | 실제 할인 전 가격이면 `compare_at_price`, 아니면 `""` |
| `barcode` | 옵션 바코드 또는 `""`입니다. 대부분의 스토어는 이 API에서 바코드를 제공하지 않습니다 |

이 필드 구성이 필수는 아닙니다. 하위 클래스에서 `_process_product()`를 재정의하면 항목 구조를 바꾸거나 다른 상품 필드를 추출할 수 있습니다.

### 참고 사항과 제한 {#notes-and-limits}

- JSON API는 온라인 스토어 채널에 게시된 상품만 제공합니다. 따라서 컬렉션의 `products_count`가 실제로 가져올 수 있는 수보다 클 수 있습니다. 스파이더는 이 값을 예상 총개수로 사용하지 않고, 0이 아니면 컬렉션을 가져오는 조건으로만 사용합니다.
- 추가 보호 기능이나 비밀번호가 있는 스토어에서는 이 템플릿이 작동하지 않을 가능성이 큽니다. 작동하게 만들 수 있더라도 여러 메서드를 직접 재정의해야 합니다.
- 동시 요청 설정, 지연, robots.txt 준수, 체크포인트, 수명 주기 훅 등 `Spider`의 기능을 그대로 사용할 수 있습니다.

### 플랫폼 템플릿으로 인정되는 범위 {#what-qualifies-as-a-platform-template}

Shopify처럼 여러 독립된 웹사이트에서 같은 기계 판독용 구조를 제공하는 플랫폼의 템플릿을 받습니다. 아무리 인기 있는 사이트라도 특정 사이트 하나만을 위한 스파이더는 라이브러리에 포함하지 않습니다.
