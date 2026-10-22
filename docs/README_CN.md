<!-- mcp-name: io.github.D4Vinci/Scrapling -->

<h1 align="center">
    <a href="https://scrapling.readthedocs.io/zh-cn/latest/">
        <picture>
          <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/docs/assets/cover_dark.svg?sanitize=true">
          <img alt="Scrapling 封面" src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/docs/assets/cover_light.svg?sanitize=true">
        </picture>
    </a>
    <br>
    <small>轻松抓取现代网站</small>
</h1>

<p align="center">
    <a href="https://github.com/D4Vinci/Scrapling/actions/workflows/tests.yml" alt="测试">
        <img alt="测试" src="https://github.com/D4Vinci/Scrapling/actions/workflows/tests.yml/badge.svg"></a>
    <a href="https://badge.fury.io/py/Scrapling" alt="PyPI 版本">
        <img alt="PyPI 版本" src="https://badge.fury.io/py/Scrapling.svg"></a>
    <a href="https://hub.docker.com/r/pyd4vinci/scrapling" target="_blank">
        <img alt="Docker 下载次数" src="https://img.shields.io/docker/pulls/pyd4vinci/scrapling?labelColor=%20%23FDB062&logo=Docker&labelColor=%20%23528bff"></a>
    <a href="https://clickpy.clickhouse.com/dashboard/scrapling" rel="nofollow"><img src="https://img.shields.io/pypi/dm/scrapling" alt="PyPI 包下载次数"></a>
    <a href="https://scrapling.readthedocs.io/zh-cn/latest/ai/agent-skill.html" alt="AI 智能体技能">
        <img alt="Agent Skill 徽章" src="https://img.shields.io/badge/Skill-black?style=flat&label=Agent&link=https%3A%2F%2Fscrapling.readthedocs.io%2Fzh-cn%2Flatest%2Fai%2Fagent-skill.html"></a>
    <a href="https://clawhub.ai/D4Vinci/scrapling-official" alt="OpenClaw 技能">
        <img alt="OpenClaw 技能" src="https://img.shields.io/badge/Clawhub-darkred?style=flat&label=OpenClaw&link=https%3A%2F%2Fclawhub.ai%2FD4Vinci%2Fscrapling-official"></a>
    <br/>
    <a href="https://discord.gg/EMgGbDceNQ" alt="Discord" target="_blank">
      <img alt="Discord" src="https://img.shields.io/discord/1360786381042880532?style=social&logo=discord&link=https%3A%2F%2Fdiscord.gg%2FEMgGbDceNQ">
    </a>
    <a href="https://x.com/Scrapling_dev" alt="X（原 Twitter）">
      <img alt="在 X（原 Twitter）上关注" src="https://img.shields.io/twitter/follow/Scrapling_dev?style=social&logo=x&link=https%3A%2F%2Fx.com%2FScrapling_dev">
    </a>
    <br/>
    <a href="https://pypi.org/project/scrapling/" alt="支持的 Python 版本">
        <img alt="支持的 Python 版本" src="https://img.shields.io/pypi/pyversions/scrapling.svg"></a>
</p>

<p align="center">
    <a href="https://scrapling.readthedocs.io/zh-cn/latest/parsing/selection.html"><strong>选择方法</strong></a>
    &middot;
    <a href="https://scrapling.readthedocs.io/zh-cn/latest/fetching/choosing.html"><strong>选择 Fetcher</strong></a>
    &middot;
    <a href="https://scrapling.readthedocs.io/zh-cn/latest/spiders/architecture.html"><strong>爬虫</strong></a>
    &middot;
    <a href="https://scrapling.readthedocs.io/zh-cn/latest/spiders/proxy-blocking.html"><strong>代理轮换</strong></a>
    &middot;
    <a href="https://scrapling.readthedocs.io/zh-cn/latest/cli/overview.html"><strong>CLI</strong></a>
    &middot;
    <a href="https://scrapling.readthedocs.io/zh-cn/latest/ai/mcp-server.html"><strong>MCP 模式</strong></a>
</p>

Scrapling 是一个 Python 网页抓取框架。它将快速 HTTP 请求、隐身浏览器、页面解析和并发爬取整合在一个库中。

抓取静态页面、运行 JavaScript、操作网站，并从网站的 API 中提取数据。构建爬虫时，可以复用会话、轮换代理、自动重试、暂停和恢复任务，还能直接导出数据。

可以在 Python 和终端中使用 Scrapling，也可以通过 MCP 服务器和 Agent Skill 让 AI 智能体使用它。从提取几个字段到将整个网站保存为整洁的 Markdown 文件，Scrapling 都能完成。

## 用 Scrapling 能做什么

- **[获取和操作页面](https://scrapling.readthedocs.io/zh-cn/latest/fetching/choosing.html)**：快速 HTTP 请求、隐身浏览器、JavaScript 渲染、处理 Cloudflare Turnstile 和 Interstitial、持久会话，以及记录后台 API 响应。
- **[解析页面和提取数据](https://scrapling.readthedocs.io/zh-cn/latest/parsing/selection.html)**：使用 CSS、XPath、文本和正则表达式搜索，跟踪页面变化后的元素，查找相似元素，并输出整洁的 Markdown。
- **[爬取和导出](https://scrapling.readthedocs.io/zh-cn/latest/spiders/getting-started.html)**：并发爬虫、代理轮换、重试、AutoThrottle、暂停和恢复、流式输出、现成的模板，以及 JSON、JSONL、CSV 和 XML 导出。
- **[使用 AI 或终端抓取](https://scrapling.readthedocs.io/zh-cn/latest/ai/mcp-server.html)**：供 AI 智能体浏览网页和提取数据的 MCP 服务器、Agent Skill、CLI 命令和交互式 Shell。

从单个页面开始：

```python
from scrapling.fetchers import Fetcher

page = Fetcher.get('https://quotes.toscrape.com/')
quotes = page.css('.quote .text::text').getall()
print(quotes)
```

也可以用 Spider 抓取更多页面：

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

输出 `10`，并将名言和作者保存到 `quotes.json`。

<p align="center">
    <a href="https://dataimpulse.com/?utm_source=scrapling&utm_medium=banner&utm_campaign=scrapling" target="_blank" style="display:flex; justify-content:center; padding:4px 0;">
        <img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/DataImpulse.png" alt="At DataImpulse, we specialize in developing custom proxy services for your business. Make requests from anywhere, collect data, and enjoy fast connections with our premium proxies." style="max-height:60px;">
    </a>
</p>

# 铂金赞助商
<table>
  <tr>
    <td width="200">
      <a href="https://go.nodemaven.com/scraplingoctober" target="_blank" title="Proxies with the Highest IP Scores">
        <img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/NodeMaven.jpg" width="240" height="100">
      </a>
    </td>
    <td>
    <a href="https://go.nodemaven.com/scraplingoctober" target="_blank">NodeMaven</a> - 最高效的网页抓取与自动化代理提供商，拥有市场上质量最高的 IP。使用优惠码 SCRAPLING35 可享 35% 折扣。
    </td>
  </tr>
  <tr>
    <td width="200">
      <a href="https://hypersolutions.co/?utm_source=github&utm_medium=readme&utm_campaign=scrapling" target="_blank" title="Bot Protection Bypass API for Akamai, DataDome, Incapsula & Kasada">
        <img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/HyperSolutions.png">
      </a>
    </td>
    <td> Scrapling 可处理 Cloudflare Turnstile。对于企业级保护，<a href="https://hypersolutions.co?utm_source=github&utm_medium=readme&utm_campaign=scrapling">
        <b>Hyper Solutions</b>
      </a> 提供 API 端点，生成适用于 <b>Akamai</b>、<b>DataDome</b>、<b>Kasada</b> 和 <b>Incapsula</b> 的有效 antibot 令牌。简单的 API 调用，无需浏览器自动化。 </td>
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
      </a>：住宅代理低至 0.49 美元/GB。提供指纹全面伪装的 Chromium 抓取浏览器，配备住宅 IP，并支持自动处理验证码和绕过反机器人防护。</br>
      <b>Scraper API 轻松获取结果。支持 MCP 和 N8N 集成。</b>
    </td>
  </tr>
  <tr>
    <td width="200">
      <a href="https://substack.thewebscraping.club/p/scrapling-hands-on-guide?utm_source=github&utm_medium=repo&utm_campaign=scrapling" target="_blank" title="The #1 newsletter dedicated to Web Scraping">
        <img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/TWSC.png">
      </a>
    </td>
    <td>
    阅读 <a href="https://substack.thewebscraping.club/p/scrapling-hands-on-guide?utm_source=github&utm_medium=repo&utm_campaign=scrapling" target="_blank">The Web Scraping Club 上关于 Scrapling 的完整评测</a>（2025 年 11 月），这是排名第一的网页抓取专业通讯。
    </td>
  </tr>
  <tr>
    <td width="200">
      <a href="https://www.swiftproxy.net/?ref=D4Vinci" target="_blank" title="Scalable Solutions for Web Data Access">
        <img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/SwiftProxy.png">
      </a>
    </td>
    <td>
    <a href="https://www.swiftproxy.net/?ref=D4Vinci" target="_blank">Swiftproxy</a> 提供可扩展的住宅代理，覆盖 195+ 国家/地区的 8000 万+ IP，提供快速可靠的连接、自动轮换和强大的防封禁功能。提供免费试用。
    </td>
  </tr>
  <tr>
    <td width="200">
      <a href="https://byteful.com/?utm_source=github&utm_medium=github-sponsor&utm_campaign=scrapling_github_sponsor" target="_blank" title="Ethically sourced residential proxy infrastructure powering web scraping and AI agents">
        <img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/byteful.png">
      </a>
    </td>
    <td>
    <a href="https://byteful.com/?utm_source=github&utm_medium=github-sponsor&utm_campaign=scrapling_github_sponsor" target="_blank">Byteful</a> 提供符合道德规范的住宅、移动、ISP 和数据中心代理，以及网页抓取和 AI 自动化工具。使用优惠码 SCRAPLING10，住宅代理可享 10% 折扣。
    </td>
  </tr>
  <tr>
    <td width="200">
      <a href="https://proxylane.dev/?utm_source=scrapling&utm_medium=partnership&utm_campaign=scrapling_platinum_202609&utm_content=github_readme" target="_blank" title="28M+ clean residential IPs for browser automation. No Blocks. No CAPTCHAs. Pay-as-you-Go.">
        <img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/proxylane.png">
      </a>
    </td>
    <td>
    <a href="https://proxylane.dev/?utm_source=scrapling&utm_medium=partnership&utm_campaign=scrapling_platinum_202609&utm_content=github_readme" target="_blank">ProxyLane</a>：将封禁和 CAPTCHA 验证码减少 90%。提供 2800 万个优质住宅 IP，适用于大规模网页抓取。覆盖 195 个国家。支持城市、ISP、邮政编码（ZIP）定向。支持使用固定 IP 或轮换 IP 的会话。流量永不过期，低至 $2/GB。使用优惠码 <strong>SCRAPEANDTAKE</strong> 可享 <em>25% 折扣</em>。
    </td>
  </tr>
  <tr>
    <td width="200">
      <a href="https://www.lundproxy.com/unlimited-residential-bandwidth.html?utm_source=github&utm_medium=sponsorship&utm_campaign=scrapling&utm_content=banner" target="_blank" title="Unlimited residential traffic, sized only by bandwidth.">
        <img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/lundproxy.png">
      </a>
    </td>
    <td>
    <a href="https://www.lundproxy.com?utm_source=github&utm_medium=sponsorship&utm_campaign=scrapling&utm_content=text" target="_blank">LundProxy</a>：无需再按 GB 付费。住宅代理流量不限量，1 亿+ IP，覆盖 190+ 个国家。按带宽付费。申请免费试用 50 Mbps 住宅代理。
    </td>
  </tr>
  <tr>
    <td width="200">
      <a href="https://dataimpulse.com/?utm_source=website&utm_medium=github_readme&utm_campaign=scrapling_platinum" target="_blank" title="Buy Pay-as-you-go proxies from $1/GB">
        <img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/DataImpulse_Platinum.png">
      </a>
    </td>
    <td>
    <a href="https://dataimpulse.com/?utm_source=website&utm_medium=github_readme&utm_campaign=scrapling_platinum" target="_blank">DataImpulse</a>，价格为 $1/GB。符合道德规范的第一方代理。9000 万+ IP，覆盖 195+ 个国家。住宅、数据中心、移动代理。按量付费 = 无需订阅。流量永不过期。
    </td>
  </tr>
</table>

<i><sub>想在这里投放广告？点击[这里](https://github.com/sponsors/D4Vinci/sponsorships?tier_id=586646)</sub></i>
# 赞助商

<!-- sponsors -->

<a href="https://cloro.dev/?utm_source=referral&utm_medium=scrapling" target="_blank" title="The search API for the AI era"><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/cloro.jpg"></a>

<br/>

<a href="https://serpapi.com/?utm_source=scrapling" target="_blank" title="Scrape Google and other search engines with SerpApi"><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/SerpApi.png"></a>
<a href="https://visit.decodo.com/Dy6W0b" target="_blank" title="Try the Most Efficient Residential Proxies for Free"><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/decodo.png"></a>
<a href="https://proxyempire.io/?ref=scrapling&utm_source=github&utm_medium=paid_referral&utm_campaign=open_source_sponsorship&utm_content=scrapling" target="_blank" title="Collect The Data Your Project Needs with the Best Residential Proxies"><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/ProxyEmpire.png"></a>
<a href="https://www.webshare.io/?referral_code=48r2m2cd5uz1" target="_blank" title="The Most Reliable Proxy with Unparalleled Performance"><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/webshare.png"></a>
<a href="https://proxiware.com/?ref=scrapling" target="_blank" title="Collect Any Data. At Any Scale."><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/proxiware.png"></a>


<!-- /sponsors -->

<i><sub>想在这里投放广告？点击[这里](https://github.com/sponsors/D4Vinci)，选择合适的方案！</sub></i>

---

## 主要功能

### Spider：完整的爬虫框架

- 🕷️ **类似 Scrapy 的 Spider API**：使用 `start_urls`、异步 `parse` 回调，以及 `Request` 和 `Response` 对象定义爬虫。
- ⚡ **并发爬取**：设置并发请求数、每个域名的并发上限，以及下载间隔。
- 🔄 **多种会话**：在同一个爬虫中使用 HTTP 请求和隐身无头浏览器。按会话 ID 将请求交给不同的会话处理。
- 💾 **暂停和恢复**：用 `crawldir` 保存待处理请求和已访问的 URL。按 Ctrl+C 安全暂停，再用同一个目录启动即可继续。
- 📡 **流式输出**：通过 `async for item in spider.stream()` 在数据提取后立即接收它，并查看实时统计信息。适合界面、数据处理流程和长时间运行的任务。
- 🛡️ **识别被拦截的请求**：自动检测并重试被拦截的请求，也可以自定义处理逻辑。
- 🚦 **AutoThrottle**：根据网站的响应速度，自动调整每个域名的请求间隔。如果网站拦截请求或限制频率，就将间隔加倍，或遵守 `Retry-After` 指定的等待时间。之后再逐步加快。
- 🤖 **遵守 robots.txt**：启用 `robots_txt_obey`，即可遵守 `Disallow`、`Crawl-delay` 和 `Request-rate`。规则按域名缓存。
- 🧪 **开发模式**：首次运行时将响应保存到磁盘，之后直接复用。这样可以修改 `parse()`，而不必再次请求服务器。
- 🧩 **现成的爬虫模板**：使用 `CrawlSpider` 按规则跟踪链接，使用 `SitemapSpider` 从 sitemap 或 robots.txt 开始爬取，使用 `XMLFeedSpider` 和 `CSVFeedSpider` 读取 XML、RSS 和 CSV 数据源，或使用 `ShopifySpider` 获取公开 Shopify 商店的商品，每个商品变体生成一条数据。
- 🔗 **提取链接**：`LinkExtractor` 可用模式允许或排除链接，过滤域名和文件扩展名，用 CSS 或 XPath 限定范围，并规范化 URL。它既可配合模板使用，也可单独使用。
- 📦 **内置导出**：用钩子和自己的处理流程导出数据，或使用内置的 JSON、JSONL、CSV 和 XML 方法：`result.items.to_json()`、`to_jsonl()`、`to_csv()` 和 `to_xml()`。

### 使用会话获取页面

- **HTTP 请求**：用 `Fetcher` 发送快速、隐蔽的 HTTP 请求。支持模拟浏览器的 TLS 指纹和请求头，也支持 HTTP/3。
- **动态加载**：用 `StealthyFetcher` 的完整浏览器自动化功能抓取动态网站。支持 Playwright 的 Chromium 和 Google Chrome。
- **绕过反爬检测**：`StealthyFetcher` 隐藏自动化特征并模拟浏览器指纹，能自动处理多种 Cloudflare Turnstile 和 Interstitial 验证。
- **会话管理**：`FetcherSession` 和 `StealthySession` 可在多次请求之间保留 Cookie 和状态。
- **代理轮换**：`ProxyRotator` 支持在所有会话类型中按顺序或自定义规则切换代理，也可以为单次请求指定代理。
- **拦截域名和广告**：拦截指定域名及其子域名的请求，或启用浏览器 Fetcher 的广告拦截功能。内置列表包含约 3,500 个已知广告和跟踪域名。
- **防止 DNS 泄漏**：启用 DNS-over-HTTPS，通过 Cloudflare 的 DoH 服务发送 DNS 查询，防止使用代理时泄漏 DNS。
- **远程浏览器**：通过 CDP 和 `cdp_url` 连接已运行的浏览器，包括本机、远程服务器和浏览器服务商提供的浏览器。也可以用 `executable_path` 为任意浏览器 Fetcher 指定自己的 Chromium 程序。
- **记录后台 API 响应**：在浏览器会话中启用 `record_requests=True`，再用 `session.network.search(limit=None)` 搜索已保存的响应。无需重复请求，即可读取多次页面访问中的 API 数据和 HTTP 错误。历史记录有大小上限，只保存文本响应的内容。
- **异步支持**：所有 Fetcher 都支持异步操作，并提供专用的异步会话类。

### 解析页面和提取数据

- 🔄 **重新定位元素**：网站结构改变后，用相似度算法重新找到元素。
- 🎯 **灵活选择**：支持 CSS、XPath、过滤器、文本、正则表达式等方式。
- 🔍 **相似元素**：自动查找与已选元素相似的元素。

### AI 功能

- 🤖 **MCP 服务器**：让 Claude、Cursor 等 AI 助手和智能体通过 Scrapling 提取数据。支持 HTTP 请求、浏览器操作、截图、保存的登录状态和后台 API 响应。它使用我们的隐身浏览器，并提供工具，让具备相应能力的模型处理 CAPTCHA，补充内置的 Cloudflare 验证处理功能。它还减少发送给模型的内容、拦截广告，并防护提示词注入。支持通过 CDP 连接远程浏览器，也支持带身份验证选项的 HTTP 连接。（[演示视频](https://www.youtube.com/watch?v=qyFk3ZNwOxE)）
- 🧠 **Agent Skill**：可安装的 [Agent Skill](https://scrapling.readthedocs.io/zh-cn/latest/ai/agent-skill.html)，帮助编程智能体了解这个库，并编写符合当前 API 的代码。
- 📚 **用于 RAG 的 Markdown**：用一行代码（`page.markdown()`）将页面转成适合语言模型的整洁 Markdown，或用 `ContentSpider` 模板将整个网站保存为 Markdown 文件。无需语言模型。（[文档](https://scrapling.readthedocs.io/zh-cn/latest/ai/building-rag-systems.html)）

### 快速且经过实际使用

- 🚀 **速度快**：经过优化，性能超过大多数 Python 网页抓取库。
- 🔋 **内存占用低**：使用优化的数据结构，并按需加载。
- ⚡ **快速输出 JSON**：速度是标准库的 10 倍。
- 🏗️ **经过实际检验**：测试覆盖率达 92%，全部代码都有类型注解。过去一年中，数百人每天用它提取数据。

### 开发和数据提取工具

- 🎯 **交互式 Shell**：可选的 IPython Shell，内置 Scrapling、快捷命令和工具，方便快速开发抓取脚本。可将 curl 请求转成 Scrapling 请求，并在浏览器中查看结果。
- 🚀 **命令行使用**：无需写代码，就能提取 URL 的内容。
- 🛠️ **DOM 导航**：访问父元素、同级元素和子元素。
- 🧬 **文本处理**：支持正则表达式、文本清理和优化的字符串操作。
- 📝 **生成选择器**：为任意元素生成可靠的 CSS 和 XPath 选择器。
- 🔌 **熟悉的 API**：与 Scrapy 和 BeautifulSoup 相似，并支持 Scrapy 和 Parsel 使用的伪元素。
- 🤝 **直接集成 Scrapy**：给回调加上 `scrapling_response` 装饰器，就能用 Scrapling 解析器处理已有的 Scrapy 响应，无需重写程序。
- 📘 **完整的类型注解**：帮助编辑器检查和补全代码。每次修改都会用 **PyRight** 和 **MyPy** 自动检查全部代码。
- 🔋 **现成的 Docker 镜像**：每次发布新版本时，自动构建并发布包含所有浏览器的 Docker 镜像。

## 入门

下面是一些常见用法。

### 基本用法
使用会话发送 HTTP 请求
```python
from scrapling.fetchers import Fetcher, FetcherSession

with FetcherSession(impersonate='chrome') as session:  # 使用 Chrome 的最新版本 TLS fingerprint
    page = session.get('https://quotes.toscrape.com/', stealthy_headers=True)
    quotes = page.css('.quote .text::text').getall()

# 或使用一次性请求
page = Fetcher.get('https://quotes.toscrape.com/')
quotes = page.css('.quote .text::text').getall()
```
隐身模式
```python
from scrapling.fetchers import StealthyFetcher, StealthySession

with StealthySession(headless=True, solve_cloudflare=True) as session:  # 保持浏览器打开直到完成
    page = session.fetch('https://nopecha.com/demo/cloudflare', google_search=False)
    data = page.css('#padded_content a').getall()

# 或使用一次性请求样式，为此请求打开浏览器，完成后关闭
page = StealthyFetcher.fetch('https://nopecha.com/demo/cloudflare', solve_cloudflare=True)
data = page.css('#padded_content a').getall()
```
完整的浏览器自动化
```python
from scrapling.fetchers import StealthyFetcher, StealthySession

with StealthySession(headless=True, disable_resources=False, network_idle=True) as session:  # 保持浏览器打开直到完成
    page = session.fetch('https://quotes.toscrape.com/', load_dom=False)
    data = page.xpath('//span[@class="text"]/text()').getall()  # 如果您偏好 XPath 选择器

# 或使用一次性请求样式，为此请求打开浏览器，完成后关闭
page = StealthyFetcher.fetch('https://quotes.toscrape.com/')
data = page.css('.quote .text::text').getall()
```

### Spider
构建支持并发请求、多种会话、暂停和恢复的完整爬虫：
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
print(f"抓取了 {len(result.items)} 条引用")
result.items.to_json("quotes.json")
```
在同一个 Spider 中使用多种会话：
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
            # 将受保护的页面路由到隐秘 Session
            if "protected" in link:
                yield Request(link, sid="stealth")
            else:
                yield Request(link, sid="fast", callback=self.parse)  # 显式 callback
```
保存进度，就能暂停和恢复长时间运行的任务。这样启动 Spider：
```python
QuotesSpider(crawldir="./crawl_data").start()
```
设置 `crawldir` 后，按 Ctrl+C 保存待处理请求和已访问 URL。使用同一个 `crawldir` 重启即可继续。请单独保存提取的数据。

也可以使用现成的模板，例如获取整个 Shopify 商店的商品目录：
```python
from scrapling.spiders import ShopifySpider

class MyStore(ShopifySpider):
    target_website = "example.com"

result = MyStore().start()  # 店铺中的所有商品，每个变体一条记录
```
模板从公开的商品集合接口读取商品，每个商品变体生成一条数据。

### 高级解析与导航
```python
from scrapling.fetchers import Fetcher

# 丰富的元素选择和导航
page = Fetcher.get('https://quotes.toscrape.com/')

# 使用多种选择方法获取引用
quotes = page.css('.quote')  # CSS 选择器
quotes = page.xpath('//div[@class="quote"]')  # XPath
quotes = page.find_all('div', {'class': 'quote'})  # BeautifulSoup 风格
# 等同于
quotes = page.find_all('div', class_='quote')
quotes = page.find_all(['div'], class_='quote')
quotes = page.find_all(class_='quote')  # 等等...
# 按文本内容查找元素
quotes = page.find_by_text('Albert Einstein', first_match=False)

# 高级导航
quote_text = page.css('.quote')[0].css('.text::text').get()
quote_texts = page.css('.quote').css('.text::text').getall()  # 链式选择器
first_quote = page.css('.quote')[0]
author = first_quote.css('.author::text').get()
next_quote = first_quote.next
parent_container = first_quote.parent

# 元素关系和相似性
similar_elements = first_quote.find_similar()
below_elements = first_quote.below_elements
```
也可以直接使用解析器，无需先获取网页：
```python
from scrapling.parser import Selector

page = Selector("<html>...</html>")
```
用法相同。

### 异步会话示例
```python
import asyncio
from scrapling.fetchers import FetcherSession, AsyncStealthySession

async def main():
    async with FetcherSession(http3=True) as http_session:  # `FetcherSession` 能识别上下文，同时支持同步和异步用法
        page1 = await http_session.get('https://quotes.toscrape.com/')
        page2 = await http_session.get('https://quotes.toscrape.com/page/2/', impersonate='chrome')
        print(len(page1.css('.quote')), len(page2.css('.quote')))

    async with AsyncStealthySession(max_pages=2) as browser_session:
        urls = ['https://quotes.toscrape.com/js/', 'https://quotes.toscrape.com/js/page/2/']
        pages = await asyncio.gather(*(browser_session.fetch(url, wait_selector='.quote') for url in urls))
        print([len(page.css('.quote')) for page in pages])

asyncio.run(main())
```

## CLI 和交互式 Shell

也可以在终端中使用 Scrapling：

[![asciicast](https://asciinema.org/a/736339.svg)](https://asciinema.org/a/736339)

启动交互式网页抓取 Shell：
```bash
pip install "scrapling[shell]"
scrapling shell
```
无需编程即可将页面直接提取到文件。使用 `--css-selector` 选择内容，或用 `--ai-targeted` 选择并清理 `body` 内容。使用 `.txt` 输出文本、`.md` 输出 Markdown，或 `.html` 输出 HTML。
```bash
scrapling extract get 'https://quotes.toscrape.com/' quotes.md
scrapling extract get 'https://quotes.toscrape.com/' quotes.txt --css-selector '.quote' --impersonate 'chrome'
scrapling extract fetch 'https://quotes.toscrape.com/js/' quotes.md --css-selector '.quote' --wait-selector '.quote' --no-headless
scrapling extract fetch 'https://nopecha.com/demo/cloudflare' captchas.html --css-selector '#padded_content a' --solve-cloudflare
```

> [!NOTE]
> 更多功能，包括 MCP 服务器和交互式 Shell，请查看[完整文档](https://scrapling.readthedocs.io/zh-cn/latest/)。

## 性能测试

Scrapling 的速度也很出色。下面对比它的解析器和其他常用库的最新版本。

### 文本提取速度（5,000 个嵌套元素）

| # |         库         | 时间（毫秒）  | 相对 Scrapling |
|---|:-----------------:|:---------:|:------------:|
| 1 |     Scrapling     |   1.99    |     1.0x     |
| 2 |   Parsel/Scrapy   |   2.06    |    1.035     |
| 3 |     原生 Lxml      |   2.56    |    1.286     |
| 4 |      PyQuery      |   23.98   |     ~12x     |
| 5 |    Selectolax     |  197.02   |     ~99x     |
| 6 |  MechanicalSoup   |  1545.15  |   ~776.5x    |
| 7 |   BS4 + Lxml   |  1562.1   |   ~785.0x    |
| 8 | BS4 + html5lib |  3412.73  |   ~1714.9x   |


### 相似元素和文本搜索

Scrapling 的自适应元素查找比其他方案更快：

| 库           | 时间（毫秒） | 相对 Scrapling |
|-------------|:---------:|:------------:|
| Scrapling   |    2.3    |     1.0x     |
| AutoScraper |   12.58   |    5.47x     |


> 每项结果都是至少 100 次运行的平均值。测试方法见 [benchmarks.py](https://github.com/D4Vinci/Scrapling/blob/main/benchmarks.py)。

## 安装

Scrapling 需要 Python 3.10 或更高版本：

```bash
pip install scrapling
```

> [!IMPORTANT]
> 这个命令只安装解析器及其依赖，不包含 Fetcher 或命令行工具。仅安装这些依赖后，像上面的示例那样从 `scrapling.fetchers` 或 `scrapling.spiders` 导入内容，会出现 `ModuleNotFoundError`。要使用 Fetcher 或 Spider，请先按下文安装 Fetcher 的依赖。

### 可选依赖

1. 要使用 Fetcher、相关类或下列扩展功能，请先安装 Fetcher 和浏览器的依赖：
    ```bash
    pip install "scrapling[fetchers]"

    scrapling install           # normal install
    scrapling install  --force  # force reinstall
    ```

    这会下载所有浏览器、所需的系统依赖，以及修改浏览器指纹的工具。

    也可以在 Python 代码中安装，无需运行命令：
    ```python
    from scrapling.cli import install

    install([], standalone_mode=False)          # normal install
    install(["--force"], standalone_mode=False) # force reinstall
    ```

2. 扩展功能：
   - 安装 MCP 服务器：
       ```bash
       pip install "scrapling[ai]"
       ```
   - 安装[构建 RAG 系统](https://scrapling.readthedocs.io/zh-cn/latest/ai/building-rag-systems.html)所需的依赖：
       ```bash
       pip install "scrapling[rag]"
       ```
   - 安装交互式 Shell 和 `extract` 命令：
       ```bash
       pip install "scrapling[shell]"
       ```
   - 安装所有功能：
       ```bash
       pip install "scrapling[all]"
       ```
   如果要使用浏览器 Fetcher，请运行 `scrapling install`。HTTP 请求不需要安装浏览器。

### Docker
也可以从 DockerHub 下载包含所有扩展功能和浏览器的 Docker 镜像：
```bash
docker pull pyd4vinci/scrapling
```
或从 GitHub 容器仓库下载：
```bash
docker pull ghcr.io/d4vinci/scrapling:latest
```
镜像基于仓库的主分支构建，由 GitHub Actions 自动发布。

## 贡献

欢迎参与项目！开始前，请阅读[贡献指南](https://github.com/D4Vinci/Scrapling/blob/main/CONTRIBUTING.md)。

## 免责声明

> [!CAUTION]
> 本库仅用于学习和研究。使用本库即表示同意遵守当地和国际上的数据抓取及隐私法律。作者和贡献者不对软件被滥用承担责任。请遵守网站的服务条款和 robots.txt 文件。

## 🎓 引用
如果在研究中使用本库，请按以下格式引用：
```text
  @misc{scrapling,
    author = {Karim Shoair},
    title = {Scrapling},
    year = {2024},
    url = {https://github.com/D4Vinci/Scrapling},
    note = {A Python Web Scraping framework for everything from a single request to a full-scale crawl!}
  }
```

## 许可证

本项目使用 BSD-3-Clause 许可证。

## 致谢

本项目包含改编自以下项目的代码：
- Parsel（BSD 许可证）：用于 [translator](https://github.com/D4Vinci/Scrapling/blob/main/scrapling/core/translator.py) 子模块

---
<div align="center"><small>由 Karim Shoair 用❤️设计和制作。</small></div><br>
