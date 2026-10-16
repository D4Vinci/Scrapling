---
title: "Scrapling Agent Skill：安装与使用"
description: "为编程智能体安装 Scrapling Skill，提供最新 API 示例和参考资料，帮助它获取页面、解析内容和爬取网站。"
---

# Scrapling Agent Skill {#scrapling-agent-skill}

[MCP 服务器](mcp-server.md)为 AI 聊天机器人提供抓取网站的工具，而 **Scrapling Agent Skill** 则让编程智能体学会使用 Scrapling 库本身。这样，它编写的代码就会使用当前 API，而不是根据过时的训练数据猜测。

该 Skill 遵循 [AgentSkills](https://agentskills.io/specification) 规范，因此 [Claude Code](https://claude.com/product/claude-code)、[OpenClaw](https://github.com/openclaw/openclaw) 等智能体工具都能读取。它包含页面获取、解析、爬取、MCP 和 RAG 的 Markdown 指南，智能体可以按需加载。加上可直接运行的示例，智能体无需离开编辑器，就能回答大部分 Scrapling 问题并编写正确的抓取代码。

该 Skill 位于仓库的 [agent-skill](https://github.com/D4Vinci/Scrapling/tree/main/agent-skill) 目录中，名称为 `scrapling-official`，版本始终与库版本保持一致。

## 安装 {#installation}

### Skills.sh {#skillssh}

使用 [skills.sh](https://skills.sh) CLI 从仓库安装：
```bash
npx skills add D4Vinci/Scrapling --skill scrapling-official
```
CLI 会检测已安装的智能体，并为它们添加该 Skill。

### Clawhub {#clawhub}

如果使用 OpenClaw，可以通过 [Clawhub](https://docs.openclaw.ai/tools/clawhub) 安装：
```bash
clawhub install scrapling-official
```
也可以从它的 [Clawhub 页面](https://clawhub.ai/D4Vinci/scrapling-official)安装。

### 手动下载 {#manual-download}

[直接从仓库](https://github.com/D4Vinci/Scrapling/raw/refs/heads/main/agent-skill/Scrapling-Skill.zip)下载 Skill 的 ZIP 文件，解压到智能体的 Skills 目录。Claude Code 对应的目录是 `~/.claude/skills/`。

## 内容 {#whats-inside}

- **`SKILL.md`**：智能体首先读取的入口文件。它介绍设置方法、Fetcher 的选择和必须遵守的安全规则。例如，调用 CLI 命令时始终传入 `--ai-targeted`，以防范提示词注入。
- **`references/`**：文档页面的 Markdown 副本，涵盖解析、页面获取、Spider、MCP 服务器和集成。它们按需加载，使用前不会占用智能体的上下文。
- **`examples/`**：可直接运行的脚本，供智能体参考。

我们已在 OpenClaw 和 Claude Code 中测试该 Skill。如果遇到问题，请提交 [Issue](https://github.com/D4Vinci/Scrapling/issues/new/choose)，或通过我们的 [Discord 服务器](https://discord.gg/EMgGbDceNQ)联系。
