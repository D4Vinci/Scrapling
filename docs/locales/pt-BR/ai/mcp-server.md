---
title: "Servidor MCP do Scrapling: configuração e extração de dados"
description: "Conecte um cliente de IA ao Scrapling para extrair dados por HTTP ou com um navegador. Use sessões, estado de login salvo, ações, filtros e histórico de APIs."
---

# Guia do servidor MCP do Scrapling {#scrapling-mcp-server-guide}

<iframe width="560" height="315" src="https://www.youtube.com/embed/NHwWEiTOoPQ" title="Reprodutor de vídeo do YouTube" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>

O **servidor MCP do Scrapling** leva as funções de extração de dados web do Scrapling ao seu chatbot ou agente de IA. Você pode pedir que ele visite sites, extraia dados e contorne proteções contra bots por meio de uma conversa no Claude ou em qualquer interface compatível com MCP.

## Funções {#features}

O servidor MCP do Scrapling oferece dezesseis ferramentas para extrair dados web e interagir com o navegador. As ferramentas de uso único obtêm uma URL e fecham seu próprio navegador ou cliente. As ferramentas de sessão mantêm cookies e configurações entre chamadas, para que a IA possa continuar as ações na mesma aba e consultar o histórico de rede.

### Ferramentas de uso único {#one-shot-tools}

#### 🚀 Extração básica por HTTP {#basic-http-scraping}

- **`make_request`**: Solicitações HTTP rápidas com qualquer método (GET, POST, PUT, DELETE) e imitação da impressão digital do navegador. Gera cabeçalhos reais de navegador que correspondem à versão de TLS, oferece suporte a HTTP/3 e mais.

#### 🔒 Extração com navegador Stealthy {#stealth-browser-scraping}

- **`browser_fetch_once`**: Executa JavaScript e extrai dados de páginas dinâmicas com nosso navegador Stealthy. Permite alterar a impressão digital do navegador, contornar Turnstile e Interstitial do Cloudflare e controlar tanto o navegador quanto a solicitação.

### Ferramentas de sessão {#session-tools}

#### 🔌 Gerenciamento de sessões {#session-management}

- **`browser_open`**: Cria uma sessão persistente de navegador Stealthy que permanece aberta entre chamadas a `browser_fetch`. Assim, não é preciso iniciar um navegador a cada vez. Guarda a configuração do navegador e devolve apenas `session_id` e `session_type`. Use `list_sessions` para ver as configurações em uso em `settings`, que fica vazio nas sessões CDP.
- **`open_request_session`**: Cria uma sessão HTTP persistente sem navegador para usar com `session_make_request`. Mantém cookies, conexões e a impressão digital do navegador (`impersonate`) entre solicitações. Devolve apenas `session_id` e `session_type`, com o tipo `static`. Use `list_sessions` para ver as configurações em uso em `settings`.
- **`close_session`**: Fecha uma sessão persistente, de navegador ou de solicitações, e libera seus recursos.
- **`list_sessions`**: Lista todas as sessões ativas com seus detalhes e `settings`.

#### Estado do navegador {#browser-state}

- **`browser_save_state`**: Salva cookies, armazenamento local e IndexedDB em um arquivo JSON compatível com Playwright. Assim, o estado de login pode ser reutilizado depois que a sessão do navegador terminar. Se o arquivo já existir, será substituído.
- **`browser_load_state`**: Restaura um arquivo salvo em uma sessão de navegador aberta, mesmo antes de carregar a primeira página. Substitui o estado armazenado atual sem fechar as abas nem navegar para outras páginas. Obtenha ou recarregue a página para usar o login restaurado.

Os arquivos de estado ficam no computador que executa o servidor MCP. Eles não incluem `sessionStorage`, abas abertas nem configurações do navegador.

#### 🎯 Obter páginas por uma sessão {#fetching-through-a-session}

- **`browser_fetch`**: Executa JavaScript e extrai dados de uma URL por uma sessão aberta de navegador Stealthy. Permite alterar a impressão digital do navegador e contornar Turnstile e Interstitial do Cloudflare. Também pode gerar um snapshot, uma visão estruturada da página com referências, posições e tamanhos dos elementos, para ajudar a IA a identificar controles e planejar ações do mouse.
- **`session_make_request`**: Faz solicitações HTTP rápidas com qualquer método (GET, POST, PUT, DELETE), imitação da impressão digital do navegador, cabeçalhos correspondentes e suporte a HTTP/3. Reutiliza cookies, conexões e a impressão digital do navegador por uma sessão aberta com `open_request_session`.

#### 📸 Capturas de tela {#screenshots}

- **`browser_screenshot`**: Captura a página atual ou um elemento em PNG ou JPEG sem recarregar. Permite conferir campos preenchidos, menus abertos, gráficos ou cartões de resultados. Capturar um só elemento reduz o conteúdo que não interessa. Aceita a área visível, a página inteira ou um elemento, com qualidade JPEG ajustável. A captura é devolvida como um bloco de imagem real que o modelo pode ver diretamente.

#### Conteúdo da página atual {#current-page-content}

- **`browser_extract`**: Lê a página atual ou um elemento como snapshot para IA, HTML, Markdown ou texto, sem recarregar. Extraia resultados depois de preencher formulários ou carregar mais conteúdo. Os snapshots incluem funções, nomes, referências, posições e tamanhos dos elementos para ações posteriores. A busca por expressão regular devolve as linhas do snapshot que correspondem ao padrão, com o contexto próximo e os nós pais.

#### Ações do navegador {#browser-actions}

- **`browser_actions`**: Encadeia ações do mouse, preenchimento de campos, atalhos de teclado, respostas a caixas de diálogo e esperas em uma chamada. Aceita ou dispensa alertas e confirmações do navegador, ou insere texto em caixas de entrada. Por exemplo, preenche um campo de busca, envia a consulta, espera os resultados e abre um deles. A IA pode agrupar etapas que já conhece e obter snapshots separados quando precisar conferir uma mudança na página. Assim, não é preciso voltar ao agente entre uma etapa e a próxima. Isso ajuda com menus que desaparecem rápido e outros controles que exigem uma ação rápida em seguida.

    Mostra menus e dicas ao passar o mouse, clica em botões e links, ou move o mouse sobre um painel aninhado para rolá-lo na vertical ou horizontal. Movimentos e cliques aceitam seletores, referências de snapshots ou coordenadas. Quando o alvo é um elemento, esperam e rolam a página até ele ficar visível de forma automática. Aceitam movimentos por coordenadas em várias etapas, cliques com os botões esquerdo, direito e do meio, além de clique duplo.

    Localize campos em qualquer parte da página com seletores ou referências de snapshots. Preencha texto, marque ou desmarque caixas, selecione botões de opção e escolha uma ou mais opções de listas suspensas nativas pelo texto visível. O texto pode substituir o conteúdo atual, apagá-lo ou continuar da posição do cursor. Atalhos de teclado podem selecionar e apagar texto, mudar o foco, enviar formulários ou fechar menus. O modo lento digita um caractere por vez, com pausas aleatórias entre os caracteres e entre todas as ações.

    Espere os resultados aparecerem, as camadas de carregamento sumirem ou os eventos de carregamento da página antes da próxima ação. Também aceita pausas fixas e espera pela redução da atividade de rede.

#### JavaScript {#javascript}

- **`browser_evaluate`**: Executa JavaScript na página atual para extração de dados personalizada, cálculos e tarefas específicas da página. A IA pode reunir dados de vários elementos, ler o estado da aplicação ou atualizar o conteúdo. Aceita scripts assíncronos e devolve os resultados como JSON.

#### Histórico de rede {#network-history}

- **`browser_network_requests`**: Busca solicitações concluídas entre abas, carregamentos de página e ações do navegador. Descubra as chamadas de API por trás dos dados de uma página, confira erros HTTP e siga redirecionamentos salvos. Os recursos estáticos ficam ocultos por padrão para reduzir o resultado. Devolve detalhes das solicitações como JSON, com paginação para históricos longos.
- **`browser_network_request`**: Consulta o resumo, os cabeçalhos, os dados enviados ou o corpo de texto da resposta de uma solicitação registrada. Devolve a parte escolhida por completo como JSON estruturado, sem carregar a página nem repetir a solicitação. As respostas salvas continuam disponíveis depois de mudar de página. Os limites de tamanho mantêm o histórico limitado; uma nota explica os corpos que não são texto, são grandes demais ou não podem ser lidos. Leia os dados necessários antes de fechar a sessão MCP.

Os corpos de resposta só são lidos e salvos para valores de `Content-Type` de texto compatíveis, como HTML, JSON, XML ou JavaScript. Para tipos binários, ausentes ou desconhecidos, são mantidos os metadados e os cabeçalhos da solicitação, sem ler nem salvar os corpos de resposta. O navegador continua carregando os recursos normalmente.

Somente solicitações concluídas são salvas, incluindo respostas HTTP 4xx e 5xx. Solicitações com falha ou ainda em andamento são omitidas. As entradas aparecem quando a captura termina; ler o histórico ou fechar a sessão não espera por elas. Capturas em andamento na hora de navegar ou fechar podem ser omitidas. Os bytes salvos vêm do navegador e podem ser diferentes dos bytes do servidor. O texto registrado usa a decodificação UTF-8 do Playwright quando válida e, caso contrário, a codificação declarada.

### Shadow DOM {#shadow-dom}

Defina `pierce_shadow=true` em `browser_fetch_once` ou em cada chamada a `browser_fetch` para incluir conteúdo de Shadow DOM aberto. O padrão é `false`. Consulte [Shadow DOM](../fetching/stealthy.md#shadow-dom) para ver exemplos de seletores e seus limites.

Os seletores do navegador também podem localizar elementos dentro de Shadow DOM fechado e interagir com eles.

### Funções principais {#key-capabilities}

- **Extração de conteúdo**: Converta páginas ou elementos em Markdown ou HTML, ou extraia uma versão limpa do texto.
- **Seletores CSS**: Use o mecanismo do Scrapling para escolher elementos específicos antes de passar o conteúdo para a IA.
- **Contornar proteções contra bots**: Lide com Turnstile, Interstitial e outras proteções do Cloudflare.
- **Proxies**: Use proxies para ocultar seu endereço e escolher a localização das solicitações.
- **Imitação do navegador**: Imite navegadores reais com a impressão digital TLS, cabeçalhos que correspondem à versão e outras opções.
- **Sessões persistentes**: Reutilize sessões do navegador entre solicitações para melhorar o desempenho.
- **Bloqueio de anúncios**: Todas as ferramentas de navegador bloqueiam automaticamente solicitações a cerca de 3.500 domínios conhecidos de anúncios e rastreamento. Isso economiza tokens e acelera o carregamento.
- **Proteção contra injeção de instruções**: Remove automaticamente conteúdo oculto que poderia ser usado para atacar o modelo: elementos ocultos por estilos inline, aria-hidden, slots ocultos, caracteres de largura zero, comentários HTML e tags template.

## Instalação {#installation}

Instale o Scrapling com suporte a MCP e confira se as dependências do navegador também estão instaladas.

```bash
# Install Scrapling with MCP server dependencies
pip install "scrapling[ai]"

# Install browser dependencies
scrapling install
```

Você também pode usar a imagem Docker diretamente do registro do Docker:
```bash
docker pull pyd4vinci/scrapling
```
Ou baixá-la do registro do GitHub:
```bash
docker pull ghcr.io/d4vinci/scrapling:latest
```

## Configurar o servidor MCP {#setting-up-the-mcp-server}

Aqui vamos mostrar como adicionar o servidor MCP do Scrapling ao [Claude Desktop](https://claude.ai/download) e ao [Claude Code](https://www.anthropic.com/claude-code). Os mesmos passos gerais servem para outros chatbots compatíveis com MCP:

!!! note "Nota"
    O comando `scrapling-mcp` dos exemplos foi adicionado na versão 0.4.13 como atalho para `scrapling mcp`. Ele facilita adicionar o Scrapling a registros e clientes MCP que esperam um único comando. Se você usa uma versão anterior, use o comando `scrapling` com `mcp` como primeiro argumento.

### Claude Desktop {#claude-desktop}

1. Abra o Claude Desktop.
2. Clique no menu (☰) no canto superior esquerdo e vá para Settings → Developer → Edit Config.
3. Adicione a configuração do servidor MCP do Scrapling:
```json
"ScraplingServer": {
  "command": "scrapling-mcp"
}
```
Se esse for o primeiro servidor MCP que você adiciona, use este conteúdo no arquivo:
```json
{
  "mcpServers": {
    "ScraplingServer": {
      "command": "scrapling-mcp"
    }
  }
}
```
Segundo o [artigo oficial](https://modelcontextprotocol.io/quickstart/user), essa ação cria um arquivo de configuração se ele ainda não existir ou abre o arquivo atual. Ele fica em:

1. **MacOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
2. **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

Para garantir que funcione, use o caminho completo do executável `scrapling-mcp`. Você pode encontrá-lo com:

1. **MacOS**: `which scrapling-mcp`
2. **Windows**: `where scrapling-mcp`

No meu Mac, o resultado foi `/Users/<MyUsername>/.venv/bin/scrapling-mcp`, então usei esta configuração:
```json
{
  "mcpServers": {
    "ScraplingServer": {
      "command": "/Users/<MyUsername>/.venv/bin/scrapling-mcp"
    }
  }
}
```
#### Docker {#docker}

Se você usa a imagem Docker, a configuração fica parecida com esta:
```json
{
  "mcpServers": {
    "ScraplingServer": {
      "command": "docker",
      "args": [
        "run", "-i", "--rm", "pyd4vinci/scrapling", "mcp"
      ]
    }
  }
}
```

A mesma lógica vale para [Cursor](https://cursor.com/docs/context/mcp), [WindSurf](https://windsurf.com/university/tutorials/configuring-first-mcp-server) e outros clientes.

### Claude Code {#claude-code}

Com o [Claude Code](https://www.anthropic.com/claude-code), é mais simples:

```bash
claude mcp add ScraplingServer "/Users/<MyUsername>/.venv/bin/scrapling-mcp"
```
Para obter o caminho do executável do Scrapling:

1. **MacOS**: `which scrapling-mcp`
2. **Windows**: `where scrapling-mcp`

Consulte o artigo da Anthropic sobre [como adicionar servidores MCP ao Claude Code](https://docs.anthropic.com/en/docs/claude-code/mcp#option-1%3A-add-a-local-stdio-server) para mais detalhes.

Depois de adicionar o servidor, feche por completo e abra novamente o aplicativo. No Claude Desktop, você deve ver o indicador de servidor MCP (🔧) no canto inferior direito do campo de chat, ou `ScraplingServer` no menu `Search and tools` desse campo.

### Executável de navegador personalizado {#custom-browser-executable}

As ferramentas `browser_fetch_once` e `browser_open` podem usar um executável de navegador compatível com Chromium no lugar do Chromium incluído. Isso é útil para versões próprias do navegador ou mecanismos mais leves.

Para definir o executável uma só vez para todo o servidor MCP, passe o caminho ao iniciar o servidor:

```bash
scrapling-mcp --executable-path "/path/to/chromium"
```

Na configuração do Claude Desktop, adicione a opção aos argumentos do servidor:

```json
{
  "mcpServers": {
    "ScraplingServer": {
      "command": "/Users/<MyUsername>/.venv/bin/scrapling-mcp",
      "args": [
        "--executable-path",
        "/path/to/chromium"
      ]
    }
  }
}
```

Você também pode definir a variável de ambiente `SCRAPLING_EXECUTABLE_PATH` antes de iniciar o servidor. A IA ainda pode escolher outro executável para uma chamada a `browser_fetch_once` ou ao abrir uma sessão com `browser_open`.

### Conectar a navegadores remotos {#connecting-to-remote-browsers}

`browser_open` não precisa iniciar um navegador local. Passe uma URL de CDP para conectar a um navegador já aberto pelo [Chrome DevTools Protocol](https://chromedevtools.github.io/devtools-protocol/). Ele pode estar no mesmo computador, em outro ou em um serviço de navegadores gerenciados:
```
Open a stealthy browser session on wss://cdp.provider.example/session/abc123, then use it to scrape the product details from https://shop.example.com. Close the session when you're done.
```
O `session_id` recebido é usado normalmente com `browser_fetch`, `browser_extract`, `browser_actions`, `browser_evaluate`, `browser_screenshot`, `browser_network_requests`, `browser_network_request`, `browser_save_state` e `browser_load_state`.

A URL pode ser um endpoint WebSocket (`ws://`/`wss://`), como os fornecidos por serviços de navegadores, ou o endpoint HTTP de um navegador que você iniciou com a porta de depuração remota ativada:
```commandline
chrome --remote-debugging-port=9222
```
Nesse caso, conecte com `cdp_url="http://localhost:9222"`, ou com o endereço do computador se o navegador estiver em outra máquina.

!!! note "Notas"

    * Como o navegador já está aberto, as sessões CDP ignoram opções que só se aplicam à inicialização: `headless`, `real_chrome` e `executable_path`, incluindo o padrão do servidor descrito acima.<br/>
    * As outras opções continuam valendo (`locale`, `useragent`, `proxy`, `cookies`, `timezone_id` etc.), porque cada sessão cria seu próprio contexto no navegador remoto.

### Streamable HTTP {#streamable-http}

Desde a versão 0.3.6, o servidor MCP pode usar o transporte 'Streamable HTTP' no lugar do transporte tradicional 'stdio'.

Em vez deste comando para 'stdio':
```bash
scrapling-mcp
```
Use o seguinte para ativar 'Streamable HTTP':
```bash
scrapling-mcp --http
```
Por padrão, o servidor escuta em '127.0.0.1', na porta 8000. Você pode mudar os dois valores:
```bash
scrapling-mcp --http --host '0.0.0.0' --port 8000
```
A configuração padrão só aceita conexões do mesmo computador. Passe `--host '0.0.0.0'` se quiser acessar o servidor pela rede. Essa opção é independente da autenticação explicada abaixo.

Se você executar 'Streamable HTTP' dentro do Docker, precisa usar '0.0.0.0' e definir um token. Caso contrário, a porta publicada não consegue chegar ao servidor, porque o '127.0.0.1' do contêiner só é visível de dentro dele:
```bash
docker run -p 8000:8000 -e SCRAPLING_MCP_AUTH_TOKEN="<your-token>" pyd4vinci/scrapling mcp --http --host '0.0.0.0'
```

### Autenticação {#authentication}

Somente o programa que inicia o servidor consegue acessar o transporte 'stdio'. Já com 'Streamable HTTP', qualquer pessoa que alcance a porta pode chamar todas as ferramentas. Isso inclui acessar qualquer URL a partir do computador que executa o servidor. Por isso, 'Streamable HTTP' exige autenticação: `--http` sozinho não inicia o servidor e pede um token:
```bash
scrapling-mcp --http --auth-token "$(openssl rand -hex 32)"
```
Os clientes precisam enviar esse token em um cabeçalho `Authorization`. Solicitações sem ele são rejeitadas com um `401`:
```json
{
  "mcpServers": {
    "ScraplingServer": {
      "url": "https://your-server.example.com/mcp",
      "headers": {
        "Authorization": "Bearer <your-token>"
      }
    }
  }
}
```
Passar o token pela linha de comando deixa o valor no histórico do shell e na lista de processos. Por isso, prefira a variável de ambiente `SCRAPLING_MCP_AUTH_TOKEN`:
```bash
export SCRAPLING_MCP_AUTH_TOKEN="<your-token>"
scrapling-mcp --http
```
Se você realmente precisa de um servidor sem autenticação, por exemplo para testes locais no '127.0.0.1' padrão, indique isso com `--no-auth`:
```bash
scrapling-mcp --http --no-auth
```
Combinar `--no-auth` com `--host '0.0.0.0'` deixa todas as ferramentas acessíveis a qualquer pessoa que alcance a porta. Evite essa combinação fora de uma rede confiável.

Quando o servidor escuta em um endereço público, informe também quais nomes de host ele deve aceitar. Isso ativa a proteção contra ataques de DNS rebinding, nos quais um site que você visita tenta se comunicar com seu servidor. A opção pode ser repetida:
```bash
scrapling-mcp --http --allowed-host 'your-server.example.com:8000'
```

!!! note "Notas"

    * A autenticação só vale para 'Streamable HTTP'. Com 'stdio', ela é ignorada e o servidor registra um aviso.<br/>
    * HTTP sem criptografia envia o token em texto legível. Antes de expor o servidor à internet, coloque-o atrás de um proxy reverso que receba as conexões TLS e encaminhe as solicitações ao servidor.<br/>
    * A autenticação usa uma única chave compartilhada, não credenciais separadas por cliente. Todos usam o mesmo token, e trocar o valor exige reiniciar o servidor.<br/>
    * Iniciar o servidor com `--http --no-auth` ainda registra um aviso de que ele está sem autenticação.<br/>
    * Se você passar `--auth-token` e `--no-auth` juntos, o token será mantido e o servidor continuará autenticado.

## Exemplos {#examples}

Estes são alguns prompts que usamos ao testar o servidor MCP. Você provavelmente vai pensar em outros ainda melhores :)

Vamos começar com instruções simples e avançar para as mais complexas. Os exemplos usam Claude Desktop, mas a mesma lógica serve para outros clientes.

1. **Extração básica de dados web**

    Extraia o conteúdo principal de uma página como Markdown:

    ```
    Scrape the main content from https://example.com and convert it to markdown format.
    ```

    O Claude pode usar `make_request` para obter a página e devolver conteúdo limpo e fácil de ler. As solicitações HTTP têm três tentativas por padrão, com um segundo de espera entre elas. Se a página precisar de JavaScript ou bloquear solicitações HTTP, a IA pode usar `browser_fetch_once`. As duas ferramentas fecham seus próprios recursos depois da chamada.

    Uma versão mais precisa do mesmo prompt seria:
    ```
    Use regular requests to scrape the main content from https://example.com and convert it to markdown format.
    ```
    Assim você diz ao Claude qual ferramenta usar, sem que ele precise adivinhar. Às vezes ele começa com solicitações comuns; em outras, escolhe um navegador sem motivo claro. Como regra geral, informe qual ferramenta deve usar para economizar tempo e dinheiro e obter resultados consistentes.

2. **Extração de dados específicos**

    Extraia elementos específicos com seletores CSS:

    ```
    Get all product titles from https://shop.example.com using the CSS selector '.product-title'. If the request fails, retry up to 5 times every 10 seconds.
    ```

    O servidor extrai apenas os elementos que correspondem ao seletor e devolve uma lista estruturada. No exemplo, pedi até cinco tentativas caso o site tenha problemas de conexão, mas o padrão costuma ser suficiente.

3. **Coletar dados de lojas online**

    Este prompt é um pouco mais complexo:
    ```
    Open a stealthy browser session and visit these e-commerce URLs one at a time:
    - https://shop1.com/product-a
    - https://shop2.com/product-b  
    - https://shop3.com/product-c
    
    Get the product names, prices, and descriptions from each page. Close the session when done.
    ```

    O Claude pode reutilizar uma sessão de navegador, chamar `browser_fetch` para cada URL em ordem e depois analisar os dados extraídos.

4. **Um processo mais avançado**

    Imagine que eu queira obter todos os jogos de ação disponíveis na primeira página da loja PlayStation. Posso usar este prompt:
    ```
    Extract the URLs of all games on this page, then visit each game in order and return a list of all action games: https://store.playstation.com/en-us/pages/browse
    ```
    Peça à IA para reutilizar uma sessão HTTP, evitando abrir um navegador quando os dados estão disponíveis por solicitações comuns:
    ```
    Open an HTTP session, extract the URLs of all games on this page, then fetch each game in order and return a list of all action games. Close the session when done: https://store.playstation.com/en-us/pages/browse
    ```
    Se você sabe escrever seletores CSS, também pode limitar o conteúdo antes que a IA o leia:
    ```
    Use an HTTP session to extract the URLs of all games on the page below, then fetch each game in order and return a list of all action games.
    The selector for games in the first page is `[href*="/concept/"]` and the selector for the genre in each game page is `[data-qa="gameInfo#releaseInformation#genre-value"]`.
    Close the session when done.

    URL: https://store.playstation.com/en-us/pages/browse
    ```

5. **Obter dados de um site protegido pelo Cloudflare**

    Se você acha que o site usa proteção do Cloudflare, avise o Claude para que ele não tenha que descobrir sozinho.
    ```
    What's the price of this product? Be cautious, as it utilizes Cloudflare's Turnstile protection. Make the browser visible while you work.

    https://ao.com/product/oo101uk-ninja-woodfire-outdoor-pizza-oven-brown-99357-685.aspx
    ```

6. **Um processo longo**

    Você pode usar um prompt assim:
    ```
    Extract all product URLs for the following category, then return the prices and details for the first 3 products.
    
    https://www.arnotts.ie/furniture/bedroom/bed-frames/
    ```
    Mas este seria melhor:
    ```
    Go to the following category URL and extract all product URLs using the CSS selector "a". Then, reuse the session to fetch the first 3 product pages in order and extract each product’s price and details. Close the session when done.
    
    Keep the output in markdown format to reduce irrelevant content.
    
    Category URL:
    https://www.arnotts.ie/furniture/bedroom/bed-frames/
    ```

7. **Usar sessões persistentes**

    Ao extrair dados de várias páginas do mesmo site, use uma sessão de navegador persistente para evitar iniciar um navegador a cada solicitação:
    ```
    Open a stealthy browser session, then use it to scrape the main details from the first 5 product pages on https://shop.example.com. Close the session when you're done.
    ```
    O Claude usa `browser_open` para criar um navegador persistente, chama `browser_fetch` para cada página de produto nessa sessão e, ao final, chama `close_session`. Isso é muito mais rápido do que abrir um navegador para cada página.

    !!! danger "Perigo"

        Sempre feche as sessões persistentes ao terminar! Caso contrário, elas continuarão abertas.

8. **Usar uma sessão persistente em um processo longo**

    Outro exemplo longo que faz o Claude pensar:

    ```
    Use Scrapling MCP to do the following in this order:

    1. Open a stealthy browser session with headless mode off.
    2. Go to this page and collect the number of stars: https://github.com/D4Vinci/Scrapling
    3. From the README, get the URL that shows the number of downloads and go to it.
    4. Get the number of downloads and the top 3 countries from the graph.
    5. Prepare a report with the results.
    6. Close the browser.
    ```

E assim por diante. Aqui, sua criatividade faz a diferença.

## Boas práticas {#best-practices}

Estas dicas técnicas ajudam você a usar o servidor.

### 1. Escolher a ferramenta certa {#1-choose-the-right-tool}

- **`make_request`**: Solicitações HTTP rápidas para uma página ou chamada de API.
- **`browser_fetch_once`**: Uma página dinâmica ou com JavaScript, ou um site protegido, incluindo Cloudflare.
- **Ferramentas de sessão**: Solicitações relacionadas, ações do navegador, capturas de tela e histórico de rede.

### 2. Melhorar o desempenho {#2-optimize-performance}

- Reutilize uma sessão e obtenha cada URL em ordem.
- Desative os recursos desnecessários.
- Defina tempos limite adequados.
- Use seletores CSS para extrair apenas o que precisa.

### 3. Lidar com conteúdo dinâmico {#3-handle-dynamic-content}

- Use `network_idle` para aplicações de página única (SPAs).
- Defina `wait_selector` para esperar por elementos específicos.
- Aumente o tempo limite em sites que carregam devagar.

### 4. Qualidade dos dados {#4-data-quality}

- Use `main_content_only=true` para selecionar e limpar o corpo da página.
- Escolha um `extraction_type` adequado à sua tarefa.

### 5. Proteção contra injeção de instruções {#5-prompt-injection-protection}

O servidor MCP limpa automaticamente o conteúdo extraído quando `main_content_only` está ativado, como ocorre por padrão. Ele remove conteúdo oculto que sites maliciosos poderiam usar para inserir instruções no contexto da IA:

- **Estilos inline que ocultam conteúdo**: `display:none`, `visibility:hidden` e valores zero para opacidade, tamanho da fonte, altura, largura, altura máxima e largura máxima.
- **Elementos ocultos para acessibilidade**: `aria-hidden="true"`.
- **Tags de template e slots ocultos**: Elementos `<template>` e `<slot hidden>`.
- **Comentários HTML**: `<!-- ... -->`.
- **Caracteres de largura zero**: Caracteres Unicode invisíveis, como espaços de largura zero.

Essa proteção é aplicada automaticamente na extração de HTML, Markdown e texto. Mantenha `main_content_only=true`, o padrão, para obter a proteção máxima.

### 6. Gerenciar sessões {#6-manage-sessions}

- Use `make_request` ou `browser_fetch_once` para obter uma página de forma independente. Elas fecham seus próprios recursos e não deixam uma sessão aberta para chamadas posteriores.
- Use `browser_open` para criar uma sessão persistente quando trabalhar com várias páginas. Depois, chame `browser_fetch` para cada página nessa sessão.
- Para várias solicitações HTTP sem navegador, use `open_request_session` e chame `session_make_request` para cada uma. Isso mantém cookies, conexões e a impressão digital do navegador (`impersonate`) entre chamadas.
- As sessões mantêm a configuração definida ao abri-las: headless, locale, cookies e opções para ocultar a automação nos navegadores; `impersonate` e `proxy` nas sessões HTTP. As opções de cada solicitação, como timeout, wait_selector, network_idle e solve_cloudflare, são passadas para `browser_fetch`/`session_make_request` em cada chamada. Seus valores padrão aparecem nos esquemas das ferramentas.
- `browser_fetch` pode resolver desafios do Cloudflare na sessão aberta de navegador Stealthy.
- Sempre feche as sessões com `close_session` ao terminar para liberar os recursos.
- Use `list_sessions` para conferir quais sessões continuam ativas e ver o `settings` com que cada uma foi criada. Ele é devolvido ao agente de IA e fica vazio nas sessões CDP.
- Passe um `session_id` próprio para as ferramentas que abrem sessões. Assim, você pode dar nomes claros, como `"search"` ou `"checkout"`, em vez do valor hexadecimal aleatório. Elas geram um erro se o ID já estiver em uso, para que você detecte o conflito desde o início.

### 7. Capturas de tela {#7-capturing-screenshots}

- `browser_screenshot` captura a página já aberta por `browser_fetch` em uma sessão de navegador Stealthy. Não recarrega a página, então a IA pode conferir campos preenchidos, menus abertos e outros resultados das ações.
- A imagem é devolvida como um bloco `ImageContent` real, para que o modelo veja a página diretamente.
- Capture a área visível ou a página inteira, incluindo o conteúdo fora da tela.
- Capture um campo, gráfico, cartão ou resultado para conferir com menos conteúdo ao redor. A captura de um elemento pode rolar a página até ele ficar visível.
- Escolha PNG para imagens sem perda ou JPEG com qualidade ajustável para reduzir o tamanho.
- A IA pode usar `browser_actions` para esperar o conteúdo ou terminar as interações antes da captura.

## Questões legais e éticas {#legal-and-ethical-considerations}

⚠️ **Orientações importantes:**

- **Consulte o robots.txt**: Visite `https://website.com/robots.txt` para ver as regras de rastreamento.
- **Respeite os limites de solicitações**: Não sobrecarregue os servidores.
- **Termos de serviço**: Leia e siga os termos do site.
- **Direitos autorais**: Respeite os direitos de propriedade intelectual.
- **Privacidade**: Leve em conta as leis de proteção de dados pessoais.
- **Uso comercial**: Garanta que você tem permissão para usar os dados com fins comerciais.

---

*Criado com ❤️ pela equipe do Scrapling. Boa extração!*
