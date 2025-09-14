# Performance Benchmarks

Scrapling isn't just powerful—it's also blazing fast, and the updates since version 0.3 deliver exceptional performance improvements across all operations!

## Benchmark Results

### Text Extraction Speed Test (5000 nested elements)

| # |      Library      | Time (ms) | vs Scrapling | 
|---|:-----------------:|:---------:|:------------:|
| 1 |     Scrapling     |   1.92    |     1.0x     |
| 2 |   Parsel/Scrapy   |   1.99    |    1.036x    |
| 3 |     Raw Lxml      |   2.33    |    1.214x    |
| 4 |      PyQuery      |   20.61   |     ~11x     |
| 5 |    Selectolax     |   80.65   |     ~42x     |
| 6 |   BS4 with Lxml   |  1283.21  |    ~698x     |
| 7 |  MechanicalSoup   |  1304.57  |    ~679x     |
| 8 | BS4 with html5lib |  3331.96  |    ~1735x    |

### Element Similarity & Text Search Performance

Scrapling's adaptive element finding capabilities significantly outperform alternatives:

|   Library   | Time (ms) | vs Scrapling |
|-------------|:---------:|:------------:|
|  Scrapling  |   1.87    |     1.0x     |
| AutoScraper |   10.24   |    5.476x    |
