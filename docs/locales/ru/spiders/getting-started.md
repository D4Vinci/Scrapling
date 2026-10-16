---
title: "Создайте первый веб-краулер на Python со Scrapling"
description: "Создайте паука, который извлекает данные, переходит по страницам и экспортирует результаты. Узнайте о начальных URL, обработчиках, ограничениях доменов и robots.txt."
---

# Начало работы {#getting-started}

## Введение {#introduction}

!!! success "Что нужно знать"

    1. Прочитайте страницу [Основы Fetcher](../fetching/choosing.md), чтобы узнать о разных типах Fetcher и понять, когда их использовать.
    2. Прочитайте страницу [Основные классы](../parsing/main_classes.md), чтобы познакомиться с классами [Selector](../parsing/main_classes.md#selector) и [Response](../fetching/choosing.md#response-object).
    3. Прочитайте страницу [Архитектура](architecture.md), чтобы понять, как устроена система пауков.

Система пауков позволяет создать краулер, который обходит много страниц и выполняет запросы одновременно, всего в нескольких строках кода. Если вы работали со Scrapy, многие приёмы будут знакомы. Если нет, это руководство поможет начать.

## Ваш первый паук {#your-first-spider}

Паук представляет собой класс, который определяет, как обходить сайты и извлекать данные. Вот самый простой пример:

```python
from scrapling.spiders import Spider, Response

class QuotesSpider(Spider):
    name = "quotes"
    start_urls = ["https://quotes.toscrape.com"]

    async def parse(self, response: Response):
        for quote in response.css("div.quote"):
            yield {
                "text": quote.css("span.text::text").get(""),
                "author": quote.css("small.author::text").get(""),
            }
```

Каждому пауку нужны три элемента:

1. **`name`** - уникальное имя паука.
2. **`start_urls`** - список URL, с которых начинается обход.
3. **`parse()`** - метод с асинхронным генератором, который обрабатывает каждый ответ и выдаёт результаты.

Основная работа происходит в методе `parse()`. В нём доступны те же методы выбора элементов, что и в [Selector](../parsing/main_classes.md#selector)/[Response](../fetching/choosing.md#response-object). Чтобы выдать извлечённые записи, используйте `yield` со словарями.

## Запуск паука {#running-the-spider}

Создайте экземпляр паука и вызовите `start()`:

```python
result = QuotesSpider().start()
```

Метод `start()` сам управляет асинхронным выполнением, поэтому настраивать цикл событий не нужно. Во время работы все события записываются в терминал. В конце обхода вы получите подробную статистику.

Она находится в возвращённом объекте `CrawlResult`, вместе с результатами обхода:

```python
result = QuotesSpider().start()

# Access scraped items
for item in result.items:
    print(item["text"], "-", item["author"])

# Check statistics
print(f"Scraped {result.stats.items_scraped} items")
print(f"Made {result.stats.requests_count} requests")
print(f"Took {result.stats.elapsed_seconds:.1f} seconds")

# Did the crawl finish or was it paused?
print(f"Completed: {result.completed}")
```

## Переход по ссылкам {#following-links}

При обходе обычно нужно переходить по ссылкам между страницами. Создавайте следующие запросы с помощью `response.follow()`:

```python
from scrapling.spiders import Spider, Response

class QuotesSpider(Spider):
    name = "quotes"
    start_urls = ["https://quotes.toscrape.com"]

    async def parse(self, response: Response):
        # Extract items from the current page
        for quote in response.css("div.quote"):
            yield {
                "text": quote.css("span.text::text").get(""),
                "author": quote.css("small.author::text").get(""),
            }

        # Follow the "next page" link
        next_page = response.css("li.next a::attr(href)").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)
```

`response.follow()` автоматически объединяет относительные URL с URL текущей страницы. По умолчанию он также указывает текущую страницу в заголовке `Referer`.

Для разных типов страниц можно назначить разные методы-обработчики:

```python
async def parse(self, response: Response):
    for link in response.css("a.product-link::attr(href)").getall():
        yield response.follow(link, callback=self.parse_product)

async def parse_product(self, response: Response):
    yield {
        "name": response.css("h1::text").get(""),
        "price": response.css(".price::text").get(""),
    }
```

!!! note

    Все обработчики должны быть асинхронными генераторами с `async def` и `yield`.

## Экспорт данных {#exporting-data}

Объект `ItemList` в `result.items` содержит встроенные методы экспорта:

```python
result = QuotesSpider().start()

# Export as JSON
result.items.to_json("quotes.json")

# Export as JSON with pretty-printing
result.items.to_json("quotes.json", indent=True)

# Export as JSON Lines (one JSON object per line)
result.items.to_jsonl("quotes.jsonl")

# Export as CSV or XML
result.items.to_csv("quotes.csv")
result.items.to_xml("quotes.xml")
```

Все эти методы автоматически создают родительские каталоги, если их ещё нет.

`to_csv()` создаёт столбец для каждого ключа, найденного в записях. Поэтому записи с разными наборами ключей тоже попадают в файл, а ячейки без значений остаются пустыми. Передайте `fields=[...]`, чтобы выбрать столбцы и их порядок, или `delimiter="\t"`, чтобы получить TSV-файл. `to_xml()` помещает каждую запись в элемент `<item>` внутри корневого элемента `<items>`. Их имена можно изменить через `root_tag` и `item_tag`.

В обоих форматах сложные значения, такие как вложенный словарь или список, записываются как JSON. Данные не отбрасываются без уведомления.

## Ограничение доменов {#filtering-domains}

Используйте `allowed_domains`, чтобы ограничить обход заданными доменами. Это не даст пауку случайно перейти на сторонний сайт:

```python
class MySpider(Spider):
    name = "my_spider"
    start_urls = ["https://example.com"]
    allowed_domains = {"example.com"}

    async def parse(self, response: Response):
        for link in response.css("a::attr(href)").getall():
            # Links to other domains are silently dropped
            yield response.follow(link, callback=self.parse)
```

Поддомены разрешаются автоматически. Например, `allowed_domains = {"example.com"}` также разрешает `sub.example.com`, `blog.example.com` и другие поддомены.

Отброшенные запросы учитываются в `stats.offsite_requests_count`, где можно посмотреть их число.

## Соблюдение robots.txt {#robotstxt-compliance}

Установите `robots_txt_obey = True`, чтобы паук проверял правила robots.txt перед обходом каждого домена:

```python
class PoliteSpider(Spider):
    name = "polite"
    start_urls = ["https://example.com"]
    robots_txt_obey = True

    async def parse(self, response: Response):
        for link in response.css("a::attr(href)").getall():
            yield response.follow(link, callback=self.parse)
```

При включённой настройке паук:

1. **Заранее загружает robots.txt** для всех доменов из `start_urls` перед началом обхода. Загрузка идёт одновременно.
2. **Проверяет каждый запрос** по правилам `Disallow` в robots.txt домена. Запрещённые запросы отбрасываются без уведомления и учитываются в `stats.robots_disallowed_count`.
3. **Соблюдает директивы `Crawl-delay` и `Request-rate`**, выбирая наибольшее значение между задержкой из директивы и настройкой `download_delay`. Поэтому правила robots.txt могут только увеличить заданную задержку. Если включён AutoThrottle, его максимальная задержка также ограничивает это значение. Задайте достаточно большое значение `autothrottle_max_delay`, чтобы соблюдать требуемую задержку.

Файлы robots.txt загружаются через сессию паука по умолчанию и хранятся в кеше для каждого домена до конца обхода. Для доменов, найденных во время обхода и отсутствующих в `start_urls`, robots.txt загружается при первом запросе к домену.

**Примечание:** `robots_txt_obey` по умолчанию выключен, чтобы не менять поведение неожиданно. Если его включить, настройки числа одновременных запросов (`concurrent_requests`, `concurrent_requests_per_domain`) не изменятся. Меняется только задержка между запросами.

Если вы не хотите выбирать `download_delay` вручную, установите `autothrottle_enabled = True`. Паук сам подберёт задержку для каждого домена по скорости его ответов и увеличит её при блокировке. Подробнее в разделе [AutoThrottle](advanced.md#autothrottle).

## Что дальше {#whats-next}

Теперь можно перейти к следующим темам:

- [Запросы и ответы](requests-responses.md): приоритет запросов, удаление дубликатов, метаданные и другие возможности.
- [Сессии](sessions.md): разные типы Fetcher (HTTP, браузер, stealth) в одном пауке.
- [Прокси и блокировки](proxy-blocking.md): смена прокси между запросами и обработка блокировок.
- [Расширенные возможности](advanced.md): число одновременных запросов, AutoThrottle, пауза и возобновление, потоковая выдача, хуки жизненного цикла и журналирование.
