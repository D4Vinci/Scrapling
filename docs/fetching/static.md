# Introduction

The `Fetcher` class provides fast and lightweight HTTP requests with some stealth capabilities. This class uses [httpx](https://www.python-httpx.org/) as an engine for making requests. For advanced usages, you will need some knowledge about [httpx](https://www.python-httpx.org/), but it becomes simpler and simpler with user feedback and updates.

## Basic Usage
You have one primary way to import this Fetcher, which is the same for all fetchers.

```python
>>> from scrapling.fetchers import Fetcher
```
Check out how to configure the parsing options [here](choosing.md#parser-configuration-in-all-fetchers)

### Shared arguments
All methods for making requests here share some arguments, so let's discuss them first.

- **url**: The URL you want to request, of course :)
- **proxy**: As the name implies, the proxy for this request is used to route all traffic (HTTP and HTTPS). The format accepted here is `http://username:password@localhost:8030`.
- **stealthy_headers**: Generate and use real browser's headers, then create a referer header as if this request came from a Google search page of this URL's domain. Enabled by default, all headers generated can be overwritten by you through the `headers` argument.
- **follow_redirects**: As the name implies, tell the fetcher to follow redirections. Enabled by default
- **timeout**: The timeout to wait for each request to be finished in milliseconds. The default is 30000ms (30 seconds).
- **retries**: The number of retries that [httpx](https://www.python-httpx.org/) will do for failed requests. The default number of retries is 3.

Other than this, you can pass any arguments that `httpx.<method_name>` takes, and that's why I said, in the beginning, you need a bit of knowledge about [httpx](https://www.python-httpx.org/), but in the following examples, we will try to cover most cases.

### HTTP Methods
Examples are the best way to explain this

> Hence: `OPTIONS` and `HEAD` methods are not supported.
#### GET
```python
>>> from scrapling.fetchers import Fetcher
>>> # Basic GET
>>> page = Fetcher.get('https://example.com')
>>> page = Fetcher.get('https://httpbin.org/get', stealthy_headers=True, follow_redirects=True)
>>> page = Fetcher.get('https://httpbin.org/get', proxy='http://username:password@localhost:8030')
>>> # With parameters
>>> page = Fetcher.get('https://example.com/search', params={'q': 'query'})
>>>
>>> # With headers
>>> page = Fetcher.get('https://example.com', headers={'User-Agent': 'Custom/1.0'})
>>> # Basic HTTP authentication
>>> page = Fetcher.get("https://example.com", auth=("my_user", "password123"))
```
And for asynchronous requests, it's a small adjustment 
```python
>>> from scrapling.fetchers import AsyncFetcher
>>> # Basic GET
>>> page = await AsyncFetcher.get('https://example.com')
>>> page = await AsyncFetcher.get('https://httpbin.org/get', stealthy_headers=True, follow_redirects=True)
>>> page = await AsyncFetcher.get('https://httpbin.org/get', proxy='http://username:password@localhost:8030')
>>> # With parameters
>>> page = await AsyncFetcher.get('https://example.com/search', params={'q': 'query'})
>>>
>>> # With headers
>>> page = await AsyncFetcher.get('https://example.com', headers={'User-Agent': 'Custom/1.0'})
>>> # Basic HTTP authentication
>>> page = await AsyncFetcher.get("https://example.com", auth=("my_user", "password123"))
```
Needless to say, the `page` object in all cases is [Response](choosing.md#response-object) object, which is an `Adaptor` as we said, so you will use it directly
```python
>>> page.css('.something.something')

>>> page = Fetcher.get('https://api.github.com/events')
>>> page.json()
[{'id': '<redacted>',
  'type': 'PushEvent',
  'actor': {'id': '<redacted>',
   'login': '<redacted>',
   'display_login': '<redacted>',
   'gravatar_id': '',
   'url': 'https://api.github.com/users/<redacted>',
   'avatar_url': 'https://avatars.githubusercontent.com/u/<redacted>'},
  'repo': {'id': '<redacted>',
...
```
#### POST
```python
>>> from scrapling.fetchers import Fetcher
>>> # Basic POST
>>> page = Fetcher.post('https://httpbin.org/post', data={'key': 'value'})
>>> page = Fetcher.post('https://httpbin.org/post', data={'key': 'value'}, stealthy_headers=True, follow_redirects=True)
>>> page = Fetcher.post('https://httpbin.org/post', data={'key': 'value'}, proxy='http://username:password@localhost:8030')
>>> # Another example of form-encoded data
>>> page = Fetcher.post('https://example.com/submit', data={'username': 'user', 'password': 'pass'})
>>> # JSON data
>>> page = Fetcher.post('https://example.com/api', json={'key': 'value'})
>>> # Uploading file
>>> r = Fetcher.post("https://httpbin.org/post", files={'upload-file': open('something.xlsx', 'rb')})
```
And for asynchronous requests, it's a small adjustment
```python
>>> from scrapling.fetchers import AsyncFetcher
>>> # Basic POST
>>> page = await AsyncFetcher.post('https://httpbin.org/post', data={'key': 'value'})
>>> page = await AsyncFetcher.post('https://httpbin.org/post', data={'key': 'value'}, stealthy_headers=True, follow_redirects=True)
>>> page = await AsyncFetcher.post('https://httpbin.org/post', data={'key': 'value'}, proxy='http://username:password@localhost:8030')
>>> # Another example of form-encoded data
>>> page = await AsyncFetcher.post('https://example.com/submit', data={'username': 'user', 'password': 'pass'})
>>> # JSON data
>>> page = await AsyncFetcher.post('https://example.com/api', json={'key': 'value'})
>>> # Uploading file
>>> r = await AsyncFetcher.post("https://httpbin.org/post", files={'upload-file': open('something.xlsx', 'rb')})
```
#### PUT
```python
>>> from scrapling.fetchers import Fetcher
>>> # Basic PUT
>>> page = Fetcher.put('https://example.com/update', data={'status': 'updated'})
>>> page = Fetcher.put('https://example.com/update', data={'status': 'updated'}, stealthy_headers=True, follow_redirects=True)
>>> page = Fetcher.put('https://example.com/update', data={'status': 'updated'}, proxy='http://username:password@localhost:8030')
>>> # Another example of form-encoded data
>>> page = Fetcher.put("https://httpbin.org/put", data={'key': ['value1', 'value2']})
```
And for asynchronous requests, it's a small adjustment
```python
>>> from scrapling.fetchers import AsyncFetcher
>>> # Basic PUT
>>> page = await AsyncFetcher.put('https://example.com/update', data={'status': 'updated'})
>>> page = await AsyncFetcher.put('https://example.com/update', data={'status': 'updated'}, stealthy_headers=True, follow_redirects=True)
>>> page = await AsyncFetcher.put('https://example.com/update', data={'status': 'updated'}, proxy='http://username:password@localhost:8030')
>>> # Another example of form-encoded data
>>> page = await AsyncFetcher.put("https://httpbin.org/put", data={'key': ['value1', 'value2']})
```

#### DELETE
```python
>>> from scrapling.fetchers import Fetcher
>>> page = Fetcher.delete('https://example.com/resource/123')
>>> page = Fetcher.delete('https://example.com/resource/123', stealthy_headers=True, follow_redirects=True)
>>> page = Fetcher.delete('https://example.com/resource/123', proxy='http://username:password@localhost:8030')
```
And for asynchronous requests, it's a small adjustment
```python
>>> from scrapling.fetchers import AsyncFetcher
>>> page = await AsyncFetcher.delete('https://example.com/resource/123')
>>> page = await AsyncFetcher.delete('https://example.com/resource/123', stealthy_headers=True, follow_redirects=True)
>>> page = await AsyncFetcher.delete('https://example.com/resource/123', proxy='http://username:password@localhost:8030')
```

## Examples
Some well-rounded examples to aid newcomers to Web Scraping

### Basic HTTP Request

```python
from scrapling.fetchers import Fetcher

# Make a request
page = Fetcher.get('https://example.com')

# Check the status
if page.status == 200:
    # Extract title
    title = page.css_first('title::text')
    print(f"Page title: {title}")
    
    # Extract all links
    links = page.css('a::attr(href)')
    print(f"Found {len(links)} links")
```

### Product Scraping

```python
from scrapling.fetchers import Fetcher

def scrape_products():
    page = Fetcher.get('https://example.com/products')
    
    # Find all product elements
    products = page.css('.product')
    
    results = []
    for product in products:
        results.append({
            'title': product.css_first('.title::text'),
            'price': product.css_first('.price::text').re_first(r'\d+\.\d{2}'),
            'description': product.css_first('.description::text'),
            'in_stock': product.has_class('in-stock')
        })
    
    return results
```

### Pagination Handling

```python
from scrapling.fetchers import Fetcher

def scrape_all_pages():
    base_url = 'https://example.com/products?page={}'
    page_num = 1
    all_products = []
    
    while True:
        # Get current page
        page = Fetcher.get(base_url.format(page_num))
        
        # Find products
        products = page.css('.product')
        if not products:
            break
            
        # Process products
        for product in products:
            all_products.append({
                'name': product.css_first('.name::text'),
                'price': product.css_first('.price::text')
            })
            
        # Next page
        page_num += 1
        
    return all_products
```

### Form Submission

```python
from scrapling.fetchers import Fetcher

# Submit login form
response = Fetcher.post(
    'https://example.com/login',
    data={
        'username': 'user@example.com',
        'password': 'password123'
    }
)

# Check login success
if response.status == 200:
    # Extract user info
    user_name = response.css_first('.user-name::text')
    print(f"Logged in as: {user_name}")
```

### Table Extraction

```python
from scrapling.fetchers import Fetcher

def extract_table():
    page = Fetcher.get('https://example.com/data')
    
    # Find table
    table = page.css_first('table')
    
    # Extract headers
    headers = [
        th.text for th in table.css('thead th')
    ]
    
    # Extract rows
    rows = []
    for row in table.css('tbody tr'):
        cells = [td.text for td in row.css('td')]
        rows.append(dict(zip(headers, cells)))
        
    return rows
```

### Navigation Menu

```python
from scrapling.fetchers import Fetcher

def extract_menu():
    page = Fetcher.get('https://example.com')
    
    # Find navigation
    nav = page.css_first('nav')
    
    menu = {}
    for item in nav.css('li'):
        link = item.css_first('a')
        if link:
            menu[link.text] = {
                'url': link.attrib['href'],
                'has_submenu': bool(item.css('.submenu'))
            }
            
    return menu
```

## When to Use

Use `Fetcher` when:

- Need fast HTTP requests
- Want minimal overhead
- Don't need JavaScript
- Want simple configuration
- Need basic stealth features

Use other fetchers when:

- Need browser automation.
- Need advanced anti-bot/stealth.
- Need JavaScript support.