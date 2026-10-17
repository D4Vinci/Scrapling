---
title: "CSS、XPath、テキスト、正規表現で HTML データを抽出する"
description: "CSS、XPath、テキスト、正規表現で HTML 要素を選びます。Scrapling のコード例で、似た要素の検索とデータ抽出を学べます。"
---

# 要素の検索 {#querying-elements}
`Selector` は HTML を解析します。適応型機能が XML では動かないためです。XML、RSS、Atom フィードには [XMLFeedSpider](../spiders/generic-templates.md#xmlfeedspider) を使ってください。XML パーサーを使い、各フィードのノードを直接渡します。

Scrapling には、主に 5 つの要素の探し方があります。

1. CSS3 セレクター
2. XPath セレクター
3. フィルターや条件による検索
4. 指定したテキストを含む要素の検索
5. 指定した正規表現に一致する内容を持つ要素の検索

間接的な探し方もありますが、ここでは主な方法を詳しく説明します。さらに、すでに見つけた要素に似た要素を探す機能も紹介します。[その説明へ直接移動](#finding-similar-elements)することもできます。

Web スクレイピングを始めたばかりで、セレクターを書いた経験が少ない場合は、まず `find`/`find_all` を学ぶのがおすすめです。[こちらで説明します](#filters-based-searching)。

## CSS/XPath セレクター {#cssxpath-selectors}

### CSS セレクターとは？ {#what-are-css-selectors}
[CSS](https://en.wikipedia.org/wiki/CSS) は HTML の見た目を設定する言語です。セレクターを使い、スタイルを特定の HTML 要素に結び付けます。

Scrapling は [W3C 仕様](http://www.w3.org/TR/2011/REC-css3-selectors-20110929/)に沿った CSS3 セレクターを使えます。対応は `cssselect` によるものなので、[対応するセレクター](https://cssselect.readthedocs.io/en/latest/#supported-selectors)や疑似関数、疑似要素については、その資料を参照してください。

Scrapling は、標準外の次の疑似要素も使えます。

* テキストノードの選択には ``::text`` を使います。
* 属性値の選択には ``::attr(name)`` を使います。name は値を取得する属性の名前です。

Scrapy や Parsel を使っていた方なら、同じ選択の仕組みを使えます。別の方式を学び直す必要はありません :)

CSS で選ぶには `css` を使います。戻り値は `Selectors` です。最初の要素は `[0]` で取得できます。テキストや属性の疑似セレクターから値を読むには、`.get()` / `.getall()` を使います。

### XPath セレクターとは？ {#what-are-xpath-selectors}
[XPath](https://en.wikipedia.org/wiki/XPath) は XML 文書のノードを選ぶ言語で、HTML にも使えます。[XPath](https://en.wikipedia.org/wiki/XPath) を学ぶには、この[早見表](https://devhints.io/xpath)が便利です。Scrapling は [lxml](https://lxml.de/) を通じて XPath を直接使います。

CSS と同じく、Scrapy や Parsel と共通の使い方です。ただし、XPath 拡張関数の `has-class` はありません。代わりに、取得した要素の `has_class` メソッドで同じ確認ができます。

XPath で選ぶには `xpath` を使います。上の CSS メソッドと同じ考え方で使えます。

> `css` と `xpath` には、適応型機能向けの追加引数があります。ここでは省き、後で専用のページで詳しく説明します。

### セレクターの例 {#selectors-examples}
CSS と XPath の使い方を並べて見てみましょう。

クラスが `product` のすべての要素を選びます。
```python
products = page.css('.product')
products = page.xpath('//*[@class="product"]')
```
!!! info "注意："

    この XPath は、別のクラスも付いている場合に正しく選べません。**クラスで選ぶなら、CSS を使うほうが確実です。**

クラスが `product` の最初の要素を選びます。
```python
product = page.css('.product')[0]
product = page.xpath('//*[@class="product"]')[0]
```
最初の `h1` 要素のテキストを取得します。
```python
title = page.css('h1::text').get()
title = page.xpath('//h1//text()').get()
```
これは次と同じです。
```python
title = page.css('h1')[0].text
title = page.xpath('//h1')[0].text
```
最初の `a` 要素の `href` 属性を取得します。
```python
link = page.css('a::attr(href)').get()
link = page.xpath('//a/@href').get()
```
`Phone` を含み、クラスが `product` の要素内にある、最初の `h1` のテキストを取得します。
```python
title = page.css('.product h1:contains("Phone")::text').get()
title = page.xpath('//*[@class="product"]//h1[contains(text(),"Phone")]/text()').get()
```
結果が返る限り、セレクターは自由に入れ子にしたり、つなげたりできます。
```python
page.css('.product')[0].css('h1:contains("Phone")::text').get()
page.xpath('//*[@class="product"]')[0].xpath('.//h1[contains(text(),"Phone")]/text()').get()
page.xpath('//*[@class="product"]')[0].css('h1:contains("Phone")::text').get()
```
現在の要素を基準にする XPath には `.//` を使います。先頭の `//` は、商品を選んだ後でも文書全体を検索します。

別の例です。

'href' 属性に 'image' が含まれるすべてのリンクを探します。
```python
links = page.css('a[href*="image"]')
links = page.xpath('//a[contains(@href, "image")]')
for index, link in enumerate(links):
    link_value = link.attrib['href']  # Cleaner than link.css('::attr(href)').get()
    link_text = link.text
    print(f'Link number {index} points to this url {link_value} with text content as "{link_text}"')
```

## テキスト内容で選ぶ {#text-content-selection}
Scrapling では、要素の直接のテキスト内容から選ぶこともできます。次の 2 つの方法があります。

1. `find_by_text` で、指定したテキストを含む要素を探します。複数の引数で動作を調整できます。
2. `find_by_regex` で、指定した正規表現に一致するテキストを持つ要素を探します。こちらにも複数の設定があります。

正規表現に慣れていれば、`find_by_text` でできることは `find_by_regex` でもできます。ただ、誰でも使いやすいように両方を用意しています。

`find_by_text` の最初の引数はテキスト、`find_by_regex` では正規表現です。次の引数は共通です。

* **first_match**：`True` なら最初の結果だけを返します。これが標準です。
* **case_sensitive**：`True` なら大文字と小文字を区別します。
* **clean_match**：`True` なら、照合前に空白文字や連続した空白を 1 つの空白に置き換えます。

標準の `find_by_text` は完全一致で探します。要素のテキスト全体が、指定したテキストと同じである必要があります。これを変えるため、次の引数があります。

* **partial**：有効にすると、`find_by_text` は指定したテキストを含む要素を返します。全体が一致する必要はありません。

!!! abstract "注意："

    `find_by_regex` は、最初の引数に通常の文字列とコンパイル済みの正規表現のどちらも受け取れます。後の例で紹介します。

### 似た要素を探す {#finding-similar-elements}
Scrapling では、すでに見つけた要素に似た要素を探せます。AutoScraper から着想を得た機能ですが、Scrapling ではどの方法で見つけた要素にも使えます。テキストで要素を見つけた後に使うことが多いため、ここで説明します。

どのように動くのでしょうか。

たとえば、商品の名前で 1 つの商品を見つけ、同じ表やコンテナー内のほかの商品も抽出したいとします。その要素で `.find_similar()` を呼ぶと、次の処理を行います。

1. DOM ツリー上で同じ深さにあるすべての要素を探します。
2. 要素自身、親、祖父母のタグ名を調べ、いずれかが異なるものを除外します。
3. ここまでで約 99% は目的の要素と考えられますが、最後に属性をあいまい照合し、似ていないものを除外します。この段階には類似度のしきい値があります。標準設定で目的の要素が得られない場合以外は、変更しないことをおすすめします。

説明が長くなりましたが、仕組みを知るために必要な部分です。次に例を示しますが、その前に引数を紹介します。

* **similarity_threshold**：手順 3 で属性を比較するときのしきい値です。標準値は 0.2 で、両方の属性が少なくとも 20% 似ている必要があります。0 にすると、この確認、つまり手順 3 を省けます。ただし、先にほかの引数も確認してください。
* **ignore_attributes**：最後の比較で無視する属性名です。標準は `('href', 'src',)` です。URL は要素ごとの差が大きく、比較の基準として安定しないためです。
* **match_text**：`True` なら、手順 3 でテキスト内容も比較します。通常はおすすめしませんが、用途によっては役立ちます。

それでは例を見てみましょう。

### 例 {#examples}
テキストと正規表現による検索を紹介します。

ここでは `Fetcher` を使います。詳しい説明は後のページにあります。
```python
from scrapling.fetchers import Fetcher
page = Fetcher.get('https://books.toscrape.com/index.html')
```
指定したテキストに完全一致する、最初の要素を探します。
```python
>>> page.find_by_text('Tipping the Velvet')
<data='<a href="catalogue/tipping-the-velvet_99...' parent='<h3><a href="catalogue/tipping-the-velve...'>
```
`page.urljoin` と組み合わせ、相対的な `href` から完全な URL を作ります。
```python
>>> page.find_by_text('Tipping the Velvet').attrib['href']
'catalogue/tipping-the-velvet_999/index.html'
>>> page.urljoin(page.find_by_text('Tipping the Velvet').attrib['href'])
'https://books.toscrape.com/catalogue/tipping-the-velvet_999/index.html'
```
複数の一致があれば、すべてを取得します。戻り値はリストです。
```python
>>> page.find_by_text('Tipping the Velvet', first_match=False)
[<data='<a href="catalogue/tipping-the-velvet_99...' parent='<h3><a href="catalogue/tipping-the-velve...'>]
```
`the` を含むすべての要素を取得します。部分一致の検索です。
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
標準では大文字と小文字を区別しないので、`the` だけでなく `The` も含まれます。小文字の `the` だけに絞ってみます。
```python
>>> results = page.find_by_text('the', partial=True, first_match=False, case_sensitive=True)
>>> [i.text for i in results]
['A Light in the ...',
 'Tipping the Velvet',
 'The Boys in the ...',
 "It's Only the Himalayas"]
```
価格の正規表現に一致するテキストを持つ、最初の要素を取得します。
```python
>>> page.find_by_regex(r'£[\d\.]+')
<data='<p class="price_color">£51.77</p>' parent='<div class="product_price"> <p class="pr...'>
>>> page.find_by_regex(r'£[\d\.]+').text
'£51.77'
```
コンパイル済みの正規表現でも同じです。Scrapling は入力の型を確認して処理します。
```python
>>> import re
>>> regex = re.compile(r'£[\d\.]+')
>>> page.find_by_regex(regex)
<data='<p class="price_color">£51.77</p>' parent='<div class="product_price"> <p class="pr...'>
>>> page.find_by_regex(regex).text
'£51.77'
```
正規表現に一致するすべての要素を取得します。
```python
>>> page.find_by_regex(r'£[\d\.]+', first_match=False)
[<data='<p class="price_color">£51.77</p>' parent='<div class="product_price"> <p class="pr...'>,
 <data='<p class="price_color">£53.74</p>' parent='<div class="product_price"> <p class="pr...'>,
 <data='<p class="price_color">£50.10</p>' parent='<div class="product_price"> <p class="pr...'>,
 <data='<p class="price_color">£47.82</p>' parent='<div class="product_price"> <p class="pr...'>,
 ...]
```
このように使えます。

位置や属性が現在の要素に似ている、すべての要素を探します。ここでは比較時に 'title' 属性を無視します。
```python
>>> element = page.find_by_text('Tipping the Velvet')
>>> element.find_similar(ignore_attributes=['title'])
[<data='<a href="catalogue/a-light-in-the-attic_...' parent='<h3><a href="catalogue/a-light-in-the-at...'>,
 <data='<a href="catalogue/soumission_998/index....' parent='<h3><a href="catalogue/soumission_998/in...'>,
 <data='<a href="catalogue/sharp-objects_997/ind...' parent='<h3><a href="catalogue/sharp-objects_997...'>,
...]
```
要素が 20 個ではなく 19 個なのは、元の要素自体が結果に含まれないためです。
```python
>>> len(element.find_similar(ignore_attributes=['title']))
19
```
似ているすべての要素から `href` を取得します。
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
少し応用し、この要素を出発点にすべての本のデータを取得してみます。
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
### 応用例 {#advanced-examples}
`find_similar` を使う、より実際の作業に近い例です。

オンラインショップの商品を抽出します。
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
表の行を抽出します。
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
フォームの項目を抽出します。
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
サイトのレビューを抽出します。
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
## フィルターで探す {#filters-based-searching}
フィルターによる検索は強力で、初心者にはセレクターを書くより学びやすいため、多くの場合おすすめの方法です。

BeautifulSoup の `find_all` を参考に、`find_all` と `find` を用意しています。どちらも複数のフィルターを受け取り、すべての条件を満たす要素を探します。

引数は次のように扱います。

* 文字列はタグ名です。
* List、Tuple、Set などの反復可能なオブジェクトは、タグ名の集合です。
* 辞書は、HTML 要素の属性名と属性値の組み合わせです。
* 正規表現は、`find_by_regex` と同じように内容で要素を絞ります。
* 関数は、独自の条件で要素を絞ります。
* キーワード引数は、HTML 属性名とその値です。

すべての引数を集め、各フィルターの結果を次のフィルターへ渡しながら、順番に絞り込みます。

現在のページや要素の中を、次の順で調べます。

1. 指定したタグ名の要素を集めます。
2. 指定したすべての属性に一致する要素を集めます。先の処理があれば、その結果だけを調べます。
3. 指定したすべての正規表現に一致する要素を集めます。先の処理があれば、その結果だけを調べます。
4. 指定したすべての関数の条件を満たす要素を集めます。先の処理があれば、その結果だけを調べます。

!!! note "注意点："

    1. この順番のうち、実際に指定された最初のフィルターから処理を始めます。タグ名がなく属性だけがあれば、手順 2 から始めます。
    2. 引数を渡す順序は関係ありません。上で示した順序だけを使います。

例を見ると分かりやすくなります :)

### 例 {#examples_1}
```python
from scrapling.fetchers import Fetcher
page = Fetcher.get('https://quotes.toscrape.com/')
```
すべての `div` 要素を探します。
```python
>>> page.find_all('div')
[<data='<div class="container"> <div class="row...' parent='<body> <div class="container"> <div clas...'>,
 <data='<div class="row header-box"> <div class=...' parent='<div class="container"> <div class="row...'>,
...]
```
クラスが `quote` と等しいすべての div 要素を探します。
```python
>>> page.find_all('div', class_='quote')
[<data='<div class="quote" itemscope itemtype="h...' parent='<div class="col-md-8"> <div class="quote...'>,
 <data='<div class="quote" itemscope itemtype="h...' parent='<div class="col-md-8"> <div class="quote...'>,
...]
```
同じ結果になる別の書き方です。
```python
>>> page.find_all('div', {'class': 'quote'})
[<data='<div class="quote" itemscope itemtype="h...' parent='<div class="col-md-8"> <div class="quote...'>,
 <data='<div class="quote" itemscope itemtype="h...' parent='<div class="col-md-8"> <div class="quote...'>,
...]
```
クラスが `quote` と等しいすべての要素を探します。
```python
>>> page.find_all({'class': 'quote'})
[<data='<div class="quote" itemscope itemtype="h...' parent='<div class="col-md-8"> <div class="quote...'>,
 <data='<div class="quote" itemscope itemtype="h...' parent='<div class="col-md-8"> <div class="quote...'>,
...]
```
クラスが `quote` で、その中に 'world' を含む `.text` 要素がある div を探します。
```python
>>> page.find_all('div', {'class': 'quote'}, lambda e: "world" in e.css('.text::text').get())
[<data='<div class="quote" itemscope itemtype="h...' parent='<div class="col-md-8"> <div class="quote...'>]
```
子を持つすべての要素を探します。
```python
>>> page.find_all(lambda element: len(element.children) > 0)
[<data='<html lang="en"><head><meta charset="UTF...'>,
 <data='<head><meta charset="UTF-8"><title>Quote...' parent='<html lang="en"><head><meta charset="UTF...'>,
 <data='<body> <div class="container"> <div clas...' parent='<html lang="en"><head><meta charset="UTF...'>,
...]
```
内容に 'world' を含むすべての要素を探します。
```python
>>> page.find_all(lambda element: "world" in element.text)
[<data='<span class="text" itemprop="text">“The...' parent='<div class="quote" itemscope itemtype="h...'>,
 <data='<a class="tag" href="/tag/world/page/1/"...' parent='<div class="tags"> Tags: <meta class="ke...'>]
```
指定した正規表現に一致するすべての span 要素を探します。
```python
>>> page.find_all('span', re.compile(r'world'))
[<data='<span class="text" itemprop="text">“The...' parent='<div class="quote" itemscope itemtype="h...'>]
```
クラスが 'quote' の div と span を探します。ここでは該当する span がないため、div だけが返ります。
```python
>>> page.find_all(['div', 'span'], {'class': 'quote'})
[<data='<div class="quote" itemscope itemtype="h...' parent='<div class="col-md-8"> <div class="quote...'>,
 <data='<div class="quote" itemscope itemtype="h...' parent='<div class="col-md-8"> <div class="quote...'>,
...]
```
複数の条件を組み合わせます。
```python
>>> page.find_all({'itemtype':"http://schema.org/CreativeWork"}, 'div').css('.author::text').getall()
['Albert Einstein',
 'J.K. Rowling',
...]
```
便利な使い方として、`href` の値が 'Einstein' で終わる要素も探せます。
```python
>>> page.find_all({'href$': 'Einstein'})
[<data='<a href="/author/Albert-Einstein">(about...' parent='<span>by <small class="author" itemprop=...'>,
 <data='<a href="/author/Albert-Einstein">(about...' parent='<span>by <small class="author" itemprop=...'>,
 <data='<a href="/author/Albert-Einstein">(about...' parent='<span>by <small class="author" itemprop=...'>]
```
`href` の値に '/author/' を含む要素を探すこともできます。
```python
>>> page.find_all({'href*': '/author/'})
[<data='<a href="/author/Albert-Einstein">(about...' parent='<span>by <small class="author" itemprop=...'>,
 <data='<a href="/author/J-K-Rowling">(about)</a...' parent='<span>by <small class="author" itemprop=...'>,
 <data='<a href="/author/Albert-Einstein">(about...' parent='<span>by <small class="author" itemprop=...'>,
...]
```
このように条件を組み合わせられます。

## セレクターを生成する {#generating-selectors}
任意の要素から CSS/XPath セレクターを生成し、ここでも別の場所でも再利用できます。元の要素をどの方法で見つけたかは関係ありません。

`url_element` に対して、可能なら短い CSS セレクターを生成します。短くできなければ完全なセレクターを返します。
```python
>>> url_element = page.find({'href*': '/author/'})
>>> url_element.generate_css_selector
'body > div > div:nth-of-type(2) > div > div > span:nth-of-type(2) > a'
```
`url_element` に対して、ページの先頭からの完全な CSS セレクターを生成します。
```python
>>> url_element.generate_full_css_selector
'body > div > div:nth-of-type(2) > div > div > span:nth-of-type(2) > a'
```
`url_element` に対して、可能なら短い XPath セレクターを生成します。短くできなければ完全なセレクターを返します。
```python
>>> url_element.generate_xpath_selector
'//body/div/div[2]/div/div/span[2]/a'
```
`url_element` に対して、ページの先頭からの完全な XPath セレクターを生成します。
```python
>>> url_element.generate_full_xpath_selector
'//body/div/div[2]/div/div/span[2]/a'
```
!!! abstract "注意："

    短いセレクターを生成するときは、`id` 属性を持つ要素など、一意に分かる要素を出発点として探します。今回の例にはないため、短いセレクターと完全なセレクターが同じになります。

## セレクターと正規表現を組み合わせる {#using-selectors-with-regular-expressions}
`parsel`/`scrapy` と同じように、`re` と `re_first` で正規表現による抽出ができます。ただし、Scrapling では `Selector`/`Selectors`/`TextHandler` と `TextHandlers` など、ほぼすべてのクラスで使えます。テキストノードを選ばなくても、要素に直接使えます。

[TextHandler](main_classes.md#texthandler) の説明で詳しく扱いますが、基本的には次のように使います。
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
次のページで、[TextHandler](main_classes.md#texthandler) と一緒にさらに詳しく説明します。