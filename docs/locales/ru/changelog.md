---
title: "История изменений Scrapling"
description: "Заметки о выпусках Scrapling: новые возможности, исправления и несовместимые изменения."
---

# История изменений {#changelog}

Все заметные изменения в Scrapling из [выпусков на GitHub](https://github.com/D4Vinci/Scrapling/releases).

## [v0.5](https://github.com/D4Vinci/Scrapling/releases/tag/v0.5) - 2026-10-17 {#v0.5}

**Scrapling v0.5 улучшает почти всё: получение и разбор страниц, пауков, автоматизацию браузера, инструменты ИИ и документацию на десяти языках 🚀**

!!! warning "Внимание"

    **Этот выпуск вносит столько несовместимых изменений, что они не поместятся здесь. Перед обновлением прочитайте [руководство по переходу на v0.5](migrating-to-v0.5.md).**

### 🚀 Новые возможности и улучшения удобства {#v0.5-new-stuff-and-quality-of-life-changes}

- **Гораздо более мощный MCP-сервер для ИИ-агентов, который может решить почти любую CAPTCHA** (см. [документацию](ai/mcp-server.md)):

    - **Полные сценарии работы в браузере**: заполняйте формы, нажимайте, наводите указатель, прокручивайте, используйте клавиатуру, работайте с диалогами и ждите результатов в одной упорядоченной последовательности. Поддерживаются разные типы полей и замедленные действия. Выполнение останавливается при первой ошибке.
    - **Читайте и ищите на текущей странице без перезагрузки**: извлекайте HTML, Markdown или текст из всей страницы или одного элемента. Снимки страницы с поиском показывают роли, имена и позиции элементов. Представления выбранных частей сохраняют окружающий контекст.
    - **Выполняйте свой JavaScript и делайте снимки нужных областей**: запускайте скрипты, включая асинхронные операции, с доступом к JavaScript самой страницы. Снимайте отдельные элементы, видимую область или всю страницу в PNG или JPEG.
    - **Изучайте сетевую активность и повторно используйте вход в аккаунт**: проверяйте записанные запросы и ответы, сохраняйте и восстанавливайте состояние входа в браузере и взаимодействуйте с элементами в открытом или закрытом Shadow DOM. Прочитайте записанный трафик до закрытия сессии.
    - **Используйте меньше токенов и получайте более понятные ошибки**: краткие описания инструментов и общие инструкции уменьшают повторы. Ошибки браузера и запросов передаются агентам с полезными сообщениями.

- **Смотрите запросы, которые делает страница**. Включите `record_requests=True`, чтобы записывать завершённый трафик при загрузках, действиях и работе с разными вкладками. Затем изучайте сохранённые ответы без повторной отправки запросов. (См. [документацию](fetching/stealthy.md#network-history).)

    ```python
    from scrapling.fetchers import StealthySession

    with StealthySession(record_requests=True) as session:
        session.fetch("https://example.com", network_idle=True)
        for response in session.network.search(url_pattern=r"/api/", limit=None):
            print(response.url, response.status, response.body)
    ```

    - Фильтруйте по URL, методу, типу ресурса или статусу. Получайте отдельный ответ по ID. Проверяйте заголовки, отправленные данные, ответы API, ошибки HTTP и перенаправления через привычный API `Response`.
    - Сохраняются поддерживаемые текстовые тела ответов с ограничениями размера, а также метаданные и причина, если тело сохранить нельзя. По умолчанию лимит составляет 1 000 запросов. Работает с синхронными и асинхронными сессиями. Сохранённая история Python остаётся доступной для чтения после закрытия.

- **Сохраните вход в аккаунт один раз и используйте его при следующих запусках**. `save_state(path)` и `load_state(path)` сохраняют cookie, локальное хранилище и IndexedDB в JSON, совместимом с Playwright. Поддерживаются как синхронные, так и асинхронные браузерные сессии. (См. [документацию](fetching/stealthy.md#save-and-load-session-state).)
    - Загрузите состояние перед получением или перезагрузкой страницы. Нужен запущенный общий контекст браузера без `proxy_rotator`. Вкладки, настройки браузера и `sessionStorage` не сохраняются.

- **Извлекайте открытый Shadow DOM с помощью `pierce_shadow=True`**, затем используйте CSS или XPath как обычно. Доступно в браузерных fetcher-классах, сессиях и через параметр CLI `--pierce-shadow`. Содержимое слотов сохраняется без изменения активной страницы. При получении HTML закрытые корни и документы iframe не включаются. (См. [документацию](fetching/stealthy.md#shadow-dom).)

- **Выберите, как ваш паук обходит сайт**. `CrawlSpider` и его подклассы, включая `ContentSpider`, поддерживают `crawl_strategy="bfs"`, чтобы первыми назначать самые старые запросы, или `"dfs"`, чтобы первыми назначать самые новые. Приоритет по-прежнему имеет преимущество. Обработка параллельных страниц может завершаться в другом порядке. (См. [документацию](spiders/generic-templates.md#crawl-order).)

### 🐛 Исправления ошибок {#v0.5-bug-fixes}

- **Улучшено прохождение проверок Cloudflare**: обнаруживаются виджеты, которые появляются с задержкой, убраны лишние ожидания и ограничены циклы повторов для пассивных проверок и скрытых фреймов. Исправляет [#468](https://github.com/D4Vinci/Scrapling/issues/468) и [#509](https://github.com/D4Vinci/Scrapling/issues/509).
- **Исправлен запуск браузера из оболочки Windows с правами администратора**. Исправляет [#463](https://github.com/D4Vinci/Scrapling/issues/463).
- **Встроенные флаги скрытного режима сохраняются при добавлении своих флагов браузера**. Изменение от @alkaz-nodemaven в [#430](https://github.com/D4Vinci/Scrapling/pull/430).
- **Улучшен разбор кодировки в ответах браузера**, включая объявления с другим регистром букв, пробелами или значениями в кавычках.
- **Отсутствие проверки Cloudflare больше не записывается как ошибка**, если проходить проверку не требуется. Исправляет [#459](https://github.com/D4Vinci/Scrapling/issues/459).

- **Исправлены отпечатки запросов** для параметров URL, изменение от @yetval в [#448](https://github.com/D4Vinci/Scrapling/pull/448), пустых или логически ложных тел JSON, изменение от @ac1982 в [#480](https://github.com/D4Vinci/Scrapling/pull/480), и порядка добавления заголовков, изменение от @SarwadnyaMahajan в [#466](https://github.com/D4Vinci/Scrapling/pull/466).
- **Исправлен перенос данных запроса при переходе по ссылкам**, включая устаревшие заголовки, связанные с телом запроса. Изменение от @yetval в [#462](https://github.com/D4Vinci/Scrapling/pull/462).
- **Заблокированные ответы больше не сохраняются в кеше разработки как успешные записи**. Изменение от @Kuang-xianxin в [#446](https://github.com/D4Vinci/Scrapling/pull/446).
- **Файлы контрольных точек сохраняются, если обход завершается исключением**. Изменение от @SulimanAbdulrazzaq в [#486](https://github.com/D4Vinci/Scrapling/pull/486).
- **Исправлена обработка ошибок robots.txt**: неудачные запросы больше не кешируются как разрешение на обход. Изменение от @prateekraawat1 в [#443](https://github.com/D4Vinci/Scrapling/pull/443).
- **Исправлено извлечение ссылок с ограничивающими селекторами**, включая отсутствие совпадений и селекторы, которые выбирают сам элемент ссылки. Изменение от @SulimanAbdulrazzaq в [#452](https://github.com/D4Vinci/Scrapling/pull/452) и [#483](https://github.com/D4Vinci/Scrapling/pull/483).
- **Исправлен выбор callback-функций для sitemap**, изменение от @SulimanAbdulrazzaq в [#458](https://github.com/D4Vinci/Scrapling/pull/458), **а также разбор XML с комментариями или инструкциями обработки**, изменение от @sup3dev в [#450](https://github.com/D4Vinci/Scrapling/pull/450).
- **Добавлена обработка меток порядка байтов в начале robots.txt и CSV-фидов**. Изменение от @SulimanAbdulrazzaq в [#453](https://github.com/D4Vinci/Scrapling/pull/453).
- **Исправлена обработка `stealthy_headers` в HTTP-сессиях пауков**: параметр передаётся сессии, а не напрямую в `curl_cffi`. Изменение от @Yigtwxx в [#475](https://github.com/D4Vinci/Scrapling/pull/475).

- **Исправлено кодирование данных формы из словаря для значений в виде списков и кортежей**, с сохранением приоритета тела запроса и прежней обработки `None`. Включены изменения от @SulimanAbdulrazzaq в [#485](https://github.com/D4Vinci/Scrapling/pull/485).
- **Исправлено объединение HTTP-заголовков сессии и отдельного запроса без учёта регистра**. Изменение от @SulimanAbdulrazzaq в [#487](https://github.com/D4Vinci/Scrapling/pull/487).
- **Исправлено незаметное удаление пустых или логически ложных тел JSON в запросах CLI**. Изменение от @SulimanAbdulrazzaq в [#484](https://github.com/D4Vinci/Scrapling/pull/484).
- **Экспорт файлов Markdown и текста теперь всегда использует UTF-8**. Ошибки преобразования больше не обрезают существующий выходной файл. Изменение от @SulimanAbdulrazzaq в [#488](https://github.com/D4Vinci/Scrapling/pull/488).
- **Исправлена обработка параметров user-agent и proxy команды curl в `curl2fetcher()`**. Изменение от @SulimanAbdulrazzaq в [#490](https://github.com/D4Vinci/Scrapling/pull/490).

- **Исправлено слияние блоков Markdown**, когда несколько выбранных элементов преобразуются через `Response.markdown()` или извлечение в CLI. Включены изменения от @Yigtwxx в [#432](https://github.com/D4Vinci/Scrapling/pull/432).
- **Исправлена очистка скрытого содержимого для вывода ИИ**: видимое содержимое, например `opacity:0.95`, сохраняется, распознаётся больше скрывающих стилей, а скрытые слоты удаляются. Включены изменения от @Yigtwxx в [#460](https://github.com/D4Vinci/Scrapling/pull/460).
- **Исправлена преждевременная остановка удаления лишних тегов при вложенности**. Изменение от @Yigtwxx в [#474](https://github.com/D4Vinci/Scrapling/pull/474).
- **Исправлены создаваемые CSS- и XPath-селекторы для первого из нескольких элементов одного родителя с одинаковым тегом**. Изменение от @yellow-dog-dog в [#495](https://github.com/D4Vinci/Scrapling/pull/495).
- **Устранено предупреждение об устаревании в HTML-парсере lxml**. Изменение от @afsuyadi в [#493](https://github.com/D4Vinci/Scrapling/pull/493).

### Документация {#v0.5-docs}

- **Весь сайт теперь доступен на десяти языках**: английском, арабском, испанском, бразильском португальском, французском, немецком, упрощённом китайском, японском, русском и корейском. Переведены руководства, справочники API, учебные материалы и [история изменений](changelog.md). Для арабского поддерживается направление справа налево, а при смене языка сохраняются страница и раздел.
- **Более понятные руководства, примеры README и шаги настройки**, которые охватывают данные контрольных точек, кодировки браузера, сохранённое состояние, историю сети, Shadow DOM и порядок обхода.
- **Обновлён Agent Skill**, его примеры, справочные материалы и архив для загрузки с учётом текущих инструментов браузера и MCP.
- **История изменений перенесена на сайт**, и добавлен доступ к исходному Markdown каждой страницы.

### Проект {#v0.5-project}

- Обновлены логотип Scrapling, изображения обложек и оформление сайта.
- Расширены тесты действий браузера, диалогов, извлечения, снимков экрана, JavaScript, записи сети, файлов состояния, Shadow DOM и исправлений обхода.
- Добавлен маркер браузерных тестов и отдельные запуски для браузерных, асинхронных и параллельных тестов. Улучшена совместимость тестов контрольных точек и CSV с Windows. Изменение от @diegobravtraps-oss в [#457](https://github.com/D4Vinci/Scrapling/pull/457).
- Обновлены общие настройки сборки многоязычной документации и правила участия в проекте.

## [v0.4.15](https://github.com/D4Vinci/Scrapling/releases/tag/v0.4.15) - 2026-08-23 {#v0.4.15}

**Один из крупнейших выпусков в этом году: переработанный MCP-сервер, Markdown для RAG одной строкой, улучшенное прохождение проверок Cloudflare и вкладки браузера, которые остаются открытыми для автоматизации 🚀**

!!! warning "Внимание"

    **Этот выпуск вносит несовместимые изменения в MCP-сервер. Перед обновлением прочитайте раздел [несовместимых изменений](https://github.com/D4Vinci/Scrapling/blob/v0.4.15/docs/ai/mcp-server.md#breaking-changes).**

### 🚀 Новые возможности и улучшения удобства {#v0.4.15-new-stuff-and-quality-of-life-changes}

- **Вкладки браузера теперь остаются открытыми и используются повторно между запросами** (см. [документацию](fetching/stealthy.md#session-management)):
    - Все браузерные сессии сохраняют вкладки после запроса. Следующий запрос использует свободную вкладку, а не открывает новую.
    - Каждый запрос заново применяет свои настройки к полученной вкладке: тайм-ауты, заголовки и блокировку ресурсов. Поэтому настройки не переходят из одного запроса в другой.
    - Вкладки с ошибками закрываются и заменяются новыми. Новый метод `close_pages()` закрывает все открытые вкладки.
    - Полученная страница остаётся загруженной, поэтому функция `page_setup` следующего запроса выполняется на ней до перехода на другой адрес. Это позволяет связывать автоматические действия между запросами.

- **Преобразуйте любую страницу в чистый Markdown для LLM с помощью `Response.markdown()`** (см. [документацию](ai/building-rag-systems.md)):

    ```python
    from scrapling.fetchers import Fetcher

    markdown = Fetcher.get("https://example.com").markdown(main_content_only=True)
    ```

    - Сначала всегда удаляются скрипты, стили и скрытое содержимое с внедрёнными инструкциями для модели. Такую же очистку выполняет MCP-сервер.
    - Передайте `css_selector`, чтобы преобразовать только нужные элементы.
    - Функция доступна в новой группе зависимостей `rag` (`pip install "scrapling[rag]"`), которая также входит в группы `ai`/`shell`/`all`.

- **Новый шаблон `SiteToMarkdownSpider` обходит весь сайт и создаёт набор Markdown-документов для RAG-конвейеров** (см. [документацию](ai/building-rag-systems.md)):

    ```python
    from scrapling.spiders import SiteToMarkdownSpider

    class DocsSpider(SiteToMarkdownSpider):
        name = "docs"
        start_urls = ["https://example.com/docs/"]
        allowed_domains = {"example.com"}
        output_dir = "docs_markdown"

    result = DocsSpider().start()
    result.items.to_jsonl("docs.jsonl")
    ```

    - Выдаёт один элемент на страницу с полями `url`/`title`/`markdown`. Необязательный параметр `output_dir` позволяет записывать каждую страницу в отдельный Markdown-файл.
    - `max_pages` ограничивает число страниц при обходе. Шаблон основан на `CrawlSpider`, поэтому, переопределив `rules()`, вы можете полностью управлять выбором ссылок для перехода.

- **MCP-сервер переработан (есть несовместимые изменения)** (см. [несовместимые изменения](https://github.com/D4Vinci/Scrapling/blob/v0.4.15/docs/ai/mcp-server.md#breaking-changes) и [документацию](ai/mcp-server.md)):
    - 13 инструментов теперь разделены на два режима: инструменты для разовых запросов (`fetch`, `bulk_fetch`, `stealthy_fetch`, `bulk_stealthy_fetch`), которые всегда запускают свой браузер и показывают реальные настройки по умолчанию, и инструменты сессий, которые используют однажды открытую сессию.
    - Новый инструмент `session_fetch` получает страницы через браузерную сессию. `open_session` теперь хранит только настройки уровня браузера и возвращает ИИ-агенту фактические настройки сессии.
    - Инструмент `get` переименован в `make_request` и теперь поддерживает любой HTTP-метод.
    - Новые инструменты `open_request_session` и `session_make_request` дают ИИ постоянные HTTP-сессии, которые сохраняют cookie и отпечаток браузера между запросами.
    - Это также устраняет сброс настроек сессии при получении страниц. Первое исправление этой проблемы внесено @Yigtwxx в [#418](https://github.com/D4Vinci/Scrapling/pull/418).

- **HTTP-транспорт MCP-сервера теперь требует аутентификации и по умолчанию привязан к localhost (несовместимое изменение)**. Изменение от @yamantaka-singh в [#414](https://github.com/D4Vinci/Scrapling/pull/414) (исправляет [#413](https://github.com/D4Vinci/Scrapling/issues/413), см. [документацию](ai/mcp-server.md#authentication)):
    - Передайте `--auth-token` (или переменную окружения `SCRAPLING_MCP_AUTH_TOKEN`), чтобы требовать Bearer-токен, либо `--no-auth`, чтобы явно запустить сервер без аутентификации.
    - Передайте `--host 0.0.0.0`, чтобы принимать подключения из сети.

### 🐛 Исправления ошибок {#v0.4.15-bug-fixes}

- **Проверки Cloudflare Turnstile/Interstitial теперь проходят независимо от локали браузера, а интерактивные проверки больше не вызывают бесконечный цикл в режиме без окна**. Страницы скрытного браузера также перестали падать во время проверки. Включены изменения от @subediparas5 в [#412](https://github.com/D4Vinci/Scrapling/pull/412). (Исправляет [#411](https://github.com/D4Vinci/Scrapling/issues/411) и [#422](https://github.com/D4Vinci/Scrapling/issues/422).)
- **Исправлен незаметный пропуск элементов с несколькими классами в `find`/`find_all` при использовании `class_`**. Изменение от @yetval в [#410](https://github.com/D4Vinci/Scrapling/pull/410). **Также исправлена обработка пустых значений `class_` и неэкранированных строковых значений CSS**. Изменение от @yamantaka-singh в [#417](https://github.com/D4Vinci/Scrapling/pull/417).
- **Исправлена потеря метаданных запроса при повторном использовании кешированных ответов в `development_mode`**. Изменение от @Yigtwxx в [#419](https://github.com/D4Vinci/Scrapling/pull/419).
- **Исправлена ошибка HTTP-запросов с `retries` меньше 1: запрос завершался с ошибкой ещё до отправки**. Изменение от @Yigtwxx в [#420](https://github.com/D4Vinci/Scrapling/pull/420).

### Документация {#v0.4.15-docs}

- **Разделы сайта перестроены**: новый раздел «Использование с ИИ» содержит MCP-сервер, новую страницу [Agent Skill](ai/agent-skill.md) и руководство [Создание RAG-систем](ai/building-rag-systems.md). Руководство по переходу с BeautifulSoup перенесено к интеграции со Scrapy в раздел «Интеграции и переход».
- **В репозиторий добавлена [история изменений](changelog.md)** с заметками обо всех выпусках.

## [v0.4.14](https://github.com/D4Vinci/Scrapling/releases/tag/v0.4.14) - 2026-08-10 {#v0.4.14}

**Небольшой технический выпуск для исправления установки через `uv` 🔧**

### 🐛 Исправления ошибок {#v0.4.14-bug-fixes}

- **Исправлена проблема, из-за которой `uv` по умолчанию отказывался устанавливать v0.4.13 и незаметно выбирал более старую версию**. Предыдущий выпуск требовал предварительную версию `curl_cffi`, а `uv` не разрешает такие версии без явного включения.
Теперь для всех зависимостей доступны стабильные версии. (Исправляет [#407](https://github.com/D4Vinci/Scrapling/issues/407).)

## [v0.4.13](https://github.com/D4Vinci/Scrapling/releases/tag/v0.4.13) - 2026-08-09 {#v0.4.13}

**Новое обновление с пауками для фидов и более умным MCP-сервером 🎉**

### 🚀 Новые возможности и улучшения удобства {#v0.4.13-new-stuff-and-quality-of-life-changes}

- **Новые шаблоны пауков для фидов**. `XMLFeedSpider` перебирает узлы любого XML-фида (RSS, Atom, товарные фиды и т. д.), а `CSVFeedSpider` перебирает строки CSV как словари. Оба автоматически распаковывают фиды, сжатые gzip. (См. [документацию](spiders/generic-templates.md).)

  ```python
  from scrapling.spiders import XMLFeedSpider

  class RSSSpider(XMLFeedSpider):
      name = "rss"
      start_urls = ["https://example.com/feed.xml"]

      async def parse_node(self, response, node):
          yield {"title": node.findtext("title"), "link": node.findtext("link")}

  result = RSSSpider().start()
  ```

- **MCP-сервер обновлён до MCP SDK v2 и стал умнее**. Теперь сервер содержит инструкции, которые учат ИИ-агента эффективно использовать инструменты. Каждый инструмент объявляет аннотации, чтобы клиенты вроде Claude Code могли автоматически разрешать действия только для чтения. Описания инструментов сокращены для экономии токенов. Сервер также сообщает MCP-клиентам свою версию и логотип. (См. [документацию](ai/mcp-server.md).)
- **Добавлена команда `scrapling-mcp`**, которая напрямую соответствует `scrapling mcp`. Теперь Scrapling можно зарегистрировать одной строкой в MCP-клиентах и реестрах, ожидающих одну команду.
- **Снята фиксация версий Playwright/Patchright и браузеров**. Создаваемый User-Agent браузера теперь всегда точно соответствует версии Chromium, которой управляет установленный Playwright/Patchright. Поэтому Scrapling больше не фиксирует их версии, и вы можете свободно их обновлять. После обновления выполните `scrapling install --force`, чтобы обновить браузеры.

### 🐛 Исправления ошибок {#v0.4.13-bug-fixes}

- **Исправлено падение при импорте Scrapling с ошибкой ValueError из `browserforge`**, когда пакет данных отпечатков отстаёт от версий браузеров. (Исправляет [#394](https://github.com/D4Vinci/Scrapling/issues/394), [#396](https://github.com/D4Vinci/Scrapling/issues/396) и [#400](https://github.com/D4Vinci/Scrapling/issues/400).)
- **Исправлен неверный размер пулов страниц в инструментах MCP для пакетной работы с браузером**. Из-за него `bulk_fetch` завершался ошибкой при обработке более 50 URL за раз, а `bulk_stealthy_fetch` получал все URL через одну вкладку. Изменение от @Yigtwxx в [#393](https://github.com/D4Vinci/Scrapling/pull/393).

### Проект {#v0.4.13-project}

- **Новая [политика участия с помощью ИИ](https://github.com/D4Vinci/Scrapling/blob/main/AI_POLICY.md)**: вклад с помощью ИИ приветствуется, но его использование нужно указывать в PR или Issue. Материалы, похожие на результат работы ИИ без такого указания, будут помечены и закрыты.

## [v0.4.12](https://github.com/D4Vinci/Scrapling/releases/tag/v0.4.12) - 2026-07-26 {#v0.4.12}

**Выпуск, который помогает паукам лучше учитывать особенности сайтов при обходе**

### 🚀 Новые возможности и улучшения удобства {#v0.4.12-new-stuff-and-quality-of-life-changes}

- **Пауки теперь могут сами регулировать скорость с помощью AutoThrottle.** Вместо подбора `download_delay`, который может быть слишком большим или приводить к блокировке, паук измеряет скорость ответа каждого сайта и сам меняет задержку для каждого домена. Если сайт начинает блокировать запросы или ограничивать их частоту, паук удваивает задержку (или ждёт ровно столько, сколько указано в заголовке `Retry-After`), пока ограничения не исчезнут, а затем снова ускоряется. Ваши `download_delay` и `Crawl-delay` из robots.txt по-прежнему задают минимальную задержку. (См. [документацию](spiders/advanced.md#autothrottle).)

    ```python
    class MySpider(Spider):
        name = "adaptive"
        start_urls = ["https://example.com"]
        autothrottle_enabled = True
        autothrottle_start_delay = 2.0
        autothrottle_max_delay = 30.0
        autothrottle_block_backoff = True
    ```

- **Результаты можно экспортировать в CSV и XML**, помимо уже доступных JSON/JSONL. Даже если у элементов разные ключи, они экспортируются без потери данных, а вложенные значения записываются как JSON. (См. [документацию](spiders/getting-started.md).)

    ```python
    result = MySpider().start()
    result.items.to_csv("products.csv")
    result.items.to_xml("products.xml")
    ```

- **MCP-сервер теперь может требовать аутентификации**, поэтому его можно безопасно открыть для внешних подключений, а не оставлять только на своём компьютере. Запросы без токена отклоняются. Также можно ограничить имена хостов, на которые отвечает сервер. (См. [документацию](ai/mcp-server.md).)

    ```bash
    scrapling mcp --http --auth-token "$(openssl rand -hex 32)"
    ```

- **Браузеры теперь принимают CDP URL по HTTP**, а не только по WebSocket. Помимо адресов `wss://` от браузерных сервисов, любой браузерный Fetcher или MCP-сессию можно подключить к Chrome, который вы сами запустили с `--remote-debugging-port=9222`.

- **Публикуемые Docker-образы теперь имеют тег версии выпуска**, а не только `latest`, чтобы вы могли выбрать точную версию. Изменение от @JanRK в [#384](https://github.com/D4Vinci/Scrapling/pull/384).

### 🐛 Исправления ошибок {#v0.4.12-bug-fixes}

- **Исправлена потеря всех cookie при кешировании ответов браузерного движка**. В режиме разработки пауков это незаметно нарушало работу сессий и аутентификации, которые зависели от cookie. Изменение от @amitvijapur в [#379](https://github.com/D4Vinci/Scrapling/pull/379). (Исправляет [#376](https://github.com/D4Vinci/Scrapling/issues/376).)

- **Исправлена проблема в `StealthyFetcher`, который принудительно задавал локаль `en-US`** для всех браузеров вместо локали системы. Из-за несовпадения локали и IP-адреса сайты считали запросы подозрительными, например Google отвечал кодом 429. (Исправляет [#381](https://github.com/D4Vinci/Scrapling/issues/381).)

- **Исправлено вводящее в заблуждение сообщение об ошибке в системе хранения** и удалён ненужный вызов после вставки данных. Изменение от @fix2015 в [#377](https://github.com/D4Vinci/Scrapling/pull/377).

### Производительность {#v0.4.12-performance}

- **Время работы `get_all_text()` теперь растёт пропорционально числу узлов, O(nodes)**. Метод больше не обходит предков каждого текстового узла, поэтому на страницах с глубокой вложенностью работает примерно в 5-6 раз быстрее. Изменение от @yetval в [#378](https://github.com/D4Vinci/Scrapling/pull/378).

## [v0.4.11](https://github.com/D4Vinci/Scrapling/releases/tag/v0.4.11) - 2026-07-12 {#v0.4.11}

**Большое обновление: первый шаблон паука для платформы, более быстрый парсер и важные исправления 🎉**

### 🚀 Новые возможности и улучшения удобства {#v0.4.11-new-stuff-and-quality-of-life-changes}

- **Добавлен `ShopifySpider`, первый шаблон паука для платформы!** Извлекайте все товары из любого магазина на Shopify через его JSON API, не работая с HTML сайта. Создайте подкласс, задайте домен магазина, и всё готово (см. [документацию](spiders/platform-templates.md)).

  ```python
  from scrapling.spiders import ShopifySpider

  class MyStore(ShopifySpider):
      target_website = "example.com"

  result = MyStore().start()
  ```

- **В браузерные команды CLI добавлен `--executable-path`**. И `scrapling extract fetch`, и `scrapling extract stealthy-fetch` теперь принимают путь к исполняемому файлу любого Chromium-совместимого браузера. Если параметр не передан, используется переменная окружения `SCRAPLING_EXECUTABLE_PATH`, как и в MCP-сервере (решает [#371](https://github.com/D4Vinci/Scrapling/issues/371)).

  ```bash
  scrapling extract fetch "https://example.com" page.html --executable-path "/path/to/chromium"
  ```

### 🤖 Улучшения удобства {#v0.4.11-quality-of-life-changes}
- **`find_by_text` и `find_by_regex` теперь работают до ~2 раз быстрее** при включённом `first_match` (по умолчанию). Объекты для элементов создаются только по мере необходимости, поэтому поиск останавливается на первом совпадении. Изменение от @yetval в [#370](https://github.com/D4Vinci/Scrapling/pull/370).
- **Бенчмарки обновлены: новые результаты сравниваются с последними версиями всех библиотек.**
- **Обновлены правила участия в проекте.**

### 🐛 Исправления ошибок {#v0.4.11-bug-fixes}

- **Исправлено падение инструментов получения страниц MCP-сервера на страницах с управляющими символами** с ошибкой `All strings must be XML compatible`. Изменение от @yetval в [#368](https://github.com/D4Vinci/Scrapling/pull/368) (исправляет [#366](https://github.com/D4Vinci/Scrapling/issues/366)).

## [v0.4.10](https://github.com/D4Vinci/Scrapling/releases/tag/v0.4.10) - 2026-07-04 {#v0.4.10}

**Новое обновление с интеграцией со Scrapy и набором исправлений от сообщества 🎉**

### 🚀 Новые возможности и улучшения удобства {#v0.4.10-new-stuff-and-quality-of-life-changes}

- **Добавлена интеграция со Scrapy**, чтобы использовать API парсинга Scrapling в существующих проектах Scrapy без переписывания. Добавьте декоратор `scrapling_response` к любому обработчику паука, и получаемый им ответ станет объектом `Response` из Scrapling. Сам обход по-прежнему выполняет Scrapy (см. [документацию](integrations/scrapy.md)):

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
                yield {"text": quote.get_all_text(strip=True)}
    ```

- **MCP-сервер теперь поддерживает любой Chromium-совместимый браузер** во всех браузерных инструментах. Задайте его один раз через `scrapling mcp --executable-path "/path/to/chromium"` или переменную окружения `SCRAPLING_EXECUTABLE_PATH`, либо для отдельного запроса через аргумент `executable_path`. Изменение от @samrusani в [#360](https://github.com/D4Vinci/Scrapling/pull/360) (решает [#347](https://github.com/D4Vinci/Scrapling/issues/347)).
- **Обновлены все браузеры и отпечатки**. После обновления выполните `scrapling install --force`, чтобы применить изменения.

### 🐛 Исправления ошибок {#v0.4.10-bug-fixes}

- **Исправлён искажённый текст (mojibake) в ответах браузерных Fetcher на сайтах с кодировкой не UTF-8**. Изменение от @yehudalevy-collab в [#365](https://github.com/D4Vinci/Scrapling/pull/365) (исправляет [#364](https://github.com/D4Vinci/Scrapling/issues/364)).
- **Исправлена проблема в `LinkExtractor`, который не отфильтровывал составные расширения вроде `.tar.gz`**. Изменение от @renbkna в [#359](https://github.com/D4Vinci/Scrapling/pull/359) (исправляет [#349](https://github.com/D4Vinci/Scrapling/issues/349)).
- **Исправлена потеря выполняющихся запросов из контрольных точек при паузе обхода: теперь при возобновлении они не пропускаются**. Изменение от @yetval в [#358](https://github.com/D4Vinci/Scrapling/pull/358).
- **Исправлен неверный расчёт задержек обхода по директивам `Request-rate` из robots.txt** благодаря обновлению Protego. Соответствующее обновление тестов от @Disaster-Terminator внесено в [#355](https://github.com/D4Vinci/Scrapling/pull/355).

### Документация {#v0.4.10-docs}

- **Уточнено взаимодействие `init_script` с изолированным контекстом выполнения Patchright в скрытном режиме**. Изменение от @mturac в [#353](https://github.com/D4Vinci/Scrapling/pull/353) (решает [#350](https://github.com/D4Vinci/Scrapling/issues/350)).
- **Добавлен способ установки навыка через [skills.sh](https://skills.sh/D4Vinci/Scrapling)**. Изменение от @ob-aion в [#363](https://github.com/D4Vinci/Scrapling/pull/363).

## [v0.4.9](https://github.com/D4Vinci/Scrapling/releases/tag/v0.4.9) - 2026-06-07 {#v0.4.9}

**Техническое обновление с множеством исправлений по сообщениям сообщества 🛠️**

### 🚀 Новые возможности и улучшения удобства {#v0.4.9-new-stuff-and-quality-of-life-changes}

- **Обновлены все браузеры и отпечатки**. После обновления выполните `scrapling install --force`, чтобы применить изменения.
- **В CLI добавлен флаг `--version`**. Изменение от @ETM-Code в [#303](https://github.com/D4Vinci/Scrapling/pull/303) (решает [#299](https://github.com/D4Vinci/Scrapling/issues/299)).

### 🐛 Исправления ошибок {#v0.4.9-bug-fixes}

- **Исправлено незаметное игнорирование аргумента `proxy` уровня сессии в HTTP-сессиях**, которое могло раскрыть ваш настоящий IP (решает [#295](https://github.com/D4Vinci/Scrapling/issues/295)). Теперь смешивание `proxy` уровня сессии с `proxies` отдельного запроса (или наоборот) вызывает ошибку, а не незаметно отбрасывает один из аргументов.
- **Исправлены сбои переходов браузера при сочетании `init_script` с `user_data_dir`** (решает [#294](https://github.com/D4Vinci/Scrapling/issues/294)).
- **Исправлено определение кодировки, когда сайт заключает значение charset в кавычки в заголовке `Content-Type`**. Изменение от @Bortlesboat в [#323](https://github.com/D4Vinci/Scrapling/pull/323).
- **Исправлена ошибка `IndexError` при адаптивном поиске элементов с включённым `auto_save`**. Изменение от @Mubashirrrr в [#340](https://github.com/D4Vinci/Scrapling/pull/340).
- **Исправлено падение при сохранении контрольных точек и кеша пауков в Windows**. Изменение от @MrStarkEG в [#344](https://github.com/D4Vinci/Scrapling/pull/344).
- **Исправлена неверная оценка сходства в `find_similar` для элементов с разным количеством атрибутов** (решает [#322](https://github.com/D4Vinci/Scrapling/issues/322)).

### Документация {#v0.4.9-docs}

- **Уточнено, что установка по умолчанию включает только парсер**, а для Fetcher и пауков нужны дополнительные группы зависимостей (решает [#343](https://github.com/D4Vinci/Scrapling/issues/343)).
- **Исправлено имя Docker-образа в оставшихся примерах**. Изменение от @evanclan в [#315](https://github.com/D4Vinci/Scrapling/pull/315).
- **Исправлена неработающая ссылка в руководстве по участию**. Изменение от @Bortlesboat в [#320](https://github.com/D4Vinci/Scrapling/pull/320).

## [v0.4.8](https://github.com/D4Vinci/Scrapling/releases/tag/v0.4.8) - 2026-05-11 {#v0.4.8}

**Большое обновление пауков, которое расширяет возможности фреймворка для обхода сайтов 🕷️**

### 🚀 Новые возможности и улучшения удобства {#v0.4.8-new-stuff-and-quality-of-life-changes}

- **Добавлен инструмент `LinkExtractor`** в `scrapling.spiders.LinkExtractor` для извлечения URL из `Response`. Есть множество настроек (см. [документацию](spiders/generic-templates.md)).

    ```python
    from scrapling.spiders import LinkExtractor

    extractor = LinkExtractor(allow=r"/posts/", deny_domains=["ads.example.com"])
    ```

- **Добавлены универсальные шаблоны пауков `CrawlSpider` и `CrawlRule`**, чтобы не писать каждый раз один и тот же код для перехода по ссылкам, соответствующим шаблону. Переопределите `rules()`, чтобы вернуть список объектов `CrawlRule`, каждый из которых связан с `LinkExtractor`. (См. [документацию](spiders/generic-templates.md).)

    ```python
    from scrapling.spiders import CrawlSpider, CrawlRule, LinkExtractor

    class QuotesSpider(CrawlSpider):
        name = "blog"
        start_urls = ["https://quotes.toscrape.com/"]

        def rules(self):
            return [
                CrawlRule(LinkExtractor(allow=r"/author/"), callback=self.parse_author),
                CrawlRule(LinkExtractor(allow=r"/page/\d+/")),  # pagination, no callback
            ]

        async def parse_author(self, response):
            yield {
                "name": response.css(".author-title::text").get(),
                "birthday": response.css(".author-born-date::text").get(),
                "url": response.url,
            }
    ```

- **Добавлен шаблон `SitemapSpider`**, который начинает обход прямо с URL карты сайта или `robots.txt`. Поддерживает карты сайта, сжатые gzip, и множество настроек. URL распределяются по правилам обхода, как в примере с **CrawlSpider** выше. (См. [документацию](spiders/generic-templates.md).)

    ```python
    from scrapling.spiders import SitemapSpider, CrawlRule, LinkExtractor

    class NewsSitemap(SitemapSpider):
        name = "news"
        sitemap_urls = ["https://example.com/robots.txt"]

        def rules(self):
            return [
                CrawlRule(LinkExtractor(allow=r"/articles/"), callback=self.parse_article),
            ]

        async def parse_article(self, response):
            yield {"url": response.url, "title": response.css("h1::text").get()}
    ```

- **Адаптивный поиск теперь использует порог сходства 40% по умолчанию** вместо `0` во всех методах. Это улучшает работу адаптивной функции. Если ни один элемент не превышает порог, предупреждение показывает максимальную найденную оценку, чтобы вы могли осознанно уменьшить `percentage`, если нужно.

- **Обновлены все браузеры и отпечатки**. После обновления снова выполните `scrapling install  --force`, чтобы обновить браузеры и отпечатки.

### 🐛 Исправления ошибок {#v0.4.8-bug-fixes}

- **Исправлена ошибка: `Fetcher.configure(...)` не применялся к отдельным запросам**. Такое же исправление внесено в `AsyncFetcher`.
- **Исправлен неверный расчёт отпечатков запросов, из-за которого пауки отправляли повторяющиеся запросы**. Изменение от @yetval в [#255](https://github.com/D4Vinci/Scrapling/pull/255).
- **Исправлено отсутствие предупреждений при слабых совпадениях в движке адаптивного сбора данных.** Вместе с изменением порога выше это означает, что при неудачном поиске вы получите предупреждение, а не вводящий в заблуждение «наиболее подходящий» элемент.

### Документация {#v0.4.8-docs}

- **Обновлены старые примеры кода** во всей документации, чтобы они соответствовали текущей версии.
- **Улучшены копирование и вставка кода** на сайте документации. Навык агента сокращён, чтобы расходовать меньше токенов при каждом вызове.

## [v0.4.7](https://github.com/D4Vinci/Scrapling/releases/tag/v0.4.7) - 2026-04-17 {#v0.4.7}

**Обновление, которое даёт вашим ИИ-агентам возможность видеть страницы 📸**

### 🚀 Новые возможности и улучшения удобства {#v0.4.7-new-stuff-and-quality-of-life-changes}

- **Добавлен MCP-инструмент `screenshot`**, который делает снимок страницы и возвращает его как настоящий блок MCP `ImageContent`, чтобы модель могла его видеть. Нужна открытая браузерная сессия, поэтому сначала вызовите `open_session` (с типом `dynamic` или `stealthy`), а затем передайте сюда `session_id`. Поддерживаются PNG и JPEG, снимки всей страницы, настройка качества JPEG и обычные параметры ожидания (`wait`, `wait_selector`, `network_idle`, `timeout`). (Реализует [#244](https://github.com/D4Vinci/Scrapling/issues/244).)
- **Добавлен параметр для собственного `session_id` в `open_session`**, чтобы давать сессиям понятные имена (`"search"`, `"checkout"`) вместо случайной 12-символьной шестнадцатеричной строки по умолчанию. Изменение от @hauntedhost в [#243](https://github.com/D4Vinci/Scrapling/pull/243).

### 🐛 Исправления ошибок {#v0.4.7-bug-fixes}

- **Исправлены повреждение состояния `FetcherSession` и падение при закрытии сессии с отложенной инициализацией**. Изменение от @yetval в [#245](https://github.com/D4Vinci/Scrapling/pull/245).
- **Исправлена ошибка `TypeError: Session.request() got an unexpected keyword argument 'block_ads'`** при использовании флага CLI `--ai-targeted` с HTTP-командами. Изменение от @voidborne-d в [#249](https://github.com/D4Vinci/Scrapling/pull/249) (исправляет [#247](https://github.com/D4Vinci/Scrapling/issues/247)).

### Переводы {#v0.4.7-translations}

- **Добавлен перевод README на бразильский португальский** от @rgomids в [#250](https://github.com/D4Vinci/Scrapling/pull/250).

## [v0.4.6](https://github.com/D4Vinci/Scrapling/releases/tag/v0.4.6) - 2026-04-13 {#v0.4.6}

**Обновление скрытной работы браузера, конфиденциальности и удобства разработки 🔒**

### 🚀 Новые возможности и улучшения удобства {#v0.4.6-new-stuff-and-quality-of-life-changes}

- **Добавлена встроенная блокировка рекламы** для браузерных Fetcher. Передайте `block_ads=True`, чтобы блокировать запросы примерно к 3 500 известным рекламным и отслеживающим доменам при перехвате маршрута. Запрос сразу отменяется, без DNS и TCP. Можно сочетать с `blocked_domains` для собственных списков. MCP-сервер и режим CLI `--ai-targeted` включают это автоматически, чтобы экономить токены и ускорять загрузку страниц.

    ```python
    page = StealthyFetcher.fetch('https://example.com', block_ads=True)
    ```

- **Добавлена поддержка DNS-over-HTTPS** для предотвращения утечек DNS при использовании прокси. Передайте `dns_over_https=True`, чтобы отправлять DNS-запросы через DoH Cloudflare. Тогда определение адресов через DNS не раскроет ваше настоящее местоположение, даже если HTTP-трафик идёт через прокси.

    ```python
    page = StealthyFetcher.fetch('https://example.com', proxy='http://proxy:8080', dns_over_https=True)
    ```

- **Добавлен обработчик `page_setup`** для браузерных Fetcher. Эта функция запускается перед `page.goto()` и позволяет зарегистрировать обработчики событий, маршруты и скрипты, которые нужно настроить до перехода на страницу. Дополняет `page_action`, который запускается после перехода. (Решает [#237](https://github.com/D4Vinci/Scrapling/issues/237).)

    ```python
    def capture_websockets(page):
        page.on("websocket", lambda ws: print(f"WS: {ws.url}"))

    page = DynamicFetcher.fetch('https://example.com', page_setup=capture_websockets)
    ```

- **Добавлены параметры CLI `--block-ads` и `--dns-over-https`** для команд `fetch` и `stealthy-fetch`.

### 🐛 Исправления ошибок {#v0.4.6-bug-fixes}

- **Исправлен псевдоним типа `Seconds`**, который не принимал дробные значения. Передача `wait=1.5` или `timeout=500.0` в браузерные Fetcher вызывала ошибку типов, потому что псевдоним ошибочно считал `float` метаданными, а не типом. Изменение от @kuishou68 в [#240](https://github.com/D4Vinci/Scrapling/pull/240).
- **Исправлено дублирование частей с ID при генерации селектора полного пути**. При создании полных CSS/XPath-путей селекторы элементов с атрибутом `id` добавлялись дважды, что давало строки вроде `body > #main > #main > #target > #target`. Также исправлена генерация отдельного условия `[@id='x']` (недопустимый XPath) вместо `*[@id='x']` в полном пути XPath. Изменение от @sjhddh в [#241](https://github.com/D4Vinci/Scrapling/pull/241).
- **Добавлены недостающие параметры в сигнатуры функций оболочки**. В сигнатурах интерактивной оболочки отсутствовали `blocked_domains`, `block_ads`, `retries`, `retry_delay`, `capture_xhr`, `executable_path` и `dns_over_https`.

## [v0.4.5](https://github.com/D4Vinci/Scrapling/releases/tag/v0.4.5) - 2026-04-07 {#v0.4.5}

**Обновление с одной большой возможностью для удобства разработки пауков и несколькими важными исправлениями 🎉**

### 🚀 Новые возможности и улучшения удобства {#v0.4.5-new-stuff-and-quality-of-life-changes}

- **Режим разработки пауков**: раньше каждая проверка изменений в `parse()` требовала снова обращаться к целевым серверам. Это медленно, создаёт лишнюю нагрузку и может привести к ограничению запросов ещё во время подбора селекторов. Новый режим разработки кеширует каждый ответ на диск при первом запуске и читает ответы с диска при следующих запусках. Вы можете менять обработчики и запускать паука сколько угодно раз, не отправляя ни одного сетевого запроса. Для включения достаточно одного атрибута класса:

    ```python
    class MySpider(Spider):
        name = "my_spider"
        start_urls = ["https://example.com"]
        development_mode = True

        async def parse(self, response):
            yield {"title": response.css("title::text").get("")}
    ```

    По умолчанию кеш хранится в `.scrapling_cache/{spider.name}/`. Его можно перенести куда угодно с помощью `development_cache_dir`. Новые счётчики `cache_hits` и `cache_misses` показывают, как используется кеш. Чтение из кеша пропускает `download_delay`, ограничение частоты и повторы заблокированных запросов, поэтому скорость проверки изменений зависит только от диска. Не оставляйте `development_mode = True` у паука в рабочей среде: это инструмент разработки, а не рабочий кеш. Подробнее в [документации](spiders/advanced.md#development-mode).

- **Более безопасные перенаправления по умолчанию**: значение `follow_redirects` теперь равно `"safe"` во всех HTTP-Fetcher, MCP-сервере и оболочке. Перенаправления по-прежнему выполняются, но адреса с внутренними или частными IP (loopback, частные сети, link-local) отклоняются. Это защищает от SSRF при сборе данных по URL, полученным от пользователей. Передайте `follow_redirects="all"`, чтобы вернуть старое поведение, или `False`, чтобы полностью отключить перенаправления.

### 🐛 Исправления ошибок {#v0.4.5-bug-fixes}

- **При принудительной остановке больше не теряется контрольная точка**: двойное нажатие Ctrl+C (принудительная остановка) у паука с включённым `crawldir` могло совпасть с записью контрольной точки. Область отмены завершала задачу до окончания записи pickle, оставляя `paused=False` и запуская очистку, которая *удаляет* предыдущую контрольную точку. В результате принудительная остановка долгого обхода могла привести к потере всего прогресса, который вы хотели сохранить. Теперь движок записывает контрольную точку **до** вызова `cancel_scope.cancel()`, поэтому принудительная остановка всегда сохраняет последнее состояние ожидающих задач. Изменение от @voidborne-d в [#230](https://github.com/D4Vinci/Scrapling/pull/230).

## [v0.4.4](https://github.com/D4Vinci/Scrapling/releases/tag/v0.4.4) - 2026-04-05 {#v0.4.4}

**Новое обновление с важными улучшениями пауков и исправлениями ошибок 🎉**

### 🚀 Новые возможности и улучшения удобства {#v0.4.4-new-stuff-and-quality-of-life-changes}
- **Во фреймворк пауков добавлено соблюдение robots.txt** через новую настройку `robots_txt_obey`. При её включении паук сам получает robots.txt перед обходом и соблюдает правила, включая `Disallow`, `Crawl-delay` и `Request-rate`. Файлы robots.txt загружаются параллельно и кешируются для каждого домена на всё время обхода. Изменение от @AbdullahY36 в [#226](https://github.com/D4Vinci/Scrapling/pull/226).
- **Добавлена предварительная подготовка кеша robots.txt**: до начала цикла обхода файлы robots.txt загружаются и разбираются для всех доменов из start_urls. Это устраняет задержку при первом запросе к каждому домену.
- **Добавлен счётчик `robots_disallowed_count`** в `CrawlStats`, чтобы отслеживать число запросов, заблокированных правилами robots.txt во время обхода.

Подробнее на сайте по [этой ссылке](spiders/getting-started.md#robotstxt-compliance).

### 🐛 Исправления ошибок {#v0.4.4-bug-fixes}
- **Исправлена серьёзная проблема MRO в `ProxyRotator`**: заглушка `_build_context_with_proxy` перекрывала настоящую реализацию из дочерних классов, из-за чего смена прокси всегда вызывала `NotImplementedError` (исправляет [#215](https://github.com/D4Vinci/Scrapling/issues/215)). Спасибо @yetval.
- **Исправлена утечка в пуле страниц** при смене прокси для каждого запроса в браузерных сессиях. Страницы из временных контекстов не удалялись из пула при очистке, поэтому в нём накапливались устаревшие ссылки. Изменение от @yetval в [#223](https://github.com/D4Vinci/Scrapling/pull/223).
- **Добавлена недостающая проверка типа** в статическом Fetcher: `curl_cffi` мог вернуть `None` из `session.request()`, что вызывало ошибки в дальнейшей обработке.

### Другие изменения {#v0.4.4-other}
- Обновлены зависимости, включая свежие отпечатки и другие улучшения.
- Добавлена новая зависимость `protego` в необязательную группу `fetchers` для разбора robots.txt.

## [v0.4.3](https://github.com/D4Vinci/Scrapling/releases/tag/v0.4.3) - 2026-03-30 {#v0.4.3}

**Новое обновление с множеством важных изменений 🎉**

### 🚀 Новые возможности и улучшения удобства {#v0.4.3-new-stuff-and-quality-of-life-changes}
- **Добавлен новый MCP-инструмент**, который открывает обычный или скрытный браузер и оставляет его открытым для дальнейшей работы других инструментов. Ещё один новый инструмент закрывает его. ([Примеры](https://github.com/D4Vinci/Scrapling/blob/v0.4.3/docs/ai/mcp-server.md#examples).)
- **Добавлен новый MCP-инструмент** для просмотра списка всех открытых браузерных сессий. Предназначен для работы с новыми инструментами.
- **В браузерные сессии добавлена новая настройка**, которая автоматически собирает все фоновые запросы, возникающие во время запроса (решает [#159](https://github.com/D4Vinci/Scrapling/pull/159)) [[Примеры](https://github.com/D4Vinci/Scrapling/blob/v0.4.3/docs/fetching/dynamic.md#capturing-xhrfetch-requests)].
- **Добавлено новое средство очистки**, которое убирает скрытое и невидимое содержимое, защищая MCP-сервер от распространённых атак с внедрением инструкций в промпт.
- **В команды сбора данных добавлен новый параметр командной строки** `--ai-targeted`. Он подготавливает содержимое для ИИ и защищает от распространённых атак с внедрением инструкций в промпт, как MCP-сервер.
- **В браузерные сессии добавлена новая настройка** `executable_path`, которая позволяет задать собственный путь к браузеру (решает [#202](https://github.com/D4Vinci/Scrapling/pull/202)).
- **Переработан** код MCP-сервера для упрощения поддержки. Все инструменты стали асинхронными.
- **Переработан** код команд CLI для упрощения поддержки. Он стал короче на 210 строк.

### 🐛 Исправления ошибок {#v0.4.3-bug-fixes}
- Исправлено сохранение HTTP-метода при повторных попытках в сессии паука. Изменение от @karesansui-u в [#201](https://github.com/D4Vinci/Scrapling/pull/201).
- Добавлен предел числа повторных попыток получения содержимого страницы, чтобы избежать бесконечного цикла. Изменение от @haosenwang1018 и @D4Vinci в [#197](https://github.com/D4Vinci/Scrapling/pull/197).
- `raise` без аргумента заменён на `return False` в `_restore_from_checkpoint`. Изменение от @haosenwang1018 в [#196](https://github.com/D4Vinci/Scrapling/pull/196).
- `get_all` заменён на `getall` в `Texthandler`, чтобы соответствовать классу Selector.

### Улучшения тестов и покрытия {#v0.4.3-coverage-tests-improvement}
- Добавлены тесты пограничных случаев `_normalize_credentials`. Изменение от @Bortlesboat в [#192](https://github.com/D4Vinci/Scrapling/pull/192).
- Добавлены тесты сохранения с последующим получением тех же данных и тесты основного хранилища. Изменение от @haosenwang1018 в [#193](https://github.com/D4Vinci/Scrapling/pull/193).
- Добавлены тесты ветвей обработки регулярных выражений в `TextHandler` и метода `TextHandlers.re()`. Изменение от @haosenwang1018 в [#194](https://github.com/D4Vinci/Scrapling/pull/194).
- Добавлены тесты пограничных случаев для `filter`, `iterancestors` и `find_similar`. Изменение от @awanawana в [#200](https://github.com/D4Vinci/Scrapling/pull/200).

### Улучшения Agent Skill {#v0.4.3-agent-skill-improvement}
- Исправлены неработающие Markdown-ссылки в справочных материалах навыка. Изменение от @yetval в [#204](https://github.com/D4Vinci/Scrapling/pull/204).
- Улучшена структура навыка для прохождения проверки [Clawhub](https://clawhub.ai/d4vinci/scrapling-official).
- Навык теперь обязан использовать параметр `--ai-targeted` при сборе данных через командную строку.

### Улучшения документации {#v0.4.3-docs-improvement}
- Добавлен перевод README на корейский от @greatsk55 в [#187](https://github.com/D4Vinci/Scrapling/pull/187).
- Исправлены пробелы между символами CJK и латиницей в китайском и японском README.
- Исправлены неработающие ссылки, оставшиеся от старого дизайна сайта.

## [v0.4.2](https://github.com/D4Vinci/Scrapling/releases/tag/v0.4.2) - 2026-03-08 {#v0.4.2}

**Новое техническое обновление с важными изменениями**

#### Исправления ошибок {#v0.4.2-bug-fixes}
- Функция `get_all_text()` теперь получает и текстовые узлы после закрывающих тегов элементов. Благодаря этому MCP-сервер и команды видят текст, который раньше пропускали ([#168](https://github.com/D4Vinci/Scrapling/pull/168)). Спасибо @mhillebrand.
- Для Referer теперь используется URL главной страницы Google вместо URL поиска Google. Предыдущая логика была неверной и могла создавать признак для обнаружения по отпечатку ([#179](https://github.com/D4Vinci/Scrapling/pull/179)). Спасибо @Bortlesboat.
- Исправлена проблема с объединением дополнительных флагов во всех браузерах. Спасибо @rostchri.
- Исправлена проблема с подсказками типов, которая приводила к сбою в версиях Python ниже 3.12. (Решает [#163](https://github.com/D4Vinci/Scrapling/issues/163))

#### Прочее {#v0.4.2-other}
- Добавлен Agent Skill для Claude Code / OpenClaw и других инструментов с ИИ-агентами.
- Agent Skill добавлен в Clawhub.
- Все браузеры и Playwright обновлены до последних версий.
- Добавлен французский перевод основного файла README.

## [v0.4.1](https://github.com/D4Vinci/Scrapling/releases/tag/v0.4.1) - 2026-02-27 {#v0.4.1}

**Обновление со многими важными изменениями**

### 🚀 Новые возможности и улучшения удобства {#v0.4.1-new-stuff-and-quality-of-life-changes}
- **Повышена точность регулярных выражений** для обнаружения проверок Cloudflare (спасибо @Rinz27 [#133](https://github.com/D4Vinci/Scrapling/pull/133)).
- **Повышены скорость и эффективность** прохождения проверок Cloudflare. Теперь они проходят почти вдвое быстрее.
- **Улучшено прохождение проверок Cloudflare** для сайтов, которые иногда дважды показывают страницу Cloudflare, прежде чем перейти к основному сайту.
- **Скрытный браузер стал быстрее и менее заметным** благодаря удалению внедряемых JS-файлов.
- **Улучшена схема MCP**, чтобы её принимал OpenCode (спасибо @robin-ede [#137](https://github.com/D4Vinci/Scrapling/pull/137)).
- **Улучшена совместимость схемы MCP**, чтобы её принимали VS Code Copilot и другие инструменты со строгими требованиями. (Решает #150)
- **Значительно сокращён расход токенов MCP-сервером**: при включённом параметре `main_content_only` удаляются бесполезные HTML-теги.
- Исправлена страница PyPI и добавлены файлы для регистрации MCP-сервера в реестре MCP-серверов.
- Добавлен пример установки зависимостей браузеров из кода, а не из командной строки, чтобы упростить автоматизацию.
- Во всех рабочих процессах actions обновлены до последних версий (спасибо @salmanmkc [#143](https://github.com/D4Vinci/Scrapling/pull/143)/[#144](https://github.com/D4Vinci/Scrapling/pull/144)).

## [v0.4](https://github.com/D4Vinci/Scrapling/releases/tag/v0.4) - 2026-02-15 {#v0.4}

**Крупнейший выпуск Scrapling: система пауков, ротация прокси и значительные улучшения парсера**

В этом выпуске появились полностью асинхронный фреймворк для обхода сайтов, умное управление прокси и важные изменения API. Они расширяют возможности Scrapling и делают его API единообразнее. Перед обновлением внимательно прочитайте раздел о несовместимых изменениях.

### 🕷️ Система пауков {#v0.4-spider-framework}

Новый асинхронный фреймворк на основе `anyio` для организованного сбора данных в больших объёмах:

```python
from scrapling.spiders import Spider, Response

class MySpider(Spider):
  name = "demo"
  start_urls = ["https://example.com/"]

  async def parse(self, response: Response):
      for item in response.css('.product'):
          yield {"title": item.css('h2::text').get()}

MySpider().start()
```

-  **API пауков в стиле Scrapy**: создавайте пауков с `start_urls`, асинхронными обработчиками `parse`, объектами `Request`/`Response` и очередью с приоритетами.
- **Одновременный обход**: настраиваемые ограничения числа одновременных запросов, ограничение скорости для каждого домена и задержки загрузки.
- **Поддержка нескольких сессий**: общий интерфейс для HTTP-запросов и скрытных браузеров в режиме без окна в одном пауке. Запросы направляются в разные сессии по ID. Сессии можно инициализировать только при необходимости.
- **Пауза и возобновление**: состояние обхода сохраняется в контрольных точках. Нажмите Ctrl+C для корректной остановки, затем запустите паука снова, чтобы продолжить с места остановки.
- **Потоковый режим**: получайте собранные записи по мере их поступления через `async for item in spider.stream()`, со статистикой в реальном времени. Подходит для интерфейсов, конвейеров обработки данных и длительного обхода.
- **Обнаружение заблокированных запросов**: автоматическое обнаружение и повторение заблокированных запросов с настраиваемой логикой.
- **Встроенный экспорт**: выгружайте результаты через хуки и собственный конвейер либо используйте встроенный экспорт в JSON/JSONL через `result.items.to_json()` / `result.items.to_jsonl()` соответственно.
- **Хуки жизненного цикла**: `on_start()`, `on_close()`, `on_error()`, `on_scraped_item()` и другие хуки позволяют полностью управлять жизненным циклом обхода.
- **Подробная статистика обхода**: запросы, ответы, байты, коды состояния, прокси, данные по доменам и сессиям, число записей каждого уровня логирования и многое другое.
- **Поддержка uvloop**: передайте `use_uvloop=True` в `spider.start()`, чтобы ускорить асинхронное выполнение, если uvloop доступен.

На сайте появился новый раздел с полной информацией. Откройте его [здесь](spiders/architecture.md).

### 🔄 Ротация прокси {#v0.4-proxy-rotation}

* Новый класс `ProxyRotator` с потокобезопасной сменой прокси. Работает со всеми Fetcher и сессиями:

  ```python
  from scrapling import ProxyRotator
  rotator = ProxyRotator(["http://proxy1:8080", "http://proxy2:8080"])
  Fetcher.get(url, proxy_rotator=rotator)
  ```

* **Свои стратегии ротации**: задайте собственную логику смены прокси.
* **Прокси для отдельного запроса**: передайте `proxy=` в отдельный вызов `get()`/`post()`/`fetch()`, чтобы заменить прокси сессии только для этого запроса.

### 🌐 Улучшения браузерных Fetcher {#v0.4-browser-fetcher-improvements}

* **Блокировка доменов**: новый параметр `blocked_domains` в `DynamicFetcher`/`StealthyFetcher` блокирует запросы к указанным доменам. Поддомены учитываются автоматически.
* **Автоматические повторные попытки**: браузерные Fetcher теперь повторяют запросы при ошибке. Это настраивается параметрами `retries` (по умолчанию: 3) и `retry_delay` (по умолчанию: 1s). Поддерживается обнаружение ошибок, связанных с прокси.
* **Метаданные ответа**: словарь `Response.meta` автоматически сохраняет использованный прокси и объединяет метаданные запроса.
* **Response.follow()**: создаёт объекты `Request` для следующих запросов с автоматической передачей Referer. Разработан для системы пауков.
* **Без автовоспроизведения**: браузерные сессии теперь блокируют автоматическое воспроизведение контента, которое раньше вызывало проблемы.
* **Скорость**: настройки флагов браузера улучшили скрытность и скорость.

### 🔧 Исправления ошибок и улучшения {#v0.4-bug-fixes-improvements}
- **Оптимизация парсера**: ускорены повторяющиеся операции парсера.
- **Ошибки страниц**: исправлена ошибка, из-за которой браузер не закрывался при ошибке на странице.
- **Пустое тело ответа**: добавлена обработка ответов с пустым телом.
- **Цикл событий Playwright**: решена проблема с незакрытым циклом событий Playwright при сбое подключения по CDP.
- **Безопасность типов**: исправлены все ошибки mypy и добавлены подсказки типов в тела функций без аннотаций. В рабочий процесс CI добавлены mypy и pyright.

### ⚠️ Несовместимые изменения {#v0.4-breaking-changes}

* **Удалены `css_first`/`xpath_first`**: используйте `css('.selector').first`, `css('.selector')[0]` или `css('.selector').get()`.
* **Все операции выбора теперь возвращают `Selectors`**: `css('::text')`, `xpath('//text()')`, `css('::attr(href)')` и `xpath('//@href')` теперь возвращают `Selectors`. Текстовые узлы оборачиваются в объекты `Selector` с `tag="#text"`, а не возвращаются как `TextHandlers`. Это делает API и подсказки типов единообразными для всех методов выбора.
* **`Response.body` всегда имеет тип `bytes`**: раньше это мог быть `str` или `bytes`, теперь всегда возвращается `bytes`.
* **Поведение `get()`/`getall()`**: у `Selector` метод `get()` возвращает `TextHandler` (сериализованный HTML или текстовое значение), а `getall()` возвращает `TextHandlers`. Псевдонимы: `extract_first = get`, `extract = getall`. Старый метод `get_all()` удалён из `Selectors`.
* **`Selectors.first`/`.last`**: безопасный доступ к элементам с возвратом `Selector | None` вместо ошибки `IndexError`.
* **Переименованы внутренние константы**: `DEFAULT_FLAGS` → `DEFAULT_ARGS`, `DEFAULT_STEALTH_FLAGS` → `STEALTH_ARGS`, `HARMFUL_DEFAULT_ARGS` → `HARMFUL_ARGS`, `DEFAULT_DISABLED_RESOURCES` → `EXTRA_RESOURCES`.

### 🔨 Прочие изменения {#v0.4-other-changes}

* **Изменения зависимостей**: `tldextract` заменён на `tld`, внутренний модуль `_html_utils.py` удалён в пользу `w3lib.html.replace_entities`, а `typing_extensions` стал обязательной зависимостью.
* **Полное обновление документации**: полный переход с MkDocs на Zensical, новый раздел о пауках, обновление всех существующих страниц и новые справочники API.

## [v0.3.14](https://github.com/D4Vinci/Scrapling/releases/tag/v0.3.14) - 2026-01-03 {#v0.3.14}

**Небольшое техническое обновление для исправления проблем v0.3.13 на некоторых устройствах**

- Режим инкогнито отключён в `StealthyFetcher` и его классах сессий, так как из-за него cookie не сохранялись между страницами на устройствах Windows. На MacOS и Linux этой проблемы не было (исправляет [#123](https://github.com/D4Vinci/Scrapling/issues/123), спасибо @frugality4121 за сообщение и @gembleman за решение).
- Закреплена последняя версия browserforge, чтобы решить проблему со старыми моделями заголовков у пользователей, у которых уже установлена старая версия browserforge.

## [v0.3.13](https://github.com/D4Vinci/Scrapling/releases/tag/v0.3.13) - 2026-01-01 {#v0.3.13}

**Это крупное обновление с улучшениями во многих частях библиотеки. Оно также содержит много необходимых несовместимых изменений. Прочитайте информацию ниже перед обновлением**

* По ряду причин мы решили полностью отказаться от Camoufox. В будущем мы можем вернуться к нему, если его разработка продолжится. Если вы хотите и дальше использовать Camoufox, как до этого выпуска, инструкции есть в этом [разделе](https://github.com/D4Vinci/Scrapling/blob/v0.3.13/docs/fetching/stealthy.md#using-camoufox-as-an-engine).

* Раньше мы использовали patchright в скрытном режиме `DynamicFetcher` и его классов сессий. Теперь мы убрали из них скрытный режим и стали использовать patchright в `StealthyFetcher` и его классах сессий. Как вы увидите ниже, мы внесли МНОГО улучшений и повысили общую скрытность поверх возможностей patchright.

**Благодаря этому `StealthyFetcher` и его классы сессий стали на 101 % быстрее, используют меньше памяти и места на диске, а код сократился примерно на 400 строк. Главное, они стабильнее, чем раньше, когда мы использовали Camoufox.**

Это также сократит время установки командой `scrapling install`, уменьшит Docker-образ, упростит выполнение тестов в GitHub CI и сделает Scrapling понятнее для новых пользователей.

### Несовместимые изменения {#v0.3.13-breaking-changes}
1. Аргумент `stealth` удалён из класса `DynamicFetcher` и его класса сессий, а `hide_canvas` перенесён в `StealthyFetcher` и его классы сессий.
2.  Аргумент `disable_webgl` перенесён из `DynamicFetcher` в класс `StealthyFetcher` и переименован в `allow_webgl`. Это касается и всех классов сессий.
3. Теперь класс `StealthyFetcher` по сути является новой скрытной версией `DynamicFetcher`, поэтому удалены аргументы `block_images`, `humanize`, `addons`, `os_randomize`, `disable_ads` и `geoip`. Я пытался воспроизвести их возможности в Chromium, но с каждой возникли свои проблемы. Это может измениться в следующих выпусках до v0.4.

Теперь о хорошем: мы многое улучшили и исправили :)

### Улучшения {#v0.3.13-improvements}
- Вы уже знаете, что класс `StealthyFetcher` и его классы сессий стали на 101 % быстрее. Теперь класс `DynamicFetcher` и его класс сессий тоже стали на 20 % быстрее.
- Алгоритм прохождения проверок Cloudflare улучшен: он быстрее завершает работу и обрабатывает больше ситуаций. Благодаря рефакторингу обработчик также проходит CAPTCHA вдвое быстрее!
- Все Fetcher теперь используют меньше памяти.
- MCP-сервер теперь использует меньше токенов и помогает экономить деньги!
- Docker-образ стал на 60 % меньше.
- Весь сайт документации обновлён с учётом новых возможностей. Объяснения стали яснее, многие разделы короче, добавлены примеры и недостающие аргументы, в справочнике API появились схемы. Есть и много других улучшений. Сайт загружается на 130 % быстрее, использует меньше трафика и лучше подходит для SEO.

### Исправления ошибок {#v0.3.13-fixes}
- В сокращённые команды оболочки для веб-скрейпинга добавлены недостающие аргументы, а сами команды стали точнее.
- Исправлена проблема, из-за которой `google_search` создавал Referer Google даже для URL с localhost или IP-адресом.

## [v0.3.12](https://github.com/D4Vinci/Scrapling/releases/tag/v0.3.12) - 2025-12-18 {#v0.3.12}

### Что изменилось {#v0.3.12-what-s-changed}
- В классы `DynamicSession`/`AsyncDynamicSession` добавлен аргумент `timezone_id`. Он позволяет настроить часовой пояс браузера под используемый прокси или VPN. Так сайты не смогут обнаружить прокси по несовпадению часовых поясов.
- Улучшено автоматическое преобразование ответа в JSON.
- В классах сессий Fetcher внутренняя функция `__create__` переименована в `start`, чтобы было проще использовать их вне контекста `with`.
- `curl_cffi` и другие зависимости обновлены до последних версий.

## [v0.3.11](https://github.com/D4Vinci/Scrapling/releases/tag/v0.3.11) - 2025-12-03 {#v0.3.11}

### Что изменилось {#v0.3.11-what-s-changed}
- Улучшена обработка тайм-аутов при использовании `network_idle` на нестабильном сайте, например на сайте с воспроизведением медиа.
- Исправлено автодополнение сокращённой команды `stealthy_fetch` в оболочке для веб-скрейпинга.

## [v0.3.10](https://github.com/D4Vinci/Scrapling/releases/tag/v0.3.10) - 2025-11-26 {#v0.3.10}

**Техническое обновление с важными и потенциально несовместимыми изменениями**

- **Решены** все проблемы с кодировками благодаря новому подходу, который обрабатывает страницы с неверно объявленной кодировкой (спасибо @Kemsty2 за сообщения в [#110](https://github.com/D4Vinci/Scrapling/issues/110) [#111](https://github.com/D4Vinci/Scrapling/pull/111)).
- **Решена** логическая проблема с переопределением параметров сессии параметрами отдельного запроса во всех браузерных Fetcher. Она существовала с v0.3.
- **Исправлены** сигнатуры сокращённых команд интерактивной оболочки для веб-скрейпинга. Теперь автодополнение этих команд работает правильно. Эта проблема тоже существовала с v0.3.
- **Обновлена** версия базы Maxmind, что улучшает работу аргумента `geoip` в `StealthyFetcher` и его классах сессий.
- **Обновлены** все используемые браузеры до последних доступных версий.
- **НЕСОВМЕСТИМЫЕ ИЗМЕНЕНИЯ**: все Fetcher прошли большой рефакторинг, который привёл к изменениям, способным нарушить работу вашего кода:
    1. Код Scrapling сократился примерно на 750 строк. Многие изменения упростят дальнейшую поддержку и немного снизят расход ресурсов.
    2. Проверка аргументов во всех Fetcher и их классах сессий стала намного быстрее, что ускорит и работу в целом.
    3. Для этого теперь все Fetcher принимают как позиционный аргумент только `url`. Остальные аргументы должны быть именованными. Нужно писать `Fetcher.get('https://google.com', stealthy_headers=True)`, а не `Fetcher.get('https://google.com', True)`, если вы по какой-то причине делали это раньше!
    4. С v0.3 у браузерных Fetcher и их классов сессий было неудобное различие: аргумент для передачи настроек парсера на уровне запроса назывался `custom_config`, а в классах сессий он назывался `selector_config`. Рефакторинг позволил привести название к `selector_config`, не нарушая работу вашего кода. Теперь основной аргумент называется `selector_config`, а `custom_config` всё ещё работает для обратной совместимости. Автодополнение будет доступно только для `selector_config`.
    5. Для всех этих изменений пришлось сделать подсказки типов функций Fetcher динамическими. Если IDE не предлагает правильное автодополнение, убедитесь, что у вас современная версия. Мы проверили почти все известные IDE и редакторы.

> Мы также обновили все таблицы тестов производительности, сравнив текущие результаты с последними версиями всех аналогичных библиотек.

## [v0.3.9](https://github.com/D4Vinci/Scrapling/releases/tag/v0.3.9) - 2025-11-17 {#v0.3.9}

**Обновление со многими важными изменениями**

### 🚀 Новые возможности и улучшения удобства {#v0.3.9-new-stuff-and-quality-of-life-changes}
- Теперь аргумент `impersonate` в `Fetcher` и `FetcherSession` принимает список браузеров. Для каждого запроса библиотека случайным образом выбирает браузер из этого списка.

```python
from scrapling.fetchers import FetcherSession

with FetcherSession(impersonate=['chrome', 'firefox', 'safari']) as s:
  s.get('https://github.com/D4Vinci/Scrapling')
```

- В метод `clean` класса `TextHandler` добавлен аргумент, который позволяет легко удалять HTML-сущности из текущего текста.
- Значительно улучшена документация: многие части объяснены точнее, добавлены автоматические переводы основного файла `README.md`.

### 🐛 Исправления ошибок {#v0.3.9-bug-fixes}
- Исправлена серьёзная проблема с получением ответов из браузерных Fetcher. Теперь тип содержимого определяется автоматически: `response.body` содержит результат отрисовки браузером только для HTML. В остальных случаях возвращается исходное содержимое последнего запроса. Это позволяет скачивать двоичные и текстовые файлы без оборачивания в HTML-теги, а при загрузке сайта получать нужное содержимое после отрисовки.

### 🔨 Прочее {#v0.3.9-misc}
- Руководство для участников обновлено и стало понятнее и проще.
- Добавлен рабочий процесс, который обязательно запускает инструменты контроля качества кода (те же, что используются в хуках pre-commit).

## [v0.3.8](https://github.com/D4Vinci/Scrapling/releases/tag/v0.3.8) - 2025-10-27 {#v0.3.8}

**Обновление со многими важными изменениями**

### 🚀 Новые возможности и улучшения удобства {#v0.3.8-new-stuff-and-quality-of-life-changes}
- Во всех браузерных Fetcher использование `network_idle` больше не приводит к сбою кода на сайтах, запросы которых никогда не завершаются.
- Изменена логика получения и проверки содержимого страниц в браузерных Fetcher. Теперь браузеры стабильнее работают на Windows, как и на Linux/MacOS (разница в поведении вызвана отличиями реализации Playwright на Windows).
- Вся логика проверки аргументов переработана, что ускорило запросы во всех браузерных Fetcher на 8-15 %.
- Новый параметр `extra_flags` добавлен в `DynamicFetcher` и его сессию. Он позволяет при запуске браузера добавлять свои флаги Chrome к уже заданным.
- При использовании `page_action` восстановлена прежняя логика перехвата ответов, изменённая в прошлой версии. Это позволяет получить актуальное содержимое страницы, даже если `page_action` меняет его без отправки запроса (спасибо @gembleman за сообщения в [#100](https://github.com/D4Vinci/Scrapling/issues/100) и [#102](https://github.com/D4Vinci/Scrapling/pull/102)).

### 🐛 Исправления ошибок {#v0.3.8-bug-fixes}
- Исправлена опечатка в `load_dom` в методе async_fetch класса DynamicSession.
- Исправлена проблема с обработчиком Cloudflare, который бесконечно ждал исчезновения встроенных CAPTCHA, остающихся на странице после прохождения. Теперь ожидание длится 30 секунд, после чего обработчик считает, что это CAPTCHA, которая не исчезает (исправляет #100).

### 🔨 Прочее {#v0.3.8-misc}
- Для удобства пользователей Docker-образ теперь автоматически публикуется в Dockerhub и реестре контейнеров GitHub.
- Добавлена [новая страница документации](https://github.com/D4Vinci/Scrapling/blob/v0.3.8/docs/tutorials/external.md) о работе со Scrapeless Browser в Scrapling.

## [v0.3.7](https://github.com/D4Vinci/Scrapling/releases/tag/v0.3.7) - 2025-10-12 {#v0.3.7}

**Обновление со многими важными изменениями**

### 🚀 Новые возможности и улучшения удобства {#v0.3.7-new-stuff-and-quality-of-life-changes}
- Переработан аргумент `solve_cloudflare` в `StealthyFetcher`, чтобы проходить все виды нестандартных реализаций Turnstile.
- Весь код переработан для успешной проверки Pyright. Теперь работать во всех IDE стало удобнее. Также исправлено много ошибок.
- Логика запросов стала проще и быстрее (также решает #97).
- Во все браузерные классы сессий добавлен параметр `user_data_dir`, позволяющий повторно использовать данные браузера из прошлых сессий: cookie, хранилище и другое. Если его не задать, Playwright, как и прежде, будет использовать случайный каталог при каждом запуске.
- Новый параметр `additional_args` добавлен в `Dynamic fetcher` и его класс сессий. Он позволяет передавать дополнительные аргументы в контекст Playwright, как раньше можно было делать в `StealthyFetcher`.
- Улучшена логика получения последнего ответа при навигации во всех браузерах. Теперь исходный ответ передаётся в парсер до обработки браузером, а не после неё, как раньше. Это особенно полезно для текстовых и JSON-ответов.

### 🐛 Исправления ошибок {#v0.3.7-bug-fixes}
- Переработка логики перехвата ответов решила проблему с получением содержимого нестабильных сайтов на некоторых устройствах Windows.
- Рефакторинг в этой версии также исправил много ошибок, которые раньше было трудно заметить, и странные проблемы с автодополнением в некоторых IDE.
- Много исправлений на сайте документации.

## [v0.3.6](https://github.com/D4Vinci/Scrapling/releases/tag/v0.3.6) - 2025-10-01 {#v0.3.6}

### 🚀 Новые возможности {#v0.3.6-new-stuff}
- Улучшен аргумент `solve_cloudflare` в `StealthyFetcher` и его классах сессий. Теперь он позволяет проходить все виды Turnstile и промежуточных проверок Cloudflare 🎉
- MCP-сервер теперь поддерживает `Streamable HTTP`, что позволяет легко открыть к нему доступ извне.
- Добавлена поддержка Docker. При каждом выпуске образ автоматически собирается и публикуется в Docker Hub (содержит все браузеры).

### 🐛 Исправления ошибок {#v0.3.6-bug-fixes}
- Исправлена возникавшая в некоторых случаях проблема с кодировкой в парсере (известная ошибка `invalid start byte`).
- Переработано несколько частей библиотеки для исправления утечек памяти. Теперь расход памяти заметно ниже, в зависимости от настроек (также решает #92).
- Улучшены аннотации типов во многих частях кода для более удобной работы в IDE (также решает #93).

## [v0.3.5](https://github.com/D4Vinci/Scrapling/releases/tag/v0.3.5) - 2025-09-20 {#v0.3.5}

**Важный выпуск с исправлениями нескольких проблем**

### 🚀 Новые возможности {#v0.3.5-new-stuff}
- Все браузерные Fetcher (`DynamicFetcher`/`StealthyFetcher`/...) и их классы сессий теперь загружают сайты на 15-20 % быстрее:
    1. Управление страницами стало намного быстрее благодаря улучшению логики от @AbdullahY36 в #87.
    2. Оптимизирована проверка аргументов и улучшено создание страниц для синхронных запросов. Вместе это заметно повысило скорость.

- Значительно улучшен скрытный режим в `DynamicFetcher` и его классах сессий за счёт замены `rebrowser-playwright` на `PatchRight`:
    1. До этого обновления `rebrowser-playwright` отключался при одновременном включении `stealth` и `real_chrome`, так как они плохо работали вместе. С `PatchRight` этой проблемы нет.
    2. Теперь можно взаимодействовать с закрытыми Shadow Root, так как `PatchRight` обрабатывает их автоматически.

### 🐛 Исправления ошибок {#v0.3.5-bug-fixes}
- Исправлена ошибка при использовании метода `re` класса `Selectors`.
- Исправлена ошибка команд `uncurl` и `curl2fetcher` в оболочке для веб-скрейпинга, из-за которой флаг curl `--data-raw` разбирался неверно.
- Исправлена ошибка команды `view` в оболочке для веб-скрейпинга, которая возникала при определённой кодировке сайта.
- Исправлена ошибка преобразования содержимого, затрагивавшая режим `mcp` и команды `extract`.

### Новые участники {#v0.3.5-new-contributors}
- @AbdullahY36 впервые внёс вклад в проект в #87.

## [v0.3.4](https://github.com/D4Vinci/Scrapling/releases/tag/v0.3.4) - 2025-09-16 {#v0.3.4}

**Важный выпуск с исправлениями нескольких проблем**

### 🚀 Новые возможности {#v0.3.4-new-stuff}
- В интерактивную оболочку добавлены все классы сессий Fetcher. Их можно использовать сразу, без импорта.

### 🐛 Исправления ошибок {#v0.3.4-bug-fixes}
- Добавлен обход ошибки Playwright API на Windows, которая возникала при получении содержимого во время прохождения проверки Cloudflare.
- Исправлена проблема с кодировкой команды `view` в интерактивной оболочке.
- Исправлена ошибка аргумента `max_pages` в `AsyncStealthySession`, приводившая к сбою кода.
- Исправлена проблема последних обновлений: свойства `html_content` и `prettify` класса `Selector` могли возвращать байты в зависимости от кодировки. Теперь оба снова возвращают строки.

## [v0.3.3](https://github.com/D4Vinci/Scrapling/releases/tag/v0.3.3) - 2025-09-15 {#v0.3.3}

- Удалена логика закрытия стандартной вкладки в браузерных Fetcher, так как она приводила к сбою (на Mac сбоя не было, его удалось воспроизвести только на Windows и Linux).

## [v0.3.2](https://github.com/D4Vinci/Scrapling/releases/tag/v0.3.2) - 2025-09-15 {#v0.3.2}

Примечания к выпуску v0.3.2

### 🚀 Новые возможности {#v0.3.2-new-stuff}

- **Необязательные зависимости Fetcher**: все Fetcher теперь входят в группы дополнительных зависимостей, что уменьшает размер основного пакета. Базовый модуль `scrapling` содержит только парсер. Для Fetcher или командной строки выполните `pip install "scrapling[fetchers]"`. Подробные инструкции по установке доступны [здесь](index.md#installation).
- **Настройки для отдельных страниц в сессии**: классы сессий браузерных Fetcher теперь позволяют настраивать каждую страницу отдельно. Все параметры получения страницы проверяются так же, как параметры сессии. Подробнее на сайте документации [здесь](fetching/stealthy.md#full-list-of-arguments).
    <br>Пример:

    ```python
    with StealthySession(headless=True, solve_cloudflare=True) as session:
        page = session.fetch('https://nopecha.com/demo/cloudflare', google_search=False)
    ```

- **Улучшения браузерных Fetcher**
    - Новый параметр определяет, нужно ли ждать завершения JavaScript на странице (по умолчанию включён, как и раньше).

        ```python
        with DynamicSession(headless=True, disable_resources=False, network_idle=True) as session:
           page = session.fetch('https://quotes.toscrape.com/', load_dom=False)
        ```

    - Скрытный режим в `DynamicFetcher` и его классах сессий стал надёжнее.
    - `DynamicFetcher` и `StealthyFetcher` теперь используют меньше ресурсов (автоматически находят и закрывают стандартную вкладку, которую открывает постоянный контекст Playwright API).
    - Исправлена важная ошибка переключения страниц в браузерных Fetcher: старые страницы теперь заменяются новыми. (В повторно используемых вкладках могут оставаться прежние настройки.)
    - `StealthyFetcher` и его классы сессий стали немного быстрее (5 %).

- **Улучшено свойство `.body`**: теперь оно возвращает переданное содержимое как есть, без обработки. Это позволяет скачивать файлы и обрабатывать запросы с содержимым, отличным от HTML. Ниже показан пример скачивания фотографии:

    ```python
    from scrapling.fetchers import Fetcher

    page = Fetcher.get('https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/poster.png')
    with open(file='poster.png', mode='wb') as f:
        f.write(page.body)
    ```

### 🐛 Исправления ошибок {#v0.3.2-bug-fixes}

- **Решены проблемы с кодировками**: исправлено несколько проблем с кодировками на отдельных сайтах в парсере, режиме mcp и командах extract (также решает #80 и #81).
- **Ускорен разбор**: благодаря многочисленным изменениям библиотека стала быстрее, что видно в обновлённых тестах производительности.

### 🔨 Прочее {#v0.3.2-misc}

- **Обновлены тесты производительности**: текущие улучшения скорости сравниваются с последними версиями похожих библиотек.
- **Многие части кода переработаны, а неиспользуемый код заменён лучшими реализациями**: кода меньше, он понятнее и проще в поддержке.
- **Добавлено видео на YouTube**: в документацию MCP добавлено видео.
- **Новый шаблон обращений**: простой шаблон для пользователей, которые не могут использовать существующие.
- **Оптимизация рабочего процесса CI**: тесты теперь не запускаются, если изменились только документация или другие файлы, не содержащие код.
- **Обновлены зависимости**: различные зависимости обновлены до последних версий.
- **Улучшения стиля кода**: новые правила ruff применены ко всем файлам.
- **Хуки pre-commit**: обновлена конфигурация pre-commit.

### 🎯 Несовместимые изменения {#v0.3.2-breaking-changes}

- Параметр `max_pages` удалён из синхронной версии `StealthySession` для соответствия `DynamicSession` (в синхронной версии он не имеет смысла).

## [v0.3.1](https://github.com/D4Vinci/Scrapling/releases/tag/v0.3.1) - 2025-09-02 {#v0.3.1}

1. Исправлена проблема установки Scrapling без набора зависимостей `shell` (#76).
2. Во все браузерные Fetcher и их классы сессий добавлен аргумент для указания JS-файла, который выполняется при создании страницы (#56):

```python
from scrapling.fetchers import StealthyFetcher

StealthyFetcher.fetch('https://example.com', init_script="/absolute/path/to/js/script.js")
```

## [v0.3](https://github.com/D4Vinci/Scrapling/releases/tag/v0.3) - 2025-09-01 {#v0.3}

🎉 **Крупный выпуск: полностью новая архитектура**

Scrapling v0.3 стал самым значительным обновлением за всю историю проекта. Архитектура полностью переписана, производительность заметно выросла, а среди новых возможностей появились интеграция с ИИ и интерактивная оболочка для сбора данных с сайтов.

Этот выпуск содержит несколько несовместимых изменений. Внимательно прочитайте примечания к выпуску.

### 🚀 Главные новые возможности {#v0.3-major-new-features}

#### Архитектура на основе сессий {#v0.3-session-based-architecture}
- **Новые классы сессий**: код полностью переписан, добавлена поддержка постоянных сессий.
    - `FetcherSession`: HTTP-запросы с сохранением состояния. Работает как с синхронным, так и с асинхронным кодом.
    - `DynamicSession`/`AsyncDynamicSession`: автоматизация браузера, который остаётся открытым до завершения вашей работы.
    - `StealthySession`/`AsyncStealthySession`: скрытная работа в браузере, который остаётся открытым до завершения вашей работы.
- **Асинхронное управление вкладками**: новый аргумент `max_pages` создаёт пул вкладок, которые используются по очереди для одновременной загрузки страниц через браузер.
- **Одновременные сессии**: запускайте несколько изолированных сессий одновременно.

Подробнее читайте в разделе `Fetching` на сайте.

#### Много новых возможностей скрытной работы и обхода защиты от ботов {#v0.3-a-lot-of-new-stealth-anti-bot-capabilities}
- **🤖 Прохождение проверок Cloudflare**: автоматическое [прохождение проверок Cloudflare Turnstile](fetching/stealthy.md#cloudflare-and-stealth-options) в `StealthyFetcher` и его классах сессий.
- **Имитация отпечатков браузера**: полностью обновлённый класс [Fetcher](fetching/static.md) имитирует TLS-отпечатки настоящих браузеров, создаёт заголовки для нужной версии браузера, поддерживает HTTP/3 и многое другое.
- **Улучшенный скрытный режим**: скрытный режим в `DynamicFetcher` и его классах сессий стал надёжнее и стабильнее (другое название класса: `PlayWrightFetcher`).

#### Интеграция с ИИ и MCP-сервер {#v0.3-ai-integration-mcp-server}
- **Встроенный MCP-сервер**: сервер Model Context Protocol для сбора данных с помощью ИИ.
- **6 мощных инструментов**: `get`, `bulk_get`, `fetch`, `bulk_fetch`, `stealthy_fetch`, `bulk_stealthy_fetch`.
- **Умное извлечение содержимого**: преобразуйте страницы и элементы в Markdown или HTML либо извлекайте очищенный текст.
- **Поддержка CSS-селекторов**: точно выбирайте нужные элементы с помощью движка Scrapling перед передачей содержимого ИИ.
- **Обход защиты от ботов**: проходите Cloudflare Turnstile и другие проверки.
- **Поддержка прокси**: используйте прокси для анонимности и запросов из нужных регионов.
- **Имитация браузера**: воспроизводите TLS-отпечатки, настоящие заголовки для нужной версии браузера и другие признаки.
- **Параллельная обработка**: собирайте данные с нескольких URL одновременно для большей эффективности.
- [И многое другое...](ai/mcp-server.md)

#### Новая интерактивная оболочка для сбора данных {#v0.3-new-interactive-web-scraping-shell}
- **Новая оболочка**: доработанная оболочка IPython со множеством удобных встроенных сокращений, таких как `get`, `post`, `put`, `delete`, `fetch` и `stealthy_fetch`.
- **Умное управление страницами**: новые команды `page` и `pages` автоматически сохраняют текущую страницу и историю всех запросов из оболочки.
- **Интеграция с curl**: функции `uncurl` и `curl2fetcher` преобразуют команды curl из DevTools браузера в запросы `Fetcher`.
- [И многое другое...](cli/interactive-shell.md)

#### Сбор данных из терминала без программирования {#v0.3-scrape-from-the-terminal-without-programming}
- **Новые команды извлечения**: собирайте данные из терминала без программирования.
    - `scrapling extract get/post/put/delete`: простые HTTP-запросы.
    - `scrapling extract fetch`: сбор динамического содержимого.
    - `scrapling extract stealthy-fetch`: обход защиты от ботов.
- **Загружает веб-страницы** и сохраняет их содержимое в файлы.
- **Преобразует HTML в удобные для чтения форматы**, например Markdown, сохраняет его как HTML или извлекает только текст страницы.
- **Поддерживает собственные CSS-селекторы** для извлечения отдельных частей страницы.
- **Выполняет HTTP-запросы и загружает страницы через браузер.**
- **Гибко настраивается**: можно задать заголовки, cookie, прокси и другие параметры. Почти все опции, доступные в коде, можно использовать и в терминале.
- [И многое другое...](cli/extract-commands.md)

### 🔧 Технические улучшения {#v0.3-technical-improvements}

#### Улучшения производительности {#v0.3-performance-enhancements}
- **Fetcher теперь в 4 раза быстрее**. Да, вы всё правильно прочитали!
- **DynamicFetcher теперь примерно на 60 % быстрее**. Прирост зависит от настроек, особенно от скрытного режима.
- **StealthyFetcher теперь на 20–30 % быстрее** благодаря новой структуре и началу перехода на нашу реализацию вместо Python-интерфейса `Camoufox`.
- **Общий прирост скорости основных методов выборки составляет 50 % и более** (`find_by_text`, `find_similar`, `find_by_regex`, `relocate` и других). 🚀
- **Методы CSS/XPath для первого совпадения стали примерно на 10 % быстрее**. `css_first` и `xpath_first` теперь быстрее, чем `css` и `xpath`.
- **Метод `get_all_text()` для извлечения содержимого стал на 40 % быстрее**.
- **Адаптивный повторный поиск элементов стал на 20 % быстрее**.
- **Оптимизированы свойства для перехода между элементами**. `next`, `previous`, `below_elements` и другие свойства теперь работают заметно быстрее.
- **Очистка текста стала в 5 раз быстрее**.
- **Улучшено использование памяти** за счёт оптимизации импорта и уменьшения накладных расходов.
- **⚡ Мгновенный импорт**: оптимизация загрузки модулей сократила время запуска.
- **Лучшие результаты тестов производительности**: все эти изменения сделали Scrapling ещё быстрее по сравнению с другими библиотеками. Он в 1775 раз быстрее BeautifulSoup и в 5,1 раза быстрее AutoScraper, см. [тесты производительности](benchmarks.md).

#### Архитектура, качество кода и удобство {#v0.3-architecture-code-quality-and-quality-of-life}
- **Постоянный контекст**: все браузерные Fetcher теперь по умолчанию используют постоянный контекст. (Это также решает #64.)
- **Быстрая проверка всех браузерных Fetcher через msgspec** перед выполнением запросов упрощает поиск ошибок.
- **Все cookie**, возвращаемые Fetcher, теперь имеют формат, который принимает этот же Fetcher. Их можно получать и снова передавать всем Fetcher и их классам сессий.
- **Более быстрые проверка и форматирование кода** благодаря переходу на `ruff`.
- **Современная система сборки**: переход с setup.py на pyproject.toml. 📦
- **Улучшенные GitHub Actions и рабочие процессы** упрощают разработку и тестирование.
- **🎨 Улучшенные подсказки типов**: полное покрытие типов по современным стандартам Python для лучшей поддержки в IDE и большей надёжности.
- **Более чистый код**: удалён неиспользуемый код и оптимизированы основные функции. 🧹
- **🚀 Обратная совместимость**: добавлены сокращения, чтобы старый код продолжал работать.

### Несовместимые изменения {#v0.3-breaking-changes}

#### Минимальная версия Python {#v0.3-minimum-python-version}
- **Требуется Python 3.10+**: поддержка Python 3.9 и более ранних версий прекращена.

#### Названия классов и методов {#v0.3-class-and-method-naming}
Эти переименования делают названия понятнее и единообразнее, особенно для новых пользователей.

- **`Adaptor` → `Selector`**: переименован основной класс парсера (для обратной совместимости его по-прежнему можно импортировать как `Adaptor`).
- **`Adaptors` → `Selectors`**: переименован класс коллекции (для обратной совместимости его по-прежнему можно импортировать как `Adaptors`).
- **`auto_match` → `adaptive`**: параметр переименован во всех методах.
- **`adaptor_arguments` → `selector_config`**: переименован параметр конфигурации.
- **`automatch_domain` → `adaptive_domain`**: переименован параметр домена.
- **`additional_arguments` → `additional_args`**: сокращено имя параметра.
- **⚠️ `text/body` → `content`**: параметр конструктора Selector теперь принимает и `str`, и `bytes`.
- **`PlayWrightFetcher` → `DynamicFetcher`**: переименован класс автоматизации браузера (для обратной совместимости его по-прежнему можно импортировать как `PlayWrightFetcher`).
- **Из DynamicFetcher удалены логика и аргументы NSTBrowser**, поскольку сохранять их больше нет смысла.
- **Аргумент headless в StealthyFetcher больше не принимает 'virtual'**, поскольку библиотека Camoufox теперь используется только для получения пути установки браузера и остальных параметров запуска.

### 🐛 Исправления ошибок {#v0.3-bug-fixes}

- Исправлен подсчёт вложенных дочерних элементов в игнорируемых тегах для `get_all_text` (#61).
- Исправлена проблема установки из-за пробелов в пути к исполняемому файлу Python (#57).
- Исправлены проблемы с потоками в хранилище при обработке рекурсии с включённой адаптивной функцией.
- Исправлены проблемы с приоритетом аргументов в `FetcherSession` с помощью шаблона Sentinel.
- Исправлена обработка типов прокси в `StealthyFetcher`.
- Исправлены конфликты аргументов `referer` и `google_search`.
- Исправлены проблемы с асинхронным внедрением скриптов для скрытной работы.

## [v0.2.99](https://github.com/D4Vinci/Scrapling/releases/tag/v0.2.99) - 2025-04-08 {#v0.2.99}

**Это важное обновление для всех, кто хочет использовать Scrapling в полной мере.**

### Что изменилось {#v0.2.99-what-s-changed}
#### Новый сайт с полной документацией {#v0.2.99-new-full-documentation-website}
- Да, наконец-то 😄 Посмотрите [здесь](index.md).
#### Единый способ импорта Fetcher {#v0.2.99-unified-import-logic-for-fetchers}
- Теперь все Fetcher можно импортировать через `from scrapling.fetchers import Fetcher, AsyncFetcher, StealthyFetcher, PlayWrightFetcher` и сразу использовать без инициализации, например `page = Fetcher.get(...)`.<br/> Это заменяет старый импорт `from scrapling.defaults import Fetcher, AsyncFetcher, StealthyFetcher, PlayWrightFetcher`.
#### Несовместимое изменение: automatch теперь выключен по умолчанию {#v0.2.99-breaking-change-automatch-is-now-turned-off-by-default}
- Появился новый способ включить automatch и задать другие параметры парсера через Fetcher. Подробности смотрите на [странице документации](fetching/choosing.md#parser-configuration-in-all-fetchers).
>  Старые импорты и логика по-прежнему работают для обратной совместимости, но выдают предупреждение.
#### Новые опции Fetcher {#v0.2.99-new-options-added-to-fetchers}
- У `StealthyFetcher` и `PlayWrightFetcher` появился аргумент `wait` для загрузки страниц. Он заставляет Fetcher подождать указанное время в миллисекундах перед закрытием страницы и возвратом ответа.
- В `StealthyFetcher` методы `fetch` и `async_fetch` теперь принимают `additional_arguments` для передачи дополнительных настроек в Camoufox. Они имеют приоритет над настройками Scrapling (#54).
#### Исправления ошибок {#v0.2.99-bugs-squashed}
- Исправлена ошибка получения перенаправлений в `async_fetch` обоих классов: `StealthyFetcher` и `PlayWrightFetcher`.

**_Спасибо за всю вашу поддержку и пожертвования!_**

## [v0.2.98](https://github.com/D4Vinci/Scrapling/releases/tag/v0.2.98) - 2025-03-17 {#v0.2.98}

**Это важное обновление для всех, кто хочет использовать Scrapling в полной мере**

### Что изменилось {#v0.2.98-what-s-changed}
#### Разные улучшения использования памяти и скорости {#v0.2.98-various-memory-usage-and-speed-optimizations}
- Все методы выборки теперь используют около 40 % прежнего объёма памяти и работают немного быстрее.
- Для всех подмодулей библиотеки добавлена отложенная загрузка: загружается только то, что вы используете. Например:
До обновления импорт `from scrapling import Adaptor` занимал `30-40mb` оперативной памяти, поскольку вместе с ним загружались все Fetcher и другие модули. Теперь он занимает `~1.2mb`.
- В прошлом обновлении при большом пуле запросов библиотека стала использовать около 32 % прежнего объёма памяти. Теперь кеширование настроено ещё точнее, чтобы расходовать ещё меньше.
- Скорость парсера в целом выросла на 2-5 %.

**_Спасибо за всю вашу поддержку и пожертвования!_**

## [v0.2.97](https://github.com/D4Vinci/Scrapling/releases/tag/v0.2.97) - 2025-03-15 {#v0.2.97}

**Это важное обновление для всех, кто хочет использовать Scrapling в полной мере**

### Что изменилось {#v0.2.97-what-s-changed}
#### Меньше памяти и немного больше скорости у всех Fetcher {#v0.2.97-lower-memory-usage-and-small-speed-increase-across-all-fetchers}
- Новые ограничения размера кеша во всей библиотеке заметно снижают расход памяти при большом числе запросов или операций.
- Значительная часть кода Fetcher переработана, чтобы упростить поддержку и немного ускорить работу.

#### Исправления ошибок {#v0.2.97-bugs-fixed}
- Исправлена ошибка `TextHandler`: при отдельном импорте класса переданный нестроковый аргумент превращался в пустую строку. Теперь любое значение для `TextHandler` сначала преобразуется в строку и только потом в `TextHandler`. Это правило действует для всех значений. Как следует из названия, `TextHandler` предназначен именно для строк! (#45)
- Исправлена ошибка, из-за которой большинство методов AsyncFetcher не учитывало аргументы `retries`.

#### Прочее {#v0.2.97-miscellaneous}
- Подсказки типов для большинства аргументов всех Fetcher стали понятнее и точнее.

**_Спасибо за всю вашу поддержку и пожертвования!_**

## [v0.2.96](https://github.com/D4Vinci/Scrapling/releases/tag/v0.2.96) - 2025-03-05 {#v0.2.96}

**Это важное обновление для всех, кто хочет использовать Scrapling в полной мере**

### Что изменилось {#v0.2.96-what-s-changed}
1. Добавлена опция `-f` для `scrapling install`, которая принудительно переустанавливает зависимости браузера. Рекомендую выполнить `scrapling install -f`, чтобы оценить значительное ускорение `StealthyFetcher` с новой версией браузера Camoufox :)
2. Исправлена ошибка `TextHandler`, когда срез возвращал `TextHandlers` вместо `TextHandler`. Также исправлена подсказка типа (#41).
3. Исправлена проблема, из-за которой `scrapling install` в некоторых случаях открывал пользователю оболочку Python!

## [v0.2.95](https://github.com/D4Vinci/Scrapling/releases/tag/v0.2.95) - 2025-02-25 {#v0.2.95}

**Это важное обновление для всех, кто хочет использовать Scrapling в полной мере**

### Что изменилось {#v0.2.95-what-s-changed}
1. Исправлена ошибка `Fetcher`, при которой заголовки от аргумента `stealthy_headers` перезаписывали некоторые заголовки пользователя, например `Accept` (#39).
2. Немного улучшена генерация заголовков, что должно слегка повысить скорость.

## [v0.2.94](https://github.com/D4Vinci/Scrapling/releases/tag/v0.2.94) - 2025-02-22 {#v0.2.94}

**Это важное обновление для всех, кто хочет использовать Scrapling в полной мере**

### Что изменилось {#v0.2.94-what-s-changed}
1. Во все Fetcher добавлено свойство `history` для просмотра перенаправлений (#32).
2. Исправлена логика аргумента `case_sensitive` во всех `re`/`re_first`. Если вы его использовали, код может начать возвращать другие результаты (но, возможно, вы это заслужили, если заметили проблему и не сообщили о ней в issue, ха-ха).
3. Обновлены зависимости, а в движке Camoufox (StealthyFetcher) снова включён `coop`.

## [v0.2.93](https://github.com/D4Vinci/Scrapling/releases/tag/v0.2.93) - 2025-01-31 {#v0.2.93}

**Это важное обновление для всех, кто хочет использовать Scrapling в полной мере**

### Что изменилось {#v0.2.93-what-s-changed}
1. Типы возвращаемых значений теперь единообразны во всём парсере. Результат всегда имеет один из типов: `Adaptor`, `Adaptors`, `TextHandler`, `TextHandlers`, `None`, либо список при смешанных результатах, например при объединении CSS-селекторов. Это упрощает код, сокращает ручные проверки типов, повышает стабильность библиотеки и всегда позволяет объединять вызовы методов в цепочку.
2. Большая часть парсера, особенно класс `Adaptor`, переработана: код стал чище и, главное, быстрее. Почти все методы и свойства, особенно методы поиска, ускорились на 5-40 %. Некоторые стали ещё быстрее: например, `find_by_regex` ускорился примерно на 60 %! Функция automatch стала примерно на 5 % быстрее.
3. Исправлены ошибки логики `find_all`/`find`, из-за которых переданные фильтры иногда объединялись через ИЛИ, а иногда через И. Теперь каждый возвращаемый элемент должен соответствовать всем фильтрам.
4. Все методы, связанные с регулярными выражениями, теперь возвращают `TextHandler`/`TextHandlers`, чтобы вызовы было проще объединять в цепочки.
5. **Добавлено новое** свойство `below_elements`, которое возвращает объект `Adaptors` со всеми элементами ниже текущего в дереве DOM.
6. Все методы и свойства, которые возвращали исходный HTML в виде строки, теперь возвращают `TextHandler`. Это упрощает работу с регулярными выражениями и другими возможностями.
7. StealthyFetcher стал немного быстрее и менее заметным. Также теперь можно нажимать на CAPTCHA внутри iframe, например на **Cloudflare Turnstile**.
8. Автодополнение и подсказки типов заметно улучшены почти в половине библиотеки, особенно в `Adaptor`, `TextHandler` и `TextHandlers`.
9. Для объекта `TextHandler` срезы, обращение по индексу и метод `split` теперь возвращают другой `TextHandler`, а не обычную строку Python. Почти все стандартные строковые операции и методы теперь возвращают `Texthandler`, чтобы всегда можно было объединять вызовы методов и функций в цепочки.
10. Исправлены мелкие ошибки и опечатки. Например, Fetcher async_put отправлял POST-запрос вместо PUT 😶‍🌫️
11. Немного улучшен README, пока я заканчиваю сайт с документацией.

Это должно было быть небольшое обновление до версии 0.3, но я решил сделать его лучше.

## [v0.2.92](https://github.com/D4Vinci/Scrapling/releases/tag/v0.2.92) - 2024-12-26 {#v0.2.92}

### Что изменилось {#v0.2.92-what-s-changed}
- Ответы браузерных Fetcher теперь используют более надёжные источники данных, если загруженная страница содержит много iframe.
- **Устанавливать `Scrapling` стало ещё проще: установите его через pip, затем выполните `scrapling install` в терминале, и всё готово!**
- Исправлена неточная подсказка типа в парсере.

## [v0.2.91](https://github.com/D4Vinci/Scrapling/releases/tag/v0.2.91) - 2024-12-19 {#v0.2.91}

### Что изменилось {#v0.2.91-what-s-changed}
- Исправлена ошибка, из-за которой сообщение журнала о загрузке отображалось только для первого запроса.
- При переходе на страницу API Playwright по умолчанию возвращает первый ответ, который соответствует состоянию загрузки, переданному в `goto`: `["load", "domcontentloaded", "networkidle"]`. Поэтому если сайт сначала показывает страницу ожидания, как у Cloudflare, а затем перенаправляет на настоящий сайт, Playwright возвращает первый код состояния, например 403. Обновление решает эту проблему в `PlaywrightFetcher` и `StealthyFetcher`, поскольку оба используют API Playwright. Результат больше не зависит от этого стандартного поведения Playwright.
- В класс `Fetcher` добавлена поддержка SOCKS-прокси.
- Исправлена подсказка типа аргумента `wait_selector_state`: теперь автодополнение показывает правильные допустимые значения.

## [v0.2.9](https://github.com/D4Vinci/Scrapling/releases/tag/v0.2.9) - 2024-12-16 {#v0.2.9}

### Что изменилось {#v0.2.9-what-s-changed}
##### Новые возможности {#v0.2.9-new-features}
1. В Scrapling появилась **долгожданная** поддержка асинхронного кода! Добавлен `AsyncFetcher`, асинхронный вариант `Fetcher`, а у `StealthyFetcher` и `PlayWrightFetcher` появился метод `async_fetch` с теми же опциями.

```python
>> from scrapling import StealthyFetcher
>> page = await StealthyFetcher().async_fetch('https://www.browserscan.net/bot-detection')  # the async version of fetch
>> page.status == 200
True
```

2. В методы загрузки класса `StealthyFetcher` добавлен аргумент `geoip`. При включении класс автоматически использует долготу, широту, часовой пояс, страну и локаль IP-адреса, а затем подменяет IP-адрес WebRTC. Он также выбирает и подменяет язык браузера с учётом распространённости языков в целевом регионе.
3. Добавлен аргумент `retries` в классы `Fetcher`/`AsyncFetcher`. Он позволяет задать число повторных попыток для каждого запроса через `httpx`.
4. Добавлен метод `url_join` в `Adaptor` и Fetcher. Он соединяет относительный URL с текущим и создаёт полный абсолютный URL!
5. Добавлен метод `keep_cdata` в `Adaptor` и Fetcher, чтобы при необходимости запретить парсеру удалять CDATA.
6. В `Adaptor`/`Response` метод `body` теперь по возможности возвращает исходный HTML-ответ без обработки в библиотеке.
7. Добавлено журналирование в класс `Response`: при использовании Fetcher теперь выводится сообщение с данными полученного ответа.
Пример:

   ```python
   >> from scrapling.defaults import Fetcher
   >> Fetcher.get('https://books.toscrape.com/index.html')
   [2024-12-16 13:33:36] INFO: Fetched (200) <GET https://books.toscrape.com/index.html> (referer: https://www.google.com/search?q=toscrape)
   >>
   ```

8. Все стандартные строковые методы объекта `TextHandler`, например `.replace()`, теперь возвращают другой `TextHandler`. Раньше они возвращали обычную строку.
9. Значительно повышена скорость всей библиотеки и улучшена скрытная работа классов Fetcher.
10. Добавлены простые функции вроде `extract_first`\`extract`, которые возвращают тот же результат, что и родительский объект. Они нужны только для удобного переноса кода из Scrapy/Parsel в Scrapling, поскольку используются в тех библиотеках!
11. Благодаря переработке большого объёма кода и кешированию в нужных местах массовые запросы теперь выполняются значительно быстрее.

##### Несовместимые изменения {#v0.2.9-breaking-changes}
- Прекращена поддержка Python 3.8. (Главным образом потому, что Playwright перестал его поддерживать, но эта версия и так была проблемной.)
- Аргумент `debug` удалён из всей библиотеки. Чтобы включить отладку, выполните это после импорта библиотеки:

   ```python
   >>> import logging
   >>> logging.getLogger("scrapling").setLevel(logging.DEBUG)
   ```

##### Исправления ошибок {#v0.2.9-bugs-squashed}
1. WebGL теперь включён по умолчанию, поскольку многие системы защиты проверяют, включён ли он.
2. Исправлены ошибки и опечатки в документации и README.

##### Улучшения удобства {#v0.2.9-quality-of-life-changes}
1. Все сообщения журнала теперь используют логгер с именем `scrapling`, чтобы ими было проще управлять. Раньше использовался корневой логгер.
2. Структура папки тестов стала понятнее, добавлены тесты новых возможностей. Все тесты переписаны в более понятном виде и дополнены для лучшего покрытия.
3. Большая часть кода переработана, чтобы он стал понятнее и проще в поддержке.

> Все эти изменения изначально планировались для 0.3. Я решил добавить их уже сейчас, поскольку до следующей версии ещё пройдёт время. Теперь нужно закончить сайт с подробной документацией, а затем приступить к версии 0.3.

## [v0.2.8](https://github.com/D4Vinci/Scrapling/releases/tag/v0.2.8) - 2024-11-30 {#v0.2.8}

### Что изменилось {#v0.2.8-what-s-changed}
- Небольшое обновление с несколькими важными улучшениями удобства работы с кодом и исправлением опечатки в основном README (#20).

## [v0.2.7](https://github.com/D4Vinci/Scrapling/releases/tag/v0.2.7) - 2024-11-26 {#v0.2.7}

### Что изменилось {#v0.2.7-what-s-changed}
##### Новые возможности {#v0.2.7-new-features}
- При использовании аргумента `wait_selector` с классами `StealthyFetcher` и `PlayWrightFetcher` Scrapling теперь снова ждёт полной загрузки и выполнения JavaScript, как обычно. Если указан `network_idle`, после всех этих ожиданий Scrapling также повторно ждёт отсутствия сетевой активности. Если все состояния уже достигнуты, ожидания, конечно, не будет.
- В `StealthyFetcher` теперь можно разрешать или блокировать рекламу аргументом `disable_ads`. По умолчанию он включён и устанавливает дополнение `ublock origin`.
- Локаль `PlayWrightFetcher` теперь можно задать аргументом `locale`. По умолчанию по-прежнему используется `en-US`.
- Простые запросы через `Fetcher` теперь принимают прокси в формате `http://username:password@localhost:8030`.
- Немного улучшен скрытный режим `PlayWrightFetcher`.

##### Исправления ошибок и улучшения {#v0.2.7-bugs-squashed-improvements}
1. Прокси в классе `PlayWrightFetcher` теперь можно включить независимо от того, включён ли режим `stealth` (спасибо [@AbdullahY36](https://github.com/AbdullahY36) за замечание).
2. `ResponseEncoding` теперь проверяет, можно ли использовать кодировку ответа для страницы. Если она вызывает ошибку, Scrapling использует `utf-8`.

## [v0.2.6](https://github.com/D4Vinci/Scrapling/releases/tag/v0.2.6) - 2024-11-24 {#v0.2.6}

### Что изменилось {#v0.2.6-what-s-changed}
##### Новые возможности {#v0.2.6-new-features}
- `PlayWrightFetcher` теперь может напрямую использовать настоящий браузер. Передайте `real_chrome` в `PlayWrightFetcher.fetch`. Для этого должен быть установлен Chrome. Scrapling запустит ваш Chrome, и большинство опций можно будет использовать как обычно. (Раньше для этого был только аргумент `cdp_url`.)
- Повышена версия в заголовках, создаваемых для настоящих браузеров.

##### Исправления ошибок {#v0.2.6-bugs-squashed}
1. Оказалось, что формат браузерных заголовков, создаваемых `BrowserForge`, устарел. Из-за этого некоторые системы защиты обнаруживали Scrapling. Теперь `BrowserForge` используется только для создания настоящего User-Agent.
2. Аргумент `hide_canvas` теперь выключен по умолчанию, поскольку его обнаруживает ReCaptcha от Google.

## [v0.2.5](https://github.com/D4Vinci/Scrapling/releases/tag/v0.2.5) - 2024-11-23 {#v0.2.5}

### Что изменилось {#v0.2.5-what-s-changed}

##### Исправления ошибок {#v0.2.5-bugs-squashed}
- Обработана ошибка аргумента 'wait_selector', если он находил более 1 элемента. Это касается классов `StealthyFetcher` и `PlayWrightFetcher`.
- Исправлена кодировка, когда значение заголовка `content_type` содержит параметры вроде `charset` (спасибо @andyfcx за [#12](https://github.com/D4Vinci/Scrapling/issues/12)).

##### Улучшения удобства {#v0.2.5-quality-of-life}
- Добавлены тесты новых частей кода, а сами тесты теперь выполняются в потоках.
- Я обновил строки документации, чтобы они правильно отображались в Sphinx apidoc и подобных инструментах.

##### Новые участники {#v0.2.5-new-contributors}
- @andyfcx впервые внёс вклад в проект в [#13 ](https://github.com/D4Vinci/Scrapling/pull/13).

## [v0.2.4](https://github.com/D4Vinci/Scrapling/releases/tag/v0.2.4) - 2024-11-20 {#v0.2.4}

### Что изменилось {#v0.2.4-what-s-changed}

##### Исправления ошибок {#v0.2.4-bugs-squashed}
- Исправлена ошибка получения байтов ответа после использования аргумента `network_idle` в классах `StealthyFetcher` и `PlayWrightFetcher`. <br/>Она вызывала следующее сообщение об ошибке:

    ```
    Response.body: Protocol error (Network.getResponseBody): No resource with given identifier found
    ```

- API PlayWright иногда возвращает пустое описание статуса ответа. Теперь `Scrapling` определяет его самостоятельно, если это происходит. Изменение касается классов `StealthyFetcher` и `PlayWrightFetcher`.

## [v0.2.3](https://github.com/D4Vinci/Scrapling/releases/tag/v0.2.3) - 2024-11-19 {#v0.2.3}

### Что изменилось {#v0.2.3-what-s-changed}

##### Исправления ошибок {#v0.2.3-bugs-squashed}
- Исправлена ошибка установки через pip, из-за которой скрытный режим PlayWright Fetcher совсем не работал.

## [v0.2.2](https://github.com/D4Vinci/Scrapling/releases/tag/v0.2.2) - 2024-11-16 {#v0.2.2}

### Что изменилось {#v0.2.2-what-s-changed}
##### Новые возможности {#v0.2.2-new-features}
- Если вы не хотите передавать аргументы создаваемому объекту `Adaptor` и используете значения по умолчанию, теперь можно сделать код короче с помощью такого импорта:

    ```python
    >> from scrapling.default import Fetcher, StealthyFetcher, PlayWrightFetcher
    >> page = Fetcher.get('https://example.com', stealthy_headers=True)
    ```

    Иначе

    ```python
    >> from scrapling import Fetcher, StealthyFetcher, PlayWrightFetcher
    >> page = Fetcher(auto_match=False).get('https://example.com', stealthy_headers=True)
    ```

##### Исправления ошибок {#v0.2.2-bugs-squashed}
1. Исправлена ошибка объекта `Response`, появившаяся во вчерашнем патче v0.2.1. Она возникала в некоторых случаях вложенной выборки или разбора.

## [v0.2.1](https://github.com/D4Vinci/Scrapling/releases/tag/v0.2.1) - 2024-11-15 {#v0.2.1}

### Что изменилось {#v0.2.1-what-s-changed}
##### Новые возможности {#v0.2.1-new-features}
1. Объект `Response`, возвращаемый всеми Fetcher, теперь работает как `Adaptor`, но имеет дополнительные атрибуты: `status`, `reason`, `cookies`, `headers` и `request_headers`. Атрибуты `cookies`, `headers` и `request_headers` всегда имеют тип `dictionary`. <br/>Теперь код можно записать так:

    ```python
    >> from scrapling import Fetcher
    >> page = Fetcher().get('https://example.com', stealthy_headers=True)
    >> print(page.status)
    200
    >> products = page.css('.product')
    ```

    Вместо прежнего варианта

    ```python
    >> from scrapling import Fetcher
    >> fetcher = Fetcher().get('https://example.com', stealthy_headers=True)
    >> print(fetcher.status)
    200
    >> page = fetcher.adaptor
    >> products = page.css('.product')
    ```

    Но свойство `.adaptor` по-прежнему работает для обратной совместимости.

2. Классы `StealthyFetcher` и `PlayWrightFetcher` теперь принимают аргумент `proxy` в методе загрузки. Значением может быть строка или словарь.
3. В классе `StealthyFetcher` появился аргумент `os_randomize` для метода `fetch`. При включении Scrapling случайно выбирает отпечатки ОС. По умолчанию отпечатки соответствуют текущей ОС.

##### Исправления ошибок {#v0.2.1-bugs-squashed}
1. Исправлена ошибка при передаче заголовков в классе `Fetcher`.
2. Исправлена ошибка разбора JSON-ответов, переданных классами Fetcher.

##### Улучшения удобства {#v0.2.1-quality-of-life-changes}
1. Функция работы с текстом пыталась удалить HTML-комментарии перед возвратом текста, но в некоторых случаях это вызывало ошибки и излишне усложняло код. Теперь восстановлено стандартное поведение lxml. **Все операции, которые используют текст элементов, например селекторы, станут немного быстрее**. Если вы хотите удалять HTML-комментарии перед возвратом текста, чтобы избежать странного разделения текста в lxml/parsel/scrapy, оставьте аргумент `keep_comments` равным True, как по умолчанию.

## [v0.2](https://github.com/D4Vinci/Scrapling/releases/tag/v0.2) - 2024-11-11 {#v0.2}

### Что изменилось {#v0.2-what-s-changed}
##### Новые возможности {#v0.2-new-features}
1. Добавлена возможность `Fetchers` с 3 основными типами, чтобы Scrapling загружал страницы за вас с МНОЖЕСТВОМ настроек!
    - Класс `Fetcher` для простых HTTP-запросов.
    - Класс `StealthyFetcher` представляет собой полностью скрытный Fetcher и использует [изменённую версию Firefox для скрытной работы](https://github.com/daijro/camoufox).
    - Класс `PlayWrightFetcher` позволяет выполнять браузерные запросы через обычный PlayWright, PlayWright с моим скрытным режимом, настоящие браузеры через CDP, а также через [NSTBrowser](https://app.nstbrowser.io/r/1vO5e5) с его [docker browserless](https://hub.docker.com/r/nstbrowser/browserless)!
2. Добавлены совершенно новые методы `find_all`/`find`, чтобы легко находить элементы на странице словно по волшебству!
3. Добавлены методы `filter` и `search` в класс `Adaptors`, упрощающие массовые операции над группами объектов `Adaptor`.
4. Добавлены методы `css_first` и `xpath_first` для более удобной работы.
5. Добавлен новый класс `TextHandlers` для массовых операций над объектами `TextHandler`, как в классе `Adaptors`.
6. Добавлены методы `generate_full_css_selector` и `generate_full_xpath_selector`.

##### Исправления ошибок {#v0.2-bugs-squashed}
1. В классе `Adaptors` метод `re_first` теперь возвращает первое совпадение среди всех вложенных объектов `Adaptor`, а не результаты `re_first` для всех объектов `Adaptor`, как было раньше по ошибке.
2. Если вы выбираете текст из элементов, например с помощью CSS-функции `::text`, через такие методы, как `.css` или `.xpath`, объект `Adaptor` теперь возвращает `TextHandlers`, а не список строк. Поэтому можно написать `page.css('something::text').re_first(r'regex_pattern').json()` вместо `page.css('something::text')[0].re_first(r'regex_pattern').json()`.
3. Аргументы re/re_first у `Adaptor`/`Adaptors` теперь согласованы с `TextHandler`. Доступны аргументы `clean_match` и `case_sensitive`.
4. Аргумент `auto_match` теперь включён по умолчанию при инициализации `Adaptor`, но для использования функции его всё равно нужно включить при выборке элементов. (Это не ошибка, так задумано.)
5. Исправлено много аннотаций типов для лучшего автодополнения при написании кода со Scrapling.

##### Улучшения удобства {#v0.2-quality-of-life-changes}
1. Методы `css_selector` и `xpath_selector` переименованы в `generate_css_selector` и `generate_xpath_selector`, чтобы названия были понятнее и не мешали автодополнению при написании кода.
2. Большая часть старого кода перенесена в подпакет `core`, также пересмотрены другие решения по структуре, чтобы код стал чище и проще в дальнейшей поддержке.
3. Папка тестов получила более понятную структуру, добавлены тесты новых возможностей. Окружения tox теперь кешируются на GitHub, чтобы ускорить автоматические тесты при каждом коммите.

## [v0.1.2](https://github.com/D4Vinci/Scrapling/releases/tag/v0.1.2) - 2024-10-16 {#v0.1.2}

**История изменений**:

- Исправлена ошибка, из-за которой аргумент `keep_comments` работал не так, как ожидалось.
- Функция работы с текстом теперь автоматически удаляет HTML-комментарии из элементов перед извлечением текста, чтобы избежать особого поведения Lxml. Например:

    ```python
    >>> page = Adaptor('<span>CONDITION: <!-- -->Excellent</span>', keep_comments=True)
    >>> page.css('span::text')
    ['CONDITION: ', 'Excellent']
    ```

    Раньше стандартное поведение Lxml давало показанный выше результат, а теперь возвращается полный текст 'CONDITION: Excellent'.
    Такое поведение известно и в parsel\scrapy, поэтому я решил обработать его здесь.

- Исправлена ошибка, из-за которой файл базы SQLite, созданный библиотекой, не удалялся при выполнении `pip uninstall scrapling` и похожих команд.

## [v0.1.1](https://github.com/D4Vinci/Scrapling/releases/tag/v0.1.1) - 2024-10-14 {#v0.1.1}

Мелкие исправления

## [v0.1](https://github.com/D4Vinci/Scrapling/releases/tag/v0.1) - 2024-10-13 {#v0.1}

**Полная история изменений**: <https://github.com/D4Vinci/Scrapling/commits/v0.1>
