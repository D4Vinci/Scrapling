---
title: "Migrar para a v0.5"
description: "Passe do Scrapling v0.4.15 para a v0.5. Atualize as importações do navegador, a captura de rede, as ferramentas MCP, os comandos CLI, as configurações do parser e o comportamento dos spiders."
---

# Migrar para a v0.5 {#migrating-to-v05}

Este guia cobre as mudanças que você precisa verificar ao passar da **v0.4.15 para a v0.5**. Inclui APIs removidas, ferramentas renomeadas e correções que podem alterar os resultados do rastreamento ou os arquivos salvos.

## Lista rápida de migração {#quick-migration-checklist}

| Se você usa... | O que mudar |
| --- | --- |
| `DynamicFetcher`, `DynamicSession` ou `AsyncDynamicSession` | Use a classe de navegação furtiva correspondente. |
| `capture_xhr` ou `response.captured_xhr` | Use uma sessão de navegador com `record_requests=True` e `session.network`. |
| `keep_cdata` | Remova das configurações do parser e do fetcher. |
| `scrapling extract stealthy-fetch` ou `stealthy_fetch()` do shell | Use `fetch` no lugar. |
| Ferramentas MCP | Atualize os nomes das ferramentas, as chamadas de captura de tela e o tratamento da resposta de criação de sessão. |
| `response.follow()` após um POST ou uma solicitação com parâmetros de consulta | Passe o método, a consulta e o corpo novamente quando precisar deles. |
| Checkpoints de rastreamento ou caches de respostas salvos | Inicie um novo rastreamento se suas solicitações usarem os dados de entrada da impressão digital que mudaram. |
| `robots_txt_obey=True` | Trate as falhas ao obter robots.txt, que agora bloqueiam o rastreamento daquele domínio. |

## Obtenção com navegador {#browser-fetching}

### Substitua as classes de navegador dinâmico {#replace-the-dynamic-browser-classes}

O mecanismo de navegador que usava Playwright diretamente foi removido. Toda obtenção com navegador agora usa o mecanismo furtivo baseado em Patchright.

| API removida | Substituição |
| --- | --- |
| `scrapling.DynamicFetcher` | `scrapling.StealthyFetcher` |
| `scrapling.fetchers.DynamicFetcher` | `scrapling.fetchers.StealthyFetcher` |
| `scrapling.fetchers.chrome.PlayWrightFetcher` | `scrapling.fetchers.StealthyFetcher` |
| `scrapling.fetchers.DynamicSession` | `scrapling.fetchers.StealthySession` |
| `scrapling.fetchers.AsyncDynamicSession` | `scrapling.fetchers.AsyncStealthySession` |

O módulo `scrapling.fetchers.chrome` e o módulo privado `_browsers._controllers` foram removidos. Use as importações públicas acima.

**Antes:**

```python
from scrapling.fetchers import DynamicFetcher

page = DynamicFetcher.fetch("https://example.com", headless=True)
```

**Agora:**

```python
from scrapling.fetchers import StealthyFetcher

page = StealthyFetcher.fetch("https://example.com", headless=True)
```

Para sessões, substitua `DynamicSession` por `StealthySession`, ou `AsyncDynamicSession` por `AsyncStealthySession`. Faça a mesma mudança no método `configure_sessions()` do seu spider. Os padrões de uso de `fetch()` e `async with` continuam válidos.

Se seus callbacks importam tipos do navegador ou capturam erros do navegador, troque `playwright.sync_api` por `patchright.sync_api`, ou `playwright.async_api` por `patchright.async_api`. Isso inclui `Page`, `Locator`, `Error` e `TimeoutError`.

O Patchright avalia JavaScript em um contexto isolado por padrão. Se um callback lê as variáveis JavaScript da própria página, use `page.evaluate(..., isolated_context=False)`.

Isso muda o comportamento do navegador além do nome de importação. Revise as opções do navegador e as configurações de impressão digital. Resolver o Cloudflare ainda exige `solve_cloudflare=True`; isso não vem ativado por padrão. Além disso, `extra_flags` agora complementa as opções furtivas integradas, em vez de substituí-las.

Veja [Obtenção com navegador](fetching/stealthy.md) para conhecer as opções atuais.

### Substitua a captura XHR pelo histórico de rede da sessão {#replace-xhr-capture-with-session-network-history}

O parâmetro `capture_xhr` e o atributo `Response.captured_xhr` foram removidos. Remova o parâmetro mesmo quando seu valor for `None`. Uma obtenção avulsa não tem mais uma lista XHR anexada à resposta.

Integrações personalizadas que chamam `ResponseFactory.from_playwright_response()` ou `ResponseFactory.from_async_playwright_response()` também precisam remover `xhr_captured`. Passe `collect_history` pelo nome para evitar problemas com a mudança na ordem dos argumentos posicionais.

**Antes:**

```python
from scrapling.fetchers import StealthyFetcher

page = StealthyFetcher.fetch("https://example.com", capture_xhr="/api/")
for response in page.captured_xhr:
    print(response.url, response.body)
```

**Agora:**

```python
from scrapling.fetchers import StealthySession

with StealthySession(record_requests=True) as session:
    page = session.fetch("https://example.com", network_idle=True)
    for response in session.network.search(url_pattern=r"/api/", limit=None):
        print(response.url, response.body)
```

Use `AsyncStealthySession` e `await session.fetch(...)` para código assíncrono. Ler `session.network` não exige `await`.

Há algumas diferenças importantes:

- Defina `record_requests=True` ao criar a sessão. É uma configuração da sessão, não de cada obtenção.
- O histórico pertence à **sessão inteira**, incluindo abas, carregamentos de páginas e ações. Use `after_id`, filtros ou `session.network.clear()` se precisar de um escopo menor.
- Mova a expressão regular antiga de `capture_xhr` para `url_pattern` ao pesquisar no histórico.
- `search()` retorna objetos `Response` salvos. Leia `.url`, `.status`, `.headers`, `.body` ou `.json()` diretamente. O ID do registro, o tipo de recurso e o corpo enviado estão em `response.meta["network_id"]`, `response.meta["resource_type"]` e `response.meta["request_body"]`.
- O histórico em Python inclui todos os tipos de recursos por padrão. Use `resource_type="xhr"` ou `resource_type="fetch"` para escolher um, ou `include_static=False` para solicitações XHR/fetch junto com erros HTTP.
- `search()` retorna no máximo 100 resultados por padrão. Passe `limit=None` para obter todos os resultados mantidos. As sessões mantêm até 1.000 solicitações por padrão; altere isso com `max_recorded_requests`.
- Só as solicitações concluídas são salvas. A captura do corpo é limitada aos tipos de conteúdo de texto aceitos, a 1 MiB por resposta e a 20 MiB de dados de corpo mantidos no total. Registros mais antigos podem ser removidos quando os limites forem atingidos. Veja `response.meta.get("body_note")` para saber por que um corpo foi ignorado.
- A leitura do histórico e o fechamento da sessão não aguardam as capturas pendentes. Espere os dados necessários antes de lê-los. O histórico em Python salvo continua disponível após fechar a sessão.

Veja [Histórico de rede](fetching/stealthy.md#network-history) para conhecer os filtros e limites.

## Configurações do parser {#parser-settings}

### Remova `keep_cdata` {#remove-keep_cdata}

`keep_cdata` foi removido de `Selector`, da configuração dos fetchers e das configurações retornadas por `display_config()`. Remova das chamadas diretas ao parser, de `Fetcher.configure(...)` e dos dicionários `selector_config` passados a fetchers ou integrações.

**Antes:**

```python
from scrapling import Selector

page = Selector("<p>Hello</p>", keep_cdata=True)
```

**Agora:**

```python
from scrapling import Selector

page = Selector("<p>Hello</p>")
```

Não há uma configuração substituta. Ela não afetava a saída do parser HTML. Se você passava as opções do parser por posição, remova o antigo argumento `keep_cdata` e use nomes para `adaptive` e as opções de armazenamento.

## Linha de comando e shell interativo {#command-line-and-interactive-shell}

### Use `fetch` para solicitações do navegador {#use-fetch-for-browser-requests}

A CLI agora tem um único comando de navegador: `scrapling extract fetch`. Ele usa `StealthyFetcher`.

**Antes:**

```bash
scrapling extract stealthy-fetch "https://example.com" page.md
```

**Agora:**

```bash
scrapling extract fetch "https://example.com" page.md
```

Se você já usa `scrapling extract fetch`, o nome do comando continua igual, mas seu mecanismo muda de `DynamicFetcher` para `StealthyFetcher`. Opções como `--solve-cloudflare` agora pertencem a `fetch`.

Em `scrapling shell`, substitua `stealthy_fetch(...)` por `fetch(...)`. O atalho existente `fetch(...)` agora chama `StealthyFetcher.fetch`. As classes dinâmicas não são mais adicionadas ao espaço de nomes do shell.

### Leia arquivos Markdown e de texto como UTF-8 {#read-markdown-and-text-files-as-utf-8}

Os comandos de extração e `Convertor.write_content_to_file()` agora gravam arquivos `.md` e `.txt` em **UTF-8**, independentemente do conjunto de caracteres da página de origem. Atualize qualquer código que leia esses arquivos com a codificação original da página. A saída `.html` ainda usa `page.encoding`.

O Markdown de vários elementos selecionados agora tem linhas em branco entre os elementos. Isso se aplica a `Response.markdown()` e à saída em arquivos Markdown. Atualize as comparações exatas da saída ou os hashes salvos que dependiam do texto concatenado.

## Servidor MCP {#mcp-server}

Atualize os prompts salvos, as listas de ferramentas permitidas, os wrappers e as definições de ferramentas do cliente MCP. Reinicie ou reconecte seu cliente MCP após atualizar o servidor para que ele leia as ferramentas atuais.

### Atualize os nomes de ferramentas e as chamadas em lote {#update-tool-names-and-bulk-calls}

| Ferramenta da v0.4.15 | Substituição na v0.5 |
| --- | --- |
| `fetch`, `stealthy_fetch` | `browser_fetch_once` |
| `open_session` | `browser_open` |
| `session_fetch` | `browser_fetch` |
| `screenshot` | `browser_screenshot` |
| `bulk_fetch`, `bulk_stealthy_fetch` | Uma chamada de `browser_fetch_once` por URL, ou chamadas repetidas de `browser_fetch` por uma sessão aberta |
| `bulk_get` | Uma chamada de `make_request` ou `session_make_request` por URL |

Todas as ferramentas em lote foram removidas. As ferramentas que obtêm uma única URL retornam um `ResponseModel` com `status`, `content` e `url`, não uma lista de respostas. O próprio `content` ainda é uma lista de strings.

Todas as ferramentas de navegador MCP agora usam o mecanismo furtivo. Remova `session_type` das chamadas de `browser_open`; não existe mais a opção de navegador dinâmico. O resultado contém `session_type="stealthy"`. As sessões HTTP ainda usam `open_request_session` e retornam `session_type="static"`.

As integrações Python também devem parar de importar `BrowserSessionType`, que foi removido. `SessionType` agora aceita apenas `"stealthy"` e `"static"`.

As chamadas por uma mesma sessão de navegador devem ser executadas em ordem porque compartilham uma página. Feche as sessões com `close_session` ao terminar.

### Leia as configurações por `list_sessions` {#read-settings-through-list_sessions}

`browser_open` e `open_request_session` agora retornam apenas:

```json
{
  "session_id": "my-session",
  "session_type": "stealthy"
}
```

O resultado da criação não inclui mais `created_at`, `is_alive`, `settings` ou `message`. Chame `list_sessions` para obter os três primeiros campos. A confirmação `message` foi removida. O código que assumia que `SessionCreatedModel` tinha todos os campos de `SessionInfo` também precisa mudar.

### Obtenha a página antes de fazer uma captura de tela {#fetch-before-taking-a-screenshot}

`browser_screenshot` captura a **página atual sem recarregá-la**. Não aceita mais uma URL nem as opções antigas de navegação e espera: `wait`, `wait_selector`, `wait_selector_state` e `network_idle`.

Use esta ordem:

1. Chame `browser_open`.
2. Chame `browser_fetch` com a URL e as opções de carregamento da página que precisar.
3. Se necessário, chame `browser_actions` para interagir com a página ou esperar o conteúdo.
4. Chame `browser_screenshot` com o ID da sessão.
5. Chame `close_session` ao terminar.

Por exemplo, os argumentos para uma captura da página inteira são:

```json
{
  "session_id": "my-session",
  "full_page": true
}
```

O `timeout` dessa ferramenta agora limita a operação de captura de tela. A ferramenta não carrega uma página. Para capturar um elemento, use `selector` ou `ref` e não defina `full_page=true`.

As capturas de tela ainda retornam blocos de conteúdo de imagem e texto, com a URL da página atual no bloco de texto. Não retornam um `ResponseModel` de obtenção.

Veja o [guia MCP](ai/mcp-server.md) e a [referência da API](api-reference/mcp-server.md) para conhecer os esquemas completos.

## Spiders e solicitações HTTP {#spiders-and-http-requests}

### Passe os dados da solicitação novamente ao seguir um link {#pass-request-data-again-when-following-a-link}

`response.follow()` não copia mais `method`, `params`, `data`, `json`, `files` ou `multipart` da solicitação anterior. Também remove os cabeçalhos `Content-Length` herdados de `headers` e `extra_headers`.

Um link seguido agora começa como uma solicitação GET simples, a menos que você passe os dados da solicitação explicitamente. Outras configurações compartilhadas, como a sessão, o proxy e os callbacks, ainda seguem as regras de herança existentes.

Se seu código antigo dependia de dados POST herdados, troque:

```python
yield response.follow("/next")
```

por:

```python
yield response.follow("/next", method="POST", json={"page": 2})
```

Passe `params` explicitamente também quando a próxima solicitação precisar deles. Deixe o cliente HTTP calcular o novo `Content-Length`.

### Verifique as impressões digitais das solicitações e o estado de rastreamento salvo {#check-request-fingerprints-and-saved-crawl-state}

A impressão digital de uma solicitação é a chave usada para detectar solicitações duplicadas e encontrar respostas em cache. Seus dados de entrada agora tratam três casos de forma diferente:

- Os `params` são combinados com a URL antes de criar a chave. Solicitações para a mesma URL com parâmetros de consulta diferentes não são mais tratadas como duplicadas por padrão.
- Corpos JSON como `{}`, `[]`, `false`, `0` e `""` são mantidos na chave. Eles não compartilham mais a chave de um corpo ausente. `None` ainda significa que não há corpo JSON.
- Com `fp_include_headers=True`, mudar apenas a ordem de inserção dos cabeçalhos não altera mais a chave.

Se seu rastreamento usa esses dados de entrada, termine antes de atualizar ou inicie um novo rastreamento com um novo checkpoint e um novo diretório de cache de respostas. As chaves antigas salvas podem ser diferentes das novas. Essa é uma mudança na identidade da solicitação, não um novo formato de arquivo de checkpoint.

O modo de desenvolvimento agora só grava respostas no cache após verificar se estão bloqueadas. Páginas bloqueadas não são salvas como resultados bem-sucedidos em cache. Os arquivos de cache existentes não são limpos automaticamente; remova entradas antigas se você já armazenou uma página de verificação.

Os rastreamentos que falham agora mantêm seus arquivos de checkpoint. Verifique seu código de limpeza se ele assumia que esses arquivos desapareciam após um erro. Veja [Pausar e retomar](spiders/advanced.md#pause-resume) e [Modo de desenvolvimento](spiders/advanced.md#development-mode).

### Verifique as falhas de robots.txt {#check-robotstxt-failures}

Com `robots_txt_obey=True`, uma exceção ao obter robots.txt ou uma resposta diferente de HTTP 200 ou 4xx agora bloqueia solicitações para aquele domínio. Antes, essas falhas permitiam o rastreamento. HTTP 200 ainda fornece as regras, e HTTP 4xx ainda permite o acesso.

O resultado fica em cache durante todo o rastreamento. Corrija o problema de acesso a robots.txt e inicie um novo rastreamento; as solicitações seguintes do mesmo rastreamento não repetirão a consulta que falhou. Isso não altera o padrão `robots_txt_obey=False`.

### Verifique as restrições de links e os callbacks de sitemaps {#check-link-restrictions-and-sitemap-callbacks}

- Uma restrição de `LinkExtractor` que não encontra nada agora não retorna links. Ela não usa mais a página inteira como alternativa. Corrija a expressão `restrict_css` ou `restrict_xpath` se seu rastreamento agora encontrar menos links.
- Uma restrição agora pode selecionar o próprio elemento do link, não apenas um elemento pai. Isso pode adicionar links que antes eram ignorados. Revise os conjuntos de URLs esperados.
- `SitemapSpider` agora envia URLs de páginas para `parse()` quando não há regras ou quando uma regra correspondente tem `callback=None`. Ele não envia mais essas páginas HTML de volta ao parser do sitemap. Implemente `parse()` para esses casos e remova as soluções alternativas para o roteamento antigo.
- A marca de ordem de bytes Unicode no início de robots.txt e de feeds CSV é removida. A primeira diretiva de robots agora tem efeito, e o primeiro cabeçalho CSV não começa mais com `\ufeff`. Se você definir `headers` personalizados, a marca será removida do valor do primeiro campo. Atualize o código que compensava esse prefixo oculto. Comentários XML e instruções de processamento de sitemaps também são ignorados, em vez de causar uma falha de análise.

### Verifique dados de formulários, cabeçalhos e JSON da CLI {#check-form-data-headers-and-cli-json}

Dados de formulários em dicionários agora expandem valores de listas e tuplas em chaves repetidas. Por exemplo, `data={"tag": ["a", "b"]}` envia `tag=a&tag=b`. Uma lista vazia não envia nenhuma entrada para essa chave. O cabeçalho padrão `Content-Type: application/x-www-form-urlencoded` é adicionado quando você não fornece um.

Se precisar de outro formato de envio, passe uma string ou bytes codificados explicitamente. `json`, `content` bruto e uploads multipart mantêm seu próprio tratamento do corpo. Valores `None` **não são removidos** dos dados de formulários ou parâmetros de consulta; eles continuam como a string `None`.

Os cabeçalhos HTTP de cada solicitação agora substituem os cabeçalhos da sessão sem diferenciar maiúsculas de minúsculas. Um cabeçalho de solicitação chamado `authorization` substitui o `Authorization` da sessão em vez de enviar ambos. Remova o código que compensava nomes de cabeçalhos duplicados.

Os valores JSON da CLI `{}`, `[]`, `false`, `0` e `""` agora são enviados em vez de descartados sem aviso. Além disso, `curl2fetcher()` agora aplica o agente de usuário de `-A` do curl e passa corretamente os proxies de `-x` como uma string de URL. Um cabeçalho explícito `-H 'User-Agent: ...'` do curl ainda tem prioridade sobre `-A`.

## Outras mudanças na saída a verificar {#other-output-changes-to-check}

Estas correções não removem APIs, mas podem alterar resultados salvos e testes de saída exata:

- Os seletores CSS e XPath gerados agora incluem `:nth-of-type(1)` ou `[1]` quando necessário para identificar o primeiro de vários elementos irmãos com a mesma tag. Atualize as strings de seletores esperadas; não remova a nova marca de posição.
- O conteúdo limpo para IA agora mantém elementos visíveis com valores como `opacity:0.95`, remove elementos ocultos por mais variações de estilos inline e elementos `<slot hidden>`, e remove todas as tags de ruído correspondentes mesmo quando estão aninhadas. Verifique novamente a saída exata de Markdown, texto e HTML sanitizado.
- A conversão de respostas do navegador agora lê declarações de charset com diferenças entre maiúsculas e minúsculas, espaços ou valores entre aspas, como `text/plain; CHARSET = "iso-8859-15"`. Respostas que não são HTML e têm esses cabeçalhos agora usam a codificação declarada em vez de recorrer ao UTF-8. Verifique novamente o texto decodificado dessas respostas.

## Verifique a atualização {#verify-your-upgrade}

Execute um rastreamento pequeno antes do trabalho completo. Verifique os dados extraídos, as URLs seguidas, os corpos das solicitações enviadas, a codificação dos arquivos salvos e qualquer comportamento de cache ou checkpoint de que você dependa. Para integrações MCP, verifique os dados de entrada das ferramentas e os dados retornados de acordo com os esquemas atuais.

Para mudanças de versões anteriores, veja o [histórico de alterações](changelog.md).
