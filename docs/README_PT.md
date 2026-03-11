<!-- mcp-name: io.github.D4Vinci/Scrapling -->

<h1 align="center">
    <a href="https://scrapling.readthedocs.io">
        <picture>
          <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/docs/assets/cover_dark.svg?sanitize=true">
          <img alt="Scrapling Poster" src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/docs/assets/cover_light.svg?sanitize=true">
        </picture>
    </a>
    <br>
    <small>Effortless Web Scraping for the Modern Web</small>
</h1>

<p align="center">
    <a href="https://github.com/D4Vinci/Scrapling/actions/workflows/tests.yml" alt="Tests">
        <img alt="Tests" src="https://github.com/D4Vinci/Scrapling/actions/workflows/tests.yml/badge.svg"></a>
    <a href="https://badge.fury.io/py/Scrapling" alt="PyPI version">
        <img alt="PyPI version" src="https://badge.fury.io/py/Scrapling.svg"></a>
    <a href="https://clickpy.clickhouse.com/dashboard/scrapling" rel="nofollow"><img src="https://img.shields.io/pypi/dm/scrapling" alt="PyPI package downloads"></a>
    <a href="https://github.com/D4Vinci/Scrapling/tree/main/agent-skill" alt="AI Agent Skill directory">
        <img alt="Static Badge" src="https://img.shields.io/badge/Skill-black?style=flat&label=Agent&link=https%3A%2F%2Fgithub.com%2FD4Vinci%2FScrapling%2Ftree%2Fmain%2Fagent-skill"></a>
    <a href="https://clawhub.ai/D4Vinci/scrapling-official" alt="OpenClaw Skill">
        <img alt="OpenClaw Skill" src="https://img.shields.io/badge/Clawhub-darkred?style=flat&label=OpenClaw&link=https%3A%2F%2Fclawhub.ai%2FD4Vinci%2Fscrapling-official"></a>
    <br/>
    <a href="https://discord.gg/EMgGbDceNQ" alt="Discord" target="_blank">
      <img alt="Discord" src="https://img.shields.io/discord/1360786381042880532?style=social&logo=discord&link=https%3A%2F%2Fdiscord.gg%2FEMgGbDceNQ">
    </a>
    <a href="https://x.com/Scrapling_dev" alt="X (formerly Twitter)">
      <img alt="X (formerly Twitter) Follow" src="https://img.shields.io/twitter/follow/Scrapling_dev?style=social&logo=x&link=https%3A%2F%2Fx.com%2FScrapling_dev">
    </a>
    <br/>
    <a href="https://pypi.org/project/scrapling/" alt="Supported Python versions">
        <img alt="Supported Python versions" src="https://img.shields.io/pypi/pyversions/scrapling.svg"></a>
</p>

<p align="center">
    <a href="https://scrapling.readthedocs.io/en/latest/parsing/selection/"><strong>Métodos de seleção</strong></a>
    &middot;
    <a href="https://scrapling.readthedocs.io/en/latest/fetching/choosing/"><strong>Escolher um fetcher</strong></a>
    &middot;
    <a href="https://scrapling.readthedocs.io/en/latest/spiders/architecture.html"><strong>Spiders</strong></a>
    &middot;
    <a href="https://scrapling.readthedocs.io/en/latest/spiders/proxy-blocking.html"><strong>Rotação de proxy</strong></a>
    &middot;
    <a href="https://scrapling.readthedocs.io/en/latest/cli/overview/"><strong>CLI</strong></a>
    &middot;
    <a href="https://scrapling.readthedocs.io/en/latest/ai/mcp-server/"><strong>Modo MCP</strong></a>
</p>

Scrapling é um framework de Web Scraping adaptativo que cuida de tudo, desde uma única solicitação até um rastreamento em grande escala.

O seu parser aprende com as mudanças dos sites e relocaliza automaticamente os seus elementos quando as páginas são atualizadas. Os seus fetchers contornam sistemas anti-bot como o Cloudflare Turnstile de forma nativa. E o seu framework Spider permite-lhe escalar para rastreamentos concorrentes com múltiplas sessões, com Pause & Resume e rotação automática de Proxy, tudo em poucas linhas de Python. Uma biblioteca, zero compromissos.

Rastreamentos ultrarrápidos com estatísticas em tempo real e Streaming. Construído por Web Scrapers para Web Scrapers e utilizadores regulares, há algo para todos.

```python
from scrapling.fetchers import Fetcher, AsyncFetcher, StealthyFetcher, DynamicFetcher
StealthyFetcher.adaptive = True
p = StealthyFetcher.fetch('https://example.com', headless=True, network_idle=True)  # Obtém o site sob o radar!
products = p.css('.product', auto_save=True)                                        # Extrai dados que sobrevivem a mudanças de design do site!
products = p.css('.product', adaptive=True)                                         # Depois, se a estrutura do site mudar, passa `adaptive=True` para encontrá-los!
```
Ou escala para rastreamentos completos
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

<p align="center">
    <a href="https://dataimpulse.com/?utm_source=scrapling&utm_medium=banner&utm_campaign=scrapling" target="_blank" style="display:flex; justify-content:center; padding:4px 0;">
        <img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/DataImpulse.png" alt="At DataImpulse, we specialize in developing custom proxy services for your business. Make requests from anywhere, collect data, and enjoy fast connections with our premium proxies." style="max-height:60px;">
    </a>
</p>

# Patrocinadores Platina
<table>
  <tr>
    <td width="200">
      <a href="https://hypersolutions.co/?utm_source=github&utm_medium=readme&utm_campaign=scrapling" target="_blank" title="Bot Protection Bypass API for Akamai, DataDome, Incapsula & Kasada">
        <img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/HyperSolutions.png">
        <br />
      </a>
    </td>
    <td> Scrapling lida com o Cloudflare Turnstile. Para proteção de nível empresarial, <a href="https://hypersolutions.co?utm_source=github&utm_medium=readme&utm_campaign=scrapling">
        <b>Hyper Solutions</b>
      </a> fornece endpoints API que geram tokens antibot válidos para <b>Akamai</b>, <b>DataDome</b>, <b>Kasada</b> e <b>Incapsula</b>. Simples chamadas API, sem automação de navegador. </td>
  </tr>
  <tr>
    <td width="200">
      <a href="https://birdproxies.com/t/scrapling" target="_blank" title="At Bird Proxies, we eliminate your pains such as banned IPs, geo restriction, and high costs so you can focus on your work.">
        <img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/BirdProxies.jpg">
        <br />
      </a>
    </td>
    <td>Olá, criámos o <a href="https://birdproxies.com/t/scrapling">
        <b>BirdProxies</b>
      </a> porque os proxies não deveriam ser complicados nem caros. <br /> Proxies residenciais e ISP rápidos em mais de 195 localizações, preços justos e suporte real. <br />
      <b>Experimenta o nosso jogo FlappyBird na página inicial para obteres dados grátis!</b>
    </td>
  </tr>
  <tr>
    <td width="200">
      <a href="https://evomi.com?utm_source=github&utm_medium=banner&utm_campaign=d4vinci-scrapling" target="_blank" title="Evomi is your Swiss Quality Proxy Provider, starting at $0.49/GB">
        <img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/evomi.png">
        <br />
      </a>
    </td>
    <td>
      <a href="https://evomi.com?utm_source=github&utm_medium=banner&utm_campaign=d4vinci-scrapling">
        <b>Evomi</b>
      </a>: proxies residenciais a partir de 0,49 $/GB. Navegador de scraping com Chromium totalmente falsificado, IPs residenciais, resolução automática de CAPTCHA e evasão anti-bot. </br>
      <b>API Scraper para resultados sem complicações. Integrações MCP e N8N disponíveis.</b>
    </td>
  </tr>
  <tr>
    <td width="200">
      <a href="https://tikhub.io/?ref=KarimShoair" target="_blank" title="Unlock the Power of Social Media Data & AI">
        <img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/TikHub.jpg">
        <br />
      </a>
    </td>
    <td>
      <a href="https://tikhub.io/?ref=KarimShoair" target="_blank">TikHub.io</a> oferece mais de 900 APIs estáveis em mais de 16 plataformas, incluindo TikTok, X, YouTube e Instagram, com mais de 40M de conjuntos de dados. <br /> Também oferece <a href="https://ai.tikhub.io/?ref=KarimShoair" target="_blank">modelos de IA com desconto</a> — Claude, GPT, GEMINI e mais com até 71% de desconto.
    </td>
  </tr>
  <tr>
    <td width="200">
      <a href="https://www.nsocks.com/?keyword=2p67aivg" target="_blank" title="Scalable Web Data Access for AI Applications">
        <img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/nsocks.png">
        <br />
      </a>
    </td>
    <td>
    <a href="https://www.nsocks.com/?keyword=2p67aivg" target="_blank">Nsocks</a> oferece proxies residenciais e ISP rápidos para programadores e scrapers. Cobertura IP global, alto anonimato, rotação inteligente e desempenho fiável para automação e extração de dados. Usa <a href="https://www.xcrawl.com/?keyword=2p67aivg" target="_blank">Xcrawl</a> para simplificar o crawling web a grande escala.
    </td>
  </tr>
</table>

<i><sub>Queres mostrar o teu anúncio aqui? Clica [aqui](https://github.com/sponsors/D4Vinci/sponsorships?tier_id=586646)</sub></i>
# Patrocinadores

<!-- sponsors -->

<a href="https://petrosky.io/d4vinci" target="_blank" title="PetroSky delivers cutting-edge VPS hosting."><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/petrosky.png"></a>

<a href="https://serpapi.com/?utm_source=scrapling" target="_blank" title="Scrape Google and other search engines with SerpApi"><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/SerpApi.png"></a>
<a href="https://visit.decodo.com/Dy6W0b" target="_blank" title="Try the Most Efficient Residential Proxies for Free"><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/decodo.png"></a>
<a href="https://hasdata.com/?utm_source=github&utm_medium=banner&utm_campaign=D4Vinci" target="_blank" title="The web scraping service that actually beats anti-bot systems!"><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/hasdata.png"></a>
<a href="https://proxyempire.io/?ref=scrapling&utm_source=scrapling" target="_blank" title="Collect The Data Your Project Needs with the Best Residential Proxies"><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/ProxyEmpire.png"></a><a href="https://www.swiftproxy.net/" target="_blank" title="Unlock Reliable Proxy Services with Swiftproxy!"><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/swiftproxy.png"></a>
<a href="https://www.rapidproxy.io/?ref=d4v" target="_blank" title="Affordable Access to the Proxy World – bypass CAPTCHAs blocks, and avoid additional costs."><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/rapidproxy.jpg"></a>
<a href="https://browser.cash/?utm_source=D4Vinci&utm_medium=referral" target="_blank" title="Browser Automation & AI Browser Agent Platform"><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/browserCash.png"></a>

<!-- /sponsors -->

<i><sub>Queres mostrar o teu anúncio aqui? Clica [aqui](https://github.com/sponsors/D4Vinci) e escolhe o nível que te convier!</sub></i>

---

## Características Principais

### Spiders — Um Framework Completo de Rastreamento
- 🕷️ **API de Spider ao estilo Scrapy**: Define spiders com `start_urls`, callbacks async `parse`, e objetos `Request`/`Response`.
- ⚡ **Rastreamento Concorrente**: Limites de concorrência configuráveis, limitação por domínio e atrasos de download.
- 🔄 **Suporte Multi-Session**: Interface unificada para solicitações HTTP e navegadores headless sigilosos num único Spider — encaminha solicitações para diferentes sessões por ID.
- 💾 **Pause & Resume**: Persistência de rastreamento baseada em Checkpoint. Pressiona Ctrl+C para um encerramento ordenado; reinicia para continuar de onde paraste.
- 📡 **Modo Streaming**: Transmite itens extraídos à medida que chegam com `async for item in spider.stream()` com estatísticas em tempo real — ideal para UI, pipelines e rastreamentos de longa duração.
- 🛡️ **Deteção de Solicitações Bloqueadas**: Deteção automática e nova tentativa de solicitações bloqueadas com lógica personalizável.
- 📦 **Exportação Integrada**: Exporta resultados através de hooks e o teu próprio pipeline ou o JSON/JSONL integrado com `result.items.to_json()` / `result.items.to_jsonl()` respetivamente.

### Obtenção Avançada de Sites com Suporte de Session
- **Solicitações HTTP**: Solicitações HTTP rápidas e sigilosas com a classe `Fetcher`. Pode imitar o fingerprint TLS dos navegadores, cabeçalhos e usar HTTP/3.
- **Carregamento Dinâmico**: Obtém sites dinâmicos com automação completa do navegador através da classe `DynamicFetcher` compatível com Chromium do Playwright e Google Chrome.
- **Evasão Anti-bot**: Capacidades de sigilo avançadas com `StealthyFetcher` e falsificação de fingerprint. Pode contornar facilmente todos os tipos de Turnstile/Interstitial do Cloudflare com automação.
- **Gestão de Session**: Suporte de sessão persistente com as classes `FetcherSession`, `StealthySession` e `DynamicSession` para a gestão de cookies e estado entre solicitações.
- **Rotação de Proxy**: `ProxyRotator` integrado com estratégias de rotação cíclica ou personalizadas em todos os tipos de sessão, além de substituições de Proxy por solicitação.
- **Bloqueio de Domínios**: Bloqueia solicitações a domínios específicos (e os seus subdomínios) em fetchers baseados em navegador.
- **Suporte Async**: Suporte async completo em todos os fetchers e classes de sessão async dedicadas.

### Scraping Adaptativo e Integração com IA
- 🔄 **Seguimento Inteligente de Elementos**: Relocaliza elementos após mudanças no site usando algoritmos inteligentes de similaridade.
- 🎯 **Seleção Flexível Inteligente**: Seletores CSS, seletores XPath, pesquisa baseada em filtros, pesquisa de texto, pesquisa regex e mais.
- 🔍 **Encontrar Elementos Similares**: Localiza automaticamente elementos similares aos elementos encontrados.
- 🤖 **Servidor MCP para usar com IA**: Servidor MCP integrado para Web Scraping assistido por IA e extração de dados. O servidor MCP apresenta capacidades poderosas e personalizadas que aproveitam o Scrapling para extrair conteúdo específico antes de o passar à IA (Claude/Cursor/etc), acelerando assim as operações e reduzindo custos ao minimizar o uso de tokens. ([vídeo demo](https://www.youtube.com/watch?v=qyFk3ZNwOxE))

### Arquitetura de Alto Desempenho e Testada em Batalha
- 🚀 **Ultrarrápido**: Desempenho otimizado que supera a maioria das bibliotecas de Web Scraping de Python.
- 🔋 **Eficiente em Memória**: Estruturas de dados otimizadas e carregamento diferido para uma pegada de memória mínima.
- ⚡ **Serialização JSON Rápida**: 10 vezes mais rápido que a biblioteca padrão.
- 🏗️ **Testado em batalha**: O Scrapling não só tem uma cobertura de testes de 92% e cobertura completa de type hints, como tem sido usado diariamente por centenas de Web Scrapers durante o último ano.

### Experiência Amigável para Programadores/Web Scrapers
- 🎯 **Shell Interativo de Web Scraping**: Shell IPython integrado opcional com integração do Scrapling, atalhos e novas ferramentas para acelerar o desenvolvimento de scripts de Web Scraping, como converter solicitações curl em solicitações Scrapling e ver resultados de solicitações no teu navegador.
- 🚀 **Usa-o diretamente a partir do Terminal**: Opcionalmente, podes usar o Scrapling para fazer scraping de um URL sem escrever uma única linha de código!
- 🛠️ **API de Navegação Rica**: Percurso avançado do DOM com métodos de navegação de pais, irmãos e filhos.
- 🧬 **Processamento de Texto Melhorado**: Métodos integrados de regex, limpeza e operações de string otimizadas.
- 📝 **Geração Automática de Seletores**: Gera seletores CSS/XPath robustos para qualquer elemento.
- 🔌 **API Familiar**: Similar ao Scrapy/BeautifulSoup com os mesmos pseudo-elementos usados no Scrapy/Parsel.
- 📘 **Cobertura Completa de Tipos**: Type hints completos para excelente suporte de IDE e autocompletação de código. Todo o código-fonte é automaticamente analisado com **PyRight** e **MyPy** em cada alteração.
- 🔋 **Imagem Docker Pronta**: Com cada lançamento, é construída e publicada automaticamente uma imagem Docker que contém todos os navegadores.

## Primeiros Passos

Aqui tens um resumo rápido do que o Scrapling pode fazer sem entrar em profundidade.

### Uso Básico
Solicitações HTTP com suporte de sessão
```python
from scrapling.fetchers import Fetcher, FetcherSession

with FetcherSession(impersonate='chrome') as session:  # Usa a última versão do fingerprint TLS do Chrome
    page = session.get('https://quotes.toscrape.com/', stealthy_headers=True)
    quotes = page.css('.quote .text::text').getall()

# Ou usa solicitações de uma única vez
page = Fetcher.get('https://quotes.toscrape.com/')
quotes = page.css('.quote .text::text').getall()
```
Modo sigiloso avançado
```python
from scrapling.fetchers import StealthyFetcher, StealthySession

with StealthySession(headless=True, solve_cloudflare=True) as session:  # Mantém o navegador aberto até terminares
    page = session.fetch('https://nopecha.com/demo/cloudflare', google_search=False)
    data = page.css('#padded_content a').getall()

# Ou usa o estilo de solicitação de uma única vez, abre o navegador para esta solicitação, depois fecha-o ao terminar
page = StealthyFetcher.fetch('https://nopecha.com/demo/cloudflare')
data = page.css('#padded_content a').getall()
```
Automação completa do navegador
```python
from scrapling.fetchers import DynamicFetcher, DynamicSession

with DynamicSession(headless=True, disable_resources=False, network_idle=True) as session:  # Mantém o navegador aberto até terminares
    page = session.fetch('https://quotes.toscrape.com/', load_dom=False)
    data = page.xpath('//span[@class="text"]/text()').getall()  # Seletor XPath se preferires

# Ou usa o estilo de solicitação de uma única vez, abre o navegador para esta solicitação, depois fecha-o ao terminar
page = DynamicFetcher.fetch('https://quotes.toscrape.com/')
data = page.css('.quote .text::text').getall()
```

### Spiders
Constrói rastreadores completos com solicitações concorrentes, múltiplos tipos de sessão e Pause & Resume:
```python
from scrapling.spiders import Spider, Request, Response

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
print(f"Foram extraídas {len(result.items)} citações")
result.items.to_json("quotes.json")
```
Usa múltiplos tipos de sessão num único Spider:
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
            # Encaminha as páginas protegidas através da sessão sigilosa
            if "protected" in link:
                yield Request(link, sid="stealth")
            else:
                yield Request(link, sid="fast", callback=self.parse)  # callback explícito
```
Pausa e retoma rastreamentos longos com checkpoints executando o Spider assim:
```python
QuotesSpider(crawldir="./crawl_data").start()
```
Pressiona Ctrl+C para pausar de forma ordenada — o progresso é guardado automaticamente. Depois, quando iniciares o Spider novamente, passa o mesmo `crawldir`, e este continuará de onde parou.

### Análise Avançada e Navegação
```python
from scrapling.fetchers import Fetcher

# Seleção rica de elementos e navegação
page = Fetcher.get('https://quotes.toscrape.com/')

# Obtém citações com múltiplos métodos de seleção
quotes = page.css('.quote')  # Seletor CSS
quotes = page.xpath('//div[@class="quote"]')  # XPath
quotes = page.find_all('div', {'class': 'quote'})  # Estilo BeautifulSoup
# Igual a
quotes = page.find_all('div', class_='quote')
quotes = page.find_all(['div'], class_='quote')
quotes = page.find_all(class_='quote')  # e assim por diante...
# Encontra elementos por conteúdo de texto
quotes = page.find_by_text('quote', tag='div')

# Navegação avançada
quote_text = page.css('.quote')[0].css('.text::text').get()
quote_text = page.css('.quote').css('.text::text').getall()  # Seletores encadeados
first_quote = page.css('.quote')[0]
author = first_quote.next_sibling.css('.author::text')
parent_container = first_quote.parent

# Relações e similaridade de elementos
similar_elements = first_quote.find_similar()
below_elements = first_quote.below_elements()
```
Podes usar o parser diretamente se não precisares de obter sites, como mostrado abaixo:
```python
from scrapling.parser import Selector

page = Selector("<html>...</html>")
```
E funciona exatamente da mesma forma!

### Exemplos de Gestão de Session Async
```python
import asyncio
from scrapling.fetchers import FetcherSession, AsyncStealthySession, AsyncDynamicSession

async with FetcherSession(http3=True) as session:  # `FetcherSession` é consciente do contexto e pode funcionar tanto em padrões sync/async
    page1 = session.get('https://quotes.toscrape.com/')
    page2 = session.get('https://quotes.toscrape.com/', impersonate='firefox135')

# Uso de sessão async
async with AsyncStealthySession(max_pages=2) as session:
    tasks = []
    urls = ['https://example.com/page1', 'https://example.com/page2']

    for url in urls:
        task = session.fetch(url)
        tasks.append(task)

    print(session.get_pool_stats())  # Opcional - O estado do pool de separadores do navegador (ocupado/livre/erro)
    results = await asyncio.gather(*tasks)
    print(session.get_pool_stats())
```

## CLI e Shell Interativo

Scrapling inclui uma poderosa interface de linha de comandos:

[![asciicast](https://asciinema.org/a/736339.svg)](https://asciinema.org/a/736339)

Lançar o Shell interativo de Web Scraping
```bash
scrapling shell
```
Extrair páginas para um ficheiro diretamente sem programar (Extrai o conteúdo dentro da tag `body` por defeito). Se o ficheiro de saída terminar com `.txt`, então será extraído o conteúdo de texto do alvo. Se terminar com `.md`, será uma representação Markdown do conteúdo HTML; se terminar com `.html`, será o conteúdo HTML em si.
```bash
scrapling extract get 'https://example.com' content.md
scrapling extract get 'https://example.com' content.txt --css-selector '#fromSkipToProducts' --impersonate 'chrome'  # Todos os elementos que coincidem com o seletor CSS '#fromSkipToProducts'
scrapling extract fetch 'https://example.com' content.md --css-selector '#fromSkipToProducts' --no-headless
scrapling extract stealthy-fetch 'https://nopecha.com/demo/cloudflare' captchas.html --css-selector '#padded_content a' --solve-cloudflare
```

> [!NOTE]
> Existem muitas características adicionais, mas queremos manter esta página concisa, incluindo o servidor MCP e o Shell Interativo de Web Scraping. Consulta a documentação completa [aqui](https://scrapling.readthedocs.io/en/latest/)

## Benchmarks de Desempenho

O Scrapling não é apenas potente, também é ultrarrápido. Os seguintes benchmarks comparam o parser do Scrapling com as últimas versões de outras bibliotecas populares.

### Teste de Velocidade de Extração de Texto (5000 elementos aninhados)

| # |    Biblioteca     | Tempo (ms) | vs Scrapling |
|---|:-----------------:|:----------:|:------------:|
| 1 |     Scrapling     |    2.02    |     1.0x     |
| 2 |   Parsel/Scrapy   |    2.04    |     1.01     |
| 3 |     Raw Lxml      |    2.54    |    1.257     |
| 4 |      PyQuery      |   24.17    |     ~12x     |
| 5 |    Selectolax     |   82.63    |     ~41x     |
| 6 |  MechanicalSoup   |  1549.71   |   ~767.1x    |
| 7 |   BS4 with Lxml   |  1584.31   |   ~784.3x    |
| 8 | BS4 with html5lib |  3391.91   |   ~1679.1x   |


### Desempenho de Similaridade de Elementos e Pesquisa de Texto

As capacidades de pesquisa adaptativa de elementos do Scrapling superam significativamente as alternativas:

| Biblioteca  | Tempo (ms) | vs Scrapling |
|-------------|:----------:|:------------:|
| Scrapling   |    2.39    |     1.0x     |
| AutoScraper |   12.45    |    5.209x    |


> Todos os benchmarks representam médias de mais de 100 execuções. Ver [benchmarks.py](https://github.com/D4Vinci/Scrapling/blob/main/benchmarks.py) para a metodologia.

## Instalação

O Scrapling requer Python 3.10 ou superior:

```bash
pip install scrapling
```

Esta instalação inclui apenas o motor de análise e as suas dependências, sem nenhum fetcher nem dependências de linha de comandos.

### Dependências Opcionais

1. Se vais usar alguma das características adicionais abaixo, os fetchers, ou as suas classes, precisarás de instalar as dependências dos fetchers e as suas dependências do navegador da seguinte forma:
    ```bash
    pip install "scrapling[fetchers]"

    scrapling install           # instalação normal
    scrapling install  --force  # reinstalação forçada
    ```

    Isto descarrega todos os navegadores, juntamente com as suas dependências do sistema e dependências de manipulação de fingerprint.

    Ou podes instalá-los a partir do código em vez de executar um comando:
    ```python
    from scrapling.cli import install

    install([], standalone_mode=False)          # instalação normal
    install(["--force"], standalone_mode=False) # reinstalação forçada
    ```

2. Características adicionais:
   - Instalar a característica do servidor MCP:
       ```bash
       pip install "scrapling[ai]"
       ```
   - Instalar características do Shell (Shell de Web Scraping e o comando `extract`):
       ```bash
       pip install "scrapling[shell]"
       ```
   - Instalar tudo:
       ```bash
       pip install "scrapling[all]"
       ```
   Lembra-te que precisas de instalar as dependências do navegador com `scrapling install` depois de qualquer um destes extras (se ainda não o fizeste)

### Docker
Também podes instalar uma imagem Docker com todos os extras e navegadores com o seguinte comando a partir do DockerHub:
```bash
docker pull pyd4vinci/scrapling
```
Ou descarrega-a a partir do registo do GitHub:
```bash
docker pull ghcr.io/d4vinci/scrapling:latest
```
Esta imagem é construída e publicada automaticamente usando GitHub Actions e o branch principal do repositório.

## Contribuir

Damos as boas-vindas às contribuições! Por favor lê as nossas [diretrizes de contribuição](https://github.com/D4Vinci/Scrapling/blob/main/CONTRIBUTING.md) antes de começares.

## Aviso Legal

> [!CAUTION]
> Esta biblioteca é fornecida apenas para fins educativos e de investigação. Ao usar esta biblioteca, aceitas cumprir as leis locais e internacionais de scraping de dados e privacidade. Os autores e contribuidores não são responsáveis por qualquer uso indevido deste software. Respeita sempre os termos de serviço dos sites e os ficheiros robots.txt.

## 🎓 Citações
Se utilizaste a nossa biblioteca para fins de investigação, por favor cita-nos com a seguinte referência:
```text
  @misc{scrapling,
    author = {Karim Shoair},
    title = {Scrapling},
    year = {2024},
    url = {https://github.com/D4Vinci/Scrapling},
    note = {An adaptive Web Scraping framework that handles everything from a single request to a full-scale crawl!}
  }
```

## Licença

Este trabalho está licenciado sob a Licença BSD-3-Clause.

## Agradecimentos

Este projeto inclui código adaptado de:
- Parsel (Licença BSD)—Usado para o submódulo [translator](https://github.com/D4Vinci/Scrapling/blob/main/scrapling/core/translator.py)

---
<div align="center"><small>Desenhado e elaborado com ❤️ por Karim Shoair.</small></div><br>
