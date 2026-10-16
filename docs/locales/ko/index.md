---
title: "Scrapling: Python 웹 스크래핑 프레임워크"
description: "Scrapling: 현대적인 웹을 간편하게 스크래핑하세요!"
---

<style>
.md-typeset h1 {
  display: none;
}
[data-md-color-scheme="default"] .only-dark { display: none; }
[data-md-color-scheme="slate"] .only-light { display: none; }
</style>

<br/>
<div align="center">
    <a href="index.html" alt="표지 이미지">
        <img alt="Scrapling" src="assets/cover_light.svg" class="only-light">
        <img alt="Scrapling" src="assets/cover_dark.svg" class="only-dark">
    </a>
</div>

<h2 align="center"><i>현대적인 웹을 간편하게 스크래핑하세요</i></h2><br>

Scrapling은 빠른 HTTP 요청, 스텔스 브라우저, 강력한 파싱, 동시 크롤링을 하나로 묶은 Python 웹 스크래핑 프레임워크입니다.

정적 페이지를 가져오고, JavaScript를 실행하고, 사이트를 조작하고, 사이트가 호출하는 API에서 데이터를 추출하세요. 세션 재사용, 프록시 교체, 자동 재시도, 일시 정지와 재개, 데이터 내보내기를 지원하는 크롤러를 만들 수 있습니다.

Python이나 터미널에서 사용할 수 있으며, MCP 서버와 Agent Skill을 통해 AI 에이전트에서도 사용할 수 있습니다. 몇 개의 필드를 추출하는 작업부터 사이트 전체를 깔끔한 Markdown 파일로 저장하는 작업까지 지원합니다.

## Scrapling으로 할 수 있는 일 {#what-you-can-do-with-scrapling}

- **[페이지 가져오기와 조작](fetching/choosing.md)**: 빠른 HTTP 요청, 스텔스 브라우저, JavaScript 실행, Cloudflare Turnstile과 Interstitial 처리, 지속 세션, 백그라운드 API 응답 기록.
- **[파싱과 데이터 추출](parsing/selection.md)**: CSS, XPath, 텍스트와 정규식 검색, 페이지가 바뀐 뒤에도 요소 추적, 비슷한 요소 찾기, 깔끔한 Markdown 출력.
- **[크롤링과 내보내기](spiders/getting-started.md)**: 동시 크롤링, 프록시 교체, 재시도, AutoThrottle, 일시 정지와 재개, 스트리밍, 바로 쓸 수 있는 템플릿, JSON·JSONL·CSV·XML 내보내기.
- **[AI나 터미널에서 스크래핑](ai/mcp-server.md)**: AI 에이전트가 사이트를 탐색하고 데이터를 추출하는 MCP 서버, Agent Skill, CLI 명령어, 대화형 셸.

한 페이지부터 시작하세요:

```python
from scrapling.fetchers import Fetcher

page = Fetcher.get('https://quotes.toscrape.com/')
quotes = page.css('.quote .text::text').getall()
print(quotes)
```

스파이더로 여러 페이지를 수집할 수도 있습니다:

```python
from scrapling.spiders import Spider, Response

class QuotesSpider(Spider):
    name = "quotes"
    start_urls = ["https://quotes.toscrape.com/"]

    async def parse(self, response: Response):
        for quote in response.css('.quote'):
            yield {
                "text": quote.css('.text::text').get(),
                "author": quote.css('.author::text').get(),
            }

result = QuotesSpider().start()
print(len(result.items))
result.items.to_json("quotes.json")
```

이 코드는 `10`을 출력하고 명언과 저자를 `quotes.json`에 저장합니다.

## 주요 후원사 {#top-sponsors}

--8<-- "sponsors.html"

<i><sub>여기에 광고를 올리고 싶으신가요? [여기](https://github.com/sponsors/D4Vinci)에서 요금제를 선택하고 다른 혜택도 받아 보세요!</sub></i>

## 주요 기능 {#key-features}

### 스파이더: 본격적인 크롤링 프레임워크 {#spiders-a-full-crawling-framework}
- 🕷️ **Scrapy와 비슷한 Spider API**: `start_urls`, 비동기 `parse` 콜백, `Request`/`Response` 객체로 스파이더를 정의합니다.
- ⚡ **동시 크롤링**: 동시에 처리할 요청 수, 도메인별 제한, 다운로드 사이의 대기 시간을 설정합니다.
- 🔄 **여러 세션 지원**: 한 스파이더에서 HTTP 요청과 스텔스 헤드리스 브라우저를 같은 방식으로 사용합니다. 세션 ID로 각 요청을 보낼 세션을 고릅니다.
- 💾 **일시 정지와 재개**: `crawldir`로 대기 중인 요청과 방문한 URL을 저장합니다. Ctrl+C로 안전하게 멈춘 뒤 같은 폴더로 다시 시작하면 이어서 실행됩니다.
- 📡 **스트리밍**: `async for item in spider.stream()`으로 추출한 항목을 바로 받고 실시간 통계를 확인합니다. 화면 표시, 데이터 처리, 긴 크롤링 작업에 적합합니다.
- 🛡️ **차단 감지**: 차단된 요청을 자동으로 감지하고 재시도합니다. 처리 방식도 바꿀 수 있습니다.
- 🚦 **AutoThrottle**: 대기 시간을 직접 추측할 필요가 없습니다. 스파이더가 응답 속도에 맞춰 도메인별 대기 시간을 조절합니다. 차단이나 요청 빈도 제한이 시작되면 두 배로 늘리거나 `Retry-After`가 지정한 시간만큼 기다리고, 문제가 사라지면 다시 속도를 높입니다.
- 🤖 **robots.txt 준수**: `robots_txt_obey`를 켜면 `Disallow`, `Crawl-delay`, `Request-rate` 규칙을 따릅니다. 규칙은 도메인별로 캐시합니다.
- 🧪 **개발 모드**: 첫 실행에서 응답을 디스크에 저장하고 다음 실행부터 다시 사용합니다. 서버에 다시 요청하지 않고 `parse()`를 수정하며 시험할 수 있습니다.
- 🧩 **바로 쓰는 스파이더 템플릿**: `CrawlSpider`는 규칙에 따라 링크를 따라가고, `SitemapSpider`는 sitemap과 robots.txt를 사용합니다. `XMLFeedSpider`/`CSVFeedSpider`는 XML·RSS·CSV 피드를 읽습니다. `ShopifySpider`는 공개 Shopify 스토어에서 상품을 수집하며, 상품 옵션 조합마다 한 항목을 만듭니다.
- 🔗 **링크 추출**: `LinkExtractor`는 허용·제외 패턴, 도메인 필터, CSS·XPath 범위 지정, 확장자 필터, URL 정규화를 지원합니다. 템플릿 안에서 또는 단독으로 사용할 수 있습니다.
- 📦 **데이터 내보내기**: 훅과 자체 처리 과정으로 결과를 저장하거나 내장 JSON·JSONL·CSV·XML 기능을 사용하세요. `result.items.to_json()`, `to_jsonl()`, `to_csv()`, `to_xml()`을 호출하면 됩니다.

### 세션을 사용한 사이트 가져오기 {#advanced-websites-fetching-with-session-support}
- **HTTP 요청**: `Fetcher`로 빠르고 탐지하기 어려운 HTTP 요청을 보냅니다. 브라우저의 TLS 지문과 헤더를 흉내 내고 HTTP/3를 사용할 수 있습니다.
- **동적 페이지**: `StealthyFetcher`로 브라우저를 자동 조작하며 동적 사이트를 가져옵니다. Playwright의 Chromium과 Google Chrome을 지원합니다.
- **봇 차단 우회**: `StealthyFetcher`는 자동화 흔적을 숨기고 브라우저 지문을 위장합니다. 모든 유형의 Cloudflare Turnstile과 Interstitial 검사를 자동으로 통과할 수 있습니다.
- **세션 관리**: `FetcherSession`과 `StealthySession`은 요청 사이에 쿠키와 상태를 유지합니다.
- **프록시 교체**: `ProxyRotator`는 모든 세션에서 프록시를 순서대로 또는 정한 규칙에 따라 교체합니다. 요청마다 다른 프록시를 지정할 수도 있습니다.
- **도메인과 광고 차단**: 특정 도메인과 하위 도메인으로 보내는 요청을 막을 수 있습니다. 브라우저 Fetcher의 광고 차단 기능은 약 3,500개의 광고·추적 도메인을 차단합니다.
- **DNS 유출 방지**: DNS-over-HTTPS를 켜면 Cloudflare의 DoH를 통해 DNS를 조회합니다. 프록시를 쓸 때 DNS가 새어 나가는 것을 막습니다.
- **원격 브라우저**: `cdp_url`로 CDP를 통해 이미 실행 중인 브라우저에 연결합니다. 같은 컴퓨터, 다른 서버, 브라우저 제공 서비스 어디에서든 사용할 수 있습니다. `executable_path`로 직접 만든 Chromium을 브라우저 Fetcher에 지정할 수도 있습니다.
- **백그라운드 API 응답 기록**: 브라우저 세션에서 `record_requests=True`를 켜고 `session.network.search(limit=None)`으로 저장된 응답을 검색하세요. 요청을 다시 보내지 않고 여러 페이지에서 발생한 API 데이터와 HTTP 오류를 읽을 수 있습니다. 기록에는 크기 제한이 있으며 텍스트 응답 본문을 저장합니다.
- **비동기 지원**: 모든 Fetcher에서 비동기 호출을 지원하며, 전용 비동기 세션 클래스도 제공합니다.

### 파싱과 데이터 추출 {#parsing-and-data-extraction}
- 🔄 **요소 추적**: 사이트가 바뀌어도 유사도 알고리즘으로 요소를 다시 찾습니다.
- 🎯 **유연한 선택**: CSS, XPath, 필터, 텍스트, 정규식 등 여러 방법을 사용할 수 있습니다.
- 🔍 **비슷한 요소 찾기**: 이미 찾은 요소와 비슷한 요소를 자동으로 찾습니다.

### AI 기능 {#ai-features}
- 🤖 **MCP 서버**: Claude나 Cursor 같은 AI 챗봇과 에이전트가 Scrapling으로 데이터를 수집합니다. HTTP 요청, 브라우저 조작, 스크린샷, 저장된 로그인 상태, 백그라운드 API 응답을 사용할 수 있습니다. 스텔스 브라우저와 도구를 통해 충분한 능력을 가진 AI 모델이 작업 중 마주치는 모든 CAPTCHA를 처리하도록 돕습니다. Cloudflare 처리 기능도 내장되어 있습니다. 모델에 보내는 내용을 줄이고 광고를 차단하며 프롬프트 인젝션으로부터 모델을 보호합니다. CDP 원격 브라우저와 인증을 지원하는 HTTP 연결도 제공합니다. ([데모 영상](https://www.youtube.com/watch?v=qyFk3ZNwOxE))
- 🧠 **Agent Skill**: 설치해서 쓰는 [Agent Skill](ai/agent-skill.md)이 코딩 에이전트에 라이브러리 전체 사용법을 알려 줍니다. 에이전트가 추측 대신 현재 API에 맞는 코드를 작성하도록 돕습니다.
- 📚 **RAG용 Markdown**: 한 줄(`page.markdown()`)로 페이지를 정리하고 위험한 내용을 제거해 LLM용 Markdown으로 만듭니다. `ContentSpider` 템플릿으로 사이트 전체를 Markdown 파일로 저장할 수도 있습니다. 이 과정에는 LLM이 필요하지 않습니다. ([문서](ai/building-rag-systems.md))

### 빠르고 실무에서 검증된 구조 {#high-performance-battle-tested-architecture}
- 🚀 **빠른 처리**: 최적화를 통해 대부분의 Python 스크래핑 라이브러리보다 빠르게 동작합니다.
- 🔋 **적은 메모리 사용**: 최적화한 자료 구조를 사용하고 필요한 시점에만 데이터를 불러옵니다.
- ⚡ **빠른 JSON 변환**: 표준 라이브러리보다 10배 빠릅니다.
- 🏗️ **실무 검증**: 테스트 커버리지 92%와 전체 코드의 타입 힌트를 갖췄습니다. 지난 1년 동안 수백 명이 매일 데이터를 수집하는 데 사용했습니다.

### 개발자를 위한 편리한 도구 {#developerweb-scraper-friendly-experience}
- 🎯 **대화형 셸**: Scrapling을 통합한 IPython 셸을 추가할 수 있습니다. 단축 명령과 도구로 스크립트를 빠르게 개발하세요. curl 요청을 Scrapling 요청으로 바꾸고 결과를 브라우저에서 볼 수 있습니다.
- 🚀 **터미널에서 바로 사용**: 코드를 한 줄도 쓰지 않고 URL에서 데이터를 가져올 수 있습니다!
- 🛠️ **DOM 탐색**: 부모, 형제, 자식 요소로 이동하는 메서드를 제공합니다.
- 🧬 **텍스트 처리**: 정규식, 텍스트 정리, 빠른 문자열 연산을 사용할 수 있습니다.
- 📝 **선택자 생성**: 어떤 요소든 안정적인 CSS·XPath 선택자를 만들 수 있습니다.
- 🔌 **익숙한 API**: Scrapy와 BeautifulSoup에 익숙하다면 쉽게 사용할 수 있습니다. Scrapy·Parsel과 같은 가상 요소를 지원합니다.
- 🤝 **Scrapy 통합**: 콜백에 `scrapling_response` 데코레이터를 붙이면 이미 가져온 응답을 Scrapling 파서로 처리할 수 있습니다. 코드를 새로 작성할 필요가 없습니다.
- 📘 **전체 타입 힌트**: 편집기 지원과 코드 자동 완성을 돕습니다. 코드가 바뀔 때마다 **PyRight**와 **MyPy**가 전체 코드를 자동으로 검사합니다.
- 🔋 **바로 쓰는 Docker 이미지**: 새 버전마다 모든 브라우저가 포함된 Docker 이미지를 자동으로 만들고 배포합니다.


## GitHub 스타 기록 {#star-history}
Scrapling의 GitHub 스타 수는 공개 이후 꾸준히 늘고 있습니다. 아래 그래프에서 확인하세요.

<div id="chartContainer">
  <a href="https://github.com/D4Vinci/Scrapling">
    <img id="chartImage" alt="GitHub 스타 수 변화 그래프" loading="lazy" src="https://api.star-history.com/svg?repos=D4Vinci/Scrapling&type=Date" height="400"/>
  </a>
</div>

<script>
const observer = new MutationObserver((mutations) => {
  mutations.forEach((mutation) => {
    if (mutation.attributeName === 'data-md-color-media') {
      const colorMedia = document.body.getAttribute('data-md-color-media');
      const isDarkScheme = document.body.getAttribute('data-md-color-scheme') === 'slate';
      const chartImg = document.querySelector('#chartImage');
      const baseUrl = 'https://api.star-history.com/svg?repos=D4Vinci/Scrapling&type=Date';
      
      if (colorMedia === '(prefers-color-scheme)' ? isDarkScheme : colorMedia.includes('dark')) {
        chartImg.src = `${baseUrl}&theme=dark`;
      } else {
        chartImg.src = baseUrl;
      }
    }
  });
});

observer.observe(document.body, {
  attributes: true,
  attributeFilter: ['data-md-color-media', 'data-md-color-scheme']
});
</script>


## 설치 {#installation}
Scrapling에는 Python 3.10 이상이 필요합니다:

```bash
pip install scrapling
```

!!! warning "주의"

    이 명령은 파서와 필요한 패키지만 설치합니다. Fetcher나 명령줄 도구는 포함되지 않습니다. 따라서 위 예제처럼 `scrapling.fetchers`나 `scrapling.spiders`에서 가져오면 `ModuleNotFoundError`가 발생합니다. Fetcher나 스파이더를 사용하려면 먼저 아래 방법으로 Fetcher에 필요한 패키지를 설치하세요.

### 추가 패키지 {#optional-dependencies}

1. Fetcher, 관련 클래스, 아래 추가 기능을 사용하려면 Fetcher와 브라우저에 필요한 패키지를 설치하세요:
    ```bash
    pip install "scrapling[fetchers]"
    
    scrapling install           # normal install
    scrapling install  --force  # force reinstall
    ```

    모든 브라우저, 필요한 시스템 패키지, 브라우저 지문을 바꾸는 도구를 다운로드합니다.

    명령어 대신 코드에서 설치할 수도 있습니다:
    ```python
    from scrapling.cli import install
    
    install([], standalone_mode=False)          # normal install
    install(["--force"], standalone_mode=False) # force reinstall
    ```

2. 추가 기능:


     - MCP 서버 설치:
       ```bash
       pip install "scrapling[ai]"
       ```
     - [RAG 시스템 만들기](ai/building-rag-systems.md)에 필요한 패키지 설치:
       ```bash
       pip install "scrapling[rag]"
       ```
     - 대화형 셸과 `extract` 명령어 설치:
         ```bash
         pip install "scrapling[shell]"
         ```
     - 모든 기능 설치:
         ```bash
         pip install "scrapling[all]"
         ```
   브라우저 Fetcher를 사용하려면 `scrapling install`을 실행하세요. HTTP 요청에는 브라우저 설치가 필요하지 않습니다.

### Docker {#docker}
모든 추가 기능과 브라우저가 포함된 Docker 이미지를 DockerHub에서 받을 수도 있습니다:
```bash
docker pull pyd4vinci/scrapling
```
또는 GitHub 레지스트리에서 받으세요:
```bash
docker pull ghcr.io/d4vinci/scrapling:latest
```
이 이미지는 저장소의 main 브랜치를 바탕으로 GitHub Actions에서 자동으로 만들고 배포합니다.

## 문서 구성 {#how-the-documentation-is-organized}
Scrapling에는 많은 문서가 있으므로 [Diátaxis 문서 구성 방식](https://diataxis.fr/)을 따르려고 합니다.

## 프로젝트 지원 {#support}

Scrapling이 마음에 든다면 다음 방법으로 개발을 지원해 주세요:

- ⭐ [GitHub 저장소](https://github.com/D4Vinci/Scrapling)에 스타를 눌러 주세요.
- 🚀 [Twitter](https://x.com/Scrapling_dev)를 팔로우하고 [Discord](https://discord.gg/EMgGbDceNQ)에 참여하세요.
- 💝 [프로젝트를 후원하거나 커피 한 잔을 보내 주세요](donate.md). :wink:
- 🐛 [GitHub Issues](https://github.com/D4Vinci/Scrapling/issues)에서 버그를 알리고 기능을 제안하세요.

## 라이선스 {#license}

이 프로젝트는 BSD-3 라이선스로 배포합니다. 자세한 내용은 [LICENSE](https://github.com/D4Vinci/Scrapling/blob/main/LICENSE)를 확인하세요.
