---
title: "Scraplings Text- und Attributtypen in Ihrem Code verwenden"
description: "Verwenden Sie TextHandler, TextHandlers und AttributesHandler außerhalb des Parsers. Lernen Sie ihre Python-Basistypen, JSON-Hilfsfunktionen und schreibgeschützten Attribute kennen."
---

# Scraplings eigene Typen verwenden {#using-scraplings-custom-types}

> Sie können die für Scrapling erstellten Typen auch außerhalb der Bibliothek nutzen. Das ist besser, als ihren Code zu kopieren :)

### Alle aktuellen Typen lassen sich einzeln importieren {#all-current-types-can-be-imported-alone-like-below}
```python
from scrapling.core.custom_types import TextHandler, AttributesHandler

somestring = TextHandler('{}')
parsed = somestring.json()
somedict_1 = AttributesHandler({'a': 1})
somedict_2 = AttributesHandler(a=1)
```

`TextHandler` ist eine Unterklasse von Pythons `str`. Deshalb funktionieren alle üblichen Operationen und Methoden für Python-Strings.
`parsed` ist das Dictionary `{}`, nicht der String `'{}'`. Prüfen Sie eine Instanz mit `isinstance(somestring, TextHandler)` und eine Klasse mit `issubclass(TextHandler, str)`.

Die Klasse `AttributesHandler` ist eine Unterklasse von `collections.abc.Mapping`. Sie ist unveränderlich, also schreibgeschützt, und erbt dessen Operationen. Auf die übergebenen Daten können Sie später über die Eigenschaft `_data` zugreifen. Diese hat jedoch den Typ `types.MappingProxyType` und ist ebenfalls schreibgeschützt. Sie ist um Bruchteile einer Sekunde schneller als `collections.abc.Mapping`.

Wenn Sie Python noch nicht gut kennen: Die üblichen Operationen und Methoden des Standardtyps `dict` funktionieren auch mit `AttributesHandler`, außer denen, die Daten ändern.

Um Daten aus `AttributesHandler` zu ändern, müssen Sie diese zuerst in ein Dictionary umwandeln, etwa mit der Funktion `dict`. Danach bearbeiten Sie dieses Dictionary außerhalb des Objekts.
