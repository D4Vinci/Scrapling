---
title: "Сбор страниц в Markdown для RAG с помощью Scrapling"
description: "Преобразуйте ответы страниц в Markdown или соберите сайт с помощью ContentSpider. Подготовьте набор документов для разбиения на части и индексации в RAG-системе."
---

# Создание RAG-систем со Scrapling {#building-rag-systems-with-scrapling}

Качество RAG зависит от текста, который вы передаёте системе. Исходный HTML тратит токены на разметку, навигацию, скрипты и код отслеживания. Он также может содержать скрытые инструкции, которые попадут прямо в LLM. Scrapling превращает страницы и целые сайты в очищенный Markdown без участия LLM. Поэтому загрузка данных проходит быстро и не требует оплаты LLM за каждую страницу.

## Установка {#installation}

```bash
pip install "scrapling[rag]"

scrapling install
```

Дополнительная группа зависимостей `rag` устанавливает Fetcher с поддержкой преобразования в Markdown. Она также входит в `ai`, `shell` и `all`. Команда `scrapling install` скачивает зависимости браузера, которые нужны только для Fetcher, работающих через браузер.

## Одна страница в Markdown {#one-page-to-markdown}

У каждого [Response](../fetching/choosing.md#response-object) есть метод `markdown()`:

```python
from scrapling.fetchers import Fetcher

markdown = Fetcher.get("https://example.com").markdown(main_content_only=True)
```

Он работает со всеми Fetcher, поэтому для страниц за Cloudflare тоже достаточно одной строки:

```python
from scrapling.fetchers import StealthyFetcher

markdown = StealthyFetcher.fetch("https://protected.example.com", solve_cloudflare=True).markdown(main_content_only=True)
```

Вывод настраивается двумя аргументами:

- `main_content_only`: преобразовать только содержимое тега `<body>`.
- `css_selector`: преобразовать только элементы, соответствующие CSS-селектору. Все совпадения объединяются. Так можно извлечь именно ту часть, которая нужна системе, и сэкономить токены:

```python
markdown = Fetcher.get("https://example.com/docs/page").markdown(css_selector="article")
```

Независимо от аргументов перед преобразованием всегда удаляются скрипты, стили и скрытое содержимое. [MCP-сервер](mcp-server.md) использует ту же очистку для защиты ИИ-агентов от внедрения инструкций в промпт. Она удаляет элементы, скрытые встроенными стилями, элементы с `aria-hidden="true"`, скрытые слоты, теги `<template>`, HTML-комментарии и символы нулевой ширины. MCP-сервер выполняет эту очистку при `main_content_only=True`.

## Весь сайт в набор документов Markdown {#a-whole-website-to-a-markdown-corpus}

Шаблон `ContentSpider` обходит сайт и преобразует каждую страницу. Он использует [фреймворк Spider](../spiders/architecture.md), поэтому доступны параллельная обработка, AutoThrottle, соблюдение robots.txt, пауза и возобновление:

```python
from scrapling.spiders import ContentSpider

class DocsSpider(ContentSpider):
    name = "docs"
    start_urls = ["https://example.com/docs/"]
    allowed_domains = {"example.com"}
    output_dir = "docs_markdown"
    max_pages = 200

result = DocsSpider().start()
result.items.to_jsonl("docs.jsonl")
```

Каждая собранная страница становится записью с ключами `url`, `title` и `markdown`. Если задан `output_dir`, страница также записывается в Markdown-файл с именем на основе её URL. В результате приведённый выше запуск создаёт папку с файлами `.md` и файл `docs.jsonl`, готовый для загрузки в систему.

Шаблону нужен `allowed_domains`, чтобы обход не выходил за пределы целевого сайта. Доступны следующие параметры:

- `css_selector` / `main_content_only`: передаются в `markdown()` для каждой страницы. `main_content_only` включён по умолчанию.
- `output_dir`: если задан, каждая страница записывается в отдельный Markdown-файл.
- `max_pages`: максимальное число преобразованных страниц. Запросы, уже попавшие в очередь к моменту достижения лимита, могут быть выполнены, но их страницы не преобразуются. `0` по умолчанию отключает лимит.

По умолчанию обход следует по всем ссылкам на страницы внутри `allowed_domains`. Шаблон основан на [CrawlSpider](../spiders/generic-templates.md#crawlspider), поэтому можно переопределить `rules()` и использовать свой [LinkExtractor](../spiders/generic-templates.md#linkextractor-reference). `allow` ограничивает обход нужными шаблонами URL, а `deny` исключает ненужные: страницы входа, списки тегов, версии для печати и другие:

```python
from scrapling.spiders import CrawlRule, LinkExtractor, ContentSpider

class DocsSpider(ContentSpider):
    name = "docs"
    start_urls = ["https://example.com/"]
    allowed_domains = {"example.com"}

    def rules(self):
        return [CrawlRule(LinkExtractor(allow=r"/docs/", deny=[r"/docs/changelog/", r"\?print="]))]
```

`deny` имеет приоритет над `allow`. Как и в любом **CrawlSpider**, правило может содержать `priority` или хук `process_request`.

## Передача данных в векторное хранилище {#feeding-a-vector-store}

Вывод JSONL можно передать в любую систему создания эмбеддингов. Минимальный пример:

```python
import json

with open("docs.jsonl", encoding="utf-8") as f:
    for line in f:
        page = json.loads(line)
        for chunk in split_into_chunks(page["markdown"]):
            vector_store.add(text=chunk, metadata={"url": page["url"], "title": page["title"]})
```

Используйте `css_selector` в Spider, чтобы убрать повторяющиеся служебные блоки до разбиения текста на части, а не очищать их на следующих этапах. Чем меньше лишнего содержимого в эмбеддингах, тем лучше поиск.

## Работа в диалоге {#interactive-alternatives}

Если вы хотите собирать данные в диалоге, а не строить цепочку обработки, [MCP-сервер](mcp-server.md) предоставляет ИИ-чатботу те же инструменты извлечения Markdown. А [Agent Skill](agent-skill.md) учит агентов самостоятельно писать такой код.
