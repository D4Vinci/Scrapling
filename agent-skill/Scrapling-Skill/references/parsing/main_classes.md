# Parsing main classes

The [Selector](#selector) class is the core parsing engine in Scrapling, providing HTML parsing and element selection capabilities. You can always import it with any of the following imports
```python
from scrapling import Selector
from scrapling.parser import Selector
```
Usage:
```python
page = Selector(
    '<html>...</html>',
    url='https://example.com'
)

# Then select elements as you like
elements = page.css('.product')
```
In Scrapling, the main object you deal with after passing an HTML source or fetching a website is, of course, a [Selector](#selector) object. Any operation you do, like selection, navigation, etc., will return either a [Selector](#selector) object or a [Selectors](#selectors) object, given that the result is element/elements from the page, not text or similar.

The main page is a [Selector](#selector) object, and the elements within are [Selector](#selector) objects. Any text (text content inside elements or attribute values) is a [TextHandler](#texthandler) object, and element attributes are stored as [AttributesHandler](#attributeshandler).

## Selector
### Arguments explained
The most important one is `content`, it's used to pass the HTML code you want to parse, and it accepts the HTML content as `str` or `bytes`.

The arguments `url`, `adaptive`, `storage`, and `storage_args` are settings used with the `adaptive` feature. They are explained in the [adaptive](adaptive.md) feature page.

Arguments for parsing adjustments:

- **encoding**: This is the encoding that will be used while parsing the HTML. The default is `UTF-8`.
- **keep_comments**: This tells the library whether to keep HTML comments while parsing the page. It's disabled by default because it can cause issues with your scraping in various ways.
- **keep_cdata**: Same logic as the HTML comments. [cdata](https://stackoverflow.com/questions/7092236/what-is-cdata-in-html) is removed by default for cleaner HTML.

The arguments `huge_tree` and `root` are advanced features not covered here.

Most properties on the main page and its elements are lazily loaded (not initialized until accessed), which contributes to Scrapling's speed.

### Properties
Properties for traversal are separated in the [traversal](#traversal) section below.

Parsing this HTML page as an example:
```html
<html>
  <head>
    <title>Some page</title>
  </head>
  <body>
    <div class="product-list">
      <article class="product" data-id="1">
        <h3>Product 1</h3>
        <p class="description">This is product 1</p>
        <span class="price">$10.99</span>
        <div class="hidden stock">In stock: 5</div>
      </article>
    
      <article class="product" data-id="2">
        <h3>Product 2</h3>
        <p class="description">This is product 2</p>
        <span class="price">$20.99</span>
        <div class="hidden stock">In stock: 3</div>
      </article>
    
      <article class="product" data-id="3">
        <h3>Product 3</h3>
        <p class="description">This is product 3</p>
        <span class="price">$15.99</span>
        <div class="hidden stock">Out of stock</div>
      </article>
    </div>

    <script id="page-data" type="application/json">
      {
        "lastUpdated": "2024-09-22T10:30:00Z",
        "totalProducts": 3
      }
    </script>
  </body>
</html>
```
Load the page directly as shown before:
```python
from scrapling import Selector
page = Selector(html_doc)
```
Get all text content on the page recursively
```python
>>> page.get_all_text()
'Some page\n\n    \n\n      \nProduct 1\nThis is product 1\n$10.99\nIn stock: 5\nProduct 2\nThis is product 2\n$20.99\nIn stock: 3\nProduct 3\nThis is product 3\n$15.99\nOut of stock'
```
Get the first article (used as an example throughout):
```python
article = page.find('article')
```
With the same logic, get all text content on the element recursively
```python
>>> article.get_all_text()
'Product 1\nThis is product 1\n$10.99\nIn stock: 5'
```
But if you try to get the direct text content, it will be empty because it doesn't have direct text in the HTML code above
```python
>>> article.text
''
```
The `get_all_text` method has the following optional arguments:

1. **separator**: All strings collected will be concatenated using this separator. The default is '\n'.
2. **strip**: If enabled, strings will be stripped before concatenation. Disabled by default.
3. **ignore_tags**: A tuple of all tag names you want to ignore in the final results and ignore any elements nested within them. The default is `('script', 'style',)`.
4. **valid_values**: If enabled, the method will only collect elements with real values, so all elements with empty text content or only whitespaces will be ignored. It's enabled by default

The text returned is a [TextHandler](#texthandler), not a standard string. If the text content can be serialized to JSON, use `.json()` on it:
```python
>>> script = page.find('script')
>>> script.json()
{'lastUpdated': '2024-09-22T10:30:00Z', 'totalProducts': 3}
```
Let's continue to get the element tag
```python
>>> article.tag
'article'
```
Using it on the page directly operates on the root `html` element:
```python
>>> page.tag
'html'
```
Getting the attributes of the element
```python
>>> print(article.attrib)
{'class': 'product', 'data-id': '1'}
```
Access a specific attribute with any of the following
```python
>>> article.attrib['class']
>>> article.attrib.get('class')
>>> article['class']  # new in v0.3
```
Check if the attributes contain a specific attribute with any of the methods below
```python
>>> 'class' in article.attrib
>>> 'class' in article  # new in v0.3
```
Get the HTML content of the element
```python
>>> article.html_content
'<article class="product" data-id="1"><h3>Product 1</h3>\n        <p class="description">This is product 1</p>\n        <span class="price">$10.99</span>\n        <div class="hidden stock">In stock: 5</div>\n      </article>'
```
Get the prettified version of the element's HTML content
```python
print(article.prettify())
```
```html
<article class="product" data-id="1"><h3>Product 1</h3>
    <p class="description">This is product 1</p>
    <span class="price">$10.99</span>
    <div class="hidden stock">In stock: 5</div>
</article>
```
Use the `.body` property to get the raw content of the page. Starting from v0.4, when used on a `Response` object from fetchers, `.body` always returns `bytes`.
```python
>>> page.body
'<html>\n  <head>\n    <title>Some page</title>\n  </head>\n  ...'
```
To get all the ancestors in the DOM tree of this element
```python
>>> article.path
[<data='<div class="product-list"> <article clas...' parent='<body> <div class="product-list"> <artic...'>,
 <data='<body> <div class="product-list"> <artic...' parent='<html><head><title>Some page</title></he...'>,
 <data='<html><head><title>Some page</title></he...'>]
```
Generate a CSS shortened selector if possible, or generate the full selector
```python
>>> article.generate_css_selector
'body > div > article'
>>> article.generate_full_css_selector
'body > div > article'
```
Same case with XPath
```python
>>> article.generate_xpath_selector
"//body/div/article"
>>> article.generate_full_xpath_selector
"//body/div/article"
```

### Traversal
Properties and methods for navigating elements on the page.

The `html` element is the root of the website's tree. Elements like `head` and `body` are "children" of `html`, and `html` is their "parent". The element `body` is a "sibling" of `head` and vice versa.

Accessing the parent of an element
```python
>>> article.parent
<data='<div class="product-list"> <article clas...' parent='<body> <div class="product-list"> <artic...'>
>>> article.parent.tag
'div'
```
Chaining is supported, as with all similar properties/methods:
```python
>>> article.parent.parent.tag
'body'
```
Get the children of an element
```python
>>> article.children
[<data='<h3>Product 1</h3>' parent='<article class="product" data-id="1"><h3...'>,
 <data='<p class="description">This is product 1...' parent='<article class="product" data-id="1"><h3...'>,
 <data='<span class="price">$10.99</span>' parent='<article class="product" data-id="1"><h3...'>,
 <data='<div class="hidden stock">In stock: 5</d...' parent='<article class="product" data-id="1"><h3...'>]
```
Get all elements underneath an element. It acts as a nested version of the `children` property
```python
>>> article.below_elements
[<data='<h3>Product 1</h3>' parent='<article class="product" data-id="1"><h3...'>,
 <data='<p class="description">This is product 1...' parent='<article class="product" data-id="1"><h3...'>,
 <data='<span class="price">$10.99</span>' parent='<article class="product" data-id="1"><h3...'>,
 <data='<div class="hidden stock">In stock: 5</d...' parent='<article class="product" data-id="1"><h3...'>]
```
This element returns the same result as the `children` property because its children don't have children.

Another example of using the element with the `product-list` class will clear the difference between the `children` property and the `below_elements` property
```python
>>> products_list = page.css('.product-list')[0]
>>> products_list.children
[<data='<article class="product" data-id="1"><h3...' parent='<div class="product-list"> <article clas...'>,
 <data='<article class="product" data-id="2"><h3...' parent='<div class="product-list"> <article clas...'>,
 <data='<article class="product" data-id="3"><h3...' parent='<div class="product-list"> <article clas...'>]

>>> products_list.below_elements
[<data='<article class="product" data-id="1"><h3...' parent='<div class="product-list"> <article clas...'>,
 <data='<h3>Product 1</h3>' parent='<article class="product" data-id="1"><h3...'>,
 <data='<p class="description">This is product 1...' parent='<article class="product" data-id="1"><h3...'>,
 <data='<span class="price">$10.99</span>' parent='<article class="product" data-id="1"><h3...'>,
 <data='<div class="hidden stock">In stock: 5</d...' parent='<article class="product" data-id="1"><h3...'>,
 <data='<article class="product" data-id="2"><h3...' parent='<div class="product-list"> <article clas...'>,
...]
```
Get the siblings of an element
```python
>>> article.siblings
[<data='<article class="product" data-id="2"><h3...' parent='<div class="product-list"> <article clas...'>,
 <data='<article class="product" data-id="3"><h3...' parent='<div class="product-list"> <article clas...'>]
```
Get the next element of the current element
```python
>>> article.next
<data='<article class="product" data-id="2"><h3...' parent='<div class="product-list"> <article clas...'>
```
The same logic applies to the `previous` property
```python
>>> article.previous  # It's the first child, so it doesn't have a previous element
>>> second_article = page.css('.product[data-id="2"]')[0]
>>> second_article.previous
<data='<article class="product" data-id="1"><h3...' parent='<div class="product-list"> <article clas...'>
```
Check if an element has a specific class name:
```python
>>> article.has_class('product')
True
```
Iterate over the entire ancestors' tree of any element:
```python
for ancestor in article.iterancestors():
    # do something with it...
```
Search for a specific ancestor that satisfies a search function. Pass a function that takes a [Selector](#selector) object as an argument and returns `True`/`False`:
```python
>>> article.find_ancestor(lambda ancestor: ancestor.has_class('product-list'))
<data='<div class="product-list"> <article clas...' parent='<body> <div class="product-list"> <artic...'>

>>> article.find_ancestor(lambda ancestor: ancestor.css('.product-list'))  # Same result, different approach
<data='<div class="product-list"> <article clas...' parent='<body> <div class="product-list"> <artic...'>
```
## Selectors
The class `Selectors` is the "List" version of the [Selector](#selector) class. It inherits from the Python standard `List` type, so it shares all `List` properties and methods while adding more methods to make the operations you want to execute on the [Selector](#selector) instances within more straightforward.

In the [Selector](#selector) class, all methods/properties that should return a group of elements return them as a [Selectors](#selectors) class instance.

Starting with v0.4, all selection methods consistently return [Selector](#selector)/[Selectors](#selectors) objects, even for text nodes and attribute values. Text nodes (selected via `::text`, `/text()`, `::attr()`, `/@attr`) are wrapped in [Selector](#selector) objects. These text node selectors have `tag` set to `"#text"`, and their `text` property returns the text value. You can still access the text value directly, and all other properties return empty/default values gracefully.

```python
>>> page.css('a::text')              # -> Selectors (of text node Selectors)
>>> page.xpath('//a/text()')         # -> Selectors
>>> page.css('a::text').get()        # -> TextHandler (the first text value)
>>> page.css('a::text').getall()     # -> TextHandlers (all text values)
>>> page.css('a::attr(href)')        # -> Selectors
>>> page.xpath('//a/@href')          # -> Selectors
>>> page.css('.price_color')         # -> Selectors
```

### Data extraction methods
Starting with v0.4, [Selector](#selector) and [Selectors](#selectors) both provide `get()`, `getall()`, and their aliases `extract_first` and `extract` (following Scrapy conventions). The old `get_all()` method has been removed.

**On a [Selector](#selector) object:**

- `get()` returns a `TextHandler` — for text node selectors, it returns the text value; for HTML element selectors, it returns the serialized outer HTML.
- `getall()` returns a `TextHandlers` list containing the single serialized string.
- `extract_first` is an alias for `get()`, and `extract` is an alias for `getall()`.

```python
>>> page.css('h3')[0].get()        # Outer HTML of the element
'<h3>Product 1</h3>'

>>> page.css('h3::text')[0].get()  # Text value of the text node
'Product 1'
```

**On a [Selectors](#selectors) object:**

- `get(default=None)` returns the serialized string of the **first** element, or `default` if the list is empty.
- `getall()` serializes **all** elements and returns a `TextHandlers` list.
- `extract_first` is an alias for `get()`, and `extract` is an alias for `getall()`.

```python
>>> page.css('.price::text').get()      # First price text
'$10.99'

>>> page.css('.price::text').getall()   # All price texts
['$10.99', '$20.99', '$15.99']

>>> page.css('.price::text').get('')    # With default value
'$10.99'
```

These methods work seamlessly with all selection types (CSS, XPath, `find`, etc.) and are the recommended way to extract text and attribute values in a Scrapy-compatible style.

### Properties
Apart from the standard operations on Python lists (iteration, slicing, etc.), the following operations are available:

CSS and XPath selectors can be executed directly on the [Selector](#selector) instances, with the same return types as [Selector](#selector)'s `css` and `xpath` methods. The arguments are similar, except the `adaptive` argument is not available. This makes chaining methods straightforward:
```python
>>> page.css('.product_pod a')
[<data='<a href="catalogue/a-light-in-the-attic_...' parent='<div class="image_container"> <a href="c...'>,
 <data='<a href="catalogue/a-light-in-the-attic_...' parent='<h3><a href="catalogue/a-light-in-the-at...'>,
 <data='<a href="catalogue/tipping-the-velvet_99...' parent='<div class="image_container"> <a href="c...'>,
 <data='<a href="catalogue/tipping-the-velvet_99...' parent='<h3><a href="catalogue/tipping-the-velve...'>,
 <data='<a href="catalogue/soumission_998/index....' parent='<div class="image_container"> <a href="c...'>,
 <data='<a href="catalogue/soumission_998/index....' parent='<h3><a href="catalogue/soumission_998/in...'>,
...]

>>> page.css('.product_pod').css('a')  # Returns the same result
[<data='<a href="catalogue/a-light-in-the-attic_...' parent='<div class="image_container"> <a href="c...'>,
 <data='<a href="catalogue/a-light-in-the-attic_...' parent='<h3><a href="catalogue/a-light-in-the-at...'>,
 <data='<a href="catalogue/tipping-the-velvet_99...' parent='<div class="image_container"> <a href="c...'>,
 <data='<a href="catalogue/tipping-the-velvet_99...' parent='<h3><a href="catalogue/tipping-the-velve...'>,
 <data='<a href="catalogue/soumission_998/index....' parent='<div class="image_container"> <a href="c...'>,
 <data='<a href="catalogue/soumission_998/index....' parent='<h3><a href="catalogue/soumission_998/in...'>,
...]
```
The `re` and `re_first` methods can be run directly. They take the same arguments as the [Selector](#selector) class. In this class, `re_first` runs `re` on each [Selector](#selector) within and returns the first one with a result. The `re` method returns a [TextHandlers](#texthandlers) object combining all matches:
```python
>>> page.css('.price_color').re(r'[\d\.]+')
['51.77',
 '53.74',
 '50.10',
 '47.82',
 '54.23',
...]

>>> page.css('.product_pod h3 a::attr(href)').re(r'catalogue/(.*)/index.html')
['a-light-in-the-attic_1000',
 'tipping-the-velvet_999',
 'soumission_998',
 'sharp-objects_997',
...]
```
The `search` method searches the available [Selector](#selector) instances. The function passed must accept a [Selector](#selector) instance as the first argument and return True/False. Returns the first matching [Selector](#selector) instance, or `None`:
```python
# Find all the products with price '53.23'.
>>> search_function = lambda p: float(p.css('.price_color').re_first(r'[\d\.]+')) == 54.23
>>> page.css('.product_pod').search(search_function)
<data='<article class="product_pod"><div class=...' parent='<li class="col-xs-6 col-sm-4 col-md-3 co...'>
```
The `filter` method takes a function like `search` but returns a `Selectors` instance of all matching [Selector](#selector) instances:
```python
# Find all products with prices over $50
>>> filtering_function = lambda p: float(p.css('.price_color').re_first(r'[\d\.]+')) > 50
>>> page.css('.product_pod').filter(filtering_function)
[<data='<article class="product_pod"><div class=...' parent='<li class="col-xs-6 col-sm-4 col-md-3 co...'>,
 <data='<article class="product_pod"><div class=...' parent='<li class="col-xs-6 col-sm-4 col-md-3 co...'>,
 <data='<article class="product_pod"><div class=...' parent='<li class="col-xs-6 col-sm-4 col-md-3 co...'>,
...]
```
Safe access to the first or last element without index errors:
```python
>>> page.css('.product').first   # First Selector or None
<data='<article class="product" data-id="1"><h3...'>
>>> page.css('.product').last    # Last Selector or None
<data='<article class="product" data-id="3"><h3...'>
>>> page.css('.nonexistent').first  # Returns None instead of raising IndexError
```

Get the number of [Selector](#selector) instances in a [Selectors](#selectors) instance:
```python
page.css('.product_pod').length
```
which is equivalent to
```python
len(page.css('.product_pod'))
```

## TextHandler
All methods/properties that return a string return `TextHandler`, and those that return a list of strings return [TextHandlers](#texthandlers) instead.

TextHandler is a subclass of the standard Python string, so all standard string operations are supported.

TextHandler provides extra methods and properties beyond standard Python strings. All methods and properties in all classes that return string(s) return TextHandler, enabling chaining and cleaner code. It can also be imported directly and used on any string.
### Usage
All operations (slicing, indexing, etc.) and methods (`split`, `replace`, `strip`, etc.) return a `TextHandler`, so they can be chained.

The `re` and `re_first` methods exist in [Selector](#selector), [Selectors](#selectors), and [TextHandlers](#texthandlers) as well, accepting the same arguments.

- The `re` method takes a string/compiled regex pattern as the first argument. It searches the data for all strings matching the regex and returns them as a [TextHandlers](#texthandlers) instance. The `re_first` method takes the same arguments but returns only the first result as a `TextHandler` instance.
    
    Also, it takes other helpful arguments, which are:
    
    - **replace_entities**: This is enabled by default. It replaces character entity references with their corresponding characters.
    - **clean_match**: It's disabled by default. This causes the method to ignore all whitespace, including consecutive spaces, while matching.
    - **case_sensitive**: It's enabled by default. As the name implies, disabling it causes the regex to ignore letter case during compilation.
  
    The return result is [TextHandlers](#texthandlers) because the `re` method is used:
    ```python
    >>> page.css('.price_color').re(r'[\d\.]+')
    ['51.77',
     '53.74',
     '50.10',
     '47.82',
     '54.23',
    ...]
    
    >>> page.css('.product_pod h3 a::attr(href)').re(r'catalogue/(.*)/index.html')
    ['a-light-in-the-attic_1000',
     'tipping-the-velvet_999',
     'soumission_998',
     'sharp-objects_997',
    ...]
    ```
    Examples with custom strings demonstrating the other arguments:
    ```python
    >>> from scrapling import TextHandler
    >>> test_string = TextHandler('hi  there')  # Hence the two spaces
    >>> test_string.re('hi there')
    >>> test_string.re('hi there', clean_match=True)  # Using `clean_match` will clean the string before matching the regex
    ['hi there']
    
    >>> test_string2 = TextHandler('Oh, Hi Mark')
    >>> test_string2.re_first('oh, hi Mark')
    >>> test_string2.re_first('oh, hi Mark', case_sensitive=False)  # Hence disabling `case_sensitive`
    'Oh, Hi Mark'
    
    # Mixing arguments
    >>> test_string.re('hi there', clean_match=True, case_sensitive=False)
    ['hi There']
    ```
    Since `html_content` returns `TextHandler`, regex can be applied directly on HTML content:
    ```python
    >>> page.html_content.re('div class=".*">(.*)</div')
    ['In stock: 5', 'In stock: 3', 'Out of stock']
    ```

- The `.json()` method converts the content to a JSON object if possible; otherwise, it throws an error:
  ```python
  >>> page.css('#page-data::text').get()
    '\n      {\n        "lastUpdated": "2024-09-22T10:30:00Z",\n        "totalProducts": 3\n      }\n    '
  >>> page.css('#page-data::text').get().json()
    {'lastUpdated': '2024-09-22T10:30:00Z', 'totalProducts': 3}
  ```
  If no text node is specified while selecting an element, the text content is selected automatically:
  ```python
  >>> page.css('#page-data')[0].json()
  {'lastUpdated': '2024-09-22T10:30:00Z', 'totalProducts': 3}
  ```
  The [Selector](#selector) class adds additional behavior. Given this page:
  ```html
  <html>
      <body>
          <div>
            <script id="page-data" type="application/json">
              {
                "lastUpdated": "2024-09-22T10:30:00Z",
                "totalProducts": 3
              }
            </script>
          </div>
      </body>
  </html>
  ```
  The [Selector](#selector) class has the `get_all_text` method, which returns a `TextHandler`. For example:
  ```python
  >>> page.css('div::text').get().json()
  ```
  This throws an error because the `div` tag has no direct text content. The `get_all_text` method handles this case:
  ```python
  >>> page.css('div')[0].get_all_text(ignore_tags=[]).json()
    {'lastUpdated': '2024-09-22T10:30:00Z', 'totalProducts': 3}
  ```
  The `ignore_tags` argument is used here because its default value is `('script', 'style',)`.

  When dealing with a JSON response:
  ```python
  >>> page = Selector("""{"some_key": "some_value"}""")
  ```
  The [Selector](#selector) class is optimized for HTML, so it treats this as a broken HTML response and wraps it. The `html_content` property shows:
  ```python
  >>> page.html_content
  '<html><body><p>{"some_key": "some_value"}</p></body></html>'
  ```
  The `json` method can be used directly:
  ```python
  >>> page.json()
  {'some_key': 'some_value'}
  ```
  For JSON responses, the [Selector](#selector) class keeps a raw copy of the content it receives. When `.json()` is called, it checks for that raw copy first and converts it to JSON. If the raw copy is unavailable (as with sub-elements), it checks the current element's text content, then falls back to `get_all_text`.

- The `.clean()` method removes all whitespace and consecutive spaces, returning a new `TextHandler` instance:
```python
>>> TextHandler('\n wonderful  idea, \reh?').clean()
'wonderful idea, eh?'
```
The `remove_entities` argument causes `clean` to replace HTML entities with their corresponding characters.

- The `.sort()` method sorts the string characters:
```python
>>> TextHandler('acb').sort()
'abc'
```
Or do it in reverse:
```python
>>> TextHandler('acb').sort(reverse=True)
'cba'
```

This class is returned in place of strings nearly everywhere in the library.

## TextHandlers
This class inherits from standard lists, adding `re` and `re_first` as new methods.

The `re_first` method runs `re` on each [TextHandler](#texthandler) and returns the first result, or `None`.

## AttributesHandler
This is a read-only version of Python's standard dictionary, or `dict`, used solely to store the attributes of each element/[Selector](#selector) instance.
```python
>>> print(page.find('script').attrib)
{'id': 'page-data', 'type': 'application/json'}
>>> type(page.find('script').attrib).__name__
'AttributesHandler'
```
Because it's read-only, it will use fewer resources than the standard dictionary. Still, it has the same dictionary method and properties, except those that allow you to modify/override the data.

It currently adds two extra simple methods:

- The `search_values` method

    Searches the current attributes by values (rather than keys) and returns a dictionary of each matching item.
    
    A simple example would be
    ```python
    >>> for i in page.find('script').attrib.search_values('page-data'):
            print(i)
    {'id': 'page-data'}
    ```
    But this method provides the `partial` argument as well, which allows you to search by part of the value:
    ```python
    >>> for i in page.find('script').attrib.search_values('page', partial=True):
            print(i)
    {'id': 'page-data'}
    ```
    A more practical example is using it with `find_all` to find all elements that have a specific value in their attributes:
    ```python
    >>> page.find_all(lambda element: list(element.attrib.search_values('product')))
    [<data='<article class="product" data-id="1"><h3...' parent='<div class="product-list"> <article clas...'>,
     <data='<article class="product" data-id="2"><h3...' parent='<div class="product-list"> <article clas...'>,
     <data='<article class="product" data-id="3"><h3...' parent='<div class="product-list"> <article clas...'>]
    ```
    All these elements have 'product' as the value for the `class` attribute.
    
    The `list` function is used here because `search_values` returns a generator, so it would be `True` for all elements.

- The `json_string` property

    This property converts current attributes to a JSON string if the attributes are JSON serializable; otherwise, it throws an error.
  
    ```python
    >>>page.find('script').attrib.json_string
    b'{"id":"page-data","type":"application/json"}'
    ```