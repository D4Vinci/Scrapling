---
title: "Извлечение HTML-данных через CSS, XPath, текст и регулярные выражения"
description: "Выбирайте HTML-элементы с помощью CSS, XPath, текста и регулярных выражений. Находите похожие элементы и извлекайте поля по примерам Scrapling."
---

# Поиск элементов {#querying-elements}
Класс `Selector` разбирает HTML. Это сделано потому, что адаптивная функция не работает с XML. Для лент XML, RSS и Atom используйте [XMLFeedSpider](../spiders/generic-templates.md#xmlfeedspider): он применяет XML-парсер и передаёт вам каждый узел ленты напрямую.

В Scrapling есть пять основных способов поиска элементов:

1. CSS3-селекторы.
2. XPath-селекторы.
3. Поиск по фильтрам и условиям.
4. Поиск элементов, содержимое которых содержит заданный текст.
5. Поиск элементов, содержимое которых соответствует регулярному выражению.

Есть и другие, косвенные способы поиска, но здесь мы подробно рассмотрим основные. Также разберём одну из самых полезных возможностей Scrapling: поиск элементов, похожих на уже найденный. К этому разделу можно перейти [сразу](#finding-similar-elements).

Если вы только начинаете собирать данные с сайтов и ещё не умеете писать селекторы, советую начать с методов `find`/`find_all` [здесь](#filters-based-searching).

## CSS/XPath-селекторы {#cssxpath-selectors}

### Что такое CSS-селекторы? {#what-are-css-selectors}
[CSS](https://en.wikipedia.org/wiki/CSS) задаёт стили HTML-документов. Селекторы связывают эти стили с определёнными HTML-элементами.

Scrapling поддерживает CSS3-селекторы по [спецификации W3C](http://www.w3.org/TR/2011/REC-css3-selectors-20110929/). Для этого используется `cssselect`, поэтому список [поддерживаемых селекторов](https://cssselect.readthedocs.io/en/latest/#supported-selectors), псевдофункций и псевдоэлементов лучше смотреть в его документации.

Scrapling также поддерживает несколько нестандартных псевдоэлементов:

* ``::text`` выбирает текстовые узлы.
* ``::attr(name)`` выбирает значения атрибута, где name обозначает имя нужного атрибута.

Если вы работали со Scrapy или Parsel, правила будут знакомыми. Нет смысла менять то, к чему многие из нас уже привыкли :)

Для выбора через CSS используйте метод `css`, который возвращает `Selectors`. Через `[0]` можно получить первый элемент, а через `.get()` / `.getall()` извлечь текст из результатов текстовых селекторов или селекторов атрибутов.

### Что такое XPath-селекторы? {#what-are-xpath-selectors}
[XPath](https://en.wikipedia.org/wiki/XPath) служит для выбора узлов XML-документов и также работает с HTML. Эта [шпаргалка](https://devhints.io/xpath) поможет освоить [XPath](https://en.wikipedia.org/wiki/XPath). Scrapling использует XPath напрямую через [lxml](https://lxml.de/).

Как и с CSS, пользователям Scrapy и Parsel многое будет знакомо. Но Scrapling не реализует их дополнительную XPath-функцию `has-class`. Вместо неё у найденных элементов есть метод `has_class` с тем же назначением.

Для выбора через XPath используйте метод `xpath`. Он работает по тем же правилам, что и описанный выше метод для CSS.

> У методов `css` и `xpath` есть дополнительные аргументы для адаптивной функции. Здесь мы их не разбираем: этой возможности посвящена отдельная страница.

### Примеры селекторов {#selectors-examples}
Рассмотрим одинаковые задачи с CSS и XPath.

Выберем все элементы с классом `product`:
```python
products = page.css('.product')
products = page.xpath('//*[@class="product"]')
```
!!! info "Примечание"

    XPath-вариант не даст точного результата, если у элемента есть ещё один класс. **Для выбора по классу лучше использовать CSS.**

Выберем первый элемент с классом `product`:
```python
product = page.css('.product')[0]
product = page.xpath('//*[@class="product"]')[0]
```
Получим текст первого элемента с тегом `h1`:
```python
title = page.css('h1::text').get()
title = page.xpath('//h1//text()').get()
```
Это то же самое, что:
```python
title = page.css('h1')[0].text
title = page.xpath('//h1')[0].text
```
Получим атрибут `href` первого элемента с тегом `a`:
```python
link = page.css('a::attr(href)').get()
link = page.xpath('//a/@href').get()
```
Выберем текст первого элемента `h1`, который содержит `Phone` и находится внутри элемента с классом `product`:
```python
title = page.css('.product h1:contains("Phone")::text').get()
title = page.xpath('//*[@class="product"]//h1[contains(text(),"Phone")]/text()').get()
```
Селекторы можно вкладывать и объединять в цепочки, если они находят результаты:
```python
page.css('.product')[0].css('h1:contains("Phone")::text').get()
page.xpath('//*[@class="product"]')[0].xpath('.//h1[contains(text(),"Phone")]/text()').get()
page.xpath('//*[@class="product"]')[0].css('h1:contains("Phone")::text').get()
```
Для XPath относительно текущего элемента используйте `.//`. Начальный `//` ищет во всём документе, даже если перед этим вы выбрали отдельный товар.

Ещё один пример:

Все ссылки, у которых атрибут 'href' содержит 'image':
```python
links = page.css('a[href*="image"]')
links = page.xpath('//a[contains(@href, "image")]')
for index, link in enumerate(links):
    link_value = link.attrib['href']  # Cleaner than link.css('::attr(href)').get()
    link_text = link.text
    print(f'Link number {index} points to this url {link_value} with text content as "{link_text}"')
```

## Выбор по тексту {#text-content-selection}
Scrapling умеет выбирать элементы по их непосредственному тексту двумя способами:

1. Метод `find_by_text` ищет элементы, чей текст содержит заданную строку, и предоставляет дополнительные настройки.
2. Метод `find_by_regex` ищет элементы, чей текст соответствует заданному регулярному выражению, и также предоставляет дополнительные настройки.

Если хорошо знать регулярные выражения, всё, что делает `find_by_text`, можно сделать через `find_by_regex`. Но отдельные методы удобнее для пользователей с разным опытом.

В `find_by_text` первым аргументом передаётся текст, а в `find_by_regex` регулярное выражение. Оба метода принимают следующие аргументы:

* **first_match**: при `True` (по умолчанию) возвращается только первый найденный результат.
* **case_sensitive**: при `True` учитывается регистр букв.
* **clean_match**: при `True` пробельные символы и последовательности пробелов заменяются одним пробелом перед сравнением.

По умолчанию `find_by_text` ищет точное совпадение: текст элемента должен полностью совпадать с переданной строкой. Для изменения этого поведения есть ещё один аргумент:

* **partial**: при включении `find_by_text` возвращает элементы, которые содержат заданный текст. Полное совпадение больше не требуется.

!!! abstract "Примечание"

    Метод `find_by_regex` принимает первым аргументом обычную строку или скомпилированное регулярное выражение. Примеры приведены ниже.

### Поиск похожих элементов {#finding-similar-elements}
Одна из самых полезных возможностей Scrapling позволяет найти элементы, похожие на уже найденный. Идея взята из AutoScraper, но в Scrapling она работает с элементами, найденными любым способом. Часто её используют после поиска по тексту, как в AutoScraper, поэтому рассмотрим её здесь.

Как это работает?

Допустим, вы нашли товар по названию и хотите получить остальные товары из той же таблицы или контейнера. Вызовите `.find_similar()` у найденного элемента, и Scrapling выполнит следующие шаги:

1. Найдёт все элементы страницы на той же глубине дерева DOM.
2. Отбросит элементы, у которых не совпадает имя тега, тег родителя или тег родителя второго уровня.
3. На этом этапе мы уже примерно на 99% уверены, что нашли нужные элементы. Для последней проверки Scrapling сравнит их атрибуты с атрибутами исходного элемента и отбросит недостаточно похожие. Порог сходства можно настроить, но советую менять его, только если настройки по умолчанию не дают нужного результата.

Объяснение получилось длинным, но детали важны. Примеры будут в следующем разделе. Сначала перечислим аргументы метода:

* **similarity_threshold**: порог сходства атрибутов из шага 3. По умолчанию 0,2, то есть атрибуты должны быть похожи хотя бы на 20%. Значение 0 отключает эту проверку. Но сначала советую прочитать об остальных аргументах.
* **ignore_attributes**: имена атрибутов, которые нужно пропустить при последнем сравнении. По умолчанию `('href', 'src',)`, потому что URL у разных элементов могут сильно различаться.
* **match_text**: при `True` текст элемента тоже учитывается в сравнении на шаге 3. Обычно это не требуется, но зависит от задачи.

Теперь рассмотрим примеры.

### Примеры {#examples}
Посмотрим, как находить элементы по обычному тексту и регулярным выражениям.

В этих примерах используется класс `Fetcher`. Подробнее о нём расскажем позже.
```python
from scrapling.fetchers import Fetcher
page = Fetcher.get('https://books.toscrape.com/index.html')
```
Найдём первый элемент, текст которого полностью совпадает с заданной строкой:
```python
>>> page.find_by_text('Tipping the Velvet')
<data='<a href="catalogue/tipping-the-velvet_99...' parent='<h3><a href="catalogue/tipping-the-velve...'>
```
С помощью `page.urljoin` получим полный URL из относительного `href`:
```python
>>> page.find_by_text('Tipping the Velvet').attrib['href']
'catalogue/tipping-the-velvet_999/index.html'
>>> page.urljoin(page.find_by_text('Tipping the Velvet').attrib['href'])
'https://books.toscrape.com/catalogue/tipping-the-velvet_999/index.html'
```
Получим все совпадения, если их несколько. Обратите внимание, что возвращается список:
```python
>>> page.find_by_text('Tipping the Velvet', first_match=False)
[<data='<a href="catalogue/tipping-the-velvet_99...' parent='<h3><a href="catalogue/tipping-the-velve...'>]
```
Получим все элементы, содержащие слово `the`, с помощью частичного совпадения:
```python
>>> results = page.find_by_text('the', partial=True, first_match=False)
>>> [i.text for i in results]
['A Light in the ...',
 'Tipping the Velvet',
 'The Requiem Red',
 'The Dirty Little Secrets ...',
 'The Coming Woman: A ...',
 'The Boys in the ...',
 'The Black Maria',
 'Mesaerion: The Best Science ...',
 "It's Only the Himalayas"]
```
Поиск не учитывает регистр, поэтому результаты содержат и `The`, и строчное `the`. Ограничим поиск элементами с `the`:
```python
>>> results = page.find_by_text('the', partial=True, first_match=False, case_sensitive=True)
>>> [i.text for i in results]
['A Light in the ...',
 'Tipping the Velvet',
 'The Boys in the ...',
 "It's Only the Himalayas"]
```
Получим первый элемент, текст которого соответствует регулярному выражению для цены:
```python
>>> page.find_by_regex(r'£[\d\.]+')
<data='<p class="price_color">£51.77</p>' parent='<div class="product_price"> <p class="pr...'>
>>> page.find_by_regex(r'£[\d\.]+').text
'£51.77'
```
Можно также передать скомпилированное выражение. Scrapling распознает тип аргумента:
```python
>>> import re
>>> regex = re.compile(r'£[\d\.]+')
>>> page.find_by_regex(regex)
<data='<p class="price_color">£51.77</p>' parent='<div class="product_price"> <p class="pr...'>
>>> page.find_by_regex(regex).text
'£51.77'
```
Получим все элементы, соответствующие регулярному выражению:
```python
>>> page.find_by_regex(r'£[\d\.]+', first_match=False)
[<data='<p class="price_color">£51.77</p>' parent='<div class="product_price"> <p class="pr...'>,
 <data='<p class="price_color">£53.74</p>' parent='<div class="product_price"> <p class="pr...'>,
 <data='<p class="price_color">£50.10</p>' parent='<div class="product_price"> <p class="pr...'>,
 <data='<p class="price_color">£47.82</p>' parent='<div class="product_price"> <p class="pr...'>,
 ...]
```
И так далее.

Найдём все элементы, похожие на текущий по расположению и атрибутам. В этом примере пропустим атрибут 'title' при сравнении:
```python
>>> element = page.find_by_text('Tipping the Velvet')
>>> element.find_similar(ignore_attributes=['title'])
[<data='<a href="catalogue/a-light-in-the-attic_...' parent='<h3><a href="catalogue/a-light-in-the-at...'>,
 <data='<a href="catalogue/soumission_998/index....' parent='<h3><a href="catalogue/soumission_998/in...'>,
 <data='<a href="catalogue/sharp-objects_997/ind...' parent='<h3><a href="catalogue/sharp-objects_997...'>,
...]
```
Обратите внимание: найдено 19 элементов, а не 20. Сам текущий элемент не входит в результаты.
```python
>>> len(element.find_similar(ignore_attributes=['title']))
19
```
Получим атрибут `href` всех похожих элементов:
```python
>>> [
    element.attrib['href']
    for element in element.find_similar(ignore_attributes=['title'])
]
['catalogue/a-light-in-the-attic_1000/index.html',
 'catalogue/soumission_998/index.html',
 'catalogue/sharp-objects_997/index.html',
 ...]
```
Немного усложним задачу: получим данные всех книг, используя найденный элемент как отправную точку.
```python
>>> first_product = element.parent.parent
>>> for product in [first_product, *first_product.find_similar()]:
        print({
            "name": product.css('h3 a::text').get(),
            "price": product.css('.price_color')[0].re_first(r'[\d\.]+'),
            "stock": product.css('.availability::text').getall()[-1].clean()
        })
{'name': 'Tipping the Velvet', 'price': '53.74', 'stock': 'In stock'}
{'name': 'A Light in the ...', 'price': '51.77', 'stock': 'In stock'}
{'name': 'Soumission', 'price': '50.10', 'stock': 'In stock'}
{'name': 'Sharp Objects', 'price': '47.82', 'stock': 'In stock'}
...
```
### Расширенные примеры {#advanced-examples}
Вот более сложные и практические примеры с методом `find_similar`.

Извлечение товаров интернет-магазина:
```python
def extract_product_grid(page):
    # Find the first product card
    first_product = page.find_by_text('Add to Cart').find_ancestor(
        lambda e: e.has_class('product-card')
    )

    # Find similar product cards
    products = [first_product, *first_product.find_similar()]

    return [
        {
            'name': p.css('h3::text').get(),
            'price': p.css('.price::text').re_first(r'\d+\.\d{2}'),
            'stock': 'In stock' in p.get_all_text(),
            'rating': p.css('.rating')[0].attrib.get('data-rating')
        }
        for p in products
    ]
```
Извлечение строк таблицы:
```python
def extract_table_data(page):
    # Find the first data row
    first_row = page.css('table tbody tr')[0]

    # Find similar rows
    rows = [first_row, *first_row.find_similar()]

    return [
        {
            'column1': row.css('td:nth-child(1)::text').get(),
            'column2': row.css('td:nth-child(2)::text').get(),
            'column3': row.css('td:nth-child(3)::text').get()
        }
        for row in rows
    ]
```
Извлечение полей формы:
```python
def extract_form_fields(page):
    # Find first form field container
    first_field = page.css('input')[0].find_ancestor(
        lambda e: e.has_class('form-field')
    )

    # Find similar field containers
    fields = [first_field, *first_field.find_similar()]

    return [
        {
            'label': f.css('label::text').get(),
            'type': f.css('input')[0].attrib.get('type'),
            'required': 'required' in f.css('input')[0].attrib
        }
        for f in fields
    ]
```
Извлечение отзывов с сайта:
```python
def extract_reviews(page):
    # Find first review
    first_review = page.find_by_text('Great product!')
    review_container = first_review.find_ancestor(
        lambda e: e.has_class('review')
    )
    
    # Find similar reviews
    all_reviews = [review_container, *review_container.find_similar()]
    
    return [
        {
            'text': r.css('.review-text::text').get(),
            'rating': r.attrib.get('data-rating'),
            'author': r.css('.reviewer::text').get()
        }
        for r in all_reviews
    ]
```
## Поиск по фильтрам {#filters-based-searching}
Это один из самых удобных способов поиска в Scrapling. Он обладает широкими возможностями, а новичкам его проще освоить, чем написание селекторов.

Методы `find_all` и `find` созданы по образцу `find_all` из BeautifulSoup. Они принимают несколько фильтров и находят элементы страницы, которые удовлетворяют всем условиям.

Аргументы обрабатываются так:

* Строка считается именем тега.
* Перебираемый объект, например List/Tuple/Set, считается набором имён тегов.
* Словарь задаёт имена атрибутов HTML-элементов и их значения.
* Регулярные выражения фильтруют элементы по содержимому, как метод `find_by_regex`.
* Функции используются для фильтрации элементов.
* Именованный аргумент задаёт имя HTML-атрибута и его значение.

Метод собирает все переданные аргументы. Каждый фильтр передаёт свой результат следующему фильтру.

Элементы текущей страницы или элемента фильтруются в таком порядке:

1. Выбираются элементы с заданными именами тегов.
2. Выбираются элементы, соответствующие всем заданным атрибутам. Если первый фильтр уже применялся, проверяются только его результаты.
3. Выбираются элементы, соответствующие всем регулярным выражениям. Если предыдущие фильтры применялись, проверяются только их результаты.
4. Выбираются элементы, удовлетворяющие всем переданным функциям. Если предыдущие фильтры применялись, проверяются только их результаты.

!!! note "Примечания"

    1. Обработка начинается с первого доступного фильтра в этом порядке. Если имена тегов не переданы, но заданы атрибуты, поиск начинается с шага 2.
    2. Порядок передачи аргументов не имеет значения. Используется только порядок, описанный выше.

Примеры помогут разобраться :)

### Примеры {#examples_1}
```python
from scrapling.fetchers import Fetcher
page = Fetcher.get('https://quotes.toscrape.com/')
```
Найдём все элементы с тегом `div`:
```python
>>> page.find_all('div')
[<data='<div class="container"> <div class="row...' parent='<body> <div class="container"> <div clas...'>,
 <data='<div class="row header-box"> <div class=...' parent='<div class="container"> <div class="row...'>,
...]
```
Найдём все элементы div с классом `quote`:
```python
>>> page.find_all('div', class_='quote')
[<data='<div class="quote" itemscope itemtype="h...' parent='<div class="col-md-8"> <div class="quote...'>,
 <data='<div class="quote" itemscope itemtype="h...' parent='<div class="col-md-8"> <div class="quote...'>,
...]
```
То же самое другим способом:
```python
>>> page.find_all('div', {'class': 'quote'})
[<data='<div class="quote" itemscope itemtype="h...' parent='<div class="col-md-8"> <div class="quote...'>,
 <data='<div class="quote" itemscope itemtype="h...' parent='<div class="col-md-8"> <div class="quote...'>,
...]
```
Найдём все элементы с классом `quote`:
```python
>>> page.find_all({'class': 'quote'})
[<data='<div class="quote" itemscope itemtype="h...' parent='<div class="col-md-8"> <div class="quote...'>,
 <data='<div class="quote" itemscope itemtype="h...' parent='<div class="col-md-8"> <div class="quote...'>,
...]
```
Найдём все элементы div с классом `quote`, внутри которых есть элемент `.text`, содержащий слово 'world':
```python
>>> page.find_all('div', {'class': 'quote'}, lambda e: "world" in e.css('.text::text').get())
[<data='<div class="quote" itemscope itemtype="h...' parent='<div class="col-md-8"> <div class="quote...'>]
```
Найдём все элементы с дочерними элементами:
```python
>>> page.find_all(lambda element: len(element.children) > 0)
[<data='<html lang="en"><head><meta charset="UTF...'>,
 <data='<head><meta charset="UTF-8"><title>Quote...' parent='<html lang="en"><head><meta charset="UTF...'>,
 <data='<body> <div class="container"> <div clas...' parent='<html lang="en"><head><meta charset="UTF...'>,
...]
```
Найдём все элементы, содержащие слово 'world':
```python
>>> page.find_all(lambda element: "world" in element.text)
[<data='<span class="text" itemprop="text">“The...' parent='<div class="quote" itemscope itemtype="h...'>,
 <data='<a class="tag" href="/tag/world/page/1/"...' parent='<div class="tags"> Tags: <meta class="ke...'>]
```
Найдём все элементы span, соответствующие регулярному выражению:
```python
>>> page.find_all('span', re.compile(r'world'))
[<data='<span class="text" itemprop="text">“The...' parent='<div class="quote" itemscope itemtype="h...'>]
```
Найдём все элементы div и span с классом 'quote'. Таких span нет, поэтому вернутся только div:
```python
>>> page.find_all(['div', 'span'], {'class': 'quote'})
[<data='<div class="quote" itemscope itemtype="h...' parent='<div class="col-md-8"> <div class="quote...'>,
 <data='<div class="quote" itemscope itemtype="h...' parent='<div class="col-md-8"> <div class="quote...'>,
...]
```
Объединим разные условия:
```python
>>> page.find_all({'itemtype':"http://schema.org/CreativeWork"}, 'div').css('.author::text').getall()
['Albert Einstein',
 'J.K. Rowling',
...]
```
Полезный приём: найдём все элементы, у которых значение `href` заканчивается словом 'Einstein':
```python
>>> page.find_all({'href$': 'Einstein'})
[<data='<a href="/author/Albert-Einstein">(about...' parent='<span>by <small class="author" itemprop=...'>,
 <data='<a href="/author/Albert-Einstein">(about...' parent='<span>by <small class="author" itemprop=...'>,
 <data='<a href="/author/Albert-Einstein">(about...' parent='<span>by <small class="author" itemprop=...'>]
```
Ещё один приём: найдём все элементы, у которых `href` содержит '/author/':
```python
>>> page.find_all({'href*': '/author/'})
[<data='<a href="/author/Albert-Einstein">(about...' parent='<span>by <small class="author" itemprop=...'>,
 <data='<a href="/author/J-K-Rowling">(about)</a...' parent='<span>by <small class="author" itemprop=...'>,
 <data='<a href="/author/Albert-Einstein">(about...' parent='<span>by <small class="author" itemprop=...'>,
...]
```
И так далее.

## Создание селекторов {#generating-selectors}
Для любого элемента можно создать CSS- или XPath-селектор и использовать его здесь или в другом месте. При этом неважно, каким способом вы нашли элемент.

Создадим короткий CSS-селектор для `url_element`. Если сократить его нельзя, получится полный селектор:
```python
>>> url_element = page.find({'href*': '/author/'})
>>> url_element.generate_css_selector
'body > div > div:nth-of-type(2) > div > div > span:nth-of-type(2) > a'
```
Создадим полный CSS-селектор для `url_element` от начала страницы:
```python
>>> url_element.generate_full_css_selector
'body > div > div:nth-of-type(2) > div > div > span:nth-of-type(2) > a'
```
Создадим короткий XPath-селектор для `url_element`. Если сократить его нельзя, получится полный селектор:
```python
>>> url_element.generate_xpath_selector
'//body/div/div[2]/div/div/span[2]/a'
```
Создадим полный XPath-селектор для `url_element` от начала страницы:
```python
>>> url_element.generate_full_xpath_selector
'//body/div/div[2]/div/div/span[2]/a'
```
!!! abstract "Примечание"

    При создании короткого селектора Scrapling ищет уникальный элемент, например с атрибутом `id`, на котором можно остановить путь. В нашем случае такого элемента нет, поэтому короткий и полный селекторы совпадают.

## Селекторы и регулярные выражения {#using-selectors-with-regular-expressions}
Как в `parsel`/`scrapy`, методы `re` и `re_first` извлекают данные с помощью регулярных выражений. Но в Scrapling они доступны почти во всех классах, включая `Selector`/`Selectors`/`TextHandler` и `TextHandlers`. Поэтому их можно вызывать прямо у элемента, даже если вы не выбрали текстовый узел.

Подробно мы разберём их при изучении класса [TextHandler](main_classes.md#texthandler). Пока посмотрим на общие примеры:
```python
>>> page.css('.price_color')[0].re_first(r'[\d\.]+')
'51.77'

>>> page.css('.price_color').re_first(r'[\d\.]+')
'51.77'

>>> page.css('.price_color').re(r'[\d\.]+')
['51.77',
 '53.74',
 '50.10',
 '47.82',
 '54.23',
...]

>>> page.css('.product_pod h3 a::attr(href)').re(r'catalogue/(.*)/index.html')
['a-light-in-the-attic_1000',
 'tipping-the-velvet_999',
 'soumission_998',
 'sharp-objects_997',
...]

>>> filtering_function = lambda e: e.parent.tag == 'h3' and e.parent.parent.has_class('product_pod')  # As above selector
>>> page.find('a', filtering_function).attrib['href'].re(r'catalogue/(.*)/index.html')
['a-light-in-the-attic_1000']

>>> page.find_by_text('Tipping the Velvet').attrib['href'].re(r'catalogue/(.*)/index.html')
['tipping-the-velvet_999']
```
Думаю, основная идея понятна. На следующей странице мы подробнее рассмотрим эти методы вместе с классом [TextHandler](main_classes.md#texthandler).