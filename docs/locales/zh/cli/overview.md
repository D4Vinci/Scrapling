---
title: "Scrapling CLI：在终端中抓取数据"
description: "安装 Scrapling 终端工具，在提取命令、交互式 Shell 和 MCP 服务器之间选择，并按照对应指南完成任务。"
---

# 命令行界面 {#command-line-interface}

从 v0.3 开始，Scrapling 提供命令行界面，包含三类主要功能：

1. **交互式 Shell**：基于 IPython 的交互式网页抓取环境，提供多种快捷方式和实用工具。
2. **提取命令**：无需编程，直接在终端中抓取网站。
3. **实用命令**：安装和管理工具。

```bash
# Launch interactive shell
scrapling shell

# Convert the content of a page to markdown and save it to a file
scrapling extract get "https://example.com" content.md

# Get help for any command
scrapling --help
scrapling extract --help
```

## 环境要求 {#requirements}

使用本节工具前，需要安装 `shell` 扩展依赖组：
```bash
pip install "scrapling[shell]"
```
如果要通过浏览器获取页面，还需要安装浏览器依赖：
```bash
scrapling install
```
该命令会下载 Chromium 及其系统依赖，并更新 TLD 列表。HTTP 请求不需要这一步。
