---
title: "한 크롤러에서 HTTP 세션과 브라우저 세션 사용하기"
description: "이름이 있는 세션을 설정하고 HTTP 또는 브라우저 Fetcher로 요청을 보내세요. 쿠키를 재사용하고 필요할 때 세션을 시작하며 API 기록을 확인합니다."
---

# 스파이더 세션 {#spiders-sessions}

!!! success "시작 전 확인"

    1. [시작하기](getting-started.md)를 읽고 간단한 스파이더를 만들고 실행하는 방법을 알아두세요.
    2. [Fetcher 기본 사항](../fetching/choosing.md)과 HTTP 세션, Stealthy 세션의 차이를 알아두세요.

스파이더는 여러 Fetcher 세션을 동시에 사용할 수 있습니다. 예를 들어 간단한 페이지에는 빠른 HTTP 세션을, 보호된 페이지에는 스텔스 브라우저 세션을 사용할 수 있습니다. 이 페이지에서 세션 설정과 사용법을 알아봅니다.

## 세션이란? {#what-are-sessions}

세션은 미리 설정한 Fetcher 인스턴스로, 크롤링하는 동안 계속 실행됩니다. 요청마다 새 연결이나 브라우저를 만드는 대신 세션을 재사용하므로 더 빠르고 자원도 절약합니다.

기본적으로 모든 스파이더는 [FetcherSession](../fetching/static.md) 하나를 만듭니다. `configure_sessions()`를 재정의하면 세션을 추가하거나 기본 세션을 바꿀 수 있습니다. 아래 표처럼 각 세션의 비동기 버전만 사용해야 합니다.


| 세션 종류 | 용도 |
|-------------------------------------------------|------------------------------------------|
| [FetcherSession](../fetching/static.md) | JavaScript 없는 빠른 HTTP 요청 |
| [AsyncStealthySession](../fetching/stealthy.md) | JavaScript, 브라우저 자동화, 봇 차단 우회 |


## 세션 설정하기 {#configuring-sessions}

스파이더의 `configure_sessions()`를 재정의하세요. `manager`는 `SessionManager` 인스턴스입니다. `manager.add()`로 세션을 등록합니다.

```python
from scrapling.spiders import Spider, Response
from scrapling.fetchers import FetcherSession

class MySpider(Spider):
    name = "my_spider"
    start_urls = ["https://example.com"]

    def configure_sessions(self, manager):
        manager.add("default", FetcherSession())

    async def parse(self, response: Response):
        yield {"title": response.css("title::text").get("")}
```

`manager.add()`의 인수는 다음과 같습니다.

| 인수 | 타입 | 기본값 | 설명 |
|--------------|-----------|------------|----------------------------------------------|
| `session_id` | `str` | *필수* | 요청에서 이 세션을 지정할 이름 |
| `session` | `Session` | *필수* | 세션 인스턴스 |
| `default` | `bool` | `False` | 기본 세션으로 설정합니다 |
| `lazy` | `bool` | `False` | 처음 사용할 때만 세션을 시작합니다 |

!!! note "참고"

    1. 요청에 세션을 지정하지 않으면 기본 세션을 사용합니다. 기본 세션은 다음 두 방법으로 정해집니다.
        1. 관리자에 처음 추가한 세션이 자동으로 기본 세션이 됩니다.
        2. 세션을 추가할 때 `default=True`를 지정합니다.
    2. 세션 인스턴스를 미리 시작할 필요는 없습니다. 스파이더가 아직 시작하지 않은 세션을 확인하고 시작합니다.
    3. 필요할 때만 세션을 시작하려면 추가할 때 `lazy`를 사용하세요. 예를 들어 브라우저를 스파이더 시작 시점이 아니라 실제로 필요할 때 열 수 있습니다.

## 여러 세션을 쓰는 스파이더 {#multi-session-spider}

목록 페이지에는 빠른 HTTP 세션을, 봇 차단이 있는 상세 페이지에는 스텔스 브라우저를 사용하는 예입니다.

```python
from scrapling.spiders import Spider, Response
from scrapling.fetchers import FetcherSession, AsyncStealthySession

class ProductSpider(Spider):
    name = "products"
    start_urls = ["https://shop.example.com/products"]

    def configure_sessions(self, manager):
        # Fast HTTP for listing pages (default)
        manager.add("http", FetcherSession())

        self.browser_session = AsyncStealthySession(
            headless=True,
            network_idle=True,
            record_requests=True,
        )
        manager.add("stealth", self.browser_session)

    async def parse(self, response: Response):
        for link in response.css("a.product::attr(href)").getall():
            # Route product pages through the stealth session
            yield response.follow(link, sid="stealth", callback=self.parse_product)

        next_page = response.css("a.next::attr(href)").get()
        if next_page:
            yield response.follow(next_page)

    async def parse_product(self, response: Response):
        yield {
            "name": response.css("h1::text").get(""),
            "price": response.css(".price::text").get(""),
        }

    async def on_close(self):
        for api_response in self.browser_session.network.search(
            url_pattern=r"https://api\.shop\.example\.com/.*", limit=None
        ):
            self.logger.info(f"Saved API response: {api_response.url} ({api_response.status})")
```

이 예는 브라우저 인스턴스를 유지하고, 세션을 닫기 전에 `on_close()`에서 저장된 API 기록을 한 번 읽습니다. 기록은 모든 상품 페이지를 포함하며 닫은 뒤에도 읽을 수 있습니다. 아직 저장 중인 기록은 기다리지 않고, 보관 개수 제한도 계속 적용됩니다.

핵심은 각 요청에 사용할 세션을 정하는 `sid`입니다. `sid` 없이 `response.follow()`를 호출하면 원래 요청의 세션 ID를 상속합니다.

세션이 서로 다른 클래스일 필요는 없습니다. 같은 클래스의 인스턴스를 서로 다른 설정으로 사용할 수도 있습니다.

```python
from scrapling.spiders import Spider, Response
from scrapling.fetchers import FetcherSession

class ProductSpider(Spider):
    name = "products"
    start_urls = ["https://shop.example.com/products"]

    def configure_sessions(self, manager):
        chrome_requests = FetcherSession(impersonate="chrome")
        firefox_requests = FetcherSession(impersonate="firefox")

        manager.add("chrome", chrome_requests)
        manager.add("firefox", firefox_requests)

    async def parse(self, response: Response):
        for link in response.css("a.product::attr(href)").getall():
            yield response.follow(link, callback=self.parse_product)

        next_page = response.css("a.next::attr(href)").get()
        if next_page:
            yield response.follow(next_page, sid="firefox")

    async def parse_product(self, response: Response):
        yield {
            "name": response.css("h1::text").get(""),
            "price": response.css(".price::text").get(""),
        }
```

또는 특정 요청을 위해 별도의 쿠키와 상태를 가진 세션을 유지할 수도 있습니다.

## 세션 인수 {#session-arguments}

`Request` 또는 `response.follow(**kwargs)`에 전달한 추가 키워드 인수는 세션의 가져오기 메서드로 전달합니다. 세션 전체 설정을 바꾸지 않고 개별 요청을 조정할 수 있습니다.

```python
async def parse(self, response: Response):
    # Pass extra headers for this specific request
    yield Request(
        "https://api.example.com/data",
        headers={"Authorization": "Bearer token123"},
        callback=self.parse_api,
    )

    # Use a different HTTP method
    yield Request(
        "https://example.com/submit",
        method="POST",
        data={"field": "value"},
        sid="firefox",
        callback=self.parse_result,
    )
```

!!! warning

    보통 `FetcherSession`, `Fetcher`, `AsyncFetcher`에서는 `.get()`, `.post()`처럼 메서드를 호출해 HTTP 메서드를 선택합니다. 하지만 스파이더에서 `FetcherSession`을 쓸 때는 이렇게 하지 않습니다. 기본 요청은 _HTTP GET_입니다. 다른 메서드를 쓰려면 위 예처럼 `method` 인수로 전달하세요. 모든 세션 종류에서 같은 `Request` 인터페이스를 사용하기 위한 방식입니다.

위의 여러 세션 예에 등록한 `"stealth"` 세션(`AsyncStealthySession`)에는 `wait_selector`, `page_action`, `extra_headers` 같은 브라우저 전용 인수도 전달할 수 있습니다.

```python
async def parse(self, response: Response):
    # Use Cloudflare solver with the `AsyncStealthySession` we configured above
    yield Request(
        "https://nopecha.com/demo/cloudflare",
        sid="stealth",
        callback=self.parse_result,
        solve_cloudflare=True,
        block_webrtc=True,
        hide_canvas=True,
        google_search=True,
    )

    yield response.follow(
        "/dynamic-page",
        sid="stealth",
        callback=self.parse_dynamic,
        wait_selector="div.loaded",
        network_idle=True,
    )
```

!!! warning

    `response.follow()`는 원래 요청의 세션 인수(**kwargs)를 상속하지만 `method`, `params`, `data`, `json`, `files`, `multipart`는 제외합니다. 따라서 POST 다음에 링크를 따라가면 일반 GET을 보냅니다. 새 인수는 상속한 인수보다 우선합니다.

```python
from scrapling.spiders import Spider, Response
from scrapling.fetchers import FetcherSession

class ProductSpider(Spider):
    name = "products"
    start_urls = ["https://shop.example.com/products"]

    def configure_sessions(self, manager):
        manager.add("http", FetcherSession(impersonate='chrome'))

    async def parse(self, response: Response):
        # I don't want the follow request to impersonate a desktop Chrome like the previous request, but a mobile one
        # so I override it like this
        for link in response.css("a.product::attr(href)").getall():
            yield response.follow(link, impersonate="chrome131_android", callback=self.parse_product)

        next_page = response.css("a.next::attr(href)").get()
        if next_page:
            yield response.follow(next_page)

    async def parse_product(self, response: Response):
        yield {
            "name": response.css("h1::text").get(""),
            "price": response.css(".price::text").get(""),
        }
```
!!! info

    스파이더가 종료될 때 관리자가 실행 중인 세션을 확인하고, 스파이더를 닫기 전에 자동으로 닫습니다.
