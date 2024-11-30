import functools
import time
import timeit
from statistics import mean

import requests
from autoscraper import AutoScraper
from bs4 import BeautifulSoup
from lxml import etree, html
from mechanicalsoup import StatefulBrowser
from parsel import Selector
from pyquery import PyQuery as pq
from selectolax.parser import HTMLParser

from scrapling import Adaptor

large_html = '<html><body>' + '<div class="item">' * 5000 + '</div>' * 5000 + '</body></html>'


def benchmark(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        benchmark_name = func.__name__.replace('test_', '').replace('_', ' ')
        print(f"-> {benchmark_name}", end=" ", flush=True)
        # Warm-up phase
        timeit.repeat(lambda: func(*args, **kwargs), number=2, repeat=2, globals=globals())
        # Measure time (1 run, repeat 100 times, take average)
        times = timeit.repeat(
            lambda: func(*args, **kwargs), number=1, repeat=100, globals=globals(), timer=time.process_time
        )
        min_time = round(mean(times) * 1000, 2)  # Convert to milliseconds
        print(f"average execution time: {min_time} ms")
        return min_time

    return wrapper


@benchmark
def test_lxml():
    return [
        e.text
        for e in etree.fromstring(
            large_html,
            # Scrapling and Parsel use the same parser inside so this is just to make it fair
            parser=html.HTMLParser(recover=True, huge_tree=True)
        ).cssselect('.item')]


@benchmark
def test_bs4_lxml():
    return [e.text for e in BeautifulSoup(large_html, 'lxml').select('.item')]


@benchmark
def test_bs4_html5lib():
    return [e.text for e in BeautifulSoup(large_html, 'html5lib').select('.item')]


@benchmark
def test_pyquery():
    return [e.text() for e in pq(large_html)('.item').items()]


@benchmark
def test_scrapling():
    # No need to do `.extract()` like parsel to extract text
    # Also, this is faster than `[t.text for t in Adaptor(large_html, auto_match=False, debug=False).css('.item')]`
    # for obvious reasons, of course.
    return Adaptor(large_html, auto_match=False, debug=False).css('.item::text')


@benchmark
def test_parsel():
    return Selector(text=large_html).css('.item::text').extract()


@benchmark
def test_mechanicalsoup():
    browser = StatefulBrowser()
    browser.open_fake_page(large_html)
    return [e.text for e in browser.page.select('.item')]


@benchmark
def test_selectolax():
    return [node.text() for node in HTMLParser(large_html).css('.item')]


def display(results):
    # Sort and display results
    sorted_results = sorted(results.items(), key=lambda x: x[1])  # Sort by time
    scrapling_time = results['Scrapling']
    print("\nRanked Results (fastest to slowest):")
    print(f" i. {'Library tested':<18} | {'avg. time (ms)':<15} | vs Scrapling")
    print('-' * 50)
    for i, (test_name, test_time) in enumerate(sorted_results, 1):
        compare = round(test_time / scrapling_time, 3)
        print(f" {i}. {test_name:<18} | {str(test_time):<15} | {compare}")


@benchmark
def test_scrapling_text(request_html):
    # Will loop over resulted elements to get text too to make comparison even more fair otherwise Scrapling will be even faster
    return [
        element.text for element in Adaptor(
            request_html, auto_match=False, debug=False
        ).find_by_text('Tipping the Velvet', first_match=True).find_similar(ignore_attributes=['title'])
    ]


@benchmark
def test_autoscraper(request_html):
    # autoscraper by default returns elements text
    return AutoScraper().build(html=request_html, wanted_list=['Tipping the Velvet'])


if __name__ == "__main__":
    print(' Benchmark: Speed of parsing and retrieving the text content of 5000 nested elements \n')
    results1 = {
        "Raw Lxml": test_lxml(),
        "Parsel/Scrapy": test_parsel(),
        "Scrapling": test_scrapling(),
        'Selectolax': test_selectolax(),
        "PyQuery": test_pyquery(),
        "BS4 with Lxml": test_bs4_lxml(),
        "MechanicalSoup": test_mechanicalsoup(),
        "BS4 with html5lib": test_bs4_html5lib(),
    }

    display(results1)
    print('\n' + "="*25)
    req = requests.get('https://books.toscrape.com/index.html')
    print(
        ' Benchmark: Speed of searching for an element by text content, and retrieving the text of similar elements\n'
    )
    results2 = {
        "Scrapling": test_scrapling_text(req.text),
        "AutoScraper": test_autoscraper(req.text),
    }
    display(results2)
