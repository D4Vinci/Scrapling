---
title: "Scrapling Agent Skill のインストールと使い方"
description: "コーディングエージェントに Scrapling Skill をインストールします。ページ取得、解析、クロールに使える最新 API の例とリファレンスを提供します。"
---

# Scrapling Agent Skill {#scrapling-agent-skill}

[MCP サーバー](mcp-server.md)は AI チャットボットに Web サイトをスクレイピングするツールを提供します。**Scrapling Agent Skill** は、コーディングエージェントにライブラリ自体の使い方を教えます。これにより、古い学習データから推測するのではなく、現在の API に合った Scrapling コードを書けるようになります。

この Skill は [AgentSkills](https://agentskills.io/specification) 仕様に従っているため、[Claude Code](https://claude.com/product/claude-code)、[OpenClaw](https://github.com/openclaw/openclaw) などのエージェントツールで読み込めます。ページ取得、解析、クロール、MCP、RAG のガイドが、必要に応じて読み込む Markdown リファレンスとしてまとめられています。そのまま実行できる例も含まれているため、エディターを離れずに、Scrapling に関する多くの質問に答え、正しいスクレイピングコードを書けます。

Skill はリポジトリの [agent-skill](https://github.com/D4Vinci/Scrapling/tree/main/agent-skill) ディレクトリに `scrapling-official` という名前で置かれています。バージョンは常にライブラリのバージョンに合わせています。

## インストール {#installation}

### Skills.sh {#skillssh}

[skills.sh](https://skills.sh) CLI を使って、リポジトリから Skill をインストールします。
```bash
npx skills add D4Vinci/Scrapling --skill scrapling-official
```
CLI がインストール済みのエージェントを検出し、それぞれに Skill を追加します。

### Clawhub {#clawhub}

OpenClaw を使っている場合は、[Clawhub](https://docs.openclaw.ai/tools/clawhub) からインストールできます。
```bash
clawhub install scrapling-official
```
[Clawhub のページ](https://clawhub.ai/D4Vinci/scrapling-official)からもインストールできます。

### 手動ダウンロード {#manual-download}

Skill の ZIP ファイルを[リポジトリから直接ダウンロード](https://github.com/D4Vinci/Scrapling/raw/refs/heads/main/agent-skill/Scrapling-Skill.zip)し、エージェントの Skill ディレクトリに展開します。Claude Code では `~/.claude/skills/` です。

## 含まれるもの {#whats-inside}

- **`SKILL.md`**：エージェントが最初に読むファイルです。セットアップ、Fetcher の選び方、守るべき安全上のルールを説明しています。例えば、プロンプトインジェクションを防ぐため、CLI コマンドには常に `--ai-targeted` を渡します。
- **`references/`**：ドキュメントページの Markdown 版です。解析、ページ取得、Spider、MCP サーバー、連携機能を扱います。必要なときに読み込むため、それまではエージェントのコンテキストを消費しません。
- **`examples/`**：エージェントがコピーして使える、実行可能なスクリプトです。

この Skill は OpenClaw と Claude Code でテストしています。問題があれば [Issue](https://github.com/D4Vinci/Scrapling/issues/new/choose) を作成するか、[Discord サーバー](https://discord.gg/EMgGbDceNQ)でお知らせください。
