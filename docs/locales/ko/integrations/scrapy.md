---
title: "Scrapy Spider에서 Scrapling 파싱 사용하기"
description: "Scrapy 응답을 Scrapling으로 변환하거나 콜백에 데코레이터를 추가하세요. 기존 Scrapy 크롤러를 유지하면서 Scrapling 선택자와 적응형 파싱을 사용할 수 있습니다."
---

# Scrapy에 Scrapling 통합하기 {#integrating-scrapling-into-scrapy}

기존 Scrapy 프로젝트를 다시 작성하지 않고도 Scrapling의 파싱 API를 사용할 수 있습니다. Scrapy 통합 기능은 Spider 콜백 안에서 Scrapy 응답을 Scrapling [Response](../fetching/choosing.md#response-object) 객체로 변환합니다. 크롤링은 계속 Scrapy가 담당하고, 파싱은 Scrapling이 담당합니다.

!!! note "설치"

    이 기능은 기본 Scrapling 설치(`pip install scrapling`)로 사용할 수 있으며 추가 의존성 그룹은 필요하지 않습니다. Scrapy만 설치되어 있으면 됩니다. 기존 Scrapy 프로젝트라면 이미 설치되어 있습니다.

## 사용법 {#usage}

Spider 콜백에 `scrapling_response` 데코레이터를 붙이면, 전달받는 `response` 인수가 Scrapling의 `Response`가 됩니다.

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

이 데코레이터는 Scrapy가 지원하는 모든 콜백 형태에서 작동합니다. 일반 함수, 제너레이터, 코루틴, 비동기 제너레이터를 지원합니다. 래퍼는 콜백의 형태, 이름, docstring을 유지하므로 Scrapy의 콜백 검사와 contract 기능도 계속 작동합니다.

데코레이터에 [Selector](../parsing/main_classes.md#selector) 설정을 전달할 수도 있습니다. 이 설정은 생성되는 `Response`에 전달됩니다.

```python
    @scrapling_response(adaptive=True, keep_comments=True)
    def parse_product(self, response):
        ...
```

미들웨어나 파이프라인처럼 콜백 밖에서 Scrapy 응답을 가지고 있다면 변환 함수를 직접 사용하세요.

```python
from scrapling.integrations.scrapy import convert_response

scrapling_response = convert_response(scrapy_response, keep_comments=False)
```

## 참고 사항 {#notes}

- 다음 페이지를 요청할 때는 위 예제처럼 `scrapy.Request(response.urljoin(href))`를 yield하세요. Scrapling의 `Response.follow()`는 [Scrapling Spider 시스템](../spiders/getting-started.md)용 요청을 만들므로 Scrapy에서 처리할 수 없습니다.
- 응답의 `meta` 딕셔너리는 얕게 복사하므로 다른 미들웨어가 저장한 객체에도 계속 접근할 수 있습니다. 예를 들어 `scrapy-playwright`를 사용하면 페이지는 여전히 `response.meta["playwright_page"]`에 있습니다.
- 원본 `Set-Cookie` 헤더에서 쿠키를 파싱해 응답의 `cookies` 딕셔너리에 넣습니다.
