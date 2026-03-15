# Migrating from BeautifulSoup to Scrapling

API comparison between BeautifulSoup and Scrapling. Scrapling is faster, provides equivalent parsing capabilities, and adds features for fetching and handling modern web pages.

Some BeautifulSoup shortcuts have no direct Scrapling equivalent. Scrapling avoids those shortcuts to preserve performance.


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
| Get a Non-pretty version of the page/element source             | `source = str(soup)`                                                                                          | `source = page.html_content`                                                      |
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
| Searching for an element in the ancestors of an element         | `target_parent = element.find_previous("a")` ¹                                                                | `target_parent = element.path.search(lambda p: p.tag == 'a')`                     |
| Searching for elements in the ancestors of an element           | `target_parent = element.find_all_previous("a")` ¹                                                            | `target_parent = element.path.filter(lambda p: p.tag == 'a')`                     |
| Get previous sibling of an element                              | `prev_element = element.previous_sibling`                                                                     | `prev_element = element.previous`                                                 |
| Navigating to children                                          | `children = list(element.children)`                                                                           | `children = element.children`                                                     |
| Get all descendants of an element                               | `children = list(element.descendants)`                                                                        | `children = element.below_elements`                                               |
| Filtering a group of elements that satisfies a condition        | `group = soup.find('p', 'story').css.filter('a')`                                                             | `group = page.find_all('p', 'story').filter(lambda p: p.tag == 'a')`              |


¹ **Note:** BS4's `find_previous`/`find_all_previous` searches all preceding elements in document order, while Scrapling's `path` only returns ancestors (the parent chain). These are not exact equivalents, but ancestor search covers the most common use case.

BeautifulSoup supports modifying/manipulating the parsed DOM. Scrapling does not — it is read-only and optimized for extraction.

### Full Example: Extracting Links

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

Scrapling combines fetching and parsing into a single step.

**Note:**

- **Parsers**: BeautifulSoup supports multiple parser engines. Scrapling always uses `lxml` for performance.
- **Element Types**: BeautifulSoup elements are `Tag` objects; Scrapling elements are `Selector` objects. Both provide similar navigation and extraction methods.
- **Error Handling**: Both libraries return `None` when an element is not found (e.g., `soup.find()` or `page.find()`). `page.css()` returns an empty `Selectors` list when no elements match. Use `page.css('.foo').first` to safely get the first match or `None`.
- **Text Extraction**: Scrapling's `TextHandler` provides additional text processing methods such as `clean()` for removing extra whitespace, consecutive spaces, or unwanted characters.