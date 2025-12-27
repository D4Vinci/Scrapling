<p align=center>
  <br>
  <a href="https://scrapling.readthedocs.io/en/latest/" target="_blank"><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/poster.png" style="width: 50%; height: 100%;" alt="main poster"/></a>
  <br>
  <i><code>简单、轻松的网页抓取，本该如此！</code></i>
</p>
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
    <a href="https://scrapling.readthedocs.io/en/latest/parsing/selection/">
        选择方法
    </a>
    ·
    <a href="https://scrapling.readthedocs.io/en/latest/fetching/choosing/">
        选择获取器
    </a>
    ·
    <a href="https://scrapling.readthedocs.io/en/latest/cli/overview/">
        命令行界面
    </a>
    ·
    <a href="https://scrapling.readthedocs.io/en/latest/ai/mcp-server/">
        MCP模式
    </a>
    ·
    <a href="https://scrapling.readthedocs.io/en/latest/tutorials/migrating_from_beautifulsoup/">
        从Beautifulsoup迁移
    </a>
</p>

**停止与反机器人系统斗争。停止在每次网站更新后重写选择器。**

Scrapling不仅仅是另一个网页抓取库。它是第一个**自适应**抓取库，能够从网站变化中学习并与之共同进化。当其他库在网站更新结构时失效，Scrapling会自动重新定位您的元素并保持抓取器运行。

为现代网络而构建，Scrapling具有**自己的快速解析引擎**和获取器来处理您面临或将要面临的所有网页抓取挑战。由网页抓取者为网页抓取者和普通用户构建，适合每个人。

```python
>> from scrapling.fetchers import Fetcher, AsyncFetcher, StealthyFetcher, DynamicFetcher
>> StealthyFetcher.adaptive = True
# 隐秘地获取网站源代码！
>> page = StealthyFetcher.fetch('https://example.com', headless=True, network_idle=True)
>> print(page.status)
200
>> products = page.css('.product', auto_save=True)  # 抓取在网站设计变更后仍能存活的数据！
>> # 之后，如果网站结构改变，传递 `adaptive=True`
>> products = page.css('.product', adaptive=True)  # Scrapling仍然能找到它们！
```

# 赞助商 

<!-- sponsors -->

<a href="https://www.scrapeless.com/en?utm_source=official&utm_term=scrapling" target="_blank" title="Effortless Web Scraping Toolkit for Business and Developers"><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/scrapeless.jpg"></a>
<a href="https://www.thordata.com/?ls=github&lk=github" target="_blank" title="Unblockable proxies and scraping infrastructure, delivering real-time, reliable web data to power AI models and workflows."><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/thordata.jpg"></a>
<a href="https://evomi.com?utm_source=github&utm_medium=banner&utm_campaign=d4vinci-scrapling" target="_blank" title="Evomi is your Swiss Quality Proxy Provider, starting at $0.49/GB"><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/evomi.png"></a>
<a href="https://serpapi.com/?utm_source=scrapling" target="_blank" title="Scrape Google and other search engines with SerpApi"><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/SerpApi.png"></a>
<a href="https://visit.decodo.com/Dy6W0b" target="_blank" title="Try the Most Efficient Residential Proxies for Free"><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/decodo.png"></a>
<a href="https://petrosky.io/d4vinci" target="_blank" title="PetroSky delivers cutting-edge VPS hosting."><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/petrosky.png"></a>
<a href="https://www.swiftproxy.net/" target="_blank" title="Unlock Reliable Proxy Services with Swiftproxy!"><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/swiftproxy.png"></a>
<a href="https://www.rapidproxy.io/?ref=d4v" target="_blank" title="Affordable Access to the Proxy World – bypass CAPTCHAs blocks, and avoid additional costs."><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/rapidproxy.jpg"></a>
<a href="https://browser.cash/?utm_source=D4Vinci&utm_medium=referral" target="_blank" title="Browser Automation & AI Browser Agent Platform"><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/browserCash.png"></a>

<!-- /sponsors -->

<i><sub>想在这里展示您的广告吗？点击[这里](https://github.com/sponsors/D4Vinci)并选择适合您的级别！</sub></i>

---

## 主要特性

### 支持会话的高级网站获取
- **HTTP请求**：使用`Fetcher`类进行快速和隐秘的HTTP请求。可以模拟浏览器的TLS指纹、标头并使用HTTP3。
- **动态加载**：通过`DynamicFetcher`类使用完整的浏览器自动化获取动态网站，支持Playwright的Chromium和Google Chrome。
- **反机器人绕过**：使用`StealthyFetcher`的高级隐秘功能和指纹伪装。可以轻松自动绕过所有类型的Cloudflare的Turnstile/Interstitial。
- **会话管理**：使用`FetcherSession`、`StealthySession`和`DynamicSession`类持久化会话支持，用于跨请求的cookie和状态管理。
- **异步支持**：所有获取器和专用异步会话类的完整异步支持。

### 自适应抓取和AI集成
- 🔄 **智能元素跟踪**：使用智能相似性算法在网站更改后重新定位元素。
- 🎯 **智能灵活选择**：CSS选择器、XPath选择器、基于过滤器的搜索、文本搜索、正则表达式搜索等。
- 🔍 **查找相似元素**：自动定位与找到的元素相似的元素。
- 🤖 **与AI一起使用的MCP服务器**：内置MCP服务器用于AI辅助网页抓取和数据提取。MCP服务器具有强大的自定义功能，利用Scrapling在将内容传递给AI（Claude/Cursor等）之前提取目标内容，从而加快操作并通过最小化令牌使用来降低成本。（[演示视频](https://www.youtube.com/watch?v=qyFk3ZNwOxE)）

### 高性能和经过实战测试的架构
- 🚀 **闪电般快速**：优化性能超越大多数Python抓取库。
- 🔋 **内存高效**：优化的数据结构和延迟加载，最小内存占用。
- ⚡ **快速JSON序列化**：比标准库快10倍。
- 🏗️ **经过实战测试**：Scrapling不仅拥有92%的测试覆盖率和完整的类型提示覆盖率，而且在过去一年中每天被数百名网页抓取者使用。

### 对开发者/网页抓取者友好的体验
- 🎯 **交互式网页抓取Shell**：可选的内置IPython shell，具有Scrapling集成、快捷方式和新工具，可加快网页抓取脚本开发，例如将curl请求转换为Scrapling请求并在浏览器中查看请求结果。
- 🚀 **直接从终端使用**：可选地，您可以使用Scrapling抓取URL而无需编写任何代码！
- 🛠️ **丰富的导航API**：使用父级、兄弟级和子级导航方法进行高级DOM遍历。
- 🧬 **增强的文本处理**：内置正则表达式、清理方法和优化的字符串操作。
- 📝 **自动选择器生成**：为任何元素生成强大的CSS/XPath选择器。
- 🔌 **熟悉的API**：类似于Scrapy/BeautifulSoup，使用与Scrapy/Parsel相同的伪元素。
- 📘 **完整的类型覆盖**：完整的类型提示，出色的IDE支持和代码补全。
- 🔋 **现成的Docker镜像**：每次发布时，包含所有浏览器的Docker镜像会自动构建和推送。

## 入门

### 基本用法
```python
from scrapling.fetchers import Fetcher, StealthyFetcher, DynamicFetcher
from scrapling.fetchers import FetcherSession, StealthySession, DynamicSession

# 支持会话的HTTP请求
with FetcherSession(impersonate='chrome') as session:  # 使用Chrome的最新版本TLS指纹
    page = session.get('https://quotes.toscrape.com/', stealthy_headers=True)
    quotes = page.css('.quote .text::text')

# 或使用一次性请求
page = Fetcher.get('https://quotes.toscrape.com/')
quotes = page.css('.quote .text::text')

# 高级隐秘模式（保持浏览器打开直到完成）
with StealthySession(headless=True, solve_cloudflare=True) as session:
    page = session.fetch('https://nopecha.com/demo/cloudflare', google_search=False)
    data = page.css('#padded_content a')

# 或使用一次性请求样式，为此请求打开浏览器，完成后关闭
page = StealthyFetcher.fetch('https://nopecha.com/demo/cloudflare')
data = page.css('#padded_content a')
    
# 完整的浏览器自动化（保持浏览器打开直到完成）
with DynamicSession(headless=True) as session:
    page = session.fetch('https://quotes.toscrape.com/', network_idle=True)
    quotes = page.css('.quote .text::text')

# 或使用一次性请求样式
page = DynamicFetcher.fetch('https://quotes.toscrape.com/', network_idle=True)
quotes = page.css('.quote .text::text')
```

### 元素选择
```python
# CSS选择器
page.css('a::text')                      # 提取文本
page.css('a::attr(href)')                # 提取属性
page.css('a', recursive=False)           # 仅直接元素
page.css('a', auto_save=True)            # 自动保存元素位置

# XPath
page.xpath('//a/text()')

# 灵活搜索
page.find_by_text('Python', first_match=True)  # 按文本查找
page.find_by_regex(r'\d{4}')                   # 按正则表达式模式查找
page.find('div', {'class': 'container'})       # 按属性查找

# 导航
element.parent                           # 获取父元素
element.next_sibling                     # 获取下一个兄弟元素
element.children                         # 获取子元素

# 相似元素
similar = page.get_similar(element)      # 查找相似元素

# 自适应抓取
saved_elements = page.css('.product', auto_save=True)
# 之后，当网站更改时：
page.css('.product', adaptive=True)      # 使用保存的位置查找元素
```

### 会话使用
```python
from scrapling.fetchers import FetcherSession, AsyncFetcherSession

# 同步会话
with FetcherSession() as session:
    # Cookie自动保持
    page1 = session.get('https://quotes.toscrape.com/login')
    page2 = session.post('https://quotes.toscrape.com/login', data={'username': 'admin', 'password': 'admin'})
    
    # 如需要，切换浏览器指纹
    page2 = session.get('https://quotes.toscrape.com/', impersonate='firefox135')

# 异步会话使用
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

Scrapling v0.3包含强大的命令行界面：

[![asciicast](https://asciinema.org/a/736339.svg)](https://asciinema.org/a/736339)

```bash
# 启动交互式网页抓取shell
scrapling shell

# 直接将页面提取到文件而无需编程（默认提取`body`标签内的内容）
# 如果输出文件以`.txt`结尾，则将提取目标的文本内容。
# 如果以`.md`结尾，它将是HTML内容的markdown表示，`.html`将直接是HTML内容。
scrapling extract get 'https://example.com' content.md
scrapling extract get 'https://example.com' content.txt --css-selector '#fromSkipToProducts' --impersonate 'chrome'  # 所有匹配CSS选择器'#fromSkipToProducts'的元素
scrapling extract fetch 'https://example.com' content.md --css-selector '#fromSkipToProducts' --no-headless
scrapling extract stealthy-fetch 'https://nopecha.com/demo/cloudflare' captchas.html --css-selector '#padded_content a' --solve-cloudflare
```

> [!NOTE]
> 还有许多其他功能，但我们希望保持此页面简洁，例如MCP服务器和交互式网页抓取Shell。查看完整文档[这里](https://scrapling.readthedocs.io/en/latest/)

## 性能基准

Scrapling不仅功能强大——它还速度极快，自0.3版本以来的更新在所有操作中都提供了卓越的性能改进。以下基准测试将Scrapling的解析器与其他流行库进行了比较。

### 文本提取速度测试（5000个嵌套元素）

| # |         库         | 时间(ms)  | vs Scrapling | 
|---|:-----------------:|:-------:|:------------:|
| 1 |     Scrapling     |  1.99   |     1.0x     |
| 2 |   Parsel/Scrapy   |  2.01   |    1.01x     |
| 3 |     Raw Lxml      |   2.5   |    1.256x    |
| 4 |      PyQuery      |  22.93  |    ~11.5x    |
| 5 |    Selectolax     |  80.57  |    ~40.5x    |
| 6 |   BS4 with Lxml   | 1541.37 |   ~774.6x    |
| 7 |  MechanicalSoup   | 1547.35 |   ~777.6x    |
| 8 | BS4 with html5lib | 3410.58 |   ~1713.9x   |


### 元素相似性和文本搜索性能

Scrapling的自适应元素查找功能明显优于替代方案：

| 库           | 时间(ms) | vs Scrapling |
|-------------|:------:|:------------:|
| Scrapling   |  2.46  |     1.0x     |
| AutoScraper |  13.3  |    5.407x    |


> 所有基准测试代表100+次运行的平均值。请参阅[benchmarks.py](https://github.com/D4Vinci/Scrapling/blob/main/benchmarks.py)了解方法。

## 安装

Scrapling需要Python 3.10或更高版本：

```bash
pip install scrapling
```

从v0.3.2开始，此安装仅包括解析器引擎及其依赖项，没有任何获取器或命令行依赖项。

### 可选依赖项

1. 如果您要使用以下任何额外功能、获取器或它们的类，您将需要安装获取器的依赖项和它们的浏览器依赖项，如下所示：
    ```bash
    pip install "scrapling[fetchers]"
    
    scrapling install
    ```

    这会下载所有浏览器，以及它们的系统依赖项和指纹操作依赖项。

2. 额外功能：
   - 安装MCP服务器功能：
       ```bash
       pip install "scrapling[ai]"
       ```
   - 安装shell功能（网页抓取shell和`extract`命令）：
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

## 许可证

本作品根据BSD-3-Clause许可证授权。

## 致谢

此项目包含改编自以下内容的代码：
- Parsel（BSD许可证）——用于[translator](https://github.com/D4Vinci/Scrapling/blob/main/scrapling/core/translator.py)子模块

## 感谢和参考

- [Daijro](https://github.com/daijro)在[BrowserForge](https://github.com/daijro/browserforge)和[Camoufox](https://github.com/daijro/camoufox)上的出色工作
- [Vinyzu](https://github.com/Vinyzu)在[Botright](https://github.com/Vinyzu/Botright)和[PatchRight](https://github.com/Kaliiiiiiiiii-Vinyzu/patchright)上的出色工作
- [brotector](https://github.com/kaliiiiiiiiii/brotector)提供的浏览器检测绕过技术
- [fakebrowser](https://github.com/kkoooqq/fakebrowser)和[BotBrowser](https://github.com/botswin/BotBrowser)提供的指纹识别研究

---
<div align="center"><small>由Karim Shoair用❤️设计和制作。</small></div><br>