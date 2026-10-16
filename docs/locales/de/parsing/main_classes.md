---
title: "Scrapling Selector und Selectors: Daten und Navigation"
description: "Erfahren Sie, wie Selector und Selectors HTML, Text und Attribute speichern. Lesen Sie Werte aus, lösen Sie URLs auf und wechseln Sie zwischen Eltern-, Kind- und Geschwisterelementen."
---

# Hauptklassen des Parsers {#parsing-main-classes}

!!! success "Voraussetzungen"

    - Sie haben die Seite [Elemente auswählen](../parsing/selection.md) gelesen und wissen, wie Sie Elemente in einem [Selector](../parsing/main_classes.md#selector)-Objekt finden und extrahieren.

Sie kennen nun die verschiedenen Möglichkeiten, Elemente mit Scrapling auszuwählen. Sehen wir uns jetzt die Klasse [Selector](#selector) und die anderen Objekte genauer an, um den Parser besser zu verstehen.

Die Klasse [Selector](#selector) bildet den Kern des Parsers von Scrapling. Sie analysiert HTML und wählt Elemente aus. Sie können sie auf eine dieser Arten importieren:
```python
from scrapling import Selector
from scrapling.parser import Selector
```
Danach verwenden Sie sie direkt, wie auf der Seite [Überblick](../overview.md) gezeigt:
```python
page = Selector(
    '<html>...</html>',
    url='https://example.com'
)

# Then select elements as you like
elements = page.css('.product')
```
Wenn Sie HTML übergeben oder eine Website abrufen, arbeiten Sie in Scrapling vor allem mit einem [Selector](#selector)-Objekt. Operationen wie Auswahl und Navigation geben ein [Selector](#selector)- oder [Selectors](#selectors)-Objekt zurück, wenn das Ergebnis ein oder mehrere Seitenelemente sind und kein Text oder Ähnliches.

Die gesamte Seite ist also ein [Selector](#selector)-Objekt. Ihre Elemente sind ebenfalls [Selector](#selector)-Objekte. Text, etwa der Inhalt eines Elements oder ein Attributwert, ist ein [TextHandler](#texthandler)-Objekt. Die Attribute eines Elements werden in einem [AttributesHandler](#attributeshandler) gespeichert. Auf beide kommen wir später zurück. Zuerst sehen wir uns [Selector](#selector) an.

## Selector {#selector}
### Die Argumente erklärt {#arguments-explained}
Das wichtigste Argument ist `content`. Damit übergeben Sie den HTML-Code, den Sie analysieren möchten, als `str` oder `bytes`.

Mit `url` legen Sie die Seiten-URL fest. Sie dient dazu, relative Links aufzulösen und gespeicherte adaptive Daten nach Domain zu trennen. Die Argumente `adaptive`, `storage` und `storage_args` gehören zur Funktion [adaptive](adaptive.md). Wenn Sie diese nicht nutzen, haben die Argumente keine Auswirkung.

Weitere Argumente steuern, wie der Parser den HTML-Inhalt verarbeitet oder dabei verändert:

- **encoding**: Die Zeichenkodierung, die beim Analysieren des HTML verwendet wird. Der Standardwert ist `UTF-8`.
- **keep_comments**: Legt fest, ob HTML-Kommentare beim Analysieren erhalten bleiben. Standardmäßig ist dies deaktiviert, weil Kommentare das Scraping auf verschiedene Arten stören können.

Die Argumente `huge_tree` und `root` lasse ich hier bewusst weg, damit diese Seite nicht unnötig kompliziert wird.
Das mache ich öfter bei fortgeschrittenen Funktionen, die Sie für die normale Nutzung nicht kennen müssen. Wenn Sie mehr wissen möchten, finden Sie diese Themen im Entwicklungsbereich.

Die meisten Eigenschaften der Seite und ihrer Elemente werden erst geladen, wenn Sie sie verwenden. Das gilt zum Beispiel für den Textinhalt. Auch deshalb ist Scrapling so schnell :)

### Eigenschaften {#properties}
Vieles davon kennen Sie schon aus dem [Überblick](../overview.md). Falls nicht, ist das kein Problem. Wir gehen es hier mit weiteren Methoden und Beispielen durch. Die Eigenschaften zur Navigation stehen getrennt im Abschnitt [Navigation](#traversal).

Für die Beispiele verwenden wir diese HTML-Seite:
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
Laden Sie die Seite direkt wie zuvor:
```python
from scrapling import Selector
page = Selector(html_doc)
```
Lesen Sie den gesamten Text der Seite einschließlich aller untergeordneten Elemente aus:
```python
>>> page.get_all_text()
'Some page\n\n    \n\n      \nProduct 1\nThis is product 1\n$10.99\nIn stock: 5\nProduct 2\nThis is product 2\n$20.99\nIn stock: 3\nProduct 3\nThis is product 3\n$15.99\nOut of stock'
```
Wählen Sie wie zuvor den ersten Artikel aus. Er dient uns als Beispiel:
```python
article = page.find('article')
```
Auf dieselbe Weise lesen Sie den gesamten Text des Elements und seiner untergeordneten Elemente aus:
```python
>>> article.get_all_text()
'Product 1\nThis is product 1\n$10.99\nIn stock: 5'
```
Der direkte Textinhalt ist dagegen leer, weil das Element im HTML oben keinen eigenen Text enthält:
```python
>>> article.text
''
```
Die Methode `get_all_text` hat folgende optionale Argumente:

1. **separator**: Verbindet alle gesammelten Zeichenketten mit diesem Trennzeichen. Der Standardwert ist '\n'.
2. **strip**: Entfernt vor dem Verbinden Leerraum am Anfang und Ende der Zeichenketten. Standardmäßig deaktiviert.
3. **ignore_tags**: Ein Tupel mit den Tag-Namen, die in den Ergebnissen fehlen sollen. Auch darin verschachtelte Elemente werden ignoriert. Der Standardwert ist `('script', 'style',)`.
4. **valid_values**: Sammelt nur Elemente mit Inhalt. Elemente mit leerem Text oder nur Leerraum werden ignoriert. Standardmäßig aktiviert.

Der zurückgegebene Text ist übrigens keine normale Zeichenkette, sondern ein [TextHandler](#texthandler). Dazu später mehr. Wenn der Text JSON enthält, können Sie `.json()` darauf aufrufen:
```python
>>> script = page.find('script')
>>> script.json()
{'lastUpdated': '2024-09-22T10:30:00Z', 'totalProducts': 3}
```
Lesen Sie jetzt den Tag-Namen des Elements aus:
```python
>>> article.tag
'article'
```
Wenn Sie dies direkt auf die Seite anwenden, arbeiten Sie mit dem Wurzelelement `html`:
```python
>>> page.tag
'html'
```
Damit sollte der Zusammenhang zwischen `page` und `element` klar sein. Darauf komme ich nicht noch einmal zurück.

Lesen Sie die Attribute des Elements aus:
```python
>>> print(article.attrib)
{'class': 'product', 'data-id': '1'}
```
Greifen Sie auf ein bestimmtes Attribut zu:
```python
article.attrib['class']
article.attrib.get('class')
article['class']  # new in v0.3
```
Prüfen Sie mit einer der folgenden Methoden, ob ein Attribut vorhanden ist:
```python
'class' in article.attrib
'class' in article  # new in v0.3
```
Lesen Sie den HTML-Inhalt des Elements aus:
```python
>>> article.html_content
'<article class="product" data-id="1"><h3>Product 1</h3>\n        <p class="description">This is product 1</p>\n        <span class="price">$10.99</span>\n        <div class="hidden stock">In stock: 5</div>\n      </article>'
```
Geben Sie den HTML-Inhalt des Elements in gut lesbarer Form aus:
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
Mit `.body` erhalten Sie den unverarbeiteten Seiteninhalt. Seit v0.4 gibt `.body` bei einem `Response`-Objekt eines Fetchers immer `bytes` zurück.
```python
>>> page.body
'<html>\n  <head>\n    <title>Some page</title>\n  </head>\n  ...'
```
So erhalten Sie alle Vorfahren dieses Elements im DOM-Baum:
```python
>>> article.path
[<data='<div class="product-list"> <article clas...' parent='<body> <div class="product-list"> <artic...'>,
 <data='<body> <div class="product-list"> <artic...' parent='<html><head><title>Some page</title></he...'>,
 <data='<html><head><title>Some page</title></he...'>]
```
Erzeugen Sie einen möglichst kurzen CSS-Selektor oder den vollständigen Selektor:
```python
>>> article.generate_css_selector
'body > div > article'
>>> article.generate_full_css_selector
'body > div > article'
```
Das geht auch mit XPath:
```python
>>> article.generate_xpath_selector
"//body/div/article"
>>> article.generate_full_xpath_selector
"//body/div/article"
```

### Navigation {#traversal}
Mit den oben gefundenen Elementen sehen wir uns nun die Eigenschaften und Methoden zur Navigation auf der Seite an.

Wenn Sie den DOM-Baum oder Baumstrukturen noch nicht kennen, kann dieser Abschnitt schwer verständlich sein. Ich empfehle, sich zuerst kurz über diese Begriffe zu informieren.

Falls Sie nicht suchen möchten, hier eine kurze Erklärung.<br/>
Das Element `html` ist die Wurzel des Seitenbaums. Jede Seite beginnt mit einem `html`-Element.<br/>
Direkt darunter liegen Elemente wie `head` und `body`. Sie sind die „Kinder“ von `html`, und `html` ist ihr „Elternteil“. Die Elemente `body` und `head` sind „Geschwister“, weil sie dasselbe Elternelement haben.

Greifen Sie auf das Elternelement zu:
```python
>>> article.parent
<data='<div class="product-list"> <article clas...' parent='<body> <div class="product-list"> <artic...'>
>>> article.parent.tag
'div'
```
Sie können diese Zugriffe beliebig verketten. Das gilt auch für die anderen ähnlichen Eigenschaften und Methoden in diesem Abschnitt.
```python
>>> article.parent.parent.tag
'body'
```
Lesen Sie die Kindelemente aus:
```python
>>> article.children
[<data='<h3>Product 1</h3>' parent='<article class="product" data-id="1"><h3...'>,
 <data='<p class="description">This is product 1...' parent='<article class="product" data-id="1"><h3...'>,
 <data='<span class="price">$10.99</span>' parent='<article class="product" data-id="1"><h3...'>,
 <data='<div class="hidden stock">In stock: 5</d...' parent='<article class="product" data-id="1"><h3...'>]
```
Lesen Sie alle Elemente unterhalb eines Elements aus. Das entspricht einer verschachtelten Version von `children`:
```python
>>> article.below_elements
[<data='<h3>Product 1</h3>' parent='<article class="product" data-id="1"><h3...'>,
 <data='<p class="description">This is product 1...' parent='<article class="product" data-id="1"><h3...'>,
 <data='<span class="price">$10.99</span>' parent='<article class="product" data-id="1"><h3...'>,
 <data='<div class="hidden stock">In stock: 5</d...' parent='<article class="product" data-id="1"><h3...'>]
```
Bei diesem Element ist das Ergebnis gleich wie bei `children`, weil seine Kinder keine weiteren Kinder haben.

Am Element mit der Klasse `product-list` wird der Unterschied zwischen `children` und `below_elements` deutlicher:
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
Lesen Sie die Geschwisterelemente aus:
```python
>>> article.siblings
[<data='<article class="product" data-id="2"><h3...' parent='<div class="product-list"> <article clas...'>,
 <data='<article class="product" data-id="3"><h3...' parent='<div class="product-list"> <article clas...'>]
```
Lesen Sie das nächste Geschwisterelement aus:
```python
>>> article.next
<data='<article class="product" data-id="2"><h3...' parent='<div class="product-list"> <article clas...'>
```
Für das vorherige Element gibt es `previous`:
```python
>>> article.previous  # It's the first child, so it doesn't have a previous element
>>> second_article = page.css('.product[data-id="2"]')[0]
>>> second_article.previous
<data='<article class="product" data-id="1"><h3...' parent='<div class="product-list"> <article clas...'>
```
Sie können einfach und schnell prüfen, ob ein Element einen bestimmten Klassennamen hat:
```python
>>> article.has_class('product')
True
```
Wenn Sie mehr als das direkte Elternelement brauchen, können Sie alle Vorfahren eines Elements durchlaufen:
```python
for ancestor in article.iterancestors():
    # do something with it...
```
Sie können auch einen Vorfahren suchen, der eine Bedingung erfüllt. Übergeben Sie eine Funktion, die ein [Selector](#selector)-Objekt annimmt und `True` zurückgibt, wenn die Bedingung erfüllt ist, sonst `False`:
```python
>>> article.find_ancestor(lambda ancestor: ancestor.has_class('product-list'))
<data='<div class="product-list"> <article clas...' parent='<body> <div class="product-list"> <artic...'>

>>> article.find_ancestor(lambda ancestor: ancestor.css('.product-list'))  # Same result, different approach
<data='<div class="product-list"> <article clas...' parent='<body> <div class="product-list"> <artic...'>
```
## Selectors {#selectors}
Die Klasse `Selectors` ist die Listenvariante von [Selector](#selector). Sie erbt vom Python-Standardtyp `List` und besitzt alle Eigenschaften und Methoden von `List`. Zusätzliche Methoden vereinfachen die Arbeit mit den enthaltenen [Selector](#selector)-Instanzen.

Alle Methoden und Eigenschaften von [Selector](#selector), die mehrere Elemente zurückgeben, liefern diese als [Selectors](#selectors)-Instanz.

Seit v0.4 geben alle Auswahlmethoden durchgehend [Selector](#selector)- oder [Selectors](#selectors)-Objekte zurück, auch für Textknoten und Attributwerte. Textknoten, die Sie mit `::text`, `/text()`, `::attr()` oder `/@attr` auswählen, werden in [Selector](#selector)-Objekte verpackt. Bei diesen ist `tag` auf `"#text"` gesetzt, und `text` gibt den Textwert zurück. Sie können weiterhin direkt auf den Textwert zugreifen. Alle anderen Eigenschaften liefern leere Werte oder Standardwerte.

```python
page.css('a::text')              # -> Selectors (of text node Selectors)
page.xpath('//a/text()')         # -> Selectors
page.css('a::text').get()        # -> TextHandler (the first text value)
page.css('a::text').getall()     # -> TextHandlers (all text values)
page.css('a::attr(href)')        # -> Selectors
page.xpath('//a/@href')          # -> Selectors
page.css('.price_color')         # -> Selectors
```

### Methoden zum Auslesen von Daten {#data-extraction-methods}
Seit v0.4 bieten [Selector](#selector) und [Selectors](#selectors) die Methoden `get()`, `getall()` sowie die Aliase `extract_first` und `extract`. Sie folgen damit den Konventionen von Scrapy. Die alte Methode `get_all()` wurde entfernt.

**Bei einem [Selector](#selector)-Objekt:**

- `get()` gibt einen `TextHandler` zurück. Bei Textknoten enthält er den Textwert, bei HTML-Elementen das serialisierte äußere HTML einschließlich des Elements selbst.
- `getall()` gibt eine `TextHandlers`-Liste mit dieser einen serialisierten Zeichenkette zurück.
- `extract_first` ist ein Alias für `get()`, und `extract` ist ein Alias für `getall()`.

```python
>>> page.css('h3')[0].get()        # Outer HTML of the element
'<h3>Product 1</h3>'

>>> page.css('h3::text')[0].get()  # Text value of the text node
'Product 1'
```

**Bei einem [Selectors](#selectors)-Objekt:**

- `get(default=None)` gibt die serialisierte Zeichenkette des **ersten** Elements zurück. Ist die Liste leer, wird `default` zurückgegeben.
- `getall()` serialisiert **alle** Elemente und gibt eine `TextHandlers`-Liste zurück.
- `extract_first` ist ein Alias für `get()`, und `extract` ist ein Alias für `getall()`.

```python
>>> page.css('.price::text').get()      # First price text
'$10.99'

>>> page.css('.price::text').getall()   # All price texts
['$10.99', '$20.99', '$15.99']

>>> page.css('.price::text').get('')    # With default value
'$10.99'
```

Diese Methoden funktionieren mit allen Auswahlarten wie CSS, XPath und `find`. Sie sind der empfohlene Weg, Text und Attributwerte im Stil von Scrapy auszulesen.

Sehen wir uns nun die weiteren Funktionen von [Selectors](#selectors) an.
### Eigenschaften {#properties_1}
Neben den normalen Listenoperationen wie Iteration und Slicing stehen diese Möglichkeiten bereit:

Sie können CSS- und XPath-Selektoren direkt auf die enthaltenen [Selector](#selector)-Instanzen anwenden. Die Rückgabetypen entsprechen denen der Methoden `css` und `xpath` von [Selector](#selector). Die Argumente sind ähnlich, aber `adaptive` steht hier nicht zur Verfügung. So lassen sich Methoden einfach verketten.
```pycon
>>> page.css('.product h3::text').getall()
['Product 1', 'Product 2', 'Product 3']
>>> page.css('.product').css('h3::text').getall()
['Product 1', 'Product 2', 'Product 3']
```
Auch `re` und `re_first` lassen sich direkt aufrufen. Sie nehmen dieselben Argumente an wie bei [Selector](#selector). Die Erklärung dieser Methoden folgt im Abschnitt [TextHandler](#texthandler).

In dieser Klasse verhält sich `re_first` etwas anders: Es führt `re` auf jedem enthaltenen [Selector](#selector) aus und gibt das erste gefundene Ergebnis zurück. Die Methode `re` liefert wie gewohnt ein [TextHandlers](#texthandlers)-Objekt. Darin werden alle [TextHandler](#texthandler)-Instanzen in einer [TextHandlers](#texthandlers)-Instanz zusammengeführt.
```pycon
>>> page.css('.price::text').re(r'[\d.]+')
['10.99', '20.99', '15.99']
>>> page.css('.product h3::text').re(r'Product (\d+)')
['1', '2', '3']
```
Mit `search` durchsuchen Sie die enthaltenen [Selector](#selector)-Instanzen. Die übergebene Funktion muss als erstes Argument eine [Selector](#selector)-Instanz annehmen und True oder False zurückgeben. Die Methode liefert die erste [Selector](#selector)-Instanz, die die Bedingung erfüllt, sonst `None`.

```pycon
>>> product = page.css('.product').search(lambda p: p.css('.price::text').get() == '$20.99')
>>> product.css('h3::text').get()
'Product 2'
```
Auch `filter` nimmt eine Funktion wie `search` an. Es gibt aber eine `Selectors`-Instanz mit allen passenden [Selector](#selector)-Instanzen zurück:

```pycon
>>> products = page.css('.product').filter(lambda p: float(p.css('.price::text').re_first(r'[\d.]+')) > 15)
>>> products.css('h3::text').getall()
['Product 2', 'Product 3']
```
Sie können sicher auf das erste oder letzte Element zugreifen, ohne einen Indexfehler zu riskieren:
```python
>>> page.css('.product').first   # First Selector or None
<data='<article class="product" data-id="1"><h3...'>
>>> page.css('.product').last    # Last Selector or None
<data='<article class="product" data-id="3"><h3...'>
>>> page.css('.nonexistent').first  # Returns None instead of raising IndexError
```

Wenn Sie wie ich einen kurzen Weg bevorzugen und wissen möchten, wie viele [Selector](#selector)-Instanzen eine [Selectors](#selectors)-Instanz enthält, geht das so:
```python
page.css('.product').length
```
Das entspricht:
```python
len(page.css('.product'))
```
Ja, wie in JavaScript :)

## TextHandler {#texthandler}
Diese Klasse sollten Sie kennen. Alle Methoden und Eigenschaften, die eine Zeichenkette zurückgeben, liefern einen `TextHandler`. Für Listen von Zeichenketten wird stattdessen [TextHandlers](#texthandlers) verwendet.

TextHandler erbt von der normalen Python-Zeichenkette. Sie können damit also alles tun, was mit einer Python-Zeichenkette möglich ist. Warum hat die Klasse dann einen eigenen Namen?

TextHandler bietet zusätzliche Methoden und Eigenschaften. Diese sehen wir uns jetzt an. Da die Klassen überall TextHandler statt normaler Zeichenketten zurückgeben, lassen sich diese Funktionen oft kombinieren. So wird Ihr Code kürzer und übersichtlicher. Sie können die Klasse auch direkt importieren und auf beliebige Zeichenketten anwenden. Das erklären wir [später](../development/scrapling_custom_types.md).
### Verwendung {#usage}
Alle Operationen wie Slicing und Indexzugriffe sowie Methoden wie `split`, `replace` und `strip` geben wieder einen `TextHandler` zurück. Sie können sie also beliebig verketten. Falls Sie eine Methode oder Eigenschaft finden, die statt `TextHandler` eine normale Zeichenkette zurückgibt, öffnen Sie bitte ein Issue. Dann passen wir auch diese an.

Beginnen wir mit `re` und `re_first`. Diese Methoden gibt es auch in [Selector](#selector), [Selectors](#selectors) und [TextHandlers](#texthandlers). Sie nehmen überall dieselben Argumente an.

- Die Methode `re` nimmt als erstes Argument eine Zeichenkette oder ein kompiliertes Regex-Muster an. Sie sucht alle passenden Zeichenketten und gibt sie als [TextHandlers](#texthandlers)-Instanz zurück. `re_first` nimmt dieselben Argumente an und arbeitet ähnlich, gibt aber nur den ersten Treffer als `TextHandler` zurück.
    
    Weitere hilfreiche Argumente sind:
    
    - **replace_entities**: Standardmäßig aktiviert. Ersetzt Zeichenreferenzen durch die entsprechenden Zeichen.
    - **clean_match**: Standardmäßig deaktiviert. Ignoriert bei der Suche alle Leerraumzeichen, auch aufeinanderfolgende Leerzeichen.
    - **case_sensitive**: Standardmäßig aktiviert. Wenn Sie es deaktivieren, unterscheidet die Regex beim Kompilieren nicht zwischen Groß- und Kleinschreibung.
  
    Diese Beispiele kennen Sie schon. Das Ergebnis ist ein [TextHandlers](#texthandlers)-Objekt, weil wir `re` verwenden.
    ```pycon
    >>> page.css('.price::text').re(r'[\d.]+')
    ['10.99', '20.99', '15.99']
    >>> page.css('.product h3::text').re(r'Product (\d+)')
    ['1', '2', '3']
    ```
    Um die weiteren Argumente zu zeigen, verwenden wir für jedes Beispiel eine eigene Zeichenkette:
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
    Da Zeichenketten überall durch `TextHandler` ersetzt werden, geben auch Eigenschaften wie `html_content` einen `TextHandler` zurück. Deshalb können Sie Regex direkt auf den HTML-Inhalt anwenden:
    ```python
    >>> page.html_content.re('div class=".*">(.*)</div')
    ['In stock: 5', 'In stock: 3', 'Out of stock']
    ```

- Die Methode `.json()` wandelt den Inhalt schnell in ein JSON-Objekt um, wenn dies möglich ist. Sonst löst sie einen Fehler aus:
  ```python
  >>> page.css('#page-data::text').get()
    '\n      {\n        "lastUpdated": "2024-09-22T10:30:00Z",\n        "totalProducts": 3\n      }\n    '
  >>> page.css('#page-data::text').get().json()
    {'lastUpdated': '2024-09-22T10:30:00Z', 'totalProducts': 3}
  ```
  Wenn Sie bei der Auswahl keinen Textknoten angeben, etwa den Textinhalt oder einen Attributwert, wird automatisch der Textinhalt verwendet:
  ```python
  >>> page.css('#page-data')[0].json()
  {'lastUpdated': '2024-09-22T10:30:00Z', 'totalProducts': 3}
  ```
  Die Klasse [Selector](#selector) bietet hier noch eine weitere Funktion. Angenommen, wir arbeiten mit dieser Seite:
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
  Die Methode `get_all_text` der Klasse [Selector](#selector) kennen Sie bereits. Auch sie gibt einen `TextHandler` zurück.<br/><br/>
  Wenn Sie Folgendes versuchen:
  ```python
  >>> page.css('div::text').get().json()
  ```
  erhalten Sie einen Fehler. Das `div`-Tag enthält keinen direkten Text, der sich als JSON lesen lässt. Es hat überhaupt keinen direkten Textinhalt.<br/><br/>
  Hier hilft `get_all_text`:
  ```python
  >>> page.css('div')[0].get_all_text(ignore_tags=[]).json()
    {'lastUpdated': '2024-09-22T10:30:00Z', 'totalProducts': 3}
  ```
  Ich verwende hier `ignore_tags`, weil dessen Standardwert `('script', 'style',)` ist.<br/><br/>
  Ein ähnliches Verhalten gibt es bei Fetchern, die wir später erklären. Angenommen, Sie erhalten diese JSON-Antwort:
  ```python
  >>> page = Selector("""{"some_key": "some_value"}""")
  ```
  Die Klasse [Selector](#selector) ist für HTML-Seiten optimiert. Sie behandelt die Antwort deshalb wie fehlerhaftes HTML und korrigiert sie. Bei `html_content` erhalten Sie dann Folgendes:
  ```python
  >>> page.html_content
  '<html><body><p>{"some_key": "some_value"}</p></body></html>'
  ```
  Die Methode `json` können Sie trotzdem direkt nutzen:
  ```python
  >>> page.json()
  {'some_key': 'some_value'}
  ```
  Vielleicht fragen Sie sich, warum das funktioniert, obwohl das `html`-Tag keinen direkten Text enthält.<br/>
  Für Fälle wie JSON-Antworten behält [Selector](#selector) eine unveränderte Kopie des empfangenen Inhalts. Wenn Sie `.json()` aufrufen, wird zuerst diese Kopie geprüft und als JSON gelesen. Ist keine Kopie vorhanden, etwa bei einzelnen Elementen, wird deren direkter Text geprüft. Andernfalls verwendet die Methode `get_all_text`.<br/>

- Die Methode `.clean()` entfernt Leerraumzeichen und aufeinanderfolgende Leerzeichen. Sie gibt eine neue `TextHandler`-Instanz zurück:
```python
>>> TextHandler('\n wonderful  idea, \reh?').clean()
'wonderful idea, eh?'
```
Mit `remove_entities` können Sie außerdem festlegen, dass `clean` HTML-Entitäten durch ihre entsprechenden Zeichen ersetzt.

- Die Methode `.sort()` sortiert die Zeichenkette, ähnlich wie bei Listen:
```python
>>> TextHandler('acb').sort()
'abc'
```
Das geht auch in umgekehrter Reihenfolge:
```python
>>> TextHandler('acb').sort(reverse=True)
'cba'
```

Mit der Zeit kommen weitere Methoden und Eigenschaften hinzu. Denken Sie daran, dass diese Klasse fast überall in der Bibliothek anstelle normaler Zeichenketten zurückgegeben wird.

## TextHandlers {#texthandlers}
Diese Klasse folgt demselben Prinzip wie [Selectors](#selectors) und [Selector](#selector). Sie übernimmt das Verhalten normaler Listen und ergänzt die Methoden `re` und `re_first`.

Der einzige Unterschied: `re_first` führt hier `re` auf jedem [TextHandler](#texthandler) aus und gibt den ersten Treffer oder `None` zurück. Mehr müssen Sie dazu vorerst nicht wissen. Weitere Methoden kommen später hinzu.

## AttributesHandler {#attributeshandler}
Dies ist eine schreibgeschützte Variante des normalen Python-Dictionarys, also `dict`. Sie speichert die Attribute eines Elements beziehungsweise einer [Selector](#selector)-Instanz.
```python
>>> print(page.find('script').attrib)
{'id': 'page-data', 'type': 'application/json'}
>>> type(page.find('script').attrib).__name__
'AttributesHandler'
```
Weil sie schreibgeschützt ist, benötigt sie weniger Ressourcen als ein normales Dictionary. Sie bietet dessen Methoden und Eigenschaften, außer denen, die Daten ändern oder überschreiben.

Dazu kommen zwei einfache Funktionen:

- Die Methode `search_values`

    Bei normalen Dictionarys können Sie mit `dict.get("key_name")` prüfen, ob ein Schlüssel vorhanden ist. Für eine Suche nach Werten brauchen Sie sonst zusätzlichen Code. Diese Methode übernimmt das: Sie durchsucht die Attributwerte und liefert für jeden Treffer ein Dictionary.
    
    Ein einfaches Beispiel:
    ```python
    >>> for i in page.find('script').attrib.search_values('page-data'):
            print(i)
    {'id': 'page-data'}
    ```
    Mit dem Argument `partial` können Sie auch nach einem Teil des Werts suchen:
    ```python
    >>> for i in page.find('script').attrib.search_values('page', partial=True):
            print(i)
    {'id': 'page-data'}
    ```
    Diese Beispiele sind eher theoretisch. In der Praxis könnten Sie die Methode zusammen mit `find_all` nutzen, um alle Elemente mit einem bestimmten Attributwert zu finden:
    ```python
    >>> page.find_all(lambda element: list(element.attrib.search_values('product')))
    [<data='<article class="product" data-id="1"><h3...' parent='<div class="product-list"> <article clas...'>,
     <data='<article class="product" data-id="2"><h3...' parent='<div class="product-list"> <article clas...'>,
     <data='<article class="product" data-id="3"><h3...' parent='<div class="product-list"> <article clas...'>]
    ```
    Bei all diesen Elementen hat das Attribut `class` den Wert 'product'.
    
    Hier nutze ich `list`, weil `search_values` einen Generator zurückgibt. Dieser würde sonst für jedes Element als `True` gelten.

- Die Eigenschaft `json_string`

    Diese Eigenschaft wandelt die aktuellen Attribute in eine JSON-Zeichenkette um, wenn sie sich als JSON serialisieren lassen. Sonst löst sie einen Fehler aus.
  
    ```python
    >>>page.find('script').attrib.json_string
    b'{"id":"page-data","type":"application/json"}'
    ```