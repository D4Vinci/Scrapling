---
title: "Web scraping por HTTP em Python com Fetcher e FetcherSession"
description: "Envie solicitações HTTP síncronas ou assíncronas com imitação de navegador, cookies, proxies e sessões reutilizáveis. Extraia dados das respostas com Scrapling."
---

# Solicitações HTTP {#http-requests}

`Fetcher` envia solicitações HTTP rápidas e leves por meio de `curl_cffi`, uma biblioteca de alto desempenho com várias opções para evitar detecção.

!!! success "Antes de começar"

    1. Leia [Conceitos básicos dos fetchers](../fetching/choosing.md) para entender o [objeto Response](../fetching/choosing.md#response-object) e escolher um fetcher.
    2. Leia [Buscar elementos](../parsing/selection.md) para aprender a buscar e extrair elementos de [Selector](../parsing/main_classes.md#selector)/[Response](../fetching/choosing.md#response-object).
    3. Leia [Classes principais](../parsing/main_classes.md) para conhecer as propriedades e os métodos que [Response](../fetching/choosing.md#response-object) herda de [Selector](../parsing/main_classes.md#selector).

## Uso básico {#basic-usage}
A forma principal de importar este fetcher é a mesma dos demais:

```python
from scrapling.fetchers import Fetcher
```
Veja como configurar o analisador [aqui](choosing.md#parser-configuration-in-all-fetchers).

### Argumentos compartilhados {#shared-arguments}
Todos os métodos de solicitação compartilham estes argumentos:

- **url**: URL de destino.
- **stealthy_headers**: gera e adiciona cabeçalhos de um navegador real, incluindo um referer do Google. Fica ativado por padrão.
- **follow_redirects**: controla os redirecionamentos. **O padrão é `"safe"`**: segue os redirecionamentos, mas rejeita os que apontam para IPs internos ou privados, protegendo contra SSRF. Use `True` para segui-los sem restrições ou `False` para desativá-los.
- **timeout**: tempo máximo, em segundos, para cada solicitação terminar. **O padrão é 30 segundos**.
- **retries**: número máximo de tentativas quando uma solicitação falha, incluindo a primeira. **O padrão é 3**.
- **retry_delay**: segundos de espera entre tentativas. **O padrão é 1 segundo**.
- **impersonate**: imita a impressão digital TLS de um navegador. Aceita uma string ou uma lista, como `"chrome110"`, `"firefox102"` ou `"safari15_5"`, para versões específicas. Use `"chrome"`, `"firefox"`, `"safari"` ou `"edge"` para escolher a versão mais recente disponível. Assim, as solicitações parecem vir de um navegador real no nível TLS. Se passar uma lista, uma opção será escolhida ao acaso em cada solicitação. **O padrão é a versão mais recente disponível do Chrome.**
- **http3**: usa HTTP/3. **O padrão é False**. Pode causar problemas quando combinado com `impersonate`.
- **cookies**: cookies da solicitação. Aceita um dicionário de `name→value` ou uma lista de dicionários.
- **proxy**: proxy usado para direcionar todo o tráfego HTTP e HTTPS desta solicitação. O formato é `http://username:password@localhost:8030`.
- **proxy_auth**: autenticação HTTP básica do proxy, como uma tupla de (usuário, senha).
- **proxies**: dicionário de proxies no formato `{"http": proxy_url, "https": proxy_url}`.
- **proxy_rotator**: objeto `ProxyRotator` para trocar de proxy automaticamente. Não pode ser combinado com `proxy` ou `proxies`.
- **headers**: cabeçalhos da solicitação. Podem substituir os gerados por `stealthy_headers`.
- **max_redirects**: número máximo de redirecionamentos. **O padrão é 30**. Use -1 para não limitar.
- **verify**: define se os certificados HTTPS serão verificados. **O padrão é True**.
- **cert**: tupla com os nomes dos arquivos (certificado, chave) do certificado do cliente.
- **selector_config**: dicionário de ajustes do analisador ao criar o objeto `Selector`/`Response` final.

!!! note "Notas"

    1. Os navegadores disponíveis para imitação são (`"edge"`, `"chrome"`, `"chrome_android"`, `"safari"`, `"safari_beta"`, `"safari_ios"`, `"safari_ios_beta"`, `"firefox"`, `"tor"`).<br/>
    2. Os navegadores e suas versões aparecem no preenchimento automático do argumento e são renovados a cada atualização de `curl_cffi`.<br/>
    3. Se você ativar `impersonate` ou `stealthy_headers`, os fetchers geram cabeçalhos reais que correspondem à versão do navegador usada.

Para ajustar outras opções, você pode passar a qualquer método os argumentos aceitos por `curl_cffi` que o método ainda não trate.

### Codificação do texto {#text-encoding}

Se uma página que não usa UTF-8 mostrar caracteres incorretos, passe `default_encoding="shift_jis"`, ou a codificação real da página, na solicitação. Ela será usada quando o cabeçalho `Content-Type` não informar uma codificação. Isso não substitui a codificação enviada pelo servidor.

Se o servidor informar uma codificação incorreta, você pode forçar a correta com `selector_config={"encoding": "shift_jis"}`.

### Métodos HTTP {#http-methods}
Cada método aceita argumentos próprios, como `params` para GET e `data`/`json` para POST, PUT e DELETE.

Veja alguns exemplos:

> Os métodos `OPTIONS` e `HEAD` não estão disponíveis.
#### GET {#get}
```python
from scrapling.fetchers import Fetcher
# Basic GET
page = Fetcher.get('https://example.com')
page = Fetcher.get('https://scrapling.requestcatcher.com/get', stealthy_headers=True)
page = Fetcher.get('https://scrapling.requestcatcher.com/get', proxy='http://username:password@localhost:8030')
# With parameters
page = Fetcher.get('https://example.com/search', params={'q': 'query'})

# With headers
page = Fetcher.get('https://example.com', headers={'User-Agent': 'Custom/1.0'})
# Basic HTTP authentication
page = Fetcher.get("https://example.com", auth=("my_user", "password123"))
# Browser impersonation
page = Fetcher.get('https://example.com', impersonate='chrome')
# HTTP/3 support
page = Fetcher.get('https://example.com', http3=True)
```
Para solicitações assíncronas, basta um pequeno ajuste:
```python
from scrapling.fetchers import AsyncFetcher
# Basic GET
page = await AsyncFetcher.get('https://example.com')
page = await AsyncFetcher.get('https://scrapling.requestcatcher.com/get', stealthy_headers=True)
page = await AsyncFetcher.get('https://scrapling.requestcatcher.com/get', proxy='http://username:password@localhost:8030')
# With parameters
page = await AsyncFetcher.get('https://example.com/search', params={'q': 'query'})
# With headers
page = await AsyncFetcher.get('https://example.com', headers={'User-Agent': 'Custom/1.0'})
# Basic HTTP authentication
page = await AsyncFetcher.get("https://example.com", auth=("my_user", "password123"))
# Browser impersonation
page = await AsyncFetcher.get('https://example.com', impersonate='chrome110')
# HTTP/3 support
page = await AsyncFetcher.get('https://example.com', http3=True)
```
Em todos os casos, `page` é um [Response](choosing.md#response-object), que também é um [Selector](../parsing/main_classes.md#selector). Você pode usá-lo diretamente:
```python
page.css('.something.something')

page = Fetcher.get('https://api.github.com/events')
>>> page.json()
[{'id': '<redacted>',
  'type': 'PushEvent',
  'actor': {'id': '<redacted>',
   'login': '<redacted>',
   'display_login': '<redacted>',
   'gravatar_id': '',
   'url': 'https://api.github.com/users/<redacted>',
   'avatar_url': 'https://avatars.githubusercontent.com/u/<redacted>'},
  'repo': {'id': '<redacted>',
...
```
#### POST {#post}
```python
from scrapling.fetchers import Fetcher
# Basic POST
page = Fetcher.post('https://scrapling.requestcatcher.com/post', data={'key': 'value'}, params={'q': 'query'})
page = Fetcher.post('https://scrapling.requestcatcher.com/post', data={'key': 'value'}, stealthy_headers=True)
page = Fetcher.post('https://scrapling.requestcatcher.com/post', data={'key': 'value'}, proxy='http://username:password@localhost:8030', impersonate="chrome")
# Another example of form-encoded data
page = Fetcher.post('https://example.com/submit', data={'username': 'user', 'password': 'pass'}, http3=True)
# JSON data
page = Fetcher.post('https://example.com/api', json={'key': 'value'})
```
Para solicitações assíncronas, basta um pequeno ajuste:
```python
from scrapling.fetchers import AsyncFetcher
# Basic POST
page = await AsyncFetcher.post('https://scrapling.requestcatcher.com/post', data={'key': 'value'})
page = await AsyncFetcher.post('https://scrapling.requestcatcher.com/post', data={'key': 'value'}, stealthy_headers=True)
page = await AsyncFetcher.post('https://scrapling.requestcatcher.com/post', data={'key': 'value'}, proxy='http://username:password@localhost:8030', impersonate="chrome")
# Another example of form-encoded data
page = await AsyncFetcher.post('https://example.com/submit', data={'username': 'user', 'password': 'pass'}, http3=True)
# JSON data
page = await AsyncFetcher.post('https://example.com/api', json={'key': 'value'})
```
#### PUT {#put}
```python
from scrapling.fetchers import Fetcher
# Basic PUT
page = Fetcher.put('https://example.com/update', data={'status': 'updated'})
page = Fetcher.put('https://example.com/update', data={'status': 'updated'}, stealthy_headers=True, impersonate="chrome")
page = Fetcher.put('https://example.com/update', data={'status': 'updated'}, proxy='http://username:password@localhost:8030')
# Another example of form-encoded data
page = Fetcher.put("https://scrapling.requestcatcher.com/put", data={'key': ['value1', 'value2']})
```
Para solicitações assíncronas, basta um pequeno ajuste:
```python
from scrapling.fetchers import AsyncFetcher
# Basic PUT
page = await AsyncFetcher.put('https://example.com/update', data={'status': 'updated'})
page = await AsyncFetcher.put('https://example.com/update', data={'status': 'updated'}, stealthy_headers=True, impersonate="chrome")
page = await AsyncFetcher.put('https://example.com/update', data={'status': 'updated'}, proxy='http://username:password@localhost:8030')
# Another example of form-encoded data
page = await AsyncFetcher.put("https://scrapling.requestcatcher.com/put", data={'key': ['value1', 'value2']})
```

#### DELETE {#delete}
```python
from scrapling.fetchers import Fetcher
page = Fetcher.delete('https://example.com/resource/123')
page = Fetcher.delete('https://example.com/resource/123', stealthy_headers=True, impersonate="chrome")
page = Fetcher.delete('https://example.com/resource/123', proxy='http://username:password@localhost:8030')
```
Para solicitações assíncronas, basta um pequeno ajuste:
```python
from scrapling.fetchers import AsyncFetcher
page = await AsyncFetcher.delete('https://example.com/resource/123')
page = await AsyncFetcher.delete('https://example.com/resource/123', stealthy_headers=True, impersonate="chrome")
page = await AsyncFetcher.delete('https://example.com/resource/123', proxy='http://username:password@localhost:8030')
```

## Gerenciamento de sessões {#session-management}

Use `FetcherSession` para enviar várias solicitações com a mesma configuração. Ela funciona em código síncrono ou assíncrono: detecta o tipo de uso e ajusta a sessão sem precisar importar outra classe.

`FetcherSession` aceita quase todos os argumentos dos métodos de solicitação. Você pode definir os ajustes para toda a sessão e alterá-los em uma solicitação específica, como mostram os exemplos.

```python
from scrapling.fetchers import FetcherSession

# Create a session with default configuration
with FetcherSession(
    impersonate='chrome',
    http3=True,
    stealthy_headers=True,
    timeout=30,
    retries=3
) as session:
    # Make multiple requests with the same settings and the same cookies
    page1 = session.get('https://scrapling.requestcatcher.com/get')
    page2 = session.post('https://scrapling.requestcatcher.com/post', data={'key': 'value'})
    page3 = session.get('https://api.github.com/events')

    # All requests share the same session and connection pool
```

Você também pode usar `ProxyRotator` com `FetcherSession` para trocar de proxy automaticamente entre solicitações:

```python
from scrapling.fetchers import FetcherSession, ProxyRotator

rotator = ProxyRotator([
    'http://proxy1:8080',
    'http://proxy2:8080',
    'http://proxy3:8080',
])

with FetcherSession(proxy_rotator=rotator, impersonate='chrome') as session:
    # Each request automatically uses the next proxy in rotation
    page1 = session.get('https://example.com/page1')
    page2 = session.get('https://example.com/page2')

    # You can check which proxy was used via the response metadata
    print(page1.meta['proxy'])
```

Para uma solicitação específica, substitua o proxy ou rotador da sessão passando `proxy=` ao método:

```python
with FetcherSession(proxy='http://default-proxy:8080') as session:
    # Uses the session proxy
    page1 = session.get('https://example.com/page1')

    # Override the proxy for this specific request
    page2 = session.get('https://example.com/page2', proxy='http://special-proxy:9090')
```

Um exemplo assíncrono:

```python
async with FetcherSession(impersonate='firefox', http3=True) as session:
    # All standard HTTP methods available
    response = await session.get('https://example.com')
    response = await session.post('https://scrapling.requestcatcher.com/post', json={'data': 'value'})
    response = await session.put('https://scrapling.requestcatcher.com/put', data={'update': 'info'})
    response = await session.delete('https://scrapling.requestcatcher.com/delete')
```
Ou, melhor ainda:
```python
import asyncio
from scrapling.fetchers import FetcherSession

# Async session usage
async with FetcherSession(impersonate="safari") as session:
    urls = ['https://example.com/page1', 'https://example.com/page2']

    tasks = [
        session.get(url) for url in urls
    ]

    pages = await asyncio.gather(*tasks)
```

`Fetcher` usa `FetcherSession` para criar uma sessão temporária a cada solicitação.

### Vantagens das sessões {#session-benefits}

- **Mais velocidade**: 10 vezes mais rápido do que criar uma sessão por solicitação.
- **Cookies persistentes**: tratamento automático dos cookies entre solicitações.
- **Menor consumo**: melhor uso de memória e CPU ao enviar várias solicitações.
- **Configuração centralizada**: um só lugar para gerenciar os ajustes.

## Exemplos {#examples}
Exemplos completos para quem está começando com web scraping.

### Solicitação HTTP básica {#basic-http-request}

```python
from scrapling.fetchers import Fetcher

# Make a request
page = Fetcher.get('https://example.com')

# Check the status
if page.status == 200:
    # Extract title
    title = page.css('title::text').get()
    print(f"Page title: {title}")

    # Extract all links
    links = page.css('a::attr(href)').getall()
    print(f"Found {len(links)} links")
```

### Extrair produtos {#product-scraping}

```python
from scrapling.fetchers import Fetcher

def scrape_products():
    page = Fetcher.get('https://example.com/products')
    
    # Find all product elements
    products = page.css('.product')
    
    results = []
    for product in products:
        results.append({
            'title': product.css('.title::text').get(),
            'price': product.css('.price::text').re_first(r'\d+\.\d{2}'),
            'description': product.css('.description::text').get(),
            'in_stock': product.has_class('in-stock')
        })
    
    return results
```

### Baixar arquivos {#downloading-files}

```python
from scrapling.fetchers import Fetcher

page = Fetcher.get('https://raw.githubusercontent.com/D4Vinci/Scrapling/main/docs/assets/main_cover.png')
with open(file='main_cover.png', mode='wb') as f:
   f.write(page.body)
```

### Percorrer páginas de resultados {#pagination-handling}

```python
from scrapling.fetchers import Fetcher

def scrape_all_pages():
    base_url = 'https://example.com/products?page={}'
    page_num = 1
    all_products = []
    
    while True:
        # Get current page
        page = Fetcher.get(base_url.format(page_num))
        
        # Find products
        products = page.css('.product')
        if not products:
            break
            
        # Process products
        for product in products:
            all_products.append({
                'name': product.css('.name::text').get(),
                'price': product.css('.price::text').get()
            })
            
        # Next page
        page_num += 1
        
    return all_products
```

### Enviar formulários {#form-submission}

```python
from scrapling.fetchers import Fetcher

# Submit login form
response = Fetcher.post(
    'https://example.com/login',
    data={
        'username': 'user@example.com',
        'password': 'password123'
    }
)

# Check login success
if response.status == 200:
    # Extract user info
    user_name = response.css('.user-name::text').get()
    print(f"Logged in as: {user_name}")
```

### Extrair tabelas {#table-extraction}

```python
from scrapling.fetchers import Fetcher

def extract_table():
    page = Fetcher.get('https://example.com/data')
    
    # Find table
    table = page.css('table')[0]
    
    # Extract headers
    headers = [
        th.text for th in table.css('thead th')
    ]
    
    # Extract rows
    rows = []
    for row in table.css('tbody tr'):
        cells = [td.text for td in row.css('td')]
        rows.append(dict(zip(headers, cells)))
        
    return rows
```

### Menu de navegação {#navigation-menu}

```python
from scrapling.fetchers import Fetcher

def extract_menu():
    page = Fetcher.get('https://example.com')
    
    # Find navigation
    nav = page.css('nav')[0]
    
    menu = {}
    for item in nav.css('li'):
        links = item.css('a')
        if links:
            link = links[0]
            menu[link.text] = {
                'url': link['href'],
                'has_submenu': bool(item.css('.submenu'))
            }
            
    return menu
```

## Quando usar cada opção {#when-to-use}

Use `Fetcher` quando:

- Precisar de solicitações HTTP rápidas.
- Quiser reduzir o consumo de recursos.
- Não precisar executar JavaScript porque os dados podem ser obtidos com solicitações HTTP.
- Precisar evitar alguma detecção, por exemplo, se o site tiver proteção, mas não usar desafios de JavaScript.

Use `FetcherSession` quando:

- Enviar várias solicitações ao mesmo site ou a sites diferentes.
- Precisar manter cookies ou autenticação entre solicitações.
- Quiser reutilizar conexões para melhorar o desempenho.
- Precisar manter os mesmos ajustes entre solicitações.
- Trabalhar com APIs que exijam estado de sessão.

Use outros fetchers quando:

- Precisar automatizar um navegador.
- Precisar de opções avançadas para evitar a detecção de bots.
- Precisar executar JavaScript ou interagir com conteúdo dinâmico.
