# Replacing AI-based Scraping with Scrapling

Scrapling provides a robust, cost-effective alternative to AI-based web scraping. This guide covers common scraping challenges, why AI is often used to solve them, and how Scrapling handles these issues without the cost of AI tokens.

## Common Web Scraping Issues

Experienced users frequently encounter these problems:

1. **Rapidly changing website structures** — Sites frequently update their DOM structures, breaking static XPath/CSS selectors.
2. **Unstable selectors** — Class names and IDs often change or use randomly generated values that break scrapers.
3. **Increasingly complex anti-bot measures** — CAPTCHA systems, browser fingerprinting, and behavior analysis make traditional scraping difficult.

For broader goals like generic or broad scraping, additional challenges appear:

1. **Extreme website diversity** — Generic scraping must handle countless variations in HTML structures, CSS usage, JavaScript frameworks, and backend technologies.
2. **Identifying relevant data** — How does the scraper know what data is important on a page it has never seen before?
3. **Pagination variations** — Infinite scroll, traditional pagination, "load more" buttons — all requiring different approaches.

## The Problem with AI-based Scraping

AI can understand page source and identify target fields or create selectors. However, most websites have vast amounts of content per page, which must be passed to the AI for processing. This burns through tokens quickly, accumulating high costs — especially at scale.

## How Scrapling Solves These Issues

### Rapidly Changing Website Structures

The [adaptive feature](parsing/adaptive.md) stores everything unique about an element. When the website structure changes, it returns the element with the highest similarity score to the previous element. Enable `adaptive` while scraping, save any element's unique properties, and find it again later even after structural changes.

### Unstable Selectors

When standard CSS/XPath selectors fail, Scrapling provides three alternative selection methods:

1. **[Text content selection](parsing/selection.md)**: Find elements through text content (`find_by_text`) or regex matching (`find_by_regex`).
2. **[Similar element selection](parsing/selection.md)**: Find an element, then find others like it with `find_similar()`.
3. **[Filter-based searching](parsing/selection.md)**: Specify conditions/filters an element must fulfill.

### Anti-bot Measures

Scrapling provides two browser-based fetchers with stealth capabilities:

1. **[DynamicFetcher](fetching/dynamic.md)** — Flexible browser automation with stealth improvements.
2. **[StealthyFetcher](fetching/stealthy.md)** — Advanced anti-bot bypass that nearly bypasses all protections, including automatic Cloudflare Turnstile/Interstitial solving.

### Extreme Website Diversity and Identifying Relevant Data

Scrapling's flexibility makes this possible without AI. For example, extracting prices from arbitrary websites:

```python
# Get the first element containing text that matches a price regex (e.g. £10.50)
price_element = page.find_by_regex(r'£[\d\.,]+', first_match=True)
# Get the container element
price_element_container = price_element.parent or price_element.find_ancestor(
    lambda ancestor: ancestor.has_class('product')
)
target_selector = price_element_container.generate_css_selector  # or generate_full_css_selector, or xpath
```

For cases where currency and amount are in separate elements:

```html
<span class='currency'> $ </span> <span class='a-price'> 45,000 </span>
```

```python
price_element_container = page.find_by_regex(r'[\d,]+', first_match=True).parent
full_price_data = price_element_container.get_all_text(strip=True)  # Returns '$45,000'
```

Cover the most common patterns first with regex, then less common ones. It requires more initial setup than AI, but is far less expensive at scale.

### Pagination Variations

While Scrapling doesn't yet have automatic pagination extraction, common patterns can be handled:

```python
next_link = page.find_by_text('Next')['href']
# or
next_link = page.find_by_text('load more')['href']
# or CSS selectors
next_link = page.css('a[href*="?page="]')
next_link = page.css('a[href*="/page/"]')
```

## Cost Comparison

| Aspect         | Scrapling                                                                  | AI-Based Tools (e.g., Browse AI, Oxylabs)                                  |
|----------------|----------------------------------------------------------------------------|----------------------------------------------------------------------------|
| Cost Structure | Likely free or low-cost, no per-use fees                                   | Starts at $19/month (Browse AI) to $49/month (Oxylabs), scales with usage  |
| Setup Effort   | Requires little technical expertise, manual setup                          | Often no-code, easier for non-technical users                              |
| Usage options  | Through code, terminal, or MCP server                                      | Often through GUI or API, depending on the option the company is providing |
| Scalability    | Depends on user implementation                                             | Built-in support for large-scale, managed services                         |
| Adaptability   | High with features like `adaptive` and the non-selectors selection methods | High, automatic with AI, but costly for frequent changes                   |

## Conclusion

Not every challenge needs AI to be solved. By leveraging features like `adaptive`, diverse selection methods (`find_by_text`, `find_by_regex`, `find_similar`), and advanced fetchers (`StealthyFetcher`), you can build resilient scrapers that handle real-world challenges at a fraction of the cost of AI-based solutions.
