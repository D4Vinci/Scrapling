> You can take advantage of the custom-made types for Scrapling and use them outside the library if you want. It's better than copying their code, after all :)

### All current types can be imported alone, like below
```python
>>> from scrapling.core.custom_types import TextHandler, AttributesHandler

>>> somestring = TextHandler('{}')
>>> somestring.json()
'{}'
>>> somedict_1 = AttributesHandler({'a': 1})
>>> somedict_2 = AttributesHandler(a=1)
```

Note that `TextHandler` is a subclass of Python's `str`, so all standard operations/methods that work with Python strings will work.
If you want to check the type in your code, it's better to use Python's built-in `issubclass` function.

The class `AttributesHandler` is a subclass of `collections.abc.Mapping`, so it's immutable (read-only), and all operations are inherited from it. The data passed can be accessed later through the `_data` property, but be careful; it's of type `types.MappingProxyType`, so it's immutable (read-only) as well (faster than `collections.abc.Mapping` by fractions of seconds).

So, to make it simple for you, if you are new to Python, the same operations and methods from the Python standard `dict` type will all work with the class `AttributesHandler` except for the ones that try to modify the actual data.

If you want to modify the data inside `AttributesHandler`, you have to convert it to a dictionary first, e.g., using the `dict` function, and then change it outside.