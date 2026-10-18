---
title: "Scrapling MCP サーバー：設定とスクレイピングの手順"
description: "AI クライアントを Scrapling に接続し、HTTP やブラウザでスクレイピングします。セッション、ログイン状態、操作、対象を絞った抽出、API 履歴を活用できます。"
---

# Scrapling MCP サーバーの使い方 {#scrapling-mcp-server-guide}

<iframe width="560" height="315" src="https://www.youtube.com/embed/NHwWEiTOoPQ" title="YouTube 動画プレーヤー" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>

**Scrapling MCP サーバー**は、Scrapling の Web スクレイピング機能を、普段使う AI チャットボットや AI エージェントに直接提供します。Claude や MCP 対応のインターフェースで会話しながら、サイトのスクレイピング、データ抽出、ボット対策の回避を行えます。

## 機能 {#features}

Scrapling MCP サーバーには、Web スクレイピングとブラウザ操作のための 16 個のツールがあります。単発ツールは 1 つの URL を取得し、使ったブラウザやクライアントを閉じます。セッションツールは呼び出し間で Cookie と設定を保つため、AI は同じタブで操作を続け、ネットワーク履歴を確認できます。

### 単発ツール {#one-shot-tools}

#### 🚀 基本的な HTTP スクレイピング {#basic-http-scraping}
- **`make_request`**：各種メソッド（GET、POST、PUT、DELETE）による高速な HTTP リクエストを送ります。ブラウザのフィンガープリントの模倣、TLS バージョンに合った実際のブラウザヘッダーの生成、HTTP/3 などに対応しています。

#### 🔒 ステルスブラウザでのスクレイピング {#stealth-browser-scraping}
- **`browser_fetch_once`**：ステルスブラウザで JavaScript を実行し、動的ページをスクレイピングします。フィンガープリントの偽装、Cloudflare Turnstile/Interstitial の回避、ブラウザとリクエストの設定に対応しています。

### セッションツール {#session-tools}

#### 🔌 セッション管理 {#session-management}
- **`browser_open`**：複数の `browser_fetch` 呼び出しで使い続けられるステルスブラウザのセッションを作ります。毎回ブラウザを起動する負荷を省けます。ブラウザレベルの設定を保持し、`session_id` と `session_type` だけを返します。有効な `settings` は `list_sessions` で確認できます。CDP セッションでは空になります。
- **`open_request_session`**：`session_make_request` で使う永続 HTTP セッションを作ります。ブラウザは使いません。リクエスト間で Cookie、接続、ブラウザのフィンガープリント（`impersonate`）を保持します。`session_id` と `session_type` だけを返し、型は `static` です。有効な `settings` は `list_sessions` で確認できます。
- **`close_session`**：ブラウザまたは HTTP のセッションを閉じ、リソースを解放します。
- **`list_sessions`**：実行中のすべてのセッションについて、詳細と `settings` を一覧表示します。

#### ブラウザの状態 {#browser-state}

- **`browser_save_state`**：Cookie、ローカルストレージ、IndexedDB を Playwright 互換の JSON ファイルに保存します。ブラウザセッションが終わった後でも、ログイン状態を再利用できます。既存のファイルは上書きします。
- **`browser_load_state`**：保存したファイルを、開いているブラウザセッションに復元します。最初のページを読み込む前にも使えます。現在の保存状態を置き換えますが、既存のタブを閉じたり移動したりはしません。復元したログイン状態を使うには、ページを取得するか再読み込みします。

状態ファイルは MCP サーバーが動くマシンに保存します。`sessionStorage`、開いているタブ、ブラウザ設定は含まれません。

#### 🎯 セッションを使った取得 {#fetching-through-a-session}
- **`browser_fetch`**：開いているステルスブラウザセッションで JavaScript を実行し、1 つの URL をスクレイピングします。フィンガープリントの偽装と Cloudflare Turnstile/Interstitial の回避に対応しています。要素の参照、位置、サイズを含む構造化されたページのスナップショットも取得できます。AI が操作対象を見つけ、マウス操作を計画するのに役立ちます。
- **`session_make_request`**：各種メソッド（GET、POST、PUT、DELETE）で高速な HTTP リクエストを送ります。ブラウザのフィンガープリントの模倣、それに合ったヘッダー、HTTP/3 に対応しています。`open_request_session` で開いたセッションを通じて、Cookie、接続、フィンガープリントを再利用します。

#### 📸 スクリーンショット {#screenshots}

- **`browser_screenshot`**：再読み込みせずに、現在のページや指定した要素を PNG または JPEG で撮影します。入力済みの欄、開いたメニュー、グラフ、結果カードなどを確認できます。要素だけを撮影すれば、周囲の不要な内容を減らせます。表示領域、ページ全体、1 つの要素を選べ、JPEG の画質も調整できます。画像はモデルが直接見られる画像コンテンツブロックとして返します。

#### 現在のページの内容 {#current-page-content}

- **`browser_extract`**：再読み込みせずに、現在のページや 1 つの要素を AI スナップショット、HTML、Markdown、テキストとして読み取ります。フォーム入力後や追加の内容を読み込んだ後の結果も抽出できます。スナップショットには、後続の操作に使う要素のロール、名前、参照、位置、サイズが含まれます。正規表現で検索すると、一致したスナップショットの行と、前後の文脈、親ノードを返します。

#### ブラウザ操作 {#browser-actions}

- **`browser_actions`**：1 回の呼び出しで、マウス操作、入力欄の操作、キーボードショートカット、ダイアログへの応答、待機を続けて実行します。アラートや確認ダイアログを受け入れる、閉じる、入力ダイアログにテキストを入れる、といった操作ができます。例えば、検索欄への入力、送信、結果の待機、結果を開く操作をまとめられます。AI は手順が分かっている操作をまとめ、ページの変化を確認したいときは別途スナップショットを取得できます。操作ごとにエージェントとのやり取りを挟まずに済むため、短時間で消えるメニューなど、すぐに次の操作をする必要がある場面で役立ちます。

    ホバーでメニューやツールチップを表示し、ボタンやリンクをクリックし、入れ子のパネル上に移動して縦や横にスクロールできます。移動とクリックでは、セレクター、スナップショットの参照、座標を指定できます。要素を対象にする場合は、自動で待機して表示範囲までスクロールします。座標間の移動を複数の段階に分けるほか、左、右、中央ボタンのクリックとダブルクリックにも対応しています。

    セレクターやスナップショットの参照で、ページ上の入力欄を指定します。テキスト入力、チェックボックスのオンとオフ、ラジオボタンの選択、標準のドロップダウンで表示ラベルに基づく 1 つ以上の選択ができます。既存のテキストを置き換える、消す、現在のカーソル位置から入力を続けることもできます。キーボードショートカットで、テキストの選択や削除、フォーカス移動、フォーム送信、メニューを閉じる操作を行えます。低速モードでは 1 文字ずつ入力し、文字間と各操作の間にランダムな待ち時間を入れます。

    次の操作の前に、結果が表示されるまで、読み込み中のオーバーレイが消えるまで、またはページの読み込みイベントまで待機できます。一定時間の停止や、ネットワークの通信が落ち着くまでの待機にも対応しています。

#### JavaScript {#javascript}

- **`browser_evaluate`**：現在のページで JavaScript を実行し、独自のデータ抽出、計算、ページ固有の処理を行います。AI は複数の要素からデータを集め、アプリの状態を読み、ページの内容を更新できます。非同期スクリプトにも対応し、結果を JSON で返します。

#### ネットワーク履歴 {#network-history}

- **`browser_network_requests`**：タブ、ページ読み込み、ブラウザ操作をまたいで、完了したリクエストを検索します。ページのデータを取得する API 呼び出しを探し、HTTP エラーや保存済みのリダイレクトを確認できます。結果を小さくするため、静的リソースはデフォルトで表示しません。詳細は JSON で返し、長い履歴にはページ分割を使えます。
- **`browser_network_request`**：記録した 1 つのリクエストの概要、ヘッダー、送信データ、テキストのレスポンス本文を、構造化された JSON として確認します。ページを読み込んだり再送したりせず、選択した部分を省略せずに返します。保存したレスポンスはページが変わっても利用できます。履歴にはサイズ制限があり、テキスト以外の本文、大きすぎる本文、読み取れない本文には理由を付けます。必要な詳細は MCP セッションを閉じる前に読んでください。

レスポンス本文を読み取って保存するのは、HTML、JSON、XML、JavaScript など、対応するテキストの `Content-Type` だけです。バイナリ、種類が不明なもの、種類の指定がないものは、本文を読み取りも保存もせず、リクエストのメタデータとヘッダーを保持します。ブラウザ自体は通常どおりリソースを読み込みます。

保存するのは完了したリクエストだけで、HTTP 4xx と 5xx のレスポンスも含みます。失敗したものや未完了のものは除きます。記録が終わると履歴に追加されます。履歴の読み取りやセッションの終了は、記録の完了を待ちません。ページ移動や終了時に記録中だったものは、含まれない場合があります。保存するバイト列はブラウザから取得するため、サーバーが送ったものと異なる場合があります。有効な UTF-8 なら Playwright と同じように UTF-8 で読み取り、それ以外では指定された文字コードを使います。

### Shadow DOM {#shadow-dom}

オープンな Shadow DOM の内容を含めるには、`browser_fetch_once` または各 `browser_fetch` 呼び出しで `pierce_shadow=true` を設定します。デフォルトは `false` です。セレクターの例と制限については [Shadow DOM](../fetching/stealthy.md#shadow-dom) をご覧ください。

ブラウザのセレクターは、クローズドな Shadow DOM 内の要素も指定して操作できます。

### 主な機能 {#key-capabilities}
- **内容の抽出**：Web ページや要素を Markdown、HTML に変換し、不要な内容を除いたテキストも抽出します。
- **CSS セレクター対応**：AI に渡す前に、Scrapling のエンジンで対象の要素を正確に選べます。
- **ボット対策の回避**：Cloudflare Turnstile、Interstitial などの保護に対応します。
- **プロキシ対応**：匿名性の確保や接続地域の指定にプロキシを使えます。
- **ブラウザの模倣**：TLS フィンガープリントや、そのバージョンに合った実際のブラウザヘッダーなどを使います。
- **セッションの維持**：複数のリクエストでブラウザセッションを再利用し、性能を上げます。
- **広告のブロック**：すべてのブラウザツールで、既知の広告、トラッキング用の約 3,500 ドメインへのリクエストを自動でブロックし、トークンを節約して読み込みを速くします。
- **プロンプトインジェクション対策**：攻撃に使われる可能性のある隠し内容を自動で除去します。インラインスタイルで隠された要素、aria-hidden、隠されたスロット、ゼロ幅文字、HTML コメント、template タグが対象です。

## インストール {#installation}

MCP 対応の Scrapling をインストールし、ブラウザの依存関係も入っていることを確認します。

```bash
# Install Scrapling with MCP server dependencies
pip install "scrapling[ai]"

# Install browser dependencies
scrapling install
```

Docker レジストリからイメージを直接使うこともできます。
```bash
docker pull pyd4vinci/scrapling
```
GitHub レジストリからもダウンロードできます。
```bash
docker pull ghcr.io/d4vinci/scrapling:latest
```

## MCP サーバーの設定 {#setting-up-the-mcp-server}

ここでは [Claude Desktop](https://claude.ai/download) と [Claude Code](https://www.anthropic.com/claude-code) に Scrapling MCP サーバーを追加する方法を説明します。MCP 対応の他のチャットボットでも基本的な手順は同じです。

!!! note "注意"
    以下の `scrapling-mcp` コマンドは v0.4.13 で追加されました。`scrapling mcp` を直接呼び出すショートカットで、単一のコマンドを求める MCP レジストリやクライアントに登録しやすくします。古いバージョンでは、`scrapling` コマンドの最初の引数に `mcp` を渡してください。

### Claude Desktop {#claude-desktop}

1. Claude Desktop を開きます。
2. 左上のメニュー（☰）→ Settings → Developer → Edit Config の順に選びます。
3. Scrapling MCP サーバーの設定を追加します。
```json
"ScraplingServer": {
  "command": "scrapling-mcp"
}
```
初めて MCP サーバーを追加する場合は、ファイル全体を次の内容にします。
```json
{
  "mcpServers": {
    "ScraplingServer": {
      "command": "scrapling-mcp"
    }
  }
}
```
[公式の記事](https://modelcontextprotocol.io/quickstart/user)によると、この操作で既存の設定ファイルが開きます。ファイルがなければ新しく作成されます。場所は次のとおりです。

1. **macOS**：`~/Library/Application Support/Claude/claude_desktop_config.json`
2. **Windows**：`%APPDATA%\Claude\claude_desktop_config.json`

確実に実行できるよう、`scrapling-mcp` 実行ファイルのフルパスを使います。

1. **macOS**：`which scrapling-mcp`
2. **Windows**：`where scrapling-mcp`

私の Mac では `/Users/<MyUsername>/.venv/bin/scrapling-mcp` が返されたため、最終的に次の設定を使いました。
```json
{
  "mcpServers": {
    "ScraplingServer": {
      "command": "/Users/<MyUsername>/.venv/bin/scrapling-mcp"
    }
  }
}
```
#### Docker {#docker}
Docker イメージを使う場合は、次のようになります。
```json
{
  "mcpServers": {
    "ScraplingServer": {
      "command": "docker",
      "args": [
        "run", "-i", "--rm", "pyd4vinci/scrapling", "mcp"
      ]
    }
  }
}
```

[Cursor](https://cursor.com/docs/context/mcp)、[WindSurf](https://windsurf.com/university/tutorials/configuring-first-mcp-server) などでも、基本的な手順は同じです。

### Claude Code {#claude-code}
[Claude Code](https://www.anthropic.com/claude-code) では、もっと簡単に追加できます。

```bash
claude mcp add ScraplingServer "/Users/<MyUsername>/.venv/bin/scrapling-mcp"
```
Scrapling の実行ファイルのパスは、次のコマンドで確認します。

1. **macOS**：`which scrapling-mcp`
2. **Windows**：`where scrapling-mcp`

詳しくは Anthropic の [Claude Code に MCP サーバーを追加する方法](https://docs.anthropic.com/en/docs/claude-code/mcp#option-1%3A-add-a-local-stdio-server)をご覧ください。


サーバーを追加したら、使っているアプリを完全に終了してから起動し直してください。Claude Desktop では、チャット入力欄の右下に MCP サーバーのアイコン（🔧）が表示されるか、入力欄の `Search and tools` メニューに `ScraplingServer` が表示されます。

### 独自のブラウザ実行ファイル {#custom-browser-executable}

`browser_fetch_once` と `browser_open` は、付属の Chromium の代わりに、Chromium 互換の別の実行ファイルを使えます。独自ビルドや軽量なブラウザエンジンを使いたい場合に便利です。

MCP サーバー全体に設定するには、起動時に実行ファイルのパスを渡します。

```bash
scrapling-mcp --executable-path "/path/to/chromium"
```

Claude Desktop の設定では、サーバーの引数にオプションを追加します。

```json
{
  "mcpServers": {
    "ScraplingServer": {
      "command": "/Users/<MyUsername>/.venv/bin/scrapling-mcp",
      "args": [
        "--executable-path",
        "/path/to/chromium"
      ]
    }
  }
}
```

起動前に `SCRAPLING_EXECUTABLE_PATH` 環境変数を設定することもできます。AI は `browser_fetch_once` の単発取得や、`browser_open` でセッションを開くときに、別の実行ファイルを選ぶこともできます。

### リモートブラウザへの接続 {#connecting-to-remote-browsers}

`browser_open` は必ずしもローカルでブラウザを起動する必要はありません。CDP URL を渡すと、[Chrome DevTools Protocol](https://chromedevtools.github.io/devtools-protocol/) で実行中のブラウザに接続します。同じマシン、別のホスト、ブラウザ提供サービスのいずれでも使えます。
```
Open a stealthy browser session on wss://cdp.provider.example/session/abc123, then use it to scrape the product details from https://shop.example.com. Close the session when you're done.
```
返される `session_id` は、通常どおり `browser_fetch`、`browser_extract`、`browser_actions`、`browser_evaluate`、`browser_screenshot`、`browser_network_requests`、`browser_network_request`、`browser_save_state`、`browser_load_state` で使います。

URL には、ブラウザ提供サービスが発行する WebSocket アドレス（`ws://`/`wss://`）、またはリモートデバッグポートを有効にして起動したブラウザの HTTP アドレスを指定できます。
```commandline
chrome --remote-debugging-port=9222
```
この場合は `cdp_url="http://localhost:9222"` で接続します。別のマシンでブラウザが動いている場合は、そのホストのアドレスを使います。

!!! note "注意点"

    * ブラウザはすでに動いているため、起動時だけに使うオプションは CDP セッションでは無視されます。対象は `headless`、`real_chrome`、`executable_path` で、上で説明したサーバー全体のデフォルト値も含みます。<br/>
    * 各セッションはリモートブラウザに専用のブラウザコンテキストを作るため、それ以外の設定（`locale`、`useragent`、`proxy`、`cookies`、`timezone_id` など）は適用されます。

### Streamable HTTP {#streamable-http}
バージョン 0.3.6 から、従来の stdio の代わりに Streamable HTTP で MCP サーバーを使えるようになりました。

stdio では次のコマンドを使います。
```bash
scrapling-mcp
```
Streamable HTTP を有効にするには、次のコマンドに変えます。
```bash
scrapling-mcp --http
```
サーバーが待ち受けるアドレスのデフォルトは 127.0.0.1、ポートは 8000 です。どちらも次のように設定できます。
```bash
scrapling-mcp --http --host '0.0.0.0' --port 8000
```
デフォルトでは、同じマシンからの接続だけを受け付けます。ネットワークからアクセスできるようにするには `--host '0.0.0.0'` を渡します。この設定と、次に説明する認証の設定は別です。

Docker 内で Streamable HTTP を使う場合は、0.0.0.0 にバインドし、トークンも設定してください。そうしないと、公開したポートからサーバーに接続できません。コンテナ内の 127.0.0.1 は、コンテナの中からしかアクセスできないためです。
```bash
docker run -p 8000:8000 -e SCRAPLING_MCP_AUTH_TOKEN="<your-token>" pyd4vinci/scrapling mcp --http --host '0.0.0.0'
```

### 認証 {#authentication}

stdio にアクセスできるのは、起動したプログラムだけです。一方、Streamable HTTP に切り替えると、ポートに接続できる人はすべてのツールを呼び出せます。サーバーが動くマシンから任意の URL を取得することも含まれます。そのため Streamable HTTP は認証を必須とし、`--http` だけでは起動せず、トークンの指定を求めます。
```bash
scrapling-mcp --http --auth-token "$(openssl rand -hex 32)"
```
クライアントは `Authorization` ヘッダーでトークンを送る必要があります。トークンのないリクエストは `401` で拒否します。
```json
{
  "mcpServers": {
    "ScraplingServer": {
      "url": "https://your-server.example.com/mcp",
      "headers": {
        "Authorization": "Bearer <your-token>"
      }
    }
  }
}
```
コマンドラインでトークンを渡すと、シェルの履歴やプロセス一覧に残ります。できるだけ `SCRAPLING_MCP_AUTH_TOKEN` 環境変数を使ってください。
```bash
export SCRAPLING_MCP_AUTH_TOKEN="<your-token>"
scrapling-mcp --http
```
デフォルトの 127.0.0.1 でローカルテストをするなど、認証なしで使う必要がある場合は、明示的に `--no-auth` を指定します。
```bash
scrapling-mcp --http --no-auth
```
`--no-auth` と `--host '0.0.0.0'` を組み合わせると、ポートに接続できる誰もがすべてのツールを使えます。信頼できるネットワークの外では、この組み合わせを避けてください。

公開アドレスで待ち受ける場合は、許可するホスト名も指定してください。これにより、ブラウザで開いたサイトがサーバーへの接続を試みる DNS リバインディング攻撃への対策が有効になります。このオプションは複数回指定できます。
```bash
scrapling-mcp --http --allowed-host 'your-server.example.com:8000'
```

!!! note "注意点"

    * 認証は Streamable HTTP だけに適用されます。stdio では無視され、その旨をログに警告として記録します。<br/>
    * 通常の HTTP はトークンを平文で送ります。インターネットに公開する前に、TLS を処理するリバースプロキシの背後にサーバーを置いてください。<br/>
    * クライアントごとの認証情報ではなく、1 つの共有キーを使います。すべてのクライアントで同じトークンを使い、変更時にはサーバーの再起動が必要です。<br/>
    * `--http --no-auth` で起動すると、認証がないことを知らせる警告をログに記録します。<br/>
    * `--auth-token` と `--no-auth` を両方渡した場合、トークンは保持されます。認証が黙って無効になることはありません。

## 例 {#examples}

MCP サーバーのテストで使ったプロンプトをいくつか紹介します。もっと工夫したプロンプトも考えられるはずです :)

簡単なものから、少しずつ複雑なものへ進めます。例では Claude Desktop を使いますが、他のクライアントでも考え方は同じです。

1. **基本的な Web スクレイピング**

    ページの本文を Markdown として抽出します。
    
    ```
    Scrape the main content from https://example.com and convert it to markdown format.
    ```
    
    Claude は `make_request` でページを取得し、不要な内容を除いた読みやすい結果を返せます。HTTP リクエストはデフォルトで最大 3 回試行し、試行の間に 1 秒待ちます。ページに JavaScript が必要な場合や HTTP リクエストがブロックされる場合は、AI が `browser_fetch_once` に切り替えられます。どちらのツールも、呼び出し後に自分が使ったリソースを閉じます。
    
    同じプロンプトを、より具体的にすると次のようになります。
    ```
    Use regular requests to scrape the main content from https://example.com and convert it to markdown format.
    ```
    これで使うツールが Claude に伝わるため、推測する必要がなくなります。指定しないと、通常のリクエストを使うこともあれば、特に理由もなくブラウザが向いていると判断することもあります。時間と費用を節約し、結果を安定させるため、使うツールを指定することをおすすめします。

2. **対象を絞ったデータ抽出**

    CSS セレクターで特定の要素を抽出します。
    
    ```
    Get all product titles from https://shop.example.com using the CSS selector '.product-title'. If the request fails, retry up to 5 times every 10 seconds.
    ```
    
    サーバーはセレクターに一致する要素だけを抽出し、構造化されたリストで返します。ここではサイトの接続不良に備え、最大 5 回試すよう指定しています。ただし、多くの場合はデフォルト設定で十分です。

3. **EC サイトのデータ収集**

    少し複雑なプロンプトの例です。
    ```
    Open a stealthy browser session and visit these e-commerce URLs one at a time:
    - https://shop1.com/product-a
    - https://shop2.com/product-b  
    - https://shop3.com/product-c
    
    Get the product names, prices, and descriptions from each page. Close the session when done.
    ```
    
    Claude は 1 つのブラウザセッションを再利用し、各 URL に順番に `browser_fetch` を呼び出してから、抽出したデータを分析できます。

4. **より高度な作業手順**

    PlayStation Store の 1 ページ目から、すべてのアクションゲームを取得するとします。次のプロンプトで実行できます。
    ```
    Extract the URLs of all games on this page, then visit each game in order and return a list of all action games: https://store.playstation.com/en-us/pages/browse
    ```
    通常のリクエストでデータを取得できる場合は、HTTP セッションを再利用するよう AI に伝えれば、ブラウザの起動を省けます。
    ```
    Open an HTTP session, extract the URLs of all games on this page, then fetch each game in order and return a list of all action games. Close the session when done: https://store.playstation.com/en-us/pages/browse
    ```
    CSS セレクターを書ける場合は、AI が読む前に内容を絞れます。
    ```
    Use an HTTP session to extract the URLs of all games on the page below, then fetch each game in order and return a list of all action games.
    The selector for games in the first page is `[href*="/concept/"]` and the selector for the genre in each game page is `[data-qa="gameInfo#releaseInformation#genre-value"]`.
    Close the session when done.

    URL: https://store.playstation.com/en-us/pages/browse
    ```

5. **Cloudflare で保護されたサイトからデータを取得する**

    対象サイトに Cloudflare の保護があると思う場合は、Claude が自分で気付くのを待たず、先に伝えてください。
    ```
    What's the price of this product? Be cautious, as it utilizes Cloudflare's Turnstile protection. Make the browser visible while you work.

    https://ao.com/product/oo101uk-ninja-woodfire-outdoor-pizza-oven-brown-99357-685.aspx
    ```

6. **長い作業手順**

    例えば、次のようなプロンプトを使えます。
    ```
    Extract all product URLs for the following category, then return the prices and details for the first 3 products.
    
    https://www.arnotts.ie/furniture/bedroom/bed-frames/
    ```
    ただし、次のように書くと、よりよくなります。
    ```
    Go to the following category URL and extract all product URLs using the CSS selector "a". Then, reuse the session to fetch the first 3 product pages in order and extract each product’s price and details. Close the session when done.
    
    Keep the output in markdown format to reduce irrelevant content.
    
    Category URL:
    https://www.arnotts.ie/furniture/bedroom/bed-frames/
    ```

7. **永続セッションを使う**

    同じサイトの複数のページを取得するときは、永続ブラウザセッションを使うと、リクエストごとにブラウザを起動する負荷を避けられます。
    ```
    Open a stealthy browser session, then use it to scrape the main details from the first 5 product pages on https://shop.example.com. Close the session when you're done.
    ```
    Claude は `browser_open` でブラウザセッションを作り、そのセッションで各商品ページに `browser_fetch` を呼び出し、最後に `close_session` を呼びます。ページごとに新しいブラウザを起動するより、はるかに高速です。

    !!! danger "危険"
    
        永続セッションを使った後は、必ず閉じてください。閉じないと開いたままになります！


8. **長い作業で永続セッションを使う**

    Claude がよく考える必要のある、長いテストの例です。

    ```
    Use Scrapling MCP to do the following in this order:

    1. Open a stealthy browser session with headless mode off.
    2. Go to this page and collect the number of stars: https://github.com/D4Vinci/Scrapling
    3. From the README, get the URL that shows the number of downloads and go to it.
    4. Get the number of downloads and the top 3 countries from the graph.
    5. Prepare a report with the results.
    6. Close the browser.
    ```

ここで紹介したのは一部の例です。工夫しながら、さまざまな使い方を試してください。

## ベストプラクティス {#best-practices}

技術的な使い方のヒントを紹介します。

### 1. 適切なツールを選ぶ {#1-choose-the-right-tool}
- **`make_request`**：1 ページや 1 回の API 呼び出しを、高速な HTTP リクエストで取得します。
- **`browser_fetch_once`**：JavaScript を使う単一の動的ページや、Cloudflare などで保護されたサイトを取得します。
- **セッションツール**：関連するリクエスト、ブラウザ操作、スクリーンショット、ネットワーク履歴に使います。

### 2. 性能を上げる {#2-optimize-performance}
- セッションを再利用し、各 URL を順に取得します。
- 不要なリソースを無効にします。
- 適切なタイムアウトを設定します。
- CSS セレクターで抽出対象を絞ります。

### 3. 動的な内容に対応する {#3-handle-dynamic-content}
- SPA では `network_idle` を使います。
- 特定の要素には `wait_selector` を設定します。
- 読み込みの遅いサイトではタイムアウトを長くします。

### 4. データの品質 {#4-data-quality}
- `main_content_only=true` でページの本文を選び、不要な内容を除去します。
- 用途に合った `extraction_type` を選びます。

### 5. プロンプトインジェクション対策 {#5-prompt-injection-protection}
MCP サーバーは `main_content_only` が有効な場合（デフォルト）、取得した内容を自動でクリーニングします。悪意のあるサイトが AI のコンテキストに指示を入れるために使える、次のような隠し内容を取り除きます。

- **インラインの非表示スタイル**：`display:none`、`visibility:hidden`、不透明度、文字サイズ、高さ、幅、最大高さ、最大幅がゼロのスタイル
- **アクセシビリティから隠された要素**：`aria-hidden="true"`
- **template タグと隠されたスロット**：`<template>` と `<slot hidden>` の要素
- **HTML コメント**：`<!-- ... -->`
- **ゼロ幅文字**：ゼロ幅スペースなど、見えない Unicode 文字

HTML、Markdown、テキストの抽出で、この保護が自動で働きます。十分な保護を得るため、デフォルトの `main_content_only=true` を維持してください。

### 6. セッションを管理する {#6-manage-sessions}
- 単発の取得には `make_request` または `browser_fetch_once` を使います。使用したリソースを閉じ、後で呼び出すためのセッションは残しません。
- 複数のページを取得するときは、`browser_open` で永続ブラウザセッションを作り、各ページに対してそのセッションで `browser_fetch` を呼び出します。
- 通常の HTTP リクエストを複数送る場合は、`open_request_session` を使い、リクエストごとに `session_make_request` を呼び出します。ブラウザなしで、Cookie、接続、ブラウザのフィンガープリント（`impersonate`）を呼び出し間で保持します。
- セッションは作成時のセッションレベルの設定を保持します。ブラウザでは headless、locale、cookies、ステルス機能の切り替えなど、HTTP セッションでは `impersonate` と `proxy` です。timeout、wait_selector、network_idle、solve_cloudflare などのリクエスト単位の設定は、各 `browser_fetch`/`session_make_request` 呼び出しに渡します。デフォルト値はツールのスキーマに記載されています。
- `browser_fetch` は、開いているステルスブラウザセッションを使って Cloudflare のチャレンジを解決できます。
- 作業後は必ず `close_session` でセッションを閉じ、リソースを解放します。
- `list_sessions` で実行中のセッションと、作成時の `settings` を確認します。これらは AI エージェントに返されますが、CDP セッションでは空です。
- セッションを開くツールに独自の `session_id` を渡すと、ランダムな十六進数の代わりに `"search"`、`"checkout"` などの分かりやすい名前を使えます。その ID が使用中ならエラーになるため、重複を早く検出できます。

### 7. スクリーンショットを撮る {#7-capturing-screenshots}

- `browser_screenshot` は、ステルスブラウザセッションで `browser_fetch` によって開いたページを撮影します。再読み込みしないため、AI は入力済みの欄、開いたメニュー、その他の操作結果を確認できます。
- 画像は実際の `ImageContent` ブロックとして返されるため、モデルがページを直接見られます。
- 表示中の領域、またはスクロールしないと見えない部分を含めたページ全体を撮影できます。
- 1 つの入力欄、グラフ、カード、結果だけを撮影すれば、周囲の内容を減らして確認できます。要素の撮影では、対象を表示範囲までスクロールできます。
- 劣化のない画像には PNG、データ量を減らしたい場合は画質を調整できる JPEG を選びます。
- AI は撮影前に `browser_actions` で内容を待ち、必要な操作を終えられます。

## 法律と倫理への配慮 {#legal-and-ethical-considerations}

⚠️ **大切な指針：**

- **robots.txt を確認する**：`https://website.com/robots.txt` でスクレイピングのルールを確認します。
- **レート制限を守る**：大量のリクエストでサーバーに負荷をかけないようにします。
- **利用規約**：サイトの規約を読み、守ります。
- **著作権**：知的財産権を尊重します。
- **プライバシー**：個人情報保護に関する法律に注意します。
- **商用利用**：業務目的での利用に必要な許可があることを確認します。

---

*Scrapling チームが ❤️ を込めて作りました。スクレイピングを楽しんでください！*
