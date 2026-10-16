---
title: "Шаблоны пауков для ссылок, карт сайта, фидов и Markdown"
description: "Выберите CrawlSpider, SitemapSpider, XMLFeedSpider, CSVFeedSpider или ContentSpider. Задайте правила для сбора страниц, записей фидов или набора документов Markdown."
---

# Общие шаблоны пауков {#generic-spider-templates}

Большинство обходов строится по одному из двух правил: переходить по ссылкам заданного вида или обходить все URL из карты сайта. В Scrapling есть шаблоны для обоих вариантов, чтобы не писать один и тот же `parse()` каждый раз.

`CrawlSpider` и `SitemapSpider` используют `LinkExtractor`, который извлекает URL из `Response` или проверяет отдельный URL через `matches()`. `SitemapSpider` также сам разбирает sitemap.xml / sitemap_index.xml, в том числе сжатые gzip.

`LinkExtractor` можно использовать прямо в любом `Spider.parse()`. Шаблоны лишь связывают готовые компоненты за вас.

## CrawlSpider {#crawlspider}

`CrawlSpider` автоматически переходит по ссылкам на основе заданных правил.

```python
from scrapling.spiders import CrawlSpider, CrawlRule, LinkExtractor

class QuotesSpider(CrawlSpider):
    name = "blog"
    start_urls = ["https://quotes.toscrape.com/"]

    def rules(self):
        return [
            CrawlRule(LinkExtractor(allow=r"/author/"), callback=self.parse_author),
            CrawlRule(LinkExtractor(allow=r"/page/\d+/")),  # follow pagination, no callback
        ]

    async def parse_author(self, response):
        yield {
            '.author-title': response.css('.author-title::text').get(),
            "birthday": response.css('.author-born-date::text').get(),
            "url": response.url,
        }

result = QuotesSpider().start()
```

`CrawlRule` связывает `LinkExtractor` с необязательным `callback` (методом паука), необязательным `priority` для создаваемого `Request` и необязательным `process_request` (методом, который меняет каждый `Request` перед выдачей). По умолчанию `parse()` применяет все правила к каждому ответу и выдаёт `Request` для каждого подходящего URL.

Если в правиле не указан обработчик, подходящие URL передаются в обычный `parse()` паука. Это удобно для перехода между страницами: извлекайте ссылки на следующую страницу и продолжайте обход без отдельного обработчика.

### Порядок обхода {#crawl-order}

Задайте `crawl_strategy` у `CrawlSpider` или его подклассов, включая `ContentSpider`, чтобы выбрать порядок ожидающих запросов:

| `crawl_strategy` | Порядок при одинаковом `Request.priority` |
|------------------|------------------------------------------|
| `"bfs"` (по умолчанию) | Сначала запрос, раньше попавший в очередь |
| `"dfs"` | Сначала запрос, позже попавший в очередь |

Планировщик сначала берёт запросы с большим `Request.priority`. Стратегия определяет порядок только для запросов с одинаковым приоритетом.

Установите `concurrent_requests = 1`, чтобы обрабатывать запросы по одному в выбранном порядке. Повторные URL по-прежнему отбрасываются: повторное обнаружение URL не перемещает его запрос в очереди. При одновременных запросах страницы могут завершаться в другом порядке, а уровни и ветви обхода могут пересекаться.

При возобновлении с контрольной точки сохраняйте прежнее значение `crawl_strategy`.

### Правила вместе со своей логикой {#combining-rules-with-custom-logic}

Переопределите `parse()` и вызовите `super().parse(response)`, чтобы совместить правила со своими результатами:

```python
class MySpider(CrawlSpider):
    def rules(self):
        return [CrawlRule(LinkExtractor(allow=r"/posts/"), callback=self.parse_post)]

    async def parse(self, response):
        yield {"page_url": response.url}
        async for req in super().parse(response):
            yield req
```

### Изменение запросов через `process_request` {#mutating-requests-with-process_request}

```python
def add_priority(self, request, response):
    request.priority = 10
    return request

def rules(self):
    return [CrawlRule(
        LinkExtractor(allow=r"/posts/"),
        callback=self.parse_post,
        process_request=self.add_priority,
    )]
```

## SitemapSpider {#sitemapspider}

`SitemapSpider` начинает обход с URL из sitemap.xml. Он использует тот же API `rules()`, что и `CrawlSpider`, поэтому принцип работы одинаковый.

```python
from scrapling.spiders import SitemapSpider, CrawlRule, LinkExtractor

class MySitemap(SitemapSpider):
    name = "sm"
    sitemap_urls = ["https://example.com/sitemap.xml"]

    def rules(self):
        return [
            CrawlRule(LinkExtractor(allow=r"/posts/"), callback=self.parse_post),
            CrawlRule(LinkExtractor(allow=r"/products/"), callback=self.parse_product),
        ]

    async def parse_post(self, response):
        yield {"title": response.css("h1::text").get()}

    async def parse_product(self, response):
        yield {"sku": response.css(".sku::text").get()}

result = MySitemap().start()
```

### Как выбирается обработчик URL {#how-urls-are-dispatched}

Для каждого URL из карты сайта `SitemapSpider` по порядку вызывает `LinkExtractor.matches(url)` каждого правила. Выбирается первое совпадение, и выдаётся `Request` с обработчиком этого правила. Если совпадений нет, а `rules()` не пуст, URL отбрасывается. Если `rules()` возвращает пустой список, все URL передаются в `parse()` паука. Без переопределения этот метод по умолчанию вызывает `NotImplementedError`.

### Индексы карт сайта {#sitemap-indexes}

Если `SitemapSpider` встречает `<sitemapindex>` (список карт сайта), он автоматически переходит в каждую вложенную карту. Чтобы выбрать только нужные вложенные карты, задайте `sitemap_follow` как `LinkExtractor`:

```python
class MySitemap(SitemapSpider):
    name = "sm"
    sitemap_urls = ["https://example.com/sitemap.xml"]
    sitemap_follow = LinkExtractor(allow=r"/posts-sitemap-\d+\.xml")  # only post sitemaps
```

### Поддержка robots.txt {#robotstxt-support}

Укажите URL `robots.txt` прямо в `sitemap_urls`. `SitemapSpider` распознает файл, извлечёт все указанные карты сайта и обойдёт их:

```python
class MySitemap(SitemapSpider):
    name = "sm"
    sitemap_urls = ["https://example.com/robots.txt"]
```

### URL на других языках {#alternate-language-urls}

Установите `sitemap_alternate_links = True`, чтобы передавать в правила также URL из `<xhtml:link rel="alternate" hreflang="...">`.

## XMLFeedSpider {#xmlfeedspider}

`XMLFeedSpider` перебирает узлы XML-фида: RSS, Atom, товарного фида и других. Задайте нужное имя узла в `itertag` (по умолчанию `"item"`) и переопределите `parse_node()`. Этот метод вызывается для каждого подходящего узла:

```python
from scrapling.spiders import XMLFeedSpider

class RSSSpider(XMLFeedSpider):
    name = "rss"
    start_urls = ["https://example.com/feed.xml"]
    itertag = "item"

    async def parse_node(self, response, node):
        yield {
            "title": node.findtext("title"),
            "link": node.findtext("link"),
            "date": node.findtext("pubDate"),
        }

result = RSSSpider().start()
```

Как и другие обработчики, `parse_node()` может выдавать объекты `Request`, например `response.follow(node.findtext("link"), callback=self.parse_post)`, чтобы обходить страницы, на которые ссылается фид.

### Выбор и разбор узлов {#how-nodes-are-matched-and-parsed}

В `parse_node()` передаётся элемент `lxml` без пространств имён. Поэтому `node.findtext("title")`, `node.find("thumbnail").get("url")` и чувствительный к регистру `node.xpath(...)` работают с любым фидом без карты пространств имён. Простое значение `itertag`, например `"entry"`, выбирает узлы по имени независимо от пространства имён. Это подходит для Atom и большинства фидов с пространствами имён. Чтобы выбрать узел из определённого пространства имён, используйте `itertag` с префиксом и задайте этот префикс в `namespaces`:

```python
class ThumbnailSpider(XMLFeedSpider):
    name = "thumbs"
    start_urls = ["https://example.com/feed.xml"]
    itertag = "media:thumbnail"
    namespaces = (("media", "http://search.yahoo.com/mrss/"),)

    async def parse_node(self, response, node):
        yield {"thumbnail": node.get("url")}
```

Фиды gzip (`.xml.gz` или с типом содержимого gzip) распаковываются автоматически с той же защитой, что и у паука для карт сайта. Некорректный XML вызывает предупреждение в журнале, а не остановку обхода.

## CSVFeedSpider {#csvfeedspider}

`CSVFeedSpider` перебирает строки CSV-фида. Переопределите `parse_row()`, который получает каждую строку как словарь с именами столбцов в качестве ключей:

```python
from scrapling.spiders import CSVFeedSpider

class PriceSpider(CSVFeedSpider):
    name = "prices"
    start_urls = ["https://example.com/products.csv"]

    async def parse_row(self, response, row):
        yield {"product": row["title"], "price": float(row["price"])}

result = PriceSpider().start()
```

По умолчанию первая строка служит заголовком. Если заголовка нет, задайте имена столбцов через `headers`. Для фидов с нестандартными разделителями используйте `delimiter`/`quotechar`:

```python
class PriceSpider(CSVFeedSpider):
    name = "prices"
    start_urls = ["https://example.com/products.csv"]
    headers = ["title", "price", "url"]
    delimiter = ";"
```

Фиды gzip здесь также распаковываются автоматически, как показано выше для **XMLFeedSpider**.

<a id="sitetomarkdownspider"></a>

## ContentSpider {#contentspider}

`ContentSpider` основан на **CrawlSpider**. Он обходит сайт и преобразует каждую страницу в очищенный Markdown для LLM. На каждую страницу выдаётся одна запись, а при необходимости создаётся отдельный Markdown-файл:

```python
from scrapling.spiders import ContentSpider

class DocsSpider(ContentSpider):
    name = "docs"
    start_urls = ["https://example.com/docs/"]
    allowed_domains = {"example.com"}
    output_dir = "docs_markdown"

result = DocsSpider().start()
```

Нужно задать `allowed_domains`, чтобы ограничить обход целевым сайтом. Полное руководство со всеми параметрами и передачей результатов в RAG находится на странице [Создание RAG-систем](../ai/building-rag-systems.md).

## Прямое использование `LinkExtractor` {#using-linkextractor-directly}

Шаблоны необязательны. `LinkExtractor` работает в любом обычном `Spider`:

```python
from scrapling.spiders import Spider, LinkExtractor

class CustomSpider(Spider):
    name = "custom"
    start_urls = ["https://example.com"]

    def __init__(self):
        super().__init__()
        self._links = LinkExtractor(allow=r"/posts/", deny_domains="ads.example.com")

    async def parse(self, response):
        for url in self._links.extract(response):
            yield response.follow(url, callback=self.parse_post)

    async def parse_post(self, response):
        yield {"title": response.css("h1::text").get()}
```

## Справочник LinkExtractor {#linkextractor-reference}

| Аргумент | По умолчанию | Описание |
|-------------------|----------------------|---------------------------------------------------------------------------------------------------|
| `allow` | `()` | Шаблоны URL, которые нужно оставить. Пустое значение допускает все URL. Строка, скомпилированный `Pattern` или перебираемый объект с такими значениями |
| `deny` | `()` | Шаблоны URL, которые нужно отбросить. Всегда имеют приоритет над `allow` |
| `allow_domains` | `()` | Разрешённые имена хостов. Поддомены учитываются автоматически: `example.com` разрешает `api.example.com` |
| `deny_domains` | `()` | Запрещённые имена хостов |
| `restrict_css` | `()` | CSS-селекторы, ограничивающие область поиска ссылок в DOM |
| `restrict_xpath` | `()` | XPath-селекторы, ограничивающие область поиска ссылок в DOM |
| `tags` | `("a", "area")` | Теги элементов, в которых нужно искать ссылки |
| `attrs` | `("href",)` | Атрибуты этих тегов, из которых читаются URL |
| `canonicalize` | `True` | Сортировать параметры запроса и нормализовать путь |
| `strip` | `True` | Удалять пробельные символы по краям извлечённых URL |
| `keep_fragment` | `False` | Сохранять `#fragment` при нормализации |
| `deny_extensions` | `IGNORED_EXTENSIONS` | Исключаемые расширения файлов: pdf, zip, изображения, видео и другие |
| `process` | `None` | Необязательный вызываемый объект для каждого извлечённого URL перед фильтрацией. Верните значение, которое считается ложным, чтобы отбросить URL |

`LinkExtractor.extract(response)` возвращает `list[str]` с абсолютными URL после фильтрации и удаления дубликатов.

`LinkExtractor.matches(url)` возвращает `bool`. Это фильтр по самому URL: allow/deny/домен/расширение. `SitemapSpider` использует его для выбора URL без `Response`.
