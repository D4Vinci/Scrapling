---
title: "Scrapling MCP 服务器 API 参考"
description: "查看 MCP 服务器工具及其请求、响应和会话模型，用于通过 HTTP 和浏览器提取数据。"
---

# MCP 服务器参考 {#mcp-server-api-reference}

**Scrapling MCP 服务器**通过 Model Context Protocol（MCP）提供十六个数据提取和浏览器操作工具。将 Scrapling 接入 AI 助手和智能体，就能通过对话提取数据，并使用反检测功能。

用下面的命令启动 MCP 服务器：

```bash
scrapling mcp
```

也可以直接导入服务器类：

```python
from scrapling.core.ai import ScraplingMCPServer

server = ScraplingMCPServer()
server.serve(http=False, host="127.0.0.1", port=8000)
```

要使用自己的 Chromium 兼容浏览器程序，请传入 `executable_path`：

```python
server = ScraplingMCPServer(executable_path="/path/to/chromium")
```

## 响应模型 {#response-model}

页面获取和 HTTP 请求工具返回以下结构，每次调用返回一个响应。会话管理工具使用后面的模型。`browser_screenshot` 将页面或元素的截图和当前 URL 作为图像块和文本块返回。`browser_extract` 和 `browser_actions` 返回纯文本。两个网络工具通过后面的模型返回结构化 JSON。`browser_evaluate` 将结果转为 JSON，放在文本块中返回。

## ::: scrapling.core.ai.server.ResponseModel
    handler: python
    :docstring:

## 网络请求模型 {#network-request-models}

`browser_network_requests` 返回 `NetworkRequestsModel`，包含 `requests`、`next_cursor`、`has_more` 和 `dropped_count`。每个 `NetworkRequestInfo` 包含 `id`、`url`、`method`、`resource_type` 和 `status`。要读取下一页，将 `next_cursor` 作为 `after_id` 传入。`has_more` 表示当前历史记录中是否还有匹配结果。

`browser_network_request` 返回 `NetworkRequestModel`，包含 `request_id`、`part`、`data` 和 `note`。摘要和请求头或响应头是对象。完整保存的内容以字符串返回，即使响应内容是 JSON 也是如此。`note` 说明内容是否缺失，或头部信息是否不完整。

## ::: scrapling.core.ai._network_formatting.NetworkRequestInfo
    handler: python
    :docstring:

## ::: scrapling.core.ai.server.NetworkRequestsModel
    handler: python
    :docstring:

## ::: scrapling.core.ai._network_formatting.NetworkRequestModel
    handler: python
    :docstring:

## 会话模型 {#session-models}

用于会话管理的模型类：

## ::: scrapling.core.ai.server.SessionInfo
    handler: python
    :docstring:

## ::: scrapling.core.ai.server.SessionCreatedModel
    handler: python
    :docstring:

## ::: scrapling.core.ai.server.SessionClosedModel
    handler: python
    :docstring:

## MCP 服务器类 {#mcp-server-class}

MCP 服务器的主类提供以下工具：

- **`make_request`**：通过 HTTP 获取一个 URL，模拟浏览器，并自动关闭客户端。支持 GET、POST、PUT 和 DELETE。
- **`browser_fetch_once`**：用隐身浏览器获取一个 URL，执行 JavaScript、处理 Cloudflare 验证，然后关闭浏览器。如果之后还要操作页面或查看网络历史记录，请使用持久会话。

- **`browser_extract`**：读取当前页面或元素，输出适合 AI 的结构化视图、HTML、Markdown 或文本，无需重新加载。表单和操作结果会保留。结构化视图包含元素的角色、名称、引用、位置和尺寸。正则表达式搜索返回匹配行、附近内容和父节点。
- **`browser_actions`**：在一次调用中组合鼠标移动、悬停、点击、滚动、填写表单、快捷键、对话框响应和等待。可以接受或关闭提示和确认框，也可以在输入对话框中填写内容。例如，填写搜索框、提交、等待并打开结果，无需每一步都调用一次工具。

    移动和点击支持选择器、结构化视图中的引用或坐标。工具会等待元素出现，并将其滚动到可见区域。支持分步移动、鼠标左键、右键和中键点击、双击，以及嵌套区域内的滚动。

    用选择器或结构化视图中的引用选择表单字段。可以输入文字、勾选或取消勾选复选框、选择单选按钮，以及按标签选择原生下拉框中的一个或多个选项。可以替换或清空文字，也可以从光标处继续输入。快捷键作用于当前焦点。慢速模式会在字符和操作之间加入随机停顿。

    用选择器或结构化视图中的引用等待内容或加载遮罩达到所需状态。也可以等待页面加载事件、网络空闲或指定时长。

- **`browser_evaluate`**：在当前页面执行 JavaScript，用于自定义数据提取、计算、读取应用状态或修改内容。支持异步脚本，并返回 JSON 结果。
- **`browser_network_requests`**：搜索跨标签页、页面跳转和操作的已完成浏览器请求。查找保存的 API 请求、HTTP 错误和重定向。默认隐藏静态资源，减少无关结果。失败或未完成的请求会被跳过。返回可分页的结构化数据。
- **`browser_network_request`**：以结构化 JSON 读取已保存请求的摘要、头部信息、发送的数据或文本内容，无需再次发送请求。所选部分会完整返回。页面跳转后仍可读取已保存的响应，包括 4xx 和 5xx HTTP 响应。记录完成后才会出现在历史中。读取历史或关闭会话不会等待尚未完成的记录，它们可能在页面跳转或关闭时丢失。字节数据来自 Playwright，可能与服务器发送的原始字节不同。保存的字节是有效 UTF-8 时，使用该编码解码，与 Playwright 一致；否则使用声明的字符集。只读取和保存具有受支持的文本 `Content-Type` 的响应内容。二进制、缺失或未知类型只保留元数据和头部信息，不读取内容。这不会改变页面加载方式。历史记录有大小限制。可选的说明会指出内容不是文本、超过大小限制或无法读取等情况。请在关闭 MCP 会话前读取需要的数据。
- **`browser_fetch`**：在已打开的隐身浏览器会话中获取页面，并提取 HTML、Markdown、文本或结构化视图。视图可以覆盖整页或单个元素，并包含供后续操作使用的引用、位置和尺寸。

## ::: scrapling.core.ai.server.ScraplingMCPServer
    handler: python
    :docstring:
