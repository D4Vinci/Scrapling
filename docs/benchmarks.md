# Performance Benchmarks

Scrapling isn't just powerful - it's also blazing fast. The following benchmarks compare Scrapling's parser with the latest versions of other popular libraries.

### Text Extraction Speed Test (5000 nested elements)

| # |      Library      | Time (ms) | vs Scrapling | 
|---|:-----------------:|:---------:|:------------:|
| 1 |     Scrapling     |   1.98    |     1.0x     |
| 2 |   Parsel/Scrapy   |   1.99    |    1.005     |
| 3 |     Raw Lxml      |   2.48    |    1.253     |
| 4 |      PyQuery      |   23.15   |     ~12x     |
| 5 |    Selectolax     |  196.09   |     ~99x     |
| 6 |  MechanicalSoup   |  1531.24  |   ~773.4x    |
| 7 |   BS4 with Lxml   |  1535.19  |   ~775.3x    |
| 8 | BS4 with html5lib |  3388.16  |   ~1711.2x   |


### Element Similarity & Text Search Performance

Scrapling's adaptive element finding capabilities significantly outperform alternatives:

| Library     | Time (ms) | vs Scrapling |
|-------------|:---------:|:------------:|
| Scrapling   |   2.29    |     1.0x     |
| AutoScraper |   12.46   |    5.441x    |

> All benchmarks represent averages of 100+ runs. See [benchmarks.py](https://github.com/D4Vinci/Scrapling/blob/main/benchmarks.py) for methodology.
