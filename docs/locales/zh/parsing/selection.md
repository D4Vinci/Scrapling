---
title: "使用 CSS、XPath、文本和正则表达式提取 HTML 数据"
description: "使用 CSS、XPath、文本和正则表达式选择 HTML 元素。通过 Scrapling 代码示例查找相似元素并提取字段。"
---

# 查询元素 {#querying-elements}
`Selector` 类解析 HTML，因为自适应功能不支持 XML。对于 XML、RSS 或 Atom Feed，请使用 [XMLFeedSpider](../spiders/generic-templates.md#xmlfeedspider)。它使用 XML 解析器，直接提供每个 Feed 节点。

Scrapling 主要有五种查找元素的方式：

1. CSS3 选择器
2. XPath 选择器
3. 根据过滤条件查找
4. 查找包含指定文本的元素
5. 查找内容匹配指定正则表达式的元素

还有其他间接查找元素的方式，这里主要介绍上述方法。另外也会介绍 Scrapling 的一项实用功能：查找与已有元素相似的元素。可以[直接跳到该部分](#finding-similar-elements)。

如果刚接触网页抓取，几乎没写过选择器，又想快速开始，建议先学习 `find`/`find_all`，[点这里查看](#filters-based-searching)。

## CSS/XPath 选择器 {#cssxpath-selectors}

### 什么是 CSS 选择器？ {#what-are-css-selectors}
[CSS](https://en.wikipedia.org/wiki/CSS) 用于设置 HTML 文档的样式。它通过选择器，把样式应用到指定的 HTML 元素。

Scrapling 支持 [W3C 规范](http://www.w3.org/TR/2011/REC-css3-selectors-20110929/)中的 CSS3 选择器。底层使用 `cssselect`，建议查看它[支持的选择器](https://cssselect.readthedocs.io/en/latest/#supported-selectors)、伪函数和伪元素。

Scrapling 还提供一些非标准伪元素：

* 使用 ``::text`` 选择文本节点。
* 使用 ``::attr(name)`` 选择属性值，其中 name 是要读取的属性名。

如果用过 Scrapy 或 Parsel，这里的选择器逻辑会很熟悉，无需另学一套方式 :)

使用 `css` 通过 CSS 选择器选择元素，返回值为 `Selectors`。用 `[0]` 获取第一个元素，或用 `.get()` / `.getall()` 从文本或属性伪选择器中提取文本值。

### 什么是 XPath 选择器？ {#what-are-xpath-selectors}
[XPath](https://en.wikipedia.org/wiki/XPath) 是一种选择 XML 节点的语言，也可以用于 HTML。这份[速查表](https://devhints.io/xpath)可以帮助学习 [XPath](https://en.wikipedia.org/wiki/XPath)。Scrapling 直接通过 [lxml](https://lxml.de/) 提供 XPath 支持。

和 CSS 一样，这里的逻辑与 Scrapy、Parsel 相同。不过，Scrapling 没有实现它们的 XPath 扩展函数 `has-class`，而是提供 `has_class` 方法，可以对找到的元素执行同样的检查。

使用 `xpath` 方法通过 XPath 选择元素，其逻辑与上面的 CSS 方法相同。

> `css` 和 `xpath` 还有一些用于自适应功能的参数。这里暂不展开，后面会用单独的页面详细介绍。

### 选择器示例 {#selectors-examples}
下面对照展示 CSS 和 XPath 的用法。

选择所有类名为 `product` 的元素：
```python
products = page.css('.product')
products = page.xpath('//*[@class="product"]')
```
!!! info "注意："

    如果元素还有其他类名，这个 XPath 就不能准确匹配。**按类名选择时，优先使用 CSS。**

选择第一个类名为 `product` 的元素：
```python
product = page.css('.product')[0]
product = page.xpath('//*[@class="product"]')[0]
```
获取第一个 `h1` 元素的文本：
```python
title = page.css('h1::text').get()
title = page.xpath('//h1//text()').get()
```
这等同于：
```python
title = page.css('h1')[0].text
title = page.xpath('//h1')[0].text
```
获取第一个 `a` 元素的 `href` 属性：
```python
link = page.css('a::attr(href)').get()
link = page.xpath('//a/@href').get()
```
获取第一个符合以下条件的 `h1` 元素的文本：包含 `Phone`，且位于类名为 `product` 的元素内。
```python
title = page.css('.product h1:contains("Phone")::text').get()
title = page.xpath('//*[@class="product"]//h1[contains(text(),"Phone")]/text()').get()
```
只要选择器返回结果，就可以按需要嵌套和链式调用：
```python
page.css('.product')[0].css('h1:contains("Phone")::text').get()
page.xpath('//*[@class="product"]')[0].xpath('.//h1[contains(text(),"Phone")]/text()').get()
page.xpath('//*[@class="product"]')[0].css('h1:contains("Phone")::text').get()
```
使用 `.//` 表示相对于当前元素的 XPath。以 `//` 开头会搜索整个文档，即使前面已经选中了某个产品。

再看一个例子：

查找 'href' 属性中包含 'image' 的所有链接：
```python
links = page.css('a[href*="image"]')
links = page.xpath('//a[contains(@href, "image")]')
for index, link in enumerate(links):
    link_value = link.attrib['href']  # Cleaner than link.css('::attr(href)').get()
    link_text = link.text
    print(f'Link number {index} points to this url {link_value} with text content as "{link_text}"')
```

## 按文本内容选择 {#text-content-selection}
Scrapling 支持根据元素的直接文本内容进行选择，有两种方式：

1. 使用 `find_by_text` 查找直接文本中包含指定内容的元素，并通过参数调整行为。
2. 使用 `find_by_regex` 查找直接文本匹配指定正则表达式的元素，也提供多种选项。

如果熟悉正则表达式，`find_by_text` 能完成的搜索也都可以用 `find_by_regex` 实现。提供两种方法，是为了让不同用户都能方便地使用。

`find_by_text` 的第一个参数是文本，`find_by_regex` 的第一个参数是正则表达式。两者共有以下参数：

* **first_match**：为 `True` 时只返回第一个结果，默认如此。
* **case_sensitive**：为 `True` 时区分大小写。
* **clean_match**：为 `True` 时，在匹配前把空白字符和连续空格替换为一个空格。

默认情况下，`find_by_text` 要求完整匹配，元素文本必须与传入文本完全相同。它还提供一个额外参数来改变这一点：

* **partial**：启用后，`find_by_text` 会返回包含指定文本的元素，不再要求完整匹配。

!!! abstract "注意："

    `find_by_regex` 的第一个参数可以是普通字符串，也可以是编译后的正则表达式，下面会展示示例。

### 查找相似元素 {#finding-similar-elements}
Scrapling 可以根据已有元素查找相似元素。这项功能的灵感来自 AutoScraper，但在 Scrapling 中，无论使用哪种方式找到元素，都可以调用它。它经常用于按文本找到元素之后，因此放在这里介绍。

它是如何工作的？

假设已经通过标题找到了一个产品，现在想提取同一表格或容器中的其他产品。对已有元素调用 `.find_similar()` 后，Scrapling 会执行以下操作：

1. 查找 DOM 树中与该元素深度相同的所有元素。
2. 检查这些元素，剔除标签名、父元素标签名或祖父元素标签名不一致的元素。
3. 此时找到的元素大约有 99% 的概率就是目标元素。最后再通过模糊匹配，剔除属性不够相似的元素。这个步骤有一个相似度阈值，建议仅在默认配置无法找到目标元素时调整。

说明有些长，但这些细节很重要。下一部分会给出示例，先看看这个方法接受的参数：

* **similarity_threshold**：步骤 3 中比较元素属性的阈值，默认为 0.2，也就是两者的属性至少有 20% 相似度。设为 0 可以关闭这项检查，相当于跳过步骤 3。不过，建议先了解其他参数。
* **ignore_attributes**：最后比较属性时忽略的属性名。默认为 `('href', 'src',)`，因为不同元素的 URL 可能相差很大，不适合作为可靠依据。
* **match_text**：为 `True` 时，在步骤 3 中也比较元素文本。一般不建议启用，具体取决于使用场景。

接下来看看示例。

### 示例 {#examples}
以下示例展示如何通过文本和正则表达式查找元素。

示例使用 `Fetcher` 类，它的详细用法会在后面介绍。
```python
from scrapling.fetchers import Fetcher
page = Fetcher.get('https://books.toscrape.com/index.html')
```
查找第一个文本完全匹配的元素：
```python
>>> page.find_by_text('Tipping the Velvet')
<data='<a href="catalogue/tipping-the-velvet_99...' parent='<h3><a href="catalogue/tipping-the-velve...'>
```
结合 `page.urljoin`，把相对 `href` 转换为完整 URL：
```python
>>> page.find_by_text('Tipping the Velvet').attrib['href']
'catalogue/tipping-the-velvet_999/index.html'
>>> page.urljoin(page.find_by_text('Tipping the Velvet').attrib['href'])
'https://books.toscrape.com/catalogue/tipping-the-velvet_999/index.html'
```
如果有多个匹配，获取所有结果，返回值是列表：
```python
>>> page.find_by_text('Tipping the Velvet', first_match=False)
[<data='<a href="catalogue/tipping-the-velvet_99...' parent='<h3><a href="catalogue/tipping-the-velve...'>]
```
获取所有包含 `the` 的元素，即部分匹配：
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
搜索默认不区分大小写，所以结果既包含 `The`，也包含 `the`。下面限制为只有小写 `the` 的元素：
```python
>>> results = page.find_by_text('the', partial=True, first_match=False, case_sensitive=True)
>>> [i.text for i in results]
['A Light in the ...',
 'Tipping the Velvet',
 'The Boys in the ...',
 "It's Only the Himalayas"]
```
获取第一个文本匹配价格正则表达式的元素：
```python
>>> page.find_by_regex(r'£[\d\.]+')
<data='<p class="price_color">£51.77</p>' parent='<div class="product_price"> <p class="pr...'>
>>> page.find_by_regex(r'£[\d\.]+').text
'£51.77'
```
传入编译后的正则表达式也一样，Scrapling 会识别类型并处理：
```python
>>> import re
>>> regex = re.compile(r'£[\d\.]+')
>>> page.find_by_regex(regex)
<data='<p class="price_color">£51.77</p>' parent='<div class="product_price"> <p class="pr...'>
>>> page.find_by_regex(regex).text
'£51.77'
```
获取所有匹配正则表达式的元素：
```python
>>> page.find_by_regex(r'£[\d\.]+', first_match=False)
[<data='<p class="price_color">£51.77</p>' parent='<div class="product_price"> <p class="pr...'>,
 <data='<p class="price_color">£53.74</p>' parent='<div class="product_price"> <p class="pr...'>,
 <data='<p class="price_color">£50.10</p>' parent='<div class="product_price"> <p class="pr...'>,
 <data='<p class="price_color">£47.82</p>' parent='<div class="product_price"> <p class="pr...'>,
 ...]
```
以此类推。

查找位置和属性与当前元素相似的所有元素。在本例中，比较时忽略 'title' 属性：
```python
>>> element = page.find_by_text('Tipping the Velvet')
>>> element.find_similar(ignore_attributes=['title'])
[<data='<a href="catalogue/a-light-in-the-attic_...' parent='<h3><a href="catalogue/a-light-in-the-at...'>,
 <data='<a href="catalogue/soumission_998/index....' parent='<h3><a href="catalogue/soumission_998/in...'>,
 <data='<a href="catalogue/sharp-objects_997/ind...' parent='<h3><a href="catalogue/sharp-objects_997...'>,
...]
```
结果有 19 个而不是 20 个，因为当前元素本身不会包含在结果中。
```python
>>> len(element.find_similar(ignore_attributes=['title']))
19
```
获取所有相似元素的 `href` 属性：
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
再复杂一点，假设希望以这个元素为起点，提取所有图书的数据：
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
### 进阶示例 {#advanced-examples}
下面是一些更接近实际任务的 `find_similar` 用法。

提取电商产品
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
提取表格行
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
提取表单字段
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
提取网站评论
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
## 基于过滤条件搜索 {#filters-based-searching}
这种方式功能强大，而且比编写选择器更容易上手，通常是 Scrapling 中查找元素的最佳选择。

受 BeautifulSoup 的 `find_all` 启发，Scrapling 提供 `find_all` 和 `find`。它们支持多个过滤条件，查找同时满足所有条件的元素。

具体规则如下：

* 字符串作为标签名。
* List、Tuple、Set 等可迭代对象作为一组标签名。
* 字典表示 HTML 元素的属性名称及对应值。
* 正则表达式按内容过滤元素，类似 `find_by_regex`。
* 函数用于按自定义条件过滤元素。
* 关键字参数表示 HTML 元素的属性名称及对应值。

所有参数会被收集起来，每个过滤步骤把结果传给下一步，逐步缩小范围。

当前页面或元素中的所有元素按以下顺序过滤：

1. 收集标签名匹配的元素。
2. 收集满足所有属性条件的元素。如果已执行上一步，则只过滤上一步的结果。
3. 收集匹配所有正则表达式的元素。如果已执行前面的步骤，则只过滤已有结果。
4. 收集满足所有函数条件的元素。如果已执行前面的步骤，则只过滤已有结果。

!!! note "注意事项："

    1. 过滤从上述顺序中第一个实际传入的条件开始。例如，没有传标签名但传了属性条件，就从步骤 2 开始。
    2. 传入参数的先后顺序不影响过滤顺序，始终按上面的规则执行。

看看示例就更清楚了 :)

### 示例 {#examples_1}
```python
from scrapling.fetchers import Fetcher
page = Fetcher.get('https://quotes.toscrape.com/')
```
查找所有 `div` 元素：
```python
>>> page.find_all('div')
[<data='<div class="container"> <div class="row...' parent='<body> <div class="container"> <div clas...'>,
 <data='<div class="row header-box"> <div class=...' parent='<div class="container"> <div class="row...'>,
...]
```
查找类名恰好为 `quote` 的所有 div 元素：
```python
>>> page.find_all('div', class_='quote')
[<data='<div class="quote" itemscope itemtype="h...' parent='<div class="col-md-8"> <div class="quote...'>,
 <data='<div class="quote" itemscope itemtype="h...' parent='<div class="col-md-8"> <div class="quote...'>,
...]
```
另一种等价写法：
```python
>>> page.find_all('div', {'class': 'quote'})
[<data='<div class="quote" itemscope itemtype="h...' parent='<div class="col-md-8"> <div class="quote...'>,
 <data='<div class="quote" itemscope itemtype="h...' parent='<div class="col-md-8"> <div class="quote...'>,
...]
```
查找类名恰好为 `quote` 的所有元素：
```python
>>> page.find_all({'class': 'quote'})
[<data='<div class="quote" itemscope itemtype="h...' parent='<div class="col-md-8"> <div class="quote...'>,
 <data='<div class="quote" itemscope itemtype="h...' parent='<div class="col-md-8"> <div class="quote...'>,
...]
```
查找类名为 `quote` 的 div 元素，其中包含 `.text` 元素，且该元素的文本中含有 'world'：
```python
>>> page.find_all('div', {'class': 'quote'}, lambda e: "world" in e.css('.text::text').get())
[<data='<div class="quote" itemscope itemtype="h...' parent='<div class="col-md-8"> <div class="quote...'>]
```
查找所有具有子元素的元素：
```python
>>> page.find_all(lambda element: len(element.children) > 0)
[<data='<html lang="en"><head><meta charset="UTF...'>,
 <data='<head><meta charset="UTF-8"><title>Quote...' parent='<html lang="en"><head><meta charset="UTF...'>,
 <data='<body> <div class="container"> <div clas...' parent='<html lang="en"><head><meta charset="UTF...'>,
...]
```
查找内容中包含 'world' 的所有元素：
```python
>>> page.find_all(lambda element: "world" in element.text)
[<data='<span class="text" itemprop="text">“The...' parent='<div class="quote" itemscope itemtype="h...'>,
 <data='<a class="tag" href="/tag/world/page/1/"...' parent='<div class="tags"> Tags: <meta class="ke...'>]
```
查找匹配指定正则表达式的所有 span 元素：
```python
>>> page.find_all('span', re.compile(r'world'))
[<data='<span class="text" itemprop="text">“The...' parent='<div class="quote" itemscope itemtype="h...'>]
```
查找类名为 'quote' 的所有 div 和 span 元素。这里没有符合条件的 span，所以只返回 div：
```python
>>> page.find_all(['div', 'span'], {'class': 'quote'})
[<data='<div class="quote" itemscope itemtype="h...' parent='<div class="col-md-8"> <div class="quote...'>,
 <data='<div class="quote" itemscope itemtype="h...' parent='<div class="col-md-8"> <div class="quote...'>,
...]
```
混合使用多种条件：
```python
>>> page.find_all({'itemtype':"http://schema.org/CreativeWork"}, 'div').css('.author::text').getall()
['Albert Einstein',
 'J.K. Rowling',
...]
```
还有一个实用技巧：查找 `href` 属性值以 'Einstein' 结尾的所有元素。
```python
>>> page.find_all({'href$': 'Einstein'})
[<data='<a href="/author/Albert-Einstein">(about...' parent='<span>by <small class="author" itemprop=...'>,
 <data='<a href="/author/Albert-Einstein">(about...' parent='<span>by <small class="author" itemprop=...'>,
 <data='<a href="/author/Albert-Einstein">(about...' parent='<span>by <small class="author" itemprop=...'>]
```
另一个技巧：查找 `href` 属性值中包含 '/author/' 的所有元素。
```python
>>> page.find_all({'href*': '/author/'})
[<data='<a href="/author/Albert-Einstein">(about...' parent='<span>by <small class="author" itemprop=...'>,
 <data='<a href="/author/J-K-Rowling">(about)</a...' parent='<span>by <small class="author" itemprop=...'>,
 <data='<a href="/author/Albert-Einstein">(about...' parent='<span>by <small class="author" itemprop=...'>,
...]
```
以此类推。

## 生成选择器 {#generating-selectors}
可以为任意元素生成 CSS/XPath 选择器，之后在 Scrapling 或其他地方复用。无论最初如何找到这个元素，都可以生成选择器。

为 `url_element` 生成简短的 CSS 选择器；如果无法简化，则生成完整选择器：
```python
>>> url_element = page.find({'href*': '/author/'})
>>> url_element.generate_css_selector
'body > div > div:nth-of-type(2) > div > div > span:nth-of-type(2) > a'
```
为 `url_element` 生成从页面根部开始的完整 CSS 选择器：
```python
>>> url_element.generate_full_css_selector
'body > div > div:nth-of-type(2) > div > div > span:nth-of-type(2) > a'
```
为 `url_element` 生成简短的 XPath 选择器；如果无法简化，则生成完整选择器：
```python
>>> url_element.generate_xpath_selector
'//body/div/div[2]/div/div/span[2]/a'
```
为 `url_element` 生成从页面根部开始的完整 XPath 选择器：
```python
>>> url_element.generate_full_xpath_selector
'//body/div/div[2]/div/div/span[2]/a'
```
!!! abstract "注意："

    生成简短选择器时，Scrapling 会寻找可唯一识别的元素作为起点，例如具有 `id` 属性的元素。本例没有这样的元素，所以简短选择器和完整选择器相同。

## 结合选择器与正则表达式 {#using-selectors-with-regular-expressions}
与 `parsel`/`scrapy` 类似，`re` 和 `re_first` 可以用正则表达式提取数据。不同的是，Scrapling 几乎在所有类中都提供这些方法，包括 `Selector`/`Selectors`/`TextHandler` 和 `TextHandlers`。因此，即使没有先选择文本节点，也可以直接对元素调用。

介绍 [TextHandler](main_classes.md#texthandler) 时会详细说明。基本用法如下：
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
以此类推。下一页会结合 [TextHandler](main_classes.md#texthandler) 更详细地介绍。