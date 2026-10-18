---
title: "Scrapling MCP 서버 설정과 스크래핑 작업"
description: "AI 클라이언트를 Scrapling에 연결해 HTTP와 브라우저로 스크래핑하세요. 세션, 저장한 로그인 상태, 브라우저 동작, 선택 추출, API 기록을 사용할 수 있습니다."
---

# Scrapling MCP 서버 안내 {#scrapling-mcp-server-guide}

<iframe width="560" height="315" src="https://www.youtube.com/embed/NHwWEiTOoPQ" title="YouTube 동영상 플레이어" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>

**Scrapling MCP 서버**는 즐겨 쓰는 AI 챗봇이나 AI 에이전트에 Scrapling의 웹 스크래핑 기능을 제공합니다. Claude나 MCP를 지원하는 인터페이스에서 대화하며 웹사이트를 스크래핑하고, 데이터를 추출하고, 봇 차단을 우회할 수 있습니다.

## 기능 {#features}

Scrapling MCP 서버는 웹 스크래핑과 브라우저 조작을 위한 도구 16개를 제공합니다. 일회성 도구는 URL 하나를 가져온 뒤 사용한 브라우저나 클라이언트를 닫습니다. 세션 도구는 호출 사이에 쿠키와 설정을 유지합니다. 따라서 AI가 같은 탭에서 브라우저 작업을 이어 가고 네트워크 기록을 확인할 수 있습니다.

### 일회성 도구 {#one-shot-tools}

#### 🚀 기본 HTTP 스크래핑 {#basic-http-scraping}
- **`make_request`**: 여러 메서드(GET, POST, PUT, DELETE)로 빠르게 HTTP 요청을 보냅니다. 브라우저 지문 모방, TLS 버전에 맞는 실제 브라우저 헤더 생성, HTTP/3 등을 지원합니다.

#### 🔒 스텔스 브라우저 스크래핑 {#stealth-browser-scraping}
- **`browser_fetch_once`**: 스텔스 브라우저로 JavaScript를 실행하고 동적 페이지를 스크래핑합니다. 지문 위장, Cloudflare Turnstile/Interstitial 우회, 브라우저와 요청 설정을 지원합니다.

### 세션 도구 {#session-tools}

#### 🔌 세션 관리 {#session-management}
- **`browser_open`**: 여러 `browser_fetch` 호출 사이에 계속 열려 있는 스텔스 브라우저 세션을 만듭니다. 매번 새 브라우저를 실행하는 부담을 줄입니다. 브라우저 수준의 설정을 보관하고 `session_id`와 `session_type`만 반환합니다. 실제 적용된 `settings`는 `list_sessions`로 확인하세요. CDP 세션에서는 비어 있습니다.
- **`open_request_session`**: `session_make_request`에서 사용하는 지속 HTTP 세션을 만듭니다. 브라우저는 사용하지 않으며 요청 사이에 쿠키, 연결, 브라우저 지문(`impersonate`)을 유지합니다. `session_id`와 `session_type`만 반환하고 타입은 `static`입니다. 실제 적용된 `settings`는 `list_sessions`로 확인하세요.
- **`close_session`**: 브라우저 또는 HTTP 세션을 닫고 자원을 해제합니다.
- **`list_sessions`**: 활성 세션과 각 세션의 정보 및 `settings`를 나열합니다.

#### 브라우저 상태 {#browser-state}

- **`browser_save_state`**: 쿠키, 로컬 스토리지, IndexedDB를 Playwright 호환 JSON 파일로 저장합니다. 브라우저 세션이 끝난 뒤에도 로그인 상태를 재사용할 수 있습니다. 기존 파일은 덮어씁니다.
- **`browser_load_state`**: 열려 있는 브라우저 세션에 저장한 파일을 복원합니다. 첫 페이지를 불러오기 전에도 사용할 수 있습니다. 현재 저장 상태를 바꾸지만 기존 탭을 닫거나 이동하지는 않습니다. 복원한 로그인 상태를 사용하려면 페이지를 가져오거나 새로고침하세요.

상태 파일은 MCP 서버가 실행되는 컴퓨터에 저장됩니다. `sessionStorage`, 열린 탭, 브라우저 설정은 포함하지 않습니다.

#### 🎯 세션으로 가져오기 {#fetching-through-a-session}
- **`browser_fetch`**: 열려 있는 스텔스 브라우저 세션에서 JavaScript를 실행하고 URL 하나를 스크래핑합니다. 지문 위장과 Cloudflare Turnstile/Interstitial 우회를 지원합니다. 요소 참조, 위치, 크기가 담긴 구조화된 페이지 스냅샷도 만들 수 있습니다. AI가 조작할 대상을 찾고 마우스 동작을 계획하는 데 도움이 됩니다.
- **`session_make_request`**: 여러 메서드(GET, POST, PUT, DELETE)로 빠르게 HTTP 요청을 보냅니다. 브라우저 지문 모방, 이에 맞는 헤더, HTTP/3를 지원합니다. `open_request_session`으로 연 세션에서 쿠키, 연결, 브라우저 지문을 재사용합니다.

#### 📸 스크린샷 {#screenshots}

- **`browser_screenshot`**: 새로고침 없이 현재 페이지나 선택한 요소를 PNG 또는 JPEG로 캡처합니다. 입력한 필드, 열린 메뉴, 차트, 결과 카드를 확인할 수 있습니다. 요소만 캡처하면 관련 없는 주변 내용을 줄일 수 있습니다. 현재 보이는 영역, 전체 페이지, 요소 하나를 지원하며 JPEG 품질도 조절할 수 있습니다. 스크린샷은 모델이 직접 볼 수 있는 실제 이미지 콘텐츠 블록으로 반환됩니다.

#### 현재 페이지 내용 {#current-page-content}

- **`browser_extract`**: 새로고침 없이 현재 페이지나 요소 하나를 AI 스냅샷, HTML, Markdown, 텍스트로 읽습니다. 폼을 입력하거나 내용을 더 불러온 뒤의 결과도 추출할 수 있습니다. 스냅샷에는 이후 동작에 사용할 요소의 역할, 이름, 참조, 위치, 크기가 포함됩니다. 정규식 검색은 일치하는 스냅샷 줄과 주변 문맥, 부모 노드를 반환합니다.

#### 브라우저 동작 {#browser-actions}

- **`browser_actions`**: 한 번의 호출로 마우스 동작, 필드 입력, 키보드 단축키, 대화 상자 응답, 대기를 이어서 실행합니다. 알림이나 확인 창을 수락하거나 닫고, 입력 대화 상자에 텍스트를 넣을 수 있습니다. 예를 들어 검색창 입력, 제출, 결과 대기, 결과 열기를 한 번에 실행할 수 있습니다. AI는 이미 알고 있는 단계를 묶어서 실행하고, 페이지 변화를 확인할 때는 스냅샷을 따로 가져올 수 있습니다. 단계마다 에이전트와 다시 통신할 필요가 없어, 잠깐만 표시되는 메뉴나 빠른 후속 동작이 필요한 다른 조작 대상을 다룰 때 도움이 됩니다.

    마우스를 올려 메뉴나 툴팁을 표시하고, 버튼이나 링크를 클릭하고, 중첩 패널 위로 이동해 세로나 가로로 스크롤할 수 있습니다. 이동과 클릭에는 선택자, 스냅샷 참조, 좌표를 사용합니다. 대상이 요소라면 자동으로 기다린 뒤 화면 안으로 스크롤합니다. 여러 단계의 좌표 이동, 왼쪽·오른쪽·가운데 버튼 클릭, 더블 클릭을 지원합니다.

    선택자나 스냅샷 참조로 페이지 어디에 있는 필드든 지정할 수 있습니다. 텍스트 입력, 체크박스 선택과 해제, 라디오 버튼 선택, 기본 드롭다운에서 보이는 라벨로 하나 이상의 옵션 선택을 지원합니다. 기존 텍스트를 바꾸거나 지우거나 현재 커서 위치에서 이어 쓸 수 있습니다. 키보드 단축키로 텍스트 선택과 삭제, 포커스 이동, 폼 제출, 메뉴 닫기를 할 수 있습니다. 느린 모드는 한 글자씩 입력하며 글자 사이와 모든 동작 사이에 무작위로 잠시 멈춥니다.

    다음 동작 전에 결과가 나타나거나 로딩 오버레이가 사라지거나 페이지 로드 이벤트가 발생할 때까지 기다릴 수 있습니다. 정해진 시간 동안 멈추기와 네트워크 활동이 잦아들 때까지 기다리기도 지원합니다.

#### JavaScript {#javascript}

- **`browser_evaluate`**: 현재 페이지에서 JavaScript를 실행해 사용자 정의 데이터 추출, 계산, 페이지별 작업을 수행합니다. AI가 여러 요소에서 데이터를 모으거나 앱 상태를 읽거나 페이지 내용을 바꿀 수 있습니다. 비동기 스크립트를 지원하고 결과는 JSON으로 반환합니다.

#### 네트워크 기록 {#network-history}

- **`browser_network_requests`**: 탭, 페이지 로드, 브라우저 동작을 거쳐 완료된 요청을 찾습니다. 페이지 데이터의 출처인 API 호출, HTTP 오류, 저장한 리디렉션을 확인할 수 있습니다. 결과를 줄이기 위해 정적 리소스는 기본으로 숨깁니다. 요청 정보를 JSON으로 반환하며 긴 기록은 페이지 단위로 조회할 수 있습니다.
- **`browser_network_request`**: 기록한 요청 하나의 요약, 헤더, 보낸 데이터, 텍스트 응답 본문을 구조화된 JSON으로 확인합니다. 페이지를 불러오거나 요청을 다시 보내지 않고 선택한 부분을 전부 반환합니다. 저장한 응답은 페이지가 바뀐 뒤에도 남습니다. 기록 크기에는 제한이 있으며 텍스트가 아닌 본문, 너무 큰 본문, 읽을 수 없는 본문에는 이유를 표시합니다. 필요한 정보는 MCP 세션을 닫기 전에 읽으세요.

응답 본문은 HTML, JSON, XML, JavaScript 등 지원하는 텍스트 `Content-Type`인 경우에만 읽고 저장합니다. 바이너리, 알 수 없는 타입, 타입이 없는 응답은 본문을 읽거나 저장하지 않고 요청 메타데이터와 헤더만 보관합니다. 브라우저는 리소스를 평소처럼 불러옵니다.

완료된 요청만 저장하며 HTTP 4xx와 5xx 응답도 포함합니다. 실패하거나 아직 끝나지 않은 요청은 제외합니다. 기록이 끝난 뒤 항목이 나타나며, 기록 조회나 세션 종료는 이를 기다리지 않습니다. 페이지 이동이나 종료 시점에 기록 중이던 항목은 빠질 수 있습니다. 저장한 바이트는 브라우저에서 가져오므로 서버가 보낸 바이트와 다를 수 있습니다. 유효한 UTF-8이라면 Playwright와 같이 UTF-8로 읽고, 그렇지 않으면 명시된 문자 인코딩을 사용합니다.

### Shadow DOM {#shadow-dom}

열린 Shadow DOM의 내용을 포함하려면 `browser_fetch_once` 또는 각 `browser_fetch` 호출에 `pierce_shadow=true`를 설정하세요. 기본값은 `false`입니다. 선택자 예제와 제한 사항은 [Shadow DOM](../fetching/stealthy.md#shadow-dom)을 참고하세요.

브라우저 선택자로 닫힌 Shadow DOM 안의 요소를 지정하고 조작할 수도 있습니다.

### 주요 기능 {#key-capabilities}
- **콘텐츠 추출**: 웹페이지나 요소를 Markdown, HTML로 바꾸거나 정리된 텍스트를 추출합니다.
- **CSS 선택자 지원**: AI에 전달하기 전에 Scrapling 엔진으로 필요한 요소를 정확히 고릅니다.
- **봇 차단 우회**: Cloudflare Turnstile, Interstitial 등 여러 보호 방식에 대응합니다.
- **프록시 지원**: 익명성을 높이고 접속 지역을 선택할 수 있습니다.
- **브라우저 모방**: TLS 지문, 해당 버전에 맞는 실제 브라우저 헤더 등을 사용합니다.
- **세션 유지**: 여러 요청에서 브라우저 세션을 재사용해 성능을 높입니다.
- **광고 차단**: 모든 브라우저 도구가 알려진 광고·추적 도메인 약 3,500개로 보내는 요청을 자동으로 차단해 토큰을 줄이고 페이지 로드를 빠르게 합니다.
- **프롬프트 인젝션 방지**: 공격에 쓰일 수 있는 숨겨진 내용을 자동으로 제거합니다. 인라인 스타일로 숨긴 요소, aria-hidden, 숨겨진 슬롯, 너비가 0인 문자, HTML 주석, template 태그가 대상입니다.

## 설치 {#installation}

MCP를 지원하는 Scrapling을 설치하고 브라우저 의존성도 설치되어 있는지 확인하세요.

```bash
# Install Scrapling with MCP server dependencies
pip install "scrapling[ai]"

# Install browser dependencies
scrapling install
```

Docker 레지스트리의 이미지를 바로 사용할 수도 있습니다.
```bash
docker pull pyd4vinci/scrapling
```
GitHub 레지스트리에서도 다운로드할 수 있습니다.
```bash
docker pull ghcr.io/d4vinci/scrapling:latest
```

## MCP 서버 설정 {#setting-up-the-mcp-server}

여기서는 [Claude Desktop](https://claude.ai/download)과 [Claude Code](https://www.anthropic.com/claude-code)에 Scrapling MCP 서버를 추가하는 방법을 설명합니다. MCP를 지원하는 다른 챗봇도 같은 방식으로 설정할 수 있습니다.

!!! note "참고"
    아래의 `scrapling-mcp` 명령은 v0.4.13에서 추가되었습니다. `scrapling mcp`를 바로 실행하는 단축 명령으로, 명령 하나를 요구하는 MCP 레지스트리나 클라이언트에 등록하기 쉽습니다. 이전 버전에서는 `scrapling` 명령의 첫 번째 인수로 `mcp`를 사용하세요.

### Claude Desktop {#claude-desktop}

1. Claude Desktop을 엽니다.
2. 왼쪽 위 메뉴(☰)에서 Settings → Developer → Edit Config를 선택합니다.
3. Scrapling MCP 서버 설정을 추가합니다.
```json
"ScraplingServer": {
  "command": "scrapling-mcp"
}
```
처음 MCP 서버를 추가한다면 파일 전체를 다음 내용으로 설정하세요.
```json
{
  "mcpServers": {
    "ScraplingServer": {
      "command": "scrapling-mcp"
    }
  }
}
```
[공식 안내](https://modelcontextprotocol.io/quickstart/user)에 따르면, 이 작업은 기존 설정 파일을 열거나 파일이 없으면 새로 만듭니다. 파일 위치는 다음과 같습니다.

1. **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
2. **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

확실하게 실행하려면 `scrapling-mcp` 실행 파일의 전체 경로를 사용하세요.

1. **macOS**: `which scrapling-mcp`
2. **Windows**: `where scrapling-mcp`

제 Mac에서는 `/Users/<MyUsername>/.venv/bin/scrapling-mcp`가 반환되어 최종 설정을 다음과 같이 사용했습니다.
```json
{
  "mcpServers": {
    "ScraplingServer": {
      "command": "/Users/<MyUsername>/.venv/bin/scrapling-mcp"
    }
  }
}
```
#### Docker {#docker}
Docker 이미지를 사용한다면 다음과 같이 설정합니다.
```json
{
  "mcpServers": {
    "ScraplingServer": {
      "command": "docker",
      "args": [
        "run", "-i", "--rm", "pyd4vinci/scrapling", "mcp"
      ]
    }
  }
}
```

[Cursor](https://cursor.com/docs/context/mcp), [WindSurf](https://windsurf.com/university/tutorials/configuring-first-mcp-server) 등도 같은 방식으로 설정할 수 있습니다.

### Claude Code {#claude-code}
[Claude Code](https://www.anthropic.com/claude-code)에서는 더 간단합니다.

```bash
claude mcp add ScraplingServer "/Users/<MyUsername>/.venv/bin/scrapling-mcp"
```
Scrapling 실행 파일의 경로를 확인하려면 다음 명령을 사용하세요.

1. **macOS**: `which scrapling-mcp`
2. **Windows**: `where scrapling-mcp`

자세한 내용은 Anthropic의 [Claude Code에 MCP 서버 추가하기](https://docs.anthropic.com/en/docs/claude-code/mcp#option-1%3A-add-a-local-stdio-server)를 참고하세요.


서버를 추가한 뒤 사용 중인 앱을 완전히 종료하고 다시 실행하세요. Claude Desktop에서는 채팅 입력창 오른쪽 아래에 MCP 서버 표시(🔧)가 나타나거나, 입력창의 `Search and tools` 메뉴에 `ScraplingServer`가 표시됩니다.

### 다른 브라우저 실행 파일 사용하기 {#custom-browser-executable}

`browser_fetch_once`와 `browser_open`은 기본 Chromium 대신 다른 Chromium 호환 실행 파일을 사용할 수 있습니다. 사용자 정의 빌드나 가벼운 브라우저 엔진을 쓸 때 유용합니다.

MCP 서버 전체에 설정하려면 서버를 시작할 때 실행 파일 경로를 전달하세요.

```bash
scrapling-mcp --executable-path "/path/to/chromium"
```

Claude Desktop 설정에서는 서버 인수에 옵션을 추가합니다.

```json
{
  "mcpServers": {
    "ScraplingServer": {
      "command": "/Users/<MyUsername>/.venv/bin/scrapling-mcp",
      "args": [
        "--executable-path",
        "/path/to/chromium"
      ]
    }
  }
}
```

서버를 시작하기 전에 `SCRAPLING_EXECUTABLE_PATH` 환경 변수를 설정할 수도 있습니다. 그래도 AI는 `browser_fetch_once`로 한 번 가져올 때나 `browser_open`으로 세션을 열 때 다른 실행 파일을 선택할 수 있습니다.

### 원격 브라우저에 연결하기 {#connecting-to-remote-browsers}

`browser_open`이 반드시 로컬 브라우저를 실행해야 하는 것은 아닙니다. CDP URL을 전달하면 [Chrome DevTools Protocol](https://chromedevtools.github.io/devtools-protocol/)로 이미 실행 중인 브라우저에 연결합니다. 같은 컴퓨터, 다른 호스트, 관리형 브라우저 서비스 모두 가능합니다.
```
Open a stealthy browser session on wss://cdp.provider.example/session/abc123, then use it to scrape the product details from https://shop.example.com. Close the session when you're done.
```
반환된 `session_id`는 평소처럼 `browser_fetch`, `browser_extract`, `browser_actions`, `browser_evaluate`, `browser_screenshot`, `browser_network_requests`, `browser_network_request`, `browser_save_state`, `browser_load_state`에 사용합니다.

URL에는 브라우저 서비스에서 제공하는 WebSocket 주소(`ws://`/`wss://`)나, 원격 디버깅 포트를 켜고 직접 실행한 브라우저의 HTTP 주소를 사용할 수 있습니다.
```commandline
chrome --remote-debugging-port=9222
```
이 브라우저에는 `cdp_url="http://localhost:9222"`로 연결합니다. 브라우저가 다른 컴퓨터에서 실행 중이면 해당 호스트의 주소를 사용하세요.

!!! note "참고:"

    * 브라우저가 이미 실행 중이므로 실행할 때만 쓰는 옵션은 CDP 세션에서 무시됩니다. `headless`, `real_chrome`, `executable_path`가 이에 해당하며, 앞에서 설명한 서버 전체 기본 경로도 포함됩니다.<br/>
    * 각 세션이 원격 브라우저에 별도의 브라우저 컨텍스트를 만들기 때문에 나머지 옵션(`locale`, `useragent`, `proxy`, `cookies`, `timezone_id` 등)은 그대로 적용됩니다.

### Streamable HTTP {#streamable-http}
버전 0.3.6부터 기존 'stdio' 전송 방식 대신 'Streamable HTTP' 전송 방식으로 MCP 서버를 실행할 수 있습니다.

다음 'stdio' 명령 대신:
```bash
scrapling-mcp
```
아래 명령으로 'Streamable HTTP' 전송 방식을 켜세요.
```bash
scrapling-mcp --http
```
서버는 기본적으로 호스트 '127.0.0.1'의 포트 8000에서 연결을 받습니다. 두 값은 다음과 같이 바꿀 수 있습니다.
```bash
scrapling-mcp --http --host '0.0.0.0' --port 8000
```
기본 설정에서는 같은 컴퓨터의 연결만 받습니다. 네트워크에서 서버에 연결할 수 있게 하려면 `--host '0.0.0.0'`을 전달하세요. 이 설정과 아래의 인증 설정은 별개입니다.

Docker 안에서 'Streamable HTTP'를 실행하려면 직접 '0.0.0.0'에 바인딩하고 토큰을 설정해야 합니다. 그렇지 않으면 공개한 포트에서 서버에 연결할 수 없습니다. 컨테이너의 '127.0.0.1'은 컨테이너 안에서만 접근할 수 있기 때문입니다.
```bash
docker run -p 8000:8000 -e SCRAPLING_MCP_AUTH_TOKEN="<your-token>" pyd4vinci/scrapling mcp --http --host '0.0.0.0'
```

### 인증 {#authentication}

'stdio' 전송 방식에서는 서버를 시작한 프로그램만 서버에 연결할 수 있습니다. 하지만 'Streamable HTTP'로 바꾸면 포트에 접근할 수 있는 누구나 모든 도구를 호출할 수 있습니다. 서버가 실행 중인 컴퓨터에서 어떤 URL이든 가져올 수도 있습니다. 이 때문에 'Streamable HTTP'에는 인증이 필요합니다. `--http`만 전달하면 서버가 시작되지 않고 토큰을 요청합니다.
```bash
scrapling-mcp --http --auth-token "$(openssl rand -hex 32)"
```
클라이언트는 `Authorization` 헤더에 토큰을 보내야 합니다. 토큰이 없는 요청은 `401`로 거부됩니다.
```json
{
  "mcpServers": {
    "ScraplingServer": {
      "url": "https://your-server.example.com/mcp",
      "headers": {
        "Authorization": "Bearer <your-token>"
      }
    }
  }
}
```
명령줄에 토큰을 넣으면 셸 기록과 프로세스 목록에 남습니다. 따라서 `SCRAPLING_MCP_AUTH_TOKEN` 환경 변수를 사용하세요.
```bash
export SCRAPLING_MCP_AUTH_TOKEN="<your-token>"
scrapling-mcp --http
```
기본 주소 '127.0.0.1'에서 로컬 테스트를 하는 경우처럼 인증 없는 서버가 필요하다면 `--no-auth`로 명시해야 합니다.
```bash
scrapling-mcp --http --no-auth
```
`--no-auth`와 `--host '0.0.0.0'`을 함께 사용하면 포트에 접근할 수 있는 누구나 모든 도구를 사용할 수 있습니다. 신뢰할 수 있는 네트워크 밖에서는 두 옵션을 함께 사용하지 마세요.

서버가 공용 주소에서 연결을 받는다면 허용할 호스트 이름도 지정하세요. 그러면 DNS 리바인딩 공격을 막는 보호 기능이 켜집니다. 이 공격은 브라우저로 방문한 웹사이트가 여러분의 서버에 연결을 시도하는 방식입니다. 이 옵션은 여러 번 전달할 수 있습니다.
```bash
scrapling-mcp --http --allowed-host 'your-server.example.com:8000'
```

!!! note "참고:"

    * 인증은 'Streamable HTTP' 전송 방식에만 적용됩니다. 'stdio'에서는 무시되며, 서버가 이를 알리는 경고를 기록합니다.<br/>
    * 일반 HTTP는 토큰을 평문으로 전송합니다. 인터넷에 공개하기 전에 TLS 연결을 처리하는 리버스 프록시 뒤에 서버를 두세요.<br/>
    * 클라이언트마다 다른 인증 정보를 쓰는 방식이 아니라 하나의 공유 키를 사용합니다. 모든 클라이언트가 같은 토큰을 쓰며, 토큰을 바꾸려면 서버를 다시 시작해야 합니다.<br/>
    * `--http --no-auth`로 시작하면 인증이 꺼져 있다는 경고가 기록됩니다.<br/>
    * `--auth-token`과 `--no-auth`를 함께 전달하면 토큰을 유지합니다. 인증을 알리지 않고 해제하지 않습니다.

## 예제 {#examples}

MCP 서버를 테스트할 때 사용한 프롬프트를 몇 가지 소개합니다. 여러분은 더 창의적이고 더 좋은 프롬프트를 만들 수 있을 거예요 :)

간단한 프롬프트부터 복잡한 프롬프트까지 차례로 살펴봅니다. 예제에서는 Claude Desktop을 사용하지만 다른 클라이언트에서도 같은 방식으로 쓸 수 있습니다.

1. **기본 웹 스크래핑**

    웹페이지의 주요 내용을 Markdown으로 추출합니다.

    ```
    Scrape the main content from https://example.com and convert it to markdown format.
    ```

    Claude는 `make_request`로 페이지를 가져와 읽기 쉬운 내용을 반환할 수 있습니다. HTTP 요청은 기본적으로 최대 세 번 시도하며, 각 시도 사이에 1초를 기다립니다. 페이지에 JavaScript가 필요하거나 HTTP 요청이 차단되면 AI가 `browser_fetch_once`를 사용할 수 있습니다. 두 도구 모두 호출 후 사용한 리소스를 정리합니다.

    같은 요청을 더 효율적으로 쓰려면 다음과 같이 합니다.
    ```
    Use regular requests to scrape the main content from https://example.com and convert it to markdown format.
    ```
    이렇게 하면 Claude가 사용할 도구를 추측할 필요가 없습니다. 때로는 일반 요청으로 시작하고, 때로는 뚜렷한 이유 없이 브라우저가 더 적합하다고 판단하기도 합니다. 시간과 비용을 줄이고 일관된 결과를 얻으려면 사용할 도구를 Claude에 직접 알려주는 것이 좋습니다.

2. **원하는 데이터만 추출하기**

    CSS 선택자로 특정 요소를 추출합니다.

    ```
    Get all product titles from https://shop.example.com using the CSS selector '.product-title'. If the request fails, retry up to 5 times every 10 seconds.
    ```

    서버는 선택자에 맞는 요소만 추출해 구조화된 목록으로 반환합니다. 웹사이트에 연결 문제가 있을 때를 대비해 최대 5번 시도하도록 지정했습니다. 대부분의 경우에는 기본 설정으로 충분합니다.

3. **쇼핑몰 데이터 수집하기**

    조금 더 복잡한 프롬프트입니다.
    ```
    Open a stealthy browser session and visit these e-commerce URLs one at a time:
    - https://shop1.com/product-a
    - https://shop2.com/product-b  
    - https://shop3.com/product-c
    
    Get the product names, prices, and descriptions from each page. Close the session when done.
    ```

    Claude는 하나의 브라우저 세션을 재사용하고 각 URL에 대해 순서대로 `browser_fetch`를 호출한 뒤 추출한 데이터를 분석할 수 있습니다.

4. **더 복잡한 작업 흐름**

    지금 PlayStation 스토어의 첫 페이지에 있는 모든 액션 게임을 가져오고 싶다면 다음 프롬프트를 사용할 수 있습니다.
    ```
    Extract the URLs of all games on this page, then visit each game in order and return a list of all action games: https://store.playstation.com/en-us/pages/browse
    ```
    일반 요청으로 데이터를 가져올 수 있다면 브라우저를 실행하지 않도록 HTTP 세션을 재사용하라고 AI에 알려주세요.
    ```
    Open an HTTP session, extract the URLs of all games on this page, then fetch each game in order and return a list of all action games. Close the session when done: https://store.playstation.com/en-us/pages/browse
    ```
    CSS 선택자를 쓸 줄 안다면 AI가 읽기 전에 내용의 범위를 좁힐 수도 있습니다.
    ```
    Use an HTTP session to extract the URLs of all games on the page below, then fetch each game in order and return a list of all action games.
    The selector for games in the first page is `[href*="/concept/"]` and the selector for the genre in each game page is `[data-qa="gameInfo#releaseInformation#genre-value"]`.
    Close the session when done.

    URL: https://store.playstation.com/en-us/pages/browse
    ```

5. **Cloudflare로 보호된 웹사이트에서 데이터 가져오기**

    대상 웹사이트에 Cloudflare 보호 기능이 있다고 생각되면 Claude가 직접 알아내도록 두지 말고 미리 알려주세요.
    ```
    What's the price of this product? Be cautious, as it utilizes Cloudflare's Turnstile protection. Make the browser visible while you work.

    https://ao.com/product/oo101uk-ninja-woodfire-outdoor-pizza-oven-brown-99357-685.aspx
    ```

6. **긴 작업 흐름**

    다음과 같은 프롬프트를 사용할 수 있습니다.
    ```
    Extract all product URLs for the following category, then return the prices and details for the first 3 products.
    
    https://www.arnotts.ie/furniture/bedroom/bed-frames/
    ```
    하지만 아래처럼 쓰는 편이 더 좋습니다.
    ```
    Go to the following category URL and extract all product URLs using the CSS selector "a". Then, reuse the session to fetch the first 3 product pages in order and extract each product’s price and details. Close the session when done.
    
    Keep the output in markdown format to reduce irrelevant content.
    
    Category URL:
    https://www.arnotts.ie/furniture/bedroom/bed-frames/
    ```

7. **지속 세션 사용하기**

    같은 사이트에서 여러 페이지를 스크래핑할 때는 지속 브라우저 세션을 사용하세요. 요청마다 새 브라우저를 실행하는 비용을 줄일 수 있습니다.
    ```
    Open a stealthy browser session, then use it to scrape the main details from the first 5 product pages on https://shop.example.com. Close the session when you're done.
    ```
    Claude는 `browser_open`으로 계속 사용할 브라우저를 만들고, 같은 세션에서 각 상품 페이지에 대해 `browser_fetch`를 호출한 뒤 마지막에 `close_session`을 호출합니다. 페이지마다 새 브라우저를 실행하는 것보다 훨씬 빠릅니다.

    !!! danger "위험"

        지속 세션을 사용한 뒤에는 반드시 닫으세요. 닫지 않으면 세션이 계속 열려 있습니다!

8. **긴 작업 흐름에서 지속 세션 사용하기**

    Claude가 여러 단계를 생각해야 하는 긴 테스트 예제입니다.

    ```
    Use Scrapling MCP to do the following in this order:

    1. Open a stealthy browser session with headless mode off.
    2. Go to this page and collect the number of stars: https://github.com/D4Vinci/Scrapling
    3. From the README, get the URL that shows the number of downloads and go to it.
    4. Get the number of downloads and the top 3 countries from the graph.
    5. Prepare a report with the results.
    6. Close the browser.
    ```

이런 식으로 활용할 수 있습니다. 여러분의 아이디어에 따라 더 많은 작업을 할 수 있습니다.

## 권장 사용 방법 {#best-practices}

기술적으로 알아두면 좋은 몇 가지 팁입니다.

### 1. 알맞은 도구 선택하기 {#1-choose-the-right-tool}
- **`make_request`**: 단일 페이지나 API 호출에 쓰는 빠른 HTTP 요청
- **`browser_fetch_once`**: JavaScript가 필요한 단일 동적 페이지나 Cloudflare 등으로 보호된 사이트
- **세션 도구**: 서로 관련된 요청, 브라우저 작업, 스크린샷, 네트워크 기록

### 2. 성능 개선하기 {#2-optimize-performance}
- 세션을 재사용하고 각 URL을 순서대로 가져오세요.
- 필요 없는 리소스는 끄세요.
- 적절한 제한 시간을 설정하세요.
- CSS 선택자로 필요한 내용만 추출하세요.

### 3. 동적 콘텐츠 처리하기 {#3-handle-dynamic-content}
- SPA에는 `network_idle`을 사용하세요.
- 특정 요소를 기다리려면 `wait_selector`를 설정하세요.
- 느리게 로드되는 사이트에서는 제한 시간을 늘리세요.

### 4. 데이터 품질 {#4-data-quality}
- 페이지의 본문을 선택하고 정리하려면 `main_content_only=true`를 사용하세요.
- 용도에 맞는 `extraction_type`을 선택하세요.

### 5. 프롬프트 인젝션 방지 {#5-prompt-injection-protection}
MCP 서버는 `main_content_only`가 켜져 있으면 스크래핑한 내용을 자동으로 정리합니다. 이 옵션은 기본으로 켜져 있습니다. 악성 웹사이트가 AI의 컨텍스트에 지시를 넣는 데 사용할 수 있는 숨겨진 내용을 제거합니다.

- **요소를 숨기는 인라인 스타일**: `display:none`, `visibility:hidden`, 불투명도, 글꼴 크기, 높이, 너비, 최대 높이, 최대 너비의 값이 0인 스타일
- **접근성 도구에서 숨긴 요소**: `aria-hidden="true"`
- **템플릿 태그와 숨겨진 슬롯**: `<template>`, `<slot hidden>` 요소
- **HTML 주석**: `<!-- ... -->`
- **너비가 0인 문자**: 너비가 0인 공백처럼 눈에 보이지 않는 유니코드 문자

이 보호 기능은 HTML, Markdown, 텍스트 추출에 자동으로 적용됩니다. 최대한 보호하려면 기본값인 `main_content_only=true`를 유지하세요.

### 6. 세션 관리하기 {#6-manage-sessions}
- 한 번만 가져올 때는 `make_request`나 `browser_fetch_once`를 사용하세요. 두 도구는 리소스를 직접 정리하며, 다음 호출에 사용할 세션을 남기지 않습니다.
- 여러 페이지를 스크래핑할 때는 `browser_open`으로 지속 브라우저 세션을 만들고, 같은 세션에서 각 페이지에 대해 `browser_fetch`를 호출하세요.
- 일반 HTTP 요청을 여러 번 보낼 때는 `open_request_session`을 사용하고, 요청마다 `session_make_request`를 호출하세요. 브라우저 없이도 호출 사이에 쿠키, 연결, 브라우저 지문(`impersonate`)을 유지합니다.
- 세션은 열 때 지정한 세션 설정을 유지합니다. 브라우저에서는 headless, locale, cookies, 스텔스 옵션 등이 해당하고, 요청 세션에서는 `impersonate`, `proxy`가 해당합니다. timeout, wait_selector, network_idle, solve_cloudflare 같은 요청별 옵션은 `browser_fetch`/`session_make_request`를 호출할 때마다 전달합니다. 기본값은 각 도구의 스키마에 나와 있습니다.
- `browser_fetch`는 열려 있는 스텔스 브라우저 세션에서 Cloudflare 검증을 통과할 수 있습니다.
- 작업이 끝나면 항상 `close_session`으로 세션을 닫아 리소스를 해제하세요.
- `list_sessions`로 아직 활성 상태인 세션과 생성할 때 사용한 `settings`를 확인하세요. 이 정보는 AI 에이전트에 반환되며, CDP 세션에서는 비어 있습니다.
- 세션을 여는 도구에 원하는 `session_id`를 전달하면 기본값인 임의의 16진수 대신 의미 있는 이름(예: `"search"`, `"checkout"`)을 붙일 수 있습니다. 이미 사용 중인 ID를 지정하면 오류가 발생하므로 이름 충돌을 바로 알 수 있습니다.

### 7. 스크린샷 찍기 {#7-capturing-screenshots}

- `browser_screenshot`은 스텔스 브라우저 세션에서 `browser_fetch`로 이미 연 페이지를 캡처합니다. 페이지를 다시 로드하지 않으므로 AI가 입력한 필드, 열린 메뉴 등 작업 결과를 확인할 수 있습니다.
- 이미지는 실제 `ImageContent` 블록으로 반환되므로 모델이 페이지를 직접 볼 수 있습니다.
- 현재 보이는 화면이나 아래쪽의 보이지 않는 내용까지 포함한 전체 페이지를 캡처할 수 있습니다.
- 필드, 차트, 카드, 결과 하나만 캡처해 주변 내용을 줄일 수 있습니다. 요소를 캡처할 때는 대상이 보이도록 스크롤할 수 있습니다.
- 손실 없는 이미지에는 PNG를, 더 작은 전송 크기에는 품질을 조절할 수 있는 JPEG를 선택하세요.
- AI는 캡처 전에 `browser_actions`로 콘텐츠를 기다리거나 필요한 조작을 마칠 수 있습니다.

## 법적 사항과 윤리 {#legal-and-ethical-considerations}

⚠️ **중요한 지침:**

- **robots.txt 확인**: `https://website.com/robots.txt`에서 스크래핑 규칙을 확인하세요.
- **요청 속도 제한 준수**: 너무 많은 요청으로 서버에 부담을 주지 마세요.
- **이용 약관**: 웹사이트의 약관을 읽고 준수하세요.
- **저작권**: 지식재산권을 존중하세요.
- **개인정보**: 개인정보 보호법에 주의하세요.
- **상업적 이용**: 사업 목적으로 이용할 권한이 있는지 확인하세요.

---

*Scrapling 팀이 ❤️를 담아 만들었습니다. 즐겁게 스크래핑하세요!*
