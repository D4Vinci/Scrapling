---
title: "可靠网页抓取的免费 AI 替代方案"
description: "Scrapling 可以应对页面变化、不稳定的选择器、反爬保护和分页，无需为每个页面调用 LLM。"
---

# Scrapling：可靠网页抓取的免费 AI 替代方案 {#scrapling-a-free-alternative-to-ai-for-robust-web-scraping}

网页抓取长期用于提取数据、建立索引和准备数据集等任务。但有经验的用户仍会遇到一些反复出现的问题，影响工作效率。最近，越来越多人开始使用 AI 抓取网页，因为它有望解决其中一些难题。

本文会介绍这些常见问题、企业转向 AI 的原因、这种方案的不足，以及 Scrapling 如何在无需承担 AI 成本的情况下提供帮助。

## 常见问题和更难的目标 {#common-issues-and-challenging-goals}

如果做过一段时间网页抓取，应该遇到过这些问题：

1. **网站结构经常变化**：网站会更新 DOM，导致固定的 XPath 或 CSS 选择器失效。
2. **选择器不稳定**：类名和 ID 经常变化，或使用随机值，导致抓取代码失效或更难编写。
3. **反爬措施越来越复杂**：CAPTCHA、浏览器指纹和行为分析让传统抓取方式更难奏效。

还有其他问题。即便只针对已知网站抓取、可以为每个网站编写专用代码，也会遇到这些情况。

如果目标更大，要从许多不同的网站抓取数据，也就是常说的 Broad Scraping 或 Generic Web Scraping，上述问题会更严重，还会出现新的难题：

1. **网站差异很大**：通用抓取程序要处理各种 HTML 结构、CSS 用法、JavaScript 框架和后端技术。
2. **识别有用数据**：面对从未见过的页面，抓取程序怎么知道哪些数据重要？
3. **分页方式不同**：无限滚动、传统分页和“加载更多”按钮，都需要不同的处理方法。

问题还不止这些。如何手动解决？这里说的是没有共同技术基础的不同网站。

## AI 能帮忙，但成本很高 {#ai-to-the-rescue-but-at-a-high-cost}

AI 能理解页面源码，找出需要的字段，或者为它们生成选择器，因此可以解决很多问题。当然，这要建立在已经使用其他工具处理好反爬保护的前提下 :)

我很喜欢这种方案，也觉得 AI，尤其是生成式 AI，很有意思。可能需要花很多时间编写和调整提示词。如果可以接受这一点，很快就会遇到这个场景中使用 AI 的真正问题。

很多页面包含大量内容，需要以某种方式传给 AI。这样会快速消耗 token，费用也会不断增加。

除非完全不在意预算，否则就会开始寻找更便宜的方案。这正是 Scrapling 能帮忙的地方 :smile:

## Scrapling 可以帮忙 {#scrapling-got-you-covered}

Scrapling 可以处理网页抓取中几乎所有常见问题，接下来的更新还会逐步覆盖其余情况。

### 解决 T1：网站结构经常变化 {#solving-issue-t1-rapidly-changing-website-structures}

这就是 [adaptive](../parsing/adaptive.md) 功能存在的原因。没错，还是要讲到它 :)

启用 `adaptive` 后，可以保存元素的特有属性。即使网站结构改变，也能在之后重新找到它。困难在于，元素的任何部分都可能变化，不一定有稳定属性可依赖。

这项功能会保存元素的全部特征。网站结构变化后，它返回与原元素相似度最高的元素。

我已经通过多个示例详细介绍过它，可以[在这里继续阅读](../parsing/adaptive.md#how-the-adaptive-scraping-feature-works)。

### 解决 T2：选择器不稳定 {#solving-issue-t2-unstable-selectors}

如果做过较长时间网页抓取，可能遇到过这样的页面：只有原始 HTML，没有 ID 或类名；类名随机生成；或者没有其他稳定特征可以用来选择元素。

此时，传统的 CSS 或 XPath 选择器不一定是最佳方案。因此，Scrapling 提供了另外三种选择方式：

1. [按元素内容选择](../parsing/selection.md#text-content-selection)：用 `find_by_text` 查找文本，或用 `find_by_regex` 通过正则表达式匹配文本。
2. [选择与另一元素相似的元素](../parsing/selection.md#finding-similar-elements)：先找到一个元素，其余交给 Scrapling。
3. [按条件筛选元素](../parsing/selection.md#filters-based-searching)：指定元素需要满足的条件或过滤规则，让 Scrapling 来查找。

打开这些链接，就能了解各个场景的处理方式。

### 解决 T3：反爬措施越来越复杂 {#solving-issue-t3-increasingly-complex-anti-bot-measures}

面对受保护的网站，仅靠代理和模拟人的操作可能不够。[StealthyFetcher](../fetching/stealthy.md) 将浏览器自动化、指纹调整和反爬处理选项结合起来。启用 `solve_cloudflare=True`，即可处理 Cloudflare Turnstile 和 Interstitial 验证。

### 解决 B1 和 B2：网站差异与有用数据识别 {#solving-issues-b1-b2-extreme-website-diversity-identifying-relevant-data}

这个问题很难，但 Scrapling 的灵活性让它有了解法。

我曾和一位用户交流，他用 AI 从不同网站提取价格。他只关心价格和标题，所以让 AI 帮他定位价格。

我告诉他，这里不一定需要 AI，并给出了这个示例：
```python
price_element = page.find_by_regex(r'£[\d\.,]+', first_match=True)  # Get the first element that contains a text that matches price regex eg. £10.50
# If you want the container/element that contains the price element
price_element_container = price_element.parent or price_element.find_ancestor(lambda ancestor: ancestor.has_class('product'))  # or other methods...
target_element_selector = price_element_container.generate_css_selector or price_element_container.generate_full_css_selector # or xpath
```
他又问，如果是下面这种情况呢：
```html
<span class='currency'> $ </span> <span class='a-price'> 45,000 </span>
```
于是我调整了代码：
```python
price_element_container = page.find_by_regex(r'[\d,]+', first_match=True).parent # Adjusted the regex for this example
full_price_data = price_element_container.get_all_text(separator="", strip=True)  # Returns '$45,000' in this case
```
这些代码已经满足了他的需求。可以先尝试第一个正则表达式，找不到结果再换下一个。先覆盖最常见的模式，再逐步覆盖其他模式。
这可能有些繁琐，但比 AI 便宜得多。

这个例子想说明的是：不是所有问题都需要 AI。有时换一种思路，就能节省很多费用。

### 解决 B3：分页方式不同 {#solving-issue-b3-pagination-variations}

Scrapling 目前没有直接自动识别分页链接的方法。它的 Spider 使用 `response.follow()` 跟随分页链接。

不过，只要查找常见模式，就能覆盖很多网站。例如 `page.find_by_text('Next')['href']`、`page.find_by_text('load more')['href']`，或 `'a[href*="?page="]'`、`'a[href*="/page/"]'` 这样的选择器。思路就是如此。

## 成本对比与节省 {#cost-comparison-and-savings}

下面是一个简单对比：

| 方面 | Scrapling | AI 工具，例如 Browse AI、Oxylabs |
|---|---|---|
| 成本 | 免费，使用库不按次数收费 | 付费套餐，价格取决于服务商和用量 |
| 设置 | 需要少量技术知识和手动设置 | 通常无需代码，对非技术用户更简单 |
| 使用方式 | 代码、终端或 MCP 服务器 | 通常是图形界面或 API，取决于服务商提供的方案 |
| 扩展到大规模 | 取决于用户的实现 | 托管服务内置大规模处理支持 |
| 适应变化 | 依靠 `adaptive` 和无需 CSS/XPath 选择器的方法，适应性强 | AI 自动处理，适应性强，但频繁变化时费用较高 |

最新价格请参阅 [Browse AI](https://www.browse.ai/pricing) 和 [Oxylabs Web Scraper API](https://oxylabs.io/products/scraper-api/web/pricing)。

## 总结 {#conclusion}

AI 功能强大，但费用可能超出许多网页抓取任务的预算。Scrapling 提供可靠、灵活且低成本的工具，既能针对已知网站抓取，也能应对多种不同网站，往往可以避免使用昂贵的 AI 方案。借助 `adaptive`、多种选择方法和高级 Fetcher，可以更高效地编写能应对变化的抓取程序。

继续阅读文档，看看 Scrapling 如何简化接下来的网页抓取项目！
