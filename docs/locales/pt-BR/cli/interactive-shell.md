---
title: "Teste a extração de dados no shell interativo do Scrapling"
description: "Obtenha páginas, teste seletores e confira resultados em um shell do IPython. Converta comandos curl, reutilize respostas recentes e teste seu código de extração."
---

# Guia do shell interativo do Scrapling {#scrapling-interactive-shell-guide}

<script src="https://asciinema.org/a/736339.js" id="asciicast-736339" async data-autoplay="1" data-loop="1" data-cols="225" data-rows="40" data-start-at="00:06" data-speed="1.5" data-theme="tango"></script>

**Um ambiente REPL de extração de dados web para desenvolvedores e cientistas de dados**

O shell interativo do Scrapling é um ambiente baseado no IPython, feito para extrair dados web. Ele oferece acesso imediato a todas as funções do Scrapling, atalhos úteis, gerenciamento automático de páginas e ferramentas como a conversão de comandos curl.

!!! success "Antes de começar"

    1. Leia a página de [conceitos básicos dos fetchers](../fetching/choosing.md) para entender o que é o [objeto Response](../fetching/choosing.md#response-object) e qual fetcher usar.
    2. Leia a página de [seleção de elementos](../parsing/selection.md) para aprender a buscar e extrair elementos de um objeto [Selector](../parsing/main_classes.md#selector)/[Response](../fetching/choosing.md#response-object).
    3. Leia a página de [classes principais](../parsing/main_classes.md) para conhecer as propriedades e os métodos que a classe [Response](../fetching/choosing.md#response-object) herda de [Selector](../parsing/main_classes.md#selector).
    4. Leia pelo menos uma página da seção de fetchers para as solicitações que você usará aqui: [solicitações HTTP](../fetching/static.md) ou [obtenção com navegador](../fetching/stealthy.md).

## Por que usar o shell interativo? {#why-use-the-interactive-shell}

Com o shell interativo, você pode explorar e testar na hora, sem precisar editar e executar um script a cada tentativa. Ele é útil para:

- **Criar protótipos rápidos**: Teste estratégias de extração na hora.
- **Explorar dados**: Navegue por sites e extraia dados de forma interativa.
- **Aprender Scrapling**: Experimente as funções em tempo real.
- **Depurar scrapers**: Confira as solicitações e seus resultados passo a passo.
- **Converter processos**: Transforme um comando curl das DevTools do navegador em uma solicitação de Fetcher com uma linha.

## Primeiros passos {#getting-started}

### Iniciar o shell {#launch-the-shell}

```bash
# Start the interactive shell
scrapling shell

# Execute code and exit (useful for scripting)
scrapling shell -c "get('https://quotes.toscrape.com'); print(len(page.css('.quote')))"

# Set logging level
scrapling shell --loglevel info
```

Ao abrir o shell, você verá o banner do Scrapling e poderá começar a extrair dados, como no vídeo acima:

```python
# No imports needed - everything is ready!
get('https://news.ycombinator.com')

# Explore the page structure
page.css('a')[:5]  # Look at first 5 links

# Refine your selectors
stories = page.css('.titleline>a')
len(stories)  # 30

# Extract specific data
for story in stories[:3]:
    title = story.text
    url = story['href']
    print(f"{title}: {url}")

# Try different approaches
titles = page.css('.titleline>a::text')  # Direct text extraction
urls = page.css('.titleline>a::attr(href)')  # Direct attribute extraction
```

## Atalhos integrados {#built-in-shortcuts}

O shell oferece atalhos para evitar código repetido:

- **`get(url, **kwargs)`** - Solicitação HTTP GET (em vez de `Fetcher.get`).
- **`post(url, **kwargs)`** - Solicitação HTTP POST (em vez de `Fetcher.post`).
- **`put(url, **kwargs)`** - Solicitação HTTP PUT (em vez de `Fetcher.put`).
- **`delete(url, **kwargs)`** - Solicitação HTTP DELETE (em vez de `Fetcher.delete`).
- **`fetch(url, **kwargs)`** - Obtenção com o navegador Stealthy (em vez de `StealthyFetcher.fetch`).

As classes mais usadas já estão disponíveis sem importação, incluindo `Fetcher`, `AsyncFetcher`, `StealthyFetcher` e `Selector`.

### Gerenciamento automático de páginas {#smart-page-management}

O shell acompanha suas solicitações e páginas:

- **Acesso à página atual**

    `page` e `response` são atualizados automaticamente com a última página obtida:

    ```python
    get('https://quotes.toscrape.com')
    # 'page' and 'response' both refer to the last fetched page
    page.url  # 'https://quotes.toscrape.com'
    response.status  # Prints 200; Same as page.status
    ```

- **Histórico de páginas**

    `pages` mantém as últimas cinco páginas em um objeto `Selectors`:

    ```python
    get('https://site1.com')
    get('https://site2.com')
    get('https://site3.com')
    
    # Access last 5 pages
    len(pages)  # `Selectors` object with `page` history -> 3
    pages[0].url  # First page in history -> 'https://site1.com'
    pages[-1].url  # Most recent page -> 'https://site3.com'
    
    # Work with historical pages
    for i, old_page in enumerate(pages):
        print(f"Page {i}: {old_page.url} - {old_page.status}")
    ```

## Outros comandos úteis {#additional-helpful-commands}

### Ver a página {#page-visualization}

Abra as páginas obtidas no seu navegador:

```python
get('https://quotes.toscrape.com')
view(page)  # Opens the page HTML in your default browser
```

### Integração com comandos curl {#curl-command-integration}

O shell inclui as funções `uncurl` e `curl2fetcher` para converter comandos curl das DevTools do navegador em solicitações de `Fetcher`.

Primeiro, copie uma solicitação como comando curl:

<img src="../assets/scrapling_shell_curl.png" title="Copiar uma solicitação do Chrome como comando curl" alt="Copiar uma solicitação do Chrome como comando curl" style="width: 70%;"/>

- **Converter um comando curl em um objeto de solicitação**

    ```python
    curl_cmd = '''curl 'https://scrapling.requestcatcher.com/post' \
      -X POST \
      -H 'Content-Type: application/json' \
      -d '{"name": "test", "value": 123}' '''
    
    request = uncurl(curl_cmd)
    request.method  # -> 'post'
    request.url  # -> 'https://scrapling.requestcatcher.com/post'
    request.headers  # -> {'Content-Type': 'application/json'}
    ```

- **Executar um comando curl diretamente**

    ```python
    # Convert and execute in one step
    curl2fetcher(curl_cmd)
    page.status  # -> 200
    ```

### Funções do IPython {#ipython-features}

O shell herda todas as funções do IPython:

```python
# Magic commands
%time page = get('https://example.com')  # Time execution
%history  # Show command history
%save filename.py 1-10  # Save commands 1-10 to file

# Tab completion works everywhere
page.c<TAB>  # Shows: css, cookies, headers, etc.
Fetcher.<TAB>  # Shows all Fetcher methods

# Object inspection
get? # Show get documentation
```

## Exemplos {#examples}

Estes são alguns exemplos gerados com IA:

#### Coletar dados de lojas online {#e-commerce-data-collection}

```python
# Start with product listing page
catalog = get('https://shop.example.com/products')

# Find product links
product_links = catalog.css('.product-link::attr(href)').getall()
print(f"Found {len(product_links)} products")

# Sample a few products first
for link in product_links[:3]:
    product = get(catalog.urljoin(link))
    name = product.css('.product-name::text').get('')
    price = product.css('.price::text').get('')
    print(f"{name}: {price}")

# Scale up with sessions for efficiency
from scrapling.fetchers import FetcherSession
with FetcherSession() as session:
    products = []
    for link in product_links:
        product = session.get(catalog.urljoin(link))
        products.append({
            'name': product.css('.product-name::text').get(''),
            'price': product.css('.price::text').get(''),
            'url': link
        })
```

#### Integrar e testar APIs {#api-integration-and-testing}

```python
>>> # Test API endpoints interactively
>>> response = get('https://jsonplaceholder.typicode.com/posts/1')
>>> response.json()
{'userId': 1, 'id': 1, 'title': 'sunt aut...', 'body': 'quia et...'}

>>> # Test POST requests
>>> new_post = post('https://jsonplaceholder.typicode.com/posts', 
...                 json={'title': 'Test Post', 'body': 'Test content', 'userId': 1})
>>> new_post.json()['id']
101

>>> # Test with different data
>>> updated = put('https://jsonplaceholder.typicode.com/posts/1',
...               json={'title': 'Updated Title'})
```

## Obter ajuda {#getting-help}

Se você precisar de mais ajuda do que a disponível no terminal, consulte:

- [Documentação do Scrapling](https://scrapling.readthedocs.io/pt-br/latest/)
- [Comunidade no Discord](https://discord.gg/EMgGbDceNQ)
- [Issues no GitHub](https://github.com/D4Vinci/Scrapling/issues)

É isso! Boa extração. O shell torna a extração de dados web tão fácil quanto uma conversa.
