---
title: "Von BeautifulSoup zu Scrapling wechseln"
description: "Vergleichen Sie häufige Aufgaben mit BeautifulSoup und Scrapling: Auswahl, Text, Attribute und Navigation. Lernen Sie die API-Unterschiede anhand praktischer Beispiele kennen."
---

# Von BeautifulSoup zu Scrapling wechseln {#migrating-from-beautifulsoup-to-scrapling}

Wenn Sie BeautifulSoup bereits kennen, wird Ihnen der Einstieg leichtfallen. Scrapling ist deutlich schneller, bietet dieselben Parsing-Funktionen und fügt weitere hinzu. Dazu kommen Funktionen zum Abrufen und Verarbeiten moderner Webseiten. Diese Anleitung hilft Ihnen, Ihren bestehenden BeautifulSoup-Code schnell an Scrapling anzupassen.

Die folgende Tabelle zeigt die häufigsten Aufgaben beim Web Scraping. Jede Zeile nennt den Code für BeautifulSoup und die entsprechende Methode in Scrapling.

Einige Abkürzungen von BeautifulSoup fehlen in Scrapling. Das ist einer der Gründe, warum BeautifulSoup langsamer ist. Wenn sich eine Funktion schon mit einer kurzen Zeile nutzen lässt, müssen wir diese nicht auf Kosten der Geschwindigkeit noch kürzer machen :)

| Aufgabe | BeautifulSoup-Code | Scrapling-Code |
|-----------------------------------------------------------------|---------------------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------|
| Parser importieren | `from bs4 import BeautifulSoup`                                                                               | `from scrapling.parser import Selector`                                           |
| HTML aus einer Zeichenfolge parsen | `soup = BeautifulSoup(html, 'html.parser')`                                                                   | `page = Selector(html)`                                                           |
| Ein Element finden | `element = soup.find('div', class_='example')`                                                                | `element = page.find('div', class_='example')`                                    |
| Mehrere Elemente finden | `elements = soup.find_all('div', class_='example')`                                                           | `elements = page.find_all('div', class_='example')`                               |
| Ein Element finden (Beispiel 2) | `element = soup.find('div', attrs={"class": "example"})`                                                      | `element = page.find('div', {"class": "example"})`                                |
| Ein Element finden (Beispiel 3) | `element = soup.find(re.compile("^b"))`                                                                       | `element = page.find(lambda e: re.search(r"^b", e.tag) is not None)` |
| Ein Element finden (Beispiel 4) | `element = soup.find(lambda e: len(list(e.children)) > 0)`                                                    | `element = page.find(lambda e: len(e.children) > 0)`                              |
| Ein Element finden (Beispiel 5) | `element = soup.find(["a", "b"])`                                                                             | `element = page.find(["a", "b"])`                                                 |
| Ein Element anhand seines Texts finden | `element = soup.find(text="some text")`                                                                       | `element = page.find_by_text("some text", partial=False)`                         |
| Den ersten Treffer mit CSS auswählen | `elements = soup.select_one('div.example')`                                                                   | `elements = page.css('div.example').first`                                        |
| Alle Treffer mit CSS auswählen | `elements = soup.select('div.example')`                                                                       | `elements = page.css('div.example')`                                              |
| Den Quelltext einer Seite oder eines Elements lesbar formatieren | `prettified = soup.prettify()`                                                                                | `prettified = page.prettify()`                                                    |
| Den Quelltext einer Seite oder eines Elements ohne zusätzliche Formatierung erhalten | `source = str(soup)`                                                                                          | `source = page.html_content`                                                      |
| Den Tag-Namen eines Elements erhalten | `name = element.name`                                                                                         | `name = element.tag`                                                              |
| Den Text eines Elements extrahieren | `string = element.string`                                                                                     | `string = element.text`                                                           |
| Den gesamten Text eines Dokuments oder unter einem Tag extrahieren | `text = soup.get_text(strip=True)`                                                                            | `text = page.get_all_text(strip=True)`                                            |
| Auf das Wörterbuch der Attribute zugreifen | `attrs = element.attrs`                                                                                       | `attrs = element.attrib`                                                          |
| Attribute extrahieren | `attr = element['href']`                                                                                      | `attr = element['href']`                                                          |
| Zum Elternelement wechseln | `parent = element.parent`                                                                                     | `parent = element.parent`                                                         |
| Alle Vorfahren eines Elements erhalten | `parents = list(element.parents)`                                                                             | `parents = list(element.iterancestors())`                                         |
| Ein Element unter den Vorfahren suchen | `target_parent = element.find_parent("a")`                                                                    | `target_parent = element.find_ancestor(lambda p: p.tag == 'a')`                   |
| Alle Geschwisterelemente erhalten | Nicht verfügbar                                                                                                           | `siblings = element.siblings`                                                     |
| Das nächste Geschwisterelement erhalten | `next_element = element.next_sibling`                                                                         | `next_element = element.next`                                                     |
| Ein Geschwisterelement suchen | `target_sibling = element.find_next_sibling("a")`<br/>`target_sibling = element.find_previous_sibling("a")`   | `target_sibling = element.siblings.search(lambda s: s.tag == 'a')`                |
| Mehrere Geschwisterelemente suchen | `target_sibling = element.find_next_siblings("a")`<br/>`target_sibling = element.find_previous_siblings("a")` | `target_sibling = element.siblings.filter(lambda s: s.tag == 'a')`                |
| Ein Element unter den folgenden Elementen suchen | `target_parent = element.find_next("a")`                                                                      | `target_parent = element.below_elements.search(lambda p: p.tag == 'a')`           |
| Mehrere Elemente unter den folgenden Elementen suchen | `target_parent = element.find_all_next("a")`                                                                  | `target_parent = element.below_elements.filter(lambda p: p.tag == 'a')`           |
| Ein Element unter den Vorfahren suchen | `target_parent = element.find_previous("a")` ¹                                                                | `target_parent = element.path.search(lambda p: p.tag == 'a')`                     |
| Mehrere Elemente unter den Vorfahren suchen | `target_parent = element.find_all_previous("a")` ¹                                                            | `target_parent = element.path.filter(lambda p: p.tag == 'a')`                     |
| Das vorherige Geschwisterelement erhalten | `prev_element = element.previous_sibling`                                                                     | `prev_element = element.previous`                                                 |
| Zu den Kindelementen wechseln | `children = list(element.children)`                                                                           | `children = element.children`                                                     |
| Alle Nachfahren eines Elements erhalten | `children = list(element.descendants)`                                                                        | `children = element.below_elements`                                               |
| Links in Absätzen mit der Klasse story auswählen | `group = soup.select('p.story a')`                                                             | `group = page.css('p.story a')`              |

Eine kompilierte Regex, die Sie direkt an Scraplings `find()` oder `find_all()` übergeben, durchsucht den Text der Elemente, nicht ihre Tag-Namen. Für Tag-Namen nutzen Sie die Lambda-Funktion aus der Tabelle. Für direkten Text können Sie `page.find_by_regex(r"^b")` verwenden.

¹ **Hinweis:** `find_previous`/`find_all_previous` von BS4 durchsuchen alle vorhergehenden Elemente in Dokumentreihenfolge. Scraplings `path` gibt dagegen nur Vorfahren zurück, also die Kette der Elternelemente. Die Methoden sind nicht genau gleich, aber die Suche unter den Vorfahren deckt den häufigsten Fall ab.

**Ein wichtiger Unterschied**: BeautifulSoup bietet Funktionen, um eine Seite nach dem Parsen zu verändern. Scrapling konzentriert sich darauf, Daten schnell zu extrahieren. Danach können Sie die Daten beliebig weiterverarbeiten. Beide Werkzeuge können beim Web Scraping helfen, aber eines ist darauf spezialisiert :)

### Ein vollständiges Beispiel {#putting-it-all-together}

Dieses einfache Beispiel extrahiert alle Links einer Webseite mit BeautifulSoup und Scrapling.

**Mit BeautifulSoup:**

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

**Mit Scrapling:**

```python
from scrapling import Fetcher

url = 'https://example.com'
page = Fetcher.get(url)

links = page.css('a::attr(href)').getall()
for link in links:
    print(link)
```

Scrapling verbindet das Abrufen und Parsen in einem Schritt. So wird Ihr Code einfacher und effizienter.

!!! abstract "**Weitere Hinweise:**"

    - **Verschiedene Parser**: In BeautifulSoup können Sie den Parser auswählen, zum Beispiel `lxml`. Scrapling verwendet aus Leistungsgründen standardmäßig die Bibliothek `lxml`.
    - **Elementtypen**: In BeautifulSoup sind Elemente `Tag`-Objekte, in Scrapling `Selector`-Objekte. Beide bieten ähnliche Methoden und Eigenschaften für Navigation und Datenextraktion.
    - **Fehlerbehandlung**: Beide Bibliotheken geben `None` zurück, wenn sie kein Element finden, zum Beispiel mit `soup.find()` oder `page.find()`. In Scrapling gibt `page.css()` eine leere `Selectors`-Liste zurück, wenn nichts passt. Mit `page.css('.foo').first` erhalten Sie sicher den ersten Treffer oder `None`. Prüfen Sie auf `None` oder leere Ergebnisse, bevor Sie auf Eigenschaften zugreifen.
    - **Textextraktion**: Scrapling bietet über `TextHandler` zusätzliche Methoden zur Textverarbeitung, etwa `clean()`. Diese Methode hilft, überflüssige Leerzeichen, aufeinanderfolgende Leerzeichen oder unerwünschte Zeichen zu entfernen. Die vollständige Liste finden Sie in der Dokumentation.

Die Dokumentation beschreibt die Funktionen von Scrapling genauer und enthält die vollständige Liste aller Argumente der Methoden.

Diese Anleitung soll Ihnen den Wechsel von BeautifulSoup zu Scrapling erleichtern. Viel Erfolg beim Scraping!
