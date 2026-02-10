# Migrating from BeautifulSoup to Scrapling

If you're already familiar with BeautifulSoup, you're in for a treat. Scrapling is much faster, provides the same parsing capabilities as BS, adds additional parsing capabilities not found in BS, and introduces powerful new features for fetching and handling modern web pages. This guide will help you quickly adapt your existing BeautifulSoup code to leverage Scrapling's capabilities.

Below is a table that covers the most common operations you'll perform when scraping web pages. Each row illustrates how to achieve a specific task using BeautifulSoup and the corresponding method in Scrapling.

You will notice that some shortcuts in BeautifulSoup are missing in Scrapling, which is one of the reasons BeautifulSoup is slower than Scrapling. The point is: If the same feature can be used in a short one-liner, there is no need to sacrifice performance to shorten that short line :)


| Task                                                            | BeautifulSoup Code                                                                                            | Scrapling Code                                                                    |
|-----------------------------------------------------------------|---------------------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------|
| Parser import                                                   | `from bs4 import BeautifulSoup`                                                                               | `from scrapling.parser import Selector`                                           |
| Parsing HTML from string                                        | `soup = BeautifulSoup(html, 'html.parser')`                                                                   | `page = Selector(html)`                                                           |
| Finding a single element                                        | `element = soup.find('div', class_='example')`                                                                | `element = page.find('div', class_='example')`                                    |
| Finding multiple elements                                       | `elements = soup.find_all('div', class_='example')`                                                           | `elements = page.find_all('div', class_='example')`                               |
| Finding a single element (Example 2)                            | `element = soup.find('div', attrs={"class": "example"})`                                                      | `element = page.find('div', {"class": "example"})`                                |
| Finding a single element (Example 3)                            | `element = soup.find(re.compile("^b"))`                                                                       | `element = page.find(re.compile("^b"))`<br/>`element = page.find_by_regex(r"^b")` |
| Finding a single element (Example 4)                            | `element = soup.find(lambda e: len(list(e.children)) > 0)`                                                    | `element = page.find(lambda e: len(e.children) > 0)`                              |
| Finding a single element (Example 5)                            | `element = soup.find(["a", "b"])`                                                                             | `element = page.find(["a", "b"])`                                                 |
| Find element by its text content                                | `element = soup.find(text="some text")`                                                                       | `element = page.find_by_text("some text", partial=False)`                         |
| Using CSS selectors to find the first matching element          | `elements = soup.select_one('div.example')`                                                                   | `elements = page.css('div.example').first`                                        |
| Using CSS selectors to find all matching element                | `elements = soup.select('div.example')`                                                                       | `elements = page.css('div.example')`                                              |
| Get a prettified version of the page/element source             | `prettified = soup.prettify()`                                                                                | `prettified = page.prettify()`                                                    |
| Get a Non-pretty version of the page/element source             | `source = str(soup)`                                                                                          | `source = page.body`                                                              |
| Get tag name of an element                                      | `name = element.name`                                                                                         | `name = element.tag`                                                              |
| Extracting text content of an element                           | `string = element.string`                                                                                     | `string = element.text`                                                           |
| Extracting all the text in a document or beneath a tag          | `text = soup.get_text(strip=True)`                                                                            | `text = page.get_all_text(strip=True)`                                            |
| Access the dictionary of attributes                             | `attrs = element.attrs`                                                                                       | `attrs = element.attrib`                                                          |
| Extracting attributes                                           | `attr = element['href']`                                                                                      | `attr = element['href']`                                                          |
| Navigating to parent                                            | `parent = element.parent`                                                                                     | `parent = element.parent`                                                         |
| Get all parents of an element                                   | `parents = list(element.parents)`                                                                             | `parents = list(element.iterancestors())`                                         |
| Searching for an element in the parents of an element           | `target_parent = element.find_parent("a")`                                                                    | `target_parent = element.find_ancestor(lambda p: p.tag == 'a')`                   |
| Get all siblings of an element                                  | N/A                                                                                                           | `siblings = element.siblings`                                                     |
| Get next sibling of an element                                  | `next_element = element.next_sibling`                                                                         | `next_element = element.next`                                                     |
| Searching for an element in the siblings of an element          | `target_sibling = element.find_next_sibling("a")`<br/>`target_sibling = element.find_previous_sibling("a")`   | `target_sibling = element.siblings.search(lambda s: s.tag == 'a')`                |
| Searching for elements in the siblings of an element            | `target_sibling = element.find_next_siblings("a")`<br/>`target_sibling = element.find_previous_siblings("a")` | `target_sibling = element.siblings.filter(lambda s: s.tag == 'a')`                |
| Searching for an element in the next elements of an element     | `target_parent = element.find_next("a")`                                                                      | `target_parent = element.below_elements.search(lambda p: p.tag == 'a')`           |
| Searching for elements in the next elements of an element       | `target_parent = element.find_all_next("a")`                                                                  | `target_parent = element.below_elements.filter(lambda p: p.tag == 'a')`           |
| Searching for an element in the previous elements of an element | `target_parent = element.find_previous("a")`                                                                  | `target_parent = element.path.search(lambda p: p.tag == 'a')`                     |
| Searching for elements in the previous elements of an element   | `target_parent = element.find_all_previous("a")`                                                              | `target_parent = element.path.filter(lambda p: p.tag == 'a')`                     |
| Get previous sibling of an element                              | `prev_element = element.previous_sibling`                                                                     | `prev_element = element.previous`                                                 |
| Navigating to children                                          | `children = list(element.children)`                                                                           | `children = element.children`                                                     |
| Get all descendants of an element                               | `children = list(element.descendants)`                                                                        | `children = element.below_elements`                                               |
| Filtering a group of elements that satisfies a condition        | `group = soup.find('p', 'story').css.filter('a')`                                                             | `group = page.find_all('p', 'story').filter(lambda p: p.tag == 'a')`              |


**One key point to remember**: BeautifulSoup offers features for modifying and manipulating the page after it has been parsed. Scrapling focuses more on scraping the page faster for you, and then you can do what you want with the extracted information. So, two different tools can be used in Web Scraping, but one of them specializes in Web Scraping :)

### Putting It All Together

Here's a simple example of scraping a web page to extract all the links using BeautifulSoup and Scrapling.

**With BeautifulSoup:**

```python
import requests
from bs4 import BeautifulSoup

url = 'https://example.com'
response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')

links = soup.find_all('a')
for link in links:
    print(link['href'])
```

**With Scrapling:**

```python
from scrapling import Fetcher

url = 'https://example.com'
page = Fetcher.get(url)

links = page.css('a::attr(href)')
for link in links:
    print(link)
```

As you can see, Scrapling simplifies the process by combining fetching and parsing into a single step, making your code cleaner and more efficient.

**Additional Notes:**

- **Different parsers**: BeautifulSoup allows you to set the parser engine to use, and one of them is `lxml`. Scrapling doesn't do that and uses the `lxml` library by default for performance reasons.
- **Element Types**: In BeautifulSoup, elements are `Tag` objects; in Scrapling, they are `Selector` objects. However, they provide similar methods and properties for navigation and data extraction.
- **Error Handling**: Both libraries return `None` when an element is not found (e.g., `soup.find()` or `page.find()`). In Scrapling, `page.css()` returns an empty `Selectors` list when no elements match, and you can use `page.css('.foo').first` to safely get the first match or `None`. To avoid errors, check for `None` or empty results before accessing properties.
- **Text Extraction**: Scrapling provides additional methods for handling text through `TextHandler`, such as `clean()`, which can help remove extra whitespace, consecutive spaces, or unwanted characters. Please check out the documentation for the complete list.

The documentation provides more details on Scrapling's features and the complete list of arguments that can be passed to all methods.

This guide should make your transition from BeautifulSoup to Scrapling smooth and straightforward. Happy scraping!