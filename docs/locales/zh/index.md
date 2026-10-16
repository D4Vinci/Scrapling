---
title: "Scrapling：Python 网页抓取框架"
description: "Scrapling：轻松抓取现代网站。"
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
    <a href="index.html" alt="封面">
        <img alt="Scrapling" src="assets/cover_light.svg" class="only-light">
        <img alt="Scrapling" src="assets/cover_dark.svg" class="only-dark">
    </a>
</div>

<h2 align="center"><i>轻松抓取现代网站</i></h2><br>

Scrapling 是一个 Python 网页抓取框架。它将快速 HTTP 请求、隐身浏览器、页面解析和并发爬取整合在一个库中。

抓取静态页面、运行 JavaScript、操作网站，并从网站的 API 中提取数据。构建爬虫时，可以复用会话、轮换代理、自动重试、暂停和恢复任务，还能直接导出数据。

可以在 Python 和终端中使用 Scrapling，也可以通过 MCP 服务器和 Agent Skill 让 AI 智能体使用它。从提取几个字段到将整个网站保存为整洁的 Markdown 文件，Scrapling 都能完成。

## 用 Scrapling 能做什么 {#what-you-can-do-with-scrapling}

- **[获取和操作页面](fetching/choosing.md)**：快速 HTTP 请求、隐身浏览器、JavaScript 渲染、处理 Cloudflare Turnstile 和 Interstitial、持久会话，以及记录后台 API 响应。
- **[解析页面和提取数据](parsing/selection.md)**：使用 CSS、XPath、文本和正则表达式搜索，跟踪页面变化后的元素，查找相似元素，并输出整洁的 Markdown。
- **[爬取和导出](spiders/getting-started.md)**：并发爬虫、代理轮换、重试、AutoThrottle、暂停和恢复、流式输出、现成的模板，以及 JSON、JSONL、CSV 和 XML 导出。
- **[使用 AI 或终端抓取](ai/mcp-server.md)**：供 AI 智能体浏览网页和提取数据的 MCP 服务器、Agent Skill、CLI 命令和交互式 Shell。

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

这段代码输出 `10`，并将名言和作者保存到 `quotes.json`。

## 主要赞助商 {#top-sponsors}

--8<-- "sponsors.html"

<i><sub>想在这里投放广告？点击[这里](https://github.com/sponsors/D4Vinci)，选择一个方案，即可获得相应权益。</sub></i>

## 主要功能 {#key-features}

### Spider：完整的爬虫框架 {#spiders-a-full-crawling-framework}
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

### 使用会话获取页面 {#advanced-websites-fetching-with-session-support}
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

### 解析页面和提取数据 {#parsing-and-data-extraction}
- 🔄 **重新定位元素**：网站结构改变后，用相似度算法重新找到元素。
- 🎯 **灵活选择**：支持 CSS、XPath、过滤器、文本、正则表达式等方式。
- 🔍 **相似元素**：自动查找与已选元素相似的元素。

### AI 功能 {#ai-features}
- 🤖 **MCP 服务器**：让 Claude、Cursor 等 AI 助手和智能体通过 Scrapling 提取数据。支持 HTTP 请求、浏览器操作、截图、保存的登录状态和后台 API 响应。它使用我们的隐身浏览器，并提供工具，让具备相应能力的模型处理 CAPTCHA，补充内置的 Cloudflare 验证处理功能。它还减少发送给模型的内容、拦截广告，并防护提示词注入。支持通过 CDP 连接远程浏览器，也支持带身份验证选项的 HTTP 连接。（[演示视频](https://www.youtube.com/watch?v=qyFk3ZNwOxE)）
- 🧠 **Agent Skill**：可安装的 [Agent Skill](ai/agent-skill.md)，帮助编程智能体了解这个库，并编写符合当前 API 的代码。
- 📚 **用于 RAG 的 Markdown**：用一行代码（`page.markdown()`）将页面转成适合语言模型的整洁 Markdown，或用 `ContentSpider` 模板将整个网站保存为 Markdown 文件。无需语言模型。（[文档](ai/building-rag-systems.md)）

### 快速且经过实际使用 {#high-performance-battle-tested-architecture}
- 🚀 **速度快**：经过优化，性能超过大多数 Python 网页抓取库。
- 🔋 **内存占用低**：使用优化的数据结构，并按需加载。
- ⚡ **快速输出 JSON**：速度是标准库的 10 倍。
- 🏗️ **经过实际检验**：测试覆盖率达 92%，全部代码都有类型注解。过去一年中，数百人每天用它提取数据。

### 开发和数据提取工具 {#developerweb-scraper-friendly-experience}
- 🎯 **交互式 Shell**：可选的 IPython Shell，内置 Scrapling、快捷命令和工具，方便快速开发抓取脚本。可将 curl 请求转成 Scrapling 请求，并在浏览器中查看结果。
- 🚀 **命令行使用**：无需写代码，就能提取 URL 的内容。
- 🛠️ **DOM 导航**：访问父元素、同级元素和子元素。
- 🧬 **文本处理**：支持正则表达式、文本清理和优化的字符串操作。
- 📝 **生成选择器**：为任意元素生成可靠的 CSS 和 XPath 选择器。
- 🔌 **熟悉的 API**：与 Scrapy 和 BeautifulSoup 相似，并支持 Scrapy 和 Parsel 使用的伪元素。
- 🤝 **直接集成 Scrapy**：给回调加上 `scrapling_response` 装饰器，就能用 Scrapling 解析器处理已有的 Scrapy 响应，无需重写程序。
- 📘 **完整的类型注解**：帮助编辑器检查和补全代码。每次修改都会用 **PyRight** 和 **MyPy** 自动检查全部代码。
- 🔋 **现成的 Docker 镜像**：每次发布新版本时，自动构建并发布包含所有浏览器的 Docker 镜像。


## GitHub 星标 {#star-history}
下图展示了 Scrapling 自发布以来的 GitHub 星标增长情况。

<div id="chartContainer">
  <a href="https://github.com/D4Vinci/Scrapling">
    <img id="chartImage" alt="GitHub 星标增长历史" loading="lazy" src="https://api.star-history.com/svg?repos=D4Vinci/Scrapling&type=Date" height="400"/>
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


## 安装 {#installation}
Scrapling 需要 Python 3.10 或更高版本：

```bash
pip install scrapling
```

!!! warning "注意"

    这个命令只安装解析器及其依赖，不包含 Fetcher 或命令行工具。仅安装这些依赖后，像上面的示例那样从 `scrapling.fetchers` 或 `scrapling.spiders` 导入内容，会出现 `ModuleNotFoundError`。要使用 Fetcher 或 Spider，请先按下文安装 Fetcher 的依赖。

### 可选依赖 {#optional-dependencies}

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
     - 安装[构建 RAG 系统](ai/building-rag-systems.md)所需的依赖：
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

### Docker {#docker}
也可以从 DockerHub 下载包含所有扩展功能和浏览器的 Docker 镜像：
```bash
docker pull pyd4vinci/scrapling
```
或从 GitHub 容器仓库下载：
```bash
docker pull ghcr.io/d4vinci/scrapling:latest
```
镜像基于仓库的主分支构建，由 GitHub Actions 自动发布。

## 文档结构 {#how-the-documentation-is-organized}
Scrapling 的文档较多，因此采用 [Diátaxis 文档体系](https://diataxis.fr/)来组织内容。

## 支持项目 {#support}

如果你喜欢 Scrapling，并希望支持它的开发：

- ⭐ 给 [GitHub 仓库](https://github.com/D4Vinci/Scrapling)加星标。
- 🚀 在 [Twitter](https://x.com/Scrapling_dev) 上关注我们，并加入 [Discord 社区](https://discord.gg/EMgGbDceNQ)。
- 💝 [赞助项目，或请我喝杯咖啡](donate.md)。:wink:
- 🐛 在 [GitHub Issues](https://github.com/D4Vinci/Scrapling/issues) 报告问题或提出功能建议。

## 许可证 {#license}

本项目使用 BSD-3 许可证。详情请查看 [LICENSE](https://github.com/D4Vinci/Scrapling/blob/main/LICENSE) 文件。
