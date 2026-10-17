---
title: "Pruebas de rendimiento de parsers HTML: Scrapling y otras bibliotecas"
description: "Compara el rendimiento de Scrapling al analizar HTML, extraer texto y buscar elementos similares con otras bibliotecas de Python."
---

# Pruebas de rendimiento {#performance-benchmarks}

Scrapling también destaca por su velocidad. Estas pruebas comparan su parser con otras bibliotecas conocidas.

### Velocidad de extracción de texto (5000 elementos anidados) {#text-extraction-speed-test-5000-nested-elements}

| # | Biblioteca | Tiempo (ms) | Frente a Scrapling |
|---|:-----------------:|:---------:|:------------:|
| 1 |     Scrapling     |   1,99    |     1,0x     |
| 2 |   Parsel/Scrapy   |   2,06    |    1,035     |
| 3 |     Raw Lxml      |   2,56    |    1,286     |
| 4 |      PyQuery      |   23,98   |     ~12x     |
| 5 |    Selectolax     |  197,02   |     ~99x     |
| 6 |  MechanicalSoup   |  1545,15  |   ~776,5x    |
| 7 |   BS4 with Lxml   |  1562,1  |   ~785,0x    |
| 8 | BS4 with html5lib |  3412,73  |   ~1714,9x   |


### Rendimiento de similitud de elementos y búsqueda de texto {#element-similarity-text-search-performance}

La búsqueda adaptativa de elementos de Scrapling es más rápida que las alternativas:

| Biblioteca | Tiempo (ms) | Frente a Scrapling |
|-------------|:---------:|:------------:|
| Scrapling   |   2,3    |     1,0x     |
| AutoScraper |   12,58   |    5,47x    |

> Cada resultado es el promedio de 100 ejecuciones medidas. Consulta [benchmarks.py](https://github.com/D4Vinci/Scrapling/blob/main/benchmarks.py) para ver el método.
