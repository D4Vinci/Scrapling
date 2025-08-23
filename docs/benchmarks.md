Scrapling isn't just powerful - it's also blazing fast. Scrapling implements many best practices, design patterns, and numerous optimizations to save fractions of seconds. All of that while focusing exclusively on parsing HTML documents.

Here are benchmarks comparing Scrapling's parsing speed to popular Python libraries in two tests. 

### Text Extraction Speed Test

This test consists of extracting the text content of 5000 nested div elements.

Here are the results comparing Scrapling to all well-known parsing libraries:


| # |      Library      | Time (ms) | vs Scrapling | 
|---|:-----------------:|:---------:|:------------:|
| 1 |     Scrapling     |   5.44    |     1.0x     |
| 2 |   Parsel/Scrapy   |   5.53    |    1.017x    |
| 3 |     Raw Lxml      |   6.76    |    1.243x    |
| 4 |      PyQuery      |   21.96   |    4.037x    |
| 5 |    Selectolax     |   67.12   |   12.338x    |
| 6 |   BS4 with Lxml   |  1307.03  |   240.263x   |
| 7 |  MechanicalSoup   |  1322.64  |   243.132x   |
| 8 | BS4 with html5lib |  3373.75  |   620.175x   |

As you see, Scrapling is on par with Scrapy and slightly faster than Lxml, which both libraries are built on top of. These are the closest results to Scrapling. PyQuery is also built on top of Lxml, but Scrapling is four times faster.

### Extraction By Text Speed Test

Scrapling can find elements based on its text content and find elements similar to these elements. The only known library with these two features, too, is AutoScraper.

So, we compared this to see how fast Scrapling can be in these two tasks compared to AutoScraper.

Here are the results:

|   Library   | Time (ms) | vs Scrapling |
|-------------|:---------:|:------------:|
|  Scrapling  |   2.51    |     1.0x     |
| AutoScraper |   11.41   |    4.546x    |

Scrapling can find elements with more methods and returns the entire element's `Adaptor` object, not only text like AutoScraper. So, to make this test fair, both libraries will extract an element with text, find similar elements, and then extract the text content for all of them. 

As you see, Scrapling is still 4.5 times faster at the same task. 

If we made Scrapling extract the elements only without stopping to extract each element's text, we would get speed twice as fast as this, but as I said, to make it fair comparison a bit :smile:

> All benchmarks' results are an average of 100 runs. See our [benchmarks.py](https://github.com/D4Vinci/Scrapling/blob/main/benchmarks.py) for methodology and to run your comparisons.