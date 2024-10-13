# 🕷️ Scrapling: Lightning-Fast, Adaptive Web Scraping for Python
[![PyPI version](https://badge.fury.io/py/scrapling.svg)](https://badge.fury.io/py/scrapling) [![Supported Python versions](https://img.shields.io/pypi/pyversions/scrapling.svg)](https://pypi.org/project/scrapling/) [![License](https://img.shields.io/badge/License-BSD--3-blue.svg)](https://opensource.org/licenses/BSD-3-Clause)

Dealing with failing web scrapers due to website changes? Meet Scrapling.

Scrapling is a high-performance, intelligent web scraping library for Python that automatically adapts to website changes while significantly outperforming popular alternatives. Whether you're a beginner or an expert, Scrapling provides powerful features while maintaining simplicity.

```python
from scrapling import Adaptor

# Scrape data that survives website changes
page = Adaptor(html, auto_match=True)
products = page.css('.product', auto_save=True)
# Later, even if selectors change:
products = page.css('.product', auto_match=True)  # Still finds them!
```

## Key Features

### Adaptive Scraping
- 🔄 **Smart Element Tracking**: Locate previously identified elements after website structure changes, using an intelligent similarity system and integrated storage.
- 🎯 **Flexible Querying**: Use CSS selectors, XPath, text search, or regex - chain them however you want!
- 🔍 **Find Similar Elements**: Automatically locate elements similar to the element you want on the page (Ex: other products like the product you found on the page).
- 🧠 **Smart Content Scraping**: Extract data from multiple websites without specific selectors using its powerful features.

### Performance
- 🚀 **Lightning Fast**: Built from the ground up with performance in mind, outperforming most popular Python scraping libraries (outperforming BeautifulSoup by up to 237x in our tests).
- 🔋 **Memory Efficient**: Optimized data structures for minimal memory footprint.
- ⚡ **Fast JSON serialization**: 10x faster JSON serialization than the standard json library with more options.

### Developing Experience
- 🛠️ **Powerful Navigation API**: Traverse the DOM tree easily in all directions and get the info you want (parent, ancestors, sibling, children, next/previous element, and more).
- 🧬 **Rich Text Processing**: All strings have built-in methods for regex matching, cleaning, and more. All elements' attributes are read-only dictionaries that are faster than standard dictionaries with added methods.
- 📝 **Automatic Selector Generation**: Create robust CSS/XPath selectors for any element.
- 🔌 **Scrapy-Compatible API**: Familiar methods and similar pseudo-elements for Scrapy users.
- 📘 **Type hints**: Complete type coverage for better IDE support and fewer bugs.

## Getting Started

Let's walk through a basic example that demonstrates small group of Scrapling's core features:

```python
import requests
from scrapling import Adaptor

# Fetch a web page
url = 'https://quotes.toscrape.com/'
response = requests.get(url)

# Create an Adaptor instance
page = Adaptor(response.text, url=url)
# Get all strings in the full page
page.get_all_text(ignore_tags=('script', 'style'))

# Get all quotes, any of these methods will return a list of strings (TextHandlers)
quotes = page.css('.quote .text::text')  # CSS selector
quotes = page.xpath('//span[@class="text"]/text()')  # XPath
quotes = page.css('.quote').css('.text::text')  # Chained selectors
quotes = [element.text for element in page.css('.quote').css('.text')]  # Slower than bulk query above

# Get the first quote element
quote = page.css('.quote').first  # or [0] or .get()

# Working with elements
quote.html_content  # Inner HTML
quote.prettify()  # Prettified version of Inner HTML
quote.attrib  # Element attributes
quote.path  # DOM path to element (List)
```
To keep it simple, all methods can be chained on top of each other as long as you are chaining methods that return an element (It's called an `Adaptor` object) or a List of Adaptors (It's called `Adaptors` object)

### Installation
Scrapling is a breeze to get started with - We only require at least Python 3.6 to work and the rest of the requirements are installed automatically with the package.
```bash
# Using pip
pip install scrapling

# Or the latest from GitHub
pip install git+https://github.com/D4Vinci/Scrapling.git@master
```

## Performance

Scrapling isn't just powerful - it's also blazing fast. Scrapling implements many best practices, design patterns, and numerous optimizations to save fractions of seconds. All of that while focusing exclusively on parsing HTML documents.
Here are benchmarks comparing Scrapling to popular Python libraries in two tests. 

### Text Extraction Speed Test (5000 nested elements).

| # |      Library      | Time (ms) | vs Scrapling | 
|---|:-----------------:|:---------:|:------------:|
| 1 |     Scrapling     |   5.44    |     1.0x     |
| 2 |   Parsel/Scrapy   |   5.53    |    1.017x    |
| 3 |     Raw Lxml      |   6.76    |    1.243x    |
| 4 |      PyQuery      |   21.96   |    4.037x    |
| 5 |    Selectolax     |   67.12   |   12.338x    |
| 6 |   BS4 with Lxml   |  1307.03  |   240.263x   |
| 7 |  MechanicalSoup   |  1322.64  |   243.132x   |
| 8 | BS4 with html5lib |  3373.75  |   620.175x   |

As you see, Scrapling is on par with Scrapy and slightly faster than Lxml which both libraries are built on top of. These are the closest results to Scrapling. PyQuery is also built on top of Lxml but still, Scrapling is 4 times faster.

### Extraction By Text Speed Test

|   Library   | Time (ms) | vs Scrapling |
|:-----------:|:---------:|:------------:|
|  Scrapling  |   2.51    |     1.0x     |
| AutoScraper |   11.41   |    4.546x    |

Scrapling can find elements with more methods and it returns full element `Adaptor` objects not only the text like AutoScraper. So, to make this test fair, both libraries will extract an element with text, find similar elements, and then extract the text content for all of them. As you see, Scrapling is still 4.5 times faster at same task.

> All benchmarks' results are an average of 100 runs. See our [benchmarks.py](/benchmarks.py) for methodology and to run your comparisons.

## Advanced Features
### Smart Navigation
```python
>>> quote.tag
'div'

>>> quote.parent
<data='<div class="col-md-8"> <div class="quote...' parent='<div class="row"> <div class="col-md-8">...'>

>>> quote.parent.tag
'div'

>>> quote.children
[<data='<span class="text" itemprop="text">“The...' parent='<div class="quote" itemscope itemtype="h...'>,
 <data='<span>by <small class="author" itemprop=...' parent='<div class="quote" itemscope itemtype="h...'>,
 <data='<div class="tags"> Tags: <meta class="ke...' parent='<div class="quote" itemscope itemtype="h...'>]

>>> quote.siblings
[<data='<div class="quote" itemscope itemtype="h...' parent='<div class="col-md-8"> <div class="quote...'>,
 <data='<div class="quote" itemscope itemtype="h...' parent='<div class="col-md-8"> <div class="quote...'>,
 <data='<div class="quote" itemscope itemtype="h...' parent='<div class="col-md-8"> <div class="quote...'>,
...]

>>> quote.next  # gets the next element, the same logic applies to `quote.previous`
<data='<div class="quote" itemscope itemtype="h...' parent='<div class="col-md-8"> <div class="quote...'>

>>> quote.children.css(".author::text")
['Albert Einstein']

>>> quote.has_class('quote')
True

# Generate new selectors for any element
>>> quote.css_selector
'body > div > div:nth-of-type(2) > div > div'

# Test these selectors on your favorite browser or reuse them again in the library in other methods!
>>> quote.xpath_selector
'//body/div/div[2]/div/div'
```
If your case needs more than the element's parent, you can iterate over the whole ancestors' tree of any element like below
```python
for ancestor in quote.iterancestors():
    # do something with it...
```
You can search for a specific ancestor of an element that satisfies a function, all you need to do is to pass a function that takes an `Adaptor` object as an argument and return `True` if the condition satisfies or `False` otherwise like below:
```python
>>> quote.find_ancestor(lambda ancestor: ancestor.has_class('row'))
<data='<div class="row"> <div class="col-md-8">...' parent='<div class="container"> <div class="row...'>
```

### Content-based Selection & Finding Similar Elements
You can select elements by their text content in multiple ways, here's a full example on another website:
```python
>>> response = requests.get('https://books.toscrape.com/index.html')

>>> page = Adaptor(response.text, url=response.url)

>>> page.find_by_text('Tipping the Velvet')  # Find the first element that its text fully matches this text
<data='<a href="catalogue/tipping-the-velvet_99...' parent='<h3><a href="catalogue/tipping-the-velve...'>

>>> page.find_by_text('Tipping the Velvet', first_match=False)  # Get all matches if there are more
[<data='<a href="catalogue/tipping-the-velvet_99...' parent='<h3><a href="catalogue/tipping-the-velve...'>]

>>> page.find_by_regex(r'£[\d\.]+')  # Get the first element that its text content matches my price regex
<data='<p class="price_color">£51.77</p>' parent='<div class="product_price"> <p class="pr...'>

>>> page.find_by_regex(r'£[\d\.]+', first_match=False)  # Get all elements that matches my price regex
[<data='<p class="price_color">£51.77</p>' parent='<div class="product_price"> <p class="pr...'>,
 <data='<p class="price_color">£53.74</p>' parent='<div class="product_price"> <p class="pr...'>,
 <data='<p class="price_color">£50.10</p>' parent='<div class="product_price"> <p class="pr...'>,
 <data='<p class="price_color">£47.82</p>' parent='<div class="product_price"> <p class="pr...'>,
 ...]
```
Find all elements that are similar to the current element in location and attributes
```python
# For this case, ignore the 'title' attribute while matching
>>> page.find_by_text('Tipping the Velvet').find_similar(ignore_attributes=['title'])
[<data='<a href="catalogue/a-light-in-the-attic_...' parent='<h3><a href="catalogue/a-light-in-the-at...'>,
 <data='<a href="catalogue/soumission_998/index....' parent='<h3><a href="catalogue/soumission_998/in...'>,
 <data='<a href="catalogue/sharp-objects_997/ind...' parent='<h3><a href="catalogue/sharp-objects_997...'>,
...]

# You will notice that the number of elements is 19 not 20 because the current element is not included.
>>> len(page.find_by_text('Tipping the Velvet').find_similar(ignore_attributes=['title']))
19

# Get the `href` attribute from all similar elements
>>> [element.attrib['href'] for element in page.find_by_text('Tipping the Velvet').find_similar(ignore_attributes=['title'])]
['catalogue/a-light-in-the-attic_1000/index.html',
 'catalogue/soumission_998/index.html',
 'catalogue/sharp-objects_997/index.html',
 ...]
```
To increase the complexity a little bit, let's say we want to get all books' data using that element as a starting point for some reason
```python
>>> for product in page.find_by_text('Tipping the Velvet').parent.parent.find_similar():
        print({
            "name": product.css('h3 a::text')[0],
            "price": product.css('.price_color')[0].re_first(r'[\d\.]+'),
            "stock": product.css('.availability::text')[-1].clean()
        })
{'name': 'A Light in the ...', 'price': '51.77', 'stock': 'In stock'}
{'name': 'Soumission', 'price': '50.10', 'stock': 'In stock'}
{'name': 'Sharp Objects', 'price': '47.82', 'stock': 'In stock'}
...
```
The [documentation](/docs/Examples) will provide more advanced examples.

### Handling Structural Changes
> Because [the internet archive](https://web.archive.org/) is down at the time of writing this, I can't use real websites as examples even though I tested that before (I mean browsing an old version of a website and then counting the current version of the website as structural changes)

Let's say you are scraping a page with a structure like this:
```html
<div class="container">
    <section class="products">
        <article class="product" id="p1">
            <h3>Product 1</h3>
            <p class="description">Description 1</p>
        </article>
        <article class="product" id="p2">
            <h3>Product 2</h3>
            <p class="description">Description 2</p>
        </article>
    </section>
</div>
```
and you want to scrape the first product, the one with the `p1` ID. You will probably write a selector like this
```python
page.css('#p1')
```
When website owners implement structural changes like
```html
<div class="new-container">
    <div class="product-wrapper">
        <section class="products">
            <article class="product new-class" data-id="p1">
                <div class="product-info">
                    <h3>Product 1</h3>
                    <p class="new-description">Description 1</p>
                </div>
            </article>
            <article class="product new-class" data-id="p2">
                <div class="product-info">
                    <h3>Product 2</h3>
                    <p class="new-description">Description 2</p>
                </div>
            </article>
        </section>
    </div>
</div>
```
The selector will no longer function and your code needs maintenance. That's where Scrapling auto-matching feature comes into play.

```python
# Before the change
page = Adaptor(page_source, url='example.com', auto_match=True)
element = page.css('#p1' auto_save=True)
if not element:  # One day website changes?
    element = page.css('#p1', auto_match=True)  # Still finds it!
# the rest of the code...
```
> How does the auto-matching work? Check the [FAQs](#FAQs) section for that and other possible issues while auto-matching.

**Notes:**
1. Passing the `auto_save` argument without setting `auto_match` to `True` while initializing the Adaptor object will only result in ignoring the `auto_save` argument value and the following warning message
    ```text
    Argument `auto_save` will be ignored because `auto_match` wasn't enabled on initialization. Check docs for more info.
    ```
    This behavior is purely for performance reasons so the database gets created/connected only when you are planning to use the auto-matching features. Same case with the `auto_match` argument.

2. The `auto_match` parameter works only for `Adaptor` instances not `Adaptors` so if you do something like this you will get an error
    ```python
    page.css('body').css('#p1', auto_match=True)
    ```
    because you can't auto-match a whole list, you have to be specific and do something like
    ```python
    page.css('body')[0].css('#p1', auto_match=True)
    ```

### Is That All?
Here's what else you can do with Scrapling:

- Accessing the `lxml.etree` object itself of any element directly
    ```python
    >>> quote._root
    <Element div at 0x107f98870>
    ```
- Saving and retrieving elements manually to auto-match them outside the `css` and the `xpath` methods but you have to set the identifier by yourself.

  - To save element to the database:
    ```python
    >>> element = page.find_by_text('Tipping the Velvet', first_match=True)
    >>> page.save(element, 'my_special_element')
    ```
  - Now later when you want to retrieve it and relocate it in the page with auto-matching, it would be like this
    ```python
    >>> element_dict = page.retrieve('my_special_element')
    >>> page.relocate(element_dict, adaptor_type=True)
    [<data='<a href="catalogue/tipping-the-velvet_99...' parent='<h3><a href="catalogue/tipping-the-velve...'>]
    >>> page.relocate(element_dict, adaptor_type=True).css('::text')
    ['Tipping the Velvet']
    ```
  - if you want to keep it as `lxml.etree` object, leave the `adaptor_type` argument
    ```python
    >>> page.relocate(element_dict)
    [<Element a at 0x105a2a7b0>]
    ```

- Doing operations on element content is the same as scrapy
    ```python
    quote.re(r'somethings')  # Get all strings (TextHandlers) that match the regex pattern
    quote.re_first(r'something')  # Get the first string (TextHandler) only
    quote.json()  # If the content text is jsonable, then convert it to json using `orjson` which is 10x faster than the standard json library and provides more options
    ```
    Hence all of these methods are actually methods from the `TextHandler` within that contains the text content so the same can be done directly if you call the `.text` property or equivalent selector function.


- Doing operations on the text content itself includes
  - Cleaning the text from any white spaces and replacing consecutive spaces with single space
    ```python
    quote.clean()
    ```
  - You already know about the regex matching and the fast json parsing but did you know that all strings returned from the regex search are actually `TextHandler` objects too? so in cases where you have for example a JS object assigned to a JS variable inside JS code and want to extract it with regex and then convert it to json object, in other libraries, these would be more than 1 line of code but here you can do it in 1 line like this
    ```python
    page.xpath('//script/text()').re_first(r'var dataLayer = (.+);').json()
    ```
  - Sort all characters in the string as if it were a list and return the new string
    ```python
    quote.sort()
    ```
  > To be clear, `TextHandler` is a sub-class of Python's `str` so all normal operations/methods that work with Python strings will work with it.

- Any element's attributes are not exactly a dictionary but a sub-class of [mapping](https://docs.python.org/3/glossary.html#term-mapping) called `AttributesHandler` that's read-only so it's faster and string values returned are actually `TextHandler` objects so all operations above can be done on them, standard dictionary operations that doesn't modify the data, and more :)
  - Unlike standard dictionaries, here you can search by values too and can do partial searches. It might be handy in some cases (returns a generator of matches)
    ```python
    >>> for item in element.attrib.search_values('catalogue', partial=True):
            print(item)
    {'href': 'catalogue/tipping-the-velvet_999/index.html'}
    ```
  - Serialize the current attributes to JSON bytes:
    ```python
    >>> element.attrib.json_string
    b'{"href":"catalogue/tipping-the-velvet_999/index.html","title":"Tipping the Velvet"}'
    ```
  - Converting it to a normal dictionary
    ```python
    >>> dict(element.attrib)
    {'href': 'catalogue/tipping-the-velvet_999/index.html',
    'title': 'Tipping the Velvet'}
    ```

Scrapling is under active development so expect many more features coming soon :)

## More Advanced Usage

There are a lot of deep details skipped here to make this as short as possible so to take a deep dive, head to the [docs](/docs) section. I will try to keep it updated as possible and add complex examples. There I will explain points like how to write your storage system, write spiders that don't depend on selectors at all, and more...

Note that implementing your storage system can be complex as there are some strict rules such as inheriting from the same abstract class, following the singleton design pattern used in other classes, and more. So make sure to read the docs first.


## FAQs
This section addresses common questions about Scrapling, please read this section before opening an issue.

### How does auto-matching work?
  1. You need to get a working selector and run it at least once with methods `css` or `xpath` with the `auto_save` parameter set to `True` before structural changes happen.
  2. Before returning results for you, Scrapling uses its configured database and saves unique properties about that element.
  3. Now because everything about the element can be changed or removed, nothing from the element can be used as a unique identifier for the database. To solve this issue, I made the storage system rely on two things:
     1. The domain of the URL you gave while initializing the first Adaptor object
     2. The `identifier` parameter you passed to the method while selecting. If you didn't pass one, then the selector string itself will be used as an identifier but remember you will have to use it as an identifier value later when the structure changes and you want to pass the new selector.

     Together both are used to retrieve the element's unique properties from the database later.
  4. Now later when you enable the `auto_match` parameter for both the Adaptor instance and the method call. The element properties are retrieved and Scrapling loops over all elements in the page and compares each one's unique properties to the unique properties we already have for this element and a score is calculated for each one.
  5. The comparison between elements is not exact but more about finding how similar these values are, so everything is taken into consideration even the values' order like the order in which the element class names were written before and the order in which the same element class names are written now.
  6. The score for each element is stored in the table and in the end, the element(s) with the highest combined similarity scores are returned.

### How does the auto-matching work if I didn't pass a URL while initializing the Adaptor object?
Not a big problem as it depends on your usage. The word `default` will be used in place of the URL field while saving the element's unique properties. So this will only be an issue if you used the same identifier later for a different website that you didn't pass the URL parameter while initializing it as well. The save process will overwrite the previous data and auto-matching uses the latest saved properties only.

### If all things about an element can change or get removed, what are the unique properties to be saved?
For each element, Scrapling will extract:
- Element tag name, text, attributes (names and values), siblings (tag names only), and path (tag names only).
- Element's parent tag name, attributes (names and values), and text.

### I have enabled the `auto_save`/`auto_match` parameter while selecting and it got completely ignored with a warning message
That's because passing the `auto_save`/`auto_match` argument without setting `auto_match` to `True` while initializing the Adaptor object will only result in ignoring the `auto_save`/`auto_match` argument value. This behavior is purely for performance reasons so the database gets created only when you are planning to use the auto-matching features.

### I have done everything as the docs but the auto-matching didn't return anything, what's wrong?
It could be one of these reasons:
1. No data were saved/stored for this element before.
2. The selector passed is not the one used while storing element data. The solution is simple
   - Pass the old selector again as an identifier to the method called.
   - Retrieve the element with the retrieve method using the old selector as identifier then save it again with the save method and the new selector as identifier.
   - Start using the identifier argument more often if you are planning to use every new selector from now on.
3. The website had some extreme structural changes like a new full design. If this happens a lot with this website, the solution would be to make your code as selector-free as possible using Scrapling features.

### Can Scrapling replace code built on top of BeautifulSoup4?
Pretty much yeah, almost all features you get from BeautifulSoup can be found or achieved in Scrapling one way or another. In fact, if you see there's a feature in bs4 that is missing in Scrapling, please make a feature request from the issues tab to let me know.

### Can Scrapling replace code built on top of AutoScraper?
Of course, you can find elements by text/regex, find similar elements in a more reliable way than AutoScraper, and finally save/retrieve elements manually to use later as the model feature in AutoScraper. I have pulled all top articles about AutoScraper from Google and tested Scrapling against examples in them. In all examples, Scrapling got the same results as AutoScraper in much less time.

### Is Scrapling thread-safe?
Yes, Scrapling instances are thread-safe. Each Adaptor instance maintains its own state.

## Contributing
Everybody is invited and welcome to contribute to Scrapling. There is a lot to do!

Please read the [contributing file](/CONTRIBUTING.md) before doing anything.

## License
This work is licensed under BSD-3

## Acknowledgments
This project includes code adapted from:
- Parsel (BSD License) - Used for [translator](/scrapling/translator.py) submodule

## Known Issues
- In the auto-matching save process, the unique properties of the first element from the selection results are the only ones that get saved. So if the selector you are using selects different elements on the page that are in different locations, auto-matching will probably return to you the first element only when you relocate it later. This doesn't include combined CSS selectors (Using commas to combine more than one selector for example) as these selectors get separated and each selector gets executed alone.
- Currently, Scrapling is not compatible with async/await.

<div align="center"><small>Made with ❤️ by Karim Shoair</small></div><br>