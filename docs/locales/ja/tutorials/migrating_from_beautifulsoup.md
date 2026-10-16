---
title: "BeautifulSoup から Scrapling に移行する"
description: "BeautifulSoup の要素選択、テキスト、属性、ナビゲーションを Scrapling に置き換えます。実用的な例で API の違いを確認します。"
---

# BeautifulSoup から Scrapling に移行する {#migrating-from-beautifulsoup-to-scrapling}

BeautifulSoup に慣れていれば、Scrapling も使いやすいはずです。Scrapling は高速で、BeautifulSoup と同じ解析機能に加え、BeautifulSoup にはない解析機能も備えています。現代の Web ページを取得して処理するための機能もあります。このガイドでは、既存の BeautifulSoup コードを Scrapling に置き換える方法を説明します。

次の表では、Web スクレイピングでよく使う操作を比較します。各行に、BeautifulSoup と Scrapling で同じ作業を行う方法を示しています。

BeautifulSoup の一部の省略記法は、Scrapling にはありません。これは、BeautifulSoup より Scrapling が速い理由の 1 つです。同じ機能を短い 1 行で書けるなら、さらに短くするために性能を落とす必要はないと考えています :)


| 作業 | BeautifulSoup のコード | Scrapling のコード |
|-----------------------------------------------------------------|---------------------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------|
| パーサーのインポート | `from bs4 import BeautifulSoup`                                                                               | `from scrapling.parser import Selector`                                           |
| 文字列の HTML を解析 | `soup = BeautifulSoup(html, 'html.parser')`                                                                   | `page = Selector(html)`                                                           |
| 1 つの要素を検索 | `element = soup.find('div', class_='example')`                                                                | `element = page.find('div', class_='example')`                                    |
| 複数の要素を検索 | `elements = soup.find_all('div', class_='example')`                                                           | `elements = page.find_all('div', class_='example')`                               |
| 1 つの要素を検索（例 2） | `element = soup.find('div', attrs={"class": "example"})`                                                      | `element = page.find('div', {"class": "example"})`                                |
| 1 つの要素を検索（例 3） | `element = soup.find(re.compile("^b"))`                                                                       | `element = page.find(lambda e: re.search(r"^b", e.tag) is not None)` |
| 1 つの要素を検索（例 4） | `element = soup.find(lambda e: len(list(e.children)) > 0)`                                                    | `element = page.find(lambda e: len(e.children) > 0)`                              |
| 1 つの要素を検索（例 5） | `element = soup.find(["a", "b"])`                                                                             | `element = page.find(["a", "b"])`                                                 |
| テキストの内容で要素を検索 | `element = soup.find(text="some text")`                                                                       | `element = page.find_by_text("some text", partial=False)`                         |
| CSS セレクターで最初の一致を検索 | `elements = soup.select_one('div.example')`                                                                   | `elements = page.css('div.example').first`                                        |
| CSS セレクターですべての一致を検索 | `elements = soup.select('div.example')`                                                                       | `elements = page.css('div.example')`                                              |
| ページや要素の整形済みソースを取得 | `prettified = soup.prettify()`                                                                                | `prettified = page.prettify()`                                                    |
| ページや要素の未整形のソースを取得 | `source = str(soup)`                                                                                          | `source = page.html_content`                                                      |
| 要素のタグ名を取得 | `name = element.name`                                                                                         | `name = element.tag`                                                              |
| 要素のテキストを抽出 | `string = element.string`                                                                                     | `string = element.text`                                                           |
| 文書全体またはタグ内のすべてのテキストを抽出 | `text = soup.get_text(strip=True)`                                                                            | `text = page.get_all_text(strip=True)`                                            |
| 属性の辞書にアクセス | `attrs = element.attrs`                                                                                       | `attrs = element.attrib`                                                          |
| 属性を抽出 | `attr = element['href']`                                                                                      | `attr = element['href']`                                                          |
| 親要素に移動 | `parent = element.parent`                                                                                     | `parent = element.parent`                                                         |
| 要素のすべての祖先を取得 | `parents = list(element.parents)`                                                                             | `parents = list(element.iterancestors())`                                         |
| 祖先要素の中から要素を検索 | `target_parent = element.find_parent("a")`                                                                    | `target_parent = element.find_ancestor(lambda p: p.tag == 'a')`                   |
| すべての兄弟要素を取得 | 非対応                                                                                                           | `siblings = element.siblings`                                                     |
| 次の兄弟要素を取得 | `next_element = element.next_sibling`                                                                         | `next_element = element.next`                                                     |
| 兄弟要素の中から 1 つの要素を検索 | `target_sibling = element.find_next_sibling("a")`<br/>`target_sibling = element.find_previous_sibling("a")`   | `target_sibling = element.siblings.search(lambda s: s.tag == 'a')`                |
| 兄弟要素の中から複数の要素を検索 | `target_sibling = element.find_next_siblings("a")`<br/>`target_sibling = element.find_previous_siblings("a")` | `target_sibling = element.siblings.filter(lambda s: s.tag == 'a')`                |
| 後続の要素から 1 つの要素を検索 | `target_parent = element.find_next("a")`                                                                      | `target_parent = element.below_elements.search(lambda p: p.tag == 'a')`           |
| 後続の要素から複数の要素を検索 | `target_parent = element.find_all_next("a")`                                                                  | `target_parent = element.below_elements.filter(lambda p: p.tag == 'a')`           |
| 祖先の中から 1 つの要素を検索 | `target_parent = element.find_previous("a")` ¹                                                                | `target_parent = element.path.search(lambda p: p.tag == 'a')`                     |
| 祖先の中から複数の要素を検索 | `target_parent = element.find_all_previous("a")` ¹                                                            | `target_parent = element.path.filter(lambda p: p.tag == 'a')`                     |
| 前の兄弟要素を取得 | `prev_element = element.previous_sibling`                                                                     | `prev_element = element.previous`                                                 |
| 子要素に移動 | `children = list(element.children)`                                                                           | `children = element.children`                                                     |
| すべての子孫要素を取得 | `children = list(element.descendants)`                                                                        | `children = element.below_elements`                                               |
| story クラスの段落内のリンクを選択 | `group = soup.select('p.story a')`                                                             | `group = page.css('p.story a')`              |

コンパイル済みの正規表現を Scrapling の `find()` や `find_all()` に直接渡すと、タグ名ではなく要素のテキストに一致させます。タグ名を検索するには上の lambda を使い、テキストを直接検索するには `page.find_by_regex(r"^b")` を使います。

¹ **注意：** BS4 の `find_previous`/`find_all_previous` は文書順で前にあるすべての要素を検索します。一方、Scrapling の `path` が返すのは祖先、つまり親をたどった要素だけです。完全に同じ動作ではありませんが、よくある用途の多くは祖先検索で対応できます。

**覚えておきたい点**：BeautifulSoup には、解析後にページを変更、操作する機能があります。Scrapling は、まずページを速くスクレイピングすることに重点を置いています。抽出した情報は、その後で自由に処理できます。どちらも Web スクレイピングに使えますが、Scrapling はその用途に特化しています :)

### 全体を組み合わせた例 {#putting-it-all-together}

BeautifulSoup と Scrapling で Web ページからすべてのリンクを抽出する、簡単な例を示します。

**BeautifulSoup の場合：**

```python
import requests
from bs4 import BeautifulSoup

url = 'https://example.com'
response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')

links = soup.find_all('a')
for link in links:
    print(link['href'])
```

**Scrapling の場合：**

```python
from scrapling import Fetcher

url = 'https://example.com'
page = Fetcher.get(url)

links = page.css('a::attr(href)').getall()
for link in links:
    print(link)
```

Scrapling は取得と解析を 1 つの手順にまとめるため、コードをすっきり、効率よく書けます。

!!! abstract "**補足：**"

    - **パーサーの違い**：BeautifulSoup では解析エンジンを選べ、その 1 つが `lxml` です。Scrapling はエンジンを切り替えず、性能のために `lxml` を標準で使います。
    - **要素の型**：BeautifulSoup の要素は `Tag`、Scrapling の要素は `Selector` オブジェクトです。移動やデータ抽出には、よく似たメソッドとプロパティを使えます。
    - **エラーへの対応**：要素が見つからない場合、両方のライブラリは `None` を返します。例えば `soup.find()` や `page.find()` です。Scrapling の `page.css()` は、一致がない場合に空の `Selectors` リストを返します。`page.css('.foo').first` を使えば、最初の一致、または `None` を安全に取得できます。エラーを避けるため、プロパティにアクセスする前に `None` や空の結果を確認してください。
    - **テキストの抽出**：Scrapling の `TextHandler` には、余分な空白、連続するスペース、不要な文字を取り除くのに役立つ `clean()` などの追加メソッドがあります。全体の一覧はドキュメントをご覧ください。

ドキュメントでは、Scrapling の機能や、各メソッドに渡せる引数をさらに詳しく説明しています。

このガイドが、BeautifulSoup から Scrapling への移行に役立てば幸いです。スクレイピングを楽しんでください。
