---
title: "Shopify-Produktdaten mit Python extrahieren"
description: "Extrahieren Sie mit ShopifySpider den Katalog eines Shopify-Shops. Legen Sie die Shop-URL fest, erfassen Sie Produktvarianten und prüfen Sie die Felder der Datensätze."
---

# Spider-Vorlagen für Plattformen {#platform-spider-templates}

Allgemeine Vorlagen decken Crawl-*Muster* ab, etwa Links folgen oder Sitemaps durchlaufen. Plattformvorlagen decken *Plattformen* ab: Systeme zum Erstellen von Websites, die auf vielen unabhängigen Websites dieselbe maschinenlesbare Struktur bereitstellen. Der Spider weiß dadurch bereits, wo die Daten liegen. Sie geben nur eine Domain an.

## ShopifySpider {#shopifyspider}

`ShopifySpider` extrahiert alle Produkte eines Shopify-Shops über die JSON-API von Shopify. Das HTML der Website wird dabei nicht verwendet.

```python
from scrapling.spiders import ShopifySpider

class MyStore(ShopifySpider):
    target_website = "example.com"

result = MyStore().start()
print(result.items[0])
```

Setzen Sie `target_website` auf die Domain des Shops. Ist der Wert leer, verwendet der Spider den ersten Eintrag in `start_urls`, danach in `allowed_domains`. Sind alle drei leer, löst er `ValueError` aus. Vollständige URLs werden automatisch auf ihre Domain gekürzt.

### Funktionsweise {#how-it-works}

1. Ruft die Seiten von `https://<store>/collections.json` ab, mit höchstens 250 Kollektionen pro Seite, dem Limit der Plattform.
2. Ruft für jede Kollektion, die Produkte meldet, die Seiten von `/collections/<handle>/products.json` ab.
3. Liefert einen Datensatz pro Produktvariante. Varianten aus mehreren Kollektionen werden nur einmal ausgegeben.

### Felder der Datensätze {#item-fields}

| Feld          | Quelle                                                                    |
|---------------|---------------------------------------------------------------------------|
| `name`        | Produkttitel, ergänzt um den Variantentitel, wenn dieser nicht der Standardtitel ist |
| `price`       | Preis der Variante als String, genau wie von Shopify zurückgegeben        |
| `category`    | Textkennung der Kollektion in der URL mit großem Anfangsbuchstaben je Wort (`summer-sale` wird zu `Summer Sale`) |
| `brand`       | Anbieter des Produkts                                                     |
| `identifier`  | ID der Variante                                                           |
| `sku`         | SKU der Variante oder `""`, wenn der Shop keine festlegt                  |
| `stock`       | `None`, wenn die Variante verfügbar ist, sonst `0`                         |
| `image_url`   | Erstes Produktbild oder `""`                                              |
| `url`         | Produktseite innerhalb der Kollektion                                     |
| `description` | `body_html` des Produkts ohne HTML-Tags                                    |
| `old_price`   | `compare_at_price`, wenn es ein tatsächlicher Preis vor dem Rabatt ist, sonst `""` |
| `barcode`     | Barcode der Variante oder `""` (die meisten Shops geben ihn an diesen Endpunkten nicht aus) |

Diese Felder sind nicht vorgeschrieben. Überschreiben Sie `_process_product()` in Ihrer Unterklasse, um die Struktur der Datensätze zu ändern oder andere Felder aus den Produktdaten zu extrahieren.

### Hinweise und Grenzen {#notes-and-limits}

- Die JSON-Endpunkte zeigen nur Produkte, die im Onlineshop-Vertriebskanal veröffentlicht sind. Daher kann `products_count` einer Kollektion höher sein als die tatsächlich abrufbare Menge. Der Spider nutzt den Wert nur so: Ist er nicht null, wird die Kollektion abgerufen. Er dient nie als erwartete Gesamtzahl.
- Bei Shops mit zusätzlichem Schutz oder Passwortschutz funktioniert diese Vorlage wahrscheinlich nicht. Wenn sie überhaupt funktioniert, müssen Sie viele Methoden selbst überschreiben.
- Alle Funktionen von `Spider` gelten weiterhin: Einstellungen für parallele Anfragen, Wartezeiten, robots.txt, Checkpoints und Lebenszyklus-Hooks.

### Welche Plattformvorlagen aufgenommen werden {#what-qualifies-as-a-platform-template}

Wir nehmen Vorlagen für Plattformen auf, die wie Shopify auf vielen unabhängigen Websites eine einheitliche, maschinenlesbare Struktur bereitstellen. Spider für einzelne Websites gehören nicht in die Bibliothek, unabhängig davon, wie beliebt die Website ist.
