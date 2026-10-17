---
title: "Переход с BeautifulSoup на Scrapling"
description: "Сравните выбор элементов, работу с текстом, атрибутами и навигацией в BeautifulSoup и Scrapling. Изучите различия API на практических примерах."
---

# Переход с BeautifulSoup на Scrapling {#migrating-from-beautifulsoup-to-scrapling}

Если вы уже знакомы с BeautifulSoup, освоить Scrapling будет легко. Scrapling работает заметно быстрее, предоставляет те же возможности парсинга и добавляет новые. В нём также есть инструменты загрузки и обработки современных веб-страниц. Это руководство поможет быстро перенести существующий код BeautifulSoup на Scrapling.

В таблице ниже собраны распространённые операции при сборе данных. Каждая строка показывает, как выполнить задачу в BeautifulSoup и как сделать то же в Scrapling.

Некоторых сокращённых записей BeautifulSoup в Scrapling нет. Это одна из причин, по которым Scrapling быстрее. Если функцию уже можно вызвать одной короткой строкой, нет смысла жертвовать скоростью, чтобы сделать эту строку ещё короче :)


| Задача | Код BeautifulSoup | Код Scrapling |
|-----------------------------------------------------------------|---------------------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------|
| Импорт парсера | `from bs4 import BeautifulSoup`                                                                               | `from scrapling.parser import Selector`                                           |
| Парсинг HTML из строки | `soup = BeautifulSoup(html, 'html.parser')`                                                                   | `page = Selector(html)`                                                           |
| Поиск одного элемента | `element = soup.find('div', class_='example')`                                                                | `element = page.find('div', class_='example')`                                    |
| Поиск нескольких элементов | `elements = soup.find_all('div', class_='example')`                                                           | `elements = page.find_all('div', class_='example')`                               |
| Поиск одного элемента (пример 2) | `element = soup.find('div', attrs={"class": "example"})`                                                      | `element = page.find('div', {"class": "example"})`                                |
| Поиск одного элемента (пример 3) | `element = soup.find(re.compile("^b"))`                                                                       | `element = page.find(lambda e: re.search(r"^b", e.tag) is not None)` |
| Поиск одного элемента (пример 4) | `element = soup.find(lambda e: len(list(e.children)) > 0)`                                                    | `element = page.find(lambda e: len(e.children) > 0)`                              |
| Поиск одного элемента (пример 5) | `element = soup.find(["a", "b"])`                                                                             | `element = page.find(["a", "b"])`                                                 |
| Поиск элемента по тексту | `element = soup.find(text="some text")`                                                                       | `element = page.find_by_text("some text", partial=False)`                         |
| Поиск первого совпадения с CSS-селектором | `elements = soup.select_one('div.example')`                                                                   | `elements = page.css('div.example').first`                                        |
| Поиск всех совпадений с CSS-селектором | `elements = soup.select('div.example')`                                                                       | `elements = page.css('div.example')`                                              |
| Получение отформатированного исходного кода страницы или элемента | `prettified = soup.prettify()`                                                                                | `prettified = page.prettify()`                                                    |
| Получение исходного кода страницы или элемента без форматирования | `source = str(soup)`                                                                                          | `source = page.html_content`                                                      |
| Получение имени тега элемента | `name = element.name`                                                                                         | `name = element.tag`                                                              |
| Извлечение текста элемента | `string = element.string`                                                                                     | `string = element.text`                                                           |
| Извлечение всего текста документа или содержимого тега | `text = soup.get_text(strip=True)`                                                                            | `text = page.get_all_text(strip=True)`                                            |
| Доступ к словарю атрибутов | `attrs = element.attrs`                                                                                       | `attrs = element.attrib`                                                          |
| Извлечение атрибутов | `attr = element['href']`                                                                                      | `attr = element['href']`                                                          |
| Переход к родителю | `parent = element.parent`                                                                                     | `parent = element.parent`                                                         |
| Получение всех предков элемента | `parents = list(element.parents)`                                                                             | `parents = list(element.iterancestors())`                                         |
| Поиск элемента среди предков | `target_parent = element.find_parent("a")`                                                                    | `target_parent = element.find_ancestor(lambda p: p.tag == 'a')`                   |
| Получение всех соседних элементов | Нет аналога                                                                                                           | `siblings = element.siblings`                                                     |
| Получение следующего соседнего элемента | `next_element = element.next_sibling`                                                                         | `next_element = element.next`                                                     |
| Поиск одного элемента среди соседних | `target_sibling = element.find_next_sibling("a")`<br/>`target_sibling = element.find_previous_sibling("a")`   | `target_sibling = element.siblings.search(lambda s: s.tag == 'a')`                |
| Поиск нескольких элементов среди соседних | `target_sibling = element.find_next_siblings("a")`<br/>`target_sibling = element.find_previous_siblings("a")` | `target_sibling = element.siblings.filter(lambda s: s.tag == 'a')`                |
| Поиск одного элемента среди последующих | `target_parent = element.find_next("a")`                                                                      | `target_parent = element.below_elements.search(lambda p: p.tag == 'a')`           |
| Поиск нескольких элементов среди последующих | `target_parent = element.find_all_next("a")`                                                                  | `target_parent = element.below_elements.filter(lambda p: p.tag == 'a')`           |
| Поиск одного элемента среди предков | `target_parent = element.find_previous("a")` ¹                                                                | `target_parent = element.path.search(lambda p: p.tag == 'a')`                     |
| Поиск нескольких элементов среди предков | `target_parent = element.find_all_previous("a")` ¹                                                            | `target_parent = element.path.filter(lambda p: p.tag == 'a')`                     |
| Получение предыдущего соседнего элемента | `prev_element = element.previous_sibling`                                                                     | `prev_element = element.previous`                                                 |
| Переход к дочерним элементам | `children = list(element.children)`                                                                           | `children = element.children`                                                     |
| Получение всех потомков | `children = list(element.descendants)`                                                                        | `children = element.below_elements`                                               |
| Выбор ссылок внутри абзацев с классом story | `group = soup.select('p.story a')`                                                             | `group = page.css('p.story a')`              |

Если передать скомпилированное регулярное выражение прямо в `find()` или `find_all()` Scrapling, оно будет проверять текст элемента, а не имя тега. Для имён тегов используйте lambda из таблицы, а для поиска по тексту можно напрямую вызвать `page.find_by_regex(r"^b")`.

¹ **Примечание:** `find_previous`/`find_all_previous` в BS4 ищут среди всех предыдущих элементов в порядке документа. `path` в Scrapling возвращает только предков, то есть цепочку родителей. Это не полные аналоги, но поиск по предкам покрывает наиболее частый случай.

**Важный момент**: BeautifulSoup позволяет изменять страницу после парсинга. Scrapling сосредоточен на быстром сборе данных, а с извлечённой информацией вы можете работать как угодно. Оба инструмента подходят для веб-скрейпинга, но Scrapling специализируется именно на нём :)

### Полный пример {#putting-it-all-together}

Простой пример извлечения всех ссылок со страницы с помощью BeautifulSoup и Scrapling.

**С BeautifulSoup:**

```python
import requests
from bs4 import BeautifulSoup

url = 'https://example.com'
response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')

links = soup.find_all('a')
for link in links:
    print(link['href'])
```

**Со Scrapling:**

```python
from scrapling import Fetcher

url = 'https://example.com'
page = Fetcher.get(url)

links = page.css('a::attr(href)').getall()
for link in links:
    print(link)
```

Scrapling объединяет загрузку и парсинг в один шаг. Это делает код короче и эффективнее.

!!! abstract "**Дополнительные примечания:**"

    - **Разные парсеры**: BeautifulSoup позволяет выбрать движок, в том числе `lxml`. Scrapling не переключает движки и по умолчанию использует `lxml` ради скорости.
    - **Типы элементов**: в BeautifulSoup элементы представлены объектами `Tag`, а в Scrapling объектами `Selector`. При этом у них похожие методы и свойства для навигации и извлечения данных.
    - **Обработка ошибок**: обе библиотеки возвращают `None`, если элемент не найден, например в `soup.find()` или `page.find()`. В Scrapling `page.css()` возвращает пустой список `Selectors`, если совпадений нет. `page.css('.foo').first` безопасно возвращает первое совпадение или `None`. Чтобы избежать ошибок, перед доступом к свойствам проверяйте, что результат не равен `None` и не пуст.
    - **Извлечение текста**: `TextHandler` в Scrapling предоставляет дополнительные методы работы с текстом. Например, `clean()` помогает удалять лишние пробельные символы, повторяющиеся пробелы и ненужные символы. Полный список есть в документации.

В документации подробно описаны возможности Scrapling и все аргументы его методов.

Надеюсь, это руководство упростит переход с BeautifulSoup на Scrapling. Удачного сбора данных!
