---
title: "스파이더 요청, 콜백, Response.follow"
description: "크롤링 요청을 만들고 메타데이터를 전달하며 response.follow로 링크를 따라가세요. 콜백, 우선순위, 요청 중복 제거를 알아봅니다."
---

# 요청과 응답 {#requests-responses}

!!! success "시작 전 확인"

    1. [시작하기](getting-started.md)를 읽고 간단한 스파이더를 만들고 실행하는 방법을 알아두세요.

이 페이지는 `Request` 객체를 자세히 설명합니다. 요청 만들기, 콜백 간 데이터 전달, 우선순위와 중복 제거 제어, `response.follow()`로 링크 따라가기를 다룹니다.

## Request 객체 {#the-request-object}

`Request`는 가져올 URL을 나타냅니다. 직접 만들거나 `response.follow()`로 만들 수 있습니다.

```python
from scrapling.spiders import Request

# Direct construction
request = Request(
    "https://example.com/page",
    callback=self.parse_page,
    priority=5,
)

# Via response.follow (preferred in callbacks)
request = response.follow("/page", callback=self.parse_page)
```

`Request`에 전달할 수 있는 인수는 다음과 같습니다.

| 인수 | 타입 | 기본값 | 설명 |
|---------------|------------|------------|-------------------------------------------------------------------------------------------------------|
| `url` | `str` | *필수* | 가져올 URL |
| `sid` | `str` | `""` | 사용할 세션의 ID입니다. [세션](sessions.md)을 참고하세요 |
| `callback` | `callable` | `None` | 응답을 처리할 비동기 제너레이터 메서드입니다. 기본값은 `parse()`입니다 |
| `priority` | `int` | `0` | 값이 클수록 먼저 처리합니다 |
| `dont_filter` | `bool` | `False` | `True`이면 중복 제거를 건너뛰고 같은 요청을 허용합니다 |
| `meta` | `dict` | `{}` | 응답에 전달할 임의의 메타데이터 |
| `**kwargs` | | | 세션의 가져오기 메서드에 전달할 추가 키워드 인수입니다. 예: `headers`, `method`, `data` |

추가 키워드 인수는 세션에 직접 전달합니다. 예를 들어 POST 요청은 다음과 같습니다.

```python
yield Request(
    "https://example.com/api",
    method="POST",
    data={"key": "value"},
    callback=self.parse_result,
)
```

## Response.follow() {#responsefollow}

`response.follow()`는 상대 URL을 현재 페이지 URL과 결합하고 새 `Request`를 만듭니다. `sid`, `callback`, `priority`를 생략하면 연결된 `response.request`의 값을 상속합니다. 새 값을 전달하면 덮어쓸 수 있습니다.

이전 요청의 헤더, 쿠키, 인증, 프록시 설정, 브라우저 설정, 기타 요청별 인수와 메타데이터를 복사하지 않습니다. 같은 사이트와 다른 사이트의 링크에 모두 적용됩니다.

`sid=""`, `callback=None`, `priority=None`이면 연결된 원래 요청의 값을 상속합니다. `priority=0`을 직접 지정하면 원래 우선순위를 덮어씁니다. 메타데이터는 기본적으로 빈 값이며 중복 제거는 켜져 있습니다. 선택한 세션의 공유 설정과 쿠키 저장소는 계속 적용됩니다.

POST 다음에 링크를 따라가면 다른 `method`를 지정하지 않는 한 GET을 보냅니다.

```python
async def parse(self, response: Response):
    # Minimal - inherits callback, sid, priority from current request
    yield response.follow("/next-page")

    # Override specific fields
    yield response.follow(
        "/product/123",
        callback=self.parse_product,
        sid="stealth",
        priority=10,
    )

    # Pass additional metadata to
    yield response.follow(
        "/details",
        callback=self.parse_details,
        meta={"category": "electronics"},
    )
```

| 인수 | 타입 | 기본값 | 설명 |
| --- | --- | --- | --- |
| `url` | `str` | *필수* | 따라갈 절대 또는 상대 URL |
| `sid` | `str` | `""` | 비어 있으면 원래 요청의 세션 ID를 상속합니다 |
| `callback` | `callable` | `None` | `None`이면 원래 요청의 콜백을 상속합니다 |
| `priority` | `int` / `None` | `None` | `None`이면 원래 요청의 우선순위를 상속합니다. 직접 지정한 `0`도 기존 값을 덮어씁니다 |
| `dont_filter` | `bool` | `False` | 중복 제거를 건너뜁니다 |
| `meta` | `dict` | `None` | 이 요청에만 사용할 메타데이터 |
| `referer_flow` | `bool` | `True` | 현재 페이지 URL을 Referer로 설정합니다 |
| `**kwargs` |  |  | 세션의 가져오기 메서드에 직접 전달할 인수 |

### Referer 전달 끄기 {#disabling-referer-flow}

기본적으로 `response.follow()`는 HTTP와 브라우저 요청의 `Referer`를 현재 페이지 URL로 설정합니다. 브라우저가 이 Referer를 사용하도록 `google_search=False`도 설정합니다. 이 동작을 끄려면 다음과 같이 사용하세요.

```python
yield response.follow("/page", referer_flow=False)
```

`referer_flow=False`이면 이 도우미는 Referer를 추가하거나 `google_search`를 바꾸지 않습니다. 직접 전달한 헤더와 세션 및 브라우저의 기본값은 계속 적용됩니다. HTTP 요청에 다른 Referer를 설정하려면 다음과 같이 사용하세요.

```python
yield response.follow(
    "/page",
    referer_flow=False,
    headers={"Referer": "https://example.com/"},
)
```

브라우저 요청에서는 `extra_headers`를 사용하고 필요하면 `google_search=False`를 설정하세요.

## 콜백 {#callbacks}

콜백은 응답을 처리하는 스파이더의 비동기 제너레이터 메서드입니다. 다음 세 타입 중 하나를 `yield`로 내보내야 합니다.

- **`dict`**: 결과에 추가할 수집 항목입니다.
- **`Request`**: 큐에 추가할 다음 요청입니다.
- **`None`**: 알림 없이 무시합니다.

```python
class MySpider(Spider):
    name = "my_spider"
    start_urls = ["https://example.com"]

    async def parse(self, response: Response):
        # Yield items (dicts)
        yield {"url": response.url, "title": response.css("title::text").get("")}

        # Yield follow-up requests
        for link in response.css("a::attr(href)").getall():
            yield response.follow(link, callback=self.parse_page)

    async def parse_page(self, response: Response):
        yield {"content": response.css("article::text").get("")}
```

!!! tip "참고"

    모든 콜백은 `async def`로 정의하고 `return` 대신 `yield`를 사용해야 합니다. 다음 요청 없이 항목만 내보내더라도 비동기 제너레이터여야 합니다.

## 요청 우선순위 {#request-priority}

우선순위 값이 높은 요청을 먼저 처리합니다. 일부 페이지를 다른 페이지보다 먼저 처리해야 할 때 유용합니다.

```python
async def parse(self, response: Response):
    # High priority - process product pages first
    for link in response.css("a.product::attr(href)").getall():
        yield response.follow(link, callback=self.parse_product, priority=10)

    # Low priority - pagination links processed after products
    next_page = response.css("a.next::attr(href)").get()
    if next_page:
        yield response.follow(next_page, callback=self.parse, priority=0)
```

`response.follow()`의 `priority` 기본값은 `None`이며 원래 요청의 우선순위를 상속합니다. `priority=0`을 포함해 값을 직접 지정하면 상속할 우선순위를 덮어씁니다.

## 중복 제거 {#deduplication}

스파이더는 URL, HTTP 메서드, 요청 본문, 세션 ID로 지문을 계산해 중복 요청을 제거합니다. 두 요청의 지문이 같으면 두 번째 요청을 알림 없이 제외합니다.

로그인 후 페이지를 다시 방문하는 경우처럼 중복 요청이 필요하면 `dont_filter=True`를 설정하세요.

```python
yield Request("https://example.com/dashboard", dont_filter=True, callback=self.parse_dashboard)

# Or with response.follow
yield response.follow("/dashboard", dont_filter=True, callback=self.parse_dashboard)
```

스파이더의 클래스 속성으로 지문에 포함할 내용을 조정할 수 있습니다.

| 속성 | 기본값 | 동작 |
|----------------------|---------|-----------------------------------------------------------------------------------------------------------------|
| `fp_include_kwargs` | `False` | 헤더 등 세션의 가져오기 메서드에 전달한 추가 요청 인수를 지문에 포함합니다 |
| `fp_keep_fragments` | `False` | 지문을 계산할 때 URL 프래그먼트(`#section`)를 유지합니다 |
| `fp_include_headers` | `False` | 요청 헤더를 지문에 포함합니다 |

예를 들어 `https://example.com/page#section1`과 `https://example.com/page#section2`를 서로 다른 URL로 처리하려면 다음과 같이 설정하세요.

```python
class MySpider(Spider):
    name = "my_spider"
    fp_keep_fragments = True
    # ...
```

## 요청 메타데이터 {#request-meta}

`meta` 딕셔너리로 콜백 사이에 원하는 데이터를 전달할 수 있습니다. 다른 페이지를 처리할 때 이전 페이지의 정보가 필요하면 유용합니다.

```python
async def parse(self, response: Response):
    for product in response.css("div.product"):
        category = product.css("span.category::text").get("")
        link = product.css("a::attr(href)").get()
        if link:
            yield response.follow(
                link,
                callback=self.parse_product,
                meta={"category": category},
            )

async def parse_product(self, response: Response):
    yield {
        "name": response.css("h1::text").get(""),
        "price": response.css(".price::text").get(""),
        # Access meta from the request
        "category": response.meta.get("category", ""),
    }
```

`response.follow()`는 직접 전달한 `meta`만 사용합니다. 이전 값이 필요하면 필요한 키만 골라 전달하세요.

스파이더 시스템은 일부 메타데이터도 자동으로 저장합니다. 예를 들어 프록시 순환을 사용하면 요청에 사용한 프록시를 `response.meta["proxy"]`에서 확인할 수 있습니다.
