---
title: "Scrapling の変更履歴"
description: "Scrapling のリリースノートです。新機能、修正、互換性に影響する変更をまとめています。"
---

# 変更履歴 {#changelog}

Scrapling の主な変更を、[GitHub のリリース](https://github.com/D4Vinci/Scrapling/releases)からまとめています。

## [v0.5](https://github.com/D4Vinci/Scrapling/releases/tag/v0.5) - 2026-10-17 {#v0.5}

**Scrapling v0.5 は、取得処理、解析、Spider、ブラウザの自動操作、AI ツール、10 言語のドキュメントまで、ほぼすべてを更新するリリースです 🚀**

!!! warning "警告"

    **このリリースには互換性に影響する変更が多数あり、ここではすべてを紹介できません。更新前に[v0.5 への移行ガイド](migrating-to-v0.5.md)を確認してください。**

### 🚀 新機能と使いやすさの改善 {#v0.5-new-stuff-and-quality-of-life-changes}

- **AI エージェント向けの MCP サーバーの機能を大幅に増やし、ほぼすべての CAPTCHA を解決できるようになりました**（[ドキュメント](ai/mcp-server.md)を参照）：

    - **ブラウザ上の操作をまとめて実行できます**。フォーム入力、クリック、ホバー、スクロール、キーボード操作、ダイアログ処理、結果の待機を、指定した順番で実行します。さまざまな入力欄とゆっくりした操作に対応し、最初のエラーで操作を停止します。
    - **再読み込みせずに現在のページを読み取り、検索できます**。ページ全体または単一の要素から、HTML、Markdown、テキストを抽出します。検索できるページスナップショットには、要素のロール、名前、位置が表示されます。対象を絞った表示でも、周囲の文脈を保持します。
    - **独自の JavaScript を実行し、必要な部分のスクリーンショットを撮影できます**。ページ自身の JavaScript にアクセスして、非同期処理を含むスクリプトを実行できます。個別の要素、ビューポート、ページ全体を PNG または JPEG で撮影できます。
    - **ネットワーク通信を確認し、ログイン状態を再利用できます**。記録したリクエストとレスポンスを調べ、ブラウザのログイン状態を保存、復元できます。開いた Shadow DOM と閉じた Shadow DOM の中にある要素も操作できます。記録した通信は、セッションを閉じる前に読み取ってください。
    - **トークンの使用量を減らし、エラーをわかりやすくしました**。短いツール説明と共通の案内で重複する文章を減らしました。ブラウザやリクエストの失敗も、役に立つエラーメッセージとともにエージェントに届きます。

- **ページの裏側で発生するリクエストを確認できます**。`record_requests=True` を有効にすると、ページの読み込み、操作、タブをまたいで完了した通信を記録します。リクエストを再送せずに、保存したレスポンスを調べられます（[ドキュメント](fetching/stealthy.md#network-history)を参照）。

    ```python
    from scrapling.fetchers import StealthySession

    with StealthySession(record_requests=True) as session:
        session.fetch("https://example.com", network_idle=True)
        for response in session.network.search(url_pattern=r"/api/", limit=None):
            print(response.url, response.status, response.body)
    ```

    - URL、メソッド、リソースの種類、ステータスで絞り込み、ID で 1 つのレスポンスを取得できます。通常の `Response` API を使って、ヘッダー、送信データ、API レスポンス、HTTP エラー、リダイレクトを確認できます。
    - 対応するテキスト本文をサイズ制限内で保持し、メタデータと、本文を保存できない場合の理由も記録します。既定の上限は 1,000 リクエストです。同期、非同期のセッションに対応し、保存した Python の履歴はセッションを閉じた後も読み取れます。

- **一度保存したログイン状態を、次の実行でも再利用できます**。`save_state(path)` と `load_state(path)` は、Cookie、ローカルストレージ、IndexedDB を Playwright と互換性のある JSON で保存します。同期、非同期のブラウザセッションで利用できます（[ドキュメント](fetching/stealthy.md#save-and-load-session-state)を参照）。
    - ページの取得や再読み込みの前に状態を読み込んでください。起動済みの共有ブラウザコンテキストが必要で、`proxy_rotator` は使用できません。タブ、ブラウザ設定、`sessionStorage` は保存されません。

- **`pierce_shadow=True` で開いた Shadow DOM を抽出できます**。抽出後は、通常どおり CSS や XPath を使えます。ブラウザ Fetcher、セッション、CLI の `--pierce-shadow` オプションで利用できます。実際のページを変更せず、スロットの内容を保持します。取得する HTML には、閉じた Shadow ルートと iframe のドキュメントは含まれません（[ドキュメント](fetching/stealthy.md#shadow-dom)を参照）。

- **Spider がサイトをたどる順序を選べます**。`CrawlSpider` と、`ContentSpider` を含むそのサブクラスでは、`crawl_strategy="bfs"` で先に追加したリクエストから、`"dfs"` で後に追加したリクエストから処理するように設定できます。リクエストの優先度はこの順序より優先され、同時に処理するページの完了順は異なる場合があります（[ドキュメント](spiders/generic-templates.md#crawl-order)を参照）。

### 🐛 バグ修正 {#v0.5-bug-fixes}

- **Cloudflare チャレンジの解決を改善しました**。遅れて表示されるウィジェットを検出し、不要な待機を減らし、受動型チャレンジと非表示フレームの再試行ループに上限を設けました（[#468](https://github.com/D4Vinci/Scrapling/issues/468) と [#509](https://github.com/D4Vinci/Scrapling/issues/509) を修正）。
- **管理者権限で実行した Windows シェルからブラウザを起動する問題を修正しました**（[#463](https://github.com/D4Vinci/Scrapling/issues/463) を修正）。
- **独自のブラウザフラグを追加しても、組み込みのステルス用フラグを保持するようにしました**。@alkaz-nodemaven による [#430](https://github.com/D4Vinci/Scrapling/pull/430) の変更です。
- **ブラウザのレスポンスの文字セット解析を改善しました**。大文字と小文字の違い、空白、引用符で囲まれた値を含む宣言にも対応します。
- **解決すべき Cloudflare チャレンジがない場合に、チャレンジが見つからないことをエラーとして記録しないようにしました**（[#459](https://github.com/D4Vinci/Scrapling/issues/459) を修正）。

- **リクエストのフィンガープリントを修正しました**。クエリパラメーターは @yetval による [#448](https://github.com/D4Vinci/Scrapling/pull/448)、空または偽と評価される JSON 本文は @ac1982 による [#480](https://github.com/D4Vinci/Scrapling/pull/480)、ヘッダーの挿入順序は @SarwadnyaMahajan による [#466](https://github.com/D4Vinci/Scrapling/pull/466) の変更です。
- **リンクをたどる際に、前のリクエストのデータが引き継がれる問題を修正しました**。古い本文関連ヘッダーが残る問題も含みます。@yetval による [#462](https://github.com/D4Vinci/Scrapling/pull/462) の変更です。
- **ブロックされたレスポンスが、成功したレスポンスとして開発用キャッシュに保存されないようにしました**。@Kuang-xianxin による [#446](https://github.com/D4Vinci/Scrapling/pull/446) の変更です。
- **クロールが例外で失敗した場合に、チェックポイントファイルを保持するようにしました**。@SulimanAbdulrazzaq による [#486](https://github.com/D4Vinci/Scrapling/pull/486) の変更です。
- **robots.txt の取得に失敗した場合の処理を修正しました**。取得失敗をクロールの許可としてキャッシュしないようにしました。@prateekraawat1 による [#443](https://github.com/D4Vinci/Scrapling/pull/443) の変更です。
- **範囲を制限するセレクターを使ったリンク抽出を修正しました**。一致する要素がない場合と、リンク要素自体を選択する場合に対応します。@SulimanAbdulrazzaq による [#452](https://github.com/D4Vinci/Scrapling/pull/452) と [#483](https://github.com/D4Vinci/Scrapling/pull/483) の変更です。
- **サイトマップのコールバックの振り分けを修正しました**。@SulimanAbdulrazzaq による [#458](https://github.com/D4Vinci/Scrapling/pull/458) の変更です。**コメントや処理命令を含む XML の解析も修正しました**。@sup3dev による [#450](https://github.com/D4Vinci/Scrapling/pull/450) の変更です。
- **robots.txt と CSV フィードの先頭にあるバイトオーダーマークに対応しました**。@SulimanAbdulrazzaq による [#453](https://github.com/D4Vinci/Scrapling/pull/453) の変更です。
- **Spider の HTTP セッションでの `stealthy_headers` の扱いを修正しました**。`curl_cffi` に直接渡さず、セッションに渡すようにしました。@Yigtwxx による [#475](https://github.com/D4Vinci/Scrapling/pull/475) の変更です。

- **辞書形式のフォームで、リストとタプルの値のエンコードを修正しました**。リクエスト本文の優先順位と、既存の `None` の扱いは維持します。@SulimanAbdulrazzaq による [#485](https://github.com/D4Vinci/Scrapling/pull/485) の貢献を含みます。
- **セッションとリクエストごとの HTTP ヘッダーを、大文字と小文字を区別せずに結合する処理を修正しました**。@SulimanAbdulrazzaq による [#487](https://github.com/D4Vinci/Scrapling/pull/487) の変更です。
- **CLI のリクエストで、空または偽と評価される JSON 本文が通知なく捨てられる問題を修正しました**。@SulimanAbdulrazzaq による [#484](https://github.com/D4Vinci/Scrapling/pull/484) の変更です。
- **Markdown とテキストファイルの書き出しで、常に UTF-8 を使うようにしました**。変換エラーによって既存の出力ファイルが切り詰められる問題も防ぎます。@SulimanAbdulrazzaq による [#488](https://github.com/D4Vinci/Scrapling/pull/488) の変更です。
- **`curl2fetcher()` での curl の User-Agent とプロキシのオプション処理を修正しました**。@SulimanAbdulrazzaq による [#490](https://github.com/D4Vinci/Scrapling/pull/490) の変更です。

- **選択した複数の要素を `Response.markdown()` または CLI の抽出処理で変換すると、Markdown のブロックがつながってしまう問題を修正しました**。@Yigtwxx による [#432](https://github.com/D4Vinci/Scrapling/pull/432) の貢献を含みます。
- **AI 向け出力での非表示コンテンツの除去を修正しました**。`opacity:0.95` のような表示される内容を残し、より多くの非表示スタイルを認識し、非表示のスロットを取り除きます。@Yigtwxx による [#460](https://github.com/D4Vinci/Scrapling/pull/460) の貢献を含みます。
- **タグが入れ子になっている箇所で、不要なタグの除去が途中で止まる問題を修正しました**。@Yigtwxx による [#474](https://github.com/D4Vinci/Scrapling/pull/474) の変更です。
- **同じタグの兄弟要素が複数あるとき、最初の要素に対して生成する CSS と XPath のセレクターを修正しました**。@yellow-dog-dog による [#495](https://github.com/D4Vinci/Scrapling/pull/495) の変更です。
- **lxml の HTML パーサーの非推奨警告を解消しました**。@afsuyadi による [#493](https://github.com/D4Vinci/Scrapling/pull/493) の変更です。

### ドキュメント {#v0.5-docs}

- **Web サイト全体が 10 言語に対応しました**。英語、アラビア語、スペイン語、ブラジルポルトガル語、フランス語、ドイツ語、簡体字中国語、日本語、ロシア語、韓国語で利用できます。ガイド、API リファレンス、チュートリアル、[変更履歴](changelog.md)を翻訳しました。アラビア語の右から左への表示に対応し、言語を切り替えても現在のページとセクションを保持します。
- **ガイド、README の例、セットアップ手順をわかりやすくしました**。チェックポイントのデータ、ブラウザの文字コード、保存した状態、ネットワーク履歴、Shadow DOM、クロール順序について説明しています。
- **Agent Skill と、その例、参考資料、ダウンロード用アーカイブを更新しました**。現在のブラウザと MCP のツールに対応しています。
- **変更履歴を Web サイトに移しました**。各ページの Markdown ソースも参照できるようにしました。

### プロジェクト {#v0.5-project}

- Scrapling のロゴ、カバー画像、Web サイトの見た目を更新しました。
- ブラウザ操作、ダイアログ、抽出、スクリーンショット、JavaScript、ネットワーク記録、状態ファイル、Shadow DOM、クローラーの修正に関するテストを増やしました。
- ブラウザテスト用のマーカーを追加し、ブラウザ、非同期、並列のテストを分けて実行するようにしました。@diegobravtraps-oss による [#457](https://github.com/D4Vinci/Scrapling/pull/457) で、Windows でのチェックポイントと CSV のテストの移植性を改善しました。
- 多言語ドキュメントで共有するビルド設定と、貢献の案内を更新しました。

## [v0.4.15](https://github.com/D4Vinci/Scrapling/releases/tag/v0.4.15) - 2026-08-23 {#v0.4.15}

**今年最大規模のリリースの 1 つです。MCP サーバーを作り直し、1 行で RAG 用の Markdown を生成できるようにしました。Cloudflare チャレンジの解決を改善し、自動操作のためにブラウザタブを開いたままにします 🚀**

!!! warning "警告"

    **このリリースには、MCP サーバーの互換性に影響する変更があります。更新前に[互換性に影響する変更](https://github.com/D4Vinci/Scrapling/blob/v0.4.15/docs/ai/mcp-server.md#breaking-changes)を確認してください。**

### 🚀 新機能と使いやすさの改善 {#v0.4.15-new-stuff-and-quality-of-life-changes}

- **ブラウザタブを開いたままにして、次のリクエストでも再利用するようになりました**（[ドキュメント](fetching/stealthy.md#session-management)を参照）：
    - すべてのブラウザセッションで、リクエスト後もタブを保持します。次のリクエストでは新しいタブを開かず、空いているタブを再利用します。
    - 各リクエストは、割り当てられたタブに自身の設定（タイムアウト、ヘッダー、リソースのブロック）を適用し直します。そのため、別のリクエストの設定が残ることはありません。
    - エラーが発生したタブは閉じて、新しいタブに置き換えます。新しい `close_pages()` メソッドでは、開いているタブをすべて閉じられます。
    - 取得したページは読み込まれたままなので、次のリクエストの `page_setup` 関数は、別のページに移動する前にそのページ上で動作します。これを使って、複数のリクエストにまたがる自動操作をつなげられます。

- **`Response.markdown()` で、どのページも不要な内容を除いた、LLM で使いやすい Markdown に変換できます**（[ドキュメント](ai/building-rag-systems.md)を参照）：

    ```python
    from scrapling.fetchers import Fetcher

    markdown = Fetcher.get("https://example.com").markdown(main_content_only=True)
    ```

    - MCP サーバーと同じ処理で、スクリプト、スタイル、プロンプトインジェクションに使われる隠れた内容を必ず先に取り除きます。
    - 必要な要素だけを変換するには、`css_selector` を渡します。
    - 新しい `rag` オプション依存関係（`pip install "scrapling[rag]"`）で利用できます。`ai`/`shell`/`all` のオプション依存関係にも含まれます。

- **Web サイト全体をクロールし、RAG パイプライン用の Markdown の文書集合を作る `SiteToMarkdownSpider` テンプレートを追加しました**（[ドキュメント](ai/building-rag-systems.md)を参照）：

    ```python
    from scrapling.spiders import SiteToMarkdownSpider

    class DocsSpider(SiteToMarkdownSpider):
        name = "docs"
        start_urls = ["https://example.com/docs/"]
        allowed_domains = {"example.com"}
        output_dir = "docs_markdown"

    result = DocsSpider().start()
    result.items.to_jsonl("docs.jsonl")
    ```

    - ページごとに `url`/`title`/`markdown` を持つアイテムを 1 つ返します。省略可能な `output_dir` を指定すると、ページごとに Markdown ファイルを 1 つ書き出します。
    - `max_pages` でクロールするページ数を制限できます。`CrawlSpider` を継承しているため、`rules()` を上書きすれば、どのリンクをたどるかを自由に制御できます。

- **MCP サーバーを作り直しました（互換性に影響します）**（[互換性に影響する変更](https://github.com/D4Vinci/Scrapling/blob/v0.4.15/docs/ai/mcp-server.md#breaking-changes)と[ドキュメント](ai/mcp-server.md)を参照）：
    - 13 個のツールを 2 つのモードに分けました。単発ツール（`fetch`、`bulk_fetch`、`stealthy_fetch`、`bulk_stealthy_fetch`）は毎回専用のブラウザを起動し、実際の既定値を表示します。セッションツールは、一度開いたセッションを使って動作します。
    - 新しい `session_fetch` ツールは、ブラウザセッションを通じてページを取得します。`open_session` はブラウザ単位の設定だけを持ち、セッションに実際に適用された設定を AI エージェントに返すようになりました。
    - `get` ツールを `make_request` に改名し、すべての HTTP メソッドに対応しました。
    - 新しい `open_request_session` と `session_make_request` ツールにより、AI が永続 HTTP セッションを使えます。リクエスト間で Cookie とブラウザのフィンガープリントを保持します。
    - これにより、取得処理でセッションの設定がリセットされる問題も解消しました。この問題は、最初に @Yigtwxx が [#418](https://github.com/D4Vinci/Scrapling/pull/418) で修正しました。

- **MCP サーバーの HTTP トランスポートは、既定で認証を必須にし、localhost にバインドするようになりました（互換性に影響します）**。@yamantaka-singh による [#414](https://github.com/D4Vinci/Scrapling/pull/414) の変更です（[#413](https://github.com/D4Vinci/Scrapling/issues/413) を修正。[ドキュメント](ai/mcp-server.md#authentication)を参照）：
    - Bearer トークンを必須にするには、`--auth-token`（または環境変数 `SCRAPLING_MCP_AUTH_TOKEN`）を渡します。意図的に認証なしで公開するには、`--no-auth` を渡します。
    - ネットワークからの接続を受け付けるには、`--host 0.0.0.0` を渡します。

### 🐛 バグ修正 {#v0.4.15-bug-fixes}

- **ブラウザのロケールにかかわらず Cloudflare Turnstile/Interstitial を解決できるようになり、ヘッドレスモードで対話型チャレンジが無限ループすることもなくなりました**。ステルスページが解決中にクラッシュする問題も修正しました。@subediparas5 による [#412](https://github.com/D4Vinci/Scrapling/pull/412) の貢献を含みます（[#411](https://github.com/D4Vinci/Scrapling/issues/411) と [#422](https://github.com/D4Vinci/Scrapling/issues/422) を修正）。
- **`find`/`find_all` で `class_` を使うと、複数のクラスを持つ要素を通知なく見落とす問題を修正しました**。@yetval による [#410](https://github.com/D4Vinci/Scrapling/pull/410) の変更です。**空の `class_` 値と、エスケープされていない CSS 文字列の値の問題も修正しました**。@yamantaka-singh による [#417](https://github.com/D4Vinci/Scrapling/pull/417) の変更です。
- **`development_mode` のキャッシュ済みレスポンスを再利用すると、リクエストのメタデータが失われる問題を修正しました**。@Yigtwxx による [#419](https://github.com/D4Vinci/Scrapling/pull/419) の変更です。
- **`retries` が 1 未満の HTTP リクエストが、送信されないまま失敗する問題を修正しました**。@Yigtwxx による [#420](https://github.com/D4Vinci/Scrapling/pull/420) の変更です。

### ドキュメント {#v0.4.15-docs}

- **Web サイトのセクションを整理しました**。新しい「AI と使う」セクションに、MCP サーバー、新しい [Agent Skill](ai/agent-skill.md) ページ、[RAG システムの構築](ai/building-rag-systems.md)ガイドをまとめました。BeautifulSoup からの移行ガイドは「連携と移行」に移し、Scrapy 連携の隣に置きました。
- **[変更履歴](changelog.md)をリポジトリに追加しました**。これまでのすべてのリリースノートを含みます。

## [v0.4.14](https://github.com/D4Vinci/Scrapling/releases/tag/v0.4.14) - 2026-08-10 {#v0.4.14}

**`uv` でのインストールを修正するための、小さなメンテナンスリリースです 🔧**

### 🐛 バグ修正 {#v0.4.14-bug-fixes}

- **`uv` が既定で v0.4.13 のインストールを拒否し、通知なく古いバージョンに戻る問題を修正しました**。前のリリースは `curl_cffi` のプレリリース版を必要としていましたが、`uv` は明示的に有効にしない限り、プレリリース版を許可しません。
すべての依存関係で、安定版を使えるようになりました（[#407](https://github.com/D4Vinci/Scrapling/issues/407) を修正）。

## [v0.4.13](https://github.com/D4Vinci/Scrapling/releases/tag/v0.4.13) - 2026-08-09 {#v0.4.13}

**フィード用 Spider と、より使いやすい MCP サーバーを追加する更新です 🎉**

### 🚀 新機能と使いやすさの改善 {#v0.4.13-new-stuff-and-quality-of-life-changes}

- **フィード用 Spider テンプレートを追加しました**。`XMLFeedSpider` は XML フィード（RSS、Atom、商品フィードなど）のノードを順に処理し、`CSVFeedSpider` は CSV の行を辞書として順に処理します。どちらも gzip 圧縮されたフィードを自動で展開します（[ドキュメント](spiders/generic-templates.md)を参照）。

  ```python
  from scrapling.spiders import XMLFeedSpider

  class RSSSpider(XMLFeedSpider):
      name = "rss"
      start_urls = ["https://example.com/feed.xml"]

      async def parse_node(self, response, node):
          yield {"title": node.findtext("title"), "link": node.findtext("link")}

  result = RSSSpider().start()
  ```

- **MCP サーバーを MCP SDK v2 に更新し、使い方を改善しました**。AI エージェントにツールの効率的な使い方を教える指示を含めました。各ツールがアノテーションを宣言するため、Claude Code などのクライアントは読み取り専用のツールを自動で承認できます。トークンを節約するため、ツールの説明も短くしました。また、サーバーのバージョンとロゴを MCP クライアントに伝えます（[ドキュメント](ai/mcp-server.md)を参照）。
- **`scrapling-mcp` コマンドを追加しました**。`scrapling mcp` に直接対応するため、単一のコマンドを必要とする MCP クライアントやレジストリに、1 行で Scrapling を登録できます。
- **Playwright/Patchright とブラウザのバージョン固定を外しました**。生成するブラウザの User-Agent は、インストール済みの Playwright/Patchright が実際に操作する Chromium のバージョンと常に一致します。そのため、Scrapling 側でバージョンを固定する必要がなくなり、自由に更新できます。更新後は `scrapling install --force` を実行して、ブラウザを更新してください。

### 🐛 バグ修正 {#v0.4.13-bug-fixes}

- **フィンガープリントのデータパッケージがブラウザのバージョンより古いときに、Scrapling のインポートが `browserforge` の ValueError でクラッシュする問題を修正しました**（[#394](https://github.com/D4Vinci/Scrapling/issues/394)、[#396](https://github.com/D4Vinci/Scrapling/issues/396)、[#400](https://github.com/D4Vinci/Scrapling/issues/400) を修正）。
- **MCP の一括ブラウザツールで、ページプールのサイズが正しく設定されない問題を修正しました**。この問題により、`bulk_fetch` は 50 個を超える URL を一括取得すると失敗し、`bulk_stealthy_fetch` はすべての URL を 1 つのタブで取得していました。@Yigtwxx による [#393](https://github.com/D4Vinci/Scrapling/pull/393) の変更です。

### プロジェクト {#v0.4.13-project}

- **[AI による貢献の方針](https://github.com/D4Vinci/Scrapling/blob/main/AI_POLICY.md)を追加しました**。AI を使った貢献は歓迎しますが、PR または Issue でその使用を明記する必要があります。AI の使用を明記せずに生成内容を提出したと判断されるものには、ラベルを付けてクローズします。

## [v0.4.12](https://github.com/D4Vinci/Scrapling/releases/tag/v0.4.12) - 2026-07-26 {#v0.4.12}

**Spider がクロール先の Web サイトに合わせて、より適切に動作できるようにするリリースです**

### 🚀 新機能と使いやすさの改善 {#v0.4.12-new-stuff-and-quality-of-life-changes}

- **Spider が AutoThrottle で速度を自動調整できるようになりました。** 遅すぎたり、アクセスを拒否されたりする `download_delay` を推測する必要はありません。Spider が各 Web サイトの応答速度を測り、ドメインごとに待機時間を調整します。Web サイトがアクセスを拒否したり、リクエスト数を制限したりすると、待機時間を 2 倍にするか、`Retry-After` ヘッダーで指定された時間だけ待ちます。制限がなくなったら、再び速度を上げます。設定した `download_delay` と robots.txt の `Crawl-delay` は、引き続き待機時間の下限として守られます（[ドキュメント](spiders/advanced.md#autothrottle)を参照）。

    ```python
    class MySpider(Spider):
        name = "adaptive"
        start_urls = ["https://example.com"]
        autothrottle_enabled = True
        autothrottle_start_delay = 2.0
        autothrottle_max_delay = 30.0
        autothrottle_block_backoff = True
    ```

- **結果を CSV と XML に書き出せるようになりました**。従来の JSON/JSONL への書き出しも使えます。アイテムごとにキーが異なっていても、内容を失わずに書き出します。入れ子の値は JSON として書き込みます（[ドキュメント](spiders/getting-started.md)を参照）。

    ```python
    result = MySpider().start()
    result.items.to_csv("products.csv")
    result.items.to_xml("products.xml")
    ```

- **MCP サーバーで認証を必須にできるようになりました**。自分の端末だけで使うのではなく、安全に外部に公開できます。トークンのないリクエストは拒否します。サーバーが応答するホスト名も制限できます（[ドキュメント](ai/mcp-server.md)を参照）。

    ```bash
    scrapling mcp --http --auth-token "$(openssl rand -hex 32)"
    ```

- **ブラウザで HTTP 形式の CDP URL を使えるようになりました**。WebSocket 形式だけに限りません。ブラウザサービスが提供する `wss://` エンドポイントに加え、`--remote-debugging-port=9222` で自分で起動した Chrome にも、ブラウザ Fetcher や MCP セッションを接続できます。

- **公開する Docker イメージに、リリースのバージョンタグを付けるようになりました**。`latest` だけでなく、使いたいバージョンを正確に指定できます。@JanRK による [#384](https://github.com/D4Vinci/Scrapling/pull/384) の変更です。

### 🐛 バグ修正 {#v0.4.12-bug-fixes}

- **ブラウザエンジンのレスポンスをキャッシュすると、すべての Cookie が失われる問題を修正しました**。Spider の開発モードでは、Cookie に依存するセッションや認証の処理が通知なく動かなくなる原因になっていました。@amitvijapur による [#379](https://github.com/D4Vinci/Scrapling/pull/379) の変更です（[#376](https://github.com/D4Vinci/Scrapling/issues/376) を修正）。

- **`StealthyFetcher` が、システム設定に従わずにすべてのブラウザに `en-US` ロケールを強制する問題を修正しました**。ロケールと IP アドレスの不一致により、Web サイトから疑わしいアクセスと見なされ、Google が 429 を返すなどの問題がありました（[#381](https://github.com/D4Vinci/Scrapling/issues/381) を修正）。

- **ストレージシステムの誤解を招くエラーメッセージを修正しました**。挿入後に残っていた不要な呼び出しも削除しました。@fix2015 による [#377](https://github.com/D4Vinci/Scrapling/pull/377) の変更です。

### パフォーマンス {#v0.4.12-performance}

- **`get_all_text()` の処理時間が、ノード数に比例する O(nodes) になりました**。各テキストノードの祖先を毎回たどらなくなったため、深く入れ子になったページでは約 5-6 倍の速度になります。@yetval による [#378](https://github.com/D4Vinci/Scrapling/pull/378) の変更です。

## [v0.4.11](https://github.com/D4Vinci/Scrapling/releases/tag/v0.4.11) - 2026-07-12 {#v0.4.11}

**初のプラットフォーム別 Spider テンプレート、より速いパーサー、重要な修正を含む更新です 🎉**

### 🚀 新機能と使いやすさの改善 {#v0.4.11-new-stuff-and-quality-of-life-changes}

- **初のプラットフォーム別 Spider テンプレート、`ShopifySpider` を追加しました！** Shopify ストアの JSON API から、すべての商品を抽出できます。Web サイトの HTML を扱う必要はありません。このクラスを継承し、ストアのドメインを設定するだけで使えます（[ドキュメント](spiders/platform-templates.md)を参照）。

  ```python
  from scrapling.spiders import ShopifySpider

  class MyStore(ShopifySpider):
      target_website = "example.com"

  result = MyStore().start()
  ```

- **CLI のブラウザコマンドに `--executable-path` を追加しました**。`scrapling extract fetch` と `scrapling extract stealthy-fetch` の両方で、任意の Chromium 互換ブラウザの実行ファイルを指定できます。このオプションがない場合は、環境変数 `SCRAPLING_EXECUTABLE_PATH` を使います。これにより、MCP サーバーと同じ機能を使えます（[#371](https://github.com/D4Vinci/Scrapling/issues/371) を解決）。

  ```bash
  scrapling extract fetch "https://example.com" page.html --executable-path "/path/to/chromium"
  ```

### 🤖 使いやすさの改善 {#v0.4.11-quality-of-life-changes}
- **`find_by_text` と `find_by_regex` の速度が最大で約 2 倍になりました**。`first_match` が有効な場合（既定）、必要になった要素だけをオブジェクトに変換することで、最初の一致が見つかった時点で検索を終了します。@yetval による [#370](https://github.com/D4Vinci/Scrapling/pull/370) の変更です。
- **すべてのライブラリの最新版と比較した、新しいベンチマーク結果に更新しました。**
- **貢献ルールを更新しました。**

### 🐛 バグ修正 {#v0.4.11-bug-fixes}

- **制御文字を含むページで、MCP サーバーの取得ツールがクラッシュする問題を修正しました**。`All strings must be XML compatible` エラーが発生していました。@yetval による [#368](https://github.com/D4Vinci/Scrapling/pull/368) の変更です（[#366](https://github.com/D4Vinci/Scrapling/issues/366) を修正）。

## [v0.4.10](https://github.com/D4Vinci/Scrapling/releases/tag/v0.4.10) - 2026-07-04 {#v0.4.10}

**新しい Scrapy 連携と、コミュニティから寄せられた修正を含む更新です 🎉**

### 🚀 新機能と使いやすさの改善 {#v0.4.10-new-stuff-and-quality-of-life-changes}

- **Scrapy 連携を追加しました**。既存の Scrapy プロジェクトを書き直さずに、Scrapling の解析 API を使えます。Spider のコールバックに `scrapling_response` デコレーターを付けると、受け取るレスポンスが Scrapling の `Response` になります。クロールは引き続き Scrapy が担当します（[ドキュメント](integrations/scrapy.md)を参照）：

    ```python
    import scrapy
    from scrapling.integrations.scrapy import scrapling_response

    class QuotesSpider(scrapy.Spider):
        name = "quotes"
        start_urls = ["https://quotes.toscrape.com"]

        @scrapling_response
        def parse(self, response):  # `response` is now a Scrapling Response
            first_quote = response.find_by_text("The world as we have created it", partial=True)
            for quote in [first_quote, *first_quote.find_similar()]:
                yield {"text": quote.get_all_text(strip=True)}
    ```

- **MCP サーバーのすべてのブラウザツールで、任意の Chromium 互換ブラウザを使えるようになりました**。`scrapling mcp --executable-path "/path/to/chromium"` または環境変数 `SCRAPLING_EXECUTABLE_PATH` で共通の設定を行えます。`executable_path` 引数でリクエストごとに指定することもできます。@samrusani による [#360](https://github.com/D4Vinci/Scrapling/pull/360) の変更です（[#347](https://github.com/D4Vinci/Scrapling/issues/347) を解決）。
- **すべてのブラウザとフィンガープリントを更新しました**。更新後に `scrapling install --force` を実行して、反映してください。

### 🐛 バグ修正 {#v0.4.10-bug-fixes}

- **UTF-8 以外の Web サイトで、ブラウザ Fetcher が文字化けしたテキストを返す問題を修正しました**。@yehudalevy-collab による [#365](https://github.com/D4Vinci/Scrapling/pull/365) の変更です（[#364](https://github.com/D4Vinci/Scrapling/issues/364) を修正）。
- **`LinkExtractor` が `.tar.gz` などの複合拡張子を除外できない問題を修正しました**。@renbkna による [#359](https://github.com/D4Vinci/Scrapling/pull/359) の変更です（[#349](https://github.com/D4Vinci/Scrapling/issues/349) を修正）。
- **クロールを一時停止すると、実行中のリクエストがチェックポイントから失われる問題を修正しました。再開後にそれらのリクエストが飛ばされることはなくなりました**。@yetval による [#358](https://github.com/D4Vinci/Scrapling/pull/358) の変更です。
- **Spider が robots.txt の `Request-rate` 指示から誤った待機時間を計算する問題を、Protego の更新により修正しました**。@Disaster-Terminator が [#355](https://github.com/D4Vinci/Scrapling/pull/355) でテストを合わせて修正しました。

### ドキュメント {#v0.4.10-docs}

- **ステルスモードで `init_script` が Patchright の分離された実行環境とどう関わるかを明確にしました**。@mturac による [#353](https://github.com/D4Vinci/Scrapling/pull/353) の変更です（[#350](https://github.com/D4Vinci/Scrapling/issues/350) を解決）。
- **Agent Skill を [skills.sh](https://skills.sh/D4Vinci/Scrapling) からインストールする方法を追加しました**。@ob-aion による [#363](https://github.com/D4Vinci/Scrapling/pull/363) の変更です。

## [v0.4.9](https://github.com/D4Vinci/Scrapling/releases/tag/v0.4.9) - 2026-06-07 {#v0.4.9}

**コミュニティから報告された多くの問題を修正するメンテナンス更新です 🛠️**

### 🚀 新機能と使いやすさの改善 {#v0.4.9-new-stuff-and-quality-of-life-changes}

- **すべてのブラウザとフィンガープリントを更新しました**。更新後に `scrapling install --force` を実行して、反映してください。
- **CLI に `--version` フラグを追加しました**。@ETM-Code による [#303](https://github.com/D4Vinci/Scrapling/pull/303) の変更です（[#299](https://github.com/D4Vinci/Scrapling/issues/299) を解決）。

### 🐛 バグ修正 {#v0.4.9-bug-fixes}

- **HTTP セッションで、セッション単位の `proxy` 引数が通知なく無視される問題を修正しました**。この問題は実際の IP アドレスを漏らす可能性がありました（[#295](https://github.com/D4Vinci/Scrapling/issues/295) を解決）。セッション単位の `proxy` とリクエスト単位の `proxies`（またはその逆）を混在させると、一方を通知なく無視する代わりにエラーを出すようになりました。
- **`init_script` と `user_data_dir` を併用すると、ブラウザのページ移動が失敗する問題を修正しました**（[#294](https://github.com/D4Vinci/Scrapling/issues/294) を解決）。
- **Web サイトが `Content-Type` ヘッダーの charset 値を引用符で囲むと、文字コードを正しく検出できない問題を修正しました**。@Bortlesboat による [#323](https://github.com/D4Vinci/Scrapling/pull/323) の変更です。
- **適応型の要素再検索で `IndexError` が発生する問題を修正しました。`auto_save` が有効なときに発生していました**。@Mubashirrrr による [#340](https://github.com/D4Vinci/Scrapling/pull/340) の変更です。
- **Windows で Spider のチェックポイントとキャッシュの保存がクラッシュする問題を修正しました**。@MrStarkEG による [#344](https://github.com/D4Vinci/Scrapling/pull/344) の変更です。
- **属性の数が異なる要素に対し、`find_similar` が誤った類似度を計算する問題を修正しました**（[#322](https://github.com/D4Vinci/Scrapling/issues/322) を解決）。

### ドキュメント {#v0.4.9-docs}

- **既定のインストールにはパーサーエンジンだけが含まれることを明確にしました**。Fetcher と Spider にはオプション依存関係が必要です（[#343](https://github.com/D4Vinci/Scrapling/issues/343) を解決）。
- **残っていた例の Docker イメージ名を修正しました**。@evanclan による [#315](https://github.com/D4Vinci/Scrapling/pull/315) の変更です。
- **貢献ガイドのリンク切れを修正しました**。@Bortlesboat による [#320](https://github.com/D4Vinci/Scrapling/pull/320) の変更です。

## [v0.4.8](https://github.com/D4Vinci/Scrapling/releases/tag/v0.4.8) - 2026-05-11 {#v0.4.8}

**クロールフレームワークをさらに使いやすくする、Spider の大きな更新です 🕷️**

### 🚀 新機能と使いやすさの改善 {#v0.4.8-new-stuff-and-quality-of-life-changes}

- **`LinkExtractor` ユーティリティを追加しました**。`scrapling.spiders.LinkExtractor` から使い、`Response` から URL を抽出できます。多くの制御オプションがあります（[ドキュメント](spiders/generic-templates.md)を参照）。

    ```python
    from scrapling.spiders import LinkExtractor

    extractor = LinkExtractor(allow=r"/posts/", deny_domains=["ads.example.com"])
    ```

- **汎用 Spider テンプレートの `CrawlSpider` と `CrawlRule` を追加しました**。「このパターンに一致するリンクをたどる」といった定型コードを毎回書く必要がなくなります。`rules()` を上書きして `CrawlRule` オブジェクトのリストを返し、それぞれに `LinkExtractor` を組み合わせます（[ドキュメント](spiders/generic-templates.md)を参照）。

    ```python
    from scrapling.spiders import CrawlSpider, CrawlRule, LinkExtractor

    class QuotesSpider(CrawlSpider):
        name = "blog"
        start_urls = ["https://quotes.toscrape.com/"]

        def rules(self):
            return [
                CrawlRule(LinkExtractor(allow=r"/author/"), callback=self.parse_author),
                CrawlRule(LinkExtractor(allow=r"/page/\d+/")),  # pagination, no callback
            ]

        async def parse_author(self, response):
            yield {
                "name": response.css(".author-title::text").get(),
                "birthday": response.css(".author-born-date::text").get(),
                "url": response.url,
            }
    ```

- **`SitemapSpider` テンプレートを追加しました**。サイトマップや `robots.txt` の URL から直接クロールを開始できます。gzip 圧縮のサイトマップに対応し、多くの制御オプションを備えています。上の **CrawlSpider** の例と同じように、クロールルールで URL の処理先を決めます（[ドキュメント](spiders/generic-templates.md)を参照）。

    ```python
    from scrapling.spiders import SitemapSpider, CrawlRule, LinkExtractor

    class NewsSitemap(SitemapSpider):
        name = "news"
        sitemap_urls = ["https://example.com/robots.txt"]

        def rules(self):
            return [
                CrawlRule(LinkExtractor(allow=r"/articles/"), callback=self.parse_article),
            ]

        async def parse_article(self, response):
            yield {"url": response.url, "title": response.css("h1::text").get()}
    ```

- **適応型の要素再検索で、すべてのメソッドの類似度のしきい値を既定で 40% にしました**。以前の既定値は `0` でした。これにより、適応型機能がより適切に動作します。しきい値を超える要素がない場合は、見つかった最高スコアを警告で伝えるため、必要に応じて `percentage` を意図的に下げられます。

- **すべてのブラウザとフィンガープリントを更新しました**。更新後に `scrapling install  --force` を再実行して、ブラウザとフィンガープリントを更新してください。

### 🐛 バグ修正 {#v0.4.8-bug-fixes}

- **`Fetcher.configure(...)` が個別のリクエスト呼び出しに適用されない問題を修正しました**。`AsyncFetcher` にも同じ修正を適用しました。
- **リクエストのフィンガープリントの計算ミスにより、Spider が重複したリクエストを送る問題を修正しました**。@yetval による [#255](https://github.com/D4Vinci/Scrapling/pull/255) の変更です。
- **適応型スクレイピングエンジンが、類似度の低い一致を通知しない問題を修正しました。** 上のしきい値変更と合わせて、要素の再検索が失敗した場合は、誤解を招く「最も近そうな」要素を返す代わりに警告を出します。

### ドキュメント {#v0.4.8-docs}

- **ドキュメント全体の古いコード例を更新しました**。現在のバージョンに合わせています。
- **ドキュメントサイトでコードをコピーして貼り付けやすくしました**。Agent Skill も整理し、呼び出すたびに使うトークンを減らしました。

## [v0.4.7](https://github.com/D4Vinci/Scrapling/releases/tag/v0.4.7) - 2026-04-17 {#v0.4.7}

**AI エージェントがページを見られるようにする更新です 📸**

### 🚀 新機能と使いやすさの改善 {#v0.4.7-new-stuff-and-quality-of-life-changes}

- **MCP ツール `screenshot` を追加しました**。ページを撮影し、MCP の実際の `ImageContent` ブロックとして返すため、モデルが画像を直接見られます。ブラウザセッションを開いておく必要があります。先に `open_session` を呼び出し（`dynamic` または `stealthy`）、その `session_id` をここに渡してください。PNG と JPEG、ページ全体の撮影、JPEG の品質指定、通常の待機オプション（`wait`、`wait_selector`、`network_idle`、`timeout`）に対応しています（[#244](https://github.com/D4Vinci/Scrapling/issues/244) を実装）。
- **任意の名前を指定する `session_id` パラメーターを `open_session` に追加しました**。既定のランダムな 12 桁の 16 進文字列の代わりに、意味のある名前（`"search"`、`"checkout"`）を付けられます。@hauntedhost による [#243](https://github.com/D4Vinci/Scrapling/pull/243) の変更です。

### 🐛 バグ修正 {#v0.4.7-bug-fixes}

- **`FetcherSession` の状態が壊れる問題と、遅延初期化するセッションを閉じるとクラッシュする問題を修正しました**。@yetval による [#245](https://github.com/D4Vinci/Scrapling/pull/245) の変更です。
- **`TypeError: Session.request() got an unexpected keyword argument 'block_ads'` を修正しました**。CLI の `--ai-targeted` フラグを HTTP コマンドで使うと発生していました。@voidborne-d による [#249](https://github.com/D4Vinci/Scrapling/pull/249) の変更です（[#247](https://github.com/D4Vinci/Scrapling/issues/247) を修正）。

### 翻訳 {#v0.4.7-translations}

- **ブラジルポルトガル語の README 翻訳を追加しました**。@rgomids による [#250](https://github.com/D4Vinci/Scrapling/pull/250) の貢献です。

## [v0.4.6](https://github.com/D4Vinci/Scrapling/releases/tag/v0.4.6) - 2026-04-13 {#v0.4.6}

**ブラウザのステルス機能、プライバシー、開発のしやすさを改善する更新です 🔒**

### 🚀 新機能と使いやすさの改善 {#v0.4.6-new-stuff-and-quality-of-life-changes}

- **ブラウザ Fetcher に広告ブロックを組み込みました**。`block_ads=True` を渡すと、約 3,500 個の既知の広告・トラッキングドメインへのリクエストをルートのインターセプト段階で止めます。DNS 問い合わせも TCP 接続も行わず、すぐに中止します。`blocked_domains` と組み合わせて、独自のリストも使えます。MCP サーバーと CLI の `--ai-targeted` モードでは自動で有効になり、トークンを節約し、ページの読み込みを速くします。

    ```python
    page = StealthyFetcher.fetch('https://example.com', block_ads=True)
    ```

- **DNS-over-HTTPS に対応しました**。プロキシ使用時の DNS 漏えいを防ぎます。`dns_over_https=True` を渡すと、Cloudflare の DoH を使って DNS 問い合わせを送ります。HTTP 通信がプロキシを通っていても、DNS の名前解決から実際の場所が漏れる問題を防げます。

    ```python
    page = StealthyFetcher.fetch('https://example.com', proxy='http://proxy:8080', dns_over_https=True)
    ```

- **ブラウザ Fetcher に `page_setup` コールバックを追加しました**。`page.goto()` の前に実行する関数です。ページ移動前に必要なイベントリスナー、ルート、スクリプトを登録できます。ページ移動後に動作する `page_action` と組み合わせて使えます（[#237](https://github.com/D4Vinci/Scrapling/issues/237) を解決）。

    ```python
    def capture_websockets(page):
        page.on("websocket", lambda ws: print(f"WS: {ws.url}"))

    page = DynamicFetcher.fetch('https://example.com', page_setup=capture_websockets)
    ```

- **CLI オプション `--block-ads` と `--dns-over-https` を追加しました**。`fetch` と `stealthy-fetch` の両方のコマンドで使えます。

### 🐛 バグ修正 {#v0.4.6-bug-fixes}

- **`Seconds` 型エイリアスが浮動小数点数を受け付けない問題を修正しました**。ブラウザ Fetcher に `wait=1.5` や `timeout=500.0` を渡すと、型エラーになっていました。型エイリアスが `float` を型ではなくメタデータとして扱っていたことが原因です。@kuishou68 による [#240](https://github.com/D4Vinci/Scrapling/pull/240) の変更です。
- **フルパスのセレクター生成で ID 部分が重複する問題を修正しました**。CSS/XPath のフルパスを生成するとき、`id` 属性を持つ要素のセレクターが 2 回追加され、`body > #main > #main > #target > #target` のようになっていました。XPath のフルパスで、`[@id='x']` だけの条件式（無効な XPath）が出力される問題も修正し、`*[@id='x']` を出力するようにしました。@sjhddh による [#241](https://github.com/D4Vinci/Scrapling/pull/241) の変更です。
- **シェルの関数シグネチャに不足していたパラメーターを追加しました**。対話型シェルの関数シグネチャには、`blocked_domains`、`block_ads`、`retries`、`retry_delay`、`capture_xhr`、`executable_path`、`dns_over_https` が含まれていませんでした。

## [v0.4.5](https://github.com/D4Vinci/Scrapling/releases/tag/v0.4.5) - 2026-04-07 {#v0.4.5}

**Spider 開発者に便利な大きな新機能と、いくつかの重要な修正を含む更新です 🎉**

### 🚀 新機能と使いやすさの改善 {#v0.4.5-new-stuff-and-quality-of-life-changes}

- **Spider の開発モード**：以前は Spider の `parse()` 処理を調整するたびに、対象サーバーに再アクセスする必要がありました。遅いうえに不要な通信が増え、セレクターを調整している間にリクエスト数を制限されることもありました。新しい開発モードでは、最初の実行時にすべてのレスポンスをディスクにキャッシュし、以降はディスクから再利用します。コールバックを何度調整して実行しても、ネットワークリクエストは発生しません。クラス属性を 1 つ設定するだけで有効にできます：

    ```python
    class MySpider(Spider):
        name = "my_spider"
        start_urls = ["https://example.com"]
        development_mode = True

        async def parse(self, response):
            yield {"title": response.css("title::text").get("")}
    ```

    キャッシュの既定の保存先は `.scrapling_cache/{spider.name}/` です。`development_cache_dir` で別の場所に変更できます。新しい統計カウンター `cache_hits` と `cache_misses` で、キャッシュの利用状況を確認できます。キャッシュの再利用では、`download_delay`、リクエスト数の制限、ブロックされたリクエストの再試行を省くため、ディスクの速度で繰り返し試せます。`development_mode = True` のまま Spider を本番で使わないでください。これは開発用の機能で、本番用のキャッシュではありません。詳しくは[ドキュメント](spiders/advanced.md#development-mode)を参照してください。

- **リダイレクトの既定の動作をより安全にしました**。すべての HTTP Fetcher、MCP サーバー、シェルで、`follow_redirects` の既定値は `"safe"` になりました。リダイレクトは引き続きたどりますが、内部・プライベート IP（ループバック、プライベートネットワーク、リンクローカル）への移動は拒否します。これにより、ユーザーが指定した URL をスクレイピングするときに SSRF を防げます。以前の動作に戻すには `follow_redirects="all"` を渡します。リダイレクトを完全に無効にするには `False` を渡します。

### 🐛 バグ修正 {#v0.4.5-bug-fixes}

- **強制停止でチェックポイントが失われることはなくなりました**。`crawldir` を有効にした Spider で Ctrl+C を 2 回押す（強制停止する）と、チェックポイントの書き込みと競合することがありました。pickle の書き込みが終わる前にキャンセルスコープがタスクを終了し、`paused=False` のままになるため、前のチェックポイントを*削除する*後片付けの処理が動いていました。その結果、長いクロールを強制停止すると、保存したかった進捗をすべて失う可能性がありました。現在のエンジンは、**チェックポイントを書き込んでから** `cancel_scope.cancel()` を呼び出すため、強制停止しても最新の未処理の状態を必ず保持します。@voidborne-d による [#230](https://github.com/D4Vinci/Scrapling/pull/230) の変更です。

## [v0.4.4](https://github.com/D4Vinci/Scrapling/releases/tag/v0.4.4) - 2026-04-05 {#v0.4.4}

**Spider の重要な改善とバグ修正を含む更新です 🎉**

### 🚀 新機能と使いやすさの改善 {#v0.4.4-new-stuff-and-quality-of-life-changes}
- **Spider フレームワークで robots.txt のルールに従えるようにしました**。新しい `robots_txt_obey` オプションで有効にします。Spider はクロール前に robots.txt を自動で取得し、`Disallow`、`Crawl-delay`、`Request-rate` などの指示を守ります。robots.txt は並行して取得し、クロールが終わるまでドメインごとにキャッシュします。@AbdullahY36 による [#226](https://github.com/D4Vinci/Scrapling/pull/226) の変更です。
- **robots.txt のキャッシュを事前に準備する機能を追加しました**。クロールループが始まる前に、start_urls のすべてのドメインの robots.txt を取得して解析します。各ドメインへの最初のリクエストで待つ必要がなくなります。
- **統計値 `robots_disallowed_count` を追加しました**。`CrawlStats` で、クロール中に robots.txt のルールでブロックされたリクエスト数を記録します。

Web サイトの説明は[こちら](spiders/getting-started.md#robotstxt-compliance)を参照してください。

### 🐛 バグ修正 {#v0.4.4-bug-fixes}
- **`ProxyRotator` の重大な MRO の問題を修正しました**。仮のメソッド `_build_context_with_proxy` が子クラスの実装を隠していたため、プロキシのローテーションで必ず `NotImplementedError` が発生していました（[#215](https://github.com/D4Vinci/Scrapling/issues/215) を修正）。@yetval に感謝します。
- **ブラウザセッションでリクエストごとにプロキシを切り替えると、ページプールに不要な参照が残る問題を修正しました**。一時的なコンテキスト内で作成したページが後片付けでプールから削除されず、無効な参照が蓄積していました。@yetval による [#223](https://github.com/D4Vinci/Scrapling/pull/223) の変更です。
- **静的 Fetcher で不足していた型のアサーションを追加しました**。`curl_cffi` が `None` を `session.request()` から返す場合があり、後続の処理でエラーになっていました。

### その他 {#v0.4.4-other}
- 依存関係を更新しました。最新のフィンガープリントなどを利用できます。
- robots.txt の解析用に、`protego` をオプション依存関係グループ `fetchers` に追加しました。

## [v0.4.3](https://github.com/D4Vinci/Scrapling/releases/tag/v0.4.3) - 2026-03-30 {#v0.4.3}

**多くの重要な変更を含む更新です 🎉**

### 🚀 新機能と使いやすさの改善 {#v0.4.3-new-stuff-and-quality-of-life-changes}
- **新しい MCP ツールを追加しました**。通常モードまたはステルスモードのブラウザを開いたままにして、ほかのツールから引き続き使えます。ブラウザを閉じるツールも追加しました（[例](https://github.com/D4Vinci/Scrapling/blob/v0.4.3/docs/ai/mcp-server.md#examples)）。
- **新しい MCP ツールを追加しました**。既存のブラウザセッションをすべて一覧表示します。新しいツール群と組み合わせて使います。
- **ブラウザセッションに新しいオプションを追加しました**。リクエスト中に発生したすべてのバックグラウンドリクエストを自動で収集します（[#159](https://github.com/D4Vinci/Scrapling/pull/159) を解決）[[例](https://github.com/D4Vinci/Scrapling/blob/v0.4.3/docs/fetching/dynamic.md#capturing-xhrfetch-requests)]。
- **新しいサニタイザーを追加しました**。隠れた内容や見えない内容を取り除き、一般的なプロンプトインジェクション攻撃から MCP サーバーを守ります。
- **Web スクレイピングコマンドに新しいコマンドラインオプションを追加しました**。`--ai-targeted` を使うと、MCP サーバーと同様に、AI 向けの内容に整え、一般的なプロンプトインジェクション攻撃を防げます。
- **ブラウザセッションに新しいオプションを追加しました**。`executable_path` で、任意のブラウザのパスを指定できます（[#202](https://github.com/D4Vinci/Scrapling/pull/202) を解決）。
- MCP サーバーのコードを**整理し直しました**。保守しやすくし、すべてのツールを非同期に統一しました。
- CLI コマンドのコードを**整理し直しました**。保守しやすくし、210 行削減しました。

### 🐛 バグ修正 {#v0.4.3-bug-fixes}
- Spider のセッションで再試行するときも HTTP メソッドを保持するように修正しました。@karesansui-u による [#201](https://github.com/D4Vinci/Scrapling/pull/201) の変更です。
- ページ内容の取得に再試行回数の上限を設け、無限ループを防ぎました。@haosenwang1018 と @D4Vinci による [#197](https://github.com/D4Vinci/Scrapling/pull/197) の変更です。
- 引数のない `raise` を `return False` に置き換えました。対象は `_restore_from_checkpoint` です。@haosenwang1018 による [#196](https://github.com/D4Vinci/Scrapling/pull/196) の変更です。
- `get_all` を `getall` に置き換え、`Texthandler` を Selector クラスに合わせました。

### カバレッジとテストの改善 {#v0.4.3-coverage-tests-improvement}
- `_normalize_credentials` の境界条件を確認するテストを追加しました。@Bortlesboat による [#192](https://github.com/D4Vinci/Scrapling/pull/192) の変更です。
- 保存したデータを同じ内容で取得できることを確認するテストと、コアストレージのカバレッジを増やすテストを追加しました。@haosenwang1018 による [#193](https://github.com/D4Vinci/Scrapling/pull/193) の変更です。
- `TextHandler` の正規表現を使う処理と `TextHandlers.re()` を確認するテストを追加しました。@haosenwang1018 による [#194](https://github.com/D4Vinci/Scrapling/pull/194) の変更です。
- `filter`、`iterancestors`、`find_similar` の境界条件を確認するテストを追加しました。@awanawana による [#200](https://github.com/D4Vinci/Scrapling/pull/200) の変更です。

### Agent Skill の改善 {#v0.4.3-agent-skill-improvement}
- Skill のリファレンス内の Markdown リンク切れを修正しました。@yetval による [#204](https://github.com/D4Vinci/Scrapling/pull/204) の変更です。
- [Clawhub](https://clawhub.ai/d4vinci/scrapling-official) の検証に通りやすいよう、Skill の構成を改善しました。
- Skill がコマンドラインでスクレイピングするときは、`--ai-targeted` オプションを必ず使うようにしました。

### ドキュメントの改善 {#v0.4.3-docs-improvement}
- 韓国語の README 翻訳を追加しました。@greatsk55 による [#187](https://github.com/D4Vinci/Scrapling/pull/187) の貢献です。
- 中国語と日本語の README で、CJK 文字とラテン文字の間の空白を修正しました。
- 以前の Web サイトのデザインから残っていたリンク切れを修正しました。

## [v0.4.2](https://github.com/D4Vinci/Scrapling/releases/tag/v0.4.2) - 2026-03-08 {#v0.4.2}

**重要な変更を含むメンテナンス更新です**

#### バグ修正 {#v0.4.2-bug-fixes}
- `get_all_text()` 関数が、要素の終了タグの後にあるテキストノードも取得するようになりました。これにより、MCP サーバーやコマンドで、以前は見落としていたテキストを読めます（[#168](https://github.com/D4Vinci/Scrapling/pull/168)）。@mhillebrand に感謝します。
- Referer に使う URL を、Google の検索 URL から Google のトップページの URL に変更しました。以前の処理は正しくなく、フィンガープリントによる識別の手がかりになっていた可能性があります（[#179](https://github.com/D4Vinci/Scrapling/pull/179)）。@Bortlesboat に感謝します。
- すべてのブラウザで、追加の起動フラグを結合する処理の問題を修正しました。@rostchri に感謝します。
- 3.12 より前の Python でクラッシュを起こしていた型ヒントの問題を修正しました（[#163](https://github.com/D4Vinci/Scrapling/issues/163) を解決）。

#### その他 {#v0.4.2-other}
- Claude Code / OpenClaw などの AI エージェントツール向けに Agent Skill を追加しました。
- Agent Skill を Clawhub に追加しました。
- すべてのブラウザと Playwright を最新バージョンに更新しました。
- メインの README ファイルにフランス語の翻訳を追加しました。

## [v0.4.1](https://github.com/D4Vinci/Scrapling/releases/tag/v0.4.1) - 2026-02-27 {#v0.4.1}

**多くの重要な変更を含む更新です**

### 🚀 新機能と使いやすさの改善 {#v0.4.1-new-stuff-and-quality-of-life-changes}
- Cloudflare のチャレンジ検出に使う**正規表現の精度を改善しました**（@Rinz27 に感謝します。[#133](https://github.com/D4Vinci/Scrapling/pull/133)）。
- Cloudflare のチャレンジ処理の**速度と効率を改善しました**。速度はほぼ以前の倍になりました。
- サイト本体に移動する前に Cloudflare のページを二度表示するサイトにも対応するよう、**Cloudflare のチャレンジ処理を改善しました**。
- 注入していた JS ファイルを削除し、**ステルスブラウザのステルス性と速度を改善しました**。
- OpenCode で使えるように **MCP スキーマを改善しました**（@robin-ede に感謝します。[#137](https://github.com/D4Vinci/Scrapling/pull/137)）。
- VS Code Copilot などの厳密なツールでも使えるよう、**MCP スキーマの互換性をさらに改善しました**（#150 を解決）。
- `main_content_only` が有効なときに不要な HTML タグを削除することで、**MCP サーバーのトークン使用量を大幅に減らしました**。
- PyPI ページを修正し、MCP サーバーレジストリへの登録に必要なファイルを追加しました。
- コマンドラインの代わりにコードからブラウザの依存関係をインストールする例を追加し、自動化しやすくしました。
- すべてのワークフローで actions を最新バージョンに更新しました（@salmanmkc に感謝します。[#143](https://github.com/D4Vinci/Scrapling/pull/143)/[#144](https://github.com/D4Vinci/Scrapling/pull/144)）。

## [v0.4](https://github.com/D4Vinci/Scrapling/releases/tag/v0.4) - 2026-02-15 {#v0.4}

**Scrapling でこれまで最大のリリースです。Spider フレームワーク、プロキシの切り替え、パーサーの大幅な改善を導入しました**

このリリースでは、完全に非同期のクローリングフレームワーク、賢いプロキシ管理、重要な API の変更を導入しました。Scrapling の機能と一貫性が向上しています。更新前に、互換性に影響する変更の節をよく確認してください。

### 🕷️ Spider フレームワーク {#v0.4-spider-framework}

`anyio` を基にした新しい非同期クローリングフレームワークです。大規模なスクレイピングを整理して実行できます。

```python
from scrapling.spiders import Spider, Response

class MySpider(Spider):
  name = "demo"
  start_urls = ["https://example.com/"]

  async def parse(self, response: Response):
      for item in response.css('.product'):
          yield {"title": item.css('h2::text').get()}

MySpider().start()
```

-  **Scrapy に似た Spider API**：`start_urls`、非同期の `parse` コールバック、`Request`/`Response` オブジェクト、優先度付きキューを使って Spider を定義できます。
- **並行クローリング**：同時実行数の上限、ドメインごとの速度制限、ダウンロード間隔を設定できます。
- **複数セッションへの対応**：同じ Spider で、HTTP リクエストとステルス対応のヘッドレスブラウザを共通のインターフェースから使えます。ID でリクエストを各セッションに振り分け、必要になった時点でセッションを初期化することもできます。
- **一時停止と再開**：チェックポイントにクロールの進み具合を保存します。Ctrl+C で安全に終了し、次の起動時に続きから再開できます。
- **ストリーミングモード**：`async for item in spider.stream()` で、取得したデータをその都度受け取れます。リアルタイムの統計もあり、UI、データ処理パイプライン、長時間のクロールに適しています。
- **ブロックされたリクエストの検出**：ブロックされたリクエストを自動で検出し、再試行します。処理はカスタマイズできます。
- **組み込みのエクスポート**：フックと独自のパイプラインで結果を出力できます。組み込みの JSON/JSONL 出力には、それぞれ `result.items.to_json()` / `result.items.to_jsonl()` を使えます。
- **ライフサイクルフック**：`on_start()`、`on_close()`、`on_error()`、`on_scraped_item()` などのフックで、クロールの開始から終了まで制御できます。
- **詳しいクロール統計**：リクエスト、レスポンス、バイト数、ステータスコード、プロキシ、ドメインやセッションごとの内訳、ログレベルごとの件数などを記録します。
- **uvloop 対応**：`use_uvloop=True` を `spider.start()` に渡すと、uvloop が利用可能な場合に非同期処理が速くなります。

Web サイトに詳しい説明の節を追加しました。[こちら](spiders/architecture.md)を参照してください。

### 🔄 プロキシの切り替え {#v0.4-proxy-rotation}

* スレッドセーフなプロキシ切り替えを行う `ProxyRotator` クラスを追加しました。すべての Fetcher とセッションで使えます。

  ```python
  from scrapling import ProxyRotator
  rotator = ProxyRotator(["http://proxy1:8080", "http://proxy2:8080"])
  Fetcher.get(url, proxy_rotator=rotator)
  ```

* **独自の切り替え方法**：プロキシを切り替える処理を自分で定義できます。
* **リクエストごとのプロキシ指定**：`proxy=` を個別の `get()`/`post()`/`fetch()` 呼び出しに渡すと、そのリクエストだけセッションのプロキシ設定を上書きできます。

### 🌐 ブラウザ用 Fetcher の改善 {#v0.4-browser-fetcher-improvements}

* **ドメインのブロック**：新しい `blocked_domains` 引数を `DynamicFetcher`/`StealthyFetcher` に追加しました。指定したドメインへのリクエストをブロックします（サブドメインも自動で対象になります）。
* **自動再試行**：ブラウザ用 Fetcher は、失敗時に再試行するようになりました。`retries`（既定値：3）と `retry_delay`（既定値：1s）で設定でき、プロキシ関連のエラーも検出します。
* **レスポンスのメタデータ**：`Response.meta` 辞書に使用したプロキシを自動で保存し、リクエストのメタデータもまとめます。
* **Response.follow()**：Referer を自動で引き継ぐ次の `Request` オブジェクトを作成します。Spider システム向けの機能です。
* **自動再生の停止**：ブラウザセッションでコンテンツの自動再生をブロックし、以前発生していた問題を防ぎます。
* **速度**：ブラウザの起動フラグを調整し、ステルス性と速度を改善しました。

### 🔧 バグ修正と改善 {#v0.4-bug-fixes-improvements}
- **パーサーの最適化**：繰り返し行う操作を最適化し、性能を改善しました。
- **ページのエラー**：ページでエラーが発生したときにブラウザが閉じない問題を修正しました。
- **空の本文**：本文が空のレスポンスに対応しました。
- **Playwright のイベントループ**：CDP 接続に失敗したときに Playwright のイベントループが閉じない問題を解決しました。
- **型の安全性**：mypy のエラーをすべて修正し、型が付いていなかった関数本体に型ヒントを追加しました。CI ワークフローに mypy と pyright を追加しました。

### ⚠️ 互換性に影響する変更 {#v0.4-breaking-changes}

* **`css_first`/`xpath_first` の削除**：代わりに `css('.selector').first`、`css('.selector')[0]`、または `css('.selector').get()` を使ってください。
* **すべての選択操作が `Selectors` を返します**：`css('::text')`、`xpath('//text()')`、`css('::attr(href)')`、`xpath('//@href')` は、`Selectors` を返すようになりました。テキストノードは `Selector` オブジェクトに包まれ、`tag="#text"` を持ちます。以前の `TextHandlers` は返しません。これにより、選択メソッド全体で API と型ヒントが一貫します。
* **`Response.body` は常に `bytes` です**：以前は `str` または `bytes` でしたが、今後は常に `bytes` を返します。
* **`get()`/`getall()` の動作**：`Selector` では、`get()` が `TextHandler`（シリアライズした HTML またはテキスト値）を返し、`getall()` が `TextHandlers` を返します。別名は `extract_first = get`、`extract = getall` です。古い `get_all()` は `Selectors` から削除しました。
* **`Selectors.first`/`.last`**：安全に要素へアクセスでき、`Selector | None` を返します。`IndexError` は発生しません。
* **内部定数の名前変更**：`DEFAULT_FLAGS` → `DEFAULT_ARGS`、`DEFAULT_STEALTH_FLAGS` → `STEALTH_ARGS`、`HARMFUL_DEFAULT_ARGS` → `HARMFUL_ARGS`、`DEFAULT_DISABLED_RESOURCES` → `EXTRA_RESOURCES`。

### 🔨 その他の変更 {#v0.4-other-changes}

* **依存関係の変更**：`tldextract` を `tld` に置き換えました。内部の `_html_utils.py` を削除して `w3lib.html.replace_entities` を使うようにし、`typing_extensions` を必須の依存関係に追加しました。
* **ドキュメントの全面更新**：MkDocs から Zensical に完全移行し、Spider のドキュメントを追加しました。既存の全ページを更新し、新しい API リファレンスも追加しました。

## [v0.3.14](https://github.com/D4Vinci/Scrapling/releases/tag/v0.3.14) - 2026-01-03 {#v0.3.14}

**v0.3.13 で一部のデバイスに発生した問題を修正する、小さなメンテナンス更新です**

- `StealthyFetcher` とそのセッションクラスでシークレットモードを無効にしました。このモードにより、Windows ではページ間で Cookie が保持されなくなっていました。MacOS と Linux では発生していません（[#123](https://github.com/D4Vinci/Scrapling/issues/123) を修正。報告した @frugality4121 と解決方法を示した @gembleman に感謝します）。
- browserforge を最新バージョンに固定しました。すでに古い browserforge が入っている環境で、古いヘッダーモデルが使われる問題を解決します。

## [v0.3.13](https://github.com/D4Vinci/Scrapling/releases/tag/v0.3.13) - 2026-01-01 {#v0.3.13}

**多くの部分を改善した大きな更新です。必要な対応として、互換性に影響する変更も多く含まれています。更新前に以下を読んでください**

* さまざまな理由から、今後は Camoufox を一切使わないことにしました。Camoufox の開発が続けば、将来また使う可能性はあります。このリリース以前のように Camoufox を使い続けたい場合は、[こちらの節](https://github.com/D4Vinci/Scrapling/blob/v0.3.13/docs/fetching/stealthy.md#using-camoufox-as-an-engine)に手順があります。

* 以前は `DynamicFetcher` とそのセッションクラスのステルスモードで patchright を使っていました。今回はそれらのステルスモードを削除し、`StealthyFetcher` とそのセッションクラスで patchright を使うようにしました。以下で説明するとおり、多くの改善を加え、patchright を基に全体のステルス性も高めています。

**これにより、`StealthyFetcher` とそのセッションクラスは以前より 101% 速くなり、メモリとディスク容量の使用量が減り、コードも約 400 行短くなりました。何より、Camoufox を使っていたときより安定しています。**

この変更で、`scrapling install` コマンドのインストール時間が短くなり、Docker イメージも小さくなります。GitHub CI のテストも円滑になり、新しいユーザーにも Scrapling が分かりやすくなります。

### 互換性に影響する変更 {#v0.3.13-breaking-changes}
1. `stealth` 引数を `DynamicFetcher` とそのセッションクラスから削除し、`hide_canvas` 引数を `StealthyFetcher` とそのセッションクラスへ移しました。
2.  `disable_webgl` 引数を `DynamicFetcher` から `StealthyFetcher` クラスへ移し、`allow_webgl` に名前を変えました。すべてのセッションクラスでも同じ変更を行っています。
3. `StealthyFetcher` は基本的に `DynamicFetcher` の新しいステルス版になりました。そのため、`block_images`、`humanize`、`addons`、`os_randomize`、`disable_ads`、`geoip` を削除しました。Chromium でこれらを再現しようとしましたが、それぞれに問題がありました。v0.4 までの今後のリリースで変わる可能性があります。

続いて良い知らせです。多くの改善と修正を行いました :)

### 改善 {#v0.3.13-improvements}
- すでに説明したように、`StealthyFetcher` とそのセッションクラスは以前より 101% 速くなりました。さらに、`DynamicFetcher` とそのセッションクラスも 20% 速くなりました。
- Cloudflare のチャレンジを処理するアルゴリズムを改善し、より多くの状況に、より速く対応できるようにしました。今回のリファクタリングで、CAPTCHA の処理も以前の倍の速度になります。
- すべての Fetcher のメモリ使用量を減らしました。
- MCP サーバーのトークン使用量が減り、費用を節約できます！
- Docker イメージが 60% 小さくなりました。
- ドキュメントサイト全体を新しい機能に合わせて更新しました。説明を明確にし、多くの節を短くして、例を追加しました。足りなかった引数の説明や API リファレンスの図なども追加し、ほかにも多くの改善を行っています。サイトの読み込みは 130% 速くなり、通信量も減り、SEO も改善しました。

### バグ修正 {#v0.3.13-fixes}
- Web スクレイピングシェルのショートカットに、以前足りなかった引数を追加し、より正確にしました。
- URL が localhost や IP アドレスでも `google_search` が Google の Referer を作っていた問題を修正しました。

## [v0.3.12](https://github.com/D4Vinci/Scrapling/releases/tag/v0.3.12) - 2025-12-18 {#v0.3.12}

### 変更内容 {#v0.3.12-what-s-changed}
- `DynamicSession`/`AsyncDynamicSession` に `timezone_id` 引数を追加しました。使用するプロキシや VPN に合わせてブラウザのタイムゾーンを設定できます。これにより、タイムゾーンの違いからプロキシの使用を検出されるのを防げます。
- レスポンスを JSON に自動変換する処理を改善しました。
- Fetcher のセッションクラスにある内部関数 `__create__` を `start` に変更しました。`with` の外でもセッションを使いやすくなります。
- `curl_cffi` などの依存関係を最新バージョンに更新しました。

## [v0.3.11](https://github.com/D4Vinci/Scrapling/releases/tag/v0.3.11) - 2025-12-03 {#v0.3.11}

### 変更内容 {#v0.3.11-what-s-changed}
- メディアを再生しているサイトなど、安定しないサイトで `network_idle` を使う場合のタイムアウト処理を改善しました。
- Web スクレイピングシェルの `stealthy_fetch` ショートカットの自動補完を修正しました。

## [v0.3.10](https://github.com/D4Vinci/Scrapling/releases/tag/v0.3.10) - 2025-11-26 {#v0.3.10}

**多くの重要な変更と、互換性に影響する可能性がある変更を含むメンテナンス更新です**

- **すべての文字コードの問題を解決しました**。文字コードが正しく宣言されていないページも扱える、より良い方法を使っています（@Kemsty2 が [#110](https://github.com/D4Vinci/Scrapling/issues/110) [#111](https://github.com/D4Vinci/Scrapling/pull/111) で問題を指摘してくれました。感謝します）。
- すべてのブラウザ用 Fetcher で、リクエスト単位の設定がセッション単位の設定を上書きする処理の問題を**解決しました**。v0.3 から存在していた問題です。
- Web スクレイピング用の対話型シェルで、ショートカットの関数シグネチャを**修正しました**。シェルで正確に自動補完されるようになりました。この問題も v0.3 から存在していました。
- Maxmind データベースを**更新しました**。`geoip` 引数の動作が `StealthyFetcher` とそのセッションクラスで改善します。
- 使用するすべてのブラウザを最新バージョンに**更新しました**。
- **互換性に影響する変更**：すべての Fetcher を大きくリファクタリングしました。以下の変更により、既存のコードが動かなくなる可能性があります。
    1. Scrapling のコードを約 750 行減らし、多くの部分を変更しました。今後の保守がしやすくなり、リソースの使用量も少し減ります。
    2. すべての Fetcher とそのセッションクラスで引数の検証が大幅に速くなり、全体の速度も向上します。
    3. この改善のため、すべての Fetcher で位置引数として渡せるのは `url` だけになりました。残りはキーワード引数にしてください。たとえば `Fetcher.get('https://google.com', stealthy_headers=True)` と書く必要があり、`Fetcher.get('https://google.com', True)` という書き方は使えません。
    4. v0.3 から、ブラウザ用 Fetcher とそのセッションクラスには不便な違いがありました。リクエストごとのパーサー設定を渡す引数が、Fetcher では `custom_config`、セッションクラスでは `selector_config` でした。今回のリファクタリングで、既存のコードを壊さずに `selector_config` に統一しました。今後は `selector_config` が主な引数になり、`custom_config` も互換性のために使えます。自動補完は `selector_config` のみ対応します。
    5. これらの変更のため、Fetcher の関数の型ヒントを動的に生成するようにしました。IDE で正しく自動補完されない場合は、新しいバージョンを使っているか確認してください。ほぼすべての有名な IDE とエディターでテストしました。

> すべてのベンチマーク表も更新し、同種のライブラリの最新バージョンと現在の結果を比較しています。

## [v0.3.9](https://github.com/D4Vinci/Scrapling/releases/tag/v0.3.9) - 2025-11-17 {#v0.3.9}

**多くの重要な変更を含む更新です**

### 🚀 新機能と使いやすさの改善 {#v0.3.9-new-stuff-and-quality-of-life-changes}
- `impersonate` 引数にブラウザのリストを渡せるようになりました。`Fetcher` と `FetcherSession` は、リクエストごとにリストからブラウザをランダムに選びます。

```python
from scrapling.fetchers import FetcherSession

with FetcherSession(impersonate=['chrome', 'firefox', 'safari']) as s:
  s.get('https://github.com/D4Vinci/Scrapling')
```

- `clean` メソッドに引数を追加しました。このメソッドは `TextHandler` にあり、現在のテキストから HTML エンティティを簡単に削除できます。
- ドキュメントを大幅に改善し、多くの部分をより正確に説明しました。メインの `README.md` の自動翻訳も追加しました。

### 🐛 バグ修正 {#v0.3.9-bug-fixes}
- ブラウザ用 Fetcher からレスポンスを取得する処理の大きな問題を修正しました。内容の種類を判定し、HTML の場合に限り、`response.body` にブラウザで描画した内容を入れます。それ以外は、最後のリクエストの元の内容を返します。これにより、バイナリファイルやテキストファイルを HTML タグに包まれずにダウンロードでき、Web サイトの取得では必要な描画済みの内容も得られます。

### 🔨 その他 {#v0.3.9-misc}
- 貢献ガイドを更新し、分かりやすくしました。
- コード品質ツールの実行を必須にする新しいワークフローを追加しました（pre-commit フックと同じツールです）。

## [v0.3.8](https://github.com/D4Vinci/Scrapling/releases/tag/v0.3.8) - 2025-10-27 {#v0.3.8}

**多くの重要な変更を含む更新です**

### 🚀 新機能と使いやすさの改善 {#v0.3.8-new-stuff-and-quality-of-life-changes}
- すべてのブラウザ用 Fetcher で、リクエストの読み込みが終わらないサイトに `network_idle` を使っても、コードがクラッシュしなくなりました。
- ブラウザ用 Fetcher でページ内容を取得・確認する処理を変え、Windows でも Linux/MacOS と同じように安定するようにしました（この動作の違いは、Windows での Playwright の実装が異なるためです）。
- 検証処理全体をリファクタリングし、すべてのブラウザ用 Fetcher のリクエストが 8-15% 速くなりました。
- 新しい `extra_flags` を `DynamicFetcher` とそのセッションに追加しました。ブラウザの起動時に、既存の Chrome フラグに独自のフラグを追加できます。
- `page_action` を使う場合は、前のバージョンで変更したレスポンス取得用のルーティング処理を元に戻しました。`page_action` がリクエストを送らずにページを変更しても、最新の内容を取得するためです（[#100](https://github.com/D4Vinci/Scrapling/issues/100) と [#102](https://github.com/D4Vinci/Scrapling/pull/102) で指摘した @gembleman に感謝します）。

### 🐛 バグ修正 {#v0.3.8-bug-fixes}
- `load_dom` のスペルミスを DynamicSession の async_fetch 内で修正しました。
- Cloudflare のチャレンジ処理で、解決後も消えない埋め込み CAPTCHA を待ち続ける問題を修正しました。今後は消えるまで 30 秒待ち、その後は消えない種類と判断します（#100 を修正）。

### 🔨 その他 {#v0.3.8-misc}
- Docker イメージを Dockerhub と GitHub のコンテナレジストリに自動で公開するようにし、利用しやすくしました。
- Scrapling で Scrapeless ブラウザを使う方法を説明する[新しいドキュメントページ](https://github.com/D4Vinci/Scrapling/blob/v0.3.8/docs/tutorials/external.md)を追加しました。

## [v0.3.7](https://github.com/D4Vinci/Scrapling/releases/tag/v0.3.7) - 2025-10-12 {#v0.3.7}

**多くの重要な変更を含む更新です**

### 🚀 新機能と使いやすさの改善 {#v0.3.7-new-stuff-and-quality-of-life-changes}
- `solve_cloudflare` の処理を `StealthyFetcher` で作り直し、あらゆる独自実装の Turnstile を解決できるようにしました。
- コード全体をリファクタリングし、Pyright のチェックを通るようにしました。すべての IDE で使い勝手が良くなり、多くのバグも修正されています。
- リクエストの処理を整理し、速くしました（#97 も解決）。
- すべてのブラウザ用セッションクラスに `user_data_dir` を追加しました。以前のセッションのブラウザデータ（Cookie、ストレージなど）を再利用できます。未指定の場合は、以前と同じく、Playwright が実行ごとにランダムなディレクトリを使います。
- 新しい設定項目 `additional_args` を `Dynamic fetcher` とそのセッションクラスに追加しました。Playwright のコンテキストに追加引数を渡せます。以前から `StealthyFetcher` で使えた機能と同じです。
- すべてのブラウザで、最後のナビゲーションレスポンスを取得するルーティング処理を改善しました。以前はブラウザで処理してから渡していましたが、今後はブラウザで処理する前のレスポンスを、そのままパーサーへ渡せます。テキストや JSON のレスポンスで特に役立ちます。

### 🐛 バグ修正 {#v0.3.7-bug-fixes}
- ルーティング処理の変更により、一部の Windows デバイスで不安定なサイトの内容を取得できない問題を解決しました。
- このバージョンのリファクタリングにより、以前は見つけにくかった多くのバグや、一部の IDE の不自然な自動補完も修正しました。
- ドキュメントサイトの多くの問題を修正しました。

## [v0.3.6](https://github.com/D4Vinci/Scrapling/releases/tag/v0.3.6) - 2025-10-01 {#v0.3.6}

### 🚀 新機能 {#v0.3.6-new-stuff}
- `solve_cloudflare` を `StealthyFetcher` とそのセッションクラスで改善し、あらゆる種類の Cloudflare Turnstile/Interstitial チャレンジを解決できるようにしました 🎉
- MCP サーバーで `Streamable HTTP` を使えるようになり、サーバーを簡単に外部へ公開できます。
- Docker 対応を追加しました。リリースごとにイメージを自動でビルドし、Docker Hub に公開します（すべてのブラウザを含みます）。

### 🐛 バグ修正 {#v0.3.6-bug-fixes}
- 一部の状況でパーサーに発生していた文字コードの問題を修正しました（よく見られた `invalid start byte` エラーです）。
- ライブラリの複数の部分を整理し、メモリリークを修正しました。設定によりますが、メモリ使用量が明らかに少なくなります（#92 も解決）。
- コードの多くの部分で型注釈を改善し、IDE を使いやすくしました（#93 も解決）。

## [v0.3.5](https://github.com/D4Vinci/Scrapling/releases/tag/v0.3.5) - 2025-09-20 {#v0.3.5}

**複数の問題を修正する重要なリリースです**

### 🚀 新機能 {#v0.3.5-new-stuff}
- すべてのブラウザ用 Fetcher（`DynamicFetcher`/`StealthyFetcher`/...）とそのセッションクラスで、サイトの取得が 15-20% 速くなりました。
    1. @AbdullahY36 が #87 で処理を改善したことで、ページ管理が大幅に速くなりました。
    2. 全体の検証処理を最適化し、同期取得でのページ作成も改善しました。これらにより速度が大きく向上しています。

- `DynamicFetcher` とそのセッションクラスでは、`rebrowser-playwright` を `PatchRight` に置き換え、ステルスモードを大幅に改善しました。
    1. 以前は `rebrowser-playwright` が、`stealth` と `real_chrome` の両方を有効にすると無効になっていました。組み合わせるとうまく動かなかったためですが、`PatchRight` ではこの問題はありません。
    2. クローズドな Shadow Root も操作できるようになりました。`PatchRight` が自動で対応します。

### 🐛 バグ修正 {#v0.3.5-bug-fixes}
- `re` メソッドを `Selectors` クラスで使ったときのバグを修正しました。
- Web スクレイピングシェルの `uncurl` と `curl2fetcher` が、curl の `--data-raw` フラグを正しく解析しない問題を修正しました。
- Web スクレイピングシェルの `view` コマンドで、サイトの文字コードによって発生するバグを修正しました。
- `mcp` モードと `extract` コマンドに影響する内容変換のバグを修正しました。

### 新しい貢献者 {#v0.3.5-new-contributors}
- @AbdullahY36 が #87 で初めて貢献しました。

## [v0.3.4](https://github.com/D4Vinci/Scrapling/releases/tag/v0.3.4) - 2025-09-16 {#v0.3.4}

**複数の問題を修正する重要なリリースです**

### 🚀 新機能 {#v0.3.4-new-stuff}
- すべての Fetcher のセッションクラスを対話型シェルに追加しました。インポートせずにすぐ使えます。

### 🐛 バグ修正 {#v0.3.4-bug-fixes}
- Windows の Playwright API で、Cloudflare のチャレンジ処理中にページ内容を取得すると起きるバグへの回避策を追加しました。
- 対話型シェルの `view` コマンドの文字コードの問題を修正しました。
- `max_pages` 引数が `AsyncStealthySession` でクラッシュを起こすバグを修正しました。
- 最近の更新により、`html_content` と `prettify` が `Selector` クラスで文字コードによって bytes を返すようになっていた問題を修正しました。どちらも以前と同じく文字列を返します。

## [v0.3.3](https://github.com/D4Vinci/Scrapling/releases/tag/v0.3.3) - 2025-09-15 {#v0.3.3}

- ブラウザ用 Fetcher で既定のタブを閉じる処理を削除しました。この処理がクラッシュを起こしていたためです（Mac では発生せず、Windows と Linux でのみ再現しました）。

## [v0.3.2](https://github.com/D4Vinci/Scrapling/releases/tag/v0.3.2) - 2025-09-15 {#v0.3.2}

v0.3.2 のリリースノート

### 🚀 新機能 {#v0.3.2-new-stuff}

- **Fetcher の依存関係をオプションに変更**：すべての Fetcher をオプション依存関係のグループに移し、基本パッケージを小さくしました。基本の `scrapling` モジュールにはパーサーだけが含まれます。Fetcher やコマンドライン機能を使う場合は、`pip install "scrapling[fetchers]"` を実行してください。詳しいインストール手順は[こちら](index.md#installation)にあります。
- **セッション内のページごとの設定**：ブラウザ用 Fetcher のセッションクラスで、ページごとに設定を変えられるようになりました。取得時の引数も、セッションの引数と同じように検証します。詳細はドキュメントサイトの[こちら](fetching/stealthy.md#full-list-of-arguments)を参照してください。
    <br>例：

    ```python
    with StealthySession(headless=True, solve_cloudflare=True) as session:
        page = session.fetch('https://nopecha.com/demo/cloudflare', google_search=False)
    ```

- **ブラウザ用 Fetcher の改善**
    - ページの JavaScript の実行完了を待つかどうかを選ぶ設定を追加しました（以前と同じく、既定で有効です）。

        ```python
        with DynamicSession(headless=True, disable_resources=False, network_idle=True) as session:
           page = session.fetch('https://quotes.toscrape.com/', load_dom=False)
        ```

    - `DynamicFetcher` とそのセッションクラスのステルスモードの信頼性が向上しました。
    - `DynamicFetcher` と `StealthyFetcher` のリソース使用量を減らしました（Playwright API の永続コンテキストが開く既定のタブを自動で見つけて閉じます）。
    - ブラウザ用 Fetcher でページを切り替える処理の重要なバグを修正しました。古いページは新しいページに置き換えます（タブを再利用すると、以前の設定が残っている場合があります）。
    - `StealthyFetcher` とそのセッションクラスが少し速くなりました（5%）。

- **`.body` プロパティの改善**：渡された内容を処理せず、そのまま返すようにしました。ファイルのダウンロードや、HTML 以外のリクエストを扱えます。以下は画像をダウンロードする例です。

    ```python
    from scrapling.fetchers import Fetcher

    page = Fetcher.get('https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/poster.png')
    with open(file='poster.png', mode='wb') as f:
        f.write(page.body)
    ```

### 🐛 バグ修正 {#v0.3.2-bug-fixes}

- **文字コードの問題を解決**：一部のサイトでパーサー、mcp モード、extract コマンドに発生していた複数の文字コードの問題を修正しました（#80 と #81 も解決）。
- **解析速度の向上**：さまざまな変更によりライブラリが速くなり、更新したベンチマークにも結果が表れています。

### 🔨 その他 {#v0.3.2-misc}

- **ベンチマークの更新**：速度の改善を同種のライブラリの最新バージョンと比較するため、性能ベンチマークを更新しました。
- **多くのコードをリファクタリングし、不要なコードをより良い実装に置き換えました**：コードが少なく、明確になり、保守しやすくなりました。
- **YouTube 動画の追加**：MCP のドキュメントに動画を追加しました。
- **新しい Issue テンプレート**：既存のテンプレートを使えないユーザー向けに、簡単なテンプレートを追加しました。
- **CI ワークフローの最適化**：ドキュメントやコード以外のファイルだけが変わった場合は、テストワークフローを実行しません。
- **依存関係の更新**：さまざまな依存関係を最新バージョンに更新しました。
- **コードスタイルの改善**：すべてのファイルに新しい ruff ルールを適用しました。
- **Pre-commit フック**：pre-commit の設定を更新しました。

### 🎯 互換性に影響する変更 {#v0.3.2-breaking-changes}

- `max_pages` 引数を同期版の `StealthySession` から削除し、`DynamicSession` とそろえました（同期版では意味のない設定です）。

## [v0.3.1](https://github.com/D4Vinci/Scrapling/releases/tag/v0.3.1) - 2025-09-02 {#v0.3.1}

1. オプション依存関係の `shell` を入れずに Scrapling をインストールしたときの問題を修正しました（#76）。
2. すべてのブラウザ用 Fetcher とそのセッションクラスに、ページ作成時に実行する JS ファイルを指定する引数を追加しました（#56）。

```python
from scrapling.fetchers import StealthyFetcher

StealthyFetcher.fetch('https://example.com', init_script="/absolute/path/to/js/script.js")
```

## [v0.3](https://github.com/D4Vinci/Scrapling/releases/tag/v0.3) - 2025-09-01 {#v0.3}

🎉 **大型リリース：アーキテクチャを全面的に刷新**

Scrapling v0.3 は、プロジェクト史上最大の更新です。アーキテクチャを全面的に書き直し、パフォーマンスを大きく改善しました。AI 連携や Web スクレイピング用の対話型シェルなど、強力な新機能も追加しています。

このリリースには互換性に影響する変更が複数あります。リリースノートをよく確認してください。

### 🚀 主な新機能 {#v0.3-major-new-features}

#### セッションを使うアーキテクチャ {#v0.3-session-based-architecture}
- **新しいセッションクラス**：全面的な書き直しにより、状態を保持するセッションに対応しました。
    - `FetcherSession`：HTTP リクエスト間で状態を保持します。同期コードと非同期コードの両方で使えます。
    - `DynamicSession`/`AsyncDynamicSession`：処理が終わるまでブラウザを開いたまま、自動操作できます。
    - `StealthySession`/`AsyncStealthySession`：処理が終わるまでブラウザを開いたまま、ステルス機能を使えます。
- **非同期のブラウザタブ管理**：新しい `max_pages` 引数でタブのプールを使えます。タブを順に利用して、ブラウザから同時にページを取得します。
- **セッションの同時実行**：互いに独立した複数のセッションを同時に実行できます。

詳しくは、Web サイトの `Fetching` セクションを参照してください。

#### ステルス機能とボット対策への対応を多数追加 {#v0.3-a-lot-of-new-stealth-anti-bot-capabilities}
- **🤖 Cloudflare チャレンジの解決**：`StealthyFetcher` とそのセッションクラスで、[Cloudflare Turnstile チャレンジを自動で解決](fetching/stealthy.md#cloudflare-and-stealth-options)できます。
- **ブラウザのフィンガープリントを再現**：新しくなった [Fetcher](fetching/static.md) クラスで、実際のブラウザの TLS フィンガープリントやバージョンに合ったヘッダーを再現できます。HTTP/3 などにも対応しています。
- **ステルスモードの改善**：`DynamicFetcher` とそのセッションクラスのステルスモードが、より安定して動作するようになりました（別名 `PlayWrightFetcher`）。

#### AI 連携と MCP サーバー {#v0.3-ai-integration-mcp-server}
- **MCP サーバーを内蔵**：Model Context Protocol サーバーを使って、AI による Web スクレイピングを行えます。
- **6 つの強力なツール**：`get`、`bulk_get`、`fetch`、`bulk_fetch`、`stealthy_fetch`、`bulk_stealthy_fetch`
- **内容を効率よく抽出**：Web ページや要素を Markdown や HTML に変換したり、不要な部分を除いたテキストを抽出したりできます。
- **CSS セレクターに対応**：AI に内容を渡す前に、Scrapling のエンジンで必要な要素を正確に選べます。
- **ボット対策の回避**：Cloudflare Turnstile などの保護機能に対応できます。
- **プロキシに対応**：プロキシで匿名性を確保したり、特定の地域からアクセスしたりできます。
- **ブラウザを再現**：TLS フィンガープリントや、ブラウザのバージョンに合った実際のヘッダーなどを再現できます。
- **並行処理**：複数の URL を同時にスクレイピングして、効率を上げられます。
- [そのほかの機能...](ai/mcp-server.md)

#### Web スクレイピング用の新しい対話型シェル {#v0.3-new-interactive-web-scraping-shell}
- **新しいシェル**：`get`、`post`、`put`、`delete`、`fetch`、`stealthy_fetch` など、多くの便利なショートカットを内蔵した独自の IPython シェルです。
- **ページを自動管理**：新しい `page` と `pages` コマンドで、現在のページと、シェルから行ったすべてのリクエストの履歴を自動で保存します。
- **Curl 連携**：`uncurl` と `curl2fetcher` 関数で、ブラウザの DevTools の curl コマンドを `Fetcher` のリクエストに変換できます。
- [そのほかの機能...](cli/interactive-shell.md)

#### プログラミングせずにターミナルからスクレイピング {#v0.3-scrape-from-the-terminal-without-programming}
- **新しい抽出コマンド**：プログラミングせずに、ターミナルでスクレイピングできます。
    - `scrapling extract get/post/put/delete`：基本的な HTTP リクエストを送信します。
    - `scrapling extract fetch`：動的な内容をスクレイピングします。
    - `scrapling extract stealthy-fetch`：ボット対策を回避します。
- **Web ページをダウンロード**し、その内容をファイルに保存します。
- **HTML を読みやすい形式に変換**できます。Markdown に変換する、HTML のまま保存する、ページのテキストだけを抽出する、といった使い方ができます。
- **独自の CSS セレクターに対応**し、ページの特定の部分を抽出できます。
- **HTTP リクエストとブラウザによる取得に対応しています。**
- **細かく設定できます**。独自のヘッダー、Cookie、プロキシなどを指定できます。コードで使えるほぼすべてのオプションを、ターミナルからも使えます。
- [そのほかの機能...](cli/extract-commands.md)

### 🔧 技術的な改善 {#v0.3-technical-improvements}

#### パフォーマンスの改善 {#v0.3-performance-enhancements}
- **Fetcher の速度が 4 倍になりました**。読み間違いではありません！
- **DynamicFetcher が約 60% 高速になりました**。設定、特にステルスモードによって、大きく高速化します。
- **StealthyFetcher が 20–30% 高速になりました**。新しい構造を使い、`Camoufox` の Python インターフェースの代わりに独自の実装を使い始めたためです。
- **主な選択メソッド全体で 50% 以上の高速化**を実現しました（`find_by_text`、`find_similar`、`find_by_regex`、`relocate` など）。🚀
- **CSS/XPath の first メソッドが約 10% 高速になりました**。`css_first` と `xpath_first` は、`css` と `xpath` より速くなりました。
- **内容抽出用の `get_all_text()` メソッドが 40% 高速になりました**。
- **適応型機能で要素を再び見つける処理が 20% 高速になりました**。
- **要素間の移動に使うプロパティを最適化しました**。`next`、`previous`、`below_elements` などが、目に見えて速くなりました。
- **テキストの整形処理が 5 倍高速になりました**。
- **メモリ効率を改善しました**。インポートを最適化し、余分な処理を減らしました。
- **⚡ インポートを高速化しました**。モジュールの読み込みを最適化し、起動時間を短くしました。
- **ベンチマークの改善**：これらの高速化により、ほかのライブラリと比べてもさらに速くなりました。BeautifulSoup の 1775 倍、AutoScraper の 5.1 倍の速度です。[ベンチマーク](benchmarks.md)を参照してください。

#### アーキテクチャ、コード品質、使いやすさ {#v0.3-architecture-code-quality-and-quality-of-life}
- **永続コンテキスト**：すべてのブラウザ Fetcher が、既定で永続コンテキストを使うようになりました。（#64 も解決します）
- **msgspec でブラウザ Fetcher をすばやく検証します**。リクエストの実行前に検証するので、エラーの原因を見つけやすくなりました。
- **Fetcher が返すすべての Cookie** が、その Fetcher で受け付ける形式になりました。取得した Cookie を、すべての Fetcher とセッションクラスに再び渡せます。
- **コードチェックと整形を高速化しました**。`ruff` に移行しています。
- **新しいビルドシステム**：setup.py から pyproject.toml に移行しました。📦
- **GitHub Actions とワークフローを改善し**、開発とテストを進めやすくしました。
- **🎨 型ヒントを改善しました**。現在の Python の標準に沿って全体に型を付け、IDE のサポートと信頼性を高めました。
- **コードを整理しました**。使われないコードを削除し、主要な関数を最適化しました。🧹
- **🚀 後方互換性**：古いコードを引き続き使えるように、ショートカットを追加しました。

### 互換性に影響する変更 {#v0.3-breaking-changes}

#### 必要な Python のバージョン {#v0.3-minimum-python-version}
- **Python 3.10+ が必要です**。Python 3.9 以前のサポートを終了しました。

#### クラスとメソッドの名前 {#v0.3-class-and-method-naming}
名前をより分かりやすく統一し、特に初めて使う人が理解しやすいように変更しました。

- **`Adaptor` → `Selector`**：主要な解析クラスの名前を変更しました（後方互換性のため、引き続き `Adaptor` としてインポートできます）。
- **`Adaptors` → `Selectors`**：コレクションクラスの名前を変更しました（後方互換性のため、引き続き `Adaptors` としてインポートできます）。
- **`auto_match` → `adaptive`**：すべてのメソッドで引数名を変更しました。
- **`adaptor_arguments` → `selector_config`**：設定用の引数名を変更しました。
- **`automatch_domain` → `adaptive_domain`**：ドメイン用の引数名を変更しました。
- **`additional_arguments` → `additional_args`**：引数名を短くしました。
- **⚠️ `text/body` → `content`**：Selector のコンストラクターの引数が、`str` と `bytes` の両方を受け付けるようになりました。
- **`PlayWrightFetcher` → `DynamicFetcher`**：ブラウザを自動操作するクラスの名前を変更しました（後方互換性のため、引き続き `PlayWrightFetcher` としてインポートできます）。
- **DynamicFetcher から NSTBrowser の処理と引数を削除しました**。これらの処理を残す必要がなくなったためです。
- **StealthyFetcher の headless 引数は 'virtual' を受け付けなくなりました**。Camoufox のライブラリは、ブラウザのインストール先とその他の起動オプションを取得するためだけに使っています。

### 🐛 バグ修正 {#v0.3-bug-fixes}

- `get_all_text` が無視するタグ内で、入れ子の子要素を数える処理を修正しました（#61）。
- Python の実行ファイルのパスに空白がある場合のインストールの問題を修正しました（#57）。
- 適応型機能を有効にしたとき、ストレージで再帰処理に伴って起こるスレッドの問題を修正しました。
- `FetcherSession` で Sentinel パターンを使い、引数の優先順位の問題を修正しました。
- `StealthyFetcher` でプロキシの型を扱う処理を修正しました。
- `referer` と `google_search` の引数が競合する問題を修正しました。
- ステルス用スクリプトを非同期で挿入するときの問題を修正しました。

## [v0.2.99](https://github.com/D4Vinci/Scrapling/releases/tag/v0.2.99) - 2025-04-08 {#v0.2.99}

**Scrapling の機能を十分に使うために、すべてのユーザーにとって重要な更新です。**

### 変更内容 {#v0.2.99-what-s-changed}
#### 完全なドキュメントを掲載する新しい Web サイト {#v0.2.99-new-full-documentation-website}
- ついにできました 😄 [こちら](index.md)からご覧ください。
#### Fetcher のインポート方法を統一 {#v0.2.99-unified-import-logic-for-fetchers}
- `from scrapling.fetchers import Fetcher, AsyncFetcher, StealthyFetcher, PlayWrightFetcher` ですべての Fetcher をインポートし、初期化せずに `page = Fetcher.get(...)` のように直接使えるようになりました。<br/>従来の `from scrapling.defaults import Fetcher, AsyncFetcher, StealthyFetcher, PlayWrightFetcher` に代わる方法です。
#### 互換性に影響する変更：automatch は既定で無効 {#v0.2.99-breaking-change-automatch-is-now-turned-off-by-default}
- Fetcher で automatch を有効にしたり、ほかの解析オプションを設定したりする新しい方法を導入しました。詳しくは[ドキュメント](fetching/choosing.md#parser-configuration-in-all-fetchers)を参照してください。
>  後方互換性のため、以前のインポート方法と処理も使えますが、警告が表示されます。
#### Fetcher に新しいオプションを追加 {#v0.2.99-new-options-added-to-fetchers}
- `StealthyFetcher` と `PlayWrightFetcher` の両方に、取得時の引数 `wait` を追加しました。ページを閉じてレスポンスを返す前に、指定した時間（ミリ秒）だけ待機します。
- `StealthyFetcher` の `fetch` と `async_fetch` メソッドに、`additional_arguments` 引数を追加しました。Camoufox に追加の設定を渡せます。この設定は Scrapling の設定より優先されます（#54）。
#### バグ修正 {#v0.2.99-bugs-squashed}
- `async_fetch` でリダイレクトを取得する際のバグを修正しました。`StealthyFetcher` と `PlayWrightFetcher` の両方が対象です。

**_ご支援とご寄付に感謝します！_**

## [v0.2.98](https://github.com/D4Vinci/Scrapling/releases/tag/v0.2.98) - 2025-03-17 {#v0.2.98}

**Scrapling の機能を十分に使うために、すべてのユーザーにとって重要な更新です**

### 変更内容 {#v0.2.98-what-s-changed}
#### メモリ使用量と速度のさまざまな改善 {#v0.2.98-various-memory-usage-and-speed-optimizations}
- すべての選択メソッドのメモリ使用量が以前の約 40% になり、速度も少し上がりました。
- ライブラリのすべてのサブモジュールを必要なときに読み込むようにしました。使うものだけが読み込まれます。たとえば、次のように変わります。
更新前は、`from scrapling import Adaptor` で Fetcher などもすべて読み込むため、RAM を `30-40mb` 使用していました。現在は `~1.2mb` です。
- 前回の更新では、大きなリクエストプールを使う場合のメモリ使用量が以前の約 32% になりました。今回はキャッシュをさらに調整し、使用量をそれよりも減らしました。
- パーサー全体が 2-5% 高速になりました。

**_ご支援とご寄付に感謝します！_**

## [v0.2.97](https://github.com/D4Vinci/Scrapling/releases/tag/v0.2.97) - 2025-03-15 {#v0.2.97}

**Scrapling の機能を十分に使うために、すべてのユーザーにとって重要な更新です**

### 変更内容 {#v0.2.97-what-s-changed}
#### すべての Fetcher でメモリ使用量を削減し、少し高速化 {#v0.2.97-lower-memory-usage-and-small-speed-increase-across-all-fetchers}
- ライブラリ全体でキャッシュサイズに新しい制限を設けました。大量のリクエストや操作を行うとき、メモリ使用量が以前より大きく減ります。
- Fetcher の多くの部分を書き直し、保守しやすくするとともに、少し高速化しました。

#### バグ修正 {#v0.2.97-bugs-fixed}
- `TextHandler` だけをインポートして文字列以外の値を渡すと、空の文字列になるバグを修正しました。現在は `TextHandler` に渡した値を必ず文字列に変換してから、`TextHandler` に変換します。どの値にもこの処理を適用します。名前のとおり、`TextHandler` は文字列を扱うためのものです！（#45）
- AsyncFetcher のほとんどのメソッドで、`retries` 引数が考慮されないバグを修正しました。

#### その他 {#v0.2.97-miscellaneous}
- すべての Fetcher のほとんどの引数について、型ヒントをより明確で正確にしました。

**_ご支援とご寄付に感謝します！_**

## [v0.2.96](https://github.com/D4Vinci/Scrapling/releases/tag/v0.2.96) - 2025-03-05 {#v0.2.96}

**Scrapling の機能を十分に使うために、すべてのユーザーにとって重要な更新です**

### 変更内容 {#v0.2.96-what-s-changed}
1. `-f` オプションを `scrapling install` に追加し、ブラウザの依存関係を強制的に再インストールできるようにしました。`scrapling install -f` を実行することをお勧めします。新しい Camoufox のブラウザバージョンで、`StealthyFetcher` が大きく高速化します :)
2. `TextHandler` のスライスが `TextHandlers` を返すバグを修正し、正しく `TextHandler` を返すようにしました。その型ヒントも修正しました（#41）。
3. `scrapling install` の実行中に、場合によっては Python シェルが開いてしまう問題を修正しました！

## [v0.2.95](https://github.com/D4Vinci/Scrapling/releases/tag/v0.2.95) - 2025-02-25 {#v0.2.95}

**Scrapling の機能を十分に使うために、すべてのユーザーにとって重要な更新です**

### 変更内容 {#v0.2.95-what-s-changed}
1. `Fetcher` で、`stealthy_headers` 引数が生成したヘッダーが、ユーザーの指定した `Accept` などのヘッダーを上書きするバグを修正しました（#39）。
2. ヘッダーの生成処理を少し改善したので、速度がわずかに上がるはずです。

## [v0.2.94](https://github.com/D4Vinci/Scrapling/releases/tag/v0.2.94) - 2025-02-22 {#v0.2.94}

**Scrapling の機能を十分に使うために、すべてのユーザーにとって重要な更新です**

### 変更内容 {#v0.2.94-what-s-changed}
1. すべての Fetcher に `history` プロパティを追加し、リダイレクトを確認できるようにしました（#32）。
2. `case_sensitive` 引数の処理を、すべての `re`/`re_first` で修正しました。使っていた場合は、コードが返す結果が変わることがあります（期待どおりに動かないと気づいていながら issue を報告しなかったのなら、自業自得かもしれませんね、笑）。
3. 依存関係を更新し、Camoufox エンジン（StealthyFetcher）で `coop` を再び有効にしました。

## [v0.2.93](https://github.com/D4Vinci/Scrapling/releases/tag/v0.2.93) - 2025-01-31 {#v0.2.93}

**Scrapling の機能を十分に使うために、すべてのユーザーにとって重要な更新です**

### 変更内容 {#v0.2.93-what-s-changed}
1. パーサー全体で戻り値の型を統一しました。必ず `Adaptor`、`Adaptors`、`TextHandler`、`TextHandlers`、`None` のいずれかを返します。CSS セレクターの組み合わせなどで結果が混在する場合は、リストを返します。手動の型チェックが減ってコードを書きやすくなり、ライブラリが安定し、いつでもメソッドをつなげて呼び出せます。
2. パーサーの多くの部分、特に `Adaptor` クラスを書き直し、より分かりやすく高速にしました。検索メソッドをはじめ、ほとんどのメソッドとプロパティが 5-40% 高速になりました。中にはさらに大きく改善したものもあり、`find_by_regex` は約 60% 高速になりました！automatch 機能も約 5% 高速になりました。
3. `find_all`/`find` メソッドで、渡したフィルターが OR として扱われる場合と AND として扱われる場合があるバグを修正しました。現在は、返されるすべての要素が、渡したすべてのフィルターを満たす必要があります。
4. 正規表現に関するすべてのメソッドが `TextHandler`/`TextHandlers` を返すようになり、メソッドをつなげて呼び出しやすくなりました。
5. **新しい** `below_elements` プロパティを追加しました。DOM ツリー内で現在の要素より下にあるすべての要素を、`Adaptors` オブジェクトとして返します。
6. HTML ソースを文字列として返していたすべてのメソッドとプロパティが、`TextHandler` を返すようになりました。これにより、正規表現などを簡単に使えます。
7. StealthyFetcher が少し高速になり、ステルス性能も向上しました。**Cloudflare Turnstile** など、iframe 内の CAPTCHA もクリックできるようになりました。
8. ライブラリのほぼ半分で、自動補完と型ヒントを大きく改善しました。特に `Adaptor`、`TextHandler`、`TextHandlers` が対象です。
9. `TextHandler` をスライスしたり、インデックスで参照したり、`split` メソッドを使ったりすると、通常の Python 文字列ではなく、別の `TextHandler` を返すようになりました。ほぼすべての標準的な文字列操作とメソッドが `Texthandler` を返すので、いつでもメソッドや関数をつなげて呼び出せます。
10. 小さなバグや誤記を修正しました。たとえば、Fetcher の async_put が PUT ではなく POST リクエストを送っていました 😶‍🌫️
11. ドキュメントの Web サイトが完成するまでの間に、README を少し改善しました。

バージョン 0.3 までの小さな更新にする予定でしたが、もう少し良くしようと思いました。

## [v0.2.92](https://github.com/D4Vinci/Scrapling/releases/tag/v0.2.92) - 2024-12-26 {#v0.2.92}

### 変更内容 {#v0.2.92-what-s-changed}
- 読み込むページに iframe が多い場合、ブラウザ Fetcher のレスポンスが、より信頼できるデータ元を使うようになりました。
- **`Scrapling` のインストールがさらに簡単になりました。pip でインストールし、ターミナルで `scrapling install` を実行すれば準備完了です！**
- パーサーの不正確な型ヒントを修正しました。

## [v0.2.91](https://github.com/D4Vinci/Scrapling/releases/tag/v0.2.91) - 2024-12-19 {#v0.2.91}

### 変更内容 {#v0.2.91-what-s-changed}
- 取得を知らせるログが最初のリクエストだけで表示されるバグを修正しました。
- Playwright API はページを開くとき、`goto` に指定した読み込み状態 `["load", "domcontentloaded", "networkidle"]` を満たす最初のレスポンスを返します。そのため、Cloudflare のような待機ページの後で実際のサイトに移動する場合、403 など、最初のステータスコードが返されていました。この更新で、Playwright API を使う `PlaywrightFetcher` と `StealthyFetcher` の両方を修正しました。結果はもう Playwright のこの既定の動作に左右されません。
- `Fetcher` クラスで SOCKS プロキシに対応しました。
- `wait_selector_state` 引数の型ヒントを修正し、自動補完で正しい値が表示されるようにしました。

## [v0.2.9](https://github.com/D4Vinci/Scrapling/releases/tag/v0.2.9) - 2024-12-16 {#v0.2.9}

### 変更内容 {#v0.2.9-what-s-changed}
##### 新機能 {#v0.2.9-new-features}
1. Scrapling に**待望の**非同期サポートを追加しました！`AsyncFetcher` が `Fetcher` の非同期版として加わりました。`StealthyFetcher` と `PlayWrightFetcher` にも、同じオプションを使える新しいメソッド `async_fetch` を追加しました。

```python
>> from scrapling import StealthyFetcher
>> page = await StealthyFetcher().async_fetch('https://www.browserscan.net/bot-detection')  # the async version of fetch
>> page.status == 200
True
```

2. `StealthyFetcher` クラスの取得メソッドに、`geoip` 引数を追加しました。有効にすると、IP アドレスに対応する経度、緯度、タイムゾーン、国、ロケールを自動で使い、WebRTC の IP アドレスを偽装します。対象地域での言語の使用割合に基づいて、ブラウザの言語も選んで偽装します。
3. `retries` 引数を `Fetcher`/`AsyncFetcher` クラスに追加しました。`httpx` で行う各リクエストの再試行回数を設定できます。
4. `url_join` メソッドを `Adaptor` と Fetcher に追加しました。相対 URL を現在の URL と結合し、完全な絶対 URL を生成します！
5. `keep_cdata` メソッドを `Adaptor` と Fetcher に追加しました。必要に応じて、パーサーが CDATA を削除しないようにできます。
6. `Adaptor`/`Response` の `body` メソッドが、可能な場合は生の HTML レスポンスを返すようになりました。ライブラリ内では加工しません。
7. `Response` クラスにログ出力を追加しました。Fetcher を使うと、受け取ったレスポンスの情報がログに表示されます。
例：

   ```python
   >> from scrapling.defaults import Fetcher
   >> Fetcher.get('https://books.toscrape.com/index.html')
   [2024-12-16 13:33:36] INFO: Fetched (200) <GET https://books.toscrape.com/index.html> (referer: https://www.google.com/search?q=toscrape)
   >>
   ```

8. `TextHandler` で `.replace()` などの標準的な文字列メソッドを使うと、別の `TextHandler` を返すようになりました。以前は通常の文字列を返していました。
9. ライブラリ全体を大きく高速化し、Fetcher クラス全体のステルス性能も改善しました。
10. `extract_first`\`extract` など、元のオブジェクトと同じ結果を返す単純な関数を追加しました。Scrapy/Parsel ではこれらの関数を使うため、必要に応じてコードを Scrapling に簡単にコピーできるようにするためだけに追加したものです！
11. 多くのコードを書き直し、適切な場所にキャッシュを使うことで、大量のリクエストをまとめて行う場合の速度が大きく上がりました。

##### 互換性に影響する変更 {#v0.2.9-breaking-changes}
- Python 3.8 のサポートを終了しました。（主な理由は Playwright がサポートを終了したためですが、もともと問題の多いバージョンでした。）
- ライブラリ全体から `debug` 引数を削除しました。デバッグを有効にするには、ライブラリをインポートした後で次を実行してください。

   ```python
   >>> import logging
   >>> logging.getLogger("scrapling").setLevel(logging.DEBUG)
   ```

##### バグ修正 {#v0.2.9-bugs-squashed}
1. WebGL を既定で有効にしました。多くの保護機能が、WebGL が有効かどうかを確認するようになったためです。
2. ドキュメントと README の誤りや誤記を修正しました。

##### 使いやすさの改善 {#v0.2.9-quality-of-life-changes}
1. すべてのログを `scrapling` という名前のロガーに統一し、簡単に管理できるようにしました。以前はルートロガーを使っていました。
2. テストフォルダーの構成を整理し、新機能のテストを追加しました。すべてのテストを分かりやすく書き直し、カバレッジを上げるためにテストを増やしました。
3. コードの大部分を書き直し、分かりやすく保守しやすくしました。

> これらはすべて 0.3 で追加する予定でしたが、次のバージョンまで時間がかかるため、先に追加することにしました。次は詳細なドキュメントの Web サイトを完成させ、その後でバージョン 0.3 に取り組みます。

## [v0.2.8](https://github.com/D4Vinci/Scrapling/releases/tag/v0.2.8) - 2024-11-30 {#v0.2.8}

### 変更内容 {#v0.2.8-what-s-changed}
- 小さな更新です。コードを使いやすくするために必要な変更を加え、メインの README の誤記を修正しました（#20）。

## [v0.2.7](https://github.com/D4Vinci/Scrapling/releases/tag/v0.2.7) - 2024-11-26 {#v0.2.7}

### 変更内容 {#v0.2.7-what-s-changed}
##### 新機能 {#v0.2.7-new-features}
- `wait_selector` 引数を `StealthyFetcher` と `PlayWrightFetcher` で使う場合、その後に JavaScript が完全に読み込まれて実行されるまで、通常と同じように再び待つようになりました。`network_idle` も使っていれば、それらを待った後で、ネットワークがアイドル状態になるまで再び待ちます。すべての状態をすでに満たしている場合は、もちろん待ちません。
- `StealthyFetcher` で `disable_ads` 引数を使い、広告を許可するかブロックするかを選べるようになりました。既定では有効で、`ublock origin` アドオンをインストールします。
- `PlayWrightFetcher` のロケールを `locale` 引数で設定できるようになりました。既定値は引き続き `en-US` です。
- `Fetcher` の基本的なリクエストで、`http://username:password@localhost:8030` 形式のプロキシを使えるようになりました。
- `PlayWrightFetcher` のステルスモードを少し改善しました。

##### バグ修正と改善 {#v0.2.7-bugs-squashed-improvements}
1. `PlayWrightFetcher` クラスでプロキシを有効にできるかどうかが、`stealth` モードの有効・無効に左右されなくなりました（ご指摘いただいた [@AbdullahY36](https://github.com/AbdullahY36) に感謝します）。
2. `ResponseEncoding` が、レスポンスの文字コードをページに使えるかどうか確認するようになりました。エラーが起きる場合は、Scrapling が `utf-8` を使います。

## [v0.2.6](https://github.com/D4Vinci/Scrapling/releases/tag/v0.2.6) - 2024-11-24 {#v0.2.6}

### 変更内容 {#v0.2.6-what-s-changed}
##### 新機能 {#v0.2.6-new-features}
- `PlayWrightFetcher` が実際のブラウザを直接使えるようになりました。`real_chrome` 引数を `PlayWrightFetcher.fetch` に渡してください。Chrome がインストールされている必要があります。Scrapling がその Chrome を起動し、ほとんどのオプションを通常どおり使えます。（以前は `cdp_url` 引数でしかできませんでした。）
- 実際のブラウザ向けに生成するヘッダーのバージョンを上げました。

##### バグ修正 {#v0.2.6-bugs-squashed}
1. `BrowserForge` が生成するブラウザヘッダーの形式が古く、一部の保護機能で Scrapling が検出されることが分かりました。そのため、`BrowserForge` は実際の User-Agent の生成にだけ使うようにしました。
2. `hide_canvas` 引数を既定で無効にしました。Google の ReCaptcha に検出されるためです。

## [v0.2.5](https://github.com/D4Vinci/Scrapling/releases/tag/v0.2.5) - 2024-11-23 {#v0.2.5}

### 変更内容 {#v0.2.5-what-s-changed}

##### バグ修正 {#v0.2.5-bugs-squashed}
- 'wait_selector' 引数が 1 個を超える要素に一致した場合に起きるエラーを処理するようにしました。`StealthyFetcher` と `PlayWrightFetcher` が対象です。
- `content_type` ヘッダーの値に `charset` などのパラメーターが含まれる場合の文字コードを修正しました（[#12](https://github.com/D4Vinci/Scrapling/issues/12) を報告してくださった @andyfcx に感謝します）。

##### 使いやすさの改善 {#v0.2.5-quality-of-life}
- コードの新しい部分を確認するテストを追加し、テストをスレッドで実行するようにしました。
- Sphinx の apidoc などのツールで正しく表示されるよう、docstring を更新しました。

##### 新しい貢献者 {#v0.2.5-new-contributors}
- @andyfcx が [#13 ](https://github.com/D4Vinci/Scrapling/pull/13) で初めて貢献しました。

## [v0.2.4](https://github.com/D4Vinci/Scrapling/releases/tag/v0.2.4) - 2024-11-20 {#v0.2.4}

### 変更内容 {#v0.2.4-what-s-changed}

##### バグ修正 {#v0.2.4-bugs-squashed}
- `network_idle` 引数を使った後でレスポンスのバイト列を取得する際のバグを修正しました。`StealthyFetcher` と `PlayWrightFetcher` の両方が対象です。<br/>このバグで、次のエラーメッセージが出ていました。

    ```
    Response.body: Protocol error (Network.getResponseBody): No resource with given identifier found
    ```

- PlayWright API は、レスポンスのステータステキストを空で返すことがあります。その場合、`Scrapling` が内部でステータステキストを求めるようにしました。`StealthyFetcher` と `PlayWrightFetcher` の両方が対象です。

## [v0.2.3](https://github.com/D4Vinci/Scrapling/releases/tag/v0.2.3) - 2024-11-19 {#v0.2.3}

### 変更内容 {#v0.2.3-what-s-changed}

##### バグ修正 {#v0.2.3-bugs-squashed}
- pip でのインストールに関するバグを修正しました。このバグで、PlayWright Fetcher のステルスモードがまったく動作しなくなっていました。

## [v0.2.2](https://github.com/D4Vinci/Scrapling/releases/tag/v0.2.2) - 2024-11-16 {#v0.2.2}

### 変更内容 {#v0.2.2-what-s-changed}
##### 新機能 {#v0.2.2-new-features}
- 作成する `Adaptor` オブジェクトに引数を渡さず、既定値を使いたい場合は、代わりに次のインポートでコードを簡潔にできます。

    ```python
    >> from scrapling.default import Fetcher, StealthyFetcher, PlayWrightFetcher
    >> page = Fetcher.get('https://example.com', stealthy_headers=True)
    ```

    それ以外の場合

    ```python
    >> from scrapling import Fetcher, StealthyFetcher, PlayWrightFetcher
    >> page = Fetcher(auto_match=False).get('https://example.com', stealthy_headers=True)
    ```

##### バグ修正 {#v0.2.2-bugs-squashed}
1. `Response` オブジェクトのバグを修正しました。昨日のパッチ v0.2.1 で入り、一部の入れ子の選択や解析で起きていた問題です。

## [v0.2.1](https://github.com/D4Vinci/Scrapling/releases/tag/v0.2.1) - 2024-11-15 {#v0.2.1}

### 変更内容 {#v0.2.1-what-s-changed}
##### 新機能 {#v0.2.1-new-features}
1. すべての Fetcher が返す `Response` オブジェクトが、`Adaptor` オブジェクトと同じように使えるようになりました。ただし、`status`、`reason`、`cookies`、`headers`、`request_headers` 属性が追加されています。`cookies`、`headers`、`request_headers` は常に `dictionary` 型です。<br/>そのため、次のように書けます。

    ```python
    >> from scrapling import Fetcher
    >> page = Fetcher().get('https://example.com', stealthy_headers=True)
    >> print(page.status)
    200
    >> products = page.css('.product')
    ```

    以前の書き方はこちらです。

    ```python
    >> from scrapling import Fetcher
    >> fetcher = Fetcher().get('https://example.com', stealthy_headers=True)
    >> print(fetcher.status)
    200
    >> page = fetcher.adaptor
    >> products = page.css('.product')
    ```

    ただし、後方互換性のために `.adaptor` プロパティは引き続き使えます。

2. `StealthyFetcher` と `PlayWrightFetcher` の両方で、取得メソッドに `proxy` 引数を渡せるようになりました。文字列か辞書を受け付けます。
3. `StealthyFetcher` クラスに `os_randomize` 引数を追加し、`fetch` メソッドで使えるようにしました。有効にすると、Scrapling が OS のフィンガープリントをランダムに選びます。既定では現在の OS に合わせます。

##### バグ修正 {#v0.2.1-bugs-squashed}
1. `Fetcher` クラスでヘッダーを渡す際に起きるバグを修正しました。
2. Fetcher クラスが渡す JSON レスポンスを解析する際のバグを修正しました。

##### 使いやすさの改善 {#v0.2.1-quality-of-life-changes}
1. テキストを返す前に HTML コメントを削除しようとしていましたが、一部のケースでエラーが起き、コードも必要以上に複雑になっていました。そのため、lxml の既定の動作に戻しました。**セレクターなど、要素のテキストを使う処理が少し速くなります**。lxml/parsel/scrapy 特有の分かりにくいテキスト分割を避けるため、テキストを返す前に HTML コメントを削除したい場合は、`keep_comments` 引数を既定の True のままにしてください。

## [v0.2](https://github.com/D4Vinci/Scrapling/releases/tag/v0.2) - 2024-11-11 {#v0.2}

### 変更内容 {#v0.2-what-s-changed}
##### 新機能 {#v0.2-new-features}
1. `Fetchers` 機能を追加しました。3 種類の主なクラスで、豊富なオプションを使って Scrapling にページを取得させられます！
    - `Fetcher` クラスは、基本的な HTTP リクエストを行います。
    - `StealthyFetcher` クラスは、[ステルス用に修正した Firefox](https://github.com/daijro/camoufox) を使う、完全なステルス機能付きの Fetcher です。
    - `PlayWrightFetcher` クラスは、通常の PlayWright、私が作ったステルスモード付きの PlayWright、CDP 経由の実際のブラウザ、[NSTBrowser](https://app.nstbrowser.io/r/1vO5e5) の [docker browserless](https://hub.docker.com/r/nstbrowser/browserless) で、ブラウザによるリクエストを行えます！
2. 新しい `find_all`/`find` メソッドを追加しました。魔法のように、ページの要素を簡単に探せます！
3. `filter` と `search` メソッドを `Adaptors` クラスに追加しました。複数の `Adaptor` オブジェクトをまとめて操作しやすくなります。
4. 使いやすくするために、`css_first` と `xpath_first` メソッドを追加しました。
5. 新しい `TextHandlers` クラスを追加しました。`TextHandler` オブジェクトをまとめて操作するためのもので、`Adaptors` クラスと同様に使えます。
6. `generate_full_css_selector` と `generate_full_xpath_selector` メソッドを追加しました。

##### バグ修正 {#v0.2-bugs-squashed}
1. `Adaptors` クラスの `re_first` が、内部のすべての `Adaptor` オブジェクトから最初に一致した結果を返すようになりました。以前は誤って、`re_first` の結果をすべての `Adaptor` オブジェクトから返していました。
2. 選択した要素からテキストを返す場合（CSS の `::text` 関数など）、`.css` や `.xpath` などのメソッドで `Adaptor` オブジェクトが返すのは、文字列のリストではなく `TextHandlers` になりました。そのため、`page.css('something::text').re_first(r'regex_pattern').json()` と書けます。以前の `page.css('something::text')[0].re_first(r'regex_pattern').json()` は不要です。
3. `Adaptor`/`Adaptors` の re/re_first の引数を、`TextHandler` と統一しました。`clean_match` と `case_sensitive` 引数を使えます。
4. `auto_match` 引数は `Adaptor` の初期化時に既定で有効になりました。ただし、実際に使うには、要素を選ぶときにも有効にする必要があります。（バグ修正ではなく、設計上の判断です。）
5. 多くの場所で型注釈を修正し、Scrapling でコードを書くときの自動補完を改善しました。

##### 使いやすさの改善 {#v0.2-quality-of-life-changes}
1. `css_selector` と `xpath_selector` を `generate_css_selector` と `generate_xpath_selector` に改名しました。名前を分かりやすくし、コード入力中の自動補完を妨げないようにするためです。
2. 既存コードの多くを `core` サブパッケージに整理し、ほかの設計も見直しました。コードを分かりやすくし、今後の保守を簡単にするためです。
3. テストフォルダーを分かりやすい構成に整理し、新機能のテストを追加しました。GitHub 上で tox 環境をキャッシュするようにして、各コミットの自動テストも高速化しました。

## [v0.1.2](https://github.com/D4Vinci/Scrapling/releases/tag/v0.1.2) - 2024-10-16 {#v0.1.2}

**変更履歴**：

- `keep_comments` 引数が想定どおりに動作しないバグを修正しました。
- テキストを抽出する前に要素から HTML コメントを自動で削除し、Lxml の異なる動作を避けるようにしました。たとえば、次の例です。

    ```python
    >>> page = Adaptor('<span>CONDITION: <!-- -->Excellent</span>', keep_comments=True)
    >>> page.css('span::text')
    ['CONDITION: ', 'Excellent']
    ```

    以前は Lxml の既定の動作によって上の結果になっていましたが、現在は完全なテキスト 'CONDITION: Excellent' を返します。
    parsel\scrapy にも同じ動作があるため、ここで対処したいと考えました。

- `pip uninstall scrapling` などを実行しても、ライブラリが作成した SQLite データベースのファイルが削除されないバグを修正しました。

## [v0.1.1](https://github.com/D4Vinci/Scrapling/releases/tag/v0.1.1) - 2024-10-14 {#v0.1.1}

小さな修正

## [v0.1](https://github.com/D4Vinci/Scrapling/releases/tag/v0.1) - 2024-10-13 {#v0.1}

**すべての変更履歴**：<https://github.com/D4Vinci/Scrapling/commits/v0.1>
