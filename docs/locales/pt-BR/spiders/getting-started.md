---
title: "Crie seu primeiro rastreador web em Python com Scrapling"
description: "Crie um spider que extraia dados, siga a paginação e exporte os resultados. Aprenda a usar URLs iniciais, callbacks, limites de domínio e robots.txt."
---

# Primeiros passos {#getting-started}

## Introdução {#introduction}

!!! success "Antes de começar"

    1. Leia a página [Conceitos básicos dos fetchers](../fetching/choosing.md) para conhecer os tipos de fetcher e saber quando usar cada um.
    2. Leia a página [Classes principais](../parsing/main_classes.md) para conhecer as classes [Selector](../parsing/main_classes.md#selector) e [Response](../fetching/choosing.md#response-object).
    3. Leia a página [Arquitetura](architecture.md) para entender como o sistema de spiders funciona.

O sistema de spiders permite rastrear várias páginas ao mesmo tempo com poucas linhas de código. Se você já usou Scrapy, vai reconhecer a forma de trabalhar. Se não, este guia explica tudo o que você precisa para começar.

## Seu primeiro spider {#your-first-spider}

Um spider é uma classe que define como percorrer sites e extrair seus dados. Este é o exemplo mais simples:

```python
from scrapling.spiders import Spider, Response

class QuotesSpider(Spider):
    name = "quotes"
    start_urls = ["https://quotes.toscrape.com"]

    async def parse(self, response: Response):
        for quote in response.css("div.quote"):
            yield {
                "text": quote.css("span.text::text").get(""),
                "author": quote.css("small.author::text").get(""),
            }
```

Todo spider precisa de três coisas:

1. **`name`**: um nome único para o spider.
2. **`start_urls`**: uma lista de URLs para iniciar o rastreamento.
3. **`parse()`**: um método gerador assíncrono que processa cada resposta e produz os resultados.

O método `parse()` contém a lógica de extração. Você usa os mesmos métodos de seleção de [Selector](../parsing/main_classes.md#selector)/[Response](../fetching/choosing.md#response-object) do Scrapling e entrega os itens extraídos como dicionários com `yield`.

## Executar o spider {#running-the-spider}

Para executar seu spider, crie uma instância e chame `start()`:

```python
result = QuotesSpider().start()
```

O método `start()` cuida da execução assíncrona, então você não precisa gerenciar loops de eventos. Enquanto o spider roda, ele registra o que acontece no terminal. Ao terminar, mostra estatísticas detalhadas.

Você também pode consultar essas estatísticas no objeto `CrawlResult` retornado:

```python
result = QuotesSpider().start()

# Access scraped items
for item in result.items:
    print(item["text"], "-", item["author"])

# Check statistics
print(f"Scraped {result.stats.items_scraped} items")
print(f"Made {result.stats.requests_count} requests")
print(f"Took {result.stats.elapsed_seconds:.1f} seconds")

# Did the crawl finish or was it paused?
print(f"Completed: {result.completed}")
```

## Seguir links {#following-links}

A maioria dos rastreamentos precisa seguir links entre várias páginas. Use `response.follow()` para criar as próximas solicitações:

```python
from scrapling.spiders import Spider, Response

class QuotesSpider(Spider):
    name = "quotes"
    start_urls = ["https://quotes.toscrape.com"]

    async def parse(self, response: Response):
        # Extract items from the current page
        for quote in response.css("div.quote"):
            yield {
                "text": quote.css("span.text::text").get(""),
                "author": quote.css("small.author::text").get(""),
            }

        # Follow the "next page" link
        next_page = response.css("li.next a::attr(href)").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)
```

`response.follow()` resolve URLs relativas usando a URL da página atual. Por padrão, também usa essa página como valor do cabeçalho `Referer`.

Você pode enviar as solicitações para callbacks diferentes conforme o tipo de página:

```python
async def parse(self, response: Response):
    for link in response.css("a.product-link::attr(href)").getall():
        yield response.follow(link, callback=self.parse_product)

async def parse_product(self, response: Response):
    yield {
        "name": response.css("h1::text").get(""),
        "price": response.css(".price::text").get(""),
    }
```

!!! note "Nota"

    Todos os callbacks devem ser métodos geradores assíncronos, com `async def` e `yield`.

## Exportar dados {#exporting-data}

O objeto `ItemList` em `result.items` inclui métodos para exportar os dados:

```python
result = QuotesSpider().start()

# Export as JSON
result.items.to_json("quotes.json")

# Export as JSON with pretty-printing
result.items.to_json("quotes.json", indent=True)

# Export as JSON Lines (one JSON object per line)
result.items.to_jsonl("quotes.jsonl")

# Export as CSV or XML
result.items.to_csv("quotes.csv")
result.items.to_xml("quotes.xml")
```

Todos criam os diretórios necessários se eles ainda não existirem.

`to_csv()` cria uma coluna para cada chave encontrada nos itens. Se um item não tiver uma chave, a célula fica vazia. Use `fields=[...]` para escolher as colunas e sua ordem, ou `delimiter="\t"` para criar um arquivo TSV. `to_xml()` coloca cada item em uma tag `<item>`, dentro da raiz `<items>`. Você pode mudar os dois nomes com `root_tag` e `item_tag`.

Nos dois formatos, valores que não são escalares simples, como listas ou dicionários aninhados, são gravados como JSON para que nenhum dado seja perdido.

## Limitar os domínios {#filtering-domains}

Use `allowed_domains` para limitar o spider a certos domínios. Isso evita que ele siga links para outros sites por engano:

```python
class MySpider(Spider):
    name = "my_spider"
    start_urls = ["https://example.com"]
    allowed_domains = {"example.com"}

    async def parse(self, response: Response):
        for link in response.css("a::attr(href)").getall():
            # Links to other domains are silently dropped
            yield response.follow(link, callback=self.parse)
```

Os subdomínios são incluídos automaticamente. Por exemplo, `allowed_domains = {"example.com"}` também permite `sub.example.com`, `blog.example.com` e outros subdomínios.

Cada solicitação descartada é contada em `stats.offsite_requests_count`, para que você veja quantas foram ignoradas.

## Respeitar robots.txt {#robotstxt-compliance}

Defina `robots_txt_obey = True` para que o spider consulte as regras de robots.txt antes de rastrear um domínio:

```python
class PoliteSpider(Spider):
    name = "polite"
    start_urls = ["https://example.com"]
    robots_txt_obey = True

    async def parse(self, response: Response):
        for link in response.css("a::attr(href)").getall():
            yield response.follow(link, callback=self.parse)
```

Com essa opção ativa, o spider:

1. **Baixa robots.txt** de todos os domínios em `start_urls` antes de começar. Esses downloads acontecem ao mesmo tempo.
2. **Verifica cada solicitação** com as regras `Disallow` do domínio. As solicitações não permitidas são descartadas sem mensagens e contadas em `stats.robots_disallowed_count`.
3. **Respeita as instruções `Crawl-delay` e `Request-rate`**, usando o maior valor entre a instrução e o seu `download_delay`. Assim, robots.txt pode aumentar a espera, mas nunca reduzi-la. Se AutoThrottle estiver ativo, sua espera máxima também limita esse valor. Defina `autothrottle_max_delay` com um valor alto o bastante para respeitar a espera necessária.

Os arquivos robots.txt são baixados com a sessão padrão do spider e mantidos em cache por domínio durante todo o rastreamento. Se um domínio que não está em `start_urls` for descoberto depois, seu robots.txt será baixado antes da primeira solicitação para ele.

**Nota:** `robots_txt_obey` vem desativado para evitar mudanças inesperadas de comportamento. Ativá-lo não altera os limites de concorrência (`concurrent_requests`, `concurrent_requests_per_domain`). Apenas a espera entre solicitações é ajustada.

Se você preferir não escolher um `download_delay` manualmente, defina `autothrottle_enabled = True`. O spider ajustará a espera de cada domínio conforme a velocidade das respostas e reduzirá o ritmo quando detectar bloqueios. Veja [AutoThrottle](advanced.md#autothrottle).

## Próximos passos {#whats-next}

Agora que você conhece o básico, pode consultar:

- [Solicitações e respostas](requests-responses.md): prioridade, remoção de duplicatas, metadados e mais.
- [Sessões](sessions.md): diferentes tipos de fetcher, como HTTP, navegador e navegador com proteção contra detecção, no mesmo spider.
- [Gerenciamento de proxies e bloqueios](proxy-blocking.md): rotação de proxies entre solicitações e tratamento de bloqueios.
- [Recursos avançados](advanced.md): controle de concorrência, AutoThrottle, pausa e retomada, streaming, hooks do ciclo de vida e logs.
