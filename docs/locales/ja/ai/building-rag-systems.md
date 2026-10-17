---
title: "Scrapling で Web サイトをクロールし、RAG 用の Markdown を作る"
description: "ページのレスポンスを Markdown に変換する方法と、ContentSpider でサイトを収集する方法を紹介します。RAG の分割とインデックス作成に使う文書集合を準備します。"
---

# Scrapling で RAG システムを作る {#building-rag-systems-with-scrapling}

RAG パイプラインの品質は、入力するテキストの品質に左右されます。生の HTML には、マークアップ、ナビゲーション、スクリプト、トラッキング関連の不要な内容が含まれ、トークンを消費します。隠されたプロンプトインジェクションの内容が、そのまま LLM に渡ることもあります。Scrapling は LLM を使わずに、ページやサイト全体を、不要な内容を取り除いた Markdown に変換します。取り込み処理が速く、ページごとの LLM 費用もかかりません。

## インストール {#installation}

```bash
pip install "scrapling[rag]"

scrapling install
```

`rag` の追加依存関係には、Fetcher と Markdown 変換機能が含まれています。`ai`、`shell`、`all` にも含まれます。`scrapling install` コマンドはブラウザの依存関係をダウンロードします。これはブラウザを使う Fetcher にだけ必要です。

## 1 ページを Markdown に変換する {#one-page-to-markdown}

すべての [Response](../fetching/choosing.md#response-object) に `markdown()` メソッドがあります。

```python
from scrapling.fetchers import Fetcher

markdown = Fetcher.get("https://example.com").markdown(main_content_only=True)
```

すべての Fetcher で使えるため、Cloudflare で保護されたページも 1 行で変換できます。

```python
from scrapling.fetchers import StealthyFetcher

markdown = StealthyFetcher.fetch("https://protected.example.com", solve_cloudflare=True).markdown(main_content_only=True)
```

出力は次の 2 つの引数で調整できます。

- `main_content_only`：ページの `<body>` タグ内だけを変換します。
- `css_selector`：CSS セレクターに一致する要素だけを変換します。すべての一致結果が結合されます。パイプラインに必要な部分だけを取り出し、トークンを節約できます。

```python
markdown = Fetcher.get("https://example.com/docs/page").markdown(css_selector="article")
```

引数にかかわらず、変換前には必ずスクリプト、スタイル、隠された内容を取り除きます。これは、[MCP サーバー](mcp-server.md)が AI エージェントをプロンプトインジェクションから守るために使う処理と同じです。インラインスタイルで隠された要素、`aria-hidden="true"` の要素、隠されたスロット、`<template>` タグ、HTML コメント、ゼロ幅文字を変換前に削除します。MCP サーバーは `main_content_only=True` のときにこの処理を使います。

## サイト全体を Markdown の文書集合に変換する {#a-whole-website-to-a-markdown-corpus}

`ContentSpider` テンプレートは、サイトをクロールして各ページを変換します。[Spider フレームワーク](../spiders/architecture.md)を使うため、並行処理、AutoThrottle、robots.txt への対応、一時停止と再開も利用できます。

```python
from scrapling.spiders import ContentSpider

class DocsSpider(ContentSpider):
    name = "docs"
    start_urls = ["https://example.com/docs/"]
    allowed_domains = {"example.com"}
    output_dir = "docs_markdown"
    max_pages = 200

result = DocsSpider().start()
result.items.to_jsonl("docs.jsonl")
```

クロールした各ページは、`url`、`title`、`markdown` キーを持つ 1 つのデータ項目になります。`output_dir` を設定すると、各ページを URL に基づく名前の Markdown ファイルにも保存します。上の実行例では、`.md` ファイルのフォルダーと、取り込みに使える `docs.jsonl` の両方が得られます。

対象サイトの外へクロールが広がらないよう、このテンプレートには `allowed_domains` が必要です。設定できるオプションは次のとおりです。

- `css_selector` / `main_content_only`：各ページの `markdown()` に渡します。`main_content_only` はデフォルトで有効です。
- `output_dir`：設定すると、ページごとに Markdown ファイルを書き出します。
- `max_pages`：変換するページ数の上限です。上限に達した時点でキューに入っているリクエストは取得される場合がありますが、変換はされません。`0`（デフォルト）では上限を設けません。

デフォルトでは、`allowed_domains` 内のすべてのページリンクをたどります。このテンプレートは [CrawlSpider](../spiders/generic-templates.md#crawlspider) を基にしているため、`rules()` をオーバーライドし、独自の [LinkExtractor](../spiders/generic-templates.md#linkextractor-reference) でクロール範囲を調整できます。`allow` で対象の URL パターンに絞り、`deny` でログインページ、タグ一覧、印刷用ページなどの不要なパターンを除外します。

```python
from scrapling.spiders import CrawlRule, LinkExtractor, ContentSpider

class DocsSpider(ContentSpider):
    name = "docs"
    start_urls = ["https://example.com/"]
    allowed_domains = {"example.com"}

    def rules(self):
        return [CrawlRule(LinkExtractor(allow=r"/docs/", deny=[r"/docs/changelog/", r"\?print="]))]
```

`deny` は `allow` より優先されます。通常の **CrawlSpider** と同様に、ルールには `priority` や `process_request` フックも指定できます。

## ベクトルストアに渡す {#feeding-a-vector-store}

JSONL 出力は、どの埋め込みパイプラインにも渡せます。最小限の例を示します。

```python
import json

with open("docs.jsonl", encoding="utf-8") as f:
    for line in f:
        page = json.loads(line)
        for chunk in split_into_chunks(page["markdown"]):
            vector_store.add(text=chunk, metadata={"url": page["url"], "title": page["title"]})
```

Spider の `css_selector` で、分割前に定型部分を取り除きます。後段で除去するよりも、最初から必要な内容だけを渡せます。埋め込みに含まれる不要な内容が少ないほど、検索結果の品質が上がります。

## 対話形式で使う方法 {#interactive-alternatives}

パイプラインではなく対話形式でスクレイピングする場合は、[MCP サーバー](mcp-server.md)を使うと、同じ Markdown 抽出機能を AI チャットボットのツールとして利用できます。[Agent Skill](agent-skill.md) は、コーディングエージェントがこのコードを自分で書けるようにします。
