---
title: "HTML 解析器性能测试：Scrapling 与其他库"
description: "对比 Scrapling 和其他 Python 库在 HTML 解析、文本提取和相似元素搜索中的性能。"
---

# 性能测试 {#performance-benchmarks}

Scrapling 的速度也很出色。下面对比它的解析器和其他常用库。

### 文本提取速度（5,000 个嵌套元素） {#text-extraction-speed-test-5000-nested-elements}

| # | 库 | 时间（毫秒） | 相对 Scrapling |
|---|:-----------------:|:---------:|:------------:|
| 1 |     Scrapling     |   1.99    |     1.0x     |
| 2 |   Parsel/Scrapy   |   2.06    |    1.035     |
| 3 |     原生 Lxml      |   2.56    |    1.286     |
| 4 |      PyQuery      |   23.98   |     ~12x     |
| 5 |    Selectolax     |  197.02   |     ~99x     |
| 6 |  MechanicalSoup   |  1545.15  |   ~776.5x    |
| 7 |   BS4 + Lxml   |  1562.1  |   ~785.0x    |
| 8 | BS4 + html5lib |  3412.73  |   ~1714.9x   |


### 相似元素和文本搜索 {#element-similarity-text-search-performance}

Scrapling 的自适应元素查找比其他方案更快：

| 库 | 时间（毫秒） | 相对 Scrapling |
|-------------|:---------:|:------------:|
| Scrapling   |   2.3    |     1.0x     |
| AutoScraper |   12.58   |    5.47x    |

> 每项结果都是 100 次测量的平均值。测试方法见 [benchmarks.py](https://github.com/D4Vinci/Scrapling/blob/main/benchmarks.py)。
