---
title: "在 Scrapling 交互式 Shell 中测试网页抓取"
description: "在 IPython Shell 中获取页面、尝试选择器并检查结果。转换 curl 命令、复用最近的响应，并测试抓取代码。"
---

# Scrapling 交互式 Shell 指南 {#scrapling-interactive-shell-guide}

<script src="https://asciinema.org/a/736339.js" id="asciicast-736339" async data-autoplay="1" data-loop="1" data-cols="225" data-rows="40" data-start-at="00:06" data-speed="1.5" data-theme="tango"></script>

**面向开发者和数据科学家的网页抓取 REPL**

Scrapling 交互式 Shell 是基于 IPython 的增强环境，专为网页抓取设计。它提供全部 Scrapling 功能、实用快捷方式、自动页面管理，以及 curl 命令转换等工具。

!!! success "前置知识"

    1. 阅读 [Fetcher 基础](../fetching/choosing.md)，了解 [Response 对象](../fetching/choosing.md#response-object)并选择合适的 Fetcher。
    2. 阅读[元素查询](../parsing/selection.md)，学习如何从 [Selector](../parsing/main_classes.md#selector)/[Response](../fetching/choosing.md#response-object) 对象中查找和提取元素。
    3. 阅读[主要类](../parsing/main_classes.md)，了解 [Response](../fetching/choosing.md#response-object) 从 [Selector](../parsing/main_classes.md#selector) 继承了哪些属性和方法。
    4. 至少阅读 Fetcher 部分的一篇相关指南：[HTTP 请求](../fetching/static.md)或[通过浏览器获取页面](../fetching/stealthy.md)。

## 为什么使用交互式 Shell？ {#why-use-the-interactive-shell}

交互式 Shell 可以即时探索和测试，不必每次修改脚本后再重新运行。它适合：

- **快速验证想法**：立即测试抓取方案。
- **探索数据**：以交互方式浏览网站并提取数据。
- **学习 Scrapling**：实时尝试各项功能。
- **调试抓取代码**：逐步执行请求并检查结果。
- **转换命令**：用一行代码将浏览器开发者工具中的 curl 命令转为 Fetcher 请求。

## 开始使用 {#getting-started}

### 启动 Shell {#launch-the-shell}

```bash
# Start the interactive shell
scrapling shell

# Execute code and exit (useful for scripting)
scrapling shell -c "get('https://quotes.toscrape.com'); print(len(page.css('.quote')))"

# Set logging level
scrapling shell --loglevel info
```

启动后会显示 Scrapling 横幅，随后就可以开始抓取，如上面的视频所示：

```python
# No imports needed - everything is ready!
get('https://news.ycombinator.com')

# Explore the page structure
page.css('a')[:5]  # Look at first 5 links

# Refine your selectors
stories = page.css('.titleline>a')
len(stories)  # 30

# Extract specific data
for story in stories[:3]:
    title = story.text
    url = story['href']
    print(f"{title}: {url}")

# Try different approaches
titles = page.css('.titleline>a::text')  # Direct text extraction
urls = page.css('.titleline>a::attr(href)')  # Direct attribute extraction
```

## 内置快捷方式 {#built-in-shortcuts}

Shell 提供这些快捷方式，减少重复代码：

- **`get(url, **kwargs)`**：HTTP GET 请求，代替 `Fetcher.get`。
- **`post(url, **kwargs)`**：HTTP POST 请求，代替 `Fetcher.post`。
- **`put(url, **kwargs)`**：HTTP PUT 请求，代替 `Fetcher.put`。
- **`delete(url, **kwargs)`**：HTTP DELETE 请求，代替 `Fetcher.delete`。
- **`fetch(url, **kwargs)`**：通过隐身浏览器获取页面，代替 `StealthyFetcher.fetch`。

常用类无需导入即可使用，包括 `Fetcher`、`AsyncFetcher`、`StealthyFetcher` 和 `Selector`。

### 自动管理页面 {#smart-page-management}

Shell 会自动记录请求和页面：

- **访问当前页面**

    `page` 和 `response` 会自动更新为最近获取的页面：

    ```python
    get('https://quotes.toscrape.com')
    # 'page' and 'response' both refer to the last fetched page
    page.url  # 'https://quotes.toscrape.com'
    response.status  # Prints 200; Same as page.status
    ```

- **页面历史**

    `pages` 用一个 `Selectors` 对象保留最近五个页面：

    ```python
    get('https://site1.com')
    get('https://site2.com')
    get('https://site3.com')
    
    # Access last 5 pages
    len(pages)  # `Selectors` object with `page` history -> 3
    pages[0].url  # First page in history -> 'https://site1.com'
    pages[-1].url  # Most recent page -> 'https://site3.com'
    
    # Work with historical pages
    for i, old_page in enumerate(pages):
        print(f"Page {i}: {old_page.url} - {old_page.status}")
    ```

## 其他实用命令 {#additional-helpful-commands}

### 查看页面 {#page-visualization}

在浏览器中查看获取的页面：

```python
get('https://quotes.toscrape.com')
view(page)  # Opens the page HTML in your default browser
```

### 转换 curl 命令 {#curl-command-integration}

Shell 提供 `uncurl` 和 `curl2fetcher`，可以把浏览器开发者工具中的 curl 命令转换为 `Fetcher` 请求。

先把一条请求复制为 curl 命令：

<img src="../assets/scrapling_shell_curl.png" title="将 Chrome 中的请求复制为 curl 命令" alt="将 Chrome 中的请求复制为 curl 命令" style="width: 70%;"/>

- **将 curl 命令转为请求对象**

    ```python
    curl_cmd = '''curl 'https://scrapling.requestcatcher.com/post' \
      -X POST \
      -H 'Content-Type: application/json' \
      -d '{"name": "test", "value": 123}' '''
    
    request = uncurl(curl_cmd)
    request.method  # -> 'post'
    request.url  # -> 'https://scrapling.requestcatcher.com/post'
    request.headers  # -> {'Content-Type': 'application/json'}
    ```

- **直接执行 curl 命令**

    ```python
    # Convert and execute in one step
    curl2fetcher(curl_cmd)
    page.status  # -> 200
    ```

### IPython 功能 {#ipython-features}

Shell 继承了 IPython 的全部功能：

```python
# Magic commands
%time page = get('https://example.com')  # Time execution
%history  # Show command history
%save filename.py 1-10  # Save commands 1-10 to file

# Tab completion works everywhere
page.c<TAB>  # Shows: css, cookies, headers, etc.
Fetcher.<TAB>  # Shows all Fetcher methods

# Object inspection
get? # Show get documentation
```

## 示例 {#examples}

下面是几个由 AI 生成的示例：

#### 采集电商数据 {#e-commerce-data-collection}

```python
# Start with product listing page
catalog = get('https://shop.example.com/products')

# Find product links
product_links = catalog.css('.product-link::attr(href)').getall()
print(f"Found {len(product_links)} products")

# Sample a few products first
for link in product_links[:3]:
    product = get(catalog.urljoin(link))
    name = product.css('.product-name::text').get('')
    price = product.css('.price::text').get('')
    print(f"{name}: {price}")

# Scale up with sessions for efficiency
from scrapling.fetchers import FetcherSession
with FetcherSession() as session:
    products = []
    for link in product_links:
        product = session.get(catalog.urljoin(link))
        products.append({
            'name': product.css('.product-name::text').get(''),
            'price': product.css('.price::text').get(''),
            'url': link
        })
```

#### API 集成与测试 {#api-integration-and-testing}

```python
>>> # Test API endpoints interactively
>>> response = get('https://jsonplaceholder.typicode.com/posts/1')
>>> response.json()
{'userId': 1, 'id': 1, 'title': 'sunt aut...', 'body': 'quia et...'}

>>> # Test POST requests
>>> new_post = post('https://jsonplaceholder.typicode.com/posts', 
...                 json={'title': 'Test Post', 'body': 'Test content', 'userId': 1})
>>> new_post.json()['id']
101

>>> # Test with different data
>>> updated = put('https://jsonplaceholder.typicode.com/posts/1',
...               json={'title': 'Updated Title'})
```

## 获取帮助 {#getting-help}

如果终端中的帮助还不够，可以查看：

- [Scrapling 文档](https://scrapling.readthedocs.io/zh-cn/latest/)
- [Discord 社区](https://discord.gg/EMgGbDceNQ)
- [GitHub Issues](https://github.com/D4Vinci/Scrapling/issues)

就是这样！祝抓取顺利。Shell 让网页抓取像对话一样简单。
