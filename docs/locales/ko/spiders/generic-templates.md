---
title: "링크, 사이트맵, 피드, Markdown용 스파이더 템플릿"
description: "CrawlSpider, SitemapSpider, XMLFeedSpider, CSVFeedSpider, ContentSpider 중에서 선택하세요. 페이지, 피드 항목, Markdown 문서를 수집할 규칙을 설정합니다."
---

# 일반 스파이더 템플릿 {#generic-spider-templates}

대부분의 크롤링은 특정 패턴의 링크를 따라가거나 사이트맵에 있는 모든 URL을 방문합니다. Scrapling은 두 방식의 템플릿을 제공하므로 같은 `parse()` 코드를 매번 작성할 필요가 없습니다.

`CrawlSpider`와 `SitemapSpider`는 `LinkExtractor`를 사용합니다. 이 클래스는 `Response`에서 URL을 추출하거나 `matches()`로 URL 하나를 검사합니다. `SitemapSpider`는 gzip 압축 여부와 관계없이 sitemap.xml / sitemap_index.xml 본문도 내부에서 파싱합니다.

일반 `Spider.parse()` 안에서 `LinkExtractor`를 직접 사용할 수도 있습니다. 템플릿은 이 연결 작업을 대신해 줄 뿐입니다.

## CrawlSpider {#crawlspider}

`CrawlSpider`는 선언한 규칙에 따라 링크를 자동으로 따라갑니다.

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

`CrawlRule`은 `LinkExtractor`에 선택적 `callback`(스파이더의 바인딩된 메서드), 생성할 `Request`의 선택적 `priority`, 선택적 `process_request`를 연결합니다. 마지막 인수는 각 `Request`를 내보내기 전에 수정하는 바인딩된 메서드입니다. 기본 `parse()`는 모든 응답에 모든 규칙을 적용하고, 일치하는 URL마다 `Request`를 내보냅니다.

규칙에 콜백이 없으면 해당 URL은 스파이더의 기본 `parse()`로 전달합니다. 다음 페이지 링크를 추출해 별도 콜백 없이 계속 방문할 수 있으므로 페이지 나누기에 유용합니다.

### 크롤링 순서 {#crawl-order}

`CrawlSpider`나 `ContentSpider`를 포함한 하위 클래스에서 `crawl_strategy`를 설정해 대기 요청의 순서를 선택하세요.

| `crawl_strategy` | 같은 `Request.priority` 안에서의 순서 |
|------------------|------------------------------------------|
| `"bfs"`(기본값) | 큐에 먼저 들어온 요청부터 |
| `"dfs"` | 큐에 나중에 들어온 요청부터 |

스케줄러는 `Request.priority`가 높은 대기 요청을 먼저 선택합니다. 전략은 우선순위가 같은 요청 사이의 순서만 정합니다.

선택한 큐 순서대로 요청을 하나씩 처리하려면 `concurrent_requests = 1`을 설정하세요. 중복 URL은 계속 제외하며, 같은 URL을 다시 발견해도 큐에 있던 요청의 위치는 바뀌지 않습니다. 동시 요청을 사용하면 페이지가 끝나는 순서가 달라지고, 탐색 단계나 분기가 겹칠 수 있습니다.

체크포인트에서 재개할 때는 같은 `crawl_strategy`를 유지하세요.

### 규칙에 원하는 동작 더하기 {#combining-rules-with-custom-logic}

`parse()`를 재정의하고 `super().parse(response)`를 호출하면 규칙에 따른 동작과 직접 내보내는 결과를 함께 사용할 수 있습니다.

```python
class MySpider(CrawlSpider):
    def rules(self):
        return [CrawlRule(LinkExtractor(allow=r"/posts/"), callback=self.parse_post)]

    async def parse(self, response):
        yield {"page_url": response.url}
        async for req in super().parse(response):
            yield req
```

### `process_request`로 요청 바꾸기 {#mutating-requests-with-process_request}

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

`SitemapSpider`는 sitemap.xml의 URL에서 크롤링을 시작합니다. `CrawlSpider`와 같은 `rules()` API를 사용하므로 동작 방식을 함께 이해할 수 있습니다.

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

### URL을 콜백으로 전달하는 방식 {#how-urls-are-dispatched}

`SitemapSpider`는 사이트맵의 URL마다 각 규칙의 `LinkExtractor.matches(url)`을 순서대로 확인합니다. 처음 일치한 규칙을 선택하고, 그 콜백을 가진 `Request`를 내보냅니다. `rules()`가 비어 있지 않은데 일치하는 규칙이 없으면 URL을 제외합니다. `rules()`가 빈 리스트이면 모든 URL을 스파이더의 `parse()`로 전달합니다. 이 메서드는 재정의하지 않으면 기본적으로 `NotImplementedError`를 발생시킵니다.

### 사이트맵 인덱스 {#sitemap-indexes}

`SitemapSpider`가 사이트맵 목록인 `<sitemapindex>`를 만나면 하위 사이트맵을 자동으로 방문합니다. 방문할 하위 사이트맵을 제한하려면 `sitemap_follow`에 `LinkExtractor`를 설정하세요.

```python
class MySitemap(SitemapSpider):
    name = "sm"
    sitemap_urls = ["https://example.com/sitemap.xml"]
    sitemap_follow = LinkExtractor(allow=r"/posts-sitemap-\d+\.xml")  # only post sitemaps
```

### robots.txt 지원 {#robotstxt-support}

`robots.txt` URL을 `sitemap_urls`에 바로 넣으면 `SitemapSpider`가 파일을 알아보고, 나열된 모든 사이트맵을 추출해 방문합니다.

```python
class MySitemap(SitemapSpider):
    name = "sm"
    sitemap_urls = ["https://example.com/robots.txt"]
```

### 다른 언어의 URL {#alternate-language-urls}

`sitemap_alternate_links = True`를 설정하면 `<xhtml:link rel="alternate" hreflang="...">`의 URL도 규칙으로 처리합니다.

## XMLFeedSpider {#xmlfeedspider}

`XMLFeedSpider`는 RSS, Atom, 상품 피드 등 XML 피드의 노드를 순회합니다. `itertag`에 원하는 노드 이름을 설정하고(기본값: `"item"`), 일치하는 노드마다 호출할 `parse_node()`를 재정의하세요.

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

다른 콜백처럼 `parse_node()`도 `Request`를 내보낼 수 있습니다. 예를 들어 `response.follow(node.findtext("link"), callback=self.parse_post)`로 피드가 가리키는 페이지를 방문할 수 있습니다.

### 노드 선택과 파싱 {#how-nodes-are-matched-and-parsed}

`parse_node()`에 전달하는 노드는 네임스페이스를 모두 제거한 `lxml` 요소입니다. 따라서 `node.findtext("title")`, `node.find("thumbnail").get("url")`, 대소문자를 구분하는 `node.xpath(...)`를 어떤 피드에서든 네임스페이스 매핑 없이 사용할 수 있습니다. `"entry"`처럼 단순한 `itertag`는 네임스페이스와 관계없이 이름으로 노드를 찾습니다. Atom과 대부분의 네임스페이스가 있는 피드에 적합합니다. 특정 네임스페이스의 노드만 찾으려면 접두사가 있는 `itertag`를 사용하고 `namespaces`에 접두사를 정의하세요.

```python
class ThumbnailSpider(XMLFeedSpider):
    name = "thumbs"
    start_urls = ["https://example.com/feed.xml"]
    itertag = "media:thumbnail"
    namespaces = (("media", "http://search.yahoo.com/mrss/"),)

    async def parse_node(self, response, node):
        yield {"thumbnail": node.get("url")}
```

gzip 피드(`.xml.gz` 또는 gzip 콘텐츠 타입으로 제공되는 피드)는 사이트맵 스파이더와 같은 보호 기능으로 자동 압축 해제합니다. 잘못된 XML은 크롤링을 중단하지 않고 경고를 기록합니다.

## CSVFeedSpider {#csvfeedspider}

`CSVFeedSpider`는 CSV 피드의 행을 순회합니다. 열 이름을 키로 하는 딕셔너리로 각 행을 받는 `parse_row()`를 재정의하세요.

```python
from scrapling.spiders import CSVFeedSpider

class PriceSpider(CSVFeedSpider):
    name = "prices"
    start_urls = ["https://example.com/products.csv"]

    async def parse_row(self, response, row):
        yield {"product": row["title"], "price": float(row["price"])}

result = PriceSpider().start()
```

기본적으로 첫 행을 헤더로 사용합니다. 헤더 행이 없으면 `headers`에 열 이름을 직접 지정하세요. 표준 쉼표 형식이 아니라면 `delimiter`/`quotechar`를 설정하세요.

```python
class PriceSpider(CSVFeedSpider):
    name = "prices"
    start_urls = ["https://example.com/products.csv"]
    headers = ["title", "price", "url"]
    delimiter = ";"
```

위의 **XMLFeedSpider**처럼 gzip 피드도 자동으로 압축 해제합니다.

<a id="sitetomarkdownspider"></a>

## ContentSpider {#contentspider}

`ContentSpider`는 **CrawlSpider**를 바탕으로 사이트를 방문하고 각 페이지를 LLM에 전달하기 좋은 정리된 Markdown으로 바꿉니다. 페이지마다 항목 하나를 내보내며, 필요하면 Markdown 파일도 하나씩 작성합니다.

```python
from scrapling.spiders import ContentSpider

class DocsSpider(ContentSpider):
    name = "docs"
    start_urls = ["https://example.com/docs/"]
    allowed_domains = {"example.com"}
    output_dir = "docs_markdown"

result = DocsSpider().start()
```

크롤링 범위를 대상 사이트로 제한하도록 `allowed_domains`를 설정해야 합니다. 전체 옵션과 RAG 파이프라인에 결과를 전달하는 방법은 [RAG 시스템 만들기](../ai/building-rag-systems.md)를 참고하세요.

## `LinkExtractor` 직접 사용하기 {#using-linkextractor-directly}

템플릿은 필수가 아닙니다. `LinkExtractor`는 일반 `Spider` 안에서도 사용할 수 있습니다.

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

## LinkExtractor 참고 자료 {#linkextractor-reference}

| 인수 | 기본값 | 설명 |
|-------------------|----------------------|---------------------------------------------------------------------------------------------------|
| `allow` | `()` | 유지할 URL 패턴입니다. 비어 있으면 모두 허용합니다. 문자열, 컴파일한 `Pattern`, 또는 이 값을 담은 반복 가능한 객체를 받습니다 |
| `deny` | `()` | 제외할 URL 패턴입니다. 항상 `allow`보다 우선합니다 |
| `allow_domains` | `()` | 허용할 호스트 이름입니다. 하위 도메인도 허용하므로 `example.com`은 `api.example.com`과도 일치합니다 |
| `deny_domains` | `()` | 제외할 호스트 이름 |
| `restrict_css` | `()` | DOM에서 링크를 추출할 영역을 제한하는 CSS 선택자 |
| `restrict_xpath` | `()` | DOM에서 링크를 추출할 영역을 제한하는 XPath 선택자 |
| `tags` | `("a", "area")` | 링크를 찾을 요소 태그 |
| `attrs` | `("href",)` | 해당 태그에서 URL을 읽을 속성 |
| `canonicalize` | `True` | 쿼리 인수를 정렬하고 경로를 정규화합니다 |
| `strip` | `True` | 추출한 URL 양 끝의 공백을 제거합니다 |
| `keep_fragment` | `False` | 정규화할 때 `#fragment`를 유지합니다 |
| `deny_extensions` | `IGNORED_EXTENSIONS` | 제외할 파일 확장자입니다. pdf, zip, 이미지, 동영상 등이 해당합니다 |
| `process` | `None` | 필터링 전에 추출한 URL마다 적용할 선택적 호출 가능 객체입니다. 거짓으로 평가되는 값을 반환하면 URL을 제외합니다 |

`LinkExtractor.extract(response)`는 필터링과 중복 제거를 마친 절대 URL의 `list[str]`를 반환합니다.

`LinkExtractor.matches(url)`은 `bool`을 반환하는 URL 전용 필터입니다. 허용/제외 패턴, 도메인, 확장자를 검사합니다. `SitemapSpider`는 이 메서드로 `Response` 없이 URL을 전달할 규칙을 정합니다.
