---
title: "リンク、サイトマップ、フィード、Markdown 用の Spider テンプレート"
description: "CrawlSpider、SitemapSpider、XMLFeedSpider、CSVFeedSpider、ContentSpider から選びます。ルールを設定してページ、フィードの行、Markdown 文書を集めます。"
---

# 汎用 Spider テンプレート {#generic-spider-templates}

多くのクロールは、「指定パターンに合うリンクをたどる」か「サイトマップに載っている URL をすべて取得する」のどちらかです。Scrapling には両方のテンプレートがあり、同じ `parse()` の基本コードを毎回書く必要はありません。

`CrawlSpider` と `SitemapSpider` は `LinkExtractor` を使います。これは `Response` から URL を取り出したり、`matches()` で 1 つの URL を判定したりします。`SitemapSpider` はさらに、sitemap.xml や sitemap_index.xml の内容を内部で解析します。gzip 圧縮にも対応しています。

通常の `Spider.parse()` 内で `LinkExtractor` を直接使うこともできます。テンプレートは、これらの部品を組み合わせる手間を省きます。

## CrawlSpider {#crawlspider}

`CrawlSpider` は、定義したルールに従ってリンクを自動でたどります。

```python
from scrapling.spiders import CrawlSpider, CrawlRule, LinkExtractor

class QuotesSpider(CrawlSpider):
    name = "blog"
    start_urls = ["https://quotes.toscrape.com/"]

    def rules(self):
        return [
            CrawlRule(LinkExtractor(allow=r"/author/"), callback=self.parse_author),
            CrawlRule(LinkExtractor(allow=r"/page/\d+/")),  # follow pagination, no callback
        ]

    async def parse_author(self, response):
        yield {
            '.author-title': response.css('.author-title::text').get(),
            "birthday": response.css('.author-born-date::text').get(),
            "url": response.url,
        }

result = QuotesSpider().start()
```

`CrawlRule` は `LinkExtractor` と、必要に応じて指定する `callback` を組み合わせます。コールバックは Spider のバインド済みメソッドです。生成する `Request` の `priority` や、各 `Request` を返す前に変更するバインド済みメソッド `process_request` も指定できます。デフォルトの `parse()` は、各レスポンスにすべてのルールを適用し、一致した URL ごとに `Request` を返します。

コールバックを指定しないルールでは、一致した URL を Spider のデフォルトの `parse()` に渡します。これはページ送りに便利です。次のページのリンクを取り出すだけでクロールを続けられ、専用の処理メソッドは不要です。

### クロールの順序 {#crawl-order}

`CrawlSpider` または `ContentSpider` などのサブクラスで `crawl_strategy` を設定すると、次に処理するリクエストの選び方を指定できます。

| `crawl_strategy` | `Request.priority` が同じ場合の順序 |
|------------------|------------------------------------|
| `"bfs"`（デフォルト） | 最も早くキューに入ったリクエストから処理 |
| `"dfs"` | 最も遅くキューに入ったリクエストから処理 |

スケジューラーは、常に `Request.priority` が高いリクエストから取り出します。戦略が決めるのは、優先度が同じリクエスト同士の順序だけです。

`concurrent_requests = 1` にすると、選んだキューの順序で 1 件ずつ処理します。重複 URL は引き続き除外され、同じ URL を再度見つけてもキュー内の位置は変わりません。並行処理ではページの完了順が変わることがあり、異なる階層や枝の処理が重なることもあります。

チェックポイントから再開するときは、同じ `crawl_strategy` を使ってください。

### ルールと独自の処理を組み合わせる {#combining-rules-with-custom-logic}

`parse()` をオーバーライドして `super().parse(response)` を呼び出すと、ルールの処理と独自の出力を両方使えます。

```python
class MySpider(CrawlSpider):
    def rules(self):
        return [CrawlRule(LinkExtractor(allow=r"/posts/"), callback=self.parse_post)]

    async def parse(self, response):
        yield {"page_url": response.url}
        async for req in super().parse(response):
            yield req
```

### `process_request` でリクエストを変更する {#mutating-requests-with-process_request}

```python
def add_priority(self, request, response):
    request.priority = 10
    return request

def rules(self):
    return [CrawlRule(
        LinkExtractor(allow=r"/posts/"),
        callback=self.parse_post,
        process_request=self.add_priority,
    )]
```

## SitemapSpider {#sitemapspider}

`SitemapSpider` は sitemap.xml の URL からクロールを開始します。`CrawlSpider` と同じ `rules()` API を使うため、考え方も共通です。

```python
from scrapling.spiders import SitemapSpider, CrawlRule, LinkExtractor

class MySitemap(SitemapSpider):
    name = "sm"
    sitemap_urls = ["https://example.com/sitemap.xml"]

    def rules(self):
        return [
            CrawlRule(LinkExtractor(allow=r"/posts/"), callback=self.parse_post),
            CrawlRule(LinkExtractor(allow=r"/products/"), callback=self.parse_product),
        ]

    async def parse_post(self, response):
        yield {"title": response.css("h1::text").get()}

    async def parse_product(self, response):
        yield {"sku": response.css(".sku::text").get()}

result = MySitemap().start()
```

### URL の振り分け {#how-urls-are-dispatched}

`SitemapSpider` はサイトマップ内の各 URL について、ルールごとの `LinkExtractor.matches(url)` を順に確認します。最初に一致したルールを使い、そのコールバックを持つ `Request` を返します。どのルールにも一致せず、`rules()` が空でなければ URL を破棄します。`rules()` が空のリストを返した場合は、すべての URL を Spider の `parse()` に渡します。このメソッドをオーバーライドしていなければ、デフォルトで `NotImplementedError` が発生します。

### サイトマップのインデックス {#sitemap-indexes}

`SitemapSpider` は `<sitemapindex>`、つまり複数のサイトマップをまとめた索引を見つけると、子のサイトマップを自動でたどります。対象を絞るには、`sitemap_follow` に `LinkExtractor` を設定します。

```python
class MySitemap(SitemapSpider):
    name = "sm"
    sitemap_urls = ["https://example.com/sitemap.xml"]
    sitemap_follow = LinkExtractor(allow=r"/posts-sitemap-\d+\.xml")  # only post sitemaps
```

### robots.txt への対応 {#robotstxt-support}

`robots.txt` の URL を `sitemap_urls` に直接入れると、`SitemapSpider` が認識し、そこに書かれたすべてのサイトマップを取り出してたどります。

```python
class MySitemap(SitemapSpider):
    name = "sm"
    sitemap_urls = ["https://example.com/robots.txt"]
```

### 別言語の URL {#alternate-language-urls}

`sitemap_alternate_links = True` にすると、`<xhtml:link rel="alternate" hreflang="...">` の URL もルールに従って処理します。

## XMLFeedSpider {#xmlfeedspider}

`XMLFeedSpider` は XML フィードのノードを順に処理します。RSS、Atom、商品フィードなどが対象です。`itertag` に必要なノード名を指定し、`parse_node()` をオーバーライドします。ノード名のデフォルトは `"item"` です。一致するノードごとにこのメソッドを呼び出します。

```python
from scrapling.spiders import XMLFeedSpider

class RSSSpider(XMLFeedSpider):
    name = "rss"
    start_urls = ["https://example.com/feed.xml"]
    itertag = "item"

    async def parse_node(self, response, node):
        yield {
            "title": node.findtext("title"),
            "link": node.findtext("link"),
            "date": node.findtext("pubDate"),
        }

result = RSSSpider().start()
```

ほかのコールバックと同じく、`parse_node()` は `Request` オブジェクトも返せます。たとえば、`response.follow(node.findtext("link"), callback=self.parse_post)` でフィードがリンクするページをクロールできます。

### ノードの選択と解析 {#how-nodes-are-matched-and-parsed}

`parse_node()` に渡すノードは、すべての名前空間を取り除いた `lxml` 要素です。そのため、`node.findtext("title")`、`node.find("thumbnail").get("url")`、大文字と小文字を区別する `node.xpath(...)` を、名前空間の対応表なしで使えます。`"entry"` のような単純な `itertag` は、名前空間に関係なくノード名で一致します。Atom や、名前空間を持つ多くのフィードに適した動作です。特定の名前空間のノードに絞るには、接頭辞付きの `itertag` を使い、`namespaces` で接頭辞を定義します。

```python
class ThumbnailSpider(XMLFeedSpider):
    name = "thumbs"
    start_urls = ["https://example.com/feed.xml"]
    itertag = "media:thumbnail"
    namespaces = (("media", "http://search.yahoo.com/mrss/"),)

    async def parse_node(self, response, node):
        yield {"thumbnail": node.get("url")}
```

gzip 圧縮されたフィードは自動で展開します。`.xml.gz` や gzip のコンテンツタイプで配信されたフィードが対象で、サイトマップ用の Spider と同じ保護機能を使います。不正な XML があってもクロールは中断せず、警告を記録します。

## CSVFeedSpider {#csvfeedspider}

`CSVFeedSpider` は CSV フィードの各行を処理します。`parse_row()` をオーバーライドしてください。列名をキーにした辞書として各行を受け取ります。

```python
from scrapling.spiders import CSVFeedSpider

class PriceSpider(CSVFeedSpider):
    name = "prices"
    start_urls = ["https://example.com/products.csv"]

    async def parse_row(self, response, row):
        yield {"product": row["title"], "price": float(row["price"])}

result = PriceSpider().start()
```

デフォルトでは最初の行をヘッダーに使います。ヘッダー行がなければ、`headers` に列名を指定します。通常のカンマ区切りでないフィードでは、`delimiter`/`quotechar` を設定できます。

```python
class PriceSpider(CSVFeedSpider):
    name = "prices"
    start_urls = ["https://example.com/products.csv"]
    headers = ["title", "price", "url"]
    delimiter = ";"
```

こちらも **XMLFeedSpider** と同じく、gzip 圧縮されたフィードを自動で展開します。

<a id="sitetomarkdownspider"></a>

## ContentSpider {#contentspider}

`ContentSpider` は **CrawlSpider** を基にして、Web サイトの各ページを LLM 向けの読みやすい Markdown に変換します。ページごとに 1 項目を返し、必要ならページごとに Markdown ファイルも保存します。

```python
from scrapling.spiders import ContentSpider

class DocsSpider(ContentSpider):
    name = "docs"
    start_urls = ["https://example.com/docs/"]
    allowed_domains = {"example.com"}
    output_dir = "docs_markdown"

result = DocsSpider().start()
```

対象サイト内にクロールを制限するため、`allowed_domains` が必須です。すべてのオプションや、RAG パイプラインに出力を渡す方法は、[RAG システムの構築](../ai/building-rag-systems.md)を参照してください。

## `LinkExtractor` を直接使う {#using-linkextractor-directly}

テンプレートを使わず、通常の `Spider` で `LinkExtractor` を使うこともできます。

```python
from scrapling.spiders import Spider, LinkExtractor

class CustomSpider(Spider):
    name = "custom"
    start_urls = ["https://example.com"]

    def __init__(self):
        super().__init__()
        self._links = LinkExtractor(allow=r"/posts/", deny_domains="ads.example.com")

    async def parse(self, response):
        for url in self._links.extract(response):
            yield response.follow(url, callback=self.parse_post)

    async def parse_post(self, response):
        yield {"title": response.css("h1::text").get()}
```

## LinkExtractor のリファレンス {#linkextractor-reference}

| 引数 | デフォルト | 説明 |
|------|------------|------|
| `allow` | `()` | 残す URL のパターン。空ならすべてに一致します。文字列、コンパイル済みの `Pattern`、またはそれらを含む反復可能なオブジェクト |
| `deny` | `()` | 除外する URL のパターン。常に `allow` より優先 |
| `allow_domains` | `()` | 許可するホスト名。サブドメインも一致します（`example.com` は `api.example.com` にも一致） |
| `deny_domains` | `()` | 除外するホスト名 |
| `restrict_css` | `()` | DOM からの抽出範囲を絞る CSS セレクター |
| `restrict_xpath` | `()` | DOM からの抽出範囲を絞る XPath セレクター |
| `tags` | `("a", "area")` | リンクを探す要素のタグ |
| `attrs` | `("href",)` | URL を読み取る属性 |
| `canonicalize` | `True` | クエリパラメーターを並べ替え、パスを正規化 |
| `strip` | `True` | 抽出した URL の前後の空白を除去 |
| `keep_fragment` | `False` | 正規化するときに `#fragment` を保持 |
| `deny_extensions` | `IGNORED_EXTENSIONS` | 除外するファイル拡張子。PDF、ZIP、画像、動画など |
| `process` | `None` | フィルター処理の前に、各 URL に適用する任意の関数。偽と判定される値を返すと URL を除外 |

`LinkExtractor.extract(response)` は、フィルターと重複排除を適用した絶対 URL の `list[str]` を返します。

`LinkExtractor.matches(url)` は `bool` を返します。URL だけを使い、許可・除外パターン、ドメイン、拡張子で判定します。`SitemapSpider` は、`Response` がない URL の振り分けに使います。
