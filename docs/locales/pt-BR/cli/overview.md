---
title: "CLI do Scrapling: extraia dados pelo terminal"
description: "Instale as ferramentas de terminal do Scrapling e escolha entre os comandos de extração, o shell interativo e o servidor MCP. Siga o guia da sua tarefa."
---

# Interface de linha de comando {#command-line-interface}

Desde a versão 0.3, o Scrapling inclui uma interface de linha de comando com três funções principais:

1. **Shell interativo**: Um ambiente de extração de dados web baseado em IPython, com vários atalhos e ferramentas úteis.
2. **Comandos de extração**: Extraia dados de sites pelo terminal sem programar.
3. **Comandos utilitários**: Ferramentas de instalação e gerenciamento.

```bash
# Launch interactive shell
scrapling shell

# Convert the content of a page to markdown and save it to a file
scrapling extract get "https://example.com" content.md

# Get help for any command
scrapling --help
scrapling extract --help
```

## Requisitos {#requirements}

Para usar as ferramentas desta seção, instale o grupo de dependências extras `shell`:
```bash
pip install "scrapling[shell]"
```
Para obter páginas com um navegador, instale também as dependências dele:
```bash
scrapling install
```
Esse comando baixa o Chromium e suas dependências de sistema, além de atualizar a lista de TLDs. As solicitações HTTP não precisam dessa etapa.
