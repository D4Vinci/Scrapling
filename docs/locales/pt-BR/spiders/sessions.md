---
title: "Use sessões HTTP e de navegador no mesmo rastreador"
description: "Configure sessões com nome e envie solicitações por HTTP ou por um navegador. Reutilize cookies, inicie sessões quando precisar e consulte o histórico de APIs."
---

# Sessões dos spiders {#spiders-sessions}

!!! success "Antes de começar"

    1. Leia a página [Primeiros passos](getting-started.md) para aprender a criar e executar um spider básico.
    2. Revise os [Conceitos básicos dos fetchers](../fetching/choosing.md) e as diferenças entre sessões HTTP e Stealthy.

Um spider pode usar várias sessões de fetcher ao mesmo tempo. Por exemplo, uma sessão HTTP rápida para páginas simples e um navegador com proteção contra detecção para páginas protegidas. Esta página mostra como configurar e usar as sessões.

## O que são sessões? {#what-are-sessions}

Uma sessão é uma instância de fetcher já configurada que fica ativa durante o rastreamento. Em vez de criar uma conexão ou um navegador para cada solicitação, o spider reutiliza as sessões. Isso é mais rápido e usa menos recursos.

Por padrão, cada spider cria uma única [FetcherSession](../fetching/static.md). Você pode adicionar outras sessões ou trocar a padrão redefinindo `configure_sessions()`. Use apenas a versão assíncrona de cada sessão, conforme a tabela:

| Tipo de sessão | Uso |
|----------------|-----|
| [FetcherSession](../fetching/static.md) | Solicitações HTTP rápidas, sem JavaScript |
| [AsyncStealthySession](../fetching/stealthy.md) | JavaScript, automação do navegador e acesso a sites com proteção antibot |

## Configurar sessões {#configuring-sessions}

Redefina `configure_sessions()` no spider para configurar as sessões. O parâmetro `manager` é uma instância de `SessionManager`. Use `manager.add()` para registrar cada sessão:

```python
from scrapling.spiders import Spider, Response
from scrapling.fetchers import FetcherSession

class MySpider(Spider):
    name = "my_spider"
    start_urls = ["https://example.com"]

    def configure_sessions(self, manager):
        manager.add("default", FetcherSession())

    async def parse(self, response: Response):
        yield {"title": response.css("title::text").get("")}
```

O método `manager.add()` aceita estes argumentos:

| Argumento | Tipo | Padrão | Descrição |
|-----------|------|--------|-----------|
| `session_id` | `str` | *obrigatório* | Nome usado para identificar esta sessão nas solicitações |
| `session` | `Session` | *obrigatório* | Instância da sessão |
| `default` | `bool` | `False` | Usa esta sessão como padrão |
| `lazy` | `bool` | `False` | Inicia a sessão apenas no primeiro uso |

!!! note "Notas"

    1. Se uma solicitação não indicar qual sessão deve usar, será usada a padrão. Ela é escolhida de uma destas formas:
        1. A primeira sessão adicionada ao gerenciador se torna a padrão.
        2. Você pode escolher outra ao adicioná-la com `default=True`.
    2. Não é preciso iniciar as sessões antes de passá-las ao gerenciador. O spider verifica quais ainda não foram iniciadas e as inicia.
    3. Para iniciar uma sessão apenas quando ela for necessária, use `lazy` ao adicioná-la. Por exemplo, abra o navegador no primeiro uso, em vez de abri-lo ao iniciar o spider.

## Spider com várias sessões {#multi-session-spider}

Este exemplo usa uma sessão HTTP rápida para páginas de listagem e um navegador com proteção contra detecção para páginas de detalhes com sistemas antibot:

```python
from scrapling.spiders import Spider, Response
from scrapling.fetchers import FetcherSession, AsyncStealthySession

class ProductSpider(Spider):
    name = "products"
    start_urls = ["https://shop.example.com/products"]

    def configure_sessions(self, manager):
        # Fast HTTP for listing pages (default)
        manager.add("http", FetcherSession())

        self.browser_session = AsyncStealthySession(
            headless=True,
            network_idle=True,
            record_requests=True,
        )
        manager.add("stealth", self.browser_session)

    async def parse(self, response: Response):
        for link in response.css("a.product::attr(href)").getall():
            # Route product pages through the stealth session
            yield response.follow(link, sid="stealth", callback=self.parse_product)

        next_page = response.css("a.next::attr(href)").get()
        if next_page:
            yield response.follow(next_page)

    async def parse_product(self, response: Response):
        yield {
            "name": response.css("h1::text").get(""),
            "price": response.css(".price::text").get(""),
        }

    async def on_close(self):
        for api_response in self.browser_session.network.search(
            url_pattern=r"https://api\.shop\.example\.com/.*", limit=None
        ):
            self.logger.info(f"Saved API response: {api_response.url} ({api_response.status})")
```

O exemplo mantém a instância do navegador e consulta seu histórico de respostas de API uma vez em `on_close()`, antes de fechar as sessões. O histórico inclui todas as páginas de produtos e continua legível depois do fechamento. Capturas pendentes não são aguardadas, e os limites do histórico continuam valendo.

O parâmetro `sid` indica qual sessão o spider deve usar em cada solicitação. Se você chamar `response.follow()` sem `sid`, o ID da sessão será herdado da solicitação original.

As sessões não precisam ser de classes diferentes. Você também pode usar várias instâncias da mesma classe com configurações distintas:

```python
from scrapling.spiders import Spider, Response
from scrapling.fetchers import FetcherSession

class ProductSpider(Spider):
    name = "products"
    start_urls = ["https://shop.example.com/products"]

    def configure_sessions(self, manager):
        chrome_requests = FetcherSession(impersonate="chrome")
        firefox_requests = FetcherSession(impersonate="firefox")

        manager.add("chrome", chrome_requests)
        manager.add("firefox", firefox_requests)

    async def parse(self, response: Response):
        for link in response.css("a.product::attr(href)").getall():
            yield response.follow(link, callback=self.parse_product)

        next_page = response.css("a.next::attr(href)").get()
        if next_page:
            yield response.follow(next_page, sid="firefox")

    async def parse_product(self, response: Response):
        yield {
            "name": response.css("h1::text").get(""),
            "price": response.css(".price::text").get(""),
        }
```

Outra opção é reservar uma sessão, com seus próprios cookies e estado, para certas solicitações.

## Argumentos da sessão {#session-arguments}

Os argumentos adicionais de um `Request`, ou de `response.follow(**kwargs)`, são passados ao método de download da sessão. Assim você pode ajustar uma solicitação sem mudar a configuração da sessão inteira:

```python
async def parse(self, response: Response):
    # Pass extra headers for this specific request
    yield Request(
        "https://api.example.com/data",
        headers={"Authorization": "Bearer token123"},
        callback=self.parse_api,
    )

    # Use a different HTTP method
    yield Request(
        "https://example.com/submit",
        method="POST",
        data={"field": "value"},
        sid="firefox",
        callback=self.parse_result,
    )
```

!!! warning "Atenção"

    Normalmente, com `FetcherSession`, `Fetcher` ou `AsyncFetcher`, você escolhe o método HTTP chamando `.get()`, `.post()` ou outro método. Dentro de um spider, não é possível fazer isso com `FetcherSession`. As solicitações usam _HTTP GET_ por padrão. Para usar outro método HTTP, passe-o no argumento `method`, como no exemplo acima. Isso permite que todos os tipos de sessão tenham a mesma interface `Request`.

Com a sessão `"stealth"` (`AsyncStealthySession`) do exemplo anterior, você pode passar argumentos próprios do navegador, como `wait_selector`, `page_action` ou `extra_headers`:

```python
async def parse(self, response: Response):
    # Use Cloudflare solver with the `AsyncStealthySession` we configured above
    yield Request(
        "https://nopecha.com/demo/cloudflare",
        sid="stealth",
        callback=self.parse_result,
        solve_cloudflare=True,
        block_webrtc=True,
        hide_canvas=True,
        google_search=True,
    )

    yield response.follow(
        "/dynamic-page",
        sid="stealth",
        callback=self.parse_dynamic,
        wait_selector="div.loaded",
        network_idle=True,
    )
```

!!! warning "Atenção"

    `response.follow()` herda os argumentos de sessão (**kwargs) da solicitação original, exceto `method`, `params`, `data`, `json`, `files` e `multipart`. Por isso, seguir um link depois de um POST envia um GET simples. Os argumentos novos têm prioridade sobre os herdados.

```python
from scrapling.spiders import Spider, Response
from scrapling.fetchers import FetcherSession

class ProductSpider(Spider):
    name = "products"
    start_urls = ["https://shop.example.com/products"]

    def configure_sessions(self, manager):
        manager.add("http", FetcherSession(impersonate='chrome'))

    async def parse(self, response: Response):
        # I don't want the follow request to impersonate a desktop Chrome like the previous request, but a mobile one
        # so I override it like this
        for link in response.css("a.product::attr(href)").getall():
            yield response.follow(link, impersonate="chrome131_android", callback=self.parse_product)

        next_page = response.css("a.next::attr(href)").get()
        if next_page:
            yield response.follow(next_page)

    async def parse_product(self, response: Response):
        yield {
            "name": response.css("h1::text").get(""),
            "price": response.css(".price::text").get(""),
        }
```

!!! info "Informação"

    Ao encerrar o spider, o gerenciador verifica se ainda há sessões ativas e as fecha antes de terminar.
