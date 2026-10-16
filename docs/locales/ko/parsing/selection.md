---
title: "CSS, XPath, 텍스트, 정규식으로 HTML 데이터 추출하기"
description: "CSS, XPath, 텍스트, 정규식으로 HTML 요소를 선택하세요. Scrapling 예제를 통해 비슷한 요소를 찾고 필요한 값을 추출합니다."
---

# 요소 찾기 {#querying-elements}
`Selector`는 HTML을 파싱합니다. 적응형 기능이 XML에서는 작동하지 않기 때문입니다. XML, RSS, Atom 피드는 XML 파서를 사용해 각 피드 노드를 직접 전달하는 [XMLFeedSpider](../spiders/generic-templates.md#xmlfeedspider)를 사용하세요.

Scrapling에서 요소를 찾는 주요 방법은 다섯 가지입니다.

1. CSS3 선택자.
2. XPath 선택자.
3. 필터나 조건으로 찾기.
4. 특정 텍스트를 포함하는 요소 찾기.
5. 특정 정규식과 일치하는 내용을 가진 요소 찾기.

간접적으로 요소를 찾는 다른 방법도 있지만, 여기서는 주요 방법을 자세히 다룹니다. 이미 찾은 요소와 비슷한 요소를 찾는 기능도 설명합니다. [해당 섹션으로 바로 이동](#finding-similar-elements)할 수도 있습니다.

웹 스크래핑이 처음이고 선택자를 작성한 경험이 적다면, [여기서](#filters-based-searching) `find`/`find_all` 메서드부터 배우는 것을 권장합니다.

## CSS/XPath 선택자 {#cssxpath-selectors}

### CSS 선택자란? {#what-are-css-selectors}
[CSS](https://en.wikipedia.org/wiki/CSS)는 HTML 문서에 스타일을 적용하는 언어입니다. 선택자는 스타일을 적용할 HTML 요소를 지정합니다.

Scrapling은 [W3C 명세](http://www.w3.org/TR/2011/REC-css3-selectors-20110929/)에 따른 CSS3 선택자를 지원합니다. CSS 지원에는 `cssselect`를 사용하므로, [지원하는 선택자](https://cssselect.readthedocs.io/en/latest/#supported-selectors)와 의사 함수 및 의사 요소는 해당 문서를 참고하세요.

Scrapling은 다음과 같은 비표준 의사 요소도 지원합니다.

* 텍스트 노드는 ``::text``로 선택합니다.
* 속성값은 ``::attr(name)``으로 선택합니다. name은 값을 가져올 속성의 이름입니다.

Scrapy나 Parsel을 사용해 봤다면 익숙한 방식입니다. 많은 사용자가 이미 익숙한 방식을 굳이 바꿀 필요는 없으니까요 :)

CSS로 요소를 선택하려면 `css` 메서드를 사용합니다. 결과는 `Selectors`입니다. `[0]`으로 첫 번째 요소를 가져오거나, `.get()` / `.getall()`로 텍스트나 속성 선택 결과의 값을 추출할 수 있습니다.

### XPath 선택자란? {#what-are-xpath-selectors}
[XPath](https://en.wikipedia.org/wiki/XPath)는 XML 문서의 노드를 선택하는 언어이며 HTML에도 사용할 수 있습니다. 이 [요약표](https://devhints.io/xpath)는 [XPath](https://en.wikipedia.org/wiki/XPath)를 배우는 데 도움이 됩니다. Scrapling은 [lxml](https://lxml.de/)을 통해 XPath 선택자를 제공합니다.

CSS와 마찬가지로 Scrapy나 Parsel과 같은 방식입니다. 다만 Scrapling은 XPath 확장 함수 `has-class`를 제공하지 않습니다. 대신 반환된 요소에서 같은 목적으로 `has_class` 메서드를 사용할 수 있습니다.

XPath로 요소를 선택하려면 `xpath`를 사용합니다. 동작 방식은 위의 CSS 메서드와 같습니다.

> `css`와 `xpath`에는 적응형 기능을 위한 추가 인수도 있습니다. 적응형 기능은 별도 페이지에서 자세히 설명하므로 여기서는 다루지 않습니다.

### 선택자 예제 {#selectors-examples}
CSS와 XPath로 같은 작업을 하는 예를 보겠습니다.

클래스가 `product`인 모든 요소를 선택합니다.
```python
products = page.css('.product')
products = page.xpath('//*[@class="product"]')
```
!!! info "참고"

    요소에 다른 클래스도 있으면 이 XPath 예는 정확하지 않습니다. **클래스로 선택할 때는 CSS를 사용하는 편이 좋습니다.**

클래스가 `product`인 첫 번째 요소를 선택합니다.
```python
product = page.css('.product')[0]
product = page.xpath('//*[@class="product"]')[0]
```
태그가 `h1`인 첫 번째 요소의 텍스트를 가져옵니다.
```python
title = page.css('h1::text').get()
title = page.xpath('//h1//text()').get()
```
다음 코드와 같습니다.
```python
title = page.css('h1')[0].text
title = page.xpath('//h1')[0].text
```
태그가 `a`인 첫 번째 요소의 `href` 속성을 가져옵니다.
```python
link = page.css('a::attr(href)').get()
link = page.xpath('//a/@href').get()
```
클래스가 `product`인 요소 아래에서 `Phone`을 포함하는 첫 번째 `h1` 요소의 텍스트를 가져옵니다.
```python
title = page.css('.product h1:contains("Phone")::text').get()
title = page.xpath('//*[@class="product"]//h1[contains(text(),"Phone")]/text()').get()
```
결과가 있는 한 선택자를 중첩하거나 이어서 사용할 수 있습니다.
```python
page.css('.product')[0].css('h1:contains("Phone")::text').get()
page.xpath('//*[@class="product"]')[0].xpath('.//h1[contains(text(),"Phone")]/text()').get()
page.xpath('//*[@class="product"]')[0].css('h1:contains("Phone")::text').get()
```
현재 요소를 기준으로 XPath를 실행하려면 `.//`를 사용하세요. `//`로 시작하면 상품 요소를 선택한 뒤에도 문서 전체에서 검색합니다.

다른 예도 보겠습니다.

'href' 속성에 'image'가 들어 있는 모든 링크를 찾습니다.
```python
links = page.css('a[href*="image"]')
links = page.xpath('//a[contains(@href, "image")]')
for index, link in enumerate(links):
    link_value = link.attrib['href']  # Cleaner than link.css('::attr(href)').get()
    link_text = link.text
    print(f'Link number {index} points to this url {link_value} with text content as "{link_text}"')
```

## 텍스트 내용으로 선택하기 {#text-content-selection}
Scrapling은 요소에 직접 들어 있는 텍스트로 요소를 선택할 수 있습니다. 두 가지 방법이 있습니다.

1. `find_by_text`는 지정한 텍스트를 포함하는 요소를 찾으며 여러 옵션을 제공합니다.
2. `find_by_regex`는 지정한 정규식과 텍스트가 일치하는 요소를 찾으며 여러 옵션을 제공합니다.

정규식에 익숙하다면 `find_by_text`의 작업을 `find_by_regex`로도 할 수 있습니다. 하지만 모든 사용자가 쉽게 사용할 수 있도록 두 방법을 제공합니다.

`find_by_text`에는 첫 번째 인수로 텍스트를, `find_by_regex`에는 정규식을 전달합니다. 두 메서드는 다음 인수를 함께 지원합니다.

* **first_match**: `True`이면 첫 번째 결과만 반환합니다. 기본값도 같습니다.
* **case_sensitive**: `True`이면 대소문자를 구분합니다.
* **clean_match**: `True`이면 비교 전에 공백 문자와 연속 공백을 하나의 공백으로 바꿉니다.

`find_by_text`는 기본적으로 정확히 일치하는 텍스트를 찾습니다. 요소의 전체 텍스트가 입력한 텍스트와 같아야 합니다. 이를 바꾸는 추가 인수가 있습니다.

* **partial**: 켜면 `find_by_text`가 입력한 텍스트를 포함하는 요소를 반환합니다. 전체가 일치할 필요는 없습니다.

!!! abstract "참고"

    `find_by_regex`의 첫 번째 인수는 일반 문자열이나 컴파일된 정규식 모두 가능합니다. 아래 예에서 확인할 수 있습니다.

### 비슷한 요소 찾기 {#finding-similar-elements}
Scrapling은 이미 찾은 요소와 비슷한 요소를 찾을 수 있습니다. AutoScraper에서 아이디어를 얻었지만, Scrapling에서는 어떤 방법으로 찾은 요소에도 적용할 수 있습니다. 텍스트로 요소를 찾은 뒤 사용하는 경우가 많으므로 여기서 설명하겠습니다.

어떻게 작동할까요?

상품 이름으로 요소를 찾은 뒤, 같은 표나 컨테이너 안의 다른 상품도 추출하고 싶다고 가정해 보겠습니다. 찾은 요소에서 `.find_similar()`를 호출하면 Scrapling이 다음 작업을 합니다.

1. DOM 트리에서 같은 깊이에 있는 모든 요소를 찾습니다.
2. 태그 이름, 부모의 태그 이름, 조부모의 태그 이름이 같지 않은 요소를 제외합니다.
3. 이 단계에서는 원하는 요소일 가능성이 약 99%입니다. 마지막으로 속성의 유사도를 비교해 원래 요소와 충분히 비슷하지 않은 요소를 제외합니다. 이때 사용할 비율을 설정할 수 있지만, 기본 설정으로 원하는 요소를 찾지 못할 때만 바꾸는 것을 권장합니다.

설명이 길었지만 동작 원리를 알려드리고 싶었습니다. 다음 섹션에서 예를 보기 전에 메서드의 인수를 살펴보겠습니다.

* **similarity_threshold**: 3단계에서 속성을 비교하는 유사도 기준입니다. 기본값은 0.2로, 두 요소의 속성이 적어도 20% 비슷해야 한다는 뜻입니다. 0으로 설정하면 이 검사를 끌 수 있지만, 먼저 다른 인수도 읽어보세요.
* **ignore_attributes**: 마지막 비교에서 무시할 속성 이름입니다. 기본값은 `('href', 'src',)`입니다. URL은 요소마다 크게 달라질 수 있어 비교 기준으로 적합하지 않기 때문입니다.
* **match_text**: `True`이면 3단계에서 요소의 텍스트도 비교합니다. 일반적인 경우에는 권장하지 않지만 작업에 따라 유용할 수 있습니다.

이제 예제를 살펴보겠습니다.

### 예제 {#examples}
일반 텍스트와 정규식으로 요소를 찾는 예입니다.

여기서는 `Fetcher` 클래스를 사용합니다. 자세한 설명은 뒤에서 다룹니다.
```python
from scrapling.fetchers import Fetcher
page = Fetcher.get('https://books.toscrape.com/index.html')
```
텍스트가 지정한 문자열과 완전히 같은 첫 번째 요소를 찾습니다.
```python
>>> page.find_by_text('Tipping the Velvet')
<data='<a href="catalogue/tipping-the-velvet_99...' parent='<h3><a href="catalogue/tipping-the-velve...'>
```
`page.urljoin`을 사용해 상대 경로인 `href`를 전체 URL로 바꿉니다.
```python
>>> page.find_by_text('Tipping the Velvet').attrib['href']
'catalogue/tipping-the-velvet_999/index.html'
>>> page.urljoin(page.find_by_text('Tipping the Velvet').attrib['href'])
'https://books.toscrape.com/catalogue/tipping-the-velvet_999/index.html'
```
일치하는 요소가 여러 개라면 모두 가져옵니다. 결과가 리스트라는 점에 주목하세요.
```python
>>> page.find_by_text('Tipping the Velvet', first_match=False)
[<data='<a href="catalogue/tipping-the-velvet_99...' parent='<h3><a href="catalogue/tipping-the-velve...'>]
```
부분 일치를 사용해 `the`를 포함하는 모든 요소를 가져옵니다.
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
대소문자를 구분하지 않으므로 결과에는 소문자 `the`뿐 아니라 `The`도 있습니다. `the`만 포함하는 요소로 제한해 보겠습니다.
```python
>>> results = page.find_by_text('the', partial=True, first_match=False, case_sensitive=True)
>>> [i.text for i in results]
['A Light in the ...',
 'Tipping the Velvet',
 'The Boys in the ...',
 "It's Only the Himalayas"]
```
가격을 찾는 정규식과 텍스트가 일치하는 첫 번째 요소를 가져옵니다.
```python
>>> page.find_by_regex(r'£[\d\.]+')
<data='<p class="price_color">£51.77</p>' parent='<div class="product_price"> <p class="pr...'>
>>> page.find_by_regex(r'£[\d\.]+').text
'£51.77'
```
컴파일된 정규식을 전달해도 같습니다. Scrapling이 입력 타입을 알아서 처리합니다.
```python
>>> import re
>>> regex = re.compile(r'£[\d\.]+')
>>> page.find_by_regex(regex)
<data='<p class="price_color">£51.77</p>' parent='<div class="product_price"> <p class="pr...'>
>>> page.find_by_regex(regex).text
'£51.77'
```
정규식과 일치하는 모든 요소를 가져옵니다.
```python
>>> page.find_by_regex(r'£[\d\.]+', first_match=False)
[<data='<p class="price_color">£51.77</p>' parent='<div class="product_price"> <p class="pr...'>,
 <data='<p class="price_color">£53.74</p>' parent='<div class="product_price"> <p class="pr...'>,
 <data='<p class="price_color">£50.10</p>' parent='<div class="product_price"> <p class="pr...'>,
 <data='<p class="price_color">£47.82</p>' parent='<div class="product_price"> <p class="pr...'>,
 ...]
```
이런 식으로 사용할 수 있습니다.

현재 요소와 위치 및 속성이 비슷한 모든 요소를 찾습니다. 여기서는 'title' 속성을 비교에서 제외합니다.
```python
>>> element = page.find_by_text('Tipping the Velvet')
>>> element.find_similar(ignore_attributes=['title'])
[<data='<a href="catalogue/a-light-in-the-attic_...' parent='<h3><a href="catalogue/a-light-in-the-at...'>,
 <data='<a href="catalogue/soumission_998/index....' parent='<h3><a href="catalogue/soumission_998/in...'>,
 <data='<a href="catalogue/sharp-objects_997/ind...' parent='<h3><a href="catalogue/sharp-objects_997...'>,
...]
```
요소가 20개가 아니라 19개인 이유는 현재 요소 자체는 결과에 포함되지 않기 때문입니다.
```python
>>> len(element.find_similar(ignore_attributes=['title']))
19
```
비슷한 모든 요소의 `href` 속성을 가져옵니다.
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
조금 더 복잡한 예로, 찾은 요소를 시작점으로 삼아 모든 책의 데이터를 가져와 보겠습니다.
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
### 고급 예제 {#advanced-examples}
`find_similar`를 사용하는 더 복잡하고 실용적인 예입니다.

쇼핑몰 상품 추출:
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
표의 행 추출:
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
폼 필드 추출:
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
사이트의 리뷰 추출:
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
## 필터로 찾기 {#filters-based-searching}
이 방법은 기능이 다양하면서도 선택자를 작성하는 것보다 배우기 쉬워, 스크래핑을 처음 시작할 때 특히 유용합니다.

BeautifulSoup의 `find_all`에서 아이디어를 얻은 `find_all`과 `find`는 여러 필터를 받고, 모든 조건에 맞는 요소를 찾습니다.

인수는 다음과 같이 해석합니다.

* 문자열은 태그 이름으로 봅니다.
* List/Tuple/Set 같은 반복 가능한 객체는 태그 이름의 모음으로 봅니다.
* 딕셔너리는 HTML 요소의 속성 이름과 값을 나타냅니다.
* 정규식은 `find_by_regex`처럼 요소의 내용으로 필터링합니다.
* 함수는 요소를 필터링하는 조건으로 사용합니다.
* 키워드 인수는 HTML 속성 이름과 값으로 봅니다.

전달한 인수를 모아 필터를 차례로 적용합니다. 각 필터의 결과가 다음 필터로 전달됩니다.

현재 페이지나 요소 안에서 다음 순서로 필터링합니다.

1. 전달한 태그 이름에 맞는 요소를 모읍니다.
2. 전달한 모든 속성과 일치하는 요소를 모읍니다. 앞 단계가 있었다면 그 결과만 필터링합니다.
3. 전달한 모든 정규식과 일치하는 요소를 모읍니다. 앞 단계가 있었다면 그 결과만 필터링합니다.
4. 전달한 모든 함수의 조건을 만족하는 요소를 모읍니다. 앞 단계가 있었다면 그 결과만 필터링합니다.

!!! note "참고"

    1. 위 순서에서 처음으로 주어진 필터부터 시작합니다. 태그 이름 없이 속성만 전달했다면 2단계부터 시작합니다.
    2. 인수를 전달한 순서는 영향을 주지 않습니다. 위에서 설명한 순서만 사용합니다.

예제를 보면 더 쉽게 이해할 수 있습니다 :)

### 예제 {#examples_1}
```python
from scrapling.fetchers import Fetcher
page = Fetcher.get('https://quotes.toscrape.com/')
```
태그가 `div`인 모든 요소를 찾습니다.
```python
>>> page.find_all('div')
[<data='<div class="container"> <div class="row...' parent='<body> <div class="container"> <div clas...'>,
 <data='<div class="row header-box"> <div class=...' parent='<div class="container"> <div class="row...'>,
...]
```
클래스가 `quote`인 모든 div 요소를 찾습니다.
```python
>>> page.find_all('div', class_='quote')
[<data='<div class="quote" itemscope itemtype="h...' parent='<div class="col-md-8"> <div class="quote...'>,
 <data='<div class="quote" itemscope itemtype="h...' parent='<div class="col-md-8"> <div class="quote...'>,
...]
```
위와 같은 작업입니다.
```python
>>> page.find_all('div', {'class': 'quote'})
[<data='<div class="quote" itemscope itemtype="h...' parent='<div class="col-md-8"> <div class="quote...'>,
 <data='<div class="quote" itemscope itemtype="h...' parent='<div class="col-md-8"> <div class="quote...'>,
...]
```
클래스가 `quote`인 모든 요소를 찾습니다.
```python
>>> page.find_all({'class': 'quote'})
[<data='<div class="quote" itemscope itemtype="h...' parent='<div class="col-md-8"> <div class="quote...'>,
 <data='<div class="quote" itemscope itemtype="h...' parent='<div class="col-md-8"> <div class="quote...'>,
...]
```
클래스가 `quote`인 div 중, 내용에 'world'가 있는 `.text` 요소를 포함하는 것을 찾습니다.
```python
>>> page.find_all('div', {'class': 'quote'}, lambda e: "world" in e.css('.text::text').get())
[<data='<div class="quote" itemscope itemtype="h...' parent='<div class="col-md-8"> <div class="quote...'>]
```
자식이 있는 모든 요소를 찾습니다.
```python
>>> page.find_all(lambda element: len(element.children) > 0)
[<data='<html lang="en"><head><meta charset="UTF...'>,
 <data='<head><meta charset="UTF-8"><title>Quote...' parent='<html lang="en"><head><meta charset="UTF...'>,
 <data='<body> <div class="container"> <div clas...' parent='<html lang="en"><head><meta charset="UTF...'>,
...]
```
내용에 'world'가 있는 모든 요소를 찾습니다.
```python
>>> page.find_all(lambda element: "world" in element.text)
[<data='<span class="text" itemprop="text">“The...' parent='<div class="quote" itemscope itemtype="h...'>,
 <data='<a class="tag" href="/tag/world/page/1/"...' parent='<div class="tags"> Tags: <meta class="ke...'>]
```
지정한 정규식과 일치하는 모든 span 요소를 찾습니다.
```python
>>> page.find_all('span', re.compile(r'world'))
[<data='<span class="text" itemprop="text">“The...' parent='<div class="quote" itemscope itemtype="h...'>]
```
클래스가 'quote'인 div와 span을 찾습니다. 해당 span이 없으므로 div만 반환됩니다.
```python
>>> page.find_all(['div', 'span'], {'class': 'quote'})
[<data='<div class="quote" itemscope itemtype="h...' parent='<div class="col-md-8"> <div class="quote...'>,
 <data='<div class="quote" itemscope itemtype="h...' parent='<div class="col-md-8"> <div class="quote...'>,
...]
```
여러 조건을 섞어 사용할 수도 있습니다.
```python
>>> page.find_all({'itemtype':"http://schema.org/CreativeWork"}, 'div').css('.author::text').getall()
['Albert Einstein',
 'J.K. Rowling',
...]
```
추가 팁: `href` 속성값이 'Einstein'으로 끝나는 모든 요소를 찾습니다.
```python
>>> page.find_all({'href$': 'Einstein'})
[<data='<a href="/author/Albert-Einstein">(about...' parent='<span>by <small class="author" itemprop=...'>,
 <data='<a href="/author/Albert-Einstein">(about...' parent='<span>by <small class="author" itemprop=...'>,
 <data='<a href="/author/Albert-Einstein">(about...' parent='<span>by <small class="author" itemprop=...'>]
```
또 다른 팁: `href` 속성값에 '/author/'가 포함된 모든 요소를 찾습니다.
```python
>>> page.find_all({'href*': '/author/'})
[<data='<a href="/author/Albert-Einstein">(about...' parent='<span>by <small class="author" itemprop=...'>,
 <data='<a href="/author/J-K-Rowling">(about)</a...' parent='<span>by <small class="author" itemprop=...'>,
 <data='<a href="/author/Albert-Einstein">(about...' parent='<span>by <small class="author" itemprop=...'>,
...]
```
이런 식으로 사용할 수 있습니다.

## 선택자 생성하기 {#generating-selectors}
어떤 방법으로 찾은 요소든 CSS/XPath 선택자를 생성할 수 있습니다. 생성한 선택자는 이곳이나 다른 도구에서 다시 사용할 수 있습니다.

`url_element`의 짧은 CSS 선택자를 만듭니다. 줄일 수 없으면 전체 선택자를 만듭니다.
```python
>>> url_element = page.find({'href*': '/author/'})
>>> url_element.generate_css_selector
'body > div > div:nth-of-type(2) > div > div > span:nth-of-type(2) > a'
```
페이지 시작부터 `url_element`까지의 전체 CSS 선택자를 만듭니다.
```python
>>> url_element.generate_full_css_selector
'body > div > div:nth-of-type(2) > div > div > span:nth-of-type(2) > a'
```
`url_element`의 짧은 XPath 선택자를 만듭니다. 줄일 수 없으면 전체 선택자를 만듭니다.
```python
>>> url_element.generate_xpath_selector
'//body/div/div[2]/div/div/span[2]/a'
```
페이지 시작부터 `url_element`까지의 전체 XPath 선택자를 만듭니다.
```python
>>> url_element.generate_full_xpath_selector
'//body/div/div[2]/div/div/span[2]/a'
```
!!! abstract "참고"

    짧은 선택자를 만들 때 Scrapling은 `id` 속성이 있는 요소처럼 고유하게 식별할 수 있는 요소를 찾아 경로의 시작점으로 사용합니다. 이 예에서는 그런 요소가 없어 짧은 선택자와 전체 선택자가 같습니다.

## 선택자와 정규식 함께 사용하기 {#using-selectors-with-regular-expressions}
`parsel`/`scrapy`처럼 `re`와 `re_first`로 정규식을 사용해 데이터를 추출할 수 있습니다. 하지만 Scrapling에서는 `Selector`/`Selectors`/`TextHandler`, `TextHandlers` 등 거의 모든 클래스가 이 메서드를 제공합니다. 따라서 텍스트 노드를 선택하지 않아도 요소에 바로 사용할 수 있습니다.

[TextHandler](main_classes.md#texthandler)를 설명할 때 자세히 다룹니다. 기본 사용법은 다음과 같습니다.
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
이제 대략적인 사용법을 알 수 있을 것입니다. 다음 페이지에서 [TextHandler](main_classes.md#texthandler)와 함께 더 자세히 설명하겠습니다.