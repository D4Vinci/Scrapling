---
title: "Como funcionam os rastreadores web do Scrapling"
description: "Entenda a relação entre spiders, solicitações, sessões, filas e o motor de rastreamento. Compare o fluxo com Scrapy e escolha por onde começar."
---

# Arquitetura dos spiders {#spiders-architecture}

!!! success "Antes de começar"

    1. Leia a página [Conceitos básicos dos fetchers](../fetching/choosing.md) para conhecer os tipos de fetcher e saber quando usar cada um.
    2. Leia a página [Classes principais](../parsing/main_classes.md) para conhecer as classes [Selector](../parsing/main_classes.md#selector) e [Response](../fetching/choosing.md#response-object).

O sistema de spiders do Scrapling é inspirado no Scrapy. Ele permite rastreamento assíncrono com várias solicitações e sessões ao mesmo tempo, além de pausa e retomada. Une o analisador e os fetchers do Scrapling em uma API de rastreamento, com fila de solicitações, controle de concorrência e checkpoints, que são pontos salvos para retomar o trabalho.

Se você conhece Scrapy, vai se sentir à vontade. Se não, não se preocupe: o sistema foi feito para ser simples de usar.

## Fluxo de dados {#data-flow}

Este diagrama mostra como os dados passam pelo sistema durante um rastreamento:

<img src="../assets/spider_architecture.png" title="Diagrama da arquitetura dos spiders por @TrueSkills" alt="Diagrama da arquitetura dos spiders por @TrueSkills" style="width: 70%;"/>

Estes são os principais passos ao executar um spider:

1. O **Spider** gera o primeiro grupo de objetos `Request`. Por padrão, cria uma solicitação para cada URL em `start_urls`. Você pode redefinir `start_requests()` para mudar essa lógica.
2. O **Scheduler** recebe as solicitações, calcula suas impressões digitais e as coloca em uma fila de prioridade. As de maior prioridade saem primeiro.
3. O **motor de rastreamento** pede a próxima solicitação ao **Scheduler**, respeitando os limites de concorrência globais e por domínio, além das esperas entre downloads. Se `robots_txt_obey` estiver ativo, verifica as regras de robots.txt do domínio e descarta as solicitações não permitidas sem mensagens. Depois envia a solicitação ao **gerenciador de sessões**, que escolhe a sessão conforme o campo `sid`, o ID da sessão.
4. A **sessão** obtém a página e devolve um objeto [Response](../fetching/choosing.md#response-object) ao **motor de rastreamento**. O motor registra estatísticas e verifica se houve bloqueio. Se houver, tenta a solicitação novamente até `max_blocked_retries` vezes. Você pode personalizar tanto a detecção quanto a lógica das novas tentativas.
5. O **motor de rastreamento** passa o objeto [Response](../fetching/choosing.md#response-object) ao callback da solicitação. O callback pode produzir um dicionário, que é salvo como item extraído, ou uma nova solicitação, que é enviada ao Scheduler para entrar na fila.
6. O ciclo volta ao passo 2 até a fila ficar vazia e não haver tarefas ativas, ou até o spider ser pausado.
7. Se você definir `crawldir` ao iniciar o spider, o **motor de rastreamento** salva periodicamente um checkpoint em disco com as solicitações pendentes e o conjunto de URLs já vistas. Ao encerrar de forma controlada com Ctrl+C, salva um último checkpoint. Quando o spider é executado de novo com o mesmo `crawldir`, ele restaura a fila e continua de onde parou, sem executar `start_requests()`.

## Componentes {#components}

### Spider {#spider}

É a classe principal com a qual você trabalha. Crie uma subclasse de `Spider` e defina `start_urls` e o método `parse()`. Você também pode configurar sessões e redefinir hooks para as etapas do rastreamento.

```python
from scrapling.spiders import Spider, Response, Request

class MySpider(Spider):
    name = "my_spider"
    start_urls = ["https://example.com"]

    async def parse(self, response: Response):
        for link in response.css("a::attr(href)").getall():
            yield response.follow(link, callback=self.parse_page)

    async def parse_page(self, response: Response):
        yield {"title": response.css("h1::text").get("")}
```

### Motor de rastreamento {#crawler-engine}

O motor coordena todo o rastreamento. Gerencia o loop principal, aplica os limites de concorrência, envia solicitações pelo gerenciador de sessões e processa os resultados dos callbacks. Você não precisa usá-lo diretamente: `Spider.start()` e `Spider.stream()` cuidam disso.

### Scheduler {#scheduler}

É uma fila de prioridade que evita repetir URLs. Calcula uma impressão digital de cada solicitação a partir da URL, do método HTTP, do corpo e do ID da sessão. Os métodos `snapshot()` e `restore()` permitem salvar e restaurar o estado do rastreamento pelo sistema de checkpoints.

### Gerenciador de sessões {#session-manager}

Gerencia uma ou mais sessões identificadas por nome. Cada sessão pode ser:

- [FetcherSession](../fetching/static.md)
- [AsyncStealthySession](../fetching/stealthy.md)

Quando chega uma solicitação, o gerenciador escolhe a sessão pelo campo `sid`. As sessões podem iniciar junto com o spider, que é o comportamento padrão, ou no primeiro uso.

### Sistema de checkpoints {#checkpoint-system}

Este sistema opcional salva o estado do rastreador em um arquivo pickle: as solicitações pendentes e as impressões digitais das URLs já vistas. As gravações são atômicas: um arquivo temporário é criado e depois renomeado, para evitar dados corrompidos. O estado é salvo em intervalos configuráveis e ao encerrar de forma controlada. Se o rastreamento terminar por completo, sem ficar pausado, os arquivos são removidos automaticamente.

### Cache de respostas {#response-cache}

Com o modo de desenvolvimento ativo, este cache opcional salva as respostas em disco e as reutiliza nas próximas execuções. Cada resposta é identificada pela impressão digital da solicitação e salva como JSON, com o corpo codificado em base64 para preservar dados binários. Serve para ajustar a lógica de `parse()` sem enviar novas solicitações aos servidores. Não foi feito para uso em produção.

### Resultados {#output}

Os itens extraídos são reunidos em um `ItemList`, uma subclasse de lista com os métodos de exportação `to_json()`, `to_jsonl()`, `to_csv()` e `to_xml()`. As estatísticas ficam em uma dataclass `CrawlStats`, que contém informações detalhadas da execução.

## Comparação com Scrapy {#comparison-with-scrapy}

Se você já usa Scrapy, esta tabela mostra as equivalências no Scrapling:

| Conceito | Scrapy | Scrapling |
|----------|--------|-----------|
| Definição do spider | Subclasse de `scrapy.Spider` | Subclasse de `scrapling.spiders.Spider` |
| Solicitações iniciais | `start_requests()` | `async start_requests()` |
| Callbacks | `def parse(self, response)` | `async def parse(self, response)` |
| Seguir links | `response.follow(url)` | `response.follow(url)` |
| Entrega de itens | `yield dict` ou `yield Item` | `yield dict` |
| Fila de solicitações | Scheduler + Dupefilter | Scheduler com remoção de duplicatas integrada |
| Download | Downloader + Middlewares | Gerenciador de sessões com suporte a várias sessões |
| Processamento de itens | Item Pipelines | Hook `on_scraped_item()` |
| Detecção de bloqueios | Por middlewares personalizados | Hooks integrados `is_blocked()` + `retry_blocked_request()` |
| Concorrência | Configuração `CONCURRENT_REQUESTS` | Atributo de classe `concurrent_requests` |
| Filtro de domínios | `allowed_domains` | `allowed_domains` |
| Robots.txt | Configuração `ROBOTSTXT_OBEY` | Atributo de classe `robots_txt_obey` |
| Pausa e retomada | Configuração `JOBDIR` | Argumento `crawldir` do construtor |
| Exportação | Feed exports | `result.items.to_json()` / `to_jsonl()` / `to_csv()` / `to_xml()`, ou hooks próprios |
| Execução | `scrapy crawl spider_name` | `MySpider().start()` |
| Streaming | Não disponível | `async for item in spider.stream()` |
| Várias sessões | Não disponível | Várias sessões de tipos diferentes por spider |
