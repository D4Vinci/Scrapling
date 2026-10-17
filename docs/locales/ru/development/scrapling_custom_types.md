---
title: "Типы текста и атрибутов Scrapling в вашем коде"
description: "Используйте TextHandler, TextHandlers и AttributesHandler вне парсера. Узнайте об их базовых типах Python, работе с JSON и атрибутах только для чтения."
---

# Использование типов Scrapling {#using-scraplings-custom-types}

> Типы, созданные для Scrapling, можно использовать и вне библиотеки. Это удобнее, чем копировать их код :)

### Все типы можно импортировать отдельно {#all-current-types-can-be-imported-alone-like-below}
```python
from scrapling.core.custom_types import TextHandler, AttributesHandler

somestring = TextHandler('{}')
parsed = somestring.json()
somedict_1 = AttributesHandler({'a': 1})
somedict_2 = AttributesHandler(a=1)
```

`TextHandler` наследует Python-класс `str`, поэтому поддерживает все стандартные операции и методы строк.
`parsed` содержит словарь `{}`, а не строку `'{}'`. Для проверки экземпляра используйте `isinstance(somestring, TextHandler)`. Для проверки класса используйте `issubclass(TextHandler, str)`.

`AttributesHandler` наследует `collections.abc.Mapping` и предоставляет неизменяемое отображение, доступное только для чтения. Операции наследуются от базового класса. Переданные данные доступны через свойство `_data`, но оно тоже доступно только для чтения: его тип `types.MappingProxyType` немного быстрее `collections.abc.Mapping`.

Если вы только начинаете изучать Python, достаточно помнить: у `AttributesHandler` работают стандартные операции и методы `dict`, кроме тех, которые меняют данные.

Чтобы изменить данные из `AttributesHandler`, сначала преобразуйте их в обычный словарь, например функцией `dict`, и меняйте уже этот словарь.
