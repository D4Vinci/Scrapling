---
title: "Scrapling MCP 서버 API 참고 문서"
description: "HTTP와 브라우저로 데이터를 수집하는 MCP 도구, 요청·응답 모델, 세션 작업을 확인하세요."
---

# MCP 서버 API 참고 문서 {#mcp-server-api-reference}

**Scrapling MCP 서버**는 Model Context Protocol(MCP)을 통해 웹 스크래핑과 브라우저 조작을 위한 16개 도구를 제공합니다. AI 챗봇이나 에이전트에 연결하면 대화로 데이터를 수집할 수 있으며, 봇 차단 우회 기능도 사용할 수 있습니다.

다음 명령으로 MCP 서버를 시작합니다:

```bash
scrapling mcp
```

서버 클래스를 직접 가져올 수도 있습니다:

```python
from scrapling.core.ai import ScraplingMCPServer

server = ScraplingMCPServer()
server.serve(http=False, host="127.0.0.1", port=8000)
```

직접 준비한 Chromium 호환 브라우저를 사용하려면 `executable_path`로 실행 파일을 지정하세요:

```python
server = ScraplingMCPServer(executable_path="/path/to/chromium")
```

## 응답 모델 {#response-model}

페이지 가져오기와 HTTP 요청 도구는 아래 형식으로 호출당 하나의 응답을 반환합니다. 세션 관리 도구는 뒤에 나오는 모델을 사용합니다. `browser_screenshot`은 페이지나 요소의 이미지와 현재 URL을 이미지 블록과 텍스트 블록으로 반환합니다. `browser_extract`와 `browser_actions`는 일반 텍스트를 반환합니다. 두 네트워크 도구는 아래 모델에 따른 구조화된 JSON을 반환합니다. `browser_evaluate`는 결과를 JSON으로 만들어 텍스트 블록에 담습니다.

## ::: scrapling.core.ai.server.ResponseModel
    handler: python
    :docstring:

## 네트워크 요청 모델 {#network-request-models}

`browser_network_requests`는 `requests`, `next_cursor`, `has_more`, `dropped_count`가 있는 `NetworkRequestsModel`을 반환합니다. 각 `NetworkRequestInfo`에는 `id`, `url`, `method`, `resource_type`, `status`가 있습니다. 다음 결과를 읽으려면 `next_cursor`를 `after_id`로 전달하세요. `has_more`는 현재 기록에 조건과 일치하는 결과가 더 있는지 나타냅니다.

`browser_network_request`는 `request_id`, `part`, `data`, `note`가 있는 `NetworkRequestModel`을 반환합니다. 요약과 헤더는 객체입니다. 저장된 전체 본문은 JSON 응답이어도 문자열로 반환합니다. `note`는 본문이 없거나 헤더가 일부만 있는 이유를 설명합니다.

## ::: scrapling.core.ai._network_formatting.NetworkRequestInfo
    handler: python
    :docstring:

## ::: scrapling.core.ai.server.NetworkRequestsModel
    handler: python
    :docstring:

## ::: scrapling.core.ai._network_formatting.NetworkRequestModel
    handler: python
    :docstring:

## 세션 모델 {#session-models}

세션 관리에 사용하는 모델 클래스입니다:

## ::: scrapling.core.ai.server.SessionInfo
    handler: python
    :docstring:

## ::: scrapling.core.ai.server.SessionCreatedModel
    handler: python
    :docstring:

## ::: scrapling.core.ai.server.SessionClosedModel
    handler: python
    :docstring:

## MCP 서버 클래스 {#mcp-server-class}

MCP 서버의 주요 클래스는 다음 도구를 제공합니다:

- **`make_request`**: 브라우저를 흉내 낸 HTTP 요청으로 URL 하나를 가져온 뒤 클라이언트를 자동으로 닫습니다. GET, POST, PUT, DELETE를 지원합니다.
- **`browser_fetch_once`**: 스텔스 브라우저로 URL 하나를 가져오고 JavaScript 실행과 Cloudflare 처리를 마친 뒤 브라우저를 닫습니다. 나중에 조작하거나 네트워크 기록을 읽으려면 지속 세션을 사용하세요.

- **`browser_extract`**: 새로고침 없이 현재 페이지나 요소를 AI용 구조 스냅샷, HTML, Markdown, 텍스트로 읽습니다. 폼 입력과 페이지 조작 결과가 유지됩니다. 스냅샷에는 요소의 역할, 이름, 참조, 위치, 크기가 들어 있습니다. 정규식 검색은 일치하는 줄과 주변 내용, 부모 노드를 반환합니다.
- **`browser_actions`**: 마우스 이동, 가리키기, 클릭, 스크롤, 필드 입력, 단축키, 대화 상자 응답, 대기를 한 번의 호출로 이어서 실행합니다. 알림과 확인 창을 수락하거나 닫고 입력 창에 글을 쓸 수 있습니다. 검색어 입력, 제출, 결과 대기, 결과 열기를 각각 호출할 필요가 없습니다.

    이동과 클릭의 대상은 선택자, 스냅샷 참조, 좌표로 지정합니다. 요소가 준비될 때까지 기다린 뒤 화면에 보이도록 스크롤합니다. 여러 단계의 이동, 왼쪽·오른쪽·가운데 클릭, 더블 클릭, 중첩 영역 스크롤을 지원합니다.

    선택자나 스냅샷 참조로 페이지의 필드를 찾습니다. 텍스트 입력, 체크박스 선택과 해제, 라디오 버튼 선택, 기본 드롭다운의 단일·다중 항목 선택을 할 수 있습니다. 드롭다운 항목은 표시된 이름으로 고릅니다. 텍스트를 바꾸거나 지우고, 커서 위치에 이어 쓸 수도 있습니다. 단축키는 현재 포커스에 적용됩니다. 느린 모드는 글자와 작업 사이에 무작위 대기 시간을 넣습니다.

    선택자나 스냅샷 참조로 콘텐츠나 로딩 표시가 지정한 상태가 될 때까지 기다릴 수 있습니다. 페이지 로드 이벤트, 네트워크 활동이 멈출 때까지의 대기, 일정 시간 대기도 지원합니다.

- **`browser_evaluate`**: 현재 페이지에서 JavaScript를 실행해 원하는 데이터를 추출하고, 계산하고, 앱 상태를 읽거나 페이지 내용을 바꿉니다. 비동기 스크립트를 지원하며 결과는 JSON으로 반환합니다.
- **`browser_network_requests`**: 탭, 페이지 이동, 조작 전반에서 완료된 브라우저 요청을 검색합니다. API 호출, HTTP 오류, 저장된 리디렉션을 찾을 수 있습니다. 결과를 줄이기 위해 정적 리소스는 기본으로 숨깁니다. 실패했거나 끝나지 않은 요청은 제외합니다. 페이지 단위로 구조화된 요청 정보를 반환합니다.
- **`browser_network_request`**: 요청을 다시 보내지 않고 저장된 요청의 요약, 헤더, 전송 데이터, 텍스트 응답 본문을 구조화된 JSON으로 읽습니다. 저장된 본문을 포함해 선택한 부분을 전부 반환합니다. HTTP 4xx·5xx 응답을 포함한 저장 기록은 페이지가 바뀌어도 남아 있습니다. 기록은 저장이 끝나야 나타납니다. 기록 읽기나 세션 종료는 저장 완료를 기다리지 않으므로 페이지 이동이나 종료 시 진행 중인 기록이 빠질 수 있습니다. 바이트는 Playwright에서 가져오므로 서버의 원본 바이트와 다를 수 있습니다. 저장된 바이트가 올바른 UTF-8이면 Playwright와 같은 방식으로 디코딩합니다. 그렇지 않으면 응답에 지정된 문자 인코딩을 사용합니다. 지원하는 텍스트 `Content-Type`의 본문만 읽고 저장합니다. 바이너리, 알 수 없는 유형, 유형이 없는 응답은 본문을 읽지 않고 메타데이터와 헤더만 저장합니다. 브라우저의 페이지 로드는 달라지지 않습니다. 기록의 크기는 제한되며, 본문이 텍스트가 아니거나 너무 크거나 읽을 수 없는 경우 선택적 메모로 이유를 설명합니다. 필요한 정보는 MCP 세션을 닫기 전에 읽으세요.
- **`browser_fetch`**: 열린 스텔스 브라우저 세션에서 페이지를 가져와 HTML, Markdown, 텍스트, 구조 스냅샷을 추출합니다. 스냅샷은 페이지 전체나 선택한 요소를 대상으로 하며, 나중에 조작할 수 있도록 요소 참조, 위치, 크기를 포함합니다.

## ::: scrapling.core.ai.server.ScraplingMCPServer
    handler: python
    :docstring:
