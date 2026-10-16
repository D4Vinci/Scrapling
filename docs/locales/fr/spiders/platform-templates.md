---
title: "Extrayez les données des produits Shopify avec Python"
description: "Extrayez le catalogue d’une boutique Shopify avec ShopifySpider. Indiquez son URL, collectez les variantes des produits et consultez les champs de chaque élément."
---

# Modèles de spiders pour les plateformes {#platform-spider-templates}

Les modèles génériques couvrent des *façons* d’explorer, comme suivre des liens ou parcourir des plans de site. Les modèles pour plateformes visent des *plateformes* qui proposent la même structure de données sur de nombreux sites indépendants. Le spider sait déjà où chercher les données. Vous indiquez simplement le domaine.

## ShopifySpider {#shopifyspider}

`ShopifySpider` extrait tous les produits d’une boutique Shopify par l’API JSON de la plateforme, sans utiliser le HTML du site.

```python
from scrapling.spiders import ShopifySpider

class MyStore(ShopifySpider):
    target_website = "example.com"

result = MyStore().start()
print(result.items[0])
```

Définissez `target_website` avec le domaine de la boutique. S’il est vide, le spider utilise la première valeur de `start_urls`, puis celle de `allowed_domains` si nécessaire. Si les trois sont vides, il lève `ValueError`. Les URL complètes sont automatiquement réduites à leur domaine.

### Fonctionnement {#how-it-works}

1. Parcourt les pages de `https://<store>/collections.json`, avec 250 collections par page, la limite de la plateforme.
2. Pour chaque collection qui indique avoir des produits, parcourt les pages de `/collections/<handle>/products.json`.
3. Produit un élément par variante de produit, sans répéter les variantes présentes dans plusieurs collections.

### Champs de chaque élément {#item-fields}

| Champ | Origine |
|-------|---------|
| `name` | Titre du produit, suivi du titre de la variante si ce n’est pas la variante par défaut |
| `price` | Prix de la variante sous forme de chaîne, tel que Shopify le renvoie |
| `category` | Identifiant textuel de la collection dans l’URL, avec une majuscule au début de chaque mot (`summer-sale` devient `Summer Sale`) |
| `brand` | Fournisseur du produit |
| `identifier` | Identifiant de la variante |
| `sku` | SKU de la variante, ou `""` si la boutique n’en définit pas |
| `stock` | `None` si la variante est disponible, ou `0` si elle est épuisée |
| `image_url` | Première image du produit, ou `""` |
| `url` | Page du produit dans la collection |
| `description` | Contenu de `body_html` du produit, sans les balises HTML |
| `old_price` | `compare_at_price` s’il s’agit d’un vrai prix avant promotion, sinon `""` |
| `barcode` | Code-barres de la variante, ou `""` (la plupart des boutiques ne le fournissent pas dans ces endpoints) |

Ces champs ne sont pas obligatoires. Redéfinissez `_process_product()` dans votre sous-classe pour changer la structure des éléments ou extraire d’autres champs des données du produit.

### Notes et limites {#notes-and-limits}

- Les endpoints JSON exposent uniquement les produits publiés sur le canal de la boutique en ligne. `products_count` peut donc être supérieur au nombre de produits réellement accessibles. Le spider utilise seulement une valeur non nulle comme signal pour consulter la collection, jamais comme un total attendu.
- Ce modèle ne fonctionnera probablement pas avec les boutiques qui ajoutent des protections ou un mot de passe. Même si vous parvenez à l’utiliser, vous devrez redéfinir de nombreuses parties.
- Toutes les fonctions de `Spider` restent disponibles : limites de concurrence, délais, respect de robots.txt, points de reprise et hooks du cycle de vie.

### Ce qui peut devenir un modèle pour plateforme {#what-qualifies-as-a-platform-template}

Les modèles sont acceptés pour les plateformes qui exposent une structure uniforme, lisible par un programme, sur de nombreux sites indépendants, comme Shopify. Les spiders destinés à un seul site ne font pas partie de la bibliothèque, quelle que soit la popularité du site.
