---
title: "Selector et Selectors de Scrapling : données et navigation"
description: "Découvrez comment Selector et Selectors stockent le HTML, le texte et les attributs. Extrayez des valeurs, résolvez les URL et parcourez parents, enfants et frères."
---

# Classes principales du parser {#parsing-main-classes}

!!! success "Avant de commencer"

    - Lisez [Rechercher des éléments](../parsing/selection.md) pour savoir comment trouver et extraire des éléments d’un objet [Selector](../parsing/main_classes.md#selector).

Après les méthodes de sélection et leurs fonctions, voyons la classe [Selector](#selector) et les autres objets. Cela vous aidera à mieux comprendre le parser.

La classe [Selector](#selector) est au cœur du parser de Scrapling. Elle analyse le HTML et permet de sélectionner des éléments. Vous pouvez l’importer de l’une de ces façons :
```python
from scrapling import Selector
from scrapling.parser import Selector
```
Utilisez-la ensuite directement, comme dans la [vue d’ensemble](../overview.md) :
```python
page = Selector(
    '<html>...</html>',
    url='https://example.com'
)

# Then select elements as you like
elements = page.css('.product')
```
Quand vous fournissez du HTML ou récupérez un site, vous travaillez principalement avec un [Selector](#selector). Les opérations de sélection ou de navigation qui renvoient des éléments de la page donnent un [Selector](#selector) ou un [Selectors](#selectors). Cela ne concerne pas les opérations qui renvoient du texte ou d’autres valeurs.

La page est un [Selector](#selector), et chaque élément qu’elle contient est aussi un [Selector](#selector). Le texte des éléments et des attributs utilise [TextHandler](#texthandler). Les attributs de chaque élément sont stockés dans [AttributesHandler](#attributeshandler). Nous y reviendrons. Commençons par [Selector](#selector).

## Selector {#selector}
### Arguments {#arguments-explained}
Le plus important est `content`, qui reçoit le HTML à analyser sous forme de `str` ou de `bytes`.

`url` définit l’URL de la page, utilisée pour résoudre les liens relatifs et séparer les données adaptatives enregistrées par domaine. Les arguments `adaptive`, `storage` et `storage_args` configurent la fonction [adaptative](adaptive.md). Ils n’ont pas d’effet si vous n’utilisez pas cette fonction.

Ces arguments contrôlent le traitement du HTML :

- **encoding** : encodage utilisé pour analyser le HTML. La valeur par défaut est `UTF-8`.
- **keep_comments** : indique si les commentaires HTML doivent être conservés. Cette option est désactivée par défaut, car les commentaires peuvent poser problème lors de l’extraction.

Nous laisserons `huge_tree` et `root` de côté pour ne pas compliquer cette page.
Ce sont des fonctions avancées dont vous n’avez pas besoin pour commencer. La section développement couvre ces détails si vous souhaitez approfondir.

La plupart des propriétés de la page et de ses éléments ne sont chargées que lorsque vous les utilisez, comme le contenu textuel. Ce chargement à la demande explique en partie la vitesse de Scrapling :)

### Propriétés {#properties}
Nous en avons déjà vu une partie dans la [vue d’ensemble](../overview.md), mais nous allons les détailler avec des exemples plus complets. Les propriétés pour parcourir la page sont regroupées dans la section [navigation](#traversal).

Pour les exemples, analysons cette page HTML :
```html
<html>
  <head>
    <title>Some page</title>
  </head>
  <body>
    <div class="product-list">
      <article class="product" data-id="1">
        <h3>Product 1</h3>
        <p class="description">This is product 1</p>
        <span class="price">$10.99</span>
        <div class="hidden stock">In stock: 5</div>
      </article>
    
      <article class="product" data-id="2">
        <h3>Product 2</h3>
        <p class="description">This is product 2</p>
        <span class="price">$20.99</span>
        <div class="hidden stock">In stock: 3</div>
      </article>
    
      <article class="product" data-id="3">
        <h3>Product 3</h3>
        <p class="description">This is product 3</p>
        <span class="price">$15.99</span>
        <div class="hidden stock">Out of stock</div>
      </article>
    </div>

    <script id="page-data" type="application/json">
      {
        "lastUpdated": "2024-09-22T10:30:00Z",
        "totalProducts": 3
      }
    </script>
  </body>
</html>
```
Chargez la page comme précédemment :
```python
from scrapling import Selector
page = Selector(html_doc)
```
Obtenez tout le texte de la page, y compris celui des éléments internes :
```python
>>> page.get_all_text()
'Some page\n\n    \n\n      \nProduct 1\nThis is product 1\n$10.99\nIn stock: 5\nProduct 2\nThis is product 2\n$20.99\nIn stock: 3\nProduct 3\nThis is product 3\n$15.99\nOut of stock'
```
Obtenez le premier article, qui servira d’exemple :
```python
article = page.find('article')
```
De la même façon, obtenez tout le texte de l’élément et des éléments qu’il contient :
```python
>>> article.get_all_text()
'Product 1\nThis is product 1\n$10.99\nIn stock: 5'
```
Si vous cherchez seulement son texte direct, le résultat sera vide. Dans le HTML ci-dessus, cet élément n’a pas de texte en dehors de ses enfants :
```python
>>> article.text
''
```
La méthode `get_all_text` accepte ces arguments facultatifs :

1. **separator** : séparateur utilisé pour joindre les textes trouvés. La valeur par défaut est '\n'.
2. **strip** : supprime les espaces au début et à la fin de chaque texte avant de les joindre. Désactivé par défaut.
3. **ignore_tags** : tuple de noms de balises à ignorer, ainsi que tout leur contenu. La valeur par défaut est `('script', 'style',)`.
4. **valid_values** : collecte uniquement les textes ayant un contenu. Ignore les textes vides ou composés uniquement d’espaces. Activé par défaut.

Le texte renvoyé est un [TextHandler](#texthandler), pas une chaîne ordinaire. Nous le verrons plus loin. S’il contient du JSON valide, vous pouvez utiliser `.json()` :
```python
>>> script = page.find('script')
>>> script.json()
{'lastUpdated': '2024-09-22T10:30:00Z', 'totalProducts': 3}
```
Obtenez la balise de l’élément :
```python
>>> article.tag
'article'
```
Sur la page directement, vous travaillez avec l’élément racine `html` :
```python
>>> page.tag
'html'
```
La même idée s’applique à `page` et à `element`, nous n’y reviendrons donc pas.

Obtenez les attributs de l’élément :
```python
>>> print(article.attrib)
{'class': 'product', 'data-id': '1'}
```
Accédez à un attribut précis de l’une de ces façons :
```python
article.attrib['class']
article.attrib.get('class')
article['class']  # new in v0.3
```
Vérifiez si un attribut existe avec l’une de ces méthodes :
```python
'class' in article.attrib
'class' in article  # new in v0.3
```
Obtenez le HTML de l’élément :
```python
>>> article.html_content
'<article class="product" data-id="1"><h3>Product 1</h3>\n        <p class="description">This is product 1</p>\n        <span class="price">$10.99</span>\n        <div class="hidden stock">In stock: 5</div>\n      </article>'
```
Obtenez une version du HTML mise en forme pour être plus lisible :
```python
print(article.prettify())
```
```html
<article class="product" data-id="1"><h3>Product 1</h3>
    <p class="description">This is product 1</p>
    <span class="price">$10.99</span>
    <div class="hidden stock">In stock: 5</div>
</article>
```
Utilisez `.body` pour obtenir le contenu brut de la page. Depuis la v0.4, sur les objets `Response` des fetchers, `.body` renvoie toujours des `bytes`.
```python
>>> page.body
'<html>\n  <head>\n    <title>Some page</title>\n  </head>\n  ...'
```
Obtenez tous les ancêtres de l’élément dans l’arbre DOM :
```python
>>> article.path
[<data='<div class="product-list"> <article clas...' parent='<body> <div class="product-list"> <artic...'>,
 <data='<body> <div class="product-list"> <artic...' parent='<html><head><title>Some page</title></he...'>,
 <data='<html><head><title>Some page</title></he...'>]
```
Générez un sélecteur CSS court si possible, sinon un sélecteur complet :
```python
>>> article.generate_css_selector
'body > div > article'
>>> article.generate_full_css_selector
'body > div > article'
```
La même chose avec XPath :
```python
>>> article.generate_xpath_selector
"//body/div/article"
>>> article.generate_full_xpath_selector
"//body/div/article"
```

### Navigation {#traversal}
À partir des éléments précédents, voyons les propriétés et méthodes pour parcourir la page.

Si vous ne connaissez pas l’arbre DOM ou les structures en arbre, cette section peut sembler déroutante. Je vous conseille de lire une présentation de ces notions.

Voici une explication rapide pour commencer.<br/>
L’élément `html` est la racine de l’arbre de la page, car toute page commence par un élément `html`.<br/>
Juste en dessous se trouvent des éléments comme `head` et `body`. Ce sont les enfants de `html`, et cet élément `html` est leur parent. `head` et `body` sont frères parce qu’ils partagent le même parent.

Accédez au parent d’un élément :
```python
>>> article.parent
<data='<div class="product-list"> <article clas...' parent='<body> <div class="product-list"> <artic...'>
>>> article.parent.tag
'div'
```
Vous pouvez enchaîner cette propriété. Cela vaut aussi pour les propriétés et méthodes similaires présentées ensuite.
```python
>>> article.parent.parent.tag
'body'
```
Obtenez les enfants d’un élément :
```python
>>> article.children
[<data='<h3>Product 1</h3>' parent='<article class="product" data-id="1"><h3...'>,
 <data='<p class="description">This is product 1...' parent='<article class="product" data-id="1"><h3...'>,
 <data='<span class="price">$10.99</span>' parent='<article class="product" data-id="1"><h3...'>,
 <data='<div class="hidden stock">In stock: 5</d...' parent='<article class="product" data-id="1"><h3...'>]
```
Obtenez tous les éléments situés en dessous, même aux niveaux plus profonds. Cela fonctionne comme `children`, mais parcourt tous les niveaux :
```python
>>> article.below_elements
[<data='<h3>Product 1</h3>' parent='<article class="product" data-id="1"><h3...'>,
 <data='<p class="description">This is product 1...' parent='<article class="product" data-id="1"><h3...'>,
 <data='<span class="price">$10.99</span>' parent='<article class="product" data-id="1"><h3...'>,
 <data='<div class="hidden stock">In stock: 5</d...' parent='<article class="product" data-id="1"><h3...'>]
```
Ici, le résultat est le même que pour `children`, car les enfants n’ont pas eux-mêmes d’enfants.

Cet exemple avec l’élément de classe `product-list` montre mieux la différence entre `children` et `below_elements` :
```python
>>> products_list = page.css('.product-list')[0]
>>> products_list.children
[<data='<article class="product" data-id="1"><h3...' parent='<div class="product-list"> <article clas...'>,
 <data='<article class="product" data-id="2"><h3...' parent='<div class="product-list"> <article clas...'>,
 <data='<article class="product" data-id="3"><h3...' parent='<div class="product-list"> <article clas...'>]

>>> products_list.below_elements
[<data='<article class="product" data-id="1"><h3...' parent='<div class="product-list"> <article clas...'>,
 <data='<h3>Product 1</h3>' parent='<article class="product" data-id="1"><h3...'>,
 <data='<p class="description">This is product 1...' parent='<article class="product" data-id="1"><h3...'>,
 <data='<span class="price">$10.99</span>' parent='<article class="product" data-id="1"><h3...'>,
 <data='<div class="hidden stock">In stock: 5</d...' parent='<article class="product" data-id="1"><h3...'>,
 <data='<article class="product" data-id="2"><h3...' parent='<div class="product-list"> <article clas...'>,
...]
```
Obtenez les frères d’un élément :
```python
>>> article.siblings
[<data='<article class="product" data-id="2"><h3...' parent='<div class="product-list"> <article clas...'>,
 <data='<article class="product" data-id="3"><h3...' parent='<div class="product-list"> <article clas...'>]
```
Obtenez l’élément suivant :
```python
>>> article.next
<data='<article class="product" data-id="2"><h3...' parent='<div class="product-list"> <article clas...'>
```
La même logique s’applique à `previous` :
```python
>>> article.previous  # It's the first child, so it doesn't have a previous element
>>> second_article = page.css('.product[data-id="2"]')[0]
>>> second_article.previous
<data='<article class="product" data-id="1"><h3...' parent='<div class="product-list"> <article clas...'>
```
Vérifiez rapidement si un élément possède une classe précise :
```python
>>> article.has_class('product')
True
```
Si vous devez remonter au-delà du parent, vous pouvez parcourir tous les ancêtres de l’élément :
```python
for ancestor in article.iterancestors():
    # do something with it...
```
Vous pouvez aussi rechercher un ancêtre qui remplit une condition. Passez une fonction qui reçoit un [Selector](#selector) et renvoie `True` si la condition est remplie, ou `False` sinon :
```python
>>> article.find_ancestor(lambda ancestor: ancestor.has_class('product-list'))
<data='<div class="product-list"> <article clas...' parent='<body> <div class="product-list"> <artic...'>

>>> article.find_ancestor(lambda ancestor: ancestor.css('.product-list'))  # Same result, different approach
<data='<div class="product-list"> <article clas...' parent='<body> <div class="product-list"> <artic...'>
```
## Selectors {#selectors}
`Selectors` est la version liste de [Selector](#selector). Elle hérite du type `List` de Python et conserve les propriétés et méthodes de `List`. Elle ajoute aussi des méthodes pour travailler avec les objets [Selector](#selector) qu’elle contient.

Dans [Selector](#selector), les méthodes et propriétés qui renvoient plusieurs éléments les fournissent dans un objet [Selectors](#selectors).

Depuis la v0.4, toutes les méthodes de sélection renvoient des objets [Selector](#selector)/[Selectors](#selectors), même pour le texte et les attributs. Les nœuds de texte obtenus avec `::text`, `/text()`, `::attr()` ou `/@attr` sont enveloppés dans des objets [Selector](#selector). Leur `tag` vaut `"#text"` et leur propriété `text` renvoie la valeur textuelle. Les autres propriétés renvoient des valeurs vides ou par défaut sans erreur.

```python
page.css('a::text')              # -> Selectors (of text node Selectors)
page.xpath('//a/text()')         # -> Selectors
page.css('a::text').get()        # -> TextHandler (the first text value)
page.css('a::text').getall()     # -> TextHandlers (all text values)
page.css('a::attr(href)')        # -> Selectors
page.xpath('//a/@href')          # -> Selectors
page.css('.price_color')         # -> Selectors
```

### Méthodes d’extraction de données {#data-extraction-methods}
Depuis la v0.4, [Selector](#selector) et [Selectors](#selectors) proposent `get()`, `getall()` et leurs alias `extract_first` et `extract`, selon les conventions de Scrapy. L’ancienne méthode `get_all()` a été supprimée.

**Sur un objet [Selector](#selector) :**

- `get()` renvoie un `TextHandler` : la valeur du texte pour un nœud de texte, ou le HTML externe complet sous forme de chaîne pour un élément HTML.
- `getall()` renvoie une liste `TextHandlers` contenant cette seule chaîne.
- `extract_first` est un alias de `get()`, et `extract` est un alias de `getall()`.

```python
>>> page.css('h3')[0].get()        # Outer HTML of the element
'<h3>Product 1</h3>'

>>> page.css('h3::text')[0].get()  # Text value of the text node
'Product 1'
```

**Sur un objet [Selectors](#selectors) :**

- `get(default=None)` renvoie la chaîne du **premier** élément, ou `default` si la liste est vide.
- `getall()` convertit **tous** les éléments en chaînes et renvoie une liste `TextHandlers`.
- `extract_first` est un alias de `get()`, et `extract` est un alias de `getall()`.

```python
>>> page.css('.price::text').get()      # First price text
'$10.99'

>>> page.css('.price::text').getall()   # All price texts
['$10.99', '$20.99', '$15.99']

>>> page.css('.price::text').get('')    # With default value
'$10.99'
```

Ces méthodes fonctionnent avec tous les types de sélection, comme CSS, XPath et `find`. Elles sont recommandées pour extraire le texte et les attributs dans un style compatible avec Scrapy.

Voyons maintenant ce que [Selectors](#selectors) propose en plus.
### Propriétés {#properties_1}
En plus des opérations habituelles sur les listes Python, comme les parcourir ou en prendre une tranche, vous pouvez effectuer les opérations suivantes :

Exécuter des sélecteurs CSS et XPath directement sur les objets [Selector](#selector) de la liste. Les types renvoyés sont les mêmes que pour `css` et `xpath` de [Selector](#selector). Les arguments sont similaires, sauf que `adaptive` n’est pas disponible ici. Cela facilite l’enchaînement des méthodes.
```pycon
>>> page.css('.product h3::text').getall()
['Product 1', 'Product 2', 'Product 3']
>>> page.css('.product').css('h3::text').getall()
['Product 1', 'Product 2', 'Product 3']
```
Exécuter `re` et `re_first` directement, avec les mêmes arguments que dans [Selector](#selector). Nous les expliquerons dans la section [TextHandler](#texthandler).

Ici, `re_first` fonctionne différemment : il exécute `re` sur chaque [Selector](#selector) et renvoie le premier ayant un résultat. `re` renvoie un [TextHandlers](#texthandlers) qui rassemble tous les objets [TextHandler](#texthandler) dans un seul [TextHandlers](#texthandlers).
```pycon
>>> page.css('.price::text').re(r'[\d.]+')
['10.99', '20.99', '15.99']
>>> page.css('.product h3::text').re(r'Product (\d+)')
['1', '2', '3']
```
Avec `search`, vous pouvez rechercher parmi les objets [Selector](#selector) de la liste. Passez une fonction qui reçoit un [Selector](#selector) comme premier argument et renvoie True ou False. La méthode renvoie le premier [Selector](#selector) qui remplit la condition, ou `None` s’il n’y en a aucun.

```pycon
>>> product = page.css('.product').search(lambda p: p.css('.price::text').get() == '$20.99')
>>> product.css('h3::text').get()
'Product 2'
```
Vous pouvez aussi utiliser `filter`. Il reçoit une fonction comme `search`, mais renvoie un `Selectors` contenant tous les objets [Selector](#selector) qui remplissent la condition.

```pycon
>>> products = page.css('.product').filter(lambda p: float(p.css('.price::text').re_first(r'[\d.]+')) > 15)
>>> products.css('h3::text').getall()
['Product 2', 'Product 3']
```
Vous pouvez accéder au premier ou au dernier élément sans risquer d’erreur d’indice :
```python
>>> page.css('.product').first   # First Selector or None
<data='<article class="product" data-id="1"><h3...'>
>>> page.css('.product').last    # Last Selector or None
<data='<article class="product" data-id="3"><h3...'>
>>> page.css('.nonexistent').first  # Returns None instead of raising IndexError
```

Pour connaître le nombre d’objets [Selector](#selector) dans un [Selectors](#selectors), faites ceci :
```python
page.css('.product').length
```
Cela équivaut à :
```python
len(page.css('.product'))
```
Oui, comme en JavaScript :)

## TextHandler {#texthandler}
Cette classe est importante : les méthodes et propriétés qui renvoient une chaîne utilisent `TextHandler`. Celles qui renvoient une liste de chaînes utilisent [TextHandlers](#texthandlers).

TextHandler hérite de la chaîne standard de Python et accepte donc toutes ses opérations. Pourquoi lui donner un autre nom ?

Parce qu’elle ajoute des méthodes et propriétés absentes des chaînes ordinaires. Comme elle est utilisée pour le texte dans toute la bibliothèque, vous pouvez combiner ces fonctions pour écrire du code plus court et plus clair. Vous pouvez aussi l’importer et l’utiliser avec n’importe quelle chaîne, comme nous le verrons [plus loin](../development/scrapling_custom_types.md).
### Utilisation {#usage}
Les opérations comme prendre une tranche, accéder par indice ou appeler `split`, `replace` et `strip` renvoient un nouveau `TextHandler`. Vous pouvez donc les enchaîner. Si une opération renvoie une chaîne ordinaire au lieu d’un `TextHandler`, ouvrez un ticket pour que nous l’adaptions aussi.

Commençons par `re` et `re_first`. Ce sont les mêmes méthodes que dans [Selector](#selector), [Selectors](#selectors) et [TextHandlers](#texthandlers), avec les mêmes arguments.

- `re` reçoit une expression régulière sous forme de chaîne ou déjà compilée comme premier argument. Il recherche toutes les correspondances et les renvoie dans un [TextHandlers](#texthandlers). `re_first` accepte les mêmes arguments, mais ne renvoie que la première correspondance sous forme de `TextHandler`.
    
    Les arguments suivants sont aussi disponibles :
    
    - **replace_entities** : remplace les références d’entités par les caractères correspondants. Activé par défaut.
    - **clean_match** : ignore les caractères d’espacement, y compris les espaces consécutifs, lors de la comparaison. Désactivé par défaut.
    - **case_sensitive** : distingue les majuscules des minuscules. Activé par défaut. Si vous le désactivez, l’expression régulière est compilée sans cette distinction.
  
    Nous avons déjà vu ces exemples. Ils renvoient [TextHandlers](#texthandlers) parce qu’ils utilisent `re` :
    ```pycon
    >>> page.css('.price::text').re(r'[\d.]+')
    ['10.99', '20.99', '15.99']
    >>> page.css('.product h3::text').re(r'Product (\d+)')
    ['1', '2', '3']
    ```
    Pour montrer les autres arguments, nous utiliserons une chaîne différente dans chaque exemple :
    ```python
    >>> from scrapling import TextHandler
    >>> test_string = TextHandler('hi  there')  # Hence the two spaces
    >>> test_string.re('hi there')
    >>> test_string.re('hi there', clean_match=True)  # Using `clean_match` will clean the string before matching the regex
    ['hi there']
    
    >>> test_string2 = TextHandler('Oh, Hi Mark')
    >>> test_string2.re_first('oh, hi Mark')
    >>> test_string2.re_first('oh, hi Mark', case_sensitive=False)  # Hence disabling `case_sensitive`
    'Oh, Hi Mark'
    
    # Mixing arguments
    >>> test_string.re('hi there', clean_match=True, case_sensitive=False)
    ['hi there']
    ```
    Utiliser `TextHandler` partout a un autre avantage : comme `html_content` renvoie un `TextHandler`, vous pouvez appliquer des expressions régulières directement au HTML :
    ```python
    >>> page.html_content.re('div class=".*">(.*)</div')
    ['In stock: 5', 'In stock: 3', 'Out of stock']
    ```

- `.json()` tente de convertir rapidement le contenu en objet JSON. Si ce n’est pas possible, il produit une erreur :
  ```python
  >>> page.css('#page-data::text').get()
    '\n      {\n        "lastUpdated": "2024-09-22T10:30:00Z",\n        "totalProducts": 3\n      }\n    '
  >>> page.css('#page-data::text').get().json()
    {'lastUpdated': '2024-09-22T10:30:00Z', 'totalProducts': 3}
  ```
  Si vous n’indiquez pas de nœud de texte ou d’attribut lors de la sélection, le contenu textuel de l’élément est utilisé automatiquement :
  ```python
  >>> page.css('#page-data')[0].json()
  {'lastUpdated': '2024-09-22T10:30:00Z', 'totalProducts': 3}
  ```
  La classe [Selector](#selector) ajoute un détail. Supposons que nous travaillions sur cette page :
  ```html
  <html>
      <body>
          <div>
            <script id="page-data" type="application/json">
              {
                "lastUpdated": "2024-09-22T10:30:00Z",
                "totalProducts": 3
              }
            </script>
          </div>
      </body>
  </html>
  ```
  [Selector](#selector) possède la méthode `get_all_text`, qui renvoie un `TextHandler`.<br/><br/>
  Si vous faites ceci :
  ```python
  >>> page.css('div::text').get().json()
  ```
  Vous obtenez une erreur, car le `div` n’a pas de texte direct à convertir en JSON. Il n’a même aucun texte direct.<br/><br/>
  Dans ce cas, utilisez `get_all_text` :
  ```python
  >>> page.css('div')[0].get_all_text(ignore_tags=[]).json()
    {'lastUpdated': '2024-09-22T10:30:00Z', 'totalProducts': 3}
  ```
  J’ai utilisé `ignore_tags` parce que sa valeur par défaut est `('script', 'style',)`.<br/><br/>
  Un autre cas lié se présente avec un fetcher. Supposons que vous receviez cette réponse JSON :
  ```python
  >>> page = Selector("""{"some_key": "some_value"}""")
  ```
  Comme [Selector](#selector) est conçu pour les pages HTML, il traite ce contenu comme du HTML incomplet et le corrige. Avec `html_content`, vous obtenez ceci :
  ```python
  >>> page.html_content
  '<html><body><p>{"some_key": "some_value"}</p></body></html>'
  ```
  Ici, vous pouvez utiliser `json` directement :
  ```python
  >>> page.json()
  {'some_key': 'some_value'}
  ```
  Vous vous demandez peut-être comment cela fonctionne puisque `html` n’a pas de texte direct.<br/>
  Pour les réponses telles que JSON, [Selector](#selector) conserve une copie du contenu brut. Quand vous appelez `.json()`, il essaie d’abord de convertir cette copie. Si elle n’existe pas, comme pour les éléments internes, il utilise le texte direct de l’élément. S’il n’y en a pas non plus, il appelle `get_all_text`.<br/>

- `.clean()` supprime les caractères d’espacement et les espaces consécutifs, puis renvoie un nouveau `TextHandler` :
```python
>>> TextHandler('\n wonderful  idea, \reh?').clean()
'wonderful idea, eh?'
```
Vous pouvez aussi passer `remove_entities` pour que `clean` remplace les entités HTML par les caractères correspondants.

- `.sort()` trie les caractères d’une chaîne, comme pour une liste :
```python
>>> TextHandler('acb').sort()
'abc'
```
Ou dans l’ordre inverse :
```python
>>> TextHandler('acb').sort(reverse=True)
'cba'
```

D’autres méthodes et propriétés seront ajoutées au fil du temps. Retenez que cette classe remplace les chaînes ordinaires dans presque toute la bibliothèque.

## TextHandlers {#texthandlers}
Cette classe suit une idée similaire à [Selectors](#selectors) et [Selector](#selector). Elle hérite des opérations des listes ordinaires et ajoute `re` et `re_first`.

Ici, `re_first` exécute `re` sur chaque [TextHandler](#texthandler) et renvoie le premier résultat, ou `None`. Le reste fonctionne comme nous l’avons vu. D’autres méthodes seront ajoutées avec le temps.

## AttributesHandler {#attributeshandler}
C’est une version en lecture seule du dictionnaire `dict` de Python. Elle stocke les attributs de chaque élément ou objet [Selector](#selector).
```python
>>> print(page.find('script').attrib)
{'id': 'page-data', 'type': 'application/json'}
>>> type(page.find('script').attrib).__name__
'AttributesHandler'
```
La lecture seule permet d’utiliser moins de ressources qu’un dictionnaire ordinaire. Les méthodes et propriétés restent les mêmes, sauf celles qui modifient les données.

Deux fonctions simples sont ajoutées :

- La méthode `search_values` :

    Dans un dictionnaire, vous pouvez utiliser `dict.get("key_name")` pour rechercher une clé. Rechercher les valeurs demande plus de code. Cette méthode le fait pour vous : elle recherche dans les valeurs des attributs et renvoie un dictionnaire pour chaque correspondance.
    
    Un exemple simple :
    ```python
    >>> for i in page.find('script').attrib.search_values('page-data'):
            print(i)
    {'id': 'page-data'}
    ```
    Elle accepte aussi `partial` pour rechercher une partie de la valeur :
    ```python
    >>> for i in page.find('script').attrib.search_values('page', partial=True):
            print(i)
    {'id': 'page-data'}
    ```
    Un cas plus courant serait de la combiner avec `find_all` pour trouver les éléments ayant une valeur précise dans leurs attributs :
    ```python
    >>> page.find_all(lambda element: list(element.attrib.search_values('product')))
    [<data='<article class="product" data-id="1"><h3...' parent='<div class="product-list"> <article clas...'>,
     <data='<article class="product" data-id="2"><h3...' parent='<div class="product-list"> <article clas...'>,
     <data='<article class="product" data-id="3"><h3...' parent='<div class="product-list"> <article clas...'>]
    ```
    Tous ces éléments ont 'product' comme valeur de `class`.
    
    J’ai utilisé `list` parce que `search_values` renvoie un générateur. Sans conversion en liste, la condition vaudrait `True` pour tous les éléments.

- La propriété `json_string` :

    Elle convertit les attributs en chaîne JSON. Si la conversion est impossible, elle produit une erreur.
  
    ```python
    >>>page.find('script').attrib.json_string
    b'{"id":"page-data","type":"application/json"}'
    ```