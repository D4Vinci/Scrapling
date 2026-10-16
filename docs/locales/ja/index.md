---
title: "Scrapling：Python のウェブスクレイピングフレームワーク"
description: "Scrapling：現代のウェブを手軽にスクレイピング。"
---

<style>
.md-typeset h1 {
  display: none;
}
[data-md-color-scheme="default"] .only-dark { display: none; }
[data-md-color-scheme="slate"] .only-light { display: none; }
</style>

<br/>
<div align="center">
    <a href="index.html" alt="カバー画像">
        <img alt="Scrapling" src="assets/cover_light.svg" class="only-light">
        <img alt="Scrapling" src="assets/cover_dark.svg" class="only-dark">
    </a>
</div>

<h2 align="center"><i>現代のウェブを手軽にスクレイピング</i></h2><br>

Scrapling は Python のウェブスクレイピングフレームワークです。高速な HTTP リクエスト、ステルスブラウザ、ページの解析、並行クロールをひとつのライブラリで扱えます。

静的なページの取得、JavaScript の実行、サイトの操作、背後にある API からのデータ抽出ができます。セッションの再利用、プロキシの切り替え、自動再試行、一時停止と再開、データの出力に対応したクローラーを作れます。

Python やターミナルから使うほか、MCP サーバーと Agent Skill を通じて AI エージェントからも使えます。少数の項目を取り出す作業から、サイト全体を整理された Markdown ファイルとして保存する作業まで対応します。

## Scrapling でできること {#what-you-can-do-with-scrapling}

- **[ページの取得と操作](fetching/choosing.md)**：高速な HTTP リクエスト、ステルスブラウザ、JavaScript の実行、Cloudflare Turnstile と Interstitial への対応、永続セッション、バックグラウンド API レスポンスの記録。
- **[解析とデータ抽出](parsing/selection.md)**：CSS、XPath、テキスト、正規表現による検索、ページ変更後の要素の追跡、類似要素の検索、整理された Markdown の出力。
- **[クロールと出力](spiders/getting-started.md)**：並行クロール、プロキシの切り替え、再試行、AutoThrottle、一時停止と再開、ストリーミング、すぐに使えるテンプレート、JSON・JSONL・CSV・XML への出力。
- **[AI やターミナルからの利用](ai/mcp-server.md)**：AI エージェントがページを操作してデータを抽出するための MCP サーバー、Agent Skill、CLI コマンド、対話型シェル。

まずはひとつのページから始めます。

```python
from scrapling.fetchers import Fetcher

page = Fetcher.get('https://quotes.toscrape.com/')
quotes = page.css('.quote .text::text').getall()
print(quotes)
```

Spider を使えば、より多くのページを取得できます。

```python
from scrapling.spiders import Spider, Response

class QuotesSpider(Spider):
    name = "quotes"
    start_urls = ["https://quotes.toscrape.com/"]

    async def parse(self, response: Response):
        for quote in response.css('.quote'):
            yield {
                "text": quote.css('.text::text').get(),
                "author": quote.css('.author::text').get(),
            }

result = QuotesSpider().start()
print(len(result.items))
result.items.to_json("quotes.json")
```

このコードは `10` を表示し、名言と作者を `quotes.json` に保存します。

## 主なスポンサー {#top-sponsors}

--8<-- "sponsors.html"

<i><sub>ここに広告を掲載するには、[こちら](https://github.com/sponsors/D4Vinci)からプランを選んでください。プランに応じた特典もあります。</sub></i>

## 主な機能 {#key-features}

### Spider：本格的なクロールフレームワーク {#spiders-a-full-crawling-framework}
- 🕷️ **Scrapy に似た Spider API**：`start_urls`、非同期の `parse` コールバック、`Request` と `Response` オブジェクトで Spider を定義します。
- ⚡ **並行クロール**：同時に処理するリクエスト数、ドメインごとの制限、ダウンロードの待ち時間を設定できます。
- 🔄 **複数のセッション**：ひとつの Spider で HTTP リクエストとステルス対応のヘッドレスブラウザを使えます。セッション ID でリクエストの処理先を選びます。
- 💾 **一時停止と再開**：`crawldir` で待機中のリクエストと訪問済み URL を保存します。Ctrl+C で安全に停止し、同じディレクトリで起動すると続きから再開できます。
- 📡 **ストリーミング**：`async for item in spider.stream()` で、抽出したデータをすぐに受け取れます。統計もリアルタイムで確認できます。画面への表示、データ処理、長時間のクロールに適しています。
- 🛡️ **ブロックの検出**：ブロックされたリクエストを自動で検出し、再試行します。処理は変更できます。
- 🚦 **AutoThrottle**：サイトの応答速度に合わせて、ドメインごとの待ち時間を自動調整します。ブロックや頻度制限を受けたら待ち時間を 2 倍にするか、`Retry-After` が指定する時間を待ちます。問題が収まると再び速度を上げます。
- 🤖 **robots.txt の遵守**：`robots_txt_obey` を有効にすると、`Disallow`、`Crawl-delay`、`Request-rate` に従います。ルールはドメインごとにキャッシュします。
- 🧪 **開発モード**：初回のレスポンスをディスクに保存し、次回から再利用します。サーバーに再度アクセスせずに `parse()` を調整できます。
- 🧩 **すぐに使える Spider テンプレート**：`CrawlSpider` はルールに沿ってリンクをたどり、`SitemapSpider` は sitemap や robots.txt を起点にクロールします。`XMLFeedSpider` と `CSVFeedSpider` は XML・RSS・CSV フィードを読み取ります。`ShopifySpider` は公開 Shopify ストアの商品を取得し、バリエーションごとに 1 件のデータを出力します。
- 🔗 **リンク抽出**：`LinkExtractor` はパターンによる許可と除外、ドメインや拡張子の絞り込み、CSS と XPath による範囲指定、URL の正規化に対応します。テンプレート内でも単体でも使えます。
- 📦 **データの出力**：フックと独自の処理を使うか、組み込みの JSON・JSONL・CSV・XML 出力を使えます。`result.items.to_json()`、`to_jsonl()`、`to_csv()`、`to_xml()` を呼び出します。

### セッションを使ったページの取得 {#advanced-websites-fetching-with-session-support}
- **HTTP リクエスト**：`Fetcher` で高速かつ検出されにくい HTTP リクエストを送れます。ブラウザの TLS フィンガープリントとヘッダーの模倣や、HTTP/3 に対応します。
- **動的なページの読み込み**：`StealthyFetcher` のブラウザ自動化で動的なサイトを取得できます。Playwright の Chromium と Google Chrome に対応します。
- **ボット検出の回避**：`StealthyFetcher` は自動化の痕跡を隠し、フィンガープリントを偽装します。Cloudflare Turnstile や Interstitial の各種検証を自動処理できます。
- **セッション管理**：`FetcherSession` と `StealthySession` は、リクエスト間で Cookie と状態を保持します。
- **プロキシの切り替え**：`ProxyRotator` は、すべてのセッションで順番に、または独自のルールでプロキシを切り替えます。リクエストごとにプロキシを指定することもできます。
- **ドメインと広告のブロック**：指定したドメインとそのサブドメインへのリクエストを止められます。ブラウザ Fetcher には広告ブロック機能もあり、約 3,500 の広告・追跡用ドメインに対応します。
- **DNS リークの防止**：DNS-over-HTTPS を有効にすると、Cloudflare の DoH を通じて DNS を問い合わせます。プロキシ使用時の DNS リークを防ぎます。
- **リモートブラウザ**：CDP と `cdp_url` を使い、すでに動いているブラウザに接続できます。同じパソコン、別のサーバー、ブラウザ提供サービスのいずれでも使えます。`executable_path` で、各ブラウザ Fetcher に独自の Chromium を指定することもできます。
- **バックグラウンド API レスポンスの記録**：ブラウザセッションで `record_requests=True` を有効にし、`session.network.search(limit=None)` で保存済みレスポンスを検索します。リクエストを送り直さずに、複数のページ読み込みで発生した API データや HTTP エラーを確認できます。履歴には上限があり、テキストのレスポンス本文を保存します。
- **非同期対応**：すべての Fetcher で非同期処理を使えます。専用の非同期セッションもあります。

### 解析とデータ抽出 {#parsing-and-data-extraction}
- 🔄 **要素の再検索**：サイトが変わった後も、類似度を使って要素を見つけ直します。
- 🎯 **柔軟な選択**：CSS、XPath、フィルター、テキスト、正規表現などを使えます。
- 🔍 **類似要素の検索**：見つけた要素に似た要素を自動で探します。

### AI 機能 {#ai-features}
- 🤖 **MCP サーバー**：Claude や Cursor などの AI アシスタントとエージェントが Scrapling を使ってデータを抽出できます。HTTP リクエスト、ブラウザ操作、スクリーンショット、保存済みログイン状態、バックグラウンド API レスポンスに対応します。ステルスブラウザとツールを使い、対応する能力を持つモデルが CAPTCHA を処理できるようにします。Cloudflare 検証の処理機能もあります。モデルへ送る内容を減らし、広告をブロックし、プロンプトインジェクションから保護します。CDP によるリモートブラウザ接続や、認証付きの HTTP 接続にも対応します。（[デモ動画](https://www.youtube.com/watch?v=qyFk3ZNwOxE)）
- 🧠 **Agent Skill**：インストールして使える [Agent Skill](ai/agent-skill.md) が、コーディングエージェントにライブラリの使い方を伝えます。現在の API に合ったコードを書く助けになります。
- 📚 **RAG 向けの Markdown**：1 行のコード（`page.markdown()`）で、ページを整理・クリーニングした LLM 向けの Markdown に変換します。`ContentSpider` テンプレートを使えば、サイト全体を Markdown ファイルに保存できます。この処理に LLM は不要です。（[ドキュメント](ai/building-rag-systems.md)）

### 高速で、実際の作業にも使われています {#high-performance-battle-tested-architecture}
- 🚀 **高速な処理**：最適化により、多くの Python スクレイピングライブラリを上回る速度を実現しています。
- 🔋 **少ないメモリ使用量**：最適化したデータ構造と、必要なときだけ読み込む仕組みを使っています。
- ⚡ **高速な JSON 出力**：標準ライブラリの 10 倍の速度です。
- 🏗️ **実際の作業で検証済み**：テストカバレッジは 92% で、すべてのコードに型ヒントがあります。この 1 年間、数百人が毎日のデータ抽出に使ってきました。

### 開発とデータ抽出のためのツール {#developerweb-scraper-friendly-experience}
- 🎯 **対話型シェル**：Scrapling と連携した IPython シェルを追加できます。ショートカットやツールでスクリプトの開発を助けます。curl リクエストを Scrapling のリクエストに変換し、結果をブラウザで確認できます。
- 🚀 **ターミナルからの利用**：コードを書かずに URL の内容を取得できます。
- 🛠️ **DOM の移動**：親要素、兄弟要素、子要素をたどれます。
- 🧬 **テキスト処理**：正規表現、テキストのクリーニング、最適化した文字列操作を使えます。
- 📝 **セレクターの生成**：任意の要素に対する CSS と XPath のセレクターを生成します。
- 🔌 **使い慣れた API**：Scrapy や BeautifulSoup に似た API で、Scrapy と Parsel と同じ疑似要素を使えます。
- 🤝 **Scrapy との連携**：コールバックに `scrapling_response` デコレーターを付けると、取得済みのレスポンスを Scrapling のパーサーで解析できます。プログラムを書き直す必要はありません。
- 📘 **すべてのコードに型ヒント**：エディターでの確認とコード補完を助けます。変更のたびに、すべてのコードを **PyRight** と **MyPy** で自動チェックします。
- 🔋 **すぐに使える Docker イメージ**：リリースごとに、すべてのブラウザを含む Docker イメージを自動で作成・公開します。


## GitHub スターの推移 {#star-history}
Scrapling の公開後、GitHub のスターは増え続けています。下のグラフで確認できます。

<div id="chartContainer">
  <a href="https://github.com/D4Vinci/Scrapling">
    <img id="chartImage" alt="GitHub スター数の推移" loading="lazy" src="https://api.star-history.com/svg?repos=D4Vinci/Scrapling&type=Date" height="400"/>
  </a>
</div>

<script>
const observer = new MutationObserver((mutations) => {
  mutations.forEach((mutation) => {
    if (mutation.attributeName === 'data-md-color-media') {
      const colorMedia = document.body.getAttribute('data-md-color-media');
      const isDarkScheme = document.body.getAttribute('data-md-color-scheme') === 'slate';
      const chartImg = document.querySelector('#chartImage');
      const baseUrl = 'https://api.star-history.com/svg?repos=D4Vinci/Scrapling&type=Date';
      
      if (colorMedia === '(prefers-color-scheme)' ? isDarkScheme : colorMedia.includes('dark')) {
        chartImg.src = `${baseUrl}&theme=dark`;
      } else {
        chartImg.src = baseUrl;
      }
    }
  });
});

observer.observe(document.body, {
  attributes: true,
  attributeFilter: ['data-md-color-media', 'data-md-color-scheme']
});
</script>


## インストール {#installation}
Scrapling には Python 3.10 以上が必要です。

```bash
pip install scrapling
```

!!! warning "注意"

    このコマンドはパーサーとその依存パッケージだけをインストールします。Fetcher やコマンドラインツールは含まれません。この状態で上の例のように `scrapling.fetchers` や `scrapling.spiders` からインポートすると、`ModuleNotFoundError` が発生します。Fetcher や Spider を使う場合は、先に以下の手順で Fetcher の依存パッケージをインストールしてください。

### 追加の依存パッケージ {#optional-dependencies}

1. Fetcher、関連するクラス、以下の追加機能を使う場合は、Fetcher とブラウザに必要なパッケージをインストールします。
    ```bash
    pip install "scrapling[fetchers]"
    
    scrapling install           # normal install
    scrapling install  --force  # force reinstall
    ```

    すべてのブラウザ、必要なシステムパッケージ、フィンガープリントを変更するツールがダウンロードされます。

    コマンドの代わりに、Python のコードからインストールすることもできます。
    ```python
    from scrapling.cli import install
    
    install([], standalone_mode=False)          # normal install
    install(["--force"], standalone_mode=False) # force reinstall
    ```

2. 追加機能：


     - MCP サーバーをインストール：
       ```bash
       pip install "scrapling[ai]"
       ```
     - [RAG システムの構築](ai/building-rag-systems.md)に必要なパッケージをインストール：
       ```bash
       pip install "scrapling[rag]"
       ```
     - 対話型シェルと `extract` コマンドをインストール：
         ```bash
         pip install "scrapling[shell]"
         ```
     - すべての機能をインストール：
         ```bash
         pip install "scrapling[all]"
         ```
   ブラウザ Fetcher を使う場合は `scrapling install` を実行してください。HTTP リクエストにはブラウザのインストールは不要です。

### Docker {#docker}
すべての追加機能とブラウザを含む Docker イメージを DockerHub から取得することもできます。
```bash
docker pull pyd4vinci/scrapling
```
GitHub のレジストリからも取得できます。
```bash
docker pull ghcr.io/d4vinci/scrapling:latest
```
このイメージはリポジトリのメインブランチを使い、GitHub Actions で自動作成・公開されます。

## ドキュメントの構成 {#how-the-documentation-is-organized}
Scrapling のドキュメントは多いため、[Diátaxis のドキュメント体系](https://diataxis.fr/)に沿って整理しています。

## プロジェクトの支援 {#support}

Scrapling を気に入っていただけたら、次の方法で開発を支援できます。

- ⭐ [GitHub リポジトリ](https://github.com/D4Vinci/Scrapling)にスターを付ける。
- 🚀 [Twitter](https://x.com/Scrapling_dev) をフォローし、[Discord コミュニティ](https://discord.gg/EMgGbDceNQ)に参加する。
- 💝 [プロジェクトにスポンサーとして参加する、またはコーヒーをおごる](donate.md)。:wink:
- 🐛 [GitHub Issues](https://github.com/D4Vinci/Scrapling/issues) で不具合を報告し、機能を提案する。

## ライセンス {#license}

本プロジェクトは BSD-3 ライセンスで公開されています。詳しくは [LICENSE](https://github.com/D4Vinci/Scrapling/blob/main/LICENSE) ファイルをご覧ください。
