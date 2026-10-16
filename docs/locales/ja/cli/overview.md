---
title: "Scrapling CLI：ターミナルからスクレイピング"
description: "Scrapling のターミナルツールをインストールし、抽出コマンド、対話型シェル、MCP サーバーから選びます。目的に合ったガイドをご覧ください。"
---

# コマンドラインインターフェース {#command-line-interface}

v0.3 以降、Scrapling には次の 3 つの主な機能を持つコマンドラインインターフェースが含まれています。

1. **対話型シェル**：IPython を使った Web スクレイピング用シェルです。便利なショートカットやツールを利用できます。
2. **抽出コマンド**：プログラムを書かずに、ターミナルから Web サイトをスクレイピングできます。
3. **補助コマンド**：インストールと管理のためのツールです。

```bash
# Launch interactive shell
scrapling shell

# Convert the content of a page to markdown and save it to a file
scrapling extract get "https://example.com" content.md

# Get help for any command
scrapling --help
scrapling extract --help
```

## 必要なもの {#requirements}
このセクションの機能を使うには、次のように `shell` の追加依存関係をインストールします。
```bash
pip install "scrapling[shell]"
```
ブラウザでページを取得する場合は、ブラウザの依存関係もインストールします。
```bash
scrapling install
```
Chromium とそのシステム依存関係をダウンロードし、TLD リストを更新します。HTTP リクエストだけを使う場合、この手順は不要です。
