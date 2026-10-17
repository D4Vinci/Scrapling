---
title: "Solicitações, callbacks e Response.follow nos spiders"
description: "Crie solicitações, passe metadados e siga links com response.follow. Aprenda a usar callbacks, prioridades e remoção de solicitações duplicadas."
---

# Solicitações e respostas {#requests-responses}

!!! success "Antes de começar"

    1. Leia a página [Primeiros passos](getting-started.md) para aprender a criar e executar um spider básico.

Esta página explica o objeto `Request`: como criar solicitações, passar dados entre callbacks, controlar a prioridade e as duplicatas, e seguir links com `response.follow()`.

## O objeto Request {#the-request-object}

Um `Request` representa uma URL que você quer obter. Você pode criar solicitações diretamente ou por `response.follow()`:

```python
from scrapling.spiders import Request

# Direct construction
request = Request(
    "https://example.com/page",
    callback=self.parse_page,
    priority=5,
)

# Via response.follow (preferred in callbacks)
request = response.follow("/page", callback=self.parse_page)
```

Estes são todos os argumentos aceitos por `Request`:

| Argumento | Tipo | Padrão | Descrição |
|-----------|------|--------|-----------|
| `url` | `str` | *obrigatório* | URL que será obtida |
| `sid` | `str` | `""` | ID da sessão. Envia a solicitação para uma sessão específica (veja [Sessões](sessions.md)) |
| `callback` | `callable` | `None` | Método gerador assíncrono que processa a resposta. Usa `parse()` por padrão |
| `priority` | `int` | `0` | Valores mais altos são processados primeiro |
| `dont_filter` | `bool` | `False` | Se for `True`, permite solicitações duplicadas |
| `meta` | `dict` | `{}` | Metadados de qualquer tipo que são passados à resposta |
| `**kwargs` | | | Argumentos adicionais passados ao método de download da sessão, como `headers`, `method` ou `data` |

Os argumentos adicionais são enviados diretamente à sessão. Por exemplo, para fazer uma solicitação POST:

```python
yield Request(
    "https://example.com/api",
    method="POST",
    data={"key": "value"},
    callback=self.parse_result,
)
```

## Response.follow() {#responsefollow}

`response.follow()` é a forma recomendada de criar novas solicitações dentro de um callback. Tem algumas vantagens sobre criar objetos `Request` diretamente:

- Resolve **URLs relativas** usando a URL da página atual.
- Usa a URL da página atual como valor padrão do **cabeçalho Referer**.
- Herda os **argumentos de sessão** da solicitação original, como cabeçalhos e configuração de proxy, exceto `method`, `params`, `data`, `json`, `files` e `multipart`. Assim, os links são seguidos com solicitações GET simples.
- Herda o **callback, o ID da sessão e a prioridade** da solicitação original se você não definir novos valores.

```python
async def parse(self, response: Response):
    # Minimal - inherits callback, sid, priority from current request
    yield response.follow("/next-page")

    # Override specific fields
    yield response.follow(
        "/product/123",
        callback=self.parse_product,
        priority=10,
    )

    # Pass additional metadata to
    yield response.follow(
        "/details",
        callback=self.parse_details,
        meta={"category": "electronics"},
    )
```

| Argumento | Tipo | Padrão | Descrição |
|-----------|------|--------|-----------|
| `url` | `str` | *obrigatório* | URL que será seguida, absoluta ou relativa |
| `sid` | `str` | `""` | ID da sessão. Se estiver vazio, é herdado da solicitação original |
| `callback` | `callable` | `None` | Método callback. Se for `None`, é herdado da solicitação original |
| `priority` | `int` | `None` | Prioridade. Se for `None`, é herdada da solicitação original |
| `dont_filter` | `bool` | `False` | Permite solicitações duplicadas |
| `meta` | `dict` | `None` | Metadados que são combinados com os da resposta |
| **`referer_flow`** | `bool` | `True` | Usa a URL atual como cabeçalho Referer |
| `**kwargs` | | | São combinados com os argumentos de sessão da solicitação original |

### Desativar o envio de Referer {#disabling-referer-flow}

Por padrão, `response.follow()` usa a URL da página atual como cabeçalho `Referer`. Para desativar:

```python
yield response.follow("/page", referer_flow=False)
```

## Callbacks {#callbacks}

Callbacks são métodos geradores assíncronos do spider que processam respostas. Devem usar `yield` para entregar um destes três tipos:

- **`dict`**: um item extraído que é adicionado aos resultados.
- **`Request`**: uma nova solicitação que entra na fila.
- **`None`**: é ignorado sem mensagens.

```python
class MySpider(Spider):
    name = "my_spider"
    start_urls = ["https://example.com"]

    async def parse(self, response: Response):
        # Yield items (dicts)
        yield {"url": response.url, "title": response.css("title::text").get("")}

        # Yield follow-up requests
        for link in response.css("a::attr(href)").getall():
            yield response.follow(link, callback=self.parse_page)

    async def parse_page(self, response: Response):
        yield {"content": response.css("article::text").get("")}
```

!!! tip "Nota"

    Todos os callbacks devem usar `async def` e `yield`, não `return`. Mesmo que um callback só entregue itens e não crie novas solicitações, ele deve continuar sendo um gerador assíncrono.

## Prioridade das solicitações {#request-priority}

Solicitações com prioridade mais alta são processadas primeiro. Isso é útil quando algumas páginas precisam ser processadas antes das outras:

```python
async def parse(self, response: Response):
    # High priority - process product pages first
    for link in response.css("a.product::attr(href)").getall():
        yield response.follow(link, callback=self.parse_product, priority=10)

    # Low priority - pagination links processed after products
    next_page = response.css("a.next::attr(href)").get()
    if next_page:
        yield response.follow(next_page, callback=self.parse, priority=0)
```

Com `response.follow()`, a prioridade é herdada da solicitação original, a menos que você defina outra.

## Remover duplicatas {#deduplication}

O spider evita repetir solicitações usando uma impressão digital calculada a partir da URL, do método HTTP, do corpo e do ID da sessão. Se duas solicitações gerarem a mesma impressão digital, a segunda será descartada sem mensagens.

Para permitir solicitações duplicadas, por exemplo ao voltar a uma página depois de fazer login, use `dont_filter=True`:

```python
yield Request("https://example.com/dashboard", dont_filter=True, callback=self.parse_dashboard)

# Or with response.follow
yield response.follow("/dashboard", dont_filter=True, callback=self.parse_dashboard)
```

Você pode ajustar quais dados entram na impressão digital com estes atributos de classe do spider:

| Atributo | Padrão | Efeito |
|----------|--------|--------|
| `fp_include_kwargs` | `False` | Inclui na impressão digital os argumentos adicionais passados ao método de download da sessão, como cabeçalhos |
| `fp_keep_fragments` | `False` | Mantém os fragmentos da URL (`#section`) ao calcular a impressão digital |
| `fp_include_headers` | `False` | Inclui os cabeçalhos da solicitação na impressão digital |

Por exemplo, para tratar `https://example.com/page#section1` e `https://example.com/page#section2` como URLs diferentes:

```python
class MySpider(Spider):
    name = "my_spider"
    fp_keep_fragments = True
    # ...
```

## Metadados da solicitação {#request-meta}

O dicionário `meta` permite passar dados entre callbacks. É útil quando você precisa de informações de uma página para processar outra:

```python
async def parse(self, response: Response):
    for product in response.css("div.product"):
        category = product.css("span.category::text").get("")
        link = product.css("a::attr(href)").get()
        if link:
            yield response.follow(
                link,
                callback=self.parse_product,
                meta={"category": category},
            )

async def parse_product(self, response: Response):
    yield {
        "name": response.css("h1::text").get(""),
        "price": response.css(".price::text").get(""),
        # Access meta from the request
        "category": response.meta.get("category", ""),
    }
```

Com `response.follow()`, os metadados da resposta atual são combinados com os novos que você fornecer. Os valores novos têm prioridade.

O sistema de spiders também salva alguns metadados automaticamente. Por exemplo, com a rotação de proxies ativa, o proxy usado em uma solicitação fica disponível em `response.meta["proxy"]`.
