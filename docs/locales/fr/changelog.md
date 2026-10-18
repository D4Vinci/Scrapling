---
title: "Historique des changements de Scrapling"
description: "Notes des versions de Scrapling, avec les nouvelles fonctionnalités, les corrections et les changements incompatibles."
---

# Historique des changements {#changelog}

Tous les changements importants de Scrapling, tirés des [versions publiées sur GitHub](https://github.com/D4Vinci/Scrapling/releases).

## [v0.5](https://github.com/D4Vinci/Scrapling/releases/tag/v0.5) - 2026-10-17 {#v0.5}

**Scrapling v0.5 améliore presque tout : la récupération, l’analyse, les spiders, l’automatisation du navigateur, les outils IA et la documentation en dix langues 🚀**

!!! warning "Avertissement"

    **Cette version introduit trop de changements incompatibles pour tous les présenter ici. Consultez le [guide de migration vers v0.5](migrating-to-v0.5.md) avant de mettre à jour.**

### 🚀 Nouveautés et améliorations d’utilisation {#v0.5-new-stuff-and-quality-of-life-changes}

- **Un serveur MCP beaucoup plus complet pour les agents IA, capable de résoudre presque tous les CAPTCHA** (consultez la [documentation](ai/mcp-server.md)) :

    - **Des parcours complets dans le navigateur** : remplissez des formulaires, cliquez, survolez, faites défiler, utilisez le clavier, gérez les boîtes de dialogue et attendez les résultats dans une seule séquence ordonnée. Différents types de champs et des interactions plus lentes sont pris en charge. Les actions s’arrêtent à la première erreur.
    - **Lisez et recherchez dans la page actuelle sans la recharger** : extrayez du HTML, du Markdown ou du texte de toute la page ou d’un élément. Les instantanés de page permettent la recherche et affichent les rôles, les noms et les positions des éléments, avec des vues ciblées qui conservent le contexte environnant.
    - **Exécutez votre JavaScript et prenez des captures d’écran ciblées** : exécutez des scripts, y compris des opérations asynchrones, avec accès au JavaScript de la page. Capturez un élément, la zone visible ou toute la page en PNG ou JPEG.
    - **Inspectez l’activité réseau et réutilisez vos connexions** : examinez les requêtes et réponses enregistrées, sauvegardez et restaurez l’état de connexion du navigateur, et interagissez avec les éléments dans un Shadow DOM ouvert ou fermé. Lisez le trafic enregistré avant de fermer la session.
    - **Utilisez moins de tokens et obtenez des erreurs plus claires** : des descriptions d’outils plus courtes et des instructions communes réduisent les répétitions. Les erreurs du navigateur et des requêtes parviennent aux agents avec des messages utiles.

- **Voyez les requêtes derrière la page**. Activez `record_requests=True` pour enregistrer le trafic terminé au fil des chargements, des actions et des onglets, puis inspectez les réponses sauvegardées sans renvoyer de requêtes. (Consultez la [documentation](fetching/stealthy.md#network-history))

    ```python
    from scrapling.fetchers import StealthySession

    with StealthySession(record_requests=True) as session:
        session.fetch("https://example.com", network_idle=True)
        for response in session.network.search(url_pattern=r"/api/", limit=None):
            print(response.url, response.status, response.body)
    ```

    - Filtrez par URL, méthode, type de ressource ou statut ; récupérez une réponse par son identifiant. Inspectez les en-têtes, les données envoyées, les réponses API, les erreurs HTTP et les redirections avec l’API `Response` habituelle.
    - Conserve les corps de réponse textuels pris en charge, dans les limites de taille, ainsi que les métadonnées et le motif si un corps ne peut pas être enregistré. La limite par défaut est de 1 000 requêtes. Fonctionne avec les sessions synchrones et asynchrones ; l’historique Python sauvegardé reste lisible après la fermeture.

- **Sauvegardez une connexion une fois et réutilisez-la d’une exécution à l’autre**. `save_state(path)` et `load_state(path)` enregistrent les cookies, le stockage local et IndexedDB dans un JSON compatible avec Playwright. Les sessions du navigateur synchrones et asynchrones les prennent en charge. (Consultez la [documentation](fetching/stealthy.md#save-and-load-session-state))
    - Chargez l’état avant de récupérer ou de recharger une page. Nécessite un contexte de navigateur partagé et démarré, sans `proxy_rotator` ; les onglets, les réglages du navigateur et `sessionStorage` ne sont pas sauvegardés.

- **Extrayez le Shadow DOM ouvert avec `pierce_shadow=True`**, puis utilisez CSS ou XPath comme d’habitude. Disponible dans les fetchers de navigateur, les sessions et l’option CLI `--pierce-shadow`. Conserve le contenu des slots sans modifier la page active. La capture HTML exclut les racines fermées et les documents iframe. (Consultez la [documentation](fetching/stealthy.md#shadow-dom))

- **Choisissez comment votre spider explore un site**. `CrawlSpider` et ses sous-classes, dont `ContentSpider`, acceptent `crawl_strategy="bfs"` pour traiter d’abord les requêtes les plus anciennes, ou `"dfs"` pour traiter d’abord les plus récentes. La priorité reste déterminante, et les pages traitées en parallèle peuvent se terminer dans un ordre différent. (Consultez la [documentation](spiders/generic-templates.md#crawl-order))

### 🐛 Corrections de bugs {#v0.5-bug-fixes}

- **Amélioration de la résolution Cloudflare** avec la détection des widgets qui apparaissent plus tard, moins d’attentes inutiles et des boucles de nouvelle tentative limitées pour les défis passifs et les frames cachées. Corrige [#468](https://github.com/D4Vinci/Scrapling/issues/468) et [#509](https://github.com/D4Vinci/Scrapling/issues/509).
- **Correction du démarrage du navigateur depuis un shell Windows lancé en tant qu’administrateur**. Corrige [#463](https://github.com/D4Vinci/Scrapling/issues/463).
- **Conservation des options de discrétion intégrées lors de l’ajout d’options de navigateur personnalisées**, par @alkaz-nodemaven dans [#430](https://github.com/D4Vinci/Scrapling/pull/430).
- **Amélioration de l’analyse du jeu de caractères des réponses du navigateur**, y compris les déclarations avec des variations de casse, des espaces ou des valeurs entre guillemets.
- **L’absence de défi Cloudflare n’est plus enregistrée comme une erreur** lorsqu’aucun défi n’a besoin d’être résolu. Corrige [#459](https://github.com/D4Vinci/Scrapling/issues/459).

- **Correction des empreintes de requête** pour les paramètres d’URL, par @yetval dans [#448](https://github.com/D4Vinci/Scrapling/pull/448), pour les corps JSON vides ou évalués comme faux, par @ac1982 dans [#480](https://github.com/D4Vinci/Scrapling/pull/480), et pour l’ordre d’insertion des en-têtes, par @SarwadnyaMahajan dans [#466](https://github.com/D4Vinci/Scrapling/pull/466).
- **Correction de la propagation des données de requête aux liens suivis**, y compris les anciens en-têtes liés au corps, par @yetval dans [#462](https://github.com/D4Vinci/Scrapling/pull/462).
- **Les réponses bloquées ne sont plus enregistrées comme des entrées réussies du cache de développement**, par @Kuang-xianxin dans [#446](https://github.com/D4Vinci/Scrapling/pull/446).
- **Conservation des fichiers de point de contrôle lorsqu’une exploration échoue avec une exception**, par @SulimanAbdulrazzaq dans [#486](https://github.com/D4Vinci/Scrapling/pull/486).
- **Correction de la gestion des erreurs de robots.txt**, afin que les consultations échouées ne soient pas mises en cache comme une autorisation d’explorer, par @prateekraawat1 dans [#443](https://github.com/D4Vinci/Scrapling/pull/443).
- **Correction de l’extraction des liens avec des sélecteurs de restriction**, y compris les correspondances vides et les sélecteurs qui ciblent l’élément du lien lui-même, par @SulimanAbdulrazzaq dans [#452](https://github.com/D4Vinci/Scrapling/pull/452) et [#483](https://github.com/D4Vinci/Scrapling/pull/483).
- **Correction du choix des callbacks de sitemap**, par @SulimanAbdulrazzaq dans [#458](https://github.com/D4Vinci/Scrapling/pull/458), **et de l’analyse XML avec des commentaires ou des instructions de traitement**, par @sup3dev dans [#450](https://github.com/D4Vinci/Scrapling/pull/450).
- **Prise en charge des indicateurs d’ordre des octets en début de robots.txt et des flux CSV**, par @SulimanAbdulrazzaq dans [#453](https://github.com/D4Vinci/Scrapling/pull/453).
- **Correction de la gestion de `stealthy_headers` dans les sessions HTTP des spiders**, en passant l’option à la session au lieu de la transmettre directement à `curl_cffi`, par @Yigtwxx dans [#475](https://github.com/D4Vinci/Scrapling/pull/475).

- **Correction de l’encodage des formulaires fournis comme dictionnaires pour les valeurs de type liste et tuple**, tout en conservant la priorité du corps de requête et la gestion actuelle de `None`, avec des contributions de @SulimanAbdulrazzaq dans [#485](https://github.com/D4Vinci/Scrapling/pull/485).
- **Correction de la fusion sans distinction de casse des en-têtes HTTP de session et de requête**, par @SulimanAbdulrazzaq dans [#487](https://github.com/D4Vinci/Scrapling/pull/487).
- **Correction des requêtes CLI qui ignoraient sans avertissement les corps JSON vides ou évalués comme faux**, par @SulimanAbdulrazzaq dans [#484](https://github.com/D4Vinci/Scrapling/pull/484).
- **Les exports de fichiers Markdown et texte utilisent toujours UTF-8**, et les erreurs de conversion ne tronquent plus un fichier de sortie existant, par @SulimanAbdulrazzaq dans [#488](https://github.com/D4Vinci/Scrapling/pull/488).
- **Correction de la gestion des options user-agent et proxy de curl dans `curl2fetcher()`**, par @SulimanAbdulrazzaq dans [#490](https://github.com/D4Vinci/Scrapling/pull/490).

- **Correction des blocs Markdown qui se retrouvaient collés** lorsque plusieurs éléments sélectionnés sont convertis avec `Response.markdown()` ou l’extraction CLI, avec des contributions de @Yigtwxx dans [#432](https://github.com/D4Vinci/Scrapling/pull/432).
- **Correction du nettoyage du contenu caché pour les sorties IA**, afin de conserver le contenu visible tel que `opacity:0.95`, de reconnaître davantage de styles cachés et de supprimer les slots cachés, avec des contributions de @Yigtwxx dans [#460](https://github.com/D4Vinci/Scrapling/pull/460).
- **Correction de la suppression des balises inutiles qui s’arrêtait trop tôt autour des balises imbriquées**, par @Yigtwxx dans [#474](https://github.com/D4Vinci/Scrapling/pull/474).
- **Correction des sélecteurs CSS et XPath générés pour le premier de plusieurs éléments frères de même balise**, par @yellow-dog-dog dans [#495](https://github.com/D4Vinci/Scrapling/pull/495).
- **Résolution d’un avertissement de dépréciation de l’analyseur HTML lxml**, par @afsuyadi dans [#493](https://github.com/D4Vinci/Scrapling/pull/493).

### Documentation {#v0.5-docs}

- **Tout le site parle maintenant dix langues** : anglais, arabe, espagnol, portugais brésilien, français, allemand, chinois simplifié, japonais, russe et coréen. Les guides, les références API, les tutoriels et l’[historique des changements](changelog.md) sont traduits, avec l’affichage de droite à gauche pour l’arabe et un changement de langue qui conserve la page et la section.
- **Des guides, des exemples README et des étapes d’installation plus clairs**, couvrant les données des points de contrôle, les encodages du navigateur, l’état sauvegardé, l’historique réseau, le Shadow DOM et l’ordre d’exploration.
- **Mise à jour de l’Agent Skill**, de ses exemples, de ses références et de son archive téléchargeable pour les outils actuels de navigateur et MCP.
- **Déplacement de l’historique des changements vers le site** et ajout de l’accès à la source Markdown de chaque page.

### Projet {#v0.5-project}

- Actualisation du logo de Scrapling, des images de couverture et de la présentation du site.
- Ajout de tests pour les actions du navigateur, les boîtes de dialogue, l’extraction, les captures d’écran, JavaScript, l’enregistrement réseau, les fichiers d’état, le Shadow DOM et les corrections du crawler.
- Ajout d’un marqueur pour les tests de navigateur et d’exécutions séparées pour les tests de navigateur, asynchrones et parallèles. Amélioration de la compatibilité des tests de points de contrôle et CSV sous Windows, par @diegobravtraps-oss dans [#457](https://github.com/D4Vinci/Scrapling/pull/457).
- Mise à jour de la configuration commune de compilation de la documentation multilingue et des consignes de contribution.

## [v0.4.15](https://github.com/D4Vinci/Scrapling/releases/tag/v0.4.15) - 2026-08-23 {#v0.4.15}

**L’une des plus grandes versions de l’année : un serveur MCP repensé, du Markdown prêt pour RAG en une ligne, une meilleure résolution des défis Cloudflare et des onglets qui restent ouverts pour l’automatisation 🚀**

!!! warning "Avertissement"

    **Cette version introduit des changements incompatibles dans le serveur MCP. Consultez la section [changements incompatibles](https://github.com/D4Vinci/Scrapling/blob/v0.4.15/docs/ai/mcp-server.md#breaking-changes) avant de mettre à jour.**

### 🚀 Nouveautés et améliorations d’utilisation {#v0.4.15-new-stuff-and-quality-of-life-changes}

- **Les onglets du navigateur restent désormais ouverts et sont réutilisés entre les requêtes** (consultez la [documentation](fetching/stealthy.md#session-management)) :
    - Toutes les sessions du navigateur conservent leurs onglets après une requête. La suivante réutilise un onglet libre au lieu d’en ouvrir un autre.
    - Chaque requête réapplique ses propres réglages (délais, en-têtes et blocage des ressources) à l’onglet qu’elle reçoit. Les réglages ne passent donc pas d’une requête à l’autre.
    - Les onglets qui rencontrent une erreur sont fermés et remplacés. La nouvelle méthode `close_pages()` ferme tous les onglets ouverts.
    - La page récupérée reste chargée. Une fonction `page_setup` de la requête suivante s’exécute donc dessus avant de naviguer ailleurs. Cela permet d’enchaîner des étapes d’automatisation entre les requêtes.

- **Convertissez n’importe quelle page en Markdown propre, prêt pour les LLM, avec `Response.markdown()`** (consultez la [documentation](ai/building-rag-systems.md)) :

    ```python
    from scrapling.fetchers import Fetcher

    markdown = Fetcher.get("https://example.com").markdown(main_content_only=True)
    ```

    - Les scripts, les styles et le contenu caché d’injection de prompts sont toujours supprimés d’abord, avec le même nettoyage que celui du serveur MCP.
    - Passez `css_selector` pour ne convertir que les éléments dont vous avez besoin.
    - Disponible via le nouvel extra `rag` (`pip install "scrapling[rag]"`), également inclus dans les extras `ai`/`shell`/`all`.

- **Nouveau modèle `SiteToMarkdownSpider` pour explorer un site entier et créer un corpus Markdown pour les pipelines RAG** (consultez la [documentation](ai/building-rag-systems.md)) :

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

    - Produit un élément par page avec `url`/`title`/`markdown`. Le paramètre facultatif `output_dir` écrit un fichier Markdown par page.
    - `max_pages` limite l’exploration. Comme le modèle repose sur `CrawlSpider`, redéfinir `rules()` vous donne un contrôle complet sur les liens suivis.

- **Le serveur MCP a été repensé (changement incompatible)** (consultez les [changements incompatibles](https://github.com/D4Vinci/Scrapling/blob/v0.4.15/docs/ai/mcp-server.md#breaking-changes) et la [documentation](ai/mcp-server.md)) :
    - Les 13 outils sont maintenant répartis en deux modes : les outils à usage unique (`fetch`, `bulk_fetch`, `stealthy_fetch`, `bulk_stealthy_fetch`), qui lancent toujours leur propre navigateur et affichent leurs vrais réglages par défaut, et les outils de session, qui utilisent une session ouverte une seule fois.
    - Le nouvel outil `session_fetch` récupère les pages via une session du navigateur. `open_session` ne contient plus que les réglages du navigateur et renvoie les réglages effectifs de la session à l’agent IA.
    - L’outil `get` a été renommé `make_request` et accepte maintenant toutes les méthodes HTTP.
    - Les nouveaux outils `open_request_session` et `session_make_request` donnent à l’IA des sessions HTTP persistantes qui conservent les cookies et l’empreinte du navigateur entre les requêtes.
    - Cela évite aussi que les récupérations réinitialisent les réglages de la session, un problème d’abord corrigé par @Yigtwxx dans [#418](https://github.com/D4Vinci/Scrapling/pull/418).

- **Le transport HTTP du serveur MCP exige maintenant une authentification et écoute sur localhost par défaut (changement incompatible)**, par @yamantaka-singh dans [#414](https://github.com/D4Vinci/Scrapling/pull/414) (corrige [#413](https://github.com/D4Vinci/Scrapling/issues/413), consultez la [documentation](ai/mcp-server.md#authentication)) :
    - Passez `--auth-token` (ou la variable d’environnement `SCRAPLING_MCP_AUTH_TOKEN`) pour exiger un jeton bearer, ou `--no-auth` pour proposer volontairement le serveur sans authentification.
    - Passez `--host 0.0.0.0` pour accepter les connexions depuis le réseau.

### 🐛 Corrections de bugs {#v0.4.15-bug-fixes}

- **La résolution de Cloudflare Turnstile/Interstitial fonctionne maintenant quelle que soit la configuration régionale du navigateur et ne boucle plus indéfiniment sur les défis interactifs en mode sans interface**. Les pages du navigateur discret ne plantent plus en cours de résolution, avec des contributions de @subediparas5 dans [#412](https://github.com/D4Vinci/Scrapling/pull/412). (Corrige [#411](https://github.com/D4Vinci/Scrapling/issues/411) et [#422](https://github.com/D4Vinci/Scrapling/issues/422))
- **Correction de `find`/`find_all` avec `class_`, qui manquaient sans avertissement les éléments ayant plusieurs classes**, par @yetval dans [#410](https://github.com/D4Vinci/Scrapling/pull/410), **ainsi que des valeurs vides de `class_` et des chaînes CSS non échappées**, par @yamantaka-singh dans [#417](https://github.com/D4Vinci/Scrapling/pull/417).
- **Correction de la perte des métadonnées de requête lors de la réutilisation des réponses en cache dans `development_mode`**, par @Yigtwxx dans [#419](https://github.com/D4Vinci/Scrapling/pull/419).
- **Correction des requêtes HTTP avec `retries` inférieur à 1 qui échouaient sans envoyer la requête**, par @Yigtwxx dans [#420](https://github.com/D4Vinci/Scrapling/pull/420).

### Documentation {#v0.4.15-docs}

- **Les sections du site ont été réorganisées** : la nouvelle section « Utilisation avec l’IA » regroupe le serveur MCP, la nouvelle page [Agent Skill](ai/agent-skill.md) et le guide [Créer des systèmes RAG](ai/building-rag-systems.md). Le guide de migration depuis BeautifulSoup rejoint l’intégration Scrapy dans « Intégrations et migrations ».
- **Ajout d’un [historique des changements](changelog.md)** au dépôt, avec les notes de toutes les versions publiées jusqu’ici.

## [v0.4.14](https://github.com/D4Vinci/Scrapling/releases/tag/v0.4.14) - 2026-08-10 {#v0.4.14}

**Une version de maintenance rapide pour corriger l’installation avec `uv` 🔧**

### 🐛 Corrections de bugs {#v0.4.14-bug-fixes}

- **Correction du refus de `uv` d’installer v0.4.13 par défaut, qui le faisait revenir à une ancienne version sans avertissement**. La version précédente exigeait une préversion de `curl_cffi`, que `uv` n’autorise pas sans activation explicite.
Toutes les dépendances utilisent maintenant des versions stables. (Corrige [#407](https://github.com/D4Vinci/Scrapling/issues/407))

## [v0.4.13](https://github.com/D4Vinci/Scrapling/releases/tag/v0.4.13) - 2026-08-09 {#v0.4.13}

**Une nouvelle mise à jour avec des spiders pour les flux et un serveur MCP plus intelligent 🎉**

### 🚀 Nouveautés et améliorations d’utilisation {#v0.4.13-new-stuff-and-quality-of-life-changes}

- **Nouveaux modèles de spiders pour les flux**. `XMLFeedSpider` parcourt les nœuds de tout flux XML (RSS, Atom, flux de produits, etc.), et `CSVFeedSpider` parcourt les lignes CSV sous forme de dictionnaires. Tous deux décompressent automatiquement les flux compressés avec gzip. (Consultez la [documentation](spiders/generic-templates.md))

  ```python
  from scrapling.spiders import XMLFeedSpider

  class RSSSpider(XMLFeedSpider):
      name = "rss"
      start_urls = ["https://example.com/feed.xml"]

      async def parse_node(self, response, node):
          yield {"title": node.findtext("title"), "link": node.findtext("link")}

  result = RSSSpider().start()
  ```

- **Le serveur MCP utilise maintenant MCP SDK v2 et devient plus intelligent**. Il fournit des instructions qui apprennent à votre agent IA à utiliser les outils efficacement ; chaque outil déclare des annotations pour que des clients comme Claude Code puissent approuver automatiquement ceux qui lisent seulement ; les descriptions sont plus courtes pour économiser des tokens ; et le serveur communique sa version et son logo aux clients MCP. (Consultez la [documentation](ai/mcp-server.md))
- **Ajout de la commande `scrapling-mcp`**, qui lance directement `scrapling mcp`. L’enregistrement de Scrapling auprès des clients et registres MCP qui attendent une seule commande tient maintenant en une ligne.
- **Les versions de Playwright/Patchright et des navigateurs ne sont plus figées**. Le User-Agent généré correspond maintenant toujours à la version exacte de Chromium pilotée par votre installation de Playwright/Patchright. Scrapling n’impose donc plus leurs versions et vous pouvez les mettre à jour librement. Exécutez `scrapling install --force` après la mise à jour pour actualiser les navigateurs.

### 🐛 Corrections de bugs {#v0.4.13-bug-fixes}

- **Correction du plantage à l’importation de Scrapling avec un ValueError de `browserforge`** lorsque le paquet de données d’empreintes est en retard sur les versions des navigateurs. (Corrige [#394](https://github.com/D4Vinci/Scrapling/issues/394), [#396](https://github.com/D4Vinci/Scrapling/issues/396) et [#400](https://github.com/D4Vinci/Scrapling/issues/400))
- **Correction de la taille incorrecte des pools de pages des outils de navigateur par lots de MCP**, qui faisait échouer `bulk_fetch` avec plus de 50 URL et obligeait `bulk_stealthy_fetch` à récupérer toutes les URL depuis un seul onglet, par @Yigtwxx dans [#393](https://github.com/D4Vinci/Scrapling/pull/393).

### Projet {#v0.4.13-project}

- **Nouvelle [politique de contribution avec l’IA](https://github.com/D4Vinci/Scrapling/blob/main/AI_POLICY.md)** : les contributions assistées par l’IA sont les bienvenues, mais vous devez le signaler dans la PR ou l’issue ; les soumissions qui semblent générées par l’IA sans le signaler sont étiquetées et fermées.

## [v0.4.12](https://github.com/D4Vinci/Scrapling/releases/tag/v0.4.12) - 2026-07-26 {#v0.4.12}

**Une version qui aide vos spiders à mieux s’adapter aux sites qu’ils explorent**

### 🚀 Nouveautés et améliorations d’utilisation {#v0.4.12-new-stuff-and-quality-of-life-changes}

- **Les spiders peuvent maintenant régler leur vitesse avec AutoThrottle.** Au lieu de deviner un `download_delay` qui sera trop lent ou entraînera un blocage, le spider mesure la vitesse de réponse de chaque site et ajuste lui-même le délai de chaque domaine. Quand un site commence à vous bloquer ou à limiter le rythme des requêtes, il double le délai (ou attend exactement la durée demandée par l’en-tête `Retry-After`) jusqu’à ce que cela cesse, puis accélère de nouveau. Votre `download_delay` et tout `Crawl-delay` de robots.txt restent le minimum. (Consultez la [documentation](spiders/advanced.md#autothrottle))

    ```python
    class MySpider(Spider):
        name = "adaptive"
        start_urls = ["https://example.com"]
        autothrottle_enabled = True
        autothrottle_start_delay = 2.0
        autothrottle_max_delay = 30.0
        autothrottle_block_backoff = True
    ```

- **Exportez vos résultats en CSV et XML**, en plus des exportateurs JSON/JSONL déjà disponibles. Les éléments qui ne partagent pas toutes les mêmes clés sont exportés sans perte, et les valeurs imbriquées sont écrites en JSON. (Consultez la [documentation](spiders/getting-started.md))

    ```python
    result = MySpider().start()
    result.items.to_csv("products.csv")
    result.items.to_xml("products.xml")
    ```

- **Le serveur MCP peut maintenant exiger une authentification**, pour que vous puissiez l’exposer en toute sécurité au lieu de le garder sur votre propre machine. Toute requête sans jeton est rejetée, et vous pouvez aussi limiter les noms d’hôte auxquels le serveur répond. (Consultez la [documentation](ai/mcp-server.md))

    ```bash
    scrapling mcp --http --auth-token "$(openssl rand -hex 32)"
    ```

- **Les navigateurs acceptent maintenant les URL CDP via HTTP**, en plus de celles via WebSocket. À côté des endpoints `wss://` des fournisseurs de navigateurs gérés, vous pouvez donc connecter tout fetcher de navigateur ou toute session MCP à un Chrome que vous avez lancé avec `--remote-debugging-port=9222`.

- **Les images Docker publiées portent maintenant une étiquette avec leur version**, au lieu de seulement `latest`, pour que vous puissiez fixer la version exacte voulue, par @JanRK dans [#384](https://github.com/D4Vinci/Scrapling/pull/384).

### 🐛 Corrections de bugs {#v0.4.12-bug-fixes}

- **Correction de la perte de tous les cookies dans les réponses en cache** quand elles provenaient d’un moteur de navigateur. Cela cassait sans avertissement toute logique de session ou d’authentification qui en dépendait dans le mode de développement des spiders, par @amitvijapur dans [#379](https://github.com/D4Vinci/Scrapling/pull/379). (Corrige [#376](https://github.com/D4Vinci/Scrapling/issues/376))

- **Correction de `StealthyFetcher`, qui imposait la configuration régionale `en-US`** à tous les navigateurs au lieu de suivre celle du système. Les sites voyaient alors une différence entre cette configuration et votre adresse IP et vous jugeaient suspect, par exemple avec des réponses 429 de Google. (Corrige [#381](https://github.com/D4Vinci/Scrapling/issues/381))

- **Correction d’un message d’erreur trompeur dans le système de stockage** et suppression d’un appel inutilisé qui restait après les insertions, par @fix2015 dans [#377](https://github.com/D4Vinci/Scrapling/pull/377).

### Performances {#v0.4.12-performance}

- **Le temps d’exécution de `get_all_text()` est maintenant proportionnel au nombre de nœuds, O(nodes)** au lieu de parcourir les ancêtres de chaque nœud de texte. Cela le rend environ 5-6 fois plus rapide sur les pages très imbriquées, par @yetval dans [#378](https://github.com/D4Vinci/Scrapling/pull/378).

## [v0.4.11](https://github.com/D4Vinci/Scrapling/releases/tag/v0.4.11) - 2026-07-12 {#v0.4.11}

**Une mise à jour importante avec le premier modèle de spider pour une plateforme, un analyseur plus rapide et des corrections importantes 🎉**

### 🚀 Nouveautés et améliorations d’utilisation {#v0.4.11-new-stuff-and-quality-of-life-changes}

- **Ajout de `ShopifySpider`, le premier modèle de spider pour une plateforme !** Extrayez tous les produits de toute boutique Shopify via son API JSON, sans toucher au HTML du site. Créez une sous-classe, définissez le domaine de la boutique et c’est prêt (consultez la [documentation](spiders/platform-templates.md))

  ```python
  from scrapling.spiders import ShopifySpider

  class MyStore(ShopifySpider):
      target_website = "example.com"

  result = MyStore().start()
  ```

- **Ajout de `--executable-path` aux commandes de navigateur de la CLI**. `scrapling extract fetch` et `scrapling extract stealthy-fetch` acceptent maintenant un exécutable de navigateur personnalisé compatible avec Chromium. Si l’option n’est pas passée, ils utilisent la variable d’environnement `SCRAPLING_EXECUTABLE_PATH`, comme le serveur MCP (résout [#371](https://github.com/D4Vinci/Scrapling/issues/371))

  ```bash
  scrapling extract fetch "https://example.com" page.html --executable-path "/path/to/chromium"
  ```

### 🤖 Améliorations d’utilisation {#v0.4.11-quality-of-life-changes}
- **`find_by_text` et `find_by_regex` sont jusqu’à environ 2 fois plus rapides** quand `first_match` est activé (par défaut), car les éléments ne sont convertis en objets qu’au besoin et la recherche s’arrête au premier résultat, par @yetval dans [#370](https://github.com/D4Vinci/Scrapling/pull/370)
- **Mise à jour des tests de performance avec les nouveaux chiffres, comparés aux dernières versions de toutes les bibliothèques.**
- **Mise à jour des règles de contribution**

### 🐛 Corrections de bugs {#v0.4.11-bug-fixes}

- **Correction des plantages des outils de récupération du serveur MCP sur les pages contenant des caractères de contrôle**, avec l’erreur `All strings must be XML compatible`, par @yetval dans [#368](https://github.com/D4Vinci/Scrapling/pull/368) (corrige [#366](https://github.com/D4Vinci/Scrapling/issues/366))

## [v0.4.10](https://github.com/D4Vinci/Scrapling/releases/tag/v0.4.10) - 2026-07-04 {#v0.4.10}

**Une nouvelle mise à jour avec une toute nouvelle intégration Scrapy et plusieurs corrections de la communauté 🎉**

### 🚀 Nouveautés et améliorations d’utilisation {#v0.4.10-new-stuff-and-quality-of-life-changes}

- **Ajout d’une intégration Scrapy** pour utiliser l’API d’analyse de Scrapling dans vos projets Scrapy existants sans les réécrire. Appliquez le décorateur `scrapling_response` à un callback de spider. La réponse qu’il reçoit devient une `Response` de Scrapling, tandis que Scrapy continue de gérer l’exploration (consultez la [documentation](integrations/scrapy.md)) :

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

- **Le serveur MCP peut maintenant utiliser un navigateur personnalisé compatible avec Chromium** pour tous les outils basés sur un navigateur. Définissez-le une fois avec `scrapling mcp --executable-path "/path/to/chromium"` ou la variable d’environnement `SCRAPLING_EXECUTABLE_PATH`, ou pour chaque requête avec l’argument `executable_path`, par @samrusani dans [#360](https://github.com/D4Vinci/Scrapling/pull/360) (résout [#347](https://github.com/D4Vinci/Scrapling/issues/347))
- **Mise à jour de tous les navigateurs et des empreintes**. Exécutez `scrapling install --force` après la mise à jour pour les actualiser.

### 🐛 Corrections de bugs {#v0.4.10-bug-fixes}

- **Correction du texte illisible (mojibake) provenant des fetchers de navigateur sur les sites qui n’utilisent pas UTF-8**, par @yehudalevy-collab dans [#365](https://github.com/D4Vinci/Scrapling/pull/365) (corrige [#364](https://github.com/D4Vinci/Scrapling/issues/364)).
- **Correction de `LinkExtractor`, qui ne filtrait pas les extensions de fichiers composées comme `.tar.gz`**, par @renbkna dans [#359](https://github.com/D4Vinci/Scrapling/pull/359) (corrige [#349](https://github.com/D4Vinci/Scrapling/issues/349)).
- **Correction de la perte des requêtes en cours dans les points de reprise des explorations en pause, pour qu’elles ne soient plus ignorées à la reprise**, par @yetval dans [#358](https://github.com/D4Vinci/Scrapling/pull/358).
- **Correction du calcul des délais d’exploration à partir des directives `Request-rate` de robots.txt** grâce à la mise à jour de Protego, avec des tests adaptés par @Disaster-Terminator dans [#355](https://github.com/D4Vinci/Scrapling/pull/355).

### Documentation {#v0.4.10-docs}

- **Clarification de l’interaction de `init_script` avec le contexte d’exécution isolé de Patchright en mode discret**, par @mturac dans [#353](https://github.com/D4Vinci/Scrapling/pull/353) (résout [#350](https://github.com/D4Vinci/Scrapling/issues/350)).
- **Ajout de la méthode d’installation de la skill pour agents via [skills.sh](https://skills.sh/D4Vinci/Scrapling)**, par @ob-aion dans [#363](https://github.com/D4Vinci/Scrapling/pull/363).

## [v0.4.9](https://github.com/D4Vinci/Scrapling/releases/tag/v0.4.9) - 2026-06-07 {#v0.4.9}

**Une mise à jour de maintenance riche en corrections de problèmes signalés par la communauté 🛠️**

### 🚀 Nouveautés et améliorations d’utilisation {#v0.4.9-new-stuff-and-quality-of-life-changes}

- **Mise à jour de tous les navigateurs et des empreintes**. Exécutez `scrapling install --force` après la mise à jour pour les actualiser.
- **Ajout de l’option `--version` à la CLI**, par @ETM-Code dans [#303](https://github.com/D4Vinci/Scrapling/pull/303) (résout [#299](https://github.com/D4Vinci/Scrapling/issues/299))

### 🐛 Corrections de bugs {#v0.4.9-bug-fixes}

- **Correction de l’argument `proxy` de session, ignoré sans avertissement dans les sessions HTTP**, ce qui pouvait révéler votre véritable IP (résout [#295](https://github.com/D4Vinci/Scrapling/issues/295)). Associer un `proxy` de session avec un argument `proxies` par requête (ou l’inverse) produit maintenant une erreur au lieu d’en ignorer un sans avertissement.
- **Correction des échecs de navigation en combinant `init_script` avec `user_data_dir`** (résout [#294](https://github.com/D4Vinci/Scrapling/issues/294)).
- **Correction de la détection de l’encodage quand les sites mettent la valeur charset entre guillemets dans l’en-tête `Content-Type`**, par @Bortlesboat dans [#323](https://github.com/D4Vinci/Scrapling/pull/323).
- **Correction d’un `IndexError` lors de la relocalisation adaptative d’éléments avec `auto_save` activé**, par @Mubashirrrr dans [#340](https://github.com/D4Vinci/Scrapling/pull/340).
- **Correction des plantages lors de l’enregistrement des points de reprise et du cache des spiders sous Windows**, par @MrStarkEG dans [#344](https://github.com/D4Vinci/Scrapling/pull/344).
- **Correction du calcul de similarité dans `find_similar` pour les éléments ayant un nombre différent d’attributs** (résout [#322](https://github.com/D4Vinci/Scrapling/issues/322)).

### Documentation {#v0.4.9-docs}

- **Clarification : l’installation par défaut contient seulement le moteur d’analyse**, et les fetchers et spiders nécessitent les extras (résout [#343](https://github.com/D4Vinci/Scrapling/issues/343)).
- **Correction du nom de l’image Docker dans les exemples restants**, par @evanclan dans [#315](https://github.com/D4Vinci/Scrapling/pull/315).
- **Correction d’un lien cassé dans le guide de contribution**, par @Bortlesboat dans [#320](https://github.com/D4Vinci/Scrapling/pull/320).

## [v0.4.8](https://github.com/D4Vinci/Scrapling/releases/tag/v0.4.8) - 2026-05-11 {#v0.4.8}

**Une grande mise à jour des spiders qui améliore le système d’exploration 🕷️**

### 🚀 Nouveautés et améliorations d’utilisation {#v0.4.8-new-stuff-and-quality-of-life-changes}

- **Ajout de l’outil `LinkExtractor`** dans `scrapling.spiders.LinkExtractor` pour extraire les URL d’une `Response`. Il offre de nombreux contrôles (consultez la [documentation](spiders/generic-templates.md))

    ```python
    from scrapling.spiders import LinkExtractor

    extractor = LinkExtractor(allow=r"/posts/", deny_domains=["ads.example.com"])
    ```

- **Ajout des modèles de spiders génériques `CrawlSpider` et `CrawlRule`** pour ne plus réécrire le même code de « suivi des liens correspondant à ce motif ». Redéfinissez `rules()` pour renvoyer une liste d’objets `CrawlRule`, chacun associé à un `LinkExtractor`. (Consultez la [documentation](spiders/generic-templates.md))

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

- **Ajout du modèle `SitemapSpider`**, qui démarre une exploration directement depuis un sitemap ou des URL de `robots.txt`. Il gère les sitemaps compressés avec gzip et offre de nombreux contrôles et options. Les URL sont réparties selon les règles d’exploration, comme pour **CrawlSpider** ci-dessus. (Consultez la [documentation](spiders/generic-templates.md))

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

- **La relocalisation adaptative utilise maintenant un seuil de similarité de 40 % par défaut**, au lieu de `0`, dans toutes les méthodes. Cela améliore le fonctionnement du mode adaptatif. Si aucun élément ne dépasse le seuil, un avertissement indique maintenant le meilleur score trouvé, pour que vous puissiez réduire `percentage` en connaissance de cause si nécessaire.

- **Mise à jour de tous les navigateurs et des empreintes**. Exécutez de nouveau `scrapling install  --force` après la mise à jour pour actualiser les navigateurs et les empreintes.

### 🐛 Corrections de bugs {#v0.4.8-bug-fixes}

- **Correction de `Fetcher.configure(...)`, qui ne s’appliquait pas aux appels par requête**. La même correction a été appliquée à `AsyncFetcher`.
- **Correction du calcul incorrect des empreintes de requêtes qui provoquait des requêtes en double dans les spiders**, par @yetval dans [#255](https://github.com/D4Vinci/Scrapling/pull/255).
- **Le moteur d’extraction adaptative signale maintenant les correspondances faibles.** Avec le changement de seuil ci-dessus, vous recevez maintenant un avertissement au lieu d’un élément trompeur présenté comme la « meilleure estimation » quand la relocalisation échoue.

### Documentation {#v0.4.8-docs}

- **Mise à jour des anciens exemples de code** dans toute la documentation pour correspondre à la version actuelle.
- **Amélioration du copier-coller de code** sur le site de documentation et réduction de la skill pour agents afin de consommer moins de tokens à chaque appel.

## [v0.4.7](https://github.com/D4Vinci/Scrapling/releases/tag/v0.4.7) - 2026-04-17 {#v0.4.7}

**Une mise à jour qui permet à vos agents IA de voir les pages 📸**

### 🚀 Nouveautés et améliorations d’utilisation {#v0.4.7-new-stuff-and-quality-of-life-changes}

- **Ajout de l’outil MCP `screenshot`**, qui capture une page et la renvoie sous forme de véritable bloc MCP `ImageContent` pour que le modèle puisse la voir. L’outil exige une session de navigateur ouverte : appelez d’abord `open_session` (avec `dynamic` ou `stealthy`), puis passez le `session_id` ici. Il prend en charge PNG et JPEG, les captures de page entière, la qualité JPEG et les contrôles d’attente habituels (`wait`, `wait_selector`, `network_idle`, `timeout`). (Implémente [#244](https://github.com/D4Vinci/Scrapling/issues/244))
- **Ajout d’un paramètre `session_id` personnalisé à `open_session`** pour nommer les sessions de façon utile (`"search"`, `"checkout"`) au lieu de la valeur hexadécimale aléatoire de 12 caractères utilisée par défaut. Par @hauntedhost dans [#243](https://github.com/D4Vinci/Scrapling/pull/243)

### 🐛 Corrections de bugs {#v0.4.7-bug-fixes}

- **Correction de la corruption de l’état de `FetcherSession` et d’un plantage à la fermeture d’une session à démarrage différé**. Par @yetval dans [#245](https://github.com/D4Vinci/Scrapling/pull/245)
- **Correction de `TypeError: Session.request() got an unexpected keyword argument 'block_ads'`** lors de l’utilisation de l’option `--ai-targeted` de la CLI avec les commandes HTTP. Par @voidborne-d dans [#249](https://github.com/D4Vinci/Scrapling/pull/249) (corrige [#247](https://github.com/D4Vinci/Scrapling/issues/247))

### Traductions {#v0.4.7-translations}

- **Ajout d’une traduction du README en portugais brésilien**, par @rgomids dans [#250](https://github.com/D4Vinci/Scrapling/pull/250)

## [v0.4.6](https://github.com/D4Vinci/Scrapling/releases/tag/v0.4.6) - 2026-04-13 {#v0.4.6}

**Une mise à jour centrée sur la discrétion du navigateur, la confidentialité et l’expérience de développement 🔒**

### 🚀 Nouveautés et améliorations d’utilisation {#v0.4.6-new-stuff-and-quality-of-life-changes}

- **Ajout du blocage de publicités intégré** aux fetchers de navigateur. Passez `block_ads=True` pour bloquer les requêtes vers environ 3 500 domaines connus de publicité et de suivi dès l’interception des routes : sans DNS, sans TCP, avec annulation immédiate. Vous pouvez le combiner avec `blocked_domains` pour vos propres listes. Le serveur MCP et le mode `--ai-targeted` de la CLI l’activent automatiquement pour économiser des tokens et accélérer le chargement des pages.

    ```python
    page = StealthyFetcher.fetch('https://example.com', block_ads=True)
    ```

- **Ajout de la prise en charge de DNS-over-HTTPS** pour éviter les fuites DNS avec les proxies. Passez `dns_over_https=True` pour envoyer les requêtes DNS au service DoH de Cloudflare. Ainsi, la résolution DNS ne révèle pas votre position réelle même quand le trafic HTTP passe par un proxy.

    ```python
    page = StealthyFetcher.fetch('https://example.com', proxy='http://proxy:8080', dns_over_https=True)
    ```

- **Ajout du callback `page_setup`** aux fetchers de navigateur. Cette fonction s’exécute avant `page.goto()` et permet d’enregistrer des écouteurs d’événements, des routes ou des scripts qui doivent être prêts avant la navigation. Elle complète `page_action` (qui s’exécute après la navigation). (Résout [#237](https://github.com/D4Vinci/Scrapling/issues/237))

    ```python
    def capture_websockets(page):
        page.on("websocket", lambda ws: print(f"WS: {ws.url}"))

    page = DynamicFetcher.fetch('https://example.com', page_setup=capture_websockets)
    ```

- **Ajout des options CLI `--block-ads` et `--dns-over-https`** aux commandes `fetch` et `stealthy-fetch`.

### 🐛 Corrections de bugs {#v0.4.6-bug-fixes}

- **Correction de l’alias de type `Seconds`**, qui rejetait les valeurs décimales. Passer `wait=1.5` ou `timeout=500.0` aux fetchers de navigateur provoquait une erreur de type, car l’alias traitait `float` comme des métadonnées plutôt que comme un type. Par @kuishou68 dans [#240](https://github.com/D4Vinci/Scrapling/pull/240)
- **Correction des segments ID en double dans la génération de sélecteurs avec un chemin complet**. Le sélecteur des éléments ayant un attribut `id` était ajouté deux fois lors de la génération de chemins CSS/XPath complets, ce qui produisait des sélecteurs comme `body > #main > #main > #target > #target`. Les chemins XPath complets produisaient aussi des conditions `[@id='x']` isolées (XPath non valide) au lieu de `*[@id='x']` ; ce problème a été corrigé. Par @sjhddh dans [#241](https://github.com/D4Vinci/Scrapling/pull/241)
- **Correction des paramètres manquants dans les signatures du shell**. Les signatures des fonctions du shell interactif ne contenaient pas `blocked_domains`, `block_ads`, `retries`, `retry_delay`, `capture_xhr`, `executable_path` et `dns_over_https`.

## [v0.4.5](https://github.com/D4Vinci/Scrapling/releases/tag/v0.4.5) - 2026-04-07 {#v0.4.5}

**Une mise à jour avec une grande amélioration d’utilisation pour les développeurs de spiders et quelques corrections importantes 🎉**

### 🚀 Nouveautés et améliorations d’utilisation {#v0.4.5-new-stuff-and-quality-of-life-changes}

- **Mode de développement des spiders** : modifier la logique de `parse()` d’un spider exigeait auparavant de solliciter les serveurs cibles à chaque exécution. C’était lent, générait du trafic et risquait de faire limiter vos requêtes alors que vous ajustiez encore vos sélecteurs. Le nouveau mode de développement met chaque réponse en cache sur disque à la première exécution, puis les relit sur disque à chaque exécution suivante. Vous pouvez donc ajuster les callbacks et relancer autant de fois que vous voulez sans envoyer une seule requête réseau. Activez-le avec un attribut de classe :

    ```python
    class MySpider(Spider):
        name = "my_spider"
        start_urls = ["https://example.com"]
        development_mode = True

        async def parse(self, response):
            yield {"title": response.css("title::text").get("")}
    ```

    Le cache se trouve dans `.scrapling_cache/{spider.name}/` par défaut, et vous pouvez changer son emplacement avec `development_cache_dir`. Deux nouveaux compteurs, `cache_hits` et `cache_misses`, indiquent les performances du cache. La relecture du cache ignore `download_delay`, la limitation du rythme et le chemin de nouvelle tentative des requêtes bloquées, pour que les essais soient aussi rapides que le disque le permet. Ne déployez pas un spider avec `development_mode = True` : c’est un outil de développement, pas un cache de production. Consultez la [documentation](spiders/advanced.md#development-mode) pour tous les détails.

- **Des redirections plus sûres par défaut** : `follow_redirects` vaut maintenant `"safe"` par défaut pour tous les fetchers HTTP, le serveur MCP et le shell. Les redirections restent suivies, mais celles qui ciblent des IP internes ou privées (loopback, réseaux privés, link-local) sont rejetées. Cela vous protège contre SSRF lors de l’extraction de données depuis des URL fournies par les utilisateurs. Passez `follow_redirects="all"` pour retrouver l’ancien comportement, ou `False` pour désactiver entièrement les redirections.

### 🐛 Corrections de bugs {#v0.4.5-bug-fixes}

- **L’arrêt forcé ne perd plus votre point de reprise** : appuyer deux fois sur Ctrl+C (arrêt forcé) dans un spider avec `crawldir` activé pouvait entrer en conflit avec l’écriture du point de reprise. Le contexte d’annulation arrêtait la tâche avant la fin du pickle, laissait `paused=False` et déclenchait le nettoyage qui *supprime* le point de reprise précédent. L’arrêt forcé d’une longue exploration pouvait ainsi faire perdre toute la progression que vous tentiez de sauver. Le moteur écrit maintenant le point de reprise **avant** d’appeler `cancel_scope.cancel()`, pour qu’un arrêt forcé conserve toujours le dernier état en attente. Par @voidborne-d dans [#230](https://github.com/D4Vinci/Scrapling/pull/230).

## [v0.4.4](https://github.com/D4Vinci/Scrapling/releases/tag/v0.4.4) - 2026-04-05 {#v0.4.4}

**Une nouvelle mise à jour avec des améliorations importantes des spiders et des corrections de bugs 🎉**

### 🚀 Nouveautés et améliorations d’utilisation {#v0.4.4-new-stuff-and-quality-of-life-changes}
- **Ajout du respect de robots.txt au système de spiders** avec la nouvelle option `robots_txt_obey`. Quand elle est activée, le spider récupère et respecte automatiquement les règles de robots.txt avant l’exploration, y compris les directives `Disallow`, `Crawl-delay` et `Request-rate`. Les fichiers robots.txt sont récupérés en parallèle et mis en cache par domaine pour toute l’exploration. Par @AbdullahY36 dans [#226](https://github.com/D4Vinci/Scrapling/pull/226)
- **Ajout du chargement préalable du cache de robots.txt**, pour récupérer et analyser les fichiers robots.txt de tous les domaines de start_urls avant le début de la boucle d’exploration. Cela évite une attente lors de la première requête vers chaque domaine.
- **Ajout de la statistique `robots_disallowed_count`** à `CrawlStats` pour compter les requêtes bloquées par les règles de robots.txt pendant l’exploration.

Consultez les détails sur le site [ici](spiders/getting-started.md#robotstxt-compliance)

### 🐛 Corrections de bugs {#v0.4.4-bug-fixes}
- **Correction d’un problème important de MRO avec `ProxyRotator`** : la méthode provisoire `_build_context_with_proxy` masquait l’implémentation réelle des classes enfants et la rotation des proxies levait toujours `NotImplementedError` (corrige [#215](https://github.com/D4Vinci/Scrapling/issues/215)). Merci, @yetval
- **Correction d’une fuite dans le pool de pages** avec la rotation des proxies par requête dans les sessions du navigateur. Les pages créées dans des contextes temporaires n’étaient pas retirées du pool au nettoyage, ce qui accumulait des références obsolètes au fil du temps. Par @yetval dans [#223](https://github.com/D4Vinci/Scrapling/pull/223)
- **Correction d’une vérification de type manquante** dans le fetcher statique : `curl_cffi` pouvait renvoyer `None` depuis `session.request()`, ce qui provoquait des erreurs ensuite.

### Autres changements {#v0.4.4-other}
- Mise à jour des dépendances, pour disposer des dernières empreintes et d’autres nouveautés.
- Ajout de `protego` comme nouvelle dépendance dans le groupe optionnel `fetchers` pour analyser robots.txt.

## [v0.4.3](https://github.com/D4Vinci/Scrapling/releases/tag/v0.4.3) - 2026-03-30 {#v0.4.3}

**Une nouvelle mise à jour avec de nombreux changements importants 🎉**

### 🚀 Nouveautés et améliorations d’utilisation {#v0.4.3-new-stuff-and-quality-of-life-changes}
- **Ajout d’un nouvel outil MCP** pour ouvrir un navigateur persistant, normal ou discret, et continuer à l’utiliser avec les autres outils, ainsi que d’un autre outil pour le fermer. ([Exemples](https://github.com/D4Vinci/Scrapling/blob/v0.4.3/docs/ai/mcp-server.md#examples))
- **Ajout d’un nouvel outil MCP** pour lister toutes les sessions du navigateur existantes, destiné à être utilisé avec les nouveaux outils.
- **Ajout d’une nouvelle option aux sessions du navigateur** pour collecter automatiquement toutes les requêtes en arrière-plan pendant une requête (résout [#159](https://github.com/D4Vinci/Scrapling/pull/159)) [[Exemples](https://github.com/D4Vinci/Scrapling/blob/v0.4.3/docs/fetching/dynamic.md#capturing-xhrfetch-requests)].
- **Ajout d’un nouveau nettoyage** pour protéger le serveur MCP contre les attaques courantes d’injection de prompts en supprimant le contenu caché ou invisible.
- **Ajout d’une nouvelle option de ligne de commande**, appelée `--ai-targeted`, aux commandes d’extraction Web pour adapter le contenu à l’IA et le protéger contre les attaques courantes d’injection de prompts, comme le serveur MCP.
- **Ajout d’une nouvelle option aux sessions du navigateur**, appelée `executable_path`, pour définir un chemin de navigateur personnalisé (résout [#202](https://github.com/D4Vinci/Scrapling/pull/202))
- **Réorganisation** du code du serveur MCP pour simplifier sa maintenance, et passage de tous les outils en mode asynchrone.
- **Réorganisation** du code des commandes CLI pour simplifier sa maintenance et le réduire de 210 lignes.

### 🐛 Corrections de bugs {#v0.4.3-bug-fixes}
- Correction d’un bug pour conserver la méthode HTTP lors des nouvelles tentatives dans la session du spider, par @karesansui-u dans [#201](https://github.com/D4Vinci/Scrapling/pull/201)
- Ajout d’un nombre maximal de tentatives pour récupérer le contenu de la page afin d’éviter une boucle infinie, par @haosenwang1018 et @D4Vinci dans [#197](https://github.com/D4Vinci/Scrapling/pull/197)
- Remplacement du `raise` sans argument par `return False` dans `_restore_from_checkpoint`, par @haosenwang1018 dans [#196](https://github.com/D4Vinci/Scrapling/pull/196)
- Remplacement de `get_all` par `getall` dans `Texthandler` pour correspondre à la classe Selector.

### Amélioration des tests et de leur couverture {#v0.4.3-coverage-tests-improvement}
- Ajout de tests des cas limites de `_normalize_credentials`, par @Bortlesboat dans [#192](https://github.com/D4Vinci/Scrapling/pull/192)
- Ajout de tests du cycle d’enregistrement et de récupération, ainsi que du stockage principal, par @haosenwang1018 dans [#193](https://github.com/D4Vinci/Scrapling/pull/193)
- Ajout d’une couverture des chemins regex de `TextHandler` et de `TextHandlers.re()`, par @haosenwang1018 dans [#194](https://github.com/D4Vinci/Scrapling/pull/194)
- Ajout de tests des cas limites de `filter`, `iterancestors` et `find_similar`, par @awanawana dans [#200](https://github.com/D4Vinci/Scrapling/pull/200)

### Amélioration de l’Agent Skill {#v0.4.3-agent-skill-improvement}
- Correction des liens Markdown cassés dans les références de la skill, par @yetval dans [#204](https://github.com/D4Vinci/Scrapling/pull/204)
- Amélioration de la structure de la skill pour mieux passer la validation de [Clawhub](https://clawhub.ai/d4vinci/scrapling-official).
- La skill impose maintenant l’option de ligne de commande `--ai-targeted` lors de l’extraction par des commandes.

### Amélioration de la documentation {#v0.4.3-docs-improvement}
- Ajout d’une traduction du README en coréen, par @greatsk55 dans [#187](https://github.com/D4Vinci/Scrapling/pull/187)
- Correction des espaces entre les caractères CJK et latins dans les README chinois et japonais.
- Correction des liens cassés de l’ancienne présentation du site.

## [v0.4.2](https://github.com/D4Vinci/Scrapling/releases/tag/v0.4.2) - 2026-03-08 {#v0.4.2}

**Une nouvelle mise à jour de maintenance avec des changements importants**

#### Corrections de bugs {#v0.4.2-bug-fixes}
- La fonction `get_all_text()` récupère désormais aussi les nœuds de texte qui suivent les éléments. Le serveur MCP et les commandes peuvent ainsi lire du texte qui était ignoré auparavant ([#168](https://github.com/D4Vinci/Scrapling/pull/168)). Merci @mhillebrand
- Referer renvoie désormais l’URL de base de Google au lieu d’une URL de recherche Google. La logique précédente était incorrecte et pouvait produire un indice permettant de reconnaître l’empreinte du navigateur ([#179](https://github.com/D4Vinci/Scrapling/pull/179)). Merci @Bortlesboat
- Correction d’un problème lors de l’assemblage des options de lancement supplémentaires dans tous les navigateurs. Merci @rostchri
- Correction d’un problème d’annotations de types qui provoquait un plantage avec les versions de Python antérieures à 3.12. (Résout [#163](https://github.com/D4Vinci/Scrapling/issues/163))

#### Autres changements {#v0.4.2-other}
- Ajout d’une Agent Skill pour Claude Code / OpenClaw et d’autres outils d’agents IA.
- Ajout de l’Agent Skill à Clawhub.
- Mise à jour de tous les navigateurs et de Playwright vers les dernières versions.
- Ajout d’une traduction française du fichier README principal.

## [v0.4.1](https://github.com/D4Vinci/Scrapling/releases/tag/v0.4.1) - 2026-02-27 {#v0.4.1}

**Une nouvelle mise à jour avec de nombreux changements importants**

### 🚀 Nouveautés et améliorations d’utilisation {#v0.4.1-new-stuff-and-quality-of-life-changes}
- **Expressions régulières plus précises** pour détecter les défis Cloudflare (Merci à @Rinz27 [#133](https://github.com/D4Vinci/Scrapling/pull/133))
- **Résolution des défis Cloudflare plus rapide et plus efficace**. Elle est désormais presque deux fois plus rapide.
- **Amélioration de la résolution des défis Cloudflare** pour les sites qui affichent parfois la page Cloudflare deux fois avant de rediriger vers le site principal.
- **Amélioration du mode furtif et de la vitesse du navigateur furtif** grâce à la suppression des fichiers JS injectés.
- **Amélioration du schéma MCP** pour qu’il soit accepté par OpenCode (Merci à @robin-ede [#137](https://github.com/D4Vinci/Scrapling/pull/137))
- **Schéma MCP encore plus conforme au protocole** pour qu’il soit accepté par VS Code Copilot et d’autres outils stricts. (Résout #150 )
- **Forte réduction de la consommation de tokens du serveur MCP** en supprimant les balises HTML inutiles quand l’option `main_content_only` est activée.
- Correction de la page PyPI et ajout des fichiers nécessaires pour inscrire le serveur MCP au registre des serveurs MCP.
- Ajout d’un exemple montrant comment installer les dépendances des navigateurs depuis le code plutôt que depuis la ligne de commande, pour faciliter l’automatisation.
- Amélioration de tous les workflows avec les dernières versions des actions (Merci à @salmanmkc [#143](https://github.com/D4Vinci/Scrapling/pull/143)/[#144](https://github.com/D4Vinci/Scrapling/pull/144))

## [v0.4](https://github.com/D4Vinci/Scrapling/releases/tag/v0.4) - 2026-02-15 {#v0.4}

**La plus grande version de Scrapling à ce jour : framework de spiders, rotation de proxies et améliorations majeures du parser**

Cette version apporte un framework de spiders et d’exploration entièrement asynchrone, une gestion intelligente des proxies et des changements importants de l’API qui rendent Scrapling plus puissant et plus cohérent. Lisez attentivement la section sur les changements incompatibles avant la mise à jour.

### 🕷️ Framework de spiders {#v0.4-spider-framework}

Un nouveau framework d’exploration asynchrone basé sur `anyio` pour une extraction organisée et à grande échelle :

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

-  **API de spiders similaire à Scrapy** : Définissez des spiders avec `start_urls`, des callbacks `parse` asynchrones, des objets `Request`/`Response` et une file de priorité.
- **Exploration concurrente** : Limites de concurrence, contrôle du débit par domaine et délais entre les téléchargements configurables.
- **Prise en charge de plusieurs sessions** : Une interface commune pour les requêtes HTTP et les navigateurs furtifs sans interface graphique dans un même spider. Dirigez les requêtes vers différentes sessions grâce à leur ID. Le démarrage des sessions au premier besoin est pris en charge.
- **Pause et reprise** : Conservation de l’état de l’exploration grâce à des points de reprise. Appuyez sur Ctrl+C pour arrêter proprement, puis redémarrez pour reprendre là où vous en étiez.
- **Mode streaming** : Recevez les éléments dès leur extraction via `async for item in spider.stream()`, avec des statistiques en temps réel. Idéal pour les interfaces, les pipelines et les longues explorations.
- **Détection des requêtes bloquées** : Détection et nouvelles tentatives automatiques des requêtes bloquées, avec une logique personnalisable.
- **Export intégré** : Exportez les résultats avec des hooks et votre propre pipeline, ou utilisez l’export intégré JSON/JSONL avec `result.items.to_json()` / `result.items.to_jsonl()`, respectivement.
- **Hooks du cycle de vie** : `on_start()`, `on_close()`, `on_error()`, `on_scraped_item()` et d’autres hooks pour contrôler tout le cycle de vie de l’exploration.
- **Statistiques détaillées d’exploration** : Suivi des requêtes, réponses, octets, codes de statut, proxies, détails par domaine et session, nombres de messages par niveau de log, et plus encore.
- **Prise en charge d’uvloop** : Passez `use_uvloop=True` à `spider.start()` pour accélérer l’exécution asynchrone quand uvloop est disponible.

Une nouvelle section du site présente tous les détails. Cliquez [ici](spiders/architecture.md)

### 🔄 Rotation de proxies {#v0.4-proxy-rotation}

* Nouvelle classe `ProxyRotator` avec une rotation sûre entre threads. Elle fonctionne avec tous les fetchers et toutes les sessions :

  ```python
  from scrapling import ProxyRotator
  rotator = ProxyRotator(["http://proxy1:8080", "http://proxy2:8080"])
  Fetcher.get(url, proxy_rotator=rotator)
  ```

* **Stratégies de rotation personnalisées** : Créez votre propre logique de rotation de proxies
* **Changement de proxy par requête** : Passez `proxy=` à un appel individuel de `get()`/`post()`/`fetch()` pour remplacer le proxy de la session pour cette requête.

### 🌐 Améliorations des fetchers de navigateur {#v0.4-browser-fetcher-improvements}

* **Blocage de domaines** : Nouveau paramètre `blocked_domains` sur `DynamicFetcher`/`StealthyFetcher` pour bloquer les requêtes vers des domaines précis. Leurs sous-domaines sont inclus automatiquement.
* **Nouvelles tentatives automatiques** : Les fetchers de navigateur réessaient désormais en cas d’échec avec les paramètres `retries` (valeur par défaut : 3) et `retry_delay` (valeur par défaut : 1s). Cela inclut la détection des erreurs liées aux proxies.
* **Métadonnées de réponse** : Le dictionnaire `Response.meta` enregistre automatiquement le proxy utilisé et intègre les métadonnées de la requête.
* **Response.follow()** : Créez des objets `Request` pour les requêtes suivantes avec une gestion automatique du referer, conçus pour le système de spiders.
* **Aucune lecture automatique** : Les sessions de navigateur bloquent désormais le contenu en lecture automatique, qui causait des problèmes auparavant.
* **Vitesse** : Amélioration de la discrétion et de la vitesse en ajustant les options de lancement du navigateur.

### 🔧 Corrections de bugs et améliorations {#v0.4-bug-fixes-improvements}
- **Optimisation du parser** : Optimisation des opérations répétées pour améliorer les performances.
- **Pages en erreur** : Correction d’un bug qui empêchait le navigateur de se fermer quand les pages renvoyaient des erreurs.
- **Corps vide** : Prise en charge des réponses dont le corps est vide.
- **Boucle Playwright** : Correction d’un problème qui laissait la boucle Playwright ouverte quand la connexion CDP échouait
- **Sécurité des types** : Correction de toutes les erreurs mypy et ajout d’annotations de types dans les corps de fonctions qui n’en avaient pas. Ajout de mypy et pyright au workflow de CI.

### ⚠️ Changements incompatibles {#v0.4-breaking-changes}

* **Suppression de `css_first`/`xpath_first`** : Utilisez `css('.selector').first`, `css('.selector')[0]` ou `css('.selector').get()` à la place.
* **Toutes les sélections renvoient désormais `Selectors`** : `css('::text')`, `xpath('//text()')`, `css('::attr(href)')` et `xpath('//@href')` renvoient maintenant `Selectors`, qui enveloppe les nœuds de texte dans des objets `Selector` avec `tag="#text"`, au lieu de `TextHandlers`. Cela rend l’API cohérente entre toutes les méthodes de sélection et les annotations de types.
* **`Response.body` est toujours de type `bytes`** : Auparavant, il pouvait être de type `str` ou `bytes`. Il renvoie désormais toujours `bytes`.
* **Comportement de `get()`/`getall()`** : Sur `Selector`, `get()` renvoie `TextHandler` (HTML sérialisé ou valeur textuelle) et `getall()` renvoie `TextHandlers`. Alias : `extract_first = get`, `extract = getall`. L’ancien `get_all()` de `Selectors` est supprimé.
* **`Selectors.first`/`.last`** : Accès sûr qui renvoie `Selector | None` au lieu de lever `IndexError`.
* **Constantes internes renommées** : `DEFAULT_FLAGS` → `DEFAULT_ARGS`, `DEFAULT_STEALTH_FLAGS` → `STEALTH_ARGS`, `HARMFUL_DEFAULT_ARGS` → `HARMFUL_ARGS`, `DEFAULT_DISABLED_RESOURCES` → `EXTRA_RESOURCES`.

### 🔨 Autres changements {#v0.4-other-changes}

* **Changements de dépendances** : Remplacement de `tldextract` par `tld`, suppression du fichier interne `_html_utils.py` au profit de `w3lib.html.replace_entities`, et ajout de `typing_extensions` comme dépendance obligatoire.
* **Refonte de la documentation** : Migration complète de MkDocs vers Zensical, nouvelle section sur les spiders, mise à jour de toutes les pages existantes et ajout de nouvelles références d’API.

## [v0.3.14](https://github.com/D4Vinci/Scrapling/releases/tag/v0.3.14) - 2026-01-03 {#v0.3.14}

**Une petite mise à jour de maintenance pour corriger des problèmes apparus sur certains appareils avec la v0.3.13**

- Désactivation du mode de navigation privée dans `StealthyFetcher` et ses classes de session, car il empêchait la conservation des cookies entre les pages sur Windows. Ce problème ne se produisait pas sur MacOS ni Linux (Corrige [#123](https://github.com/D4Vinci/Scrapling/issues/123) ; merci à @frugality4121 de l’avoir signalé et à @gembleman d’avoir indiqué la solution).
- La version de browserforge est désormais fixée à la plus récente pour résoudre le problème des anciens modèles d’en-têtes chez les utilisateurs qui avaient déjà une ancienne version de browserforge.

## [v0.3.13](https://github.com/D4Vinci/Scrapling/releases/tag/v0.3.13) - 2026-01-01 {#v0.3.13}

**Une mise à jour majeure avec des améliorations dans de nombreux domaines, mais aussi beaucoup de changements incompatibles pour de bonnes raisons. Lisez ce qui suit avant de mettre à jour**

* Pour plusieurs raisons, nous avons décidé de ne plus utiliser Camoufox du tout à partir de maintenant. Nous pourrions y revenir si son développement se poursuit. Si vous préférez continuer à utiliser Camoufox comme avant cette version, consultez les instructions dans cette [section](https://github.com/D4Vinci/Scrapling/blob/v0.3.13/docs/fetching/stealthy.md#using-camoufox-as-an-engine).

* Nous utilisions auparavant patchright dans le mode furtif de `DynamicFetcher` et de ses classes de session. Nous avons retiré ce mode de ces classes et commencé à utiliser patchright dans `StealthyFetcher` et ses classes de session, avec BEAUCOUP d’améliorations, comme vous le verrez, qui renforcent la discrétion au-delà de ce que patchright apporte déjà.

**Cela rend `StealthyFetcher` et ses classes de session 101 % plus rapides, réduit leur utilisation de mémoire et d’espace et retire environ ~400 lignes de code. Surtout, ils sont plus stables que lorsque nous utilisions Camoufox.**

Cela réduit aussi le temps d’installation de la commande `scrapling install` et la taille de l’image Docker, améliore le déroulement des tests dans la CI de GitHub et rend scrapling moins déroutant pour les nouveaux utilisateurs.

### Changements incompatibles {#v0.3.13-breaking-changes}
1. L’argument `stealth` a été supprimé de `DynamicFetcher` et de sa classe de session, tandis que `hide_canvas` a été déplacé vers `StealthyFetcher` et ses classes de session.
2.  L’argument `disable_webgl` a été déplacé de `DynamicFetcher` vers la classe `StealthyFetcher` et renommé `allow_webgl`. Cela vaut aussi pour toutes les classes de session.
3. La classe `StealthyFetcher` est désormais la nouvelle version furtive de `DynamicFetcher`. Les arguments suivants sont donc supprimés : `block_images`, `humanize`, `addons`, `os_randomize`, `disable_ads` et `geoip`. J’ai essayé de les reproduire dans Chromium, mais chacun posait un problème particulier. Cela pourrait changer dans les prochaines versions avant la v0.4.

Passons aux bonnes nouvelles : nous avons amélioré et corrigé beaucoup de choses :)

### Améliorations {#v0.3.13-improvements}
- Vous savez déjà que `StealthyFetcher` et ses classes de session sont 101 % plus rapides, mais `DynamicFetcher` et sa classe de session sont aussi 20 % plus rapides.
- L’algorithme de résolution des défis Cloudflare a été amélioré pour terminer plus vite et traiter plus de cas. Grâce à la réorganisation du code, attendez-vous aussi à une résolution des captchas deux fois plus rapide !
- Tous les fetchers utilisent désormais moins de mémoire.
- Le serveur MCP utilise moins de tokens pour vous faire économiser davantage !
- L’image Docker est désormais 60 % plus petite.
- Tout le site de documentation a été mis à jour avec les nouveautés. Les explications sont plus claires, de nombreuses sections ont été raccourcies, des exemples et des arguments manquants ont été ajoutés, la référence de l’API comprend des graphiques et de nombreuses autres améliorations ont été apportées. Le site charge désormais 130 % plus vite, utilise moins de données et est mieux adapté au référencement SEO.

### Corrections {#v0.3.13-fixes}
- Ajout des arguments manquants dans les raccourcis du shell de web scraping, et amélioration de leur précision.
- Correction d’un problème où `google_search` créait un referer Google même si l’URL pointait vers localhost ou une adresse IP.

## [v0.3.12](https://github.com/D4Vinci/Scrapling/releases/tag/v0.3.12) - 2025-12-18 {#v0.3.12}

### Ce qui a changé {#v0.3.12-what-s-changed}
- Ajout aux classes `DynamicSession`/`AsyncDynamicSession` d’un argument nommé `timezone_id`. Il permet de régler le fuseau horaire du navigateur pour qu’il corresponde à celui du proxy ou VPN utilisé. Les sites ne peuvent ainsi plus détecter le proxy grâce à une différence de fuseau horaire.
- Amélioration de la conversion automatique des réponses en JSON.
- La fonction interne `__create__` a été renommée `start` dans les classes de session des fetchers, pour faciliter leur utilisation hors du contexte `with`.
- Mise à jour de `curl_cffi` et d’autres dépendances vers les dernières versions.

## [v0.3.11](https://github.com/D4Vinci/Scrapling/releases/tag/v0.3.11) - 2025-12-03 {#v0.3.11}

### Ce qui a changé {#v0.3.11-what-s-changed}
- Amélioration de la gestion des erreurs de délai d’attente quand `network_idle` est utilisé sur un site instable, comme un site qui lit du contenu multimédia en continu.
- Correction de l’autocomplétion du raccourci `stealthy_fetch` dans le shell de web scraping

## [v0.3.10](https://github.com/D4Vinci/Scrapling/releases/tag/v0.3.10) - 2025-11-26 {#v0.3.10}

**Une mise à jour de maintenance avec de nombreux changements importants, dont certains peuvent être incompatibles**

- **Résolution** de tous les problèmes d’encodage grâce à une meilleure approche qui gère les pages dont l’encodage n’est pas déclaré correctement (Merci à @Kemsty2 pour ses efforts pour le signaler dans [#110](https://github.com/D4Vinci/Scrapling/issues/110) [#111](https://github.com/D4Vinci/Scrapling/pull/111) )
- **Résolution** d’un problème de logique dans le remplacement des paramètres de session par les paramètres de requête dans tous les fetchers de navigateur, présent depuis la v0.3
- **Correction** des signatures des raccourcis du shell interactif de web scraping, pour une autocomplétion complète de ces raccourcis. Ce problème existait lui aussi depuis la v0.3.
- **Mise à jour** de la version de la base de données Maxmind, ce qui améliore l’argument `geoip` de `StealthyFetcher` et de ses classes de session.
- **Mise à jour** de tous les navigateurs utilisés vers les dernières versions disponibles.
- **CHANGEMENTS INCOMPATIBLES** : Tous les fetchers ont fait l’objet d’une grande réorganisation, avec des changements intéressants qui pourraient affecter votre code :
    1. Le code de Scrapling comporte désormais environ ~750 lignes de moins et de nombreux changements qui facilitent la maintenance future et réduisent un peu l’utilisation des ressources.
    2. La validation de tous les fetchers et de leurs classes de session est beaucoup plus rapide, ce qui améliore leur vitesse globale.
    3. Pour cela, les fetchers n’acceptent plus d’arguments positionnels autres que `url`. Tous les autres doivent être passés par leur nom. Votre code doit donc utiliser `Fetcher.get('https://google.com', stealthy_headers=True)` et non `Fetcher.get('https://google.com', True)`, si vous le faisiez ainsi pour une raison quelconque !
    4. Depuis la v0.3, une différence gênante existait entre les fetchers de navigateur et leurs classes de session : l’argument qui permettait de configurer le parser par requête s’appelait `custom_config`, contre `selector_config` dans les classes de session. Cette réorganisation a permis d’unifier le nom en `selector_config` sans casser votre code. Le nom principal est donc maintenant `selector_config`, avec une compatibilité pour l’ancien argument `custom_config`. L’autocomplétion sera disponible uniquement pour `selector_config`.
    5. Pour permettre tous ces changements, les annotations de types des fonctions des fetchers sont désormais générées dynamiquement. Si l’autocomplétion ne fonctionne pas correctement dans votre IDE, vérifiez que vous utilisez une version récente. Nous avons testé presque tous les IDE et éditeurs connus.

> Nous avons aussi mis à jour toutes les tables de performances avec les chiffres actuels, comparés aux dernières versions de toutes les bibliothèques alternatives.

## [v0.3.9](https://github.com/D4Vinci/Scrapling/releases/tag/v0.3.9) - 2025-11-17 {#v0.3.9}

**Une nouvelle mise à jour avec de nombreux changements importants**

### 🚀 Nouveautés et améliorations d’utilisation {#v0.3.9-new-stuff-and-quality-of-life-changes}
- L’argument `impersonate` de `Fetcher` et `FetcherSession` accepte désormais une liste de navigateurs. La bibliothèque en choisit un au hasard pour chaque requête.

```python
from scrapling.fetchers import FetcherSession

with FetcherSession(impersonate=['chrome', 'firefox', 'safari']) as s:
  s.get('https://github.com/D4Vinci/Scrapling')
```

- Un nouvel argument de la méthode `clean` de `TextHandler` permet de retirer facilement les entités HTML du texte actuel.
- Améliorations majeures de la documentation, avec des explications plus précises de nombreuses parties et des traductions automatiques du fichier `README.md` principal.

### 🐛 Corrections de bugs {#v0.3.9-bug-fixes}
- Correction d’un problème important lors de la récupération des réponses des fetchers de navigateur. Une détection intelligente du type de contenu garantit désormais que `response.body` contient le contenu rendu par le navigateur uniquement s’il s’agit de HTML. Sinon, il contient le contenu brut de la dernière requête. Cela permet de télécharger des fichiers binaires et texte sans les retrouver enveloppés dans des balises HTML, tout en pouvant récupérer le contenu rendu du site quand vous en avez besoin.

### 🔨 Autres changements {#v0.3.9-misc}
- Mise à jour du guide de contribution pour le rendre plus clair et plus simple.
- Ajout d’un workflow qui impose l’utilisation des outils de qualité du code, les mêmes que ceux utilisés comme hooks de pre-commit.

## [v0.3.8](https://github.com/D4Vinci/Scrapling/releases/tag/v0.3.8) - 2025-10-27 {#v0.3.8}

**Une nouvelle mise à jour avec de nombreux changements importants**

### 🚀 Nouveautés et améliorations d’utilisation {#v0.3.8-new-stuff-and-quality-of-life-changes}
- Dans tous les fetchers de navigateur, les sites dont les requêtes ne finissent jamais de charger ne font plus planter le code quand vous utilisez `network_idle`.
- Modification de la logique de collecte et de vérification du contenu des pages dans les fetchers de navigateur, pour rendre les navigateurs aussi stables sur Windows que sur Linux/MacOS. Cette différence de comportement vient de l’implémentation de Playwright sur Windows.
- Réorganisation de toute la logique de validation, ce qui accélère de 8-15 % les requêtes de tous les fetchers de navigateur
- Ajout de l’option `extra_flags` à `DynamicFetcher` et à sa session pour ajouter des options Chrome personnalisées aux options existantes au lancement du navigateur.
- Rétablissement de l’ancienne logique de routage pour capturer les réponses quand `page_action` est utilisé, après le changement de la version précédente. Cela permet de récupérer le dernier contenu de la page si `page_action` le modifie sans envoyer de requête. (Merci à @gembleman de l’avoir signalé dans [#100](https://github.com/D4Vinci/Scrapling/issues/100) et [#102](https://github.com/D4Vinci/Scrapling/pull/102) )

### 🐛 Corrections de bugs {#v0.3.8-bug-fixes}
- Correction d’une faute de frappe dans `load_dom` de la méthode async_fetch de DynamicSession
- Correction d’un problème de résolution des défis Cloudflare qui attendait indéfiniment la disparition des captchas intégrés restant visibles après leur résolution. L’attente est désormais de 30 secondes, après quoi le captcha est considéré comme un type qui ne disparaît pas (Corrige #100 )

### 🔨 Autres changements {#v0.3.8-misc}
- L’image Docker est désormais publiée automatiquement sur Dockerhub et dans le registre de conteneurs de GitHub pour faciliter son utilisation.
- Ajout d’une [nouvelle page de documentation](https://github.com/D4Vinci/Scrapling/blob/v0.3.8/docs/tutorials/external.md) expliquant comment utiliser le navigateur Scrapeless avec Scrapling.

## [v0.3.7](https://github.com/D4Vinci/Scrapling/releases/tag/v0.3.7) - 2025-10-12 {#v0.3.7}

**Une nouvelle mise à jour avec de nombreux changements importants**

### 🚀 Nouveautés et améliorations d’utilisation {#v0.3.7-new-stuff-and-quality-of-life-changes}
- Refonte de l’argument `solve_cloudflare` de `StealthyFetcher` pour résoudre tous les types d’implémentations personnalisées de Turnstile.
- Réorganisation de tout le code pour qu’il passe les contrôles de Pyright, ce qui améliore l’utilisation de tous les IDE et corrige de nombreux bugs.
- Réorganisation de la logique des requêtes pour la rendre plus claire et plus rapide (Résout aussi #97 )
- Ajout de l’option `user_data_dir` à toutes les classes de session de navigateur pour réutiliser les données de sessions précédentes, comme les cookies et le stockage. Si vous ne la renseignez pas, Playwright utilise un répertoire aléatoire à chaque exécution, comme auparavant.
- Ajout de l’option de personnalisation `additional_args` à `Dynamic fetcher` et à sa classe de session pour passer des arguments supplémentaires au contexte Playwright, comme c’était déjà possible avec `StealthyFetcher`.
- Amélioration de la logique de routage qui collecte la dernière réponse de navigation pour tous les navigateurs. Les réponses brutes peuvent ainsi parvenir au parser avant leur traitement par le navigateur, au lieu d’être traitées d’abord par celui-ci comme auparavant. C’est très utile pour les réponses texte et JSON.

### 🐛 Corrections de bugs {#v0.3.7-bug-fixes}
- La nouvelle logique de routage a résolu un problème de récupération du contenu de sites instables sur certains appareils Windows.
- Les réorganisations du code de cette version ont corrigé de nombreux bugs difficiles à repérer et des problèmes inhabituels d’autocomplétion dans certains IDE.
- Nombreuses corrections sur le site de documentation

## [v0.3.6](https://github.com/D4Vinci/Scrapling/releases/tag/v0.3.6) - 2025-10-01 {#v0.3.6}

### 🚀 Nouveautés {#v0.3.6-new-stuff}
- Amélioration de l’argument `solve_cloudflare` de `StealthyFetcher` et de ses classes de session pour résoudre tous les types de défis Turnstile et de pages intermédiaires Cloudflare 🎉
- Le serveur MCP permet désormais d’utiliser `Streamable HTTP` pour rendre le serveur facilement accessible.
- Ajout de la prise en charge de Docker. Une image contenant tous les navigateurs est créée et publiée automatiquement sur Docker Hub à chaque version

### 🐛 Corrections de bugs {#v0.3.6-bug-fixes}
- Correction d’un problème d’encodage du parser qui se produisait dans certains cas, la célèbre erreur `invalid start byte`
- Réorganisation de plusieurs parties de la bibliothèque pour corriger des fuites de mémoire. L’utilisation de la mémoire est désormais nettement plus faible selon votre configuration (Résout aussi #92 )
- Amélioration des annotations de types dans de nombreuses parties du code pour faciliter le travail dans l’IDE (Résout aussi #93 )

## [v0.3.5](https://github.com/D4Vinci/Scrapling/releases/tag/v0.3.5) - 2025-09-20 {#v0.3.5}

**Une version nécessaire qui corrige plusieurs problèmes**

### 🚀 Nouveautés {#v0.3.5-new-stuff}
- Tous les fetchers de navigateur (`DynamicFetcher`/`StealthyFetcher`/...) et leurs classes de session récupèrent désormais les pages 15-20 % plus vite :
    1. La gestion des pages est beaucoup plus rapide grâce à l’amélioration de la logique par @AbdullahY36 dans #87
    2. Optimisation de la logique de validation globale et amélioration de la création des pages pour les requêtes synchrones. Ensemble, ces changements ont apporté de nombreux gains de vitesse

- Améliorations majeures du mode furtif de `DynamicFetcher` et de ses classes de session grâce au remplacement de `rebrowser-playwright` par `PatchRight` :
    1. Avant cette mise à jour, `rebrowser-playwright` était désactivé quand vous activiez `stealth` et `real_chrome`, car ils fonctionnaient mal ensemble. Ce problème n’existe plus avec `PatchRight`
    2. Vous pouvez désormais interagir avec les Shadow Roots fermés, car `PatchRight` les gère automatiquement.

### 🐛 Corrections de bugs {#v0.3.5-bug-fixes}
- Correction d’un bug lors de l’utilisation de la méthode `re` de la classe `Selectors`.
- Correction d’un bug des commandes `uncurl` et `curl2fetcher` du shell de web scraping qui provoquait une mauvaise analyse de l’option `--data-raw` de curl.
- Correction d’un bug de la commande `view` du shell de web scraping qui apparaissait selon l’encodage du site.
- Correction d’un bug de conversion du contenu qui affectait le mode `mcp` et les commandes `extract`.

### Nouveaux contributeurs {#v0.3.5-new-contributors}
- @AbdullahY36 a fait sa première contribution dans #87

## [v0.3.4](https://github.com/D4Vinci/Scrapling/releases/tag/v0.3.4) - 2025-09-16 {#v0.3.4}

**Une version nécessaire qui corrige plusieurs problèmes**

### 🚀 Nouveautés {#v0.3.4-new-stuff}
- Ajout de toutes les classes de session des fetchers au shell interactif pour les utiliser immédiatement, sans importation.

### 🐛 Corrections de bugs {#v0.3.4-bug-fixes}
- Ajout d’une solution de contournement pour un bug de l’API Playwright sur Windows lors de la récupération du contenu pendant la résolution de défis Cloudflare.
- Correction d’un problème d’encodage de la commande `view` dans le shell interactif
- Correction d’un bug de l’argument `max_pages` dans `AsyncStealthySession` qui faisait planter le code.
- Correction d’un problème apparu avec les dernières mises à jour : les propriétés `html_content` et `prettify` de `Selector` renvoyaient des octets selon l’encodage. Elles renvoient de nouveau des chaînes de caractères.

## [v0.3.3](https://github.com/D4Vinci/Scrapling/releases/tag/v0.3.3) - 2025-09-15 {#v0.3.3}

- Suppression de la logique qui fermait l’onglet par défaut du navigateur dans les fetchers de navigateur, car elle provoquait un plantage. Le problème ne se produisait pas sur Mac et n’a pu être reproduit que sur Windows et Linux

## [v0.3.2](https://github.com/D4Vinci/Scrapling/releases/tag/v0.3.2) - 2025-09-15 {#v0.3.2}

Notes de la version v0.3.2

### 🚀 Nouveautés {#v0.3.2-new-stuff}

- **Dépendances facultatives des fetchers** : Tous les fetchers font désormais partie de groupes de dépendances facultatifs, ce qui réduit la taille du paquet de base. Le module de base `scrapling` ne contient plus que le parser. Pour utiliser les fetchers ou les options de ligne de commande, exécutez `pip install "scrapling[fetchers]"`. Consultez les instructions d’installation détaillées [ici](index.md#installation)
- **Configuration par page dans les sessions** : Les classes de session des fetchers de navigateur permettent désormais de configurer chaque page séparément. Tous les paramètres de requête sont maintenant validés comme les paramètres de session. Plus de détails sur le site de documentation [ici](fetching/stealthy.md#full-list-of-arguments)
    <br>Exemple :

    ```python
    with StealthySession(headless=True, solve_cloudflare=True) as session:
        page = session.fetch('https://nopecha.com/demo/cloudflare', google_search=False)
    ```

- **Amélioration des fetchers de navigateur**
    - Une nouvelle option permet de choisir s’il faut attendre la fin de l’exécution de JavaScript dans les pages. Elle est activée par défaut, comme auparavant

        ```python
        with DynamicSession(headless=True, disable_resources=False, network_idle=True) as session:
           page = session.fetch('https://quotes.toscrape.com/', load_dom=False)
        ```

    - Le mode furtif est désormais plus fiable dans `DynamicFetcher` et ses classes de session.
    - `DynamicFetcher` et `StealthyFetcher` utilisent moins de ressources en trouvant et en fermant automatiquement l’onglet par défaut ouvert par les contextes persistants de l’API Playwright
    - Correction d’un bug important dans la rotation des pages des fetchers de navigateur. Les anciennes pages sont désormais remplacées par des pages neuves, car les onglets réutilisés pouvaient garder des réglages de leurs utilisations précédentes
    - `StealthyFetcher` et ses classes de session sont désormais un peu plus rapides (5 %)

- **Amélioration de la propriété `.body`** : Elle renvoie désormais le contenu reçu tel quel, sans traitement. Cela permet de télécharger des fichiers et de gérer les requêtes qui ne renvoient pas du HTML. Voici un exemple de téléchargement d’image :

    ```python
    from scrapling.fetchers import Fetcher

    page = Fetcher.get('https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/poster.png')
    with open(file='poster.png', mode='wb') as f:
        f.write(page.body)
    ```

### 🐛 Corrections de bugs {#v0.3.2-bug-fixes}

- **Problèmes d’encodage résolus** : Correction de plusieurs problèmes d’encodage avec certains sites dans le parser, le mode mcp et les commandes extract (Résout aussi #80 et #81)
- **Analyse plus rapide** : Grâce à de nombreux changements dans différentes parties, la bibliothèque est désormais plus rapide, comme le montrent les tests de performances mis à jour

### 🔨 Autres changements {#v0.3.2-misc}

- **Tests de performances mis à jour** : Actualisation des mesures pour comparer les gains de vitesse actuels aux dernières versions de bibliothèques similaires
- **Réorganisation d’une grande partie du code et remplacement du code inutilisé par de meilleures implémentations** : Moins de code, plus clair et plus facile à maintenir
- **Ajout d’une vidéo YouTube** : Ajout de contenu vidéo à la documentation MCP.
- **Nouveau modèle d’issue** : Un modèle simple pour les utilisateurs qui ne peuvent pas utiliser les modèles actuels.
- **Optimisation du workflow de CI** : Le workflow de tests ignore désormais les exécutions où seuls la documentation ou d’autres fichiers sans code ont changé.
- **Dépendances mises à jour** : Mise à jour de plusieurs dépendances vers les dernières versions.
- **Améliorations du style de code** : Application de nouvelles règles ruff dans tous les fichiers.
- **Hooks de pre-commit** : Mise à jour de la configuration de pre-commit.

### 🎯 Changements incompatibles {#v0.3.2-breaking-changes}

- Suppression du paramètre `max_pages` de la version synchrone de `StealthySession` pour l’aligner sur `DynamicSession`, car il n’a pas d’utilité dans la version synchrone

## [v0.3.1](https://github.com/D4Vinci/Scrapling/releases/tag/v0.3.1) - 2025-09-02 {#v0.3.1}

1. Correction d’un problème d’installation de scrapling sans l’extra `shell` (#76 )
2. Ajout d’un argument à tous les fetchers de navigateur et à leurs classes de session pour passer un fichier JS à exécuter lors de la création de la page (#56) :

```python
from scrapling.fetchers import StealthyFetcher

StealthyFetcher.fetch('https://example.com', init_script="/absolute/path/to/js/script.js")
```

## [v0.3](https://github.com/D4Vinci/Scrapling/releases/tag/v0.3) - 2025-09-01 {#v0.3}

🎉 **Version majeure - Refonte complète de l’architecture**

Scrapling v0.3 est la plus grande mise à jour de l’histoire du projet. Elle comprend une réécriture complète de l’architecture, d’importants gains de performances et de nouvelles fonctions puissantes, dont l’intégration avec l’IA et un shell interactif de web scraping.

Cette version comporte plusieurs changements incompatibles. Lisez attentivement les notes de version.

### 🚀 Principales nouveautés {#v0.3-major-new-features}

#### Architecture basée sur les sessions {#v0.3-session-based-architecture}
- **Nouvelles classes de session** : Réécriture complète qui ajoute la prise en charge des sessions persistantes
    - `FetcherSession` - Requêtes HTTP avec conservation de l’état, pour le code synchrone comme asynchrone
    - `DynamicSession`/`AsyncDynamicSession` - Automatisation du navigateur, qui reste ouvert jusqu’à ce que vous ayez terminé
    - `StealthySession`/`AsyncStealthySession` - Navigation discrète, avec un navigateur qui reste ouvert jusqu’à ce que vous ayez terminé
- **Gestion asynchrone des onglets du navigateur** : Nouveau groupe d’onglets via l’argument `max_pages`, qui alterne entre les onglets pour effectuer des requêtes simultanées avec le navigateur
- **Sessions simultanées** : Exécutez plusieurs sessions isolées en même temps

Consultez la section `Fetching` du site pour plus de détails.

#### De nombreuses fonctions pour masquer l’automatisation et contourner les protections antibots {#v0.3-a-lot-of-new-stealth-anti-bot-capabilities}
- **🤖 Résolution des défis Cloudflare** : [Résolution automatique des défis Cloudflare Turnstile](fetching/stealthy.md#cloudflare-and-stealth-options) dans `StealthyFetcher` et ses classes de session
- **Imitation des empreintes du navigateur** : Imitez les empreintes TLS de vrais navigateurs, utilisez des en-têtes qui correspondent à leur version, profitez de HTTP/3 et plus encore avec la toute nouvelle classe [Fetcher](fetching/static.md)
- **Mode discret amélioré** : Le mode discret de `DynamicFetcher` et de ses classes de session est désormais plus robuste et fiable (également connu sous le nom `PlayWrightFetcher`)

#### Intégration avec l’IA et serveur MCP {#v0.3-ai-integration-mcp-server}
- **Serveur MCP intégré** : Serveur Model Context Protocol pour le web scraping assisté par IA
- **6 outils puissants** : `get`, `bulk_get`, `fetch`, `bulk_fetch`, `stealthy_fetch`, `bulk_stealthy_fetch`
- **Extraction intelligente du contenu** : Convertissez des pages ou éléments web en Markdown ou HTML, ou extrayez une version propre du texte
- **Prise en charge des sélecteurs CSS** : Utilisez le moteur de Scrapling pour cibler précisément des éléments avant de transmettre le contenu à l’IA
- **Contournement des protections antibots** : Gérez Cloudflare Turnstile et d’autres protections
- **Prise en charge des proxies** : Utilisez des proxies pour préserver l’anonymat et choisir la localisation géographique
- **Imitation des navigateurs** : Imitez de vrais navigateurs avec leurs empreintes TLS, des en-têtes réels qui correspondent à leur version et plus encore
- **Traitement en parallèle** : Extrayez les données de plusieurs URL simultanément pour gagner en efficacité
- [et plus encore...](ai/mcp-server.md)

#### Nouveau shell interactif de web scraping {#v0.3-new-interactive-web-scraping-shell}
- **Nouveau shell** : Shell IPython personnalisé avec de nombreux raccourcis intelligents intégrés, comme `get`, `post`, `put`, `delete`, `fetch` et `stealthy_fetch`
- **Gestion intelligente des pages** : Nouvelles commandes `page` et `pages` pour conserver automatiquement la page actuelle et l’historique de toutes les requêtes faites depuis le shell
- **Intégration avec Curl** : Utilisez les fonctions `uncurl` et `curl2fetcher` pour convertir les commandes curl des outils de développement du navigateur en requêtes `Fetcher`
- [et plus encore...](cli/interactive-shell.md)

#### Extraire des données depuis le terminal sans programmer {#v0.3-scrape-from-the-terminal-without-programming}
- **Nouvelles commandes d’extraction** : Extrayez des données depuis le terminal sans programmer
    - `scrapling extract get/post/put/delete` - Requêtes HTTP simples
    - `scrapling extract fetch` - Extraction de contenu dynamique
    - `scrapling extract stealthy-fetch` - Contournement des protections antibots
- **Télécharge des pages web** et enregistre leur contenu dans des fichiers.
- **Convertit le HTML en formats lisibles**, comme Markdown, le conserve en HTML ou extrait uniquement le texte de la page.
- **Accepte des sélecteurs CSS personnalisés** pour extraire des parties précises de la page.
- **Gère les requêtes HTTP et la récupération de pages avec un navigateur.**
- **De nombreuses options de personnalisation**, avec des en-têtes, cookies, proxies et autres réglages. Presque toutes les options disponibles dans le code sont aussi accessibles depuis le terminal.
- [et plus encore...](cli/extract-commands.md)

### 🔧 Améliorations techniques {#v0.3-technical-improvements}

#### Améliorations des performances {#v0.3-performance-enhancements}
- **Fetcher est désormais 4 fois plus rapide** - Oui, vous avez bien lu !
- **DynamicFetcher est désormais ~60 % plus rapide** - Une version bien plus rapide selon votre configuration (surtout le mode discret)
- **StealthyFetcher est désormais 20–30 % plus rapide** - Grâce à la nouvelle structure et à l’adoption de notre propre code à la place de l’interface Python de `Camoufox`
- **Gain de vitesse cumulé de 50 %+** sur les principales méthodes de sélection (`find_by_text`, `find_similar`, `find_by_regex`, `relocate`, etc.) 🚀
- **Gain de vitesse de ~10 % pour les méthodes qui récupèrent la première correspondance CSS/XPath** - `css_first` et `xpath_first` sont désormais plus rapides que `css` et `xpath`
- **La méthode `get_all_text()` est 40 % plus rapide** pour extraire du contenu
- **Gain de vitesse de 20 %** pour retrouver les éléments de façon adaptative
- **Optimisation des propriétés de navigation** - Des propriétés comme `next`, `previous`, `below_elements` et d’autres sont désormais nettement plus rapides
- **Nettoyage du texte 5 fois plus rapide**
- **Meilleure utilisation de la mémoire** grâce à des importations optimisées et à moins de traitements supplémentaires
- **⚡ Importations très rapides** : Démarrage plus rapide grâce à un chargement optimisé des modules
- **De meilleurs résultats aux tests de performances** : Tous ces gains rendent Scrapling bien plus rapide qu’avant face aux autres bibliothèques (1775 fois plus rapide que BeautifulSoup et 5,1 fois plus rapide qu’AutoScraper ; consultez les [tests de performances](benchmarks.md))

#### Architecture, qualité du code et améliorations d’utilisation {#v0.3-architecture-code-quality-and-quality-of-life}
- **Contexte persistant** : Tous les fetchers basés sur un navigateur utilisent désormais un contexte persistant par défaut. (Résout aussi #64)
- **Utilisation de msgspec pour valider très vite la configuration de tous les fetchers basés sur un navigateur** avant d’exécuter les requêtes, ce qui facilite la recherche d’erreurs.
- **Tous les cookies** renvoyés par les fetchers ont désormais le format accepté par le même fetcher. Vous pouvez donc récupérer des cookies et les transmettre à nouveau à tous les fetchers et à leurs classes de session.
- **Vérification et mise en forme du code plus rapides** après la migration vers `ruff`
- **Système de build moderne** : Migration de setup.py vers pyproject.toml 📦
- **Amélioration des actions et workflows GitHub** pour faciliter le développement et les tests
- **🎨 Meilleures annotations de types** : Couverture complète des types selon les normes modernes de Python pour améliorer la prise en charge par les IDE et la fiabilité
- **Code plus propre** : Suppression du code inutilisé et optimisation des fonctions principales 🧹
- **🚀 Compatibilité avec les versions précédentes** : Ajout de raccourcis pour préserver la compatibilité avec l’ancien code

### Changements incompatibles {#v0.3-breaking-changes}

#### Version minimale de Python {#v0.3-minimum-python-version}
- **Python 3.10+ requis** : Fin de la prise en charge de Python 3.9 et des versions précédentes

#### Noms des classes et des méthodes {#v0.3-class-and-method-naming}
Ces changements de noms visent à apporter plus de clarté et de cohérence, surtout pour les nouveaux utilisateurs.

- **`Adaptor` → `Selector`** : La classe principale d’analyse a été renommée (vous pouvez toujours l’importer sous le nom `Adaptor` pour préserver la compatibilité)
- **`Adaptors` → `Selectors`** : La classe de collection a été renommée (vous pouvez toujours l’importer sous le nom `Adaptors` pour préserver la compatibilité)
- **`auto_match` → `adaptive`** : Le paramètre a été renommé dans toutes les méthodes
- **`adaptor_arguments` → `selector_config`** : Le paramètre de configuration a été renommé
- **`automatch_domain` → `adaptive_domain`** : Le paramètre de domaine a été renommé
- **`additional_arguments` → `additional_args`** : Le nom du paramètre a été raccourci
- **⚠️ `text/body` → `content`** : Le paramètre du constructeur de Selector accepte désormais `str` et `bytes`
- **`PlayWrightFetcher` → `DynamicFetcher`** : La classe d’automatisation du navigateur a été renommée (vous pouvez toujours l’importer sous le nom `PlayWrightFetcher` pour préserver la compatibilité)
- **DynamicFetcher ne contient plus la logique ni les arguments de NSTBrowser**, car il n’y a plus de raison de les conserver.
- **L’argument headless de StealthyFetcher n’accepte plus 'virtual'** car nous utilisons désormais la bibliothèque Camoufox uniquement pour obtenir le chemin d’installation du navigateur et les autres options de lancement

### 🐛 Corrections de bugs {#v0.3-bug-fixes}

- Correction du comptage des enfants imbriqués dans les balises ignorées par `get_all_text` (#61)
- Correction du problème d’installation causé par les espaces dans le chemin de l’exécutable Python (#57)
- Résolution des problèmes de threads dans le stockage, avec gestion de la récursion lorsque la fonction adaptative est activée
- Correction des problèmes de priorité des arguments avec le modèle Sentinel dans `FetcherSession`
- Correction de la gestion des types de proxies dans `StealthyFetcher`
- Correction des conflits entre les arguments `referer` et `google_search`
- Correction des problèmes d’injection asynchrone des scripts du mode discret

## [v0.2.99](https://github.com/D4Vinci/Scrapling/releases/tag/v0.2.99) - 2025-04-08 {#v0.2.99}

**Cette mise à jour est importante pour profiter pleinement de Scrapling tel qu’il a été conçu.**

### Ce qui a changé {#v0.2.99-what-s-changed}
#### Nouveau site avec toute la documentation {#v0.2.99-new-full-documentation-website}
- Oui, enfin 😄 Découvrez-le [ici](index.md)
#### Importation unifiée des fetchers {#v0.2.99-unified-import-logic-for-fetchers}
- Vous pouvez désormais importer tous les fetchers avec `from scrapling.fetchers import Fetcher, AsyncFetcher, StealthyFetcher, PlayWrightFetcher`, puis les utiliser directement, comme dans `page = Fetcher.get(...)`, sans créer d’instance.<br/> Cela remplace l’ancienne importation `from scrapling.defaults import Fetcher, AsyncFetcher, StealthyFetcher, PlayWrightFetcher`.
#### Changement incompatible : automatch est désormais désactivé par défaut {#v0.2.99-breaking-change-automatch-is-now-turned-off-by-default}
- Une nouvelle logique permet d’activer automatch depuis les fetchers ou les autres options d’analyse. Consultez la [documentation](fetching/choosing.md#parser-configuration-in-all-fetchers) pour plus de détails.
>  Les anciennes importations et l’ancienne logique restent utilisables, avec un avertissement, pour préserver la compatibilité.
#### Nouvelles options pour les fetchers {#v0.2.99-new-options-added-to-fetchers}
- `StealthyFetcher` et `PlayWrightFetcher` ont désormais un nouvel argument appelé `wait` pour récupérer des pages. Il fait attendre le fetcher pendant une durée définie en millisecondes avant de fermer la page et de vous renvoyer la réponse.
- Les méthodes de `StealthyFetcher` nommées `fetch` et `async_fetch` acceptent désormais l’argument `additional_arguments` pour transmettre des réglages supplémentaires à Camoufox. Ils ont priorité sur les réglages de Scrapling (#54 )
#### Corrections de bugs {#v0.2.99-bugs-squashed}
- Correction d’un bug de détection des redirections dans `async_fetch` des classes `StealthyFetcher` et `PlayWrightFetcher`.

**_Merci pour votre soutien et vos dons !_**

## [v0.2.98](https://github.com/D4Vinci/Scrapling/releases/tag/v0.2.98) - 2025-03-17 {#v0.2.98}

**Cette mise à jour est importante pour profiter pleinement de Scrapling tel qu’il a été conçu**

### Ce qui a changé {#v0.2.98-what-s-changed}
#### Améliorations de la consommation de mémoire et de la vitesse {#v0.2.98-various-memory-usage-and-speed-optimizations}
- Les méthodes de sélection utilisent désormais ~40 % de la mémoire utilisée auparavant, avec un léger gain de vitesse.
- Le chargement à la demande s’applique à tous les sous-modules de la bibliothèque : seuls les modules utilisés sont chargés. Par exemple :
Avant la mise à jour, l’importation `from scrapling import Adaptor` utilisait `30-40mb` de RAM car elle chargeait aussi tous les fetchers et d’autres composants. Elle utilise désormais `~1.2mb`.
- La dernière mise à jour réduisait la consommation de la bibliothèque à ~32 % de la mémoire utilisée auparavant avec un grand groupe de requêtes. Nous avons encore ajusté le cache pour utiliser moins de mémoire.
- Léger gain de vitesse global du parser, de 2-5 %

**_Merci pour votre soutien et vos dons !_**

## [v0.2.97](https://github.com/D4Vinci/Scrapling/releases/tag/v0.2.97) - 2025-03-15 {#v0.2.97}

**Cette mise à jour est importante pour profiter pleinement de Scrapling tel qu’il a été conçu**

### Ce qui a changé {#v0.2.97-what-s-changed}
#### Moins de mémoire utilisée et un léger gain de vitesse pour tous les fetchers {#v0.2.97-lower-memory-usage-and-small-speed-increase-across-all-fetchers}
- Les nouvelles limites de taille du cache dans toute la bibliothèque réduisent nettement la consommation de mémoire lors de nombreuses requêtes ou opérations.
- Réorganisation de grandes parties des fetchers pour faciliter leur maintenance et augmenter légèrement leur vitesse.

#### Corrections de bugs {#v0.2.97-bugs-fixed}
- Correction d’un bug de `TextHandler` qui transformait une valeur non textuelle en chaîne vide lorsque cette classe était importée seule. Toute valeur transmise à `TextHandler` est désormais convertie en chaîne, puis en `TextHandler`. Cela s’applique à toutes les valeurs : après tout, `TextHandler`, comme son nom l’indique, est conçu uniquement pour le texte ! (#45 )
- Correction d’un bug qui faisait ignorer l’argument `retries` par la plupart des méthodes d’AsyncFetcher.

#### Autres changements {#v0.2.97-miscellaneous}
- Mise à jour des annotations de types de la plupart des arguments dans tous les fetchers pour les rendre plus claires et précises.

**_Merci pour votre soutien et vos dons !_**

## [v0.2.96](https://github.com/D4Vinci/Scrapling/releases/tag/v0.2.96) - 2025-03-05 {#v0.2.96}

**Cette mise à jour est importante pour profiter pleinement de Scrapling tel qu’il a été conçu**

### Ce qui a changé {#v0.2.96-what-s-changed}
1. Ajout de l’option `-f` à `scrapling install` pour forcer la réinstallation des dépendances du navigateur. Je vous recommande d’exécuter `scrapling install -f` maintenant pour profiter du grand gain de vitesse de `StealthyFetcher` avec la nouvelle version du navigateur Camoufox :)
2. Correction d’un bug de `TextHandler` qui renvoyait `TextHandlers` au lieu de `TextHandler` lors de l’extraction d’une portion du texte, et correction de l’annotation de type correspondante (#41 )
3. Correction d’un problème qui pouvait faire ouvrir un shell Python par `scrapling install` dans certains cas !

## [v0.2.95](https://github.com/D4Vinci/Scrapling/releases/tag/v0.2.95) - 2025-02-25 {#v0.2.95}

**Cette mise à jour est importante pour profiter pleinement de Scrapling tel qu’il a été conçu**

### Ce qui a changé {#v0.2.95-what-s-changed}
1. Correction d’un bug de `Fetcher` : les en-têtes générés avec l’argument `stealthy_headers` écrasaient certains en-têtes fournis par l’utilisateur, comme `Accept` (#39 )
2. Légère amélioration de la logique de génération des en-têtes, qui devrait apporter un petit gain de vitesse.

## [v0.2.94](https://github.com/D4Vinci/Scrapling/releases/tag/v0.2.94) - 2025-02-22 {#v0.2.94}

**Cette mise à jour est importante pour profiter pleinement de Scrapling tel qu’il a été conçu**

### Ce qui a changé {#v0.2.94-what-s-changed}
1. Ajout de la propriété `history` à tous les fetchers pour afficher les redirections (#32 )
2. Correction de la logique de l’argument `case_sensitive` dans toutes les méthodes `re`/`re_first`. Si vous l’utilisiez, les résultats de votre code peuvent changer (mais vous l’avez peut-être mérité en voyant que cela ne fonctionnait pas comme prévu sans ouvrir d’issue, haha)
3. Mise à jour des dépendances et réactivation de `coop` dans le moteur Camoufox (StealthyFetcher).

## [v0.2.93](https://github.com/D4Vinci/Scrapling/releases/tag/v0.2.93) - 2025-01-31 {#v0.2.93}

**Cette mise à jour est importante pour profiter pleinement de Scrapling tel qu’il a été conçu**

### Ce qui a changé {#v0.2.93-what-s-changed}
1. Le type de retour est désormais cohérent dans tout le moteur d’analyse. Vous recevrez toujours un de ces types : `Adaptor`, `Adaptors`, `TextHandler`, `TextHandlers`, `None`, ou une liste si les résultats sont mixtes, comme avec un sélecteur CSS combiné. Cela facilite la programmation avec moins de vérifications manuelles des types, rend la bibliothèque plus stable et permet de toujours enchaîner les méthodes.
2. Réorganisation de la majeure partie du moteur d’analyse, surtout de la classe `Adaptor`, pour le rendre plus propre et surtout plus rapide. Presque toutes les méthodes et propriétés, notamment celles de recherche, gagnent 5-40 % de vitesse. Certaines gagnent davantage, comme `find_by_regex`, avec ~60 % de gain ! La fonction automatch gagne environ ~5 %.
3. Correction de bugs dans la logique de `find_all`/`find` qui appliquait les filtres avec OR dans certains cas et avec AND dans d’autres. Tous les éléments renvoyés doivent désormais satisfaire tous les filtres transmis.
4. Toutes les méthodes liées aux expressions régulières renvoient désormais `TextHandler`/`TextHandlers` pour faciliter l’enchaînement des méthodes.
5. **Ajout d’une nouvelle** propriété `below_elements`, qui renvoie un objet `Adaptors` contenant tous les éléments sous l’élément actuel dans l’arbre DOM.
6. Toutes les méthodes et propriétés qui renvoyaient du code HTML sous forme de chaîne le renvoient désormais comme `TextHandler`, pour faciliter l’utilisation des expressions régulières et d’autres opérations...
7. StealthyFetcher est désormais un peu plus rapide et discret. Vous pouvez aussi cliquer sur les CAPTCHA dans des iframes, comme **Cloudflare Turnstile**.
8. L’autocomplétion et les annotations de types sont nettement améliorées dans près de la moitié de la bibliothèque, surtout dans `Adaptor`, `TextHandler` et `TextHandlers`.
9. Extraire une portion de `TextHandler`, accéder à un caractère par son indice ou utiliser la méthode `split` renvoie désormais un autre `TextHandler` au lieu d’une chaîne Python standard. Presque toutes les opérations et méthodes standard de chaînes renvoient un autre `Texthandler` pour toujours permettre l’enchaînement des méthodes et fonctions.
10. Correction de petits bugs et de fautes de frappe. Par exemple, async_put de Fetcher envoyait une requête post au lieu d’une requête put 😶‍🌫️
11. Petite amélioration du README en attendant que je termine le site de documentation.

Cela devait être une petite mise à jour avant la version 0.3, mais j’ai décidé de l’améliorer davantage.

## [v0.2.92](https://github.com/D4Vinci/Scrapling/releases/tag/v0.2.92) - 2024-12-26 {#v0.2.92}

### Ce qui a changé {#v0.2.92-what-s-changed}
- Les réponses des fetchers basés sur un navigateur utilisent désormais des sources de données plus fiables lorsque la page chargée contient beaucoup d’iframes.
- **Installer `Scrapling` est encore plus simple : installez-le avec pip, exécutez `scrapling install` dans le terminal, et c’est prêt !**
- Correction d’une annotation de type imprécise dans le parser.

## [v0.2.91](https://github.com/D4Vinci/Scrapling/releases/tag/v0.2.91) - 2024-12-19 {#v0.2.91}

### Ce qui a changé {#v0.2.91-what-s-changed}
- Correction d’un bug qui faisait apparaître le message de journal de récupération de page uniquement lors de la première requête.
- Par défaut, l’API de Playwright renvoie la première réponse qui satisfait l’état de chargement transmis à la méthode `goto` : `["load", "domcontentloaded", "networkidle"]`. Si un site affiche une page d’attente, comme celle de Cloudflare, qui redirige ensuite vers le vrai site, Playwright renvoie le premier code de statut, par exemple 403. Cette mise à jour résout ce problème dans `PlaywrightFetcher` et `StealthyFetcher`, qui utilisent tous deux l’API de Playwright. Le résultat ne dépend plus de ce comportement par défaut.
- Ajout de la prise en charge des proxies SOCKS dans la classe `Fetcher`.
- Correction de l’annotation de type de l’argument `wait_selector_state` pour que l’autocomplétion affiche les valeurs correctes à utiliser.

## [v0.2.9](https://github.com/D4Vinci/Scrapling/releases/tag/v0.2.9) - 2024-12-16 {#v0.2.9}

### Ce qui a changé {#v0.2.9-what-s-changed}
##### Nouvelles fonctionnalités {#v0.2.9-new-features}
1. Voici le support asynchrone **tant attendu** dans Scrapling ! Vous disposez désormais de `AsyncFetcher`, la version asynchrone de `Fetcher`, et `StealthyFetcher` comme `PlayWrightFetcher` proposent une nouvelle méthode `async_fetch` avec les mêmes options.

```python
>> from scrapling import StealthyFetcher
>> page = await StealthyFetcher().async_fetch('https://www.browserscan.net/bot-detection')  # the async version of fetch
>> page.status == 200
True
```

2. La classe `StealthyFetcher` possède désormais l’argument `geoip` dans ses méthodes de récupération. Lorsqu’il est activé, elle utilise automatiquement la longitude, la latitude, le fuseau horaire, le pays et les paramètres régionaux de l’IP, puis modifie l’adresse IP exposée par WebRTC. Elle détermine et simule aussi la langue du navigateur selon la répartition des locuteurs dans la région ciblée.
3. Ajout de l’argument `retries` aux classes `Fetcher`/`AsyncFetcher` pour définir le nombre de nouvelles tentatives de chaque requête effectuée par `httpx`.
4. Ajout de la méthode `url_join` à `Adaptor` et aux fetchers. Elle combine une URL relative avec l’URL actuelle pour créer une URL absolue complète !
5. Ajout de la méthode `keep_cdata` à `Adaptor` et aux fetchers pour empêcher le parser de supprimer cdata lorsque vous souhaitez le conserver.
6. Dans `Adaptor`/`Response`, la méthode `body` renvoie désormais la réponse HTML brute quand c’est possible, sans traitement dans la bibliothèque.
7. Ajout de la journalisation à la classe `Response`. Quand vous utilisez les fetchers, vous recevez désormais un journal avec des informations sur la réponse.
Exemple :

   ```python
   >> from scrapling.defaults import Fetcher
   >> Fetcher.get('https://books.toscrape.com/index.html')
   [2024-12-16 13:33:36] INFO: Fetched (200) <GET https://books.toscrape.com/index.html> (referer: https://www.google.com/search?q=toscrape)
   >>
   ```

8. Utiliser des méthodes standard de chaînes sur un `TextHandler`, comme `.replace()`, renvoie désormais un autre `TextHandler`. Elles renvoyaient auparavant une chaîne standard.
9. Gains de vitesse importants dans toute la bibliothèque et amélioration de la discrétion des classes de fetchers en général.
10. Ajout de fonctions de compatibilité comme `extract_first`\`extract`, qui renvoient le même résultat que l’objet d’origine. Elles servent uniquement à faciliter la copie de code de Scrapy/Parsel vers Scrapling si nécessaire, car ces fonctions y sont utilisées !
11. Les requêtes par lots sont désormais beaucoup plus rapides grâce à la réorganisation d’une grande partie du code et à l’utilisation du cache aux bons endroits.

##### Changements incompatibles {#v0.2.9-breaking-changes}
- Fin de la prise en charge de Python 3.8. (Surtout parce que Playwright ne le prend plus en charge, mais cette version posait déjà des problèmes)
- L’argument `debug` a été retiré de toute la bibliothèque. Pour activer le débogage, faites ceci après l’avoir importée :

   ```python
   >>> import logging
   >>> logging.getLogger("scrapling").setLevel(logging.DEBUG)
   ```

##### Corrections de bugs {#v0.2.9-bugs-squashed}
1. WebGL est désormais activé par défaut, car de nombreuses protections vérifient s’il est actif.
2. Correction de quelques erreurs et fautes de frappe dans la documentation et le README.

##### Améliorations d’utilisation {#v0.2.9-quality-of-life-changes}
1. Tous les journaux utilisent désormais le logger nommé `scrapling` pour simplifier leur contrôle. Nous utilisions auparavant le logger racine.
2. Réorganisation du dossier des tests pour le rendre plus clair et ajout de tests pour les nouvelles fonctions. Tous les tests ont été réécrits plus proprement, et de nouveaux tests augmentent la couverture.
3. Réorganisation d’une grande partie du code pour le rendre plus propre et plus facile à maintenir.

> Tous ces changements étaient prévus pour la version 0.3, mais j’ai décidé de les inclure ici car la prochaine version prendra encore du temps. La prochaine étape est de terminer le site de documentation détaillée, puis de travailler sur la version 0.3

## [v0.2.8](https://github.com/D4Vinci/Scrapling/releases/tag/v0.2.8) - 2024-11-30 {#v0.2.8}

### Ce qui a changé {#v0.2.8-what-s-changed}
- Petite mise à jour avec des améliorations d’utilisation nécessaires dans le code et la correction d’une faute de frappe dans le README principal (#20)

## [v0.2.7](https://github.com/D4Vinci/Scrapling/releases/tag/v0.2.7) - 2024-11-26 {#v0.2.7}

### Ce qui a changé {#v0.2.7-what-s-changed}
##### Nouvelles fonctionnalités {#v0.2.7-new-features}
- Si vous utilisez l’argument `wait_selector` avec les classes `StealthyFetcher` et `PlayWrightFetcher`, Scrapling attend de nouveau le chargement et l’exécution complets du JS, comme d’habitude. Si vous utilisez `network_idle`, il attend aussi de nouveau cet état après tout cela. Bien sûr, si tous les états sont déjà satisfaits, il n’attend pas.
- Vous pouvez désormais activer ou désactiver les publicités dans `StealthyFetcher` avec l’argument `disable_ads`. Le blocage est activé par défaut et installe l’extension `ublock origin`.
- Vous pouvez désormais définir les paramètres régionaux de `PlayWrightFetcher` avec l’argument `locale`. La valeur par défaut reste `en-US`.
- Les requêtes simples effectuées par `Fetcher` acceptent désormais des proxies au format `http://username:password@localhost:8030`.
- Légère amélioration du mode discret de `PlayWrightFetcher`.

##### Corrections de bugs et améliorations {#v0.2.7-bugs-squashed-improvements}
1. L’activation des proxies dans la classe `PlayWrightFetcher` ne dépend plus de l’activation ou non du mode `stealth` (merci à [@AbdullahY36](https://github.com/AbdullahY36) pour le signalement)
2. `ResponseEncoding` vérifie désormais si l’encodage indiqué dans la réponse peut être utilisé avec la page. Si cet encodage provoque une erreur, Scrapling utilise `utf-8` par défaut

## [v0.2.6](https://github.com/D4Vinci/Scrapling/releases/tag/v0.2.6) - 2024-11-24 {#v0.2.6}

### Ce qui a changé {#v0.2.6-what-s-changed}
##### Nouvelles fonctionnalités {#v0.2.6-new-features}
- `PlayWrightFetcher` peut désormais utiliser directement le vrai navigateur en passant `real_chrome` à la fonction `PlayWrightFetcher.fetch`, à condition que Chrome soit installé. Scrapling ouvre une instance de votre navigateur Chrome, et vous pouvez utiliser la plupart des options comme d’habitude. (Auparavant, seul l’argument `cdp_url` permettait de le faire)
- Mise à jour de la version indiquée dans les en-têtes générés pour les vrais navigateurs.

##### Corrections de bugs {#v0.2.6-bugs-squashed}
1. Le format des en-têtes de navigateur générés par `BrowserForge` était dépassé, ce qui permettait à certaines protections de détecter Scrapling. `BrowserForge` sert désormais uniquement à générer un useragent réel.
2. L’argument `hide_canvas` est désormais désactivé par défaut car ReCaptcha de Google le détecte.

## [v0.2.5](https://github.com/D4Vinci/Scrapling/releases/tag/v0.2.5) - 2024-11-23 {#v0.2.5}

### Ce qui a changé {#v0.2.5-what-s-changed}

##### Corrections de bugs {#v0.2.5-bugs-squashed}
- Gestion d’une erreur de l’argument 'wait_selector' lorsqu’il correspond à plus de 1 élément. Cela concerne les classes `StealthyFetcher` et `PlayWrightFetcher`.
- Correction du type d’encodage lorsque la valeur de l’en-tête `content_type` contient des paramètres comme `charset` (merci à @andyfcx pour [#12](https://github.com/D4Vinci/Scrapling/issues/12) )

##### Améliorations d’utilisation {#v0.2.5-quality-of-life}
- Ajout de tests pour couvrir de nouvelles parties du code et exécution des tests dans des threads.
- Mise à jour des docstrings pour qu’ils s’affichent correctement dans apidoc de Sphinx et les outils similaires.

##### Nouveaux contributeurs {#v0.2.5-new-contributors}
- @andyfcx a fait sa première contribution dans [#13 ](https://github.com/D4Vinci/Scrapling/pull/13)

## [v0.2.4](https://github.com/D4Vinci/Scrapling/releases/tag/v0.2.4) - 2024-11-20 {#v0.2.4}

### Ce qui a changé {#v0.2.4-what-s-changed}

##### Corrections de bugs {#v0.2.4-bugs-squashed}
- Correction d’un bug lors de la récupération des octets de la réponse après l’utilisation de `network_idle` dans les classes `StealthyFetcher` et `PlayWrightFetcher`. <br/> Cela provoquait le message d’erreur suivant :

    ```
    Response.body: Protocol error (Network.getResponseBody): No resource with given identifier found
    ```

- L’API de PlayWright renvoie parfois des réponses avec un texte de statut vide. `Scrapling` le détermine désormais lui-même dans ce cas. Cela concerne les classes `StealthyFetcher` et `PlayWrightFetcher`.

## [v0.2.3](https://github.com/D4Vinci/Scrapling/releases/tag/v0.2.3) - 2024-11-19 {#v0.2.3}

### Ce qui a changé {#v0.2.3-what-s-changed}

##### Corrections de bugs {#v0.2.3-bugs-squashed}
- Correction d’un bug d’installation avec pip qui empêchait complètement le mode discret de PlayWright Fetcher de fonctionner.

## [v0.2.2](https://github.com/D4Vinci/Scrapling/releases/tag/v0.2.2) - 2024-11-16 {#v0.2.2}

### Ce qui a changé {#v0.2.2-what-s-changed}
##### Nouvelles fonctionnalités {#v0.2.2-new-features}
- Si vous ne souhaitez pas transmettre d’arguments à l’objet `Adaptor` créé et préférez les valeurs par défaut, vous pouvez utiliser cette importation pour simplifier le code

    ```python
    >> from scrapling.default import Fetcher, StealthyFetcher, PlayWrightFetcher
    >> page = Fetcher.get('https://example.com', stealthy_headers=True)
    ```

    Sinon

    ```python
    >> from scrapling import Fetcher, StealthyFetcher, PlayWrightFetcher
    >> page = Fetcher(auto_match=False).get('https://example.com', stealthy_headers=True)
    ```

##### Corrections de bugs {#v0.2.2-bugs-squashed}
1. Correction d’un bug de l’objet `Response`, apparu avec le correctif v0.2.1 d’hier, dans certains cas de sélection ou d’analyse imbriquées.

## [v0.2.1](https://github.com/D4Vinci/Scrapling/releases/tag/v0.2.1) - 2024-11-15 {#v0.2.1}

### Ce qui a changé {#v0.2.1-what-s-changed}
##### Nouvelles fonctionnalités {#v0.2.1-new-features}
1. L’objet `Response` renvoyé par tous les fetchers est désormais identique à l’objet `Adaptor`, avec les attributs supplémentaires suivants : `status`, `reason`, `cookies`, `headers` et `request_headers`. Les attributs `cookies`, `headers` et `request_headers` sont toujours de type `dictionary`. <br/>Votre code peut donc devenir :

    ```python
    >> from scrapling import Fetcher
    >> page = Fetcher().get('https://example.com', stealthy_headers=True)
    >> print(page.status)
    200
    >> products = page.css('.product')
    ```

    Au lieu du code précédent

    ```python
    >> from scrapling import Fetcher
    >> fetcher = Fetcher().get('https://example.com', stealthy_headers=True)
    >> print(fetcher.status)
    200
    >> page = fetcher.adaptor
    >> products = page.css('.product')
    ```

    J’ai conservé la propriété `.adaptor` pour préserver la compatibilité avec les versions précédentes.

2. Les classes `StealthyFetcher` et `PlayWrightFetcher` acceptent désormais un argument `proxy` dans la méthode de récupération, sous forme de chaîne ou de dictionnaire.
3. La classe `StealthyFetcher` possède désormais l’argument `os_randomize` dans la méthode `fetch`. S’il est activé, Scrapling choisit au hasard les empreintes du système d’exploitation. Par défaut, les empreintes correspondent au système d’exploitation actuel.

##### Corrections de bugs {#v0.2.1-bugs-squashed}
1. Correction d’un bug lors de la transmission d’en-têtes à la classe `Fetcher`.
2. Correction d’un bug lors de l’analyse de réponses JSON transmises par les classes de fetchers.

##### Améliorations d’utilisation {#v0.2.1-quality-of-life-changes}
1. Les fonctions de texte essayaient de supprimer les commentaires HTML avant de renvoyer le texte, mais cela causait des erreurs dans certains cas et compliquait inutilement le code. Elles reviennent désormais au comportement par défaut de lxml : **vous remarquerez un léger gain de vitesse dans toutes les opérations qui dépendent du texte des éléments, comme les sélecteurs**. Si vous souhaitez que Scrapling retire les commentaires HTML avant de renvoyer le texte pour éviter l’étrange découpage du texte dans lxml/parsel/scrapy, laissez l’argument `keep_comments` à True, sa valeur par défaut.

## [v0.2](https://github.com/D4Vinci/Scrapling/releases/tag/v0.2) - 2024-11-11 {#v0.2}

### Ce qui a changé {#v0.2-what-s-changed}
##### Nouvelles fonctionnalités {#v0.2-new-features}
1. Voici la fonction `Fetchers`, avec 3 nouveaux types principaux pour que Scrapling récupère des pages à votre place avec BEAUCOUP d’options !
    - La classe `Fetcher`, pour les requêtes HTTP simples
    - La classe `StealthyFetcher`, un fetcher entièrement discret qui utilise une [version modifiée de Firefox pour masquer l’automatisation](https://github.com/daijro/camoufox).
    - La classe `PlayWrightFetcher`, pour effectuer des requêtes avec un navigateur via PlayWright sans modification, PlayWright avec un mode discret créé par moi, de vrais navigateurs via CDP, et [NSTBrowser](https://app.nstbrowser.io/r/1vO5e5) avec son [docker browserless](https://hub.docker.com/r/nstbrowser/browserless) !
2. Ajout des toutes nouvelles méthodes `find_all`/`find` pour trouver facilement des éléments sur la page avec un peu de magie noire !
3. Ajout des méthodes `filter` et `search` à la classe `Adaptors` pour faciliter les opérations par lots sur des groupes d’objets `Adaptor`.
4. Ajout des méthodes `css_first` et `xpath_first` pour simplifier l’utilisation.
5. Ajout de la nouvelle classe `TextHandlers`, utilisée pour les opérations par lots sur des objets `TextHandler`, comme la classe `Adaptors`.
6. Ajout des méthodes `generate_full_css_selector` et `generate_full_xpath_selector`.

##### Corrections de bugs {#v0.2-bugs-squashed}
1. Dans la classe `Adaptors`, `re_first` renvoie désormais la première correspondance trouvée parmi tous les objets `Adaptor` qu’elle contient, au lieu de renvoyer par erreur les résultats de `re_first` de tous les objets `Adaptor`.
2. Si vous sélectionnez le contenu textuel d’éléments (comme avec la fonction CSS `::text`) via une méthode comme `.css` ou `.xpath`, l’objet `Adaptor` renvoie désormais la classe `TextHandlers` au lieu d’une liste de chaînes. Vous pouvez donc utiliser `page.css('something::text').re_first(r'regex_pattern').json()` au lieu de `page.css('something::text')[0].re_first(r'regex_pattern').json()`
3. Les arguments re/re_first de `Adaptor`/`Adaptors` sont désormais cohérents avec ceux de `TextHandler`. Vous disposez donc des arguments `clean_match` et `case_sensitive`.
4. L’argument `auto_match` est activé par défaut lors de la création de `Adaptor`, mais vous devez toujours l’activer lors de la sélection des éléments si vous souhaitez l’utiliser. (Ce n’est pas un bug, mais un choix de conception)
5. Correction de nombreuses annotations de types pour améliorer l’autocomplétion quand vous programmez avec Scrapling.

##### Améliorations d’utilisation {#v0.2-quality-of-life-changes}
1. Les méthodes `css_selector` et `xpath_selector` ont été renommées `generate_css_selector` et `generate_xpath_selector` pour plus de clarté et pour ne pas perturber l’autocomplétion pendant la programmation.
2. Réorganisation de la majeure partie de l’ancien code dans un sous-paquet `core`, avec d’autres choix de conception pour faciliter la maintenance future.
3. Réorganisation du dossier des tests et ajout de tests pour les nouvelles fonctions. Les environnements tox sont désormais conservés en cache sur GitHub pour accélérer les tests automatiques à chaque commit.

## [v0.1.2](https://github.com/D4Vinci/Scrapling/releases/tag/v0.1.2) - 2024-10-16 {#v0.1.2}

**Historique des changements** :

- Correction d’un bug qui empêchait l’argument `keep_comments` de fonctionner comme prévu.
- Ajustement de la fonction de texte pour supprimer automatiquement les commentaires HTML des éléments avant d’en extraire le texte et éviter le comportement différent de Lxml. Par exemple :

    ```python
    >>> page = Adaptor('<span>CONDITION: <!-- -->Excellent</span>', keep_comments=True)
    >>> page.css('span::text')
    ['CONDITION: ', 'Excellent']
    ```

    Ce résultat était dû au comportement par défaut de Lxml, mais la fonction renvoie désormais le texte complet 'CONDITION: Excellent'
    Ce comportement est aussi connu dans parsel\scrapy, j’ai donc voulu le traiter ici.

- Correction d’un bug qui empêchait de supprimer le fichier de base de données SQLite créé par la bibliothèque lors de l’exécution de `pip uninstall scrapling` ou d’une commande similaire.

## [v0.1.1](https://github.com/D4Vinci/Scrapling/releases/tag/v0.1.1) - 2024-10-14 {#v0.1.1}

Petites corrections

## [v0.1](https://github.com/D4Vinci/Scrapling/releases/tag/v0.1) - 2024-10-13 {#v0.1}

**Historique complet des changements** : <https://github.com/D4Vinci/Scrapling/commits/v0.1>
