---
title: "Agent Skill de Scrapling: instalación y uso"
description: "Instala la skill de Scrapling para tu agente de programación. Dale ejemplos y referencias de la API actual para obtener páginas, extraer datos y rastrear sitios."
---

# Agent Skill de Scrapling {#scrapling-agent-skill}

El [servidor MCP](mcp-server.md) da a los chatbots de IA herramientas para extraer datos de sitios web. La **Agent Skill de Scrapling** enseña la propia biblioteca a los agentes de programación. Así, el código que escriben con Scrapling usa la API actual y no depende de lo que aprendieron con datos antiguos.

La skill sigue la especificación [AgentSkills](https://agentskills.io/specification), por lo que pueden leerla [Claude Code](https://claude.com/product/claude-code), [OpenClaw](https://github.com/openclaw/openclaw) y otras herramientas con agentes. Incluye guías en Markdown sobre la obtención de páginas, la extracción de datos, el rastreo, MCP y RAG. El agente las carga cuando las necesita. También incluye ejemplos listos para ejecutar, para que pueda responder la mayoría de las preguntas sobre Scrapling y escribir código correcto sin salir de tu editor.

La skill está en el directorio [agent-skill](https://github.com/D4Vinci/Scrapling/tree/main/agent-skill) del repositorio, con el nombre `scrapling-official`. Su versión siempre sigue la de la biblioteca.

## Instalación {#installation}

### Skills.sh {#skillssh}

Instala la skill desde el repositorio con la CLI de [skills.sh](https://skills.sh):
```bash
npx skills add D4Vinci/Scrapling --skill scrapling-official
```
La CLI detecta los agentes que tienes instalados y les añade la skill.

### Clawhub {#clawhub}

Si usas OpenClaw, puedes instalar la skill desde [Clawhub](https://docs.openclaw.ai/tools/clawhub):
```bash
clawhub install scrapling-official
```
O instálala desde su [página de Clawhub](https://clawhub.ai/D4Vinci/scrapling-official).

### Descarga manual {#manual-download}

Descarga el ZIP de la skill [directamente desde el repositorio](https://github.com/D4Vinci/Scrapling/raw/refs/heads/main/agent-skill/Scrapling-Skill.zip) y extrae su contenido en el directorio de skills de tu agente. Para Claude Code, es `~/.claude/skills/`.

## Contenido {#whats-inside}

- **`SKILL.md`**: El archivo que el agente lee primero. Explica la configuración, qué fetcher elegir y las reglas de seguridad que debe seguir. Por ejemplo, añadir siempre `--ai-targeted` a los comandos de la CLI para protegerse de la inyección de instrucciones.
- **`references/`**: Copias en Markdown de las páginas de documentación sobre extracción de datos, obtención de páginas, spiders, el servidor MCP e integraciones. Se cargan cuando hacen falta para no ocupar el contexto del agente antes de tiempo.
- **`examples/`**: Scripts listos para ejecutar que el agente puede usar como base.

Probamos la skill con OpenClaw y Claude Code. Si tienes algún problema, abre una [incidencia](https://github.com/D4Vinci/Scrapling/issues/new/choose) o escríbenos en nuestro [servidor de Discord](https://discord.gg/EMgGbDceNQ).
