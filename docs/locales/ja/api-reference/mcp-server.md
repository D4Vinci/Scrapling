---
title: "Scrapling MCP サーバーの API リファレンス"
description: "HTTP とブラウザによるデータ抽出に使う MCP ツールと、リクエスト・レスポンス・セッションのモデルを確認します。"
---

# MCP サーバーのリファレンス {#mcp-server-api-reference}

**Scrapling MCP サーバー**は、Model Context Protocol（MCP）を通じて、データ抽出とブラウザ操作のための 16 個のツールを提供します。AI アシスタントやエージェントに接続すると、会話を通じてデータを抽出できます。ボット検出を避ける機能も使えます。

次のコマンドで MCP サーバーを起動します。

```bash
scrapling mcp
```

サーバークラスを直接インポートすることもできます。

```python
from scrapling.core.ai import ScraplingMCPServer

server = ScraplingMCPServer()
server.serve(http=False, host="127.0.0.1", port=8000)
```

独自の Chromium 互換ブラウザを使う場合は、`executable_path` を指定します。

```python
server = ScraplingMCPServer(executable_path="/path/to/chromium")
```

## レスポンスモデル {#response-model}

ページ取得と HTTP リクエストのツールは、次の形式で 1 回の呼び出しにつき 1 件のレスポンスを返します。セッション管理のツールは、後に示すモデルを使います。`browser_screenshot` はページまたは要素の画像と現在の URL を、画像ブロックとテキストブロックで返します。`browser_extract` と `browser_actions` は通常のテキストを返します。2 つのネットワークツールは、後に示すモデルで構造化された JSON を返します。`browser_evaluate` は結果を JSON にして、テキストブロックで返します。

## ::: scrapling.core.ai.server.ResponseModel
    handler: python
    :docstring:

## ネットワークリクエストのモデル {#network-request-models}

`browser_network_requests` は `NetworkRequestsModel` を返し、`requests`、`next_cursor`、`has_more`、`dropped_count` を含みます。各 `NetworkRequestInfo` には `id`、`url`、`method`、`resource_type`、`status` があります。続きを取得するには、`next_cursor` を `after_id` として渡します。`has_more` は、現在の履歴にまだ一致する結果があるかを示します。

`browser_network_request` は `NetworkRequestModel` を返し、`request_id`、`part`、`data`、`note` を含みます。概要とヘッダーはオブジェクトです。保存された本文全体は、内容が JSON でも文字列で返します。`note` は、本文がない場合やヘッダーが不完全な場合の説明です。

## ::: scrapling.core.ai._network_formatting.NetworkRequestInfo
    handler: python
    :docstring:

## ::: scrapling.core.ai.server.NetworkRequestsModel
    handler: python
    :docstring:

## ::: scrapling.core.ai._network_formatting.NetworkRequestModel
    handler: python
    :docstring:

## セッションモデル {#session-models}

セッション管理に使うモデルクラスです。

## ::: scrapling.core.ai.server.SessionInfo
    handler: python
    :docstring:

## ::: scrapling.core.ai.server.SessionCreatedModel
    handler: python
    :docstring:

## ::: scrapling.core.ai.server.SessionClosedModel
    handler: python
    :docstring:

## MCP サーバークラス {#mcp-server-class}

MCP サーバーのメインクラスは、次のツールを提供します。

- **`make_request`**：ブラウザを模倣した HTTP リクエストで 1 つの URL を取得し、クライアントを自動で閉じます。GET、POST、PUT、DELETE に対応します。
- **`browser_fetch_once`**：ステルスブラウザで 1 つの URL を取得し、JavaScript の実行と Cloudflare 検証の処理を行ってからブラウザを閉じます。その後もページを操作したり、ネットワーク履歴を確認したりする場合は、永続セッションを使ってください。

- **`browser_extract`**：現在のページや要素を、AI 向けの構造化されたスナップショット、HTML、Markdown、テキストとして読み取ります。再読み込みは不要で、フォームや操作の結果を保ちます。スナップショットには要素の役割、名前、参照、位置、サイズが含まれます。正規表現の検索では、一致する行とその前後の内容、親ノードを返します。
- **`browser_actions`**：マウスの移動、ホバー、クリック、スクロール、フォーム入力、キー操作、ダイアログへの応答、待機を 1 回の呼び出しにまとめます。通知や確認を受け入れるか閉じることができ、入力ダイアログには文字を入力できます。検索欄に入力して送信し、待ってから結果を開く操作も、段階ごとに呼び出さずに実行できます。

    移動とクリックには、セレクター、スナップショットの参照、座標を指定できます。要素を待ち、表示領域までスクロールします。段階的な移動、左・右・中央クリック、ダブルクリック、入れ子の領域内のスクロールに対応します。

    セレクターやスナップショットの参照で入力欄を選びます。文字の入力、チェックボックスのオンとオフ、ラジオボタンの選択、標準の選択リストのラベルによる単一・複数選択ができます。文字の置き換えや消去、カーソル位置からの追加入力もできます。キー操作は現在フォーカスがある場所に作用します。低速モードでは、文字や操作の間にランダムな待ち時間を入れます。

    セレクターやスナップショットの参照で、コンテンツや読み込み中のオーバーレイが指定した状態になるまで待てます。読み込みイベント、ネットワークの通信が落ち着くまでの待機、指定時間の待機も使えます。

- **`browser_evaluate`**：現在のページで JavaScript を実行し、独自のデータ抽出、計算、アプリの状態確認、内容の変更を行います。非同期スクリプトに対応し、結果を JSON で返します。
- **`browser_network_requests`**：タブ、ページ移動、操作をまたいで、完了したブラウザリクエストを検索します。保存された API 呼び出し、HTTP エラー、リダイレクトを探せます。静的リソースは既定で非表示にして、不要な結果を減らします。失敗したリクエストや未完了のリクエストは含みません。ページ分割に対応した構造化データを返します。
- **`browser_network_request`**：保存済みリクエストの概要、ヘッダー、送信データ、本文を構造化された JSON で読み取ります。再送信せず、選んだ部分を省略せずに返します。4xx や 5xx の HTTP レスポンスも含め、保存済みレスポンスはページ移動後も読めます。記録が完了したものだけが履歴に現れます。履歴の読み取りやセッションの終了は、進行中の記録を待ちません。未完了の記録はページ移動や終了時に失われることがあります。バイト列は Playwright から取得するため、サーバーが送信した生のバイト列と異なる場合があります。保存したバイト列が有効な UTF-8 なら、Playwright と同じ方法でテキストに変換します。それ以外では、宣言された文字コードを使います。本文を読み取って保存するのは、対応するテキスト形式の `Content-Type` だけです。バイナリ、種類が不明なもの、種類が指定されていないものは、本文を読まずにメタデータとヘッダーだけを保存します。ページの読み込み方は変わりません。履歴にはサイズ上限があります。本文がテキストでない、大きすぎる、読めない場合などは、補足情報で理由を示します。必要なデータは MCP セッションを閉じる前に読んでください。
- **`browser_fetch`**：開いているステルスブラウザセッションでページを取得し、HTML、Markdown、テキスト、スナップショットを抽出します。スナップショットはページ全体または指定した要素を対象にし、後の操作で使う参照、位置、サイズを含みます。

## ::: scrapling.core.ai.server.ScraplingMCPServer
    handler: python
    :docstring:
