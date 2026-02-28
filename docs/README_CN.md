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
    <a href="https://pepy.tech/project/scrapling" alt="PyPI Downloads">
        <img alt="PyPI Downloads" src="https://static.pepy.tech/personalized-badge/scrapling?period=total&units=INTERNATIONAL_SYSTEM&left_color=GREY&right_color=GREEN&left_text=Downloads"></a>
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
    <a href="https://scrapling.readthedocs.io/en/latest/parsing/selection/"><strong>选择方法</strong></a>
    &middot;
    <a href="https://scrapling.readthedocs.io/en/latest/fetching/choosing/"><strong>选择Fetcher</strong></a>
    &middot;
    <a href="https://scrapling.readthedocs.io/en/latest/spiders/architecture.html"><strong>爬虫</strong></a>
    &middot;
    <a href="https://scrapling.readthedocs.io/en/latest/spiders/proxy-blocking.html"><strong>代理轮换</strong></a>
    &middot;
    <a href="https://scrapling.readthedocs.io/en/latest/cli/overview/"><strong>CLI</strong></a>
    &middot;
    <a href="https://scrapling.readthedocs.io/en/latest/ai/mcp-server/"><strong>MCP模式</strong></a>
</p>

Scrapling是一个自适应Web Scraping框架，能处理从单个请求到大规模爬取的一切需求。

它的解析器能够从网站变化中学习，并在页面更新时自动重新定位您的元素。它的Fetcher能够开箱即用地绕过Cloudflare Turnstile等反机器人系统。它的Spider框架让您可以扩展到并发、多Session爬取，支持暂停/恢复和自动Proxy轮换——只需几行Python代码。一个库，零妥协。

极速爬取，实时统计和Streaming。由Web Scraper为Web Scraper和普通用户而构建，每个人都能找到适合自己的功能。

```python
from scrapling.fetchers import Fetcher, AsyncFetcher, StealthyFetcher, DynamicFetcher
StealthyFetcher.adaptive = True
p = StealthyFetcher.fetch('https://example.com', headless=True, network_idle=True)  # 隐秘地获取网站！
products = p.css('.product', auto_save=True)                                        # 抓取在网站设计变更后仍能存活的数据！
products = p.css('.product', adaptive=True)                                         # 之后，如果网站结构改变，传递 `adaptive=True` 来找到它们！
```
或扩展为完整爬取
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


# 铂金赞助商

<i><sub>想成为第一个出现在这里的公司吗？点击[这里](https://github.com/sponsors/D4Vinci/sponsorships?tier_id=586646)</sub></i>
# 赞助商

<!-- sponsors -->

<a href="https://www.thordata.com/?ls=github&lk=github" target="_blank" title="Unblockable proxies and scraping infrastructure, delivering real-time, reliable web data to power AI models and workflows."><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/thordata.jpg"></a>
<a href="https://evomi.com?utm_source=github&utm_medium=banner&utm_campaign=d4vinci-scrapling" target="_blank" title="Evomi is your Swiss Quality Proxy Provider, starting at $0.49/GB"><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/evomi.png"></a>
<a href="https://serpapi.com/?utm_source=scrapling" target="_blank" title="Scrape Google and other search engines with SerpApi"><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/SerpApi.png"></a>
<a href="https://visit.decodo.com/Dy6W0b" target="_blank" title="Try the Most Efficient Residential Proxies for Free"><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/decodo.png"></a>
<a href="https://petrosky.io/d4vinci" target="_blank" title="PetroSky delivers cutting-edge VPS hosting."><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/petrosky.png"></a>
<a href="https://hasdata.com/?utm_source=github&utm_medium=banner&utm_campaign=D4Vinci" target="_blank" title="The web scraping service that actually beats anti-bot systems!"><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/hasdata.png"></a>
<a href="https://proxyempire.io/?ref=scrapling&utm_source=scrapling" target="_blank" title="Collect The Data Your Project Needs with the Best Residential Proxies"><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/ProxyEmpire.png"></a>
<a href="https://hypersolutions.co/?utm_source=github&utm_medium=readme&utm_campaign=scrapling" target="_blank" title="Bot Protection Bypass API for Akamai, DataDome, Incapsula & Kasada"><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/HyperSolutions.png"></a>


<a href="https://www.swiftproxy.net/" target="_blank" title="Unlock Reliable Proxy Services with Swiftproxy!"><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/swiftproxy.png"></a>
<a href="https://www.rapidproxy.io/?ref=d4v" target="_blank" title="Affordable Access to the Proxy World – bypass CAPTCHAs blocks, and avoid additional costs."><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/rapidproxy.jpg"></a>
<a href="https://browser.cash/?utm_source=D4Vinci&utm_medium=referral" target="_blank" title="Browser Automation & AI Browser Agent Platform"><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/browserCash.png"></a>

<!-- /sponsors -->

<i><sub>想在这里展示您的广告吗？点击[这里](https://github.com/sponsors/D4Vinci)并选择适合您的级别！</sub></i>

---

## 主要特性

### Spider — 完整的爬取框架
- 🕷️ **类Scrapy的Spider API**：使用`start_urls`、async `parse` callback和`Request`/`Response`对象定义Spider。
- ⚡ **并发爬取**：可配置的并发限制、按域名节流和下载延迟。
- 🔄 **多Session支持**：统一接口，支持HTTP请求和隐秘无头浏览器在同一个Spider中使用——通过ID将请求路由到不同的Session。
- 💾 **暂停与恢复**：基于Checkpoint的爬取持久化。按Ctrl+C优雅关闭；重启后从上次停止的地方继续。
- 📡 **Streaming模式**：通过`async for item in spider.stream()`以实时统计Streaming抓取的数据——非常适合UI、管道和长时间运行的爬取。
- 🛡️ **被阻止请求检测**：自动检测并重试被阻止的请求，支持自定义逻辑。
- 📦 **内置导出**：通过钩子和您自己的管道导出结果，或使用内置的JSON/JSONL，分别通过`result.items.to_json()`/`result.items.to_jsonl()`。

### 支持Session的高级网站获取
- **HTTP请求**：使用`Fetcher`类进行快速和隐秘的HTTP请求。可以模拟浏览器的TLS fingerprint、标头并使用HTTP/3。
- **动态加载**：通过`DynamicFetcher`类使用完整的浏览器自动化获取动态网站，支持Playwright的Chromium和Google Chrome。
- **反机器人绕过**：使用`StealthyFetcher`的高级隐秘功能和fingerprint伪装。可以轻松自动绕过所有类型的Cloudflare Turnstile/Interstitial。
- **Session管理**：使用`FetcherSession`、`StealthySession`和`DynamicSession`类实现持久化Session支持，用于跨请求的cookie和状态管理。
- **Proxy轮换**：内置`ProxyRotator`，支持轮询或自定义策略，适用于所有Session类型，并支持按请求覆盖Proxy。
- **域名屏蔽**：在基于浏览器的Fetcher中屏蔽对特定域名（及其子域名）的请求。
- **Async支持**：所有Fetcher和专用async Session类的完整async支持。

### 自适应抓取和AI集成
- 🔄 **智能元素跟踪**：使用智能相似性算法在网站更改后重新定位元素。
- 🎯 **智能灵活选择**：CSS选择器、XPath选择器、基于过滤器的搜索、文本搜索、正则表达式搜索等。
- 🔍 **查找相似元素**：自动定位与已找到元素相似的元素。
- 🤖 **与AI一起使用的MCP服务器**：内置MCP服务器用于AI辅助Web Scraping和数据提取。MCP服务器具有强大的自定义功能，利用Scrapling在将内容传递给AI（Claude/Cursor等）之前提取目标内容，从而加快操作并通过最小化token使用来降低成本。（[演示视频](https://www.youtube.com/watch?v=qyFk3ZNwOxE)）

### 高性能和经过实战测试的架构
- 🚀 **闪电般快速**：优化性能超越大多数Python抓取库。
- 🔋 **内存高效**：优化的数据结构和延迟加载，最小内存占用。
- ⚡ **快速JSON序列化**：比标准库快10倍。
- 🏗️ **经过实战测试**：Scrapling不仅拥有92%的测试覆盖率和完整的类型提示覆盖率，而且在过去一年中每天被数百名Web Scraper使用。

### 对开发者/Web Scraper友好的体验
- 🎯 **交互式Web Scraping Shell**：可选的内置IPython Shell，具有Scrapling集成、快捷方式和新工具，可加快Web Scraping脚本开发，例如将curl请求转换为Scrapling请求并在浏览器中查看请求结果。
- 🚀 **直接从终端使用**：可选地，您可以使用Scrapling抓取URL而无需编写任何代码！
- 🛠️ **丰富的导航API**：使用父级、兄弟级和子级导航方法进行高级DOM遍历。
- 🧬 **增强的文本处理**：内置正则表达式、清理方法和优化的字符串操作。
- 📝 **自动选择器生成**：为任何元素生成强大的CSS/XPath选择器。
- 🔌 **熟悉的API**：类似于Scrapy/BeautifulSoup，使用与Scrapy/Parsel相同的伪元素。
- 📘 **完整的类型覆盖**：完整的类型提示，出色的IDE支持和代码补全。整个代码库在每次更改时都会自动使用**PyRight**和**MyPy**扫描。
- 🔋 **现成的Docker镜像**：每次发布时，包含所有浏览器的Docker镜像会自动构建和推送。

## 入门

让我们快速展示Scrapling的功能，无需深入了解。

### 基本用法
支持Session的HTTP请求
```python
from scrapling.fetchers import Fetcher, FetcherSession

with FetcherSession(impersonate='chrome') as session:  # 使用Chrome的最新版本TLS fingerprint
    page = session.get('https://quotes.toscrape.com/', stealthy_headers=True)
    quotes = page.css('.quote .text::text').getall()

# 或使用一次性请求
page = Fetcher.get('https://quotes.toscrape.com/')
quotes = page.css('.quote .text::text').getall()
```
高级隐秘模式
```python
from scrapling.fetchers import StealthyFetcher, StealthySession

with StealthySession(headless=True, solve_cloudflare=True) as session:  # 保持浏览器打开直到完成
    page = session.fetch('https://nopecha.com/demo/cloudflare', google_search=False)
    data = page.css('#padded_content a').getall()

# 或使用一次性请求样式，为此请求打开浏览器，完成后关闭
page = StealthyFetcher.fetch('https://nopecha.com/demo/cloudflare')
data = page.css('#padded_content a').getall()
```
完整的浏览器自动化
```python
from scrapling.fetchers import DynamicFetcher, DynamicSession

with DynamicSession(headless=True, disable_resources=False, network_idle=True) as session:  # 保持浏览器打开直到完成
    page = session.fetch('https://quotes.toscrape.com/', load_dom=False)
    data = page.xpath('//span[@class="text"]/text()').getall()  # 如果您偏好XPath选择器

# 或使用一次性请求样式，为此请求打开浏览器，完成后关闭
page = DynamicFetcher.fetch('https://quotes.toscrape.com/')
data = page.css('.quote .text::text').getall()
```

### Spider
构建具有并发请求、多种Session类型和暂停/恢复功能的完整爬虫：
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
print(f"抓取了 {len(result.items)} 条引用")
result.items.to_json("quotes.json")
```
在单个Spider中使用多种Session类型：
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
            # 将受保护的页面路由到隐秘Session
            if "protected" in link:
                yield Request(link, sid="stealth")
            else:
                yield Request(link, sid="fast", callback=self.parse)  # 显式callback
```
通过如下方式运行Spider来暂停和恢复长时间爬取，使用Checkpoint：
```python
QuotesSpider(crawldir="./crawl_data").start()
```
按Ctrl+C优雅暂停——进度会自动保存。之后，当您再次启动Spider时，传递相同的`crawldir`，它将从上次停止的地方继续。

### 高级解析与导航
```python
from scrapling.fetchers import Fetcher

# 丰富的元素选择和导航
page = Fetcher.get('https://quotes.toscrape.com/')

# 使用多种选择方法获取引用
quotes = page.css('.quote')  # CSS选择器
quotes = page.xpath('//div[@class="quote"]')  # XPath
quotes = page.find_all('div', {'class': 'quote'})  # BeautifulSoup风格
# 等同于
quotes = page.find_all('div', class_='quote')
quotes = page.find_all(['div'], class_='quote')
quotes = page.find_all(class_='quote')  # 等等...
# 按文本内容查找元素
quotes = page.find_by_text('quote', tag='div')

# 高级导航
quote_text = page.css('.quote')[0].css('.text::text').get()
quote_text = page.css('.quote').css('.text::text').getall()  # 链式选择器
first_quote = page.css('.quote')[0]
author = first_quote.next_sibling.css('.author::text')
parent_container = first_quote.parent

# 元素关系和相似性
similar_elements = first_quote.find_similar()
below_elements = first_quote.below_elements()
```
如果您不想获取网站，可以直接使用解析器，如下所示：
```python
from scrapling.parser import Selector

page = Selector("<html>...</html>")
```
用法完全相同！

### Async Session管理示例
```python
import asyncio
from scrapling.fetchers import FetcherSession, AsyncStealthySession, AsyncDynamicSession

async with FetcherSession(http3=True) as session:  # `FetcherSession`是上下文感知的，可以在sync/async模式下工作
    page1 = session.get('https://quotes.toscrape.com/')
    page2 = session.get('https://quotes.toscrape.com/', impersonate='firefox135')

# Async Session用法
async with AsyncStealthySession(max_pages=2) as session:
    tasks = []
    urls = ['https://example.com/page1', 'https://example.com/page2']

    for url in urls:
        task = session.fetch(url)
        tasks.append(task)

    print(session.get_pool_stats())  # 可选 - 浏览器标签池的状态（忙/空闲/错误）
    results = await asyncio.gather(*tasks)
    print(session.get_pool_stats())
```

## CLI和交互式Shell

Scrapling包含强大的命令行界面：

[![asciicast](https://asciinema.org/a/736339.svg)](https://asciinema.org/a/736339)

启动交互式Web Scraping Shell
```bash
scrapling shell
```
直接将页面提取到文件而无需编程（默认提取`body`标签内的内容）。如果输出文件以`.txt`结尾，则将提取目标的文本内容。如果以`.md`结尾，它将是HTML内容的Markdown表示；如果以`.html`结尾，它将是HTML内容本身。
```bash
scrapling extract get 'https://example.com' content.md
scrapling extract get 'https://example.com' content.txt --css-selector '#fromSkipToProducts' --impersonate 'chrome'  # 所有匹配CSS选择器'#fromSkipToProducts'的元素
scrapling extract fetch 'https://example.com' content.md --css-selector '#fromSkipToProducts' --no-headless
scrapling extract stealthy-fetch 'https://nopecha.com/demo/cloudflare' captchas.html --css-selector '#padded_content a' --solve-cloudflare
```

> [!NOTE]
> 还有许多其他功能，但我们希望保持此页面简洁，包括MCP服务器和交互式Web Scraping Shell。查看完整文档[这里](https://scrapling.readthedocs.io/en/latest/)

## 性能基准

Scrapling不仅功能强大——它还速度极快。以下基准测试将Scrapling的解析器与其他流行库的最新版本进行了比较。

### 文本提取速度测试（5000个嵌套元素）

| # |         库         | 时间(ms)  | vs Scrapling |
|---|:-----------------:|:---------:|:------------:|
| 1 |     Scrapling     |   2.02    |     1.0x     |
| 2 |   Parsel/Scrapy   |   2.04    |     1.01     |
| 3 |     Raw Lxml      |   2.54    |    1.257     |
| 4 |      PyQuery      |   24.17   |     ~12x     |
| 5 |    Selectolax     |   82.63   |     ~41x     |
| 6 |  MechanicalSoup   |  1549.71  |   ~767.1x    |
| 7 |   BS4 with Lxml   |  1584.31  |   ~784.3x    |
| 8 | BS4 with html5lib |  3391.91  |   ~1679.1x   |


### 元素相似性和文本搜索性能

Scrapling的自适应元素查找功能明显优于替代方案：

| 库           | 时间(ms) | vs Scrapling |
|-------------|:---------:|:------------:|
| Scrapling   |   2.39    |     1.0x     |
| AutoScraper |   12.45   |    5.209x    |


> 所有基准测试代表100+次运行的平均值。请参阅[benchmarks.py](https://github.com/D4Vinci/Scrapling/blob/main/benchmarks.py)了解方法。

## 安装

Scrapling需要Python 3.10或更高版本：

```bash
pip install scrapling
```

此安装仅包括解析器引擎及其依赖项，没有任何Fetcher或命令行依赖项。

### 可选依赖项

1. 如果您要使用以下任何额外功能、Fetcher或它们的类，您将需要安装Fetcher的依赖项和它们的浏览器依赖项，如下所示：
    ```bash
    pip install "scrapling[fetchers]"

    scrapling install           # normal install
    scrapling install  --force  # force reinstall
    ```

    这会下载所有浏览器，以及它们的系统依赖项和fingerprint操作依赖项。

    或者你可以从代码中安装，而不是运行命令：
    ```python
    from scrapling.cli import install

    install([], standalone_mode=False)          # normal install
    install(["--force"], standalone_mode=False) # force reinstall
    ```

2. 额外功能：
   - 安装MCP服务器功能：
       ```bash
       pip install "scrapling[ai]"
       ```
   - 安装Shell功能（Web Scraping Shell和`extract`命令）：
       ```bash
       pip install "scrapling[shell]"
       ```
   - 安装所有内容：
       ```bash
       pip install "scrapling[all]"
       ```
   请记住，在安装任何这些额外功能后（如果您还没有安装），您需要使用`scrapling install`安装浏览器依赖项

### Docker
您还可以使用以下命令从DockerHub安装包含所有额外功能和浏览器的Docker镜像：
```bash
docker pull pyd4vinci/scrapling
```
或从GitHub注册表下载：
```bash
docker pull ghcr.io/d4vinci/scrapling:latest
```
此镜像使用GitHub Actions和仓库主分支自动构建和推送。

## 贡献

我们欢迎贡献！在开始之前，请阅读我们的[贡献指南](https://github.com/D4Vinci/Scrapling/blob/main/CONTRIBUTING.md)。

## 免责声明

> [!CAUTION]
> 此库仅用于教育和研究目的。使用此库即表示您同意遵守本地和国际数据抓取和隐私法律。作者和贡献者对本软件的任何滥用不承担责任。始终尊重网站的服务条款和robots.txt文件。

## 🎓 引用
如果您将我们的库用于研究目的，请使用以下参考文献引用我们：
```text
  @misc{scrapling,
    author = {Karim Shoair},
    title = {Scrapling},
    year = {2024},
    url = {https://github.com/D4Vinci/Scrapling},
    note = {An adaptive Web Scraping framework that handles everything from a single request to a full-scale crawl!}
  }
```

## 许可证

本作品根据BSD-3-Clause许可证授权。

## 致谢

此项目包含改编自以下内容的代码：
- Parsel（BSD许可证）——用于[translator](https://github.com/D4Vinci/Scrapling/blob/main/scrapling/core/translator.py)子模块

---
<div align="center"><small>由Karim Shoair用❤️设计和制作。</small></div><br>
