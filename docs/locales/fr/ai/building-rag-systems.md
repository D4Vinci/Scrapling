---
title: "Convertir des sites en Markdown pour RAG avec Scrapling"
description: "Convertissez les réponses des pages en Markdown ou utilisez ContentSpider pour collecter un site. Préparez les textes à découper et à indexer dans un système RAG."
---

# Créer des systèmes RAG avec Scrapling {#building-rag-systems-with-scrapling}

La qualité d’un système RAG dépend du texte qu’il reçoit. Le HTML brut consomme des tokens pour les balises, la navigation, les scripts et le contenu de suivi. Il peut même transmettre des instructions malveillantes cachées à votre LLM. Scrapling transforme des pages et des sites entiers en Markdown propre et supprime ce contenu caché, sans utiliser de LLM. La collecte est donc rapide et ne coûte rien par page.

## Installation {#installation}

```bash
pip install "scrapling[rag]"

scrapling install
```

L’extra `rag` installe les fetchers avec la conversion en Markdown. Les extras `ai`, `shell` et `all` l’incluent aussi. La commande `scrapling install` télécharge les dépendances du navigateur, nécessaires uniquement aux fetchers qui utilisent un navigateur.

## Convertir une page en Markdown {#one-page-to-markdown}

Chaque [Response](../fetching/choosing.md#response-object) possède une méthode `markdown()` :

```python
from scrapling.fetchers import Fetcher

markdown = Fetcher.get("https://example.com").markdown(main_content_only=True)
```

Elle fonctionne avec tous les fetchers. Vous pouvez donc aussi récupérer une page protégée par Cloudflare en une ligne :

```python
from scrapling.fetchers import StealthyFetcher

markdown = StealthyFetcher.fetch("https://protected.example.com", solve_cloudflare=True).markdown(main_content_only=True)
```

Deux arguments contrôlent le résultat :

- `main_content_only` : Convertit uniquement le contenu à l’intérieur de la balise `<body>` de la page.
- `css_selector` : Convertit uniquement les éléments qui correspondent à un sélecteur CSS, puis réunit toutes les correspondances. Utilisez-le pour extraire exactement la partie utile à votre traitement et économiser des tokens :

```python
markdown = Fetcher.get("https://example.com/docs/page").markdown(css_selector="article")
```

Quels que soient les arguments, les scripts, les styles et le contenu caché sont toujours supprimés avant la conversion. C’est le même nettoyage que celui du [serveur MCP](mcp-server.md) pour protéger les agents IA contre l’injection d’instructions. Il supprime les éléments cachés par des styles en ligne, ceux avec `aria-hidden="true"`, les slots cachés, les balises `<template>`, les commentaires HTML et les caractères de largeur nulle. Le serveur MCP applique ce nettoyage avec `main_content_only=True`.

## Convertir un site entier en un ensemble de fichiers Markdown {#a-whole-website-to-a-markdown-corpus}

Le modèle `ContentSpider` explore un site et convertit chaque page. Il utilise le [système de spiders](../spiders/architecture.md), qui fournit déjà la concurrence, AutoThrottle, le respect de robots.txt et la pause avec reprise :

```python
from scrapling.spiders import ContentSpider

class DocsSpider(ContentSpider):
    name = "docs"
    start_urls = ["https://example.com/docs/"]
    allowed_domains = {"example.com"}
    output_dir = "docs_markdown"
    max_pages = 200

result = DocsSpider().start()
result.items.to_jsonl("docs.jsonl")
```

Chaque page explorée devient un élément avec les clés `url`, `title` et `markdown`. Si vous définissez `output_dir`, chaque page est aussi enregistrée dans un fichier Markdown dont le nom est basé sur son URL. L’exemple ci-dessus produit donc un dossier de fichiers `.md` et un fichier `docs.jsonl` prêt à charger.

Le modèle exige `allowed_domains` pour limiter l’exploration au site visé. Voici les options :

- `css_selector` / `main_content_only` : Passés à `markdown()` pour chaque page. `main_content_only` est activé par défaut.
- `output_dir` : S’il est défini, écrit un fichier Markdown par page.
- `max_pages` : Nombre maximal de pages à convertir. Les requêtes déjà en attente lorsque la limite est atteinte peuvent encore être envoyées, mais leurs pages ne sont pas converties. La valeur par défaut, `0`, désactive la limite.

Par défaut, tous les liens dans `allowed_domains` sont suivis. Comme le modèle repose sur [CrawlSpider](../spiders/generic-templates.md#crawlspider), vous pouvez redéfinir `rules()` avec votre propre [LinkExtractor](../spiders/generic-templates.md#linkextractor-reference) pour contrôler l’exploration. `allow` la limite aux motifs d’URL souhaités, et `deny` exclut les motifs indésirables, comme ceux des pages de connexion, des listes de tags ou des versions à imprimer :

```python
from scrapling.spiders import CrawlRule, LinkExtractor, ContentSpider

class DocsSpider(ContentSpider):
    name = "docs"
    start_urls = ["https://example.com/"]
    allowed_domains = {"example.com"}

    def rules(self):
        return [CrawlRule(LinkExtractor(allow=r"/docs/", deny=[r"/docs/changelog/", r"\?print="]))]
```

`deny` est prioritaire sur `allow`. Une règle peut inclure `priority` ou un hook `process_request`, comme avec tout **CrawlSpider**.

## Charger les données dans une base vectorielle {#feeding-a-vector-store}

Vous pouvez utiliser le fichier JSONL dans tout processus de création d’embeddings. Voici un exemple minimal :

```python
import json

with open("docs.jsonl", encoding="utf-8") as f:
    for line in f:
        page = json.loads(line)
        for chunk in split_into_chunks(page["markdown"]):
            vector_store.add(text=chunk, metadata={"url": page["url"], "title": page["title"]})
```

Utilisez `css_selector` dans le spider pour retirer le contenu répétitif avant de découper le texte, plutôt que de le nettoyer après. Moins vos embeddings contiennent de contenu inutile, meilleurs seront les résultats de recherche.

## Solutions interactives {#interactive-alternatives}

Si vous préférez extraire les données par une conversation, le [serveur MCP](mcp-server.md) donne à votre chatbot IA des outils avec la même extraction en Markdown. L’[Agent skill](agent-skill.md) apprend aux agents de programmation à écrire ce code eux-mêmes.
