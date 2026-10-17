---
title: "StealthyFetcher で JavaScript サイトをスクレイピングする"
description: "Scrapling のブラウザセッションでページを描画し、データを待ち、ログイン状態を再利用し、バックグラウンドの API レスポンスを読み取ります。プロキシやボット対策のチャレンジへの対応も設定できます。"
---

# StealthyFetcher でブラウザから取得する {#browser-fetching-with-stealthyfetcher}

`StealthyFetcher` クラスは JavaScript ページを読み込み、ボット対策への対応機能を使って Chromium や Google Chrome を自動操作します。ステルス用の修正を加えた [Playwright の API](https://playwright.dev/python/docs/intro) を使います。

後で説明するページの自動操作には、[Playwright の Page API](https://playwright.dev/python/docs/api/class-page) の知識が必要です。

!!! success "前提条件"

    1. [Fetcher の基本](../fetching/choosing.md)を読み、[Response オブジェクト](../fetching/choosing.md#response-object)と Fetcher の選び方を理解していること。
    2. [要素の検索](../parsing/selection.md)を読み、[Selector](../parsing/main_classes.md#selector)/[Response](../fetching/choosing.md#response-object) オブジェクトから要素を探して抽出する方法を理解していること。
    3. [主なクラス](../parsing/main_classes.md)を読み、[Response](../fetching/choosing.md#response-object) クラスが [Selector](../parsing/main_classes.md#selector) クラスから引き継ぐプロパティとメソッドを理解していること。

## 基本的な使い方 {#basic-usage}
この Fetcher の基本のインポート方法は、ほかの Fetcher と同じです。

```python
from scrapling.fetchers import StealthyFetcher
```
解析オプションの設定方法は[こちら](choosing.md#parser-configuration-in-all-fetchers)を参照してください。

ここからは、主な引数を例とともに説明します。すべての引数を一覧で確認したい場合は、[こちら](#full-list-of-arguments)に進んでください。

!!! abstract "概要"

    `fetch` メソッドの非同期版は `async_fetch` です。


この Fetcher には、現在、主に 3 つの実行方法があります。必要に応じて組み合わせられます。

次の方法があります。

### 1. 付属の Chromium {#1-bundled-chromium}
```python
StealthyFetcher.fetch('https://example.com')
```
既定のステルス設定で付属の Chromium ブラウザを開き、ページを読み込みます。

### 2. インストール済みの Chrome {#2-real-chrome}
```python
StealthyFetcher.fetch('https://example.com', real_chrome=True)
```
Google Chrome がインストールされている場合は、このオプションを使えます。最初の方法と同じですが、Chromium の代わりに端末上の Google Chrome を使います。リクエストが通常のブラウザからのものに近づき、検出されにくくなります。

Google Chrome が未インストールの場合は、手動でインストールする代わりに、次のコマンドをターミナルで実行してライブラリ用にインストールできます。
```commandline
playwright install chrome
```

### 3. CDP 接続 {#3-cdp-connection}
```python
StealthyFetcher.fetch('https://example.com', cdp_url='ws://localhost:9222')
```
ローカルで Chromium や Google Chrome を起動する代わりに、[Chrome DevTools Protocol](https://chromedevtools.github.io/devtools-protocol/) を通じてリモートのブラウザに接続できます。

URL には、ブラウザサービスから提供される WebSocket エンドポイント（`ws://`/`wss://`）、またはブラウザの HTTP エンドポイント（例：`http://localhost:9222`）を使えます。


## どのような機能がありますか？ {#what-does-it-do}

StealthyFetcher は次のボット対策への対応機能を備えています。

1. `solve_cloudflare=True` で、Cloudflare のあらゆる Turnstile/Interstitial チャレンジを自動で解決します。
2. CDP ランタイムや WebRTC からの情報漏えいを防ぎます。
3. JavaScript の実行環境を分離し、多くの Playwright のフィンガープリントを除去します。ボットに特有の既知の動作による検出も防ぎます。
4. Canvas にノイズを加え、Canvas によるフィンガープリントの取得を防ぎます。
5. ヘッドレスモードを検出する既知の方法に自動で対処します。タイムゾーンの不一致による検出に対応するオプションもあります。
6. そのほかにも、ボット対策に対応するオプションがあります。

## 引数の一覧 {#full-list-of-arguments}
Scrapling は、この Fetcher とセッションクラスに多くのオプションを用意しています。[例](#examples)に進む前に、引数の一覧を示します。


| 引数 | 説明 | 省略可能 |
|:---------------------:|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|:--------:|
| url | 対象の URL。 | ❌ |
| headless | `True` でブラウザを非表示のヘッドレスモード（**既定**）で実行します。`False` ではブラウザを表示します。 | ✔️ |
| disable_resources | 不要なリソースへのリクエストを省いて速度を上げます。対象は `font`、`image`、`media`、`beacon`、`object`、`imageset`、`texttrack`、`websocket`、`csp_report`、`stylesheet` です。 | ✔️ |
| cookies | 次のリクエストに使う Cookie を設定します。 | ✔️ |
| useragent | 使用する User-Agent 文字列を指定します。**指定しない場合、Fetcher は同じブラウザとバージョンの実際の User-Agent を生成して使います。** | ✔️ |
| network_idle | ネットワーク接続が少なくとも 500 ミリ秒間なくなるまで待ちます。 | ✔️ |
| load_dom | 既定で有効です。ページ上の JavaScript がすべて読み込まれて実行されるまで（`domcontentloaded` 状態になるまで）待ちます。 | ✔️ |
| pierce_shadow | オープンな Shadow DOM の内容をレスポンスの HTML に含めます。既定値は `False` です。セッション全体に設定でき、リクエストごとに上書きできます。 | ✔️ |
| timeout | ページ上のすべての操作と待機に使うタイムアウト（ミリ秒）です。既定値は 30,000 ミリ秒（30 秒）です。 | ✔️ |
| wait | すべての処理が終わってからページを閉じて `Response` オブジェクトを返すまでの待機時間（ミリ秒）です。 | ✔️ |
| page_action | 自動操作のための引数です。`page` オブジェクトを受け取り、ページ移動後に必要な操作を行う関数を渡します。 | ✔️ |
| page_setup | `page` オブジェクトを受け取り、ページ移動前に実行する関数です。ページの読み込み前に必要なイベントリスナーやルートを登録するために使います。 | ✔️ |
| wait_selector | 指定した CSS セレクターの要素が、指定した状態になるまで待ちます。 | ✔️ |
| init_script | このセッションの各ページを作成するときに実行する JavaScript ファイルの絶対パスです。 | ✔️ |
| wait_selector_state | `wait_selector` で指定したセレクターの要素が、この状態になるまで待ちます。 _既定の状態は `attached` です。_ | ✔️ |
| google_search | 既定で有効です。Scrapling が Google の Referer ヘッダーを設定します。 | ✔️ |
| extra_headers | リクエストに追加するヘッダーの辞書です。 _`google_search` と併用すると、そちらが設定する Referer が、ここで設定する Referer より優先されます。_ | ✔️ |
| proxy | リクエストに使うプロキシです。文字列、または 'server'、'username'、'password' のキーだけを含む辞書で指定できます。 | ✔️ |
| real_chrome | 端末に Chrome がインストールされている場合に有効にすると、Fetcher がそのブラウザを起動して使います。 | ✔️ |
| locale | `en-GB`、`de-DE` などのロケールを指定します。`navigator.language`、リクエストの `Accept-Language` ヘッダー、数値と日付の表示形式に影響します。既定ではシステムのロケールを使います。 | ✔️ |
| timezone_id | ブラウザのタイムゾーンを変更します。既定ではシステムのタイムゾーンを使います。 | ✔️ |
| cdp_url | 新しいブラウザを起動する代わりに、この CDP URL に接続してブラウザを操作します。 | ✔️ |
| user_data_dir | Cookie やローカルストレージなどのブラウザセッションデータを保存するユーザーデータディレクトリのパスです。既定では一時ディレクトリを作成します。**セッションでのみ使えます。** | ✔️ |
| extra_flags | 起動時にブラウザへ渡す追加フラグのリストです。 | ✔️ |
| solve_cloudflare | 有効にすると、Fetcher は Cloudflare のあらゆる Turnstile/Interstitial チャレンジを解決してからレスポンスを返します。既定値は `False` です。 | ✔️ |
| block_webrtc | WebRTC にプロキシ設定を適用し、ローカル IP アドレスの漏えいを防ぎます。 | ✔️ |
| hide_canvas | Canvas の操作にランダムなノイズを加え、フィンガープリントの取得を防ぎます。 | ✔️ |
| allow_webgl | 既定で有効です。無効にすると WebGL と WebGL 2.0 が完全に無効になります。多くの WAF が WebGL の有効状態を調べるため、無効化は推奨しません。 | ✔️ |
| additional_args | Playwright のコンテキストに渡す追加設定です。Scrapling の設定より優先されます。 | ✔️ |
| selector_config | 最終的な `Selector`/`Response` クラスの作成時に使う解析オプションの辞書です。 | ✔️ |
| blocked_domains | リクエストをブロックするドメイン名の集合です。サブドメインも対象です。たとえば `"example.com"` は `"sub.example.com"` もブロックします。 | ✔️ |
| block_ads | 既知の広告・追跡ドメイン約 3,500 件へのリクエストをブロックします。`blocked_domains` と併用できます。 | ✔️ |
| dns_over_https | DNS クエリを Cloudflare の DNS-over-HTTPS に通し、プロキシの使用時に DNS の漏えいを防ぎます。 | ✔️ |
| proxy_rotator | 自動でプロキシを切り替える `ProxyRotator` インスタンスです。`proxy` と併用できません。 | ✔️ |
| retries | リクエスト失敗時の再試行回数です。既定値は 3 です。 | ✔️ |
| retry_delay | 再試行の間に待つ秒数です。既定値は 1 です。 | ✔️ |
| record_requests | 完了したリクエストと保存済みのレスポンスを `session.network` に保持します。セッション専用で、既定値は `False` です。 | ✔️ |
| max_recorded_requests | セッションごとに保持するリクエストの最大件数です。既定値は 1,000 です。保存する本文には固定のサイズ制限もあります。 | ✔️ |
| executable_path | 付属の Chromium の代わりに使うブラウザ実行ファイルの絶対パスです。標準とは異なるインストール先や、独自ビルドのブラウザを使う場合に役立ちます。 | ✔️ |

セッションクラスでは、これらの引数をセッション全体に設定できます。また、タブ単位で設定できる引数を渡すと、リクエストごとに設定を変えられます。対象は `google_search`、`timeout`、`wait`、`page_action`、`page_setup`、`extra_headers`、`disable_resources`、`wait_selector`、`wait_selector_state`、`network_idle`、`load_dom`、`pierce_shadow`、`solve_cloudflare`、`blocked_domains`、`proxy`、`selector_config` などです。

!!! note "補足"

    1. 私のテストでは、`disable_resources` によって一部のサイトでリクエストが約 25% 速くなりました。プロキシの通信量も減らせます。ただし、サイトによっては読み込みが終わらなくなることがあるため、注意してください。
    2. `google_search` はすべてのリクエストで既定で有効です。Referer を `https://www.google.com/` に設定します。`extra_headers` と併用すると、そちらで設定した Referer より優先されます。
    3. User-Agent を指定せずにヘッドレスモードを有効にすると、Fetcher が同じブラウザバージョンの実際の User-Agent を生成して使います。User-Agent を指定せず、ヘッドレスモードも有効にしない場合は、ブラウザの既定の User-Agent を使います。最近のバージョンでは、これは通常のブラウザと同じ値です。
    4. `init_script` はブラウザコンテキストに登録され、ページ作成時に実行されます。ステルスモードでは、既定で Patchright の分離された実行コンテキストを使います。スクリプトが `window` に設定したグローバル変数を `page_action` で読む場合は、その関数内で `page.evaluate(..., isolated_context=False)` を呼び出してください。

## セッションの管理 {#session-management}

同じ設定で複数のリクエストを行う間、ブラウザを開いたままにするには、`StealthySession`/`AsyncStealthySession` クラスを使います。これらのクラスは `fetch` 関数と同じ引数を受け取るため、セッション全体の設定を指定できます。

```python
from scrapling.fetchers import StealthySession


with StealthySession(
    headless=True,
    disable_resources=True,
    real_chrome=True
) as session:

    page1 = session.fetch('https://example1.com')
    page2 = session.fetch('https://example2.com')
    page3 = session.fetch('https://dynamic-site.com')


```

### 非同期セッションの使い方 {#async-session-usage}

```python
import asyncio
from scrapling.fetchers import AsyncStealthySession

async def scrape_multiple_sites():
    async with AsyncStealthySession(
        network_idle=True,
        timeout=30000,
        max_pages=3
    ) as session:

        pages = await asyncio.gather(
            session.fetch('https://spa-app1.com'),
            session.fetch('https://spa-app2.com'),
            session.fetch('https://dynamic-content.com')
        )
        return pages
```

`max_pages` 引数に気づいたかもしれません。この引数は、Fetcher が再利用する**ブラウザのタブのプール**を設定し、同時に開けるタブの数を制限します。リクエストが終わってもタブは開いたままです。各リクエストでは、次の処理を行います。

1. 空いているタブがあれば再利用します。各リクエストは、割り当てられたタブに独自のタブ単位の設定（`timeout`、`extra_headers`、`disable_resources`、`blocked_domains` など）を適用するため、前のリクエストの設定が残りません。
2. 空きがなく、開いているタブの数が `max_pages` 未満なら、新しいタブを開きます。
3. それ以外の場合は、1 秒未満の間隔で空きタブを確認し、60 秒待っても空きがなければ `TimeoutError` を発生させます。取得先のサイトが応答しなくなると、この状態になることがあります。

エラーが起きたタブは閉じて置き換えます。`session.close_pages()` を使えば、いつでも開いているタブをすべて閉じられます。その後のリクエストで新しいタブを開きます。

この仕組みにより、同じブラウザで複数の URL を同時に取得できます。リソースを大きく節約でき、何より高速です :)

タブが開いたままなので、取得したページは次のリクエストまで残ります。次のリクエストの `page_setup` 関数は、別のページへ移動する前にそのページ上で動きます。これにより、複数のリクエストにまたがる自動操作をつなげられます。

バージョン 0.3.2 から 0.4.14 までは、タブの再利用で前の設定が残る問題があったため、リクエストごとにタブを閉じていました。0.4.15 以降は再利用のたびに設定をリセットするため、タブを開いたままにできます。

### セッション状態の保存と読み込み {#save-and-load-session-state}

`save_state(path)` で Cookie、ローカルストレージ、IndexedDB を JSON ファイルに保存します。`load_state(path)` で別のセッションに復元するか、現在のセッションの保存状態を置き換えます。どちらも文字列または `pathlib.Path` を受け取り、`None` を返します。形式は Playwright のストレージ状態ファイルと互換性があります。

```python
from scrapling.fetchers import StealthySession

with StealthySession() as session:
    session.fetch('https://example.com')
    session.save_state('state.json')

with StealthySession() as session:
    session.load_state('state.json')
    page = session.fetch('https://example.com')
```

ログインなどのブラウザ操作が終わってから保存してください。どちらのメソッドも、開始済みのセッション内で、処理中の取得がすべて終わってから呼び出します。読み込み時には、既存の Cookie、ローカルストレージ、IndexedDB を置き換えます。復元したログイン状態を使うには、ページを取得するか再読み込みしてください。読み込み自体は既存のタブを移動しません。

`AsyncStealthySession` では `await` を使います。

```python
from scrapling.fetchers import AsyncStealthySession

async def restore_session():
    async with AsyncStealthySession() as session:
        await session.load_state('state.json')
        page = await session.fetch('https://example.com')
        await session.save_state('state.json')
        return page
```

これらのメソッドは、共有ブラウザコンテキストだけを保存・復元します。リクエストごとの一時的なプロキシコンテキストには影響しません。`proxy_rotator` を使うセッションには共有コンテキストがないため、`RuntimeError` が発生します。セッションに固定の `proxy` を設定した場合は通常どおり動作します。

ファイルには `sessionStorage`、開いているタブ、ブラウザ設定は含まれません。保存時にはファイルを上書きします。親ディレクトリは事前に作成してください。ファイルや JSON のエラーは呼び出し元に伝わります。

### セッションの利点 {#session-benefits}

- **ブラウザの再利用**：同じブラウザを使うため、2 回目以降のリクエストが大幅に速くなります。
- **Cookie の保持**：通常のブラウザと同じように、Cookie とセッション状態を自動で扱います。
- **一定のフィンガープリント**：すべてのリクエストで同じブラウザのフィンガープリントを使います。
- **メモリの効率**：取得のたびに新しいブラウザを起動するより、リソースを効率よく使えます。


## 使用例 {#examples}
例を見るとわかりやすいので、実際に見てみましょう。

### リソースの制御 {#resource-control}

```python

page = StealthyFetcher.fetch('https://example.com', disable_resources=True)
```

### Shadow DOM {#shadow-dom}

ページによっては、通常の HTML に含まれない、オープンな Shadow Root の中に内容があります。`pierce_shadow` を有効にすると、その内容をレスポンスに含められます。その後は通常どおり CSS や XPath セレクターを使えます。

```python
from scrapling.fetchers import StealthyFetcher

page = StealthyFetcher.fetch('https://example.com', pierce_shadow=True)
titles = page.css('product-card .title::text').getall()
```

既定値は `False` です。セッション全体で有効にし、特定のリクエストだけ無効にすることもできます。

```python
from scrapling.fetchers import StealthySession

with StealthySession(pierce_shadow=True) as session:
    page = session.fetch('https://example.com')
    plain_page = session.fetch('https://example.com', pierce_shadow=False)
```

同じオプションを `async_fetch` と非同期セッションでも使えます。

対象はオープンな Shadow Root だけです。クローズドな Shadow Rootや iframe 内のドキュメントはたどりません。コンポーネントがページより後に読み込まれる場合は、`wait_selector` を使ってください。

各オープン Shadow Rootは、レスポンス内で `<shadow-root>` ラッパーになります。スロットはタグと属性を保ち、割り当てられたノードを含みます。割り当てがなければ代替の内容を含みます。割り当てられていない Light DOM の子要素は省きます。ブラウザ上のページは変わりません。

```html
<product-card>
  <shadow-root>
    <div class="title">Product name</div>
    <slot name="price"><span class="price">20</span></slot>
  </shadow-root>
</product-card>
```

子孫セレクターは、これらの要素をまたいで使えます。直接の子を選ぶセレクターには、ラッパーとスロットを含める必要があります。

```python
titles = page.css('product-card .title::text').getall()
titles = page.css('product-card > shadow-root > .title::text').getall()
prices = page.css('product-card > shadow-root > slot[name="price"] > .price::text').getall()
```

ラッパーとスロットは、XPath のパス、`.children`、`response.body`、HTML 出力に現れます。Markdown とテキストの抽出では、タグを表示せずに内容だけを返します。非表示のスロットの属性は残るため、内容を整理する処理で使えます。

スナップショットは内容の順序を保ちますが、CSS による表示状態やレイアウトは計算しません。`<shadow-root>` を含むセレクターは、ブラウザ上のページではなく Scrapling のレスポンスに適用します。ほかの HTML パーサーでは、通常と異なる入れ子構造の扱いが違う場合があります。

### ドメインのブロック {#domain-blocking}

```python

page = StealthyFetcher.fetch('https://example.com', blocked_domains={"ads.example.com", "tracker.net"})
```

### ネットワークの制御 {#network-control}

```python

page = StealthyFetcher.fetch('https://example.com', network_idle=True)


page = StealthyFetcher.fetch('https://example.com', timeout=30000)


page = StealthyFetcher.fetch('https://example.com', proxy='http://username:password@host:port')
```

### ファイルのダウンロード {#downloading-files}

```python
page = StealthyFetcher.fetch('https://raw.githubusercontent.com/D4Vinci/Scrapling/main/docs/assets/main_cover.png')

with open(file='main_cover.png', mode='wb') as f:
    f.write(page.body)
```

`Response` オブジェクトの `body` 属性は、常に `bytes` を返します。

### ページ移動前の準備 {#pre-navigation-setup}
ページ移動前にイベントリスナー、ルート、スクリプトを登録する必要がある場合は、`page_setup` を使います。この関数は `page` オブジェクトを受け取り、`page.goto()` の呼び出し前に実行されます。

```python
from patchright.sync_api import Page

def capture_websockets(page: Page):
    page.on("websocket", lambda ws: print(f"WebSocket opened: {ws.url}"))

page = StealthyFetcher.fetch('https://example.com', page_setup=capture_websockets)
```
非同期版です。
```python
from patchright.async_api import Page

async def capture_websockets(page: Page):
    page.on("websocket", lambda ws: print(f"WebSocket opened: {ws.url}"))

page = await StealthyFetcher.async_fetch('https://example.com', page_setup=capture_websockets)
```

`page_action` と組み合わせられます。`page_setup` はページ移動前に、`page_action` は移動後に実行されます。

### Cloudflare とステルスのオプション {#cloudflare-and-stealth-options}

```python

page = StealthyFetcher.fetch('https://nopecha.com/demo/cloudflare', solve_cloudflare=True)


page = StealthyFetcher.fetch(
    'https://protected-site.com',
    solve_cloudflare=True,
    block_webrtc=True,
    real_chrome=True,
    hide_canvas=True,
    google_search=True,
    proxy='http://username:password@host:port',  # It can also be a dictionary with only the keys 'server', 'username', and 'password'.
)
```

`solve_cloudflare` を有効にすると、Cloudflare のあらゆる Turnstile/Interstitial チャレンジを自動で検出し、解決します。

- JavaScript チャレンジ（マネージド）
- 操作が必要なチャレンジ（確認ボックスのクリック）
- 見えないチャレンジ（バックグラウンドでの自動確認）

CAPTCHA を埋め込んだ独自のページにも対応します。

!!! notes "**重要な補足**"

    1. 独自の実装を使うサイトでは、CAPTCHA の解決後に実際のコンテンツが読み込まれるまで待つため、`wait_selector` が必要な場合があります。できるだけ多くのサイトに対応するようにしていますが、特殊な対応が必要なサイトもあります。
    2. Cloudflare の解決機能を使う場合は、処理時間を確保するため、タイムアウトを少なくとも 60 秒にしてください。
    3. この機能は、プロキシやほかのステルスオプションと組み合わせて使えます。

### ブラウザの自動操作 {#browser-automation}
ここで [Playwright の Page API](https://playwright.dev/python/docs/api/class-page) の知識が役立ちます。渡した関数が Playwright のページオブジェクトを受け取り、必要な操作を行います。その後、Fetcher が処理を続けます。

この関数は、`network_idle` が有効な場合はその待機直後に実行されます。`wait_selector` の待機より前に実行されるため、自動操作以外にも使い、ページを自由に変更できます。

次の例では、ページの[マウスイベント](https://playwright.dev/python/docs/api/class-mouse)を使ってホイールでスクロールし、その後マウスを動かします。
```python
from patchright.sync_api import Page

def scroll_page(page: Page):
    page.mouse.wheel(10, 0)
    page.mouse.move(100, 400)
    page.mouse.up()

page = StealthyFetcher.fetch('https://example.com', page_action=scroll_page)
```
非同期版の取得メソッドを使う場合は、関数も非同期にしてください。
```python
from patchright.async_api import Page

async def scroll_page(page: Page):
   await page.mouse.wheel(10, 0)
   await page.mouse.move(100, 400)
   await page.mouse.up()

page = await StealthyFetcher.async_fetch('https://example.com', page_action=scroll_page)
```

### 待機条件 {#wait-conditions}

```python

page = StealthyFetcher.fetch(
    'https://quotes.toscrape.com/js-delayed/',
    wait_selector='.quote',
    wait_selector_state='visible'
)
```
有効にした場合、レスポンスを返す前に行う最後の待機です。`wait_selector` に CSS セレクターを渡すと、`wait_selector_state` で指定した状態になるまで待ちます。状態を指定しなければ、既定の `attached` を使い、要素が DOM に存在するまで待ちます。

その後、`load_dom` が有効（既定）なら、すべての JavaScript ファイルの読み込みと実行が終わったか（`domcontentloaded` 状態か）を再確認し、必要なら待機を続けます。`network_idle` も有効なら、前述のとおり `network_idle` の条件を再び満たすまで待ちます。

待機できる状態は次のとおりです（[参照元](https://playwright.dev/python/docs/api/class-page#page-wait-for-selector)）。

- `attached`：要素が DOM に存在するまで待ちます。
- `detached`：要素が DOM に存在しなくなるまで待ちます。
- `visible`：要素のバウンディングボックスが空でなく、`visibility:hidden` が設定されていない状態を待ちます。内容がない要素や `display:none` の要素はバウンディングボックスが空なので、表示されているとは見なしません。
- `hidden`：要素が DOM から外れるか、バウンディングボックスが空になるか、`visibility:hidden` が設定されるまで待ちます。`'visible'` の反対です。

### ネットワーク履歴 {#network-history}

ブラウザセッションで `record_requests` を有効にすると、ページの読み込み、自動操作、複数のタブにまたがる完了済みリクエストを確認できます。一時的なプロキシコンテキストも含むセッション全体の履歴を保存し、レスポンスを Scrapling の `Response` オブジェクトとして保持します。リクエストを再送せずに API 呼び出し、HTTP エラー、リダイレクトを探せます。セッションを閉じた後も、保存済みのヘッダーと本文を読めます。失敗したリクエストと未完了のリクエストは省きますが、完了した HTTP 4xx・5xx レスポンスは含めます。

```python
from scrapling.fetchers import StealthySession

with StealthySession(record_requests=True, max_recorded_requests=1000) as session:
    session.fetch('https://example.com', network_idle=True)

for response in session.network.search(resource_type='document', limit=None):
    print(response.meta['network_id'], response.url, response.status)
    if note := response.meta.get('body_note'):
        print(note)
    else:
        print(response.body)
        print(response.css('title::text').get())

session.network.clear()
```

同じ API を `AsyncStealthySession` でも使えます。記録は既定で無効です。セッションの作成時に `record_requests=True` を設定し、必要なら `max_recorded_requests` も設定します。

- `session.network.search(url_pattern=None, method=None, resource_type=None, status=None, after_id=0, limit=100, include_static=True)` は、保存済みの `Response` オブジェクトをネットワーク ID の順で返します。`limit=None` は保持している一致結果をすべて返します。`url_pattern` は検索時に適用する正規表現で、不正なパターンはその時点でエラーになります。`after_id` は、それより大きいネットワーク ID のレスポンスを選びます。`include_static=False` では XHR/fetch リクエストと HTTP エラーだけを対象にします。すべてのリソース種別と保存済みリダイレクトを含めるには `True` を使います。
- `session.network.get(request_id)` は、保存済みの `Response` を 1 件返します。すでに保持されていなければ `None` を返します。
- `session.network.clear()` は履歴を削除します。リクエスト ID は増え続け、再利用されません。

保存済みの各 `Response` では、`.url`、`.method`、`.status`、`.headers`、`.request_headers`、`.body` のバイト列、`.json()`、CSS/XPath メソッドを直接使えます。`.meta` には `network_id`、`resource_type`、`request_body`（バイト列または `None`）が入ります。ヘッダー全体の読み取りに失敗すると、一部だけになる場合があります。非同期セッションでも、これらはローカルの読み取りです。await したり、`.body()` を呼び出したりしないでください。保存した内容を解析できない場合もバイト列は保持しますが、CSS/XPath メソッドは空のドキュメントを使います。

URL で API の通信を探すには、`session.network.search(url_pattern=r'https://api\.example\.com/.*', limit=None)` を使います。特定のリクエスト種別だけが必要なら、`resource_type='fetch'` または `resource_type='xhr'` を追加します。

記録機能が読み取り、保存する本文は、対応するテキストの `Content-Type` に限られます。対象は `text/*`、`+json`/`+xml` 型（SVG を含む）、JSON、XML、JavaScript、GraphQL、URL エンコードされたフォームデータです。バイナリ型、未対応の型、`Content-Type` がないレスポンスでは、メタデータだけを保持し、本文のバイト列は保存しません。ブラウザによるリソースの読み込みは通常どおり行われます。

保存するレスポンスのバイト列は Playwright から取得するため、サーバーの元のバイト列とは異なる場合があります。保存したバイト列が有効な UTF-8 なら、Playwright と同じく UTF-8 として扱います。それ以外では、宣言された文字コードを使います。レスポンスヘッダーは変更しません。

省略された本文、サイズ制限を超えた本文、読み取れない本文は `b''` を返し、理由を `response.meta.get('body_note')` に記録します。テキスト以外の本文では `Non-text body; not saved.` となります。レスポンスのメタデータと取得できたヘッダーは保持します。空のテキストを含め、保存されたテキストには注記がありません。HEAD レスポンスとステータスコード 204、205、304 は、注記なしで空のままです。

履歴の `search`、`get`、`clear` は、非同期セッションでもローカルで動く同期メソッドです。レスポンスを変換して保存した後にだけ、項目が履歴に現れます。ブラウザのイベントは Playwright が動作中に処理されます。非同期の記録にはイベントループの実行も必要です。履歴の読み取りは、記録の完了を待ちません。

セッションを閉じるときも、記録の完了は待ちません。ページ移動やブラウザコンテキストの終了時に記録中のレスポンスは、省略される場合があります。保存済みのレスポンスは、終了後も読めます。

既定では最大 1,000 件のリクエストを保持します。保存するレスポンス本文には、1 件あたり 1 MiB、合計 20 MiB の制限があります。保持数や容量の上限に達すると、古い記録を削除します。本文の制限は固定で、セッションの設定では変更できません。これらの上限は、保持する項目とレスポンスのバイト列に対するものです。ブラウザの総メモリ、同時に進む記録、一時的な本文全体の読み取り、解析済み HTML、リクエスト本文には適用されません。

#### v5 への移行 {#migrating-in-v5}

`capture_xhr` と `response.captured_xhr` は v5 で削除されました。`record_requests=True` を指定してブラウザセッションを作成し、`session.network.search(url_pattern=..., limit=None)` で読み取ってください。1 回だけ使う Fetcher による API の記録もこの方法に置き換わるため、セッションインスタンスを保持してください。フィルターは、記録時や 1 回の取得にではなく、セッション全体の保存済み履歴に適用します。本文を保存するのは、対応するテキストレスポンスだけです。`search()` は既定で最大 100 件を返します。`limit=None` は履歴の保持上限を変えずに、保持している一致結果をすべて返します。

### ブラウザのヘッダーとロケール {#browser-headers-and-locale}

```python
page = StealthyFetcher.fetch(
    'https://example.com',
    google_search=True,
    useragent='Mozilla/5.0...',
    locale='en-US',
)
```

### 全体の例 {#general-example}
```python
from scrapling.fetchers import StealthyFetcher

def scrape_dynamic_content():

    page = StealthyFetcher.fetch(
        'https://example.com/dynamic',
        network_idle=True,
        wait_selector='.content'
    )


    content = page.css('.content')

    return {
        'title': content.css('h1::text').get(),
        'items': [
            item.text for item in content.css('.item')
        ]
    }
```

### プロキシの切り替え {#proxy-rotation}

```python
from scrapling.fetchers import StealthySession, ProxyRotator


rotator = ProxyRotator([
    "http://proxy1:8080",
    "http://proxy2:8080",
    "http://proxy3:8080",
])


with StealthySession(proxy_rotator=rotator, headless=True) as session:
    page1 = session.fetch('https://example1.com')
    page2 = session.fetch('https://example2.com')


    page3 = session.fetch('https://example3.com', proxy='http://specific-proxy:8080')
```

!!! warning "注意"

    ブラウザを使うすべての Fetcher とセッションは、既定でタブのプールを持つ永続的なブラウザコンテキストを使います。ただし、ブラウザはタブごとにプロキシを設定できません。そのため `ProxyRotator` を使う場合、Fetcher はプロキシごとに別のコンテキストを開き、それぞれに 1 つのタブを作ります。タブの処理が終わると、タブとそのコンテキストの両方を閉じます。

## 使う場面 {#when-to-use}

StealthyFetcher は、次のような場合に使います。

- ボット対策を回避したい場合
- 信頼できるブラウザのフィンガープリントが必要な場合
- JavaScript を完全に実行する必要がある場合
- 自動のステルス機能を使いたい場合
- ブラウザの自動操作が必要な場合
- Cloudflare の保護に対応する場合
