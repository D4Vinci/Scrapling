---
title: "Usa los tipos de texto y atributos de Scrapling en tu código"
description: "Usa TextHandler, TextHandlers y AttributesHandler fuera del analizador. Conoce sus tipos base de Python, las funciones JSON y los atributos de solo lectura."
---

# Usar los tipos propios de Scrapling {#using-scraplings-custom-types}

> Puedes usar los tipos creados para Scrapling fuera de la biblioteca. Es más fácil que copiar su código :)

### Puedes importar cada tipo por separado {#all-current-types-can-be-imported-alone-like-below}

```python
from scrapling.core.custom_types import TextHandler, AttributesHandler

somestring = TextHandler('{}')
parsed = somestring.json()
somedict_1 = AttributesHandler({'a': 1})
somedict_2 = AttributesHandler(a=1)
```

`TextHandler` es una subclase de `str` de Python, así que admite todas las operaciones y métodos habituales de las cadenas.
`parsed` es el diccionario `{}`, no la cadena `'{}'`. Para comprobar una instancia, usa `isinstance(somestring, TextHandler)`. Para comprobar una clase, usa `issubclass(TextHandler, str)`.

`AttributesHandler` es una subclase de `collections.abc.Mapping`. Es inmutable, es decir, de solo lectura, y hereda sus operaciones. Puedes acceder a los datos mediante la propiedad `_data`, pero también es de solo lectura: su tipo es `types.MappingProxyType`, algo más rápido que `collections.abc.Mapping`.

Si estás empezando con Python, piensa en `AttributesHandler` como un `dict` que puedes consultar, pero cuyos datos no puedes cambiar. Las operaciones y los métodos habituales de los diccionarios funcionan, salvo los que modifican los datos.

Para modificar los datos de `AttributesHandler`, conviértelos primero en un diccionario, por ejemplo con `dict`, y cambia esa copia.
