# Performance Benchmarks

Scrapling isn't just powerful—it's also blazing fast, and version 0.3 delivers exceptional performance improvements across all operations!

## Benchmark Results

### Text Extraction Speed Test (5000 nested elements)

| # |      Library      | Time (ms) | vs Scrapling | 
|---|:-----------------:|:---------:|:------------:|
| 1 |     Scrapling     |   1.88    |     1.0x     |
| 2 |   Parsel/Scrapy   |   1.96    |    1.043x    |
| 3 |     Raw Lxml      |   2.32    |    1.234x    |
| 4 |      PyQuery      |   20.2    |     ~11x     |
| 5 |    Selectolax     |   85.2    |     ~45x     |
| 6 |  MechanicalSoup   |  1305.84  |    ~695x     |
| 7 |   BS4 with Lxml   |  1307.92  |    ~696x     |
| 8 | BS4 with html5lib |  3336.28  |    ~1775x    |

### Element Similarity & Text Search Performance

Scrapling's adaptive element finding capabilities significantly outperform alternatives:

|   Library   | Time (ms) | vs Scrapling |
|-------------|:---------:|:------------:|
|  Scrapling  |   2.02    |     1.0x     |
| AutoScraper |   10.26   |    5.08x     |
