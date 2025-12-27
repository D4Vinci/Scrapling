# Performance Benchmarks

Scrapling isn't just powerful—it's also blazing fast, and the updates since version 0.3 have delivered exceptional performance improvements across all operations. The following benchmarks compare Scrapling's parser with other popular libraries.

## Benchmark Results

### Text Extraction Speed Test (5000 nested elements)

| # |      Library      | Time (ms) | vs Scrapling | 
|---|:-----------------:|:---------:|:------------:|
| 1 |     Scrapling     |   1.99    |     1.0x     |
| 2 |   Parsel/Scrapy   |   2.01    |    1.01x     |
| 3 |     Raw Lxml      |    2.5    |    1.256x    |
| 4 |      PyQuery      |   22.93   |    ~11.5x    |
| 5 |    Selectolax     |   80.57   |    ~40.5x    |
| 6 |   BS4 with Lxml   |  1541.37  |   ~774.6x    |
| 7 |  MechanicalSoup   |  1547.35  |   ~777.6x    |
| 8 | BS4 with html5lib |  3410.58  |   ~1713.9x   |

### Element Similarity & Text Search Performance

Scrapling's adaptive element finding capabilities significantly outperform alternatives:

| Library     | Time (ms) | vs Scrapling |
|-------------|:---------:|:------------:|
| Scrapling   |   2.46    |     1.0x     |
| AutoScraper |   13.3    |    5.407x    |
