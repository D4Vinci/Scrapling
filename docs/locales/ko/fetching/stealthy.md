---
title: "StealthyFetcher로 JavaScript 사이트 스크래핑하기"
description: "Scrapling 브라우저 세션으로 페이지를 렌더링하고 데이터를 기다리며 로그인 상태와 백그라운드 API 응답을 활용하세요. 프록시와 보안 검사 처리도 설정할 수 있습니다."
---

# StealthyFetcher로 브라우저에서 가져오기 {#browser-fetching-with-stealthyfetcher}

`StealthyFetcher`는 JavaScript 페이지를 로드하고 봇 차단 우회 기능으로 Chromium이나 Google Chrome을 자동화합니다. 탐지를 피하도록 수정한 [Playwright API](https://playwright.dev/python/docs/intro)를 사용합니다.

뒤에서 설명할 페이지 자동화에는 [Playwright의 Page API](https://playwright.dev/python/docs/api/class-page)에 대한 기본 지식이 필요합니다.

!!! success "사전 준비"

    1. [Fetcher 기초](../fetching/choosing.md)를 읽고 [Response 객체](../fetching/choosing.md#response-object)와 Fetcher를 고르는 방법을 알아두세요.
    2. [요소 찾기](../parsing/selection.md)를 읽고 [Selector](../parsing/main_classes.md#selector)/[Response](../fetching/choosing.md#response-object)에서 요소를 찾고 추출하는 방법을 알아두세요.
    3. [주요 클래스](../parsing/main_classes.md)를 읽고 [Response](../fetching/choosing.md#response-object)가 [Selector](../parsing/main_classes.md#selector)에서 상속하는 속성과 메서드를 알아두세요.

## 기본 사용법 {#basic-usage}
이 Fetcher를 가져오는 기본 방법은 다른 Fetcher와 같습니다.

```python
from scrapling.fetchers import StealthyFetcher
```
파서 설정 방법은 [여기](choosing.md#parser-configuration-in-all-fetchers)를 참고하세요.

이제 주요 인수를 예제와 함께 하나씩 살펴보겠습니다. 전체 인수를 빠르게 확인하려면 [표로 바로 이동](#full-list-of-arguments)하세요.

!!! abstract "요약"

    `fetch`의 비동기 버전은 `async_fetch`입니다.


현재 이 Fetcher에는 세 가지 주요 실행 방법이 있으며 필요에 따라 함께 사용할 수 있습니다.

다음 방법을 제공합니다.

### 1. 함께 제공되는 Chromium {#1-bundled-chromium}
```python
StealthyFetcher.fetch('https://example.com')
```
기본 스텔스 설정으로 함께 제공되는 Chromium을 열고 페이지를 로드합니다.

### 2. 설치된 Chrome {#2-real-chrome}
```python
StealthyFetcher.fetch('https://example.com', real_chrome=True)
```
Google Chrome이 설치되어 있다면 이 옵션을 사용할 수 있습니다. 첫 번째 방법과 같지만 Chromium 대신 기기에 설치된 Google Chrome을 사용합니다. 요청이 일반 브라우저의 요청에 더 가까워져 탐지될 가능성이 줄어듭니다.

Google Chrome을 아직 설치하지 않았다면 직접 설치하는 대신 다음 명령으로 라이브러리에서 사용할 Chrome을 설치할 수 있습니다.
```commandline
playwright install chrome
```

### 3. CDP 연결 {#3-cdp-connection}
```python
StealthyFetcher.fetch('https://example.com', cdp_url='ws://localhost:9222')
```
로컬에서 Chromium이나 Google Chrome을 실행하는 대신 [Chrome DevTools Protocol](https://chromedevtools.github.io/devtools-protocol/)로 원격 브라우저에 연결할 수 있습니다.

URL은 브라우저 서비스가 제공하는 WebSocket 주소(`ws://`/`wss://`)나 브라우저의 HTTP 주소(예: `http://localhost:9222`)일 수 있습니다.


## 어떤 기능이 있나요? {#what-does-it-do}

StealthyFetcher는 다음과 같은 봇 차단 우회 기능을 제공합니다.

1. `solve_cloudflare=True`로 모든 종류의 Cloudflare Turnstile/Interstitial 검사를 자동으로 통과합니다.
2. CDP 런타임과 WebRTC를 통한 정보 유출을 막습니다.
3. JavaScript 실행을 격리하고 많은 Playwright 지문을 제거하며, 알려진 봇 행동에 따른 탐지를 피합니다.
4. Canvas에 노이즈를 추가해 Canvas를 통한 지문 수집을 막습니다.
5. 창 없는 모드를 탐지하는 알려진 방법에 자동으로 대응합니다. 시간대 불일치를 이용한 탐지를 막는 옵션도 제공합니다.
6. 그 밖에도 보호 기능에 대응하는 여러 옵션이 있습니다.

## 전체 인수 목록 {#full-list-of-arguments}
이 Fetcher와 세션 클래스에는 다양한 옵션이 있습니다. [예제](#examples)를 보기 전에 전체 인수를 살펴보겠습니다.


| 인수 | 설명 | 선택 사항 |
|:---------------------:|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|:--------:|
| url | 대상 URL입니다. | ❌ |
| headless | `True`는 창을 표시하지 않는 모드(**기본값**)로 실행하고, `False`는 창을 표시합니다. | ✔️ |
| disable_resources | 불필요한 리소스 요청을 건너뛰어 속도를 높입니다. 대상 타입은 `font`, `image`, `media`, `beacon`, `object`, `imageset`, `texttrack`, `websocket`, `csp_report`, `stylesheet`입니다. | ✔️ |
| cookies | 다음 요청에 사용할 쿠키를 설정합니다. | ✔️ |
| useragent | 사용할 User-Agent 문자열입니다. **생략하면 Fetcher가 같은 브라우저와 버전의 실제 User-Agent를 생성해 사용합니다.** | ✔️ |
| network_idle | 최소 500밀리초 동안 네트워크 연결이 없을 때까지 기다립니다. | ✔️ |
| load_dom | 기본적으로 켜져 있습니다. 페이지의 모든 JavaScript가 로드되고 실행될 때까지, 즉 `domcontentloaded` 상태가 될 때까지 기다립니다. | ✔️ |
| pierce_shadow | open 모드의 Shadow DOM 내용을 응답 HTML에 포함합니다. 기본값은 `False`입니다. 세션 전체에 설정하거나 요청별로 덮어쓸 수 있습니다. | ✔️ |
| timeout | 페이지의 모든 작업과 대기에 사용하는 제한 시간입니다. 단위는 밀리초이며 기본값은 30,000밀리초(30초)입니다. | ✔️ |
| wait | 모든 처리가 끝난 뒤 페이지를 닫고 `Response`를 반환하기 전에 기다리는 시간입니다. 단위는 밀리초입니다. | ✔️ |
| page_action | 자동화용 함수입니다. `page` 객체를 받고 페이지 이동 후 필요한 작업을 실행합니다. | ✔️ |
| page_setup | `page` 객체를 받고 페이지 이동 전에 실행되는 함수입니다. 페이지 로드 전에 필요한 이벤트 리스너나 라우트를 등록할 때 사용합니다. | ✔️ |
| wait_selector | 지정한 CSS 선택자의 요소가 특정 상태가 될 때까지 기다립니다. | ✔️ |
| init_script | 이 세션의 각 페이지가 생성될 때 실행할 JavaScript 파일의 절대 경로입니다. | ✔️ |
| wait_selector_state | `wait_selector`로 지정한 요소가 이 상태가 될 때까지 기다립니다. _기본 상태는 `attached`입니다._ | ✔️ |
| google_search | 기본적으로 켜져 있습니다. Scrapling이 Google Referer 헤더를 설정합니다. | ✔️ |
| extra_headers | 요청에 추가할 헤더의 딕셔너리입니다. _`google_search`와 함께 사용하면 해당 옵션의 Referer가 여기서 설정한 Referer보다 우선합니다._ | ✔️ |
| proxy | 요청에 사용할 프록시입니다. 문자열 또는 'server', 'username', 'password' 키만 있는 딕셔너리를 받습니다. | ✔️ |
| real_chrome | 기기에 Chrome이 설치되어 있다면 이 옵션을 켜서 해당 브라우저를 실행할 수 있습니다. | ✔️ |
| locale | `en-GB`, `de-DE` 같은 로캘입니다. `navigator.language`, 요청의 `Accept-Language` 헤더, 숫자와 날짜 표시 형식에 영향을 줍니다. 기본값은 시스템 로캘입니다. | ✔️ |
| timezone_id | 브라우저의 시간대를 바꿉니다. 기본값은 시스템 시간대입니다. | ✔️ |
| cdp_url | 새 브라우저를 실행하는 대신 이 CDP URL에 연결해 브라우저를 제어합니다. | ✔️ |
| user_data_dir | 쿠키와 로컬 스토리지 같은 브라우저 세션 데이터를 저장하는 사용자 데이터 디렉터리입니다. 기본적으로 임시 디렉터리를 만듭니다. **세션에서만 사용할 수 있습니다.** | ✔️ |
| extra_flags | 브라우저 시작 시 전달할 추가 플래그 리스트입니다. | ✔️ |
| solve_cloudflare | 켜면 모든 종류의 Cloudflare Turnstile/Interstitial 검사를 통과한 뒤 응답을 반환합니다. 기본값은 `False`입니다. | ✔️ |
| block_webrtc | WebRTC에 프록시 설정을 적용해 로컬 IP 주소 유출을 막습니다. | ✔️ |
| hide_canvas | Canvas 작업에 무작위 노이즈를 추가해 지문 수집을 막습니다. | ✔️ |
| allow_webgl | 기본적으로 켜져 있습니다. 끄면 WebGL과 WebGL 2.0을 모두 사용할 수 없습니다. 많은 WAF가 WebGL 활성화 여부를 확인하므로 끄는 것은 권장하지 않습니다. | ✔️ |
| additional_args | Playwright 컨텍스트에 전달할 추가 설정입니다. Scrapling의 설정보다 우선합니다. | ✔️ |
| selector_config | 최종 `Selector`/`Response` 객체를 만들 때 사용할 파서 설정 딕셔너리입니다. | ✔️ |
| blocked_domains | 요청을 차단할 도메인 이름의 집합입니다. 하위 도메인도 일치합니다. 예를 들어 `"example.com"`은 `"sub.example.com"`도 차단합니다. | ✔️ |
| block_ads | 알려진 광고 및 추적 도메인 약 3,500개에 대한 요청을 차단합니다. `blocked_domains`와 함께 사용할 수 있습니다. | ✔️ |
| dns_over_https | DNS 쿼리를 Cloudflare DNS-over-HTTPS로 보내 프록시 사용 시 DNS 유출을 막습니다. | ✔️ |
| proxy_rotator | 자동 프록시 순환에 사용할 `ProxyRotator` 객체입니다. `proxy`와 함께 사용할 수 없습니다. | ✔️ |
| retries | 실패한 요청의 재시도 횟수입니다. 기본값은 3입니다. | ✔️ |
| retry_delay | 재시도 사이에 기다리는 초 단위 시간입니다. 기본값은 1입니다. | ✔️ |
| record_requests | 완료된 요청과 저장된 응답을 `session.network`에 보관합니다. 세션 전용이며 기본값은 `False`입니다. | ✔️ |
| max_recorded_requests | 세션별로 보관할 요청의 최대 개수입니다. 기본값은 1,000입니다. 저장하는 본문에는 고정된 크기 제한도 있습니다. | ✔️ |
| executable_path | 함께 제공되는 Chromium 대신 사용할 브라우저 실행 파일의 절대 경로입니다. 일반적이지 않은 설치나 자체 브라우저 빌드에 유용합니다. | ✔️ |

세션 클래스에서는 이 인수들을 세션 전체에 설정할 수 있습니다. 탭 단위로 적용할 수 있는 다음 인수는 요청마다 다르게 전달할 수도 있습니다: `google_search`, `timeout`, `wait`, `page_action`, `page_setup`, `extra_headers`, `disable_resources`, `wait_selector`, `wait_selector_state`, `network_idle`, `load_dom`, `pierce_shadow`, `solve_cloudflare`, `blocked_domains`, `proxy`, `selector_config`.

!!! note "참고"

    1. 제 테스트에서 `disable_resources`는 일부 사이트의 요청을 약 25% 빠르게 했습니다. 프록시 사용량도 줄일 수 있습니다. 다만 일부 사이트는 로딩이 끝나지 않을 수 있으니 주의하세요.
    2. `google_search`는 모든 요청에서 기본적으로 켜져 있으며 Referer를 `https://www.google.com/`으로 설정합니다. `extra_headers`와 함께 사용하면 그곳에서 설정한 Referer보다 우선합니다.
    3. User-Agent를 지정하지 않고 창 없는 모드를 켜면 Fetcher가 같은 브라우저 버전의 실제 User-Agent를 생성합니다. User-Agent를 지정하지 않고 창 없는 모드도 켜지 않았다면 브라우저의 기본 User-Agent를 사용합니다. 최신 버전에서는 일반 브라우저와 같은 값입니다.
    4. `init_script`는 브라우저 컨텍스트에 등록되어 페이지 생성 시 실행됩니다. 스텔스 모드는 기본적으로 Patchright의 격리된 실행 컨텍스트를 사용합니다. 스크립트가 `window`에 넣은 전역 값을 `page_action`에서 읽어야 한다면, 해당 함수 안에서 `page.evaluate(..., isolated_context=False)`를 호출하세요.

## 세션 관리 {#session-management}

같은 설정으로 여러 요청을 보낼 동안 브라우저를 열어두려면 `StealthySession`/`AsyncStealthySession`을 사용하세요. 이 클래스들은 `fetch`와 같은 인수를 받으므로 세션 전체를 설정할 수 있습니다.

```python
from scrapling.fetchers import StealthySession


with StealthySession(
    headless=True,
    disable_resources=True,
    real_chrome=True
) as session:

    page1 = session.fetch('https://example1.com')
    page2 = session.fetch('https://example2.com')
    page3 = session.fetch('https://dynamic-site.com')


```

### 비동기 세션 사용법 {#async-session-usage}

```python
import asyncio
from scrapling.fetchers import AsyncStealthySession

async def scrape_multiple_sites():
    async with AsyncStealthySession(
        network_idle=True,
        timeout=30000,
        max_pages=3
    ) as session:

        pages = await asyncio.gather(
            session.fetch('https://spa-app1.com'),
            session.fetch('https://spa-app2.com'),
            session.fetch('https://dynamic-content.com')
        )
        return pages
```

`max_pages`는 재사용할 **브라우저 탭 풀**의 크기를 정합니다. 동시에 열어둘 수 있는 탭의 최대 개수입니다. 요청이 끝나도 탭을 열어두며, 각 요청에서 다음 작업을 합니다.

1. 사용하지 않는 탭이 있으면 재사용합니다. 각 요청은 할당받은 탭에 자체 설정(`timeout`, `extra_headers`, `disable_resources`, `blocked_domains` 등)을 적용하므로 이전 요청의 설정이 남지 않습니다.
2. 빈 탭이 없고 열린 탭 수가 `max_pages`보다 적으면 새 탭을 엽니다.
3. 그렇지 않으면 1초보다 짧은 간격으로 빈 탭이 생겼는지 확인합니다. 60초가 지나도 없으면 `TimeoutError`를 발생시킵니다. 대상 사이트가 응답하지 않을 때 이런 상황이 생길 수 있습니다.

오류가 난 탭은 닫고 교체합니다. `session.close_pages()`로 언제든 모든 탭을 닫을 수도 있습니다. 다음 요청은 새 탭을 엽니다.

이 방식은 같은 브라우저에서 여러 URL을 동시에 가져올 수 있어 리소스를 많이 아끼고 빠르게 동작합니다 :)

탭을 열어두면 가져온 페이지가 다음 요청까지 남습니다. 다음 요청의 `page_setup`은 다른 페이지로 이동하기 전에 기존 페이지에서 실행됩니다. 이를 이용해 여러 요청에 걸친 자동화를 연결할 수 있습니다.

0.3.2부터 0.4.14까지는 탭을 재사용할 때 이전 설정이 남는 문제로 요청마다 탭을 닫았습니다. 0.4.15부터는 재사용할 때마다 설정을 초기화하므로 탭을 열어둡니다.

### 세션 상태 저장과 불러오기 {#save-and-load-session-state}

`save_state(path)`는 쿠키, 로컬 스토리지, IndexedDB를 JSON 파일에 저장합니다. `load_state(path)`는 다른 세션에 복원하거나 현재 세션의 저장 상태를 바꿉니다. 두 메서드는 문자열 또는 `pathlib.Path`를 받고 `None`을 반환합니다. 형식은 Playwright의 스토리지 상태 파일과 호환됩니다.

```python
from scrapling.fetchers import StealthySession

with StealthySession() as session:
    session.fetch('https://example.com')
    session.save_state('state.json')

with StealthySession() as session:
    session.load_state('state.json')
    page = session.fetch('https://example.com')
```

로그인이나 다른 브라우저 작업이 끝난 뒤 저장하세요. 두 메서드는 실행 중인 세션 안에서 진행 중인 모든 요청이 끝난 뒤 호출해야 합니다. 불러오기는 기존 쿠키, 로컬 스토리지, IndexedDB를 바꿉니다. 복원한 로그인 상태를 사용하려면 페이지를 가져오거나 새로고침하세요. 상태를 불러오는 것만으로 기존 탭이 이동하지는 않습니다.

`AsyncStealthySession`에서는 `await`를 사용합니다.

```python
from scrapling.fetchers import AsyncStealthySession

async def restore_session():
    async with AsyncStealthySession() as session:
        await session.load_state('state.json')
        page = await session.fetch('https://example.com')
        await session.save_state('state.json')
        return page
```

이 메서드들은 공유 브라우저 컨텍스트만 저장하고 복원합니다. 요청별 프록시의 임시 컨텍스트에는 영향을 주지 않습니다. `proxy_rotator`를 사용하는 세션에는 공유 컨텍스트가 없으므로 `RuntimeError`가 발생합니다. 고정된 세션 `proxy`는 평소처럼 사용할 수 있습니다.

파일에는 `sessionStorage`, 열린 탭, 브라우저 설정이 포함되지 않습니다. 저장하면 파일을 덮어쓰며, 상위 디렉터리는 미리 있어야 합니다. 파일과 JSON 오류는 호출한 코드에 전달됩니다.

### 세션의 장점 {#session-benefits}

- **브라우저 재사용**: 같은 브라우저를 사용하므로 이후 요청이 훨씬 빠릅니다.
- **쿠키 유지**: 일반 브라우저처럼 쿠키와 세션 상태를 자동으로 관리합니다.
- **일관된 지문**: 모든 요청에서 같은 브라우저 지문을 사용합니다.
- **메모리 효율**: 요청마다 새 브라우저를 실행하는 것보다 리소스를 적게 사용합니다.


## 예제 {#examples}
예제를 보면 더 쉽게 이해할 수 있습니다.

### 리소스 제어 {#resource-control}

```python

page = StealthyFetcher.fetch('https://example.com', disable_resources=True)
```

### Shadow DOM {#shadow-dom}

일부 페이지는 일반 HTML에 포함되지 않는 open 모드의 Shadow Root 안에 내용을 저장합니다. `pierce_shadow`를 켜면 이 내용도 응답에 포함됩니다. 그다음 CSS나 XPath 선택자를 평소처럼 사용하면 됩니다.

```python
from scrapling.fetchers import StealthyFetcher

page = StealthyFetcher.fetch('https://example.com', pierce_shadow=True)
titles = page.css('product-card .title::text').getall()
```

기본값은 `False`입니다. 세션 전체에서 켜고 특정 요청에서만 끌 수도 있습니다.

```python
from scrapling.fetchers import StealthySession

with StealthySession(pierce_shadow=True) as session:
    page = session.fetch('https://example.com')
    plain_page = session.fetch('https://example.com', pierce_shadow=False)
```

같은 옵션을 `async_fetch`와 비동기 세션에서도 사용할 수 있습니다.

open 모드의 Shadow Root만 포함됩니다. closed 모드의 루트와 iframe 문서는 탐색하지 않습니다. 컴포넌트가 페이지보다 늦게 로드되면 `wait_selector`를 사용하세요.

open 모드의 각 루트는 응답에서 `<shadow-root>` 래퍼가 됩니다. 슬롯은 태그와 속성을 유지하며 할당된 노드를 담습니다. 할당된 노드가 없으면 대체 내용을 담습니다. 할당되지 않은 Light DOM 자식은 제외됩니다. 브라우저의 실제 페이지는 바뀌지 않습니다.

```html
<product-card>
  <shadow-root>
    <div class="title">Product name</div>
    <slot name="price"><span class="price">20</span></slot>
  </shadow-root>
</product-card>
```

후손 선택자는 이 요소들을 가로질러 사용할 수 있습니다. 바로 아래 자식을 고르는 선택자에는 래퍼와 슬롯도 포함해야 합니다.

```python
titles = page.css('product-card .title::text').getall()
titles = page.css('product-card > shadow-root > .title::text').getall()
prices = page.css('product-card > shadow-root > slot[name="price"] > .price::text').getall()
```

래퍼와 슬롯은 XPath 경로, `.children`, `response.body`, HTML 내보내기에 나타납니다. Markdown과 텍스트 추출은 태그 없이 내용만 반환합니다. 숨겨진 슬롯의 속성도 남아 있으므로 콘텐츠 정리 작업에서 사용할 수 있습니다.

스냅샷은 내용의 순서를 따르지만 CSS 표시 여부나 레이아웃은 계산하지 않습니다. `<shadow-root>`가 있는 선택자는 실제 브라우저 페이지가 아니라 Scrapling 응답에 적용합니다. 다른 HTML 파서는 특이한 중첩 구조를 다르게 처리할 수 있습니다.

### 도메인 차단 {#domain-blocking}

```python

page = StealthyFetcher.fetch('https://example.com', blocked_domains={"ads.example.com", "tracker.net"})
```

### 네트워크 제어 {#network-control}

```python

page = StealthyFetcher.fetch('https://example.com', network_idle=True)


page = StealthyFetcher.fetch('https://example.com', timeout=30000)


page = StealthyFetcher.fetch('https://example.com', proxy='http://username:password@host:port')
```

### 파일 다운로드 {#downloading-files}

```python
page = StealthyFetcher.fetch('https://raw.githubusercontent.com/D4Vinci/Scrapling/main/docs/assets/main_cover.png')

with open(file='main_cover.png', mode='wb') as f:
    f.write(page.body)
```

`Response` 객체의 `body` 속성은 항상 `bytes`를 반환합니다.

### 페이지 이동 전 설정 {#pre-navigation-setup}
페이지 이동 전에 이벤트 리스너, 라우트, 스크립트를 등록해야 한다면 `page_setup`을 사용하세요. 이 함수는 `page` 객체를 받고 `page.goto()` 호출 전에 실행됩니다.

```python
from patchright.sync_api import Page

def capture_websockets(page: Page):
    page.on("websocket", lambda ws: print(f"WebSocket opened: {ws.url}"))

page = StealthyFetcher.fetch('https://example.com', page_setup=capture_websockets)
```
비동기 버전입니다.
```python
from patchright.async_api import Page

async def capture_websockets(page: Page):
    page.on("websocket", lambda ws: print(f"WebSocket opened: {ws.url}"))

page = await StealthyFetcher.async_fetch('https://example.com', page_setup=capture_websockets)
```

`page_action`과 함께 사용할 수 있습니다. `page_setup`은 이동 전에, `page_action`은 이동 후에 실행됩니다.

### Cloudflare와 스텔스 옵션 {#cloudflare-and-stealth-options}

```python

page = StealthyFetcher.fetch('https://nopecha.com/demo/cloudflare', solve_cloudflare=True)


page = StealthyFetcher.fetch(
    'https://protected-site.com',
    solve_cloudflare=True,
    block_webrtc=True,
    real_chrome=True,
    hide_canvas=True,
    google_search=True,
    proxy='http://username:password@host:port',  # It can also be a dictionary with only the keys 'server', 'username', and 'password'.
)
```

`solve_cloudflare`는 모든 종류의 Cloudflare Turnstile/Interstitial 검사를 자동으로 감지하고 처리합니다.

- JavaScript 검사(managed).
- 확인 상자를 클릭하는 대화형 검사.
- 백그라운드에서 자동으로 처리되는 보이지 않는 검사.

CAPTCHA가 포함된 사용자 지정 페이지도 처리합니다.

!!! notes "**중요한 참고 사항**"

    1. 보호 기능을 자체적으로 구현한 사이트에서는 CAPTCHA 처리 후 실제 콘텐츠가 로드될 때까지 기다리도록 `wait_selector`를 써야 할 수 있습니다. 최대한 여러 사이트에서 작동하도록 만들고 있지만, 매우 특이한 사례도 있습니다.
    2. Cloudflare 처리 기능을 사용한다면 충분한 처리 시간을 확보하도록 제한 시간을 최소 60초로 설정하세요.
    3. 이 기능은 프록시와 다른 스텔스 옵션과 함께 사용할 수 있습니다.

### 브라우저 자동화 {#browser-automation}
여기서 [Playwright의 Page API](https://playwright.dev/python/docs/api/class-page) 지식이 필요합니다. 전달한 함수는 Playwright의 페이지 객체를 받아 필요한 작업을 수행하고, 그 뒤에 Fetcher가 처리를 이어갑니다.

이 함수는 `network_idle`이 켜져 있다면 그 대기를 마친 직후, `wait_selector`를 기다리기 전에 실행됩니다. 자동화 외의 용도로도 쓸 수 있으며 페이지를 원하는 대로 바꿀 수 있습니다.

다음 예에서는 페이지의 [마우스 이벤트](https://playwright.dev/python/docs/api/class-mouse)로 휠을 스크롤하고 마우스를 움직입니다.
```python
from patchright.sync_api import Page

def scroll_page(page: Page):
    page.mouse.wheel(10, 0)
    page.mouse.move(100, 400)
    page.mouse.up()

page = StealthyFetcher.fetch('https://example.com', page_action=scroll_page)
```
비동기 가져오기 메서드를 사용한다면 함수도 비동기로 작성해야 합니다.
```python
from patchright.async_api import Page

async def scroll_page(page: Page):
   await page.mouse.wheel(10, 0)
   await page.mouse.move(100, 400)
   await page.mouse.up()

page = await StealthyFetcher.async_fetch('https://example.com', page_action=scroll_page)
```

### 대기 조건 {#wait-conditions}

```python

page = StealthyFetcher.fetch(
    'https://quotes.toscrape.com/js-delayed/',
    wait_selector='.quote',
    wait_selector_state='visible'
)
```
이 옵션을 켜면 응답을 반환하기 전에 지정한 조건을 기다립니다. `wait_selector`에 CSS 선택자를 전달하면 `wait_selector_state`로 지정한 상태가 될 때까지 기다립니다. 상태를 생략하면 기본값인 `attached`를 사용해 요소가 DOM에 나타날 때까지 기다립니다.

그 후 `load_dom`이 켜져 있다면(기본값), 모든 JavaScript 파일의 로드와 실행이 끝났는지, 즉 `domcontentloaded` 상태인지 다시 확인하고 필요하면 계속 기다립니다. `network_idle`도 켜져 있다면 앞서 설명한 `network_idle` 조건을 다시 기다립니다.

기다릴 수 있는 상태는 다음과 같습니다([출처](https://playwright.dev/python/docs/api/class-page#page-wait-for-selector)).

- `attached`: 요소가 DOM에 있을 때까지 기다립니다.
- `detached`: 요소가 DOM에 없을 때까지 기다립니다.
- `visible`: 요소의 경계 상자가 비어 있지 않고 `visibility:hidden`이 아닐 때까지 기다립니다. 내용이 없거나 `display:none`인 요소는 경계 상자가 비어 있으므로 보이는 것으로 간주하지 않습니다.
- `hidden`: 요소가 DOM에서 제거되거나, 경계 상자가 비거나, `visibility:hidden`이 될 때까지 기다립니다. `'visible'`의 반대입니다.

### 네트워크 기록 {#network-history}

브라우저 세션에서 `record_requests`를 켜면 페이지 로딩, 작업, 여러 탭에 걸친 완료된 요청을 확인할 수 있습니다. 기록은 임시 프록시 컨텍스트를 포함한 세션의 컨텍스트를 다루며 응답을 Scrapling `Response` 객체로 저장합니다. 요청을 다시 보내지 않고 API 호출, HTTP 오류, 리디렉션을 찾을 수 있습니다. 저장된 헤더와 본문은 세션을 닫은 뒤에도 읽을 수 있습니다. 실패했거나 끝나지 않은 요청은 제외하지만, 완료된 HTTP 4xx와 5xx 응답은 포함합니다.

```python
from scrapling.fetchers import StealthySession

with StealthySession(record_requests=True, max_recorded_requests=1000) as session:
    session.fetch('https://example.com', network_idle=True)

for response in session.network.search(resource_type='document', limit=None):
    print(response.meta['network_id'], response.url, response.status)
    if note := response.meta.get('body_note'):
        print(note)
    else:
        print(response.body)
        print(response.css('title::text').get())

session.network.clear()
```

`AsyncStealthySession`에서도 같은 API를 사용합니다. 기록은 기본적으로 꺼져 있습니다. 세션을 만들 때 `record_requests=True`를 설정하고, 필요하면 `max_recorded_requests`도 지정하세요.

- `session.network.search(url_pattern=None, method=None, resource_type=None, status=None, after_id=0, limit=100, include_static=True)`는 저장된 `Response`를 네트워크 ID 순서로 반환합니다. `limit=None`은 보관 중인 일치 결과를 모두 반환합니다. `url_pattern`은 검색할 때 적용하는 정규식입니다. 잘못된 패턴은 그 시점에 오류가 발생합니다. `after_id`는 더 큰 네트워크 ID를 가진 응답을 선택합니다. `include_static=False`는 XHR/fetch 요청과 HTTP 오류만 남깁니다. 모든 리소스 타입과 저장된 리디렉션을 포함하려면 `True`를 사용하세요.
- `session.network.get(request_id)`는 저장된 `Response` 하나를 반환합니다. 더는 보관하지 않으면 `None`을 반환합니다.
- `session.network.clear()`는 기록을 지웁니다. 요청 ID는 계속 증가하며 재사용되지 않습니다.

저장된 각 `Response`에서 `.url`, `.method`, `.status`, `.headers`, `.request_headers`, `.body` 바이트, `.json()`, CSS/XPath 메서드를 바로 사용할 수 있습니다. `.meta`에는 `network_id`, `resource_type`, `request_body`(바이트 또는 `None`)가 있습니다. 전체 헤더를 읽지 못하면 일부만 제공될 수 있습니다. 비동기 세션에서도 로컬 읽기 작업이므로 await를 사용하거나 `.body()`를 호출하지 마세요. 저장된 내용을 파싱할 수 없어도 바이트는 유지하지만, CSS/XPath 메서드는 빈 문서를 사용합니다.

URL로 API 트래픽을 찾으려면 `session.network.search(url_pattern=r'https://api\.example\.com/.*', limit=None)`을 사용하세요. 특정 요청 타입만 필요하면 `resource_type='fetch'` 또는 `resource_type='xhr'`를 추가하세요.

기록 기능은 지원하는 텍스트 `Content-Type`의 응답 본문만 읽고 저장합니다. 대상은 `text/*`, `+json`/`+xml` 타입(SVG 포함), JSON, XML, JavaScript, GraphQL, URL 인코딩된 폼 데이터입니다. 바이너리나 알 수 없는 타입, `Content-Type`이 없는 응답은 메타데이터만 보관하고 본문 바이트는 저장하지 않습니다. 브라우저는 리소스를 평소처럼 로드합니다.

저장된 응답 바이트는 Playwright에서 가져오므로 서버가 보낸 원래 바이트와 다를 수 있습니다. 저장된 바이트가 올바른 UTF-8이면 Playwright처럼 UTF-8로 처리합니다. 그렇지 않으면 응답에 선언된 문자 인코딩을 사용합니다. 응답 헤더는 바꾸지 않습니다.

건너뛰었거나 너무 크거나 읽을 수 없는 본문은 `b''`를 반환하고, 이유를 `response.meta.get('body_note')`에 넣습니다. 텍스트가 아니면 `Non-text body; not saved.`를 사용합니다. 응답 메타데이터와 읽을 수 있는 헤더는 유지합니다. 빈 텍스트를 포함해 저장된 텍스트에는 메모가 없습니다. HEAD 응답과 상태 코드 204, 205, 304는 메모 없이 빈 상태로 남습니다.

기록의 `search`, `get`, `clear`는 비동기 세션에서도 로컬 동기 호출입니다. 응답을 변환하고 저장한 뒤에만 기록이 나타납니다. 브라우저 이벤트는 Playwright가 동작 중일 때 처리되며, 비동기 기록에는 이벤트 루프 실행도 필요합니다. 기록을 읽는 작업은 수집 완료를 기다리지 않습니다.

세션을 닫을 때도 수집 완료를 기다리지 않습니다. 페이지 이동이나 브라우저 컨텍스트 종료 시 아직 수집 중인 응답은 제외될 수 있습니다. 이미 저장된 응답은 종료 후에도 읽을 수 있습니다.

기본적으로 최대 1,000개의 요청을 보관합니다. 저장된 응답 본문은 각각 1 MiB, 전체 20 MiB로 제한됩니다. 보관 한도에 도달하면 오래된 기록을 제거합니다. 본문 크기 제한은 고정값이며 세션 설정이 아닙니다. 이 제한은 저장된 항목과 응답 바이트에만 적용합니다. 브라우저 전체 메모리, 동시 수집, 임시 전체 본문 읽기, 파싱된 HTML, 요청 본문에는 적용하지 않습니다.

#### v5로 이전하기 {#migrating-in-v5}

v5에서는 `capture_xhr`와 `response.captured_xhr`가 제거되었습니다. `record_requests=True`로 브라우저 세션을 직접 만들고 `session.network.search(url_pattern=..., limit=None)`으로 읽으세요. 일회용 Fetcher의 API 기록도 이 방식으로 대체하므로 세션 객체를 유지해야 합니다. 필터는 수집 시점이나 한 번의 가져오기가 아니라 세션 전체의 저장 기록에 적용합니다. 지원하는 텍스트 응답 본문만 저장합니다. `search()`는 기본적으로 최대 100개를 반환합니다. `limit=None`은 기록의 보관 한도를 바꾸지 않고 보관 중인 일치 결과를 모두 반환합니다.

### 브라우저 헤더와 로캘 {#browser-headers-and-locale}

```python
page = StealthyFetcher.fetch(
    'https://example.com',
    google_search=True,
    useragent='Mozilla/5.0...',
    locale='en-US',
)
```

### 전체 예제 {#general-example}
```python
from scrapling.fetchers import StealthyFetcher

def scrape_dynamic_content():

    page = StealthyFetcher.fetch(
        'https://example.com/dynamic',
        network_idle=True,
        wait_selector='.content'
    )


    content = page.css('.content')

    return {
        'title': content.css('h1::text').get(),
        'items': [
            item.text for item in content.css('.item')
        ]
    }
```

### 프록시 순환 {#proxy-rotation}

```python
from scrapling.fetchers import StealthySession, ProxyRotator


rotator = ProxyRotator([
    "http://proxy1:8080",
    "http://proxy2:8080",
    "http://proxy3:8080",
])


with StealthySession(proxy_rotator=rotator, headless=True) as session:
    page1 = session.fetch('https://example1.com')
    page2 = session.fetch('https://example2.com')


    page3 = session.fetch('https://example3.com', proxy='http://specific-proxy:8080')
```

!!! warning "주의"

    모든 브라우저 Fetcher와 세션은 기본적으로 탭 풀을 가진 영구 브라우저 컨텍스트를 사용합니다. 하지만 브라우저는 탭별로 프록시를 설정할 수 없습니다. 따라서 `ProxyRotator`를 사용하면 Fetcher가 프록시마다 별도 컨텍스트를 열고 각각 하나의 탭을 만듭니다. 탭의 작업이 끝나면 탭과 컨텍스트를 모두 닫습니다.

## 언제 사용하나요? {#when-to-use}

다음 경우에는 StealthyFetcher를 사용하세요.

- 봇 차단을 우회해야 할 때.
- 신뢰할 수 있는 브라우저 지문이 필요할 때.
- JavaScript를 완전히 실행해야 할 때.
- 자동 스텔스 기능이 필요할 때.
- 브라우저 자동화가 필요할 때.
- Cloudflare 보호 기능에 대응해야 할 때.
