<!-- mcp-name: io.github.D4Vinci/Scrapling -->

<h1 align="center">
    <a href="https://scrapling.readthedocs.io/fr/latest/">
        <picture>
          <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/docs/assets/cover_dark.svg?sanitize=true">
          <img alt="Couverture de Scrapling" src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/docs/assets/cover_light.svg?sanitize=true">
        </picture>
    </a>
    <br>
    <small>Extrayez simplement les données du web moderne</small>
</h1>

<p align="center">
    <a href="https://github.com/D4Vinci/Scrapling/actions/workflows/tests.yml" alt="Tests">
        <img alt="Tests" src="https://github.com/D4Vinci/Scrapling/actions/workflows/tests.yml/badge.svg"></a>
    <a href="https://badge.fury.io/py/Scrapling" alt="Version sur PyPI">
        <img alt="Version sur PyPI" src="https://badge.fury.io/py/Scrapling.svg"></a>
    <a href="https://hub.docker.com/r/pyd4vinci/scrapling" target="_blank">
        <img alt="Téléchargements Docker" src="https://img.shields.io/docker/pulls/pyd4vinci/scrapling?labelColor=%20%23FDB062&logo=Docker&labelColor=%20%23528bff"></a>
    <a href="https://clickpy.clickhouse.com/dashboard/scrapling" rel="nofollow"><img src="https://img.shields.io/pypi/dm/scrapling" alt="Téléchargements du paquet sur PyPI"></a>
    <a href="https://scrapling.readthedocs.io/fr/latest/ai/agent-skill.html" alt="Skill pour agents IA">
        <img alt="Badge Agent Skill" src="https://img.shields.io/badge/Skill-black?style=flat&label=Agent&link=https%3A%2F%2Fscrapling.readthedocs.io%2Ffr%2Flatest%2Fai%2Fagent-skill.html"></a>
    <a href="https://clawhub.ai/D4Vinci/scrapling-official" alt="Skill pour OpenClaw">
        <img alt="Skill pour OpenClaw" src="https://img.shields.io/badge/Clawhub-darkred?style=flat&label=OpenClaw&link=https%3A%2F%2Fclawhub.ai%2FD4Vinci%2Fscrapling-official"></a>
    <br/>
    <a href="https://discord.gg/EMgGbDceNQ" alt="Discord" target="_blank">
      <img alt="Discord" src="https://img.shields.io/discord/1360786381042880532?style=social&logo=discord&link=https%3A%2F%2Fdiscord.gg%2FEMgGbDceNQ">
    </a>
    <a href="https://x.com/Scrapling_dev" alt="X (anciennement Twitter)">
      <img alt="Suivre sur X (anciennement Twitter)" src="https://img.shields.io/twitter/follow/Scrapling_dev?style=social&logo=x&link=https%3A%2F%2Fx.com%2FScrapling_dev">
    </a>
    <br/>
    <a href="https://pypi.org/project/scrapling/" alt="Versions de Python compatibles">
        <img alt="Versions de Python compatibles" src="https://img.shields.io/pypi/pyversions/scrapling.svg"></a>
</p>

<p align="center">
    <a href="https://scrapling.readthedocs.io/fr/latest/parsing/selection.html"><strong>Méthodes de sélection</strong></a>
    &middot;
    <a href="https://scrapling.readthedocs.io/fr/latest/fetching/choosing.html"><strong>Fetchers</strong></a>
    &middot;
    <a href="https://scrapling.readthedocs.io/fr/latest/spiders/architecture.html"><strong>Spiders</strong></a>
    &middot;
    <a href="https://scrapling.readthedocs.io/fr/latest/spiders/proxy-blocking.html"><strong>Rotation des proxies</strong></a>
    &middot;
    <a href="https://scrapling.readthedocs.io/fr/latest/cli/overview.html"><strong>CLI</strong></a>
    &middot;
    <a href="https://scrapling.readthedocs.io/fr/latest/ai/mcp-server.html"><strong>MCP</strong></a>
</p>

Scrapling est un framework de web scraping pour Python. Il réunit des requêtes HTTP rapides, des navigateurs furtifs, l’analyse de pages et l’exploration simultanée de sites dans une seule bibliothèque.

Extrayez les données de pages statiques, exécutez JavaScript, interagissez avec les sites et accédez aux API qu’ils utilisent. Créez des crawlers avec des sessions réutilisables, la rotation des proxies, de nouvelles tentatives automatiques, la pause et la reprise, et des exports intégrés.

Utilisez Scrapling depuis Python, le terminal ou votre agent IA grâce au serveur MCP et à l’Agent Skill. Il couvre tout le processus, de l’extraction de quelques champs à l’enregistrement d’un site entier en fichiers Markdown propres.

## Ce que vous pouvez faire avec Scrapling

- **[Récupérer des pages et interagir](https://scrapling.readthedocs.io/fr/latest/fetching/choosing.html)** : Requêtes HTTP rapides, navigateurs furtifs, exécution de JavaScript, gestion de Cloudflare Turnstile et Interstitial, sessions persistantes et capture des réponses des API en arrière-plan.
- **[Analyser et extraire](https://scrapling.readthedocs.io/fr/latest/parsing/selection.html)** : Recherche par CSS, XPath, texte et expressions régulières, suivi des éléments après un changement de page, recherche d’éléments similaires et sortie en Markdown propre.
- **[Explorer et exporter](https://scrapling.readthedocs.io/fr/latest/spiders/getting-started.html)** : Spiders simultanés, rotation des proxies, nouvelles tentatives, AutoThrottle, pause et reprise, résultats en streaming, modèles prêts à l’emploi et exports en JSON, JSONL, CSV et XML.
- **[Extraire avec l’IA ou depuis le terminal](https://scrapling.readthedocs.io/fr/latest/ai/mcp-server.html)** : Un serveur MCP pour que les agents IA naviguent et extraient des données, une Agent Skill, des commandes CLI et un shell interactif.

Commencez par une seule page :

```python
from scrapling.fetchers import Fetcher

page = Fetcher.get('https://quotes.toscrape.com/')
quotes = page.css('.quote .text::text').getall()
print(quotes)
```

Ou extrayez plus de données avec un spider :

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

Cet exemple affiche `10` et enregistre les citations et leurs auteurs dans `quotes.json`.

<p align="center">
    <a href="https://dataimpulse.com/?utm_source=scrapling&utm_medium=banner&utm_campaign=scrapling" target="_blank" style="display:flex; justify-content:center; padding:4px 0;">
        <img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/DataImpulse.png" alt="At DataImpulse, we specialize in developing custom proxy services for your business. Make requests from anywhere, collect data, and enjoy fast connections with our premium proxies." style="max-height:60px;">
    </a>
</p>

# Sponsors Platine
<table>
  <tr>
    <td width="200">
      <a href="https://go.nodemaven.com/scraplingoctober" target="_blank" title="Proxies with the Highest IP Scores">
        <img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/NodeMaven.jpg" width="240" height="100">
      </a>
    </td>
    <td>
    <a href="https://go.nodemaven.com/scraplingoctober" target="_blank">NodeMaven</a> - le fournisseur de proxys le plus efficace pour le Web Scraping et l'automatisation, avec la meilleure qualité d'IP du marché. Utilisez le code SCRAPLING35 pour obtenir 35 % de réduction.
    </td>
  </tr>
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
      <a href="https://evomi.com?utm_source=github&utm_medium=banner&utm_campaign=d4vinci-scrapling" target="_blank" title="Evomi is your Swiss Quality Proxy Provider, starting at $0.49/GB">
        <img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/evomi.png">
      </a>
    </td>
    <td>
      <a href="https://evomi.com?utm_source=github&utm_medium=banner&utm_campaign=d4vinci-scrapling">
        <b>Evomi</b>
      </a> : proxies résidentiels à partir de 0,49 $/Go. Navigateur de scraping avec Chromium dont l’empreinte est entièrement modifiée, IPs résidentielles, résolution automatique de CAPTCHA et contournement anti-bot. </br>
      <b>API Scraper pour des résultats sans tracas. Intégrations MCP et N8N disponibles.</b>
    </td>
  </tr>
  <tr>
    <td width="200">
      <a href="https://substack.thewebscraping.club/p/scrapling-hands-on-guide?utm_source=github&utm_medium=repo&utm_campaign=scrapling" target="_blank" title="The #1 newsletter dedicated to Web Scraping">
        <img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/TWSC.png">
      </a>
    </td>
    <td>
    Lisez une critique complète de <a href="https://substack.thewebscraping.club/p/scrapling-hands-on-guide?utm_source=github&utm_medium=repo&utm_campaign=scrapling" target="_blank">Scrapling sur The Web Scraping Club</a> (nov. 2025), la newsletter n°1 dédiée au Web Scraping.
    </td>
  </tr>
  <tr>
    <td width="200">
      <a href="https://www.swiftproxy.net/?ref=D4Vinci" target="_blank" title="Scalable Solutions for Web Data Access">
        <img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/SwiftProxy.png">
      </a>
    </td>
    <td>
    <a href="https://www.swiftproxy.net/?ref=D4Vinci" target="_blank">Swiftproxy</a> propose des proxys résidentiels évolutifs avec plus de 80 millions d'IPs dans plus de 195 pays, offrant des connexions rapides et fiables, une rotation automatique et des fonctions pour éviter les blocages. Essai gratuit disponible.
    </td>
  </tr>
  <tr>
    <td width="200">
      <a href="https://byteful.com/?utm_source=github&utm_medium=github-sponsor&utm_campaign=scrapling_github_sponsor" target="_blank" title="Ethically sourced residential proxy infrastructure powering web scraping and AI agents">
        <img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/byteful.png">
      </a>
    </td>
    <td>
    <a href="https://byteful.com/?utm_source=github&utm_medium=github-sponsor&utm_campaign=scrapling_github_sponsor" target="_blank">Byteful</a> fournit des proxys résidentiels, mobiles, ISP et de centres de données issus de sources éthiques, ainsi que des outils de scraping et d’automatisation par IA. Utilisez le code SCRAPLING10 pour obtenir 10 % de réduction sur les proxys résidentiels.
    </td>
  </tr>
  <tr>
    <td width="200">
      <a href="https://proxylane.dev/?utm_source=scrapling&utm_medium=partnership&utm_campaign=scrapling_platinum_202609&utm_content=github_readme" target="_blank" title="28M+ clean residential IPs for browser automation. No Blocks. No CAPTCHAs. Pay-as-you-Go.">
        <img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/proxylane.png">
      </a>
    </td>
    <td>
    <a href="https://proxylane.dev/?utm_source=scrapling&utm_medium=partnership&utm_campaign=scrapling_platinum_202609&utm_content=github_readme" target="_blank">ProxyLane</a> : Réduisez les blocages et les CAPTCHAs de 90 %. 28 millions d’adresses IP résidentielles premium pour le scraping web intensif. 195 pays. Ciblage par ville/ISP/code postal. Sessions fixes ou rotatives. Trafic sans expiration à partir de $2/GB. Code <strong>SCRAPEANDTAKE</strong> : <em>25 % de réduction</em>.
    </td>
  </tr>
  <tr>
    <td width="200">
      <a href="https://www.lundproxy.com/unlimited-residential-bandwidth.html?utm_source=github&utm_medium=sponsorship&utm_campaign=scrapling&utm_content=banner" target="_blank" title="Unlimited residential traffic, sized only by bandwidth.">
        <img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/lundproxy.png">
      </a>
    </td>
    <td>
    <a href="https://www.lundproxy.com?utm_source=github&utm_medium=sponsorship&utm_campaign=scrapling&utm_content=text" target="_blank">LundProxy</a> : Ne payez plus par GB. Trafic résidentiel illimité, plus de 100 millions d’IP, plus de 190 pays. Payez selon la bande passante. Demandez un essai gratuit de proxies résidentiels à 50 Mbps.
    </td>
  </tr>
  <tr>
    <td width="200">
      <a href="https://dataimpulse.com/?utm_source=website&utm_medium=github_readme&utm_campaign=scrapling_platinum" target="_blank" title="Buy Pay-as-you-go proxies from $1/GB">
        <img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/DataImpulse_Platinum.png">
      </a>
    </td>
    <td>
    $1/GB chez <a href="https://dataimpulse.com/?utm_source=website&utm_medium=github_readme&utm_campaign=scrapling_platinum" target="_blank">DataImpulse</a>. Proxies de première main issus de sources éthiques. Plus de 90 millions d’IP, plus de 195 pays. Résidentiels, de datacenter et mobiles. Paiement à l’usage = sans abonnement. Le trafic n’expire jamais.
    </td>
  </tr>
</table>

<i><sub>Vous souhaitez afficher votre publicité ici ? Cliquez [ici](https://github.com/sponsors/D4Vinci/sponsorships?tier_id=586646)</sub></i>
# Sponsors

<!-- sponsors -->

<a href="https://cloro.dev/?utm_source=referral&utm_medium=scrapling" target="_blank" title="The search API for the AI era"><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/cloro.jpg"></a>

<br/>

<a href="https://serpapi.com/?utm_source=scrapling" target="_blank" title="Scrape Google and other search engines with SerpApi"><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/SerpApi.png"></a>
<a href="https://visit.decodo.com/Dy6W0b" target="_blank" title="Try the Most Efficient Residential Proxies for Free"><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/decodo.png"></a>
<a href="https://proxyempire.io/?ref=scrapling&utm_source=github&utm_medium=paid_referral&utm_campaign=open_source_sponsorship&utm_content=scrapling" target="_blank" title="Collect The Data Your Project Needs with the Best Residential Proxies"><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/ProxyEmpire.png"></a>
<a href="https://www.webshare.io/?referral_code=48r2m2cd5uz1" target="_blank" title="The Most Reliable Proxy with Unparalleled Performance"><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/webshare.png"></a>
<a href="https://proxiware.com/?ref=scrapling" target="_blank" title="Collect Any Data. At Any Scale."><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/proxiware.png"></a>


<!-- /sponsors -->

<i><sub>Vous souhaitez afficher votre publicité ici ? Cliquez [ici](https://github.com/sponsors/D4Vinci) et choisissez le niveau qui vous convient !</sub></i>

---

## Fonctions principales

### Spiders : un framework complet d’exploration de sites

- 🕷️ **API de Spider proche de Scrapy** : Définissez des spiders avec `start_urls`, des callbacks `parse` asynchrones et des objets `Request` et `Response`.
- ⚡ **Exploration simultanée** : Réglez le nombre de requêtes simultanées, les limites par domaine et le délai entre les téléchargements.
- 🔄 **Plusieurs sessions** : Utilisez des requêtes HTTP et des navigateurs furtifs sans interface graphique dans le même spider. Dirigez les requêtes vers différentes sessions grâce à leur ID.
- 💾 **Pause et reprise** : Enregistrez les requêtes en attente et les URL visitées avec `crawldir`. Appuyez sur Ctrl+C pour arrêter proprement, puis relancez avec le même dossier.
- 📡 **Résultats en streaming** : Recevez les éléments dès leur extraction avec `async for item in spider.stream()`, avec des statistiques en temps réel. Utile pour les interfaces, les traitements de données et les explorations longues.
- 🛡️ **Détection des requêtes bloquées** : Détectez et relancez les requêtes bloquées automatiquement. Vous pouvez adapter ce comportement.
- 🚦 **AutoThrottle** : Le spider ajuste le délai de chaque domaine selon la vitesse de réponse du site. Si le site bloque ou limite les requêtes, il double le délai ou respecte la durée indiquée par `Retry-After`. Il accélère à nouveau quand la limitation prend fin.
- 🤖 **Respect de robots.txt** : Activez `robots_txt_obey` pour respecter les directives `Disallow`, `Crawl-delay` et `Request-rate`, avec un cache par domaine.
- 🧪 **Mode développement** : Enregistrez les réponses sur disque lors de la première exécution et réutilisez-les ensuite. Vous pouvez ainsi ajuster `parse()` sans envoyer de nouvelles requêtes aux serveurs.
- 🧩 **Modèles de spider prêts à l’emploi** : Utilisez `CrawlSpider` pour suivre les liens selon des règles, `SitemapSpider` pour explorer à partir de sitemaps ou de robots.txt, `XMLFeedSpider` et `CSVFeedSpider` pour lire des flux XML, RSS et CSV, et `ShopifySpider` pour collecter les produits des boutiques Shopify publiques, avec un élément par variante.
- 🔗 **Extraction de liens** : `LinkExtractor` permet d’accepter ou de refuser des liens selon des motifs, de filtrer les domaines et les extensions, de limiter la recherche avec CSS ou XPath et de normaliser les URL. Utilisez-le avec les modèles ou seul.
- 📦 **Export intégré** : Exportez les résultats avec des hooks et votre propre traitement de données, ou utilisez les formats JSON, JSONL, CSV et XML intégrés : `result.items.to_json()`, `to_jsonl()`, `to_csv()` et `to_xml()`.

### Récupération de pages avec des sessions

- **Requêtes HTTP** : Envoyez des requêtes HTTP rapides et furtives avec `Fetcher`. Vous pouvez imiter l’empreinte TLS et les en-têtes d’un navigateur, et utiliser HTTP/3.
- **Chargement dynamique** : Récupérez les sites dynamiques avec une automatisation complète du navigateur grâce à `StealthyFetcher`, compatible avec le Chromium de Playwright et Google Chrome.
- **Contournement des systèmes antibot** : `StealthyFetcher` masque l’automatisation et imite les empreintes du navigateur. Il peut franchir automatiquement les différents types de Cloudflare Turnstile et Interstitial.
- **Gestion des sessions** : `FetcherSession` et `StealthySession` conservent les cookies et l’état entre les requêtes.
- **Rotation des proxies** : `ProxyRotator` permet une rotation cyclique ou personnalisée dans tous les types de sessions. Vous pouvez aussi choisir un proxy pour une requête précise.
- **Blocage des domaines et des publicités** : Bloquez les requêtes vers certains domaines et leurs sous-domaines, ou activez le blocage des publicités des fetchers de navigateur. Il couvre environ 3 500 domaines connus de publicité et de suivi.
- **Prévention des fuites DNS** : Activez DNS-over-HTTPS pour envoyer les requêtes DNS par le service DoH de Cloudflare et éviter les fuites lorsque vous utilisez des proxies.
- **Navigateurs distants** : Connectez-vous par CDP à un navigateur déjà ouvert avec `cdp_url`, sur votre ordinateur, un autre serveur ou un service de navigateurs. Vous pouvez aussi utiliser votre propre version de Chromium avec tout fetcher de navigateur grâce à `executable_path`.
- **Capture des API en arrière-plan** : Activez `record_requests=True` dans une session de navigateur et cherchez les réponses enregistrées avec `session.network.search(limit=None)`. Lisez les données des API et les erreurs HTTP de plusieurs chargements sans répéter les requêtes. L’historique a une taille limitée et conserve le contenu des réponses textuelles.
- **Mode asynchrone** : Tous les fetchers peuvent fonctionner en mode asynchrone, avec des classes de session propres à ce mode.

### Analyse de pages et extraction de données

- 🔄 **Suivi des éléments** : Retrouvez les éléments après un changement du site grâce à des algorithmes de similarité.
- 🎯 **Sélection souple** : Utilisez CSS, XPath, les filtres, le texte, les expressions régulières et plus encore.
- 🔍 **Éléments similaires** : Trouvez automatiquement des éléments proches de ceux que vous avez déjà trouvés.

### Fonctions pour l’IA

- 🤖 **Serveur MCP** : Permet aux assistants et agents IA, comme Claude et Cursor, d’extraire des données avec Scrapling par des requêtes HTTP, des actions du navigateur, des captures d’écran, un état de connexion enregistré et des réponses d’API en arrière-plan. Il utilise notre navigateur furtif et des outils qui aident les modèles adaptés à résoudre les CAPTCHA, en plus du solveur Cloudflare. Il réduit le contenu envoyé au modèle, bloque les publicités et protège contre les injections de prompts. Il permet aussi d’utiliser des navigateurs distants par CDP et des connexions HTTP avec des options d’authentification. ([Vidéo de démonstration](https://www.youtube.com/watch?v=qyFk3ZNwOxE))
- 🧠 **Agent Skill** : Une [Agent Skill](https://scrapling.readthedocs.io/fr/latest/ai/agent-skill.html) prête à installer qui enseigne la bibliothèque aux agents de programmation pour qu’ils écrivent du code conforme à l’API actuelle.
- 📚 **Markdown prêt pour le RAG** : Convertissez une page en Markdown propre et adapté aux modèles de langage avec une ligne (`page.markdown()`), ou enregistrez un site entier en fichiers Markdown avec le modèle `ContentSpider`. Le processus ne demande aucun modèle de langage. ([Documentation](https://scrapling.readthedocs.io/fr/latest/ai/building-rag-systems.html))

### Performances et usage réel

- 🚀 **Grande vitesse** : Des performances optimisées qui dépassent la plupart des bibliothèques de web scraping pour Python.
- 🔋 **Faible usage de la mémoire** : Des structures de données optimisées et un chargement à la demande.
- ⚡ **Conversion rapide en JSON** : 10 fois plus rapide que la bibliothèque standard.
- 🏗️ **Testé en pratique** : Les tests couvrent 92 % de Scrapling et tout le code a des annotations de type. Des centaines de personnes l’ont utilisé chaque jour pour extraire des données pendant l’année passée.

### Outils pour développer et extraire des données

- 🎯 **Shell interactif** : Un shell IPython en option, intégré à Scrapling, avec des raccourcis et des outils pour créer des scripts plus vite. Convertissez les requêtes curl en requêtes Scrapling et consultez les résultats dans votre navigateur.
- 🚀 **Usage depuis le terminal** : Extrayez les données d’une URL sans écrire de code.
- 🛠️ **Navigation dans le DOM** : Accédez aux éléments parents, frères et enfants.
- 🧬 **Traitement du texte** : Expressions régulières, nettoyage du texte et opérations optimisées sur les chaînes.
- 📝 **Création de sélecteurs** : Générez des sélecteurs CSS et XPath fiables pour tout élément.
- 🔌 **API familière** : Proche de Scrapy et BeautifulSoup, avec les mêmes pseudo-éléments que Scrapy et Parsel.
- 🤝 **Intégration directe avec Scrapy** : Ajoutez le décorateur `scrapling_response` à un callback pour analyser les réponses que vous récupérez déjà avec le parser de Scrapling, sans réécrire votre programme.
- 📘 **Annotations de type complètes** : Elles aident l’éditeur à vérifier et à compléter le code. Tout le code est vérifié automatiquement par **PyRight** et **MyPy** à chaque changement.
- 🔋 **Image Docker prête à l’emploi** : Une image Docker avec tous les navigateurs est créée et publiée automatiquement à chaque version.

## Pour commencer

Voici quelques exemples de ce que vous pouvez faire avec Scrapling.

### Utilisation de base
Requêtes HTTP avec des sessions
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
page = StealthyFetcher.fetch('https://nopecha.com/demo/cloudflare', solve_cloudflare=True)
data = page.css('#padded_content a').getall()
```
Automatisation complète du navigateur
```python
from scrapling.fetchers import StealthyFetcher, StealthySession

with StealthySession(headless=True, disable_resources=False, network_idle=True) as session:  # Garder le navigateur ouvert jusqu'à ce que vous ayez terminé
    page = session.fetch('https://quotes.toscrape.com/', load_dom=False)
    data = page.xpath('//span[@class="text"]/text()').getall()  # Sélecteur XPath si vous le préférez

# Ou utiliser le style requête ponctuelle : ouvre le navigateur pour cette requête, puis le ferme après
page = StealthyFetcher.fetch('https://quotes.toscrape.com/')
data = page.css('.quote .text::text').getall()
```

### Spiders
Créez des crawlers complets avec des requêtes simultanées, plusieurs types de sessions, la pause et la reprise :
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
print(f"{len(result.items)} citations scrapées")
result.items.to_json("quotes.json")
```
Utilisez plusieurs types de sessions dans un seul spider :
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
Enregistrez la progression pour mettre en pause et reprendre les explorations longues. Lancez le spider ainsi :
```python
QuotesSpider(crawldir="./crawl_data").start()
```
Avec `crawldir`, Ctrl+C enregistre les requêtes en attente et les URL visitées. Relancez avec le même `crawldir` pour reprendre. Enregistrez les données extraites séparément.

Vous pouvez aussi utiliser un modèle prêt à l’emploi. Par exemple, récupérez tout le catalogue d’une boutique Shopify :
```python
from scrapling.spiders import ShopifySpider

class MyStore(ShopifySpider):
    target_website = "example.com"

result = MyStore().start()  # Tous les produits de la boutique, un élément par variante
```
Le modèle lit les produits disponibles sur les endpoints publics des collections, avec un élément par variante.

### Analyse avancée et navigation
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
quotes = page.find_by_text('Albert Einstein', first_match=False)

# Navigation avancée
quote_text = page.css('.quote')[0].css('.text::text').get()
quote_texts = page.css('.quote').css('.text::text').getall()  # Sélecteurs chaînés
first_quote = page.css('.quote')[0]
author = first_quote.css('.author::text').get()
next_quote = first_quote.next
parent_container = first_quote.parent

# Relations et similarité entre éléments
similar_elements = first_quote.find_similar()
below_elements = first_quote.below_elements
```
Vous pouvez utiliser le parser directement, sans récupérer de page web :
```python
from scrapling.parser import Selector

page = Selector("<html>...</html>")
```
Il fonctionne de la même façon.

### Exemples de sessions asynchrones
```python
import asyncio
from scrapling.fetchers import FetcherSession, AsyncStealthySession

async def main():
    async with FetcherSession(http3=True) as http_session:  # `FetcherSession` s'adapte au contexte et fonctionne en mode sync comme async
        page1 = await http_session.get('https://quotes.toscrape.com/')
        page2 = await http_session.get('https://quotes.toscrape.com/page/2/', impersonate='chrome')
        print(len(page1.css('.quote')), len(page2.css('.quote')))

    async with AsyncStealthySession(max_pages=2) as browser_session:
        urls = ['https://quotes.toscrape.com/js/', 'https://quotes.toscrape.com/js/page/2/']
        pages = await asyncio.gather(*(browser_session.fetch(url, wait_selector='.quote') for url in urls))
        print([len(page.css('.quote')) for page in pages])

asyncio.run(main())
```

## CLI et shell interactif

Vous pouvez aussi utiliser Scrapling depuis le terminal :

[![asciicast](https://asciinema.org/a/736339.svg)](https://asciinema.org/a/736339)

Lancez le shell interactif de web scraping :
```bash
pip install "scrapling[shell]"
scrapling shell
```
Extrayez des pages directement dans un fichier sans programmation. Utilisez `--css-selector` pour choisir le contenu ou `--ai-targeted` pour sélectionner et nettoyer le contenu de `body`. Utilisez `.txt` pour du texte, `.md` pour du Markdown ou `.html` pour du HTML.
```bash
scrapling extract get 'https://quotes.toscrape.com/' quotes.md
scrapling extract get 'https://quotes.toscrape.com/' quotes.txt --css-selector '.quote' --impersonate 'chrome'
scrapling extract fetch 'https://quotes.toscrape.com/js/' quotes.md --css-selector '.quote' --wait-selector '.quote' --no-headless
scrapling extract fetch 'https://nopecha.com/demo/cloudflare' captchas.html --css-selector '#padded_content a' --solve-cloudflare
```

> [!NOTE]
> Consultez les autres fonctions, dont le serveur MCP et le shell interactif, dans la [documentation complète](https://scrapling.readthedocs.io/fr/latest/).

## Tests de performance

Scrapling se distingue aussi par sa vitesse. Ces tests comparent son parser aux dernières versions d’autres bibliothèques connues.

### Vitesse d’extraction du texte (5 000 éléments imbriqués)

| # |   Bibliothèque    | Temps (ms) | Par rapport à Scrapling |
|---|:-----------------:|:----------:|:------------:|
| 1 |     Scrapling     |    1,99    |     1,0x     |
| 2 |   Parsel/Scrapy   |    2,06    |     1,035    |
| 3 |     Lxml seul      |    2,56    |    1,286     |
| 4 |      PyQuery      |   23,98    |     ~12x     |
| 5 |    Selectolax     |   197,02   |     ~99x     |
| 6 |  MechanicalSoup   |  1545,15   |   ~776,5x    |
| 7 |   BS4 avec Lxml   |  1562,1   |   ~785,0x    |
| 8 | BS4 avec html5lib |  3412,73   |   ~1714,9x   |


### Recherche d’éléments similaires et de texte

La recherche adaptative d’éléments de Scrapling est plus rapide que les autres solutions :

| Bibliothèque | Temps (ms) | Par rapport à Scrapling |
|--------------|:----------:|:------------:|
| Scrapling    |    2,3    |     1,0x     |
| AutoScraper  |   12,58    |    5,47x    |


> Chaque résultat est la moyenne d’au moins 100 exécutions. Consultez [benchmarks.py](https://github.com/D4Vinci/Scrapling/blob/main/benchmarks.py) pour connaître la méthode.

## Installation

Scrapling demande Python 3.10 ou une version plus récente :

```bash
pip install scrapling
```

> [!IMPORTANT]
> Cette commande installe seulement le parser et ses dépendances, sans fetchers ni outils en ligne de commande. Avec cette seule installation, importer depuis `scrapling.fetchers` ou `scrapling.spiders`, comme dans les exemples précédents, provoque `ModuleNotFoundError`. Pour utiliser les fetchers ou les spiders, installez d’abord les dépendances des fetchers comme indiqué ci-dessous.

### Dépendances facultatives

1. Pour utiliser les fetchers, leurs classes ou les fonctions supplémentaires suivantes, installez les dépendances des fetchers et des navigateurs :
    ```bash
    pip install "scrapling[fetchers]"

    scrapling install           # installation normale
    scrapling install  --force  # réinstallation forcée
    ```

    Cette commande télécharge tous les navigateurs, leurs dépendances système et les outils de modification des empreintes du navigateur.

    Vous pouvez aussi les installer depuis Python, au lieu de lancer une commande :
    ```python
    from scrapling.cli import install

    install([], standalone_mode=False)          # installation normale
    install(["--force"], standalone_mode=False) # réinstallation forcée
    ```

2. Fonctions supplémentaires :
   - Installer le serveur MCP :
       ```bash
       pip install "scrapling[ai]"
       ```
   - Installer les dépendances pour [créer des systèmes RAG](https://scrapling.readthedocs.io/fr/latest/ai/building-rag-systems.html) :
       ```bash
       pip install "scrapling[rag]"
       ```
   - Installer le shell interactif et la commande `extract` :
       ```bash
       pip install "scrapling[shell]"
       ```
   - Tout installer :
       ```bash
       pip install "scrapling[all]"
       ```
   Lancez `scrapling install` pour utiliser les fetchers de navigateur. Les requêtes HTTP ne demandent pas de navigateur.

### Docker
Vous pouvez aussi télécharger depuis DockerHub une image Docker avec tous les extras et navigateurs :
```bash
docker pull pyd4vinci/scrapling
```
Ou la télécharger depuis le registre GitHub :
```bash
docker pull ghcr.io/d4vinci/scrapling:latest
```
L’image est créée à partir de la branche principale du dépôt et publiée automatiquement par GitHub Actions.

## Contribuer

Les contributions sont les bienvenues ! Lisez nos [consignes de contribution](https://github.com/D4Vinci/Scrapling/blob/main/CONTRIBUTING.md) avant de commencer.

## Avertissement

> [!CAUTION]
> Cette bibliothèque est destinée à l’enseignement et à la recherche. En l’utilisant, vous acceptez de respecter les lois locales et internationales sur l’extraction de données et la vie privée. Les auteurs et contributeurs ne sont pas responsables d’un usage abusif de ce logiciel. Respectez les conditions d’utilisation des sites et les fichiers robots.txt.

## 🎓 Citations
Si vous avez utilisé cette bibliothèque dans vos recherches, citez-la avec cette référence :
```text
  @misc{scrapling,
    author = {Karim Shoair},
    title = {Scrapling},
    year = {2024},
    url = {https://github.com/D4Vinci/Scrapling},
    note = {A Python Web Scraping framework for everything from a single request to a full-scale crawl!}
  }
```

## Licence

Ce projet utilise la licence BSD-3-Clause.

## Remerciements

Ce projet inclut du code adapté de :
- Parsel (Licence BSD) - Utilisé pour le sous-module [translator](https://github.com/D4Vinci/Scrapling/blob/main/scrapling/core/translator.py)

---
<div align="center"><small>Conçu et développé avec ❤️ par Karim Shoair.</small></div><br>
