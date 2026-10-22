<!-- mcp-name: io.github.D4Vinci/Scrapling -->

<h1 align="center">
    <a href="https://scrapling.readthedocs.io/ko/latest/">
        <picture>
          <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/docs/assets/cover_dark.svg?sanitize=true">
          <img alt="Scrapling 표지" src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/docs/assets/cover_light.svg?sanitize=true">
        </picture>
    </a>
    <br>
    <small>현대적인 웹을 간편하게 스크래핑하세요</small>
</h1>

<p align="center">
    <a href="https://github.com/D4Vinci/Scrapling/actions/workflows/tests.yml" alt="테스트">
        <img alt="테스트" src="https://github.com/D4Vinci/Scrapling/actions/workflows/tests.yml/badge.svg"></a>
    <a href="https://badge.fury.io/py/Scrapling" alt="PyPI 버전">
        <img alt="PyPI 버전" src="https://badge.fury.io/py/Scrapling.svg"></a>
    <a href="https://hub.docker.com/r/pyd4vinci/scrapling" target="_blank">
        <img alt="Docker 다운로드 수" src="https://img.shields.io/docker/pulls/pyd4vinci/scrapling?labelColor=%20%23FDB062&logo=Docker&labelColor=%20%23528bff"></a>
    <a href="https://clickpy.clickhouse.com/dashboard/scrapling" rel="nofollow"><img src="https://img.shields.io/pypi/dm/scrapling" alt="PyPI 패키지 다운로드 수"></a>
    <a href="https://scrapling.readthedocs.io/ko/latest/ai/agent-skill.html" alt="AI 에이전트용 Skill">
        <img alt="Agent Skill 배지" src="https://img.shields.io/badge/Skill-black?style=flat&label=Agent&link=https%3A%2F%2Fscrapling.readthedocs.io%2Fko%2Flatest%2Fai%2Fagent-skill.html"></a>
    <a href="https://clawhub.ai/D4Vinci/scrapling-official" alt="OpenClaw용 Skill">
        <img alt="OpenClaw용 Skill" src="https://img.shields.io/badge/Clawhub-darkred?style=flat&label=OpenClaw&link=https%3A%2F%2Fclawhub.ai%2FD4Vinci%2Fscrapling-official"></a>
    <br/>
    <a href="https://discord.gg/EMgGbDceNQ" alt="Discord" target="_blank">
      <img alt="Discord" src="https://img.shields.io/discord/1360786381042880532?style=social&logo=discord&link=https%3A%2F%2Fdiscord.gg%2FEMgGbDceNQ">
    </a>
    <a href="https://x.com/Scrapling_dev" alt="X(구 Twitter)">
      <img alt="X(구 Twitter) 팔로우" src="https://img.shields.io/twitter/follow/Scrapling_dev?style=social&logo=x&link=https%3A%2F%2Fx.com%2FScrapling_dev">
    </a>
    <br/>
    <a href="https://pypi.org/project/scrapling/" alt="지원하는 Python 버전">
        <img alt="지원하는 Python 버전" src="https://img.shields.io/pypi/pyversions/scrapling.svg"></a>
</p>

<p align="center">
    <a href="https://scrapling.readthedocs.io/ko/latest/parsing/selection.html"><strong>요소 찾기</strong></a>
    &middot;
    <a href="https://scrapling.readthedocs.io/ko/latest/fetching/choosing.html"><strong>Fetcher 선택 가이드</strong></a>
    &middot;
    <a href="https://scrapling.readthedocs.io/ko/latest/spiders/architecture.html"><strong>Spider</strong></a>
    &middot;
    <a href="https://scrapling.readthedocs.io/ko/latest/spiders/proxy-blocking.html"><strong>프록시 교체</strong></a>
    &middot;
    <a href="https://scrapling.readthedocs.io/ko/latest/cli/overview.html"><strong>CLI</strong></a>
    &middot;
    <a href="https://scrapling.readthedocs.io/ko/latest/ai/mcp-server.html"><strong>MCP 서버</strong></a>
</p>

Scrapling은 빠른 HTTP 요청, 스텔스 브라우저, 강력한 파싱, 동시 크롤링을 하나로 묶은 Python 웹 스크래핑 프레임워크입니다.

정적 페이지를 가져오고, JavaScript를 실행하고, 사이트를 조작하고, 사이트가 호출하는 API에서 데이터를 추출하세요. 세션 재사용, 프록시 교체, 자동 재시도, 일시 정지와 재개, 데이터 내보내기를 지원하는 크롤러를 만들 수 있습니다.

Python이나 터미널에서 사용할 수 있으며, MCP 서버와 Agent Skill을 통해 AI 에이전트에서도 사용할 수 있습니다. 몇 개의 필드를 추출하는 작업부터 사이트 전체를 깔끔한 Markdown 파일로 저장하는 작업까지 지원합니다.

## Scrapling으로 할 수 있는 일

- **[페이지 가져오기와 조작](https://scrapling.readthedocs.io/ko/latest/fetching/choosing.html)**: 빠른 HTTP 요청, 스텔스 브라우저, JavaScript 실행, Cloudflare Turnstile과 Interstitial 처리, 지속 세션, 백그라운드 API 응답 기록.
- **[파싱과 데이터 추출](https://scrapling.readthedocs.io/ko/latest/parsing/selection.html)**: CSS, XPath, 텍스트와 정규식 검색, 페이지가 바뀐 뒤에도 요소 추적, 비슷한 요소 찾기, 깔끔한 Markdown 출력.
- **[크롤링과 내보내기](https://scrapling.readthedocs.io/ko/latest/spiders/getting-started.html)**: 동시 크롤링, 프록시 교체, 재시도, AutoThrottle, 일시 정지와 재개, 스트리밍, 바로 쓸 수 있는 템플릿, JSON·JSONL·CSV·XML 내보내기.
- **[AI나 터미널에서 스크래핑](https://scrapling.readthedocs.io/ko/latest/ai/mcp-server.html)**: AI 에이전트가 사이트를 탐색하고 데이터를 추출하는 MCP 서버, Agent Skill, CLI 명령어, 대화형 셸.

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

<p align="center">
    <a href="https://dataimpulse.com/?utm_source=scrapling&utm_medium=banner&utm_campaign=scrapling" target="_blank" style="display:flex; justify-content:center; padding:4px 0;">
        <img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/DataImpulse.png" alt="At DataImpulse, we specialize in developing custom proxy services for your business. Make requests from anywhere, collect data, and enjoy fast connections with our premium proxies." style="max-height:60px;">
    </a>
</p>

# 플래티넘 스폰서
<table>
  <tr>
    <td width="200">
      <a href="https://go.nodemaven.com/scraplingoctober" target="_blank" title="Proxies with the Highest IP Scores">
        <img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/NodeMaven.jpg" width="240" height="100">
      </a>
    </td>
    <td>
    <a href="https://go.nodemaven.com/scraplingoctober" target="_blank">NodeMaven</a> - 웹 스크래핑과 자동화를 위한 가장 효율적인 프록시 제공업체로, 시장에서 가장 높은 품질의 IP를 제공합니다. 코드 SCRAPLING35를 사용하면 35% 할인을 받을 수 있습니다.
    </td>
  </tr>
  <tr>
    <td width="200">
      <a href="https://hypersolutions.co/?utm_source=github&utm_medium=readme&utm_campaign=scrapling" target="_blank" title="Bot Protection Bypass API for Akamai, DataDome, Incapsula & Kasada">
        <img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/HyperSolutions.png">
      </a>
    </td>
    <td> Scrapling은 Cloudflare Turnstile을 처리합니다. 기업용 보호 기능을 우회해야 한다면, <a href="https://hypersolutions.co?utm_source=github&utm_medium=readme&utm_campaign=scrapling">
        <b>Hyper Solutions</b>
      </a>가 <b>Akamai</b>, <b>DataDome</b>, <b>Kasada</b>, <b>Incapsula</b>용 유효한 안티봇 토큰을 생성하는 API 엔드포인트를 제공합니다. 간단한 API 호출만으로 사용할 수 있으며 브라우저 자동화는 필요 없습니다. </td>
  </tr>
  <tr>
    <td width="200">
      <a href="https://evomi.com?utm_source=github&utm_medium=banner&utm_campaign=d4vinci-scrapling" target="_blank" title="Evomi is your Swiss Quality Proxy Provider, starting at $0.49/GB">
        <img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/evomi.png">
      </a>
    </td>
    <td>
      <a href="https://evomi.com?utm_source=github&utm_medium=banner&utm_campaign=d4vinci-scrapling">
        <b>Evomi</b>
      </a>: 레지덴셜 프록시를 GB당 $0.49부터 제공합니다. 브라우저 지문을 완전히 위장한 Chromium 기반 스크래핑 브라우저, 레지덴셜 IP, 자동 CAPTCHA 처리, 봇 차단 우회를 지원합니다.</br>
      <b>Scraper API로 번거로움 없이 결과를 얻으세요. MCP 및 N8N 연동도 지원합니다.</b>
    </td>
  </tr>
  <tr>
    <td width="200">
      <a href="https://substack.thewebscraping.club/p/scrapling-hands-on-guide?utm_source=github&utm_medium=repo&utm_campaign=scrapling" target="_blank" title="The #1 newsletter dedicated to Web Scraping">
        <img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/TWSC.png">
      </a>
    </td>
    <td>
    <a href="https://substack.thewebscraping.club/p/scrapling-hands-on-guide?utm_source=github&utm_medium=repo&utm_campaign=scrapling" target="_blank">The Web Scraping Club에서 Scrapling의 전체 리뷰</a>(2025년 11월)를 읽어보세요. 웹 스크래핑 전문 No.1 뉴스레터입니다.
    </td>
  </tr>
  <tr>
    <td width="200">
      <a href="https://www.swiftproxy.net/?ref=D4Vinci" target="_blank" title="Scalable Solutions for Web Data Access">
        <img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/SwiftProxy.png">
      </a>
    </td>
    <td>
    <a href="https://www.swiftproxy.net/?ref=D4Vinci" target="_blank">Swiftproxy</a>는 195개국 이상에서 8천만 개 이상의 IP를 갖춘 확장 가능한 주거용 프록시를 제공하며, 빠르고 안정적인 연결, 자동 프록시 교체, 강력한 차단 방지 기능을 제공합니다. 무료로 체험할 수 있습니다.
    </td>
  </tr>
  <tr>
    <td width="200">
      <a href="https://byteful.com/?utm_source=github&utm_medium=github-sponsor&utm_campaign=scrapling_github_sponsor" target="_blank" title="Ethically sourced residential proxy infrastructure powering web scraping and AI agents">
        <img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/byteful.png">
      </a>
    </td>
    <td>
    <a href="https://byteful.com/?utm_source=github&utm_medium=github-sponsor&utm_campaign=scrapling_github_sponsor" target="_blank">Byteful</a>은 윤리적으로 확보한 주거용, 모바일, ISP 및 데이터센터 프록시와 스크래핑 및 AI 자동화 도구를 제공합니다. 코드 SCRAPLING10을 사용하면 주거용 프록시를 10% 할인받을 수 있습니다.
    </td>
  </tr>
  <tr>
    <td width="200">
      <a href="https://proxylane.dev/?utm_source=scrapling&utm_medium=partnership&utm_campaign=scrapling_platinum_202609&utm_content=github_readme" target="_blank" title="28M+ clean residential IPs for browser automation. No Blocks. No CAPTCHAs. Pay-as-you-Go.">
        <img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/proxylane.png">
      </a>
    </td>
    <td>
    <a href="https://proxylane.dev/?utm_source=scrapling&utm_medium=partnership&utm_campaign=scrapling_platinum_202609&utm_content=github_readme" target="_blank">ProxyLane</a>: 차단과 CAPTCHA를 90% 줄입니다. 대규모 웹 스크래핑을 위한 2,800만 개의 프리미엄 주거용 IP를 제공합니다. 195개 국가를 지원하며 도시, ISP, 우편번호(ZIP)를 지정할 수 있습니다. IP를 유지하거나 바꾸는 세션을 사용할 수 있습니다. 유효 기간이 없는 트래픽을 $2/GB부터 제공합니다. 코드 <strong>SCRAPEANDTAKE</strong>를 사용하면 <em>25% 할인</em>을 받을 수 있습니다.
    </td>
  </tr>
  <tr>
    <td width="200">
      <a href="https://www.lundproxy.com/unlimited-residential-bandwidth.html?utm_source=github&utm_medium=sponsorship&utm_campaign=scrapling&utm_content=banner" target="_blank" title="Unlimited residential traffic, sized only by bandwidth.">
        <img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/lundproxy.png">
      </a>
    </td>
    <td>
    <a href="https://www.lundproxy.com?utm_source=github&utm_medium=sponsorship&utm_campaign=scrapling&utm_content=text" target="_blank">LundProxy</a>: GB당 요금을 내지 않아도 됩니다. 무제한 주거용 프록시 트래픽과 1억 개 이상의 IP를 제공하며 190개 이상의 국가를 지원합니다. 대역폭에 따라 요금을 지불하세요. 50 Mbps 주거용 프록시 무료 체험을 신청하세요.
    </td>
  </tr>
  <tr>
    <td width="200">
      <a href="https://dataimpulse.com/?utm_source=website&utm_medium=github_readme&utm_campaign=scrapling_platinum" target="_blank" title="Buy Pay-as-you-go proxies from $1/GB">
        <img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/DataImpulse_Platinum.png">
      </a>
    </td>
    <td>
    <a href="https://dataimpulse.com/?utm_source=website&utm_medium=github_readme&utm_campaign=scrapling_platinum" target="_blank">DataImpulse</a>에서 $1/GB로 이용하세요. 윤리적으로 확보한 자체 프록시를 제공합니다. 9,000만 개 이상의 IP와 195개 이상의 국가를 지원합니다. 주거용, 데이터센터, 모바일 프록시를 사용할 수 있습니다. 사용량에 따라 결제하므로 구독이 필요 없습니다. 트래픽에 유효 기간이 없습니다.
    </td>
  </tr>
</table>

<i><sub>여기에 광고를 게재하고 싶으신가요? [여기](https://github.com/sponsors/D4Vinci/sponsorships?tier_id=586646)를 클릭하세요</sub></i>
# 스폰서

<!-- sponsors -->

<a href="https://cloro.dev/?utm_source=referral&utm_medium=scrapling" target="_blank" title="The search API for the AI era"><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/cloro.jpg"></a>

<br/>

<a href="https://serpapi.com/?utm_source=scrapling" target="_blank" title="Scrape Google and other search engines with SerpApi"><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/SerpApi.png"></a>
<a href="https://visit.decodo.com/Dy6W0b" target="_blank" title="Try the Most Efficient Residential Proxies for Free"><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/decodo.png"></a>
<a href="https://proxyempire.io/?ref=scrapling&utm_source=github&utm_medium=paid_referral&utm_campaign=open_source_sponsorship&utm_content=scrapling" target="_blank" title="Collect The Data Your Project Needs with the Best Residential Proxies"><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/ProxyEmpire.png"></a>
<a href="https://www.webshare.io/?referral_code=48r2m2cd5uz1" target="_blank" title="The Most Reliable Proxy with Unparalleled Performance"><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/webshare.png"></a>
<a href="https://proxiware.com/?ref=scrapling" target="_blank" title="Collect Any Data. At Any Scale."><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/proxiware.png"></a>


<!-- /sponsors -->

<i><sub>여기에 광고를 게재하고 싶으신가요? [여기](https://github.com/sponsors/D4Vinci)를 클릭하고 원하는 요금제를 선택하세요!</sub></i>

---

## 주요 기능

### 스파이더: 본격적인 크롤링 프레임워크

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

### 세션을 사용한 사이트 가져오기

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

### 파싱과 데이터 추출

- 🔄 **요소 추적**: 사이트가 바뀌어도 유사도 알고리즘으로 요소를 다시 찾습니다.
- 🎯 **유연한 선택**: CSS, XPath, 필터, 텍스트, 정규식 등 여러 방법을 사용할 수 있습니다.
- 🔍 **비슷한 요소 찾기**: 이미 찾은 요소와 비슷한 요소를 자동으로 찾습니다.

### AI 기능

- 🤖 **MCP 서버**: Claude나 Cursor 같은 AI 챗봇과 에이전트가 Scrapling으로 데이터를 수집합니다. HTTP 요청, 브라우저 조작, 스크린샷, 저장된 로그인 상태, 백그라운드 API 응답을 사용할 수 있습니다. 스텔스 브라우저와 도구를 통해 충분한 능력을 가진 AI 모델이 작업 중 마주치는 모든 CAPTCHA를 처리하도록 돕습니다. Cloudflare 처리 기능도 내장되어 있습니다. 모델에 보내는 내용을 줄이고 광고를 차단하며 프롬프트 인젝션으로부터 모델을 보호합니다. CDP 원격 브라우저와 인증을 지원하는 HTTP 연결도 제공합니다. ([데모 영상](https://www.youtube.com/watch?v=qyFk3ZNwOxE))
- 🧠 **Agent Skill**: 설치해서 쓰는 [Agent Skill](https://scrapling.readthedocs.io/ko/latest/ai/agent-skill.html)이 코딩 에이전트에 라이브러리 전체 사용법을 알려 줍니다. 에이전트가 추측 대신 현재 API에 맞는 코드를 작성하도록 돕습니다.
- 📚 **RAG용 Markdown**: 한 줄(`page.markdown()`)로 페이지를 정리하고 위험한 내용을 제거해 LLM용 Markdown으로 만듭니다. `ContentSpider` 템플릿으로 사이트 전체를 Markdown 파일로 저장할 수도 있습니다. 이 과정에는 LLM이 필요하지 않습니다. ([문서](https://scrapling.readthedocs.io/ko/latest/ai/building-rag-systems.html))

### 빠르고 실무에서 검증된 구조

- 🚀 **빠른 처리**: 최적화를 통해 대부분의 Python 스크래핑 라이브러리보다 빠르게 동작합니다.
- 🔋 **적은 메모리 사용**: 최적화한 자료 구조를 사용하고 필요한 시점에만 데이터를 불러옵니다.
- ⚡ **빠른 JSON 변환**: 표준 라이브러리보다 10배 빠릅니다.
- 🏗️ **실무 검증**: 테스트 커버리지 92%와 전체 코드의 타입 힌트를 갖췄습니다. 지난 1년 동안 수백 명이 매일 데이터를 수집하는 데 사용했습니다.

### 개발자를 위한 편리한 도구

- 🎯 **대화형 셸**: Scrapling을 통합한 IPython 셸을 추가할 수 있습니다. 단축 명령과 도구로 스크립트를 빠르게 개발하세요. curl 요청을 Scrapling 요청으로 바꾸고 결과를 브라우저에서 볼 수 있습니다.
- 🚀 **터미널에서 바로 사용**: 코드를 한 줄도 쓰지 않고 URL에서 데이터를 가져올 수 있습니다!
- 🛠️ **DOM 탐색**: 부모, 형제, 자식 요소로 이동하는 메서드를 제공합니다.
- 🧬 **텍스트 처리**: 정규식, 텍스트 정리, 빠른 문자열 연산을 사용할 수 있습니다.
- 📝 **선택자 생성**: 어떤 요소든 안정적인 CSS·XPath 선택자를 만들 수 있습니다.
- 🔌 **익숙한 API**: Scrapy와 BeautifulSoup에 익숙하다면 쉽게 사용할 수 있습니다. Scrapy·Parsel과 같은 가상 요소를 지원합니다.
- 🤝 **Scrapy 통합**: 콜백에 `scrapling_response` 데코레이터를 붙이면 이미 가져온 응답을 Scrapling 파서로 처리할 수 있습니다. 코드를 새로 작성할 필요가 없습니다.
- 📘 **전체 타입 힌트**: 편집기 지원과 코드 자동 완성을 돕습니다. 코드가 바뀔 때마다 **PyRight**와 **MyPy**가 전체 코드를 자동으로 검사합니다.
- 🔋 **바로 쓰는 Docker 이미지**: 새 버전마다 모든 브라우저가 포함된 Docker 이미지를 자동으로 만들고 배포합니다.

## 시작하기

자주 쓰는 기능을 몇 가지 살펴보겠습니다.

### 기본 사용법
세션을 지원하는 HTTP 요청
```python
from scrapling.fetchers import Fetcher, FetcherSession

with FetcherSession(impersonate='chrome') as session:  # Chrome의 최신 TLS fingerprint 사용
    page = session.get('https://quotes.toscrape.com/', stealthy_headers=True)
    quotes = page.css('.quote .text::text').getall()

# 또는 일회성 요청 사용
page = Fetcher.get('https://quotes.toscrape.com/')
quotes = page.css('.quote .text::text').getall()
```
고급 스텔스 모드
```python
from scrapling.fetchers import StealthyFetcher, StealthySession

with StealthySession(headless=True, solve_cloudflare=True) as session:  # 작업이 끝날 때까지 브라우저를 열어둡니다
    page = session.fetch('https://nopecha.com/demo/cloudflare', google_search=False)
    data = page.css('#padded_content a').getall()

# 또는 일회성 요청 스타일 - 이 요청을 위해 브라우저를 열고, 완료 후 닫습니다
page = StealthyFetcher.fetch('https://nopecha.com/demo/cloudflare', solve_cloudflare=True)
data = page.css('#padded_content a').getall()
```
완전한 브라우저 자동화
```python
from scrapling.fetchers import StealthyFetcher, StealthySession

with StealthySession(headless=True, disable_resources=False, network_idle=True) as session:  # 작업이 끝날 때까지 브라우저를 열어둡니다
    page = session.fetch('https://quotes.toscrape.com/', load_dom=False)
    data = page.xpath('//span[@class="text"]/text()').getall()  # 원하시면 XPath selector도 사용 가능

# 또는 일회성 요청 스타일 - 이 요청을 위해 브라우저를 열고, 완료 후 닫습니다
page = StealthyFetcher.fetch('https://quotes.toscrape.com/')
data = page.css('.quote .text::text').getall()
```

### 스파이더
동시 요청, 여러 세션, 일시 정지와 재개를 지원하는 크롤러를 만들 수 있습니다:
```python
from scrapling.spiders import Spider, Response

class QuotesSpider(Spider):
    name = "quotes"
    start_urls = ["https://quotes.toscrape.com/"]
    concurrent_requests = 10

    async def parse(self, response: Response):
        for quote in response.css('.quote'):
            yield {
                "text": quote.css('.text::text').get(),
                "author": quote.css('.author::text').get(),
            }

        next_page = response.css('.next a')
        if next_page:
            yield response.follow(next_page[0].attrib['href'])

result = QuotesSpider().start()
print(f"{len(result.items)}개의 인용구를 스크레이핑했습니다")
result.items.to_json("quotes.json")
```
한 스파이더에서 여러 종류의 세션을 사용합니다:
```python
from scrapling.spiders import Spider, Request, Response
from scrapling.fetchers import FetcherSession, AsyncStealthySession

class MultiSessionSpider(Spider):
    name = "multi"
    start_urls = ["https://example.com/"]

    def configure_sessions(self, manager):
        manager.add("fast", FetcherSession(impersonate="chrome"))
        manager.add("stealth", AsyncStealthySession(headless=True), lazy=True)

    async def parse(self, response: Response):
        for link in response.css('a::attr(href)').getall():
            # 보호된 페이지는 스텔스 세션을 통해 라우팅
            if "protected" in link:
                yield Request(link, sid="stealth")
            else:
                yield Request(link, sid="fast", callback=self.parse)  # 명시적 콜백
```
진행 상태를 저장하면 긴 크롤링 작업을 멈췄다가 이어서 실행할 수 있습니다. 다음처럼 스파이더를 시작하세요:
```python
QuotesSpider(crawldir="./crawl_data").start()
```
`crawldir`를 설정한 뒤 Ctrl+C를 누르면 대기 중인 요청과 방문한 URL이 저장됩니다. 같은 `crawldir`로 다시 시작하면 이어서 실행됩니다. 추출한 데이터는 따로 저장하세요.

바로 쓸 수 있는 템플릿도 있습니다. 예를 들어 Shopify 스토어의 전체 상품을 가져올 수 있습니다:
```python
from scrapling.spiders import ShopifySpider

class MyStore(ShopifySpider):
    target_website = "example.com"

result = MyStore().start()  # 스토어의 모든 상품을 변형당 한 항목씩 수집
```
이 템플릿은 공개 컬렉션 API에서 상품을 읽고, 상품 옵션 조합마다 한 항목을 만듭니다.

### 고급 파싱과 요소 탐색
```python
from scrapling.fetchers import Fetcher

# 풍부한 요소 선택과 내비게이션
page = Fetcher.get('https://quotes.toscrape.com/')

# 여러 선택 메서드로 인용구 가져오기
quotes = page.css('.quote')  # CSS selector
quotes = page.xpath('//div[@class="quote"]')  # XPath
quotes = page.find_all('div', {'class': 'quote'})  # BeautifulSoup 스타일
# 아래와 동일
quotes = page.find_all('div', class_='quote')
quotes = page.find_all(['div'], class_='quote')
quotes = page.find_all(class_='quote')  # 등등...
# 텍스트 내용으로 요소 찾기
quotes = page.find_by_text('Albert Einstein', first_match=False)

# 고급 내비게이션
quote_text = page.css('.quote')[0].css('.text::text').get()
quote_texts = page.css('.quote').css('.text::text').getall()  # 체이닝 셀렉터
first_quote = page.css('.quote')[0]
author = first_quote.css('.author::text').get()
next_quote = first_quote.next
parent_container = first_quote.parent

# 요소 관계와 유사도
similar_elements = first_quote.find_similar()
below_elements = first_quote.below_elements
```
페이지를 가져오지 않고 파서를 직접 사용할 수도 있습니다:
```python
from scrapling.parser import Selector

page = Selector("<html>...</html>")
```
사용법은 같습니다!

### 비동기 세션 예제
```python
import asyncio
from scrapling.fetchers import FetcherSession, AsyncStealthySession

async def main():
    async with FetcherSession(http3=True) as http_session:  # `FetcherSession`은 컨텍스트에 따라 동기/비동기 방식 모두로 동작합니다
        page1 = await http_session.get('https://quotes.toscrape.com/')
        page2 = await http_session.get('https://quotes.toscrape.com/page/2/', impersonate='chrome')
        print(len(page1.css('.quote')), len(page2.css('.quote')))

    async with AsyncStealthySession(max_pages=2) as browser_session:
        urls = ['https://quotes.toscrape.com/js/', 'https://quotes.toscrape.com/js/page/2/']
        pages = await asyncio.gather(*(browser_session.fetch(url, wait_selector='.quote') for url in urls))
        print([len(page.css('.quote')) for page in pages])

asyncio.run(main())
```

## CLI와 대화형 셸

터미널에서도 Scrapling을 사용할 수 있습니다:

[![asciicast](https://asciinema.org/a/736339.svg)](https://asciinema.org/a/736339)

스크래핑용 대화형 셸을 실행합니다:
```bash
pip install "scrapling[shell]"
scrapling shell
```
프로그래밍 없이 페이지를 파일로 바로 추출합니다. `--css-selector`로 내용을 고르거나 `--ai-targeted`로 `body` 내용을 선택하고 정리하세요. 텍스트는 `.txt`, Markdown은 `.md`, HTML은 `.html`을 사용하세요.
```bash
scrapling extract get 'https://quotes.toscrape.com/' quotes.md
scrapling extract get 'https://quotes.toscrape.com/' quotes.txt --css-selector '.quote' --impersonate 'chrome'
scrapling extract fetch 'https://quotes.toscrape.com/js/' quotes.md --css-selector '.quote' --wait-selector '.quote' --no-headless
scrapling extract fetch 'https://nopecha.com/demo/cloudflare' captchas.html --css-selector '#padded_content a' --solve-cloudflare
```

> [!NOTE]
> MCP 서버와 대화형 셸 등 다른 기능은 [문서](https://scrapling.readthedocs.io/ko/latest/)에서 확인하세요.

## 성능 테스트

Scrapling은 강력할 뿐 아니라 매우 빠릅니다. 다음 테스트는 Scrapling 파서와 널리 쓰이는 다른 라이브러리의 최신 버전을 비교합니다.

### 텍스트 추출 속도: 중첩 요소 5,000개

| # |      라이브러리      | 시간(ms) | Scrapling 대비 |
|---|:-----------------:|:---------:|:------------:|
| 1 |     Scrapling     |   1.99    |     1.0x     |
| 2 |   Parsel/Scrapy   |   2.06    |    1.035     |
| 3 |     Lxml 단독      |   2.56    |    1.286     |
| 4 |      PyQuery      |   23.98   |     ~12x     |
| 5 |    Selectolax     |  197.02   |     ~99x     |
| 6 |  MechanicalSoup   |  1545.15  |   ~776.5x    |
| 7 |   BS4 + Lxml   |  1562.1   |   ~785.0x    |
| 8 | BS4 + html5lib |  3412.73  |   ~1714.9x   |


### 비슷한 요소 찾기와 텍스트 검색

Scrapling의 적응형 요소 검색은 다른 방법보다 훨씬 빠릅니다:

| 라이브러리     | 시간(ms) | Scrapling 대비 |
|-------------|:---------:|:------------:|
| Scrapling   |    2.3    |     1.0x     |
| AutoScraper |   12.58   |    5.47x     |


> 각 결과는 100회 이상 실행한 평균입니다. 측정 방법은 [benchmarks.py](https://github.com/D4Vinci/Scrapling/blob/main/benchmarks.py)를 확인하세요.

## 설치

Scrapling에는 Python 3.10 이상이 필요합니다:

```bash
pip install scrapling
```

> [!IMPORTANT]
> 이 명령은 파서와 필요한 패키지만 설치합니다. Fetcher나 명령줄 도구는 포함되지 않습니다. 따라서 위 예제처럼 `scrapling.fetchers`나 `scrapling.spiders`에서 가져오면 `ModuleNotFoundError`가 발생합니다. Fetcher나 스파이더를 사용하려면 먼저 아래 방법으로 Fetcher에 필요한 패키지를 설치하세요.

### 추가 패키지

1. Fetcher, 관련 클래스, 아래 추가 기능을 사용하려면 Fetcher와 브라우저에 필요한 패키지를 설치하세요:
    ```bash
    pip install "scrapling[fetchers]"

    scrapling install           # 일반 설치
    scrapling install  --force  # 강제 재설치
    ```

    모든 브라우저, 필요한 시스템 패키지, 브라우저 지문을 바꾸는 도구를 다운로드합니다.

    명령어 대신 코드에서 설치할 수도 있습니다:
    ```python
    from scrapling.cli import install

    install([], standalone_mode=False)          # 일반 설치
    install(["--force"], standalone_mode=False) # 강제 재설치
    ```

2. 추가 기능:
   - MCP 서버 설치:
       ```bash
       pip install "scrapling[ai]"
       ```
   - [RAG 시스템 만들기](https://scrapling.readthedocs.io/ko/latest/ai/building-rag-systems.html)에 필요한 패키지 설치:
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

### Docker
모든 추가 기능과 브라우저가 포함된 Docker 이미지를 DockerHub에서 받을 수도 있습니다:
```bash
docker pull pyd4vinci/scrapling
```
또는 GitHub 레지스트리에서 받으세요:
```bash
docker pull ghcr.io/d4vinci/scrapling:latest
```
이 이미지는 저장소의 main 브랜치를 바탕으로 GitHub Actions에서 자동으로 만들고 배포합니다.

## 개발에 참여하기

개발 참여를 환영합니다! 시작하기 전에 [참여 안내](https://github.com/D4Vinci/Scrapling/blob/main/CONTRIBUTING.md)를 읽어 주세요.

## 면책 조항

> [!CAUTION]
> 이 라이브러리는 학습과 연구 목적으로 제공합니다. 사용하면 국내외 데이터 수집과 개인정보 보호 관련 법률을 따르는 데 동의한 것으로 봅니다. 작성자와 참여자는 소프트웨어의 오용에 책임지지 않습니다. 사이트의 이용 약관과 robots.txt를 지켜 주세요.

## 🎓 인용
연구에 이 라이브러리를 사용했다면 다음 형식으로 인용해 주세요:
```text
  @misc{scrapling,
    author = {Karim Shoair},
    title = {Scrapling},
    year = {2024},
    url = {https://github.com/D4Vinci/Scrapling},
    note = {A Python Web Scraping framework for everything from a single request to a full-scale crawl!}
  }
```

## 라이선스

이 프로젝트는 BSD-3-Clause 라이선스로 배포합니다.

## 감사의 말

다음 프로젝트를 바탕으로 한 코드가 포함되어 있습니다:
- Parsel (BSD 라이선스) - [translator](https://github.com/D4Vinci/Scrapling/blob/main/scrapling/core/translator.py) 서브모듈에 사용

---
<div align="center"><small>Karim Shoair가 ❤️으로 디자인하고 만들었습니다.</small></div><br>
