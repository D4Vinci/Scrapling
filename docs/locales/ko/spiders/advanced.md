---
title: "크롤링 제어: AutoThrottle, 체크포인트, 캐시, 스트리밍"
description: "크롤링 속도와 동시 요청을 제어하세요. 응답 캐시, 일시 중지와 재개, 항목 스트리밍, 체크포인트에 저장되는 상태를 알아봅니다."
---

# 고급 기능 {#advanced-usages}

## 소개 {#introduction}

!!! success "시작 전 확인"

    1. [시작하기](getting-started.md)를 읽고 간단한 스파이더를 만들고 실행하는 방법을 알아두세요.

이 페이지는 동시 요청 제어, 일시 중지와 재개, 스트리밍, 수명 주기 훅, 통계, 로깅 등 스파이더의 고급 기능을 설명합니다.

## 동시 요청 제어 {#concurrency-control}

다음 클래스 속성으로 크롤링 부하를 조정합니다.

| 속성 | 기본값 | 설명 |
|----------------------------------|---------|------------------------------------------------------------------|
| `concurrent_requests` | `4` | 동시에 처리할 최대 요청 수 |
| `concurrent_requests_per_domain` | `0` | 도메인별 최대 동시 요청 수입니다. 0은 도메인별 제한이 없다는 뜻입니다 |
| `download_delay` | `0.0` | 각 요청 전 대기 시간(초) |
| `robots_txt_obey` | `False` | robots.txt의 Disallow, Crawl-delay, Request-rate 규칙을 지킵니다 |

```python
class PoliteSpider(Spider):
    name = "polite"
    start_urls = ["https://example.com"]

    # Be gentle with the server
    concurrent_requests = 4
    concurrent_requests_per_domain = 2
    download_delay = 1.0  # Wait 1 second between requests

    async def parse(self, response: Response):
        yield {"title": response.css("title::text").get("")}
```

`concurrent_requests_per_domain`을 설정하면 전체 제한 외에 도메인별 제한이 생깁니다. 여러 도메인을 동시에 크롤링할 때 전체 요청 수는 높게 유지하면서 각 사이트의 부하를 줄일 수 있습니다.

!!! tip

    `download_delay`는 도메인과 관계없이 모든 요청 전에 고정된 시간을 기다립니다. 간단한 요청 빈도 제한에 사용하세요.

## AutoThrottle {#autothrottle}

고정된 `download_delay`는 직접 예상해서 정해야 합니다. 너무 짧으면 차단되고 너무 길면 크롤링이 오래 걸립니다. AutoThrottle은 실제 응답 속도를 보고 각 도메인의 지연을 조정합니다. 빠른 서버에서는 속도를 높이고, 느리거나 요청을 차단하는 서버에서는 속도를 줄입니다.

| 속성 | 기본값 | 설명 |
|------------------------------------|---------|-------------------------------------------------------------------|
| `autothrottle_enabled` | `False` | 적응형 지연을 켭니다 |
| `autothrottle_start_delay` | `5.0` | 도메인의 첫 요청에 사용할 지연 |
| `autothrottle_max_delay` | `60.0` | 허용되는 최대 지연 |
| `autothrottle_target_concurrency` | `None` | 목표로 하는 도메인별 동시 요청 수입니다. 아래 설명을 참고하세요 |
| `autothrottle_block_backoff` | `True` | 차단될 때마다 해당 도메인의 지연을 두 배로 늘립니다 |

```python
class AdaptiveSpider(Spider):
    name = "adaptive"
    start_urls = ["https://example.com"]

    concurrent_requests = 8
    concurrent_requests_per_domain = 1

    autothrottle_enabled = True
    autothrottle_start_delay = 2.0
    autothrottle_max_delay = 30.0

    async def parse(self, response: Response):
        yield {"title": response.css("title::text").get("")}
```

응답을 받을 때마다 지연은 서버의 응답 시간에 가까워집니다. 사이트가 0.5초 안에 응답하면 지연도 약 0.5초가 되며, 대략 요청 하나씩 처리하는 상태가 됩니다. 도메인별 목표 요청 수는 설정된 `autothrottle_target_concurrency`, 다음으로 `concurrent_requests_per_domain`, 둘 다 없으면 1을 사용합니다. 이미 설정한 도메인별 제한이 목표가 되고 지연을 그 값으로 나누므로, 보통 별도의 목표를 지정할 필요가 없습니다. 응답 시간이 급격히 늘어나면 평균을 기다리지 않고 바로 반영합니다. 따라서 서버가 느려지면 즉시 속도를 줄이고, 다시 빨라질 때는 서서히 속도를 높입니다.

### 차단될 때 속도 줄이기 {#backing-off-when-blocked}

응답 시간만으로는 요청 빈도 제한을 알 수 없습니다. `429`, `403`, CAPTCHA 페이지는 실제 콘텐츠보다 *더 빨리* 돌아오는 경우가 많습니다. 시간만 보면 속도를 높여도 된다고 판단할 수 있습니다. 따라서 상태 코드가 2xx가 아니거나 `is_blocked()`가 차단으로 판단한 응답은 도메인의 지연을 **두 배로 늘립니다**.

```
0.5s -> 1s -> 2s -> 4s -> 8s ...   (up to autothrottle_max_delay)
```

사이트가 계속 거부하면 스파이더도 계속 느려집니다. 정상 응답이 돌아오면 다시 평균을 적용해 서버 속도에 맞게 지연을 낮춥니다. 다시 시작하지 않아도 자동으로 회복합니다.

사이트가 `429` 또는 `503` 응답의 `Retry-After` 헤더로 대기 시간을 알려주면, 지연을 두 배로 늘리는 대신 그 값을 사용합니다. 숫자 형식(`Retry-After: 120`)과 HTTP 날짜 형식을 모두 이해합니다.

이 기능을 끄려면 `autothrottle_block_backoff = False`를 설정하세요. 응답 시간만으로 지연을 조정하며, 차단은 속도가 더 빨라지는 것만 막습니다.

도메인별 최종 지연은 통계에서 확인할 수 있습니다.

```python
result = AdaptiveSpider().start()
print(result.stats.autothrottle_delays)  # {'example.com': 0.62}
```

!!! note "참고"

    * `download_delay`와 robots.txt 지연은 최솟값으로 사용하지만, 이 값도 `autothrottle_max_delay`의 제한을 받습니다. 지켜야 하는 설정 또는 robots.txt 지연 이상으로 최댓값을 정하세요.<br/>
    * `concurrent_requests_per_domain`은 도메인의 동시 요청 수를 제한하면서 AutoThrottle의 목표가 됩니다. 보통 목표를 따로 설정할 필요는 없습니다. 이 값을 설정하는 것이 좋습니다. 요청이 도메인 지연을 기다리는 동안에도 전체 제한의 한 자리를 차지하기 때문입니다. 도메인별 제한이 없으면 대기 중인 요청들이 다른 도메인과 공유하는 자리를 사용합니다.<br/>
    * 측정 시간에는 내부 재시도를 포함한 전체 가져오기 시간이 들어갑니다. 브라우저 세션에서는 페이지 렌더링 시간도 포함합니다.<br/>
    * `autothrottle_max_delay`는 `Retry-After`를 포함한 모든 지연을 제한합니다. 사이트가 더 오래 기다리라고 하면 `autothrottle_max_delay`를 늘리세요.<br/>
    * 계산된 지연은 체크포인트에 저장하지 않습니다. 일시 중지 후 재개하면 각 도메인은 다시 `autothrottle_start_delay`부터 시작합니다.

## uvloop 사용하기 {#using-uvloop}

`start()`의 `use_uvloop` 인수로 더 빠른 [uvloop](https://github.com/MagicStack/uvloop)/[winloop](https://github.com/nicktimko/winloop) 이벤트 루프를 사용할 수 있습니다. 해당 패키지가 설치되어 있어야 합니다.

```python
result = MySpider().start(use_uvloop=True)
```

입출력이 많은 크롤링의 처리량을 높일 수 있습니다. `uvloop`(Linux/macOS) 또는 `winloop`(Windows)를 별도로 설치하세요.

## 일시 중지와 재개 {#pause-resume}

스파이더는 체크포인트로 안전하게 일시 중지하고 재개할 수 있습니다. 사용하려면 생성자에 `crawldir` 디렉터리를 전달하세요.

```python
spider = MySpider(crawldir="crawl_data/my_spider")
result = spider.start()

if result.paused:
    print("Crawl was paused. Run again to resume.")
else:
    print("Crawl completed!")
```

### 동작 방식 {#how-it-works}

1. **일시 중지**: 크롤링 중 `Ctrl+C`를 누르세요. 실행 중인 요청이 끝날 때까지 기다린 뒤, 대기 요청과 이미 확인한 요청 지문 집합을 체크포인트로 저장하고 종료합니다.
2. **강제 중지**: `Ctrl+C`를 다시 누르면 실행 중인 작업을 기다리지 않고 바로 멈춥니다.
3. **재개**: 같은 `crawldir`로 다시 실행하세요. 체크포인트를 찾아 큐와 지문 집합을 복원하고, `start_requests()`를 건너뛰어 중단한 곳부터 계속합니다.
4. **정리**: 일시 중지가 아니라 크롤링이 정상적으로 끝나면 체크포인트 파일을 자동으로 삭제합니다.

**크롤링 중에도 체크포인트를 주기적으로 저장합니다. 기본 간격은 5분입니다.**

간격은 다음과 같이 바꿀 수 있습니다.

```python
# Save checkpoint every 2 minutes
spider = MySpider(crawldir="crawl_data/my_spider", interval=120.0)
```

체크포인트를 쓸 때는 임시 파일을 사용하고, 쓰기에 성공한 경우에만 이전 체크포인트를 교체합니다.

!!! warning "체크포인트 데이터"

    `crawldir`를 사용하면 `meta`와 요청 인수를 포함한 대기 요청의 값은 Python의 `pickle` 모듈로 저장할 수 있어야 합니다. 저장할 수 없는 값이 있으면 체크포인트 저장에 실패하고 크롤링이 중지됩니다. `Selector`는 콜백에서 사용할 수 있지만 이 방식으로 저장할 수는 없습니다.

    `Selector` 객체 대신 문자열이나 숫자처럼 추출한 값을 저장하세요. 리스트와 딕셔너리에도 저장할 수 있는 값만 담아야 합니다.

    ```python
    yield response.follow("/details", meta={"title": str(response.css("h1::text").get(""))})
    ```

!!! tip

    `start()`를 사용할 때 `Ctrl+C`를 누르면 체크포인트를 켜지 않아도 진행 중인 작업을 마친 뒤 종료합니다. 기다리지 않고 다시 누르면 즉시 강제로 종료합니다.

### 재개 중인지 확인하기 {#knowing-if-youre-resuming}

`on_start()` 훅은 `resuming` 플래그를 받습니다.

```python
async def on_start(self, resuming: bool = False):
    if resuming:
        self.logger.info("Resuming from checkpoint!")
    else:
        self.logger.info("Starting fresh crawl")
```

## 개발 모드 {#development-mode}

`parse()`를 수정할 때마다 서버에 요청하면 느리고 불필요한 부하가 생깁니다. 개발 모드는 첫 실행에서 응답을 디스크에 캐시하고, 다음 실행에서는 저장된 응답을 사용합니다. 같은 페이지를 다시 가져오지 않고 선택자를 바꾸고 스파이더를 반복 실행할 수 있습니다.

스파이더에 `development_mode = True`를 설정하세요.

```python
class MySpider(Spider):
    name = "my_spider"
    start_urls = ["https://example.com"]
    development_mode = True

    async def parse(self, response: Response):
        yield {"title": response.css("title::text").get("")}
```

첫 실행은 정상적으로 페이지를 가져와 응답을 저장합니다. 다음 실행부터 같은 요청은 페이지를 가져오지 않고 캐시에서 처리합니다. `robots_txt_obey=True`이면 캐시를 찾기 전에 robots.txt를 확인합니다.

### 캐시 위치 {#cache-location}

기본 위치는 현재 작업 디렉터리 아래의 `.scrapling_cache/{spider.name}/`입니다. 스파이더를 실행한 디렉터리이며, 스크립트 파일이 있는 위치가 **아닙니다**. `development_cache_dir`로 변경할 수 있습니다.

```python
class MySpider(Spider):
    name = "my_spider"
    start_urls = ["https://example.com"]
    development_mode = True
    development_cache_dir = "/tmp/my_spider_cache"
```

### 동작 방식 {#how-it-works_1}

1. **캐시 키**: 요청 지문을 사용합니다. 지문에 영향을 주는 속성(`fp_include_kwargs`, `fp_include_headers`, `fp_keep_fragments`)을 바꾸면 새로 가져옵니다.
2. **저장 형식**: 응답마다 `{fingerprint_hex}.json` 파일 하나를 만듭니다. 바이너리 데이터를 그대로 보관하도록 본문은 base64로 인코딩합니다. 임시 파일을 만든 뒤 이름을 바꾸는 원자적 쓰기를 사용합니다.
3. **캐시 사용**: 캐시에 있으면 페이지 가져오기와 함께 `download_delay`, 요청 빈도 제한, `is_blocked()` 재시도 과정을 건너뜁니다. 캐시된 응답은 콜백으로 바로 전달합니다.
4. **통계**: 캐시 요청도 `requests_count`, `response_bytes`, 상태 코드별 횟수에 포함되므로 일반 크롤링과 같은 통계를 볼 수 있습니다. `cache_hits`와 `cache_misses`로 캐시 사용 결과도 확인할 수 있습니다.

### 캐시 지우기 {#clearing-the-cache}

캐시는 자동으로 만료되지 않습니다. 새로 크롤링하려면 캐시 디렉터리를 삭제하거나 관리자의 `clear()`를 직접 호출하세요.

!!! warning

    개발 모드는 개발 전용입니다. 캐시 응답은 만료되지 않고, 캐시 사용 시 요청 빈도 제한과 차단 요청 재시도를 건너뜁니다. 운영 환경에서는 `development_mode = True`를 사용하지 마세요.

## 스트리밍 {#streaming}

오래 실행하는 스파이더나 수집한 항목을 즉시 사용하는 앱에서는 `start()` 대신 `stream()`을 사용하세요.

```python
import anyio

async def main():
    spider = MySpider()
    async for item in spider.stream():
        print(f"Got item: {item}")
        # Access real-time stats
        print(f"Items so far: {spider.stats.items_scraped}")
        print(f"Requests made: {spider.stats.requests_count}")

anyio.run(main)
```

`start()`와의 주요 차이는 다음과 같습니다.

- `stream()`은 비동기 컨텍스트에서 호출해야 합니다.
- 항목을 리스트에 모으지 않고 수집할 때마다 하나씩 내보냅니다.
- 반복 중에 `spider.stats`로 실시간 통계를 볼 수 있습니다.

!!! abstract

    `spider.stats`에서 확인할 수 있는 전체 통계는 [아래](#results-statistics)에 설명되어 있습니다.

체크포인트와 함께 사용할 수도 있습니다. 실시간 데이터를 보여주면서 일시 중지와 재개를 지원하는 UI를 쉽게 만들 수 있습니다.

```python
import anyio

async def main():
    spider = MySpider(crawldir="crawl_data/my_spider")
    async for item in spider.stream():
        print(f"Got item: {item}")
        # Access real-time stats
        print(f"Items so far: {spider.stats.items_scraped}")
        print(f"Requests made: {spider.stats.requests_count}")

anyio.run(main)
```
위 코드에서 `spider.pause()`로 스파이더를 종료할 수도 있습니다. 체크포인트를 켜지 않았다면 크롤링만 종료합니다.

## 수명 주기 훅 {#lifecycle-hooks}

여러 단계에서 원하는 동작을 추가할 수 있도록 재정의 가능한 훅을 제공합니다.

### on_start {#on_start}

크롤링 전에 호출합니다. 데이터 로드나 자원 초기화 같은 준비 작업에 사용하세요.

```python
async def on_start(self, resuming: bool = False):
    self.logger.info("Spider starting up")
    # Load seed URLs from a database, initialize counters, etc.
```

### on_close {#on_close}

크롤링이 완료되거나 일시 중지된 뒤 호출합니다. 자원 정리에 사용하세요.

```python
async def on_close(self):
    self.logger.info("Spider shutting down")
    # Close database connections, flush buffers, etc.
```

### on_error {#on_error}

요청에서 예외가 발생하면 호출합니다. 오류 기록이나 복구 작업에 사용하세요.

```python
async def on_error(self, request: Request, error: Exception):
    self.logger.error(f"Failed: {request.url} - {error}")
    # Log to error tracker, save failed URL for later, etc.
```

### on_scraped_item {#on_scraped_item}

수집한 각 항목을 결과에 넣기 전에 호출합니다. 유지하려면 수정 여부와 관계없이 항목을 반환하고, 제외하려면 `None`을 반환하세요.

```python
async def on_scraped_item(self, item: dict) -> dict | None:
    # Drop items without a title
    if not item.get("title"):
        return None

    # Modify items (e.g., add timestamps)
    item["scraped_at"] = "2026-01-01"
    return item
```

!!! tip

    이 훅으로 항목을 직접 만든 처리 파이프라인에 전달한 뒤 스파이더 결과에서 제외할 수도 있습니다.

### start_requests {#start_requests}

`start_urls` 대신 원하는 방식으로 시작 요청을 만들려면 `start_requests()`를 재정의하세요.

```python
async def start_requests(self):
    # POST request to log in first
    yield Request(
        "https://example.com/login",
        method="POST",
        data={"user": "admin", "pass": "secret"},
        callback=self.after_login,
    )

async def after_login(self, response: Response):
    # Now crawl the authenticated pages
    yield response.follow("/dashboard", callback=self.parse)
```

## 결과와 통계 {#results-statistics}

`start()`가 반환하는 `CrawlResult`에는 수집한 항목과 자세한 통계가 있습니다.

```python
result = MySpider().start()

# Items
print(f"Total items: {len(result.items)}")
result.items.to_json("output.json", indent=True)

# Did the crawl complete?
print(f"Completed: {result.completed}")
print(f"Paused: {result.paused}")

# Statistics
stats = result.stats
print(f"Requests: {stats.requests_count}")
print(f"Failed: {stats.failed_requests_count}")
print(f"Blocked: {stats.blocked_requests_count}")
print(f"Offsite filtered: {stats.offsite_requests_count}")
print(f"Robots.txt disallowed: {stats.robots_disallowed_count}")
print(f"Cache hits: {stats.cache_hits}")
print(f"Cache misses: {stats.cache_misses}")
print(f"Items scraped: {stats.items_scraped}")
print(f"Items dropped: {stats.items_dropped}")
print(f"Response bytes: {stats.response_bytes}")
print(f"Duration: {stats.elapsed_seconds:.1f}s")
print(f"Speed: {stats.requests_per_second:.1f} req/s")
```

### 자세한 통계 {#detailed-stats}

`CrawlStats`는 다음과 같은 세부 정보를 기록합니다.

```python
stats = result.stats

# Status code distribution
print(stats.response_status_count)
# {'status_200': 150, 'status_404': 3, 'status_403': 1}

# Bytes downloaded per domain
print(stats.domains_response_bytes)
# {'example.com': 1234567, 'api.example.com': 45678}

# Requests per session
print(stats.sessions_requests_count)
# {'http': 120, 'stealth': 34}

# Proxies used during the crawl
print(stats.proxies)
# ['http://proxy1:8080', 'http://proxy2:8080']

# Log level counts
print(stats.log_levels_counter)
# {'debug': 200, 'info': 50, 'warning': 3, 'error': 1, 'critical': 0}

# Timing information
print(stats.start_time)       # Unix timestamp when crawl started
print(stats.end_time)         # Unix timestamp when crawl finished
print(stats.download_delay)   # The download delay used (seconds)

# Concurrency settings used
print(stats.concurrent_requests)             # Global concurrency limit
print(stats.concurrent_requests_per_domain)  # Per-domain concurrency limit

# AutoThrottle
print(stats.autothrottle_enabled)  # Whether the adaptive delay was on
print(stats.autothrottle_delays)   # Final delay per domain, {'example.com': 0.62}

# Custom stats (set by your spider code)
print(stats.custom_stats)
# {'login_attempts': 3, 'pages_with_errors': 5}

# Export everything as a dict
print(stats.to_dict())
```

## 로깅 {#logging}

스파이더의 기본 로거는 `self.logger`로 사용할 수 있습니다. 스파이더 이름이 미리 설정되어 있고 다음 항목을 바꿀 수 있습니다.

| 속성 | 기본값 | 설명 |
|-----------------------|--------------------------------------------------------------|----------------------------------------------------|
| `logging_level` | `logging.DEBUG` | 기록할 최소 로그 수준 |
| `logging_format` | `"[%(asctime)s]:({spider_name}) %(levelname)s: %(message)s"` | 로그 메시지 형식 |
| `logging_date_format` | `"%Y-%m-%d %H:%M:%S"` | 로그 메시지의 날짜 형식 |
| `log_file` | `None` | 콘솔 출력과 함께 사용할 로그 파일 경로 |

```python
import logging

class MySpider(Spider):
    name = "my_spider"
    start_urls = ["https://example.com"]
    logging_level = logging.INFO
    log_file = "logs/my_spider.log"

    async def parse(self, response: Response):
        self.logger.info(f"Processing {response.url}")
        yield {"title": response.css("title::text").get("")}
```

로그 파일의 디렉터리가 없으면 자동으로 만듭니다. 콘솔과 파일은 같은 출력 형식을 사용합니다.
