---
title: "Scrapling の Selector と Selectors：データとナビゲーション"
description: "Selector と Selectors の HTML、テキスト、属性の扱いを紹介します。値の抽出、URL の解決、親・子・兄弟要素への移動を学べます。"
---

# 解析の主なクラス {#parsing-main-classes}

!!! success "前提条件"

    - [要素の検索](../parsing/selection.md)を読み、[Selector](../parsing/main_classes.md#selector) から要素を探して抽出する方法を理解していること。

さまざまな要素の選び方を見たところで、[Selector](#selector) と関連するオブジェクトを見直し、解析エンジンの仕組みを理解しましょう。

[Selector](#selector) は Scrapling の解析エンジンの中心で、HTML の解析と要素の選択を行います。次のいずれかの方法でインポートできます。
```python
from scrapling import Selector
from scrapling.parser import Selector
```
その後は[概要](../overview.md)で紹介したように直接使います。
```python
page = Selector(
    '<html>...</html>',
    url='https://example.com'
)

# Then select elements as you like
elements = page.css('.product')
```
HTML を渡した後やサイトを取得した後に主に扱うのは、[Selector](#selector) オブジェクトです。選択や移動などの操作結果がページの要素であれば、[Selector](#selector) または [Selectors](#selectors) を返します。テキストなどを返す操作は別です。

つまり、ページ全体も [Selector](#selector) で、その中の要素も [Selector](#selector) です。要素のテキストや属性値などの文字列は [TextHandler](#texthandler) で、属性の集合は [AttributesHandler](#attributeshandler) に保存されます。この 2 つは後で説明し、まずは [Selector](#selector) を見ていきます。

## Selector {#selector}
### 引数の説明 {#arguments-explained}
最も重要なのは `content` です。解析する HTML を `str` または `bytes` で渡します。

`url` は、相対リンクの解決と、保存した適応型データをドメインごとに分けるためのページ URL です。`adaptive`、`storage`、`storage_args` は[適応型機能](adaptive.md)の設定です。この機能を使わない場合は影響しません。

次の引数は、解析方法や解析中の HTML の扱いを調整します。

- **encoding**：HTML の解析に使う文字コードです。標準は `UTF-8` です。
- **keep_comments**：HTML コメントを残すかどうかを指定します。コメントがスクレイピングに影響することがあるため、標準では無効です。

ここでは説明を複雑にしないため、`huge_tree` と `root` を省いています。
通常の利用には不要な高度な機能は、このように省略しています。詳しく知りたい場合は、開発セクションで扱います。

ページや要素の多くのプロパティは、実際に使うまで読み込まれません。テキスト内容なども同じです。この遅延読み込みも Scrapling が速い理由の 1 つです :)

### プロパティ {#properties}
[概要](../overview.md)で紹介したものも多いですが、まだ読んでいなくても大丈夫です。ここではさらに詳しく説明します。移動に使うプロパティは、後の[要素間の移動](#traversal)にまとめています。

説明には、次の HTML ページを使います。
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
先ほどと同じようにページを読み込みます。
```python
from scrapling import Selector
page = Selector(html_doc)
```
入れ子の要素も含め、ページ内のすべてのテキストを取得します。
```python
>>> page.get_all_text()
'Some page\n\n    \n\n      \nProduct 1\nThis is product 1\n$10.99\nIn stock: 5\nProduct 2\nThis is product 2\n$20.99\nIn stock: 3\nProduct 3\nThis is product 3\n$15.99\nOut of stock'
```
最初の記事を取得し、例として使います。
```python
article = page.find('article')
```
同じように、要素内のすべてのテキストを再帰的に取得できます。
```python
>>> article.get_all_text()
'Product 1\nThis is product 1\n$10.99\nIn stock: 5'
```
ただし、この要素には直接のテキストがないため、直接のテキスト内容は空になります。
```python
>>> article.text
''
```
`get_all_text` には次の省略可能な引数があります。

1. **separator**：集めた文字列をつなぐ区切り文字です。標準は '\n' です。
2. **strip**：連結する前に、文字列の前後の空白を取り除きます。標準では無効です。
3. **ignore_tags**：除外するタグ名のタプルです。その中の要素もすべて除外します。標準は `('script', 'style',)` です。
4. **valid_values**：内容のある要素だけを集め、テキストが空または空白だけの要素を除外します。標準では有効です。

返されるテキストは通常の文字列ではなく、[TextHandler](#texthandler) です。詳しくは後で説明しますが、JSON として読めるテキストなら `.json()` を使えます。
```python
>>> script = page.find('script')
>>> script.json()
{'lastUpdated': '2024-09-22T10:30:00Z', 'totalProducts': 3}
```
次に要素のタグ名を取得します。
```python
>>> article.tag
'article'
```
ページ自体で実行すると、ルートの `html` 要素を扱っていることが分かります。
```python
>>> page.tag
'html'
```
これで `page` と `element` の関係は分かったと思うので、以降は繰り返しません。

要素の属性を取得します。
```python
>>> print(article.attrib)
{'class': 'product', 'data-id': '1'}
```
特定の属性には、次のどちらの方法でもアクセスできます。
```python
article.attrib['class']
article.attrib.get('class')
article['class']  # new in v0.3
```
次の方法で、特定の属性があるか確認できます。
```python
'class' in article.attrib
'class' in article  # new in v0.3
```
要素の HTML 内容を取得します。
```python
>>> article.html_content
'<article class="product" data-id="1"><h3>Product 1</h3>\n        <p class="description">This is product 1</p>\n        <span class="price">$10.99</span>\n        <div class="hidden stock">In stock: 5</div>\n      </article>'
```
要素の HTML を読みやすく整形して取得します。
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
`.body` でページの生の内容を取得できます。v0.4 以降、Fetcher が返す `Response` での `.body` は常に `bytes` です。
```python
>>> page.body
'<html>\n  <head>\n    <title>Some page</title>\n  </head>\n  ...'
```
DOM ツリー上のすべての祖先を取得します。
```python
>>> article.path
[<data='<div class="product-list"> <article clas...' parent='<body> <div class="product-list"> <artic...'>,
 <data='<body> <div class="product-list"> <artic...' parent='<html><head><title>Some page</title></he...'>,
 <data='<html><head><title>Some page</title></he...'>]
```
可能なら短い CSS セレクターを生成するか、完全なセレクターを生成します。
```python
>>> article.generate_css_selector
'body > div > article'
>>> article.generate_full_css_selector
'body > div > article'
```
XPath でも同じことができます。
```python
>>> article.generate_xpath_selector
"//body/div/article"
>>> article.generate_full_xpath_selector
"//body/div/article"
```

### 要素間の移動 {#traversal}
先ほど見つけた要素を使い、ページ内の移動に使うプロパティやメソッドを説明します。

DOM ツリーや木構造を知らない場合は、この部分が分かりにくいかもしれません。先にこれらの概念を調べることをおすすめします。

ここにも簡単な説明を載せておきます。<br/>
ページは `html` 要素から始まるので、`html` がページの木構造の根になります。<br/>
その直下に `head` や `body` があります。これらは `html` の「子」で、`html` はその「親」です。`body` と `head` は同じ親を持つので「兄弟」です。

要素の親にアクセスします。
```python
>>> article.parent
<data='<div class="product-list"> <article clas...' parent='<body> <div class="product-list"> <artic...'>
>>> article.parent.tag
'div'
```
必要なだけ連続して呼び出せます。以下の同様のプロパティやメソッドでも同じです。
```python
>>> article.parent.parent.tag
'body'
```
要素の子を取得します。
```python
>>> article.children
[<data='<h3>Product 1</h3>' parent='<article class="product" data-id="1"><h3...'>,
 <data='<p class="description">This is product 1...' parent='<article class="product" data-id="1"><h3...'>,
 <data='<span class="price">$10.99</span>' parent='<article class="product" data-id="1"><h3...'>,
 <data='<div class="hidden stock">In stock: 5</d...' parent='<article class="product" data-id="1"><h3...'>]
```
要素の下にあるすべての要素を取得します。`children` を再帰的に使うような働きです。
```python
>>> article.below_elements
[<data='<h3>Product 1</h3>' parent='<article class="product" data-id="1"><h3...'>,
 <data='<p class="description">This is product 1...' parent='<article class="product" data-id="1"><h3...'>,
 <data='<span class="price">$10.99</span>' parent='<article class="product" data-id="1"><h3...'>,
 <data='<div class="hidden stock">In stock: 5</d...' parent='<article class="product" data-id="1"><h3...'>]
```
この要素では、子にさらに子がないため、`children` と同じ結果になります。

クラスが `product-list` の要素を使うと、`children` と `below_elements` の違いが分かりやすくなります。
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
兄弟要素を取得します。
```python
>>> article.siblings
[<data='<article class="product" data-id="2"><h3...' parent='<div class="product-list"> <article clas...'>,
 <data='<article class="product" data-id="3"><h3...' parent='<div class="product-list"> <article clas...'>]
```
次の兄弟要素を取得します。
```python
>>> article.next
<data='<article class="product" data-id="2"><h3...' parent='<div class="product-list"> <article clas...'>
```
前の要素には `previous` を使います。
```python
>>> article.previous  # It's the first child, so it doesn't have a previous element
>>> second_article = page.css('.product[data-id="2"]')[0]
>>> second_article.previous
<data='<article class="product" data-id="1"><h3...' parent='<div class="product-list"> <article clas...'>
```
特定のクラス名を持つかどうかも、簡単に素早く確認できます。
```python
>>> article.has_class('product')
True
```
直接の親だけでなく、すべての祖先を順番に調べることもできます。
```python
for ancestor in article.iterancestors():
    # do something with it...
```
条件を満たす祖先を探すこともできます。[Selector](#selector) を受け取り、条件を満たすときは `True`、それ以外は `False` を返す関数を渡してください。
```python
>>> article.find_ancestor(lambda ancestor: ancestor.has_class('product-list'))
<data='<div class="product-list"> <article clas...' parent='<body> <div class="product-list"> <artic...'>

>>> article.find_ancestor(lambda ancestor: ancestor.css('.product-list'))  # Same result, different approach
<data='<div class="product-list"> <article clas...' parent='<body> <div class="product-list"> <artic...'>
```
## Selectors {#selectors}
`Selectors` は [Selector](#selector) のリスト版です。Python 標準の `List` を継承し、`List` のプロパティとメソッドをすべて使えます。さらに、中の [Selector](#selector) を扱いやすくするメソッドを追加しています。

[Selector](#selector) で複数の要素を返すメソッドやプロパティは、すべて [Selectors](#selectors) インスタンスを返します。

v0.4 以降、テキストノードや属性値も含め、選択メソッドは一貫して [Selector](#selector)/[Selectors](#selectors) を返します。`::text`、`/text()`、`::attr()`、`/@attr` で選んだテキストノードも [Selector](#selector) に包まれます。これらの `tag` は `"#text"` で、`text` が文字列を返します。テキスト値には直接アクセスでき、ほかのプロパティは空の値や標準値を返します。

```python
page.css('a::text')              # -> Selectors (of text node Selectors)
page.xpath('//a/text()')         # -> Selectors
page.css('a::text').get()        # -> TextHandler (the first text value)
page.css('a::text').getall()     # -> TextHandlers (all text values)
page.css('a::attr(href)')        # -> Selectors
page.xpath('//a/@href')          # -> Selectors
page.css('.price_color')         # -> Selectors
```

### データ抽出メソッド {#data-extraction-methods}
v0.4 以降、[Selector](#selector) と [Selectors](#selectors) は `get()`、`getall()` と、その別名である `extract_first`、`extract` を提供します。Scrapy の方式に合わせています。古い `get_all()` は削除されました。

**[Selector](#selector) オブジェクトの場合：**

- `get()` は `TextHandler` を返します。テキストノードならテキスト値、HTML 要素なら要素自体のタグを含む外側の HTML を文字列として返します。
- `getall()` は、その 1 つの文字列を含む `TextHandlers` リストを返します。
- `extract_first` は `get()` の別名、`extract` は `getall()` の別名です。

```python
>>> page.css('h3')[0].get()        # Outer HTML of the element
'<h3>Product 1</h3>'

>>> page.css('h3::text')[0].get()  # Text value of the text node
'Product 1'
```

**[Selectors](#selectors) オブジェクトの場合：**

- `get(default=None)` は、**最初の**要素を文字列として返します。リストが空なら `default` を返します。
- `getall()` は**すべての**要素を文字列に変換し、`TextHandlers` リストを返します。
- `extract_first` は `get()` の別名、`extract` は `getall()` の別名です。

```python
>>> page.css('.price::text').get()      # First price text
'$10.99'

>>> page.css('.price::text').getall()   # All price texts
['$10.99', '$20.99', '$15.99']

>>> page.css('.price::text').get('')    # With default value
'$10.99'
```

これらは CSS、XPath、`find` など、すべての選択方式で使えます。Scrapy と互換性のある形でテキストや属性値を抽出する、推奨の方法です。

次に、[Selectors](#selectors) が追加する機能を見ていきます。
### プロパティ {#properties_1}
繰り返しやスライスなど、通常の Python リストの操作に加え、次の操作ができます。

中の [Selector](#selector) に対して CSS や XPath を直接実行できます。戻り値の型は [Selector](#selector) の `css`、`xpath` と同じです。引数も似ていますが、ここでは `adaptive` は使えません。複数のメソッドを簡単につなげられます。
```pycon
>>> page.css('.product h3::text').getall()
['Product 1', 'Product 2', 'Product 3']
>>> page.css('.product').css('h3::text').getall()
['Product 1', 'Product 2', 'Product 3']
```
`re` と `re_first` も直接呼び出せます。引数は [Selector](#selector) と同じです。これらの詳しい説明は、後の [TextHandler](#texthandler) にまとめます。

ただし、ここでの `re_first` は各 [Selector](#selector) に `re` を実行し、最初に見つかった結果を返します。`re` は通常どおり [TextHandlers](#texthandlers) を返し、各 [TextHandler](#texthandler) を 1 つの [TextHandlers](#texthandlers) にまとめます。
```pycon
>>> page.css('.price::text').re(r'[\d.]+')
['10.99', '20.99', '15.99']
>>> page.css('.product h3::text').re(r'Product (\d+)')
['1', '2', '3']
```
`search` で、中の [Selector](#selector) を素早く探せます。渡す関数は最初の引数に [Selector](#selector) を受け取り、True または False を返します。条件を満たす最初の [Selector](#selector) を返し、なければ `None` を返します。

```pycon
>>> product = page.css('.product').search(lambda p: p.css('.price::text').get() == '$20.99')
>>> product.css('h3::text').get()
'Product 2'
```
`filter` も `search` と同じ形の関数を受け取りますが、条件を満たすすべての [Selector](#selector) を含む `Selectors` を返します。

```pycon
>>> products = page.css('.product').filter(lambda p: float(p.css('.price::text').re_first(r'[\d.]+')) > 15)
>>> products.css('h3::text').getall()
['Product 2', 'Product 3']
```
インデックスエラーを気にせず、最初や最後の要素に安全にアクセスできます。
```python
>>> page.css('.product').first   # First Selector or None
<data='<article class="product" data-id="1"><h3...'>
>>> page.css('.product').last    # Last Selector or None
<data='<article class="product" data-id="3"><h3...'>
>>> page.css('.nonexistent').first  # Returns None instead of raising IndexError
```

[Selectors](#selectors) 内の [Selector](#selector) の数を短く書いて調べたいなら、次の方法があります。
```python
page.css('.product').length
```
これは次と同じです。
```python
len(page.css('.product'))
```
そう、JavaScript のように書けます :)

## TextHandler {#texthandler}
このクラスは重要です。文字列を返すメソッドやプロパティは `TextHandler` を返し、文字列のリストを返すものは [TextHandlers](#texthandlers) を返します。

TextHandler は Python の標準文字列を継承するので、文字列でできる操作はそのまま使えます。では、なぜ別の名前があるのでしょうか。

TextHandler には、標準文字列にないメソッドやプロパティがあります。ライブラリ全体で文字列の代わりに TextHandler を返すため、機能を組み合わせて短く読みやすいコードを書けます。直接インポートして任意の文字列に使う方法も、[後で](../development/scrapling_custom_types.md)紹介します。
### 使い方 {#usage}
スライスやインデックスアクセス、`split`、`replace`、`strip` などの操作は、再び `TextHandler` を返します。そのため、続けてメソッドを呼び出せます。`TextHandler` ではなく通常の文字列を返すものを見つけた場合は、Issue を開いてください。そこも対応します。

まず `re` と `re_first` です。[Selector](#selector)、[Selectors](#selectors)、[TextHandlers](#texthandlers) にもあるメソッドで、引数は共通です。

- `re` は最初の引数として文字列またはコンパイル済みの正規表現を受け取ります。一致する文字列をすべて探し、[TextHandlers](#texthandlers) として返します。`re_first` は同じ引数を受け取りますが、最初の結果だけを `TextHandler` として返します。
    
    ほかに次の引数があります。
    
    - **replace_entities**：標準では有効です。文字参照を対応する文字に置き換えます。
    - **clean_match**：標準では無効です。照合時に連続した空白も含め、すべての空白文字を無視します。
    - **case_sensitive**：標準では有効です。無効にすると、正規表現のコンパイル時に大文字と小文字を区別しなくなります。
  
    次の例は前にも紹介しました。`re` を使うので、結果は [TextHandlers](#texthandlers) です。
    ```pycon
    >>> page.css('.price::text').re(r'[\d.]+')
    ['10.99', '20.99', '15.99']
    >>> page.css('.product h3::text').re(r'Product (\d+)')
    ['1', '2', '3']
    ```
    ほかの引数を説明するため、以下では例ごとに文字列を用意します。
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
    文字列を `TextHandler` に置き換える利点は、`html_content` のようなプロパティも `TextHandler` を返すことです。HTML 内容に直接正規表現を使えます。
    ```python
    >>> page.html_content.re('div class=".*">(.*)</div')
    ['In stock: 5', 'In stock: 3', 'Out of stock']
    ```

- `.json()` は、内容を JSON オブジェクトに素早く変換します。変換できない場合はエラーになります。
  ```python
  >>> page.css('#page-data::text').get()
    '\n      {\n        "lastUpdated": "2024-09-22T10:30:00Z",\n        "totalProducts": 3\n      }\n    '
  >>> page.css('#page-data::text').get().json()
    {'lastUpdated': '2024-09-22T10:30:00Z', 'totalProducts': 3}
  ```
  要素を選ぶときにテキストノードや属性値を指定しなかった場合は、その要素のテキスト内容を自動で使います。
  ```python
  >>> page.css('#page-data')[0].json()
  {'lastUpdated': '2024-09-22T10:30:00Z', 'totalProducts': 3}
  ```
  [Selector](#selector) では、さらに工夫をしています。次のページを例にします。
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
  [Selector](#selector) の `get_all_text` は、先ほど説明したように `TextHandler` を返します。<br/><br/>
  ここで次を実行すると、
  ```python
  >>> page.css('div::text').get().json()
  ```
  エラーになります。`div` には JSON として読める直接のテキストがなく、そもそも直接のテキスト自体がないからです。<br/><br/>
  この場合は `get_all_text` を使えます。
  ```python
  >>> page.css('div')[0].get_all_text(ignore_tags=[]).json()
    {'lastUpdated': '2024-09-22T10:30:00Z', 'totalProducts': 3}
  ```
  `ignore_tags` の標準値が `('script', 'style',)` なので、ここでは指定し直しています。<br/><br/>
  Fetcher を使う場合にも、関連する動作があります。次の JSON レスポンスを受け取ったとします。
  ```python
  >>> page = Selector("""{"some_key": "some_value"}""")
  ```
  [Selector](#selector) は HTML ページ向けなので、これを不完全な HTML として修正します。`html_content` では次の結果になります。
  ```python
  >>> page.html_content
  '<html><body><p>{"some_key": "some_value"}</p></body></html>'
  ```
  それでも `json` は直接使えます。
  ```python
  >>> page.json()
  {'some_key': 'some_value'}
  ```
  `html` タグに直接のテキストがないのに、なぜ動くのでしょうか。<br/>
  JSON レスポンスなどを扱うため、[Selector](#selector) は受け取った内容の生のコピーを保存します。`.json()` はまずそのコピーを JSON として読みます。個々の要素のようにコピーがなければ直接のテキストを確認し、それでもなければ `get_all_text` を使います。<br/>

- `.clean()` は空白文字や連続した空白を取り除き、新しい `TextHandler` を返します。
```python
>>> TextHandler('\n wonderful  idea, \reh?').clean()
'wonderful idea, eh?'
```
`remove_entities` を渡すと、`clean` で HTML エンティティを対応する文字に置き換えることもできます。

- `.sort()` では、リストのように文字列を並べ替えられます。
```python
>>> TextHandler('acb').sort()
'abc'
```
逆順にもできます。
```python
>>> TextHandler('acb').sort(reverse=True)
'cba'
```

今後もメソッドやプロパティを追加していきます。ライブラリのほぼ全体で、通常の文字列の代わりにこのクラスを返すことを覚えておいてください。

## TextHandlers {#texthandlers}
このクラスも [Selectors](#selectors) と [Selector](#selector) の関係に似ています。通常のリストの動作を引き継ぎ、`re` と `re_first` を追加しています。

違いは、ここでの `re_first` が各 [TextHandler](#texthandler) に `re` を実行し、最初の結果か `None` を返すことです。現時点ではほかに新しい説明はありませんが、今後メソッドを追加する予定です。

## AttributesHandler {#attributeshandler}
Python の標準辞書 `dict` の読み取り専用版で、要素や [Selector](#selector) の属性を保存するために使います。
```python
>>> print(page.find('script').attrib)
{'id': 'page-data', 'type': 'application/json'}
>>> type(page.find('script').attrib).__name__
'AttributesHandler'
```
読み取り専用なので、通常の辞書より少ないリソースで動きます。データの変更や上書きを行うものを除き、辞書と同じメソッドやプロパティを使えます。

現在は、次の 2 つの機能を追加しています。

- `search_values` メソッド

    通常の辞書では、`dict.get("key_name")` でキーの存在を調べられます。値で探す場合は追加のコードが必要ですが、このメソッドなら属性値を検索し、一致する項目ごとに辞書を返します。
    
    簡単な例です。
    ```python
    >>> for i in page.find('script').attrib.search_values('page-data'):
            print(i)
    {'id': 'page-data'}
    ```
    `partial` を使うと、値の一部でも検索できます。
    ```python
    >>> for i in page.find('script').attrib.search_values('page', partial=True):
            print(i)
    {'id': 'page-data'}
    ```
    上の例は単純ですが、実際には `find_all` と組み合わせ、特定の属性値を持つ要素を探すといった使い方ができます。
    ```python
    >>> page.find_all(lambda element: list(element.attrib.search_values('product')))
    [<data='<article class="product" data-id="1"><h3...' parent='<div class="product-list"> <article clas...'>,
     <data='<article class="product" data-id="2"><h3...' parent='<div class="product-list"> <article clas...'>,
     <data='<article class="product" data-id="3"><h3...' parent='<div class="product-list"> <article clas...'>]
    ```
    これらの要素は、すべて `class` の値に 'product' を持っています。
    
    `search_values` はジェネレーターを返すので、ここでは `list` を使っています。そのままだと、どの要素でも `True` と判定されてしまいます。

- `json_string` プロパティ

    属性を JSON 文字列に変換します。JSON に変換できない場合はエラーになります。
  
    ```python
    >>>page.find('script').attrib.json_string
    b'{"id":"page-data","type":"application/json"}'
    ```