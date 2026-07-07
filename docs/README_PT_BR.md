<!-- mcp-name: io.github.D4Vinci/Scrapling -->

<h1 align="center">
    <a href="https://scrapling.readthedocs.io">
        <picture>
          <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/docs/assets/cover_dark.svg?sanitize=true">
          <img alt="Scrapling Poster" src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/docs/assets/cover_light.svg?sanitize=true">
        </picture>
    </a>
    <br>
    <small>Web Scraping sem esforço para a web moderna</small>
</h1>

<p align="center">
    <a href="https://trendshift.io/repositories/14244" target="_blank"><img src="https://trendshift.io/api/badge/repositories/14244" alt="D4Vinci%2FScrapling | Trendshift" style="width: 250px; height: 55px;" width="250" height="55"/></a>
    <br/>
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
    <a href="https://scrapling.readthedocs.io/en/latest/parsing/selection.html"><strong>Métodos de seleção</strong></a>
    &middot;
    <a href="https://scrapling.readthedocs.io/en/latest/fetching/choosing.html"><strong>Fetchers</strong></a>
    &middot;
    <a href="https://scrapling.readthedocs.io/en/latest/spiders/architecture.html"><strong>Spiders</strong></a>
    &middot;
    <a href="https://scrapling.readthedocs.io/en/latest/spiders/proxy-blocking.html"><strong>Rotação de proxy</strong></a>
    &middot;
    <a href="https://scrapling.readthedocs.io/en/latest/cli/overview.html"><strong>CLI</strong></a>
    &middot;
    <a href="https://scrapling.readthedocs.io/en/latest/ai/mcp-server.html"><strong>MCP</strong></a>
</p>

Scrapling é um framework adaptativo de Web Scraping que lida com tudo, desde uma única requisição até um crawl em larga escala.

Seu parser aprende com as mudanças nos sites e relocaliza automaticamente seus elementos quando as páginas são atualizadas. Seus fetchers contornam sistemas anti-bot como o Cloudflare Turnstile de forma nativa. E seu framework de spiders permite escalar para crawls concorrentes com múltiplas sessões, pausa/retomada e rotação automática de proxies, tudo em poucas linhas de Python. Uma biblioteca, zero concessões.

Crawls extremamente rápidos com estatísticas em tempo real e streaming. Feito por Web Scrapers para Web Scrapers e usuários comuns, há algo para todo mundo.

```python
from scrapling.fetchers import Fetcher, AsyncFetcher, StealthyFetcher, DynamicFetcher
StealthyFetcher.adaptive = True
p = StealthyFetcher.fetch('https://example.com', headless=True, network_idle=True)  # Busque o site sem chamar atenção!
products = p.css('.product', auto_save=True)                                        # Extraia dados que sobrevivem a mudanças no design do site!
products = p.css('.product', adaptive=True)                                         # Depois, se a estrutura do site mudar, passe `adaptive=True` para encontrá-los!
```
Ou escale para crawls completos
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
      <a href="https://proxidize.com/?utm_source=github&utm_medium=sponsorship&utm_campaign=scrapling&utm_content=d4vinci" target="_blank" title="Clean Proxies with No Nonsense.">
        <img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/proxidize.png">
      </a>
    </td>
    <td> A <a href="https://proxidize.com/?utm_source=github&utm_medium=sponsorship&utm_campaign=scrapling&utm_content=d4vinci" target="_blank"><b>Proxidize</b></a> oferece proxies móveis e residenciais para scraping, automação de navegador, monitoramento de SEO, agentes de IA e coleta de dados. <i>Use o código <b>scrapling20</b> para 20% de desconto</i>.
    </td>
  </tr>
  <tr>
    <td width="200">
      <a href="https://coldproxy.com/" target="_blank" title="Residential, IPv6 & Datacenter Proxies for Web Scraping">
        <img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/coldproxy.png">
      </a>
    </td>
    <td> A <a href="https://coldproxy.com/" target="_blank"><b>ColdProxy</b></a> oferece proxies residenciais e de datacenter para web scraping estável, coleta de dados públicos e testes com segmentação geográfica em mais de 195 países.
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
      <a href="https://birdproxies.com/t/scrapling" target="_blank" title="At Bird Proxies, we eliminate your pains such as banned IPs, geo restriction, and high costs so you can focus on your work.">
        <img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/BirdProxies.jpg">
      </a>
    </td>
    <td>Nós criamos a <a href="https://birdproxies.com/t/scrapling">
        <b>BirdProxies</b>
      </a> porque proxies não deveriam ser complicados nem caros. Proxies residenciais e ISP rápidos em mais de 195 localidades, preços justos e suporte de verdade. <br />
      <b>Experimente nosso jogo FlappyBird na landing page para ganhar dados grátis!</b>
    </td>
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
      </a>: proxies residenciais a partir de US$0.49/GB. Navegador de scraping com Chromium totalmente spoofado, IPs residenciais, resolução automática de CAPTCHA e bypass anti-bot. </br>
      <b>Scraper API para resultados sem complicação. Integrações com MCP e N8N estão disponíveis.</b>
    </td>
  </tr>
  <tr>
    <td width="200">
      <a href="https://tikhub.io/?utm_source=github.com/D4Vinci/Scrapling&utm_medium=marketing_social&utm_campaign=retargeting&utm_content=carousel_ad" target="_blank" title="Unlock the Power of Social Media Data & AI">
        <img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/TikHub.jpg">
      </a>
    </td>
    <td>
      <a href="https://tikhub.io/?utm_source=github.com/D4Vinci/Scrapling&utm_medium=marketing_social&utm_campaign=retargeting&utm_content=carousel_ad" target="_blank">TikHub.io</a> oferece mais de 900 APIs estáveis em mais de 16 plataformas, incluindo TikTok, X, YouTube e Instagram, com mais de 40M de datasets. <br /> Também oferece <a href="https://ai.tikhub.io/?ref=KarimShoair" target="_blank">modelos de IA com desconto</a> - Claude, GPT, GEMINI e mais com até 71% de desconto.
    </td>
  </tr>
  <tr>
    <td width="200">
      <a href="https://petrosky.io/d4vinci" target="_blank" title="PetroSky delivers cutting-edge VPS hosting.">
        <img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/petrosky.png">
      </a>
    </td>
    <td>
    Feche o notebook. Seus scrapers continuam rodando. <br />
    <a href="https://petrosky.io/d4vinci" target="_blank">PetroSky VPS</a> - servidores em nuvem feitos para automação ininterrupta. Máquinas Windows e Linux com controle total. A partir de €6.99/mês.
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
    <a href="https://www.swiftproxy.net/?ref=D4Vinci" target="_blank">Swiftproxy</a> fornece proxies residenciais escaláveis com mais de 80M de IPs em mais de 195 países, entregando conexões rápidas e confiáveis, rotação automática e forte desempenho anti-bloqueio. Teste grátis disponível.
    </td>
  </tr>
  <tr>
    <td width="200">
      <a href="https://go.nodemaven.com/scraplingjune" target="_blank" title="Proxies with the Highest IP Scores">
        <img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/NodeMaven.svg" width="240" height="100">
      </a>
    </td>
    <td>
    <a href="https://go.nodemaven.com/scraplingjune" target="_blank">NodeMaven</a> - provedor de proxies confiável com a mais alta qualidade de IP do mercado. Use o código promocional SCRAPLING35 para obter 35% de desconto em proxies.
    </td>
  </tr>
</table>

<i><sub>Quer mostrar seu anúncio aqui? Clique [aqui](https://github.com/sponsors/D4Vinci/sponsorships?tier_id=586646)</sub></i>
# Patrocinadores

<!-- sponsors -->

<a href="https://serpapi.com/?utm_source=scrapling" target="_blank" title="Scrape Google and other search engines with SerpApi"><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/SerpApi.png"></a>
<a href="https://visit.decodo.com/Dy6W0b" target="_blank" title="Try the Most Efficient Residential Proxies for Free"><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/decodo.png"></a>
<a href="https://hasdata.com/?utm_source=github&utm_medium=banner&utm_campaign=D4Vinci" target="_blank" title="The web scraping service that actually beats anti-bot systems!"><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/hasdata.png"></a>
<a href="https://proxyempire.io/?ref=scrapling&utm_source=scrapling" target="_blank" title="Collect The Data Your Project Needs with the Best Residential Proxies"><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/ProxyEmpire.png"></a>
<a href="https://www.webshare.io/?referral_code=48r2m2cd5uz1" target="_blank" title="The Most Reliable Proxy with Unparalleled Performance"><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/webshare.png"></a>
<a href="https://proxiware.com/?ref=scrapling" target="_blank" title="Collect Any Data. At Any Scale."><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/proxiware.png"></a>


<!-- /sponsors -->

<i><sub>Quer mostrar seu anúncio aqui? Clique [aqui](https://github.com/sponsors/D4Vinci) e escolha o plano que fizer mais sentido para você!</sub></i>

---

## Principais Recursos

### Spiders - Um Framework Completo de Crawling
- 🕷️ **API de Spider estilo Scrapy**: Defina spiders com `start_urls`, callbacks assíncronos `parse` e objetos `Request`/`Response`.
- ⚡ **Crawling Concorrente**: Limites de concorrência configuráveis, throttling por domínio e delays de download.
- 🔄 **Suporte Multi-Sessão**: Interface unificada para requisições HTTP e navegadores headless furtivos em uma única spider - direcione requisições para diferentes sessões por ID.
- 💾 **Pausa e Retomada**: Persistência de crawl baseada em checkpoints. Pressione Ctrl+C para um encerramento gracioso; reinicie para continuar de onde parou.
- 📡 **Modo Streaming**: Faça streaming dos itens extraídos conforme chegam com `async for item in spider.stream()` e estatísticas em tempo real - ideal para UI, pipelines e crawls de longa duração.
- 🛡️ **Detecção de Requisições Bloqueadas**: Detecção automática e retry de requisições bloqueadas com lógica personalizável.
- 🤖 **Conformidade com robots.txt**: Flag opcional `robots_txt_obey` que respeita as diretivas `Disallow`, `Crawl-delay` e `Request-rate` com cache por domínio.
- 🧪 **Modo de Desenvolvimento**: Armazene respostas em disco na primeira execução e reproduza-as nas seguintes - itere sobre sua lógica de `parse()` sem reenviar requisições aos servidores-alvo.
- 📦 **Exportação Nativa**: Exporte resultados via hooks, seu próprio pipeline ou JSON/JSONL nativos com `result.items.to_json()` / `result.items.to_jsonl()` respectivamente.

### Busca Avançada de Sites com Suporte a Sessões
- **Requisições HTTP**: Requisições HTTP rápidas e furtivas com a classe `Fetcher`. Pode imitar fingerprint TLS de navegadores, cabeçalhos e usar HTTP/3.
- **Carregamento Dinâmico**: Busque sites dinâmicos com automação completa de navegador através da classe `DynamicFetcher`, compatível com o Chromium do Playwright e o Google Chrome.
- **Bypass Anti-Bot**: Capacidades avançadas de stealth com `StealthyFetcher` e spoofing de fingerprint. Pode contornar facilmente todos os tipos de Turnstile/Interstitial do Cloudflare com automação.
- **Gerenciamento de Sessão**: Suporte a sessões persistentes com as classes `FetcherSession`, `StealthySession` e `DynamicSession` para gerenciar cookies e estado entre requisições.
- **Rotação de Proxy**: `ProxyRotator` nativo com estratégias cíclicas ou personalizadas em todos os tipos de sessão, além de sobrescritas de proxy por requisição.
- **Bloqueio de Domínios e Anúncios**: Bloqueie requisições para domínios específicos (e seus subdomínios) ou habilite o bloqueio nativo de anúncios (~3.500 domínios conhecidos de anúncios/rastreadores) nos fetchers baseados em navegador.
- **Prevenção de Vazamento de DNS**: Suporte opcional a DNS-over-HTTPS para rotear consultas DNS através do DoH da Cloudflare, evitando vazamentos de DNS ao usar proxies.
- **Suporte Async**: Suporte assíncrono completo em todos os fetchers e classes dedicadas de sessão async.

### Scraping Adaptativo e Integração com IA
- 🔄 **Rastreamento Inteligente de Elementos**: Relocalize elementos após mudanças no site usando algoritmos inteligentes de similaridade.
- 🎯 **Seleção Flexível Inteligente**: Seletores CSS, seletores XPath, busca baseada em filtros, busca por texto, busca por regex e muito mais.
- 🔍 **Encontrar Elementos Semelhantes**: Localize automaticamente elementos parecidos com os elementos encontrados.
- 🤖 **Servidor MCP para uso com IA**: Servidor MCP nativo para Web Scraping assistido por IA e extração de dados. O servidor MCP oferece capacidades poderosas e personalizadas que usam o Scrapling para extrair conteúdo direcionado antes de passá-lo à IA (Claude/Cursor/etc), acelerando as operações e reduzindo custos ao minimizar o uso de tokens. ([vídeo demo](https://www.youtube.com/watch?v=qyFk3ZNwOxE))

### Arquitetura de Alto Desempenho e Testada em Batalha
- 🚀 **Muito Rápido**: Desempenho otimizado que supera a maioria das bibliotecas Python de scraping.
- 🔋 **Eficiente em Memória**: Estruturas de dados otimizadas e lazy loading para um uso mínimo de memória.
- ⚡ **Serialização JSON Rápida**: 10x mais rápido que a biblioteca padrão.
- 🏗️ **Testado em batalha**: O Scrapling não apenas tem 92% de cobertura de testes e cobertura completa de type hints, como também vem sendo usado diariamente por centenas de Web Scrapers ao longo do último ano.

### Experiência Amigável para Desenvolvedores/Web Scrapers
- 🎯 **Shell Interativo de Web Scraping**: Shell opcional embutido em IPython com integração ao Scrapling, atalhos e novas ferramentas para acelerar o desenvolvimento de scripts de Web Scraping, como converter requisições curl em requisições Scrapling e visualizar resultados no navegador.
- 🚀 **Use diretamente no Terminal**: Opcionalmente, você pode usar o Scrapling para extrair uma URL sem escrever uma única linha de código!
- 🛠️ **API Rica de Navegação**: Travessia avançada do DOM com métodos de navegação por pais, irmãos e filhos.
- 🧬 **Processamento de Texto Aprimorado**: Métodos nativos de regex, limpeza e operações de string otimizadas.
- 📝 **Geração Automática de Seletores**: Gere seletores CSS/XPath robustos para qualquer elemento.
- 🔌 **API Familiar**: Semelhante a Scrapy/BeautifulSoup, com os mesmos pseudo-elementos usados em Scrapy/Parsel.
- 📘 **Cobertura Completa de Tipos**: Type hints completos para excelente suporte em IDEs e autocompletar de código. Todo o codebase é escaneado automaticamente com **PyRight** e **MyPy** a cada alteração.
- 🔋 **Imagem Docker Pronta**: A cada release, uma imagem Docker contendo todos os navegadores é construída e publicada automaticamente.

## Primeiros Passos

Vamos dar uma visão rápida do que o Scrapling pode fazer sem entrar em muitos detalhes.

### Uso Básico
Requisições HTTP com suporte a sessões
```python
from scrapling.fetchers import Fetcher, FetcherSession

with FetcherSession(impersonate='chrome') as session:  # Use a versão mais recente da fingerprint TLS do Chrome
    page = session.get('https://quotes.toscrape.com/', stealthy_headers=True)
    quotes = page.css('.quote .text::text').getall()

# Ou use requisições avulsas
page = Fetcher.get('https://quotes.toscrape.com/')
quotes = page.css('.quote .text::text').getall()
```
Modo stealth avançado
```python
from scrapling.fetchers import StealthyFetcher, StealthySession

with StealthySession(headless=True, solve_cloudflare=True) as session:  # Mantenha o navegador aberto até terminar
    page = session.fetch('https://nopecha.com/demo/cloudflare', google_search=False)
    data = page.css('#padded_content a').getall()

# Ou use o estilo de requisição avulsa, ele abre o navegador para esta requisição e o fecha ao finalizar
page = StealthyFetcher.fetch('https://nopecha.com/demo/cloudflare')
data = page.css('#padded_content a').getall()
```
Automação completa de navegador
```python
from scrapling.fetchers import DynamicFetcher, DynamicSession

with DynamicSession(headless=True, disable_resources=False, network_idle=True) as session:  # Mantenha o navegador aberto até terminar
    page = session.fetch('https://quotes.toscrape.com/', load_dom=False)
    data = page.xpath('//span[@class="text"]/text()').getall()  # Se preferir, use seletor XPath

# Ou use o estilo de requisição avulsa, ele abre o navegador para esta requisição e o fecha ao finalizar
page = DynamicFetcher.fetch('https://quotes.toscrape.com/')
data = page.css('.quote .text::text').getall()
```

### Spiders
Construa crawlers completos com requisições concorrentes, múltiplos tipos de sessão e pausa/retomada:
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
print(f"Extraídas {len(result.items)} citações")
result.items.to_json("quotes.json")
```
Use múltiplos tipos de sessão em uma única spider:
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
Pause e retome crawls longos com checkpoints executando a spider assim:
```python
QuotesSpider(crawldir="./crawl_data").start()
```
Pressione Ctrl+C para pausar de forma graciosa - o progresso é salvo automaticamente. Depois, quando você iniciar a spider novamente, passe o mesmo `crawldir` e ela continuará de onde parou.

### Parsing Avançado e Navegação
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
quotes = page.find_by_text('quote', tag='div')

# Navegação avançada
quote_text = page.css('.quote')[0].css('.text::text').get()
quote_text = page.css('.quote').css('.text::text').getall()  # Seletores encadeados
first_quote = page.css('.quote')[0]
author = first_quote.next_sibling.css('.author::text')
parent_container = first_quote.parent

# Relações e similaridade entre elementos
similar_elements = first_quote.find_similar()
below_elements = first_quote.below_elements()
```
Você pode usar o parser imediatamente se não quiser buscar sites, como abaixo:
```python
from scrapling.parser import Selector

page = Selector("<html>...</html>")
```
E ele funciona exatamente da mesma maneira!

### Exemplos de Gerenciamento de Sessão Assíncrona
```python
import asyncio
from scrapling.fetchers import FetcherSession, AsyncStealthySession, AsyncDynamicSession

async with FetcherSession(http3=True) as session:  # `FetcherSession` entende o contexto e funciona tanto em padrões sync quanto async
    page1 = session.get('https://quotes.toscrape.com/')
    page2 = session.get('https://quotes.toscrape.com/', impersonate='firefox135')

# Uso de sessão assíncrona
async with AsyncStealthySession(max_pages=2) as session:
    tasks = []
    urls = ['https://example.com/page1', 'https://example.com/page2']
    
    for url in urls:
        task = session.fetch(url)
        tasks.append(task)
    
    print(session.get_pool_stats())  # Opcional - O estado do pool de abas do navegador (ocupada/livre/erro)
    results = await asyncio.gather(*tasks)
    print(session.get_pool_stats())
```

## CLI e Shell Interativo

O Scrapling inclui uma poderosa interface de linha de comando:

[![asciicast](https://asciinema.org/a/736339.svg)](https://asciinema.org/a/736339)

Inicie o shell interativo de Web Scraping
```bash
scrapling shell
```
Extraia páginas diretamente para um arquivo sem programar (por padrão, extrai o conteúdo dentro da tag `body`). Se o arquivo de saída terminar com `.txt`, então o conteúdo em texto do alvo será extraído. Se terminar com `.md`, será uma representação em Markdown do conteúdo HTML; se terminar com `.html`, será o próprio conteúdo HTML.
```bash
scrapling extract get 'https://example.com' content.md
scrapling extract get 'https://example.com' content.txt --css-selector '#fromSkipToProducts' --impersonate 'chrome'  # Todos os elementos que correspondem ao seletor CSS '#fromSkipToProducts'
scrapling extract fetch 'https://example.com' content.md --css-selector '#fromSkipToProducts' --no-headless
scrapling extract stealthy-fetch 'https://nopecha.com/demo/cloudflare' captchas.html --css-selector '#padded_content a' --solve-cloudflare
```

> [!NOTE]
> Existem muitos recursos adicionais, mas queremos manter esta página concisa, incluindo o servidor MCP e o Shell Interativo de Web Scraping. Confira a documentação completa [aqui](https://scrapling.readthedocs.io/en/latest/)

## Benchmarks de Desempenho

O Scrapling não é apenas poderoso - ele também é extremamente rápido. Os benchmarks abaixo comparam o parser do Scrapling com as versões mais recentes de outras bibliotecas populares.

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


### Desempenho de Similaridade de Elementos e Busca por Texto

Os recursos de localização adaptativa de elementos do Scrapling superam significativamente as alternativas:

| Biblioteca  | Tempo (ms) | vs Scrapling |
|-------------|:----------:|:------------:|
| Scrapling   |    2.39    |     1.0x     |
| AutoScraper |   12.45    |    5.209x    |


> Todos os benchmarks representam médias de 100+ execuções. Veja [benchmarks.py](https://github.com/D4Vinci/Scrapling/blob/main/benchmarks.py) para a metodologia.

## Instalação

O Scrapling requer Python 3.10 ou superior:

```bash
pip install scrapling
```

> [!IMPORTANT]
> Esta instalação inclui apenas o motor de parsing e suas dependências, sem fetchers nem dependências de linha de comando. Portanto, importar qualquer coisa de `scrapling.fetchers` ou `scrapling.spiders`, como nos exemplos acima, lançará um `ModuleNotFoundError` apenas com esta instalação. Se você for usar algum dos fetchers ou spiders, instale primeiro as dependências dos fetchers como mostrado abaixo.

### Dependências Opcionais

1. Se você vai usar qualquer um dos recursos extras abaixo, os fetchers ou suas classes, precisará instalar as dependências dos fetchers e as dependências de navegador deles da seguinte forma:
    ```bash
    pip install "scrapling[fetchers]"
    
    scrapling install           # instalação normal
    scrapling install  --force  # forçar reinstalação
    ```

    Isso baixa todos os navegadores, juntamente com suas dependências de sistema e dependências de manipulação de fingerprint.

    Ou você pode instalá-los a partir do código em vez de executar um comando como este:
    ```python
    from scrapling.cli import install
    
    install([], standalone_mode=False)          # instalação normal
    install(["--force"], standalone_mode=False) # forçar reinstalação
    ```

2. Recursos extras:
   - Instale o recurso do servidor MCP:
       ```bash
       pip install "scrapling[ai]"
       ```
   - Instale os recursos do shell (Shell de Web Scraping e o comando `extract`):
       ```bash
       pip install "scrapling[shell]"
       ```
   - Instale tudo:
       ```bash
       pip install "scrapling[all]"
       ```
   Lembre-se de que você precisa instalar as dependências de navegador com `scrapling install` depois de qualquer um desses extras (caso ainda não tenha feito isso)

### Docker
Você também pode baixar uma imagem Docker com todos os extras e navegadores com o seguinte comando a partir do DockerHub:
```bash
docker pull pyd4vinci/scrapling
```
Ou baixá-la do registro do GitHub:
```bash
docker pull ghcr.io/d4vinci/scrapling:latest
```
Essa imagem é construída e publicada automaticamente usando GitHub Actions e o branch principal do repositório.

## Contribuindo

Contribuições são bem-vindas! Leia nossas [diretrizes de contribuição](https://github.com/D4Vinci/Scrapling/blob/main/CONTRIBUTING.md) antes de começar.

## Aviso Legal

> [!CAUTION]
> Esta biblioteca é fornecida apenas para fins educacionais e de pesquisa. Ao usar esta biblioteca, você concorda em cumprir as leis locais e internacionais de scraping de dados e privacidade. Os autores e contribuidores não se responsabilizam por qualquer uso indevido deste software. Sempre respeite os termos de serviço dos sites e os arquivos robots.txt.

## 🎓 Citações
Se você usou nossa biblioteca para fins de pesquisa, cite-nos com a seguinte referência:
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

Este trabalho está licenciado sob a licença BSD-3-Clause.

## Agradecimentos

Este projeto inclui código adaptado de:
- Parsel (Licença BSD) - usado para o submódulo [translator](https://github.com/D4Vinci/Scrapling/blob/main/scrapling/core/translator.py)

---
<div align="center"><small>Projetado e desenvolvido com ❤️ por Karim Shoair.</small></div><br>
