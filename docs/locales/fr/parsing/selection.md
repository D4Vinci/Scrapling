---
title: "Extrayez des données HTML avec CSS, XPath, le texte et les regex"
description: "Sélectionnez des éléments HTML avec CSS, XPath, le texte et les regex. Trouvez des éléments similaires et extrayez des données avec des exemples Scrapling."
---

# Rechercher des éléments {#querying-elements}
La classe `Selector` analyse du HTML. Ce choix vient du fait que la fonction adaptative ne fonctionne pas avec XML. Pour les flux XML, RSS ou Atom, utilisez [XMLFeedSpider](../spiders/generic-templates.md#xmlfeedspider), qui utilise un parser XML et vous fournit directement chaque nœud du flux.

Scrapling propose cinq grandes façons de rechercher des éléments :

1. Les sélecteurs CSS3.
2. Les sélecteurs XPath.
3. Les filtres ou conditions.
4. Un texte précis dans le contenu.
5. Une expression régulière qui correspond au contenu.

Il existe d’autres façons indirectes de trouver des éléments, mais nous allons détailler les principales. Nous verrons aussi une fonction utile : trouver des éléments similaires à un élément déjà connu. Vous pouvez aller directement à [cette section](#finding-similar-elements).

Si vous débutez en web scraping, avez peu d’expérience avec les sélecteurs et voulez commencer rapidement, je vous conseille les méthodes `find`/`find_all` [ici](#filters-based-searching).

## Sélecteurs CSS et XPath {#cssxpath-selectors}

### Que sont les sélecteurs CSS ? {#what-are-css-selectors}
[CSS](https://en.wikipedia.org/wiki/CSS) est un langage qui applique des styles aux documents HTML. Ses sélecteurs indiquent quels éléments reçoivent chaque style.

Scrapling prend en charge les sélecteurs CSS3 selon la [spécification du W3C](http://www.w3.org/TR/2011/REC-css3-selectors-20110929/). Il utilise `cssselect` pour cela. Consultez les [sélecteurs pris en charge par cssselect](https://cssselect.readthedocs.io/en/latest/#supported-selectors), y compris les pseudo-fonctions et pseudo-éléments.

Scrapling ajoute aussi quelques pseudo-éléments non standard :

* Pour sélectionner des nœuds de texte, utilisez ``::text``.
* Pour sélectionner la valeur d’un attribut, utilisez ``::attr(name)``, où name est le nom de l’attribut.

Si vous connaissez Scrapy ou Parsel, vous retrouverez la même logique. Pas besoin d’apprendre une nouvelle façon d’utiliser les sélecteurs :)

Pour sélectionner avec CSS, utilisez `css`, qui renvoie `Selectors`. Utilisez `[0]` pour obtenir le premier élément, ou `.get()` / `.getall()` pour extraire les valeurs des pseudo-sélecteurs de texte et d’attributs.

### Que sont les sélecteurs XPath ? {#what-are-xpath-selectors}
[XPath](https://en.wikipedia.org/wiki/XPath) est un langage de sélection de nœuds dans les documents XML, qui fonctionne aussi avec HTML. Cet [aide-mémoire](https://devhints.io/xpath) est utile pour apprendre [XPath](https://en.wikipedia.org/wiki/XPath). Scrapling propose XPath directement grâce à [lxml](https://lxml.de/).

Comme pour CSS, les utilisateurs de Scrapy ou Parsel retrouveront la même logique. Scrapling n’inclut toutefois pas la fonction XPath `has-class`. Il propose à la place la méthode `has_class` pour vérifier les classes des éléments trouvés.

Pour sélectionner avec XPath, utilisez `xpath`. Cette méthode suit la même logique que la méthode CSS ci-dessus.

> Les méthodes `css` et `xpath` ont d’autres arguments liés à la fonction adaptative. Nous les expliquerons dans la page consacrée à cette fonction.

### Exemples de sélecteurs {#selectors-examples}
Voici quelques exemples équivalents avec CSS et XPath.

Sélectionnez tous les éléments de classe `product` :
```python
products = page.css('.product')
products = page.xpath('//*[@class="product"]')
```
!!! info "Note"

    Le XPath ne sera pas précis si l’élément a une autre classe. **Il vaut mieux utiliser CSS pour sélectionner par classe.**

Sélectionnez le premier élément de classe `product` :
```python
product = page.css('.product')[0]
product = page.xpath('//*[@class="product"]')[0]
```
Obtenez le texte du premier élément portant la balise `h1` :
```python
title = page.css('h1::text').get()
title = page.xpath('//h1//text()').get()
```
Cela revient à faire ceci :
```python
title = page.css('h1')[0].text
title = page.xpath('//h1')[0].text
```
Obtenez l’attribut `href` du premier élément portant la balise `a` :
```python
link = page.css('a::attr(href)').get()
link = page.xpath('//a/@href').get()
```
Sélectionnez le texte du premier `h1` qui contient `Phone` et se trouve dans un élément de classe `product` :
```python
title = page.css('.product h1:contains("Phone")::text').get()
title = page.xpath('//*[@class="product"]//h1[contains(text(),"Phone")]/text()').get()
```
Vous pouvez imbriquer et enchaîner les sélecteurs tant qu’ils renvoient des résultats :
```python
page.css('.product')[0].css('h1:contains("Phone")::text').get()
page.xpath('//*[@class="product"]')[0].xpath('.//h1[contains(text(),"Phone")]/text()').get()
page.xpath('//*[@class="product"]')[0].css('h1:contains("Phone")::text').get()
```
Utilisez `.//` pour que XPath recherche à partir de l’élément actuel. Si le sélecteur commence par `//`, il recherche dans tout le document, même après la sélection d’un produit.

Autre exemple :

Tous les liens contenant 'image' dans leur attribut 'href' :
```python
links = page.css('a[href*="image"]')
links = page.xpath('//a[contains(@href, "image")]')
for index, link in enumerate(links):
    link_value = link.attrib['href']  # Cleaner than link.css('::attr(href)').get()
    link_text = link.text
    print(f'Link number {index} points to this url {link_value} with text content as "{link_text}"')
```

## Sélection par contenu textuel {#text-content-selection}
Scrapling permet de rechercher dans le texte direct de chaque élément de deux façons :

1. Avec `find_by_text`, recherchez les éléments dont le texte direct contient le texte donné. La méthode propose plusieurs options.
2. Avec `find_by_regex`, recherchez les éléments dont le texte direct correspond à une expression régulière. Cette méthode propose aussi plusieurs options.

Si vous maîtrisez les expressions régulières, vous pouvez faire avec `find_by_regex` ce que fait `find_by_text`. Nous proposons les deux méthodes pour faciliter leur utilisation par tous.

Le premier argument de `find_by_text` est le texte recherché. Celui de `find_by_regex` est l’expression régulière. Les deux méthodes partagent ces arguments :

* **first_match** : si sa valeur est `True`, la valeur par défaut, renvoie uniquement le premier résultat.
* **case_sensitive** : si sa valeur est `True`, distingue les majuscules des minuscules.
* **clean_match** : si sa valeur est `True`, remplace les caractères d’espacement et les espaces consécutifs par une seule espace avant la comparaison.

Par défaut, `find_by_text` recherche une correspondance exacte. Le texte de l’élément doit contenir UNIQUEMENT le texte donné. Pour changer ce comportement, utilisez cet argument supplémentaire :

* **partial** : si activé, `find_by_text` renvoie les éléments contenant le texte donné, même s’ils contiennent aussi autre chose.

!!! abstract "Note"

    `find_by_regex` accepte une chaîne ordinaire ou une expression régulière compilée comme premier argument. Nous le verrons dans les exemples.

### Rechercher des éléments similaires {#finding-similar-elements}
L’une des fonctions les plus utiles de Scrapling consiste à rechercher des éléments similaires à un élément déjà trouvé. Elle s’inspire d’AutoScraper, mais fonctionne ici avec les éléments obtenus par n’importe quelle méthode. Elle sert souvent après une recherche par texte, comme dans AutoScraper, d’où sa présentation dans cette section.

Comment fonctionne-t-elle ?

Supposons que vous trouviez un produit par son titre et souhaitiez extraire les autres produits du même tableau ou conteneur. Appelez `.find_similar()` sur cet élément. Scrapling effectue alors ces opérations :

1. Recherche tous les éléments situés à la même profondeur dans l’arbre DOM.
2. Écarte ceux dont le nom de balise, le nom de balise du parent ou celui du grand-parent diffère.
3. Les éléments restants sont très probablement ceux recherchés. Pour finir, Scrapling compare leurs attributs et écarte ceux qui ne ressemblent pas assez à l’élément de départ. Vous pouvez régler le pourcentage de ressemblance, mais je conseille de garder la valeur par défaut tant qu’elle trouve les éléments souhaités.

Cela fait plusieurs étapes, mais elles aident à comprendre la méthode. Nous verrons des exemples dans la section suivante. Voici les arguments disponibles :

* **similarity_threshold** : règle la comparaison des attributs à l’étape 3. La valeur par défaut est 0,2 : les attributs doivent être au moins 20 % similaires. La valeur 0 désactive cette vérification. Avant de la changer, regardez ce que font les autres arguments.
* **ignore_attributes** : noms des attributs ignorés dans la dernière comparaison. La valeur par défaut est `('href', 'src',)`, car les URL peuvent beaucoup varier entre les éléments et ne sont pas une référence fiable.
* **match_text** : si sa valeur est `True`, le texte de l’élément entre aussi dans la comparaison de l’étape 3. Ce n’est généralement pas nécessaire, mais cela dépend du cas.

Passons aux exemples.

### Exemples {#examples}
Voici des exemples de recherche par texte et par expression régulière.

J’utiliserai la classe `Fetcher`, qui sera expliquée en détail plus loin.
```python
from scrapling.fetchers import Fetcher
page = Fetcher.get('https://books.toscrape.com/index.html')
```
Trouvez le premier élément dont le texte correspond exactement au texte donné :
```python
>>> page.find_by_text('Tipping the Velvet')
<data='<a href="catalogue/tipping-the-velvet_99...' parent='<h3><a href="catalogue/tipping-the-velve...'>
```
Combinez avec `page.urljoin` pour convertir le `href` relatif en URL complète :
```python
>>> page.find_by_text('Tipping the Velvet').attrib['href']
'catalogue/tipping-the-velvet_999/index.html'
>>> page.urljoin(page.find_by_text('Tipping the Velvet').attrib['href'])
'https://books.toscrape.com/catalogue/tipping-the-velvet_999/index.html'
```
Obtenez toutes les correspondances s’il y en a plusieurs. Le résultat est une liste :
```python
>>> page.find_by_text('Tipping the Velvet', first_match=False)
[<data='<a href="catalogue/tipping-the-velvet_99...' parent='<h3><a href="catalogue/tipping-the-velve...'>]
```
Obtenez tous les éléments contenant le mot `the`, avec une correspondance partielle :
```python
>>> results = page.find_by_text('the', partial=True, first_match=False)
>>> [i.text for i in results]
['A Light in the ...',
 'Tipping the Velvet',
 'The Requiem Red',
 'The Dirty Little Secrets ...',
 'The Coming Woman: A ...',
 'The Boys in the ...',
 'The Black Maria',
 'Mesaerion: The Best Science ...',
 "It's Only the Himalayas"]
```
La recherche ne distingue pas les majuscules des minuscules. Elle inclut donc `The` en plus de `the`. Limitons les résultats à `the` :
```python
>>> results = page.find_by_text('the', partial=True, first_match=False, case_sensitive=True)
>>> [i.text for i in results]
['A Light in the ...',
 'Tipping the Velvet',
 'The Boys in the ...',
 "It's Only the Himalayas"]
```
Obtenez le premier élément dont le texte correspond à cette expression régulière de prix :
```python
>>> page.find_by_regex(r'£[\d\.]+')
<data='<p class="price_color">£51.77</p>' parent='<div class="product_price"> <p class="pr...'>
>>> page.find_by_regex(r'£[\d\.]+').text
'£51.77'
```
Vous pouvez aussi passer une expression régulière compilée. Scrapling détecte le type fourni et l’utilise :
```python
>>> import re
>>> regex = re.compile(r'£[\d\.]+')
>>> page.find_by_regex(regex)
<data='<p class="price_color">£51.77</p>' parent='<div class="product_price"> <p class="pr...'>
>>> page.find_by_regex(regex).text
'£51.77'
```
Obtenez tous les éléments correspondant à l’expression régulière :
```python
>>> page.find_by_regex(r'£[\d\.]+', first_match=False)
[<data='<p class="price_color">£51.77</p>' parent='<div class="product_price"> <p class="pr...'>,
 <data='<p class="price_color">£53.74</p>' parent='<div class="product_price"> <p class="pr...'>,
 <data='<p class="price_color">£50.10</p>' parent='<div class="product_price"> <p class="pr...'>,
 <data='<p class="price_color">£47.82</p>' parent='<div class="product_price"> <p class="pr...'>,
 ...]
```
Et ainsi de suite...

Trouvez les éléments similaires à l’élément actuel par leur position et leurs attributs. Dans ce cas, ignorez l’attribut 'title' lors de la comparaison :
```python
>>> element = page.find_by_text('Tipping the Velvet')
>>> element.find_similar(ignore_attributes=['title'])
[<data='<a href="catalogue/a-light-in-the-attic_...' parent='<h3><a href="catalogue/a-light-in-the-at...'>,
 <data='<a href="catalogue/soumission_998/index....' parent='<h3><a href="catalogue/soumission_998/in...'>,
 <data='<a href="catalogue/sharp-objects_997/ind...' parent='<h3><a href="catalogue/sharp-objects_997...'>,
...]
```
Il y a 19 éléments, pas 20, car l’élément actuel n’est pas inclus dans les résultats.
```python
>>> len(element.find_similar(ignore_attributes=['title']))
19
```
Obtenez l’attribut `href` de tous les éléments similaires :
```python
>>> [
    element.attrib['href']
    for element in element.find_similar(ignore_attributes=['title'])
]
['catalogue/a-light-in-the-attic_1000/index.html',
 'catalogue/soumission_998/index.html',
 'catalogue/sharp-objects_997/index.html',
 ...]
```
Voici un exemple un peu plus complet : extraire toutes les données des livres en partant de cet élément.
```python
>>> first_product = element.parent.parent
>>> for product in [first_product, *first_product.find_similar()]:
        print({
            "name": product.css('h3 a::text').get(),
            "price": product.css('.price_color')[0].re_first(r'[\d\.]+'),
            "stock": product.css('.availability::text').getall()[-1].clean()
        })
{'name': 'Tipping the Velvet', 'price': '53.74', 'stock': 'In stock'}
{'name': 'A Light in the ...', 'price': '51.77', 'stock': 'In stock'}
{'name': 'Soumission', 'price': '50.10', 'stock': 'In stock'}
{'name': 'Sharp Objects', 'price': '47.82', 'stock': 'In stock'}
...
```
### Exemples avancés {#advanced-examples}
Voyons des cas plus complets d’utilisation de `find_similar`.

Extraire les produits d’une boutique :
```python
def extract_product_grid(page):
    # Find the first product card
    first_product = page.find_by_text('Add to Cart').find_ancestor(
        lambda e: e.has_class('product-card')
    )

    # Find similar product cards
    products = [first_product, *first_product.find_similar()]

    return [
        {
            'name': p.css('h3::text').get(),
            'price': p.css('.price::text').re_first(r'\d+\.\d{2}'),
            'stock': 'In stock' in p.get_all_text(),
            'rating': p.css('.rating')[0].attrib.get('data-rating')
        }
        for p in products
    ]
```
Extraire les lignes d’un tableau :
```python
def extract_table_data(page):
    # Find the first data row
    first_row = page.css('table tbody tr')[0]

    # Find similar rows
    rows = [first_row, *first_row.find_similar()]

    return [
        {
            'column1': row.css('td:nth-child(1)::text').get(),
            'column2': row.css('td:nth-child(2)::text').get(),
            'column3': row.css('td:nth-child(3)::text').get()
        }
        for row in rows
    ]
```
Extraire les champs d’un formulaire :
```python
def extract_form_fields(page):
    # Find first form field container
    first_field = page.css('input')[0].find_ancestor(
        lambda e: e.has_class('form-field')
    )

    # Find similar field containers
    fields = [first_field, *first_field.find_similar()]

    return [
        {
            'label': f.css('label::text').get(),
            'type': f.css('input')[0].attrib.get('type'),
            'required': 'required' in f.css('input')[0].attrib
        }
        for f in fields
    ]
```
Extraire les avis d’un site :
```python
def extract_reviews(page):
    # Find first review
    first_review = page.find_by_text('Great product!')
    review_container = first_review.find_ancestor(
        lambda e: e.has_class('review')
    )
    
    # Find similar reviews
    all_reviews = [review_container, *review_container.find_similar()]
    
    return [
        {
            'text': r.css('.review-text::text').get(),
            'rating': r.attrib.get('data-rating'),
            'author': r.css('.reviewer::text').get()
        }
        for r in all_reviews
    ]
```
## Recherche par filtres {#filters-based-searching}
Cette méthode est l’une des meilleures façons de rechercher des éléments dans Scrapling. Elle est puissante et généralement plus facile à apprendre que les sélecteurs pour les débutants en web scraping.

Inspirées de `find_all` de BeautifulSoup, les méthodes `find_all` et `find` acceptent plusieurs filtres et recherchent les éléments qui remplissent toutes les conditions.

Chaque type d’argument est interprété ainsi :

* Une chaîne est un nom de balise.
* Un itérable, comme List, Tuple ou Set, contient des noms de balises.
* Un dictionnaire associe des noms d’attributs HTML à leurs valeurs.
* Une expression régulière filtre le contenu, comme `find_by_regex`.
* Une fonction filtre les éléments.
* Un argument nommé représente un attribut HTML et sa valeur.

La méthode rassemble tous les arguments et applique les filtres à la suite. Chaque filtre reçoit les résultats du précédent.

Les filtres s’appliquent aux éléments de la page ou de l’élément actuel dans cet ordre :

1. Recherche les éléments portant les noms de balises indiqués.
2. Recherche ceux qui correspondent à tous les attributs indiqués. Si un filtre a déjà été appliqué, seuls ses résultats sont examinés.
3. Recherche ceux qui correspondent à toutes les expressions régulières. Si des filtres ont déjà été appliqués, seuls leurs résultats sont examinés.
4. Recherche ceux qui remplissent toutes les conditions des fonctions. Si des filtres ont déjà été appliqués, seuls leurs résultats sont examinés.

!!! note "Notes"

    1. Le processus commence par le premier filtre disponible dans l’ordre ci-dessus. Sans noms de balises, mais avec des attributs, il commence à l’étape 2.
    2. L’ordre dans lequel vous passez les arguments ne compte pas. Seul l’ordre expliqué ci-dessus est utilisé.

Les exemples permettent d’y voir plus clair :)

### Exemples {#examples_1}
```python
from scrapling.fetchers import Fetcher
page = Fetcher.get('https://quotes.toscrape.com/')
```
Trouvez tous les éléments portant la balise `div` :
```python
>>> page.find_all('div')
[<data='<div class="container"> <div class="row...' parent='<body> <div class="container"> <div clas...'>,
 <data='<div class="row header-box"> <div class=...' parent='<div class="container"> <div class="row...'>,
...]
```
Trouvez tous les div dont la classe est `quote` :
```python
>>> page.find_all('div', class_='quote')
[<data='<div class="quote" itemscope itemtype="h...' parent='<div class="col-md-8"> <div class="quote...'>,
 <data='<div class="quote" itemscope itemtype="h...' parent='<div class="col-md-8"> <div class="quote...'>,
...]
```
La même chose que précédemment :
```python
>>> page.find_all('div', {'class': 'quote'})
[<data='<div class="quote" itemscope itemtype="h...' parent='<div class="col-md-8"> <div class="quote...'>,
 <data='<div class="quote" itemscope itemtype="h...' parent='<div class="col-md-8"> <div class="quote...'>,
...]
```
Trouvez tous les éléments dont la classe est `quote` :
```python
>>> page.find_all({'class': 'quote'})
[<data='<div class="quote" itemscope itemtype="h...' parent='<div class="col-md-8"> <div class="quote...'>,
 <data='<div class="quote" itemscope itemtype="h...' parent='<div class="col-md-8"> <div class="quote...'>,
...]
```
Trouvez tous les div dont la classe est `quote` et qui contiennent un élément `.text` avec le mot 'world' :
```python
>>> page.find_all('div', {'class': 'quote'}, lambda e: "world" in e.css('.text::text').get())
[<data='<div class="quote" itemscope itemtype="h...' parent='<div class="col-md-8"> <div class="quote...'>]
```
Trouvez tous les éléments qui ont des enfants :
```python
>>> page.find_all(lambda element: len(element.children) > 0)
[<data='<html lang="en"><head><meta charset="UTF...'>,
 <data='<head><meta charset="UTF-8"><title>Quote...' parent='<html lang="en"><head><meta charset="UTF...'>,
 <data='<body> <div class="container"> <div clas...' parent='<html lang="en"><head><meta charset="UTF...'>,
...]
```
Trouvez tous les éléments dont le texte contient le mot 'world' :
```python
>>> page.find_all(lambda element: "world" in element.text)
[<data='<span class="text" itemprop="text">“The...' parent='<div class="quote" itemscope itemtype="h...'>,
 <data='<a class="tag" href="/tag/world/page/1/"...' parent='<div class="tags"> Tags: <meta class="ke...'>]
```
Trouvez tous les span correspondant à l’expression régulière :
```python
>>> page.find_all('span', re.compile(r'world'))
[<data='<span class="text" itemprop="text">“The...' parent='<div class="quote" itemscope itemtype="h...'>]
```
Trouvez les div et span de classe 'quote'. Aucun span ne correspond, donc seuls des div sont renvoyés :
```python
>>> page.find_all(['div', 'span'], {'class': 'quote'})
[<data='<div class="quote" itemscope itemtype="h...' parent='<div class="col-md-8"> <div class="quote...'>,
 <data='<div class="quote" itemscope itemtype="h...' parent='<div class="col-md-8"> <div class="quote...'>,
...]
```
Combinez plusieurs filtres :
```python
>>> page.find_all({'itemtype':"http://schema.org/CreativeWork"}, 'div').css('.author::text').getall()
['Albert Einstein',
 'J.K. Rowling',
...]
```
Une astuce supplémentaire : trouvez les éléments dont l’attribut `href` se termine par 'Einstein' :
```python
>>> page.find_all({'href$': 'Einstein'})
[<data='<a href="/author/Albert-Einstein">(about...' parent='<span>by <small class="author" itemprop=...'>,
 <data='<a href="/author/Albert-Einstein">(about...' parent='<span>by <small class="author" itemprop=...'>,
 <data='<a href="/author/Albert-Einstein">(about...' parent='<span>by <small class="author" itemprop=...'>]
```
Autre astuce : trouvez les éléments dont l’attribut `href` contient '/author/' :
```python
>>> page.find_all({'href*': '/author/'})
[<data='<a href="/author/Albert-Einstein">(about...' parent='<span>by <small class="author" itemprop=...'>,
 <data='<a href="/author/J-K-Rowling">(about)</a...' parent='<span>by <small class="author" itemprop=...'>,
 <data='<a href="/author/Albert-Einstein">(about...' parent='<span>by <small class="author" itemprop=...'>,
...]
```
Et ainsi de suite...

## Générer des sélecteurs {#generating-selectors}
Vous pouvez générer des sélecteurs CSS et XPath pour tout élément, puis les réutiliser ici ou ailleurs. Peu importe la méthode utilisée pour trouver l’élément.

Générez un sélecteur CSS court pour `url_element`. Si ce n’est pas possible, générez un sélecteur complet :
```python
>>> url_element = page.find({'href*': '/author/'})
>>> url_element.generate_css_selector
'body > div > div:nth-of-type(2) > div > div > span:nth-of-type(2) > a'
```
Générez un sélecteur CSS complet pour `url_element`, depuis le début de la page :
```python
>>> url_element.generate_full_css_selector
'body > div > div:nth-of-type(2) > div > div > span:nth-of-type(2) > a'
```
Générez un sélecteur XPath court pour `url_element`. Si ce n’est pas possible, générez un sélecteur complet :
```python
>>> url_element.generate_xpath_selector
'//body/div/div[2]/div/div/span[2]/a'
```
Générez un sélecteur XPath complet pour `url_element`, depuis le début de la page :
```python
>>> url_element.generate_full_xpath_selector
'//body/div/div[2]/div/div/span[2]/a'
```
!!! abstract "Note"

    Pour créer un sélecteur court, Scrapling cherche un élément unique comme point de départ, par exemple un élément avec un attribut `id`. Ici, il n’y en a pas. Le sélecteur court et le sélecteur complet sont donc identiques.

## Utiliser des sélecteurs avec des expressions régulières {#using-selectors-with-regular-expressions}
Comme dans `parsel`/`scrapy`, vous pouvez utiliser `re` et `re_first` pour extraire des données avec des expressions régulières. Dans Scrapling, ces méthodes existent dans presque toutes les classes, comme `Selector`/`Selectors`/`TextHandler` et `TextHandlers`. Vous pouvez donc les utiliser directement sur un élément sans sélectionner de nœud de texte au préalable.

Nous les détaillerons avec [TextHandler](main_classes.md#texthandler). Pour le moment, voici comment elles fonctionnent :
```python
>>> page.css('.price_color')[0].re_first(r'[\d\.]+')
'51.77'

>>> page.css('.price_color').re_first(r'[\d\.]+')
'51.77'

>>> page.css('.price_color').re(r'[\d\.]+')
['51.77',
 '53.74',
 '50.10',
 '47.82',
 '54.23',
...]

>>> page.css('.product_pod h3 a::attr(href)').re(r'catalogue/(.*)/index.html')
['a-light-in-the-attic_1000',
 'tipping-the-velvet_999',
 'soumission_998',
 'sharp-objects_997',
...]

>>> filtering_function = lambda e: e.parent.tag == 'h3' and e.parent.parent.has_class('product_pod')  # As above selector
>>> page.find('a', filtering_function).attrib['href'].re(r'catalogue/(.*)/index.html')
['a-light-in-the-attic_1000']

>>> page.find_by_text('Tipping the Velvet').attrib['href'].re(r'catalogue/(.*)/index.html')
['tipping-the-velvet_999']
```
Et ainsi de suite. Nous expliquerons cela plus en détail dans la prochaine page, avec la classe [TextHandler](main_classes.md#texthandler).