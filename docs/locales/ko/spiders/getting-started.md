---
title: "Scrapling으로 첫 Python 웹 크롤러 만들기"
description: "데이터를 추출하고 다음 페이지를 방문하며 결과를 내보내는 스파이더를 만드세요. 시작 URL, 콜백, 도메인 제한, robots.txt 설정을 알아봅니다."
---

# 시작하기 {#getting-started}

## 소개 {#introduction}

!!! success "시작 전 확인"

    1. [Fetcher 기본 사항](../fetching/choosing.md)을 읽고 Fetcher 종류와 각각의 용도를 이해해야 합니다.
    2. [주요 클래스](../parsing/main_classes.md)를 읽고 [Selector](../parsing/main_classes.md#selector)와 [Response](../fetching/choosing.md#response-object) 클래스를 이해해야 합니다.
    3. [아키텍처](architecture.md)를 읽고 스파이더 시스템의 전체 동작을 알아두세요.

스파이더 시스템을 사용하면 짧은 코드로 여러 페이지를 동시에 수집하는 크롤러를 만들 수 있습니다. Scrapy를 사용해 봤다면 익숙한 방식입니다. 처음이라도 이 안내에 따라 시작할 수 있습니다.

## 첫 스파이더 만들기 {#your-first-spider}

스파이더는 웹사이트를 탐색하고 데이터를 추출하는 방법을 정의하는 클래스입니다. 가장 간단한 예는 다음과 같습니다.

```python
from scrapling.spiders import Spider, Response

class QuotesSpider(Spider):
    name = "quotes"
    start_urls = ["https://quotes.toscrape.com"]

    async def parse(self, response: Response):
        for quote in response.css("div.quote"):
            yield {
                "text": quote.css("span.text::text").get(""),
                "author": quote.css("small.author::text").get(""),
            }
```

모든 스파이더에는 다음 세 가지가 필요합니다.

1. **`name`**: 스파이더의 고유한 이름입니다.
2. **`start_urls`**: 크롤링을 시작할 URL 목록입니다.
3. **`parse()`**: 각 응답을 처리하고 결과를 내보내는 비동기 제너레이터 메서드입니다.

주요 처리는 `parse()`에서 합니다. Scrapling의 [Selector](../parsing/main_classes.md#selector)/[Response](../fetching/choosing.md#response-object)와 같은 선택 메서드를 사용하고, 딕셔너리를 `yield`로 내보내 수집한 항목을 전달합니다.

## 스파이더 실행하기 {#running-the-spider}

스파이더 인스턴스를 만들고 `start()`를 호출하세요.

```python
result = QuotesSpider().start()
```

`start()`가 비동기 실행을 내부에서 처리하므로 이벤트 루프를 직접 관리할 필요가 없습니다. 실행 중에는 모든 동작이 터미널에 기록되고, 크롤링이 끝나면 자세한 통계를 얻습니다.

통계와 결과는 반환된 `CrawlResult` 객체에서 확인할 수 있습니다.

```python
result = QuotesSpider().start()

# Access scraped items
for item in result.items:
    print(item["text"], "-", item["author"])

# Check statistics
print(f"Scraped {result.stats.items_scraped} items")
print(f"Made {result.stats.requests_count} requests")
print(f"Took {result.stats.elapsed_seconds:.1f} seconds")

# Did the crawl finish or was it paused?
print(f"Completed: {result.completed}")
```

## 링크 따라가기 {#following-links}

대부분의 크롤링은 링크를 따라 여러 페이지를 방문합니다. `response.follow()`로 다음 요청을 만드세요.

```python
from scrapling.spiders import Spider, Response

class QuotesSpider(Spider):
    name = "quotes"
    start_urls = ["https://quotes.toscrape.com"]

    async def parse(self, response: Response):
        # Extract items from the current page
        for quote in response.css("div.quote"):
            yield {
                "text": quote.css("span.text::text").get(""),
                "author": quote.css("small.author::text").get(""),
            }

        # Follow the "next page" link
        next_page = response.css("li.next a::attr(href)").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)
```

`response.follow()`는 상대 URL을 현재 페이지의 URL과 자동으로 결합합니다. 기본적으로 현재 페이지를 `Referer` 헤더에도 설정합니다.

페이지 종류에 따라 다른 콜백 메서드를 지정할 수 있습니다.

```python
async def parse(self, response: Response):
    for link in response.css("a.product-link::attr(href)").getall():
        yield response.follow(link, callback=self.parse_product)

async def parse_product(self, response: Response):
    yield {
        "name": response.css("h1::text").get(""),
        "price": response.css(".price::text").get(""),
    }
```

!!! note

    모든 콜백 메서드는 `async def`와 `yield`를 사용하는 비동기 제너레이터여야 합니다.

## 데이터 내보내기 {#exporting-data}

`result.items`의 `ItemList`에는 내보내기 메서드가 있습니다.

```python
result = QuotesSpider().start()

# Export as JSON
result.items.to_json("quotes.json")

# Export as JSON with pretty-printing
result.items.to_json("quotes.json", indent=True)

# Export as JSON Lines (one JSON object per line)
result.items.to_jsonl("quotes.jsonl")

# Export as CSV or XML
result.items.to_csv("quotes.csv")
result.items.to_xml("quotes.xml")
```

모든 메서드는 상위 디렉터리가 없으면 자동으로 만듭니다.

`to_csv()`는 전체 항목에서 발견한 모든 키를 열로 만듭니다. 항목마다 키가 달라도 내보낼 수 있으며, 값이 없는 셀은 비워 둡니다. 열과 순서를 직접 선택하려면 `fields=[...]`를, TSV 파일을 만들려면 `delimiter="\t"`를 전달하세요. `to_xml()`은 각 항목을 `<item>` 요소로 감싸고 `<items>` 루트 안에 넣습니다. 두 이름은 `root_tag`와 `item_tag`로 변경할 수 있습니다.

두 형식 모두 중첩 딕셔너리나 리스트처럼 단순한 스칼라가 아닌 값은 JSON으로 기록합니다. 데이터가 알림 없이 사라지지 않습니다.

## 도메인 제한하기 {#filtering-domains}

`allowed_domains`로 방문할 도메인을 제한하세요. 외부 웹사이트의 링크를 실수로 따라가는 일을 막을 수 있습니다.

```python
class MySpider(Spider):
    name = "my_spider"
    start_urls = ["https://example.com"]
    allowed_domains = {"example.com"}

    async def parse(self, response: Response):
        for link in response.css("a::attr(href)").getall():
            # Links to other domains are silently dropped
            yield response.follow(link, callback=self.parse)
```

하위 도메인도 자동으로 허용합니다. 예를 들어 `allowed_domains = {"example.com"}`은 `sub.example.com`, `blog.example.com` 등도 허용합니다.

제외한 요청 수는 `stats.offsite_requests_count`에서 확인할 수 있습니다.

## robots.txt 준수하기 {#robotstxt-compliance}

`robots_txt_obey = True`를 설정하면 각 도메인을 크롤링하기 전에 robots.txt 규칙을 확인합니다.

```python
class PoliteSpider(Spider):
    name = "polite"
    start_urls = ["https://example.com"]
    robots_txt_obey = True

    async def parse(self, response: Response):
        for link in response.css("a::attr(href)").getall():
            yield response.follow(link, callback=self.parse)
```

활성화하면 다음과 같이 동작합니다.

1. 크롤링 전에 `start_urls`의 모든 도메인에서 **robots.txt를 미리 가져옵니다**. 여러 도메인을 동시에 처리합니다.
2. **모든 요청을 확인**하여 도메인의 robots.txt `Disallow` 규칙을 적용합니다. 금지된 요청은 알림 없이 제외하고 `stats.robots_disallowed_count`에 집계합니다.
3. **`Crawl-delay`와 `Request-rate` 지시문을 준수**합니다. 지시문이 요구하는 지연과 설정한 `download_delay` 중 큰 값을 사용합니다. 따라서 robots.txt는 설정한 지연을 줄이지 않고 필요할 때만 늘립니다. AutoThrottle이 활성화되어 있으면 최대 지연 설정도 적용됩니다. 필요한 지연을 지킬 수 있도록 `autothrottle_max_delay`를 충분히 크게 설정하세요.

robots.txt 파일은 기본 세션으로 가져오며, 크롤링이 끝날 때까지 도메인별로 캐시합니다. 크롤링 중 발견한 도메인이 `start_urls`에 없다면 해당 도메인에 처음 요청할 때 robots.txt를 가져옵니다.

**참고:** 예상치 못한 동작을 피하기 위해 `robots_txt_obey`는 기본적으로 꺼져 있습니다. 활성화해도 동시 요청 설정인 `concurrent_requests`, `concurrent_requests_per_domain`은 바뀌지 않습니다. 요청 사이의 지연만 조정합니다.

`download_delay`를 직접 정하고 싶지 않다면 `autothrottle_enabled = True`를 설정하세요. 스파이더가 각 도메인의 응답 속도에 맞춰 지연을 조정하고, 차단되면 속도를 줄입니다. [AutoThrottle](advanced.md#autothrottle)을 참고하세요.

## 다음 단계 {#whats-next}

기본 사항을 익혔다면 다음 내용을 살펴보세요.

- [요청과 응답](requests-responses.md): 요청 우선순위, 중복 제거, 메타데이터 등을 알아봅니다.
- [세션](sessions.md): 한 스파이더에서 HTTP, 브라우저, 스텔스 등 여러 Fetcher 종류를 사용합니다.
- [프록시와 차단 처리](proxy-blocking.md): 요청마다 프록시를 바꾸고 차단을 처리합니다.
- [고급 기능](advanced.md): 동시 요청 제어, AutoThrottle, 일시 중지와 재개, 스트리밍, 수명 주기 훅, 로깅을 알아봅니다.
