---
title: "HTML パーサーの速度比較：Scrapling と他の Python ライブラリ"
description: "HTML 解析、テキスト抽出、類似要素検索で、Scrapling と他の Python ライブラリの性能を比較します。"
---

# 性能テスト {#performance-benchmarks}

Scrapling は処理速度も重視しています。以下では、そのパーサーと他のよく使われるライブラリを比較します。

### テキスト抽出の速度（5,000 個の入れ子の要素） {#text-extraction-speed-test-5000-nested-elements}

| # | ライブラリ | 時間（ミリ秒） | Scrapling との比較 |
|---|:-----------------:|:---------:|:------------:|
| 1 |     Scrapling     |   1.99    |     1.0x     |
| 2 |   Parsel/Scrapy   |   2.06    |    1.035     |
| 3 |     Lxml 単体      |   2.56    |    1.286     |
| 4 |      PyQuery      |   23.98   |     ~12x     |
| 5 |    Selectolax     |  197.02   |     ~99x     |
| 6 |  MechanicalSoup   |  1545.15  |   ~776.5x    |
| 7 |   BS4 + Lxml   |  1562.1  |   ~785.0x    |
| 8 | BS4 + html5lib |  3412.73  |   ~1714.9x   |


### 類似要素とテキストの検索 {#element-similarity-text-search-performance}

Scrapling の適応型の要素検索は、他の方法より高速です。

| ライブラリ | 時間（ミリ秒） | Scrapling との比較 |
|-------------|:---------:|:------------:|
| Scrapling   |   2.3    |     1.0x     |
| AutoScraper |   12.58   |    5.47x    |

> 各結果は、100 回の測定の平均です。測定方法は [benchmarks.py](https://github.com/D4Vinci/Scrapling/blob/main/benchmarks.py) をご覧ください。
