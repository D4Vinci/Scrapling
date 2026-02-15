# Performance Benchmarks

Scrapling isn't just powerful—it's also blazing fast. The following benchmarks compare Scrapling's parser with the latest versions of other popular libraries.

### Text Extraction Speed Test (5000 nested elements)

| # |      Library      | Time (ms) | vs Scrapling | 
|---|:-----------------:|:---------:|:------------:|
| 1 |     Scrapling     |   2.02    |     1.0x     |
| 2 |   Parsel/Scrapy   |   2.04    |     1.01     |
| 3 |     Raw Lxml      |   2.54    |    1.257     |
| 4 |      PyQuery      |   24.17   |     ~12x     |
| 5 |    Selectolax     |   82.63   |     ~41x     |
| 6 |  MechanicalSoup   |  1549.71  |   ~767.1x    |
| 7 |   BS4 with Lxml   |  1584.31  |   ~784.3x    |
| 8 | BS4 with html5lib |  3391.91  |   ~1679.1x   |


### Element Similarity & Text Search Performance

Scrapling's adaptive element finding capabilities significantly outperform alternatives:

| Library     | Time (ms) | vs Scrapling |
|-------------|:---------:|:------------:|
| Scrapling   |   2.39    |     1.0x     |
| AutoScraper |   12.45   |    5.209x    |

> All benchmarks represent averages of 100+ runs. See [benchmarks.py](https://github.com/D4Vinci/Scrapling/blob/main/benchmarks.py) for methodology.
