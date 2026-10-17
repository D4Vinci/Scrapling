---
title: "v0.5로 마이그레이션"
description: "Scrapling v0.4.15에서 v0.5로 업그레이드하세요. 브라우저 가져오기 구문, 네트워크 기록, MCP 도구, CLI 명령, 파서 설정, 스파이더 동작을 업데이트합니다."
---

# v0.5로 마이그레이션 {#migrating-to-v05}

이 가이드는 **v0.4.15에서 v0.5로** 옮길 때 확인할 변경 사항을 다룹니다. 삭제된 API, 이름이 바뀐 도구, 크롤링 결과나 저장된 파일에 영향을 줄 수 있는 수정 사항을 설명합니다.

## 빠른 마이그레이션 점검표 {#quick-migration-checklist}

| 사용 중인 기능 | 변경할 내용 |
| --- | --- |
| `DynamicFetcher`, `DynamicSession` 또는 `AsyncDynamicSession` | 대응하는 스텔스 클래스를 사용하세요. |
| `capture_xhr` 또는 `response.captured_xhr` | `record_requests=True`로 설정한 브라우저 세션과 `session.network`를 사용하세요. |
| `keep_cdata` | 파서와 Fetcher 설정에서 삭제하세요. |
| `scrapling extract stealthy-fetch` 또는 셸의 `stealthy_fetch()` | 대신 `fetch`를 사용하세요. |
| MCP 도구 | 도구 이름, 스크린샷 호출, 세션 생성 응답 처리 방식을 업데이트하세요. |
| POST 요청이나 쿼리 매개변수가 있는 요청 뒤의 `response.follow()` | 필요하면 메서드, 쿼리, 본문을 다시 전달하세요. |
| 저장된 크롤링 체크포인트 또는 응답 캐시 | 요청이 변경된 지문 입력값을 사용하면 새 크롤링을 시작하세요. |
| `robots_txt_obey=True` | robots.txt 가져오기 실패를 처리하세요. 이제 실패하면 해당 도메인의 크롤링이 차단됩니다. |

## 브라우저로 가져오기 {#browser-fetching}

### 동적 브라우저 클래스 교체 {#replace-the-dynamic-browser-classes}

Playwright를 직접 사용하는 브라우저 백엔드는 삭제되었습니다. 이제 모든 브라우저 가져오기는 Patchright 기반 스텔스 백엔드를 사용합니다.

| 삭제된 API | 대체 API |
| --- | --- |
| `scrapling.DynamicFetcher` | `scrapling.StealthyFetcher` |
| `scrapling.fetchers.DynamicFetcher` | `scrapling.fetchers.StealthyFetcher` |
| `scrapling.fetchers.chrome.PlayWrightFetcher` | `scrapling.fetchers.StealthyFetcher` |
| `scrapling.fetchers.DynamicSession` | `scrapling.fetchers.StealthySession` |
| `scrapling.fetchers.AsyncDynamicSession` | `scrapling.fetchers.AsyncStealthySession` |

`scrapling.fetchers.chrome` 모듈과 비공개 `_browsers._controllers` 모듈은 삭제되었습니다. 위에 나온 공개 가져오기 경로를 사용하세요.

**이전:**

```python
from scrapling.fetchers import DynamicFetcher

page = DynamicFetcher.fetch("https://example.com", headless=True)
```

**현재:**

```python
from scrapling.fetchers import StealthyFetcher

page = StealthyFetcher.fetch("https://example.com", headless=True)
```

세션에서는 `DynamicSession`을 `StealthySession`으로, 또는 `AsyncDynamicSession`을 `AsyncStealthySession`으로 바꾸세요. 스파이더의 `configure_sessions()` 메서드에도 같은 변경을 적용하세요. `fetch()`와 `async with` 사용 방식은 그대로입니다.

콜백이 브라우저 타입을 가져오거나 브라우저 오류를 처리한다면 `playwright.sync_api`를 `patchright.sync_api`로, 또는 `playwright.async_api`를 `patchright.async_api`로 바꾸세요. 여기에는 `Page`, `Locator`, `Error`, `TimeoutError`가 포함됩니다.

Patchright는 기본적으로 격리된 컨텍스트에서 JavaScript를 실행합니다. 콜백이 페이지 자체의 JavaScript 변수를 읽는다면 `page.evaluate(..., isolated_context=False)`를 사용하세요.

가져오기 이름과 함께 브라우저 동작도 바뀝니다. 브라우저 플래그와 지문 설정을 확인하세요. Cloudflare 해결에는 여전히 `solve_cloudflare=True`가 필요하며, 기본적으로 활성화되지 않습니다. 또한 `extra_flags`는 이제 내장 스텔스 플래그를 교체하지 않고 추가합니다.

현재 옵션은 [브라우저로 가져오기](fetching/stealthy.md)를 참고하세요.

### XHR 캡처를 세션 네트워크 기록으로 교체 {#replace-xhr-capture-with-session-network-history}

`capture_xhr` 매개변수와 `Response.captured_xhr` 속성은 삭제되었습니다. 값이 `None`이어도 매개변수를 삭제하세요. 일회성 가져오기의 응답에는 더 이상 XHR 목록이 붙지 않습니다.

`ResponseFactory.from_playwright_response()` 또는 `ResponseFactory.from_async_playwright_response()`를 호출하는 사용자 정의 통합 코드에서도 `xhr_captured`를 삭제해야 합니다. 위치 인수 순서 변경으로 생기는 문제를 피하려면 `collect_history`를 이름으로 전달하세요.

**이전:**

```python
from scrapling.fetchers import StealthyFetcher

page = StealthyFetcher.fetch("https://example.com", capture_xhr="/api/")
for response in page.captured_xhr:
    print(response.url, response.body)
```

**현재:**

```python
from scrapling.fetchers import StealthySession

with StealthySession(record_requests=True) as session:
    page = session.fetch("https://example.com", network_idle=True)
    for response in session.network.search(url_pattern=r"/api/", limit=None):
        print(response.url, response.body)
```

비동기 코드에서는 `AsyncStealthySession`과 `await session.fetch(...)`를 사용하세요. `session.network`를 읽는 데는 `await`가 필요하지 않습니다.

다음 차이를 확인하세요.

- 세션을 만들 때 `record_requests=True`를 설정하세요. 개별 가져오기 설정이 아니라 세션 설정입니다.
- 기록은 탭, 페이지 로드, 작업을 아우르는 **세션 전체**에 속합니다. 범위를 줄여야 한다면 `after_id`, 필터 또는 `session.network.clear()`를 사용하세요.
- 기록을 검색할 때는 이전 `capture_xhr` 정규식을 `url_pattern`으로 옮기세요.
- `search()`는 저장된 `Response` 객체를 반환합니다. `.url`, `.status`, `.headers`, `.body` 또는 `.json()`을 직접 읽으세요. 기록 ID, 리소스 타입, 전송한 본문은 `response.meta["network_id"]`, `response.meta["resource_type"]`, `response.meta["request_body"]`에 있습니다.
- Python 기록은 기본적으로 모든 리소스 타입을 포함합니다. `resource_type="xhr"` 또는 `resource_type="fetch"`로 하나를 선택하거나, `include_static=False`로 XHR/fetch 요청과 HTTP 오류를 선택하세요.
- `search()`는 기본적으로 최대 100개의 일치 항목을 반환합니다. 보관된 일치 항목을 모두 얻으려면 `limit=None`을 전달하세요. 세션은 기본적으로 최대 1,000개의 요청을 보관하며, `max_recorded_requests`로 변경할 수 있습니다.
- 완료된 요청만 저장합니다. 본문 캡처는 지원되는 텍스트 콘텐츠 타입으로 제한되며, 응답당 1 MiB, 보관된 본문 데이터 전체는 20 MiB가 한도입니다. 한도에 도달하면 오래된 기록이 삭제될 수 있습니다. 본문을 건너뛴 이유는 `response.meta.get("body_note")`로 확인하세요.
- 기록을 읽거나 세션을 닫아도 진행 중인 캡처가 끝날 때까지 기다리지 않습니다. 필요한 데이터가 준비된 뒤에 읽으세요. 저장된 Python 기록은 세션을 닫은 후에도 읽을 수 있습니다.

필터와 한도는 [네트워크 기록](fetching/stealthy.md#network-history)을 참고하세요.

## 파서 설정 {#parser-settings}

### `keep_cdata` 삭제 {#remove-keep_cdata}

`keep_cdata`는 `Selector`, Fetcher 구성, `display_config()`가 반환하는 설정에서 삭제되었습니다. 직접 파서를 호출하는 코드, `Fetcher.configure(...)`, Fetcher나 통합 기능에 전달하는 `selector_config` 딕셔너리에서 삭제하세요.

**이전:**

```python
from scrapling import Selector

page = Selector("<p>Hello</p>", keep_cdata=True)
```

**현재:**

```python
from scrapling import Selector

page = Selector("<p>Hello</p>")
```

대체 설정은 없습니다. 이 설정은 HTML 파서의 출력에 영향을 주지 않았습니다. 파서 옵션을 위치 인수로 전달했다면 기존 `keep_cdata` 인수를 삭제하고 `adaptive`와 저장소 옵션을 이름으로 전달하세요.

## 명령줄과 대화형 셸 {#command-line-and-interactive-shell}

### 브라우저 요청에 `fetch` 사용 {#use-fetch-for-browser-requests}

CLI의 브라우저 명령은 이제 `scrapling extract fetch` 하나입니다. 이 명령은 `StealthyFetcher`를 사용합니다.

**이전:**

```bash
scrapling extract stealthy-fetch "https://example.com" page.md
```

**현재:**

```bash
scrapling extract fetch "https://example.com" page.md
```

이미 `scrapling extract fetch`를 사용한다면 명령 이름은 그대로지만, 백엔드가 `DynamicFetcher`에서 `StealthyFetcher`로 바뀝니다. `--solve-cloudflare` 같은 옵션은 이제 `fetch`에 속합니다.

`scrapling shell`에서는 `stealthy_fetch(...)`를 `fetch(...)`로 바꾸세요. 기존 `fetch(...)` 바로가기는 이제 `StealthyFetcher.fetch`를 호출합니다. 동적 클래스는 더 이상 셸의 이름 공간에 추가되지 않습니다.

### Markdown과 텍스트 파일을 UTF-8로 읽기 {#read-markdown-and-text-files-as-utf-8}

추출 명령과 `Convertor.write_content_to_file()`은 이제 원본 페이지의 문자 집합과 관계없이 `.md`와 `.txt` 파일을 **UTF-8**로 기록합니다. 원본 페이지 인코딩으로 이 파일을 읽는 코드를 업데이트하세요. `.html` 출력은 여전히 `page.encoding`을 사용합니다.

선택한 여러 요소에서 만든 Markdown은 이제 요소 사이에 빈 줄을 넣습니다. 이는 `Response.markdown()`과 Markdown 파일 출력에 적용됩니다. 직접 이어 붙인 텍스트에 의존하던 정확한 출력 비교나 저장된 해시를 업데이트하세요.

## MCP 서버 {#mcp-server}

저장된 프롬프트, 도구 허용 목록, 래퍼, MCP 클라이언트의 도구 정의를 업데이트하세요. 서버를 업데이트한 후에는 MCP 클라이언트를 다시 시작하거나 다시 연결해 현재 도구 목록을 읽게 하세요.

### 도구 이름과 일괄 호출 업데이트 {#update-tool-names-and-bulk-calls}

| v0.4.15 도구 | v0.5 대체 방법 |
| --- | --- |
| `fetch`, `stealthy_fetch` | `browser_fetch_once` |
| `open_session` | `browser_open` |
| `session_fetch` | `browser_fetch` |
| `screenshot` | `browser_screenshot` |
| `bulk_fetch`, `bulk_stealthy_fetch` | URL마다 `browser_fetch_once`를 한 번 호출하거나 열린 세션에서 `browser_fetch`를 반복 호출 |
| `bulk_get` | URL마다 `make_request` 또는 `session_make_request`를 한 번 호출 |

모든 일괄 도구가 삭제되었습니다. 단일 URL 가져오기 도구는 응답 목록 대신 `status`, `content`, `url`이 있는 `ResponseModel` 하나를 반환합니다. `content` 자체는 여전히 문자열 목록입니다.

모든 MCP 브라우저 도구는 이제 스텔스 백엔드를 사용합니다. `browser_open` 호출에서 `session_type`을 삭제하세요. 동적 브라우저는 더 이상 선택할 수 없습니다. 결과에는 `session_type="stealthy"`가 들어 있습니다. HTTP 세션은 여전히 `open_request_session`을 사용하고 `session_type="static"`을 반환합니다.

Python 통합 코드에서도 삭제된 `BrowserSessionType`을 가져오지 않아야 합니다. `SessionType`은 이제 `"stealthy"`와 `"static"`만 허용합니다.

같은 브라우저 세션의 호출은 페이지를 공유하므로 순서대로 실행해야 합니다. 작업을 마치면 `close_session`으로 세션을 닫으세요.

### `list_sessions`로 설정 읽기 {#read-settings-through-list_sessions}

`browser_open`과 `open_request_session`은 이제 다음 항목만 반환합니다.

```json
{
  "session_id": "my-session",
  "session_type": "stealthy"
}
```

생성 결과에는 더 이상 `created_at`, `is_alive`, `settings`, `message`가 포함되지 않습니다. 앞의 세 필드는 `list_sessions`를 호출해 얻으세요. 확인 메시지인 `message`는 삭제되었습니다. `SessionCreatedModel`이 `SessionInfo`의 모든 필드를 가진다고 가정하던 코드도 바꿔야 합니다.

### 스크린샷을 찍기 전에 페이지 가져오기 {#fetch-before-taking-a-screenshot}

`browser_screenshot`은 **현재 페이지를 다시 로드하지 않고 캡처**합니다. URL이나 기존 탐색 및 대기 옵션인 `wait`, `wait_selector`, `wait_selector_state`, `network_idle`은 더 이상 받지 않습니다.

다음 순서로 사용하세요.

1. `browser_open`을 호출합니다.
2. URL과 필요한 페이지 로드 옵션을 넣어 `browser_fetch`를 호출합니다.
3. 필요하면 `browser_actions`를 호출해 페이지와 상호작용하거나 콘텐츠를 기다립니다.
4. 세션 ID를 넣어 `browser_screenshot`을 호출합니다.
5. 작업을 마치면 `close_session`을 호출합니다.

예를 들어 전체 페이지 스크린샷의 인수는 다음과 같습니다.

```json
{
  "session_id": "my-session",
  "full_page": true
}
```

이 도구의 `timeout`은 이제 스크린샷 작업 시간을 제한합니다. 도구는 페이지를 로드하지 않습니다. 요소 스크린샷을 찍으려면 `selector` 또는 `ref`를 사용하고 `full_page=true`는 설정하지 마세요.

스크린샷은 여전히 이미지와 텍스트 콘텐츠 블록을 반환하며, 텍스트 블록에는 현재 페이지 URL이 들어 있습니다. 가져오기용 `ResponseModel`은 반환하지 않습니다.

전체 스키마는 [MCP 가이드](ai/mcp-server.md)와 [API 참조](api-reference/mcp-server.md)를 참고하세요.

## 스파이더와 HTTP 요청 {#spiders-and-http-requests}

### 링크를 따라갈 때 요청 데이터 다시 전달 {#pass-request-data-again-when-following-a-link}

`response.follow()`는 이전 요청에서 `method`, `params`, `data`, `json`, `files`, `multipart`를 더 이상 복사하지 않습니다. 또한 `headers`와 `extra_headers`에서 상속된 `Content-Length` 헤더를 삭제합니다.

요청 데이터를 명시적으로 전달하지 않으면 링크를 따라가는 요청은 이제 일반 GET으로 시작합니다. 세션, 프록시, 콜백 등 다른 공유 설정은 기존 상속 규칙을 따릅니다.

기존 코드가 상속된 POST 데이터에 의존했다면 다음 코드를 바꾸세요.

```python
yield response.follow("/next")
```

변경 후:

```python
yield response.follow("/next", method="POST", json={"page": 2})
```

다음 요청에 `params`가 필요하면 이 값도 명시적으로 전달하세요. 새 `Content-Length`는 HTTP 클라이언트가 계산하게 하세요.

### 요청 지문과 저장된 크롤링 상태 확인 {#check-request-fingerprints-and-saved-crawl-state}

요청 지문은 중복 요청을 찾고 캐시된 응답을 검색하는 데 사용하는 키입니다. 입력값을 처리하는 방식이 다음 세 경우에 달라졌습니다.

- 키를 만들기 전에 `params`가 URL에 합쳐집니다. 같은 URL이라도 쿼리 매개변수가 다르면 기본적으로 중복 요청으로 취급하지 않습니다.
- `{}`, `[]`, `false`, `0`, `""` 같은 JSON 본문은 키에 유지됩니다. 이제 본문이 없는 경우와 같은 키를 쓰지 않습니다. `None`은 여전히 JSON 본문이 없다는 뜻입니다.
- `fp_include_headers=True`일 때 헤더를 추가한 순서만 달라져도 키가 바뀌던 동작이 사라졌습니다.

크롤링이 이 입력값을 사용한다면 업그레이드 전에 마치거나, 새 체크포인트와 새 응답 캐시 디렉터리로 새 크롤링을 시작하세요. 이전에 저장한 키는 새 키와 다를 수 있습니다. 이는 요청 식별 방식의 변경이며 체크포인트 파일 형식의 변경은 아닙니다.

개발 모드는 이제 응답이 차단되었는지 확인한 뒤에만 캐시에 응답을 기록합니다. 차단된 페이지는 성공한 결과로 캐시에 저장되지 않습니다. 기존 캐시 파일은 자동으로 정리되지 않습니다. 이전에 검증 페이지를 캐시했다면 오래된 항목을 지우세요.

실패한 크롤링은 이제 체크포인트 파일을 유지합니다. 오류 후에 이 파일이 사라진다고 가정했다면 정리 코드를 확인하세요. [일시 중지와 재개](spiders/advanced.md#pause-resume) 및 [개발 모드](spiders/advanced.md#development-mode)를 참고하세요.

### robots.txt 가져오기 실패 확인 {#check-robotstxt-failures}

`robots_txt_obey=True`일 때 robots.txt를 가져오다가 예외가 발생하거나 HTTP 200 또는 4xx가 아닌 응답을 받으면 이제 해당 도메인 요청을 차단합니다. 이전에는 이 실패 상황에서도 크롤링을 허용했습니다. HTTP 200은 여전히 규칙을 제공하고 HTTP 4xx는 여전히 접근을 허용합니다.

결과는 크롤링 전체에 걸쳐 캐시됩니다. robots.txt 접근 문제를 해결한 뒤 새 크롤링을 시작하세요. 같은 크롤링의 후속 요청은 실패한 조회를 다시 시도하지 않습니다. 기본값 `robots_txt_obey=False`는 바뀌지 않습니다.

### 링크 제한과 사이트맵 콜백 확인 {#check-link-restrictions-and-sitemap-callbacks}

- `LinkExtractor` 제한 조건에 일치하는 항목이 없으면 이제 링크를 반환하지 않습니다. 전체 페이지로 범위를 넓혀 다시 찾지 않습니다. 크롤링에서 찾는 링크가 줄었다면 `restrict_css` 또는 `restrict_xpath` 표현식을 수정하세요.
- 제한 조건은 이제 부모 요소뿐 아니라 링크 요소 자체도 선택할 수 있습니다. 이전에 놓쳤던 링크가 추가될 수 있으므로 예상 URL 집합을 확인하세요.
- 규칙이 없거나 일치하는 규칙에 `callback=None`이 있으면 `SitemapSpider`는 이제 페이지 URL을 `parse()`로 보냅니다. 해당 HTML 페이지를 사이트맵 파서로 다시 보내지 않습니다. 이 경우를 위한 `parse()`를 구현하고 이전 처리 경로의 문제를 우회하던 코드를 삭제하세요.
- robots.txt와 CSV 피드의 맨 앞에 있는 Unicode 바이트 순서 표시가 제거됩니다. 이제 robots의 첫 지시문이 적용되고 CSV의 첫 열 이름이 `\ufeff`로 시작하지 않습니다. 사용자 정의 `headers`를 설정했다면 대신 첫 필드 값에서 표시가 제거됩니다. 이 숨은 접두사를 처리하던 코드를 업데이트하세요. 사이트맵의 XML 주석과 처리 명령도 파싱 실패를 일으키지 않고 건너뜁니다.

### 폼 데이터, 헤더, CLI JSON 확인 {#check-form-data-headers-and-cli-json}

딕셔너리 형태의 폼 데이터는 이제 리스트와 튜플 값을 반복되는 키로 펼칩니다. 예를 들어 `data={"tag": ["a", "b"]}`는 `tag=a&tag=b`를 보냅니다. 빈 리스트는 해당 키의 항목을 보내지 않습니다. Content-Type을 지정하지 않았다면 기본값 `Content-Type: application/x-www-form-urlencoded`를 추가합니다.

다른 전송 형식이 필요하면 명시적으로 인코딩한 문자열이나 바이트를 전달하세요. `json`, 원시 `content`, multipart 업로드는 각자의 본문 처리 방식을 유지합니다. 폼 데이터나 쿼리 매개변수의 `None` 값은 **제거되지 않습니다**. 문자열 `None`으로 남습니다.

요청별 HTTP 헤더는 이제 대소문자와 관계없이 세션 헤더를 덮어씁니다. 이름이 `authorization`인 요청 헤더는 세션의 `Authorization`과 함께 전송되지 않고 이를 교체합니다. 중복된 헤더 이름을 처리하던 코드를 삭제하세요.

CLI JSON 값 `{}`, `[]`, `false`, `0`, `""`는 이제 알림 없이 버려지지 않고 전송됩니다. 또한 `curl2fetcher()`는 curl의 `-A` 사용자 에이전트를 적용하고 `-x` 프록시를 URL 문자열로 올바르게 전달합니다. 명시적인 curl 헤더 `-H 'User-Agent: ...'`는 여전히 `-A`보다 우선합니다.

## 그 밖에 확인할 출력 변경 {#other-output-changes-to-check}

이 수정 사항은 API를 삭제하지 않지만 저장된 결과와 정확한 출력 비교 테스트를 바꿀 수 있습니다.

- 생성된 CSS 및 XPath 선택자는 같은 태그를 가진 여러 형제 요소 중 첫 요소를 식별해야 할 때 `:nth-of-type(1)` 또는 `[1]`을 포함합니다. 예상 선택자 문자열을 업데이트하고 새 위치 표시를 삭제하지 마세요.
- AI용으로 정리한 콘텐츠는 이제 `opacity:0.95` 같은 값을 가진 표시 요소를 유지합니다. 더 다양한 인라인 스타일로 숨긴 요소와 `<slot hidden>` 요소를 제거하며, 일치하는 불필요한 태그는 중첩되어 있어도 모두 제거합니다. Markdown, 텍스트, 정리된 HTML의 정확한 출력을 다시 확인하세요.
- 브라우저 응답 변환은 이제 대소문자가 다르거나 공백 또는 따옴표로 감싼 값이 있는 charset 선언을 읽습니다. 예를 들어 `text/plain; CHARSET = "iso-8859-15"`입니다. 이 헤더가 있는 HTML이 아닌 응답은 이제 UTF-8로 대체하지 않고 선언된 인코딩을 사용합니다. 해당 응답에서 디코딩한 텍스트를 다시 확인하세요.

## 업그레이드 검증 {#verify-your-upgrade}

전체 작업 전에 작은 크롤링을 실행하세요. 추출된 데이터, 따라간 URL, 전송한 요청 본문, 저장된 파일의 인코딩, 의존하는 캐시나 체크포인트 동작을 확인하세요. MCP 통합에서는 도구 입력과 반환된 데이터를 모두 현재 스키마와 비교하세요.

이전 릴리스의 변경 사항은 [변경 기록](changelog.md)을 참고하세요.
