---
title: "AI の代わりに無料で使える、変化に強い Web スクレイピング"
description: "Scrapling はページの変化、不安定なセレクター、ボット対策、ページ送りに対応します。ページごとに LLM を呼び出す必要はありません。"
---

# Scrapling：AI の代わりに無料で使える、変化に強い Web スクレイピング {#scrapling-a-free-alternative-to-ai-for-robust-web-scraping}

Web スクレイピングは、データ抽出、インデックス作成、データセットの準備などに長く使われてきました。しかし、経験のあるユーザーでも、作業を妨げる同じ問題に何度も出会います。最近は、こうした課題を解決するために、AI を使った Web スクレイピングへ移る動きが目立っています。

この記事では、よくある問題、企業が AI を選ぶ理由、その方法の課題、そして Scrapling が AI の費用をかけずにどう対応するかを説明します。

## よくある問題と難しい目標 {#common-issues-and-challenging-goals}

長く Web スクレイピングをしていると、次のような問題を何度も経験するはずです。

1. **頻繁に変わるサイト構造**：サイトの DOM 構造が更新され、固定の XPath/CSS セレクターが使えなくなります。
2. **不安定なセレクター**：クラス名や ID が変わったり、ランダムな値になったりして、スクレイパーが動かなくなる、または作りにくくなります。
3. **複雑になるボット対策**：CAPTCHA、ブラウザのフィンガープリント検出、行動分析によって、従来のスクレイピングが難しくなります。

ほかにも問題はあります。

これは、既知のサイトを対象に、サイトごとに専用のコードを書ける場合の話です。

さらに広い範囲を対象とする汎用的な Web スクレイピングを考えると、上の問題はより深刻になります。次のような新しい問題も加わります。

1. **サイトごとの大きな違い**：HTML 構造、CSS の使い方、JavaScript フレームワーク、バックエンド技術の数多くの組み合わせに対応する必要があります。
2. **必要なデータの特定**：初めて見るページで、どのデータが重要かをスクレイパーはどう判断するのでしょうか。
3. **ページ送りの違い**：無限スクロール、通常のページ番号、「もっと見る」ボタンでは、それぞれ対応方法が異なります。

ほかにも多くの違いがあります。

共通の技術を使っていないさまざまなサイトを、汎用的にスクレイピングするには、これらをどう手作業で解決すればよいのでしょうか。

## AI は役立ちますが、費用がかかります {#ai-to-the-rescue-but-at-a-high-cost}

AI はページのソースを理解し、必要な項目を見つけたり、そのセレクターを作ったりできるため、これらの問題の多くを簡単に解決できます。もちろん、ボット対策は別のツールですでに解決していることが前提です :)

この方法は魅力的です。私も AI、特に生成 AI に強い関心があります。プロンプトの設計や調整にかなり時間を使うかもしれません。それが問題なくても、やがて本当の課題に直面します。

多くのサイトでは、1 ページに大量の内容があります。AI が処理できるように、それを何らかの形で渡す必要があります。するとトークンを大量に消費し、費用がすぐに膨らみます。

費用を気にしなくてよい場合を除けば、もっと安い方法を探すことになるでしょう。そこで Scrapling の出番です :smile:

## Scrapling にお任せください {#scrapling-got-you-covered}

Scrapling は Web スクレイピングで出会う問題のほとんどに対応できます。残る問題も、今後の更新で少しずつ対応していきます。

### T1 への対応：頻繁に変わるサイト構造 {#solving-issue-t1-rapidly-changing-website-structures}
このために作ったのが[適応型解析](../parsing/adaptive.md)です。ここで登場すると思っていた方もいるでしょう :)

スクレイピング中に `adaptive` を有効にすると、要素の特徴を保存し、サイト構造が変わった後でも再び見つけられます。難しいのは、要素のどの部分も変更される可能性があり、固定の情報に頼れないことです。

適応型解析は、要素を特徴付ける情報を保存します。サイト構造が変わると、以前の要素との類似度が最も高い要素を返します。

詳しい仕組みと多くの例は、[こちら](../parsing/adaptive.md#how-the-adaptive-scraping-feature-works)で説明しています。

### T2 への対応：不安定なセレクター {#solving-issue-t2-unstable-selectors}
長く Web スクレイピングをしていれば、一度は経験があるはずです。ID やクラスがない HTML、ランダムなクラス名など、手掛かりが少なく、扱いにくいサイトです。

こうした場合、通常の CSS/XPath セレクターが最適とは限りません。そのため、Scrapling には次の 3 つの選択方法もあります。

1. [要素の内容で選ぶ](../parsing/selection.md#text-content-selection)：テキストで検索する `find_by_text` と、テキストに正規表現を適用する `find_by_regex` を使います。
2. [別の要素に似た要素を選ぶ](../parsing/selection.md#finding-similar-elements)：1 つの要素を見つければ、似た要素は Scrapling が探します。
3. [条件で要素を選ぶ](../parsing/selection.md#filters-based-searching)：要素が満たすべき条件を指定すると、Scrapling が探します。

各リンクに使い方があるので、ここでは説明を繰り返しません。

### T3 への対応：複雑になるボット対策 {#solving-issue-t3-increasingly-complex-anti-bot-measures}
保護されたサイトでは、プロキシや人間らしい操作だけでは十分でない場合があります。[StealthyFetcher](../fetching/stealthy.md) は、ブラウザの自動操作に、フィンガープリントの修正とボット対策への対応オプションを組み合わせています。Cloudflare Turnstile や Interstitial のチャレンジには `solve_cloudflare=True` を有効にします。

### B1 と B2 への対応：サイトごとの違いと必要なデータの特定 {#solving-issues-b1-b2-extreme-website-diversity-identifying-relevant-data}

難しい課題ですが、Scrapling の柔軟さを使えば対応できます。

以前、さまざまなサイトから AI で価格を抽出している方と話しました。必要なのは価格とタイトルだけで、その価格を AI に探してもらっていました。

私は、この用途なら AI は不要だと伝え、次のコードを例として示しました。
```python
price_element = page.find_by_regex(r'£[\d\.,]+', first_match=True)  # Get the first element that contains a text that matches price regex eg. £10.50
# If you want the container/element that contains the price element
price_element_container = price_element.parent or price_element.find_ancestor(lambda ancestor: ancestor.has_class('product'))  # or other methods...
target_element_selector = price_element_container.generate_css_selector or price_element_container.generate_full_css_selector # or xpath
```
すると、次のような場合はどうするのかと聞かれました。
```html
<span class='currency'> $ </span> <span class='a-price'> 45,000 </span>
```
そこで、コードを次のように変更しました。
```python
price_element_container = page.find_by_regex(r'[\d,]+', first_match=True).parent # Adjusted the regex for this example
full_price_data = price_element_container.get_all_text(separator="", strip=True)  # Returns '$45,000' in this case
```
これで、その方の用途には十分でした。最初の正規表現で何も見つからなければ、次の正規表現を試す、という形にできます。よくあるパターンから対応し、次に少ないパターンへ広げていきます。
少し退屈な作業ですが、AI よりも費用を抑えられます。

この例で伝えたいのは、すべての課題に AI が必要なわけではないということです。少し工夫するだけで、大きく費用を節約できる場合があります。

### B3 への対応：ページ送りの違い {#solving-issue-b3-pagination-variations}
現在、Scrapling にはページ送りのリンクを自動で特定する専用の方法はありません。Spider は `response.follow()` でページ送りのリンクをたどります。

ただし、多くのサイトは、よくあるパターンを探すことで対応できます。例えば `page.find_by_text('Next')['href']`、`page.find_by_text('load more')['href']`、あるいは `'a[href*="?page="]'` や `'a[href*="/page/"]'` のようなセレクターを使います。

## 費用と節約効果の比較 {#cost-comparison-and-savings}
簡単に比較します。

| 項目 | Scrapling | AI ツール（Browse AI、Oxylabs など） |
|----------------|----------------------------------------------------------------------------|----------------------------------------------------------------------------|
| 費用 | 無料で、ライブラリの利用回数に応じた料金はありません | 有料プランがあり、提供元と使用量によって料金が変わります |
| セットアップ | 少しの技術知識と手動の設定が必要です | ノーコードのものが多く、技術に詳しくない方でも使いやすいです |
| 使い方 | コード、ターミナル、MCP サーバーから使えます | 多くは GUI または API を使いますが、提供元の機能によります |
| 規模の拡大 | ユーザーの実装によります | 大規模運用向けのマネージドサービスが用意されています |
| 変化への対応 | `adaptive` やセレクター以外の選択方法で柔軟に対応できます | AI による自動対応ができますが、変更が多いと費用がかかります |

最新の料金は [Browse AI の料金](https://www.browse.ai/pricing)と [Oxylabs Web Scraper API の料金](https://oxylabs.io/products/scraper-api/web/pricing)をご確認ください。

## おわりに {#conclusion}
AI は強力ですが、多くの Web スクレイピング作業では費用が高くなりすぎることがあります。Scrapling は、特定サイトから幅広いサイトまで、実際の課題に対応できる柔軟で費用を抑えたツールを提供します。高価な AI を使わずに済む場合も多くあります。`adaptive`、さまざまな選択方法、高機能な Fetcher を使うと、変化に強いスクレイパーを効率よく作れます。

ドキュメントを読み進めて、今後の Web スクレイピングで Scrapling がどう役立つかをご確認ください。
