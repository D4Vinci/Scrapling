---
title: "Testes de desempenho de parsers HTML: Scrapling e outras bibliotecas"
description: "Compare o desempenho do Scrapling na análise de HTML, extração de texto e busca de elementos semelhantes com outras bibliotecas Python."
---

# Testes de desempenho {#performance-benchmarks}

Scrapling também se destaca pela velocidade. Estes testes comparam seu parser com outras bibliotecas conhecidas.

### Velocidade de extração de texto (5.000 elementos aninhados) {#text-extraction-speed-test-5000-nested-elements}

| # | Biblioteca | Tempo (ms) | Comparação com Scrapling |
|---|:-----------------:|:---------:|:------------:|
| 1 |     Scrapling     |   1,99    |     1,0x     |
| 2 |   Parsel/Scrapy   |   2,06    |    1,035     |
| 3 |     Lxml puro      |   2,56    |    1,286     |
| 4 |      PyQuery      |   23,98   |     ~12x     |
| 5 |    Selectolax     |  197,02   |     ~99x     |
| 6 |  MechanicalSoup   |  1545,15  |   ~776,5x    |
| 7 |   BS4 com Lxml   |  1562,1  |   ~785,0x    |
| 8 | BS4 com html5lib |  3412,73  |   ~1714,9x   |


### Desempenho da busca de elementos semelhantes e de texto {#element-similarity-text-search-performance}

A busca adaptativa de elementos do Scrapling é mais rápida que as alternativas:

| Biblioteca | Tempo (ms) | Comparação com Scrapling |
|-------------|:---------:|:------------:|
| Scrapling   |   2,3    |     1,0x     |
| AutoScraper |   12,58   |    5,47x    |

> Cada resultado é a média de 100 execuções medidas. Veja o método em [benchmarks.py](https://github.com/D4Vinci/Scrapling/blob/main/benchmarks.py).
