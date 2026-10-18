---
title: "Histórico de mudanças do Scrapling"
description: "Notas das versões do Scrapling, com novos recursos, correções e mudanças incompatíveis."
---

# Histórico de mudanças {#changelog}

Todas as mudanças importantes do Scrapling, extraídas das [versões no GitHub](https://github.com/D4Vinci/Scrapling/releases).

## [v0.5](https://github.com/D4Vinci/Scrapling/releases/tag/v0.5) - 2026-10-17 {#v0.5}

**O Scrapling v0.5 melhora quase tudo: busca de páginas, análise, spiders, automação do navegador, ferramentas de IA e documentação em dez idiomas 🚀**

!!! warning "Aviso"

    **Esta versão traz muitas mudanças incompatíveis que não cabem aqui. Confira o [guia de migração para a v0.5](migrating-to-v0.5.md) antes de atualizar.**

### 🚀 Novidades e melhorias de uso {#v0.5-new-stuff-and-quality-of-life-changes}

- **Um servidor MCP muito mais capaz para agentes de IA que podem resolver quase qualquer CAPTCHA** (confira a [documentação](ai/mcp-server.md)):

    - **Fluxos completos no navegador**: preencha formulários, clique, passe o cursor sobre elementos, role a página, use o teclado, trate diálogos e aguarde resultados em uma única sequência ordenada. Aceita diferentes tipos de campos e interações mais lentas, e as ações param no primeiro erro.
    - **Leia e pesquise a página atual sem recarregá-la**: extraia HTML, Markdown ou texto de uma página inteira ou de um elemento. As capturas da estrutura da página permitem buscas e mostram as funções, os nomes e as posições dos elementos, com visualizações focadas que mantêm o contexto ao redor.
    - **Execute JavaScript próprio e tire capturas de áreas específicas**: execute scripts, incluindo tarefas assíncronas, com acesso ao JavaScript da própria página. Capture elementos individuais, a área visível ou a página inteira em PNG ou JPEG.
    - **Inspecione a atividade de rede e reutilize logins**: examine solicitações e respostas registradas, salve e restaure o estado de login do navegador e interaja com elementos dentro de Shadow DOM aberto ou fechado. Leia o tráfego registrado antes de fechar a sessão.
    - **Use menos tokens e receba erros mais claros**: descrições mais curtas das ferramentas e orientações compartilhadas reduzem o texto repetido, enquanto as falhas do navegador e das solicitações chegam aos agentes com mensagens de erro úteis.

- **Veja as solicitações por trás da página**. Ative `record_requests=True` para registrar o tráfego concluído durante carregamentos, ações e entre abas. Depois, inspecione as respostas salvas sem enviar as solicitações novamente. (Confira a [documentação](fetching/stealthy.md#network-history))

    ```python
    from scrapling.fetchers import StealthySession

    with StealthySession(record_requests=True) as session:
        session.fetch("https://example.com", network_idle=True)
        for response in session.network.search(url_pattern=r"/api/", limit=None):
            print(response.url, response.status, response.body)
    ```

    - Filtre por URL, método, tipo de recurso ou status; obtenha uma resposta pelo ID. Inspecione cabeçalhos, dados enviados, respostas de APIs, erros HTTP e redirecionamentos pela API habitual de `Response`.
    - Mantém os corpos de texto aceitos com limites de tamanho, além dos metadados e do motivo quando um corpo não pode ser salvo. O limite padrão é de 1.000 solicitações. Funciona com sessões síncronas e assíncronas; o histórico salvo em Python continua disponível para leitura após o fechamento.

- **Salve um login uma vez e reutilize-o entre execuções**. `save_state(path)` e `load_state(path)` salvam e carregam cookies, armazenamento local e IndexedDB em JSON compatível com o Playwright. As sessões de navegador síncronas e assíncronas aceitam os dois métodos. (Confira a [documentação](fetching/stealthy.md#save-and-load-session-state))
    - Carregue o estado antes de buscar ou recarregar uma página. Exige um contexto de navegador compartilhado já iniciado e sem `proxy_rotator`; abas, configurações do navegador e `sessionStorage` não são salvos.

- **Extraia Shadow DOM aberto com `pierce_shadow=True`** e use CSS ou XPath como de costume. Disponível nos fetchers de navegador, nas sessões e na opção `--pierce-shadow` da CLI. Mantém o conteúdo dos slots sem mudar a página ativa. A captura de HTML exclui raízes fechadas e documentos de iframes. (Confira a [documentação](fetching/stealthy.md#shadow-dom))

- **Escolha como seu spider explora um site**. `CrawlSpider` e suas subclasses, incluindo `ContentSpider`, aceitam `crawl_strategy="bfs"` para agendar primeiro as solicitações mais antigas ou `"dfs"` para agendar primeiro as mais recentes. A prioridade continua prevalecendo, e páginas processadas ao mesmo tempo podem terminar em outra ordem. (Confira a [documentação](spiders/generic-templates.md#crawl-order))

### 🐛 Correções de erros {#v0.5-bug-fixes}

- **Melhorada a resolução de Cloudflare** com detecção de widgets que aparecem com atraso, menos esperas desnecessárias e limites nos loops de novas tentativas para desafios passivos e frames ocultos. Corrige [#468](https://github.com/D4Vinci/Scrapling/issues/468) e [#509](https://github.com/D4Vinci/Scrapling/issues/509).
- **Corrigida a inicialização do navegador a partir de um terminal do Windows com privilégios de administrador**. Corrige [#463](https://github.com/D4Vinci/Scrapling/issues/463).
- **Mantidas as opções de ocultação integradas ao adicionar opções próprias do navegador**, por @alkaz-nodemaven em [#430](https://github.com/D4Vinci/Scrapling/pull/430).
- **Melhorada a leitura da codificação de caracteres nas respostas do navegador**, incluindo declarações com diferenças entre maiúsculas e minúsculas, espaços ou valores entre aspas.
- **A ausência de um desafio de Cloudflare não é mais registrada como erro** quando não há desafio a resolver. Corrige [#459](https://github.com/D4Vinci/Scrapling/issues/459).

- **Corrigidas as impressões digitais das solicitações** para parâmetros de consulta, por @yetval em [#448](https://github.com/D4Vinci/Scrapling/pull/448), corpos JSON vazios ou com valores avaliados como falsos, por @ac1982 em [#480](https://github.com/D4Vinci/Scrapling/pull/480), e a ordem de inserção dos cabeçalhos, por @SarwadnyaMahajan em [#466](https://github.com/D4Vinci/Scrapling/pull/466).
- **Corrigida a transferência indevida de dados da solicitação para links seguidos**, incluindo cabeçalhos antigos relacionados ao corpo, por @yetval em [#462](https://github.com/D4Vinci/Scrapling/pull/462).
- **Impedido o armazenamento de respostas bloqueadas como entradas bem-sucedidas no cache de desenvolvimento**, por @Kuang-xianxin em [#446](https://github.com/D4Vinci/Scrapling/pull/446).
- **Mantidos os arquivos de pontos de controle quando um rastreamento falha com uma exceção**, por @SulimanAbdulrazzaq em [#486](https://github.com/D4Vinci/Scrapling/pull/486).
- **Corrigido o tratamento de falhas de robots.txt** para que consultas com falha não sejam armazenadas em cache como permissão para rastrear, por @prateekraawat1 em [#443](https://github.com/D4Vinci/Scrapling/pull/443).
- **Corrigida a extração de links com seletores que limitam o escopo**, incluindo correspondências vazias e seletores que apontam para o próprio elemento do link, por @SulimanAbdulrazzaq em [#452](https://github.com/D4Vinci/Scrapling/pull/452) e [#483](https://github.com/D4Vinci/Scrapling/pull/483).
- **Corrigido o encaminhamento para callbacks do sitemap**, por @SulimanAbdulrazzaq em [#458](https://github.com/D4Vinci/Scrapling/pull/458), **e a análise de XML com comentários ou instruções de processamento**, por @sup3dev em [#450](https://github.com/D4Vinci/Scrapling/pull/450).
- **Tratadas as marcas de ordem de bytes no início de robots.txt e feeds CSV**, por @SulimanAbdulrazzaq em [#453](https://github.com/D4Vinci/Scrapling/pull/453).
- **Corrigido o tratamento de `stealthy_headers` nas sessões HTTP dos spiders**, passando a opção para a sessão em vez de enviá-la diretamente ao `curl_cffi`, por @Yigtwxx em [#475](https://github.com/D4Vinci/Scrapling/pull/475).

- **Corrigida a codificação de formulários a partir de dicionários com valores de lista ou tupla**, mantendo a precedência do corpo da solicitação e o tratamento existente de `None`, com contribuições de @SulimanAbdulrazzaq em [#485](https://github.com/D4Vinci/Scrapling/pull/485).
- **Corrigida a combinação dos cabeçalhos HTTP da sessão e de cada solicitação sem distinguir maiúsculas de minúsculas**, por @SulimanAbdulrazzaq em [#487](https://github.com/D4Vinci/Scrapling/pull/487).
- **Corrigidas as solicitações da CLI que descartavam sem aviso corpos JSON vazios ou com valores avaliados como falsos**, por @SulimanAbdulrazzaq em [#484](https://github.com/D4Vinci/Scrapling/pull/484).
- **As exportações para arquivos Markdown e de texto agora usam sempre UTF-8**, e erros de conversão não truncam mais um arquivo de saída existente, por @SulimanAbdulrazzaq em [#488](https://github.com/D4Vinci/Scrapling/pull/488).
- **Corrigido o tratamento das opções de agente de usuário e proxy do curl em `curl2fetcher()`**, por @SulimanAbdulrazzaq em [#490](https://github.com/D4Vinci/Scrapling/pull/490).

- **Corrigidos os blocos Markdown que ficavam unidos sem separação** ao converter vários elementos selecionados por `Response.markdown()` ou pela extração da CLI, com contribuições de @Yigtwxx em [#432](https://github.com/D4Vinci/Scrapling/pull/432).
- **Corrigida a limpeza de conteúdo oculto na saída para IA** para manter conteúdo visível como `opacity:0.95`, reconhecer mais estilos que ocultam conteúdo e remover slots ocultos, com contribuições de @Yigtwxx em [#460](https://github.com/D4Vinci/Scrapling/pull/460).
- **Corrigida a remoção de tags de ruído que parava antes da hora ao encontrar tags aninhadas**, por @Yigtwxx em [#474](https://github.com/D4Vinci/Scrapling/pull/474).
- **Corrigidos os seletores CSS e XPath gerados para o primeiro de vários elementos irmãos com a mesma tag**, por @yellow-dog-dog em [#495](https://github.com/D4Vinci/Scrapling/pull/495).
- **Resolvido um aviso de descontinuação do analisador HTML do lxml**, por @afsuyadi em [#493](https://github.com/D4Vinci/Scrapling/pull/493).

### Documentação {#v0.5-docs}

- **O site inteiro agora está em dez idiomas**: inglês, árabe, espanhol, português do Brasil, francês, alemão, chinês simplificado, japonês, russo e coreano. Guias, referências de APIs, tutoriais e o [histórico de mudanças](changelog.md) estão traduzidos, com escrita da direita para a esquerda em árabe e trocas de idioma que mantêm a página e a seção.
- **Guias, exemplos do README e etapas de configuração mais claros**, abrangendo dados de pontos de controle, codificações do navegador, estado salvo, histórico de rede, Shadow DOM e ordem de rastreamento.
- **Atualizada a skill para agentes**, com seus exemplos, referências e arquivo para download, para as ferramentas atuais de navegador e MCP.
- **O histórico de mudanças foi movido para o site**, com acesso ao código-fonte Markdown de cada página.

### Projeto {#v0.5-project}

- Renovados o logotipo do Scrapling, as imagens de capa e a apresentação do site.
- Ampliados os testes de ações do navegador, diálogos, extração, capturas de tela, JavaScript, registro de rede, arquivos de estado, Shadow DOM e correções do rastreador.
- Adicionado um marcador para testes de navegador e execuções separadas para testes de navegador, assíncronos e em paralelo. Melhorada a compatibilidade com Windows dos testes de pontos de controle e CSV, por @diegobravtraps-oss em [#457](https://github.com/D4Vinci/Scrapling/pull/457).
- Atualizada a configuração compartilhada de compilação da documentação multilíngue e as orientações de contribuição.

## [v0.4.15](https://github.com/D4Vinci/Scrapling/releases/tag/v0.4.15) - 2026-08-23 {#v0.4.15}

**Uma das maiores versões deste ano: um servidor MCP reformulado, Markdown pronto para RAG em uma linha, um solucionador de Cloudflare melhorado e abas do navegador que continuam abertas para automação 🚀**

!!! warning "Aviso"

    **Esta versão traz mudanças incompatíveis no servidor MCP. Confira a seção de [mudanças incompatíveis](https://github.com/D4Vinci/Scrapling/blob/v0.4.15/docs/ai/mcp-server.md#breaking-changes) antes de atualizar.**

### 🚀 Novidades e melhorias de uso {#v0.4.15-new-stuff-and-quality-of-life-changes}

- **As abas do navegador agora continuam abertas e são reutilizadas entre solicitações** (confira a [documentação](fetching/stealthy.md#session-management)):
    - Todas as sessões do navegador mantêm suas abas após uma solicitação, e a próxima reutiliza uma aba livre em vez de abrir outra.
    - Cada solicitação reaplica suas próprias configurações (tempos limite, cabeçalhos e bloqueio de recursos) à aba que recebe, para que as configurações não passem de uma solicitação para outra.
    - As abas que apresentam erro são fechadas e substituídas, e o novo método `close_pages()` fecha todas as abas abertas.
    - A página que você buscou continua carregada, então uma função `page_setup` na próxima solicitação é executada nela antes de navegar para outra página. Isso permite encadear etapas de automação entre solicitações.

- **Transforme qualquer página em Markdown limpo e pronto para LLMs com `Response.markdown()`** (confira a [documentação](ai/building-rag-systems.md)):

    ```python
    from scrapling.fetchers import Fetcher

    markdown = Fetcher.get("https://example.com").markdown(main_content_only=True)
    ```

    - Scripts, estilos e conteúdo oculto de injeção de prompts são sempre removidos primeiro, com a mesma limpeza que o servidor MCP faz.
    - Passe `css_selector` para converter apenas os elementos de que você precisa.
    - Disponível pelo novo extra `rag` (`pip install "scrapling[rag]"`), também incluído nos extras `ai`/`shell`/`all`.

- **Novo modelo `SiteToMarkdownSpider` para rastrear um site inteiro e criar uma coleção de documentos Markdown para pipelines de RAG** (confira a [documentação](ai/building-rag-systems.md)):

    ```python
    from scrapling.spiders import SiteToMarkdownSpider

    class DocsSpider(SiteToMarkdownSpider):
        name = "docs"
        start_urls = ["https://example.com/docs/"]
        allowed_domains = {"example.com"}
        output_dir = "docs_markdown"

    result = DocsSpider().start()
    result.items.to_jsonl("docs.jsonl")
    ```

    - Produz um item por página com `url`/`title`/`markdown`, e o parâmetro opcional `output_dir` grava um arquivo Markdown por página.
    - `max_pages` limita o rastreamento e, como o modelo se baseia em `CrawlSpider`, redefinir `rules()` dá a você controle total sobre quais links são seguidos.

- **O servidor MCP foi reformulado (mudança incompatível)** (confira as [mudanças incompatíveis](https://github.com/D4Vinci/Scrapling/blob/v0.4.15/docs/ai/mcp-server.md#breaking-changes) e a [documentação](ai/mcp-server.md)):
    - As 13 ferramentas agora se dividem em dois modos: ferramentas de execução única (`fetch`, `bulk_fetch`, `stealthy_fetch`, `bulk_stealthy_fetch`), que sempre iniciam seu próprio navegador e mostram seus valores padrão reais, e ferramentas de sessão, que usam uma sessão aberta uma única vez.
    - A nova ferramenta `session_fetch` busca páginas por uma sessão do navegador, enquanto `open_session` agora guarda apenas as configurações do navegador e retorna as configurações efetivas da sessão para o agente de IA.
    - A ferramenta `get` passou a se chamar `make_request` e agora aceita qualquer método HTTP.
    - As novas ferramentas `open_request_session` e `session_make_request` dão à IA sessões HTTP persistentes que mantêm cookies e a impressão digital do navegador entre solicitações.
    - Isso também impede que as buscas redefinam as configurações da sessão, um problema corrigido primeiro por @Yigtwxx em [#418](https://github.com/D4Vinci/Scrapling/pull/418).

- **O transporte HTTP do servidor MCP agora exige autenticação e escuta em localhost por padrão (mudança incompatível)**, por @yamantaka-singh em [#414](https://github.com/D4Vinci/Scrapling/pull/414) (corrige [#413](https://github.com/D4Vinci/Scrapling/issues/413); confira a [documentação](ai/mcp-server.md#authentication)):
    - Passe `--auth-token` (ou a variável de ambiente `SCRAPLING_MCP_AUTH_TOKEN`) para exigir um token bearer, ou `--no-auth` se quiser disponibilizar o servidor sem autenticação de forma explícita.
    - Passe `--host 0.0.0.0` para aceitar conexões da rede.

### 🐛 Correções de erros {#v0.4.15-bug-fixes}

- **A resolução de Cloudflare Turnstile/Interstitial agora funciona independentemente do idioma e da região do navegador e não entra mais em um loop infinito em desafios interativos no modo sem interface**. As páginas do navegador com recursos de ocultação também deixam de falhar durante a resolução, com contribuições de @subediparas5 em [#412](https://github.com/D4Vinci/Scrapling/pull/412). (Corrige [#411](https://github.com/D4Vinci/Scrapling/issues/411) e [#422](https://github.com/D4Vinci/Scrapling/issues/422))
- **Corrigido o problema em que `find`/`find_all` com `class_` ignoravam sem aviso elementos com várias classes**, por @yetval em [#410](https://github.com/D4Vinci/Scrapling/pull/410), **e os valores vazios de `class_` e as strings CSS sem escape**, por @yamantaka-singh em [#417](https://github.com/D4Vinci/Scrapling/pull/417).
- **Corrigida a perda dos metadados da solicitação ao reutilizar respostas em cache no `development_mode`**, por @Yigtwxx em [#419](https://github.com/D4Vinci/Scrapling/pull/419).
- **Corrigidas as solicitações HTTP com `retries` abaixo de 1 que falhavam sem enviar a solicitação**, por @Yigtwxx em [#420](https://github.com/D4Vinci/Scrapling/pull/420).

### Documentação {#v0.4.15-docs}

- **As seções do site foram reorganizadas**: a nova seção "Uso com IA" reúne o servidor MCP, a nova página de [skill para agentes](ai/agent-skill.md) e o guia para [criar sistemas RAG](ai/building-rag-systems.md). O guia de migração do BeautifulSoup foi movido para junto da integração com Scrapy em "Integrações e migrações".
- **Adicionado um [histórico de mudanças](changelog.md)** ao repositório com as notas de todas as versões lançadas até agora.

## [v0.4.14](https://github.com/D4Vinci/Scrapling/releases/tag/v0.4.14) - 2026-08-10 {#v0.4.14}

**Uma versão rápida de manutenção para corrigir a instalação com `uv` 🔧**

### 🐛 Correções de erros {#v0.4.14-bug-fixes}

- **Corrigido o problema em que `uv` se recusava a instalar v0.4.13 por padrão e usava uma versão antiga sem aviso**. A versão anterior exigia uma versão preliminar de `curl_cffi`, o que `uv` não permite sem ativação explícita.
Todas as dependências agora são resolvidas com versões estáveis. (Corrige [#407](https://github.com/D4Vinci/Scrapling/issues/407))

## [v0.4.13](https://github.com/D4Vinci/Scrapling/releases/tag/v0.4.13) - 2026-08-09 {#v0.4.13}

**Uma nova atualização com spiders para feeds e um servidor MCP mais inteligente 🎉**

### 🚀 Novidades e melhorias de uso {#v0.4.13-new-stuff-and-quality-of-life-changes}

- **Novos modelos de spiders para feeds**. `XMLFeedSpider` percorre os nós de qualquer feed XML (RSS, Atom, feeds de produtos etc.), e `CSVFeedSpider` percorre as linhas CSV como dicionários. Ambos descompactam automaticamente os feeds comprimidos com gzip. (Confira a [documentação](spiders/generic-templates.md))

  ```python
  from scrapling.spiders import XMLFeedSpider

  class RSSSpider(XMLFeedSpider):
      name = "rss"
      start_urls = ["https://example.com/feed.xml"]

      async def parse_node(self, response, node):
          yield {"title": node.findtext("title"), "link": node.findtext("link")}

  result = RSSSpider().start()
  ```

- **O servidor MCP foi atualizado para MCP SDK v2 e ficou mais inteligente**. O servidor agora inclui instruções que ensinam seu agente de IA a usar as ferramentas de forma eficiente; cada ferramenta declara anotações para que clientes como Claude Code aprovem automaticamente as que apenas leem; as descrições das ferramentas estão mais curtas para economizar tokens; e o servidor informa sua versão e seu logotipo aos clientes MCP. (Confira a [documentação](ai/mcp-server.md))
- **Adicionado o comando `scrapling-mcp`**, que executa diretamente `scrapling mcp`, para registrar o Scrapling em clientes e registros MCP que esperam um único comando com apenas uma linha.
- **As versões do Playwright/Patchright e dos navegadores não são mais fixadas**. O User-Agent gerado agora sempre corresponde à versão exata do Chromium controlada pela instalação do Playwright/Patchright. Por isso, o Scrapling não fixa mais suas versões e você pode atualizá-las livremente. Execute `scrapling install --force` depois de atualizar para renovar os navegadores.

### 🐛 Correções de erros {#v0.4.13-bug-fixes}

- **Corrigida a falha ao importar o Scrapling com um ValueError do `browserforge`** quando o pacote de dados de impressões digitais fica atrás das versões dos navegadores. (Corrige [#394](https://github.com/D4Vinci/Scrapling/issues/394), [#396](https://github.com/D4Vinci/Scrapling/issues/396) e [#400](https://github.com/D4Vinci/Scrapling/issues/400))
- **Corrigido o tamanho incorreto dos pools de páginas nas ferramentas de navegador em lote do MCP**, que fazia `bulk_fetch` falhar com lotes de mais de 50 URLs e `bulk_stealthy_fetch` buscar todas as URLs em uma única aba, por @Yigtwxx em [#393](https://github.com/D4Vinci/Scrapling/pull/393).

### Projeto {#v0.4.13-project}

- **Nova [política de contribuições com IA](https://github.com/D4Vinci/Scrapling/blob/main/AI_POLICY.md)**: contribuições com ajuda de IA são bem-vindas, mas isso deve ser informado no PR ou na issue; envios que parecem gerados por IA sem informar isso recebem uma etiqueta e são fechados.

## [v0.4.12](https://github.com/D4Vinci/Scrapling/releases/tag/v0.4.12) - 2026-07-26 {#v0.4.12}

**Uma versão focada em tornar seus spiders mais inteligentes ao lidar com os sites que rastreiam**

### 🚀 Novidades e melhorias de uso {#v0.4.12-new-stuff-and-quality-of-life-changes}

- **Os spiders agora podem ajustar a própria velocidade com AutoThrottle.** Em vez de tentar adivinhar um `download_delay` que pode ser lento demais ou causar bloqueios, o spider mede a velocidade de resposta de cada site e ajusta a espera de cada domínio sozinho. Quando um site começa a bloquear você ou limitar suas solicitações, ele dobra a espera (ou aguarda exatamente o tempo indicado pelo cabeçalho `Retry-After`) até isso parar, e depois volta a acelerar. Seu `download_delay` e qualquer `Crawl-delay` de robots.txt continuam sendo o mínimo. (Confira a [documentação](spiders/advanced.md#autothrottle))

    ```python
    class MySpider(Spider):
        name = "adaptive"
        start_urls = ["https://example.com"]
        autothrottle_enabled = True
        autothrottle_start_delay = 2.0
        autothrottle_max_delay = 30.0
        autothrottle_block_backoff = True
    ```

- **Exporte seus resultados para CSV e XML**, além dos exportadores JSON/JSONL que você já tinha. Itens que não compartilham todas as chaves continuam sendo exportados sem perda de dados, e os valores aninhados são gravados como JSON. (Confira a [documentação](spiders/getting-started.md))

    ```python
    result = MySpider().start()
    result.items.to_csv("products.csv")
    result.items.to_xml("products.xml")
    ```

- **O servidor MCP agora pode exigir autenticação**, para que você possa disponibilizá-lo com segurança em vez de mantê-lo apenas no seu computador. Qualquer solicitação sem o token é rejeitada, e você também pode limitar os nomes de host aos quais o servidor responde. (Confira a [documentação](ai/mcp-server.md))

    ```bash
    scrapling mcp --http --auth-token "$(openssl rand -hex 32)"
    ```

- **Os navegadores agora aceitam URLs de CDP por HTTP**, além das de WebSocket. Assim, além dos endpoints `wss://` oferecidos pelos provedores de navegadores gerenciados, você pode conectar qualquer fetcher de navegador ou sessão MCP a um Chrome que iniciou com `--remote-debugging-port=9222`.

- **As imagens Docker publicadas agora recebem uma tag com sua versão**, em vez de apenas `latest`, para que você possa fixar a versão exata que quiser, por @JanRK em [#384](https://github.com/D4Vinci/Scrapling/pull/384).

### 🐛 Correções de erros {#v0.4.12-bug-fixes}

- **Corrigida a perda de todos os cookies nas respostas em cache** quando vinham de um motor de navegador, o que quebrava sem aviso a lógica de sessão ou autenticação que dependia deles no modo de desenvolvimento dos spiders, por @amitvijapur em [#379](https://github.com/D4Vinci/Scrapling/pull/379). (Corrige [#376](https://github.com/D4Vinci/Scrapling/issues/376))

- **Corrigido o problema em que `StealthyFetcher` impunha a configuração regional `en-US`** a todos os navegadores, em vez de seguir a do sistema. Isso fazia os sites perceberem uma diferença entre a configuração regional e o endereço IP e tratarem você como suspeito, como nas respostas 429 do Google. (Corrige [#381](https://github.com/D4Vinci/Scrapling/issues/381))

- **Corrigida uma mensagem de erro enganosa no sistema de armazenamento** e removida uma chamada sem uso que restava após as inserções, por @fix2015 em [#377](https://github.com/D4Vinci/Scrapling/pull/377).

### Desempenho {#v0.4.12-performance}

- **O tempo de execução de `get_all_text()` agora cresce em proporção ao número de nós, O(nodes)** em vez de percorrer os ancestrais de cada nó de texto, o que o torna cerca de 5-6 vezes mais rápido em páginas com muitos níveis aninhados, por @yetval em [#378](https://github.com/D4Vinci/Scrapling/pull/378).

## [v0.4.11](https://github.com/D4Vinci/Scrapling/releases/tag/v0.4.11) - 2026-07-12 {#v0.4.11}

**Uma atualização importante com o primeiro modelo de spider para uma plataforma, um parser mais rápido e correções importantes 🎉**

### 🚀 Novidades e melhorias de uso {#v0.4.11-new-stuff-and-quality-of-life-changes}

- **Adicionado `ShopifySpider`, o primeiro modelo de spider para uma plataforma!** Extraia todos os produtos de qualquer loja Shopify pela API JSON, sem usar o HTML do site. Crie uma subclasse, defina o domínio da loja e pronto (confira a [documentação](spiders/platform-templates.md))

  ```python
  from scrapling.spiders import ShopifySpider

  class MyStore(ShopifySpider):
      target_website = "example.com"

  result = MyStore().start()
  ```

- **Adicionado `--executable-path` aos comandos de navegador da CLI**. Tanto `scrapling extract fetch` quanto `scrapling extract stealthy-fetch` agora aceitam um executável de navegador personalizado compatível com Chromium e usam a variável de ambiente `SCRAPLING_EXECUTABLE_PATH` quando você não passa a opção. Assim, oferecem o mesmo recurso do servidor MCP (resolve [#371](https://github.com/D4Vinci/Scrapling/issues/371))

  ```bash
  scrapling extract fetch "https://example.com" page.html --executable-path "/path/to/chromium"
  ```

### 🤖 Melhorias de uso {#v0.4.11-quality-of-life-changes}
- **`find_by_text` e `find_by_regex` ficaram até cerca de 2 vezes mais rápidos** quando `first_match` está ativado (padrão), porque os elementos são convertidos em objetos apenas quando necessário, para que a busca pare na primeira correspondência, por @yetval em [#370](https://github.com/D4Vinci/Scrapling/pull/370)
- **Atualizados os benchmarks com os novos números em comparação com as versões mais recentes de todas as bibliotecas.**
- **Atualizadas as regras de contribuição**

### 🐛 Correções de erros {#v0.4.11-bug-fixes}

- **Corrigidas as falhas das ferramentas de obtenção de páginas do servidor MCP em páginas com caracteres de controle**, que causavam o erro `All strings must be XML compatible`, por @yetval em [#368](https://github.com/D4Vinci/Scrapling/pull/368) (corrige [#366](https://github.com/D4Vinci/Scrapling/issues/366))

## [v0.4.10](https://github.com/D4Vinci/Scrapling/releases/tag/v0.4.10) - 2026-07-04 {#v0.4.10}

**Uma nova atualização com uma nova integração com Scrapy e várias correções da comunidade 🎉**

### 🚀 Novidades e melhorias de uso {#v0.4.10-new-stuff-and-quality-of-life-changes}

- **Adicionada uma integração com Scrapy** para usar a API de parsing do Scrapling nos seus projetos Scrapy existentes sem reescrevê-los. Aplique o decorador `scrapling_response` a qualquer callback de um spider, e a resposta que ele recebe vira uma `Response` do Scrapling, enquanto o Scrapy continua cuidando do rastreamento (confira a [documentação](integrations/scrapy.md)):

    ```python
    import scrapy
    from scrapling.integrations.scrapy import scrapling_response

    class QuotesSpider(scrapy.Spider):
        name = "quotes"
        start_urls = ["https://quotes.toscrape.com"]

        @scrapling_response
        def parse(self, response):  # `response` is now a Scrapling Response
            first_quote = response.find_by_text("The world as we have created it", partial=True)
            for quote in [first_quote, *first_quote.find_similar()]:
                yield {"text": quote.get_all_text(strip=True)}
    ```

- **O servidor MCP agora pode usar um navegador personalizado compatível com Chromium** em todas as ferramentas baseadas em navegador. Defina-o uma vez com `scrapling mcp --executable-path "/path/to/chromium"` ou com a variável de ambiente `SCRAPLING_EXECUTABLE_PATH`, ou por solicitação com o argumento `executable_path`, por @samrusani em [#360](https://github.com/D4Vinci/Scrapling/pull/360) (resolve [#347](https://github.com/D4Vinci/Scrapling/issues/347))
- **Atualizados todos os navegadores e impressões digitais**. Execute `scrapling install --force` depois de atualizar para renová-los.

### 🐛 Correções de erros {#v0.4.10-bug-fixes}

- **Corrigido o texto ilegível (mojibake) dos fetchers de navegador em sites que não usam UTF-8**, por @yehudalevy-collab em [#365](https://github.com/D4Vinci/Scrapling/pull/365) (corrige [#364](https://github.com/D4Vinci/Scrapling/issues/364)).
- **Corrigido o problema em que `LinkExtractor` não filtrava extensões de arquivo compostas, como `.tar.gz`**, por @renbkna em [#359](https://github.com/D4Vinci/Scrapling/pull/359) (corrige [#349](https://github.com/D4Vinci/Scrapling/issues/349)).
- **Corrigida a perda de solicitações em andamento nos checkpoints de rastreamentos pausados, para que não sejam mais ignoradas ao retomar**, por @yetval em [#358](https://github.com/D4Vinci/Scrapling/pull/358).
- **Corrigido o cálculo incorreto das esperas de rastreamento a partir das diretivas `Request-rate` de robots.txt** com a atualização do Protego e testes ajustados por @Disaster-Terminator em [#355](https://github.com/D4Vinci/Scrapling/pull/355).

### Documentação {#v0.4.10-docs}

- **Esclarecida a interação de `init_script` com o contexto de execução isolado do Patchright no modo de ocultação**, por @mturac em [#353](https://github.com/D4Vinci/Scrapling/pull/353) (resolve [#350](https://github.com/D4Vinci/Scrapling/issues/350)).
- **Adicionado o método de instalação da skill para agentes pelo [skills.sh](https://skills.sh/D4Vinci/Scrapling)**, por @ob-aion em [#363](https://github.com/D4Vinci/Scrapling/pull/363).

## [v0.4.9](https://github.com/D4Vinci/Scrapling/releases/tag/v0.4.9) - 2026-06-07 {#v0.4.9}

**Uma atualização de manutenção cheia de correções de problemas relatados pela comunidade 🛠️**

### 🚀 Novidades e melhorias de uso {#v0.4.9-new-stuff-and-quality-of-life-changes}

- **Atualizados todos os navegadores e impressões digitais**. Execute `scrapling install --force` depois de atualizar para renová-los.
- **Adicionada a opção `--version` à CLI**, por @ETM-Code em [#303](https://github.com/D4Vinci/Scrapling/pull/303) (resolve [#299](https://github.com/D4Vinci/Scrapling/issues/299))

### 🐛 Correções de erros {#v0.4.9-bug-fixes}

- **Corrigido o problema em que o argumento `proxy` da sessão era ignorado sem aviso nas sessões HTTP**, o que podia expor seu IP real (resolve [#295](https://github.com/D4Vinci/Scrapling/issues/295)). Combinar um `proxy` da sessão com um argumento `proxies` por solicitação (ou o contrário) agora gera um erro, em vez de ignorar um deles sem aviso.
- **Corrigidas as falhas de navegação ao combinar `init_script` com `user_data_dir`** (resolve [#294](https://github.com/D4Vinci/Scrapling/issues/294)).
- **Corrigida a detecção de codificação quando os sites colocam o valor charset entre aspas no cabeçalho `Content-Type`**, por @Bortlesboat em [#323](https://github.com/D4Vinci/Scrapling/pull/323).
- **Corrigido um `IndexError` na realocação adaptativa de elementos quando `auto_save` está ativado**, por @Mubashirrrr em [#340](https://github.com/D4Vinci/Scrapling/pull/340).
- **Corrigidas as falhas ao salvar checkpoints e o cache dos spiders no Windows**, por @MrStarkEG em [#344](https://github.com/D4Vinci/Scrapling/pull/344).
- **Corrigido o cálculo de similaridade em `find_similar` para elementos com quantidades diferentes de atributos** (resolve [#322](https://github.com/D4Vinci/Scrapling/issues/322)).

### Documentação {#v0.4.9-docs}

- **Esclarecido que a instalação padrão inclui apenas o motor de parsing**, e que os fetchers e spiders precisam dos extras (resolve [#343](https://github.com/D4Vinci/Scrapling/issues/343)).
- **Corrigido o nome da imagem Docker nos exemplos restantes**, por @evanclan em [#315](https://github.com/D4Vinci/Scrapling/pull/315).
- **Corrigido um link quebrado no guia de contribuição**, por @Bortlesboat em [#320](https://github.com/D4Vinci/Scrapling/pull/320).

## [v0.4.8](https://github.com/D4Vinci/Scrapling/releases/tag/v0.4.8) - 2026-05-11 {#v0.4.8}

**Uma grande atualização dos spiders que melhora o sistema de rastreamento 🕷️**

### 🚀 Novidades e melhorias de uso {#v0.4.8-new-stuff-and-quality-of-life-changes}

- **Adicionada a ferramenta `LinkExtractor`** em `scrapling.spiders.LinkExtractor` para extrair URLs de uma `Response`. Ela oferece muitos controles (confira a [documentação](spiders/generic-templates.md))

    ```python
    from scrapling.spiders import LinkExtractor

    extractor = LinkExtractor(allow=r"/posts/", deny_domains=["ads.example.com"])
    ```

- **Adicionados os modelos genéricos de spider `CrawlSpider` e `CrawlRule`** para que você não precise escrever sempre o mesmo código de "seguir links que correspondem a este padrão". Redefina `rules()` para retornar uma lista de objetos `CrawlRule`, cada um associado a um `LinkExtractor`. (Confira a [documentação](spiders/generic-templates.md))

    ```python
    from scrapling.spiders import CrawlSpider, CrawlRule, LinkExtractor

    class QuotesSpider(CrawlSpider):
        name = "blog"
        start_urls = ["https://quotes.toscrape.com/"]

        def rules(self):
            return [
                CrawlRule(LinkExtractor(allow=r"/author/"), callback=self.parse_author),
                CrawlRule(LinkExtractor(allow=r"/page/\d+/")),  # pagination, no callback
            ]

        async def parse_author(self, response):
            yield {
                "name": response.css(".author-title::text").get(),
                "birthday": response.css(".author-born-date::text").get(),
                "url": response.url,
            }
    ```

- **Adicionado um modelo `SitemapSpider`** que inicia o rastreamento diretamente de um sitemap ou de URLs de `robots.txt`. Ele aceita sitemaps compactados com gzip e oferece muitos controles e opções. As URLs são encaminhadas pelas regras de rastreamento, como no exemplo de **CrawlSpider** acima. (Confira a [documentação](spiders/generic-templates.md))

    ```python
    from scrapling.spiders import SitemapSpider, CrawlRule, LinkExtractor

    class NewsSitemap(SitemapSpider):
        name = "news"
        sitemap_urls = ["https://example.com/robots.txt"]

        def rules(self):
            return [
                CrawlRule(LinkExtractor(allow=r"/articles/"), callback=self.parse_article),
            ]

        async def parse_article(self, response):
            yield {"url": response.url, "title": response.css("h1::text").get()}
    ```

- **A realocação adaptativa agora usa um limite padrão de similaridade de 40%**, em vez de `0`, em todos os métodos. Isso melhora o funcionamento do recurso adaptativo. Quando nenhum elemento supera o limite, um aviso mostra a maior pontuação encontrada, para que você possa reduzir `percentage` de forma consciente, se necessário.

- **Atualizados todos os navegadores e impressões digitais**. Execute novamente `scrapling install  --force` depois de atualizar para renovar os navegadores e impressões digitais.

### 🐛 Correções de erros {#v0.4.8-bug-fixes}

- **Corrigido o problema em que `Fetcher.configure(...)` não era aplicado às chamadas por solicitação**. A mesma correção foi aplicada a `AsyncFetcher`.
- **Corrigido o cálculo incorreto de impressões digitais das solicitações que causava solicitações duplicadas nos spiders**, por @yetval em [#255](https://github.com/D4Vinci/Scrapling/pull/255).
- **Corrigida a falta de aviso do motor de extração adaptativa em correspondências fracas.** Junto com a mudança de limite acima, agora você recebe um aviso em vez de um elemento enganoso como "melhor palpite" quando a realocação falha.

### Documentação {#v0.4.8-docs}

- **Atualizados os exemplos de código antigos** da documentação para corresponder à versão atual.
- **Melhorada a experiência de copiar e colar código** no site de documentação e reduzida a skill para agentes para usar menos tokens por chamada.

## [v0.4.7](https://github.com/D4Vinci/Scrapling/releases/tag/v0.4.7) - 2026-04-17 {#v0.4.7}

**Uma atualização focada em dar visão aos seus agentes de IA 📸**

### 🚀 Novidades e melhorias de uso {#v0.4.7-new-stuff-and-quality-of-life-changes}

- **Adicionada a ferramenta MCP `screenshot`**, que captura uma página e a retorna como um bloco MCP real de tipo `ImageContent`, para que o modelo possa vê-la. A ferramenta exige uma sessão de navegador aberta: chame `open_session` primeiro (com `dynamic` ou `stealthy`) e passe o `session_id` aqui. Aceita PNG e JPEG, capturas da página inteira, qualidade JPEG e os controles habituais de espera (`wait`, `wait_selector`, `network_idle`, `timeout`). (Implementa [#244](https://github.com/D4Vinci/Scrapling/issues/244))
- **Adicionado um parâmetro `session_id` personalizado a `open_session`** para dar nomes úteis às sessões (`"search"`, `"checkout"`), em vez do padrão hexadecimal aleatório de 12 caracteres. Por @hauntedhost em [#243](https://github.com/D4Vinci/Scrapling/pull/243)

### 🐛 Correções de erros {#v0.4.7-bug-fixes}

- **Corrigida a corrupção do estado de `FetcherSession` e uma falha ao fechar uma sessão com inicialização adiada**. Por @yetval em [#245](https://github.com/D4Vinci/Scrapling/pull/245)
- **Corrigido `TypeError: Session.request() got an unexpected keyword argument 'block_ads'`** ao usar a opção `--ai-targeted` da CLI com comandos HTTP. Por @voidborne-d em [#249](https://github.com/D4Vinci/Scrapling/pull/249) (corrige [#247](https://github.com/D4Vinci/Scrapling/issues/247))

### Traduções {#v0.4.7-translations}

- **Adicionada uma tradução do README para português brasileiro**, por @rgomids em [#250](https://github.com/D4Vinci/Scrapling/pull/250)

## [v0.4.6](https://github.com/D4Vinci/Scrapling/releases/tag/v0.4.6) - 2026-04-13 {#v0.4.6}

**Uma atualização focada no modo de ocultação do navegador, na privacidade e na experiência de desenvolvimento 🔒**

### 🚀 Novidades e melhorias de uso {#v0.4.6-new-stuff-and-quality-of-life-changes}

- **Adicionado bloqueio de anúncios integrado** para os fetchers de navegador. Passe `block_ads=True` para bloquear solicitações a cerca de 3.500 domínios conhecidos de anúncios e rastreadores ao interceptar a rota: sem DNS, sem TCP e com cancelamento imediato. Você pode combinar com `blocked_domains` para usar listas próprias. O servidor MCP e o modo `--ai-targeted` da CLI ativam isso automaticamente para economizar tokens e acelerar o carregamento das páginas.

    ```python
    page = StealthyFetcher.fetch('https://example.com', block_ads=True)
    ```

- **Adicionado suporte a DNS-over-HTTPS** para evitar vazamentos de DNS ao usar proxies. Passe `dns_over_https=True` para direcionar as consultas DNS ao serviço DoH da Cloudflare, evitando que a resolução DNS exponha sua localização real mesmo quando o tráfego HTTP passa por um proxy.

    ```python
    page = StealthyFetcher.fetch('https://example.com', proxy='http://proxy:8080', dns_over_https=True)
    ```

- **Adicionado o callback `page_setup`** para os fetchers de navegador. É uma função executada antes de `page.goto()`, que permite registrar listeners de eventos, rotas ou scripts que precisam ser preparados antes da navegação. Funciona junto com `page_action` (executado após a navegação). (Resolve [#237](https://github.com/D4Vinci/Scrapling/issues/237))

    ```python
    def capture_websockets(page):
        page.on("websocket", lambda ws: print(f"WS: {ws.url}"))

    page = DynamicFetcher.fetch('https://example.com', page_setup=capture_websockets)
    ```

- **Adicionadas as opções de CLI `--block-ads` e `--dns-over-https`** aos comandos `fetch` e `stealthy-fetch`.

### 🐛 Correções de erros {#v0.4.6-bug-fixes}

- **Corrigido o alias de tipo `Seconds`**, que rejeitava valores decimais. Passar `wait=1.5` ou `timeout=500.0` aos fetchers de navegador falhava com um erro de tipo porque o alias tratava `float` como metadados em vez de um tipo. Por @kuishou68 em [#240](https://github.com/D4Vinci/Scrapling/pull/240)
- **Corrigidos os segmentos ID duplicados na geração de seletores com caminho completo**. O seletor dos elementos com atributos `id` era adicionado duas vezes ao gerar caminhos CSS/XPath completos, produzindo seletores como `body > #main > #main > #target > #target`. Também foi corrigida a geração de condições `[@id='x']` isoladas (XPath inválido) em vez de `*[@id='x']` nos caminhos XPath completos. Por @sjhddh em [#241](https://github.com/D4Vinci/Scrapling/pull/241)
- **Corrigidos os parâmetros que faltavam nas assinaturas do shell**. As assinaturas das funções do shell interativo não incluíam `blocked_domains`, `block_ads`, `retries`, `retry_delay`, `capture_xhr`, `executable_path` e `dns_over_https`.

## [v0.4.5](https://github.com/D4Vinci/Scrapling/releases/tag/v0.4.5) - 2026-04-07 {#v0.4.5}

**Uma atualização com uma grande melhoria de uso para quem desenvolve spiders e algumas correções importantes 🎉**

### 🚀 Novidades e melhorias de uso {#v0.4.5-new-stuff-and-quality-of-life-changes}

- **Modo de desenvolvimento dos spiders**: testar mudanças na lógica de `parse()` de um spider antes exigia acessar os servidores do site de novo a cada execução. Isso é lento, gera tráfego e pode causar limites de solicitações enquanto você ainda ajusta os seletores. O novo modo de desenvolvimento salva cada resposta em disco na primeira execução e a reutiliza do disco nas seguintes. Assim, você pode ajustar os callbacks e executar quantas vezes quiser sem fazer nenhuma solicitação de rede. Ative com um atributo de classe:

    ```python
    class MySpider(Spider):
        name = "my_spider"
        start_urls = ["https://example.com"]
        development_mode = True

        async def parse(self, response):
            yield {"title": response.css("title::text").get("")}
    ```

    O cache fica em `.scrapling_cache/{spider.name}/` por padrão, e você pode mudar sua localização com `development_cache_dir`. Dois novos contadores, `cache_hits` e `cache_misses`, mostram o desempenho do cache. A reutilização do cache ignora `download_delay`, os limites de solicitações e o caminho de novas tentativas de solicitações bloqueadas, para que os testes sejam tão rápidos quanto o disco permitir. Não publique um spider com `development_mode = True`: é uma ferramenta de desenvolvimento, não um cache de produção. Confira a [documentação](spiders/advanced.md#development-mode) para todos os detalhes.

- **Redirecionamentos mais seguros por padrão**: o padrão de `follow_redirects` agora é `"safe"` em todos os fetchers HTTP, no servidor MCP e no shell. Os redirecionamentos continuam sendo seguidos, mas os que apontam para IPs internos ou privados (loopback, redes privadas e link-local) são rejeitados. Isso protege você contra SSRF ao extrair dados de URLs fornecidas por usuários. Passe `follow_redirects="all"` para recuperar o comportamento anterior, ou `False` para desativar todos os redirecionamentos.

### 🐛 Correções de erros {#v0.4.5-bug-fixes}

- **A parada forçada não perde mais seu checkpoint**: pressionar Ctrl+C duas vezes (parada forçada) em um spider com `crawldir` ativado podia coincidir com a gravação do checkpoint. O escopo de cancelamento encerrava a tarefa antes de terminar o pickle, deixava `paused=False` e acionava a limpeza que *exclui* o checkpoint anterior. Assim, interromper à força um rastreamento longo podia perder todo o progresso que você tentava salvar. O motor agora grava o checkpoint **antes** de chamar `cancel_scope.cancel()`, para que uma parada forçada sempre preserve o estado pendente mais recente. Por @voidborne-d em [#230](https://github.com/D4Vinci/Scrapling/pull/230).

## [v0.4.4](https://github.com/D4Vinci/Scrapling/releases/tag/v0.4.4) - 2026-04-05 {#v0.4.4}

**Uma nova atualização com melhorias importantes nos spiders e correções de erros 🎉**

### 🚀 Novidades e melhorias de uso {#v0.4.4-new-stuff-and-quality-of-life-changes}
- **Adicionado suporte ao cumprimento de robots.txt no sistema de spiders** com a nova opção `robots_txt_obey`. Quando ativada, o spider busca e respeita as regras de robots.txt automaticamente antes de rastrear, incluindo as diretivas `Disallow`, `Crawl-delay` e `Request-rate`. Os arquivos robots.txt são buscados de forma concorrente e mantidos em cache por domínio durante todo o rastreamento. Por @AbdullahY36 em [#226](https://github.com/D4Vinci/Scrapling/pull/226)
- **Adicionado o preenchimento prévio do cache de robots.txt**, para buscar e analisar os arquivos robots.txt de todos os domínios de start_urls antes de iniciar o loop de rastreamento, evitando atrasos na primeira solicitação a cada domínio.
- **Adicionada a nova estatística `robots_disallowed_count`** a `CrawlStats` para contar quantas solicitações foram bloqueadas pelas regras de robots.txt durante o rastreamento.

Confira no site [aqui](spiders/getting-started.md#robotstxt-compliance)

### 🐛 Correções de erros {#v0.4.4-bug-fixes}
- **Corrigido um problema importante de MRO com `ProxyRotator`**, no qual o método provisório `_build_context_with_proxy` ocultava a implementação real das classes filhas, fazendo a rotação de proxies sempre gerar `NotImplementedError` (corrige [#215](https://github.com/D4Vinci/Scrapling/issues/215)). Obrigado, @yetval
- **Corrigido um vazamento no pool de páginas** ao usar rotação de proxies por solicitação nas sessões do navegador. As páginas criadas em contextos temporários não eram removidas do pool na limpeza, acumulando referências antigas ao longo do tempo. Por @yetval em [#223](https://github.com/D4Vinci/Scrapling/pull/223)
- **Corrigida uma verificação de tipo ausente** no fetcher estático: `curl_cffi` podia retornar `None` de `session.request()`, causando erros depois.

### Outras mudanças {#v0.4.4-other}
- Atualizadas as dependências para incluir as impressões digitais mais recentes e outras novidades.
- Adicionado `protego` como nova dependência do grupo opcional `fetchers` para analisar robots.txt.

## [v0.4.3](https://github.com/D4Vinci/Scrapling/releases/tag/v0.4.3) - 2026-03-30 {#v0.4.3}

**Uma nova atualização com muitas mudanças importantes 🎉**

### 🚀 Novidades e melhorias de uso {#v0.4.3-new-stuff-and-quality-of-life-changes}
- **Adicionada uma nova ferramenta MCP** para abrir um navegador persistente, normal ou com recursos de ocultação, e continuar usando esse navegador com as outras ferramentas, além de outra ferramenta nova para fechá-lo. ([Exemplos](https://github.com/D4Vinci/Scrapling/blob/v0.4.3/docs/ai/mcp-server.md#examples))
- **Adicionada uma nova ferramenta MCP** para listar todas as sessões de navegador existentes, feita para usar com as novas ferramentas.
- **Adicionada uma nova opção às sessões do navegador** para coletar automaticamente todas as solicitações em segundo plano que ocorrem durante uma solicitação (resolve [#159](https://github.com/D4Vinci/Scrapling/pull/159)) [[Exemplos](https://github.com/D4Vinci/Scrapling/blob/v0.4.3/docs/fetching/dynamic.md#capturing-xhrfetch-requests)].
- **Adicionado um novo sanitizador** para proteger o servidor MCP de ataques comuns de injeção de prompts, removendo conteúdo oculto ou invisível.
- **Adicionada uma nova opção de linha de comando**, chamada `--ai-targeted`, aos comandos de extração web para preparar o conteúdo para IA e protegê-lo contra ataques comuns de injeção de prompts, como faz o servidor MCP.
- **Adicionada uma nova opção às sessões do navegador**, chamada `executable_path`, para definir um caminho de navegador personalizado (resolve [#202](https://github.com/D4Vinci/Scrapling/pull/202))
- **Reorganizado** o código do servidor MCP para facilitar a manutenção, e todas as ferramentas foram padronizadas como assíncronas.
- **Reorganizado** o código dos comandos da CLI para facilitar a manutenção e reduzi-lo em 210 linhas.

### 🐛 Correções de erros {#v0.4.3-bug-fixes}
- Correção para manter o método HTTP entre novas tentativas na sessão do spider, por @karesansui-u em [#201](https://github.com/D4Vinci/Scrapling/pull/201)
- Adicionado um limite máximo de tentativas de obter o conteúdo da página para evitar um loop infinito, por @haosenwang1018 e @D4Vinci em [#197](https://github.com/D4Vinci/Scrapling/pull/197)
- Substituído o `raise` sem argumento por `return False` em `_restore_from_checkpoint`, por @haosenwang1018 em [#196](https://github.com/D4Vinci/Scrapling/pull/196)
- Substituído `get_all` por `getall` em `Texthandler` para corresponder à classe Selector.

### Melhorias nos testes e na cobertura {#v0.4.3-coverage-tests-improvement}
- Adicionados testes de casos extremos de `_normalize_credentials`, por @Bortlesboat em [#192](https://github.com/D4Vinci/Scrapling/pull/192)
- Adicionados testes do ciclo de salvar e recuperar e do armazenamento principal, por @haosenwang1018 em [#193](https://github.com/D4Vinci/Scrapling/pull/193)
- Adicionada cobertura dos caminhos de regex de `TextHandler` e de `TextHandlers.re()`, por @haosenwang1018 em [#194](https://github.com/D4Vinci/Scrapling/pull/194)
- Adicionados testes de casos extremos de `filter`, `iterancestors` e `find_similar`, por @awanawana em [#200](https://github.com/D4Vinci/Scrapling/pull/200)

### Melhorias na skill para agentes {#v0.4.3-agent-skill-improvement}
- Corrigidos links Markdown quebrados nas referências da skill, por @yetval em [#204](https://github.com/D4Vinci/Scrapling/pull/204)
- Melhorada a estrutura da skill para passar melhor pela validação do [Clawhub](https://clawhub.ai/d4vinci/scrapling-official).
- A skill agora exige a opção de linha de comando `--ai-targeted` ao extrair dados por comandos.

### Melhorias na documentação {#v0.4.3-docs-improvement}
- Adicionada uma tradução do README para coreano, por @greatsk55 em [#187](https://github.com/D4Vinci/Scrapling/pull/187)
- Corrigidos os espaços entre caracteres CJK e latinos nos READMEs em chinês e japonês.
- Corrigidos links quebrados do design antigo do site.

## [v0.4.2](https://github.com/D4Vinci/Scrapling/releases/tag/v0.4.2) - 2026-03-08 {#v0.4.2}

**Uma nova atualização de manutenção com mudanças importantes**

#### Correções de erros {#v0.4.2-bug-fixes}
- A função `get_all_text()` agora também captura os nós de texto que vêm depois dos elementos. Assim, o servidor MCP e os comandos conseguem ler textos que antes eram ignorados ([#168](https://github.com/D4Vinci/Scrapling/pull/168)). Obrigado, @mhillebrand
- Referer agora retorna a URL base do Google em vez de uma URL de pesquisa do Google. A lógica anterior estava incorreta e podia gerar um sinal que ajudasse a identificar a impressão digital do navegador ([#179](https://github.com/D4Vinci/Scrapling/pull/179)). Obrigado, @Bortlesboat
- Corrigido um problema na junção de opções extras de inicialização em todos os navegadores. Obrigado, @rostchri
- Corrigido um problema nas anotações de tipos que causava falhas em versões do Python anteriores à 3.12. (Resolve [#163](https://github.com/D4Vinci/Scrapling/issues/163))

#### Outras mudanças {#v0.4.2-other}
- Adicionada uma Agent Skill para Claude Code / OpenClaw e outras ferramentas de agentes de IA.
- Adicionada a Agent Skill ao Clawhub.
- Todos os navegadores e o Playwright foram atualizados para as versões mais recentes.
- Adicionada uma tradução para francês do arquivo README principal.

## [v0.4.1](https://github.com/D4Vinci/Scrapling/releases/tag/v0.4.1) - 2026-02-27 {#v0.4.1}

**Uma nova atualização com muitas mudanças importantes**

### 🚀 Novidades e melhorias de uso {#v0.4.1-new-stuff-and-quality-of-life-changes}
- **Maior precisão das expressões regulares** na detecção de desafios do Cloudflare (Obrigado a @Rinz27 [#133](https://github.com/D4Vinci/Scrapling/pull/133))
- **Melhorias na velocidade e na eficiência** da resolução de desafios do Cloudflare. Agora ela é quase duas vezes mais rápida.
- **Melhorias na resolução de desafios do Cloudflare** para lidar com sites que às vezes mostram a página do Cloudflare duas vezes antes de redirecionar para o site principal.
- **Melhorias no modo de ocultação e na velocidade do navegador com recursos de ocultação** com a remoção dos arquivos JS injetados.
- **Melhorias no esquema MCP** para que seja aceito pelo OpenCode (Obrigado a @robin-ede [#137](https://github.com/D4Vinci/Scrapling/pull/137))
- **Maior compatibilidade do esquema MCP com o protocolo** para que seja aceito pelo VS Code Copilot e por outras ferramentas mais rigorosas. (Resolve #150 )
- **Grande redução no consumo de tokens do servidor MCP** com a remoção de tags HTML desnecessárias quando a opção `main_content_only` está ativada.
- Corrigida a página do PyPI e adicionados os arquivos necessários para cadastrar o servidor MCP no registro de servidores MCP.
- Adicionado um exemplo de código que mostra como instalar as dependências dos navegadores pelo código, em vez da linha de comando, para facilitar a automação.
- Todos os workflows foram melhorados com as versões mais recentes das actions (Obrigado a @salmanmkc [#143](https://github.com/D4Vinci/Scrapling/pull/143)/[#144](https://github.com/D4Vinci/Scrapling/pull/144))

## [v0.4](https://github.com/D4Vinci/Scrapling/releases/tag/v0.4) - 2026-02-15 {#v0.4}

**A maior versão do Scrapling até agora: framework de spiders, rotação de proxies e grandes melhorias no parser**

Esta versão traz um framework de spiders e rastreamento totalmente assíncrono, gerenciamento inteligente de proxies e mudanças importantes na API que tornam o Scrapling mais poderoso e consistente. Leia com atenção a seção de mudanças incompatíveis antes de atualizar.

### 🕷️ Framework de spiders {#v0.4-spider-framework}

Um novo framework de rastreamento assíncrono baseado em `anyio` para extração de dados organizada e em grande escala:

```python
from scrapling.spiders import Spider, Response

class MySpider(Spider):
  name = "demo"
  start_urls = ["https://example.com/"]

  async def parse(self, response: Response):
      for item in response.css('.product'):
          yield {"title": item.css('h2::text').get()}

MySpider().start()
```

-  **API de spiders semelhante à do Scrapy**: Defina spiders com `start_urls`, callbacks `parse` assíncronos, objetos `Request`/`Response` e uma fila de prioridades.
- **Rastreamento concorrente**: Limites de concorrência, controle da frequência por domínio e pausas entre downloads configuráveis.
- **Suporte a várias sessões**: Interface unificada para solicitações HTTP e navegadores sem interface gráfica com recursos de ocultação em um único spider. Direcione as solicitações para sessões diferentes pelo ID. Permite iniciar as sessões somente quando forem necessárias.
- **Pausar e retomar**: Salva o estado do rastreamento por meio de checkpoints. Pressione Ctrl+C para encerrar de forma organizada e reinicie para continuar de onde parou.
- **Modo streaming**: Receba os itens assim que forem extraídos por meio de `async for item in spider.stream()`, com estatísticas em tempo real. Ideal para interfaces, pipelines e rastreamentos longos.
- **Detecção de solicitações bloqueadas**: Detecta e repete automaticamente as solicitações bloqueadas, com lógica personalizável.
- **Exportação integrada**: Exporte os resultados por meio de hooks e do seu próprio pipeline, ou use a exportação integrada para JSON/JSONL com `result.items.to_json()` / `result.items.to_jsonl()`, respectivamente.
- **Hooks do ciclo de vida**: `on_start()`, `on_close()`, `on_error()`, `on_scraped_item()` e outros hooks para controlar todo o ciclo de vida do rastreamento.
- **Estatísticas detalhadas do rastreamento**: Acompanhe solicitações, respostas, bytes, códigos de status, proxies, detalhes por domínio e sessão, contagens por nível de log e muito mais.
- **Suporte a uvloop**: Passe `use_uvloop=True` para `spider.start()` para acelerar a execução assíncrona quando ele estiver disponível.

Uma nova seção foi adicionada ao site com todos os detalhes. Clique [aqui](spiders/architecture.md)

### 🔄 Rotação de proxies {#v0.4-proxy-rotation}

* Nova classe `ProxyRotator` com rotação segura entre threads. Funciona com todos os fetchers e sessões:

  ```python
  from scrapling import ProxyRotator
  rotator = ProxyRotator(["http://proxy1:8080", "http://proxy2:8080"])
  Fetcher.get(url, proxy_rotator=rotator)
  ```

* **Estratégias de rotação personalizadas**: Crie sua própria lógica de rotação de proxies
* **Troca de proxy por solicitação**: Passe `proxy=` para qualquer chamada individual a `get()`/`post()`/`fetch()` para substituir o proxy da sessão nessa solicitação.

### 🌐 Melhorias nos fetchers de navegador {#v0.4-browser-fetcher-improvements}

* **Bloqueio de domínios**: Novo parâmetro `blocked_domains` em `DynamicFetcher`/`StealthyFetcher` para bloquear solicitações a domínios específicos. Os subdomínios são incluídos automaticamente.
* **Novas tentativas automáticas**: Os fetchers de navegador agora repetem solicitações que falham com os parâmetros `retries` (padrão: 3) e `retry_delay` (padrão: 1s). Inclui detecção de erros relacionados a proxies.
* **Metadados da resposta**: O dicionário `Response.meta` salva automaticamente o proxy usado e incorpora os metadados da solicitação.
* **Response.follow()**: Crie objetos `Request` para solicitações seguintes com gerenciamento automático do referer, feitos para o sistema de spiders.
* **Sem reprodução automática**: As sessões de navegador agora bloqueiam conteúdo com reprodução automática, que antes causava problemas.
* **Velocidade**: Melhorias no modo de ocultação e na velocidade com ajustes nas opções de inicialização do navegador.

### 🔧 Correções de erros e melhorias {#v0.4-bug-fixes-improvements}
- **Otimização do parser**: O parser foi otimizado para operações repetidas, melhorando o desempenho.
- **Páginas com erros**: Corrigido um erro que impedia o fechamento do navegador quando as páginas retornavam erros.
- **Corpo vazio**: Tratamento de respostas com corpo vazio.
- **Loop do Playwright**: Resolvido um problema que deixava o loop do Playwright aberto quando a conexão CDP falhava
- **Segurança de tipos**: Corrigidos todos os erros do mypy e adicionadas anotações de tipos nos corpos de funções que não as tinham. Adicionados mypy e pyright ao workflow de CI.

### ⚠️ Mudanças incompatíveis {#v0.4-breaking-changes}

* **Remoção de `css_first`/`xpath_first`**: Use `css('.selector').first`, `css('.selector')[0]` ou `css('.selector').get()` no lugar deles.
* **Todas as seleções agora retornam `Selectors`**: `css('::text')`, `xpath('//text()')`, `css('::attr(href)')` e `xpath('//@href')` agora retornam `Selectors`, que envolve os nós de texto em objetos `Selector` com `tag="#text"`, em vez de `TextHandlers`. Isso torna a API consistente entre todos os métodos de seleção e as anotações de tipos.
* **`Response.body` é sempre `bytes`**: Antes podia ser `str` ou `bytes`; agora sempre retorna `bytes`.
* **Comportamento de `get()`/`getall()`**: Em `Selector`, `get()` retorna `TextHandler` (HTML serializado ou um valor de texto) e `getall()` retorna `TextHandlers`. Aliases: `extract_first = get`, `extract = getall`. O antigo `get_all()` de `Selectors` foi removido.
* **`Selectors.first`/`.last`**: Propriedades de acesso seguras que retornam `Selector | None` em vez de lançar `IndexError`.
* **Constantes internas renomeadas**: `DEFAULT_FLAGS` → `DEFAULT_ARGS`, `DEFAULT_STEALTH_FLAGS` → `STEALTH_ARGS`, `HARMFUL_DEFAULT_ARGS` → `HARMFUL_ARGS`, `DEFAULT_DISABLED_RESOURCES` → `EXTRA_RESOURCES`.

### 🔨 Outras mudanças {#v0.4-other-changes}

* **Mudanças nas dependências**: `tldextract` foi substituído por `tld`, o arquivo interno `_html_utils.py` foi removido em favor de `w3lib.html.replace_entities`, e `typing_extensions` passou a ser obrigatório.
* **Renovação da documentação**: Migração completa do MkDocs para o Zensical, nova seção sobre spiders, atualização de todas as páginas existentes e novas referências da API.

## [v0.3.14](https://github.com/D4Vinci/Scrapling/releases/tag/v0.3.14) - 2026-01-03 {#v0.3.14}

**Uma pequena atualização de manutenção para corrigir problemas que apareceram em alguns dispositivos na v0.3.13**

- O modo anônimo foi desativado em `StealthyFetcher` e suas classes de sessão porque impedia que os cookies fossem mantidos entre páginas no Windows. Isso não acontecia no MacOS nem no Linux (Corrige [#123](https://github.com/D4Vinci/Scrapling/issues/123); obrigado a @frugality4121 por relatar e a @gembleman por indicar a solução).
- A versão mais recente do browserforge foi fixada para resolver o problema com modelos de cabeçalhos antigos para quem já tinha uma versão antiga do browserforge.

## [v0.3.13](https://github.com/D4Vinci/Scrapling/releases/tag/v0.3.13) - 2026-01-01 {#v0.3.13}

**Uma grande atualização com melhorias em muitas partes, mas também com várias mudanças incompatíveis por bons motivos. Leia o texto abaixo antes de atualizar**

* Por vários motivos, decidimos parar completamente de usar o Camoufox a partir de agora. Podemos voltar a usá-lo no futuro se o desenvolvimento continuar. Se você prefere continuar usando o Camoufox como antes desta versão, veja as instruções nesta [seção](https://github.com/D4Vinci/Scrapling/blob/v0.3.13/docs/fetching/stealthy.md#using-camoufox-as-an-engine).

* Antes usávamos patchright no modo de ocultação de `DynamicFetcher` e suas classes de sessão. Agora removemos esse modo dessas classes e começamos a usar patchright em `StealthyFetcher` e suas classes de sessão, com MUITAS melhorias, como você verá, que reforçam o modo de ocultação além do que o patchright já oferece.

**Isso torna `StealthyFetcher` e suas classes de sessão 101% mais rápidos, com menor uso de memória e espaço e cerca de ~400 linhas de código a menos. O mais importante é que estão mais estáveis do que quando usávamos Camoufox.**

Isso também reduz o tempo de instalação do comando `scrapling install` e o tamanho da imagem Docker, melhora a execução dos testes no CI do GitHub e torna o scrapling menos confuso para novos usuários.

### Mudanças incompatíveis {#v0.3.13-breaking-changes}
1. O argumento `stealth` foi removido de `DynamicFetcher` e sua classe de sessão, enquanto `hide_canvas` foi movido para `StealthyFetcher` e suas classes de sessão.
2.  O argumento `disable_webgl` foi movido de `DynamicFetcher` para a classe `StealthyFetcher` e renomeado para `allow_webgl`. O mesmo vale para todas as classes de sessão.
3. A classe `StealthyFetcher` agora é, basicamente, a nova versão com recursos de ocultação de `DynamicFetcher`. Por isso, foram removidos os argumentos `block_images`, `humanize`, `addons`, `os_randomize`, `disable_ads` e `geoip`. Tentei reproduzi-los no Chromium, mas cada um tinha seu próprio problema. Isso pode mudar nas próximas versões antes da v0.4.

Agora, as boas notícias: melhoramos e corrigimos muitas coisas :)

### Melhorias {#v0.3.13-improvements}
- Você já sabe que `StealthyFetcher` e suas classes de sessão estão 101% mais rápidos, mas `DynamicFetcher` e sua classe de sessão também estão 20% mais rápidos.
- O algoritmo de resolução de desafios do Cloudflare foi melhorado para terminar mais rápido e cobrir mais casos. Além disso, graças à reorganização do código, espere que ele resolva os captchas duas vezes mais rápido!
- Todos os fetchers agora usam menos memória.
- O servidor MCP agora usa menos tokens para economizar mais dinheiro!
- A imagem Docker agora é 60% menor.
- Todo o site de documentação foi atualizado com os novos recursos. As explicações também ficaram mais claras, muitas seções foram encurtadas, mais exemplos e argumentos que faltavam foram adicionados, a referência da API ganhou gráficos e várias outras melhorias foram feitas. O site agora carrega 130% mais rápido, usa menos dados e está melhor preparado para SEO.

### Correções {#v0.3.13-fixes}
- Adicionados os argumentos que faltavam nos atalhos do shell de web scraping, que também ficaram mais precisos.
- Corrigido um problema em que `google_search` criava um referer do Google mesmo quando a URL apontava para localhost ou um IP.

## [v0.3.12](https://github.com/D4Vinci/Scrapling/releases/tag/v0.3.12) - 2025-12-18 {#v0.3.12}

### O que mudou {#v0.3.12-what-s-changed}
- Adicionado às classes `DynamicSession`/`AsyncDynamicSession` um argumento chamado `timezone_id`. Ele permite configurar o fuso horário do navegador para corresponder ao do proxy ou VPN que você usa. Assim, os sites não conseguem detectar o proxy pela diferença de fuso horário.
- Melhorada a conversão automática de respostas para JSON.
- A função interna `__create__` foi renomeada para `start` nas classes de sessão dos fetchers, para facilitar seu uso fora do contexto `with`.
- `curl_cffi` e outras dependências foram atualizados para as versões mais recentes.

## [v0.3.11](https://github.com/D4Vinci/Scrapling/releases/tag/v0.3.11) - 2025-12-03 {#v0.3.11}

### O que mudou {#v0.3.11-what-s-changed}
- Melhorada a lógica para lidar com erros de tempo limite ao usar `network_idle` em sites instáveis, como sites com reprodução contínua de mídia.
- Corrigido o preenchimento automático do atalho `stealthy_fetch` no shell de web scraping

## [v0.3.10](https://github.com/D4Vinci/Scrapling/releases/tag/v0.3.10) - 2025-11-26 {#v0.3.10}

**Uma atualização de manutenção com muitas mudanças importantes e possíveis mudanças incompatíveis**

- **Resolvidos** todos os problemas de codificação com uma abordagem melhor, que lida com páginas que não declaram a codificação corretamente (Obrigado a @Kemsty2 pelo esforço de apontar isso em [#110](https://github.com/D4Vinci/Scrapling/issues/110) [#111](https://github.com/D4Vinci/Scrapling/pull/111) )
- **Resolvido** um problema de lógica ao substituir parâmetros da sessão por parâmetros da solicitação em todos os fetchers de navegador, presente desde a v0.3
- **Corrigidas** as assinaturas dos atalhos no shell interativo de web scraping, permitindo o preenchimento automático completo dos atalhos. Esse problema também existia desde a v0.3.
- **Atualizada** a versão do banco de dados Maxmind, o que melhora o argumento `geoip` de `StealthyFetcher` e suas classes de sessão.
- **Atualizados** todos os navegadores usados para as versões mais recentes disponíveis.
- **MUDANÇAS INCOMPATÍVEIS**: Todos os fetchers passaram por uma grande reorganização do código, com algumas mudanças interessantes que podem afetar seu código:
    1. O código do Scrapling agora tem cerca de ~750 linhas a menos e várias mudanças que facilitam muito a manutenção futura e reduzem um pouco o uso de recursos.
    2. A validação de todos os fetchers e suas classes de sessão ficou muito mais rápida, o que melhora a velocidade geral.
    3. Para isso, os fetchers não aceitam mais argumentos posicionais além de `url`. Os demais devem ser passados pelo nome, então seu código deve usar `Fetcher.get('https://google.com', stealthy_headers=True)` e não `Fetcher.get('https://google.com', True)`, caso você fizesse isso por algum motivo!
    4. Desde a v0.3, havia uma diferença incômoda entre os fetchers de navegador e suas classes de sessão: o argumento para passar configurações personalizadas do parser por solicitação era chamado `custom_config`, enquanto nas classes de sessão era `selector_config`. Essa reorganização permitiu unificar o nome como `selector_config` sem quebrar seu código. Agora o nome principal é `selector_config`, com compatibilidade para o antigo argumento `custom_config`. O preenchimento automático estará disponível somente para `selector_config`.
    5. Além disso, para permitir todas essas mudanças, as anotações de tipos das funções dos fetchers passaram a ser geradas dinamicamente. Se o preenchimento automático não funcionar bem na sua IDE, confira se você está usando uma versão recente. Testamos quase todas as IDEs e editores conhecidos.

> Também atualizamos todas as tabelas de desempenho com os números atuais, comparados às versões mais recentes de todas as bibliotecas alternativas.

## [v0.3.9](https://github.com/D4Vinci/Scrapling/releases/tag/v0.3.9) - 2025-11-17 {#v0.3.9}

**Uma nova atualização com muitas mudanças importantes**

### 🚀 Novidades e melhorias de uso {#v0.3.9-new-stuff-and-quality-of-life-changes}
- O argumento `impersonate` de `Fetcher` e `FetcherSession` agora aceita uma lista de navegadores. A biblioteca escolhe um deles aleatoriamente a cada solicitação.

```python
from scrapling.fetchers import FetcherSession

with FetcherSession(impersonate=['chrome', 'firefox', 'safari']) as s:
  s.get('https://github.com/D4Vinci/Scrapling')
```

- Um novo argumento no método `clean` de `TextHandler` permite remover facilmente entidades HTML do texto atual.
- Grandes melhorias na documentação, com explicações mais precisas de várias partes e traduções automáticas do arquivo `README.md` principal.

### 🐛 Correções de erros {#v0.3.9-bug-fixes}
- Corrigido um problema importante ao obter respostas dos fetchers de navegador. Agora há detecção inteligente do tipo de conteúdo para garantir que `response.body` contenha o conteúdo renderizado pelo navegador somente quando ele for HTML. Nos demais casos, contém o conteúdo bruto da última solicitação. Isso permite baixar arquivos binários e de texto sem que eles fiquem envolvidos em tags HTML, mantendo a possibilidade de obter o conteúdo renderizado do site quando você precisar.

### 🔨 Outras mudanças {#v0.3.9-misc}
- O guia de contribuição foi atualizado para ficar mais claro e simples.
- Adicionado um workflow para exigir o uso das ferramentas de qualidade de código, as mesmas usadas como hooks de pre-commit.

## [v0.3.8](https://github.com/D4Vinci/Scrapling/releases/tag/v0.3.8) - 2025-10-27 {#v0.3.8}

**Uma nova atualização com muitas mudanças importantes**

### 🚀 Novidades e melhorias de uso {#v0.3.8-new-stuff-and-quality-of-life-changes}
- Em todos os fetchers de navegador, sites cujas solicitações nunca terminam de carregar não causam mais falhas no código quando você usa `network_idle`.
- A lógica para coletar e verificar o conteúdo das páginas nos fetchers de navegador foi alterada para que os navegadores no Windows sejam tão estáveis quanto no Linux/MacOS. Essa diferença de comportamento ocorre por causa da implementação do Playwright no Windows.
- Toda a lógica de validação foi reorganizada, tornando as solicitações de todos os fetchers de navegador 8-15% mais rápidas
- Adicionada a opção `extra_flags` a `DynamicFetcher` e sua sessão para permitir que você acrescente opções personalizadas do Chrome às opções existentes ao iniciar o navegador.
- Restaurada a lógica anterior de rotas para capturar respostas ao usar `page_action`, que havia mudado na última versão. Isso permite coletar a versão mais recente do conteúdo da página caso `page_action` o altere sem fazer uma solicitação. (Obrigado a @gembleman por apontar isso em [#100](https://github.com/D4Vinci/Scrapling/issues/100) e [#102](https://github.com/D4Vinci/Scrapling/pull/102) )

### 🐛 Correções de erros {#v0.3.8-bug-fixes}
- Corrigido um erro de digitação em `load_dom` no async_fetch de DynamicSession
- Corrigido um problema na resolução de desafios do Cloudflare que causava uma espera sem fim por captchas incorporados que não desaparecem após serem resolvidos. Agora a espera é de 30 segundos; depois disso, o captcha é tratado como um dos que não desaparecem (Corrige #100 )

### 🔨 Outras mudanças {#v0.3.8-misc}
- A imagem Docker agora é publicada automaticamente no Dockerhub e no registro de contêineres do GitHub para facilitar o uso.
- Adicionada uma [nova página de documentação](https://github.com/D4Vinci/Scrapling/blob/v0.3.8/docs/tutorials/external.md) que mostra como usar o navegador Scrapeless com o Scrapling.

## [v0.3.7](https://github.com/D4Vinci/Scrapling/releases/tag/v0.3.7) - 2025-10-12 {#v0.3.7}

**Uma nova atualização com muitas mudanças importantes**

### 🚀 Novidades e melhorias de uso {#v0.3.7-new-stuff-and-quality-of-life-changes}
- O argumento `solve_cloudflare` de `StealthyFetcher` foi reformulado para resolver todos os tipos de implementações personalizadas do Turnstile.
- Todo o código foi reorganizado para passar nas verificações do Pyright, melhorando o uso em todas as IDEs e corrigindo muitos erros.
- A lógica das solicitações foi reorganizada para ficar mais clara e rápida (Também resolve #97 )
- Adicionada a opção `user_data_dir` a todas as classes de sessão de navegador para reutilizar os dados de sessões anteriores, como cookies e armazenamento. Se você não informar essa opção, o Playwright usa um diretório aleatório a cada execução, como fazia antes.
- Adicionada a opção de personalização `additional_args` a `Dynamic fetcher` e sua classe de sessão para passar argumentos extras ao contexto do Playwright, como já era possível com `StealthyFetcher`.
- A lógica de rotas que coleta a última resposta de navegação em todos os navegadores foi melhorada. Isso permite passar as respostas brutas ao parser, em vez de passá-las após o processamento pelo navegador como antes. Isso é muito útil para respostas de texto e JSON.

### 🐛 Correções de erros {#v0.3.7-bug-fixes}
- A nova lógica de rotas resolveu um problema ao obter conteúdo de sites instáveis em alguns dispositivos Windows.
- As reorganizações de código desta versão corrigiram muitos erros difíceis de perceber e problemas estranhos de preenchimento automático em algumas IDEs.
- Várias correções no site de documentação

## [v0.3.6](https://github.com/D4Vinci/Scrapling/releases/tag/v0.3.6) - 2025-10-01 {#v0.3.6}

### 🚀 Novidades {#v0.3.6-new-stuff}
- Melhorado o argumento `solve_cloudflare` de `StealthyFetcher` e suas classes de sessão para resolver todos os tipos de desafios Turnstile e de páginas intermediárias do Cloudflare 🎉
- O servidor MCP agora permite usar `Streamable HTTP` para disponibilizar o servidor facilmente.
- Adicionado suporte a Docker. Uma imagem que inclui todos os navegadores é criada e publicada automaticamente no Docker Hub a cada versão

### 🐛 Correções de erros {#v0.3.6-bug-fixes}
- Corrigido um problema de codificação no parser que ocorria em alguns casos, o conhecido erro `invalid start byte`
- Várias partes da biblioteca foram reorganizadas para corrigir vazamentos de memória. Agora o uso de memória é bem menor, dependendo da sua configuração (Também resolve #92 )
- Melhoradas as anotações de tipos em várias partes do código para facilitar o trabalho na IDE (Também resolve #93 )

## [v0.3.5](https://github.com/D4Vinci/Scrapling/releases/tag/v0.3.5) - 2025-09-20 {#v0.3.5}

**Uma versão necessária que corrige vários problemas**

### 🚀 Novidades {#v0.3.5-new-stuff}
- Todos os fetchers de navegador (`DynamicFetcher`/`StealthyFetcher`/...) e suas classes de sessão agora obtêm páginas 15-20% mais rápido:
    1. O gerenciamento de páginas ficou muito mais rápido graças à melhoria de lógica de @AbdullahY36 em #87
    2. A lógica geral de validação foi otimizada e a criação de páginas em solicitações síncronas foi melhorada. Juntas, essas mudanças trouxeram grandes ganhos de velocidade

- Grandes melhorias no modo de ocultação de `DynamicFetcher` e suas classes de sessão com a troca de `rebrowser-playwright` por `PatchRight`:
    1. Antes desta atualização, `rebrowser-playwright` era desativado quando você ativava `stealth` e `real_chrome`, pois eles não funcionavam bem juntos. Com `PatchRight`, esse problema não existe mais
    2. Agora você pode interagir com Shadow Roots fechados, pois `PatchRight` consegue lidar com eles automaticamente.

### 🐛 Correções de erros {#v0.3.5-bug-fixes}
- Corrigido um erro ao usar o método `re` da classe `Selectors`.
- Corrigido um erro nos comandos `uncurl` e `curl2fetcher` do shell de web scraping que fazia a opção `--data-raw` do curl ser interpretada incorretamente.
- Corrigido um erro no comando `view` do shell de web scraping que ocorria dependendo da codificação do site.
- Corrigido um erro na conversão de conteúdo que afetava o modo `mcp` e os comandos `extract`.

### Novos colaboradores {#v0.3.5-new-contributors}
- @AbdullahY36 fez sua primeira contribuição em #87

## [v0.3.4](https://github.com/D4Vinci/Scrapling/releases/tag/v0.3.4) - 2025-09-16 {#v0.3.4}

**Uma versão necessária que corrige vários problemas**

### 🚀 Novidades {#v0.3.4-new-stuff}
- Todas as classes de sessão dos fetchers foram adicionadas ao shell interativo para uso imediato, sem importação.

### 🐛 Correções de erros {#v0.3.4-bug-fixes}
- Adicionada uma solução alternativa para um erro da API do Playwright no Windows ao obter conteúdo durante a resolução de desafios do Cloudflare.
- Corrigido um problema de codificação no comando `view` do shell interativo
- Corrigido um erro no argumento `max_pages` de `AsyncStealthySession` que causava falhas no código.
- Corrigido um problema das últimas atualizações que fazia as propriedades `html_content` e `prettify` de `Selector` retornarem bytes, dependendo da codificação. Ambas voltaram a retornar strings.

## [v0.3.3](https://github.com/D4Vinci/Scrapling/releases/tag/v0.3.3) - 2025-09-15 {#v0.3.3}

- Removida a lógica que fechava a aba padrão do navegador nos fetchers de navegador, porque causava uma falha. Isso não acontecia no Mac; só foi possível reproduzir no Windows e no Linux

## [v0.3.2](https://github.com/D4Vinci/Scrapling/releases/tag/v0.3.2) - 2025-09-15 {#v0.3.2}

Notas da versão v0.3.2

### 🚀 Novidades {#v0.3.2-new-stuff}

- **Dependências opcionais dos fetchers**: Todos os fetchers agora fazem parte de grupos de dependências opcionais, reduzindo o tamanho do pacote base. O módulo base `scrapling` contém apenas o parser. Para usar os fetchers ou as opções de linha de comando, execute `pip install "scrapling[fetchers]"`. Veja as instruções detalhadas de instalação [aqui](index.md#installation)
- **Configuração por página nas sessões**: As classes de sessão dos fetchers de navegador agora permitem configurar cada página separadamente. Todos os parâmetros das solicitações são validados como os das sessões. Mais detalhes no site de documentação [aqui](fetching/stealthy.md#full-list-of-arguments)
    <br>Exemplo:

    ```python
    with StealthySession(headless=True, solve_cloudflare=True) as session:
        page = session.fetch('https://nopecha.com/demo/cloudflare', google_search=False)
    ```

- **Melhorias nos fetchers de navegador**
    - Uma nova opção permite controlar se o navegador deve esperar a execução de JavaScript terminar nas páginas. Ela está ativada por padrão, como antes

        ```python
        with DynamicSession(headless=True, disable_resources=False, network_idle=True) as session:
           page = session.fetch('https://quotes.toscrape.com/', load_dom=False)
        ```

    - O modo de ocultação agora é mais confiável em `DynamicFetcher` e suas classes de sessão.
    - `DynamicFetcher` e `StealthyFetcher` agora usam menos recursos, ao encontrar e fechar automaticamente a aba padrão aberta pelos contextos persistentes da API do Playwright
    - Corrigido um erro importante de lógica na rotação de páginas dos fetchers de navegador. As páginas anteriores agora são substituídas por novas, pois as abas reutilizadas podiam manter configurações de usos anteriores
    - `StealthyFetcher` e suas classes de sessão agora estão um pouco mais rápidos (5%)

- **Melhorias na propriedade `.body`**: Agora retorna o conteúdo recebido como está, sem processamento. Isso permite baixar arquivos e lidar com solicitações que não retornam HTML. O exemplo abaixo mostra como baixar uma imagem:

    ```python
    from scrapling.fetchers import Fetcher

    page = Fetcher.get('https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/poster.png')
    with open(file='poster.png', mode='wb') as f:
        f.write(page.body)
    ```

### 🐛 Correções de erros {#v0.3.2-bug-fixes}

- **Problemas de codificação resolvidos**: Corrigidos vários problemas de codificação com alguns sites no parser, no modo mcp e nos comandos extract (Também resolve #80 e #81)
- **Análise mais rápida**: Graças a várias mudanças em diferentes partes, a biblioteca agora está mais rápida, como mostram os benchmarks atualizados

### 🔨 Outras mudanças {#v0.3.2-misc}

- **Benchmarks atualizados**: As medições foram atualizadas para comparar as melhorias atuais de velocidade com as versões mais recentes de bibliotecas semelhantes
- **Grande parte do código foi reorganizada e o código sem uso foi substituído por implementações melhores**: Menos código, mais claro e mais fácil de manter
- **Novo vídeo do YouTube**: Adicionado conteúdo em vídeo à documentação do MCP.
- **Novo modelo de issue**: Um modelo simples para quem não consegue usar os modelos atuais.
- **Otimização do workflow de CI**: O workflow de testes agora ignora execuções quando apenas a documentação ou outros arquivos sem código são alterados.
- **Dependências atualizadas**: Várias dependências foram atualizadas para as versões mais recentes.
- **Melhorias no estilo do código**: Novas regras do ruff foram aplicadas em todos os arquivos.
- **Hooks de pre-commit**: Atualizada a configuração do pre-commit.

### 🎯 Mudanças incompatíveis {#v0.3.2-breaking-changes}

- Removido o parâmetro `max_pages` da versão síncrona de `StealthySession` para corresponder a `DynamicSession`, pois ele não faz sentido na versão síncrona

## [v0.3.1](https://github.com/D4Vinci/Scrapling/releases/tag/v0.3.1) - 2025-09-02 {#v0.3.1}

1. Corrigido um problema ao instalar scrapling sem o extra `shell` (#76 )
2. Adicionado um argumento a todos os fetchers de navegador e suas classes de sessão para passar um arquivo JS que é executado na criação da página (#56) :

```python
from scrapling.fetchers import StealthyFetcher

StealthyFetcher.fetch('https://example.com', init_script="/absolute/path/to/js/script.js")
```

## [v0.3](https://github.com/D4Vinci/Scrapling/releases/tag/v0.3) - 2025-09-01 {#v0.3}

🎉 **Versão principal - Renovação completa da arquitetura**

O Scrapling v0.3 é a maior atualização da história do projeto. Inclui uma reescrita completa da arquitetura, grandes melhorias de desempenho e novos recursos poderosos, como integração com IA e um shell interativo de web scraping.

Esta versão inclui várias mudanças incompatíveis. Leia as notas da versão com atenção.

### 🚀 Principais novidades {#v0.3-major-new-features}

#### Arquitetura baseada em sessões {#v0.3-session-based-architecture}
- **Novas classes de sessão**: Reescrita completa que adiciona suporte a sessões persistentes
    - `FetcherSession` - Solicitações HTTP com gerenciamento de estado persistente, tanto para código síncrono quanto assíncrono
    - `DynamicSession`/`AsyncDynamicSession` - Automação do navegador, que fica aberto até você terminar
    - `StealthySession`/`AsyncStealthySession` - Navegação com ocultação da automação, mantendo o navegador aberto até você terminar
- **Gerenciamento assíncrono de abas do navegador**: Novo grupo de abas pelo argumento `max_pages`, que alterna entre elas para fazer solicitações simultâneas com o navegador
- **Sessões simultâneas**: Execute várias sessões isoladas ao mesmo tempo

Consulte a seção `Fetching` do site para mais detalhes.

#### Muitos recursos novos para ocultar a automação e contornar sistemas antibot {#v0.3-a-lot-of-new-stealth-anti-bot-capabilities}
- **🤖 Resolução de desafios do Cloudflare**: [Resolução automática de desafios do Cloudflare Turnstile](fetching/stealthy.md#cloudflare-and-stealth-options) no `StealthyFetcher` e em suas classes de sessão
- **Simulação de impressões digitais do navegador**: Simule impressões digitais TLS de navegadores reais, use cabeçalhos compatíveis com a versão do navegador e aproveite o suporte a HTTP/3 e outros recursos da nova classe [Fetcher](fetching/static.md)
- **Modo de ocultação melhorado**: O modo de ocultação do `DynamicFetcher` e de suas classes de sessão agora é mais robusto e confiável (também conhecido como `PlayWrightFetcher`)

#### Integração com IA e servidor MCP {#v0.3-ai-integration-mcp-server}
- **Servidor MCP integrado**: Servidor Model Context Protocol para web scraping com ajuda de IA
- **6 ferramentas poderosas**: `get`, `bulk_get`, `fetch`, `bulk_fetch`, `stealthy_fetch`, `bulk_stealthy_fetch`
- **Extração inteligente de conteúdo**: Converta páginas ou elementos da web para Markdown ou HTML, ou extraia uma versão limpa do texto
- **Suporte a seletores CSS**: Use o motor do Scrapling para selecionar elementos específicos com precisão antes de enviar o conteúdo à IA
- **Contorno de sistemas antibot**: Lide com Cloudflare Turnstile e outras proteções
- **Suporte a proxies**: Use proxies para manter o anonimato e escolher a localização geográfica
- **Simulação de navegadores**: Simule navegadores reais com impressões digitais TLS, cabeçalhos reais compatíveis com a versão e mais
- **Processamento em paralelo**: Extraia dados de várias URLs ao mesmo tempo para ganhar eficiência
- [e mais...](ai/mcp-server.md)

#### Novo shell interativo de web scraping {#v0.3-new-interactive-web-scraping-shell}
- **Novo shell**: Shell IPython personalizado com vários atalhos inteligentes integrados, como `get`, `post`, `put`, `delete`, `fetch` e `stealthy_fetch`
- **Gerenciamento inteligente de páginas**: Novos comandos `page` e `pages` para guardar automaticamente a página atual e o histórico de todas as solicitações feitas pelo shell
- **Integração com Curl**: Use as funções `uncurl` e `curl2fetcher` para converter comandos curl das ferramentas de desenvolvedor do navegador em solicitações do `Fetcher`
- [e mais...](cli/interactive-shell.md)

#### Extraia dados pelo terminal sem programar {#v0.3-scrape-from-the-terminal-without-programming}
- **Novos comandos de extração**: Extraia dados pelo terminal sem programar
    - `scrapling extract get/post/put/delete` - Solicitações HTTP simples
    - `scrapling extract fetch` - Extração de conteúdo dinâmico
    - `scrapling extract stealthy-fetch` - Contorno de sistemas antibot
- **Baixa páginas da web** e salva seu conteúdo em arquivos.
- **Converte HTML para formatos legíveis**, como Markdown, mantém o conteúdo em HTML ou extrai apenas o texto da página.
- **Aceita seletores CSS personalizados** para extrair partes específicas da página.
- **Lida com solicitações HTTP e obtenção de páginas por navegadores.**
- **Muitas opções de personalização**, com cabeçalhos, cookies, proxies e outras configurações. Quase todas as opções disponíveis no código também estão disponíveis pelo terminal.
- [e mais...](cli/extract-commands.md)

### 🔧 Melhorias técnicas {#v0.3-technical-improvements}

#### Melhorias de desempenho {#v0.3-performance-enhancements}
- **Fetcher agora é 4 vezes mais rápido** - Sim, você leu certo!
- **DynamicFetcher agora é ~60% mais rápido** - Uma versão muito mais rápida conforme a sua configuração (principalmente o modo de ocultação)
- **StealthyFetcher agora é 20–30% mais rápido** - Graças à nova estrutura e ao uso da nossa implementação em vez da interface Python do `Camoufox`
- **Ganho combinado de velocidade de 50%+** nos principais métodos de seleção (`find_by_text`, `find_similar`, `find_by_regex`, `relocate` etc.) 🚀
- **Aumento de ~10% na velocidade dos métodos que obtêm a primeira correspondência CSS/XPath** - `css_first` e `xpath_first` agora são mais rápidos que `css` e `xpath`
- **O método `get_all_text()` está 40% mais rápido** na extração de conteúdo
- **Melhoria de velocidade de 20%** ao reencontrar elementos de forma adaptativa
- **Otimização das propriedades de navegação** - Propriedades como `next`, `previous`, `below_elements` e outras agora são bem mais rápidas
- **Limpeza de texto 5 vezes mais rápida**
- **Melhor uso de memória** com importações otimizadas e menos trabalho adicional
- **⚡ Importações muito rápidas**: Menor tempo de inicialização com o carregamento otimizado de módulos
- **Melhores resultados nos testes de desempenho**: Todas as melhorias de velocidade tornam o Scrapling muito mais rápido que antes em comparação com outras bibliotecas (1775 vezes mais rápido que BeautifulSoup e 5.1 vezes mais rápido que AutoScraper; veja os [testes de desempenho](benchmarks.md))

#### Arquitetura, qualidade do código e melhorias de uso {#v0.3-architecture-code-quality-and-quality-of-life}
- **Contexto persistente**: Todos os fetchers baseados em navegador agora usam um contexto persistente por padrão. (Também resolve #64)
- **Uso de msgspec para validar rapidamente a configuração de todos os fetchers baseados em navegador** antes de executar as solicitações, o que facilita encontrar erros.
- **Todos os cookies** retornados pelos fetchers agora têm o formato aceito pelo mesmo fetcher. Assim, você pode obter cookies e passá-los novamente a todos os fetchers e suas classes de sessão.
- **Verificação e formatação de código mais rápidas** após a migração para `ruff`
- **Sistema de build moderno**: Migração de setup.py para pyproject.toml 📦
- **Melhores ações e fluxos de trabalho do GitHub** para facilitar o desenvolvimento e os testes
- **🎨 Melhores anotações de tipos**: Cobertura completa de tipos com padrões modernos do Python para melhorar o suporte da IDE e a confiabilidade
- **Código mais limpo**: Remoção de código sem uso e otimização das funções principais 🧹
- **🚀 Compatibilidade com versões anteriores**: Novos atalhos para manter a compatibilidade com código antigo

### Mudanças incompatíveis {#v0.3-breaking-changes}

#### Versão mínima do Python {#v0.3-minimum-python-version}
- **Requer Python 3.10+**: Fim do suporte ao Python 3.9 e versões anteriores

#### Nomes de classes e métodos {#v0.3-class-and-method-naming}
Essas mudanças de nomes buscam dar mais clareza e consistência, principalmente para novos usuários.

- **`Adaptor` → `Selector`**: A classe principal de análise foi renomeada (ainda pode ser importada como `Adaptor` para manter a compatibilidade)
- **`Adaptors` → `Selectors`**: A classe de coleção foi renomeada (ainda pode ser importada como `Adaptors` para manter a compatibilidade)
- **`auto_match` → `adaptive`**: O parâmetro foi renomeado em todos os métodos
- **`adaptor_arguments` → `selector_config`**: O parâmetro de configuração foi renomeado
- **`automatch_domain` → `adaptive_domain`**: O parâmetro de domínio foi renomeado
- **`additional_arguments` → `additional_args`**: O nome do parâmetro foi encurtado
- **⚠️ `text/body` → `content`**: O parâmetro do construtor de Selector agora aceita tanto `str` quanto `bytes`
- **`PlayWrightFetcher` → `DynamicFetcher`**: A classe de automação do navegador foi renomeada (ainda pode ser importada como `PlayWrightFetcher` para manter a compatibilidade)
- **DynamicFetcher não inclui mais a lógica nem os argumentos do NSTBrowser**, pois não faz mais sentido mantê-los.
- **O argumento headless do StealthyFetcher não aceita mais 'virtual'** porque agora só usamos a biblioteca Camoufox para obter o caminho de instalação do navegador e as demais opções de inicialização

### 🐛 Correções de erros {#v0.3-bug-fixes}

- Corrigida a contagem de filhos aninhados em tags ignoradas por `get_all_text` (#61)
- Corrigido o problema de instalação causado por espaços no caminho do executável do Python (#57)
- Resolvidos problemas de threads no armazenamento, com tratamento da recursão quando o recurso adaptativo está ativado
- Corrigidos problemas de prioridade de argumentos com o padrão Sentinel em `FetcherSession`
- Corrigido o tratamento dos tipos de proxy em `StealthyFetcher`
- Corrigidos conflitos entre os argumentos `referer` e `google_search`
- Corrigidos problemas na injeção assíncrona de scripts de ocultação

## [v0.2.99](https://github.com/D4Vinci/Scrapling/releases/tag/v0.2.99) - 2025-04-08 {#v0.2.99}

**Esta é uma atualização importante para que todos aproveitem o Scrapling por completo, como ele foi pensado.**

### O que mudou {#v0.2.99-what-s-changed}
#### Novo site com toda a documentação {#v0.2.99-new-full-documentation-website}
- Sim, finalmente 😄 Confira [aqui](index.md)
#### Importação unificada dos fetchers {#v0.2.99-unified-import-logic-for-fetchers}
- Agora você pode importar todos os fetchers com `from scrapling.fetchers import Fetcher, AsyncFetcher, StealthyFetcher, PlayWrightFetcher` e usá-los diretamente, como em `page = Fetcher.get(...)`, sem criar uma instância.<br/> Isso substitui a importação antiga `from scrapling.defaults import Fetcher, AsyncFetcher, StealthyFetcher, PlayWrightFetcher`.
#### Mudança incompatível: automatch agora está desativado por padrão {#v0.2.99-breaking-change-automatch-is-now-turned-off-by-default}
- Agora existe uma nova forma de ativar automatch pelos fetchers ou pelas outras opções de análise. Veja a [documentação](fetching/choosing.md#parser-configuration-in-all-fetchers) para mais detalhes.
>  As importações e a lógica antigas continuam disponíveis, com um aviso, para manter a compatibilidade.
#### Novas opções para os fetchers {#v0.2.99-new-options-added-to-fetchers}
- Agora `StealthyFetcher` e `PlayWrightFetcher` têm um novo argumento chamado `wait` ao obter páginas. Ele faz o fetcher esperar um tempo definido em milissegundos antes de fechar a página e retornar a resposta.
- Os métodos de `StealthyFetcher` chamados `fetch` e `async_fetch` agora têm o argumento `additional_arguments` para passar configurações extras ao Camoufox. Elas têm prioridade sobre as configurações do Scrapling (#54 )
#### Correções de erros {#v0.2.99-bugs-squashed}
- Corrigido um erro ao detectar redirecionamentos em `async_fetch` nas classes `StealthyFetcher` e `PlayWrightFetcher`.

**_Obrigado por todo o apoio e pelas doações!_**

## [v0.2.98](https://github.com/D4Vinci/Scrapling/releases/tag/v0.2.98) - 2025-03-17 {#v0.2.98}

**Esta é uma atualização importante para que todos aproveitem o Scrapling por completo, como ele foi pensado**

### O que mudou {#v0.2.98-what-s-changed}
#### Melhorias no uso de memória e na velocidade {#v0.2.98-various-memory-usage-and-speed-optimizations}
- O uso de memória de todos os métodos de seleção agora é ~40% do uso anterior, com um pequeno aumento de velocidade.
- Aplicado carregamento sob demanda a todos os submódulos da biblioteca: agora só é carregado o que você usa. Por exemplo:
Antes da atualização, a importação `from scrapling import Adaptor` usava `30-40mb` de RAM porque também carregava todos os fetchers e outros componentes. Agora usa `~1.2mb`.
- A última atualização fez a biblioteca usar ~32% da memória que usava antes com um grupo grande de solicitações. Agora ajustamos ainda mais o cache para usar menos memória.
- Pequeno aumento geral de velocidade do analisador, de 2-5%

**_Obrigado por todo o apoio e pelas doações!_**

## [v0.2.97](https://github.com/D4Vinci/Scrapling/releases/tag/v0.2.97) - 2025-03-15 {#v0.2.97}

**Esta é uma atualização importante para que todos aproveitem o Scrapling por completo, como ele foi pensado**

### O que mudou {#v0.2.97-what-s-changed}
#### Menor uso de memória e um pequeno aumento de velocidade em todos os fetchers {#v0.2.97-lower-memory-usage-and-small-speed-increase-across-all-fetchers}
- Os novos limites de tamanho do cache em toda a biblioteca reduzem bastante o uso de memória ao fazer muitas solicitações ou operações.
- Reorganizadas grandes partes dos fetchers para facilitar a manutenção e aumentar um pouco a velocidade.

#### Correções de erros {#v0.2.97-bugs-fixed}
- Corrigido um erro de `TextHandler` que convertia um valor não textual em uma string vazia quando ele era importado sozinho. Agora qualquer valor passado a `TextHandler` é convertido primeiro em string e depois em `TextHandler`. Isso vale para todos os valores: afinal, como o nome indica, `TextHandler` foi feito para trabalhar apenas com texto! (#45 )
- Corrigido um erro que fazia a maioria dos métodos de AsyncFetcher ignorar o argumento `retries`.

#### Outras mudanças {#v0.2.97-miscellaneous}
- Atualizadas as anotações de tipos da maioria dos argumentos em todos os fetchers para ficarem mais claras e precisas.

**_Obrigado por todo o apoio e pelas doações!_**

## [v0.2.96](https://github.com/D4Vinci/Scrapling/releases/tag/v0.2.96) - 2025-03-05 {#v0.2.96}

**Esta é uma atualização importante para que todos aproveitem o Scrapling por completo, como ele foi pensado**

### O que mudou {#v0.2.96-what-s-changed}
1. Adicionada a opção `-f` a `scrapling install` para forçar a reinstalação das dependências do navegador. Recomendo executar `scrapling install -f` agora para aproveitar o grande aumento de velocidade do `StealthyFetcher` com a nova versão do navegador Camoufox :)
2. Corrigido um erro de `TextHandler` que retornava `TextHandlers` em vez de `TextHandler` ao obter uma fatia do texto, e corrigida a anotação de tipo desse retorno (#41 )
3. Corrigido um problema que fazia `scrapling install` abrir um shell Python em alguns casos!

## [v0.2.95](https://github.com/D4Vinci/Scrapling/releases/tag/v0.2.95) - 2025-02-25 {#v0.2.95}

**Esta é uma atualização importante para que todos aproveitem o Scrapling por completo, como ele foi pensado**

### O que mudou {#v0.2.95-what-s-changed}
1. Corrigido um erro de `Fetcher` que fazia os cabeçalhos gerados pelo argumento `stealthy_headers` substituírem alguns cabeçalhos do usuário, como `Accept` (#39 )
2. Melhorada um pouco a lógica de geração de cabeçalhos, o que deve aumentar ligeiramente a velocidade.

## [v0.2.94](https://github.com/D4Vinci/Scrapling/releases/tag/v0.2.94) - 2025-02-22 {#v0.2.94}

**Esta é uma atualização importante para que todos aproveitem o Scrapling por completo, como ele foi pensado**

### O que mudou {#v0.2.94-what-s-changed}
1. Adicionada a propriedade `history` a todos os fetchers para mostrar os redirecionamentos (#32 )
2. Corrigida a lógica do argumento `case_sensitive` em todos os métodos `re`/`re_first`. Se você usava essa opção, os resultados do seu código podem mudar (mas talvez você mereça, já que percebeu que ela não funcionava direito e não abriu uma issue, hahaha)
3. Atualizadas as dependências e reativado `coop` no motor Camoufox (StealthyFetcher).

## [v0.2.93](https://github.com/D4Vinci/Scrapling/releases/tag/v0.2.93) - 2025-01-31 {#v0.2.93}

**Esta é uma atualização importante para que todos aproveitem o Scrapling por completo, como ele foi pensado**

### O que mudou {#v0.2.93-what-s-changed}
1. O tipo de retorno agora é consistente em todo o motor de análise. Você sempre recebe um destes tipos: `Adaptor`, `Adaptors`, `TextHandler`, `TextHandlers`, `None`, ou uma lista quando há resultados mistos, como com um seletor CSS combinado. Isso facilita a programação com menos verificações manuais de tipos, torna a biblioteca mais estável e permite encadear métodos em todos os casos.
2. Reorganizada a maior parte do motor de análise, principalmente a classe `Adaptor`, para deixá-lo mais limpo e, acima de tudo, mais rápido. Quase todos os métodos e propriedades, principalmente os de busca, ganharam entre 5-40% de velocidade. Alguns melhoraram ainda mais, como `find_by_regex`, que ganhou ~60%! O recurso automatch ganhou cerca de ~5%.
3. Corrigidos erros na lógica de `find_all`/`find` que aplicavam os filtros com OR em alguns casos e com AND em outros. Agora todos os elementos retornados precisam atender a todos os filtros que você passar.
4. Todos os métodos ligados a regex agora retornam `TextHandler`/`TextHandlers` para facilitar o encadeamento de métodos.
5. **Adicionada uma nova** propriedade `below_elements`, que retorna um objeto `Adaptors` com todos os elementos abaixo do elemento atual na árvore DOM.
6. Todos os métodos e propriedades que retornavam código HTML como string agora retornam `TextHandler`, para facilitar o uso de regex e outras operações...
7. StealthyFetcher agora é um pouco mais rápido e oculta melhor a automação. Também é possível clicar em CAPTCHAs dentro de iframes, como o **Cloudflare Turnstile**.
8. O preenchimento automático e as anotações de tipos melhoraram bastante em quase metade da biblioteca, principalmente em `Adaptor`, `TextHandler` e `TextHandlers`.
9. Ao obter uma fatia de `TextHandler`, acessar por índice ou usar o método `split`, você agora recebe outro `TextHandler` em vez de uma string padrão do Python. Quase todas as operações e métodos padrão de strings retornam outro `Texthandler` para que você sempre possa encadear métodos e funções.
10. Corrigidos alguns erros pequenos e de digitação. Por exemplo, async_put de Fetcher fazia uma solicitação post em vez de put 😶‍🌫️
11. Melhorado um pouco o README enquanto termino o site da documentação.

Era para ser uma pequena atualização antes da versão 0.3, mas decidi melhorá-la um pouco mais.

## [v0.2.92](https://github.com/D4Vinci/Scrapling/releases/tag/v0.2.92) - 2024-12-26 {#v0.2.92}

### O que mudou {#v0.2.92-what-s-changed}
- As respostas dos fetchers baseados em navegador agora usam fontes de dados mais confiáveis quando a página carregada contém muitos iframes.
- **Instalar `Scrapling` ficou ainda mais fácil: instale com pip, execute `scrapling install` no terminal e pronto!**
- Corrigida uma anotação de tipo imprecisa no analisador.

## [v0.2.91](https://github.com/D4Vinci/Scrapling/releases/tag/v0.2.91) - 2024-12-19 {#v0.2.91}

### O que mudou {#v0.2.91-what-s-changed}
- Corrigido um erro que fazia a mensagem de log da obtenção de páginas aparecer só na primeira solicitação.
- Por padrão, a API do Playwright retorna a primeira resposta que atende ao estado de carregamento passado ao método `goto`: `["load", "domcontentloaded", "networkidle"]`. Se um site tiver uma página de espera, como a do Cloudflare, que depois redireciona para o site real, o Playwright retorna o primeiro código de status, que pode ser 403. Esta atualização resolve o problema em `PlaywrightFetcher` e `StealthyFetcher`, já que ambos usam a API do Playwright. O resultado não depende mais desse comportamento padrão.
- Adicionado suporte a proxies SOCKS na classe `Fetcher`.
- Corrigida a anotação de tipo do argumento `wait_selector_state` para que o preenchimento automático mostre os valores corretos que você pode usar.

## [v0.2.9](https://github.com/D4Vinci/Scrapling/releases/tag/v0.2.9) - 2024-12-16 {#v0.2.9}

### O que mudou {#v0.2.9-what-s-changed}
##### Novos recursos {#v0.2.9-new-features}
1. Chegou o **tão esperado** suporte assíncrono ao Scrapling! Agora você tem `AsyncFetcher`, a versão assíncrona de `Fetcher`, e tanto `StealthyFetcher` quanto `PlayWrightFetcher` têm um novo método chamado `async_fetch` com as mesmas opções.

```python
>> from scrapling import StealthyFetcher
>> page = await StealthyFetcher().async_fetch('https://www.browserscan.net/bot-detection')  # the async version of fetch
>> page.status == 200
True
```

2. A classe `StealthyFetcher` agora tem o argumento `geoip` nos métodos de obtenção de páginas. Quando ativado, usa automaticamente a longitude, latitude, fuso horário, país e configuração regional do IP, e altera o endereço IP exposto pelo WebRTC. Também calcula e simula o idioma do navegador conforme a distribuição dos falantes de cada idioma na região de destino.
3. Adicionado o argumento `retries` às classes `Fetcher`/`AsyncFetcher`, para você definir o número de novas tentativas de cada solicitação feita por `httpx`.
4. Adicionado o método `url_join` a `Adaptor` e aos fetchers. Ele recebe uma URL relativa e a combina com a URL atual para gerar uma URL absoluta completa!
5. Adicionado o método `keep_cdata` a `Adaptor` e aos fetchers para impedir que o analisador remova cdata quando você precisar mantê-lo.
6. Em `Adaptor`/`Response`, o método `body` agora retorna a resposta HTML original quando possível, sem processá-la na biblioteca.
7. Adicionado registro de logs à classe `Response`. Ao usar os fetchers, você agora recebe um log com informações sobre a resposta.
Exemplo:

   ```python
   >> from scrapling.defaults import Fetcher
   >> Fetcher.get('https://books.toscrape.com/index.html')
   [2024-12-16 13:33:36] INFO: Fetched (200) <GET https://books.toscrape.com/index.html> (referer: https://www.google.com/search?q=toscrape)
   >>
   ```

8. Ao usar métodos padrão de strings em um `TextHandler`, como `.replace()`, você agora recebe outro `TextHandler`. Antes eles retornavam uma string padrão.
9. Grandes melhorias de velocidade em toda a biblioteca e melhorias na ocultação da automação nas classes de fetchers em geral.
10. Adicionadas funções de compatibilidade como `extract_first`\`extract`, que retornam o mesmo resultado que o objeto original. Elas existem apenas para facilitar a cópia de código do Scrapy/Parsel para o Scrapling quando necessário, pois são usadas nessas bibliotecas!
11. As solicitações em lote agora são muito mais rápidas graças à reorganização de boa parte do código e ao uso de cache nos lugares certos.

##### Mudanças incompatíveis {#v0.2.9-breaking-changes}
- Removido o suporte ao Python 3.8. (Principalmente porque o Playwright deixou de dar suporte a ele, mas essa versão já era problemática)
- O argumento `debug` foi removido de toda a biblioteca. Para ativar a depuração, faça isto depois de importá-la:

   ```python
   >>> import logging
   >>> logging.getLogger("scrapling").setLevel(logging.DEBUG)
   ```

##### Correções de erros {#v0.2.9-bugs-squashed}
1. WebGL agora está ativado por padrão porque muitas proteções verificam se ele está habilitado.
2. Corrigidos alguns erros e erros de digitação na documentação e no README.

##### Melhorias de uso {#v0.2.9-quality-of-life-changes}
1. Todos os logs agora usam o logger chamado `scrapling` para facilitar o controle. Antes usávamos o logger raiz.
2. Reorganizada a pasta de testes para ficar mais clara e adicionados testes dos novos recursos. Todos os testes foram reescritos de forma mais limpa e novos testes foram adicionados para aumentar a cobertura.
3. Reorganizada boa parte do código para deixá-lo mais limpo e fácil de manter.

> Todas essas mudanças estavam previstas para a versão 0.3, mas decidi incluí-las aqui porque ainda vai levar um tempo até a próxima versão. O próximo passo é terminar o site da documentação detalhada e depois trabalhar na versão 0.3

## [v0.2.8](https://github.com/D4Vinci/Scrapling/releases/tag/v0.2.8) - 2024-11-30 {#v0.2.8}

### O que mudou {#v0.2.8-what-s-changed}
- Pequena atualização com melhorias de uso necessárias no código e a correção de um erro de digitação no README principal (#20)

## [v0.2.7](https://github.com/D4Vinci/Scrapling/releases/tag/v0.2.7) - 2024-11-26 {#v0.2.7}

### O que mudou {#v0.2.7-what-s-changed}
##### Novos recursos {#v0.2.7-new-features}
- Se você usar o argumento `wait_selector` com as classes `StealthyFetcher` e `PlayWrightFetcher`, o Scrapling espera novamente que o JS seja carregado e executado por completo, como de costume. Se usar `network_idle`, ele também espera esse estado novamente depois. Se todos os estados já tiverem sido atendidos, não há espera.
- Agora você pode ativar e desativar anúncios em `StealthyFetcher` com o argumento `disable_ads`. O bloqueio está ativado por padrão e instala a extensão `ublock origin`.
- Agora você pode definir a configuração regional usada por `PlayWrightFetcher` com o argumento `locale`. O valor padrão continua sendo `en-US`.
- As solicitações básicas feitas por `Fetcher` agora aceitam proxies no formato `http://username:password@localhost:8030`.
- Melhorado um pouco o modo de ocultação de `PlayWrightFetcher`.

##### Correções de erros e melhorias {#v0.2.7-bugs-squashed-improvements}
1. Ativar proxies na classe `PlayWrightFetcher` não depende mais de o modo `stealth` estar ativado ou desativado (obrigado a [@AbdullahY36](https://github.com/AbdullahY36) pelo aviso)
2. Agora `ResponseEncoding` verifica se a codificação retornada na resposta pode ser usada com a página. Se ela causar um erro, o Scrapling usa `utf-8` por padrão

## [v0.2.6](https://github.com/D4Vinci/Scrapling/releases/tag/v0.2.6) - 2024-11-24 {#v0.2.6}

### O que mudou {#v0.2.6-what-s-changed}
##### Novos recursos {#v0.2.6-new-features}
- Agora `PlayWrightFetcher` pode usar o navegador real diretamente se você passar `real_chrome` à função `PlayWrightFetcher.fetch`, mas é necessário ter o Chrome instalado. O Scrapling abre uma instância do seu Chrome e você pode usar a maioria das opções normalmente. (Antes só havia o argumento `cdp_url` para fazer isso)
- Atualizada a versão indicada nos cabeçalhos gerados para navegadores reais.

##### Correções de erros {#v0.2.6-bugs-squashed}
1. O formato dos cabeçalhos de navegador gerados por `BrowserForge` estava desatualizado, o que fazia algumas proteções detectarem o Scrapling. Agora `BrowserForge` só é usado para gerar um useragent real.
2. O argumento `hide_canvas` agora está desativado por padrão porque o ReCaptcha do Google o detecta.

## [v0.2.5](https://github.com/D4Vinci/Scrapling/releases/tag/v0.2.5) - 2024-11-23 {#v0.2.5}

### O que mudou {#v0.2.5-what-s-changed}

##### Correções de erros {#v0.2.5-bugs-squashed}
- Tratado um erro do argumento 'wait_selector' quando ele encontra mais de 1 elemento. Isso afeta as classes `StealthyFetcher` e `PlayWrightFetcher`.
- Corrigido o tipo de codificação quando o cabeçalho `content_type` recebe valores com parâmetros como `charset` (obrigado a @andyfcx por [#12](https://github.com/D4Vinci/Scrapling/issues/12) )

##### Melhorias de uso {#v0.2.5-quality-of-life}
- Adicionados testes para cobrir novas partes do código, e os testes passaram a rodar em threads.
- Atualizei os docstrings para que sejam exibidos corretamente no apidoc do Sphinx e em ferramentas semelhantes.

##### Novos colaboradores {#v0.2.5-new-contributors}
- @andyfcx fez sua primeira contribuição em [#13 ](https://github.com/D4Vinci/Scrapling/pull/13)

## [v0.2.4](https://github.com/D4Vinci/Scrapling/releases/tag/v0.2.4) - 2024-11-20 {#v0.2.4}

### O que mudou {#v0.2.4-what-s-changed}

##### Correções de erros {#v0.2.4-bugs-squashed}
- Corrigido um erro ao obter os bytes da resposta depois de usar `network_idle` nas classes `StealthyFetcher` e `PlayWrightFetcher`. <br/> Isso causava a seguinte mensagem de erro:

    ```
    Response.body: Protocol error (Network.getResponseBody): No resource with given identifier found
    ```

- A API do PlayWright às vezes retorna respostas com o texto de status vazio. Agora o `Scrapling` calcula esse texto por conta própria se isso acontecer. Isso afeta as classes `StealthyFetcher` e `PlayWrightFetcher`.

## [v0.2.3](https://github.com/D4Vinci/Scrapling/releases/tag/v0.2.3) - 2024-11-19 {#v0.2.3}

### O que mudou {#v0.2.3-what-s-changed}

##### Correções de erros {#v0.2.3-bugs-squashed}
- Corrigido um erro na instalação com pip que impedia por completo o funcionamento do modo de ocultação do PlayWright Fetcher.

## [v0.2.2](https://github.com/D4Vinci/Scrapling/releases/tag/v0.2.2) - 2024-11-16 {#v0.2.2}

### O que mudou {#v0.2.2-what-s-changed}
##### Novos recursos {#v0.2.2-new-features}
- Se você não quiser passar argumentos ao objeto `Adaptor` gerado e preferir usar os valores padrão, pode usar esta importação para deixar o código mais limpo

    ```python
    >> from scrapling.default import Fetcher, StealthyFetcher, PlayWrightFetcher
    >> page = Fetcher.get('https://example.com', stealthy_headers=True)
    ```

    Caso contrário

    ```python
    >> from scrapling import Fetcher, StealthyFetcher, PlayWrightFetcher
    >> page = Fetcher(auto_match=False).get('https://example.com', stealthy_headers=True)
    ```

##### Correções de erros {#v0.2.2-bugs-squashed}
1. Corrigido um erro no objeto `Response`, introduzido no patch v0.2.1 de ontem, que acontecia em alguns casos de seleção ou análise aninhadas.

## [v0.2.1](https://github.com/D4Vinci/Scrapling/releases/tag/v0.2.1) - 2024-11-15 {#v0.2.1}

### O que mudou {#v0.2.1-what-s-changed}
##### Novos recursos {#v0.2.1-new-features}
1. O objeto `Response` retornado por todos os fetchers agora é igual ao objeto `Adaptor`, mas com estes atributos adicionais: `status`, `reason`, `cookies`, `headers` e `request_headers`. Os atributos `cookies`, `headers` e `request_headers` sempre são do tipo `dictionary`. <br/>Assim, seu código agora pode ser:

    ```python
    >> from scrapling import Fetcher
    >> page = Fetcher().get('https://example.com', stealthy_headers=True)
    >> print(page.status)
    200
    >> products = page.css('.product')
    ```

    Em vez do código anterior

    ```python
    >> from scrapling import Fetcher
    >> fetcher = Fetcher().get('https://example.com', stealthy_headers=True)
    >> print(fetcher.status)
    200
    >> page = fetcher.adaptor
    >> products = page.css('.product')
    ```

    Mantive a propriedade `.adaptor` funcionando para preservar a compatibilidade com versões anteriores.

2. As classes `StealthyFetcher` e `PlayWrightFetcher` agora aceitam um argumento `proxy` no método de obtenção de páginas, que pode ser uma string ou um dicionário.
3. A classe `StealthyFetcher` agora tem o argumento `os_randomize` no método `fetch`. Se ativado, o Scrapling escolhe aleatoriamente as impressões digitais do sistema operacional. Por padrão, as impressões digitais correspondem ao sistema operacional atual.

##### Correções de erros {#v0.2.1-bugs-squashed}
1. Corrigido um erro ao passar cabeçalhos com a classe `Fetcher`.
2. Corrigido um erro ao analisar respostas JSON recebidas das classes de fetchers.

##### Melhorias de uso {#v0.2.1-quality-of-life-changes}
1. As funções de texto tentavam remover comentários HTML antes de retornar o texto, mas isso causava erros em alguns casos e complicava o código sem necessidade. Agora elas voltaram ao comportamento padrão do lxml: **você vai notar um pequeno aumento de velocidade nas operações que dependem do texto dos elementos, como os seletores**. Se quiser que o Scrapling remova comentários HTML antes de retornar o texto para evitar a divisão estranha de texto do lxml/parsel/scrapy, mantenha o argumento `keep_comments` como True, que é o padrão.

## [v0.2](https://github.com/D4Vinci/Scrapling/releases/tag/v0.2) - 2024-11-11 {#v0.2}

### O que mudou {#v0.2-what-s-changed}
##### Novos recursos {#v0.2-new-features}
1. Chegou o recurso `Fetchers`, com 3 novos tipos principais para o Scrapling obter páginas para você com MUITAS opções!
    - A classe `Fetcher`, para solicitações HTTP básicas
    - A classe `StealthyFetcher`, um fetcher que oculta totalmente a automação usando uma [versão modificada do Firefox com recursos contra detecção](https://github.com/daijro/camoufox).
    - A classe `PlayWrightFetcher`, para fazer solicitações com navegador usando PlayWright sem modificações, PlayWright com um modo de ocultação feito por mim, navegadores reais via CDP e o [NSTBrowser](https://app.nstbrowser.io/r/1vO5e5) com seu [docker browserless](https://hub.docker.com/r/nstbrowser/browserless)!
2. Adicionados os métodos totalmente novos `find_all`/`find` para encontrar elementos na página com facilidade e um pouco de magia negra!
3. Adicionados os métodos `filter` e `search` à classe `Adaptors` para facilitar operações em lote com grupos de objetos `Adaptor`.
4. Adicionados os métodos `css_first` e `xpath_first` para facilitar o uso.
5. Adicionada a nova classe `TextHandlers`, usada em operações em lote com objetos `TextHandler`, assim como a classe `Adaptors`.
6. Adicionados os métodos `generate_full_css_selector` e `generate_full_xpath_selector`.

##### Correções de erros {#v0.2-bugs-squashed}
1. Na classe `Adaptors`, `re_first` agora retorna a primeira correspondência entre todos os objetos `Adaptor` que ela contém, em vez de retornar por engano os resultados de `re_first` de todos os objetos `Adaptor`.
2. Se você selecionar conteúdo de texto dos elementos (como com a função CSS `::text`) por um método como `.css` ou `.xpath`, o objeto `Adaptor` agora retorna a classe `TextHandlers` em vez de uma lista de strings. Assim, você pode usar `page.css('something::text').re_first(r'regex_pattern').json()` em vez de `page.css('something::text')[0].re_first(r'regex_pattern').json()`
3. Os argumentos re/re_first de `Adaptor`/`Adaptors` agora são consistentes com os de `TextHandler`. Agora você tem os argumentos `clean_match` e `case_sensitive`.
4. O argumento `auto_match` está ativado por padrão ao criar `Adaptor`, mas você ainda precisa ativá-lo ao selecionar elementos se quiser usá-lo. (Não é um erro, e sim uma decisão de projeto)
5. Corrigidas várias anotações de tipos para melhorar o preenchimento automático ao programar com Scrapling.

##### Melhorias de uso {#v0.2-quality-of-life-changes}
1. Os métodos `css_selector` e `xpath_selector` foram renomeados para `generate_css_selector` e `generate_xpath_selector` para dar mais clareza e não atrapalhar o preenchimento automático ao programar.
2. Reorganizada a maior parte do código antigo em um subpacote `core`, junto com outras decisões de projeto para facilitar a manutenção futura.
3. Reorganizada a pasta de testes e adicionados testes dos novos recursos. Agora os ambientes do tox ficam em cache no GitHub para acelerar os testes automáticos de cada commit.

## [v0.1.2](https://github.com/D4Vinci/Scrapling/releases/tag/v0.1.2) - 2024-10-16 {#v0.1.2}

**Histórico de mudanças**:

- Corrigido um erro que impedia o argumento `keep_comments` de funcionar como deveria.
- Ajustada a função de texto para remover automaticamente comentários HTML dos elementos antes de extrair seu texto e evitar o comportamento diferente do Lxml. Por exemplo:

    ```python
    >>> page = Adaptor('<span>CONDITION: <!-- -->Excellent</span>', keep_comments=True)
    >>> page.css('span::text')
    ['CONDITION: ', 'Excellent']
    ```

    Antes, esse era o resultado por causa do comportamento padrão do Lxml, mas agora ele retorna o texto completo 'CONDITION: Excellent'
    Esse comportamento também é conhecido no parsel\scrapy, então quis tratá-lo aqui.

- Corrigido um erro que impedia a remoção do arquivo de banco de dados SQLite criado pela biblioteca ao executar `pip uninstall scrapling` ou um comando semelhante.

## [v0.1.1](https://github.com/D4Vinci/Scrapling/releases/tag/v0.1.1) - 2024-10-14 {#v0.1.1}

Pequenas correções

## [v0.1](https://github.com/D4Vinci/Scrapling/releases/tag/v0.1) - 2024-10-13 {#v0.1}

**Histórico completo de mudanças**: <https://github.com/D4Vinci/Scrapling/commits/v0.1>
