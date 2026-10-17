---
title: "HTML-Daten mit CSS, XPath, Text und Regex auslesen"
description: "Wählen Sie HTML-Elemente mit CSS, XPath, Text und Regex aus. Finden Sie ähnliche Elemente und lesen Sie Daten mit den Codebeispielen von Scrapling aus."
---

# Elemente auswählen {#querying-elements}
Die Klasse `Selector` analysiert HTML. Dafür haben wir uns entschieden, weil die adaptive Funktion nicht mit XML funktioniert. Für XML-, RSS- oder Atom-Feeds nutzen Sie [XMLFeedSpider](../spiders/generic-templates.md#xmlfeedspider). Dieser verwendet einen XML-Parser und gibt Ihnen jeden Feed-Knoten direkt.

In Scrapling gibt es fünf wichtige Wege, Elemente zu finden:

1. CSS3-Selektoren
2. XPath-Selektoren
3. Suche mit Filtern oder Bedingungen
4. Suche nach Elementen mit einem bestimmten Text
5. Suche nach Elementen, deren Inhalt zu einer Regex passt

Es gibt auch andere, indirekte Wege. Hier erklären wir die wichtigsten genauer. Außerdem zeigen wir eine besonders nützliche Funktion von Scrapling: Es kann Elemente finden, die einem bereits gefundenen Element ähneln. Sie können [direkt zu diesem Abschnitt springen](#finding-similar-elements).

Wenn Sie neu im Web Scraping sind, kaum Erfahrung mit Selektoren haben und schnell anfangen möchten, empfehle ich Ihnen die Methoden `find`/`find_all`. Sie werden [hier erklärt](#filters-based-searching).

## CSS/XPath-Selektoren {#cssxpath-selectors}

### Was sind CSS-Selektoren? {#what-are-css-selectors}
[CSS](https://en.wikipedia.org/wiki/CSS) ist eine Sprache zur Gestaltung von HTML-Dokumenten. Mit Selektoren ordnet sie die Gestaltung bestimmten HTML-Elementen zu.

Scrapling unterstützt CSS3-Selektoren nach der [W3C-Spezifikation](http://www.w3.org/TR/2011/REC-css3-selectors-20110929/). Dafür nutzt es `cssselect`. Lesen Sie dort nach, welche [Selektoren](https://cssselect.readthedocs.io/en/latest/#supported-selectors), Pseudofunktionen und Pseudoelemente unterstützt werden.

Scrapling bietet außerdem einige Pseudoelemente außerhalb des Standards:

* Mit ``::text`` wählen Sie Textknoten aus.
* Mit ``::attr(name)`` wählen Sie Attributwerte aus. Dabei steht name für den Namen des Attributs, dessen Wert Sie brauchen.

Wenn Sie Scrapy oder Parsel kennen, finden Sie hier dieselbe Selektorlogik. So müssen Sie keine andere Arbeitsweise lernen :)

Mit der Methode `css` wählen Sie Elemente über CSS-Selektoren aus. Sie gibt `Selectors` zurück. Mit `[0]` erhalten Sie das erste Element. Mit `.get()` / `.getall()` lesen Sie Textwerte aus Text- oder Attribut-Pseudoselektoren aus.

### Was sind XPath-Selektoren? {#what-are-xpath-selectors}
[XPath](https://en.wikipedia.org/wiki/XPath) ist eine Sprache zur Auswahl von Knoten in XML-Dokumenten. Sie lässt sich auch mit HTML nutzen. Diese [Kurzreferenz](https://devhints.io/xpath) hilft beim Lernen von [XPath](https://en.wikipedia.org/wiki/XPath). Scrapling stellt XPath-Selektoren direkt über [lxml](https://lxml.de/) bereit.

Wie bei CSS finden Sie auch hier die bekannte Selektorlogik von Scrapy und Parsel. Scrapling bietet allerdings nicht deren XPath-Erweiterungsfunktion `has-class`. Stattdessen können Sie die Methode `has_class` für denselben Zweck auf gefundenen Elementen aufrufen.

Für XPath-Selektoren verwenden Sie die Methode `xpath`. Sie folgt derselben Logik wie die oben gezeigte CSS-Methode.

> Die Methoden `css` und `xpath` haben weitere Argumente für die adaptive Funktion. Diese erklären wir später ausführlich auf einer eigenen Seite.

### Beispiele für Selektoren {#selectors-examples}
Sehen wir uns einige Beispiele mit CSS und XPath an.

Wählen Sie alle Elemente mit der Klasse `product` aus:
```python
products = page.css('.product')
products = page.xpath('//*[@class="product"]')
```
!!! info "Hinweis:"

    Der XPath-Ausdruck funktioniert nicht genau, wenn das Element noch eine weitere Klasse hat. **Für die Auswahl nach Klasse ist CSS immer die bessere Wahl.**

Wählen Sie das erste Element mit der Klasse `product` aus:
```python
product = page.css('.product')[0]
product = page.xpath('//*[@class="product"]')[0]
```
Lesen Sie den Text des ersten Elements mit dem Tag-Namen `h1` aus:
```python
title = page.css('h1::text').get()
title = page.xpath('//h1//text()').get()
```
Das entspricht:
```python
title = page.css('h1')[0].text
title = page.xpath('//h1')[0].text
```
Lesen Sie das Attribut `href` des ersten Elements mit dem Tag-Namen `a` aus:
```python
link = page.css('a::attr(href)').get()
link = page.xpath('//a/@href').get()
```
Lesen Sie den Text des ersten `h1`-Elements aus, das `Phone` enthält und unter einem Element mit der Klasse `product` liegt:
```python
title = page.css('.product h1:contains("Phone")::text').get()
title = page.xpath('//*[@class="product"]//h1[contains(text(),"Phone")]/text()').get()
```
Sie können Selektoren beliebig verschachteln und verketten, solange sie Ergebnisse liefern:
```python
page.css('.product')[0].css('h1:contains("Phone")::text').get()
page.xpath('//*[@class="product"]')[0].xpath('.//h1[contains(text(),"Phone")]/text()').get()
page.xpath('//*[@class="product"]')[0].css('h1:contains("Phone")::text').get()
```
Mit `.//` beginnt ein XPath relativ zum aktuellen Element. Ein führendes `//` durchsucht dagegen das ganze Dokument, auch nachdem Sie ein Produkt ausgewählt haben.

Ein weiteres Beispiel:

Alle Links, deren Attribut 'href' den Text 'image' enthält:
```python
links = page.css('a[href*="image"]')
links = page.xpath('//a[contains(@href, "image")]')
for index, link in enumerate(links):
    link_value = link.attrib['href']  # Cleaner than link.css('::attr(href)').get()
    link_text = link.text
    print(f'Link number {index} points to this url {link_value} with text content as "{link_text}"')
```

## Nach Textinhalt auswählen {#text-content-selection}
Scrapling kann Elemente über ihren direkten Textinhalt auswählen. Dafür gibt es zwei Wege:

1. Mit `find_by_text` suchen Sie Elemente, deren direkter Text den angegebenen Text enthält. Mehrere Optionen steuern die Suche.
2. Mit `find_by_regex` suchen Sie Elemente, deren direkter Text zum angegebenen Regex-Muster passt. Auch hier gibt es mehrere Optionen.

Wenn Sie sich mit regulären Ausdrücken auskennen, können Sie alle Aufgaben von `find_by_text` auch mit `find_by_regex` lösen. Wir bieten beide Wege an, damit die Suche für alle einfach bleibt.

Bei `find_by_text` ist das erste Argument der gesuchte Text. Bei `find_by_regex` ist es das Regex-Muster. Beide Methoden haben diese weiteren Argumente:

* **first_match**: Bei `True`, dem Standardwert, gibt die Methode nur den ersten Treffer zurück.
* **case_sensitive**: Bei `True` wird die Groß- und Kleinschreibung berücksichtigt.
* **clean_match**: Bei `True` werden vor dem Vergleich alle Leerraumzeichen und aufeinanderfolgenden Leerzeichen durch ein einzelnes Leerzeichen ersetzt.

Standardmäßig sucht `find_by_text` nach einer exakten Übereinstimmung. Der Text des gesuchten Elements darf dann nur aus dem angegebenen Text bestehen. Um das zu ändern, gibt es ein weiteres Argument:

* **partial**: Wenn aktiviert, gibt `find_by_text` Elemente zurück, die den angegebenen Text enthalten. Der gesamte Text muss dann nicht genau übereinstimmen.

!!! abstract "Hinweis:"

    `find_by_regex` nimmt als erstes Argument eine normale Zeichenkette oder ein kompiliertes Regex-Muster an. Beispiele dazu folgen gleich.

### Ähnliche Elemente finden {#finding-similar-elements}
Eine besonders nützliche Funktion von Scrapling ist die Suche nach Elementen, die einem vorhandenen Element ähneln. Die Idee stammt aus AutoScraper. In Scrapling funktioniert sie aber mit Elementen, die Sie auf beliebige Weise gefunden haben. Oft wird sie nach einer Textsuche genutzt, wie bei AutoScraper. Deshalb erklären wir sie hier.

Wie funktioniert das?

Angenommen, Sie haben ein Produkt über seinen Titel gefunden und möchten die anderen Produkte aus derselben Tabelle oder demselben Container auslesen. Rufen Sie auf dem gefundenen Element `.find_similar()` auf. Scrapling führt dann diese Schritte aus:

1. Es sucht alle Elemente auf derselben Ebene des DOM-Baums.
2. Es prüft diese Elemente und entfernt alle, deren Tag-Name oder die Tag-Namen ihres Eltern- und Großelternelements nicht übereinstimmen.
3. Nun sind die gewünschten Elemente mit etwa 99 % Sicherheit gefunden. Als letzte Prüfung vergleicht Scrapling ihre Attribute auf Ähnlichkeit. Elemente mit zu unähnlichen Attributen fallen weg. Ein Schwellenwert steuert diesen Schritt. Ändern Sie ihn am besten nur, wenn die Standardeinstellung nicht die gewünschten Ergebnisse liefert.

Das war viel Erklärung, aber die Details sind wichtig. Im nächsten Abschnitt folgen Beispiele. Zuerst sehen wir uns die Argumente der Methode an:

* **similarity_threshold**: Der Schwellenwert aus Schritt 3 zum Vergleich der Attribute. Der Standardwert ist 0,2. Die Attribute beider Elemente müssen also mindestens zu 20 % ähnlich sein. Mit 0 schalten Sie diese Prüfung und damit Schritt 3 aus. Lesen Sie aber zuerst die anderen Argumente durch.
* **ignore_attributes**: Die hier angegebenen Attribute werden im letzten Vergleichsschritt ignoriert. Der Standardwert ist `('href', 'src',)`, weil URLs zwischen Elementen stark variieren und deshalb kein zuverlässiges Merkmal sind.
* **match_text**: Bei `True` wird in Schritt 3 auch der Textinhalt verglichen. Für normale Fälle ist diese Option nicht empfohlen, sie kann aber je nach Aufgabe sinnvoll sein.

Sehen wir uns nun die Beispiele an.

### Beispiele {#examples}
Hier sind einige Beispiele für die Suche mit Text und Regex.

Die Beispiele nutzen `Fetcher`. Diese Klasse erklären wir später genauer.
```python
from scrapling.fetchers import Fetcher
page = Fetcher.get('https://books.toscrape.com/index.html')
```
Finden Sie das erste Element, dessen Text genau übereinstimmt:
```python
>>> page.find_by_text('Tipping the Velvet')
<data='<a href="catalogue/tipping-the-velvet_99...' parent='<h3><a href="catalogue/tipping-the-velve...'>
```
Mit `page.urljoin` erhalten Sie aus dem relativen `href` die vollständige URL:
```python
>>> page.find_by_text('Tipping the Velvet').attrib['href']
'catalogue/tipping-the-velvet_999/index.html'
>>> page.urljoin(page.find_by_text('Tipping the Velvet').attrib['href'])
'https://books.toscrape.com/catalogue/tipping-the-velvet_999/index.html'
```
Lesen Sie alle Treffer aus. Das Ergebnis ist eine Liste:
```python
>>> page.find_by_text('Tipping the Velvet', first_match=False)
[<data='<a href="catalogue/tipping-the-velvet_99...' parent='<h3><a href="catalogue/tipping-the-velve...'>]
```
Finden Sie alle Elemente, die das Wort `the` enthalten, also teilweise übereinstimmen:
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
Die Suche unterscheidet bisher nicht zwischen Groß- und Kleinschreibung. Deshalb sind Treffer mit `The` und nicht nur mit `the` dabei. Beschränken wir sie auf das kleingeschriebene `the`:
```python
>>> results = page.find_by_text('the', partial=True, first_match=False, case_sensitive=True)
>>> [i.text for i in results]
['A Light in the ...',
 'Tipping the Velvet',
 'The Boys in the ...',
 "It's Only the Himalayas"]
```
Finden Sie das erste Element, dessen Text zu diesem Regex-Muster für Preise passt:
```python
>>> page.find_by_regex(r'£[\d\.]+')
<data='<p class="price_color">£51.77</p>' parent='<div class="product_price"> <p class="pr...'>
>>> page.find_by_regex(r'£[\d\.]+').text
'£51.77'
```
Sie können auch eine kompilierte Regex übergeben. Scrapling erkennt den Typ und verarbeitet ihn entsprechend:
```python
>>> import re
>>> regex = re.compile(r'£[\d\.]+')
>>> page.find_by_regex(regex)
<data='<p class="price_color">£51.77</p>' parent='<div class="product_price"> <p class="pr...'>
>>> page.find_by_regex(regex).text
'£51.77'
```
Lesen Sie alle Elemente aus, die zur Regex passen:
```python
>>> page.find_by_regex(r'£[\d\.]+', first_match=False)
[<data='<p class="price_color">£51.77</p>' parent='<div class="product_price"> <p class="pr...'>,
 <data='<p class="price_color">£53.74</p>' parent='<div class="product_price"> <p class="pr...'>,
 <data='<p class="price_color">£50.10</p>' parent='<div class="product_price"> <p class="pr...'>,
 <data='<p class="price_color">£47.82</p>' parent='<div class="product_price"> <p class="pr...'>,
 ...]
```
Und so weiter...

Finden Sie alle Elemente mit ähnlicher Position und ähnlichen Attributen. In diesem Fall ignorieren wir beim Vergleich das Attribut 'title':
```python
>>> element = page.find_by_text('Tipping the Velvet')
>>> element.find_similar(ignore_attributes=['title'])
[<data='<a href="catalogue/a-light-in-the-attic_...' parent='<h3><a href="catalogue/a-light-in-the-at...'>,
 <data='<a href="catalogue/soumission_998/index....' parent='<h3><a href="catalogue/soumission_998/in...'>,
 <data='<a href="catalogue/sharp-objects_997/ind...' parent='<h3><a href="catalogue/sharp-objects_997...'>,
...]
```
Es sind 19 Elemente statt 20, weil das Ausgangselement nicht im Ergebnis enthalten ist.
```python
>>> len(element.find_similar(ignore_attributes=['title']))
19
```
Lesen Sie das Attribut `href` aller ähnlichen Elemente aus:
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
Etwas umfangreicher wird es, wenn Sie alle Buchdaten auslesen möchten und dieses Element als Ausgangspunkt nutzen:
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
### Fortgeschrittene Beispiele {#advanced-examples}
Hier sind weitere Beispiele für `find_similar`, die näher an typischen Aufgaben liegen.

Produkte aus einem Onlineshop auslesen
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
Tabellenzeilen auslesen
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
Formularfelder auslesen
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
Bewertungen von einer Website auslesen
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
## Mit Filtern suchen {#filters-based-searching}
Die Suche mit Filtern ist oft der beste Weg, Elemente in Scrapling zu finden. Sie ist leistungsfähig und für Einsteiger leichter zu lernen als Selektoren.

Die Methoden `find_all` und `find` sind von der Funktion `find_all` aus BeautifulSoup inspiriert. Sie nehmen mehrere Filter an und suchen Elemente, die alle Bedingungen erfüllen.

Dabei gilt:

* Eine Zeichenkette wird als Tag-Name behandelt.
* Ein iterierbares Objekt wie List, Tuple oder Set wird als Sammlung von Tag-Namen behandelt.
* Ein Dictionary ordnet Attributnamen den gesuchten Werten von HTML-Elementen zu.
* Regex-Muster filtern Elemente nach ihrem Inhalt, ähnlich wie `find_by_regex`.
* Funktionen filtern die Elemente nach eigenen Bedingungen.
* Jedes Schlüsselwortargument gilt als HTML-Attribut mit dem angegebenen Wert.

Alle Argumente werden gesammelt. Die Filter werden nacheinander angewendet, wobei jeder Filter seine Ergebnisse an den nächsten weitergibt.

Die Elemente der aktuellen Seite oder des aktuellen Elements werden in dieser Reihenfolge gefiltert:

1. Alle Elemente mit den angegebenen Tag-Namen werden gesammelt.
2. Die Elemente werden nach allen angegebenen Attributen gefiltert. Falls Schritt 1 ausgeführt wurde, wird nur dessen Ergebnis geprüft.
3. Die Elemente werden nach allen angegebenen Regex-Mustern gefiltert. Falls zuvor Filter angewendet wurden, wird nur deren Ergebnis geprüft.
4. Die Elemente werden nach allen angegebenen Funktionen gefiltert. Falls zuvor Filter angewendet wurden, wird nur deren Ergebnis geprüft.

!!! note "Hinweise:"

    1. Die Verarbeitung beginnt mit dem ersten vorhandenen Filter in der oben genannten Reihenfolge. Wenn Sie keine Tag-Namen, aber Attribute angeben, startet sie also bei Schritt 2.
    2. Die Reihenfolge Ihrer Argumente spielt keine Rolle. Es gilt immer die oben beschriebene Reihenfolge.

Die Beispiele machen es deutlicher :)

### Beispiele {#examples_1}
```python
from scrapling.fetchers import Fetcher
page = Fetcher.get('https://quotes.toscrape.com/')
```
Finden Sie alle Elemente mit dem Tag-Namen `div`:
```python
>>> page.find_all('div')
[<data='<div class="container"> <div class="row...' parent='<body> <div class="container"> <div clas...'>,
 <data='<div class="row header-box"> <div class=...' parent='<div class="container"> <div class="row...'>,
...]
```
Finden Sie alle div-Elemente, deren Klasse genau `quote` ist:
```python
>>> page.find_all('div', class_='quote')
[<data='<div class="quote" itemscope itemtype="h...' parent='<div class="col-md-8"> <div class="quote...'>,
 <data='<div class="quote" itemscope itemtype="h...' parent='<div class="col-md-8"> <div class="quote...'>,
...]
```
Dasselbe Ergebnis auf einem anderen Weg:
```python
>>> page.find_all('div', {'class': 'quote'})
[<data='<div class="quote" itemscope itemtype="h...' parent='<div class="col-md-8"> <div class="quote...'>,
 <data='<div class="quote" itemscope itemtype="h...' parent='<div class="col-md-8"> <div class="quote...'>,
...]
```
Finden Sie alle Elemente, deren Klasse genau `quote` ist:
```python
>>> page.find_all({'class': 'quote'})
[<data='<div class="quote" itemscope itemtype="h...' parent='<div class="col-md-8"> <div class="quote...'>,
 <data='<div class="quote" itemscope itemtype="h...' parent='<div class="col-md-8"> <div class="quote...'>,
...]
```
Finden Sie alle div-Elemente mit der Klasse `quote`, die ein Element `.text` mit dem Wort 'world' im Inhalt enthalten:
```python
>>> page.find_all('div', {'class': 'quote'}, lambda e: "world" in e.css('.text::text').get())
[<data='<div class="quote" itemscope itemtype="h...' parent='<div class="col-md-8"> <div class="quote...'>]
```
Finden Sie alle Elemente, die Kinder haben:
```python
>>> page.find_all(lambda element: len(element.children) > 0)
[<data='<html lang="en"><head><meta charset="UTF...'>,
 <data='<head><meta charset="UTF-8"><title>Quote...' parent='<html lang="en"><head><meta charset="UTF...'>,
 <data='<body> <div class="container"> <div clas...' parent='<html lang="en"><head><meta charset="UTF...'>,
...]
```
Finden Sie alle Elemente mit dem Wort 'world' im Inhalt:
```python
>>> page.find_all(lambda element: "world" in element.text)
[<data='<span class="text" itemprop="text">“The...' parent='<div class="quote" itemscope itemtype="h...'>,
 <data='<a class="tag" href="/tag/world/page/1/"...' parent='<div class="tags"> Tags: <meta class="ke...'>]
```
Finden Sie alle span-Elemente, die zur angegebenen Regex passen:
```python
>>> page.find_all('span', re.compile(r'world'))
[<data='<span class="text" itemprop="text">“The...' parent='<div class="quote" itemscope itemtype="h...'>]
```
Finden Sie alle div- und span-Elemente mit der Klasse 'quote'. Hier gibt es keine passenden span-Elemente, daher werden nur div-Elemente zurückgegeben:
```python
>>> page.find_all(['div', 'span'], {'class': 'quote'})
[<data='<div class="quote" itemscope itemtype="h...' parent='<div class="col-md-8"> <div class="quote...'>,
 <data='<div class="quote" itemscope itemtype="h...' parent='<div class="col-md-8"> <div class="quote...'>,
...]
```
Kombinieren Sie verschiedene Filter:
```python
>>> page.find_all({'itemtype':"http://schema.org/CreativeWork"}, 'div').css('.author::text').getall()
['Albert Einstein',
 'J.K. Rowling',
...]
```
Noch ein Tipp: Finden Sie alle Elemente, deren `href`-Wert mit 'Einstein' endet:
```python
>>> page.find_all({'href$': 'Einstein'})
[<data='<a href="/author/Albert-Einstein">(about...' parent='<span>by <small class="author" itemprop=...'>,
 <data='<a href="/author/Albert-Einstein">(about...' parent='<span>by <small class="author" itemprop=...'>,
 <data='<a href="/author/Albert-Einstein">(about...' parent='<span>by <small class="author" itemprop=...'>]
```
Ein weiterer Tipp: Finden Sie alle Elemente, deren `href`-Wert '/author/' enthält:
```python
>>> page.find_all({'href*': '/author/'})
[<data='<a href="/author/Albert-Einstein">(about...' parent='<span>by <small class="author" itemprop=...'>,
 <data='<a href="/author/J-K-Rowling">(about)</a...' parent='<span>by <small class="author" itemprop=...'>,
 <data='<a href="/author/Albert-Einstein">(about...' parent='<span>by <small class="author" itemprop=...'>,
...]
```
Und so weiter...

## Selektoren erzeugen {#generating-selectors}
Sie können für jedes Element CSS- oder XPath-Selektoren erzeugen und diese in Scrapling oder anderswo wiederverwenden. Dabei spielt es keine Rolle, mit welcher Methode Sie das Element gefunden haben!

Erzeugen Sie für `url_element` möglichst einen kurzen CSS-Selektor. Falls das nicht geht, wird ein vollständiger Selektor erzeugt:
```python
>>> url_element = page.find({'href*': '/author/'})
>>> url_element.generate_css_selector
'body > div > div:nth-of-type(2) > div > div > span:nth-of-type(2) > a'
```
Erzeugen Sie für `url_element` einen vollständigen CSS-Selektor vom Seitenanfang aus:
```python
>>> url_element.generate_full_css_selector
'body > div > div:nth-of-type(2) > div > div > span:nth-of-type(2) > a'
```
Erzeugen Sie für `url_element` möglichst einen kurzen XPath-Selektor. Falls das nicht geht, wird ein vollständiger Selektor erzeugt:
```python
>>> url_element.generate_xpath_selector
'//body/div/div[2]/div/div/span[2]/a'
```
Erzeugen Sie für `url_element` einen vollständigen XPath-Selektor vom Seitenanfang aus:
```python
>>> url_element.generate_full_xpath_selector
'//body/div/div[2]/div/div/span[2]/a'
```
!!! abstract "Hinweis:"

    Für einen kurzen Selektor sucht Scrapling ein eindeutig erkennbares Element als Ausgangspunkt, etwa eines mit einem `id`-Attribut. In unserem Fall gibt es keines. Deshalb sind der kurze und der vollständige Selektor gleich.

## Selektoren mit regulären Ausdrücken nutzen {#using-selectors-with-regular-expressions}
Wie in `parsel`/`scrapy` gibt es die Methoden `re` und `re_first`, um Daten mit regulären Ausdrücken auszulesen. In Scrapling stehen sie aber in fast allen Klassen bereit, etwa in `Selector`/`Selectors`/`TextHandler` und `TextHandlers`. Sie können sie daher direkt auf einem Element aufrufen, ohne zuvor einen Textknoten auszuwählen.

Im Abschnitt zu [TextHandler](main_classes.md#texthandler) erklären wir das genauer. Grundsätzlich funktioniert es wie in diesen Beispielen:
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
Und so weiter. Auf der nächsten Seite erklären wir dies zusammen mit der Klasse [TextHandler](main_classes.md#texthandler) genauer.