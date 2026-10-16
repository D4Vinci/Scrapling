---
title: "Selector и Selectors в Scrapling: данные и навигация"
description: "Узнайте, как Selector и Selectors хранят HTML, текст и атрибуты. Извлекайте значения, преобразуйте URL и переходите к родителям, дочерним и соседним элементам."
---

# Основные классы парсера {#parsing-main-classes}

!!! success "Перед началом"

    - Прочитайте страницу [Поиск элементов](../parsing/selection.md), чтобы понять, как находить и извлекать элементы из объекта [Selector](../parsing/main_classes.md#selector).

Теперь, когда мы рассмотрели способы выбора элементов в Scrapling, разберём класс [Selector](#selector) и связанные объекты. Это поможет лучше понять работу парсера.

Класс [Selector](#selector) составляет основу парсера Scrapling: он разбирает HTML и позволяет выбирать элементы. Его можно импортировать любым из следующих способов:
```python
from scrapling import Selector
from scrapling.parser import Selector
```
Затем используйте его напрямую, как показано на странице [Обзор](../overview.md):
```python
page = Selector(
    '<html>...</html>',
    url='https://example.com'
)

# Then select elements as you like
elements = page.css('.product')
```
После передачи HTML или получения страницы основным объектом в Scrapling становится [Selector](#selector). Выбор элементов, навигация и другие операции возвращают объект [Selector](#selector) или [Selectors](#selectors), если результатом является один или несколько элементов страницы, а не текст или подобные данные.

Другими словами, сама страница является объектом [Selector](#selector), и каждый её элемент тоже является объектом [Selector](#selector). Любой текст, включая содержимое элементов и значения их атрибутов, представлен объектом [TextHandler](#texthandler). Атрибуты каждого элемента хранятся в [AttributesHandler](#attributeshandler). К этим двум объектам мы вернёмся позже, а пока рассмотрим [Selector](#selector).

## Selector {#selector}
### Аргументы {#arguments-explained}
Самый важный аргумент, `content`, принимает HTML для разбора в виде `str` или `bytes`.

Аргумент `url` задаёт URL страницы для преобразования относительных ссылок и разделения сохранённых адаптивных данных по доменам. Аргументы `adaptive`, `storage` и `storage_args` относятся к [адаптивной функции](adaptive.md) и не влияют на работу, если вы её не используете.

Следующие аргументы управляют разбором и обработкой HTML:

- **encoding**: кодировка HTML. По умолчанию `UTF-8`.
- **keep_comments**: сохранять ли HTML-комментарии при разборе страницы. По умолчанию выключено, так как комментарии могут мешать сбору данных.

Я намеренно пропустил аргументы `huge_tree` и `root`, чтобы не усложнять эту страницу.
Возможно, вы заметили, что я часто так поступаю с расширенными возможностями, которые не нужны для начала работы. Подробнее о них можно узнать в разделе разработки.

Большинство свойств страницы и её элементов загружаются только при первом обращении. Например, текст страницы или элемента обрабатывается, когда он вам понадобится. Это одна из причин высокой скорости Scrapling :)

### Свойства {#properties}
Многое из этого уже было на странице [Обзор](../overview.md), но здесь мы разберём свойства подробнее и рассмотрим более сложные примеры. Свойства для перемещения по элементам вынесены в раздел [Навигация](#traversal).

Для примера разберём такую HTML-страницу:
```html
<html>
  <head>
    <title>Some page</title>
  </head>
  <body>
    <div class="product-list">
      <article class="product" data-id="1">
        <h3>Product 1</h3>
        <p class="description">This is product 1</p>
        <span class="price">$10.99</span>
        <div class="hidden stock">In stock: 5</div>
      </article>
    
      <article class="product" data-id="2">
        <h3>Product 2</h3>
        <p class="description">This is product 2</p>
        <span class="price">$20.99</span>
        <div class="hidden stock">In stock: 3</div>
      </article>
    
      <article class="product" data-id="3">
        <h3>Product 3</h3>
        <p class="description">This is product 3</p>
        <span class="price">$15.99</span>
        <div class="hidden stock">Out of stock</div>
      </article>
    </div>

    <script id="page-data" type="application/json">
      {
        "lastUpdated": "2024-09-22T10:30:00Z",
        "totalProducts": 3
      }
    </script>
  </body>
</html>
```
Загрузим страницу, как показано ранее:
```python
from scrapling import Selector
page = Selector(html_doc)
```
Получим весь текст страницы, включая вложенные элементы:
```python
>>> page.get_all_text()
'Some page\n\n    \n\n      \nProduct 1\nThis is product 1\n$10.99\nIn stock: 5\nProduct 2\nThis is product 2\n$20.99\nIn stock: 3\nProduct 3\nThis is product 3\n$15.99\nOut of stock'
```
Получим первый элемент article и используем его в примерах:
```python
article = page.find('article')
```
Таким же способом получим весь текст элемента, включая вложенные элементы:
```python
>>> article.get_all_text()
'Product 1\nThis is product 1\n$10.99\nIn stock: 5'
```
Но если запросить только непосредственный текст элемента, результат будет пустым: в HTML выше у него нет собственного текста.
```python
>>> article.text
''
```
Метод `get_all_text` принимает следующие необязательные аргументы:

1. **separator**: разделитель для объединения найденных строк. По умолчанию '\n'.
2. **strip**: удалять пробельные символы по краям строк перед объединением. По умолчанию выключено.
3. **ignore_tags**: кортеж имён тегов, которые нужно пропустить вместе со всем вложенным содержимым. По умолчанию `('script', 'style',)`.
4. **valid_values**: собирать только элементы с непустым текстом. Пустой текст и текст только из пробельных символов пропускаются. По умолчанию включено.

Возвращаемый текст имеет тип [TextHandler](#texthandler), а не обычной строки. Позже мы разберём его подробнее. Если текст содержит JSON, его можно преобразовать методом `.json()`:
```python
>>> script = page.find('script')
>>> script.json()
{'lastUpdated': '2024-09-22T10:30:00Z', 'totalProducts': 3}
```
Теперь получим имя тега элемента:
```python
>>> article.tag
'article'
```
Если обратиться к этому свойству у самой страницы, вы увидите, что работаете с корневым элементом `html`:
```python
>>> page.tag
'html'
```
Думаю, связь между `page` и `element` теперь понятна, поэтому больше не будем к ней возвращаться.

Получим атрибуты элемента:
```python
>>> print(article.attrib)
{'class': 'product', 'data-id': '1'}
```
К отдельному атрибуту можно обратиться любым из этих способов:
```python
article.attrib['class']
article.attrib.get('class')
article['class']  # new in v0.3
```
Проверить наличие атрибута можно так:
```python
'class' in article.attrib
'class' in article  # new in v0.3
```
Получим HTML элемента:
```python
>>> article.html_content
'<article class="product" data-id="1"><h3>Product 1</h3>\n        <p class="description">This is product 1</p>\n        <span class="price">$10.99</span>\n        <div class="hidden stock">In stock: 5</div>\n      </article>'
```
Получим красиво отформатированный HTML элемента:
```python
print(article.prettify())
```
```html
<article class="product" data-id="1"><h3>Product 1</h3>
    <p class="description">This is product 1</p>
    <span class="price">$10.99</span>
    <div class="hidden stock">In stock: 5</div>
</article>
```
Свойство `.body` возвращает исходное содержимое страницы. Начиная с v0.4, у объектов `Response`, полученных через Fetcher, `.body` всегда возвращает `bytes`.
```python
>>> page.body
'<html>\n  <head>\n    <title>Some page</title>\n  </head>\n  ...'
```
Получим всех предков элемента в дереве DOM:
```python
>>> article.path
[<data='<div class="product-list"> <article clas...' parent='<body> <div class="product-list"> <artic...'>,
 <data='<body> <div class="product-list"> <artic...' parent='<html><head><title>Some page</title></he...'>,
 <data='<html><head><title>Some page</title></he...'>]
```
Создадим сокращённый CSS-селектор, если это возможно, или полный селектор:
```python
>>> article.generate_css_selector
'body > div > article'
>>> article.generate_full_css_selector
'body > div > article'
```
То же самое для XPath:
```python
>>> article.generate_xpath_selector
"//body/div/article"
>>> article.generate_full_xpath_selector
"//body/div/article"
```

### Навигация {#traversal}
На найденных выше элементах подробно рассмотрим свойства и методы для перемещения по странице.

Если вы не знакомы с деревом DOM или структурой данных «дерево», этот раздел может быть непонятен. Советую сначала прочитать об этих понятиях.

А если хотите сразу продолжить, вот краткое объяснение.<br/>
Элемент `html` является корнем дерева сайта: каждая страница начинается с элемента `html`.<br/>
Непосредственно под ним находятся такие элементы, как `head` и `body`. Они считаются дочерними элементами `html`, а `html` является их родителем. Элементы `body` и `head` считаются соседними, так как у них один родитель.

Получим родителя элемента:
```python
>>> article.parent
<data='<div class="product-list"> <article clas...' parent='<body> <div class="product-list"> <artic...'>
>>> article.parent.tag
'div'
```
Обращения можно объединять в цепочки. Это относится и к остальным похожим свойствам и методам ниже.
```python
>>> article.parent.parent.tag
'body'
```
Получим дочерние элементы:
```python
>>> article.children
[<data='<h3>Product 1</h3>' parent='<article class="product" data-id="1"><h3...'>,
 <data='<p class="description">This is product 1...' parent='<article class="product" data-id="1"><h3...'>,
 <data='<span class="price">$10.99</span>' parent='<article class="product" data-id="1"><h3...'>,
 <data='<div class="hidden stock">In stock: 5</d...' parent='<article class="product" data-id="1"><h3...'>]
```
Получим все элементы ниже текущего, включая вложенные. Это похоже на свойство `children`, но для всех уровней вложенности:
```python
>>> article.below_elements
[<data='<h3>Product 1</h3>' parent='<article class="product" data-id="1"><h3...'>,
 <data='<p class="description">This is product 1...' parent='<article class="product" data-id="1"><h3...'>,
 <data='<span class="price">$10.99</span>' parent='<article class="product" data-id="1"><h3...'>,
 <data='<div class="hidden stock">In stock: 5</d...' parent='<article class="product" data-id="1"><h3...'>]
```
Здесь результат совпадает со свойством `children`, потому что у дочерних элементов нет своих дочерних элементов.

Пример с элементом класса `product-list` лучше показывает разницу между `children` и `below_elements`:
```python
>>> products_list = page.css('.product-list')[0]
>>> products_list.children
[<data='<article class="product" data-id="1"><h3...' parent='<div class="product-list"> <article clas...'>,
 <data='<article class="product" data-id="2"><h3...' parent='<div class="product-list"> <article clas...'>,
 <data='<article class="product" data-id="3"><h3...' parent='<div class="product-list"> <article clas...'>]

>>> products_list.below_elements
[<data='<article class="product" data-id="1"><h3...' parent='<div class="product-list"> <article clas...'>,
 <data='<h3>Product 1</h3>' parent='<article class="product" data-id="1"><h3...'>,
 <data='<p class="description">This is product 1...' parent='<article class="product" data-id="1"><h3...'>,
 <data='<span class="price">$10.99</span>' parent='<article class="product" data-id="1"><h3...'>,
 <data='<div class="hidden stock">In stock: 5</d...' parent='<article class="product" data-id="1"><h3...'>,
 <data='<article class="product" data-id="2"><h3...' parent='<div class="product-list"> <article clas...'>,
...]
```
Получим соседние элементы с тем же родителем:
```python
>>> article.siblings
[<data='<article class="product" data-id="2"><h3...' parent='<div class="product-list"> <article clas...'>,
 <data='<article class="product" data-id="3"><h3...' parent='<div class="product-list"> <article clas...'>]
```
Получим следующий соседний элемент:
```python
>>> article.next
<data='<article class="product" data-id="2"><h3...' parent='<div class="product-list"> <article clas...'>
```
Свойство `previous` работает аналогично:
```python
>>> article.previous  # It's the first child, so it doesn't have a previous element
>>> second_article = page.css('.product[data-id="2"]')[0]
>>> second_article.previous
<data='<article class="product" data-id="1"><h3...' parent='<div class="product-list"> <article clas...'>
```
Можно быстро проверить, есть ли у элемента определённый класс:
```python
>>> article.has_class('product')
True
```
Если одного родителя недостаточно, можно перебрать всех предков элемента:
```python
for ancestor in article.iterancestors():
    # do something with it...
```
Также можно найти предка, который удовлетворяет условию. Передайте функцию, которая принимает объект [Selector](#selector) и возвращает `True`, если условие выполнено, или `False` в противном случае:
```python
>>> article.find_ancestor(lambda ancestor: ancestor.has_class('product-list'))
<data='<div class="product-list"> <article clas...' parent='<body> <div class="product-list"> <artic...'>

>>> article.find_ancestor(lambda ancestor: ancestor.css('.product-list'))  # Same result, different approach
<data='<div class="product-list"> <article clas...' parent='<body> <div class="product-list"> <artic...'>
```
## Selectors {#selectors}
Класс `Selectors` представляет список объектов [Selector](#selector). Он наследует стандартный тип Python `List`, поэтому содержит все свойства и методы `List`, а также дополнительные методы для удобной работы с объектами [Selector](#selector) внутри него.

Все методы и свойства [Selector](#selector), которые возвращают несколько элементов, возвращают экземпляр [Selectors](#selectors).

Начиная с v0.4, все методы выбора возвращают объекты [Selector](#selector)/[Selectors](#selectors), даже для текстовых узлов и значений атрибутов. Текстовые узлы, выбранные через `::text`, `/text()`, `::attr()` или `/@attr`, оборачиваются в объекты [Selector](#selector). У них `tag` равен `"#text"`, а свойство `text` возвращает текстовое значение. Текст по-прежнему доступен напрямую, а остальные свойства возвращают пустые значения или значения по умолчанию.

```python
page.css('a::text')              # -> Selectors (of text node Selectors)
page.xpath('//a/text()')         # -> Selectors
page.css('a::text').get()        # -> TextHandler (the first text value)
page.css('a::text').getall()     # -> TextHandlers (all text values)
page.css('a::attr(href)')        # -> Selectors
page.xpath('//a/@href')          # -> Selectors
page.css('.price_color')         # -> Selectors
```

### Методы извлечения данных {#data-extraction-methods}
Начиная с v0.4, [Selector](#selector) и [Selectors](#selectors) предоставляют методы `get()`, `getall()` и их псевдонимы `extract_first` и `extract`, как в Scrapy. Старый метод `get_all()` удалён.

**У объекта [Selector](#selector):**

- `get()` возвращает `TextHandler`: для текстовых узлов это текстовое значение, для HTML-элементов это строка с внешним HTML элемента.
- `getall()` возвращает список `TextHandlers` с одной строкой представления элемента.
- `extract_first` является псевдонимом `get()`, а `extract` является псевдонимом `getall()`.

```python
>>> page.css('h3')[0].get()        # Outer HTML of the element
'<h3>Product 1</h3>'

>>> page.css('h3::text')[0].get()  # Text value of the text node
'Product 1'
```

**У объекта [Selectors](#selectors):**

- `get(default=None)` возвращает строковое представление **первого** элемента или `default`, если список пуст.
- `getall()` преобразует **все** элементы в строки и возвращает список `TextHandlers`.
- `extract_first` является псевдонимом `get()`, а `extract` является псевдонимом `getall()`.

```python
>>> page.css('.price::text').get()      # First price text
'$10.99'

>>> page.css('.price::text').getall()   # All price texts
['$10.99', '$20.99', '$15.99']

>>> page.css('.price::text').get('')    # With default value
'$10.99'
```

Эти методы работают со всеми способами выбора: CSS, XPath, `find` и другими. Это рекомендуемый способ извлекать текст и значения атрибутов в стиле Scrapy.

Теперь посмотрим, какие ещё возможности добавляет класс [Selectors](#selectors).
### Свойства {#properties_1}
Помимо обычных операций со списками Python, таких как перебор и срезы, доступны следующие возможности:

Можно выполнять CSS- и XPath-запросы прямо для содержащихся в списке объектов [Selector](#selector). Типы результатов такие же, как у методов `css` и `xpath` класса [Selector](#selector). Аргументы тоже совпадают, кроме отсутствующего здесь `adaptive`. Благодаря этому методы легко объединять в цепочки.
```pycon
>>> page.css('.product h3::text').getall()
['Product 1', 'Product 2', 'Product 3']
>>> page.css('.product').css('h3::text').getall()
['Product 1', 'Product 2', 'Product 3']
```
Можно напрямую вызывать `re` и `re_first`. Они принимают те же аргументы, что и в классе [Selector](#selector). Подробнее о них читайте ниже в разделе [TextHandler](#texthandler).

Однако здесь `re_first` работает иначе: вызывает `re` для каждого [Selector](#selector) и возвращает первый найденный результат. Метод `re` возвращает обычный объект [TextHandlers](#texthandlers), объединяя все экземпляры [TextHandler](#texthandler) в один [TextHandlers](#texthandlers).
```pycon
>>> page.css('.price::text').re(r'[\d.]+')
['10.99', '20.99', '15.99']
>>> page.css('.product h3::text').re(r'Product (\d+)')
['1', '2', '3']
```
Метод `search` позволяет быстро искать среди объектов [Selector](#selector). Переданная функция должна принимать [Selector](#selector) первым аргументом и возвращать True/False. Метод вернёт первый [Selector](#selector), для которого условие выполнено, или `None`, если совпадений нет.

```pycon
>>> product = page.css('.product').search(lambda p: p.css('.price::text').get() == '$20.99')
>>> product.css('h3::text').get()
'Product 2'
```
Метод `filter` тоже принимает функцию, как `search`, но возвращает объект `Selectors` со всеми экземплярами [Selector](#selector), которые удовлетворяют условию.

```pycon
>>> products = page.css('.product').filter(lambda p: float(p.css('.price::text').re_first(r'[\d.]+')) > 15)
>>> products.css('h3::text').getall()
['Product 2', 'Product 3']
```
К первому и последнему элементу можно безопасно обращаться без риска ошибки индекса:
```python
>>> page.css('.product').first   # First Selector or None
<data='<article class="product" data-id="1"><h3...'>
>>> page.css('.product').last    # Last Selector or None
<data='<article class="product" data-id="3"><h3...'>
>>> page.css('.nonexistent').first  # Returns None instead of raising IndexError
```

Если вам, как и мне, хочется короче записать число объектов [Selector](#selector) в [Selectors](#selectors), можно сделать так:
```python
page.css('.product').length
```
Это равнозначно следующей записи:
```python
len(page.css('.product'))
```
Да, как в JavaScript :)

## TextHandler {#texthandler}
Этот класс важно знать: все методы и свойства, которые должны вернуть строку, возвращают `TextHandler`. А вместо списка строк они возвращают [TextHandlers](#texthandlers).

TextHandler наследует стандартную строку Python, поэтому поддерживает все обычные операции со строками. Зачем тогда отдельное имя?

TextHandler добавляет методы и свойства, которых нет у стандартных строк Python. Мы сейчас их рассмотрим. Помните, что все классы возвращают строки как TextHandler. Это позволяет писать более короткий и удобный код. Можно также импортировать класс и применять его к любой строке, как описано [далее](../development/scrapling_custom_types.md).
### Использование {#usage}
Срезы, доступ по индексу и методы вроде `split`, `replace` и `strip` снова возвращают `TextHandler`. Поэтому их можно объединять в цепочки. Если найдёте метод или свойство, которое возвращает обычную строку вместо `TextHandler`, создайте issue, и мы исправим его.

Начнём с методов `re` и `re_first`. Они есть и в классах [Selector](#selector), [Selectors](#selectors) и [TextHandlers](#texthandlers) и везде принимают одинаковые аргументы.

- Метод `re` принимает первым аргументом строку или скомпилированное регулярное выражение. Он находит все совпадения и возвращает их как [TextHandlers](#texthandlers). Метод `re_first` принимает те же аргументы и работает похожим образом, но возвращает только первый результат как `TextHandler`.
    
    Есть и другие полезные аргументы:
    
    - **replace_entities**: по умолчанию включён. Заменяет HTML-сущности соответствующими символами.
    - **clean_match**: по умолчанию выключен. Позволяет игнорировать пробельные символы, в том числе последовательности пробелов, при поиске совпадений.
    - **case_sensitive**: по умолчанию включён. При отключении регулярное выражение компилируется без учёта регистра.
  
    Вы уже видели эти примеры. Результат имеет тип [TextHandlers](#texthandlers), так как мы использовали `re`.
    ```pycon
    >>> page.css('.price::text').re(r'[\d.]+')
    ['10.99', '20.99', '15.99']
    >>> page.css('.product h3::text').re(r'Product (\d+)')
    ['1', '2', '3']
    ```
    Чтобы показать остальные аргументы, возьмём отдельную строку для каждого примера:
    ```python
    >>> from scrapling import TextHandler
    >>> test_string = TextHandler('hi  there')  # Hence the two spaces
    >>> test_string.re('hi there')
    >>> test_string.re('hi there', clean_match=True)  # Using `clean_match` will clean the string before matching the regex
    ['hi there']
    
    >>> test_string2 = TextHandler('Oh, Hi Mark')
    >>> test_string2.re_first('oh, hi Mark')
    >>> test_string2.re_first('oh, hi Mark', case_sensitive=False)  # Hence disabling `case_sensitive`
    'Oh, Hi Mark'
    
    # Mixing arguments
    >>> test_string.re('hi there', clean_match=True, case_sensitive=False)
    ['hi there']
    ```
    Ещё одно преимущество использования `TextHandler`: свойство `html_content` тоже возвращает `TextHandler`, поэтому можно искать регулярным выражением прямо в HTML:
    ```python
    >>> page.html_content.re('div class=".*">(.*)</div')
    ['In stock: 5', 'In stock: 3', 'Out of stock']
    ```

- Метод `.json()` быстро преобразует содержимое в объект JSON, если это возможно. Иначе он вызывает ошибку.
  ```python
  >>> page.css('#page-data::text').get()
    '\n      {\n        "lastUpdated": "2024-09-22T10:30:00Z",\n        "totalProducts": 3\n      }\n    '
  >>> page.css('#page-data::text').get().json()
    {'lastUpdated': '2024-09-22T10:30:00Z', 'totalProducts': 3}
  ```
  Если при выборе элемента вы не указали текстовый узел, например текст элемента или значение атрибута, текст элемента будет выбран автоматически:
  ```python
  >>> page.css('#page-data')[0].json()
  {'lastUpdated': '2024-09-22T10:30:00Z', 'totalProducts': 3}
  ```
  Класс [Selector](#selector) добавляет ещё одну возможность. Допустим, мы работаем с такой страницей:
  ```html
  <html>
      <body>
          <div>
            <script id="page-data" type="application/json">
              {
                "lastUpdated": "2024-09-22T10:30:00Z",
                "totalProducts": 3
              }
            </script>
          </div>
      </body>
  </html>
  ```
  У класса [Selector](#selector) есть уже знакомый метод `get_all_text`, который возвращает `TextHandler`.<br/><br/>
  Если выполнить следующее:
  ```python
  >>> page.css('div::text').get().json()
  ```
  Возникнет ошибка: у тега `div` нет собственного текста, который можно преобразовать в JSON. У него вообще нет непосредственного текстового содержимого.<br/><br/>
  В этом случае поможет метод `get_all_text`:
  ```python
  >>> page.css('div')[0].get_all_text(ignore_tags=[]).json()
    {'lastUpdated': '2024-09-22T10:30:00Z', 'totalProducts': 3}
  ```
  Здесь я указал `ignore_tags`, потому что его значение по умолчанию равно `('script', 'style',)`.<br/><br/>
  Ещё один связанный случай возникает при работе с Fetcher, которые мы рассмотрим позже. Допустим, вы получили такой JSON-ответ:
  ```python
  >>> page = Selector("""{"some_key": "some_value"}""")
  ```
  Класс [Selector](#selector) предназначен для HTML-страниц. Он воспринимает такой ответ как повреждённый HTML и исправляет его. Поэтому свойство `html_content` вернёт следующее:
  ```python
  >>> page.html_content
  '<html><body><p>{"some_key": "some_value"}</p></body></html>'
  ```
  При этом метод `json` можно вызвать напрямую, и он сработает:
  ```python
  >>> page.json()
  {'some_key': 'some_value'}
  ```
  Как это возможно, если у тега `html` нет непосредственного текста?<br/>
  Для таких случаев, как JSON-ответы, класс [Selector](#selector) сохраняет исходную копию полученного содержимого. Метод `.json()` сначала проверяет эту копию и преобразует её в JSON. Если копии нет, как у отдельных элементов, он проверяет текст текущего элемента, а затем при необходимости использует `get_all_text`.<br/>

- Полезный метод `.clean()` удаляет пробельные символы и последовательности пробелов и возвращает новый экземпляр `TextHandler`.
```python
>>> TextHandler('\n wonderful  idea, \reh?').clean()
'wonderful idea, eh?'
```
Аргумент `remove_entities` позволяет методу `clean` заменять HTML-сущности соответствующими символами.

- Метод `.sort()` сортирует символы строки, как при сортировке списка:
```python
>>> TextHandler('acb').sort()
'abc'
```
Можно сортировать и в обратном порядке:
```python
>>> TextHandler('acb').sort(reverse=True)
'cba'
```

Со временем появятся и другие методы и свойства. Главное помнить: почти везде в библиотеке этот класс используется вместо обычных строк.

## TextHandlers {#texthandlers}
Как вы, наверное, догадались, этот класс похож на [Selectors](#selectors) и [Selector](#selector), но наследует поведение стандартного списка. Дополнительно он предоставляет методы `re` и `re_first`.

Метод `re_first` здесь вызывает `re` для каждого [TextHandler](#texthandler) и возвращает первый результат или `None`. В остальном новых особенностей пока нет, но позже будут добавлены новые методы.

## AttributesHandler {#attributeshandler}
Это версия стандартного словаря Python, `dict`, доступная только для чтения. Она хранит атрибуты каждого элемента, то есть экземпляра [Selector](#selector).
```python
>>> print(page.find('script').attrib)
{'id': 'page-data', 'type': 'application/json'}
>>> type(page.find('script').attrib).__name__
'AttributesHandler'
```
Благодаря режиму только для чтения этот класс использует меньше ресурсов, чем обычный словарь. При этом у него те же методы и свойства, кроме тех, которые изменяют или перезаписывают данные.

Сейчас он добавляет две простые возможности:

- Метод `search_values`.

    В обычном словаре можно проверить наличие ключа через `dict.get("key_name")`. Но для поиска по значениям нужен дополнительный код. Этот метод делает это за вас: ищет среди значений атрибутов и возвращает словарь для каждого совпадения.
    
    Простой пример:
    ```python
    >>> for i in page.find('script').attrib.search_values('page-data'):
            print(i)
    {'id': 'page-data'}
    ```
    Аргумент `partial` позволяет искать по части значения:
    ```python
    >>> for i in page.find('script').attrib.search_values('page', partial=True):
            print(i)
    {'id': 'page-data'}
    ```
    Предыдущие примеры условны. В реальной задаче метод можно использовать вместе с `find_all`, чтобы найти все элементы с определённым значением атрибута:
    ```python
    >>> page.find_all(lambda element: list(element.attrib.search_values('product')))
    [<data='<article class="product" data-id="1"><h3...' parent='<div class="product-list"> <article clas...'>,
     <data='<article class="product" data-id="2"><h3...' parent='<div class="product-list"> <article clas...'>,
     <data='<article class="product" data-id="3"><h3...' parent='<div class="product-list"> <article clas...'>]
    ```
    У всех этих элементов значение атрибута `class` равно 'product'.
    
    Здесь используется `list`, потому что `search_values` возвращает генератор. Сам генератор дал бы `True` для каждого элемента.

- Свойство `json_string`.

    Преобразует текущие атрибуты в строку JSON, если это возможно. Иначе вызывает ошибку.
  
    ```python
    >>>page.find('script').attrib.json_string
    b'{"id":"page-data","type":"application/json"}'
    ```