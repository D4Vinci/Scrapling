<!-- mcp-name: io.github.D4Vinci/Scrapling -->

<h1 align="center">
    <a href="https://scrapling.readthedocs.io/pt-br/latest/">
        <picture>
          <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/docs/assets/cover_dark.svg?sanitize=true">
          <img alt="Capa do Scrapling" src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/docs/assets/cover_light.svg?sanitize=true">
        </picture>
    </a>
    <br>
    <small>Extraia dados da web moderna de forma simples</small>
</h1>

<p align="center">
    <a href="https://trendshift.io/repositories/14244" target="_blank"><img src="https://trendshift.io/api/badge/repositories/14244" alt="D4Vinci%2FScrapling | Trendshift" style="width: 250px; height: 55px;" width="250" height="55"/></a>
    <br/>
    <a href="https://github.com/D4Vinci/Scrapling/actions/workflows/tests.yml" alt="Testes">
        <img alt="Testes" src="https://github.com/D4Vinci/Scrapling/actions/workflows/tests.yml/badge.svg"></a>
    <a href="https://badge.fury.io/py/Scrapling" alt="Versão no PyPI">
        <img alt="Versão no PyPI" src="https://badge.fury.io/py/Scrapling.svg"></a>
    <a href="https://hub.docker.com/r/pyd4vinci/scrapling" target="_blank">
        <img alt="Downloads no Docker" src="https://img.shields.io/docker/pulls/pyd4vinci/scrapling?labelColor=%20%23FDB062&logo=Docker&labelColor=%20%23528bff"></a>
    <a href="https://clickpy.clickhouse.com/dashboard/scrapling" rel="nofollow"><img src="https://img.shields.io/pypi/dm/scrapling" alt="Downloads do pacote no PyPI"></a>
    <a href="https://scrapling.readthedocs.io/pt-br/latest/ai/agent-skill.html" alt="Skill para agentes de IA">
        <img alt="Badge da Agent Skill" src="https://img.shields.io/badge/Skill-black?style=flat&label=Agent&link=https%3A%2F%2Fscrapling.readthedocs.io%2Fpt-br%2Flatest%2Fai%2Fagent-skill.html"></a>
    <a href="https://clawhub.ai/D4Vinci/scrapling-official" alt="Skill para OpenClaw">
        <img alt="Skill para OpenClaw" src="https://img.shields.io/badge/Clawhub-darkred?style=flat&label=OpenClaw&link=https%3A%2F%2Fclawhub.ai%2FD4Vinci%2Fscrapling-official"></a>
    <br/>
    <a href="https://discord.gg/EMgGbDceNQ" alt="Discord" target="_blank">
      <img alt="Discord" src="https://img.shields.io/discord/1360786381042880532?style=social&logo=discord&link=https%3A%2F%2Fdiscord.gg%2FEMgGbDceNQ">
    </a>
    <a href="https://x.com/Scrapling_dev" alt="X (antigo Twitter)">
      <img alt="Siga no X (antigo Twitter)" src="https://img.shields.io/twitter/follow/Scrapling_dev?style=social&logo=x&link=https%3A%2F%2Fx.com%2FScrapling_dev">
    </a>
    <br/>
    <a href="https://pypi.org/project/scrapling/" alt="Versões do Python compatíveis">
        <img alt="Versões do Python compatíveis" src="https://img.shields.io/pypi/pyversions/scrapling.svg"></a>
</p>

<p align="center">
    <a href="https://scrapling.readthedocs.io/pt-br/latest/parsing/selection.html"><strong>Métodos de seleção</strong></a>
    &middot;
    <a href="https://scrapling.readthedocs.io/pt-br/latest/fetching/choosing.html"><strong>Fetchers</strong></a>
    &middot;
    <a href="https://scrapling.readthedocs.io/pt-br/latest/spiders/architecture.html"><strong>Spiders</strong></a>
    &middot;
    <a href="https://scrapling.readthedocs.io/pt-br/latest/spiders/proxy-blocking.html"><strong>Rotação de proxies</strong></a>
    &middot;
    <a href="https://scrapling.readthedocs.io/pt-br/latest/cli/overview.html"><strong>CLI</strong></a>
    &middot;
    <a href="https://scrapling.readthedocs.io/pt-br/latest/ai/mcp-server.html"><strong>MCP</strong></a>
</p>

Scrapling é um framework de web scraping para Python. Ele reúne solicitações HTTP rápidas, navegadores furtivos, análise de páginas e rastreamento simultâneo em uma só biblioteca.

Extraia dados de páginas estáticas, execute JavaScript, interaja com sites e acesse as APIs que eles usam. Crie crawlers com sessões reutilizáveis, rotação de proxies, novas tentativas automáticas, pausa e retomada, e exportação de dados integrada.

Use o Scrapling pelo Python, pelo terminal ou com seu agente de IA por meio do servidor MCP e da Agent Skill. Ele cobre todo o processo, desde extrair alguns campos até salvar um site inteiro como arquivos Markdown limpos.

## O que você pode fazer com o Scrapling

- **[Obter páginas e interagir](https://scrapling.readthedocs.io/pt-br/latest/fetching/choosing.html)**: Solicitações HTTP rápidas, navegadores furtivos, execução de JavaScript, tratamento de Cloudflare Turnstile e Interstitial, sessões persistentes e captura de respostas de APIs em segundo plano.
- **[Analisar e extrair](https://scrapling.readthedocs.io/pt-br/latest/parsing/selection.html)**: Busca com CSS, XPath, texto e expressões regulares, localização de elementos após mudanças na página, busca de elementos semelhantes e saída em Markdown limpo.
- **[Rastrear e exportar](https://scrapling.readthedocs.io/pt-br/latest/spiders/getting-started.html)**: Spiders simultâneos, rotação de proxies, novas tentativas, AutoThrottle, pausa e retomada, resultados em streaming, modelos prontos e exportação em JSON, JSONL, CSV e XML.
- **[Extrair dados com IA ou pelo terminal](https://scrapling.readthedocs.io/pt-br/latest/ai/mcp-server.html)**: Um servidor MCP para agentes de IA navegarem e extraírem dados, uma Agent Skill, comandos CLI e um shell interativo.

Comece com uma só página:

```python
from scrapling.fetchers import Fetcher

page = Fetcher.get('https://quotes.toscrape.com/')
quotes = page.css('.quote .text::text').getall()
print(quotes)
```

Ou extraia mais dados com um spider:

```python
from scrapling.spiders import Spider, Response

class QuotesSpider(Spider):
    name = "quotes"
    start_urls = ["https://quotes.toscrape.com/"]

    async def parse(self, response: Response):
        for quote in response.css('.quote'):
            yield {
                "text": quote.css('.text::text').get(),
                "author": quote.css('.author::text').get(),
            }

result = QuotesSpider().start()
print(len(result.items))
result.items.to_json("quotes.json")
```

Este exemplo imprime `10` e salva as citações e seus autores em `quotes.json`.

<p align="center">
    <a href="https://dataimpulse.com/?utm_source=scrapling&utm_medium=banner&utm_campaign=scrapling" target="_blank" style="display:flex; justify-content:center; padding:4px 0;">
        <img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/DataImpulse.png" alt="At DataImpulse, we specialize in developing custom proxy services for your business. Make requests from anywhere, collect data, and enjoy fast connections with our premium proxies." style="max-height:60px;">
    </a>
</p>

# Patrocinadores Platinum
<table>
  <tr>
    <td width="200">
      <a href="https://go.nodemaven.com/scraplingoctober" target="_blank" title="Proxies with the Highest IP Scores">
        <img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/NodeMaven.jpg" width="240" height="100">
      </a>
    </td>
    <td>
    <a href="https://go.nodemaven.com/scraplingoctober" target="_blank">NodeMaven</a> - o provedor de proxies mais eficiente para Web Scraping e automação, com a mais alta qualidade de IP do mercado. Use o código SCRAPLING35 para obter 35% de desconto.
    </td>
  </tr>
  <tr>
    <td width="200">
      <a href="https://hypersolutions.co/?utm_source=github&utm_medium=readme&utm_campaign=scrapling" target="_blank" title="Bot Protection Bypass API for Akamai, DataDome, Incapsula & Kasada">
        <img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/HyperSolutions.png">
      </a>
    </td>
    <td> Scrapling lida com o Cloudflare Turnstile. Para proteção de nível empresarial, <a href="https://hypersolutions.co?utm_source=github&utm_medium=readme&utm_campaign=scrapling">
        <b>Hyper Solutions</b>
      </a> oferece endpoints de API que geram tokens antibot válidos para <b>Akamai</b>, <b>DataDome</b>, <b>Kasada</b> e <b>Incapsula</b>. Chamadas simples de API, sem necessidade de automação de navegador. </td>
  </tr>
  <tr>
    <td width="200">
      <a href="https://evomi.com?utm_source=github&utm_medium=banner&utm_campaign=d4vinci-scrapling" target="_blank" title="Evomi is your Swiss Quality Proxy Provider, starting at $0.49/GB">
        <img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/evomi.png">
      </a>
    </td>
    <td>
      <a href="https://evomi.com?utm_source=github&utm_medium=banner&utm_campaign=d4vinci-scrapling">
        <b>Evomi</b>
      </a>: proxies residenciais a partir de US$0,49/GB. Navegador de scraping com Chromium que altera sua identificação, IPs residenciais, resolução automática de CAPTCHA e recursos para evitar sistemas antibot. </br>
      <b>Scraper API para resultados sem complicação. Integrações com MCP e N8N estão disponíveis.</b>
    </td>
  </tr>
  <tr>
    <td width="200">
      <a href="https://substack.thewebscraping.club/p/scrapling-hands-on-guide?utm_source=github&utm_medium=repo&utm_campaign=scrapling" target="_blank" title="The #1 newsletter dedicated to Web Scraping">
        <img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/TWSC.png">
      </a>
    </td>
    <td>
    Leia uma análise completa do <a href="https://substack.thewebscraping.club/p/scrapling-hands-on-guide?utm_source=github&utm_medium=repo&utm_campaign=scrapling" target="_blank">Scrapling no The Web Scraping Club</a> (nov. 2025), a newsletter número 1 dedicada a Web Scraping.
    </td>
  </tr>
  <tr>
    <td width="200">
      <a href="https://www.swiftproxy.net/?ref=D4Vinci" target="_blank" title="Scalable Solutions for Web Data Access">
        <img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/SwiftProxy.png">
      </a>
    </td>
    <td>
    <a href="https://www.swiftproxy.net/?ref=D4Vinci" target="_blank">Swiftproxy</a> fornece proxies residenciais escaláveis com mais de 80 milhões de IPs em mais de 195 países, entregando conexões rápidas e confiáveis, rotação automática e recursos para evitar bloqueios. Teste grátis disponível.
    </td>
  </tr>
  <tr>
    <td width="200">
      <a href="https://byteful.com/?utm_source=github&utm_medium=github-sponsor&utm_campaign=scrapling_github_sponsor" target="_blank" title="Ethically sourced residential proxy infrastructure powering web scraping and AI agents">
        <img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/byteful.png">
      </a>
    </td>
    <td>
    A <a href="https://byteful.com/?utm_source=github&utm_medium=github-sponsor&utm_campaign=scrapling_github_sponsor" target="_blank">Byteful</a> fornece proxies residenciais, móveis, ISP e de datacenter de origem ética, além de ferramentas de scraping e automação com IA. Use o código SCRAPLING10 para obter 10% de desconto em proxies residenciais.
    </td>
  </tr>
  <tr>
    <td width="200">
      <a href="https://proxylane.dev/?utm_source=scrapling&utm_medium=partnership&utm_campaign=scrapling_platinum_202609&utm_content=github_readme" target="_blank" title="28M+ clean residential IPs for browser automation. No Blocks. No CAPTCHAs. Pay-as-you-Go.">
        <img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/proxylane.png">
      </a>
    </td>
    <td>
    <a href="https://proxylane.dev/?utm_source=scrapling&utm_medium=partnership&utm_campaign=scrapling_platinum_202609&utm_content=github_readme" target="_blank">ProxyLane</a>: Reduza os bloqueios e os CAPTCHAs em 90%. 28 milhões de IPs residenciais premium para scraping intensivo da web. 195 países. Segmentação por cidade/ISP/CEP. Sessões fixas ou rotativas. Tráfego sem prazo de validade a partir de $2/GB. Código <strong>SCRAPEANDTAKE</strong>: <em>25% de desconto</em>.
    </td>
  </tr>
  <tr>
    <td width="200">
      <a href="https://www.lundproxy.com/unlimited-residential-bandwidth.html?utm_source=github&utm_medium=sponsorship&utm_campaign=scrapling&utm_content=banner" target="_blank" title="Unlimited residential traffic, sized only by bandwidth.">
        <img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/lundproxy.png">
      </a>
    </td>
    <td>
    <a href="https://www.lundproxy.com?utm_source=github&utm_medium=sponsorship&utm_campaign=scrapling&utm_content=text" target="_blank">LundProxy</a>: Pare de pagar por GB. Tráfego residencial ilimitado, mais de 100 milhões de IPs, mais de 190 países. Pague pela largura de banda. Solicite um teste gratuito de proxies residenciais de 50 Mbps.
    </td>
  </tr>
  <tr>
    <td width="200">
      <a href="https://dataimpulse.com/?utm_source=website&utm_medium=github_readme&utm_campaign=scrapling_platinum" target="_blank" title="Buy Pay-as-you-go proxies from $1/GB">
        <img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/DataImpulse_Platinum.png">
      </a>
    </td>
    <td>
    $1/GB na <a href="https://dataimpulse.com/?utm_source=website&utm_medium=github_readme&utm_campaign=scrapling_platinum" target="_blank">DataImpulse</a>. Proxies de origem ética, direto da fonte. Mais de 90 milhões de IPs, mais de 195 países. Residenciais, de datacenter e móveis. Pagamento por uso = sem assinatura. O tráfego nunca expira.
    </td>
  </tr>
</table>

<i><sub>Quer mostrar seu anúncio aqui? Clique [aqui](https://github.com/sponsors/D4Vinci/sponsorships?tier_id=586646)</sub></i>
# Patrocinadores

<!-- sponsors -->

<a href="https://cloro.dev/?utm_source=referral&utm_medium=scrapling" target="_blank" title="The search API for the AI era"><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/cloro.jpg"></a>

<br/>

<a href="https://serpapi.com/?utm_source=scrapling" target="_blank" title="Scrape Google and other search engines with SerpApi"><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/SerpApi.png"></a>
<a href="https://visit.decodo.com/Dy6W0b" target="_blank" title="Try the Most Efficient Residential Proxies for Free"><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/decodo.png"></a>
<a href="https://proxyempire.io/?ref=scrapling&utm_source=github&utm_medium=paid_referral&utm_campaign=open_source_sponsorship&utm_content=scrapling" target="_blank" title="Collect The Data Your Project Needs with the Best Residential Proxies"><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/ProxyEmpire.png"></a>
<a href="https://www.webshare.io/?referral_code=48r2m2cd5uz1" target="_blank" title="The Most Reliable Proxy with Unparalleled Performance"><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/webshare.png"></a>
<a href="https://proxiware.com/?ref=scrapling" target="_blank" title="Collect Any Data. At Any Scale."><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/proxiware.png"></a>


<!-- /sponsors -->

<i><sub>Quer mostrar seu anúncio aqui? Clique [aqui](https://github.com/sponsors/D4Vinci) e escolha o plano que fizer mais sentido para você!</sub></i>

---

## Principais recursos

### Spiders: um framework completo de rastreamento

- 🕷️ **API de Spider parecida com a do Scrapy**: Defina spiders com `start_urls`, callbacks `parse` assíncronos e objetos `Request` e `Response`.
- ⚡ **Rastreamento simultâneo**: Configure o número de solicitações simultâneas, os limites por domínio e o intervalo entre downloads.
- 🔄 **Várias sessões**: Use solicitações HTTP e navegadores furtivos sem interface gráfica no mesmo spider. Direcione as solicitações para sessões diferentes pelo ID.
- 💾 **Pausa e retomada**: Salve as solicitações pendentes e as URLs visitadas com `crawldir`. Pressione Ctrl+C para parar com segurança e reinicie com o mesmo diretório.
- 📡 **Resultados em streaming**: Receba os itens assim que forem extraídos com `async for item in spider.stream()`, junto com estatísticas em tempo real. É útil para interfaces, processos de dados e rastreamentos longos.
- 🛡️ **Detecção de solicitações bloqueadas**: Detecte e repita automaticamente as solicitações bloqueadas. Você pode personalizar esse comportamento.
- 🚦 **AutoThrottle**: O spider ajusta o intervalo de cada domínio conforme a velocidade de resposta do site. Se o site bloquear ou limitar as solicitações, ele dobra o intervalo ou respeita o tempo indicado por `Retry-After`. Quando a limitação termina, volta a acelerar.
- 🤖 **Respeito ao robots.txt**: Ative `robots_txt_obey` para respeitar as diretivas `Disallow`, `Crawl-delay` e `Request-rate`, com cache por domínio.
- 🧪 **Modo de desenvolvimento**: Salve as respostas em disco na primeira execução e reutilize-as nas próximas. Assim você pode ajustar `parse()` sem enviar novas solicitações aos servidores.
- 🧩 **Modelos de spider prontos**: Use `CrawlSpider` para seguir links por regras, `SitemapSpider` para rastrear a partir de sitemaps ou robots.txt, `XMLFeedSpider` e `CSVFeedSpider` para ler feeds XML, RSS e CSV, e `ShopifySpider` para coletar produtos de lojas públicas do Shopify, com um item por variante.
- 🔗 **Extração de links**: `LinkExtractor` permite aceitar ou recusar links por padrões, filtrar domínios e extensões, limitar a busca com CSS ou XPath e normalizar as URLs. Use com os modelos ou separadamente.
- 📦 **Exportação integrada**: Exporte os resultados com hooks e seu próprio processo de dados, ou use os formatos JSON, JSONL, CSV e XML integrados: `result.items.to_json()`, `to_jsonl()`, `to_csv()` e `to_xml()`.

### Obtenção de páginas com suporte a sessões

- **Solicitações HTTP**: Envie solicitações HTTP rápidas e furtivas com `Fetcher`. Você pode imitar a impressão digital TLS e os cabeçalhos de um navegador, além de usar HTTP/3.
- **Carregamento dinâmico**: Obtenha sites dinâmicos com automação completa do navegador por meio de `StealthyFetcher`, compatível com o Chromium do Playwright e o Google Chrome.
- **Evasão de sistemas antibot**: `StealthyFetcher` oculta a automação e imita impressões digitais do navegador. Pode superar automaticamente os diferentes tipos de Cloudflare Turnstile e Interstitial.
- **Gerenciamento de sessões**: `FetcherSession` e `StealthySession` mantêm os cookies e o estado entre solicitações.
- **Rotação de proxies**: `ProxyRotator` permite alternar os proxies de forma cíclica ou personalizada em todos os tipos de sessão. Você também pode escolher um proxy para uma solicitação específica.
- **Bloqueio de domínios e anúncios**: Bloqueie solicitações a domínios e subdomínios específicos ou ative o bloqueio de anúncios dos fetchers de navegador. Ele inclui cerca de 3.500 domínios conhecidos de anúncios e rastreamento.
- **Prevenção de vazamentos de DNS**: Ative DNS-over-HTTPS para enviar consultas DNS pelo serviço DoH da Cloudflare e evitar vazamentos ao usar proxies.
- **Navegadores remotos**: Conecte-se a um navegador em execução por CDP com `cdp_url`, seja no seu computador, em outro servidor ou em um serviço de navegadores. Você também pode usar sua própria versão do Chromium com qualquer fetcher de navegador por meio de `executable_path`.
- **Captura de APIs em segundo plano**: Ative `record_requests=True` em uma sessão de navegador e busque as respostas salvas com `session.network.search(limit=None)`. Leia dados de APIs e erros HTTP de diferentes carregamentos sem repetir as solicitações. O histórico tem tamanho limitado e salva o conteúdo das respostas de texto.
- **Suporte assíncrono**: Todos os fetchers permitem o uso assíncrono, com classes de sessão próprias para esse modo.

### Análise de páginas e extração de dados

- 🔄 **Localização de elementos**: Encontre os elementos após mudanças no site usando algoritmos de semelhança.
- 🎯 **Seleção flexível**: Use seletores CSS e XPath, filtros, texto, expressões regulares e mais.
- 🔍 **Elementos semelhantes**: Encontre automaticamente elementos parecidos com os que você já localizou.

### Recursos de IA

- 🤖 **Servidor MCP**: Permite que assistentes e agentes de IA, como Claude e Cursor, extraiam dados com Scrapling por meio de solicitações HTTP, ações do navegador, capturas de tela, estado de login salvo e respostas de APIs em segundo plano. Usa nosso navegador furtivo e ferramentas que ajudam os modelos adequados a resolver CAPTCHA, além do solucionador de Cloudflare. Reduz o conteúdo enviado ao modelo, bloqueia anúncios e protege contra injeção de instruções (prompt injection). Também permite usar navegadores remotos por CDP e conexões HTTP com opções de autenticação. ([Vídeo de demonstração](https://www.youtube.com/watch?v=qyFk3ZNwOxE))
- 🧠 **Agent Skill**: Uma [Agent Skill](https://scrapling.readthedocs.io/pt-br/latest/ai/agent-skill.html) pronta para instalar que ensina a biblioteca aos agentes de programação, para que escrevam código compatível com a API atual.
- 📚 **Markdown pronto para RAG**: Converta uma página em Markdown limpo e preparado para modelos de linguagem com uma linha (`page.markdown()`), ou salve um site inteiro como arquivos Markdown com o modelo `ContentSpider`. O processo não precisa de um modelo de linguagem. ([Documentação](https://scrapling.readthedocs.io/pt-br/latest/ai/building-rag-systems.html))

### Alto desempenho e uso comprovado

- 🚀 **Alta velocidade**: Desempenho otimizado que supera a maioria das bibliotecas de web scraping para Python.
- 🔋 **Baixo consumo de memória**: Estruturas de dados otimizadas e carregamento apenas quando necessário.
- ⚡ **Conversão rápida para JSON**: 10 vezes mais rápida que a biblioteca padrão.
- 🏗️ **Testado na prática**: Os testes cobrem 92% do Scrapling e todo o código tem anotações de tipo. Centenas de pessoas o usaram diariamente para extrair dados durante o último ano.

### Ferramentas para desenvolver e extrair dados

- 🎯 **Shell interativo**: Shell IPython opcional integrado ao Scrapling, com atalhos e ferramentas para criar scripts mais rápido. Converta solicitações curl em solicitações do Scrapling e veja os resultados no navegador.
- 🚀 **Uso pelo terminal**: Extraia os dados de uma URL sem escrever código.
- 🛠️ **Navegação pelo DOM**: Acesse os elementos pai, irmãos e filhos.
- 🧬 **Processamento de texto**: Expressões regulares, limpeza de texto e operações de strings otimizadas.
- 📝 **Geração de seletores**: Gere seletores CSS e XPath confiáveis para qualquer elemento.
- 🔌 **API conhecida**: Parecida com Scrapy e BeautifulSoup, com os mesmos pseudoelementos do Scrapy e do Parsel.
- 🤝 **Integração direta com Scrapy**: Adicione o decorador `scrapling_response` a um callback para analisar as respostas que você já obtém com o parser do Scrapling, sem reescrever seu programa.
- 📘 **Anotações de tipo completas**: Ajudam o editor a verificar e completar o código. Todo o código é verificado automaticamente com **PyRight** e **MyPy** a cada alteração.
- 🔋 **Imagem Docker pronta**: Uma imagem Docker com todos os navegadores é criada e publicada automaticamente a cada versão.

## Primeiros passos

Veja alguns exemplos do que você pode fazer com o Scrapling.

### Uso básico
Solicitações HTTP com suporte a sessões
```python
from scrapling.fetchers import Fetcher, FetcherSession

with FetcherSession(impersonate='chrome') as session:  # Use a versão mais recente da fingerprint TLS do Chrome
    page = session.get('https://quotes.toscrape.com/', stealthy_headers=True)
    quotes = page.css('.quote .text::text').getall()

# Ou use requisições avulsas
page = Fetcher.get('https://quotes.toscrape.com/')
quotes = page.css('.quote .text::text').getall()
```
Navegação furtiva
```python
from scrapling.fetchers import StealthyFetcher, StealthySession

with StealthySession(headless=True, solve_cloudflare=True) as session:  # Mantenha o navegador aberto até terminar
    page = session.fetch('https://nopecha.com/demo/cloudflare', google_search=False)
    data = page.css('#padded_content a').getall()

# Ou use o estilo de requisição avulsa, ele abre o navegador para esta requisição e o fecha ao finalizar
page = StealthyFetcher.fetch('https://nopecha.com/demo/cloudflare', solve_cloudflare=True)
data = page.css('#padded_content a').getall()
```
Automação completa de navegador
```python
from scrapling.fetchers import StealthyFetcher, StealthySession

with StealthySession(headless=True, disable_resources=False, network_idle=True) as session:  # Mantenha o navegador aberto até terminar
    page = session.fetch('https://quotes.toscrape.com/', load_dom=False)
    data = page.xpath('//span[@class="text"]/text()').getall()  # Se preferir, use seletor XPath

# Ou use o estilo de requisição avulsa, ele abre o navegador para esta requisição e o fecha ao finalizar
page = StealthyFetcher.fetch('https://quotes.toscrape.com/')
data = page.css('.quote .text::text').getall()
```

### Spiders
Crie crawlers completos com solicitações simultâneas, vários tipos de sessão, pausa e retomada:
```python
from scrapling.spiders import Spider, Response

class QuotesSpider(Spider):
    name = "quotes"
    start_urls = ["https://quotes.toscrape.com/"]
    concurrent_requests = 10
    
    async def parse(self, response: Response):
        for quote in response.css('.quote'):
            yield {
                "text": quote.css('.text::text').get(),
                "author": quote.css('.author::text').get(),
            }
            
        next_page = response.css('.next a')
        if next_page:
            yield response.follow(next_page[0].attrib['href'])

result = QuotesSpider().start()
print(f"Extraídas {len(result.items)} citações")
result.items.to_json("quotes.json")
```
Use vários tipos de sessão no mesmo spider:
```python
from scrapling.spiders import Spider, Request, Response
from scrapling.fetchers import FetcherSession, AsyncStealthySession

class MultiSessionSpider(Spider):
    name = "multi"
    start_urls = ["https://example.com/"]
    
    def configure_sessions(self, manager):
        manager.add("fast", FetcherSession(impersonate="chrome"))
        manager.add("stealth", AsyncStealthySession(headless=True), lazy=True)
    
    async def parse(self, response: Response):
        for link in response.css('a::attr(href)').getall():
            # Direcione páginas protegidas através da sessão stealth
            if "protected" in link:
                yield Request(link, sid="stealth")
            else:
                yield Request(link, sid="fast", callback=self.parse)  # callback explícito
```
Salve o progresso para pausar e retomar rastreamentos longos. Execute o spider assim:
```python
QuotesSpider(crawldir="./crawl_data").start()
```
Com `crawldir` definido, pressione Ctrl+C para salvar as solicitações pendentes e as URLs visitadas. Reinicie com o mesmo `crawldir` para continuar. Salve os dados extraídos separadamente.

Você também pode usar um modelo pronto. Por exemplo, extraia o catálogo inteiro de uma loja Shopify:
```python
from scrapling.spiders import ShopifySpider

class MyStore(ShopifySpider):
    target_website = "example.com"

result = MyStore().start()  # Todos os produtos da loja, um item por variante
```
O modelo lê os produtos disponíveis nos endpoints públicos das coleções, com um item por variante.

### Análise avançada e navegação
```python
from scrapling.fetchers import Fetcher

# Seleção rica de elementos e navegação
page = Fetcher.get('https://quotes.toscrape.com/')

# Obtenha citações com múltiplos métodos de seleção
quotes = page.css('.quote')  # Seletor CSS
quotes = page.xpath('//div[@class="quote"]')  # XPath
quotes = page.find_all('div', {'class': 'quote'})  # Estilo BeautifulSoup
# O mesmo que
quotes = page.find_all('div', class_='quote')
quotes = page.find_all(['div'], class_='quote')
quotes = page.find_all(class_='quote')  # e assim por diante...
# Encontre elementos por conteúdo de texto
quotes = page.find_by_text('Albert Einstein', first_match=False)

# Navegação avançada
quote_text = page.css('.quote')[0].css('.text::text').get()
quote_texts = page.css('.quote').css('.text::text').getall()  # Seletores encadeados
first_quote = page.css('.quote')[0]
author = first_quote.css('.author::text').get()
next_quote = first_quote.next
parent_container = first_quote.parent

# Relações e similaridade entre elementos
similar_elements = first_quote.find_similar()
below_elements = first_quote.below_elements
```
Você pode usar o parser diretamente, sem obter uma página da web:
```python
from scrapling.parser import Selector

page = Selector("<html>...</html>")
```
Ele funciona da mesma forma.

### Exemplos de sessões assíncronas
```python
import asyncio
from scrapling.fetchers import FetcherSession, AsyncStealthySession

async def main():
    async with FetcherSession(http3=True) as http_session:  # `FetcherSession` se adapta ao contexto e funciona tanto com sync quanto com async
        page1 = await http_session.get('https://quotes.toscrape.com/')
        page2 = await http_session.get('https://quotes.toscrape.com/page/2/', impersonate='chrome')
        print(len(page1.css('.quote')), len(page2.css('.quote')))

    async with AsyncStealthySession(max_pages=2) as browser_session:
        urls = ['https://quotes.toscrape.com/js/', 'https://quotes.toscrape.com/js/page/2/']
        pages = await asyncio.gather(*(browser_session.fetch(url, wait_selector='.quote') for url in urls))
        print([len(page.css('.quote')) for page in pages])

asyncio.run(main())
```

## CLI e shell interativo

Você também pode usar o Scrapling pelo terminal:

[![asciicast](https://asciinema.org/a/736339.svg)](https://asciinema.org/a/736339)

Inicie o shell interativo de web scraping:
```bash
pip install "scrapling[shell]"
scrapling shell
```
Extraia páginas diretamente para um arquivo sem programar. Use `--css-selector` para escolher o conteúdo ou `--ai-targeted` para selecionar e limpar o conteúdo de `body`. Use `.txt` para texto, `.md` para Markdown ou `.html` para HTML.
```bash
scrapling extract get 'https://quotes.toscrape.com/' quotes.md
scrapling extract get 'https://quotes.toscrape.com/' quotes.txt --css-selector '.quote' --impersonate 'chrome'
scrapling extract fetch 'https://quotes.toscrape.com/js/' quotes.md --css-selector '.quote' --wait-selector '.quote' --no-headless
scrapling extract fetch 'https://nopecha.com/demo/cloudflare' captchas.html --css-selector '#padded_content a' --solve-cloudflare
```

> [!NOTE]
> Veja mais recursos, incluindo o servidor MCP e o shell interativo, na [documentação completa](https://scrapling.readthedocs.io/pt-br/latest/).

## Testes de desempenho

Scrapling também se destaca pela velocidade. Estes testes comparam seu parser com as versões mais recentes de outras bibliotecas conhecidas.

### Velocidade de extração de texto (5.000 elementos aninhados)

| # |    Biblioteca     | Tempo (ms) | Comparação com Scrapling |
|---|:-----------------:|:----------:|:------------:|
| 1 |     Scrapling     |    1,99    |     1,0x     |
| 2 |   Parsel/Scrapy   |    2,06    |     1,035    |
| 3 |     Lxml puro      |    2,56    |    1,286     |
| 4 |      PyQuery      |   23,98    |     ~12x     |
| 5 |    Selectolax     |   197,02   |     ~99x     |
| 6 |  MechanicalSoup   |  1545,15   |   ~776,5x    |
| 7 |   BS4 com Lxml   |   1562,1   |   ~785,0x    |
| 8 | BS4 com html5lib |  3412,73   |   ~1714,9x   |


### Desempenho da busca de elementos semelhantes e de texto

A busca adaptativa de elementos do Scrapling é mais rápida que as alternativas:

| Biblioteca  | Tempo (ms) | Comparação com Scrapling |
|-------------|:----------:|:------------:|
| Scrapling   |    2,3     |     1,0x     |
| AutoScraper |   12,58    |    5,47x     |


> Cada resultado é a média de pelo menos 100 execuções. Veja o método em [benchmarks.py](https://github.com/D4Vinci/Scrapling/blob/main/benchmarks.py).

## Instalação

Scrapling requer Python 3.10 ou mais recente:

```bash
pip install scrapling
```

> [!IMPORTANT]
> Este comando instala apenas o parser e suas dependências, sem fetchers ou ferramentas de linha de comando. Se você instalar apenas isso, importar de `scrapling.fetchers` ou `scrapling.spiders`, como nos exemplos anteriores, gera `ModuleNotFoundError`. Para usar fetchers ou spiders, instale primeiro as dependências dos fetchers, como mostrado a seguir.

### Dependências opcionais

1. Para usar os fetchers, suas classes ou os recursos adicionais a seguir, instale as dependências dos fetchers e dos navegadores:
    ```bash
    pip install "scrapling[fetchers]"
    
    scrapling install           # instalação normal
    scrapling install  --force  # forçar reinstalação
    ```

    Isso baixa todos os navegadores, as dependências do sistema e as ferramentas para alterar as impressões digitais do navegador.

    Você também pode instalar pelo Python, em vez de executar um comando:
    ```python
    from scrapling.cli import install
    
    install([], standalone_mode=False)          # instalação normal
    install(["--force"], standalone_mode=False) # forçar reinstalação
    ```

2. Recursos adicionais:
   - Instalar o servidor MCP:
       ```bash
       pip install "scrapling[ai]"
       ```
   - Instalar as dependências para [criar sistemas RAG](https://scrapling.readthedocs.io/pt-br/latest/ai/building-rag-systems.html):
       ```bash
       pip install "scrapling[rag]"
       ```
   - Instalar o shell interativo e o comando `extract`:
       ```bash
       pip install "scrapling[shell]"
       ```
   - Instalar tudo:
       ```bash
       pip install "scrapling[all]"
       ```
   Execute `scrapling install` para usar fetchers de navegador. Solicitações HTTP não precisam de um navegador.

### Docker
Você também pode baixar do DockerHub uma imagem Docker com todos os extras e navegadores:
```bash
docker pull pyd4vinci/scrapling
```
Ou baixar pelo registro do GitHub:
```bash
docker pull ghcr.io/d4vinci/scrapling:latest
```
A imagem é criada a partir da branch principal do repositório e publicada automaticamente pelo GitHub Actions.

## Como contribuir

Contribuições são bem-vindas! Leia nossas [diretrizes de contribuição](https://github.com/D4Vinci/Scrapling/blob/main/CONTRIBUTING.md) antes de começar.

## Aviso legal

> [!CAUTION]
> Esta biblioteca é apenas para ensino e pesquisa. Ao usá-la, você concorda em cumprir as leis locais e internacionais de extração de dados e privacidade. Os autores e colaboradores não se responsabilizam pelo uso indevido deste software. Respeite os termos de serviço dos sites e os arquivos robots.txt.

## 🎓 Citações
Se você usou esta biblioteca em sua pesquisa, cite-a com esta referência:
```text
  @misc{scrapling,
    author = {Karim Shoair},
    title = {Scrapling},
    year = {2024},
    url = {https://github.com/D4Vinci/Scrapling},
    note = {A Python Web Scraping framework for everything from a single request to a full-scale crawl!}
  }
```

## Licença

Este projeto usa a licença BSD-3-Clause.

## Agradecimentos

Este projeto inclui código adaptado de:
- Parsel (Licença BSD) - usado para o submódulo [translator](https://github.com/D4Vinci/Scrapling/blob/main/scrapling/core/translator.py)

---
<div align="center"><small>Projetado e desenvolvido com ❤️ por Karim Shoair.</small></div><br>
