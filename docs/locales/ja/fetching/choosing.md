---
title: "Web スクレイピングで HTTP リクエストとブラウザを選ぶ"
description: "タスクに合った Fetcher または StealthyFetcher を選びます。直接の HTTP リクエスト、JavaScript の描画、再利用できるセッションの使い分けを紹介します。"
---

# Fetcher の基本 {#fetchers-basics}

## はじめに {#introduction}
Fetcher は、1 行でリクエストを送ったりページを取得したりできるクラスです。さまざまな機能を備え、[Response](#response-object) オブジェクトを返します。v0.3 からは、すべての Fetcher にセッションを維持する専用クラスがあります。たとえばブラウザを使う Fetcher では、何度もブラウザを開かず、すべてのリクエストが終わるまで同じブラウザを開いておけます。使い方はタスクに応じて選んでください。

v0.2 より前の Scrapling は解析エンジンだけでした。Fetcher を追加したのは、Web スクレイピングに必要な作業を少しずつすべて扱えるようにするためです。

> Fetcher は、ほかのライブラリを単純に包んだものではありません。それらをページ取得のエンジンとして使い、元のエンジンにない機能を追加しています。また、エンジンの機能を活用し、Web スクレイピング向けに最適化しています。

## Fetcher の概要 {#fetchers-overview}

Scrapling には HTTP 用の `Fetcher` と `AsyncFetcher`、ブラウザ用の `StealthyFetcher` があります。繰り返しリクエストを送るためのセッションクラスも用意しています。

次の表を選ぶ際の参考にしてください。


| 機能 | Fetcher | StealthyFetcher |
|--------------------|---------------------------------------------------|--------------------------------------------------------------------------------------------|
| 相対的な速度 | 🐇🐇🐇🐇🐇 | 🐇🐇🐇 |
| ステルス性 | ⭐⭐ | ⭐⭐⭐⭐⭐ |
| ボット対策への対応 | ⭐⭐ | ⭐⭐⭐⭐⭐ |
| JavaScript の読み込み | ❌ | ✅ |
| メモリ使用量 | ⭐ | ⭐⭐⭐ |
| 主な用途 | HTTP リクエストだけで済む基本的なスクレイピング | - 動的に読み込まれるサイト <br/>- 小規模な自動化 <br/>- 簡単なものから複雑なものまでの保護への対応 |
| ブラウザ | ❌ | Chromium と Google Chrome |
| 使用するブラウザ API | ❌ | Playwright |
| 設定の難しさ | 簡単 | 簡単 |

次のページから、それぞれを詳しく説明します。

## Fetcher 共通のパーサー設定 {#parser-configuration-in-all-fetchers}
すべての Fetcher は同じ形でインポートできます。
```python
from scrapling.fetchers import Fetcher, AsyncFetcher, StealthyFetcher
```
インスタンスを作らず、そのまま使えます。この場合はパーサーの標準設定を使います。
```python
page = StealthyFetcher.fetch('https://example.com') 
```
レスポンスを返す前に使うパーサー（[Selector クラス](../parsing/main_classes.md#selector)）を設定するには、先に次を実行します。
```python
from scrapling.fetchers import Fetcher
Fetcher.configure(adaptive=True, keep_comments=False)  # and the rest
```
または、
```python
from scrapling.fetchers import Fetcher
Fetcher.adaptive=True
Fetcher.keep_comments=False
```
その後は通常どおりコードを続けます。

設定できる引数は `adaptive`、`adaptive_domain`、`huge_tree`、`keep_comments`、`storage`、`storage_args` です。[Selector](../parsing/main_classes.md#selector) の引数と同じです。`<fetcher_class>.display_config()` で現在の設定をいつでも表示できます。

!!! info

    `adaptive` は標準では無効です。この機能を使うには、有効にする必要があります。

### リクエストごとのパーサー設定 {#set-parser-config-per-request}
上の設定は、使い方を簡単にするため、そのクラスから送るすべてのリクエストに適用されます。

リクエストごとに違う設定が必要な場合は、メソッド（`fetch`/`get`/`post`/...）の `selector_config` に辞書を渡してください。

## Response オブジェクト {#response-object}
`Response` は [Selector](../parsing/main_classes.md#selector) を基にしたクラスで、ヘッダー、ステータス、Cookie などのレスポンス情報も持っています。
```python
from scrapling.fetchers import Fetcher
page = Fetcher.get('https://example.com')

page.status          # HTTP status code
page.reason          # Status message
page.cookies         # Response cookies as a dictionary
page.headers         # Response headers
page.request_headers # Request headers
page.history         # Response history of redirections, if any
page.body            # Raw response body as bytes
page.encoding        # Response encoding
page.meta            # Response metadata dictionary (e.g., proxy used). Mainly helpful with the spiders system.
```
すべての Fetcher は `Response` を返します。`record_requests=True` のブラウザセッションでも、`session.network.search(limit=None)` や `session.network.get(request_id)` から保存済みの `Response` を取得できます。API レスポンスの保存と v5 への移行については、[ネットワーク履歴](stealthy.md#network-history)を参照してください。

`Response` を使えば、1 行でページを LLM 向けの読みやすい Markdown に変換できます。
```python
markdown = Fetcher.get('https://example.com').markdown(main_content_only=True)
```
変換前には必ず、スクリプト、スタイル、隠れた内容、プロンプトインジェクションの内容を削除します。`css_selector` で特定の要素だけを変換することもできます。追加依存関係の `rag` が必要で、`ai`/`shell`/`all` にも含まれています。詳しくは [RAG システムの構築](../ai/building-rag-systems.md)を参照してください。

!!! note

    [Selector](../parsing/main_classes.md#selector) と異なり、v0.4 以降の `Response` の本文は常に bytes です。
