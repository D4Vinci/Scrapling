---
title: "웹 스크래핑에 HTTP 요청과 브라우저 중 무엇을 쓸까요?"
description: "작업에 맞는 Fetcher 또는 StealthyFetcher를 선택하세요. 직접 HTTP 요청, JavaScript 실행, 세션 재사용이 필요한 경우를 알아봅니다."
---

# Fetcher 기초 {#fetchers-basics}

## 소개 {#introduction}
Fetcher는 한 줄로 요청을 보내거나 페이지를 가져오고 [Response](#response-object) 객체를 반환하는 클래스입니다. 다양한 기능도 제공합니다. v0.3부터 모든 Fetcher에는 세션을 유지하는 별도 클래스가 있습니다. 예를 들어 브라우저 Fetcher는 요청마다 새 브라우저를 여는 대신 모든 요청이 끝날 때까지 같은 브라우저를 열어둘 수 있습니다. 작업에 맞게 선택하면 됩니다.

v0.2 이전의 Scrapling은 파싱만 제공했습니다. 웹 스크래핑에 필요한 모든 기능을 한곳에서 제공하기 위해 이 기능들을 추가했습니다.

> Fetcher는 다른 라이브러리를 단순히 감싼 도구가 아닙니다. 다른 라이브러리를 요청과 페이지 로딩을 위한 엔진으로 사용합니다. 각 Fetcher는 해당 엔진에 없는 기능을 추가하면서 엔진의 기능을 활용하고 웹 스크래핑에 맞게 최적화합니다.

## Fetcher 비교 {#fetchers-overview}

Scrapling은 HTTP용 `Fetcher`와 `AsyncFetcher`, 브라우저용 `StealthyFetcher`, 그리고 반복 요청에 쓰는 세션 클래스를 제공합니다.

다음 표를 보면 작업에 맞는 Fetcher를 빠르게 선택할 수 있습니다.


| 기능 | Fetcher | StealthyFetcher |
|--------------------|---------------------------------------------------|--------------------------------------------------------------------------------------------|
| 상대적인 속도 | 🐇🐇🐇🐇🐇 | 🐇🐇🐇 |
| 탐지 회피 | ⭐⭐ | ⭐⭐⭐⭐⭐ |
| 봇 차단 우회 옵션 | ⭐⭐ | ⭐⭐⭐⭐⭐ |
| JavaScript 로딩 | ❌ | ✅ |
| 메모리 사용량 | ⭐ | ⭐⭐⭐ |
| 적합한 작업 | HTTP 요청만으로 가능한 기본적인 스크래핑 | - 동적으로 로드되는 사이트 <br/>- 간단한 자동화 <br/>- 단순한 보호부터 복잡한 보호까지 우회 |
| 브라우저 | ❌ | Chromium과 Google Chrome |
| 사용하는 브라우저 API | ❌ | Playwright |
| 설정 난이도 | 쉬움 | 쉬움 |

다음 페이지부터 각각 자세히 살펴보겠습니다.

## 모든 Fetcher의 파서 설정 {#parser-configuration-in-all-fetchers}
모든 Fetcher는 다음과 같은 방식으로 가져옵니다.
```python
from scrapling.fetchers import Fetcher, AsyncFetcher, StealthyFetcher
```
객체를 만들지 않고 바로 사용할 수 있으며, 파서의 기본 설정을 사용합니다.
```python
page = StealthyFetcher.fetch('https://example.com') 
```
응답을 반환하기 전에 적용할 파서([Selector 클래스](../parsing/main_classes.md#selector))를 설정하려면 먼저 다음을 실행하세요.
```python
from scrapling.fetchers import Fetcher
Fetcher.configure(adaptive=True, keep_comments=False)  # and the rest
```
또는 다음처럼 작성합니다.
```python
from scrapling.fetchers import Fetcher
Fetcher.adaptive=True
Fetcher.keep_comments=False
```
그런 다음 평소처럼 코드를 이어서 작성하면 됩니다.

설정할 수 있는 인수는 `adaptive`, `adaptive_domain`, `huge_tree`, `keep_comments`, `storage`, `storage_args`입니다. [Selector](../parsing/main_classes.md#selector) 클래스에 전달하는 것과 같습니다. `<fetcher_class>.display_config()`로 현재 설정을 언제든 확인할 수 있습니다.

!!! info "정보"

    `adaptive`는 기본적으로 꺼져 있습니다. 적응형 기능을 사용하려면 켜야 합니다.

### 요청별 파서 설정 {#set-parser-config-per-request}
위의 파서 설정은 해당 클래스를 통해 보내는 모든 요청에 적용됩니다. 공통 설정을 간단히 지정할 때 사용합니다.

요청마다 다른 설정이 필요하면 요청 메서드(`fetch`/`get`/`post`/...)의 `selector_config` 인수에 딕셔너리를 전달하세요.

## Response 객체 {#response-object}
`Response`는 [Selector](../parsing/main_classes.md#selector)를 기반으로 하며, 응답 헤더, 상태, 쿠키 등 추가 정보도 제공합니다.
```python
from scrapling.fetchers import Fetcher
page = Fetcher.get('https://example.com')

page.status          # HTTP status code
page.reason          # Status message
page.cookies         # Response cookies as a dictionary
page.headers         # Response headers
page.request_headers # Request headers
page.history         # Response history of redirections, if any
page.body            # Raw response body as bytes
page.encoding        # Response encoding
page.meta            # Response metadata dictionary (e.g., proxy used). Mainly helpful with the spiders system.
```
모든 Fetcher는 `Response` 객체를 반환합니다. `record_requests=True`로 만든 브라우저 세션에서는 `session.network.search(limit=None)`과 `session.network.get(request_id)`도 저장된 `Response` 객체를 반환합니다. 저장된 API 응답과 v5로의 이전은 [네트워크 기록](stealthy.md#network-history)을 참고하세요.

`Response` 객체는 한 줄로 페이지를 정리된 LLM용 Markdown으로 바꿀 수도 있습니다.
```python
markdown = Fetcher.get('https://example.com').markdown(main_content_only=True)
```
변환 전에 스크립트, 스타일, 숨겨진 내용과 프롬프트 인젝션 내용을 항상 제거합니다. `css_selector`로 특정 요소만 변환할 수도 있습니다. `rag` 추가 패키지가 필요하며 `ai`/`shell`/`all`에도 포함됩니다. 자세한 설명은 [RAG 시스템 만들기](../ai/building-rag-systems.md)를 참고하세요.

!!! note "참고"

    v0.4부터 `Response`의 본문은 [Selector](../parsing/main_classes.md#selector)와 달리 항상 바이트입니다.
