---
title: "在自己的代码中使用 Scrapling 的文本和属性类型"
description: "在解析器之外使用 TextHandler、TextHandlers 和 AttributesHandler。了解它们的 Python 基础类型、JSON 辅助方法和只读属性。"
---

# 使用 Scrapling 的自定义类型 {#using-scraplings-custom-types}

> Scrapling 的自定义类型也可以在库外使用。毕竟，直接使用比复制代码更好 :)

### 当前所有类型都可以单独导入 {#all-current-types-can-be-imported-alone-like-below}
```python
from scrapling.core.custom_types import TextHandler, AttributesHandler

somestring = TextHandler('{}')
parsed = somestring.json()
somedict_1 = AttributesHandler({'a': 1})
somedict_2 = AttributesHandler(a=1)
```

`TextHandler` 是 Python `str` 的子类，因此 Python 字符串支持的所有标准操作和方法都能使用。
`parsed` 是字典 `{}`，不是字符串 `'{}'`。检查实例时使用 `isinstance(somestring, TextHandler)`，检查类时使用 `issubclass(TextHandler, str)`。

`AttributesHandler` 是 `collections.abc.Mapping` 的子类，因此不可修改，也就是只读，并继承了它的操作。之后可以通过 `_data` 属性访问传入的数据，但它的类型是 `types.MappingProxyType`，同样是只读的，比 `collections.abc.Mapping` 快一点。

如果刚接触 Python，可以这样理解：Python 标准 `dict` 类型的操作和方法，在 `AttributesHandler` 上也能使用，但修改数据的操作除外。

如果要修改 `AttributesHandler` 中的数据，必须先将其转成字典，例如使用 `dict` 函数，然后在对象之外修改这个字典。
