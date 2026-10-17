---
title: "Scrapling의 Selector와 Selectors: 데이터와 탐색"
description: "Selector와 Selectors가 HTML, 텍스트, 속성을 저장하는 방식을 알아봅니다. 값을 추출하고 URL을 완성하며 부모, 자식, 형제 요소를 탐색하세요."
---

# 파싱의 주요 클래스 {#parsing-main-classes}

!!! success "사전 준비"

    - [요소 찾기](../parsing/selection.md)를 읽고 [Selector](../parsing/main_classes.md#selector) 객체에서 요소를 찾고 추출하는 방법을 알아두세요.

Scrapling에서 요소를 선택하는 여러 방법을 살펴봤습니다. 이제 [Selector](#selector) 클래스와 관련 객체를 살펴보며 파서가 어떻게 작동하는지 알아보겠습니다.

[Selector](#selector)는 HTML 파싱과 요소 선택을 담당하는 Scrapling의 핵심 클래스입니다. 다음 중 어느 방식으로든 가져올 수 있습니다.
```python
from scrapling import Selector
from scrapling.parser import Selector
```
그런 다음 [개요](../overview.md)에서 배운 것처럼 바로 사용합니다.
```python
page = Selector(
    '<html>...</html>',
    url='https://example.com'
)

# Then select elements as you like
elements = page.css('.product')
```
HTML을 전달하거나 사이트를 가져온 뒤 주로 다루는 객체는 [Selector](#selector)입니다. 선택이나 탐색 등의 작업 결과가 텍스트가 아니라 페이지의 요소라면, [Selector](#selector) 또는 [Selectors](#selectors) 객체를 반환합니다.

페이지 자체도 [Selector](#selector) 객체이고, 그 안의 요소들도 [Selector](#selector) 객체입니다. 요소의 내용이나 속성값 같은 텍스트는 [TextHandler](#texthandler) 객체이며, 각 요소의 속성은 [AttributesHandler](#attributeshandler)에 저장됩니다. 이 두 객체는 뒤에서 설명하고, 먼저 [Selector](#selector)를 살펴보겠습니다.

## Selector {#selector}
### 인수 설명 {#arguments-explained}
가장 중요한 인수는 `content`입니다. 파싱할 HTML을 `str` 또는 `bytes`로 전달합니다.

`url`은 상대 링크를 완성하고 저장된 적응형 데이터를 도메인별로 나눌 때 사용하는 페이지 URL입니다. `adaptive`, `storage`, `storage_args`는 [적응형 기능](adaptive.md)의 설정이며, 이 기능을 사용하지 않으면 영향을 주지 않습니다.

HTML 파싱과 처리 방식을 바꾸는 인수도 있습니다.

- **encoding**: HTML을 파싱할 때 사용할 인코딩입니다. 기본값은 `UTF-8`입니다.
- **keep_comments**: 파싱할 때 HTML 주석을 유지할지 정합니다. 주석이 스크래핑에 문제를 일으킬 수 있어 기본적으로 꺼져 있습니다.

설명을 너무 복잡하게 만들지 않기 위해 `huge_tree`와 `root`는 여기서 다루지 않습니다.
라이브러리를 사용하기 위해 꼭 알 필요는 없는 고급 기능은 종종 이렇게 생략합니다. 자세히 알고 싶다면 개발 섹션을 참고하세요.

페이지와 요소의 속성은 대부분 필요할 때만 계산합니다. 예를 들어 텍스트 내용은 실제로 접근할 때 초기화합니다. 이것도 Scrapling이 빠른 이유 중 하나입니다 :)

### 속성 {#properties}
[개요](../overview.md)에서 이미 본 내용도 있지만, 여기서는 더 자세한 사용법을 살펴봅니다. 요소 사이를 이동하는 속성은 아래 [탐색](#traversal) 섹션에 따로 정리했습니다.

다음 HTML 페이지를 예로 사용하겠습니다.
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
앞서 본 방법으로 페이지를 불러옵니다.
```python
from scrapling import Selector
page = Selector(html_doc)
```
중첩된 요소까지 포함해 페이지의 모든 텍스트를 가져옵니다.
```python
>>> page.get_all_text()
'Some page\n\n    \n\n      \nProduct 1\nThis is product 1\n$10.99\nIn stock: 5\nProduct 2\nThis is product 2\n$20.99\nIn stock: 3\nProduct 3\nThis is product 3\n$15.99\nOut of stock'
```
첫 번째 article 요소를 가져와 예로 사용하겠습니다.
```python
article = page.find('article')
```
같은 방법으로 요소 안의 모든 텍스트를 가져옵니다.
```python
>>> article.get_all_text()
'Product 1\nThis is product 1\n$10.99\nIn stock: 5'
```
하지만 요소에 직접 들어 있는 텍스트만 요청하면 빈 값이 나옵니다. 위 HTML에서 이 요소에는 직접 작성된 텍스트가 없기 때문입니다.
```python
>>> article.text
''
```
`get_all_text`에는 다음과 같은 선택적 인수가 있습니다.

1. **separator**: 찾은 문자열을 합칠 때 사용하는 구분자입니다. 기본값은 '\n'입니다.
2. **strip**: 합치기 전에 각 문자열의 양 끝 공백을 제거합니다. 기본적으로 꺼져 있습니다.
3. **ignore_tags**: 결과에서 제외할 태그 이름의 튜플입니다. 해당 태그 안의 중첩 요소도 제외합니다. 기본값은 `('script', 'style',)`입니다.
4. **valid_values**: 값이 있는 요소만 수집합니다. 텍스트가 비어 있거나 공백만 있는 요소는 제외합니다. 기본적으로 켜져 있습니다.

여기서 반환하는 텍스트는 일반 문자열이 아니라 [TextHandler](#texthandler)입니다. 뒤에서 자세히 설명하겠습니다. 내용이 JSON이라면 `.json()`으로 변환할 수 있습니다.
```python
>>> script = page.find('script')
>>> script.json()
{'lastUpdated': '2024-09-22T10:30:00Z', 'totalProducts': 3}
```
이제 요소의 태그를 가져옵니다.
```python
>>> article.tag
'article'
```
페이지에 직접 사용하면 루트 `html` 요소를 다루고 있다는 것을 확인할 수 있습니다.
```python
>>> page.tag
'html'
```
이제 `page`와 `element`의 관계는 충분히 설명했으니 다시 다루지 않겠습니다.

요소의 속성을 가져옵니다.
```python
>>> print(article.attrib)
{'class': 'product', 'data-id': '1'}
```
특정 속성은 다음 중 어느 방법으로든 읽을 수 있습니다.
```python
article.attrib['class']
article.attrib.get('class')
article['class']  # new in v0.3
```
특정 속성이 있는지는 다음처럼 확인합니다.
```python
'class' in article.attrib
'class' in article  # new in v0.3
```
요소의 HTML 내용을 가져옵니다.
```python
>>> article.html_content
'<article class="product" data-id="1"><h3>Product 1</h3>\n        <p class="description">This is product 1</p>\n        <span class="price">$10.99</span>\n        <div class="hidden stock">In stock: 5</div>\n      </article>'
```
보기 좋게 정리한 HTML을 가져옵니다.
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
`.body` 속성은 페이지의 원본 내용을 반환합니다. v0.4부터 Fetcher가 반환하는 `Response` 객체의 `.body`는 항상 `bytes`입니다.
```python
>>> page.body
'<html>\n  <head>\n    <title>Some page</title>\n  </head>\n  ...'
```
DOM 트리에서 이 요소의 모든 조상을 가져옵니다.
```python
>>> article.path
[<data='<div class="product-list"> <article clas...' parent='<body> <div class="product-list"> <artic...'>,
 <data='<body> <div class="product-list"> <artic...' parent='<html><head><title>Some page</title></he...'>,
 <data='<html><head><title>Some page</title></he...'>]
```
가능하면 짧은 CSS 선택자를 만들고, 그렇지 않으면 전체 선택자를 만듭니다.
```python
>>> article.generate_css_selector
'body > div > article'
>>> article.generate_full_css_selector
'body > div > article'
```
XPath도 같은 방식입니다.
```python
>>> article.generate_xpath_selector
"//body/div/article"
>>> article.generate_full_xpath_selector
"//body/div/article"
```

### 탐색 {#traversal}
앞에서 찾은 요소를 사용해 페이지 안에서 이동하는 속성과 메서드를 자세히 살펴보겠습니다.

DOM 트리나 트리 자료구조가 익숙하지 않으면 이 부분이 어려울 수 있습니다. 먼저 해당 개념을 찾아보면 도움이 됩니다.

바로 이어서 읽고 싶다면 다음의 짧은 설명을 참고하세요.<br/>
`html` 요소는 사이트 트리의 루트입니다. 모든 페이지가 `html` 요소로 시작하기 때문입니다.<br/>
그 바로 아래에는 `head`와 `body` 같은 요소가 있습니다. 이들은 `html`의 자식이며, `html`은 이들의 부모입니다. `body`와 `head`는 부모가 같으므로 서로 형제 요소입니다.

요소의 부모를 가져옵니다.
```python
>>> article.parent
<data='<div class="product-list"> <article clas...' parent='<body> <div class="product-list"> <artic...'>
>>> article.parent.tag
'div'
```
이런 접근은 원하는 만큼 이어서 사용할 수 있습니다. 아래에서 다룰 비슷한 속성과 메서드에도 적용됩니다.
```python
>>> article.parent.parent.tag
'body'
```
요소의 자식을 가져옵니다.
```python
>>> article.children
[<data='<h3>Product 1</h3>' parent='<article class="product" data-id="1"><h3...'>,
 <data='<p class="description">This is product 1...' parent='<article class="product" data-id="1"><h3...'>,
 <data='<span class="price">$10.99</span>' parent='<article class="product" data-id="1"><h3...'>,
 <data='<div class="hidden stock">In stock: 5</d...' parent='<article class="product" data-id="1"><h3...'>]
```
요소 아래의 모든 중첩 요소를 가져옵니다. `children`을 모든 깊이에 적용하는 것과 비슷합니다.
```python
>>> article.below_elements
[<data='<h3>Product 1</h3>' parent='<article class="product" data-id="1"><h3...'>,
 <data='<p class="description">This is product 1...' parent='<article class="product" data-id="1"><h3...'>,
 <data='<span class="price">$10.99</span>' parent='<article class="product" data-id="1"><h3...'>,
 <data='<div class="hidden stock">In stock: 5</d...' parent='<article class="product" data-id="1"><h3...'>]
```
이 예에서는 자식에게 다른 자식이 없으므로 `children`과 결과가 같습니다.

`product-list` 클래스가 있는 요소를 보면 `children`과 `below_elements`의 차이가 더 분명해집니다.
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
요소의 형제를 가져옵니다.
```python
>>> article.siblings
[<data='<article class="product" data-id="2"><h3...' parent='<div class="product-list"> <article clas...'>,
 <data='<article class="product" data-id="3"><h3...' parent='<div class="product-list"> <article clas...'>]
```
현재 요소의 다음 형제 요소를 가져옵니다.
```python
>>> article.next
<data='<article class="product" data-id="2"><h3...' parent='<div class="product-list"> <article clas...'>
```
`previous`도 같은 방식으로 동작합니다.
```python
>>> article.previous  # It's the first child, so it doesn't have a previous element
>>> second_article = page.css('.product[data-id="2"]')[0]
>>> second_article.previous
<data='<article class="product" data-id="1"><h3...' parent='<div class="product-list"> <article clas...'>
```
요소에 특정 클래스가 있는지 빠르고 쉽게 확인할 수 있습니다.
```python
>>> article.has_class('product')
True
```
부모 하나로 충분하지 않다면 모든 조상을 순서대로 살펴볼 수 있습니다.
```python
for ancestor in article.iterancestors():
    # do something with it...
```
조건에 맞는 특정 조상을 찾을 수도 있습니다. [Selector](#selector) 객체를 받고 조건이 맞으면 `True`, 아니면 `False`를 반환하는 함수를 전달하세요.
```python
>>> article.find_ancestor(lambda ancestor: ancestor.has_class('product-list'))
<data='<div class="product-list"> <article clas...' parent='<body> <div class="product-list"> <artic...'>

>>> article.find_ancestor(lambda ancestor: ancestor.css('.product-list'))  # Same result, different approach
<data='<div class="product-list"> <article clas...' parent='<body> <div class="product-list"> <artic...'>
```
## Selectors {#selectors}
`Selectors`는 [Selector](#selector) 객체를 담는 리스트입니다. Python의 표준 `List`를 상속하므로 모든 `List` 속성과 메서드를 지원합니다. 여기에 내부의 [Selector](#selector) 객체를 더 쉽게 다룰 수 있는 메서드를 추가했습니다.

[Selector](#selector)의 메서드와 속성이 여러 요소를 반환할 때는 [Selectors](#selectors) 객체를 사용합니다.

v0.4부터 모든 선택 메서드는 텍스트 노드와 속성값에도 [Selector](#selector)/[Selectors](#selectors) 객체를 반환합니다. `::text`, `/text()`, `::attr()`, `/@attr`로 선택한 텍스트 노드도 [Selector](#selector)로 감쌉니다. 이 객체의 `tag`는 `"#text"`이며, `text` 속성은 텍스트값을 반환합니다. 텍스트는 직접 읽을 수 있고, 다른 속성은 빈 값이나 기본값을 반환합니다.

```python
page.css('a::text')              # -> Selectors (of text node Selectors)
page.xpath('//a/text()')         # -> Selectors
page.css('a::text').get()        # -> TextHandler (the first text value)
page.css('a::text').getall()     # -> TextHandlers (all text values)
page.css('a::attr(href)')        # -> Selectors
page.xpath('//a/@href')          # -> Selectors
page.css('.price_color')         # -> Selectors
```

### 데이터 추출 메서드 {#data-extraction-methods}
v0.4부터 [Selector](#selector)와 [Selectors](#selectors)는 모두 `get()`, `getall()`과 별칭인 `extract_first`, `extract`를 제공합니다. Scrapy의 방식을 따릅니다. 이전의 `get_all()`은 제거되었습니다.

**[Selector](#selector) 객체에서는 다음과 같이 동작합니다.**

- `get()`은 `TextHandler`를 반환합니다. 텍스트 노드라면 텍스트값을, HTML 요소라면 바깥 태그를 포함한 HTML 문자열을 반환합니다.
- `getall()`은 해당 문자열 하나를 담은 `TextHandlers` 리스트를 반환합니다.
- `extract_first`는 `get()`의 별칭이고, `extract`는 `getall()`의 별칭입니다.

```python
>>> page.css('h3')[0].get()        # Outer HTML of the element
'<h3>Product 1</h3>'

>>> page.css('h3::text')[0].get()  # Text value of the text node
'Product 1'
```

**[Selectors](#selectors) 객체에서는 다음과 같이 동작합니다.**

- `get(default=None)`은 **첫 번째** 요소의 문자열을 반환합니다. 리스트가 비어 있으면 `default`를 반환합니다.
- `getall()`은 **모든** 요소를 문자열로 변환해 `TextHandlers` 리스트로 반환합니다.
- `extract_first`는 `get()`의 별칭이고, `extract`는 `getall()`의 별칭입니다.

```python
>>> page.css('.price::text').get()      # First price text
'$10.99'

>>> page.css('.price::text').getall()   # All price texts
['$10.99', '$20.99', '$15.99']

>>> page.css('.price::text').get('')    # With default value
'$10.99'
```

이 메서드는 CSS, XPath, `find` 등 모든 선택 방법에서 사용할 수 있습니다. Scrapy와 호환되는 방식으로 텍스트와 속성값을 추출할 때 권장합니다.

이제 [Selectors](#selectors)가 제공하는 다른 기능을 살펴보겠습니다.
### 속성 {#properties_1}
반복과 슬라이싱 같은 Python 리스트의 기본 연산 외에도 다음 작업을 할 수 있습니다.



리스트 안의 [Selector](#selector) 객체에 CSS와 XPath 선택자를 바로 실행할 수 있습니다. 반환 타입은 [Selector](#selector)의 `css`, `xpath` 메서드와 같습니다. 인수도 같지만 여기서는 `adaptive`를 사용할 수 없습니다. 따라서 메서드를 쉽게 이어서 사용할 수 있습니다.
```pycon
>>> page.css('.product h3::text').getall()
['Product 1', 'Product 2', 'Product 3']
>>> page.css('.product').css('h3::text').getall()
['Product 1', 'Product 2', 'Product 3']
```
`re`와 `re_first`도 바로 실행할 수 있습니다. [Selector](#selector)와 같은 인수를 받습니다. 이 메서드들은 아래 [TextHandler](#texthandler) 섹션에서 설명합니다.

다만 여기서 `re_first`는 각 [Selector](#selector)에 `re`를 실행하고, 결과가 있는 첫 번째 항목의 결과를 반환합니다. `re`는 여러 [TextHandler](#texthandler)를 하나의 [TextHandlers](#texthandlers)로 합친 [TextHandlers](#texthandlers) 객체를 반환합니다.
```pycon
>>> page.css('.price::text').re(r'[\d.]+')
['10.99', '20.99', '15.99']
>>> page.css('.product h3::text').re(r'Product (\d+)')
['1', '2', '3']
```
`search`로 리스트 안의 [Selector](#selector)를 빠르게 검색할 수 있습니다. 전달한 함수는 첫 번째 인수로 [Selector](#selector)를 받고 True/False를 반환해야 합니다. 메서드는 조건에 맞는 첫 번째 [Selector](#selector)를 반환하며, 없으면 `None`을 반환합니다.

```pycon
>>> product = page.css('.product').search(lambda p: p.css('.price::text').get() == '$20.99')
>>> product.css('h3::text').get()
'Product 2'
```
`filter`도 `search`처럼 함수를 받지만, 조건에 맞는 모든 [Selector](#selector)를 담은 `Selectors`를 반환합니다.

```pycon
>>> products = page.css('.product').filter(lambda p: float(p.css('.price::text').re_first(r'[\d.]+')) > 15)
>>> products.css('h3::text').getall()
['Product 2', 'Product 3']
```
인덱스 오류 걱정 없이 첫 번째나 마지막 요소에 안전하게 접근할 수 있습니다.
```python
>>> page.css('.product').first   # First Selector or None
<data='<article class="product" data-id="1"><h3...'>
>>> page.css('.product').last    # Last Selector or None
<data='<article class="product" data-id="3"><h3...'>
>>> page.css('.nonexistent').first  # Returns None instead of raising IndexError
```

[Selectors](#selectors) 안에 있는 [Selector](#selector)의 개수를 짧게 쓰고 싶다면 다음처럼 할 수 있습니다.
```python
page.css('.product').length
```
다음 코드와 같습니다.
```python
len(page.css('.product'))
```
네, JavaScript와 비슷하죠 :)

## TextHandler {#texthandler}
이 클래스는 꼭 알아두세요. 문자열을 반환하는 모든 메서드와 속성은 `TextHandler`를 반환하며, 문자열 리스트를 반환하는 경우에는 [TextHandlers](#texthandlers)를 사용합니다.

TextHandler는 Python의 표준 문자열을 상속하므로 일반 문자열로 할 수 있는 작업을 모두 지원합니다. 그렇다면 왜 다른 이름을 쓸까요?

TextHandler는 일반 문자열에 없는 메서드와 속성을 추가합니다. 모든 클래스에서 문자열을 반환할 때 TextHandler를 사용하므로, 이를 활용하면 코드를 더 짧고 간단하게 작성할 수 있습니다. 직접 가져와서 어떤 문자열에든 사용할 수도 있습니다. 이 방법은 [뒤에서](../development/scrapling_custom_types.md) 설명합니다.
### 사용법 {#usage}
슬라이싱, 인덱스 접근과 `split`, `replace`, `strip` 같은 메서드도 다시 `TextHandler`를 반환합니다. 그래서 원하는 대로 이어서 사용할 수 있습니다. `TextHandler` 대신 일반 문자열을 반환하는 메서드나 속성을 발견하면 issue로 알려주세요. 그 부분도 수정하겠습니다.

먼저 `re`와 `re_first`를 살펴보겠습니다. [Selector](#selector), [Selectors](#selectors), [TextHandlers](#texthandlers)에도 있는 메서드이며 같은 인수를 받습니다.

- `re`는 첫 번째 인수로 문자열이나 컴파일된 정규식을 받습니다. 일치하는 모든 문자열을 찾아 [TextHandlers](#texthandlers)로 반환합니다. `re_first`도 같은 인수를 받고 비슷하게 동작하지만, 첫 번째 결과만 `TextHandler`로 반환합니다.
    
    다음과 같은 추가 인수도 있습니다.
    
    - **replace_entities**: 기본적으로 켜져 있습니다. HTML 엔티티를 해당 문자로 바꿉니다.
    - **clean_match**: 기본적으로 꺼져 있습니다. 일치 여부를 확인할 때 연속 공백을 포함한 공백 문자를 무시합니다.
    - **case_sensitive**: 기본적으로 켜져 있습니다. 끄면 정규식을 컴파일할 때 대소문자를 구분하지 않습니다.
  
    앞서 본 예입니다. `re`를 사용했으므로 결과는 [TextHandlers](#texthandlers)입니다.
    ```pycon
    >>> page.css('.price::text').re(r'[\d.]+')
    ['10.99', '20.99', '15.99']
    >>> page.css('.product h3::text').re(r'Product (\d+)')
    ['1', '2', '3']
    ```
    다른 인수를 설명하기 위해 각 예에서 별도의 문자열을 사용하겠습니다.
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
    `TextHandler`를 사용하는 또 다른 장점입니다. `html_content`도 `TextHandler`를 반환하므로 HTML에 바로 정규식을 적용할 수 있습니다.
    ```python
    >>> page.html_content.re('div class=".*">(.*)</div')
    ['In stock: 5', 'In stock: 3', 'Out of stock']
    ```

- `.json()`은 내용을 빠르게 JSON 객체로 변환합니다. 변환할 수 없으면 오류를 발생시킵니다.
  ```python
  >>> page.css('#page-data::text').get()
    '\n      {\n        "lastUpdated": "2024-09-22T10:30:00Z",\n        "totalProducts": 3\n      }\n    '
  >>> page.css('#page-data::text').get().json()
    {'lastUpdated': '2024-09-22T10:30:00Z', 'totalProducts': 3}
  ```
  요소를 선택할 때 텍스트나 속성값 같은 텍스트 노드를 지정하지 않았다면, 요소의 텍스트 내용을 자동으로 사용합니다.
  ```python
  >>> page.css('#page-data')[0].json()
  {'lastUpdated': '2024-09-22T10:30:00Z', 'totalProducts': 3}
  ```
  [Selector](#selector)는 여기서 한 가지 기능을 더 제공합니다. 다음 페이지를 예로 들어 보겠습니다.
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
  [Selector](#selector)의 `get_all_text`는 앞서 설명했듯 `TextHandler`를 반환합니다.<br/><br/>
  다음처럼 실행하면,
  ```python
  >>> page.css('div::text').get().json()
  ```
  `div` 태그에 JSON으로 변환할 직접적인 텍스트가 없어 오류가 발생합니다. 이 태그에는 직접 들어 있는 텍스트가 전혀 없습니다.<br/><br/>
  이때 `get_all_text`를 사용하면 됩니다.
  ```python
  >>> page.css('div')[0].get_all_text(ignore_tags=[]).json()
    {'lastUpdated': '2024-09-22T10:30:00Z', 'totalProducts': 3}
  ```
  `ignore_tags`의 기본값이 `('script', 'style',)`이므로 여기서는 값을 따로 지정했습니다.<br/><br/>
  나중에 설명할 Fetcher에서도 관련된 동작이 있습니다. 다음과 같은 JSON 응답을 받았다고 가정해 보겠습니다.
  ```python
  >>> page = Selector("""{"some_key": "some_value"}""")
  ```
  [Selector](#selector)는 HTML 페이지에 맞춰져 있으므로, 이 응답을 잘못된 HTML로 보고 수정합니다. 따라서 `html_content`를 사용하면 다음 결과가 나옵니다.
  ```python
  >>> page.html_content
  '<html><body><p>{"some_key": "some_value"}</p></body></html>'
  ```
  하지만 `json` 메서드를 바로 호출하면 정상적으로 동작합니다.
  ```python
  >>> page.json()
  {'some_key': 'some_value'}
  ```
  `html` 태그에 직접적인 텍스트가 없는데 어떻게 가능한 걸까요?<br/>
  JSON 응답 같은 경우를 위해 [Selector](#selector)는 받은 내용의 원본 사본을 보관합니다. `.json()`은 먼저 원본을 확인하고 JSON으로 변환합니다. 개별 요소처럼 원본이 없으면 현재 요소의 텍스트를 확인하고, 필요하면 `get_all_text`를 사용합니다.<br/>

- `.clean()`은 공백 문자와 연속 공백을 제거하고 새 `TextHandler`를 반환합니다.
```python
>>> TextHandler('\n wonderful  idea, \reh?').clean()
'wonderful idea, eh?'
```
`remove_entities`를 전달하면 `clean`이 HTML 엔티티를 해당 문자로 바꿉니다.

- `.sort()`는 리스트처럼 문자열의 문자를 정렬합니다.
```python
>>> TextHandler('acb').sort()
'abc'
```
역순으로 정렬할 수도 있습니다.
```python
>>> TextHandler('acb').sort(reverse=True)
'cba'
```

앞으로 더 많은 메서드와 속성이 추가될 것입니다. 이 클래스는 라이브러리 거의 모든 곳에서 일반 문자열 대신 반환된다는 점을 기억하세요.

## TextHandlers {#texthandlers}
이 클래스는 [Selectors](#selectors)와 [Selector](#selector)의 관계와 비슷합니다. 일반 리스트의 동작을 상속하고 `re`, `re_first` 메서드를 추가합니다.

여기서 `re_first`는 각 [TextHandler](#texthandler)에 `re`를 실행해 첫 번째 결과를 반환합니다. 결과가 없으면 `None`을 반환합니다. 나머지는 앞의 설명과 같으며, 앞으로 다른 메서드도 추가될 것입니다.

## AttributesHandler {#attributeshandler}
Python의 표준 딕셔너리인 `dict`를 읽기 전용으로 만든 형태입니다. 각 요소, 즉 [Selector](#selector) 객체의 속성을 저장합니다.
```python
>>> print(page.find('script').attrib)
{'id': 'page-data', 'type': 'application/json'}
>>> type(page.find('script').attrib).__name__
'AttributesHandler'
```
읽기 전용이므로 일반 딕셔너리보다 리소스를 적게 사용합니다. 데이터를 변경하거나 덮어쓰는 기능을 제외하면 딕셔너리와 같은 메서드와 속성을 제공합니다.

현재 다음 두 가지 기능을 추가로 제공합니다.

- `search_values` 메서드.

    일반 딕셔너리에서는 `dict.get("key_name")`으로 키를 확인할 수 있지만, 값으로 검색하려면 코드가 더 필요합니다. 이 메서드는 속성값을 검색하고 일치하는 항목마다 딕셔너리를 반환합니다.
    
    간단한 예입니다.
    ```python
    >>> for i in page.find('script').attrib.search_values('page-data'):
            print(i)
    {'id': 'page-data'}
    ```
    `partial` 인수를 사용하면 값의 일부로 검색할 수도 있습니다.
    ```python
    >>> for i in page.find('script').attrib.search_values('page', partial=True):
            print(i)
    {'id': 'page-data'}
    ```
    위 예는 설명을 위한 것입니다. 실제로는 `find_all`과 함께 사용해 속성에 특정 값이 있는 요소를 모두 찾을 수 있습니다.
    ```python
    >>> page.find_all(lambda element: list(element.attrib.search_values('product')))
    [<data='<article class="product" data-id="1"><h3...' parent='<div class="product-list"> <article clas...'>,
     <data='<article class="product" data-id="2"><h3...' parent='<div class="product-list"> <article clas...'>,
     <data='<article class="product" data-id="3"><h3...' parent='<div class="product-list"> <article clas...'>]
    ```
    이 요소들의 `class` 속성값은 모두 'product'입니다.
    
    `search_values`는 제너레이터를 반환하므로 여기서는 `list`를 사용했습니다. 제너레이터 자체를 조건으로 쓰면 모든 요소에서 `True`가 되기 때문입니다.

- `json_string` 속성.

    현재 속성을 JSON 문자열로 변환합니다. JSON으로 변환할 수 없으면 오류를 발생시킵니다.
  
    ```python
    >>>page.find('script').attrib.json_string
    b'{"id":"page-data","type":"application/json"}'
    ```