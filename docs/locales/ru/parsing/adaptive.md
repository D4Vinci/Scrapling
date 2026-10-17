---
title: "Поиск HTML-элементов после изменений с адаптивным разбором"
description: "Сохраняйте признаки элементов и находите их после изменений HTML. Узнайте, как включить адаптивный разбор и использовать save, retrieve и relocate."
---

# Адаптивный сбор данных {#adaptive-scraping}

!!! success "Перед началом"

    1. Прочитайте страницу [Поиск элементов](../parsing/selection.md), чтобы понять, как находить и извлекать элементы из объекта [Selector](../parsing/main_classes.md#selector).
    2. Прочитайте страницу [Основные классы](../parsing/main_classes.md), чтобы разобраться в классе [Selector](../parsing/main_classes.md#selector).

Адаптивный сбор данных, ранее известный как automatch, относится к самым полезным возможностям Scrapling. Он отслеживает элементы и находит их заново, чтобы ваш скрейпер продолжал работать после изменений сайта.

Допустим, вы собираете данные со страницы с такой структурой:
```html
<div class="container">
    <section class="products">
        <article class="product" id="p1">
            <h3>Product 1</h3>
            <p class="description">Description 1</p>
        </article>
        <article class="product" id="p2">
            <h3>Product 2</h3>
            <p class="description">Description 2</p>
        </article>
    </section>
</div>
```
Чтобы получить первый товар с ID `p1`, вы, скорее всего, напишете такой селектор:
```python
page.css('#p1')
```
Если владельцы сайта изменят структуру следующим образом:
```html
<div class="new-container">
    <div class="product-wrapper">
        <section class="products">
            <article class="product new-class" data-id="p1">
                <div class="product-info">
                    <h3>Product 1</h3>
                    <p class="new-description">Description 1</p>
                </div>
            </article>
            <article class="product new-class" data-id="p2">
                <div class="product-info">
                    <h3>Product 2</h3>
                    <p class="new-description">Description 2</p>
                </div>
            </article>
        </section>
    </div>
</div>
```
Селектор перестанет работать, и код придётся исправлять. Здесь и пригодится функция `adaptive` в Scrapling.

В Scrapling можно включить `adaptive` при первом выборе элемента. Если при следующем выборе элемент не найдётся, Scrapling вспомнит его признаки и найдёт на сайте наиболее похожий элемент. Всё это без ИИ :)

```python
from scrapling import Selector, Fetcher
# Before the change
page = Selector(page_source, adaptive=True, url='example.com')
# or
Fetcher.adaptive = True
page = Fetcher.get('https://example.com')
# then
element = page.css('#p1', auto_save=True)
if not element:  # One day website changes?
    element = page.css('#p1', adaptive=True)  # Scrapling still finds it!
# the rest of your code...
```
Ниже я покажу пример, а затем подробно объясню, как использовать эту функцию и как она работает. Она доступна для всех способов выбора элементов, а не только CSS/XPath.

## Пример с реальным сайтом {#real-world-scenario}
Возьмём реальный сайт и получим его исходный код через один из Fetcher. Для этого нужно найти сайт, который вот-вот изменит дизайн или структуру, сохранить его исходный код и дождаться изменений. Узнать об этом заранее почти невозможно, если только я не знаком с владельцем сайта. Но тогда тест был бы постановочным :)

Поэтому я воспользуюсь [Wayback Machine](https://web.archive.org/) от [The Web Archive](https://archive.org/). Вот копия [сайта StackOverFlow за 2010 год](https://web.archive.org/web/20100102003420/http://stackoverflow.com/). Довольно старая, правда?</br>Проверим, сможет ли адаптивная функция найти одну и ту же кнопку в дизайне 2010 года и в текущем дизайне с помощью одного селектора :)

Чтобы найти кнопку Questions в старом дизайне, можно использовать селектор `#hmenus > div:nth-child(1) > ul > li:nth-child(1) > a`. Он слишком подробный, потому что его создал Google Chrome.


Теперь проверим этот селектор в обеих версиях:
```python
from scrapling import Fetcher
selector = '#hmenus > div:nth-child(1) > ul > li:nth-child(1) > a'
old_url = "https://web.archive.org/web/20100102003420/http://stackoverflow.com/"
new_url = "https://stackoverflow.com/"
Fetcher.configure(adaptive = True, adaptive_domain='stackoverflow.com')
page = Fetcher.get(old_url, timeout=30)
element1 = page.css(selector, auto_save=True)[0]
# Same selector but used in the updated website
page = Fetcher.get(new_url)
element2 = page.css(selector, adaptive=True)[0]

if element1.text == element2.text:
    print('Scrapling found the same element in the old and new designs!')  # Spoiler alert: it does!
```
Здесь появился новый аргумент `adaptive_domain`. Для Scrapling это два разных домена (`archive.org` и `stackoverflow.com`), поэтому их данные `adaptive` хранятся отдельно. Чтобы указать, что это один сайт, нужно передать одинаковый пользовательский домен для сохранения данных `adaptive` в обоих случаях.

В реальной задаче код будет таким же, но оба запроса будут использовать один URL, поэтому аргумент `adaptive_domain` не понадобится. Это самый близкий к реальности пример, который я могу привести. Надеюсь, он вас не запутал :)

В двух примерах выше я использовал классы `Selector` и `Fetcher`, чтобы показать: адаптивный поиск работает одинаково в обоих случаях.

!!! info "Информация"

    Аргумент `adaptive_domain` в первую очередь нужен, если сайт меняет URL вместе с дизайном или структурой. Он позволяет использовать ранее сохранённые адаптивные данные для нового URL. Без него Scrapling сочтёт сайт новым и не будет использовать старые данные.

## Как работает адаптивный сбор данных {#how-the-adaptive-scraping-feature-works}
Адаптивный сбор данных состоит из двух этапов:

1. **Сохранение**: запись отличительных признаков элементов.
2. **Сопоставление**: поиск элементов с похожими признаками при следующем обращении.

Допустим, вы выбрали элемент любым способом и хотите, чтобы библиотека нашла его при следующем сборе данных, даже если структура или дизайн сайта изменятся.

Если не вдаваться в технические детали, процесс выглядит так:

  1. Вы просите Scrapling сохранить отличительные признаки элемента одним из способов, описанных ниже.
  2. Scrapling сохраняет признаки каждого элемента в настроенную базу данных. По умолчанию это SQLite.
  3. Владельцы сайта могут изменить или удалить любое свойство элемента. Поэтому ни одно из них нельзя использовать как постоянный идентификатор в базе данных. Для решения этой задачи система хранения использует два значения:
     1. Домен текущего сайта. Для класса `Selector` передайте его при создании объекта. Fetcher автоматически возьмёт домен из URL.
     2. `identifier`, по которому можно получить признаки элемента из базы данных. Не всегда нужно задавать его вручную. К этому мы ещё вернёмся.

     Вместе эти значения позволяют позже получить из базы сохранённые признаки элемента.

  4. После изменения структуры сайта включите `adaptive`, чтобы найти элемент. Scrapling получит его сохранённые признаки и сравнит с ними все элементы страницы. Для каждого будет рассчитана степень сходства с нужным элементом. При сравнении учитывается всё, как вы увидите ниже.
  5. Scrapling вернёт элемент или элементы с наибольшим сходством.

### Отличительные признаки {#the-unique-properties}
Может возникнуть вопрос: какие признаки мы считаем отличительными, если все свойства элемента могут измениться или исчезнуть?

Scrapling использует следующие признаки:

- Имя тега, текст, атрибуты (имена и значения), соседние элементы с тем же родителем (только имена тегов) и путь элемента (только имена тегов).
- Имя тега, атрибуты (имена и значения) и текст родителя элемента.

При этом не требуется точное совпадение. Важно, насколько похожи значения. Учитывается даже их порядок: например, порядок имён классов элемента до изменений и после них.

## Как использовать адаптивную функцию {#how-to-use-adaptive-feature}
Адаптивную функцию можно применить к любому найденному элементу. В методах выбора по CSS/XPath она доступна через аргументы, как в примерах выше. Мы ещё к ним вернёмся.

Сначала включите `adaptive`: передайте `adaptive=True` при создании [Selector](main_classes.md#selector) или включите эту настройку в используемом Fetcher, как показано ниже.

Примеры:
```python
from scrapling import Selector, Fetcher
page = Selector(html_doc, adaptive=True)
# OR
Fetcher.adaptive = True
page = Fetcher.get('https://example.com')
```
При работе с классом [Selector](main_classes.md#selector) передайте URL сайта в аргументе `url`, чтобы Scrapling разделял сохранённые признаки элементов по доменам.

Если URL не передан, при сохранении признаков вместо него используется слово `default`. Проблема возникнет, только если позже использовать тот же идентификатор для другого сайта и снова не передать URL при создании объекта. Сохранение перезаписывает прежние данные, а `adaptive` использует только последние сохранённые признаки.

Аргументы `storage` и `storage_args` задают подключение к базе данных. По умолчанию используется класс SQLite из библиотеки. Эти аргументы нужны, только если вы хотите создать свою систему хранения. Этому посвящена [отдельная страница в разделе разработки](../development/adaptive_storage_system.md).

После включения `adaptive` на уровне класса можно использовать функцию двумя основными способами.

### Через CSS/XPath {#the-cssxpath-selection-way}
Как в примере выше, сначала передайте `auto_save` при выборе элемента, который ещё есть на странице:
```python
element = page.css('#p1', auto_save=True)
```
Если элемент больше не находится, используйте тот же селектор с аргументом `adaptive`, и библиотека найдёт его:
```python
element = page.css('#p1', adaptive=True)
```
Довольно просто, правда?

При этом внутри происходит немало работы. Помните идентификатор, который нужен для получения признаков элемента? Методы `css`/`xpath` автоматически используют переданный селектор как идентификатор, чтобы вам было проще :)

Во всех этих методах можно задать свой `identifier`. Это полезно в некоторых задачах, в том числе при сохранении признаков с аргументом `auto_save`.

### Вручную {#the-manual-way}
Можно вручную сохранить признаки элемента, получить их и найти элемент заново с помощью `adaptive`, как показано ниже. Так вы можете повторно находить элементы, выбранные любым способом.

Допустим, вы нашли элемент по тексту:
```python
element = page.find_by_text('Tipping the Velvet', first_match=True)
```
Сохраните его отличительные признаки методом `save`. Здесь идентификатор нужно задать самостоятельно. В примере я выбрал `my_special_element`, но в своём коде лучше использовать понятное имя, как и для переменных :)
```python
page.save(element, 'my_special_element')
```
Позже, чтобы получить признаки и найти элемент на странице с помощью `adaptive`, выполните:
```python
>>> element_dict = page.retrieve('my_special_element')
>>> page.relocate(element_dict, selector_type=True)
[<data='<a href="catalogue/tipping-the-velvet_99...' parent='<h3><a href="catalogue/tipping-the-velve...'>]
>>> page.relocate(element_dict, selector_type=True).css('::text').getall()
['Tipping the Velvet']
```
Для этого используются методы `retrieve` и `relocate`.

Если нужно оставить результат объектом `lxml.etree`, не передавайте аргумент `selector_type`:
```python
>>> page.relocate(element_dict)
[<Element a at 0x105a2a7b0>]
```

## Решение проблем {#troubleshooting}

### Совпадения не найдены {#no-matches-found}
```python
# 1. Check if data was saved
element_data = page.retrieve('identifier')
if not element_data:
    print("No data saved for this identifier")

# 2. Try with different identifier
products = page.css('.product', adaptive=True, identifier='old_selector')

# 3. Save again with new identifier
products = page.css('.new-product', auto_save=True, identifier='new_identifier')
```

### Найдены не те элементы {#wrong-elements-matched}
```python
# Use more specific selectors
products = page.css('.product-list .product', auto_save=True)

# Or save with more context
product = page.find_by_text('Product Name').parent
page.save(product, 'specific_product')
```

## Известные ограничения {#known-issues}
При сохранении через `adaptive` записываются признаки только первого элемента результата. Поэтому, если селектор выбирает разные элементы в нескольких местах страницы, при повторном поиске `adaptive` вернёт только первый. Это не касается составных CSS-селекторов, например селекторов, объединённых запятыми: каждый из них обрабатывается отдельно.

## В заключение {#final-thoughts}
Подробно и просто объяснить эту функцию оказалось непросто. Если что-то осталось неясным, напишите в [обсуждениях](https://github.com/D4Vinci/Scrapling/discussions), на сервере Discord или лично мне. Постараюсь ответить как можно скорее :)