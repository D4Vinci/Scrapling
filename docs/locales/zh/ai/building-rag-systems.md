---
title: "用 Scrapling 将网站转为 Markdown，供 RAG 使用"
description: "将页面响应转为 Markdown，或用 ContentSpider 采集整个网站，为 RAG 系统准备可分块和建立索引的文本。"
---

# 用 Scrapling 构建 RAG 系统 {#building-rag-systems-with-scrapling}

RAG 系统的效果取决于输入的文本。原始 HTML 中的标签、导航、脚本和跟踪内容会浪费 token，甚至可能把隐藏的提示词注入内容直接传给 LLM。Scrapling 无需调用 LLM，就能把页面和整个网站转换为经过清理的 Markdown。数据采集因此速度快，也没有按页计费的成本。

## 安装 {#installation}

```bash
pip install "scrapling[rag]"

scrapling install
```

`rag` 扩展会安装 Fetcher 和 Markdown 转换支持，`ai`、`shell` 和 `all` 扩展也包含这些功能。`scrapling install` 会下载浏览器依赖，只有使用浏览器的 Fetcher 才需要它们。

## 将单个页面转为 Markdown {#one-page-to-markdown}

每个 [Response](../fetching/choosing.md#response-object) 都有 `markdown()` 方法：

```python
from scrapling.fetchers import Fetcher

markdown = Fetcher.get("https://example.com").markdown(main_content_only=True)
```

它适用于所有 Fetcher，因此也可以用一行代码获取受 Cloudflare 保护的页面：

```python
from scrapling.fetchers import StealthyFetcher

markdown = StealthyFetcher.fetch("https://protected.example.com", solve_cloudflare=True).markdown(main_content_only=True)
```

两个参数控制输出：

- `main_content_only`：只转换页面 `<body>` 标签内的内容。
- `css_selector`：只转换匹配 CSS 选择器的元素，并合并所有匹配结果。这样可以只提取处理流程需要的部分，节省 token：

```python
markdown = Fetcher.get("https://example.com/docs/page").markdown(css_selector="article")
```

无论传入什么参数，转换前都会移除脚本、样式和隐藏内容。这与 [MCP 服务器](mcp-server.md)保护 AI 智能体免受提示词注入时使用的清理方式相同。它会移除通过内联样式隐藏的元素、带有 `aria-hidden="true"` 的元素、隐藏的 slot、`<template>` 标签、HTML 注释和零宽字符。MCP 服务器在 `main_content_only=True` 时使用这套清理流程。

## 将整个网站转为 Markdown 文档集 {#a-whole-website-to-a-markdown-corpus}

`ContentSpider` 模板会爬取网站并转换每个页面。它基于 [Spider 框架](../spiders/architecture.md)，支持并发、AutoThrottle、robots.txt 规则，以及暂停和恢复功能：

```python
from scrapling.spiders import ContentSpider

class DocsSpider(ContentSpider):
    name = "docs"
    start_urls = ["https://example.com/docs/"]
    allowed_domains = {"example.com"}
    output_dir = "docs_markdown"
    max_pages = 200

result = DocsSpider().start()
result.items.to_jsonl("docs.jsonl")
```

每个爬取的页面都会生成一个数据项，包含 `url`、`title` 和 `markdown` 键。如果设置了 `output_dir`，每个页面还会保存为一个 Markdown 文件，文件名根据 URL 生成。因此，上面的示例会得到一个包含 `.md` 文件的文件夹，以及一个可直接导入的 `docs.jsonl`。

模板要求设置 `allowed_domains`，让爬取范围始终限制在目标网站内。可用选项如下：

- `css_selector` / `main_content_only`：每个页面都会将它们传给 `markdown()`，其中 `main_content_only` 默认启用。
- `output_dir`：设置后，每个页面都会写入一个 Markdown 文件。
- `max_pages`：最多转换的页面数。达到上限时，已排队的请求可能仍会执行，但对应页面不会转换。默认值 `0` 表示不限制。

默认会跟随 `allowed_domains` 内的所有页面链接。模板基于 [CrawlSpider](../spiders/generic-templates.md#crawlspider)，因此可以重写 `rules()`，使用自己的 [LinkExtractor](../spiders/generic-templates.md#linkextractor-reference) 控制爬取范围。`allow` 只保留需要的 URL 模式，`deny` 排除不需要的模式，例如登录页、标签列表页和打印版页面：

```python
from scrapling.spiders import CrawlRule, LinkExtractor, ContentSpider

class DocsSpider(ContentSpider):
    name = "docs"
    start_urls = ["https://example.com/"]
    allowed_domains = {"example.com"}

    def rules(self):
        return [CrawlRule(LinkExtractor(allow=r"/docs/", deny=[r"/docs/changelog/", r"\?print="]))]
```

`deny` 的优先级高于 `allow`。与其他 **CrawlSpider** 一样，规则还可以包含 `priority` 或 `process_request` 钩子。

## 将数据导入向量存储 {#feeding-a-vector-store}

JSONL 输出可以接入任何生成 embedding 的流程。下面是一个最小示例：

```python
import json

with open("docs.jsonl", encoding="utf-8") as f:
    for line in f:
        page = json.loads(line)
        for chunk in split_into_chunks(page["markdown"]):
            vector_store.add(text=chunk, metadata={"url": page["url"], "title": page["title"]})
```

在 Spider 中使用 `css_selector`，在文本分块前去掉重复的无关内容，避免后续再清理。embedding 中的噪声越少，检索效果就越好。

## 交互式方案 {#interactive-alternatives}

如果更喜欢通过对话抓取数据，[MCP 服务器](mcp-server.md)可以为 AI 聊天机器人提供同样的 Markdown 提取工具。[Agent Skill](agent-skill.md) 则能教会编程智能体自行编写这些代码。
