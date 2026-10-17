---
title: "Suivez et retrouvez des éléments HTML avec l’analyse adaptative"
description: "Enregistrez les propriétés d’un élément et retrouvez-le après une modification du HTML. Apprenez à activer l’analyse adaptative et à utiliser save, retrieve et relocate."
---

# Scraping adaptatif {#adaptive-scraping}

!!! success "Avant de commencer"

    1. Lisez la page [Rechercher des éléments](../parsing/selection.md) pour savoir comment trouver et extraire des éléments d’un objet [Selector](../parsing/main_classes.md#selector).
    2. Lisez la page [Classes principales](../parsing/main_classes.md) pour connaître la classe [Selector](../parsing/main_classes.md#selector).

Le scraping adaptatif, auparavant appelé automatch, est l’une des fonctions les plus puissantes de Scrapling. Il permet à votre scraper de continuer à fonctionner quand un site change, en suivant les éléments et en les retrouvant.

Supposons que vous vouliez extraire des données d’une page avec cette structure :
```html
<div class="container">
    <section class="products">
        <article class="product" id="p1">
            <h3>Product 1</h3>
            <p class="description">Description 1</p>
        </article>
        <article class="product" id="p2">
            <h3>Product 2</h3>
            <p class="description">Description 2</p>
        </article>
    </section>
</div>
```
Vous voulez extraire le premier produit, celui dont l’ID est `p1`. Vous utiliseriez sans doute ce sélecteur :
```python
page.css('#p1')
```
Si les responsables du site modifient la structure ainsi :
```html
<div class="new-container">
    <div class="product-wrapper">
        <section class="products">
            <article class="product new-class" data-id="p1">
                <div class="product-info">
                    <h3>Product 1</h3>
                    <p class="new-description">Description 1</p>
                </div>
            </article>
            <article class="product new-class" data-id="p2">
                <div class="product-info">
                    <h3>Product 2</h3>
                    <p class="new-description">Description 2</p>
                </div>
            </article>
        </section>
    </div>
</div>
```
Le sélecteur ne fonctionnera plus et vous devrez modifier votre code. C’est là que la fonction `adaptive` de Scrapling intervient.

Vous pouvez activer `adaptive` la première fois que vous sélectionnez un élément. Si le sélecteur ne le trouve plus la fois suivante, Scrapling utilise les propriétés enregistrées pour chercher l’élément le plus ressemblant dans la page. Et cela sans IA :)

```python
from scrapling import Selector, Fetcher
# Before the change
page = Selector(page_source, adaptive=True, url='example.com')
# or
Fetcher.adaptive = True
page = Fetcher.get('https://example.com')
# then
element = page.css('#p1', auto_save=True)
if not element:  # One day website changes?
    element = page.css('#p1', adaptive=True)  # Scrapling still finds it!
# the rest of your code...
```
Vous trouverez ci-dessous un exemple, puis les détails d’utilisation. Cette fonction marche avec toutes les méthodes de sélection, pas seulement CSS et XPath.

## Un exemple réel {#real-world-scenario}
Prenons un vrai site et utilisons un fetcher pour obtenir son code. Pour tester une modification de structure, il faudrait enregistrer le code avant la mise à jour, puis attendre le changement. Il est presque impossible de savoir quand cela arrivera, sauf si je connais le propriétaire. Mais ce serait alors un test préparé à l’avance, haha.

Pour résoudre ce problème, je vais utiliser [The Web Archive](https://archive.org/) et sa [Wayback Machine](https://web.archive.org/). Voici une copie du [site StackOverFlow en 2010](https://web.archive.org/web/20100102003420/http://stackoverflow.com/). Cela remonte à loin, non ?</br>Voyons si la fonction adaptative peut extraire le même bouton dans la version de 2010 et dans la version actuelle avec un seul sélecteur :)

Pour extraire le bouton Questions dans l’ancienne version, je peux utiliser `#hmenus > div:nth-child(1) > ul > li:nth-child(1) > a`. Ce sélecteur est très précis parce qu’il a été généré par Google Chrome.


Testons le même sélecteur dans les deux versions :
```python
from scrapling import Fetcher
selector = '#hmenus > div:nth-child(1) > ul > li:nth-child(1) > a'
old_url = "https://web.archive.org/web/20100102003420/http://stackoverflow.com/"
new_url = "https://stackoverflow.com/"
Fetcher.configure(adaptive = True, adaptive_domain='stackoverflow.com')
page = Fetcher.get(old_url, timeout=30)
element1 = page.css(selector, auto_save=True)[0]
# Same selector but used in the updated website
page = Fetcher.get(new_url)
element2 = page.css(selector, adaptive=True)[0]

if element1.text == element2.text:
    print('Scrapling found the same element in the old and new designs!')  # Spoiler alert: it does!
```
Un nouvel argument apparaît ici : `adaptive_domain`. Pour Scrapling, `archive.org` et `stackoverflow.com` sont deux domaines distincts, donc leurs données `adaptive` sont séparées. Pour indiquer qu’il s’agit du même site, nous passons le même domaine personnalisé lors de l’enregistrement des données `adaptive` des deux versions.

Dans un cas réel, le code serait identique, mais utiliserait la même URL pour les deux requêtes. Vous n’auriez pas besoin de `adaptive_domain`. C’est l’exemple le plus proche d’un cas réel que je puisse montrer. J’espère qu’il est clair :)

J’ai utilisé les classes `Selector` et `Fetcher` dans les deux exemples pour montrer que la logique adaptative est la même.

!!! info "Information"

    `adaptive_domain` a surtout été ajouté pour gérer les sites qui changent d’URL en même temps que de structure ou de présentation. Cet argument permet de réutiliser les données adaptatives déjà enregistrées avec la nouvelle URL. Sans lui, Scrapling considère qu’il s’agit d’un autre site et n’utilise plus les anciennes données.

## Comment fonctionne le scraping adaptatif {#how-the-adaptive-scraping-feature-works}
Le scraping adaptatif se déroule en deux étapes :

1. **Enregistrer** : stocker les propriétés qui distinguent chaque élément.
2. **Rechercher une correspondance** : retrouver ensuite les éléments aux propriétés similaires.

Supposons que vous ayez sélectionné un élément avec n’importe quelle méthode. Vous voulez que la bibliothèque le retrouve lors de la prochaine collecte, même si la structure ou la présentation du site change.

Sans entrer dans trop de détails techniques, voici le fonctionnement :

  1. Vous demandez à Scrapling d’enregistrer les propriétés de l’élément avec l’une des méthodes présentées plus bas.
  2. Scrapling enregistre ces propriétés dans la base de données configurée, SQLite par défaut.
  3. Les responsables du site peuvent modifier ou supprimer n’importe quelle propriété de l’élément. Aucune ne peut donc servir d’identifiant unique dans la base de données. Pour résoudre ce problème, le système de stockage utilise deux valeurs :
     1. Le domaine du site actuel. Avec `Selector`, indiquez-le à la création de l’objet. Avec un fetcher, il est obtenu automatiquement à partir de l’URL.
     2. Un `identifier` pour retrouver les propriétés de l’élément dans la base. Vous n’avez pas toujours à le définir vous-même, comme nous le verrons plus loin.

     Ensemble, ces valeurs permettent de récupérer les propriétés enregistrées de l’élément.

  4. Quand la structure du site change, activez `adaptive` pour rechercher l’élément. Scrapling récupère les propriétés enregistrées et les compare à celles de tous les éléments de la page. Il attribue à chaque élément un score de ressemblance, en tenant compte des données présentées ci-dessous.
  5. Il renvoie l’élément ou les éléments ayant le meilleur score.

### Les propriétés de l’élément {#the-unique-properties}
Vous vous demandez peut-être quelles propriétés peuvent être utiles si toutes sont susceptibles de changer ou de disparaître.

Scrapling utilise ces données :

- Le nom de la balise, le texte, les attributs avec leurs noms et leurs valeurs, les noms de balises des éléments frères et les noms de balises du chemin de l’élément.
- Le nom de la balise du parent, ses attributs avec leurs noms et leurs valeurs, et son texte.

La comparaison n’exige pas des valeurs identiques. Elle mesure leur ressemblance. Elle tient même compte de leur ordre, par exemple celui des noms de classes avant et après la modification.

## Utiliser la fonction adaptative {#how-to-use-adaptive-feature}
Vous pouvez appliquer la fonction adaptative à tout élément trouvé. Elle est aussi disponible sous forme d’arguments dans les méthodes CSS et XPath, comme nous l’avons vu. Nous y reviendrons plus bas.

Activez d’abord `adaptive` en passant `adaptive=True` à la création d’un [Selector](main_classes.md#selector), ou activez-la dans le fetcher utilisé, comme ci-dessous.

Exemples :
```python
from scrapling import Selector, Fetcher
page = Selector(html_doc, adaptive=True)
# OR
Fetcher.adaptive = True
page = Fetcher.get('https://example.com')
```
Si vous utilisez [Selector](main_classes.md#selector), passez l’URL du site avec l’argument `url`. Scrapling peut ainsi séparer les propriétés enregistrées par domaine.

Sans URL, la valeur `default` est utilisée dans ce champ lors de l’enregistrement. Cela ne pose problème que si vous réutilisez ensuite le même identifiant pour un autre site sans indiquer son URL. Chaque enregistrement remplace les données précédentes, et `adaptive` utilise uniquement les dernières propriétés enregistrées.

Les arguments `storage` et `storage_args` configurent la connexion à la base de données. Par défaut, la bibliothèque utilise sa propre classe SQLite. Vous n’avez besoin de ces arguments que pour créer votre propre système de stockage, décrit dans [une page de la section développement](../development/adaptive_storage_system.md).

Une fois `adaptive` activée globalement, vous avez deux façons principales de l’utiliser.

### Avec la sélection CSS ou XPath {#the-cssxpath-selection-way}
Comme dans l’exemple précédent, utilisez d’abord `auto_save` pour sélectionner un élément présent dans la page :
```python
element = page.css('#p1', auto_save=True)
```
Si le sélecteur ne le trouve plus, utilisez le même sélecteur avec `adaptive` pour que la bibliothèque le recherche :
```python
element = page.css('#p1', adaptive=True)
```
Plutôt simple, non ?

Plusieurs opérations se déroulent en coulisses. Vous vous souvenez de l’identifiant qui permet de récupérer l’élément ? Les méthodes `css` et `xpath` utilisent automatiquement le sélecteur comme identifiant pour vous simplifier la tâche :)

Vous pouvez aussi passer `identifier` à ces méthodes pour définir votre propre valeur. Cela peut être utile dans certains cas, y compris lors de l’enregistrement avec `auto_save`.

### Manuellement {#the-manual-way}
Vous pouvez enregistrer et récupérer un élément manuellement, puis le retrouver avec `adaptive`. Cela fonctionne avec les éléments obtenus par n’importe quelle méthode de sélection.

Par exemple, supposons que vous trouviez un élément par son texte :
```python
element = page.find_by_text('Tipping the Velvet', first_match=True)
```
Enregistrez ses propriétés avec `save`. Dans ce cas, vous devez choisir l’identifiant. J’ai utilisé `my_special_element` ici. Dans votre code, choisissez un nom qui décrit l’élément, comme vous le faites pour vos variables :)
```python
page.save(element, 'my_special_element')
```
Plus tard, vous pouvez récupérer les données et rechercher l’élément dans la page avec `adaptive` :
```python
>>> element_dict = page.retrieve('my_special_element')
>>> page.relocate(element_dict, selector_type=True)
[<data='<a href="catalogue/tipping-the-velvet_99...' parent='<h3><a href="catalogue/tipping-the-velve...'>]
>>> page.relocate(element_dict, selector_type=True).css('::text').getall()
['Tipping the Velvet']
```
Pour cela, utilisez `retrieve` et `relocate`.

Pour conserver le résultat sous forme d’objet `lxml.etree`, ne passez pas `selector_type` :
```python
>>> page.relocate(element_dict)
[<Element a at 0x105a2a7b0>]
```

## Résoudre les problèmes {#troubleshooting}

### Aucune correspondance trouvée {#no-matches-found}
```python
# 1. Check if data was saved
element_data = page.retrieve('identifier')
if not element_data:
    print("No data saved for this identifier")

# 2. Try with different identifier
products = page.css('.product', adaptive=True, identifier='old_selector')

# 3. Save again with new identifier
products = page.css('.new-product', auto_save=True, identifier='new_identifier')
```

### Mauvais éléments trouvés {#wrong-elements-matched}
```python
# Use more specific selectors
products = page.css('.product-list .product', auto_save=True)

# Or save with more context
product = page.find_by_text('Product Name').parent
page.save(product, 'specific_product')
```

## Problèmes connus {#known-issues}
Lors de l’enregistrement avec `adaptive`, seules les propriétés du premier élément trouvé sont conservées. Si votre sélecteur trouve plusieurs éléments à différents endroits de la page, `adaptive` ne retrouvera que le premier. Cela ne concerne pas les sélecteurs CSS combinés, par exemple ceux séparés par des virgules. Ils sont séparés et exécutés un par un.

## Pour terminer {#final-thoughts}
Expliquer cette fonction en détail sans la compliquer a été un défi. Si quelque chose reste flou, écrivez dans la [section des discussions](https://github.com/D4Vinci/Scrapling/discussions) et je vous répondrai dès que possible. Vous pouvez aussi utiliser le serveur Discord ou me contacter en privé :)