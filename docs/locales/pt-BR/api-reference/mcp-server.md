---
title: "Referência da API do servidor MCP do Scrapling"
description: "Veja as ferramentas do servidor MCP e seus modelos de solicitações, respostas e sessões para extrair dados por HTTP ou navegadores."
---

# Referência do servidor MCP {#mcp-server-api-reference}

O **servidor MCP do Scrapling** oferece dezesseis ferramentas para extrair dados e interagir com o navegador por meio do Model Context Protocol (MCP). Integre o Scrapling a assistentes e agentes de IA para extrair dados por conversas, com recursos para evitar a detecção de bots.

Inicie o servidor MCP com este comando:

```bash
scrapling mcp
```

Ou importe a classe do servidor diretamente:

```python
from scrapling.core.ai import ScraplingMCPServer

server = ScraplingMCPServer()
server.serve(http=False, host="127.0.0.1", port=8000)
```

Para usar seu próprio executável de navegador compatível com Chromium, passe `executable_path`:

```python
server = ScraplingMCPServer(executable_path="/path/to/chromium")
```

## Modelo de resposta {#response-model}

As ferramentas de obtenção de páginas e solicitações HTTP retornam esta estrutura, com uma resposta por chamada. As ferramentas de gerenciamento de sessões usam os modelos a seguir. `browser_screenshot` retorna uma imagem da página ou de um elemento, junto com a URL atual, como blocos de imagem e texto. `browser_extract` e `browser_actions` retornam texto simples. As duas ferramentas de rede retornam JSON estruturado por meio dos modelos a seguir. `browser_evaluate` retorna o resultado como JSON dentro de um bloco de texto.

## ::: scrapling.core.ai.server.ResponseModel
    handler: python
    :docstring:

## Modelos de solicitações de rede {#network-request-models}

`browser_network_requests` retorna `NetworkRequestsModel` com `requests`, `next_cursor`, `has_more` e `dropped_count`. Cada `NetworkRequestInfo` contém `id`, `url`, `method`, `resource_type` e `status`. Para continuar, passe `next_cursor` como `after_id`. `has_more` indica se há mais correspondências no histórico atual.

`browser_network_request` retorna `NetworkRequestModel` com `request_id`, `part`, `data` e `note`. Os resumos e os cabeçalhos são objetos. O conteúdo completo salvo é retornado como uma string, mesmo que a resposta contenha JSON. `note` explica se faltam dados do conteúdo ou se os cabeçalhos estão incompletos.

## ::: scrapling.core.ai._network_formatting.NetworkRequestInfo
    handler: python
    :docstring:

## ::: scrapling.core.ai.server.NetworkRequestsModel
    handler: python
    :docstring:

## ::: scrapling.core.ai._network_formatting.NetworkRequestModel
    handler: python
    :docstring:

## Modelos de sessões {#session-models}

Classes de modelos para gerenciar sessões:

## ::: scrapling.core.ai.server.SessionInfo
    handler: python
    :docstring:

## ::: scrapling.core.ai.server.SessionCreatedModel
    handler: python
    :docstring:

## ::: scrapling.core.ai.server.SessionClosedModel
    handler: python
    :docstring:

## Classe do servidor MCP {#mcp-server-class}

A classe principal do servidor MCP oferece as seguintes ferramentas:

- **`make_request`**: Obtém uma URL por HTTP com imitação de navegador e fechamento automático do cliente. Aceita GET, POST, PUT e DELETE.
- **`browser_fetch_once`**: Obtém uma URL com um navegador furtivo, executa JavaScript, lida com Cloudflare e fecha o navegador. Use uma sessão persistente se precisar realizar ações depois ou consultar o histórico de rede.

- **`browser_extract`**: Lê a página atual ou um elemento como uma captura estruturada para IA, HTML, Markdown ou texto, sem recarregar. Mantém os resultados de formulários e ações. As capturas incluem papéis, nomes, referências, posições e tamanhos dos elementos. A busca com expressões regulares retorna as linhas correspondentes, o contexto próximo e os nós pai.
- **`browser_actions`**: Encadeia movimentos do mouse, ações ao passar o cursor, cliques, rolagens, preenchimento de campos, atalhos de teclado, respostas a caixas de diálogo e esperas em uma chamada. Aceite ou dispense alertas e confirmações, ou escreva em caixas de entrada. Você pode preencher uma busca, enviá-la, esperar e abrir um resultado sem fazer uma chamada por etapa.

    Os movimentos e cliques aceitam seletores, referências de capturas ou coordenadas. A ferramenta espera pelos elementos e os traz para a área visível. Aceita movimentos em etapas, cliques esquerdo, direito e central, clique duplo e rolagem em painéis aninhados.

    Selecione campos por seletores ou referências de capturas. Digite texto, marque ou desmarque caixas de seleção, selecione botões de opção e escolha uma ou várias opções de listas nativas pelo rótulo. Substitua ou apague o texto, ou digite na posição do cursor. Os atalhos usam o foco atual. O modo lento adiciona pausas aleatórias entre os caracteres e as ações.

    Espere pelo conteúdo ou até que os indicadores de carregamento desapareçam usando seletores ou referências de capturas. Você também pode esperar por eventos de carregamento, pelo fim da atividade de rede ou por um tempo fixo.

- **`browser_evaluate`**: Executa JavaScript na página atual para extrair dados personalizados, fazer cálculos, ler o estado da aplicação ou alterar o conteúdo. Aceita scripts assíncronos e retorna seus resultados como JSON.
- **`browser_network_requests`**: Busca solicitações de navegador concluídas entre abas, navegações e ações. Encontre chamadas de API, erros HTTP e redirecionamentos salvos. Oculta recursos estáticos por padrão para reduzir os resultados. Ignora solicitações que falharam ou não foram concluídas. Retorna dados estruturados com paginação.
- **`browser_network_request`**: Lê o resumo, os cabeçalhos, os dados enviados ou o conteúdo de texto de uma solicitação salva como JSON estruturado, sem repeti-la. Retorna a parte escolhida completa. As respostas salvas continuam disponíveis após mudar de página, incluindo respostas HTTP 4xx e 5xx. Os registros aparecem quando a captura termina. Consultar o histórico ou fechar a sessão não espera pelas capturas pendentes, que podem se perder ao navegar ou fechar. Os bytes vêm do Playwright e podem ser diferentes dos enviados pelo servidor. O texto usa a decodificação UTF-8 do Playwright quando ela é válida; caso contrário, usa o charset declarado. Só lê e salva o conteúdo com um `Content-Type` de texto compatível. Para tipos binários, ausentes ou desconhecidos, mantém os metadados e cabeçalhos sem ler o conteúdo. Isso não muda o carregamento da página. O histórico tem limites de tamanho. Uma nota opcional explica se o conteúdo não é texto, é muito grande ou não pode ser lido. Leia os dados de que precisa antes de fechar a sessão MCP.
- **`browser_fetch`**: Obtém uma página usando uma sessão de navegador furtivo aberta e extrai HTML, Markdown, texto ou uma captura estruturada. As capturas podem cobrir toda a página ou um elemento e incluem referências, posições e tamanhos para interagir depois.

## ::: scrapling.core.ai.server.ScraplingMCPServer
    handler: python
    :docstring:
