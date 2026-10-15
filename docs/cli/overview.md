---
title: "Scrapling CLI: Scrape from the Terminal"
description: "Install Scrapling terminal tools and choose between extract commands, the interactive shell and the MCP server. Follow the guide for your task."
---

# Command Line Interface

Since v0.3, Scrapling includes a powerful command-line interface that provides three main capabilities:

1. **Interactive Shell**: An interactive Web Scraping shell based on IPython that provides many shortcuts and useful tools
2. **Extract Commands**: Scrape websites from the terminal without any programming
3. **Utility Commands**: Installation and management tools

```bash
# Launch interactive shell
scrapling shell

# Convert the content of a page to markdown and save it to a file
scrapling extract get "https://example.com" content.md

# Get help for any command
scrapling --help
scrapling extract --help
```

## Requirements
This section requires you to install the extra `shell` dependency group, like the following:
```bash
pip install "scrapling[shell]"
```
For browser fetching, also install the browser dependencies:
```bash
scrapling install
```
This downloads Chromium and its system dependencies, and updates the TLD list. HTTP requests do not need this step.