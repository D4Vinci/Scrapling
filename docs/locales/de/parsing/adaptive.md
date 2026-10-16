---
title: "HTML-Elemente mit adaptivem Parsing verfolgen und wiederfinden"
description: "Speichern Sie die Merkmale von Elementen und finden Sie diese nach HTML-Änderungen wieder. Lernen Sie, adaptives Parsing mit save, retrieve und relocate zu nutzen."
---

# Adaptives Scraping {#adaptive-scraping}

!!! success "Voraussetzungen"

    1. Sie haben die Seite [Elemente auswählen](../parsing/selection.md) gelesen und wissen, wie Sie Elemente in einem [Selector](../parsing/main_classes.md#selector)-Objekt finden und extrahieren.
    2. Sie haben die Seite [Hauptklassen](../parsing/main_classes.md) gelesen und kennen die Klasse [Selector](../parsing/main_classes.md#selector).

Adaptives Scraping, früher als automatch bekannt, ist eine der stärksten Funktionen von Scrapling. Es verfolgt Elemente und findet sie wieder, damit Ihr Scraper auch nach Änderungen an einer Website weiter funktioniert.

Angenommen, Sie lesen Daten aus einer Seite mit dieser Struktur aus:
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
Sie möchten das erste Produkt mit der ID `p1` auslesen. Dafür würden Sie vermutlich diesen Selektor verwenden:
```python
page.css('#p1')
```
Wenn die Betreiber der Website die Struktur so ändern:
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
Dann funktioniert der Selektor nicht mehr, und Sie müssen Ihren Code anpassen. Hier hilft die Funktion `adaptive` von Scrapling.

Mit Scrapling können Sie `adaptive` aktivieren, wenn Sie ein Element zum ersten Mal auswählen. Wenn Sie es später erneut auswählen und es nicht mehr gefunden wird, nutzt Scrapling die gespeicherten Merkmale. Es sucht auf der Website nach dem Element mit der höchsten Ähnlichkeit. Und das ohne KI :)

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
Im folgenden Beispiel sehen Sie, wie Sie diese Funktion nutzen. Danach erklären wir die Verwendung und die Details genauer. Sie funktioniert mit allen Auswahlmethoden, nicht nur mit CSS/XPath.

## Beispiel aus der Praxis {#real-world-scenario}
Nehmen wir eine echte Website und laden ihren Quelltext mit einem Fetcher. Dafür müssten wir eine Website finden, deren Design oder Struktur sich bald ändert. Dann würden wir ihren Quelltext speichern und auf die Änderung warten. Das lässt sich natürlich kaum vorhersagen, außer ich kenne den Betreiber. Dann wäre der Test aber gestellt, haha.

Deshalb nutze ich die [Wayback Machine](https://web.archive.org/) von [The Web Archive](https://archive.org/). Hier ist eine Kopie der [StackOverFlow-Website von 2010](https://web.archive.org/web/20100102003420/http://stackoverflow.com/). Ziemlich alt, oder?</br>Prüfen wir, ob die adaptive Funktion mit demselben Selektor den gleichen Button im alten Design von 2010 und im aktuellen Design findet :)

Um den Button Questions im alten Design auszuwählen, kann ich diesen Selektor nutzen: `#hmenus > div:nth-child(1) > ul > li:nth-child(1) > a`. Er ist sehr genau festgelegt, weil Google Chrome ihn erzeugt hat.


Testen wir jetzt denselben Selektor in beiden Versionen:
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
Hier kommt das neue Argument `adaptive_domain` dazu. Für Scrapling sind `archive.org` und `stackoverflow.com` zwei verschiedene Domains. Deshalb speichert es ihre `adaptive`-Daten getrennt. Damit Scrapling beide als dieselbe Website behandelt, geben wir für beide eine gemeinsame Domain zum Speichern der `adaptive`-Daten an.

In der Praxis wäre der Code gleich, aber beide Anfragen hätten dieselbe URL. Dann brauchen Sie das Argument `adaptive_domain` nicht. Dieses Beispiel kommt einem echten Fall so nah wie möglich. Ich hoffe, es hat Sie nicht verwirrt :)

In den beiden Beispielen habe ich die Klassen `Selector` und `Fetcher` verwendet. So sehen Sie, dass die adaptive Logik bei beiden gleich ist.

!!! info

    Das Argument `adaptive_domain` ist vor allem für Websites gedacht, die mit ihrem Design oder ihrer Struktur auch die URL ändern. Sie können damit die gespeicherten adaptiven Daten unter der neuen URL weiter nutzen. Sonst behandelt Scrapling die URL als neue Website und verwendet die alten Daten nicht mehr.

## So funktioniert adaptives Scraping {#how-the-adaptive-scraping-feature-works}
Adaptives Scraping hat zwei Phasen:

1. **Speichern**: Die besonderen Merkmale der Elemente speichern.
2. **Abgleichen**: Später Elemente mit ähnlichen Merkmalen finden.

Angenommen, Sie haben ein Element mit einer beliebigen Methode ausgewählt. Die Bibliothek soll es beim nächsten Abruf der Website wiederfinden, auch wenn sich Struktur oder Design geändert haben.

Ohne zu viele technische Details läuft das so ab:

  1. Sie weisen Scrapling an, die besonderen Merkmale des Elements zu speichern. Die möglichen Wege zeigen wir weiter unten.
  2. Scrapling speichert die Merkmale jedes Elements in der eingestellten Datenbank. Standardmäßig ist das SQLite.
  3. Die Betreiber der Website können jedes Merkmal eines Elements ändern oder entfernen. Deshalb eignet sich keines davon als feste Kennung in der Datenbank. Das Speichersystem nutzt stattdessen zwei Angaben:
     1. Die Domain der aktuellen Website. Bei der Klasse `Selector` geben Sie diese beim Erstellen an. Bei einem Fetcher wird sie automatisch aus der URL übernommen.
     2. Einen `identifier`, um die Merkmale des Elements aus der Datenbank abzurufen. Diese Kennung müssen Sie nicht immer selbst festlegen. Dazu später mehr.

     Zusammen dienen beide Angaben dazu, die gespeicherten Merkmale des Elements aus der Datenbank abzurufen.

  4. Wenn sich die Struktur der Website später ändert, aktivieren Sie `adaptive`, um das Element zu finden. Scrapling lädt seine gespeicherten Merkmale und vergleicht alle Elemente auf der Seite damit. Für jedes Element berechnet es einen Wert für die Ähnlichkeit zum gesuchten Element. Dabei berücksichtigt es alle Merkmale, wie wir gleich sehen.
  5. Es gibt die Elemente mit der höchsten Ähnlichkeit zum gesuchten Element zurück.

### Die besonderen Merkmale {#the-unique-properties}
Vielleicht fragen Sie sich, welche Merkmale hier gemeint sind, wenn sich doch alle Eigenschaften eines Elements ändern oder entfernen lassen.

Scrapling nutzt diese Merkmale:

- Tag-Name, Text, Attribute mit Namen und Werten, Geschwisterelemente mit ihren Tag-Namen und der Pfad mit seinen Tag-Namen.
- Tag-Name, Attribute mit Namen und Werten sowie Text des übergeordneten Elements.

Der Vergleich sucht nicht nach exakt gleichen Werten, sondern nach ähnlichen. Dabei zählt alles, auch die Reihenfolge der Werte. Das gilt zum Beispiel für die Reihenfolge der Klassennamen eines Elements vor und nach der Änderung.

## Die adaptive Funktion nutzen {#how-to-use-adaptive-feature}
Sie können die adaptive Funktion auf jedes gefundene Element anwenden. Wie oben gezeigt, steht sie auch über Argumente der CSS/XPath-Auswahlmethoden bereit. Darauf kommen wir gleich zurück.

Zuerst müssen Sie `adaptive` aktivieren. Übergeben Sie dazu `adaptive=True`, wenn Sie eine Instanz der Klasse [Selector](main_classes.md#selector) erstellen. Oder aktivieren Sie die Funktion im verwendeten Fetcher, wie wir gleich zeigen.

Beispiele:
```python
from scrapling import Selector, Fetcher
page = Selector(html_doc, adaptive=True)
# OR
Fetcher.adaptive = True
page = Fetcher.get('https://example.com')
```
Wenn Sie die Klasse [Selector](main_classes.md#selector) nutzen, geben Sie mit `url` die URL der Website an. Damit kann Scrapling die gespeicherten Merkmale nach Domain trennen.

Ohne URL wird beim Speichern der Merkmale das Wort `default` als URL-Wert verwendet. Das wird nur dann zum Problem, wenn Sie später dieselbe Kennung für eine andere Website nutzen und beim Erstellen wieder keine URL angeben. Das Speichern überschreibt die bisherigen Daten. Die Funktion `adaptive` nutzt immer die zuletzt gespeicherten Merkmale.

Außerdem gibt es `storage` und `storage_args`. Diese Argumente legen die Verbindung zur Datenbank fest. Standardmäßig wird die SQLite-Klasse der Bibliothek verwendet. Sie brauchen diese Argumente nur, wenn Sie ein eigenes Speichersystem schreiben möchten. Das erklären wir auf einer [eigenen Seite im Entwicklungsbereich](../development/adaptive_storage_system.md).

Nachdem Sie `adaptive` global aktiviert haben, können Sie die Funktion auf zwei Arten nutzen.

### Mit CSS/XPath auswählen {#the-cssxpath-selection-way}
Wie im Beispiel oben wählen Sie zuerst ein vorhandenes Element mit dem Argument `auto_save` aus:
```python
element = page.css('#p1', auto_save=True)
```
Wenn das Element später nicht mehr gefunden wird, verwenden Sie denselben Selektor mit `adaptive`. Die Bibliothek sucht es dann für Sie:
```python
element = page.css('#p1', adaptive=True)
```
Ziemlich einfach, oder?

Im Hintergrund passiert dabei einiges. Erinnern Sie sich an die Kennung, mit der Sie die Merkmale des gewünschten Elements abrufen? Bei den Methoden `css`/`xpath` wird dafür automatisch der übergebene Selektor verwendet. Das macht die Nutzung einfacher :)

Sie können bei all diesen Methoden auch `identifier` übergeben und die Kennung selbst festlegen. Das ist in manchen Fällen hilfreich. Sie können diese Kennung auch zusammen mit `auto_save` zum Speichern der Merkmale nutzen.

### Manuell vorgehen {#the-manual-way}
Sie können ein Element selbst speichern, seine Merkmale abrufen und es dann wiederfinden. Auch das geschieht mit `adaptive`, wie unten gezeigt. So können Sie jedes Element wiederfinden, unabhängig von der verwendeten Auswahlmethode!

Angenommen, Sie haben ein Element über seinen Text gefunden:
```python
element = page.find_by_text('Tipping the Velvet', first_match=True)
```
Mit der Methode `save` speichern Sie seine besonderen Merkmale. Dabei müssen Sie die Kennung selbst festlegen. Hier verwende ich `my_special_element`. Wählen Sie in Ihrem Code einen aussagekräftigen Namen, genau wie bei Variablen :)
```python
page.save(element, 'my_special_element')
```
Wenn Sie die Merkmale später abrufen und das Element mit `adaptive` auf der Seite wiederfinden möchten, geht das so:
```python
>>> element_dict = page.retrieve('my_special_element')
>>> page.relocate(element_dict, selector_type=True)
[<data='<a href="catalogue/tipping-the-velvet_99...' parent='<h3><a href="catalogue/tipping-the-velve...'>]
>>> page.relocate(element_dict, selector_type=True).css('::text').getall()
['Tipping the Velvet']
```
Dafür werden also die Methoden `retrieve` und `relocate` verwendet.

Wenn Sie das Ergebnis als `lxml.etree`-Objekt behalten möchten, lassen Sie das Argument `selector_type` weg:
```python
>>> page.relocate(element_dict)
[<Element a at 0x105a2a7b0>]
```

## Fehler beheben {#troubleshooting}

### Keine Treffer gefunden {#no-matches-found}
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

### Falsche Elemente gefunden {#wrong-elements-matched}
```python
# Use more specific selectors
products = page.css('.product-list .product', auto_save=True)

# Or save with more context
product = page.find_by_text('Product Name').parent
page.save(product, 'specific_product')
```

## Bekannte Probleme {#known-issues}
Beim Speichern mit `adaptive` werden nur die besonderen Merkmale des ersten Elements im Auswahlergebnis gespeichert. Wenn Ihr Selektor verschiedene Elemente an mehreren Stellen der Seite auswählt, findet `adaptive` später nur das erste davon wieder. Das gilt nicht für kombinierte CSS-Selektoren, zum Beispiel mehrere mit Kommas getrennte Selektoren. Diese werden einzeln ausgeführt.

## Zum Schluss {#final-thoughts}
Diese Funktion genau und trotzdem einfach zu erklären, war nicht leicht. Falls etwas unklar bleibt, schreiben Sie im [Diskussionsbereich](https://github.com/D4Vinci/Scrapling/discussions). Ich antworte so schnell wie möglich. Sie können auch den Discord-Server nutzen oder mir direkt schreiben :)