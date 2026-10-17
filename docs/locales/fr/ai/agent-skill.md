---
title: "Agent Skill de Scrapling : installation et utilisation"
description: "Installez la skill Scrapling pour votre agent de programmation. Donnez-lui des exemples et des références de l’API actuelle pour récupérer des pages, extraire des données et explorer des sites."
---

# Agent Skill de Scrapling {#scrapling-agent-skill}

Le [serveur MCP](mcp-server.md) donne aux chatbots IA des outils pour extraire des données sur le Web. L’**Agent Skill de Scrapling** apprend aux agents de programmation à utiliser la bibliothèque elle-même. Le code qu’ils écrivent avec Scrapling suit ainsi l’API actuelle, sans dépendre d’informations anciennes issues de leur entraînement.

La skill suit la spécification [AgentSkills](https://agentskills.io/specification). Elle peut donc être lue par [Claude Code](https://claude.com/product/claude-code), [OpenClaw](https://github.com/openclaw/openclaw) et d’autres outils à base d’agents. Elle contient des guides en Markdown sur la récupération de pages, l’analyse, l’exploration de sites, MCP et RAG. L’agent les charge quand il en a besoin. Des exemples prêts à exécuter lui permettent aussi de répondre à la plupart des questions sur Scrapling et d’écrire du code d’extraction correct sans quitter votre éditeur.

La skill se trouve dans le dossier [agent-skill](https://github.com/D4Vinci/Scrapling/tree/main/agent-skill) du dépôt, sous le nom `scrapling-official`. Sa version suit toujours celle de la bibliothèque.

## Installation {#installation}

### Skills.sh {#skillssh}

Installez la skill depuis le dépôt avec la CLI de [skills.sh](https://skills.sh) :
```bash
npx skills add D4Vinci/Scrapling --skill scrapling-official
```
La CLI détecte les agents installés et leur ajoute la skill.

### Clawhub {#clawhub}

Si vous utilisez OpenClaw, vous pouvez installer la skill avec [Clawhub](https://docs.openclaw.ai/tools/clawhub) :
```bash
clawhub install scrapling-official
```
Ou installez-la depuis sa [page Clawhub](https://clawhub.ai/D4Vinci/scrapling-official).

### Téléchargement manuel {#manual-download}

Téléchargez le fichier ZIP de la skill [directement depuis le dépôt](https://github.com/D4Vinci/Scrapling/raw/refs/heads/main/agent-skill/Scrapling-Skill.zip), puis extrayez son contenu dans le dossier des skills de votre agent. Pour Claude Code, il s’agit de `~/.claude/skills/`.

## Contenu de la skill {#whats-inside}

- **`SKILL.md`** : Le premier fichier que l’agent lit. Il présente la configuration, le choix du fetcher et les règles de sécurité à suivre. Par exemple, toujours passer `--ai-targeted` aux commandes de la CLI pour se protéger contre l’injection d’instructions.
- **`references/`** : Des copies en Markdown des pages de documentation sur l’analyse, la récupération de pages, les spiders, le serveur MCP et les intégrations. Elles sont chargées à la demande pour ne pas occuper le contexte de l’agent avant d’être utiles.
- **`examples/`** : Des scripts prêts à exécuter dont l’agent peut s’inspirer.

Nous avons testé la skill avec OpenClaw et Claude Code. Si vous rencontrez un problème, ouvrez un [ticket](https://github.com/D4Vinci/Scrapling/issues/new/choose) ou contactez-nous sur notre [serveur Discord](https://discord.gg/EMgGbDceNQ).
