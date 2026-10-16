---
title: "Scrapling: фреймворк для веб-скрапинга на Python"
description: "Scrapling: простой веб-скрапинг для современного интернета!"
---

<style>
.md-typeset h1 {
  display: none;
}
[data-md-color-scheme="default"] .only-dark { display: none; }
[data-md-color-scheme="slate"] .only-light { display: none; }
</style>

<br/>
<div align="center">
    <a href="index.html" alt="Обложка">
        <img alt="Scrapling" src="assets/cover_light.svg" class="only-light">
        <img alt="Scrapling" src="assets/cover_dark.svg" class="only-dark">
    </a>
</div>

<h2 align="center"><i>Простой веб-скрапинг для современного интернета</i></h2><br>

Scrapling объединяет быстрые HTTP-запросы, скрытные браузеры, мощный разбор страниц и параллельный обход сайтов в одной библиотеке Python.

Загружайте статические страницы, выполняйте JavaScript, работайте с сайтами и извлекайте данные из API этих сайтов. Создавайте краулеры с повторным использованием сессий, сменой прокси, автоматическими повторами, паузой и продолжением работы, а также готовым экспортом данных.

Используйте Scrapling из Python, терминала или AI-агента через MCP-сервер и Agent Skill. Библиотека помогает на всех этапах: от извлечения нескольких полей до сохранения целого сайта в виде чистых Markdown-файлов.

## Что можно сделать со Scrapling {#what-you-can-do-with-scrapling}

- **[Загрузка и работа с сайтами](fetching/choosing.md)**: быстрые HTTP-запросы, скрытные браузеры, выполнение JavaScript, прохождение Cloudflare Turnstile и Interstitial, постоянные сессии и запись фоновых API-ответов.
- **[Разбор и извлечение данных](parsing/selection.md)**: CSS, XPath, поиск по тексту и регулярным выражениям, поиск элементов после изменений страницы, поиск похожих элементов и чистый Markdown.
- **[Обход и экспорт](spiders/getting-started.md)**: параллельные Spider, смена прокси, повторы, AutoThrottle, пауза и продолжение, потоковая выдача, готовые шаблоны и экспорт в JSON, JSONL, CSV и XML.
- **[Сбор данных с AI или из терминала](ai/mcp-server.md)**: MCP-сервер для работы AI-агентов с сайтами и данными, Agent Skill, команды CLI и интерактивная оболочка.

Начните с одной страницы:

```python
from scrapling.fetchers import Fetcher

page = Fetcher.get('https://quotes.toscrape.com/')
quotes = page.css('.quote .text::text').getall()
print(quotes)
```

Или используйте Spider для обхода многих страниц:

```python
from scrapling.spiders import Spider, Response

class QuotesSpider(Spider):
    name = "quotes"
    start_urls = ["https://quotes.toscrape.com/"]

    async def parse(self, response: Response):
        for quote in response.css('.quote'):
            yield {
                "text": quote.css('.text::text').get(),
                "author": quote.css('.author::text').get(),
            }

result = QuotesSpider().start()
print(len(result.items))
result.items.to_json("quotes.json")
```

Код выведет `10` и сохранит цитаты с авторами в `quotes.json`.

## Главные спонсоры {#top-sponsors}

--8<-- "sponsors.html"

<i><sub>Хотите разместить здесь рекламу? Выберите план [здесь](https://github.com/sponsors/D4Vinci) и получите все его преимущества!</sub></i>

## Основные возможности {#key-features}

### Spider: всё для обхода сайтов {#spiders-a-full-crawling-framework}
- 🕷️ **API Spider в стиле Scrapy**: задайте `start_urls`, асинхронные обработчики `parse` и объекты `Request`/`Response`.
- ⚡ **Параллельный обход**: настройте число одновременных запросов, ограничения для каждого домена и задержки между загрузками.
- 🔄 **Несколько сессий**: используйте HTTP-запросы и скрытные браузеры без окна в одном Spider. Выбирайте сессию для запроса по её ID.
- 💾 **Пауза и продолжение**: сохраняйте ожидающие запросы и посещённые URL с помощью `crawldir`. Нажмите Ctrl+C для корректной остановки, затем запустите Spider с той же папкой.
- 📡 **Потоковая выдача**: получайте данные сразу после извлечения через `async for item in spider.stream()` и следите за статистикой в реальном времени. Удобно для интерфейсов, обработки данных и долгих обходов.
- 🛡️ **Обнаружение блокировок**: заблокированные запросы автоматически обнаруживаются и повторяются. Логику можно настроить.
- 🚦 **AutoThrottle**: больше не нужно угадывать задержки. Spider сам меняет задержку для каждого домена по скорости ответа сайта. При блокировках или ограничении частоты запросов он удваивает её либо ждёт время из `Retry-After`, а затем снова ускоряется.
- 🤖 **Соблюдение robots.txt**: включите `robots_txt_obey`, чтобы учитывать `Disallow`, `Crawl-delay` и `Request-rate`. Правила кешируются для каждого домена.
- 🧪 **Режим разработки**: сохраните ответы на диск при первом запуске и используйте их снова. Меняйте логику `parse()` без повторных обращений к серверам.
- 🧩 **Готовые шаблоны Spider**: `CrawlSpider` обходит ссылки по правилам, `SitemapSpider` использует sitemap и robots.txt, `XMLFeedSpider`/`CSVFeedSpider` читают ленты XML/RSS и CSV, а `ShopifySpider` собирает товары из открытых магазинов Shopify, по одной записи на вариант.
- 🔗 **Извлечение ссылок**: `LinkExtractor` поддерживает разрешающие и запрещающие шаблоны, фильтры доменов и расширений, выбор области через CSS/XPath и приведение URL к единому виду. Используйте его в шаблонах или отдельно.
- 📦 **Готовый экспорт**: сохраняйте результаты через хуки и собственную обработку либо в JSON, JSONL, CSV и XML через `result.items.to_json()`, `to_jsonl()`, `to_csv()` и `to_xml()`.

### Загрузка сайтов с поддержкой сессий {#advanced-websites-fetching-with-session-support}
- **HTTP-запросы**: `Fetcher` отправляет быстрые и скрытные запросы. Он умеет имитировать TLS-отпечаток и заголовки браузера, а также использовать HTTP/3.
- **Динамические страницы**: `StealthyFetcher` загружает сайты с полной автоматизацией браузера. Поддерживаются Chromium из Playwright и Google Chrome.
- **Обход защиты от ботов**: `StealthyFetcher` скрывает признаки автоматизации и подменяет отпечаток браузера. Он автоматически проходит все виды проверок Cloudflare Turnstile и Interstitial.
- **Управление сессиями**: `FetcherSession` и `StealthySession` сохраняют cookie и состояние между запросами.
- **Смена прокси**: `ProxyRotator` перебирает прокси по кругу или по вашим правилам во всех типах сессий. Для отдельного запроса можно указать другой прокси.
- **Блокировка доменов и рекламы**: блокируйте запросы к выбранным доменам и их поддоменам. В браузерных Fetcher можно включить блокировку рекламы, которая охватывает около 3 500 рекламных и отслеживающих доменов.
- **Защита от утечек DNS**: включите DNS-over-HTTPS, чтобы отправлять DNS-запросы через DoH от Cloudflare и не допускать утечек DNS при работе с прокси.
- **Удалённые браузеры**: подключайтесь к уже запущенному браузеру через CDP с помощью `cdp_url`. Браузер может работать на том же компьютере, другом сервере или у провайдера браузерных услуг. Параметр `executable_path` позволяет указать собственную сборку Chromium для любого браузерного Fetcher.
- **Запись фоновых API-ответов**: включите `record_requests=True` в браузерной сессии, затем ищите сохранённые ответы через `session.network.search(limit=None)`. Читайте API-данные и HTTP-ошибки от разных загрузок страниц без повторной отправки запросов. История имеет ограниченный размер и сохраняет текстовые тела ответов.
- **Асинхронная работа**: все Fetcher поддерживают асинхронные вызовы. Есть и отдельные классы асинхронных сессий.

### Разбор и извлечение данных {#parsing-and-data-extraction}
- 🔄 **Поиск элементов после изменений**: алгоритмы сходства находят элементы снова, даже если сайт изменился.
- 🎯 **Гибкий поиск**: используйте CSS, XPath, фильтры, текст, регулярные выражения и другие способы.
- 🔍 **Похожие элементы**: автоматически находите элементы, похожие на уже найденные.

### Возможности для AI {#ai-features}
- 🤖 **MCP-сервер**: AI-боты и агенты, такие как Claude и Cursor, могут собирать данные через Scrapling. Им доступны HTTP-запросы, действия в браузере, снимки экрана, сохранённый вход и фоновые API-ответы. Скрытный браузер и нужные инструменты позволяют подходящим AI-моделям проходить любые CAPTCHA во время работы, а проверки Cloudflare обрабатываются встроенным решением. Сервер уменьшает объём данных для модели, блокирует рекламу и защищает от Prompt Injection. Есть подключение к удалённым браузерам по CDP и HTTP-транспорт с настройками аутентификации. ([Демонстрация](https://www.youtube.com/watch?v=qyFk3ZNwOxE))
- 🧠 **Agent Skill**: готовый к установке [Agent Skill](ai/agent-skill.md) знакомит агента со всей библиотекой. Он помогает писать код под текущий API без догадок.
- 📚 **Markdown для RAG**: одна строка (`page.markdown()`) превращает страницу в чистый и безопасный Markdown для LLM. Шаблон `ContentSpider` сохраняет целый сайт в набор Markdown-файлов. Для самого сбора и преобразования LLM не нужна. ([Документация](ai/building-rag-systems.md))

### Высокая скорость, проверенная на практике {#high-performance-battle-tested-architecture}
- 🚀 **Быстрая работа**: оптимизации позволяют опережать большинство библиотек Python для скрапинга.
- 🔋 **Мало памяти**: оптимизированные структуры данных и загрузка только по мере необходимости.
- ⚡ **Быстрое преобразование в JSON**: в 10 раз быстрее стандартной библиотеки.
- 🏗️ **Проверено на практике**: 92% покрытия тестами и аннотации типов для всего кода. За последний год сотни специалистов ежедневно использовали Scrapling для сбора данных.

### Удобные инструменты для разработчиков {#developerweb-scraper-friendly-experience}
- 🎯 **Интерактивная оболочка**: дополнительная оболочка IPython со Scrapling, сокращёнными командами и инструментами для быстрой разработки. Преобразуйте curl-запросы в запросы Scrapling и просматривайте результаты в браузере.
- 🚀 **Работа из терминала**: собирайте данные по URL, не написав ни строки кода!
- 🛠️ **Навигация по DOM**: переходите к родителям, соседним и дочерним элементам.
- 🧬 **Обработка текста**: регулярные выражения, очистка текста и быстрые операции со строками.
- 📝 **Создание селекторов**: получайте надёжные CSS- и XPath-селекторы для любого элемента.
- 🔌 **Знакомый API**: подход похож на Scrapy и BeautifulSoup, с теми же псевдоэлементами, что и в Scrapy/Parsel.
- 🤝 **Интеграция со Scrapy**: добавьте декоратор `scrapling_response` к обработчику, чтобы разбирать уже загруженные ответы парсером Scrapling. Переписывать проект не нужно.
- 📘 **Полные аннотации типов**: удобная работа в редакторе и автодополнение. При каждом изменении весь код автоматически проверяется **PyRight** и **MyPy**.
- 🔋 **Готовый образ Docker**: с каждым выпуском автоматически собирается и публикуется образ со всеми браузерами.


## История звёзд GitHub {#star-history}
С момента выпуска число звёзд Scrapling на GitHub постоянно растёт. Это видно на графике ниже.

<div id="chartContainer">
  <a href="https://github.com/D4Vinci/Scrapling">
    <img id="chartImage" alt="График числа звёзд GitHub" loading="lazy" src="https://api.star-history.com/svg?repos=D4Vinci/Scrapling&type=Date" height="400"/>
  </a>
</div>

<script>
const observer = new MutationObserver((mutations) => {
  mutations.forEach((mutation) => {
    if (mutation.attributeName === 'data-md-color-media') {
      const colorMedia = document.body.getAttribute('data-md-color-media');
      const isDarkScheme = document.body.getAttribute('data-md-color-scheme') === 'slate';
      const chartImg = document.querySelector('#chartImage');
      const baseUrl = 'https://api.star-history.com/svg?repos=D4Vinci/Scrapling&type=Date';
      
      if (colorMedia === '(prefers-color-scheme)' ? isDarkScheme : colorMedia.includes('dark')) {
        chartImg.src = `${baseUrl}&theme=dark`;
      } else {
        chartImg.src = baseUrl;
      }
    }
  });
});

observer.observe(document.body, {
  attributes: true,
  attributeFilter: ['data-md-color-media', 'data-md-color-scheme']
});
</script>


## Установка {#installation}
Для Scrapling нужен Python 3.10 или новее:

```bash
pip install scrapling
```

!!! warning "Внимание"

    Эта команда устанавливает только парсер и его зависимости. Fetcher и инструменты командной строки в неё не входят. Поэтому импорт из `scrapling.fetchers` или `scrapling.spiders`, как в примерах выше, вызовет `ModuleNotFoundError`. Чтобы использовать Fetcher или Spider, сначала установите зависимости для загрузки страниц, как показано ниже.

### Дополнительные зависимости {#optional-dependencies}

1. Для Fetcher, их классов и дополнительных функций ниже установите зависимости для загрузки страниц и браузеров:
    ```bash
    pip install "scrapling[fetchers]"
    
    scrapling install           # normal install
    scrapling install  --force  # force reinstall
    ```

    Команда загрузит все браузеры, нужные системные пакеты и средства изменения отпечатков браузера.

    Вместо команды можно запустить установку из кода:
    ```python
    from scrapling.cli import install
    
    install([], standalone_mode=False)          # normal install
    install(["--force"], standalone_mode=False) # force reinstall
    ```

2. Дополнительные функции:


     - MCP-сервер:
       ```bash
       pip install "scrapling[ai]"
       ```
     - Зависимости для [создания RAG-систем](ai/building-rag-systems.md):
       ```bash
       pip install "scrapling[rag]"
       ```
     - Интерактивная оболочка и команда `extract`:
         ```bash
         pip install "scrapling[shell]"
         ```
     - Все возможности:
         ```bash
         pip install "scrapling[all]"
         ```
   Выполните `scrapling install`, если нужны браузерные Fetcher. Для HTTP-запросов устанавливать браузер не нужно.

### Docker {#docker}
Образ Docker со всеми дополнениями и браузерами можно скачать из DockerHub:
```bash
docker pull pyd4vinci/scrapling
```
Или из реестра GitHub:
```bash
docker pull ghcr.io/d4vinci/scrapling:latest
```
Образ автоматически собирается и публикуется через GitHub Actions из основной ветки репозитория.

## Как устроена документация {#how-the-documentation-is-organized}
У Scrapling много документации, поэтому мы стараемся следовать подходу [Diátaxis](https://diataxis.fr/).

## Поддержка {#support}

Если вам нравится Scrapling, поддержите его развитие:

- ⭐ Поставьте звезду [репозиторию на GitHub](https://github.com/D4Vinci/Scrapling).
- 🚀 Подпишитесь на нас в [Twitter](https://x.com/Scrapling_dev) и присоединитесь к [Discord](https://discord.gg/EMgGbDceNQ).
- 💝 [Станьте спонсором проекта или угостите меня кофе](donate.md). :wink:
- 🐛 Сообщайте об ошибках и предлагайте идеи через [GitHub Issues](https://github.com/D4Vinci/Scrapling/issues).

## Лицензия {#license}

Проект распространяется по лицензии BSD-3. Подробности в файле [LICENSE](https://github.com/D4Vinci/Scrapling/blob/main/LICENSE).
