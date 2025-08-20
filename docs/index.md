<style>
.md-typeset h1 {
  display: none;
}
</style>

<p align="center">
    <a href="https://scrapling.readthedocs.io/en/latest/" alt="poster">
        <img alt="poster" src="assets/poster.png" style="width: 50%; height: 100%;"></a>
</p>

Scrapling is an Undetectable, high-performance, intelligent Web scraping library for Python 3 to make Web Scraping easy!

Scrapling isn't only about making undetectable requests or fetching pages under the radar!

It has its own parser that adapts to website changes and provides many element selection/querying options other than traditional selectors, powerful DOM traversal API, and many other features while significantly outperforming popular parsing alternatives.

Scrapling is built from the ground up by Web scraping experts for beginners and experts. The goal is to provide powerful features while maintaining simplicity and minimal boilerplate code.

```python
>> from scrapling.fetchers import Fetcher, AsyncFetcher, StealthyFetcher, PlayWrightFetcher
>> StealthyFetcher.auto_match = True
# Fetch websites' source under the radar!
>> page = StealthyFetcher.fetch('https://example.com', headless=True, network_idle=True)
>> print(page.status)
200
>> products = page.css('.product', auto_save=True)  # Scrape data that survives website design changes!
>> # Later, if the website structure changes, pass `auto_match=True`
>> products = page.css('.product', auto_match=True)  # and Scrapling still finds them!
```

## Top Sponsors 

<!-- sponsors -->
<p style="text-align: center;">
<a href="https://evomi.com?utm_source=github&utm_medium=banner&utm_campaign=d4vinci-scrapling" target="_blank" title="Evomi is your Swiss Quality Proxy Provider, starting at $0.49/GB"><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/evomi.png"></a>
</p>
<!-- /sponsors -->

<i><sub>Do you want to show your ad here? Click [here](https://github.com/sponsors/D4Vinci) and choose the tier that suites you!</sub></i>

## Key Features
### Fetch websites as you prefer with async support
- **HTTP Requests**: Fast and stealthy HTTP requests with the `Fetcher` class.
- **Dynamic Loading & Automation**: Fetch dynamic websites with the `PlayWrightFetcher` class through your real browser, Scrapling's stealth mode, Playwright's Chromium browser, or [NSTbrowser](https://app.nstbrowser.io/r/1vO5e5)'s browserless!
- **Anti-bot Protections Bypass**: Easily bypass protections with the `StealthyFetcher` and `PlayWrightFetcher` classes.

### Easy Scraping
- **Smart Element Tracking**: Relocate elements after website changes using an intelligent similarity system and integrated storage.
- **Flexible Selection**: CSS selectors, XPath selectors, filters-based search, text search, regex search, and more.
- **Find Similar Elements**: Automatically locate elements similar to the element you found!
- **Smart Content Scraping**: Extract data from multiple websites without specific selectors using Scrapling powerful features.

### High Performance
- **Lightning Fast**: Built from the ground up with performance in mind, outperforming most popular Python scraping libraries.
- **Memory Efficient**: Optimized data structures for minimal memory footprint.
- **Fast JSON serialization**: 10x faster than standard library.

### Developer Friendly
- **Powerful Navigation API**: Easy DOM traversal in all directions.
- **Rich Text Processing**: All strings have built-in regex, cleaning methods, and more. All elements' attributes are optimized dictionaries that use less memory than standard dictionaries with added methods.
- **Auto Selectors Generation**: Generate robust short and full CSS/XPath selectors for any element.
- **Familiar API**: Similar to Scrapy/BeautifulSoup and the same CSS pseudo-elements used in Scrapy.
- **Type hints**: Complete type/doc-strings coverage for future-proofing and best autocompletion support.

## Star History
Scrapling’s GitHub stars have grown steadily since its release (see chart below).

<div id="chartContainer">
  <a href="https://github.com/D4Vinci/Scrapling">
    <img id="chartImage" alt="Star History Chart" loading="lazy" src="https://api.star-history.com/svg?repos=D4Vinci/Scrapling&type=Date" height="400"/>
  </a>
</div>

<script>
const observer = new MutationObserver((mutations) => {
  mutations.forEach((mutation) => {
    if (mutation.attributeName === 'data-md-color-media') {
      const colorMedia = document.body.getAttribute('data-md-color-media');
      const isDarkScheme = document.body.getAttribute('data-md-color-scheme') === 'slate';
      const chartImg = document.querySelector('#chartImage');
      const baseUrl = 'https://api.star-history.com/svg?repos=D4Vinci/Scrapling&type=Date';
      
      if (colorMedia === '(prefers-color-scheme)' ? isDarkScheme : colorMedia.includes('dark')) {
        chartImg.src = `${baseUrl}&theme=dark`;
      } else {
        chartImg.src = baseUrl;
      }
    }
  });
});

observer.observe(document.body, {
  attributes: true,
  attributeFilter: ['data-md-color-media', 'data-md-color-scheme']
});
</script>

## Installation
Scrapling is a breeze to get started with!<br/>Starting from version 0.2.9, we require at least Python 3.9 to work.

Run this command to install it with Python's pip.
```bash
pip3 install scrapling
```
You are ready if you plan to use the parser only (the `Adaptor` class).

But if you are going to make requests or fetch pages with Scrapling, then run this command to install browsers' dependencies needed to use the Fetchers
```bash
scrapling install
```
If you have any installation issues, please open an [issue](https://github.com/D4Vinci/Scrapling/issues/new/choose).

## How the documentation is organized
Scrapling has a lot of documentation, so we try to follow a guideline called the [Diátaxis documentation framework](https://diataxis.fr/).

## Support

If you like Scrapling and want to support its development:

- ⭐ Star the [GitHub repository](https://github.com/D4Vinci/Scrapling)
- 🚀 Follow us on [Twitter](https://x.com/Scrapling_dev) and join the [discord server](https://discord.gg/EMgGbDceNQ)
- 💝 Consider [sponsoring the project or buying me a coffe](donate.md) :wink:
- 🐛 Report bugs and suggest features through [GitHub Issues](https://github.com/D4Vinci/Scrapling/issues)

## License

This project is licensed under BSD-3 License. See the [LICENSE](https://github.com/D4Vinci/Scrapling/blob/main/LICENSE) file for details.