---
title: "使用自适应解析跟踪并重新定位 HTML 元素"
description: "保存元素特征，在 HTML 变化后重新找到元素。了解如何启用自适应解析，以及如何使用 save、retrieve 和 relocate。"
---

# 自适应抓取 {#adaptive-scraping}

!!! success "前提条件"

    1. 已阅读[查询元素](../parsing/selection.md)，了解如何从 [Selector](../parsing/main_classes.md#selector) 对象中查找和提取元素。
    2. 已阅读[主要类](../parsing/main_classes.md)，了解 [Selector](../parsing/main_classes.md#selector) 类。

自适应抓取以前称为 automatch，是 Scrapling 最强大的功能之一。它会跟踪并重新定位元素，让爬虫在网站变化后仍能继续工作。

假设要抓取的页面结构如下：
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
要抓取第一个产品，也就是 ID 为 `p1` 的元素，可能会写出这样的选择器：
```python
page.css('#p1')
```
如果网站维护者把结构改成这样：
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
选择器就无法工作了，需要修改代码。这时就可以用到 Scrapling 的 `adaptive` 功能。

第一次选择元素时，可以启用 `adaptive` 功能。下次使用同一选择器却找不到元素时，Scrapling 会根据之前保存的特征，在网站中寻找相似度最高的元素。整个过程不需要 AI :)

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
下面先用一个例子展示这项功能，再详细介绍它的用法和原理。它适用于所有选择方式，不只是 CSS/XPath。

## 实际场景 {#real-world-scenario}
我们用一个真实网站作为例子，并通过 Fetcher 获取它的源码。理想情况下，要先找到一个即将修改设计或结构的网站，保存源码，再等待它发生变化。当然，除非认识网站维护者，否则几乎不可能提前知道。但那样又像是安排好的测试了，哈哈。

所以，我会使用 [The Web Archive](https://archive.org/) 的 [Wayback Machine](https://web.archive.org/)。这是 [StackOverFlow 网站在 2010 年的副本](https://web.archive.org/web/20100102003420/http://stackoverflow.com/)，很老了吧？</br>看看自适应功能能否用同一个选择器，从 2010 年的旧版页面和当前页面中找到同一个按钮 :)

要从旧版页面中提取 Questions 按钮，可以使用这个选择器：`#hmenus > div:nth-child(1) > ul > li:nth-child(1) > a`。它由 Google Chrome 生成，所以对结构的要求很具体。


现在，在两个版本中测试同一个选择器：
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
这里新增了一个参数 `adaptive_domain`。因为对 Scrapling 来说，`archive.org` 和 `stackoverflow.com` 是两个不同的域名，它会分别保存它们的 `adaptive` 数据。为告诉 Scrapling 这是同一个网站，需要在保存两边的 `adaptive` 数据时指定同一个自定义域名。

在实际场景中，代码基本相同，只是两次请求使用相同的 URL，因此不需要 `adaptive_domain`。这是我能给出的最接近实际情况的例子，希望这个例子足够清楚 :)

上面的两个例子分别使用了 `Selector` 和 `Fetcher`，说明它们的自适应逻辑相同。

!!! info

    `adaptive_domain` 主要用于网站在修改设计或结构时也更换 URL 的情况。通过它，可以在新 URL 上继续使用之前保存的自适应数据。否则，Scrapling 会把它当成新网站，不再使用旧数据。

## 自适应抓取的原理 {#how-the-adaptive-scraping-feature-works}
自适应抓取分为两个阶段：

1. **保存阶段**：保存元素的特征。
2. **匹配阶段**：之后查找具有相似特征的元素。

假设已经通过任意方式选中了一个元素，并希望下次抓取时，即使网站结构或设计变了，库也能找到它。

尽量不涉及复杂细节，整个流程如下：

  1. 通过下面介绍的方式，让 Scrapling 保存元素的特征。
  2. Scrapling 使用配置的数据库，默认为 SQLite，保存每个元素的特征。
  3. 网站维护者可以修改或删除元素的任何信息，因此不能把元素本身的某个属性作为数据库中的固定标识。为解决这个问题，存储系统使用两项信息：
     1. 当前网站的域名。如果使用 `Selector`，需要在初始化时传入；如果使用 Fetcher，则会自动从 URL 获取。
     2. 用于从数据库查询元素特征的 `identifier`。不必每次都手动设置这个标识符，后面会详细说明。

     之后会结合这两项信息，从数据库中读取元素的特征。

  4. 网站结构变化后，启用 `adaptive` 来查找元素。Scrapling 会读取已保存的特征，并与页面上的所有元素进行比较，根据相似程度计算得分。比较时会考虑所有特征，后面会具体说明。
  5. 返回与目标元素相似度最高的元素。

### 元素特征 {#the-unique-properties}
既然元素的任何属性都可能被删除或修改，这里所说的特征到底是什么？

Scrapling 使用以下信息：

- 元素的标签名、文本、属性名称和值、同级元素的标签名，以及路径中的标签名。
- 父元素的标签名、属性名称和值，以及文本。

这些信息不需要完全相同，Scrapling 比较的是相似程度。它会考虑各种细节，包括值的顺序，例如元素类名在变化前后的排列顺序。

## 使用自适应功能 {#how-to-use-adaptive-feature}
自适应功能可以用于任何已找到的元素。它也作为参数集成在 CSS/XPath 选择方法中，上面的例子已经展示过，稍后会再说明。

首先需要启用 `adaptive`。创建 [Selector](main_classes.md#selector) 时传入 `adaptive=True`，或者在所用的 Fetcher 中启用它，如下所示。

示例：
```python
from scrapling import Selector, Fetcher
page = Selector(html_doc, adaptive=True)
# OR
Fetcher.adaptive = True
page = Fetcher.get('https://example.com')
```
使用 [Selector](main_classes.md#selector) 时，需要通过 `url` 传入网站 URL，让 Scrapling 按域名区分各元素保存的特征。

如果不传 URL，保存元素特征时会用 `default` 作为 URL 字段的值。只有在之后对其他网站使用同一个标识符，且仍未传入 URL 时，才会出问题。新的保存操作会覆盖旧数据，`adaptive` 只使用最近保存的特征。

此外还有 `storage` 和 `storage_args`，用于设置数据库连接。默认使用库提供的 SQLite 类。只有需要编写自己的存储系统时才需要关注这两个参数，相关内容在[开发部分的单独页面](../development/adaptive_storage_system.md)中介绍。

全局启用 `adaptive` 后，主要有两种使用方式。

### 通过 CSS/XPath 选择 {#the-cssxpath-selection-way}
如上面的例子所示，先在选择页面上存在的元素时使用 `auto_save`：
```python
element = page.css('#p1', auto_save=True)
```
之后找不到元素时，使用相同的选择器并传入 `adaptive`，库就会尝试重新找到它：
```python
element = page.css('#p1', adaptive=True)
```
很简单吧？

其实背后做了不少工作。还记得用于读取元素特征的标识符吗？为方便使用，`css`/`xpath` 方法会自动把传入的选择器作为标识符 :)

也可以向这些方法传入 `identifier`，自己指定标识符。这在某些场景中很有用，也可以与 `auto_save` 一起使用来保存特征。

### 手动处理 {#the-manual-way}
也可以手动保存元素、读取特征，再重新定位。如下所示，这些操作同样属于 `adaptive` 功能。这样就能重新定位通过任意方法选中的元素。

假设通过文本找到了一个元素：
```python
element = page.find_by_text('Tipping the Velvet', first_match=True)
```
使用 `save` 保存它的特征，但需要自己指定标识符。这里选择 `my_special_element`。实际代码中应使用有意义的名称，就像给变量起名一样 :)
```python
page.save(element, 'my_special_element')
```
之后需要读取特征，并通过 `adaptive` 在页面中重新定位时，可以这样写：
```python
>>> element_dict = page.retrieve('my_special_element')
>>> page.relocate(element_dict, selector_type=True)
[<data='<a href="catalogue/tipping-the-velvet_99...' parent='<h3><a href="catalogue/tipping-the-velve...'>]
>>> page.relocate(element_dict, selector_type=True).css('::text').getall()
['Tipping the Velvet']
```
这里使用了 `retrieve` 和 `relocate` 方法。

如果希望保留 `lxml.etree` 对象，不要传入 `selector_type`：
```python
>>> page.relocate(element_dict)
[<Element a at 0x105a2a7b0>]
```

## 排查问题 {#troubleshooting}

### 找不到匹配元素 {#no-matches-found}
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

### 匹配到了错误元素 {#wrong-elements-matched}
```python
# Use more specific selectors
products = page.css('.product-list .product', auto_save=True)

# Or save with more context
product = page.find_by_text('Product Name').parent
page.save(product, 'specific_product')
```

## 已知问题 {#known-issues}
`adaptive` 保存时只记录选择结果中第一个元素的特征。如果选择器选中了页面上不同位置的多个元素，之后用 `adaptive` 重新定位时只会找回第一个。这不影响组合 CSS 选择器，例如用逗号连接的多个选择器，因为它们会被拆开并分别执行。

## 最后说明 {#final-thoughts}
要把这项功能讲清楚，又不让内容太复杂，并不容易。如果还有不明白的地方，可以到[讨论区](https://github.com/D4Vinci/Scrapling/discussions)提问，我会尽快回复。也可以使用 Discord 服务器，或直接联系我聊聊 :)