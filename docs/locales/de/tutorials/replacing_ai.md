---
title: "Eine kostenlose Alternative zu KI für zuverlässiges Web Scraping"
description: "Scrapling hilft bei geänderten Seiten, instabilen Selektoren, Bot-Schutz und Seitennavigation, ohne für jede Seite ein LLM aufzurufen."
---

# Scrapling: Eine kostenlose Alternative zu KI für zuverlässiges Web Scraping {#scrapling-a-free-alternative-to-ai-for-robust-web-scraping}

Web Scraping wird seit Langem genutzt, um Daten zu sammeln, Inhalte zu indexieren und Datensätze vorzubereiten. Erfahrene Nutzer stoßen dabei oft auf Probleme, die ihre Arbeit erschweren. In letzter Zeit wächst das Interesse an Web Scraping mit KI, weil sie einen Teil dieser Probleme lösen kann.

In diesem Artikel sehen wir uns die häufigsten Probleme an. Wir erklären, warum Unternehmen KI einsetzen, welche Grenzen dieser Ansatz hat und wie Scrapling ohne die Kosten von KI helfen kann.

## Häufige Probleme und schwierige Ziele {#common-issues-and-challenging-goals}

Wenn Sie schon länger Web Scraping betreiben, kennen Sie wahrscheinlich diese wiederkehrenden Probleme:

1. **Häufige Änderungen an der Seitenstruktur**: Websites ändern ihren DOM. Feste XPath- oder CSS-Selektoren funktionieren dann nicht mehr.
2. **Instabile Selektoren**: Klassennamen und IDs ändern sich oder werden zufällig erzeugt. Das lässt Scraper scheitern oder erschwert die Datenextraktion.
3. **Immer komplexerer Bot-Schutz**: CAPTCHA-Systeme, Browser-Fingerprinting und Verhaltensanalysen erschweren klassisches Scraping.

Und das sind noch nicht alle. Diese Probleme treten schon bei bekannten Websites auf, für die Sie jeweils eigenen Code schreiben können.

Wenn Sie größere Ziele haben und viele verschiedene Websites abdecken wollen, oft Broad Scraping oder Generic Web Scraping genannt, werden diese Probleme größer. Weitere kommen hinzu:

1. **Sehr unterschiedliche Websites**: Ein allgemeiner Scraper muss viele HTML-Strukturen, CSS-Nutzungsweisen, JavaScript-Frameworks und Backend-Technologien unterstützen.
2. **Wichtige Daten erkennen**: Woher weiß der Scraper, welche Daten auf einer unbekannten Seite wichtig sind?
3. **Verschiedene Arten der Seitennavigation**: Endloses Scrollen, nummerierte Seiten und Schaltflächen zum Nachladen brauchen unterschiedliche Ansätze.

Die Liste geht weiter. Wie lösen Sie das alles von Hand? Gemeint sind verschiedene Websites, die keine gemeinsamen Technologien verwenden.

## KI hilft, kostet aber viel {#ai-to-the-rescue-but-at-a-high-cost}

KI kann viele dieser Probleme lösen, weil sie den Quelltext der Seite versteht, gewünschte Felder erkennt oder Selektoren dafür erstellt. Natürlich setzt das voraus, dass Sie den Bot-Schutz bereits mit anderen Werkzeugen umgehen :)

Ich mag diesen Ansatz. KI fasziniert mich, besonders generative KI. Sie werden wahrscheinlich viel Zeit damit verbringen, Prompts zu schreiben und anzupassen. Wenn Sie damit zufrieden sind, stoßen Sie bald auf das eigentliche Problem beim Einsatz von KI in diesem Fall.

Viele Seiten enthalten sehr große Mengen an Inhalt. Diesen müssen Sie dem Modell irgendwie übergeben. Dabei werden schnell viele Tokens verbraucht, und die Kosten steigen rasch.

Wenn Geld für Sie eine Rolle spielt, werden Sie nach günstigeren Lösungen suchen. Hier kommt Scrapling ins Spiel :smile:

## Scrapling hilft Ihnen {#scrapling-got-you-covered}

Scrapling kann fast alle Probleme bewältigen, die Ihnen beim Web Scraping begegnen. Die nächsten Updates werden die übrigen abdecken.

### Problem T1 lösen: Häufige Änderungen an der Seitenstruktur {#solving-issue-t1-rapidly-changing-website-structures}

Dafür wurde die Funktion [adaptive](../parsing/adaptive.md) entwickelt. Sie wussten, dass ich darauf zurückkommen würde, und jetzt ist es so weit :)

Wenn `adaptive` aktiviert ist, können Sie die besonderen Eigenschaften eines Elements speichern. So finden Sie es später wieder, auch wenn sich die Struktur der Website ändert. Das Schwierige ist, dass sich jeder Teil eines Elements ändern kann. Es gibt also nicht immer eine feste Eigenschaft, auf die Sie sich verlassen können.

Die Funktion speichert alles, was das Element auszeichnet. Wenn die Website ihre Struktur ändert, gibt sie das Element zurück, das dem früheren Element am ähnlichsten ist.

Ich habe das bereits mit mehreren Beispielen ausführlich erklärt. Lesen Sie [hier](../parsing/adaptive.md#how-the-adaptive-scraping-feature-works) mehr dazu.

### Problem T2 lösen: Instabile Selektoren {#solving-issue-t2-unstable-selectors}

Wenn Sie schon lange Daten von Websites extrahieren, ist Ihnen das wahrscheinlich schon begegnet: eine HTML-Seite ohne IDs oder Klassen, zufällige Klassennamen oder eine Struktur, die keine stabilen Merkmale zur Auswahl bietet.

In solchen Fällen sind klassische CSS- oder XPath-Selektoren nicht immer die beste Wahl. Deshalb bietet Scrapling drei weitere Möglichkeiten zur Auswahl von Elementen:

1. [Nach Inhalt auswählen](../parsing/selection.md#text-content-selection): Suchen Sie nach Text mit `find_by_text` oder nach einer passenden Regex mit `find_by_regex`.
2. [Ähnliche Elemente auswählen](../parsing/selection.md#finding-similar-elements): Sie finden ein Element, und wir suchen die anderen.
3. [Mit Filtern auswählen](../parsing/selection.md#filters-based-searching): Sie geben die Bedingungen an, die ein Element erfüllen muss, und wir finden es.

Öffnen Sie die Links, um zu sehen, wie Scrapling die einzelnen Fälle löst.

### Problem T3 lösen: Immer komplexerer Bot-Schutz {#solving-issue-t3-increasingly-complex-anti-bot-measures}

Proxies und menschenähnliche Aktionen allein reichen bei geschützten Websites nicht immer aus. [StealthyFetcher](../fetching/stealthy.md) verbindet Browser-Automatisierung mit Anpassungen des Fingerprints und Optionen gegen Bot-Schutz. Aktivieren Sie `solve_cloudflare=True` für die Turnstile- und Interstitial-Prüfungen von Cloudflare.

### Probleme B1 und B2 lösen: Unterschiedliche Websites und wichtige Daten {#solving-issues-b1-b2-extreme-website-diversity-identifying-relevant-data}

Dieses Problem ist schwierig. Die Flexibilität von Scrapling macht es aber lösbar.

Ich habe mit jemandem gesprochen, der KI nutzt, um Preise auf verschiedenen Websites zu finden. Ihn interessieren nur Preise und Titel, deshalb lässt er die KI den Preis suchen.

Ich sagte ihm, dass er dafür keine KI braucht, und zeigte diesen Code:
```python
price_element = page.find_by_regex(r'£[\d\.,]+', first_match=True)  # Get the first element that contains a text that matches price regex eg. £10.50
# If you want the container/element that contains the price element
price_element_container = price_element.parent or price_element.find_ancestor(lambda ancestor: ancestor.has_class('product'))  # or other methods...
target_element_selector = price_element_container.generate_css_selector or price_element_container.generate_full_css_selector # or xpath
```
Dann fragte er nach einem Fall wie diesem:
```html
<span class='currency'> $ </span> <span class='a-price'> 45,000 </span>
```
Also passte ich den Code an:
```python
price_element_container = page.find_by_regex(r'[\d,]+', first_match=True).parent # Adjusted the regex for this example
full_price_data = price_element_container.get_all_text(separator="", strip=True)  # Returns '$45,000' in this case
```
Das reichte für seinen Fall. Sie können zuerst die erste Regex versuchen und zur nächsten wechseln, wenn sie nichts findet. Decken Sie zuerst die häufigsten Muster ab, dann die selteneren.
Das ist vielleicht etwas mühsam, aber deutlich günstiger als KI.

Darum geht es in diesem Beispiel: Nicht jedes Problem braucht KI. Manchmal spart Ihnen eine andere Lösung viel Geld.

### Problem B3 lösen: Verschiedene Arten der Seitennavigation {#solving-issue-b3-pagination-variations}

Scrapling hat noch keine direkte Methode, um Links zur nächsten Seite automatisch zu erkennen. Seine Spider folgen diesen Links mit `response.follow()`.

Sie können aber viele Websites abdecken, indem Sie nach häufigen Mustern suchen. Nutzen Sie zum Beispiel `page.find_by_text('Next')['href']` oder `page.find_by_text('load more')['href']`, oder Selektoren wie `'a[href*="?page="]'` oder `'a[href*="/page/"]'`. Sie sehen die Idee.

## Kostenvergleich und Einsparungen {#cost-comparison-and-savings}

Hier ist ein kurzer Vergleich:

| Aspekt | Scrapling | Werkzeuge mit KI, etwa Browse AI oder Oxylabs |
|---|---|---|
| Kosten | Kostenlos, ohne Bibliotheksgebühren pro Nutzung | Kostenpflichtige Tarife, abhängig von Anbieter und Nutzung |
| Einrichtung | Erfordert etwas technisches Wissen und manuelle Einrichtung | Oft ohne Code nutzbar und daher einfacher ohne technisches Wissen |
| Nutzung | Über Code, Terminal oder MCP-Server | Oft über eine grafische Oberfläche oder API, je nach Angebot |
| Skalierung | Hängt von der Umsetzung durch den Nutzer ab | Verwaltete Dienste mit Unterstützung für große Datenmengen |
| Anpassung an Änderungen | Hoch durch `adaptive` und Auswahlmethoden ohne CSS- oder XPath-Selektoren | Hoch und automatisch mit KI, aber bei häufigen Änderungen teuer |

Aktuelle Preise finden Sie bei [Browse AI](https://www.browse.ai/pricing) und der [Web Scraper API von Oxylabs](https://oxylabs.io/products/scraper-api/web/pricing).

## Fazit {#conclusion}

KI bietet viele starke Funktionen. Ihre Kosten können für zahlreiche Scraping-Aufgaben aber zu hoch sein. Scrapling bietet zuverlässige, flexible und günstige Werkzeuge für einzelne bekannte Websites und für viele verschiedene Websites. Damit lässt sich der Einsatz teurer KI-Lösungen oft vermeiden. Mit `adaptive`, verschiedenen Auswahlmethoden und fortgeschrittenen Fetchern können Sie Scraper erstellen, die mit Änderungen besser umgehen.

Lesen Sie weiter in der Dokumentation und entdecken Sie, wie Scrapling Ihre nächsten Web-Scraping-Projekte vereinfachen kann!
