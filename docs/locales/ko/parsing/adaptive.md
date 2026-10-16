---
title: "적응형 파싱으로 HTML 요소를 추적하고 다시 찾기"
description: "요소의 특징을 저장하고 HTML이 바뀐 뒤에도 일치하는 요소를 찾으세요. 적응형 파싱을 켜고 save, retrieve, relocate를 사용하는 방법을 알아봅니다."
---

# 적응형 스크래핑 {#adaptive-scraping}

!!! success "사전 준비"

    1. [요소 찾기](../parsing/selection.md)를 읽고 [Selector](../parsing/main_classes.md#selector) 객체에서 요소를 찾고 추출하는 방법을 알아두세요.
    2. [주요 클래스](../parsing/main_classes.md)를 읽고 [Selector](../parsing/main_classes.md#selector) 클래스를 알아두세요.

적응형 스크래핑은 이전에 automatch라고 불렸던 Scrapling의 강력한 기능입니다. 요소를 추적하고 다시 찾아서 사이트가 바뀌어도 스크래퍼가 계속 작동하도록 돕습니다.

다음과 같은 구조의 페이지에서 데이터를 수집한다고 가정해 보겠습니다.
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
ID가 `p1`인 첫 번째 상품을 추출하려면 다음과 같은 선택자를 작성할 것입니다.
```python
page.css('#p1')
```
그런데 사이트 운영자가 구조를 다음처럼 바꾸면,
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
선택자가 더는 작동하지 않아 코드를 수정해야 합니다. 이때 Scrapling의 `adaptive` 기능이 도움이 됩니다.

Scrapling에서는 요소를 처음 선택할 때 `adaptive` 기능을 켤 수 있습니다. 다음에 같은 요소를 선택했는데 찾지 못하면, 저장한 특징을 바탕으로 사이트에서 가장 비슷한 요소를 찾습니다. AI 없이도 가능합니다 :)

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
먼저 사용 예를 보고, 이후에 사용법과 동작 원리를 자세히 설명하겠습니다. 이 기능은 CSS/XPath뿐 아니라 모든 요소 선택 방법에서 사용할 수 있습니다.

## 실제 사이트를 사용한 예 {#real-world-scenario}
실제 사이트를 예로 들어 Fetcher로 소스를 가져와 보겠습니다. 원래라면 디자인이나 구조를 바꾸기 직전인 사이트를 찾아 소스를 저장하고 변경을 기다려야 합니다. 사이트 운영자를 알지 못하면 변경 시점을 미리 알기는 거의 불가능합니다. 운영자를 안다면 연출한 테스트가 되겠죠 :)

그래서 [The Web Archive](https://archive.org/)의 [Wayback Machine](https://web.archive.org/)을 사용하겠습니다. [2010년 StackOverFlow 사이트](https://web.archive.org/web/20100102003420/http://stackoverflow.com/)의 사본입니다. 꽤 오래됐죠?</br>같은 선택자로 2010년 디자인과 현재 디자인에서 동일한 버튼을 찾을 수 있는지 확인해 보겠습니다 :)

이전 디자인에서 Questions 버튼을 추출하려면 `#hmenus > div:nth-child(1) > ul > li:nth-child(1) > a` 같은 선택자를 사용할 수 있습니다. Google Chrome이 생성한 선택자라 지나치게 구체적입니다.


이제 두 버전에서 같은 선택자를 시험해 보겠습니다.
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
여기서는 `adaptive_domain`이라는 새 인수를 사용했습니다. Scrapling은 두 도메인(`archive.org`와 `stackoverflow.com`)을 다른 사이트로 보므로 `adaptive` 데이터를 따로 저장합니다. 두 주소가 같은 사이트임을 알려주려면, 양쪽의 `adaptive` 데이터를 저장할 때 같은 사용자 지정 도메인을 전달해야 합니다.

실제 상황에서도 코드는 같지만 두 요청에 같은 URL을 사용하므로 `adaptive_domain`은 필요하지 않습니다. 가능한 한 실제 상황에 가깝게 만든 예입니다. 이해하는 데 도움이 되었으면 좋겠습니다 :)

위의 두 예에서는 `Selector`와 `Fetcher` 클래스를 모두 사용해 적응형 기능의 동작 방식이 같다는 것을 보여줍니다.

!!! info "정보"

    `adaptive_domain`은 사이트가 디자인이나 구조와 함께 URL도 바꿀 때를 위해 만들었습니다. 이 인수를 사용하면 새 URL에서도 이전에 저장한 적응형 데이터를 계속 사용할 수 있습니다. 그렇지 않으면 Scrapling은 새 사이트로 판단하고 이전 데이터를 사용하지 않습니다.

## 적응형 스크래핑의 동작 원리 {#how-the-adaptive-scraping-feature-works}
적응형 스크래핑은 두 단계로 동작합니다.

1. **저장 단계**: 요소를 구분하는 특징을 저장합니다.
2. **일치 요소 찾기 단계**: 나중에 비슷한 특징을 가진 요소를 찾습니다.

어떤 방법으로든 요소를 선택한 뒤, 다음에 사이트를 수집할 때 구조나 디자인이 바뀌어도 같은 요소를 찾고 싶다고 가정해 보겠습니다.

기술적인 설명을 줄이면 다음과 같습니다.

  1. 아래에서 설명할 방법 중 하나로 요소의 특징을 저장하도록 Scrapling에 요청합니다.
  2. Scrapling은 설정된 데이터베이스에 각 요소의 특징을 저장합니다. 기본값은 SQLite입니다.
  3. 사이트 운영자는 요소의 모든 속성을 바꾸거나 지울 수 있습니다. 따라서 요소 자체의 속성을 데이터베이스의 고정 식별자로 사용할 수 없습니다. 이를 해결하기 위해 저장 시스템은 두 가지 값을 사용합니다.
     1. 현재 사이트의 도메인입니다. `Selector`를 사용한다면 초기화할 때 전달하세요. Fetcher는 URL에서 도메인을 자동으로 가져옵니다.
     2. 데이터베이스에서 요소의 특징을 조회할 `identifier`입니다. 항상 직접 지정해야 하는 것은 아니며, 뒤에서 설명합니다.

     나중에 이 두 값을 함께 사용해 저장된 요소의 특징을 불러옵니다.

  4. 사이트 구조가 바뀌면 `adaptive`를 켜서 요소를 찾습니다. Scrapling은 저장한 특징을 불러와 페이지의 모든 요소와 비교하고, 원하는 요소와의 유사도를 계산합니다. 아래에서 보듯 여러 특징을 모두 고려합니다.
  5. 가장 비슷한 요소를 반환합니다. 점수가 같은 요소가 여러 개라면 함께 반환합니다.

### 요소를 구분하는 특징 {#the-unique-properties}
요소의 모든 속성이 바뀌거나 사라질 수 있는데 어떤 특징을 저장하는지 궁금할 수 있습니다.

Scrapling은 다음 특징을 사용합니다.

- 요소의 태그 이름, 텍스트, 속성의 이름과 값, 형제 요소의 태그 이름, 경로에 있는 태그 이름.
- 부모 요소의 태그 이름, 속성의 이름과 값, 텍스트.

완전히 같은지를 비교하는 것이 아니라 값이 얼마나 비슷한지를 비교합니다. 값의 순서도 고려합니다. 예를 들어 변경 전후에 요소의 클래스 이름이 어떤 순서로 쓰였는지도 비교합니다.

## 적응형 기능 사용하기 {#how-to-use-adaptive-feature}
적응형 기능은 찾은 모든 요소에 적용할 수 있습니다. 위에서 본 것처럼 CSS/XPath 선택 메서드의 인수로도 사용할 수 있으며, 뒤에서 다시 살펴보겠습니다.

먼저 [Selector](main_classes.md#selector)를 초기화할 때 `adaptive=True`를 전달해 `adaptive`를 켜세요. 또는 사용하는 Fetcher에서 같은 기능을 켜면 됩니다.

예를 들면 다음과 같습니다.
```python
from scrapling import Selector, Fetcher
page = Selector(html_doc, adaptive=True)
# OR
Fetcher.adaptive = True
page = Fetcher.get('https://example.com')
```
[Selector](main_classes.md#selector)를 사용할 때는 사이트 URL을 `url` 인수로 전달하세요. Scrapling이 각 요소의 특징을 도메인별로 구분해서 저장할 수 있습니다.

URL을 전달하지 않으면 요소의 특징을 저장할 때 URL 대신 `default`라는 값을 사용합니다. 나중에 다른 사이트에서 같은 식별자를 쓰면서 URL도 전달하지 않으면 문제가 생길 수 있습니다. 저장할 때 이전 데이터를 덮어쓰며, `adaptive`는 가장 최근에 저장한 특징만 사용합니다.

`storage`와 `storage_args`는 데이터베이스 연결을 설정하는 인수입니다. 기본적으로 라이브러리가 제공하는 SQLite 클래스를 사용합니다. 직접 저장 시스템을 만들 때만 필요한 설정이며, [개발 섹션의 별도 페이지](../development/adaptive_storage_system.md)에서 설명합니다.

이제 `adaptive`를 전체 설정에서 켰으므로 두 가지 주요 방법으로 사용할 수 있습니다.

### CSS/XPath 선택으로 사용하기 {#the-cssxpath-selection-way}
위 예처럼 페이지에 요소가 아직 있을 때 `auto_save` 인수로 특징을 저장합니다.
```python
element = page.css('#p1', auto_save=True)
```
요소가 더는 선택되지 않으면 같은 선택자에 `adaptive` 인수를 사용해 다시 찾을 수 있습니다.
```python
element = page.css('#p1', adaptive=True)
```
간단하죠?

내부에서는 여러 작업이 일어납니다. 요소의 특징을 다시 불러오기 위해 필요한 식별자를 기억하시나요? `css`/`xpath` 메서드는 편의를 위해 전달한 선택자를 식별자로 자동 사용합니다 :)

이 메서드들에 `identifier` 인수를 전달하면 식별자를 직접 지정할 수도 있습니다. `auto_save`로 특징을 저장할 때를 비롯해 여러 상황에서 유용합니다.

### 직접 저장하고 찾기 {#the-manual-way}
요소의 특징을 직접 저장하고 불러온 뒤, `adaptive` 기능으로 요소를 다시 찾을 수 있습니다. 이렇게 하면 어떤 방법으로 선택한 요소라도 다시 찾을 수 있습니다.

먼저 텍스트로 요소를 찾았다고 가정하겠습니다.
```python
element = page.find_by_text('Tipping the Velvet', first_match=True)
```
`save` 메서드로 특징을 저장할 수 있습니다. 이때는 식별자를 직접 지정해야 합니다. 예에서는 `my_special_element`를 사용했지만, 실제 코드에서는 변수 이름처럼 의미가 분명한 이름을 쓰는 것이 좋습니다 :)
```python
page.save(element, 'my_special_element')
```
나중에 특징을 불러와 `adaptive`로 페이지에서 요소를 다시 찾으려면 다음처럼 작성합니다.
```python
>>> element_dict = page.retrieve('my_special_element')
>>> page.relocate(element_dict, selector_type=True)
[<data='<a href="catalogue/tipping-the-velvet_99...' parent='<h3><a href="catalogue/tipping-the-velve...'>]
>>> page.relocate(element_dict, selector_type=True).css('::text').getall()
['Tipping the Velvet']
```
여기서는 `retrieve`와 `relocate` 메서드를 사용합니다.

결과를 `lxml.etree` 객체로 유지하려면 `selector_type` 인수를 생략하세요.
```python
>>> page.relocate(element_dict)
[<Element a at 0x105a2a7b0>]
```

## 문제 해결 {#troubleshooting}

### 일치하는 요소가 없을 때 {#no-matches-found}
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

### 다른 요소가 선택될 때 {#wrong-elements-matched}
```python
# Use more specific selectors
products = page.css('.product-list .product', auto_save=True)

# Or save with more context
product = page.find_by_text('Product Name').parent
page.save(product, 'specific_product')
```

## 알려진 제한 사항 {#known-issues}
`adaptive`로 저장할 때는 선택 결과의 첫 번째 요소에 대한 특징만 저장합니다. 선택자가 페이지의 여러 위치에서 다른 요소들을 선택하더라도, 나중에 `adaptive`로 다시 찾으면 첫 번째 요소만 반환합니다. 쉼표로 묶은 CSS 선택자는 예외입니다. 각 선택자를 분리해 따로 실행하기 때문입니다.

## 마무리 {#final-thoughts}
이 기능을 쉽고 자세하게 설명하기가 생각보다 어려웠습니다. 아직 궁금한 점이 있다면 [토론 게시판](https://github.com/D4Vinci/Scrapling/discussions), Discord 서버 또는 개인 메시지로 알려주세요. 가능한 한 빨리 답하겠습니다 :)