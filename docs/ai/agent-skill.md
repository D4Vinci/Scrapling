# Scrapling Agent Skill

While the [MCP server](mcp-server.md) gives AI chatbots tools to scrape websites for you, the **Scrapling Agent Skill** teaches coding agents the library itself, so the code they write with Scrapling matches the current API instead of guessing from outdated training data.

The skill follows the [AgentSkills](https://agentskills.io/specification) specification, so it's readable by [Claude Code](https://claude.com/product/claude-code), [OpenClaw](https://github.com/openclaw/openclaw), and other agentic tools. It packages almost all of this documentation website's content as Markdown references that the agent loads on demand, together with ready-to-run examples, so it can answer most Scrapling questions and write correct scraping code without leaving your editor.

The skill lives in the [agent-skill](https://github.com/D4Vinci/Scrapling/tree/main/agent-skill) directory of the repository under the name `scrapling-official`, and its version always tracks the library version.

## Installation

### Skills.sh

Install the skill from the repository with the [skills.sh](https://skills.sh) CLI:
```bash
npx skills add D4Vinci/Scrapling --skill scrapling-official
```
The CLI detects the agents you have installed and adds the skill to them.

### Clawhub

If you use OpenClaw, you can install the skill through [Clawhub](https://docs.openclaw.ai/tools/clawhub):
```bash
clawhub install scrapling-official
```
Or install it from its [Clawhub page](https://clawhub.ai/D4Vinci/scrapling-official).

### Manual download

Download the skill's ZIP file [directly from the repository](https://github.com/D4Vinci/Scrapling/raw/refs/heads/main/agent-skill/Scrapling-Skill.zip) and extract it into your agent's skills directory (for Claude Code, that's `~/.claude/skills/`).

## What's inside

- **`SKILL.md`**: The entry point the agent reads first. It covers setup, which fetcher to choose, and the safety rules the agent must follow, like always passing `--ai-targeted` to the CLI commands for prompt injection protection.
- **`references/`**: Markdown mirrors of the documentation pages (parsing, fetching, spiders, CLI, MCP server, and integrations), loaded on demand so they don't consume the agent's context until needed.
- **`examples/`**: Ready-to-run scripts the agent can copy from.

We tested the skill on OpenClaw and Claude Code. If you face any issues with it, open a [ticket](https://github.com/D4Vinci/Scrapling/issues/new/choose) or reach out on our [Discord server](https://discord.gg/EMgGbDceNQ).
