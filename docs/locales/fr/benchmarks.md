---
title: "Tests de performance des parsers HTML : Scrapling et autres bibliothèques"
description: "Comparez Scrapling à d’autres bibliothèques Python pour l’analyse HTML, l’extraction de texte et la recherche d’éléments similaires."
---

# Tests de performance {#performance-benchmarks}

Scrapling se distingue aussi par sa vitesse. Ces tests comparent son parser à d’autres bibliothèques connues.

### Vitesse d’extraction du texte (5 000 éléments imbriqués) {#text-extraction-speed-test-5000-nested-elements}

| # | Bibliothèque | Temps (ms) | Par rapport à Scrapling |
|---|:-----------------:|:---------:|:------------:|
| 1 |     Scrapling     |   1,99    |     1,0x     |
| 2 |   Parsel/Scrapy   |   2,06    |    1,035     |
| 3 |     Lxml seul      |   2,56    |    1,286     |
| 4 |      PyQuery      |   23,98   |     ~12x     |
| 5 |    Selectolax     |  197,02   |     ~99x     |
| 6 |  MechanicalSoup   |  1545,15  |   ~776,5x    |
| 7 |   BS4 avec Lxml   |  1562,1  |   ~785,0x    |
| 8 | BS4 avec html5lib |  3412,73  |   ~1714,9x   |


### Recherche d’éléments similaires et de texte {#element-similarity-text-search-performance}

La recherche adaptative d’éléments de Scrapling est plus rapide que les autres solutions :

| Bibliothèque | Temps (ms) | Par rapport à Scrapling |
|-------------|:---------:|:------------:|
| Scrapling   |   2,3    |     1,0x     |
| AutoScraper |   12,58   |    5,47x    |

> Chaque résultat est la moyenne de 100 exécutions chronométrées. Consultez [benchmarks.py](https://github.com/D4Vinci/Scrapling/blob/main/benchmarks.py) pour connaître la méthode.
