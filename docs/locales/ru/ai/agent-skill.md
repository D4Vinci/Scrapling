---
title: "Scrapling Agent Skill: установка и использование"
description: "Установите навык Scrapling для агента, который пишет код. Дайте ему актуальные примеры API и справочные материалы по загрузке, парсингу и обходу сайтов."
---

# Scrapling Agent Skill {#scrapling-agent-skill}

[MCP-сервер](mcp-server.md) даёт ИИ-чатботам инструменты для сбора данных с сайтов. **Scrapling Agent Skill** знакомит агентов, которые пишут код, с самой библиотекой. Так они используют текущий API Scrapling, а не угадывают его по устаревшим обучающим данным.

Навык соответствует спецификации [AgentSkills](https://agentskills.io/specification), поэтому его могут читать [Claude Code](https://claude.com/product/claude-code), [OpenClaw](https://github.com/openclaw/openclaw) и другие инструменты с ИИ-агентами. Он содержит руководства по загрузке страниц, парсингу, обходу сайтов, MCP и RAG в виде справочных Markdown-файлов, которые агент загружает по мере необходимости. Есть и готовые к запуску примеры. Это позволяет отвечать на большинство вопросов о Scrapling и писать правильный код для сбора данных, не выходя из редактора.

Навык находится в каталоге [agent-skill](https://github.com/D4Vinci/Scrapling/tree/main/agent-skill) репозитория под именем `scrapling-official`. Его версия всегда соответствует версии библиотеки.

## Установка {#installation}

### Skills.sh {#skillssh}

Установите навык из репозитория с помощью CLI [skills.sh](https://skills.sh):
```bash
npx skills add D4Vinci/Scrapling --skill scrapling-official
```
CLI найдёт установленных агентов и добавит им навык.

### Clawhub {#clawhub}

Если вы используете OpenClaw, навык можно установить через [Clawhub](https://docs.openclaw.ai/tools/clawhub):
```bash
clawhub install scrapling-official
```
Или со [страницы в Clawhub](https://clawhub.ai/D4Vinci/scrapling-official).

### Скачивание вручную {#manual-download}

Скачайте ZIP-файл навыка [прямо из репозитория](https://github.com/D4Vinci/Scrapling/raw/refs/heads/main/agent-skill/Scrapling-Skill.zip) и распакуйте его в каталог навыков вашего агента. Для Claude Code это `~/.claude/skills/`.

## Что входит в навык {#whats-inside}

- **`SKILL.md`**: файл, который агент читает первым. В нём описаны настройка, выбор Fetcher и правила безопасности. Например, для защиты от внедрения инструкций в промпт агент должен всегда передавать `--ai-targeted` командам CLI.
- **`references/`**: копии страниц документации в Markdown: парсинг, загрузка страниц, Spider, MCP-сервер и интеграции. Они загружаются по мере необходимости и до этого не занимают контекст агента.
- **`examples/`**: готовые к запуску скрипты, из которых агент может брать код.

Мы проверили навык в OpenClaw и Claude Code. Если возникнут проблемы, создайте [Issue](https://github.com/D4Vinci/Scrapling/issues/new/choose) или напишите на нашем [Discord-сервере](https://discord.gg/EMgGbDceNQ).
