---
title: "Парсинг Scrapling в Spider на Scrapy"
description: "Преобразуйте ответы Scrapy в Scrapling или добавьте декоратор к обработчику. Сохраните свой краулер Scrapy и используйте селекторы и адаптивный парсинг Scrapling."
---

# Интеграция Scrapling со Scrapy {#integrating-scrapling-into-scrapy}

Если у вас уже есть проект Scrapy, его не нужно переписывать, чтобы использовать API парсинга Scrapling. Интеграция преобразует ответы Scrapy в объекты [Response](../fetching/choosing.md#response-object) Scrapling прямо в обработчиках Spider. Scrapy продолжает выполнять обход, а Scrapling отвечает за парсинг.

!!! note "Установка"

    Интеграция работает с обычной установкой Scrapling (`pip install scrapling`), без дополнительных групп зависимостей. Нужен только установленный Scrapy, который уже есть в проекте Scrapy.

## Использование {#usage}

Добавьте декоратор `scrapling_response` к любому обработчику Spider. Получаемый аргумент `response` станет объектом `Response` Scrapling:

```python
import scrapy
from scrapling.integrations.scrapy import scrapling_response


class QuotesSpider(scrapy.Spider):
    name = "quotes"
    start_urls = ["https://quotes.toscrape.com"]

    @scrapling_response
    def parse(self, response):  # `response` is now a Scrapling Response
        first_quote = response.find_by_text("The world as we have created it", partial=True)
        for quote in [first_quote, *first_quote.find_similar()]:
            card = quote.parent
            yield {
                "text": quote.get_all_text(strip=True),
                "author": card.find("small", class_="author").text,
                "tags": [tag.text for tag in card.find_all("a", class_="tag")],
            }
        next_page = response.css("li.next a::attr(href)").get()
        if next_page:
            yield scrapy.Request(response.urljoin(next_page), callback=self.parse)
```

Декоратор работает со всеми видами обработчиков Scrapy: обычными функциями, генераторами, корутинами и асинхронными генераторами. Обёртка сохраняет вид, имя и строку документации обработчика, поэтому проверка обработчиков и контракты Scrapy продолжают работать.

Декоратору можно передать настройки [Selector](../parsing/main_classes.md#selector). Они попадут в создаваемый `Response`:

```python
    @scrapling_response(adaptive=True, keep_comments=True)
    def parse_product(self, response):
        ...
```

Если ответ Scrapy доступен вне обработчика, например в middleware или конвейере обработки, используйте преобразователь напрямую:

```python
from scrapling.integrations.scrapy import convert_response

scrapling_response = convert_response(scrapy_response, keep_comments=False)
```

## Примечания {#notes}

- Для следующих страниц возвращайте через yield `scrapy.Request(response.urljoin(href))`, как в примере выше. Метод `Response.follow()` Scrapling создаёт запросы для [системы Spider в Scrapling](../spiders/getting-started.md), которые Scrapy не понимает.
- Словарь `meta` ответа копируется поверхностно, поэтому объекты, сохранённые другими middleware, остаются доступны. Например, при использовании `scrapy-playwright` страница по-прежнему находится в `response.meta["playwright_page"]`.
- Cookie извлекаются из исходных заголовков `Set-Cookie` и помещаются в словарь `cookies` ответа.
