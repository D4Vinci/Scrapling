---
title: "v0.5 への移行"
description: "Scrapling v0.4.15 から v0.5 に移行します。ブラウザのインポート、ネットワーク記録、MCP ツール、CLI コマンド、パーサーの設定、Spider の動作を更新します。"
---

# v0.5 への移行 {#migrating-to-v05}

このガイドでは、**v0.4.15 から v0.5** に移行するときに確認すべき変更を説明します。削除された API、名前が変わったツール、クロール結果や保存ファイルに影響する修正を扱います。

## 移行チェックリスト {#quick-migration-checklist}

| 使用しているもの | 必要な変更 |
| --- | --- |
| `DynamicFetcher`、`DynamicSession`、`AsyncDynamicSession` | 対応するステルスクラスを使います。 |
| `capture_xhr` または `response.captured_xhr` | `record_requests=True` を設定したブラウザセッションと `session.network` を使います。 |
| `keep_cdata` | パーサーと Fetcher の設定から削除します。 |
| `scrapling extract stealthy-fetch` またはシェルの `stealthy_fetch()` | 代わりに `fetch` を使います。 |
| MCP ツール | ツール名、スクリーンショットの呼び出し、セッション作成時のレスポンス処理を更新します。 |
| POST またはクエリパラメーター付きリクエストの後の `response.follow()` | 必要な場合は、メソッド、クエリ、ボディを再度渡します。 |
| 保存済みのクロールチェックポイントやレスポンスキャッシュ | リクエストが変更されたフィンガープリント入力を使う場合は、新しいクロールを始めます。 |
| `robots_txt_obey=True` | robots.txt の取得失敗に対応します。取得に失敗すると、そのドメインのクロールがブロックされるようになりました。 |

## ブラウザでの取得 {#browser-fetching}

### 動的ブラウザクラスを置き換える {#replace-the-dynamic-browser-classes}

Playwright を直接使うブラウザバックエンドは削除されました。ブラウザによる取得はすべて、Patchright ベースのステルスバックエンドを使うようになりました。

| 削除された API | 代わりに使う API |
| --- | --- |
| `scrapling.DynamicFetcher` | `scrapling.StealthyFetcher` |
| `scrapling.fetchers.DynamicFetcher` | `scrapling.fetchers.StealthyFetcher` |
| `scrapling.fetchers.chrome.PlayWrightFetcher` | `scrapling.fetchers.StealthyFetcher` |
| `scrapling.fetchers.DynamicSession` | `scrapling.fetchers.StealthySession` |
| `scrapling.fetchers.AsyncDynamicSession` | `scrapling.fetchers.AsyncStealthySession` |

`scrapling.fetchers.chrome` モジュールと非公開の `_browsers._controllers` モジュールは削除されました。上の公開インポートを使ってください。

**変更前：**

```python
from scrapling.fetchers import DynamicFetcher

page = DynamicFetcher.fetch("https://example.com", headless=True)
```

**変更後：**

```python
from scrapling.fetchers import StealthyFetcher

page = StealthyFetcher.fetch("https://example.com", headless=True)
```

セッションでは、`DynamicSession` を `StealthySession` に、または `AsyncDynamicSession` を `AsyncStealthySession` に置き換えます。Spider の `configure_sessions()` メソッドでも同じ変更を行ってください。`fetch()` と `async with` の使い方は引き続き有効です。

コールバックでブラウザの型をインポートしたり、ブラウザのエラーを捕捉したりする場合は、`playwright.sync_api` を `patchright.sync_api` に、または `playwright.async_api` を `patchright.async_api` に変えてください。対象には `Page`、`Locator`、`Error`、`TimeoutError` が含まれます。

Patchright はデフォルトで、分離されたコンテキスト内で JavaScript を評価します。コールバックがページ自身の JavaScript 変数を読む場合は、`page.evaluate(..., isolated_context=False)` を使ってください。

インポート名だけでなく、ブラウザの動作も変わります。ブラウザのフラグとフィンガープリントの設定を確認してください。Cloudflare の解決には引き続き `solve_cloudflare=True` が必要で、デフォルトでは有効になりません。また、`extra_flags` は組み込みのステルスフラグを置き換えず、追加するようになりました。

現在のオプションは[ブラウザでの取得](fetching/stealthy.md)を参照してください。

### XHR キャプチャをセッションのネットワーク履歴に置き換える {#replace-xhr-capture-with-session-network-history}

`capture_xhr` パラメーターと `Response.captured_xhr` 属性は削除されました。値が `None` でも、このパラメーターを削除してください。単発取得のレスポンスには XHR のリストが付かなくなりました。

`ResponseFactory.from_playwright_response()` または `ResponseFactory.from_async_playwright_response()` を呼ぶ独自の連携コードでも、`xhr_captured` を削除する必要があります。位置引数の順序変更による問題を避けるため、`collect_history` は名前を指定して渡してください。

**変更前：**

```python
from scrapling.fetchers import StealthyFetcher

page = StealthyFetcher.fetch("https://example.com", capture_xhr="/api/")
for response in page.captured_xhr:
    print(response.url, response.body)
```

**変更後：**

```python
from scrapling.fetchers import StealthySession

with StealthySession(record_requests=True) as session:
    page = session.fetch("https://example.com", network_idle=True)
    for response in session.network.search(url_pattern=r"/api/", limit=None):
        print(response.url, response.body)
```

非同期コードでは `AsyncStealthySession` と `await session.fetch(...)` を使います。`session.network` の読み取りに `await` は不要です。

主な違いは次のとおりです。

- セッションの作成時に `record_requests=True` を設定します。取得ごとの設定ではなく、セッションの設定です。
- 履歴は**セッション全体**に属し、タブ、ページの読み込み、操作をまたいで記録されます。範囲を絞る場合は、`after_id`、フィルター、`session.network.clear()` を使ってください。
- 履歴を検索するときは、以前の `capture_xhr` の正規表現を `url_pattern` に渡します。
- `search()` は保存済みの `Response` オブジェクトを返します。`.url`、`.status`、`.headers`、`.body`、`.json()` を直接読めます。記録 ID、リソースの種類、送信したボディは、`response.meta["network_id"]`、`response.meta["resource_type"]`、`response.meta["request_body"]` に入っています。
- Python の履歴は、デフォルトですべてのリソースの種類を含みます。`resource_type="xhr"` または `resource_type="fetch"` で種類を選ぶか、`include_static=False` で XHR/fetch リクエストと HTTP エラーを選んでください。
- `search()` はデフォルトで最大 100 件の一致を返します。保持されている一致をすべて取得するには、`limit=None` を渡します。セッションはデフォルトで最大 1,000 件のリクエストを保持します。`max_recorded_requests` で変更できます。
- 完了したリクエストだけが保存されます。ボディのキャプチャは対応するテキストコンテンツ型に限られ、1 レスポンスあたり 1 MiB、保持するボディデータ全体で 20 MiB が上限です。上限に達すると古い記録が削除される場合があります。ボディが省略された理由は `response.meta.get("body_note")` で確認できます。
- 履歴の読み取りやセッションの終了は、未完了のキャプチャを待ちません。必要なデータがそろってから読んでください。保存済みの Python の履歴は、セッション終了後も読めます。

フィルターと上限は[ネットワーク履歴](fetching/stealthy.md#network-history)を参照してください。

## パーサーの設定 {#parser-settings}

### `keep_cdata` を削除する {#remove-keep_cdata}

`keep_cdata` は `Selector`、Fetcher の設定、`display_config()` が返す設定から削除されました。パーサーの直接呼び出し、`Fetcher.configure(...)`、Fetcher や連携機能に渡す `selector_config` 辞書から削除してください。

**変更前：**

```python
from scrapling import Selector

page = Selector("<p>Hello</p>", keep_cdata=True)
```

**変更後：**

```python
from scrapling import Selector

page = Selector("<p>Hello</p>")
```

代わりの設定はありません。この設定は HTML パーサーの出力に影響していませんでした。パーサーのオプションを位置引数で渡していた場合は、古い `keep_cdata` 引数を削除し、`adaptive` とストレージのオプションを名前付きで渡してください。

## コマンドラインと対話型シェル {#command-line-and-interactive-shell}

### ブラウザのリクエストに `fetch` を使う {#use-fetch-for-browser-requests}

CLI のブラウザコマンドは `scrapling extract fetch` の 1 つになりました。これは `StealthyFetcher` を使います。

**変更前：**

```bash
scrapling extract stealthy-fetch "https://example.com" page.md
```

**変更後：**

```bash
scrapling extract fetch "https://example.com" page.md
```

すでに `scrapling extract fetch` を使っている場合、コマンド名は変わりません。ただし、バックエンドが `DynamicFetcher` から `StealthyFetcher` に変わります。`--solve-cloudflare` などのオプションは、`fetch` のオプションになりました。

`scrapling shell` では、`stealthy_fetch(...)` を `fetch(...)` に置き換えてください。既存のショートカット `fetch(...)` は `StealthyFetcher.fetch` を呼ぶようになりました。動的クラスはシェルの名前空間に追加されなくなりました。

### Markdown とテキストファイルを UTF-8 として読む {#read-markdown-and-text-files-as-utf-8}

抽出コマンドと `Convertor.write_content_to_file()` は、元ページの文字セットにかかわらず、`.md` と `.txt` ファイルを **UTF-8** で書き込むようになりました。元ページのエンコーディングでこれらのファイルを読むコードを更新してください。`.html` の出力は引き続き `page.encoding` を使います。

複数の選択要素から作る Markdown には、要素間に空行が入るようになりました。これは `Response.markdown()` と Markdown ファイルの出力に適用されます。テキストの直接連結に依存していた完全一致の出力比較や保存済みハッシュを更新してください。

## MCP サーバー {#mcp-server}

保存済みのプロンプト、ツールの許可リスト、ラッパー、MCP クライアントのツール定義を更新してください。サーバーを更新した後は、MCP クライアントを再起動または再接続し、現在のツールを読み込ませてください。

### ツール名と一括呼び出しを更新する {#update-tool-names-and-bulk-calls}

| v0.4.15 のツール | v0.5 での代替 |
| --- | --- |
| `fetch`, `stealthy_fetch` | `browser_fetch_once` |
| `open_session` | `browser_open` |
| `session_fetch` | `browser_fetch` |
| `screenshot` | `browser_screenshot` |
| `bulk_fetch`, `bulk_stealthy_fetch` | URL ごとに `browser_fetch_once` を 1 回呼ぶか、開いているセッションで `browser_fetch` を繰り返し呼び出す |
| `bulk_get` | URL ごとに `make_request` または `session_make_request` を 1 回呼び出す |

一括処理ツールはすべて削除されました。単一 URL の取得ツールは、レスポンスのリストではなく、`status`、`content`、`url` を持つ 1 つの `ResponseModel` を返します。`content` 自体は引き続き文字列のリストです。

MCP のブラウザツールはすべてステルスバックエンドを使うようになりました。`browser_open` の呼び出しから `session_type` を削除してください。動的ブラウザは選べなくなりました。結果には `session_type="stealthy"` が含まれます。HTTP セッションは引き続き `open_request_session` を使い、`session_type="static"` を返します。

Python の連携コードも、削除された `BrowserSessionType` のインポートをやめる必要があります。`SessionType` が受け付ける値は `"stealthy"` と `"static"` だけになりました。

同じブラウザセッションの呼び出しはページを共有するため、順番に実行する必要があります。完了したら `close_session` でセッションを閉じてください。

### `list_sessions` で設定を読む {#read-settings-through-list_sessions}

`browser_open` と `open_request_session` が返す内容は、次の項目だけになりました。

```json
{
  "session_id": "my-session",
  "session_type": "stealthy"
}
```

作成結果には `created_at`、`is_alive`、`settings`、`message` が含まれなくなりました。最初の 3 項目は `list_sessions` で取得してください。確認用の `message` は削除されました。`SessionCreatedModel` が `SessionInfo` の全フィールドを持つと想定していたコードも変更が必要です。

### スクリーンショットの前にページを取得する {#fetch-before-taking-a-screenshot}

`browser_screenshot` は、**現在のページを再読み込みせずに撮影**します。URL と、以前の移動・待機オプションである `wait`、`wait_selector`、`wait_selector_state`、`network_idle` は受け付けなくなりました。

次の順序で使ってください。

1. `browser_open` を呼び出します。
2. URL と必要なページ読み込みオプションを指定して `browser_fetch` を呼び出します。
3. 必要に応じて `browser_actions` を呼び、ページを操作したりコンテンツを待ったりします。
4. セッション ID を指定して `browser_screenshot` を呼び出します。
5. 完了したら `close_session` を呼び出します。

たとえば、ページ全体のスクリーンショットの引数は次のとおりです。

```json
{
  "session_id": "my-session",
  "full_page": true
}
```

このツールの `timeout` は、スクリーンショット操作の制限時間になりました。ツールはページを読み込みません。要素のスクリーンショットでは `selector` または `ref` を使い、`full_page=true` は設定しないでください。

スクリーンショットは引き続き画像とテキストのコンテンツブロックを返し、テキストブロックには現在のページ URL が含まれます。取得用の `ResponseModel` は返しません。

完全なスキーマは [MCP ガイド](ai/mcp-server.md)と [API リファレンス](api-reference/mcp-server.md)を参照してください。

## Spider と HTTP リクエスト {#spiders-and-http-requests}

### リンクをたどるときにリクエストデータを再度渡す {#pass-request-data-again-when-following-a-link}

`response.follow()` は、前のリクエストから `method`、`params`、`data`、`json`、`files`、`multipart` をコピーしなくなりました。また、`headers` と `extra_headers` から継承された `Content-Length` ヘッダーも削除します。

リンクをたどるときは、リクエストデータを明示的に渡さない限り、通常の GET リクエストになります。セッション、プロキシ、コールバックなど、ほかの共有設定は既存の継承規則に従います。

古いコードが継承された POST データに依存していた場合は、次のコードを変更してください。

```python
yield response.follow("/next")
```

変更後：

```python
yield response.follow("/next", method="POST", json={"page": 2})
```

次のリクエストで `params` が必要な場合も、明示的に渡してください。新しい `Content-Length` の計算は HTTP クライアントに任せてください。

### リクエストのフィンガープリントと保存済みクロール状態を確認する {#check-request-fingerprints-and-saved-crawl-state}

リクエストのフィンガープリントは、重複リクエストの検出とキャッシュ済みレスポンスの検索に使うキーです。入力の扱いが次の 3 点で変わりました。

- キーを作る前に `params` が URL に統合されます。同じ URL でもクエリパラメーターが異なるリクエストは、デフォルトでは重複と見なされなくなりました。
- `{}`、`[]`、`false`、`0`、`""` などの JSON ボディがキーに保持されます。ボディがない場合と同じキーにはならなくなりました。`None` は引き続き JSON ボディがないことを意味します。
- `fp_include_headers=True` の場合、ヘッダーの挿入順序だけを変えてもキーは変わらなくなりました。

クロールがこれらの入力を使っている場合は、更新前に完了させるか、新しいチェックポイントとレスポンスキャッシュ用ディレクトリで新しいクロールを始めてください。保存済みの古いキーは、新しいキーと異なる場合があります。これはリクエストの識別方法の変更であり、チェックポイントのファイル形式の変更ではありません。

開発モードでは、ブロックされたレスポンスかどうかを確認してからキャッシュに書き込むようになりました。ブロックされたページは、成功した結果としてキャッシュに保存されません。既存のキャッシュファイルは自動で整理されません。以前に認証チャレンジのページを保存した場合は、古い項目を削除してください。

失敗したクロールは、チェックポイントファイルを保持するようになりました。エラー後にこれらのファイルが消えると想定していた場合は、クリーンアップ用コードを確認してください。[一時停止と再開](spiders/advanced.md#pause-resume)と[開発モード](spiders/advanced.md#development-mode)を参照してください。

### robots.txt の取得失敗を確認する {#check-robotstxt-failures}

`robots_txt_obey=True` の場合、robots.txt の取得中の例外や、HTTP 200 または 4xx 以外のレスポンスによって、そのドメインへのリクエストがブロックされるようになりました。以前は、このような失敗でもクロールが許可されていました。HTTP 200 は引き続き規則を提供し、HTTP 4xx は引き続きアクセスを許可します。

結果はクロール全体でキャッシュされます。robots.txt へのアクセス問題を直して、新しいクロールを始めてください。同じクロール内の後続リクエストでは、失敗した取得を再試行しません。デフォルトの `robots_txt_obey=False` は変わりません。

### リンクの制限とサイトマップのコールバックを確認する {#check-link-restrictions-and-sitemap-callbacks}

- `LinkExtractor` の制限に一致するものがない場合、リンクを返さなくなりました。ページ全体に戻って探すことはありません。見つかるリンクが減った場合は、`restrict_css` または `restrict_xpath` の式を修正してください。
- 制限で親要素だけでなく、リンク要素自体も選べるようになりました。以前は見落としていたリンクが追加される場合があります。想定する URL の集合を確認してください。
- 規則がない場合、または一致した規則が `callback=None` の場合、`SitemapSpider` はページ URL を `parse()` に送るようになりました。これらの HTML ページをサイトマップパーサーに戻すことはありません。該当する場合の `parse()` を実装し、以前の振り分けに対する回避策を削除してください。
- robots.txt と CSV フィードの先頭にある Unicode バイトオーダーマークが削除されます。robots の最初の指示が有効になり、CSV の最初の列名が `\ufeff` で始まらなくなりました。独自の `headers` を設定した場合は、代わりに最初のフィールド値からマークが削除されます。この見えない接頭辞に対処していたコードを更新してください。サイトマップの XML コメントと処理命令も、解析エラーの原因になるのではなく、読み飛ばされるようになりました。

### フォームデータ、ヘッダー、CLI の JSON を確認する {#check-form-data-headers-and-cli-json}

辞書形式のフォームデータでは、リストとタプルの値が同じキーの繰り返しに展開されるようになりました。たとえば `data={"tag": ["a", "b"]}` は `tag=a&tag=b` を送信します。空のリストでは、そのキーの項目は送信されません。Content-Type を指定していない場合は、デフォルトの `Content-Type: application/x-www-form-urlencoded` が追加されます。

別の送信形式が必要な場合は、明示的にエンコードした文字列またはバイト列を渡してください。`json`、生の `content`、multipart アップロードは、それぞれのボディ処理を維持します。フォームデータやクエリパラメーターの `None` 値は**削除されません**。文字列 `None` のまま残ります。

リクエストごとの HTTP ヘッダーは、大文字と小文字に関係なくセッションのヘッダーを上書きするようになりました。`authorization` というリクエストヘッダーは、セッションの `Authorization` と両方送信されるのではなく、それを置き換えます。ヘッダー名の重複を回避していたコードを削除してください。

CLI の JSON 値 `{}`、`[]`、`false`、`0`、`""` は、通知なしに省略されず、送信されるようになりました。また、`curl2fetcher()` は curl の `-A` のユーザーエージェントを適用し、`-x` のプロキシを URL 文字列として正しく渡すようになりました。curl で明示した `-H 'User-Agent: ...'` は、引き続き `-A` より優先されます。

## 確認すべきその他の出力変更 {#other-output-changes-to-check}

これらの修正は API を削除しませんが、保存済みの結果や出力の完全一致テストに影響する場合があります。

- 生成される CSS と XPath のセレクターは、同じタグの兄弟要素が複数あるとき、その先頭を特定するために必要なら `:nth-of-type(1)` または `[1]` を含むようになりました。期待するセレクター文字列を更新し、新しい位置指定を削除しないでください。
- AI 向けに整形したコンテンツは、`opacity:0.95` などの値を持つ表示要素を保持するようになりました。また、より多くの形式のインラインスタイルで非表示になった要素や `<slot hidden>` 要素を削除し、一致する不要なタグは入れ子でもすべて削除します。Markdown、テキスト、サニタイズ済み HTML の正確な出力を再確認してください。
- ブラウザレスポンスの変換では、大文字と小文字の違い、空白、引用符付きの値がある charset 宣言も読めるようになりました。たとえば `text/plain; CHARSET = "iso-8859-15"` です。このようなヘッダーを持つ HTML 以外のレスポンスは、UTF-8 に戻るのではなく、宣言されたエンコーディングを使うようになりました。これらのレスポンスからデコードしたテキストを再確認してください。

## 更新結果を確認する {#verify-your-upgrade}

全体の処理を実行する前に、小さなクロールを試してください。抽出データ、たどった URL、送信したリクエストボディ、保存ファイルのエンコーディング、依存しているキャッシュやチェックポイントの動作を確認します。MCP の連携では、ツールへの入力と返されるデータの両方を、現在のスキーマと照合してください。

以前のリリースの変更は[変更履歴](changelog.md)を参照してください。
