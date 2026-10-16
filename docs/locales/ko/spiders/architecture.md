---
title: "Scrapling 웹 크롤러의 동작 방식"
description: "스파이더, 요청, 세션, 스케줄러, 크롤링 엔진이 어떻게 연결되는지 알아봅니다. Scrapy와 비교하고 시작할 방법을 선택하세요."
---

# 스파이더 아키텍처 {#spiders-architecture}

!!! success "시작 전 확인"

    1. [Fetcher 기본 사항](../fetching/choosing.md)을 읽고 Fetcher 종류와 각각의 용도를 이해해야 합니다.
    2. [주요 클래스](../parsing/main_classes.md)를 읽고 [Selector](../parsing/main_classes.md#selector)와 [Response](../fetching/choosing.md#response-object) 클래스를 이해해야 합니다.

Scrapling의 스파이더 시스템은 Scrapy에서 아이디어를 얻은 비동기 크롤링 프레임워크입니다. 여러 세션과 동시 요청, 일시 중지와 재개를 지원합니다. Scrapling의 파싱 엔진과 Fetcher를 하나의 크롤링 API로 묶고, 요청 예약, 동시 요청 제어, 체크포인트 기능을 제공합니다.

Scrapy에 익숙하다면 쉽게 사용할 수 있습니다. 처음 사용하는 사람도 이해하기 쉽게 설계했습니다.

## 데이터 흐름 {#data-flow}

다음 그림은 크롤링 중 데이터가 이동하는 과정을 보여줍니다.

<img src="../assets/spider_architecture.png" title="@TrueSkills가 만든 스파이더 아키텍처 그림" alt="@TrueSkills가 만든 스파이더 아키텍처 그림" style="width: 70%;"/>

스파이더를 실행하면 다음 순서로 동작합니다.

1. **스파이더**가 첫 `Request` 객체들을 만듭니다. 기본적으로 `start_urls`의 각 URL마다 요청 하나를 만듭니다. 다른 방식이 필요하면 `start_requests()`를 재정의할 수 있습니다.
2. **스케줄러**가 요청을 받아 우선순위 큐에 넣고 요청의 지문을 만듭니다. 우선순위가 높은 요청부터 꺼냅니다.
3. **크롤링 엔진**이 전체 및 도메인별 동시 요청 제한과 다운로드 지연을 지키면서 **스케줄러**에 다음 요청을 요청합니다. `robots_txt_obey`가 활성화되어 있으면 도메인의 robots.txt 규칙을 먼저 확인하고, 금지된 요청은 알림 없이 제외합니다. **크롤링 엔진**은 받은 요청을 **세션 관리자**에 전달합니다. 세션 관리자는 요청의 `sid`(세션 ID)로 사용할 세션을 선택합니다.
4. **세션**이 페이지를 가져와 [Response](../fetching/choosing.md#response-object) 객체를 **크롤링 엔진**에 반환합니다. 엔진은 통계를 기록하고 응답이 차단되었는지 확인합니다. 차단된 요청은 최대 `max_blocked_retries`번 재시도합니다. 차단 감지와 재시도 방식은 바꿀 수 있습니다.
5. **크롤링 엔진**이 [Response](../fetching/choosing.md#response-object)를 요청의 콜백에 전달합니다. 콜백은 수집한 항목을 나타내는 딕셔너리 또는 다음 요청을 내보냅니다. 다음 요청은 스케줄러로 전달되어 큐에 들어갑니다.
6. 큐가 비고 실행 중인 작업이 없어지거나 스파이더를 일시 중지할 때까지 2단계부터 반복합니다.
7. 시작할 때 `crawldir`를 설정했다면 **크롤링 엔진**이 대기 중인 요청과 이미 확인한 URL 집합을 체크포인트로 주기적으로 디스크에 저장합니다. 정상적인 종료 절차(Ctrl+C)에서도 마지막 체크포인트를 저장합니다. 같은 `crawldir`로 다시 실행하면 `start_requests()`를 건너뛰고 스케줄러 상태를 복원하여 중단한 곳부터 이어갑니다.


## 구성 요소 {#components}

### Spider {#spider}

사용자가 주로 다루는 클래스입니다. `Spider`를 상속하고 `start_urls`와 `parse()`를 정의합니다. 필요하면 세션을 설정하고 수명 주기 훅을 재정의합니다.

```python
from scrapling.spiders import Spider, Response, Request

class MySpider(Spider):
    name = "my_spider"
    start_urls = ["https://example.com"]

    async def parse(self, response: Response):
        for link in response.css("a::attr(href)").getall():
            yield response.follow(link, callback=self.parse_page)

    async def parse_page(self, response: Response):
        yield {"title": response.css("h1::text").get("")}
```

### 크롤링 엔진 {#crawler-engine}

전체 크롤링을 관리합니다. 메인 루프와 동시 요청 제한을 관리하고, 세션 관리자를 통해 요청을 보내고, 콜백 결과를 처리합니다. 직접 다룰 필요는 없습니다. `Spider.start()`와 `Spider.stream()`이 대신 처리합니다.

### 스케줄러 {#scheduler}

URL 중복 제거 기능이 있는 우선순위 큐입니다. 요청의 URL, HTTP 메서드, 본문, 세션 ID로 지문을 계산합니다. 체크포인트를 위한 `snapshot()`과 `restore()`를 지원하므로 크롤링 상태를 저장하고 복원할 수 있습니다.

### 세션 관리자 {#session-manager}

이름이 지정된 세션 인스턴스를 하나 이상 관리합니다. 세션은 다음 종류 중 하나입니다.

- [FetcherSession](../fetching/static.md)
- [AsyncStealthySession](../fetching/stealthy.md)

요청을 받으면 `sid` 필드로 알맞은 세션을 선택합니다. 세션은 기본적으로 스파이더와 함께 시작하지만, 처음 사용할 때 시작하도록 설정할 수도 있습니다.

### 체크포인트 시스템 {#checkpoint-system}

선택적으로 사용할 수 있는 기능입니다. 대기 중인 요청과 이미 확인한 URL 지문 등 크롤러 상태를 디스크의 pickle 파일에 저장합니다. 임시 파일을 만든 뒤 이름을 바꾸는 원자적 쓰기로 데이터 손상을 방지합니다. 체크포인트는 설정한 간격과 정상적인 종료 절차에서 저장됩니다. 일시 중지가 아닌 성공적인 크롤링 완료 후에는 파일이 자동으로 삭제됩니다.

### 응답 캐시 {#response-cache}

개발 모드에서 사용할 수 있는 선택적 캐시입니다. 가져온 응답을 디스크에 저장하고 다음 실행에서 다시 사용합니다. 각 응답은 요청 지문을 키로 삼아 JSON으로 저장합니다. 바이너리 데이터가 유지되도록 본문은 base64로 인코딩합니다. 서버에 다시 요청하지 않고 `parse()`를 수정하기 위한 기능이며, 운영 환경용이 아닙니다.

### 출력 {#output}

수집한 항목은 `ItemList`에 모입니다. 리스트를 상속하며 `to_json()`, `to_jsonl()`, `to_csv()`, `to_xml()` 내보내기 메서드를 제공합니다. 크롤링 통계는 유용한 정보를 담은 `CrawlStats` dataclass에 기록합니다.


## Scrapy와 비교 {#comparison-with-scrapy}

Scrapy를 사용했다면 다음 표로 기능을 비교할 수 있습니다.

| 개념 | Scrapy | Scrapling |
|--------------------|-------------------------------|-----------------------------------------------------------------|
| 스파이더 정의 | `scrapy.Spider` 상속 | `scrapling.spiders.Spider` 상속 |
| 시작 요청 | `start_requests()` | `async start_requests()` |
| 콜백 | `def parse(self, response)` | `async def parse(self, response)` |
| 링크 따라가기 | `response.follow(url)` | `response.follow(url)` |
| 항목 출력 | `yield dict` 또는 `yield Item` | `yield dict` |
| 요청 예약 | Scheduler + Dupefilter | 중복 제거 기능이 있는 스케줄러 |
| 다운로드 | Downloader + Middlewares | 여러 세션을 지원하는 세션 관리자 |
| 항목 처리 | Item Pipelines | `on_scraped_item()` 훅 |
| 차단 감지 | 사용자 정의 미들웨어 | 기본 제공 `is_blocked()` + `retry_blocked_request()` 훅 |
| 동시 요청 | `CONCURRENT_REQUESTS` 설정 | `concurrent_requests` 클래스 속성 |
| 도메인 제한 | `allowed_domains` | `allowed_domains` |
| Robots.txt | `ROBOTSTXT_OBEY` 설정 | `robots_txt_obey` 클래스 속성 |
| 일시 중지와 재개 | `JOBDIR` 설정 | `crawldir` 생성자 인수 |
| 내보내기 | Feed exports | `result.items.to_json()` / `to_jsonl()` / `to_csv()` / `to_xml()` 또는 훅을 통한 사용자 정의 내보내기 |
| 실행 | `scrapy crawl spider_name` | `MySpider().start()` |
| 스트리밍 | 지원 안 함 | `async for item in spider.stream()` |
| 여러 세션 | 지원 안 함 | 스파이더 하나에서 여러 종류의 세션 사용 |
