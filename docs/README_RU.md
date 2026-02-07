<p align=center>
  <br>
  <a href="https://scrapling.readthedocs.io/en/latest/" target="_blank"><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/poster.png" style="width: 50%; height: 100%;" alt="main poster"/></a>
  <br>
  <i><code>Простой, легкий веб-скрапинг, каким он и должен быть!</code></i>
</p>
<p align="center">
    <a href="https://github.com/D4Vinci/Scrapling/actions/workflows/tests.yml" alt="Tests">
        <img alt="Tests" src="https://github.com/D4Vinci/Scrapling/actions/workflows/tests.yml/badge.svg"></a>
    <a href="https://badge.fury.io/py/Scrapling" alt="PyPI version">
        <img alt="PyPI version" src="https://badge.fury.io/py/Scrapling.svg"></a>
    <a href="https://pepy.tech/project/scrapling" alt="PyPI Downloads">
        <img alt="PyPI Downloads" src="https://static.pepy.tech/personalized-badge/scrapling?period=total&units=INTERNATIONAL_SYSTEM&left_color=GREY&right_color=GREEN&left_text=Downloads"></a>
    <br/>
    <a href="https://discord.gg/EMgGbDceNQ" alt="Discord" target="_blank">
      <img alt="Discord" src="https://img.shields.io/discord/1360786381042880532?style=social&logo=discord&link=https%3A%2F%2Fdiscord.gg%2FEMgGbDceNQ">
    </a>
    <a href="https://x.com/Scrapling_dev" alt="X (formerly Twitter)">
      <img alt="X (formerly Twitter) Follow" src="https://img.shields.io/twitter/follow/Scrapling_dev?style=social&logo=x&link=https%3A%2F%2Fx.com%2FScrapling_dev">
    </a>
    <br/>
    <a href="https://pypi.org/project/scrapling/" alt="Supported Python versions">
        <img alt="Supported Python versions" src="https://img.shields.io/pypi/pyversions/scrapling.svg"></a>
</p>

<p align="center">
    <a href="https://scrapling.readthedocs.io/en/latest/parsing/selection/">
        Методы выбора
    </a>
    ·
    <a href="https://scrapling.readthedocs.io/en/latest/fetching/choosing/">
        Выбор фетчера
    </a>
    ·
    <a href="https://scrapling.readthedocs.io/en/latest/cli/overview/">
        CLI
    </a>
    ·
    <a href="https://scrapling.readthedocs.io/en/latest/ai/mcp-server/">
        Режим MCP
    </a>
    ·
    <a href="https://scrapling.readthedocs.io/en/latest/tutorials/migrating_from_beautifulsoup/">
        Миграция с Beautifulsoup
    </a>
</p>

**Прекратите бороться с анти-ботовыми системами. Прекратите переписывать селекторы после каждого обновления сайта.**

Scrapling - это не просто очередная библиотека для веб-скрапинга. Это первая **адаптивная** библиотека для скрапинга, которая учится на изменениях сайтов и развивается вместе с ними. В то время как другие библиотеки ломаются, когда сайты обновляют свою структуру, Scrapling автоматически перемещает ваши элементы и поддерживает работу ваших скраперов.

Созданный для современного веба, Scrapling имеет **собственный быстрый движок парсинга** и фетчеры для решения всех задач веб-скрапинга, с которыми вы сталкиваетесь или столкнетесь. Созданный веб-скраперами для веб-скраперов и обычных пользователей, здесь есть что-то для каждого.

```python
>> from scrapling.fetchers import Fetcher, AsyncFetcher, StealthyFetcher, DynamicFetcher
>> StealthyFetcher.adaptive = True
# Получайте исходный код сайтов незаметно!
>> page = StealthyFetcher.fetch('https://example.com', headless=True, network_idle=True)
>> print(page.status)
200
>> products = page.css('.product', auto_save=True)  # Скрапьте данные, которые переживут изменения дизайна сайта!
>> # Позже, если структура сайта изменится, передайте `adaptive=True`
>> products = page.css('.product', adaptive=True)  # и Scrapling все равно их найдет!
```

# Спонсоры 

<!-- sponsors -->

<a href="https://www.scrapeless.com/en?utm_source=official&utm_term=scrapling" target="_blank" title="Effortless Web Scraping Toolkit for Business and Developers"><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/scrapeless.jpg"></a>
<a href="https://www.thordata.com/?ls=github&lk=github" target="_blank" title="Unblockable proxies and scraping infrastructure, delivering real-time, reliable web data to power AI models and workflows."><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/thordata.jpg"></a>
<a href="https://evomi.com?utm_source=github&utm_medium=banner&utm_campaign=d4vinci-scrapling" target="_blank" title="Evomi is your Swiss Quality Proxy Provider, starting at $0.49/GB"><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/evomi.png"></a>
<a href="https://serpapi.com/?utm_source=scrapling" target="_blank" title="Scrape Google and other search engines with SerpApi"><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/SerpApi.png"></a>
<a href="https://visit.decodo.com/Dy6W0b" target="_blank" title="Try the Most Efficient Residential Proxies for Free"><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/decodo.png"></a>
<a href="https://petrosky.io/d4vinci" target="_blank" title="PetroSky delivers cutting-edge VPS hosting."><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/petrosky.png"></a>
<a href="https://hasdata.com/?utm_source=github&utm_medium=banner&utm_campaign=D4Vinci" target="_blank" title="The web scraping service that actually beats anti-bot systems!"><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/hasdata.png"></a>
<a href="https://hypersolutions.co/?utm_source=github&utm_medium=readme&utm_campaign=scrapling" target="_blank" title="Bot Protection Bypass API for Akamai, DataDome, Incapsula & Kasada"><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/HyperSolutions.png"></a>
<a href="https://www.swiftproxy.net/" target="_blank" title="Unlock Reliable Proxy Services with Swiftproxy!"><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/swiftproxy.png"></a>
<a href="https://www.rapidproxy.io/?ref=d4v" target="_blank" title="Affordable Access to the Proxy World – bypass CAPTCHAs blocks, and avoid additional costs."><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/rapidproxy.jpg"></a>
<a href="https://browser.cash/?utm_source=D4Vinci&utm_medium=referral" target="_blank" title="Browser Automation & AI Browser Agent Platform"><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/browserCash.png"></a>

<!-- /sponsors -->

<i><sub>Хотите показать здесь свою рекламу? Нажмите [здесь](https://github.com/sponsors/D4Vinci) и выберите подходящий вам уровень!</sub></i>

---

## Ключевые особенности

### Продвинутая загрузка сайтов с поддержкой сессий
- **HTTP-запросы**: Быстрые и скрытные HTTP-запросы с классом `Fetcher`. Может имитировать TLS-отпечаток браузера, заголовки и использовать HTTP3.
- **Динамическая загрузка**: Загрузка динамических сайтов с полной автоматизацией браузера через класс `DynamicFetcher`, поддерживающий Chromium от Playwright и Google Chrome.
- **Обход анти-ботов**: Расширенные возможности скрытности с `StealthyFetcher` и подмену отпечатков. Может легко обойти все типы Turnstile/Interstitial от Cloudflare с помощью автоматизации.
- **Управление сессиями**: Поддержка постоянных сессий с классами `FetcherSession`, `StealthySession` и `DynamicSession` для управления cookie и состоянием между запросами.
- **Поддержка асинхронности**: Полная асинхронная поддержка во всех фетчерах и выделенных асинхронных классах сессий.

### Адаптивный скрапинг и интеграция с ИИ
- 🔄 **Умное отслеживание элементов**: Перемещайте элементы после изменений сайта с помощью интеллектуальных алгоритмов подобия.
- 🎯 **Умный гибкий выбор**: CSS-селекторы, XPath-селекторы, поиск на основе фильтров, текстовый поиск, поиск по регулярным выражениям и многое другое.
- 🔍 **Поиск похожих элементов**: Автоматически находите элементы, похожие на найденные элементы.
- 🤖 **MCP-сервер для использования с ИИ**: Встроенный MCP-сервер для веб-скрапинга с помощью ИИ и извлечения данных. MCP-сервер обладает мощными, пользовательскими возможностями, которые используют Scrapling для извлечения целевого контента перед передачей его ИИ (Claude/Cursor/и т.д.), тем самым ускоряя операции и снижая затраты за счет минимизации использования токенов. ([демо-видео](https://www.youtube.com/watch?v=qyFk3ZNwOxE))

### Высокопроизводительная и проверенная в боях архитектура
- 🚀 **Молниеносно быстро**: Оптимизированная производительность превосходит большинство библиотек скрапинга Python.
- 🔋 **Эффективное использование памяти**: Оптимизированные структуры данных и ленивая загрузка для минимального потребления памяти.
- ⚡ **Быстрая сериализация JSON**: В 10 раз быстрее, чем стандартная библиотека.
- 🏗️ **Проверено в боях**: Scrapling имеет не только 92% покрытия тестами и полное покрытие type hints, но и ежедневно использовался сотнями веб-скраперов в течение последнего года.

### Удобный для разработчиков/веб-скраперов опыт
- 🎯 **Интерактивная оболочка веб-скрапинга**: Опциональная встроенная оболочка IPython с интеграцией Scrapling, ярлыками и новыми инструментами для ускорения разработки скриптов веб-скрапинга, такими как преобразование curl-запросов в Scrapling-запросы и просмотр результатов запросов в вашем браузере.
- 🚀 **Используйте прямо из терминала**: При желании вы можете использовать Scrapling для скрапинга URL без написания ни одной строки кода!
- 🛠️ **Богатый API навигации**: Расширенный обход DOM с методами навигации по родителям, братьям и детям.
- 🧬 **Улучшенная обработка текста**: Встроенные регулярные выражения, методы очистки и оптимизированные операции со строками.
- 📝 **Автоматическая генерация селекторов**: Генерация надежных CSS/XPath селекторов для любого элемента.
- 🔌 **Знакомый API**: Похож на Scrapy/BeautifulSoup с теми же псевдоэлементами, используемыми в Scrapy/Parsel.
- 📘 **Полное покрытие типами**: Полные подсказки типов для отличной поддержки IDE и автодополнения кода.
- 🔋 **Готовый Docker-образ**: С каждым релизом автоматически создается и отправляется Docker-образ, содержащий все браузеры.

## Начало работы

### Базовое использование
```python
from scrapling.fetchers import Fetcher, StealthyFetcher, DynamicFetcher
from scrapling.fetchers import FetcherSession, StealthySession, DynamicSession

# HTTP-запросы с поддержкой сессий
with FetcherSession(impersonate='chrome') as session:  # Используйте последнюю версию TLS-отпечатка Chrome
    page = session.get('https://quotes.toscrape.com/', stealthy_headers=True)
    quotes = page.css('.quote .text::text')

# Или используйте одноразовые запросы
page = Fetcher.get('https://quotes.toscrape.com/')
quotes = page.css('.quote .text::text')

# Расширенный режим скрытности (Держите браузер открытым до завершения)
with StealthySession(headless=True, solve_cloudflare=True) as session:
    page = session.fetch('https://nopecha.com/demo/cloudflare', google_search=False)
    data = page.css('#padded_content a')

# Или используйте стиль одноразового запроса, открывает браузер для этого запроса, затем закрывает его после завершения
page = StealthyFetcher.fetch('https://nopecha.com/demo/cloudflare')
data = page.css('#padded_content a')
    
# Полная автоматизация браузера (Держите браузер открытым до завершения)
with DynamicSession(headless=True) as session:
    page = session.fetch('https://quotes.toscrape.com/', network_idle=True)
    quotes = page.css('.quote .text::text')

# Или используйте стиль одноразового запроса
page = DynamicFetcher.fetch('https://quotes.toscrape.com/', network_idle=True)
quotes = page.css('.quote .text::text')
```

### Выбор элементов
```python
# CSS-селекторы
page.css('a::text')                      # Извлечь текст
page.css('a::attr(href)')                # Извлечь атрибуты
page.css('a', recursive=False)           # Только прямые элементы
page.css('a', auto_save=True)            # Автоматически сохранять позиции элементов

# XPath
page.xpath('//a/text()')

# Гибкий поиск
page.find_by_text('Python', first_match=True)  # Найти по тексту
page.find_by_regex(r'\d{4}')                   # Найти по паттерну regex
page.find('div', {'class': 'container'})       # Найти по атрибутам

# Навигация
element.parent                           # Получить родительский элемент
element.next_sibling                     # Получить следующего брата
element.children                         # Получить дочерние элементы

# Похожие элементы
similar = page.get_similar(element)      # Найти похожие элементы

# Адаптивный скрапинг
saved_elements = page.css('.product', auto_save=True)
# Позже, когда сайт изменится:
page.css('.product', adaptive=True)      # Найти элементы используя сохраненные позиции
```

### Использование сессий
```python
from scrapling.fetchers import FetcherSession, AsyncFetcherSession

# Синхронная сессия
with FetcherSession() as session:
    # Cookie автоматически сохраняются
    page1 = session.get('https://quotes.toscrape.com/login')
    page2 = session.post('https://quotes.toscrape.com/login', data={'username': 'admin', 'password': 'admin'})
    
    # При необходимости переключите отпечаток браузера
    page2 = session.get('https://quotes.toscrape.com/', impersonate='firefox135')

# Использование асинхронной сессии
async with AsyncStealthySession(max_pages=2) as session:
    tasks = []
    urls = ['https://example.com/page1', 'https://example.com/page2']
    
    for url in urls:
        task = session.fetch(url)
        tasks.append(task)
    
    print(session.get_pool_stats())  # Опционально - Статус пула вкладок браузера (занят/свободен/ошибка)
    results = await asyncio.gather(*tasks)
    print(session.get_pool_stats())
```

## CLI и интерактивная оболочка

Scrapling v0.3 включает мощный интерфейс командной строки:

[![asciicast](https://asciinema.org/a/736339.svg)](https://asciinema.org/a/736339)

Запустить интерактивную оболочку веб-скрапинга
```bash
scrapling shell
```
Извлечь страницы в файл напрямую без программирования (Извлекает содержимое внутри тега `body` по умолчанию). Если выходной файл заканчивается на `.txt`, то будет извлечено текстовое содержимое цели. Если заканчивается на `.md`, это будет Markdown-представление HTML-содержимого; если заканчивается на `.html`, это будет само HTML-содержимое.
```bash
scrapling extract get 'https://example.com' content.md
scrapling extract get 'https://example.com' content.txt --css-selector '#fromSkipToProducts' --impersonate 'chrome'  # Все элементы, соответствующие CSS-селектору '#fromSkipToProducts'
scrapling extract fetch 'https://example.com' content.md --css-selector '#fromSkipToProducts' --no-headless
scrapling extract stealthy-fetch 'https://nopecha.com/demo/cloudflare' captchas.html --css-selector '#padded_content a' --solve-cloudflare
```

> [!NOTE]
> Есть много дополнительных функций, но мы хотим сохранить эту страницу краткой, например, MCP-сервер и интерактивная оболочка веб-скрапинга. Ознакомьтесь с полной документацией [здесь](https://scrapling.readthedocs.io/en/latest/)

## Тесты производительности

Scrapling не только мощный - он также невероятно быстрый, и обновления с версии 0.3 обеспечили исключительные улучшения производительности во всех операциях. Следующие тесты производительности сравнивают парсер Scrapling с другими популярными библиотеками.

### Тест скорости извлечения текста (5000 вложенных элементов)

| # |    Библиотека     | Время (мс) | vs Scrapling | 
|---|:-----------------:|:----------:|:------------:|
| 1 |     Scrapling     |    1.99    |     1.0x     |
| 2 |   Parsel/Scrapy   |    2.01    |    1.01x     |
| 3 |     Raw Lxml      |    2.5     |    1.256x    |
| 4 |      PyQuery      |   22.93    |    ~11.5x    |
| 5 |    Selectolax     |   80.57    |    ~40.5x    |
| 6 |   BS4 with Lxml   |  1541.37   |   ~774.6x    |
| 7 |  MechanicalSoup   |  1547.35   |   ~777.6x    |
| 8 | BS4 with html5lib |  3410.58   |   ~1713.9x   |


### Производительность подобия элементов и текстового поиска

Возможности адаптивного поиска элементов Scrapling значительно превосходят альтернативы:

| Библиотека  | Время (мс) | vs Scrapling |
|-------------|:----------:|:------------:|
| Scrapling   |    2.46    |     1.0x     |
| AutoScraper |    13.3    |    5.407x    |


> Все тесты производительности представляют собой средние значения более 100 запусков. См. [benchmarks.py](https://github.com/D4Vinci/Scrapling/blob/main/benchmarks.py) для методологии.

## Установка

Scrapling требует Python 3.10 или выше:

```bash
pip install scrapling
```

Начиная с v0.3.2, эта установка включает только движок парсера и его зависимости, без каких-либо фетчеров или зависимостей командной строки.

### Опциональные зависимости

1. Если вы собираетесь использовать какие-либо из дополнительных функций ниже, фетчеры или их классы, вам необходимо установить зависимости фетчеров и их зависимости браузера следующим образом:
    ```bash
    pip install "scrapling[fetchers]"
    
    scrapling install
    ```

    Это загрузит все браузеры вместе с их системными зависимостями и зависимостями манипуляции отпечатками.

2. Дополнительные функции:
   - Установить функцию MCP-сервера:
       ```bash
       pip install "scrapling[ai]"
       ```
   - Установить функции оболочки (оболочка веб-скрапинга и команда `extract`):
       ```bash
       pip install "scrapling[shell]"
       ```
   - Установить все:
       ```bash
       pip install "scrapling[all]"
       ```
   Помните, что вам нужно установить зависимости браузера с помощью `scrapling install` после любого из этих дополнений (если вы еще этого не сделали)

### Docker
Вы также можете установить Docker-образ со всеми дополнениями и браузерами с помощью следующей команды из DockerHub:
```bash
docker pull pyd4vinci/scrapling
```
Или скачайте его из реестра GitHub:
```bash
docker pull ghcr.io/d4vinci/scrapling:latest
```
Этот образ автоматически создается и отправляется с использованием GitHub Actions и основной ветки репозитория.

## Вклад

Мы приветствуем вклад! Пожалуйста, прочитайте наши [руководства по внесению вклада](https://github.com/D4Vinci/Scrapling/blob/main/CONTRIBUTING.md) перед началом работы.

## Отказ от ответственности

> [!CAUTION]
> Эта библиотека предоставляется только в образовательных и исследовательских целях. Используя эту библиотеку, вы соглашаетесь соблюдать местные и международные законы о скрапинге данных и конфиденциальности. Авторы и участники не несут ответственности за любое неправомерное использование этого программного обеспечения. Всегда уважайте условия обслуживания веб-сайтов и файлы robots.txt.

## Лицензия

Эта работа лицензирована по лицензии BSD-3-Clause.

## Благодарности

Этот проект включает код, адаптированный из:
- Parsel (лицензия BSD) — Используется для подмодуля [translator](https://github.com/D4Vinci/Scrapling/blob/main/scrapling/core/translator.py)

## Благодарности и ссылки

- Блестящая работа [Daijro](https://github.com/daijro) над [BrowserForge](https://github.com/daijro/browserforge) и [Camoufox](https://github.com/daijro/camoufox)
- Блестящая работа [Vinyzu](https://github.com/Vinyzu) над [Botright](https://github.com/Vinyzu/Botright) и [PatchRight](https://github.com/Kaliiiiiiiiii-Vinyzu/patchright)
- [brotector](https://github.com/kaliiiiiiiiii/brotector) за техники обхода обнаружения браузера
- [fakebrowser](https://github.com/kkoooqq/fakebrowser) и [BotBrowser](https://github.com/botswin/BotBrowser) за исследование отпечатков

---
<div align="center"><small>Разработано и создано с ❤️ Карим Шоаир.</small></div><br>