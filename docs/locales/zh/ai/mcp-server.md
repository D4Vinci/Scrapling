---
title: "Scrapling MCP 服务器：设置与抓取流程"
description: "将 AI 客户端连接到 Scrapling，进行 HTTP 或浏览器抓取。使用会话、保存的登录状态、浏览器操作、定向提取和 API 历史记录。"
---

# Scrapling MCP 服务器指南 {#scrapling-mcp-server-guide}

<iframe width="560" height="315" src="https://www.youtube.com/embed/NHwWEiTOoPQ" title="YouTube 视频播放器" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>

**Scrapling MCP 服务器**将 Scrapling 的网页抓取能力直接提供给 AI 聊天机器人或智能体。通过 Claude 或其他支持 MCP 的界面，可以在对话中抓取网站、提取数据并绕过反爬保护。

## 功能 {#features}

Scrapling MCP 服务器提供十六个工具，用于网页抓取和浏览器交互。单次调用工具获取一个 URL 后，会关闭自己创建的浏览器或客户端。会话工具则在调用之间保留 Cookie 和设置，让 AI 可以继续操作同一个标签页，并查看网络历史记录。

### 单次调用工具 {#one-shot-tools}

#### 🚀 基础 HTTP 抓取 {#basic-http-scraping}

- **`make_request`**：快速发送任意方法的 HTTP 请求（GET、POST、PUT、DELETE），并模拟浏览器指纹。它会生成与 TLS 版本匹配的真实浏览器请求头，还支持 HTTP/3 等功能。

#### 🔒 隐身浏览器抓取 {#stealth-browser-scraping}

- **`browser_fetch_once`**：使用隐身浏览器运行 JavaScript 并抓取动态页面。支持模拟指纹、绕过 Cloudflare Turnstile 和 Interstitial，以及控制浏览器和请求。

### 会话工具 {#session-tools}

#### 🔌 会话管理 {#session-management}

- **`browser_open`**：创建持久的隐身浏览器会话，在多次 `browser_fetch` 调用之间保持打开，避免每次重新启动浏览器。它保留浏览器级配置，只返回 `session_id` 和 `session_type`。使用 `list_sessions` 查看实际生效的 `settings`，CDP 会话的该值为空。
- **`open_request_session`**：创建不使用浏览器的持久 HTTP 会话，配合 `session_make_request` 使用。在请求之间保留 Cookie、连接和浏览器指纹（`impersonate`）。它只返回 `session_id` 和 `session_type`，类型为 `static`。使用 `list_sessions` 查看实际生效的 `settings`。
- **`close_session`**：关闭持久的浏览器或 HTTP 会话，并释放资源。
- **`list_sessions`**：列出所有活动会话及其详细信息和 `settings`。

#### 浏览器状态 {#browser-state}

- **`browser_save_state`**：将 Cookie、Local Storage 和 IndexedDB 保存为兼容 Playwright 的 JSON 文件，让登录状态在浏览器会话结束后仍可复用。保存时会覆盖已有文件。
- **`browser_load_state`**：将保存的文件恢复到已打开的浏览器会话中，也可以在首次加载页面前使用。它会替换当前存储的状态，但不会关闭已有标签页或切换页面。要使用恢复的登录状态，需要获取或重新加载页面。

状态文件存放在运行 MCP 服务器的机器上。它们不包含 `sessionStorage`、打开的标签页或浏览器设置。

#### 🎯 通过会话获取页面 {#fetching-through-a-session}

- **`browser_fetch`**：在已打开的隐身浏览器会话中运行 JavaScript 并抓取一个 URL，支持模拟指纹以及绕过 Cloudflare Turnstile 和 Interstitial。还可以生成包含元素引用、位置和大小的结构化页面快照，帮助 AI 识别控件并规划鼠标操作。
- **`session_make_request`**：快速发送任意方法的 HTTP 请求（GET、POST、PUT、DELETE），支持模拟浏览器指纹、匹配的浏览器请求头和 HTTP/3。通过 `open_request_session` 打开的会话，复用 Cookie、连接和浏览器指纹。

#### 📸 截图 {#screenshots}

- **`browser_screenshot`**：无需重新加载，将当前页面或指定元素截图为 PNG 或 JPEG。可以检查已填写的字段、打开的菜单、图表或结果卡片。只截取一个元素可以减少无关内容。支持可见区域、整页或单个元素，并可调整 JPEG 质量。截图以图像内容块返回，模型可以直接查看。

#### 当前页面内容 {#current-page-content}

- **`browser_extract`**：无需重新加载，将当前页面或一个元素读取为 AI 快照、HTML、Markdown 或文本。可在填写表单或加载更多内容后提取结果。快照包含元素的角色、名称、引用、位置和大小，方便后续操作。正则搜索会返回匹配的快照行，以及附近上下文和父节点。

#### 浏览器操作 {#browser-actions}

- **`browser_actions`**：在一次调用中串联鼠标操作、字段填写、快捷键、对话框响应和等待。可以接受或关闭浏览器提示和确认框，也可以在输入对话框中填写文本。例如，填写搜索框、提交、等待结果，然后打开一个结果。AI 可以合并已知步骤；需要检查页面变化时，再单独获取快照。这样就不必在每一步之后都把控制权交回智能体，再由它发起下一次调用，有助于处理只短暂显示的菜单，以及需要快速衔接操作的其他控件。

    悬停以显示菜单和提示，点击按钮和链接，或将鼠标移到嵌套区域内进行纵向或横向滚动。移动和点击支持选择器、快照引用或坐标。以元素为目标时，会自动等待并将其滚动到可见区域。支持分多步移动到坐标、左键、右键和中键点击，以及双击。

    使用选择器或快照引用定位页面中的字段。可以填写文本、勾选或取消勾选复选框、选择单选按钮，以及按可见标签选择原生下拉列表中的一个或多个选项。文本可以替换现有内容、清空内容，或从当前光标位置继续输入。快捷键可以选择和删除文本、移动焦点、提交表单或关闭菜单。慢速模式逐字输入，并在字符之间及各个操作之间加入随机暂停。

    在下一步操作前，可以等待结果出现、加载遮罩消失或页面加载事件发生。也支持固定暂停，以及等待网络活动平息。

#### JavaScript {#javascript}

- **`browser_evaluate`**：在当前页面运行 JavaScript，进行自定义数据提取、计算或页面特有的操作。AI 可以汇总多个元素的数据、读取应用状态或更新页面内容。支持异步脚本，并以 JSON 返回结果。

#### 网络历史记录 {#network-history}

- **`browser_network_requests`**：查找跨标签页、页面加载和浏览器操作的已完成请求。可以找出页面数据背后的 API 调用、检查 HTTP 错误并查看已保存的重定向。默认隐藏静态资源，以缩小结果。请求详情以 JSON 返回，较长的历史记录支持分页。
- **`browser_network_request`**：以结构化 JSON 查看某条已记录请求的摘要、HTTP 头信息、发送数据或文本响应体。完整返回选中的部分，无需加载页面或重发请求。已保存的响应在页面变化后仍然可用。大小限制会控制历史记录的规模；对于非文本、过大或无法读取的响应体，会用说明指出原因。请在关闭 MCP 会话前读取需要的详情。

只有受支持的文本 `Content-Type` 才会读取并保存响应体，例如 HTML、JSON、XML 或 JavaScript。二进制、缺失或未知的内容类型只保留请求元数据和 HTTP 头信息，不读取或保存响应体。浏览器仍会正常加载资源。

只保存已完成的请求，包括 HTTP 4xx 和 5xx 响应。失败和未完成的请求会被忽略。条目在捕获完成后才会出现，读取历史记录或关闭会话不会等待捕获。切换页面或关闭时仍在捕获的内容可能被忽略。保存的字节来自浏览器，可能与服务器原始字节不同。若为有效 UTF-8，文本按 Playwright 的 UTF-8 方式解码，否则使用声明的字符集。

### Shadow DOM {#shadow-dom}

在 `browser_fetch_once` 或每次 `browser_fetch` 调用中设置 `pierce_shadow=true`，即可包含开放 Shadow DOM 的内容。默认值为 `false`。选择器示例和限制请参阅 [Shadow DOM](../fetching/stealthy.md#shadow-dom)。

浏览器选择器也可以定位封闭 Shadow DOM 内的元素并与之交互。

### 核心能力 {#key-capabilities}

- **内容提取**：将网页或元素转换为 Markdown、HTML，或提取干净的文本。
- **CSS 选择器**：先用 Scrapling 精确选择元素，再将内容交给 AI。
- **绕过反爬保护**：处理 Cloudflare Turnstile、Interstitial 和其他保护。
- **代理支持**：使用代理隐藏来源或选择请求所在地区。
- **模拟浏览器**：通过 TLS 指纹、匹配版本的真实浏览器请求头等方式模拟真实浏览器。
- **持久会话**：在多次请求中复用浏览器会话，提高性能。
- **广告拦截**：所有浏览器工具都会自动阻止发往约 3,500 个已知广告和跟踪域名的请求，节省 token 并加快加载。
- **提示词注入防护**：自动清理可能用于攻击的隐藏内容，包括通过内联样式隐藏的元素、aria-hidden、隐藏的 slot、零宽字符、HTML 注释和 template 标签。

## 安装 {#installation}

安装带 MCP 支持的 Scrapling，并确认浏览器依赖也已安装。

```bash
# Install Scrapling with MCP server dependencies
pip install "scrapling[ai]"

# Install browser dependencies
scrapling install
```

也可以直接使用 Docker Registry 中的镜像：
```bash
docker pull pyd4vinci/scrapling
```
或者从 GitHub Registry 下载：
```bash
docker pull ghcr.io/d4vinci/scrapling:latest
```

## 设置 MCP 服务器 {#setting-up-the-mcp-server}

下面介绍如何把 Scrapling MCP 服务器添加到 [Claude Desktop](https://claude.ai/download) 和 [Claude Code](https://www.anthropic.com/claude-code)。其他支持 MCP 的聊天机器人也可以参考相同步骤：

!!! note "注意"
    下面使用的 `scrapling-mcp` 命令在 v0.4.13 中加入，直接对应 `scrapling mcp`。它让只接受单个命令的 MCP 注册目录和客户端更容易接入 Scrapling。旧版本请使用 `scrapling` 命令，并将 `mcp` 作为第一个参数。

### Claude Desktop {#claude-desktop}

1. 打开 Claude Desktop。
2. 点击左上角菜单（☰），依次选择 Settings → Developer → Edit Config。
3. 添加 Scrapling MCP 服务器配置：
```json
"ScraplingServer": {
  "command": "scrapling-mcp"
}
```
如果这是第一个 MCP 服务器，将文件内容设为：
```json
{
  "mcpServers": {
    "ScraplingServer": {
      "command": "scrapling-mcp"
    }
  }
}
```
根据[官方文章](https://modelcontextprotocol.io/quickstart/user)，如果没有配置文件，这一步会创建它；如果已有配置文件，就会打开现有文件。文件位置如下：

1. **MacOS**：`~/Library/Application Support/Claude/claude_desktop_config.json`
2. **Windows**：`%APPDATA%\Claude\claude_desktop_config.json`

为确保正常运行，请使用 `scrapling-mcp` 可执行文件的完整路径。可以用以下命令查找：

1. **MacOS**：`which scrapling-mcp`
2. **Windows**：`where scrapling-mcp`

在我的 Mac 上，结果是 `/Users/<MyUsername>/.venv/bin/scrapling-mcp`，因此最终配置如下：
```json
{
  "mcpServers": {
    "ScraplingServer": {
      "command": "/Users/<MyUsername>/.venv/bin/scrapling-mcp"
    }
  }
}
```
#### Docker {#docker}

如果使用 Docker 镜像，配置类似这样：
```json
{
  "mcpServers": {
    "ScraplingServer": {
      "command": "docker",
      "args": [
        "run", "-i", "--rm", "pyd4vinci/scrapling", "mcp"
      ]
    }
  }
}
```

[Cursor](https://cursor.com/docs/context/mcp)、[WindSurf](https://windsurf.com/university/tutorials/configuring-first-mcp-server) 等客户端也适用相同的配置思路。

### Claude Code {#claude-code}

[Claude Code](https://www.anthropic.com/claude-code) 的配置更简单：

```bash
claude mcp add ScraplingServer "/Users/<MyUsername>/.venv/bin/scrapling-mcp"
```
查找 Scrapling 可执行文件路径：

1. **MacOS**：`which scrapling-mcp`
2. **Windows**：`where scrapling-mcp`

更多细节请参阅 Anthropic 关于[向 Claude Code 添加 MCP 服务器](https://docs.anthropic.com/en/docs/claude-code/mcp#option-1%3A-add-a-local-stdio-server)的文章。

添加服务器后，完全退出并重新启动应用。在 Claude Desktop 中，应能看到输入框右下角的 MCP 服务器图标（🔧），或输入框 `Search and tools` 菜单中的 `ScraplingServer`。

### 自定义浏览器可执行文件 {#custom-browser-executable}

`browser_fetch_once` 和 `browser_open` 可以使用兼容 Chromium 的自定义浏览器可执行文件，替代自带的 Chromium。这适用于定制浏览器版本或轻量浏览器引擎。

要为整个 MCP 服务器统一设置，在启动时传入可执行文件路径：

```bash
scrapling-mcp --executable-path "/path/to/chromium"
```

在 Claude Desktop 配置中，将该选项加入服务器参数：

```json
{
  "mcpServers": {
    "ScraplingServer": {
      "command": "/Users/<MyUsername>/.venv/bin/scrapling-mcp",
      "args": [
        "--executable-path",
        "/path/to/chromium"
      ]
    }
  }
}
```

也可以在启动前设置环境变量 `SCRAPLING_EXECUTABLE_PATH`。AI 仍可在单次 `browser_fetch_once` 调用中，或使用 `browser_open` 打开会话时，选择另一个浏览器可执行文件。

### 连接远程浏览器 {#connecting-to-remote-browsers}

`browser_open` 不一定要启动本地浏览器。传入 CDP URL 后，它会通过 [Chrome DevTools Protocol](https://chromedevtools.github.io/devtools-protocol/) 连接到已运行的浏览器。浏览器可以在同一台机器、其他主机或托管浏览器服务中运行：
```
Open a stealthy browser session on wss://cdp.provider.example/session/abc123, then use it to scrape the product details from https://shop.example.com. Close the session when you're done.
```
返回的 `session_id` 可以照常用于 `browser_fetch`、`browser_extract`、`browser_actions`、`browser_evaluate`、`browser_screenshot`、`browser_network_requests`、`browser_network_request`、`browser_save_state` 和 `browser_load_state`。

URL 可以是浏览器服务提供的 WebSocket 地址（`ws://`/`wss://`），也可以是自行启动并开启远程调试端口的浏览器 HTTP 地址：
```commandline
chrome --remote-debugging-port=9222
```
可以通过 `cdp_url="http://localhost:9222"` 连接它；如果浏览器运行在另一台机器上，则使用那台机器的地址。

!!! note "说明"

    * 浏览器已经在运行，因此 CDP 会话会忽略仅在启动浏览器时生效的选项：`headless`、`real_chrome` 和 `executable_path`（包括上面提到的服务器默认值）。<br/>
    * 其他选项仍然生效（`locale`、`useragent`、`proxy`、`cookies`、`timezone_id` 等），因为每个会话都会在远程浏览器中创建自己的浏览器上下文。

### Streamable HTTP {#streamable-http}
从 0.3.6 版起，MCP 服务器可以使用 Streamable HTTP 传输方式，替代传统的 stdio 传输方式。

原来使用的是以下 stdio 命令：
```bash
scrapling-mcp
```
改用以下命令即可启用 Streamable HTTP：
```bash
scrapling-mcp --http
```
服务器默认监听地址为 127.0.0.1，端口为 8000，两者都可以按下面的方式设置：
```bash
scrapling-mcp --http --host '0.0.0.0' --port 8000
```
默认只接受来自同一台机器的连接。要让其他机器通过网络访问服务器，请传入 `--host '0.0.0.0'`。网络访问和下面介绍的身份验证是两个独立的设置。

在 Docker 中运行 Streamable HTTP 时，必须手动绑定到 0.0.0.0 并设置 token，否则映射的端口无法连接到服务器，因为容器中的 127.0.0.1 只能在容器内部访问：
```bash
docker run -p 8000:8000 -e SCRAPLING_MCP_AUTH_TOKEN="<your-token>" pyd4vinci/scrapling mcp --http --host '0.0.0.0'
```

### 身份验证 {#authentication}

stdio 只能由启动它的程序访问。切换到 Streamable HTTP 后，任何能访问该端口的人都可以调用全部工具，包括从服务器所在的机器获取任意 URL。因此，Streamable HTTP 要求身份验证；只传入 `--http` 时，服务器会拒绝启动，并要求提供 token：
```bash
scrapling-mcp --http --auth-token "$(openssl rand -hex 32)"
```
客户端必须在 `Authorization` 请求头中发送该 token。没有 token 的请求会收到 `401` 响应：
```json
{
  "mcpServers": {
    "ScraplingServer": {
      "url": "https://your-server.example.com/mcp",
      "headers": {
        "Authorization": "Bearer <your-token>"
      }
    }
  }
}
```
通过命令行传入 token 会使它留在 shell 历史记录和进程列表中，因此建议使用 `SCRAPLING_MCP_AUTH_TOKEN` 环境变量：
```bash
export SCRAPLING_MCP_AUTH_TOKEN="<your-token>"
scrapling-mcp --http
```
如果确实需要关闭身份验证，例如在默认地址 127.0.0.1 上进行本地测试，必须明确传入 `--no-auth`：
```bash
scrapling-mcp --http --no-auth
```
同时使用 `--no-auth` 和 `--host '0.0.0.0'`，会让任何能访问该端口的人调用全部工具，因此不要在不受信任的网络中这样设置。

服务器监听公网地址时，还应指定允许的主机名，以启用 DNS 重绑定攻击防护。这类攻击会让浏览器访问的网站尝试连接到本地服务器。可以多次传入该选项：
```bash
scrapling-mcp --http --allowed-host 'your-server.example.com:8000'
```

!!! note "说明"

    * 身份验证仅适用于 Streamable HTTP。stdio 会忽略它，并在日志中记录警告。<br/>
    * 普通 HTTP 会以明文发送 token，因此将服务器开放到互联网前，应在它前面部署负责 TLS 的反向代理。<br/>
    * 这是一个共享密钥，不是每个客户端各自的凭据。所有客户端使用同一个 token，更换 token 后需要重启服务器。<br/>
    * 使用 `--http --no-auth` 启动时，服务器仍会记录警告，提醒身份验证已关闭。<br/>
    * 同时传入 `--auth-token` 和 `--no-auth` 时，服务器会保留 token 并继续验证身份，不会悄悄关闭身份验证。

## 示例 {#examples}

下面介绍一些测试 MCP 服务器时使用的提示词。也许大家能想出更有创意的用法，写出更好的提示词 :)

我们会从简单的提示词逐步讲到更复杂的提示词。示例使用 Claude Desktop，但相同思路也适用于其他客户端。

1. **基本网页抓取**

    将网页的主要内容提取为 Markdown：
    
    ```
    Scrape the main content from https://example.com and convert it to markdown format.
    ```
    
    Claude 可以使用 `make_request` 获取页面，并返回干净、易读的内容。HTTP 请求默认最多尝试三次，每次尝试之间等待一秒。如果页面需要 JavaScript 或阻止 HTTP 请求，AI 可以改用 `browser_fetch_once`。这两个工具都会在调用结束后关闭各自的资源。
    
    同一个提示词可以写得更明确：
    ```
    Use regular requests to scrape the main content from https://example.com and convert it to markdown format.
    ```
    这样可以告诉 Claude 要使用哪个工具，无需让它猜。有时它会自行使用普通请求，有时又会在没有明显理由的情况下认为浏览器更适合这个网站。通常，明确指定工具可以节省时间和费用，也能让结果更一致。

2. **定向提取数据**

    使用 CSS 选择器提取指定元素：
    
    ```
    Get all product titles from https://shop.example.com using the CSS selector '.product-title'. If the request fails, retry up to 5 times every 10 seconds.
    ```
    
    服务器只会提取与选择器匹配的元素，并以结构化列表返回。这里让工具最多尝试 5 次，以应对网站连接问题，不过默认设置已适合大多数情况。

3. **收集电商数据**

    再看一个稍复杂的提示词：
    ```
    Open a stealthy browser session and visit these e-commerce URLs one at a time:
    - https://shop1.com/product-a
    - https://shop2.com/product-b  
    - https://shop3.com/product-c
    
    Get the product names, prices, and descriptions from each page. Close the session when done.
    ```
    
    Claude 可以复用一个浏览器会话，按顺序为每个 URL 调用 `browser_fetch`，再分析提取的数据。

4. **更复杂的工作流程**

    假设要获取 PlayStation 商店第一页上的所有动作游戏，可以使用以下提示词：
    ```
    Extract the URLs of all games on this page, then visit each game in order and return a list of all action games: https://store.playstation.com/en-us/pages/browse
    ```
    如果普通请求就能获取数据，可以让 AI 复用 HTTP 会话，避免启动浏览器：
    ```
    Open an HTTP session, extract the URLs of all games on this page, then fetch each game in order and return a list of all action games. Close the session when done: https://store.playstation.com/en-us/pages/browse
    ```
    如果会编写 CSS 选择器，还可以在 AI 读取内容前缩小提取范围：
    ```
    Use an HTTP session to extract the URLs of all games on the page below, then fetch each game in order and return a list of all action games.
    The selector for games in the first page is `[href*="/concept/"]` and the selector for the genre in each game page is `[data-qa="gameInfo#releaseInformation#genre-value"]`.
    Close the session when done.

    URL: https://store.playstation.com/en-us/pages/browse
    ```

5. **从有 Cloudflare 保护的网站获取数据**

    如果认为目标网站有 Cloudflare 保护，请直接告诉 Claude，不要让它自行发现。
    ```
    What's the price of this product? Be cautious, as it utilizes Cloudflare's Turnstile protection. Make the browser visible while you work.

    https://ao.com/product/oo101uk-ninja-woodfire-outdoor-pizza-oven-brown-99357-685.aspx
    ```

6. **较长的工作流程**

    例如，可以使用这样的提示词：
    ```
    Extract all product URLs for the following category, then return the prices and details for the first 3 products.
    
    https://www.arnotts.ie/furniture/bedroom/bed-frames/
    ```
    但下面的提示词更好：
    ```
    Go to the following category URL and extract all product URLs using the CSS selector "a". Then, reuse the session to fetch the first 3 product pages in order and extract each product’s price and details. Close the session when done.
    
    Keep the output in markdown format to reduce irrelevant content.
    
    Category URL:
    https://www.arnotts.ie/furniture/bedroom/bed-frames/
    ```

7. **使用持久会话**

    抓取同一个网站的多个页面时，使用持久浏览器会话可以避免为每个请求启动新浏览器的开销：
    ```
    Open a stealthy browser session, then use it to scrape the main details from the first 5 product pages on https://shop.example.com. Close the session when you're done.
    ```
    Claude 会用 `browser_open` 创建持久浏览器，通过该会话为每个商品页面调用 `browser_fetch`，最后调用 `close_session`。这比每个页面都启动一个新浏览器快得多。

    !!! danger "危险"
    
        使用持久会话时，完成后一定要关闭会话，否则它会一直保持打开状态！


8. **在较长的流程中使用持久会话**

    另一个需要 Claude 多思考的较长测试示例：

    ```
    Use Scrapling MCP to do the following in this order:

    1. Open a stealthy browser session with headless mode off.
    2. Go to this page and collect the number of stars: https://github.com/D4Vinci/Scrapling
    3. From the README, get the URL that shows the number of downloads and go to it.
    4. Get the number of downloads and the top 3 countries from the graph.
    5. Prepare a report with the results.
    6. Close the browser.
    ```

这些只是一些例子，还可以发挥创意，探索更多用法。

## 最佳实践 {#best-practices}

下面是一些技术建议。

### 1. 选择合适的工具 {#1-choose-the-right-tool}
- **`make_request`**：快速完成单个页面或 API 的 HTTP 请求
- **`browser_fetch_once`**：获取单个需要 JavaScript 的动态页面，或包括 Cloudflare 在内的受保护网站
- **会话工具**：处理相关请求、浏览器操作、截图和网络历史记录

### 2. 提高性能 {#2-optimize-performance}
- 复用会话，并按顺序获取每个 URL
- 禁用不需要的资源
- 设置合适的超时时间
- 使用 CSS 选择器定向提取内容

### 3. 处理动态内容 {#3-handle-dynamic-content}
- 对单页应用（SPA）使用 `network_idle`
- 设置 `wait_selector` 来等待指定元素
- 对加载较慢的网站增加超时时间

### 4. 数据质量 {#4-data-quality}
- 使用 `main_content_only=true` 选取并清理页面的正文
- 根据用途选择合适的 `extraction_type`

### 5. 提示词注入防护 {#5-prompt-injection-protection}
启用 `main_content_only`（默认启用）时，MCP 服务器会自动清理抓取的内容，移除恶意网站可能用来向 AI 上下文注入指令的隐藏内容：

- **用于隐藏内容的内联样式**：`display:none`、`visibility:hidden`，以及透明度、字号、高度、宽度、最大高度或最大宽度为零的样式
- **对辅助功能隐藏的元素**：`aria-hidden="true"`
- **模板标签和隐藏插槽**：`<template>` 和 `<slot hidden>` 元素
- **HTML 注释**：`<!-- ... -->`
- **零宽字符**：零宽空格等不可见的 Unicode 字符

提取 HTML、Markdown 和文本时都会自动执行此防护。保留默认的 `main_content_only=true` 可以获得最完整的防护。

### 6. 管理会话 {#6-manage-sessions}
- 单次获取页面时，使用 `make_request` 或 `browser_fetch_once`；它们会关闭各自的资源，不会留下供后续调用使用的会话
- 抓取多个页面时，使用 `browser_open` 创建持久浏览器会话，再通过该会话为每个页面调用 `browser_fetch`
- 发送多个普通 HTTP 请求时，改用 `open_request_session`，并为每个请求调用 `session_make_request`；它会在调用之间保留 Cookie、连接和浏览器指纹（`impersonate`），无需启动浏览器
- 会话会保留创建时的会话级配置，浏览器会话包括 headless、locale、cookies、隐身功能开关等，HTTP 请求会话包括 `impersonate` 和 `proxy`。每次调用时，通过 `browser_fetch`/`session_make_request` 传入请求级选项，如 timeout、wait_selector、network_idle、solve_cloudflare 等；默认值见工具的 schema
- `browser_fetch` 可以通过已打开的隐身浏览器会话处理 Cloudflare 验证
- 使用完毕后，务必调用 `close_session` 关闭会话并释放资源
- 使用 `list_sessions` 查看仍在运行的会话，以及各会话创建时使用的 `settings`（返回给 AI 智能体；CDP 会话中为空）
- 调用创建会话的工具时，可以传入自定义 `session_id`，用有意义的名称（如 `"search"`、`"checkout"`）代替默认的随机十六进制值。如果所选 ID 已被使用，工具会抛出异常，便于及时发现冲突

### 7. 截图 {#7-capturing-screenshots}

- `browser_screenshot` 会截取通过 `browser_fetch` 在隐身浏览器会话中打开的页面。它不会重新加载页面，因此 AI 可以查看已填写的字段、已展开的菜单，以及其他操作的结果。
- 图片会以真正的 `ImageContent` 块返回，让模型直接查看页面。
- 可以截取可见视口，也可以截取整个页面，包括需要向下滚动才能看到的内容。
- 可以只截取某个字段、图表、卡片或结果，减少周围内容的干扰。截取元素时，可以将目标滚动到可见区域。
- 需要无损图片时选择 PNG；需要减少数据量时选择 JPEG，并调整画质。
- 截图前，AI 可以使用 `browser_actions` 等待内容加载或完成交互。

## 法律和道德事项 {#legal-and-ethical-considerations}

⚠️ **重要准则：**

- **检查 robots.txt**：访问 `https://website.com/robots.txt`，查看抓取规则
- **遵守请求频率限制**：不要用大量请求使服务器过载
- **服务条款**：阅读并遵守网站条款
- **版权**：尊重知识产权
- **隐私**：注意个人数据保护相关法律
- **商业用途**：确认已取得商业使用所需的许可

---

*由 Scrapling 团队用 ❤️ 打造。祝抓取顺利！*
