---
title: "HTTP- и браузерные сессии в одном краулере"
description: "Настройте именованные сессии и отправляйте запросы паука через HTTP- или браузерные Fetcher. Сохраняйте cookies, запускайте сессии по мере необходимости и изучайте историю API."
---

# Сессии пауков {#spiders-sessions}

!!! success "Что нужно знать"

    1. Прочитайте страницу [Начало работы](getting-started.md), чтобы научиться создавать и запускать простого паука.
    2. Познакомьтесь с [основами Fetcher](../fetching/choosing.md) и различиями между HTTP- и Stealthy-сессиями.

Паук может одновременно использовать несколько сессий Fetcher. Например, быструю HTTP-сессию для простых страниц и stealth-браузер для защищённых. Здесь показано, как настроить и использовать сессии.

## Что такое сессия? {#what-are-sessions}

Сессия представляет собой настроенный экземпляр Fetcher, который работает в течение всего обхода. Паук не создаёт новое соединение или браузер для каждого запроса, а повторно использует сессии. Это быстрее и требует меньше ресурсов.

По умолчанию каждый паук создаёт одну [FetcherSession](../fetching/static.md). Чтобы добавить сессии или заменить основную, переопределите `configure_sessions()`. Используйте только асинхронные варианты сессий, как в таблице ниже:


| Тип сессии | Назначение |
|-------------------------------------------------|------------------------------------------|
| [FetcherSession](../fetching/static.md) | Быстрые HTTP-запросы без JavaScript |
| [AsyncStealthySession](../fetching/stealthy.md) | JavaScript, управление браузером, обход защиты от ботов |


## Настройка сессий {#configuring-sessions}

Переопределите `configure_sessions()` в пауке. Параметр `manager` содержит экземпляр `SessionManager`. Регистрируйте сессии через `manager.add()`:

```python
from scrapling.spiders import Spider, Response
from scrapling.fetchers import FetcherSession

class MySpider(Spider):
    name = "my_spider"
    start_urls = ["https://example.com"]

    def configure_sessions(self, manager):
        manager.add("default", FetcherSession())

    async def parse(self, response: Response):
        yield {"title": response.css("title::text").get("")}
```

Аргументы `manager.add()`:

| Аргумент | Тип | По умолчанию | Описание |
|--------------|-----------|------------|----------------------------------------------|
| `session_id` | `str` | *обязателен* | Имя, по которому сессию можно указать в запросе |
| `session` | `Session` | *обязателен* | Экземпляр сессии |
| `default` | `bool` | `False` | Сделать эту сессию основной |
| `lazy` | `bool` | `False` | Запускать сессию только при первом использовании |

!!! note "Примечания"

    1. Если сессия не указана в запросе, используется сессия по умолчанию. Она определяется одним из двух способов:
        1. Первая добавленная в менеджер сессия автоматически становится основной.
        2. Сессия добавляется в менеджер с `default=True`.
    2. Переданные экземпляры сессий не обязательно запускать заранее. Паук проверит все сессии и запустит те, которые ещё не работают.
    3. Чтобы запускать сессию только при использовании, укажите аргумент `lazy` при её добавлении. Например, так можно открывать браузер только при необходимости, а не вместе с пауком.

## Паук с несколькими сессиями {#multi-session-spider}

Практический пример: быстрая HTTP-сессия для страниц со списками и stealth-браузер для страниц с подробностями, защищённых от ботов:

```python
from scrapling.spiders import Spider, Response
from scrapling.fetchers import FetcherSession, AsyncStealthySession

class ProductSpider(Spider):
    name = "products"
    start_urls = ["https://shop.example.com/products"]

    def configure_sessions(self, manager):
        # Fast HTTP for listing pages (default)
        manager.add("http", FetcherSession())

        self.browser_session = AsyncStealthySession(
            headless=True,
            network_idle=True,
            record_requests=True,
        )
        manager.add("stealth", self.browser_session)

    async def parse(self, response: Response):
        for link in response.css("a.product::attr(href)").getall():
            # Route product pages through the stealth session
            yield response.follow(link, sid="stealth", callback=self.parse_product)

        next_page = response.css("a.next::attr(href)").get()
        if next_page:
            yield response.follow(next_page)

    async def parse_product(self, response: Response):
        yield {
            "name": response.css("h1::text").get(""),
            "price": response.css(".price::text").get(""),
        }

    async def on_close(self):
        for api_response in self.browser_session.network.search(
            url_pattern=r"https://api\.shop\.example\.com/.*", limit=None
        ):
            self.logger.info(f"Saved API response: {api_response.url} ({api_response.status})")
```

В примере сохраняется экземпляр браузера, а его история API читается один раз в `on_close()` перед закрытием сессий. История охватывает все страницы товаров и остаётся доступной после закрытия. Завершение ещё не записанных запросов не ожидается, а ограничения объёма истории продолжают действовать.

Основную роль играет `sid`: он указывает пауку сессию для каждого запроса. Если вызвать `response.follow()` без `sid`, ID сессии наследуется от исходного запроса.

Сессии не обязательно должны относиться к разным классам. Можно создать несколько экземпляров одного класса с разными настройками:

```python
from scrapling.spiders import Spider, Response
from scrapling.fetchers import FetcherSession

class ProductSpider(Spider):
    name = "products"
    start_urls = ["https://shop.example.com/products"]

    def configure_sessions(self, manager):
        chrome_requests = FetcherSession(impersonate="chrome")
        firefox_requests = FetcherSession(impersonate="firefox")

        manager.add("chrome", chrome_requests)
        manager.add("firefox", firefox_requests)

    async def parse(self, response: Response):
        for link in response.css("a.product::attr(href)").getall():
            yield response.follow(link, callback=self.parse_product)

        next_page = response.css("a.next::attr(href)").get()
        if next_page:
            yield response.follow(next_page, sid="firefox")

    async def parse_product(self, response: Response):
        yield {
            "name": response.css("h1::text").get(""),
            "price": response.css(".price::text").get(""),
        }
```

Также можно выделить отдельную сессию со своими cookies и состоянием для определённых запросов.

## Аргументы сессии {#session-arguments}

Дополнительные именованные аргументы `Request` или `response.follow(**kwargs)` передаются в метод загрузки сессии. Так можно настроить отдельный запрос, не меняя настройки всей сессии:

```python
async def parse(self, response: Response):
    # Pass extra headers for this specific request
    yield Request(
        "https://api.example.com/data",
        headers={"Authorization": "Bearer token123"},
        callback=self.parse_api,
    )

    # Use a different HTTP method
    yield Request(
        "https://example.com/submit",
        method="POST",
        data={"field": "value"},
        sid="firefox",
        callback=self.parse_result,
    )
```

!!! warning

    Обычно при работе с `FetcherSession`, `Fetcher` или `AsyncFetcher` HTTP-метод выбирается вызовом `.get()`, `.post()` и подобных методов. В пауках с `FetcherSession` это устроено иначе. По умолчанию отправляется _HTTP GET_. Чтобы выбрать другой метод, передайте его через аргумент `method`, как в примере выше. Это позволяет использовать единый интерфейс `Request` для всех типов сессий.

Для сессии `"stealth"` (`AsyncStealthySession`) из примера выше можно передать браузерные аргументы, такие как `wait_selector`, `page_action` и `extra_headers`:

```python
async def parse(self, response: Response):
    # Use Cloudflare solver with the `AsyncStealthySession` we configured above
    yield Request(
        "https://nopecha.com/demo/cloudflare",
        sid="stealth",
        callback=self.parse_result,
        solve_cloudflare=True,
        block_webrtc=True,
        hide_canvas=True,
        google_search=True,
    )

    yield response.follow(
        "/dynamic-page",
        sid="stealth",
        callback=self.parse_dynamic,
        wait_selector="div.loaded",
        network_idle=True,
    )
```

!!! warning

    `response.follow()` наследует аргументы сессии (**kwargs) от исходного запроса, кроме `method`, `params`, `data`, `json`, `files` и `multipart`. Поэтому переход по ссылке после POST отправляет обычный GET. Новые аргументы имеют приоритет над унаследованными.

```python
from scrapling.spiders import Spider, Response
from scrapling.fetchers import FetcherSession

class ProductSpider(Spider):
    name = "products"
    start_urls = ["https://shop.example.com/products"]

    def configure_sessions(self, manager):
        manager.add("http", FetcherSession(impersonate='chrome'))

    async def parse(self, response: Response):
        # I don't want the follow request to impersonate a desktop Chrome like the previous request, but a mobile one
        # so I override it like this
        for link in response.css("a.product::attr(href)").getall():
            yield response.follow(link, impersonate="chrome131_android", callback=self.parse_product)

        next_page = response.css("a.next::attr(href)").get()
        if next_page:
            yield response.follow(next_page)

    async def parse_product(self, response: Response):
        yield {
            "name": response.css("h1::text").get(""),
            "price": response.css(".price::text").get(""),
        }
```
!!! info

    При завершении паука менеджер автоматически проверяет, остались ли работающие сессии, и закрывает их перед закрытием паука.
