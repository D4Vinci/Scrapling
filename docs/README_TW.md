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
    <a href="https://scrapling.readthedocs.io/en/latest/parsing/selection.html"><strong>選擇方法</strong></a>
    &middot;
    <a href="https://scrapling.readthedocs.io/en/latest/fetching/choosing.html"><strong>選擇 Fetcher</strong></a>
    &middot;
    <a href="https://scrapling.readthedocs.io/en/latest/spiders/architecture.html"><strong>爬蟲</strong></a>
    &middot;
    <a href="https://scrapling.readthedocs.io/en/latest/spiders/proxy-blocking.html"><strong>代理輪換</strong></a>
    &middot;
    <a href="https://scrapling.readthedocs.io/en/latest/cli/overview.html"><strong>CLI</strong></a>
    &middot;
    <a href="https://scrapling.readthedocs.io/en/latest/ai/mcp-server.html"><strong>MCP 模式</strong></a>
</p>

Scrapling 是一個自適應 Web Scraping 框架，能處理從單個請求到大規模爬取的一切需求。

它的解析器能夠從網站變化中學習，並在頁面更新時自動重新定位您的元素。它的 Fetcher 能夠開箱即用地繞過 Cloudflare Turnstile 等反機器人系統。它的 Spider 框架讓您可以擴充套件到併發、多 Session 爬取，支援暫停/恢復和自動 Proxy 輪換--只需幾行 Python 程式碼。一個庫，零妥協。

極速爬取，即時統計和 Streaming。由 Web Scraper 為 Web Scraper 和普通使用者而構建，每個人都能找到適合自己的功能。

```python
from scrapling.fetchers import Fetcher, AsyncFetcher, StealthyFetcher, DynamicFetcher
StealthyFetcher.adaptive = True
p = StealthyFetcher.fetch('https://example.com', headless=True, network_idle=True)  # 隱秘地獲取網站！
products = p.css('.product', auto_save=True)                                        # 抓取在網站設計變更後仍能存活的資料！
products = p.css('.product', adaptive=True)                                         # 之後，如果網站結構改變，傳遞 `adaptive=True` 來找到它們！
```
或擴充套件為完整爬取
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

# 鉑金贊助商
<table>
  <tr>
    <td width="200">
      <a href="https://coldproxy.com/" target="_blank" title="Residential, IPv6 & Datacenter Proxies for Web Scraping">
        <img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/coldproxy.png">
      </a>
    </td>
    <td> <a href="https://coldproxy.com/" target="_blank"><b>ColdProxy</b></a> 提供住宅代理和資料中心代理，用於穩定的網路抓取、公共資料收集，以及覆蓋 195 多個國家/地區的地理定向測試。
    </td>
  </tr>
  <tr>
    <td width="200">
      <a href="https://hypersolutions.co/?utm_source=github&utm_medium=readme&utm_campaign=scrapling" target="_blank" title="Bot Protection Bypass API for Akamai, DataDome, Incapsula & Kasada">
        <img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/HyperSolutions.png">
      </a>
    </td>
    <td> Scrapling 可處理 Cloudflare Turnstile。對於企業級保護，<a href="https://hypersolutions.co?utm_source=github&utm_medium=readme&utm_campaign=scrapling">
        <b>Hyper Solutions</b>
      </a> 提供 API 端點，生成適用於 <b>Akamai</b>、<b>DataDome</b>、<b>Kasada</b> 和 <b>Incapsula</b> 的有效 antibot 令牌。簡單的 API 呼叫，無需瀏覽器自動化。 </td>
  </tr>
  <tr>
    <td width="200">
      <a href="https://birdproxies.com/t/scrapling" target="_blank" title="At Bird Proxies, we eliminate your pains such as banned IPs, geo restriction, and high costs so you can focus on your work.">
        <img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/BirdProxies.jpg">
      </a>
    </td>
    <td>嘿，我們建立了 <a href="https://birdproxies.com/t/scrapling">
        <b>BirdProxies</b>
      </a>，因為代理不應該複雜或昂貴。 <br /> 覆蓋 195+ 地區的快速住宅和 ISP 代理，公平定價，真正的支援。 <br />
      <b>在落地頁試試我們的 FlappyBird 遊戲，獲取免費流量！</b>
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
      </a>：住宅代理低至 0.49 美元/GB。具備完全偽裝 Chromium 的爬蟲瀏覽器、住宅 IP、自動驗證碼解決和反機器人繞過。</br>
      <b>Scraper API 輕鬆獲取結果。支援 MCP 和 N8N 整合。</b>
    </td>
  </tr>
  <tr>
    <td width="200">
      <a href="https://tikhub.io/?utm_source=github.com/D4Vinci/Scrapling&utm_medium=marketing_social&utm_campaign=retargeting&utm_content=carousel_ad" target="_blank" title="Unlock the Power of Social Media Data & AI">
        <img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/TikHub.jpg">
      </a>
    </td>
    <td>
      <a href="https://tikhub.io/?utm_source=github.com/D4Vinci/Scrapling&utm_medium=marketing_social&utm_campaign=retargeting&utm_content=carousel_ad" target="_blank">TikHub.io</a> 提供覆蓋 16+ 平臺（包括 TikTok、X、YouTube 和 Instagram）的 900+ 穩定 API，擁有 4000 萬+ 資料集。<br /> 還提供<a href="https://ai.tikhub.io/?ref=KarimShoair" target="_blank">優惠 AI 模型</a> - Claude、GPT、GEMINI 等，最高優惠 71%。
    </td>
  </tr>
  <tr>
    <td width="200">
      <a href="https://www.nsocks.com/?keyword=2p67aivg" target="_blank" title="Scalable Web Data Access for AI Applications">
        <img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/nsocks.png">
      </a>
    </td>
    <td>
    <a href="https://www.nsocks.com/?keyword=2p67aivg" target="_blank">Nsocks</a> 提供面向開發者和爬蟲的快速住宅和 ISP 代理。全球 IP 覆蓋、高匿名性、智慧輪換，以及可靠的自動化和資料提取效能。使用 <a href="https://www.xcrawl.com/?keyword=2p67aivg" target="_blank">Xcrawl</a> 簡化大規模網頁爬取。
    </td>
  </tr>
  <tr>
    <td width="200">
      <a href="https://petrosky.io/d4vinci" target="_blank" title="PetroSky delivers cutting-edge VPS hosting.">
        <img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/petrosky.png">
      </a>
    </td>
    <td>
    合上筆記型電腦，您的爬蟲仍在執行。<br />
    <a href="https://petrosky.io/d4vinci" target="_blank">PetroSky VPS</a> - 為不間斷自動化而生的雲伺服器。Windows 和 Linux 系統，完全掌控。低至 €6.99/月。
    </td>
  </tr>
  <tr>
    <td width="200">
      <a href="https://substack.thewebscraping.club/p/scrapling-hands-on-guide?utm_source=github&utm_medium=repo&utm_campaign=scrapling" target="_blank" title="The #1 newsletter dedicated to Web Scraping">
        <img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/TWSC.png">
      </a>
    </td>
    <td>
    閱讀 <a href="https://substack.thewebscraping.club/p/scrapling-hands-on-guide?utm_source=github&utm_medium=repo&utm_campaign=scrapling" target="_blank">The Web Scraping Club 上關於 Scrapling 的完整評測</a>（2025 年 11 月），這是排名第一的網頁抓取專業通訊。
    </td>
  </tr>
  <tr>
    <td width="200">
      <a href="http://mangoproxy.com/?utm_source=D4Vinci&utm_medium=GitHub&utm_campaign=D4Vinci" target="_blank" title="Proxies You Can Rely On: Residential, Server, and Mobile">
        <img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/MangoProxy.png">
      </a>
    </td>
    <td>
    <a href="http://mangoproxy.com/?utm_source=D4Vinci&utm_medium=GitHub&utm_campaign=D4Vinci" target="_blank">穩定的代理</a>，適用於資料抓取、自動化和多賬號管理。乾淨的 IP、快速響應、高負載下可靠的效能。專為可擴充套件的工作流程而構建。
    </td>
  </tr>
  <tr>
    <td width="200">
      <a href="https://www.swiftproxy.net/?ref=D4Vinci" target="_blank" title="Scalable Solutions for Web Data Access">
        <img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/SwiftProxy.png">
      </a>
    </td>
    <td>
    <a href="https://www.swiftproxy.net/?ref=D4Vinci" target="_blank">Swiftproxy</a> 提供可擴充套件的住宅代理，覆蓋 195+ 國家/地區的 8000 萬+ IP，提供快速可靠的連線、自動輪換和強大的反遮蔽效能。提供免費試用。
    </td>
  </tr>
</table>

<i><sub>想在這裡展示您的廣告嗎？點選 [這裡](https://github.com/sponsors/D4Vinci/sponsorships?tier_id=586646)</sub></i>
# 贊助商

<!-- sponsors -->
<a href="https://www.crawleo.dev/?utm_source=github&utm_medium=sponsor&utm_campaign=scrapling" target="_blank" title="Supercharge your AI with Real-Time Web Intelligence"><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/crawleo.png"></a>
<br/>

<a href="https://serpapi.com/?utm_source=scrapling" target="_blank" title="Scrape Google and other search engines with SerpApi"><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/SerpApi.png"></a>
<a href="https://visit.decodo.com/Dy6W0b" target="_blank" title="Try the Most Efficient Residential Proxies for Free"><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/decodo.png"></a>
<a href="https://hasdata.com/?utm_source=github&utm_medium=banner&utm_campaign=D4Vinci" target="_blank" title="The web scraping service that actually beats anti-bot systems!"><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/hasdata.png"></a>
<a href="https://proxyempire.io/?ref=scrapling&utm_source=scrapling" target="_blank" title="Collect The Data Your Project Needs with the Best Residential Proxies"><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/ProxyEmpire.png"></a>
<a href="https://www.webshare.io/?referral_code=48r2m2cd5uz1" target="_blank" title="The Most Reliable Proxy with Unparalleled Performance"><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/webshare.png"></a>
<a href="https://www.rapidproxy.io/?ref=d4v" target="_blank" title="Affordable Access to the Proxy World – bypass CAPTCHAs blocks, and avoid additional costs."><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/rapidproxy.jpg"></a>
<a href="https://www.ipfoxy.com/?r=scrapling" target="_blank" title="Unlock the Full Potential of Global Business with IPFoxy's High-Quality Rotating and Dedicated Proxy Services."><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/IPFoxy.jpg"></a>
<a href="https://www.ipcook.com/?ref=EAENO9&utm_source=github&utm_medium=referral&utm_campaign=d4vinci_scrapling" target="_blank" title="Fast Proxies. Smart Pricing. Premium Performance."><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/IPCook.png"></a>
<a href="https://proxiware.com/?ref=scrapling" target="_blank" title="Collect Any Data. At Any Scale."><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/proxiware.png"></a>


<!-- /sponsors -->

<i><sub>想在這裡展示您的廣告嗎？點選 [這裡](https://github.com/sponsors/D4Vinci) 並選擇適合您的級別！</sub></i>

---

## 主要特性

### Spider - 完整的爬取框架
- 🕷️ **類 Scrapy 的 Spider API**：使用 `start_urls`、async `parse` callback 和`Request`/`Response` 物件定義 Spider。
- ⚡ **併發爬取**：可配置的併發限制、按域名節流和下載延遲。
- 🔄 **多 Session 支援**：統一介面，支援 HTTP 請求和隱秘無頭瀏覽器在同一個 Spider 中使用--透過 ID 將請求路由到不同的 Session。
- 💾 **暫停與恢復**：基於 Checkpoint 的爬取持久化。按 Ctrl+C 優雅關閉；重啟後從上次停止的地方繼續。
- 📡 **Streaming 模式**：透過 `async for item in spider.stream()` 以即時統計 Streaming 抓取的資料--非常適合 UI、管道和長時間執行的爬取。
- 🛡️ **被阻止請求檢測**：自動檢測並重試被阻止的請求，支援自定義邏輯。
- 🤖 **robots.txt 合規**：可選的 `robots_txt_obey` 標誌，支援 `Disallow`、`Crawl-delay` 和 `Request-rate` 指令，並按域名快取。
- 🧪 **開發模式**：首次執行時將響應快取到磁碟，後續執行時直接回放 - 在不重新請求目標伺服器的情況下迭代你的 `parse()` 邏輯。
- 📦 **內建匯出**：透過鉤子和您自己的管道匯出結果，或使用內建的 JSON/JSONL，分別透過 `result.items.to_json()`/`result.items.to_jsonl()`。

### 支援 Session 的高階網站獲取
- **HTTP 請求**：使用 `Fetcher` 類進行快速和隱秘的 HTTP 請求。可以模擬瀏覽器的 TLS fingerprint、標頭並使用 HTTP/3。
- **動態載入**：透過 `DynamicFetcher` 類使用完整的瀏覽器自動化獲取動態網站，支援 Playwright 的 Chromium 和 Google Chrome。
- **反機器人繞過**：使用 `StealthyFetcher` 的高階隱秘功能和 fingerprint 偽裝。可以輕鬆自動繞過所有型別的 Cloudflare Turnstile/Interstitial。
- **Session 管理**：使用 `FetcherSession`、`StealthySession` 和 `DynamicSession` 類實現持久化 Session 支援，用於跨請求的 cookie 和狀態管理。
- **Proxy 輪換**：內建 `ProxyRotator`，支援輪詢或自定義策略，適用於所有 Session 型別，並支援按請求覆蓋 Proxy。
- **域名和廣告遮蔽**：在基於瀏覽器的 Fetcher 中遮蔽對特定域名（及其子域名）的請求，或啟用內建廣告遮蔽（約 3,500 個已知廣告/追蹤域名）。
- **DNS 洩漏防護**：可選的 DNS-over-HTTPS 支援，透過 Cloudflare 的 DoH 路由 DNS 查詢，防止使用代理時的 DNS 洩漏。
- **Async 支援**：所有 Fetcher 和專用 async Session 類的完整 async 支援。

### 自適應抓取和 AI 整合
- 🔄 **智慧元素跟蹤**：使用智慧相似性演算法在網站更改後重新定位元素。
- 🎯 **智慧靈活選擇**：CSS 選擇器、XPath 選擇器、基於過濾器的搜尋、文本搜尋、正則表示式搜尋等。
- 🔍 **查詢相似元素**：自動定位與已找到元素相似的元素。
- 🤖 **與 AI 一起使用的 MCP 伺服器**：內建 MCP 伺服器用於 AI 輔助 Web Scraping 和資料提取。MCP 伺服器具有強大的自定義功能，利用 Scrapling 在將內容傳遞給 AI（Claude/Cursor 等）之前提取目標內容，從而加快操作並透過最小化 token 使用來降低成本。（[演示影片](https://www.youtube.com/watch?v=qyFk3ZNwOxE)）

### 高效能和經過實戰測試的架構
- 🚀 **閃電般快速**：最佳化效能超越大多數 Python 抓取庫。
- 🔋 **記憶體高效**：最佳化的資料結構和延遲載入，最小記憶體佔用。
- ⚡ **快速 JSON 序列化**：比標準庫快 10 倍。
- 🏗️ **經過實戰測試**：Scrapling 不僅擁有 92% 的測試覆蓋率和完整的型別提示覆蓋率，而且在過去一年中每天被數百名 Web Scraper 使用。

### 對開發者/Web Scraper 友好的體驗
- 🎯 **互動式 Web Scraping Shell**：可選的內建 IPython Shell，具有 Scrapling 整合、快捷方式和新工具，可加快 Web Scraping 指令碼開發，例如將 curl 請求轉換為 Scrapling 請求並在瀏覽器中檢視請求結果。
- 🚀 **直接從終端使用**：可選地，您可以使用 Scrapling 抓取 URL 而無需編寫任何程式碼！
- 🛠️ **豐富的導航 API**：使用父級、兄弟級和子級導航方法進行高階 DOM 遍歷。
- 🧬 **增強的文本處理**：內建正則表示式、清理方法和最佳化的字串操作。
- 📝 **自動選擇器生成**：為任何元素生成強大的 CSS/XPath 選擇器。
- 🔌 **熟悉的 API**：類似於 Scrapy/BeautifulSoup，使用與 Scrapy/Parsel 相同的偽元素。
- 📘 **完整的型別覆蓋**：完整的型別提示，出色的 IDE 支援和程式碼補全。整個程式碼庫在每次更改時都會自動使用**PyRight**和**MyPy**掃描。
- 🔋 **現成的 Docker 映象**：每次釋出時，包含所有瀏覽器的 Docker 映象會自動構建和推送。

## 入門

讓我們快速展示 Scrapling 的功能，無需深入瞭解。

### 基本用法
支援 Session 的 HTTP 請求
```python
from scrapling.fetchers import Fetcher, FetcherSession

with FetcherSession(impersonate='chrome') as session:  # 使用 Chrome 的最新版本 TLS fingerprint
    page = session.get('https://quotes.toscrape.com/', stealthy_headers=True)
    quotes = page.css('.quote .text::text').getall()

# 或使用一次性請求
page = Fetcher.get('https://quotes.toscrape.com/')
quotes = page.css('.quote .text::text').getall()
```
高階隱秘模式
```python
from scrapling.fetchers import StealthyFetcher, StealthySession

with StealthySession(headless=True, solve_cloudflare=True) as session:  # 保持瀏覽器開啟直到完成
    page = session.fetch('https://nopecha.com/demo/cloudflare', google_search=False)
    data = page.css('#padded_content a').getall()

# 或使用一次性請求樣式，為此請求開啟瀏覽器，完成後關閉
page = StealthyFetcher.fetch('https://nopecha.com/demo/cloudflare')
data = page.css('#padded_content a').getall()
```
完整的瀏覽器自動化
```python
from scrapling.fetchers import DynamicFetcher, DynamicSession

with DynamicSession(headless=True, disable_resources=False, network_idle=True) as session:  # 保持瀏覽器開啟直到完成
    page = session.fetch('https://quotes.toscrape.com/', load_dom=False)
    data = page.xpath('//span[@class="text"]/text()').getall()  # 如果您偏好 XPath 選擇器

# 或使用一次性請求樣式，為此請求開啟瀏覽器，完成後關閉
page = DynamicFetcher.fetch('https://quotes.toscrape.com/')
data = page.css('.quote .text::text').getall()
```

### Spider
構建具有併發請求、多種 Session 型別和暫停/恢復功能的完整爬蟲：
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
print(f"抓取了 {len(result.items)} 條引用")
result.items.to_json("quotes.json")
```
在單個 Spider 中使用多種 Session 型別：
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
            # 將受保護的頁面路由到隱秘 Session
            if "protected" in link:
                yield Request(link, sid="stealth")
            else:
                yield Request(link, sid="fast", callback=self.parse)  # 顯式 callback
```
透過如下方式執行 Spider 來暫停和恢復長時間爬取，使用 Checkpoint：
```python
QuotesSpider(crawldir="./crawl_data").start()
```
按 Ctrl+C 優雅暫停--進度會自動儲存。之後，當您再次啟動 Spider 時，傳遞相同的 `crawldir`，它將從上次停止的地方繼續。

### 高階解析與導航
```python
from scrapling.fetchers import Fetcher

# 豐富的元素選擇和導航
page = Fetcher.get('https://quotes.toscrape.com/')

# 使用多種選擇方法獲取引用
quotes = page.css('.quote')  # CSS 選擇器
quotes = page.xpath('//div[@class="quote"]')  # XPath
quotes = page.find_all('div', {'class': 'quote'})  # BeautifulSoup 風格
# 等同於
quotes = page.find_all('div', class_='quote')
quotes = page.find_all(['div'], class_='quote')
quotes = page.find_all(class_='quote')  # 等等...
# 按文本內容查詢元素
quotes = page.find_by_text('quote', tag='div')

# 高階導航
quote_text = page.css('.quote')[0].css('.text::text').get()
quote_text = page.css('.quote').css('.text::text').getall()  # 鏈式選擇器
first_quote = page.css('.quote')[0]
author = first_quote.next_sibling.css('.author::text')
parent_container = first_quote.parent

# 元素關係和相似性
similar_elements = first_quote.find_similar()
below_elements = first_quote.below_elements()
```
如果您不想獲取網站，可以直接使用解析器，如下所示：
```python
from scrapling.parser import Selector

page = Selector("<html>...</html>")
```
用法完全相同！

### Async Session 管理示例
```python
import asyncio
from scrapling.fetchers import FetcherSession, AsyncStealthySession, AsyncDynamicSession

async with FetcherSession(http3=True) as session:  # `FetcherSession`是上下文感知的，可以在 sync/async 模式下工作
    page1 = session.get('https://quotes.toscrape.com/')
    page2 = session.get('https://quotes.toscrape.com/', impersonate='firefox135')

# Async Session 用法
async with AsyncStealthySession(max_pages=2) as session:
    tasks = []
    urls = ['https://example.com/page1', 'https://example.com/page2']

    for url in urls:
        task = session.fetch(url)
        tasks.append(task)

    print(session.get_pool_stats())  # 可選 - 瀏覽器標籤池的狀態（忙/空閒/錯誤）
    results = await asyncio.gather(*tasks)
    print(session.get_pool_stats())
```

## CLI 和互動式 Shell

Scrapling 包含強大的命令列介面：

[![asciicast](https://asciinema.org/a/736339.svg)](https://asciinema.org/a/736339)

啟動互動式 Web Scraping Shell
```bash
scrapling shell
```
直接將頁面提取到檔案而無需程式設計（預設提取 `body` 標籤內的內容）。如果輸出檔案以`.txt` 結尾，則將提取目標的文本內容。如果以`.md` 結尾，它將是 HTML 內容的 Markdown 表示；如果以`.html` 結尾，它將是 HTML 內容本身。
```bash
scrapling extract get 'https://example.com' content.md
scrapling extract get 'https://example.com' content.txt --css-selector '#fromSkipToProducts' --impersonate 'chrome'  # 所有匹配 CSS 選擇器'#fromSkipToProducts' 的元素
scrapling extract fetch 'https://example.com' content.md --css-selector '#fromSkipToProducts' --no-headless
scrapling extract stealthy-fetch 'https://nopecha.com/demo/cloudflare' captchas.html --css-selector '#padded_content a' --solve-cloudflare
```

> [!NOTE]
> 還有許多其他功能，但我們希望保持此頁面簡潔，包括 MCP 伺服器和互動式 Web Scraping Shell。檢視完整文件 [這裡](https://scrapling.readthedocs.io/en/latest/)

## 效能基準

Scrapling 不僅功能強大--它還速度極快。以下基準測試將 Scrapling 的解析器與其他流行庫的最新版本進行了比較。

### 文本提取速度測試（5000 個巢狀元素）

| # |         庫         | 時間 (ms)  | vs Scrapling |
|---|:-----------------:|:---------:|:------------:|
| 1 |     Scrapling     |   2.02    |     1.0x     |
| 2 |   Parsel/Scrapy   |   2.04    |     1.01     |
| 3 |     Raw Lxml      |   2.54    |    1.257     |
| 4 |      PyQuery      |   24.17   |     ~12x     |
| 5 |    Selectolax     |   82.63   |     ~41x     |
| 6 |  MechanicalSoup   |  1549.71  |   ~767.1x    |
| 7 |   BS4 with Lxml   |  1584.31  |   ~784.3x    |
| 8 | BS4 with html5lib |  3391.91  |   ~1679.1x   |


### 元素相似性和文本搜尋效能

Scrapling 的自適應元素查詢功能明顯優於替代方案：

| 庫           | 時間 (ms) | vs Scrapling |
|-------------|:---------:|:------------:|
| Scrapling   |   2.39    |     1.0x     |
| AutoScraper |   12.45   |    5.209x    |


> 所有基準測試代表 100+ 次執行的平均值。請參閱 [benchmarks.py](https://github.com/D4Vinci/Scrapling/blob/main/benchmarks.py) 瞭解方法。

## 安裝

Scrapling 需要 Python 3.10 或更高版本：

```bash
pip install scrapling
```

此安裝僅包括解析器引擎及其依賴項，沒有任何 Fetcher 或命令列依賴項。

### 可選依賴項

1. 如果您要使用以下任何額外功能、Fetcher 或它們的類，您將需要安裝 Fetcher 的依賴項和它們的瀏覽器依賴項，如下所示：
    ```bash
    pip install "scrapling[fetchers]"

    scrapling install           # normal install
    scrapling install  --force  # force reinstall
    ```

    這會下載所有瀏覽器，以及它們的系統依賴項和 fingerprint 操作依賴項。

    或者你可以從程式碼中安裝，而不是執行命令：
    ```python
    from scrapling.cli import install

    install([], standalone_mode=False)          # normal install
    install(["--force"], standalone_mode=False) # force reinstall
    ```

2. 額外功能：
   - 安裝 MCP 伺服器功能：
       ```bash
       pip install "scrapling[ai]"
       ```
   - 安裝 Shell 功能（Web Scraping Shell 和 `extract` 命令）：
       ```bash
       pip install "scrapling[shell]"
       ```
   - 安裝所有內容：
       ```bash
       pip install "scrapling[all]"
       ```
   請記住，在安裝任何這些額外功能後（如果您還沒有安裝），您需要使用 `scrapling install` 安裝瀏覽器依賴項

### Docker
您還可以使用以下命令從 DockerHub 安裝包含所有額外功能和瀏覽器的 Docker 映象：
```bash
docker pull pyd4vinci/scrapling
```
或從 GitHub 登錄檔下載：
```bash
docker pull ghcr.io/d4vinci/scrapling:latest
```
此映象使用 GitHub Actions 和倉庫主分支自動構建和推送。

## 貢獻

我們歡迎貢獻！在開始之前，請閱讀我們的 [貢獻指南](https://github.com/D4Vinci/Scrapling/blob/main/CONTRIBUTING.md)。

## 免責宣告

> [!CAUTION]
> 此庫僅用於教育和研究目的。使用此庫即表示您同意遵守本地和國際資料抓取和隱私法律。作者和貢獻者對本軟體的任何濫用不承擔責任。始終尊重網站的服務條款和 robots.txt 檔案。

## 🎓 引用
如果您將我們的庫用於研究目的，請使用以下參考文獻引用我們：
```text
  @misc{scrapling,
    author = {Karim Shoair},
    title = {Scrapling},
    year = {2024},
    url = {https://github.com/D4Vinci/Scrapling},
    note = {An adaptive Web Scraping framework that handles everything from a single request to a full-scale crawl!}
  }
```

## 許可證

本作品根據 BSD-3-Clause 許可證授權。

## 致謝

此專案包含改編自以下內容的程式碼：
- Parsel（BSD 許可證）--用於 [translator](https://github.com/D4Vinci/Scrapling/blob/main/scrapling/core/translator.py)子模組

---
<div align="center"><small>由 Karim Shoair 用❤️設計和製作。</small></div><br>
