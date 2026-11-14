---
title: "Запросы пауков, обработчики и Response.follow"
description: "Создавайте запросы для обхода, передавайте метаданные и переходите по ссылкам через response.follow. Узнайте об обработчиках, приоритетах и удалении повторных запросов."
---

# Запросы и ответы {#requests-responses}

!!! success "Что нужно знать"

    1. Прочитайте страницу [Начало работы](getting-started.md), чтобы научиться создавать и запускать простого паука.

Здесь подробно описан объект `Request`: создание запросов, передача данных между обработчиками, приоритеты, удаление дубликатов и переход по ссылкам с `response.follow()`.

## Объект Request {#the-request-object}

`Request` представляет URL, который нужно загрузить. Запрос можно создать напрямую или через `response.follow()`:

```python
from scrapling.spiders import Request

# Direct construction
request = Request(
    "https://example.com/page",
    callback=self.parse_page,
    priority=5,
)

# Via response.follow (preferred in callbacks)
request = response.follow("/page", callback=self.parse_page)
```

Все аргументы `Request`:

| Аргумент | Тип | По умолчанию | Описание |
|---------------|------------|------------|-------------------------------------------------------------------------------------------------------|
| `url` | `str` | *обязателен* | URL для загрузки |
| `sid` | `str` | `""` | ID сессии, через которую отправляется запрос (см. [Сессии](sessions.md)) |
| `callback` | `callable` | `None` | Метод с асинхронным генератором для обработки ответа. По умолчанию `parse()` |
| `priority` | `int` | `0` | Запросы с большим значением обрабатываются первыми |
| `dont_filter` | `bool` | `False` | При `True` разрешает повторные запросы |
| `meta` | `dict` | `{}` | Произвольные метаданные, которые передаются в ответ |
| `**kwargs` | | | Дополнительные именованные аргументы метода загрузки сессии (например, `headers`, `method`, `data`) |

Все дополнительные именованные аргументы передаются прямо в сессию. Например, для POST-запроса:

```python
yield Request(
    "https://example.com/api",
    method="POST",
    data={"key": "value"},
    callback=self.parse_result,
)
```

## Response.follow() {#responsefollow}

`response.follow()` объединяет относительный URL с URL текущей страницы и создаёт новый `Request`. Если не задать `sid`, `callback` или `priority`, метод наследует эти значения из связанного `response.request`. Их можно заменить, передав новые значения.

Заголовки, cookies, данные аутентификации, настройки прокси и браузера, другие аргументы отдельного запроса и метаданные не копируются из предыдущего запроса. Это относится к ссылкам как на тот же сайт, так и на другие сайты.

`sid=""`, `callback=None` и `priority=None` наследуют значения связанного исходного запроса. Явное `priority=0` заменяет прежний приоритет. Метаданные по умолчанию пусты, удаление дубликатов включено. Общие настройки и хранилище cookies выбранной сессии продолжают действовать.

Переход по ссылке после POST отправляет GET, если не передать другое значение `method`.

```python
async def parse(self, response: Response):
    # Minimal - inherits callback, sid, priority from current request
    yield response.follow("/next-page")

    # Override specific fields
    yield response.follow(
        "/product/123",
        callback=self.parse_product,
        sid="stealth",
        priority=10,
    )

    # Pass additional metadata to
    yield response.follow(
        "/details",
        callback=self.parse_details,
        meta={"category": "electronics"},
    )
```

| Аргумент | Тип | По умолчанию | Описание |
| --- | --- | --- | --- |
| `url` | `str` | *обязателен* | URL для перехода: абсолютный или относительный |
| `sid` | `str` | `""` | Пустое значение наследует ID сессии исходного запроса |
| `callback` | `callable` | `None` | `None` наследует обработчик исходного запроса |
| `priority` | `int` / `None` | `None` | `None` наследует исходный приоритет. Явный `0` также заменяет прежнее значение |
| `dont_filter` | `bool` | `False` | Разрешить повторные запросы |
| `meta` | `dict` | `None` | Метаданные только для этого запроса |
| `referer_flow` | `bool` | `True` | Указать URL текущей страницы в Referer |
| `**kwargs` |  |  | Явные аргументы для метода загрузки сессии |

### Отключение передачи Referer {#disabling-referer-flow}

По умолчанию `response.follow()` задаёт URL текущей страницы в `Referer` для HTTP- и браузерных запросов. Он также задаёт `google_search=False`, чтобы браузер использовал этот Referer. Чтобы отключить это поведение:

```python
yield response.follow("/page", referer_flow=False)
```

При `referer_flow=False` метод не добавляет Referer и не меняет `google_search`. Переданные заголовки и настройки сессии или браузера по умолчанию продолжают действовать. Чтобы задать другой Referer для HTTP-запроса:

```python
yield response.follow(
    "/page",
    referer_flow=False,
    headers={"Referer": "https://example.com/"},
)
```

Для браузерного запроса используйте `extra_headers` и при необходимости задайте `google_search=False`.

## Обработчики {#callbacks}

Обработчики представляют собой методы паука с асинхронными генераторами, которые обрабатывают ответы. Они должны выдавать через `yield` один из трёх типов:

- **`dict`**: извлечённая запись, которая добавляется в результаты.
- **`Request`**: следующий запрос, который добавляется в очередь.
- **`None`**: игнорируется без уведомления.

```python
class MySpider(Spider):
    name = "my_spider"
    start_urls = ["https://example.com"]

    async def parse(self, response: Response):
        # Yield items (dicts)
        yield {"url": response.url, "title": response.css("title::text").get("")}

        # Yield follow-up requests
        for link in response.css("a::attr(href)").getall():
            yield response.follow(link, callback=self.parse_page)

    async def parse_page(self, response: Response):
        yield {"content": response.css("article::text").get("")}
```

!!! tip "Примечание"

    Все обработчики должны использовать `async def` и `yield`, а не `return`. Даже если обработчик выдаёт только записи без следующих запросов, он всё равно должен быть асинхронным генератором.

## Приоритет запросов {#request-priority}

Запросы с более высоким значением приоритета обрабатываются первыми. Это удобно, если одни страницы нужно обработать раньше других:

```python
async def parse(self, response: Response):
    # High priority - process product pages first
    for link in response.css("a.product::attr(href)").getall():
        yield response.follow(link, callback=self.parse_product, priority=10)

    # Low priority - pagination links processed after products
    next_page = response.css("a.next::attr(href)").get()
    if next_page:
        yield response.follow(next_page, callback=self.parse, priority=0)
```

В `response.follow()` значение `priority` по умолчанию равно `None` и наследует приоритет исходного запроса. Явное значение, включая `priority=0`, заменяет наследуемый приоритет.

## Удаление дубликатов {#deduplication}

Паук автоматически удаляет повторные запросы по отпечатку, который вычисляется из URL, HTTP-метода, тела запроса и ID сессии. Если два запроса имеют одинаковый отпечаток, второй отбрасывается без уведомления.

Чтобы разрешить повторы, например для повторного посещения страницы после входа, установите `dont_filter=True`:

```python
yield Request("https://example.com/dashboard", dont_filter=True, callback=self.parse_dashboard)

# Or with response.follow
yield response.follow("/dashboard", dont_filter=True, callback=self.parse_dashboard)
```

Состав отпечатка можно настроить атрибутами класса паука:

| Атрибут | По умолчанию | Действие |
|----------------------|---------|-----------------------------------------------------------------------------------------------------------------|
| `fp_include_kwargs` | `False` | Включить дополнительные аргументы запроса, переданные методу загрузки сессии, например заголовки |
| `fp_keep_fragments` | `False` | Сохранять фрагменты URL (`#section`) при вычислении отпечатка |
| `fp_include_headers` | `False` | Включить заголовки запроса в отпечаток |

Например, чтобы считать `https://example.com/page#section1` и `https://example.com/page#section2` разными URL:

```python
class MySpider(Spider):
    name = "my_spider"
    fp_keep_fragments = True
    # ...
```

## Метаданные запроса {#request-meta}

Словарь `meta` позволяет передавать любые данные между обработчиками. Это полезно, когда для обработки одной страницы нужны данные с другой:

```python
async def parse(self, response: Response):
    for product in response.css("div.product"):
        category = product.css("span.category::text").get("")
        link = product.css("a::attr(href)").get()
        if link:
            yield response.follow(
                link,
                callback=self.parse_product,
                meta={"category": category},
            )

async def parse_product(self, response: Response):
    yield {
        "name": response.css("h1::text").get(""),
        "price": response.css(".price::text").get(""),
        # Access meta from the request
        "category": response.meta.get("category", ""),
    }
```

`response.follow()` использует только явно переданный `meta`. Чтобы повторно использовать прежние значения, выберите и передайте только нужные ключи.

Система пауков также сохраняет часть метаданных автоматически. Например, при включённой смене прокси адрес использованного прокси доступен в `response.meta["proxy"]`.
