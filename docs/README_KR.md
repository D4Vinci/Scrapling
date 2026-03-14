<!-- mcp-name: io.github.D4Vinci/Scrapling -->

<h1 align="center">
    <a href="https://scrapling.readthedocs.io">
        <picture>
          <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/docs/assets/cover_dark.svg?sanitize=true">
          <img alt="Scrapling Poster" src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/docs/assets/cover_light.svg?sanitize=true">
        </picture>
    </a>
    <br>
    <small>Effortless Web Scraping for the Modern Web</small>
</h1>

<p align="center">
    <a href="https://github.com/D4Vinci/Scrapling/actions/workflows/tests.yml" alt="Tests">
        <img alt="Tests" src="https://github.com/D4Vinci/Scrapling/actions/workflows/tests.yml/badge.svg"></a>
    <a href="https://badge.fury.io/py/Scrapling" alt="PyPI version">
        <img alt="PyPI version" src="https://badge.fury.io/py/Scrapling.svg"></a>
    <a href="https://clickpy.clickhouse.com/dashboard/scrapling" rel="nofollow"><img src="https://img.shields.io/pypi/dm/scrapling" alt="PyPI package downloads"></a>
    <a href="https://github.com/D4Vinci/Scrapling/tree/main/agent-skill" alt="AI Agent Skill directory">
        <img alt="Static Badge" src="https://img.shields.io/badge/Skill-black?style=flat&label=Agent&link=https%3A%2F%2Fgithub.com%2FD4Vinci%2FScrapling%2Ftree%2Fmain%2Fagent-skill"></a>
    <a href="https://clawhub.ai/D4Vinci/scrapling-official" alt="OpenClaw Skill">
        <img alt="OpenClaw Skill" src="https://img.shields.io/badge/Clawhub-darkred?style=flat&label=OpenClaw&link=https%3A%2F%2Fclawhub.ai%2FD4Vinci%2Fscrapling-official"></a>
    <br/>
    <a href="https://discord.gg/EMgGbDceNQ" alt="Discord" target="_blank">
      <img alt="Discord" src="https://img.shields.io/discord/1360786381042880532?style=social&logo=discord&link=https%3A%2F%2Fdiscord.gg%2FEMgGbDceNQ">
    </a>
    <a href="https://x.com/Scrapling_dev" alt="X (formerly Twitter)">
      <img alt="X (formerly Twitter) Follow" src="https://img.shields.io/twitter/follow/Scrapling_dev?style=social&logo=x&link=https%3A%2F%2Fx.com%2FScrapling_dev">
    </a>
    <br/>
    <a href="https://pypi.org/project/scrapling/" alt="Supported Python versions">
        <img alt="Supported Python versions" src="https://img.shields.io/pypi/pyversions/scrapling.svg"></a>
</p>

<p align="center">
    <a href="https://scrapling.readthedocs.io/en/latest/parsing/selection/"><strong>선택 메서드</strong></a>
    &middot;
    <a href="https://scrapling.readthedocs.io/en/latest/fetching/choosing/"><strong>Fetcher 선택 가이드</strong></a>
    &middot;
    <a href="https://scrapling.readthedocs.io/en/latest/spiders/architecture.html"><strong>Spider</strong></a>
    &middot;
    <a href="https://scrapling.readthedocs.io/en/latest/spiders/proxy-blocking.html"><strong>프록시 로테이션</strong></a>
    &middot;
    <a href="https://scrapling.readthedocs.io/en/latest/cli/overview/"><strong>CLI</strong></a>
    &middot;
    <a href="https://scrapling.readthedocs.io/en/latest/ai/mcp-server/"><strong>MCP 서버</strong></a>
</p>

Scrapling은 단일 요청부터 대규모 크롤링까지 모든 것을 처리하는 적응형 Web Scraping 프레임워크입니다.

파서는 웹사이트 변경 사항을 학습하고, 페이지가 업데이트되면 요소를 자동으로 재배치합니다. Fetcher는 Cloudflare Turnstile 같은 안티봇 시스템을 별도 설정 없이 우회합니다. Spider 프레임워크를 사용하면 일시정지/재개 및 자동 프록시 로테이션을 갖춘 동시 멀티 세션 크롤링으로 확장할 수 있습니다 — 모두 Python 몇 줄이면 됩니다. 하나의 라이브러리, 타협 없는 성능.

실시간 통계와 스트리밍을 통한 초고속 크롤링. Web Scraper가 만들고, Web Scraper와 일반 사용자 모두를 위해 설계했습니다.

```python
from scrapling.fetchers import Fetcher, AsyncFetcher, StealthyFetcher, DynamicFetcher
StealthyFetcher.adaptive = True
p = StealthyFetcher.fetch('https://example.com', headless=True, network_idle=True)  # 탐지를 피해 웹사이트를 가져옵니다!
products = p.css('.product', auto_save=True)                                        # 웹사이트 디자인 변경에도 살아남는 데이터를 스크레이핑!
products = p.css('.product', adaptive=True)                                         # 나중에 웹사이트 구조가 바뀌면, `adaptive=True`를 전달해서 찾으세요!
```
또는 본격적인 크롤링으로 확장
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

<p align="center">
    <a href="https://dataimpulse.com/?utm_source=scrapling&utm_medium=banner&utm_campaign=scrapling" target="_blank" style="display:flex; justify-content:center; padding:4px 0;">
        <img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/DataImpulse.png" alt="At DataImpulse, we specialize in developing custom proxy services for your business. Make requests from anywhere, collect data, and enjoy fast connections with our premium proxies." style="max-height:60px;">
    </a>
</p>

# 플래티넘 스폰서
<table>
  <tr>
    <td width="200">
      <a href="https://hypersolutions.co/?utm_source=github&utm_medium=readme&utm_campaign=scrapling" target="_blank" title="Bot Protection Bypass API for Akamai, DataDome, Incapsula & Kasada">
        <img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/HyperSolutions.png">
      </a>
    </td>
    <td> Scrapling은 Cloudflare Turnstile을 처리합니다. 엔터프라이즈급 보호가 필요하다면, <a href="https://hypersolutions.co?utm_source=github&utm_medium=readme&utm_campaign=scrapling">
        <b>Hyper Solutions</b>
      </a>가 <b>Akamai</b>, <b>DataDome</b>, <b>Kasada</b>, <b>Incapsula</b>용 유효한 안티봇 토큰을 생성하는 API 엔드포인트를 제공합니다. 간단한 API 호출만으로, 브라우저 자동화가 필요 없습니다. </td>
  </tr>
  <tr>
    <td width="200">
      <a href="https://birdproxies.com/t/scrapling" target="_blank" title="At Bird Proxies, we eliminate your pains such as banned IPs, geo restriction, and high costs so you can focus on your work.">
        <img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/BirdProxies.jpg">
      </a>
    </td>
    <td>프록시는 복잡하거나 비쌀 이유가 없다는 생각으로 <a href="https://birdproxies.com/t/scrapling">
        <b>BirdProxies</b>
      </a>를 만들었습니다. <br /> 195개 이상 지역의 빠른 레지덴셜 및 ISP 프록시, 합리적인 가격, 실질적인 지원. <br />
      <b>랜딩 페이지에서 FlappyBird 게임을 플레이하고 무료 데이터를 받으세요!</b>
    </td>
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
      </a>: 레지덴셜 프록시 GB당 $0.49부터. 완전히 위장된 Chromium 스크레이핑 브라우저, 레지덴셜 IP, 자동 CAPTCHA 해결, 안티봇 우회.</br>
      <b>Scraper API로 번거로움 없이 결과를 얻으세요. MCP 및 N8N 통합 지원.</b>
    </td>
  </tr>
  <tr>
    <td width="200">
      <a href="https://tikhub.io/?ref=KarimShoair" target="_blank" title="Unlock the Power of Social Media Data & AI">
        <img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/TikHub.jpg">
      </a>
    </td>
    <td>
      <a href="https://tikhub.io/?ref=KarimShoair" target="_blank">TikHub.io</a>는 TikTok, X, YouTube, Instagram 등 16개 이상 플랫폼에서 900개 이상의 안정적인 API를 제공하며, 4,000만 이상의 데이터셋을 보유하고 있습니다. <br /> <a href="https://ai.tikhub.io/?ref=KarimShoair" target="_blank">할인된 AI 모델</a>도 제공 — Claude, GPT, GEMINI 등 최대 71% 할인.
    </td>
  </tr>
  <tr>
    <td width="200">
      <a href="https://www.nsocks.com/?keyword=2p67aivg" target="_blank" title="Scalable Web Data Access for AI Applications">
        <img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/nsocks.png">
      </a>
    </td>
    <td>
    <a href="https://www.nsocks.com/?keyword=2p67aivg" target="_blank">Nsocks</a>는 개발자와 스크레이퍼를 위한 빠른 레지덴셜 및 ISP 프록시를 제공합니다. 글로벌 IP 커버리지, 높은 익명성, 스마트 로테이션, 자동화와 데이터 추출을 위한 안정적인 성능. <a href="https://www.xcrawl.com/?keyword=2p67aivg" target="_blank">Xcrawl</a>로 대규모 웹 크롤링을 간소화하세요.
    </td>
  </tr>
  <tr>
    <td width="200">
      <a href="https://petrosky.io/d4vinci" target="_blank" title="PetroSky delivers cutting-edge VPS hosting.">
        <img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/petrosky.png">
      </a>
    </td>
    <td>
    노트북을 닫으세요. 스크래퍼는 계속 작동합니다. <br />
    <a href="https://petrosky.io/d4vinci" target="_blank">PetroSky VPS</a> - 논스톱 자동화를 위한 클라우드 서버. Windows 및 Linux 머신을 완벽하게 제어. 월 €6.99부터.
    </td>
  </tr>
</table>

<i><sub>여기에 광고를 게재하고 싶으신가요? [여기](https://github.com/sponsors/D4Vinci/sponsorships?tier_id=586646)를 클릭하세요</sub></i>
# 스폰서

<!-- sponsors -->

<a href="https://serpapi.com/?utm_source=scrapling" target="_blank" title="Scrape Google and other search engines with SerpApi"><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/SerpApi.png"></a>
<a href="https://visit.decodo.com/Dy6W0b" target="_blank" title="Try the Most Efficient Residential Proxies for Free"><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/decodo.png"></a>
<a href="https://hasdata.com/?utm_source=github&utm_medium=banner&utm_campaign=D4Vinci" target="_blank" title="The web scraping service that actually beats anti-bot systems!"><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/hasdata.png"></a>
<a href="https://proxyempire.io/?ref=scrapling&utm_source=scrapling" target="_blank" title="Collect The Data Your Project Needs with the Best Residential Proxies"><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/ProxyEmpire.png"></a><a href="https://www.swiftproxy.net/" target="_blank" title="Unlock Reliable Proxy Services with Swiftproxy!"><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/swiftproxy.png"></a>
<a href="https://www.rapidproxy.io/?ref=d4v" target="_blank" title="Affordable Access to the Proxy World – bypass CAPTCHAs blocks, and avoid additional costs."><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/rapidproxy.jpg"></a>
<a href="https://browser.cash/?utm_source=D4Vinci&utm_medium=referral" target="_blank" title="Browser Automation & AI Browser Agent Platform"><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/browserCash.png"></a>

<!-- /sponsors -->

<i><sub>여기에 광고를 게재하고 싶으신가요? [여기](https://github.com/sponsors/D4Vinci)를 클릭하고 원하는 티어를 선택하세요!</sub></i>

---

## 주요 기능

### Spider — 본격적인 크롤링 프레임워크
- 🕷️ **Scrapy 스타일 Spider API**: `start_urls`, 비동기 `parse` 콜백, `Request`/`Response` 객체로 Spider를 정의합니다.
- ⚡ **동시 크롤링**: 설정 가능한 동시 요청 수 제한, 도메인별 스로틀링, 다운로드 딜레이를 지원합니다.
- 🔄 **멀티 세션 지원**: HTTP 요청과 스텔스 헤드리스 브라우저를 하나의 인터페이스로 통합 — ID로 요청을 다른 세션에 라우팅합니다.
- 💾 **일시정지 & 재개**: 체크포인트 기반의 크롤링 영속화. Ctrl+C로 정상 종료하고, 재시작하면 중단된 지점부터 이어갑니다.
- 📡 **스트리밍 모드**: `async for item in spider.stream()`으로 스크레이핑된 아이템을 실시간 통계와 함께 스트리밍으로 수신 — UI, 파이프라인, 장시간 크롤링에 적합합니다.
- 🛡️ **차단된 요청 감지**: 커스텀 로직을 통한 차단된 요청의 자동 감지 및 재시도를 지원합니다.
- 📦 **내장 내보내기**: 훅이나 자체 파이프라인, 또는 내장 JSON/JSONL로 결과를 내보냅니다. 각각 `result.items.to_json()` / `result.items.to_jsonl()`을 사용합니다.

### 세션을 지원하는 고급 웹사이트 가져오기
- **HTTP 요청**: `Fetcher` 클래스로 빠르고 은밀한 HTTP 요청. 브라우저의 TLS fingerprint, 헤더를 모방하고, HTTP/3를 사용할 수 있습니다.
- **동적 로딩**: Playwright의 Chromium과 Google Chrome을 지원하는 `DynamicFetcher` 클래스로 완전한 브라우저 자동화를 통해 동적 웹사이트를 가져옵니다.
- **안티봇 우회**: `StealthyFetcher`와 fingerprint 위장을 통한 고급 스텔스 기능. 자동화로 모든 유형의 Cloudflare Turnstile/Interstitial을 손쉽게 우회합니다.
- **세션 관리**: `FetcherSession`, `StealthySession`, `DynamicSession` 클래스로 요청 간 쿠키와 상태를 관리하는 영속적 세션을 지원합니다.
- **프록시 로테이션**: 모든 세션 타입에 대응하는 순환 또는 커스텀 전략의 내장 `ProxyRotator`와 요청별 프록시 오버라이드를 제공합니다.
- **도메인 차단**: 브라우저 기반 Fetcher에서 특정 도메인(및 하위 도메인)으로의 요청을 차단합니다.
- **비동기 지원**: 모든 Fetcher와 전용 비동기 세션 클래스에서 완전한 비동기를 지원합니다.

### 적응형 스크레이핑 & AI 통합
- 🔄 **스마트 요소 추적**: 지능적인 유사도 알고리즘으로 웹사이트 변경 후에도 요소를 재배치합니다.
- 🎯 **유연한 스마트 선택**: CSS selector, XPath selector, 필터 기반 검색, 텍스트 검색, 정규식 검색 등을 지원합니다.
- 🔍 **유사 요소 찾기**: 발견된 요소와 유사한 요소를 자동으로 찾아냅니다.
- 🤖 **AI와 함께 사용하는 MCP 서버**: AI 기반 Web Scraping과 데이터 추출을 위한 내장 MCP 서버. AI(Claude/Cursor 등)에 전달하기 전에 Scrapling을 활용해 대상 콘텐츠를 추출하는 강력한 커스텀 기능을 갖추고 있어, 작업 속도를 높이고 토큰 사용량을 최소화해 비용을 절감합니다. ([데모 영상](https://www.youtube.com/watch?v=qyFk3ZNwOxE))

### 고성능 & 실전 검증된 아키텍처
- 🚀 **초고속**: 대부분의 Python 스크레이핑 라이브러리를 능가하는 최적화된 성능.
- 🔋 **메모리 효율**: 최적화된 데이터 구조와 지연 로딩으로 메모리 사용을 최소화합니다.
- ⚡ **고속 JSON 직렬화**: 표준 라이브러리보다 10배 빠릅니다.
- 🏗️ **실전 검증**: Scrapling은 92%의 테스트 커버리지와 완전한 타입 힌트 커버리지를 갖추고 있을 뿐 아니라, 지난 1년간 수백 명의 Web Scraper가 매일 사용해 왔습니다.

### 개발자/Web Scraper 친화적 경험
- 🎯 **인터랙티브 Web Scraping Shell**: Scrapling 통합, 단축키, curl 요청을 Scrapling 요청으로 변환하거나 브라우저에서 요청 결과를 확인하는 등의 도구를 갖춘 선택적 내장 IPython Shell로, Web Scraping 스크립트 개발을 가속합니다.
- 🚀 **터미널에서 바로 사용**: 코드 한 줄 없이 Scrapling으로 URL을 스크레이핑할 수 있습니다!
- 🛠️ **풍부한 내비게이션 API**: 부모, 형제, 자식 탐색 메서드를 통한 고급 DOM 순회를 지원합니다.
- 🧬 **향상된 텍스트 처리**: 내장 정규식, 클리닝 메서드, 최적화된 문자열 연산을 제공합니다.
- 📝 **자동 셀렉터 생성**: 모든 요소에 대해 견고한 CSS/XPath selector를 생성합니다.
- 🔌 **익숙한 API**: Scrapy/Parsel에서 사용하는 것과 동일한 의사 요소(pseudo-element)를 가진 Scrapy/BeautifulSoup 스타일의 API.
- 📘 **완전한 타입 커버리지**: 뛰어난 IDE 지원과 코드 자동완성을 위한 완전한 타입 힌트. 코드베이스 전체가 변경될 때마다 **PyRight**와 **MyPy**로 자동 검사됩니다.
- 🔋 **바로 사용 가능한 Docker 이미지**: 매 릴리스마다 모든 브라우저를 포함한 Docker 이미지가 자동으로 빌드 및 푸시됩니다.

## 시작하기

깊이 들어가지 않고, Scrapling이 할 수 있는 것들을 간단히 살펴보겠습니다.

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

# 또는 일회성 요청 스타일 — 이 요청을 위해 브라우저를 열고, 완료 후 닫습니다
page = StealthyFetcher.fetch('https://nopecha.com/demo/cloudflare')
data = page.css('#padded_content a').getall()
```
완전한 브라우저 자동화
```python
from scrapling.fetchers import DynamicFetcher, DynamicSession

with DynamicSession(headless=True, disable_resources=False, network_idle=True) as session:  # 작업이 끝날 때까지 브라우저를 열어둡니다
    page = session.fetch('https://quotes.toscrape.com/', load_dom=False)
    data = page.xpath('//span[@class="text"]/text()').getall()  # 원하시면 XPath selector도 사용 가능

# 또는 일회성 요청 스타일 — 이 요청을 위해 브라우저를 열고, 완료 후 닫습니다
page = DynamicFetcher.fetch('https://quotes.toscrape.com/')
data = page.css('.quote .text::text').getall()
```

### Spider
동시 요청, 여러 세션 타입, 일시정지 & 재개를 갖춘 본격적인 크롤러 구축:
```python
from scrapling.spiders import Spider, Request, Response

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
하나의 Spider에서 여러 세션 타입 사용:
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
체크포인트를 사용해 장시간 크롤링을 일시정지 & 재개:
```python
QuotesSpider(crawldir="./crawl_data").start()
```
Ctrl+C를 누르면 정상적으로 일시정지되고, 진행 상황이 자동 저장됩니다. 이후 Spider를 다시 시작할 때 동일한 `crawldir`을 전달하면 중단된 지점부터 재개합니다.

### 고급 파싱 & 내비게이션
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
quotes = page.find_by_text('quote', tag='div')

# 고급 내비게이션
quote_text = page.css('.quote')[0].css('.text::text').get()
quote_text = page.css('.quote').css('.text::text').getall()  # 체이닝 셀렉터
first_quote = page.css('.quote')[0]
author = first_quote.next_sibling.css('.author::text')
parent_container = first_quote.parent

# 요소 관계와 유사도
similar_elements = first_quote.find_similar()
below_elements = first_quote.below_elements()
```
웹사이트를 가져오지 않고 파서를 바로 사용할 수도 있습니다:
```python
from scrapling.parser import Selector

page = Selector("<html>...</html>")
```
사용법은 완전히 동일합니다!

### 비동기 세션 관리 예시
```python
import asyncio
from scrapling.fetchers import FetcherSession, AsyncStealthySession, AsyncDynamicSession

async with FetcherSession(http3=True) as session:  # `FetcherSession`은 컨텍스트 인식이 가능하며 동기/비동기 패턴 모두에서 작동
    page1 = session.get('https://quotes.toscrape.com/')
    page2 = session.get('https://quotes.toscrape.com/', impersonate='firefox135')

# 비동기 세션 사용
async with AsyncStealthySession(max_pages=2) as session:
    tasks = []
    urls = ['https://example.com/page1', 'https://example.com/page2']

    for url in urls:
        task = session.fetch(url)
        tasks.append(task)

    print(session.get_pool_stats())  # 선택 사항 - 브라우저 탭 풀 상태 (사용 중/유휴/에러)
    results = await asyncio.gather(*tasks)
    print(session.get_pool_stats())
```

## CLI & 인터랙티브 Shell

Scrapling에는 강력한 커맨드라인 인터페이스가 포함되어 있습니다:

[![asciicast](https://asciinema.org/a/736339.svg)](https://asciinema.org/a/736339)

인터랙티브 Web Scraping Shell 실행
```bash
scrapling shell
```
프로그래밍 없이 페이지를 파일로 바로 추출합니다 (기본적으로 `body` 태그 내부의 콘텐츠를 추출). 출력 파일이 `.txt`로 끝나면 대상의 텍스트 콘텐츠가 추출됩니다. `.md`로 끝나면 HTML 콘텐츠의 Markdown 표현이 됩니다. `.html`로 끝나면 HTML 콘텐츠 자체가 됩니다.
```bash
scrapling extract get 'https://example.com' content.md
scrapling extract get 'https://example.com' content.txt --css-selector '#fromSkipToProducts' --impersonate 'chrome'  # CSS selector '#fromSkipToProducts'에 매칭되는 모든 요소
scrapling extract fetch 'https://example.com' content.md --css-selector '#fromSkipToProducts' --no-headless
scrapling extract stealthy-fetch 'https://nopecha.com/demo/cloudflare' captchas.html --css-selector '#padded_content a' --solve-cloudflare
```

> [!NOTE]
> MCP 서버와 인터랙티브 Web Scraping Shell 등 더 많은 기능이 있지만, 이 페이지는 간결하게 유지하겠습니다. 전체 문서는 [여기](https://scrapling.readthedocs.io/en/latest/)에서 확인하세요.

## 성능 벤치마크

Scrapling은 강력할 뿐만 아니라 초고속입니다. 아래 벤치마크는 Scrapling의 파서를 다른 인기 라이브러리의 최신 버전과 비교한 것입니다.

### 텍스트 추출 속도 테스트 (5000개 중첩 요소)

| # |      Library      | Time (ms) | vs Scrapling |
|---|:-----------------:|:---------:|:------------:|
| 1 |     Scrapling     |   2.02    |     1.0x     |
| 2 |   Parsel/Scrapy   |   2.04    |     1.01     |
| 3 |     Raw Lxml      |   2.54    |    1.257     |
| 4 |      PyQuery      |   24.17   |     ~12x     |
| 5 |    Selectolax     |   82.63   |     ~41x     |
| 6 |  MechanicalSoup   |  1549.71  |   ~767.1x    |
| 7 |   BS4 with Lxml   |  1584.31  |   ~784.3x    |
| 8 | BS4 with html5lib |  3391.91  |   ~1679.1x   |


### 요소 유사도 & 텍스트 검색 성능

Scrapling의 적응형 요소 찾기 기능은 대안들을 크게 앞섭니다:

| Library     | Time (ms) | vs Scrapling |
|-------------|:---------:|:------------:|
| Scrapling   |   2.39    |     1.0x     |
| AutoScraper |   12.45   |    5.209x    |


> 모든 벤치마크는 100회 이상 실행의 평균입니다. 측정 방법은 [benchmarks.py](https://github.com/D4Vinci/Scrapling/blob/main/benchmarks.py)를 참조하세요.

## 설치

Scrapling은 Python 3.10 이상이 필요합니다:

```bash
pip install scrapling
```

이 설치에는 파서 엔진과 의존성만 포함되며, Fetcher나 커맨드라인 의존성은 포함되지 않습니다.

### 선택적 의존성

1. 아래의 추가 기능, Fetcher, 또는 관련 클래스를 사용하려면 Fetcher 의존성과 브라우저 의존성을 다음과 같이 설치해야 합니다:
    ```bash
    pip install "scrapling[fetchers]"

    scrapling install           # 일반 설치
    scrapling install  --force  # 강제 재설치
    ```

    이렇게 하면 모든 브라우저와 시스템 의존성, fingerprint 조작 의존성이 다운로드됩니다.

    또는 명령어 대신 코드에서 설치할 수도 있습니다:
    ```python
    from scrapling.cli import install

    install([], standalone_mode=False)          # 일반 설치
    install(["--force"], standalone_mode=False) # 강제 재설치
    ```

2. 추가 기능:
   - MCP 서버 기능 설치:
       ```bash
       pip install "scrapling[ai]"
       ```
   - Shell 기능 (Web Scraping Shell 및 `extract` 명령어) 설치:
       ```bash
       pip install "scrapling[shell]"
       ```
   - 모든 기능 설치:
       ```bash
       pip install "scrapling[all]"
       ```
   위 추가 기능을 설치한 후에도 (아직 하지 않았다면) `scrapling install`로 브라우저 의존성을 설치해야 합니다.

### Docker
DockerHub에서 모든 추가 기능과 브라우저가 포함된 Docker 이미지를 설치할 수도 있습니다:
```bash
docker pull pyd4vinci/scrapling
```
또는 GitHub 레지스트리에서 다운로드:
```bash
docker pull ghcr.io/d4vinci/scrapling:latest
```
이 이미지는 GitHub Actions와 레포지토리의 main 브랜치를 사용하여 자동으로 빌드 및 푸시됩니다.

## 기여하기

기여를 환영합니다! 시작하기 전에 [기여 가이드라인](https://github.com/D4Vinci/Scrapling/blob/main/CONTRIBUTING.md)을 읽어주세요.

## 면책 조항

> [!CAUTION]
> 이 라이브러리는 교육 및 연구 목적으로만 제공됩니다. 이 라이브러리를 사용함으로써, 국내외 데이터 스크레이핑 및 개인정보 보호 관련 법률을 준수하는 데 동의한 것으로 간주됩니다. 저자와 기여자는 이 소프트웨어의 오용에 대해 책임지지 않습니다. 항상 웹사이트의 이용약관과 robots.txt 파일을 존중하세요.

## 🎓 인용
연구 목적으로 이 라이브러리를 사용하셨다면, 아래 참고 문헌으로 인용해 주세요:
```text
  @misc{scrapling,
    author = {Karim Shoair},
    title = {Scrapling},
    year = {2024},
    url = {https://github.com/D4Vinci/Scrapling},
    note = {An adaptive Web Scraping framework that handles everything from a single request to a full-scale crawl!}
  }
```

## 라이선스

이 프로젝트는 BSD-3-Clause 라이선스 하에 배포됩니다.

## 감사의 말

이 프로젝트에는 다음에서 차용한 코드가 포함되어 있습니다:
- Parsel (BSD 라이선스) — [translator](https://github.com/D4Vinci/Scrapling/blob/main/scrapling/core/translator.py) 서브모듈에 사용

---
<div align="center"><small>Karim Shoair가 ❤️으로 디자인하고 만들었습니다.</small></div><br>
