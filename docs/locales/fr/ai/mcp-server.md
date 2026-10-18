---
title: "Serveur MCP de Scrapling : configuration et extraction de données"
description: "Connectez un client IA à Scrapling pour extraire des données par HTTP ou avec un navigateur. Utilisez les sessions, l’état de connexion sauvegardé, les actions, les filtres et l’historique des API."
---

# Guide du serveur MCP de Scrapling {#scrapling-mcp-server-guide}

<iframe width="560" height="315" src="https://www.youtube.com/embed/NHwWEiTOoPQ" title="Lecteur vidéo YouTube" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>

Le **serveur MCP de Scrapling** met les fonctions d’extraction de données web de Scrapling à la disposition de votre chatbot ou agent IA. Vous pouvez lui demander de visiter des sites, d’extraire des données et de contourner les protections antibot au cours d’une conversation dans Claude ou dans toute interface compatible avec MCP.

## Fonctions {#features}

Le serveur MCP de Scrapling fournit seize outils pour extraire des données web et interagir avec le navigateur. Les outils à usage unique récupèrent une URL, puis ferment leur navigateur ou client. Les outils de session gardent les cookies et les réglages entre les appels. L’IA peut ainsi poursuivre ses actions dans le même onglet et consulter l’historique réseau.

### Outils à usage unique {#one-shot-tools}

#### 🚀 Extraction de base par HTTP {#basic-http-scraping}

- **`make_request`** : Des requêtes HTTP rapides avec n’importe quelle méthode (GET, POST, PUT, DELETE) et imitation de l’empreinte du navigateur. Cet outil génère de vrais en-têtes de navigateur correspondant à la version TLS, prend en charge HTTP/3 et plus encore.

#### 🔒 Extraction avec le navigateur Stealthy {#stealth-browser-scraping}

- **`browser_fetch_once`** : Exécute JavaScript et extrait des données de pages dynamiques avec notre navigateur Stealthy. L’outil permet de modifier l’empreinte du navigateur, de contourner Turnstile et Interstitial de Cloudflare, et de contrôler le navigateur comme la requête.

### Outils de session {#session-tools}

#### 🔌 Gestion des sessions {#session-management}

- **`browser_open`** : Crée une session persistante de navigateur Stealthy qui reste ouverte entre les appels à `browser_fetch`. Il n’est donc pas nécessaire de lancer un navigateur à chaque fois. Elle garde la configuration du navigateur et renvoie seulement `session_id` et `session_type`. Utilisez `list_sessions` pour voir sa configuration effective dans `settings`, qui est vide pour les sessions CDP.
- **`open_request_session`** : Crée une session HTTP persistante sans navigateur, à utiliser avec `session_make_request`. Elle garde les cookies, les connexions et l’empreinte du navigateur (`impersonate`) entre les requêtes. Elle renvoie seulement `session_id` et `session_type`, avec le type `static`. Utilisez `list_sessions` pour voir sa configuration effective dans `settings`.
- **`close_session`** : Ferme une session persistante de navigateur ou de requêtes et libère ses ressources.
- **`list_sessions`** : Liste toutes les sessions actives avec leurs détails et leur `settings`.

#### État du navigateur {#browser-state}

- **`browser_save_state`** : Enregistre les cookies, le stockage local et IndexedDB dans un fichier JSON compatible avec Playwright. Vous pouvez ainsi réutiliser l’état de connexion après la fin de la session du navigateur. L’enregistrement remplace le fichier s’il existe déjà.
- **`browser_load_state`** : Restaure un fichier enregistré dans une session de navigateur ouverte, même avant le premier chargement de page. Le contenu remplace l’état stocké actuel sans fermer les onglets ni changer de page. Récupérez ou rechargez la page pour utiliser la connexion restaurée.

Les fichiers d’état se trouvent sur l’ordinateur qui exécute le serveur MCP. Ils ne contiennent pas `sessionStorage`, les onglets ouverts ni les réglages du navigateur.

#### 🎯 Récupérer des pages dans une session {#fetching-through-a-session}

- **`browser_fetch`** : Exécute JavaScript et extrait les données d’une URL dans une session ouverte de navigateur Stealthy. L’outil permet de modifier l’empreinte du navigateur et de contourner Turnstile et Interstitial de Cloudflare. Il peut aussi créer une vue structurée de la page avec les références, positions et tailles des éléments, pour aider l’IA à repérer les contrôles et à préparer les actions de la souris.
- **`session_make_request`** : Envoie des requêtes HTTP rapides avec n’importe quelle méthode (GET, POST, PUT, DELETE), imitation de l’empreinte du navigateur, en-têtes correspondants et prise en charge d’HTTP/3. Réutilise les cookies, les connexions et l’empreinte du navigateur dans une session ouverte avec `open_request_session`.

#### 📸 Captures d’écran {#screenshots}

- **`browser_screenshot`** : Capture la page actuelle ou un élément en PNG ou JPEG sans la recharger. Vous pouvez vérifier les champs remplis, les menus ouverts, les graphiques ou les cartes de résultats. Capturer un seul élément réduit le contenu inutile. L’outil accepte la zone visible, la page entière ou un élément, avec une qualité JPEG réglable. La capture est renvoyée sous forme de bloc d’image réel que le modèle peut voir directement.

#### Contenu de la page actuelle {#current-page-content}

- **`browser_extract`** : Lit la page actuelle ou un élément sous forme de vue structurée pour l’IA, de HTML, de Markdown ou de texte, sans rechargement. Extrayez les résultats après avoir rempli un formulaire ou chargé plus de contenu. Les vues incluent les rôles, noms, références, positions et tailles des éléments pour les actions suivantes. La recherche par expression régulière renvoie les lignes correspondantes avec le contexte proche et les nœuds parents.

#### Actions du navigateur {#browser-actions}

- **`browser_actions`** : Enchaîne les actions de la souris, le remplissage des champs, les raccourcis clavier, les réponses aux boîtes de dialogue et les attentes dans un seul appel. Accepte ou ferme les alertes et confirmations du navigateur, ou saisit du texte dans les boîtes de saisie. Par exemple, remplit un champ de recherche, envoie la requête, attend les résultats et en ouvre un. L’IA peut regrouper les étapes connues et demander des vues séparées lorsqu’elle doit vérifier une modification de la page. Cela évite un aller-retour avec l’agent entre deux étapes. C’est utile pour les menus qui disparaissent rapidement et les autres contrôles qui demandent d’enchaîner vite les actions.

    Affiche les menus et infobulles au survol, clique sur les boutons et liens, ou place la souris sur un panneau imbriqué pour le faire défiler verticalement ou horizontalement. Les déplacements et clics acceptent des sélecteurs, des références de la vue structurée ou des coordonnées. Pour les éléments ciblés, l’outil attend automatiquement leur présence et fait défiler la page pour les rendre visibles. Il accepte les déplacements par coordonnées en plusieurs étapes, les clics gauche, droit et central, ainsi que les doubles clics.

    Ciblez les champs n’importe où sur la page avec des sélecteurs ou des références. Saisissez du texte, cochez ou décochez des cases, sélectionnez des boutons radio et choisissez une ou plusieurs options de listes déroulantes natives par leur libellé visible. Le texte peut remplacer le contenu, l’effacer ou continuer à la position du curseur. Les raccourcis clavier permettent de sélectionner et supprimer du texte, de changer le focus, d’envoyer des formulaires ou de fermer des menus. Le mode lent saisit un caractère à la fois, avec des pauses aléatoires entre les caractères et entre toutes les actions.

    Attendez que les résultats apparaissent, que les couches de chargement disparaissent ou que les événements de chargement de la page se produisent avant l’action suivante. L’outil accepte aussi les pauses fixes et l’attente d’une stabilisation de l’activité réseau.

#### JavaScript {#javascript}

- **`browser_evaluate`** : Exécute JavaScript sur la page actuelle pour une extraction personnalisée, des calculs ou des tâches propres à la page. L’IA peut réunir des données de plusieurs éléments, lire l’état de l’application ou modifier le contenu. L’outil accepte les scripts asynchrones et renvoie leurs résultats en JSON.

#### Historique réseau {#network-history}

- **`browser_network_requests`** : Recherche les requêtes terminées parmi les onglets, les chargements de page et les actions du navigateur. Trouvez les appels d’API derrière les données d’une page, vérifiez les erreurs HTTP et suivez les redirections enregistrées. Les ressources statiques sont cachées par défaut pour réduire le résultat. Les détails sont renvoyés en JSON, avec une pagination pour les longs historiques.
- **`browser_network_request`** : Consulte le résumé, les en-têtes, les données envoyées ou le corps textuel de la réponse d’une requête enregistrée. Renvoie toute la partie choisie en JSON structuré sans charger la page ni renvoyer la requête. Les réponses enregistrées restent disponibles après un changement de page. Des limites s’appliquent à la taille de l’historique ; une note explique les corps non textuels, trop volumineux ou impossibles à lire. Lisez les détails nécessaires avant de fermer la session MCP.

Les corps de réponse sont lus et enregistrés uniquement pour les valeurs de `Content-Type` textuelles prises en charge, comme HTML, JSON, XML ou JavaScript. Pour les types binaires, absents ou inconnus, les métadonnées et en-têtes de la requête sont conservés, sans lire ni enregistrer le corps. Le navigateur continue de charger les ressources normalement.

Seules les requêtes terminées sont enregistrées, y compris les réponses HTTP 4xx et 5xx. Les requêtes en échec ou encore en cours sont omises. Les entrées apparaissent une fois la capture terminée ; lire l’historique ou fermer la session n’attend pas les captures. Celles qui sont encore en cours lors d’une navigation ou d’une fermeture peuvent être omises. Les octets enregistrés viennent du navigateur et peuvent différer de ceux du serveur. Le texte suit le décodage UTF-8 de Playwright lorsqu’il est valide, sinon l’encodage déclaré.

### Shadow DOM {#shadow-dom}

Définissez `pierce_shadow=true` dans `browser_fetch_once` ou dans chaque appel à `browser_fetch` pour inclure le contenu des Shadow DOM ouverts. La valeur par défaut est `false`. Consultez [Shadow DOM](../fetching/stealthy.md#shadow-dom) pour voir des exemples de sélecteurs et leurs limites.

Les sélecteurs du navigateur peuvent aussi cibler des éléments dans un Shadow DOM fermé et interagir avec eux.

### Fonctions principales {#key-capabilities}

- **Extraction de contenu** : Convertissez des pages ou des éléments en Markdown ou HTML, ou extrayez une version propre du texte.
- **Sélecteurs CSS** : Utilisez le moteur de Scrapling pour choisir des éléments précis avant de transmettre le contenu à l’IA.
- **Contournement des protections antibot** : Gérez Turnstile, Interstitial et d’autres protections de Cloudflare.
- **Proxies** : Utilisez des proxies pour masquer votre adresse et choisir la localisation des requêtes.
- **Imitation du navigateur** : Imitez de vrais navigateurs avec l’empreinte TLS, des en-têtes correspondant à leur version et d’autres options.
- **Sessions persistantes** : Réutilisez les sessions du navigateur entre les requêtes pour améliorer les performances.
- **Blocage des publicités** : Tous les outils de navigateur bloquent automatiquement les requêtes vers environ 3 500 domaines connus de publicité et de suivi. Cela économise des tokens et accélère le chargement.
- **Protection contre l’injection d’instructions** : Supprime automatiquement le contenu caché qui pourrait servir à attaquer le modèle : éléments cachés par des styles en ligne, aria-hidden, slots cachés, caractères de largeur nulle, commentaires HTML et balises template.

## Installation {#installation}

Installez Scrapling avec la prise en charge de MCP, puis vérifiez que les dépendances du navigateur sont aussi installées.

```bash
# Install Scrapling with MCP server dependencies
pip install "scrapling[ai]"

# Install browser dependencies
scrapling install
```

Vous pouvez aussi utiliser l’image Docker directement depuis le registre Docker :
```bash
docker pull pyd4vinci/scrapling
```
Ou la télécharger depuis le registre GitHub :
```bash
docker pull ghcr.io/d4vinci/scrapling:latest
```

## Configurer le serveur MCP {#setting-up-the-mcp-server}

Voici comment ajouter le serveur MCP de Scrapling à [Claude Desktop](https://claude.ai/download) et [Claude Code](https://www.anthropic.com/claude-code). Les mêmes étapes générales s’appliquent aux autres chatbots compatibles avec MCP :

!!! note "Note"
    La commande `scrapling-mcp` des exemples a été ajoutée dans la version 0.4.13 comme raccourci de `scrapling mcp`. Elle facilite l’ajout de Scrapling aux registres et clients MCP qui attendent une seule commande. Avec une version plus ancienne, utilisez la commande `scrapling` avec `mcp` comme premier argument.

### Claude Desktop {#claude-desktop}

1. Ouvrez Claude Desktop.
2. Cliquez sur le menu (☰) en haut à gauche, puis sur Settings → Developer → Edit Config.
3. Ajoutez la configuration du serveur MCP de Scrapling :
```json
"ScraplingServer": {
  "command": "scrapling-mcp"
}
```
S’il s’agit de votre premier serveur MCP, utilisez ce contenu pour le fichier :
```json
{
  "mcpServers": {
    "ScraplingServer": {
      "command": "scrapling-mcp"
    }
  }
}
```
Selon l’[article officiel](https://modelcontextprotocol.io/quickstart/user), cette action crée un fichier de configuration s’il n’existe pas encore, ou ouvre le fichier existant. Il se trouve ici :

1. **MacOS** : `~/Library/Application Support/Claude/claude_desktop_config.json`
2. **Windows** : `%APPDATA%\Claude\claude_desktop_config.json`

Pour vous assurer que cela fonctionne, utilisez le chemin complet de l’exécutable `scrapling-mcp`. Vous pouvez le trouver avec :

1. **MacOS** : `which scrapling-mcp`
2. **Windows** : `where scrapling-mcp`

Sur mon Mac, le résultat était `/Users/<MyUsername>/.venv/bin/scrapling-mcp`. J’ai donc utilisé cette configuration :
```json
{
  "mcpServers": {
    "ScraplingServer": {
      "command": "/Users/<MyUsername>/.venv/bin/scrapling-mcp"
    }
  }
}
```
#### Docker {#docker}

Si vous utilisez l’image Docker, la configuration ressemble à ceci :
```json
{
  "mcpServers": {
    "ScraplingServer": {
      "command": "docker",
      "args": [
        "run", "-i", "--rm", "pyd4vinci/scrapling", "mcp"
      ]
    }
  }
}
```

La même logique s’applique à [Cursor](https://cursor.com/docs/context/mcp), [WindSurf](https://windsurf.com/university/tutorials/configuring-first-mcp-server) et aux autres clients.

### Claude Code {#claude-code}

Avec [Claude Code](https://www.anthropic.com/claude-code), c’est plus simple :

```bash
claude mcp add ScraplingServer "/Users/<MyUsername>/.venv/bin/scrapling-mcp"
```
Pour obtenir le chemin de l’exécutable de Scrapling :

1. **MacOS** : `which scrapling-mcp`
2. **Windows** : `where scrapling-mcp`

Consultez l’article d’Anthropic sur [l’ajout de serveurs MCP à Claude Code](https://docs.anthropic.com/en/docs/claude-code/mcp#option-1%3A-add-a-local-stdio-server) pour plus de détails.

Après l’ajout du serveur, quittez complètement l’application et relancez-la. Dans Claude Desktop, vous devriez voir l’indicateur de serveur MCP (🔧) en bas à droite du champ de saisie, ou `ScraplingServer` dans le menu `Search and tools` de ce champ.

### Exécutable de navigateur personnalisé {#custom-browser-executable}

Les outils `browser_fetch_once` et `browser_open` peuvent utiliser un exécutable de navigateur compatible avec Chromium à la place du Chromium fourni. Cela convient aux versions personnalisées du navigateur ou aux moteurs légers.

Pour le définir une seule fois pour tout le serveur MCP, passez le chemin de l’exécutable au démarrage :

```bash
scrapling-mcp --executable-path "/path/to/chromium"
```

Dans la configuration de Claude Desktop, ajoutez l’option aux arguments du serveur :

```json
{
  "mcpServers": {
    "ScraplingServer": {
      "command": "/Users/<MyUsername>/.venv/bin/scrapling-mcp",
      "args": [
        "--executable-path",
        "/path/to/chromium"
      ]
    }
  }
}
```

Vous pouvez aussi définir la variable d’environnement `SCRAPLING_EXECUTABLE_PATH` avant de démarrer le serveur. L’IA peut toujours choisir un autre exécutable pour une récupération avec `browser_fetch_once` ou à l’ouverture d’une session avec `browser_open`.

### Se connecter à des navigateurs distants {#connecting-to-remote-browsers}

`browser_open` n’a pas besoin de lancer un navigateur local. Passez une URL CDP pour vous connecter à un navigateur déjà ouvert avec le [Chrome DevTools Protocol](https://chromedevtools.github.io/devtools-protocol/). Il peut se trouver sur le même ordinateur, sur un autre ou chez un fournisseur de navigateurs gérés :
```
Open a stealthy browser session on wss://cdp.provider.example/session/abc123, then use it to scrape the product details from https://shop.example.com. Close the session when you're done.
```
Le `session_id` renvoyé s’utilise comme d’habitude avec `browser_fetch`, `browser_extract`, `browser_actions`, `browser_evaluate`, `browser_screenshot`, `browser_network_requests`, `browser_network_request`, `browser_save_state` et `browser_load_state`.

L’URL peut être un endpoint WebSocket (`ws://`/`wss://`), comme ceux fournis par les services de navigateurs, ou l’endpoint HTTP d’un navigateur que vous avez lancé avec le port de débogage distant activé :
```commandline
chrome --remote-debugging-port=9222
```
Dans ce cas, connectez-vous avec `cdp_url="http://localhost:9222"`, ou avec l’adresse de l’hôte si le navigateur tourne sur un autre ordinateur.

!!! note "Notes"

    * Comme le navigateur est déjà ouvert, les sessions CDP ignorent les options qui ne servent qu’au lancement : `headless`, `real_chrome` et `executable_path`, y compris la valeur par défaut du serveur décrite plus haut.<br/>
    * Les autres options s’appliquent toujours (`locale`, `useragent`, `proxy`, `cookies`, `timezone_id`, etc.), car chaque session crée son propre contexte dans le navigateur distant.

### Streamable HTTP {#streamable-http}

Depuis la version 0.3.6, le serveur MCP peut utiliser le transport 'Streamable HTTP' à la place du transport classique 'stdio'.

Au lieu de cette commande pour 'stdio' :
```bash
scrapling-mcp
```
Utilisez la suivante pour activer 'Streamable HTTP' :
```bash
scrapling-mcp --http
```
Par défaut, le serveur écoute sur '127.0.0.1', au port 8000. Vous pouvez modifier ces deux valeurs :
```bash
scrapling-mcp --http --host '0.0.0.0' --port 8000
```
La configuration par défaut n’accepte que les connexions du même ordinateur. Passez `--host '0.0.0.0'` pour rendre le serveur accessible depuis le réseau. Ce choix est indépendant de l’authentification décrite ci-dessous.

Si vous exécutez 'Streamable HTTP' dans Docker, vous devez utiliser '0.0.0.0' et définir un token. Sinon, le port publié ne peut pas atteindre le serveur, car le '127.0.0.1' du conteneur n’est visible que depuis l’intérieur :
```bash
docker run -p 8000:8000 -e SCRAPLING_MCP_AUTH_TOKEN="<your-token>" pyd4vinci/scrapling mcp --http --host '0.0.0.0'
```

### Authentification {#authentication}

Seul le programme qui a lancé le serveur peut accéder au transport 'stdio'. Avec 'Streamable HTTP', toute personne qui peut atteindre le port peut appeler tous les outils. Cela inclut l’accès à n’importe quelle URL depuis l’ordinateur qui exécute le serveur. C’est pourquoi 'Streamable HTTP' exige une authentification : `--http` seul refuse de démarrer et demande un token :
```bash
scrapling-mcp --http --auth-token "$(openssl rand -hex 32)"
```
Les clients doivent envoyer ce token dans un en-tête `Authorization`. Toute requête sans token est rejetée avec un `401` :
```json
{
  "mcpServers": {
    "ScraplingServer": {
      "url": "https://your-server.example.com/mcp",
      "headers": {
        "Authorization": "Bearer <your-token>"
      }
    }
  }
}
```
Passer le token sur la ligne de commande le laisse dans l’historique du shell et dans la liste des processus. Préférez donc la variable d’environnement `SCRAPLING_MCP_AUTH_TOKEN` :
```bash
export SCRAPLING_MCP_AUTH_TOKEN="<your-token>"
scrapling-mcp --http
```
Si vous voulez vraiment un serveur sans authentification, par exemple pour un test local sur l’adresse par défaut '127.0.0.1', indiquez-le avec `--no-auth` :
```bash
scrapling-mcp --http --no-auth
```
Combiner `--no-auth` avec `--host '0.0.0.0'` rend tous les outils accessibles à toute personne qui peut atteindre le port. Évitez cette combinaison en dehors d’un réseau de confiance.

Quand le serveur écoute sur une adresse publique, indiquez aussi les noms d’hôte qu’il doit accepter. Cela active la protection contre le DNS rebinding, une attaque où un site visité essaie de communiquer avec votre serveur. Vous pouvez répéter l’option :
```bash
scrapling-mcp --http --allowed-host 'your-server.example.com:8000'
```

!!! note "Notes"

    * L’authentification s’applique uniquement à 'Streamable HTTP'. Avec 'stdio', elle est ignorée et le serveur l’indique par un avertissement dans les logs.<br/>
    * HTTP non chiffré envoie le token en clair. Avant d’exposer le serveur sur Internet, placez-le derrière un proxy inverse qui reçoit les connexions TLS et transmet les requêtes au serveur.<br/>
    * Il s’agit d’une seule clé partagée, pas d’identifiants propres à chaque client. Tous les clients utilisent le même token et il faut redémarrer le serveur pour le changer.<br/>
    * Démarrer le serveur avec `--http --no-auth` produit tout de même un avertissement indiquant l’absence d’authentification.<br/>
    * Si vous passez `--auth-token` et `--no-auth` ensemble, le token est conservé et le serveur garde l’authentification.

## Exemples {#examples}

Voici quelques prompts utilisés pour tester le serveur MCP. Vous en trouverez sûrement d’autres encore meilleurs :)

Nous allons passer des instructions simples aux plus complexes. Les exemples utilisent Claude Desktop, mais la même logique vaut pour les autres clients.

1. **Extraction de données web de base**

    Extrayez le contenu principal d’une page en Markdown :

    ```
    Scrape the main content from https://example.com and convert it to markdown format.
    ```

    Claude peut utiliser `make_request` pour récupérer la page et renvoyer un contenu propre et lisible. Les requêtes HTTP ont trois tentatives par défaut, avec une seconde d’attente entre elles. Si la page demande JavaScript ou bloque les requêtes HTTP, l’IA peut utiliser `browser_fetch_once`. Les deux outils ferment leurs propres ressources après l’appel.

    Une version plus précise du même prompt serait :
    ```
    Use regular requests to scrape the main content from https://example.com and convert it to markdown format.
    ```
    Vous indiquez ainsi à Claude quel outil utiliser, sans le laisser deviner. Parfois il commence par des requêtes classiques ; parfois il choisit un navigateur sans raison claire. En règle générale, précisez l’outil à utiliser pour économiser du temps et de l’argent et obtenir des résultats constants.

2. **Extraction de données ciblées**

    Extrayez des éléments précis avec des sélecteurs CSS :

    ```
    Get all product titles from https://shop.example.com using the CSS selector '.product-title'. If the request fails, retry up to 5 times every 10 seconds.
    ```

    Le serveur extrait uniquement les éléments correspondant au sélecteur et les renvoie sous forme de liste structurée. Dans cet exemple, j’ai demandé jusqu’à cinq tentatives en cas de problème de connexion au site. La valeur par défaut suffit toutefois dans la plupart des cas.

3. **Collecter des données de boutiques en ligne**

    Voici un prompt un peu plus complexe :
    ```
    Open a stealthy browser session and visit these e-commerce URLs one at a time:
    - https://shop1.com/product-a
    - https://shop2.com/product-b  
    - https://shop3.com/product-c
    
    Get the product names, prices, and descriptions from each page. Close the session when done.
    ```

    Claude peut réutiliser une session de navigateur, appeler `browser_fetch` pour chaque URL dans l’ordre, puis analyser les données extraites.

4. **Un processus plus avancé**

    Imaginons que je veuille tous les jeux d’action présents sur la première page du PlayStation Store. Je peux utiliser ce prompt :
    ```
    Extract the URLs of all games on this page, then visit each game in order and return a list of all action games: https://store.playstation.com/en-us/pages/browse
    ```
    Demandez à l’IA de réutiliser une session HTTP pour éviter de lancer un navigateur lorsque les données sont accessibles par des requêtes classiques :
    ```
    Open an HTTP session, extract the URLs of all games on this page, then fetch each game in order and return a list of all action games. Close the session when done: https://store.playstation.com/en-us/pages/browse
    ```
    Si vous savez écrire des sélecteurs CSS, vous pouvez limiter le contenu avant que l’IA le lise :
    ```
    Use an HTTP session to extract the URLs of all games on the page below, then fetch each game in order and return a list of all action games.
    The selector for games in the first page is `[href*="/concept/"]` and the selector for the genre in each game page is `[data-qa="gameInfo#releaseInformation#genre-value"]`.
    Close the session when done.

    URL: https://store.playstation.com/en-us/pages/browse
    ```

5. **Obtenir les données d’un site protégé par Cloudflare**

    Si vous pensez que le site utilise Cloudflare, dites-le à Claude pour qu’il n’ait pas à le découvrir seul.
    ```
    What's the price of this product? Be cautious, as it utilizes Cloudflare's Turnstile protection. Make the browser visible while you work.

    https://ao.com/product/oo101uk-ninja-woodfire-outdoor-pizza-oven-brown-99357-685.aspx
    ```

6. **Un processus long**

    Vous pouvez utiliser un prompt comme celui-ci :
    ```
    Extract all product URLs for the following category, then return the prices and details for the first 3 products.
    
    https://www.arnotts.ie/furniture/bedroom/bed-frames/
    ```
    Mais celui-ci serait meilleur :
    ```
    Go to the following category URL and extract all product URLs using the CSS selector "a". Then, reuse the session to fetch the first 3 product pages in order and extract each product’s price and details. Close the session when done.
    
    Keep the output in markdown format to reduce irrelevant content.
    
    Category URL:
    https://www.arnotts.ie/furniture/bedroom/bed-frames/
    ```

7. **Utiliser des sessions persistantes**

    Pour extraire des données de plusieurs pages du même site, utilisez une session de navigateur persistante. Vous évitez ainsi de lancer un navigateur à chaque requête :
    ```
    Open a stealthy browser session, then use it to scrape the main details from the first 5 product pages on https://shop.example.com. Close the session when you're done.
    ```
    Claude utilise `browser_open` pour créer un navigateur persistant, appelle `browser_fetch` pour chaque page de produit dans cette session, puis appelle `close_session` à la fin. C’est bien plus rapide que de lancer un navigateur pour chaque page.

    !!! danger "Danger"

        Fermez toujours les sessions persistantes quand vous avez terminé ! Sinon, elles restent ouvertes.

8. **Utiliser une session persistante pour un processus long**

    Voici un autre exemple long qui fait réfléchir Claude :

    ```
    Use Scrapling MCP to do the following in this order:

    1. Open a stealthy browser session with headless mode off.
    2. Go to this page and collect the number of stars: https://github.com/D4Vinci/Scrapling
    3. From the README, get the URL that shows the number of downloads and go to it.
    4. Get the number of downloads and the top 3 countries from the graph.
    5. Prepare a report with the results.
    6. Close the browser.
    ```

Et ainsi de suite. Votre créativité est la clé.

## Bonnes pratiques {#best-practices}

Voici quelques conseils techniques pour utiliser le serveur.

### 1. Choisir le bon outil {#1-choose-the-right-tool}

- **`make_request`** : Requêtes HTTP rapides pour une seule page ou un appel d’API.
- **`browser_fetch_once`** : Une page JavaScript ou dynamique, ou un site protégé, y compris par Cloudflare.
- **Outils de session** : Requêtes liées, actions du navigateur, captures d’écran et historique réseau.

### 2. Améliorer les performances {#2-optimize-performance}

- Réutilisez une session et récupérez chaque URL dans l’ordre.
- Désactivez les ressources inutiles.
- Définissez des délais d’expiration adaptés.
- Utilisez des sélecteurs CSS pour extraire uniquement le contenu voulu.

### 3. Gérer le contenu dynamique {#3-handle-dynamic-content}

- Utilisez `network_idle` pour les applications à page unique (SPA).
- Définissez `wait_selector` pour attendre des éléments précis.
- Augmentez le délai d’expiration pour les sites lents.

### 4. Qualité des données {#4-data-quality}

- Utilisez `main_content_only=true` pour sélectionner et nettoyer le corps de la page.
- Choisissez un `extraction_type` adapté à votre besoin.

### 5. Protection contre l’injection d’instructions {#5-prompt-injection-protection}

Le serveur MCP nettoie automatiquement le contenu extrait quand `main_content_only` est activé, comme c’est le cas par défaut. Il retire le contenu caché qu’un site malveillant pourrait utiliser pour injecter des instructions dans le contexte de l’IA :

- **Styles en ligne qui masquent le contenu** : `display:none`, `visibility:hidden` et valeurs nulles pour l’opacité, la taille de police, la hauteur, la largeur, la hauteur maximale et la largeur maximale.
- **Éléments cachés pour l’accessibilité** : `aria-hidden="true"`.
- **Balises de template et slots cachés** : Éléments `<template>` et `<slot hidden>`.
- **Commentaires HTML** : `<!-- ... -->`.
- **Caractères de largeur nulle** : Caractères Unicode invisibles, comme les espaces de largeur nulle.

Cette protection s’applique automatiquement à l’extraction HTML, Markdown et texte. Gardez `main_content_only=true`, la valeur par défaut, pour une protection maximale.

### 6. Gérer les sessions {#6-manage-sessions}

- Utilisez `make_request` ou `browser_fetch_once` pour une récupération indépendante. Ces outils ferment leurs propres ressources et ne laissent pas de session pour les appels suivants.
- Utilisez `browser_open` pour créer une session persistante lorsque vous travaillez sur plusieurs pages. Appelez ensuite `browser_fetch` pour chaque page dans cette session.
- Pour plusieurs requêtes HTTP sans navigateur, utilisez `open_request_session`, puis `session_make_request` pour chacune. La session conserve les cookies, les connexions et l’empreinte du navigateur (`impersonate`) entre les appels.
- Les sessions gardent la configuration définie à leur ouverture : headless, locale, cookies et options de discrétion pour les navigateurs ; `impersonate` et `proxy` pour les sessions HTTP. Les options propres à une requête, comme timeout, wait_selector, network_idle et solve_cloudflare, sont passées à `browser_fetch`/`session_make_request` à chaque appel. Leurs valeurs par défaut figurent dans les schémas des outils.
- `browser_fetch` peut résoudre les défis Cloudflare dans la session ouverte de navigateur Stealthy.
- Fermez toujours les sessions avec `close_session` à la fin pour libérer les ressources.
- Utilisez `list_sessions` pour vérifier quelles sessions restent actives et consulter le `settings` utilisé à leur création. Il est renvoyé à l’agent IA et reste vide pour les sessions CDP.
- Passez votre propre `session_id` aux outils d’ouverture pour donner des noms clairs aux sessions, comme `"search"` ou `"checkout"`, plutôt que la valeur hexadécimale aléatoire. Les outils lèvent une erreur si l’identifiant est déjà utilisé, pour que vous détectiez le conflit dès le départ.

### 7. Captures d’écran {#7-capturing-screenshots}

- `browser_screenshot` capture la page déjà ouverte avec `browser_fetch` dans une session de navigateur Stealthy. Il ne la recharge pas. L’IA peut donc vérifier les champs remplis, les menus ouverts et les autres résultats de ses actions.
- L’image est renvoyée sous forme de bloc `ImageContent` réel pour que le modèle voie la page directement.
- Capturez la zone visible ou la page entière, y compris le contenu hors écran.
- Capturez un champ, un graphique, une carte ou un résultat pour l’inspecter avec moins de contenu autour. La capture d’un élément peut faire défiler la page pour le rendre visible.
- Choisissez PNG pour une image sans perte ou JPEG avec une qualité réglable pour réduire la taille.
- L’IA peut utiliser `browser_actions` pour attendre le contenu ou terminer les interactions avant la capture.

## Aspects juridiques et éthiques {#legal-and-ethical-considerations}

⚠️ **Consignes importantes :**

- **Consultez robots.txt** : Ouvrez `https://website.com/robots.txt` pour voir les règles d’exploration.
- **Respectez les limites de requêtes** : Ne surchargez pas les serveurs.
- **Conditions d’utilisation** : Lisez et respectez les conditions du site.
- **Droits d’auteur** : Respectez les droits de propriété intellectuelle.
- **Vie privée** : Tenez compte des lois sur la protection des données personnelles.
- **Usage commercial** : Assurez-vous d’avoir l’autorisation d’utiliser les données à des fins commerciales.

---

*Créé avec ❤️ par l’équipe de Scrapling. Bonne extraction !*
