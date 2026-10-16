---
title: "Проверка сбора данных в интерактивной оболочке Scrapling"
description: "Загружайте страницы, пробуйте селекторы и изучайте результаты в IPython. Преобразуйте команды curl, повторно используйте недавние ответы и проверяйте код сбора данных."
---

# Интерактивная оболочка Scrapling {#scrapling-interactive-shell-guide}

<script src="https://asciinema.org/a/736339.js" id="asciicast-736339" async data-autoplay="1" data-loop="1" data-cols="225" data-rows="40" data-start-at="00:06" data-speed="1.5" data-theme="tango"></script>

**Среда REPL для разработчиков и специалистов по данным, работающих с веб-скрейпингом**

Интерактивная оболочка Scrapling расширяет IPython для задач сбора данных с сайтов. Все возможности Scrapling доступны сразу. В ней есть удобные сокращения, автоматическое управление страницами и инструменты вроде преобразования команд curl.

!!! success "Перед началом"

    1. Прочитайте [основы Fetcher](../fetching/choosing.md), чтобы понять, что такое [объект Response](../fetching/choosing.md#response-object) и какой Fetcher выбрать.
    2. Прочитайте [поиск элементов](../parsing/selection.md), чтобы научиться находить и извлекать элементы из [Selector](../parsing/main_classes.md#selector)/[Response](../fetching/choosing.md#response-object).
    3. Прочитайте [основные классы](../parsing/main_classes.md), чтобы узнать, какие свойства и методы [Response](../fetching/choosing.md#response-object) наследует от [Selector](../parsing/main_classes.md#selector).
    4. Прочитайте хотя бы одну страницу о Fetcher, который будете использовать: [HTTP-запросы](../fetching/static.md) или [загрузка через браузер](../fetching/stealthy.md).


## Зачем нужна интерактивная оболочка {#why-use-the-interactive-shell}

Оболочка позволяет быстро пробовать разные подходы, вместо того чтобы каждый раз писать и запускать скрипт. Она подходит для следующих задач:

- **Быстрые прототипы**: сразу проверяйте способы сбора данных.
- **Изучение данных**: переходите по сайту и извлекайте данные в диалоге с оболочкой.
- **Изучение Scrapling**: пробуйте функции на практике.
- **Отладка**: выполняйте запросы по шагам и проверяйте результаты.
- **Преобразование рабочих запросов**: превращайте команду curl из DevTools браузера в запрос Fetcher одной строкой.

## Начало работы {#getting-started}

### Запуск оболочки {#launch-the-shell}

```bash
# Start the interactive shell
scrapling shell

# Execute code and exit (useful for scripting)
scrapling shell -c "get('https://quotes.toscrape.com'); print(len(page.css('.quote')))"

# Set logging level
scrapling shell --loglevel info
```

После запуска появится баннер Scrapling. Можно сразу начинать сбор данных, как в видео выше:

```python
# No imports needed - everything is ready!
get('https://news.ycombinator.com')

# Explore the page structure
page.css('a')[:5]  # Look at first 5 links

# Refine your selectors
stories = page.css('.titleline>a')
len(stories)  # 30

# Extract specific data
for story in stories[:3]:
    title = story.text
    url = story['href']
    print(f"{title}: {url}")

# Try different approaches
titles = page.css('.titleline>a::text')  # Direct text extraction
urls = page.css('.titleline>a::attr(href)')  # Direct attribute extraction
```

## Встроенные сокращения {#built-in-shortcuts}

Оболочка предоставляет сокращения, чтобы не писать повторяющийся код:

- **`get(url, **kwargs)`**: HTTP GET-запрос вместо `Fetcher.get`.
- **`post(url, **kwargs)`**: HTTP POST-запрос вместо `Fetcher.post`.
- **`put(url, **kwargs)`**: HTTP PUT-запрос вместо `Fetcher.put`.
- **`delete(url, **kwargs)`**: HTTP DELETE-запрос вместо `Fetcher.delete`.
- **`fetch(url, **kwargs)`**: загрузка через скрытный браузер вместо `StealthyFetcher.fetch`.

Часто используемые классы уже доступны без импорта, в том числе `Fetcher`, `AsyncFetcher`, `StealthyFetcher` и `Selector`.

### Автоматическое управление страницами {#smart-page-management}

Оболочка автоматически отслеживает запросы и страницы:

- **Доступ к текущей странице**

    `page` и `response` автоматически обновляются и содержат последнюю загруженную страницу:
    
    ```python
    get('https://quotes.toscrape.com')
    # 'page' and 'response' both refer to the last fetched page
    page.url  # 'https://quotes.toscrape.com'
    response.status  # Prints 200; Same as page.status
    ```

- **История страниц**

    `pages` хранит последние пять страниц в объекте `Selectors`:
    
    ```python
    get('https://site1.com')
    get('https://site2.com')
    get('https://site3.com')
    
    # Access last 5 pages
    len(pages)  # `Selectors` object with `page` history -> 3
    pages[0].url  # First page in history -> 'https://site1.com'
    pages[-1].url  # Most recent page -> 'https://site3.com'
    
    # Work with historical pages
    for i, old_page in enumerate(pages):
        print(f"Page {i}: {old_page.url} - {old_page.status}")
    ```

## Другие полезные команды {#additional-helpful-commands}

### Просмотр страницы {#page-visualization}

Откройте загруженную страницу в браузере:

```python
get('https://quotes.toscrape.com')
view(page)  # Opens the page HTML in your default browser
```

### Работа с командами curl {#curl-command-integration}

Для преобразования команд curl из DevTools браузера в запросы `Fetcher` есть функции `uncurl` и `curl2fetcher`.

Сначала скопируйте запрос как команду curl:

<img src="../assets/scrapling_shell_curl.png" title="Копирование запроса из Chrome в виде команды curl" alt="Копирование запроса из Chrome в виде команды curl" style="width: 70%;"/>

- **Преобразование команды curl в объект Request**

    ```python
    curl_cmd = '''curl 'https://scrapling.requestcatcher.com/post' \
      -X POST \
      -H 'Content-Type: application/json' \
      -d '{"name": "test", "value": 123}' '''
    
    request = uncurl(curl_cmd)
    request.method  # -> 'post'
    request.url  # -> 'https://scrapling.requestcatcher.com/post'
    request.headers  # -> {'Content-Type': 'application/json'}
    ```

- **Прямое выполнение команды curl**

    ```python
    # Convert and execute in one step
    curl2fetcher(curl_cmd)
    page.status  # -> 200
    ```

### Возможности IPython {#ipython-features}

Оболочка поддерживает все возможности IPython:

```python
# Magic commands
%time page = get('https://example.com')  # Time execution
%history  # Show command history
%save filename.py 1-10  # Save commands 1-10 to file

# Tab completion works everywhere
page.c<TAB>  # Shows: css, cookies, headers, etc.
Fetcher.<TAB>  # Shows all Fetcher methods

# Object inspection
get? # Show get documentation
```

## Примеры {#examples}

Несколько примеров, созданных с помощью ИИ:

#### Сбор данных интернет-магазина {#e-commerce-data-collection}

```python
# Start with product listing page
catalog = get('https://shop.example.com/products')

# Find product links
product_links = catalog.css('.product-link::attr(href)').getall()
print(f"Found {len(product_links)} products")

# Sample a few products first
for link in product_links[:3]:
    product = get(catalog.urljoin(link))
    name = product.css('.product-name::text').get('')
    price = product.css('.price::text').get('')
    print(f"{name}: {price}")

# Scale up with sessions for efficiency
from scrapling.fetchers import FetcherSession
with FetcherSession() as session:
    products = []
    for link in product_links:
        product = session.get(catalog.urljoin(link))
        products.append({
            'name': product.css('.product-name::text').get(''),
            'price': product.css('.price::text').get(''),
            'url': link
        })
```

#### Интеграция и проверка API {#api-integration-and-testing}

```python
>>> # Test API endpoints interactively
>>> response = get('https://jsonplaceholder.typicode.com/posts/1')
>>> response.json()
{'userId': 1, 'id': 1, 'title': 'sunt aut...', 'body': 'quia et...'}

>>> # Test POST requests
>>> new_post = post('https://jsonplaceholder.typicode.com/posts', 
...                 json={'title': 'Test Post', 'body': 'Test content', 'userId': 1})
>>> new_post.json()['id']
101

>>> # Test with different data
>>> updated = put('https://jsonplaceholder.typicode.com/posts/1',
...               json={'title': 'Updated Title'})
```

## Помощь {#getting-help}

Если встроенной справки терминала недостаточно, используйте:

- [Документацию Scrapling](https://scrapling.readthedocs.io/ru/latest/)
- [Сообщество в Discord](https://discord.gg/EMgGbDceNQ)
- [GitHub Issues](https://github.com/D4Vinci/Scrapling/issues)

На этом всё. Удачного сбора данных! Оболочка позволяет работать с сайтами так же просто, как вести беседу.
