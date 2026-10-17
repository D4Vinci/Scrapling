---
title: "Controle do rastreamento: AutoThrottle, checkpoints, cache e streaming"
description: "Controle a velocidade e a concorrência do rastreamento. Aprenda a usar o cache, pausar e retomar, receber itens em tempo real e salvar o estado."
---

# Usos avançados {#advanced-usages}

## Introdução {#introduction}

!!! success "Antes de começar"

    1. Leia a página [Primeiros passos](getting-started.md) para aprender a criar e executar um spider básico.

Esta página explica os recursos avançados dos spiders: controle de concorrência, pausa e retomada, streaming, hooks do ciclo de vida, estatísticas e logs.

## Controle de concorrência {#concurrency-control}

O sistema de spiders usa estes atributos de classe para controlar o ritmo do rastreamento:

| Atributo | Padrão | Descrição |
|----------|--------|-----------|
| `concurrent_requests` | `4` | Número máximo de solicitações processadas ao mesmo tempo |
| `concurrent_requests_per_domain` | `0` | Máximo de solicitações simultâneas por domínio. 0 significa sem limite por domínio |
| `download_delay` | `0.0` | Segundos de espera antes de cada solicitação |
| `robots_txt_obey` | `False` | Respeita as regras de robots.txt: Disallow, Crawl-delay e Request-rate |

```python
class PoliteSpider(Spider):
    name = "polite"
    start_urls = ["https://example.com"]

    # Be gentle with the server
    concurrent_requests = 4
    concurrent_requests_per_domain = 2
    download_delay = 1.0  # Wait 1 second between requests

    async def parse(self, response: Response):
        yield {"title": response.css("title::text").get("")}
```

Ao definir `concurrent_requests_per_domain`, cada domínio ganha seu próprio limite de concorrência, além do limite global. Isso é útil ao rastrear vários domínios: você pode permitir muitas solicitações no total sem sobrecarregar cada domínio.

!!! tip "Dica"

    `download_delay` adiciona uma espera fixa antes de cada solicitação, independentemente do domínio. Use-o para limitar o ritmo de forma simples.

## AutoThrottle {#autothrottle}

Escolher um `download_delay` fixo exige testes: se for baixo demais, você pode receber bloqueios; se for alto demais, o rastreamento demora muito. AutoThrottle observa quanto tempo o site leva para responder e ajusta a espera de cada domínio. Assim, acelera em servidores rápidos e reduz o ritmo nos lentos ou nos que bloqueiam solicitações.

| Atributo | Padrão | Descrição |
|----------|--------|-----------|
| `autothrottle_enabled` | `False` | Ativa o ajuste automático da espera |
| `autothrottle_start_delay` | `5.0` | Espera usada na primeira solicitação a um domínio |
| `autothrottle_max_delay` | `60.0` | Maior espera permitida |
| `autothrottle_target_concurrency` | `None` | Número de solicitações simultâneas que se tenta manter por domínio, como explicado abaixo |
| `autothrottle_block_backoff` | `True` | Duplica a espera do domínio cada vez que ele bloqueia uma solicitação |

```python
class AdaptiveSpider(Spider):
    name = "adaptive"
    start_urls = ["https://example.com"]

    concurrent_requests = 8
    concurrent_requests_per_domain = 1

    autothrottle_enabled = True
    autothrottle_start_delay = 2.0
    autothrottle_max_delay = 30.0

    async def parse(self, response: Response):
        yield {"title": response.css("title::text").get("")}
```

Após cada resposta, a espera se aproxima do tempo que o servidor levou para responder. Por exemplo, se ele responde em 0,5 segundo, a espera se estabiliza perto de 0,5 segundo, mantendo aproximadamente uma solicitação ativa. O número de solicitações desejado por domínio é escolhido nesta ordem: `autothrottle_target_concurrency`, se definido; depois, `concurrent_requests_per_domain`; por último, 1. Normalmente você não precisa definir outro alvo: o limite por domínio que já configurou é usado, e a espera é dividida por esse valor. Aumentos bruscos no tempo de resposta são aplicados de imediato, sem entrar na média. Assim, o spider reduz o ritmo assim que o servidor começa a ter problemas e só volta a acelerar aos poucos.

### Reduzir o ritmo após bloqueios {#backing-off-when-blocked}

O tempo de resposta sozinho não detecta limites de solicitações. Uma resposta `429`, `403` ou uma página com captcha costuma chegar *mais rápido* que o conteúdo real. Medir apenas esse tempo faria o spider acelerar. Por isso, uma resposta com código fora de 2xx ou que `is_blocked()` marque como bloqueada **duplica** a espera daquele domínio:

```
0.5s -> 1s -> 2s -> 4s -> 8s ...   (up to autothrottle_max_delay)
```

O spider continua reduzindo o ritmo enquanto o site recusar as solicitações. Quando as respostas normais voltam, o ajuste pela média diminui a espera aos poucos até se aproximar da velocidade real do servidor. Você não precisa reiniciar nada.

Se uma resposta `429` ou `503` tiver o cabeçalho `Retry-After`, essa espera será usada em vez da duplicação. São aceitos tanto o formato numérico (`Retry-After: 120`) quanto o formato de data HTTP.

Defina `autothrottle_block_backoff = False` para desativar esse comportamento e ajustar o ritmo apenas pelo tempo de resposta. Nesse caso, um bloqueio só impede que o spider acelere.

Você pode consultar a espera final de cada domínio nas estatísticas:

```python
result = AdaptiveSpider().start()
print(result.stats.autothrottle_delays)  # {'example.com': 0.62}
```

!!! note "Notas"

    * `download_delay` e as esperas de robots.txt definem um mínimo, mas `autothrottle_max_delay` também limita esse mínimo. Use um máximo pelo menos igual à espera configurada ou exigida por robots.txt.<br/>
    * `concurrent_requests_per_domain` tem duas funções: limita as solicitações ativas de um domínio e serve como alvo de AutoThrottle. Por isso, geralmente não é preciso configurar outro alvo. É recomendável defini-lo porque uma solicitação em espera ocupa uma vaga do limite global. Sem um limite por domínio, essas esperas podem ocupar as vagas de que os outros domínios precisam.<br/>
    * O tempo medido inclui todo o download, com as tentativas internas e, em sessões de navegador, o tempo de renderização da página.<br/>
    * `autothrottle_max_delay` limita todas as esperas, inclusive `Retry-After`. Se um site pedir uma espera maior, aumente `autothrottle_max_delay` para respeitá-la.<br/>
    * As esperas aprendidas não são salvas nos checkpoints. Depois de pausar e retomar, cada domínio começa novamente com `autothrottle_start_delay`.

## Usar uvloop {#using-uvloop}

O método `start()` aceita `use_uvloop` para usar o loop de eventos mais rápido de [uvloop](https://github.com/MagicStack/uvloop)/[winloop](https://github.com/nicktimko/winloop), se estiver disponível:

```python
result = MySpider().start(use_uvloop=True)
```

Isso pode melhorar o desempenho em rastreamentos com muitas operações de entrada e saída. Você precisa instalar `uvloop` no Linux/macOS ou `winloop` no Windows separadamente.

## Pausar e retomar {#pause-resume}

O spider permite pausar e retomar o rastreamento com checkpoints. Para ativá-los, passe um diretório `crawldir` ao construtor:

```python
spider = MySpider(crawldir="crawl_data/my_spider")
result = spider.start()

if result.paused:
    print("Crawl was paused. Run again to resume.")
else:
    print("Crawl completed!")
```

### Como funciona {#how-it-works}

1. **Pausar**: pressione `Ctrl+C` durante o rastreamento. O spider espera as solicitações ativas terminarem, salva as pendentes e o conjunto de impressões digitais já vistas, e encerra.
2. **Forçar o encerramento**: pressione `Ctrl+C` de novo para parar imediatamente, sem esperar pelas tarefas ativas.
3. **Retomar**: execute o spider novamente com o mesmo `crawldir`. Ele detecta o checkpoint, restaura a fila e as impressões digitais já vistas, e continua de onde parou, sem executar `start_requests()`.
4. **Limpar**: quando o rastreamento termina por completo, sem ficar pausado, os arquivos de checkpoint são removidos automaticamente.

**Checkpoints também são salvos durante o rastreamento, a cada 5 minutos por padrão.**

Você pode mudar o intervalo assim:

```python
# Save checkpoint every 2 minutes
spider = MySpider(crawldir="crawl_data/my_spider", interval=120.0)
```

A gravação de um checkpoint usa um arquivo temporário e só substitui o checkpoint anterior após a gravação terminar com sucesso.

!!! warning "Dados do checkpoint"

    Quando você ativa `crawldir`, os valores das solicitações pendentes, incluindo `meta` e os argumentos das solicitações, devem poder ser salvos com o módulo `pickle` do Python. Se um valor não puder ser salvo, a gravação do checkpoint falha e o rastreamento para. Um `Selector` pode funcionar em um callback, mas não pode ser salvo dessa forma.

    Salve os valores extraídos, como strings ou números, em vez de objetos `Selector`. As listas e os dicionários também devem conter apenas valores que possam ser salvos:

    ```python
    yield response.follow("/details", meta={"title": str(response.css("h1::text").get(""))})
    ```

!!! tip "Dica"

    Com `start()`, pressionar `Ctrl+C` encerra o spider de forma controlada mesmo sem checkpoints ativos. Pressionar de novo, sem esperar, força o encerramento imediato.

### Saber se você está retomando um rastreamento {#knowing-if-youre-resuming}

O hook `on_start()` recebe o indicador `resuming`:

```python
async def on_start(self, resuming: bool = False):
    if resuming:
        self.logger.info("Resuming from checkpoint!")
    else:
        self.logger.info("Starting fresh crawl")
```

## Modo de desenvolvimento {#development-mode}

Ao ajustar a lógica de `parse()`, baixar as páginas novamente em cada execução consome tempo e gera solicitações desnecessárias. O modo de desenvolvimento salva as respostas em disco na primeira execução e as reutiliza depois. Assim, você pode mudar os seletores e executar o spider quantas vezes precisar sem baixar essas páginas de novo.

Ative com `development_mode = True` no seu spider:

```python
class MySpider(Spider):
    name = "my_spider"
    start_urls = ["https://example.com"]
    development_mode = True

    async def parse(self, response: Response):
        yield {"title": response.css("title::text").get("")}
```

A primeira execução baixa as páginas e salva cada resposta em disco. Nas seguintes, as mesmas solicitações são atendidas pelo cache. Com `robots_txt_obey=True`, as regras de robots.txt são verificadas antes da consulta ao cache.

### Local do cache {#cache-location}

Por padrão, as respostas são salvas em `.scrapling_cache/{spider.name}/`, dentro do diretório de trabalho atual. É o diretório de onde você executou o spider, **não** aquele que contém seu arquivo. Você pode mudar isso com `development_cache_dir`:

```python
class MySpider(Spider):
    name = "my_spider"
    start_urls = ["https://example.com"]
    development_mode = True
    development_cache_dir = "/tmp/my_spider_cache"
```

### Como funciona {#how-it-works_1}

1. **Chave do cache**: cada resposta é identificada pela impressão digital da solicitação. Mudar atributos que afetam essa impressão (`fp_include_kwargs`, `fp_include_headers`, `fp_keep_fragments`) fará uma nova solicitação ao site.
2. **Formato**: um arquivo JSON por resposta, com o nome `{fingerprint_hex}.json`. O corpo é codificado em base64 para manter os dados binários intactos. A gravação é atômica: cria um arquivo temporário e depois o renomeia.
3. **Reutilização**: se houver uma resposta no cache, o motor pula o download, `download_delay`, os limites de ritmo e as novas tentativas de `is_blocked()`. A resposta salva vai direto para o callback.
4. **Estatísticas**: solicitações atendidas pelo cache entram em `requests_count`, `response_bytes` e nos contadores por código de status, como em um rastreamento normal. `cache_hits` e `cache_misses` mostram quantas solicitações encontraram uma resposta salva e quantas não encontraram.

### Limpar o cache {#clearing-the-cache}

O cache não expira automaticamente. Para baixar tudo de novo, remova seu diretório ou chame diretamente o método `clear()` do gerenciador.

!!! warning "Atenção"

    Este modo é feito para desenvolvimento, não para produção. As respostas salvas nunca expiram e, ao reutilizá-las, os limites de ritmo e as novas tentativas de solicitações bloqueadas não são aplicados. Não publique um spider com `development_mode = True`.

## Streaming {#streaming}

Para spiders que demoram muito ou aplicações que precisam dos dados em tempo real, use `stream()` em vez de `start()`:

```python
import anyio

async def main():
    spider = MySpider()
    async for item in spider.stream():
        print(f"Got item: {item}")
        # Access real-time stats
        print(f"Items so far: {spider.stats.items_scraped}")
        print(f"Requests made: {spider.stats.requests_count}")

anyio.run(main)
```

Principais diferenças em relação a `start()`:

- Você deve chamar `stream()` de um contexto assíncrono.
- Os itens são entregues um a um conforme são extraídos, em vez de serem reunidos em uma lista.
- Você pode consultar `spider.stats` durante a iteração para ver estatísticas em tempo real.

!!! abstract "Mais informações"

    A seção [Resultados e estatísticas](#results-statistics) explica todas as estatísticas disponíveis em `spider.stats`.

Você também pode combinar esse recurso com checkpoints. Assim, pode criar interfaces que mostram dados em tempo real e permitem pausar e retomar o rastreamento.

```python
import anyio

async def main():
    spider = MySpider(crawldir="crawl_data/my_spider")
    async for item in spider.stream():
        print(f"Got item: {item}")
        # Access real-time stats
        print(f"Items so far: {spider.stats.items_scraped}")
        print(f"Requests made: {spider.stats.requests_count}")

anyio.run(main)
```

Você também pode usar `spider.pause()` para parar o spider do exemplo acima. Se não tiver ativado checkpoints, ele apenas encerra o rastreamento.

## Hooks do ciclo de vida {#lifecycle-hooks}

O spider oferece hooks, métodos que você pode redefinir para adicionar sua lógica em diferentes etapas do rastreamento:

### on_start {#on_start}

Chamado antes de começar. Use para preparar o trabalho, como carregar dados ou iniciar recursos:

```python
async def on_start(self, resuming: bool = False):
    self.logger.info("Spider starting up")
    # Load seed URLs from a database, initialize counters, etc.
```

### on_close {#on_close}

Chamado quando o rastreamento termina, tanto se foi concluído quanto se foi pausado. Use para liberar recursos:

```python
async def on_close(self):
    self.logger.info("Spider shutting down")
    # Close database connections, flush buffers, etc.
```

### on_error {#on_error}

Chamado quando uma solicitação falha com uma exceção. Use para registrar erros ou aplicar sua própria lógica de recuperação:

```python
async def on_error(self, request: Request, error: Exception):
    self.logger.error(f"Failed: {request.url} - {error}")
    # Log to error tracker, save failed URL for later, etc.
```

### on_scraped_item {#on_scraped_item}

Chamado para cada item extraído antes de adicioná-lo aos resultados. Retorne o item, alterado ou não, para mantê-lo. Retorne `None` para descartá-lo:

```python
async def on_scraped_item(self, item: dict) -> dict | None:
    # Drop items without a title
    if not item.get("title"):
        return None

    # Modify items (e.g., add timestamps)
    item["scraped_at"] = "2026-01-01"
    return item
```

!!! tip "Dica"

    Você também pode usar esse hook para enviar os itens ao seu próprio fluxo de processamento e removê-los dos resultados do spider.

### start_requests {#start_requests}

Redefina `start_requests()` para gerar suas próprias solicitações iniciais em vez de usar `start_urls`:

```python
async def start_requests(self):
    # POST request to log in first
    yield Request(
        "https://example.com/login",
        method="POST",
        data={"user": "admin", "pass": "secret"},
        callback=self.after_login,
    )

async def after_login(self, response: Response):
    # Now crawl the authenticated pages
    yield response.follow("/dashboard", callback=self.parse)
```

## Resultados e estatísticas {#results-statistics}

O `CrawlResult` retornado por `start()` contém os itens extraídos e estatísticas detalhadas:

```python
result = MySpider().start()

# Items
print(f"Total items: {len(result.items)}")
result.items.to_json("output.json", indent=True)

# Did the crawl complete?
print(f"Completed: {result.completed}")
print(f"Paused: {result.paused}")

# Statistics
stats = result.stats
print(f"Requests: {stats.requests_count}")
print(f"Failed: {stats.failed_requests_count}")
print(f"Blocked: {stats.blocked_requests_count}")
print(f"Offsite filtered: {stats.offsite_requests_count}")
print(f"Robots.txt disallowed: {stats.robots_disallowed_count}")
print(f"Cache hits: {stats.cache_hits}")
print(f"Cache misses: {stats.cache_misses}")
print(f"Items scraped: {stats.items_scraped}")
print(f"Items dropped: {stats.items_dropped}")
print(f"Response bytes: {stats.response_bytes}")
print(f"Duration: {stats.elapsed_seconds:.1f}s")
print(f"Speed: {stats.requests_per_second:.1f} req/s")
```

### Estatísticas detalhadas {#detailed-stats}

O objeto `CrawlStats` registra informações detalhadas:

```python
stats = result.stats

# Status code distribution
print(stats.response_status_count)
# {'status_200': 150, 'status_404': 3, 'status_403': 1}

# Bytes downloaded per domain
print(stats.domains_response_bytes)
# {'example.com': 1234567, 'api.example.com': 45678}

# Requests per session
print(stats.sessions_requests_count)
# {'http': 120, 'stealth': 34}

# Proxies used during the crawl
print(stats.proxies)
# ['http://proxy1:8080', 'http://proxy2:8080']

# Log level counts
print(stats.log_levels_counter)
# {'debug': 200, 'info': 50, 'warning': 3, 'error': 1, 'critical': 0}

# Timing information
print(stats.start_time)       # Unix timestamp when crawl started
print(stats.end_time)         # Unix timestamp when crawl finished
print(stats.download_delay)   # The download delay used (seconds)

# Concurrency settings used
print(stats.concurrent_requests)             # Global concurrency limit
print(stats.concurrent_requests_per_domain)  # Per-domain concurrency limit

# AutoThrottle
print(stats.autothrottle_enabled)  # Whether the adaptive delay was on
print(stats.autothrottle_delays)   # Final delay per domain, {'example.com': 0.62}

# Custom stats (set by your spider code)
print(stats.custom_stats)
# {'login_attempts': 3, 'pages_with_errors': 5}

# Export everything as a dict
print(stats.to_dict())
```

## Logs {#logging}

O spider tem um logger integrado, disponível em `self.logger`. Ele já usa o nome do spider e permite estes ajustes:

| Atributo | Padrão | Descrição |
|----------|--------|-----------|
| `logging_level` | `logging.DEBUG` | Nível mínimo registrado |
| `logging_format` | `"[%(asctime)s]:({spider_name}) %(levelname)s: %(message)s"` | Formato das mensagens |
| `logging_date_format` | `"%Y-%m-%d %H:%M:%S"` | Formato da data nas mensagens |
| `log_file` | `None` | Caminho de um arquivo de log, além da saída no console |

```python
import logging

class MySpider(Spider):
    name = "my_spider"
    start_urls = ["https://example.com"]
    logging_level = logging.INFO
    log_file = "logs/my_spider.log"

    async def parse(self, response: Response):
        self.logger.info(f"Processing {response.url}")
        yield {"title": response.css("title::text").get("")}
```

Se o diretório do arquivo de log não existir, ele será criado automaticamente. O console e o arquivo usam o mesmo formato.
