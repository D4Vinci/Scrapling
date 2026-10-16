---
title: "Leistungstests für HTML-Parser: Scrapling und andere Bibliotheken"
description: "Vergleichen Sie Scrapling mit anderen Python-Bibliotheken beim Auswerten von HTML, Extrahieren von Text und Suchen ähnlicher Elemente."
---

# Leistungstests {#performance-benchmarks}

Scrapling zeichnet sich auch durch seine Geschwindigkeit aus. Diese Tests vergleichen seinen Parser mit anderen bekannten Bibliotheken.

### Geschwindigkeit der Textextraktion (5.000 verschachtelte Elemente) {#text-extraction-speed-test-5000-nested-elements}

| # | Bibliothek | Zeit (ms) | Im Vergleich zu Scrapling |
|---|:-----------------:|:---------:|:------------:|
| 1 |     Scrapling     |   1,99    |     1,0x     |
| 2 |   Parsel/Scrapy   |   2,06    |    1,035     |
| 3 |     Lxml allein      |   2,56    |    1,286     |
| 4 |      PyQuery      |   23,98   |     ~12x     |
| 5 |    Selectolax     |  197,02   |     ~99x     |
| 6 |  MechanicalSoup   |  1545,15  |   ~776,5x    |
| 7 |   BS4 mit Lxml   |  1562,1  |   ~785,0x    |
| 8 | BS4 mit html5lib |  3412,73  |   ~1714,9x   |


### Suche nach ähnlichen Elementen und Text {#element-similarity-text-search-performance}

Die adaptive Elementsuche von Scrapling ist schneller als die Alternativen:

| Bibliothek | Zeit (ms) | Im Vergleich zu Scrapling |
|-------------|:---------:|:------------:|
| Scrapling   |   2,3    |     1,0x     |
| AutoScraper |   12,58   |    5,47x    |

> Jedes Ergebnis ist der Durchschnitt aus 100 gemessenen Durchläufen. Die Methode steht in [benchmarks.py](https://github.com/D4Vinci/Scrapling/blob/main/benchmarks.py).
