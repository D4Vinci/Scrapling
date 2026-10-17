---
title: "Управление обходом: AutoThrottle, контрольные точки, кеш и потоковая выдача"
description: "Настройте скорость и число одновременных запросов. Узнайте о кеше ответов, паузе и возобновлении, потоковой выдаче записей и сохранении состояния."
---

# Расширенные возможности {#advanced-usages}

## Введение {#introduction}

!!! success "Что нужно знать"

    1. Прочитайте страницу [Начало работы](getting-started.md), чтобы научиться создавать и запускать простого паука.

Здесь описаны расширенные возможности пауков: управление одновременными запросами, пауза и возобновление, потоковая выдача, хуки жизненного цикла, статистика и журналирование.

## Число одновременных запросов {#concurrency-control}

Следующие атрибуты класса управляют нагрузкой при обходе:

| Атрибут | По умолчанию | Описание |
|----------------------------------|---------|------------------------------------------------------------------|
| `concurrent_requests` | `4` | Максимальное число запросов, которые обрабатываются одновременно |
| `concurrent_requests_per_domain` | `0` | Максимальное число одновременных запросов к одному домену. 0 означает отсутствие ограничения для домена |
| `download_delay` | `0.0` | Задержка перед каждым запросом в секундах |
| `robots_txt_obey` | `False` | Соблюдать правила robots.txt: Disallow, Crawl-delay, Request-rate |

```python
class PoliteSpider(Spider):
    name = "polite"
    start_urls = ["https://example.com"]

    # Be gentle with the server
    concurrent_requests = 4
    concurrent_requests_per_domain = 2
    download_delay = 1.0  # Wait 1 second between requests

    async def parse(self, response: Response):
        yield {"title": response.css("title::text").get("")}
```

При заданном `concurrent_requests_per_domain` каждый домен получает своё ограничение в дополнение к общему. Это удобно при обходе нескольких доменов: можно выполнять много запросов в целом, не перегружая отдельный сайт.

!!! tip

    `download_delay` добавляет постоянную задержку перед каждым запросом независимо от домена. Это простой способ ограничить частоту запросов.

## AutoThrottle {#autothrottle}

Постоянную задержку `download_delay` приходится подбирать: слишком малая приводит к блокировкам, слишком большая затягивает обход. AutoThrottle измеряет скорость ответов сайта и сам меняет задержку для каждого домена. Быстрые серверы обходятся быстрее, а медленные или блокирующие запросы получают меньше нагрузки.

| Атрибут | По умолчанию | Описание |
|------------------------------------|---------|-------------------------------------------------------------------|
| `autothrottle_enabled` | `False` | Включить адаптивную задержку |
| `autothrottle_start_delay` | `5.0` | Задержка перед первым запросом к домену |
| `autothrottle_max_delay` | `60.0` | Наибольшая допустимая задержка |
| `autothrottle_target_concurrency` | `None` | Целевое число одновременных запросов к домену, см. ниже |
| `autothrottle_block_backoff` | `True` | Удваивать задержку домена при каждой блокировке |

```python
class AdaptiveSpider(Spider):
    name = "adaptive"
    start_urls = ["https://example.com"]

    concurrent_requests = 8
    concurrent_requests_per_domain = 1

    autothrottle_enabled = True
    autothrottle_start_delay = 2.0
    autothrottle_max_delay = 30.0

    async def parse(self, response: Response):
        yield {"title": response.css("title::text").get("")}
```

После каждого ответа задержка приближается к времени ответа сервера. Если сайт отвечает за 0,5 секунды, задержка устанавливается примерно на 0,5 секунды. Это соответствует примерно одному выполняемому запросу. Целевое число запросов к домену выбирается так: заданный `autothrottle_target_concurrency`, затем `concurrent_requests_per_domain`, иначе 1. Поэтому отдельную цель обычно задавать не нужно: используется уже настроенное ограничение для домена, и задержка делится на это число. Резкое увеличение времени ответа учитывается сразу, без усреднения. Паук сразу замедляется при проблемах на сервере, а ускоряется постепенно.

### Замедление при блокировке {#backing-off-when-blocked}

По одному времени ответа нельзя обнаружить ограничение частоты. Ответ `429`, `403` или страница с CAPTCHA обычно приходят *быстрее* обычного содержимого. Если учитывать только время, это выглядит как повод ускориться. Поэтому любой ответ со статусом вне диапазона 2xx или ответ, который `is_blocked()` считает заблокированным, **удваивает** задержку домена:

```
0.5s -> 1s -> 2s -> 4s -> 8s ...   (up to autothrottle_max_delay)
```

Паук продолжает замедляться, пока сайт отказывает в доступе. Когда нормальные ответы возвращаются, обычное усреднение постепенно снижает задержку до скорости сервера. Работа восстанавливается без перезапуска.

Если сайт передаёт точное время ожидания в заголовке `Retry-After` ответа `429` или `503`, оно используется вместо удвоения. Поддерживается число (`Retry-After: 120`) и дата в формате HTTP.

Установите `autothrottle_block_backoff = False`, чтобы отключить это поведение и учитывать только время ответа. Тогда блокировка лишь не даст пауку ускориться.

Итоговая задержка для каждого домена доступна в статистике:

```python
result = AdaptiveSpider().start()
print(result.stats.autothrottle_delays)  # {'example.com': 0.62}
```

!!! note "Примечания"

    * `download_delay` и задержки robots.txt задают нижнюю границу, но `autothrottle_max_delay` ограничивает и её. Максимум должен быть не меньше задержки из настройки или robots.txt, которую нужно соблюдать.<br/>
    * `concurrent_requests_per_domain` выполняет две задачи: ограничивает число запросов к домену и служит целью AutoThrottle. Поэтому отдельная цель обычно не нужна. Рекомендуется задать этот параметр: пока запрос ожидает задержку домена, он занимает место в общем ограничении. Без ограничения для домена такие ожидающие запросы используют места, общие для всех доменов.<br/>
    * Измеряется полное время загрузки, включая внутренние повторы, а для браузерных сессий и время отрисовки страницы.<br/>
    * `autothrottle_max_delay` ограничивает всё, включая `Retry-After`. Если сайт просит ждать дольше этого максимума, увеличьте `autothrottle_max_delay`.<br/>
    * Вычисленные задержки не входят в контрольную точку. После паузы и возобновления каждый домен снова начинает с `autothrottle_start_delay`.

## Использование uvloop {#using-uvloop}

Метод `start()` принимает параметр `use_uvloop`, чтобы использовать более быстрый цикл событий [uvloop](https://github.com/MagicStack/uvloop)/[winloop](https://github.com/nicktimko/winloop), если он доступен:

```python
result = MySpider().start(use_uvloop=True)
```

Это может ускорить обход с большим объёмом ввода-вывода. Установите `uvloop` (Linux/macOS) или `winloop` (Windows) отдельно.

## Пауза и возобновление {#pause-resume}

Паук поддерживает корректную остановку и возобновление через контрольные точки. Чтобы включить их, передайте каталог `crawldir` в конструктор паука:

```python
spider = MySpider(crawldir="crawl_data/my_spider")
result = spider.start()

if result.paused:
    print("Crawl was paused. Run again to resume.")
else:
    print("Crawl completed!")
```

### Как это работает {#how-it-works}

1. **Пауза**: нажмите `Ctrl+C` во время обхода. Паук дождётся завершения всех текущих запросов, сохранит контрольную точку с ожидающими запросами и множеством отпечатков уже встреченных запросов, затем завершит работу.
2. **Принудительная остановка**: нажмите `Ctrl+C` ещё раз, чтобы сразу остановиться, не дожидаясь активных задач.
3. **Возобновление**: запустите паука с тем же `crawldir`. Он найдёт контрольную точку, восстановит очередь и множество отпечатков, затем продолжит работу с места остановки, пропустив `start_requests()`.
4. **Очистка**: после обычного завершения обхода, а не паузы, файлы контрольных точек удаляются автоматически.

**Контрольные точки также сохраняются периодически во время обхода. По умолчанию каждые 5 минут.**

Интервал можно изменить:

```python
# Save checkpoint every 2 minutes
spider = MySpider(crawldir="crawl_data/my_spider", interval=120.0)
```

При записи контрольной точки используется временный файл. Предыдущая контрольная точка заменяется только после успешной записи.

!!! warning "Данные контрольной точки"

    При включении `crawldir` модуль `pickle` в Python должен уметь сохранять значения ожидающих запросов, включая `meta` и аргументы запросов. Если сохранить значение невозможно, сохранение контрольной точки завершается ошибкой и обход останавливается. Объект `Selector` может работать в обработчике, но его нельзя сохранить таким способом.

    Храните извлечённые значения, например строки или числа, вместо объектов `Selector`. Списки и словари также должны содержать только значения, которые можно сохранить:

    ```python
    yield response.follow("/details", meta={"title": str(response.css("h1::text").get(""))})
    ```

!!! tip

    При использовании `start()` нажатие `Ctrl+C` корректно завершает паука, даже если контрольные точки не включены. Повторное нажатие сразу останавливает его.

### Как узнать, что обход возобновлён {#knowing-if-youre-resuming}

Хук `on_start()` получает флаг `resuming`:

```python
async def on_start(self, resuming: bool = False):
    if resuming:
        self.logger.info("Resuming from checkpoint!")
    else:
        self.logger.info("Starting fresh crawl")
```

## Режим разработки {#development-mode}

При доработке `parse()` повторная загрузка страниц на каждом запуске занимает время и создаёт лишнюю нагрузку. Режим разработки сохраняет каждый ответ на диск при первом запуске, а затем читает ответы с диска. Можно менять селекторы и запускать паука сколько угодно раз без повторной загрузки тех же страниц.

Установите у паука `development_mode = True`:

```python
class MySpider(Spider):
    name = "my_spider"
    start_urls = ["https://example.com"]
    development_mode = True

    async def parse(self, response: Response):
        yield {"title": response.css("title::text").get("")}
```

Первый запуск загружает страницы как обычно и сохраняет ответы на диск. Последующие запуски берут ответы на те же запросы из кеша, без загрузки страниц. При `robots_txt_obey=True` правила robots.txt проверяются перед поиском в кеше.

### Расположение кеша {#cache-location}

По умолчанию ответы сохраняются в `.scrapling_cache/{spider.name}/` относительно текущего рабочего каталога. Это каталог, из которого вы запустили паука, **а не** каталог его скрипта. Путь можно изменить через `development_cache_dir`:

```python
class MySpider(Spider):
    name = "my_spider"
    start_urls = ["https://example.com"]
    development_mode = True
    development_cache_dir = "/tmp/my_spider_cache"
```

### Как это работает {#how-it-works_1}

1. **Ключ кеша**: отпечаток запроса. Изменение влияющих на него атрибутов (`fp_include_kwargs`, `fp_include_headers`, `fp_keep_fragments`) приводит к новой загрузке.
2. **Формат хранения**: отдельный JSON-файл `{fingerprint_hex}.json` для каждого ответа. Тело кодируется в base64 для точного сохранения двоичных данных. Запись атомарная: временный файл и переименование.
3. **Чтение из кеша**: при совпадении движок пропускает загрузку страницы, включая `download_delay`, ограничение частоты и повторы через `is_blocked()`. Ответ из кеша сразу передаётся обработчику.
4. **Статистика**: запросы из кеша по-прежнему учитываются в `requests_count`, `response_bytes` и счётчиках статусов. Поэтому статистика выглядит как при обычном обходе. Дополнительные счётчики `cache_hits` и `cache_misses` показывают работу кеша.

### Очистка кеша {#clearing-the-cache}

Автоматического срока действия нет. Чтобы заново загрузить страницы, удалите каталог кеша или напрямую вызовите `clear()` у менеджера.

!!! warning

    Режим разработки предназначен только для разработки. Срок действия ответов в кеше не ограничен, а чтение из него пропускает ограничение частоты и повторы заблокированных запросов. Не оставляйте `development_mode = True` у паука в рабочей среде.

## Потоковая выдача {#streaming}

Для долгих обходов или приложений, которым нужны записи сразу после извлечения, используйте `stream()` вместо `start()`:

```python
import anyio

async def main():
    spider = MySpider()
    async for item in spider.stream():
        print(f"Got item: {item}")
        # Access real-time stats
        print(f"Items so far: {spider.stats.items_scraped}")
        print(f"Requests made: {spider.stats.requests_count}")

anyio.run(main)
```

Главные отличия от `start()`:

- `stream()` нужно вызывать из асинхронного контекста.
- Записи выдаются по одной сразу после извлечения, а не собираются в список.
- Во время перебора доступен `spider.stats` с текущей статистикой.

!!! abstract

    Все показатели, доступные через `spider.stats`, описаны [ниже](#results-statistics).

Потоковую выдачу можно совместить с контрольными точками. Так удобно создавать интерфейсы с текущими данными и возможностью поставить обход на паузу или возобновить его.

```python
import anyio

async def main():
    spider = MySpider(crawldir="crawl_data/my_spider")
    async for item in spider.stream():
        print(f"Got item: {item}")
        # Access real-time stats
        print(f"Items so far: {spider.stats.items_scraped}")
        print(f"Requests made: {spider.stats.requests_count}")

anyio.run(main)
```
В этом примере можно вызвать `spider.pause()`, чтобы остановить паука. Без включённых контрольных точек этот вызов просто завершит обход.

## Хуки жизненного цикла {#lifecycle-hooks}

Паук предоставляет хуки, которые можно переопределить для своей логики на разных этапах обхода:

### on_start {#on_start}

Вызывается перед началом обхода. Подходит для подготовки, например загрузки данных или создания ресурсов:

```python
async def on_start(self, resuming: bool = False):
    self.logger.info("Spider starting up")
    # Load seed URLs from a database, initialize counters, etc.
```

### on_close {#on_close}

Вызывается после завершения или приостановки обхода. Подходит для освобождения ресурсов:

```python
async def on_close(self):
    self.logger.info("Spider shutting down")
    # Close database connections, flush buffers, etc.
```

### on_error {#on_error}

Вызывается, когда запрос завершается исключением. Подходит для учёта ошибок и своей логики восстановления:

```python
async def on_error(self, request: Request, error: Exception):
    self.logger.error(f"Failed: {request.url} - {error}")
    # Log to error tracker, save failed URL for later, etc.
```

### on_scraped_item {#on_scraped_item}

Вызывается для каждой извлечённой записи перед добавлением в результаты. Верните запись с изменениями или без них, чтобы сохранить её, либо `None`, чтобы отбросить:

```python
async def on_scraped_item(self, item: dict) -> dict | None:
    # Drop items without a title
    if not item.get("title"):
        return None

    # Modify items (e.g., add timestamps)
    item["scraped_at"] = "2026-01-01"
    return item
```

!!! tip

    Через этот хук можно передавать записи в свои цепочки обработки и удалять их из результатов паука.

### start_requests {#start_requests}

Переопределите `start_requests()`, чтобы создавать начальные запросы своей логикой вместо `start_urls`:

```python
async def start_requests(self):
    # POST request to log in first
    yield Request(
        "https://example.com/login",
        method="POST",
        data={"user": "admin", "pass": "secret"},
        callback=self.after_login,
    )

async def after_login(self, response: Response):
    # Now crawl the authenticated pages
    yield response.follow("/dashboard", callback=self.parse)
```

## Результаты и статистика {#results-statistics}

`CrawlResult`, возвращаемый `start()`, содержит извлечённые записи и подробную статистику:

```python
result = MySpider().start()

# Items
print(f"Total items: {len(result.items)}")
result.items.to_json("output.json", indent=True)

# Did the crawl complete?
print(f"Completed: {result.completed}")
print(f"Paused: {result.paused}")

# Statistics
stats = result.stats
print(f"Requests: {stats.requests_count}")
print(f"Failed: {stats.failed_requests_count}")
print(f"Blocked: {stats.blocked_requests_count}")
print(f"Offsite filtered: {stats.offsite_requests_count}")
print(f"Robots.txt disallowed: {stats.robots_disallowed_count}")
print(f"Cache hits: {stats.cache_hits}")
print(f"Cache misses: {stats.cache_misses}")
print(f"Items scraped: {stats.items_scraped}")
print(f"Items dropped: {stats.items_dropped}")
print(f"Response bytes: {stats.response_bytes}")
print(f"Duration: {stats.elapsed_seconds:.1f}s")
print(f"Speed: {stats.requests_per_second:.1f} req/s")
```

### Подробная статистика {#detailed-stats}

Объект `CrawlStats` содержит подробные показатели:

```python
stats = result.stats

# Status code distribution
print(stats.response_status_count)
# {'status_200': 150, 'status_404': 3, 'status_403': 1}

# Bytes downloaded per domain
print(stats.domains_response_bytes)
# {'example.com': 1234567, 'api.example.com': 45678}

# Requests per session
print(stats.sessions_requests_count)
# {'http': 120, 'stealth': 34}

# Proxies used during the crawl
print(stats.proxies)
# ['http://proxy1:8080', 'http://proxy2:8080']

# Log level counts
print(stats.log_levels_counter)
# {'debug': 200, 'info': 50, 'warning': 3, 'error': 1, 'critical': 0}

# Timing information
print(stats.start_time)       # Unix timestamp when crawl started
print(stats.end_time)         # Unix timestamp when crawl finished
print(stats.download_delay)   # The download delay used (seconds)

# Concurrency settings used
print(stats.concurrent_requests)             # Global concurrency limit
print(stats.concurrent_requests_per_domain)  # Per-domain concurrency limit

# AutoThrottle
print(stats.autothrottle_enabled)  # Whether the adaptive delay was on
print(stats.autothrottle_delays)   # Final delay per domain, {'example.com': 0.62}

# Custom stats (set by your spider code)
print(stats.custom_stats)
# {'login_attempts': 3, 'pages_with_errors': 5}

# Export everything as a dict
print(stats.to_dict())
```

## Журналирование {#logging}

У паука есть встроенный logger, доступный через `self.logger`. В нём уже указано имя паука, а поведение можно настроить:

| Атрибут | По умолчанию | Описание |
|-----------------------|--------------------------------------------------------------|----------------------------------------------------|
| `logging_level` | `logging.DEBUG` | Минимальный уровень сообщений |
| `logging_format` | `"[%(asctime)s]:({spider_name}) %(levelname)s: %(message)s"` | Формат сообщения |
| `logging_date_format` | `"%Y-%m-%d %H:%M:%S"` | Формат даты в сообщениях |
| `log_file` | `None` | Путь к файлу журнала в дополнение к выводу в консоль |

```python
import logging

class MySpider(Spider):
    name = "my_spider"
    start_urls = ["https://example.com"]
    logging_level = logging.INFO
    log_file = "logs/my_spider.log"

    async def parse(self, response: Response):
        self.logger.info(f"Processing {response.url}")
        yield {"title": response.css("title::text").get("")}
```

Каталог файла журнала создаётся автоматически, если его нет. Консоль и файл используют один формат.
