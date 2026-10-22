<!-- mcp-name: io.github.D4Vinci/Scrapling -->

<h1 align="center">
    <a href="https://scrapling.readthedocs.io/ru/latest/">
        <picture>
          <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/docs/assets/cover_dark.svg?sanitize=true">
          <img alt="Обложка Scrapling" src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/docs/assets/cover_light.svg?sanitize=true">
        </picture>
    </a>
    <br>
    <small>Простой веб-скрапинг для современного интернета</small>
</h1>

<p align="center">
    <a href="https://github.com/D4Vinci/Scrapling/actions/workflows/tests.yml" alt="Тесты">
        <img alt="Тесты" src="https://github.com/D4Vinci/Scrapling/actions/workflows/tests.yml/badge.svg"></a>
    <a href="https://badge.fury.io/py/Scrapling" alt="Версия PyPI">
        <img alt="Версия PyPI" src="https://badge.fury.io/py/Scrapling.svg"></a>
    <a href="https://hub.docker.com/r/pyd4vinci/scrapling" target="_blank">
        <img alt="Загрузки Docker" src="https://img.shields.io/docker/pulls/pyd4vinci/scrapling?labelColor=%20%23FDB062&logo=Docker&labelColor=%20%23528bff"></a>
    <a href="https://clickpy.clickhouse.com/dashboard/scrapling" rel="nofollow"><img src="https://img.shields.io/pypi/dm/scrapling" alt="Загрузки пакета PyPI"></a>
    <a href="https://scrapling.readthedocs.io/ru/latest/ai/agent-skill.html" alt="Skill для AI-агентов">
        <img alt="Значок Agent Skill" src="https://img.shields.io/badge/Skill-black?style=flat&label=Agent&link=https%3A%2F%2Fscrapling.readthedocs.io%2Fru%2Flatest%2Fai%2Fagent-skill.html"></a>
    <a href="https://clawhub.ai/D4Vinci/scrapling-official" alt="Skill для OpenClaw">
        <img alt="Skill для OpenClaw" src="https://img.shields.io/badge/Clawhub-darkred?style=flat&label=OpenClaw&link=https%3A%2F%2Fclawhub.ai%2FD4Vinci%2Fscrapling-official"></a>
    <br/>
    <a href="https://discord.gg/EMgGbDceNQ" alt="Discord" target="_blank">
      <img alt="Discord" src="https://img.shields.io/discord/1360786381042880532?style=social&logo=discord&link=https%3A%2F%2Fdiscord.gg%2FEMgGbDceNQ">
    </a>
    <a href="https://x.com/Scrapling_dev" alt="X (бывший Twitter)">
      <img alt="Подписаться в X (бывший Twitter)" src="https://img.shields.io/twitter/follow/Scrapling_dev?style=social&logo=x&link=https%3A%2F%2Fx.com%2FScrapling_dev">
    </a>
    <br/>
    <a href="https://pypi.org/project/scrapling/" alt="Поддерживаемые версии Python">
        <img alt="Поддерживаемые версии Python" src="https://img.shields.io/pypi/pyversions/scrapling.svg"></a>
</p>

<p align="center">
    <a href="https://scrapling.readthedocs.io/ru/latest/parsing/selection.html"><strong>Поиск элементов</strong></a>
    &middot;
    <a href="https://scrapling.readthedocs.io/ru/latest/fetching/choosing.html"><strong>Выбор Fetcher</strong></a>
    &middot;
    <a href="https://scrapling.readthedocs.io/ru/latest/spiders/architecture.html"><strong>Пауки</strong></a>
    &middot;
    <a href="https://scrapling.readthedocs.io/ru/latest/spiders/proxy-blocking.html"><strong>Смена прокси</strong></a>
    &middot;
    <a href="https://scrapling.readthedocs.io/ru/latest/cli/overview.html"><strong>CLI</strong></a>
    &middot;
    <a href="https://scrapling.readthedocs.io/ru/latest/ai/mcp-server.html"><strong>MCP-сервер</strong></a>
</p>

Scrapling объединяет быстрые HTTP-запросы, скрытные браузеры, мощный разбор страниц и параллельный обход сайтов в одной библиотеке Python.

Загружайте статические страницы, выполняйте JavaScript, работайте с сайтами и извлекайте данные из API этих сайтов. Создавайте краулеры с повторным использованием сессий, сменой прокси, автоматическими повторами, паузой и продолжением работы, а также готовым экспортом данных.

Используйте Scrapling из Python, терминала или AI-агента через MCP-сервер и Agent Skill. Библиотека помогает на всех этапах: от извлечения нескольких полей до сохранения целого сайта в виде чистых Markdown-файлов.

## Что можно сделать со Scrapling

- **[Загрузка и работа с сайтами](https://scrapling.readthedocs.io/ru/latest/fetching/choosing.html)**: быстрые HTTP-запросы, скрытные браузеры, выполнение JavaScript, прохождение Cloudflare Turnstile и Interstitial, постоянные сессии и запись фоновых API-ответов.
- **[Разбор и извлечение данных](https://scrapling.readthedocs.io/ru/latest/parsing/selection.html)**: CSS, XPath, поиск по тексту и регулярным выражениям, поиск элементов после изменений страницы, поиск похожих элементов и чистый Markdown.
- **[Обход и экспорт](https://scrapling.readthedocs.io/ru/latest/spiders/getting-started.html)**: параллельные Spider, смена прокси, повторы, AutoThrottle, пауза и продолжение, потоковая выдача, готовые шаблоны и экспорт в JSON, JSONL, CSV и XML.
- **[Сбор данных с AI или из терминала](https://scrapling.readthedocs.io/ru/latest/ai/mcp-server.html)**: MCP-сервер для работы AI-агентов с сайтами и данными, Agent Skill, команды CLI и интерактивная оболочка.

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

<p align="center">
    <a href="https://dataimpulse.com/?utm_source=scrapling&utm_medium=banner&utm_campaign=scrapling" target="_blank" style="display:flex; justify-content:center; padding:4px 0;">
        <img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/DataImpulse.png" alt="At DataImpulse, we specialize in developing custom proxy services for your business. Make requests from anywhere, collect data, and enjoy fast connections with our premium proxies." style="max-height:60px;">
    </a>
</p>

# Платиновые спонсоры
<table>
  <tr>
    <td width="200">
      <a href="https://go.nodemaven.com/scraplingoctober" target="_blank" title="Proxies with the Highest IP Scores">
        <img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/NodeMaven.jpg" width="240" height="100">
      </a>
    </td>
    <td>
    <a href="https://go.nodemaven.com/scraplingoctober" target="_blank">NodeMaven</a> - самый эффективный провайдер прокси для веб-скрапинга и автоматизации с IP-адресами самого высокого качества на рынке. Используйте код SCRAPLING35 для получения скидки 35%.
    </td>
  </tr>
  <tr>
    <td width="200">
      <a href="https://hypersolutions.co/?utm_source=github&utm_medium=readme&utm_campaign=scrapling" target="_blank" title="Bot Protection Bypass API for Akamai, DataDome, Incapsula & Kasada">
        <img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/HyperSolutions.png">
      </a>
    </td>
    <td> Scrapling справляется с Cloudflare Turnstile. Для обхода защиты корпоративного уровня
      <a href="https://hypersolutions.co?utm_source=github&utm_medium=readme&utm_campaign=scrapling">
        <b>Hyper Solutions</b>
      </a> предоставляет API для получения действительных antibot-токенов для <b>Akamai</b>, <b>DataDome</b>, <b>Kasada</b> и <b>Incapsula</b>. Достаточно простых вызовов API. Автоматизация браузера не нужна.
    </td>
  </tr>
  <tr>
    <td width="200">
      <a href="https://evomi.com?utm_source=github&utm_medium=banner&utm_campaign=d4vinci-scrapling" target="_blank" title="Evomi is your Swiss Quality Proxy Provider, starting at $0.49/GB">
        <img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/evomi.png">
      </a>
    </td>
    <td>
      <a href="https://evomi.com?utm_source=github&utm_medium=banner&utm_campaign=d4vinci-scrapling">
        <b>Evomi</b>
      </a>: резидентные прокси от $0,49/ГБ. Браузер для скрапинга на основе Chromium с полной подменой отпечатка браузера, резидентными IP, автоматическим решением CAPTCHA и обходом защиты от ботов. </br>
      <b>Scraper API для получения результатов без лишних сложностей. Доступны интеграции с MCP и N8N.</b>
    </td>
  </tr>
  <tr>
    <td width="200">
      <a href="https://substack.thewebscraping.club/p/scrapling-hands-on-guide?utm_source=github&utm_medium=repo&utm_campaign=scrapling" target="_blank" title="The #1 newsletter dedicated to Web Scraping">
        <img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/TWSC.png">
      </a>
    </td>
    <td>
    Прочитайте полный обзор <a href="https://substack.thewebscraping.club/p/scrapling-hands-on-guide?utm_source=github&utm_medium=repo&utm_campaign=scrapling" target="_blank">Scrapling на The Web Scraping Club</a> (ноябрь 2025), опубликованный в рассылке №1 по веб-скрапингу.
    </td>
  </tr>
  <tr>
    <td width="200">
      <a href="https://www.swiftproxy.net/?ref=D4Vinci" target="_blank" title="Scalable Solutions for Web Data Access">
        <img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/SwiftProxy.png">
      </a>
    </td>
    <td>
    <a href="https://www.swiftproxy.net/?ref=D4Vinci" target="_blank">Swiftproxy</a> предоставляет масштабируемые резидентные прокси с более чем 80 млн IP в 195+ странах, обеспечивая быстрые и надёжные соединения, автоматическую ротацию и высокую устойчивость к блокировкам. Доступна бесплатная пробная версия.
    </td>
  </tr>
  <tr>
    <td width="200">
      <a href="https://byteful.com/?utm_source=github&utm_medium=github-sponsor&utm_campaign=scrapling_github_sponsor" target="_blank" title="Ethically sourced residential proxy infrastructure powering web scraping and AI agents">
        <img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/byteful.png">
      </a>
    </td>
    <td>
    <a href="https://byteful.com/?utm_source=github&utm_medium=github-sponsor&utm_campaign=scrapling_github_sponsor" target="_blank">Byteful</a> предоставляет резидентные, мобильные, ISP- и дата-центровые прокси из этичных источников, а также инструменты для веб-скрапинга и автоматизации с AI. Используйте код SCRAPLING10 для получения скидки 10% на резидентные прокси.
    </td>
  </tr>
  <tr>
    <td width="200">
      <a href="https://proxylane.dev/?utm_source=scrapling&utm_medium=partnership&utm_campaign=scrapling_platinum_202609&utm_content=github_readme" target="_blank" title="28M+ clean residential IPs for browser automation. No Blocks. No CAPTCHAs. Pay-as-you-Go.">
        <img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/proxylane.png">
      </a>
    </td>
    <td>
    <a href="https://proxylane.dev/?utm_source=scrapling&utm_medium=partnership&utm_campaign=scrapling_platinum_202609&utm_content=github_readme" target="_blank">ProxyLane</a>: Сократите число блокировок и CAPTCHA на 90%. 28 млн премиальных резидентных IP-адресов для интенсивного веб-скрапинга. 195 стран. Выбор города, ISP и почтового индекса. Сессии с постоянным IP или сменой IP. Трафик без срока действия от $2/ГБ. Код <strong>SCRAPEANDTAKE</strong>: <em>скидка 25%</em>.
    </td>
  </tr>
  <tr>
    <td width="200">
      <a href="https://www.lundproxy.com/unlimited-residential-bandwidth.html?utm_source=github&utm_medium=sponsorship&utm_campaign=scrapling&utm_content=banner" target="_blank" title="Unlimited residential traffic, sized only by bandwidth.">
        <img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/lundproxy.png">
      </a>
    </td>
    <td>
    <a href="https://www.lundproxy.com?utm_source=github&utm_medium=sponsorship&utm_campaign=scrapling&utm_content=text" target="_blank">LundProxy</a>: Хватит платить за каждый ГБ. Безлимитный резидентный трафик, более 100 млн IP-адресов, более 190 стран. Оплата по пропускной способности. Запросите бесплатный пробный доступ к резидентным прокси на скорости 50 Мбит/с.
    </td>
  </tr>
  <tr>
    <td width="200">
      <a href="https://dataimpulse.com/?utm_source=website&utm_medium=github_readme&utm_campaign=scrapling_platinum" target="_blank" title="Buy Pay-as-you-go proxies from $1/GB">
        <img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/DataImpulse_Platinum.png">
      </a>
    </td>
    <td>
    $1/ГБ в <a href="https://dataimpulse.com/?utm_source=website&utm_medium=github_readme&utm_campaign=scrapling_platinum" target="_blank">DataImpulse</a>. Прокси из этичных источников, без посредников. Более 90 млн IP-адресов, более 195 стран. Резидентные, дата-центровые и мобильные. Оплата по мере использования, без подписки. Трафик без срока действия.
    </td>
  </tr>
</table>

<i><sub>Хотите разместить здесь свою рекламу? Нажмите [здесь](https://github.com/sponsors/D4Vinci/sponsorships?tier_id=586646)</sub></i>
# Спонсоры

<!-- sponsors -->

<a href="https://cloro.dev/?utm_source=referral&utm_medium=scrapling" target="_blank" title="The search API for the AI era"><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/cloro.jpg"></a>

<br/>

<a href="https://serpapi.com/?utm_source=scrapling" target="_blank" title="Scrape Google and other search engines with SerpApi"><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/SerpApi.png"></a>
<a href="https://visit.decodo.com/Dy6W0b" target="_blank" title="Try the Most Efficient Residential Proxies for Free"><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/decodo.png"></a>
<a href="https://proxyempire.io/?ref=scrapling&utm_source=github&utm_medium=paid_referral&utm_campaign=open_source_sponsorship&utm_content=scrapling" target="_blank" title="Collect The Data Your Project Needs with the Best Residential Proxies"><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/ProxyEmpire.png"></a>
<a href="https://www.webshare.io/?referral_code=48r2m2cd5uz1" target="_blank" title="The Most Reliable Proxy with Unparalleled Performance"><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/webshare.png"></a>
<a href="https://proxiware.com/?ref=scrapling" target="_blank" title="Collect Any Data. At Any Scale."><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/proxiware.png"></a>


<!-- /sponsors -->

<i><sub>Хотите разместить здесь свою рекламу? Нажмите [здесь](https://github.com/sponsors/D4Vinci) и выберите подходящий план!</sub></i>

---

## Основные возможности

### Spider: всё для обхода сайтов

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

### Загрузка сайтов с поддержкой сессий

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

### Разбор и извлечение данных

- 🔄 **Поиск элементов после изменений**: алгоритмы сходства находят элементы снова, даже если сайт изменился.
- 🎯 **Гибкий поиск**: используйте CSS, XPath, фильтры, текст, регулярные выражения и другие способы.
- 🔍 **Похожие элементы**: автоматически находите элементы, похожие на уже найденные.

### Возможности для AI

- 🤖 **MCP-сервер**: AI-боты и агенты, такие как Claude и Cursor, могут собирать данные через Scrapling. Им доступны HTTP-запросы, действия в браузере, снимки экрана, сохранённый вход и фоновые API-ответы. Скрытный браузер и нужные инструменты позволяют подходящим AI-моделям проходить любые CAPTCHA во время работы, а проверки Cloudflare обрабатываются встроенным решением. Сервер уменьшает объём данных для модели, блокирует рекламу и защищает от Prompt Injection. Есть подключение к удалённым браузерам по CDP и HTTP-транспорт с настройками аутентификации. ([Демонстрация](https://www.youtube.com/watch?v=qyFk3ZNwOxE))
- 🧠 **Agent Skill**: готовый к установке [Agent Skill](https://scrapling.readthedocs.io/ru/latest/ai/agent-skill.html) знакомит агента со всей библиотекой. Он помогает писать код под текущий API без догадок.
- 📚 **Markdown для RAG**: одна строка (`page.markdown()`) превращает страницу в чистый и безопасный Markdown для LLM. Шаблон `ContentSpider` сохраняет целый сайт в набор Markdown-файлов. Для самого сбора и преобразования LLM не нужна. ([Документация](https://scrapling.readthedocs.io/ru/latest/ai/building-rag-systems.html))

### Высокая скорость, проверенная на практике

- 🚀 **Быстрая работа**: оптимизации позволяют опережать большинство библиотек Python для скрапинга.
- 🔋 **Мало памяти**: оптимизированные структуры данных и загрузка только по мере необходимости.
- ⚡ **Быстрое преобразование в JSON**: в 10 раз быстрее стандартной библиотеки.
- 🏗️ **Проверено на практике**: 92% покрытия тестами и аннотации типов для всего кода. За последний год сотни специалистов ежедневно использовали Scrapling для сбора данных.

### Удобные инструменты для разработчиков

- 🎯 **Интерактивная оболочка**: дополнительная оболочка IPython со Scrapling, сокращёнными командами и инструментами для быстрой разработки. Преобразуйте curl-запросы в запросы Scrapling и просматривайте результаты в браузере.
- 🚀 **Работа из терминала**: собирайте данные по URL, не написав ни строки кода!
- 🛠️ **Навигация по DOM**: переходите к родителям, соседним и дочерним элементам.
- 🧬 **Обработка текста**: регулярные выражения, очистка текста и быстрые операции со строками.
- 📝 **Создание селекторов**: получайте надёжные CSS- и XPath-селекторы для любого элемента.
- 🔌 **Знакомый API**: подход похож на Scrapy и BeautifulSoup, с теми же псевдоэлементами, что и в Scrapy/Parsel.
- 🤝 **Интеграция со Scrapy**: добавьте декоратор `scrapling_response` к обработчику, чтобы разбирать уже загруженные ответы парсером Scrapling. Переписывать проект не нужно.
- 📘 **Полные аннотации типов**: удобная работа в редакторе и автодополнение. При каждом изменении весь код автоматически проверяется **PyRight** и **MyPy**.
- 🔋 **Готовый образ Docker**: с каждым выпуском автоматически собирается и публикуется образ со всеми браузерами.

## Начало работы

Вот несколько примеров того, что умеет Scrapling.

### Базовое использование
HTTP-запросы с сессиями
```python
from scrapling.fetchers import Fetcher, FetcherSession

with FetcherSession(impersonate='chrome') as session:  # Используйте последнюю версию TLS fingerprint Chrome
    page = session.get('https://quotes.toscrape.com/', stealthy_headers=True)
    quotes = page.css('.quote .text::text').getall()

# Или используйте одноразовые запросы
page = Fetcher.get('https://quotes.toscrape.com/')
quotes = page.css('.quote .text::text').getall()
```
Расширенный режим скрытности
```python
from scrapling.fetchers import StealthyFetcher, StealthySession

with StealthySession(headless=True, solve_cloudflare=True) as session:  # Держите браузер открытым, пока не закончите
    page = session.fetch('https://nopecha.com/demo/cloudflare', google_search=False)
    data = page.css('#padded_content a').getall()

# Или используйте стиль одноразового запроса - открывает браузер для этого запроса, затем закрывает его после завершения
page = StealthyFetcher.fetch('https://nopecha.com/demo/cloudflare', solve_cloudflare=True)
data = page.css('#padded_content a').getall()
```
Полная автоматизация браузера
```python
from scrapling.fetchers import StealthyFetcher, StealthySession

with StealthySession(headless=True, disable_resources=False, network_idle=True) as session:  # Держите браузер открытым, пока не закончите
    page = session.fetch('https://quotes.toscrape.com/', load_dom=False)
    data = page.xpath('//span[@class="text"]/text()').getall()  # XPath-селектор, если вы предпочитаете его

# Или используйте стиль одноразового запроса - открывает браузер для этого запроса, затем закрывает его после завершения
page = StealthyFetcher.fetch('https://quotes.toscrape.com/')
data = page.css('.quote .text::text').getall()
```

### Пауки
Создавайте краулеры с параллельными запросами, разными сессиями, паузой и продолжением работы:
```python
from scrapling.spiders import Spider, Response

class QuotesSpider(Spider):
    name = "quotes"
    start_urls = ["https://quotes.toscrape.com/"]
    concurrent_requests = 10

    async def parse(self, response: Response):
        for quote in response.css('.quote'):
            yield {
                "text": quote.css('.text::text').get(),
                "author": quote.css('.author::text').get(),
            }

        next_page = response.css('.next a')
        if next_page:
            yield response.follow(next_page[0].attrib['href'])

result = QuotesSpider().start()
print(f"Извлечено {len(result.items)} цитат")
result.items.to_json("quotes.json")
```
Используйте несколько типов сессий в одном Spider:
```python
from scrapling.spiders import Spider, Request, Response
from scrapling.fetchers import FetcherSession, AsyncStealthySession

class MultiSessionSpider(Spider):
    name = "multi"
    start_urls = ["https://example.com/"]

    def configure_sessions(self, manager):
        manager.add("fast", FetcherSession(impersonate="chrome"))
        manager.add("stealth", AsyncStealthySession(headless=True), lazy=True)

    async def parse(self, response: Response):
        for link in response.css('a::attr(href)').getall():
            # Направляйте защищённые страницы через stealth-сессию
            if "protected" in link:
                yield Request(link, sid="stealth")
            else:
                yield Request(link, sid="fast", callback=self.parse)  # явный callback
```
Сохраняйте прогресс, чтобы приостанавливать и продолжать долгий обход. Запустите Spider так:
```python
QuotesSpider(crawldir="./crawl_data").start()
```
Если задан `crawldir`, нажмите Ctrl+C, чтобы сохранить ожидающие запросы и уже посещённые URL. Для продолжения запустите Spider с тем же `crawldir`. Сохраняйте извлечённые данные отдельно.

Можно взять готовый шаблон. Например, для сбора всего каталога магазина Shopify:
```python
from scrapling.spiders import ShopifySpider

class MyStore(ShopifySpider):
    target_website = "example.com"

result = MyStore().start()  # Все товары магазина, по одной записи на вариант
```
Шаблон получает товары через открытые API коллекций и выдаёт одну запись на каждый вариант товара.

### Расширенный разбор и навигация
```python
from scrapling.fetchers import Fetcher

# Богатый выбор элементов и навигация
page = Fetcher.get('https://quotes.toscrape.com/')

# Получение цитат различными методами выбора
quotes = page.css('.quote')  # CSS-селектор
quotes = page.xpath('//div[@class="quote"]')  # XPath
quotes = page.find_all('div', {'class': 'quote'})  # В стиле BeautifulSoup
# То же самое, что
quotes = page.find_all('div', class_='quote')
quotes = page.find_all(['div'], class_='quote')
quotes = page.find_all(class_='quote')  # и так далее...
# Найти элемент по текстовому содержимому
quotes = page.find_by_text('Albert Einstein', first_match=False)

# Продвинутая навигация
quote_text = page.css('.quote')[0].css('.text::text').get()
quote_texts = page.css('.quote').css('.text::text').getall()  # Цепочка селекторов
first_quote = page.css('.quote')[0]
author = first_quote.css('.author::text').get()
next_quote = first_quote.next
parent_container = first_quote.parent

# Связи элементов и подобие
similar_elements = first_quote.find_similar()
below_elements = first_quote.below_elements
```
Можно использовать парсер напрямую, без загрузки сайта:
```python
from scrapling.parser import Selector

page = Selector("<html>...</html>")
```
И он работает точно так же!

### Асинхронные сессии
```python
import asyncio
from scrapling.fetchers import FetcherSession, AsyncStealthySession

async def main():
    async with FetcherSession(http3=True) as http_session:  # `FetcherSession` учитывает контекст и работает как с sync, так и с async
        page1 = await http_session.get('https://quotes.toscrape.com/')
        page2 = await http_session.get('https://quotes.toscrape.com/page/2/', impersonate='chrome')
        print(len(page1.css('.quote')), len(page2.css('.quote')))

    async with AsyncStealthySession(max_pages=2) as browser_session:
        urls = ['https://quotes.toscrape.com/js/', 'https://quotes.toscrape.com/js/page/2/']
        pages = await asyncio.gather(*(browser_session.fetch(url, wait_selector='.quote') for url in urls))
        print([len(page.css('.quote')) for page in pages])

asyncio.run(main())
```

## CLI и интерактивная оболочка

Scrapling можно использовать из командной строки:

[![asciicast](https://asciinema.org/a/736339.svg)](https://asciinema.org/a/736339)

Запустите интерактивную оболочку для сбора данных:
```bash
pip install "scrapling[shell]"
scrapling shell
```
Извлекайте страницы прямо в файл без программирования. Выберите содержимое с `--css-selector` или используйте `--ai-targeted` для выбора и очистки содержимого `body`. Используйте `.txt` для текста, `.md` для Markdown или `.html` для HTML.
```bash
scrapling extract get 'https://quotes.toscrape.com/' quotes.md
scrapling extract get 'https://quotes.toscrape.com/' quotes.txt --css-selector '.quote' --impersonate 'chrome'
scrapling extract fetch 'https://quotes.toscrape.com/js/' quotes.md --css-selector '.quote' --wait-selector '.quote' --no-headless
scrapling extract fetch 'https://nopecha.com/demo/cloudflare' captchas.html --css-selector '#padded_content a' --solve-cloudflare
```

> [!NOTE]
> О других возможностях, включая MCP-сервер и интерактивную оболочку, читайте в [документации](https://scrapling.readthedocs.io/ru/latest/).

## Тесты производительности

Scrapling не только мощный, но и очень быстрый. Следующие тесты производительности сравнивают парсер Scrapling с последними версиями других популярных библиотек.

### Скорость извлечения текста: 5 000 вложенных элементов

| # |    Библиотека     | Время (мс) | По сравнению со Scrapling |
|---|:-----------------:|:----------:|:------------:|
| 1 |     Scrapling     |    1,99    |     1,0x     |
| 2 |   Parsel/Scrapy   |    2,06    |     1,035    |
| 3 |     Чистый Lxml      |    2,56    |    1,286     |
| 4 |      PyQuery      |   23,98    |     ~12x     |
| 5 |    Selectolax     |   197,02   |     ~99x     |
| 6 |  MechanicalSoup   |  1545,15   |   ~776,5x    |
| 7 |   BS4 + Lxml   |   1562,1   |   ~785,0x    |
| 8 | BS4 + html5lib |  3412,73   |   ~1714,9x   |


### Поиск похожих элементов и текста

Адаптивный поиск элементов в Scrapling значительно опережает другие решения:

| Библиотека  | Время (мс) | По сравнению со Scrapling |
|-------------|:----------:|:------------:|
| Scrapling   |    2,3     |     1,0x     |
| AutoScraper |   12,58    |    5,47x     |


> Результаты усреднены по более чем 100 запускам. Методика приведена в [benchmarks.py](https://github.com/D4Vinci/Scrapling/blob/main/benchmarks.py).

## Установка

Для Scrapling нужен Python 3.10 или новее:

```bash
pip install scrapling
```

> [!IMPORTANT]
> Эта команда устанавливает только парсер и его зависимости. Fetcher и инструменты командной строки в неё не входят. Поэтому импорт из `scrapling.fetchers` или `scrapling.spiders`, как в примерах выше, вызовет `ModuleNotFoundError`. Чтобы использовать Fetcher или Spider, сначала установите зависимости для загрузки страниц, как показано ниже.

### Дополнительные зависимости

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

2. Дополнительные возможности:
   - MCP-сервер:
       ```bash
       pip install "scrapling[ai]"
       ```
   - Зависимости для [создания RAG-систем](https://scrapling.readthedocs.io/ru/latest/ai/building-rag-systems.html):
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

### Docker
Образ Docker со всеми дополнениями и браузерами можно скачать из DockerHub:
```bash
docker pull pyd4vinci/scrapling
```
Или из реестра GitHub:
```bash
docker pull ghcr.io/d4vinci/scrapling:latest
```
Образ автоматически собирается и публикуется через GitHub Actions из основной ветки репозитория.

## Участие в разработке

Присоединяйтесь к разработке! Перед началом прочитайте [руководство для участников](https://github.com/D4Vinci/Scrapling/blob/main/CONTRIBUTING.md).

## Отказ от ответственности

> [!CAUTION]
> Библиотека предназначена только для обучения и исследований. Используя её, вы соглашаетесь соблюдать местные и международные законы о сборе данных и конфиденциальности. Авторы и участники не отвечают за неправомерное использование программы. Соблюдайте условия сайтов и правила robots.txt.

## 🎓 Цитирование
Если вы использовали библиотеку в исследовании, укажите её так:
```text
  @misc{scrapling,
    author = {Karim Shoair},
    title = {Scrapling},
    year = {2024},
    url = {https://github.com/D4Vinci/Scrapling},
    note = {A Python Web Scraping framework for everything from a single request to a full-scale crawl!}
  }
```

## Лицензия

Проект распространяется по лицензии BSD-3-Clause.

## Благодарности

В проекте есть код на основе следующих проектов:
- Parsel (лицензия BSD) - Используется для подмодуля [translator](https://github.com/D4Vinci/Scrapling/blob/main/scrapling/core/translator.py)

---
<div align="center"><small>Разработал и создал с ❤️ Карим Шоаир.</small></div><br>
