---
title: "Сбор данных с JavaScript-сайтов через StealthyFetcher"
description: "Загружайте страницы, ждите данные, повторно используйте состояние входа и читайте фоновые ответы API через браузерные сессии Scrapling. Настраивайте прокси и обработку проверок."
---

# Получение страниц через StealthyFetcher {#browser-fetching-with-stealthyfetcher}

Класс `StealthyFetcher` загружает JavaScript-страницы и управляет Chromium или Google Chrome с функциями обхода защиты от ботов. Он использует [API Playwright](https://playwright.dev/python/docs/intro) с изменениями для скрытной работы.

Для автоматизации страницы, которую мы рассмотрим позже, нужно немного знать [Page API Playwright](https://playwright.dev/python/docs/api/class-page).

!!! success "Перед началом"

    1. Прочитайте [Основы работы с Fetcher](../fetching/choosing.md), чтобы понять, что такое [объект Response](../fetching/choosing.md#response-object) и какой Fetcher выбрать.
    2. Прочитайте [Поиск элементов](../parsing/selection.md), чтобы понять, как находить и извлекать элементы из [Selector](../parsing/main_classes.md#selector)/[Response](../fetching/choosing.md#response-object).
    3. Прочитайте [Основные классы](../parsing/main_classes.md), чтобы узнать, какие свойства и методы [Response](../fetching/choosing.md#response-object) наследует от [Selector](../parsing/main_classes.md#selector).

## Основы использования {#basic-usage}
Основной способ импорта этого Fetcher такой же, как и для остальных:

```python
from scrapling.fetchers import StealthyFetcher
```
О настройке парсера читайте [здесь](choosing.md#parser-configuration-in-all-fetchers).

Теперь рассмотрим основные аргументы по отдельности на примерах. Для быстрой справки можно сразу перейти к [полной таблице аргументов](#full-list-of-arguments).

!!! abstract "Кратко"

    Асинхронная версия метода `fetch` называется `async_fetch`.


Сейчас этот Fetcher предоставляет три основных варианта запуска, которые можно сочетать по необходимости.

Вот эти варианты:

### 1. Chromium из комплекта {#1-bundled-chromium}
```python
StealthyFetcher.fetch('https://example.com')
```
Этот вариант открывает поставляемый с библиотекой Chromium с настройками скрытной работы по умолчанию и загружает страницу.

### 2. Установленный Chrome {#2-real-chrome}
```python
StealthyFetcher.fetch('https://example.com', real_chrome=True)
```
Если у вас установлен Google Chrome, используйте этот вариант. Он работает как первый, но запускает ваш Google Chrome вместо Chromium. Запросы больше похожи на обычные действия браузера и менее заметны для защиты.

Если Google Chrome ещё не установлен, его можно установить для библиотеки следующей командой в терминале вместо ручной установки:
```commandline
playwright install chrome
```

### 3. Подключение по CDP {#3-cdp-connection}
```python
StealthyFetcher.fetch('https://example.com', cdp_url='ws://localhost:9222')
```
Вместо локального запуска Chromium или Google Chrome можно подключиться к удалённому браузеру через [Chrome DevTools Protocol](https://chromedevtools.github.io/devtools-protocol/).

URL может быть адресом WebSocket (`ws://`/`wss://`), который выдают браузерные сервисы, или HTTP-адресом браузера, например `http://localhost:9222`.


## Что он умеет? {#what-does-it-do}

StealthyFetcher предоставляет следующие средства обхода защиты от ботов:

1. Автоматически проходит все виды Cloudflare Turnstile/Interstitial при `solve_cloudflare=True`.
2. Предотвращает утечки через CDP Runtime и WebRTC.
3. Изолирует выполнение JavaScript, убирает многие признаки Playwright и предотвращает обнаружение по известным особенностям поведения ботов.
4. Добавляет шум в Canvas, чтобы помешать получению отпечатка через него.
5. Автоматически противодействует известным способам обнаружения режима без окна и предлагает настройку для защиты от проверок несовпадения часовых поясов.
6. Предоставляет и другие возможности обхода защиты.

## Все аргументы {#full-list-of-arguments}
У этого Fetcher и его классов сессий много настроек. Перед переходом к [примерам](#examples) приведём полный список аргументов.


| Аргумент | Описание | Необязательный |
|:---------------------:|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|:--------:|
| url | URL назначения. | ❌ |
| headless | Передайте `True` для работы браузера без видимого окна (**по умолчанию**) или `False`, чтобы показывать окно. | ✔️ |
| disable_resources | Пропускает запросы ненужных ресурсов для ускорения работы. Пропускаются типы `font`, `image`, `media`, `beacon`, `object`, `imageset`, `texttrack`, `websocket`, `csp_report` и `stylesheet`. | ✔️ |
| cookies | Cookie для следующего запроса. | ✔️ |
| useragent | Строка User-Agent. **Если не указана, Fetcher создаёт и использует User-Agent настоящего браузера того же вида и версии.** | ✔️ |
| network_idle | Ждёт, пока на странице не будет сетевых соединений хотя бы 500 мс. | ✔️ |
| load_dom | По умолчанию включено. Ждёт загрузки и выполнения всего JavaScript на странице, то есть состояния `domcontentloaded`. | ✔️ |
| pierce_shadow | Включает содержимое открытых Shadow DOM в HTML ответа. По умолчанию `False`. Можно задать для сессии и переопределить для отдельного запроса. | ✔️ |
| timeout | Тайм-аут в миллисекундах для всех операций и ожиданий на странице. По умолчанию 30 000 мс (30 секунд). | ✔️ |
| wait | Время в миллисекундах, которое Fetcher ждёт после всех операций, прежде чем закрыть страницу и вернуть объект `Response`. | ✔️ |
| page_action | Функция автоматизации. Принимает объект `page` и выполняет нужные действия после перехода на страницу. | ✔️ |
| page_setup | Функция, которая принимает `page` и выполняется до перехода на страницу. Используйте её для регистрации обработчиков событий или маршрутов до загрузки страницы. | ✔️ |
| wait_selector | Ждёт, пока элемент по CSS-селектору достигнет указанного состояния. | ✔️ |
| init_script | Абсолютный путь к JavaScript-файлу, который запускается при создании каждой страницы в этой сессии. | ✔️ |
| wait_selector_state | Состояние, которого Scrapling ждёт для селектора из `wait_selector`. _По умолчанию `attached`._ | ✔️ |
| google_search | По умолчанию включено. Scrapling устанавливает заголовок Referer для Google. | ✔️ |
| extra_headers | Словарь дополнительных заголовков запроса. _При совместном использовании Referer от `google_search` имеет приоритет над Referer из этого словаря._ | ✔️ |
| proxy | Прокси для запросов. Строка или словарь только с ключами 'server', 'username' и 'password'. | ✔️ |
| real_chrome | Если на устройстве установлен Chrome, включите эту настройку, и Fetcher запустит ваш браузер. | ✔️ |
| locale | Локаль, например `en-GB` или `de-DE`. Влияет на `navigator.language`, заголовок запроса `Accept-Language`, а также формат чисел и дат. По умолчанию используется системная локаль. | ✔️ |
| timezone_id | Меняет часовой пояс браузера. По умолчанию используется системный часовой пояс. | ✔️ |
| cdp_url | Подключается к браузеру по этому CDP URL вместо запуска нового экземпляра. | ✔️ |
| user_data_dir | Путь к каталогу пользовательских данных браузера, например cookie и local storage. По умолчанию создаётся временный каталог. **Работает только с сессиями.** | ✔️ |
| extra_flags | Список дополнительных флагов, передаваемых браузеру при запуске. | ✔️ |
| solve_cloudflare | При включении Fetcher проходит все виды Cloudflare Turnstile/Interstitial перед возвратом ответа. По умолчанию `False`. | ✔️ |
| block_webrtc | Заставляет WebRTC учитывать настройки прокси, чтобы избежать утечки локального IP-адреса. | ✔️ |
| hide_canvas | Добавляет случайный шум к операциям Canvas, чтобы помешать получению отпечатка. | ✔️ |
| allow_webgl | По умолчанию включено. Отключение полностью убирает поддержку WebGL и WebGL 2.0. Отключать не рекомендуется, так как многие WAF проверяют наличие WebGL. | ✔️ |
| additional_args | Дополнительные настройки контекста Playwright. Имеют приоритет над настройками Scrapling. | ✔️ |
| selector_config | Словарь настроек парсера для создания итогового объекта `Selector`/`Response`. | ✔️ |
| blocked_domains | Множество доменов, запросы к которым нужно блокировать. Поддомены тоже учитываются: `"example.com"` блокирует и `"sub.example.com"`. | ✔️ |
| block_ads | Блокирует запросы примерно к 3 500 известным рекламным и отслеживающим доменам. Можно использовать вместе с `blocked_domains`. | ✔️ |
| dns_over_https | Направляет DNS-запросы через Cloudflare DNS-over-HTTPS, чтобы избежать утечек DNS при использовании прокси. | ✔️ |
| proxy_rotator | Экземпляр `ProxyRotator` для автоматической смены прокси. Нельзя использовать вместе с `proxy`. | ✔️ |
| retries | Число повторных попыток при ошибке запроса. По умолчанию 3. | ✔️ |
| retry_delay | Пауза между повторными попытками в секундах. По умолчанию 1. | ✔️ |
| record_requests | Сохраняет завершённые запросы и ответы в `session.network`. Только для сессий, по умолчанию `False`. | ✔️ |
| max_recorded_requests | Максимальное число сохранённых запросов в сессии. По умолчанию 1 000. Для сохранённых тел ответов также есть фиксированные ограничения размера. | ✔️ |
| executable_path | Абсолютный путь к своему исполняемому файлу браузера вместо Chromium из комплекта. Полезно для нестандартной установки или собственной сборки браузера. | ✔️ |

В классах сессий все эти аргументы можно задать для всей сессии. Некоторые настройки уровня вкладки можно также передавать отдельно в каждом запросе: `google_search`, `timeout`, `wait`, `page_action`, `page_setup`, `extra_headers`, `disable_resources`, `wait_selector`, `wait_selector_state`, `network_idle`, `load_dom`, `pierce_shadow`, `solve_cloudflare`, `blocked_domains`, `proxy` и `selector_config`.

!!! note "Примечания"

    1. В моих тестах `disable_resources` ускорял запросы примерно на 25% для некоторых сайтов. Он также помогает сократить трафик через прокси. Но будьте осторожны: некоторые сайты с этой настройкой могут так и не завершить загрузку.
    2. Аргумент `google_search` включён по умолчанию для всех запросов и задаёт Referer `https://www.google.com/`. При использовании с `extra_headers` он имеет приоритет над Referer из этого словаря.
    3. Если User-Agent не задан, а режим без окна включён, Fetcher создаст User-Agent настоящего браузера той же версии. Если User-Agent не задан и режим без окна не включён, используется стандартный User-Agent браузера. В последних версиях он совпадает с обычными браузерами.
    4. `init_script` регистрируется в контексте браузера и выполняется при создании страниц. Режим скрытной работы по умолчанию использует изолированный контекст выполнения Patchright. Если `page_action` должен читать глобальные переменные, которые скрипт добавил в `window`, вызывайте внутри него `page.evaluate(..., isolated_context=False)`.

## Управление сессиями {#session-management}

Чтобы держать браузер открытым для нескольких запросов с общими настройками, используйте `StealthySession`/`AsyncStealthySession`. Эти классы принимают все аргументы функции `fetch`, поэтому можно настроить всю сессию сразу.

```python
from scrapling.fetchers import StealthySession


with StealthySession(
    headless=True,
    disable_resources=True,
    real_chrome=True
) as session:

    page1 = session.fetch('https://example1.com')
    page2 = session.fetch('https://example2.com')
    page3 = session.fetch('https://dynamic-site.com')


```

### Асинхронные сессии {#async-session-usage}

```python
import asyncio
from scrapling.fetchers import AsyncStealthySession

async def scrape_multiple_sites():
    async with AsyncStealthySession(
        network_idle=True,
        timeout=30000,
        max_pages=3
    ) as session:

        pages = await asyncio.gather(
            session.fetch('https://spa-app1.com'),
            session.fetch('https://spa-app2.com'),
            session.fetch('https://dynamic-content.com')
        )
        return pages
```

Аргумент `max_pages` задаёт максимальный размер **пула вкладок браузера**, то есть число вкладок, которые могут быть открыты одновременно. После запроса вкладки остаются открытыми. Для каждого следующего запроса библиотека выполняет такие действия:

1. Повторно использует свободную вкладку, если она есть. Запрос применяет свои настройки уровня вкладки (`timeout`, `extra_headers`, `disable_resources`, `blocked_domains` и другие), поэтому настройки предыдущего запроса не сохраняются.
2. Если свободных вкладок нет, а их число меньше `max_pages`, открывает новую.
3. Иначе проверяет наличие свободной вкладки чаще одного раза в секунду в течение 60 секунд, а затем вызывает `TimeoutError`. Это может произойти, если сайт перестал отвечать.

Вкладки с ошибками закрываются и заменяются. В любой момент можно закрыть все открытые вкладки через `session.close_pages()`. Следующий запрос откроет новую.

Так можно получать несколько URL одновременно в одном браузере. Это заметно экономит ресурсы и, что особенно приятно, работает быстро :)

Открытая вкладка сохраняет загруженную страницу до следующего запроса. Его функция `page_setup` запускается на этой странице до перехода по новому адресу. Это позволяет связывать автоматические действия между запросами.

В версиях с 0.3.2 по 0.4.14 каждая вкладка закрывалась после запроса, потому что при повторном использовании сохранялись старые настройки. Начиная с 0.4.15, настройки сбрасываются при каждом использовании, поэтому вкладки остаются открытыми.

### Сохранение и загрузка состояния сессии {#save-and-load-session-state}

Метод `save_state(path)` сохраняет cookie, local storage и IndexedDB в JSON-файл. Метод `load_state(path)` восстанавливает их в другой сессии или заменяет сохранённое состояние текущей сессии. Оба принимают строку или `pathlib.Path` и возвращают `None`. Формат совместим с файлами состояния хранилища Playwright.

```python
from scrapling.fetchers import StealthySession

with StealthySession() as session:
    session.fetch('https://example.com')
    session.save_state('state.json')

with StealthySession() as session:
    session.load_state('state.json')
    page = session.fetch('https://example.com')
```

Сохраняйте состояние после входа или завершения других действий браузера. Оба метода вызывайте внутри запущенной сессии, когда все текущие запросы завершены. Загрузка заменяет существующие cookie, local storage и IndexedDB. Чтобы использовать восстановленный вход, получите или перезагрузите страницу. Сама загрузка состояния не меняет адрес открытых вкладок.

С `AsyncStealthySession` используйте `await`:

```python
from scrapling.fetchers import AsyncStealthySession

async def restore_session():
    async with AsyncStealthySession() as session:
        await session.load_state('state.json')
        page = await session.fetch('https://example.com')
        await session.save_state('state.json')
        return page
```

Эти методы сохраняют и восстанавливают только общий контекст браузера. Они не затрагивают временные контексты для прокси отдельных запросов. У сессий с `proxy_rotator` нет общего контекста, поэтому методы вызывают `RuntimeError`. Фиксированный `proxy` сессии работает как обычно.

Файл не содержит `sessionStorage`, открытые вкладки или настройки браузера. Сохранение перезаписывает файл, а его родительский каталог должен уже существовать. Ошибки файла и JSON передаются вызывающему коду.

### Преимущества сессий {#session-benefits}

- **Повторное использование браузера**: следующие запросы намного быстрее, потому что используется тот же экземпляр браузера.
- **Сохранение cookie**: автоматическая работа с cookie и состоянием сессии, как в обычном браузере.
- **Постоянный отпечаток**: один и тот же отпечаток браузера для всех запросов.
- **Экономия памяти**: меньше затрат ресурсов, чем при запуске нового браузера для каждого запроса.


## Примеры {#examples}
На примерах разобраться проще, поэтому перейдём к ним.

### Управление ресурсами {#resource-control}

```python

page = StealthyFetcher.fetch('https://example.com', disable_resources=True)
```

### Shadow DOM {#shadow-dom}

Некоторые страницы хранят содержимое в открытых корнях Shadow DOM. Оно не входит в обычный HTML страницы. Включите `pierce_shadow`, чтобы добавить его в ответ, а затем используйте CSS- и XPath-селекторы как обычно:

```python
from scrapling.fetchers import StealthyFetcher

page = StealthyFetcher.fetch('https://example.com', pierce_shadow=True)
titles = page.css('product-card .title::text').getall()
```

По умолчанию установлено `False`. Можно включить настройку для всей сессии и отключить для отдельного запроса:

```python
from scrapling.fetchers import StealthySession

with StealthySession(pierce_shadow=True) as session:
    page = session.fetch('https://example.com')
    plain_page = session.fetch('https://example.com', pierce_shadow=False)
```

Эта настройка также работает с `async_fetch` и асинхронными сессиями.

Включаются только корни Shadow DOM в открытом режиме. Закрытые корни и документы iframe не обходятся. Если компонент загружается позже самой страницы, используйте `wait_selector`.

Каждый открытый корень превращается в обёртку `<shadow-root>` в ответе. Слоты сохраняют свои теги и атрибуты и содержат назначенные им узлы либо запасное содержимое, если ничего не назначено. Неназначенные дочерние элементы Light DOM пропускаются. Живая страница в браузере не меняется.

```html
<product-card>
  <shadow-root>
    <div class="title">Product name</div>
    <slot name="price"><span class="price">20</span></slot>
  </shadow-root>
</product-card>
```

Селекторы потомков работают через эти элементы. Селекторы прямых дочерних элементов должны учитывать обёртки и слоты:

```python
titles = page.css('product-card .title::text').getall()
titles = page.css('product-card > shadow-root > .title::text').getall()
prices = page.css('product-card > shadow-root > slot[name="price"] > .price::text').getall()
```

Обёртки и слоты появляются в XPath-путях, `.children`, `response.body` и HTML-экспорте. Извлечение Markdown и текста возвращает их содержимое без тегов. Атрибуты скрытых слотов сохраняются и доступны при очистке содержимого.

Снимок сохраняет порядок содержимого, но не рассчитывает видимость по CSS или расположение элементов. Селекторы с `<shadow-root>` относятся к ответу Scrapling, а не к странице в браузере. Другие HTML-парсеры могут иначе обрабатывать необычную вложенность.

### Блокировка доменов {#domain-blocking}

```python

page = StealthyFetcher.fetch('https://example.com', blocked_domains={"ads.example.com", "tracker.net"})
```

### Управление сетью {#network-control}

```python

page = StealthyFetcher.fetch('https://example.com', network_idle=True)


page = StealthyFetcher.fetch('https://example.com', timeout=30000)


page = StealthyFetcher.fetch('https://example.com', proxy='http://username:password@host:port')
```

### Скачивание файлов {#downloading-files}

```python
page = StealthyFetcher.fetch('https://raw.githubusercontent.com/D4Vinci/Scrapling/main/docs/assets/main_cover.png')

with open(file='main_cover.png', mode='wb') as f:
    f.write(page.body)
```

Атрибут `body` объекта `Response` всегда возвращает `bytes`.

### Подготовка до перехода на страницу {#pre-navigation-setup}
Если обработчики событий, маршруты или скрипты нужно зарегистрировать до перехода на страницу, используйте `page_setup`. Функция получает объект `page` и выполняется до вызова `page.goto()`.

```python
from patchright.sync_api import Page

def capture_websockets(page: Page):
    page.on("websocket", lambda ws: print(f"WebSocket opened: {ws.url}"))

page = StealthyFetcher.fetch('https://example.com', page_setup=capture_websockets)
```
Асинхронная версия:
```python
from patchright.async_api import Page

async def capture_websockets(page: Page):
    page.on("websocket", lambda ws: print(f"WebSocket opened: {ws.url}"))

page = await StealthyFetcher.async_fetch('https://example.com', page_setup=capture_websockets)
```

Можно сочетать её с `page_action`: `page_setup` выполняется до перехода, а `page_action` после него.

### Cloudflare и скрытная работа {#cloudflare-and-stealth-options}

```python

page = StealthyFetcher.fetch('https://nopecha.com/demo/cloudflare', solve_cloudflare=True)


page = StealthyFetcher.fetch(
    'https://protected-site.com',
    solve_cloudflare=True,
    block_webrtc=True,
    real_chrome=True,
    hide_canvas=True,
    google_search=True,
    proxy='http://username:password@host:port',  # It can also be a dictionary with only the keys 'server', 'username', and 'password'.
)
```

Параметр `solve_cloudflare` включает автоматическое обнаружение и прохождение всех видов проверок Cloudflare Turnstile/Interstitial:

- Проверки JavaScript (managed).
- Интерактивные проверки с нажатием на поле подтверждения.
- Невидимые проверки, выполняемые автоматически в фоне.

Он также проходит проверки на нестандартных страницах со встроенной CAPTCHA.

!!! notes "**Важные примечания**"

    1. На сайтах с собственной реализацией защиты иногда нужен `wait_selector`, чтобы дождаться настоящего содержимого сайта после прохождения CAPTCHA. Мы стараемся сделать обработчик универсальным, но встречаются очень необычные случаи.
    2. При использовании обработчика Cloudflare тайм-аут должен быть не меньше 60 секунд, чтобы дать достаточно времени на проверку.
    3. Эта возможность работает вместе с прокси и другими настройками скрытной работы.

### Автоматизация браузера {#browser-automation}
Здесь пригодятся знания [Page API Playwright](https://playwright.dev/python/docs/api/class-page). Переданная функция получает объект страницы Playwright и выполняет нужные действия, после чего Fetcher продолжает работу.

Функция запускается сразу после ожидания `network_idle`, если оно включено, и до ожидания `wait_selector`. Поэтому её можно использовать не только для автоматизации, но и для любых нужных изменений страницы.

В следующем примере я использую [события мыши](https://playwright.dev/python/docs/api/class-mouse), чтобы прокрутить страницу колёсиком, а затем переместить мышь:
```python
from patchright.sync_api import Page

def scroll_page(page: Page):
    page.mouse.wheel(10, 0)
    page.mouse.move(100, 400)
    page.mouse.up()

page = StealthyFetcher.fetch('https://example.com', page_action=scroll_page)
```
Если используется асинхронный метод получения страницы, функция тоже должна быть асинхронной.
```python
from patchright.async_api import Page

async def scroll_page(page: Page):
   await page.mouse.wheel(10, 0)
   await page.mouse.move(100, 400)
   await page.mouse.up()

page = await StealthyFetcher.async_fetch('https://example.com', page_action=scroll_page)
```

### Условия ожидания {#wait-conditions}

```python

page = StealthyFetcher.fetch(
    'https://quotes.toscrape.com/js-delayed/',
    wait_selector='.quote',
    wait_selector_state='visible'
)
```
Если эта настройка включена, Fetcher ждёт указанное условие перед возвратом ответа. Передайте CSS-селектор в `wait_selector`, и Fetcher дождётся состояния из `wait_selector_state`. По умолчанию используется `attached`: ожидание появления элемента в DOM.

Затем, если `load_dom` включён (по умолчанию), Fetcher ещё раз проверяет завершение загрузки и выполнения JavaScript, то есть состояние `domcontentloaded`, и при необходимости продолжает ждать. Если включён `network_idle`, он снова ждёт выполнения условия `network_idle`, как описано выше.

Можно ждать следующие состояния ([источник](https://playwright.dev/python/docs/api/class-page#page-wait-for-selector)):

- `attached`: элемент присутствует в DOM.
- `detached`: элемент отсутствует в DOM.
- `visible`: у элемента непустая ограничивающая рамка и нет `visibility:hidden`. Элемент без содержимого или с `display:none` имеет пустую рамку и не считается видимым.
- `hidden`: элемент удалён из DOM, имеет пустую ограничивающую рамку или `visibility:hidden`. Это противоположность `'visible'`.

### История сети {#network-history}

Включите `record_requests` в браузерной сессии, чтобы просматривать завершённые запросы при загрузке страниц, выполнении действий и работе с разными вкладками. История охватывает контексты сессии, включая временные контексты прокси, и сохраняет ответы как объекты Scrapling `Response`. Можно найти вызовы API, HTTP-ошибки и перенаправления без повторной отправки запросов. Сохранённые заголовки и тела доступны даже после закрытия сессии. Неудачные и незавершённые запросы пропускаются, но завершённые HTTP-ответы 4xx и 5xx включаются.

```python
from scrapling.fetchers import StealthySession

with StealthySession(record_requests=True, max_recorded_requests=1000) as session:
    session.fetch('https://example.com', network_idle=True)

for response in session.network.search(resource_type='document', limit=None):
    print(response.meta['network_id'], response.url, response.status)
    if note := response.meta.get('body_note'):
        print(note)
    else:
        print(response.body)
        print(response.css('title::text').get())

session.network.clear()
```

Этот API работает и с `AsyncStealthySession`. По умолчанию запись выключена. При создании сессии задайте `record_requests=True` и при необходимости `max_recorded_requests`.

- `session.network.search(url_pattern=None, method=None, resource_type=None, status=None, after_id=0, limit=100, include_static=True)` возвращает сохранённые объекты `Response` в порядке сетевых ID. `limit=None` возвращает все сохранённые совпадения. `url_pattern` задаёт регулярное выражение, применяемое при поиске. Неверный шаблон вызывает ошибку именно в этот момент. `after_id` выбирает ответы с большим сетевым ID. `include_static=False` оставляет только XHR/fetch-запросы и HTTP-ошибки. Используйте `True`, чтобы включить все типы ресурсов и сохранённые перенаправления.
- `session.network.get(request_id)` возвращает один сохранённый `Response` или `None`, если он больше не хранится.
- `session.network.clear()` очищает историю. ID запросов продолжают увеличиваться и не используются повторно.

Каждый сохранённый `Response` предоставляет `.url`, `.method`, `.status`, `.headers`, `.request_headers`, байты `.body`, `.json()` и методы CSS/XPath напрямую. В `.meta` находятся `network_id`, `resource_type` и `request_body` (байты или `None`). Заголовки могут быть неполными, если чтение полного набора не удалось. Это локальные операции даже в асинхронных сессиях: не используйте для них await и не вызывайте `.body()`. Если сохранённое содержимое нельзя разобрать, его байты остаются, но методы CSS/XPath работают с пустым документом.

Для поиска API-трафика по URL используйте `session.network.search(url_pattern=r'https://api\.example\.com/.*', limit=None)`. Если нужен определённый тип запроса, добавьте `resource_type='fetch'` или `resource_type='xhr'`.

Записываются только тела с поддерживаемыми текстовыми значениями `Content-Type`: `text/*`, типы `+json`/`+xml` (включая SVG), JSON, XML, JavaScript, GraphQL и данные формы в URL-кодировке. Для двоичных и неизвестных типов, а также ответов без `Content-Type`, сохраняются метаданные, но не байты тела. Браузер продолжает загружать ресурсы как обычно.

Сохранённые байты ответа получены от Playwright и могут отличаться от исходных байтов сервера. Если они являются корректным UTF-8, текст декодируется как UTF-8, как в Playwright. В противном случае используется объявленная кодировка. Заголовки ответа не меняются.

Для пропущенных, слишком больших или нечитаемых тел возвращается `b''`, а причина указана в `response.meta.get('body_note')`. Для нетекстовых тел используется `Non-text body; not saved.`. Метаданные и доступные заголовки сохраняются. У сохранённого текста, включая пустой, примечания нет. Ответы HEAD и статусы 204, 205 и 304 остаются пустыми без примечания.

Методы истории `search`, `get` и `clear` всегда локальные и синхронные, даже в асинхронной сессии. Запись появляется после преобразования и сохранения ответа. События браузера обрабатываются, пока активен Playwright. Для асинхронной записи также должен работать цикл событий. Чтение истории не ждёт завершения записи.

Закрытие сессии тоже не ждёт завершения записи. Ответы, которые ещё записывались при переходе на другую страницу или закрытии контекста, могут быть пропущены. Уже сохранённые ответы доступны и после закрытия.

По умолчанию история хранит до 1 000 запросов. Размер каждого сохранённого тела ограничен 1 MiB, а общий размер тел ограничен 20 MiB. При достижении лимитов старые записи удаляются. Ограничения размера тел фиксированы и не меняются настройками сессии. Они относятся к сохранённым записям и байтам ответов, но не к общей памяти браузера, одновременным записям, временному чтению полного тела, разобранному HTML или телам запросов.

#### Переход на v5 {#migrating-in-v5}

В v5 удалены `capture_xhr` и `response.captured_xhr`. Создайте браузерную сессию с `record_requests=True`, затем читайте `session.network.search(url_pattern=..., limit=None)`. Этот способ также заменяет запись API через одноразовые Fetcher, поэтому сохраняйте экземпляр сессии. Фильтры применяются к сохранённой истории всей сессии, а не во время записи или только к одному получению страницы. Сохраняются только поддерживаемые текстовые тела ответов. `search()` по умолчанию возвращает не больше 100 совпадений. `limit=None` возвращает все сохранённые совпадения, не меняя лимиты хранения истории.

### Заголовки и локаль браузера {#browser-headers-and-locale}

```python
page = StealthyFetcher.fetch(
    'https://example.com',
    google_search=True,
    useragent='Mozilla/5.0...',
    locale='en-US',
)
```

### Полный пример {#general-example}
```python
from scrapling.fetchers import StealthyFetcher

def scrape_dynamic_content():

    page = StealthyFetcher.fetch(
        'https://example.com/dynamic',
        network_idle=True,
        wait_selector='.content'
    )


    content = page.css('.content')

    return {
        'title': content.css('h1::text').get(),
        'items': [
            item.text for item in content.css('.item')
        ]
    }
```

### Смена прокси {#proxy-rotation}

```python
from scrapling.fetchers import StealthySession, ProxyRotator


rotator = ProxyRotator([
    "http://proxy1:8080",
    "http://proxy2:8080",
    "http://proxy3:8080",
])


with StealthySession(proxy_rotator=rotator, headless=True) as session:
    page1 = session.fetch('https://example1.com')
    page2 = session.fetch('https://example2.com')


    page3 = session.fetch('https://example3.com', proxy='http://specific-proxy:8080')
```

!!! warning "Внимание"

    По умолчанию все браузерные Fetcher и сессии используют постоянный контекст браузера с пулом вкладок. Но браузеры не позволяют задать прокси для отдельной вкладки. Поэтому при использовании `ProxyRotator` Fetcher создаёт отдельный контекст для каждого прокси, с одной вкладкой в каждом. Когда вкладка завершает работу, закрываются и она, и её контекст.

## Когда использовать {#when-to-use}

Используйте StealthyFetcher, если:

- Нужно обходить защиту от ботов.
- Нужен надёжный отпечаток браузера.
- Требуется полная поддержка JavaScript.
- Нужны автоматические функции скрытной работы.
- Нужна автоматизация браузера.
- Нужно работать с защитой Cloudflare.
