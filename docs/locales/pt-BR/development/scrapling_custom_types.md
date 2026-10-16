---
title: "Use os tipos de texto e atributos do Scrapling no seu código"
description: "Use TextHandler, TextHandlers e AttributesHandler fora do analisador. Conheça os tipos base do Python, as funções JSON e os atributos somente leitura."
---

# Usar os tipos próprios do Scrapling {#using-scraplings-custom-types}

> Você pode usar os tipos criados para o Scrapling fora da biblioteca. É mais fácil do que copiar o código deles :)

### Você pode importar cada tipo separadamente {#all-current-types-can-be-imported-alone-like-below}

```python
from scrapling.core.custom_types import TextHandler, AttributesHandler

somestring = TextHandler('{}')
parsed = somestring.json()
somedict_1 = AttributesHandler({'a': 1})
somedict_2 = AttributesHandler(a=1)
```

`TextHandler` é uma subclasse de `str` do Python, então aceita todas as operações e métodos comuns de strings.
`parsed` é o dicionário `{}`, não a string `'{}'`. Para verificar uma instância, use `isinstance(somestring, TextHandler)`. Para verificar uma classe, use `issubclass(TextHandler, str)`.

`AttributesHandler` é uma subclasse de `collections.abc.Mapping`. É imutável, ou seja, somente leitura, e herda suas operações. Você pode acessar os dados pela propriedade `_data`, mas ela também é somente leitura: seu tipo é `types.MappingProxyType`, um pouco mais rápido que `collections.abc.Mapping`.

Se você está começando com Python, pense em `AttributesHandler` como um `dict` que pode ser consultado, mas cujos dados não podem ser alterados. As operações e os métodos comuns dos dicionários funcionam, exceto os que modificam os dados.

Para modificar os dados de `AttributesHandler`, primeiro converta-os em um dicionário, por exemplo com `dict`, e altere essa cópia.
