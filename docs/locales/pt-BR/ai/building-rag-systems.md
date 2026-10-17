---
title: "Converta sites em Markdown para RAG com Scrapling"
description: "Converta respostas de páginas em Markdown ou use ContentSpider para coletar um site. Prepare os textos para dividir e indexar em um sistema RAG."
---

# Criar sistemas RAG com Scrapling {#building-rag-systems-with-scrapling}

A qualidade de um sistema RAG depende do texto que ele recebe. O HTML bruto gasta tokens com marcação, navegação, scripts e conteúdo de rastreamento. Ele pode até levar instruções maliciosas ocultas para o seu LLM. O Scrapling transforma páginas e sites inteiros em Markdown limpo, remove esse conteúdo oculto e não precisa de um LLM no processo. Assim, a entrada de dados é rápida e não tem custo por página.

## Instalação {#installation}

```bash
pip install "scrapling[rag]"

scrapling install
```

O extra `rag` instala os fetchers com suporte à conversão para Markdown. Os extras `ai`, `shell` e `all` também incluem esse suporte. O comando `scrapling install` baixa as dependências do navegador, necessárias apenas para os fetchers que usam navegador.

## Converter uma página em Markdown {#one-page-to-markdown}

Todo [Response](../fetching/choosing.md#response-object) tem um método `markdown()`:

```python
from scrapling.fetchers import Fetcher

markdown = Fetcher.get("https://example.com").markdown(main_content_only=True)
```

Ele funciona com todos os fetchers, então você também pode obter páginas protegidas pelo Cloudflare com uma linha:

```python
from scrapling.fetchers import StealthyFetcher

markdown = StealthyFetcher.fetch("https://protected.example.com", solve_cloudflare=True).markdown(main_content_only=True)
```

Dois argumentos controlam a saída:

- `main_content_only`: Converte apenas o conteúdo dentro da tag `<body>` da página.
- `css_selector`: Converte apenas os elementos que correspondem a um seletor CSS e junta todas as correspondências. Use para extrair a parte que seu processo precisa e economizar tokens:

```python
markdown = Fetcher.get("https://example.com/docs/page").markdown(css_selector="article")
```

Seja qual for a configuração, scripts, estilos e conteúdo oculto sempre são removidos antes da conversão. É a mesma limpeza que o [servidor MCP](mcp-server.md) usa para proteger agentes de IA contra injeção de instruções. Ela remove elementos ocultos por estilos inline, elementos com `aria-hidden="true"`, slots ocultos, tags `<template>`, comentários HTML e caracteres de largura zero. O servidor MCP faz essa limpeza com `main_content_only=True`.

## Converter um site inteiro em uma coleção de Markdown {#a-whole-website-to-a-markdown-corpus}

O template `ContentSpider` rastreia um site e converte cada página. Ele usa o [sistema de spiders](../spiders/architecture.md), que já oferece concorrência, AutoThrottle, respeito ao robots.txt e pausa e retomada:

```python
from scrapling.spiders import ContentSpider

class DocsSpider(ContentSpider):
    name = "docs"
    start_urls = ["https://example.com/docs/"]
    allowed_domains = {"example.com"}
    output_dir = "docs_markdown"
    max_pages = 200

result = DocsSpider().start()
result.items.to_jsonl("docs.jsonl")
```

Cada página rastreada vira um item com as chaves `url`, `title` e `markdown`. Se você definir `output_dir`, cada página também será salva em um arquivo Markdown com nome baseado na URL. Assim, o exemplo acima gera tanto uma pasta de arquivos `.md` quanto um arquivo `docs.jsonl` pronto para carregar.

O template exige `allowed_domains` para manter o rastreamento dentro do site escolhido. Estas são as opções:

- `css_selector` / `main_content_only`: São passados para `markdown()` em cada página. `main_content_only` fica ativado por padrão.
- `output_dir`: Quando definido, grava um arquivo Markdown por página.
- `max_pages`: Número máximo de páginas a converter. Solicitações que já estão na fila quando o limite é atingido ainda podem ser feitas, mas suas páginas não são convertidas. O valor padrão, `0`, desativa o limite.

Por padrão, todos os links dentro de `allowed_domains` são seguidos. Como o template se baseia em [CrawlSpider](../spiders/generic-templates.md#crawlspider), você pode sobrescrever `rules()` com seu próprio [LinkExtractor](../spiders/generic-templates.md#linkextractor-reference) para controlar o rastreamento. `allow` limita as URLs aos padrões que você quer, e `deny` exclui os que não quer, como páginas de login, listas de tags e versões para impressão:

```python
from scrapling.spiders import CrawlRule, LinkExtractor, ContentSpider

class DocsSpider(ContentSpider):
    name = "docs"
    start_urls = ["https://example.com/"]
    allowed_domains = {"example.com"}

    def rules(self):
        return [CrawlRule(LinkExtractor(allow=r"/docs/", deny=[r"/docs/changelog/", r"\?print="]))]
```

`deny` tem prioridade sobre `allow`. Uma regra pode incluir `priority` ou um hook `process_request`, como em qualquer **CrawlSpider**.

## Carregar os dados em um banco de vetores {#feeding-a-vector-store}

Você pode usar a saída JSONL em qualquer processo de criação de embeddings. Este é um exemplo básico:

```python
import json

with open("docs.jsonl", encoding="utf-8") as f:
    for line in f:
        page = json.loads(line)
        for chunk in split_into_chunks(page["markdown"]):
            vector_store.add(text=chunk, metadata={"url": page["url"], "title": page["title"]})
```

Use `css_selector` no spider para remover o conteúdo repetido antes de dividir o texto, em vez de fazer a limpeza depois. Quanto menos conteúdo irrelevante você incluir nos embeddings, melhores serão os resultados da busca.

## Alternativas interativas {#interactive-alternatives}

Se você prefere extrair dados por meio de uma conversa, o [servidor MCP](mcp-server.md) oferece ao seu chatbot de IA ferramentas com a mesma extração para Markdown. A [Agent skill](agent-skill.md) ensina os agentes de programação a escrever esse código por conta própria.
