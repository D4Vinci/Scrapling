---
title: "CLI de Scrapling : extraire des données depuis le terminal"
description: "Installez les outils de terminal de Scrapling et choisissez entre les commandes d’extraction, le shell interactif et le serveur MCP. Suivez le guide adapté à votre tâche."
---

# Interface en ligne de commande {#command-line-interface}

Depuis la version 0.3, Scrapling inclut une interface en ligne de commande avec trois fonctions principales :

1. **Shell interactif** : Un environnement d’extraction de données web basé sur IPython, avec de nombreux raccourcis et outils utiles.
2. **Commandes d’extraction** : Extrayez des données de sites depuis le terminal sans programmer.
3. **Commandes utilitaires** : Des outils d’installation et de gestion.

```bash
# Launch interactive shell
scrapling shell

# Convert the content of a page to markdown and save it to a file
scrapling extract get "https://example.com" content.md

# Get help for any command
scrapling --help
scrapling extract --help
```

## Prérequis {#requirements}

Pour utiliser les outils de cette section, installez le groupe de dépendances supplémentaires `shell` :
```bash
pip install "scrapling[shell]"
```
Pour récupérer des pages avec un navigateur, installez aussi ses dépendances :
```bash
scrapling install
```
Cette commande télécharge Chromium et ses dépendances système, puis met à jour la liste des TLD. Les requêtes HTTP n’ont pas besoin de cette étape.
