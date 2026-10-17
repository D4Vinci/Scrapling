---
title: "Scrapy Spider で Scrapling の解析機能を使う"
description: "Scrapy のレスポンスを変換する方法と、コールバックにデコレーターを付ける方法を紹介します。Scrapy クローラーを維持したまま、Scrapling のセレクターと適応型解析を使えます。"
---

# Scrapling を Scrapy に組み込む {#integrating-scrapling-into-scrapy}

既存の Scrapy プロジェクトがある場合、Scrapling の解析 API を使うために書き直す必要はありません。Scrapy 連携機能は、Spider のコールバック内で Scrapy のレスポンスを Scrapling の [Response](../fetching/choosing.md#response-object) オブジェクトに変換します。クロールは引き続き Scrapy が担当し、解析を Scrapling が担当します。

!!! note "インストール"

    この連携機能は、標準の Scrapling インストール（`pip install scrapling`）で使えます。追加の依存関係グループは不要です。Scrapy のインストールだけが必要ですが、Scrapy プロジェクトにはすでに入っています。

## 使い方 {#usage}

Spider のコールバックに `scrapling_response` デコレーターを付けると、受け取る `response` 引数が Scrapling の `Response` になります。

```python
import scrapy
from scrapling.integrations.scrapy import scrapling_response


class QuotesSpider(scrapy.Spider):
    name = "quotes"
    start_urls = ["https://quotes.toscrape.com"]

    @scrapling_response
    def parse(self, response):  # `response` is now a Scrapling Response
        first_quote = response.find_by_text("The world as we have created it", partial=True)
        for quote in [first_quote, *first_quote.find_similar()]:
            card = quote.parent
            yield {
                "text": quote.get_all_text(strip=True),
                "author": card.find("small", class_="author").text,
                "tags": [tag.text for tag in card.find_all("a", class_="tag")],
            }
        next_page = response.css("li.next a::attr(href)").get()
        if next_page:
            yield scrapy.Request(response.urljoin(next_page), callback=self.parse)
```

このデコレーターは、Scrapy が対応するすべてのコールバック形式で使えます。通常の関数、ジェネレーター、コルーチン、非同期ジェネレーターに対応しています。ラッパーは元の形式、名前、docstring を保つため、Scrapy のコールバック検査やコントラクトも引き続き動作します。

デコレーターに [Selector](../parsing/main_classes.md#selector) の設定を渡すこともできます。その設定は、生成される `Response` に渡されます。

```python
    @scrapling_response(adaptive=True, keep_comments=True)
    def parse_product(self, response):
        ...
```

ミドルウェアやパイプラインなど、コールバック以外の場所に Scrapy のレスポンスがある場合は、変換関数を直接使います。

```python
from scrapling.integrations.scrapy import convert_response

scrapling_response = convert_response(scrapy_response, keep_comments=False)
```

## 注意点 {#notes}

- 次のページを取得するには、上の例のように `scrapy.Request(response.urljoin(href))` を yield します。Scrapling の `Response.follow()` は [Scrapling の Spider システム](../spiders/getting-started.md)用のリクエストを作るため、Scrapy では扱えません。
- レスポンスの `meta` 辞書は浅いコピーを作るため、他のミドルウェアが保存したオブジェクトにも引き続きアクセスできます。例えば `scrapy-playwright` のページは、そのまま `response.meta["playwright_page"]` にあります。
- 生の `Set-Cookie` ヘッダーから Cookie を解析し、レスポンスの `cookies` 辞書に格納します。
