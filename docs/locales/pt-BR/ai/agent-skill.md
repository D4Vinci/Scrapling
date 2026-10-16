---
title: "Agent Skill do Scrapling: instalação e uso"
description: "Instale a skill do Scrapling no seu agente de programação. Forneça exemplos e referências da API atual para obter páginas, extrair dados e rastrear sites."
---

# Agent Skill do Scrapling {#scrapling-agent-skill}

O [servidor MCP](mcp-server.md) oferece aos chatbots de IA ferramentas para extrair dados de sites. Já a **Agent Skill do Scrapling** ensina a própria biblioteca aos agentes de programação. Assim, o código que eles escrevem com Scrapling segue a API atual, sem depender de informações antigas dos dados de treinamento.

A skill segue a especificação [AgentSkills](https://agentskills.io/specification), por isso pode ser lida pelo [Claude Code](https://claude.com/product/claude-code), pelo [OpenClaw](https://github.com/openclaw/openclaw) e por outras ferramentas com agentes. Ela reúne guias em Markdown sobre obtenção de páginas, extração de dados, rastreamento, MCP e RAG, que o agente carrega conforme precisa. Também inclui exemplos prontos para executar. Assim, o agente pode responder à maioria das dúvidas sobre Scrapling e escrever código de extração correto sem sair do seu editor.

A skill está no diretório [agent-skill](https://github.com/D4Vinci/Scrapling/tree/main/agent-skill) do repositório, com o nome `scrapling-official`. A versão dela sempre acompanha a versão da biblioteca.

## Instalação {#installation}

### Skills.sh {#skillssh}

Instale a skill a partir do repositório com a CLI do [skills.sh](https://skills.sh):
```bash
npx skills add D4Vinci/Scrapling --skill scrapling-official
```
A CLI detecta os agentes instalados e adiciona a skill a eles.

### Clawhub {#clawhub}

Se você usa OpenClaw, pode instalar a skill pelo [Clawhub](https://docs.openclaw.ai/tools/clawhub):
```bash
clawhub install scrapling-official
```
Ou instale pela [página dela no Clawhub](https://clawhub.ai/D4Vinci/scrapling-official).

### Download manual {#manual-download}

Baixe o arquivo ZIP da skill [diretamente do repositório](https://github.com/D4Vinci/Scrapling/raw/refs/heads/main/agent-skill/Scrapling-Skill.zip) e extraia o conteúdo no diretório de skills do seu agente. No Claude Code, esse diretório é `~/.claude/skills/`.

## Conteúdo da skill {#whats-inside}

- **`SKILL.md`**: O primeiro arquivo que o agente lê. Explica a configuração, qual fetcher escolher e as regras de segurança que o agente deve seguir. Por exemplo, sempre passar `--ai-targeted` aos comandos da CLI para se proteger contra injeção de instruções.
- **`references/`**: Cópias em Markdown das páginas de documentação sobre extração de dados, obtenção de páginas, spiders, servidor MCP e integrações. São carregadas conforme a necessidade, para não ocupar o contexto do agente antes da hora.
- **`examples/`**: Scripts prontos para executar que o agente pode usar como base.

Testamos a skill no OpenClaw e no Claude Code. Se encontrar algum problema, abra uma [issue](https://github.com/D4Vinci/Scrapling/issues/new/choose) ou fale com a gente no [servidor do Discord](https://discord.gg/EMgGbDceNQ).
