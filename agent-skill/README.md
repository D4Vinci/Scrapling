# Scrapling Agent Skill

The skill follows the [AgentSkills](https://agentskills.io/specification) specification, so it's readable by [OpenClaw](https://github.com/openclaw/openclaw), [Claude Code](https://claude.com/product/claude-code), and other agentic tools. It gives your coding agent Scrapling guides and examples for HTTP requests, browser sessions, parsing, crawlers, and AI workflows, so it can use the current API instead of guessing from outdated training data.

Use it to look up the API or build a scraper from a complete task guide without leaving your editor. We tested it on [OpenClaw](https://github.com/openclaw/openclaw) and [Claude Code](https://claude.com/product/claude-code), but please open a [ticket](https://github.com/D4Vinci/Scrapling/issues/new/choose) if you face any issues or use our [Discord server](https://discord.gg/EMgGbDceNQ).

## Installation

You can use this [direct URL](https://github.com/D4Vinci/Scrapling/raw/refs/heads/main/agent-skill/Scrapling-Skill.zip) to download the ZIP file of the skill directly. We will try to update this page with all available methods.

### Clawhub
If you use [OpenClaw](https://github.com/openclaw/openclaw), you can install the skill using [Clawhub](https://docs.openclaw.ai/tools/clawhub) directly:
```bash
clawhub install scrapling-official
```

Or go to the [Clawhub](https://docs.openclaw.ai/tools/clawhub) page from [here](https://clawhub.ai/D4Vinci/scrapling-official).

### Skills.sh
You can install the skill from this repository using the [skills.sh](https://skills.sh) CLI directly:
```bash
npx skills add D4Vinci/Scrapling --skill scrapling-official
```

The CLI will detect the agents you have installed and add the skill to them.
