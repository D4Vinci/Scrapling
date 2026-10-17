---
title: "Scrapling : framework de web scraping pour Python"
description: "Scrapling : extrayez simplement les données du web moderne."
---

<style>
.md-typeset h1 {
  display: none;
}
[data-md-color-scheme="default"] .only-dark { display: none; }
[data-md-color-scheme="slate"] .only-light { display: none; }
</style>

<br/>
<div align="center">
    <a href="index.html" alt="Couverture">
        <img alt="Scrapling" src="assets/cover_light.svg" class="only-light">
        <img alt="Scrapling" src="assets/cover_dark.svg" class="only-dark">
    </a>
</div>

<h2 align="center"><i>Extrayez simplement les données du web moderne</i></h2><br>

Scrapling est un framework de web scraping pour Python. Il réunit des requêtes HTTP rapides, des navigateurs furtifs, l’analyse de pages et l’exploration simultanée de sites dans une seule bibliothèque.

Extrayez les données de pages statiques, exécutez JavaScript, interagissez avec les sites et accédez aux API qu’ils utilisent. Créez des crawlers avec des sessions réutilisables, la rotation des proxies, de nouvelles tentatives automatiques, la pause et la reprise, et des exports intégrés.

Utilisez Scrapling depuis Python, le terminal ou votre agent IA grâce au serveur MCP et à l’Agent Skill. Il couvre tout le processus, de l’extraction de quelques champs à l’enregistrement d’un site entier en fichiers Markdown propres.

## Ce que vous pouvez faire avec Scrapling {#what-you-can-do-with-scrapling}

- **[Récupérer des pages et interagir](fetching/choosing.md)** : Requêtes HTTP rapides, navigateurs furtifs, exécution de JavaScript, gestion de Cloudflare Turnstile et Interstitial, sessions persistantes et capture des réponses des API en arrière-plan.
- **[Analyser et extraire](parsing/selection.md)** : Recherche par CSS, XPath, texte et expressions régulières, suivi des éléments après un changement de page, recherche d’éléments similaires et sortie en Markdown propre.
- **[Explorer et exporter](spiders/getting-started.md)** : Spiders simultanés, rotation des proxies, nouvelles tentatives, AutoThrottle, pause et reprise, résultats en streaming, modèles prêts à l’emploi et exports en JSON, JSONL, CSV et XML.
- **[Extraire avec l’IA ou depuis le terminal](ai/mcp-server.md)** : Un serveur MCP pour que les agents IA naviguent et extraient des données, une Agent Skill, des commandes CLI et un shell interactif.

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

## Sponsors principaux {#top-sponsors}

--8<-- "sponsors.html"

<i><sub>Vous souhaitez afficher votre publicité ici ? Cliquez [ici](https://github.com/sponsors/D4Vinci), choisissez une offre et profitez de ses avantages.</sub></i>

## Fonctions principales {#key-features}

### Spiders : un framework complet d’exploration de sites {#spiders-a-full-crawling-framework}
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

### Récupération de pages avec des sessions {#advanced-websites-fetching-with-session-support}
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

### Analyse de pages et extraction de données {#parsing-and-data-extraction}
- 🔄 **Suivi des éléments** : Retrouvez les éléments après un changement du site grâce à des algorithmes de similarité.
- 🎯 **Sélection souple** : Utilisez CSS, XPath, les filtres, le texte, les expressions régulières et plus encore.
- 🔍 **Éléments similaires** : Trouvez automatiquement des éléments proches de ceux que vous avez déjà trouvés.

### Fonctions pour l’IA {#ai-features}
- 🤖 **Serveur MCP** : Permet aux assistants et agents IA, comme Claude et Cursor, d’extraire des données avec Scrapling par des requêtes HTTP, des actions du navigateur, des captures d’écran, un état de connexion enregistré et des réponses d’API en arrière-plan. Il utilise notre navigateur furtif et des outils qui aident les modèles adaptés à résoudre les CAPTCHA, en plus du solveur Cloudflare. Il réduit le contenu envoyé au modèle, bloque les publicités et protège contre les injections de prompts. Il permet aussi d’utiliser des navigateurs distants par CDP et des connexions HTTP avec des options d’authentification. ([Vidéo de démonstration](https://www.youtube.com/watch?v=qyFk3ZNwOxE))
- 🧠 **Agent Skill** : Une [Agent Skill](ai/agent-skill.md) prête à installer qui enseigne la bibliothèque aux agents de programmation pour qu’ils écrivent du code conforme à l’API actuelle.
- 📚 **Markdown prêt pour le RAG** : Convertissez une page en Markdown propre et adapté aux modèles de langage avec une ligne (`page.markdown()`), ou enregistrez un site entier en fichiers Markdown avec le modèle `ContentSpider`. Le processus ne demande aucun modèle de langage. ([Documentation](ai/building-rag-systems.md))

### Performances et usage réel {#high-performance-battle-tested-architecture}
- 🚀 **Grande vitesse** : Des performances optimisées qui dépassent la plupart des bibliothèques de web scraping pour Python.
- 🔋 **Faible usage de la mémoire** : Des structures de données optimisées et un chargement à la demande.
- ⚡ **Conversion rapide en JSON** : 10 fois plus rapide que la bibliothèque standard.
- 🏗️ **Testé en pratique** : Les tests couvrent 92 % de Scrapling et tout le code a des annotations de type. Des centaines de personnes l’ont utilisé chaque jour pour extraire des données pendant l’année passée.

### Outils pour développer et extraire des données {#developerweb-scraper-friendly-experience}
- 🎯 **Shell interactif** : Un shell IPython en option, intégré à Scrapling, avec des raccourcis et des outils pour créer des scripts plus vite. Convertissez les requêtes curl en requêtes Scrapling et consultez les résultats dans votre navigateur.
- 🚀 **Usage depuis le terminal** : Extrayez les données d’une URL sans écrire de code.
- 🛠️ **Navigation dans le DOM** : Accédez aux éléments parents, frères et enfants.
- 🧬 **Traitement du texte** : Expressions régulières, nettoyage du texte et opérations optimisées sur les chaînes.
- 📝 **Création de sélecteurs** : Générez des sélecteurs CSS et XPath fiables pour tout élément.
- 🔌 **API familière** : Proche de Scrapy et BeautifulSoup, avec les mêmes pseudo-éléments que Scrapy et Parsel.
- 🤝 **Intégration directe avec Scrapy** : Ajoutez le décorateur `scrapling_response` à un callback pour analyser les réponses que vous récupérez déjà avec le parser de Scrapling, sans réécrire votre programme.
- 📘 **Annotations de type complètes** : Elles aident l’éditeur à vérifier et à compléter le code. Tout le code est vérifié automatiquement par **PyRight** et **MyPy** à chaque changement.
- 🔋 **Image Docker prête à l’emploi** : Une image Docker avec tous les navigateurs est créée et publiée automatiquement à chaque version.


## Historique des étoiles {#star-history}
Le nombre d’étoiles de Scrapling sur GitHub augmente depuis son lancement, comme le montre le graphique.

<div id="chartContainer">
  <a href="https://github.com/D4Vinci/Scrapling">
    <img id="chartImage" alt="Historique des étoiles" loading="lazy" src="https://api.star-history.com/svg?repos=D4Vinci/Scrapling&type=Date" height="400"/>
  </a>
</div>

<script>
const observer = new MutationObserver((mutations) => {
  mutations.forEach((mutation) => {
    if (mutation.attributeName === 'data-md-color-media') {
      const colorMedia = document.body.getAttribute('data-md-color-media');
      const isDarkScheme = document.body.getAttribute('data-md-color-scheme') === 'slate';
      const chartImg = document.querySelector('#chartImage');
      const baseUrl = 'https://api.star-history.com/svg?repos=D4Vinci/Scrapling&type=Date';
      
      if (colorMedia === '(prefers-color-scheme)' ? isDarkScheme : colorMedia.includes('dark')) {
        chartImg.src = `${baseUrl}&theme=dark`;
      } else {
        chartImg.src = baseUrl;
      }
    }
  });
});

observer.observe(document.body, {
  attributes: true,
  attributeFilter: ['data-md-color-media', 'data-md-color-scheme']
});
</script>


## Installation {#installation}
Scrapling demande Python 3.10 ou une version plus récente :

```bash
pip install scrapling
```

!!! warning "Attention"

    Cette commande installe seulement le parser et ses dépendances, sans fetchers ni outils en ligne de commande. Avec cette seule installation, importer depuis `scrapling.fetchers` ou `scrapling.spiders`, comme dans les exemples précédents, provoque `ModuleNotFoundError`. Pour utiliser les fetchers ou les spiders, installez d’abord les dépendances des fetchers comme indiqué ci-dessous.

### Dépendances facultatives {#optional-dependencies}

1. Pour utiliser les fetchers, leurs classes ou les fonctions supplémentaires suivantes, installez les dépendances des fetchers et des navigateurs :
    ```bash
    pip install "scrapling[fetchers]"
    
    scrapling install           # normal install
    scrapling install  --force  # force reinstall
    ```

    Cette commande télécharge tous les navigateurs, leurs dépendances système et les outils de modification des empreintes du navigateur.

    Vous pouvez aussi les installer depuis Python, au lieu de lancer une commande :
    ```python
    from scrapling.cli import install
    
    install([], standalone_mode=False)          # normal install
    install(["--force"], standalone_mode=False) # force reinstall
    ```

2. Fonctions supplémentaires :


     - Installer le serveur MCP :
       ```bash
       pip install "scrapling[ai]"
       ```
     - Installer les dépendances pour [créer des systèmes RAG](ai/building-rag-systems.md) :
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

### Docker {#docker}
Vous pouvez aussi télécharger depuis DockerHub une image Docker avec tous les extras et navigateurs :
```bash
docker pull pyd4vinci/scrapling
```
Ou la télécharger depuis le registre GitHub :
```bash
docker pull ghcr.io/d4vinci/scrapling:latest
```
L’image est créée à partir de la branche principale du dépôt et publiée automatiquement par GitHub Actions.

## Organisation de la documentation {#how-the-documentation-is-organized}
La documentation de Scrapling est vaste. Nous suivons donc le [modèle de documentation Diátaxis](https://diataxis.fr/).

## Soutien {#support}

Si vous aimez Scrapling et souhaitez soutenir son développement :

- ⭐ Ajoutez une étoile au [dépôt GitHub](https://github.com/D4Vinci/Scrapling).
- 🚀 Suivez-nous sur [Twitter](https://x.com/Scrapling_dev) et rejoignez le [serveur Discord](https://discord.gg/EMgGbDceNQ).
- 💝 Vous pouvez [sponsoriser le projet ou m’offrir un café](donate.md). :wink:
- 🐛 Signalez les bugs et proposez des fonctions sur [GitHub Issues](https://github.com/D4Vinci/Scrapling/issues).

## Licence {#license}

Ce projet utilise la licence BSD-3. Consultez le fichier [LICENSE](https://github.com/D4Vinci/Scrapling/blob/main/LICENSE) pour en savoir plus.
