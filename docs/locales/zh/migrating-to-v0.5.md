---
title: "迁移到 v0.5"
description: "从 Scrapling v0.4.15 升级到 v0.5。更新浏览器导入、网络记录、MCP 工具、CLI 命令、解析器设置和爬虫行为。"
---

# 迁移到 v0.5 {#migrating-to-v05}

本指南介绍从 **v0.4.15 升级到 v0.5** 时需要检查的变化，包括已移除的 API、重命名的工具，以及可能改变抓取结果或已保存文件的修复。

## 迁移速查表 {#quick-migration-checklist}

| 如果使用了…… | 需要修改的内容 |
| --- | --- |
| `DynamicFetcher`、`DynamicSession` 或 `AsyncDynamicSession` | 使用对应的隐身类。 |
| `capture_xhr` 或 `response.captured_xhr` | 使用启用了 `record_requests=True` 的浏览器会话和 `session.network`。 |
| `keep_cdata` | 从解析器和 Fetcher 设置中移除。 |
| `scrapling extract stealthy-fetch` 或 Shell 中的 `stealthy_fetch()` | 改用 `fetch`。 |
| MCP 工具 | 更新工具名称、截图调用，以及会话创建响应的处理方式。 |
| 在 POST 请求或带查询参数的请求后使用 `response.follow()` | 需要时再次传入方法、查询参数和请求体。 |
| 已保存的抓取检查点或响应缓存 | 如果请求使用了已变化的指纹输入，请开始新的抓取。 |
| `robots_txt_obey=True` | 处理 robots.txt 获取失败的情况。现在这会阻止对该域名的抓取。 |

## 浏览器抓取 {#browser-fetching}

### 替换动态浏览器类 {#replace-the-dynamic-browser-classes}

直接使用 Playwright 的浏览器后端已被移除。所有浏览器抓取现在都使用基于 Patchright 的隐身后端。

| 已移除的 API | 替代 API |
| --- | --- |
| `scrapling.DynamicFetcher` | `scrapling.StealthyFetcher` |
| `scrapling.fetchers.DynamicFetcher` | `scrapling.fetchers.StealthyFetcher` |
| `scrapling.fetchers.chrome.PlayWrightFetcher` | `scrapling.fetchers.StealthyFetcher` |
| `scrapling.fetchers.DynamicSession` | `scrapling.fetchers.StealthySession` |
| `scrapling.fetchers.AsyncDynamicSession` | `scrapling.fetchers.AsyncStealthySession` |

`scrapling.fetchers.chrome` 模块和私有的 `_browsers._controllers` 模块已被移除。请使用上表中的公开导入路径。

**之前：**

```python
from scrapling.fetchers import DynamicFetcher

page = DynamicFetcher.fetch("https://example.com", headless=True)
```

**现在：**

```python
from scrapling.fetchers import StealthyFetcher

page = StealthyFetcher.fetch("https://example.com", headless=True)
```

对于会话，将 `DynamicSession` 替换为 `StealthySession`，或将 `AsyncDynamicSession` 替换为 `AsyncStealthySession`。在爬虫的 `configure_sessions()` 方法中也做相同修改。`fetch()` 和 `async with` 的用法仍然适用。

如果回调导入了浏览器类型或捕获浏览器错误，将 `playwright.sync_api` 改为 `patchright.sync_api`，或将 `playwright.async_api` 改为 `patchright.async_api`。这包括 `Page`、`Locator`、`Error` 和 `TimeoutError`。

Patchright 默认在隔离的上下文中执行 JavaScript。如果回调需要读取页面自身的 JavaScript 变量，请使用 `page.evaluate(..., isolated_context=False)`。

除了导入名称，浏览器行为也会改变。请检查浏览器启动参数和指纹设置。处理 Cloudflare 验证仍需设置 `solve_cloudflare=True`，默认不会启用。此外，`extra_flags` 现在会追加到内置隐身启动参数中，而不是替换它们。

当前选项见[浏览器抓取](fetching/stealthy.md)。

### 用会话网络历史替代 XHR 捕获 {#replace-xhr-capture-with-session-network-history}

`capture_xhr` 参数和 `Response.captured_xhr` 属性已被移除。即使参数值为 `None`，也需要移除该参数。单次抓取的响应不再附带 XHR 列表。

调用 `ResponseFactory.from_playwright_response()` 或 `ResponseFactory.from_async_playwright_response()` 的自定义集成也必须移除 `xhr_captured`。请按名称传入 `collect_history`，避免位置参数顺序变化带来的问题。

**之前：**

```python
from scrapling.fetchers import StealthyFetcher

page = StealthyFetcher.fetch("https://example.com", capture_xhr="/api/")
for response in page.captured_xhr:
    print(response.url, response.body)
```

**现在：**

```python
from scrapling.fetchers import StealthySession

with StealthySession(record_requests=True) as session:
    page = session.fetch("https://example.com", network_idle=True)
    for response in session.network.search(url_pattern=r"/api/", limit=None):
        print(response.url, response.body)
```

异步代码使用 `AsyncStealthySession` 和 `await session.fetch(...)`。读取 `session.network` 不需要 `await`。

需要注意以下区别：

- 在创建会话时设置 `record_requests=True`。这是会话设置，不能按单次抓取设置。
- 历史记录属于**整个会话**，涵盖各个标签页、页面加载和操作。如果需要缩小范围，请使用 `after_id`、筛选条件或 `session.network.clear()`。
- 搜索历史记录时，将原来的 `capture_xhr` 正则表达式移到 `url_pattern`。
- `search()` 返回已保存的 `Response` 对象。直接读取 `.url`、`.status`、`.headers`、`.body` 或 `.json()`。记录 ID、资源类型和已发送的请求体分别位于 `response.meta["network_id"]`、`response.meta["resource_type"]` 和 `response.meta["request_body"]`。
- Python 历史记录默认包含所有资源类型。使用 `resource_type="xhr"` 或 `resource_type="fetch"` 选择其中一种，或使用 `include_static=False` 获取 XHR/fetch 请求和 HTTP 错误。
- `search()` 默认最多返回 100 条匹配记录。传入 `limit=None` 可获取所有保留的匹配记录。会话默认最多保留 1,000 个请求；可通过 `max_recorded_requests` 修改。
- 只保存已完成的请求。响应体捕获仅支持指定的文本内容类型，每个响应最多 1 MiB，保留的响应体数据总量最多 20 MiB。达到限制时，较旧的记录可能被移除。查看 `response.meta.get("body_note")` 可了解跳过响应体的原因。
- 读取历史记录或关闭会话不会等待尚未完成的捕获。请先等待所需数据就绪，再读取数据。会话关闭后，已保存的 Python 历史记录仍可读取。

筛选条件和限制见[网络历史](fetching/stealthy.md#network-history)。

## 解析器设置 {#parser-settings}

### 移除 `keep_cdata` {#remove-keep_cdata}

`keep_cdata` 已从 `Selector`、Fetcher 配置和 `display_config()` 返回的设置中移除。请从直接调用解析器的代码、`Fetcher.configure(...)`，以及传给 Fetcher 或集成的 `selector_config` 字典中移除它。

**之前：**

```python
from scrapling import Selector

page = Selector("<p>Hello</p>", keep_cdata=True)
```

**现在：**

```python
from scrapling import Selector

page = Selector("<p>Hello</p>")
```

没有替代设置。该设置原本不会影响 HTML 解析器的输出。如果之前按位置传入解析器选项，请移除旧的 `keep_cdata` 参数，并按名称传入 `adaptive` 和存储选项。

## 命令行和交互式 Shell {#command-line-and-interactive-shell}

### 使用 `fetch` 发送浏览器请求 {#use-fetch-for-browser-requests}

CLI 现在只有一个浏览器命令：`scrapling extract fetch`。它使用 `StealthyFetcher`。

**之前：**

```bash
scrapling extract stealthy-fetch "https://example.com" page.md
```

**现在：**

```bash
scrapling extract fetch "https://example.com" page.md
```

如果已经使用 `scrapling extract fetch`，命令名称不变，但其后端会从 `DynamicFetcher` 改为 `StealthyFetcher`。`--solve-cloudflare` 等选项现在属于 `fetch`。

在 `scrapling shell` 中，将 `stealthy_fetch(...)` 替换为 `fetch(...)`。现有的 `fetch(...)` 快捷调用现在会调用 `StealthyFetcher.fetch`。动态类不再加入 Shell 的命名空间。

### 按 UTF-8 读取 Markdown 和文本文件 {#read-markdown-and-text-files-as-utf-8}

提取命令和 `Convertor.write_content_to_file()` 现在会以 **UTF-8** 写入 `.md` 和 `.txt` 文件，不受源页面字符集的影响。如果代码使用页面原始编码读取这些文件，请更新它。`.html` 输出仍使用 `page.encoding`。

从多个选中元素生成的 Markdown 现在会在元素之间加入空行。这适用于 `Response.markdown()` 和 Markdown 文件输出。请更新依赖直接拼接文本的精确输出比较或已保存的哈希值。

## MCP 服务器 {#mcp-server}

请更新已保存的提示词、工具允许列表、封装代码和 MCP 客户端的工具定义。更新服务器后，请重启或重新连接 MCP 客户端，让它读取当前工具列表。

### 更新工具名称和批量调用 {#update-tool-names-and-bulk-calls}

| v0.4.15 工具 | v0.5 替代方式 |
| --- | --- |
| `fetch`, `stealthy_fetch` | `browser_fetch_once` |
| `open_session` | `browser_open` |
| `session_fetch` | `browser_fetch` |
| `screenshot` | `browser_screenshot` |
| `bulk_fetch`, `bulk_stealthy_fetch` | 每个 URL 调用一次 `browser_fetch_once`，或通过已打开的会话重复调用 `browser_fetch` |
| `bulk_get` | 每个 URL 调用一次 `make_request` 或 `session_make_request` |

所有批量工具已被移除。单 URL 抓取工具返回一个包含 `status`、`content` 和 `url` 的 `ResponseModel`，不再返回响应列表。`content` 本身仍然是字符串列表。

所有 MCP 浏览器工具现在都使用隐身后端。请从 `browser_open` 调用中移除 `session_type`；不再提供动态浏览器选项。其结果包含 `session_type="stealthy"`。HTTP 会话仍使用 `open_request_session`，并返回 `session_type="static"`。

Python 集成还必须停止导入已被移除的 `BrowserSessionType`。`SessionType` 现在只接受 `"stealthy"` 和 `"static"`。

同一浏览器会话中的调用必须按顺序执行，因为它们共用一个页面。完成后使用 `close_session` 关闭会话。

### 通过 `list_sessions` 读取设置 {#read-settings-through-list_sessions}

`browser_open` 和 `open_request_session` 现在只返回：

```json
{
  "session_id": "my-session",
  "session_type": "stealthy"
}
```

创建结果不再包含 `created_at`、`is_alive`、`settings` 或 `message`。调用 `list_sessions` 可获取前三个字段。确认信息 `message` 已被移除。如果代码假设 `SessionCreatedModel` 具有 `SessionInfo` 的所有字段，也需要修改。

### 截图前先获取页面 {#fetch-before-taking-a-screenshot}

`browser_screenshot` 会截取**当前页面，不会重新加载页面**。它不再接受 URL，也不再接受旧的导航和等待选项：`wait`、`wait_selector`、`wait_selector_state` 和 `network_idle`。

请按以下顺序操作：

1. 调用 `browser_open`。
2. 调用 `browser_fetch`，传入 URL 和所需的页面加载选项。
3. 如有需要，调用 `browser_actions` 与页面交互或等待内容。
4. 调用 `browser_screenshot`，传入会话 ID。
5. 完成后调用 `close_session`。

例如，整页截图的参数如下：

```json
{
  "session_id": "my-session",
  "full_page": true
}
```

该工具的 `timeout` 现在限制的是截图操作的时长。该工具不会加载页面。要截取某个元素，请使用 `selector` 或 `ref`，且不要设置 `full_page=true`。

截图仍返回图像和文本内容块，文本块中包含当前页面的 URL。它们不会返回抓取使用的 `ResponseModel`。

完整的输入和输出结构见 [MCP 指南](ai/mcp-server.md)和 [API 参考](api-reference/mcp-server.md)。

## 爬虫和 HTTP 请求 {#spiders-and-http-requests}

### 跟随链接时重新传入请求数据 {#pass-request-data-again-when-following-a-link}

`response.follow()` 不再从上一个请求复制 `method`、`params`、`data`、`json`、`files` 或 `multipart`。它还会从 `headers` 和 `extra_headers` 中移除继承的 `Content-Length` 请求头。

跟随链接现在默认发起普通 GET 请求，除非显式传入请求数据。会话、代理和回调等其他共享设置仍遵循现有的继承规则。

如果旧代码依赖继承的 POST 数据，请将：

```python
yield response.follow("/next")
```

改为：

```python
yield response.follow("/next", method="POST", json={"page": 2})
```

如果下一个请求需要 `params`，也要显式传入。让 HTTP 客户端计算新的 `Content-Length`。

### 检查请求指纹和已保存的抓取状态 {#check-request-fingerprints-and-saved-crawl-state}

请求指纹是用于识别重复请求和查找缓存响应的键。现在有三种输入情况的处理方式发生变化：

- 构建键之前，`params` 会合并到 URL 中。默认情况下，同一 URL 使用不同查询参数的请求不再被视为重复请求。
- `{}`、`[]`、`false`、`0` 和 `""` 等 JSON 请求体会保留在键中。它们不再与没有请求体的情况共用同一个键。`None` 仍表示没有 JSON 请求体。
- 当 `fp_include_headers=True` 时，仅改变请求头的插入顺序不会再改变键。

如果抓取使用了这些输入，请在升级前完成抓取，或使用新的检查点和响应缓存目录开始新的抓取。旧的已保存键可能与新键不同。这是请求标识方式的变化，不是检查点文件格式的变化。

开发模式现在只会在检查响应是否被封锁之后，将响应写入缓存。封锁页面不会作为成功结果存入缓存。现有缓存文件不会自动清理；如果之前缓存过验证页面，请清除旧条目。

失败的抓取现在会保留检查点文件。如果清理代码假设这些文件会在出错后消失，请检查该代码。参见[暂停和恢复](spiders/advanced.md#pause-resume)及[开发模式](spiders/advanced.md#development-mode)。

### 检查 robots.txt 获取失败的情况 {#check-robotstxt-failures}

设置 `robots_txt_obey=True` 后，如果获取 robots.txt 时出现异常，或响应状态不是 HTTP 200 或 4xx，现在会阻止对该域名的请求。此前，这些失败情况会允许继续抓取。HTTP 200 仍提供规则，HTTP 4xx 仍允许访问。

该结果会在整个抓取期间缓存。请修复 robots.txt 的访问问题，然后开始新的抓取；同一次抓取中的后续请求不会重试失败的查询。默认值 `robots_txt_obey=False` 不变。

### 检查链接限制和站点地图回调 {#check-link-restrictions-and-sitemap-callbacks}

- `LinkExtractor` 的限制条件没有匹配项时，现在不会返回任何链接。它不再退回到整个页面。如果抓取找到的链接变少，请修正 `restrict_css` 或 `restrict_xpath` 表达式。
- 限制条件现在可以选中链接元素本身，而不只是父元素。这可能会增加之前遗漏的链接。请检查预期的 URL 集合。
- 当没有规则，或匹配规则的 `callback=None` 时，`SitemapSpider` 现在会把页面 URL 交给 `parse()`。它不再将这些 HTML 页面送回站点地图解析器。请为这些情况实现 `parse()`，并移除针对旧分发方式的变通代码。
- robots.txt 和 CSV 数据源开头的 Unicode 字节顺序标记会被移除。robots 的第一条指令现在会生效，CSV 的第一个列名也不再以 `\ufeff` 开头。如果设置了自定义 `headers`，则会改为从第一个字段值中移除该标记。请更新用于处理该隐藏前缀的代码。站点地图中的 XML 注释和处理指令也会被跳过，不再导致解析失败。

### 检查表单数据、请求头和 CLI JSON {#check-form-data-headers-and-cli-json}

字典形式的表单数据现在会将列表和元组值展开为重复的键。例如，`data={"tag": ["a", "b"]}` 会发送 `tag=a&tag=b`。空列表不会为该键发送任何条目。如果未提供 Content-Type，会添加默认值 `Content-Type: application/x-www-form-urlencoded`。

如果需要其他传输格式，请显式传入编码后的字符串或字节。`json`、原始 `content` 和 multipart 上传仍使用各自的请求体处理方式。表单数据或查询参数中的 `None` 值**不会被移除**；它们仍是字符串 `None`。

单个请求的 HTTP 请求头现在会覆盖会话请求头，不区分大小写。名为 `authorization` 的请求头会替换会话中的 `Authorization`，而不是同时发送两者。请移除用于处理重复请求头名称的代码。

CLI JSON 值 `{}`、`[]`、`false`、`0` 和 `""` 现在会被发送，不再被静默丢弃。此外，`curl2fetcher()` 现在会应用 curl 的 `-A` 用户代理，并将 `-x` 代理正确地作为 URL 字符串传入。显式指定的 curl 请求头 `-H 'User-Agent: ...'` 仍优先于 `-A`。

## 其他需要检查的输出变化 {#other-output-changes-to-check}

这些修复没有移除 API，但可能改变已保存的结果和精确输出测试：

- 生成的 CSS 和 XPath 选择器现在会在需要时包含 `:nth-of-type(1)` 或 `[1]`，以识别多个同标签兄弟元素中的第一个。请更新预期的选择器字符串，不要移除新的位置标记。
- AI 内容清理现在会保留具有 `opacity:0.95` 等值的可见元素，识别更多种隐藏内联样式并移除相应元素，同时移除 `<slot hidden>` 元素及所有匹配的干扰标签，包括嵌套的标签。请重新检查 Markdown、文本和净化后 HTML 的精确输出。
- 浏览器响应转换现在能读取包含不同大小写、空格或带引号值的 charset 声明，例如 `text/plain; CHARSET = "iso-8859-15"`。带有这些响应头的非 HTML 响应现在会使用声明的编码，不再回退到 UTF-8。请重新检查从这些响应中解码得到的文本。

## 验证升级结果 {#verify-your-upgrade}

在运行完整任务之前，先进行小规模抓取。检查提取的数据、跟随的 URL、发送的请求体、已保存文件的编码，以及所依赖的缓存或检查点行为。对于 MCP 集成，请对照当前结构检查工具输入和返回的数据。

更早版本的变化见[更新日志](changelog.md)。
