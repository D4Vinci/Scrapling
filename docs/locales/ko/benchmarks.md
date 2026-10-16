---
title: "Python HTML 파서 성능 비교: Scrapling과 다른 라이브러리"
description: "HTML 파싱, 텍스트 추출, 비슷한 요소 찾기에서 Scrapling과 다른 Python 라이브러리의 성능을 비교합니다."
---

# 성능 테스트 {#performance-benchmarks}

Scrapling은 강력할 뿐 아니라 매우 빠릅니다. 다음 테스트는 Scrapling 파서와 널리 쓰이는 다른 라이브러리를 비교합니다.

### 텍스트 추출 속도: 중첩 요소 5,000개 {#text-extraction-speed-test-5000-nested-elements}

| # | 라이브러리 | 시간(ms) | Scrapling 대비 |
|---|:-----------------:|:---------:|:------------:|
| 1 |     Scrapling     |   1.99    |     1.0x     |
| 2 |   Parsel/Scrapy   |   2.06    |    1.035     |
| 3 |     Lxml 단독      |   2.56    |    1.286     |
| 4 |      PyQuery      |   23.98   |     ~12x     |
| 5 |    Selectolax     |  197.02   |     ~99x     |
| 6 |  MechanicalSoup   |  1545.15  |   ~776.5x    |
| 7 |   BS4 + Lxml   |  1562.1  |   ~785.0x    |
| 8 | BS4 + html5lib |  3412.73  |   ~1714.9x   |


### 비슷한 요소 찾기와 텍스트 검색 {#element-similarity-text-search-performance}

Scrapling의 적응형 요소 검색은 다른 방법보다 훨씬 빠릅니다:

| 라이브러리 | 시간(ms) | Scrapling 대비 |
|-------------|:---------:|:------------:|
| Scrapling   |   2.3    |     1.0x     |
| AutoScraper |   12.58   |    5.47x    |

> 각 결과는 시간을 측정한 100회 실행의 평균입니다. 측정 방법은 [benchmarks.py](https://github.com/D4Vinci/Scrapling/blob/main/benchmarks.py)를 확인하세요.
