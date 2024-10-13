> You can take advantage from the custom-made types for Scrapling and use it outside the library if you want. It's better than copying their code after all :)

### All current types can be imported alone like below
```python
>>> from scrapling import TextHandler, AttributesHandler

>>> somestring = TextHandler('{}')
>>> somestring.json()
'{}'
>>> somedict_1 = AttributesHandler({'a': 1})
>>> somedict_2 = AttributesHandler(a=1)
```

Note `TextHandler` is a sub-class of Python's `str` so all normal operations/methods that work with Python strings will work.
If you want to check for the type in your code, it's better to depend on Python built-in function `issubclass`.

The class `AttributesHandler` is a sub-class of `collections.abc.Mapping` so it's immutable (read-only) and all operations are inherited from it. The data passed can be accessed later though the `._data` method but careful it's of type `types.MappingProxyType` so it's immutable (read-only) as well (faster than `collections.abc.Mapping` by fractions of seconds).

So basically to make it simple to you if you are new to Python, the same operations and methods from Python standard `dict` type will all work with class `AttributesHandler` except the ones that try to modify the actual data.

If you want to modify the data inside `AttributesHandler`, you have to convert it to dictionary first like with using the `dict` function and modify it outside.