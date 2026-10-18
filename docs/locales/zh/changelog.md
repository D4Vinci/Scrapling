---
title: "Scrapling 更新日志"
description: "Scrapling 各版本的发布说明，包括新功能、问题修复和不兼容变更。"
---

# 更新日志 {#changelog}

Scrapling 的所有重要变更，整理自 [GitHub 发布记录](https://github.com/D4Vinci/Scrapling/releases)。

## [v0.5](https://github.com/D4Vinci/Scrapling/releases/tag/v0.5) - 2026-10-17 {#v0.5}

**Scrapling v0.5 几乎全面升级：页面获取、解析、Spider、浏览器自动化、AI 工具，以及十种语言的文档 🚀**

!!! warning "警告"

    **此版本包含大量不兼容变更，无法在此全部列出。更新前请查看[迁移到 v0.5 指南](migrating-to-v0.5.md)。**

### 🚀 新功能与使用体验改进 {#v0.5-new-stuff-and-quality-of-life-changes}

- **面向 AI 智能体的 MCP 服务器功能大幅增强，能够处理几乎所有 CAPTCHA 验证码**（参见[文档](ai/mcp-server.md)）：

    - **完整的浏览器操作流程**：按顺序填表、点击、悬停、滚动、使用键盘、处理对话框并等待结果。支持多种字段类型和放慢操作速度，遇到第一个错误时停止执行。
    - **无需重新加载，即可读取和搜索当前页面**：从整个页面或单个元素中提取 HTML、Markdown 或文本。可搜索的页面快照会显示元素的角色、名称和位置，聚焦查看时仍保留周围的上下文。
    - **运行自定义 JavaScript 并截取指定区域**：执行脚本，包括异步操作，并可访问页面自身的 JavaScript。可以将单个元素、视口或整个页面保存为 PNG 或 JPEG 截图。
    - **检查网络活动并复用登录状态**：查看记录的请求和响应，保存和恢复浏览器登录状态，并与开放或封闭 Shadow DOM 内的元素交互。请在关闭会话前读取记录的网络流量。
    - **减少 token 消耗，让错误更清晰**：更简洁的工具描述和共享说明减少了重复文本，浏览器及请求失败时也会向智能体提供有用的错误信息。

- **查看页面背后的请求**。启用 `record_requests=True`，记录页面加载、操作和标签页中已完成的网络流量，然后直接查看保存的响应，无需再次发送请求。（参见[文档](fetching/stealthy.md#network-history)）

    ```python
    from scrapling.fetchers import StealthySession

    with StealthySession(record_requests=True) as session:
        session.fetch("https://example.com", network_idle=True)
        for response in session.network.search(url_pattern=r"/api/", limit=None):
            print(response.url, response.status, response.body)
    ```

    - 按 URL、方法、资源类型或状态筛选，也可通过 ID 获取单个响应。通过常用的 `Response` API 查看请求头和响应头、发送的数据、API 响应、HTTP 错误和重定向。
    - 在大小限制内保留支持的文本正文，并保存元数据；无法保存正文时会记录原因。默认上限为 1,000 个请求。支持同步和异步会话，保存的 Python 历史记录在会话关闭后仍可读取。

- **登录状态只需保存一次，即可在多次运行中复用**。`save_state(path)` 和 `load_state(path)` 以兼容 Playwright 的 JSON 格式保存 Cookie、本地存储和 IndexedDB。同步和异步浏览器会话均支持这两个方法。（参见[文档](fetching/stealthy.md#save-and-load-session-state)）
    - 获取或重新加载页面前先加载状态。需要已启动的共享浏览器上下文，且不能使用 `proxy_rotator`；标签页、浏览器设置和 `sessionStorage` 不会保存。

- **使用 `pierce_shadow=True` 提取开放的 Shadow DOM**，然后照常使用 CSS 或 XPath。浏览器获取器、会话以及 CLI 的 `--pierce-shadow` 选项均支持此功能。保留插槽内容，同时不修改实时页面。捕获的 HTML 不包含封闭的 Shadow 根和 iframe 文档。（参见[文档](fetching/stealthy.md#shadow-dom)）

- **选择 Spider 探索网站的顺序**。`CrawlSpider` 及其子类（包括 `ContentSpider`）支持 `crawl_strategy="bfs"`，优先调度最早加入的请求；也可使用 `"dfs"`，优先调度最新加入的请求。优先级仍然优先，并发页面的完成顺序可能不同。（参见[文档](spiders/generic-templates.md#crawl-order)）

### 🐛 问题修复 {#v0.5-bug-fixes}

- **改进 Cloudflare 挑战处理**，检测延迟出现的验证组件，减少不必要的等待，并限制被动挑战和隐藏框架的重试循环。修复 [#468](https://github.com/D4Vinci/Scrapling/issues/468) 和 [#509](https://github.com/D4Vinci/Scrapling/issues/509)。
- **修复从以管理员权限运行的 Windows shell 启动浏览器的问题**。修复 [#463](https://github.com/D4Vinci/Scrapling/issues/463)。
- **添加自定义浏览器参数时保留内置的隐身参数**，由 @alkaz-nodemaven 在 [#430](https://github.com/D4Vinci/Scrapling/pull/430) 中贡献。
- **改进浏览器响应的字符集解析**，支持大小写不同、包含空格或带引号的声明值。
- **无需处理 Cloudflare 挑战时，不再将未检测到挑战记录为错误**。修复 [#459](https://github.com/D4Vinci/Scrapling/issues/459)。

- **修正请求指纹**：查询参数由 @yetval 在 [#448](https://github.com/D4Vinci/Scrapling/pull/448) 中修复，空值或假值 JSON 正文由 @ac1982 在 [#480](https://github.com/D4Vinci/Scrapling/pull/480) 中修复，请求头插入顺序由 @SarwadnyaMahajan 在 [#466](https://github.com/D4Vinci/Scrapling/pull/466) 中修复。
- **修复请求数据被带入后续链接请求的问题**，包括残留的正文相关请求头，由 @yetval 在 [#462](https://github.com/D4Vinci/Scrapling/pull/462) 中贡献。
- **防止被拦截的响应作为成功响应存入开发缓存**，由 @Kuang-xianxin 在 [#446](https://github.com/D4Vinci/Scrapling/pull/446) 中贡献。
- **抓取因异常失败时保留检查点文件**，由 @SulimanAbdulrazzaq 在 [#486](https://github.com/D4Vinci/Scrapling/pull/486) 中贡献。
- **修正 robots.txt 获取失败的处理方式**，不再将获取失败缓存为允许抓取，由 @prateekraawat1 在 [#443](https://github.com/D4Vinci/Scrapling/pull/443) 中贡献。
- **修复使用范围限制选择器提取链接的问题**，包括没有匹配项，以及选择器直接指向链接元素本身的情况，由 @SulimanAbdulrazzaq 在 [#452](https://github.com/D4Vinci/Scrapling/pull/452) 和 [#483](https://github.com/D4Vinci/Scrapling/pull/483) 中贡献。
- **修复 sitemap 的回调路由**，由 @SulimanAbdulrazzaq 在 [#458](https://github.com/D4Vinci/Scrapling/pull/458) 中贡献；**修复包含注释或处理指令时的 XML 解析问题**，由 @sup3dev 在 [#450](https://github.com/D4Vinci/Scrapling/pull/450) 中贡献。
- **处理 robots.txt 和 CSV Feed 开头的字节顺序标记**，由 @SulimanAbdulrazzaq 在 [#453](https://github.com/D4Vinci/Scrapling/pull/453) 中贡献。
- **修复 Spider HTTP 会话对 `stealthy_headers` 的处理**，将该选项传给会话，而不是直接传给 `curl_cffi`，由 @Yigtwxx 在 [#475](https://github.com/D4Vinci/Scrapling/pull/475) 中贡献。

- **修复字典表单中列表和元组值的编码**，同时保留请求正文的优先顺序和现有的 `None` 处理方式，包含 @SulimanAbdulrazzaq 在 [#485](https://github.com/D4Vinci/Scrapling/pull/485) 中的贡献。
- **修复会话与单次请求的 HTTP 请求头合并，正确忽略大小写**，由 @SulimanAbdulrazzaq 在 [#487](https://github.com/D4Vinci/Scrapling/pull/487) 中贡献。
- **修复 CLI 请求无提示地丢弃空值或假值 JSON 正文的问题**，由 @SulimanAbdulrazzaq 在 [#484](https://github.com/D4Vinci/Scrapling/pull/484) 中贡献。
- **让 Markdown 和文本文件导出统一使用 UTF-8**，并防止转换错误截断已有的输出文件，由 @SulimanAbdulrazzaq 在 [#488](https://github.com/D4Vinci/Scrapling/pull/488) 中贡献。
- **修复 `curl2fetcher()` 对 curl 的 User-Agent 和代理选项的处理**，由 @SulimanAbdulrazzaq 在 [#490](https://github.com/D4Vinci/Scrapling/pull/490) 中贡献。

- **修复 Markdown 块连在一起的问题**，该问题发生在通过 `Response.markdown()` 或 CLI 提取转换多个选中元素时，包含 @Yigtwxx 在 [#432](https://github.com/D4Vinci/Scrapling/pull/432) 中的贡献。
- **修复 AI 输出的隐藏内容清理**，保留 `opacity:0.95` 这类可见内容，识别更多隐藏样式并移除隐藏插槽，包含 @Yigtwxx 在 [#460](https://github.com/D4Vinci/Scrapling/pull/460) 中的贡献。
- **修复在嵌套标签附近过早停止移除噪声标签的问题**，由 @Yigtwxx 在 [#474](https://github.com/D4Vinci/Scrapling/pull/474) 中贡献。
- **修复为多个同标签兄弟元素中的第一个元素生成 CSS 和 XPath 选择器的问题**，由 @yellow-dog-dog 在 [#495](https://github.com/D4Vinci/Scrapling/pull/495) 中贡献。
- **解决 lxml HTML 解析器的弃用警告**，由 @afsuyadi 在 [#493](https://github.com/D4Vinci/Scrapling/pull/493) 中贡献。

### 文档 {#v0.5-docs}

- **整个网站现已支持十种语言**：英语、阿拉伯语、西班牙语、巴西葡萄牙语、法语、德语、简体中文、日语、俄语和韩语。指南、API 参考、教程和[更新日志](changelog.md)均已翻译，支持阿拉伯语从右到左的布局，切换语言时会保留当前页面和章节。
- **改进指南、README 示例和设置步骤**，涵盖检查点数据、浏览器编码、保存的状态、网络历史记录、Shadow DOM 和抓取顺序。
- **更新 Agent Skill** 及其示例、参考资料和可下载的压缩包，使其与当前的浏览器和 MCP 工具保持一致。
- **将更新日志移至网站**，并提供每个页面的 Markdown 源文件入口。

### 项目 {#v0.5-project}

- 更新 Scrapling 的徽标、封面图片和网站外观。
- 扩展测试，覆盖浏览器操作、对话框、内容提取、截图、JavaScript、网络记录、状态文件、Shadow DOM 和爬虫修复。
- 添加浏览器测试标记，将浏览器、异步和并行测试分别运行。@diegobravtraps-oss 在 [#457](https://github.com/D4Vinci/Scrapling/pull/457) 中改进了 Windows 上检查点和 CSV 测试的兼容性。
- 更新共享的多语言文档构建配置和贡献指南。

## [v0.4.15](https://github.com/D4Vinci/Scrapling/releases/tag/v0.4.15) - 2026-08-23 {#v0.4.15}

**今年规模最大的版本之一：重构 MCP 服务器，一行代码生成可用于 RAG 的 Markdown，改进 Cloudflare 挑战处理，并让浏览器标签页保持打开以便继续自动化操作 🚀**

!!! warning "警告"

    **此版本对 MCP 服务器进行了不兼容变更。更新前请查看[不兼容变更](https://github.com/D4Vinci/Scrapling/blob/v0.4.15/docs/ai/mcp-server.md#breaking-changes)部分。**

### 🚀 新功能与使用体验改进 {#v0.4.15-new-stuff-and-quality-of-life-changes}

- **浏览器标签页现在会保持打开，并在后续请求中复用**（参见[文档](fetching/stealthy.md#session-management)）：
    - 所有浏览器会话都会在请求结束后保留标签页，下一个请求会复用空闲标签页，而不是新开一个。
    - 每次请求都会将自己的设置（超时、请求头、资源拦截）重新应用到分配的标签页，因此不同请求的设置不会互相影响。
    - 出错的标签页会关闭并被替换，新增的 `close_pages()` 方法可以关闭所有打开的标签页。
    - 已获取的页面会保持加载状态，因此下一个请求中的 `page_setup` 函数会先在该页面上运行，再导航到其他页面。这是跨请求串联自动化操作的基础。

- **使用 `Response.markdown()` 将任意页面转为干净、适合 LLM 使用的 Markdown**（参见[文档](ai/building-rag-systems.md)）：

    ```python
    from scrapling.fetchers import Fetcher

    markdown = Fetcher.get("https://example.com").markdown(main_content_only=True)
    ```

    - 始终先移除脚本、样式和隐藏的提示词注入内容，清理方式与 MCP 服务器相同。
    - 传入 `css_selector`，只转换需要的元素。
    - 通过新增的 `rag` 扩展安装项提供（`pip install "scrapling[rag]"`），`ai`/`shell`/`all` 也包含该扩展。

- **新增 `SiteToMarkdownSpider` 模板，将整个网站抓取为 Markdown 语料，用于 RAG 流程**（参见[文档](ai/building-rag-systems.md)）：

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

    - 每个页面生成一个包含 `url`/`title`/`markdown` 的数据项；可选的 `output_dir` 会为每个页面写入一个 Markdown 文件。
    - `max_pages` 限制抓取页面数量。由于模板基于 `CrawlSpider`，重写 `rules()` 即可完全控制要跟随哪些链接。

- **重构 MCP 服务器（不兼容变更）**（参见[不兼容变更](https://github.com/D4Vinci/Scrapling/blob/v0.4.15/docs/ai/mcp-server.md#breaking-changes)和[文档](ai/mcp-server.md)）：
    - 13 个工具现在分为两种模式：单次调用工具（`fetch`、`bulk_fetch`、`stealthy_fetch`、`bulk_stealthy_fetch`）始终启动自己的浏览器，并显示真实的默认设置；会话工具则使用只需打开一次的会话。
    - 新增的 `session_fetch` 工具通过浏览器会话获取页面，`open_session` 现在只保存浏览器级设置，并将会话实际生效的设置返回给 AI 智能体。
    - `get` 工具更名为 `make_request`，现在支持任意 HTTP 方法。
    - 新增的 `open_request_session` 和 `session_make_request` 工具为 AI 提供持久化 HTTP 会话，在请求之间保留 Cookie 和浏览器指纹。
    - 这也解决了获取页面时重置会话设置的问题，该问题最初由 @Yigtwxx 在 [#418](https://github.com/D4Vinci/Scrapling/pull/418) 中修复。

- **MCP 服务器的 HTTP 传输现在要求身份验证，并默认只监听 localhost（不兼容变更）**，由 @yamantaka-singh 在 [#414](https://github.com/D4Vinci/Scrapling/pull/414) 中贡献（修复 [#413](https://github.com/D4Vinci/Scrapling/issues/413)，参见[文档](ai/mcp-server.md#authentication)）：
    - 传入 `--auth-token`（或使用环境变量 `SCRAPLING_MCP_AUTH_TOKEN`）来要求 bearer token；如果确实要禁用身份验证，则传入 `--no-auth`。
    - 传入 `--host 0.0.0.0` 以接受来自网络的连接。

### 🐛 问题修复 {#v0.4.15-bug-fixes}

- **Cloudflare Turnstile/Interstitial 挑战处理现在不受浏览器语言和地区设置影响，在无头模式下处理交互式挑战时也不再陷入死循环**。隐身浏览器页面在处理挑战的过程中也不再崩溃，包含 @subediparas5 在 [#412](https://github.com/D4Vinci/Scrapling/pull/412) 中的贡献。（修复 [#411](https://github.com/D4Vinci/Scrapling/issues/411) 和 [#422](https://github.com/D4Vinci/Scrapling/issues/422)）
- **修复 `find`/`find_all` 使用 `class_` 时无提示地漏掉含多个 class 的元素的问题**，由 @yetval 在 [#410](https://github.com/D4Vinci/Scrapling/pull/410) 中贡献；**修复空白 `class_` 值及 CSS 字符串值未转义的问题**，由 @yamantaka-singh 在 [#417](https://github.com/D4Vinci/Scrapling/pull/417) 中贡献。
- **修复 `development_mode` 中重放缓存响应时丢失请求元数据的问题**，由 @Yigtwxx 在 [#419](https://github.com/D4Vinci/Scrapling/pull/419) 中贡献。
- **修复 `retries` 小于 1 时 HTTP 请求尚未发出就失败的问题**，由 @Yigtwxx 在 [#420](https://github.com/D4Vinci/Scrapling/pull/420) 中贡献。

### 文档 {#v0.4.15-docs}

- **重新组织网站栏目**：新增“与 AI 配合使用”栏目，包含 MCP 服务器、新的 [Agent Skill](ai/agent-skill.md) 页面和[构建 RAG 系统](ai/building-rag-systems.md)指南。BeautifulSoup 迁移指南移至“集成与迁移”栏目，与 Scrapy 集成放在一起。
- **向仓库添加[更新日志](changelog.md)**，包含迄今为止所有版本的发布说明。

## [v0.4.14](https://github.com/D4Vinci/Scrapling/releases/tag/v0.4.14) - 2026-08-10 {#v0.4.14}

**快速维护版本，修复使用 `uv` 安装的问题 🔧**

### 🐛 问题修复 {#v0.4.14-bug-fixes}

- **修复 `uv` 默认拒绝安装 v0.4.13，并在没有提示的情况下回退到旧版本的问题**。前一版本要求安装 `curl_cffi` 的预发布版本，而 `uv` 只有在明确启用后才允许这样做。
所有依赖现在都可以使用稳定版本。（修复 [#407](https://github.com/D4Vinci/Scrapling/issues/407)）

## [v0.4.13](https://github.com/D4Vinci/Scrapling/releases/tag/v0.4.13) - 2026-08-09 {#v0.4.13}

**新版本带来了 Feed Spider 和更智能的 MCP 服务器 🎉**

### 🚀 新功能与使用体验改进 {#v0.4.13-new-stuff-and-quality-of-life-changes}

- **新增 Feed Spider 模板**。`XMLFeedSpider` 遍历任意 XML Feed 的节点（RSS、Atom、商品 Feed 等），`CSVFeedSpider` 将 CSV 行作为字典逐行处理。两者都会自动解压 gzip 压缩的 Feed。（参见[文档](spiders/generic-templates.md)）

  ```python
  from scrapling.spiders import XMLFeedSpider

  class RSSSpider(XMLFeedSpider):
      name = "rss"
      start_urls = ["https://example.com/feed.xml"]

      async def parse_node(self, response, node):
          yield {"title": node.findtext("title"), "link": node.findtext("link")}

  result = RSSSpider().start()
  ```

- **将 MCP 服务器升级至 MCP SDK v2，并改进智能体使用体验**。服务器现在提供说明，指导 AI 智能体高效使用工具；每个工具都声明注解，让 Claude Code 等客户端能自动批准只读工具；工具描述更简洁，减少 token 消耗；服务器还会向 MCP 客户端提供版本和徽标信息。（参见[文档](ai/mcp-server.md)）
- **新增 `scrapling-mcp` 命令**，直接对应 `scrapling mcp`。对于只接受单个命令的 MCP 客户端和注册服务，现在只需一行命令即可注册 Scrapling。
- **不再固定 Playwright/Patchright 和浏览器版本**。生成的浏览器 User-Agent 现在始终匹配已安装的 Playwright/Patchright 实际使用的 Chromium 版本，因此 Scrapling 不再固定它们的版本，可以自由升级。更新后运行 `scrapling install --force` 来更新浏览器。

### 🐛 问题修复 {#v0.4.13-bug-fixes}

- **修复指纹数据包落后于浏览器版本时，导入 Scrapling 会因 `browserforge` 的 ValueError 而崩溃的问题**。（修复 [#394](https://github.com/D4Vinci/Scrapling/issues/394)、[#396](https://github.com/D4Vinci/Scrapling/issues/396) 和 [#400](https://github.com/D4Vinci/Scrapling/issues/400)）
- **修复 MCP 批量浏览器工具的页面池大小设置错误的问题**。此错误会导致 `bulk_fetch` 在一批超过 50 个 URL 时失败，并让 `bulk_stealthy_fetch` 通过同一个标签页获取所有 URL。由 @Yigtwxx 在 [#393](https://github.com/D4Vinci/Scrapling/pull/393) 中贡献。

### 项目 {#v0.4.13-project}

- **新增 [AI 贡献政策](https://github.com/D4Vinci/Scrapling/blob/main/AI_POLICY.md)**：欢迎借助 AI 做贡献，但必须在 PR 或 issue 中说明；看起来使用了 AI 却未说明的提交会被添加标签并关闭。

## [v0.4.12](https://github.com/D4Vinci/Scrapling/releases/tag/v0.4.12) - 2026-07-26 {#v0.4.12}

**本次版本专注于让 Spider 更智能地应对所抓取的网站**

### 🚀 新功能与使用体验改进 {#v0.4.12-new-stuff-and-quality-of-life-changes}

- **Spider 现在可以通过 AutoThrottle 自动调整速度。** 不必再猜测一个可能过慢或导致封锁的 `download_delay`：Spider 会测量各网站的响应速度，并单独调整每个域名的延迟。当网站开始封锁或限流时，它会将延迟翻倍（或严格按 `Retry-After` 响应头要求的时长等待），直到恢复正常，然后再恢复速度。你设置的 `download_delay` 和 robots.txt 中的 `Crawl-delay` 仍会作为最小值。（参见[文档](spiders/advanced.md#autothrottle)）

    ```python
    class MySpider(Spider):
        name = "adaptive"
        start_urls = ["https://example.com"]
        autothrottle_enabled = True
        autothrottle_start_delay = 2.0
        autothrottle_max_delay = 30.0
        autothrottle_block_backoff = True
    ```

- **支持将结果导出为 CSV 和 XML**，此外仍可使用已有的 JSON/JSONL 导出功能。即使数据项的键不同，也能完整导出，嵌套值会写成 JSON。（参见[文档](spiders/getting-started.md)）

    ```python
    result = MySpider().start()
    result.items.to_csv("products.csv")
    result.items.to_xml("products.xml")
    ```

- **MCP 服务器现在可以要求身份验证**，因此可以安全地对外提供服务，而不必仅限于本机。缺少 token 的请求会被拒绝，也可以限制服务器响应的主机名。（参见[文档](ai/mcp-server.md)）

    ```bash
    scrapling mcp --http --auth-token "$(openssl rand -hex 32)"
    ```

- **浏览器现在接受 HTTP 形式的 CDP URL**，不再只支持 WebSocket。除了托管浏览器服务提供的 `wss://` 端点，现在还可以将任意浏览器 Fetcher 或 MCP 会话连接到通过 `--remote-debugging-port=9222` 自行启动的 Chrome。

- **发布的 Docker 镜像现在带有版本号标签**，而不只是 `latest`，这样就可以固定使用所需的具体版本。由 @JanRK 在 [#384](https://github.com/D4Vinci/Scrapling/pull/384) 中贡献。

### 🐛 问题修复 {#v0.4.12-bug-fixes}

- **修复浏览器引擎生成的响应在缓存后丢失全部 Cookie 的问题**。此问题会让 Spider 开发模式中依赖 Cookie 的会话或身份验证逻辑在没有提示的情况下失效。由 @amitvijapur 在 [#379](https://github.com/D4Vinci/Scrapling/pull/379) 中贡献。（修复 [#376](https://github.com/D4Vinci/Scrapling/issues/376)）

- **修复 `StealthyFetcher` 强制所有浏览器使用 `en-US` 语言和地区设置，而不是跟随系统设置的问题**。这会让网站发现语言和地区设置与 IP 地址不一致，并将其视为可疑行为，例如 Google 返回 429。（修复 [#381](https://github.com/D4Vinci/Scrapling/issues/381)）

- **修复存储系统中一条容易误导的错误信息**，并移除插入操作后遗留的无用调用。由 @fix2015 在 [#377](https://github.com/D4Vinci/Scrapling/pull/377) 中贡献。

### 性能 {#v0.4.12-performance}

- **`get_all_text()` 的耗时现在与节点数量成正比（O(nodes)）**，不再逐个遍历每个文本节点的祖先元素，在深层嵌套页面上的速度约为原来的 5-6 倍。由 @yetval 在 [#378](https://github.com/D4Vinci/Scrapling/pull/378) 中贡献。

## [v0.4.11](https://github.com/D4Vinci/Scrapling/releases/tag/v0.4.11) - 2026-07-12 {#v0.4.11}

**一次重要更新，带来首个特定平台 Spider 模板、更快的解析器和重要修复 🎉**

### 🚀 新功能与使用体验改进 {#v0.4.11-new-stuff-and-quality-of-life-changes}

- **新增 `ShopifySpider`，首个特定平台 Spider 模板！** 通过 Shopify 商店的 JSON API 提取所有商品，无需处理网站 HTML。继承该类，设置商店域名，就可以使用（参见[文档](spiders/platform-templates.md)）

  ```python
  from scrapling.spiders import ShopifySpider

  class MyStore(ShopifySpider):
      target_website = "example.com"

  result = MyStore().start()
  ```

- **为 CLI 浏览器命令添加 `--executable-path`**。`scrapling extract fetch` 和 `scrapling extract stealthy-fetch` 现在都接受自定义的 Chromium 兼容浏览器可执行文件；没有传入该选项时，会使用环境变量 `SCRAPLING_EXECUTABLE_PATH`，与 MCP 服务器的功能保持一致（解决 [#371](https://github.com/D4Vinci/Scrapling/issues/371)）

  ```bash
  scrapling extract fetch "https://example.com" page.html --executable-path "/path/to/chromium"
  ```

### 🤖 使用体验改进 {#v0.4.11-quality-of-life-changes}
- **`find_by_text` 和 `find_by_regex` 的速度最高提升到原来的约 2 倍**，适用于启用 `first_match`（默认设置）的情况。元素只在需要时转换成对象，因此搜索会在首个匹配处停止。由 @yetval 在 [#370](https://github.com/D4Vinci/Scrapling/pull/370) 中贡献
- **使用新数据更新基准测试，并与所有库的最新版本进行比较。**
- **更新贡献规则**

### 🐛 问题修复 {#v0.4.11-bug-fixes}

- **修复 MCP 服务器的页面获取工具在含有控制字符的页面上崩溃的问题**，错误信息为 `All strings must be XML compatible`。由 @yetval 在 [#368](https://github.com/D4Vinci/Scrapling/pull/368) 中贡献（修复 [#366](https://github.com/D4Vinci/Scrapling/issues/366)）

## [v0.4.10](https://github.com/D4Vinci/Scrapling/releases/tag/v0.4.10) - 2026-07-04 {#v0.4.10}

**新版本带来全新的 Scrapy 集成和一批社区贡献的修复 🎉**

### 🚀 新功能与使用体验改进 {#v0.4.10-new-stuff-and-quality-of-life-changes}

- **新增 Scrapy 集成**，可以在现有 Scrapy 项目中使用 Scrapling 的解析 API，无需重写项目。给任意 Spider 回调添加 `scrapling_response` 装饰器，回调收到的响应就会变成 Scrapling 的 `Response`，同时仍由 Scrapy 负责抓取调度（参见[文档](integrations/scrapy.md)）：

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

- **MCP 服务器现在可以为所有浏览器工具使用自定义的 Chromium 兼容浏览器**。通过 `scrapling mcp --executable-path "/path/to/chromium"` 或环境变量 `SCRAPLING_EXECUTABLE_PATH` 统一设置，也可以用 `executable_path` 参数逐个请求指定。由 @samrusani 在 [#360](https://github.com/D4Vinci/Scrapling/pull/360) 中贡献（解决 [#347](https://github.com/D4Vinci/Scrapling/issues/347)）
- **更新所有浏览器和指纹**。更新后运行 `scrapling install --force` 以刷新它们。

### 🐛 问题修复 {#v0.4.10-bug-fixes}

- **修复浏览器 Fetcher 在非 UTF-8 网站上返回乱码（mojibake）的问题**，由 @yehudalevy-collab 在 [#365](https://github.com/D4Vinci/Scrapling/pull/365) 中贡献（修复 [#364](https://github.com/D4Vinci/Scrapling/issues/364)）。
- **修复 `LinkExtractor` 无法过滤 `.tar.gz` 等复合文件扩展名的问题**，由 @renbkna 在 [#359](https://github.com/D4Vinci/Scrapling/pull/359) 中贡献（修复 [#349](https://github.com/D4Vinci/Scrapling/issues/349)）。
- **修复暂停抓取时，检查点丢失执行中请求的问题，恢复后不再跳过这些请求**，由 @yetval 在 [#358](https://github.com/D4Vinci/Scrapling/pull/358) 中贡献。
- **通过升级 Protego，修复 Spider 根据 robots.txt 的 `Request-rate` 指令计算出错误抓取延迟的问题**，由 @Disaster-Terminator 在 [#355](https://github.com/D4Vinci/Scrapling/pull/355) 中同步调整测试。

### 文档 {#v0.4.10-docs}

- **说明隐身模式下 `init_script` 与 Patchright 隔离执行上下文的交互方式**，由 @mturac 在 [#353](https://github.com/D4Vinci/Scrapling/pull/353) 中贡献（解决 [#350](https://github.com/D4Vinci/Scrapling/issues/350)）。
- **为 Agent Skill 添加通过 [skills.sh](https://skills.sh/D4Vinci/Scrapling) 安装的方式**，由 @ob-aion 在 [#363](https://github.com/D4Vinci/Scrapling/pull/363) 中贡献。

## [v0.4.9](https://github.com/D4Vinci/Scrapling/releases/tag/v0.4.9) - 2026-06-07 {#v0.4.9}

**维护更新，包含许多针对社区反馈问题的修复 🛠️**

### 🚀 新功能与使用体验改进 {#v0.4.9-new-stuff-and-quality-of-life-changes}

- **更新所有浏览器和指纹**。更新后运行 `scrapling install --force` 以刷新它们。
- **为 CLI 添加 `--version` 选项**，由 @ETM-Code 在 [#303](https://github.com/D4Vinci/Scrapling/pull/303) 中贡献（解决 [#299](https://github.com/D4Vinci/Scrapling/issues/299)）

### 🐛 问题修复 {#v0.4.9-bug-fixes}

- **修复 HTTP 会话中无提示地忽略会话级 `proxy` 参数的问题**，这可能泄露真实 IP（解决 [#295](https://github.com/D4Vinci/Scrapling/issues/295)）。现在，如果将会话级 `proxy` 与单次请求的 `proxies` 参数混用（或反过来），会直接报错，不再静默丢弃其中一个。
- **修复同时使用 `init_script` 和 `user_data_dir` 时浏览器导航失败的问题**（解决 [#294](https://github.com/D4Vinci/Scrapling/issues/294)）。
- **修复网站在 `Content-Type` 响应头中用引号包裹 charset 值时的编码检测问题**，由 @Bortlesboat 在 [#323](https://github.com/D4Vinci/Scrapling/pull/323) 中贡献。
- **修复自适应元素重定位时出现的 `IndexError`，该问题发生在启用 `auto_save` 时**，由 @Mubashirrrr 在 [#340](https://github.com/D4Vinci/Scrapling/pull/340) 中贡献。
- **修复 Windows 上保存 Spider 检查点和缓存时崩溃的问题**，由 @MrStarkEG 在 [#344](https://github.com/D4Vinci/Scrapling/pull/344) 中贡献。
- **修复 `find_similar` 对属性数量不同的元素计算相似度不准确的问题**（解决 [#322](https://github.com/D4Vinci/Scrapling/issues/322)）。

### 文档 {#v0.4.9-docs}

- **明确说明默认安装仅包含解析器引擎**，Fetcher 和 Spider 需要安装额外扩展（解决 [#343](https://github.com/D4Vinci/Scrapling/issues/343)）。
- **修复其余示例中的 Docker 镜像名称**，由 @evanclan 在 [#315](https://github.com/D4Vinci/Scrapling/pull/315) 中贡献。
- **修复贡献指南中的失效链接**，由 @Bortlesboat 在 [#320](https://github.com/D4Vinci/Scrapling/pull/320) 中贡献。

## [v0.4.8](https://github.com/D4Vinci/Scrapling/releases/tag/v0.4.8) - 2026-05-11 {#v0.4.8}

**Spider 大更新，进一步改进抓取框架 🕷️**

### 🚀 新功能与使用体验改进 {#v0.4.8-new-stuff-and-quality-of-life-changes}

- **新增 `LinkExtractor` 工具**，位于 `scrapling.spiders.LinkExtractor`，用于从 `Response` 提取 URL，提供丰富的控制选项（参见[文档](spiders/generic-templates.md)）

    ```python
    from scrapling.spiders import LinkExtractor

    extractor = LinkExtractor(allow=r"/posts/", deny_domains=["ads.example.com"])
    ```

- **新增通用 Spider 模板 `CrawlSpider` 和 `CrawlRule`**，无需再重复编写“跟随符合某个模式的链接”这一类代码。重写 `rules()` 来返回 `CrawlRule` 对象列表，每个对象关联一个 `LinkExtractor`。（参见[文档](spiders/generic-templates.md)）

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

- **新增 `SitemapSpider` 模板**，直接从 sitemap 或 `robots.txt` URL 开始抓取。支持 gzip 压缩的 sitemap，并提供丰富的控制选项。URL 通过抓取规则分发，方式与上面的 **CrawlSpider** 示例相同。（参见[文档](spiders/generic-templates.md)）

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

- **自适应重定位的所有方法现在默认使用 40% 相似度阈值**，不再使用 `0`，让自适应功能表现更好。如果没有元素超过阈值，会用警告显示找到的最高相似度，便于按需主动降低 `percentage`。

- **更新所有浏览器和指纹**。更新后重新运行 `scrapling install  --force` 以刷新浏览器和指纹。

### 🐛 问题修复 {#v0.4.8-bug-fixes}

- **修复 `Fetcher.configure(...)` 没有应用到单次请求调用的问题**，同样修复了 `AsyncFetcher`。
- **修复请求指纹计算错误导致 Spider 重复请求的问题**，由 @yetval 在 [#255](https://github.com/D4Vinci/Scrapling/pull/255) 中贡献。
- **修复自适应抓取引擎在匹配度低时不发出提示的问题。** 配合上面的阈值调整，现在重定位失败时会给出警告，而不是返回一个容易误导的“最佳猜测”元素。

### 文档 {#v0.4.8-docs}

- **更新文档中的旧代码示例**，使其与当前版本一致。
- **改进文档网站的代码复制粘贴体验**，并精简 Agent Skill，减少每次调用消耗的 token。

## [v0.4.7](https://github.com/D4Vinci/Scrapling/releases/tag/v0.4.7) - 2026-04-17 {#v0.4.7}

**本次更新让 AI 智能体能够看到页面 📸**

### 🚀 新功能与使用体验改进 {#v0.4.7-new-stuff-and-quality-of-life-changes}

- **新增 MCP 工具 `screenshot`**，截取页面并返回真正的 MCP `ImageContent` 内容块，让模型可以直接看到图片。该工具需要打开的浏览器会话，因此先调用 `open_session`（使用 `dynamic` 或 `stealthy`），再在这里传入 `session_id`。支持 PNG 和 JPEG、整页截图、JPEG 质量设置，以及常用的就绪等待选项（`wait`、`wait_selector`、`network_idle`、`timeout`）。（实现 [#244](https://github.com/D4Vinci/Scrapling/issues/244)）
- **新增自定义 `session_id` 参数，供 `open_session` 使用**，可以为会话取有意义的名字（`"search"`、`"checkout"`），不再局限于默认的 12 位随机十六进制字符串。由 @hauntedhost 在 [#243](https://github.com/D4Vinci/Scrapling/pull/243) 中贡献

### 🐛 问题修复 {#v0.4.7-bug-fixes}

- **修复 `FetcherSession` 状态损坏和延迟初始化会话关闭时崩溃的问题**，由 @yetval 在 [#245](https://github.com/D4Vinci/Scrapling/pull/245) 中贡献。
- **修复 `TypeError: Session.request() got an unexpected keyword argument 'block_ads'` 错误**，该错误出现在 CLI 的 `--ai-targeted` 选项用于 HTTP 命令时。由 @voidborne-d 在 [#249](https://github.com/D4Vinci/Scrapling/pull/249) 中贡献（修复 [#247](https://github.com/D4Vinci/Scrapling/issues/247)）

### 翻译 {#v0.4.7-translations}

- **新增巴西葡萄牙语 README 翻译**，由 @rgomids 在 [#250](https://github.com/D4Vinci/Scrapling/pull/250) 中贡献

## [v0.4.6](https://github.com/D4Vinci/Scrapling/releases/tag/v0.4.6) - 2026-04-13 {#v0.4.6}

**本次更新专注于浏览器隐身、隐私和开发体验 🔒**

### 🚀 新功能与使用体验改进 {#v0.4.6-new-stuff-and-quality-of-life-changes}

- **为浏览器 Fetcher 添加内置广告拦截**。传入 `block_ads=True`，即可在路由拦截阶段阻止对约 3,500 个已知广告和跟踪域名的请求：不发起 DNS 或 TCP，立即中止。可与 `blocked_domains` 配合使用自定义列表。MCP 服务器和 CLI 的 `--ai-targeted` 模式会自动启用该功能，以减少 token 消耗并加快页面加载。

    ```python
    page = StealthyFetcher.fetch('https://example.com', block_ads=True)
    ```

- **新增 DNS-over-HTTPS 支持**，防止使用代理时泄露 DNS。传入 `dns_over_https=True`，通过 Cloudflare 的 DoH 服务发送 DNS 查询，避免 HTTP 流量经过代理时，DNS 解析仍暴露真实位置。

    ```python
    page = StealthyFetcher.fetch('https://example.com', proxy='http://proxy:8080', dns_over_https=True)
    ```

- **为浏览器 Fetcher 添加 `page_setup` 回调**。该函数在 `page.goto()` 之前执行，可以注册必须在页面导航前设置好的事件监听器、路由或脚本。它与 `page_action` 配合使用，后者在导航后运行。（解决 [#237](https://github.com/D4Vinci/Scrapling/issues/237)）

    ```python
    def capture_websockets(page):
        page.on("websocket", lambda ws: print(f"WS: {ws.url}"))

    page = DynamicFetcher.fetch('https://example.com', page_setup=capture_websockets)
    ```

- **新增 CLI 选项 `--block-ads` 和 `--dns-over-https`，用于 `fetch` 和 `stealthy-fetch` 命令**。

### 🐛 问题修复 {#v0.4.6-bug-fixes}

- **修复 `Seconds` 类型别名拒绝浮点数的问题**。向浏览器 Fetcher 传入 `wait=1.5` 或 `timeout=500.0` 时曾会出现类型错误，因为类型别名错误地将 `float` 当成元数据，而不是类型。由 @kuishou68 在 [#240](https://github.com/D4Vinci/Scrapling/pull/240) 中贡献
- **修复生成完整路径选择器时 ID 片段重复的问题**。生成完整 CSS/XPath 路径时，带有 `id` 属性的元素，其选择器会被重复添加，得到 `body > #main > #main > #target > #target` 之类的选择器。同时修复完整 XPath 路径生成单独的条件 `[@id='x']`（无效 XPath），而不是 `*[@id='x']` 的问题。由 @sjhddh 在 [#241](https://github.com/D4Vinci/Scrapling/pull/241) 中贡献
- **补全 Shell 函数签名中缺少的参数**。交互式 Shell 的函数签名原先缺少 `blocked_domains`、`block_ads`、`retries`、`retry_delay`、`capture_xhr`、`executable_path` 和 `dns_over_https`。

## [v0.4.5](https://github.com/D4Vinci/Scrapling/releases/tag/v0.4.5) - 2026-04-07 {#v0.4.5}

**本次更新为 Spider 开发者带来一个大幅改善使用体验的功能，以及几项重要修复 🎉**

### 🚀 新功能与使用体验改进 {#v0.4.5-new-stuff-and-quality-of-life-changes}

- **Spider 开发模式**：以前修改 Spider 的 `parse()` 逻辑，每次运行都要重新访问目标服务器，既慢又会产生额外流量，还可能在调整选择器时就触发限流。新的开发模式会在首次运行时将每个响应缓存到磁盘，以后的运行直接从磁盘重放。这样就能反复修改回调并运行，而不发出任何网络请求。设置一个类属性即可启用：

    ```python
    class MySpider(Spider):
        name = "my_spider"
        start_urls = ["https://example.com"]
        development_mode = True

        async def parse(self, response):
            yield {"title": response.css("title::text").get("")}
    ```

    缓存默认保存在 `.scrapling_cache/{spider.name}/`，可用 `development_cache_dir` 改到其他位置。新增的 `cache_hits` 和 `cache_misses` 统计项用于查看缓存表现。重放缓存会跳过 `download_delay`、限流和被封锁请求的重试流程，让调试速度只受磁盘速度限制。不要在生产环境中启用 `development_mode = True`；它是开发工具，不是生产缓存。完整说明见[文档](spiders/advanced.md#development-mode)。

- **默认使用更安全的重定向**：所有 HTTP Fetcher、MCP 服务器和 Shell 中，`follow_redirects` 的默认值现在为 `"safe"`。仍会跟随重定向，但会拒绝指向内部或私有 IP 的地址（回环地址、私有网络、链路本地地址）。这能在抓取用户提供的 URL 时防范 SSRF。传入 `follow_redirects="all"` 可恢复旧行为，传入 `False` 则完全禁用重定向。

### 🐛 问题修复 {#v0.4.5-bug-fixes}

- **强制停止不再丢失检查点**：对于启用 `crawldir` 的 Spider，连续按两次 Ctrl+C（强制停止）以前可能与检查点写入发生竞争。取消作用域会在 pickle 写入完成前结束任务，留下 `paused=False`，进而触发会*删除*旧检查点的清理流程。因此，强制停止长时间抓取可能丢失原本想保存的所有进度。引擎现在会在调用 `cancel_scope.cancel()` **之前**写入检查点，确保强制停止时始终保留最新的待处理状态。由 @voidborne-d 在 [#230](https://github.com/D4Vinci/Scrapling/pull/230) 中贡献。

## [v0.4.4](https://github.com/D4Vinci/Scrapling/releases/tag/v0.4.4) - 2026-04-05 {#v0.4.4}

**新版本带来重要的 Spider 改进和问题修复 🎉**

### 🚀 新功能与使用体验改进 {#v0.4.4-new-stuff-and-quality-of-life-changes}
- **为 Spider 框架添加 robots.txt 支持**，通过新的 `robots_txt_obey` 选项启用。启用后，Spider 会在抓取前自动获取并遵守 robots.txt 规则，包括 `Disallow`、`Crawl-delay` 和 `Request-rate`。robots.txt 文件会并发获取，并按域名缓存到整个抓取任务结束。由 @AbdullahY36 在 [#226](https://github.com/D4Vinci/Scrapling/pull/226) 中贡献
- **新增 robots.txt 缓存预热**，在抓取循环开始前获取并解析所有 start_urls 域名的 robots.txt，避免首次请求各域名时等待。
- **新增 `robots_disallowed_count` 统计项，加入 `CrawlStats`**，用于记录抓取过程中有多少请求被 robots.txt 规则阻止。

点击[这里](spiders/getting-started.md#robotstxt-compliance)查看网站上的说明

### 🐛 问题修复 {#v0.4.4-bug-fixes}
- **修复 `ProxyRotator` 中一个严重的 MRO 问题**：占位方法 `_build_context_with_proxy` 遮蔽了子类的实际实现，导致代理轮换总是抛出 `NotImplementedError`（修复 [#215](https://github.com/D4Vinci/Scrapling/issues/215)）。感谢 @yetval
- **修复浏览器会话按请求轮换代理时的页面池泄漏**。临时上下文中创建的页面在清理时没有从池中移除，导致失效引用不断积累。由 @yetval 在 [#223](https://github.com/D4Vinci/Scrapling/pull/223) 中贡献
- **补充静态 Fetcher 中缺少的类型断言**。此前 `curl_cffi` 可能返回 `None` 作为 `session.request()` 的结果，进而引发后续错误。

### 其他变更 {#v0.4.4-other}
- 更新依赖，包含最新指纹和其他更新。
- 新增依赖 `protego`，放入可选的 `fetchers` 依赖组，用于解析 robots.txt。

## [v0.4.3](https://github.com/D4Vinci/Scrapling/releases/tag/v0.4.3) - 2026-03-30 {#v0.4.3}

**新版本包含许多重要变更 🎉**

### 🚀 新功能与使用体验改进 {#v0.4.3-new-stuff-and-quality-of-life-changes}
- **新增 MCP 工具**，用于打开持久化的普通或隐身浏览器，供其他工具继续使用；同时新增另一个工具来关闭它。（[示例](https://github.com/D4Vinci/Scrapling/blob/v0.4.3/docs/ai/mcp-server.md#examples)）
- **新增 MCP 工具**，列出所有现有浏览器会话，配合新工具使用。
- **为浏览器会话添加新选项**，自动收集一次请求期间产生的所有后台请求（解决 [#159](https://github.com/D4Vinci/Scrapling/pull/159)）[[示例](https://github.com/D4Vinci/Scrapling/blob/v0.4.3/docs/fetching/dynamic.md#capturing-xhrfetch-requests)]。
- **新增内容清理功能**，移除隐藏或不可见的内容，保护 MCP 服务器免受常见提示词注入攻击。
- **为网页抓取命令添加 `--ai-targeted` 命令行选项**，让内容适合 AI 使用，并像 MCP 服务器一样防范常见的提示词注入攻击。
- **为浏览器会话添加 `executable_path` 选项**，允许指定自定义浏览器路径（解决 [#202](https://github.com/D4Vinci/Scrapling/pull/202)）
- **重构** MCP 服务器代码，让维护更方便，并统一将所有工具改为异步。
- **重构** CLI 命令代码，让维护更方便，并减少 210 行代码。

### 🐛 问题修复 {#v0.4.3-bug-fixes}
- 修复 Spider 会话重试时没有保留 HTTP 方法的问题，由 @karesansui-u 在 [#201](https://github.com/D4Vinci/Scrapling/pull/201) 中贡献
- 为获取页面内容添加最大重试次数，避免死循环，由 @haosenwang1018 和 @D4Vinci 在 [#197](https://github.com/D4Vinci/Scrapling/pull/197) 中贡献
- 将不带参数的 `raise` 替换为 `return False`，应用于 `_restore_from_checkpoint`，由 @haosenwang1018 在 [#196](https://github.com/D4Vinci/Scrapling/pull/196) 中贡献
- 将 `get_all` 替换为 `getall`，让 `Texthandler` 与 Selector 类保持一致。

### 测试与覆盖率改进 {#v0.4.3-coverage-tests-improvement}
- 添加 `_normalize_credentials` 的边界情况测试，由 @Bortlesboat 在 [#192](https://github.com/D4Vinci/Scrapling/pull/192) 中贡献
- 添加保存后再读取的往返测试，以及核心存储的覆盖测试，由 @haosenwang1018 在 [#193](https://github.com/D4Vinci/Scrapling/pull/193) 中贡献
- 添加对 `TextHandler` 正则处理路径和 `TextHandlers.re()` 的测试覆盖，由 @haosenwang1018 在 [#194](https://github.com/D4Vinci/Scrapling/pull/194) 中贡献
- 添加 `filter`、`iterancestors` 和 `find_similar` 的边界情况测试，由 @awanawana 在 [#200](https://github.com/D4Vinci/Scrapling/pull/200) 中贡献

### Agent Skill 改进 {#v0.4.3-agent-skill-improvement}
- 修复 Skill 参考资料中的失效 Markdown 链接，由 @yetval 在 [#204](https://github.com/D4Vinci/Scrapling/pull/204) 中贡献
- 改进 Skill 结构，使其更符合 [Clawhub](https://clawhub.ai/d4vinci/scrapling-official) 的验证要求。
- 要求 Skill 通过命令行抓取时使用 `--ai-targeted` 选项。

### 文档改进 {#v0.4.3-docs-improvement}
- 添加韩语 README 翻译，由 @greatsk55 在 [#187](https://github.com/D4Vinci/Scrapling/pull/187) 中贡献
- 修复中文和日文 README 中 CJK 字符与拉丁字符之间的空格。
- 修复旧网站设计中遗留的失效链接。

## [v0.4.2](https://github.com/D4Vinci/Scrapling/releases/tag/v0.4.2) - 2026-03-08 {#v0.4.2}

**一次包含重要变更的维护更新**

#### 问题修复 {#v0.4.2-bug-fixes}
- `get_all_text()` 函数现在会获取元素结束标签后的文本节点。这让 MCP 服务器和命令能够读取之前遗漏的文本（[#168](https://github.com/D4Vinci/Scrapling/pull/168)）。感谢 @mhillebrand
- Referer 现在使用 Google 首页 URL，而不是 Google 搜索 URL。之前的逻辑不正确，可能留下可用于指纹识别的特征（[#179](https://github.com/D4Vinci/Scrapling/pull/179)）。感谢 @Bortlesboat
- 修复了所有浏览器中额外启动参数的拼接问题。感谢 @rostchri
- 修复了在低于 3.12 的 Python 版本中导致程序崩溃的类型提示问题。（解决 [#163](https://github.com/D4Vinci/Scrapling/issues/163)）

#### 其他 {#v0.4.2-other}
- 为 Claude Code / OpenClaw 和其他 AI 智能体工具添加了 Agent Skill。
- 将 Agent Skill 添加到了 Clawhub。
- 将所有浏览器和 Playwright 更新到最新版本。
- 为主 README 文件添加了法语翻译。

## [v0.4.1](https://github.com/D4Vinci/Scrapling/releases/tag/v0.4.1) - 2026-02-27 {#v0.4.1}

**一次包含多项重要变更的新更新**

### 🚀 新功能与使用体验改进 {#v0.4.1-new-stuff-and-quality-of-life-changes}
- **提高了正则表达式的准确性**，使 Cloudflare 验证检测更准确（感谢 @Rinz27 [#133](https://github.com/D4Vinci/Scrapling/pull/133)）
- **提高了 Cloudflare 验证处理的速度和效率**。现在的速度接近原来的两倍。
- **改进了 Cloudflare 验证处理逻辑**，能够应对某些网站在跳转到主站之前连续两次显示 Cloudflare 验证页面的情况。
- 通过移除注入的 JS 文件，**提高了隐身浏览器的隐蔽性和速度**。
- **改进了 MCP schema**，使 OpenCode 能够接受它（感谢 @robin-ede [#137](https://github.com/D4Vinci/Scrapling/pull/137)）
- **进一步改进了 MCP schema 的兼容性**，使 VS Code Copilot 和其他要求严格的工具能够接受它。（解决 #150）
- 启用 `main_content_only` 选项时会移除无用的 HTML 标签，**大幅减少了 MCP 服务器的 token 用量**。
- 修复了 PyPI 页面，并添加了将 MCP 服务器注册到 MCP 服务器注册表所需的文件。
- 添加了新的代码示例，展示如何通过代码安装浏览器依赖，而不必使用命令行，让自动化更方便。
- 将所有工作流中的 actions 更新到最新版本（感谢 @salmanmkc [#143](https://github.com/D4Vinci/Scrapling/pull/143)/[#144](https://github.com/D4Vinci/Scrapling/pull/144)）

## [v0.4](https://github.com/D4Vinci/Scrapling/releases/tag/v0.4) - 2026-02-15 {#v0.4}

**Scrapling 迄今为止最大的一次发布：推出 Spider 框架、代理轮换和重要的解析器改进**

这个版本带来了全异步爬虫框架、智能代理管理和重要的 API 变更，让 Scrapling 更强大、更一致。升级前请仔细阅读不兼容变更部分。

### 🕷️ Spider 框架 {#v0.4-spider-framework}

基于 `anyio` 的全新异步爬虫框架，适合有组织的大规模抓取：

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

-  **类似 Scrapy 的 Spider API**：通过 `start_urls`、异步 `parse` 回调、`Request`/`Response` 对象和优先队列定义爬虫。
- **并发抓取**：可设置并发上限、按域名限速和下载延迟。
- **多会话支持**：在同一个爬虫中，通过统一接口使用 HTTP 请求和隐身无头浏览器，按 ID 将请求分配给不同会话。支持按需初始化会话。
- **暂停与恢复**：通过检查点保存抓取进度。按 Ctrl+C 安全关闭，再次启动即可从停止的位置继续。
- **流式模式**：通过 `async for item in spider.stream()` 实时接收抓取到的数据，并查看实时统计，适合 UI、数据处理流程和长时间运行的抓取任务。
- **被拦截请求检测**：自动检测并重试被拦截的请求，支持自定义逻辑。
- **内置导出**：可通过钩子和自己的数据处理流程导出结果，也可以分别使用内置的 `result.items.to_json()` / `result.items.to_jsonl()` 导出 JSON/JSONL。
- **生命周期钩子**：通过 `on_start()`、`on_close()`、`on_error()`、`on_scraped_item()` 等钩子全面控制抓取过程。
- **详细抓取统计**：记录请求、响应、字节数、状态码、代理、按域名和会话分类的数据、各日志级别的数量等信息。
- **uvloop 支持**：将 `use_uvloop=True` 传给 `spider.start()`，可在 uvloop 可用时加快异步执行。

文档网站新增了介绍完整细节的章节。点击[这里](spiders/architecture.md)查看。

### 🔄 代理轮换 {#v0.4-proxy-rotation}

* 新增 `ProxyRotator` 类，支持线程安全的代理轮换。适用于所有 Fetcher 和会话：

  ```python
  from scrapling import ProxyRotator
  rotator = ProxyRotator(["http://proxy1:8080", "http://proxy2:8080"])
  Fetcher.get(url, proxy_rotator=rotator)
  ```

* **自定义轮换策略**：编写自己的代理轮换逻辑。
* **为单次请求指定代理**：将 `proxy=` 传给任意一次 `get()`/`post()`/`fetch()` 调用，即可为该请求覆盖会话代理。

### 🌐 浏览器 Fetcher 改进 {#v0.4-browser-fetcher-improvements}

* **域名拦截**：新增 `blocked_domains` 参数，可用于 `DynamicFetcher`/`StealthyFetcher`，阻止向指定域名发送请求（自动匹配子域名）。
* **自动重试**：浏览器 Fetcher 现在会在失败时重试，通过 `retries`（默认：3）和 `retry_delay`（默认：1s）参数控制，并能识别代理相关错误。
* **响应元数据**：`Response.meta` 字典会自动保存所用的代理，并合并请求元数据。
* **Response.follow()**：创建后续 `Request` 对象，自动传递 Referer，专为爬虫系统设计。
* **禁止自动播放**：浏览器会话现在会阻止内容自动播放，避免之前出现的问题。
* **速度**：通过调整浏览器启动参数，提高了隐蔽性和速度。

### 🔧 问题修复与改进 {#v0.4-bug-fixes-improvements}
- **解析器优化**：针对重复操作优化了解析器，提高了性能。
- **页面错误**：修复了页面报错时浏览器无法关闭的问题。
- **空响应体**：支持处理响应体为空的响应。
- **Playwright 事件循环**：解决了 CDP 连接失败时 Playwright 事件循环未关闭的问题。
- **类型安全**：修复了所有 mypy 错误，并为没有类型标注的函数体补充了类型提示。在 CI 工作流中添加了 mypy 和 pyright。

### ⚠️ 不兼容变更 {#v0.4-breaking-changes}

* **移除了 `css_first`/`xpath_first`**：请改用 `css('.selector').first`、`css('.selector')[0]` 或 `css('.selector').get()`。
* **所有选择操作现在都返回 `Selectors`**：`css('::text')`、`xpath('//text()')`、`css('::attr(href)')` 和 `xpath('//@href')` 现在返回 `Selectors`（文本节点被包装为 `Selector` 对象，并带有 `tag="#text"`），不再返回 `TextHandlers`。这样，所有选择方法及其类型提示都保持一致。
* **`Response.body` 始终为 `bytes`**：之前可能是 `str` 或 `bytes`，现在始终返回 `bytes`。
* **`get()`/`getall()` 的行为**：在 `Selector` 上，`get()` 返回 `TextHandler`（序列化后的 HTML 或文本值），`getall()` 返回 `TextHandlers`。别名为 `extract_first = get`、`extract = getall`。旧的 `get_all()` 已从 `Selectors` 中移除。
* **`Selectors.first`/`.last`**：可安全访问元素，返回 `Selector | None`，不会抛出 `IndexError`。
* **内部常量重命名**：`DEFAULT_FLAGS` → `DEFAULT_ARGS`、`DEFAULT_STEALTH_FLAGS` → `STEALTH_ARGS`、`HARMFUL_DEFAULT_ARGS` → `HARMFUL_ARGS`、`DEFAULT_DISABLED_RESOURCES` → `EXTRA_RESOURCES`。

### 🔨 其他变更 {#v0.4-other-changes}

* **依赖变更**：将 `tldextract` 替换为 `tld`，移除了内部的 `_html_utils.py`，改用 `w3lib.html.replace_entities`，并将 `typing_extensions` 加为必需依赖。
* **文档全面更新**：从 MkDocs 完全切换到 Zensical，新增爬虫文档章节，更新所有已有页面，并添加新的 API 参考。

## [v0.3.14](https://github.com/D4Vinci/Scrapling/releases/tag/v0.3.14) - 2026-01-03 {#v0.3.14}

**一次小型维护更新，修复 v0.3.13 在部分设备上出现的问题**

- 禁用了 `StealthyFetcher` 及其会话类的无痕模式，因为它会导致 Windows 设备上的 Cookie 无法在页面之间保留。MacOS 和 Linux 没有这个问题（修复 [#123](https://github.com/D4Vinci/Scrapling/issues/123)，感谢 @frugality4121 提出问题，也感谢 @gembleman 指出解决方法）。
- 固定使用 browserforge 的最新版本，解决已有旧版 browserforge 的用户遇到的请求头模型过旧问题。

## [v0.3.13](https://github.com/D4Vinci/Scrapling/releases/tag/v0.3.13) - 2026-01-01 {#v0.3.13}

**这是一次大型更新，改进了多个方面，也出于必要原因引入了多项不兼容变更。更新前请阅读以下内容。**

* 出于多方面的原因，我们决定从现在起完全停止使用 Camoufox。如果它继续开发，我们以后可能会重新采用它。如果你想像这个版本之前一样继续使用 Camoufox，请参阅[这一节](https://github.com/D4Vinci/Scrapling/blob/v0.3.13/docs/fetching/stealthy.md#using-camoufox-as-an-engine)中的说明。

* 之前，我们在 `DynamicFetcher` 及其会话类的隐身模式中使用 patchright。现在移除了它们的隐身模式，改为在 `StealthyFetcher` 及其会话类中使用 patchright。我们还做了大量改进，进一步增强了 patchright 基础上的整体隐蔽性，具体见下文。

**这让 `StealthyFetcher` 及其会话类的速度提高了 101%，内存和空间用量更少，代码减少了约 400 行。更重要的是，它们比之前使用 Camoufox 时更稳定。**

这也会缩短 `scrapling install` 命令的安装时间，减小 Docker 镜像，让 GitHub CI 中的测试更顺畅，并让新用户更容易理解 Scrapling。

### 不兼容变更 {#v0.3.13-breaking-changes}
1. `stealth` 参数已从 `DynamicFetcher` 类及其会话类中移除，`hide_canvas` 参数则移到了 `StealthyFetcher` 及其会话类。
2.  将 `disable_webgl` 参数从 `DynamicFetcher` 移到了 `StealthyFetcher` 类，并重命名为 `allow_webgl`。所有会话类也做了相同调整。
3. `StealthyFetcher` 类现在基本上是 `DynamicFetcher` 的新版隐身版本，因此移除了以下参数：`block_images`、`humanize`、`addons`、`os_randomize`、`disable_ads` 和 `geoip`。我尝试在 Chromium 中实现这些功能，但每个都有自己的问题。这可能会在 v0.4 之前的后续版本中改变。

接下来是好消息，我们做了很多改进和修复 :)

### 改进 {#v0.3.13-improvements}
- 你已经知道，`StealthyFetcher` 类及其会话类的速度提高了 101%。现在，`DynamicFetcher` 类及其会话类的速度也提高了 20%。
- 改进了 Cloudflare 验证处理算法，使其更快完成，并能处理更多情况。由于这次重构，验证码处理速度也提高到原来的两倍！
- 所有 Fetcher 的内存用量都减少了。
- MCP 服务器现在使用更少的 token，帮你节省更多费用！
- Docker 镜像现在缩小了 60%。
- 整个文档网站都更新了新内容。同时，说明更清楚，多个章节更精简，新增了更多示例，补全了遗漏的参数，并为 API 参考添加了图表，还有许多其他改进。网站加载速度现在提高了 130%，流量更少，也更利于 SEO。

### 问题修复 {#v0.3.13-fixes}
- 为网页抓取 Shell 的快捷方法补全了之前遗漏的参数，并让它们更准确。
- 修复了即使 URL 为 localhost/IP，`google_search` 参数仍会创建 Google Referer 的问题。

## [v0.3.12](https://github.com/D4Vinci/Scrapling/releases/tag/v0.3.12) - 2025-12-18 {#v0.3.12}

### 更新内容 {#v0.3.12-what-s-changed}
- 为 `DynamicSession`/`AsyncDynamicSession` 类添加了 `timezone_id` 参数，可以设置浏览器时区，使其与使用的代理或 VPN 的时区一致。这样，网站就无法通过时区不一致来发现你使用了代理。
- 改进了将响应自动转换为 JSON 的处理方式。
- 将 Fetcher 会话类中的内部函数 `__create__` 重命名为 `start`，更方便在 `with` 上下文之外使用这些会话类。
- 将 `curl_cffi` 和其他依赖更新到最新版本。

## [v0.3.11](https://github.com/D4Vinci/Scrapling/releases/tag/v0.3.11) - 2025-12-03 {#v0.3.11}

### 更新内容 {#v0.3.11-what-s-changed}
- 改进了在不稳定的网站（如正在播放媒体的网站）上使用 `network_idle` 参数时的超时错误处理逻辑。
- 修复了网页抓取 Shell 中 `stealthy_fetch` 快捷方法的自动补全。

## [v0.3.10](https://github.com/D4Vinci/Scrapling/releases/tag/v0.3.10) - 2025-11-26 {#v0.3.10}

**一次包含多项重要变更和潜在不兼容变更的维护更新**

- **解决了**所有编码问题，采用更好的方法处理未正确声明编码的网页（感谢 @Kemsty2 在 [#110](https://github.com/D4Vinci/Scrapling/issues/110) [#111](https://github.com/D4Vinci/Scrapling/pull/111) 中指出这个问题）。
- **解决了**所有浏览器 Fetcher 中从 v0.3 起就存在的逻辑问题：请求级参数无法正确覆盖会话级参数。
- **修复了**交互式网页抓取 Shell 中快捷方法的函数签名，使快捷方法在 Shell 中能够准确自动补全。这个问题也从 v0.3 起就存在。
- **更新了** Maxmind 数据库版本，改善了 `geoip` 参数在 `StealthyFetcher` 及其会话类中的效果。
- **更新了**所有使用的浏览器，均升级到了最新版本。
- **不兼容变更**：所有 Fetcher 都经过了大规模重构，带来了一些可能影响现有代码的变化：
    1. Scrapling 代码减少了约 750 行，还做了多项调整，让后续维护更简单，资源用量也略有减少。
    2. 所有 Fetcher 及其会话类的参数校验都变得更快，从而提高了整体速度。
    3. 为此，所有 Fetcher 现在只允许 `url` 使用位置参数，其余都必须使用关键字参数。因此，如果你之前写的是位置参数形式，现在必须写成 `Fetcher.get('https://google.com', stealthy_headers=True)`，不能写成 `Fetcher.get('https://google.com', True)`！
    4. 从 v0.3 起，浏览器 Fetcher 及其会话类之间一直存在一个不便之处：为单次请求传入自定义解析器设置的参数在 Fetcher 中叫 `custom_config`，在会话类中却叫 `selector_config`。这次重构在不影响现有代码的情况下，将名称统一为 `selector_config`。现在主要使用 `selector_config`，同时向后兼容 `custom_config` 参数。只有 `selector_config` 参数支持自动补全。
    5. 为了实现这些改进，我们还改为动态生成 Fetcher 函数的类型提示。如果 IDE 无法正确自动补全，请确保使用较新的版本。我们测试了几乎所有常见的 IDE 和编辑器。

> 我们还更新了所有基准测试表，使用当前结果与所有同类库的最新版本进行对比。

## [v0.3.9](https://github.com/D4Vinci/Scrapling/releases/tag/v0.3.9) - 2025-11-17 {#v0.3.9}

**一次包含多项重要变更的新更新**

### 🚀 新功能与使用体验改进 {#v0.3.9-new-stuff-and-quality-of-life-changes}
- `impersonate` 参数现在可以接收浏览器列表；`Fetcher` 和 `FetcherSession` 每次请求都会从中随机选择一个浏览器。

```python
from scrapling.fetchers import FetcherSession

with FetcherSession(impersonate=['chrome', 'firefox', 'safari']) as s:
  s.get('https://github.com/D4Vinci/Scrapling')
```

- 为 `clean` 方法添加了新参数，这个方法属于 `TextHandler`，可以方便地移除当前文本中的 HTML 实体。
- 大幅改进了文档，更准确地解释了多个部分，并为主 `README.md` 文件添加了自动翻译。

### 🐛 问题修复 {#v0.3.9-bug-fixes}
- 修复了从浏览器 Fetcher 获取响应时的一个重要问题。现在会智能检测内容类型，确保只有 HTML 内容才会让 `response.body` 包含浏览器渲染后的内容；其他类型则包含最后一次请求的原始内容。这样，下载二进制文件和文本文件时，内容不会被 HTML 标签包裹，同时获取网页时仍能得到所需的渲染后内容。

### 🔨 其他 {#v0.3.9-misc}
- 更新了贡献指南，让说明更清楚、更易懂。
- 添加了新的工作流，强制运行代码质量工具（与 pre-commit 钩子中使用的工具相同）。

## [v0.3.8](https://github.com/D4Vinci/Scrapling/releases/tag/v0.3.8) - 2025-10-27 {#v0.3.8}

**一次包含多项重要变更的新更新**

### 🚀 新功能与使用体验改进 {#v0.3.8-new-stuff-and-quality-of-life-changes}
- 对所有浏览器 Fetcher，使用 `network_idle` 时，即使网站的请求始终没有全部完成，也不再导致代码崩溃。
- 调整了浏览器 Fetcher 获取和检查页面内容的逻辑，让浏览器在 Windows 上也能像在 Linux/MacOS 上一样稳定（这种行为差异来自 Playwright 在 Windows 上的不同实现）。
- 重构了所有校验逻辑，让所有浏览器 Fetcher 的请求速度提高了 8-15%。
- 新增 `extra_flags` 选项，可用于 `DynamicFetcher` 及其会话，让用户在启动浏览器时可以在已有 Chrome 启动参数之外添加自定义参数。
- 调整了上一版本修改的响应捕获路由逻辑：使用 `page_action` 时恢复旧版路由方式。这样，即使 `page_action` 修改了页面却没有发送请求，也能获取最新的页面内容。（感谢 @gembleman 在 [#100](https://github.com/D4Vinci/Scrapling/issues/100) 和 [#102](https://github.com/D4Vinci/Scrapling/pull/102) 中指出问题。）

### 🐛 问题修复 {#v0.3.8-bug-fixes}
- 修复了 DynamicSession 的 async_fetch 中 `load_dom` 的拼写错误。
- 修复了 Cloudflare 验证处理逻辑的一个问题：某些嵌入式验证码在验证完成后不会消失，导致程序一直等待。现在最多等待验证码消失 30 秒，然后将其视为不会消失的类型（修复 #100）。

### 🔨 其他 {#v0.3.8-misc}
- 现在会自动将 Docker 镜像推送到 Dockerhub 和 GitHub 容器注册表，方便用户使用。
- 添加了[新文档页面](https://github.com/D4Vinci/Scrapling/blob/v0.3.8/docs/tutorials/external.md)，介绍如何在 Scrapling 中使用 Scrapeless 浏览器。

## [v0.3.7](https://github.com/D4Vinci/Scrapling/releases/tag/v0.3.7) - 2025-10-12 {#v0.3.7}

**一次包含多项重要变更的新更新**

### 🚀 新功能与使用体验改进 {#v0.3.7-new-stuff-and-quality-of-life-changes}
- 重新设计了 `solve_cloudflare` 参数在 `StealthyFetcher` 中的处理逻辑，使其能够处理各种自定义 Turnstile 实现。
- 重构了整个代码库，使其通过 Pyright 检查。现在各类 IDE 中的使用体验都更完善，也修复了许多问题。
- 重构了请求逻辑，使其更清晰、更快（同时解决 #97）。
- 为所有浏览器会话类添加了 `user_data_dir` 选项，让用户可以复用之前会话的浏览器数据（Cookie、存储等）。不设置时，Playwright 仍会像以前一样在每次运行时使用随机目录。
- 新增 `additional_args` 自定义选项，可用于 `Dynamic fetcher` 及其会话类，让用户可以向 Playwright 上下文传入额外参数，就像之前的 `StealthyFetcher` 一样。
- 改进了所有浏览器中获取最后一次导航响应的路由逻辑。现在原始响应会在浏览器处理前传给解析器，而不是像以前那样先由浏览器处理。这对文本和 JSON 响应很有帮助。

### 🐛 问题修复 {#v0.3.7-bug-fixes}
- 路由逻辑的重写解决了在部分 Windows 设备上获取不稳定网站内容的问题。
- 这个版本中的多项重构同时解决了许多之前难以发现的问题，以及部分 IDE 中奇怪的自动补全问题。
- 修复了文档网站的多处问题。

## [v0.3.6](https://github.com/D4Vinci/Scrapling/releases/tag/v0.3.6) - 2025-10-01 {#v0.3.6}

### 🚀 新功能 {#v0.3.6-new-stuff}
- 改进了 `solve_cloudflare` 参数在 `StealthyFetcher` 及其会话类中的处理逻辑，使其能够处理所有类型的 Turnstile 和 Cloudflare 中间验证页面 🎉
- MCP 服务器现在可选择使用 `Streamable HTTP`，方便对外提供服务。
- 添加了 Docker 支持，每次发布时都会自动构建镜像并推送到 Docker Hub（包含所有浏览器）。

### 🐛 问题修复 {#v0.3.6-bug-fixes}
- 修复了解析器在某些情况下出现的编码问题（常见的 `invalid start byte` 错误）。
- 调整了库中多个部分的结构，修复了一些内存泄漏问题。根据配置不同，现在内存用量会明显减少（同时解决 #92）。
- 改进了多处代码的类型标注，让 IDE 使用体验更好（同时解决 #93）。

## [v0.3.5](https://github.com/D4Vinci/Scrapling/releases/tag/v0.3.5) - 2025-09-20 {#v0.3.5}

**修复多项问题的重要版本**

### 🚀 新功能 {#v0.3.5-new-stuff}
- 所有浏览器 Fetcher（`DynamicFetcher`/`StealthyFetcher`/...）及其会话类的网页获取速度现在提高了 15-20%：
    1. 得益于 @AbdullahY36 在 #87 中对逻辑的改进，页面管理现在快了很多。
    2. 整体优化了校验逻辑，并改进了同步获取时的页面创建，两者一起带来了明显的速度提升。

- 将 `DynamicFetcher` 及其会话类中的 `rebrowser-playwright` 替换为 `PatchRight`，大幅改进了隐身模式：
    1. 之前，`rebrowser-playwright` 会在同时启用 `stealth` 和 `real_chrome` 时关闭，因为它们无法很好地配合。现在使用 `PatchRight` 后不再有这个问题。
    2. 现在可以操作封闭的 Shadow Root，因为 `PatchRight` 会自动处理它们。

### 🐛 问题修复 {#v0.3.5-bug-fixes}
- 修复了使用 `re` 方法时出现的问题，该方法属于 `Selectors` 类。
- 修复了网页抓取 Shell 中 `uncurl` 和 `curl2fetcher` 命令错误解析 curl 的 `--data-raw` 参数的问题。
- 修复了网页抓取 Shell 中 `view` 命令在某些网站编码下出现的问题。
- 修复了影响 `mcp` 模式和 `extract` 命令的内容转换问题。

### 新贡献者 {#v0.3.5-new-contributors}
- @AbdullahY36 在 #87 中做出了首次贡献。

## [v0.3.4](https://github.com/D4Vinci/Scrapling/releases/tag/v0.3.4) - 2025-09-16 {#v0.3.4}

**修复多项问题的重要版本**

### 🚀 新功能 {#v0.3.4-new-stuff}
- 将所有 Fetcher 会话类添加到交互式 Shell 中，无需导入即可直接使用。

### 🐛 问题修复 {#v0.3.4-bug-fixes}
- 为 Windows 上 Playwright API 的一个问题添加了应对方法，该问题出现在处理 Cloudflare 验证时获取页面内容的过程中。
- 修复了交互式 Shell 中 `view` 命令的编码问题。
- 修复了 `max_pages` 参数在 `AsyncStealthySession` 中导致代码崩溃的问题。
- 修复了最近更新引入的问题：`html_content` 和 `prettify` 这两个 `Selector` 类的属性在某些编码下会返回 bytes。现在两者都和之前一样返回字符串。

## [v0.3.3](https://github.com/D4Vinci/Scrapling/releases/tag/v0.3.3) - 2025-09-15 {#v0.3.3}

- 移除了浏览器 Fetcher 中关闭默认标签页的逻辑，因为它会导致崩溃（Mac 上没有出现，只在 Windows 和 Linux 上复现）。

## [v0.3.2](https://github.com/D4Vinci/Scrapling/releases/tag/v0.3.2) - 2025-09-15 {#v0.3.2}

v0.3.2 发布说明

### 🚀 新功能 {#v0.3.2-new-stuff}

- **可选的 Fetcher 依赖**：所有 Fetcher 现在都属于可选依赖组，减小了核心包的体积。因此，基础 `scrapling` 模块现在只包含解析器。要使用 Fetcher 或命令行选项，需要运行：`pip install "scrapling[fetchers]"`。详细安装说明见[这里](index.md#installation)。
- **会话中的单页面配置**：浏览器 Fetcher 的会话类现在支持为会话内的每个页面单独配置。每次获取页面时传入的参数现在都会像会话级参数一样进行校验。更多说明见[文档网站](fetching/stealthy.md#full-list-of-arguments)。
    <br>示例：

    ```python
    with StealthySession(headless=True, solve_cloudflare=True) as session:
        page = session.fetch('https://nopecha.com/demo/cloudflare', google_search=False)
    ```

- **浏览器 Fetcher 改进**
    - 新增选项，可控制是否等待页面中的 JavaScript 执行完成（和之前一样，默认启用）。

        ```python
        with DynamicSession(headless=True, disable_resources=False, network_idle=True) as session:
           page = session.fetch('https://quotes.toscrape.com/', load_dom=False)
        ```

    - `DynamicFetcher` 及其会话类的隐身模式现在更可靠。
    - `DynamicFetcher` 和 `StealthyFetcher` 现在都使用更少的资源（自动查找并关闭 Playwright API 持久上下文打开的默认标签页）。
    - 修复了浏览器 Fetcher 页面轮换中的重要逻辑问题：现在会用新页面替换旧页面。（重复使用的标签页可能残留之前使用过的设置。）
    - `StealthyFetcher` 及其会话类现在略快一些（5%）。

- **增强了 `.body` 属性**：现在原样返回传入的内容，不做处理，支持下载文件和处理非 HTML 请求。下面是下载图片的示例：

    ```python
    from scrapling.fetchers import Fetcher

    page = Fetcher.get('https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/poster.png')
    with open(file='poster.png', mode='wb') as f:
        f.write(page.body)
    ```

### 🐛 问题修复 {#v0.3.2-bug-fixes}

- **解决编码问题**：修复了解析器、mcp 模式和 extract 命令在部分网站上出现的多个编码问题（同时解决 #80 和 #81）。
- **解析更快**：通过多处改进，库的运行速度更快了，更新后的基准测试也体现了这一点。

### 🔨 其他 {#v0.3.2-misc}

- **更新基准测试**：更新了性能基准测试，将当前的速度改进与同类库的最新版本进行对比。
- **重构了大量代码，并用更好的实现替换了无用代码**：代码更少、更清晰，也更容易维护。
- **添加 YouTube 视频**：为 MCP 文档添加了视频内容。
- **新的问题模板**：为无法使用现有模板的用户提供了简单的新模板。
- **CI 工作流优化**：仅修改文档或非代码文件时，测试工作流现在会跳过运行。
- **更新依赖**：将多项依赖升级到了最新版本。
- **代码风格改进**：对所有文件应用了新的 ruff 规则。
- **Pre-commit 钩子**：更新了 pre-commit 配置。

### 🎯 不兼容变更 {#v0.3.2-breaking-changes}

- 移除了 `max_pages` 参数在同步 `StealthySession` 中的支持，与 `DynamicSession` 保持一致（这个参数在同步版本中没有意义）。

## [v0.3.1](https://github.com/D4Vinci/Scrapling/releases/tag/v0.3.1) - 2025-09-02 {#v0.3.1}

1. 修复了不安装 `shell` 扩展依赖时 Scrapling 安装出错的问题（#76）。
2. 为所有浏览器 Fetcher 及其会话类添加了新参数，可以指定一个在页面创建时执行的 JS 文件（#56）：

```python
from scrapling.fetchers import StealthyFetcher

StealthyFetcher.fetch('https://example.com', init_script="/absolute/path/to/js/script.js")
```

## [v0.3](https://github.com/D4Vinci/Scrapling/releases/tag/v0.3) - 2025-09-01 {#v0.3}

🎉 **重大版本：全面重构架构**

Scrapling v0.3 是项目历史上规模最大的一次更新。它重写了整个架构，大幅提升性能，并加入多项强大的新功能，包括 AI 集成和用于网页抓取的交互式 Shell。

此版本包含多项不兼容变更，请仔细阅读版本说明。

### 🚀 主要新功能 {#v0.3-major-new-features}

#### 基于会话的架构 {#v0.3-session-based-architecture}
- **新的会话类**：全面重写，加入持久会话支持
    - `FetcherSession`：发送 HTTP 请求并保留状态，同时支持同步和异步代码
    - `DynamicSession`/`AsyncDynamicSession`：执行浏览器自动化，浏览器会一直保持打开，直到操作结束
    - `StealthySession`/`AsyncStealthySession`：使用隐身浏览器，浏览器会一直保持打开，直到操作结束
- **异步管理浏览器标签页**：新的 `max_pages` 参数提供标签页池，轮流使用标签页来并发获取页面
- **并发会话**：同时运行多个相互隔离的会话

更多信息请参阅网站的 `Fetching` 部分。

#### 多项新的隐身与反机器人应对功能 {#v0.3-a-lot-of-new-stealth-anti-bot-capabilities}
- **🤖 Cloudflare 挑战处理**：在 `StealthyFetcher` 及其会话类中自动[处理 Cloudflare Turnstile 挑战](fetching/stealthy.md#cloudflare-and-stealth-options)
- **模拟浏览器指纹**：全新的 [Fetcher](fetching/static.md) 类可以模拟真实浏览器的 TLS 指纹、生成与浏览器版本匹配的请求头，并支持 HTTP/3 等功能
- **改进隐身模式**：`DynamicFetcher` 及其会话类的隐身模式现在更稳定、更可靠（也称为 `PlayWrightFetcher`）

#### AI 集成与 MCP 服务器 {#v0.3-ai-integration-mcp-server}
- **内置 MCP 服务器**：通过 Model Context Protocol 服务器实现 AI 辅助网页抓取
- **6 个强大的工具**：`get`、`bulk_get`、`fetch`、`bulk_fetch`、`stealthy_fetch`、`bulk_stealthy_fetch`
- **智能内容提取**：将网页或元素转换为 Markdown、HTML，或提取经过清理的文本内容
- **支持 CSS 选择器**：将内容交给 AI 前，先用 Scrapling 引擎精确选择所需元素
- **绕过反机器人防护**：处理 Cloudflare Turnstile 和其他防护
- **支持代理**：使用代理隐藏身份，或从指定地区发送请求
- **模拟浏览器**：使用 TLS 指纹、与浏览器版本匹配的真实请求头等来模拟真实浏览器
- **并行处理**：同时抓取多个 URL，提高效率
- [还有更多...](ai/mcp-server.md)

#### 新的网页抓取交互式 Shell {#v0.3-new-interactive-web-scraping-shell}
- **新的 Shell**：定制的 IPython Shell，内置许多实用快捷方式，例如 `get`、`post`、`put`、`delete`、`fetch` 和 `stealthy_fetch`
- **智能页面管理**：新的 `page` 和 `pages` 命令会自动保存当前页面，以及所有通过 Shell 发出的请求的历史记录
- **Curl 集成**：使用 `uncurl` 和 `curl2fetcher` 函数，将浏览器开发者工具中的 curl 命令转换为 `Fetcher` 请求
- [还有更多...](cli/interactive-shell.md)

#### 无需编程，直接在终端抓取网页 {#v0.3-scrape-from-the-terminal-without-programming}
- **新的提取命令**：无需编程，在终端中抓取网页
    - `scrapling extract get/post/put/delete`：发送简单的 HTTP 请求
    - `scrapling extract fetch`：抓取动态内容
    - `scrapling extract stealthy-fetch`：绕过反机器人防护
- **下载网页**，并将内容保存到文件。
- **将 HTML 转换为易读的格式**，例如 Markdown，也可以保留 HTML，或只提取页面的文本内容。
- **支持自定义 CSS 选择器**，用于提取页面的指定部分。
- **支持 HTTP 请求和浏览器页面获取。**
- **可灵活配置**，包括自定义请求头、Cookie、代理及其他选项。代码中可用的选项几乎都能在终端中使用。
- [还有更多...](cli/extract-commands.md)

### 🔧 技术改进 {#v0.3-technical-improvements}

#### 性能提升 {#v0.3-performance-enhancements}
- **Fetcher 的速度现在是原来的 4 倍**：没错，你没有看错！
- **DynamicFetcher 的速度提高约 60%**：具体提升取决于配置，尤其是隐身模式
- **StealthyFetcher 的速度提高 20–30%**：采用新的结构，并开始使用我们自己的实现，替代 `Camoufox` 的 Python 接口
- **核心查询方法的综合速度提升至少 50%**，包括 `find_by_text`、`find_similar`、`find_by_regex`、`relocate` 等 🚀
- **CSS/XPath 的 first 方法速度提高约 10%**：`css_first` 和 `xpath_first` 现在比 `css` 和 `xpath` 更快
- **用于内容提取的 `get_all_text()` 方法速度提高 40%**
- **自适应元素重定位的速度提高 20%**
- **优化导航属性**：`next`、`previous`、`below_elements` 等属性现在明显更快
- **文本清理速度提高到原来的 5 倍**
- **减少内存占用**：优化导入并减少额外开销
- **⚡ 快速导入**：通过优化模块加载来缩短启动时间
- **更好的基准测试结果**：这些改进让 Scrapling 相比其他库的速度优势更大，是 BeautifulSoup 的 1775 倍、AutoScraper 的 5.1 倍，详见[基准测试](benchmarks.md)

#### 架构、代码质量与使用体验 {#v0.3-architecture-code-quality-and-quality-of-life}
- **持久化上下文**：所有浏览器 Fetcher 现在默认使用持久化上下文。（也解决了 #64）
- **使用 msgspec 快速验证所有浏览器 Fetcher**，在发送请求前完成检查，让错误更容易排查。
- **Fetcher 返回的所有 Cookie** 现在都符合该 Fetcher 接受的格式。你可以获取 Cookie，再传给所有 Fetcher 及其会话类。
- **代码检查和格式化更快**：迁移到 `ruff`
- **现代化的构建系统**：从 setup.py 迁移到 pyproject.toml 📦
- **改进 GitHub Actions 和工作流**，让开发和测试更顺畅
- **🎨 改进类型提示**：按照现代 Python 标准提供完整的类型标注，改善 IDE 支持和可靠性
- **更清晰的代码**：移除不再使用的代码，并优化核心函数 🧹
- **🚀 向后兼容**：添加快捷方式，让旧代码可以继续使用

### 不兼容变更 {#v0.3-breaking-changes}

#### 最低 Python 版本 {#v0.3-minimum-python-version}
- **需要 Python 3.10+**：不再支持 Python 3.9 及更早版本

#### 类和方法的命名 {#v0.3-class-and-method-naming}
这些更名让命名更加清晰、统一，尤其方便新用户理解。

- **`Adaptor` → `Selector`**：核心解析类更名（为保持向后兼容，仍可使用 `Adaptor` 导入）
- **`Adaptors` → `Selectors`**：集合类更名（为保持向后兼容，仍可使用 `Adaptors` 导入）
- **`auto_match` → `adaptive`**：在所有方法中更改参数名
- **`adaptor_arguments` → `selector_config`**：更改配置参数名
- **`automatch_domain` → `adaptive_domain`**：更改域名参数名
- **`additional_arguments` → `additional_args`**：缩短参数名
- **⚠️ `text/body` → `content`**：Selector 构造函数的这个参数现在同时接受 `str` 和 `bytes`
- **`PlayWrightFetcher` → `DynamicFetcher`**：浏览器自动化类更名（为保持向后兼容，仍可使用 `PlayWrightFetcher` 导入）
- **DynamicFetcher 不再包含 NSTBrowser 的逻辑和参数**，因为已经没有保留这些逻辑的必要。
- **StealthyFetcher 的 headless 参数不再接受 'virtual'**，因为目前只用 Camoufox 库获取浏览器安装路径和其他启动选项

### 🐛 问题修复 {#v0.3-bug-fixes}

- 修复 `get_all_text` 在忽略的标签中统计嵌套子元素的问题（#61）
- 修复 Python 可执行文件路径含有空格时出现的安装问题（#57）
- 修复启用自适应功能时，存储系统在处理递归过程中出现的线程问题
- 在 `FetcherSession` 中使用 Sentinel 模式，修复参数优先级问题
- 修复 `StealthyFetcher` 对代理类型的处理
- 修复 `referer` 与 `google_search` 参数冲突
- 修复异步注入隐身脚本的问题

## [v0.2.99](https://github.com/D4Vinci/Scrapling/releases/tag/v0.2.99) - 2025-04-08 {#v0.2.99}

**这是一次重要更新，建议所有用户更新，以充分使用 Scrapling。**

### 更新内容 {#v0.2.99-what-s-changed}
#### 新的完整文档网站 {#v0.2.99-new-full-documentation-website}
- 是的，终于来了 😄 点击[这里](index.md)查看
#### 统一 Fetcher 的导入方式 {#v0.2.99-unified-import-logic-for-fetchers}
- 现在可以用 `from scrapling.fetchers import Fetcher, AsyncFetcher, StealthyFetcher, PlayWrightFetcher` 导入所有 Fetcher，然后直接调用，例如 `page = Fetcher.get(...)`，无需初始化。<br/>这取代了旧的导入方式 `from scrapling.defaults import Fetcher, AsyncFetcher, StealthyFetcher, PlayWrightFetcher`。
#### 不兼容变更：automatch 现在默认关闭 {#v0.2.99-breaking-change-automatch-is-now-turned-off-by-default}
- 现在可以通过新的方式在 Fetcher 中启用 automatch 或设置其他解析选项，详情请看[文档页面](fetching/choosing.md#parser-configuration-in-all-fetchers)。
>  为保持向后兼容，旧的导入方式和逻辑仍然可用，但会发出警告。
#### 为 Fetcher 添加新选项 {#v0.2.99-new-options-added-to-fetchers}
- `StealthyFetcher` 和 `PlayWrightFetcher` 在获取页面时都新增了 `wait` 参数。它让 Fetcher 在关闭页面并返回响应前，等待指定时间，单位为毫秒。
- `StealthyFetcher` 的 `fetch` 和 `async_fetch` 方法现在接受 `additional_arguments` 参数，用于向 Camoufox 传入额外设置。这些设置的优先级高于 Scrapling 的设置（#54）
#### 问题修复 {#v0.2.99-bugs-squashed}
- 修复 `async_fetch` 中捕获重定向的问题，涉及 `StealthyFetcher` 和 `PlayWrightFetcher` 两个类。

**_感谢大家的支持和捐赠！_**

## [v0.2.98](https://github.com/D4Vinci/Scrapling/releases/tag/v0.2.98) - 2025-03-17 {#v0.2.98}

**这是一次重要更新，建议所有用户更新，以充分使用 Scrapling**

### 更新内容 {#v0.2.98-what-s-changed}
#### 多项内存与速度优化 {#v0.2.98-various-memory-usage-and-speed-optimizations}
- 所有查询方法的内存占用降至原来的约 40%，速度也略有提高。
- 所有子模块现在都延迟加载，只加载实际使用的部分。例如：
更新前，`from scrapling import Adaptor` 会占用 `30-40mb` 内存，因为它同时加载了所有 Fetcher 和其他模块。现在只占用 `~1.2mb`。
- 上次更新已经让库在使用大型请求池时，仅占用原来约 32% 的内存。此次进一步调整缓存，让内存占用更低。
- 解析器的整体速度提高 2-5%

**_感谢大家的支持和捐赠！_**

## [v0.2.97](https://github.com/D4Vinci/Scrapling/releases/tag/v0.2.97) - 2025-03-15 {#v0.2.97}

**这是一次重要更新，建议所有用户更新，以充分使用 Scrapling**

### 更新内容 {#v0.2.97-what-s-changed}
#### 降低所有 Fetcher 的内存占用，并略微提高速度 {#v0.2.97-lower-memory-usage-and-small-speed-increase-across-all-fetchers}
- 在整个库中为缓存大小设置新的限制。执行大量请求或操作时，内存占用会明显低于以前。
- 重构 Fetcher 的大部分代码，使其更易维护，并略微提高速度。

#### 问题修复 {#v0.2.97-bugs-fixed}
- 修复 `TextHandler` 的一个问题：单独导入它后，传入非字符串值会得到空字符串。现在传给 `TextHandler` 的任何值都会先转换为字符串，再转换为 `TextHandler`。这适用于所有传入的值，毕竟 `TextHandler` 顾名思义就是用来处理字符串的！（#45）
- 修复大多数 AsyncFetcher 方法未使用 `retries` 参数的问题。

#### 其他 {#v0.2.97-miscellaneous}
- 更新所有 Fetcher 中大部分参数的类型提示，使其更清晰、更准确。

**_感谢大家的支持和捐赠！_**

## [v0.2.96](https://github.com/D4Vinci/Scrapling/releases/tag/v0.2.96) - 2025-03-05 {#v0.2.96}

**这是一次重要更新，建议所有用户更新，以充分使用 Scrapling**

### 更新内容 {#v0.2.96-what-s-changed}
1. 新增 `-f` 选项，可用于 `scrapling install`，强制重新安装浏览器依赖。建议现在执行 `scrapling install -f`，体验新版 Camoufox 浏览器给 `StealthyFetcher` 带来的大幅速度提升 :)
2. 修复 `TextHandler` 切片返回 `TextHandlers` 而非 `TextHandler` 的问题，并修正相应的类型提示（#41）
3. 修复 `scrapling install` 在某些情况下意外进入 Python Shell 的问题！

## [v0.2.95](https://github.com/D4Vinci/Scrapling/releases/tag/v0.2.95) - 2025-02-25 {#v0.2.95}

**这是一次重要更新，建议所有用户更新，以充分使用 Scrapling**

### 更新内容 {#v0.2.95-what-s-changed}
1. 修复 `Fetcher` 的一个问题：由 `stealthy_headers` 参数生成的请求头会覆盖用户提供的部分请求头，例如 `Accept`（#39）
2. 略微改进请求头生成逻辑，预计速度会有小幅提升。

## [v0.2.94](https://github.com/D4Vinci/Scrapling/releases/tag/v0.2.94) - 2025-02-22 {#v0.2.94}

**这是一次重要更新，建议所有用户更新，以充分使用 Scrapling**

### 更新内容 {#v0.2.94-what-s-changed}
1. 为所有 Fetcher 添加 `history` 属性，用来显示重定向记录（#32）
2. 修复 `case_sensitive` 参数在所有 `re`/`re_first` 方法中的逻辑。如果使用了这个参数，代码现在可能会返回不同的结果（不过，如果你已经发现它有问题却没有提 issue，那这可能也是自找的，哈哈）。
3. 更新依赖，并在 Camoufox 引擎（StealthyFetcher）中重新启用 `coop`。

## [v0.2.93](https://github.com/D4Vinci/Scrapling/releases/tag/v0.2.93) - 2025-01-31 {#v0.2.93}

**这是一次重要更新，建议所有用户更新，以充分使用 Scrapling**

### 更新内容 {#v0.2.93-what-s-changed}
1. 整个解析引擎现在统一了返回类型，总会返回 `Adaptor`、`Adaptors`、`TextHandler`、`TextHandlers`、`None` 之一；若结果混合了多种类型，例如使用组合 CSS 选择器，则返回列表。这样能减少手动类型检查，让编程更方便、库更稳定，并让方法始终可以链式调用。
2. 重构了解析引擎的大部分代码，尤其是 `Adaptor` 类，使代码更清晰，最重要的是更快。几乎所有方法和属性，特别是搜索方法，速度都提高了 5-40%。某些方法提升更大，例如 `find_by_regex` 提速约 60%！automatch 功能也提速约 5%。
3. 修复 `find_all`/`find` 方法的逻辑问题：传入的筛选条件有时按“或”组合，有时按“与”组合。现在返回的元素必须满足所有传入的条件。
4. 所有正则表达式相关方法现在都返回 `TextHandler`/`TextHandlers`，更方便链式调用。
5. **新增** `below_elements` 属性，返回一个 `Adaptors` 对象，包含 DOM 树中当前元素下方的所有元素。
6. 之前将 HTML 源码作为字符串返回的方法和属性，现在都返回 `TextHandler`，方便在结果上使用正则表达式等功能。
7. StealthyFetcher 现在更快，隐身效果也更好。还可以点击 iframe 内的验证码，例如 **Cloudflare Turnstile**。
8. 改善了近一半库代码的自动补全和类型提示，尤其是 `Adaptor`、`TextHandler` 和 `TextHandlers`。
9. 对 `TextHandler` 进行切片、索引访问或调用 `split`，现在都会返回另一个 `TextHandler`，而不是普通 Python 字符串。几乎所有标准字符串操作和方法现在都返回 `Texthandler`，让方法和函数始终可以链式调用。
10. 修复一些小问题和拼写错误。例如，Fetcher 的 async_put 原来发送的是 POST 请求，而不是 PUT 请求 😶‍🌫️
11. 在文档网站完成前，先对 README 做了一些改进。

这本来只是 0.3 之前的一个小更新，但我还是想把它做得更好。

## [v0.2.92](https://github.com/D4Vinci/Scrapling/releases/tag/v0.2.92) - 2024-12-26 {#v0.2.92}

### 更新内容 {#v0.2.92-what-s-changed}
- 当页面包含许多 iframe 时，浏览器 Fetcher 返回的响应现在会使用更可靠的数据源。
- **安装 `Scrapling` 更简单了：用 pip 安装后，在终端运行 `scrapling install`，就可以开始使用！**
- 修正解析器中一处不准确的类型提示。

## [v0.2.91](https://github.com/D4Vinci/Scrapling/releases/tag/v0.2.91) - 2024-12-19 {#v0.2.91}

### 更新内容 {#v0.2.91-what-s-changed}
- 修复页面获取日志只在第一次请求时显示的问题。
- Playwright API 在浏览页面时，默认返回第一个达到 `goto` 所指定加载状态 `["load", "domcontentloaded", "networkidle"]` 的响应。如果网站先显示一个等待页面，例如 Cloudflare 的等待页面，然后再跳转到真实网站，Playwright 会返回第一个状态码，可能是 403。此次更新修复了 `PlaywrightFetcher` 和 `StealthyFetcher` 中的这个问题。它们都使用 Playwright API，但返回结果现在不再受这个默认行为影响。
- 为 `Fetcher` 类添加 SOCKS 代理支持。
- 修正 `wait_selector_state` 参数的类型提示，自动补全现在会显示正确的可用值。

## [v0.2.9](https://github.com/D4Vinci/Scrapling/releases/tag/v0.2.9) - 2024-12-16 {#v0.2.9}

### 更新内容 {#v0.2.9-what-s-changed}
##### 新功能 {#v0.2.9-new-features}
1. Scrapling **期待已久**的异步支持来了！现在有 `AsyncFetcher` 类，作为 `Fetcher` 的异步版本，而 `StealthyFetcher` 和 `PlayWrightFetcher` 也新增了 `async_fetch` 方法，选项与同步版本相同。

```python
>> from scrapling import StealthyFetcher
>> page = await StealthyFetcher().async_fetch('https://www.browserscan.net/bot-detection')  # the async version of fetch
>> page.status == 200
True
```

2. `StealthyFetcher` 类的获取方法新增 `geoip` 参数。启用后，会自动使用 IP 对应的经度、纬度、时区、国家和区域设置，并伪装 WebRTC IP 地址。它还会根据目标地区使用各种语言的人口分布，确定并伪装浏览器语言。
3. 新增 `retries` 参数，适用于 `Fetcher`/`AsyncFetcher` 类，可以设置 `httpx` 发出的每次请求的重试次数。
4. 新增 `url_join` 方法，供 `Adaptor` 和 Fetcher 使用，将相对 URL 与当前 URL 合并，生成完整的绝对 URL！
5. 新增 `keep_cdata` 方法，供 `Adaptor` 和 Fetcher 使用，需要时可以阻止解析器移除 CDATA。
6. `Adaptor`/`Response` 的 `body` 方法现在会在可能的情况下返回原始 HTML 响应，不在库中进行处理。
7. 为 `Response` 类添加日志记录。使用 Fetcher 时，现在会输出包含响应信息的日志。
示例：

   ```python
   >> from scrapling.defaults import Fetcher
   >> Fetcher.get('https://books.toscrape.com/index.html')
   [2024-12-16 13:33:36] INFO: Fetched (200) <GET https://books.toscrape.com/index.html> (referer: https://www.google.com/search?q=toscrape)
   >>
   ```

8. 在 `TextHandler` 上调用标准字符串方法，例如 `.replace()`，现在会得到另一个 `TextHandler`，而不是之前的普通字符串。
9. 大幅提高整个库的速度，并整体改善 Fetcher 类的隐身效果。
10. 添加 `extract_first`\`extract` 等简单函数，返回与父对象相同的结果。这些函数仅用于方便将 Scrapy/Parsel 代码复制到 Scrapling，因为那些库会使用这些函数！
11. 重构了大量代码，并在适当的位置使用缓存，因此批量发送请求的速度大幅提高。

##### 不兼容变更 {#v0.2.9-breaking-changes}
- 不再支持 Python 3.8。（主要是因为 Playwright 已停止支持它，不过这个版本本来也有不少问题。）
- 从整个库中移除了 `debug` 参数。如果要启用调试，请在导入库后执行以下代码：

   ```python
   >>> import logging
   >>> logging.getLogger("scrapling").setLevel(logging.DEBUG)
   ```

##### 问题修复 {#v0.2.9-bugs-squashed}
1. WebGL 现在默认启用，因为许多防护系统会检查它是否开启。
2. 修复文档和 README 中的一些错误和拼写问题。

##### 使用体验改进 {#v0.2.9-quality-of-life-changes}
1. 所有日志现在统一使用名为 `scrapling` 的日志记录器，更容易管理。之前使用的是根日志记录器。
2. 重新整理测试目录，使结构更清晰，并为新功能添加测试。所有测试都经过重写，更易阅读，同时增加更多测试来提高覆盖率。
3. 重构大部分代码，使其更清晰、更易维护。

> 这些变更原本都计划放到 0.3 中，但距离下个版本还有一段时间，所以决定提前加入。下一步是完成详细的文档网站，然后继续开发 0.3 版本。

## [v0.2.8](https://github.com/D4Vinci/Scrapling/releases/tag/v0.2.8) - 2024-11-30 {#v0.2.8}

### 更新内容 {#v0.2.8-what-s-changed}
- 这是一次小更新，包含一些让代码更易用的必要改进，并修复主 README 文件中的一个拼写错误（#20）。

## [v0.2.7](https://github.com/D4Vinci/Scrapling/releases/tag/v0.2.7) - 2024-11-26 {#v0.2.7}

### 更新内容 {#v0.2.7-what-s-changed}
##### 新功能 {#v0.2.7-new-features}
- 使用 `wait_selector` 参数时，在 `StealthyFetcher` 和 `PlayWrightFetcher` 中，Scrapling 现在会再次等待 JavaScript 完全加载并执行。如果还使用了 `network_idle`，完成上述等待后也会再次等待网络空闲。当然，如果所有状态都已满足，就不会额外等待。
- 在 `StealthyFetcher` 中，现在可以用 `disable_ads` 参数允许或屏蔽广告。此选项默认启用，会安装 `ublock origin` 扩展。
- `PlayWrightFetcher` 现在支持通过 `locale` 参数指定区域设置。默认值仍是 `en-US`。
- `Fetcher` 发出的基本请求现在接受 `http://username:password@localhost:8030` 格式的代理。
- 略微改进 `PlayWrightFetcher` 的隐身模式。

##### 问题修复与改进 {#v0.2.7-bugs-squashed-improvements}
1. 在 `PlayWrightFetcher` 类中启用代理，现在不再依赖 `stealth` 模式是否开启（感谢 [@AbdullahY36](https://github.com/AbdullahY36) 指出这个问题）。
2. `ResponseEncoding` 现在会检查响应返回的编码是否适用于页面。如果使用该编码出错，Scrapling 会改用 `utf-8`。

## [v0.2.6](https://github.com/D4Vinci/Scrapling/releases/tag/v0.2.6) - 2024-11-24 {#v0.2.6}

### 更新内容 {#v0.2.6-what-s-changed}
##### 新功能 {#v0.2.6-new-features}
- `PlayWrightFetcher` 现在可以直接使用真实浏览器，只需将 `real_chrome` 参数传给 `PlayWrightFetcher.fetch`。这需要已安装 Chrome。Scrapling 会启动你的 Chrome 浏览器实例，大多数选项都可以照常使用。（之前只能通过 `cdp_url` 参数实现。）
- 更新为真实浏览器生成的请求头中的版本号。

##### 问题修复 {#v0.2.6-bugs-squashed}
1. 发现 `BrowserForge` 生成的浏览器请求头格式已经过时，导致 Scrapling 被某些防护系统识别。因此现在只用 `BrowserForge` 生成真实的 User-Agent。
2. `hide_canvas` 参数现在默认关闭，因为 Google 的 ReCaptcha 会检测到它。

## [v0.2.5](https://github.com/D4Vinci/Scrapling/releases/tag/v0.2.5) - 2024-11-23 {#v0.2.5}

### 更新内容 {#v0.2.5-what-s-changed}

##### 问题修复 {#v0.2.5-bugs-squashed}
- 修复 'wait_selector' 参数匹配到超过 1 个元素时的错误。这会影响 `StealthyFetcher` 和 `PlayWrightFetcher` 类。
- 修复 `content_type` 头字段的值包含 `charset` 等参数时的编码类型问题（感谢 @andyfcx 提交 [#12](https://github.com/D4Vinci/Scrapling/issues/12)）。

##### 使用体验改进 {#v0.2.5-quality-of-life}
- 添加更多测试来覆盖新的代码部分，并让测试在线程中运行。
- 调整文档字符串，使 Sphinx apidoc 等工具可以正确显示。

##### 新贡献者 {#v0.2.5-new-contributors}
- @andyfcx 在 [#13 ](https://github.com/D4Vinci/Scrapling/pull/13) 中做出了首次贡献

## [v0.2.4](https://github.com/D4Vinci/Scrapling/releases/tag/v0.2.4) - 2024-11-20 {#v0.2.4}

### 更新内容 {#v0.2.4-what-s-changed}

##### 问题修复 {#v0.2.4-bugs-squashed}
- 修复使用 `network_idle` 参数后获取响应字节时的问题，涉及 `StealthyFetcher` 和 `PlayWrightFetcher` 两个类。<br/>它会导致以下错误：

    ```
    Response.body: Protocol error (Network.getResponseBody): No resource with given identifier found
    ```

- PlayWright API 有时会返回空的响应状态文本。现在出现这种情况时，`Scrapling` 会自行计算状态文本。这会影响 `StealthyFetcher` 和 `PlayWrightFetcher` 类。

## [v0.2.3](https://github.com/D4Vinci/Scrapling/releases/tag/v0.2.3) - 2024-11-19 {#v0.2.3}

### 更新内容 {#v0.2.3-what-s-changed}

##### 问题修复 {#v0.2.3-bugs-squashed}
- 修复 pip 安装时的一个问题，该问题会导致 PlayWright Fetcher 的隐身模式完全无法使用。

## [v0.2.2](https://github.com/D4Vinci/Scrapling/releases/tag/v0.2.2) - 2024-11-16 {#v0.2.2}

### 更新内容 {#v0.2.2-what-s-changed}
##### 新功能 {#v0.2.2-new-features}
- 如果不需要向生成的 `Adaptor` 对象传入参数，而是使用默认值，现在可以改用以下导入方式，让代码更简洁

    ```python
    >> from scrapling.default import Fetcher, StealthyFetcher, PlayWrightFetcher
    >> page = Fetcher.get('https://example.com', stealthy_headers=True)
    ```

    否则

    ```python
    >> from scrapling import Fetcher, StealthyFetcher, PlayWrightFetcher
    >> page = Fetcher(auto_match=False).get('https://example.com', stealthy_headers=True)
    ```

##### 问题修复 {#v0.2.2-bugs-squashed}
1. 修复昨天的 v0.2.1 补丁引入的 `Response` 对象问题。它会在某些嵌套查询或解析情况下发生。

## [v0.2.1](https://github.com/D4Vinci/Scrapling/releases/tag/v0.2.1) - 2024-11-15 {#v0.2.1}

### 更新内容 {#v0.2.1-what-s-changed}
##### 新功能 {#v0.2.1-new-features}
1. 所有 Fetcher 返回的 `Response` 对象现在与 `Adaptor` 对象相同，但额外包含 `status`、`reason`、`cookies`、`headers` 和 `request_headers` 属性。其中 `cookies`、`headers` 和 `request_headers` 始终是 `dictionary` 类型。<br/>因此，代码现在可以写成：

    ```python
    >> from scrapling import Fetcher
    >> page = Fetcher().get('https://example.com', stealthy_headers=True)
    >> print(page.status)
    200
    >> products = page.css('.product')
    ```

    而不是以前这样

    ```python
    >> from scrapling import Fetcher
    >> fetcher = Fetcher().get('https://example.com', stealthy_headers=True)
    >> print(fetcher.status)
    200
    >> page = fetcher.adaptor
    >> products = page.css('.product')
    ```

    为了向后兼容，`.adaptor` 属性仍然可用。

2. `StealthyFetcher` 和 `PlayWrightFetcher` 类现在都可以在获取方法中接受 `proxy` 参数，值可以是字符串或字典。
3. `StealthyFetcher` 类新增 `os_randomize` 参数，用于 `fetch` 方法。启用后，Scrapling 会随机选择所用的操作系统指纹。默认情况下，指纹与当前操作系统匹配。

##### 问题修复 {#v0.2.1-bugs-squashed}
1. 修复使用 `Fetcher` 类传入请求头时的问题。
2. 修复解析 Fetcher 类传来的 JSON 响应时的问题。

##### 使用体验改进 {#v0.2.1-quality-of-life-changes}
1. 文本功能之前会尝试先删除 HTML 注释，再返回文本，但这在某些情况下会导致错误，也让代码变得不必要地复杂。现在已恢复 lxml 的默认行为，**所有依赖元素文本的操作，例如选择器，速度都会略有提高**。如果希望 Scrapling 在返回文本前删除元素中的 HTML 注释，以避免 lxml/parsel/scrapy 中不直观的文本拆分行为，只需让 `keep_comments` 参数保持默认的 True。

## [v0.2](https://github.com/D4Vinci/Scrapling/releases/tag/v0.2) - 2024-11-11 {#v0.2}

### 更新内容 {#v0.2-what-s-changed}
##### 新功能 {#v0.2-new-features}
1. 推出 `Fetchers` 功能，提供 3 种主要类型，让 Scrapling 为你获取页面，并提供丰富的选项！
    - `Fetcher` 类用于基本 HTTP 请求
    - `StealthyFetcher` 类是一个完全隐身的 Fetcher，使用[经过隐身改造的 Firefox](https://github.com/daijro/camoufox)。
    - `PlayWrightFetcher` 类支持多种基于浏览器的请求方式：原版 PlayWright、使用我编写的隐身模式的 PlayWright、通过 CDP 连接的真实浏览器，以及 [NSTBrowser](https://app.nstbrowser.io/r/1vO5e5) 的 [docker browserless](https://hub.docker.com/r/nstbrowser/browserless)！
2. 添加全新的 `find_all`/`find` 方法，像施魔法一样轻松查找页面元素！
3. 新增 `filter` 和 `search` 方法，加入 `Adaptors` 类，更方便批量处理 `Adaptor` 对象组。
4. 添加 `css_first` 和 `xpath_first` 方法，让使用更简单。
5. 添加新的 `TextHandlers` 类，用于批量处理 `TextHandler` 对象，功能类似 `Adaptors` 类。
6. 添加 `generate_full_css_selector` 和 `generate_full_xpath_selector` 方法。

##### 问题修复 {#v0.2-bugs-squashed}
1. `Adaptors` 类中的 `re_first` 现在会返回所有内部 `Adaptor` 对象中第一个匹配的结果。之前的错误逻辑会返回 `re_first` 在所有 `Adaptor` 对象上的结果。
2. 如果要从选中的元素中返回文本内容，例如 CSS 的 `::text` 函数，无论使用 `.css` 还是 `.xpath` 等方法，`Adaptor` 对象现在都会返回 `TextHandlers`，而不是以前的字符串列表。因此可以写成 `page.css('something::text').re_first(r'regex_pattern').json()`，而不必使用 `page.css('something::text')[0].re_first(r'regex_pattern').json()`。
3. `Adaptor`/`Adaptors` 的 re/re_first 参数现在与 `TextHandler` 一致，提供 `clean_match` 和 `case_sensitive` 参数。
4. `auto_match` 参数现在在初始化 `Adaptor` 时默认开启，但如果要使用此功能，仍需在查询元素时启用它。（这不是错误，而是设计决定。）
5. 修正多处类型标注，让使用 Scrapling 编程时的自动补全更好用。

##### 使用体验改进 {#v0.2-quality-of-life-changes}
1. 将 `css_selector` 和 `xpath_selector` 方法更名为 `generate_css_selector` 和 `generate_xpath_selector`，让命名更清晰，也避免干扰编程时的自动补全。
2. 将大部分旧代码重新整理到 `core` 子包中，并调整其他设计，让代码更清晰，今后更易维护。
3. 重新整理测试目录，使结构更清晰，并为新功能添加测试。tox 环境现在还会在 GitHub 上缓存，以加快每次提交时的自动测试。

## [v0.1.2](https://github.com/D4Vinci/Scrapling/releases/tag/v0.1.2) - 2024-10-16 {#v0.1.2}

**更新日志**：

- 修复 `keep_comments` 参数未按预期工作的问题。
- 调整文本函数，在提取文本前自动移除元素中的 HTML 注释，避免 Lxml 的不同处理方式造成影响，例如：

    ```python
    >>> page = Adaptor('<span>CONDITION: <!-- -->Excellent</span>', keep_comments=True)
    >>> page.css('span::text')
    ['CONDITION: ', 'Excellent']
    ```

    上面的结果是之前由 Lxml 的默认行为产生的，现在会返回完整文本 'CONDITION: Excellent'。
    parsel\scrapy 也有这种行为，所以我想在这里处理它。

- 修复执行 `pip uninstall scrapling` 等命令时，库创建的 SQLite 数据库文件未被删除的问题。

## [v0.1.1](https://github.com/D4Vinci/Scrapling/releases/tag/v0.1.1) - 2024-10-14 {#v0.1.1}

小幅修复

## [v0.1](https://github.com/D4Vinci/Scrapling/releases/tag/v0.1) - 2024-10-13 {#v0.1}

**完整更新日志**：<https://github.com/D4Vinci/Scrapling/commits/v0.1>
