Scrapling by default is using SQLite but in case you want to write your storage system to store elements properties there for the auto-matching, this tutorial got you covered.

You might want to use FireBase for example and share the database between multiple spiders on different machines, it's a great idea to use an online database like that because this way the spiders will share with each others.

So first to make your storage class work, it must do the big 3:
1. Inherit from the abstract class `scrapling.storage_adaptors.StorageSystemMixin` and accept a string argument which will be the `url` argument to maintain the library logic.
2. Use the decorator `functools.lru_cache` on top of the class itself to follow the Singleton design pattern as other classes.
3. Implement methods `save` and `retrieve`, as you see from the type hints:
   - The method `save` returns nothing and will get two arguments from the library
        * The first one is of type `lxml.html.HtmlElement` which is the element itself, ofc. It must be converted to dictionary using the function `scrapling.utils._StorageTools.element_to_dict` so we keep the same format then saved to your database as you wish.
        * The second one is string which is the identifier used for retrieval. The combination of this identifier and the `url` argument from initialization must be unique for each row or the auto-match will be messed up.
   - The method `retrieve` takes a string which is the identifier, using it with the `url` passed on initialization the element's dictionary is retrieved from the database and returned if it exist otherwise it returns `None`
> If the instructions weren't clear enough for you, you can check my implementation using SQLite3 in [storage_adaptors](/scrapling/storage_adaptors.py) file

If your class satisfy this, the rest is easy. If you are planning to use the library in a threaded application, make sure that your class supports it. The default used class is thread-safe.

There are some helper functions added to the abstract class if you want to use it. It's easier to see it for yourself in the [code](/scrapling/storage_adaptors.py), it's heavily commented :)
