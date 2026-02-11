## Introduction

!!! success "Prerequisites"

    - You’ve completed or read the [Querying elements](../parsing/selection.md) page to understand how to find/extract elements from the [Selector](../parsing/main_classes.md#selector) object.

After exploring the various ways to select elements with Scrapling and its related features, let's take a step back and examine the [Selector](#selector) class in general, as well as other objects, to gain a better understanding of the parsing engine.

The [Selector](#selector) class is the core parsing engine in Scrapling, providing HTML parsing and element selection capabilities. You can always import it with any of the following imports
```python
from scrapling import Selector
from scrapling.parser import Selector
```
Then use it directly as you already learned in the [overview](../overview.md) page
```python
page = Selector(
    '<html>...</html>',
    url='https://example.com'
)

# Then select elements as you like
elements = page.css('.product')
```
In Scrapling, the main object you deal with after passing an HTML source or fetching a website is, of course, a [Selector](#selector) object. Any operation you do, like selection, navigation, etc., will return either a [Selector](#selector) object or a [Selectors](#selectors) object, given that the result is element/elements from the page, not text or similar.

In other words, the main page is a [Selector](#selector) object, and the elements within are [Selector](#selector) objects, and so on. Any text, such as the text content inside elements or the text inside element attributes, is a [TextHandler](#texthandler) object, and the attributes of each element are stored as [AttributesHandler](#attributeshandler). We will return to both objects later, so let's focus on the [Selector](#selector) object.

## Selector
### Arguments explained
The most important one is `content`, it's used to pass the HTML code you want to parse, and it accepts the HTML content as `str` or `bytes`.

Otherwise, you have the arguments `url`, `adaptive`, `storage`, and `storage_args`. All these arguments are settings used with the `adaptive` feature, and they don't make a difference if you are not going to use that feature, so just ignore them for now, and we will explain them in the [adaptive](adaptive.md) feature page.

Then you have the arguments for parsing adjustments or adjusting/manipulating the HTML content while the library is parsing it:

- **encoding**: This is the encoding that will be used while parsing the HTML. The default is `UTF-8`.
- **keep_comments**: This tells the library whether to keep HTML comments while parsing the page. It's disabled by default because it can cause issues with your scraping in various ways.
- **keep_cdata**: Same logic as the HTML comments. [cdata](https://stackoverflow.com/questions/7092236/what-is-cdata-in-html) is removed by default for cleaner HTML.

I have intended to ignore the arguments `huge_tree` and `root` to avoid making this page more complicated than needed.
You may notice that I'm doing that a lot because it involves advanced features that you don't need to know to use the library. The development section will cover these missing parts if you are very invested.

After that, most properties on the main page and its elements are lazily loaded. This means they don't get initialized until you use them like the text content of a page/element, and this is one of the reasons for Scrapling speed :)

### Properties
You have already seen much of this on the [overview](../overview.md) page, but don't worry if you didn't. We will review it more thoroughly using more advanced methods/usages. For clarity, the properties for traversal are separated below in the [traversal](#traversal) section.

Let's say we are parsing this HTML page for simplicity:
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
Get the first article, as explained before; we will use it as an example
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

By the way, the text returned here is not a standard string but a [TextHandler](#texthandler); we will get to this in detail later, so if the text content can be serialized to JSON, use `.json()` on it
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
If you use it on the page directly, you will find that you are operating on the root `html` element
```python
>>> page.tag
'html'
```
Now, I think I've hammered the (`page`/`element`) idea, so I won't return to it.

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
Using the elements we found above, we will go over the properties/methods for moving on the page in detail.

If you are unfamiliar with the DOM tree or the tree data structure in general, the following traversal part can be confusing. I recommend you look up these concepts online to better understand them.

If you are too lazy to search about it, here's a quick explanation to give you a good idea.<br/>
In simple words, the `html` element is the root of the website's tree, as every page starts with an `html` element.<br/>
This element will be positioned directly above elements such as `head` and `body`. These are considered "children" of the `html` element, and the `html` element is considered their "parent". The element `body` is a "sibling" of the element `head` and vice versa.

Accessing the parent of an element
```python
>>> article.parent
<data='<div class="product-list"> <article clas...' parent='<body> <div class="product-list"> <artic...'>
>>> article.parent.tag
'div'
```
You can chain it as you want, which applies to all similar properties/methods we will review.
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
You can check easily and pretty fast if an element has a specific class name or not
```python
>>> article.has_class('product')
True
```
If your case needs more than the element's parent, you can iterate over the whole ancestors' tree of any element, like the example below
```python
for ancestor in article.iterancestors():
    # do something with it...
```
You can search for a specific ancestor of an element that satisfies a search function; all you need to do is pass a function that takes a [Selector](#selector) object as an argument and return `True` if the condition satisfies or `False` otherwise, like below:
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

Now, let's see what [Selectors](#selectors) class adds to the table with that out of the way.
### Properties
Apart from the standard operations on Python lists, such as iteration and slicing.

You can do the following:

Execute CSS and XPath selectors directly on the [Selector](#selector) instances it has, while the arguments and the return types are the same as [Selector](#selector)'s `css` and `xpath` methods. This, of course, makes chaining methods very straightforward.
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
Run the `re` and `re_first` methods directly. They take the same arguments passed to the [Selector](#selector) class. I will leave the explanation of these methods to the [TextHandler](#texthandler) section below.

However, in this class, the `re_first` behaves differently as it runs `re` on each [Selector](#selector) within and returns the first one with a result. The `re` method will return a [TextHandlers](#texthandlers) object as normal, which combines all the [TextHandler](#texthandler) instances into one [TextHandlers](#texthandlers) instance.
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
With the `search` method, you can search quickly in the available [Selector](#selector) instances. The function you pass must accept a [Selector](#selector) instance as the first argument and return True/False. The method will return the first [Selector](#selector) instance that satisfies the function; otherwise, it will return `None`.
```python
# Find all the products with price '53.23'.
>>> search_function = lambda p: float(p.css('.price_color').re_first(r'[\d\.]+')) == 54.23
>>> page.css('.product_pod').search(search_function)
<data='<article class="product_pod"><div class=...' parent='<li class="col-xs-6 col-sm-4 col-md-3 co...'>
```
You can use the `filter` method, too, which takes a function like the `search` method but returns an `Selectors` instance of all the [Selector](#selector) instances that satisfy the function
```python
# Find all products with prices over $50
>>> filtering_function = lambda p: float(p.css('.price_color').re_first(r'[\d\.]+')) > 50
>>> page.css('.product_pod').filter(filtering_function)
[<data='<article class="product_pod"><div class=...' parent='<li class="col-xs-6 col-sm-4 col-md-3 co...'>,
 <data='<article class="product_pod"><div class=...' parent='<li class="col-xs-6 col-sm-4 col-md-3 co...'>,
 <data='<article class="product_pod"><div class=...' parent='<li class="col-xs-6 col-sm-4 col-md-3 co...'>,
...]
```
You can safely access the first or last element without worrying about index errors:
```python
>>> page.css('.product').first   # First Selector or None
<data='<article class="product" data-id="1"><h3...'>
>>> page.css('.product').last    # Last Selector or None
<data='<article class="product" data-id="3"><h3...'>
>>> page.css('.nonexistent').first  # Returns None instead of raising IndexError
```

If you are too lazy like me and want to know the number of [Selector](#selector) instances in a [Selectors](#selectors) instance. You can do this:
```python
page.css('.product_pod').length
```
which is equivalent to
```python
len(page.css('.product_pod'))
```
Yup, like JavaScript :)

## TextHandler
This class is mandatory to understand, as all methods/properties that should return a string for you will return `TextHandler`, and the ones that should return a list of strings will return [TextHandlers](#texthandlers) instead.

TextHandler is a subclass of the standard Python string, so you can do anything with it that you can do with a Python string. So, what is the difference that requires a different naming?

Of course, TextHandler provides extra methods and properties that standard Python strings can't do. We will review them now, but remember that all methods and properties in all classes that return string(s) return TextHandler, which opens the door for creativity and makes the code shorter and cleaner, as you will see. Also, you can import it directly and use it on any string, which we will explain [later](../development/scrapling_custom_types.md).
### Usage
First, before discussing the added methods, you need to know that all operations on it, like slicing, accessing by index, etc., and methods like `split`, `replace`, `strip`, etc., all return a `TextHandler` again, so you can chain them as you want. If you find a method or property that returns a standard string instead of `TextHandler`, please open an issue, and we will override it as well.

First, we start with the `re` and `re_first` methods. These are the same methods that exist in the other classes ([Selector](#selector), [Selectors](#selectors), and [TextHandlers](#texthandlers)), so they accept the same arguments.

- The `re` method takes a string/compiled regex pattern as the first argument. It searches the data for all strings matching the regex and returns them as a [TextHandlers](#texthandlers) instance. The `re_first` method takes the same arguments and behaves similarly, but, as you probably figured out from the name, it returns only the first result as a `TextHandler` instance.
    
    Also, it takes other helpful arguments, which are:
    
    - **replace_entities**: This is enabled by default. It replaces character entity references with their corresponding characters.
    - **clean_match**: It's disabled by default. This causes the method to ignore all whitespace, including consecutive spaces, while matching.
    - **case_sensitive**: It's enabled by default. As the name implies, disabling it causes the regex to ignore letter case during compilation.
  
    You have seen these examples before; the return result is [TextHandlers](#texthandlers) because we used the `re` method.
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
    To explain the other arguments better, we will use a custom string for each example below
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
    Another use of the idea of replacing strings with `TextHandler` everywhere is that a property like `html_content` returns `TextHandler`, so you can do regex on the HTML content if you want:
    ```python
    >>> page.html_content.re('div class=".*">(.*)</div')
    ['In stock: 5', 'In stock: 3', 'Out of stock']
    ```

- You also have the `.json()` method, which tries to convert the content to a JSON object quickly if possible; otherwise, it throws an error
  ```python
  >>> page.css('#page-data::text').get()
    '\n      {\n        "lastUpdated": "2024-09-22T10:30:00Z",\n        "totalProducts": 3\n      }\n    '
  >>> page.css('#page-data::text').get().json()
    {'lastUpdated': '2024-09-22T10:30:00Z', 'totalProducts': 3}
  ```
  Hence, if you didn't specify a text node while selecting an element (like the text content or an attribute text content), the text content will be selected automatically, like this
  ```python
  >>> page.css('#page-data')[0].json()
  {'lastUpdated': '2024-09-22T10:30:00Z', 'totalProducts': 3}
  ```
  The [Selector](#selector) class adds one thing here, too; let's say this is the page we are working with:
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
  The [Selector](#selector) class has the `get_all_text` method, which you should be aware of by now. This method returns a `TextHandler`, of course.<br/><br/>
  So, as you know here, if you did something like this
  ```python
  >>> page.css('div::text').get().json()
  ```
  You will get an error because the `div` tag doesn't have any direct text content that can be serialized to JSON; it doesn't have any direct text content at all.<br/><br/>
  In this case, the `get_all_text` method comes to the rescue, so you can do something like that
  ```python
  >>> page.css('div')[0].get_all_text(ignore_tags=[]).json()
    {'lastUpdated': '2024-09-22T10:30:00Z', 'totalProducts': 3}
  ```
  I used the `ignore_tags` argument here because the default value of it is `('script', 'style',)`, as you are aware.<br/><br/>
  Another related behavior to be aware of occurs when using any fetcher, which we will explain later. If you have a JSON response like this example:
  ```python
  >>> page = Selector("""{"some_key": "some_value"}""")
  ```
  Because the [Selector](#selector) class is optimized to deal with HTML pages, it will deal with it as a broken HTML response and fix it, so if you used the `html_content` property, you get this
  ```python
  >>> page.html_content
  '<html><body><p>{"some_key": "some_value"}</p></body></html>'
  ```
  Here, you can use the `json` method directly, and it will work
  ```python
  >>> page.json()
  {'some_key': 'some_value'}
  ```
  You might wonder how this happened, given that the `html` tag doesn't contain direct text.<br/>
  Well, for cases like JSON responses, I made the [Selector](#selector) class keep a raw copy of the content it receives. This way, when you use the `.json()` method, it checks for that raw copy and then converts it to JSON. If the raw copy is unavailable, as with the elements, it checks the current element's text content; otherwise, it uses the `get_all_text` method directly.<br/>

- Another handy method is `.clean()`, which will remove all white spaces and consecutive spaces for you and return a new `TextHandler` instance
```python
>>> TextHandler('\n wonderful  idea, \reh?').clean()
'wonderful idea, eh?'
```
Also, you can pass the `remove_entities` argument to make `clean` replace HTML entities with their corresponding characters.

- Another method that might be helpful in some cases is the `.sort()` method to sort the string for you, as you do with lists
```python
>>> TextHandler('acb').sort()
'abc'
```
Or do it in reverse:
```python
>>> TextHandler('acb').sort(reverse=True)
'cba'
```

Other methods and properties will be added over time, but remember that this class is returned in place of strings nearly everywhere in the library.

## TextHandlers
You probably guessed it: This class is similar to [Selectors](#selectors) and [Selector](#selector), but here it inherits the same logic and method as standard lists, with only `re` and `re_first` as new methods.

The only difference is that the `re_first` method logic here runs `re` on each [TextHandler](#texthandler) and returns the first result, or `None`. Nothing new needs to be explained here, but new methods will be added over time.

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

    In standard dictionaries, you can do `dict.get("key_name")` to check if a key exists. However, if you want to search by values rather than keys, you will need some additional code lines. This method does that for you. It allows you to search the current attributes by values and returns a dictionary of each matching item.
    
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
    These examples won't happen in the real world; most likely, a more real-world example would be using it with the `find_all` method to find all elements that have a specific value in their arguments:
    ```python
    >>> page.find_all(lambda element: list(element.attrib.search_values('product')))
    [<data='<article class="product" data-id="1"><h3...' parent='<div class="product-list"> <article clas...'>,
     <data='<article class="product" data-id="2"><h3...' parent='<div class="product-list"> <article clas...'>,
     <data='<article class="product" data-id="3"><h3...' parent='<div class="product-list"> <article clas...'>]
    ```
    All these elements have 'product' as the value for the `class` attribute.
    
    Hence, I used the `list` function here because `search_values` returns a generator, so it would be `True` for all elements.

- The `json_string` property

    This property converts current attributes to a JSON string if the attributes are JSON serializable; otherwise, it throws an error.
  
    ```python
    >>>page.find('script').attrib.json_string
    b'{"id":"page-data","type":"application/json"}'
    ```