---
title: "Alterne proxies e repita solicitações bloqueadas"
description: "Use proxies e estratégias de rotação nos spiders do Scrapling. Detecte bloqueios, repita solicitações e troque sessões HTTP por sessões de navegador."
---

# Gerenciar proxies e bloqueios {#proxy-management-and-handling-blocks}

## Introdução {#introduction}

!!! success "Antes de começar"

    1. Leia a página [Primeiros passos](getting-started.md) para aprender a criar e executar um spider básico.
    2. Leia a página [Sessões](sessions.md) para aprender a configurá-las.

Ao extrair muitos dados, você costuma precisar alternar entre vários proxies para evitar limites de solicitações e bloqueios. O `ProxyRotator` do Scrapling facilita esse processo. Funciona com todos os tipos de sessão e se integra ao sistema de novas tentativas para solicitações bloqueadas.

Se você não sabe o que é um proxy ou como escolher um, [este guia pode ajudar](https://substack.thewebscraping.club/p/everything-about-proxies).

## ProxyRotator {#proxyrotator}

A classe `ProxyRotator` gerencia uma lista de proxies e alterna entre eles automaticamente. Passe-a para qualquer tipo de sessão pelo parâmetro `proxy_rotator`:

```python
from scrapling.spiders import Spider, Response
from scrapling.fetchers import FetcherSession, ProxyRotator

class MySpider(Spider):
    name = "my_spider"
    start_urls = ["https://example.com"]

    def configure_sessions(self, manager):
        rotator = ProxyRotator([
            "http://proxy1:8080",
            "http://proxy2:8080",
            "http://user:pass@proxy3:8080",
        ])
        manager.add("default", FetcherSession(proxy_rotator=rotator))

    async def parse(self, response: Response):
        # Check which proxy was used
        print(f"Proxy used: {response.meta.get('proxy')}")
        yield {"title": response.css("title::text").get("")}
```

Cada solicitação recebe o próximo proxy da rotação. O proxy usado fica salvo em `response.meta["proxy"]`, para que você saiba qual obteve cada página.

Para usar com sessões de navegador, configure assim:

```python
from scrapling.fetchers import AsyncStealthySession, ProxyRotator

# String proxies work for all session types
rotator = ProxyRotator([
    "http://proxy1:8080",
    "http://proxy2:8080",
])

# Dict proxies (Playwright format) work for browser sessions
rotator = ProxyRotator([
    {"server": "http://proxy1:8080", "username": "user", "password": "pass"},
    {"server": "http://proxy2:8080"},
])

# Then inside the spider
def configure_sessions(self, manager):
    rotator = ProxyRotator(["http://proxy1:8080", "http://proxy2:8080"])
    manager.add("browser", AsyncStealthySession(proxy_rotator=rotator))
```

!!! info "Informação"

    1. Você não pode usar `proxy_rotator` junto com os parâmetros fixos `proxy` ou `proxies` na mesma sessão. Escolha uma opção ao configurar a sessão. Depois, se quiser, indique outro proxy em uma solicitação específica, como mostrado mais adiante.
    2. Por padrão, as sessões de navegador usam um contexto persistente com um grupo de abas. Navegadores não permitem escolher um proxy por aba. Por isso, ao usar `ProxyRotator`, o fetcher abre um contexto separado para cada proxy, com uma aba por contexto. Quando o trabalho da aba termina, a aba e seu contexto são fechados.

## Estratégias próprias de rotação {#custom-rotation-strategies}

Por padrão, `ProxyRotator` percorre os proxies em ordem e volta ao primeiro depois do último.

Você pode passar uma função com sua própria estratégia para mudar esse comportamento. Ela deve ter esta assinatura:

```python
from scrapling.core._types import ProxyType

def my_strategy(proxies: list, current_index: int) -> tuple[ProxyType, int]:
    ...
```

A função recebe a lista de proxies e o índice atual. Deve retornar o proxy escolhido e o próximo índice.

Estes são alguns exemplos de estratégias que você pode usar.

### Rotação aleatória {#random-rotation}

```python
import random
from scrapling.fetchers import ProxyRotator

def random_strategy(proxies, current_index):
    idx = random.randint(0, len(proxies) - 1)
    return proxies[idx], idx

rotator = ProxyRotator(
    ["http://proxy1:8080", "http://proxy2:8080", "http://proxy3:8080"],
    strategy=random_strategy,
)
```

### Rotação por pesos {#weighted-rotation}

```python
import random

def weighted_strategy(proxies, current_index):
    # First proxy gets 60% of traffic, others split the rest
    weights = [60] + [40 // (len(proxies) - 1)] * (len(proxies) - 1)
    proxy = random.choices(proxies, weights=weights, k=1)[0]
    return proxy, current_index  # Index doesn't matter for weighted

rotator = ProxyRotator(proxies, strategy=weighted_strategy)
```

## Escolher um proxy por solicitação {#per-request-proxy-override}

Você pode ignorar o rotador em uma solicitação específica passando o argumento `proxy=`:

```python
async def parse(self, response: Response):
    # This request uses the rotator's next proxy
    yield response.follow("/page1", callback=self.parse_page)

    # This request uses a specific proxy, bypassing the rotator
    yield response.follow(
        "/special-page",
        callback=self.parse_page,
        proxy="http://special-proxy:8080",
    )
```

Isso é útil quando uma página exige um proxy específico, como um proxy de uma determinada região para acessar conteúdo local.

## Tratar solicitações bloqueadas {#blocked-request-handling}

O spider inclui detecção de bloqueios e novas tentativas. Por padrão, considera bloqueadas as respostas com estes códigos HTTP: `401`, `403`, `407`, `429`, `444`, `500`, `502`, `503` e `504`.

O sistema de novas tentativas funciona assim:

1. Quando chega uma resposta, o spider chama `is_blocked(response)`.
2. Se detectar bloqueio, copia a solicitação e chama `retry_blocked_request()` para que você possa modificá-la antes da nova tentativa.
3. A solicitação volta à fila com `dont_filter=True`, para permitir a duplicata, e com prioridade menor, para não ser repetida imediatamente.
4. O processo se repete até `max_blocked_retries` vezes. O padrão é 3.

!!! tip "Dica"

    1. Antes da nova tentativa, os argumentos `proxy`/`proxies` são removidos da solicitação para que o rotador escolha um novo proxy.
    2. `max_blocked_retries` é independente das novas tentativas da sessão. Os contadores são separados.

### Personalizar a detecção de bloqueios {#custom-block-detection}

Redefina `is_blocked()` para adicionar sua própria lógica:

```python
class MySpider(Spider):
    name = "my_spider"
    start_urls = ["https://example.com"]

    async def is_blocked(self, response: Response) -> bool:
        # Check status codes (default behavior)
        if response.status in {403, 429, 503}:
            return True

        # Check response content
        body = response.body.decode("utf-8", errors="ignore")
        if "access denied" in body.lower() or "rate limit" in body.lower():
            return True

        return False

    async def parse(self, response: Response):
        yield {"title": response.css("title::text").get("")}
```

### Personalizar as novas tentativas {#customizing-retries}

Redefina `retry_blocked_request()` para modificar a solicitação antes de tentar novamente. O atributo `max_blocked_retries` controla quantas vezes uma solicitação bloqueada é repetida. O padrão é 3:

```python
from scrapling.spiders import Spider, SessionManager, Request, Response
from scrapling.fetchers import FetcherSession, AsyncStealthySession


class MySpider(Spider):
    name = "my_spider"
    start_urls = ["https://example.com"]
    max_blocked_retries = 5

    def configure_sessions(self, manager: SessionManager) -> None:
        manager.add('requests', FetcherSession(impersonate=['chrome', 'firefox', 'safari']))
        manager.add('stealth', AsyncStealthySession(block_webrtc=True), lazy=True)

    async def retry_blocked_request(self, request: Request, response: Response) -> Request:
        request.sid = "stealth"
        self.logger.info(f"Retrying blocked request: {request.url}")
        return request

    async def parse(self, response: Response):
        yield {"title": response.css("title::text").get("")}
```

Neste exemplo, a detecção de bloqueios padrão é mantida. O spider usa solicitações HTTP até receber um bloqueio e, então, muda para o navegador com proteção contra detecção.

Agora podemos combinar tudo:

```python
from scrapling.spiders import Spider, SessionManager, Request, Response
from scrapling.fetchers import FetcherSession, AsyncStealthySession, ProxyRotator


cheap_proxies = ProxyRotator([ "http://proxy1:8080", "http://proxy2:8080"])

# A format acceptable by the browser
expensive_proxies = ProxyRotator([
    {"server": "http://residential_proxy1:8080", "username": "user", "password": "pass"},
    {"server": "http://residential_proxy2:8080", "username": "user", "password": "pass"},
    {"server": "http://mobile_proxy1:8080", "username": "user", "password": "pass"},
    {"server": "http://mobile_proxy2:8080", "username": "user", "password": "pass"},
])


class MySpider(Spider):
    name = "my_spider"
    start_urls = ["https://example.com"]
    max_blocked_retries = 5

    def configure_sessions(self, manager: SessionManager) -> None:
        manager.add('requests', FetcherSession(impersonate=['chrome', 'firefox', 'safari'], proxy_rotator=cheap_proxies))
        manager.add('stealth', AsyncStealthySession(block_webrtc=True, proxy_rotator=expensive_proxies), lazy=True)

    async def retry_blocked_request(self, request: Request, response: Response) -> Request:
        request.sid = "stealth"
        self.logger.info(f"Retrying blocked request: {request.url}")
        return request

    async def parse(self, response: Response):
        yield {"title": response.css("title::text").get("")}
```

A lógica é a seguinte: as solicitações usam proxies baratos, como os de datacenter, até receberem um bloqueio. Depois são repetidas com proxies de maior qualidade, como os residenciais ou móveis.
