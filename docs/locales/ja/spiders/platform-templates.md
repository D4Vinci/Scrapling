---
title: "Python で Shopify の商品データを取得する"
description: "ShopifySpider で Shopify ストアの商品一覧を取得します。ストアの URL を設定し、商品バリエーションを集め、各データ項目のフィールドを確認します。"
---

# プラットフォーム用の Spider テンプレート {#platform-spider-templates}

汎用テンプレートは、リンクをたどる、サイトマップを巡回するといったクロールの*パターン*を扱います。プラットフォーム用テンプレートは、*プラットフォーム*を扱います。多くの独立したサイトに同じ機械可読の構造を提供するサイト作成サービスなので、Spider はデータの場所をあらかじめ知っています。指定するのはドメインだけです。

## ShopifySpider {#shopifyspider}

`ShopifySpider` は Shopify の JSON API を使い、ストアのすべての商品を抽出します。サイトの HTML は使いません。

```python
from scrapling.spiders import ShopifySpider

class MyStore(ShopifySpider):
    target_website = "example.com"

result = MyStore().start()
print(result.items[0])
```

`target_website` にストアのドメインを設定します。空の場合は、`start_urls`、次に `allowed_domains` の最初の項目を使います。3 つとも空なら `ValueError` を発生させます。完全な URL を指定しても、自動でドメインに変換します。

### 仕組み {#how-it-works}

1. `https://<store>/collections.json` をページごとに取得します。1 ページの上限は、プラットフォームが定める 250 コレクションです。
2. 商品があると報告する各コレクションについて、`/collections/<handle>/products.json` をページごとに取得します。
3. 商品バリエーションごとに 1 項目を返します。複数のコレクションに現れる同じバリエーションは、重複して出力しません。

### データ項目のフィールド {#item-fields}

| フィールド | 取得元 |
|------------|--------|
| `name` | 商品名。バリエーション名がデフォルトでなければ、それも追加 |
| `price` | バリエーションの価格。Shopify が返す文字列をそのまま使用 |
| `category` | URL 内でコレクションを表す handle の各単語の先頭を大文字にしたもの（`summer-sale` は `Summer Sale`） |
| `brand` | 商品の販売元 |
| `identifier` | バリエーションの ID |
| `sku` | バリエーションの SKU。ストアが設定していなければ `""` |
| `stock` | 購入可能なら `None`、在庫切れなら `0` |
| `image_url` | 最初の商品画像、または `""` |
| `url` | コレクション内の商品ページ |
| `description` | 商品の `body_html` から HTML タグを除いた内容 |
| `old_price` | 実際の値引き前価格なら `compare_at_price`、それ以外は `""` |
| `barcode` | バリエーションのバーコード、または `""`。多くのストアでは、このエンドポイントから取得できません |

これらのフィールドは固定ではありません。サブクラスで `_process_product()` をオーバーライドすると、項目の構造を変更したり、商品データから別のフィールドを取得したりできます。

### 注意点と制限 {#notes-and-limits}

- JSON エンドポイントが返すのは、オンラインストアの販売チャネルで公開された商品だけです。そのため、コレクションの `products_count` が実際に取得できる数を上回る場合があります。Spider は、この値が 0 でなければコレクションを取得しますが、取得予定の総数としては使いません。
- 追加の保護やパスワードがあるストアでは、おそらくこのテンプレートは使えません。使える場合でも、多くのメソッドを自分でオーバーライドする必要があります。
- `Spider` の機能はすべて使えます。並行処理の設定、待機時間、robots.txt、チェックポイント、ライフサイクルフックも同じです。

### プラットフォーム用テンプレートの対象 {#what-qualifies-as-a-platform-template}

Shopify のように、多くの独立したサイトで共通の機械可読な構造を提供するプラットフォームのテンプレートを受け入れています。特定の 1 サイトだけに対応する Spider は、そのサイトの人気に関係なくライブラリには含めません。
