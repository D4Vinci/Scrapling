---
title: "適応型解析で HTML 要素を追跡し、再び見つける"
description: "要素の特徴を保存し、HTML が変わった後も一致する要素を探します。適応型解析の有効化と save、retrieve、relocate の使い方を紹介します。"
---

# 適応型スクレイピング {#adaptive-scraping}

!!! success "前提条件"

    1. [要素の検索](../parsing/selection.md)を読み、[Selector](../parsing/main_classes.md#selector) オブジェクトから要素を探して抽出する方法を理解していること。
    2. [主なクラス](../parsing/main_classes.md)を読み、[Selector](../parsing/main_classes.md#selector) クラスを理解していること。

適応型スクレイピングは、以前は automatch と呼ばれていた、Scrapling の特に強力な機能です。要素を追跡して再び見つけることで、サイトが変わってもスクレイパーを動かし続けられます。

次のような構造のページをスクレイピングするとします。
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
ID が `p1` の最初の商品を取得するなら、次のようなセレクターを書くでしょう。
```python
page.css('#p1')
```
サイトの運営者が構造を次のように変えると、
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
そのセレクターは機能しなくなり、コードの修正が必要になります。ここで Scrapling の `adaptive` 機能が役立ちます。

最初に要素を選ぶときに `adaptive` を有効にできます。次に同じ要素を選ぼうとして見つからなければ、Scrapling は保存した特徴を使い、サイト内で最も似ている要素を探します。AI は使いません :)

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
まず例で使い方を示し、その後で仕組みと詳しい使い方を説明します。この機能は CSS/XPath だけでなく、すべての選択方法で使えます。

## 実際のサイトを使う例 {#real-world-scenario}
実際のサイトを例に、Fetcher でソースを取得してみます。本来なら、デザインや構造が変わる直前のサイトを見つけ、ソースを保存して変更を待つ必要があります。ただ、運営者を知らない限り、変更の予定を知るのはほぼ無理です。知っていれば、今度は仕込んだテストになってしまいますね。

そこで [The Web Archive](https://archive.org/) の [Wayback Machine](https://web.archive.org/) を使います。これは [2010 年の StackOverFlow](https://web.archive.org/web/20100102003420/http://stackoverflow.com/) のコピーです。かなり古いですね。</br>同じセレクターで、2010 年のデザインと現在のデザインから同じボタンを見つけられるか試します :)

古いデザインの Questions ボタンは、`#hmenus > div:nth-child(1) > ul > li:nth-child(1) > a` で選べます。Google Chrome が生成したため、構造を細かく指定したセレクターです。


両方のページで同じセレクターを試します。
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
ここでは `adaptive_domain` という引数を追加しました。Scrapling にとって `archive.org` と `stackoverflow.com` は別のドメインなので、`adaptive` のデータも別々に保存されます。同じサイトとして扱うため、両方の `adaptive` データを保存するときに共通のドメインを指定します。

実際のサイトでは、両方のリクエストに同じ URL を使うので、`adaptive_domain` は不要です。それ以外のコードは同じです。できるだけ実際の状況に近い例にしたので、参考になればうれしいです :)

上の 2 つの例では `Selector` と `Fetcher` を使い、適応型機能の仕組みが同じであることを示しました。

!!! info

    `adaptive_domain` は主に、サイトがデザインや構造と一緒に URL も変える場合に使います。新しい URL でも、保存済みの適応型データを引き続き利用できます。指定しないと、Scrapling は新しいサイトと判断し、古いデータを使いません。

## 適応型スクレイピングの仕組み {#how-the-adaptive-scraping-feature-works}
処理は 2 つの段階に分かれます。

1. **保存**：要素の特徴を保存します。
2. **照合**：後で似た特徴の要素を探します。

任意の方法で要素を選び、サイトの構造やデザインが変わっても、次回の取得時に同じ要素を見つけたいとします。

細かな技術の話を省くと、次の流れになります。

  1. 後で説明する方法のいずれかで、要素の特徴を保存するよう Scrapling に指示します。
  2. Scrapling は設定されたデータベースに、各要素の特徴を保存します。標準では SQLite を使います。
  3. 運営者は要素のどの情報も変更や削除ができるため、要素自体の属性をデータベースの固定識別子にはできません。そこで、保存システムは次の 2 つを使います。
     1. 現在のサイトのドメイン。`Selector` を使う場合は初期化時に渡します。Fetcher では URL から自動で取得します。
     2. データベースから要素の特徴を読み出すための `identifier`。必ずしも手動で設定する必要はありません。詳しくは後で説明します。

     この 2 つを組み合わせて、保存した要素の特徴を読み出します。

  4. サイトの構造が変わったら、`adaptive` を有効にして要素を探します。Scrapling は保存した特徴を読み出し、ページ上のすべての要素と比較します。目的の要素との類似度に応じてスコアを計算します。この比較では、後で説明するすべての特徴を考慮します。
  5. 目的の要素と最も似ている要素を返します。

### 保存する特徴 {#the-unique-properties}
要素の情報がすべて変更や削除の対象になるなら、どの特徴を使うのでしょうか。

Scrapling は次の情報を使います。

- 要素のタグ名、テキスト、属性の名前と値、兄弟要素のタグ名、パス上のタグ名。
- 親要素のタグ名、属性の名前と値、テキスト。

比較では完全一致ではなく、どの程度似ているかを調べます。値の並び順も対象です。たとえば、要素のクラス名が変更前後でどの順番に並んでいるかも比較します。

## 適応型機能の使い方 {#how-to-use-adaptive-feature}
適応型機能は、見つかったどの要素にも適用できます。先ほどのように CSS/XPath の選択メソッドから引数で使うこともできます。詳しくは後で説明します。

まず `adaptive` を有効にします。[Selector](main_classes.md#selector) の作成時に `adaptive=True` を渡すか、使用する Fetcher で有効にしてください。

例：
```python
from scrapling import Selector, Fetcher
page = Selector(html_doc, adaptive=True)
# OR
Fetcher.adaptive = True
page = Fetcher.get('https://example.com')
```
[Selector](main_classes.md#selector) を使う場合は、`url` に対象サイトの URL を渡してください。これにより、Scrapling は保存する要素の特徴をドメインごとに分けられます。

URL を渡さない場合、保存時の URL 欄には `default` が使われます。別のサイトで同じ識別子を使い、再び URL を指定しなければ、前のデータを上書きしてしまいます。`adaptive` が使うのは、最後に保存された特徴だけです。

ほかに `storage` と `storage_args` があります。データベース接続のための引数で、標準ではライブラリ付属の SQLite クラスを使います。独自の保存システムを作る場合以外は、気にする必要はありません。詳しくは[開発セクションの別ページ](../development/adaptive_storage_system.md)で説明します。

`adaptive` を全体で有効にしたら、主に 2 通りの方法で使えます。

### CSS/XPath で使う {#the-cssxpath-selection-way}
まず、ページに存在する要素を選ぶときに `auto_save` を指定します。
```python
element = page.css('#p1', auto_save=True)
```
後で要素が見つからなくなったら、同じセレクターに `adaptive` を指定すると、ライブラリが探し直します。
```python
element = page.css('#p1', adaptive=True)
```
簡単ですね。

ただし、内部ではいくつかの処理をしています。要素の特徴を読み出す識別子を覚えていますか。`css`/`xpath` では、使いやすいように、渡したセレクターを自動で識別子にします :)

これらのメソッドでは、`identifier` を渡して識別子を自分で設定することもできます。必要に応じて使ってください。`auto_save` と組み合わせて、その識別子で特徴を保存することもできます。

### 手動で使う {#the-manual-way}
要素を手動で保存し、特徴を読み出してから再び見つけることもできます。これも `adaptive` の機能です。どの方法で選んだ要素にも使えます。

たとえば、テキストから次のように要素を見つけたとします。
```python
element = page.find_by_text('Tipping the Velvet', first_match=True)
```
`save` で特徴を保存できますが、識別子は自分で設定します。ここでは `my_special_element` にしました。実際のコードでは、変数名と同じように、意味の分かる名前を使ってください :)
```python
page.save(element, 'my_special_element')
```
後で特徴を読み出し、`adaptive` でページ内の要素を探し直すには、次のようにします。
```python
>>> element_dict = page.retrieve('my_special_element')
>>> page.relocate(element_dict, selector_type=True)
[<data='<a href="catalogue/tipping-the-velvet_99...' parent='<h3><a href="catalogue/tipping-the-velve...'>]
>>> page.relocate(element_dict, selector_type=True).css('::text').getall()
['Tipping the Velvet']
```
ここでは `retrieve` と `relocate` を使っています。

`lxml.etree` オブジェクトのまま受け取りたい場合は、`selector_type` を指定しません。
```python
>>> page.relocate(element_dict)
[<Element a at 0x105a2a7b0>]
```

## 問題の対処 {#troubleshooting}

### 要素が見つからない {#no-matches-found}
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

### 別の要素に一致する {#wrong-elements-matched}
```python
# Use more specific selectors
products = page.css('.product-list .product', auto_save=True)

# Or save with more context
product = page.find_by_text('Product Name').parent
page.save(product, 'specific_product')
```

## 既知の問題 {#known-issues}
`adaptive` の保存処理では、選択結果の最初の要素の特徴だけを保存します。セレクターがページ内の異なる場所から複数の要素を選んだ場合、後で `adaptive` が見つけ直すのは最初の要素だけです。ただし、カンマでつないだ複数の CSS セレクターは対象外です。それぞれを分けて実行するためです。

## 最後に {#final-thoughts}
この機能を詳しく、かつ分かりやすく説明するのは簡単ではありませんでした。不明点があれば[ディスカッション](https://github.com/D4Vinci/Scrapling/discussions)で質問してください。できるだけ早く返答します。Discord サーバーや個別の連絡でも大丈夫です :)