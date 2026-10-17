---
title: "为网页抓取选择 HTTP 请求或浏览器"
description: "为抓取任务选择 Fetcher 或 StealthyFetcher。了解何时使用直接 HTTP 请求、JavaScript 渲染和可复用会话。"
---

# Fetcher 基础 {#fetchers-basics}

## 简介 {#introduction}
Fetcher 是用于发送请求或获取页面的类。一行代码就能使用多种功能，并得到一个 [Response](#response-object) 对象。从 v0.3 开始，所有 Fetcher 都有独立的会话类，用于保持会话运行。例如，浏览器 Fetcher 可以在所有请求完成前一直保持同一个浏览器打开，而不必重复打开浏览器。具体用哪种方式取决于任务需求。

在 v0.2 之前，Scrapling 只是一个解析引擎。加入 Fetcher，是为了逐步覆盖网页抓取的整个流程。

> Fetcher 不只是对其他库的简单封装。它们把这些库作为请求和获取页面的引擎，同时提供底层引擎没有的功能，并充分利用和优化这些引擎，让它们更适合网页抓取。

## Fetcher 概览 {#fetchers-overview}

Scrapling 提供 HTTP Fetcher（`Fetcher` 和 `AsyncFetcher`）以及浏览器 Fetcher（`StealthyFetcher`）。重复发送请求时可以使用相应的会话类。

下表可帮助快速选择。


| 功能 | Fetcher | StealthyFetcher |
|--------------------|---------------------------------------------------|--------------------------------------------------------------------------------------------|
| 相对速度 | 🐇🐇🐇🐇🐇 | 🐇🐇🐇 |
| 隐蔽性 | ⭐⭐ | ⭐⭐⭐⭐⭐ |
| 反机器人应对选项 | ⭐⭐ | ⭐⭐⭐⭐⭐ |
| 加载 JavaScript | ❌ | ✅ |
| 内存用量 | ⭐ | ⭐⭐⭐ |
| 适用场景 | 只需 HTTP 请求即可完成的基础抓取 | - 动态加载的网站 <br/>- 简单自动化 <br/>- 从简单到复杂的防护 |
| 浏览器 | ❌ | Chromium 和 Google Chrome |
| 使用的浏览器 API | ❌ | Playwright |
| 配置难度 | 简单 | 简单 |

接下来的页面会分别详细介绍。

## 配置所有 Fetcher 的解析器 {#parser-configuration-in-all-fetchers}
所有 Fetcher 的导入方式相同，后面的页面会具体展示：
```python
from scrapling.fetchers import Fetcher, AsyncFetcher, StealthyFetcher
```
无需创建实例，即可直接使用。默认会采用解析器的标准设置：
```python
page = StealthyFetcher.fetch('https://example.com') 
```
如果要配置处理响应的解析器（[Selector 类](../parsing/main_classes.md#selector)），先执行以下操作：
```python
from scrapling.fetchers import Fetcher
Fetcher.configure(adaptive=True, keep_comments=False)  # and the rest
```
或者
```python
from scrapling.fetchers import Fetcher
Fetcher.adaptive=True
Fetcher.keep_comments=False
```
然后继续编写其他代码。

可用的配置参数有 `adaptive`、`adaptive_domain`、`huge_tree`、`keep_comments`、`storage` 和 `storage_args`，与 [Selector](../parsing/main_classes.md#selector) 的对应参数相同。随时可以通过 `<fetcher_class>.display_config()` 查看当前配置。

!!! info

    `adaptive` 默认关闭。要使用自适应功能，需要先启用它。

### 为每次请求配置解析器 {#set-parser-config-per-request}
上面的配置会全局应用到通过该类发出的所有请求，目的是简化使用。

如果不同请求需要不同配置，可以向请求方法（`fetch`/`get`/`post`/...）的 `selector_config` 参数传入字典。

## Response 对象 {#response-object}
`Response` 基于 [Selector](../parsing/main_classes.md#selector)，还包含响应头、状态、Cookie 等响应信息，如下所示：
```python
from scrapling.fetchers import Fetcher
page = Fetcher.get('https://example.com')

page.status          # HTTP status code
page.reason          # Status message
page.cookies         # Response cookies as a dictionary
page.headers         # Response headers
page.request_headers # Request headers
page.history         # Response history of redirections, if any
page.body            # Raw response body as bytes
page.encoding        # Response encoding
page.meta            # Response metadata dictionary (e.g., proxy used). Mainly helpful with the spiders system.
```
所有 Fetcher 都返回 `Response` 对象。启用 `record_requests=True` 的浏览器会话，也会通过 `session.network.search(limit=None)` 和 `session.network.get(request_id)` 返回已保存的 `Response` 对象。有关保存 API 响应和迁移到 v5 的说明，请参阅[网络历史记录](stealthy.md#network-history)。

`Response` 还可以用一行代码把页面转换为适合 LLM 使用的干净 Markdown：
```python
markdown = Fetcher.get('https://example.com').markdown(main_content_only=True)
```
转换前始终会移除脚本、样式、隐藏内容和提示注入内容。传入 `css_selector` 可以只转换指定元素。这需要安装 `rag` 扩展依赖，`ai`/`shell`/`all` 也包含它。详细说明见[构建 RAG 系统](../ai/building-rag-systems.md)。

!!! note

    与 [Selector](../parsing/main_classes.md#selector) 不同，从 v0.4 开始，`Response` 的响应体始终为 bytes。
