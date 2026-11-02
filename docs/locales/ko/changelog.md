---
title: "Scrapling 변경 기록"
description: "새 기능, 수정 사항, 호환성에 영향을 주는 변경 사항을 담은 Scrapling 릴리스 노트입니다."
---

# 변경 기록 {#changelog}

[GitHub 릴리스](https://github.com/D4Vinci/Scrapling/releases)에서 가져온 Scrapling의 주요 변경 사항을 모두 모았습니다.

## [v0.5](https://github.com/D4Vinci/Scrapling/releases/tag/v0.5) - 2026-10-17 {#v0.5}

**Scrapling v0.5는 가져오기, 파싱, 스파이더, 브라우저 자동화, AI 도구, 10개 언어로 된 문서까지 거의 모든 부분을 개선한 릴리스입니다 🚀**

!!! warning "주의"

    **이 릴리스에는 여기에 모두 담을 수 없을 만큼 호환성에 영향을 주는 변경 사항이 많습니다. 업데이트 전에 [v0.5 마이그레이션 가이드](migrating-to-v0.5.md)를 확인하세요.**

### 🚀 새 기능과 사용 편의 개선 {#v0.5-new-stuff-and-quality-of-life-changes}

- **AI 에이전트를 위한 MCP 서버의 기능이 크게 늘어나 거의 모든 CAPTCHA를 해결할 수 있습니다**([문서](ai/mcp-server.md) 참고):

    - **브라우저 작업을 처음부터 끝까지 실행합니다**. 폼 입력, 클릭, 마우스 올리기, 스크롤, 키보드 사용, 대화 상자 처리, 결과 대기를 지정한 순서대로 실행합니다. 다양한 입력 필드와 느린 동작을 지원하며, 첫 오류가 발생하면 작업을 멈춥니다.
    - **다시 로드하지 않고 현재 페이지를 읽고 검색합니다**. 페이지 전체나 요소 하나에서 HTML, Markdown, 텍스트를 추출합니다. 검색 가능한 페이지 스냅샷은 요소의 역할, 이름, 위치를 표시하며, 특정 부분만 볼 때도 주변 맥락을 유지합니다.
    - **사용자 지정 JavaScript를 실행하고 원하는 부분을 캡처합니다**. 페이지 자체의 JavaScript에 접근해 비동기 작업을 포함한 스크립트를 실행합니다. 개별 요소, 뷰포트, 전체 페이지를 PNG나 JPEG로 캡처할 수 있습니다.
    - **네트워크 활동을 확인하고 로그인 상태를 재사용합니다**. 기록된 요청과 응답을 살펴보고, 브라우저 로그인 상태를 저장하고 복원하며, 열리거나 닫힌 Shadow DOM 내부의 요소를 조작할 수 있습니다. 기록된 통신은 세션을 닫기 전에 읽으세요.
    - **토큰 사용을 줄이고 오류를 더 명확히 전달합니다**. 짧은 도구 설명과 공통 지침으로 반복되는 내용을 줄였습니다. 브라우저나 요청이 실패하면 에이전트에 유용한 오류 메시지를 전달합니다.

- **페이지 뒤에서 일어나는 요청을 볼 수 있습니다**. `record_requests=True`를 켜면 페이지 로드, 동작, 여러 탭에서 완료된 통신을 기록합니다. 요청을 다시 보내지 않고 저장된 응답을 확인할 수 있습니다([문서](fetching/stealthy.md#network-history) 참고).

    ```python
    from scrapling.fetchers import StealthySession

    with StealthySession(record_requests=True) as session:
        session.fetch("https://example.com", network_idle=True)
        for response in session.network.search(url_pattern=r"/api/", limit=None):
            print(response.url, response.status, response.body)
    ```

    - URL, 메서드, 리소스 유형, 상태로 필터링하거나 ID로 응답 하나를 가져올 수 있습니다. 기존 `Response` API로 헤더, 보낸 데이터, API 응답, HTTP 오류, 리디렉션을 확인합니다.
    - 지원되는 텍스트 본문을 크기 제한 안에서 보관합니다. 메타데이터와 본문을 저장할 수 없을 때의 이유도 기록합니다. 기본 한도는 요청 1,000개입니다. 동기 및 비동기 세션을 지원하며, 저장된 Python 기록은 세션을 닫은 뒤에도 읽을 수 있습니다.

- **로그인 상태를 한 번 저장하고 여러 실행에서 재사용합니다**. `save_state(path)`와 `load_state(path)`는 쿠키, 로컬 스토리지, IndexedDB를 Playwright와 호환되는 JSON으로 저장합니다. 동기 및 비동기 브라우저 세션에서 모두 지원합니다([문서](fetching/stealthy.md#save-and-load-session-state) 참고).
    - 페이지를 가져오거나 다시 로드하기 전에 상태를 불러오세요. 시작된 공유 브라우저 컨텍스트가 필요하며 `proxy_rotator`는 사용할 수 없습니다. 탭, 브라우저 설정, `sessionStorage`는 저장하지 않습니다.

- **`pierce_shadow=True`로 열린 Shadow DOM을 추출할 수 있습니다**. 그다음 평소처럼 CSS나 XPath를 사용하세요. 브라우저 Fetcher, 세션, CLI의 `--pierce-shadow` 옵션에서 사용할 수 있습니다. 실제 페이지를 바꾸지 않고 슬롯 내용을 유지합니다. 캡처한 HTML에는 닫힌 Shadow 루트와 iframe 문서가 포함되지 않습니다([문서](fetching/stealthy.md#shadow-dom) 참고).

- **스파이더가 사이트를 탐색하는 순서를 선택할 수 있습니다**. `CrawlSpider`와 `ContentSpider`를 포함한 하위 클래스는 `crawl_strategy="bfs"`로 먼저 들어온 요청부터, `"dfs"`로 나중에 들어온 요청부터 처리하도록 예약할 수 있습니다. 요청의 우선순위가 계속 우선하며, 동시에 처리하는 페이지는 다른 순서로 완료될 수 있습니다([문서](spiders/generic-templates.md#crawl-order) 참고).

### 🐛 버그 수정 {#v0.5-bug-fixes}

- **Cloudflare 검사 처리를 개선했습니다**. 늦게 나타나는 위젯을 감지하고, 불필요한 대기를 줄였으며, 수동 조작이 필요 없는 검사와 숨겨진 프레임의 재시도 횟수에 제한을 두었습니다([#468](https://github.com/D4Vinci/Scrapling/issues/468)과 [#509](https://github.com/D4Vinci/Scrapling/issues/509) 수정).
- **관리자 권한으로 실행한 Windows 셸에서 브라우저가 시작되지 않는 문제를 수정했습니다**([#463](https://github.com/D4Vinci/Scrapling/issues/463) 수정).
- **사용자 지정 브라우저 플래그를 추가할 때도 기본 스텔스 플래그를 유지합니다**. @alkaz-nodemaven의 [#430](https://github.com/D4Vinci/Scrapling/pull/430) 기여입니다.
- **브라우저 응답의 문자 집합 파싱을 개선했습니다**. 대소문자가 다르거나 공백, 따옴표로 감싼 값이 있는 선언도 지원합니다.
- **해결할 Cloudflare 검사가 없을 때, 검사가 없다는 사실을 오류로 기록하지 않습니다**([#459](https://github.com/D4Vinci/Scrapling/issues/459) 수정).

- **요청 지문을 수정했습니다**. 쿼리 매개변수는 @yetval의 [#448](https://github.com/D4Vinci/Scrapling/pull/448), 비어 있거나 거짓으로 평가되는 JSON 본문은 @ac1982의 [#480](https://github.com/D4Vinci/Scrapling/pull/480), 헤더 삽입 순서는 @SarwadnyaMahajan의 [#466](https://github.com/D4Vinci/Scrapling/pull/466) 기여입니다.
- **링크를 따라갈 때 이전 요청의 데이터가 넘어가는 문제를 수정했습니다**. 남아 있던 본문 관련 헤더도 포함합니다. @yetval의 [#462](https://github.com/D4Vinci/Scrapling/pull/462) 기여입니다.
- **차단된 응답이 성공한 응답으로 개발 캐시에 저장되지 않도록 했습니다**. @Kuang-xianxin의 [#446](https://github.com/D4Vinci/Scrapling/pull/446) 기여입니다.
- **예외로 크롤링이 실패하면 체크포인트 파일을 보존합니다**. @SulimanAbdulrazzaq의 [#486](https://github.com/D4Vinci/Scrapling/pull/486) 기여입니다.
- **robots.txt 조회 실패 처리를 수정했습니다**. 조회에 실패한 결과를 크롤링 허용으로 캐시하지 않습니다. @prateekraawat1의 [#443](https://github.com/D4Vinci/Scrapling/pull/443) 기여입니다.
- **범위를 제한하는 선택자를 사용한 링크 추출을 수정했습니다**. 일치하는 요소가 없거나 선택자가 링크 요소 자체를 가리키는 경우도 처리합니다. @SulimanAbdulrazzaq의 [#452](https://github.com/D4Vinci/Scrapling/pull/452)와 [#483](https://github.com/D4Vinci/Scrapling/pull/483) 기여입니다.
- **사이트맵의 콜백 연결을 수정했습니다**. @SulimanAbdulrazzaq의 [#458](https://github.com/D4Vinci/Scrapling/pull/458) 기여입니다. **주석이나 처리 명령이 포함된 XML의 파싱도 수정했습니다**. @sup3dev의 [#450](https://github.com/D4Vinci/Scrapling/pull/450) 기여입니다.
- **robots.txt와 CSV 피드의 시작 부분에 있는 바이트 순서 표시를 처리합니다**. @SulimanAbdulrazzaq의 [#453](https://github.com/D4Vinci/Scrapling/pull/453) 기여입니다.
- **스파이더 HTTP 세션에서 `stealthy_headers`를 처리하는 방식을 수정했습니다**. 옵션을 `curl_cffi`에 직접 전달하지 않고 세션에 전달합니다. @Yigtwxx의 [#475](https://github.com/D4Vinci/Scrapling/pull/475) 기여입니다.

- **딕셔너리 폼에서 리스트와 튜플 값을 인코딩하는 문제를 수정했습니다**. 요청 본문의 우선순위와 기존 `None` 처리는 유지합니다. @SulimanAbdulrazzaq의 [#485](https://github.com/D4Vinci/Scrapling/pull/485) 기여를 포함합니다.
- **세션과 개별 요청의 HTTP 헤더를 대소문자 구분 없이 합치는 처리를 수정했습니다**. @SulimanAbdulrazzaq의 [#487](https://github.com/D4Vinci/Scrapling/pull/487) 기여입니다.
- **CLI 요청에서 비어 있거나 거짓으로 평가되는 JSON 본문을 알림 없이 버리는 문제를 수정했습니다**. @SulimanAbdulrazzaq의 [#484](https://github.com/D4Vinci/Scrapling/pull/484) 기여입니다.
- **Markdown과 텍스트 파일을 내보낼 때 항상 UTF-8을 사용합니다**. 변환 오류로 기존 출력 파일의 내용이 잘리는 문제도 방지했습니다. @SulimanAbdulrazzaq의 [#488](https://github.com/D4Vinci/Scrapling/pull/488) 기여입니다.
- **`curl2fetcher()`에서 curl의 User-Agent 및 프록시 옵션 처리를 수정했습니다**. @SulimanAbdulrazzaq의 [#490](https://github.com/D4Vinci/Scrapling/pull/490) 기여입니다.

- **선택한 여러 요소를 `Response.markdown()`이나 CLI 추출로 변환할 때 Markdown 블록이 붙어 버리는 문제를 수정했습니다**. @Yigtwxx의 [#432](https://github.com/D4Vinci/Scrapling/pull/432) 기여를 포함합니다.
- **AI 출력의 숨겨진 콘텐츠 정리를 수정했습니다**. `opacity:0.95`처럼 보이는 내용은 유지하고, 더 많은 숨김 스타일을 감지하며, 숨겨진 슬롯은 제거합니다. @Yigtwxx의 [#460](https://github.com/D4Vinci/Scrapling/pull/460) 기여를 포함합니다.
- **중첩된 태그 주변에서 불필요한 태그 제거가 일찍 멈추는 문제를 수정했습니다**. @Yigtwxx의 [#474](https://github.com/D4Vinci/Scrapling/pull/474) 기여입니다.
- **같은 태그를 가진 형제 요소가 여러 개일 때 첫 요소에 대해 생성하는 CSS와 XPath 선택자를 수정했습니다**. @yellow-dog-dog의 [#495](https://github.com/D4Vinci/Scrapling/pull/495) 기여입니다.
- **lxml HTML 파서의 지원 중단 예정 경고를 해결했습니다**. @afsuyadi의 [#493](https://github.com/D4Vinci/Scrapling/pull/493) 기여입니다.

### 문서 {#v0.5-docs}

- **웹사이트 전체를 10개 언어로 제공합니다**. 영어, 아랍어, 스페인어, 브라질 포르투갈어, 프랑스어, 독일어, 중국어 간체, 일본어, 러시아어, 한국어를 지원합니다. 가이드, API 참조, 튜토리얼, [변경 기록](changelog.md)을 번역했습니다. 아랍어의 오른쪽에서 왼쪽으로 쓰는 방향을 지원하며, 언어를 바꿔도 현재 페이지와 섹션을 유지합니다.
- **가이드, README 예제, 설정 단계를 더 명확히 했습니다**. 체크포인트 데이터, 브라우저 인코딩, 저장된 상태, 네트워크 기록, Shadow DOM, 크롤링 순서를 다룹니다.
- **Agent Skill과 예제, 참고 자료, 다운로드용 압축 파일을 업데이트했습니다**. 현재 브라우저 및 MCP 도구에 맞췄습니다.
- **변경 기록을 웹사이트로 옮겼습니다**. 각 페이지의 Markdown 원본에도 접근할 수 있습니다.

### 프로젝트 {#v0.5-project}

- Scrapling 로고, 표지 이미지, 웹사이트의 모습을 새롭게 바꿨습니다.
- 브라우저 동작, 대화 상자, 추출, 스크린샷, JavaScript, 네트워크 기록, 상태 파일, Shadow DOM, 크롤러 수정 사항에 대한 테스트를 늘렸습니다.
- 브라우저 테스트 마커를 추가하고 브라우저, 비동기, 병렬 테스트를 나누어 실행합니다. @diegobravtraps-oss의 [#457](https://github.com/D4Vinci/Scrapling/pull/457) 기여로 Windows에서 체크포인트와 CSV 테스트의 호환성을 개선했습니다.
- 다국어 문서의 공통 빌드 설정과 기여 지침을 업데이트했습니다.

## [v0.4.15](https://github.com/D4Vinci/Scrapling/releases/tag/v0.4.15) - 2026-08-23 {#v0.4.15}

**올해 가장 큰 릴리스 중 하나입니다. MCP 서버를 새롭게 구성하고, 한 줄로 RAG용 Markdown을 만들 수 있게 했습니다. Cloudflare 검사 처리도 개선했으며, 자동화를 위해 브라우저 탭을 열린 상태로 유지합니다 🚀**

!!! warning "주의"

    **이 릴리스에는 MCP 서버의 호환성에 영향을 주는 변경 사항이 있습니다. 업데이트 전에 [호환성에 영향을 주는 변경 사항](https://github.com/D4Vinci/Scrapling/blob/v0.4.15/docs/ai/mcp-server.md#breaking-changes)을 확인하세요.**

### 🚀 새 기능과 사용 편의 개선 {#v0.4.15-new-stuff-and-quality-of-life-changes}

- **브라우저 탭을 열린 상태로 유지하고 다음 요청에서도 재사용합니다**([문서](fetching/stealthy.md#session-management) 참고):
    - 모든 브라우저 세션이 요청 후에도 탭을 유지합니다. 다음 요청은 새 탭을 여는 대신 사용 중이 아닌 탭을 재사용합니다.
    - 각 요청은 할당받은 탭에 제한 시간, 헤더, 리소스 차단 등 자신의 설정을 다시 적용합니다. 따라서 다른 요청의 설정이 남지 않습니다.
    - 오류가 난 탭은 닫고 새 탭으로 교체합니다. 새 `close_pages()` 메서드로 열린 탭을 모두 닫을 수 있습니다.
    - 가져온 페이지는 로드된 상태로 유지됩니다. 따라서 다음 요청의 `page_setup` 함수는 다른 페이지로 이동하기 전에 그 페이지에서 실행됩니다. 이를 바탕으로 여러 요청에 걸친 자동화 작업을 연결할 수 있습니다.

- **`Response.markdown()`으로 어떤 페이지든 LLM에서 바로 쓸 수 있는 깔끔한 Markdown으로 바꿀 수 있습니다**([문서](ai/building-rag-systems.md) 참고):

    ```python
    from scrapling.fetchers import Fetcher

    markdown = Fetcher.get("https://example.com").markdown(main_content_only=True)
    ```

    - MCP 서버와 같은 정리 과정을 거쳐, 스크립트와 스타일, 숨겨진 프롬프트 인젝션 내용을 항상 먼저 제거합니다.
    - 필요한 요소만 변환하려면 `css_selector`를 전달하세요.
    - 새 선택 의존성 그룹 `rag`(`pip install "scrapling[rag]"`)로 사용할 수 있습니다. `ai`/`shell`/`all` 그룹에도 포함됩니다.

- **웹사이트 전체를 크롤링해 RAG 파이프라인용 Markdown 문서 모음을 만드는 `SiteToMarkdownSpider` 템플릿을 추가했습니다**([문서](ai/building-rag-systems.md) 참고):

    ```python
    from scrapling.spiders import SiteToMarkdownSpider

    class DocsSpider(SiteToMarkdownSpider):
        name = "docs"
        start_urls = ["https://example.com/docs/"]
        allowed_domains = {"example.com"}
        output_dir = "docs_markdown"

    result = DocsSpider().start()
    result.items.to_jsonl("docs.jsonl")
    ```

    - 페이지마다 `url`/`title`/`markdown`을 가진 항목 하나를 반환합니다. 선택 사항인 `output_dir`을 지정하면 페이지마다 Markdown 파일 하나를 저장합니다.
    - `max_pages`로 크롤링할 페이지 수를 제한합니다. `CrawlSpider`를 기반으로 하므로 `rules()`를 재정의해 어떤 링크를 따라갈지 자유롭게 정할 수 있습니다.

- **MCP 서버를 새롭게 구성했습니다(호환성에 영향을 줍니다)**([호환성에 영향을 주는 변경 사항](https://github.com/D4Vinci/Scrapling/blob/v0.4.15/docs/ai/mcp-server.md#breaking-changes)과 [문서](ai/mcp-server.md) 참고):
    - 도구 13개를 두 모드로 나눴습니다. 일회성 도구(`fetch`, `bulk_fetch`, `stealthy_fetch`, `bulk_stealthy_fetch`)는 항상 자체 브라우저를 실행하고 실제 기본값을 표시합니다. 세션 도구는 한 번 열어 둔 세션을 사용합니다.
    - 새 `session_fetch` 도구는 브라우저 세션으로 페이지를 가져옵니다. `open_session`은 이제 브라우저 수준의 설정만 관리하며, 세션에 실제로 적용된 설정을 AI 에이전트에 반환합니다.
    - `get` 도구의 이름을 `make_request`로 바꿨으며, 모든 HTTP 메서드를 지원합니다.
    - 새 `open_request_session`과 `session_make_request` 도구로 AI가 지속적인 HTTP 세션을 사용할 수 있습니다. 요청 사이에 쿠키와 브라우저 지문을 유지합니다.
    - 이 변경으로 페이지를 가져올 때 세션 설정이 초기화되는 문제도 해결했습니다. 이 문제는 @Yigtwxx가 [#418](https://github.com/D4Vinci/Scrapling/pull/418)에서 처음 수정했습니다.

- **MCP 서버의 HTTP 전송은 기본적으로 인증을 요구하고 localhost에 바인딩합니다(호환성에 영향을 줍니다)**. @yamantaka-singh의 [#414](https://github.com/D4Vinci/Scrapling/pull/414) 기여입니다([#413](https://github.com/D4Vinci/Scrapling/issues/413) 수정, [문서](ai/mcp-server.md#authentication) 참고):
    - Bearer 토큰을 요구하려면 `--auth-token` 또는 환경 변수 `SCRAPLING_MCP_AUTH_TOKEN`을 전달하세요. 의도적으로 인증 없이 서비스하려면 `--no-auth`를 전달하세요.
    - 네트워크에서 들어오는 연결을 허용하려면 `--host 0.0.0.0`을 전달하세요.

### 🐛 버그 수정 {#v0.4.15-bug-fixes}

- **브라우저 로캘과 관계없이 Cloudflare Turnstile/Interstitial 검사를 통과하며, 창 없는 모드에서 상호작용이 필요한 검사를 무한히 반복하지 않습니다**. 스텔스 페이지가 검사 처리 중에 비정상 종료되는 문제도 해결했습니다. @subediparas5의 [#412](https://github.com/D4Vinci/Scrapling/pull/412) 기여를 포함합니다([#411](https://github.com/D4Vinci/Scrapling/issues/411)과 [#422](https://github.com/D4Vinci/Scrapling/issues/422) 수정).
- **`find`/`find_all`에서 `class_`를 사용하면 클래스가 여러 개인 요소를 알림 없이 놓치는 문제를 수정했습니다**. @yetval의 [#410](https://github.com/D4Vinci/Scrapling/pull/410) 기여입니다. **빈 `class_` 값과 이스케이프하지 않은 CSS 문자열 값 문제도 수정했습니다**. @yamantaka-singh의 [#417](https://github.com/D4Vinci/Scrapling/pull/417) 기여입니다.
- **`development_mode`에서 캐시한 응답을 다시 사용할 때 요청 메타데이터가 사라지는 문제를 수정했습니다**. @Yigtwxx의 [#419](https://github.com/D4Vinci/Scrapling/pull/419) 기여입니다.
- **`retries`가 1보다 작은 HTTP 요청이 전송되지도 않고 실패하는 문제를 수정했습니다**. @Yigtwxx의 [#420](https://github.com/D4Vinci/Scrapling/pull/420) 기여입니다.

### 문서 {#v0.4.15-docs}

- **웹사이트의 구성을 정리했습니다**. 새 “AI와 함께 사용하기” 섹션에 MCP 서버, 새 [Agent Skill](ai/agent-skill.md) 페이지, [RAG 시스템 만들기](ai/building-rag-systems.md) 가이드를 모았습니다. BeautifulSoup 마이그레이션 가이드는 “통합과 마이그레이션” 섹션의 Scrapy 통합 옆으로 옮겼습니다.
- **저장소에 [변경 기록](changelog.md)을 추가했습니다**. 지금까지의 모든 릴리스 노트를 포함합니다.

## [v0.4.14](https://github.com/D4Vinci/Scrapling/releases/tag/v0.4.14) - 2026-08-10 {#v0.4.14}

**`uv` 설치 문제를 해결하는 작은 유지 보수 릴리스입니다 🔧**

### 🐛 버그 수정 {#v0.4.14-bug-fixes}

- **`uv`가 기본적으로 v0.4.13 설치를 거부하고 알림 없이 이전 버전으로 돌아가는 문제를 수정했습니다**. 이전 릴리스는 `curl_cffi`의 사전 릴리스 버전을 요구했지만, `uv`는 명시적으로 허용하지 않으면 사전 릴리스 버전을 설치하지 않습니다.
이제 모든 의존성을 안정 버전으로 설치할 수 있습니다([#407](https://github.com/D4Vinci/Scrapling/issues/407) 수정).

## [v0.4.13](https://github.com/D4Vinci/Scrapling/releases/tag/v0.4.13) - 2026-08-09 {#v0.4.13}

**피드 스파이더와 더 똑똑한 MCP 서버를 제공하는 업데이트입니다 🎉**

### 🚀 새 기능과 사용 편의 개선 {#v0.4.13-new-stuff-and-quality-of-life-changes}

- **피드 스파이더 템플릿을 추가했습니다**. `XMLFeedSpider`는 XML 피드(RSS, Atom, 상품 피드 등)의 노드를 순회하고, `CSVFeedSpider`는 CSV 행을 딕셔너리로 순회합니다. 둘 다 gzip으로 압축한 피드를 자동으로 풉니다([문서](spiders/generic-templates.md) 참고).

  ```python
  from scrapling.spiders import XMLFeedSpider

  class RSSSpider(XMLFeedSpider):
      name = "rss"
      start_urls = ["https://example.com/feed.xml"]

      async def parse_node(self, response, node):
          yield {"title": node.findtext("title"), "link": node.findtext("link")}

  result = RSSSpider().start()
  ```

- **MCP 서버를 MCP SDK v2로 업그레이드하고 더 똑똑하게 만들었습니다**. AI 에이전트에 도구를 효율적으로 사용하는 방법을 알려 주는 지침을 포함합니다. 각 도구가 어노테이션을 선언하므로 Claude Code 같은 클라이언트는 읽기 전용 도구를 자동으로 승인할 수 있습니다. 토큰을 아끼도록 도구 설명도 줄였습니다. 서버의 버전과 로고도 MCP 클라이언트에 알립니다([문서](ai/mcp-server.md) 참고).
- **`scrapling-mcp` 명령을 추가했습니다**. `scrapling mcp`에 직접 대응하므로, 단일 명령을 요구하는 MCP 클라이언트와 레지스트리에 한 줄로 Scrapling을 등록할 수 있습니다.
- **Playwright/Patchright와 브라우저의 버전 고정을 해제했습니다**. 생성한 브라우저 User-Agent는 이제 설치된 Playwright/Patchright가 실제로 구동하는 Chromium 버전과 항상 일치합니다. 따라서 Scrapling이 버전을 고정할 필요가 없어 자유롭게 업그레이드할 수 있습니다. 업데이트 후 `scrapling install --force`를 실행해 브라우저를 갱신하세요.

### 🐛 버그 수정 {#v0.4.13-bug-fixes}

- **지문 데이터 패키지가 브라우저 버전보다 뒤처졌을 때 Scrapling을 임포트하면 `browserforge`의 ValueError로 비정상 종료되는 문제를 수정했습니다**([#394](https://github.com/D4Vinci/Scrapling/issues/394), [#396](https://github.com/D4Vinci/Scrapling/issues/396), [#400](https://github.com/D4Vinci/Scrapling/issues/400) 수정).
- **MCP 일괄 브라우저 도구의 페이지 풀 크기가 잘못 설정되는 문제를 수정했습니다**. 이 문제로 `bulk_fetch`는 한 번에 URL 50개를 넘게 처리하면 실패했고, `bulk_stealthy_fetch`는 탭 하나로 모든 URL을 가져왔습니다. @Yigtwxx의 [#393](https://github.com/D4Vinci/Scrapling/pull/393) 기여입니다.

### 프로젝트 {#v0.4.13-project}

- **새 [AI 기여 정책](https://github.com/D4Vinci/Scrapling/blob/main/AI_POLICY.md)을 추가했습니다**. AI를 활용한 기여는 환영하지만 PR이나 이슈에 사용 사실을 밝혀야 합니다. AI 사용 사실을 밝히지 않은 생성물로 보이는 제출물은 라벨을 붙이고 닫습니다.

## [v0.4.12](https://github.com/D4Vinci/Scrapling/releases/tag/v0.4.12) - 2026-07-26 {#v0.4.12}

**스파이더가 크롤링하는 웹사이트에 맞춰 더 똑똑하게 동작하도록 하는 릴리스입니다**

### 🚀 새 기능과 사용 편의 개선 {#v0.4.12-new-stuff-and-quality-of-life-changes}

- **스파이더가 AutoThrottle로 속도를 스스로 조정할 수 있습니다.** 너무 느리거나 차단을 일으킬 수 있는 `download_delay`를 추측할 필요가 없습니다. 스파이더가 각 웹사이트의 응답 속도를 측정해 도메인별 지연을 자동으로 조정합니다. 사이트가 요청을 차단하거나 요청 수를 제한하면, 제한이 없어질 때까지 지연을 두 배로 늘리거나 `Retry-After` 헤더가 지정한 시간만큼 기다립니다. 이후 다시 속도를 높입니다. 설정한 `download_delay`와 robots.txt의 `Crawl-delay`는 계속 최소 대기 시간으로 지킵니다([문서](spiders/advanced.md#autothrottle) 참고).

    ```python
    class MySpider(Spider):
        name = "adaptive"
        start_urls = ["https://example.com"]
        autothrottle_enabled = True
        autothrottle_start_delay = 2.0
        autothrottle_max_delay = 30.0
        autothrottle_block_backoff = True
    ```

- **결과를 CSV와 XML로 내보낼 수 있습니다**. 기존 JSON/JSONL 내보내기도 계속 사용할 수 있습니다. 항목마다 키가 달라도 빠짐없이 내보내며, 중첩된 값은 JSON으로 기록합니다([문서](spiders/getting-started.md) 참고).

    ```python
    result = MySpider().start()
    result.items.to_csv("products.csv")
    result.items.to_xml("products.xml")
    ```

- **MCP 서버에서 인증을 요구할 수 있습니다**. 자신의 컴퓨터에서만 쓰지 않고 안전하게 외부에 공개할 수 있습니다. 토큰이 없는 요청은 거부하며, 서버가 응답할 호스트 이름도 제한할 수 있습니다([문서](ai/mcp-server.md) 참고).

    ```bash
    scrapling mcp --http --auth-token "$(openssl rand -hex 32)"
    ```

- **브라우저가 HTTP 형식의 CDP URL도 받습니다**. WebSocket에만 한정되지 않습니다. 관리형 브라우저 서비스의 `wss://` 주소뿐 아니라, `--remote-debugging-port=9222`로 직접 실행한 Chrome에도 브라우저 Fetcher나 MCP 세션을 연결할 수 있습니다.

- **게시하는 Docker 이미지에 릴리스 버전 태그를 붙입니다**. 이제 `latest`뿐 아니라 원하는 버전을 정확히 고정할 수 있습니다. @JanRK의 [#384](https://github.com/D4Vinci/Scrapling/pull/384) 기여입니다.

### 🐛 버그 수정 {#v0.4.12-bug-fixes}

- **브라우저 엔진의 응답을 캐시하면 쿠키가 모두 사라지는 문제를 수정했습니다**. 스파이더 개발 모드에서 쿠키에 의존하는 세션이나 인증 로직이 알림 없이 동작하지 않게 되는 원인이었습니다. @amitvijapur의 [#379](https://github.com/D4Vinci/Scrapling/pull/379) 기여입니다([#376](https://github.com/D4Vinci/Scrapling/issues/376) 수정).

- **`StealthyFetcher`가 시스템 설정을 따르지 않고 모든 브라우저에 `en-US` 로캘을 강제하는 문제를 수정했습니다**. 사이트가 로캘과 IP 주소의 불일치를 보고 의심스러운 요청으로 판단해, Google에서 429를 반환하는 등의 문제가 생겼습니다([#381](https://github.com/D4Vinci/Scrapling/issues/381) 수정).

- **저장 시스템에서 혼동을 주는 오류 메시지를 수정했습니다**. 데이터 삽입 후 남아 있던 불필요한 호출도 제거했습니다. @fix2015의 [#377](https://github.com/D4Vinci/Scrapling/pull/377) 기여입니다.

### 성능 {#v0.4.12-performance}

- **`get_all_text()`의 실행 시간이 이제 노드 수에 비례합니다(O(nodes))**. 각 텍스트 노드의 조상을 매번 따라가지 않으므로, 깊게 중첩된 페이지에서 약 5-6배 빠르게 동작합니다. @yetval의 [#378](https://github.com/D4Vinci/Scrapling/pull/378) 기여입니다.

## [v0.4.11](https://github.com/D4Vinci/Scrapling/releases/tag/v0.4.11) - 2026-07-12 {#v0.4.11}

**첫 플랫폼별 스파이더 템플릿, 더 빠른 파서, 중요한 수정 사항을 담은 업데이트입니다 🎉**

### 🚀 새 기능과 사용 편의 개선 {#v0.4.11-new-stuff-and-quality-of-life-changes}

- **첫 플랫폼별 스파이더 템플릿 `ShopifySpider`를 추가했습니다!** Shopify 기반 상점의 JSON API로 모든 상품을 추출할 수 있습니다. 사이트의 HTML을 다룰 필요가 없습니다. 이 클래스를 상속하고 상점 도메인만 설정하면 됩니다([문서](spiders/platform-templates.md) 참고).

  ```python
  from scrapling.spiders import ShopifySpider

  class MyStore(ShopifySpider):
      target_website = "example.com"

  result = MyStore().start()
  ```

- **CLI 브라우저 명령에 `--executable-path`를 추가했습니다**. `scrapling extract fetch`와 `scrapling extract stealthy-fetch` 모두 원하는 Chromium 호환 브라우저 실행 파일을 지정할 수 있습니다. 옵션을 전달하지 않으면 환경 변수 `SCRAPLING_EXECUTABLE_PATH`를 사용하므로 MCP 서버와 같은 기능을 제공합니다([#371](https://github.com/D4Vinci/Scrapling/issues/371) 해결).

  ```bash
  scrapling extract fetch "https://example.com" page.html --executable-path "/path/to/chromium"
  ```

### 🤖 사용 편의 개선 {#v0.4.11-quality-of-life-changes}
- **`find_by_text`와 `find_by_regex`가 최대 약 2배 빨라졌습니다**. `first_match`가 켜진 경우(기본값) 요소를 필요할 때만 객체로 감싸므로 첫 일치 항목에서 검색을 멈춥니다. @yetval의 [#370](https://github.com/D4Vinci/Scrapling/pull/370) 기여입니다.
- **모든 라이브러리의 최신 버전과 비교한 새 수치로 벤치마크를 갱신했습니다.**
- **기여 규칙을 갱신했습니다.**

### 🐛 버그 수정 {#v0.4.11-bug-fixes}

- **제어 문자가 있는 페이지에서 MCP 서버의 가져오기 도구가 비정상 종료되는 문제를 수정했습니다**. `All strings must be XML compatible` 오류가 발생하던 문제입니다. @yetval의 [#368](https://github.com/D4Vinci/Scrapling/pull/368) 기여입니다([#366](https://github.com/D4Vinci/Scrapling/issues/366) 수정).

## [v0.4.10](https://github.com/D4Vinci/Scrapling/releases/tag/v0.4.10) - 2026-07-04 {#v0.4.10}

**새 Scrapy 통합 기능과 커뮤니티의 여러 수정 사항을 담은 업데이트입니다 🎉**

### 🚀 새 기능과 사용 편의 개선 {#v0.4.10-new-stuff-and-quality-of-life-changes}

- **Scrapy 통합을 추가했습니다**. 기존 Scrapy 프로젝트를 다시 작성하지 않고 Scrapling의 파싱 API를 사용할 수 있습니다. 스파이더 콜백에 `scrapling_response` 데코레이터를 붙이면 받는 응답이 Scrapling의 `Response`로 바뀝니다. 크롤링은 계속 Scrapy가 처리합니다([문서](integrations/scrapy.md) 참고):

    ```python
    import scrapy
    from scrapling.integrations.scrapy import scrapling_response

    class QuotesSpider(scrapy.Spider):
        name = "quotes"
        start_urls = ["https://quotes.toscrape.com"]

        @scrapling_response
        def parse(self, response):  # `response` is now a Scrapling Response
            first_quote = response.find_by_text("The world as we have created it", partial=True)
            for quote in [first_quote, *first_quote.find_similar()]:
                yield {"text": quote.get_all_text(strip=True)}
    ```

- **MCP 서버의 모든 브라우저 도구에서 원하는 Chromium 호환 브라우저를 사용할 수 있습니다**. `scrapling mcp --executable-path "/path/to/chromium"` 또는 환경 변수 `SCRAPLING_EXECUTABLE_PATH`로 공통 설정을 하거나, `executable_path` 인수로 요청별로 지정할 수 있습니다. @samrusani의 [#360](https://github.com/D4Vinci/Scrapling/pull/360) 기여입니다([#347](https://github.com/D4Vinci/Scrapling/issues/347) 해결).
- **모든 브라우저와 지문을 갱신했습니다**. 업데이트 후 `scrapling install --force`를 실행해 적용하세요.

### 🐛 버그 수정 {#v0.4.10-bug-fixes}

- **UTF-8이 아닌 웹사이트에서 브라우저 Fetcher가 깨진 텍스트(mojibake)를 반환하는 문제를 수정했습니다**. @yehudalevy-collab의 [#365](https://github.com/D4Vinci/Scrapling/pull/365) 기여입니다([#364](https://github.com/D4Vinci/Scrapling/issues/364) 수정).
- **`LinkExtractor`가 `.tar.gz` 같은 복합 확장자를 걸러내지 못하는 문제를 수정했습니다**. @renbkna의 [#359](https://github.com/D4Vinci/Scrapling/pull/359) 기여입니다([#349](https://github.com/D4Vinci/Scrapling/issues/349) 수정).
- **크롤링을 일시 중지할 때 실행 중인 요청이 체크포인트에서 사라지는 문제를 수정했습니다. 이제 재개할 때 해당 요청을 건너뛰지 않습니다**. @yetval의 [#358](https://github.com/D4Vinci/Scrapling/pull/358) 기여입니다.
- **스파이더가 robots.txt의 `Request-rate` 지시에서 잘못된 크롤링 지연을 계산하는 문제를 Protego 업그레이드로 수정했습니다**. @Disaster-Terminator가 [#355](https://github.com/D4Vinci/Scrapling/pull/355)에서 테스트도 이에 맞게 수정했습니다.

### 문서 {#v0.4.10-docs}

- **스텔스 모드에서 `init_script`가 Patchright의 격리된 실행 컨텍스트와 상호작용하는 방식을 명확히 설명했습니다**. @mturac의 [#353](https://github.com/D4Vinci/Scrapling/pull/353) 기여입니다([#350](https://github.com/D4Vinci/Scrapling/issues/350) 해결).
- **에이전트 스킬을 [skills.sh](https://skills.sh/D4Vinci/Scrapling)로 설치하는 방법을 추가했습니다**. @ob-aion의 [#363](https://github.com/D4Vinci/Scrapling/pull/363) 기여입니다.

## [v0.4.9](https://github.com/D4Vinci/Scrapling/releases/tag/v0.4.9) - 2026-06-07 {#v0.4.9}

**커뮤니티에서 보고한 여러 문제를 수정한 유지 보수 업데이트입니다 🛠️**

### 🚀 새 기능과 사용 편의 개선 {#v0.4.9-new-stuff-and-quality-of-life-changes}

- **모든 브라우저와 지문을 갱신했습니다**. 업데이트 후 `scrapling install --force`를 실행해 적용하세요.
- **CLI에 `--version` 플래그를 추가했습니다**. @ETM-Code의 [#303](https://github.com/D4Vinci/Scrapling/pull/303) 기여입니다([#299](https://github.com/D4Vinci/Scrapling/issues/299) 해결).

### 🐛 버그 수정 {#v0.4.9-bug-fixes}

- **HTTP 세션에서 세션 수준의 `proxy` 인수가 알림 없이 무시되는 문제를 수정했습니다**. 실제 IP가 노출될 수 있던 문제입니다([#295](https://github.com/D4Vinci/Scrapling/issues/295) 해결). 이제 세션 수준의 `proxy`와 요청별 `proxies` 인수를 섞어 쓰거나 그 반대로 쓰면, 하나를 알림 없이 버리지 않고 오류를 냅니다.
- **`init_script`와 `user_data_dir`을 함께 쓰면 브라우저의 페이지 이동이 실패하는 문제를 수정했습니다**([#294](https://github.com/D4Vinci/Scrapling/issues/294) 해결).
- **사이트가 `Content-Type` 헤더의 charset 값을 따옴표로 감쌀 때 인코딩을 잘못 감지하는 문제를 수정했습니다**. @Bortlesboat의 [#323](https://github.com/D4Vinci/Scrapling/pull/323) 기여입니다.
- **적응형 요소 재탐색에서 `IndexError`가 발생하는 문제를 수정했습니다. `auto_save`가 켜져 있을 때 발생하던 문제입니다**. @Mubashirrrr의 [#340](https://github.com/D4Vinci/Scrapling/pull/340) 기여입니다.
- **Windows에서 스파이더 체크포인트와 캐시 저장 중 비정상 종료되는 문제를 수정했습니다**. @MrStarkEG의 [#344](https://github.com/D4Vinci/Scrapling/pull/344) 기여입니다.
- **속성 수가 다른 요소에 대해 `find_similar`가 유사도 점수를 잘못 계산하는 문제를 수정했습니다**([#322](https://github.com/D4Vinci/Scrapling/issues/322) 해결).

### 문서 {#v0.4.9-docs}

- **기본 설치에는 파서 엔진만 포함된다는 점을 명확히 했습니다**. Fetcher와 스파이더는 선택 의존성 그룹을 설치해야 합니다([#343](https://github.com/D4Vinci/Scrapling/issues/343) 해결).
- **남아 있던 예제의 Docker 이미지 이름을 수정했습니다**. @evanclan의 [#315](https://github.com/D4Vinci/Scrapling/pull/315) 기여입니다.
- **기여 가이드의 잘못된 링크를 수정했습니다**. @Bortlesboat의 [#320](https://github.com/D4Vinci/Scrapling/pull/320) 기여입니다.

## [v0.4.8](https://github.com/D4Vinci/Scrapling/releases/tag/v0.4.8) - 2026-05-11 {#v0.4.8}

**크롤링 프레임워크를 한 단계 발전시키는 대규모 스파이더 업데이트입니다 🕷️**

### 🚀 새 기능과 사용 편의 개선 {#v0.4.8-new-stuff-and-quality-of-life-changes}

- **`LinkExtractor` 도구를 추가했습니다**. `scrapling.spiders.LinkExtractor`에서 사용하며, `Response`에서 URL을 추출합니다. 다양한 제어 옵션을 제공합니다([문서](spiders/generic-templates.md) 참고).

    ```python
    from scrapling.spiders import LinkExtractor

    extractor = LinkExtractor(allow=r"/posts/", deny_domains=["ads.example.com"])
    ```

- **범용 스파이더 템플릿 `CrawlSpider`와 `CrawlRule`을 추가했습니다**. 이제 “이 패턴과 일치하는 링크 따라가기” 같은 코드를 매번 직접 작성할 필요가 없습니다. `rules()`를 재정의해 `CrawlRule` 객체 목록을 반환하고, 각 객체에 `LinkExtractor`를 연결하세요([문서](spiders/generic-templates.md) 참고).

    ```python
    from scrapling.spiders import CrawlSpider, CrawlRule, LinkExtractor

    class QuotesSpider(CrawlSpider):
        name = "blog"
        start_urls = ["https://quotes.toscrape.com/"]

        def rules(self):
            return [
                CrawlRule(LinkExtractor(allow=r"/author/"), callback=self.parse_author),
                CrawlRule(LinkExtractor(allow=r"/page/\d+/")),  # pagination, no callback
            ]

        async def parse_author(self, response):
            yield {
                "name": response.css(".author-title::text").get(),
                "birthday": response.css(".author-born-date::text").get(),
                "url": response.url,
            }
    ```

- **`SitemapSpider` 템플릿을 추가했습니다**. 사이트맵이나 `robots.txt` URL에서 바로 크롤링을 시작합니다. gzip으로 압축한 사이트맵과 다양한 제어 옵션을 지원합니다. 위의 **CrawlSpider** 예제처럼 크롤링 규칙에 따라 URL을 처리합니다([문서](spiders/generic-templates.md) 참고).

    ```python
    from scrapling.spiders import SitemapSpider, CrawlRule, LinkExtractor

    class NewsSitemap(SitemapSpider):
        name = "news"
        sitemap_urls = ["https://example.com/robots.txt"]

        def rules(self):
            return [
                CrawlRule(LinkExtractor(allow=r"/articles/"), callback=self.parse_article),
            ]

        async def parse_article(self, response):
            yield {"url": response.url, "title": response.css("h1::text").get()}
    ```

- **적응형 요소 재탐색의 기본 유사도 기준을 모든 메서드에서 40%로 바꿨습니다**. 이전 기본값인 `0`보다 적응형 기능이 더 잘 동작하도록 합니다. 기준을 넘는 요소가 없으면 경고에 가장 높은 점수를 표시하므로, 필요할 때 확인하고 `percentage`를 낮출 수 있습니다.

- **모든 브라우저와 지문을 갱신했습니다**. 업데이트 후 `scrapling install  --force`를 다시 실행해 브라우저와 지문을 갱신하세요.

### 🐛 버그 수정 {#v0.4.8-bug-fixes}

- **`Fetcher.configure(...)`가 개별 요청 호출에 적용되지 않는 문제를 수정했습니다**. `AsyncFetcher`에도 같은 수정을 적용했습니다.
- **잘못된 요청 지문 계산으로 스파이더가 중복 요청을 보내는 문제를 수정했습니다**. @yetval의 [#255](https://github.com/D4Vinci/Scrapling/pull/255) 기여입니다.
- **적응형 스크래핑 엔진이 유사도가 낮은 일치 결과를 알리지 않는 문제를 수정했습니다.** 위의 유사도 기준 변경과 함께, 재탐색에 실패하면 오해를 부르는 “가장 그럴듯한” 요소를 반환하는 대신 경고를 표시합니다.

### 문서 {#v0.4.8-docs}

- **문서 전체의 오래된 코드 예제를 갱신했습니다**. 현재 버전에 맞췄습니다.
- **문서 사이트에서 코드를 복사하고 붙여 넣기 쉽게 개선했습니다**. 에이전트 스킬도 정리해 호출할 때마다 쓰는 토큰을 줄였습니다.

## [v0.4.7](https://github.com/D4Vinci/Scrapling/releases/tag/v0.4.7) - 2026-04-17 {#v0.4.7}

**AI 에이전트가 페이지를 볼 수 있게 하는 업데이트입니다 📸**

### 🚀 새 기능과 사용 편의 개선 {#v0.4.7-new-stuff-and-quality-of-life-changes}

- **MCP 도구 `screenshot`을 추가했습니다**. 페이지를 캡처해 실제 MCP `ImageContent` 블록으로 반환하므로 모델이 이미지를 직접 볼 수 있습니다. 열린 브라우저 세션이 필요하므로 먼저 `open_session`을 호출하고(`dynamic` 또는 `stealthy` 사용), 그 `session_id`를 이 도구에 전달하세요. PNG와 JPEG, 전체 페이지 캡처, JPEG 품질 설정, 일반적인 대기 옵션(`wait`, `wait_selector`, `network_idle`, `timeout`)을 지원합니다([#244](https://github.com/D4Vinci/Scrapling/issues/244) 구현).
- **원하는 이름을 지정하는 `session_id` 매개변수를 `open_session`에 추가했습니다**. 기본값인 무작위 12자리 16진수 문자열 대신 의미 있는 이름(`"search"`, `"checkout"`)을 붙일 수 있습니다. @hauntedhost의 [#243](https://github.com/D4Vinci/Scrapling/pull/243) 기여입니다.

### 🐛 버그 수정 {#v0.4.7-bug-fixes}

- **`FetcherSession`의 상태가 손상되는 문제와 지연 초기화 세션을 닫을 때 비정상 종료되는 문제를 수정했습니다**. @yetval의 [#245](https://github.com/D4Vinci/Scrapling/pull/245) 기여입니다.
- **`TypeError: Session.request() got an unexpected keyword argument 'block_ads'` 오류를 수정했습니다**. CLI의 `--ai-targeted` 플래그를 HTTP 명령과 함께 사용할 때 발생하던 문제입니다. @voidborne-d의 [#249](https://github.com/D4Vinci/Scrapling/pull/249) 기여입니다([#247](https://github.com/D4Vinci/Scrapling/issues/247) 수정).

### 번역 {#v0.4.7-translations}

- **브라질 포르투갈어 README 번역을 추가했습니다**. @rgomids의 [#250](https://github.com/D4Vinci/Scrapling/pull/250) 기여입니다.

## [v0.4.6](https://github.com/D4Vinci/Scrapling/releases/tag/v0.4.6) - 2026-04-13 {#v0.4.6}

**브라우저의 스텔스 기능, 개인정보 보호, 개발 편의를 개선하는 업데이트입니다 🔒**

### 🚀 새 기능과 사용 편의 개선 {#v0.4.6-new-stuff-and-quality-of-life-changes}

- **브라우저 Fetcher에 광고 차단 기능을 내장했습니다**. `block_ads=True`를 전달하면 알려진 광고 및 추적 도메인 약 3,500개로 향하는 요청을 라우트 가로채기 단계에서 막습니다. DNS 조회나 TCP 연결 없이 즉시 중단합니다. `blocked_domains`와 함께 사용해 직접 만든 목록도 추가할 수 있습니다. MCP 서버와 CLI의 `--ai-targeted` 모드는 이를 자동으로 켜서 토큰을 아끼고 페이지 로드를 빠르게 합니다.

    ```python
    page = StealthyFetcher.fetch('https://example.com', block_ads=True)
    ```

- **DNS-over-HTTPS 지원을 추가했습니다**. 프록시를 사용할 때 DNS 정보가 새는 것을 막습니다. `dns_over_https=True`를 전달하면 Cloudflare의 DoH로 DNS 쿼리를 보냅니다. HTTP 트래픽이 프록시를 거쳐도 DNS 조회로 실제 위치가 노출되는 문제를 방지합니다.

    ```python
    page = StealthyFetcher.fetch('https://example.com', proxy='http://proxy:8080', dns_over_https=True)
    ```

- **브라우저 Fetcher에 `page_setup` 콜백을 추가했습니다**. `page.goto()` 전에 실행되는 함수로, 페이지 이동 전에 필요한 이벤트 리스너, 라우트, 스크립트를 등록할 수 있습니다. 페이지 이동 후 실행되는 `page_action`과 함께 사용합니다([#237](https://github.com/D4Vinci/Scrapling/issues/237) 해결).

    ```python
    def capture_websockets(page):
        page.on("websocket", lambda ws: print(f"WS: {ws.url}"))

    page = DynamicFetcher.fetch('https://example.com', page_setup=capture_websockets)
    ```

- **CLI 옵션 `--block-ads`와 `--dns-over-https`를 추가했습니다**. `fetch`와 `stealthy-fetch` 명령 모두에서 사용할 수 있습니다.

### 🐛 버그 수정 {#v0.4.6-bug-fixes}

- **`Seconds` 타입 별칭이 부동소수점 값을 허용하지 않는 문제를 수정했습니다**. 브라우저 Fetcher에 `wait=1.5`나 `timeout=500.0`을 전달하면 타입 오류가 났습니다. 타입 별칭이 `float`를 타입이 아니라 메타데이터로 잘못 취급했기 때문입니다. @kuishou68의 [#240](https://github.com/D4Vinci/Scrapling/pull/240) 기여입니다.
- **전체 경로 선택자를 생성할 때 ID 부분이 중복되는 문제를 수정했습니다**. 전체 CSS/XPath 경로를 만들 때 `id` 속성이 있는 요소의 선택자가 두 번 추가되어 `body > #main > #main > #target > #target` 같은 결과가 나왔습니다. 전체 XPath 경로에서 `[@id='x']` 조건만 출력해 유효하지 않은 XPath가 되는 문제도 수정하고, `*[@id='x']`를 출력하도록 했습니다. @sjhddh의 [#241](https://github.com/D4Vinci/Scrapling/pull/241) 기여입니다.
- **셸 함수 시그니처에서 빠진 매개변수를 추가했습니다**. 대화형 셸의 함수 시그니처에는 `blocked_domains`, `block_ads`, `retries`, `retry_delay`, `capture_xhr`, `executable_path`, `dns_over_https`가 빠져 있었습니다.

## [v0.4.5](https://github.com/D4Vinci/Scrapling/releases/tag/v0.4.5) - 2026-04-07 {#v0.4.5}

**스파이더 개발을 크게 편하게 해 주는 기능 하나와 중요한 수정 사항을 담은 업데이트입니다 🎉**

### 🚀 새 기능과 사용 편의 개선 {#v0.4.5-new-stuff-and-quality-of-life-changes}

- **스파이더 개발 모드**: 이전에는 스파이더의 `parse()` 로직을 수정하고 실행할 때마다 대상 서버에 다시 요청해야 했습니다. 느리고 불필요한 트래픽을 만들며, 선택자를 조정하는 중에 요청 수 제한에 걸릴 수도 있었습니다. 새 개발 모드는 첫 실행에서 모든 응답을 디스크에 캐시하고, 이후에는 디스크에서 다시 읽습니다. 네트워크 요청을 하나도 보내지 않고 콜백을 수정해 원하는 만큼 다시 실행할 수 있습니다. 클래스 속성 하나로 켤 수 있습니다:

    ```python
    class MySpider(Spider):
        name = "my_spider"
        start_urls = ["https://example.com"]
        development_mode = True

        async def parse(self, response):
            yield {"title": response.css("title::text").get("")}
    ```

    기본 캐시 위치는 `.scrapling_cache/{spider.name}/`이며 `development_cache_dir`로 다른 위치를 지정할 수 있습니다. 새 통계 카운터 `cache_hits`와 `cache_misses`로 캐시 사용 상태를 확인할 수 있습니다. 캐시를 읽을 때는 `download_delay`, 요청 수 제한, 차단된 요청의 재시도 과정을 건너뛰므로 디스크가 허용하는 속도로 반복해서 확인할 수 있습니다. `development_mode = True`인 상태로 스파이더를 운영 환경에 배포하지 마세요. 개발 도구이지 운영용 캐시가 아닙니다. 자세한 내용은 [문서](spiders/advanced.md#development-mode)를 참고하세요.

- **기본 리디렉션를 더 안전하게 바꿨습니다**. 모든 HTTP Fetcher, MCP 서버, 셸에서 `follow_redirects`의 기본값이 `"safe"`가 됐습니다. 리디렉션는 계속 따라가지만, 내부 또는 사설 IP(루프백, 사설 네트워크, 링크 로컬)로 향하는 주소는 거부합니다. 사용자가 제공한 URL을 스크래핑할 때 SSRF를 방지합니다. 이전 동작을 사용하려면 `follow_redirects="all"`을, 리디렉션를 완전히 끄려면 `False`를 전달하세요.

### 🐛 버그 수정 {#v0.4.5-bug-fixes}

- **강제 종료해도 체크포인트가 사라지지 않습니다**. `crawldir`을 켠 스파이더에서 Ctrl+C를 두 번 눌러 강제 종료하면 체크포인트 쓰기와 충돌할 수 있었습니다. pickle 기록이 끝나기 전에 취소 범위가 작업을 종료해 `paused=False`가 남고, 이전 체크포인트를 *삭제하는* 정리 과정이 실행됐습니다. 그래서 긴 크롤링을 강제 종료하면 저장하려던 진행 상황을 모두 잃을 수 있었습니다. 이제 엔진은 **체크포인트를 먼저 기록한 뒤** `cancel_scope.cancel()`을 호출하므로, 강제 종료해도 최신 대기 상태를 항상 보존합니다. @voidborne-d의 [#230](https://github.com/D4Vinci/Scrapling/pull/230) 기여입니다.

## [v0.4.4](https://github.com/D4Vinci/Scrapling/releases/tag/v0.4.4) - 2026-04-05 {#v0.4.4}

**중요한 스파이더 개선과 버그 수정을 담은 업데이트입니다 🎉**

### 🚀 새 기능과 사용 편의 개선 {#v0.4.4-new-stuff-and-quality-of-life-changes}
- **스파이더 프레임워크에 robots.txt 준수 기능을 추가했습니다**. 새 `robots_txt_obey` 옵션을 켜면 크롤링 전에 robots.txt를 자동으로 가져와 `Disallow`, `Crawl-delay`, `Request-rate` 등의 규칙을 지킵니다. robots.txt 파일은 동시에 가져오고, 크롤링이 끝날 때까지 도메인별로 캐시합니다. @AbdullahY36의 [#226](https://github.com/D4Vinci/Scrapling/pull/226) 기여입니다.
- **robots.txt 캐시를 미리 준비하는 기능을 추가했습니다**. 크롤링 루프가 시작되기 전에 start_urls의 모든 도메인에서 robots.txt를 가져와 파싱합니다. 각 도메인의 첫 요청에서 기다릴 필요가 없어집니다.
- **새 통계 `robots_disallowed_count`를 추가했습니다**. `CrawlStats`에서 크롤링 중 robots.txt 규칙에 따라 차단된 요청 수를 기록합니다.

자세한 내용은 웹사이트의 [이 페이지](spiders/getting-started.md#robotstxt-compliance)를 확인하세요.

### 🐛 버그 수정 {#v0.4.4-bug-fixes}
- **`ProxyRotator`의 심각한 MRO 문제를 수정했습니다**. 임시 메서드 `_build_context_with_proxy`가 자식 클래스의 실제 구현을 가려, 프록시 순환 때마다 `NotImplementedError`가 발생했습니다([#215](https://github.com/D4Vinci/Scrapling/issues/215) 수정). @yetval에게 감사드립니다.
- **브라우저 세션에서 요청별로 프록시를 순환할 때 페이지 풀에 불필요한 참조가 남는 문제를 수정했습니다**. 임시 컨텍스트에서 만든 페이지가 정리할 때 풀에서 제거되지 않아, 유효하지 않은 참조가 계속 쌓였습니다. @yetval의 [#223](https://github.com/D4Vinci/Scrapling/pull/223) 기여입니다.
- **정적 Fetcher에 빠져 있던 타입 검증을 추가했습니다**. `curl_cffi`가 `None`을 `session.request()`에서 반환할 수 있어 후속 처리에 오류가 생기던 문제입니다.

### 기타 {#v0.4.4-other}
- 의존성을 갱신해 최신 지문과 다른 업데이트를 포함했습니다.
- robots.txt 파싱을 위해 `protego`를 선택 의존성 그룹 `fetchers`에 추가했습니다.

## [v0.4.3](https://github.com/D4Vinci/Scrapling/releases/tag/v0.4.3) - 2026-03-30 {#v0.4.3}

**여러 중요한 변경 사항을 담은 업데이트입니다 🎉**

### 🚀 새 기능과 사용 편의 개선 {#v0.4.3-new-stuff-and-quality-of-life-changes}
- **새 MCP 도구를 추가했습니다**. 일반 또는 스텔스 브라우저를 열고 그대로 유지해 다른 도구에서도 계속 사용할 수 있습니다. 브라우저를 닫는 도구도 추가했습니다([예제](https://github.com/D4Vinci/Scrapling/blob/v0.4.3/docs/ai/mcp-server.md#examples)).
- **새 MCP 도구를 추가했습니다**. 기존 브라우저 세션을 모두 나열하며, 새 도구들과 함께 사용하도록 만들었습니다.
- **브라우저 세션에 새 옵션을 추가했습니다**. 요청 중에 발생하는 모든 백그라운드 요청을 자동으로 수집합니다([#159](https://github.com/D4Vinci/Scrapling/pull/159) 해결) [[예제](https://github.com/D4Vinci/Scrapling/blob/v0.4.3/docs/fetching/dynamic.md#capturing-xhrfetch-requests)].
- **새 정리 도구를 추가했습니다**. 숨겨지거나 보이지 않는 내용을 제거해 일반적인 프롬프트 인젝션 공격으로부터 MCP 서버를 보호합니다.
- **웹 스크래핑 명령에 새 명령줄 옵션을 추가했습니다**. `--ai-targeted`를 사용하면 MCP 서버처럼 내용을 AI에 맞게 정리하고, 일반적인 프롬프트 인젝션 공격을 방지합니다.
- **브라우저 세션에 새 옵션을 추가했습니다**. `executable_path`로 원하는 브라우저 경로를 지정할 수 있습니다([#202](https://github.com/D4Vinci/Scrapling/pull/202) 해결).
- MCP 서버 코드를 **리팩터링**해 유지 보수를 쉽게 하고, 모든 도구를 비동기로 통일했습니다.
- CLI 명령 코드를 **리팩터링**해 유지 보수를 쉽게 하고, 210줄 줄였습니다.

### 🐛 버그 수정 {#v0.4.3-bug-fixes}
- 스파이더 세션에서 재시도할 때 HTTP 메서드를 유지하도록 수정했습니다. @karesansui-u의 [#201](https://github.com/D4Vinci/Scrapling/pull/201) 기여입니다.
- 페이지 내용을 가져올 때 재시도 횟수의 상한을 두어 무한 루프를 방지했습니다. @haosenwang1018 및 @D4Vinci의 [#197](https://github.com/D4Vinci/Scrapling/pull/197) 기여입니다.
- 예외를 지정하지 않은 `raise`를 `return False`로 바꿨습니다. 대상은 `_restore_from_checkpoint`입니다. @haosenwang1018의 [#196](https://github.com/D4Vinci/Scrapling/pull/196) 기여입니다.
- `get_all`을 `getall`로 바꿔 `Texthandler`를 Selector 클래스와 맞췄습니다.

### 커버리지와 테스트 개선 {#v0.4.3-coverage-tests-improvement}
- `_normalize_credentials`의 경계 사례를 검사하는 테스트를 추가했습니다. @Bortlesboat의 [#192](https://github.com/D4Vinci/Scrapling/pull/192) 기여입니다.
- 저장 후 같은 데이터를 다시 읽을 수 있는지 확인하는 테스트와 핵심 저장소 테스트를 추가했습니다. @haosenwang1018의 [#193](https://github.com/D4Vinci/Scrapling/pull/193) 기여입니다.
- `TextHandler`의 정규식 처리 경로와 `TextHandlers.re()`를 검사하는 테스트를 추가했습니다. @haosenwang1018의 [#194](https://github.com/D4Vinci/Scrapling/pull/194) 기여입니다.
- `filter`, `iterancestors`, `find_similar`의 경계 사례를 검사하는 테스트를 추가했습니다. @awanawana의 [#200](https://github.com/D4Vinci/Scrapling/pull/200) 기여입니다.

### Agent Skill 개선 {#v0.4.3-agent-skill-improvement}
- 스킬 참고 자료의 잘못된 Markdown 링크를 수정했습니다. @yetval의 [#204](https://github.com/D4Vinci/Scrapling/pull/204) 기여입니다.
- [Clawhub](https://clawhub.ai/d4vinci/scrapling-official) 검증을 더 잘 통과하도록 스킬 구성을 개선했습니다.
- 스킬이 명령줄로 스크래핑할 때 `--ai-targeted` 옵션을 반드시 사용하도록 했습니다.

### 문서 개선 {#v0.4.3-docs-improvement}
- 한국어 README 번역을 추가했습니다. @greatsk55의 [#187](https://github.com/D4Vinci/Scrapling/pull/187) 기여입니다.
- 중국어와 일본어 README에서 CJK 문자와 라틴 문자 사이의 공백을 수정했습니다.
- 이전 웹사이트 디자인에서 남아 있던 잘못된 링크를 수정했습니다.

## [v0.4.2](https://github.com/D4Vinci/Scrapling/releases/tag/v0.4.2) - 2026-03-08 {#v0.4.2}

**중요한 변경 사항이 포함된 새 유지 보수 업데이트입니다**

#### 버그 수정 {#v0.4.2-bug-fixes}
- 이제 `get_all_text()` 함수가 요소 뒤에 오는 텍스트 노드도 가져옵니다. 따라서 MCP 서버와 명령이 이전에 놓쳤던 텍스트도 읽을 수 있습니다([#168](https://github.com/D4Vinci/Scrapling/pull/168)). @mhillebrand 님 감사합니다.
- 이제 Referer는 Google 검색 URL 대신 Google 홈페이지 URL을 반환합니다. 이전 로직은 잘못되었으며, 봇을 식별하는 지문 신호가 되었을 수 있습니다([#179](https://github.com/D4Vinci/Scrapling/pull/179)). @Bortlesboat 님 감사합니다.
- 모든 브라우저에서 추가 플래그를 합칠 때 발생하던 문제를 수정했습니다. @rostchri 님 감사합니다.
- 3.12 미만의 Python 버전에서 실행이 중단되던 타입 힌트 문제를 수정했습니다. ([#163](https://github.com/D4Vinci/Scrapling/issues/163) 해결)

#### 기타 {#v0.4.2-other}
- Claude Code / OpenClaw 및 다른 AI 에이전트 도구를 위한 Agent Skill을 추가했습니다.
- Clawhub에 Agent Skill을 추가했습니다.
- 모든 브라우저와 Playwright를 최신 버전으로 업데이트했습니다.
- 기본 README 파일에 프랑스어 번역을 추가했습니다.

## [v0.4.1](https://github.com/D4Vinci/Scrapling/releases/tag/v0.4.1) - 2026-02-27 {#v0.4.1}

**중요한 변경 사항이 많이 포함된 새 업데이트입니다**

### 🚀 새 기능과 사용 편의 개선 {#v0.4.1-new-stuff-and-quality-of-life-changes}
- Cloudflare 검사를 감지하는 **정규식의 정확도를 개선했습니다**. (@Rinz27 님 감사합니다. [#133](https://github.com/D4Vinci/Scrapling/pull/133))
- Cloudflare 검사 처리의 **속도와 효율을 개선했습니다**. 이제 거의 두 배 빠릅니다.
- 웹사이트가 본 사이트로 이동하기 전에 Cloudflare 페이지를 두 번 표시하는 경우도 처리하도록 **Cloudflare 검사 처리를 개선했습니다**.
- 삽입하던 JS 파일을 제거하여 **스텔스 브라우저**의 스텔스 모드와 속도를 개선했습니다.
- OpenCode에서 사용할 수 있도록 **MCP 스키마를 개선했습니다**. (@robin-ede 님 감사합니다. [#137](https://github.com/D4Vinci/Scrapling/pull/137))
- VS Code Copilot과 검사가 엄격한 다른 도구에서도 사용할 수 있도록 **MCP 스키마의 호환성을 더 높였습니다**. (#150 해결)
- `main_content_only` 옵션이 켜져 있을 때 불필요한 HTML 태그를 제거하여 **MCP 서버의 토큰 사용량을 크게 줄였습니다**.
- PyPI 페이지를 수정하고 MCP 서버 레지스트리에 MCP 서버를 등록하는 데 필요한 파일을 추가했습니다.
- 자동화하기 쉽도록 명령줄 대신 코드로 브라우저 의존성을 설치하는 예제를 추가했습니다.
- 최신 버전의 액션을 사용하도록 모든 워크플로를 개선했습니다. (@salmanmkc 님 감사합니다. [#143](https://github.com/D4Vinci/Scrapling/pull/143)/[#144](https://github.com/D4Vinci/Scrapling/pull/144))

## [v0.4](https://github.com/D4Vinci/Scrapling/releases/tag/v0.4) - 2026-02-15 {#v0.4}

**지금까지 가장 큰 Scrapling 릴리스입니다. 스파이더 프레임워크, 프록시 순환, 주요 파서 개선 사항을 소개합니다**

이번 릴리스는 완전한 비동기 스파이더/크롤링 프레임워크, 스마트한 프록시 관리, 중요한 API 변경을 제공합니다. Scrapling의 기능이 더 강력해지고 일관성도 높아졌습니다. 업데이트하기 전에 호환성에 영향을 주는 변경 사항을 자세히 확인하세요.

### 🕷️ 스파이더 프레임워크 {#v0.4-spider-framework}

`anyio`를 기반으로 만든 새 비동기 크롤링 프레임워크로 대규모 스크래핑을 체계적으로 처리할 수 있습니다.

```python
from scrapling.spiders import Spider, Response

class MySpider(Spider):
  name = "demo"
  start_urls = ["https://example.com/"]

  async def parse(self, response: Response):
      for item in response.css('.product'):
          yield {"title": item.css('h2::text').get()}

MySpider().start()
```

-  **Scrapy와 비슷한 스파이더 API**: `start_urls`, 비동기 `parse` 콜백, `Request`/`Response` 객체, 우선순위 큐를 사용하여 스파이더를 정의합니다.
- **동시 크롤링**: 동시 요청 수 제한, 도메인별 속도 제한, 다운로드 지연을 설정할 수 있습니다.
- **여러 세션 지원**: 하나의 스파이더에서 HTTP 요청과 창 없는 모드의 스텔스 브라우저를 같은 인터페이스로 사용합니다. ID로 요청을 다른 세션에 보낼 수 있으며, 세션을 처음 사용할 때 초기화하는 방식도 지원합니다.
- **일시 중지와 재개**: 체크포인트로 크롤링 상태를 저장합니다. Ctrl+C로 안전하게 종료한 뒤 다시 실행하면 중단한 곳부터 계속합니다.
- **스트리밍 모드**: `async for item in spider.stream()`으로 수집한 항목을 즉시 받아 처리하고 실시간 통계도 확인합니다. UI, 파이프라인, 장시간 크롤링에 적합합니다.
- **차단된 요청 감지**: 차단된 요청을 자동으로 감지하고 다시 시도합니다. 처리 로직을 바꿀 수 있습니다.
- **기본 내보내기 기능**: 훅과 직접 만든 파이프라인으로 결과를 내보내거나, 기본 제공하는 `result.items.to_json()` / `result.items.to_jsonl()`로 각각 JSON/JSONL 형식으로 내보냅니다.
- **수명 주기 훅**: `on_start()`, `on_close()`, `on_error()`, `on_scraped_item()` 등 여러 훅으로 크롤링의 전체 수명 주기를 제어합니다.
- **자세한 크롤링 통계**: 요청, 응답, 바이트 수, 상태 코드, 프록시, 도메인별/세션별 통계, 로그 수준별 개수 등을 기록합니다.
- **uvloop 지원**: `use_uvloop=True`를 `spider.start()`에 전달하면 uvloop를 사용할 수 있는 환경에서 비동기 실행이 빨라집니다.

웹사이트에 자세한 설명을 담은 새 섹션을 추가했습니다. [여기](spiders/architecture.md)를 확인하세요.

### 🔄 프록시 순환 {#v0.4-proxy-rotation}

* 여러 스레드에서 안전하게 프록시를 순환하는 새 `ProxyRotator` 클래스입니다. 모든 Fetcher와 세션에서 사용할 수 있습니다.

  ```python
  from scrapling import ProxyRotator
  rotator = ProxyRotator(["http://proxy1:8080", "http://proxy2:8080"])
  Fetcher.get(url, proxy_rotator=rotator)
  ```

* **사용자 정의 순환 전략**: 프록시 순환 로직을 직접 만들 수 있습니다.
* **요청별 프록시 변경**: `proxy=`를 개별 `get()`/`post()`/`fetch()` 호출에 전달하면 해당 요청에서 세션의 프록시 대신 사용합니다.

### 🌐 브라우저 Fetcher 개선 {#v0.4-browser-fetcher-improvements}

* **도메인 차단**: 새 `blocked_domains` 매개변수를 `DynamicFetcher`/`StealthyFetcher`에 추가했습니다. 특정 도메인으로 가는 요청을 차단하며, 하위 도메인도 자동으로 포함합니다.
* **자동 재시도**: 이제 브라우저 Fetcher는 `retries`(기본값: 3)와 `retry_delay`(기본값: 1s) 매개변수에 따라 실패한 요청을 다시 시도합니다. 프록시 관련 오류도 감지합니다.
* **응답 메타데이터**: `Response.meta` 딕셔너리는 사용한 프록시를 자동으로 저장하고 요청 메타데이터를 합칩니다.
* **Response.follow()**: 스파이더 시스템을 위해 만든 기능으로, Referer를 자동으로 전달하는 후속 `Request` 객체를 생성합니다.
* **자동 재생 차단**: 브라우저 세션이 이전에 문제를 일으키던 자동 재생 콘텐츠를 차단합니다.
* **속도**: 브라우저 플래그를 조정하여 탐지 회피와 속도를 개선했습니다.

### 🔧 버그 수정 및 개선 {#v0.4-bug-fixes-improvements}
- **파서 최적화**: 반복 작업을 최적화하여 파서의 성능을 높였습니다.
- **페이지 오류**: 페이지에서 오류가 발생하면 브라우저가 닫히지 않던 버그를 수정했습니다.
- **빈 본문**: 본문이 비어 있는 응답을 처리합니다.
- **Playwright 루프**: CDP 연결이 실패하면 Playwright 루프가 열린 채로 남던 문제를 해결했습니다.
- **타입 안전성**: 모든 mypy 오류를 수정하고 타입이 없던 함수 본문 전체에 타입 힌트를 추가했습니다. CI 워크플로에 mypy와 pyright를 추가했습니다.

### ⚠️ 호환성에 영향을 주는 변경 사항 {#v0.4-breaking-changes}

* **`css_first`/`xpath_first` 제거**: 대신 `css('.selector').first`, `css('.selector')[0]` 또는 `css('.selector').get()`을 사용하세요.
* **모든 선택 작업이 `Selectors` 반환**: 이제 `css('::text')`, `xpath('//text()')`, `css('::attr(href)')`, `xpath('//@href')`는 `Selectors`를 반환합니다. 텍스트 노드를 `Selector` 객체로 감싸고 `tag="#text"`를 설정하며, 더 이상 `TextHandlers`를 반환하지 않습니다. 모든 선택 메서드와 타입 힌트에서 API가 일관되게 동작합니다.
* **`Response.body`는 항상 `bytes`**: 이전에는 `str` 또는 `bytes`였지만 이제 항상 `bytes`를 반환합니다.
* **`get()`/`getall()` 동작**: `Selector`에서 `get()`은 `TextHandler`(직렬화된 HTML 또는 텍스트 값)를, `getall()`은 `TextHandlers`를 반환합니다. 별칭은 `extract_first = get`, `extract = getall`입니다. 이전 `get_all()` 메서드는 `Selectors`에서 제거했습니다.
* **`Selectors.first`/`.last`**: `Selector | None`을 반환하며 `IndexError`를 발생시키지 않는 안전한 접근 속성입니다.
* **내부 상수 이름 변경**: `DEFAULT_FLAGS` → `DEFAULT_ARGS`, `DEFAULT_STEALTH_FLAGS` → `STEALTH_ARGS`, `HARMFUL_DEFAULT_ARGS` → `HARMFUL_ARGS`, `DEFAULT_DISABLED_RESOURCES` → `EXTRA_RESOURCES`.

### 🔨 기타 변경 사항 {#v0.4-other-changes}

* **의존성 변경**: `tldextract`를 `tld`로 교체하고 내부 `_html_utils.py` 대신 `w3lib.html.replace_entities`를 사용합니다. `typing_extensions`를 필수 의존성으로 추가했습니다.
* **문서 개편**: MkDocs에서 Zensical로 완전히 전환했습니다. 스파이더 문서 섹션을 새로 만들고 기존 페이지를 모두 업데이트했으며 새 API 참고 문서를 추가했습니다.

## [v0.3.14](https://github.com/D4Vinci/Scrapling/releases/tag/v0.3.14) - 2026-01-03 {#v0.3.14}

**v0.3.13에서 일부 기기에 발생한 문제를 수정하는 작은 유지 보수 업데이트입니다**

- Windows 기기에서 페이지 간에 쿠키가 유지되지 않아 `StealthyFetcher`와 해당 세션 클래스의 시크릿 모드를 껐습니다. MacOS와 Linux에서는 발생하지 않았습니다. ([#123](https://github.com/D4Vinci/Scrapling/issues/123) 수정. 문제를 알려 준 @frugality4121 님과 해결 방법을 알려 준 @gembleman 님 감사합니다.)
- 이미 오래된 browserforge를 사용하는 환경에서 이전 헤더 모델 때문에 발생하는 문제를 해결하도록 browserforge의 최신 버전을 고정했습니다.

## [v0.3.13](https://github.com/D4Vinci/Scrapling/releases/tag/v0.3.13) - 2026-01-01 {#v0.3.13}

**여러 부분을 개선한 큰 업데이트입니다. 필요에 따라 호환성에 영향을 주는 변경도 많이 포함했습니다. 업데이트하기 전에 아래 내용을 읽어 주세요**

* 여러 이유로 앞으로 Camoufox 사용을 완전히 중단하기로 했습니다. 개발이 계속된다면 나중에 다시 사용할 수도 있습니다. 이번 릴리스 이전처럼 Camoufox를 계속 사용하려면 이 [섹션](https://github.com/D4Vinci/Scrapling/blob/v0.3.13/docs/fetching/stealthy.md#using-camoufox-as-an-engine)의 설명을 따르세요.

* 이전에는 `DynamicFetcher`와 해당 세션 클래스의 스텔스 모드에서 patchright를 사용했습니다. 이제 해당 클래스에서 스텔스 모드를 제거하고 `StealthyFetcher`와 해당 세션 클래스에서 patchright를 사용합니다. 아래에서 설명하는 여러 개선을 더해 patchright의 기본 기능보다 전반적인 탐지 회피 성능을 높였습니다.

**이 변경으로 `StealthyFetcher`와 해당 세션 클래스는 이전보다 101% 빨라졌고 메모리와 저장 공간도 덜 사용하며, 코드가 약 400줄 줄었습니다. 무엇보다 이전에 Camoufox를 사용할 때보다 안정적입니다.**

또한 `scrapling install` 명령의 설치 시간을 줄이고 Docker 이미지 크기를 줄이며, GitHub CI에서 테스트가 더 원활하게 실행됩니다. 처음 쓰는 사람도 Scrapling을 더 쉽게 이해할 수 있습니다.

### 호환성에 영향을 주는 변경 사항 {#v0.3.13-breaking-changes}
1. `stealth` 인수를 `DynamicFetcher` 클래스와 해당 세션 클래스에서 제거했습니다. `hide_canvas` 인수는 `StealthyFetcher`와 해당 세션 클래스로 옮겼습니다.
2.  `disable_webgl` 인수를 `DynamicFetcher`에서 `StealthyFetcher` 클래스로 옮기고 이름을 `allow_webgl`로 바꿨습니다. 모든 세션 클래스에도 적용됩니다.
3. 이제 `StealthyFetcher` 클래스는 기본적으로 `DynamicFetcher`의 새 스텔스 버전입니다. 따라서 `block_images`, `humanize`, `addons`, `os_randomize`, `disable_ads`, `geoip` 인수를 제거했습니다. Chromium에서 같은 기능을 구현하려고 했지만 각 기능마다 문제가 있었습니다. v0.4 이전의 후속 릴리스에서 바뀔 수도 있습니다.

좋은 소식도 있습니다. 많은 부분을 개선하고 수정했습니다 :)

### 개선 사항 {#v0.3.13-improvements}
- 앞에서 설명했듯이 `StealthyFetcher` 클래스와 해당 세션 클래스는 이전보다 101% 빨라졌습니다. `DynamicFetcher` 클래스와 해당 세션 클래스도 20% 빨라졌습니다.
- Cloudflare 검사 처리 알고리즘을 개선하여 더 빠르게 완료하고 더 많은 경우를 처리합니다. 새 리팩터링 덕분에 CAPTCHA도 두 배 빠르게 해결할 수 있습니다!
- 모든 Fetcher가 메모리를 덜 사용합니다.
- MCP 서버의 토큰 사용량이 줄어 비용을 더 아낄 수 있습니다!
- Docker 이미지가 60% 작아졌습니다.
- 문서 웹사이트 전체에 새 내용을 반영했습니다. 동시에 설명을 더 명확하게 쓰고 여러 섹션을 짧게 줄였으며, 예제를 추가하고 누락된 인수를 포함했습니다. API 참고 문서에 그래프를 추가하는 등 여러 부분을 개선했습니다. 이제 웹사이트가 130% 빨리 로드되고 데이터를 덜 사용하며 SEO에도 더 적합합니다.

### 수정 사항 {#v0.3.13-fixes}
- 웹 스크래핑 셸의 단축 함수에 누락되었던 인수를 추가하고 더 정확하게 동작하도록 수정했습니다.
- URL이 localhost/IP여도 `google_search` 인수가 Google Referer를 만들던 문제를 수정했습니다.

## [v0.3.12](https://github.com/D4Vinci/Scrapling/releases/tag/v0.3.12) - 2025-12-18 {#v0.3.12}

### 변경 사항 {#v0.3.12-what-s-changed}
- `DynamicSession`/`AsyncDynamicSession` 클래스에 `timezone_id`라는 새 인수를 추가했습니다. 사용 중인 프록시/VPN의 시간대에 맞게 브라우저의 시간대를 설정할 수 있습니다. 따라서 웹사이트가 시간대 불일치로 프록시 사용을 감지할 수 없습니다.
- 응답을 JSON으로 자동 변환하는 기능을 개선했습니다.
- Fetcher의 세션 클래스에서 내부 함수 `__create__`의 이름을 `start`로 바꿨습니다. `with` 컨텍스트 밖에서도 더 쉽게 사용할 수 있습니다.
- `curl_cffi`와 다른 의존성을 최신 버전으로 업데이트했습니다.

## [v0.3.11](https://github.com/D4Vinci/Scrapling/releases/tag/v0.3.11) - 2025-12-03 {#v0.3.11}

### 변경 사항 {#v0.3.11-what-s-changed}
- 불안정한 웹사이트(미디어가 재생되는 사이트 등)에서 `network_idle` 인수를 사용할 때 타임아웃 오류를 더 잘 처리하도록 개선했습니다.
- 웹 스크래핑 셸에서 `stealthy_fetch` 단축 함수의 자동 완성을 수정했습니다.

## [v0.3.10](https://github.com/D4Vinci/Scrapling/releases/tag/v0.3.10) - 2025-11-26 {#v0.3.10}

**많은 주요 변경 사항과 호환성에 영향을 줄 수 있는 변경이 포함된 유지 보수 업데이트입니다**

- 인코딩이 올바르게 선언되지 않은 웹페이지도 처리하는 더 나은 방식으로 모든 인코딩 문제를 **해결했습니다**. (@Kemsty2 님이 [#110](https://github.com/D4Vinci/Scrapling/issues/110) [#111](https://github.com/D4Vinci/Scrapling/pull/111)에서 문제를 알려 주셨습니다. 감사합니다.)
- 모든 브라우저 Fetcher에서 요청 수준의 매개변수로 세션 수준의 매개변수를 덮어쓸 때 발생하던 로직 문제를 **해결했습니다**. v0.3부터 있던 문제입니다.
- 대화형 웹 스크래핑 셸의 단축 함수 시그니처를 **수정하여** 셸에서 단축 함수의 자동 완성이 완벽하게 동작하도록 했습니다. 이 문제도 v0.3부터 있었습니다.
- Maxmind 데이터베이스의 버전을 **높였습니다**. `geoip` 인수가 `StealthyFetcher`와 해당 세션 클래스에서 더 잘 동작합니다.
- 사용하는 모든 브라우저를 최신 버전으로 **업데이트했습니다**.
- **호환성에 영향을 주는 변경** - 모든 Fetcher를 크게 리팩터링했습니다. 다음 변경으로 기존 코드가 동작하지 않을 수 있습니다.
    1. Scrapling 코드가 약 750줄 줄었습니다. 여러 변경으로 앞으로 유지 보수가 훨씬 쉬워지고 리소스 사용량도 조금 줄어듭니다.
    2. 모든 Fetcher와 해당 세션 클래스의 검증 속도가 크게 빨라져 전체 속도도 높아집니다.
    3. 이를 위해 모든 Fetcher에서 `url` 인수만 위치 인수로 받을 수 있게 했습니다. 나머지는 키워드 인수여야 합니다. 코드를 `Fetcher.get('https://google.com', stealthy_headers=True)`처럼 작성해야 합니다. 어떤 이유로든 `Fetcher.get('https://google.com', True)`처럼 사용했다면 수정하세요!
    4. v0.3부터 브라우저 Fetcher와 해당 세션 클래스 사이에 불편한 차이가 있었습니다. 요청별 파서 설정을 전달하는 인수가 Fetcher에서는 `custom_config`, 세션 클래스에서는 `selector_config`였습니다. 이번 리팩터링으로 기존 코드를 깨뜨리지 않고 이름을 `selector_config`로 통일했습니다. 기본 이름은 이제 `selector_config`이며, `custom_config` 인수와의 하위 호환성도 유지합니다. 자동 완성은 `selector_config` 인수에만 지원됩니다.
    5. 이 모든 변경을 위해 Fetcher 함수의 타입 힌트를 동적으로 생성하도록 바꿨습니다. IDE의 자동 완성이 제대로 동작하지 않으면 오래된 버전은 아닌지 확인하세요. 거의 모든 주요 IDE와 편집기에서 테스트했습니다.

> 모든 벤치마크 표도 현재 수치로 업데이트하여 다른 라이브러리의 최신 버전과 비교했습니다.

## [v0.3.9](https://github.com/D4Vinci/Scrapling/releases/tag/v0.3.9) - 2025-11-17 {#v0.3.9}

**중요한 변경 사항이 많이 포함된 새 업데이트입니다**

### 🚀 새 기능과 사용 편의 개선 {#v0.3.9-new-stuff-and-quality-of-life-changes}
- 이제 `impersonate` 인수는 `Fetcher`와 `FetcherSession`에서 브라우저 목록을 받을 수 있습니다. 요청마다 목록에서 브라우저 하나를 무작위로 선택합니다.

```python
from scrapling.fetchers import FetcherSession

with FetcherSession(impersonate=['chrome', 'firefox', 'safari']) as s:
  s.get('https://github.com/D4Vinci/Scrapling')
```

- `clean` 메서드에 새 인수를 추가했습니다. `TextHandler`의 현재 텍스트에서 HTML 엔티티를 쉽게 제거할 수 있습니다.
- 여러 부분의 설명을 더 정확하게 쓰고 기본 `README.md` 파일의 자동 번역을 추가하는 등 문서를 크게 개선했습니다.

### 🐛 버그 수정 {#v0.3.9-bug-fixes}
- 브라우저 Fetcher에서 응답을 가져올 때 발생하던 큰 문제를 수정했습니다. 이제 콘텐츠 유형을 감지하여 HTML일 때만 `response.body`에 브라우저가 렌더링한 내용을 넣습니다. 그 외에는 마지막 요청의 원본 내용을 넣습니다. 따라서 바이너리 파일과 텍스트 파일을 HTML 태그로 감싸지 않은 상태로 다운로드할 수 있으며, 웹사이트를 가져올 때는 원하는 렌더링 결과도 받을 수 있습니다.

### 🔨 기타 {#v0.3.9-misc}
- 기여 가이드를 더 명확하고 쉽게 업데이트했습니다.
- 코드 품질 도구를 반드시 실행하는 새 워크플로를 추가했습니다. pre-commit 훅과 같은 도구를 사용합니다.

## [v0.3.8](https://github.com/D4Vinci/Scrapling/releases/tag/v0.3.8) - 2025-10-27 {#v0.3.8}

**중요한 변경 사항이 많이 포함된 새 업데이트입니다**

### 🚀 새 기능과 사용 편의 개선 {#v0.3.8-new-stuff-and-quality-of-life-changes}
- 모든 브라우저 Fetcher에서 요청 로딩이 끝나지 않는 웹사이트에 `network_idle`을 사용해도 코드 실행이 중단되지 않습니다.
- 브라우저 Fetcher가 페이지 내용을 가져오고 확인하는 로직을 바꿨습니다. 이제 Windows에서도 Linux/MacOS처럼 브라우저가 더 안정적으로 동작합니다. 이 동작 차이는 Windows에서 Playwright의 구현 방식이 다르기 때문에 발생했습니다.
- 모든 검증 로직을 리팩터링하여 모든 브라우저 Fetcher의 요청이 8-15% 빨라졌습니다.
- `extra_flags`라는 새 옵션을 `DynamicFetcher`와 해당 세션에 추가했습니다. 브라우저를 시작할 때 기존 Chrome 플래그에 원하는 플래그를 더할 수 있습니다.
- `page_action`을 사용할 때는 응답을 가져오는 라우팅 로직을 이전 버전으로 되돌렸습니다. 이 로직은 직전 버전에서 바뀌었습니다. `page_action`이 요청을 보내지 않고 페이지 내용을 바꾸더라도 최신 내용을 가져오기 위한 변경입니다. ([#100](https://github.com/D4Vinci/Scrapling/issues/100)과 [#102](https://github.com/D4Vinci/Scrapling/pull/102)에서 알려 준 @gembleman 님 감사합니다.)

### 🐛 버그 수정 {#v0.3.8-bug-fixes}
- DynamicSession의 async_fetch에서 `load_dom`의 오타를 수정했습니다.
- 통과한 뒤에도 사라지지 않는 삽입형 CAPTCHA를 Cloudflare 검사 처리 중에 계속 기다리던 문제를 수정했습니다. 이제 CAPTCHA가 사라질 때까지 30초 동안 기다린 다음, 사라지지 않는 유형으로 간주합니다. (#100 수정)

### 🔨 기타 {#v0.3.8-misc}
- 사용자가 편리하게 쓸 수 있도록 Docker 이미지를 Dockerhub와 GitHub 컨테이너 레지스트리에 자동으로 푸시합니다.
- Scrapling에서 Scrapeless 브라우저를 사용하는 방법을 설명하는 [새 문서 페이지](https://github.com/D4Vinci/Scrapling/blob/v0.3.8/docs/tutorials/external.md)를 추가했습니다.

## [v0.3.7](https://github.com/D4Vinci/Scrapling/releases/tag/v0.3.7) - 2025-10-12 {#v0.3.7}

**중요한 변경 사항이 많이 포함된 새 업데이트입니다**

### 🚀 새 기능과 사용 편의 개선 {#v0.3.7-new-stuff-and-quality-of-life-changes}
- `solve_cloudflare` 인수를 다시 구현하여 `StealthyFetcher`가 모든 종류의 사용자 정의 Turnstile 구현을 해결할 수 있게 했습니다.
- Pyright 검사를 통과하도록 전체 코드를 리팩터링했습니다. 이제 모든 IDE에서 원활하게 작업할 수 있으며, 여러 버그도 해결했습니다.
- 요청 로직을 더 깔끔하고 빠르게 리팩터링했습니다. (#97도 해결)
- 모든 브라우저 세션 클래스에 새 `user_data_dir` 옵션을 추가했습니다. 이전 세션의 브라우저 데이터(쿠키/저장소 등)를 다시 사용할 수 있습니다. 지정하지 않으면 이전처럼 Playwright가 실행할 때마다 무작위 디렉터리를 사용합니다.
- 새 `additional_args` 옵션을 `Dynamic fetcher`와 해당 세션 클래스에 추가했습니다. 이전의 `StealthyFetcher`처럼 Playwright 컨텍스트에 추가 인수를 전달할 수 있습니다.
- 모든 브라우저에서 마지막 탐색 응답을 가져오는 라우팅 로직을 개선했습니다. 이전에는 브라우저가 먼저 처리했지만, 이제 처리 전의 원본 응답을 파서에 전달합니다. 텍스트/JSON 응답에 매우 유용합니다.

### 🐛 버그 수정 {#v0.3.7-bug-fixes}
- 라우팅 로직을 다시 구현하여 일부 Windows 기기에서 불안정한 웹사이트의 내용을 가져오지 못하던 문제를 해결했습니다.
- 이번 버전의 여러 리팩터링 과정에서 이전에는 찾기 어려웠던 많은 버그와 일부 IDE의 이상한 자동 완성 문제도 해결했습니다.
- 문서 웹사이트의 여러 부분을 수정했습니다.

## [v0.3.6](https://github.com/D4Vinci/Scrapling/releases/tag/v0.3.6) - 2025-10-01 {#v0.3.6}

### 🚀 새 기능 {#v0.3.6-new-stuff}
- `solve_cloudflare` 인수를 개선하여 `StealthyFetcher`와 해당 세션 클래스가 모든 종류의 Cloudflare Turnstile/Interstitial 검사를 통과할 수 있게 했습니다 🎉
- 이제 MCP 서버에서 `Streamable HTTP`를 사용할 수 있어 서버를 쉽게 외부에 제공할 수 있습니다.
- Docker 지원을 추가했습니다. 이제 릴리스마다 모든 브라우저가 포함된 이미지를 자동으로 빌드하고 Docker Hub에 푸시합니다.

### 🐛 버그 수정 {#v0.3.6-bug-fixes}
- 일부 상황에서 파서에 발생하던 인코딩 문제를 수정했습니다. 잘 알려진 `invalid start byte` 오류입니다.
- 라이브러리의 여러 부분을 재구성하여 메모리 누수를 수정했습니다. 이제 설정에 따라 메모리 사용량이 눈에 띄게 줄어듭니다. (#92도 해결)
- 코드 곳곳의 타입 표기를 개선하여 IDE를 더 편하게 사용할 수 있게 했습니다. (#93도 해결)

## [v0.3.5](https://github.com/D4Vinci/Scrapling/releases/tag/v0.3.5) - 2025-09-20 {#v0.3.5}

**여러 문제를 해결하는 필수 릴리스입니다**

### 🚀 새 기능 {#v0.3.5-new-stuff}
- 모든 브라우저 Fetcher(`DynamicFetcher`/`StealthyFetcher`/...)와 해당 세션 클래스가 웹사이트를 15-20% 더 빠르게 가져옵니다.
    1. @AbdullahY36 님이 #87에서 로직을 개선하여 페이지 관리가 훨씬 빨라졌습니다.
    2. 전체 검증 로직을 최적화하고 동기 요청의 페이지 생성을 개선하여 속도가 크게 높아졌습니다.

- `DynamicFetcher`와 해당 세션 클래스에서 `rebrowser-playwright`를 `PatchRight`로 교체하여 스텔스 모드를 크게 개선했습니다.
    1. 이전에는 `rebrowser-playwright`가 `stealth`와 `real_chrome`을 함께 사용하면 제대로 동작하지 않아 비활성화되었습니다. 이제 `PatchRight`에서는 이 문제가 없습니다.
    2. 이제 closed 모드의 Shadow Root와 상호작용할 수 있습니다. `PatchRight`가 자동으로 처리합니다.

### 🐛 버그 수정 {#v0.3.5-bug-fixes}
- `re` 메서드를 `Selectors` 클래스에서 사용할 때 발생하던 버그를 수정했습니다.
- 웹 스크래핑 셸의 `uncurl`과 `curl2fetcher` 명령이 curl의 `--data-raw` 플래그를 잘못 파싱하던 버그를 수정했습니다.
- 웹 스크래핑 셸의 `view` 명령에서 웹사이트의 인코딩에 따라 발생하던 버그를 수정했습니다.
- `mcp` 모드와 `extract` 명령에 영향을 주던 콘텐츠 변환 버그를 수정했습니다.

### 새 기여자 {#v0.3.5-new-contributors}
- @AbdullahY36 님이 #87에서 처음으로 기여했습니다.

## [v0.3.4](https://github.com/D4Vinci/Scrapling/releases/tag/v0.3.4) - 2025-09-16 {#v0.3.4}

**여러 문제를 해결하는 필수 릴리스입니다**

### 🚀 새 기능 {#v0.3.4-new-stuff}
- 대화형 셸에 모든 Fetcher 세션 클래스를 추가했습니다. 임포트 없이 바로 사용할 수 있습니다.

### 🐛 버그 수정 {#v0.3.4-bug-fixes}
- Cloudflare 검사를 처리하면서 페이지 내용을 가져올 때 Windows의 Playwright API에서 발생하던 버그를 우회하는 방법을 추가했습니다.
- 대화형 셸에서 `view` 명령의 인코딩 문제를 수정했습니다.
- `max_pages` 인수로 인해 `AsyncStealthySession`에서 실행이 중단되던 버그를 수정했습니다.
- `html_content`와 `prettify` 속성에 최근 업데이트로 생긴 문제를 수정했습니다. `Selector` 클래스의 두 속성이 인코딩에 따라 바이트를 반환했습니다. 이제 둘 다 이전처럼 문자열을 반환합니다.

## [v0.3.3](https://github.com/D4Vinci/Scrapling/releases/tag/v0.3.3) - 2025-09-15 {#v0.3.3}

- 브라우저 Fetcher에서 기본 브라우저 탭을 제거하는 로직을 없앴습니다. 이 로직이 실행을 중단시키는 오류를 일으켰기 때문입니다. Mac에서는 발생하지 않았고 Windows와 Linux에서만 재현했습니다.

## [v0.3.2](https://github.com/D4Vinci/Scrapling/releases/tag/v0.3.2) - 2025-09-15 {#v0.3.2}

v0.3.2 릴리스 노트

### 🚀 새 기능 {#v0.3.2-new-stuff}

- **선택적 Fetcher 의존성**: 모든 Fetcher를 선택적 의존성 그룹으로 옮겨 핵심 패키지 크기를 줄였습니다. 이제 기본 `scrapling` 모듈에는 파서만 있습니다. Fetcher나 명령줄 옵션을 사용하려면 `pip install "scrapling[fetchers]"`를 실행해야 합니다. 자세한 설치 방법은 [여기](index.md#installation)를 확인하세요.
- **세션의 페이지별 설정**: 브라우저 Fetcher의 세션 클래스에서 각 페이지를 별도로 설정할 수 있습니다. 이제 요청 수준의 모든 매개변수도 세션 수준의 매개변수처럼 검증합니다. 자세한 내용은 문서 웹사이트의 [이 페이지](fetching/stealthy.md#full-list-of-arguments)를 확인하세요.
    <br>예제:

    ```python
    with StealthySession(headless=True, solve_cloudflare=True) as session:
        page = session.fetch('https://nopecha.com/demo/cloudflare', google_search=False)
    ```

- **브라우저 Fetcher 개선**
    - 페이지에서 JavaScript 실행이 끝날 때까지 기다릴지 정하는 새 옵션을 추가했습니다. 이전과 같이 기본적으로 켜져 있습니다.

        ```python
        with DynamicSession(headless=True, disable_resources=False, network_idle=True) as session:
           page = session.fetch('https://quotes.toscrape.com/', load_dom=False)
        ```

    - `DynamicFetcher`와 해당 세션 클래스의 스텔스 모드가 더 안정적으로 동작합니다.
    - `DynamicFetcher`와 `StealthyFetcher` 모두 리소스를 덜 사용합니다. Playwright API의 영구 컨텍스트가 여는 기본 탭을 자동으로 찾아 닫습니다.
    - 브라우저 Fetcher의 페이지 순환 로직에서 중요한 버그를 수정했습니다. 이제 이전 페이지를 새 페이지로 교체합니다. 순환하며 재사용하는 탭에는 이전 설정이 남아 있을 수 있습니다.
    - `StealthyFetcher`와 해당 세션 클래스가 조금 더 빨라졌습니다(5%).

- **`.body` 속성 개선**: 전달받은 내용을 처리하지 않고 그대로 반환하므로 파일을 다운로드하고 HTML이 아닌 요청도 처리할 수 있습니다. 다음은 사진을 다운로드하는 예제입니다.

    ```python
    from scrapling.fetchers import Fetcher

    page = Fetcher.get('https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/poster.png')
    with open(file='poster.png', mode='wb') as f:
        f.write(page.body)
    ```

### 🐛 버그 수정 {#v0.3.2-bug-fixes}

- **인코딩 문제 해결**: 일부 웹사이트에서 파서, mcp 모드, extract 명령에 발생하던 여러 인코딩 문제를 수정했습니다. (#80과 #81도 해결)
- **더 빠른 파싱**: 여러 변경으로 라이브러리가 더 빨라졌으며, 업데이트된 벤치마크에서 확인할 수 있습니다.

### 🔨 기타 {#v0.3.2-misc}

- **벤치마크 업데이트**: 현재 속도 개선을 비슷한 라이브러리의 최신 버전과 비교하도록 성능 벤치마크를 갱신했습니다.
- **많은 코드를 리팩터링하고 사용하지 않는 코드를 더 나은 구현으로 교체했습니다**: 코드가 줄고 더 깔끔해져 유지 보수가 쉬워졌습니다.
- **YouTube 영상 추가**: MCP 문서에 영상을 포함했습니다.
- **새 이슈 템플릿**: 기존 템플릿을 사용할 수 없는 사용자를 위해 쉬운 새 템플릿을 추가했습니다.
- **CI 워크플로 최적화**: 문서나 코드가 아닌 파일만 바뀌면 테스트 워크플로를 건너뜁니다.
- **의존성 업데이트**: 여러 의존성을 최신 버전으로 높였습니다.
- **코드 스타일 개선**: 모든 파일에 새 ruff 규칙을 적용했습니다.
- **Pre-commit 훅**: pre-commit 설정을 업데이트했습니다.

### 🎯 호환성에 영향을 주는 변경 사항 {#v0.3.2-breaking-changes}

- `max_pages` 매개변수를 동기 `StealthySession`에서 제거하여 `DynamicSession`과 맞췄습니다. 동기 버전에서는 의미가 없는 매개변수입니다.

## [v0.3.1](https://github.com/D4Vinci/Scrapling/releases/tag/v0.3.1) - 2025-09-02 {#v0.3.1}

1. `shell` 선택 의존성 그룹 없이 Scrapling을 설치할 때 발생하던 문제를 수정했습니다. (#76)
2. 모든 브라우저 Fetcher와 해당 세션 클래스에 페이지 생성 시 실행할 JS 파일을 지정하는 새 인수를 추가했습니다. (#56):

```python
from scrapling.fetchers import StealthyFetcher

StealthyFetcher.fetch('https://example.com', init_script="/absolute/path/to/js/script.js")
```

## [v0.3](https://github.com/D4Vinci/Scrapling/releases/tag/v0.3) - 2025-09-01 {#v0.3}

🎉 **주요 릴리스 - 전체 구조 개편**

Scrapling v0.3은 프로젝트 역사상 가장 큰 업데이트입니다. 전체 구조를 새로 작성하고 성능을 크게 개선했으며, AI 연동과 대화형 웹 스크래핑 셸을 비롯한 강력한 새 기능을 추가했습니다.

이번 릴리스에는 호환성에 영향을 주는 변경 사항이 여러 개 있습니다. 릴리스 노트를 주의 깊게 읽어 주세요.

### 🚀 주요 새 기능 {#v0.3-major-new-features}

#### 세션 기반 구조 {#v0.3-session-based-architecture}
- **새 세션 클래스**: 코드를 완전히 새로 작성해 세션을 유지하는 기능을 추가했습니다.
    - `FetcherSession` - 상태를 유지하는 HTTP 요청을 동기 코드와 비동기 코드 모두에서 사용할 수 있습니다.
    - `DynamicSession`/`AsyncDynamicSession` - 작업이 끝날 때까지 브라우저를 열어둔 채로 브라우저를 자동화합니다.
    - `StealthySession`/`AsyncStealthySession` - 작업이 끝날 때까지 브라우저를 열어둔 채로 스텔스 모드에서 탐색합니다.
- **비동기 브라우저 탭 관리**: 새 탭 풀 기능의 `max_pages` 인수로 브라우저 탭을 번갈아 사용하며 여러 페이지를 동시에 가져올 수 있습니다.
- **동시 세션**: 서로 분리된 여러 세션을 동시에 실행합니다.

자세한 내용은 웹사이트의 `Fetching` 섹션을 참고하세요.

#### 다양한 새 스텔스 및 봇 차단 우회 기능 {#v0.3-a-lot-of-new-stealth-anti-bot-capabilities}
- **🤖 Cloudflare 검사 통과**: [Cloudflare Turnstile 검사를 자동으로 통과하는 기능](fetching/stealthy.md#cloudflare-and-stealth-options)을 `StealthyFetcher`와 해당 세션 클래스에 추가했습니다.
- **브라우저 지문 모방**: 완전히 새로 만든 [Fetcher](fetching/static.md) 클래스로 실제 브라우저의 TLS 지문과 버전에 맞는 브라우저 헤더를 모방하고, HTTP/3 등을 사용할 수 있습니다.
- **스텔스 모드 개선**: `DynamicFetcher`와 해당 세션 클래스의 스텔스 모드가 더 강력하고 안정적으로 바뀌었습니다. (클래스의 다른 이름은 `PlayWrightFetcher`입니다.)

#### AI 연동 및 MCP 서버 {#v0.3-ai-integration-mcp-server}
- **기본 제공 MCP 서버**: AI로 웹 스크래핑을 돕는 Model Context Protocol 서버입니다.
- **강력한 도구 6개**: `get`, `bulk_get`, `fetch`, `bulk_fetch`, `stealthy_fetch`, `bulk_stealthy_fetch`
- **스마트 콘텐츠 추출**: 웹페이지나 요소를 Markdown 또는 HTML로 변환하거나 정리된 텍스트만 추출합니다.
- **CSS 선택자 지원**: AI에 콘텐츠를 전달하기 전에 Scrapling 엔진으로 특정 요소를 정확하게 선택합니다.
- **봇 차단 우회**: Cloudflare Turnstile과 다른 보호 장치를 처리합니다.
- **프록시 지원**: 프록시로 익명성을 유지하고 특정 지역에서 접속할 수 있습니다.
- **브라우저 모방**: TLS 지문과 버전에 맞는 실제 브라우저 헤더 등으로 실제 브라우저를 모방합니다.
- **병렬 처리**: 여러 URL을 동시에 스크래핑해 효율을 높입니다.
- [그 밖의 기능...](ai/mcp-server.md)

#### 새로운 대화형 웹 스크래핑 셸 {#v0.3-new-interactive-web-scraping-shell}
- **새로운 셸**: `get`, `post`, `put`, `delete`, `fetch`, `stealthy_fetch` 같은 편리한 단축 함수를 기본 제공하는 맞춤형 IPython 셸입니다.
- **스마트 페이지 관리**: 새 명령인 `page`와 `pages`가 셸에서 보낸 모든 요청의 현재 페이지와 기록을 자동으로 저장합니다.
- **curl 연동**: 브라우저 DevTools의 curl 명령을 `uncurl`과 `curl2fetcher` 함수로 `Fetcher` 요청으로 변환합니다.
- [그 밖의 기능...](cli/interactive-shell.md)

#### 프로그래밍 없이 터미널에서 스크래핑하기 {#v0.3-scrape-from-the-terminal-without-programming}
- **새 추출 명령**: 프로그래밍 없이 터미널에서 스크래핑합니다.
    - `scrapling extract get/post/put/delete` - 간단한 HTTP 요청
    - `scrapling extract fetch` - 동적 콘텐츠 스크래핑
    - `scrapling extract stealthy-fetch` - 봇 차단 우회
- **웹페이지를 다운로드**하고 콘텐츠를 파일에 저장합니다.
- **HTML을 Markdown처럼 읽기 쉬운 형식으로 변환**하거나, HTML 그대로 저장하거나, 페이지의 텍스트만 추출합니다.
- **사용자 지정 CSS 선택자를 지원**해 페이지의 특정 부분을 추출할 수 있습니다.
- **HTTP 요청과 브라우저를 통한 가져오기를 처리합니다.**
- **다양한 설정을 지원합니다.** 사용자 지정 헤더, 쿠키, 프록시 등 여러 옵션을 사용할 수 있습니다. 코드에서 쓸 수 있는 거의 모든 옵션을 터미널에서도 쓸 수 있습니다.
- [그 밖의 기능...](cli/extract-commands.md)

### 🔧 기술 개선 {#v0.3-technical-improvements}

#### 성능 개선 {#v0.3-performance-enhancements}
- **Fetcher가 이제 4배 빠릅니다.** 네, 제대로 읽으셨습니다!
- **DynamicFetcher가 이제 약 60% 빠릅니다.** 설정에 따라 훨씬 빨라집니다. 특히 스텔스 모드에서 그렇습니다.
- **StealthyFetcher가 이제 20–30% 빠릅니다.** 새 구조를 사용하고 `Camoufox` Python 인터페이스 대신 자체 구현을 사용하기 시작했습니다.
- 주요 선택 메서드(`find_by_text`, `find_similar`, `find_by_regex`, `relocate` 등)의 **전체 속도가 50%+ 향상됐습니다.** 🚀
- **첫 결과를 반환하는 CSS/XPath 메서드의 속도가 약 10% 향상됐습니다.** `css_first`와 `xpath_first`가 이제 `css`와 `xpath`보다 빠릅니다.
- 콘텐츠 추출에 쓰는 **`get_all_text()` 메서드가 40% 빨라졌습니다.**
- 적응형 기능으로 요소를 다시 찾는 **속도가 20% 향상됐습니다.**
- **탐색 속성 최적화**: `next`, `previous`, `below_elements` 등의 속성이 눈에 띄게 빨라졌습니다.
- **텍스트 정리 작업이 5배 빨라졌습니다.**
- 가져오기 구문을 최적화하고 부가 작업을 줄여 **메모리 효율을 개선했습니다.**
- **⚡ 매우 빠른 가져오기**: 모듈 로딩을 최적화해 시작 시간을 줄였습니다.
- **벤치마크 개선**: 속도 개선으로 Scrapling이 다른 라이브러리와 비교해 이전보다 훨씬 빨라졌습니다. BeautifulSoup보다 1775배, AutoScraper보다 5.1배 빠릅니다. [벤치마크](benchmarks.md)를 확인하세요.

#### 구조, 코드 품질 및 사용 편의 개선 {#v0.3-architecture-code-quality-and-quality-of-life}
- **영구 컨텍스트**: 모든 브라우저 기반 Fetcher가 이제 기본적으로 영구 컨텍스트를 사용합니다. (#64도 해결합니다.)
- **msgspec으로 모든 브라우저 기반 Fetcher의 설정을 빠르게 검증합니다.** 요청을 실행하기 전에 검증하므로 오류를 더 쉽게 찾을 수 있습니다.
- Fetcher가 반환하는 **모든 쿠키**가 이제 해당 Fetcher에서 받는 형식과 일치합니다. 따라서 쿠키를 가져온 뒤 모든 Fetcher와 해당 세션 클래스에 다시 전달할 수 있습니다.
- `ruff`로 전환해 **린트 검사와 서식 지정이 빨라졌습니다.**
- **현대적인 빌드 시스템**: setup.py에서 pyproject.toml로 전환했습니다. 📦
- **GitHub Actions와 워크플로를 개선**해 개발과 테스트를 더 원활하게 진행할 수 있습니다.
- **🎨 타입 힌트 개선**: 최신 Python 표준으로 모든 타입을 표시해 IDE 지원과 안정성을 높였습니다.
- **더 깔끔한 코드**: 사용하지 않는 코드를 제거하고 핵심 함수를 최적화했습니다. 🧹
- **🚀 하위 호환성**: 이전 코드와의 호환성을 유지하는 단축 기능을 추가했습니다.

### 호환성에 영향을 주는 변경 사항 {#v0.3-breaking-changes}

#### 최소 Python 버전 {#v0.3-minimum-python-version}
- **Python 3.10+ 필요**: Python 3.9 이하 버전의 지원을 중단했습니다.

#### 클래스와 메서드 이름 {#v0.3-class-and-method-naming}
특히 새 사용자가 더 쉽게 이해하고 일관되게 사용할 수 있도록 이름을 바꿨습니다.

- **`Adaptor` → `Selector`**: 핵심 파싱 클래스의 이름을 바꿨습니다. 하위 호환성을 위해 `Adaptor`로도 가져올 수 있습니다.
- **`Adaptors` → `Selectors`**: 컬렉션 클래스의 이름을 바꿨습니다. 하위 호환성을 위해 `Adaptors`로도 가져올 수 있습니다.
- **`auto_match` → `adaptive`**: 모든 메서드에서 인수 이름을 바꿨습니다.
- **`adaptor_arguments` → `selector_config`**: 설정 인수의 이름을 바꿨습니다.
- **`automatch_domain` → `adaptive_domain`**: 도메인 인수의 이름을 바꿨습니다.
- **`additional_arguments` → `additional_args`**: 인수 이름을 줄였습니다.
- **⚠️ `text/body` → `content`**: Selector 생성자 인수가 이제 `str`과 `bytes` 형식을 모두 받습니다.
- **`PlayWrightFetcher` → `DynamicFetcher`**: 브라우저 자동화 클래스의 이름을 바꿨습니다. 하위 호환성을 위해 `PlayWrightFetcher`로도 가져올 수 있습니다.
- **DynamicFetcher에서 NSTBrowser 로직과 인수를 제거했습니다.** 이제 이 로직을 남겨둘 이유가 없기 때문입니다.
- **StealthyFetcher의 headless 인수에 더 이상 'virtual'을 전달할 수 없습니다.** 이제 Camoufox 라이브러리는 브라우저 설치 경로와 나머지 실행 옵션을 가져오는 용도로만 사용하기 때문입니다.

### 🐛 버그 수정 {#v0.3-bug-fixes}

- `get_all_text`에서 무시하는 태그 안에 중첩된 자식 요소를 세는 방식을 수정했습니다. (#61)
- Python 실행 파일 경로에 공백이 있으면 설치에 문제가 생기는 오류를 수정했습니다. (#57)
- 적응형 기능을 켰을 때 저장소의 재귀 처리에서 생기는 스레드 문제를 해결했습니다.
- `FetcherSession`에 Sentinel 패턴을 사용해 인수 우선순위 문제를 수정했습니다.
- `StealthyFetcher`의 프록시 타입 처리 문제를 해결했습니다.
- `referer`와 `google_search` 인수의 충돌을 수정했습니다.
- 비동기 스텔스 스크립트 삽입 문제를 수정했습니다.

## [v0.2.99](https://github.com/D4Vinci/Scrapling/releases/tag/v0.2.99) - 2025-04-08 {#v0.2.99}

**Scrapling의 기능을 온전히 사용하려면 꼭 필요한 업데이트입니다.**

### 변경 사항 {#v0.2.99-what-s-changed}
#### 전체 문서를 담은 새 웹사이트 {#v0.2.99-new-full-documentation-website}
- 드디어 완성했습니다. 😄 [여기](index.md)에서 확인하세요.
#### Fetcher 가져오기 방식 통일 {#v0.2.99-unified-import-logic-for-fetchers}
- 이제 `from scrapling.fetchers import Fetcher, AsyncFetcher, StealthyFetcher, PlayWrightFetcher`로 모든 Fetcher를 가져온 뒤, 객체를 만들지 않고 `page = Fetcher.get(...)`처럼 바로 사용할 수 있습니다.<br/> 기존의 `from scrapling.defaults import Fetcher, AsyncFetcher, StealthyFetcher, PlayWrightFetcher`를 대체합니다.
#### 호환성에 영향을 주는 변경: automatch가 이제 기본적으로 꺼집니다 {#v0.2.99-breaking-change-automatch-is-now-turned-off-by-default}
- Fetcher에서 automatch를 켜거나 다른 파싱 옵션을 설정하는 새 방식을 추가했습니다. 자세한 내용은 [문서 페이지](fetching/choosing.md#parser-configuration-in-all-fetchers)를 참고하세요.
>  하위 호환성을 위해 기존 가져오기 구문과 로직도 경고와 함께 계속 사용할 수 있습니다.
#### Fetcher에 새 옵션 추가 {#v0.2.99-new-options-added-to-fetchers}
- `StealthyFetcher`와 `PlayWrightFetcher` 모두 페이지를 가져올 때 쓰는 새 인수 `wait`를 지원합니다. 페이지를 닫고 응답을 반환하기 전에 지정한 시간(밀리초)만큼 기다립니다.
- 이제 `StealthyFetcher`의 `fetch`와 `async_fetch` 메서드가 `additional_arguments` 인수를 지원합니다. Camoufox에 추가 설정으로 전달하며 Scrapling 설정보다 우선합니다. (#54)
#### 버그 수정 {#v0.2.99-bugs-squashed}
- `async_fetch`에서 리디렉션을 처리하는 버그를 수정했습니다. `StealthyFetcher`와 `PlayWrightFetcher` 클래스 모두에 해당합니다.

**_모든 응원과 기부에 감사드립니다!_**

## [v0.2.98](https://github.com/D4Vinci/Scrapling/releases/tag/v0.2.98) - 2025-03-17 {#v0.2.98}

**Scrapling의 기능을 온전히 사용하려면 꼭 필요한 업데이트입니다.**

### 변경 사항 {#v0.2.98-what-s-changed}
#### 다양한 메모리 사용량 및 속도 최적화 {#v0.2.98-various-memory-usage-and-speed-optimizations}
- 모든 선택 메서드의 메모리 사용량이 이전의 약 40%로 줄었고 속도도 조금 빨라졌습니다.
- 라이브러리의 모든 하위 모듈에 지연 로딩을 적용해 사용하는 부분만 로드합니다. 예를 들면 다음과 같습니다.
업데이트 전에는 `from scrapling import Adaptor`를 실행하면 모든 Fetcher 등도 함께 로드되어 RAM을 `30-40mb` 사용했습니다. 이제는 `~1.2mb`만 사용합니다.
- 지난 업데이트에서는 큰 요청 풀을 사용할 때 메모리 사용량을 이전의 약 32%로 줄였습니다. 이번에는 캐시를 더 조정해 그보다 적게 사용합니다.
- 파서의 전체 속도가 2-5% 정도 향상됐습니다.

**_모든 응원과 기부에 감사드립니다!_**

## [v0.2.97](https://github.com/D4Vinci/Scrapling/releases/tag/v0.2.97) - 2025-03-15 {#v0.2.97}

**Scrapling의 기능을 온전히 사용하려면 꼭 필요한 업데이트입니다.**

### 변경 사항 {#v0.2.97-what-s-changed}
#### 모든 Fetcher의 메모리 사용량 감소 및 소폭 속도 향상 {#v0.2.97-lower-memory-usage-and-small-speed-increase-across-all-fetchers}
- 라이브러리 전반에 캐시 크기 제한을 새로 적용했습니다. 많은 요청이나 작업을 처리할 때 메모리 사용량이 눈에 띄게 줄어듭니다.
- Fetcher 코드의 많은 부분을 정리해 유지보수를 쉽게 하고 속도를 조금 높였습니다.

#### 버그 수정 {#v0.2.97-bugs-fixed}
- `TextHandler`만 가져와 문자열이 아닌 값을 전달하면 빈 문자열로 바뀌던 버그를 수정했습니다. 이제 `TextHandler`에 전달한 값은 먼저 문자열로 바뀐 다음 `TextHandler`로 변환됩니다. 어떤 값이든 이 과정을 거칩니다. `TextHandler`는 이름 그대로 문자열만 다루는 클래스입니다! (#45)
- 대부분의 AsyncFetcher 메서드에서 `retries` 인수가 반영되지 않던 버그를 수정했습니다.

#### 기타 {#v0.2.97-miscellaneous}
- 모든 Fetcher에서 대부분의 인수에 대한 타입 힌트를 더 명확하고 정확하게 바꿨습니다.

**_모든 응원과 기부에 감사드립니다!_**

## [v0.2.96](https://github.com/D4Vinci/Scrapling/releases/tag/v0.2.96) - 2025-03-05 {#v0.2.96}

**Scrapling의 기능을 온전히 사용하려면 꼭 필요한 업데이트입니다.**

### 변경 사항 {#v0.2.96-what-s-changed}
1. `-f` 옵션을 `scrapling install`에 추가해 브라우저 의존 패키지를 강제로 다시 설치할 수 있습니다. 지금 `scrapling install -f`를 실행하는 것을 권장합니다. 새 Camoufox 브라우저 버전으로 `StealthyFetcher`가 훨씬 빨라진 것을 느낄 수 있습니다. :)
2. `TextHandler`를 슬라이싱하면 `TextHandlers`가 반환되던 버그를 수정했습니다. 이제 `TextHandler`를 반환하며 관련 타입 힌트도 수정했습니다. (#41)
3. `scrapling install`이 일부 상황에서 Python 셸을 열던 문제를 수정했습니다!

## [v0.2.95](https://github.com/D4Vinci/Scrapling/releases/tag/v0.2.95) - 2025-02-25 {#v0.2.95}

**Scrapling의 기능을 온전히 사용하려면 꼭 필요한 업데이트입니다.**

### 변경 사항 {#v0.2.95-what-s-changed}
1. `Fetcher`에서 `stealthy_headers` 인수로 생성한 헤더가 `Accept` 등 사용자가 지정한 일부 헤더를 덮어쓰던 버그를 수정했습니다. (#39)
2. 헤더 생성 로직을 조금 개선해 속도도 약간 빨라질 것입니다.

## [v0.2.94](https://github.com/D4Vinci/Scrapling/releases/tag/v0.2.94) - 2025-02-22 {#v0.2.94}

**Scrapling의 기능을 온전히 사용하려면 꼭 필요한 업데이트입니다.**

### 변경 사항 {#v0.2.94-what-s-changed}
1. 리디렉션을 확인할 수 있도록 모든 Fetcher에 `history` 속성을 추가했습니다. (#32)
2. `case_sensitive` 인수의 로직을 모든 `re`/`re_first`에서 수정했습니다. 이 인수를 사용했다면 코드가 다른 결과를 반환할 수 있습니다. (제대로 작동하지 않는 것을 알면서 이슈를 열지 않으셨으니 어쩔 수 없죠. ㅎㅎ)
3. 의존 패키지를 업데이트하고 Camoufox 엔진(StealthyFetcher)에서 `coop`을 다시 켰습니다.

## [v0.2.93](https://github.com/D4Vinci/Scrapling/releases/tag/v0.2.93) - 2025-01-31 {#v0.2.93}

**Scrapling의 기능을 온전히 사용하려면 꼭 필요한 업데이트입니다.**

### 변경 사항 {#v0.2.93-what-s-changed}
1. 파싱 엔진 전체의 반환 타입을 통일했습니다. 항상 `Adaptor`, `Adaptors`, `TextHandler`, `TextHandlers`, `None` 중 하나를 반환하며, CSS 선택자를 조합한 경우처럼 결과가 섞여 있으면 리스트를 반환합니다. 타입을 직접 확인하는 작업을 줄여 코드를 더 편하게 작성하고, 라이브러리를 더 안정적으로 사용하며, 메서드를 항상 이어서 호출할 수 있습니다.
2. 파싱 엔진 대부분, 특히 `Adaptor` 클래스를 더 깔끔하고 빠르게 정리했습니다. 거의 모든 메서드와 속성, 특히 검색 메서드의 속도가 5-40% 향상됐습니다. 일부 메서드는 더 크게 빨라졌습니다. `find_by_regex`는 약 60% 빨라졌습니다! automatch 기능도 약 5% 빨라졌습니다.
3. `find_all`/`find` 메서드가 전달받은 필터를 어떤 때는 OR로, 어떤 때는 AND로 적용하던 로직 버그를 수정했습니다. 이제 반환되는 모든 요소는 전달한 모든 필터를 만족해야 합니다.
4. 정규식 관련 메서드가 모두 `TextHandler`/`TextHandlers`를 반환해 메서드를 쉽게 이어서 호출할 수 있습니다.
5. **새로운** `below_elements` 속성을 추가했습니다. DOM 트리에서 현재 요소 아래에 있는 모든 요소를 담은 `Adaptors` 객체를 반환합니다.
6. HTML 소스를 문자열로 반환하던 모든 메서드와 속성이 이제 `TextHandler`로 반환합니다. 결과에 정규식을 쉽게 적용하는 등의 작업을 할 수 있습니다.
7. StealthyFetcher가 조금 더 빨라졌고 탐지도 더 잘 피합니다. **Cloudflare Turnstile**처럼 iframe 안에 있는 CAPTCHA도 클릭할 수 있습니다.
8. 라이브러리의 거의 절반에서 자동 완성과 타입 힌트를 크게 개선했습니다. 특히 `Adaptor`, `TextHandler`, `TextHandlers`를 개선했습니다.
9. `TextHandler`를 슬라이싱하거나 인덱스로 접근하거나 `split` 메서드를 쓰면 이제 다른 `TextHandler`를 반환합니다. 표준 Python 문자열은 반환하지 않습니다. 거의 모든 표준 문자열 연산과 메서드가 일반 문자열 대신 다른 `Texthandler`를 반환하므로 메서드와 함수를 항상 이어서 호출할 수 있습니다.
10. 작은 버그와 오타를 수정했습니다. 예를 들어 Fetcher의 async_put이 put 요청 대신 post 요청을 보내고 있었습니다. 😶‍🌫️
11. 문서 웹사이트를 완성하기 전에 README를 조금 개선했습니다.

원래는 0.3 버전까지 기다리는 동안 작은 업데이트만 하려 했지만, 더 나은 버전으로 만들기로 했습니다.

## [v0.2.92](https://github.com/D4Vinci/Scrapling/releases/tag/v0.2.92) - 2024-12-26 {#v0.2.92}

### 변경 사항 {#v0.2.92-what-s-changed}
- 로드한 페이지에 iframe이 많을 때 브라우저 기반 Fetcher가 반환하는 응답은 이제 더 신뢰할 수 있는 데이터 소스를 사용합니다.
- **`Scrapling` 설치가 더 쉬워졌습니다. pip로 설치한 다음 터미널에서 `scrapling install`을 실행하면 준비가 끝납니다!**
- 파서의 부정확한 타입 힌트를 수정했습니다.

## [v0.2.91](https://github.com/D4Vinci/Scrapling/releases/tag/v0.2.91) - 2024-12-19 {#v0.2.91}

### 변경 사항 {#v0.2.91-what-s-changed}
- 페이지를 가져왔다는 로그가 첫 요청에서만 표시되던 버그를 수정했습니다.
- Playwright API는 기본적으로 페이지를 탐색할 때 `goto` 메서드에 지정한 로드 상태 `["load", "domcontentloaded", "networkidle"]`를 만족하는 첫 응답을 반환합니다. 따라서 Cloudflare처럼 대기 페이지를 거쳐 실제 웹사이트로 이동하면 Playwright는 첫 상태 코드를 반환하며, 이 코드는 403일 수 있습니다. 이번 업데이트에서는 Playwright API를 사용하는 `PlaywrightFetcher`와 `StealthyFetcher` 모두에서 이 문제를 해결했습니다. 이제 결과가 Playwright의 기본 동작에 영향을 받지 않습니다.
- `Fetcher` 클래스에 SOCKS 프록시 지원을 추가했습니다.
- `wait_selector_state` 인수의 타입 힌트를 수정했습니다. 이제 자동 완성에서 실제로 사용할 수 있는 값이 표시됩니다.

## [v0.2.9](https://github.com/D4Vinci/Scrapling/releases/tag/v0.2.9) - 2024-12-16 {#v0.2.9}

### 변경 사항 {#v0.2.9-what-s-changed}
##### 새 기능 {#v0.2.9-new-features}
1. **오랫동안 기다려온** Scrapling의 비동기 지원을 추가했습니다! `AsyncFetcher`는 `Fetcher`의 비동기 버전입니다. `StealthyFetcher`와 `PlayWrightFetcher` 모두 같은 옵션을 지원하는 새 메서드 `async_fetch`를 제공합니다.

```python
>> from scrapling import StealthyFetcher
>> page = await StealthyFetcher().async_fetch('https://www.browserscan.net/bot-detection')  # the async version of fetch
>> page.status == 200
True
```

2. `StealthyFetcher` 클래스의 가져오기 메서드에 `geoip` 인수를 추가했습니다. 켜면 IP 주소의 경도, 위도, 시간대, 국가, 로캘을 자동으로 사용하고 WebRTC IP 주소를 위장합니다. 대상 지역의 언어 사용자 분포를 바탕으로 브라우저 언어도 계산하고 위장합니다.
3. `retries` 인수를 `Fetcher`/`AsyncFetcher` 클래스에 추가했습니다. 이제 `httpx`로 보내는 각 요청의 재시도 횟수를 설정할 수 있습니다.
4. `url_join` 메서드를 `Adaptor`와 Fetcher에 추가했습니다. 상대 URL을 현재 URL과 합쳐 완전한 절대 URL을 만듭니다!
5. `keep_cdata` 메서드를 `Adaptor`와 Fetcher에 추가했습니다. 필요할 때 파서가 cdata를 제거하지 않도록 할 수 있습니다.
6. 이제 `Adaptor`/`Response`의 `body` 메서드가 가능하면 원본 HTML 응답을 반환합니다. 라이브러리에서 처리하지 않은 응답입니다.
7. `Response` 클래스에 로깅을 추가했습니다. 이제 Fetcher를 사용하면 받은 응답의 정보를 로그로 확인할 수 있습니다.
예:

   ```python
   >> from scrapling.defaults import Fetcher
   >> Fetcher.get('https://books.toscrape.com/index.html')
   [2024-12-16 13:33:36] INFO: Fetched (200) <GET https://books.toscrape.com/index.html> (referer: https://www.google.com/search?q=toscrape)
   >>
   ```

8. 이제 `TextHandler`에 `.replace()` 같은 표준 문자열 메서드를 사용하면 다른 `TextHandler`를 반환합니다. 이전에는 표준 문자열을 반환했습니다.
9. 라이브러리 전반의 속도를 크게 개선하고 Fetcher 클래스 전체의 탐지 회피 성능도 개선했습니다.
10. `extract_first`\`extract`처럼 원래 객체와 같은 결과를 반환하는 호환용 함수를 추가했습니다. 이 함수들은 Scrapy/Parsel에서 쓰이므로, 필요할 때 그 코드를 Scrapling으로 쉽게 옮기기 위해서만 추가했습니다!
11. 코드의 많은 부분을 정리하고 필요한 곳에 캐시를 적용했습니다. 이제 요청을 한꺼번에 많이 보내면 속도가 크게 빨라집니다.

##### 호환성에 영향을 주는 변경 사항 {#v0.2.9-breaking-changes}
- Python 3.8 지원을 중단했습니다. 주된 이유는 Playwright가 지원을 중단했기 때문이지만, 원래 문제가 많던 버전이기도 합니다.
- 라이브러리 전체에서 `debug` 인수를 제거했습니다. 이제 디버깅 모드로 설정하려면 라이브러리를 가져온 뒤 다음 코드를 실행하세요.

   ```python
   >>> import logging
   >>> logging.getLogger("scrapling").setLevel(logging.DEBUG)
   ```

##### 버그 수정 {#v0.2.9-bugs-squashed}
1. 많은 보호 장치가 WebGL의 활성화 여부를 확인하므로 이제 기본적으로 켜집니다.
2. 문서와 README의 일부 잘못된 내용과 오타를 수정했습니다.

##### 사용 편의 개선 {#v0.2.9-quality-of-life-changes}
1. 모든 로깅을 `scrapling`이라는 로거로 통일해 더 쉽고 깔끔하게 제어할 수 있습니다. 이전에는 루트 로거를 사용했습니다.
2. 테스트 폴더를 더 깔끔하게 구성하고 새 기능의 테스트를 추가했습니다. 모든 테스트를 더 깔끔하게 다시 작성했으며, 더 많은 코드를 확인하도록 테스트를 추가했습니다.
3. 코드의 많은 부분을 더 깔끔하고 유지보수하기 쉽게 정리했습니다.

> 이 변경 사항은 원래 0.3에 넣으려던 내용입니다. 다음 버전까지 시간이 걸릴 것 같아 이번에 넣었습니다. 이제 자세한 설명을 담은 문서 웹사이트를 완성한 뒤 0.3 버전을 작업할 예정입니다.

## [v0.2.8](https://github.com/D4Vinci/Scrapling/releases/tag/v0.2.8) - 2024-11-30 {#v0.2.8}

### 변경 사항 {#v0.2.8-what-s-changed}
- 코드 사용에 꼭 필요한 편의 개선을 하고 기본 README 파일의 오타를 수정한 작은 업데이트입니다. (#20)

## [v0.2.7](https://github.com/D4Vinci/Scrapling/releases/tag/v0.2.7) - 2024-11-26 {#v0.2.7}

### 변경 사항 {#v0.2.7-what-s-changed}
##### 새 기능 {#v0.2.7-new-features}
- 이제 `wait_selector` 인수를 `StealthyFetcher`와 `PlayWrightFetcher` 클래스에서 사용하면, Scrapling이 평소처럼 JS가 완전히 로드되고 실행될 때까지 다시 기다립니다. `network_idle` 인수도 사용했다면 이 과정이 끝난 뒤 해당 상태도 다시 기다립니다. 물론 모든 상태가 이미 충족됐다면 기다리지 않습니다.
- 이제 `StealthyFetcher`에서 `disable_ads` 인수로 광고를 켜거나 끌 수 있습니다. 이 옵션은 기본적으로 켜져 있으며 `ublock origin` 확장 기능을 설치합니다.
- 이제 `PlayWrightFetcher`가 사용하는 로캘을 `locale` 인수로 설정할 수 있습니다. 기본값은 여전히 `en-US`입니다.
- 이제 `Fetcher`로 보내는 기본 요청에 `http://username:password@localhost:8030` 형식의 프록시를 사용할 수 있습니다.
- `PlayWrightFetcher`의 스텔스 모드를 조금 개선했습니다.

##### 버그 수정 및 개선 {#v0.2.7-bugs-squashed-improvements}
1. 이제 `PlayWrightFetcher` 클래스에서 프록시를 켜는 것은 `stealth` 모드의 활성화 여부와 관계없습니다. 알려주신 [@AbdullahY36](https://github.com/AbdullahY36) 님께 감사드립니다.
2. 이제 `ResponseEncoding`이 응답에서 받은 인코딩을 해당 페이지에 사용할 수 있는지 확인합니다. 받은 인코딩에서 오류가 나면 Scrapling은 `utf-8`을 사용합니다.

## [v0.2.6](https://github.com/D4Vinci/Scrapling/releases/tag/v0.2.6) - 2024-11-24 {#v0.2.6}

### 변경 사항 {#v0.2.6-what-s-changed}
##### 새 기능 {#v0.2.6-new-features}
- 이제 `PlayWrightFetcher`는 `real_chrome` 인수를 `PlayWrightFetcher.fetch` 함수에 전달해 실제 브라우저를 바로 사용할 수 있습니다. Chrome이 설치되어 있어야 합니다. Scrapling이 설치된 Chrome을 실행하며 대부분의 옵션을 평소처럼 사용할 수 있습니다. 이전에는 `cdp_url` 인수로만 가능했습니다.
- 실제 브라우저용으로 생성하는 헤더의 버전을 높였습니다.

##### 버그 수정 {#v0.2.6-bugs-squashed}
1. `BrowserForge`가 생성하는 브라우저 헤더의 형식이 오래되어 일부 보호 장치가 Scrapling을 탐지한다는 것을 알게 됐습니다. 이제 `BrowserForge`는 실제 브라우저의 User-Agent를 생성하는 데만 사용합니다.
2. Google의 ReCaptcha가 탐지하므로 이제 `hide_canvas` 인수는 기본적으로 꺼져 있습니다.

## [v0.2.5](https://github.com/D4Vinci/Scrapling/releases/tag/v0.2.5) - 2024-11-23 {#v0.2.5}

### 변경 사항 {#v0.2.5-what-s-changed}

##### 버그 수정 {#v0.2.5-bugs-squashed}
- 'wait_selector' 인수에 맞는 요소가 1개보다 많을 때 생기는 오류를 처리했습니다. `StealthyFetcher`와 `PlayWrightFetcher` 클래스에 해당합니다.
- `content_type` 헤더의 값에 `charset` 같은 매개변수가 있을 때 인코딩 타입이 잘못되던 문제를 수정했습니다. [#12](https://github.com/D4Vinci/Scrapling/issues/12)를 알려주신 @andyfcx 님께 감사드립니다.

##### 사용 편의 개선 {#v0.2.5-quality-of-life}
- 새로운 코드 영역도 확인하도록 테스트를 추가하고 스레드에서 테스트를 실행하게 했습니다.
- Sphinx의 apidoc이나 비슷한 도구에서 제대로 읽을 수 있도록 docstring을 수정했습니다.

##### 새 기여자 {#v0.2.5-new-contributors}
- @andyfcx 님이 [#13 ](https://github.com/D4Vinci/Scrapling/pull/13)에서 처음 기여했습니다.

## [v0.2.4](https://github.com/D4Vinci/Scrapling/releases/tag/v0.2.4) - 2024-11-20 {#v0.2.4}

### 변경 사항 {#v0.2.4-what-s-changed}

##### 버그 수정 {#v0.2.4-bugs-squashed}
- `network_idle` 인수를 사용한 뒤 응답 바이트를 가져올 때 생기는 버그를 수정했습니다. `StealthyFetcher`와 `PlayWrightFetcher` 클래스 모두에 해당합니다. <br/> 이 버그로 다음 오류 메시지가 표시됐습니다.

    ```
    Response.body: Protocol error (Network.getResponseBody): No resource with given identifier found
    ```

- PlayWright API가 응답에 빈 상태 메시지를 반환할 때가 있습니다. 이제 이런 경우 `Scrapling`이 상태 메시지를 직접 생성합니다. `StealthyFetcher`와 `PlayWrightFetcher` 클래스 모두에 해당합니다.

## [v0.2.3](https://github.com/D4Vinci/Scrapling/releases/tag/v0.2.3) - 2024-11-19 {#v0.2.3}

### 변경 사항 {#v0.2.3-what-s-changed}

##### 버그 수정 {#v0.2.3-bugs-squashed}
- pip로 설치하면 PlayWright Fetcher의 스텔스 모드가 전혀 작동하지 않던 버그를 수정했습니다.

## [v0.2.2](https://github.com/D4Vinci/Scrapling/releases/tag/v0.2.2) - 2024-11-16 {#v0.2.2}

### 변경 사항 {#v0.2.2-what-s-changed}
##### 새 기능 {#v0.2.2-new-features}
- 생성되는 `Adaptor` 객체에 인수를 전달하지 않고 기본값을 쓰려면, 이제 다음 가져오기 구문으로 코드를 더 깔끔하게 작성할 수 있습니다.

    ```python
    >> from scrapling.default import Fetcher, StealthyFetcher, PlayWrightFetcher
    >> page = Fetcher.get('https://example.com', stealthy_headers=True)
    ```

    그렇지 않으면 다음처럼 작성합니다.

    ```python
    >> from scrapling import Fetcher, StealthyFetcher, PlayWrightFetcher
    >> page = Fetcher(auto_match=False).get('https://example.com', stealthy_headers=True)
    ```

##### 버그 수정 {#v0.2.2-bugs-squashed}
1. 어제 배포한 v0.2.1 패치에서 `Response` 객체에 생긴 버그를 수정했습니다. 일부 중첩된 선택 및 파싱 작업에서 발생했습니다.

## [v0.2.1](https://github.com/D4Vinci/Scrapling/releases/tag/v0.2.1) - 2024-11-15 {#v0.2.1}

### 변경 사항 {#v0.2.1-what-s-changed}
##### 새 기능 {#v0.2.1-new-features}
1. 이제 모든 Fetcher가 반환하는 `Response` 객체는 `Adaptor` 객체와 같으며, `status`, `reason`, `cookies`, `headers`, `request_headers` 속성만 추가로 있습니다. `cookies`, `headers`, `request_headers`는 항상 `dictionary` 타입입니다. <br/>이제 다음처럼 코드를 작성할 수 있습니다.

    ```python
    >> from scrapling import Fetcher
    >> page = Fetcher().get('https://example.com', stealthy_headers=True)
    >> print(page.status)
    200
    >> products = page.css('.product')
    ```

    이전에는 다음처럼 작성했습니다.

    ```python
    >> from scrapling import Fetcher
    >> fetcher = Fetcher().get('https://example.com', stealthy_headers=True)
    >> print(fetcher.status)
    200
    >> page = fetcher.adaptor
    >> products = page.css('.product')
    ```

    하위 호환성을 위해 `.adaptor` 속성도 계속 작동하도록 남겨두었습니다.

2. 이제 `StealthyFetcher`와 `PlayWrightFetcher` 클래스 모두 가져오기 메서드에 `proxy` 인수를 받습니다. 문자열이나 딕셔너리를 전달할 수 있습니다.
3. 이제 `StealthyFetcher` 클래스에 `os_randomize` 인수가 있습니다. `fetch` 메서드에서 사용합니다. 켜면 Scrapling이 사용할 OS 지문을 무작위로 선택합니다. 기본적으로는 현재 OS와 일치하는 지문을 사용합니다.

##### 버그 수정 {#v0.2.1-bugs-squashed}
1. `Fetcher` 클래스에서 헤더를 전달할 때 생기는 버그를 수정했습니다.
2. Fetcher 유형의 클래스에서 전달한 JSON 응답을 파싱할 때 생기는 버그를 수정했습니다.

##### 사용 편의 개선 {#v0.2.1-quality-of-life-changes}
1. 텍스트 기능은 원래 텍스트를 반환하기 전에 HTML 주석을 제거하려고 했습니다. 하지만 일부 상황에서 오류가 발생했고 코드가 필요 이상으로 복잡해졌습니다. 이제 lxml의 기본 동작으로 되돌렸습니다. **선택자처럼 요소의 텍스트를 사용하는 모든 작업이 조금 빨라집니다.** lxml/parsel/scrapy에서 텍스트가 이상하게 나뉘는 것을 피하려고 텍스트를 반환하기 전에 요소의 HTML 주석을 제거하려면, `keep_comments` 인수를 기본값인 True로 유지하세요.

## [v0.2](https://github.com/D4Vinci/Scrapling/releases/tag/v0.2) - 2024-11-11 {#v0.2}

### 변경 사항 {#v0.2-what-s-changed}
##### 새 기능 {#v0.2-new-features}
1. 3개의 새로운 주요 유형을 갖춘 `Fetchers` 기능을 추가했습니다. 다양한 옵션으로 Scrapling이 페이지를 가져오게 할 수 있습니다!
    - `Fetcher` 클래스는 기본 HTTP 요청에 사용합니다.
    - `StealthyFetcher` 클래스는 [스텔스 기능을 추가한 Firefox](https://github.com/daijro/camoufox)를 사용하는 완전한 스텔스 Fetcher입니다.
    - `PlayWrightFetcher` 클래스는 기본 PlayWright, 제가 만든 스텔스 모드의 PlayWright, CDP를 통한 실제 브라우저, [NSTBrowser](https://app.nstbrowser.io/r/1vO5e5)의 [docker browserless](https://hub.docker.com/r/nstbrowser/browserless)로 브라우저 기반 요청을 보낼 수 있습니다!
2. 페이지에서 마법처럼 요소를 쉽게 찾는 완전히 새로운 `find_all`/`find` 메서드를 추가했습니다!
3. `filter`와 `search` 메서드를 `Adaptors` 클래스에 추가해 `Adaptor` 객체 그룹을 한꺼번에 쉽게 처리할 수 있습니다.
4. 더 편하게 쓸 수 있도록 `css_first`와 `xpath_first` 메서드를 추가했습니다.
5. 새 클래스 타입 `TextHandlers`를 추가했습니다. `TextHandler` 객체를 한꺼번에 처리하는 데 사용하며, `Adaptors` 클래스와 비슷합니다.
6. `generate_full_css_selector`와 `generate_full_xpath_selector` 메서드를 추가했습니다.

##### 버그 수정 {#v0.2-bugs-squashed}
1. 이제 `Adaptors` 클래스의 `re_first`는 내부의 모든 `Adaptor` 객체에서 처음 일치하는 결과를 반환합니다. 이전에는 `re_first`를 모든 `Adaptor` 객체에 호출한 결과를 모아 반환하는 잘못된 로직이 있었습니다.
2. CSS의 `::text` 함수처럼 텍스트 콘텐츠를 선택해 반환하려고 `.css`나 `.xpath` 같은 메서드를 사용하면, 이제 `Adaptor` 객체가 `TextHandlers` 클래스를 반환합니다. 이전처럼 문자열 리스트를 반환하지 않습니다. 따라서 이제 `page.css('something::text').re_first(r'regex_pattern').json()`을 사용할 수 있으며, 기존의 `page.css('something::text')[0].re_first(r'regex_pattern').json()`은 필요하지 않습니다.
3. 이제 `Adaptor`/`Adaptors`의 re/re_first 인수가 `TextHandler`와 일치합니다. `clean_match`와 `case_sensitive` 인수를 사용할 수 있습니다.
4. 이제 `auto_match` 인수는 `Adaptor`를 초기화할 때 기본적으로 켜집니다. 하지만 요소를 선택할 때도 이 기능을 따로 켜야 사용할 수 있습니다. 버그가 아닌 설계상의 결정입니다.
5. Scrapling으로 코드를 작성할 때 자동 완성을 더 편하게 쓸 수 있도록 여러 타입 표기를 수정했습니다.

##### 사용 편의 개선 {#v0.2-quality-of-life-changes}
1. `css_selector`와 `xpath_selector` 메서드의 이름을 `generate_css_selector`와 `generate_xpath_selector`로 바꿨습니다. 의미를 명확하게 하고 코드 작성 중 자동 완성을 방해하지 않도록 했습니다.
2. 기존 코드 대부분을 `core` 하위 패키지로 옮기고 다른 설계도 바꿔 앞으로 더 깔끔하고 쉽게 유지보수할 수 있게 했습니다.
3. 테스트 폴더를 더 깔끔하게 구성하고 새 기능의 테스트를 추가했습니다. 이제 GitHub에서 tox 환경을 캐시하므로 커밋마다 실행하는 자동 테스트가 더 빨라집니다.

## [v0.1.2](https://github.com/D4Vinci/Scrapling/releases/tag/v0.1.2) - 2024-10-16 {#v0.1.2}

**변경 기록**:

- `keep_comments` 인수가 의도대로 작동하지 않던 버그를 수정했습니다.
- Lxml 특유의 동작을 피하도록 텍스트 함수를 수정했습니다. 이제 텍스트를 추출하기 전에 요소의 HTML 주석을 자동으로 제거합니다. 예를 들면 다음과 같습니다.

    ```python
    >>> page = Adaptor('<span>CONDITION: <!-- -->Excellent</span>', keep_comments=True)
    >>> page.css('span::text')
    ['CONDITION: ', 'Excellent']
    ```

    이전에는 Lxml의 기본 동작 때문에 위와 같은 결과가 나왔지만, 이제는 전체 텍스트 'CONDITION: Excellent'를 반환합니다.
    parsel\scrapy에서도 알려진 동작이라 여기서 처리하고자 했습니다.

- `pip uninstall scrapling` 같은 명령을 실행해도 라이브러리가 만든 SQLite DB 파일이 삭제되지 않던 버그를 수정했습니다.

## [v0.1.1](https://github.com/D4Vinci/Scrapling/releases/tag/v0.1.1) - 2024-10-14 {#v0.1.1}

작은 수정 사항

## [v0.1](https://github.com/D4Vinci/Scrapling/releases/tag/v0.1) - 2024-10-13 {#v0.1}

**전체 변경 기록**: <https://github.com/D4Vinci/Scrapling/commits/v0.1>
