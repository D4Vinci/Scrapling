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
    <a href="https://scrapling.readthedocs.io/en/latest/parsing/selection/"><strong>Méthodes de sélection</strong></a>
    &middot;
    <a href="https://scrapling.readthedocs.io/en/latest/fetching/choosing/"><strong>Fetchers</strong></a>
    &middot;
    <a href="https://scrapling.readthedocs.io/en/latest/spiders/architecture.html"><strong>Spiders</strong></a>
    &middot;
    <a href="https://scrapling.readthedocs.io/en/latest/spiders/proxy-blocking.html"><strong>Rotation de proxy</strong></a>
    &middot;
    <a href="https://scrapling.readthedocs.io/en/latest/cli/overview/"><strong>CLI</strong></a>
    &middot;
    <a href="https://scrapling.readthedocs.io/en/latest/ai/mcp-server/"><strong>MCP</strong></a>
</p>

Scrapling est un framework de Web Scraping adaptatif qui gère tout, d'une simple requête à un crawl à grande échelle.

Son parser apprend des modifications de sites web et relocalise automatiquement vos éléments lorsque les pages sont mises à jour. Ses fetchers contournent les systèmes anti-bot comme Cloudflare Turnstile nativement. Et son framework Spider vous permet de monter en charge vers des crawls concurrents multi-sessions avec pause/reprise et rotation automatique de proxy — le tout en quelques lignes de Python. Une seule bibliothèque, zéro compromis.

Des crawls ultra-rapides avec des statistiques en temps réel et du streaming. Conçu par des Web Scrapers pour des Web Scrapers et des utilisateurs réguliers, il y en a pour tout le monde.

```python
from scrapling.fetchers import Fetcher, AsyncFetcher, StealthyFetcher, DynamicFetcher
StealthyFetcher.adaptive = True
p = StealthyFetcher.fetch('https://example.com', headless=True, network_idle=True)  # Récupérer un site web en toute discrétion !
products = p.css('.product', auto_save=True)                                        # Scraper des données qui survivent aux changements de design !
products = p.css('.product', adaptive=True)                                         # Plus tard, si la structure du site change, passez `adaptive=True` pour les retrouver !
```
Ou montez en charge vers des crawls complets
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

# Sponsors Platine
<table>
  <tr>
    <td width="200">
      <a href="https://hypersolutions.co/?utm_source=github&utm_medium=readme&utm_campaign=scrapling" target="_blank" title="Bot Protection Bypass API for Akamai, DataDome, Incapsula & Kasada">
        <img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/HyperSolutions.png">
      </a>
    </td>
    <td> Scrapling gère Cloudflare Turnstile. Pour une protection de niveau entreprise, <a href="https://hypersolutions.co?utm_source=github&utm_medium=readme&utm_campaign=scrapling">
        <b>Hyper Solutions</b>
      </a> fournit des endpoints API qui génèrent des tokens antibot valides pour <b>Akamai</b>, <b>DataDome</b>, <b>Kasada</b> et <b>Incapsula</b>. De simples appels API, sans automatisation de navigateur. </td>
  </tr>
  <tr>
    <td width="200">
      <a href="https://birdproxies.com/t/scrapling" target="_blank" title="At Bird Proxies, we eliminate your pains such as banned IPs, geo restriction, and high costs so you can focus on your work.">
        <img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/BirdProxies.jpg">
      </a>
    </td>
    <td>Nous avons créé <a href="https://birdproxies.com/t/scrapling">
        <b>BirdProxies</b>
      </a> parce que les proxies ne devraient pas être compliqués ni trop chers. Des proxies résidentiels et ISP rapides dans plus de 195 localisations, des prix équitables et un vrai support. <br />
      <b>Essayez notre jeu FlappyBird sur la page d'accueil pour des données gratuites !</b>
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
      </a> : proxies résidentiels à partir de 0,49 $/Go. Navigateur de scraping avec Chromium entièrement falsifié, IPs résidentielles, résolution automatique de CAPTCHA et contournement anti-bot. </br>
      <b>API Scraper pour des résultats sans tracas. Intégrations MCP et N8N disponibles.</b>
    </td>
  </tr>
  <tr>
    <td width="200">
      <a href="https://tikhub.io/?ref=KarimShoair" target="_blank" title="Unlock the Power of Social Media Data & AI">
        <img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/TikHub.jpg">
      </a>
    </td>
    <td>
      <a href="https://tikhub.io/?ref=KarimShoair" target="_blank">TikHub.io</a> propose plus de 900 APIs stables sur plus de 16 plateformes, dont TikTok, X, YouTube et Instagram, avec plus de 40M de jeux de données. <br /> Propose également des <a href="https://ai.tikhub.io/?ref=KarimShoair" target="_blank">modèles IA à prix réduit</a> — Claude, GPT, GEMINI et plus, jusqu'à 71% de réduction.
    </td>
  </tr>
  <tr>
    <td width="200">
      <a href="https://www.nsocks.com/?keyword=2p67aivg" target="_blank" title="Scalable Web Data Access for AI Applications">
        <img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/nsocks.png">
      </a>
    </td>
    <td>
    <a href="https://www.nsocks.com/?keyword=2p67aivg" target="_blank">Nsocks</a> fournit des proxies résidentiels et ISP rapides pour les développeurs et les scrapeurs. Couverture IP mondiale, anonymat élevé, rotation intelligente et performances fiables pour l'automatisation et l'extraction de données. Utilisez <a href="https://www.xcrawl.com/?keyword=2p67aivg" target="_blank">Xcrawl</a> pour simplifier le crawling web à grande échelle.
    </td>
  </tr>
  <tr>
    <td width="200">
      <a href="https://petrosky.io/d4vinci" target="_blank" title="PetroSky delivers cutting-edge VPS hosting.">
        <img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/petrosky.png">
      </a>
    </td>
    <td>
    Fermez votre ordinateur. Vos scrapers continuent de tourner. <br />
    <a href="https://petrosky.io/d4vinci" target="_blank">PetroSky VPS</a> - des serveurs cloud conçus pour l'automatisation sans interruption. Machines Windows et Linux avec contrôle total. À partir de 6,99 €/mois.
    </td>
  </tr>
</table>

<i><sub>Vous souhaitez afficher votre publicité ici ? Cliquez [ici](https://github.com/sponsors/D4Vinci/sponsorships?tier_id=586646)</sub></i>
# Sponsors

<!-- sponsors -->

<a href="https://serpapi.com/?utm_source=scrapling" target="_blank" title="Scrape Google and other search engines with SerpApi"><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/SerpApi.png"></a>
<a href="https://visit.decodo.com/Dy6W0b" target="_blank" title="Try the Most Efficient Residential Proxies for Free"><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/decodo.png"></a>
<a href="https://hasdata.com/?utm_source=github&utm_medium=banner&utm_campaign=D4Vinci" target="_blank" title="The web scraping service that actually beats anti-bot systems!"><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/hasdata.png"></a>
<a href="https://proxyempire.io/?ref=scrapling&utm_source=scrapling" target="_blank" title="Collect The Data Your Project Needs with the Best Residential Proxies"><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/ProxyEmpire.png"></a><a href="https://www.swiftproxy.net/" target="_blank" title="Unlock Reliable Proxy Services with Swiftproxy!"><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/swiftproxy.png"></a>
<a href="https://www.rapidproxy.io/?ref=d4v" target="_blank" title="Affordable Access to the Proxy World – bypass CAPTCHAs blocks, and avoid additional costs."><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/rapidproxy.jpg"></a>
<a href="https://browser.cash/?utm_source=D4Vinci&utm_medium=referral" target="_blank" title="Browser Automation & AI Browser Agent Platform"><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/browserCash.png"></a>

<!-- /sponsors -->

<i><sub>Vous souhaitez afficher votre publicité ici ? Cliquez [ici](https://github.com/sponsors/D4Vinci) et choisissez le niveau qui vous convient !</sub></i>

---

## Fonctionnalités principales

### Spiders — Un framework de crawling complet
- 🕷️ **API Spider à la Scrapy** : Définissez des spiders avec `start_urls`, des callbacks async `parse` et des objets `Request`/`Response`.
- ⚡ **Crawling concurrent** : Limites de concurrence configurables, throttling par domaine et délais de téléchargement.
- 🔄 **Support multi-sessions** : Interface unifiée pour les requêtes HTTP et les navigateurs headless furtifs dans un seul spider — routez les requêtes vers différentes sessions par ID.
- 💾 **Pause & Reprise** : Persistance du crawl basée sur des checkpoints. Appuyez sur Ctrl+C pour un arrêt gracieux ; redémarrez pour reprendre là où vous vous étiez arrêté.
- 📡 **Mode streaming** : Diffusez les éléments scrapés en temps réel via `async for item in spider.stream()` avec des statistiques en temps réel — idéal pour les UI, pipelines et crawls de longue durée.
- 🛡️ **Détection des requêtes bloquées** : Détection automatique et réessai des requêtes bloquées avec une logique personnalisable.
- 📦 **Export intégré** : Exportez les résultats via des hooks et votre propre pipeline ou l'export JSON/JSONL intégré avec `result.items.to_json()` / `result.items.to_jsonl()` respectivement.

### Récupération avancée de sites web avec support de sessions
- **Requêtes HTTP** : Requêtes HTTP rapides et furtives avec la classe `Fetcher`. Peut imiter l'empreinte TLS des navigateurs, les headers et utiliser HTTP/3.
- **Chargement dynamique** : Récupérez des sites web dynamiques avec une automatisation complète du navigateur via la classe `DynamicFetcher` supportant Chromium de Playwright et Google Chrome.
- **Contournement anti-bot** : Capacités de furtivité avancées avec `StealthyFetcher` et usurpation d'empreinte. Peut facilement contourner tous les types de Turnstile/Interstitial de Cloudflare avec l'automatisation.
- **Gestion de sessions** : Support de sessions persistantes avec les classes `FetcherSession`, `StealthySession` et `DynamicSession` pour la gestion des cookies et de l'état entre les requêtes.
- **Rotation de proxy** : `ProxyRotator` intégré avec des stratégies de rotation cycliques ou personnalisées sur tous les types de sessions, plus des surcharges de proxy par requête.
- **Blocage de domaines** : Bloquez les requêtes vers des domaines spécifiques (et leurs sous-domaines) dans les fetchers basés sur navigateur.
- **Support async** : Support async complet sur tous les fetchers et classes de sessions async dédiées.

### Scraping adaptatif & Intégration IA
- 🔄 **Suivi intelligent des éléments** : Relocalisez les éléments après des modifications de site web en utilisant des algorithmes de similarité intelligents.
- 🎯 **Sélection flexible intelligente** : Sélecteurs CSS, sélecteurs XPath, recherche par filtres, recherche textuelle, recherche regex et plus encore.
- 🔍 **Trouver des éléments similaires** : Localisez automatiquement des éléments similaires aux éléments trouvés.
- 🤖 **Serveur MCP pour utilisation avec l'IA** : Serveur MCP intégré pour le Web Scraping et l'extraction de données assistés par IA. Le serveur MCP dispose de capacités puissantes et personnalisées qui exploitent Scrapling pour extraire du contenu ciblé avant de le transmettre à l'IA (Claude/Cursor/etc.), accélérant ainsi les opérations et réduisant les coûts en minimisant l'utilisation de tokens. ([vidéo de démonstration](https://www.youtube.com/watch?v=qyFk3ZNwOxE))

### Architecture haute performance et éprouvée
- 🚀 **Ultra rapide** : Performance optimisée surpassant la plupart des bibliothèques de scraping Python.
- 🔋 **Économe en mémoire** : Structures de données optimisées et chargement paresseux pour une empreinte mémoire minimale.
- ⚡ **Sérialisation JSON rapide** : 10x plus rapide que la bibliothèque standard.
- 🏗️ **Éprouvé en conditions réelles** : Non seulement Scrapling dispose d'une couverture de tests de 92% et d'une couverture complète des type hints, mais il est utilisé quotidiennement par des centaines de Web Scrapers depuis l'année dernière.

### Expérience conviviale pour développeurs/Web Scrapers
- 🎯 **Shell interactif de Web Scraping** : Shell IPython intégré optionnel avec intégration Scrapling, raccourcis et nouveaux outils pour accélérer le développement de scripts de Web Scraping, comme la conversion de requêtes curl en requêtes Scrapling et l'affichage des résultats dans votre navigateur.
- 🚀 **Utilisez-le directement depuis le terminal** : Optionnellement, vous pouvez utiliser Scrapling pour scraper une URL sans écrire une seule ligne de code !
- 🛠️ **API de navigation riche** : Traversée avancée du DOM avec des méthodes de navigation parent, frère et enfant.
- 🧬 **Traitement de texte amélioré** : Regex intégrées, méthodes de nettoyage et opérations sur les chaînes optimisées.
- 📝 **Génération automatique de sélecteurs** : Générez des sélecteurs CSS/XPath robustes pour n'importe quel élément.
- 🔌 **API familière** : Similaire à Scrapy/BeautifulSoup avec les mêmes pseudo-éléments utilisés dans Scrapy/Parsel.
- 📘 **Couverture de types complète** : Type hints complets pour un excellent support IDE et la complétion de code. L'ensemble de la base de code est automatiquement analysé avec **PyRight** et **MyPy** à chaque modification.
- 🔋 **Image Docker prête à l'emploi** : À chaque version, une image Docker contenant tous les navigateurs est automatiquement construite et publiée.

## Pour commencer

Voici un aperçu rapide de ce que Scrapling peut faire sans entrer dans les détails.

### Utilisation de base
Requêtes HTTP avec support de sessions
```python
from scrapling.fetchers import Fetcher, FetcherSession

with FetcherSession(impersonate='chrome') as session:  # Utiliser la dernière version de l'empreinte TLS de Chrome
    page = session.get('https://quotes.toscrape.com/', stealthy_headers=True)
    quotes = page.css('.quote .text::text').getall()

# Ou utiliser des requêtes ponctuelles
page = Fetcher.get('https://quotes.toscrape.com/')
quotes = page.css('.quote .text::text').getall()
```
Mode furtif avancé
```python
from scrapling.fetchers import StealthyFetcher, StealthySession

with StealthySession(headless=True, solve_cloudflare=True) as session:  # Garder le navigateur ouvert jusqu'à ce que vous ayez terminé
    page = session.fetch('https://nopecha.com/demo/cloudflare', google_search=False)
    data = page.css('#padded_content a').getall()

# Ou utiliser le style requête ponctuelle : ouvre le navigateur pour cette requête, puis le ferme après
page = StealthyFetcher.fetch('https://nopecha.com/demo/cloudflare')
data = page.css('#padded_content a').getall()
```
Automatisation complète du navigateur
```python
from scrapling.fetchers import DynamicFetcher, DynamicSession

with DynamicSession(headless=True, disable_resources=False, network_idle=True) as session:  # Garder le navigateur ouvert jusqu'à ce que vous ayez terminé
    page = session.fetch('https://quotes.toscrape.com/', load_dom=False)
    data = page.xpath('//span[@class="text"]/text()').getall()  # Sélecteur XPath si vous le préférez

# Ou utiliser le style requête ponctuelle : ouvre le navigateur pour cette requête, puis le ferme après
page = DynamicFetcher.fetch('https://quotes.toscrape.com/')
data = page.css('.quote .text::text').getall()
```

### Spiders
Construisez des crawlers complets avec des requêtes concurrentes, plusieurs types de sessions et pause/reprise :
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
print(f"{len(result.items)} citations scrapées")
result.items.to_json("quotes.json")
```
Utilisez plusieurs types de sessions dans un seul spider :
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
            # Router les pages protégées via la session furtive
            if "protected" in link:
                yield Request(link, sid="stealth")
            else:
                yield Request(link, sid="fast", callback=self.parse)  # Callback explicite
```
Mettez en pause et reprenez les longs crawls avec des checkpoints en lançant le spider ainsi :
```python
QuotesSpider(crawldir="./crawl_data").start()
```
Appuyez sur Ctrl+C pour mettre en pause gracieusement — la progression est sauvegardée automatiquement. Plus tard, lorsque vous relancez le spider, passez le même `crawldir`, et il reprendra là où il s'était arrêté.

### Parsing avancé & Navigation
```python
from scrapling.fetchers import Fetcher

# Sélection riche d'éléments et navigation
page = Fetcher.get('https://quotes.toscrape.com/')

# Obtenir des citations avec plusieurs méthodes de sélection
quotes = page.css('.quote')  # Sélecteur CSS
quotes = page.xpath('//div[@class="quote"]')  # XPath
quotes = page.find_all('div', {'class': 'quote'})  # Style BeautifulSoup
# Identique à
quotes = page.find_all('div', class_='quote')
quotes = page.find_all(['div'], class_='quote')
quotes = page.find_all(class_='quote')  # et ainsi de suite...
# Trouver un élément par contenu textuel
quotes = page.find_by_text('quote', tag='div')

# Navigation avancée
quote_text = page.css('.quote')[0].css('.text::text').get()
quote_text = page.css('.quote').css('.text::text').getall()  # Sélecteurs chaînés
first_quote = page.css('.quote')[0]
author = first_quote.next_sibling.css('.author::text')
parent_container = first_quote.parent

# Relations et similarité entre éléments
similar_elements = first_quote.find_similar()
below_elements = first_quote.below_elements()
```
Vous pouvez utiliser le parser directement si vous ne souhaitez pas récupérer de sites web, comme ci-dessous :
```python
from scrapling.parser import Selector

page = Selector("<html>...</html>")
```
Et cela fonctionne exactement de la même manière !

### Exemples de gestion de sessions async
```python
import asyncio
from scrapling.fetchers import FetcherSession, AsyncStealthySession, AsyncDynamicSession

async with FetcherSession(http3=True) as session:  # `FetcherSession` est sensible au contexte et peut fonctionner en mode sync comme async
    page1 = session.get('https://quotes.toscrape.com/')
    page2 = session.get('https://quotes.toscrape.com/', impersonate='firefox135')

# Utilisation de session async
async with AsyncStealthySession(max_pages=2) as session:
    tasks = []
    urls = ['https://example.com/page1', 'https://example.com/page2']

    for url in urls:
        task = session.fetch(url)
        tasks.append(task)

    print(session.get_pool_stats())  # Optionnel - Le statut du pool d'onglets du navigateur (occupé/libre/erreur)
    results = await asyncio.gather(*tasks)
    print(session.get_pool_stats())
```

## CLI & Shell interactif

Scrapling inclut une interface en ligne de commande puissante :

[![asciicast](https://asciinema.org/a/736339.svg)](https://asciinema.org/a/736339)

Lancer le shell interactif de Web Scraping
```bash
scrapling shell
```
Extraire des pages directement dans un fichier sans programmation (extrait par défaut le contenu de la balise `body`). Si le fichier de sortie se termine par `.txt`, le contenu textuel de la cible sera extrait. S'il se termine par `.md`, ce sera une représentation Markdown du contenu HTML ; s'il se termine par `.html`, ce sera le contenu HTML lui-même.
```bash
scrapling extract get 'https://example.com' content.md
scrapling extract get 'https://example.com' content.txt --css-selector '#fromSkipToProducts' --impersonate 'chrome'  # Tous les éléments correspondant au sélecteur CSS '#fromSkipToProducts'
scrapling extract fetch 'https://example.com' content.md --css-selector '#fromSkipToProducts' --no-headless
scrapling extract stealthy-fetch 'https://nopecha.com/demo/cloudflare' captchas.html --css-selector '#padded_content a' --solve-cloudflare
```

> [!NOTE]
> Il existe de nombreuses fonctionnalités supplémentaires, mais nous souhaitons garder cette page concise, y compris le serveur MCP et le shell interactif de Web Scraping. Consultez la documentation complète [ici](https://scrapling.readthedocs.io/en/latest/)

## Benchmarks de performance

Scrapling n'est pas seulement puissant — il est aussi ultra rapide. Les benchmarks suivants comparent le parser de Scrapling avec les dernières versions d'autres bibliothèques populaires.

### Test de vitesse d'extraction de texte (5000 éléments imbriqués)

| # |   Bibliothèque    | Temps (ms) | vs Scrapling |
|---|:-----------------:|:----------:|:------------:|
| 1 |     Scrapling     |    2.02    |     1.0x     |
| 2 |   Parsel/Scrapy   |    2.04    |     1.01     |
| 3 |     Raw Lxml      |    2.54    |    1.257     |
| 4 |      PyQuery      |   24.17    |     ~12x     |
| 5 |    Selectolax     |   82.63    |     ~41x     |
| 6 |  MechanicalSoup   |  1549.71   |   ~767.1x    |
| 7 |   BS4 with Lxml   |  1584.31   |   ~784.3x    |
| 8 | BS4 with html5lib |  3391.91   |   ~1679.1x   |


### Performance de similarité d'éléments & recherche textuelle

Les capacités adaptatives de recherche d'éléments de Scrapling surpassent significativement les alternatives :

| Bibliothèque | Temps (ms) | vs Scrapling |
|--------------|:----------:|:------------:|
| Scrapling    |    2.39    |     1.0x     |
| AutoScraper  |   12.45    |    5.209x    |


> Tous les benchmarks représentent des moyennes de plus de 100 exécutions. Voir [benchmarks.py](https://github.com/D4Vinci/Scrapling/blob/main/benchmarks.py) pour la méthodologie.

## Installation

Scrapling nécessite Python 3.10 ou supérieur :

```bash
pip install scrapling
```

Cette installation n'inclut que le moteur de parsing et ses dépendances, sans aucun fetcher ni dépendance en ligne de commande.

### Dépendances optionnelles

1. Si vous allez utiliser l'une des fonctionnalités supplémentaires ci-dessous, les fetchers ou leurs classes, vous devrez installer les dépendances des fetchers et leurs dépendances navigateur comme suit :
    ```bash
    pip install "scrapling[fetchers]"

    scrapling install           # installation normale
    scrapling install  --force  # réinstallation forcée
    ```

    Cela télécharge tous les navigateurs, ainsi que leurs dépendances système et les dépendances de manipulation d'empreintes.

    Ou vous pouvez les installer depuis le code au lieu d'exécuter une commande :
    ```python
    from scrapling.cli import install

    install([], standalone_mode=False)          # installation normale
    install(["--force"], standalone_mode=False) # réinstallation forcée
    ```

2. Fonctionnalités supplémentaires :
   - Installer la fonctionnalité serveur MCP :
       ```bash
       pip install "scrapling[ai]"
       ```
   - Installer les fonctionnalités shell (shell de Web Scraping et la commande `extract`) :
       ```bash
       pip install "scrapling[shell]"
       ```
   - Tout installer :
       ```bash
       pip install "scrapling[all]"
       ```
   N'oubliez pas que vous devez installer les dépendances navigateur avec `scrapling install` après l'un de ces extras (si vous ne l'avez pas déjà fait)

### Docker
Vous pouvez également installer une image Docker avec tous les extras et navigateurs avec la commande suivante depuis DockerHub :
```bash
docker pull pyd4vinci/scrapling
```
Ou téléchargez-la depuis le registre GitHub :
```bash
docker pull ghcr.io/d4vinci/scrapling:latest
```
Cette image est automatiquement construite et publiée en utilisant GitHub Actions et la branche principale du dépôt.

## Contribuer

Les contributions sont les bienvenues ! Veuillez lire nos [directives de contribution](https://github.com/D4Vinci/Scrapling/blob/main/CONTRIBUTING.md) avant de commencer.

## Avertissement

> [!CAUTION]
> Cette bibliothèque est fournie uniquement à des fins éducatives et de recherche. En utilisant cette bibliothèque, vous acceptez de vous conformer aux lois locales et internationales sur le scraping de données et la confidentialité. Les auteurs et contributeurs ne sont pas responsables de toute utilisation abusive de ce logiciel. Respectez toujours les conditions d'utilisation des sites web et les fichiers robots.txt.

## 🎓 Citations
Si vous avez utilisé notre bibliothèque à des fins de recherche, veuillez nous citer avec la référence suivante :
```text
  @misc{scrapling,
    author = {Karim Shoair},
    title = {Scrapling},
    year = {2024},
    url = {https://github.com/D4Vinci/Scrapling},
    note = {An adaptive Web Scraping framework that handles everything from a single request to a full-scale crawl!}
  }
```

## Licence

Ce travail est sous licence BSD-3-Clause.

## Remerciements

Ce projet inclut du code adapté de :
- Parsel (Licence BSD) — Utilisé pour le sous-module [translator](https://github.com/D4Vinci/Scrapling/blob/main/scrapling/core/translator.py)

---
<div align="center"><small>Conçu et développé avec ❤️ par Karim Shoair.</small></div><br>
