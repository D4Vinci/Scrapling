---
title: "Référence de l’API du serveur MCP de Scrapling"
description: "Consultez les outils du serveur MCP et ses modèles de requêtes, réponses et sessions pour extraire des données par HTTP ou navigateur."
---

# Référence du serveur MCP {#mcp-server-api-reference}

Le **serveur MCP de Scrapling** propose seize outils pour extraire des données et interagir avec le navigateur via le Model Context Protocol (MCP). Intégrez Scrapling aux assistants et agents IA pour extraire des données par la conversation, avec des fonctions contre la détection des bots.

Démarrez le serveur MCP avec cette commande :

```bash
scrapling mcp
```

Ou importez directement la classe du serveur :

```python
from scrapling.core.ai import ScraplingMCPServer

server = ScraplingMCPServer()
server.serve(http=False, host="127.0.0.1", port=8000)
```

Pour utiliser votre propre exécutable de navigateur compatible avec Chromium, passez `executable_path` :

```python
server = ScraplingMCPServer(executable_path="/path/to/chromium")
```

## Modèle de réponse {#response-model}

Les outils de récupération de pages et de requêtes HTTP renvoient cette structure, avec une réponse par appel. Les outils de gestion des sessions utilisent les modèles suivants. `browser_screenshot` renvoie une image de la page ou d’un élément, avec l’URL actuelle, sous forme de blocs image et texte. `browser_extract` et `browser_actions` renvoient du texte brut. Les deux outils réseau renvoient du JSON structuré avec les modèles suivants. `browser_evaluate` renvoie le résultat en JSON dans un bloc texte.

## ::: scrapling.core.ai.server.ResponseModel
    handler: python
    :docstring:

## Modèles des requêtes réseau {#network-request-models}

`browser_network_requests` renvoie `NetworkRequestsModel` avec `requests`, `next_cursor`, `has_more` et `dropped_count`. Chaque `NetworkRequestInfo` contient `id`, `url`, `method`, `resource_type` et `status`. Pour continuer, passez `next_cursor` comme `after_id`. `has_more` indique s’il reste des résultats dans l’historique actuel.

`browser_network_request` renvoie `NetworkRequestModel` avec `request_id`, `part`, `data` et `note`. Les résumés et les en-têtes sont des objets. Le contenu complet enregistré est renvoyé comme une chaîne, même si la réponse contient du JSON. `note` explique si des données du contenu manquent ou si les en-têtes sont incomplets.

## ::: scrapling.core.ai._network_formatting.NetworkRequestInfo
    handler: python
    :docstring:

## ::: scrapling.core.ai.server.NetworkRequestsModel
    handler: python
    :docstring:

## ::: scrapling.core.ai._network_formatting.NetworkRequestModel
    handler: python
    :docstring:

## Modèles des sessions {#session-models}

Classes de modèles pour gérer les sessions :

## ::: scrapling.core.ai.server.SessionInfo
    handler: python
    :docstring:

## ::: scrapling.core.ai.server.SessionCreatedModel
    handler: python
    :docstring:

## ::: scrapling.core.ai.server.SessionClosedModel
    handler: python
    :docstring:

## Classe du serveur MCP {#mcp-server-class}

La classe principale du serveur MCP propose les outils suivants :

- **`make_request`** : Récupère une URL par HTTP avec imitation du navigateur et fermeture automatique du client. Accepte GET, POST, PUT et DELETE.
- **`browser_fetch_once`** : Récupère une URL avec un navigateur furtif, exécute JavaScript, gère Cloudflare et ferme le navigateur. Utilisez une session persistante si vous devez agir ensuite ou consulter l’historique réseau.

- **`browser_extract`** : Lit la page actuelle ou un élément sous forme de vue structurée pour l’IA, de HTML, de Markdown ou de texte, sans recharger. Conserve les résultats des formulaires et des actions. Les vues structurées incluent les rôles, noms, références, positions et tailles des éléments. La recherche par expression régulière renvoie les lignes correspondantes, le contexte proche et les nœuds parents.
- **`browser_actions`** : Enchaîne les mouvements de souris, survols, clics, défilements, saisies, raccourcis clavier, réponses aux boîtes de dialogue et attentes dans un appel. Acceptez ou fermez les alertes et confirmations, ou saisissez du texte dans une boîte de dialogue. Vous pouvez saisir une recherche, l’envoyer, attendre et ouvrir un résultat sans faire un appel par étape.

    Les mouvements et clics acceptent des sélecteurs, des références de vues structurées ou des coordonnées. L’outil attend les éléments et les amène dans la zone visible. Il accepte les mouvements par étapes, les clics gauche, droit et central, le double-clic et le défilement dans des panneaux imbriqués.

    Sélectionnez les champs par sélecteur ou référence de vue structurée. Saisissez du texte, cochez ou décochez des cases, sélectionnez des boutons radio et choisissez une ou plusieurs options de listes natives par leur libellé. Remplacez ou effacez le texte, ou écrivez à la position du curseur. Les raccourcis utilisent le focus actuel. Le mode lent ajoute des pauses aléatoires entre les caractères et les actions.

    Attendez le contenu ou la disparition des indicateurs de chargement avec des sélecteurs ou des références de vues structurées. Vous pouvez aussi attendre des événements de chargement, la fin de l’activité réseau ou une durée fixe.

- **`browser_evaluate`** : Exécute du JavaScript dans la page actuelle pour extraire des données personnalisées, faire des calculs, lire l’état de l’application ou modifier le contenu. Accepte les scripts asynchrones et renvoie leurs résultats en JSON.
- **`browser_network_requests`** : Recherche les requêtes du navigateur terminées entre les onglets, navigations et actions. Trouvez les appels API, erreurs HTTP et redirections enregistrés. Masque les ressources statiques par défaut pour réduire les résultats. Ignore les requêtes en échec ou incomplètes. Renvoie des données structurées avec pagination.
- **`browser_network_request`** : Lit le résumé, les en-têtes, les données envoyées ou le contenu textuel d’une requête enregistrée sous forme de JSON structuré, sans la répéter. Renvoie toute la partie choisie. Les réponses enregistrées restent disponibles après un changement de page, y compris les réponses HTTP 4xx et 5xx. Les entrées apparaissent quand la capture se termine. Consulter l’historique ou fermer la session n’attend pas les captures en cours, qui peuvent être perdues lors de la navigation ou de la fermeture. Les octets viennent de Playwright et peuvent différer de ceux envoyés par le serveur. Le texte utilise le décodage UTF-8 de Playwright lorsqu’il est valide, sinon l’encodage déclaré. Seul le contenu avec un `Content-Type` textuel compatible est lu et enregistré. Pour les types binaires, absents ou inconnus, les métadonnées et les en-têtes sont conservés sans lire le contenu. Cela ne change pas le chargement de la page. L’historique a des limites de taille. Une note facultative explique si le contenu n’est pas du texte, est trop grand ou ne peut pas être lu. Lisez les données nécessaires avant de fermer la session MCP.
- **`browser_fetch`** : Récupère une page dans une session ouverte de navigateur furtif et extrait du HTML, du Markdown, du texte ou une vue structurée. Ces vues peuvent couvrir toute la page ou un élément et incluent des références, positions et tailles pour agir ensuite.

## ::: scrapling.core.ai.server.ScraplingMCPServer
    handler: python
    :docstring:
