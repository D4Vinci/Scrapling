---
title: "프록시 순환과 차단된 크롤링 요청 재시도"
description: "Scrapling 스파이더에서 프록시와 순환 방식을 사용하세요. 차단된 응답을 감지하고 요청을 재시도하며 HTTP에서 브라우저 세션으로 전환합니다."
---

# 프록시 관리와 차단 처리 {#proxy-management-and-handling-blocks}

## 소개 {#introduction}

!!! success "시작 전 확인"

    1. [시작하기](getting-started.md)를 읽고 간단한 스파이더를 만들고 실행하는 방법을 알아두세요.
    2. [세션](sessions.md)을 읽고 세션 설정 방법을 이해해야 합니다.

많은 데이터를 수집할 때는 요청 빈도 제한이나 차단을 피하기 위해 여러 프록시를 번갈아 써야 할 수 있습니다. Scrapling의 `ProxyRotator`로 간단하게 처리할 수 있습니다. 모든 세션 종류와 함께 사용할 수 있고, 스파이더의 차단 요청 재시도 기능과도 연결됩니다.

프록시가 무엇인지, 어떻게 골라야 하는지 모른다면 [이 안내](https://substack.thewebscraping.club/p/everything-about-proxies)를 참고하세요.

## ProxyRotator {#proxyrotator}

`ProxyRotator`는 프록시 목록을 관리하고 자동으로 순환합니다. 세션의 `proxy_rotator` 인수로 전달하세요.

```python
from scrapling.spiders import Spider, Response
from scrapling.fetchers import FetcherSession, ProxyRotator

class MySpider(Spider):
    name = "my_spider"
    start_urls = ["https://example.com"]

    def configure_sessions(self, manager):
        rotator = ProxyRotator([
            "http://proxy1:8080",
            "http://proxy2:8080",
            "http://user:pass@proxy3:8080",
        ])
        manager.add("default", FetcherSession(proxy_rotator=rotator))

    async def parse(self, response: Response):
        # Check which proxy was used
        print(f"Proxy used: {response.meta.get('proxy')}")
        yield {"title": response.css("title::text").get("")}
```

각 요청은 순서에 따라 다음 프록시를 자동으로 사용합니다. 사용한 프록시는 `response.meta["proxy"]`에 저장되므로 어떤 프록시로 페이지를 가져왔는지 확인할 수 있습니다.


브라우저 세션에서는 다음과 같이 조금 다르게 설정합니다.

```python
from scrapling.fetchers import AsyncStealthySession, ProxyRotator

# String proxies work for all session types
rotator = ProxyRotator([
    "http://proxy1:8080",
    "http://proxy2:8080",
])

# Dict proxies (Playwright format) work for browser sessions
rotator = ProxyRotator([
    {"server": "http://proxy1:8080", "username": "user", "password": "pass"},
    {"server": "http://proxy2:8080"},
])

# Then inside the spider
def configure_sessions(self, manager):
    rotator = ProxyRotator(["http://proxy1:8080", "http://proxy2:8080"])
    manager.add("browser", AsyncStealthySession(proxy_rotator=rotator))
```

!!! info

    1. 한 세션에서 `proxy_rotator`를 고정 `proxy` 또는 `proxies` 인수와 함께 사용할 수 없습니다. 세션을 설정할 때 한 방식을 선택하세요. 나중에 개별 요청에서 프록시를 바꾸는 방법은 아래에서 설명합니다.
    2. 기본적으로 모든 브라우저 세션은 여러 탭을 관리하는 풀과 영구 브라우저 컨텍스트를 사용합니다. 하지만 브라우저는 탭마다 다른 프록시를 설정할 수 없습니다. 따라서 `ProxyRotator`를 사용하면 Fetcher가 프록시마다 별도의 컨텍스트와 탭 하나를 만듭니다. 탭의 작업이 끝나면 탭과 컨텍스트를 모두 닫습니다.

## 프록시 순환 방식 바꾸기 {#custom-rotation-strategies}

기본적으로 `ProxyRotator`는 프록시를 순서대로 사용하고, 마지막에 도달하면 처음부터 다시 시작합니다.

다른 방식이 필요하면 다음 시그니처를 따르는 함수를 전달하세요.

```python
from scrapling.core._types import ProxyType

def my_strategy(proxies: list, current_index: int) -> tuple[ProxyType, int]:
    ...
```

이 함수는 프록시 목록과 현재 인덱스를 받고, 선택한 프록시와 다음 인덱스를 반환해야 합니다.

다음은 사용자 정의 순환 방식의 예입니다.

### 무작위 선택 {#random-rotation}

```python
import random
from scrapling.fetchers import ProxyRotator

def random_strategy(proxies, current_index):
    idx = random.randint(0, len(proxies) - 1)
    return proxies[idx], idx

rotator = ProxyRotator(
    ["http://proxy1:8080", "http://proxy2:8080", "http://proxy3:8080"],
    strategy=random_strategy,
)
```

### 가중치에 따른 선택 {#weighted-rotation}

```python
import random

def weighted_strategy(proxies, current_index):
    # First proxy gets 60% of traffic, others split the rest
    weights = [60] + [40 // (len(proxies) - 1)] * (len(proxies) - 1)
    proxy = random.choices(proxies, weights=weights, k=1)[0]
    return proxy, current_index  # Index doesn't matter for weighted

rotator = ProxyRotator(proxies, strategy=weighted_strategy)
```


## 개별 요청의 프록시 바꾸기 {#per-request-proxy-override}

개별 요청에 `proxy=` 키워드 인수를 전달하면 자동 순환 대신 해당 프록시를 사용합니다.

```python
async def parse(self, response: Response):
    # This request uses the rotator's next proxy
    yield response.follow("/page1", callback=self.parse_page)

    # This request uses a specific proxy, bypassing the rotator
    yield response.follow(
        "/special-page",
        callback=self.parse_page,
        proxy="http://special-proxy:8080",
    )
```

특정 페이지에 지정된 프록시가 필요할 때 유용합니다. 예를 들어 지역별 콘텐츠를 가져올 때 해당 지역의 프록시를 쓸 수 있습니다.

## 차단된 요청 처리 {#blocked-request-handling}

스파이더에는 차단 감지와 재시도 기능이 있습니다. 기본적으로 `401`, `403`, `407`, `429`, `444`, `500`, `502`, `503`, `504` HTTP 상태 코드를 차단으로 봅니다.

재시도는 다음 순서로 진행합니다.

1. 응답을 받으면 `is_blocked(response)`를 호출합니다.
2. 차단된 경우 요청을 복사하고 `retry_blocked_request()`를 호출합니다. 여기서 재시도할 요청을 수정할 수 있습니다.
3. 요청을 `dont_filter=True`와 낮은 우선순위로 큐에 다시 넣습니다. 중복 제거를 건너뛰고 바로 재시도하지 않도록 합니다.
4. 최대 `max_blocked_retries`번 반복합니다. 기본값은 3입니다.

!!! tip

    1. 재시도할 때 기존 `proxy`/`proxies` 인수를 요청에서 자동으로 지웁니다. 따라서 순환 기능이 새 프록시를 선택합니다.
    2. `max_blocked_retries`는 세션 내부의 재시도와 별개이며 횟수를 공유하지 않습니다.

### 차단 감지 바꾸기 {#custom-block-detection}

`is_blocked()`를 재정의해 필요한 감지 방식을 추가하세요.

```python
class MySpider(Spider):
    name = "my_spider"
    start_urls = ["https://example.com"]

    async def is_blocked(self, response: Response) -> bool:
        # Check status codes (default behavior)
        if response.status in {403, 429, 503}:
            return True

        # Check response content
        body = response.body.decode("utf-8", errors="ignore")
        if "access denied" in body.lower() or "rate limit" in body.lower():
            return True

        return False

    async def parse(self, response: Response):
        yield {"title": response.css("title::text").get("")}
```

### 재시도 동작 바꾸기 {#customizing-retries}

`retry_blocked_request()`를 재정의하면 재시도 전에 요청을 바꿀 수 있습니다. `max_blocked_retries`는 차단된 요청의 재시도 횟수이며 기본값은 3입니다.

```python
from scrapling.spiders import Spider, SessionManager, Request, Response
from scrapling.fetchers import FetcherSession, AsyncStealthySession


class MySpider(Spider):
    name = "my_spider"
    start_urls = ["https://example.com"]
    max_blocked_retries = 5

    def configure_sessions(self, manager: SessionManager) -> None:
        manager.add('requests', FetcherSession(impersonate=['chrome', 'firefox', 'safari']))
        manager.add('stealth', AsyncStealthySession(block_webrtc=True), lazy=True)

    async def retry_blocked_request(self, request: Request, response: Response) -> Request:
        request.sid = "stealth"
        self.logger.info(f"Retrying blocked request: {request.url}")
        return request

    async def parse(self, response: Response):
        yield {"title": response.css("title::text").get("")}
```

위 예는 차단 감지 방식을 그대로 두고 HTTP 요청을 사용하다가 차단되면 스텔스 브라우저로 전환합니다.


모두 합치면 다음과 같습니다.

```python
from scrapling.spiders import Spider, SessionManager, Request, Response
from scrapling.fetchers import FetcherSession, AsyncStealthySession, ProxyRotator


cheap_proxies = ProxyRotator([ "http://proxy1:8080", "http://proxy2:8080"])

# A format acceptable by the browser
expensive_proxies = ProxyRotator([
    {"server": "http://residential_proxy1:8080", "username": "user", "password": "pass"},
    {"server": "http://residential_proxy2:8080", "username": "user", "password": "pass"},
    {"server": "http://mobile_proxy1:8080", "username": "user", "password": "pass"},
    {"server": "http://mobile_proxy2:8080", "username": "user", "password": "pass"},
])


class MySpider(Spider):
    name = "my_spider"
    start_urls = ["https://example.com"]
    max_blocked_retries = 5

    def configure_sessions(self, manager: SessionManager) -> None:
        manager.add('requests', FetcherSession(impersonate=['chrome', 'firefox', 'safari'], proxy_rotator=cheap_proxies))
        manager.add('stealth', AsyncStealthySession(block_webrtc=True, proxy_rotator=expensive_proxies), lazy=True)

    async def retry_blocked_request(self, request: Request, response: Response) -> Request:
        request.sid = "stealth"
        self.logger.info(f"Retrying blocked request: {request.url}")
        return request

    async def parse(self, response: Response):
        yield {"title": response.css("title::text").get("")}
```
처음에는 데이터센터 프록시처럼 저렴한 프록시를 사용합니다. 차단되면 주거용이나 모바일 프록시처럼 품질이 높은 프록시로 재시도합니다.
