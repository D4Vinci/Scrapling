---
title: "使用 StealthyFetcher 抓取 JavaScript 网站"
description: "用 Scrapling 浏览器会话渲染页面、等待数据、复用登录状态并读取后台 API 响应。配置代理和防护挑战处理。"
---

# 使用 StealthyFetcher 在浏览器中获取页面 {#browser-fetching-with-stealthyfetcher}

`StealthyFetcher` 可以加载 JavaScript 页面，并通过带有反机器人应对功能的 Chromium 或 Google Chrome 执行自动化。它使用经过隐身调整的 [Playwright API](https://playwright.dev/python/docs/intro)。

要自动操作页面，需要了解一些 [Playwright Page API](https://playwright.dev/python/docs/api/class-page)，后面会说明。

!!! success "前提条件"

    1. 已阅读 [Fetcher 基础](../fetching/choosing.md)，了解 [Response 对象](../fetching/choosing.md#response-object)，并知道如何选择 Fetcher。
    2. 已阅读[查询元素](../parsing/selection.md)，了解如何从 [Selector](../parsing/main_classes.md#selector)/[Response](../fetching/choosing.md#response-object) 对象中查找和提取元素。
    3. 已阅读[主要类](../parsing/main_classes.md)，了解 [Response](../fetching/choosing.md#response-object) 从 [Selector](../parsing/main_classes.md#selector) 继承的属性和方法。

## 基本用法 {#basic-usage}
这个 Fetcher 的主要导入方式与其他 Fetcher 相同：

```python
from scrapling.fetchers import StealthyFetcher
```
解析选项的配置方法见[这里](choosing.md#parser-configuration-in-all-fetchers)。

下面通过示例逐个介绍大部分参数。如需快速查阅，可以直接查看[完整参数表](#full-list-of-arguments)。

!!! abstract "说明"

    `fetch` 的异步版本是 `async_fetch`。


目前提供三种主要运行方式，可以按需要组合使用。

分别是：

### 1. 自带的 Chromium {#1-bundled-chromium}
```python
StealthyFetcher.fetch('https://example.com')
```
打开自带的 Chromium，使用默认隐身设置并加载页面。

### 2. 已安装的 Chrome {#2-real-chrome}
```python
StealthyFetcher.fetch('https://example.com', real_chrome=True)
```
如果设备上已安装 Google Chrome，可以使用这个选项。它与第一种方式类似，但使用本机的 Google Chrome 而不是 Chromium。这样请求更接近真实用户，也更难被识别为自动化。

如果还没有安装 Google Chrome，可以通过以下终端命令为库安装，而不必手动处理：
```commandline
playwright install chrome
```

### 3. CDP 连接 {#3-cdp-connection}
```python
StealthyFetcher.fetch('https://example.com', cdp_url='ws://localhost:9222')
```
除了在本机启动 Chromium 或 Google Chrome，还可以通过 [Chrome DevTools Protocol](https://chromedevtools.github.io/devtools-protocol/) 连接远程浏览器。

URL 可以是浏览器服务商提供的 WebSocket 地址（`ws://`/`wss://`），也可以是浏览器的 HTTP 地址，例如 `http://localhost:9222`。


## 它提供哪些功能？ {#what-does-it-do}

StealthyFetcher 提供以下反机器人应对功能：

1. 通过 `solve_cloudflare=True` 自动处理所有类型的 Cloudflare Turnstile 和 Interstitial 挑战。
2. 避免 CDP runtime 和 WebRTC 泄露信息。
3. 隔离 JavaScript 执行，移除多种 Playwright 指纹，并避免一些已知机器人行为触发检测。
4. 为 Canvas 添加随机噪声，防止通过 Canvas 识别指纹。
5. 自动处理已知的无头模式检测方式，并提供选项来应对时区不一致检测。
6. 还有其他应对防护的选项。

## 完整参数列表 {#full-list-of-arguments}
这个 Fetcher 及其会话类提供很多选项。在查看[示例](#examples)前，先列出完整参数：


| 参数 | 说明 | 可选 |
|:---------------------:|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|:--------:|
| url | 目标 URL。 | ❌ |
| headless | `True` 表示无头模式，即不显示窗口，**默认如此**。`False` 表示显示浏览器窗口。 | ✔️ |
| disable_resources | 阻止不必要的资源请求以提高速度。类型包括 `font`、`image`、`media`、`beacon`、`object`、`imageset`、`texttrack`、`websocket`、`csp_report` 和 `stylesheet`。 | ✔️ |
| cookies | 为下一次请求设置 Cookie。 | ✔️ |
| useragent | 指定 User-Agent 字符串。**未指定时，Fetcher 会生成并使用相同浏览器及版本的真实 User-Agent。** | ✔️ |
| network_idle | 等待页面至少连续 500 ms 没有网络连接。 | ✔️ |
| load_dom | 等待页面上的所有 JavaScript 加载并执行，即等待 `domcontentloaded` 状态。默认开启。 | ✔️ |
| pierce_shadow | 将开放的 Shadow DOM 内容包含在响应 HTML 中，默认为 `False`。可以为整个会话设置，也可以按请求覆盖。 | ✔️ |
| timeout | 页面操作和等待使用的超时时间，单位为毫秒。默认为 30,000 ms，即 30 秒。 | ✔️ |
| wait | 所有步骤结束后，在关闭页面并返回 `Response` 前额外等待的时间，单位为毫秒。 | ✔️ |
| page_action | 用于自动化的函数，接收 `page` 对象，在导航后执行所需操作。 | ✔️ |
| page_setup | 接收 `page` 对象并在导航前执行的函数。用于注册必须在页面加载前准备好的事件监听器或路由。 | ✔️ |
| wait_selector | 等待指定 CSS 选择器达到指定状态。 | ✔️ |
| init_script | JavaScript 文件的绝对路径，在此会话中的每个页面创建时执行。 | ✔️ |
| wait_selector_state | 等待 `wait_selector` 指定的元素达到这个状态。_默认状态为 `attached`。_ | ✔️ |
| google_search | 设置 Google referer 请求头，默认开启。 | ✔️ |
| extra_headers | 要添加到请求中的额外请求头字典。_同时使用时，`google_search` 设置的 referer 优先于这里的值。_ | ✔️ |
| proxy | 请求使用的代理，可以是字符串，或仅包含 'server'、'username'、'password' 的字典。 | ✔️ |
| real_chrome | 启用后，Fetcher 会启动并使用设备上已安装的 Chrome。 | ✔️ |
| locale | 区域设置，例如 `en-GB`、`de-DE`。影响 `navigator.language`、请求头 `Accept-Language`，以及数字和日期格式。默认使用系统区域设置。 | ✔️ |
| timezone_id | 修改浏览器时区，默认使用系统时区。 | ✔️ |
| cdp_url | 连接此 CDP URL 来控制已有浏览器，而不是启动新实例。 | ✔️ |
| user_data_dir | 用户数据目录的路径，用于保存 Cookie、本地存储等浏览器会话数据。默认创建临时目录。**仅支持会话。** | ✔️ |
| extra_flags | 启动浏览器时传入的额外参数列表。 | ✔️ |
| solve_cloudflare | 返回响应前，处理所有类型的 Cloudflare Turnstile 和 Interstitial 挑战。默认为 `False`。 | ✔️ |
| block_webrtc | 强制 WebRTC 遵守代理设置，避免泄露本地 IP 地址。 | ✔️ |
| hide_canvas | 为 Canvas 操作添加随机噪声，防止指纹识别。 | ✔️ |
| allow_webgl | 默认开启。关闭后会完全禁用 WebGL 和 WebGL 2.0。不建议关闭，因为很多 WAF 会检查 WebGL 是否启用。 | ✔️ |
| additional_args | 传给 Playwright 上下文的额外设置，优先级高于 Scrapling 设置。 | ✔️ |
| selector_config | 创建最终 `Selector`/`Response` 对象时使用的自定义解析参数字典。 | ✔️ |
| blocked_domains | 要阻止请求的域名集合，也会匹配子域名，例如 `"example.com"` 也会阻止 `"sub.example.com"`。 | ✔️ |
| block_ads | 阻止向约 3,500 个已知广告或跟踪域名发送请求，可与 `blocked_domains` 结合使用。 | ✔️ |
| dns_over_https | 通过 Cloudflare 的 DNS-over-HTTPS 发送 DNS 查询，避免使用代理时发生 DNS 泄露。 | ✔️ |
| proxy_rotator | 自动轮换代理的 `ProxyRotator` 实例，不能与 `proxy` 同时使用。 | ✔️ |
| retries | 失败请求的重试次数，默认为 3。 | ✔️ |
| retry_delay | 重试之间的等待秒数，默认为 1。 | ✔️ |
| record_requests | 在 `session.network` 中保留已完成的请求及保存的响应。仅用于会话，默认为 `False`。 | ✔️ |
| max_recorded_requests | 每个会话保留的最大请求条目数，默认为 1,000。保存的响应体还受固定大小限制。 | ✔️ |
| executable_path | 自定义浏览器可执行文件的绝对路径，用来替代自带的 Chromium。适用于特殊安装方式或自定义浏览器构建。 | ✔️ |

在会话类中，可以为整个会话设置这些参数。部分标签页级设置还可以在每次请求中单独覆盖，包括 `google_search`、`timeout`、`wait`、`page_action`、`page_setup`、`extra_headers`、`disable_resources`、`wait_selector`、`wait_selector_state`、`network_idle`、`load_dom`、`pierce_shadow`、`solve_cloudflare`、`blocked_domains`、`proxy` 和 `selector_config`。

!!! note "注意事项："

    1. 在我的测试中，`disable_resources` 让部分网站的请求加快了约 25%，也能减少代理流量。但要谨慎使用，因为它可能导致某些网站一直无法完成加载。
    2. 所有请求默认启用 `google_search`，将 referer 设为 `https://www.google.com/`。它的优先级高于 `extra_headers` 中设置的 referer。
    3. 未指定 User-Agent 且启用无头模式时，Fetcher 会生成并使用同版本浏览器的真实 User-Agent。未启用无头模式时，则使用浏览器默认的 User-Agent，在当前版本中与普通浏览器相同。
    4. `init_script` 注册在浏览器上下文中，因此会在页面创建时运行。隐身模式默认使用 Patchright 的隔离执行上下文。如果 `page_action` 需要读取脚本放在 `window` 上的全局值，应在操作函数中调用 `page.evaluate(..., isolated_context=False)`。

## 会话管理 {#session-management}

使用 `StealthySession`/`AsyncStealthySession`，可以在多次请求期间保持浏览器打开，并复用同一配置。这些类支持 `fetch` 的所有参数，因此可以统一设置整个会话。

```python
from scrapling.fetchers import StealthySession


with StealthySession(
    headless=True,
    disable_resources=True,
    real_chrome=True
) as session:

    page1 = session.fetch('https://example1.com')
    page2 = session.fetch('https://example2.com')
    page3 = session.fetch('https://dynamic-site.com')


```

### 使用异步会话 {#async-session-usage}

```python
import asyncio
from scrapling.fetchers import AsyncStealthySession

async def scrape_multiple_sites():
    async with AsyncStealthySession(
        network_idle=True,
        timeout=30000,
        max_pages=3
    ) as session:

        pages = await asyncio.gather(
            session.fetch('https://spa-app1.com'),
            session.fetch('https://spa-app2.com'),
            session.fetch('https://dynamic-content.com')
        )
        return pages
```

`max_pages` 控制**浏览器标签页池**中同时打开的最大标签页数。请求完成后，标签页保持打开。每次请求时，库会按以下步骤处理：

1. 如果有空闲标签页，就复用它。每次请求都会应用自己的 `timeout`、`extra_headers`、`disable_resources`、`blocked_domains` 等标签页设置，不会沿用上一次请求的配置。
2. 否则，如果当前标签页数少于 `max_pages`，就打开新标签页。
3. 否则，以不到一秒的间隔检查是否有标签页空闲。等待 60 秒后仍不可用，就抛出 `TimeoutError`。这可能发生在目标网站无响应时。

出现错误的标签页会被关闭并替换。也可以随时调用 `session.close_pages()` 关闭所有标签页，下一次请求会打开新的标签页。

这样就能在同一个浏览器中同时获取多个 URL，节省资源，而且速度很快 :)

标签页保持打开，也意味着下次请求开始时，之前的页面仍然存在。下一次请求的 `page_setup` 会在离开旧页面前运行，因此可以把自动化操作串联到多次请求中。

在 0.3.2 到 0.4.14 版本中，请求后会关闭标签页，因为复用时可能残留前一次请求的设置。从 0.4.15 开始，每次复用都会重置设置，因此标签页可以保持打开。

### 保存和加载会话状态 {#save-and-load-session-state}

使用 `save_state(path)` 把 Cookie、本地存储和 IndexedDB 保存到 JSON 文件。使用 `load_state(path)` 在另一个会话中恢复，或替换当前会话的已存储状态。两者都接受字符串或 `pathlib.Path`，并返回 `None`。文件格式与 Playwright 的存储状态文件兼容。

```python
from scrapling.fetchers import StealthySession

with StealthySession() as session:
    session.fetch('https://example.com')
    session.save_state('state.json')

with StealthySession() as session:
    session.load_state('state.json')
    page = session.fetch('https://example.com')
```

登录或其他浏览器操作完成后再保存。在已启动的会话中调用这两个方法，并先等待所有抓取完成。加载会替换已有 Cookie、本地存储和 IndexedDB。要使用恢复的登录状态，需要获取或重新加载页面；加载状态本身不会让现有标签页跳转。

使用 `AsyncStealthySession` 时需要 `await`：

```python
from scrapling.fetchers import AsyncStealthySession

async def restore_session():
    async with AsyncStealthySession() as session:
        await session.load_state('state.json')
        page = await session.fetch('https://example.com')
        await session.save_state('state.json')
        return page
```

这些方法只保存和恢复共享浏览器上下文，不影响单次代理请求的临时上下文。使用 `proxy_rotator` 的会话没有共享上下文，因此会抛出 `RuntimeError`。固定的会话 `proxy` 可以正常使用。

文件不包含 `sessionStorage`、打开的标签页或浏览器设置。保存会覆盖文件，其父目录必须已存在。文件和 JSON 错误会直接抛给调用方。

### 会话的优点 {#session-benefits}

- **复用浏览器**：后续请求使用同一个浏览器实例，速度更快。
- **保留 Cookie**：像普通浏览器一样自动管理 Cookie 和会话状态。
- **一致的指纹**：所有请求使用相同的浏览器指纹。
- **节省内存**：比每次请求都启动新浏览器更节省资源。


## 示例 {#examples}
通过示例更容易理解，下面逐一展示。

### 控制资源 {#resource-control}

```python

page = StealthyFetcher.fetch('https://example.com', disable_resources=True)
```

### Shadow DOM {#shadow-dom}

有些页面把内容放在开放的 Shadow Root 中，这些内容不会出现在页面的普通 HTML 里。启用 `pierce_shadow`，即可把它们加入响应，再照常使用 CSS 或 XPath：

```python
from scrapling.fetchers import StealthyFetcher

page = StealthyFetcher.fetch('https://example.com', pierce_shadow=True)
titles = page.css('product-card .title::text').getall()
```

此选项默认为 `False`。也可以为会话开启，再针对单次请求关闭：

```python
from scrapling.fetchers import StealthySession

with StealthySession(pierce_shadow=True) as session:
    page = session.fetch('https://example.com')
    plain_page = session.fetch('https://example.com', pierce_shadow=False)
```

相同选项也适用于 `async_fetch` 和异步会话。

只包含开放的 Shadow Root，不会遍历封闭的 Shadow Root 或 iframe 文档。如果组件在页面加载后才出现，可以使用 `wait_selector`。

每个开放的 Shadow Root 会在响应中包装为一个 `<shadow-root>` 元素。Slot 保留原有标签和属性，并包含分配给它的节点；如果没有分配节点，则使用后备内容。未分配到 Slot 的 Light DOM 子节点会被省略。真实浏览器页面不会被修改。

```html
<product-card>
  <shadow-root>
    <div class="title">Product name</div>
    <slot name="price"><span class="price">20</span></slot>
  </shadow-root>
</product-card>
```

后代选择器可以跨这些元素查找。直接子元素选择器则必须包含新增的包装元素和 Slot：

```python
titles = page.css('product-card .title::text').getall()
titles = page.css('product-card > shadow-root > .title::text').getall()
prices = page.css('product-card > shadow-root > slot[name="price"] > .price::text').getall()
```

这些包装元素和 Slot 会出现在 XPath 路径、`.children`、`response.body` 和 HTML 导出中。Markdown 和文本提取只返回内容，不输出标签。表示隐藏状态的 Slot 属性仍会保留，供内容清理使用。

快照遵循内容顺序，但不计算 CSS 可见性或布局。包含 `<shadow-root>` 的选择器针对 Scrapling 响应，而不是真实浏览器页面。其他 HTML 解析器可能以不同方式处理这些特殊嵌套结构。

### 屏蔽域名 {#domain-blocking}

```python

page = StealthyFetcher.fetch('https://example.com', blocked_domains={"ads.example.com", "tracker.net"})
```

### 控制网络 {#network-control}

```python

page = StealthyFetcher.fetch('https://example.com', network_idle=True)


page = StealthyFetcher.fetch('https://example.com', timeout=30000)


page = StealthyFetcher.fetch('https://example.com', proxy='http://username:password@host:port')
```

### 下载文件 {#downloading-files}

```python
page = StealthyFetcher.fetch('https://raw.githubusercontent.com/D4Vinci/Scrapling/main/docs/assets/main_cover.png')

with open(file='main_cover.png', mode='wb') as f:
    f.write(page.body)
```

`Response` 对象的 `body` 属性始终返回 `bytes`。

### 导航前设置 {#pre-navigation-setup}
如果事件监听器、路由或脚本必须在页面导航前注册，使用 `page_setup`。这个函数接收 `page` 对象，并在 `page.goto()` 之前运行。

```python
from patchright.sync_api import Page

def capture_websockets(page: Page):
    page.on("websocket", lambda ws: print(f"WebSocket opened: {ws.url}"))

page = StealthyFetcher.fetch('https://example.com', page_setup=capture_websockets)
```
异步版本：
```python
from patchright.async_api import Page

async def capture_websockets(page: Page):
    page.on("websocket", lambda ws: print(f"WebSocket opened: {ws.url}"))

page = await StealthyFetcher.async_fetch('https://example.com', page_setup=capture_websockets)
```

可以与 `page_action` 配合使用：`page_setup` 在导航前执行，`page_action` 在导航后执行。

### Cloudflare 和隐身选项 {#cloudflare-and-stealth-options}

```python

page = StealthyFetcher.fetch('https://nopecha.com/demo/cloudflare', solve_cloudflare=True)


page = StealthyFetcher.fetch(
    'https://protected-site.com',
    solve_cloudflare=True,
    block_webrtc=True,
    real_chrome=True,
    hide_canvas=True,
    google_search=True,
    proxy='http://username:password@host:port',  # It can also be a dictionary with only the keys 'server', 'username', and 'password'.
)
```

`solve_cloudflare` 会自动检测并处理所有类型的 Cloudflare Turnstile 和 Interstitial 挑战：

- JavaScript 挑战，由 Cloudflare 管理
- 交互式挑战，例如点击验证框
- 无感挑战，在后台自动验证

也支持包含嵌入式验证码的自定义页面。

!!! notes "**重要说明：**"

    1. 某些网站使用自定义实现，需要设置 `wait_selector`，确保解开验证码后继续等待真实页面内容。我们尽量让处理逻辑通用，但有些网站确实属于特殊情况。
    2. 使用 Cloudflare 处理功能时，超时应至少设为 60 秒，留出足够的挑战处理时间。
    3. 这项功能可以与代理和其他隐身选项一起使用。

### 浏览器自动化 {#browser-automation}
这里需要了解 [Playwright Page API](https://playwright.dev/python/docs/api/class-page)。传入的函数接收 Playwright 的 Page 对象，执行所需操作，然后 Fetcher 继续工作。

如果启用了 `network_idle`，这个函数会在等待完成后立即执行。它在等待 `wait_selector` 之前执行，因此除了自动化，也可以用于其他页面修改。

下面通过页面的[鼠标事件](https://playwright.dev/python/docs/api/class-mouse)，先用滚轮滚动，再移动鼠标。
```python
from patchright.sync_api import Page

def scroll_page(page: Page):
    page.mouse.wheel(10, 0)
    page.mouse.move(100, 400)
    page.mouse.up()

page = StealthyFetcher.fetch('https://example.com', page_action=scroll_page)
```
使用异步抓取方法时，这个函数也必须是异步函数。
```python
from patchright.async_api import Page

async def scroll_page(page: Page):
   await page.mouse.wheel(10, 0)
   await page.mouse.move(100, 400)
   await page.mouse.up()

page = await StealthyFetcher.async_fetch('https://example.com', page_action=scroll_page)
```

### 等待条件 {#wait-conditions}

```python

page = StealthyFetcher.fetch(
    'https://quotes.toscrape.com/js-delayed/',
    wait_selector='.quote',
    wait_selector_state='visible'
)
```
这是返回响应前最后一项可配置的等待条件。向 `wait_selector` 传入 CSS 选择器，Fetcher 会等待 `wait_selector_state` 指定的状态。未指定时默认为 `attached`，即元素已经出现在 DOM 中。

之后，如果开启 `load_dom`，Fetcher 会再次检查所有 JavaScript 是否已加载并执行，也就是是否达到 `domcontentloaded` 状态，必要时继续等待。这个选项默认开启。如果启用了 `network_idle`，还会再次等待 `network_idle` 满足条件。

可以等待以下状态（[来源](https://playwright.dev/python/docs/api/class-page#page-wait-for-selector)）：

- `attached`：等待元素出现在 DOM 中。
- `detached`：等待元素从 DOM 中移除。
- `visible`：等待元素的边界框非空，且没有设置 `visibility:hidden`。没有内容或设置了 `display:none` 的元素边界框为空，不算可见。
- `hidden`：等待元素从 DOM 中移除、边界框为空，或设置了 `visibility:hidden`。它与 `'visible'` 相反。

### 网络历史记录 {#network-history}

在浏览器会话中启用 `record_requests`，即可检查跨页面加载、操作和标签页的已完成请求。历史记录覆盖会话的所有上下文，包括临时代理上下文，并把响应保存为 Scrapling `Response`。可以查找 API 调用、HTTP 错误和重定向，而不必再次发送请求。会话关闭后也能读取已保存的响应头和响应体。失败或尚未完成的请求会被省略，已完成的 HTTP 4xx 和 5xx 响应则会保留。

```python
from scrapling.fetchers import StealthySession

with StealthySession(record_requests=True, max_recorded_requests=1000) as session:
    session.fetch('https://example.com', network_idle=True)

for response in session.network.search(resource_type='document', limit=None):
    print(response.meta['network_id'], response.url, response.status)
    if note := response.meta.get('body_note'):
        print(note)
    else:
        print(response.body)
        print(response.css('title::text').get())

session.network.clear()
```

同一 API 也适用于 `AsyncStealthySession`。记录功能默认关闭。创建会话时设置 `record_requests=True`，需要时再设置 `max_recorded_requests`。

- `session.network.search(url_pattern=None, method=None, resource_type=None, status=None, after_id=0, limit=100, include_static=True)` 按网络 ID 顺序返回已保存的 `Response`。`limit=None` 返回所有仍被保留的匹配项。`url_pattern` 是搜索时使用的正则表达式，模式无效时会在搜索时抛出错误。`after_id` 选择网络 ID 更大的响应。`include_static=False` 只保留 XHR/fetch 请求和 HTTP 错误；使用 `True` 可包含所有资源类型和已保存的重定向。
- `session.network.get(request_id)` 返回一个已保存的 `Response`，如果记录已被移除，则返回 `None`。
- `session.network.clear()` 清空历史记录。请求 ID 仍继续递增，不会重复使用。

每个已保存的 `Response` 都可以直接访问 `.url`、`.method`、`.status`、`.headers`、`.request_headers`、字节形式的 `.body`、`.json()` 和 CSS/XPath 方法。`.meta` 包含 `network_id`、`resource_type` 和 `request_body`，后者为字节或 `None`。如果读取完整响应头失败，保存的头信息可能不完整。这些都是本地读取。即使在异步会话中，也不要使用 await 等待这些读取，或调用 `.body()`。如果保存的内容无法解析，原始字节仍会保留，但 CSS/XPath 方法会使用空文档。

要按 URL 查找 API 流量，可以使用 `session.network.search(url_pattern=r'https://api\.example\.com/.*', limit=None)`。只需要某种请求类型时，再加上 `resource_type='fetch'` 或 `resource_type='xhr'`。

记录器只读取并保存受支持的文本 `Content-Type` 响应体，包括 `text/*`、`+json`/`+xml` 类型及 SVG、JSON、XML、JavaScript、GraphQL 和 URL 编码的表单数据。二进制、未知类型或没有 `Content-Type` 的响应只保留元数据，不保留响应体字节。浏览器仍会正常加载资源。

保存的响应字节来自 Playwright，可能与服务器最初发送的字节不同。如果字节是有效的 UTF-8，就按 UTF-8 读取，与 Playwright 一致；否则使用声明的字符集。响应头保持不变。

被跳过、过大或无法读取的响应体返回 `b''`，原因保存在 `response.meta.get('body_note')`。非文本内容的说明是 `Non-text body; not saved.`。响应元数据和可用响应头仍会保留。已保存的文本，包括空文本，不带这个说明。HEAD 响应及状态码 204、205、304 的响应保持为空，也不带说明。

历史记录的 `search`、`get` 和 `clear` 都是本地同步调用，即使使用异步会话也一样。只有响应转换并保存后，条目才会出现。浏览器事件在 Playwright 活动期间处理，异步记录还需要事件循环运行。读取历史记录不会等待正在进行的记录操作。

关闭会话也不会等待记录操作。页面导航或浏览器上下文关闭时，尚未完成的记录可能丢失。已经保存的响应在关闭后仍可读取。

默认最多保留 1,000 个请求。每个响应体最多 1 MiB，所有响应体合计最多 20 MiB。达到限制时会删除旧记录。这些响应体大小限制是固定的，不能通过会话参数修改。它们只限制保留的条目和响应字节，不限制浏览器总内存、并行记录、临时完整读取、解析后的 HTML 或请求体。

#### 迁移到 v5 {#migrating-in-v5}

v5 移除了 `capture_xhr` 和 `response.captured_xhr`。请创建独立的浏览器会话，设置 `record_requests=True`，再读取 `session.network.search(url_pattern=..., limit=None)`。这也替代了单次 Fetcher 调用的 API 记录方式，所以需要保留会话实例。过滤条件应用于整个会话的已保存历史，而不是记录阶段或某一次抓取。只保存受支持的文本响应体。`search()` 默认最多返回 100 个匹配项，`limit=None` 返回所有仍保留的匹配项，但不会改变历史记录的存储限制。

### 浏览器请求头和区域设置 {#browser-headers-and-locale}

```python
page = StealthyFetcher.fetch(
    'https://example.com',
    google_search=True,
    useragent='Mozilla/5.0...',
    locale='en-US',
)
```

### 综合示例 {#general-example}
```python
from scrapling.fetchers import StealthyFetcher

def scrape_dynamic_content():

    page = StealthyFetcher.fetch(
        'https://example.com/dynamic',
        network_idle=True,
        wait_selector='.content'
    )


    content = page.css('.content')

    return {
        'title': content.css('h1::text').get(),
        'items': [
            item.text for item in content.css('.item')
        ]
    }
```

### 代理轮换 {#proxy-rotation}

```python
from scrapling.fetchers import StealthySession, ProxyRotator


rotator = ProxyRotator([
    "http://proxy1:8080",
    "http://proxy2:8080",
    "http://proxy3:8080",
])


with StealthySession(proxy_rotator=rotator, headless=True) as session:
    page1 = session.fetch('https://example1.com')
    page2 = session.fetch('https://example2.com')


    page3 = session.fetch('https://example3.com', proxy='http://specific-proxy:8080')
```

!!! warning

    所有浏览器 Fetcher 及其会话默认使用持久浏览器上下文和标签页池。但浏览器无法为每个标签页单独设置代理。因此，使用 `ProxyRotator` 时，Fetcher 会为每个代理创建独立上下文，每个上下文只有一个标签页。任务完成后，标签页和对应上下文都会关闭。

## 适用场景 {#when-to-use}

以下情况适合使用 StealthyFetcher：

- 需要绕过反机器人防护。
- 需要可靠的浏览器指纹。
- 需要完整的 JavaScript 支持。
- 希望自动启用隐身功能。
- 需要浏览器自动化。
- 需要处理 Cloudflare 防护。
