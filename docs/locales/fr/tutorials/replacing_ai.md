---
title: "Une solution gratuite pour extraire des données web de façon fiable sans IA"
description: "Scrapling gère les pages qui changent, les sélecteurs instables, les protections antibot et la pagination sans appeler un LLM pour chaque page."
---

# Scrapling : une solution gratuite pour extraire des données web de façon fiable sans IA {#scrapling-a-free-alternative-to-ai-for-robust-web-scraping}

L’extraction de données web sert depuis longtemps à collecter des informations, indexer du contenu et préparer des jeux de données, entre autres usages. Mais les utilisateurs expérimentés rencontrent souvent des problèmes qui compliquent le travail. Récemment, l’intérêt pour l’extraction avec l’IA a augmenté, car elle peut résoudre une partie de ces difficultés.

Dans cet article, nous verrons ces problèmes courants, pourquoi les entreprises se tournent vers l’IA, les limites de cette approche et comment Scrapling peut vous aider sans le coût de l’IA.

## Problèmes courants et objectifs difficiles {#common-issues-and-challenging-goals}

Si vous extrayez des données web depuis un certain temps, vous avez sans doute déjà rencontré ces problèmes :

1. **Des structures de sites qui changent souvent** : Les sites modifient leur DOM et les sélecteurs XPath/CSS fixes ne fonctionnent plus.
2. **Des sélecteurs instables** : Les noms de classes et les identifiants changent ou sont générés au hasard. Cela casse les scrapers ou rend l’extraction difficile.
3. **Des protections antibot de plus en plus complexes** : Les CAPTCHA, l’empreinte du navigateur et l’analyse du comportement compliquent l’extraction classique.

Et ce ne sont pas les seuls. Tout cela arrive même avec des sites connus pour lesquels vous pouvez écrire du code précis.

Si vous voulez aller plus loin et extraire des données sur de nombreux sites différents, ce qu’on appelle parfois Broad Scraping ou Generic Web Scraping, ces difficultés augmentent et d’autres apparaissent :

1. **Une grande diversité de sites** : Un scraper générique doit gérer de nombreuses structures HTML, façons d’utiliser CSS, frameworks JavaScript et technologies côté serveur.
2. **Trouver les données utiles** : Comment le scraper sait-il quelles données comptent sur une page qu’il n’a jamais vue ?
3. **Différentes formes de pagination** : Le défilement infini, les pages numérotées et les boutons pour charger plus de contenu demandent des approches différentes.

Et la liste continue. Comment résoudre tout cela à la main ? Je parle ici de sites différents qui ne partagent pas les mêmes technologies.

## L’IA aide, mais coûte cher {#ai-to-the-rescue-but-at-a-high-cost}

L’IA peut résoudre beaucoup de ces problèmes parce qu’elle comprend le code de la page, trouve les champs souhaités ou crée des sélecteurs pour eux. Bien sûr, cela suppose que vous avez déjà géré les protections antibot avec d’autres outils :)

J’aime cette approche. Je trouve l’IA fascinante, surtout l’IA générative. Vous passerez probablement beaucoup de temps à régler les instructions données au modèle. Si cela ne vous gêne pas, vous arriverez vite au vrai problème de l’IA dans ce contexte.

Beaucoup de pages contiennent énormément de contenu, qu’il faut transmettre d’une façon ou d’une autre au modèle. Cela consomme des tokens très vite et les coûts peuvent grimper rapidement.

À moins que le budget ne compte pas pour vous, vous chercherez des solutions moins chères. C’est là que Scrapling intervient :smile:

## Scrapling vous aide {#scrapling-got-you-covered}

Scrapling peut gérer presque tous les problèmes que vous rencontrerez en extrayant des données web. Les prochaines mises à jour prendront en charge les autres.

### Résoudre T1 : des structures de sites qui changent souvent {#solving-issue-t1-rapidly-changing-website-structures}

C’est pour cela que la fonction [adaptive](../parsing/adaptive.md) existe. Vous saviez que j’allais en parler, et nous y voilà :)

Avec `adaptive` activé, vous pouvez enregistrer les propriétés qui distinguent un élément pour le retrouver plus tard, même si la structure du site change. Le plus difficile est que n’importe quelle partie de l’élément peut changer. Il n’y a donc pas toujours de propriété fixe sur laquelle s’appuyer.

La fonction enregistre tout ce qui distingue l’élément. Lorsque la structure du site change, elle renvoie l’élément dont le score de ressemblance avec l’ancien est le plus élevé.

J’ai déjà expliqué cela en détail, avec plusieurs exemples. Vous pouvez les lire [ici](../parsing/adaptive.md#how-the-adaptive-scraping-feature-works).

### Résoudre T2 : des sélecteurs instables {#solving-issue-t2-unstable-selectors}

Si vous extrayez des données depuis longtemps, cela vous est sans doute arrivé : un site en HTML sans identifiants ni classes, des noms de classes aléatoires ou une structure qui n’offre rien de stable pour sélectionner les éléments.

Dans ces cas, les sélecteurs CSS/XPath classiques ne sont pas toujours le meilleur choix. Scrapling propose donc trois autres façons de sélectionner les éléments :

1. [Sélectionner par le contenu](../parsing/selection.md#text-content-selection) : Cherchez du texte avec `find_by_text`, ou utilisez une expression régulière qui correspond au texte avec `find_by_regex`.
2. [Sélectionner des éléments qui ressemblent à un autre](../parsing/selection.md#finding-similar-elements) : Trouvez un élément et nous cherchons les autres.
3. [Sélectionner avec des filtres](../parsing/selection.md#filters-based-searching) : Indiquez les conditions que l’élément doit remplir et nous le trouvons.

Ouvrez les liens pour voir comment Scrapling résout chaque cas.

### Résoudre T3 : des protections antibot de plus en plus complexes {#solving-issue-t3-increasingly-complex-anti-bot-measures}

Les proxies et les actions qui imitent une personne ne suffisent pas toujours sur les sites protégés. [StealthyFetcher](../fetching/stealthy.md) combine l’automatisation du navigateur, des modifications de son empreinte et des options pour gérer les protections antibot. Activez `solve_cloudflare=True` pour les défis Turnstile et Interstitial de Cloudflare.

### Résoudre B1 et B2 : diversité des sites et recherche des données utiles {#solving-issues-b1-b2-extreme-website-diversity-identifying-relevant-data}

Ce problème est difficile, mais la souplesse de Scrapling permet de l’aborder.

J’ai parlé avec une personne qui utilise l’IA pour extraire des prix sur différents sites. Seuls les prix et les titres l’intéressent, alors elle demande à l’IA de trouver les prix.

Je lui ai dit que l’IA n’était pas nécessaire ici et donné cet exemple :
```python
price_element = page.find_by_regex(r'£[\d\.,]+', first_match=True)  # Get the first element that contains a text that matches price regex eg. £10.50
# If you want the container/element that contains the price element
price_element_container = price_element.parent or price_element.find_ancestor(lambda ancestor: ancestor.has_class('product'))  # or other methods...
target_element_selector = price_element_container.generate_css_selector or price_element_container.generate_full_css_selector # or xpath
```
Elle m’a alors demandé comment gérer un cas comme celui-ci :
```html
<span class='currency'> $ </span> <span class='a-price'> 45,000 </span>
```
J’ai donc adapté le code :
```python
price_element_container = page.find_by_regex(r'[\d,]+', first_match=True).parent # Adjusted the regex for this example
full_price_data = price_element_container.get_all_text(separator="", strip=True)  # Returns '$45,000' in this case
```
Cela suffisait pour son besoin. Vous pouvez essayer la première expression régulière et, si elle ne trouve rien, passer à la suivante. Commencez par les motifs les plus fréquents, puis couvrez les autres.
Cela peut être un peu fastidieux, mais coûte bien moins cher que l’IA.

Voilà ce que montre cet exemple : tous les problèmes ne demandent pas une IA. Parfois, chercher une autre solution peut vous faire économiser beaucoup d’argent.

### Résoudre B3 : différentes formes de pagination {#solving-issue-b3-pagination-variations}

Scrapling n’a pas encore de méthode qui détecte automatiquement les liens de pagination. Ses spiders suivent ces liens avec `response.follow()`.

Vous pouvez toutefois couvrir beaucoup de sites en cherchant les motifs courants avec `page.find_by_text('Next')['href']` ou `page.find_by_text('load more')['href']`, ou avec des sélecteurs comme `'a[href*="?page="]'` ou `'a[href*="/page/"]'`. Vous voyez l’idée.

## Comparaison des coûts et économies {#cost-comparison-and-savings}

Voici une comparaison rapide :

| Aspect | Scrapling | Outils avec IA (par exemple Browse AI ou Oxylabs) |
|---|---|---|
| Coût | Gratuit, sans frais par utilisation de la bibliothèque | Offres payantes, avec un prix qui dépend du fournisseur et de l’usage |
| Configuration | Demande quelques connaissances techniques et une configuration manuelle | Souvent sans code, donc plus simple sans connaissances techniques |
| Modes d’utilisation | Code, terminal ou serveur MCP | Souvent une interface graphique ou une API, selon l’offre de l’entreprise |
| Passage à grande échelle | Dépend de la mise en œuvre par l’utilisateur | Services gérés avec prise en charge de grands volumes |
| Adaptation aux changements | Élevée avec `adaptive` et les méthodes de sélection sans sélecteurs CSS/XPath | Élevée et automatique avec l’IA, mais chère si les changements sont fréquents |

Consultez les tarifs actuels de [Browse AI](https://www.browse.ai/pricing) et de la [Web Scraper API d’Oxylabs](https://oxylabs.io/products/scraper-api/web/pricing).

## Conclusion {#conclusion}

L’IA offre des fonctions puissantes, mais son coût peut être trop élevé pour beaucoup de tâches d’extraction web. Scrapling réunit des outils fiables, souples et économiques pour extraire des données sur des sites précis ou sur de nombreux sites différents. Il évite souvent de recourir à des solutions d’IA coûteuses. Avec `adaptive`, plusieurs méthodes de sélection et des fetchers avancés, vous pouvez créer des scrapers qui résistent mieux aux changements.

Explorez la documentation pour découvrir comment Scrapling peut simplifier vos prochains projets d’extraction de données web !
