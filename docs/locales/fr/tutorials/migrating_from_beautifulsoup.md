---
title: "Passer de BeautifulSoup à Scrapling"
description: "Comparez les tâches courantes de sélection, de texte, d’attributs et de navigation entre BeautifulSoup et Scrapling. Découvrez les différences d’API avec des exemples pratiques."
---

# Passer de BeautifulSoup à Scrapling {#migrating-from-beautifulsoup-to-scrapling}

Si vous connaissez déjà BeautifulSoup, vous prendrez vite Scrapling en main. Il est bien plus rapide, offre les mêmes fonctions d’analyse que BS et en ajoute d’autres que BS n’a pas. Il fournit aussi des outils pour récupérer des pages web modernes et travailler avec elles. Ce guide vous aide à adapter votre code BeautifulSoup à Scrapling.

Le tableau suivant présente les tâches les plus courantes lors de l’extraction de données web. Chaque ligne montre comment réaliser une tâche avec BeautifulSoup et la méthode correspondante dans Scrapling.

Vous remarquerez que certains raccourcis de BeautifulSoup n’existent pas dans Scrapling. C’est une des raisons pour lesquelles BeautifulSoup est plus lent. L’idée est simple : si une fonction tient déjà sur une ligne courte, il n’est pas nécessaire de sacrifier les performances pour la raccourcir un peu plus :)

| Tâche | Code BeautifulSoup | Code Scrapling |
|---|---|---|
| Importer le parser | `from bs4 import BeautifulSoup`                                                                               | `from scrapling.parser import Selector`                                           |
| Analyser du HTML depuis une chaîne | `soup = BeautifulSoup(html, 'html.parser')`                                                                   | `page = Selector(html)`                                                           |
| Trouver un élément | `element = soup.find('div', class_='example')`                                                                | `element = page.find('div', class_='example')`                                    |
| Trouver plusieurs éléments | `elements = soup.find_all('div', class_='example')`                                                           | `elements = page.find_all('div', class_='example')`                               |
| Trouver un élément (exemple 2) | `element = soup.find('div', attrs={"class": "example"})`                                                      | `element = page.find('div', {"class": "example"})`                                |
| Trouver un élément (exemple 3) | `element = soup.find(re.compile("^b"))`                                                                       | `element = page.find(lambda e: re.search(r"^b", e.tag) is not None)` |
| Trouver un élément (exemple 4) | `element = soup.find(lambda e: len(list(e.children)) > 0)`                                                    | `element = page.find(lambda e: len(e.children) > 0)`                              |
| Trouver un élément (exemple 5) | `element = soup.find(["a", "b"])`                                                                             | `element = page.find(["a", "b"])`                                                 |
| Trouver un élément par son texte | `element = soup.find(text="some text")`                                                                       | `element = page.find_by_text("some text", partial=False)`                         |
| Utiliser CSS pour trouver la première correspondance | `elements = soup.select_one('div.example')`                                                                   | `elements = page.css('div.example').first`                                        |
| Utiliser CSS pour trouver toutes les correspondances | `elements = soup.select('div.example')`                                                                       | `elements = page.css('div.example')`                                              |
| Obtenir le code de la page ou de l’élément avec une mise en forme lisible | `prettified = soup.prettify()`                                                                                | `prettified = page.prettify()`                                                    |
| Obtenir le code de la page ou de l’élément sans mise en forme supplémentaire | `source = str(soup)`                                                                                          | `source = page.html_content`                                                      |
| Obtenir le nom de balise d’un élément | `name = element.name`                                                                                         | `name = element.tag`                                                              |
| Extraire le texte d’un élément | `string = element.string`                                                                                     | `string = element.text`                                                           |
| Extraire tout le texte d’un document ou sous une balise | `text = soup.get_text(strip=True)`                                                                            | `text = page.get_all_text(strip=True)`                                            |
| Accéder au dictionnaire des attributs | `attrs = element.attrs`                                                                                       | `attrs = element.attrib`                                                          |
| Extraire des attributs | `attr = element['href']`                                                                                      | `attr = element['href']`                                                          |
| Accéder à l’élément parent | `parent = element.parent`                                                                                     | `parent = element.parent`                                                         |
| Obtenir tous les ancêtres d’un élément | `parents = list(element.parents)`                                                                             | `parents = list(element.iterancestors())`                                         |
| Chercher un élément parmi les ancêtres | `target_parent = element.find_parent("a")`                                                                    | `target_parent = element.find_ancestor(lambda p: p.tag == 'a')`                   |
| Obtenir tous les éléments frères | Non disponible                                                                                                           | `siblings = element.siblings`                                                     |
| Obtenir l’élément frère suivant | `next_element = element.next_sibling`                                                                         | `next_element = element.next`                                                     |
| Chercher un élément parmi les frères | `target_sibling = element.find_next_sibling("a")`<br/>`target_sibling = element.find_previous_sibling("a")`   | `target_sibling = element.siblings.search(lambda s: s.tag == 'a')`                |
| Chercher plusieurs éléments parmi les frères | `target_sibling = element.find_next_siblings("a")`<br/>`target_sibling = element.find_previous_siblings("a")` | `target_sibling = element.siblings.filter(lambda s: s.tag == 'a')`                |
| Chercher un élément parmi les éléments suivants | `target_parent = element.find_next("a")`                                                                      | `target_parent = element.below_elements.search(lambda p: p.tag == 'a')`           |
| Chercher plusieurs éléments parmi les éléments suivants | `target_parent = element.find_all_next("a")`                                                                  | `target_parent = element.below_elements.filter(lambda p: p.tag == 'a')`           |
| Chercher un élément parmi les ancêtres | `target_parent = element.find_previous("a")` ¹                                                                | `target_parent = element.path.search(lambda p: p.tag == 'a')`                     |
| Chercher plusieurs éléments parmi les ancêtres | `target_parent = element.find_all_previous("a")` ¹                                                            | `target_parent = element.path.filter(lambda p: p.tag == 'a')`                     |
| Obtenir l’élément frère précédent | `prev_element = element.previous_sibling`                                                                     | `prev_element = element.previous`                                                 |
| Accéder aux éléments enfants | `children = list(element.children)`                                                                           | `children = element.children`                                                     |
| Obtenir tous les descendants d’un élément | `children = list(element.descendants)`                                                                        | `children = element.below_elements`                                               |
| Sélectionner les liens dans les paragraphes de classe story | `group = soup.select('p.story a')`                                                             | `group = page.css('p.story a')`              |

Une expression régulière compilée passée directement à `find()` ou `find_all()` de Scrapling cherche dans le texte des éléments, pas dans les noms de balises. Utilisez la lambda du tableau pour chercher par nom de balise, ou `page.find_by_regex(r"^b")` pour chercher directement dans le texte.

¹ **Note :** `find_previous`/`find_all_previous` de BS4 cherchent dans tous les éléments précédents selon l’ordre du document. En revanche, `path` de Scrapling ne renvoie que les ancêtres, c’est-à-dire la chaîne des éléments parents. Ce ne sont pas des équivalents exacts, mais la recherche parmi les ancêtres couvre le cas le plus courant.

**Un point important** : BeautifulSoup propose des fonctions pour modifier la page après son analyse. Scrapling se concentre sur l’extraction rapide des données, puis vous laisse en faire ce dont vous avez besoin. Les deux outils servent à extraire des données web, mais l’un d’eux se spécialise dans cette tâche :)

### Un exemple complet {#putting-it-all-together}

Cet exemple montre comment extraire tous les liens d’une page avec BeautifulSoup et Scrapling.

**Avec BeautifulSoup :**

```python
import requests
from bs4 import BeautifulSoup

url = 'https://example.com'
response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')

links = soup.find_all('a')
for link in links:
    print(link['href'])
```

**Avec Scrapling :**

```python
from scrapling import Fetcher

url = 'https://example.com'
page = Fetcher.get(url)

links = page.css('a::attr(href)').getall()
for link in links:
    print(link)
```

Comme vous le voyez, Scrapling réunit la récupération et l’analyse de la page en une seule étape. Le code devient plus simple et plus efficace.

!!! abstract "**Notes supplémentaires :**"

    - **Des parsers différents** : BeautifulSoup permet de choisir le moteur d’analyse, dont `lxml`. Scrapling utilise la bibliothèque `lxml` par défaut pour des raisons de performances.
    - **Types d’éléments** : Dans BeautifulSoup, les éléments sont des objets `Tag` ; dans Scrapling, ce sont des objets `Selector`. Les deux proposent des méthodes et propriétés similaires pour naviguer et extraire des données.
    - **Gestion des erreurs** : Les deux bibliothèques renvoient `None` lorsqu’un élément n’est pas trouvé, par exemple avec `soup.find()` ou `page.find()`. Dans Scrapling, `page.css()` renvoie une liste `Selectors` vide si rien ne correspond. Vous pouvez utiliser `page.css('.foo').first` pour obtenir la première correspondance ou `None`. Pour éviter les erreurs, vérifiez si le résultat vaut `None` ou s’il est vide avant d’accéder aux propriétés.
    - **Extraction de texte** : Scrapling offre d’autres méthodes pour traiter le texte avec `TextHandler`, comme `clean()`. Cette méthode aide à supprimer les espaces superflus, les espaces consécutifs ou les caractères indésirables. Consultez la documentation pour voir la liste complète.

La documentation décrit les fonctions de Scrapling plus en détail et donne la liste de tous les arguments acceptés par chaque méthode.

Nous espérons que ce guide facilitera votre passage de BeautifulSoup à Scrapling. Bonne extraction !
