<!-- mcp-name: io.github.D4Vinci/Scrapling -->

<h1 align="center">
    <a href="https://scrapling.readthedocs.io">
        <picture>
          <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/docs/assets/cover_dark.svg?sanitize=true">
          <img alt="Scrapling Poster" src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/docs/assets/cover_light.svg?sanitize=true">
        </picture>
    </a>
    <br>
    <small>Effortless Web Scraping for the Modern Web</small>
</h1>

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
    <a href="https://scrapling.readthedocs.io/en/latest/parsing/selection/"><strong>Методы выбора</strong></a>
    &middot;
    <a href="https://scrapling.readthedocs.io/en/latest/fetching/choosing/"><strong>Выбор Fetcher</strong></a>
    &middot;
    <a href="https://scrapling.readthedocs.io/en/latest/spiders/architecture.html"><strong>Пауки</strong></a>
    &middot;
    <a href="https://scrapling.readthedocs.io/en/latest/spiders/proxy-blocking.html"><strong>Ротация прокси</strong></a>
    &middot;
    <a href="https://scrapling.readthedocs.io/en/latest/cli/overview/"><strong>CLI</strong></a>
    &middot;
    <a href="https://scrapling.readthedocs.io/en/latest/ai/mcp-server/"><strong>Режим MCP</strong></a>
</p>

Scrapling — это адаптивный фреймворк для Web Scraping, который берёт на себя всё: от одного запроса до полномасштабного обхода сайтов.

Его парсер учится на изменениях сайтов и автоматически перемещает ваши элементы при обновлении страниц. Его Fetcher'ы обходят анти-бот системы вроде Cloudflare Turnstile прямо из коробки. А его Spider-фреймворк позволяет масштабироваться до параллельных, многосессионных обходов с Pause & Resume и автоматической ротацией Proxy — и всё это в нескольких строках Python. Одна библиотека, без компромиссов.

Молниеносно быстрые обходы с отслеживанием статистики в реальном времени и Streaming. Создано веб-скраперами для веб-скраперов и обычных пользователей — здесь есть что-то для каждого.

```python
from scrapling.fetchers import Fetcher, AsyncFetcher, StealthyFetcher, DynamicFetcher
StealthyFetcher.adaptive = True
p = StealthyFetcher.fetch('https://example.com', headless=True, network_idle=True)  # Загрузите сайт незаметно!
products = p.css('.product', auto_save=True)                                        # Скрапьте данные, которые переживут изменения дизайна сайта!
products = p.css('.product', adaptive=True)                                         # Позже, если структура сайта изменится, передайте `adaptive=True`, чтобы найти их!
```
Или масштабируйте до полного обхода
```python
from scrapling.spiders import Spider, Response

class MySpider(Spider):
  name = "demo"
  start_urls = ["https://example.com/"]

  async def parse(self, response: Response):
      for item in response.css('.product'):
          yield {"title": item.css('h2::text').get()}

MySpider().start()
```


# Платиновые спонсоры

<i><sub>Хотите стать первой компанией, которая появится здесь? Нажмите [здесь](https://github.com/sponsors/D4Vinci/sponsorships?tier_id=586646)</sub></i>
# Спонсоры

<!-- sponsors -->

<a href="https://www.thordata.com/?ls=github&lk=github" target="_blank" title="Unblockable proxies and scraping infrastructure, delivering real-time, reliable web data to power AI models and workflows."><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/thordata.jpg"></a>
<a href="https://evomi.com?utm_source=github&utm_medium=banner&utm_campaign=d4vinci-scrapling" target="_blank" title="Evomi is your Swiss Quality Proxy Provider, starting at $0.49/GB"><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/evomi.png"></a>
<a href="https://serpapi.com/?utm_source=scrapling" target="_blank" title="Scrape Google and other search engines with SerpApi"><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/SerpApi.png"></a>
<a href="https://visit.decodo.com/Dy6W0b" target="_blank" title="Try the Most Efficient Residential Proxies for Free"><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/decodo.png"></a>
<a href="https://petrosky.io/d4vinci" target="_blank" title="PetroSky delivers cutting-edge VPS hosting."><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/petrosky.png"></a>
<a href="https://hasdata.com/?utm_source=github&utm_medium=banner&utm_campaign=D4Vinci" target="_blank" title="The web scraping service that actually beats anti-bot systems!"><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/hasdata.png"></a>
<a href="https://proxyempire.io/" target="_blank" title="Collect The Data Your Project Needs with the Best Residential Proxies"><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/ProxyEmpire.png"></a>
<a href="https://hypersolutions.co/?utm_source=github&utm_medium=readme&utm_campaign=scrapling" target="_blank" title="Bot Protection Bypass API for Akamai, DataDome, Incapsula & Kasada"><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/HyperSolutions.png"></a>


<a href="https://www.swiftproxy.net/" target="_blank" title="Unlock Reliable Proxy Services with Swiftproxy!"><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/swiftproxy.png"></a>
<a href="https://www.rapidproxy.io/?ref=d4v" target="_blank" title="Affordable Access to the Proxy World – bypass CAPTCHAs blocks, and avoid additional costs."><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/rapidproxy.jpg"></a>
<a href="https://browser.cash/?utm_source=D4Vinci&utm_medium=referral" target="_blank" title="Browser Automation & AI Browser Agent Platform"><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/browserCash.png"></a>

<!-- /sponsors -->

<i><sub>Хотите показать здесь свою рекламу? Нажмите [здесь](https://github.com/sponsors/D4Vinci) и выберите подходящий вам уровень!</sub></i>

---

## Ключевые особенности

### Spider'ы — полноценный фреймворк для обхода сайтов
- 🕷️ **Scrapy-подобный Spider API**: Определяйте Spider'ов с `start_urls`, async `parse` callback'ами и объектами `Request`/`Response`.
- ⚡ **Параллельный обход**: Настраиваемые лимиты параллелизма, ограничение скорости по домену и задержки загрузки.
- 🔄 **Поддержка нескольких сессий**: Единый интерфейс для HTTP-запросов и скрытных headless-браузеров в одном Spider — маршрутизируйте запросы к разным сессиям по ID.
- 💾 **Pause & Resume**: Persistence обхода на основе Checkpoint'ов. Нажмите Ctrl+C для мягкой остановки; перезапустите, чтобы продолжить с того места, где вы остановились.
- 📡 **Режим Streaming**: Стримьте извлечённые элементы по мере их поступления через `async for item in spider.stream()` со статистикой в реальном времени — идеально для UI, конвейеров и длительных обходов.
- 🛡️ **Обнаружение заблокированных запросов**: Автоматическое обнаружение и повторная отправка заблокированных запросов с настраиваемой логикой.
- 📦 **Встроенный экспорт**: Экспортируйте результаты через хуки и собственный конвейер или встроенный JSON/JSONL с `result.items.to_json()` / `result.items.to_jsonl()` соответственно.

### Продвинутая загрузка сайтов с поддержкой Session
- **HTTP-запросы**: Быстрые и скрытные HTTP-запросы с классом `Fetcher`. Может имитировать TLS fingerprint браузера, заголовки и использовать HTTP/3.
- **Динамическая загрузка**: Загрузка динамических сайтов с полной автоматизацией браузера через класс `DynamicFetcher`, поддерживающий Chromium от Playwright и Google Chrome.
- **Обход анти-ботов**: Расширенные возможности скрытности с `StealthyFetcher` и подмену fingerprint'ов. Может легко обойти все типы Cloudflare Turnstile/Interstitial с помощью автоматизации.
- **Управление сессиями**: Поддержка постоянных сессий с классами `FetcherSession`, `StealthySession` и `DynamicSession` для управления cookie и состоянием между запросами.
- **Ротация Proxy**: Встроенный `ProxyRotator` с циклической или пользовательскими стратегиями для всех типов сессий, а также переопределение Proxy для каждого запроса.
- **Блокировка доменов**: Блокируйте запросы к определённым доменам (и их поддоменам) в браузерных Fetcher'ах.
- **Поддержка async**: Полная async-поддержка во всех Fetcher'ах и выделенных async-классах сессий.

### Адаптивный скрапинг и интеграция с ИИ
- 🔄 **Умное отслеживание элементов**: Перемещайте элементы после изменений сайта с помощью интеллектуальных алгоритмов подобия.
- 🎯 **Умный гибкий выбор**: CSS-селекторы, XPath-селекторы, поиск на основе фильтров, текстовый поиск, поиск по регулярным выражениям и многое другое.
- 🔍 **Поиск похожих элементов**: Автоматически находите элементы, похожие на найденные.
- 🤖 **MCP-сервер для использования с ИИ**: Встроенный MCP-сервер для Web Scraping с помощью ИИ и извлечения данных. MCP-сервер обладает мощными пользовательскими возможностями, которые используют Scrapling для извлечения целевого контента перед передачей его ИИ (Claude/Cursor/и т.д.), тем самым ускоряя операции и снижая затраты за счёт минимизации использования токенов. ([демо-видео](https://www.youtube.com/watch?v=qyFk3ZNwOxE))

### Высокопроизводительная и проверенная в боях архитектура
- 🚀 **Молниеносная скорость**: Оптимизированная производительность, превосходящая большинство Python-библиотек для скрапинга.
- 🔋 **Эффективное использование памяти**: Оптимизированные структуры данных и ленивая загрузка для минимального потребления памяти.
- ⚡ **Быстрая сериализация JSON**: В 10 раз быстрее стандартной библиотеки.
- 🏗️ **Проверено в боях**: Scrapling имеет не только 92% покрытия тестами и полное покрытие type hints, но и ежедневно использовался сотнями веб-скраперов в течение последнего года.

### Удобный для разработчиков/веб-скраперов опыт
- 🎯 **Интерактивная Web Scraping Shell**: Опциональная встроенная IPython-оболочка с интеграцией Scrapling, ярлыками и новыми инструментами для ускорения разработки скриптов Web Scraping, такими как преобразование curl-запросов в запросы Scrapling и просмотр результатов запросов в браузере.
- 🚀 **Используйте прямо из терминала**: При желании вы можете использовать Scrapling для скрапинга URL без написания ни одной строки кода!
- 🛠️ **Богатый API навигации**: Расширенный обход DOM с методами навигации по родителям, братьям и детям.
- 🧬 **Улучшенная обработка текста**: Встроенные регулярные выражения, методы очистки и оптимизированные операции со строками.
- 📝 **Автоматическая генерация селекторов**: Генерация надёжных CSS/XPath-селекторов для любого элемента.
- 🔌 **Знакомый API**: Похож на Scrapy/BeautifulSoup с теми же псевдоэлементами, используемыми в Scrapy/Parsel.
- 📘 **Полное покрытие типами**: Полные type hints для отличной поддержки IDE и автодополнения кода. Вся кодовая база автоматически проверяется **PyRight** и **MyPy** при каждом изменении.
- 🔋 **Готовый Docker-образ**: С каждым релизом автоматически создаётся и публикуется Docker-образ, содержащий все браузеры.

## Начало работы

Давайте кратко покажем, на что способен Scrapling, без глубокого погружения.

### Базовое использование
HTTP-запросы с поддержкой Session
```python
from scrapling.fetchers import Fetcher, FetcherSession

with FetcherSession(impersonate='chrome') as session:  # Используйте последнюю версию TLS fingerprint Chrome
    page = session.get('https://quotes.toscrape.com/', stealthy_headers=True)
    quotes = page.css('.quote .text::text').getall()

# Или используйте одноразовые запросы
page = Fetcher.get('https://quotes.toscrape.com/')
quotes = page.css('.quote .text::text').getall()
```
Расширенный режим скрытности
```python
from scrapling.fetchers import StealthyFetcher, StealthySession

with StealthySession(headless=True, solve_cloudflare=True) as session:  # Держите браузер открытым, пока не закончите
    page = session.fetch('https://nopecha.com/demo/cloudflare', google_search=False)
    data = page.css('#padded_content a').getall()

# Или используйте стиль одноразового запроса — открывает браузер для этого запроса, затем закрывает его после завершения
page = StealthyFetcher.fetch('https://nopecha.com/demo/cloudflare')
data = page.css('#padded_content a').getall()
```
Полная автоматизация браузера
```python
from scrapling.fetchers import DynamicFetcher, DynamicSession

with DynamicSession(headless=True, disable_resources=False, network_idle=True) as session:  # Держите браузер открытым, пока не закончите
    page = session.fetch('https://quotes.toscrape.com/', load_dom=False)
    data = page.xpath('//span[@class="text"]/text()').getall()  # XPath-селектор, если вы предпочитаете его

# Или используйте стиль одноразового запроса — открывает браузер для этого запроса, затем закрывает его после завершения
page = DynamicFetcher.fetch('https://quotes.toscrape.com/')
data = page.css('.quote .text::text').getall()
```

### Spider'ы
Создавайте полноценные обходчики с параллельными запросами, несколькими типами сессий и Pause & Resume:
```python
from scrapling.spiders import Spider, Request, Response

class QuotesSpider(Spider):
    name = "quotes"
    start_urls = ["https://quotes.toscrape.com/"]
    concurrent_requests = 10

    async def parse(self, response: Response):
        for quote in response.css('.quote'):
            yield {
                "text": quote.css('.text::text').get(),
                "author": quote.css('.author::text').get(),
            }

        next_page = response.css('.next a')
        if next_page:
            yield response.follow(next_page[0].attrib['href'])

result = QuotesSpider().start()
print(f"Извлечено {len(result.items)} цитат")
result.items.to_json("quotes.json")
```
Используйте несколько типов сессий в одном Spider:
```python
from scrapling.spiders import Spider, Request, Response
from scrapling.fetchers import FetcherSession, AsyncStealthySession

class MultiSessionSpider(Spider):
    name = "multi"
    start_urls = ["https://example.com/"]

    def configure_sessions(self, manager):
        manager.add("fast", FetcherSession(impersonate="chrome"))
        manager.add("stealth", AsyncStealthySession(headless=True), lazy=True)

    async def parse(self, response: Response):
        for link in response.css('a::attr(href)').getall():
            # Направляйте защищённые страницы через stealth-сессию
            if "protected" in link:
                yield Request(link, sid="stealth")
            else:
                yield Request(link, sid="fast", callback=self.parse)  # явный callback
```
Приостанавливайте и возобновляйте длительные обходы с помощью Checkpoint'ов, запуская Spider следующим образом:
```python
QuotesSpider(crawldir="./crawl_data").start()
```
Нажмите Ctrl+C для мягкой остановки — прогресс сохраняется автоматически. Позже, когда вы снова запустите Spider, передайте тот же `crawldir`, и он продолжит с того места, где остановился.

### Продвинутый парсинг и навигация
```python
from scrapling.fetchers import Fetcher

# Богатый выбор элементов и навигация
page = Fetcher.get('https://quotes.toscrape.com/')

# Получение цитат различными методами выбора
quotes = page.css('.quote')  # CSS-селектор
quotes = page.xpath('//div[@class="quote"]')  # XPath
quotes = page.find_all('div', {'class': 'quote'})  # В стиле BeautifulSoup
# То же самое, что
quotes = page.find_all('div', class_='quote')
quotes = page.find_all(['div'], class_='quote')
quotes = page.find_all(class_='quote')  # и так далее...
# Найти элемент по текстовому содержимому
quotes = page.find_by_text('quote', tag='div')

# Продвинутая навигация
quote_text = page.css('.quote')[0].css('.text::text').get()
quote_text = page.css('.quote').css('.text::text').getall()  # Цепочка селекторов
first_quote = page.css('.quote')[0]
author = first_quote.next_sibling.css('.author::text')
parent_container = first_quote.parent

# Связи элементов и подобие
similar_elements = first_quote.find_similar()
below_elements = first_quote.below_elements()
```
Вы можете использовать парсер напрямую, если не хотите загружать сайты, как показано ниже:
```python
from scrapling.parser import Selector

page = Selector("<html>...</html>")
```
И он работает точно так же!

### Примеры async Session
```python
import asyncio
from scrapling.fetchers import FetcherSession, AsyncStealthySession, AsyncDynamicSession

async with FetcherSession(http3=True) as session:  # `FetcherSession` контекстно-осведомлён и может работать как в sync, так и в async-режимах
    page1 = session.get('https://quotes.toscrape.com/')
    page2 = session.get('https://quotes.toscrape.com/', impersonate='firefox135')

# Использование async-сессии
async with AsyncStealthySession(max_pages=2) as session:
    tasks = []
    urls = ['https://example.com/page1', 'https://example.com/page2']

    for url in urls:
        task = session.fetch(url)
        tasks.append(task)

    print(session.get_pool_stats())  # Опционально — статус пула вкладок браузера (занят/свободен/ошибка)
    results = await asyncio.gather(*tasks)
    print(session.get_pool_stats())
```

## CLI и интерактивная Shell

Scrapling включает мощный интерфейс командной строки:

[![asciicast](https://asciinema.org/a/736339.svg)](https://asciinema.org/a/736339)

Запустить интерактивную Web Scraping Shell
```bash
scrapling shell
```
Извлечь страницы в файл напрямую без программирования (по умолчанию извлекает содержимое внутри тега `body`). Если выходной файл заканчивается на `.txt`, будет извлечено текстовое содержимое цели. Если заканчивается на `.md`, это будет Markdown-представление HTML-содержимого; если заканчивается на `.html`, это будет само HTML-содержимое.
```bash
scrapling extract get 'https://example.com' content.md
scrapling extract get 'https://example.com' content.txt --css-selector '#fromSkipToProducts' --impersonate 'chrome'  # Все элементы, соответствующие CSS-селектору '#fromSkipToProducts'
scrapling extract fetch 'https://example.com' content.md --css-selector '#fromSkipToProducts' --no-headless
scrapling extract stealthy-fetch 'https://nopecha.com/demo/cloudflare' captchas.html --css-selector '#padded_content a' --solve-cloudflare
```

> [!NOTE]
> Есть множество дополнительных возможностей, но мы хотим сохранить эту страницу краткой, включая MCP-сервер и интерактивную Web Scraping Shell. Ознакомьтесь с полной документацией [здесь](https://scrapling.readthedocs.io/en/latest/)

## Тесты производительности

Scrapling не только мощный — он ещё и невероятно быстрый. Следующие тесты производительности сравнивают парсер Scrapling с последними версиями других популярных библиотек.

### Тест скорости извлечения текста (5000 вложенных элементов)

| # |    Библиотека     | Время (мс) | vs Scrapling |
|---|:-----------------:|:----------:|:------------:|
| 1 |     Scrapling     |    2.02    |     1.0x     |
| 2 |   Parsel/Scrapy   |    2.04    |     1.01     |
| 3 |     Raw Lxml      |    2.54    |    1.257     |
| 4 |      PyQuery      |   24.17    |     ~12x     |
| 5 |    Selectolax     |   82.63    |     ~41x     |
| 6 |  MechanicalSoup   |  1549.71   |   ~767.1x    |
| 7 |   BS4 with Lxml   |  1584.31   |   ~784.3x    |
| 8 | BS4 with html5lib |  3391.91   |   ~1679.1x   |


### Производительность подобия элементов и текстового поиска

Возможности адаптивного поиска элементов Scrapling значительно превосходят альтернативы:

| Библиотека  | Время (мс) | vs Scrapling |
|-------------|:----------:|:------------:|
| Scrapling   |    2.39    |     1.0x     |
| AutoScraper |   12.45    |    5.209x    |


> Все тесты производительности представляют собой средние значения более 100 запусков. См. [benchmarks.py](https://github.com/D4Vinci/Scrapling/blob/main/benchmarks.py) для методологии.

## Установка

Scrapling требует Python 3.10 или выше:

```bash
pip install scrapling
```

Эта установка включает только движок парсера и его зависимости, без каких-либо Fetcher'ов или зависимостей командной строки.

### Опциональные зависимости

1. Если вы собираетесь использовать какие-либо из дополнительных возможностей ниже, Fetcher'ы или их классы, вам необходимо установить зависимости Fetcher'ов и браузеров следующим образом:
    ```bash
    pip install "scrapling[fetchers]"

    scrapling install           # normal install
    scrapling install  --force  # force reinstall
    ```

    Это загрузит все браузеры вместе с их системными зависимостями и зависимостями для манипуляции fingerprint'ами.

    Или вы можете установить их из кода вместо выполнения команды:
    ```python
    from scrapling.cli import install

    install([], standalone_mode=False)          # normal install
    install(["--force"], standalone_mode=False) # force reinstall
    ```

2. Дополнительные возможности:
   - Установить функцию MCP-сервера:
       ```bash
       pip install "scrapling[ai]"
       ```
   - Установить функции Shell (Web Scraping Shell и команда `extract`):
       ```bash
       pip install "scrapling[shell]"
       ```
   - Установить всё:
       ```bash
       pip install "scrapling[all]"
       ```
   Помните, что вам нужно установить зависимости браузеров с помощью `scrapling install` после любого из этих дополнений (если вы ещё этого не сделали)

### Docker
Вы также можете установить Docker-образ со всеми дополнениями и браузерами с помощью следующей команды из DockerHub:
```bash
docker pull pyd4vinci/scrapling
```
Или скачайте его из реестра GitHub:
```bash
docker pull ghcr.io/d4vinci/scrapling:latest
```
Этот образ автоматически создаётся и публикуется с помощью GitHub Actions и основной ветки репозитория.

## Участие в разработке

Мы приветствуем участие! Пожалуйста, прочитайте наши [руководства по участию в разработке](https://github.com/D4Vinci/Scrapling/blob/main/CONTRIBUTING.md) перед началом работы.

## Отказ от ответственности

> [!CAUTION]
> Эта библиотека предоставляется только в образовательных и исследовательских целях. Используя эту библиотеку, вы соглашаетесь соблюдать местные и международные законы о скрапинге данных и конфиденциальности. Авторы и участники не несут ответственности за любое неправомерное использование этого программного обеспечения. Всегда уважайте условия обслуживания веб-сайтов и файлы robots.txt.

## Лицензия

Эта работа лицензирована по лицензии BSD-3-Clause.

## Благодарности

Этот проект включает код, адаптированный из:
- Parsel (лицензия BSD) — Используется для подмодуля [translator](https://github.com/D4Vinci/Scrapling/blob/main/scrapling/core/translator.py)

---
<div align="center"><small>Разработано и создано с ❤️ Карим Шоаир.</small></div><br>
