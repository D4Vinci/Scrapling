---
title: "Выбор между HTTP-запросами и браузером для сбора данных"
description: "Выберите Fetcher или StealthyFetcher для своей задачи. Узнайте, когда нужны прямые HTTP-запросы, выполнение JavaScript и повторное использование сессий."
---

# Основы работы с Fetcher {#fetchers-basics}

## Введение {#introduction}
Fetcher позволяют отправлять запросы и получать страницы одной строкой кода, а затем возвращают объект [Response](#response-object). У них есть много дополнительных возможностей. Начиная с v0.3, у всех Fetcher есть отдельные классы для работы с сессиями. Например, браузерный Fetcher может держать браузер открытым до завершения всех запросов, вместо того чтобы открывать несколько браузеров. Выбор зависит от вашей задачи.

До v0.2 Scrapling был только средством разбора страниц. Эти возможности появились, чтобы постепенно собрать в одной библиотеке всё необходимое для веб-скрейпинга.

> Fetcher не просто оборачивают другие библиотеки. Они используют их как движки для отправки запросов и получения страниц. Каждый Fetcher добавляет возможности, которых нет у самого движка, при этом использует его возможности и настраивает их для сбора данных.

## Обзор Fetcher {#fetchers-overview}

В Scrapling есть HTTP-классы (`Fetcher` и `AsyncFetcher`) и браузерный класс (`StealthyFetcher`), а также классы сессий для повторных запросов.

Эта таблица поможет быстро сравнить их и сделать выбор.


| Возможность | Fetcher | StealthyFetcher |
|--------------------|---------------------------------------------------|--------------------------------------------------------------------------------------------|
| Относительная скорость | 🐇🐇🐇🐇🐇 | 🐇🐇🐇 |
| Скрытность | ⭐⭐ | ⭐⭐⭐⭐⭐ |
| Средства обхода защиты от ботов | ⭐⭐ | ⭐⭐⭐⭐⭐ |
| Выполнение JavaScript | ❌ | ✅ |
| Использование памяти | ⭐ | ⭐⭐⭐ |
| Лучше подходит для | Простого сбора данных, когда достаточно HTTP-запросов | - Сайтов с динамической загрузкой <br/>- Небольших задач автоматизации <br/>- Обхода защиты разной сложности |
| Браузеры | ❌ | Chromium и Google Chrome |
| API браузера | ❌ | Playwright |
| Сложность настройки | Просто | Просто |

На следующих страницах мы подробно рассмотрим каждый из них.

## Настройка парсера во всех Fetcher {#parser-configuration-in-all-fetchers}
Все Fetcher импортируются одинаково, как вы увидите далее:
```python
from scrapling.fetchers import Fetcher, AsyncFetcher, StealthyFetcher
```
После импорта их можно использовать сразу, без создания экземпляра. Парсер будет работать с настройками по умолчанию:
```python
page = StealthyFetcher.fetch('https://example.com') 
```
Чтобы настроить парсер ([класс Selector](../parsing/main_classes.md#selector)), который обработает ответ перед возвратом, сначала выполните:
```python
from scrapling.fetchers import Fetcher
Fetcher.configure(adaptive=True, keep_comments=False)  # and the rest
```
или:
```python
from scrapling.fetchers import Fetcher
Fetcher.adaptive=True
Fetcher.keep_comments=False
```
Затем продолжайте писать код как обычно.

Доступны аргументы `adaptive`, `adaptive_domain`, `huge_tree`, `keep_comments`, `storage` и `storage_args`. Это те же аргументы, которые принимает класс [Selector](../parsing/main_classes.md#selector). Текущую конфигурацию можно в любой момент вывести командой `<fetcher_class>.display_config()`.

!!! info "Информация"

    Аргумент `adaptive` по умолчанию выключен. Включите его, чтобы использовать адаптивную функцию.

### Настройка парсера для отдельного запроса {#set-parser-config-per-request}
Приведённая выше настройка парсера действует на все запросы этого класса. Так проще работать с общими настройками.

Если для каждого запроса нужна своя конфигурация, передайте словарь в аргумент `selector_config` метода запроса (`fetch`/`get`/`post`/...).

## Объект Response {#response-object}
Объект `Response` основан на классе [Selector](../parsing/main_classes.md#selector), но содержит дополнительные сведения об ответе: заголовки, статус, cookie и другие данные, как показано ниже:
```python
from scrapling.fetchers import Fetcher
page = Fetcher.get('https://example.com')

page.status          # HTTP status code
page.reason          # Status message
page.cookies         # Response cookies as a dictionary
page.headers         # Response headers
page.request_headers # Request headers
page.history         # Response history of redirections, if any
page.body            # Raw response body as bytes
page.encoding        # Response encoding
page.meta            # Response metadata dictionary (e.g., proxy used). Mainly helpful with the spiders system.
```
Все Fetcher возвращают объект `Response`. В браузерных сессиях с `record_requests=True` методы `session.network.search(limit=None)` и `session.network.get(request_id)` также возвращают сохранённые объекты `Response`. Подробнее о сохранённых ответах API и переходе на v5 читайте в разделе [История сети](stealthy.md#network-history).

Объект `Response` также позволяет одной строкой преобразовать страницу в очищенный Markdown для LLM:
```python
markdown = Fetcher.get('https://example.com').markdown(main_content_only=True)
```
Перед преобразованием всегда удаляются скрипты, стили, скрытое содержимое и содержимое с внедрением инструкций. Аргумент `css_selector` позволяет преобразовать только выбранные элементы. Нужен набор зависимостей `rag`, который также входит в `ai`/`shell`/`all`. Подробнее читайте на странице [Создание RAG-систем](../ai/building-rag-systems.md).

!!! note "Примечание"

    В отличие от [Selector](../parsing/main_classes.md#selector), тело ответа класса `Response` начиная с v0.4 всегда хранится в байтах.
