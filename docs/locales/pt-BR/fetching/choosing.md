---
title: "Escolha solicitações HTTP ou um navegador para web scraping"
description: "Escolha Fetcher ou StealthyFetcher conforme sua tarefa. Saiba quando usar HTTP direto, executar JavaScript e reutilizar sessões."
---

# Conceitos básicos dos fetchers {#fetchers-basics}

## Introdução {#introduction}
Fetchers são classes que enviam solicitações ou obtêm páginas com uma linha de código e retornam um objeto [Response](#response-object). Desde a v0.3, eles têm classes de sessão separadas para manter a conexão aberta. Por exemplo, uma sessão de navegador mantém o navegador aberto até você terminar todas as solicitações, em vez de abrir vários navegadores. Escolha conforme sua necessidade.

Esses recursos foram adicionados porque, antes da v0.2, o Scrapling só analisava páginas. O objetivo é atender, aos poucos, a todas as necessidades de web scraping.

> Os fetchers não são apenas camadas sobre outras bibliotecas. Eles usam essas bibliotecas como motores para enviar solicitações e obter páginas, mas acrescentam recursos que os motores não oferecem. Também aproveitam suas capacidades e as ajustam para web scraping.

## Comparação dos fetchers {#fetchers-overview}

O Scrapling oferece fetchers HTTP (`Fetcher` e `AsyncFetcher`) e um fetcher de navegador (`StealthyFetcher`), com classes de sessão para várias solicitações.

Esta tabela ajuda você a comparar e escolher:


| Recurso | Fetcher | StealthyFetcher |
|--------------------|---------------------------------------------------|--------------------------------------------------------------------------------------------|
| Velocidade relativa | 🐇🐇🐇🐇🐇 | 🐇🐇🐇 |
| Ocultação da automação | ⭐⭐ | ⭐⭐⭐⭐⭐ |
| Opções contra detecção de bots | ⭐⭐ | ⭐⭐⭐⭐⭐ |
| Execução de JavaScript | ❌ | ✅ |
| Uso de memória | ⭐ | ⭐⭐⭐ |
| Uso recomendado | Extração simples quando solicitações HTTP bastam | - Sites com carregamento dinâmico <br/>- Automações pequenas <br/>- Proteções simples ou complexas |
| Navegadores | ❌ | Chromium e Google Chrome |
| API de navegador usada | ❌ | Playwright |
| Dificuldade de configuração | Simples | Simples |

Veremos cada ferramenta em detalhes nas próximas páginas.

## Configurar o analisador em todos os fetchers {#parser-configuration-in-all-fetchers}
Todos os fetchers são importados da mesma forma:
```python
from scrapling.fetchers import Fetcher, AsyncFetcher, StealthyFetcher
```
Depois, você pode usá-los diretamente, sem criar um objeto. Serão usados os ajustes padrão do analisador:
```python
page = StealthyFetcher.fetch('https://example.com') 
```
Se quiser configurar o analisador, ou seja, a [classe Selector](../parsing/main_classes.md#selector), que processará a resposta antes de retorná-la, faça isto primeiro:
```python
from scrapling.fetchers import Fetcher
Fetcher.configure(adaptive=True, keep_comments=False)  # and the rest
```
Ou:
```python
from scrapling.fetchers import Fetcher
Fetcher.adaptive=True
Fetcher.keep_comments=False
```
Depois, continue seu código normalmente.

Os argumentos disponíveis são `adaptive`, `adaptive_domain`, `huge_tree`, `keep_comments`, `storage` e `storage_args`. São os mesmos aceitos por [Selector](../parsing/main_classes.md#selector). Você pode ver a configuração atual com `<fetcher_class>.display_config()`.

!!! info "Informação"

    `adaptive` fica desativado por padrão. Você precisa ativá-lo para usar esse recurso.

### Configurar o analisador por solicitação {#set-parser-config-per-request}
Os ajustes acima se aplicam a todas as solicitações enviadas por aquela classe, para simplificar o uso.

Se precisar de ajustes diferentes por solicitação, passe um dicionário no argumento `selector_config` do método usado (`fetch`/`get`/`post`/...).

## Objeto Response {#response-object}
`Response` funciona como [Selector](../parsing/main_classes.md#selector), mas acrescenta dados da resposta, como cabeçalhos, status e cookies:
```python
from scrapling.fetchers import Fetcher
page = Fetcher.get('https://example.com')

page.status          # HTTP status code
page.reason          # Status message
page.cookies         # Response cookies as a dictionary
page.headers         # Response headers
page.request_headers # Request headers
page.history         # Response history of redirections, if any
page.body            # Raw response body as bytes
page.encoding        # Response encoding
page.meta            # Response metadata dictionary (e.g., proxy used). Mainly helpful with the spiders system.
```
Todos os fetchers retornam `Response`. Sessões de navegador com `record_requests=True` também retornam objetos `Response` salvos por meio de `session.network.search(limit=None)` e `session.network.get(request_id)`. Consulte o [histórico de rede](stealthy.md#network-history) para saber como usar as respostas de API salvas e migrar para a v5.

`Response` também pode converter a página em Markdown limpo e pronto para modelos de linguagem com uma linha:
```python
markdown = Fetcher.get('https://example.com').markdown(main_content_only=True)
```
Antes da conversão, scripts, estilos, conteúdo oculto e tentativas de injeção de instruções são sempre removidos. Você pode passar `css_selector` para converter apenas certos elementos. O recurso exige o extra `rag`, também incluído em `ai`/`shell`/`all`. A página [Criar sistemas RAG](../ai/building-rag-systems.md) explica isso em detalhes.

!!! note "Nota"

    Ao contrário de [Selector](../parsing/main_classes.md#selector), o corpo de `Response` sempre é bytes desde a v0.4.
