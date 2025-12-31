# Scrapling: A Free Alternative to AI for Robust Web Scraping

Web scraping has long been a vital tool for data extraction, indexing, and preparing datasets, among other purposes. But experienced users often encounter persistent issues that can hinder effectiveness. Recently, there's been a noticeable shift toward AI-based web scraping, driven by its potential to address these challenges.

In this article, we will discuss these common issues, why companies are shifting toward that approach, the problems with that approach, and how scrapling solves them for you without the cost of using AI.

## Common issues and challenging goals

If you have been doing Web Scraping for a long time, you probably noticed that there are repeating problems with Web Scraping, like:

1. **Rapidly changing website structures** — Sites frequently update their DOM structures, breaking static XPath/CSS selectors.
2. **Unstable selectors** — Class names and IDs often change or use randomly generated values that break scrapers or make scraping these websites difficult.
3. **Increasingly complex anti-bot measures** — CAPTCHA systems, browser fingerprinting, and behavior analysis make traditional scraping difficult
and others

But that's only if you are doing targeted Web Scraping for known websites, in which case you can write specific code for every website.

If you start thinking about bigger goals like Broad Scraping or Generic Web Scraping, or what you like to call it, then the above issues intensify, and you will face new issues like:

1. **Extreme Website Diversity** — Generic scraping must handle countless variations in HTML structures, CSS usage, JavaScript frameworks, and backend technologies.
2. **Identifying Relevant Data** — How does the scraper know what data is important on a page it has never seen before?
3. **Pagination variations** — Infinite scroll, traditional pagination, "load more" buttons, all requiring different approaches
and more

How will you solve that manually? I'm referring to generic web scraping of various websites that don't share any common technologies.

## AI to the rescue, but at a high cost

Of course, AI can easily solve most of these issues because it can understand the page source and identify the fields you want or create selectors for them. That's, of course, if you already solved the anti-bot measures through other tools :)

This approach is, of course, beautiful. I love AI and find it very fascinating, especially Generative AI. You will probably spend a lot of time on prompt engineering and tweaking the prompts, but if that's cool with you, you will soon hit the real issue with using AI here.

Most websites have vast amounts of content per page, which you will need to pass to the AI somehow so it can do its magic. This will burn through tokens like fire in a haystack, quickly accumulating high costs.

Unless money is irrelevant to you, you will try to find less expensive approaches, and that's where Scrapling comes into play :smile:

## Scrapling got you covered

Scrapling can handle almost all issues you will face during Web Scraping, and the following updates will cover the rest carefully.

### Solving issue T1: Rapidly changing website structures
That's why the [adaptive](https://scrapling.readthedocs.io/en/latest/parsing/adaptive/) feature was made. You knew I would talk about it, and here we are :)

While Web Scraping, if you have the `adaptive` feature enabled, you can save any element's unique properties so you can find it again later when the website's structure changes. The most frustrating thing about changes is that anything about an element can change, so there's nothing to rely on. 

That's how the adaptive feature works: it stores everything unique about an element. When the website structure changes, it returns the element with the highest similarity score of the previous element.

I have already explained this in more detail, with many examples. Read more from [here](https://scrapling.readthedocs.io/en/latest/parsing/adaptive/#how-the-adaptive-feature-works).

### Solving issue T2: Unstable selectors
If you have been doing Web scraping for a long enough time, you have likely experienced this once. I'm referring to a website that employs poor design patterns, built on raw HTML without any IDs/classes, or uses random class names with nothing else to rely on, etc...

In these cases, standard selection methods with CSS/XPath selectors won't be optimal, and that's why Scrapling provides three more methods for Selection:

1. [Selection by element content](https://scrapling.readthedocs.io/en/latest/parsing/selection/#text-content-selection): Through text content (`find_by_text`) or regex that matches text content (`find_by_regex`)
2. [Selecting elements similar to another element](https://scrapling.readthedocs.io/en/latest/parsing/selection/#finding-similar-elements): You find an element, and we will do the rest!
3. [Selecting elements by filters](https://scrapling.readthedocs.io/en/latest/parsing/selection/#filters-based-searching): You specify conditions/filters that this element must fulfill, we find it!

There is no need to explain any of these; click on the links, and it will be clear how Scrapling solves this.

### Solving issue T3: Increasingly complex anti-bot measures
It's well known that creating an undetectable spider requires more than residential/mobile proxies and human-like behavior. It also needs a hard-to-detect browser, which Scrapling provides two main options to solve:

1. [DynamicFetcher](https://scrapling.readthedocs.io/en/latest/fetching/dynamic/) — This fetcher provides flexible browser automation with multiple configuration options and little under-the-hood stealth improvements.
2. [StealthyFetcher](https://scrapling.readthedocs.io/en/latest/fetching/stealthy/) — Because we live in a harsh world and you need to take [full measure instead of half-measures](https://www.youtube.com/watch?v=7BE4QcwX4dU), `StealthyFetcher` was born. This fetcher uses our stealthy browser -- a version of [DynamicFetcher](https://scrapling.readthedocs.io/en/latest/fetching/dynamic/) that nearly bypasses all annoying anti-protections, provides tools to handle the rest, and automatically bypasses all types of Cloudflare's Turnstile/Interstitial!

We keep improving these two with each update, so stay tuned :)

### Solving issues B1 & B2: Extreme Website Diversity / Identifying Relevant Data

This one is tough to handle, but Scrapling's flexibility makes it possible. 

I talked with someone who uses AI to extract prices from different websites. He is only interested in prices and titles, so he uses AI to find the price for him.

I told him you don't need to use AI here and gave this code as an example
```python
price_element = page.find_by_regex(r'£[\d\.,]+', first_match=True)  # Get the first element that contains a text that matches price regex eg. £10.50
# If you want the container/element that contains the price element
price_element_container = price_element.parent or price_element.find_ancestor(lambda ancestor: ancestor.has_class('product'))  # or other methods...
target_element_selector = price_element_container.generate_css_selector or price_element_container.generate_full_css_selector # or xpath
```
Then he said What about cases like this:
```html
<span class='currency'> $ </span> <span class='a-price'> 45,000 </span>
```
So, I updated the code like this
```python
price_element_container = page.find_by_regex(r'[\d,]+', first_match=True).parent # Adjusted the regex for this example
full_price_data = price_element_container.get_all_text(strip=True)  # Returns '$45,000' in this case
```
This was enough for his use case. You can use the first regex, and if it doesn't find anything, use the following regex, and so on. Try to cover the most common patterns first, then the less common ones, and so on.
It will be a bit boring, but it's definitely less expensive than AI.

This example illustrates the point I aim to convey here. Not every challenge will need AI to be solved, but sometimes you need to be creative, and that might save you a lot of money.

### Solving issue B3: Pagination variations
This issue, Scrapling currently doesn't have a direct method to automatically extract pagination's URLs for you, but it will be added with the upcoming updates :)

But you can handle most websites if you search for the most common patterns with `page.find_by_text('Next')['href']` or `page.find_by_text('load more')['href']` or selectors like `'a[href*="?page="]'` or `'a[href*="/page/"]'`—you get the idea.

## Cost Comparison and Savings
For a quick comparison.

| Aspect         | Scrapling                                                                  | AI-Based Tools (e.g., Browse AI, Oxylabs)                                  |
|----------------|----------------------------------------------------------------------------|----------------------------------------------------------------------------|
| Cost Structure | Likely free or low-cost, no per-use fees                                   | Starts at $19/month (Browse AI) to $49/month (Oxylabs), scales with usage  |
| Setup Effort   | Requires little technical expertise, manual setup                          | Often no-code, easier for non-technical users                              |
| Usage options  | Through code, terminal, or MCP server.                                     | Often through GUI or API, depending on the option the company is providing |
| Scalability    | Depends on user implementation                                             | Built-in support for large-scale, managed services                         |
| Adaptability   | High with features like `adaptive` and the non-selectors selection methods | High, automatic with AI, but costly for frequent changes                   |

This table is based on pricing from [Browse AI Pricing](https://www.browse.ai/pricing) and [Oxylabs Web Scraper API Pricing](https://oxylabs.io/products/scraper-api/web/pricing)

## Conclusion
While AI offers powerful capabilities, its cost can be prohibitive for many Web scraping tasks. Scrapling provides a robust, flexible, and cost-effective toolkit for tackling the real-world challenges of both targeted and broad scraping, often eliminating the need for expensive AI solutions. You can build resilient scrapers more efficiently by leveraging features like `adaptive`, diverse selection methods, and advanced fetchers.

Explore the documentation further and see how Scrapling can simplify your future Web Scraping projects!