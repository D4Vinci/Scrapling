---
title: "Scrapling 的 Selector 和 Selectors：数据与导航"
description: "了解 Selector 和 Selectors 如何保存 HTML、文本和属性。提取值、解析 URL，并在父元素、子元素和同级元素之间导航。"
---

# 解析器的主要类 {#parsing-main-classes}

!!! success "前提条件"

    - 已阅读[查询元素](../parsing/selection.md)，了解如何从 [Selector](../parsing/main_classes.md#selector) 对象中查找和提取元素。

了解各种元素选择方式后，我们再整体看看 [Selector](#selector) 和其他对象，以便更好地理解解析引擎。

[Selector](#selector) 是 Scrapling 解析引擎的核心，负责解析 HTML 和选择元素。可以通过以下任意方式导入：
```python
from scrapling import Selector
from scrapling.parser import Selector
```
然后像[概览](../overview.md)中介绍的那样直接使用：
```python
page = Selector(
    '<html>...</html>',
    url='https://example.com'
)

# Then select elements as you like
elements = page.css('.product')
```
传入 HTML 源码或获取网站后，主要操作的就是 [Selector](#selector) 对象。选择、导航等操作只要返回的是页面元素，而不是文本等其他内容，就会返回 [Selector](#selector) 或 [Selectors](#selectors) 对象。

也就是说，整个页面是一个 [Selector](#selector) 对象，里面的各个元素也是 [Selector](#selector) 对象。元素文本和属性值等文本内容是 [TextHandler](#texthandler) 对象。每个元素的属性集合保存在 [AttributesHandler](#attributeshandler) 中。这两个类稍后再讲，先来看 [Selector](#selector)。

## Selector {#selector}
### 参数说明 {#arguments-explained}
最重要的参数是 `content`，用于传入要解析的 HTML，支持 `str` 和 `bytes`。

`url` 设置页面 URL，用于解析相对链接，并按域名区分已保存的自适应数据。`adaptive`、`storage` 和 `storage_args` 与[自适应功能](adaptive.md)有关。不使用该功能时，这些参数不会产生影响。

还有一些参数用于调整解析过程，或控制解析时如何处理 HTML：

- **encoding**：解析 HTML 使用的编码，默认为 `UTF-8`。
- **keep_comments**：解析时是否保留 HTML 注释。默认关闭，因为注释可能以多种方式影响抓取。

这里先不介绍 `huge_tree` 和 `root`，避免让这页变得过于复杂。
类似的高级功能会暂时略过，因为正常使用库时并不需要了解它们。如果想深入研究，可以阅读开发部分。

页面和元素的大多数属性都采用延迟加载，只有使用时才会初始化，例如页面或元素的文本内容。这也是 Scrapling 速度快的原因之一 :)

### 属性 {#properties}
[概览](../overview.md)已经展示过不少内容。没看过也不用担心，这里会结合更多方法和用法详细介绍。为了便于阅读，用于遍历的属性放在后面的[遍历](#traversal)部分。

为方便演示，假设要解析以下 HTML 页面：
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
像前面那样直接加载页面：
```python
from scrapling import Selector
page = Selector(html_doc)
```
递归获取页面的全部文本，包括嵌套元素中的文本：
```python
>>> page.get_all_text()
'Some page\n\n    \n\n      \nProduct 1\nThis is product 1\n$10.99\nIn stock: 5\nProduct 2\nThis is product 2\n$20.99\nIn stock: 3\nProduct 3\nThis is product 3\n$15.99\nOut of stock'
```
按前面介绍的方法获取第一篇文章，作为接下来的示例：
```python
article = page.find('article')
```
同样可以递归获取该元素中的全部文本：
```python
>>> article.get_all_text()
'Product 1\nThis is product 1\n$10.99\nIn stock: 5'
```
但它的直接文本内容为空，因为上面的 HTML 中，这个元素没有直接文本：
```python
>>> article.text
''
```
`get_all_text` 有以下可选参数：

1. **separator**：使用这个分隔符连接所有收集到的字符串，默认为 '\n'。
2. **strip**：连接前移除字符串首尾的空白，默认关闭。
3. **ignore_tags**：需要忽略的标签名元组，标签内的所有嵌套元素也会被忽略。默认为 `('script', 'style',)`。
4. **valid_values**：只收集有实际文本的元素，忽略空文本或只有空白的元素。默认开启。

这里返回的文本不是普通字符串，而是 [TextHandler](#texthandler)，后面会详细介绍。如果文本可以解析为 JSON，可以直接调用 `.json()`：
```python
>>> script = page.find('script')
>>> script.json()
{'lastUpdated': '2024-09-22T10:30:00Z', 'totalProducts': 3}
```
接着获取元素的标签名：
```python
>>> article.tag
'article'
```
如果直接对页面执行这个操作，得到的是根元素 `html`：
```python
>>> page.tag
'html'
```
现在应该已经理解 `page` 和 `element` 的关系，后面就不再重复了。

获取元素的属性集合：
```python
>>> print(article.attrib)
{'class': 'product', 'data-id': '1'}
```
通过以下任意方式访问某个属性：
```python
article.attrib['class']
article.attrib.get('class')
article['class']  # new in v0.3
```
通过以下方式检查是否包含指定属性：
```python
'class' in article.attrib
'class' in article  # new in v0.3
```
获取元素的 HTML 内容：
```python
>>> article.html_content
'<article class="product" data-id="1"><h3>Product 1</h3>\n        <p class="description">This is product 1</p>\n        <span class="price">$10.99</span>\n        <div class="hidden stock">In stock: 5</div>\n      </article>'
```
获取格式化后的 HTML 内容，使其更易阅读：
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
使用 `.body` 获取页面的原始内容。从 v0.4 开始，对 Fetcher 返回的 `Response` 对象调用 `.body`，结果始终为 `bytes`。
```python
>>> page.body
'<html>\n  <head>\n    <title>Some page</title>\n  </head>\n  ...'
```
获取元素在 DOM 树中的所有祖先：
```python
>>> article.path
[<data='<div class="product-list"> <article clas...' parent='<body> <div class="product-list"> <artic...'>,
 <data='<body> <div class="product-list"> <artic...' parent='<html><head><title>Some page</title></he...'>,
 <data='<html><head><title>Some page</title></he...'>]
```
尽量生成简短的 CSS 选择器，或生成完整选择器：
```python
>>> article.generate_css_selector
'body > div > article'
>>> article.generate_full_css_selector
'body > div > article'
```
XPath 也一样：
```python
>>> article.generate_xpath_selector
"//body/div/article"
>>> article.generate_full_xpath_selector
"//body/div/article"
```

### 遍历 {#traversal}
使用上面找到的元素，详细看看如何在页面中移动。

如果还不了解 DOM 树或树形数据结构，下面的内容可能不太容易理解。建议先查阅这些概念。

如果不想另外查找，这里有一个简单说明。<br/>
`html` 是页面树的根元素，因为每个页面都从 `html` 元素开始。<br/>
`head` 和 `body` 等元素直接位于它下面，因此是 `html` 的子元素，而 `html` 是它们的父元素。`body` 和 `head` 有同一个父元素，所以互为同级元素。

访问元素的父元素：
```python
>>> article.parent
<data='<div class="product-list"> <article clas...' parent='<body> <div class="product-list"> <artic...'>
>>> article.parent.tag
'div'
```
可以按需要连续调用。下面介绍的类似属性和方法也支持这种方式。
```python
>>> article.parent.parent.tag
'body'
```
获取元素的子元素：
```python
>>> article.children
[<data='<h3>Product 1</h3>' parent='<article class="product" data-id="1"><h3...'>,
 <data='<p class="description">This is product 1...' parent='<article class="product" data-id="1"><h3...'>,
 <data='<span class="price">$10.99</span>' parent='<article class="product" data-id="1"><h3...'>,
 <data='<div class="hidden stock">In stock: 5</d...' parent='<article class="product" data-id="1"><h3...'>]
```
获取元素下面的所有元素，相当于递归版本的 `children`：
```python
>>> article.below_elements
[<data='<h3>Product 1</h3>' parent='<article class="product" data-id="1"><h3...'>,
 <data='<p class="description">This is product 1...' parent='<article class="product" data-id="1"><h3...'>,
 <data='<span class="price">$10.99</span>' parent='<article class="product" data-id="1"><h3...'>,
 <data='<div class="hidden stock">In stock: 5</d...' parent='<article class="product" data-id="1"><h3...'>]
```
这个元素的子元素没有再嵌套其他元素，所以结果与 `children` 相同。

使用类名为 `product-list` 的元素，可以更清楚地看到 `children` 和 `below_elements` 的区别：
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
获取同级元素：
```python
>>> article.siblings
[<data='<article class="product" data-id="2"><h3...' parent='<div class="product-list"> <article clas...'>,
 <data='<article class="product" data-id="3"><h3...' parent='<div class="product-list"> <article clas...'>]
```
获取当前元素的下一个同级元素：
```python
>>> article.next
<data='<article class="product" data-id="2"><h3...' parent='<div class="product-list"> <article clas...'>
```
`previous` 用于获取上一个同级元素：
```python
>>> article.previous  # It's the first child, so it doesn't have a previous element
>>> second_article = page.css('.product[data-id="2"]')[0]
>>> second_article.previous
<data='<article class="product" data-id="1"><h3...' parent='<div class="product-list"> <article clas...'>
```
可以快速检查元素是否具有指定类名：
```python
>>> article.has_class('product')
True
```
如果只访问父元素还不够，可以遍历元素的所有祖先：
```python
for ancestor in article.iterancestors():
    # do something with it...
```
也可以查找满足条件的祖先。传入一个接收 [Selector](#selector) 的函数，条件满足时返回 `True`，否则返回 `False`：
```python
>>> article.find_ancestor(lambda ancestor: ancestor.has_class('product-list'))
<data='<div class="product-list"> <article clas...' parent='<body> <div class="product-list"> <artic...'>

>>> article.find_ancestor(lambda ancestor: ancestor.css('.product-list'))  # Same result, different approach
<data='<div class="product-list"> <article clas...' parent='<body> <div class="product-list"> <artic...'>
```
## Selectors {#selectors}
`Selectors` 是 [Selector](#selector) 的列表版本。它继承 Python 的标准 `List` 类型，保留所有 `List` 属性和方法，并添加一些方法，让操作其中的 [Selector](#selector) 实例更方便。

[Selector](#selector) 中所有返回一组元素的方法和属性，都会返回 [Selectors](#selectors) 实例。

从 v0.4 开始，所有选择方法都统一返回 [Selector](#selector)/[Selectors](#selectors)，包括文本节点和属性值。通过 `::text`、`/text()`、`::attr()`、`/@attr` 选出的文本节点也会包装成 [Selector](#selector)。这些对象的 `tag` 是 `"#text"`，`text` 属性返回文本值。仍然可以直接读取文本值，其他属性会返回空值或默认值，不会因此报错。

```python
page.css('a::text')              # -> Selectors (of text node Selectors)
page.xpath('//a/text()')         # -> Selectors
page.css('a::text').get()        # -> TextHandler (the first text value)
page.css('a::text').getall()     # -> TextHandlers (all text values)
page.css('a::attr(href)')        # -> Selectors
page.xpath('//a/@href')          # -> Selectors
page.css('.price_color')         # -> Selectors
```

### 数据提取方法 {#data-extraction-methods}
从 v0.4 开始，[Selector](#selector) 和 [Selectors](#selectors) 都提供 `get()`、`getall()` 及其别名 `extract_first` 和 `extract`，遵循 Scrapy 的用法。旧的 `get_all()` 已移除。

**对于 [Selector](#selector) 对象：**

- `get()` 返回 `TextHandler`。对于文本节点，返回文本值；对于 HTML 元素，返回包含元素自身标签的序列化 HTML。
- `getall()` 返回一个 `TextHandlers` 列表，其中只包含这一个序列化字符串。
- `extract_first` 是 `get()` 的别名，`extract` 是 `getall()` 的别名。

```python
>>> page.css('h3')[0].get()        # Outer HTML of the element
'<h3>Product 1</h3>'

>>> page.css('h3::text')[0].get()  # Text value of the text node
'Product 1'
```

**对于 [Selectors](#selectors) 对象：**

- `get(default=None)` 返回**第一个**元素的序列化字符串。列表为空时返回 `default`。
- `getall()` 序列化**所有**元素，并返回 `TextHandlers` 列表。
- `extract_first` 是 `get()` 的别名，`extract` 是 `getall()` 的别名。

```python
>>> page.css('.price::text').get()      # First price text
'$10.99'

>>> page.css('.price::text').getall()   # All price texts
['$10.99', '$20.99', '$15.99']

>>> page.css('.price::text').get('')    # With default value
'$10.99'
```

这些方法适用于 CSS、XPath、`find` 等所有选择方式，也是以兼容 Scrapy 的方式提取文本和属性值的推荐方法。

接着看看 [Selectors](#selectors) 还提供了哪些功能。
### 属性 {#properties_1}
除了遍历、切片等标准 Python 列表操作，还可以使用以下功能：

直接对包含的 [Selector](#selector) 实例执行 CSS 和 XPath 选择。返回类型与 [Selector](#selector) 的 `css`、`xpath` 相同。参数也类似，但这里不能使用 `adaptive`。这让链式调用很方便。
```pycon
>>> page.css('.product h3::text').getall()
['Product 1', 'Product 2', 'Product 3']
>>> page.css('.product').css('h3::text').getall()
['Product 1', 'Product 2', 'Product 3']
```
也可以直接调用 `re` 和 `re_first`。它们的参数与 [Selector](#selector) 中相同，后面的 [TextHandler](#texthandler) 部分会详细解释。

不过，这里的 `re_first` 会对每个 [Selector](#selector) 调用 `re`，并返回第一个有结果的匹配。`re` 则照常返回 [TextHandlers](#texthandlers)，把所有 [TextHandler](#texthandler) 实例合并到一个 [TextHandlers](#texthandlers) 实例中。
```pycon
>>> page.css('.price::text').re(r'[\d.]+')
['10.99', '20.99', '15.99']
>>> page.css('.product h3::text').re(r'Product (\d+)')
['1', '2', '3']
```
使用 `search` 可以快速查找包含的 [Selector](#selector) 实例。传入的函数必须接收一个 [Selector](#selector) 作为第一个参数，并返回 True 或 False。方法会返回第一个满足条件的 [Selector](#selector)，没有匹配时返回 `None`。

```pycon
>>> product = page.css('.product').search(lambda p: p.css('.price::text').get() == '$20.99')
>>> product.css('h3::text').get()
'Product 2'
```
`filter` 也接收与 `search` 类似的函数，但会返回一个 `Selectors`，包含所有满足条件的 [Selector](#selector)：

```pycon
>>> products = page.css('.product').filter(lambda p: float(p.css('.price::text').re_first(r'[\d.]+')) > 15)
>>> products.css('h3::text').getall()
['Product 2', 'Product 3']
```
可以安全地访问第一个或最后一个元素，不必担心索引错误：
```python
>>> page.css('.product').first   # First Selector or None
<data='<article class="product" data-id="1"><h3...'>
>>> page.css('.product').last    # Last Selector or None
<data='<article class="product" data-id="3"><h3...'>
>>> page.css('.nonexistent').first  # Returns None instead of raising IndexError
```

如果想用简短的方式获取 [Selectors](#selectors) 中 [Selector](#selector) 实例的数量，可以这样写：
```python
page.css('.product').length
```
这等同于：
```python
len(page.css('.product'))
```
没错，就像 JavaScript :)

## TextHandler {#texthandler}
这个类很重要。所有应返回字符串的方法和属性都会返回 `TextHandler`，应返回字符串列表的则会返回 [TextHandlers](#texthandlers)。

TextHandler 继承标准 Python 字符串，因此普通字符串能做的操作，它也能做。那为什么还需要单独的名称呢？

因为 TextHandler 提供了额外的方法和属性。库中的各个类都使用 TextHandler 返回字符串，所以可以灵活组合这些功能，让代码更短、更清晰。也可以直接导入它，对任意字符串使用，具体会在[后面](../development/scrapling_custom_types.md)介绍。
### 用法 {#usage}
切片、索引访问，以及 `split`、`replace`、`strip` 等操作和方法，都会再次返回 `TextHandler`，因此可以继续链式调用。如果发现某个方法或属性返回了普通字符串，而不是 `TextHandler`，请提交 Issue，我们也会调整它。

先介绍 `re` 和 `re_first`。这些方法也存在于 [Selector](#selector)、[Selectors](#selectors) 和 [TextHandlers](#texthandlers) 中，参数相同。

- `re` 的第一个参数可以是字符串或编译后的正则表达式。它查找所有匹配的字符串，并返回 [TextHandlers](#texthandlers)。`re_first` 接收相同参数，行为也类似，但只返回第一个结果，类型为 `TextHandler`。
    
    还有以下实用参数：
    
    - **replace_entities**：默认开启，将字符实体引用替换为对应字符。
    - **clean_match**：默认关闭，匹配时忽略所有空白，包括连续空格。
    - **case_sensitive**：默认开启。关闭后，编译正则表达式时会忽略大小写。
  
    这些例子前面已经见过。因为调用的是 `re`，所以结果为 [TextHandlers](#texthandlers)。
    ```pycon
    >>> page.css('.price::text').re(r'[\d.]+')
    ['10.99', '20.99', '15.99']
    >>> page.css('.product h3::text').re(r'Product (\d+)')
    ['1', '2', '3']
    ```
    为说明其他参数，下面的每个例子使用一个自定义字符串：
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
    到处使用 `TextHandler` 的另一个好处是，`html_content` 也会返回 `TextHandler`。因此可以直接对 HTML 内容使用正则表达式：
    ```python
    >>> page.html_content.re('div class=".*">(.*)</div')
    ['In stock: 5', 'In stock: 3', 'Out of stock']
    ```

- `.json()` 会尝试快速把内容转换为 JSON 对象，无法转换时抛出错误：
  ```python
  >>> page.css('#page-data::text').get()
    '\n      {\n        "lastUpdated": "2024-09-22T10:30:00Z",\n        "totalProducts": 3\n      }\n    '
  >>> page.css('#page-data::text').get().json()
    {'lastUpdated': '2024-09-22T10:30:00Z', 'totalProducts': 3}
  ```
  如果选择元素时没有指定文本节点，例如元素文本或属性文本，就会自动使用元素的文本内容：
  ```python
  >>> page.css('#page-data')[0].json()
  {'lastUpdated': '2024-09-22T10:30:00Z', 'totalProducts': 3}
  ```
  [Selector](#selector) 还做了额外处理。假设页面如下：
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
  前面介绍的 [Selector](#selector) 方法 `get_all_text` 也会返回 `TextHandler`。<br/><br/>
  如果这样调用：
  ```python
  >>> page.css('div::text').get().json()
  ```
  就会报错，因为 `div` 标签没有可以解析为 JSON 的直接文本，实际上它完全没有直接文本。<br/><br/>
  这时可以使用 `get_all_text`：
  ```python
  >>> page.css('div')[0].get_all_text(ignore_tags=[]).json()
    {'lastUpdated': '2024-09-22T10:30:00Z', 'totalProducts': 3}
  ```
  这里使用 `ignore_tags`，是因为它默认忽略 `('script', 'style',)`。<br/><br/>
  使用 Fetcher 时还有一个相关行为。假设获取到这样的 JSON 响应：
  ```python
  >>> page = Selector("""{"some_key": "some_value"}""")
  ```
  [Selector](#selector) 主要处理 HTML 页面，因此会把它当作不完整的 HTML 并修复。读取 `html_content` 时会得到：
  ```python
  >>> page.html_content
  '<html><body><p>{"some_key": "some_value"}</p></body></html>'
  ```
  不过，直接调用 `json` 仍然有效：
  ```python
  >>> page.json()
  {'some_key': 'some_value'}
  ```
  `html` 标签没有直接文本，为什么还能成功呢？<br/>
  为处理 JSON 响应等情况，[Selector](#selector) 会保留收到内容的原始副本。调用 `.json()` 时，会先尝试把这个副本解析为 JSON。如果没有副本，例如操作的是单个元素，则检查元素的直接文本；否则会直接使用 `get_all_text`。<br/>

- `.clean()` 会移除空白字符和连续空格，并返回新的 `TextHandler` 实例：
```python
>>> TextHandler('\n wonderful  idea, \reh?').clean()
'wonderful idea, eh?'
```
还可以传入 `remove_entities`，让 `clean` 把 HTML 实体替换为对应字符。

- `.sort()` 可以像处理列表一样对字符串排序：
```python
>>> TextHandler('acb').sort()
'abc'
```
也可以反向排序：
```python
>>> TextHandler('acb').sort(reverse=True)
'cba'
```

以后会继续添加方法和属性。请记住，库中几乎所有原本返回字符串的地方都会返回这个类。

## TextHandlers {#texthandlers}
这个类的思路与 [Selectors](#selectors) 和 [Selector](#selector) 类似。它继承标准列表的行为，并增加 `re` 和 `re_first`。

区别在于，这里的 `re_first` 会对每个 [TextHandler](#texthandler) 调用 `re`，返回第一个结果或 `None`。目前没有其他需要说明的内容，以后会继续添加方法。

## AttributesHandler {#attributeshandler}
这是标准 Python 字典 `dict` 的只读版本，专门保存元素或 [Selector](#selector) 实例的属性。
```python
>>> print(page.find('script').attrib)
{'id': 'page-data', 'type': 'application/json'}
>>> type(page.find('script').attrib).__name__
'AttributesHandler'
```
因为是只读的，它比标准字典占用更少资源。除修改或覆盖数据的方法外，其他方法和属性与字典相同。

目前还提供两个简单功能：

- `search_values` 方法

    普通字典可以用 `dict.get("key_name")` 检查键是否存在。如果要按值搜索，通常需要额外代码。这个方法可以直接搜索属性值，并为每个匹配项返回一个字典。
    
    简单示例：
    ```python
    >>> for i in page.find('script').attrib.search_values('page-data'):
            print(i)
    {'id': 'page-data'}
    ```
    还可以通过 `partial` 搜索值的一部分：
    ```python
    >>> for i in page.find('script').attrib.search_values('page', partial=True):
            print(i)
    {'id': 'page-data'}
    ```
    上面的例子比较简单。更实际的用法是与 `find_all` 配合，查找具有指定属性值的所有元素：
    ```python
    >>> page.find_all(lambda element: list(element.attrib.search_values('product')))
    [<data='<article class="product" data-id="1"><h3...' parent='<div class="product-list"> <article clas...'>,
     <data='<article class="product" data-id="2"><h3...' parent='<div class="product-list"> <article clas...'>,
     <data='<article class="product" data-id="3"><h3...' parent='<div class="product-list"> <article clas...'>]
    ```
    这些元素的 `class` 属性值都是 'product'。
    
    这里使用 `list`，是因为 `search_values` 返回生成器。如果不转换，对所有元素都会被判断为 `True`。

- `json_string` 属性

    如果当前属性可以序列化为 JSON，这个属性会将它们转换为 JSON 字符串，否则抛出错误。
  
    ```python
    >>>page.find('script').attrib.json_string
    b'{"id":"page-data","type":"application/json"}'
    ```