## Introduction
Scrapling currently supports parsing HTML pages exclusively, so it doesn't support XML feeds. This decision was made because the adaptive feature won't work with XML, but that might change soon, so stay tuned :)

In Scrapling, there are five main ways to find elements:

1. CSS3 Selectors
2. XPath Selectors
3. Finding elements based on filters/conditions.
4. Finding elements whose content contains a specific text
5. Finding elements whose content matches a specific regex

Of course, there are other indirect ways to find elements with Scrapling, but here we will discuss the main ways in detail. We will also bring up one of the most remarkable features of Scrapling: the ability to find elements that are similar to the element you have; you can jump to that section directly from [here](#finding-similar-elements).

If you are new to Web Scraping, have little to no experience writing selectors, and want to start quickly, I recommend you jump directly to learning the `find`/`find_all` methods from [here](#filters-based-searching).

## CSS/XPath selectors

### What are CSS selectors?
[CSS](https://en.wikipedia.org/wiki/CSS) is a language for applying styles to HTML documents. It defines selectors to associate those styles with specific HTML elements.

Scrapling implements CSS3 selectors as described in the [W3C specification](http://www.w3.org/TR/2011/REC-css3-selectors-20110929/). CSS selectors support comes from `cssselect`, so it's better to read about which [selectors are supported from cssselect](https://cssselect.readthedocs.io/en/latest/#supported-selectors) and pseudo-functions/elements.

Also, Scrapling implements some non-standard pseudo-elements like:

* To select text nodes, use ``::text``.
* To select attribute values, use ``::attr(name)`` where name is the name of the attribute that you want the value of

In short, if you come from Scrapy/Parsel, you will find the same logic for selectors here to make it easier. No need to implement a stranger logic to the one that most of us are used to :)

To select elements with CSS selectors, you have the `css` method which returns `Selectors`. Use `[0]` to get the first element, or `.get()` / `.getall()` to extract text values from text/attribute pseudo-selectors.

### What are XPath selectors?
[XPath](https://en.wikipedia.org/wiki/XPath) is a language for selecting nodes in XML documents, which can also be used with HTML. This [cheatsheet](https://devhints.io/xpath) is a good resource for learning about [XPath](https://en.wikipedia.org/wiki/XPath). Scrapling adds XPath selectors directly through [lxml](https://lxml.de/).

In short, it is the same situation as CSS Selectors; if you come from Scrapy/Parsel, you will find the same logic for selectors here. However, Scrapling doesn't implement the XPath extension function `has-class` as Scrapy/Parsel does. Instead, it provides the `has_class` method, which can be used on elements returned for the same purpose.

To select elements with XPath selectors, you have the `xpath` method. Again, this method follows the same logic as the CSS selectors method above.

> Note that each method of `css` and `xpath` has additional arguments, but we didn't explain them here, as they are all about the adaptive feature. The adaptive feature will have its own page later to be described in detail.

### Selectors examples
Let's see some shared examples of using CSS and XPath Selectors.

Select all elements with the class `product`.
```python
products = page.css('.product')
products = page.xpath('//*[@class="product"]')
```
Note: The XPath one won't be accurate if there's another class; **it's always better to rely on CSS for selecting by class**

Select the first element with the class `product`.
```python
product = page.css('.product')[0]
product = page.xpath('//*[@class="product"]')[0]
```
Get the text of the first element with the `h1` tag name
```python
title = page.css('h1::text').get()
title = page.xpath('//h1//text()').get()
```
Which is the same as doing
```python
title = page.css('h1')[0].text
title = page.xpath('//h1')[0].text
```
Get the `href` attribute of the first element with the `a` tag name
```python
link = page.css('a::attr(href)').get()
link = page.xpath('//a/@href').get()
```
Select the text of the first element with the `h1` tag name, which contains `Phone`, and under an element with class `product`.
```python
title = page.css('.product h1:contains("Phone")::text').get()
title = page.xpath('//*[@class="product"]//h1[contains(text(),"Phone")]/text()').get()
```
You can nest and chain selectors as you want, given that they return results
```python
page.css('.product')[0].css('h1:contains("Phone")::text').get()
page.xpath('//*[@class="product"]')[0].xpath('//h1[contains(text(),"Phone")]/text()').get()
page.xpath('//*[@class="product"]')[0].css('h1:contains("Phone")::text').get()
```
Another example

All links that have 'image' in their 'href' attribute
```python
links = page.css('a[href*="image"]')
links = page.xpath('//a[contains(@href, "image")]')
for index, link in enumerate(links):
    link_value = link.attrib['href']  # Cleaner than link.css('::attr(href)').get()
    link_text = link.text
    print(f'Link number {index} points to this url {link_value} with text content as "{link_text}"')
```

## Text-content selection
Scrapling provides the ability to select elements based on their direct text content, and you have two ways to do this:

1. Elements whose direct text content contains the given text with many options through the `find_by_text` method.
2. Elements whose direct text content matches the given regex pattern with many options through the `find_by_regex` method.

What you can do with `find_by_text` can be done with `find_by_regex` if you are good enough with regular expressions (regex), but we are providing more options to make them easier for all users to access.

With `find_by_text`, you pass the text as the first argument; with `find_by_regex`, the regex pattern is the first argument. Both methods share the following arguments:

* **first_match**: If `True` (the default), the method used will return the first result it finds.
* **case_sensitive**: If `True`, the case of the letters will be considered.
* **clean_match**: If `True`, all whitespaces and consecutive spaces will be replaced with a single space before matching.

By default, Scrapling searches for the exact matching of the text/pattern you pass to `find_by_text`, so the text content of the wanted element has to be ONLY the text you input, but that's why it also has one extra argument, which is:

* **partial**: If enabled, `find_by_text` will return elements that contain the input text. So it's not an exact match anymore

Note: The method `find_by_regex` can accept both regular strings and a compiled regex pattern as its first argument, as you will see in the upcoming examples.

### Finding Similar Elements
One of the most remarkable new features Scrapling puts on the table is the ability to tell Scrapling to find elements similar to the element at hand. This feature's inspiration came from the AutoScraper library, but in Scrapling, it can be used on elements found by any method. Most of its usage would likely occur after finding elements through text content, similar to how AutoScraper works, making it convenient to explain here.

So, how does it work?

Imagine a scenario where you found a product by its title, for example, and you want to extract other products listed in the same table/container. With the element you have, you can call the method `.find_similar()` on it, and Scrapling will:

1. Find all page elements with the same DOM tree depth as this element. 
2. All found elements will be checked, and those without the same tag name, parent tag name, and grandparent tag name will be dropped.
3. Now we are sure (like 99% sure) that these elements are the ones we want, but as a last check, Scrapling will use fuzzy matching to drop the elements whose attributes don't look like the attributes of our element. There's a percentage to control this step, and I recommend you not play with it unless the default settings don't get the elements you want.

That's a lot of talking, I know, but I had to go deep. I will give examples of using this method in the next section, but first, these are the arguments that can be passed to this method:

* **similarity_threshold**: This is the percentage we discussed in step 3 for comparing elements' attributes. The default value is 0.2. In Simpler words, the tag attributes of both elements should be at least 20% similar. If you want to turn off this check (basically Step 3), you can set this attribute to 0, but I recommend you read what the other arguments do first.
* **ignore_attributes**: The attribute names passed will be ignored while matching the attributes in the last step. The default value is `('href', 'src',)` because URLs can change significantly across elements, making them unreliable.
* **match_text**: If `True`, the element's text content will be considered when matching (Step 3). Using this argument in typical cases is not recommended, but it depends.

Now, let's check out the examples below.

### Examples
Let's see some shared examples of finding elements with raw text and regex.

I will use the `Fetcher` class with these examples, but it will be explained in detail later.
```python
from scrapling.fetchers import Fetcher
page = Fetcher.get('https://books.toscrape.com/index.html')
```
Find the first element whose text fully matches this text
```python
>>> page.find_by_text('Tipping the Velvet')
<data='<a href="catalogue/tipping-the-velvet_99...' parent='<h3><a href="catalogue/tipping-the-velve...'>
```
Combining it with `page.urljoin` to return the full URL from the relative `href`.
```python
>>> page.find_by_text('Tipping the Velvet').attrib['href']
'catalogue/tipping-the-velvet_999/index.html'
>>> page.urljoin(page.find_by_text('Tipping the Velvet').attrib['href'])
'https://books.toscrape.com/catalogue/tipping-the-velvet_999/index.html'
```
Get all matches if there are more (notice it returns a list)
```python
>>> page.find_by_text('Tipping the Velvet', first_match=False)
[<data='<a href="catalogue/tipping-the-velvet_99...' parent='<h3><a href="catalogue/tipping-the-velve...'>]
```
Get all elements that contain the word `the` (Partial matching)
```python
>>> results = page.find_by_text('the', partial=True, first_match=False)
>>> [i.text for i in results]
['A Light in the ...',
 'Tipping the Velvet',
 'The Requiem Red',
 'The Dirty Little Secrets ...',
 'The Coming Woman: A ...',
 'The Boys in the ...',
 'The Black Maria',
 'Mesaerion: The Best Science ...',
 "It's Only the Himalayas"]
```
The search is case-insensitive, so those results include `The`, not just the lowercase `the`; let's limit the search to elements with `the` only.
```python
>>> results = page.find_by_text('the', partial=True, first_match=False, case_sensitive=True)
>>> [i.text for i in results]
['A Light in the ...',
 'Tipping the Velvet',
 'The Boys in the ...',
 "It's Only the Himalayas"]
```
Get the first element whose text content matches my price regex
```python
>>> page.find_by_regex(r'£[\d\.]+')
<data='<p class="price_color">£51.77</p>' parent='<div class="product_price"> <p class="pr...'>
>>> page.find_by_regex(r'£[\d\.]+').text
'£51.77'
```
It's the same if you pass the compiled regex as well; Scrapling will detect the input type and act upon that:
```python
>>> import re
>>> regex = re.compile(r'£[\d\.]+')
>>> page.find_by_regex(regex)
<data='<p class="price_color">£51.77</p>' parent='<div class="product_price"> <p class="pr...'>
>>> page.find_by_regex(regex).text
'£51.77'
```
Get all elements that match the regex
```python
>>> page.find_by_regex(r'£[\d\.]+', first_match=False)
[<data='<p class="price_color">£51.77</p>' parent='<div class="product_price"> <p class="pr...'>,
 <data='<p class="price_color">£53.74</p>' parent='<div class="product_price"> <p class="pr...'>,
 <data='<p class="price_color">£50.10</p>' parent='<div class="product_price"> <p class="pr...'>,
 <data='<p class="price_color">£47.82</p>' parent='<div class="product_price"> <p class="pr...'>,
 ...]
```
And so on...

Find all elements similar to the current element in location and attributes. For our case, ignore the 'title' attribute while matching
```python
>>> element = page.find_by_text('Tipping the Velvet')
>>> element.find_similar(ignore_attributes=['title'])
[<data='<a href="catalogue/a-light-in-the-attic_...' parent='<h3><a href="catalogue/a-light-in-the-at...'>,
 <data='<a href="catalogue/soumission_998/index....' parent='<h3><a href="catalogue/soumission_998/in...'>,
 <data='<a href="catalogue/sharp-objects_997/ind...' parent='<h3><a href="catalogue/sharp-objects_997...'>,
...]
```
Notice that the number of elements is 19, not 20, because the current element is not included in the results.
```python
>>> len(element.find_similar(ignore_attributes=['title']))
19
```
Get the `href` attribute from all similar elements
```python
>>> [
    element.attrib['href']
    for element in element.find_similar(ignore_attributes=['title'])
]
['catalogue/a-light-in-the-attic_1000/index.html',
 'catalogue/soumission_998/index.html',
 'catalogue/sharp-objects_997/index.html',
 ...]
```
To increase the complexity a little bit, let's say we want to get all the books' data using that element as a starting point for some reason
```python
>>> for product in element.parent.parent.find_similar():
        print({
            "name": product.css('h3 a::text').get(),
            "price": product.css('.price_color')[0].re_first(r'[\d\.]+'),
            "stock": product.css('.availability::text').getall()[-1].clean()
        })
{'name': 'A Light in the ...', 'price': '51.77', 'stock': 'In stock'}
{'name': 'Soumission', 'price': '50.10', 'stock': 'In stock'}
{'name': 'Sharp Objects', 'price': '47.82', 'stock': 'In stock'}
...
```
### Advanced examples 
See more advanced or real-world examples using the `find_similar` method.

E-commerce Product Extraction
```python
def extract_product_grid(page):
    # Find the first product card
    first_product = page.find_by_text('Add to Cart').find_ancestor(
        lambda e: e.has_class('product-card')
    )

    # Find similar product cards
    products = first_product.find_similar()

    return [
        {
            'name': p.css('h3::text').get(),
            'price': p.css('.price::text').re_first(r'\d+\.\d{2}'),
            'stock': 'In stock' in p.text,
            'rating': p.css('.rating')[0].attrib.get('data-rating')
        }
        for p in products
    ]
```
Table Row Extraction
```python
def extract_table_data(page):
    # Find the first data row
    first_row = page.css('table tbody tr')[0]

    # Find similar rows
    rows = first_row.find_similar()

    return [
        {
            'column1': row.css('td:nth-child(1)::text').get(),
            'column2': row.css('td:nth-child(2)::text').get(),
            'column3': row.css('td:nth-child(3)::text').get()
        }
        for row in rows
    ]
```
Form Field Extraction
```python
def extract_form_fields(page):
    # Find first form field container
    first_field = page.css('input')[0].find_ancestor(
        lambda e: e.has_class('form-field')
    )

    # Find similar field containers
    fields = first_field.find_similar()

    return [
        {
            'label': f.css('label::text').get(),
            'type': f.css('input')[0].attrib.get('type'),
            'required': 'required' in f.css('input')[0].attrib
        }
        for f in fields
    ]
```
Extracting reviews from a website
```python
def extract_reviews(page):
    # Find first review
    first_review = page.find_by_text('Great product!')
    review_container = first_review.find_ancestor(
        lambda e: e.has_class('review')
    )
    
    # Find similar reviews
    all_reviews = review_container.find_similar()
    
    return [
        {
            'text': r.css('.review-text::text').get(),
            'rating': r.attrib.get('data-rating'),
            'author': r.css('.reviewer::text').get()
        }
        for r in all_reviews
    ]
```
## Filters-based searching
This search method is arguably the best way to find elements in Scrapling, as it is powerful and easier for newcomers to Web Scraping to learn than writing selectors. 

Inspired by BeautifulSoup's `find_all` function, you can find elements using the `find_all` and `find` methods. Both methods can accept multiple filters and return all elements on the pages where all these filters apply.

To be more specific:

* Any string passed is considered a tag name.
* Any iterable passed, like List/Tuple/Set, will be considered as an iterable of tag names.
* Any dictionary is considered a mapping of HTML element(s), attribute names, and attribute values.
* Any regex patterns passed are used to filter elements by content, like the `find_by_regex` method
* Any functions passed are used to filter elements
* Any keyword argument passed is considered as an HTML element attribute with its value.

It collects all passed arguments and keywords, and each filter passes its results to the following filter in a waterfall-like filtering system.

It filters all elements in the current page/element in the following order:

1. All elements with the passed tag name(s) get collected.
2. All elements that match all passed attribute(s) are collected; if a previous filter is used, then previously collected elements are filtered.
3. All elements that match all passed regex patterns are collected, or if previous filter(s) are used, then previously collected elements are filtered.
4. All elements that fulfill all passed function(s) are collected; if a previous filter(s) is used, then previously collected elements are filtered.

Notes:

1. As you probably understood, the filtering process always starts from the first filter it finds in the filtering order above. So, if no tag name(s) are passed but attributes are passed, the process starts from that step (number 2), and so on.
2. The order in which you pass the arguments doesn't matter. The only order considered is the one explained above.

Check examples to clear any confusion :)

### Examples
```python
>>> from scrapling.fetchers import Fetcher
>>> page = Fetcher.get('https://quotes.toscrape.com/')
```
Find all elements with the tag name `div`.
```python
>>> page.find_all('div')
[<data='<div class="container"> <div class="row...' parent='<body> <div class="container"> <div clas...'>,
 <data='<div class="row header-box"> <div class=...' parent='<div class="container"> <div class="row...'>,
...]
```
Find all div elements with a class that equals `quote`.
```python
>>> page.find_all('div', class_='quote')
[<data='<div class="quote" itemscope itemtype="h...' parent='<div class="col-md-8"> <div class="quote...'>,
 <data='<div class="quote" itemscope itemtype="h...' parent='<div class="col-md-8"> <div class="quote...'>,
...]
```
Same as above.
```python
>>> page.find_all('div', {'class': 'quote'})
[<data='<div class="quote" itemscope itemtype="h...' parent='<div class="col-md-8"> <div class="quote...'>,
 <data='<div class="quote" itemscope itemtype="h...' parent='<div class="col-md-8"> <div class="quote...'>,
...]
```
Find all elements with a class that equals `quote`.
```python
>>> page.find_all({'class': 'quote'})
[<data='<div class="quote" itemscope itemtype="h...' parent='<div class="col-md-8"> <div class="quote...'>,
 <data='<div class="quote" itemscope itemtype="h...' parent='<div class="col-md-8"> <div class="quote...'>,
...]
```
Find all div elements with a class that equals `quote` and contains the element `.text`, which contains the word 'world' in its content.
```python
>>> page.find_all('div', {'class': 'quote'}, lambda e: "world" in e.css('.text::text').get())
[<data='<div class="quote" itemscope itemtype="h...' parent='<div class="col-md-8"> <div class="quote...'>]
```
Find all elements that don't have children.
```python
>>> page.find_all(lambda element: len(element.children) > 0)
[<data='<html lang="en"><head><meta charset="UTF...'>,
 <data='<head><meta charset="UTF-8"><title>Quote...' parent='<html lang="en"><head><meta charset="UTF...'>,
 <data='<body> <div class="container"> <div clas...' parent='<html lang="en"><head><meta charset="UTF...'>,
...]
```
Find all elements that contain the word 'world' in their content.
```python
>>> page.find_all(lambda element: "world" in element.text)
[<data='<span class="text" itemprop="text">“The...' parent='<div class="quote" itemscope itemtype="h...'>,
 <data='<a class="tag" href="/tag/world/page/1/"...' parent='<div class="tags"> Tags: <meta class="ke...'>]
```
Find all span elements that match the given regex
```python
>>> page.find_all('span', re.compile(r'world'))
[<data='<span class="text" itemprop="text">“The...' parent='<div class="quote" itemscope itemtype="h...'>]
```
Find all div and span elements with class 'quote' (No span elements like that, so only div returned)
```python
>>> page.find_all(['div', 'span'], {'class': 'quote'})
[<data='<div class="quote" itemscope itemtype="h...' parent='<div class="col-md-8"> <div class="quote...'>,
 <data='<div class="quote" itemscope itemtype="h...' parent='<div class="col-md-8"> <div class="quote...'>,
...]
```
Mix things up
```python
>>> page.find_all({'itemtype':"http://schema.org/CreativeWork"}, 'div').css('.author::text').getall()
['Albert Einstein',
 'J.K. Rowling',
...]
```
A bonus pro tip: Find all elements whose `href` attribute's value ends with the word 'Einstein'.
```python
>>> page.find_all({'href$': 'Einstein'})
[<data='<a href="/author/Albert-Einstein">(about...' parent='<span>by <small class="author" itemprop=...'>,
 <data='<a href="/author/Albert-Einstein">(about...' parent='<span>by <small class="author" itemprop=...'>,
 <data='<a href="/author/Albert-Einstein">(about...' parent='<span>by <small class="author" itemprop=...'>]
```
Another pro tip: Find all elements whose `href` attribute's value has '/author/' in it
```python
>>> page.find_all({'href*': '/author/'})
[<data='<a href="/author/Albert-Einstein">(about...' parent='<span>by <small class="author" itemprop=...'>,
 <data='<a href="/author/J-K-Rowling">(about)</a...' parent='<span>by <small class="author" itemprop=...'>,
 <data='<a href="/author/Albert-Einstein">(about...' parent='<span>by <small class="author" itemprop=...'>,
...]
```
And so on...

## Generating selectors
You can always generate CSS/XPath selectors for any element that can be reused here or anywhere else, and the most remarkable thing is that it doesn't matter what method you used to find that element!

Generate a short CSS selector for the `url_element` element (if possible, create a short one; otherwise, it's a full selector)
```python
>>> url_element = page.find({'href*': '/author/'})
>>> url_element.generate_css_selector
'body > div > div:nth-of-type(2) > div > div > span:nth-of-type(2) > a'
```
Generate a full CSS selector for the `url_element` element from the start of the page
```python
>>> url_element.generate_full_css_selector
'body > div > div:nth-of-type(2) > div > div > span:nth-of-type(2) > a'
```
Generate a short XPath selector for the `url_element` element (if possible, create a short one; otherwise, it's a full selector)
```python
>>> url_element.generate_xpath_selector
'//body/div/div[2]/div/div/span[2]/a'
```
Generate a full XPath selector for the `url_element` element from the start of the page
```python
>>> url_element.generate_full_xpath_selector
'//body/div/div[2]/div/div/span[2]/a'
```
> Note: <br>
> When you tell Scrapling to create a short selector, it tries to find a unique element to use in generation as a stop point, like an element with an `id` attribute, but in our case, there wasn't any, so that's why the short and the full selector will be the same.

## Using selectors with regular expressions
Similar to `parsel`/`scrapy`, `re` and `re_first` methods are available for extracting data using regular expressions. However, unlike the former libraries, these methods are in nearly all classes like `Selector`/`Selectors`/`TextHandler` and `TextHandlers`, which means you can use them directly on the element even if you didn't select a text node. 

We will have a deep look at it while explaining the [TextHandler](main_classes.md#texthandler) class, but in general, it works like the examples below:
```python
>>> page.css('.price_color')[0].re_first(r'[\d\.]+')
'51.77'

>>> page.css('.price_color').re_first(r'[\d\.]+')
'51.77'

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

>>> filtering_function = lambda e: e.parent.tag == 'h3' and e.parent.parent.has_class('product_pod')  # As above selector
>>> page.find('a', filtering_function).attrib['href'].re(r'catalogue/(.*)/index.html')
['a-light-in-the-attic_1000']

>>> page.find_by_text('Tipping the Velvet').attrib['href'].re(r'catalogue/(.*)/index.html')
['tipping-the-velvet_999']
```
And so on. You get the idea. We will explain this in more detail on the next page, along with the [TextHandler](main_classes.md#texthandler) class.