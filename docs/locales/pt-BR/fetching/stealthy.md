---
title: "Extraia dados de sites com JavaScript usando StealthyFetcher"
description: "Carregue páginas, espere pelos dados, reutilize logins e leia respostas de API em segundo plano com as sessões de navegador do Scrapling. Configure proxies e a resolução de desafios."
---

# Obter páginas com StealthyFetcher {#browser-fetching-with-stealthyfetcher}

`StealthyFetcher` carrega páginas com JavaScript e automatiza Chromium ou Google Chrome com recursos contra detecção de bots. Ele usa a [API do Playwright](https://playwright.dev/python/docs/intro) com ajustes para ocultar a automação.

Para automatizar uma página, você precisará conhecer um pouco da [API Page do Playwright](https://playwright.dev/python/docs/api/class-page), como veremos depois.

!!! success "Antes de começar"

    1. Leia [Conceitos básicos dos fetchers](../fetching/choosing.md) para entender o [objeto Response](../fetching/choosing.md#response-object) e escolher um fetcher.
    2. Leia [Buscar elementos](../parsing/selection.md) para aprender a buscar e extrair elementos de [Selector](../parsing/main_classes.md#selector)/[Response](../fetching/choosing.md#response-object).
    3. Leia [Classes principais](../parsing/main_classes.md) para conhecer as propriedades e os métodos que [Response](../fetching/choosing.md#response-object) herda de [Selector](../parsing/main_classes.md#selector).

## Uso básico {#basic-usage}
A forma principal de importar este fetcher é a mesma dos demais:

```python
from scrapling.fetchers import StealthyFetcher
```
Veja como configurar o analisador [aqui](choosing.md#parser-configuration-in-all-fetchers).

Vamos ver os principais argumentos com exemplos. Se preferir uma tabela de consulta com todos eles, [vá para esta seção](#full-list-of-arguments).

!!! abstract "Nota"

    A versão assíncrona de `fetch` se chama `async_fetch`.


Este fetcher oferece três opções principais de execução, que você pode combinar conforme precisar.

São elas:

### 1. Chromium incluído {#1-bundled-chromium}
```python
StealthyFetcher.fetch('https://example.com')
```
Abre o Chromium incluído, aplica os ajustes padrão de ocultação e carrega a página.

### 2. Google Chrome instalado {#2-real-chrome}
```python
StealthyFetcher.fetch('https://example.com', real_chrome=True)
```
Use esta opção se você tiver Google Chrome instalado. Ela funciona como a anterior, mas abre sua cópia do Google Chrome em vez do Chromium. Isso faz as solicitações parecerem mais reais e reduz a chance de detecção.

Se você não tiver Google Chrome, pode instalá-lo para a biblioteca com este comando no terminal:
```commandline
playwright install chrome
```

### 3. Conexão CDP {#3-cdp-connection}
```python
StealthyFetcher.fetch('https://example.com', cdp_url='ws://localhost:9222')
```
Em vez de abrir um navegador local, você pode se conectar a um navegador remoto pelo [Chrome DevTools Protocol](https://chromedevtools.github.io/devtools-protocol/).

A URL pode ser um endpoint WebSocket (`ws://`/`wss://`), como os fornecidos por serviços de navegador, ou o endpoint HTTP de um navegador, como `http://localhost:9222`.


## O que ele faz? {#what-does-it-do}

StealthyFetcher oferece estes recursos contra detecção de bots:

1. Resolve automaticamente todos os tipos de Cloudflare Turnstile e Interstitial com `solve_cloudflare=True`.
2. Evita vazamentos do ambiente de execução CDP e do WebRTC.
3. Isola a execução de JavaScript, remove várias marcas do Playwright e evita a detecção de alguns comportamentos típicos de bots.
4. Adiciona ruído ao canvas para impedir seu uso como impressão digital.
5. Corrige métodos conhecidos de detecção do modo sem interface e oferece uma opção contra detecção por diferenças de fuso horário.
6. Inclui outras opções para superar proteções.

## Lista completa de argumentos {#full-list-of-arguments}
Este fetcher e suas classes de sessão oferecem várias opções. Antes dos [exemplos](#examples), veja a lista completa:


| Argumento | Descrição | Opcional |
|:---------------------:|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|:--------:|
|          url          | URL de destino. |    ❌     |
|       headless        | Use `True` para executar o navegador sem interface visível (**padrão**) ou `False` para mostrá-lo. |    ✔️    |
|   disable_resources   | Ignora recursos desnecessários para acelerar o carregamento. Bloqueia os tipos `font`, `image`, `media`, `beacon`, `object`, `imageset`, `texttrack`, `websocket`, `csp_report` e `stylesheet`. |    ✔️    |
|        cookies        | Cookies para a próxima solicitação. |    ✔️    |
|       useragent       | String de user agent a ser usada. **Se você não informar uma, o fetcher gera uma real para o mesmo navegador e versão.** |    ✔️    |
|     network_idle      | Espera até que a página passe pelo menos 500 ms sem conexões de rede. |    ✔️    |
|       load_dom        | Espera pelo estado `domcontentloaded` para o carregamento e a execução de JavaScript. Fica ativado por padrão. |    ✔️    |
|     pierce_shadow     | Inclui o conteúdo de Shadow DOM aberto no HTML da resposta. O padrão é `False`. Pode ser definido para a sessão ou alterado por solicitação. |    ✔️    |
|        timeout        | Tempo máximo, em milissegundos, para operações e esperas da página. O padrão é 30.000 ms, ou 30 segundos. |    ✔️    |
|         wait          | Milissegundos de espera depois que tudo termina, antes de fechar a página e retornar `Response`. |    ✔️    |
|      page_action      | Função de automação que recebe `page` e roda depois de navegar. |    ✔️    |
|      page_setup       | Função que recebe `page` e roda antes de navegar. Use para registrar eventos ou rotas antes do carregamento. |    ✔️    |
|     wait_selector     | Espera até que um seletor CSS atinja um estado específico. |    ✔️    |
|      init_script      | Caminho absoluto de um arquivo JavaScript executado ao criar cada página da sessão. |    ✔️    |
|  wait_selector_state  | Estado que o seletor informado em `wait_selector` precisa atingir. _O padrão é `attached`._ |    ✔️    |
|     google_search     | Define um referer do Google. Fica ativado por padrão. |    ✔️    |
|     extra_headers     | Dicionário de cabeçalhos extras. _Se usado com `google_search`, o referer dessa opção tem prioridade._ |    ✔️    |
|         proxy         | Proxy das solicitações. Aceita uma string ou um dicionário com as chaves 'server', 'username' e 'password'. |    ✔️    |
|      real_chrome      | Ative para abrir e usar o Google Chrome instalado no seu computador. |    ✔️    |
|        locale         | Configuração regional, como `en-GB` ou `de-DE`. Afeta `navigator.language`, o cabeçalho `Accept-Language` e os formatos de números e datas. O padrão é o valor do sistema. |    ✔️    |
|      timezone_id      | Fuso horário do navegador. O padrão é o fuso do sistema. |    ✔️    |
|        cdp_url        | URL CDP à qual se conectar para controlar um navegador existente em vez de abrir outro. |    ✔️    |
|     user_data_dir     | Pasta onde são guardados dados do navegador, como cookies e armazenamento local. Por padrão, uma pasta temporária é criada. **Só funciona com sessões.** |    ✔️    |
|      extra_flags      | Lista de opções extras passadas ao iniciar o navegador. |    ✔️    |
|   solve_cloudflare    | Resolve os tipos de desafios Turnstile e Interstitial do Cloudflare antes de retornar a resposta. O padrão é `False`. |    ✔️    |
|     block_webrtc      | Faz o WebRTC respeitar os ajustes do proxy para evitar que revele o IP local. |    ✔️    |
|      hide_canvas      | Adiciona ruído aleatório ao canvas para impedir seu uso como impressão digital. |    ✔️    |
|      allow_webgl      | Ativado por padrão. Desativá-lo remove o suporte a WebGL e WebGL 2.0. Não é recomendado: muitos WAFs verificam se WebGL está disponível. |    ✔️    |
|    additional_args    | Ajustes extras para o contexto do Playwright. Têm prioridade sobre os ajustes do Scrapling. |    ✔️    |
|    selector_config    | Dicionário de ajustes do analisador ao criar o objeto `Selector`/`Response` final. |    ✔️    |
|    blocked_domains    | Conjunto de domínios que serão bloqueados, incluindo subdomínios. Por exemplo, `"example.com"` também bloqueia `"sub.example.com"`. |    ✔️    |
|       block_ads       | Bloqueia solicitações para cerca de 3500 domínios conhecidos de anúncios e rastreamento. Pode ser combinado com `blocked_domains`. |    ✔️    |
|    dns_over_https     | Envia as consultas DNS pelo DNS-over-HTTPS do Cloudflare para evitar vazamentos ao usar proxies. |    ✔️    |
|     proxy_rotator     | Objeto `ProxyRotator` para trocar de proxy automaticamente. Não pode ser combinado com `proxy`. |    ✔️    |
|        retries        | Número de tentativas para solicitações que falharam. O padrão é 3. |    ✔️    |
|      retry_delay      | Segundos de espera entre tentativas. O padrão é 1. |    ✔️    |
|    record_requests    | Guarda solicitações concluídas e respostas salvas em `session.network`. Só para sessões. O padrão é `False`. |    ✔️    |
| max_recorded_requests | Número máximo de solicitações guardadas por sessão. O padrão é 1000. O conteúdo salvo também tem limites fixos de tamanho. |    ✔️    |
|    executable_path    | Caminho absoluto de um executável de navegador próprio, usado no lugar do Chromium incluído. Útil para instalações ou versões especiais. |    ✔️    |

Nas classes de sessão, você pode definir esses argumentos para toda a sessão. Também pode alterar por solicitação os ajustes que pertencem à aba: `google_search`, `timeout`, `wait`, `page_action`, `page_setup`, `extra_headers`, `disable_resources`, `wait_selector`, `wait_selector_state`, `network_idle`, `load_dom`, `pierce_shadow`, `solve_cloudflare`, `blocked_domains`, `proxy` e `selector_config`.

!!! note "Notas"

    1. Nos meus testes, `disable_resources` acelerou as solicitações em cerca de 25% em alguns sites. Também pode reduzir o tráfego do proxy. Use com cuidado: alguns sites podem nunca terminar de carregar.
    2. `google_search` fica ativado por padrão e define o referer como `https://www.google.com/`. Se você também usar `extra_headers`, ele terá prioridade sobre o referer informado ali.
    3. Se você não definir um user agent e usar o modo sem interface, será gerado um real para a mesma versão do navegador. Se não definir um user agent e usar o navegador visível, será usado o padrão do próprio navegador, como nas versões atuais dos navegadores comuns.
    4. `init_script` é registrado no contexto do navegador e executado quando as páginas são criadas. O modo de ocultação usa o ambiente isolado do Patchright por padrão. Se `page_action` precisar ler variáveis que o script coloca em `window`, use `page.evaluate(..., isolated_context=False)` dentro da ação.

## Gerenciamento de sessões {#session-management}

Para manter o navegador aberto e enviar várias solicitações com os mesmos ajustes, use `StealthySession`/`AsyncStealthySession`. Essas classes aceitam todos os argumentos de `fetch`, permitindo configurar a sessão inteira.

```python
from scrapling.fetchers import StealthySession


with StealthySession(
    headless=True,
    disable_resources=True,
    real_chrome=True
) as session:

    page1 = session.fetch('https://example1.com')
    page2 = session.fetch('https://example2.com')
    page3 = session.fetch('https://dynamic-site.com')


```

### Uso de sessões assíncronas {#async-session-usage}

```python
import asyncio
from scrapling.fetchers import AsyncStealthySession

async def scrape_multiple_sites():
    async with AsyncStealthySession(
        network_idle=True,
        timeout=30000,
        max_pages=3
    ) as session:

        pages = await asyncio.gather(
            session.fetch('https://spa-app1.com'),
            session.fetch('https://spa-app2.com'),
            session.fetch('https://dynamic-content.com')
        )
        return pages
```

O argumento `max_pages` define o número máximo de abas que podem ficar abertas ao mesmo tempo. A sessão mantém um **conjunto de abas reutilizáveis**. Cada aba continua aberta quando sua solicitação termina. Em cada nova solicitação, a biblioteca faz o seguinte:

1. Reutiliza uma aba livre, se houver. Aplica os ajustes da solicitação (`timeout`, `extra_headers`, `disable_resources`, `blocked_domains` etc.) para não manter ajustes da anterior.
2. Se não houver uma livre, abre outra, desde que ainda não tenha atingido `max_pages`.
3. Se o limite já tiver sido atingido, verifica várias vezes por segundo se uma aba ficou livre, por até 60 segundos. Depois disso, gera `TimeoutError`. Isso pode acontecer se o site parar de responder.

As abas que apresentam erro são fechadas e substituídas. Você também pode fechar todas com `session.close_pages()`. A próxima solicitação abrirá uma nova.

Assim, você pode obter várias URLs ao mesmo tempo no mesmo navegador, economizando recursos e ganhando bastante velocidade :)

Como a aba continua aberta, a página anterior ainda está nela. O `page_setup` da próxima solicitação roda antes de sair dessa página. Isso permite encadear ações entre solicitações.

As versões de 0.3.2 a 0.4.14 fechavam cada aba ao terminar, pois a reutilização deixava ajustes passarem de uma solicitação para outra. Desde a 0.4.15, os ajustes são redefinidos a cada reutilização e as abas ficam abertas.

### Salvar e carregar o estado da sessão {#save-and-load-session-state}

Use `save_state(path)` para salvar cookies, armazenamento local e IndexedDB em um arquivo JSON. Use `load_state(path)` para restaurá-lo em outra sessão ou substituir o estado da sessão atual. Os dois aceitam uma string ou `pathlib.Path` e retornam `None`. O formato é compatível com os arquivos de estado do Playwright.

```python
from scrapling.fetchers import StealthySession

with StealthySession() as session:
    session.fetch('https://example.com')
    session.save_state('state.json')

with StealthySession() as session:
    session.load_state('state.json')
    page = session.fetch('https://example.com')
```

Salve o estado depois de fazer login ou terminar as ações do navegador. Chame os dois métodos dentro de uma sessão iniciada, depois que todas as solicitações pendentes terminarem. Carregar o arquivo substitui os cookies, o armazenamento local e o IndexedDB atuais. Obtenha ou recarregue a página para usar o login restaurado: carregar o estado não muda as páginas abertas.

Com `AsyncStealthySession`, use `await`:

```python
from scrapling.fetchers import AsyncStealthySession

async def restore_session():
    async with AsyncStealthySession() as session:
        await session.load_state('state.json')
        page = await session.fetch('https://example.com')
        await session.save_state('state.json')
        return page
```

Esses métodos só salvam e restauram o contexto compartilhado do navegador. Eles não afetam os contextos temporários de proxy por solicitação. Sessões com `proxy_rotator` não têm um contexto compartilhado, então esses métodos geram `RuntimeError`. Um `proxy` fixo para a sessão funciona normalmente.

O arquivo não inclui `sessionStorage`, abas abertas ou ajustes do navegador. Ao salvar, o arquivo anterior é substituído e a pasta que o contém precisa existir. Erros de arquivo ou JSON são passados ao código que chamou o método.

### Vantagens das sessões {#session-benefits}

- **Reutilização do navegador**: as próximas solicitações são muito mais rápidas porque usam o mesmo navegador.
- **Cookies persistentes**: tratamento automático dos cookies e do estado, como em qualquer navegador.
- **Impressão digital constante**: a mesma impressão digital do navegador em todas as solicitações.
- **Menor uso de memória**: consome menos recursos do que abrir um navegador a cada acesso.


## Exemplos {#examples}
Fica mais fácil entender com exemplos. Vamos ver alguns.

### Controle de recursos {#resource-control}

```python

page = StealthyFetcher.fetch('https://example.com', disable_resources=True)
```

### Shadow DOM {#shadow-dom}

Algumas páginas guardam conteúdo em raízes abertas de Shadow DOM. Esse conteúdo não aparece no HTML normal da página. Ative `pierce_shadow` para incluí-lo na resposta e use CSS ou XPath como de costume:

```python
from scrapling.fetchers import StealthyFetcher

page = StealthyFetcher.fetch('https://example.com', pierce_shadow=True)
titles = page.css('product-card .title::text').getall()
```

O padrão é `False`. Você também pode ativá-lo para a sessão e desativá-lo em uma solicitação específica:

```python
from scrapling.fetchers import StealthySession

with StealthySession(pierce_shadow=True) as session:
    page = session.fetch('https://example.com')
    plain_page = session.fetch('https://example.com', pierce_shadow=False)
```

A opção funciona da mesma forma com `async_fetch` e sessões assíncronas.

Só são incluídas raízes abertas. Raízes fechadas e documentos dentro de iframes não são percorridos. Use `wait_selector` se um componente carregar depois da página.

Cada raiz aberta vira um contêiner `<shadow-root>` na resposta. Os slots mantêm suas tags e atributos e contêm os nós atribuídos a eles, ou o conteúdo alternativo quando não há nenhum. Filhos do DOM normal sem slot atribuído são omitidos. A página no navegador não muda.

```html
<product-card>
  <shadow-root>
    <div class="title">Product name</div>
    <slot name="price"><span class="price">20</span></slot>
  </shadow-root>
</product-card>
```

Seletores de descendentes atravessam esses elementos. Seletores de filhos diretos precisam incluir os contêineres e slots:

```python
titles = page.css('product-card .title::text').getall()
titles = page.css('product-card > shadow-root > .title::text').getall()
prices = page.css('product-card > shadow-root > slot[name="price"] > .price::text').getall()
```

Os contêineres e slots aparecem nos caminhos XPath, em `.children`, em `response.body` e nas exportações HTML. A extração para Markdown e texto retorna o conteúdo sem mostrar as tags. Os atributos que ocultam slots continuam disponíveis para a limpeza do conteúdo.

A cópia preserva a ordem do conteúdo, mas não calcula sua visibilidade por CSS nem o layout. Seletores com `<shadow-root>` se aplicam à resposta do Scrapling, não à página no navegador. Outros analisadores HTML podem tratar de outra forma os elementos aninhados de maneira incomum.

### Bloquear domínios {#domain-blocking}

```python

page = StealthyFetcher.fetch('https://example.com', blocked_domains={"ads.example.com", "tracker.net"})
```

### Controle de rede {#network-control}

```python

page = StealthyFetcher.fetch('https://example.com', network_idle=True)


page = StealthyFetcher.fetch('https://example.com', timeout=30000)


page = StealthyFetcher.fetch('https://example.com', proxy='http://username:password@host:port')
```

### Baixar arquivos {#downloading-files}

```python
page = StealthyFetcher.fetch('https://raw.githubusercontent.com/D4Vinci/Scrapling/main/docs/assets/main_cover.png')

with open(file='main_cover.png', mode='wb') as f:
    f.write(page.body)
```

O atributo `body` de `Response` sempre retorna `bytes`.

### Configuração antes de navegar {#pre-navigation-setup}
Para registrar eventos, rotas ou scripts antes de carregar a página, use `page_setup`. Essa função recebe `page` e roda antes da chamada a `page.goto()`.

```python
from patchright.sync_api import Page

def capture_websockets(page: Page):
    page.on("websocket", lambda ws: print(f"WebSocket opened: {ws.url}"))

page = StealthyFetcher.fetch('https://example.com', page_setup=capture_websockets)
```
Versão assíncrona:
```python
from patchright.async_api import Page

async def capture_websockets(page: Page):
    page.on("websocket", lambda ws: print(f"WebSocket opened: {ws.url}"))

page = await StealthyFetcher.async_fetch('https://example.com', page_setup=capture_websockets)
```

Você pode combinar com `page_action`: `page_setup` roda antes da navegação, e `page_action` roda depois.

### Cloudflare e opções de ocultação {#cloudflare-and-stealth-options}

```python

page = StealthyFetcher.fetch('https://nopecha.com/demo/cloudflare', solve_cloudflare=True)


page = StealthyFetcher.fetch(
    'https://protected-site.com',
    solve_cloudflare=True,
    block_webrtc=True,
    real_chrome=True,
    hide_canvas=True,
    google_search=True,
    proxy='http://username:password@host:port',  # It can also be a dictionary with only the keys 'server', 'username', and 'password'.
)
```

`solve_cloudflare` ativa a detecção e a resolução automática de todos os tipos de desafios Turnstile e Interstitial do Cloudflare:

- Desafios de JavaScript gerenciados.
- Desafios interativos, como clicar em caixas de verificação.
- Desafios invisíveis, com verificação automática em segundo plano.

Também resolve páginas personalizadas com CAPTCHA integrado.

!!! notes "**Notas importantes**"

    1. Em sites com implementações próprias, talvez você precise de `wait_selector` para esperar pelo conteúdo real depois do CAPTCHA. Alguns sites são casos bem específicos, embora tentemos criar uma solução geral.
    2. Use um timeout de pelo menos 60 segundos para dar tempo de resolver os desafios do Cloudflare.
    3. O recurso funciona com proxies e com as outras opções de ocultação.

### Automação do navegador {#browser-automation}
Aqui, você precisa conhecer a [API Page do Playwright](https://playwright.dev/python/docs/api/class-page). A função informada recebe o objeto de página do Playwright, executa as ações e então permite que o fetcher continue.

Ela roda logo depois da espera por `network_idle`, se estiver ativado, e antes da espera por `wait_selector`. Você pode usá-la para automatizar ações ou modificar a página.

Este exemplo usa os [eventos do mouse](https://playwright.dev/python/docs/api/class-mouse) para rolar a página com a roda e depois mover o mouse.
```python
from patchright.sync_api import Page

def scroll_page(page: Page):
    page.mouse.wheel(10, 0)
    page.mouse.move(100, 400)
    page.mouse.up()

page = StealthyFetcher.fetch('https://example.com', page_action=scroll_page)
```
Se usar a obtenção assíncrona, a função também precisa ser assíncrona.
```python
from patchright.async_api import Page

async def scroll_page(page: Page):
   await page.mouse.wheel(10, 0)
   await page.mouse.move(100, 400)
   await page.mouse.up()

page = await StealthyFetcher.async_fetch('https://example.com', page_action=scroll_page)
```

### Condições de espera {#wait-conditions}

```python

page = StealthyFetcher.fetch(
    'https://quotes.toscrape.com/js-delayed/',
    wait_selector='.quote',
    wait_selector_state='visible'
)
```
Se estiver ativada, esta é a última condição de espera antes de retornar a resposta. Passe um seletor CSS em `wait_selector` e um estado em `wait_selector_state`. O padrão é `attached`, que indica que o elemento está presente no DOM.

Depois, se `load_dom` estiver ativado, como ocorre por padrão, o fetcher volta a esperar pelo estado `domcontentloaded` para verificar o carregamento e a execução de JavaScript. Se você ativou `network_idle`, ele também espera de novo por `network_idle`.

Os estados disponíveis são estes ([fonte](https://playwright.dev/python/docs/api/class-page#page-wait-for-selector)):

- `attached`: espera até que o elemento esteja presente no DOM.
- `detached`: espera até que o elemento não esteja no DOM.
- `visible`: espera até que o elemento tenha uma área com tamanho maior que zero e não use `visibility:hidden`. Elementos sem conteúdo ou com `display:none` têm área vazia e não são considerados visíveis.
- `hidden`: espera até que o elemento saia do DOM, tenha área vazia ou use `visibility:hidden`. É o oposto de `'visible'`.

### Histórico de rede {#network-history}

Ative `record_requests` em uma sessão de navegador para revisar solicitações concluídas entre carregamentos de páginas, ações e abas. O histórico cobre os contextos da sessão, incluindo os temporários de proxy, e salva as respostas como objetos `Response` do Scrapling. Você pode buscar chamadas de API, erros HTTP e redirecionamentos sem enviar as solicitações de novo, e ler os cabeçalhos e o conteúdo mesmo depois de fechar a sessão. Solicitações que falharam ou ainda não terminaram são omitidas. Respostas HTTP 4xx e 5xx concluídas são incluídas.

```python
from scrapling.fetchers import StealthySession

with StealthySession(record_requests=True, max_recorded_requests=1000) as session:
    session.fetch('https://example.com', network_idle=True)

for response in session.network.search(resource_type='document', limit=None):
    print(response.meta['network_id'], response.url, response.status)
    if note := response.meta.get('body_note'):
        print(note)
    else:
        print(response.body)
        print(response.css('title::text').get())

session.network.clear()
```

A mesma API funciona com `AsyncStealthySession`. O registro fica desativado por padrão. Ao criar a sessão, use `record_requests=True` e, se necessário, `max_recorded_requests`.

- `session.network.search(url_pattern=None, method=None, resource_type=None, status=None, after_id=0, limit=100, include_static=True)` retorna os objetos `Response` salvos na ordem do ID de rede. Com `limit=None`, retorna todas as correspondências mantidas no histórico. `url_pattern` é uma expressão regular aplicada na busca; se não for válida, o erro ocorre nesse momento. `after_id` seleciona respostas com ID maior. `include_static=False` inclui solicitações XHR/fetch e erros HTTP. Use `True` para incluir todos os tipos de recurso e redirecionamentos salvos.
- `session.network.get(request_id)` retorna um `Response` salvo, ou `None` se ele já saiu do histórico.
- `session.network.clear()` limpa o histórico. Os IDs continuam aumentando e nunca são reutilizados.

Cada `Response` salvo oferece diretamente `.url`, `.method`, `.status`, `.headers`, `.request_headers`, `.body` como bytes, `.json()` e os métodos CSS/XPath. Seu `.meta` contém `network_id`, `resource_type` e `request_body`, que pode ser bytes ou `None`. Os cabeçalhos podem ficar incompletos se a leitura completa falhar. Essas leituras são locais mesmo em sessões assíncronas: não use await nem chame `.body()`. Se o conteúdo não puder ser analisado, seus bytes são mantidos, mas CSS e XPath usam um documento vazio.

Para buscar tráfego de API por URL, use `session.network.search(url_pattern=r'https://api\.example\.com/.*', limit=None)`. Adicione `resource_type='fetch'` ou `resource_type='xhr'` se precisar de apenas um tipo de solicitação.

Só é salvo o conteúdo de respostas com os valores de texto aceitos em `Content-Type`: `text/*`, tipos `+json`/`+xml`, incluindo SVG, JSON, XML, JavaScript, GraphQL e dados de formulário codificados como URL. Tipos binários, desconhecidos ou sem `Content-Type` mantêm seus metadados, mas não os bytes do conteúdo. O navegador continua carregando os recursos normalmente.

Os bytes salvos vêm do Playwright e podem ser diferentes dos bytes originais do servidor. Se forem UTF-8 válidos, o texto usa UTF-8, como no Playwright. Caso contrário, usa a codificação declarada. Os cabeçalhos não mudam.

Se o conteúdo for omitido, exceder o tamanho máximo ou não puder ser lido, retorna `b''` e informa o motivo em `response.meta.get('body_note')`. Conteúdo que não é texto usa `Non-text body; not saved.`. Os metadados e cabeçalhos disponíveis são mantidos. Texto salvo, mesmo vazio, não tem nota. Respostas HEAD e status 204, 205 e 304 ficam vazios, sem nota.

Os métodos `search`, `get` e `clear` são locais e síncronos, mesmo nas sessões assíncronas. Uma entrada só aparece depois que sua resposta é convertida e salva. Os eventos do navegador são processados enquanto o Playwright está ativo. Capturas assíncronas também precisam que o loop de eventos esteja rodando. Ler o histórico não espera pelas capturas pendentes.

Fechar uma sessão também não espera pelas capturas. As que ainda estiverem em andamento quando a página mudar ou o contexto fechar podem ser omitidas. As respostas já salvas continuam disponíveis após o fechamento.

Por padrão, o histórico guarda até 1000 solicitações. Cada corpo de resposta tem limite de 1 MiB, e todos juntos têm limite de 20 MiB. Ao atingir um limite, os registros antigos são removidos. Os limites de conteúdo são fixos e não podem ser alterados na sessão. Eles cobrem as entradas guardadas e os bytes das respostas, não a memória total do navegador, capturas simultâneas, leituras temporárias completas, HTML analisado ou corpos de solicitação.

#### Migração para a v5 {#migrating-in-v5}

Na v5, `capture_xhr` e `response.captured_xhr` foram removidos. Use uma sessão de navegador explícita com `record_requests=True` e leia `session.network.search(url_pattern=..., limit=None)`. Isso também substitui a captura de API pelos fetchers de chamada única, então guarde o objeto da sessão. Os filtros se aplicam ao histórico salvo de toda a sessão, não à captura ou a uma única obtenção de página. Só são salvos os tipos de texto aceitos nos corpos de resposta. `search()` retorna até 100 correspondências por padrão. `limit=None` retorna todas as correspondências mantidas, sem mudar os limites do histórico.

### Cabeçalhos e configuração regional do navegador {#browser-headers-and-locale}

```python
page = StealthyFetcher.fetch(
    'https://example.com',
    google_search=True,
    useragent='Mozilla/5.0...',
    locale='en-US',
)
```

### Exemplo geral {#general-example}
```python
from scrapling.fetchers import StealthyFetcher

def scrape_dynamic_content():

    page = StealthyFetcher.fetch(
        'https://example.com/dynamic',
        network_idle=True,
        wait_selector='.content'
    )


    content = page.css('.content')

    return {
        'title': content.css('h1::text').get(),
        'items': [
            item.text for item in content.css('.item')
        ]
    }
```

### Rotação de proxies {#proxy-rotation}

```python
from scrapling.fetchers import StealthySession, ProxyRotator


rotator = ProxyRotator([
    "http://proxy1:8080",
    "http://proxy2:8080",
    "http://proxy3:8080",
])


with StealthySession(proxy_rotator=rotator, headless=True) as session:
    page1 = session.fetch('https://example1.com')
    page2 = session.fetch('https://example2.com')


    page3 = session.fetch('https://example3.com', proxy='http://specific-proxy:8080')
```

!!! warning "Aviso"

    Por padrão, os fetchers de navegador e suas sessões usam um contexto persistente com um conjunto de abas. Como os navegadores não permitem definir um proxy por aba, ao usar `ProxyRotator`, o fetcher abre um contexto separado para cada proxy, com uma aba por contexto. Quando a tarefa da aba termina, tanto ela quanto o contexto são fechados.

## Quando usar {#when-to-use}

Use StealthyFetcher quando:

- Precisar superar proteções contra bots.
- Precisar de uma impressão digital de navegador confiável.
- Precisar de suporte completo a JavaScript.
- Quiser recursos automáticos para evitar detecção.
- Precisar automatizar um navegador.
- Trabalhar com sites protegidos pelo Cloudflare.
