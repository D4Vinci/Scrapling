---
title: "Смена прокси и повтор заблокированных запросов"
description: "Используйте прокси и способы их смены в пауках Scrapling. Обнаруживайте блокировки, повторяйте запросы и переходите с HTTP на браузерные сессии."
---

# Управление прокси и обработка блокировок {#proxy-management-and-handling-blocks}

## Введение {#introduction}

!!! success "Что нужно знать"

    1. Прочитайте страницу [Начало работы](getting-started.md), чтобы научиться создавать и запускать простого паука.
    2. Прочитайте страницу [Сессии](sessions.md), чтобы понять, как настраивать сессии.

При сборе больших объёмов данных часто нужно менять прокси, чтобы избежать ограничений частоты запросов и блокировок. Для этого в Scrapling есть `ProxyRotator`. Он работает со всеми типами сессий и связан с системой повторов заблокированных запросов.

Если вы не знаете, что такое прокси и как его выбрать, поможет [это руководство](https://substack.thewebscraping.club/p/everything-about-proxies).

## ProxyRotator {#proxyrotator}

Класс `ProxyRotator` управляет списком прокси и автоматически меняет их. Передайте его в любую сессию через параметр `proxy_rotator`:

```python
from scrapling.spiders import Spider, Response
from scrapling.fetchers import FetcherSession, ProxyRotator

class MySpider(Spider):
    name = "my_spider"
    start_urls = ["https://example.com"]

    def configure_sessions(self, manager):
        rotator = ProxyRotator([
            "http://proxy1:8080",
            "http://proxy2:8080",
            "http://user:pass@proxy3:8080",
        ])
        manager.add("default", FetcherSession(proxy_rotator=rotator))

    async def parse(self, response: Response):
        # Check which proxy was used
        print(f"Proxy used: {response.meta.get('proxy')}")
        yield {"title": response.css("title::text").get("")}
```

Каждый запрос автоматически получает следующий прокси. Использованный прокси сохраняется в `response.meta["proxy"]`, поэтому можно проверить, через какой прокси была загружена каждая страница.


Для браузерных сессий потребуются небольшие изменения:

```python
from scrapling.fetchers import AsyncStealthySession, ProxyRotator

# String proxies work for all session types
rotator = ProxyRotator([
    "http://proxy1:8080",
    "http://proxy2:8080",
])

# Dict proxies (Playwright format) work for browser sessions
rotator = ProxyRotator([
    {"server": "http://proxy1:8080", "username": "user", "password": "pass"},
    {"server": "http://proxy2:8080"},
])

# Then inside the spider
def configure_sessions(self, manager):
    rotator = ProxyRotator(["http://proxy1:8080", "http://proxy2:8080"])
    manager.add("browser", AsyncStealthySession(proxy_rotator=rotator))
```

!!! info

    1. В одной сессии нельзя использовать `proxy_rotator` вместе с постоянными параметрами `proxy` или `proxies`. Выберите один вариант при настройке сессии. Позже можно переопределить прокси для отдельного запроса, как показано ниже.
    2. По умолчанию браузерные сессии используют постоянный контекст браузера с пулом вкладок. Браузер не позволяет задать отдельный прокси для каждой вкладки. Поэтому с `ProxyRotator` Fetcher автоматически создаёт отдельный контекст для каждого прокси с одной вкладкой. Когда задача вкладки завершена, вкладка и её контекст закрываются.

## Свои способы смены прокси {#custom-rotation-strategies}

По умолчанию `ProxyRotator` перебирает прокси по порядку и после последнего возвращается к первому.

Чтобы изменить это поведение, передайте свою функцию с такой сигнатурой:

```python
from scrapling.core._types import ProxyType

def my_strategy(proxies: list, current_index: int) -> tuple[ProxyType, int]:
    ...
```

Она получает список прокси и текущий индекс, а вернуть должна выбранный прокси и следующий индекс.

Ниже приведены примеры своих способов смены прокси.

### Случайный выбор {#random-rotation}

```python
import random
from scrapling.fetchers import ProxyRotator

def random_strategy(proxies, current_index):
    idx = random.randint(0, len(proxies) - 1)
    return proxies[idx], idx

rotator = ProxyRotator(
    ["http://proxy1:8080", "http://proxy2:8080", "http://proxy3:8080"],
    strategy=random_strategy,
)
```

### Выбор с весами {#weighted-rotation}

```python
import random

def weighted_strategy(proxies, current_index):
    # First proxy gets 60% of traffic, others split the rest
    weights = [60] + [40 // (len(proxies) - 1)] * (len(proxies) - 1)
    proxy = random.choices(proxies, weights=weights, k=1)[0]
    return proxy, current_index  # Index doesn't matter for weighted

rotator = ProxyRotator(proxies, strategy=weighted_strategy)
```


## Прокси для отдельного запроса {#per-request-proxy-override}

Для отдельного запроса можно заменить выбор ротатора, передав именованный аргумент `proxy=`:

```python
async def parse(self, response: Response):
    # This request uses the rotator's next proxy
    yield response.follow("/page1", callback=self.parse_page)

    # This request uses a specific proxy, bypassing the rotator
    yield response.follow(
        "/special-page",
        callback=self.parse_page,
        proxy="http://special-proxy:8080",
    )
```

Это удобно, когда странице нужен определённый прокси, например из нужного региона для доступа к местному содержимому.

## Обработка заблокированных запросов {#blocked-request-handling}

Паук умеет обнаруживать блокировки и повторять запросы. По умолчанию заблокированными считаются ответы с HTTP-статусами `401`, `403`, `407`, `429`, `444`, `500`, `502`, `503`, `504`.

Повторные попытки устроены так:

1. После получения ответа паук вызывает `is_blocked(response)`.
2. При блокировке он копирует запрос и вызывает `retry_blocked_request()`, чтобы вы могли изменить его перед повтором.
3. Запрос снова попадает в очередь с `dont_filter=True`, чтобы обойти удаление дубликатов, и с пониженным приоритетом, чтобы не повторяться сразу.
4. Это повторяется до `max_blocked_retries` раз. По умолчанию 3.

!!! tip

    1. Перед повтором аргументы `proxy`/`proxies` автоматически удаляются из запроса, чтобы ротатор назначил новый прокси.
    2. Атрибут `max_blocked_retries` не связан с повторами внутри сессии. У них разные счётчики.

### Своя проверка блокировок {#custom-block-detection}

Переопределите `is_blocked()`, чтобы добавить свои проверки:

```python
class MySpider(Spider):
    name = "my_spider"
    start_urls = ["https://example.com"]

    async def is_blocked(self, response: Response) -> bool:
        # Check status codes (default behavior)
        if response.status in {403, 429, 503}:
            return True

        # Check response content
        body = response.body.decode("utf-8", errors="ignore")
        if "access denied" in body.lower() or "rate limit" in body.lower():
            return True

        return False

    async def parse(self, response: Response):
        yield {"title": response.css("title::text").get("")}
```

### Настройка повторных попыток {#customizing-retries}

Переопределите `retry_blocked_request()`, чтобы менять запрос перед повтором. Атрибут `max_blocked_retries` задаёт число повторов заблокированного запроса. По умолчанию их 3:

```python
from scrapling.spiders import Spider, SessionManager, Request, Response
from scrapling.fetchers import FetcherSession, AsyncStealthySession


class MySpider(Spider):
    name = "my_spider"
    start_urls = ["https://example.com"]
    max_blocked_retries = 5

    def configure_sessions(self, manager: SessionManager) -> None:
        manager.add('requests', FetcherSession(impersonate=['chrome', 'firefox', 'safari']))
        manager.add('stealth', AsyncStealthySession(block_webrtc=True), lazy=True)

    async def retry_blocked_request(self, request: Request, response: Response) -> Request:
        request.sid = "stealth"
        self.logger.info(f"Retrying blocked request: {request.url}")
        return request

    async def parse(self, response: Response):
        yield {"title": response.css("title::text").get("")}
```

В этом примере проверка блокировок не менялась. Паук использует HTTP-запросы, пока не получит блокировку, затем переключается на stealth-браузер.


Объединим всё в одном примере:

```python
from scrapling.spiders import Spider, SessionManager, Request, Response
from scrapling.fetchers import FetcherSession, AsyncStealthySession, ProxyRotator


cheap_proxies = ProxyRotator([ "http://proxy1:8080", "http://proxy2:8080"])

# A format acceptable by the browser
expensive_proxies = ProxyRotator([
    {"server": "http://residential_proxy1:8080", "username": "user", "password": "pass"},
    {"server": "http://residential_proxy2:8080", "username": "user", "password": "pass"},
    {"server": "http://mobile_proxy1:8080", "username": "user", "password": "pass"},
    {"server": "http://mobile_proxy2:8080", "username": "user", "password": "pass"},
])


class MySpider(Spider):
    name = "my_spider"
    start_urls = ["https://example.com"]
    max_blocked_retries = 5

    def configure_sessions(self, manager: SessionManager) -> None:
        manager.add('requests', FetcherSession(impersonate=['chrome', 'firefox', 'safari'], proxy_rotator=cheap_proxies))
        manager.add('stealth', AsyncStealthySession(block_webrtc=True, proxy_rotator=expensive_proxies), lazy=True)

    async def retry_blocked_request(self, request: Request, response: Response) -> Request:
        request.sid = "stealth"
        self.logger.info(f"Retrying blocked request: {request.url}")
        return request

    async def parse(self, response: Response):
        yield {"title": response.css("title::text").get("")}
```
Запросы сначала идут через недорогие прокси, например из дата-центров. После блокировки они повторяются через более качественные прокси, например домашние или мобильные.
